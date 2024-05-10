# Prerequisites

- Poetry
- python3.11 and python3.11-dev
- libpq-dev
- docker


# Start up:

```bash
cp .env.template .env
```
set DJANGO_SECRET_KEY in .env to the output of `python3 -c 'from django.utils.crypto import get_random_string; print(get_random_string(50))'`


```bash
poetry install

poetry shell
```

## dev:

### via docker

```bash
docker compose up
```

### Run django manually

Add this to /etc/hosts
```
127.0.0.1       db
```


```bash
docker compose up -d db

python manage.py migrate

python manage.py runserver
```

## Initialize
```bash
python manage.py createsuperuser

# or when running through Docker compose
docker compose run -it web ./manage.py createsuperuser
```

## prod:

```bash
docker compose up -f compose.yml -f compose.prod.yml up
```
