from datetime import datetime, date, time
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    Time,
    TIMESTAMP,
    UniqueConstraint,
    func,
    BigInteger,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Role(Base, TimestampMixin):
    """Role model for user permission management"""

    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.role_id}, name='{self.name}')>"


class Permission(Base, TimestampMixin):
    """Permission model for granular access control"""

    __tablename__ = "permissions"

    permission_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (UniqueConstraint("resource", "action"),)

    def __repr__(self) -> str:
        return f"<Permission(id={self.permission_id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"


class RolePermission(Base, TimestampMixin):
    """Association table linking roles to their permissions"""

    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.permission_id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_permissions"
    )

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


class Classroom(Base, TimestampMixin):
    """Classroom model for managing physical classroom spaces"""

    __tablename__ = "classrooms"

    classroom_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    semester: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Relationships
    student_classroom: Mapped[List["Routine"]] = relationship(
        "StudentClassroom", back_populates="classroom", cascade="all, delete-orphan"
    )
    routines: Mapped[List["Routine"]] = relationship(
        "Routine", back_populates="classroom", cascade="all, delete-orphan"
    )
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture", back_populates="classroom", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Classroom(id={self.classroom_id}, name='{self.name}', semester={self.semester})>"


class Paper(Base, TimestampMixin):
    """Paper/Subject model for academic courses"""

    __tablename__ = "papers"

    paper_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    paper_title: Mapped[str] = mapped_column(String(200), nullable=False)
    paper_type: Mapped[str] = mapped_column(String(50), nullable=False)
    semester: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Relationships
    routines: Mapped[List["Routine"]] = relationship(
        "Routine", back_populates="paper", cascade="all, delete-orphan"
    )
    student_papers: Mapped[List["StudentPaper"]] = relationship(
        "StudentPaper", back_populates="paper", cascade="all, delete-orphan"
    )
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture", back_populates="paper", cascade="all, delete-orphan"
    )
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment", back_populates="paper", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Paper(code='{self.paper_code}', title='{self.paper_title}')>"


class User(Base, TimestampMixin):
    """User model for all system users (students, instructors, admins)"""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    mobile_no: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)

    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    routines: Mapped[List["Routine"]] = relationship(
        "Routine", back_populates="teacher"
    )
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture", back_populates="teacher"
    )
    student_papers: Mapped[List["StudentPaper"]] = relationship(
        "StudentPaper", back_populates="student", cascade="all, delete-orphan"
    )
    student_classroom: Mapped[List["StudentClassroom"]] = relationship(
        "StudentClassroom", back_populates="student", cascade="all, delete-orphan"
    )
    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance",
        back_populates="student",
        cascade="all, delete-orphan",
        foreign_keys="Attendance.student_id",
    )
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment", back_populates="teacher"
    )
    submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission", back_populates="student", cascade="all, delete-orphan"
    )
    marked_attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance",
        back_populates="marked_by_user",
        foreign_keys="Attendance.marked_by",
    )

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"<User(id={self.user_id}, email='{self.email}', name='{self.full_name}')>"
        )


class UserRole(Base, TimestampMixin):
    """Association table linking users to their roles"""

    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True
    )

    # Constraints
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class StudentClassroom(Base, TimestampMixin):
    """Association table linking students with their classroom"""

    __tablename__ = "student_classroom"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    classroom_id: Mapped[str] = mapped_column(
        ForeignKey("classrooms.classroom_id", ondelete="CASCADE"), primary_key=True
    )

    # Constraints
    __table_args__ = (UniqueConstraint("student_id", "classroom_id"),)

    # Relationships
    student: Mapped["User"] = relationship("User", back_populates="student_classroom")
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="student_classroom"
    )

    def __repr__(self) -> str:
        return f"<StudentClassroom(student_id={self.student_id}, classroom_id='{self.classroom_id}')>"


class StudentPaper(Base, TimestampMixin):
    """Association table linking students with their enrolled papers/subjects"""

    __tablename__ = "student_papers"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), primary_key=True
    )

    # Constraints
    __table_args__ = (UniqueConstraint("student_id", "paper_code"),)

    # Relationships
    student: Mapped["User"] = relationship("User", back_populates="student_papers")
    paper: Mapped["Paper"] = relationship("Paper", back_populates="student_papers")

    def __repr__(self) -> str:
        return f"<StudentPaper(student_id={self.student_id}, paper_code='{self.paper_code}')>"


class Routine(Base, TimestampMixin):
    """Routine model for managing class schedules and timetables"""

    __tablename__ = "routines"

    routine_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.classroom_id", ondelete="CASCADE"), nullable=False
    )
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="0=Sunday, 1=Monday, ..., 6=Saturday"
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="routines"
    )
    paper: Mapped["Paper"] = relationship("Paper", back_populates="routines")
    teacher: Mapped["User"] = relationship("User", back_populates="routines")
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture", back_populates="routine"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6"),
        CheckConstraint("start_time < end_time"),
        UniqueConstraint(
            "classroom_id",
            "day_of_week",
            "start_time",
            "end_time",
        ),
    )

    @property
    def day_name(self) -> str:
        """Get human-readable day name"""
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        return days[self.day_of_week]

    @property
    def duration_minutes(self) -> int:
        """Calculate routine duration in minutes"""
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        return int((end_datetime - start_datetime).total_seconds() / 60)

    def __repr__(self) -> str:
        return f"<Routine(id={self.routine_id}, classroom={self.classroom_id}, paper='{self.paper_code}', {self.day_name} {self.start_time}-{self.end_time})>"


class Lecture(Base, TimestampMixin):
    """Lecture model for individual lecture instances generated from routines"""

    __tablename__ = "lectures"

    lecture_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    routine_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("routines.routine_id", ondelete="SET NULL")
    )
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.classroom_id", ondelete="SET NULL"), nullable=False
    )
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    lecture_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    lecture_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="regular"
    )
    topic: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="scheduled"
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    attendance_marked: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Relationships
    routine: Mapped[Optional["Routine"]] = relationship(
        "Routine", back_populates="lectures"
    )
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="lectures"
    )
    paper: Mapped["Paper"] = relationship("Paper", back_populates="lectures")
    teacher: Mapped["User"] = relationship("User", back_populates="lectures")
    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance", back_populates="lecture", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("start_time < end_time"),
        CheckConstraint("lecture_type IN ('regular', 'extra', 'makeup', 'lab')"),
        CheckConstraint("status IN ('scheduled', 'ongoing', 'completed', 'cancelled')"),
        UniqueConstraint("classroom_id", "lecture_date", "start_time", "end_time"),
    )

    @property
    def duration_minutes(self) -> int:
        """Calculate lecture duration in minutes"""
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        return int((end_datetime - start_datetime).total_seconds() / 60)

    def __repr__(self) -> str:
        return f"<Lecture(id={self.lecture_id}, date={self.lecture_date}, paper='{self.paper_code}', status='{self.status}')>"


class Attendance(Base, TimestampMixin):
    """Attendance model for tracking student attendance in lectures"""

    __tablename__ = "attendances"

    attendance_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lecture_id: Mapped[int] = mapped_column(
        ForeignKey("lectures.lecture_id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="absent"
    )
    marked_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    marked_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL")
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    lecture: Mapped["Lecture"] = relationship("Lecture", back_populates="attendances")
    student: Mapped["User"] = relationship(
        "User", back_populates="attendances", foreign_keys=[student_id]
    )
    marked_by_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="marked_attendances", foreign_keys=[marked_by]
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('present', 'absent', 'late', 'excused')"),
        UniqueConstraint("lecture_id", "student_id"),
    )

    def __repr__(self) -> str:
        return f"<Attendance(id={self.attendance_id}, lecture_id={self.lecture_id}, student_id={self.student_id}, status='{self.status}')>"


class Assignment(Base, TimestampMixin):
    """Assignment model for managing course assignments and tasks"""

    __tablename__ = "assignments"

    assignment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    paper_code: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_code", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assignment_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="homework"
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    assigned_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="assignments")
    teacher: Mapped["User"] = relationship("User", back_populates="assignments")
    submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "assignment_type IN ('homework', 'project', 'lab', 'presentation')"
        ),
    )

    @property
    def is_overdue(self) -> bool:
        """Check if assignment is overdue"""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date

    def __repr__(self) -> str:
        return f"<Assignment(id={self.assignment_id}, title='{self.title}', paper='{self.paper_code}', type='{self.assignment_type}')>"


class AssignmentSubmission(Base, TimestampMixin):
    """Assignment submission model for tracking student submissions"""

    __tablename__ = "assignment_submissions"

    submission_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.assignment_id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    submission_text: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(
        String(15), nullable=False, server_default="submitted"
    )
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    is_late: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Relationships
    assignment: Mapped["Assignment"] = relationship(
        "Assignment", back_populates="submissions"
    )
    student: Mapped["User"] = relationship("User", back_populates="submissions")
    attachments: Mapped[List["SubmissionAttachment"]] = relationship(
        "SubmissionAttachment",
        back_populates="submission",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'submitted', 'returned')"),
        UniqueConstraint("assignment_id", "student_id"),
    )

    def __repr__(self) -> str:
        return f"<AssignmentSubmission(id={self.submission_id}, assignment_id={self.assignment_id}, student_id={self.student_id}, status='{self.status}')>"


class SubmissionAttachment(Base, TimestampMixin):
    """Model for assignment submission attachments"""

    __tablename__ = "submission_attachments"

    attachment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("assignment_submissions.submission_id", ondelete="CASCADE"),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64))
    upload_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="1"
    )

    # Relationships
    submission: Mapped["AssignmentSubmission"] = relationship(
        "AssignmentSubmission", back_populates="attachments"
    )

    __table_args__ = (UniqueConstraint("submission_id", "upload_order"),)

    def __repr__(self) -> str:
        return f"<SubmissionAttachment(id={self.attachment_id}, filename='{self.original_filename}')>"
