from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_extended_control_coverage.py"


def checker_module():
    spec = importlib.util.spec_from_file_location("extended_coverage_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_coverage_report_tracks_every_required_algorithm() -> None:
    scope = json.loads((ROOT / "Config/control_platform/extended_control_scope_catalog.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "Config/control_platform/control_module_registry.json").read_text(encoding="utf-8"))
    report = checker_module().build_report(scope, registry)
    assert report["algorithm_count"] == 58
    assert report["registered_count"] == 6
    assert report["status_counts"] == {"interface_ready": 6, "unregistered": 52}
    assert report["selectable_count"] == 0
    assert report["complete"] is False
    assert len({item["algorithm_id"] for item in report["algorithms"]}) == 58


def test_coverage_does_not_inherit_from_similar_baseline() -> None:
    scope = {"families": [{"family_id": "pid", "required_algorithm_ids": ["neural_pid"]}]}
    registry = {"modules": [{"module_id": "official_pid", "status": "accepted", "selectable": True}]}
    report = checker_module().build_report(scope, registry)
    assert report["algorithms"][0]["status"] == "unregistered"
