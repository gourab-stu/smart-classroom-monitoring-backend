# from sqlalchemy import (
#     BigInteger,
#     Boolean,
#     Column,
#     ForeignKey,
#     Integer,
#     Sequence,
#     String,
#     Text,
#     Time,
# )
# from app.core.sqlalchemy import Base


# class Student(Base):
#     __tablename__: str = "students"

#     reg_no = Column(String(13), primary_key=True, nullable=False)
#     first_name = Column(String(50), nullable=False)
#     middle_name = Column(String(50))
#     last_name = Column(String(50), nullable=False)
#     email = Column(Text, nullable=False, unique=True)
#     mobile_no = Column(String(10), nullable=False, unique=True)


# class Teacher(Base):
#     __tablename__: str = "teachers"

#     teacher_id = Column(
#         BigInteger, Sequence(name="teacher_id_seq"), primary_key=True, nullable=False
#     )
#     first_name = Column(String(50), nullable=False)
#     middle_name = Column(String(50))
#     last_name = Column(String(50), nullable=False)
#     email = Column(Text, nullable=False, unique=True)
#     mobile_no = Column(String(10), nullable=False, unique=True)


# class Paper(Base):
#     __tablename__: str = "papers"
#     paper_code = Column(String(20), primary_key=True, nullable=False)
#     paper_title = Column(String(50), nullable=False)
#     paper_type = Column(String(20), nullable=False)
#     semester = Column(Integer, nullable=False)


# class Routine(Base):
#     __tablename__: str = "routines"

#     routine_id = Column(BigInteger, primary_key=True, nullable=False)
#     day = Column(String(3), nullable=False)
#     teacher_id = Column(BigInteger, ForeignKey("teachers.teacher_id"), nullable=False)
#     class_id = Column(String(30), nullable=False)
#     paper_code = Column(String(20), ForeignKey("papers.paper_code"), nullable=False)
#     starting_at = Column(Time, nullable=False)
#     ending_at = Column(Time, nullable=False)
#     status = Column(Boolean, nullable=False)


from datetime import date, datetime, time
from typing import Any, List, Optional, Union

from passlib.context import CryptContext
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint, Text, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import BIGINT, SMALLINT

from app.core.config import settings
from app.utilities.token import create_token, decode_token


# Create password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Base(DeclarativeBase):
    pass


class Class(Base):
    __tablename__ = "classes"

    class_id: Mapped[int] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    semester: Mapped[int] = mapped_column(SMALLINT, nullable=False)

    students: Mapped[List["Student"]] = relationship(back_populates="class_")
    routines: Mapped[List["Routine"]] = relationship(back_populates="class_")
    lectures: Mapped[List["Lecture"]] = relationship(back_populates="class_")


class Paper(Base):
    __tablename__ = "papers"

    paper_code: Mapped[str] = mapped_column(Text, primary_key=True)
    paper_title: Mapped[str] = mapped_column(Text, nullable=False)
    paper_type: Mapped[str] = mapped_column(Text, nullable=False)
    semester: Mapped[int] = mapped_column(SMALLINT, nullable=False)

    routines: Mapped[List["Routine"]] = relationship(back_populates="paper")
    lectures: Mapped[List["Lecture"]] = relationship(back_populates="paper")
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="paper")


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    mobile_no: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    _access_token: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    _refresh_token: Mapped[Optional[str]] = mapped_column(Text, unique=True)

    routines: Mapped[List["Routine"]] = relationship(back_populates="teacher")
    lectures: Mapped[List["Lecture"]] = relationship(back_populates="teacher")
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="teacher")

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @access_token.setter
    def access_token(self, token: dict[str, Any]) -> None:
        self._access_token = create_token(
            token,
            settings.ACCESS_TOKEN_SECRET,
            settings.ACCESS_TOKEN_EXPIRY,
            settings.JWT_ALGORITHM,
        )

    @refresh_token.setter
    def refresh_token(self, token: dict[str, Any]) -> None:
        self._refresh_token = create_token(
            token,
            settings.REFRESH_TOKEN_SECRET,
            settings.REFRESH_TOKEN_EXPIRY,
            settings.JWT_ALGORITHM,
        )

    @access_token.getter
    def get_access_token(self):
        return decode_token(
            self.access_token, settings.ACCESS_TOKEN_SECRET, settings.JWT_ALGORITHM
        )

    @refresh_token.getter
    def get_refresh_token(self):
        return decode_token(
            self.refresh_token, settings.REFRESH_TOKEN_SECRET, settings.JWT_ALGORITHM
        )

    def generate_access_token(self, data: dict[str, Any]) -> str:
        self.access_token = data
        return self.access_token

    def generate_refresh_token(self, data: dict[str, Any]) -> str:
        self.refresh_token = data
        return self.refresh_token


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(primary_key=True)
    reg_no: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    mobile_no: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    roll_no: Mapped[int] = mapped_column(SMALLINT, nullable=False)
    semester: Mapped[int] = mapped_column(SMALLINT, nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column()
    profile_pic: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    class_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("classes.class_id", ondelete="SET NULL")
    )
    _access_token: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    _refresh_token: Mapped[Optional[str]] = mapped_column(Text, unique=True)

    class_: Mapped[Optional[Class]] = relationship(back_populates="students")
    subjects: Mapped[List["StudentSubject"]] = relationship(back_populates="student")
    attendances: Mapped[List["LectureAttendance"]] = relationship(
        back_populates="student"
    )
    submissions: Mapped[List["Submission"]] = relationship(back_populates="student")

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @access_token.setter
    def access_token(self, token: dict[str, Any]) -> None:
        self._access_token = create_token(
            token,
            settings.ACCESS_TOKEN_SECRET,
            settings.ACCESS_TOKEN_EXPIRY,
            settings.JWT_ALGORITHM,
        )

    @refresh_token.setter
    def refresh_token(self, token: dict[str, Any]) -> None:
        self._refresh_token = create_token(
            token,
            settings.REFRESH_TOKEN_SECRET,
            settings.REFRESH_TOKEN_EXPIRY,
            settings.JWT_ALGORITHM,
        )

    @access_token.getter
    def get_access_token(self):
        return decode_token(
            self.access_token, settings.ACCESS_TOKEN_SECRET, settings.JWT_ALGORITHM
        )

    @refresh_token.getter
    def get_refresh_token(self):
        return decode_token(
            self.refresh_token, settings.REFRESH_TOKEN_SECRET, settings.JWT_ALGORITHM
        )

    def generate_access_token(self, data: dict[str, Any]) -> str:
        self.access_token = data
        return self.access_token

    def generate_refresh_token(self, data: dict[str, Any]) -> str:
        self.refresh_token = data
        return self.refresh_token


class StudentSubject(Base):
    __tablename__ = "student_subjects"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True
    )
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), primary_key=True
    )

    student: Mapped["Student"] = relationship(back_populates="subjects")
    paper: Mapped["Paper"] = relationship()


class Routine(Base):
    __tablename__ = "routines"

    routine_id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False
    )
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.teacher_id", ondelete="SET NULL"), nullable=False
    )
    day_of_week: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint(
            "day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')",
            name="valid_day_of_week",
        ),
    )

    class_: Mapped["Class"] = relationship(back_populates="routines")
    paper: Mapped["Paper"] = relationship(back_populates="routines")
    teacher: Mapped["Teacher"] = relationship(back_populates="routines")
    lectures: Mapped[List["Lecture"]] = relationship(back_populates="routine")


class Lecture(Base):
    __tablename__ = "lectures"

    lecture_id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("routines.routine_id", ondelete="CASCADE")
    )
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.teacher_id", ondelete="SET NULL"), nullable=False
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False
    )
    lecture_date: Mapped[date] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[Optional[str]] = mapped_column(Text, default="Scheduled")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "status IN ('Scheduled', 'Ongoing', 'Completed', 'Cancelled')",
            name="valid_lecture_status",
        ),
    )

    routine: Mapped[Optional["Routine"]] = relationship(back_populates="lectures")
    paper: Mapped["Paper"] = relationship(back_populates="lectures")
    teacher: Mapped["Teacher"] = relationship(back_populates="lectures")
    class_: Mapped["Class"] = relationship(back_populates="lectures")
    attendances: Mapped[List["LectureAttendance"]] = relationship(
        back_populates="lecture"
    )


class LectureAttendance(Base):
    __tablename__ = "lecture_attendances"

    attendance_id: Mapped[int] = mapped_column(primary_key=True)
    lecture_id: Mapped[int] = mapped_column(
        ForeignKey("lectures.lecture_id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.student_id"), nullable=False
    )
    status: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("lecture_id", "student_id", name="unique_lecture_student"),
        CheckConstraint(
            "status IN ('Present', 'Absent', 'Late')", name="valid_attendance_status"
        ),
    )

    lecture: Mapped["Lecture"] = relationship(back_populates="attendances")
    student: Mapped["Student"] = relationship(back_populates="attendances")


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code"), nullable=False
    )
    teacher_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teachers.teacher_id"))
    assigned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    due_date: Mapped[datetime] = mapped_column(nullable=False)

    paper: Mapped["Paper"] = relationship(back_populates="assignments")
    teacher: Mapped[Optional["Teacher"]] = relationship(back_populates="assignments")
    submissions: Mapped[List["Submission"]] = relationship(back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"

    submission_id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.assignment_id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "assignment_id", "student_id", name="unique_assignment_submission"
        ),
    )

    assignment: Mapped["Assignment"] = relationship(back_populates="submissions")
    student: Mapped["Student"] = relationship(back_populates="submissions")
    attachments: Mapped[List["Attachment"]] = relationship(back_populates="submission")


class Attachment(Base):
    __tablename__ = "attachments"

    attachment_id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.submission_id", ondelete="CASCADE"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "file_type IN ('PDF', 'Image', 'Text')", name="valid_file_type"
        ),
    )

    submission: Mapped["Submission"] = relationship(back_populates="attachments")


class Admin(Base):
    __tablename__ = "admin"

    admin_id: Mapped[str] = mapped_column(primary_key=True)
    _password: Mapped[str] = mapped_column("password")
    _access_token: Mapped[Optional[str]] = mapped_column("access_token", unique=True)
    _refresh_token: Mapped[Optional[str]] = mapped_column("refresh_token", unique=True)

    @property
    def password(self) -> str:
        return self._password

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @password.setter
    def password(self, plain_password: str) -> None:
        self._password = pwd_context.hash(plain_password)

    @access_token.setter
    def access_token(self, token: dict[str, Any]) -> None:
        self._access_token = create_token(
            token,
            settings.ACCESS_TOKEN_SECRET,
            settings.ACCESS_TOKEN_EXPIRY,
            settings.JWT_ALGORITHM,
        )

    @refresh_token.setter
    def refresh_token(self, token: Union[dict[str, Any], None]) -> None:
        self._refresh_token = create_token(
            token,
            settings.REFRESH_TOKEN_SECRET,
            settings.REFRESH_TOKEN_EXPIRY,
            settings.JWT_ALGORITHM,
        )

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self._password)

    def generate_access_token(self, data: dict[str, Any]) -> str:
        self.access_token = data
        return self.access_token

    def generate_refresh_token(self, data: dict[str, Any]) -> str:
        self.refresh_token = data
        return self.refresh_token
