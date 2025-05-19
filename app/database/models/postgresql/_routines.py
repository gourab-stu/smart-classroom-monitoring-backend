from sqlalchemy import Column, BigInteger, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
# from app.database.models.postgresql._teachers import _teacher

Base = declarative_base()


class _routine(Base):
    __tablename__: str = "routines"

    routine_id = Column(
        BigInteger,
        primary_key=True,
        nullable=False
    )
    day = Column(
        String(length=3),
        nullable=False
    )
    teacher_id = Column(
        BigInteger,
        ForeignKey(column="teachers.teacher_id"),
        nullable=False
    )
    class_id = Column(
        String(length=30),
        nullable=False
    )
    paper_code = Column(
        String(length=20),
        ForeignKey(column="papers.paper_code"),
        nullable=False
    )
    starting_at = Column(
        Time,
        nullable=False
    )
    ending_at = Column(
        Time,
        nullable=False
    )
    status = Column(
        Boolean,
        nullable=False
    )
