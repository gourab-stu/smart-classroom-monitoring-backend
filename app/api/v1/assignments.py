# ├── assignments/
# │   ├── GET / ============================= > list all assignments =================== > super_admin (all), admin (all), teacher (created), student (assigned to)
# │   ├── POST / ============================ > create assignment ====================== > super_admin, teacher
# │   ├── GET /{assignment_id} ============== > get assignment by id =================== > super_admin (all), admin (all), teacher (created), student (assigned to)
# │   ├── PATCH /{assignment_id} ============ > update an assignment =================== > super_admin, teacher (creator)
# │   ├── DELETE /{assignment_id} =========== > delete assignment ====================== > super_admin, teacher (creator)
# │   ├── POST /{assignment_id}/submit ====== > submit an assignment =================== > super_admin, teacher
# │   └── GET /{assignment_id}/submissions == > list all submissions of an assignment == > super_admin, teacher

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    create_assignment_endpoint_dependency,
    delete_assignment_endpoint_dependency,
    get_assignment_by_id_endpoint_dependency,
    list_all_assignments_endpoint_dependency,
    update_assignment_endpoint_dependency,
)
from app.api.exceptions import (
    assignment_integrity_exception,
    assignment_not_found_exception,
    authorization_exception,
    server_error_exception,
)
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import Assignment, StudentPaper, User
from app.schemas.api_response import MessageResponse
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)

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
            user = result.scalars().first()

            if not user:
                raise authorization_exception

        if role not in ["super_admin", "admin"]:
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
    user_id: Annotated[int, Depends(update_assignment_endpoint_dependency)],
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


@router.post("/{assignment_id}/submit")
async def submit_assignment_endpoint(assignment_id: int):
    pass


@router.get("/{assignment_id}/submissions")
async def get_assignment_submissions_endpoint(assignment_id: int):
    pass
