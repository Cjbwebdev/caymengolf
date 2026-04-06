#!/bin/bash
python manage.py migrate --noinput 2>/dev/null || echo "Migration skipped or failed, starting anyway..."
exec gunicorn core.wsgi --log-file - --bind 0.0.0.0:$PORT
