#!/bin/bash
set -e

# Run migrations (best effort - don't fail if DB not ready)
python manage.py migrate --noinput || echo "Migration skipped or failed"

# Run collectstatic
python manage.py collectstatic --noinput || echo "Collectstatic skipped or failed"

# Start the server
exec gunicorn core.wsgi --log-file - --bind 0.0.0.0:$PORT