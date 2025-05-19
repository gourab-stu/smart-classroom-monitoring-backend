from app.database.models.postgresql._students import _student as Student
from app.database.models.postgresql._teachers import _teacher as Teacher
from app.database.models.postgresql._papers import _paper as Paper
from app.database.models.postgresql._routines import _routine as Routine


__all__: list[str] = [
    "Student",
    "Teacher",
    "Routine",
    "Paper"
]
