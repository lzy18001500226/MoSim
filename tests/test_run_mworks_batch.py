#!/usr/bin/env python3
"""Regression checks for batch scenario command planning."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/run_mworks_batch.py",
            "--dry-run",
            "--skip-existing",
            "scenarios/smoke/*.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "example1_pid_mcp_smoke.yaml" not in output:
        raise AssertionError(output)
    if "Skipped existing: 1" not in output:
        raise AssertionError(output)
    if "Failures: 0" not in output:
        raise AssertionError(output)
    print("[OK] run_mworks_batch dry-run regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
