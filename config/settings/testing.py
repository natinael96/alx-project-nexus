"""
Testing settings for Job Board Platform.
"""
from .base import *
from decouple import config

DEBUG = True

# Use SQLite for faster testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable migrations during testing for speed
# This speeds up tests by using the current state of models directly
class DisableMigrations:
    """
    Disable migrations during testing to speed up test execution.
    Tests will use the current state of models directly.
    """
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests
LOGGING_CONFIG = None

