#!/bin/sh
# vim:sw=4:ts=4:et

python manage.py collectstatic --noinput

# Creating the first user in the system
# USER_EXISTS="from django.contrib.auth import get_user_model; User = get_user_model(); exit(User.objects.exists())"
# exec python manage.py shell -c "$USER_EXISTS" && su-exec "$USER" python manage.py createsuperuser --noinput


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
