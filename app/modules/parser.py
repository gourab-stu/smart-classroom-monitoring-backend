import cv2
import numpy as np
from cv2.typing import MatLike


def to_frame(data: str) -> MatLike:
    frame_np = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)
    return frame


def to_frame_rgb(data: str) -> MatLike:
    frame = to_frame(data)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame_rgb
