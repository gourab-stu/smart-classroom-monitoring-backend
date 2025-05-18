from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import close_redis_pool, init_redis_pool
from app.core.beanie import close_beanie_db, init_beanie_db
from app.core.sqlalchemy import close_postgres_connection, init_postgres_models
from app.routes import router


load_dotenv(dotenv_path='.env.development')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_postgres_models()
    await init_beanie_db()
    await init_redis_pool()
    yield
    await close_postgres_connection()
    await close_beanie_db()
    await close_redis_pool()

app = FastAPI()

# Allow CORS so frontend can POST
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)
