from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.otp import request_otp, verify_otp
from app.core.sqlalchemy import get_db_session
from app.database.models.postgresql import Student
from app.schemas.auth import OTPRequestSchema, OTPVerifySchema
from app.services.otp import generate_and_send_otp


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(path="/request-otp")
async def request_otp_endpoint(otpReq: OTPRequestSchema, db: AsyncSession = Depends(get_db_session)):
    # data = await req.json()

    result = await db.execute(select(Student).where(Student.email == otpReq.email))
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    await generate_and_send_otp(profile_id=otpReq.email, email=otpReq.email)
    return {"success": True, "message": "OTP sent successfully"}


@router.post(path="/verify-otp")
async def verify_otp_endpoint(req: Request, db: AsyncSession = Depends(get_db_session)):
    data = await req.json()
    otpVerify = OTPVerifySchema(email=data['email'], otp=data['otp'])
    return await verify_otp(data=otpVerify)
