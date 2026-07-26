#!/usr/bin/env python3
"""Run the formal Official PID whole-aircraft baseline outside the frozen G6 matrix.

The 46-route G6 matrix proves current graphical controller routes at their
declared evidence boundary.  This runner starts the next gate: a separately
bound, plant-coupled Official PID baseline that later candidates must compare
against only after each candidate passes its own formal minimum closure.

It deliberately reuses the hardened MWORKS sequence from the G6 executor, but
does not write a route record into the 46-route matrix or alter its status.
"""

from __future__ import annotations

import argparse
import csv
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
    write_csv,
    write_json,
    write_metrics,
    write_native_result_manifest,
    wait_for_fresh_result_artifacts,
    wrapper_command,
)
from run_sysplorer_mcp_smoke import resolve_native_result_dir  # noqa: E402


SCHEMA = "mosim.g6_formal_closed_loop_baseline_run.v1"
STATUS_SCHEMA = "mosim.g6_formal_closed_loop_baseline_status.v1"
SCREENSHOT_SCHEMA = "mosim.g6_formal_closed_loop_baseline_screenshot_manifest.v1"
SELECTION_PATH = ROOT / "Config" / "control_platform" / "g6_champion_selection.json"
HARNESS_MAP_PATH = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
G6_MATRIX_PATH = ROOT / "Results" / "control_platform" / "g6_controller_execution_20260724" / "G6_EXECUTION_MATRIX.json"
DEFAULT_RUN_DIR = ROOT / "Results" / "control_platform" / "g6_formal_closed_loop_20260724" / "official_pid_climb_path_50s"
BASELINE_ID = "official_pid"
BASELINE_SCENARIO = "climb_path_50s"
BASELINE_DURATION_S = 50.0
REACTION_TORQUE_016_DIAGNOSTIC_ID = "official_pid_reaction_torque_016_diagnostic"
REACTION_TORQUE_016_DIAGNOSTIC_SCENARIO = "shared_assembly_reaction_torque_016_cm_50s"
REACTION_TORQUE_016_DIAGNOSTIC_RATIO = 0.016
REACTION_TORQUE_016_DIAGNOSTIC_FILE = (
    "Models/MoSimQuadrotorModel/Experiment/Runners/OfficialPidReactionTorque016Diagnostic.mo"
)
REACTION_TORQUE_016_DIAGNOSTIC_CLASS = (
    "MoSimQuadrotorModel.Experiment.Runners.OfficialPidReactionTorque016Diagnostic"
)
YAW_AUTHORITY_MAPPED_DIAGNOSTIC_ID = "official_pid_yaw_authority_mapped_diagnostic"
YAW_AUTHORITY_MAPPED_DIAGNOSTIC_SCENARIO = "shared_assembly_yaw_authority_map_50s"
YAW_AUTHORITY_MAPPED_DIAGNOSTIC_FILE = (
    "Models/MoSimQuadrotorModel/Experiment/Runners/OfficialPidYawAuthorityMappedDiagnostic.mo"
)
YAW_AUTHORITY_MAPPED_DIAGNOSTIC_CLASS = (
    "MoSimQuadrotorModel.Experiment.Runners.OfficialPidYawAuthorityMappedDiagnostic"
)
YAW_AUTHORITY_MAPPED_ADAPTER_FILE = (
    "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDYawAuthorityMappedRotorAdapter.mo"
)
YAW_AUTHORITY_MAPPED_ADAPTER_CLASS = (
    "MoSimQuadrotorModel.Control.Adapters.OfficialPIDYawAuthorityMappedRotorAdapter"
)
YAW_AUTHORITY_MAPPED_LEGACY_RATIO = 0.016
STABILITY_TAIL_WINDOW_S = 5.0
STABILITY_TERMINAL_ERROR_LIMIT_M = 0.5
STABILITY_TAIL_RMSE_LIMIT_M = 0.5
STABILITY_TAIL_PEAK_LIMIT_M = 1.0
TERMINAL_STATUSES = {
    "passed",
    "stability_failed",
    "model_check_failed",
    "result_binding_failed",
    "graphical_topology",
    "execution_failed",
    "source_hash_mismatch",
    "screenshot_failed",
    "license_or_login",
    "internal_or_mcp",
}

# RotorCommandRunner exposes the shared plant at this exact public boundary.
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
    "rotor_speed_1": "rotor_speed[1]",
}

# Keep the native evidence plot legible. The full state/command set remains in
# CSV and Result.msr; the result-window evidence is a tracking review surface.
RESULT_VIEWER_VARIABLES = {
    key: FORMAL_VARIABLES[key]
    for key in ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")
}


# Bind the physical closure and the named 50 s reference explicitly. The thin
# formal runner alone is insufficient provenance because it instantiates these
# sources indirectly.
SHARED_CLOSURE_SOURCES: tuple[tuple[str, str], ...] = (
    ("shared_sunray150_assembly", "Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo"),
    ("physical_wrench_adapter", "Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo"),
    ("wrapper_surface", "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo"),
    ("rotor_actuator_core", "Models/MoSimQuadrotorModel/Vehicle/Dynamics/RotorActuatorCore.mo"),
    ("plant_sensor_surface", "Models/MoSimQuadrotorModel/Vehicle/Sensors/package.mo"),
    ("virtual_px4_classic_profile", "Models/MoSimQuadrotorModel/Parameters/Sunray150VirtualPx4Classic.mo"),
    ("climb_path_reference", "Models/MoSimQuadrotorModel/Guidance/Trajectories/package.mo"),
)


def project_path(path_text: str, *, label: str) -> Path:
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} leaves the project root: {path_text}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path_text}")
    return path


def require_object(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def require_text(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")
    return value


def resolve_formal_binding() -> dict[str, Any]:
    """Resolve and hash-bind the declared Official PID formal baseline."""
    selection = require_object(read_json(SELECTION_PATH), label="champion selection")
    harness_map = require_object(read_json(HARNESS_MAP_PATH), label="formal harness map")
    selection_baseline = require_object(selection.get("official_pid_baseline"), label="selection official_pid baseline")
    map_selection = require_object(
        harness_map.get("provisional_champion_selection"),
        label="harness map provisional champion selection",
    )
    map_baseline = require_object(map_selection.get("official_pid_baseline"), label="harness-map official_pid baseline")

    for label, baseline in (("selection", selection_baseline), ("harness map", map_baseline)):
        if baseline.get("scheme_id") != BASELINE_ID:
            raise ValueError(f"{label} baseline must bind {BASELINE_ID}")
        if baseline.get("binding_state") != "formal_binding_ready_for_validation":
            raise ValueError(f"{label} baseline is not ready for formal validation")
        scenario = require_object(baseline.get("minimum_scenario"), label=f"{label} minimum scenario")
        if scenario.get("scenario_id") != BASELINE_SCENARIO:
            raise ValueError(f"{label} baseline must use {BASELINE_SCENARIO}")
        if float(scenario.get("duration_s", 0.0)) != BASELINE_DURATION_S:
            raise ValueError(f"{label} baseline duration must remain {BASELINE_DURATION_S:g} seconds")

    selection_adapter = require_object(selection_baseline.get("formal_adapter"), label="selection formal adapter")
    selection_runner = require_object(selection_baseline.get("whole_aircraft_source_harness"), label="selection formal runner")
    map_adapter = require_object(map_baseline.get("formal_adapter"), label="harness-map formal adapter")
    map_runner = require_object(map_baseline.get("whole_aircraft_source_harness"), label="harness-map formal runner")

    for label, selection_item, map_item in (
        ("formal adapter", selection_adapter, map_adapter),
        ("formal runner", selection_runner, map_runner),
    ):
        for key in ("model_file", "model_class"):
            if selection_item.get(key) != map_item.get(key):
                raise ValueError(f"{label} {key} differs between selection and harness map")

    adapter_file = project_path(require_text(map_adapter.get("model_file"), label="formal adapter model file"), label="formal adapter")
    runner_file = project_path(require_text(map_runner.get("model_file"), label="formal runner model file"), label="formal runner")
    rotor_runner_file = project_path(
        "Models/MoSimQuadrotorModel/Experiment/Runners/RotorCommandRunner.mo",
        label="shared rotor-command runner",
    )
    expected_adapter_hash = require_text(map_adapter.get("model_sha256"), label="formal adapter model SHA-256")
    expected_runner_hash = require_text(map_runner.get("model_sha256"), label="formal runner model SHA-256")

    sources = [
        {
            "role": "selection_authority",
            "path": relative(SELECTION_PATH),
            "expected_sha256": sha256(SELECTION_PATH),
        },
        {
            "role": "formal_harness_map_authority",
            "path": relative(HARNESS_MAP_PATH),
            "expected_sha256": sha256(HARNESS_MAP_PATH),
        },
        {
            "role": "formal_runner",
            "path": relative(runner_file),
            "expected_sha256": expected_runner_hash,
        },
        {
            "role": "formal_adapter",
            "path": relative(adapter_file),
            "expected_sha256": expected_adapter_hash,
        },
        {
            "role": "shared_rotor_command_runner",
            "path": relative(rotor_runner_file),
            "expected_sha256": sha256(rotor_runner_file),
        },
        *(
            {
                "role": role,
                "path": relative(project_path(path, label=role)),
                "expected_sha256": sha256(project_path(path, label=role)),
            }
            for role, path in SHARED_CLOSURE_SOURCES
        ),
    ]
    for source in sources:
        path = project_path(require_text(source.get("path"), label=f"{source['role']} path"), label=str(source["role"]))
        actual = sha256(path)
        if actual != source["expected_sha256"]:
            raise ValueError(
                f"{source['role']} hash does not match its declared binding: {actual} != {source['expected_sha256']}"
            )

    return {
        "controller_id": BASELINE_ID,
        "scenario_id": BASELINE_SCENARIO,
        "duration_s": BASELINE_DURATION_S,
        "target": {
            "model_file": relative(runner_file),
            "model_class": require_text(map_runner.get("model_class"), label="formal runner model class"),
            "model_sha256": expected_runner_hash,
        },
        "formal_adapter": {
            "model_file": relative(adapter_file),
            "model_class": require_text(map_adapter.get("model_class"), label="formal adapter model class"),
            "model_sha256": expected_adapter_hash,
            "output_boundary": map_adapter.get("output_boundary"),
        },
        "source_bindings": sources,
        "claim_boundary": (
            "Real offline MWORKS formal whole-aircraft minimum closure for the separately bound Official PID baseline. "
            "This run is outside the frozen 46-route G6 execution matrix and is not PX4, Gazebo, ROS1, or flight evidence."
        ),
    }


def resolve_reaction_torque_016_diagnostic_binding() -> dict[str, Any]:
    """Bind the one approved coefficient diagnostic without changing production parameters."""

    binding = resolve_formal_binding()
    diagnostic_file = project_path(
        REACTION_TORQUE_016_DIAGNOSTIC_FILE,
        label="reaction-torque 0.016 diagnostic runner",
    )
    diagnostic_text = diagnostic_file.read_text(encoding="utf-8")
    if "extends MoSimQuadrotorModel.Experiment.Runners.OfficialPidFormalRunner" not in diagnostic_text:
        raise ValueError("reaction-torque 0.016 diagnostic must extend OfficialPidFormalRunner")
    ratio_pattern = rf"reaction_moment_ratio\s*=\s*{REACTION_TORQUE_016_DIAGNOSTIC_RATIO:g}(?:0+)?\b"
    if re.search(ratio_pattern, diagnostic_text) is None:
        raise ValueError(
            "reaction-torque 0.016 diagnostic must set plant(reaction_moment_ratio = 0.016) exactly"
        )

    binding["baseline_target"] = dict(require_object(binding["target"], label="formal baseline target"))
    binding["target"] = {
        "model_file": relative(diagnostic_file),
        "model_class": REACTION_TORQUE_016_DIAGNOSTIC_CLASS,
        "model_sha256": sha256(diagnostic_file),
    }
    binding["controller_id"] = REACTION_TORQUE_016_DIAGNOSTIC_ID
    binding["scenario_id"] = REACTION_TORQUE_016_DIAGNOSTIC_SCENARIO
    binding["run_mode"] = "diagnostic_only"
    binding["diagnostic"] = {
        "parameter": "Plant.Sunray150Assembly.reaction_moment_ratio",
        "value": REACTION_TORQUE_016_DIAGNOSTIC_RATIO,
        "production_parameter_changed": False,
        "promotion_rule": "This result is an attribution experiment only. Do not change the production profile until the pinned PX4 Iris source is verified.",
    }
    binding["source_bindings"].append(
        {
            "role": "reaction_torque_016_diagnostic_runner",
            "path": relative(diagnostic_file),
            "expected_sha256": sha256(diagnostic_file),
        }
    )
    binding["claim_boundary"] = (
        "Real offline MWORKS diagnostic of the shared Sunray150Assembly with the embedded Official PID and "
        "reaction_moment_ratio=0.016. It isolates coefficient sensitivity only; it is not a production-parameter "
        "change, controller acceptance, PX4, Gazebo, ROS1, or flight evidence."
    )
    return binding


def resolve_yaw_authority_mapped_diagnostic_binding() -> dict[str, Any]:
    """Bind one allocation-only diagnostic while retaining the production plant profile."""

    binding = resolve_formal_binding()
    diagnostic_file = project_path(
        YAW_AUTHORITY_MAPPED_DIAGNOSTIC_FILE,
        label="yaw-authority mapped diagnostic runner",
    )
    adapter_file = project_path(
        YAW_AUTHORITY_MAPPED_ADAPTER_FILE,
        label="yaw-authority mapped diagnostic adapter",
    )
    diagnostic_text = diagnostic_file.read_text(encoding="utf-8")
    adapter_text = adapter_file.read_text(encoding="utf-8")
    if "extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner" not in diagnostic_text:
        raise ValueError("yaw-authority mapped diagnostic must extend RotorCommandRunner")
    if YAW_AUTHORITY_MAPPED_ADAPTER_CLASS not in diagnostic_text:
        raise ValueError("yaw-authority mapped diagnostic must bind the dedicated adapter")
    ratio_pattern = rf"legacy_effective_yaw_reaction_ratio\s*=\s*{YAW_AUTHORITY_MAPPED_LEGACY_RATIO:g}(?:0+)?\b"
    if re.search(ratio_pattern, adapter_text) is None:
        raise ValueError("yaw-authority mapped adapter must retain the approved 0.016 legacy authority")
    if "profile.moment_constant_ratio_m" not in adapter_text:
        raise ValueError("yaw-authority mapped adapter must map against the production physical ratio")
    if "mapped_collective_amplitude_error" not in adapter_text:
        raise ValueError("yaw-authority mapped adapter must expose its collective preservation check")

    binding["baseline_target"] = dict(require_object(binding["target"], label="formal baseline target"))
    binding["baseline_formal_adapter"] = dict(
        require_object(binding["formal_adapter"], label="formal baseline adapter")
    )
    binding["target"] = {
        "model_file": relative(diagnostic_file),
        "model_class": YAW_AUTHORITY_MAPPED_DIAGNOSTIC_CLASS,
        "model_sha256": sha256(diagnostic_file),
    }
    binding["formal_adapter"] = {
        "model_file": relative(adapter_file),
        "model_class": YAW_AUTHORITY_MAPPED_ADAPTER_CLASS,
        "model_sha256": sha256(adapter_file),
        "output_boundary": "ROTOR_COMMAND",
    }
    binding["controller_id"] = YAW_AUTHORITY_MAPPED_DIAGNOSTIC_ID
    binding["scenario_id"] = YAW_AUTHORITY_MAPPED_DIAGNOSTIC_SCENARIO
    binding["run_mode"] = "diagnostic_only"
    binding["diagnostic"] = {
        "kind": "yaw_authority_allocation_map",
        "legacy_effective_yaw_reaction_ratio": YAW_AUTHORITY_MAPPED_LEGACY_RATIO,
        "physical_reaction_ratio": "profile.moment_constant_ratio_m",
        "production_parameter_changed": False,
        "official_pid_gain_changed": False,
        "mass_or_geometry_changed": False,
        "collective_policy": "Preserve the linear sum of embedded mixer amplitudes while scaling only its projected yaw component.",
        "promotion_rule": "This result is diagnostic only. Promote only after the production adapter and formal binding are updated and the non-diagnostic OfficialPidFormalRunner passes.",
    }
    for source in binding["source_bindings"]:
        if source["role"] == "formal_adapter":
            source["path"] = relative(adapter_file)
            source["expected_sha256"] = sha256(adapter_file)
            break
    else:
        raise ValueError("formal binding has no formal_adapter source to replace")
    binding["source_bindings"].extend(
        [
            {
                "role": "yaw_authority_mapped_diagnostic_runner",
                "path": relative(diagnostic_file),
                "expected_sha256": sha256(diagnostic_file),
            },
            {
                "role": "yaw_authority_mapped_diagnostic_adapter",
                "path": relative(adapter_file),
                "expected_sha256": sha256(adapter_file),
            },
        ]
    )
    binding["claim_boundary"] = (
        "Real offline MWORKS diagnostic of the shared Sunray150Assembly with the embedded Official PID, the "
        "production physical reaction_moment_ratio, and an allocation-only legacy yaw-authority map. It is not "
        "a production controller acceptance, PX4, Gazebo, ROS1, or flight claim."
    )
    return binding


def resolve_run_binding(
    *, reaction_torque_016_diagnostic: bool, yaw_authority_mapped_diagnostic: bool
) -> dict[str, Any]:
    if reaction_torque_016_diagnostic and yaw_authority_mapped_diagnostic:
        raise ValueError("only one formal-baseline diagnostic may be selected")
    if reaction_torque_016_diagnostic:
        return resolve_reaction_torque_016_diagnostic_binding()
    if yaw_authority_mapped_diagnostic:
        return resolve_yaw_authority_mapped_diagnostic_binding()
    return resolve_formal_binding()


def verify_source_bindings(record: dict[str, Any], binding: dict[str, Any], *, phase: str) -> None:
    observations = record.setdefault("source_hash_observations", [])
    if not isinstance(observations, list):
        raise RuntimeError("source_hash_observations must be a list")
    for source in binding["source_bindings"]:
        path = project_path(str(source["path"]), label=str(source["role"]))
        actual = sha256(path)
        expected = str(source["expected_sha256"])
        observation = {
            "phase": phase,
            "role": source["role"],
            "path": relative(path),
            "sha256": actual,
            "expected_sha256": expected,
            "matches_binding": actual == expected,
        }
        observations.append(observation)
        if actual != expected:
            raise RuntimeError(
                f"Formal source binding hash changed during {phase}: {source['role']} {actual} != {expected}"
            )


def existing_terminal_record(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "RUN_RECORD.json"
    if not path.is_file():
        return None
    try:
        record = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(record, dict) and record.get("status") in TERMINAL_STATUSES:
        return record
    return None


def archive_rerun(run_dir: Path) -> str | None:
    previous = existing_terminal_record(run_dir)
    if previous is None:
        return None
    archive = run_dir / "superseded" / time.strftime("%Y%m%d_%H%M%S")
    archive.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    for name in ("RUN_RECORD.json", "FORMAL_BASELINE_STATUS.json", "logs", "raw", "metrics", "screenshots"):
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
            "schema": "mosim.g6_formal_closed_loop_baseline_superseded_run.v1",
            "archived_at": now_iso(),
            "source_run_dir": relative(run_dir),
            "copied": copied,
            "native_result_retention": "The prior Result.msr remains in its unique source root recorded by the archived RUN_RECORD.",
        },
    )
    return relative(archive)


def write_screenshot_manifest(run_dir: Path, record: dict[str, Any]) -> Path:
    output = run_dir / "logs" / "screenshot_manifest.json"
    write_json(
        output,
        {
            "schema": SCREENSHOT_SCHEMA,
            "controller_id": record.get("controller_id"),
            "scenario_id": record.get("scenario_id"),
            "target": record.get("formal_binding", {}).get("target"),
            "captures": record.get("mworks_phase_screenshots", []),
            "model_layout_boundary": record.get("model_layout_boundary"),
            "claim_boundary": record.get("claim_boundary"),
        },
    )
    return output


def terminal_status(record: dict[str, Any], *, cleanup: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema": STATUS_SCHEMA,
        "generated_at": now_iso(),
        "controller_id": record.get("controller_id"),
        "scenario_id": record.get("scenario_id"),
        "status": record.get("status"),
        "run_record": relative(Path(record["run_dir"]) / "RUN_RECORD.json"),
        "formal_matrix_membership": "not_member_of_frozen_46_route_matrix",
        "session_cleanup": cleanup,
        "claim_boundary": record.get("claim_boundary"),
    }


def formal_stability_gate(raw_output: Path) -> dict[str, Any]:
    """Reject a finite but divergent formal baseline from the terminal record."""

    with raw_output.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) < 2:
        raise RuntimeError(f"Formal baseline raw result is too short for stability review: {relative(raw_output)}")

    samples: list[tuple[float, float]] = []
    for index, row in enumerate(rows, start=2):
        try:
            time_s = float(row["time"])
            error_m = float(row["position_error_norm"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Formal baseline raw result lacks a numeric time/position_error_norm at CSV row {index}"
            ) from exc
        if not math.isfinite(time_s) or not math.isfinite(error_m):
            raise RuntimeError(f"Formal baseline raw result is non-finite at CSV row {index}")
        samples.append((time_s, error_m))

    final_time_s = samples[-1][0]
    tail_start_s = max(0.0, final_time_s - STABILITY_TAIL_WINDOW_S)
    tail_errors_m = [error_m for time_s, error_m in samples if time_s >= tail_start_s]
    if len(tail_errors_m) < 2:
        raise RuntimeError("Formal baseline has insufficient tail samples for stability review")

    terminal_error_m = samples[-1][1]
    tail_peak_error_m = max(tail_errors_m)
    tail_rmse_m = math.sqrt(sum(error_m * error_m for error_m in tail_errors_m) / len(tail_errors_m))
    checks = {
        "reaches_declared_stop_time": final_time_s >= BASELINE_DURATION_S - 0.05,
        "terminal_error_within_limit": terminal_error_m <= STABILITY_TERMINAL_ERROR_LIMIT_M,
        "tail_rmse_within_limit": tail_rmse_m <= STABILITY_TAIL_RMSE_LIMIT_M,
        "tail_peak_within_limit": tail_peak_error_m <= STABILITY_TAIL_PEAK_LIMIT_M,
    }
    return {
        "schema": "mosim.formal_baseline_stability_gate.v1",
        "raw_file": relative(raw_output),
        "tail_window_s": STABILITY_TAIL_WINDOW_S,
        "tail_start_s": tail_start_s,
        "final_time_s": final_time_s,
        "sample_count": len(samples),
        "tail_sample_count": len(tail_errors_m),
        "terminal_error_m": terminal_error_m,
        "tail_rmse_m": tail_rmse_m,
        "tail_peak_error_m": tail_peak_error_m,
        "limits": {
            "terminal_error_m": STABILITY_TERMINAL_ERROR_LIMIT_M,
            "tail_rmse_m": STABILITY_TAIL_RMSE_LIMIT_M,
            "tail_peak_error_m": STABILITY_TAIL_PEAK_LIMIT_M,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--wrapper", help="Optional explicit project-local Sysplorer MCP wrapper")
    parser.add_argument("--rerun", action="store_true", help="Archive an existing terminal baseline record before replacing it")
    parser.add_argument("--check-only", action="store_true", help="Validate the formal binding without starting MWORKS")
    parser.add_argument(
        "--reaction-torque-016-diagnostic",
        action="store_true",
        help="Run only the approved shared-assembly Cm=0.016 attribution diagnostic; production parameters remain unchanged",
    )
    parser.add_argument(
        "--yaw-authority-mapped-diagnostic",
        action="store_true",
        help="Run only the allocation-level Official PID yaw-authority diagnostic while preserving the production physical profile",
    )
    return parser.parse_args()


def checked_run_dir(path: Path) -> Path:
    run_dir = path.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        run_dir.relative_to(results_root)
    except ValueError as exc:
        raise ValueError("output-dir must stay below Results/") from exc
    return run_dir


def main() -> int:
    args = parse_args()
    binding = resolve_run_binding(
        reaction_torque_016_diagnostic=args.reaction_torque_016_diagnostic,
        yaw_authority_mapped_diagnostic=args.yaw_authority_mapped_diagnostic,
    )
    controller_id = require_text(binding.get("controller_id"), label="run controller id")
    scenario_id = require_text(binding.get("scenario_id"), label="run scenario id")
    duration_s = float(binding.get("duration_s", 0.0))
    if duration_s != BASELINE_DURATION_S:
        raise ValueError(f"Formal run duration must remain {BASELINE_DURATION_S:g} seconds")
    diagnostic = binding.get("diagnostic") if isinstance(binding.get("diagnostic"), dict) else None
    run_label = "Official PID reaction-torque diagnostic" if diagnostic else "Formal Official PID baseline"
    if args.check_only:
        print(json.dumps({"ok": True, "binding": binding, "variables": FORMAL_VARIABLES}, ensure_ascii=False, indent=2))
        return 0

    run_dir = checked_run_dir(args.output_dir)
    existing = existing_terminal_record(run_dir)
    if existing is not None and not args.rerun:
        print(f"Formal baseline already has terminal record: {relative(run_dir / 'RUN_RECORD.json')}")
        return 0 if existing.get("status") == "passed" else 1
    supersedes = archive_rerun(run_dir) if args.rerun else None
    for directory in (run_dir / "logs", run_dir / "raw", run_dir / "metrics", run_dir / "screenshots"):
        directory.mkdir(parents=True, exist_ok=True)

    target = require_object(binding["target"], label="formal target")
    target_file = project_path(str(target["model_file"]), label="formal target")
    target_class = str(target["model_class"])
    log_path = run_dir / "logs" / "mcp.jsonl"
    log_path.write_text("", encoding="utf-8")
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "controller_id": controller_id,
        "scenario_id": scenario_id,
        "started_at": now_iso(),
        "run_dir": relative(run_dir),
        "status": "running",
        "source": "MWORKS_MCP",
        "formal_binding": binding,
        "run_mode": binding.get("run_mode", "formal_baseline"),
        "diagnostic": diagnostic,
        "frozen_46_route_matrix": {
            "path": relative(G6_MATRIX_PATH),
            "membership": "not_member",
            "reason": "Formal Official PID baseline is a separate A/B binding and does not alter the frozen 46-route G6 evidence matrix.",
        },
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "model_layout_boundary": {
            "state": "thin_wrapper_not_accepted_as_controller_graphical_topology",
            "reason": (
                "OfficialPidFormalRunner is an extends-only formal harness. Its model-window capture proves "
                "the named MWORKS wrapper was checked, but an empty wrapper canvas is not controller graphical-layout evidence."
            ),
        },
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
        record["base_package_preload"] = preload_base_packages(client)
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
            raise RuntimeError(f"Formal baseline model load failed: {load}")
        verify_source_bindings(record, binding, phase="after_load")

        check = client.call_tool(
            "check_model",
            {"model_name": target_class, "stop_on_error": True},
            timeout_s=300,
        )
        write_json(run_dir / "logs" / "check_model_direct.json", check)
        if not check.get("ok"):
            raise RuntimeError(f"Formal baseline CheckModel failed: {check}")
        verify_source_bindings(record, binding, phase="after_check")

        opened = client.call_tool("model_manager", {"action": "open", "model_name": target_class}, timeout_s=60)
        write_json(run_dir / "logs" / "open_model.json", opened)
        if not opened.get("ok"):
            raise RuntimeError(f"Formal baseline model window failed to open: {opened}")
        model_capture = capture_phase(
            run_dir=run_dir,
            phase="after_check",
            target_class=target_class,
            expected_pid=expected_pid,
            destination=run_dir / "screenshots" / "01_after_check.png",
            capture_surface="model",
        )
        record["mworks_phase_screenshots"].append(model_capture)
        record["mworks_phase_observations"].append(
            "Formal Official PID runner passed CheckModel and its named wrapper window was captured. "
            "The wrapper canvas is not accepted as controller graphical-topology evidence."
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
        )
        write_json(run_dir / "logs" / "simulate_model_direct.json", simulation)
        if not simulation.get("ok"):
            raise RuntimeError(f"Formal baseline simulation failed: {simulation}")
        if simulation.get("simulate_api_reported_failure"):
            record["mworks_phase_observations"].append(
                "SimulateModel reported false. The formal baseline remains provisional until its current native Result.msr and complete time series pass the freshness gate."
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
            controller_id,
            "mworks_shared_assembly_reaction_torque_diagnostic" if diagnostic else "g6_formal_whole_aircraft_baseline",
            "standard_tracking",
        )
        metrics = require_object(read_json(metrics_json), label="formal baseline metrics")
        if metrics.get("valid") is not True:
            raise RuntimeError(f"Formal baseline metrics are invalid: {metrics}")
        stability = formal_stability_gate(raw_output)
        metrics["formal_stability_gate"] = stability
        write_json(metrics_json, metrics)
        record["formal_stability_gate"] = stability

        plot = show_native_plot(client, native_result=native_result, variables=RESULT_VIEWER_VARIABLES)
        write_json(run_dir / "logs" / "open_native_result_plot.json", plot)
        result_capture = capture_phase(
            run_dir=run_dir,
            phase="result_window",
            target_class=target_class,
            expected_pid=expected_pid,
            destination=run_dir / "screenshots" / "02_result_window.png",
            capture_surface="result_viewer",
        )
        record["mworks_phase_screenshots"].append(result_capture)
        record["mworks_phase_observations"].append(
            "The current native Result.msr was opened, position/reference variables were plotted for legible tracking review, and the rendered native result viewer was captured."
        )
        verify_source_bindings(record, binding, phase="before_record")
        record["metrics_summary"] = {
            "row_count": metrics.get("row_count"),
            "duration_s": metrics.get("duration_s"),
            "nan_count": metrics.get("nan_count"),
            "valid": metrics.get("valid"),
            "formal_stability_passed": stability["passed"],
        }
        if stability["passed"]:
            record["status"] = "passed"
        else:
            record["status"] = "stability_failed"
            record["error"] = {
                "message": (
                    f"{run_label} is numerically finite but failed the tail stability gate: "
                    f"{stability}"
                )
            }
    except Exception as exc:
        message = str(exc)
        classification = "source_hash_mismatch" if "source binding hash changed" in message else classify_error(message)
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
        cleanup = close_dedicated_session(
            client,
            session=session,
            output=run_dir / "logs" / "session_cleanup.json",
        )
    finally:
        client.close()
    record["session_cleanup"] = cleanup
    write_json(run_dir / "RUN_RECORD.json", record)
    write_json(run_dir / "FORMAL_BASELINE_STATUS.json", terminal_status(record, cleanup=cleanup))
    print(json.dumps({"status": record["status"], "run_record": relative(run_dir / "RUN_RECORD.json")}, ensure_ascii=False))
    if record["status"] != "passed":
        return 1
    return 0 if not (cleanup and cleanup.get("requested") and not cleanup.get("verified_closed")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
