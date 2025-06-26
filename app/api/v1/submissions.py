# ├── submissions/
# │   └── GET /{submission_id}/attachments == > list all attachments of a submission ======= > super_admin, teacher, student (only his/her own submission)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_attachments_of_a_submission_endpoint_dependency
from app.api.exceptions import (
    attachment_not_found_exception,
    authorization_exception,
    server_error_exception,
)
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import (
    Assignment,
    AssignmentSubmission,
    SubmissionAttachment,
)
from app.schemas.api_response import MessageResponse
from app.schemas.attachment import AttachmentResponse

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.get(
    "/{submission_id}/attachments",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def get_attachments_of_a_submission_endpoint(
    submission_id: int,
    data: Annotated[dict, Depends(get_attachments_of_a_submission_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        if role == "super_admin":
            stmt = (
                select(SubmissionAttachment)
                .join(
                    AssignmentSubmission,
                    SubmissionAttachment.submission_id
                    == AssignmentSubmission.submission_id,
                )
                .where(SubmissionAttachment.submission_id == submission_id)
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
                .where(Assignment.teacher_id == user_id)
                .where(SubmissionAttachment.submission_id == submission_id)
            )
        if role == "student":
            stmt = (
                select(SubmissionAttachment)
                .join(
                    AssignmentSubmission,
                    SubmissionAttachment.submission_id
                    == AssignmentSubmission.submission_id,
                )
                .where(AssignmentSubmission.student_id == user_id)
                .where(SubmissionAttachment.submission_id == submission_id)
            )

        result = await db.execute(stmt)
        attachments = result.scalars().fetchall()

        if not attachments:
            raise (
                attachment_not_found_exception
                if role == "super_admin"
                else authorization_exception
            )

        return MessageResponse(
            content=[
                AttachmentResponse.model_validate(attachment)
                for attachment in attachments
            ],
            message="All attachments fetched",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception
