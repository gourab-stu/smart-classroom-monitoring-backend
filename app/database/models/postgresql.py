from sqlalchemy import Boolean, Column, BigInteger, ForeignKey, Integer, Sequence, String, Text, Time

from app.core.sqlalchemy import Base


class Student(Base):
    __tablename__: str = "students"

    reg_no = Column(BigInteger, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    email = Column(Text, nullable=False, unique=True)
    mobile_no = Column(String(10), nullable=False, unique=True)


class Teacher(Base):
    __tablename__: str = "teachers"

    teacher_id = Column(BigInteger, Sequence(
        name="teacher_id_seq"), primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    email = Column(Text, nullable=False, unique=True)
    mobile_no = Column(String(10), nullable=False, unique=True)


class Paper(Base):
    __tablename__: str = "papers"
    paper_code = Column(String(20), primary_key=True, nullable=False)
    paper_title = Column(String(50), nullable=False)
    paper_type = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)


class Routine(Base):
    __tablename__: str = "routines"

    routine_id = Column(BigInteger, primary_key=True, nullable=False)
    day = Column(String(3), nullable=False)
    teacher_id = Column(BigInteger, ForeignKey(
        "teachers.teacher_id"), nullable=False)
    class_id = Column(String(30), nullable=False)
    paper_code = Column(String(20), ForeignKey(
        "papers.paper_code"), nullable=False)
    starting_at = Column(Time, nullable=False)
    ending_at = Column(Time, nullable=False)
    status = Column(Boolean, nullable=False)
