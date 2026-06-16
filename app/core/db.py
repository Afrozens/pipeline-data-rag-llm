from pymongo import MongoClient
from app.core.config import settings

client: MongoClient | None = None

def get_db():
    global client
    if client is None:
        client = MongoClient(settings.MONGODB_URI)
    return client[settings.MONGODB_DB_NAME]
