from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core import POSTGRES_URI


Base = declarative_base()

# Create the async engine
engine: AsyncEngine = create_async_engine(
    url=POSTGRES_URI,  # e.g. "postgresql+asyncpg://user:pass@localhost/db"
    echo=False,
    future=True
)

# Create an async session factory
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


# Dependency for FastAPI routes
async def get_db_session():
    async with async_session() as session:
        print(f"postgres session info: {session.info}")
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


# Called at app startup to create tables
async def init_postgres_models():
    import app.database.models.postgresql  # Ensure all models are registered
    async with engine.begin() as conn:
        await conn.run_sync(fn=Base.metadata.create_all)


# Called at app shutdown to close connection
async def close_postgres_connection():
    await engine.dispose()


__all__ = [
    "get_db_session",
    "init_postgres_models",
    "close_postgres_connection"
]
