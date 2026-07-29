#!/usr/bin/env python3
"""Verify the static G1-G7 controller-evidence taxonomy contract.

This checker is deliberately source-only. It does not open MWORKS, mutate a
Modelica package, start any simulation, or promote historical result copies to
current model entries.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
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
HISTORICAL_WORKFLOW_ROOT = ROOT / "Docs" / "Cache" / "workflow_history"
HISTORICAL_CAPTURE_PATH = HISTORICAL_WORKFLOW_ROOT / "controller_document_evidence_capture_20260720.md"
HISTORICAL_CLASSIC_CLOSEOUT_PATH = HISTORICAL_WORKFLOW_ROOT / "classic_controller_family_closeout.md"

TAXONOMY_DOCS = (
    WORKFLOW_PATH,
    ROOT / "Docs" / "Workflows" / "g6_controller_experiment_execution.md",
    MODEL_INDEX_PATH,
    CONTROLLER_DESIGN_ROOT / "README.md",
    CONTROLLER_DESIGN_ROOT / "控制器证据矩阵.md",
    ROOT / "Docs" / "Design" / "架构.md",
    ROOT / "Docs" / "Workflows" / "mainline_operations_board.md",
    ROOT / "Docs" / "报告" / "审计" / "控制器证据审计.md",
    ROOT / "Docs" / "报告" / "README.md",
    ROOT / "Docs" / "报告" / "图" / "README.md",
)

ACTIVE_ENTRY_COUNT = 48
MWORKS_PROFILE_COUNT = 47
CURRENT_MWORKS_ROUTE_COUNT = 46
TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT = 45
TIER2_CURRENT_MWORKS_ROUTE_COUNT = 44
FAMILY_SCREENING_CANDIDATE_COUNT = 43
TIER1_ONLY_SCHEME_IDS = {"pid_awff_linear_eso", "smc_boundary_layer", "nmpc_outer"}
SEMANTIC_FAMILIES = {
    "pid_family",
    "linear_robust_state_feedback",
    "nonlinear_adaptive",
    "sliding_mode",
    "optimization_predictive",
    "geometric_flatness",
    "learning",
}
EXPECTED_ENTRY_TYPE_COUNTS = Counter(
    {
        "mworks_control_profile": MWORKS_PROFILE_COUNT,
        "engineering_deployment_baseline": 1,
    }
)
EXPECTED_MAP_STATES = Counter(
    {
        "resolved_current_model": 46,
        "planned_profile_no_model": 1,
        "pending_mworks_equivalent_core": 1,
    }
)
EXPECTED_HARNESS_STATES = Counter(
    {
        "missing_closed_loop_harness": 41,
        "resolved_canonical_whole_aircraft_harness": 5,
        "planned_profile_no_model": 1,
        "pending_mworks_equivalent_core": 1,
    }
)
EXPECTED_OPERATION_SCOPE = "allowlisted_model_studio_operations_only"
EXPECTED_NON_AUTHORITY = {
    "complete_48_profile_model_entry_mapping",
    "current_project_model_entry_promotion",
    "g4_g5_mworks_eligibility",
}
FORBIDDEN_ACTIVE_G89 = re.compile(
    r"(?:\bcurrent\s+G(?:8|9(?:\.\d+)?)\b|\bactive\s+G(?:8|9(?:\.\d+)?)\b|当前\s*G(?:8|9(?:\.\d+)?))",
    re.IGNORECASE,
)
FORBIDDEN_OPEN_ENHANCEMENT = re.compile(r"0\s*\.\.\s*N", re.IGNORECASE)
STALE_TAXONOMY = re.compile(
    r"(?:当前\s*49\s*条|49\s*方案目录|六个名义控制族|六族冠军|fixed_integrated)",
    re.IGNORECASE,
)


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
        "taxonomy_docs": {portable(path): read_text(path) for path in TAXONOMY_DOCS},
        "active_docs": active_document_texts(),
        "historical_capture": read_text(HISTORICAL_CAPTURE_PATH),
        "historical_classic_closeout": read_text(HISTORICAL_CLASSIC_CLOSEOUT_PATH),
    }


def validate(inputs: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    closeout = str(inputs.get("closeout") or "")
    model_index = str(inputs.get("model_index") or "")
    workflow_index = str(inputs.get("workflow_index") or "")
    taxonomy_docs = inputs.get("taxonomy_docs")
    active_docs = inputs.get("active_docs")
    operation_catalog = inputs.get("operation_catalog")
    scheme_catalog = inputs.get("scheme_catalog")
    inventory = inputs.get("inventory")
    current_model_map = inputs.get("current_model_map")
    formal_harness_map = inputs.get("formal_harness_map")

    for phrase in (
        "当前 G1-G7 顺序",
        "48 个活动条目",
        "47 个 MWORKS Control Profile",
        "七个语义控制族",
        "46 条当前 MWORKS 路线",
        "41 条图形控制器核",
        "5 条命名整机 Profile",
        "pid_awff_linear_eso",
        "px4ctrl",
        "Windows 原生整窗截图",
    ):
        if phrase not in closeout:
            add("CCEC-DOC-01", f"closeout workflow is missing taxonomy marker: {phrase}")

    for phrase in (
        "G4 Current Model Entry Mapping and Non-destructive Refactor Contract",
        "Config/control_platform/current_model_entry_map.json",
        "not the 48-profile current-model-entry registry",
        "G4 is non-destructive",
        "does not open MWORKS",
        "formal_closed_loop_harness_map.json",
        "41 graphical controller cores",
        "five named whole-aircraft profiles",
        "seven semantic families",
    ):
        if phrase not in model_index:
            add("CCEC-DOC-02", f"model structure index is missing taxonomy marker: {phrase}")

    if "Docs/Workflows/controller_evidence_closeout.md" not in workflow_index:
        add("CCEC-DOC-03", "workflow index must route controller evidence closeout work to its current workflow")

    if not isinstance(taxonomy_docs, dict):
        add("CCEC-DOC-04", "taxonomy documentation set must be available")
    else:
        for path, text in taxonomy_docs.items():
            if STALE_TAXONOMY.search(str(text)):
                add("CCEC-DOC-04", f"taxonomy document still carries stale 49/six-family/fixed-chain wording: {path}")

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

    historical_capture = str(inputs.get("historical_capture") or "")
    if "历史快照" not in historical_capture or "controller_evidence_closeout.md" not in historical_capture:
        add("CCEC-DOC-09", "old screenshot-capture workflow must remain an explicit historical redirect")
    historical_classic = str(inputs.get("historical_classic_closeout") or "")
    if "Historical Snapshot" not in historical_classic or "controller_evidence_closeout.md" not in historical_classic:
        add("CCEC-DOC-10", "classic-controller closeout must remain an explicit historical snapshot")

    if not isinstance(operation_catalog, dict):
        add("CCEC-CATALOG-01", "model operation catalog must be an object")
    else:
        if operation_catalog.get("authority_scope") != EXPECTED_OPERATION_SCOPE:
            add("CCEC-CATALOG-02", "model operation catalog must declare its narrow operation-only scope")
        non_authoritative_for = operation_catalog.get("non_authoritative_for")
        if not isinstance(non_authoritative_for, list) or not EXPECTED_NON_AUTHORITY.issubset(
            {str(value) for value in non_authoritative_for}
        ):
            add("CCEC-CATALOG-03", "model operation catalog must reject 48-profile mapping/promotion/G4-G5 authority")
        profiles = operation_catalog.get("model_profiles")
        if not isinstance(profiles, list) or not profiles:
            add("CCEC-CATALOG-04", "model operation catalog must contain explicit allowlisted operation profiles")
        elif len(profiles) >= ACTIVE_ENTRY_COUNT:
            add("CCEC-CATALOG-05", "model operation catalog cannot become a substitute active profile registry")

    if not isinstance(scheme_catalog, dict) or not isinstance(inventory, dict):
        add("CCEC-INV-01", "scheme catalog and G1 inventory must be readable objects")
        return errors
    catalog_rows = scheme_catalog.get("schemes")
    inventory_rows = inventory.get("schemes")
    if (
        scheme_catalog.get("schema") != "mosim.control_profile_catalog.v2"
        or inventory.get("schema") != "mosim.control_scheme_execution_inventory.v2"
        or not isinstance(catalog_rows, list)
        or not isinstance(inventory_rows, list)
    ):
        add("CCEC-INV-02", "catalog and G1 inventory must use the current v2 profile schemas")
        return errors
    catalog_ids = {
        str(row.get("scheme_id")) for row in catalog_rows if isinstance(row, dict) and row.get("scheme_id")
    }
    inventory_ids = {
        str(row.get("scheme_id")) for row in inventory_rows if isinstance(row, dict) and row.get("scheme_id")
    }
    if len(catalog_ids) != ACTIVE_ENTRY_COUNT or inventory_ids != catalog_ids:
        add("CCEC-INV-03", "G1 inventory must cover exactly the 48 active profile IDs")
    catalog_type_counts = Counter(
        str(row.get("entry_type")) for row in catalog_rows if isinstance(row, dict)
    )
    inventory_type_counts = Counter(
        str(row.get("entry_type")) for row in inventory_rows if isinstance(row, dict)
    )
    if catalog_type_counts != EXPECTED_ENTRY_TYPE_COUNTS or inventory_type_counts != EXPECTED_ENTRY_TYPE_COUNTS:
        add("CCEC-INV-04", "catalog and inventory must retain 47 MWORKS profiles plus px4ctrl")
    if {"mu_synthesis", "neural_smc"} & catalog_ids:
        add("CCEC-INV-05", "historical-only mu_synthesis and neural_smc cannot remain active catalog entries")
    catalog_by_id = {str(row.get("scheme_id")): row for row in catalog_rows if isinstance(row, dict)}
    eso = catalog_by_id.get("pid_awff_linear_eso")
    px4_catalog = catalog_by_id.get("px4ctrl")
    if not isinstance(eso, dict) or eso.get("entry_type") != "mworks_control_profile" or eso.get("execution_kind") != "planned_profile":
        add("CCEC-INV-06", "pid_awff_linear_eso must remain the planned MWORKS profile")
    if not isinstance(px4_catalog, dict) or px4_catalog.get("entry_type") != "engineering_deployment_baseline":
        add("CCEC-INV-07", "px4ctrl must remain the engineering/deployment baseline")
    semantic_categories = {
        str(row.get("category"))
        for row in catalog_rows
        if isinstance(row, dict) and row.get("entry_type") == "mworks_control_profile"
    }
    if semantic_categories != SEMANTIC_FAMILIES:
        add("CCEC-INV-08", "MWORKS profiles must occupy exactly the seven semantic controller families")

    if not isinstance(current_model_map, dict):
        add("CCEC-MAP-01", "current model entry map must be a readable object")
        return errors
    current_rows = current_model_map.get("schemes")
    if current_model_map.get("schema") != "mosim.current_model_entry_map.v1" or not isinstance(current_rows, list):
        add("CCEC-MAP-02", "current model entry map schema or scheme list is invalid")
        return errors
    current_ids = {
        str(row.get("scheme_id")) for row in current_rows if isinstance(row, dict) and row.get("scheme_id")
    }
    if len(current_ids) != ACTIVE_ENTRY_COUNT or current_ids != catalog_ids:
        add("CCEC-MAP-03", "current model entry map must cover the 48 active catalog IDs")
    state_counts = Counter(str(row.get("mapping_state")) for row in current_rows if isinstance(row, dict))
    if state_counts != EXPECTED_MAP_STATES:
        add("CCEC-MAP-04", "current map must retain the 46 + planned ESO + pending px4ctrl split")
    current_by_id = {str(row.get("scheme_id")): row for row in current_rows if isinstance(row, dict)}
    px4_map = current_by_id.get("px4ctrl")
    eso_map = current_by_id.get("pid_awff_linear_eso")
    if (
        not isinstance(px4_map, dict)
        or px4_map.get("entry_type") != "engineering_deployment_baseline"
        or px4_map.get("mapping_state") != "pending_mworks_equivalent_core"
        or px4_map.get("mworks_run_eligible") is not False
    ):
        add("CCEC-MAP-05", "px4ctrl must remain the pending MWORKS-equivalent engineering baseline")
    if (
        not isinstance(eso_map, dict)
        or eso_map.get("mapping_state") != "planned_profile_no_model"
        or eso_map.get("mworks_run_eligible") is not False
    ):
        add("CCEC-MAP-06", "pid_awff_linear_eso must remain planned without a runnable model")
    role_counts = Counter(
        str(row.get("current_model_role"))
        for row in current_rows
        if isinstance(row, dict) and row.get("mapping_state") == "resolved_current_model"
    )
    if role_counts != Counter({"graphical_controller_core": 41, "full_profile_whole_aircraft_closed_loop": 5}):
        add("CCEC-MAP-07", "resolved routes must remain 41 graphical cores plus five named whole-aircraft profiles")
    for row in current_rows:
        if not isinstance(row, dict):
            continue
        scheme_id = str(row.get("scheme_id") or "<missing>")
        state = row.get("mapping_state")
        current_file = str(row.get("current_model_file") or "")
        eligible = row.get("mworks_run_eligible")
        if state == "resolved_current_model" and not current_file.startswith("Models/"):
            add("CCEC-MAP-08", f"{scheme_id}: resolved model must live below Models/")
        if eligible is True and (state != "resolved_current_model" or not current_file.startswith("Models/")):
            add("CCEC-MAP-09", f"{scheme_id}: unresolved or non-model row cannot enable MWORKS")

    if not isinstance(formal_harness_map, dict):
        add("CCEC-HARNESS-01", "formal closed-loop harness map must be a readable object")
        return errors
    harness_rows = formal_harness_map.get("schemes")
    if formal_harness_map.get("schema") != "mosim.formal_closed_loop_harness_map.v2" or not isinstance(harness_rows, list):
        add("CCEC-HARNESS-02", "formal harness map must use the current v2 schema")
        return errors
    harness_ids = {
        str(row.get("scheme_id")) for row in harness_rows if isinstance(row, dict) and row.get("scheme_id")
    }
    if len(harness_ids) != ACTIVE_ENTRY_COUNT or harness_ids != catalog_ids:
        add("CCEC-HARNESS-03", "formal harness map must cover the 48 active profile IDs")
    harness_state_counts = Counter(
        str(row.get("formal_harness_state")) for row in harness_rows if isinstance(row, dict)
    )
    if harness_state_counts != EXPECTED_HARNESS_STATES:
        add("CCEC-HARNESS-04", "formal harness map must retain the 41 + 5 + ESO + px4ctrl state split")
    tier1_only_ids = {
        str(row.get("scheme_id"))
        for row in harness_rows
        if isinstance(row, dict)
        and row.get("whole_aircraft_tier") == "tier1_only"
        and row.get("tier2_closure_eligibility") == "excluded"
    }
    tier2_rows = [
        row for row in harness_rows
        if isinstance(row, dict) and row.get("tier2_closure_eligibility") == "included"
    ]
    tier2_current_rows = [
        row for row in tier2_rows
        if row.get("formal_harness_state")
        in {"missing_closed_loop_harness", "resolved_canonical_whole_aircraft_harness"}
    ]
    if tier1_only_ids != TIER1_ONLY_SCHEME_IDS:
        add("CCEC-HARNESS-04A", "formal harness map must identify the three approved Tier1-only profiles")
    if len(tier2_rows) != TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT or len(tier2_current_rows) != TIER2_CURRENT_MWORKS_ROUTE_COUNT:
        add("CCEC-HARNESS-04B", "formal harness Tier2 population must be 45 total and 44 current MWORKS routes")
    graphical_rows = [
        row for row in harness_rows if isinstance(row, dict) and row.get("formal_harness_state") == "missing_closed_loop_harness"
    ]
    profile_rows = [
        row for row in harness_rows if isinstance(row, dict) and row.get("formal_harness_state") == "resolved_canonical_whole_aircraft_harness"
    ]
    if len(graphical_rows) != 41 or len(profile_rows) != 5:
        add("CCEC-HARNESS-05", "formal harness map must split 46 routes into 41 graphical cores and five named whole-aircraft profiles")
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
    for row in profile_rows:
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
            add("CCEC-HARNESS-07", f"{row.get('scheme_id')}: whole-aircraft profile must retain its formal harness")
    promotion = formal_harness_map.get("champion_harness_promotion")
    if not isinstance(promotion, dict) or promotion.get("state") != "required_before_g6":
        add("CCEC-HARNESS-08", "champion formal-harness promotion gate must remain required before G6")
    if not isinstance(promotion, dict) or set(promotion.get("semantic_family_categories") or []) != SEMANTIC_FAMILIES:
        add("CCEC-HARNESS-09", "champion promotion must name the seven semantic families")
    selection = formal_harness_map.get("measured_family_selection")
    if not isinstance(selection, dict):
        add("CCEC-HARNESS-10", "measured family-selection contract is missing")
    else:
        pools = selection.get("family_pools")
        categories = {
            str(pool.get("category")) for pool in pools if isinstance(pool, dict)
        } if isinstance(pools, list) else set()
        valid_pools = (
            selection.get("schema") == "mosim.g6_measured_family_selection.v2"
            and selection.get("state") == "awaiting_phase1_minimum_closure"
            and isinstance(pools, list)
            and len(pools) == len(SEMANTIC_FAMILIES)
            and categories == SEMANTIC_FAMILIES
            and sum(int(pool.get("candidate_count") or 0) for pool in pools if isinstance(pool, dict)) == FAMILY_SCREENING_CANDIDATE_COUNT
            and all(pool.get("winner_scheme_id") is None for pool in pools if isinstance(pool, dict))
        )
        if not valid_pools:
            add("CCEC-HARNESS-11", "measured selection must retain seven unset winner pools until Phase 1 current-source records exist")
        baselines = selection.get("ab_baselines")
        official = baselines.get("official_pid") if isinstance(baselines, dict) else None
        px4_baseline = baselines.get("px4ctrl_core") if isinstance(baselines, dict) else None
        if (
            not isinstance(official, dict)
            or official.get("scheme_id") != "official_pid"
            or official.get("profile_role") != "reference_baseline"
            or not isinstance(px4_baseline, dict)
            or px4_baseline.get("scheme_id") != "px4ctrl"
            or px4_baseline.get("profile_role") != "engineering_deployment_baseline"
        ):
            add("CCEC-HARNESS-12", "Official PID and px4ctrl must remain explicit non-winner A/B baselines")

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
        "schema": "mosim.controller_evidence_closeout_contract.v2",
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
