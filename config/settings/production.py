"""
Production settings for Job Board Platform.
Optimized for Heroku deployment.
"""
from .base import *
from decouple import config
import dj_database_url
import os

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='.herokuapp.com'
).split(',')

# Security settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security) settings
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)

# Referrer Policy
SECURE_REFERRER_POLICY = config('SECURE_REFERRER_POLICY', default='strict-origin-when-cross-origin')

# Heroku terminates SSL at the load balancer, so we need this
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Database Configuration ---
# Heroku sets DATABASE_URL automatically when you provision Heroku Postgres
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    # Fallback to manual config from base.py (non-Heroku environments)
    DATABASES['default']['OPTIONS'].update({
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000'
    })
    # Database connection pooling for production
    if config('DB_CONN_MAX_AGE', default=None):
        DATABASES['default']['CONN_MAX_AGE'] = config('DB_CONN_MAX_AGE', cast=int)

# --- Email Configuration ---
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@jobboard.com')

# --- CORS settings for production ---
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default=''
    ).split(',')
    if origin.strip()
]

# --- Static Files (WhiteNoise for Heroku) ---
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Cache Configuration ---
# Heroku Redis addon sets REDIS_URL or REDIS_TLS_URL
REDIS_URL = config('REDIS_URL', default=config('REDIS_TLS_URL', default=None))

if REDIS_URL:
    # Handle Heroku Redis TLS URL scheme (rediss://)
    # Heroku Redis uses self-signed certs, so we need to disable SSL cert verification
    import ssl
    redis_options = {}
    if REDIS_URL.startswith('rediss://'):
        redis_options = {
            'ssl_cert_reqs': ssl.CERT_NONE,
        }

    cache_backend = 'django_redis.cache.RedisCache'
    CACHES = {
        'default': {
            'BACKEND': cache_backend,
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='jobboard'),
            'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'IGNORE_EXCEPTIONS': False,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                    **redis_options,
                },
            },
        }
    }

else:
    # Fallback: use local memory cache if no Redis available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='jobboard'),
            'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),
        }
    }

# --- Sentry Error Tracking ---
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    import logging

    SENTRY_DSN = config('SENTRY_DSN', default='')
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(
                    transaction_style='url',
                    middleware_spans=True,
                    signals_spans=True,
                ),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR,
                ),
            ],
            traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float),
            send_default_pii=True,
            environment=config('ENVIRONMENT', default='production'),
            release=config('RELEASE_VERSION', default='1.0.0'),
        )
except ImportError:
    pass
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Sentry initialization failed: {str(e)}")
