FROM python:3.12.3-slim as builder

WORKDIR /code

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==1.8
COPY pyproject.toml poetry.lock ./

RUN poetry install

######################################################

FROM python:3.12.3-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY ./.env /code/.env

COPY ./app /code/app

COPY ./migrations /code/migrations
COPY ./alembic.ini /code/alembic.ini
