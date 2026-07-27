#!/usr/bin/env python3
"""Run a hash-bound whole-aircraft MWORKS closure.

The frozen 46-route G6 matrix only establishes each route at its declared
internal-probe or existing-integrated-chain boundary.  This runner supports
two explicitly different gate types:

* a selected G6 family champion's whole-aircraft minimum closure before it
  enters the seven-scenario Official-PID A/B matrix;
* a shared Plant/Runner boundary baseline that validates a runner fixture and
  its declared adapter without mislabelling it as a champion result.

The runner consumes a small hash-bound binding manifest.  It deliberately
reuses the Official-PID baseline evidence plumbing so all champions emit the
same kind of native result, raw series, metrics, MCP log, and native-window
captures.  It never promotes a result to Gazebo, PX4, ROS, or flight evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
import time
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MCP_DIR = ROOT / "Scripts" / "mworks"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

from run_g6_controller_execution import (  # noqa: E402
    JsonlMcpClient,
    artifact,
    base_model_files,
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
    write_csv,
    write_json,
    write_metrics,
    write_native_result_manifest,
    wait_for_fresh_result_artifacts,
    wrapper_command,
)
from run_sysplorer_mcp_smoke import resolve_native_result_dir  # noqa: E402


CHAMPION_BINDING_SCHEMA = "mosim.g6_formal_champion_binding.v1"
RUNNER_BASELINE_BINDING_SCHEMA = "mosim.runner_boundary_baseline_binding.v1"
SCHEMA = "mosim.g6_formal_champion_minimum_closure_run.v1"
STATUS_SCHEMA = "mosim.g6_formal_champion_minimum_closure_status.v1"
SCREENSHOT_SCHEMA = "mosim.g6_formal_champion_minimum_closure_screenshot_manifest.v1"
DEFAULT_G6_MATRIX_PATH = ROOT / "Results" / "control_platform" / "g6_controller_execution_20260724" / "G6_EXECUTION_MATRIX.json"
TERMINAL_ERROR_LIMIT_M = 5.0
# Controllers sample at 100 Hz.  Recording at the same interval preserves the
# closed-loop response for ranking without serializing every adaptive solver step.
FORMAL_RESULT_INTERVAL_S = 0.01
# All six candidates use this fixed-step profile.  It changes neither a
# controller nor the Sunray150 plant; it only prevents adaptive internal steps
# from turning a 50 s result into an unbounded native-result serialization.
FORMAL_SOLVER_PROFILE = {
    "algo": "Rkfix4",
    "integralStep": 0.002,
    "storeDouble": True,
    "storeEvent": False,
    "isPieceWiseStep": True,
    "pieceWiseStep": ((0.0, 0.002),),
}
TERMINAL_STATUSES = {
    "passed",
    "model_check_failed",
    "result_binding_failed",
    "graphical_topology",
    "execution_failed",
    "source_hash_mismatch",
    "screenshot_failed",
    "license_or_login",
    "internal_or_mcp",
    "terminal_position_error_exceeds_limit",
}

# AttitudeThrustRunner exposes the shared plant at these public result names.
FORMAL_VARIABLES = {
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
RESULT_VIEWER_VARIABLES = {
    key: FORMAL_VARIABLES[key]
    for key in ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")
}


def require_object(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def require_text(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")
    return value


def project_file(path_text: str, *, label: str) -> Path:
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} leaves the project root: {path_text}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path_text}")
    return path


def execution_metadata(binding: dict[str, Any]) -> dict[str, str]:
    """Keep champion promotion and runner-boundary evidence distinguishable."""
    if binding["schema"] == RUNNER_BASELINE_BINDING_SCHEMA:
        return {
            "kind": "runner_boundary_baseline",
            "record_schema": "mosim.runner_boundary_baseline_run.v1",
            "status_schema": "mosim.runner_boundary_baseline_status.v1",
            "screenshot_schema": "mosim.runner_boundary_baseline_screenshot_manifest.v1",
            "archive_schema": "mosim.runner_boundary_baseline_superseded_run.v1",
            "status_file_name": "RUNNER_BASELINE_STATUS.json",
            "matrix_membership": "not_member",
            "matrix_reason": "Runner-boundary baseline validates the shared Plant/Runner interface and does not promote a controller or rewrite the frozen 46-route matrix.",
            "metrics_source": "runner_boundary_baseline",
        }
    return {
        "kind": "champion_promotion",
        "record_schema": SCHEMA,
        "status_schema": STATUS_SCHEMA,
        "screenshot_schema": SCREENSHOT_SCHEMA,
        "archive_schema": "mosim.g6_formal_champion_superseded_run.v1",
        "status_file_name": "FORMAL_CHAMPION_STATUS.json",
        "matrix_membership": "champion-promotion outside frozen provenance matrix",
        "matrix_reason": "Champion promotion is a separately bound whole-aircraft gate and does not rewrite the frozen provenance matrix.",
        "metrics_source": "g6_formal_champion_minimum_closure",
    }


def validate_feedback_boundary(binding: dict[str, Any], target_file: Path) -> None:
    """Bind an explicit sampled controller-input declaration to its Modelica source."""
    boundary = binding.get("formal_harness_feedback_boundary")
    if boundary is None:
        return
    boundary = require_object(boundary, label="formal harness feedback boundary")
    if boundary.get("kind") != "sampled_controller_inputs":
        raise ValueError("formal harness feedback boundary kind is unsupported")
    if float(boundary.get("sample_period_s", 0.0)) != 0.01:
        raise ValueError("sampled controller-input formal boundary must use a 0.01 s period")
    if boundary.get("initial_measurement") != "zero":
        raise ValueError("sampled controller-input formal boundary must declare zero initial measurement")
    expected_signals = [
        "reference.position_command -> controller.position_ref",
        "plant.position -> controller.position_mea",
        "plant.attitude -> controller.attitude_mea",
    ]
    if boundary.get("signals") != expected_signals:
        raise ValueError("sampled controller-input formal boundary signals are incomplete or reordered")
    expected_continuous_signals = ["plant.attitude -> offline_inner_allocator.attitude_mea"]
    if boundary.get("continuous_inner_loop_signals") != expected_continuous_signals:
        raise ValueError("continuous inner-loop formal boundary signals are incomplete or reordered")
    source = target_file.read_text(encoding="utf-8")
    required_fragments = (
        "parameter Real controller_sample_period_s = 0.01",
        "Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3]",
        "Modelica.Blocks.Discrete.UnitDelay sampled_position[3]",
        "Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3]",
        "each samplePeriod = controller_sample_period_s",
        "each y_start = 0",
        "connect(reference.position_command, sampled_position_ref.u)",
        "connect(sampled_position_ref.y, controller.position_ref)",
        "connect(plant.position, sampled_position.u)",
        "connect(sampled_position.y, controller.position_mea)",
        "connect(plant.attitude, sampled_attitude.u)",
        "connect(sampled_attitude.y, controller.attitude_mea)",
        "connect(plant.attitude, offline_inner_allocator.attitude_mea)",
    )
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise ValueError(f"sampled controller-input source boundary is incomplete: {missing}")
    forbidden_fragments = (
        "connect(reference.position_command, controller.position_ref)",
        "connect(plant.position, controller.position_mea)",
        "connect(plant.attitude, controller.attitude_mea)",
        "connect(sampled_attitude.y, offline_inner_allocator.attitude_mea)",
    )
    direct_feedback = [fragment for fragment in forbidden_fragments if fragment in source]
    if direct_feedback:
        raise ValueError(f"sampled controller-input source retains direct feedback: {direct_feedback}")


def materialize_package_roots_after_target(client: JsonlMcpClient) -> list[dict[str, Any]]:
    """Rebuild package classes that Sysplorer can erase when it opens a leaf runner.

    Formal champion runners are individual ``.mo`` leaves inside
    ``MoSimQuadrotorModel``.  Opening such a leaf can remove the loaded package
    root even with ``force_reload=False``. Reopening the canonical root
    reloads the target through ``package.order`` and restores the embedded
    Plant types required by CheckModel.
    """
    records: list[dict[str, Any]] = []
    for package_file in base_model_files():
        if not package_file.is_file():
            raise FileNotFoundError(f"Required G6 base package is missing: {package_file}")
        result = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": str(package_file),
                "force_reload": True,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        record = {
            "path": relative(package_file),
            "sha256": sha256(package_file),
            "force_reload": True,
            "auto_load_deps": True,
            "ok": bool(result.get("ok")),
        }
        records.append(record)
        if not record["ok"]:
            raise RuntimeError(f"Required formal package root load failed: {record['path']}: {result}")
    return records


def read_binding(path: Path) -> dict[str, Any]:
    binding_path = path.resolve()
    try:
        binding_path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("binding must remain inside the project root") from exc
    binding = require_object(read_json(binding_path), label="formal champion binding")
    schema = require_text(binding.get("schema"), label="binding schema")
    if schema not in {CHAMPION_BINDING_SCHEMA, RUNNER_BASELINE_BINDING_SCHEMA}:
        raise ValueError(
            "binding schema must be mosim.g6_formal_champion_binding.v1 or "
            "mosim.runner_boundary_baseline_binding.v1"
        )

    controller_id = require_text(binding.get("controller_id"), label="binding controller_id")
    require_text(binding.get("controller_category"), label="binding controller_category")
    scenario = require_object(binding.get("scenario"), label="binding scenario")
    require_text(scenario.get("scenario_id"), label="binding scenario_id")
    duration = float(scenario.get("duration_s", 0))
    if duration <= 0:
        raise ValueError("binding scenario duration_s must be positive")

    target = require_object(binding.get("target"), label="binding target")
    adapter = require_object(binding.get("formal_adapter"), label="binding formal_adapter")
    for label, item in (("target", target), ("formal_adapter", adapter)):
        require_text(item.get("model_file"), label=f"binding {label} model_file")
        require_text(item.get("model_class"), label=f"binding {label} model_class")
        require_text(item.get("model_sha256"), label=f"binding {label} model_sha256")

    sources = binding.get("source_bindings")
    if not isinstance(sources, list) or not sources:
        raise ValueError("binding source_bindings must be a non-empty list")
    roles: set[str] = set()
    for source in sources:
        item = require_object(source, label="binding source binding")
        role = require_text(item.get("role"), label="binding source role")
        if role in roles:
            raise ValueError(f"binding source role repeats: {role}")
        roles.add(role)
        require_text(item.get("path"), label=f"binding source {role} path")
        require_text(item.get("expected_sha256"), label=f"binding source {role} expected_sha256")

    target_file = project_file(str(target["model_file"]), label="formal target")
    adapter_file = project_file(str(adapter["model_file"]), label="formal adapter")
    if sha256(target_file) != target["model_sha256"]:
        raise RuntimeError("target model SHA-256 does not match the binding")
    if sha256(adapter_file) != adapter["model_sha256"]:
        raise RuntimeError("formal adapter SHA-256 does not match the binding")
    validate_feedback_boundary(binding, target_file)

    binding["binding_file"] = relative(binding_path)
    binding["binding_sha256"] = sha256(binding_path)
    binding["controller_id"] = controller_id
    binding["scenario"] = scenario
    binding["execution_metadata"] = execution_metadata(binding)
    return binding


def verify_source_bindings(record: dict[str, Any], binding: dict[str, Any], *, phase: str) -> None:
    observations = record.setdefault("source_hash_observations", [])
    if not isinstance(observations, list):
        raise RuntimeError("source_hash_observations must be a list")
    for source in binding["source_bindings"]:
        item = require_object(source, label="source binding")
        role = require_text(item.get("role"), label="source binding role")
        path = project_file(require_text(item.get("path"), label=f"source {role} path"), label=role)
        expected = require_text(item.get("expected_sha256"), label=f"source {role} expected SHA-256")
        actual = sha256(path)
        observations.append(
            {
                "phase": phase,
                "role": role,
                "path": relative(path),
                "sha256": actual,
                "expected_sha256": expected,
                "matches_binding": actual == expected,
            }
        )
        if actual != expected:
            raise RuntimeError(f"Formal source binding hash changed during {phase}: {role} {actual} != {expected}")


def existing_terminal_record(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "RUN_RECORD.json"
    if not path.is_file():
        return None
    try:
        record = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    return record if isinstance(record, dict) and record.get("status") in TERMINAL_STATUSES else None


def archive_rerun(run_dir: Path, *, metadata: dict[str, str]) -> str | None:
    previous = existing_terminal_record(run_dir)
    if previous is None:
        return None
    archive = run_dir / "superseded" / time.strftime("%Y%m%d_%H%M%S")
    archive.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    for name in ("RUN_RECORD.json", metadata["status_file_name"], "logs", "raw", "metrics", "screenshots"):
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
            "schema": metadata["archive_schema"],
            "archived_at": now_iso(),
            "source_run_dir": relative(run_dir),
            "copied": copied,
            "native_result_retention": "The prior Result.msr remains at the unique source root recorded by the archived RUN_RECORD.",
        },
    )
    return relative(archive)


def write_screenshot_manifest(run_dir: Path, record: dict[str, Any]) -> Path:
    output = run_dir / "logs" / "screenshot_manifest.json"
    write_json(
        output,
        {
            "schema": record["execution_metadata"]["screenshot_schema"],
            "controller_id": record.get("controller_id"),
            "scenario_id": record.get("scenario_id"),
            "target": record.get("formal_binding", {}).get("target"),
            "captures": record.get("mworks_phase_screenshots", []),
            "model_layout_boundary": record.get("model_layout_boundary"),
            "claim_boundary": record.get("claim_boundary"),
        },
    )
    return output


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
        errors.append(
            math.sqrt(
                (values[3] - values[0]) ** 2
                + (values[4] - values[1]) ** 2
                + (values[5] - values[2]) ** 2
            )
        )
    series["position_error_norm"] = errors
    terminal = errors[-1]
    if not math.isfinite(terminal):
        raise RuntimeError("terminal position_error_norm is non-finite")
    return terminal


def terminal_status(record: dict[str, Any], *, cleanup: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema": record["execution_metadata"]["status_schema"],
        "generated_at": now_iso(),
        "controller_id": record.get("controller_id"),
        "controller_category": record.get("controller_category"),
        "scenario_id": record.get("scenario_id"),
        "status": record.get("status"),
        "run_record": relative(Path(record["run_dir"]) / "RUN_RECORD.json"),
        "formal_matrix_membership": record["frozen_46_route_matrix"]["membership"],
        "session_cleanup": cleanup,
        "claim_boundary": record.get("claim_boundary"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True, help="project-local champion or runner-baseline binding JSON")
    parser.add_argument("--output-dir", type=Path, help="project-local result directory below Results/")
    parser.add_argument(
        "--route-matrix",
        type=Path,
        help=(
            "project-local 46-route frozen matrix below Results/ used for provenance; "
            "default preserves the historical matrix reference"
        ),
    )
    parser.add_argument("--wrapper", help="optional explicit project-local Sysplorer MCP wrapper")
    parser.add_argument("--rerun", action="store_true", help="archive an existing terminal record before replacing it")
    parser.add_argument("--check-only", action="store_true", help="validate binding and source hashes without starting MWORKS")
    return parser.parse_args()


def checked_run_dir(path: Path) -> Path:
    run_dir = path.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        run_dir.relative_to(results_root)
    except ValueError as exc:
        raise ValueError("output-dir must stay below Results/") from exc
    return run_dir


def checked_route_matrix(path: Path | None) -> Path:
    matrix = DEFAULT_G6_MATRIX_PATH if path is None else path
    if not matrix.is_absolute():
        matrix = ROOT / matrix
    matrix = matrix.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        matrix.relative_to(results_root)
    except ValueError as exc:
        raise ValueError("route-matrix must stay below Results/") from exc
    if matrix.name not in {"G6_EXECUTION_MATRIX.json", "PHASE1_MATRIX.json"}:
        raise ValueError("route-matrix file name must be G6_EXECUTION_MATRIX.json or PHASE1_MATRIX.json")
    if not matrix.is_file():
        raise FileNotFoundError(f"route matrix is missing: {matrix}")
    return matrix


def main() -> int:
    args = parse_args()
    binding = read_binding(args.binding)
    route_matrix = checked_route_matrix(args.route_matrix)
    metadata = binding["execution_metadata"]
    if args.check_only:
        print(json.dumps({"ok": True, "binding": binding, "variables": FORMAL_VARIABLES}, ensure_ascii=False, indent=2))
        return 0

    default_run_dir = (ROOT / "Results" / "control_platform" / "g6_formal_champion_promotion_20260725" / binding["controller_id"] / "minimum_closure")
    run_dir = checked_run_dir(args.output_dir or default_run_dir)
    existing = existing_terminal_record(run_dir)
    if existing is not None and not args.rerun:
        print(f"Formal champion already has terminal record: {relative(run_dir / 'RUN_RECORD.json')}")
        return 0 if existing.get("status") == "passed" else 1
    supersedes = archive_rerun(run_dir, metadata=metadata) if args.rerun else None
    for directory in (run_dir / "logs", run_dir / "raw", run_dir / "metrics", run_dir / "screenshots"):
        directory.mkdir(parents=True, exist_ok=True)

    target = require_object(binding["target"], label="binding target")
    target_file = project_file(str(target["model_file"]), label="formal target")
    target_class = str(target["model_class"])
    scenario = require_object(binding["scenario"], label="binding scenario")
    scenario_id = str(scenario["scenario_id"])
    duration_s = float(scenario["duration_s"])
    log_path = run_dir / "logs" / "mcp.jsonl"
    log_path.write_text("", encoding="utf-8")
    record: dict[str, Any] = {
        "schema": metadata["record_schema"],
        "execution_kind": metadata["kind"],
        "execution_metadata": metadata,
        "controller_id": binding["controller_id"],
        "controller_category": binding["controller_category"],
        "scenario_id": scenario_id,
        "started_at": now_iso(),
        "run_dir": relative(run_dir),
        "status": "running",
        "source": "MWORKS_MCP",
        "formal_binding": binding,
        "result_output_interval_s": FORMAL_RESULT_INTERVAL_S,
        "formal_solver_profile": {
            "api": "ModelingPy.SimulateModel",
            "purpose": "common fixed-step and bounded-output profile for six-candidate ClimbPath ranking",
            "options": FORMAL_SOLVER_PROFILE,
        },
        "frozen_46_route_matrix": {
            "path": relative(route_matrix),
            "sha256": sha256(route_matrix),
            "membership": metadata["matrix_membership"],
            "reason": metadata["matrix_reason"],
        },
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "model_layout_boundary": binding.get(
            "model_layout_boundary",
            {
                "state": "formal_runner_wrapper_not_controller_graphical_topology",
                "reason": "The runner capture proves the named whole-aircraft closure; controller graphical topology remains the separate G5 evidence image.",
            },
        ),
        "claim_boundary": binding.get(
            "claim_boundary",
            "Real offline MWORKS whole-aircraft minimum closure only. This is not PX4, Gazebo, ROS, or flight-runtime evidence.",
        ),
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": [],
        "artifact_refs": [],
    }
    if supersedes:
        record["supersedes"] = supersedes

    client = JsonlMcpClient(wrapper_command(resolve_wrapper(args.wrapper)), log_path)
    session: dict[str, Any] | None = None
    cleanup: dict[str, Any] | None = None
    try:
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
        verify_source_bindings(record, binding, phase="before_load")
        # Leaf-first loading loses graphical-block dependencies in a clean session.
        record["base_package_preload"] = preload_base_packages(client)
        verify_source_bindings(record, binding, phase="after_base_package_preload")
        load = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": str(target_file),
                "force_reload": False,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        write_json(run_dir / "logs" / "load_model.json", load)
        if not load.get("ok"):
            raise RuntimeError(f"Formal champion model load failed: {load}")
        record["package_root_materialization"] = materialize_package_roots_after_target(client)
        write_json(
            run_dir / "logs" / "package_root_materialization.json",
            record["package_root_materialization"],
        )
        verify_source_bindings(record, binding, phase="after_load")

        check = client.call_tool(
            "check_model",
            {"model_name": target_class, "stop_on_error": True},
            timeout_s=300,
        )
        write_json(run_dir / "logs" / "check_model_direct.json", check)
        if not check.get("ok"):
            raise RuntimeError(f"Formal champion CheckModel failed: {check}")
        verify_source_bindings(record, binding, phase="after_check")

        opened = client.call_tool("model_manager", {"action": "open", "model_name": target_class}, timeout_s=60)
        write_json(run_dir / "logs" / "open_model.json", opened)
        if not opened.get("ok"):
            raise RuntimeError(f"Formal champion model window failed to open: {opened}")
        record["mworks_phase_screenshots"].append(
            capture_phase(
                run_dir=run_dir,
                phase="after_check",
                target_class=target_class,
                expected_pid=expected_pid,
                destination=run_dir / "screenshots" / "01_after_check.png",
                capture_surface="model",
            )
        )
        record["mworks_phase_observations"].append(
            "The formal runner passed CheckModel and its named wrapper window was captured. The wrapper does not replace the separate G5 controller-topology evidence."
        )

        raw_output = run_dir / "raw" / "result.csv"
        metrics_json = run_dir / "metrics" / "metrics.json"
        metrics_csv = run_dir / "metrics" / "metrics.csv"
        preferred_native = run_dir / "native_result"
        native_dir, native_manifest = resolve_native_result_dir(raw_output, preferred_native, target_class)
        native_dir, expected_native, native_root = prepare_route_native_result(native_dir, target_class)
        record["native_result_root"] = native_root
        simulation_started_unix = time.time()
        simulation = simulate_modelingpy(
            client,
            model_name=target_class,
            target_time=[0.0, duration_s],
            native_result_dir=native_dir,
            verify_result_var=FORMAL_VARIABLES["z"],
            verify_time_point="end",
            interval=FORMAL_RESULT_INTERVAL_S,
            simulate_model_options=FORMAL_SOLVER_PROFILE,
        )
        write_json(run_dir / "logs" / "simulate_model_direct.json", simulation)
        if not simulation.get("ok"):
            raise RuntimeError(f"Formal champion simulation failed: {simulation}")
        if simulation.get("simulate_api_reported_failure"):
            record["mworks_phase_observations"].append(
                "SimulateModel reported false. The formal run remains provisional until its current native Result.msr and complete time series pass the freshness gate."
            )
        verify_source_bindings(record, binding, phase="after_simulation")

        readiness = wait_for_fresh_result_artifacts(
            client,
            model_name=target_class,
            variables=FORMAL_VARIABLES,
            native_dir=native_dir,
            expected_native=expected_native,
            expected_stop_time=duration_s,
            not_before_unix=simulation_started_unix,
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
        write_csv(series, FORMAL_VARIABLES, raw_output)
        write_metrics(
            raw_output,
            metrics_json,
            metrics_csv,
            scenario_id,
            str(binding["controller_id"]),
            metadata["metrics_source"],
            "standard_tracking",
        )
        metrics = require_object(read_json(metrics_json), label="formal champion metrics")
        if metrics.get("valid") is not True:
            raise RuntimeError(f"Formal champion metrics are invalid: {metrics}")
        terminal_error = add_derived_position_error(series)
        position_rmse_m = float(metrics.get("position_rmse_m", float("nan")))
        if not math.isfinite(position_rmse_m):
            raise RuntimeError("formal champion position_rmse_m is non-finite")

        plot = show_native_plot(client, native_result=native_result, variables=RESULT_VIEWER_VARIABLES)
        write_json(run_dir / "logs" / "open_native_result_plot.json", plot)
        record["mworks_phase_screenshots"].append(
            capture_phase(
                run_dir=run_dir,
                phase="result_window",
                target_class=target_class,
                expected_pid=expected_pid,
                destination=run_dir / "screenshots" / "02_result_window.png",
                capture_surface="result_viewer",
            )
        )
        record["mworks_phase_observations"].append(
            "The current native Result.msr was opened, position/reference variables were plotted for tracking review, and the native result viewer was captured."
        )
        verify_source_bindings(record, binding, phase="before_record")
        record["metrics_summary"] = {
            "row_count": metrics.get("row_count"),
            "duration_s": metrics.get("duration_s"),
            "nan_count": metrics.get("nan_count"),
            "valid": metrics.get("valid"),
            "position_rmse_m": position_rmse_m,
        }
        record["terminal_position_error_norm_m"] = terminal_error
        record["position_rmse_m"] = position_rmse_m
        if terminal_error < TERMINAL_ERROR_LIMIT_M:
            record["status"] = "passed"
        else:
            record["status"] = "terminal_position_error_exceeds_limit"
            record["failure_class"] = "terminal_position_error_exceeds_limit"
    except Exception as exc:
        message = str(exc)
        classification = "source_hash_mismatch" if "source binding hash changed" in message or "SHA-256" in message else classify_error(message)
        if classification == "execution_failed" and ("capture" in message.lower() or "result-window" in message.lower()):
            classification = "screenshot_failed"
        record["status"] = classification
        record["error"] = {"message": message, "traceback": traceback.format_exc()}
    finally:
        for tool, output_name in (("check_model", "check_model.json"), ("call_code", "simulate_model.json")):
            try:
                extract_tool_log(log_path, tool, run_dir / "logs" / output_name)
            except Exception as exc:
                record.setdefault("log_extraction_warnings", []).append(repr(exc))
        screenshot_manifest = write_screenshot_manifest(run_dir, record)
        for candidate in (
            artifact(run_dir / "logs" / "load_model.json", "log"),
            artifact(run_dir / "logs" / "check_model_direct.json", "log"),
            artifact(run_dir / "logs" / "simulate_model_direct.json", "log"),
            artifact(run_dir / "raw" / "result.csv", "raw"),
            artifact(run_dir / "metrics" / "metrics.json", "metrics"),
            artifact(run_dir / "metrics" / "metrics.csv", "metrics"),
            artifact(run_dir / "screenshots" / "01_after_check.png", "figure"),
            artifact(run_dir / "screenshots" / "02_result_window.png", "figure"),
            artifact(log_path, "log"),
            artifact(screenshot_manifest, "log"),
        ):
            if candidate:
                record["artifact_refs"].append(candidate)
        native_locator = record.get("native_result_locator")
        if isinstance(native_locator, str):
            native_artifact = artifact(ROOT / native_locator, "native_result")
            if native_artifact:
                record["artifact_refs"].append(native_artifact)
        record["finished_at"] = now_iso()

    try:
        cleanup = close_dedicated_session(client, session=session, output=run_dir / "logs" / "session_cleanup.json")
    finally:
        client.close()
    record["session_cleanup"] = cleanup
    write_json(run_dir / "RUN_RECORD.json", record)
    write_json(run_dir / metadata["status_file_name"], terminal_status(record, cleanup=cleanup))
    print(json.dumps({"status": record["status"], "run_record": relative(run_dir / "RUN_RECORD.json")}, ensure_ascii=False))
    if record["status"] != "passed":
        return 1
    return 0 if not (cleanup and cleanup.get("requested") and not cleanup.get("verified_closed")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
