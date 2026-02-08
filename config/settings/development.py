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

# Email backend for development (Mailtrap)
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.mailtrap.io')
EMAIL_PORT = config('EMAIL_PORT', default=2525, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@jobboard.local')

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Database configuration (can override in .env)
# Use CONN_MAX_AGE=0 in dev to get a fresh connection each request
# This prevents "SSL SYSCALL error: EOF detected" with cloud databases
DATABASES['default'].update({
    'CONN_MAX_AGE': 0,
    'CONN_HEALTH_CHECKS': True,
    'OPTIONS': {
        'connect_timeout': 10,
    },
})

# Static files serving in development
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / 'static']

# Cache configuration for development
# Uses CACHE_BACKEND and CACHE_LOCATION from .env
# Falls back to local memory cache if Redis not available
cache_backend = config('CACHE_BACKEND', default='django.core.cache.backends.locmem.LocMemCache')
cache_location = config('CACHE_LOCATION', default='unique-snowflake')

CACHES = {
    'default': {
        'BACKEND': cache_backend,
        'LOCATION': cache_location,
        'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='jobboard'),
        'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),
    }
}

# Add django-redis specific options only if using django-redis backend
if 'django_redis' in cache_backend:
    CACHES['default']['OPTIONS'] = {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'SOCKET_CONNECT_TIMEOUT': 5,
        'SOCKET_TIMEOUT': 5,
        'IGNORE_EXCEPTIONS': True,  # Fail silently if Redis unavailable
    }