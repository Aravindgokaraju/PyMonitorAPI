# from pymongo import MongoClient
# from django.conf import settings
# from urllib.parse import quote_plus

# # Global database connection
# _db = None

# def get_db():
#     global _db
#     if _db is None:
#         print("Initializing MongoDB connection...")
#         try:
#             # Option 1: Use MONGODB_URI directly if provided (For Atlas)
#             if hasattr(settings, 'MONGODB_URI') and settings.MONGODB_URI:
#                 print("Using MongoDB Atlas connection...")
#                 # Mask password in log for security
#                 masked_uri = settings.MONGODB_URI
#                 if '://' in masked_uri and '@' in masked_uri:
#                     # Basic masking: replace password with ***
#                     parts = masked_uri.split('@')
#                     auth_part = parts[0]
#                     if ':' in auth_part:
#                         user_pass = auth_part.split('://')[1]
#                         if ':' in user_pass:
#                             user = user_pass.split(':')[0]
#                             masked_uri = masked_uri.replace(user_pass, f"{user}:***")
                
#                 print(f"MongoDB URI: {masked_uri}")
                
#                 client = MongoClient(
#                     settings.MONGODB_URI,
#                     connectTimeoutMS=10000,      
#                     socketTimeoutMS=30000,       
#                     maxPoolSize=50,
#                     serverSelectionTimeoutMS=10000,  
#                     retryWrites=True,            
#                     w="majority"                 
#                 )
            

#             # Test connection
#             client.admin.command('ping')
#             print("MongoDB connection successful")
            
#             # Get database
#             _db = client[settings.MONGO_DB_NAME]
#             _db.command('ping')
#             print("Database access successful")
#             print(f"Available collections: {_db.list_collection_names()}")
            
#         except Exception as e:
#             print(f"MongoDB connection failed: {e}")
#             raise
    
#     return _db

# def ensure_db_initialized():
#     # Just call get_db() to ensure initialization
#     db = get_db()
#     if db is None:
#         raise ConnectionError("Failed to initialize MongoDB connection")

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
            client = None  # Initialize client

            # Option 1: Use MONGODB_URI directly if provided (For Atlas)
            if hasattr(settings, 'MONGODB_URI') and settings.MONGODB_URI:
                print("Using MongoDB Atlas connection...")
                
                # --- Mask password in log for security ---
                masked_uri = settings.MONGODB_URI
                if '://' in masked_uri and '@' in masked_uri:
                    parts = masked_uri.split('@')
                    auth_part = parts[0]
                    if ':' in auth_part:
                        user_pass = auth_part.split('://')[1]
                        if ':' in user_pass:
                            user = user_pass.split(':')[0]
                            masked_uri = masked_uri.replace(user_pass, f"{user}:***")
                print(f"MongoDB URI: {masked_uri}")
                # --- End Masking ---
                
                client = MongoClient(
                    settings.MONGODB_URI,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=30000,
                    maxPoolSize=50,
                    serverSelectionTimeoutMS=10000,
                    retryWrites=True,
                    w="majority"
                )

            # Option 2: Build URI from individual settings (For Docker/Local)
            elif hasattr(settings, 'MONGO_HOST'):
                print("Building MongoDB connection string from local settings...")
                
                # Get connection parts from settings
                HOST = settings.MONGO_HOST
                PORT = getattr(settings, 'MONGO_PORT', 27017) # Default to 27017
                USER = getattr(settings, 'MONGO_USER', None)
                PASS = getattr(settings, 'MONGO_PASS', None)
                AUTH_SOURCE = getattr(settings, 'MONGO_AUTH_SOURCE', 'admin') # Default auth DB
                
                connection_string = f"mongodb://{HOST}:{PORT}/"
                
                # Add authentication if username and password are provided
                if USER and PASS:
                    USER_ESCAPED = quote_plus(USER)
                    PASS_ESCAPED = quote_plus(PASS)
                    connection_string = f"mongodb://{USER_ESCAPED}:{PASS_ESCAPED}@{HOST}:{PORT}/?authSource={AUTH_SOURCE}"
                    print(f"Connecting to: mongodb://{USER_ESCAPED}:***@{HOST}:{PORT}/?authSource={AUTH_SOURCE}")
                else:
                    print(f"Connecting to: {connection_string} (no auth)")

                client = MongoClient(
                    connection_string,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=30000,
                    maxPoolSize=50,
                    serverSelectionTimeoutMS=10000
                )
            
            else:
                # No settings found
                raise Exception("No MongoDB connection settings found. Please set MONGODB_URI or MONGO_HOST in your settings.")

            # Test connection
            client.admin.command('ping')
            print("MongoDB connection successful")
            
            # Get database
            _db = client[settings.MONGO_DB_NAME]
            _db.command('ping') # Test database access
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