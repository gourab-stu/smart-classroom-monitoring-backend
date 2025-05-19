from datetime import datetime
from typing import List
from beanie import Document

from bson import ObjectId


class _submission(Document):
    assignment_id: ObjectId
    student_id: ObjectId
    submitted_at: datetime
    upload_url: List[str]

    class Config:
        arbitrary_types_allowed = True
