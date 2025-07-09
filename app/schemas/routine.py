from datetime import time
from typing import Optional

from app.schemas.main import BaseSchema


class RoutineBase(BaseSchema):
    classroom_id: int
    paper_code: str
    teacher_id: int
    day_of_week: int
    start_time: time
    end_time: time
    notes: Optional[str] = None


class RoutineCreate(RoutineBase):
    pass


class RoutineUpdate(BaseSchema):
    classroom_id: Optional[int]
    paper_code: Optional[str]
    teacher_id: Optional[int]
    day_of_week: Optional[int]
    start_time: Optional[time]
    end_time: Optional[time]
    notes: Optional[str]


class RoutineInDB(RoutineBase):
    routine_id: int
