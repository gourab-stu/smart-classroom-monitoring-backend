from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class _student(Base):
    __tablename__: str = "students"

    reg_no = Column(
        BigInteger,
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
