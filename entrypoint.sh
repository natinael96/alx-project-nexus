#!/bin/bash
set -e

# Only wait for local PostgreSQL if DB_HOST is 'db' (Docker service)
if [ "${DB_HOST:-db}" = "db" ]; then
    echo "Waiting for PostgreSQL to be ready..."
    while ! nc -z db 5432; do
      sleep 0.1
    done
    echo "PostgreSQL is ready!"
else
    echo "Using external database: ${DB_HOST}"
fi

echo "Waiting for Redis to be ready..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting application..."
exec "$@"
