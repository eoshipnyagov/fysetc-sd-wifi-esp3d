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
    session = requests.Session()

    response = session.get(f"{base}/files", params={"path": "/"}, timeout=20)
    response.raise_for_status()
    info = response.json()
    if info.get("status") != "ok":
        raise SystemExit(f"LittleFS unavailable: {info.get('status')}")
    print(f"LittleFS: {info.get('used')} / {info.get('total')}")

    for image, content_type in (
        (ROOT / "dist" / "index.html.gz", "application/gzip"),
        (ROOT / "dist" / "favicon.svg", "image/svg+xml"),
    ):
        payload = image.read_bytes()
        response = session.post(
            f"{base}/files",
            data={"path": "/", f"{image.name}S": str(len(payload))},
            files={"myfiles": (image.name, payload, content_type)},
            timeout=90,
        )
        response.raise_for_status()
        uploaded = response.json()
        status = str(uploaded.get("status", "")).lower()
        if "failed" in status or "error" in status:
            raise SystemExit(f"Upload failed: {uploaded.get('status')}")

        response = session.get(f"{base}/{image.name}", timeout=20)
        response.raise_for_status()
        actual = response.content
        if hashlib.sha256(actual).digest() != hashlib.sha256(payload).digest():
            raise SystemExit(f"Verification failed: stored {image.name} differs from the build")
        print(f"Verified {image.name}: {len(actual)} bytes")

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
    if b"SD Wi" not in response.content or b"page-files" not in response.content or b"favicon.svg" not in response.content:
        raise SystemExit("Root page did not serve the new WebUI")
    print(f"Installed at {base}/")


if __name__ == "__main__":
    main()
