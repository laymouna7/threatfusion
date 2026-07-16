#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

export PATH="$HOME/.local/bin:$PATH"

# Create venv with Python 3.12 if missing
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment (3.12)..."
  uv venv --python 3.12
fi

source .venv/bin/activate

# Install deps if missing
if [ ! -f ".venv/installed" ]; then
  echo "Installing dependencies..."
  uv pip install -q -r requirements-dev.txt
  touch .venv/installed
fi

echo "Starting ThreatFusion backend on http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
