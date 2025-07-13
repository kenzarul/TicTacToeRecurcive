#!/bin/bash
set -e

echo "=== TicTacToe Docker Deployment Validation ==="

echo "Waiting for MySQL to be ready..."
while ! nc -z db 3306; do
  sleep 1
done
echo "✅ MySQL is ready!"

echo "Waiting for Redis to be ready..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "✅ Redis is ready!"

echo "Running Django system checks..."
python manage.py check --deploy

echo "Checking for missing migrations..."
python manage.py makemigrations --check --dry-run

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('✅ Superuser already exists')
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Testing health check endpoint..."
python manage.py shell << EOF
from django.test import Client
client = Client()
response = client.get('/health/')
if response.status_code == 200:
    print('✅ Health check endpoint working')
else:
    print('❌ Health check endpoint failed')
    exit(1)
EOF

echo "✅ All validation checks passed!"
echo "Starting Daphne ASGI server on port 8080..."
exec daphne -b 0.0.0.0 -p 8080 tictactoe.asgi:application
