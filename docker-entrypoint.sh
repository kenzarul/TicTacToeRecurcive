#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL is ready!"

echo "Waiting for Redis to be ready..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Daphne ASGI server..."
exec daphne -b 0.0.0.0 -p 8000 tictactoe.asgi:application
