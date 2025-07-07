from typing import Annotated, Optional

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, Request
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import (
    authorization_exception,
    credentials_exception,
    email_empty_exception,
    logout_exception,
    revoke_token_exception,
    server_error_exception,
    usr_not_found_exception,
)
from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import User
from app.schemas.assignment import AssignmentBase, AssignmentCreate
from app.schemas.otp import OTPRequestSchema, OTPVerifySchema, OTPVerifySchemaExtended
from app.schemas.user import UserBase, UserCreate

settings = get_settings()


# # helper methods


async def check_auth_header_refresh_token_and_get_user_id(
    authorization: str, redis: Redis, refresh_token: str
):
    try:
        # Validate authorization header format
        if not authorization or not authorization.lower().startswith("bearer "):
            raise credentials_exception

        # Extract token
        access_token = authorization[7:].strip()
        if not access_token:
            raise credentials_exception

        # Check if token is blacklisted
        blacklist_key = f"blacklist:{access_token}"
        if await redis.exists(blacklist_key):
            raise revoke_token_exception

        # Decode token
        try:
            access_payload: dict = jwt.decode(
                access_token,
                settings.ACCESS_TOKEN_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            refresh_payload: dict = jwt.decode(
                refresh_token,
                settings.REFRESH_TOKEN_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.PyJWTError as e:
            logger.error(e)
            credentials_exception.detail = str(e)
            raise credentials_exception

        # Validate token type
        if access_payload.get("type") != "access":
            raise credentials_exception
        if refresh_payload.get("type") != "refresh":
            raise credentials_exception

        # Extract user ID
        user_id = access_payload.get("sub")
        if not user_id:
            raise credentials_exception
        another_user_id = refresh_payload.get("sub")
        if not another_user_id:
            raise credentials_exception

        # Validate if user ID from access and refresh token
        if user_id != another_user_id:
            raise credentials_exception

        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


async def role_checker(db: AsyncSession, authorization: str, refresh_token: str):
    """Dependency to check the role of the current user using JWT token"""

    try:
        redis = get_redis_client()
        user_id = await check_auth_header_refresh_token_and_get_user_id(
            authorization, redis, refresh_token
        )

        # Fetch role from database
        stmt = text("""
            SELECT r.name
            FROM roles r
            INNER JOIN user_role ur ON r.role_id = ur.role_id
            WHERE ur.user_id = :user_id
        """)
        params = {"user_id": int(user_id)}
        result = await db.execute(stmt, params)
        role_in_db = result.scalar_one_or_none()

        if not role_in_db:
            raise credentials_exception

        token = authorization[7:].strip()
        payload: dict = jwt.decode(
            token, settings.ACCESS_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract role
        role_in_token = payload.get("role")

        if role_in_db != role_in_token:
            raise credentials_exception

        return {"role": role_in_db, "user_id": int(user_id)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


# # dependency injections


# auth


async def request_otp_endpoint_dependency(
    otpReq: OTPRequestSchema,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    refresh_token: Optional[str] = Cookie(default=None),
):
    """Dependency to validate and return user from OTP request"""
    try:
        if refresh_token:
            raise logout_exception

        if not otpReq.email or not otpReq.email.strip():
            raise email_empty_exception

        result = await db.execute(
            select(User).where(User.email == otpReq.email.lower())
        )
        user = result.scalars().first()

        if not user:
            raise usr_not_found_exception

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


async def verify_otp_endpoint_dependency(
    otpVerify: OTPVerifySchema,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    refresh_token: Optional[str] = Cookie(default=None),
):
    """Dependency to validate and return user from OTP verify request"""
    try:
        if refresh_token:
            raise logout_exception
        if not otpVerify.email or not otpVerify.email.strip():
            raise email_empty_exception

        result = await db.execute(
            select(User).where(User.email == otpVerify.email.lower())
        )
        user = result.scalars().first()

        if not user:
            raise usr_not_found_exception

        return OTPVerifySchemaExtended(
            email=otpVerify.email, otp=otpVerify.otp, user=user
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


async def logout_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> User:
    """Dependency to get current user from JWT token"""

    user_id = await check_auth_header_refresh_token_and_get_user_id(
        authorization, redis, refresh_token
    )

    try:
        # Fetch user from database
        stmt = select(User).where(User.user_id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise credentials_exception

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


async def refresh_token_endpoint_dependency(request: Request):
    """Extract refresh token from HTTP-only cookie"""
    token = request.cookies.get("refresh_token")
    if not token:
        raise
    return token


# assignments


async def list_all_assignments_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "admin", "teacher", "student"]:
        raise authorization_exception

    return data


async def create_assignment_endpoint_dependency(
    baseAssignment: AssignmentBase,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = str(data.get("role"))
    user_id = str(data.get("user_id"))

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    newAssignment = AssignmentCreate(
        paper_code=baseAssignment.paper_code,
        title=baseAssignment.title,
        description=baseAssignment.description,
        assignment_type=baseAssignment.assignment_type,
        due_date=baseAssignment.due_date,
        assigned_date=baseAssignment.assigned_date,
        instructions=baseAssignment.instructions,
        is_active=baseAssignment.is_active,
        teacher_id=int(user_id),
    )

    return newAssignment


async def get_assignment_by_id_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "admin", "teacher", "student"]:
        raise authorization_exception

    return data


async def update_assignment_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return data


async def delete_assignment_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return user_id


async def add_attachment_to_assignment_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "student"]:
        raise authorization_exception

    return data


async def get_assignment_submissions_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return data


# attachments


async def get_attachment_by_id_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher", "student"]:
        raise authorization_exception

    return data


async def delete_attachment_by_id_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "student"]:
        raise authorization_exception

    return data


# submissions


async def get_attachments_of_a_submission_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher", "student"]:
        raise authorization_exception

    return data


# users


async def get_me_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    # role = data.get("role")
    user_id = data.get("user_id")

    return user_id


async def create_user_endpoint_dependency(
    userBase: UserBase,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    user_id = data.get("user_id")

    if not user_id:
        raise authorization_exception

    if role not in ["super_admin", "admin"]:
        raise authorization_exception

    if userBase.role == "super_admin" and role != "super_admin":
        raise authorization_exception

    # new_user = UserCreate(
    #     first_name=userBase.first_name,
    #     middle_name=userBase.middle_name,
    #     last_name=userBase.last_name,
    #     email=userBase.email,
    #     mobile_no=userBase.mobile_no,
    #     role=userBase.role,
    #     created_by=int(user_id),
    # )
    new_user = UserCreate(**userBase.model_dump(), created_by=int(user_id))

    return new_user


async def update_user_by_id_endpoint_deps(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return data


# # dependencies


# users


async def get_all_users_endpoint_deps(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "admin"]:
        raise authorization_exception


async def get_user_by_id_endpoint_deps(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    refresh_token: Annotated[str, Cookie()],
):
    data = await role_checker(db, authorization, refresh_token)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "admin", "teacher"]:
        raise authorization_exception
