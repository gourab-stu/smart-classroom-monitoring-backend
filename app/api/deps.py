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

settings = get_settings()


# # helper methods


async def check_auth_header_and_get_user_id(
    authorization: str,
    redis: Redis,
):
    try:
        # Validate authorization header format
        if not authorization or not authorization.lower().startswith("bearer "):
            raise credentials_exception

        # Extract token
        token = authorization[7:].strip()
        if not token:
            raise credentials_exception

        # Check if token is blacklisted
        blacklist_key = f"blacklist:{token}"
        if await redis.exists(blacklist_key):
            raise revoke_token_exception

        # Decode token
        try:
            payload: dict = jwt.decode(
                token, settings.ACCESS_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.PyJWTError as e:
            logger.error(e)
            credentials_exception.detail = str(e)
            raise credentials_exception

        # Validate token type
        if payload.get("type") != "access":
            raise credentials_exception

        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception

        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise server_error_exception


async def role_checker(db: AsyncSession, authorization: str):
    """Dependency to check the role of the current user using JWT token"""

    try:
        redis = get_redis_client()
        user_id = await check_auth_header_and_get_user_id(authorization, redis)

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


async def get_user_from_otp_request(
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


async def get_user_from_otp_verify_request(
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


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> User:
    """Dependency to get current user from JWT token"""

    user_id = await check_auth_header_and_get_user_id(authorization, redis)

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


async def get_refresh_token_from_cookie(request: Request):
    """Extract refresh token from HTTP-only cookie"""
    token = request.cookies.get("refresh_token")
    if not token:
        raise
    return token


# assignments


async def list_all_assignments_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "admin", "teacher", "student"]:
        raise authorization_exception

    return data


async def create_assignment_endpoint_dependency(
    baseAssignment: AssignmentBase,
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

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
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "admin", "teacher", "student"]:
        raise authorization_exception

    return data


async def update_assignment_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return user_id


async def delete_assignment_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return user_id


async def add_attachment_to_assignment_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "student"]:
        raise authorization_exception

    return data


# attachments


async def get_attachment_by_attachment_id_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher", "student"]:
        raise authorization_exception

    return data


async def get_assignment_submissions_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher"]:
        raise authorization_exception

    return data


# submissions


async def get_attachments_of_a_submission_endpoint_dependency(
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    authorization: Annotated[str, Header()],
):
    data = await role_checker(db, authorization)

    role = data.get("role")
    # user_id = data.get("user_id")

    if role not in ["super_admin", "teacher", "student"]:
        raise authorization_exception

    return data


# # dependencies
