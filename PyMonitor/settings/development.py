from .base import *
import os
from dotenv import load_dotenv

# Load development environment variables
print("DEVELOPMENT")
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ← This is the key change!

print(f"BASE_DIR: {BASE_DIR}")
print(f"Looking for .env.development in: {BASE_DIR}")

# Load development environment variables
env_path = BASE_DIR / '.env.development'
print(f"Env file path: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(".env.development loaded successfully")
else:
    print(".env.development file not found!")



# Development settings
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-for-development-only')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}

# MongoDB settings
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = int(os.environ.get('MONGO_PORT'))
MONGO_USER = os.environ.get('MONGO_USER')
MONGO_PASS = os.environ.get('MONGO_PASS')
MONGO_AUTH_SOURCE = os.environ.get('MONGO_AUTH_SOURCE')

# CORS for development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Allows any origin


REDIS_HOST = "redis"
REDIS_PORT = "6379"


# Security settings for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False