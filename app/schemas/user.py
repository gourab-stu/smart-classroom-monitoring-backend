from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from app.schemas.main import BaseSchema, UserRoleEnum


class UserBase(BaseSchema):
    # all roles
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    mobile_no: str
    role: UserRoleEnum
    # student
    semester: Optional[int] = None
    elective_papers: Optional[list[str]] = None


class UserCreate(UserBase):
    created_by: int


class UserUpdate(BaseSchema):
    # all roles
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_no: Optional[str] = None
    # student
    semester: Optional[int] = None
    elective_papers: Optional[list[str]] = None


class UserResponse(UserBase):
    # all roles
    user_id: int
    # user
    papers: Optional[list[str]] = None
    # admin, super_admin
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
