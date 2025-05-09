from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from bson import ObjectId

# Custom ObjectId validator


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# Submissions schema


class SubmissionModel(BaseModel):
    submitted_by: PyObjectId
    upload_link: HttpUrl

# Assignment schema


class AssignmentModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    created_by: PyObjectId
    submissions: List[SubmissionModel] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Assignment 1",
                "created_by": "60c72b2f4f1a4e3f8c76f0b1",
                "submissions": [
                    {
                        "submitted_by": "60c73d9e2f1a4e3f8c76fabc",
                        "upload_link": "https://res.cloudinary.com/demo/image/upload/v12345/assignment.pdf"
                    }
                ]
            }
        }
