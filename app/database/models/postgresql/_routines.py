from sqlalchemy import Column, BigInteger, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
# from app.database.models.postgresql._teachers import _teacher

Base = declarative_base()


class _routine(Base):
    __tablename__: str = "routines"

    routine_id = Column(
        __name_pos=BigInteger,
        primary_key=True,
        nullable=False
    )
    day = Column(
        __name_pos=String(length=3),
        nullable=False
    )
    teacher_id = Column(
        __name_pos=BigInteger,
        __type_pos=ForeignKey(column="teachers.teacher_id"),
        nullable=False
    )
    class_id = Column(
        __name_pos=String(length=30),
        nullable=False
    )
    paper_code = Column(
        __name_pos=String(length=20),
        __type_pos=ForeignKey(column="papers.paper_code"),
        nullable=False
    )
    starting_at = Column(
        __name_pos=Time,
        nullable=False
    )
    ending_at = Column(
        __name_pos=Time,
        nullable=False
    )
    status = Column(
        __name_pos=Boolean,
        nullable=False
    )
