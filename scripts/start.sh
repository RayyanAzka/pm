#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
LOG_FILE="$ROOT_DIR/.pm-server.log"
PID_FILE="$ROOT_DIR/.pm-server.pid"

cd "$BACKEND_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it with: pip install uv"
  exit 1
fi

if [ ! -d .venv ]; then
  uv venv .venv --python 3.12
fi

uv sync
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

echo "$SERVER_PID" > "$PID_FILE"
echo "PM server started on http://localhost:8000"
