from typing import List, Optional
from beanie import Document

from bson import ObjectId


class _teacher_profile(Document):
    teacher_id: int
    lectures: Optional[List[ObjectId]]
    assignments: Optional[List[ObjectId]]
    hod: bool

    class Config:
        arbitrary_types_allowed = True
