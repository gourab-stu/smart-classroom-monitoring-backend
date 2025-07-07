from typing import Any, Optional

from app.schemas.link import Links
from app.schemas.main import BaseSchema


class MessageResponse(BaseSchema):
    content: Optional[Any] = None
    message: Optional[str] = None
    success: bool = True
    links: Optional[Links] = None


class ErrorResponse(BaseSchema):
    detail: str
    error_code: int
    success: bool = False
