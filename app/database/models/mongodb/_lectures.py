# from datetime import datetime
# from beanie import Document, Link
# from pydantic import Field

# from app.database.models._students import Student
# from app.database.models._teachers import Teacher


# class OTP(Document):
#     user_id: Link[Student] | Link[Teacher] = Field(
#         default=...,
#         description="ObjectId, referencing either a Student or a Teacher"
#     )
#     otp: str = Field(
#         default=...,
#         pattern=r"^[A-Za-z0-9]{6}$"
#     )
#     creation_time: datetime = Field(
#         default=...,
#         description="Date and time of the OTP generation"
#     )
#     expiration_time: datetime = Field(
#         default=...,
#         description="Expiration date and time of the OTP"
#     )

#     class Settings:
#         name: str = "otps"


# lecture.py
from datetime import date
from typing import List, Optional
from beanie import Document, Link

from app.database.models.mongodb._classes import _class
from app.database.models.mongodb._student_profiles import _student_profile


class _lecture(Document):
    routine_ref: Optional[int]  # FK to routines
    class_id: Link[_class]
    class_type: str
    student_ids: List[Link[_student_profile]]
    date_of_class: date
