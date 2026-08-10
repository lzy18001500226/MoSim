#!/usr/bin/env python3
"""Run the seven shared profiles through the native Official PID Sysblock Golden route.

This is deliberately separate from ``run_seven_scenario_ab.py``.  That
historical A/B driver binds Formal runners, while this driver binds the
reviewable native Sysblock controller to the same trajectory and Plant
injection profiles without replacing or overwriting the Formal evidence.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import math
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_v2.json"
CONTRACT_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract_v2.json"
RUNNER_SCRIPT = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
MODEL_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
RUNNER_CLASS = (
    "MoSimQuadrotorModel.Experiment.Runners.Golden."
    "OfficialPidSysblockSingleUavRunner"
)
DEFAULT_RESULT_ROOT = ROOT / "Results" / "control_platform" / "official_pid_native_sysblock_seven_scenario_20260809"
EVIDENCE_LEVEL = "mworks_native_sysblock_official_pid_profile_replay_v1"
SCENARIO_IDS = (
    "hover",
    "step_response",
    "figure8",
    "spiral",
    "wind_disturbance",
    "parameter_mismatch",
    "motor_efficiency_fault",
)

CORE_OVERRIDES = (
    ("x", "position[1]"),
    ("y", "position[2]"),
    ("z", "position[3]"),
    ("x_ref", "position_ref[1]"),
    ("y_ref", "position_ref[2]"),
    ("z_ref", "position_ref[3]"),
    ("roll", "attitude[1]"),
    ("pitch", "attitude[2]"),
    ("yaw", "attitude[3]"),
    ("u1", "rotor_command[1]"),
    ("u2", "rotor_command[2]"),
    ("u3", "rotor_command[3]"),
    ("u4", "rotor_command[4]"),
)
INJECTION_VARIABLES = (
    ("plant_gust_force_x_N", "injection_gust_force_N[1]"),
    ("plant_gust_force_y_N", "injection_gust_force_N[2]"),
    ("plant_gust_force_z_N", "injection_gust_force_N[3]"),
    ("plant_mass_kg", "injection_plant_mass_kg"),
    ("plant_inertia_11_kg_m2", "injection_plant_inertia_diagonal_kg_m2[1]"),
    ("plant_inertia_22_kg_m2", "injection_plant_inertia_diagonal_kg_m2[2]"),
    ("plant_inertia_33_kg_m2", "injection_plant_inertia_diagonal_kg_m2[3]"),
    ("fault_effectiveness_1", "injection_fault_effectiveness[1]"),
    ("fault_effectiveness_2", "injection_fault_effectiveness[2]"),
    ("fault_effectiveness_3", "injection_fault_effectiveness[3]"),
    ("fault_effectiveness_4", "injection_fault_effectiveness[4]"),
)


@dataclass(frozen=True)
class Case:
    profile: dict[str, Any]
    result_root: Path

    @property
    def scenario_id(self) -> str:
        return str(self.profile["scenario_id"])

    @property
    def model_name(self) -> str:
        return f"NativeSysblockOfficialPid{camel_case(self.scenario_id)}"

    @property
    def output_dir(self) -> Path:
        return self.result_root / "official_pid_native_sysblock" / self.scenario_id


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def camel_case(value: str) -> str:
    return "".join(part.capitalize() for part in value.split("_"))


def modelica_number(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Modelica numeric value is invalid: {value!r}")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"Modelica numeric value is non-finite: {value!r}")
    return f"{numeric:.17g}"


def modelica_value(value: Any) -> str:
    if isinstance(value, list):
        return "{" + ", ".join(modelica_value(item) for item in value) + "}"
    return modelica_number(value)


def profile_trajectory_modification(profile: dict[str, Any]) -> str:
    trajectory_class = str(profile["trajectory_class"])
    overrides = profile.get("trajectory_parameter_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError(f"trajectory_parameter_overrides must be an object: {profile['scenario_id']}")
    if not overrides:
        return trajectory_class
    arguments = ", ".join(f"{key} = {modelica_value(value)}" for key, value in overrides.items())
    return f"{trajectory_class}({arguments})"


def render_harness(case: Case) -> str:
    profile = case.profile
    runner_overrides = profile.get("runner_parameter_overrides", {})
    if not isinstance(runner_overrides, dict):
        raise ValueError(f"runner_parameter_overrides must be an object: {case.scenario_id}")
    modifications = [
        f"redeclare model Trajectory = {profile_trajectory_modification(profile)}",
        *(f"{key} = {modelica_value(value)}" for key, value in runner_overrides.items()),
    ]
    duration = modelica_number(profile["duration_s"])
    modification_text = ",\n    ".join(modifications)

    return f'''within ;
model {case.model_name}
  "Native Sysblock evidence harness for official_pid/{case.scenario_id}"

  extends {RUNNER_CLASS}(
    {modification_text});

  // Plant injection observability only. The native Sysblock constants are not
  // duplicated as Modelica parameters or synthetic diagnostic consumers.
  Real injection_gust_force_N[3](each unit = "N");
  Real injection_plant_mass_kg(unit = "kg");
  Real injection_plant_inertia_diagonal_kg_m2[3](each unit = "kg.m2");
  Real injection_fault_effectiveness[4];

equation
  injection_gust_force_N = plant.gust.force;
  injection_plant_mass_kg = plant.physical.wrapper.dynamics.mass_kg;
  injection_plant_inertia_diagonal_kg_m2 = {{
    plant.physical.body.I_11,
    plant.physical.body.I_22,
    plant.physical.body.I_33}};
  injection_fault_effectiveness = plant.physical.wrapper.dynamics.fault_effectiveness;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = {duration},
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end {case.model_name};
'''


def read_profiles(path: Path) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    profiles = document.get("profiles") if isinstance(document, dict) else None
    if not isinstance(profiles, list):
        raise ValueError(f"Profile document has no profile list: {path}")
    scenario_ids = tuple(str(profile.get("scenario_id")) for profile in profiles if isinstance(profile, dict))
    if scenario_ids != SCENARIO_IDS:
        raise ValueError(f"Unexpected ordered scenario IDs: {scenario_ids}")
    if any(not isinstance(profile, dict) for profile in profiles):
        raise ValueError("Profile document contains a non-object profile")
    return profiles, sha256_path(path), document


def read_contract(path: Path) -> tuple[str, dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"Injection contract is not an object: {path}")
    return sha256_path(path), document


def select_cases(profiles: list[dict[str, Any]], scenarios: list[str] | None, result_root: Path) -> list[Case]:
    requested = set(scenarios or SCENARIO_IDS)
    unknown = requested.difference(SCENARIO_IDS)
    if unknown:
        raise ValueError(f"Unknown scenario(s): {', '.join(sorted(unknown))}")
    return [Case(profile=profile, result_root=result_root) for profile in profiles if str(profile["scenario_id"]) in requested]


def metrics_context(case: Case) -> dict[str, float]:
    overrides = case.profile["runner_parameter_overrides"]
    context: dict[str, float] = {}
    if case.scenario_id == "wind_disturbance":
        context["gust_start_s"] = float(overrides["gust_start_s"])
        context["gust_duration_s"] = float(overrides["gust_duration_s"])
    if case.scenario_id == "motor_efficiency_fault":
        context["fault_start_s"] = float(overrides["fault_start_s"])
        context["fault_rotor_effectiveness"] = float(overrides["fault_rotor_effectiveness"])
    return context


def harness_path(case: Case) -> Path:
    return case.output_dir / "harness" / f"{case.model_name}.mo"


def runner_arguments(case: Case, *, timeout_s: float) -> list[str]:
    output = case.output_dir
    arguments = [
        "--model-file", str(MODEL_FILE),
        "--extra-model-file", str(harness_path(case)),
        "--model-name", case.model_name,
        "--target-time", f"0,{float(case.profile['duration_s']):g}",
        "--simulation-interval", "0.01",
        "--simulation-timeout-s", f"{timeout_s:g}",
        "--raw-output", str(output / "raw" / "result.csv"),
        "--metrics-json", str(output / "metrics" / "metrics.python.json"),
        "--metrics-csv", str(output / "metrics" / "metrics.python.csv"),
        "--log-output", str(output / "logs" / "sysplorer_mcp.jsonl"),
        "--native-result-dir", str(output / "native_result"),
        "--scene-id", case.scenario_id,
        "--controller-id", "official_pid_native_sysblock",
        "--evidence-level", EVIDENCE_LEVEL,
        "--metrics-context-json", json.dumps(metrics_context(case), sort_keys=True),
        # Keep a native Result.msr but never open/reset GUI plots or windows in this batch.
        "--no-gui-open",
    ]
    for alias, variable in CORE_OVERRIDES:
        arguments.extend(["--override-variable", f"{alias}={variable}"])
    for alias, variable in INJECTION_VARIABLES:
        arguments.extend(["--extra-variable", f"{alias}={variable}"])
    return arguments


def stage_case(case: Case, *, profile_path: Path, profile_hash: str, contract_path: Path, contract_hash: str, profile_document: dict[str, Any]) -> None:
    harness = harness_path(case)
    harness.parent.mkdir(parents=True, exist_ok=True)
    harness.write_text(render_harness(case), encoding="utf-8", newline="\n")
    write_json(case.output_dir / "RUN_CONFIG.json", {
        "schema": "mosim.native_sysblock_seven_scenario_run_config.v1",
        "created_at": utc_now(),
        "controller_id": "official_pid_native_sysblock",
        "scenario_id": case.scenario_id,
        "model_name": case.model_name,
        "runner_class": RUNNER_CLASS,
        "profile": case.profile,
        "profile_document": project_relative(profile_path),
        "profile_sha256": profile_hash,
        "profile_schema": profile_document.get("schema"),
        "profile_version": profile_document.get("version"),
        "injection_contract_document": project_relative(contract_path),
        "injection_contract_sha256": contract_hash,
        "harness": project_relative(harness),
        "evidence_level": EVIDENCE_LEVEL,
        "execution_boundary": "native_sysblock_core plus Modelica PlantBridge",
        "profile_reuse_boundary": (
            "Uses the v2 trajectory and Plant injection values only. It is a separate native Sysblock "
            "evidence lane, not a replacement for the Formal v2 A/B matrix."
        ),
        "command_arguments": runner_arguments(case, timeout_s=240.0),
    })


def read_raw(path: Path) -> tuple[list[dict[str, float]], list[str]]:
    if not path.is_file():
        return [], [f"raw CSV does not exist: {path}"]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        required = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "u1", "u2", "u3", "u4"]
        missing = [field for field in required if field not in fields]
        if missing:
            return [], [f"raw CSV misses required columns: {', '.join(missing)}"]
        rows: list[dict[str, float]] = []
        try:
            for item in reader:
                rows.append({name: float(value) if value not in (None, "") else math.nan for name, value in item.items()})
        except ValueError as exc:
            return [], [f"raw CSV has a non-numeric value: {exc}"]
    if len(rows) <= 10:
        return rows, [f"raw CSV has only {len(rows)} rows"]
    nonfinite = [
        field for field in ("time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "u1", "u2", "u3", "u4")
        if any(not math.isfinite(row[field]) for row in rows)
    ]
    return rows, ([f"raw CSV has non-finite values: {', '.join(nonfinite)}"] if nonfinite else [])


def injection_observation(case: Case, rows: list[dict[str, float]]) -> dict[str, Any]:
    if not rows:
        return {"status": "not_evaluable", "reason": "raw result is unavailable"}
    scenario = case.scenario_id
    overrides = case.profile["runner_parameter_overrides"]
    if scenario == "wind_disturbance":
        start = float(overrides["gust_start_s"])
        expected = [float(value) for value in overrides["gust_force"]]
        active = [row for row in rows if row["time"] >= start + 0.01]
        aliases = ("plant_gust_force_x_N", "plant_gust_force_y_N", "plant_gust_force_z_N")
        observed = [[row.get(alias, math.nan) for row in active] for alias in aliases]
        passed = bool(active) and all(
            all(math.isfinite(value) and abs(value - target) <= 1e-6 for value in values)
            for values, target in zip(observed, expected)
        )
        return {"status": "passed" if passed else "failed", "start_s": start, "expected_force_N": expected}
    if scenario == "motor_efficiency_fault":
        start = float(overrides["fault_start_s"])
        target = float(overrides["fault_rotor_effectiveness"])
        pre = [row.get("fault_effectiveness_1", math.nan) for row in rows if row["time"] < start - 0.01]
        post = [row.get("fault_effectiveness_1", math.nan) for row in rows if row["time"] >= start + 0.01]
        passed = bool(pre and post) and all(abs(value - 1.0) <= 1e-6 for value in pre) and all(abs(value - target) <= 1e-6 for value in post)
        return {"status": "passed" if passed else "failed", "start_s": start, "expected_effectiveness": target}
    if scenario == "parameter_mismatch":
        values = [row.get("plant_mass_kg", math.nan) for row in rows]
        finite_values = [value for value in values if math.isfinite(value)]
        return {
            "status": "observed" if finite_values else "failed",
            "mass_scale": float(overrides["mass_scale"]),
            "observed_plant_mass_kg": {"min": min(finite_values) if finite_values else None, "max": max(finite_values) if finite_values else None},
        }
    return {"status": "not_applicable"}


def verify_case(case: Case, *, return_code: int) -> dict[str, Any]:
    raw = case.output_dir / "raw" / "result.csv"
    metrics = case.output_dir / "metrics" / "metrics.python.json"
    rows, failures = read_raw(raw)
    expected_stop = float(case.profile["duration_s"])
    if rows and abs(rows[0]["time"]) > 1e-9:
        failures.append(f"raw result starts at {rows[0]['time']}, expected 0")
    if rows and rows[-1]["time"] < expected_stop - 0.005:
        failures.append(f"raw result ends at {rows[-1]['time']}, expected at least {expected_stop}")
    metric_payload: dict[str, Any] | None = None
    if not metrics.is_file():
        failures.append(f"metrics JSON does not exist: {metrics}")
    else:
        try:
            metric_payload = json.loads(metrics.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"metrics JSON is unreadable: {exc}")
    injection = injection_observation(case, rows)
    if injection.get("status") == "failed":
        failures.append(f"scenario injection verification failed: {case.scenario_id}")
    if return_code != 0:
        failures.append(f"MWORKS runner exited {return_code}")
    return {
        "status": "valid" if not failures else "invalid",
        "row_count": len(rows),
        "time_range_s": [rows[0]["time"], rows[-1]["time"]] if rows else None,
        "injection": injection,
        "metrics": metric_payload,
        "failures": failures,
    }


def load_runner_module() -> Any:
    spec = importlib.util.spec_from_file_location("native_sysblock_mworks_runner", RUNNER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load MWORKS runner: {RUNNER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute_case(case: Case, runner: Any, client: Any, *, timeout_s: float) -> dict[str, Any]:
    arguments = runner_arguments(case, timeout_s=timeout_s)
    parsed = runner.parse_args(arguments)
    parsed.simulate_ex_options = runner.parse_simulate_ex_options(parsed.simulate_ex_options_json)
    parsed.metrics_context = runner.parse_metrics_context(parsed.metrics_context_json)
    if parsed.metrics_csv is None:
        parsed.metrics_csv = parsed.metrics_json.with_suffix(".csv")
    active_log, final_log = runner.prepare_log_output(parsed.log_output)
    client.set_log_path(active_log)
    stdout = io.StringIO()
    stderr = io.StringIO()
    return_code = 0
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            runner.run_mcp_simulation(parsed, client, active_log_output=active_log, final_log_output=final_log)
    except Exception:
        return_code = 1
        traceback.print_exc(file=stderr)
    logs = case.output_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "runner_stdout.log").write_text(stdout.getvalue(), encoding="utf-8")
    (logs / "runner_stderr.log").write_text(stderr.getvalue(), encoding="utf-8")
    verification = verify_case(case, return_code=return_code)
    return {"return_code": return_code, "verification": verification}


def write_record(case: Case, execution: dict[str, Any] | None, *, dry_run: bool) -> dict[str, Any]:
    verification = execution.get("verification") if execution else None
    status = "planned" if dry_run else str(verification["status"])
    record = {
        "schema": "mosim.native_sysblock_seven_scenario_run_record.v1",
        "recorded_at": utc_now(),
        "status": status,
        "controller_id": "official_pid_native_sysblock",
        "scenario_id": case.scenario_id,
        "model_name": case.model_name,
        "runner_class": RUNNER_CLASS,
        "source": "MWORKS_MCP" if not dry_run else "not_run",
        "evidence_level": EVIDENCE_LEVEL,
        "raw_result": project_relative(case.output_dir / "raw" / "result.csv"),
        "metrics": project_relative(case.output_dir / "metrics" / "metrics.python.json"),
        "mcp_log": project_relative(case.output_dir / "logs" / "sysplorer_mcp.jsonl"),
        "native_result_directory": project_relative(case.output_dir / "native_result"),
        "harness": project_relative(harness_path(case)),
        "verification": verification,
        "will_not_click_activation_login": True,
        "live_mworks_touched": not dry_run,
        "screenshot_incomplete": not dry_run,
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": (
            "Batch run retains native Result.msr and MCP/raw/metric evidence but deliberately skips GUI plot/animation "
            "opening and window reset. It makes no per-scenario GUI-layout acceptance claim."
        ),
        "wiring_claim_boundary": (
            "The checked native Sysblock Core/Adapter/Mapper diagrams are the graphical audit surface. "
            "The Modelica PlantBridge is behavior-verified by the exported result series; MWORKS renders that cross-domain boundary as dashed red links."
        ),
    }
    write_json(case.output_dir / "RUN_RECORD.json", record)
    return record


def write_matrix(
    records: list[dict[str, Any]],
    *,
    result_root: Path,
    profile_path: Path,
    profile_hash: str,
    contract_path: Path,
    contract_hash: str,
    dry_run: bool,
) -> Path:
    valid_count = sum(record["status"] == "valid" for record in records)
    path = result_root / "NATIVE_SYSBLOCK_SEVEN_SCENARIO_MATRIX.json"
    write_json(path, {
        "schema": "mosim.native_sysblock_seven_scenario_matrix.v1",
        "generated_at": utc_now(),
        "controller_id": "official_pid_native_sysblock",
        "runner_class": RUNNER_CLASS,
        "profile_document": project_relative(profile_path),
        "profile_sha256": profile_hash,
        "injection_contract_document": project_relative(contract_path),
        "injection_contract_sha256": contract_hash,
        "evidence_level": EVIDENCE_LEVEL,
        "status": (
            "planned"
            if dry_run
            else "pass" if valid_count == len(records) and records else "partial_or_invalid"
        ),
        "scenario_count": len(records),
        "valid_count": valid_count,
        "rows": records,
    })
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", help="Run one scenario; repeatable. Defaults to all seven.")
    parser.add_argument("--profile-path", type=Path, default=PROFILE_PATH)
    parser.add_argument("--contract-path", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--result-root", type=Path, default=DEFAULT_RESULT_ROOT)
    parser.add_argument("--simulation-timeout-s", type=float, default=240.0)
    parser.add_argument("--dry-run", action="store_true", help="Stage harnesses and configs without starting MWORKS.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.simulation_timeout_s <= 0:
        raise ValueError("--simulation-timeout-s must be positive")
    profile_path = args.profile_path.resolve()
    contract_path = args.contract_path.resolve()
    result_root = args.result_root.resolve()
    profiles, profile_hash, profile_document = read_profiles(profile_path)
    contract_hash, _ = read_contract(contract_path)
    cases = select_cases(profiles, args.scenario, result_root)
    for case in cases:
        stage_case(
            case,
            profile_path=profile_path,
            profile_hash=profile_hash,
            contract_path=contract_path,
            contract_hash=contract_hash,
            profile_document=profile_document,
        )

    executions: dict[str, dict[str, Any]] = {}
    client = None
    if not args.dry_run:
        runner = load_runner_module()
        wrapper = runner.resolve_wrapper(None)
        client = runner.JsonlMcpClient(runner.wrapper_command(wrapper), result_root / "batch_session_mcp.jsonl")
        runner.initialize_mcp_client(client)
        try:
            for index, case in enumerate(cases, start=1):
                print(f"[{index}/{len(cases)}] official_pid_native_sysblock/{case.scenario_id}", flush=True)
                executions[case.scenario_id] = execute_case(case, runner, client, timeout_s=args.simulation_timeout_s)
        finally:
            # Deliberately retain the MWORKS/Sysplorer session; only the helper client exits.
            client.close()

    records = [write_record(case, executions.get(case.scenario_id), dry_run=args.dry_run) for case in cases]
    matrix = write_matrix(
        records,
        result_root=result_root,
        profile_path=profile_path,
        profile_hash=profile_hash,
        contract_path=contract_path,
        contract_hash=contract_hash,
        dry_run=args.dry_run,
    )
    invalid_count = sum(record["status"] == "invalid" for record in records)
    print(f"Matrix: {matrix}")
    print(f"Cases: {len(records)}, invalid: {invalid_count}")
    return 0 if args.dry_run or invalid_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
