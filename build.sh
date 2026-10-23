#!/usr/bin/env bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser (if not exists)..."
# Единственный источник дефолта; в Python читается строго из окружения
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@foodbase.by', os.environ['ADMIN_PASSWORD'])
    print('Superuser created.')
else:
    print('Superuser already exists, skipping.')
"
