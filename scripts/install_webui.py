"""Install the compact WebUI onto a running ESP3D board over HTTP.

The script verifies the new page before removing legacy pages. The board
must already be reachable in STA mode or through its access point.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="Board IP address or hostname, without http://")
    parser.add_argument("--keep-legacy", action="store_true", help="Do not remove old tool/camera pages")
    args = parser.parse_args()
    base = f"http://{args.host.strip('/')}"
    image = ROOT / "dist" / "index.html.gz"
    payload = image.read_bytes()
    session = requests.Session()

    response = session.get(f"{base}/files", params={"path": "/"}, timeout=20)
    response.raise_for_status()
    info = response.json()
    if info.get("status") != "ok":
        raise SystemExit(f"LittleFS unavailable: {info.get('status')}")
    print(f"LittleFS: {info.get('used')} / {info.get('total')}")

    response = session.post(
        f"{base}/files",
        data={"path": "/", "index.html.gzS": str(len(payload))},
        files={"myfiles": ("index.html.gz", payload, "application/gzip")},
        timeout=90,
    )
    response.raise_for_status()
    uploaded = response.json()
    if "failed" in str(uploaded.get("status", "")).lower() or "error" in str(uploaded.get("status", "")).lower():
        raise SystemExit(f"Upload failed: {uploaded.get('status')}")

    response = session.get(f"{base}/index.html.gz", timeout=20)
    response.raise_for_status()
    actual = response.content
    if hashlib.sha256(actual).digest() != hashlib.sha256(payload).digest():
        raise SystemExit("Verification failed: the stored page differs from the build")
    print(f"New WebUI verified: {len(actual)} bytes")

    if not args.keep_legacy:
        for name in ("tool.html", "esp32cam.html"):
            response = session.get(
                f"{base}/files",
                params={"path": "/", "action": "delete", "filename": name},
                timeout=20,
            )
            response.raise_for_status()
            result = response.json()
            status = result.get("status", "")
            if "deleted" not in status and "does not exists" not in status:
                raise SystemExit(f"Could not remove {name}: {status}")
            print(f"Removed {name}")

    response = session.get(f"{base}/", timeout=20)
    response.raise_for_status()
    if b"SD Wi" not in response.content or b"page-files" not in response.content:
        raise SystemExit("Root page did not serve the new WebUI")
    print(f"Installed at {base}/")


if __name__ == "__main__":
    main()
