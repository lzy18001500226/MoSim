#!/usr/bin/env python3
"""Build the G1 fail-closed inventory for MoSim's 49 top-level schemes.

The output is an audit artifact.  It deliberately records source candidates,
not a newly approved MWORKS model entry, until G4 maps every runnable scheme
into the restructured model library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
DEFAULT_MATRIX = (
    ROOT
    / "Results"
    / "control_platform"
    / "classic_controller_closeout_20260717"
    / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
)
DEFAULT_REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"
DEFAULT_DOCUMENT_INVENTORY = (
    ROOT
    / "Results"
    / "control_platform"
    / "controller_document_evidence_20260720"
    / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.json"
)
DEFAULT_MODEL_CATALOG = ROOT / "Config" / "control_platform" / "model_operation_catalog.json"
DEFAULT_COMPOSITION_CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "control_platform"
    / "g1_control_scheme_execution_inventory_20260722"
    / "CONTROL_SCHEME_EXECUTION_INVENTORY.json"
)

NOMINAL_SCREENING_SCENARIOS = ["hover", "step", "figure8", "spiral"]
FULL_SCENARIOS = NOMINAL_SCREENING_SCENARIOS + [
    "wind",
    "parameter_mismatch",
    "motor_efficiency_fault",
]


def write_utf8_lf(path: Path, text: str) -> None:
    """Write generated artifacts with LF regardless of the host platform."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def sha256_json(value: Any) -> str:
    """Match the checker hash for parsed JSON authority sources."""
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def as_strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def yaml_values(path: Path, key: str) -> list[str]:
    if not path.is_file():
        return []
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*([^#\r\n]+)", re.MULTILINE)
    return [match.group(1).strip().strip("\"'") for match in pattern.finditer(path.read_text(encoding="utf-8"))]


def add_blocker(blockers: list[str], value: str | None) -> None:
    if value and value not in blockers:
        blockers.append(value)


def registry_binding(module: dict[str, Any] | None, runners: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(module, dict):
        return {
            "mapping_state": "no_exact_registry_binding",
            "module_id": None,
            "profile_id": None,
            "status": None,
            "output_variant": None,
            "offline_runner": None,
            "offline_inner_owner": None,
        }
    variant = str(module.get("output_variant", "")) or None
    runner = runners.get(variant) if variant else None
    return {
        "mapping_state": "exact_registry_binding",
        "module_id": module.get("module_id"),
        "profile_id": module.get("profile_id"),
        "status": module.get("status"),
        "output_variant": variant,
        "offline_runner": runner.get("model") if isinstance(runner, dict) else None,
        "offline_inner_owner": runner.get("offline_inner_owner") if isinstance(runner, dict) else None,
    }


def model_catalog_bindings(model_catalog: dict[str, Any], controller_id: str) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for profile in model_catalog.get("model_profiles", []):
        if not isinstance(profile, dict) or controller_id not in as_strings(profile.get("controller_ids")):
            continue
        run_mil = profile.get("run_mil") if isinstance(profile.get("run_mil"), dict) else {}
        bindings.append(
            {
                "model_profile_id": profile.get("model_profile_id"),
                "model_file": run_mil.get("model_file"),
                "model_name": run_mil.get("model_name"),
                "status": profile.get("status"),
            }
        )
    return bindings


def primary_entry(
    scheme: dict[str, Any],
    matrix_row: dict[str, Any],
    document_row: dict[str, Any],
    module: dict[str, Any] | None,
    model_catalog: dict[str, Any],
    runners: dict[str, Any],
) -> dict[str, Any]:
    controller = str(scheme["evidence_matrix_controller"])
    model_sources = as_strings(document_row.get("model_sources"))
    missing_evidence = as_strings(document_row.get("missing_evidence"))
    implementation_blocked = bool(document_row.get("implementation_blocked"))
    blockers: list[str] = []
    add_blocker(blockers, str(matrix_row.get("first_blocker") or "") or None)
    for item in missing_evidence:
        add_blocker(blockers, f"missing_evidence:{item}")
    if implementation_blocked:
        add_blocker(blockers, "implementation_blocked")
    binding = registry_binding(module, runners)
    if binding["mapping_state"] != "exact_registry_binding":
        add_blocker(blockers, "no_exact_registry_binding")
    if implementation_blocked:
        model_state = "implementation_blocked"
    elif not model_sources:
        model_state = "source_model_missing"
        add_blocker(blockers, "source_model_missing")
    else:
        model_state = "source_candidates_need_g4_mapping"
        add_blocker(blockers, "current_model_entry_unmapped")

    return {
        "scheme_id": scheme["scheme_id"],
        "display_name_zh": scheme.get("display_name_zh"),
        "category": scheme.get("category"),
        "entry_type": scheme["entry_type"],
        "control_owner": "nominal_controller",
        "evidence_route": controller,
        "registry_binding": binding,
        "model_entry": {
            "mapping_state": model_state,
            "current_model_file": None,
            "current_model_name": None,
            "source_model_candidates": model_sources,
            "existing_model_operation_candidates": model_catalog_bindings(model_catalog, controller),
        },
        "scenario_contract": {
            "g5_nominal_screening": {
                "scenario_ids": NOMINAL_SCREENING_SCENARIOS,
                "eligibility": "blocked_until_g4_current_model_mapping",
            },
            "g6_family_champion": {
                "scenario_ids": FULL_SCENARIOS,
                "eligibility": "not_selected_until_g5_screening",
            },
        },
        "current_evidence": {
            "matrix_status": matrix_row.get("status"),
            "implementation_state": matrix_row.get("implementation_state"),
            "claim_ceiling": matrix_row.get("claim_ceiling"),
            "document_inventory_next_action": document_row.get("next_action"),
            "model_source_count": len(model_sources),
            "result_viewer_screenshot_count": len(as_strings(document_row.get("result_viewer_screenshots"))),
            "numeric_result_count": len(as_strings(document_row.get("numeric_results_or_metrics"))),
            "native_result_msr_count": len(as_strings(document_row.get("native_result_msr"))),
            "evidence_paths": as_strings(matrix_row.get("evidence_paths")),
        },
        "blockers": blockers,
        "mworks_run_eligible": False,
        "next_gate": "G4 model mapping, then G5 CheckModel and minimum MIL",
    }


def px4ctrl_entry(scheme: dict[str, Any], module: dict[str, Any] | None, runners: dict[str, Any]) -> dict[str, Any]:
    binding = registry_binding(module, runners)
    return {
        "scheme_id": scheme["scheme_id"],
        "display_name_zh": scheme.get("display_name_zh"),
        "category": scheme.get("category"),
        "entry_type": scheme["entry_type"],
        "control_owner": "nominal_controller_runtime_baseline",
        "evidence_route": None,
        "registry_binding": binding,
        "model_entry": {
            "mapping_state": "not_applicable_runtime_baseline",
            "current_model_file": None,
            "current_model_name": None,
            "source_model_candidates": [],
            "existing_model_operation_candidates": [],
        },
        "scenario_contract": {
            "g5_nominal_screening": {
                "scenario_ids": [],
                "eligibility": "not_applicable_px4ctrl_is_not_an_mworks_graphical_scheme",
            },
            "g6_family_champion": {
                "scenario_ids": FULL_SCENARIOS,
                "eligibility": "runtime_baseline_only_after_this_goal",
            },
        },
        "current_evidence": {
            "matrix_status": None,
            "implementation_state": binding.get("status"),
            "claim_ceiling": module.get("claim_ceiling") if isinstance(module, dict) else None,
            "evidence_paths": [],
        },
        "blockers": ["out_of_scope_runtime_baseline_until_post_G7_deployment"],
        "mworks_run_eligible": False,
        "next_gate": "Post-G7 ROS1/Sunray/Gazebo/PX4 baseline verification",
    }


def fixed_entry(scheme: dict[str, Any], composition: dict[str, Any]) -> dict[str, Any]:
    source_config = str(scheme.get("source_config", ""))
    config_path = ROOT / source_config
    declared_models = yaml_values(config_path, "model_name")
    controller_id = str(scheme.get("source_controller_id", ""))
    composition_module = composition.get("modules", {}).get(controller_id)
    blockers = ["current_model_entry_unmapped"]
    if not config_path.is_file():
        blockers.insert(0, "fixed_chain_source_config_missing")
    return {
        "scheme_id": scheme["scheme_id"],
        "display_name_zh": scheme.get("display_name_zh"),
        "category": scheme.get("category"),
        "entry_type": scheme["entry_type"],
        "control_owner": "fixed_integrated_chain",
        "evidence_route": None,
        "registry_binding": {
            "mapping_state": "fixed_chain_source_config",
            "module_id": controller_id,
            "profile_id": None,
            "status": scheme.get("selection_state"),
            "output_variant": None,
            "offline_runner": None,
            "offline_inner_owner": None,
        },
        "model_entry": {
            "mapping_state": "source_config_candidates_need_g4_mapping",
            "current_model_file": None,
            "current_model_name": None,
            "source_model_candidates": [],
            "source_config": source_config,
            "source_config_exists": config_path.is_file(),
            "declared_model_names": declared_models,
            "offline_composition_binding": composition_module if isinstance(composition_module, dict) else None,
        },
        "fixed_order": as_strings(scheme.get("fixed_order")),
        "scenario_contract": {
            "g5_nominal_screening": {
                "scenario_ids": NOMINAL_SCREENING_SCENARIOS,
                "eligibility": "blocked_until_g4_current_model_mapping",
            },
            "g6_family_champion": {
                "scenario_ids": FULL_SCENARIOS,
                "eligibility": "not_automatically_in_six_nominal_family_champions",
            },
        },
        "current_evidence": {
            "matrix_status": None,
            "implementation_state": scheme.get("selection_state"),
            "claim_ceiling": "offline_chain_claim_only_until_g5_evidence",
            "evidence_paths": [source_config],
        },
        "blockers": blockers,
        "mworks_run_eligible": False,
        "next_gate": "G4 fixed-chain source-to-current-model mapping, then G5 CheckModel and minimum MIL",
    }


def build_inventory(
    catalog_path: Path = DEFAULT_CATALOG,
    matrix_path: Path = DEFAULT_MATRIX,
    registry_path: Path = DEFAULT_REGISTRY,
    document_inventory_path: Path = DEFAULT_DOCUMENT_INVENTORY,
    model_catalog_path: Path = DEFAULT_MODEL_CATALOG,
    composition_catalog_path: Path = DEFAULT_COMPOSITION_CATALOG,
) -> dict[str, Any]:
    catalog = load_json(catalog_path)
    matrix = load_json(matrix_path)
    registry = load_json(registry_path)
    document_inventory = load_json(document_inventory_path)
    model_catalog = load_json(model_catalog_path)
    composition = load_json(composition_catalog_path)
    matrix_by_controller = {
        str(row.get("controller")): row
        for row in matrix.get("rows", [])
        if isinstance(row, dict) and row.get("controller")
    }
    inventory_by_controller = {
        str(row.get("controller")): row
        for row in document_inventory.get("rows", [])
        if isinstance(row, dict) and row.get("controller")
    }
    registry_by_module = {
        str(module.get("module_id")): module
        for module in registry.get("modules", [])
        if isinstance(module, dict) and module.get("module_id")
    }
    runners = composition.get("runners") if isinstance(composition.get("runners"), dict) else {}
    entries: list[dict[str, Any]] = []
    for scheme in catalog.get("schemes", []):
        if not isinstance(scheme, dict):
            continue
        entry_type = str(scheme.get("entry_type"))
        scheme_id = str(scheme.get("scheme_id"))
        if entry_type == "competition_primary_route":
            controller = str(scheme.get("evidence_matrix_controller"))
            matrix_row = matrix_by_controller.get(controller)
            document_row = inventory_by_controller.get(controller)
            if not isinstance(matrix_row, dict) or not isinstance(document_row, dict):
                raise ValueError(f"primary scheme lacks authority rows: {scheme_id}")
            entries.append(primary_entry(scheme, matrix_row, document_row, registry_by_module.get(scheme_id), model_catalog, runners))
        elif entry_type == "engineering_baseline":
            entries.append(px4ctrl_entry(scheme, registry_by_module.get(scheme_id), runners))
        elif entry_type == "fixed_integrated_scheme":
            entries.append(fixed_entry(scheme, composition))
        else:
            raise ValueError(f"unsupported scheme entry_type: {entry_type}")

    type_counts = Counter(str(entry["entry_type"]) for entry in entries)
    category_counts = Counter(str(entry["category"]) for entry in entries)
    matrix_status_counts = Counter(
        str(entry["current_evidence"]["matrix_status"])
        for entry in entries
        if entry["current_evidence"].get("matrix_status")
    )
    input_paths = {
        "control_scheme_catalog": catalog_path,
        "classic_controller_final_matrix": matrix_path,
        "control_module_registry": registry_path,
        "controller_document_evidence_inventory": document_inventory_path,
        "model_operation_catalog": model_catalog_path,
        "offline_composition_catalog": composition_catalog_path,
    }
    return {
        "schema": "mosim.control_scheme_execution_inventory.v1",
        "version": 1,
        "scope": "G1 audit only. This inventory does not authorize MWORKS, code generation, or runtime execution.",
        "source_files": {key: repo_path(path) for key, path in input_paths.items()},
        "source_sha256": {
            "control_scheme_catalog": sha256_json(catalog),
            "classic_controller_final_matrix": sha256_json(matrix),
            "control_module_registry": sha256_json(registry),
            "controller_document_evidence_inventory": sha256_json(document_inventory),
            "model_operation_catalog": sha256_json(model_catalog),
            "offline_composition_catalog": sha256_json(composition),
        },
        "summary": {
            "top_level_scheme_count": len(entries),
            "entry_type_counts": dict(sorted(type_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "matrix_status_counts_for_primary_routes": dict(sorted(matrix_status_counts.items())),
            "exact_registry_binding_count": sum(
                entry["registry_binding"]["mapping_state"] == "exact_registry_binding" for entry in entries
            ),
            "primary_source_model_present_count": sum(
                entry["entry_type"] == "competition_primary_route"
                and bool(entry["model_entry"]["source_model_candidates"])
                for entry in entries
            ),
            "current_mworks_model_mapping_ready_count": 0,
            "mworks_run_eligible_count": sum(bool(entry["mworks_run_eligible"]) for entry in entries),
        },
        "schemes": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--document-inventory", type=Path, default=DEFAULT_DOCUMENT_INVENTORY)
    parser.add_argument("--model-catalog", type=Path, default=DEFAULT_MODEL_CATALOG)
    parser.add_argument("--composition-catalog", type=Path, default=DEFAULT_COMPOSITION_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    inventory = build_inventory(
        args.catalog,
        args.matrix,
        args.registry,
        args.document_inventory,
        args.model_catalog,
        args.composition_catalog,
    )
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    write_utf8_lf(output, json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"ok": True, "output": str(output), "summary": inventory["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
