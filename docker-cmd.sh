#!/bin/sh
# vim:sw=4:ts=4:et

python manage.py collectstatic --noinput

if [ "$1" = "--debug" ]; then
  # Django development server
  exec python manage.py runserver 0.0.0.0:8000
else
  # Gunicorn
  exec gunicorn "nfc_card_game.wsgi:application" \
    --bind "0.0.0.0:8000" \
    --workers "$GUNICORN_WORKERS" \
    --timeout "$GUNICORN_TIMEOUT" \
    --log-level "$GUNICORN_LOG_LEVEL"
fi
