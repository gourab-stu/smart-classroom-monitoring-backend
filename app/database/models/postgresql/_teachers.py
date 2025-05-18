from sqlalchemy import Column, BigInteger, String, Text, Sequence
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class _teacher(Base):
    __tablename__: str = "teachers"

    teacher_id = Column(
        __name_pos=BigInteger,
        __type_pos=Sequence(name="teacher_id_seq"),
        primary_key=True,
        nullable=False
    )
    first_name = Column(
        __name_pos=String(length=50),
        nullable=False
    )
    middle_name = Column(
        __name_pos=String(length=50)
    )
    last_name = Column(
        __name_pos=String(length=50),
        nullable=False
    )
    email = Column(
        __name_pos=Text,
        nullable=False,
        unique=True
    )
    mobile_no = Column(
        __name_pos=String(length=10),
        nullable=False,
        unique=True
    )
