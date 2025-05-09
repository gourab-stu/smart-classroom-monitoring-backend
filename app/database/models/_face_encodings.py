from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from bson import ObjectId

# Helper to support ObjectId validation


class PyObjectId(ObjectId):
    @classmethod
    def get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class FaceEncodingModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId = Field(..., description="ObjectId of the student")
    encoding: List[float] = Field(..., description="128-d face encoding")

    @field_validator("encoding")
    def validate_encoding_length(cls, v):
        if len(v) != 128:
            raise ValueError("Encoding must be a list of 128 float values")
        return v

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "student_id": "64fa3c8e9a5c3e9b1e3f024a",
                "encoding": [0.123, 0.456, ..., 0.789]  # 128 floats
            }
        }
