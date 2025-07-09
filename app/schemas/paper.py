from datetime import datetime
from typing import Optional

from app.schemas.main import BaseSchema


class PaperBase(BaseSchema):
    paper_code: str
    paper_title: str
    paper_type: str
    semester: int


class PaperCreate(PaperBase):
    pass


class PaperUpdate(BaseSchema):
    paper_title: Optional[str]
    paper_type: Optional[str]
    semester: Optional[int]


class PaperResponse(PaperBase):
    created_at: datetime
    updated_at: datetime
