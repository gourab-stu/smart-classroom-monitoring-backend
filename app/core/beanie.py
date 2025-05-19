from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core import MONGO_URI, MONGO_DATABASE_NAME
from app.database.models.mongodb import *

client: AsyncIOMotorClient | None = None


async def init_beanie_db() -> None:
    global client
    client = AsyncIOMotorClient(host=MONGO_URI)
    await init_beanie(
        database=client[str(object=MONGO_DATABASE_NAME)],
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
    print(f"database connected to {client.HOST} via port {client.PORT}")


async def close_beanie_db() -> None:
    global client
    if client:
        client.close()


__all__ = [
    "init_beanie_db",
    "close_beanie_db"
]
