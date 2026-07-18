#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export PATH="$HOME/.local/bin:$PATH"

if [ ! -d ".venv" ]; then
  echo "No .venv found. Run 'pnpm dev' first to set up."
  exit 1
fi

source .venv/bin/activate

echo "Upgrading all packages to latest compatible versions..."
uv pip install --upgrade -r requirements.txt

echo ""
echo "Done. Run 'pnpm check:deps' to verify no outdated packages remain."
