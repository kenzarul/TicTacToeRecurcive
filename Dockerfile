# syntax=docker/dockerfile:1.13
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE='tictactoe.settings'

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache pip install --upgrade pip && \
    pip install --use-pep517 -r requirements.txt

COPY . .

EXPOSE 8000
ENTRYPOINT ["bash", "/app/run.sh"]