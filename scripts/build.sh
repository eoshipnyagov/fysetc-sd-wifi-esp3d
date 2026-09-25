#!/usr/bin/env bash
# Build firmware.bin and littlefs.bin into dist/.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

if [[ ! -x .venv/bin/python || ! -x .venv/bin/pio ]]; then
  echo "Run scripts/setup.sh first." >&2
  exit 1
fi

.venv/bin/python scripts/build.py --platformio "$repo_dir/.venv/bin/pio"
