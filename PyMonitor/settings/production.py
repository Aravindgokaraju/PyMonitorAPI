import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
print("REAL PRODUCTION")
# Production settings
from .base import *

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY')  # Required in production

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Check if Supabase URI is provided
if os.environ.get('SUPA_URI'):
    # Parse Supabase PostgreSQL connection
    print("Connecting with URI")
    import dj_database_url
    
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('SUPA_URI'),
            conn_max_age=600,
            ssl_require=True
        )
    }
# else:
#     # Fallback to MySQL
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': os.environ.get('DB_NAME'),
#             'USER': os.environ.get('DB_USER'),
#             'PASSWORD': os.environ.get('DB_PASSWORD'),
#             'HOST': os.environ.get('DB_HOST'),
#             'PORT': os.environ.get('DB_PORT'),
#             'OPTIONS': {
#                 'sql_mode': 'STRICT_TRANS_TABLES',
#             }
#         }
#     }
# # Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': os.environ.get('DB_PORT'),
#         'OPTIONS': {
#             'sql_mode': 'STRICT_TRANS_TABLES',
#         }
#     }
# }

# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # This is the important one

# MongoDB settings
# MongoDB Configuration with safe defaults
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'pymonitor')
# MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
# MONGO_PORT = int(os.environ.get('MONGO_PORT', '27017'))  # Note: string default converted to int
# MONGO_USER = os.environ.get('MONGO_USER', '')
# MONGO_PASS = os.environ.get('MONGO_PASS', '')
# MONGO_AUTH_SOURCE = os.environ.get('MONGO_AUTH_SOURCE', 'admin')

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



