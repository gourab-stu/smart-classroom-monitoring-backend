import os
from pymongo.mongo_client import MongoClient

uri = os.getenv('MONGODB_URI')
dbname = os.getenv('DATABASE_NAME')

client = MongoClient(uri)
database = client[dbname]
face_encodings_collection = database['face-encodings']

print(f"connected to database, HOST: {client.address}")
