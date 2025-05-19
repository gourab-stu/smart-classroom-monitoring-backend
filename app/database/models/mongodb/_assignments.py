from beanie import Document
from typing import Optional
from datetime import datetime

from bson import ObjectId


class _assignment(Document):
    title: str
    class_id: ObjectId
    creation_date: datetime
    due_date: Optional[datetime]

    class Config:
        arbitrary_types_allowed = True
