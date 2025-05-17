import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..db.face_recognition import crud
from ..modules import face_recognition_utils as fru

router = APIRouter(prefix="/detection", tags=["Face Detection"])


@router.websocket("/student")
async def login_student(websocket: WebSocket):
    await websocket.accept()
    known_faces = crud.load_known_faces()
    try:
        while True:
            bytes = await websocket.receive_bytes()
            frame = fru.to_frame(data=bytes)

            if frame is None:
                continue

            detection_result = fru.detect_face_info(frame, known_faces)
            await websocket.send_text(json.dumps(detection_result))
    except WebSocketDisconnect:
        print("Client disconnected")


@router.websocket("/teacher")
async def register_student(websocket: WebSocket):
    pass
