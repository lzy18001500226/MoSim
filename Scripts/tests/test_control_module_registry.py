from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_control_module_registry.py"
REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_control_module_registry", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_current_registry_matches_profile_catalog() -> None:
    checker = load_checker()
    assert checker.validate(load_registry()) == []


def test_l1_awff_is_typed_but_not_runtime_selectable() -> None:
    module = next(
        item for item in load_registry()["modules"]
        if item["module_id"] == "l1_awff_minimal"
    )
    assert module["kind"] == "augmentation"
    assert module["status"] == "implemented"
    assert module["output_variant"] == "ATTITUDE_THRUST"
    assert module["selectable"] is False
    assert "not_formal_l1_or_runtime_selectable" in module["claim_ceiling"]


def test_blocked_module_cannot_be_selectable() -> None:
    checker = load_checker()
    registry = load_registry()
    module = next(item for item in registry["modules"] if item["status"] == "blocked")
    module["selectable"] = True
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-SELECT-02" in codes


def test_catalog_status_drift_is_rejected() -> None:
    checker = load_checker()
    registry = load_registry()
    registry["modules"][0]["status"] = "implemented"
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-DRIFT-01" in codes


def test_missing_command_variant_is_rejected() -> None:
    checker = load_checker()
    registry = load_registry()
    registry["command_variants"].remove("WRENCH")
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-CMD-01" in codes
