#!/usr/bin/env python3
"""Tests for the Sunray FAST-LIO frame-transform C++ helper."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_sunray_cpp_frame_transform() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "Scripts" / "quality" / "check_sunray_cpp_frame_transform.py")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    if payload["status"] != "passed":
        raise AssertionError(payload)
    if not any("Static compile/unit check only" in item for item in payload["claim_boundary"]):
        raise AssertionError(payload)


if __name__ == "__main__":
    test_sunray_cpp_frame_transform()
    print("[OK] Sunray C++ frame transform")
