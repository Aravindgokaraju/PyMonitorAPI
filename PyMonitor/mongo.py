# PyMonitor/mongo.py (simplified)
from pymongo import MongoClient
from django.conf import settings

# Global database connection
_db = None

def get_db():
    global _db
    if _db is None:
        print("Initializing MongoDB connection...")
        try:
            client = MongoClient(
                host=settings.MONGO_HOST,
                port=settings.MONGO_PORT,
                username=settings.MONGO_USER,
                password=settings.MONGO_PASS,
                authSource=settings.MONGO_AUTH_SOURCE,
                connectTimeoutMS=3000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            client.admin.command('ping')
            print("MongoDB connection successful")
            
            # Get database
            _db = client[settings.MONGO_DB_NAME]
            _db.command('ping')
            print("Database access successful")
            print(f"Available collections: {_db.list_collection_names()}")
            
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            raise
    
    return _db

def ensure_db_initialized():
    # Just call get_db() to ensure initialization
    db = get_db()
    if db is None:
        raise ConnectionError("Failed to initialize MongoDB connection")