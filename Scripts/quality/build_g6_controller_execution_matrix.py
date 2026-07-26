#!/usr/bin/env python3
"""Build the current G6 controller-execution matrix from frozen G5/D2 state.

The matrix is deliberately a planning and provenance record. It does not open
MWORKS, simulate a model, create a placeholder result, or promote an internal
fixed-input probe into a whole-aircraft result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from current_model_entry_map_lib import (
    CATALOG_PATH,
    DIRECT_GRAPHICAL_PRIMARY,
    INVENTORY_PATH,
    direct_graphical_native_equivalence_mode,
    import_plan,
)


ROOT = Path(__file__).resolve().parents[2]
HARNESS_MAP = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
G5_STATUS = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "G5_GRAPHICAL_REVIEW_STATUS.json"
)
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "control_platform" / "g6_controller_execution_20260724"
OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT
OUTPUT_PATH = OUTPUT_ROOT / "G6_EXECUTION_MATRIX.json"
STATUS_PATH = OUTPUT_ROOT / "G6_EXECUTION_STATUS.json"
NATIVE_HASH_REFRESH_MANIFEST = OUTPUT_ROOT / "G6_NATIVE_HASH_REFREEZE_MANIFEST.json"
METADATA_ONLY_REFRESH_MANIFEST = OUTPUT_ROOT / "G6_METADATA_ONLY_REFRESH_MANIFEST.json"
OFFICIAL_PID_PROBE = {
    "model_file": "Models/MoSimQuadrotorModel/Experiment/Probes/OfficialPidFixedInputProbe.mo",
    "model_class": "MoSimQuadrotorModel.Experiment.Probes.OfficialPidFixedInputProbe",
    "fixed_inputs": {"altitude_error": 0.15},
    "result_variables": ["thrust_command"],
}

# G6 result-window evidence is materialized beside the G5 native structure
# capture.  Keep this mapping here rather than inferring a report path at run
# time so the frozen matrix names every required artifact up front.
REPORT_FAMILY_DIRECTORIES = {
    "pid_family": "01_PID族",
    "classic_robust": "02_线性与鲁棒",
    "sliding_mode": "03_滑模控制",
    "optimization": "04_MPC族",
    "geometric_flatness": "05_几何与平坦",
    "learning": "06_学习控制",
    "fixed_integrated": "07_固定集成链",
}

G6_ROUTE_STATES = {
    "missing_closed_loop_harness",
    "resolved_canonical_whole_aircraft_harness",
}
ROUTE_SOURCE_FIELDS = (
    "scheme_id",
    "category",
    "formal_harness_state",
    "current_model_file",
    "current_model_class",
)
WHOLE_AIRCRAFT_HARNESS_FIELDS = (
    "whole_aircraft_source_file",
    "whole_aircraft_source_class",
)
MODEL_LOAD_PREREQUISITE_FIELDS = (
    "role",
    "source_component",
    "source_declared_type",
    "base_model_class",
    "model_file",
    "model_class",
    "model_sha256",
)
MATRIX_ROUTE_BINDING_FIELDS = (
    "scheme_id",
    "category",
    "evidence_class",
    "formal_harness_state",
    "target",
    "model_load_prerequisites",
    "controller_core",
    "probe_contract",
    "result_root",
    "required_artifacts",
    "state",
    "claim_boundary",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    """Serialize a source projection independently of map presentation metadata."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def configure_output_root(value: Path | None) -> None:
    """Bind a new evidence root without mutating an earlier frozen matrix."""

    global OUTPUT_ROOT, OUTPUT_PATH, STATUS_PATH
    global NATIVE_HASH_REFRESH_MANIFEST, METADATA_ONLY_REFRESH_MANIFEST
    candidate = DEFAULT_OUTPUT_ROOT if value is None else value
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        candidate.relative_to(results_root)
    except ValueError as exc:
        raise ValueError("output root must remain below Results/") from exc
    OUTPUT_ROOT = candidate
    OUTPUT_PATH = OUTPUT_ROOT / "G6_EXECUTION_MATRIX.json"
    STATUS_PATH = OUTPUT_ROOT / "G6_EXECUTION_STATUS.json"
    NATIVE_HASH_REFRESH_MANIFEST = OUTPUT_ROOT / "G6_NATIVE_HASH_REFREEZE_MANIFEST.json"
    METADATA_ONLY_REFRESH_MANIFEST = OUTPUT_ROOT / "G6_METADATA_ONLY_REFRESH_MANIFEST.json"


def top_level_outports(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    names = re.findall(
        r"SysplorerEmbeddedCoder\.Port\.Outport\s+([A-Za-z_][A-Za-z0-9_]*)",
        text,
    )
    if not names:
        raise ValueError(f"no top-level Sysblock outports found: {relative(path)}")
    return names


def fixed_source_count(path: Path) -> int:
    return len(
        re.findall(
            r"SysplorerEmbeddedCoder\.Sources\.(?:Constant|Step|Ramp|SineWave)\s+",
            path.read_text(encoding="utf-8"),
        )
    )


def g6_route_source_projection(harness: dict[str, Any]) -> dict[str, Any]:
    """Return exactly the harness-map fields consumed by :func:`route_row`.

    The formal harness map also carries post-G6 champion-selection and other
    review metadata. Those fields cannot invalidate historical G6 routes when
    the actual route target, source hash, or probe contract is unchanged.
    """
    schemes = harness.get("schemes")
    if not isinstance(schemes, list):
        raise ValueError("formal harness map has no scheme list")
    projected: list[dict[str, Any]] = []
    for row in schemes:
        if not isinstance(row, dict) or row.get("formal_harness_state") not in G6_ROUTE_STATES:
            continue
        item = {field: row.get(field) for field in ROUTE_SOURCE_FIELDS}
        if item["formal_harness_state"] == "resolved_canonical_whole_aircraft_harness":
            source_harness = row.get("canonical_closed_loop_harness")
            item["canonical_closed_loop_harness"] = (
                {field: source_harness.get(field) for field in WHOLE_AIRCRAFT_HARNESS_FIELDS}
                if isinstance(source_harness, dict)
                else None
            )
            prerequisites = row.get("model_load_prerequisites")
            item["model_load_prerequisites"] = (
                [
                    {field: prerequisite.get(field) for field in MODEL_LOAD_PREREQUISITE_FIELDS}
                    for prerequisite in prerequisites
                    if isinstance(prerequisite, dict)
                ]
                if isinstance(prerequisites, list)
                else None
            )
        projected.append(item)
    projected.sort(key=lambda item: (str(item["category"]), str(item["scheme_id"])))
    return {
        "schema": "mosim.g6_route_source_projection.v1",
        "schemes": projected,
    }


def matrix_route_binding_projection(matrix: dict[str, Any]) -> dict[str, Any]:
    """Project immutable route bindings, excluding matrix-source presentation metadata."""
    rows = matrix.get("rows")
    if not isinstance(rows, list) or len(rows) != 46:
        raise ValueError("G6 route binding projection requires exactly 46 matrix rows")
    projected: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("G6 route binding projection found a non-object row")
        scheme_id = row.get("scheme_id")
        if not isinstance(scheme_id, str) or not scheme_id:
            raise ValueError("G6 route binding projection found a route without scheme_id")
        projected.append({field: row.get(field) for field in MATRIX_ROUTE_BINDING_FIELDS})
    projected.sort(key=lambda item: (str(item["category"]), str(item["scheme_id"])))
    if len({item["scheme_id"] for item in projected}) != len(projected):
        raise ValueError("G6 route binding projection found duplicate scheme_ids")
    return {
        "schema": "mosim.g6_matrix_route_binding_projection.v1",
        "rows": projected,
    }


def route_binding_change_ids(previous: dict[str, Any], refreshed: dict[str, Any]) -> list[str]:
    """Return changed route identifiers for a metadata-only refresh rejection."""
    previous_rows = matrix_route_binding_projection(previous)["rows"]
    refreshed_rows = matrix_route_binding_projection(refreshed)["rows"]
    previous_by_id = {str(row["scheme_id"]): row for row in previous_rows}
    refreshed_by_id = {str(row["scheme_id"]): row for row in refreshed_rows}
    changed = set(previous_by_id) ^ set(refreshed_by_id)
    changed.update(
        scheme_id
        for scheme_id in set(previous_by_id) & set(refreshed_by_id)
        if canonical_json(previous_by_id[scheme_id]) != canonical_json(refreshed_by_id[scheme_id])
    )
    return sorted(changed)


def run_record_inventory(matrix: dict[str, Any]) -> list[dict[str, str]]:
    """Hash every matrix-bound run record without writing or relabeling evidence."""
    inventory: list[dict[str, str]] = []
    for row in matrix_route_binding_projection(matrix)["rows"]:
        scheme_id = str(row["scheme_id"])
        artifacts = row.get("required_artifacts")
        if not isinstance(artifacts, dict) or not isinstance(artifacts.get("run_record"), str):
            raise ValueError(f"{scheme_id}: matrix route has no run-record artifact path")
        record_path = ROOT / str(artifacts["run_record"])
        try:
            record_path.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ValueError(f"{scheme_id}: run-record artifact leaves repository") from exc
        if not record_path.is_file():
            raise ValueError(f"{scheme_id}: matrix-bound run record is missing: {relative(record_path)}")
        inventory.append(
            {
                "scheme_id": scheme_id,
                "path": relative(record_path),
                "sha256": sha256(record_path),
            }
        )
    return inventory


def route_row(row: dict[str, Any]) -> dict[str, Any]:
    scheme_id = str(row["scheme_id"])
    category = str(row["category"])
    state = str(row["formal_harness_state"])
    core_file = str(row["current_model_file"])
    core_class = str(row["current_model_class"])
    core_path = ROOT / core_file
    if not core_path.is_file():
        raise ValueError(f"{scheme_id}: controller core is missing: {core_file}")
    model_load_prerequisites: list[dict[str, Any]] = []
    if state == "missing_closed_loop_harness":
        probe_override = OFFICIAL_PID_PROBE if scheme_id == "official_pid" else None
        target_file = str(probe_override["model_file"]) if probe_override else core_file
        target_class = str(probe_override["model_class"]) if probe_override else core_class
        result_variables = (
            list(probe_override["result_variables"])
            if probe_override
            else top_level_outports(core_path)[:4]
        )
        input_contract: dict[str, Any] = (
            {
                "kind": "thin_fixed_input_fixture",
                "values": dict(probe_override["fixed_inputs"]),
                "fixture_only": True,
            }
            if probe_override
            else {
                "kind": "embedded_fixed_input_sources",
                "source_block_count": fixed_source_count(core_path),
                "fixture_only": False,
            }
        )
        evidence_class = "internal_fixed_input_probe"
        claim_boundary = "Graphical controller internal response only; not a plant-coupled whole-aircraft result."
    elif state == "resolved_canonical_whole_aircraft_harness":
        harness = row.get("canonical_closed_loop_harness")
        if not isinstance(harness, dict):
            raise ValueError(f"{scheme_id}: resolved harness is missing")
        target_file = str(harness["whole_aircraft_source_file"])
        target_class = str(harness["whole_aircraft_source_class"])
        result_variables = [
            "sensors1_1.PosMea[3]",
            "climbePath.position_command[3]",
            "sensors1_1.PosMea[1]",
            "climbePath.position_command[1]",
        ]
        input_contract = {"kind": "formal_whole_aircraft_minimum_scenario"}
        evidence_class = "whole_aircraft_minimum_closure"
        claim_boundary = "Named formal whole-aircraft minimum closure only; no code-generation or runtime claim."
        prerequisites = row.get("model_load_prerequisites")
        if not isinstance(prerequisites, list) or not prerequisites:
            raise ValueError(f"{scheme_id}: resolved whole-aircraft harness has no frozen load prerequisite")
        for prerequisite in prerequisites:
            if not isinstance(prerequisite, dict):
                raise ValueError(f"{scheme_id}: invalid frozen load prerequisite")
            prerequisite_file = prerequisite.get("model_file")
            prerequisite_class = prerequisite.get("model_class")
            prerequisite_hash = prerequisite.get("model_sha256")
            if not isinstance(prerequisite_file, str) or not isinstance(prerequisite_class, str) or not isinstance(prerequisite_hash, str):
                raise ValueError(f"{scheme_id}: incomplete frozen load prerequisite")
            prerequisite_path = ROOT / prerequisite_file
            if not prerequisite_path.is_file():
                raise ValueError(f"{scheme_id}: load prerequisite is missing: {prerequisite_file}")
            actual_prerequisite_hash = sha256(prerequisite_path)
            if actual_prerequisite_hash != prerequisite_hash:
                raise ValueError(
                    f"{scheme_id}: load prerequisite hash drift: {actual_prerequisite_hash} != {prerequisite_hash}"
                )
            model_load_prerequisites.append(
                {
                    "role": prerequisite.get("role"),
                    "source_component": prerequisite.get("source_component"),
                    "source_declared_type": prerequisite.get("source_declared_type"),
                    "base_model_class": prerequisite.get("base_model_class"),
                    "model_file": prerequisite_file,
                    "model_class": prerequisite_class,
                    "model_sha256": prerequisite_hash,
                }
            )
    else:
        raise ValueError(f"{scheme_id}: unsupported current G6 state {state}")

    source = ROOT / target_file
    if not source.is_file():
        raise ValueError(f"{scheme_id}: target model is missing: {target_file}")
    model_hash = sha256(source)
    run_dir = OUTPUT_ROOT / "runs" / scheme_id
    report_family = REPORT_FAMILY_DIRECTORIES.get(category)
    if report_family is None:
        raise ValueError(f"{scheme_id}: unsupported report family {category}")
    report_result = (
        ROOT
        / "Docs"
        / "报告"
        / "图"
        / "控制器"
        / report_family
        / scheme_id
        / "02_最小闭环结果原生窗口.png"
    )
    return {
        "scheme_id": scheme_id,
        "category": category,
        "evidence_class": evidence_class,
        "formal_harness_state": state,
        "target": {
            "model_file": target_file,
            "model_class": target_class,
            "model_sha256": model_hash,
        },
        "model_load_prerequisites": model_load_prerequisites,
        "controller_core": {
            "model_file": core_file,
            "model_class": core_class,
            "model_sha256": sha256(core_path),
        },
        "probe_contract": {
            "input": input_contract,
            "result_variables": result_variables,
        },
        "result_root": relative(run_dir),
        "required_artifacts": {
            "run_record": relative(run_dir / "RUN_RECORD.json"),
            "check_model_log": relative(run_dir / "logs" / "check_model.json"),
            "simulate_log": relative(run_dir / "logs" / "simulate_model.json"),
            "screenshot_manifest": relative(run_dir / "logs" / "screenshot_manifest.json"),
            "result_window_screenshot": relative(run_dir / "screenshots" / "02_result_window.png"),
            "report_result_screenshot": relative(report_result),
        },
        "state": "pending",
        "claim_boundary": claim_boundary,
    }


def build() -> dict[str, Any]:
    harness = read_json(HARNESS_MAP)
    route_source = g6_route_source_projection(harness)
    status = read_json(G5_STATUS)
    summary = status.get("summary")
    reviewed = status.get("reviewed")
    if not isinstance(summary, dict) or summary.get("graphical_ready_count") != 46:
        raise ValueError("G6 requires 46 graphical_ready routes")
    if not isinstance(reviewed, list) or any(item.get("processing_state") != "graphical_ready" for item in reviewed if isinstance(item, dict)):
        raise ValueError("G6 requires every reviewed G5 route to be graphical_ready")
    schemes = harness.get("schemes")
    if not isinstance(schemes, list):
        raise ValueError("formal harness map has no scheme list")
    rows = [
        route_row(row)
        for row in schemes
        if isinstance(row, dict)
        and row.get("formal_harness_state") in G6_ROUTE_STATES
    ]
    rows.sort(key=lambda item: (item["category"], item["scheme_id"]))
    counts = Counter(row["evidence_class"] for row in rows)
    if len(rows) != 46 or counts != {
        "internal_fixed_input_probe": 41,
        "whole_aircraft_minimum_closure": 5,
    }:
        raise ValueError(f"unexpected G6 split: routes={len(rows)} counts={dict(counts)}")
    return {
        "schema": "mosim.g6_controller_execution_matrix.v1",
        "scope": "Current G6 execution plan and source binding only. It records no MWORKS simulation result until an individual run record exists.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "formal_harness_map": relative(HARNESS_MAP),
            "formal_harness_route_projection_schema": route_source["schema"],
            "formal_harness_route_projection_sha256": value_sha256(route_source),
            "g5_status": relative(G5_STATUS),
            "g5_status_sha256": sha256(G5_STATUS),
        },
        "summary": {
            "route_count": len(rows),
            "internal_fixed_input_probe_count": counts["internal_fixed_input_probe"],
            "whole_aircraft_minimum_closure_count": counts["whole_aircraft_minimum_closure"],
            "terminal_result_count": 0,
        },
        "rows": rows,
        "next_gate": "The 46 G6 routes are terminal. Bind each provisional six-family candidate to its own formal whole-aircraft adapter and minimum closure before seven-scenario A/B against the separately bound Official PID baseline.",
    }


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def equals_for_check(expected: dict[str, Any], actual_text: str) -> bool:
    """Compare matrix content while allowing its generation timestamp to differ."""
    actual = json.loads(actual_text)
    if not isinstance(actual, dict):
        return False
    expected_without_timestamp = dict(expected)
    actual_without_timestamp = dict(actual)
    expected_without_timestamp.pop("generated_at", None)
    actual_without_timestamp.pop("generated_at", None)
    return actual_without_timestamp == expected_without_timestamp


def native_hash_refresh_rows(previous: dict[str, Any], refreshed: dict[str, Any]) -> list[dict[str, str]]:
    """Validate the sole allowed source-hash refresh for G6 direct graphs.

    MWORKS may materialize its exact default experiment annotation when one of
    the 13 direct graphical controllers is first loaded. This operation is a
    bounded re-freeze, not a generic way to replace a matrix after model work:
    every changed row must be one of those direct graphs and must pass the
    strict native-serialization comparator.
    """
    previous_rows = previous.get("rows")
    refreshed_rows = refreshed.get("rows")
    if not isinstance(previous_rows, list) or not isinstance(refreshed_rows, list):
        raise ValueError("G6 native hash refresh requires row lists in both matrices")
    previous_by_id = {
        str(row.get("scheme_id")): row for row in previous_rows if isinstance(row, dict)
    }
    refreshed_by_id = {
        str(row.get("scheme_id")): row for row in refreshed_rows if isinstance(row, dict)
    }
    if set(previous_by_id) != set(refreshed_by_id):
        raise ValueError("G6 native hash refresh cannot add, remove, or rename matrix routes")

    catalog = read_json(CATALOG_PATH)
    inventory = read_json(INVENTORY_PATH)
    imports = {
        str(item["scheme_id"]): item
        for item in import_plan(catalog, inventory)
    }
    changed: list[dict[str, str]] = []
    for scheme_id in sorted(previous_by_id):
        previous_row = previous_by_id[scheme_id]
        refreshed_row = refreshed_by_id[scheme_id]
        previous_target = previous_row.get("target") if isinstance(previous_row.get("target"), dict) else {}
        refreshed_target = refreshed_row.get("target") if isinstance(refreshed_row.get("target"), dict) else {}
        old_hash = previous_target.get("model_sha256")
        new_hash = refreshed_target.get("model_sha256")
        if not isinstance(old_hash, str) or not isinstance(new_hash, str):
            raise ValueError(f"{scheme_id}: matrix target hash is missing")
        if old_hash == new_hash:
            continue
        if scheme_id not in DIRECT_GRAPHICAL_PRIMARY:
            raise ValueError(f"{scheme_id}: native hash refresh is not allowed for this route")
        if previous_target.get("model_file") != refreshed_target.get("model_file"):
            raise ValueError(f"{scheme_id}: native hash refresh cannot change the target file")
        item = imports.get(scheme_id)
        if item is None:
            raise ValueError(f"{scheme_id}: no current direct graphical import item exists")
        mode = direct_graphical_native_equivalence_mode(
            item, ROOT / str(refreshed_target["model_file"])
        )
        if mode != "audited_sysplorer_native_direct_graphical_serialization":
            raise ValueError(f"{scheme_id}: source change is not the accepted MWORKS native serialization")
        changed.append(
            {
                "scheme_id": scheme_id,
                "model_file": str(refreshed_target["model_file"]),
                "previous_model_sha256": old_hash,
                "refreshed_model_sha256": new_hash,
                "equivalence": mode,
            }
        )
    if not changed:
        raise ValueError("G6 native hash refresh requested but no target source hashes changed")
    return changed


def archive_native_hash_refresh(previous: dict[str, Any], refreshed: dict[str, Any]) -> dict[str, Any]:
    """Archive stale G6 planning state before replacing it with current bytes."""
    changes = native_hash_refresh_rows(previous, refreshed)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = OUTPUT_ROOT / "matrix_superseded" / f"native_serialization_{stamp}"
    archive_dir.mkdir(parents=True, exist_ok=False)
    archived_files: list[dict[str, str]] = []
    for source in (OUTPUT_PATH, STATUS_PATH):
        if source.is_file():
            destination = archive_dir / source.name
            shutil.copy2(source, destination)
            archived_files.append(
                {
                    "source": relative(source),
                    "archive": relative(destination),
                    "sha256": sha256(source),
                }
            )
    if not any(item["source"] == relative(OUTPUT_PATH) for item in archived_files):
        raise ValueError("G6 native hash refresh could not archive the prior matrix")
    return {
        "schema": "mosim.g6_controller_execution_native_hash_refreeze.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "reason": "MWORKS materialized the exact audited direct-graph default experiment serialization; no controller law, port, equation, or layout drift was accepted.",
        "previous_matrix": {
            "path": relative(archive_dir / OUTPUT_PATH.name),
            "sha256": sha256(archive_dir / OUTPUT_PATH.name),
        },
        "previous_status": next(
            (
                {"path": item["archive"], "sha256": item["sha256"]}
                for item in archived_files
                if item["source"] == relative(STATUS_PATH)
            ),
            None,
        ),
        "refreshed_matrix": {
            "path": relative(OUTPUT_PATH),
            "sha256": hashlib.sha256(dump(refreshed).encode("utf-8")).hexdigest(),
        },
        "changed_routes": changes,
        "unchanged_route_result_rule": "Existing G6 route records remain bound only when their route target file and target SHA-256 are unchanged. Refreshed routes require an explicit --rerun and supersede their prior terminal record.",
    }


def status_has_terminal_results() -> bool:
    """Return whether a persisted status table protects existing G6 evidence."""
    if not STATUS_PATH.is_file():
        return False
    status = read_json(STATUS_PATH)
    summary = status.get("summary")
    if isinstance(summary, dict):
        try:
            if int(summary.get("terminal_count", 0)) > 0:
                return True
        except (TypeError, ValueError):
            pass
    rows = status.get("rows")
    return isinstance(rows, list) and any(
        isinstance(row, dict) and row.get("status") not in {None, "pending"}
        for row in rows
    )


def initial_execution_status(matrix: dict[str, Any]) -> dict[str, Any]:
    """Create the explicit all-pending state for a newly frozen matrix."""

    rows = matrix.get("rows")
    if not isinstance(rows, list) or len(rows) != 46:
        raise ValueError("initial G6 execution status requires exactly 46 matrix rows")
    return {
        "schema": "mosim.g6_controller_execution_status.v1",
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "matrix": relative(OUTPUT_PATH),
        "matrix_sha256": sha256(OUTPUT_PATH),
        "summary": {
            "route_count": len(rows),
            "terminal_count": 0,
            "passed_count": 0,
            "pending_count": len(rows),
            "status_counts": {"pending": len(rows)},
        },
        "rows": [
            {
                "scheme_id": row["scheme_id"],
                "category": row["category"],
                "evidence_class": row["evidence_class"],
                "status": "pending",
                "run_record": None,
            }
            for row in rows
        ],
    }


def archive_metadata_only_matrix(previous: dict[str, Any]) -> dict[str, str]:
    """Retain the old plan matrix while leaving every result artifact in place."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = OUTPUT_ROOT / "matrix_superseded" / f"metadata_only_{stamp}"
    archive_dir.mkdir(parents=True, exist_ok=False)
    archived_matrix = archive_dir / OUTPUT_PATH.name
    shutil.copy2(OUTPUT_PATH, archived_matrix)
    return {
        "path": relative(archived_matrix),
        "sha256": sha256(archived_matrix),
        "sources": previous.get("sources"),
    }


def prepare_metadata_only_refresh(
    previous: dict[str, Any],
    refreshed: dict[str, Any],
    refreshed_text: str,
) -> dict[str, Any]:
    """Prove that a source-metadata refresh cannot mutate G6 route evidence."""
    changed_routes = route_binding_change_ids(previous, refreshed)
    if changed_routes:
        raise ValueError(
            "G6 metadata-only refresh rejected because route bindings changed: "
            + ", ".join(changed_routes)
        )
    previous_binding = matrix_route_binding_projection(previous)
    refreshed_binding = matrix_route_binding_projection(refreshed)
    previous_binding_hash = value_sha256(previous_binding)
    refreshed_binding_hash = value_sha256(refreshed_binding)
    if previous_binding_hash != refreshed_binding_hash:
        raise ValueError("G6 metadata-only refresh route binding fingerprint changed")
    if not STATUS_PATH.is_file():
        raise ValueError("G6 metadata-only refresh requires the existing execution status")
    status = read_json(STATUS_PATH)
    status_summary = status.get("summary")
    if not isinstance(status_summary, dict) or status_summary.get("passed_count") != 46:
        raise ValueError("G6 metadata-only refresh requires 46 passed status rows")
    previous_matrix_hash = sha256(OUTPUT_PATH)
    status_matrix_hash = status.get("matrix_sha256")
    if status_matrix_hash != previous_matrix_hash:
        raise ValueError(
            "G6 metadata-only refresh requires the status table to bind the current pre-refresh matrix"
        )
    records = run_record_inventory(previous)
    if len(records) != 46:
        raise ValueError("G6 metadata-only refresh requires 46 matrix-bound run records")
    archived_matrix = archive_metadata_only_matrix(previous)
    return {
        "schema": "mosim.g6_controller_execution_metadata_only_refresh.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "reason": (
            "Post-G6 formal-harness/champion metadata changed outside the canonical 46-route "
            "source projection. All route bindings, target hashes, run records, and the "
            "execution status remain unchanged."
        ),
        "previous_matrix": archived_matrix,
        "refreshed_matrix": {
            "path": relative(OUTPUT_PATH),
            "sha256": hashlib.sha256(refreshed_text.encode("utf-8")).hexdigest(),
            "sources": refreshed.get("sources"),
        },
        "route_binding": {
            "route_count": 46,
            "previous_sha256": previous_binding_hash,
            "refreshed_sha256": refreshed_binding_hash,
            "all_46_route_bindings_unchanged": True,
        },
        "status": {
            "path": relative(STATUS_PATH),
            "sha256": sha256(STATUS_PATH),
            "matrix_sha256_before_refresh": status_matrix_hash,
            "preserved_without_rewrite": True,
        },
        "run_records": {
            "count": len(records),
            "inventory_sha256": value_sha256(records),
            "preserved_without_rewrite": True,
            "records": records,
        },
        "claim_boundary": (
            "Metadata-continuity evidence only. This does not convert the 41 internal probes "
            "into whole-aircraft results or validate the six pending candidate adapters."
        ),
    }


def validate_status_matrix_continuity() -> None:
    """Accept either direct status binding or one verified metadata-only bridge."""
    if not STATUS_PATH.is_file():
        return
    status = read_json(STATUS_PATH)
    status_matrix_hash = status.get("matrix_sha256")
    current_matrix_hash = sha256(OUTPUT_PATH)
    if status_matrix_hash == current_matrix_hash:
        return
    if not METADATA_ONLY_REFRESH_MANIFEST.is_file():
        raise ValueError("G6 execution status points to a different matrix without a metadata-only refresh manifest")
    manifest = read_json(METADATA_ONLY_REFRESH_MANIFEST)
    if manifest.get("schema") != "mosim.g6_controller_execution_metadata_only_refresh.v1":
        raise ValueError("G6 metadata-only refresh manifest has an invalid schema")
    previous_matrix = manifest.get("previous_matrix")
    refreshed_matrix = manifest.get("refreshed_matrix")
    binding = manifest.get("route_binding")
    status_binding = manifest.get("status")
    records = manifest.get("run_records")
    if not all(isinstance(value, dict) for value in (previous_matrix, refreshed_matrix, binding, status_binding, records)):
        raise ValueError("G6 metadata-only refresh manifest is incomplete")
    current_matrix = read_json(OUTPUT_PATH)
    current_binding_hash = value_sha256(matrix_route_binding_projection(current_matrix))
    current_records = run_record_inventory(current_matrix)
    if (
        previous_matrix.get("sha256") != status_matrix_hash
        or refreshed_matrix.get("sha256") != current_matrix_hash
        or binding.get("route_count") != 46
        or binding.get("all_46_route_bindings_unchanged") is not True
        or binding.get("previous_sha256") != current_binding_hash
        or binding.get("refreshed_sha256") != current_binding_hash
        or status_binding.get("sha256") != sha256(STATUS_PATH)
        or status_binding.get("preserved_without_rewrite") is not True
        or records.get("count") != 46
        or records.get("inventory_sha256") != value_sha256(current_records)
        or records.get("preserved_without_rewrite") is not True
    ):
        raise ValueError("G6 metadata-only refresh manifest does not preserve the current route evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the generated matrix")
    parser.add_argument("--check", action="store_true", help="fail when the committed matrix is absent or stale")
    parser.add_argument(
        "--output-root",
        type=Path,
        help=(
            "project-local Results directory for a new frozen matrix; the default preserves "
            "the historical G6 evidence root"
        ),
    )
    parser.add_argument(
        "--refresh-native-serialization",
        action="store_true",
        help="archive and re-freeze only the audited MWORKS direct-graph native serialization hash transition",
    )
    parser.add_argument(
        "--refresh-metadata-only",
        action="store_true",
        help="refresh only post-G6 map metadata after proving all 46 route bindings and evidence files are unchanged",
    )
    args = parser.parse_args()
    configure_output_root(args.output_root)
    if args.write == args.check:
        parser.error("use exactly one of --write or --check")
    if args.refresh_native_serialization and not args.write:
        parser.error("--refresh-native-serialization requires --write")
    if args.refresh_metadata_only and not args.write:
        parser.error("--refresh-metadata-only requires --write")
    if args.refresh_native_serialization and args.refresh_metadata_only:
        parser.error("metadata-only and native-serialization refresh modes are mutually exclusive")
    try:
        matrix = build()
        expected = dump(matrix)
        if args.write:
            OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
            native_refresh_manifest = None
            metadata_refresh_manifest = None
            if args.refresh_native_serialization:
                if not OUTPUT_PATH.is_file():
                    raise ValueError("G6 native hash refresh requires an existing frozen matrix")
                native_refresh_manifest = archive_native_hash_refresh(read_json(OUTPUT_PATH), matrix)
            elif args.refresh_metadata_only:
                if not OUTPUT_PATH.is_file():
                    raise ValueError("G6 metadata-only refresh requires an existing frozen matrix")
                metadata_refresh_manifest = prepare_metadata_only_refresh(
                    read_json(OUTPUT_PATH), matrix, expected
                )
            elif OUTPUT_PATH.is_file() and status_has_terminal_results():
                raise ValueError(
                    "G6 matrix has terminal evidence; use --refresh-metadata-only only when all 46 route bindings are unchanged, or the explicit native/source supersession workflow"
                )
            OUTPUT_PATH.write_text(expected, encoding="utf-8", newline="\n")
            if not STATUS_PATH.is_file() or not status_has_terminal_results():
                STATUS_PATH.write_text(
                    dump(initial_execution_status(matrix)), encoding="utf-8", newline="\n"
                )
            if native_refresh_manifest is not None:
                NATIVE_HASH_REFRESH_MANIFEST.write_text(
                    dump(native_refresh_manifest), encoding="utf-8", newline="\n"
                )
            if metadata_refresh_manifest is not None:
                if sha256(STATUS_PATH) != metadata_refresh_manifest["status"]["sha256"]:
                    raise ValueError("G6 execution status changed during metadata-only refresh")
                if value_sha256(run_record_inventory(read_json(OUTPUT_PATH))) != metadata_refresh_manifest["run_records"]["inventory_sha256"]:
                    raise ValueError("a matrix-bound G6 run record changed during metadata-only refresh")
                METADATA_ONLY_REFRESH_MANIFEST.write_text(
                    dump(metadata_refresh_manifest), encoding="utf-8", newline="\n"
                )
            report = {
                "ok": True,
                "matrix": relative(OUTPUT_PATH),
                "summary": matrix["summary"],
                "native_hash_refresh": native_refresh_manifest,
                "metadata_only_refresh": metadata_refresh_manifest,
            }
        else:
            if not OUTPUT_PATH.is_file() or not equals_for_check(
                matrix, OUTPUT_PATH.read_text(encoding="utf-8")
            ):
                raise ValueError("G6 execution matrix is absent or stale")
            validate_status_matrix_continuity()
            report = {"ok": True, "matrix": relative(OUTPUT_PATH), "summary": matrix["summary"]}
    except Exception as exc:
        report = {"ok": False, "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
