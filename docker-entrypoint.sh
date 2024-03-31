#!/usr/bin/env bash

set -e

# You can comment out this line if you want to migrate manually
python manage.py migrate --noinput

exec "$@"
