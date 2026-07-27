#!/usr/bin/env python3
"""Validate the G1 active 48-entry execution inventory without execution."""

from __future__ import annotations

import argparse
import hashlib
import json
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
DEFAULT_INVENTORY = (
    ROOT
    / "Results"
    / "control_platform"
    / "g1_control_scheme_execution_inventory_20260722"
    / "CONTROL_SCHEME_EXECUTION_INVENTORY.json"
)

ACTIVE_ENTRY_COUNT = 48
CURRENT_MWORKS_ROUTE_COUNT = 46
FAMILY_SCREENING_CANDIDATE_COUNT = 45


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def validate(
    inventory: dict[str, Any],
    catalog: dict[str, Any],
    matrix: dict[str, Any],
    registry: dict[str, Any],
    document_inventory: dict[str, Any],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    if (
        inventory.get("schema") != "mosim.control_scheme_execution_inventory.v2"
        or inventory.get("version") != 2
    ):
        add("CSE-SCHEMA-01", "inventory must use mosim.control_scheme_execution_inventory.v2 version 2")
    schemes = inventory.get("schemes")
    if not isinstance(schemes, list):
        add("CSE-ROWS-01", "schemes must be a list")
        return errors
    catalog_schemes = catalog.get("schemes") if isinstance(catalog.get("schemes"), list) else []
    catalog_by_id = {
        str(item.get("scheme_id")): item for item in catalog_schemes if isinstance(item, dict)
    }
    inventory_by_id = {
        str(item.get("scheme_id")): item for item in schemes if isinstance(item, dict)
    }
    if (
        len(schemes) != ACTIVE_ENTRY_COUNT
        or len(inventory_by_id) != ACTIVE_ENTRY_COUNT
        or set(inventory_by_id) != set(catalog_by_id)
    ):
        add("CSE-COUNT-01", "inventory must contain exactly the 48 unique active catalog profile IDs")
    for retired_id in ("mu_synthesis", "neural_smc"):
        if retired_id in inventory_by_id:
            add("CSE-RETIRED-01", f"{retired_id} must remain historical-only, not an active inventory row")

    source_hashes = inventory.get("source_sha256")
    expected_hashes = {
        "control_scheme_catalog": catalog,
        "classic_controller_final_matrix": matrix,
        "control_module_registry": registry,
        "controller_document_evidence_inventory": document_inventory,
    }
    if not isinstance(source_hashes, dict):
        add("CSE-SOURCE-01", "source_sha256 must be an object")
    else:
        for name, data in expected_hashes.items():
            encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            expected = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
            if source_hashes.get(name) != expected:
                add("CSE-SOURCE-02", f"{name} hash is stale; rebuild the G1 inventory")

    matrix_by_id = {
        str(row.get("controller")): row
        for row in matrix.get("rows", [])
        if isinstance(row, dict) and row.get("controller")
    }
    document_by_id = {
        str(row.get("controller")): row
        for row in document_inventory.get("rows", [])
        if isinstance(row, dict) and row.get("controller")
    }
    registry_by_id = {
        str(row.get("module_id")): row
        for row in registry.get("modules", [])
        if isinstance(row, dict) and row.get("module_id")
    }

    current_route_count = 0
    screening_candidate_count = 0
    type_counts: Counter[str] = Counter()
    for scheme_id, row in inventory_by_id.items():
        catalog_row = catalog_by_id.get(scheme_id)
        if not isinstance(catalog_row, dict):
            continue
        prefix = f"{scheme_id}: "
        entry_type = str(catalog_row.get("entry_type"))
        execution_kind = str(catalog_row.get("execution_kind"))
        type_counts[entry_type] += 1
        if (
            row.get("entry_type") != entry_type
            or row.get("category") != catalog_row.get("category")
            or row.get("profile_role") != catalog_row.get("role")
            or row.get("selection_eligibility") != catalog_row.get("selection_eligibility")
            or row.get("execution_kind") != execution_kind
        ):
            add("CSE-CATALOG-01", prefix + "profile identity fields must match the active catalog")

        model_entry = row.get("model_entry") if isinstance(row.get("model_entry"), dict) else {}
        eligible = row.get("mworks_run_eligible")
        if not isinstance(eligible, bool):
            add("CSE-RUN-01", prefix + "mworks_run_eligible must be boolean")
        if eligible:
            add("CSE-RUN-02", prefix + "G1 inventory may not authorize MWORKS execution")

        if entry_type == "mworks_control_profile":
            if execution_kind in {"graphical_control_core", "full_profile_whole_aircraft"}:
                current_route_count += 1
                if catalog_row.get("selection_eligibility") == "family_screening":
                    screening_candidate_count += 1
            if execution_kind == "graphical_control_core":
                controller = str(catalog_row.get("evidence_matrix_controller"))
                matrix_row = matrix_by_id.get(controller)
                document_row = document_by_id.get(controller)
                if row.get("control_owner") != "profile_graphical_control_core":
                    add("CSE-GRAPHICAL-01", prefix + "graphical profile must own the graphical-control-core slot")
                if row.get("evidence_route") != controller or not isinstance(matrix_row, dict):
                    add("CSE-GRAPHICAL-02", prefix + "graphical profile must bind its exact historical matrix row")
                elif row.get("current_evidence", {}).get("matrix_status") != matrix_row.get("status"):
                    add("CSE-GRAPHICAL-03", prefix + "matrix status drifted from authority")
                if not isinstance(document_row, dict):
                    add("CSE-GRAPHICAL-04", prefix + "graphical profile is missing document-evidence inventory row")
                binding = row.get("registry_binding") if isinstance(row.get("registry_binding"), dict) else {}
                registry_module = registry_by_id.get(scheme_id)
                if registry_module and binding.get("mapping_state") != "exact_registry_binding":
                    add("CSE-GRAPHICAL-05", prefix + "registered graphical profile must retain exact registry binding")
                if not registry_module and binding.get("mapping_state") != "no_exact_registry_binding":
                    add("CSE-GRAPHICAL-06", prefix + "unregistered graphical profile must remain explicitly unbound")
            elif execution_kind == "full_profile_whole_aircraft":
                if row.get("control_owner") != "full_profile_whole_aircraft":
                    add("CSE-FULL-01", prefix + "full profile must retain whole-aircraft profile ownership")
                if model_entry.get("source_config") != catalog_row.get("source_config"):
                    add("CSE-FULL-02", prefix + "full-profile source config drifted from catalog")
                if not isinstance(row.get("profile_chain"), list) or len(row["profile_chain"]) < 2:
                    add("CSE-FULL-03", prefix + "full profile must retain a non-trivial profile chain")
            elif execution_kind == "planned_profile":
                if scheme_id != "pid_awff_linear_eso" or row.get("control_owner") != "planned_profile":
                    add("CSE-PLANNED-01", prefix + "only the approved ESO row may remain planned")
                if model_entry.get("mapping_state") != "planned_profile_no_model":
                    add("CSE-PLANNED-02", prefix + "planned ESO profile must not invent a current model")
            else:
                add("CSE-KIND-01", prefix + "unsupported MWORKS execution kind")
        elif entry_type == "engineering_deployment_baseline":
            if scheme_id != "px4ctrl" or row.get("control_owner") != "engineering_deployment_baseline":
                add("CSE-PX4CTRL-01", prefix + "deployment baseline must remain px4ctrl")
            if model_entry.get("mapping_state") != "pending_mworks_equivalent_core" or eligible:
                add("CSE-PX4CTRL-02", prefix + "px4ctrl must remain pending its MWORKS-equivalent core")
        else:
            add("CSE-TYPE-01", prefix + "unsupported catalog entry_type")

    if type_counts != Counter({"mworks_control_profile": 47, "engineering_deployment_baseline": 1}):
        add("CSE-COUNT-02", "inventory must retain 47 MWORKS profiles plus px4ctrl")
    if current_route_count != CURRENT_MWORKS_ROUTE_COUNT:
        add("CSE-COUNT-03", "inventory must retain 46 current MWORKS routes")
    if screening_candidate_count != FAMILY_SCREENING_CANDIDATE_COUNT:
        add("CSE-COUNT-04", "inventory must retain 45 family-screening candidates")
    summary = inventory.get("summary")
    if not isinstance(summary, dict) or summary.get("active_top_level_entry_count") != ACTIVE_ENTRY_COUNT:
        add("CSE-SUMMARY-01", "summary must retain the active 48-entry boundary")
    if isinstance(summary, dict) and summary.get("mworks_run_eligible_count") != 0:
        add("CSE-SUMMARY-02", "G1 inventory may not promote any MWORKS route to runnable")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--document-inventory", type=Path, default=DEFAULT_DOCUMENT_INVENTORY)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    paths = [args.inventory, args.catalog, args.matrix, args.registry, args.document_inventory]
    paths = [path if path.is_absolute() else ROOT / path for path in paths]
    try:
        inventory, catalog, matrix, registry, document_inventory = [load_json(path) for path in paths]
        errors = validate(inventory, catalog, matrix, registry, document_inventory)
    except Exception as exc:
        errors = [{"code": "CSE-READ-01", "message": str(exc)}]
    report = {
        "ok": not errors,
        "inventory": str(paths[0]),
        "active_top_level_entry_count": len(inventory.get("schemes", [])) if "inventory" in locals() else 0,
        "mworks_run_eligible_count": (
            sum(bool(row.get("mworks_run_eligible")) for row in inventory.get("schemes", []) if isinstance(row, dict))
            if "inventory" in locals()
            else 0
        ),
        "error_count": len(errors),
        "errors": errors,
    }
    if args.output_json:
        output = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
