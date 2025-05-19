from typing import List
from beanie import Document

from bson import ObjectId


class _face_encoding(Document):
    profile_id: ObjectId
    encoding: List[float]

    class Config:
        arbitrary_types_allowed = True
