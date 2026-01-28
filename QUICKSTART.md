# Quick Start Guide

This guide will help you get the Job Board Platform backend up and running quickly.

## Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Docker and Docker Compose (optional, for containerized setup)

## Option 1: Docker Setup (Recommended)

### Step 1: Clone and Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env file with your settings (optional, defaults work for Docker)
```

### Step 2: Build and Run with Docker

```bash
# Build and start all services
make setup

# Or manually:
docker-compose build
docker-compose up -d

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Step 3: Access the Application

- **API**: http://localhost:8000/api/
- **Swagger Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

## Option 2: Local Development Setup

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup PostgreSQL Database

```bash
# Create database
psql -U postgres
CREATE DATABASE jobboard_db;
CREATE USER jobboard_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE jobboard_db TO jobboard_user;
\q
```

### Step 4: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env file with your database credentials
# Update DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

## Testing the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "role": "user",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 3. Get Jobs (No Authentication Required)

```bash
curl http://localhost:8000/api/jobs/
```

### 4. Create a Job (Requires Authentication)

```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Software Developer",
    "description": "We are looking for a skilled software developer...",
    "requirements": "5+ years experience in Python and Django",
    "category": 1,
    "location": "New York, NY",
    "job_type": "full-time",
    "salary_min": 80000,
    "salary_max": 120000,
    "status": "active"
  }'
```

## Common Commands

### Docker Commands

```bash
# View logs
make logs
# or
docker-compose logs -f

# Run migrations
make migrate
# or
docker-compose exec web python manage.py migrate

# Create superuser
make createsuperuser
# or
docker-compose exec web python manage.py createsuperuser

# Access Django shell
make shell
# or
docker-compose exec web python manage.py shell

# Stop services
make down
# or
docker-compose down
```

### Local Development Commands

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Access Django shell
python manage.py shell
```

## Next Steps

1. Explore the API documentation at `/api/docs/`
2. Create test users with different roles (admin, employer, user)
3. Create categories for jobs
4. Post jobs and test the application flow
5. Review the full README.md for detailed documentation

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists and user has proper permissions

### Migration Errors

```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial
```

### Port Already in Use

```bash
# Change port in docker-compose.yml or use different port
python manage.py runserver 8001
```

## Support

For more information, see the full [README.md](README.md) file.

