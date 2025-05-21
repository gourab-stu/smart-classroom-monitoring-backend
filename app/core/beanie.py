from typing import Union
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.database.models.mongodb import *

client: Union[AsyncIOMotorClient, None] = None


async def init_beanie_db() -> None:
    global client
    client = AsyncIOMotorClient(host=settings.MONGO_URI)
    await init_beanie(
        database=client[str(object=settings.MONGO_DATABASE_NAME)],
        document_models=[
            Assignment,
            Class,
            FaceEncoding,
            Lecture,
            StudentProfile,
            Submission,
            TeacherProfile
        ]
    )
    print("✅ MongoDB connected successfully.")


async def close_beanie_db() -> None:
    global client
    if client:
        client.close()
