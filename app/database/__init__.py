import os
from motor.motor_asyncio import AsyncIOMotorClient

uri = os.getenv('MONGODB_URI')
dbname = os.getenv('DATABASE_NAME')

client = AsyncIOMotorClient(uri)
database = client[dbname]

print(f"connected to database, HOST: {client.address}")
