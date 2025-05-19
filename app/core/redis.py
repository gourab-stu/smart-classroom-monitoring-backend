from typing import Union
from redis.asyncio import Redis

from app.core import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME

redis_client: Union[Redis, None] = None


async def init_redis_pool():
    global redis_client
    redis_client = await Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    try:
        await redis_client.ping()
        print("✅ Redis connected successfully.")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")


async def close_redis_pool():
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
