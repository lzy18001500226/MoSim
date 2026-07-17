from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/audit_classic_controller_coverage.py"
SPEC = importlib.util.spec_from_file_location("classic_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def complete_registry_and_matrix() -> tuple[dict, dict]:
    modules = []
    rows = []
    for item in MODULE.CANONICAL_CONTROLLERS:
        modules.append(
            {
                "module_id": item.module_id,
                "family": item.family,
                "kind": item.expected_kind,
                "status": "blocked",
                "selectable": False,
                "claim_ceiling": "test",
            }
        )
        rows.append({"controller": item.module_id, "status": "not_run"})
    return {"modules": modules}, {"rows": rows}


def test_complete_canonical_inventory_passes() -> None:
    registry, matrix = complete_registry_and_matrix()
    report = MODULE.build_audit(registry, matrix)
    assert report["status"] == "passed"
    assert report["counts"]["canonical"] == 22


def test_missing_new_controller_and_duplicate_are_reported() -> None:
    registry, matrix = complete_registry_and_matrix()
    registry["modules"] = [
        module for module in registry["modules"] if module["module_id"] != "mrac"
    ]
    matrix["rows"].append({"controller": "lqr_baseline", "status": "not_run"})
    report = MODULE.build_audit(registry, matrix)
    codes = {(item["code"], item["module_id"]) for item in report["findings"]}
    assert ("missing_registry", "mrac") in codes
    assert ("duplicate_matrix_id", "lqr_baseline") in codes
    assert report["status"] == "blocked"
