from typing import List
from beanie import Document, Link
from pydantic import Field

from app.database.models._students import Student


class FaceEncoding(Document):
    student_id: Link[Student] = Field(
        default=...,
        description="ObjectId of the student whose face it is"
    )
    encoding: List[float] = Field(
        default=...,
        description="Face encoding of the student in readable format which is a list of 128 floating point numbers"
    )   # Length will be validated at application level

    class Settings:
        name: str = "face_encodings"
