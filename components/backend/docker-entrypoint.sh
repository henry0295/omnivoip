#!/bin/bash
set -e

echo "========================================"
echo "OmniVoIP Backend Starting..."
echo "========================================"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! pg_isready -h "${POSTGRES_HOST:-postgresql}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-omnivoip}"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up and running!"

# Wait for Redis
echo "Waiting for Redis..."
until redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ${REDIS_PASSWORD:+-a "$REDIS_PASSWORD"} ping 2>/dev/null; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "Redis is up and running!"

# Run migrations
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  python manage.py migrate --noinput
fi

# Collect static files
if [ "${COLLECT_STATIC:-true}" = "true" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput --clear
fi

# Create cache table
echo "Creating cache table..."
python manage.py createcachetable 2>/dev/null || true

# Create default superuser if it doesn't exist
echo "Checking for admin user..."
python manage.py shell <<EOF 2>/dev/null || true
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@omnivoip.com', 'admin')
    print("Admin user created: admin/admin")
else:
    print("Admin user already exists")
EOF

echo "========================================"
echo "Starting application server..."
echo "========================================"

# Execute the main command
exec "$@"
