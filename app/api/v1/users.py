# ├── users/
# │   ├── GET /me ================> get current user ======> user (currently logged in)
# │   ├── GET / ==================> get all users =========> super_admin, admin
# │   ├── POST / =================> create an user ========> super_admin, admin
# │   ├── GET /{user_id} =========> get an user by id =====> super_admin, admin, teacher
# │   ├── PATCH /{user_id} =======> update an user by id ==> super_admin, admin
# │   └── DELETE /{user_id} ======> delete an user by id ==> super_admin, admin

import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    create_user_endpoint_dependency,
    get_all_users_endpoint_deps,
    get_me_endpoint_dependency,
    get_user_by_id_endpoint_deps,
    update_user_by_id_endpoint_deps,
)
from app.api.exceptions import (
    authorization_exception,
    elective_papers_missing_exception,
    invalid_role_exception,
    server_error_exception,
    user_email_integrity_exception,
    user_mobile_no_integrity_exception,
    usr_not_found_exception,
)
from app.core.config import get_settings
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import Paper, Role, StudentPaper, User, UserRole
from app.schemas.api_response import MessageResponse
from app.schemas.link import Link, Links
from app.schemas.main import UserRoleEnum
from app.schemas.user import UserCreate, UserResponse, UserUpdate

settings = get_settings()
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def get_me_endpoint(
    data: Annotated[dict, Depends(get_me_endpoint_dependency)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        user_id = data.get("user_id")
        role = data.get("role")

        stmt = text("""
            SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.mobile_no, u.created_at, u.updated_at, r.name as role
            FROM users u
            INNER JOIN user_role ur ON u.user_id = ur.user_id
            INNER JOIN roles r ON ur.role_id = r.role_id
            WHERE u.user_id = :user_id
        """)
        params = {"user_id": int(user_id)}
        result = await db.execute(stmt, params)
        user = result.first()

        if not user:
            raise usr_not_found_exception

        model_data = {c: getattr(user, c) for c in user._fields}

        if role == "student":
            stmt = (
                select(Paper)
                .join(StudentPaper, Paper.paper_code == StudentPaper.paper_code)
                .where(StudentPaper.student_id == user_id)
            )
            result = await db.execute(stmt)
            papers = result.scalars().all()
            model_data["papers"] = list({paper.paper_title for paper in papers})
            model_data["semester"] = papers[0].semester

        return MessageResponse(
            content=UserResponse(**model_data),
            message="User fetched successfully",
            success=True,
            links=Links(
                refresh_token=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/auth/refresh-token",
                    method="POST",
                ),
                logout=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/auth/logout",
                    method="POST",
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
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_all_users_endpoint_deps)],
)
async def get_all_users_endpoint(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
):
    try:
        stmt = text("""
            SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.mobile_no, u.created_at, u.updated_at, r.name as role
            FROM users u
            INNER JOIN user_role ur ON u.user_id = ur.user_id
            INNER JOIN roles r ON ur.role_id = r.role_id
        """)
        result = await db.execute(stmt)
        users = result.all()

        return MessageResponse(
            content=[
                MessageResponse(
                    content=UserResponse.model_validate(user),
                    links=Links(
                        view=Link(
                            url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                            method="GET",
                        ),
                        update=Link(
                            url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                            method="PUT",
                        ),
                        delete=Link(
                            url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                            method="DELETE",
                        ),
                    ),
                )
                for user in users
            ],
            message="All users fetched successfully",
            success=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    data: Annotated[UserCreate, Depends(create_user_endpoint_dependency)],
):
    try:
        user = User(**data.model_dump(exclude={"role", "semester", "elective_papers"}))

        db.add(user)

        stmt = select(Role).where(Role.name == data.role)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise invalid_role_exception

        user_role = UserRole(user_id=user.user_id, role_id=role.role_id)

        db.add(user_role)

        if data.role == "student":
            stmt = select(Paper).where(Paper.semester == data.semester)
            result = await db.execute(stmt)
            papers = result.scalars().all()

            core_papers = [
                paper.paper_code for paper in papers if paper.paper_type == "core"
            ]
            elective_papers = [
                paper.paper_code for paper in papers if paper.paper_type == "dse"
            ]

            if len(elective_papers) != 0:
                if not data.elective_papers:
                    raise elective_papers_missing_exception

                if False in [
                    paper in elective_papers for paper in data.elective_papers
                ]:
                    raise elective_papers_missing_exception

            paper_codes = (
                core_papers + data.elective_papers if data.elective_papers else []
            )

            student_papers = [
                StudentPaper(student_id=user.user_id, paper_code=paper_code)
                for paper_code in paper_codes
            ]

            db.add_all(student_papers)

        await db.commit()
        await db.refresh(user)

        model_data = {c.name: getattr(user, c.name) for c in user.__table__.columns}
        model_data["role"] = data.role
        model_data["papers"] = paper_codes if data.role == "student" else None

        return MessageResponse(
            content=UserResponse(**model_data),
            message="User created successfully",
            success=True,
            links=Links(
                me=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/me", method="GET"
                ),
                view=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                    method="GET",
                ),
                update=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                    method="PUT",
                ),
            ),
        )
    except IntegrityError as e:
        message = str(e.orig)
        logger.debug("Raw error message:", message)

        match = re.search(r'unique constraint "([^"]+)"', message)
        constraint = match.group(1) if match else None

        # Check which unique constraint was violated
        if constraint == "users_email_key":
            raise user_email_integrity_exception
        elif constraint == "users_mobile_no_key":
            raise user_mobile_no_integrity_exception
        else:
            # Generic fallback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error.",
            )
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


@router.get(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_user_by_id_endpoint_deps)],
)
async def get_user_by_id_endpoint(
    user_id: int, db: Annotated[AsyncSession, Depends(get_postgres_session)]
):
    try:
        stmt = text("""
            SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.mobile_no, u.created_at, u.updated_at, r.name as role
            FROM users u
            INNER JOIN user_role ur ON u.user_id = ur.user_id
            INNER JOIN roles r ON ur.role_id = r.role_id
            WHERE u.user_id = :user_id
        """)
        params = {"user_id": user_id}
        result = await db.execute(stmt, params)
        user = result.first()

        if not user:
            usr_not_found_exception.detail = "User not found"
            raise usr_not_found_exception

        return MessageResponse(
            content=UserResponse.model_validate(user),
            message="User fetched successfully",
            success=True,
            links=Links(
                update=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                    method="PUT",
                ),
                delete=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
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


@router.patch(
    "/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def update_user_by_id_endpoint(
    user_id: int,
    update_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    data: Annotated[dict, Depends(update_user_by_id_endpoint_deps)],
):
    try:
        role = data.get("role")
        req_user_id = data.get("user_id")

        if not req_user_id:
            raise usr_not_found_exception

        stmt = select(User).where(User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise usr_not_found_exception

        if role == "admin" and (
            update_data.first_name or update_data.middle_name or update_data.last_name
        ):
            raise authorization_exception

        update_fields = update_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(user, field, value)

        user.updated_by = int(req_user_id)

        stmt = (
            select(Role)
            .join(UserRole, Role.role_id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        await db.commit()
        await db.refresh(user)

        return MessageResponse(
            content=UserResponse(
                user_id=user.user_id,
                first_name=user.first_name,
                middle_name=user.middle_name,
                last_name=user.last_name,
                email=user.email,
                mobile_no=user.mobile_no,
                role=UserRoleEnum(role.name),  # type: ignore
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
            message="User updated successfully",
            success=True,
            links=Links(
                view=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                    method="GET",
                ),
                delete=Link(
                    url=f"{settings.BASE_URL}/{settings.VERSION}/users/{user.user_id}",
                    method="DELETE",
                ),
            ),
        )
    except IntegrityError as e:
        message = str(e.orig)
        logger.debug("Raw error message:", message)

        match = re.search(r'unique constraint "([^"]+)"', message)
        constraint = match.group(1) if match else None

        # Check which unique constraint was violated
        if constraint == "users_email_key":
            raise user_email_integrity_exception
        elif constraint == "users_mobile_no_key":
            raise user_mobile_no_integrity_exception
        else:
            # Generic fallback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error.",
            )
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


# @router.delete("/{user_id}", status_code=status.HTTP_200_OK)
# async def delete_user_by_id_endpoint():
#     pass
