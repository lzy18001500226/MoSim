#!/usr/bin/env python3
"""Regression checks for graphical Sysblock controller contracts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "mworks" / "check_sysblock_graphics.py"
    spec = importlib.util.spec_from_file_location("check_sysblock_graphics", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_sysblock_graphics.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_graphical_awff_sysblock_contract() -> None:
    module = load_module()
    summary = module.run_checks()
    if not summary["ok"]:
        failures = []
        for item in summary["Results"]:
            for failure in item["failures"]:
                failures.append(f"{Path(item['file']).name}: {failure}")
        raise AssertionError("; ".join(failures))


def main() -> int:
    test_graphical_awff_sysblock_contract()
    print("[OK] graphical Sysblock contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
