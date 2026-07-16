#!/usr/bin/env python3
"""Generate or verify the immutable QGroundControl vendor SHA256 manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VENDOR = PROJECT_ROOT / "apps" / "flight_console" / "vendor" / "qgroundcontrol"
DEFAULT_MANIFEST = DEFAULT_VENDOR.parent / "qgroundcontrol.SHA256SUMS"


def iter_files(root: Path):
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "custom":
            continue
        if path.is_file() and ".git" not in path.parts:
            yield path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest().upper()


def render(root: Path) -> str:
    lines = [f"{digest(path)}  {path.relative_to(root).as_posix()}" for path in iter_files(root)]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendor", type=Path, default=DEFAULT_VENDOR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    expected = render(args.vendor.resolve())
    if args.verify:
        if not args.manifest.is_file():
            print(f"missing manifest: {args.manifest}")
            return 1
        if args.manifest.read_text(encoding="utf-8") != expected:
            print(f"vendor manifest mismatch: {args.manifest}")
            return 1
        print(f"vendor manifest verified: {len(expected.splitlines())} files")
        return 0

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(expected, encoding="utf-8", newline="\n")
    print(f"vendor manifest written: {len(expected.splitlines())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
