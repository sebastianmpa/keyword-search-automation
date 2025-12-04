from pymongo import MongoClient
from core.config_provider import get_mongo_uri
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_mongo_client():
    uri = get_mongo_uri()
    options = {
        "connectTimeoutMS": int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", 30000)),
        "maxPoolSize": int(os.getenv("MONGO_MAX_POOL_SIZE", 10)),
        "minPoolSize": int(os.getenv("MONGO_MIN_POOL_SIZE", 1)),
        "serverSelectionTimeoutMS": 5000,
        "authSource": os.getenv("MONGO_DBNAME", "admin"),
    }
    
    max_idle_time = int(os.getenv("MONGO_MAX_IDLE_TIME_MS", 0))
    if max_idle_time > 0:
        options["maxIdleTimeMS"] = max_idle_time
    
    client = MongoClient(uri, **options)
    return client

def get_database():
    client = get_mongo_client()
    db_name = os.getenv("MONGO_DBNAME")
    if not db_name:
        raise ValueError("MONGO_DBNAME environment variable is not set")
    
    db = client[db_name]
    return db