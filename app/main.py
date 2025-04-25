from fastapi import FastAPI
from dotenv import load_dotenv
from .routes import auth

load_dotenv('.env')

app = FastAPI()

app.include_router(auth.router)
