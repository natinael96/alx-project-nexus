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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='jobboard_db'),
        'USER': config('DB_USER', default='jobboard_user'),
        'PASSWORD': config('DB_PASSWORD', default='jobboard_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        # Connection settings
        'CONN_MAX_AGE': 0,  # Override in production for connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        },
        # Transaction settings
        'ATOMIC_REQUESTS': False,  # Set per-view transaction handling
    }
}

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
CACHES = {
    'default': {
        'BACKEND': config(
            'CACHE_BACKEND',
            default='django.core.cache.backends.redis.RedisCache'
        ),
        'LOCATION': config(
            'CACHE_LOCATION',
            default='redis://127.0.0.1:6379/1'
        ),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Fail silently if Redis is unavailable
        },
        'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='jobboard'),
        'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),  # 5 minutes default
    }
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
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# File Storage Configuration
FILE_STORAGE_BACKEND = config('FILE_STORAGE_BACKEND', default='local')  # local, supabase, s3

# Supabase Storage Configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_KEY', default='')
SUPABASE_STORAGE_BUCKET = config('SUPABASE_STORAGE_BUCKET', default='files')

# AWS S3 Configuration (alternative to Supabase)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')  # For CDN

# File Processing Configuration
ENABLE_VIRUS_SCANNING = config('ENABLE_VIRUS_SCANNING', default=False, cast=bool)
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
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
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
}

# Logging Configuration
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
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'api_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'api.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'INFO',
        },
        'performance_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'INFO',
        },
        'django.server': {
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': config('DB_LOG_LEVEL', default='WARNING'),  # Set to DEBUG to log all queries
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.api': {
            'handlers': ['api_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.performance': {
            'handlers': ['performance_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Email Configuration (Base settings - override in environment-specific files)
SITE_NAME = config('SITE_NAME', default='Job Board Platform')
SITE_URL = config('SITE_URL', default='http://localhost:8000')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@jobboard.com')

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery Task Settings
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_DEAD = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Celery Beat (Scheduled Tasks)
CELERY_BEAT_SCHEDULE = {
    'process-job-expiration': {
        'task': 'apps.jobs.tasks.process_job_expiration',
        'schedule': 3600.0,  # Run every hour
    },
    'process-scheduled-jobs': {
        'task': 'apps.jobs.tasks.process_scheduled_jobs',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'send-application-deadline-reminders': {
        'task': 'apps.jobs.tasks.send_application_deadline_reminders',
        'schedule': 86400.0,  # Run daily
    },
    'cleanup-old-notifications': {
        'task': 'apps.core.tasks.cleanup_old_notifications',
        'schedule': 86400.0,  # Run daily
    },
    'generate-daily-reports': {
        'task': 'apps.core.tasks.generate_daily_reports',
        'schedule': 86400.0,  # Run daily at midnight
    },
}
