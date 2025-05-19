from datetime import date
from typing import List, Optional
from beanie import Document
from bson import ObjectId


class _lecture(Document):
    routine_ref: Optional[int]
    class_id: ObjectId
    class_type: str
    student_ids: List[ObjectId]
    date_of_class: date

    class Config:
        arbitrary_types_allowed = True
