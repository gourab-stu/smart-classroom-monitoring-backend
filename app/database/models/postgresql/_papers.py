from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class _paper(Base):
    __tablename__: str = "papers"
    paper_code = Column(
        String(length=20),
        primary_key=True,
        nullable=False
    )
    paper_title = Column(
        String(length=50),
        nullable=False
    )
    paper_type = Column(
        String(length=20),
        nullable=False
    )
    semester = Column(
        Integer,
        nullable=False
    )
