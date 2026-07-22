#!/usr/bin/env python3
"""Validate the G1 49-scheme execution inventory without promoting execution."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    if inventory.get("schema") != "mosim.control_scheme_execution_inventory.v1" or inventory.get("version") != 1:
        add("CSE-SCHEMA-01", "inventory must use mosim.control_scheme_execution_inventory.v1 version 1")
    schemes = inventory.get("schemes")
    if not isinstance(schemes, list):
        add("CSE-ROWS-01", "schemes must be a list")
        return errors
    catalog_schemes = catalog.get("schemes") if isinstance(catalog.get("schemes"), list) else []
    catalog_by_id = {str(item.get("scheme_id")): item for item in catalog_schemes if isinstance(item, dict)}
    inventory_by_id = {str(item.get("scheme_id")): item for item in schemes if isinstance(item, dict)}
    if len(schemes) != 49 or len(inventory_by_id) != 49 or set(inventory_by_id) != set(catalog_by_id):
        add("CSE-COUNT-01", "inventory must contain exactly the 49 unique catalog scheme IDs")

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
    for scheme_id, row in inventory_by_id.items():
        catalog_row = catalog_by_id.get(scheme_id)
        if not isinstance(catalog_row, dict):
            continue
        prefix = f"{scheme_id}: "
        if row.get("entry_type") != catalog_row.get("entry_type") or row.get("category") != catalog_row.get("category"):
            add("CSE-CATALOG-01", prefix + "entry_type/category must match the frozen catalog")
        model_entry = row.get("model_entry") if isinstance(row.get("model_entry"), dict) else {}
        eligible = row.get("mworks_run_eligible")
        if not isinstance(eligible, bool):
            add("CSE-RUN-01", prefix + "mworks_run_eligible must be boolean")
        if eligible and model_entry.get("mapping_state") != "resolved_current_model":
            add("CSE-RUN-02", prefix + "unresolved model mapping may not authorize an MWORKS run")
        if eligible and not str(model_entry.get("current_model_file") or ""):
            add("CSE-RUN-03", prefix + "eligible MWORKS run requires a current model file")

        entry_type = str(catalog_row.get("entry_type"))
        if entry_type == "competition_primary_route":
            controller = str(catalog_row.get("evidence_matrix_controller"))
            matrix_row = matrix_by_id.get(controller)
            document_row = document_by_id.get(controller)
            if row.get("control_owner") != "nominal_controller":
                add("CSE-PRIMARY-01", prefix + "primary route must own the nominal-controller slot")
            if row.get("evidence_route") != controller or not isinstance(matrix_row, dict):
                add("CSE-PRIMARY-02", prefix + "primary evidence route must bind its exact matrix row")
            elif row.get("current_evidence", {}).get("matrix_status") != matrix_row.get("status"):
                add("CSE-PRIMARY-03", prefix + "matrix status drifted from authority")
            if not isinstance(document_row, dict):
                add("CSE-PRIMARY-04", prefix + "primary route is missing document-evidence inventory row")
            binding = row.get("registry_binding") if isinstance(row.get("registry_binding"), dict) else {}
            registry_module = registry_by_id.get(scheme_id)
            if registry_module and binding.get("mapping_state") != "exact_registry_binding":
                add("CSE-PRIMARY-05", prefix + "registered primary route must retain exact registry binding")
            if not registry_module and binding.get("mapping_state") != "no_exact_registry_binding":
                add("CSE-PRIMARY-06", prefix + "unregistered legacy primary route must remain explicitly unbound")
        elif entry_type == "engineering_baseline":
            if scheme_id != "px4ctrl" or row.get("control_owner") != "nominal_controller_runtime_baseline":
                add("CSE-PX4CTRL-01", prefix + "engineering baseline must remain px4ctrl runtime baseline")
            if model_entry.get("mapping_state") != "not_applicable_runtime_baseline" or eligible:
                add("CSE-PX4CTRL-02", prefix + "px4ctrl must not be misrepresented as an MWORKS graphical scheme")
        elif entry_type == "fixed_integrated_scheme":
            if row.get("control_owner") != "fixed_integrated_chain":
                add("CSE-FIXED-01", prefix + "fixed scheme must retain fixed-integrated-chain ownership")
            if row.get("fixed_order") != catalog_row.get("fixed_order"):
                add("CSE-FIXED-02", prefix + "fixed order drifted from catalog")
            if model_entry.get("source_config") != catalog_row.get("source_config"):
                add("CSE-FIXED-03", prefix + "source config drifted from catalog")

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
        "top_level_scheme_count": len(inventory.get("schemes", [])) if "inventory" in locals() else 0,
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
