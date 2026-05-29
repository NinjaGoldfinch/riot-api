#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
fi

cd "${ROOT_DIR}"
export APP_NAME="${APP_NAME:-Riot API}"
export APP_ENV="${APP_ENV:-development}"

"${PYTHON_BIN}" - <<'PY'
import json
from pathlib import Path

from app.main import app

output_path = Path("docs/openapi.json")
output_path.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output_path}")
PY
