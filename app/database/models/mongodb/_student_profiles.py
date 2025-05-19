from datetime import date
from typing import List, Optional
from beanie import Document

from bson import ObjectId


class _student_profile(Document):
    reg_no: int
    roll_no: int
    semester: int
    subjects: List[str]
    date_of_birth: Optional[date]
    profile_pic: Optional[str]
    assignments: Optional[List[ObjectId]]
    lectures_attended: Optional[List[ObjectId]]

    class Config:
        arbitrary_types_allowed = True
