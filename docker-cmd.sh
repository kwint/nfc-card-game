#!/bin/sh
# vim:sw=4:ts=4:et

python manage.py collectstatic --noinput

if [ "$1" = "--debug" ]; then
  # Django development server
  exec python manage.py runserver 0.0.0.0:8000
else
  # Gunicorn
  exec daphne -p 8000 "nfc_card_game.wsgi:application" \
    --workers "$GUNICORN_WORKERS" \
    --http-timeout "$GUNICORN_TIMEOUT" \
    --log-level "$GUNICORN_LOG_LEVEL"
fi
