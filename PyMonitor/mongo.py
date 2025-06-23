from pymongo import MongoClient
from django.conf import settings

def get_db():
    """Returns the MongoDB database instance with connection pooling"""
    client = MongoClient(
        host='localhost',
        port=27017,
        # Add these if you enabled auth in MongoDB:
        username='admin',
        password='M0ng0_pass',
        authSource='admin',
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
        maxPoolSize=50  # Adjust based on expected load
    )
    return client['pymonitor']  # Your database name

# Global db instance (reused across requests)
db = get_db()