from .. import database
from ..models import StudentModel
from typing import Any, Mapping


class Student:
    _students_collection = database['students']

    def create_one(students: StudentModel):
        Student._students_collection.insert_one(
            students.model_dump(by_alias=True))
        pass

    def create_many(students: list[StudentModel]):
        Student._students_collection.insert_many(
            [student.model_dump(by_alias=True) for student in students])
        pass

    def read(key: str, value: str) -> list[dict[str, Any]] | None:
        result = [res for res in Student._students_collection.find({
                                                                   key: value})]
        return result

    def read() -> list[dict[str, Any]] | None:
        result = [res for res in Student._students_collection.find({})]
        return result

    def update_all(filter: Mapping[str, Any], update_value: Mapping[str, Any]):
        result = Student._students_collection.update_many(
            filter=filter, update=update_value)
        return result

    def delete(filter: dict[str, Any]):
        Student._students_collection.delete_many(filter=filter)
        pass
