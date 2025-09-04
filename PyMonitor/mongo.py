# PyMonitor/mongo.py
from pymongo import MongoClient
from django.conf import settings
from urllib.parse import quote_plus

# Global database connection
_db = None

def get_db():
    global _db
    if _db is None:
        print("Initializing MongoDB connection...")
        try:
            # Option 1: Use MONGODB_URI directly if provided
            if hasattr(settings, 'MONGODB_URI') and settings.MONGODB_URI:
                print(f"Using MongoDB URI: {settings.MONGODB_URI.replace(settings.MONGO_PASS, '***') if hasattr(settings, 'MONGO_PASS') else '***'}")
                client = MongoClient(
                    settings.MONGODB_URI,
                    connectTimeoutMS=3000,
                    socketTimeoutMS=5000,
                    maxPoolSize=50,
                    serverSelectionTimeoutMS=5000
                )
            
            # Option 2: Build URI from individual settings (fallback)
            else:
                # Properly encode username and password for URI
                username = quote_plus(settings.MONGO_USER)
                password = quote_plus(settings.MONGO_PASS)
                
                mongo_uri = f"mongodb://{username}:{password}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB_NAME}?authSource={settings.MONGO_AUTH_SOURCE}"
                print(f"Using constructed MongoDB URI: {mongo_uri.replace(password, '***')}")
                
                client = MongoClient(
                    mongo_uri,
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