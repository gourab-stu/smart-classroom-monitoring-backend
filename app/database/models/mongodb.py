# # # # # V1 # # # # #

from datetime import datetime
from typing import List

from beanie import Document
from pydantic import Field


class FaceEncoding(Document):
    student_id: str
    encoding: List[float]

    class Settings:
        name = "face_encodings"  # MongoDB collection name


class AssignmentChatbox(Document):
    assignment_id: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assignments_chatbox"  # MongoDB collection name


# # # # # V2 # # # # #


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


# # # # # V3 # # # # #


# from datetime import datetime
# from typing import List, Optional, Dict, Any
# from beanie import Document
# from pydantic import Field
# from pymongo import IndexModel


# class FaceEncoding(Document):
#     """Face encoding storage for face recognition"""

#     user_id: int  # Reference to PostgreSQL user
#     encoding: List[float] = Field(..., description="128-dimensional face encoding")
#     image_url: Optional[str] = Field(None, description="URL to the face image")
#     image_hash: Optional[str] = Field(
#         None, description="Hash of the image for deduplication"
#     )
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     is_active: bool = Field(default=True, description="Whether this encoding is active")
#     confidence_score: Optional[float] = Field(
#         None, description="Confidence score of the encoding"
#     )

#     class Settings:
#         name = "face_encodings"
#         indexes = [
#             IndexModel([("user_id", 1)]),
#             IndexModel([("created_at", -1)]),
#             IndexModel([("is_active", 1)]),
#         ]


# class AssignmentChatbox(Document):
#     """Chat messages for assignment discussions"""

#     assignment_id: int  # Reference to PostgreSQL assignment
#     user_id: int  # Reference to PostgreSQL user
#     message: str = Field(..., description="Chat message content")
#     message_type: str = Field(default="text", description="Type of message")
#     attachments: List[Dict[str, Any]] = Field(
#         default_factory=list, description="Message attachments"
#     )
#     is_deleted: bool = Field(default=False, description="Soft delete flag")
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)

#     class Settings:
#         name = "assignment_chatbox"
#         indexes = [
#             IndexModel([("assignment_id", 1), ("created_at", -1)]),
#             IndexModel([("user_id", 1)]),
#             IndexModel([("is_deleted", 1)]),
#         ]


# class SystemLog(Document):
#     """System activity and audit logs"""

#     user_id: Optional[int] = Field(None, description="User who performed the action")
#     action: str = Field(..., description="Action performed")
#     resource: str = Field(..., description="Resource affected")
#     resource_id: Optional[str] = Field(None, description="ID of the affected resource")
#     details: Dict[str, Any] = Field(
#         default_factory=dict, description="Additional details"
#     )
#     ip_address: Optional[str] = Field(None, description="IP address of the user")
#     user_agent: Optional[str] = Field(None, description="User agent string")
#     severity: str = Field(default="info", description="Log severity level")
#     timestamp: datetime = Field(default_factory=datetime.utcnow)

#     class Settings:
#         name = "system_logs"
#         indexes = [
#             IndexModel([("user_id", 1), ("timestamp", -1)]),
#             IndexModel([("action", 1), ("timestamp", -1)]),
#             IndexModel([("resource", 1), ("timestamp", -1)]),
#             IndexModel([("severity", 1), ("timestamp", -1)]),
#             IndexModel([("timestamp", -1)]),
#         ]


# class AttendanceSession(Document):
#     """Active attendance sessions for face recognition"""

#     lecture_id: int  # Reference to PostgreSQL lecture
#     teacher_id: int  # Reference to PostgreSQL user
#     session_token: str = Field(..., description="Unique session token")
#     is_active: bool = Field(default=True, description="Whether session is active")
#     start_time: datetime = Field(default_factory=datetime.utcnow)
#     end_time: Optional[datetime] = Field(None, description="When session ended")
#     settings: Dict[str, Any] = Field(
#         default_factory=dict, description="Session settings"
#     )
#     recognized_students: List[int] = Field(
#         default_factory=list, description="Already recognized student IDs"
#     )

#     class Settings:
#         name = "attendance_sessions"
#         indexes = [
#             IndexModel([("lecture_id", 1)]),
#             IndexModel([("teacher_id", 1)]),
#             IndexModel([("session_token", 1)]),
#             IndexModel([("is_active", 1), ("start_time", -1)]),
#         ]


# class NotificationQueue(Document):
#     """Queue for sending notifications (email, SMS, etc.)"""

#     user_id: int  # Reference to PostgreSQL user
#     notification_type: str = Field(..., description="Type of notification")
#     channel: str = Field(..., description="Delivery channel (email, sms, push)")
#     recipient: str = Field(..., description="Recipient address")
#     subject: Optional[str] = Field(None, description="Notification subject")
#     message: str = Field(..., description="Notification message")
#     template_data: Dict[str, Any] = Field(
#         default_factory=dict, description="Template variables"
#     )
#     status: str = Field(default="pending", description="Delivery status")
#     attempts: int = Field(default=0, description="Delivery attempts")
#     max_attempts: int = Field(default=3, description="Maximum delivery attempts")
#     scheduled_at: datetime = Field(default_factory=datetime.utcnow)
#     sent_at: Optional[datetime] = Field(None, description="When notification was sent")
#     error_message: Optional[str] = Field(None, description="Error message if failed")

#     class Settings:
#         name = "notification_queue"
#         indexes = [
#             IndexModel([("user_id", 1)]),
#             IndexModel([("status", 1), ("scheduled_at", 1)]),
#             IndexModel([("notification_type", 1)]),
#             IndexModel([("channel", 1)]),
#         ]
