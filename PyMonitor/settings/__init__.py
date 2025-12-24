"""
Django settings selector - chooses the right environment automatically.
"""
import os
import importlib
from django.core.exceptions import ImproperlyConfigured

# Map environment names to settings modules
ENVIRONMENT_SETTINGS = {
    'development': 'PyMonitor.settings.development',
    'production': 'PyMonitor.settings.production',
    'production_local': 'PyMonitor.settings.production_local',
    'worker': 'PyMonitor.settings.worker',

}
print("INIT Settings")
# Get environment (default to development for safety)
env = os.environ.get('DJANGO_ENV','production').lower()
settings_module_path = ENVIRONMENT_SETTINGS.get(env)

print(f"Loading {env} settings from: {settings_module_path}")

try:
    # Import the appropriate settings module
    settings_module = importlib.import_module(settings_module_path)
    
    # Copy all variables from the target module into this module's globals
    for setting_name in dir(settings_module):
        if setting_name.isupper():  # Only import uppercase settings (Django convention)
            globals()[setting_name] = getattr(settings_module, setting_name)
            
    print(f"Successfully loaded {env} settings")
    print(f"DEBUG mode: {globals().get('DEBUG', 'NOT SET')}")
    print(f"ALLOWED_HOSTS: {globals().get('ALLOWED_HOSTS', 'NOT SET')}")
    
except ImportError as e:
    raise ImproperlyConfigured(
        f"Could not import settings module '{settings_module_path}': {e}"
    )
except Exception as e:
    raise ImproperlyConfigured(
        f"Error loading settings from '{settings_module_path}': {e}"
    )

# Add this at the very end of your settings.py file
print("=" * 50)
print("CURRENT SETTINGS DEBUG INFO:")
print(f"Environment: {env}")
print(f"MONGO_HOST: {globals().get('MONGO_HOST', 'NOT SET')}")
print(f"MONGO_PORT: {globals().get('MONGO_PORT', 'NOT SET')}")
print(f"MONGO_DB_NAME: {globals().get('MONGO_DB_NAME', 'NOT SET')}")
print(f"MONGO_USER: {globals().get('MONGO_USER', 'NOT SET')}")
print("=" * 50)