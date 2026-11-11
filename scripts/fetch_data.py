"""Download the four files of PhysioNet treadmill-exercise-cardioresp 1.0.1 and verify them.

Usage (from the project root):
    .venv/bin/python scripts/fetch_data.py

Files already present are only verified. Missing files are downloaded to a .part file, checked
against the pinned official SHA256 and size, and only then renamed into data/raw/. The script
exits with an error on any mismatch and never overwrites or deletes an existing file.
The CSV files stay local under data/raw/ and are gitignored; they are not redistributed.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from malaga_exercise_lab import data as D  # noqa: E402

PINNED = {D.SUMS_FILE: {"sha256": D.SUMS_SHA256, "bytes": D.SUMS_BYTES}, **D.EXPECTED}


def fetch(name: str) -> None:
    target = D.RAW_DIR / name
    if target.exists():
        return
    part = target.with_suffix(target.suffix + ".part")
    url = D.FILES_URL + name
    print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as resp, open(part, "wb") as fh:
        while chunk := resp.read(1 << 20):
            fh.write(chunk)
    D.verify_file(part, PINNED[name]["sha256"], PINNED[name]["bytes"])
    part.rename(target)


def main() -> int:
    D.RAW_DIR.mkdir(parents=True, exist_ok=True)
    try:
        for name in PINNED:
            fetch(name)
        result = D.verify_raw()
    except D.IntegrityError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    for name, v in result.items():
        print(f"ok {name} {v['bytes']} bytes sha256 {v['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
