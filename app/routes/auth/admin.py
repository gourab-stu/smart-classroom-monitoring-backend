from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.sqlalchemy import get_db_session
from app.database.models.postgresql import Admin
from app.schemas.admin import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminLogoutResponse,
    AdminRegisterRequest,
    AdminRegisterResponse,
)
from app.utilities.token import decode_token


router = APIRouter(prefix="/admin", tags=["Auth - Admin"])


@router.post(
    path="/register",
    response_model=AdminRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def admin_register_endpoint(
    adminRegReq: AdminRegisterRequest, db: AsyncSession = Depends(get_db_session)
) -> AdminRegisterResponse:
    # check if an admin exists with the provided admin_id
    result = await db.execute(
        select(Admin).where(Admin.admin_id == adminRegReq.admin_id)
    )
    existing_admin = result.scalar_one_or_none()

    # if exists, return already exists error
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "An admin already exists with this ID",
                "success": False,
            },
        )

    # create a new admin with the provided credentials
    new_admin = Admin(admin_id=adminRegReq.admin_id, password=adminRegReq.password)

    # create a new admin with the provided credentials and close database connection
    db.add(new_admin)
    await db.commit()
    await db.close()

    return AdminRegisterResponse(
        admin_id=new_admin.admin_id, success=True, message="Admin created successfully"
    )


@router.post(
    path="/login", response_model=AdminLoginResponse, status_code=status.HTTP_200_OK
)
async def admin_login_endpoint(
    adminLogReq: AdminLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    # fetch the admin with the provided admin_id
    result = await db.execute(
        select(Admin).where(Admin.admin_id == adminLogReq.admin_id)
    )
    existing_admin = result.scalar_one_or_none()

    # if the admin doesn't exist or
    # if the provided password doesn't match with the existing admin password raise 401 error
    if not existing_admin or not existing_admin.verify_password(adminLogReq.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid Credentials", "success": False},
        )

    # generate access and refresh tokens
    access_token = existing_admin.generate_access_token(
        {"admin_id": existing_admin.admin_id}
    )
    refresh_token = existing_admin.generate_refresh_token(
        {"admin_id": existing_admin.admin_id}
    )

    # save changes to database and close connection
    await db.commit()
    await db.close()

    # send refresh_tokens via httpcookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRY.seconds,
        httponly=True,
    )

    # send access tokens via json response
    return AdminLoginResponse(
        admin_id=existing_admin.admin_id,
        success=True,
        message="Admin login successful",
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    path="/logout", response_model=AdminLogoutResponse, status_code=status.HTTP_200_OK
)
async def admin_logout_endpoint(
    request: Request, response: Response, db: AsyncSession = Depends(get_db_session)
):
    # checking the admin is logged in or not
    token = request.cookies.get("refresh_token")
    print(token)
    if token:
        # decoding and processing the payload
        payload = decode_token(
            token, settings.REFRESH_TOKEN_SECRET, settings.JWT_ALGORITHM
        )
        print(payload)
        if payload:
            admin_id = payload.get("admin_id")
            admin = (
                (await db.execute(select(Admin).where(Admin.admin_id == admin_id)))
                .scalars()
                .first()
            )
            print(admin)
            if admin:
                # resetting the refresh_token of both admin and from database
                admin.refresh_token = None
                await db.commit()
                await db.close()
                print(admin)
                response.delete_cookie("refresh_token")
                return AdminLogoutResponse(
                    success=True, message="Admin logout successful"
                )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized request"
    )


__all__ = ["router"]
