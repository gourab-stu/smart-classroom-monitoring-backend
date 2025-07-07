# ├── assignments/
# │   ├── GET / ============================= > list all assignments =================== > super_admin (all), admin (all), teacher (created), student (assigned to)
# │   ├── POST / ============================ > create assignment ====================== > super_admin, teacher
# │   ├── GET /{assignment_id} ============== > get assignment by id =================== > super_admin (all), admin (all), teacher (created), student (assigned to)
# │   ├── PATCH /{assignment_id} ============ > update an assignment =================== > super_admin, teacher (creator)
# │   ├── DELETE /{assignment_id} =========== > delete assignment ====================== > super_admin, teacher (creator)
# │   ├── POST /{assignment_id}/attachment == > add an attachment to assignment ======== > super_admin, student (assigned to)
# │   └── GET /{assignment_id}/submissions == > list all submissions of an assignment == > super_admin, teacher (creator)

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    add_attachment_to_assignment_endpoint_dependency,
    create_assignment_endpoint_dependency,
    delete_assignment_endpoint_dependency,
    get_assignment_by_id_endpoint_dependency,
    get_assignment_submissions_endpoint_dependency,
    list_all_assignments_endpoint_dependency,
    update_assignment_endpoint_dependency,
)
from app.api.exceptions import (
    assignment_integrity_exception,
    assignment_not_found_exception,
    authorization_exception,
    file_size_exceeds_exception,
    filetype_exception,
    no_submissions_found_exception,
    server_error_exception,
)
from app.core.config import get_settings
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import (
    Assignment,
    AssignmentSubmission,
    StudentPaper,
    SubmissionAttachment,
    User,
)
from app.schemas.api_response import MessageResponse
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.schemas.link import Link, Links
from app.schemas.submission import SubmissionResponse
from app.tasks.attachment import upload_assignment_attachment

settings = get_settings()
router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.get("/", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def list_all_assignments_endpoint(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    data: Annotated[dict, Depends(list_all_assignments_endpoint_dependency)],
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        if role in ["super_admin", "admin"]:
            stmt = select(Assignment)
        if role == "teacher":
            stmt = select(Assignment).where(Assignment.teacher_id == user_id)
        if role == "student":
            stmt = (
                select(Assignment)
                .join(StudentPaper, Assignment.paper_code == StudentPaper.paper_code)
                .where(StudentPaper.student_id == user_id)
            )

        result = await db.execute(stmt)
        assignments = result.scalars().all()
        assignment_schemas = [AssignmentResponse.model_validate(a) for a in assignments]

        return MessageResponse(
            content=assignment_schemas,
            message=f"All {'of your ' if role in ['teacher', 'student'] else ''}assignments fetched successfully",
            success=True,
        )
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment_endpoint(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    data: Annotated[AssignmentCreate, Depends(create_assignment_endpoint_dependency)],
):
    try:
        assignment = Assignment(**data.model_dump())

        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        return MessageResponse(
            content=AssignmentResponse.model_validate(assignment),
            message="Assignment created successfully",
            success=True,
        )
    except IntegrityError:
        raise assignment_integrity_exception
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.get(
    "/{assignment_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def get_assignment_by_id_endpoint(
    assignment_id: int,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    data: Annotated[dict, Depends(get_assignment_by_id_endpoint_dependency)],
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise assignment_not_found_exception

        if role == "teacher":
            if assignment.teacher_id != user_id:
                raise authorization_exception

        if role == "student":
            stmt = (
                select(User)
                .join(StudentPaper, User.user_id == StudentPaper.student_id)
                .where(StudentPaper.paper_code == assignment.paper_code)
                .where(User.user_id == user_id)
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise authorization_exception

        return MessageResponse(
            content=AssignmentResponse.model_validate(assignment),
            message="Assignment fetched successfully",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.patch(
    "/{assignment_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def update_assignment_endpoint(
    assignment_id: int,
    update_data: AssignmentUpdate,
    data: Annotated[dict, Depends(update_assignment_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise assignment_not_found_exception

        if role == "teacher" and assignment.teacher_id != user_id:
            raise authorization_exception

        update_fields = update_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(assignment, field, value)

        await db.commit()
        await db.refresh(assignment)

        return MessageResponse(
            content=AssignmentResponse.model_validate(assignment),
            message="Assignment updated",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.delete(
    "/{assignment_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def delete_assignment_endpoint(
    assignment_id: int,
    user_id: Annotated[int, Depends(delete_assignment_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise assignment_not_found_exception

        if assignment.teacher_id != user_id:
            raise authorization_exception

        stmt = delete(Assignment).where(Assignment.assignment_id == assignment_id)
        await db.execute(stmt)
        await db.commit()

        return MessageResponse(message="Assignment deleted successfully", success=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.post(
    "/{assignment_id}/attachment",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def add_attachment_to_assignment_endpoint(
    assignment_id: int,
    file: Annotated[UploadFile, File(...)],
    data: Annotated[dict, Depends(add_attachment_to_assignment_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    bg_tasks: BackgroundTasks,
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        if not file.filename:
            raise filetype_exception

        ext = file.filename.split(".")[-1].lower()
        if ext not in settings.ALLOWED_FILE_TYPES:
            raise filetype_exception

        original_filename = file.filename
        mime_type = file.content_type
        content = await file.read()
        file_size = len(content)

        if file_size > settings.MAX_FILE_SIZE:
            raise file_size_exceeds_exception

        # find assignment with assignment_id depending on their role
        if role == "super_admin":
            stmt = select(Assignment).where(Assignment.assignment_id == assignment_id)
        if role == "student":
            stmt = (
                select(Assignment)
                .join(StudentPaper, Assignment.paper_code == StudentPaper.paper_code)
                .where(StudentPaper.student_id == user_id)
                .where(Assignment.assignment_id == assignment_id)
            )

        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()

        # if it doesn't exist raise exception
        if not assignment:
            raise (
                assignment_not_found_exception
                if role == "super_admin"
                else authorization_exception
            )

        # Generate unique file_id
        base_dir = Path(__file__).resolve().parent.parent.parent.parent  # ./app/api/v1/
        upload_dir = base_dir / "static" / "uploads" / "attachments"
        upload_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        while True:
            file_id = uuid.uuid4().hex
            conflict = any(
                f.is_file() and f.name.startswith(file_id) for f in upload_dir.iterdir()
            )
            if not conflict:
                break  # Found unique file_id

        # Write content to disk
        file_path = upload_dir / f"{file_id}.{ext}"
        with open(file_path, "wb") as f:
            f.write(content)

        # check if any submission entry already exists or not
        stmt = (
            select(AssignmentSubmission)
            .join(
                Assignment,
                AssignmentSubmission.assignment_id == Assignment.assignment_id,
            )
            .where(AssignmentSubmission.assignment_id == assignment_id)
            .where(AssignmentSubmission.student_id == user_id)
        )
        result = await db.execute(stmt)
        submission = result.scalar_one_or_none()

        # if no submission entry exists, create one
        if not submission:
            submission = AssignmentSubmission(
                assignment_id=assignment_id, student_id=user_id
            )
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

        # create an attachment
        attachment = SubmissionAttachment(
            submission_id=submission.submission_id,
            original_filename=original_filename,
            stored_filename=f"{file_id}.{ext}",
            file_size=file_size,
            mime_type=mime_type,
        )
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)

        # add background task to upload file to cloudinary
        bg_tasks.add_task(
            upload_assignment_attachment,
            assignment_id=assignment_id,
            attachment_id=attachment.attachment_id,
            stored_filename=attachment.stored_filename,
        )

        # send response with uniform interfaces
        return MessageResponse(
            message="Attachment uploaded successfully.",
            success=True,
            links=Links(
                view=Link(
                    url=f"/attachments/{attachment.attachment_id}",
                    method="GET",
                ),
                delete=Link(
                    url=f"/attachments/{attachment.attachment_id}",
                    method="DELETE",
                ),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.get(
    "/{assignment_id}/submissions",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def get_assignment_submissions_endpoint(
    assignment_id: int,
    data: Annotated[dict, Depends(get_assignment_submissions_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        role = data.get("role")
        user_id = data.get("user_id")

        if role == "super_admin":
            stmt = select(AssignmentSubmission).where(
                AssignmentSubmission.assignment_id == assignment_id
            )
        if role == "teacher":
            stmt = (
                select(AssignmentSubmission)
                .join(
                    Assignment,
                    AssignmentSubmission.assignment_id == Assignment.assignment_id,
                )
                .where(AssignmentSubmission.assignment_id == assignment_id)
                .where(Assignment.teacher_id == user_id)
            )

        result = await db.execute(stmt)
        submissions = result.scalars().fetchall()

        if not submissions:
            raise (
                no_submissions_found_exception
                if role == "super_admin"
                else authorization_exception
            )

        return MessageResponse(
            content=[
                SubmissionResponse.model_validate(submission)
                for submission in submissions
            ],
            message="All submissions fetched",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception
