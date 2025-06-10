from pydantic import BaseModel, EmailStr

from app.database.models.postgresql import User


class OTPRequestSchema(BaseModel):
    email: EmailStr


class OTPVerifySchema(OTPRequestSchema):
    otp: str


class OTPVerifySchemaExtended(OTPVerifySchema):
    user: User

    class Config:
        arbitrary_types_allowed = True


class OTPVerifyResponseSchema(BaseModel):
    is_student: bool
    otp: str
