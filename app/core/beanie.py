from typing import Union

from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.database.models.mongodb import AssignmentChatbox, FaceEncoding

settings = get_settings()
client: Union[AsyncIOMotorClient, None] = None


async def init_beanie_db() -> None:
    global client
    try:
        client = AsyncIOMotorClient(host=settings.MONGO_URI)
        await init_beanie(
            database=client[str(object=settings.MONGO_DATABASE_NAME)],
            document_models=[AssignmentChatbox, FaceEncoding],
        )
        logger.info("✅ MongoDB connected successfully.")
    except Exception:
        logger.error("❌ MongoDB not connected.")


async def close_beanie_db() -> None:
    global client
    if client:
        client.close()


async def get_mongo_client():
    if client is None:
        raise RuntimeError("Database not initialized. Call init_beanie_db first.")

    return client
