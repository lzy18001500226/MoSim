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
CHAMPION_SELECTION_PATH = ROOT / "Config" / "control_platform" / "g6_champion_selection.json"
DEFAULT_G6_STATUS_PATH = ROOT / "Results" / "control_platform" / "g6_controller_execution_20260724" / "G6_EXECUTION_STATUS.json"
G6_STATUS_PATH = DEFAULT_G6_STATUS_PATH
FORMAL_MODEL_PREFIX = "Models/MoSimQuadrotorModel/"
FORMAL_INTERFACE_PREFIX = "MoSimQuadrotorModel.Control.Interfaces."
SYSBLOCK_DEFINITION_ROOT = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "Sysblocks"
)
CHAMPION_SELECTION_SCHEMA = "mosim.g6_provisional_champion_selection.v1"

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


def project_file(path_text: str, label: str) -> Path:
    """Resolve one project-owned file without allowing an external path."""
    if not isinstance(path_text, str) or not path_text:
        raise HarnessMapError(f"{label} path is missing")
    path = ROOT / path_text
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise HarnessMapError(f"{label} leaves the project root: {path_text}") from exc
    if not path.is_file():
        raise HarnessMapError(f"{label} is missing: {path_text}")
    return path


def configure_g6_status_path(value: Path | None) -> None:
    """Select the active 46-route status table without rewriting historical runs."""

    global G6_STATUS_PATH
    candidate = DEFAULT_G6_STATUS_PATH if value is None else value
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        candidate.relative_to(results_root)
    except ValueError as exc:
        raise HarnessMapError("G6 execution status must remain below Results/") from exc
    if candidate.name != "G6_EXECUTION_STATUS.json":
        raise HarnessMapError("G6 execution status file name must be G6_EXECUTION_STATUS.json")
    if not candidate.is_file():
        raise HarnessMapError(f"G6 execution status is missing: {candidate}")
    G6_STATUS_PATH = candidate


def model_class_from_file(model_path: Path, label: str) -> str:
    """Return the declared Modelica class and reject aliases with a wrong name."""
    text = model_path.read_text(encoding="utf-8")
    within = model_within(model_path, label)
    match = re.search(r"^\s*(?:model|block)\s+([A-Za-z_]\w*)\b", text, re.MULTILINE)
    if not match:
        raise HarnessMapError(f"{label} has no model/block declaration: {model_path}")
    return f"{within}.{match.group(1)}"


def configured_formal_model(
    value: Any,
    label: str,
    required_extends: str | None = None,
) -> dict[str, Any]:
    """Validate one configured adapter or runner and bind its current hash."""
    if not isinstance(value, dict):
        raise HarnessMapError(f"{label} must be an object")
    path_text = value.get("model_file")
    class_text = value.get("model_class")
    if not isinstance(path_text, str) or not isinstance(class_text, str):
        raise HarnessMapError(f"{label} must name model_file and model_class")
    path = formal_file(path_text, label)
    actual_class = model_class_from_file(path, label)
    if actual_class != class_text:
        raise HarnessMapError(f"{label} class mismatch: {actual_class} != {class_text}")
    text = path.read_text(encoding="utf-8")
    if required_extends and not re.search(
        rf"\bextends\s+{re.escape(required_extends)}\b", text
    ):
        raise HarnessMapError(f"{label} must extend {required_extends}")
    descriptor = {
        "model_file": path_text,
        "model_class": class_text,
        "model_sha256": sha256_file(path),
    }
    if isinstance(value.get("output_boundary"), str):
        descriptor["output_boundary"] = value["output_boundary"]
    return descriptor


def g6_current_probe(scheme_id: str, category: str, current_core_hash: str) -> dict[str, Any]:
    """Bind a family candidate to the active matrix, including pending state."""

    status = read_json(G6_STATUS_PATH)
    if status.get("schema") != "mosim.g6_controller_execution_status.v1":
        raise HarnessMapError("G6 execution status schema is invalid")
    matrix_text = status.get("matrix")
    if not isinstance(matrix_text, str):
        raise HarnessMapError("G6 execution status has no matrix path")
    matrix_path = project_file(matrix_text, "G6 execution matrix")
    matrix = read_json(matrix_path)
    if status.get("matrix_sha256") != sha256_file(matrix_path):
        raise HarnessMapError("G6 execution status matrix SHA-256 is stale")
    matrix_rows = matrix.get("rows")
    if not isinstance(matrix_rows, list):
        raise HarnessMapError("G6 execution matrix has no route rows")
    rows = status.get("rows")
    if not isinstance(rows, list):
        raise HarnessMapError("G6 execution status has no rows")
    matches = [row for row in rows if isinstance(row, dict) and row.get("scheme_id") == scheme_id]
    if len(matches) != 1:
        raise HarnessMapError(f"{scheme_id}: G6 execution status has no unique route")
    row = matches[0]
    if row.get("category") != category:
        raise HarnessMapError(f"{scheme_id}: G6 category does not match provisional selection")
    matrix_matches = [
        item for item in matrix_rows if isinstance(item, dict) and item.get("scheme_id") == scheme_id
    ]
    if len(matrix_matches) != 1:
        raise HarnessMapError(f"{scheme_id}: G6 execution matrix has no unique route")
    matrix_row = matrix_matches[0]
    target = matrix_row.get("target") if isinstance(matrix_row.get("target"), dict) else {}
    target_hash = target.get("model_sha256")
    if matrix_row.get("category") != category or row.get("evidence_class") != "internal_fixed_input_probe":
        raise HarnessMapError(f"{scheme_id}: G6 route does not match the selected graphical candidate")
    base = {
        "status": row.get("status"),
        "evidence_class": "internal_fixed_input_probe",
        "matrix": str(matrix_text).replace("\\", "/"),
        "matrix_sha256": status.get("matrix_sha256"),
        "target_model_sha256": target_hash,
    }
    if target_hash != current_core_hash:
        base["status"] = "source_hash_mismatch"
        base["reason"] = "The active matrix target hash does not match the current graphical core."
        base["run_record"] = None
        return base
    if row.get("status") == "pending":
        base["run_record"] = None
        return base
    if row.get("status") != "passed":
        base["run_record"] = row.get("run_record")
        base["reason"] = "The active current-matrix probe is terminal but not passed."
        return base
    record_text = row.get("run_record")
    record_path = project_file(str(record_text), f"{scheme_id}: G6 run record")
    record = read_json(record_path)
    record_target = record.get("matrix", {}).get("target") if isinstance(record.get("matrix"), dict) else {}
    if (
        record.get("scheme_id") != scheme_id
        or record.get("status") != "passed"
        or record_target.get("model_sha256") != current_core_hash
    ):
        raise HarnessMapError(f"{scheme_id}: G6 run record is not a passed matching current route")
    return {
        **base,
        "status": "passed",
        "run_record": str(record_text).replace("\\", "/"),
        "run_record_sha256": sha256_file(record_path),
    }


def candidate_promotion_state(probe: dict[str, Any]) -> str:
    """Keep candidate naming separate from champion promotion and A/B admission."""

    return "adapter_binding_pending" if probe.get("status") == "passed" else "awaiting_current_g6_probe"


def build_provisional_champion_selection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the post-G6 selection layer without changing the frozen 41+5 split."""
    selection = read_json(CHAMPION_SELECTION_PATH)
    if selection.get("schema") != CHAMPION_SELECTION_SCHEMA:
        raise HarnessMapError("G6 provisional champion selection schema is invalid")
    source_candidates = selection.get("candidates")
    if not isinstance(source_candidates, list):
        raise HarnessMapError("G6 provisional champion selection has no candidate list")
    expected_categories = list(CHAMPION_HARNESS_PROMOTION_CONTRACT["nominal_family_categories"])
    if len(source_candidates) != len(expected_categories):
        raise HarnessMapError("G6 provisional champion selection must contain six family candidates")
    by_id = {str(row.get("scheme_id")): row for row in rows}
    selected_categories: list[str] = []
    selected_ids: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for candidate in source_candidates:
        if not isinstance(candidate, dict):
            raise HarnessMapError("G6 provisional champion selection contains a non-object candidate")
        category = candidate.get("category")
        scheme_id = candidate.get("scheme_id")
        if not isinstance(category, str) or not isinstance(scheme_id, str):
            raise HarnessMapError("G6 provisional champion candidate is missing category or scheme_id")
        if category in selected_categories or scheme_id in selected_ids:
            raise HarnessMapError(f"G6 provisional champion candidate is duplicated: {category}/{scheme_id}")
        selected_categories.append(category)
        selected_ids.add(scheme_id)
        row = by_id.get(scheme_id)
        if not isinstance(row, dict):
            raise HarnessMapError(f"{scheme_id}: provisional champion is not in the formal map")
        if row.get("category") != category:
            raise HarnessMapError(f"{scheme_id}: provisional champion category does not match formal map")
        if row.get("formal_harness_state") != "missing_closed_loop_harness":
            raise HarnessMapError(f"{scheme_id}: provisional champion must start from a current graphical core")
        if candidate.get("promotion_state") != "awaiting_current_g6_probe":
            raise HarnessMapError(f"{scheme_id}: family candidate must await the active current-matrix probe")
        adapter_contract = candidate.get("required_adapter_contract")
        if adapter_contract != "ATTITUDE_THRUST":
            raise HarnessMapError(f"{scheme_id}: provisional champion must declare ATTITUDE_THRUST adapter contract")
        reason = candidate.get("selection_reason")
        if not isinstance(reason, str) or not reason.strip():
            raise HarnessMapError(f"{scheme_id}: provisional champion selection reason is missing")
        implementation_reference = candidate.get("implementation_reference")
        implementation_path = project_file(str(implementation_reference), f"{scheme_id}: implementation reference")
        probe = g6_current_probe(scheme_id, category, str(row.get("current_model_sha256")))
        candidates.append(
            {
                "category": category,
                "scheme_id": scheme_id,
                "display_name_zh": row.get("display_name_zh"),
                "selection_reason": reason,
                "promotion_state": candidate_promotion_state(probe),
                "champion_core": {
                    "model_file": row.get("current_model_file"),
                    "model_class": row.get("current_model_class"),
                    "model_sha256": row.get("current_model_sha256"),
                },
                "g6_probe": probe,
                "required_adapter_contract": adapter_contract,
                "implementation_reference": {
                    "path": str(implementation_reference).replace("\\", "/"),
                    "sha256": sha256_file(implementation_path),
                    "claim_boundary": "Implementation reference only. A future formal adapter must be checked for behavior and interface equivalence before minimum closure.",
                },
            }
        )
    if sorted(selected_categories) != sorted(expected_categories):
        raise HarnessMapError("G6 provisional champion selection must cover each nominal family exactly once")

    baseline = selection.get("official_pid_baseline")
    if not isinstance(baseline, dict) or baseline.get("scheme_id") != "official_pid":
        raise HarnessMapError("G6 provisional selection must include the official_pid A/B baseline")
    baseline_row = by_id.get("official_pid")
    if not isinstance(baseline_row, dict) or baseline_row.get("category") != "pid_family":
        raise HarnessMapError("official_pid baseline category is invalid")
    if baseline.get("binding_state") != "formal_binding_ready_for_validation":
        raise HarnessMapError("official_pid baseline must be ready for validation, not promoted as a family champion")
    boundary = baseline.get("semantic_boundary")
    if not isinstance(boundary, str) or not boundary.strip():
        raise HarnessMapError("official_pid baseline semantic boundary is missing")
    core_reference = baseline.get("core_reference")
    if not isinstance(core_reference, dict) or core_reference.get("model_class") != "MoSimQuadrotorModel.Vehicle.Blocks.Controller.Controller":
        raise HarnessMapError("official_pid baseline must bind the full embedded Plant controller core")
    adapter = configured_formal_model(
        baseline.get("formal_adapter"),
        "official_pid baseline adapter",
        "MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController",
    )
    if adapter.get("output_boundary") != "ROTOR_COMMAND":
        raise HarnessMapError("official_pid baseline adapter must use the ROTOR_COMMAND boundary")
    harness = configured_formal_model(
        baseline.get("whole_aircraft_source_harness"),
        "official_pid baseline runner",
        "MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner",
    )
    minimum_scenario = baseline.get("minimum_scenario")
    if (
        not isinstance(minimum_scenario, dict)
        or minimum_scenario.get("scenario_id") != "climb_path_50s"
        or minimum_scenario.get("reference_owner") != "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath"
        or minimum_scenario.get("duration_s") != 50
    ):
        raise HarnessMapError("official_pid baseline minimum scenario must be the 50 s ClimbPath run")
    return {
        "schema": CHAMPION_SELECTION_SCHEMA,
        "state": (
            "candidate_slate_ready_for_family_selection"
            if all(candidate["g6_probe"].get("status") == "passed" for candidate in candidates)
            else "candidate_slate_pending_current_matrix"
        ),
        "selection_criteria": selection.get("selection_criteria"),
        "official_pid_baseline": {
            "scheme_id": "official_pid",
            "binding_state": "formal_binding_ready_for_validation",
            "semantic_boundary": boundary,
            "core_reference": core_reference,
            "formal_adapter": adapter,
            "whole_aircraft_source_harness": harness,
            "minimum_scenario": minimum_scenario,
        },
        "candidates": candidates,
        "summary": {
            "selected_family_count": len(candidates),
            "awaiting_current_g6_probe_count": sum(
                1 for candidate in candidates if candidate["promotion_state"] == "awaiting_current_g6_probe"
            ),
            "adapter_binding_pending_count": sum(
                1 for candidate in candidates if candidate["promotion_state"] == "adapter_binding_pending"
            ),
            "formal_candidate_minimum_closure_passed_count": 0,
            "official_pid_baseline_ready_for_validation_count": 1,
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
        r"^\s*((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)\s+controller3_2(?:\s*\([^;]*\))?\s*;",
        source_text,
        flags=re.MULTILINE,
    )
    if len(type_matches) != 1:
        raise HarnessMapError(
            f"{scheme_id}: expected exactly one unqualified controller3_2 type in {source_path.name}, found {type_matches}"
        )
    declared_type = type_matches[0]
    controller_type = declared_type.rsplit(".", 1)[-1]
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
        "source_component": "controller3_2",
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
        "source_component": "controller3_2",
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
    provisional_selection = build_provisional_champion_selection(rows)
    provisional_summary = provisional_selection["summary"]
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
        "source_g6_champion_selection": str(CHAMPION_SELECTION_PATH.relative_to(ROOT)).replace("\\", "/"),
        "source_g6_champion_selection_sha256": sha256_file(CHAMPION_SELECTION_PATH),
        "source_g6_execution_status": str(G6_STATUS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "source_g6_execution_status_sha256": sha256_file(G6_STATUS_PATH),
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
            "provisional_champion_selection_count": provisional_summary["selected_family_count"],
            "provisional_champion_adapter_pending_count": provisional_summary["adapter_binding_pending_count"],
            "provisional_champion_minimum_closure_passed_count": provisional_summary[
                "formal_candidate_minimum_closure_passed_count"
            ],
            "official_pid_baseline_ready_for_validation_count": provisional_summary[
                "official_pid_baseline_ready_for_validation_count"
            ],
        },
        "champion_harness_promotion": CHAMPION_HARNESS_PROMOTION_CONTRACT,
        "provisional_champion_selection": provisional_selection,
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
        prerequisites = row.get("model_load_prerequisites")
        if not isinstance(prerequisites, list) or not prerequisites or any(not isinstance(item, dict) for item in prerequisites):
            errors.append(f"{row.get('scheme_id')}: fixed integrated chain needs frozen load prerequisites")
        else:
            prerequisite = prerequisites[0]
            if not isinstance(harness, dict):
                continue
            source_file = harness.get("whole_aircraft_source_file")
            if not isinstance(source_file, str):
                errors.append(f"{row.get('scheme_id')}: fixed integrated chain has no source for its prerequisite")
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
    provisional = value.get("provisional_champion_selection")
    if not isinstance(provisional, dict):
        errors.append("provisional champion selection is missing")
        return errors
    if provisional.get("schema") != CHAMPION_SELECTION_SCHEMA:
        errors.append("provisional champion selection schema is invalid")
    if provisional.get("state") not in {
        "candidate_slate_pending_current_matrix",
        "candidate_slate_ready_for_family_selection",
    }:
        errors.append("provisional champion selection state is invalid")
    provisional_candidates = provisional.get("candidates")
    expected_categories = set(CHAMPION_HARNESS_PROMOTION_CONTRACT["nominal_family_categories"])
    if not isinstance(provisional_candidates, list) or len(provisional_candidates) != len(expected_categories):
        errors.append("provisional champion selection must contain exactly six candidates")
    else:
        categories = {str(candidate.get("category")) for candidate in provisional_candidates if isinstance(candidate, dict)}
        identifiers = {str(candidate.get("scheme_id")) for candidate in provisional_candidates if isinstance(candidate, dict)}
        if categories != expected_categories or len(identifiers) != len(expected_categories):
            errors.append("provisional champion selection must cover six distinct nominal families")
        for candidate in provisional_candidates:
            if not isinstance(candidate, dict):
                errors.append("provisional champion selection contains a non-object candidate")
                continue
            scheme_id = str(candidate.get("scheme_id"))
            mapped = by_id.get(scheme_id, {})
            if mapped.get("formal_harness_state") != "missing_closed_loop_harness":
                errors.append(f"{scheme_id}: provisional champion must retain its internal-only G6 route state")
            core = candidate.get("champion_core")
            probe = candidate.get("g6_probe")
            if not isinstance(core, dict) or core.get("model_sha256") != mapped.get("current_model_sha256"):
                errors.append(f"{scheme_id}: provisional champion core is not hash-bound to the current model")
            probe_status = probe.get("status") if isinstance(probe, dict) else None
            expected_promotion = "adapter_binding_pending" if probe_status == "passed" else "awaiting_current_g6_probe"
            if not isinstance(probe, dict) or probe.get("evidence_class") != "internal_fixed_input_probe":
                errors.append(f"{scheme_id}: provisional candidate has no active G6 probe binding")
            if candidate.get("promotion_state") != expected_promotion:
                errors.append(f"{scheme_id}: candidate promotion state does not match its current G6 probe")
    baseline = provisional.get("official_pid_baseline")
    if not isinstance(baseline, dict):
        errors.append("official_pid A/B baseline binding is missing")
    else:
        if baseline.get("scheme_id") != "official_pid" or baseline.get("binding_state") != "formal_binding_ready_for_validation":
            errors.append("official_pid baseline binding state is invalid")
        if not isinstance(baseline.get("formal_adapter"), dict) or not isinstance(
            baseline.get("whole_aircraft_source_harness"), dict
        ):
            errors.append("official_pid baseline requires an adapter and whole-aircraft runner")
    summary = provisional.get("summary")
    if not isinstance(summary, dict) or summary.get("selected_family_count") != 6 or summary.get(
        "formal_candidate_minimum_closure_passed_count"
    ) != 0 or summary.get("official_pid_baseline_ready_for_validation_count") != 1:
        errors.append("provisional champion selection summary is invalid")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--g6-status",
        type=Path,
        help="active project-local G6 execution status below Results/",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the on-disk map differs from the deterministic build",
    )
    args = parser.parse_args(argv)
    try:
        configure_g6_status_path(args.g6_status)
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
