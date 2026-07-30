#!/usr/bin/env python3
"""Freeze one Model Studio task without starting MWORKS.

The resulting JSON describes an existing single- or three-UAV MWORKS model
plus a temporary Modelica harness. The harness adds no controller logic. It is
an input for the manual MWORKS opening path only; this script never starts a
solver, opens a Sysplorer session, or records simulation evidence.
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
FORMAL_TASK_IDS = (
    "climb_path_50s",
    "hover",
    "step_response",
    "figure8",
    "spiral",
)
LEGACY_INJECTION_TASK_IDS = (
    "wind_disturbance",
    "parameter_mismatch",
    "motor_efficiency_fault",
)
SPECIAL_TASK_IDS = (
    "single_uav_autonomous_avoidance",
    "three_uav_figure8",
    "three_uav_autonomous_avoidance",
)
TASK_ORDER = FORMAL_TASK_IDS + LEGACY_INJECTION_TASK_IDS + SPECIAL_TASK_IDS
FORMAL_CONTROLLER_IDS = frozenset({"official_pid", "px4ctrl"})
MAP_IDS = frozenset({"blank", "openblocks"})
EPSILON = 1e-9
DEFAULT_INJECTION_START_S = 15.0

SPECIAL_ROUTES: dict[str, dict[str, Any]] = {
    "single_uav_autonomous_avoidance": {
        "vehicle_count": 1,
        "map_id": "openblocks",
        "controller_ids": frozenset({"px4ctrl"}),
        "base_model": "MoSimQuadrotorModel.Guidance.Planning.OpenBlocksPx4Ctrl",
        "duration_s": 80.1247340259,
        "injection_supported": True,
        "configuration_kind": "single_uav_planning_route",
    },
    "three_uav_figure8": {
        "vehicle_count": 3,
        "map_id": "blank",
        "controller_ids": frozenset({"px4ctrl"}),
        "base_model": "MoSimQuadrotorModel.Experiment.Runners.Formation.Px4CtrlThreeUavFigure8Runner",
        "duration_s": 50.0,
        "injection_supported": True,
        "configuration_kind": "three_uav_formation_route",
    },
    "three_uav_autonomous_avoidance": {
        "vehicle_count": 3,
        "map_id": "openblocks",
        "controller_ids": frozenset({"linear_mpc"}),
        "base_model": "MoSimQuadrotorModel.Guidance.Planning.OpenBlocksThreeUavFormation",
        "duration_s": 360.0,
        "injection_supported": False,
        "configuration_kind": "three_uav_planning_route",
    },
}

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


def injection_is_nominal(
    gust_force_x_n: float,
    mass_inertia_scale: float,
    motor_effectiveness: list[float],
) -> bool:
    return (
        abs(gust_force_x_n) <= EPSILON
        and abs(mass_inertia_scale - 1.0) <= EPSILON
        and is_nominal(motor_effectiveness)
    )


def selected_profile(driver: Any, task_id: str) -> tuple[dict[str, Any], str, str]:
    profiles, profile_hash = driver.read_profiles(PROFILE_PATH)
    contract, contract_hash = driver.read_contract(CONTRACT_PATH)
    driver.validate_profile_contract_alignment(profiles, contract)
    if task_id == "climb_path_50s":
        return copy.deepcopy(BASELINE_PROFILE), profile_hash, contract_hash
    profile = next(
        (row for row in profiles["profiles"] if row.get("scenario_id") == task_id),
        None,
    )
    if profile is None:
        raise ValueError(f"unknown_formal_task_id: {task_id}")
    return copy.deepcopy(profile), profile_hash, contract_hash


def validate_selection(
    task_id: str,
    controller_id: str,
    vehicle_count: int,
    map_id: str,
    fault_target_uav: int,
) -> dict[str, Any] | None:
    if not 1 <= vehicle_count <= 9:
        raise ValueError("vehicle_count_must_be_within_1_and_9")
    if map_id not in MAP_IDS:
        raise ValueError("unknown_map_id")
    if not 1 <= fault_target_uav <= vehicle_count:
        raise ValueError("fault_target_uav_must_be_within_vehicle_count")

    if task_id in FORMAL_TASK_IDS or task_id in LEGACY_INJECTION_TASK_IDS:
        if vehicle_count != 1:
            raise ValueError("formal_task_requires_single_uav")
        if map_id != "blank":
            raise ValueError("formal_task_requires_blank_map")
        if controller_id not in FORMAL_CONTROLLER_IDS:
            raise ValueError("formal_task_controller_must_be_official_pid_or_px4ctrl")
        return None

    route = SPECIAL_ROUTES.get(task_id)
    if route is None:
        raise ValueError(f"unknown_task_id: {task_id}")
    if vehicle_count != route["vehicle_count"]:
        raise ValueError("task_vehicle_count_not_supported")
    if map_id != route["map_id"]:
        raise ValueError("task_map_not_supported")
    if controller_id not in route["controller_ids"]:
        raise ValueError("task_controller_not_supported")
    return route


def normalized_injection(
    *,
    gust_force_x_n: float,
    mass_inertia_scale: float,
    motor_effectiveness: list[float],
    fault_start_s: float,
    duration_s: float,
) -> dict[str, Any]:
    gust_force_x_n = finite_value("gust_force_x_n", gust_force_x_n, 0.0, 0.5)
    mass_inertia_scale = finite_value("mass_inertia_scale", mass_inertia_scale, 1.0, 1.4)
    fault_start_s = finite_value("fault_start_s", fault_start_s, 0.0, duration_s)
    impaired = [index for index, value in enumerate(motor_effectiveness, start=1) if value < 1.0 - EPSILON]
    if len(impaired) > 1:
        raise ValueError("motor_fault_requires_exactly_one_impaired_motor")
    rotor_index = impaired[0] if impaired else 1
    rotor_effectiveness = motor_effectiveness[rotor_index - 1] if impaired else 1.0
    return {
        "gust_force_x_n": gust_force_x_n,
        "mass_inertia_scale": mass_inertia_scale,
        "motor_effectiveness": motor_effectiveness,
        "fault_start_s": fault_start_s,
        "fault_rotor_index": rotor_index,
        "fault_rotor_effectiveness": rotor_effectiveness,
    }


def apply_independent_parameters(profile: dict[str, Any], injection: dict[str, Any]) -> None:
    runner = profile["runner_parameter_overrides"]
    gust_force_x_n = float(injection["gust_force_x_n"])
    fault_start_s = float(injection["fault_start_s"])
    duration_s = float(profile["duration_s"])
    runner["gust_force"] = [gust_force_x_n, 0.0, 0.0]
    runner["gust_start_s"] = fault_start_s if gust_force_x_n > EPSILON else 0.0
    runner["gust_duration_s"] = max(0.0, duration_s - fault_start_s) if gust_force_x_n > EPSILON else 0.0
    mass_inertia_scale = float(injection["mass_inertia_scale"])
    runner["mass_scale"] = mass_inertia_scale
    runner["inertia_scale"] = [mass_inertia_scale, mass_inertia_scale, mass_inertia_scale]
    runner["rotor_effectiveness"] = [1.0, 1.0, 1.0, 1.0]
    runner["fault_start_s"] = fault_start_s if float(injection["fault_rotor_effectiveness"]) < 1.0 - EPSILON else 1_000_000_000.0
    runner["fault_rotor_index"] = int(injection["fault_rotor_index"])
    runner["fault_rotor_effectiveness"] = float(injection["fault_rotor_effectiveness"])


def model_name(
    driver: Any,
    controller_id: str,
    task_id: str,
    selection: dict[str, Any],
    profile: dict[str, Any] | None,
    route: dict[str, Any] | None,
) -> str:
    controller = driver.CONTROLLERS.get(controller_id, {"model_slug": driver.camel_case(controller_id)})
    route_identity = None if route is None else {
        key: sorted(value) if isinstance(value, frozenset) else value
        for key, value in route.items()
    }
    identity = {
        "controller_id": controller_id,
        "task_id": task_id,
        "selection": selection,
        "profile": profile,
        "route": route_identity,
    }
    token = sha256_bytes(
        json.dumps(identity, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )[:12]
    return f"ModelStudio_{controller['model_slug']}_{driver.camel_case(task_id)}_{token}"


def rendered_formal_harness(driver: Any, controller_id: str, task_id: str, profile: dict[str, Any], name: str) -> str:
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


def injection_modifications(
    driver: Any,
    injection: dict[str, Any],
    duration_s: float,
) -> list[str]:
    gust_force_x_n = float(injection["gust_force_x_n"])
    mass_inertia_scale = float(injection["mass_inertia_scale"])
    fault_start_s = float(injection["fault_start_s"])
    gust_duration_s = max(0.0, duration_s - fault_start_s) if gust_force_x_n > EPSILON else 0.0
    return [
        f"gust_force = {driver.modelica_value([gust_force_x_n, 0.0, 0.0])}",
        f"gust_start_s = {driver.modelica_value(fault_start_s if gust_force_x_n > EPSILON else 0.0)}",
        f"gust_duration_s = {driver.modelica_value(gust_duration_s)}",
        f"mass_scale = {driver.modelica_value(mass_inertia_scale)}",
        f"inertia_scale = {driver.modelica_value([mass_inertia_scale, mass_inertia_scale, mass_inertia_scale])}",
        "rotor_effectiveness = {1, 1, 1, 1}",
        f"fault_start_s = {driver.modelica_value(float(injection['fault_start_s']) if float(injection['fault_rotor_effectiveness']) < 1.0 - EPSILON else 1_000_000_000.0)}",
        f"fault_rotor_index = {driver.modelica_value(int(injection['fault_rotor_index']))}",
        f"fault_rotor_effectiveness = {driver.modelica_value(float(injection['fault_rotor_effectiveness']))}",
    ]


def rendered_special_harness(
    driver: Any,
    *,
    task_id: str,
    route: dict[str, Any],
    injection: dict[str, Any],
    fault_target_uav: int,
    name: str,
) -> str:
    base_model = str(route["base_model"])
    if not route["injection_supported"]:
        return f'''within ;
model {name}
  "Frozen Model Studio route for {task_id}"
  extends {base_model};
end {name};
'''

    modifications = injection_modifications(driver, injection, float(route["duration_s"]))
    if task_id == "three_uav_figure8":
        modifier_text = ",\n      ".join(modifications)
        extends_text = f"{base_model}(\n    plant_{fault_target_uav}(\n      {modifier_text}))"
    else:
        modifier_text = ",\n    ".join(modifications)
        extends_text = f"{base_model}(\n    {modifier_text})"
    return f'''within ;
model {name}
  "Frozen Model Studio route for {task_id}"
  extends {extends_text};
end {name};
'''


def configuration_kind(task_id: str, profile: dict[str, Any], source_profile: dict[str, Any]) -> str:
    if task_id == "climb_path_50s" and profile == source_profile:
        return "climb_path_baseline"
    return "formal_v2_profile" if profile == source_profile else "task_parameter_variant"


def write_task_config(
    *,
    task_id: str,
    controller_id: str,
    gust_force_x_n: float,
    mass_inertia_scale: float,
    motor_effectiveness: list[float],
    vehicle_count: int = 1,
    map_id: str = "blank",
    fault_target_uav: int = 1,
    fault_start_s: float = DEFAULT_INJECTION_START_S,
    output: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    if task_id not in TASK_ORDER:
        raise ValueError(f"unknown_task_id: {task_id}")

    route = validate_selection(task_id, controller_id, vehicle_count, map_id, fault_target_uav)
    driver = load_driver()
    profile: dict[str, Any] | None = None
    source_profile: dict[str, Any] | None = None
    profile_hash: str | None = None
    contract_hash: str | None = None
    duration_s = float(route["duration_s"]) if route is not None else 50.0
    if route is None:
        profile, profile_hash, contract_hash = selected_profile(driver, task_id)
        source_profile = copy.deepcopy(profile)
        duration_s = float(profile["duration_s"])

    injection = normalized_injection(
        gust_force_x_n=gust_force_x_n,
        mass_inertia_scale=mass_inertia_scale,
        motor_effectiveness=motor_effectiveness,
        fault_start_s=fault_start_s,
        duration_s=duration_s,
    )
    if route is not None and not route["injection_supported"] and not injection_is_nominal(
        float(injection["gust_force_x_n"]),
        float(injection["mass_inertia_scale"]),
        list(injection["motor_effectiveness"]),
    ):
        raise ValueError("task_route_does_not_support_injection")

    selection = {
        "vehicle_count": vehicle_count,
        "map_id": map_id,
        "fault_target_uav": fault_target_uav,
    }
    if profile is not None:
        apply_independent_parameters(profile, injection)
    name = model_name(driver, controller_id, task_id, selection, profile, route)
    resolved_output = output.resolve()
    harness_path = resolved_output.parent / "harness" / name / f"{name}.mo"
    if profile is not None:
        harness_text = rendered_formal_harness(driver, controller_id, task_id, profile, name)
        runner_class = driver.CONTROLLERS[controller_id]["runner_class"]
        kind = configuration_kind(task_id, profile, source_profile or profile)
    else:
        harness_text = rendered_special_harness(
            driver,
            task_id=task_id,
            route=route,
            injection=injection,
            fault_target_uav=fault_target_uav,
            name=name,
        )
        runner_class = str(route["base_model"])
        kind = str(route["configuration_kind"])
    harness_path.parent.mkdir(parents=True, exist_ok=True)
    harness_path.write_text(harness_text, encoding="utf-8", newline="\n")

    payload = {
        "schema": TASK_CONFIG_SCHEMA,
        "created_at": utc_now(),
        "controller_id": controller_id,
        "runner_class": runner_class,
        "task_id": task_id,
        "configuration_kind": kind,
        "selection": selection,
        "model_name": name,
        "harness_file": project_path_text(harness_path),
        "harness_sha256": sha256_path(harness_path),
        "profile": profile,
        "task_parameters": injection,
        "profile_source": project_path_text(PROFILE_PATH) if profile_hash is not None else None,
        "profile_source_sha256": profile_hash,
        "contract_source": project_path_text(CONTRACT_PATH) if contract_hash is not None else None,
        "contract_source_sha256": contract_hash,
        "claim_boundary": "Frozen configuration and generated harness only; no MWORKS simulation has been started.",
    }
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", choices=TASK_ORDER, required=True)
    parser.add_argument("--controller-id", required=True)
    parser.add_argument("--vehicle-count", type=int, default=1)
    parser.add_argument("--map-id", choices=sorted(MAP_IDS), default="blank")
    parser.add_argument("--fault-target-uav", type=int, default=1)
    parser.add_argument("--fault-start-s", type=float, default=DEFAULT_INJECTION_START_S)
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
        vehicle_count=args.vehicle_count,
        map_id=args.map_id,
        fault_target_uav=args.fault_target_uav,
        fault_start_s=args.fault_start_s,
        output=output,
    )
    print(json.dumps({
        "task_id": payload["task_id"],
        "controller_id": payload["controller_id"],
        "vehicle_count": payload["selection"]["vehicle_count"],
        "configuration_kind": payload["configuration_kind"],
        "harness_file": payload["harness_file"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
