import os
from pathlib import Path

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import delete, select

from app.api.exceptions import attachment_not_found_exception
from app.core.sqlalchemy import get_manual_postgres_session
from app.database.models.postgresql import (
    AssignmentSubmission,
    SubmissionAttachment,
)
from app.utilities.cloudinary import delete_from_cloudinary, upload_to_cloudinary


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
            file_path = (
                base_dir / "static" / "uploads" / "attachments" / stored_filename
            )
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
                logger.debug(f"✅ Deleted file: {file_path}")
            except OSError as e:
                logger.warning(f"❌ Failed to delete file {file_path}: {e}")
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)


async def delete_assignment_attachment(attachment_id: int):
    try:
        async with get_manual_postgres_session() as db:
            stmt = select(SubmissionAttachment).where(
                SubmissionAttachment.attachment_id == attachment_id
            )
            result = await db.execute(stmt)
            attachment = result.scalar_one_or_none()

            if not attachment:
                raise attachment_not_found_exception

            # if file_url is not present delete local file
            if not attachment.file_url:
                base_dir = Path(__file__).resolve().parent.parent.parent
                file_path = (
                    base_dir
                    / "static"
                    / "uploads"
                    / "attachments"
                    / attachment.stored_filename
                )
                logger.debug(file_path)
                try:
                    if file_path.is_file():
                        os.remove(file_path)
                        logger.debug(
                            f"✅ Deleted attachment {attachment.original_filename} from local machine"
                        )
                except OSError as e:
                    logger.error(
                        f"❌ Failed to delete file {attachment.stored_filename} from local machine: {e}"
                    )

            # if file_url is present delete cloudinary file
            if attachment.file_url:
                try:
                    await delete_from_cloudinary(
                        attachment.file_url.split("/")[-1].split(".")[0]
                    )
                    logger.debug(
                        f"✅ Deleted attachment {attachment.original_filename} from cloudinary"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Failed to delete file {attachment.stored_filename} from cloudinary: {e}"
                    )

            # delete attachment
            await db.delete(attachment)
            await db.commit()

            # if no other attachments exists for this submission, delete the submission entry
            stmt = select(SubmissionAttachment).where(
                SubmissionAttachment.submission_id == attachment.submission_id
            )
            result = await db.execute(stmt)
            attachments = result.scalars().fetchall()
            if len(attachments) == 0:
                logger.debug(
                    f"✅ No more attachments. Deleted submission {attachment.submission_id}"
                )
                stmt = delete(AssignmentSubmission).where(
                    AssignmentSubmission.submission_id == attachment.submission_id
                )
                await db.execute(stmt)
                await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
