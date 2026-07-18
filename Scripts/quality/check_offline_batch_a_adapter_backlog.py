#!/usr/bin/env python3
"""Validate the frozen-baseline Batch A offline Adapter implementation queue."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BACKLOG_PATH = ROOT / "Config/control_platform/offline_batch_a_adapter_backlog.json"
INVENTORY_PATH = ROOT / "Config/control_platform/offline_expansion_inventory.json"
BATCH = "P3_BATCH_A_MATURE_HIGH_VALUE"
ALLOWED_STATES = {
    "EXTERNAL_RUNTIME_ONLY_REQUIRES_OFFLINE_MODEL",
    "EXISTING_LEGACY_BUNDLE_REQUIRES_NATIVE_ADAPTER",
    "MWORKS_CONTRACT_MODEL_AVAILABLE_ADAPTER_REQUIRED",
    "HISTORICAL_BUNDLE_MAPPING_BLOCKED",
}


def validate(backlog: dict[str, Any], inventory: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if backlog.get("schema") != "mosim.offline_batch_a_adapter_backlog.v1":
        errors.append("invalid_schema")
    if backlog.get("baseline_commit") != inventory.get("baseline_commit"):
        errors.append("baseline_commit_mismatch")
    expected = {
        module["module_id"]: module
        for module in inventory.get("modules", [])
        if module.get("expansion_batch") == BATCH
    }
    entries = backlog.get("entries", [])
    actual_ids = [entry.get("module_id") for entry in entries]
    if len(actual_ids) != len(set(actual_ids)):
        errors.append("duplicate_module_id")
    if set(actual_ids) != set(expected):
        errors.append("batch_a_module_coverage_mismatch")
    for entry in entries:
        module_id = entry.get("module_id")
        authority = expected.get(module_id)
        if authority is None:
            continue
        if entry.get("layer") != authority.get("layer"):
            errors.append(f"layer_mismatch:{module_id}")
        if authority.get("native_output_boundary") != "ATTITUDE_THRUST":
            errors.append(f"unexpected_native_boundary:{module_id}")
        if entry.get("adapter_state") not in ALLOWED_STATES:
            errors.append(f"invalid_adapter_state:{module_id}")
        source = entry.get("source_anchor")
        if not isinstance(source, str) or not (root / source).is_file():
            errors.append(f"source_anchor_missing:{module_id}")
        if not entry.get("next_gate"):
            errors.append(f"next_gate_missing:{module_id}")
        if module_id == "neural_pid" and "zero_untrained" not in entry.get("next_gate", ""):
            errors.append("neural_pid_claim_boundary_missing")
        if module_id == "ilc" and "reset_lifecycle" not in entry.get("next_gate", ""):
            errors.append("ilc_lifecycle_gate_missing")
    return errors


def main() -> int:
    backlog = json.loads(BACKLOG_PATH.read_text(encoding="utf-8-sig"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    errors = validate(backlog, inventory)
    print(json.dumps({"ok": not errors, "errors": errors, "entry_count": len(backlog.get("entries", []))}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
