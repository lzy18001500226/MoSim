#!/usr/bin/env python3
"""Run the G2 nominal 50 s ClimbPath validation for every FormalRunner.

This driver deliberately validates the public formal entries only.  It does
not change controller gains, Modelica sources, or scenario-injection settings.
Each runner receives a terminal record even when model checking or simulation
fails, so the result tree is a complete 48-row audit rather than a success-only
collection.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
import time
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results" / "control_platform" / "phase2_full_48_climbpath"
FORMAL_RUNNER_DIR = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Formal"
PACKAGE_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
PLANT_PATH = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Sunray150Assembly.mo"
# ClimbPath is a nested class in this package rather than a standalone .mo file.
TRAJECTORY_PATH = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Trajectories" / "package.mo"
MATRIX_PATH = RESULT_ROOT / "G2_MATRIX.json"
STATUS_PATH = RESULT_ROOT / "G2_STATUS.json"
CONTRACT_PATH = RESULT_ROOT / "G2_EXECUTION_CONTRACT.json"

STOP_TIME_S = 50.0
TERMINAL_ERROR_LIMIT_M = 5.0
SIMULATION_TIMEOUT_S = 360.0
SCHEMA = "mosim.phase2_full_48_climbpath.v1"
MATRIX_SCHEMA = "mosim.phase2_full_48_climbpath_matrix.v1"
STATUS_SCHEMA = "mosim.phase2_full_48_climbpath_status.v1"
TERMINAL_STATUSES = {"pass", "fail"}

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
PLOT_VARIABLES = {key: RUNNER_VARIABLES[key] for key in ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")}

MCP_DIR = ROOT / "Scripts" / "mworks"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

from run_g6_controller_execution import (  # noqa: E402
    JsonlMcpClient,
    artifact,
    capture_phase,
    close_dedicated_session,
    initialize_mcp_client,
    mworks_pid_for_port,
    now_iso,
    preload_base_packages,
    prepare_route_native_result,
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
from run_sysplorer_mcp_smoke import resolve_native_result_dir  # noqa: E402


ADAPTER_RE = re.compile(
    r"redeclare\s+model\s+Controller\s*=\s*"
    r"MoSimQuadrotorModel\.Control\.Adapters\.([A-Za-z0-9_]+)"
)
ADAPTER_INSTANCE_RE = re.compile(
    r"MoSimQuadrotorModel\.Control\.Adapters\.([A-Za-z0-9_]+)\s+controller\b"
)
BASE_RUNNERS = {
    "FormalAttitudeThrustRunnerBase": (
        "Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalAttitudeThrustRunnerBase.mo"
    ),
    "FormalBodyRateThrustRunnerBase": (
        "Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalBodyRateThrustRunnerBase.mo"
    ),
    "FormalRotorCommandRunnerBase": (
        "Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalRotorCommandRunnerBase.mo"
    ),
    "FormalWrenchRunnerBase": (
        "Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalWrenchRunnerBase.mo"
    ),
}

# Keep the deployment baseline aligned with its existing project-wide ID.
CONTROLLER_ID_OVERRIDES = {"Px4Ctrl": "px4ctrl"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def project_file(path_text: str) -> Path:
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"path leaves project root: {path_text}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"required project file is absent: {path_text}")
    return path


def camel_to_snake(value: str) -> str:
    tokens = re.findall(r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|\d+", value)
    return "_".join(token.lower() for token in tokens)


def controller_id_for_runner(runner_id: str) -> str:
    return CONTROLLER_ID_OVERRIDES.get(runner_id, camel_to_snake(runner_id))


def source_entry(path: Path, role: str) -> dict[str, str]:
    relative_path = relative(path)
    if not relative_path:
        raise ValueError(f"source is outside project root: {path}")
    return {"role": role, "path": relative_path, "sha256": sha256(path)}


def runner_sources(runner_file: Path) -> tuple[list[dict[str, str]], str | None]:
    source_text = runner_file.read_text(encoding="utf-8")
    sources = [
        source_entry(runner_file, "formal_runner"),
        source_entry(PACKAGE_ROOT, "package_root"),
        source_entry(PLANT_PATH, "shared_plant"),
        source_entry(TRAJECTORY_PATH, "trajectory"),
    ]
    for base_name, relative_path in BASE_RUNNERS.items():
        if base_name in source_text:
            sources.append(source_entry(project_file(relative_path), "shared_runner_base"))
    adapter_match = ADAPTER_RE.search(source_text) or ADAPTER_INSTANCE_RE.search(source_text)
    adapter_class = adapter_match.group(1) if adapter_match else None
    if adapter_class:
        adapter_path = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / f"{adapter_class}.mo"
        if adapter_path.is_file():
            sources.append(source_entry(adapter_path, "formal_adapter"))
    unique: dict[str, dict[str, str]] = {}
    for entry in sources:
        unique[entry["path"]] = entry
    return list(unique.values()), adapter_class


def build_matrix() -> dict[str, Any]:
    runner_files = sorted(
        path for path in FORMAL_RUNNER_DIR.glob("*.mo") if path.name != "package.mo"
    )
    if len(runner_files) != 48:
        raise RuntimeError(f"expected exactly 48 FormalRunner files, found {len(runner_files)}")
    rows: list[dict[str, Any]] = []
    for runner_file in runner_files:
        leaf = runner_file.stem
        controller_stem = leaf.removesuffix("FormalRunner")
        sources, adapter_class = runner_sources(runner_file)
        rows.append(
            {
                "runner_id": controller_stem,
                "controller_id": controller_id_for_runner(controller_stem),
                "runner_class": f"MoSimQuadrotorModel.Experiment.Runners.Formal.{leaf}",
                "runner_file": relative(runner_file),
                "adapter_class": adapter_class,
                "source_bindings": sources,
            }
        )
    return {
        "schema": MATRIX_SCHEMA,
        "generated_at": now_iso(),
        "scope": {
            "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
            "duration_s": STOP_TIME_S,
            "scenario_injection": "none",
            "runner_directory": relative(FORMAL_RUNNER_DIR),
            "runner_count": len(rows),
        },
        "rows": rows,
    }


def stable_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in matrix.items() if key != "generated_at"}


def freeze_matrix(matrix: dict[str, Any], *, refresh: bool) -> dict[str, Any]:
    if MATRIX_PATH.is_file():
        existing = read_json(MATRIX_PATH)
        if stable_matrix(existing) != stable_matrix(matrix):
            if not refresh:
                raise RuntimeError(
                    "G2 matrix differs from the existing frozen matrix; do not mix source revisions. "
                    "Use --refresh-matrix only before any terminal G2 record exists."
                )
            if any(RESULT_ROOT.glob("*/RUN_RECORD.json")):
                raise RuntimeError("cannot refresh G2 matrix after terminal records exist")
        else:
            return existing
    write_json(MATRIX_PATH, matrix)
    return matrix


def source_observations(row: dict[str, Any], phase: str) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for source in row["source_bindings"]:
        path = project_file(str(source["path"]))
        current = sha256(path)
        expected = str(source["sha256"])
        observations.append(
            {
                "phase": phase,
                "role": source["role"],
                "path": source["path"],
                "sha256": current,
                "frozen_sha256": expected,
                "matches_frozen": current == expected,
            }
        )
        if current != expected:
            raise RuntimeError(
                f"source hash changed during {phase}: {source['path']} {current} != {expected}"
            )
    return observations


def run_dir_for(row: dict[str, Any]) -> Path:
    return RESULT_ROOT / str(row["controller_id"])


def existing_terminal_record(run_dir: Path) -> dict[str, Any] | None:
    record_path = run_dir / "RUN_RECORD.json"
    if not record_path.is_file():
        return None
    try:
        record = read_json(record_path)
    except (OSError, json.JSONDecodeError):
        return None
    return record if record.get("status") in TERMINAL_STATUSES else None


def archive_existing_record(run_dir: Path) -> str | None:
    existing = existing_terminal_record(run_dir)
    if existing is None:
        return None
    archive = run_dir / "superseded" / time.strftime("%Y%m%d_%H%M%S")
    archive.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    for name in ("RUN_RECORD.json", "G2_ROUTE_STATUS.json", "RUN_CONFIG.json", "logs", "raw", "metrics", "screenshots", "native_result"):
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
            "schema": "mosim.phase2_full_48_climbpath_superseded_run.v1",
            "archived_at": now_iso(),
            "source_run_dir": relative(run_dir),
            "copied": copied,
        },
    )
    return relative(archive)


def error_class(message: str) -> str:
    text = message.lower()
    if "source hash changed" in text:
        return "source_hash_mismatch"
    if "model check failed" in text or "checkmodel failed" in text or "check model failed" in text:
        return "check_model_failed"
    if "simulation failed" in text or "simulatemodel" in text:
        return "simulate_failed"
    if "nan" in text or "non-finite" in text or "infinite" in text:
        return "numerical_divergence"
    if "result" in text or "variable" in text or "csv" in text:
        return "result_binding_failed"
    return "other"


def terminal_error_from_series(series: dict[str, list[float]]) -> tuple[float, float, float]:
    required = ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")
    if any(key not in series or not series[key] for key in required):
        raise RuntimeError("tracking result does not expose complete position/reference series")
    count = min(len(series[key]) for key in required)
    if count <= 10:
        raise RuntimeError("result contains too few samples")
    errors = series.get("position_error_norm")
    if not errors or len(errors) < count:
        errors = []
        for index in range(count):
            x, y, z, x_ref, y_ref, z_ref = (float(series[key][index]) for key in required[1:])
            errors.append(math.sqrt((x_ref - x) ** 2 + (y_ref - y) ** 2 + (z_ref - z) ** 2))
        series["position_error_norm"] = errors
    values = [float(value) for value in errors[:count]]
    if not all(math.isfinite(value) for value in values):
        raise RuntimeError("position_error_norm contains NaN or Inf")
    terminal_time = float(series["time"][count - 1])
    if not math.isfinite(terminal_time):
        raise RuntimeError("terminal time is non-finite")
    return terminal_time, values[-1], max(values)


def capture_optional(
    record: dict[str, Any],
    *,
    run_dir: Path,
    phase: str,
    target_class: str,
    expected_pid: int | None,
    surface: str,
) -> None:
    destination = run_dir / "screenshots" / ("01_after_check.png" if phase == "after_check" else "02_result_window.png")
    try:
        capture = capture_phase(
            run_dir=run_dir,
            phase=phase,
            target_class=target_class,
            expected_pid=expected_pid,
            destination=destination,
            capture_surface=surface,
        )
        record["mworks_phase_screenshots"].append(capture)
    except Exception as exc:
        record.setdefault("evidence_warnings", []).append(
            {"phase": phase, "kind": "screenshot_failed", "message": str(exc)}
        )


def artifact_refs(record: dict[str, Any], run_dir: Path, log_path: Path) -> None:
    for candidate in (
        artifact(log_path, "log"),
        artifact(run_dir / "logs" / "load_model.json", "log"),
        artifact(run_dir / "logs" / "check_model_direct.json", "log"),
        artifact(run_dir / "logs" / "simulate_model_direct.json", "log"),
        artifact(run_dir / "raw" / "result.csv", "raw"),
        artifact(run_dir / "metrics" / "METRICS.json", "metrics"),
        artifact(run_dir / "metrics" / "metrics.csv", "metrics"),
        artifact(run_dir / "screenshots" / "01_after_check.png", "figure"),
        artifact(run_dir / "screenshots" / "02_result_window.png", "figure"),
    ):
        if candidate and candidate not in record["artifact_refs"]:
            record["artifact_refs"].append(candidate)
    write_json(
        run_dir / "logs" / "screenshot_manifest.json",
        {
            "schema": "mosim.phase2_full_48_climbpath_screenshot_manifest.v1",
            "runner_class": record["runner_class"],
            "captures": record["mworks_phase_screenshots"],
            "warnings": record.get("evidence_warnings", []),
        },
    )


def write_route_status(record: dict[str, Any], run_dir: Path) -> None:
    write_json(
        run_dir / "G2_ROUTE_STATUS.json",
        {
            "schema": STATUS_SCHEMA,
            "generated_at": now_iso(),
            "controller_id": record["controller_id"],
            "runner_class": record["runner_class"],
            "status": record["status"],
            "failure_class": record.get("failure_class"),
            "position_rmse_m": record.get("position_rmse_m"),
            "terminal_position_error_norm_m": record.get("terminal_position_error_norm_m"),
            "run_record": relative(run_dir / "RUN_RECORD.json"),
        },
    )


def static_failure(row: dict[str, Any], matrix_hash: str, reason: str) -> dict[str, Any]:
    run_dir = run_dir_for(row)
    for directory in (run_dir / "logs", run_dir / "raw", run_dir / "metrics", run_dir / "screenshots"):
        directory.mkdir(parents=True, exist_ok=True)
    record = {
        "schema": SCHEMA,
        "controller_id": row["controller_id"],
        "runner_id": row["runner_id"],
        "runner_class": row["runner_class"],
        "adapter_class": row.get("adapter_class"),
        "scenario_id": "climb_path_50s",
        "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
        "status": "fail",
        "failure_class": error_class(reason),
        "failure_reasons": [reason],
        "position_rmse_m": None,
        "terminal_position_error_norm_m": None,
        "simulation_completed": False,
        "source": "static_source_integrity_audit",
        "live_mworks_touched": False,
        "will_not_click_activation_login": True,
        "matrix": {"path": relative(MATRIX_PATH), "sha256": matrix_hash},
        "source_hash_observations": [],
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": ["No MWORKS simulation was started because the frozen G2 source hash changed before this route."],
        "artifact_refs": [],
        "started_at": now_iso(),
        "finished_at": now_iso(),
        "result_data_status": "missing",
    }
    try:
        record["source_hash_observations"] = source_observations(row, "static_source_integrity")
    except Exception as exc:
        record["source_hash_observations"].append({"phase": "static_source_integrity", "error": str(exc)})
    write_json(run_dir / "RUN_RECORD.json", record)
    write_route_status(record, run_dir)
    return record


def run_route(row: dict[str, Any], matrix_hash: str, *, rerun: bool, wrapper: str | None) -> dict[str, Any]:
    run_dir = run_dir_for(row)
    if rerun:
        supersedes = archive_existing_record(run_dir)
    else:
        supersedes = None
    for directory in (run_dir / "logs", run_dir / "raw", run_dir / "metrics", run_dir / "screenshots"):
        directory.mkdir(parents=True, exist_ok=True)

    target_file = project_file(str(row["runner_file"]))
    target_class = str(row["runner_class"])
    log_path = run_dir / "logs" / "mcp.jsonl"
    log_path.write_text("", encoding="utf-8")
    write_json(
        run_dir / "RUN_CONFIG.json",
        {
            "schema": "mosim.phase2_full_48_climbpath_run_config.v1",
            "generated_at": now_iso(),
            "runner_class": target_class,
            "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
            "target_time_s": [0.0, STOP_TIME_S],
            "simulation_timeout_s": SIMULATION_TIMEOUT_S,
            "scenario_injection": "none",
            "terminal_position_error_limit_m": TERMINAL_ERROR_LIMIT_M,
            "matrix": {"path": relative(MATRIX_PATH), "sha256": matrix_hash},
        },
    )
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "controller_id": row["controller_id"],
        "runner_id": row["runner_id"],
        "runner_class": target_class,
        "adapter_class": row.get("adapter_class"),
        "scenario_id": "climb_path_50s",
        "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
        "started_at": now_iso(),
        "run_dir": relative(run_dir),
        "status": "running",
        "failure_class": None,
        "failure_reasons": [],
        "position_rmse_m": None,
        "terminal_position_error_norm_m": None,
        "maximum_position_error_norm_m": None,
        "terminal_time_s": None,
        "simulation_completed": False,
        "source": "MWORKS_MCP",
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "claim_boundary": "Nominal MWORKS whole-aircraft ClimbPath closure only; not gain tuning, seven-scenario, code-generation, Gazebo, PX4, ROS, or flight-runtime evidence.",
        "matrix": {"path": relative(MATRIX_PATH), "sha256": matrix_hash},
        "source_hash_observations": [],
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": [],
        "artifact_refs": [],
    }
    if supersedes:
        record["supersedes"] = supersedes

    client = JsonlMcpClient(wrapper_command(resolve_wrapper(wrapper)), log_path)
    session: dict[str, Any] | None = None
    cleanup: dict[str, Any] | None = None
    try:
        record["source_hash_observations"].extend(source_observations(row, "before_session"))
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
        load = client.call_tool(
            "model_manager",
            {"action": "load_file", "file_path": str(target_file), "force_reload": False, "auto_load_deps": True},
            timeout_s=300,
        )
        write_json(run_dir / "logs" / "load_model.json", load)
        if not load.get("ok"):
            raise RuntimeError(f"model load failed: {load}")
        materialized = materialize_package_roots_after_target(client)
        write_json(run_dir / "logs" / "package_root_materialization.json", materialized)
        record["package_root_materialization"] = materialized
        record["source_hash_observations"].extend(source_observations(row, "after_load"))

        check = client.call_tool("check_model", {"model_name": target_class, "stop_on_error": True}, timeout_s=300)
        write_json(run_dir / "logs" / "check_model_direct.json", check)
        if not check.get("ok"):
            raise RuntimeError(f"model check failed: {check}")
        record["source_hash_observations"].extend(source_observations(row, "after_check"))
        opened = client.call_tool("model_manager", {"action": "open", "model_name": target_class}, timeout_s=60)
        write_json(run_dir / "logs" / "open_model.json", opened)
        if opened.get("ok"):
            capture_optional(
                record,
                run_dir=run_dir,
                phase="after_check",
                target_class=target_class,
                expected_pid=expected_pid,
                surface="model",
            )
        else:
            record.setdefault("evidence_warnings", []).append(
                {"phase": "after_check", "kind": "model_open_failed", "message": str(opened)}
            )

        raw_output = run_dir / "raw" / "result.csv"
        metrics_json = run_dir / "metrics" / "METRICS.json"
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
            verify_result_var=RUNNER_VARIABLES["z"],
            verify_time_point="end",
            timeout_s=SIMULATION_TIMEOUT_S,
        )
        write_json(run_dir / "logs" / "simulate_model_direct.json", simulation)
        if not simulation.get("ok"):
            raise RuntimeError(f"simulation failed: {simulation}")
        if simulation.get("simulate_api_reported_failure"):
            raise RuntimeError(f"simulation API reported failure: {simulation}")
        readiness = wait_for_fresh_result_artifacts(
            client,
            model_name=target_class,
            variables=RUNNER_VARIABLES,
            native_dir=native_dir,
            expected_native=expected_native,
            expected_stop_time=STOP_TIME_S,
            not_before_unix=started_unix,
        )
        record["result_readiness"] = readiness["readiness"]
        native_result = readiness["native_result"]
        series = readiness["series"]
        write_native_result_manifest(
            native_manifest,
            native_result_dir=native_dir,
            native_result=native_result,
            model_name=target_class,
        )
        record["native_result_locator"] = relative(native_result)
        terminal_time, terminal_error, maximum_error = terminal_error_from_series(series)
        write_csv(series, RUNNER_VARIABLES, raw_output)
        write_metrics(
            raw_output,
            metrics_json,
            metrics_csv,
            "climb_path_50s",
            str(row["controller_id"]),
            "formal_mworks_g2_climbpath_v1",
            "standard_tracking",
        )
        metrics = read_json(metrics_json)
        record["simulation_completed"] = True
        record["terminal_time_s"] = terminal_time
        record["terminal_position_error_norm_m"] = terminal_error
        record["maximum_position_error_norm_m"] = maximum_error
        record["position_rmse_m"] = metrics.get("position_rmse_m")
        record["metrics_summary"] = {
            "row_count": metrics.get("row_count"),
            "duration_s": metrics.get("duration_s"),
            "nan_count": metrics.get("nan_count"),
            "valid": metrics.get("valid"),
        }
        if not metrics.get("valid"):
            raise RuntimeError(f"tracking metrics are invalid: {metrics}")
        if terminal_time < STOP_TIME_S - 0.01:
            record["status"] = "fail"
            record["failure_class"] = "simulate_failed"
            record["failure_reasons"].append(
                f"simulation ended at {terminal_time:.6g}s before required {STOP_TIME_S:.6g}s"
            )
        elif terminal_error >= TERMINAL_ERROR_LIMIT_M:
            record["status"] = "fail"
            record["failure_class"] = "terminal_position_error_exceeds_5m"
            record["failure_reasons"].append(
                f"terminal position_error_norm {terminal_error:.6g}m is not below {TERMINAL_ERROR_LIMIT_M:.6g}m"
            )
        else:
            record["status"] = "pass"
        try:
            plot = show_native_plot(client, native_result=native_result, variables=PLOT_VARIABLES)
            write_json(run_dir / "logs" / "open_native_result_plot.json", plot)
            capture_optional(
                record,
                run_dir=run_dir,
                phase="result_window",
                target_class=target_class,
                expected_pid=expected_pid,
                surface="result_viewer",
            )
        except Exception as exc:
            record.setdefault("evidence_warnings", []).append(
                {"phase": "result_window", "kind": "native_plot_or_capture_failed", "message": str(exc)}
            )
        record["mworks_phase_observations"].append(
            "Native CheckModel, 50 s ClimbPath simulation, result export, and terminal-error evaluation completed."
        )
        record["source_hash_observations"].extend(source_observations(row, "before_cleanup"))
    except Exception as exc:
        message = str(exc)
        record["status"] = "fail"
        record["failure_class"] = error_class(message)
        record["failure_reasons"].append(message)
        record["error"] = {"message": message, "traceback": traceback.format_exc()}
    finally:
        try:
            cleanup = close_dedicated_session(client, session=session, output=run_dir / "logs" / "session_cleanup.json")
        finally:
            client.close()
        record["session_cleanup"] = cleanup
        try:
            record["source_hash_observations"].extend(source_observations(row, "after_session_shutdown"))
        except Exception as exc:
            message = str(exc)
            record["status"] = "fail"
            record["failure_class"] = "source_hash_mismatch"
            record["failure_reasons"].append(message)
            record.setdefault("error", {"message": message, "traceback": traceback.format_exc()})
        raw = run_dir / "raw" / "result.csv"
        metrics = run_dir / "metrics" / "METRICS.json"
        record["result_data_status"] = (
            "complete" if record.get("simulation_completed") and raw.is_file() and metrics.is_file() else
            "partial" if raw.is_file() else
            "missing"
        )
        record["finished_at"] = now_iso()
        artifact_refs(record, run_dir, log_path)
        write_json(run_dir / "RUN_RECORD.json", record)
        write_route_status(record, run_dir)
    return record


def persisted_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(RESULT_ROOT.glob("*/RUN_RECORD.json")):
        try:
            record = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("schema") == SCHEMA:
            records.append(record)
    return records


def write_status(matrix: dict[str, Any]) -> dict[str, Any]:
    records = persisted_records()
    failures: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for record in records:
        if record.get("status") == "fail":
            failure = str(record.get("failure_class") or "other")
            failures[failure] = failures.get(failure, 0) + 1
        rows.append(
            {
                "controller_id": record.get("controller_id"),
                "runner_class": record.get("runner_class"),
                "status": record.get("status"),
                "position_rmse_m": record.get("position_rmse_m"),
                "terminal_position_error_norm_m": record.get("terminal_position_error_norm_m"),
                "failure_class": record.get("failure_class"),
                "failure_reasons": record.get("failure_reasons", []),
            }
        )
    passed_count = sum(record.get("status") == "pass" for record in records)
    failed_count = sum(record.get("status") == "fail" for record in records)
    status = {
        "schema": STATUS_SCHEMA,
        "generated_at": now_iso(),
        "matrix": {"path": relative(MATRIX_PATH), "sha256": sha256(MATRIX_PATH)},
        "runner_count": len(matrix["rows"]),
        "terminal_record_count": len(records),
        "pending_count": len(matrix["rows"]) - len(records),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "failure_counts": failures,
        "completed": len(records) == len(matrix["rows"]),
        "rows": rows,
    }
    write_json(STATUS_PATH, status)
    return status


def write_contract(matrix: dict[str, Any]) -> None:
    sentinel = RESULT_ROOT / "preflight" / "mworks_gui_sentinel.json"
    sentinel_summary: dict[str, Any] | None = None
    if sentinel.is_file():
        try:
            sentinel_data = read_json(sentinel)
            sentinel_summary = {
                "path": relative(sentinel),
                "status": sentinel_data.get("status"),
                "matched_license_patterns": sentinel_data.get("matched_license_patterns"),
                "login_activation_window_count": sentinel_data.get("login_activation_window_count"),
                "authorization_window_count": sentinel_data.get("authorization_window_count"),
                "helper_mworks_window_count": sentinel_data.get("helper_mworks_window_count"),
            }
        except (OSError, json.JSONDecodeError):
            sentinel_summary = {"path": relative(sentinel), "parse_error": True}
    write_json(
        CONTRACT_PATH,
        {
            "schema": "mosim.phase2_full_48_climbpath_contract.v1",
            "generated_at": now_iso(),
            "matrix": {"path": relative(MATRIX_PATH), "sha256": sha256(MATRIX_PATH)},
            "scope": matrix["scope"],
            "acceptance": {
                "status_values": ["pass", "fail"],
                "terminal_position_error_limit_m": TERMINAL_ERROR_LIMIT_M,
                "all_48_records_required": True,
                "no_gain_tuning": True,
                "no_model_source_changes": True,
                "no_seven_scenario_runs": True,
            },
            "preflight": sentinel_summary,
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="comma-separated controller IDs or FormalRunner class leaves for a bounded retry")
    parser.add_argument("--rerun", action="store_true", help="archive and rerun existing terminal records")
    parser.add_argument("--plan-only", action="store_true", help="freeze the 48-row matrix without starting MWORKS")
    parser.add_argument("--refresh-matrix", action="store_true", help="replace an unchanged-record-free frozen matrix")
    parser.add_argument("--wrapper", help="optional explicit project-local Sysplorer MCP wrapper")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    matrix = freeze_matrix(build_matrix(), refresh=args.refresh_matrix)
    write_contract(matrix)
    identifiers = {str(row["controller_id"]): row for row in matrix["rows"]}
    identifiers.update({str(row["runner_id"]): row for row in matrix["rows"]})
    if args.only:
        requested = {item.strip() for item in args.only.split(",") if item.strip()}
        unknown = requested - identifiers.keys()
        if unknown:
            raise ValueError(f"unknown G2 runner selector(s): {sorted(unknown)}")
        selected = [row for row in matrix["rows"] if row["controller_id"] in requested or row["runner_id"] in requested]
    else:
        selected = list(matrix["rows"])
    if args.plan_only:
        status = write_status(matrix)
        print(json.dumps({"planned_runner_count": len(selected), "status": status}, ensure_ascii=False, indent=2))
        return 0

    matrix_hash = sha256(MATRIX_PATH)
    for row in selected:
        run_dir = run_dir_for(row)
        if not args.rerun and existing_terminal_record(run_dir):
            continue
        try:
            source_observations(row, "before_route")
        except Exception as exc:
            static_failure(row, matrix_hash, str(exc))
            continue
        run_route(row, matrix_hash, rerun=args.rerun, wrapper=args.wrapper)
    status = write_status(matrix)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if (args.only or status["completed"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
