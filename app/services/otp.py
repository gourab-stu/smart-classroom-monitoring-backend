import secrets
from app.core.redis import get_redis
from app.services.email import send_email
# from app.services.sms_sender import send_sms

OTP_EXPIRE_SECONDS = 300


def otp_key(profile_id: str) -> str:
    return f"otp:{profile_id}"


async def generate_and_send_otp(profile_id: str, email: str) -> str:
    otp: str = f"{secrets.randbelow(exclusive_upper_bound=1000000):06d}"
    await get_redis().setex(name=otp_key(profile_id=profile_id), time=OTP_EXPIRE_SECONDS, value=otp)

    if email:
        await send_email(to_email=email, subject="Your OTP Code", content=f"Your OTP is: {otp}")
    # if phone:
    #     send_sms(phone, f"Your OTP is: {otp}")

    return otp
