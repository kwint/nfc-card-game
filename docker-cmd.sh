#!/bin/sh
# vim:sw=4:ts=4:et

python manage.py collectstatic --noinput

if [ "$1" = "--debug" ]; then
  # Django development server
  exec python manage.py runserver 0.0.0.0:8000
else
  # Gunicorn
  exec daphne "nfc_card_game.asgi:application" \
    -p 8000 \
    -t "$GUNICORN_TIMEOUT"
fi
