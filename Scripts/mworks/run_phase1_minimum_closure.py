#!/usr/bin/env python3
"""Execute the user-authorized Phase 1 minimum-closure matrix.

Phase 1 is deliberately a readiness gate, not controller selection.  It
freezes the 46 current MWORKS candidates, executes every route for which a
truthful plant-coupled ClimbPath harness exists, and creates an explicit
terminal failure record for routes that still lack such an adapter.  A
controller-only graphical probe is never substituted for aircraft tracking.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results" / "control_platform" / "phase1_minimum_closure"
INTERFACE_MATRIX_PATH = ROOT / "Config" / "control_platform" / "controller_route_interface_matrix.json"
HARNESS_MAP_PATH = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
HISTORICAL_G6_MATRIX_PATH = (
    ROOT / "Results" / "model_library_refactor" / "controller_route_execution_current" / "G6_EXECUTION_MATRIX.json"
)
CFUNCTION_CHECK_SCRIPT = ROOT / "Scripts" / "control_platform" / "build_g6_champion_cfunction_adapters.py"

MCP_DIR = ROOT / "Scripts" / "mworks"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

from run_g6_controller_execution import (  # noqa: E402
    JsonlMcpClient,
    artifact,
    capture_phase,
    classify_error,
    close_dedicated_session,
    extract_tool_log,
    initialize_mcp_client,
    mworks_pid_for_port,
    now_iso,
    preload_base_packages,
    prepare_route_native_result,
    read_json,
    relative,
    resolve_wrapper,
    sha256,
    show_native_plot,
    simulate_modelingpy,
    wait_for_fresh_result_artifacts,
    wrapper_command,
    write_csv,
    write_json,
    write_metrics,
    write_native_result_manifest,
)
from run_g6_formal_champion import materialize_package_roots_after_target  # noqa: E402
from run_sysplorer_mcp_smoke import DEFAULT_VARIABLES, resolve_native_result_dir  # noqa: E402


SCHEMA = "mosim.phase1_minimum_closure.v1"
MATRIX_SCHEMA = "mosim.phase1_minimum_closure_matrix.v1"
STATUS_SCHEMA = "mosim.phase1_minimum_closure_status.v1"
TERMINAL_STATUSES = {"pass", "fail"}
STOP_TIME_S = 50.0
TERMINAL_ERROR_LIMIT_M = 5.0

RUNNER_VARIABLES = {
    "time": "time",
    "x": "position[1]",
    "y": "position[2]",
    "z": "position[3]",
    "x_ref": "position_ref[1]",
    "y_ref": "position_ref[2]",
    "z_ref": "position_ref[3]",
    "roll": "attitude[1]",
    "pitch": "attitude[2]",
    "yaw": "attitude[3]",
    "u1": "rotor_command[1]",
    "u2": "rotor_command[2]",
    "u3": "rotor_command[3]",
    "u4": "rotor_command[4]",
    "position_error_norm": "position_error_norm",
}
PLOT_VARIABLES = {
    key: RUNNER_VARIABLES[key]
    for key in ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")
}
LEGACY_VARIABLES = dict(DEFAULT_VARIABLES)
LEGACY_PLOT_VARIABLES = {
    key: LEGACY_VARIABLES[key]
    for key in ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")
}

FORMAL_BINDING_FILES = {
    "cascade_pid": ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "cascade_pid.json",
    "lqr_baseline": ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "lqr_baseline.json",
    "super_twisting_smc": ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "super_twisting_smc.json",
    "linear_mpc": ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "linear_mpc.json",
    "dfbc_high_order_attitude": ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "dfbc_high_order_attitude.json",
    "trained_neural_residual": ROOT / "Config" / "control_platform" / "g6_champion_bindings" / "trained_neural_residual.json",
}
OFFICIAL_PID_BINDING = {
    "target": {
        "model_file": "Models/MoSimQuadrotorModel/Experiment/Runners/OfficialPidFormalRunner.mo",
        "model_class": "MoSimQuadrotorModel.Experiment.Runners.OfficialPidFormalRunner",
    },
    "formal_adapter": {
        "model_file": "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDRotorAdapter.mo",
        "model_class": "MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter",
        "output_boundary": "ROTOR_COMMAND",
    },
}


def project_file(relative_path: str) -> Path:
    path = (ROOT / relative_path).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"path leaves project root: {relative_path}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"required project file is absent: {relative_path}")
    return path


def json_file(path: Path) -> dict[str, Any]:
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative(path)}")
    return value


def source_entry(path_text: str, role: str, *, declared_sha256: str | None = None) -> dict[str, str]:
    path = project_file(path_text)
    current_hash = sha256(path)
    return {
        "role": role,
        "path": relative(path) or str(path),
        "sha256": current_hash,
        "declared_sha256": declared_sha256 or current_hash,
    }


def historical_prerequisites() -> dict[str, list[dict[str, str]]]:
    """Carry only the active Sysblock preload identities into the new matrix."""

    if not HISTORICAL_G6_MATRIX_PATH.is_file():
        return {}
    historical = json_file(HISTORICAL_G6_MATRIX_PATH)
    rows = historical.get("rows")
    if not isinstance(rows, list):
        return {}
    result: dict[str, list[dict[str, str]]] = {}
    for item in rows:
        if not isinstance(item, dict) or not isinstance(item.get("scheme_id"), str):
            continue
        prerequisites = item.get("model_load_prerequisites")
        if not isinstance(prerequisites, list):
            continue
        entries: list[dict[str, str]] = []
        for prerequisite in prerequisites:
            if not isinstance(prerequisite, dict):
                continue
            path_text = prerequisite.get("model_file")
            model_class = prerequisite.get("model_class")
            if not isinstance(path_text, str) or not isinstance(model_class, str):
                continue
            source = source_entry(path_text, str(prerequisite.get("role") or "prerequisite"))
            source["model_class"] = model_class
            entries.append(source)
        if entries:
            result[str(item["scheme_id"])] = entries
    return result


def binding_route(scheme_id: str, category: str, boundary: str) -> dict[str, Any]:
    if scheme_id == "official_pid":
        binding = OFFICIAL_PID_BINDING
        binding_file = None
        source_bindings = [
            source_entry(binding["target"]["model_file"], "formal_runner"),
            source_entry(binding["formal_adapter"]["model_file"], "formal_adapter"),
            source_entry("Models/MoSimQuadrotorModel/Experiment/Runners/RotorCommandRunner.mo", "shared_runner"),
            source_entry("Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo", "shared_plant"),
        ]
    else:
        binding_file = FORMAL_BINDING_FILES[scheme_id]
        binding = json_file(binding_file)
        target = binding.get("target")
        adapter = binding.get("formal_adapter")
        if not isinstance(target, dict) or not isinstance(adapter, dict):
            raise ValueError(f"formal binding is incomplete: {relative(binding_file)}")
        source_bindings = []
        for item in binding.get("source_bindings", []):
            if not isinstance(item, dict):
                continue
            path_text = item.get("path")
            role = item.get("role")
            expected = item.get("expected_sha256")
            if isinstance(path_text, str) and isinstance(role, str):
                source_bindings.append(source_entry(path_text, role, declared_sha256=expected if isinstance(expected, str) else None))
        if not source_bindings:
            raise ValueError(f"formal binding has no source bindings: {relative(binding_file)}")
    target = binding["target"]
    adapter = binding["formal_adapter"]
    target_file = project_file(str(target["model_file"]))
    return {
        "scheme_id": scheme_id,
        "category": category,
        "target_boundary": boundary,
        "execution_kind": "adapter_backed_whole_aircraft",
        "target": {
            "model_file": relative(target_file),
            "model_class": str(target["model_class"]),
            "sha256": sha256(target_file),
        },
        "adapter": {
            "model_file": str(adapter["model_file"]),
            "model_class": str(adapter["model_class"]),
            "output_boundary": str(adapter.get("output_boundary") or boundary),
            "sha256": sha256(project_file(str(adapter["model_file"]))),
        },
        "binding_file": relative(binding_file) if binding_file else None,
        "source_bindings": source_bindings,
        "variables_profile": "shared_runner",
        "rematerialize_package_root": True,
        "model_load_prerequisites": [],
        "claim_boundary": (
            "Offline MWORKS whole-aircraft ClimbPath closure through the named current adapter and "
            "shared Sunray150Assembly only. It is not controller-family selection, seven-scenario "
            "comparison, code generation, Gazebo, PX4, ROS, or flight-runtime evidence."
        ),
    }


def fixed_route(
    route: dict[str, Any],
    harness: dict[str, Any],
    prerequisites: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    scheme_id = str(route["scheme_id"])
    target_file = str(harness["public_entry_file"])
    source_file = str(harness["whole_aircraft_source_file"])
    target = project_file(target_file)
    return {
        "scheme_id": scheme_id,
        "category": str(route["category"]),
        "target_boundary": "WHOLE_AIRCRAFT_EMBEDDED",
        "execution_kind": "fixed_integrated_whole_aircraft",
        "target": {
            "model_file": relative(target),
            "model_class": str(harness["public_entry_class"]),
            "sha256": sha256(target),
        },
        "adapter": None,
        "binding_file": None,
        "source_bindings": [
            source_entry(target_file, "formal_public_alias"),
            source_entry(source_file, "whole_aircraft_source"),
            *prerequisites.get(scheme_id, []),
        ],
        "variables_profile": "legacy_whole_aircraft",
        "rematerialize_package_root": False,
        "model_load_prerequisites": prerequisites.get(scheme_id, []),
        "claim_boundary": (
            "Offline MWORKS whole-aircraft ClimbPath closure of the named fixed integrated chain only. "
            "It is not controller-family selection, seven-scenario comparison, code generation, Gazebo, "
            "PX4, ROS, or flight-runtime evidence."
        ),
    }


def missing_adapter_route(route: dict[str, Any]) -> dict[str, Any]:
    current = route.get("current_model") if isinstance(route.get("current_model"), dict) else {}
    surface = route.get("current_graphical_surface") if isinstance(route.get("current_graphical_surface"), dict) else {}
    integration = route.get("integration") if isinstance(route.get("integration"), dict) else {}
    target_contract = integration.get("target_contract") if isinstance(integration.get("target_contract"), dict) else {}
    model_file = str(current.get("file") or "")
    source_bindings = [source_entry(model_file, "graphical_controller_core")] if model_file else []
    target_boundary = str(target_contract.get("boundary") or "unresolved")
    input_mode = str(surface.get("input_mode") or "unknown")
    return {
        "scheme_id": str(route["scheme_id"]),
        "category": str(route["category"]),
        "target_boundary": target_boundary,
        "execution_kind": "adapter_missing",
        "target": {
            "model_file": model_file or None,
            "model_class": current.get("class"),
            "sha256": source_bindings[0]["sha256"] if source_bindings else None,
        },
        "adapter": None,
        "binding_file": None,
        "source_bindings": source_bindings,
        "variables_profile": None,
        "rematerialize_package_root": False,
        "model_load_prerequisites": [],
        "adapter_missing_reason": (
            f"The current graphical core exposes {input_mode} and has no project-owned adapter that "
            f"implements the {target_boundary} runner contract for this scheme. A ClimbPath plant closure "
            "would therefore require an unimplemented interface translation and cannot be truthfully simulated."
        ),
        "claim_boundary": (
            "No aircraft-tracking simulation was executed. This terminal failure records a missing current "
            "plant-coupled adapter; it is not an internal graphical-probe result."
        ),
    }


def build_matrix() -> dict[str, Any]:
    interface = json_file(INTERFACE_MATRIX_PATH)
    harness_map = json_file(HARNESS_MAP_PATH)
    routes = interface.get("routes")
    schemes = harness_map.get("schemes")
    if not isinstance(routes, list) or len(routes) != 46:
        raise ValueError("controller route interface matrix must contain exactly 46 routes")
    if not isinstance(schemes, list):
        raise ValueError("formal harness map schemes must be a list")
    harness_by_id = {str(item.get("scheme_id")): item for item in schemes if isinstance(item, dict)}
    prerequisites = historical_prerequisites()
    matrix_rows: list[dict[str, Any]] = []
    for route in sorted((item for item in routes if isinstance(item, dict)), key=lambda item: str(item.get("scheme_id"))):
        scheme_id = str(route.get("scheme_id"))
        category = str(route.get("category"))
        integration = route.get("integration") if isinstance(route.get("integration"), dict) else {}
        target_contract = integration.get("target_contract") if isinstance(integration.get("target_contract"), dict) else {}
        boundary = str(target_contract.get("boundary") or "WHOLE_AIRCRAFT_EMBEDDED")
        if scheme_id in FORMAL_BINDING_FILES or scheme_id == "official_pid":
            row = binding_route(scheme_id, category, boundary)
        elif category == "fixed_integrated":
            scheme = harness_by_id.get(scheme_id)
            harness = scheme.get("canonical_closed_loop_harness") if isinstance(scheme, dict) else None
            if not isinstance(harness, dict):
                raise ValueError(f"fixed chain lacks canonical harness mapping: {scheme_id}")
            row = fixed_route(route, harness, prerequisites)
        else:
            row = missing_adapter_route(route)
        matrix_rows.append(row)
    if len(matrix_rows) != 46 or len({str(row["scheme_id"]) for row in matrix_rows}) != 46:
        raise ValueError("Phase 1 route matrix does not have exactly 46 unique rows")
    actual_count = sum(row["execution_kind"] != "adapter_missing" for row in matrix_rows)
    return {
        "schema": MATRIX_SCHEMA,
        "purpose": "Frozen Phase 1 50 s ClimbPath minimum-closure worklist.",
        "scenario": {
            "scenario_id": "climb_path_50s",
            "reference_owner": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
            "duration_s": STOP_TIME_S,
            "terminal_position_error_limit_m": TERMINAL_ERROR_LIMIT_M,
        },
        "route_count": len(matrix_rows),
        "truthfully_runnable_route_count": actual_count,
        "adapter_missing_route_count": len(matrix_rows) - actual_count,
        "source_inputs": {
            "interface_matrix": {"path": relative(INTERFACE_MATRIX_PATH), "sha256": sha256(INTERFACE_MATRIX_PATH)},
            "formal_harness_map": {"path": relative(HARNESS_MAP_PATH), "sha256": sha256(HARNESS_MAP_PATH)},
            "historical_prerequisite_source": {
                "path": relative(HISTORICAL_G6_MATRIX_PATH) if HISTORICAL_G6_MATRIX_PATH.is_file() else None,
                "sha256": sha256(HISTORICAL_G6_MATRIX_PATH) if HISTORICAL_G6_MATRIX_PATH.is_file() else None,
            },
        },
        "rows": matrix_rows,
    }


def stable_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in matrix.items() if key != "generated_at"}


def freeze_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    path = RESULT_ROOT / "PHASE1_MATRIX.json"
    if path.is_file():
        existing = json_file(path)
        if stable_matrix(existing) != stable_matrix(matrix):
            raise RuntimeError(
                "Existing Phase 1 matrix differs from current source bindings; use a new result root or explicitly archive it before changing the frozen execution set."
            )
        return existing
    frozen = dict(matrix)
    frozen["generated_at"] = now_iso()
    write_json(path, frozen)
    return frozen


def run_cfunction_check() -> dict[str, Any]:
    output = RESULT_ROOT / "CFunctionConsistency" / "cfunction_check.json"
    completed = subprocess.run(
        [sys.executable, str(CFUNCTION_CHECK_SCRIPT), "--check"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=120,
        check=False,
    )
    try:
        parsed = json.loads(completed.stdout) if completed.stdout.strip() else None
    except json.JSONDecodeError:
        parsed = None
    result = {
        "schema": "mosim.phase1_cfunction_consistency_check.v1",
        "checked_at": now_iso(),
        "command": ["python", "Scripts/control_platform/build_g6_champion_cfunction_adapters.py", "--check"],
        "exit_code": completed.returncode,
        "ok": completed.returncode == 0,
        "result": parsed,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    write_json(output, result)
    return result


def run_dir_for(row: dict[str, Any]) -> Path:
    return RESULT_ROOT / str(row["scheme_id"])


def existing_terminal_record(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "RUN_RECORD.json"
    if not path.is_file():
        return None
    try:
        record = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    return record if isinstance(record, dict) and record.get("status") in TERMINAL_STATUSES else None


def archive_existing_record(run_dir: Path) -> str | None:
    existing = existing_terminal_record(run_dir)
    if existing is None:
        return None
    archive = run_dir / "superseded" / time.strftime("%Y%m%d_%H%M%S")
    archive.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    for name in ("RUN_RECORD.json", "PHASE1_ROUTE_STATUS.json", "logs", "raw", "metrics", "screenshots"):
        source = run_dir / name
        destination = archive / name
        if source.is_file():
            shutil.copy2(source, destination)
            copied.append(relative(destination) or str(destination))
        elif source.is_dir():
            shutil.copytree(source, destination)
            copied.append(relative(destination) or str(destination))
    write_json(
        archive / "ARCHIVE_MANIFEST.json",
        {
            "schema": "mosim.phase1_minimum_closure_superseded_run.v1",
            "archived_at": now_iso(),
            "source_run_dir": relative(run_dir),
            "copied": copied,
        },
    )
    return relative(archive)


def source_hash_observations(row: dict[str, Any], phase: str) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for source in row.get("source_bindings", []):
        if not isinstance(source, dict):
            continue
        path_text = source.get("path")
        if not isinstance(path_text, str):
            continue
        path = project_file(path_text)
        current = sha256(path)
        expected = source.get("sha256")
        declared = source.get("declared_sha256")
        observations.append(
            {
                "phase": phase,
                "role": source.get("role"),
                "path": relative(path),
                "sha256": current,
                "frozen_sha256": expected,
                "declared_sha256": declared,
                "matches_frozen": current == expected,
                "matches_declared": declared is None or current == declared,
            }
        )
        if current != expected:
            raise RuntimeError(f"source hash changed during {phase}: {path_text} {current} != {expected}")
    return observations


def load_prerequisites(client: JsonlMcpClient, row: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in row.get("model_load_prerequisites", []):
        if not isinstance(item, dict):
            continue
        path_text = item.get("path")
        model_class = item.get("model_class")
        if not isinstance(path_text, str) or not isinstance(model_class, str):
            raise RuntimeError(f"incomplete model prerequisite for {row['scheme_id']}")
        path = project_file(path_text)
        check_hash = sha256(path)
        if check_hash != item.get("sha256"):
            raise RuntimeError(f"prerequisite hash changed: {path_text}")
        response = client.call_tool(
            "model_manager",
            {"action": "load_file", "file_path": str(path), "force_reload": False, "auto_load_deps": True},
            timeout_s=300,
        )
        entry = {
            "role": item.get("role"),
            "path": relative(path),
            "model_class": model_class,
            "sha256": check_hash,
            "ok": bool(response.get("ok")),
            "response": response,
        }
        results.append(entry)
        if not entry["ok"]:
            raise RuntimeError(f"model prerequisite load failed: {entry}")
    return results


def add_derived_position_error(series: dict[str, list[float]]) -> float:
    aliases = ("x", "y", "z", "x_ref", "y_ref", "z_ref")
    if any(alias not in series for alias in aliases):
        raise RuntimeError("cannot derive terminal position error because tracking series are incomplete")
    count = min(len(series[alias]) for alias in aliases)
    if count <= 0:
        raise RuntimeError("cannot derive terminal position error from empty tracking series")
    errors: list[float] = []
    for index in range(count):
        values = [float(series[alias][index]) for alias in aliases]
        if not all(math.isfinite(value) for value in values):
            errors.append(float("nan"))
            continue
        errors.append(math.sqrt(
            (values[3] - values[0]) ** 2 + (values[4] - values[1]) ** 2 + (values[5] - values[2]) ** 2
        ))
    series["position_error_norm"] = errors
    terminal = errors[-1]
    if not math.isfinite(terminal):
        raise RuntimeError("terminal position_error_norm is non-finite")
    return terminal


def route_variables(row: dict[str, Any]) -> tuple[dict[str, str], dict[str, str], bool]:
    if row["variables_profile"] == "shared_runner":
        return dict(RUNNER_VARIABLES), dict(PLOT_VARIABLES), True
    if row["variables_profile"] == "legacy_whole_aircraft":
        return dict(LEGACY_VARIABLES), dict(LEGACY_PLOT_VARIABLES), False
    raise ValueError(f"unsupported variable profile: {row['variables_profile']}")


def capture_optional(
    record: dict[str, Any],
    *,
    run_dir: Path,
    phase: str,
    target_class: str,
    expected_pid: int | None,
    capture_surface: str,
) -> None:
    destination = run_dir / "screenshots" / ("01_after_check.png" if phase == "after_check" else "02_result_window.png")
    try:
        capture = capture_phase(
            run_dir=run_dir,
            phase=phase,
            target_class=target_class,
            expected_pid=expected_pid,
            destination=destination,
            capture_surface=capture_surface,
        )
        record["mworks_phase_screenshots"].append(capture)
    except Exception as exc:
        record.setdefault("evidence_warnings", []).append(
            {"phase": phase, "kind": "screenshot_failed", "message": str(exc)}
        )


def write_route_status(record: dict[str, Any], run_dir: Path) -> None:
    write_json(
        run_dir / "PHASE1_ROUTE_STATUS.json",
        {
            "schema": STATUS_SCHEMA,
            "generated_at": now_iso(),
            "scheme_id": record["scheme_id"],
            "status": record["status"],
            "failure_class": record.get("failure_class"),
            "terminal_position_error_norm_m": record.get("terminal_position_error_norm_m"),
            "run_record": relative(run_dir / "RUN_RECORD.json"),
        },
    )


def finalize_artifacts(record: dict[str, Any], run_dir: Path, log_path: Path) -> None:
    for candidate in (
        artifact(log_path, "log"),
        artifact(run_dir / "logs" / "check_model_direct.json", "log"),
        artifact(run_dir / "logs" / "simulate_model_direct.json", "log"),
        artifact(run_dir / "raw" / "result.csv", "raw"),
        artifact(run_dir / "metrics" / "metrics.json", "metrics"),
        artifact(run_dir / "metrics" / "metrics.csv", "metrics"),
        artifact(run_dir / "screenshots" / "01_after_check.png", "figure"),
        artifact(run_dir / "screenshots" / "02_result_window.png", "figure"),
    ):
        if candidate and candidate not in record["artifact_refs"]:
            record["artifact_refs"].append(candidate)
    write_json(
        run_dir / "logs" / "screenshot_manifest.json",
        {
            "schema": "mosim.phase1_minimum_closure_screenshot_manifest.v1",
            "scheme_id": record["scheme_id"],
            "target": record.get("matrix_row", {}).get("target"),
            "captures": record.get("mworks_phase_screenshots", []),
            "warnings": record.get("evidence_warnings", []),
        },
    )


def run_adapter_missing(row: dict[str, Any], matrix_path: Path, *, rerun: bool) -> dict[str, Any]:
    run_dir = run_dir_for(row)
    if rerun:
        archive_existing_record(run_dir)
    for directory in (run_dir / "logs", run_dir / "raw", run_dir / "metrics", run_dir / "screenshots"):
        directory.mkdir(parents=True, exist_ok=True)
    record = {
        "schema": SCHEMA,
        "scheme_id": row["scheme_id"],
        "category": row["category"],
        "scenario_id": "climb_path_50s",
        "started_at": now_iso(),
        "finished_at": now_iso(),
        "run_dir": relative(run_dir),
        "status": "fail",
        "failure_class": "adapter_missing",
        "simulation_completed": False,
        "terminal_position_error_norm_m": None,
        "matrix": {"path": relative(matrix_path), "sha256": sha256(matrix_path)},
        "matrix_row": row,
        "source": "static_interface_audit",
        "live_mworks_touched": False,
        "will_not_click_activation_login": True,
        "claim_boundary": row["claim_boundary"],
        "reason": row["adapter_missing_reason"],
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": [
            "No MWORKS simulation was started because the route has no truthful plant-coupled adapter at its declared runner boundary."
        ],
        "artifact_refs": [],
        "source_hash_observations": source_hash_observations(row, "static_record"),
    }
    write_json(run_dir / "RUN_RECORD.json", record)
    write_route_status(record, run_dir)
    return record


def run_real_route(row: dict[str, Any], matrix_path: Path, *, rerun: bool, wrapper: str | None) -> dict[str, Any]:
    run_dir = run_dir_for(row)
    if rerun:
        supersedes = archive_existing_record(run_dir)
    else:
        supersedes = None
    for directory in (run_dir / "logs", run_dir / "raw", run_dir / "metrics", run_dir / "screenshots"):
        directory.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "logs" / "mcp.jsonl"
    log_path.write_text("", encoding="utf-8")
    target = row["target"]
    target_file = project_file(str(target["model_file"]))
    target_class = str(target["model_class"])
    variables, plot_variables, explicit_error = route_variables(row)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "scheme_id": row["scheme_id"],
        "category": row["category"],
        "scenario_id": "climb_path_50s",
        "started_at": now_iso(),
        "run_dir": relative(run_dir),
        "status": "running",
        "simulation_completed": False,
        "terminal_position_error_norm_m": None,
        "matrix": {"path": relative(matrix_path), "sha256": sha256(matrix_path)},
        "matrix_row": row,
        "source": "MWORKS_MCP",
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "claim_boundary": row["claim_boundary"],
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": [],
        "artifact_refs": [],
        "source_hash_observations": [],
    }
    if supersedes:
        record["supersedes"] = supersedes
    client = JsonlMcpClient(wrapper_command(resolve_wrapper(wrapper)), log_path)
    cleanup: dict[str, Any] | None = None
    session: dict[str, Any] | None = None
    try:
        record["source_hash_observations"].extend(source_hash_observations(row, "before_session"))
        health = initialize_mcp_client(client)
        startup = health.get("sysplorer_startup") if isinstance(health.get("sysplorer_startup"), dict) else {}
        port = startup.get("dedicated_sysplorer_port")
        expected_pid = mworks_pid_for_port(port)
        session = {
            "health": health,
            "dedicated_sysplorer_port": port,
            "mworks_pid": expected_pid,
            "mcp_log": relative(log_path),
        }
        record["session"] = session
        record["base_package_preload"] = preload_base_packages(client)
        record["model_load_prerequisites"] = load_prerequisites(client, row)
        record["source_hash_observations"].extend(source_hash_observations(row, "after_prerequisite_load"))
        load = client.call_tool(
            "model_manager",
            {"action": "load_file", "file_path": str(target_file), "force_reload": False, "auto_load_deps": True},
            timeout_s=300,
        )
        write_json(run_dir / "logs" / "load_model.json", load)
        if not load.get("ok"):
            raise RuntimeError(f"model load failed: {load}")
        if row.get("rematerialize_package_root"):
            record["package_root_materialization"] = materialize_package_roots_after_target(client)
            write_json(run_dir / "logs" / "package_root_materialization.json", record["package_root_materialization"])
        record["source_hash_observations"].extend(source_hash_observations(row, "after_load"))
        check = client.call_tool("check_model", {"model_name": target_class, "stop_on_error": True}, timeout_s=300)
        write_json(run_dir / "logs" / "check_model_direct.json", check)
        if not check.get("ok"):
            raise RuntimeError(f"CheckModel failed: {check}")
        record["source_hash_observations"].extend(source_hash_observations(row, "after_check"))
        opened = client.call_tool("model_manager", {"action": "open", "model_name": target_class}, timeout_s=60)
        write_json(run_dir / "logs" / "open_model.json", opened)
        if not opened.get("ok"):
            record.setdefault("evidence_warnings", []).append({"phase": "after_check", "kind": "model_open_failed", "message": str(opened)})
        else:
            capture_optional(
                record,
                run_dir=run_dir,
                phase="after_check",
                target_class=target_class,
                expected_pid=expected_pid,
                capture_surface="model",
            )
        raw_output = run_dir / "raw" / "result.csv"
        metrics_json = run_dir / "metrics" / "metrics.json"
        metrics_csv = run_dir / "metrics" / "metrics.csv"
        native_dir, native_manifest = resolve_native_result_dir(raw_output, run_dir / "native_result", target_class)
        native_dir, expected_native, native_root = prepare_route_native_result(native_dir, target_class)
        record["native_result_root"] = native_root
        started_unix = time.time()
        simulation = simulate_modelingpy(
            client,
            model_name=target_class,
            target_time=[0.0, STOP_TIME_S],
            native_result_dir=native_dir,
            verify_result_var=variables["z"],
            verify_time_point="end",
        )
        write_json(run_dir / "logs" / "simulate_model_direct.json", simulation)
        if not simulation.get("ok"):
            raise RuntimeError(f"simulation failed: {simulation}")
        if simulation.get("simulate_api_reported_failure"):
            record["mworks_phase_observations"].append(
                "SimulateModel reported false; current native result and complete time-series freshness remain the acceptance gate."
            )
        readiness = wait_for_fresh_result_artifacts(
            client,
            model_name=target_class,
            variables=variables,
            native_dir=native_dir,
            expected_native=expected_native,
            expected_stop_time=STOP_TIME_S,
            not_before_unix=started_unix,
        )
        record["result_readiness"] = readiness["readiness"]
        native_result = readiness["native_result"]
        series = readiness["series"]
        write_native_result_manifest(native_manifest, native_result_dir=native_dir, native_result=native_result, model_name=target_class)
        record["native_result_locator"] = relative(native_result)
        if explicit_error:
            error_values = series.get("position_error_norm", [])
            if not error_values:
                raise RuntimeError("runner did not expose position_error_norm")
            terminal_error = float(error_values[-1])
            if not math.isfinite(terminal_error):
                raise RuntimeError("terminal position_error_norm is non-finite")
        else:
            terminal_error = add_derived_position_error(series)
            variables["position_error_norm"] = "derived_from_position_and_reference"
        write_csv(series, variables, raw_output)
        write_metrics(
            raw_output,
            metrics_json,
            metrics_csv,
            "climb_path_50s",
            str(row["scheme_id"]),
            str(row["execution_kind"]),
            "standard_tracking",
        )
        metrics = json_file(metrics_json)
        if not metrics.get("valid"):
            raise RuntimeError(f"tracking metrics are invalid: {metrics}")
        record["simulation_completed"] = True
        record["terminal_position_error_norm_m"] = terminal_error
        record["metrics_summary"] = {
            "row_count": metrics.get("row_count"),
            "duration_s": metrics.get("duration_s"),
            "nan_count": metrics.get("nan_count"),
            "valid": metrics.get("valid"),
        }
        if terminal_error < TERMINAL_ERROR_LIMIT_M:
            record["status"] = "pass"
        else:
            record["status"] = "fail"
            record["failure_class"] = "terminal_position_error_exceeds_limit"
        try:
            plot = show_native_plot(client, native_result=native_result, variables=plot_variables)
            write_json(run_dir / "logs" / "open_native_result_plot.json", plot)
            capture_optional(
                record,
                run_dir=run_dir,
                phase="result_window",
                target_class=target_class,
                expected_pid=expected_pid,
                capture_surface="result_viewer",
            )
        except Exception as exc:
            record.setdefault("evidence_warnings", []).append(
                {"phase": "result_window", "kind": "native_plot_or_capture_failed", "message": str(exc)}
            )
        record["mworks_phase_observations"].append(
            "A fresh native result reached 50 s and was evaluated against the Phase 1 terminal position-error gate."
        )
        record["source_hash_observations"].extend(source_hash_observations(row, "before_cleanup"))
    except Exception as exc:
        message = str(exc)
        record["status"] = "fail"
        record["failure_class"] = "source_hash_mismatch" if "source hash changed" in message else classify_error(message)
        record["error"] = {"message": message, "traceback": traceback.format_exc()}
    finally:
        try:
            cleanup = close_dedicated_session(client, session=session, output=run_dir / "logs" / "session_cleanup.json")
        finally:
            client.close()
        record["session_cleanup"] = cleanup
        if cleanup.get("requested") and not cleanup.get("verified_closed") and record.get("status") == "pass":
            record["status"] = "fail"
            record["failure_class"] = "session_cleanup_unverified"
        try:
            record["source_hash_observations"].extend(source_hash_observations(row, "after_session_shutdown"))
        except Exception as exc:
            record["status"] = "fail"
            record["failure_class"] = "source_hash_mismatch"
            record.setdefault("error", {"message": str(exc), "traceback": traceback.format_exc()})
        extract_tool_log(log_path, "check_model", run_dir / "logs" / "check_model.json")
        extract_tool_log(log_path, "call_code", run_dir / "logs" / "simulate_model.json")
        record["finished_at"] = now_iso()
        finalize_artifacts(record, run_dir, log_path)
        write_json(run_dir / "RUN_RECORD.json", record)
        write_route_status(record, run_dir)
    return record


def write_status(matrix: dict[str, Any], cfunction_check: dict[str, Any]) -> dict[str, Any]:
    rows = matrix["rows"]
    records: list[dict[str, Any]] = []
    for row in rows:
        record = existing_terminal_record(run_dir_for(row))
        if record:
            records.append(record)
    passed = [record for record in records if record.get("status") == "pass"]
    failed = [record for record in records if record.get("status") == "fail"]
    failure_counts: dict[str, int] = {}
    for record in failed:
        name = str(record.get("failure_class") or "unspecified")
        failure_counts[name] = failure_counts.get(name, 0) + 1
    status = {
        "schema": STATUS_SCHEMA,
        "generated_at": now_iso(),
        "matrix": {"path": relative(RESULT_ROOT / "PHASE1_MATRIX.json"), "sha256": sha256(RESULT_ROOT / "PHASE1_MATRIX.json")},
        "route_count": len(rows),
        "terminal_record_count": len(records),
        "pending_count": len(rows) - len(records),
        "passed_count": len(passed),
        "failed_count": len(failed),
        "failure_counts": failure_counts,
        "completed": len(records) == len(rows),
        "cfunction_consistency_check": {
            "ok": cfunction_check.get("ok"),
            "path": relative(RESULT_ROOT / "CFunctionConsistency" / "cfunction_check.json"),
        },
    }
    write_json(RESULT_ROOT / "PHASE1_STATUS.json", status)
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="comma-separated route IDs for a bounded retry or diagnosis")
    parser.add_argument("--rerun", action="store_true", help="archive and rerun routes that already have terminal records")
    parser.add_argument("--plan-only", action="store_true", help="freeze and report the matrix without starting MWORKS")
    parser.add_argument("--wrapper", help="optional explicit project-local Sysplorer MCP wrapper")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    matrix = freeze_matrix(build_matrix())
    cfunction_check = run_cfunction_check()
    selected = {item.strip() for item in args.only.split(",") if item.strip()} if args.only else None
    rows = matrix["rows"]
    if selected is not None:
        known = {str(row["scheme_id"]) for row in rows}
        unknown = selected - known
        if unknown:
            raise SystemExit(f"unknown Phase 1 route IDs: {', '.join(sorted(unknown))}")
        rows = [row for row in rows if row["scheme_id"] in selected]
    if args.plan_only:
        status = write_status(matrix, cfunction_check)
        print(json.dumps({"plan_rows": len(rows), "matrix": relative(RESULT_ROOT / "PHASE1_MATRIX.json"), "status": status}, ensure_ascii=False, indent=2))
        return 0

    infrastructure_stop = False
    for row in rows:
        run_dir = run_dir_for(row)
        if existing_terminal_record(run_dir) is not None and not args.rerun:
            continue
        if row["execution_kind"] == "adapter_missing":
            record = run_adapter_missing(row, RESULT_ROOT / "PHASE1_MATRIX.json", rerun=args.rerun)
        else:
            record = run_real_route(row, RESULT_ROOT / "PHASE1_MATRIX.json", rerun=args.rerun, wrapper=args.wrapper)
        status = write_status(matrix, cfunction_check)
        print(
            json.dumps(
                {
                    "scheme_id": record["scheme_id"],
                    "status": record["status"],
                    "failure_class": record.get("failure_class"),
                    "terminal_position_error_norm_m": record.get("terminal_position_error_norm_m"),
                    "terminal_records": status["terminal_record_count"],
                },
                ensure_ascii=False,
            )
        )
        if record.get("failure_class") in {"license_or_login", "internal_or_mcp"}:
            infrastructure_stop = True
            break
    final_status = write_status(matrix, cfunction_check)
    print(json.dumps(final_status, ensure_ascii=False, indent=2))
    if infrastructure_stop or final_status["pending_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
