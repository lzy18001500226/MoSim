#!/usr/bin/env python3
"""Statically verify the frozen seven-scenario MWORKS preflight contract.

This checker deliberately performs no MWORKS call and starts no simulation. It
proves only that the source/configuration contract is internally coherent
before native ``CheckModel`` and formal A/B execution are attempted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
CONTRACT_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract.json"
PROFILES_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles.json"
DEFAULT_OUTPUT = ROOT / "Results" / "control_platform" / "seven_scenario_preflight_20260727" / "STATIC_PREFLIGHT_VALIDATION.json"

SCENARIO_IDS = (
    "hover",
    "step_response",
    "figure8",
    "spiral",
    "wind_disturbance",
    "parameter_mismatch",
    "motor_efficiency_fault",
)
INJECTION_PARAMETERS = (
    "gust_force",
    "gust_start_s",
    "gust_duration_s",
    "mass_scale",
    "inertia_scale",
    "rotor_effectiveness",
    "fault_start_s",
    "fault_rotor_index",
    "fault_rotor_effectiveness",
)
SHARED_RUNNERS = (
    "AttitudeThrustRunner.mo",
    "BodyRateThrustRunner.mo",
    "RotorCommandRunner.mo",
    "WrenchRunner.mo",
)
FORMAL_RUNNERS_DIR = MODEL_ROOT / "Experiment" / "Runners" / "Formal"
FORMAL_RUNNER_BASES_DIR = MODEL_ROOT / "Experiment" / "Runners" / "Base"
FORMAL_RUNNER_BASES = (
    "FormalAttitudeThrustRunnerBase",
    "FormalBodyRateThrustRunnerBase",
    "FormalRotorCommandRunnerBase",
    "FormalWrenchRunnerBase",
)
FORMAL_RUNNERS = {
    "official_pid": "OfficialPidFormalRunner.mo",
    "cascade_pid": "CascadePidFormalRunner.mo",
    "lqr_baseline": "LqrBaselineFormalRunner.mo",
    "super_twisting_smc": "SuperTwistingSmcFormalRunner.mo",
    "linear_mpc": "LinearMpcFormalRunner.mo",
    "dfbc_high_order_attitude": "DfbcHighOrderFormalRunner.mo",
    "trained_neural_residual": "TrainedNeuralResidualFormalRunner.mo",
    "px4ctrl": "Px4CtrlFormalRunner.mo",
}
CHAMPION_ADAPTERS = {
    "cascade_pid": "CascadePidAttitudeThrustAdapter.mo",
    "lqr_baseline": "LqrBaselineAttitudeThrustAdapter.mo",
    "super_twisting_smc": "SuperTwistingSmcAttitudeThrustAdapter.mo",
    "linear_mpc": "LinearMpcAttitudeThrustAdapter.mo",
    "dfbc_high_order_attitude": "DfbcHighOrderAttitudeThrustAdapter.mo",
    "trained_neural_residual": "TrainedNeuralResidualAttitudeThrustAdapter.mo",
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {path}")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def formal_runner_source(runner_name: str) -> str:
    """Return a formal runner together with its shared Base when it inherits one."""
    text = source(FORMAL_RUNNERS_DIR / runner_name)
    for base_name in FORMAL_RUNNER_BASES:
        reference = f"extends MoSimQuadrotorModel.Experiment.Runners.Base.{base_name}("
        if reference in text:
            return f"{text}\n{source(FORMAL_RUNNER_BASES_DIR / f'{base_name}.mo')}"
    return text


def formal_runner_classes() -> list[str]:
    """Return the complete formal-runner allowlist in browser/package order."""
    names = [
        line.strip()
        for line in (FORMAL_RUNNERS_DIR / "package.order").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [f"MoSimQuadrotorModel.Experiment.Runners.Formal.{name}" for name in names]


def check_contains(checks: list[dict[str, Any]], name: str, text: str, *needles: str) -> None:
    missing = [needle for needle in needles if needle not in text]
    checks.append(
        {
            "name": name,
            "ok": not missing,
            "missing": missing,
        }
    )


def check_equal(checks: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    checks.append(
        {
            "name": name,
            "ok": actual == expected,
            "actual": actual,
            "expected": expected,
        }
    )


def preflight_paths() -> tuple[Path, ...]:
    runners = MODEL_ROOT / "Experiment" / "Runners"
    adapters = MODEL_ROOT / "Control" / "Adapters"
    trajectories = MODEL_ROOT / "Guidance" / "Trajectories"
    paths = [
        CONTRACT_PATH,
        PROFILES_PATH,
        MODEL_ROOT / "Vehicle" / "Sunray150Assembly.mo",
        MODEL_ROOT / "Vehicle" / "Dynamics" / "PhysicalWrenchAdapter.mo",
        MODEL_ROOT / "Vehicle" / "Dynamics" / "RotorActuatorCore.mo",
        MODEL_ROOT / "Parameters" / "package.mo",
        trajectories / "package.mo",
        ROOT / "Scripts" / "results" / "calc_metrics.py",
        ROOT / "Scripts" / "results" / "calc_metrics.jl",
        ROOT / "Scripts" / "syslab" / "compare_controllers.jl",
    ]
    paths.extend(runners / name for name in SHARED_RUNNERS)
    paths.extend(FORMAL_RUNNERS_DIR / name for name in FORMAL_RUNNERS.values())
    paths.append(FORMAL_RUNNERS_DIR / "package.order")
    paths.extend(adapters / name for name in CHAMPION_ADAPTERS.values())
    paths.append(adapters / "OfficialPIDRotorAdapter.mo")
    paths.extend(
        trajectories / name
        for name in (
            "HoverHold.mo",
            "StepResponse.mo",
            "Figure8.mo",
            "SpiralAscent.mo",
            "WindDisturbance.mo",
            "ParameterMismatch.mo",
            "MotorFault.mo",
        )
    )
    return tuple(paths)


def validate_preflight() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    contract = read_json(CONTRACT_PATH)
    profiles = read_json(PROFILES_PATH)

    check_equal(checks, "contract_schema", contract.get("schema"), "mosim.seven_scenario_injection_contract.v1")
    common = contract.get("common_execution", {})
    check_equal(checks, "common_result_interval_s", common.get("result_interval_s"), 0.01)
    check_equal(
        checks,
        "common_execution_semantics_manifest_fields",
        common.get("sampling_fairness", {}).get("required_manifest_fields", [])[3:],
        [
            "controller_execution_semantics",
            "reference_path_semantics",
            "measurement_path_semantics",
            "command_path_semantics",
        ],
    )
    scenarios = {item.get("scenario_id"): item for item in contract.get("scenarios", []) if isinstance(item, dict)}
    check_equal(checks, "contract_scenario_order", list(scenarios), list(SCENARIO_IDS))
    wind = scenarios.get("wind_disturbance", {}).get("plant_injection", {})
    mismatch = scenarios.get("parameter_mismatch", {}).get("plant_injection", {})
    fault = scenarios.get("motor_efficiency_fault", {}).get("plant_injection", {})
    check_equal(checks, "wind_force_n", wind.get("gust_force_N"), [0.25, 0.0, 0.0])
    check_equal(checks, "wind_window", [wind.get("start_s"), wind.get("duration_s")], [0.0, 50.0])
    check_equal(checks, "mismatch_plant_only_scale", [mismatch.get("mass_scale"), mismatch.get("inertia_scale"), mismatch.get("controller_parameter_scale")], [1.2, [1.2, 1.2, 1.2], 1.0])
    check_equal(checks, "motor_fault_contract", [fault.get("fault_rotor_index"), fault.get("fault_effectiveness"), fault.get("fault_start_s")], [1, 0.5, 15.0])

    profile_rows = profiles.get("profiles", [])
    profile_by_id = {item.get("scenario_id"): item for item in profile_rows if isinstance(item, dict)}
    check_equal(checks, "profile_scenario_order", list(profile_by_id), list(SCENARIO_IDS))
    check_equal(checks, "profile_common_interval_s", profiles.get("common_execution", {}).get("result_interval_s"), 0.01)
    check_equal(
        checks,
        "profile_controller_execution_semantics",
        profiles.get("common_execution", {}).get("controller_execution_semantics"),
        "Each FormalRunner declares its own controller boundary; result_interval_s is an output and metric sampling cadence only.",
    )
    allowed = profiles.get("formal_runner_binding", {}).get("allowed_runner_classes", [])
    expected_runners = formal_runner_classes()
    check_equal(checks, "profile_allowed_formal_runners", allowed, expected_runners)
    for scenario_id in SCENARIO_IDS:
        profile = profile_by_id.get(scenario_id, {})
        overrides = profile.get("runner_parameter_overrides", {})
        check_equal(checks, f"{scenario_id}_runner_override_keys", list(overrides), list(INJECTION_PARAMETERS))
    check_equal(checks, "wind_profile_force", profile_by_id.get("wind_disturbance", {}).get("runner_parameter_overrides", {}).get("gust_force"), [0.25, 0.0, 0.0])
    check_equal(checks, "mismatch_profile_mass_scale", profile_by_id.get("parameter_mismatch", {}).get("runner_parameter_overrides", {}).get("mass_scale"), 1.2)
    motor_profile = profile_by_id.get("motor_efficiency_fault", {}).get("runner_parameter_overrides", {})
    check_equal(checks, "motor_profile_schedule", [motor_profile.get("fault_start_s"), motor_profile.get("fault_rotor_index"), motor_profile.get("fault_rotor_effectiveness")], [15.0, 1, 0.5])

    runners_dir = MODEL_ROOT / "Experiment" / "Runners"
    for runner_name in SHARED_RUNNERS:
        text = source(runners_dir / runner_name)
        check_contains(
            checks,
            f"shared_runner_injection_{runner_name}",
            text,
            *INJECTION_PARAMETERS,
            "MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(",
            "fault_rotor_effectiveness = fault_rotor_effectiveness",
        )
    for scheme_id, runner_name in FORMAL_RUNNERS.items():
        if scheme_id == "official_pid":
            continue
        text = formal_runner_source(runner_name)
        check_contains(
            checks,
            f"formal_runner_injection_{scheme_id}",
            text,
            *INJECTION_PARAMETERS,
            "MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(",
            "Interval = 0.01",
            "replaceable model Trajectory",
            "sampled_position_ref",
            "sampled_velocity_ref",
            "sampled_acceleration_ref",
            "sampled_position",
            "sampled_attitude",
        )
    official_text = (
        formal_runner_source(FORMAL_RUNNERS["official_pid"])
        + "\n"
        + source(runners_dir / "RotorCommandRunner.mo")
    )
    check_contains(
        checks,
        "official_pid_native_continuous_baseline",
        official_text,
        "extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(",
        "MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter",
        "Interval = 0.01",
    )
    official_boundary = profiles.get("formal_runner_binding", {}).get("official_pid_boundary", {})
    check_equal(
        checks,
        "official_pid_native_continuous_boundary_contract",
        [
            official_boundary.get("execution_mode"),
            official_boundary.get("reference_path"),
            official_boundary.get("measurement_path"),
            official_boundary.get("command_path"),
            official_boundary.get("result_interval_s"),
        ],
        ["native_continuous_closed_loop", "direct", "direct", "direct", 0.01],
    )

    assembly_text = source(MODEL_ROOT / "Vehicle" / "Sunray150Assembly.mo")
    check_contains(
        checks,
        "sunray150_plant_injection",
        assembly_text,
        "Modelica.Mechanics.MultiBody.Forces.WorldForce gust",
        "gust.force[1] = if time >= gust_start_s",
        "mass_scale = mass_scale",
        "inertia_scale = inertia_scale",
        "fault_start_s = fault_start_s",
        "fault_rotor_effectiveness = fault_rotor_effectiveness",
    )
    physical_text = source(MODEL_ROOT / "Vehicle" / "Dynamics" / "PhysicalWrenchAdapter.mo")
    check_contains(
        checks,
        "physical_mass_and_inertia_mismatch",
        physical_text,
        "mass_kg = profile.takeoff_mass_kg * mass_scale",
        "I_11 = profile.body_inertia_diagonal_kg_m2[1] * inertia_scale[1]",
        "I_22 = profile.body_inertia_diagonal_kg_m2[2] * inertia_scale[2]",
        "I_33 = profile.body_inertia_diagonal_kg_m2[3] * inertia_scale[3]",
    )
    rotor_text = source(MODEL_ROOT / "Vehicle" / "Dynamics" / "RotorActuatorCore.mo")
    check_contains(
        checks,
        "rotor_fault_schedule",
        rotor_text,
        "time >= fault_start_s",
        "fault_effectiveness[i]",
        "thrust[i] = fault_effectiveness[i]",
        "reaction_moment_effectiveness[i]",
    )

    trajectory_root = MODEL_ROOT / "Guidance" / "Trajectories"
    climb_source = source(trajectory_root / "package.mo")
    check_contains(
        checks,
        "climb_path_reference_ports",
        climb_source,
        "model ClimbPath",
        "position_command[3]",
        "velocity_command[3]",
        "acceleration_command[3]",
    )
    for trajectory_name in ("HoverHold", "StepResponse", "Figure8", "SpiralAscent"):
        text = source(trajectory_root / f"{trajectory_name}.mo")
        check_contains(
            checks,
            f"trajectory_ports_{trajectory_name}",
            text,
            "position_command[3]",
            "velocity_command[3]",
            "acceleration_command[3]",
        )
    for trajectory_name in ("WindDisturbance", "ParameterMismatch", "MotorFault"):
        text = source(trajectory_root / f"{trajectory_name}.mo")
        check_contains(
            checks,
            f"trajectory_inherits_ports_{trajectory_name}",
            text,
            "extends MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
        )
    step_text = source(trajectory_root / "StepResponse.mo")
    check_contains(
        checks,
        "step_response_definition",
        step_text,
        "step_time_s(unit = \"s\") = 15",
        "x_step_m(unit = \"m\") = 1",
        "y_step_m(unit = \"m\") = -1",
    )

    adapters_dir = MODEL_ROOT / "Control" / "Adapters"
    for scheme_id, adapter_name in CHAMPION_ADAPTERS.items():
        text = source(adapters_dir / adapter_name)
        check_contains(
            checks,
            f"adapter_feedforward_{scheme_id}",
            text,
            "velocity_mea[1]",
            "velocity_mea[2]",
            "velocity_mea[3]",
            "velocity_ref[1]",
            "velocity_ref[2]",
            "velocity_ref[3]",
            "acceleration_ref[1]",
            "acceleration_ref[2]",
            "acceleration_ref[3]",
        )
    provenance_text = source(MODEL_ROOT / "Parameters" / "package.mo")
    check_contains(
        checks,
        "official_pid_provenance",
        provenance_text,
        "official_pid_source_anchor",
        "official_pid_case_reference",
        "official_pid_provenance_boundary",
        "no velocity or acceleration feedforward port",
    )
    metrics_python = source(ROOT / "Scripts" / "results" / "calc_metrics.py")
    metrics_julia = source(ROOT / "Scripts" / "results" / "calc_metrics.jl")
    comparison_julia = source(ROOT / "Scripts" / "syslab" / "compare_controllers.jl")
    for label, text in (("python", metrics_python), ("julia", metrics_julia)):
        check_contains(
            checks,
            f"{label}_scenario_metrics",
            text,
            "overshoot_percent_x",
            "overshoot_percent_y",
            "persistent_step_settling_time",
            "disturbance_window_rmse_m",
            "pre_fault_rmse_m",
            "post_fault_rmse_m",
            "post_fault_peak_error_m",
        )
    check_contains(
        checks,
        "syslab_comparison_script",
        comparison_julia,
        "ClimbPath Position RMSE Comparison",
        "Step Response Overlay (XY)",
        "--self-test",
        "compute_metrics",
    )

    missing_paths = [str(path.relative_to(ROOT)) for path in preflight_paths() if not path.is_file()]
    checks.append({"name": "required_preflight_paths_exist", "ok": not missing_paths, "missing": missing_paths})
    errors = [check["name"] for check in checks if not check["ok"]]
    source_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
        for path in preflight_paths()
        if path.is_file()
    }
    return {
        "schema": "mosim.seven_scenario_preflight_static_validation.v1",
        "status": "passed" if not errors else "failed",
        "live_mworks_touched": False,
        "scenario_simulation_started": False,
        "claim_boundary": "Static source and configuration validation only. It is not CheckModel or simulation evidence.",
        "error_count": len(errors),
        "errors": errors,
        "checks": checks,
        "source_sha256": source_hashes,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write deterministic static evidence")
    parser.add_argument("--check", action="store_true", help="require the existing evidence to match the current source")
    args = parser.parse_args(argv)
    payload = validate_preflight()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if args.write:
        write_json(output, payload)
    if args.check:
        if not output.is_file():
            payload["status"] = "failed"
            payload["errors"].append(f"missing static evidence: {output}")
            payload["error_count"] = len(payload["errors"])
        else:
            existing = read_json(output)
            if existing != payload:
                payload["status"] = "failed"
                payload["errors"].append("static evidence does not match current source/configuration")
                payload["error_count"] = len(payload["errors"])
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
