from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import time
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class RoutineModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    day: Literal["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]
    teacher: PyObjectId
    paper: PyObjectId
    starting_time: time
    ending_time: time

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "day": "Tuesday",
                "teacher": "60c72b2f4f1a4e3f8c76f0b1",
                "paper": "60c72b2f4f1a4e3f8c76f0c9",
                "starting_time": "09:00",
                "ending_time": "10:30"
            }
        }
