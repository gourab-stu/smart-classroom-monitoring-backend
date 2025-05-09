from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from bson import ObjectId

# Helper to support ObjectId validation in Pydantic


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class TeacherModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    paper: List[PyObjectId] = Field(default_factory=list)
    tests: List[PyObjectId] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Dr. Jane Smith",
                "email": "jane.smith@example.com",
                "paper": ["60c72b2f4f1a4e3f8c76f0b1"],
                "tests": []
            }
        }
