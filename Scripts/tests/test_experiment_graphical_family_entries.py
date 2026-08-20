from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "mworks" / "check_experiment_graphical_family_entries.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_experiment_graphical_family_entries", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_all_implemented_family_entries_use_graphical_sos_routes() -> None:
    summary = load_checker().run_checks()
    assert summary["family_entry_count"] == 46
    assert summary["planned_included"] == ["pid_awff_linear_eso"]
    assert set(summary["app_policy"]["active_controller_ids"]) == {
        row["scheme_id"]
        for row in __import__("json").loads(
            (ROOT / "Config" / "control_platform" / "control_scheme_catalog.json").read_text(encoding="utf-8-sig")
        )["schemes"]
    }
    assert summary["status"] == "pass", summary["failures"]
