#!/usr/bin/env python3
"""Freeze a single-UAV Model Studio task without starting MWORKS.

The resulting JSON describes one existing FormalRunner plus a temporary
Modelica harness. The harness adds no controller logic. It is an input for the
manual MWORKS opening path only; this script never starts a solver, opens a
Sysplorer session, or records simulation evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_v2.json"
CONTRACT_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract_v2.json"
DRIVER_PATH = ROOT / "Scripts" / "mworks" / "run_seven_scenario_ab.py"
DEFAULT_OUTPUT = ROOT / "Results" / "ui_platform" / "model_studio_task_handoffs" / "latest.json"
TASK_CONFIG_SCHEMA = "mosim.model_studio.task_config.v1"
TASK_ORDER = (
    "climb_path_50s",
    "hover",
    "step_response",
    "figure8",
    "spiral",
    "wind_disturbance",
    "parameter_mismatch",
    "motor_efficiency_fault",
)
FORMAL_CONTROLLER_IDS = frozenset({"official_pid", "px4ctrl"})
EPSILON = 1e-9

BASELINE_PROFILE: dict[str, Any] = {
    "profile_id": "model_studio_climb_path_50s_v1",
    "scenario_id": "climb_path_50s",
    "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
    "duration_s": 50.0,
    "trajectory_parameter_overrides": {},
    "runner_parameter_overrides": {
        "gust_force": [0.0, 0.0, 0.0],
        "gust_start_s": 0.0,
        "gust_duration_s": 0.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 1_000_000_000.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 1.0,
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def project_path_text(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def load_driver() -> Any:
    spec = importlib.util.spec_from_file_location("model_studio_seven_scenario_driver", DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"driver_load_failed: {DRIVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_motor_effectiveness(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",")]
    except ValueError as exc:
        raise ValueError("motor_effectiveness_must_be_four_comma_separated_numbers") from exc
    if len(values) != 4:
        raise ValueError("motor_effectiveness_must_have_four_values")
    if any(not math.isfinite(item) or item < 0.0 or item > 1.0 for item in values):
        raise ValueError("motor_effectiveness_must_be_within_0_and_1")
    return values


def finite_value(name: str, value: float, lower: float, upper: float) -> float:
    if not math.isfinite(value) or value < lower or value > upper:
        raise ValueError(f"{name}_must_be_within_{lower:g}_and_{upper:g}")
    return value


def is_nominal(values: list[float]) -> bool:
    return all(abs(value - 1.0) <= EPSILON for value in values)


def selected_profile(driver: Any, task_id: str) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    profiles, profile_hash = driver.read_profiles(PROFILE_PATH)
    contract, contract_hash = driver.read_contract(CONTRACT_PATH)
    driver.validate_profile_contract_alignment(profiles, contract)
    if task_id == "climb_path_50s":
        return copy.deepcopy(BASELINE_PROFILE), profiles, profile_hash, contract_hash
    profile = next(
        (row for row in profiles["profiles"] if row.get("scenario_id") == task_id),
        None,
    )
    if profile is None:
        raise ValueError(f"unknown_task_id: {task_id}")
    return copy.deepcopy(profile), profiles, profile_hash, contract_hash


def apply_task_parameters(
    profile: dict[str, Any],
    task_id: str,
    gust_force_x_n: float,
    mass_inertia_scale: float,
    motor_effectiveness: list[float],
) -> None:
    gust_force_x_n = finite_value("gust_force_x_n", gust_force_x_n, 0.0, 0.5)
    mass_inertia_scale = finite_value("mass_inertia_scale", mass_inertia_scale, 1.0, 1.4)
    runner = profile["runner_parameter_overrides"]

    if task_id == "wind_disturbance":
        if abs(mass_inertia_scale - 1.0) > EPSILON or not is_nominal(motor_effectiveness):
            raise ValueError("wind_task_only_accepts_external_force_parameter")
        runner["gust_force"] = [gust_force_x_n, 0.0, 0.0]
        return

    if task_id == "parameter_mismatch":
        if abs(gust_force_x_n) > EPSILON or not is_nominal(motor_effectiveness):
            raise ValueError("parameter_mismatch_only_accepts_mass_inertia_scale")
        runner["mass_scale"] = mass_inertia_scale
        runner["inertia_scale"] = [mass_inertia_scale, mass_inertia_scale, mass_inertia_scale]
        return

    if task_id == "motor_efficiency_fault":
        if abs(gust_force_x_n) > EPSILON or abs(mass_inertia_scale - 1.0) > EPSILON:
            raise ValueError("motor_fault_only_accepts_one_motor_effectiveness")
        impaired = [index for index, value in enumerate(motor_effectiveness, start=1) if value < 1.0 - EPSILON]
        if len(impaired) != 1:
            raise ValueError("motor_fault_requires_exactly_one_impaired_motor")
        index = impaired[0]
        runner["rotor_effectiveness"] = [1.0, 1.0, 1.0, 1.0]
        runner["fault_rotor_index"] = index
        runner["fault_rotor_effectiveness"] = motor_effectiveness[index - 1]
        return

    if abs(gust_force_x_n) > EPSILON or abs(mass_inertia_scale - 1.0) > EPSILON or not is_nominal(motor_effectiveness):
        raise ValueError("nominal_task_does_not_accept_injection_parameters")


def model_name(driver: Any, controller_id: str, task_id: str, profile: dict[str, Any]) -> str:
    controller = driver.CONTROLLERS[controller_id]
    identity = {
        "controller_id": controller_id,
        "runner_class": controller["runner_class"],
        "task_id": task_id,
        "profile": profile,
    }
    token = sha256_bytes(
        json.dumps(identity, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )[:12]
    return f"ModelStudio_{controller['model_slug']}_{driver.camel_case(task_id)}_{token}"


def rendered_harness(driver: Any, controller_id: str, task_id: str, profile: dict[str, Any], name: str) -> str:
    case = driver.Case(
        controller_id=controller_id,
        scenario_id=task_id,
        profile=profile,
        result_root=DEFAULT_OUTPUT.parent,
    )
    source_name = case.model_name
    rendered = driver.render_harness(case)
    rendered = rendered.replace(f"model {source_name}", f"model {name}", 1)
    rendered = rendered.replace(f"end {source_name};", f"end {name};", 1)
    return rendered


def configuration_kind(task_id: str, profile: dict[str, Any], source_profile: dict[str, Any]) -> str:
    if task_id == "climb_path_50s":
        return "climb_path_baseline"
    return "formal_v2_profile" if profile == source_profile else "task_parameter_variant"


def write_task_config(
    *,
    task_id: str,
    controller_id: str,
    gust_force_x_n: float,
    mass_inertia_scale: float,
    motor_effectiveness: list[float],
    output: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    if task_id not in TASK_ORDER:
        raise ValueError(f"unknown_task_id: {task_id}")
    if controller_id not in FORMAL_CONTROLLER_IDS:
        raise ValueError("formal_task_controller_must_be_official_pid_or_px4ctrl")

    driver = load_driver()
    profile, profiles_document, profile_hash, contract_hash = selected_profile(driver, task_id)
    source_profile = copy.deepcopy(profile)
    apply_task_parameters(
        profile,
        task_id,
        gust_force_x_n,
        mass_inertia_scale,
        motor_effectiveness,
    )

    resolved_output = output.resolve()
    name = model_name(driver, controller_id, task_id, profile)
    harness_path = resolved_output.parent / "harness" / name / f"{name}.mo"
    harness_text = rendered_harness(driver, controller_id, task_id, profile, name)
    harness_path.parent.mkdir(parents=True, exist_ok=True)
    harness_path.write_text(harness_text, encoding="utf-8", newline="\n")

    payload = {
        "schema": TASK_CONFIG_SCHEMA,
        "created_at": utc_now(),
        "controller_id": controller_id,
        "runner_class": driver.CONTROLLERS[controller_id]["runner_class"],
        "task_id": task_id,
        "configuration_kind": configuration_kind(task_id, profile, source_profile),
        "model_name": name,
        "harness_file": project_path_text(harness_path),
        "harness_sha256": sha256_path(harness_path),
        "profile": profile,
        "task_parameters": {
            "gust_force_x_n": gust_force_x_n,
            "mass_inertia_scale": mass_inertia_scale,
            "motor_effectiveness": motor_effectiveness,
        },
        "profile_source": project_path_text(PROFILE_PATH),
        "profile_source_sha256": profile_hash,
        "contract_source": project_path_text(CONTRACT_PATH),
        "contract_source_sha256": contract_hash,
        "claim_boundary": "Frozen configuration and generated harness only; no MWORKS simulation has been started.",
    }
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", choices=TASK_ORDER, required=True)
    parser.add_argument("--controller-id", choices=sorted(FORMAL_CONTROLLER_IDS), required=True)
    parser.add_argument("--gust-force-x-n", type=float, default=0.0)
    parser.add_argument("--mass-inertia-scale", type=float, default=1.0)
    parser.add_argument("--motor-effectiveness", default="1,1,1,1")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = args.output if args.output.is_absolute() else ROOT / args.output
    payload = write_task_config(
        task_id=args.task_id,
        controller_id=args.controller_id,
        gust_force_x_n=args.gust_force_x_n,
        mass_inertia_scale=args.mass_inertia_scale,
        motor_effectiveness=parse_motor_effectiveness(args.motor_effectiveness),
        output=output,
    )
    print(json.dumps({
        "task_id": payload["task_id"],
        "controller_id": payload["controller_id"],
        "configuration_kind": payload["configuration_kind"],
        "harness_file": payload["harness_file"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
