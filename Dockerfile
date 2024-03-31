# This Dockerfile uses multi-stage build to customize DEV and PROD images:
# https://docs.docker.com/develop/develop-images/multistage-build/
FROM python:3.11.4-slim-bullseye as python-base

ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.7.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    \
    RUN_CRON=false


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY ./docker/django/entrypoint.sh /docker-entrypoint.sh
RUN chmod +x "/docker-entrypoint.sh"

ENTRYPOINT ["/docker-entrypoint.sh"]

# System deps:
RUN apt-get -y update && apt-get install --no-install-recommends -y \
  git gettext build-essential 

FROM python-base as builder-base

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where 
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN --mount=type=cache,target=/root/.cache \
    poetry install --only main --no-directory

# Copy core and material library and install as package
COPY ./core $PYSETUP_PATH/core
RUN --mount=type=cache,target=/root/.cache \
    poetry install --only main


FROM python-base as develop
ENV DJANGO_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Also install dev deps
RUN --mount=type=cache,target=/root/.cache \
    poetry install --with=dev --sync

EXPOSE 8000
WORKDIR /nfc-card-game

#############
# PRODUCTION
# This steps needs bundled core in metal-cloud/core/dist/metal.exe
#############
FROM python-base as production
ENV DJANGO_ENV=production

COPY ./docker/django/cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob && crontab /etc/cron.d/cronjob

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /nfc-card-game

WORKDIR /nfc-card-game


