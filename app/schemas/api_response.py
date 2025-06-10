from typing import Any, Optional
from app.schemas.main import BaseSchema


class MessageResponse(BaseSchema):
    content: Optional[Any] = None
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    detail: str
    error_code: int
    success: bool = False
