from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_extended_control_scope.py"
CATALOG = ROOT / "Config" / "control_platform" / "extended_control_scope_catalog.json"


def checker_module():
    spec = importlib.util.spec_from_file_location("extended_scope_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_expanded_scope_catalog_is_complete() -> None:
    data = catalog()
    errors = checker_module().validate(data)
    assert errors == []
    assert sum(len(item["required_algorithm_ids"]) for item in data["families"]) == 58


def test_duplicate_algorithm_is_rejected() -> None:
    data = catalog()
    data["families"][1]["required_algorithm_ids"].append("cascade_pid")
    errors = checker_module().validate(data)
    assert any("duplicate algorithm id: cascade_pid" in error for error in errors)
