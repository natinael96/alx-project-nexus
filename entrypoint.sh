#!/bin/bash
set -e

# Using cloud PostgreSQL (Neon) - no need to wait for local database
echo "Using cloud database: ${DB_HOST}"

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
max_attempts=30
attempt=0
while ! nc -z redis 6379; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "Redis is not available after $max_attempts attempts. Continuing anyway..."
    break
  fi
  sleep 1
done
if nc -z redis 6379; then
  echo "Redis is ready!"
else
  echo "Warning: Redis connection check failed, but continuing..."
fi

echo "Creating migrations..."
python manage.py makemigrations || echo "No new migrations to create"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting application..."
exec "$@"
