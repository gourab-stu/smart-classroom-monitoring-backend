from aioredis import Redis

redis_client: Redis | None = None


async def init_redis_pool():
    global redis_client
    redis_client = Redis(host="localhost", port=6379, decode_responses=True)


async def close_redis_pool():
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
