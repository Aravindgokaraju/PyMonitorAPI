# PyMonitor/settings/worker.py
import os
from pathlib import Path

print("WORKER SETTINGS")
BASE_DIR = Path(__file__).resolve().parent.parent

# Minimal settings - worker doesn't need most Django features
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-minimal-key-for-worker-only')

# Worker should never run in debug mode
DEBUG = False

ALLOWED_HOSTS = ['*']  # Worker doesn't serve HTTP, so this doesn't matter

# ABSOLUTE MINIMAL installed apps - only what RQ worker needs
INSTALLED_APPS = [
    'django.contrib.contenttypes',  # Needed for model references
    'django.contrib.auth',          # Needed for user model if tasks reference users
    'django_rq',                    # RQ framework
    'execution',                    # Your app with task definitions
]

# Minimal middleware - worker doesn't process HTTP requests
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

# Use dummy database - worker doesn't need real DB access
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}

AUTH_USER_MODEL = 'execution.AppUser'


REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 360,
    },
    'worker': {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 600,
    },
}

# Internationalization (minimal)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = False

# Disable ALL unnecessary features
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CORS_ORIGIN_ALLOW_ALL = False

# No static files, no templates, no email, etc.

print("=" * 50)
print("PURE PROCESSOR WORKER SETTINGS LOADED")
print("Worker: No database, just processing")
print(f"Redis URL: {RQ_QUEUES['worker']['URL']}")
print("=" * 50)