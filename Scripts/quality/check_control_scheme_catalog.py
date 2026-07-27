#!/usr/bin/env python3
"""Validate the active MoSim control-profile catalog.

The catalog is an active terminology and selection contract.  Historical
67-route evidence remains provenance only and must not reintroduce retired
blockers or an eighth ``fixed_integrated`` controller family.
"""

from __future__ import annotations

import argparse
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

REQUIRED_SCHEMA = "mosim.control_profile_catalog.v2"
ACTIVE_ENTRY_COUNT = 48
MWORKS_PROFILE_COUNT = 47
CURRENT_MWORKS_ROUTE_COUNT = 46
CURRENT_GRAPHICAL_CORE_COUNT = 41
CURRENT_FULL_PROFILE_COUNT = 5
ARCHIVED_HISTORICAL_IDS = {"mu_synthesis", "neural_smc"}
FAMILY_SPECS = {
    "pid_family": {"target_profile_count": 10, "current_route_count": 9},
    "linear_robust_state_feedback": {"target_profile_count": 6, "current_route_count": 6},
    "nonlinear_adaptive": {"target_profile_count": 6, "current_route_count": 6},
    "sliding_mode": {"target_profile_count": 7, "current_route_count": 7},
    "optimization_predictive": {"target_profile_count": 10, "current_route_count": 10},
    "geometric_flatness": {"target_profile_count": 6, "current_route_count": 6},
    "learning": {"target_profile_count": 2, "current_route_count": 2},
}
FULL_PROFILE_SPECS = {
    "fixed_awff_pid": {
        "profile_id": "PidAwff",
        "category": "pid_family",
        "source_config": "Config/controllers/awff_pid/default.yaml",
        "source_controller_id": "awff_pid",
        "role": "candidate",
    },
    "fixed_awff_l1_residual": {
        "profile_id": "PidAwffL1Residual",
        "category": "pid_family",
        "source_config": "Config/controllers/l1_residual_sysblock/default.yaml",
        "source_controller_id": "l1_residual_sysblock",
        "role": "candidate",
    },
    "fixed_awff_l1_indi": {
        "profile_id": "PidAwffL1Indi",
        "category": "pid_family",
        "source_config": "Config/controllers/awff_indi_sysblock/default.yaml",
        "source_controller_id": "awff_indi_sysblock",
        "role": "candidate",
    },
    "fixed_linear_mpc_l1_indi": {
        "profile_id": "LinearMpcL1Indi",
        "category": "optimization_predictive",
        "source_config": "Config/controllers/linear_mpc_sysblock/default.yaml",
        "source_controller_id": "linear_mpc_sysblock",
        "role": "candidate",
    },
    "fixed_qp_nmpc_l1_indi_cbf": {
        "profile_id": "QpNmpcL1IndiCbf",
        "category": "optimization_predictive",
        "source_config": "Config/controllers/nmpc_indi_l1/default.yaml",
        "source_controller_id": "nmpc_indi_l1",
        "role": "candidate",
    },
}
PLANNED_PROFILE_ID = "pid_awff_linear_eso"
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

    if catalog.get("schema") != REQUIRED_SCHEMA or catalog.get("version") != 2:
        add("CSC-SCHEMA-01", "catalog must use mosim.control_profile_catalog.v2 version 2")
    if catalog.get("frozen_at") != "2026-07-27" or not str(catalog.get("frozen_decision", "")).strip():
        add("CSC-FREEZE-01", "catalog must retain the 2026-07-27 active taxonomy decision")
    if catalog.get("frozen_scheme_count") != ACTIVE_ENTRY_COUNT:
        add("CSC-COUNT-01", f"frozen_scheme_count must equal {ACTIVE_ENTRY_COUNT}")

    expected_summary = {
        "mworks_control_profiles": MWORKS_PROFILE_COUNT,
        "current_mworks_routes": CURRENT_MWORKS_ROUTE_COUNT,
        "planned_mworks_profiles": 1,
        "engineering_deployment_baseline": 1,
        "total": ACTIVE_ENTRY_COUNT,
    }
    summary = catalog.get("count_summary")
    if not isinstance(summary, dict) or any(summary.get(key) != value for key, value in expected_summary.items()):
        add("CSC-COUNT-02", f"count_summary must equal {expected_summary}")

    families = catalog.get("families")
    if not isinstance(families, list):
        add("CSC-FAMILY-01", "families must be a list")
    else:
        actual_families = {
            str(item.get("category")): {
                "target_profile_count": item.get("target_profile_count"),
                "current_route_count": item.get("current_route_count"),
            }
            for item in families
            if isinstance(item, dict)
        }
        if actual_families != FAMILY_SPECS:
            add("CSC-FAMILY-02", "families must define the seven approved semantic families and counts")

    selection = catalog.get("selection_contract")
    if not isinstance(selection, dict):
        add("CSC-POLICY-01", "selection_contract must be an object")
    else:
        if selection.get("one_top_level_profile_per_run") is not True:
            add("CSC-POLICY-02", "exactly one top-level profile must be selected per run")
        if selection.get("generic_augmentation_selector") != "not_exposed_in_standard_ui":
            add("CSC-POLICY-03", "standard UI must not expose generic augmentation multi-selection")
        if selection.get("mpc_role") != "MPC/NMPC is a nominal optimization outer-loop family, not a generic augmentation.":
            add("CSC-POLICY-04", "MPC/NMPC must remain a nominal optimization family")
        if not str(selection.get("seven_scenario_policy", "")).strip():
            add("CSC-POLICY-05", "seven-scenario comparison policy is missing")

    schemes = catalog.get("schemes")
    if not isinstance(schemes, list):
        add("CSC-SCHEMES-01", "schemes must be a list")
        return errors
    if len(schemes) != ACTIVE_ENTRY_COUNT:
        add("CSC-COUNT-03", f"schemes must contain exactly {ACTIVE_ENTRY_COUNT} entries")

    by_id: dict[str, dict[str, Any]] = {}
    profile_ids: set[str] = set()
    type_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    graphical_matrix_ids: list[str] = []
    current_routes = 0
    full_profiles = 0
    planned_profiles = 0
    for index, scheme in enumerate(schemes):
        if not isinstance(scheme, dict):
            add("CSC-SCHEMES-02", f"schemes[{index}] must be an object")
            continue
        scheme_id = str(scheme.get("scheme_id", ""))
        profile_id = str(scheme.get("profile_id", ""))
        entry_type = str(scheme.get("entry_type", ""))
        category = str(scheme.get("category", ""))
        if not scheme_id or scheme_id in by_id:
            add("CSC-ID-01", f"schemes[{index}] has a missing or duplicate scheme_id: {scheme_id}")
        else:
            by_id[scheme_id] = scheme
        if not profile_id or profile_id in profile_ids:
            add("CSC-ID-02", f"schemes[{index}] has a missing or duplicate profile_id: {profile_id}")
        profile_ids.add(profile_id)
        type_counts[entry_type] += 1
        category_counts[category] += 1

        if scheme_id in ARCHIVED_HISTORICAL_IDS:
            add("CSC-ARCHIVE-01", f"{scheme_id} is historical blocker evidence, not an active profile")
        if entry_type == "mworks_control_profile":
            if category not in FAMILY_SPECS:
                add("CSC-FAMILY-03", f"{scheme_id} has an unsupported MWORKS profile category: {category}")
            execution_kind = scheme.get("execution_kind")
            if execution_kind == "graphical_control_core":
                current_routes += 1
                matrix_id = str(scheme.get("evidence_matrix_controller", ""))
                if not matrix_id:
                    add("CSC-GRAPHICAL-01", f"{scheme_id} must bind one historical evidence-matrix controller")
                else:
                    graphical_matrix_ids.append(matrix_id)
                if not str(scheme.get("implementation_package", "")).strip():
                    add("CSC-GRAPHICAL-02", f"{scheme_id} must identify its current implementation package")
            elif execution_kind == "full_profile_whole_aircraft":
                current_routes += 1
                full_profiles += 1
            elif execution_kind == "planned_profile":
                planned_profiles += 1
                if scheme_id != PLANNED_PROFILE_ID or scheme.get("role") != "planned" or scheme.get("implementation_status") != "planned":
                    add("CSC-PLANNED-01", "only the planned PidAwffLinearEso profile may use planned_profile")
            else:
                add("CSC-KIND-01", f"{scheme_id} has an invalid MWORKS execution_kind: {execution_kind}")
        elif entry_type == "engineering_deployment_baseline":
            if scheme_id != "px4ctrl" or category != "engineering_deployment_baseline":
                add("CSC-PX4CTRL-01", "the sole deployment baseline must be px4ctrl")
            if scheme.get("execution_kind") != "mworks_equivalent_core_pending":
                add("CSC-PX4CTRL-02", "px4ctrl must remain pending MWORKS-equivalent-core implementation")
            if scheme.get("registry_module_id") != "px4ctrl":
                add("CSC-PX4CTRL-03", "px4ctrl must bind the registered px4ctrl module")
        else:
            add("CSC-TYPE-01", f"{scheme_id} has an unsupported entry_type: {entry_type}")

    if type_counts != Counter({"mworks_control_profile": MWORKS_PROFILE_COUNT, "engineering_deployment_baseline": 1}):
        add("CSC-TYPE-02", "entry types must be 47 MWORKS profiles plus one deployment baseline")
    for category, spec in FAMILY_SPECS.items():
        if category_counts[category] != spec["target_profile_count"]:
            add("CSC-FAMILY-04", f"{category} must contain {spec['target_profile_count']} profiles")
    if current_routes != CURRENT_MWORKS_ROUTE_COUNT or full_profiles != CURRENT_FULL_PROFILE_COUNT or planned_profiles != 1:
        add("CSC-COUNT-04", "MWORKS split must remain 46 current routes = 41 graphical cores + 5 full profiles, plus one planned profile")
    if len(graphical_matrix_ids) != CURRENT_GRAPHICAL_CORE_COUNT or len(set(graphical_matrix_ids)) != len(graphical_matrix_ids):
        add("CSC-GRAPHICAL-03", "current graphical core bindings must contain 41 unique historical matrix IDs")

    matrix_rows = matrix.get("rows")
    if not isinstance(matrix_rows, list):
        add("CSC-MATRIX-01", "historical controller evidence matrix rows must be a list")
    else:
        matrix_ids = [str(row.get("controller", "")) for row in matrix_rows if isinstance(row, dict)]
        if len(matrix_ids) != len(set(matrix_ids)):
            add("CSC-MATRIX-02", "historical controller evidence matrix has duplicate controller IDs")
        missing = sorted(set(graphical_matrix_ids) - set(matrix_ids))
        if missing:
            add("CSC-MATRIX-03", f"active graphical profiles are missing historical source rows: {missing}")

    for scheme_id, expected in FULL_PROFILE_SPECS.items():
        entry = by_id.get(scheme_id)
        if not isinstance(entry, dict):
            add("CSC-FULL-01", f"full profile is missing: {scheme_id}")
            continue
        for field, value in expected.items():
            if entry.get(field) != value:
                add("CSC-FULL-02", f"{scheme_id} {field} must equal {value}")
        source_path = resolve(str(entry.get("source_config", "")))
        if not source_path.is_file():
            add("CSC-FULL-03", f"{scheme_id} source config is missing: {source_path}")
        elif yaml_controller_id(source_path) != entry.get("source_controller_id"):
            add("CSC-FULL-04", f"{scheme_id} source_controller_id does not match {source_path}")
        chain = entry.get("profile_chain")
        if not isinstance(chain, list) or len(chain) < 2 or not all(isinstance(item, str) and item for item in chain):
            add("CSC-FULL-05", f"{scheme_id} must declare a non-trivial profile_chain")
        if not str(entry.get("profile_topology_note", "")).strip():
            add("CSC-FULL-06", f"{scheme_id} must explain its fixed internal topology")

    registry_modules = registry.get("modules") if isinstance(registry.get("modules"), list) else []
    px4ctrl_module = next(
        (item for item in registry_modules if isinstance(item, dict) and item.get("module_id") == "px4ctrl"),
        None,
    )
    if not isinstance(px4ctrl_module, dict) or px4ctrl_module.get("kind") != "nominal_controller" or px4ctrl_module.get("family") != "px4ctrl":
        add("CSC-PX4CTRL-04", "registry must retain px4ctrl as a nominal-controller deployment baseline")

    research = catalog.get("research_basis")
    doi_values = (
        {str(item.get("doi", "")).lower() for item in research if isinstance(item, dict)}
        if isinstance(research, list)
        else set()
    )
    if doi_values != REQUIRED_RESEARCH_DOIS:
        add("CSC-RESEARCH-01", "research_basis DOI set does not match the approved architecture basis")

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
        "active_entry_count": ACTIVE_ENTRY_COUNT,
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
