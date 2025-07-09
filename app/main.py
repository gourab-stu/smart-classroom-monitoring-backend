from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import (
    assignments,
    attachments,
    auth,
    papers,
    routines,
    submissions,
    users,
)
from app.utilities.startup_and_shutdown import start_all, stop_all

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.12.126:5173",
    "https://mlec.vercel.app",
    "https://stinkbug-witty-yeti.ngrok-free.app",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_all()
    logger.info("FastAPI app started.")
    yield
    await stop_all()
    logger.info("FastAPI app shutdown.")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(attachments.router, prefix="/api/v1")
app.include_router(submissions.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(papers.router, prefix="/api/v1")
app.include_router(routines.router, prefix="/api/v1")
