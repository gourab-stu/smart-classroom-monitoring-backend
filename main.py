# import cv2
# import SimpleFaceRecognition as SFR

# # using webcam
# cap = cv2.VideoCapture(0)

# SFR.capture_face(cap, "Gourab")
# # SFR.detect_faces_live(cap)

# cap.release()
# cv2.destroyAllWindows()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64

app = FastAPI()


@app.websocket("/ws/video")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            frame_data = base64.b64decode(data)
            np_arr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imshow("Client Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        cv2.destroyAllWindows()
