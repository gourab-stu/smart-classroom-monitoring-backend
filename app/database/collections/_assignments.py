from .. import database
from ..models import AssignmentModel


class Assignment:
    assignments_collection = database['assignments']

    def create(self, assignment: AssignmentModel):
        self.assignments_collection.insert_one(
            assignment.model_dump(by_alias=True))
        pass

    def create(self, assignments: list[AssignmentModel]):
        self.assignments_collection.insert_one(
            [assignment.model_dump(by_alias=True) for assignment in assignments])
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
