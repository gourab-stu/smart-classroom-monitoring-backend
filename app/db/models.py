from pydantic import BaseModel
from typing import List


class FaceIn(BaseModel):
    face: List[List[float]]
    face_name: str


class FaceOut(FaceIn):
    id: str
