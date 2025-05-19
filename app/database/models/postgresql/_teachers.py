from sqlalchemy import Column, BigInteger, String, Text, Sequence
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class _teacher(Base):
    __tablename__: str = "teachers"

    teacher_id = Column(
        BigInteger,
        Sequence(name="teacher_id_seq"),
        primary_key=True,
        nullable=False
    )
    first_name = Column(
        String(length=50),
        nullable=False
    )
    middle_name = Column(
        String(length=50)
    )
    last_name = Column(
        String(length=50),
        nullable=False
    )
    email = Column(
        Text,
        nullable=False,
        unique=True
    )
    mobile_no = Column(
        String(length=10),
        nullable=False,
        unique=True
    )
