#!/usr/bin/env python3
"""Fail-closed validation for the Model Studio offline expansion inventory."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = ROOT / "Config/control_platform/offline_expansion_inventory.json"
EXPECTED_BASELINE = "7384e2161d0704c7e2dc022f359b74154c6d4ab9"
EXPECTED_COUNT = 77
VALID_MATURITY = {"accepted", "implemented", "blocked"}
VALID_PROFILE_STATES = {
    "EXISTING_CERTIFIED_PROFILE",
    "DEFAULT_PROFILE_REQUIRED",
    "FORBIDDEN_UNTIL_VERSIONED_UNBLOCK",
}


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    modules = data.get("modules")
    if data.get("schema") != "mosim.offline_expansion_inventory.v1":
        errors.append("schema must be mosim.offline_expansion_inventory.v1")
    if data.get("baseline_commit") != EXPECTED_BASELINE:
        errors.append("baseline_commit does not match the frozen competition baseline")
    if not isinstance(modules, list):
        return errors + ["modules must be a list"]
    if len(modules) != EXPECTED_COUNT:
        errors.append(f"expected {EXPECTED_COUNT} modules, found {len(modules)}")
    if data.get("baseline_module_count") != len(modules):
        errors.append("baseline_module_count does not match modules length")

    ids = [module.get("module_id") for module in modules]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate module_id values: {duplicates}")

    allowed_boundaries = set(data.get("allowed_native_output_boundaries", []))
    allowed_batches = set(data.get("batch_order", []))
    required_fields = {
        "module_id",
        "profile_id",
        "layer",
        "family",
        "native_output_boundary",
        "baseline_maturity",
        "mworks_model_state",
        "graphical_model_state",
        "offline_adapter_state",
        "codegen_state",
        "offline_simulation_state",
        "competition_value",
        "expansion_batch",
        "legal_default_profile_state",
        "claim_ceiling",
        "baseline_evidence",
    }
    for index, module in enumerate(modules):
        label = module.get("module_id") or f"index {index}"
        missing = sorted(required_fields - set(module))
        if missing:
            errors.append(f"{label}: missing fields {missing}")
        if module.get("native_output_boundary") not in allowed_boundaries:
            errors.append(f"{label}: invalid native_output_boundary")
        if module.get("baseline_maturity") not in VALID_MATURITY:
            errors.append(f"{label}: invalid baseline_maturity")
        if module.get("expansion_batch") not in allowed_batches:
            errors.append(f"{label}: invalid expansion_batch")
        if module.get("legal_default_profile_state") not in VALID_PROFILE_STATES:
            errors.append(f"{label}: invalid legal_default_profile_state")
        if (
            module.get("baseline_maturity") == "blocked"
            and module.get("legal_default_profile_state")
            != "FORBIDDEN_UNTIL_VERSIONED_UNBLOCK"
        ):
            errors.append(f"{label}: blocked module is allowed in a default Profile")
        if (
            module.get("legal_default_profile_state")
            == "FORBIDDEN_UNTIL_VERSIONED_UNBLOCK"
            and module.get("baseline_selectable")
        ):
            errors.append(f"{label}: blocked default Profile module is selectable")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", nargs="?", type=Path, default=DEFAULT_INVENTORY)
    args = parser.parse_args()
    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"offline expansion inventory passed: {len(data['modules'])} modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
