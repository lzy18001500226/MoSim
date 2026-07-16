#!/usr/bin/env python3
"""Validate that the expanded controller goal has no omitted or duplicate item."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "control_platform" / "extended_control_scope_catalog.json"
REQUIRED_FAMILIES = {
    "pid",
    "linear_robust",
    "sliding_mode",
    "mpc",
    "disturbance_and_learning",
    "safety",
    "fault_tolerance",
    "formation",
}
REQUIRED_LAYERS = {
    "nominal_controller",
    "augmentation",
    "safety_and_supervision",
    "fault_management_and_allocation",
    "formation_controller",
}


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "mosim.control_platform.extended_scope_catalog.v1":
        errors.append("unsupported schema")
    if not isinstance(data.get("evidence_gates"), list) or len(data["evidence_gates"]) < 7:
        errors.append("evidence_gates must contain the complete seven-gate contract")
    if not isinstance(data.get("shared_contracts"), list) or "FaultEvent" not in data["shared_contracts"]:
        errors.append("shared_contracts must include FaultEvent")

    families = data.get("families")
    if not isinstance(families, list):
        return errors + ["families must be a list"]
    seen_families: set[str] = set()
    seen_algorithms: set[str] = set()
    for index, family in enumerate(families):
        if not isinstance(family, dict):
            errors.append(f"families[{index}] must be an object")
            continue
        family_id = family.get("family_id")
        if not isinstance(family_id, str) or not family_id:
            errors.append(f"families[{index}] missing family_id")
            continue
        if family_id in seen_families:
            errors.append(f"duplicate family_id: {family_id}")
        seen_families.add(family_id)
        if family.get("layer") not in REQUIRED_LAYERS:
            errors.append(f"{family_id} has unsupported layer: {family.get('layer')}")
        algorithms = family.get("required_algorithm_ids")
        if not isinstance(algorithms, list) or not algorithms:
            errors.append(f"{family_id} must declare required_algorithm_ids")
            continue
        for algorithm_id in algorithms:
            if not isinstance(algorithm_id, str) or not algorithm_id:
                errors.append(f"{family_id} contains an invalid algorithm id")
            elif algorithm_id in seen_algorithms:
                errors.append(f"duplicate algorithm id: {algorithm_id}")
            else:
                seen_algorithms.add(algorithm_id)
    missing_families = REQUIRED_FAMILIES - seen_families
    errors.extend(f"missing family: {family_id}" for family_id in sorted(missing_families))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors = validate(data)
    payload = {
        "ok": not errors,
        "catalog": str(args.catalog),
        "family_count": len(data.get("families", [])),
        "algorithm_count": sum(len(item.get("required_algorithm_ids", [])) for item in data.get("families", [])),
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
