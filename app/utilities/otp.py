import secrets

# from app.core.config import settings
# from app.core.redis import get_redis
from app.database.models.redis import OTP
# from app.services.email import send_email
# from app.services.sms_sender import send_sms


async def generate_otp(profile_id: str) -> OTP:
    value: int = int(f"{secrets.randbelow(exclusive_upper_bound=1000000):06d}")
    otp = OTP(is_profile_id=True, profile_id=profile_id, otp=value)
    return otp
    # redis = await get_redis()
    # await redis.setex(
    #     name=otp.key,
    #     time=settings.OTP_EXPIRY_SECONDS,
    #     value=otp.value
    # )

    # if email:
    #     await send_email(to_email=email, subject="Your OTP Code", content=f"Your OTP is: {otp.value}")
    # # if phone:
    # #     send_sms(phone, f"Your OTP is: {otp}")

    # return otp.value
