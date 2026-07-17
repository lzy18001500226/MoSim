#!/usr/bin/env python3
"""Prepare a PX4 rcS overlay that uses the official RAM dataman backend."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


SCHEMA = "mosim.px4.ram_dataman_rcs.v1"
TARGET_LINE = "dataman start"
INSERTION = (
    "# MoSim SITL runs do not require mission persistence across PX4 restarts.\n"
    "param set SYS_DM_BACKEND 1\n"
    "dataman start -r"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def transform(source: str) -> str:
    lines = source.splitlines()
    matches = [index for index, line in enumerate(lines) if line == TARGET_LINE]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {TARGET_LINE!r} line, found {len(matches)}")
    lines[matches[0] : matches[0] + 1] = INSERTION.splitlines()
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_bytes = args.source.read_bytes()
    output_text = transform(source_bytes.decode("utf-8"))
    output_bytes = output_text.encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output_bytes)
    os.chmod(args.output, 0o755)

    payload = {
        "schema": SCHEMA,
        "status": "passed",
        "source": str(args.source.resolve()),
        "source_sha256": sha256_bytes(source_bytes),
        "output": str(args.output.resolve()),
        "output_sha256": sha256_bytes(output_bytes),
        "dataman_backend": "ram",
        "sys_dm_backend": 1,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
