from app.database.models._assignments import Assignment
from app.database.models._face_encodings import FaceEncoding
from app.database.models._otps import OTP
from app.database.models._papers import Paper
from app.database.models._routines import Routine
from app.database.models._students import Student
from app.database.models._teachers import Teacher


__all__: list[str] = [
    "Assignment",
    "FaceEncoding",
    "OTP",
    "Paper",
    "Routine",
    "Student",
    "Teacher"
]
