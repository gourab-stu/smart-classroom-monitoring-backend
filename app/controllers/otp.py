from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis
from app.database.models.postgresql import Student, Teacher
from app.schemas.auth import OTPRequestSchema, OTPVerifySchema
from app.services.email import send_email
from app.utilities.otp import OTP, generate_otp


async def request_otp(data: OTPRequestSchema, dbSession: AsyncSession) -> bool:
    result = await dbSession.execute(statement=select(Student).where(Student.email == data.email))
    student = result.scalars().first()

    if not student:
        next_result = await dbSession.execute(statement=select(Teacher).where(Teacher.email == data.email))
        teacher = next_result.scalars().first()
        if not teacher:
            return False

    otp: OTP = await generate_otp(profile_id=data.email)

    redis = await get_redis()
    await redis.setex(
        name=otp.key,
        time=settings.OTP_EXPIRY_SECONDS,
        value=otp.value
    )

    subject: str = "OTP verification for MLeC"
    body: str = f"Your OTP to sign in to MLeC is {otp.value}"
    await send_email(
        to_email=data.email,
        subject=subject,
        content=body
    )
    return True


async def verify_otp(data: OTPVerifySchema) -> bool:
    redis = await get_redis()
    key = OTP.get_key(is_profile_id=True, profile_id=data.email)
    stored_otp = await redis.get(key)

    if not stored_otp or str(object=stored_otp) != str(object=data.otp):
        subject: str = "Unsuccessful Sign In Attempt"
        body: str = f"Your sign in attempt on {datetime.now().strftime('%A, %d %B %Y')} at {datetime.now().strftime('%I:%M %p')} was unsuccessful"
        await send_email(
            to_email=data.email,
            subject=subject,
            content=body
        )
        return False

    await redis.delete(key)

    subject: str = "Sign In Successful"
    body: str = f"Your sign in attempt on {datetime.now().strftime('%A, %d %B %Y')} at {datetime.now().strftime('%I:%M %p')} was successful"
    await send_email(
        to_email=data.email,
        subject=subject,
        content=body
    )
    return True
