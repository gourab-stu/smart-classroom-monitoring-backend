from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.otp import request_otp, verify_otp
from app.core.sqlalchemy import get_db_session
from app.schemas.auth import OTPRequestSchema, OTPVerifySchema


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(path="/request-otp")
async def request_otp_endpoint(otpReq: OTPRequestSchema, db: AsyncSession = Depends(get_db_session)):
    try:
        result: bool = await request_otp(otpReq, db)
        await db.close()

        if not result:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "User not found"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "OTP sent successfully"
            },
            status_code=status.HTTP_200_OK
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
        )


@router.post(path="/verify-otp")
async def verify_otp_endpoint(otpVerify: OTPVerifySchema, db: AsyncSession = Depends(get_db_session)):
    try:
        result: bool = await verify_otp(otpVerify)
        await db.close()

        if not result:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Invalid OTP"
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "OTP verification successful"
            },
            status_code=status.HTTP_200_OK
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
        )
