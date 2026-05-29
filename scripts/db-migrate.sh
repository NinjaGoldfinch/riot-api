#!/usr/bin/env sh
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is required to run migrations."
  exit 1
fi

python -m alembic upgrade head
