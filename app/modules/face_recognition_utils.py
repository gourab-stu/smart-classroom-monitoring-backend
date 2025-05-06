import cv2
import face_recognition as fr
import numpy as np
from cv2.typing import MatLike
from typing import Dict, Any


def detect_face_info(frame: MatLike, known_faces: list[dict]) -> Dict:
    # Assume frame is already BGR
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = fr.face_locations(rgb_small_frame, model="hog")
    # face_locations = fr.face_locations(frame_rgb, model="hog")
    if not face_locations:
        return {"face_detected": False}

    face_encodings = fr.face_encodings(rgb_small_frame, face_locations)
    # face_encodings = fr.face_encodings(frame_rgb, face_locations)
    if not face_encodings:
        return {"face_detected": False}

    # build known faces
    known_face_encodings = [f['encoding'] for f in known_faces if f]
    known_names = [f['name'] for f in known_faces if f]
    known_emails = [f['email'] for f in known_faces if f]
    known_face_ids = [str(f['_id']) for f in known_faces if f]

    # just compare the first detected face for speed
    distances = fr.face_distance(known_face_encodings, face_encodings[0])
    name = "Unknown"
    min_distance = min(distances)
    threshold = 5.0
    if min_distance < threshold:
        matched_idx = distances.tolist().index(min_distance)
        name = known_names[matched_idx]
        email = known_emails[matched_idx]
        face_id = known_face_ids[matched_idx]

    top, right, bottom, left = face_locations[0]
    return {
        "face_detected": True,
        "name": name,
        "email": email,
        "id": face_id,
        "bounding_box": {
            "top": top * 4,
            "right": right * 4,
            "bottom": bottom * 4,
            "left": left * 4
        }
    }


def to_frame(data: str) -> MatLike:
    frame_np = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)
    return frame


def to_frame_rgb(data: str) -> MatLike:
    frame = to_frame(data)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame_rgb
