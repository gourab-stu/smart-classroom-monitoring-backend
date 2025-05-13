from typing import Optional
from beanie import Document
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel


class Student(Document):
    name: str = Field(
        default=...,
        description="Name is required and must be a string"
    )
    email: EmailStr = Field(
        default=...,
        description="Email is required and must be a valid email string"
    )
    attendance: Optional[int] = Field(
        default=0,
        ge=0,
        description="Attendance is optional and must be a non-negative integer"
    )

    class Settings:
        name: str = "students"
        indexes: list[IndexModel] = [
            IndexModel(keys=[("email", ASCENDING)], unique=True)
        ]
