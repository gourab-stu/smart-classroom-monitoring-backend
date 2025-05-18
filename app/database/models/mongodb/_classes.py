# from beanie import Document
# from pydantic import Field
# from pymongo import ASCENDING, IndexModel


# class Paper(Document):
#     name: str = Field(
#         default=...,
#         description="Name of the paper"
#     )
#     code: str = Field(
#         default=...,
#         description="Code of the paper in block letters",
#         pattern=r"[A-Z0-9]*"
#     )

#     class Settings:
#         name: str = "papers"
#         indexes: list[IndexModel] = [
#             IndexModel(keys=[("code", ASCENDING)], unique=True)
#         ]


# class_model.py
from typing import List
from beanie import Document, Link

from app.database.models.mongodb._student_profiles import _student_profile


class _class(Document):
    semester: int
    student_ids: List[Link[_student_profile]]
