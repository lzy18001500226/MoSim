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


def test_backend_owned_chain_is_registered() -> None:
    modules = {item["profile_id"]: item for item in load_registry()["modules"]}
    adapter = modules["mavros_attitude_thrust_v1"]
    inner = modules[adapter["backend_inner_profile"]]
    allocator = modules[adapter["backend_allocator_profile"]]

    assert inner["kind"] == "attitude_rate_inner"
    assert inner["backend_owned"] is True
    assert allocator["kind"] == "control_allocator"
    assert allocator["backend_owned"] is True
    assert inner["output_variant"] == allocator["input_variant"]


def test_adapter_backend_chain_mismatch_is_rejected() -> None:
    checker = load_checker()
    registry = load_registry()
    adapter = next(item for item in registry["modules"] if item["kind"] == "command_adapter")
    adapter["backend_allocator_profile"] = "missing_allocator_v1"
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-DRIFT-09" in codes
    assert "CMR-CHAIN-02" in codes


def test_selectable_controller_requires_matching_adapter() -> None:
    checker = load_checker()
    registry = load_registry()
    for module in registry["modules"]:
        if module.get("kind") == "command_adapter" and module.get("input_variant") == "BODY_RATE_THRUST":
            module["selectable"] = False
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-CHAIN-05" in codes


def test_catalog_section_rejects_wrong_module_kind() -> None:
    checker = load_checker()
    registry = load_registry()
    safety = next(item for item in registry["modules"] if item["kind"] == "safety_filter")
    safety["kind"] = "command_adapter"
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-MODULE-08" in codes


def test_selectable_controller_requires_matching_safety_filter() -> None:
    checker = load_checker()
    registry = load_registry()
    safety = next(item for item in registry["modules"] if item["kind"] == "safety_filter")
    safety["supported_variants"] = ["ATTITUDE_THRUST"]
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-CHAIN-06" in codes


def test_formation_controller_requires_multi_uav_reference_output() -> None:
    checker = load_checker()
    registry = load_registry()
    formation = next(item for item in registry["modules"] if item["kind"] == "formation_controller")
    formation["output_variant"] = "ATTITUDE_THRUST"
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-FORMATION-01" in codes


def test_fault_manager_contract_and_family_are_checked() -> None:
    checker = load_checker()
    registry = load_registry()
    fault = next(item for item in registry["modules"] if item["kind"] == "fault_manager")
    fault["input_variant"] = "ATTITUDE_THRUST"
    fault["family"] = "wrong_family"
    codes = {error["code"] for error in checker.validate(registry)}
    assert "CMR-FAULT-01" in codes
    assert "CMR-DRIFT-03" in codes
