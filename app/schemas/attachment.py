from datetime import datetime

from app.schemas.main import BaseSchema


class AttachmentResponse(BaseSchema):
    attachment_id: int
    submission_id: int
    original_filename: str
    file_url: str
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
