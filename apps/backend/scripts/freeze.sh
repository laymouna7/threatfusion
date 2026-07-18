#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export PATH="$HOME/.local/bin:$PATH"

if [ ! -d ".venv" ]; then
  echo "No .venv found. Run 'pnpm dev' first to set up."
  exit 1
fi

source .venv/bin/activate

echo "Pinning installed versions to requirements.txt..."
uv pip freeze > requirements.txt

echo "Done. requirements.txt now has pinned versions."
