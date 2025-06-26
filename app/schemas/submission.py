from datetime import datetime

from app.schemas.main import BaseSchema, SubmissionStatusEnum


class SubmissionResponse(BaseSchema):
    submission_id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    status: SubmissionStatusEnum
    # feedback: Optional[str] = None
    # is_late: bool
    # created_at: datetime
    # student: Optional[UserResponse] = None
    # attachments: List[AttachmentResponse] = []
