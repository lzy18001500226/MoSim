from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "mworks" / "check_baseline_ssblock_entries.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_baseline_ssblock_entries", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_baseline_ssblock_entry_contract() -> None:
    summary = load_checker().run_checks()
    assert summary["status"] == "pass", summary["failures"]
    assert summary["package_registration"]["ok"] is True
    assert all(item["ok"] for item in summary["graphical_classes"].values())
    assert all(item["ok"] for item in summary["runners"].values())
