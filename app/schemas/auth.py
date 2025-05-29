from pydantic import BaseModel, EmailStr


class OTPRequestSchema(BaseModel):
    email: EmailStr


class OTPVerifySchema(BaseModel):
    email: EmailStr
    otp: str


class StudentInfoSchema(BaseModel):
    reg_no: str
