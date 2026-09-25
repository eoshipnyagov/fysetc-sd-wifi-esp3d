#!/usr/bin/env bash
# Create a local Python environment and install the tools used by this project.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

python_cmd="${PYTHON:-python3}"
if ! command -v "$python_cmd" >/dev/null 2>&1; then
  python_cmd="python"
fi
if ! command -v "$python_cmd" >/dev/null 2>&1; then
  echo "Python 3.9 or newer is required." >&2
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  "$python_cmd" -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt platformio esptool
echo "Environment is ready: $repo_dir/.venv"
