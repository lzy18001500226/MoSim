#!/usr/bin/env python3
"""Verify the static G1-G7 controller-evidence closeout contract.

This checker is deliberately source-only. It does not open MWORKS, mutate a
Modelica package, start any simulation, or promote historical result copies to
current model entries.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / "Docs" / "Workflows" / "controller_evidence_closeout.md"
MODEL_INDEX_PATH = ROOT / "Docs" / "Index" / "simulation_model_structure_index.md"
WORKFLOW_INDEX_PATH = ROOT / "Docs" / "Index" / "workflow_index.md"

REQUIREMENTS_PATH = ROOT / "Docs" / "Design" / "需求.md"
CONTROLLER_DESIGN_ROOT = ROOT / "Docs" / "Design" / "架构" / "01_控制器平台"
WORKFLOW_ROOT = ROOT / "Docs" / "Workflows"
OPERATION_CATALOG_PATH = ROOT / "Config" / "control_platform" / "model_operation_catalog.json"
SCHEME_CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
INVENTORY_PATH = (
    ROOT
    / "Results"
    / "control_platform"
    / "g1_control_scheme_execution_inventory_20260722"
    / "CONTROL_SCHEME_EXECUTION_INVENTORY.json"
)
CURRENT_MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"

EXPECTED_ENTRY_TYPE_COUNTS = {
    "competition_primary_route": 43,
    "engineering_baseline": 1,
    "fixed_integrated_scheme": 5,
}
EXPECTED_OPERATION_SCOPE = "allowlisted_model_studio_operations_only"
EXPECTED_NON_AUTHORITY = {
    "complete_49_scheme_model_entry_mapping",
    "current_project_model_entry_promotion",
    "g4_g5_mworks_eligibility",
}
FORBIDDEN_ACTIVE_G89 = re.compile(
    r"(?:\bcurrent\s+G(?:8|9(?:\.\d+)?)\b|\bactive\s+G(?:8|9(?:\.\d+)?)\b|当前\s*G(?:8|9(?:\.\d+)?))",
    re.IGNORECASE,
)
FORBIDDEN_OPEN_ENHANCEMENT = re.compile(r"0\s*\.\.\s*N", re.IGNORECASE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def portable(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def active_document_texts() -> dict[str, str]:
    paths = sorted(WORKFLOW_ROOT.glob("*.md"))
    paths.extend(sorted(CONTROLLER_DESIGN_ROOT.rglob("*.md")))
    paths.append(REQUIREMENTS_PATH)
    return {portable(path): read_text(path) for path in paths}


def load_inputs() -> dict[str, Any]:
    return {
        "closeout": read_text(WORKFLOW_PATH),
        "model_index": read_text(MODEL_INDEX_PATH),
        "workflow_index": read_text(WORKFLOW_INDEX_PATH),
        "operation_catalog": read_json(OPERATION_CATALOG_PATH),
        "scheme_catalog": read_json(SCHEME_CATALOG_PATH),
        "inventory": read_json(INVENTORY_PATH),
        "current_model_map": read_json(CURRENT_MAP_PATH),
        "active_docs": active_document_texts(),
    }


def validate(inputs: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    closeout = str(inputs.get("closeout") or "")
    model_index = str(inputs.get("model_index") or "")
    workflow_index = str(inputs.get("workflow_index") or "")
    operation_catalog = inputs.get("operation_catalog")
    scheme_catalog = inputs.get("scheme_catalog")
    inventory = inputs.get("inventory")
    current_model_map = inputs.get("current_model_map")
    active_docs = inputs.get("active_docs")

    for phrase in (
        "当前 G1-G7 顺序",
        "G1：以 49 方案目录",
        "G7：补齐安全、故障、固定三机编队",
        "46 条当前 MWORKS 路线",
        "2026-07-16 的旧",
        "历史 H1-H7",
    ):
        if phrase not in closeout:
            add("CCEC-DOC-01", f"closeout workflow is missing contract marker: {phrase}")

    for phrase in (
        "G4 Current Model Entry Mapping and Non-destructive Refactor Contract",
        "Config/control_platform/current_model_entry_map.json",
        "not the 49-scheme current-model-entry registry",
        "G4 is non-destructive",
        "does not open MWORKS",
    ):
        if phrase not in model_index:
            add("CCEC-DOC-02", f"model structure index is missing G4 contract marker: {phrase}")

    if "Docs/Workflows/controller_evidence_closeout.md" not in workflow_index:
        add("CCEC-DOC-03", "workflow index must route controller evidence closeout work to its current workflow")

    if not isinstance(active_docs, dict):
        add("CCEC-DOC-05", "active documentation set must be available for stale-goal checks")
    else:
        for path, text in active_docs.items():
            normalized = str(text)
            if FORBIDDEN_ACTIVE_G89.search(normalized):
                add("CCEC-DOC-06", f"active document still presents G8/G9 as current: {path}")
            if FORBIDDEN_OPEN_ENHANCEMENT.search(normalized):
                add("CCEC-DOC-07", f"active document still permits open-ended 0..N enhancement composition: {path}")

        requirement_text = str(active_docs.get(portable(REQUIREMENTS_PATH), ""))
        if "Docs/Workflows/controller_evidence_closeout.md" not in requirement_text:
            add("CCEC-DOC-08", "requirements must point current G1-G7 execution to the closeout workflow")
        historical_interface = CONTROLLER_DESIGN_ROOT / "控制平台接口与闭环实施规范.md"
        historical_text = str(active_docs.get(portable(historical_interface), ""))
        if "历史 H1-H7" not in historical_text or "当前 G1-G7" not in historical_text:
            add("CCEC-DOC-09", "old interface-closeout numbering must remain explicitly historical H1-H7")

    if not isinstance(operation_catalog, dict):
        add("CCEC-CATALOG-01", "model operation catalog must be an object")
    else:
        if operation_catalog.get("authority_scope") != EXPECTED_OPERATION_SCOPE:
            add("CCEC-CATALOG-02", "model operation catalog must declare its narrow operation-only scope")
        non_authoritative_for = operation_catalog.get("non_authoritative_for")
        if not isinstance(non_authoritative_for, list) or not EXPECTED_NON_AUTHORITY.issubset(
            {str(value) for value in non_authoritative_for}
        ):
            add("CCEC-CATALOG-03", "model operation catalog must reject 49-scheme mapping/promotion/G4-G5 authority")
        profiles = operation_catalog.get("model_profiles")
        if not isinstance(profiles, list) or not profiles:
            add("CCEC-CATALOG-04", "model operation catalog must contain explicit allowlisted operation profiles")
        elif len(profiles) >= 49:
            add("CCEC-CATALOG-05", "model operation catalog cannot become a substitute 49-scheme model-entry registry")

    if not isinstance(scheme_catalog, dict) or not isinstance(inventory, dict):
        add("CCEC-INV-01", "scheme catalog and G1 inventory must be readable objects")
        return errors

    catalog_rows = scheme_catalog.get("schemes")
    inventory_rows = inventory.get("schemes")
    if not isinstance(catalog_rows, list) or not isinstance(inventory_rows, list):
        add("CCEC-INV-02", "scheme catalog and G1 inventory must both expose scheme lists")
        return errors

    catalog_ids = {str(row.get("scheme_id")) for row in catalog_rows if isinstance(row, dict) and row.get("scheme_id")}
    inventory_ids = {str(row.get("scheme_id")) for row in inventory_rows if isinstance(row, dict) and row.get("scheme_id")}
    if len(catalog_ids) != 49 or inventory_ids != catalog_ids:
        add("CCEC-INV-03", "G1 inventory must cover exactly the frozen 49 catalog scheme IDs")

    type_counts: dict[str, int] = {}
    for row in inventory_rows:
        if not isinstance(row, dict):
            continue
        entry_type = str(row.get("entry_type"))
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
    if type_counts != EXPECTED_ENTRY_TYPE_COUNTS:
        add("CCEC-INV-04", "inventory must retain the 43 primary + 1 px4ctrl + 5 fixed-chain boundary")

    if not isinstance(current_model_map, dict):
        add("CCEC-MAP-01", "current model entry map must be a readable object")
    else:
        current_rows = current_model_map.get("schemes")
        if current_model_map.get("schema") != "mosim.current_model_entry_map.v1" or not isinstance(current_rows, list):
            add("CCEC-MAP-02", "current model entry map schema or scheme list is invalid")
        else:
            current_ids = {str(row.get("scheme_id")) for row in current_rows if isinstance(row, dict) and row.get("scheme_id")}
            if len(current_ids) != 49 or current_ids != catalog_ids:
                add("CCEC-MAP-03", "current model entry map must cover the frozen 49 catalog scheme IDs")
            state_counts: dict[str, int] = {}
            for row in current_rows:
                if not isinstance(row, dict):
                    continue
                state = str(row.get("mapping_state"))
                state_counts[state] = state_counts.get(state, 0) + 1
            if state_counts != {
                "resolved_current_model": 46,
                "blocked_missing_current_model": 2,
                "not_applicable_runtime_baseline": 1,
            }:
                add("CCEC-MAP-04", "current model map must retain 46 resolved routes, 2 blockers, and 1 runtime baseline")
            blocked_ids = {
                str(row.get("scheme_id"))
                for row in current_rows
                if isinstance(row, dict) and row.get("mapping_state") == "blocked_missing_current_model"
            }
            if blocked_ids != {"mu_synthesis", "neural_smc"}:
                add("CCEC-MAP-05", "mu_synthesis and neural_smc must remain the only blocked current-model routes")
            px4_rows = [row for row in current_rows if isinstance(row, dict) and row.get("scheme_id") == "px4ctrl"]
            if len(px4_rows) != 1:
                add("CCEC-MAP-06", "current model map must contain exactly one px4ctrl runtime baseline")
            else:
                px4 = px4_rows[0]
                if (
                    px4.get("entry_type") != "engineering_baseline"
                    or px4.get("mapping_state") != "not_applicable_runtime_baseline"
                    or px4.get("mworks_run_eligible") is not False
                ):
                    add("CCEC-MAP-07", "px4ctrl must remain a non-graphical MWORKS-inapplicable runtime baseline")
            for row in current_rows:
                if not isinstance(row, dict):
                    continue
                scheme_id = str(row.get("scheme_id") or "<missing>")
                mapping_state = row.get("mapping_state")
                current_file = str(row.get("current_model_file") or "")
                eligible = row.get("mworks_run_eligible")
                if mapping_state == "resolved_current_model" and not current_file.startswith("Models/"):
                    add("CCEC-MAP-08", f"{scheme_id}: resolved current model must live below Models/")
                if eligible is True and (mapping_state != "resolved_current_model" or not current_file.startswith("Models/")):
                    add("CCEC-MAP-09", f"{scheme_id}: unresolved or Results-backed model cannot enable MWORKS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    try:
        inputs = load_inputs()
        errors = validate(inputs)
    except Exception as exc:
        errors = [{"code": "CCEC-READ-01", "message": str(exc)}]
        inputs = {}
    report = {
        "schema": "mosim.controller_evidence_closeout_contract.v1",
        "ok": not errors,
        "current_goal": "G1-G7 controller evidence closeout",
        "active_document_count": len(inputs.get("active_docs", {})),
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
