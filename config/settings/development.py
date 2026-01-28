"""
Development settings for Job Board Platform.
"""
from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0'
).split(',')

# Development-specific middleware
if DEBUG:
    INSTALLED_APPS += ['django_extensions']

# Email backend for development
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Database configuration (can override in .env)
DATABASES['default'].update({
    'OPTIONS': {
        'connect_timeout': 10,
    }
})

# Static files serving in development
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / 'static']

