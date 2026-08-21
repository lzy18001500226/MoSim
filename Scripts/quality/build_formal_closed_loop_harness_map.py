#!/usr/bin/env python3
"""Build and validate the formal G5 closed-loop harness map.

A current controller-core import can be opened and reviewed in MWORKS without
being a whole-aircraft simulation.  This map makes that distinction executable:
every current route names its graphical review target, while only routes with a
formal project-root whole-aircraft harness are eligible for a minimum closed-loop
claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import ROOT


CURRENT_MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
QUEUE_PATH = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "G5_GRAPHICAL_REVIEW_QUEUE.json"
)
DEFAULT_OUTPUT = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
CHAMPION_SELECTION_PATH = ROOT / "Config" / "control_platform" / "g6_champion_selection.json"
FORMAL_MODEL_PREFIX = "Models/MoSimQuadrotorModel/"
FORMAL_INTERFACE_PREFIX = "MoSimQuadrotorModel.Control.Interfaces."
FORMAL_HARNESS_MAP_SCHEMA = "mosim.formal_closed_loop_harness_map.v2"
G5_QUEUE_SCHEMA = "mosim.g5_graphical_review_queue.v2"
SYSBLOCK_DEFINITION_ROOT = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "Sysblocks"
)
CHAMPION_SELECTION_SCHEMA = "mosim.g6_measured_family_selection.v2"
ACTIVE_ENTRY_COUNT = 48
CURRENT_MWORKS_ROUTE_COUNT = 46
TIER1_ONLY_SCHEME_IDS = (
    "pid_awff_linear_eso",
    "smc_boundary_layer",
    "nmpc_outer",
)
TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT = 45
TIER2_CURRENT_MWORKS_ROUTE_COUNT = 44
FAMILY_SCREENING_CANDIDATE_COUNT = 43

CHAMPION_HARNESS_PROMOTION_CONTRACT = {
    "state": "required_before_g6",
    "semantic_family_categories": [
        "pid_family",
        "linear_robust_state_feedback",
        "nonlinear_adaptive",
        "sliding_mode",
        "optimization_predictive",
        "geometric_flatness",
        "learning",
    ],
    "selection_gate": "All 45 Tier2 whole-aircraft routes must first have current-source ClimbPath 50 s minimum-closure records before a measured family winner is selected.",
    "selection_metric": "Use the valid current-source ClimbPath 50 s position RMSE, with terminal position error and numerical stability as tie breakers. Do not rank from superseded pre-repair results.",
    "baseline_rule": "Official PID and the future MWORKS-equivalent px4ctrl_core are fixed A/B baselines, not predeclared family winners. Official PID is screened with the other 46 routes but remains excluded from the PID-family winner pool because it is the reference baseline.",
    "required_bindings": [
        "champion_core",
        "formal_adapter",
        "whole_aircraft_source_harness",
        "minimum_scenario",
        "model_hash",
        "check_model_and_minimum_closed_loop_record",
    ],
    "mapping_update_rule": "Promote the selected champion in this D2 map and update its generator/checker before any G6 seven-scenario A/B run.",
    "prohibited_substitutions": [
        "whole_aircraft_profile_from_a_different_semantic_family",
        "historical_result",
        "neighbor_route_result",
    ],
}


class HarnessMapError(ValueError):
    """Raised when a route cannot be safely classified before live MWORKS work."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise HarnessMapError(f"JSON object required: {path}")
    return value


def write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tier_policy(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the catalog-owned Tier1/Tier2 decision for every active entry."""

    policy = catalog.get("whole_aircraft_closure_policy")
    if not isinstance(policy, dict):
        raise HarnessMapError("whole-aircraft closure policy is missing from the catalog")
    tier2 = policy.get("tier2")
    if not isinstance(tier2, dict) or tier2.get("planned_route_count") != TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT:
        raise HarnessMapError("catalog Tier2 route count is invalid")
    entries = policy.get("tier1_only_profiles")
    if not isinstance(entries, list):
        raise HarnessMapError("catalog Tier1-only profile list is missing")

    tier1_only: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise HarnessMapError("catalog Tier1-only profile entry is invalid")
        scheme_id = str(entry.get("scheme_id") or "")
        reason = str(entry.get("reason") or "")
        if not scheme_id or not reason or scheme_id in tier1_only:
            raise HarnessMapError("catalog Tier1-only profile entry is incomplete or duplicated")
        tier1_only[scheme_id] = reason
    if tuple(tier1_only) != TIER1_ONLY_SCHEME_IDS:
        raise HarnessMapError("catalog Tier1-only profile IDs drift from the approved decision")

    schemes = catalog.get("schemes")
    if not isinstance(schemes, list) or len(schemes) != ACTIVE_ENTRY_COUNT:
        raise HarnessMapError("catalog must retain 48 active entries")
    result: dict[str, dict[str, Any]] = {}
    for entry in schemes:
        if not isinstance(entry, dict):
            raise HarnessMapError("catalog contains a non-object scheme")
        scheme_id = str(entry.get("scheme_id") or "")
        if not scheme_id or scheme_id in result:
            raise HarnessMapError("catalog scheme IDs are incomplete or duplicated")
        if scheme_id in tier1_only:
            if (
                entry.get("whole_aircraft_tier") != "tier1_only"
                or entry.get("tier2_closure_eligibility") != "excluded"
                or entry.get("tier2_exclusion_reason") != tier1_only[scheme_id]
            ):
                raise HarnessMapError(f"{scheme_id}: catalog Tier1-only row is incomplete")
            result[scheme_id] = {
                "whole_aircraft_tier": "tier1_only",
                "tier2_closure_eligibility": "excluded",
                "tier2_exclusion_reason": tier1_only[scheme_id],
            }
        else:
            result[scheme_id] = {
                "whole_aircraft_tier": "tier1_and_tier2",
                "tier2_closure_eligibility": "included",
                "tier2_exclusion_reason": None,
            }
    if len(result) - len(tier1_only) != TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT:
        raise HarnessMapError("catalog Tier2 population does not equal 45 routes")
    return result


def formal_file(path_text: str, label: str) -> Path:
    if not path_text.startswith(FORMAL_MODEL_PREFIX):
        raise HarnessMapError(f"{label} must stay below {FORMAL_MODEL_PREFIX}: {path_text}")
    path = ROOT / path_text
    if not path.is_file():
        raise HarnessMapError(f"{label} is missing: {path_text}")
    return path


def build_measured_family_selection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Freeze winner-selection rules without predeclaring a champion.

    The former six-row slate expressed design preferences before the 46-route
    screen existed. The active contract derives pools from the current models,
    waits for shared current-source ClimbPath records, and leaves every winner
    unset until its measured ranking is available.
    """

    selection = read_json(CHAMPION_SELECTION_PATH)
    if selection.get("schema") != CHAMPION_SELECTION_SCHEMA:
        raise HarnessMapError("G6 measured family-selection schema is invalid")
    if selection.get("state") != "awaiting_phase1_minimum_closure":
        raise HarnessMapError("G6 measured family selection must await Phase 1 minimum closure")
    expected_categories = list(CHAMPION_HARNESS_PROMOTION_CONTRACT["semantic_family_categories"])
    if selection.get("family_categories") != expected_categories:
        raise HarnessMapError("G6 family categories drift from the semantic family contract")
    metric = selection.get("selection_metric")
    if (
        not isinstance(metric, dict)
        or metric.get("scenario_id") != "climb_path_50s"
        or metric.get("duration_s") != 50
        or metric.get("primary_metric") != "position_rmse_m"
        or not isinstance(metric.get("tie_breakers"), list)
    ):
        raise HarnessMapError("G6 measured family-selection metric contract is incomplete")
    pool_policy = selection.get("pool_policy")
    if not isinstance(pool_policy, dict) or pool_policy.get("selection_eligibility") != "family_screening":
        raise HarnessMapError("G6 measured family selection must use family_screening eligibility")
    ab_baselines = selection.get("ab_baselines")
    if not isinstance(ab_baselines, dict):
        raise HarnessMapError("G6 measured family selection requires explicit A/B baselines")
    if not isinstance(ab_baselines.get("official_pid"), dict) or ab_baselines["official_pid"].get("scheme_id") != "official_pid":
        raise HarnessMapError("Official PID must remain an explicit A/B baseline")
    if not isinstance(ab_baselines.get("px4ctrl_core"), dict) or ab_baselines["px4ctrl_core"].get("scheme_id") != "px4ctrl":
        raise HarnessMapError("px4ctrl_core must remain an explicit A/B baseline")

    current_rows = [
        row
        for row in rows
        if row.get("formal_harness_state")
        in {"missing_closed_loop_harness", "resolved_canonical_whole_aircraft_harness"}
    ]
    if len(current_rows) != CURRENT_MWORKS_ROUTE_COUNT:
        raise HarnessMapError("G6 measured family selection requires exactly 46 current MWORKS routes")
    tier2_current_rows = [
        row for row in current_rows if row.get("tier2_closure_eligibility") == "included"
    ]
    if len(tier2_current_rows) != TIER2_CURRENT_MWORKS_ROUTE_COUNT:
        raise HarnessMapError("G6 measured family selection requires 44 Tier2 current MWORKS routes")
    if (
        pool_policy.get("eligible_current_mworks_route_count")
        != FAMILY_SCREENING_CANDIDATE_COUNT
        or pool_policy.get("tier2_whole_aircraft_route_count")
        != TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT
        or tuple(pool_policy.get("tier1_only_scheme_ids") or ()) != TIER1_ONLY_SCHEME_IDS
    ):
        raise HarnessMapError("G6 pool policy drifts from the approved Tier1/Tier2 decision")
    pools: list[dict[str, Any]] = []
    candidate_ids: list[str] = []
    for category in expected_categories:
        pool_ids = sorted(
            str(row["scheme_id"])
            for row in tier2_current_rows
            if row.get("category") == category
            and row.get("selection_eligibility") == "family_screening"
        )
        if not pool_ids:
            raise HarnessMapError(f"{category}: measured family-selection pool is empty")
        candidate_ids.extend(pool_ids)
        pools.append(
            {
                "category": category,
                "candidate_scheme_ids": pool_ids,
                "candidate_count": len(pool_ids),
                "winner_scheme_id": None,
                "winner_selection_state": "awaiting_all_current_source_phase1_records",
            }
        )
    if len(set(candidate_ids)) != len(candidate_ids):
        raise HarnessMapError("G6 measured family-selection pools overlap")
    if "official_pid" in candidate_ids:
        raise HarnessMapError("Official PID must remain the fixed A/B baseline, not a family-winner candidate")
    if len(candidate_ids) != FAMILY_SCREENING_CANDIDATE_COUNT:
        raise HarnessMapError("G6 measured family-selection pool must contain 43 candidates")
    return {
        "schema": CHAMPION_SELECTION_SCHEMA,
        "state": "awaiting_phase1_minimum_closure",
        "selection_metric": metric,
        "pool_policy": pool_policy,
        "ab_baselines": ab_baselines,
        "family_pools": pools,
        "summary": {
            "semantic_family_count": len(pools),
            "family_screening_candidate_count": len(candidate_ids),
            "selected_family_winner_count": 0,
            "current_mworks_route_count": len(current_rows),
            "tier2_current_mworks_route_count": len(tier2_current_rows),
            "tier2_whole_aircraft_route_count": TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT,
            "tier1_only_profile_count": len(TIER1_ONLY_SCHEME_IDS),
            "official_pid_baseline_count": 1,
            "px4ctrl_core_baseline_count": 1,
        },
    }


def review_target(queue_row: dict[str, Any], scheme_id: str) -> dict[str, Any]:
    target = queue_row.get("review_target")
    if not isinstance(target, dict):
        raise HarnessMapError(f"{scheme_id}: G5 review target is missing")
    target_file = target.get("model_file")
    if not isinstance(target_file, str) or not target_file:
        raise HarnessMapError(f"{scheme_id}: G5 review target file is missing")
    formal_file(target_file, f"{scheme_id}: G5 review target")
    return target


def model_within(model_path: Path, scheme_id: str) -> str:
    within_match = re.search(
        r"^\s*within\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*;",
        model_path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not within_match:
        raise HarnessMapError(f"{scheme_id}: model has no within clause: {model_path}")
    return within_match.group(1)


def whole_aircraft_sysblock_load_prerequisites(source_path: Path, scheme_id: str) -> list[dict[str, Any]]:
    """Resolve the ordered definitions needed by an aircraft source's controller.

    G5 selects a graphical review target, which can be a wrapper of the real
    class.  Whole-aircraft compilation instead depends on the type named in
    the source model itself. A legacy unqualified source declaration needs its
    true Sysblock definition followed by a local namespace compatibility alias;
    a qualified declaration needs only the true definition. This keeps clean
    MWORKS execution independent of package-load side effects.
    """
    source_text = source_path.read_text(encoding="utf-8")
    type_matches = re.findall(
        r"^\s*((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)\s+"
        r"(controller3_2|controller_core|controller|core)"
        r"(?:\s*\([^;]*\))?"
        r"(?:\s+annotation\([^;]*\))?\s*;",
        source_text,
        flags=re.MULTILINE,
    )
    if len(type_matches) != 1:
        raise HarnessMapError(
            f"{scheme_id}: expected exactly one controller component type in {source_path.name}, found {type_matches}"
        )
    declared_type, source_component = type_matches[0]
    controller_type = declared_type.rsplit(".", 1)[-1]
    if "." in declared_type and declared_type.startswith("MoSimQuadrotorModel."):
        model_path = ROOT / "Models" / Path(*declared_type.split("."))
        model_path = model_path.with_suffix(".mo")
        if model_path.is_file():
            model_class = declared_type
            return [
                {
                    "role": "project_controller_definition",
                    "source_component": source_component,
                    "source_declared_type": declared_type,
                    "model_file": str(model_path.relative_to(ROOT)).replace("\\", "/"),
                    "model_class": model_class,
                    "model_sha256": sha256_file(model_path),
                }
            ]
    if not SYSBLOCK_DEFINITION_ROOT.is_dir():
        raise HarnessMapError(f"{scheme_id}: Sysblock definition root is missing: {SYSBLOCK_DEFINITION_ROOT}")
    declaration = re.compile(rf"^\s*(?:model|block)\s+{re.escape(controller_type)}\b", re.MULTILINE)
    matches = [
        candidate
        for candidate in SYSBLOCK_DEFINITION_ROOT.rglob("*.mo")
        if candidate.name != "package.mo" and declaration.search(candidate.read_text(encoding="utf-8"))
    ]
    if len(matches) != 1:
        found = [str(candidate.relative_to(ROOT)).replace("\\", "/") for candidate in matches]
        raise HarnessMapError(
            f"{scheme_id}: expected one definition for {controller_type}, found {found}"
        )
    model_path = matches[0]
    model_class = f"{model_within(model_path, scheme_id)}.{controller_type}"
    if "." in declared_type and declared_type != model_class:
        raise HarnessMapError(
            f"{scheme_id}: controller3_2 declares {declared_type}, but its definition is {model_class}"
        )
    definition = {
        "role": "embedded_sysblock_definition",
        "source_component": source_component,
        "source_declared_type": declared_type,
        "model_file": str(model_path.relative_to(ROOT)).replace("\\", "/"),
        "model_class": model_class,
        "model_sha256": sha256_file(model_path),
    }
    if "." in declared_type:
        return [definition]

    alias_path = source_path.parent / f"{controller_type}.mo"
    if not alias_path.is_file():
        raise HarnessMapError(
            f"{scheme_id}: unqualified {controller_type} needs a namespace compatibility alias: {alias_path}"
        )
    source_namespace = model_within(source_path, scheme_id)
    if model_within(alias_path, scheme_id) != source_namespace:
        raise HarnessMapError(f"{scheme_id}: compatibility alias leaves source namespace: {alias_path}")
    alias_text = alias_path.read_text(encoding="utf-8")
    alias_declaration = re.compile(rf"^\s*model\s+{re.escape(controller_type)}\b", re.MULTILINE)
    if not alias_declaration.search(alias_text):
        raise HarnessMapError(f"{scheme_id}: compatibility alias has the wrong model declaration: {alias_path}")
    extends_pattern = re.compile(rf"\bextends\s+{re.escape(model_class)}\s*;", re.MULTILINE)
    if not extends_pattern.search(alias_text):
        raise HarnessMapError(f"{scheme_id}: compatibility alias does not extend {model_class}: {alias_path}")
    alias = {
        "role": "namespace_compatibility_alias",
        "source_component": source_component,
        "source_declared_type": declared_type,
        "model_file": str(alias_path.relative_to(ROOT)).replace("\\", "/"),
        "model_class": f"{source_namespace}.{controller_type}",
        "model_sha256": sha256_file(alias_path),
        "base_model_class": model_class,
    }
    return [definition, alias]


def has_formal_runner_interface(model_path: Path) -> bool:
    text = model_path.read_text(encoding="utf-8")
    return bool(
        re.search(
            rf"\bextends\s+{re.escape(FORMAL_INTERFACE_PREFIX)}[A-Za-z_]\w*\b",
            text,
        )
    )


def common_row(
    map_row: dict[str, Any], queue_row: dict[str, Any], tier: dict[str, Any]
) -> dict[str, Any]:
    scheme_id = str(map_row["scheme_id"])
    return {
        "scheme_id": scheme_id,
        "display_name_zh": map_row.get("display_name_zh"),
        "category": map_row.get("category"),
        "entry_type": map_row.get("entry_type"),
        "profile_role": map_row.get("role"),
        "selection_eligibility": map_row.get("selection_eligibility"),
        "execution_kind": map_row.get("execution_kind"),
        "mapping_state": map_row.get("mapping_state"),
        "current_model_role": map_row.get("current_model_role"),
        "current_model_file": map_row.get("current_model_file"),
        "current_model_class": map_row.get("current_model_class"),
        "current_model_sha256": map_row.get("current_model_sha256"),
        "topology_review_target": review_target(queue_row, scheme_id),
        **tier,
    }


def graphical_core_row(
    map_row: dict[str, Any], queue_row: dict[str, Any], tier: dict[str, Any]
) -> dict[str, Any]:
    row = common_row(map_row, queue_row, tier)
    scheme_id = str(row["scheme_id"])
    model_file = str(row["current_model_file"])
    model_path = formal_file(model_file, f"{scheme_id}: graphical core")
    if has_formal_runner_interface(model_path):
        raise HarnessMapError(
            f"{scheme_id}: graphical-core role unexpectedly implements a formal ExperimentRunner interface"
        )
    row.update(
        {
            "formal_harness_state": "missing_closed_loop_harness",
            "minimum_whole_aircraft_closure_eligible": False,
            "canonical_closed_loop_harness": None,
            "formal_adapter": None,
            "internal_probe": {
                "model_file": model_file,
                "model_class": row["current_model_class"],
                "probe_kind": "fixed_input_graphical_internal_response",
                "claim_boundary": (
                    "This source-derived GraphicalMIL model may be opened, inspected, "
                    "and simulated for its own fixed-input internal response. It is not "
                    "a plant-coupled whole-aircraft closed-loop result."
                ),
            },
            "reason": (
                "The formal current model is a graphical controller core and does not "
                "implement an ExperimentRunner controller interface or name a canonical "
                "whole-aircraft harness."
            ),
        }
    )
    return row


def full_profile_row(
    map_row: dict[str, Any], queue_row: dict[str, Any], tier: dict[str, Any]
) -> dict[str, Any]:
    row = common_row(map_row, queue_row, tier)
    scheme_id = str(row["scheme_id"])
    public_entry = formal_file(str(row["current_model_file"]), f"{scheme_id}: formal public entry")
    provenance = map_row.get("source_provenance")
    if not isinstance(provenance, dict):
        raise HarnessMapError(f"{scheme_id}: full-profile source provenance is missing")
    source_file = provenance.get("source_file")
    source_class = provenance.get("source_model_class")
    source_hash = provenance.get("source_sha256")
    if not isinstance(source_file, str) or not isinstance(source_class, str) or not isinstance(source_hash, str):
        raise HarnessMapError(f"{scheme_id}: full-profile source provenance is incomplete")
    source_path = formal_file(source_file, f"{scheme_id}: whole-aircraft source")
    if sha256_file(source_path) != source_hash:
        raise HarnessMapError(f"{scheme_id}: whole-aircraft source hash drift")
    prerequisites = whole_aircraft_sysblock_load_prerequisites(source_path, scheme_id)
    row.update(
        {
            "formal_harness_state": "resolved_canonical_whole_aircraft_harness",
            "minimum_whole_aircraft_closure_eligible": True,
            "canonical_closed_loop_harness": {
                "public_entry_file": str(row["current_model_file"]),
                "public_entry_class": row["current_model_class"],
                "public_entry_sha256": sha256_file(public_entry),
                "whole_aircraft_source_file": source_file,
                "whole_aircraft_source_class": source_class,
                "whole_aircraft_source_sha256": source_hash,
                "binding_kind": "formal_public_alias_extends_project_root_whole_aircraft_model",
            },
            "formal_adapter": {
                "kind": "embedded_sysblock_and_physical_plant",
                "claim_boundary": (
                    "The route is eligible for a real MWORKS whole-aircraft minimum "
                    "closure only through this named formal alias/source pair."
                ),
            },
            "model_load_prerequisites": prerequisites,
            "internal_probe": None,
        }
    )
    return row


def planned_profile_row(map_row: dict[str, Any], tier: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_id": map_row["scheme_id"],
        "display_name_zh": map_row.get("display_name_zh"),
        "category": map_row.get("category"),
        "entry_type": map_row.get("entry_type"),
        "profile_role": map_row.get("role"),
        "selection_eligibility": map_row.get("selection_eligibility"),
        "execution_kind": map_row.get("execution_kind"),
        "mapping_state": map_row.get("mapping_state"),
        "formal_harness_state": "planned_profile_no_model",
        "minimum_whole_aircraft_closure_eligible": False,
        "blocker_code": map_row.get("blocker_code"),
        "blocker_reason": map_row.get("blocker_reason"),
        **tier,
    }


def pending_mworks_equivalent_core_row(map_row: dict[str, Any], tier: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_id": map_row["scheme_id"],
        "display_name_zh": map_row.get("display_name_zh"),
        "category": map_row.get("category"),
        "entry_type": map_row.get("entry_type"),
        "profile_role": map_row.get("role"),
        "selection_eligibility": map_row.get("selection_eligibility"),
        "execution_kind": map_row.get("execution_kind"),
        "mapping_state": map_row.get("mapping_state"),
        "formal_harness_state": "pending_mworks_equivalent_core",
        "minimum_whole_aircraft_closure_eligible": False,
        "claim_boundary": "px4ctrl remains the engineering/deployment baseline. Its MWORKS-equivalent core, graphical review, and formal A/B entry are pending an explicit C++ behavior/interface-equivalence gate.",
        **tier,
    }


def build_harness_map() -> dict[str, Any]:
    current_map = read_json(CURRENT_MAP_PATH)
    catalog = read_json(CATALOG_PATH)
    tiers = tier_policy(catalog)
    queue = read_json(QUEUE_PATH)
    if current_map.get("schema") != "mosim.current_model_entry_map.v1":
        raise HarnessMapError("Current model entry map schema is invalid")
    if queue.get("schema") != G5_QUEUE_SCHEMA:
        raise HarnessMapError("G5 graphical review queue schema is invalid")
    map_rows = current_map.get("schemes")
    queue_rows = queue.get("schemes")
    if not isinstance(map_rows, list) or len(map_rows) != ACTIVE_ENTRY_COUNT:
        raise HarnessMapError("Current model entry map must contain 48 active profiles")
    if not isinstance(queue_rows, list) or len(queue_rows) != ACTIVE_ENTRY_COUNT:
        raise HarnessMapError("G5 graphical review queue must contain 48 active profiles")
    queue_by_id = {
        str(row.get("scheme_id")): row
        for row in queue_rows
        if isinstance(row, dict) and row.get("scheme_id")
    }
    if len(queue_by_id) != ACTIVE_ENTRY_COUNT:
        raise HarnessMapError("G5 graphical review queue has duplicate or missing active profile IDs")

    rows: list[dict[str, Any]] = []
    for map_row in map_rows:
        if not isinstance(map_row, dict):
            raise HarnessMapError("Current model entry map contains a non-object row")
        scheme_id = str(map_row.get("scheme_id") or "")
        state = map_row.get("mapping_state")
        role = map_row.get("current_model_role")
        queue_row = queue_by_id.get(scheme_id)
        tier = tiers.get(scheme_id)
        if not isinstance(tier, dict):
            raise HarnessMapError(f"{scheme_id}: missing catalog Tier1/Tier2 policy")
        if state == "resolved_current_model" and not isinstance(queue_row, dict):
            raise HarnessMapError(f"{scheme_id}: missing G5 queue row")
        if state == "resolved_current_model" and role == "graphical_controller_core":
            rows.append(graphical_core_row(map_row, queue_row, tier))
        elif state == "resolved_current_model" and role == "full_profile_whole_aircraft_closed_loop":
            rows.append(full_profile_row(map_row, queue_row, tier))
        elif state == "planned_profile_no_model":
            rows.append(planned_profile_row(map_row, tier))
        elif state == "pending_mworks_equivalent_core":
            rows.append(pending_mworks_equivalent_core_row(map_row, tier))
        else:
            raise HarnessMapError(f"{scheme_id}: unsupported mapping state/role: {state}/{role}")

    state_counts = Counter(str(row["formal_harness_state"]) for row in rows)
    measured_selection = build_measured_family_selection(rows)
    measured_summary = measured_selection["summary"]
    return {
        "schema": FORMAL_HARNESS_MAP_SCHEMA,
        "scope": (
            "D2 static formal-harness mapping and measured-winner selection contract "
            "only. It does not prove a MWORKS check, graphical review, simulation, "
            "result, metric, code-generation, or runtime success."
        ),
        "source_current_model_map": "Config/control_platform/current_model_entry_map.json",
        "source_current_model_map_sha256": sha256_file(CURRENT_MAP_PATH),
        "source_control_scheme_catalog": "Config/control_platform/control_scheme_catalog.json",
        "source_control_scheme_catalog_sha256": sha256_file(CATALOG_PATH),
        "source_g5_graphical_review_queue": (
            "Results/control_platform/g5_graphical_structure_review_20260722/"
            "G5_GRAPHICAL_REVIEW_QUEUE.json"
        ),
        "source_g5_graphical_review_queue_sha256": sha256_file(QUEUE_PATH),
        "source_g6_champion_selection": str(CHAMPION_SELECTION_PATH.relative_to(ROOT)).replace("\\", "/"),
        "source_g6_champion_selection_sha256": sha256_file(CHAMPION_SELECTION_PATH),
        "summary": {
            "active_top_level_entry_count": len(rows),
            "current_mworks_route_count": (
                state_counts["missing_closed_loop_harness"]
                + state_counts["resolved_canonical_whole_aircraft_harness"]
            ),
            "resolved_canonical_whole_aircraft_harness_count": state_counts[
                "resolved_canonical_whole_aircraft_harness"
            ],
            "missing_closed_loop_harness_count": state_counts["missing_closed_loop_harness"],
            "planned_profile_no_model_count": state_counts["planned_profile_no_model"],
            "pending_mworks_equivalent_core_count": state_counts["pending_mworks_equivalent_core"],
            "tier1_only_profile_count": len(TIER1_ONLY_SCHEME_IDS),
            "tier2_whole_aircraft_route_count": sum(
                row.get("tier2_closure_eligibility") == "included" for row in rows
            ),
            "tier2_current_mworks_route_count": sum(
                row.get("tier2_closure_eligibility") == "included"
                and row.get("formal_harness_state")
                in {"missing_closed_loop_harness", "resolved_canonical_whole_aircraft_harness"}
                for row in rows
            ),
            "semantic_family_count": measured_summary["semantic_family_count"],
            "family_screening_candidate_count": measured_summary["family_screening_candidate_count"],
            "selected_family_winner_count": measured_summary["selected_family_winner_count"],
            "official_pid_baseline_count": measured_summary["official_pid_baseline_count"],
            "px4ctrl_core_baseline_count": measured_summary["px4ctrl_core_baseline_count"],
        },
        "champion_harness_promotion": CHAMPION_HARNESS_PROMOTION_CONTRACT,
        "measured_family_selection": measured_selection,
        "schemes": rows,
    }


def validate_harness_map(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("schema") != FORMAL_HARNESS_MAP_SCHEMA:
        errors.append("schema is invalid")
    rows = value.get("schemes")
    if not isinstance(rows, list) or len(rows) != ACTIVE_ENTRY_COUNT:
        errors.append("map must contain exactly 48 active profiles")
        return errors
    identifiers = [str(row.get("scheme_id")) for row in rows if isinstance(row, dict)]
    if len(identifiers) != ACTIVE_ENTRY_COUNT or len(set(identifiers)) != ACTIVE_ENTRY_COUNT:
        errors.append("scheme IDs must be complete and unique")
    by_id = {str(row.get("scheme_id")): row for row in rows if isinstance(row, dict)}
    for scheme_id in ("mu_synthesis", "neural_smc"):
        if scheme_id in by_id:
            errors.append(f"{scheme_id} must not remain in the active formal-harness map")
    if by_id.get("pid_awff_linear_eso", {}).get("formal_harness_state") != "planned_profile_no_model":
        errors.append("ESO profile must remain planned_profile_no_model until a MWORKS implementation exists")
    if by_id.get("px4ctrl", {}).get("formal_harness_state") != "pending_mworks_equivalent_core":
        errors.append("px4ctrl must remain pending_mworks_equivalent_core")
    tier1_only_ids = {
        scheme_id
        for scheme_id, row in by_id.items()
        if row.get("whole_aircraft_tier") == "tier1_only"
        and row.get("tier2_closure_eligibility") == "excluded"
        and isinstance(row.get("tier2_exclusion_reason"), str)
    }
    if tier1_only_ids != set(TIER1_ONLY_SCHEME_IDS):
        errors.append("Tier1-only profile set must match the approved three-route decision")
    tier2_rows = [
        row for row in rows if isinstance(row, dict) and row.get("tier2_closure_eligibility") == "included"
    ]
    if len(tier2_rows) != TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT:
        errors.append("Tier2 whole-aircraft population must equal 45 routes")

    candidates = [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("formal_harness_state")
        in {"missing_closed_loop_harness", "resolved_canonical_whole_aircraft_harness"}
    ]
    graphical = [row for row in candidates if row.get("formal_harness_state") == "missing_closed_loop_harness"]
    integrated = [
        row
        for row in candidates
        if row.get("formal_harness_state") == "resolved_canonical_whole_aircraft_harness"
    ]
    if len(candidates) != CURRENT_MWORKS_ROUTE_COUNT or len(graphical) != 41 or len(integrated) != 5:
        errors.append("current-route split must remain 46 = 41 graphical cores + 5 full-profile whole-aircraft harnesses")
    for row in candidates:
        target = row.get("topology_review_target")
        if not isinstance(target, dict) or not isinstance(target.get("model_file"), str):
            errors.append(f"{row.get('scheme_id')}: topology review target is missing")
        elif not str(target["model_file"]).startswith(FORMAL_MODEL_PREFIX):
            errors.append(f"{row.get('scheme_id')}: topology review target leaves formal model root")
    for row in graphical:
        if row.get("minimum_whole_aircraft_closure_eligible") is not False:
            errors.append(f"{row.get('scheme_id')}: graphical core cannot enable minimum whole-aircraft closure")
        if row.get("canonical_closed_loop_harness") is not None:
            errors.append(f"{row.get('scheme_id')}: graphical core cannot declare a formal harness")
        if not isinstance(row.get("internal_probe"), dict):
            errors.append(f"{row.get('scheme_id')}: graphical core must retain its internal-probe boundary")
    for row in integrated:
        harness = row.get("canonical_closed_loop_harness")
        if row.get("minimum_whole_aircraft_closure_eligible") is not True:
            errors.append(f"{row.get('scheme_id')}: full profile must enable minimum whole-aircraft closure")
        if not isinstance(harness, dict):
            errors.append(f"{row.get('scheme_id')}: full profile must declare a canonical harness")
        else:
            for key in ("public_entry_file", "whole_aircraft_source_file"):
                path_text = harness.get(key)
                if not isinstance(path_text, str) or not path_text.startswith(FORMAL_MODEL_PREFIX):
                    errors.append(f"{row.get('scheme_id')}: harness {key} leaves formal model root")
        prerequisites = row.get("model_load_prerequisites")
        if not isinstance(prerequisites, list) or not prerequisites or any(not isinstance(item, dict) for item in prerequisites):
            errors.append(f"{row.get('scheme_id')}: full profile needs frozen load prerequisites")
        else:
            prerequisite = prerequisites[0]
            if not isinstance(harness, dict):
                continue
            source_file = harness.get("whole_aircraft_source_file")
            if not isinstance(source_file, str):
                errors.append(f"{row.get('scheme_id')}: full profile has no source for its prerequisite")
                continue
            try:
                expected_prerequisites = whole_aircraft_sysblock_load_prerequisites(
                    formal_file(source_file, f"{row.get('scheme_id')}: whole-aircraft source"),
                    str(row.get("scheme_id")),
                )
            except HarnessMapError as exc:
                errors.append(str(exc))
                continue
            if len(prerequisites) != len(expected_prerequisites):
                errors.append(f"{row.get('scheme_id')}: frozen prerequisite count does not match its source controller type")
                continue
            for index, (prerequisite, expected_prerequisite) in enumerate(zip(prerequisites, expected_prerequisites)):
                for key in (
                    "role",
                    "source_component",
                    "source_declared_type",
                    "model_file",
                    "model_class",
                    "model_sha256",
                    "base_model_class",
                ):
                    if prerequisite.get(key) != expected_prerequisite.get(key):
                        errors.append(
                            f"{row.get('scheme_id')}: load prerequisite {index} {key} must bind its source controller type"
                        )
    expected_summary = {
        "active_top_level_entry_count": ACTIVE_ENTRY_COUNT,
        "current_mworks_route_count": CURRENT_MWORKS_ROUTE_COUNT,
        "resolved_canonical_whole_aircraft_harness_count": 5,
        "missing_closed_loop_harness_count": 41,
        "planned_profile_no_model_count": 1,
        "pending_mworks_equivalent_core_count": 1,
        "semantic_family_count": 7,
        "tier1_only_profile_count": len(TIER1_ONLY_SCHEME_IDS),
        "tier2_whole_aircraft_route_count": TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT,
        "tier2_current_mworks_route_count": TIER2_CURRENT_MWORKS_ROUTE_COUNT,
        "family_screening_candidate_count": FAMILY_SCREENING_CANDIDATE_COUNT,
        "selected_family_winner_count": 0,
        "official_pid_baseline_count": 1,
        "px4ctrl_core_baseline_count": 1,
    }
    summary = value.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary is missing")
    else:
        for key, expected in expected_summary.items():
            if summary.get(key) != expected:
                errors.append(f"summary.{key} must equal {expected}")
    if value.get("champion_harness_promotion") != CHAMPION_HARNESS_PROMOTION_CONTRACT:
        errors.append("champion formal-harness promotion contract is missing or has drifted")
    measured = value.get("measured_family_selection")
    if not isinstance(measured, dict):
        errors.append("measured family selection is missing")
        return errors
    if measured.get("schema") != CHAMPION_SELECTION_SCHEMA:
        errors.append("measured family selection schema is invalid")
    if measured.get("state") != "awaiting_phase1_minimum_closure":
        errors.append("measured family selection must await the current-source Phase 1 screen")
    expected_categories = list(CHAMPION_HARNESS_PROMOTION_CONTRACT["semantic_family_categories"])
    pools = measured.get("family_pools")
    if not isinstance(pools, list) or len(pools) != len(expected_categories):
        errors.append("measured family selection must contain seven semantic-family pools")
    else:
        pool_categories = [str(pool.get("category")) for pool in pools if isinstance(pool, dict)]
        if pool_categories != expected_categories:
            errors.append("measured family-selection pools must preserve the seven-family order")
        pooled_ids: list[str] = []
        for pool in pools:
            if not isinstance(pool, dict):
                errors.append("measured family selection contains a non-object pool")
                continue
            category = str(pool.get("category"))
            actual_ids = pool.get("candidate_scheme_ids")
            expected_ids = sorted(
                scheme_id
                for scheme_id, row in by_id.items()
                if row.get("category") == category
                and row.get("selection_eligibility") == "family_screening"
                and row.get("formal_harness_state")
                in {"missing_closed_loop_harness", "resolved_canonical_whole_aircraft_harness"}
                and row.get("tier2_closure_eligibility") == "included"
            )
            if not isinstance(actual_ids, list) or actual_ids != expected_ids:
                errors.append(f"{category}: measured family-selection pool does not match current eligible routes")
                continue
            if pool.get("candidate_count") != len(actual_ids):
                errors.append(f"{category}: candidate count does not match its pool")
            if pool.get("winner_scheme_id") is not None:
                errors.append(f"{category}: winner cannot be predeclared before current-source Phase 1")
            if pool.get("winner_selection_state") != "awaiting_all_current_source_phase1_records":
                errors.append(f"{category}: winner selection state is invalid")
            pooled_ids.extend(str(item) for item in actual_ids)
        if len(pooled_ids) != FAMILY_SCREENING_CANDIDATE_COUNT or len(set(pooled_ids)) != FAMILY_SCREENING_CANDIDATE_COUNT:
            errors.append("measured family-selection pools must contain 43 unique eligible routes")
        if "official_pid" in pooled_ids:
            errors.append("Official PID must remain an A/B baseline outside the family-winner pool")
    baselines = measured.get("ab_baselines")
    if not isinstance(baselines, dict):
        errors.append("measured family selection requires explicit A/B baselines")
    else:
        official = baselines.get("official_pid")
        px4ctrl = baselines.get("px4ctrl_core")
        if not isinstance(official, dict) or official.get("scheme_id") != "official_pid":
            errors.append("Official PID A/B baseline is invalid")
        if not isinstance(px4ctrl, dict) or px4ctrl.get("scheme_id") != "px4ctrl":
            errors.append("px4ctrl_core A/B baseline is invalid")
    measured_summary = measured.get("summary")
    if not isinstance(measured_summary, dict):
        errors.append("measured family-selection summary is missing")
    else:
        for key, expected in {
            "semantic_family_count": 7,
            "family_screening_candidate_count": FAMILY_SCREENING_CANDIDATE_COUNT,
            "selected_family_winner_count": 0,
            "current_mworks_route_count": CURRENT_MWORKS_ROUTE_COUNT,
            "tier2_current_mworks_route_count": TIER2_CURRENT_MWORKS_ROUTE_COUNT,
            "tier2_whole_aircraft_route_count": TIER2_WHOLE_AIRCRAFT_ROUTE_COUNT,
            "tier1_only_profile_count": len(TIER1_ONLY_SCHEME_IDS),
            "official_pid_baseline_count": 1,
            "px4ctrl_core_baseline_count": 1,
        }.items():
            if measured_summary.get(key) != expected:
                errors.append(f"measured family-selection summary.{key} must equal {expected}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the on-disk map differs from the deterministic build",
    )
    args = parser.parse_args(argv)
    try:
        expected = build_harness_map()
        errors = validate_harness_map(expected)
        output = args.output if args.output.is_absolute() else ROOT / args.output
        if args.check:
            if not output.is_file():
                errors.append(f"map is missing: {output}")
            else:
                current = read_json(output)
                if current != expected:
                    errors.append("on-disk harness map differs from deterministic build")
        else:
            write_utf8_lf(output, canonical_json(expected))
    except Exception as exc:
        errors = [str(exc)]
        expected = {}
    report = {
        "schema": "mosim.formal_closed_loop_harness_map_check.v2",
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "output": str(args.output),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
