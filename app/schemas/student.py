from pydantic import BaseModel, EmailStr, constr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    full_name: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    full_name: str
