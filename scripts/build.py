"""Rebuild the FYSETC SD-WiFi V2.1 firmware and LittleFS image.

Requirements: git, PlatformIO CLI, Python 3.9+.
The build downloads only the pinned public ESP3D source. It never reads
credentials or a flash dump from the device.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_URL = "https://github.com/luc-github/ESP3D.git"
UPSTREAM_COMMIT = "b85dc1cce0f87894e524c96f3685fcba48006e67"


def run(*args: str, cwd: Path | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Use an existing clean ESP3D checkout")
    parser.add_argument("--platformio", default="pio", help="PlatformIO executable")
    args = parser.parse_args()

    source = args.source.resolve() if args.source else ROOT / ".build" / "ESP3D"
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "--branch", "3.1", UPSTREAM_URL, str(source))
        run("git", "checkout", "--detach", UPSTREAM_COMMIT, cwd=source)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if commit != UPSTREAM_COMMIT:
        raise SystemExit(f"Expected ESP3D {UPSTREAM_COMMIT}, got {commit}")
    patch = ROOT / "firmware" / "esp3d-3.1.patch"
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=source, text=True).splitlines()
    already_patched = subprocess.run(
        ["git", "apply", "--reverse", "--check", str(patch)], cwd=source
    ).returncode == 0
    expected_generated = {"?? esp3d/data-sdwifi/"}
    unexpected = [line for line in status if line not in expected_generated]
    if unexpected and not already_patched:
        raise SystemExit("ESP3D source contains unexpected local changes")
    if not already_patched:
        run("git", "apply", "--check", str(patch), cwd=source)
        run("git", "apply", str(patch), cwd=source)
    data_dir = source / "esp3d" / "data-sdwifi"
    data_dir.mkdir(exist_ok=True)
    html = (ROOT / "web" / "index.html").read_bytes()
    (data_dir / "index.html.gz").write_bytes(gzip.compress(html, compresslevel=9, mtime=0))
    shutil.copy2(ROOT / "web" / "favicon.svg", data_dir / "favicon.svg")

    run(args.platformio, "run", "-e", "esp8285", "-t", "buildfs", cwd=source)
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    shutil.copy2(source / ".pioenvs" / "esp8285" / "littlefs.bin", output / "littlefs.bin")
    run(args.platformio, "run", "-e", "esp8285", cwd=source)
    shutil.copy2(source / ".pioenvs" / "esp8285" / "firmware.bin", output / "firmware.bin")
    shutil.copy2(data_dir / "index.html.gz", output / "index.html.gz")
    shutil.copy2(data_dir / "favicon.svg", output / "favicon.svg")
    for name in ("firmware.bin", "littlefs.bin", "index.html.gz", "favicon.svg"):
        path = output / name
        print(f"{name}: {path.stat().st_size} bytes, SHA-256 {sha256(path)}")


if __name__ == "__main__":
    main()
