from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.main import BaseSchema


class AssignmentBase(BaseSchema):
    paper_code: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assignment_type: str
    due_date: Optional[datetime] = None
    assigned_date: datetime
    instructions: Optional[str] = None
    is_active: bool = True


class AssignmentCreate(AssignmentBase):
    teacher_id: int
    pass


class AssignmentUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    instructions: Optional[str] = None


class AssignmentResponse(AssignmentCreate):
    assignment_id: int
    created_at: datetime
    updated_at: datetime
