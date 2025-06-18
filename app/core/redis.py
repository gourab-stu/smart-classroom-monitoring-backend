from typing import Union

from loguru import logger
from redis.asyncio import Redis

from app.core.config import get_settings

redis_client: Union[Redis, None] = None
settings = get_settings()


async def init_redis_pool():
    global redis_client
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        username=settings.REDIS_USERNAME,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        logger.info("✅ Redis connected successfully.")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")


async def close_redis_pool():
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis_client():
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
