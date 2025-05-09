from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class AttendanceModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    date_of_class: date = Field(..., description="Date of the scheduled class")
    class_id: PyObjectId = Field(...,
                                 description="ObjectId of the scheduled class from routines")
    present: List[PyObjectId] = Field(
        ..., description="List of student ObjectIds who were present")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "date": "2025-05-10",
                "class_id": "60c72b2f9f1b8e6d88f0eabc",
                "present": [
                    "60c72c4a9f1b8e6d88f0ead1",
                    "60c72c4a9f1b8e6d88f0ead2"
                ]
            }
        }
