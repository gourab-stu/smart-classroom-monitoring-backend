from fastapi import FastAPI
from dotenv import load_dotenv
from .routes import face_detection_recognition

load_dotenv('.env')

app = FastAPI()

app.include_router(face_detection_recognition.router)
