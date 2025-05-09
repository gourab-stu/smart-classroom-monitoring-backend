from ...database import database
from ..models import StudentModel
from typing import Any, Mapping


class Student:
    students_collection = database['students']

    def create(self, students: StudentModel):
        self.students_collection.insert_one(students.model_dump(by_alias=True))
        pass

    def create(self, students: list[StudentModel]):
        self.students_collection.insert_many(
            [student.model_dump(by_alias=True) for student in students])
        pass

    def read(self, key: str | None = None, value: str | None = None) -> list[dict[str, Any]] | None:
        result = [res for res in self.students_collection.find(
            {} if key is None or value is None else {key: value})]
        return result

    def update(self, filter: Mapping[str, Any], update_value: Mapping[str, Any]):
        result = self.students_collection.update_many(
            filter=filter, update=update_value)
        return result

    def delete(self, filter: dict[str, Any]):
        self.students_collection.delete_many(filter=filter)
        pass
