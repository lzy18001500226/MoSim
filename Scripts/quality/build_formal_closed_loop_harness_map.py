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
QUEUE_PATH = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "G5_GRAPHICAL_REVIEW_QUEUE.json"
)
DEFAULT_OUTPUT = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
FORMAL_MODEL_PREFIX = "Models/MoSimQuadrotorModel/"
FORMAL_INTERFACE_PREFIX = "MoSimQuadrotorModel.ExperimentRunner.Interfaces."

CHAMPION_HARNESS_PROMOTION_CONTRACT = {
    "state": "required_before_g6",
    "nominal_family_categories": [
        "pid_family",
        "classic_robust",
        "sliding_mode",
        "optimization",
        "geometric_flatness",
        "learning",
    ],
    "baseline_rule": "Official PID must use a version-matched formal-root harness; it may be reused only when it is also the selected PID-family champion.",
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
        "existing_fixed_integrated_chain_for_different_champion",
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


def formal_file(path_text: str, label: str) -> Path:
    if not path_text.startswith(FORMAL_MODEL_PREFIX):
        raise HarnessMapError(f"{label} must stay below {FORMAL_MODEL_PREFIX}: {path_text}")
    path = ROOT / path_text
    if not path.is_file():
        raise HarnessMapError(f"{label} is missing: {path_text}")
    return path


def review_target(queue_row: dict[str, Any], scheme_id: str) -> dict[str, Any]:
    target = queue_row.get("review_target")
    if not isinstance(target, dict):
        raise HarnessMapError(f"{scheme_id}: G5 review target is missing")
    target_file = target.get("model_file")
    if not isinstance(target_file, str) or not target_file:
        raise HarnessMapError(f"{scheme_id}: G5 review target file is missing")
    formal_file(target_file, f"{scheme_id}: G5 review target")
    return target


def has_formal_runner_interface(model_path: Path) -> bool:
    text = model_path.read_text(encoding="utf-8")
    return bool(
        re.search(
            rf"\bextends\s+{re.escape(FORMAL_INTERFACE_PREFIX)}[A-Za-z_]\w*\b",
            text,
        )
    )


def common_row(map_row: dict[str, Any], queue_row: dict[str, Any]) -> dict[str, Any]:
    scheme_id = str(map_row["scheme_id"])
    return {
        "scheme_id": scheme_id,
        "display_name_zh": map_row.get("display_name_zh"),
        "category": map_row.get("category"),
        "entry_type": map_row.get("entry_type"),
        "mapping_state": map_row.get("mapping_state"),
        "current_model_role": map_row.get("current_model_role"),
        "current_model_file": map_row.get("current_model_file"),
        "current_model_class": map_row.get("current_model_class"),
        "current_model_sha256": map_row.get("current_model_sha256"),
        "topology_review_target": review_target(queue_row, scheme_id),
    }


def graphical_core_row(map_row: dict[str, Any], queue_row: dict[str, Any]) -> dict[str, Any]:
    row = common_row(map_row, queue_row)
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


def fixed_integrated_row(map_row: dict[str, Any], queue_row: dict[str, Any]) -> dict[str, Any]:
    row = common_row(map_row, queue_row)
    scheme_id = str(row["scheme_id"])
    public_entry = formal_file(str(row["current_model_file"]), f"{scheme_id}: formal public entry")
    provenance = map_row.get("source_provenance")
    if not isinstance(provenance, dict):
        raise HarnessMapError(f"{scheme_id}: fixed integrated source provenance is missing")
    source_file = provenance.get("source_file")
    source_class = provenance.get("source_model_class")
    source_hash = provenance.get("source_sha256")
    if not isinstance(source_file, str) or not isinstance(source_class, str) or not isinstance(source_hash, str):
        raise HarnessMapError(f"{scheme_id}: fixed integrated source provenance is incomplete")
    source_path = formal_file(source_file, f"{scheme_id}: whole-aircraft source")
    if sha256_file(source_path) != source_hash:
        raise HarnessMapError(f"{scheme_id}: whole-aircraft source hash drift")
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
            "internal_probe": None,
        }
    )
    return row


def blocked_row(map_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_id": map_row["scheme_id"],
        "display_name_zh": map_row.get("display_name_zh"),
        "category": map_row.get("category"),
        "entry_type": map_row.get("entry_type"),
        "mapping_state": map_row.get("mapping_state"),
        "formal_harness_state": "blocked_before_harness_mapping",
        "minimum_whole_aircraft_closure_eligible": False,
        "blocker_code": map_row.get("blocker_code"),
        "blocker_reason": map_row.get("blocker_reason"),
    }


def runtime_baseline_row(map_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_id": map_row["scheme_id"],
        "display_name_zh": map_row.get("display_name_zh"),
        "category": map_row.get("category"),
        "entry_type": map_row.get("entry_type"),
        "mapping_state": map_row.get("mapping_state"),
        "formal_harness_state": "not_applicable_runtime_baseline",
        "minimum_whole_aircraft_closure_eligible": False,
        "claim_boundary": "px4ctrl remains a ROS1/PX4 runtime baseline and has no MWORKS graphical harness.",
    }


def build_harness_map() -> dict[str, Any]:
    current_map = read_json(CURRENT_MAP_PATH)
    queue = read_json(QUEUE_PATH)
    if current_map.get("schema") != "mosim.current_model_entry_map.v1":
        raise HarnessMapError("Current model entry map schema is invalid")
    if queue.get("schema") != "mosim.g5_graphical_review_queue.v1":
        raise HarnessMapError("G5 graphical review queue schema is invalid")
    map_rows = current_map.get("schemes")
    queue_rows = queue.get("schemes")
    if not isinstance(map_rows, list) or len(map_rows) != 49:
        raise HarnessMapError("Current model entry map must contain 49 schemes")
    if not isinstance(queue_rows, list) or len(queue_rows) != 49:
        raise HarnessMapError("G5 graphical review queue must contain 49 schemes")
    queue_by_id = {
        str(row.get("scheme_id")): row
        for row in queue_rows
        if isinstance(row, dict) and row.get("scheme_id")
    }
    if len(queue_by_id) != 49:
        raise HarnessMapError("G5 graphical review queue has duplicate or missing scheme IDs")

    rows: list[dict[str, Any]] = []
    for map_row in map_rows:
        if not isinstance(map_row, dict):
            raise HarnessMapError("Current model entry map contains a non-object row")
        scheme_id = str(map_row.get("scheme_id") or "")
        state = map_row.get("mapping_state")
        role = map_row.get("current_model_role")
        queue_row = queue_by_id.get(scheme_id)
        if state == "resolved_current_model" and not isinstance(queue_row, dict):
            raise HarnessMapError(f"{scheme_id}: missing G5 queue row")
        if state == "resolved_current_model" and role == "graphical_controller_core":
            rows.append(graphical_core_row(map_row, queue_row))
        elif state == "resolved_current_model" and role == "fixed_integrated_whole_aircraft_closed_loop":
            rows.append(fixed_integrated_row(map_row, queue_row))
        elif state == "blocked_missing_current_model":
            rows.append(blocked_row(map_row))
        elif state == "not_applicable_runtime_baseline":
            rows.append(runtime_baseline_row(map_row))
        else:
            raise HarnessMapError(f"{scheme_id}: unsupported mapping state/role: {state}/{role}")

    state_counts = Counter(str(row["formal_harness_state"]) for row in rows)
    return {
        "schema": "mosim.formal_closed_loop_harness_map.v1",
        "scope": (
            "D2 static formal-harness mapping only. It does not prove a MWORKS "
            "check, graphical review, simulation, result, metric, or runtime success."
        ),
        "source_current_model_map": "Config/control_platform/current_model_entry_map.json",
        "source_current_model_map_sha256": sha256_file(CURRENT_MAP_PATH),
        "source_g5_graphical_review_queue": (
            "Results/control_platform/g5_graphical_structure_review_20260722/"
            "G5_GRAPHICAL_REVIEW_QUEUE.json"
        ),
        "source_g5_graphical_review_queue_sha256": sha256_file(QUEUE_PATH),
        "summary": {
            "top_level_scheme_count": len(rows),
            "current_mworks_candidate_count": (
                state_counts["missing_closed_loop_harness"]
                + state_counts["resolved_canonical_whole_aircraft_harness"]
            ),
            "resolved_canonical_whole_aircraft_harness_count": state_counts[
                "resolved_canonical_whole_aircraft_harness"
            ],
            "missing_closed_loop_harness_count": state_counts["missing_closed_loop_harness"],
            "blocked_before_harness_mapping_count": state_counts["blocked_before_harness_mapping"],
            "not_applicable_runtime_baseline_count": state_counts["not_applicable_runtime_baseline"],
        },
        "champion_harness_promotion": CHAMPION_HARNESS_PROMOTION_CONTRACT,
        "schemes": rows,
    }


def validate_harness_map(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("schema") != "mosim.formal_closed_loop_harness_map.v1":
        errors.append("schema is invalid")
    rows = value.get("schemes")
    if not isinstance(rows, list) or len(rows) != 49:
        errors.append("map must contain exactly 49 schemes")
        return errors
    identifiers = [str(row.get("scheme_id")) for row in rows if isinstance(row, dict)]
    if len(identifiers) != 49 or len(set(identifiers)) != 49:
        errors.append("scheme IDs must be complete and unique")
    by_id = {str(row.get("scheme_id")): row for row in rows if isinstance(row, dict)}
    for scheme_id in ("mu_synthesis", "neural_smc"):
        if by_id.get(scheme_id, {}).get("formal_harness_state") != "blocked_before_harness_mapping":
            errors.append(f"{scheme_id} must remain blocked_before_harness_mapping")
    if by_id.get("px4ctrl", {}).get("formal_harness_state") != "not_applicable_runtime_baseline":
        errors.append("px4ctrl must remain not_applicable_runtime_baseline")

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
    if len(candidates) != 46 or len(graphical) != 41 or len(integrated) != 5:
        errors.append("candidate split must remain 46 = 41 graphical cores + 5 fixed integrated harnesses")
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
            errors.append(f"{row.get('scheme_id')}: fixed integrated chain must enable minimum whole-aircraft closure")
        if not isinstance(harness, dict):
            errors.append(f"{row.get('scheme_id')}: fixed integrated chain must declare a canonical harness")
        else:
            for key in ("public_entry_file", "whole_aircraft_source_file"):
                path_text = harness.get(key)
                if not isinstance(path_text, str) or not path_text.startswith(FORMAL_MODEL_PREFIX):
                    errors.append(f"{row.get('scheme_id')}: harness {key} leaves formal model root")
    expected_summary = {
        "top_level_scheme_count": 49,
        "current_mworks_candidate_count": 46,
        "resolved_canonical_whole_aircraft_harness_count": 5,
        "missing_closed_loop_harness_count": 41,
        "blocked_before_harness_mapping_count": 2,
        "not_applicable_runtime_baseline_count": 1,
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
        "schema": "mosim.formal_closed_loop_harness_map_check.v1",
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "output": str(args.output),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
