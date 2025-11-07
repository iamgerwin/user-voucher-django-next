#!/bin/bash
set -e

echo "Starting Django entrypoint script..."

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."

    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):\([0-9]*\)\/.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):\([0-9]*\)\/.*/\2/p')

    # Default values if extraction fails
    DB_HOST=${DB_HOST:-db}
    DB_PORT=${DB_PORT:-5432}

    # Wait for PostgreSQL to be ready
    max_attempts=30
    attempt=0

    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null || [ $attempt -eq $max_attempts ]; do
        attempt=$((attempt + 1))
        echo "PostgreSQL is unavailable - attempt $attempt/$max_attempts - sleeping"
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        echo "PostgreSQL did not become ready in time. Proceeding anyway..."
    else
        echo "PostgreSQL is ready!"
    fi
}

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis to be ready..."

    # Extract host and port from REDIS_URL
    REDIS_HOST=$(echo $REDIS_URL | sed -n 's|redis://\([^:]*\):\([0-9]*\).*|\1|p')
    REDIS_PORT=$(echo $REDIS_URL | sed -n 's|redis://\([^:]*\):\([0-9]*\).*|\2|p')

    # Default values if extraction fails
    REDIS_HOST=${REDIS_HOST:-redis}
    REDIS_PORT=${REDIS_PORT:-6379}

    # Wait for Redis to be ready
    max_attempts=30
    attempt=0

    until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null | grep -q PONG || [ $attempt -eq $max_attempts ]; do
        attempt=$((attempt + 1))
        echo "Redis is unavailable - attempt $attempt/$max_attempts - sleeping"
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        echo "Redis did not become ready in time. Proceeding anyway..."
    else
        echo "Redis is ready!"
    fi
}

# Wait for services
wait_for_postgres
wait_for_redis

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if DJANGO_SUPERUSER_USERNAME is set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser if it doesn't exist..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
END
fi

echo "Entrypoint script completed successfully!"

# Execute the main command
exec "$@"
