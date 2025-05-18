from app.database.models.postgresql import Student
from app.schemas.auth import OTPRequestSchema


async def request_otp(data: OTPRequestSchema):
    Student.
