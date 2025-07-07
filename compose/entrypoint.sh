#!/usr/bin/env bash
set -e

# Attendre que Postgres réponde
until pg_isready -h "\" -p "\" -U "\"; do
  echo "Postgres indisponible — attente…"
  sleep 2
done

python manage.py check --deploy
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

exec daphne -b 0.0.0.0 -p 8000 tictactoe.asgi:application
