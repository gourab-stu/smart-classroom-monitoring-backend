from datetime import datetime
from typing import List, Optional
from beanie import Document, Link
from pydantic import BaseModel, Field, HttpUrl

from app.database.models._students import Student
from app.database.models._teachers import Teacher


class Submission(BaseModel):
    submitted_by: Link[Student] = Field(
        default=...,
        description="Reference to a student"
    )
    upload_link: HttpUrl = Field(
        default=...,
        description="Must be a valid URL"
    )


class Assignment(Document):
    name: str = Field(
        default=...,
        description="Assignment name must be a string"
    )
    created_by: Link[Teacher] = Field(
        default=...,
        description="Must be a reference to a teacher"
    )
    creation_date: datetime
    due_date: datetime
    submissions: Optional[List[Submission]] = Field(
        default_factory=list,
        description="List of student submissions"
    )

    class Settings:
        name: str = "assignments"
