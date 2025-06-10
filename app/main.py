from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth
from app.utilities.startup_and_shutdown import start_all, stop_all


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await start_all()


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")


@app.on_event("shutdown")
async def on_shutdown():
    await stop_all()
