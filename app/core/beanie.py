from typing import Union
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.database.models.mongodb import FaceEncoding, AssignmentChatbox


client: Union[AsyncIOMotorClient, None] = None
settings = get_settings()


async def init_beanie_db() -> None:
    global client
    client = AsyncIOMotorClient(host=settings.MONGO_URI)
    await init_beanie(
        database=client[str(object=settings.MONGO_DATABASE_NAME)],
        document_models=[AssignmentChatbox, FaceEncoding],
    )
    print("✅ MongoDB connected successfully.")


async def close_beanie_db() -> None:
    global client
    if client:
        client.close()


async def get_mongo_client():
    if client is None:
        raise RuntimeError("Database not initialized. Call init_beanie_db first.")

    return client
