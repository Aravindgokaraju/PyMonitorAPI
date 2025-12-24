import os
from pathlib import Path
from dotenv import load_dotenv


# BASE_DIR = Path(__file__).resolve().parent.parent.parent # NEEDED FOR DOTENV ONLY
# print("BAAAASSSSEEEE____DIIIIRRRRR",BASE_DIR)
# # Production settings
# dotenv_path = BASE_DIR / '.env.production'
# print("DOOOTTTEEENVVVV",dotenv_path)
# load_dotenv(dotenv_path=dotenv_path)

from .base import *

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY')  # Required in production

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Check if Supabase URI is provided
if os.environ.get('SUPA_URI'):
    # Parse Supabase PostgreSQL connection
    import dj_database_url
    
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('SUPA_URI'),
            conn_max_age=600,
            ssl_require=True
        )
    }

# MongoDB settings
# MongoDB Configuration with safe defaults
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'pymonitor')
MONGODB_URI = os.environ.get('MONGODB_URI')


# Security settings for production
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'

# Additional production security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Scraping settings
MAX_CONCURRENT_SCRAPES = 3  # Adjust based on your paid worker size



