#!/usr/bin/env python3
"""Validate the finite MoSim top-level control-scheme catalog.

This is a static catalog gate. It freezes the report/APP-facing scheme count
without promoting any route to MWORKS, generated-C, Gazebo, PX4, or ROS1
runtime acceptance.
"""

from __future__ import annotations

import argparse
import json
import re
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

REQUIRED_SCHEMA = "mosim.control_scheme_catalog.v1"
FROZEN_SCHEME_COUNT = 49
EXPECTED_ENTRY_TYPE_COUNTS = {
    "competition_primary_route": 43,
    "engineering_baseline": 1,
    "fixed_integrated_scheme": 5,
}
MATRIX_EXCLUSIONS = {
    "anti_windup",
    "feedforward_profile",
    "pid_indi",
    "awff",
    "complete_adrc",
    "ilc",
    "l1_adaptive",
    "parameter_scheduling",
    "standardized_indi",
    "dfbc_dob_eso",
    "dfbc_dob_eso_disabled",
    "l1_awff_minimal",
    "so3_attitude",
    "safety_supervisor_family",
    "fdi_ftc_family",
    "consensus",
    "containment",
    "distributed_mpc_formation",
    "fault_tolerant_formation",
    "formation_cbf",
    "formation_reconfiguration",
    "formation_tracking",
    "leader_follower",
    "virtual_structure",
}
FIXED_SCHEME_SPECS = {
    "fixed_awff_pid": {
        "source_config": "Config/controllers/awff_pid/default.yaml",
        "source_controller_id": "awff_pid",
        "selection_state": "offline_evidence_available",
    },
    "fixed_awff_l1_residual": {
        "source_config": "Config/controllers/l1_residual_sysblock/default.yaml",
        "source_controller_id": "l1_residual_sysblock",
        "selection_state": "offline_evidence_available",
    },
    "fixed_awff_l1_indi": {
        "source_config": "Config/controllers/awff_indi_sysblock/default.yaml",
        "source_controller_id": "awff_indi_sysblock",
        "selection_state": "offline_evidence_available",
    },
    "fixed_linear_mpc_l1_indi": {
        "source_config": "Config/controllers/linear_mpc_sysblock/default.yaml",
        "source_controller_id": "linear_mpc_sysblock",
        "selection_state": "offline_evidence_available",
    },
    "fixed_qp_nmpc_l1_indi_cbf": {
        "source_config": "Config/controllers/nmpc_indi_l1/default.yaml",
        "source_controller_id": "nmpc_indi_l1",
        "selection_state": "visible_disabled",
    },
}
REQUIRED_RESEARCH_DOIS = {
    "10.1109/aucc.2013.6697298",
    "10.2514/1.g001490",
    "10.23919/ecc.2013.6669410",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def yaml_controller_id(path: Path) -> str:
    match = re.search(
        r"^controller_id:\s*([^\s#]+)",
        path.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    return match.group(1) if match else ""


def validate(catalog: dict[str, Any], matrix: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    if catalog.get("schema") != REQUIRED_SCHEMA or catalog.get("version") != 1:
        add("CSC-SCHEMA-01", "catalog must use mosim.control_scheme_catalog.v1 version 1")
    if catalog.get("frozen_at") != "2026-07-21" or not str(catalog.get("frozen_decision", "")).strip():
        add("CSC-FREEZE-01", "catalog must retain its freeze date and non-empty frozen decision")

    frozen_count = catalog.get("frozen_scheme_count")
    if not isinstance(frozen_count, int) or isinstance(frozen_count, bool) or frozen_count != FROZEN_SCHEME_COUNT:
        add("CSC-COUNT-01", f"frozen_scheme_count must equal {FROZEN_SCHEME_COUNT}")

    selection = catalog.get("selection_contract")
    if not isinstance(selection, dict):
        add("CSC-POLICY-01", "selection_contract must be an object")
    else:
        if selection.get("one_top_level_scheme_per_run") is not True:
            add("CSC-POLICY-02", "exactly one top-level scheme must be selected per run")
        if selection.get("generic_augmentation_selector") != "not_exposed_in_standard_ui":
            add("CSC-POLICY-03", "standard UI must not expose generic augmentation multi-selection")
        if selection.get("mpc_role") != "MPC/NMPC is a nominal optimization outer-loop family, not a generic augmentation.":
            add("CSC-POLICY-04", "MPC/NMPC must remain a nominal optimization family")

    schemes = catalog.get("schemes")
    if not isinstance(schemes, list):
        add("CSC-SCHEMES-01", "schemes must be a list")
        return errors
    if len(schemes) != FROZEN_SCHEME_COUNT:
        add("CSC-COUNT-02", f"schemes must contain exactly {FROZEN_SCHEME_COUNT} entries")

    by_id: dict[str, dict[str, Any]] = {}
    by_type: dict[str, list[dict[str, Any]]] = {}
    for index, scheme in enumerate(schemes):
        if not isinstance(scheme, dict):
            add("CSC-SCHEMES-02", f"schemes[{index}] must be an object")
            continue
        scheme_id = str(scheme.get("scheme_id", ""))
        entry_type = str(scheme.get("entry_type", ""))
        if not scheme_id or scheme_id in by_id:
            add("CSC-ID-01", f"schemes[{index}] has a missing or duplicate scheme_id: {scheme_id}")
        else:
            by_id[scheme_id] = scheme
        if entry_type not in EXPECTED_ENTRY_TYPE_COUNTS:
            add("CSC-TYPE-01", f"{scheme_id} has unsupported entry_type: {entry_type}")
        else:
            by_type.setdefault(entry_type, []).append(scheme)

    for entry_type, expected_count in EXPECTED_ENTRY_TYPE_COUNTS.items():
        actual_count = len(by_type.get(entry_type, []))
        if actual_count != expected_count:
            add("CSC-TYPE-02", f"{entry_type} count must equal {expected_count}, got {actual_count}")

    summary = catalog.get("count_summary")
    expected_summary = {
        "competition_primary_routes": 43,
        "engineering_baseline": 1,
        "fixed_integrated_schemes": 5,
        "total": FROZEN_SCHEME_COUNT,
    }
    if not isinstance(summary, dict) or any(summary.get(key) != value for key, value in expected_summary.items()):
        add("CSC-COUNT-03", f"count_summary must equal {expected_summary}")

    research = catalog.get("research_basis")
    doi_values = (
        {str(item.get("doi", "")).lower() for item in research if isinstance(item, dict)}
        if isinstance(research, list)
        else set()
    )
    if doi_values != REQUIRED_RESEARCH_DOIS:
        add("CSC-RESEARCH-01", "research_basis DOI set does not match the frozen architecture basis")

    matrix_rows = matrix.get("rows")
    if not isinstance(matrix_rows, list):
        add("CSC-MATRIX-01", "controller evidence matrix rows must be a list")
        return errors
    matrix_ids = [str(row.get("controller", "")) for row in matrix_rows if isinstance(row, dict)]
    matrix_id_set = set(matrix_ids)
    if len(matrix_rows) != 67 or len(matrix_ids) != len(matrix_rows) or len(matrix_id_set) != len(matrix_ids):
        add("CSC-MATRIX-02", "controller evidence matrix must retain 67 unique controller rows")
    missing_exclusions = sorted(MATRIX_EXCLUSIONS - matrix_id_set)
    if missing_exclusions:
        add("CSC-MATRIX-03", f"matrix is missing frozen non-scheme rows: {missing_exclusions}")
    expected_primary_ids = matrix_id_set - MATRIX_EXCLUSIONS
    if len(expected_primary_ids) != EXPECTED_ENTRY_TYPE_COUNTS["competition_primary_route"]:
        add("CSC-MATRIX-04", "matrix exclusions must leave exactly 43 primary routes")

    primary_entries = by_type.get("competition_primary_route", [])
    primary_ids = [str(item.get("evidence_matrix_controller", "")) for item in primary_entries]
    if any(not item for item in primary_ids) or len(primary_ids) != len(set(primary_ids)):
        add("CSC-PRIMARY-01", "primary entries require unique evidence_matrix_controller values")
    if set(primary_ids) != expected_primary_ids:
        missing = sorted(expected_primary_ids - set(primary_ids))
        extra = sorted(set(primary_ids) - expected_primary_ids)
        add("CSC-PRIMARY-02", f"primary scheme matrix mapping mismatch; missing={missing}, extra={extra}")
    for entry_type, entries in by_type.items():
        if entry_type == "competition_primary_route":
            continue
        for entry in entries:
            if "evidence_matrix_controller" in entry:
                add("CSC-PRIMARY-03", f"{entry.get('scheme_id')} must not alias a primary matrix route")

    baseline_entries = by_type.get("engineering_baseline", [])
    if len(baseline_entries) == 1:
        baseline = baseline_entries[0]
        if baseline.get("scheme_id") != "px4ctrl" or baseline.get("registry_module_id") != "px4ctrl":
            add("CSC-PX4CTRL-01", "engineering baseline must be the registered px4ctrl module")
        registry_modules = registry.get("modules") if isinstance(registry.get("modules"), list) else []
        px4ctrl_module = next(
            (item for item in registry_modules if isinstance(item, dict) and item.get("module_id") == "px4ctrl"),
            None,
        )
        if not isinstance(px4ctrl_module, dict) or px4ctrl_module.get("kind") != "nominal_controller" or px4ctrl_module.get("family") != "px4ctrl":
            add("CSC-PX4CTRL-02", "registry must retain px4ctrl as a nominal-controller engineering baseline")

    fixed_entries = {str(item.get("scheme_id", "")): item for item in by_type.get("fixed_integrated_scheme", [])}
    if set(fixed_entries) != set(FIXED_SCHEME_SPECS):
        missing = sorted(set(FIXED_SCHEME_SPECS) - set(fixed_entries))
        extra = sorted(set(fixed_entries) - set(FIXED_SCHEME_SPECS))
        add("CSC-FIXED-01", f"fixed scheme IDs mismatch; missing={missing}, extra={extra}")
    for scheme_id, expected in FIXED_SCHEME_SPECS.items():
        entry = fixed_entries.get(scheme_id)
        if not isinstance(entry, dict):
            continue
        for field, value in expected.items():
            if entry.get(field) != value:
                add("CSC-FIXED-02", f"{scheme_id} {field} must equal {value}")
        source_path = resolve(str(entry.get("source_config", "")))
        if not source_path.is_file():
            add("CSC-FIXED-03", f"{scheme_id} source config is missing: {source_path}")
        elif yaml_controller_id(source_path) != entry.get("source_controller_id"):
            add("CSC-FIXED-04", f"{scheme_id} source_controller_id does not match {source_path}")
        fixed_order = entry.get("fixed_order")
        if not isinstance(fixed_order, list) or len(fixed_order) < 2 or not all(isinstance(item, str) and item for item in fixed_order):
            add("CSC-FIXED-05", f"{scheme_id} must declare a non-trivial fixed_order")
        if not str(entry.get("deduplication_note", "")).strip():
            add("CSC-FIXED-06", f"{scheme_id} must state why it is not a generic augmentation stack")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output-json")
    args = parser.parse_args()
    try:
        catalog_path = resolve(args.catalog)
        matrix_path = resolve(args.matrix)
        registry_path = resolve(args.registry)
        errors = validate(load_json(catalog_path), load_json(matrix_path), load_json(registry_path))
    except Exception as exc:
        errors = [{"code": "CSC-READ-01", "message": str(exc)}]
    report = {
        "ok": not errors,
        "catalog": str(resolve(args.catalog)),
        "matrix": str(resolve(args.matrix)),
        "registry": str(resolve(args.registry)),
        "frozen_scheme_count": FROZEN_SCHEME_COUNT,
        "error_count": len(errors),
        "errors": errors,
    }
    if args.output_json:
        output = resolve(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
