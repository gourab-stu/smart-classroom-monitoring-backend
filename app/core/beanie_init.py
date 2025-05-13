from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core import db_name, mongo_uri
from app.database.models import OTP, Assignment, FaceEncoding, Paper, Routine, Student, Teacher

client: AsyncIOMotorClient | None = None


async def init_beanie_db() -> None:
    global client
    client = AsyncIOMotorClient(host=mongo_uri)
    await init_beanie(
        database=client[str(object=db_name)],
        document_models=[
            Assignment,
            FaceEncoding,
            OTP,
            Paper,
            Routine,
            Student,
            Teacher
        ]
    )
    print(f"database connected to {client.HOST} via port {client.PORT}")


async def close_beanie_db() -> None:
    global client
    if client:
        client.close()
