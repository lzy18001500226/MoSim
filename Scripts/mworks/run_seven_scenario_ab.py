#!/usr/bin/env python3
"""Run the authorized Official PID versus px4ctrl seven-scenario MWORKS A/B.

Each invocation binds an existing FormalRunner to one versioned profile through
an ephemeral Modelica harness.  The harness is stored with that run's evidence
but is not added to the model library: it contains no controller logic and only
records the profile-selected trajectory and Plant injection parameters.

The script intentionally runs one case at a time.  A failed case receives a
terminal ``RUN_RECORD.json`` and does not prevent the remaining requested
cases from running.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import re
import shutil
import subprocess
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles.json"
PLANT_PATH = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Sunray150Assembly.mo"
RUNNER_SCRIPT = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
CAPTURE_SCRIPT = ROOT / "Scripts" / "tools" / "capture_window_background.ps1"
RESULT_ROOT = ROOT / "Results" / "control_platform" / "seven_scenario_ab"

CONTROLLERS: dict[str, dict[str, str]] = {
    "official_pid": {
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner",
        "model_slug": "OfficialPid",
    },
    "px4ctrl": {
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner",
        "model_slug": "Px4Ctrl",
    },
}

CORE_COLUMNS = ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref")
INJECTION_SCENARIOS = frozenset({
    "wind_disturbance",
    "parameter_mismatch",
    "motor_efficiency_fault",
})
INJECTION_COLUMNS = (
    "plant_gust_force_x_N",
    "plant_gust_force_y_N",
    "plant_gust_force_z_N",
    "plant_mass_kg",
    "controller_nominal_mass_kg",
    "fault_effectiveness_1",
    "fault_effectiveness_2",
    "fault_effectiveness_3",
    "fault_effectiveness_4",
)


class MworksBatchSession:
    """One dedicated MCP/Sysplorer session for the active A/B batch.

    The normal CLI launcher creates a dedicated Sysplorer instance per process.
    Reusing the client here prevents a 14-case experiment from accumulating
    14 orphaned MWORKS windows while retaining the native result viewer long
    enough for the outer evidence collector to capture it.
    """

    def __init__(self) -> None:
        spec = importlib.util.spec_from_file_location("mosim_mworks_runner", RUNNER_SCRIPT)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load MWORKS runner module: {RUNNER_SCRIPT}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.module = module
        self.session_log = RESULT_ROOT / "batch_session_mcp.jsonl"
        wrapper = module.resolve_wrapper(None)
        self.client = module.JsonlMcpClient(module.wrapper_command(wrapper), self.session_log)
        self.closed = False
        module.initialize_mcp_client(self.client)

    def run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        args = self.module.parse_args(command[2:])
        args.simulate_ex_options = self.module.parse_simulate_ex_options(args.simulate_ex_options_json)
        if args.metrics_csv is None:
            args.metrics_csv = args.metrics_json.with_suffix(".csv")
        active_log, final_log = self.module.prepare_log_output(args.log_output)
        self.client.set_log_path(active_log)
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.module.run_mcp_simulation(
                    args,
                    self.client,
                    active_log_output=active_log,
                    final_log_output=final_log,
                )
            return subprocess.CompletedProcess(command, 0, stdout.getvalue(), stderr.getvalue())
        except Exception:
            traceback.print_exc(file=stderr)
            return subprocess.CompletedProcess(command, 1, stdout.getvalue(), stderr.getvalue())

    def close(self) -> None:
        if self.closed:
            return
        self.client.set_log_path(self.session_log)
        try:
            shutdown = self.client.call_tool("session_manager", {"action": "shutdown"}, timeout_s=60)
            write_json(RESULT_ROOT / "batch_session_shutdown.json", {
                "schema": "mosim.seven_scenario_ab_batch_session_shutdown.v1",
                "recorded_at": utc_now(),
                "shutdown": shutdown,
            })
        finally:
            self.client.close()
            self.closed = True


@dataclass(frozen=True)
class Case:
    controller_id: str
    scenario_id: str
    profile: dict[str, Any]

    @property
    def controller(self) -> dict[str, str]:
        return CONTROLLERS[self.controller_id]

    @property
    def model_name(self) -> str:
        return f"SevenScenarioAB_{self.controller['model_slug']}_{camel_case(self.scenario_id)}"

    @property
    def output_dir(self) -> Path:
        return RESULT_ROOT / self.controller_id / self.scenario_id


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_hash(path: Path) -> str:
    return sha256_path(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def camel_case(value: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^A-Za-z0-9]+", value) if part)


def modelica_number(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Profile contains a non-finite number: {value!r}")
        return format(value, ".17g")
    raise TypeError(f"Unsupported Modelica scalar: {value!r}")


def modelica_value(value: Any) -> str:
    if isinstance(value, list):
        return "{" + ", ".join(modelica_value(item) for item in value) + "}"
    return modelica_number(value)


def profile_trajectory_modification(profile: dict[str, Any]) -> str:
    trajectory_class = str(profile["trajectory_class"])
    parameters = profile.get("trajectory_parameter_overrides", {})
    if not isinstance(parameters, dict):
        raise ValueError(f"trajectory_parameter_overrides must be an object: {profile['scenario_id']}")
    if not parameters:
        return trajectory_class
    modifications = ", ".join(
        f"{key} = {modelica_value(value)}" for key, value in parameters.items()
    )
    return f"{trajectory_class}({modifications})"


def render_harness(case: Case) -> str:
    runner_parameters = case.profile.get("runner_parameter_overrides", {})
    if not isinstance(runner_parameters, dict):
        raise ValueError(f"runner_parameter_overrides must be an object: {case.scenario_id}")
    trajectory = profile_trajectory_modification(case.profile)
    runner_modifications = [f"redeclare model Trajectory = {trajectory}"]
    runner_modifications.extend(
        f"{key} = {modelica_value(value)}" for key, value in runner_parameters.items()
    )
    runner_modification_text = ",\n    ".join(runner_modifications)
    duration = modelica_number(float(case.profile["duration_s"]))

    return f'''within ;
model {case.model_name}
  "Ephemeral evidence harness for {case.controller_id}/{case.scenario_id}"

  extends {case.controller['runner_class']}(
    {runner_modification_text});

  // Export internal Plant state used to validate the profile injection.
  Real injection_gust_force_N[3](each unit = "N");
  Real injection_plant_mass_kg(unit = "kg");
  Real injection_controller_nominal_mass_kg(unit = "kg");
  Real injection_fault_effectiveness[4];

equation
  injection_gust_force_N = plant.gust.force;
  injection_plant_mass_kg = plant.physical.wrapper.dynamics.mass_kg;
  injection_controller_nominal_mass_kg = controller.profile.takeoff_mass_kg;
  injection_fault_effectiveness = plant.physical.wrapper.dynamics.fault_effectiveness;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = {duration},
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end {case.model_name};
'''


def read_profiles() -> tuple[dict[str, Any], str]:
    document = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profiles = document.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 7:
        raise ValueError("Seven-scenario profile document must contain exactly seven profiles")
    expected = {
        "hover",
        "step_response",
        "figure8",
        "spiral",
        "wind_disturbance",
        "parameter_mismatch",
        "motor_efficiency_fault",
    }
    actual = {str(profile.get("scenario_id")) for profile in profiles if isinstance(profile, dict)}
    if actual != expected:
        raise ValueError(f"Unexpected scenario IDs: {sorted(actual)}")
    return document, json_hash(PROFILE_PATH)


def selected_cases(document: dict[str, Any], controllers: list[str], scenarios: list[str] | None) -> list[Case]:
    profile_by_scenario = {str(profile["scenario_id"]): profile for profile in document["profiles"]}
    ordered_scenarios = [str(profile["scenario_id"]) for profile in document["profiles"]]
    if scenarios:
        requested = set(scenarios)
        unknown = requested.difference(profile_by_scenario)
        if unknown:
            raise ValueError(f"Unknown scenario selector(s): {sorted(unknown)}")
        ordered_scenarios = [scenario for scenario in ordered_scenarios if scenario in requested]
    return [Case(controller_id, scenario_id, profile_by_scenario[scenario_id])
            for controller_id in controllers for scenario_id in ordered_scenarios]


def harness_path(case: Case) -> Path:
    return case.output_dir / "harness" / f"{case.model_name}.mo"


def stage_harness(case: Case) -> Path:
    path = harness_path(case)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_harness(case), encoding="utf-8", newline="\n")
    return path


def runner_arguments(case: Case, harness: Path) -> list[str]:
    run_root = case.output_dir
    raw = run_root / "raw" / "result.csv"
    metrics_json = run_root / "metrics" / "metrics.python.json"
    log = run_root / "logs" / "sysplorer_mcp.jsonl"
    args = [
        sys.executable,
        str(RUNNER_SCRIPT),
        "--model-file", str(ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"),
        "--extra-model-file", str(harness),
        "--model-name", case.model_name,
        "--target-time", f"0,{float(case.profile['duration_s']):g}",
        "--simulation-interval", "0.01",
        "--raw-output", str(raw),
        "--metrics-json", str(metrics_json),
        "--metrics-csv", str(metrics_json.with_suffix(".csv")),
        "--log-output", str(log),
        "--native-result-dir", str(run_root / "native_result"),
        "--scene-id", case.scenario_id,
        "--controller-id", case.controller_id,
        "--evidence-level", "formal_mworks_seven_scenario_ab_v1",
        "--gui-reset-windows",
        # Preserve a readable partial native result when SimulateModel reports
        # failure.  The outer validator still marks incomplete/divergent runs
        # invalid, but the raw trace remains an auditable negative sample.
        "--allow-readable-result-after-simulate-false",
    ]
    overrides = {
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
    }
    extras = {
        "plant_gust_force_x_N": "injection_gust_force_N[1]",
        "plant_gust_force_y_N": "injection_gust_force_N[2]",
        "plant_gust_force_z_N": "injection_gust_force_N[3]",
        "plant_mass_kg": "injection_plant_mass_kg",
        "controller_nominal_mass_kg": "injection_controller_nominal_mass_kg",
        "fault_effectiveness_1": "injection_fault_effectiveness[1]",
        "fault_effectiveness_2": "injection_fault_effectiveness[2]",
        "fault_effectiveness_3": "injection_fault_effectiveness[3]",
        "fault_effectiveness_4": "injection_fault_effectiveness[4]",
    }
    for alias, variable in overrides.items():
        args.extend(["--override-variable", f"{alias}={variable}"])
    for alias, variable in extras.items():
        args.extend(["--extra-variable", f"{alias}={variable}"])
    return args


def recovery_runner_arguments(case: Case) -> list[str]:
    """Read an existing failed native result without launching another simulation."""
    native_result = case.output_dir / "native_result" / case.model_name / "Result.msr"
    raw = case.output_dir / "raw" / "result.csv"
    metrics_json = case.output_dir / "metrics" / "metrics.python.json"
    log = case.output_dir / "logs" / "sysplorer_mcp_recovery.jsonl"
    args = [
        sys.executable,
        str(RUNNER_SCRIPT),
        "--read-native-result", str(native_result),
        "--model-name", case.model_name,
        "--raw-output", str(raw),
        "--metrics-json", str(metrics_json),
        "--metrics-csv", str(metrics_json.with_suffix(".csv")),
        "--log-output", str(log),
        "--scene-id", case.scenario_id,
        "--controller-id", case.controller_id,
        "--evidence-level", "formal_mworks_seven_scenario_ab_v1",
        "--no-gui-result-viewer",
        "--no-gui-open",
        "--shutdown-session",
    ]
    overrides = {
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
    }
    extras = {
        "plant_gust_force_x_N": "injection_gust_force_N[1]",
        "plant_gust_force_y_N": "injection_gust_force_N[2]",
        "plant_gust_force_z_N": "injection_gust_force_N[3]",
        "plant_mass_kg": "injection_plant_mass_kg",
        "controller_nominal_mass_kg": "injection_controller_nominal_mass_kg",
        "fault_effectiveness_1": "injection_fault_effectiveness[1]",
        "fault_effectiveness_2": "injection_fault_effectiveness[2]",
        "fault_effectiveness_3": "injection_fault_effectiveness[3]",
        "fault_effectiveness_4": "injection_fault_effectiveness[4]",
    }
    for alias, variable in overrides.items():
        args.extend(["--override-variable", f"{alias}={variable}"])
    for alias, variable in extras.items():
        args.extend(["--extra-variable", f"{alias}={variable}"])
    return args


def save_process_output(run_root: Path, completed: subprocess.CompletedProcess[str]) -> None:
    logs = run_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "runner_stdout.log").write_text(completed.stdout or "", encoding="utf-8")
    (logs / "runner_stderr.log").write_text(completed.stderr or "", encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [column for column in (*CORE_COLUMNS, *INJECTION_COLUMNS) if column not in fieldnames]
        if missing:
            raise ValueError(f"Raw CSV misses required exported columns: {', '.join(missing)}")
        rows: list[dict[str, float]] = []
        for row_number, row in enumerate(reader, start=2):
            numeric: dict[str, float] = {}
            for key, value in row.items():
                try:
                    numeric[str(key)] = float(value) if value not in (None, "") else float("nan")
                except ValueError as exc:
                    raise ValueError(f"Raw CSV row {row_number} has nonnumeric {key}={value!r}") from exc
            rows.append(numeric)
    return rows


def all_close(values: list[float], expected: float, tolerance: float = 1e-6) -> bool:
    return bool(values) and all(math.isfinite(value) and abs(value - expected) <= tolerance for value in values)


def validate_injection(case: Case, rows: list[dict[str, float]]) -> dict[str, Any]:
    scenario = case.scenario_id
    result: dict[str, Any] = {"scenario_id": scenario, "status": "not_applicable", "checks": []}
    if scenario == "wind_disturbance":
        values = [row["plant_gust_force_x_N"] for row in rows]
        required_stop = float(case.profile["duration_s"])
        observed_start = rows[0]["time"] if rows else None
        observed_stop = rows[-1]["time"] if rows else None
        force_passed = all_close(values, 0.25)
        full_window_observed = bool(
            rows
            and observed_start is not None
            and observed_stop is not None
            and observed_start <= 0.005
            and observed_stop >= required_stop - 0.005
        )
        status = (
            "passed" if force_passed and full_window_observed else
            "failed" if not force_passed else
            "not_evaluable"
        )
        result.update({
            "status": status,
            "checks": [
                {
                    "name": "persistent_world_frame_gust_force_x_N",
                    "expected": 0.25,
                    "min": min(values) if values else None,
                    "max": max(values) if values else None,
                    "sample_count": len(values),
                    "passed": force_passed,
                },
                {
                    "name": "full_disturbance_window_observed",
                    "expected_time_window": f"0 to {required_stop:g} s",
                    "observed_start_s": observed_start,
                    "observed_stop_s": observed_stop,
                    "passed": full_window_observed,
                    "reason": None if full_window_observed else (
                        "solver output ended before the full disturbance window"
                    ),
                },
            ],
        })
    elif scenario == "parameter_mismatch":
        plant_values = [row["plant_mass_kg"] for row in rows]
        controller_values = [row["controller_nominal_mass_kg"] for row in rows]
        plant_passed = all_close(plant_values, 1.2)
        controller_passed = all_close(controller_values, 1.0)
        result.update({
            "status": "passed" if plant_passed and controller_passed else "failed",
            "checks": [
                {
                    "name": "plant_mass_kg",
                    "expected": 1.2,
                    "min": min(plant_values) if plant_values else None,
                    "max": max(plant_values) if plant_values else None,
                    "passed": plant_passed,
                },
                {
                    "name": "controller_nominal_mass_kg",
                    "expected": 1.0,
                    "min": min(controller_values) if controller_values else None,
                    "max": max(controller_values) if controller_values else None,
                    "passed": controller_passed,
                },
            ],
        })
    elif scenario == "motor_efficiency_fault":
        rotor1_pre = [row["fault_effectiveness_1"] for row in rows if row["time"] < 15.0 - 1e-9]
        rotor1_post = [row["fault_effectiveness_1"] for row in rows if row["time"] >= 15.0 - 1e-9]
        other_rotors = {
            f"rotor_{index}": [row[f"fault_effectiveness_{index}"] for row in rows]
            for index in (2, 3, 4)
        }
        pre_passed = all_close(rotor1_pre, 1.0)
        post_passed = all_close(rotor1_post, 0.5)
        others_passed = all(all_close(values, 1.0) for values in other_rotors.values())
        result.update({
            "status": "passed" if pre_passed and post_passed and others_passed else "failed",
            "checks": [
                {
                    "name": "rotor_1_pre_fault_effectiveness",
                    "time_window": "t < 15 s",
                    "expected": 1.0,
                    "sample_count": len(rotor1_pre),
                    "min": min(rotor1_pre) if rotor1_pre else None,
                    "max": max(rotor1_pre) if rotor1_pre else None,
                    "passed": pre_passed,
                },
                {
                    "name": "rotor_1_post_fault_effectiveness",
                    "time_window": "t >= 15 s",
                    "expected": 0.5,
                    "sample_count": len(rotor1_post),
                    "min": min(rotor1_post) if rotor1_post else None,
                    "max": max(rotor1_post) if rotor1_post else None,
                    "passed": post_passed,
                },
                {
                    "name": "rotors_2_to_4_effectiveness",
                    "expected": 1.0,
                    "passed": others_passed,
                    "ranges": {
                        rotor: {"min": min(values) if values else None, "max": max(values) if values else None}
                        for rotor, values in other_rotors.items()
                    },
                },
            ],
        })
    return result


def not_evaluable_injection(case: Case, raw: Path) -> dict[str, Any]:
    """Describe a required Plant-trace check when the trace cannot be read."""
    reason = (
        "raw CSV could not be parsed into a Plant trace"
        if raw.is_file() else
        "raw CSV was not produced by the native solver"
    )
    return {
        "scenario_id": case.scenario_id,
        "status": "not_evaluable",
        "checks": [{
            "name": "raw_trace_available",
            "passed": False,
            "reason": reason,
        }],
    }


def validate_numerical_closure(case: Case, rows: list[dict[str, float]]) -> dict[str, Any]:
    if not rows:
        return {"passed": False, "reasons": ["raw CSV has no rows"]}
    finite = all(
        math.isfinite(row[column])
        for row in rows
        for column in CORE_COLUMNS
    )
    errors = [
        math.sqrt(
            (row["x"] - row["x_ref"]) ** 2
            + (row["y"] - row["y_ref"]) ** 2
            + (row["z"] - row["z_ref"]) ** 2
        )
        for row in rows
    ]
    expected_stop = float(case.profile["duration_s"])
    terminal_time = rows[-1]["time"]
    reaches_stop = math.isfinite(terminal_time) and terminal_time >= expected_stop - 0.005
    max_error = max(errors) if errors else float("nan")
    bounded = math.isfinite(max_error) and max_error < 5.0
    reasons: list[str] = []
    if not finite:
        reasons.append("core trajectory signals contain NaN or Inf")
    if not reaches_stop:
        reasons.append(f"simulation ended at {terminal_time:g}s before required {expected_stop:g}s")
    if not bounded:
        reasons.append(f"maximum position error {max_error:g}m is not below 5m")
    return {
        "passed": not reasons,
        "row_count": len(rows),
        "terminal_time_s": terminal_time,
        "maximum_position_error_m": max_error,
        "terminal_position_error_m": errors[-1] if errors else None,
        "reasons": reasons,
    }


def capture_result_window(case: Case) -> dict[str, Any]:
    screenshot_dir = case.output_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(CAPTURE_SCRIPT),
        "-TitleRegex",
        ".*",
        "-ProcessRegex",
        "^(mworks|sysplorer)$",
        "-OutDir",
        str(screenshot_dir),
        "-RestoreMinimized",
        "-MinimizeAfter",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (case.output_dir / "logs" / "capture_stdout.log").write_text(completed.stdout or "", encoding="utf-8")
    (case.output_dir / "logs" / "capture_stderr.log").write_text(completed.stderr or "", encoding="utf-8")
    manifest_path = screenshot_dir / "capture_manifest.json"
    rows: list[dict[str, Any]] = []
    if manifest_path.is_file():
        try:
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(parsed, list):
                rows = [row for row in parsed if isinstance(row, dict)]
        except json.JSONDecodeError:
            pass
    result_candidates = [
        row for row in rows
        if str(row.get("path") or "").endswith(".png")
        and re.search(r"plot|result|curve|chart|曲线|结果", str(row.get("title") or ""), re.IGNORECASE)
    ]
    main_window_candidates = [
        row for row in rows
        if str(row.get("path") or "").endswith(".png")
        and re.search(r"sysplorer|mworks", str(row.get("title") or ""), re.IGNORECASE)
    ]
    selected = result_candidates[0] if result_candidates else (
        main_window_candidates[0] if main_window_candidates else None
    )
    output = {
        "schema": "mosim.native_result_window_capture.v1",
        "captured_at": utc_now(),
        "capture_exit_code": completed.returncode,
        "capture_manifest": str(manifest_path.relative_to(ROOT)) if manifest_path.is_file() else None,
        "captured_windows": rows,
        "selected_result_window": selected,
        "valid_native_result_window_capture": selected is not None,
        "capture_kind": (
            "result_window" if result_candidates else
            "sysplorer_main_window_fallback" if selected else
            "missing"
        ),
        "visual_curve_review_required": bool(selected and not result_candidates),
    }
    write_json(case.output_dir / "logs" / "screenshot_manifest.json", output)
    return output


def recover_saved_result_window_capture(case: Case) -> dict[str, Any]:
    """Reuse a pre-existing native capture while materializing a failed result."""
    screenshot_dir = case.output_dir / "screenshots"
    manifest_path = screenshot_dir / "capture_manifest.json"
    rows: list[dict[str, Any]] = []
    if manifest_path.is_file():
        try:
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(parsed, list):
                rows = [row for row in parsed if isinstance(row, dict)]
        except json.JSONDecodeError:
            pass
    result_candidates = [
        row for row in rows
        if str(row.get("path") or "").endswith(".png")
        and re.search(r"plot|result|curve|chart|曲线|结果", str(row.get("title") or ""), re.IGNORECASE)
    ]
    main_window_candidates = [
        row for row in rows
        if str(row.get("path") or "").endswith(".png")
        and re.search(r"sysplorer|mworks", str(row.get("title") or ""), re.IGNORECASE)
    ]
    selected = result_candidates[0] if result_candidates else (
        main_window_candidates[0] if main_window_candidates else None
    )
    output = {
        "schema": "mosim.native_result_window_capture.v1",
        "captured_at": utc_now(),
        "capture_exit_code": None,
        "capture_manifest": str(manifest_path.relative_to(ROOT)) if manifest_path.is_file() else None,
        "captured_windows": rows,
        "selected_result_window": selected,
        "valid_native_result_window_capture": selected is not None,
        "capture_kind": (
            "result_window" if result_candidates else
            "sysplorer_main_window_fallback" if selected else
            "missing"
        ),
        "visual_curve_review_required": bool(selected and not result_candidates),
        "recovered_from_existing_capture": True,
    }
    write_json(case.output_dir / "logs" / "screenshot_manifest.json", output)
    return output


def project_relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def write_run_record(
    case: Case,
    profile_hash: str,
    harness: Path,
    *,
    process: subprocess.CompletedProcess[str] | None,
    numerical: dict[str, Any] | None,
    injection: dict[str, Any] | None,
    screenshot: dict[str, Any] | None,
    error: str | None,
) -> dict[str, Any]:
    raw = case.output_dir / "raw" / "result.csv"
    metrics = case.output_dir / "metrics" / "metrics.python.json"
    if injection is None and case.scenario_id in INJECTION_SCENARIOS:
        injection = not_evaluable_injection(case, raw)
    if metrics.is_file():
        # The Python metrics are deterministic and are retained only as an
        # immediate run artifact.  Syslab writes the final METRICS.json later.
        shutil.copyfile(metrics, case.output_dir / "metrics" / "METRICS.json")
    artifacts = {
        "raw_csv": project_relative(raw) if raw.is_file() else None,
        "metrics_json": project_relative(case.output_dir / "metrics" / "METRICS.json")
        if (case.output_dir / "metrics" / "METRICS.json").is_file() else None,
        "native_result_directory": project_relative(case.output_dir / "native_result")
        if (case.output_dir / "native_result").is_dir() else None,
        "result_window_screenshot": (
            screenshot.get("selected_result_window", {}).get("path")
            if screenshot and isinstance(screenshot.get("selected_result_window"), dict) else None
        ),
        "screenshot_manifest": project_relative(case.output_dir / "logs" / "screenshot_manifest.json")
        if (case.output_dir / "logs" / "screenshot_manifest.json").is_file() else None,
        "mcp_log": project_relative(case.output_dir / "logs" / "sysplorer_mcp.jsonl")
        if (case.output_dir / "logs" / "sysplorer_mcp.jsonl").is_file() else None,
    }
    failure_reasons: list[str] = []
    if process is None or process.returncode != 0:
        failure_reasons.append("MWORKS runner returned a nonzero exit code")
    if error:
        failure_reasons.append(error)
    if numerical and not numerical.get("passed"):
        failure_reasons.extend(str(reason) for reason in numerical.get("reasons", []))
    if injection and injection.get("status") == "failed":
        failure_reasons.append("Plant injection self-check failed")
    if injection and injection.get("status") == "not_evaluable":
        failure_reasons.append("Plant injection self-check not evaluable from the raw trace")
    if screenshot and not screenshot.get("valid_native_result_window_capture"):
        failure_reasons.append("No native result-window capture was identified")
    if not raw.is_file():
        failure_reasons.append("raw CSV is missing")
    if not (case.output_dir / "metrics" / "METRICS.json").is_file():
        failure_reasons.append("metrics JSON is missing")
    record = {
        "schema": "mosim.seven_scenario_ab_run_record.v1",
        "recorded_at": utc_now(),
        "status": "valid" if not failure_reasons else "invalid",
        "failure_reasons": failure_reasons,
        "controller_id": case.controller_id,
        "runner_class": case.controller["runner_class"],
        "scenario_id": case.scenario_id,
        "profile_id": case.profile["profile_id"],
        "source": "MWORKS_MCP",
        "execution": {
            "solver_algorithm": "Dassl",
            "solver_tolerance": 0.0001,
            "result_interval_s": 0.01,
            "stop_time_s": case.profile["duration_s"],
            "runner_command_exit_code": process.returncode if process else None,
        },
        "result_data_status": (
            "complete" if numerical and numerical.get("passed") else
            "partial" if raw.is_file() else
            "missing"
        ),
        "hashes": {
            "seven_scenario_profile_sha256": profile_hash,
            "harness_sha256": sha256_path(harness) if harness.is_file() else None,
            "runner_source_sha256": sha256_path(
                ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Formal"
                / ("OfficialPidFormalRunner.mo" if case.controller_id == "official_pid" else "Px4CtrlFormalRunner.mo")
            ),
            "plant_source_sha256": sha256_path(PLANT_PATH),
            "raw_csv_sha256": sha256_path(raw) if raw.is_file() else None,
        },
        "artifacts": artifacts,
        "numerical_closure": numerical,
        "injection_self_check": injection,
    }
    write_json(case.output_dir / "RUN_RECORD.json", record)
    return record


def run_case(
    case: Case,
    profile_hash: str,
    *,
    dry_run: bool,
    overwrite: bool,
    recover_existing: bool,
    batch_session: MworksBatchSession | None = None,
) -> dict[str, Any]:
    run_record = case.output_dir / "RUN_RECORD.json"
    if run_record.is_file() and not overwrite and not recover_existing:
        existing = json.loads(run_record.read_text(encoding="utf-8"))
        return {"skipped": True, "record": existing}

    if overwrite and case.output_dir.exists():
        # Only this exact evidence leaf is owned by this command.
        shutil.rmtree(case.output_dir)
    harness = stage_harness(case)
    command = recovery_runner_arguments(case) if recover_existing else runner_arguments(case, harness)
    run_config_path = case.output_dir / (
        "RECOVERY_RUN_CONFIG.json" if recover_existing else "RUN_CONFIG.json"
    )
    write_json(run_config_path, {
        "schema": "mosim.seven_scenario_ab_run_config.v1",
        "generated_at": utc_now(),
        "mode": "recover_existing_native_result" if recover_existing else "simulate",
        "controller_id": case.controller_id,
        "scenario_id": case.scenario_id,
        "profile": case.profile,
        "profile_sha256": profile_hash,
        "harness": project_relative(harness),
        "command": command,
    })
    if dry_run:
        return {"skipped": False, "dry_run": True, "harness": str(harness)}

    process: subprocess.CompletedProcess[str] | None = None
    numerical: dict[str, Any] | None = None
    injection: dict[str, Any] | None = None
    screenshot: dict[str, Any] | None = None
    error: str | None = None
    try:
        process = (
            batch_session.run(command)
            if batch_session is not None else
            subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        )
        save_process_output(case.output_dir, process)
        raw = case.output_dir / "raw" / "result.csv"
        if raw.is_file():
            rows = read_csv_rows(raw)
            numerical = validate_numerical_closure(case, rows)
            injection = validate_injection(case, rows)
        if recover_existing:
            screenshot = recover_saved_result_window_capture(case)
        else:
            screenshot = capture_result_window(case)
        if process.returncode == 0 and not raw.is_file():
            error = "MWORKS runner reported success but did not write raw CSV"
    except Exception as exc:  # Keep a terminal invalid record for the case.
        error = f"{type(exc).__name__}: {exc}"
    record = write_run_record(
        case,
        profile_hash,
        harness,
        process=process,
        numerical=numerical,
        injection=injection,
        screenshot=screenshot,
        error=error,
    )
    return {"skipped": False, "record": record}


def persisted_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(RESULT_ROOT.glob("*/*/RUN_RECORD.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def write_matrix(records: list[dict[str, Any]]) -> Path:
    # The evidence tree is authoritative.  This keeps a targeted recovery from
    # replacing the matrix with only the one case handled by that invocation.
    del records
    rows: list[dict[str, Any]] = []
    for record in persisted_records():
        numerical = record.get("numerical_closure") if isinstance(record.get("numerical_closure"), dict) else {}
        metrics: dict[str, Any] = {}
        metrics_path = record.get("artifacts", {}).get("metrics_json") if isinstance(record.get("artifacts"), dict) else None
        if isinstance(metrics_path, str):
            candidate = ROOT / metrics_path
            if candidate.is_file():
                try:
                    parsed = json.loads(candidate.read_text(encoding="utf-8"))
                    if isinstance(parsed, dict):
                        metrics = parsed
                except json.JSONDecodeError:
                    pass
        rows.append({
            "controller_id": record.get("controller_id"),
            "scenario_id": record.get("scenario_id"),
            "status": record.get("status"),
            "result_data_status": record.get("result_data_status"),
            "position_rmse_m": metrics.get("position_rmse_m"),
            "tail_rmse_m": metrics.get("tail_rmse_m"),
            "maximum_position_error_m": numerical.get("maximum_position_error_m"),
            "terminal_position_error_m": numerical.get("terminal_position_error_m"),
            "injection_status": (record.get("injection_self_check") or {}).get("status"),
        })
    matrix = {
        "schema": "mosim.seven_scenario_ab_matrix.v1",
        "generated_at": utc_now(),
        "row_count": len(rows),
        "rows": rows,
    }
    path = RESULT_ROOT / "SCENARIO_RMSE_MATRIX.pending_syslab.json"
    write_json(path, matrix)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--controller",
        action="append",
        choices=sorted(CONTROLLERS),
        help="Run only this controller; repeatable. Defaults to both authorized controllers.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        help="Run only this scenario; repeatable. Defaults to all seven profiles.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Write harnesses and configs without invoking MWORKS.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing exact controller/scenario evidence leaf.")
    parser.add_argument(
        "--recover-existing",
        action="store_true",
        help="Materialize an existing native Result.msr without launching another simulation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document, profile_hash = read_profiles()
    controllers = args.controller or list(CONTROLLERS)
    cases = selected_cases(document, controllers, args.scenario)
    if not cases:
        raise ValueError("No cases selected")
    records: list[dict[str, Any]] = []
    batch_session = None if args.dry_run or args.recover_existing else MworksBatchSession()
    try:
        for index, case in enumerate(cases, start=1):
            print(f"[{index}/{len(cases)}] {case.controller_id}/{case.scenario_id}", flush=True)
            records.append(run_case(
                case,
                profile_hash,
                dry_run=args.dry_run,
                overwrite=args.overwrite,
                recover_existing=args.recover_existing,
                batch_session=batch_session,
            ))
    finally:
        if batch_session is not None:
            batch_session.close()
    matrix = write_matrix(records)
    invalid_count = sum(
        1 for item in records
        if isinstance(item.get("record"), dict) and item["record"].get("status") == "invalid"
    )
    print(f"Matrix: {matrix}")
    print(f"Cases: {len(records)}, invalid: {invalid_count}")
    # Individual failures are represented as invalid evidence, not a batch
    # abort.  Reserve a nonzero process exit for orchestration-level errors.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
