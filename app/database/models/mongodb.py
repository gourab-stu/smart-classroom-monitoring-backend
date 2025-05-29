# from datetime import date, datetime
# from typing import List, Optional
# from beanie import Document
# from bson import ObjectId


# class Class(Document):
#     semester: int
#     student_ids: List[ObjectId]

#     class Config:
#         collections: str = "classes"
#         arbitrary_types_allowed = True


# class Lecture(Document):
#     routine_ref: Optional[int]
#     class_id: ObjectId
#     class_type: str
#     student_ids: List[ObjectId]
#     date_of_class: date

#     class Config:
#         collections: str = "lectures"
#         arbitrary_types_allowed = True


# class Assignment(Document):
#     title: str
#     class_id: ObjectId
#     creation_date: datetime
#     due_date: Optional[datetime]

#     class Config:
#         collections: str = "assignments"
#         arbitrary_types_allowed = True


# class Submission(Document):
#     assignment_id: ObjectId
#     student_id: ObjectId
#     submitted_at: datetime
#     upload_url: List[str]

#     class Config:
#         collections: str = "submissions"
#         arbitrary_types_allowed = True


# class StudentProfile(Document):
#     reg_no: str
#     roll_no: int
#     semester: int
#     subjects: List[str]
#     date_of_birth: Optional[date]
#     profile_pic: Optional[str]
#     assignments: Optional[List[ObjectId]]
#     lectures_attended: Optional[List[ObjectId]]
#     refresh_token: Optional[str]

#     class Config:
#         collections: str = "student_profiles"
#         arbitrary_types_allowed = True


# class TeacherProfile(Document):
#     teacher_id: int
#     lectures: Optional[List[ObjectId]]
#     assignments: Optional[List[ObjectId]]
#     hod: bool
#     refresh_token: Optional[str]

#     class Config:
#         collections: str = "teacher_profiles"
#         arbitrary_types_allowed = True


# class FaceEncoding(Document):
#     profile_id: ObjectId
#     encoding: List[float]

#     class Config:
#         collections: str = "face_encodings"
#         arbitrary_types_allowed = True


from datetime import datetime
from beanie import Document
from pydantic import Field
from typing import List


class FaceEncoding(Document):
    student_id: str
    encoding: List[float]

    class Settings:
        name = "face_encodings"  # MongoDB collection name

    class Config:
        json_schema_extra = {
            "example": {"student_id": "123", "encoding": [0.123, 0.456, 0.789]}
        }


class AssignmentChatbox(Document):
    assignment_id: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assignments_chatbox"  # MongoDB collection name

    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "assignment123",
                "message": "Please complete this by tomorrow!",
                "created_at": "2025-05-27T12:00:00Z",
            }
        }
