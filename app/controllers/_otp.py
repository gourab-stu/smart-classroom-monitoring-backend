from redis.asyncio import Redis
from sqlalchemy import select
from app.database.models.postgresql import Student
from app.schemas.auth import OTPRequestSchema, OTPVerifySchema
from app.core.sqlalchemy import async_session
from app.services.otp import generate_and_send_otp, otp_key
from app.core.redis import get_redis
from fastapi import HTTPException, status


async def request_otp(data: OTPRequestSchema):
    async with async_session() as session:
        result = await session.execute(statement=select(Student).where(Student.email == data.email))
        student = result.scalars().first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        await generate_and_send_otp(profile_id=data.email, email=data.email)
        return {"success": True, "message": "OTP sent successfully"}


async def verify_otp(data: OTPVerifySchema):
    redis: Redis = await get_redis()
    key: str = otp_key(profile_id=data.email)
    stored_otp = await redis.get(name=key)

    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired or not found")

    if str(object=stored_otp) != str(object=data.otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    await redis.delete(key)  # Invalidate OTP after successful verification
    return {"verified": True, "message": "OTP verified successfully"}
