import cv2
import face_recognition as fr
from cv2.typing import MatLike
from typing import Dict


def detect_face_info(frame: MatLike) -> Dict:
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(frame_rgb, (0, 0), fx=0.25, fy=0.25)
    face_locations = fr.face_locations(small_frame, model="hog")

    if not face_locations:
        return {"face_detected": False}

    top, right, bottom, left = face_locations[0]  # take first face
    top *= 4
    right *= 4
    bottom *= 4
    left *= 4
    return {
        "face_detected": True,
        "bounding_box": {
            "top": top,
            "right": right,
            "bottom": bottom,
            "left": left
        }
    }
