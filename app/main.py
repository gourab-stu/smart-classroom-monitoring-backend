from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import assignments, attachments, auth, submissions
from app.utilities.startup_and_shutdown import start_all, stop_all


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(attachments.router, prefix="/api/v1")
app.include_router(submissions.router, prefix="/api/v1")
