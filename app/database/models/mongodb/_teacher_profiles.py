# from typing import Optional
# from beanie import Document
# from pydantic import EmailStr, Field
# from pymongo import ASCENDING, IndexModel


# class Student(Document):
#     name: str = Field(
#         default=...,
#         description="Name is required and must be a string"
#     )
#     email: EmailStr = Field(
#         default=...,
#         description="Email is required and must be a valid email string"
#     )
#     attendance: Optional[int] = Field(
#         default=0,
#         ge=0,
#         description="Attendance is optional and must be a non-negative integer"
#     )

#     class Settings:
#         name: str = "students"
#         indexes: list[IndexModel] = [
#             IndexModel(keys=[("email", ASCENDING)], unique=True)
#         ]


# teacher_profile.py
from typing import List
from beanie import Document, Link

from app.database.models.mongodb._assignments import _assignment
from app.database.models.mongodb._lectures import _lecture


class _teacher_profile(Document):
    teacher_id: int
    hod: bool
    lectures: List[Link[_lecture]]
    assignments: List[Link[_assignment]]
