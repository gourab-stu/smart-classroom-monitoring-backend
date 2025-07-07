from pydantic import EmailStr, Field
from app.schemas.main import BaseSchema
from app.schemas.user import UserResponse


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class LoginResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class PasswordResetRequest(BaseSchema):
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerificationRequest(BaseSchema):
    token: str
