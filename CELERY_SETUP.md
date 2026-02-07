# Celery Setup Guide

This guide explains how to set up and run Celery for background tasks in the Job Board Platform.

## Prerequisites

1. Redis server running (for Celery broker and result backend)
2. Python packages installed: `celery`, `celery-beat`, `redis`

## Installation

```bash
pip install celery celery-beat redis
```

## Configuration

Celery is configured in `config/celery.py` and uses Redis as the message broker.

### Environment Variables

Add to your `.env` file:

```env
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

## Running Celery

### 1. Start Redis Server

```bash
# On Linux/Mac
redis-server

# On Windows (if installed)
redis-server
```

### 2. Start Celery Worker

```bash
celery -A config worker --loglevel=info
```

### 3. Start Celery Beat (Scheduler)

```bash
celery -A config beat --loglevel=info
```

### 4. Start Both Together (Development)

```bash
celery -A config worker --beat --loglevel=info
```

## Production Setup

For production, use a process manager like `supervisord` or `systemd`:

### Supervisor Configuration Example

```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A config worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A config beat --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

## Scheduled Tasks

The following tasks are scheduled via Celery Beat:

- **process-job-expiration**: Runs every hour to close expired jobs
- **process-scheduled-jobs**: Runs every 5 minutes to publish scheduled jobs
- **send-application-deadline-reminders**: Runs daily to send deadline reminders
- **cleanup-old-notifications**: Runs daily to clean up old notifications
- **generate-daily-reports**: Runs daily to generate reports

## Available Tasks

### Email Tasks
- `send_email_async`: Send emails asynchronously

### Job Tasks
- `process_job_expiration`: Process expired jobs
- `process_scheduled_jobs`: Publish scheduled jobs
- `send_application_deadline_reminders`: Send deadline reminders

### File Processing Tasks
- `process_file_async`: Process files (resume parsing, image optimization, etc.)

### Core Tasks
- `cleanup_old_notifications`: Clean up old notifications
- `generate_daily_reports`: Generate daily reports
- `send_bulk_notifications`: Send notifications to multiple users

## Monitoring

### Flower (Optional)

Install Flower for Celery monitoring:

```bash
pip install flower
celery -A config flower
```

Access Flower at `http://localhost:5555`

## Troubleshooting

1. **Redis Connection Error**: Ensure Redis is running and accessible
2. **Tasks Not Executing**: Check Celery worker logs
3. **Scheduled Tasks Not Running**: Ensure Celery Beat is running
4. **Import Errors**: Ensure all apps are in `INSTALLED_APPS`

## Docker Setup

If using Docker, add Celery services to `docker-compose.yml`:

```yaml
celery_worker:
  build: .
  command: celery -A config worker --loglevel=info
  volumes:
    - .:/app
  depends_on:
    - db
    - redis
  env_file:
    - .env

celery_beat:
  build: .
  command: celery -A config beat --loglevel=info
  volumes:
    - .:/app
  depends_on:
    - db
    - redis
  env_file:
    - .env

redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```
