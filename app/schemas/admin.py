from pydantic import BaseModel


class AdminRegisterRequest(BaseModel):
    admin_id: str
    password: str


class AdminRegisterResponse(BaseModel):
    admin_id: str
    success: bool
    message: str


class AdminLoginRequest(BaseModel):
    admin_id: str
    password: str


class AdminLoginResponse(BaseModel):
    admin_id: str
    success: bool
    message: str
    access_token: str
    token_type: str


class AdminLogoutResponse(BaseModel):
    success: bool
    message: str
