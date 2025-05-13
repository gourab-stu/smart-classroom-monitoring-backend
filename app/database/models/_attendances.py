from datetime import datetime
from typing import List

from beanie import Document, Link
from pydantic import Field

from app.database.models import Routine, Student


class Attendance(Document):
    date_of_class: datetime = Field(
        default=...,
        description="Date of the class taken"
    )
    class_id: Link[Routine] = Field(
        default=...,
        description="Class id from the routines collections"
    )
    present: List[Link[Student]] = Field(
        default=...,
        description="ObjectIds of the students who were present at that class"
    )

    class Settings:
        name: str = "attendances"
