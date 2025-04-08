import os
from pymongo.mongo_client import MongoClient

uri = os.getenv('MONGODB_URI')
dbname = os.getenv('DATABASE_NAME')

client = MongoClient(uri)
database = client[dbname]
