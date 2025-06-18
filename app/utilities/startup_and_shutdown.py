from app.core.beanie import close_beanie_db, init_beanie_db
from app.core.log_config import init_logger
from app.core.redis import close_redis_pool, init_redis_pool
from app.core.sqlalchemy import close_postgres_db, init_postgres_db


async def start_all():
    await init_postgres_db()
    await init_beanie_db()
    await init_redis_pool()
    # patch_loggers()
    init_logger()


async def stop_all():
    await close_postgres_db()
    await close_beanie_db()
    await close_redis_pool()
