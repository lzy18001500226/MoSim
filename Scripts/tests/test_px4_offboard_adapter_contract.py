#!/usr/bin/env python3
"""Tests for the guarded PX4 Offboard adapter static contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_px4_offboard_adapter_contract() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "Scripts" / "quality" / "check_px4_offboard_adapter_contract.py")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    if payload["status"] != "passed":
      raise AssertionError(payload)
    if payload["missing_contracts"]:
      raise AssertionError(payload)
    if not any("Default parameters do not arm" in item for item in payload["claim_boundary"]):
      raise AssertionError(payload)


if __name__ == "__main__":
    test_px4_offboard_adapter_contract()
    print("[OK] PX4 Offboard adapter contract")
