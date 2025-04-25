from .. import face_encodings_collection
from ..models import FaceIn, FaceOut


def create_face(student: FaceIn) -> bool:
    try:
        face_encodings_collection.insert_one(student)
    except:
        return False
    return True


def load_known_faces() -> list[dict]:
    result = face_encodings_collection.find({})
    known_faces = []
    for face in result:
        known_faces.append(face)
    return known_faces


def update_student(student: FaceIn):
    pass


def delete_student(student: FaceIn):
    pass
