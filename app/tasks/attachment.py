import os
from pathlib import Path

from loguru import logger
from sqlalchemy import select

from app.api.exceptions import attachment_not_found_exception
from app.core.sqlalchemy import get_manual_postgres_session
from app.database.models.postgresql import (
    SubmissionAttachment,
)
from app.utilities.cloudinary_uploader import upload_to_cloudinary


async def upload_assignment_attachment(
    assignment_id: int,
    attachment_id: int,
    stored_filename: str,
):
    try:
        async with get_manual_postgres_session() as db:  # type: ignore
            # find attachment with attachment_id
            stmt = select(SubmissionAttachment).where(
                SubmissionAttachment.attachment_id == attachment_id
            )
            result = await db.execute(stmt)
            attachment = result.scalar_one_or_none()

            # if no attachment found with the mentioned id raise exception
            if not attachment:
                raise attachment_not_found_exception

            # read file content
            base_dir = Path(__file__).resolve().parent.parent.parent  # ./app/tasks/
            file_path = base_dir / "static" / "uploads" / stored_filename
            with open(file_path, "rb") as f:
                content = f.read()

            # if an entry already exists, save attachment to disk
            upload_url = await upload_to_cloudinary(
                content,
                folder=f"assignments/{assignment_id}",
                public_id=stored_filename.split(".")[0],
            )
            logger.debug(
                f"Attachment for submission {attachment.submission_id} uploaded to {upload_url}"
            )

            # add uploaded url to attachment
            attachment.file_url = upload_url
            db.add(attachment)
            await db.commit()
            await db.refresh(attachment)

            # remove file from os
            try:
                os.remove(file_path)
                logger.debug(f"✅ Deleted temp file: {file_path}")
            except OSError as e:
                logger.warning(f"❌ Failed to delete temp file {file_path}: {e}")
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
