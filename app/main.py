from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routes import auth, detection

load_dotenv('.env')

app = FastAPI()

# Allow CORS so frontend can POST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(detection.router)
