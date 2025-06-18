# └── auth/
#     ├── POST /request-otp ==== > request otp from client == > no role required
#     ├── POST /verify-otp ===== > verify incoming otp ====== > no role required
#     ├── POST /logout ========= > logout client ============ > no role required
#     └── POST /refresh-token == > refresh incoming token === > no role required

from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from loguru import logger
from redis import Redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_refresh_token_from_cookie,
    get_user_from_otp_request,
    get_user_from_otp_verify_request,
)
from app.api.exceptions import (
    auth_failure_exception,
    invalid_otp_exception,
    invalid_refresh_token_exception,
    logout_failure_exception,
    multiple_otp_request_exception,
    otp_expired_exception,
    otp_sending_failed_exception,
    token_refreshing_failure,
    usr_not_found_exception,
)
from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.core.sqlalchemy import get_postgres_session
from app.database.models.postgresql import User
from app.database.models.redis import OTP
from app.schemas.api_response import MessageResponse
from app.schemas.otp import OTPVerifySchemaExtended
from app.services.email import send_email
from app.utilities.otp import generate_otp

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post(
    "/request-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def request_otp_endpoint(
    user: Annotated[User, Depends(get_user_from_otp_request)],
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    """Request OTP for user authentication"""
    try:
        # Check rate limiting
        rate_limit_key = f"otp_rate_limit:{user.user_id}"
        if await redis.exists(rate_limit_key):
            raise multiple_otp_request_exception

        # Set rate limit (1 OTP per minute)
        await redis.setex(rate_limit_key, 60, "1")

        # Generate OTP
        otp: OTP = await generate_otp(id=str(user.user_id))

        # Store OTP in Redis
        await redis.setex(
            name=otp.key, time=settings.OTP_EXPIRY_SECONDS, value=otp.value
        )

        # # Send email
        # subject = "OTP verification for MLeC"
        # body = f"Your OTP to sign in to MLeC is {otp.value}. This OTP will expire in {settings.OTP_EXPIRY_SECONDS // 60} minutes."
        # await send_email(to_email=user.email, subject=subject, content=body)

        return MessageResponse(success=True, message="OTP sent successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise otp_sending_failed_exception


@router.post(
    "/verify-otp", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def verify_otp_endpoint(
    data: Annotated[OTPVerifySchemaExtended, Depends(get_user_from_otp_verify_request)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    response: Response,
):
    """Verify OTP and return access token"""
    user = data.user
    otp = data.otp

    # Generate OTP key
    key = OTP.get_key(str(user.user_id))

    # Get value for key
    value = await redis.get(key)

    # Validate OTP
    if not value:
        raise otp_expired_exception

    if otp != value:
        raise invalid_otp_exception

    # Delete OTP after successful verification
    await redis.delete(key)

    try:
        # Get user role
        result = await db.execute(
            text("""
                SELECT r.name 
                FROM roles r 
                INNER JOIN user_role ur ON ur.role_id = r.role_id 
                INNER JOIN users u ON u.user_id = ur.user_id 
                WHERE u.user_id = :user_id
            """),
            {"user_id": user.user_id},
        )
        role = result.scalars().first()

        # # Get user permissions
        # result = await db.execute(
        #     text("""
        #         SELECT p.name
        #         FROM permissions p
        #         INNER JOIN role_permissions rp ON rp.permission_id = p.permission_id
        #         INNER JOIN roles r ON rp.role_id = r.role_id
        #         INNER JOIN user_role ur ON ur.role_id = r.role_id
        #         INNER JOIN users u ON u.user_id = ur.user_id
        #         WHERE u.user_id = :user_id
        #     """),
        #     {"user_id": user.user_id},
        # )
        # permissions = result.scalars().all()

        # Generate tokens
        current_time = datetime.now(timezone.utc)

        access_token_data = {
            "sub": str(user.user_id),
            "role": role,
            # "permissions": permissions,
            "type": "access",
            "iat": current_time,
            "exp": current_time + settings.ACCESS_TOKEN_EXPIRY,
        }

        refresh_token_data = {
            "sub": str(user.user_id),
            "type": "refresh",
            "iat": current_time,
            "exp": current_time + settings.REFRESH_TOKEN_EXPIRY,
        }

        access_token = jwt.encode(
            access_token_data,
            settings.ACCESS_TOKEN_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        refresh_token = jwt.encode(
            refresh_token_data,
            settings.REFRESH_TOKEN_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Store refresh token hash in Redis for validation
        refresh_key = f"refresh_token:{user.user_id}"
        await redis.setex(
            refresh_key,
            int(settings.REFRESH_TOKEN_EXPIRY.total_seconds()),
            refresh_token,
        )

        # Set secure HTTP-only cookie
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=int(settings.REFRESH_TOKEN_EXPIRY.total_seconds()),
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return MessageResponse(
            success=True,
            message="OTP verified successfully",
            content={"access_token": access_token},
        )

    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise auth_failure_exception


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout_endpoint(
    user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    response: Response,
    authorization: Annotated[str, Header()],
):
    """Logout user and invalidate tokens"""
    try:
        # Extract access token
        access_token = authorization[7:].strip()

        # Decode to get expiration
        payload: dict = jwt.decode(
            access_token,
            settings.ACCESS_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Calculate remaining TTL
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            remaining_ttl = int(
                (exp_datetime - datetime.now(timezone.utc)).total_seconds()
            )

            if remaining_ttl > 0:
                # Blacklist the access token
                blacklist_key = f"blacklist:{access_token}"
                await redis.setex(blacklist_key, remaining_ttl, "1")

        # Remove refresh token from Redis
        refresh_key = f"refresh_token:{user.user_id}"
        await redis.delete(refresh_key)

        # Clear refresh token cookie
        response.delete_cookie("refresh_token")

        return MessageResponse(success=True, message="Logged out successfully")

    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise logout_failure_exception


@router.post(
    "/refresh-token",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token_endpoint(
    refresh_token: Annotated[str, Depends(get_refresh_token_from_cookie)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    db: Annotated[AsyncSession, Depends(get_postgres_session)],
    response: Response,
):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload: dict = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id or token_type != "refresh":
            raise invalid_refresh_token_exception

        # Verify refresh token exists in Redis
        refresh_key = f"refresh_token:{user_id}"
        stored_token = await redis.get(refresh_key)

        if not stored_token or stored_token != refresh_token:
            raise invalid_refresh_token_exception

        # Get user from database
        stmt = select(User).where(User.user_id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise usr_not_found_exception

        # Get user role and permissions (similar to verify_otp)
        result = await db.execute(
            text("""
                SELECT r.name 
                FROM roles r 
                INNER JOIN user_role ur ON ur.role_id = r.role_id 
                INNER JOIN users u ON u.user_id = ur.user_id 
                WHERE u.user_id = :user_id
            """),
            {"user_id": user.user_id},
        )
        role = result.scalars().first()

        # result = await db.execute(
        #     text("""
        #         SELECT p.name
        #         FROM permissions p
        #         INNER JOIN role_permissions rp ON rp.permission_id = p.permission_id
        #         INNER JOIN roles r ON rp.role_id = r.role_id
        #         INNER JOIN user_role ur ON ur.role_id = r.role_id
        #         INNER JOIN users u ON u.user_id = ur.user_id
        #         WHERE u.user_id = :user_id
        #     """),
        #     {"user_id": user.user_id},
        # )
        # permissions = result.scalars().all()

        # Generate new access token
        current_time = datetime.now(timezone.utc)
        access_token_data = {
            "sub": str(user.user_id),
            "role": role,
            # "permissions": permissions,
            "type": "access",
            "iat": current_time,
            "exp": current_time + settings.ACCESS_TOKEN_EXPIRY,
        }

        new_access_token = jwt.encode(
            access_token_data,
            settings.ACCESS_TOKEN_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        return MessageResponse(
            success=True,
            message="Token refreshed successfully",
            content={"access_token": new_access_token},
        )

    except jwt.PyJWTError:
        raise invalid_refresh_token_exception
    except Exception as e:
        logger.error(e)
        logger.error(e.__class__)
        raise token_refreshing_failure
