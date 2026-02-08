"""
Django settings for Job Board Platform project.
Base settings shared across all environments.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    
    # Local apps
    'apps.accounts',
    'apps.jobs',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom middleware for logging and monitoring
    'apps.core.middleware.APILoggingMiddleware',
    'apps.core.middleware.PerformanceMonitoringMiddleware',
    'apps.core.middleware.DatabaseQueryLoggingMiddleware',
    'apps.core.middleware_audit.AuditLoggingMiddleware',
    # Security middleware
    'apps.core.middleware_security.APIKeyAuthenticationMiddleware',
    'apps.core.middleware_security.IPWhitelistMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Support for Neon PostgreSQL (cloud) or local PostgreSQL
# Neon requires SSL, so we check if SSL is required via DB_SSL_REQUIRE or if host contains 'neon'
DB_SSL_REQUIRE = config('DB_SSL_REQUIRE', default=False, cast=bool)
DB_HOST = config('DB_HOST', default='localhost')

# Auto-detect Neon database (if host contains 'neon', enable SSL)
if 'neon' in DB_HOST.lower() or DB_SSL_REQUIRE:
    DB_SSL_REQUIRE = True

# Determine if using cloud database (Neon, Supabase, etc.)
IS_CLOUD_DB = 'neon' in DB_HOST.lower() or 'supabase' in DB_HOST.lower() or 'azure' in DB_HOST.lower() or DB_SSL_REQUIRE

# Connection max age: shorter for cloud databases to avoid connection issues
if IS_CLOUD_DB:
    # Cloud databases (Neon, etc.) benefit from shorter connection times
    # to avoid "connection closed" errors
    CONN_MAX_AGE = config('DB_CONN_MAX_AGE', default=60, cast=int)  # 1 minute for cloud
else:
    # Local databases can keep connections longer
    CONN_MAX_AGE = config('DB_CONN_MAX_AGE', default=600, cast=int)  # 10 minutes for local

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='jobboard_db'),
        'USER': config('DB_USER', default='jobboard_user'),
        'PASSWORD': config('DB_PASSWORD', default='jobboard_password'),
        'HOST': DB_HOST,
        'PORT': config('DB_PORT', default='5432'),
        # Connection pooling - shorter for cloud databases
        'CONN_MAX_AGE': CONN_MAX_AGE,
        # Validate connections before reuse (prevents "SSL SYSCALL error: EOF detected")
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 seconds
        },
        # Transaction settings
        'ATOMIC_REQUESTS': False,  # Set per-view transaction handling
    }
}

# Add SSL options if required (for Neon or cloud databases)
if DB_SSL_REQUIRE:
    DATABASES['default']['OPTIONS'].update({
        'sslmode': 'require',
        # Additional SSL options for better compatibility
        'sslcert': config('DB_SSL_CERT', default=None),
        'sslkey': config('DB_SSL_KEY', default=None),
        'sslrootcert': config('DB_SSL_ROOT_CERT', default=None),
    })
    # Remove None values from OPTIONS
    DATABASES['default']['OPTIONS'] = {
        k: v for k, v in DATABASES['default']['OPTIONS'].items() if v is not None
    }

# Read replica configuration (for scaling)
USE_READ_REPLICA = config('USE_READ_REPLICA', default=False, cast=bool)
if USE_READ_REPLICA:
    DATABASES['read_replica'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_REPLICA_NAME', default='jobboard_db_replica'),
        'USER': config('DB_REPLICA_USER', default='postgres'),
        'PASSWORD': config('DB_REPLICA_PASSWORD', default='postgres'),
        'HOST': config('DB_REPLICA_HOST', default='localhost'),
        'PORT': config('DB_REPLICA_PORT', default='5432'),
        'CONN_MAX_AGE': config('DB_REPLICA_CONN_MAX_AGE', default=600, cast=int),
    }
    
    # Database router for read replicas
    DATABASE_ROUTERS = ['apps.core.db_router.ReadReplicaRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')
TIME_ZONE = config('TIME_ZONE', default='UTC')
USE_I18N = True
USE_TZ = True

# Cache Configuration
# Get the cache backend from environment, default to django-redis
cache_backend = config(
    'CACHE_BACKEND',
    default='django_redis.cache.RedisCache'
)

CACHES = {
    'default': {
        'BACKEND': cache_backend,
        'LOCATION': config(
            'CACHE_LOCATION',
            default='redis://127.0.0.1:6379/1'
        ),
        'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='jobboard'),
        'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),  # 5 minutes default
    }
}

# Add django-redis specific options only if using django-redis backend
if 'django_redis' in cache_backend:
    CACHES['default']['OPTIONS'] = {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'SOCKET_CONNECT_TIMEOUT': 5,
        'SOCKET_TIMEOUT': 5,
        'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        'IGNORE_EXCEPTIONS': True,  # Fail silently if Redis is unavailable
    }

# Cache key naming strategy
CACHE_KEY_PREFIX = config('CACHE_KEY_PREFIX', default='jobboard')
CACHE_TIMEOUT_SHORT = 60  # 1 minute
CACHE_TIMEOUT_MEDIUM = 300  # 5 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour
CACHE_TIMEOUT_VERY_LONG = 86400  # 24 hours

# Static files (CSS, JavaScript, Images)
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Only include static dir if it exists (it may not exist on Heroku)
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.is_dir() else []

# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# File Storage Configuration
FILE_STORAGE_BACKEND = config('FILE_STORAGE_BACKEND', default='supabase')  # local, supabase

# Supabase Storage Configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_KEY', default='')
SUPABASE_STORAGE_BUCKET = config('SUPABASE_STORAGE_BUCKET', default='files')

# File Processing Configuration
ENABLE_VIRUS_SCANNING = config('ENABLE_VIRUS_SCANNING', default=False, cast=bool)
ENABLE_RESUME_PARSING = config('ENABLE_RESUME_PARSING', default=False, cast=bool)
ENABLE_IMAGE_OPTIMIZATION = config('ENABLE_IMAGE_OPTIMIZATION', default=True, cast=bool)
ENABLE_RESUME_PARSING = config('ENABLE_RESUME_PARSING', default=True, cast=bool)
MAX_IMAGE_WIDTH = config('MAX_IMAGE_WIDTH', default=800, cast=int)
MAX_IMAGE_HEIGHT = config('MAX_IMAGE_HEIGHT', default=800, cast=int)
IMAGE_QUALITY = config('IMAGE_QUALITY', default=85, cast=int)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.core.throttling.UserBurstRateThrottle',
        'apps.core.throttling.AnonBurstRateThrottle',
        'apps.core.throttling.ReadWriteThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/hour',
        'anon': '100/hour',
        'user_burst': '50/minute',
        'anon_burst': '20/minute',
        'read': '1000/hour',
        'write': '200/hour',
        'ip_based': '100/hour',
    },
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%SZ',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(config('ACCESS_TOKEN_LIFETIME', default=60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(config('REFRESH_TOKEN_LIFETIME', default=1440))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000,http://localhost:8000'
    ).split(',')
    if origin.strip()  # Filter out empty strings
]

CORS_ALLOW_CREDENTIALS = True

# CORS additional settings
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Swagger/OpenAPI Settings
SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'apps.core.swagger.TaggedAutoSchema',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'DOC_EXPANSION': 'list',
    'TAGS_SORTER': 'alpha',
    'OPERATIONS_SORTER': 'method',
}

# Logging Configuration
# Detect if running on Heroku (ephemeral filesystem - no file logging)
IS_HEROKU = config('IS_HEROKU', default=False, cast=bool) or 'DYNO' in os.environ

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': config('LOG_LEVEL', default='INFO'),
        },
        'django.server': {
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': config('DB_LOG_LEVEL', default='WARNING'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.api': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.performance': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Add file handlers only when NOT on Heroku (Heroku has ephemeral filesystem)
if not IS_HEROKU:
    os.makedirs(BASE_DIR / 'logs', exist_ok=True)
    LOGGING['handlers'].update({
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'level': config('LOG_LEVEL', default='INFO'),
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'api_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'api.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'json',
            'level': 'INFO',
        },
        'performance_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'json',
            'level': 'INFO',
        },
    })
    LOGGING['root']['handlers'] = ['console', 'file']
    LOGGING['loggers']['django']['handlers'] = ['console', 'file', 'error_file']
    LOGGING['loggers']['django.db.backends']['handlers'] = ['console', 'file']
    LOGGING['loggers']['django.request']['handlers'] = ['file', 'error_file']
    LOGGING['loggers']['apps']['handlers'] = ['console', 'file', 'error_file']
    LOGGING['loggers']['apps.api']['handlers'] = ['api_file', 'console']
    LOGGING['loggers']['apps.performance']['handlers'] = ['performance_file', 'console']

# Email Configuration (Base settings - override in environment-specific files)
SITE_NAME = config('SITE_NAME', default='Job Board Platform')
SITE_URL = config('SITE_URL', default='http://localhost:8000')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@jobboard.com')

