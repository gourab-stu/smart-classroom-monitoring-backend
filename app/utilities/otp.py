import secrets

from app.database.models.redis import OTP


async def generate_otp(id: str) -> OTP:
    value: int = int(f"{secrets.randbelow(exclusive_upper_bound=1000000):06d}")
    otp = OTP(id, value)
    return otp
