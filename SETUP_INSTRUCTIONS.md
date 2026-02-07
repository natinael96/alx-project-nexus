# Complete Setup Instructions - Job Board Platform Backend

This guide provides step-by-step instructions to set up and run the Job Board Platform backend using Docker or locally.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Local Development Setup](#local-development-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Accessing the Application](#accessing-the-application)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### For Docker Setup:
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (to clone the repository)

### For Local Setup:
- **Python** 3.9 or higher
- **PostgreSQL** 14 or higher
- **Redis** 7.0 or higher (for caching and Celery)
- **pip** (Python package manager)
- **virtualenv** (recommended)

## Quick Start with Docker

This is the **recommended** way to run the application.

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd alx-project-nexus
```

### Step 2: Create Environment File

Create a `.env` file in the root directory:

```bash
cp .env.example .env  # If you have an example file
# OR create manually
```

Edit `.env` with your configuration:

```env
# Django Settings
DJANGO_ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
# For Neon PostgreSQL (cloud database):
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_xnM0hF4OgDcK
DB_HOST=ep-gentle-credit-a8vtl67d-pooler.eastus2.azure.neon.tech
DB_PORT=5432
DB_SSL_REQUIRE=True

# For local Docker PostgreSQL (uncomment and use these instead):
# DB_NAME=jobboard_db
# DB_USER=jobboard_user
# DB_PASSWORD=jobboard_password
# DB_HOST=db
# DB_PORT=5432
# DB_SSL_REQUIRE=False

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes

# Email Configuration (Mailtrap for development/testing)
# How to get Mailtrap credentials:
# 1. Go to https://mailtrap.io and sign up/login
# 2. Create a new inbox or select existing inbox
# 3. Go to SMTP Settings tab
# 4. Select "Integrations" → "Django"
# 5. Copy the credentials shown
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-mailtrap-username
EMAIL_HOST_PASSWORD=your-mailtrap-password
DEFAULT_FROM_EMAIL=noreply@jobboard.local
FRONTEND_URL=http://localhost:3000

# File Storage (Local for development)
FILE_STORAGE_BACKEND=local
MEDIA_ROOT=/app/media
MEDIA_URL=/media/
STATIC_ROOT=/app/staticfiles
STATIC_URL=/static/

# Optional: Supabase Storage (if using cloud storage)
# How to get these values:
# 1. Go to https://supabase.com and sign in/create account
# 2. Create a new project or select existing project
# 3. Go to Project Settings (gear icon) > API
# 4. Copy "Project URL" → SUPABASE_URL
# 5. Copy "anon public" key (or "service_role" key for admin access) → SUPABASE_KEY
# 6. Go to Storage section in Supabase dashboard
# 7. Create a bucket (or use existing) → SUPABASE_STORAGE_BUCKET
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key-here
SUPABASE_STORAGE_BUCKET=your-bucket-name

# Optional: AWS S3 (if using S3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Security Settings
ENABLE_IP_WHITELIST=False
ENABLE_API_KEY_AUTH=False
ADMIN_IP_WHITELIST=

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Cache Configuration
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
CACHE_LOCATION=redis://redis:6379/1
CACHE_KEY_PREFIX=jobboard
CACHE_TIMEOUT=300

# Application Settings
PORT=8000
SITE_NAME=Job Board Platform
SITE_URL=http://localhost:8000

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
DB_LOG_LEVEL=WARNING

# File Processing Settings
ENABLE_VIRUS_SCANNING=False
ENABLE_RESUME_PARSING=True
ENABLE_IMAGE_OPTIMIZATION=True
IMAGE_QUALITY=85
MAX_IMAGE_WIDTH=1920
MAX_IMAGE_HEIGHT=1080
PDF_THUMBNAIL_SIZE=200,200

# Database Connection Pooling
DB_CONN_MAX_AGE=600
```

### Step 3: Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f celery_worker
```

### Step 4: Run Database Migrations

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

### Step 5: Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Step 6: Verify Services

Check that all services are running:

```bash
docker-compose ps
```

You should see:
- `jobboard_web` - Django application
- `jobboard_db` - PostgreSQL database
- `jobboard_redis` - Redis cache
- `jobboard_celery_worker` - Celery worker
- `jobboard_celery_beat` - Celery beat scheduler
- `jobboard_nginx` - Nginx reverse proxy

## Local Development Setup

If you prefer to run the application locally without Docker:

### Step 1: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install PostgreSQL and Redis

**PostgreSQL:**
- Download and install from [postgresql.org](https://www.postgresql.org/download/)
- Create a database:
  ```sql
  CREATE DATABASE jobboard_db;
  CREATE USER jobboard_user WITH PASSWORD 'jobboard_password';
  GRANT ALL PRIVILEGES ON DATABASE jobboard_db TO jobboard_user;
  ```

**Redis:**
- Download and install from [redis.io](https://redis.io/download)
- Start Redis server:
  ```bash
  redis-server
  ```

### Step 3: Configure Environment

Create a `.env` file (same as Docker setup, but update hostnames):

```env
DB_HOST=localhost
REDIS_HOST=localhost
```

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Start Development Server

```bash
python manage.py runserver
```

### Step 8: Start Celery (in separate terminals)

```bash
# Terminal 1: Celery Worker
celery -A config worker --loglevel=info

# Terminal 2: Celery Beat (for scheduled tasks)
celery -A config beat --loglevel=info
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_ENVIRONMENT` | Environment (development/production/testing) | `development` |
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | **Required** |
| `DB_NAME` | Database name | `jobboard_db` |
| `DB_USER` | Database user | `jobboard_user` |
| `DB_PASSWORD` | Database password | **Required** |
| `DB_HOST` | Database host | `db` (Docker) / `localhost` (Local) |
| `REDIS_HOST` | Redis host | `redis` (Docker) / `localhost` (Local) |

### Optional Environment Variables

See `.env.example` for a complete list of optional variables.

## Database Setup

### Initial Setup

```bash
# With Docker
docker-compose exec web python manage.py migrate

# Locally
python manage.py migrate
```

### Create Superuser

```bash
# With Docker
docker-compose exec web python manage.py createsuperuser

# Locally
python manage.py createsuperuser
```

### Load Sample Data (Optional)

```bash
# Create a management command or use Django admin
python manage.py shell
```

## Running the Application

### With Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart a specific service
docker-compose restart web

# View logs
docker-compose logs -f web
```

### Local Development

```bash
# Start Django server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A config worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A config beat --loglevel=info
```

## Accessing the Application

Once the application is running:

### API Endpoints

- **API Base URL**: `http://localhost:8000/api/v1/`
- **Swagger Documentation**: `http://localhost:8000/api/docs/`
- **ReDoc Documentation**: `http://localhost:8000/api/redoc/`
- **Health Check**: `http://localhost:8000/health/`

### Admin Panel

- **Admin URL**: `http://localhost:8000/admin/`
- Use the superuser credentials created earlier

### With Nginx (Docker)

- **Application**: `http://localhost/`
- **API**: `http://localhost/api/v1/`
- **Admin**: `http://localhost/admin/`

## Common Commands

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec web python manage.py <command>

# Access database
docker-compose exec db psql -U jobboard_user -d jobboard_db

# Access Redis CLI
docker-compose exec redis redis-cli
```

### Django Management Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run Django shell
python manage.py shell

# Check for issues
python manage.py check

# Run tests
python manage.py test
# OR
pytest
```

## Troubleshooting

### Database Connection Issues

**Problem**: Cannot connect to database

**Solutions**:
1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps db
   ```
2. Verify database credentials in `.env`
3. Check database logs:
   ```bash
   docker-compose logs db
   ```

### Redis Connection Issues

**Problem**: Redis connection errors

**Solutions**:
1. Check if Redis is running:
   ```bash
   docker-compose ps redis
   ```
2. Test Redis connection:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Migration Issues

**Problem**: Migration errors

**Solutions**:
```bash
# Reset migrations (WARNING: deletes data)
docker-compose exec web python manage.py migrate --run-syncdb

# Or manually fix migration conflicts
```

### Port Already in Use

**Problem**: Port 8000 or 5432 already in use

**Solutions**:
1. Change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"  # Change 8001 to available port
   ```
2. Or stop the service using the port

### Static Files Not Loading

**Problem**: Static files return 404

**Solutions**:
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL in settings
```

### Celery Not Working

**Problem**: Background tasks not executing

**Solutions**:
1. Check Celery worker logs:
   ```bash
   docker-compose logs celery_worker
   ```
2. Verify Redis connection
3. Restart Celery:
   ```bash
   docker-compose restart celery_worker celery_beat
   ```

### Permission Issues (Linux/Mac)

**Problem**: Permission denied errors

**Solutions**:
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x entrypoint.sh
```

## Production Deployment

For production deployment:

1. Set `DJANGO_ENVIRONMENT=production` in `.env`
2. Set `DEBUG=False`
3. Use a strong `SECRET_KEY`
4. Configure proper `ALLOWED_HOSTS`
5. Set up proper email backend (SMTP)
6. Use cloud storage (S3 or Supabase)
7. Configure SSL/TLS certificates
8. Set up proper database backups
9. Configure monitoring and logging
10. Review security settings

## Next Steps

1. **Import Postman Collection**: See `Job_Board_API.postman_collection.json`
2. **Read API Documentation**: Visit `http://localhost:8000/api/docs/`
3. **Create Test Users**: Use admin panel or API
4. **Explore Endpoints**: Use the Postman collection

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed documentation
- Review API documentation at `/api/docs/`
- Check logs: `docker-compose logs -f`

---

**Happy Coding! 🚀**
