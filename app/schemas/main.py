from enum import Enum

from pydantic import BaseModel


# Enums
class UserRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class AssignmentStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class SubmissionStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    RETURNED = "returned"


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
