from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from bson import ObjectId
import re

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


class OTPModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user: PyObjectId
    timestamp: datetime
    otp: str

    @field_validator("otp")
    def validate_otp(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9]{6}", v):
            raise ValueError("OTP must be exactly 6 alphanumeric characters")
        return v

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user": "60c72b2f4f1a4e3f8c76f0b1",
                "timestamp": "2024-06-01T12:00:00Z",
                "otp": "A1B2C3"
            }
        }
