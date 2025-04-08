import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..modules import parser
from ..modules import face_recognition_utils as fru

router = APIRouter(prefix="/face-detection-recognition")


@router.websocket("/video")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            bytes = await websocket.receive_bytes()
            frame = parser.to_frame(data=bytes)

            if frame is None:
                continue

            detection_result = fru.detect_face_info(frame)
            await websocket.send_text(json.dumps(detection_result))
    except WebSocketDisconnect:
        print("Client disconnected")
