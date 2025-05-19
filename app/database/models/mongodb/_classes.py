from typing import List
from beanie import Document
from bson import ObjectId


class _class(Document):
    semester: int
    student_ids: List[ObjectId]

    class Config:
        arbitrary_types_allowed = True
