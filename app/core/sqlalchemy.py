from typing import Union

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.database.models.postgresql import Base

engine: Union[AsyncEngine, None] = None
async_session: Union[async_sessionmaker[AsyncSession], None] = None
settings = get_settings()


async def init_postgres_db() -> None:
    global engine, async_session

    try:
        engine = create_async_engine(
            url=settings.POSTGRES_URI,
            echo=False,
            future=True,
        )

        async_session = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ PostgreSQL connected and tables created successfully.")
    except Exception as e:
        logger.info(e)
        logger.error("❌ PostgreSQL not connected.")


async def close_postgres_db() -> None:
    global engine
    if engine:
        await engine.dispose()


async def get_postgres_session():
    if not async_session:
        raise RuntimeError("Database not initialized. Call init_postgres_db first.")

    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
