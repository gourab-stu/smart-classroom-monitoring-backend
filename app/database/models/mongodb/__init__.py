from app.database.models.mongodb._assignments import _assignment as Assignment
from app.database.models.mongodb._classes import _class as Class
from app.database.models.mongodb._face_encodings import _face_encoding as FaceEncoding
from app.database.models.mongodb._lectures import _lecture as Lecture
from app.database.models.mongodb._student_profiles import _student_profile as StudentProfile
from app.database.models.mongodb._submissions import _submission as Submission
from app.database.models.mongodb._teacher_profiles import _teacher_profile as TeacherProfile


__all__: list[str] = [
    "Assignment",
    "Class",
    "FaceEncoding",
    "Lecture",
    "StudentProfile",
    "Submission",
    "TeacherProfile"
]
