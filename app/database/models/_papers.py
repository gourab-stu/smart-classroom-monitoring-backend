from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class Paper(Document):
    name: str = Field(
        default=...,
        description="Name of the paper"
    )
    code: str = Field(
        default=...,
        description="Code of the paper in block letters",
        pattern=r"[A-Z0-9]*"
    )

    class Settings:
        name: str = "papers"
        indexes: list[IndexModel] = [
            IndexModel(keys=[("code", ASCENDING)], unique=True)
        ]
