# inspired by https://github.com/michaeloliverx/python-poetry-docker-example/blob/master/docker/Dockerfile
FROM python:3.12-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

# install poetry - see https://python-poetry.org/docs/#installation
ENV POETRY_VERSION=1.8.3
RUN curl -sSL https://install.python-poetry.org | python3 -


RUN apt-get update && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR /app
COPY ./poetry.lock .
COPY ./pyproject.toml .
RUN poetry install --no-dev

# 'development' stage installs all dev deps and can be used to develop code.
# For example using docker-compose to mount local volume under /app
FROM base AS development

WORKDIR /app
COPY . .

RUN poetry install

ENV DJANGO_SETTINGS_MODULE=core.settings

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]