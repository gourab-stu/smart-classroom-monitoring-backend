import secrets

from app.database.models.redis import OTP


async def generate_otp(id: str) -> OTP:
    value: int = int("".join(secrets.choice("123456789") for _ in range(6)))
    otp = OTP(id, value)
    return otp
