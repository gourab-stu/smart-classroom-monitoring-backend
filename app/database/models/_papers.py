from pydantic import BaseModel, Field
from typing import Optional
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


class PaperModel(BaseModel):
    id: Optional[PyObjectId] = Field(
        default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Name of the paper")
    code: str = Field(..., description="Code of the paper")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Design and Analysis of Algorithms",
                "code": "CMSACOR11"
            }
        }
