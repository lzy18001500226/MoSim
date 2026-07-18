#!/usr/bin/env python3
"""Build the offline-expansion inventory from the frozen Git baseline."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASELINE_COMMIT = "7384e2161d0704c7e2dc022f359b74154c6d4ab9"
REGISTRY_PATH = "Config/control_platform/control_module_registry.json"
CATALOG_PATH = "Config/control_platform/offline_composition_catalog.json"
OUTPUT_PATH = ROOT / "Config/control_platform/offline_expansion_inventory.json"

PLATFORM_KINDS = {"command_adapter", "attitude_rate_inner", "control_allocator"}

BATCH_A_IDS = {
    "px4ctrl", "official_pid", "cascade_pid", "gain_scheduled_pid",
    "fuzzy_pid", "neural_pid", "pid_indi", "anti_windup",
    "feedforward_profile", "l1_awff_minimal", "l1_adaptive", "awff",
    "complete_adrc", "standardized_indi", "parameter_scheduling", "ilc",
}

BATCH_C_IDS = {"trained_neural_residual", "rl_gain_scheduler"}


def git_json(path: str) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "show", f"{BASELINE_COMMIT}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def expansion_batch(module: dict[str, Any]) -> str:
    module_id = module["module_id"]
    kind = module["kind"]
    if kind in PLATFORM_KINDS:
        return "P2_PLATFORM_CORE"
    if kind == "formation_controller":
        return "P6_BATCH_D_FORMATION"
    if kind in {"safety_filter", "fault_manager"} or module_id in BATCH_C_IDS:
        return "P5_BATCH_C_INTELLIGENT_SAFETY_FTC"
    if module_id in BATCH_A_IDS:
        return "P3_BATCH_A_MATURE_HIGH_VALUE"
    return "P4_BATCH_B_CLASSIC_ROBUST_MPC_SMC"


def competition_value(module: dict[str, Any]) -> str:
    if module["module_id"] in BATCH_A_IDS:
        return "P0_CORE_STORY"
    if module["kind"] in {"fault_manager", "safety_filter"}:
        return "P0_COMPETITION_DIFFERENTIATOR"
    if module["kind"] == "formation_controller":
        return "P1_MULTI_UAV_STORY"
    if module["module_id"] in BATCH_C_IDS:
        return "P1_INTELLIGENT_CONTROL_STORY"
    if module["kind"] in PLATFORM_KINDS:
        return "P0_PLATFORM_DEPENDENCY"
    return "P2_FAMILY_COVERAGE"


def evidence_paths(module: dict[str, Any]) -> list[str]:
    keys = (
        "latest_offline_evidence",
        "latest_runtime_evidence",
        "latest_static_evidence",
        "latest_provenance_evidence",
    )
    return [module[key] for key in keys if module.get(key)]


def codegen_state(module: dict[str, Any]) -> str:
    claim = module.get("claim_ceiling", "").lower()
    if "generated_c" in claim or "codegen" in claim:
        return "EVIDENCE_RECORDED_IN_REGISTRY"
    return "REQUIRES_AUDIT"


def build_inventory() -> dict[str, Any]:
    registry = git_json(REGISTRY_PATH)
    catalog = git_json(CATALOG_PATH)
    catalog_modules = catalog.get("modules", {})
    certified_ids = {
        profile["controller_id"]
        for profile in catalog.get("certified_profiles", [])
        if profile.get("certification_state") == "accepted"
    }

    entries = []
    for module in registry["modules"]:
        module_id = module["module_id"]
        status = module["status"]
        adapter = catalog_modules.get(module_id)
        if status == "blocked":
            legal_profile_state = "FORBIDDEN_UNTIL_VERSIONED_UNBLOCK"
        elif module_id in certified_ids:
            legal_profile_state = "EXISTING_CERTIFIED_PROFILE"
        else:
            legal_profile_state = "DEFAULT_PROFILE_REQUIRED"

        entries.append(
            {
                "module_id": module_id,
                "profile_id": module["profile_id"],
                "layer": module["kind"],
                "family": module["family"],
                "native_output_boundary": module.get("output_variant")
                or "BOUNDARY_AGNOSTIC",
                "baseline_maturity": status,
                "baseline_selectable": bool(module.get("selectable", False)),
                "source_implementation_state": (
                    "BLOCKED_CAPABILITY_OR_IMPLEMENTATION"
                    if status == "blocked"
                    else "SOURCE_RECORDED_IN_BASELINE_REGISTRY"
                ),
                "mworks_model_state": (
                    "EXISTING_OFFLINE_ADAPTER"
                    if adapter and adapter.get("adapter_model")
                    else "REQUIRES_MODEL_AUDIT"
                ),
                "graphical_model_state": (
                    "SHARED_RUNNER_INTEGRATED"
                    if module_id in certified_ids
                    else "REQUIRES_GRAPHICAL_AUDIT"
                ),
                "offline_adapter_state": (
                    "EXISTING"
                    if adapter and adapter.get("adapter_model")
                    else "REQUIRED"
                ),
                "codegen_state": codegen_state(module),
                "offline_simulation_state": (
                    "CERTIFIED_BASELINE"
                    if module_id in certified_ids
                    else "NOT_CERTIFIED_BY_EXPANSION_GOAL"
                ),
                "competition_value": competition_value(module),
                "expansion_batch": expansion_batch(module),
                "legal_default_profile_state": legal_profile_state,
                "claim_ceiling": module.get("claim_ceiling", "unclassified"),
                "baseline_evidence": evidence_paths(module),
                "blocking_reason": (
                    module.get("decision") or module.get("claim_ceiling")
                    if status == "blocked"
                    else None
                ),
            }
        )

    return {
        "schema": "mosim.offline_expansion_inventory.v1",
        "version": 1,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_registry": REGISTRY_PATH,
        "baseline_module_count": len(entries),
        "claim_boundary": (
            "Planning inventory only. Existing evidence is retained at its recorded "
            "claim ceiling and does not certify a module under this expansion Goal."
        ),
        "allowed_native_output_boundaries": [
            "ATTITUDE_THRUST",
            "BODY_RATE_THRUST",
            "WRENCH",
            "ROTOR_COMMAND",
            "MULTI_UAV_REFERENCE",
            "FAULT_EVENT",
            "ROTOR_COMMAND_AND_LAND_ACTION",
            "BOUNDARY_AGNOSTIC",
        ],
        "batch_order": [
            "P2_PLATFORM_CORE",
            "P3_BATCH_A_MATURE_HIGH_VALUE",
            "P4_BATCH_B_CLASSIC_ROBUST_MPC_SMC",
            "P5_BATCH_C_INTELLIGENT_SAFETY_FTC",
            "P6_BATCH_D_FORMATION",
        ],
        "modules": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    expected = json.dumps(build_inventory(), indent=2, ensure_ascii=True) + "\n"
    output = args.output.resolve()
    if args.check:
        if not output.exists() or output.read_bytes() != expected.encode("utf-8"):
            print(f"stale inventory: {output}")
            return 1
        print(f"inventory is reproducible: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8", newline="\n")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
