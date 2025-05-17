from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.beanie_init import close_beanie_db, init_beanie_db
from app.routes import router


load_dotenv(dotenv_path='.env.development')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie_db()
    yield
    await close_beanie_db()

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
