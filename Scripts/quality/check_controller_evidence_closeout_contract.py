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
HARNESS_MAP_PATH = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
HISTORICAL_CAPTURE_PATH = WORKFLOW_ROOT / "controller_document_evidence_capture_20260720.md"
HISTORICAL_CLASSIC_CLOSEOUT_PATH = WORKFLOW_ROOT / "classic_controller_family_closeout.md"
CONTROLLER_DESIGN_README_PATH = CONTROLLER_DESIGN_ROOT / "README.md"

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
        "formal_harness_map": read_json(HARNESS_MAP_PATH),
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
    formal_harness_map = inputs.get("formal_harness_map")
    active_docs = inputs.get("active_docs")

    for phrase in (
        "当前 G1-G7 顺序",
        "G1：以 49 方案目录",
        "G7：补齐安全、故障、固定三机编队",
        "46 条当前 MWORKS 路线",
        "2026-07-16 的旧",
        "历史 H1-H7",
        "formal_closed_loop_harness_map.json",
        "`internal_graphical_probe`",
        "`resolved_canonical_whole_aircraft_harness`",
        "Windows 原生整窗截图",
        "冠军测试壳晋级",
        "正式根内的核心、Adapter、整机 source harness",
    ):
        if phrase not in closeout:
            add("CCEC-DOC-01", f"closeout workflow is missing contract marker: {phrase}")

    for phrase in (
        "G4 Current Model Entry Mapping and Non-destructive Refactor Contract",
        "Config/control_platform/current_model_entry_map.json",
        "not the 49-scheme current-model-entry registry",
        "G4 is non-destructive",
        "does not open MWORKS",
        "formal_closed_loop_harness_map.json",
        "internal_graphical_probe",
        "champion-specific core/Adapter/plant binding",
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
        historical_capture = str(active_docs.get(portable(HISTORICAL_CAPTURE_PATH), ""))
        if (
            "历史快照" not in historical_capture
            or "controller_evidence_closeout.md" not in historical_capture
            or "formal_closed_loop_harness_map.json" not in historical_capture
        ):
            add("CCEC-DOC-10", "old screenshot-capture workflow must remain an explicit historical redirect")
        historical_classic = str(active_docs.get(portable(HISTORICAL_CLASSIC_CLOSEOUT_PATH), ""))
        if (
            "Historical Snapshot" not in historical_classic
            or "controller_evidence_closeout.md" not in historical_classic
        ):
            add("CCEC-DOC-11", "classic-controller closeout must remain an explicit historical snapshot")
        controller_readme = str(active_docs.get(portable(CONTROLLER_DESIGN_README_PATH), ""))
        if "当前 49 条方案与历史 67 条分层路线" not in controller_readme:
            add("CCEC-DOC-12", "controller design README must distinguish current 49 schemes from historical 67 routes")

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
    if not isinstance(formal_harness_map, dict):
        add("CCEC-HARNESS-01", "formal closed-loop harness map must be a readable object")
    else:
        harness_rows = formal_harness_map.get("schemes")
        if (
            formal_harness_map.get("schema") != "mosim.formal_closed_loop_harness_map.v1"
            or not isinstance(harness_rows, list)
        ):
            add("CCEC-HARNESS-02", "formal harness map schema or scheme list is invalid")
        else:
            harness_ids = {
                str(row.get("scheme_id"))
                for row in harness_rows
                if isinstance(row, dict) and row.get("scheme_id")
            }
            if len(harness_ids) != 49 or harness_ids != catalog_ids:
                add("CCEC-HARNESS-03", "formal harness map must cover the frozen 49 catalog scheme IDs")
            harness_state_counts: dict[str, int] = {}
            for row in harness_rows:
                if not isinstance(row, dict):
                    continue
                state = str(row.get("formal_harness_state"))
                harness_state_counts[state] = harness_state_counts.get(state, 0) + 1
            if harness_state_counts != {
                "missing_closed_loop_harness": 41,
                "resolved_canonical_whole_aircraft_harness": 5,
                "blocked_before_harness_mapping": 2,
                "not_applicable_runtime_baseline": 1,
            }:
                add("CCEC-HARNESS-04", "formal harness map must retain 41 internal-only cores and 5 whole-aircraft harnesses")
            graphical_rows = [
                row
                for row in harness_rows
                if isinstance(row, dict)
                and row.get("formal_harness_state") == "missing_closed_loop_harness"
            ]
            integrated_rows = [
                row
                for row in harness_rows
                if isinstance(row, dict)
                and row.get("formal_harness_state") == "resolved_canonical_whole_aircraft_harness"
            ]
            if len(graphical_rows) != 41 or len(integrated_rows) != 5:
                add("CCEC-HARNESS-05", "formal harness map candidate split must remain 46 = 41 graphical cores + 5 fixed integrated chains")
            for row in graphical_rows:
                target = row.get("topology_review_target")
                target_file = str(target.get("model_file") or "") if isinstance(target, dict) else ""
                if (
                    row.get("minimum_whole_aircraft_closure_eligible") is not False
                    or not isinstance(row.get("internal_probe"), dict)
                    or row.get("canonical_closed_loop_harness") is not None
                    or not target_file.startswith("Models/MoSimQuadrotorModel/")
                ):
                    add("CCEC-HARNESS-06", f"{row.get('scheme_id')}: graphical core must remain an internal-only formal-root probe")
            for row in integrated_rows:
                harness = row.get("canonical_closed_loop_harness")
                public_file = str(harness.get("public_entry_file") or "") if isinstance(harness, dict) else ""
                source_file = str(harness.get("whole_aircraft_source_file") or "") if isinstance(harness, dict) else ""
                if (
                    row.get("minimum_whole_aircraft_closure_eligible") is not True
                    or not isinstance(harness, dict)
                    or not isinstance(row.get("formal_adapter"), dict)
                    or not public_file.startswith("Models/MoSimQuadrotorModel/")
                    or not source_file.startswith("Models/MoSimQuadrotorModel/")
                ):
                    add("CCEC-HARNESS-07", f"{row.get('scheme_id')}: integrated chain must retain its formal whole-aircraft harness")
        promotion = formal_harness_map.get("champion_harness_promotion")
        if not isinstance(promotion, dict) or promotion.get("state") != "required_before_g6":
            add("CCEC-HARNESS-08", "champion formal-harness promotion gate must remain required before G6")
        provisional = formal_harness_map.get("provisional_champion_selection")
        if not isinstance(provisional, dict):
            add("CCEC-HARNESS-09", "provisional six-family champion selection is missing")
        else:
            candidates = provisional.get("candidates")
            expected_categories = {
                "pid_family",
                "classic_robust",
                "sliding_mode",
                "optimization",
                "geometric_flatness",
                "learning",
            }
            categories = {
                str(candidate.get("category"))
                for candidate in candidates
                if isinstance(candidate, dict)
            } if isinstance(candidates, list) else set()
            selection_state = provisional.get("state")
            valid_selection_states = {
                "candidate_slate_pending_current_matrix",
                "candidate_slate_ready_for_family_selection",
            }
            if (
                provisional.get("schema") != "mosim.g6_provisional_champion_selection.v1"
                or selection_state not in valid_selection_states
                or not isinstance(candidates, list)
                or len(candidates) != 6
                or categories != expected_categories
            ):
                add("CCEC-HARNESS-10", "candidate slate must cover six nominal families with a valid current-matrix state")
            probe_statuses: list[object] = []
            for candidate in candidates if isinstance(candidates, list) else []:
                if not isinstance(candidate, dict):
                    continue
                scheme_id = str(candidate.get("scheme_id") or "<missing>")
                mapped = next(
                    (
                        row
                        for row in harness_rows
                        if isinstance(row, dict) and row.get("scheme_id") == scheme_id
                    ),
                    None,
                )
                probe = candidate.get("g6_probe")
                probe_status = probe.get("status") if isinstance(probe, dict) else None
                probe_statuses.append(probe_status)
                expected_promotion = (
                    "adapter_binding_pending"
                    if probe_status == "passed"
                    else "awaiting_current_g6_probe"
                )
                if (
                    not isinstance(mapped, dict)
                    or mapped.get("formal_harness_state") != "missing_closed_loop_harness"
                    or not isinstance(probe, dict)
                    or probe.get("evidence_class") != "internal_fixed_input_probe"
                    or candidate.get("promotion_state") != expected_promotion
                ):
                    add("CCEC-HARNESS-11", f"{scheme_id}: candidate state does not match the current probe and adapter prerequisite")
            if isinstance(candidates, list) and len(candidates) == 6:
                all_probes_passed = all(status == "passed" for status in probe_statuses)
                if selection_state == "candidate_slate_pending_current_matrix" and all_probes_passed:
                    add("CCEC-HARNESS-10", "candidate slate remains pending although every current-matrix probe passed")
                if selection_state == "candidate_slate_ready_for_family_selection" and not all_probes_passed:
                    add("CCEC-HARNESS-10", "candidate slate is ready although a current-matrix probe is not passed")
            baseline = provisional.get("official_pid_baseline")
            if (
                not isinstance(baseline, dict)
                or baseline.get("scheme_id") != "official_pid"
                or baseline.get("binding_state") != "formal_binding_ready_for_validation"
                or not isinstance(baseline.get("formal_adapter"), dict)
                or not isinstance(baseline.get("whole_aircraft_source_harness"), dict)
            ):
                add("CCEC-HARNESS-12", "Official PID A/B baseline must remain a separately bound formal runner")
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
