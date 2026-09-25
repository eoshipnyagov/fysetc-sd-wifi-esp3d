#!/usr/bin/env bash
# Flash firmware and the WebUI image. Usage: ./scripts/flash-com.sh [PORT]
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${1:-COM3}"
cd "$repo_dir"

if [[ ! -x .venv/bin/python ]]; then
  echo "Run scripts/setup.sh first." >&2
  exit 1
fi
if [[ ! -f dist/firmware.bin || ! -f dist/littlefs.bin ]]; then
  echo "Build images first: ./scripts/build.sh" >&2
  exit 1
fi

echo "Flashing $port. Put the board into bootloader mode first: USB2UART, hold FLSH while connecting USB, then release FLSH."
.venv/bin/python -m esptool --port "$port" --chip esp8266 --baud 460800 --before no-reset --after hard-reset \
  write-flash --flash-mode dout --flash-freq 40m --flash-size 2MB \
  0x0 dist/firmware.bin 0x1C0000 dist/littlefs.bin
echo "Done. Press RST without FLSH."
