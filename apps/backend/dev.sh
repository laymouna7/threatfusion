#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Starting ThreatFusion backend on http://localhost:8000"
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
