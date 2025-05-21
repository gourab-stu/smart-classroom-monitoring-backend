# from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.redis import close_redis_pool, init_redis_pool
from app.core.beanie import close_beanie_db, init_beanie_db
from app.core.sqlalchemy import init_postgres_db, close_postgres_db
from app.routes import router


# load_dotenv(dotenv_path='.env.local')


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_postgres_db()
    await init_beanie_db()
    await init_redis_pool()

# Allow CORS so frontend can POST
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)


@app.on_event("shutdown")
async def on_shutdown():
    await close_postgres_db()
    await close_beanie_db()
    await close_redis_pool()
