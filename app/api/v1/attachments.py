# ├── attachments/
# │   ├── GET /{attachment_id} ===== > get attachment by attachment id ===== > super_admin (all), admin (all), teacher (created), student (assigned to)
# │   └── DELETE /{attachment_id} == > delete attachment by attachment id == > super_admin, teacher (creator)

import tempfile
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_attachment_by_attachment_id_endpoint_dependency
from app.api.exceptions import (
    attachment_not_found_exception,
    authorization_exception,
    server_error_exception,
)
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import (
    Assignment,
    AssignmentSubmission,
    StudentPaper,
    SubmissionAttachment,
)
from app.tasks.file_handler import cleanup_temp_file

router = APIRouter(prefix="/attachments", tags=["Attachments"])


@router.get("/{attachment_id}", status_code=status.HTTP_200_OK)
async def get_attachment_by_attachment_id_endpoint(
    attachment_id: int,
    data: Annotated[dict, Depends(get_attachment_by_attachment_id_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    bg_tasks: BackgroundTasks,
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        if role == "super_admin":
            stmt = select(SubmissionAttachment).where(
                SubmissionAttachment.attachment_id == attachment_id
            )
        if role == "teacher":
            stmt = (
                select(SubmissionAttachment)
                .join(
                    AssignmentSubmission,
                    SubmissionAttachment.submission_id
                    == AssignmentSubmission.submission_id,
                )
                .join(
                    Assignment,
                    AssignmentSubmission.assignment_id == Assignment.assignment_id,
                )
                .where(SubmissionAttachment.attachment_id == attachment_id)
                .where(Assignment.teacher_id == user_id)
            )
        if role == "student":
            stmt = (
                select(SubmissionAttachment)
                .join(
                    AssignmentSubmission,
                    SubmissionAttachment.submission_id
                    == AssignmentSubmission.submission_id,
                )
                .join(
                    Assignment,
                    AssignmentSubmission.assignment_id == Assignment.assignment_id,
                )
                .join(StudentPaper, Assignment.paper_code == StudentPaper.paper_code)
                .where(SubmissionAttachment.attachment_id == attachment_id)
                .where(StudentPaper.student_id == user_id)
            )

        result = await db.execute(stmt)
        attachment = result.scalar_one_or_none()

        # if attchment is not found send exception
        if not attachment:
            raise (
                attachment_not_found_exception
                if role == "super_admin"
                else authorization_exception
            )

        # if attchment.file_url is not found try to find the file in the static folder
        if not attachment.file_url:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            file_dir = base_dir / "static" / "uploads"

            # search folder for the mentioned file
            for file in file_dir.iterdir():
                if file.is_file() and file.name.startswith(
                    f"attachment.{attachment_id}"
                ):
                    # add file cleanup task
                    bg_tasks.add_task(cleanup_temp_file, file.name)

                    # Serve file
                    return FileResponse(
                        path=file.name,
                        filename=f"{attachment.original_filename}",
                        media_type=f"{attachment.mime_type}",
                        headers={
                            "Content-Disposition": f"inline; filename={attachment.original_filename}"
                        },
                    )

            # if file not found, send exceptions
            raise attachment_not_found_exception

        else:
            # Download remote file to a temp file
            async with httpx.AsyncClient() as client:
                response = await client.get(attachment.file_url)
                if response.status_code != 200:
                    raise attachment_not_found_exception

            # Write to temp file
            tmp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=attachment.file_url.split(".")[-1]
            )
            tmp_file.write(response.content)
            tmp_file.close()

            # add file cleanup task
            bg_tasks.add_task(cleanup_temp_file, tmp_file.name)

            # Serve file
            return FileResponse(
                path=tmp_file.name,
                filename=f"{attachment.original_filename}",
                media_type=f"{attachment.mime_type}",
                headers={
                    "Content-Disposition": f"inline; filename={attachment.original_filename}"
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception
