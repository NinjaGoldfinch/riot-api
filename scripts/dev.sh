#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

"${PYTHON_BIN}" -m uvicorn app.main:app \
  --reload \
  --host "${HOST:-127.0.0.1}" \
  --port "${PORT:-8000}"
