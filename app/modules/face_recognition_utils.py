import cv2
import face_recognition as fr
from cv2.typing import MatLike
from typing import Dict, Any


def detect_face_info(frame: MatLike, known_faces: list[dict]) -> Dict:
    # Assume frame is already BGR
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = fr.face_locations(rgb_small_frame, model="hog")
    if not face_locations:
        return {"face_detected": False}

    face_encodings = fr.face_encodings(rgb_small_frame, face_locations)
    if not face_encodings:
        return {"face_detected": False}

    # build known faces
    known_face_encodings = [f['encoding'] for f in known_faces if f]
    known_names = [f['name'] for f in known_faces if f]

    # just compare the first detected face for speed
    matches = fr.compare_faces(known_face_encodings, face_encodings[0])
    name = "Unknown"
    if True in matches:
        known_names_set = set(known_names)
        known_names_dict = dict.fromkeys(known_names_set, 0)
        for index in range(len(matches)):
            known_names_dict[known_names[index]] += int(matches[index])
        name = max(known_names_dict, key=known_names_dict.get)

    top, right, bottom, left = face_locations[0]
    return {
        "face_detected": True,
        "name": name,
        "bounding_box": {
            "top": top * 4,
            "right": right * 4,
            "bottom": bottom * 4,
            "left": left * 4
        }
    }


def recognize_face(frame: MatLike, bounding_box: tuple[int, Any, Any, int]):
    pass
