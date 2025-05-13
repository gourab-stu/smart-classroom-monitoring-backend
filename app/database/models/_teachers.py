from typing import List, Optional
from beanie import Document, Link
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel

from app.database.models._papers import Paper


class Teacher(Document):
    name: str = Field(
        default=...,
        description="Name is required and must be a string"
    )
    email: EmailStr = Field(
        default=...,
        description="Email is required and must be valid"
    )
    paper: Optional[List[Link[Paper]]] = Field(
        default_factory=list,
        description="Optional list of ObjectIds from papers collection"
    )

    class Settings:
        name: str = "teachers"
        indexes: list[IndexModel] = [
            IndexModel(keys=[("email", ASCENDING)], unique=True)
        ]
