#!/usr/bin/env python3
"""Regression checks for the seven-scenario static preflight contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_seven_scenario_preflight.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_seven_scenario_preflight", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_static_preflight_contract() -> None:
    checker = load_checker()
    payload = checker.validate_preflight()
    assert payload["status"] == "passed", payload["errors"]
    assert payload["live_mworks_touched"] is False
    assert payload["scenario_simulation_started"] is False
    assert payload["error_count"] == 0


def main() -> int:
    test_static_preflight_contract()
    print("[OK] seven-scenario static preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
