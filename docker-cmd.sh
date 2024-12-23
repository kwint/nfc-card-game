#!/bin/sh
# vim:sw=4:ts=4:et

python manage.py collectstatic --noinput

if [ "$1" = "--debug" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  exec daphne -b 0.0.0.0 -p 8000 nfc_card_game.asgi:application
fi
