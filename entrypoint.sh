#!/bin/bash
# Don't exit on error - we want to handle migration errors gracefully
set +e

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

# Wait for database to be ready (check by trying to show migrations)
echo "Waiting for database connection..."
max_attempts=30
attempt=0
while ! python manage.py showmigrations > /dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "Database is not available after $max_attempts attempts. Exiting..."
    exit 1
  fi
  sleep 1
done
echo "Database connection established!"

# Check if we need to create migrations (only if SKIP_MAKEMIGRATIONS is not set)
if [ -z "$SKIP_MAKEMIGRATIONS" ]; then
  echo "Checking for new migrations..."
  python manage.py makemigrations --check > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "No new migrations needed."
  else
    echo "Creating new migrations..."
    python manage.py makemigrations || {
      echo "Warning: Failed to create migrations. Continuing with existing migrations..."
    }
  fi
else
  echo "Skipping makemigrations (SKIP_MAKEMIGRATIONS is set)"
fi

# Run migrations with better error handling
echo "Running migrations..."
python manage.py migrate --noinput
MIGRATE_EXIT_CODE=$?

if [ $MIGRATE_EXIT_CODE -ne 0 ]; then
  echo "Migration failed with exit code $MIGRATE_EXIT_CODE"
  echo "Checking migration status..."
  python manage.py showmigrations --list | grep "\[ \]" || echo "All migrations appear to be applied"
  
  # If migration fails, try to show what's wrong
  echo "Attempting to get more details..."
  python manage.py migrate --noinput --verbosity 2 2>&1 | tail -20
  
  # Don't exit - let the application start anyway if it's just a migration conflict
  # The admin can fix migrations manually if needed
  echo "Warning: Migrations did not complete successfully. Application will start anyway."
  echo "You may need to run migrations manually: docker-compose exec web python manage.py migrate"
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput || {
  echo "Warning: Failed to collect static files. Continuing..."
}

echo "Starting application..."
# Re-enable exit on error for the actual application
set -e
exec "$@"
