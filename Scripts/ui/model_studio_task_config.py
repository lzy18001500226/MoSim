#!/usr/bin/env python3
"""Freeze one Model Studio task without starting MWORKS.

The resulting JSON describes an existing single- or three-UAV MWORKS model
plus a temporary Modelica harness, or a hash-bound batch execution plan for
the seven-scenario route. The harness adds no controller logic. This script
never starts a solver, opens a Sysplorer session, or records simulation
evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_v2.json"
CONTRACT_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract_v2.json"
DRIVER_PATH = ROOT / "Scripts" / "mworks" / "run_seven_scenario_ab.py"
TASK_ROUTE_PATH = ROOT / "Config" / "control_platform" / "model_studio_task_routes_v1.toml"
CONTROL_SCHEME_CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
CURRENT_MODEL_ENTRY_MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
DEFAULT_OUTPUT = ROOT / "Results" / "ui_platform" / "model_studio_task_handoffs" / "latest.json"
TASK_CONFIG_SCHEMA = "mosim.model_studio.task_config.v1"
TASK_ROUTE_SCHEMA = "mosim.model_studio_task_routes.v1"
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
    "seven_scenario_ab",
    "single_uav_autonomous_avoidance",
    "three_uav_figure8",
    "three_uav_autonomous_avoidance",
)
TASK_ORDER = FORMAL_TASK_IDS + LEGACY_INJECTION_TASK_IDS + SPECIAL_TASK_IDS
V2_EVIDENCE_CONTROLLER_IDS = frozenset({"official_pid", "px4ctrl"})
# These routes have a project-owned whole-aircraft Runner even when the
# historical current-model map has not yet been promoted to runtime evidence.
MOTHER_BUS_CONTROLLER_IDS = frozenset({"official_pid", "px4ctrl", "pid_awff_linear_eso"})
MAP_IDS = frozenset({"blank", "openblocks"})
EPSILON = 1e-9
DEFAULT_INJECTION_START_S = 15.0
MODEL_DECLARATION_PATTERN = re.compile(r"^model\s+([A-Za-z_]\w*)", re.MULTILINE)
SCENARIO_PARAMETER_PATTERN = re.compile(
    r"^\s*parameter\s+Integer\s+scenario_mode\b[^=]*=\s*[^;]+;?",
    re.MULTILINE,
)
REFERENCE_BINDING_PATTERN = re.compile(
    r"MultiModeTrajectory\s+reference\s*\(\s*scenario_mode\s*=\s*scenario_mode\b",
    re.MULTILINE,
)
COMMON_RUNNER_PARAMETER_NAMES = (
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
SCENARIO_MODE_BY_TRAJECTORY = {
    "ClimbPath": 0,
    "ClimbTrajectory": 0,
    "HoverHold": 1,
    "StepResponse": 2,
    "Figure8": 3,
    "SpiralAscent": 4,
}

SPECIAL_ROUTES: dict[str, dict[str, Any]] = {
    "seven_scenario_ab": {
        "vehicle_count": 1,
        "map_id": "blank",
        "controller_ids": frozenset({"official_pid", "px4ctrl"}),
        "duration_s": 50.0,
        "injection_supported": False,
        "configuration_kind": "seven_scenario_ab_batch",
        "batch_profile_path": "Config/control_platform/seven_scenario_experiment_profiles_v2.json",
        "batch_contract_path": "Config/control_platform/seven_scenario_injection_contract_v2.json",
        "batch_driver_path": "Scripts/mworks/run_seven_scenario_ab.py",
        "batch_result_root": "Results/control_platform/seven_scenario_ab_v2",
        "batch_evidence_level": "formal_mworks_seven_scenario_ab_v2",
    },
    "single_uav_autonomous_avoidance": {
        "vehicle_count": 1,
        "map_id": "openblocks",
        "controller_ids": frozenset({"px4ctrl"}),
        "base_model": "MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.SingleUav.Px4CtrlOpenBlocksRunner",
        "duration_s": 80.1247340259,
        "injection_supported": True,
        "configuration_kind": "single_uav_planning_route",
    },
    "three_uav_figure8": {
        "vehicle_count": 3,
        "map_id": "blank",
        "controller_ids": frozenset({"px4ctrl"}),
        "base_model": "MoSimQuadrotorModel.Experiment.Formation.Px4Ctrl.ThreeUavPx4CtrlFormationRunner",
        "duration_s": 50.0,
        "injection_supported": True,
        "configuration_kind": "three_uav_formation_route",
    },
    "three_uav_autonomous_avoidance": {
        "vehicle_count": 3,
        "map_id": "openblocks",
        "controller_ids": frozenset({"linear_mpc"}),
        "base_model": "MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.Formation.ThreeUavPx4CtrlOpenBlocksRunner",
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


def active_controller_ids() -> frozenset[str]:
    document = json.loads(CONTROL_SCHEME_CATALOG_PATH.read_text(encoding="utf-8-sig"))
    rows = document.get("schemes")
    if document.get("schema") != "mosim.control_profile_catalog.v2" or not isinstance(rows, list):
        raise ValueError("model_studio_controller_catalog_invalid")
    controller_ids = [row.get("scheme_id") for row in rows if isinstance(row, dict)]
    if any(not isinstance(controller_id, str) or not controller_id for controller_id in controller_ids):
        raise ValueError("model_studio_controller_catalog_id_missing")
    if len(set(controller_ids)) != len(controller_ids):
        raise ValueError("model_studio_controller_catalog_id_duplicate")
    return frozenset(controller_ids)


def load_current_model_entries() -> dict[str, dict[str, Any]]:
    document = json.loads(CURRENT_MODEL_ENTRY_MAP_PATH.read_text(encoding="utf-8-sig"))
    if document.get("schema") != "mosim.current_model_entry_map.v1":
        raise ValueError("current_model_entry_map_schema_invalid")
    rows = document.get("schemes")
    if not isinstance(rows, list):
        raise ValueError("current_model_entry_map_schemes_invalid")
    entries: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("scheme_id"), str):
            raise ValueError("current_model_entry_map_scheme_invalid")
        scheme_id = str(row["scheme_id"])
        if scheme_id in entries:
            raise ValueError(f"current_model_entry_map_scheme_duplicate: {scheme_id}")
        entries[scheme_id] = row
    return entries


CURRENT_MODEL_ENTRIES = load_current_model_entries()


def load_manual_formal_routes() -> dict[str, dict[str, Any]]:
    with TASK_ROUTE_PATH.open("rb") as handle:
        document = tomllib.load(handle)
    if document.get("schema") != TASK_ROUTE_SCHEMA:
        raise ValueError("invalid_model_studio_task_route_schema")
    configured_task_ids = tuple(str(item) for item in document.get("formal_task_ids", []))
    if configured_task_ids != FORMAL_TASK_IDS:
        raise ValueError("model_studio_task_route_formal_task_ids_mismatch")
    rows = document.get("route", [])
    if not isinstance(rows, list):
        raise ValueError("model_studio_task_routes_must_be_a_list")
    routes: dict[str, dict[str, Any]] = {}
    for raw_route in rows:
        if not isinstance(raw_route, dict):
            raise ValueError("model_studio_task_route_must_be_an_object")
        controller_id = raw_route.get("controller_id")
        if not isinstance(controller_id, str) or not controller_id:
            raise ValueError("model_studio_task_route_controller_id_missing")
        if controller_id in routes:
            raise ValueError(f"model_studio_task_route_duplicate_controller: {controller_id}")
        available = raw_route.get("available")
        if not isinstance(available, bool):
            raise ValueError(f"model_studio_task_route_available_invalid: {controller_id}")
        route = dict(raw_route)
        if available:
            for field in ("runner_class", "runner_file", "boundary"):
                if not isinstance(route.get(field), str) or not route[field]:
                    raise ValueError(f"model_studio_task_route_{field}_missing: {controller_id}")
            runner_file = (ROOT / str(route["runner_file"])).resolve()
            try:
                runner_file.relative_to(ROOT.resolve())
            except ValueError as exc:
                raise ValueError(f"model_studio_task_route_runner_file_outside_project: {controller_id}") from exc
            if not runner_file.is_file():
                raise ValueError(f"model_studio_task_route_runner_file_missing: {controller_id}")
            current_entry = CURRENT_MODEL_ENTRIES.get(controller_id)
            if controller_id not in MOTHER_BUS_CONTROLLER_IDS:
                if current_entry is None:
                    raise ValueError(f"model_studio_task_route_current_model_missing: {controller_id}")
                if current_entry.get("mapping_state") != "resolved_current_model":
                    raise ValueError(
                        f"model_studio_task_route_current_model_not_resolved: {controller_id}: "
                        f"{current_entry.get('mapping_state')}"
                    )
            runner_source = runner_file.read_text(encoding="utf-8")
            within_match = re.search(r"^within\s+([^;]+);", runner_source, re.MULTILINE)
            model_match = MODEL_DECLARATION_PATTERN.search(runner_source)
            declared_class = (
                f"{within_match.group(1)}.{model_match.group(1)}"
                if within_match is not None and model_match is not None
                else None
            )
            if declared_class != route["runner_class"]:
                raise ValueError(
                    f"model_studio_task_route_runner_class_mismatch: {controller_id}: "
                    f"{route['runner_class']} != {declared_class}"
                )
            if SCENARIO_PARAMETER_PATTERN.search(runner_source) is None:
                raise ValueError(f"model_studio_task_route_scenario_parameter_missing: {controller_id}")
            if REFERENCE_BINDING_PATTERN.search(runner_source) is None:
                raise ValueError(f"model_studio_task_route_trajectory_binding_missing: {controller_id}")
            missing_parameters = [
                name
                for name in COMMON_RUNNER_PARAMETER_NAMES
                if re.search(rf"\bparameter\s+(?:Real|Integer)\s+{re.escape(name)}\b", runner_source) is None
            ]
            if missing_parameters:
                raise ValueError(
                    f"model_studio_task_route_parameter_missing: {controller_id}: {','.join(missing_parameters)}"
                )
        elif not isinstance(route.get("reason"), str) or not route["reason"]:
            raise ValueError(f"model_studio_task_route_reason_missing: {controller_id}")
        routes[controller_id] = route
    catalog_ids = active_controller_ids()
    route_ids = frozenset(routes)
    if route_ids != catalog_ids:
        missing = sorted(catalog_ids - route_ids)
        extra = sorted(route_ids - catalog_ids)
        raise ValueError(
            "model_studio_task_route_controller_ids_mismatch: "
            f"missing={missing}, extra={extra}"
        )
    return routes


FORMAL_CONTROLLER_ROUTES = load_manual_formal_routes()
FORMAL_CONTROLLER_IDS = frozenset(
    controller_id
    for controller_id, route in FORMAL_CONTROLLER_ROUTES.items()
    if bool(route["available"])
)
SEVEN_SCENARIO_CONTROLLER_IDS = frozenset(FORMAL_CONTROLLER_ROUTES)
SPECIAL_ROUTES["seven_scenario_ab"]["controller_ids"] = SEVEN_SCENARIO_CONTROLLER_IDS


def controller_source_entry(controller_id: str) -> dict[str, Any] | None:
    entry = CURRENT_MODEL_ENTRIES.get(controller_id)
    if entry is None:
        return None
    return {
        "scheme_id": controller_id,
        "mapping_state": entry.get("mapping_state"),
        "current_model_file": entry.get("current_model_file"),
        "current_model_class": entry.get("current_model_class"),
        "current_model_sha256": entry.get("current_model_sha256"),
        "current_model_role": entry.get("current_model_role"),
        "next_gate": entry.get("next_gate"),
    }


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
) -> tuple[str, dict[str, Any]]:
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
        route = FORMAL_CONTROLLER_ROUTES.get(controller_id)
        if route is None or not bool(route["available"]):
            raise ValueError("formal_task_controller_has_no_registered_runner")
        return "formal", copy.deepcopy(route)

    route = SPECIAL_ROUTES.get(task_id)
    if route is None:
        raise ValueError(f"unknown_task_id: {task_id}")
    if vehicle_count != route["vehicle_count"]:
        raise ValueError("task_vehicle_count_not_supported")
    if map_id != route["map_id"]:
        raise ValueError("task_map_not_supported")
    if controller_id not in route["controller_ids"]:
        raise ValueError("task_controller_not_supported")
    return "special", copy.deepcopy(route)


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


def modelica_number(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non_finite_modelica_value: {value!r}")
        return format(value, ".17g")
    raise TypeError(f"unsupported_modelica_scalar: {value!r}")


def modelica_value(value: Any) -> str:
    if isinstance(value, list):
        return "{" + ", ".join(modelica_value(item) for item in value) + "}"
    return modelica_number(value)


def profile_trajectory_modification(profile: dict[str, Any]) -> str:
    trajectory_class = str(profile["trajectory_class"])
    parameters = profile.get("trajectory_parameter_overrides", {})
    if not isinstance(parameters, dict):
        raise ValueError(f"trajectory_parameter_overrides_invalid: {profile['scenario_id']}")
    if not parameters:
        return trajectory_class
    modifications = ", ".join(
        f"{key} = {modelica_value(value)}" for key, value in parameters.items()
    )
    return f"{trajectory_class}({modifications})"


def scenario_mode_for_profile(profile: dict[str, Any]) -> int:
    trajectory_class = str(profile["trajectory_class"])
    trajectory_name = trajectory_class.rsplit(".", 1)[-1]
    try:
        return SCENARIO_MODE_BY_TRAJECTORY[trajectory_name]
    except KeyError as exc:
        raise ValueError(f"unsupported_multimode_trajectory: {trajectory_class}") from exc


def scenario_mode_modifications(profile: dict[str, Any]) -> list[str]:
    parameters = profile.get("trajectory_parameter_overrides", {})
    if not isinstance(parameters, dict):
        raise ValueError(f"trajectory_parameter_overrides_invalid: {profile['scenario_id']}")
    nested_reference = [
        f"{key} = {modelica_value(value)}" for key, value in parameters.items()
    ]
    modifications = [f"scenario_mode = {scenario_mode_for_profile(profile)}"]
    if nested_reference:
        modifications.append("reference(" + ", ".join(nested_reference) + ")")
    return modifications


TRAJECTORY_COMPONENT_TYPE = "MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory"


def _skip_modelica_token(text: str, index: int) -> int:
    """Advance past a string literal or comment starting at index; else index + 1."""
    if text.startswith('"', index):
        index += 1
        while index < len(text):
            if text[index] == "\\":
                index += 2
                continue
            if text[index] == '"':
                return index + 1
            index += 1
        raise ValueError("unterminated_modelica_string")
    if text.startswith("//", index):
        end = text.find("\n", index)
        return len(text) if end < 0 else end
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        if end < 0:
            raise ValueError("unterminated_modelica_comment")
        return end + 2
    return index + 1


def _match_paren(text: str, open_index: int) -> int:
    """Return the index just past the ')' that closes text[open_index] == '('."""
    if text[open_index] != "(":
        raise ValueError("expected_open_parenthesis")
    depth = 0
    index = open_index
    while index < len(text):
        char = text[index]
        if char in '"/':
            moved = _skip_modelica_token(text, index)
            if moved != index + 1:
                index = moved
                continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
        index = _skip_modelica_token(text, index)
    raise ValueError("unbalanced_parenthesis")


def _split_modifier_items(body: str) -> list[str]:
    """Split a modifier body on top-level commas, ignoring nested brackets."""
    items: list[str] = []
    depth = 0
    start = 0
    index = 0
    while index < len(body):
        char = body[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            items.append(body[start:index])
            start = index + 1
        index = _skip_modelica_token(body, index)
    tail = body[start:]
    if tail.strip():
        items.append(tail)
    return items


def patched_parameter_default(text: str, parameter_name: str, value: str) -> str:
    """Rewrite the default binding of one top-level parameter declaration."""
    declaration = re.search(
        rf"(?m)^[ \t]*parameter[ \t]+[A-Za-z_][\w.]*[ \t]+{re.escape(parameter_name)}(?![\w])",
        text,
    )
    if declaration is None:
        raise ValueError(f"runner_parameter_not_declared: {parameter_name}")

    depth = 0
    index = declaration.end()
    equals_index: int | None = None
    while index < len(text):
        char = text[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth == 0 and char == "=":
            equals_index = index
            break
        elif depth == 0 and char in ';"':
            break
        index = _skip_modelica_token(text, index)

    if equals_index is None:
        # No default binding yet; insert one right after the declared type.
        return f"{text[:index].rstrip()} = {value}{text[index:]}"

    depth = 0
    index = equals_index + 1
    while index < len(text):
        char = text[index]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth == 0 and char in ';"':
            break
        index = _skip_modelica_token(text, index)
    return f"{text[:equals_index]}= {value}{'' if text[index] == ';' else ' '}{text[index:]}"


def patched_component_modifiers(
    text: str,
    component_type: str,
    overrides: dict[str, str],
) -> str:
    """Upsert modifiers on the first component declared with component_type."""
    if not overrides:
        return text
    declaration = re.search(
        rf"{re.escape(component_type)}[ \t\r\n]+([A-Za-z_]\w*)",
        text,
    )
    if declaration is None:
        raise ValueError(f"runner_component_not_declared: {component_type}")

    cursor = declaration.end()
    while cursor < len(text) and text[cursor] in " \t\r\n":
        cursor += 1
    if cursor < len(text) and text[cursor] == "(":
        close = _match_paren(text, cursor)
        items = _split_modifier_items(text[cursor + 1 : close - 1])
    else:
        close = cursor
        items = []

    remaining = dict(overrides)
    rewritten: list[str] = []
    for item in items:
        key = re.match(r"\s*([A-Za-z_]\w*)\s*(?:\(|=)", item)
        if key is not None and key.group(1) in remaining:
            rewritten.append(f"{key.group(1)} = {remaining.pop(key.group(1))}")
        else:
            rewritten.append(item.strip())
    rewritten.extend(f"{key} = {value}" for key, value in remaining.items())
    return f"{text[:cursor]}({', '.join(rewritten)}){text[close:]}"


def rendered_generic_formal_harness(
    *,
    task_id: str,
    route: dict[str, Any],
    profile: dict[str, Any],
    name: str,
) -> str:
    """Freeze the task as a renamed copy of the Runner with patched defaults.

    MWORKS 2026a raises "编译器错误(2000): Internal Error, code 1" when it
    instantiates a subclass of these whole-aircraft Runners, so the harness
    cannot use `extends`. Copying the Runner source and rewriting the parameter
    defaults keeps both the graphical diagram and the flat result-variable names
    (`position[1]`, not `runner.position[1]`) that the App review surface needs.
    """
    runner_parameters = profile.get("runner_parameter_overrides", {})
    if not isinstance(runner_parameters, dict):
        raise ValueError(f"runner_parameter_overrides_invalid: {task_id}")
    trajectory_parameters = profile.get("trajectory_parameter_overrides", {})
    if not isinstance(trajectory_parameters, dict):
        raise ValueError(f"trajectory_parameter_overrides_invalid: {task_id}")

    runner_class = str(route["runner_class"])
    runner_source = ROOT / str(route["runner_file"])
    if not runner_source.is_file():
        raise ValueError(f"runner_file_missing: {route['runner_file']}")
    source_name = runner_class.rsplit(".", 1)[-1]
    text = runner_source.read_text(encoding="utf-8")

    header = re.match(r"\s*within[^;]*;", text)
    if header is None:
        raise ValueError(f"runner_within_clause_missing: {route['runner_file']}")
    text = f"within ;{text[header.end():]}"

    class_declaration = re.search(rf"(?m)^\s*model[ \t]+{re.escape(source_name)}(?![\w])", text)
    class_terminator = re.search(rf"(?m)^\s*end[ \t]+{re.escape(source_name)}[ \t]*;", text)
    if class_declaration is None or class_terminator is None:
        raise ValueError(f"runner_class_not_found: {runner_class}")
    text = f"{text[:class_terminator.start()]}end {name};\n"

    banner = (
        f'model {name}\n'
        f'  "Frozen Model Studio task for {task_id}; no simulation evidence is recorded"\n'
        f'  // Copied from {runner_class} with parameter defaults patched in place.\n'
        f'  // MWORKS 2026a internal-errors when instantiating a subclass of this\n'
        f'  // Runner, so this harness is a renamed copy rather than an extends.\n'
    )
    body_start = class_declaration.end()
    description = re.match(r'[ \t\r\n]*"(?:[^"\\]|\\.)*"', text[body_start:])
    if description is not None:
        body_start += description.end()
    text = text[: class_declaration.start()] + "\n" + banner + text[body_start:]

    text = patched_parameter_default(
        text, "scenario_mode", str(scenario_mode_for_profile(profile))
    )
    for key, value in runner_parameters.items():
        text = patched_parameter_default(text, key, modelica_value(value))
    text = patched_component_modifiers(
        text,
        TRAJECTORY_COMPONENT_TYPE,
        {key: modelica_value(value) for key, value in trajectory_parameters.items()},
    )
    return text



def injection_modifications(
    injection: dict[str, Any],
    duration_s: float,
) -> list[str]:
    gust_force_x_n = float(injection["gust_force_x_n"])
    mass_inertia_scale = float(injection["mass_inertia_scale"])
    fault_start_s = float(injection["fault_start_s"])
    gust_duration_s = max(0.0, duration_s - fault_start_s) if gust_force_x_n > EPSILON else 0.0
    return [
        f"gust_force = {modelica_value([gust_force_x_n, 0.0, 0.0])}",
        f"gust_start_s = {modelica_value(fault_start_s if gust_force_x_n > EPSILON else 0.0)}",
        f"gust_duration_s = {modelica_value(gust_duration_s)}",
        f"mass_scale = {modelica_value(mass_inertia_scale)}",
        f"inertia_scale = {modelica_value([mass_inertia_scale, mass_inertia_scale, mass_inertia_scale])}",
        "rotor_effectiveness = {1, 1, 1, 1}",
        f"fault_start_s = {modelica_value(float(injection['fault_start_s']) if float(injection['fault_rotor_effectiveness']) < 1.0 - EPSILON else 1_000_000_000.0)}",
        f"fault_rotor_index = {modelica_value(int(injection['fault_rotor_index']))}",
        f"fault_rotor_effectiveness = {modelica_value(float(injection['fault_rotor_effectiveness']))}",
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

    modifications = injection_modifications(injection, float(route["duration_s"]))
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

    route_kind, route = validate_selection(task_id, controller_id, vehicle_count, map_id, fault_target_uav)
    driver = load_driver()
    profile: dict[str, Any] | None = None
    source_profile: dict[str, Any] | None = None
    profile_hash: str | None = None
    contract_hash: str | None = None
    duration_s = float(route["duration_s"]) if route_kind == "special" else 50.0
    if route_kind == "formal":
        profile, profile_hash, contract_hash = selected_profile(driver, task_id)
        source_profile = copy.deepcopy(profile)
        duration_s = float(profile["duration_s"])
    elif route.get("configuration_kind") == "seven_scenario_ab_batch":
        _, profile_hash = driver.read_profiles(PROFILE_PATH)
        _, contract_hash = driver.read_contract(CONTRACT_PATH)

    injection = normalized_injection(
        gust_force_x_n=gust_force_x_n,
        mass_inertia_scale=mass_inertia_scale,
        motor_effectiveness=motor_effectiveness,
        fault_start_s=fault_start_s,
        duration_s=duration_s,
    )
    if route_kind == "special" and not route["injection_supported"] and not injection_is_nominal(
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
    if route_kind == "formal":
        apply_independent_parameters(profile, injection)
    name = model_name(driver, controller_id, task_id, selection, profile, route)
    resolved_output = output.resolve()
    batch_route = route_kind == "special" and route.get("configuration_kind") == "seven_scenario_ab_batch"
    harness_path = None if batch_route else resolved_output.parent / "harness" / name / f"{name}.mo"
    if route_kind == "formal":
        if controller_id == "official_pid":
            # The graphical golden runner is the App review surface. The unchanged
            # Formal runner remains the numerical reference outside this manual path.
            harness_text = rendered_generic_formal_harness(
                task_id=task_id,
                route=route,
                profile=profile,
                name=name,
            )
            kind = configuration_kind(task_id, profile, source_profile or profile)
        elif controller_id in V2_EVIDENCE_CONTROLLER_IDS:
            # The app handoff must bind the same current Runner catalog as every
            # other controller. Formal evidence generation remains in the driver.
            harness_text = rendered_generic_formal_harness(
                task_id=task_id,
                route=route,
                profile=profile,
                name=name,
            )
            kind = configuration_kind(task_id, profile, source_profile or profile)
        else:
            harness_text = rendered_generic_formal_harness(
                task_id=task_id,
                route=route,
                profile=profile,
                name=name,
            )
            kind = "manual_formal_task"
        runner_class = str(route["runner_class"])
    elif batch_route:
        harness_text = None
        runner_class = str(route["batch_driver_path"])
        kind = str(route["configuration_kind"])
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
    if harness_path is not None and harness_text is not None:
        harness_path.parent.mkdir(parents=True, exist_ok=True)
        harness_path.write_text(harness_text, encoding="utf-8", newline="\n")

    batch_command = None
    if batch_route:
        batch_command = [
            "python",
            route["batch_driver_path"],
            "--profile-path",
            route["batch_profile_path"],
            "--contract-path",
            route["batch_contract_path"],
            "--result-root",
            route["batch_result_root"],
            "--evidence-level",
            route["batch_evidence_level"],
        ]
        for batch_controller_id in sorted(SEVEN_SCENARIO_CONTROLLER_IDS):
            batch_command.extend(["--controller", batch_controller_id])

    payload = {
        "schema": TASK_CONFIG_SCHEMA,
        "created_at": utc_now(),
        "controller_id": controller_id,
        "runner_class": runner_class,
        "trajectory_binding": "scenario_mode",
        "trajectory_mode": scenario_mode_for_profile(profile) if route_kind == "formal" else None,
        "task_id": task_id,
        "configuration_kind": kind,
        "selection": selection,
        "model_name": name,
        "harness_file": project_path_text(harness_path) if harness_path is not None else None,
        "harness_sha256": sha256_path(harness_path) if harness_path is not None else None,
        "profile": profile,
        "task_parameters": injection,
        "profile_source": project_path_text(PROFILE_PATH) if profile_hash is not None else None,
        "profile_source_sha256": profile_hash,
        "contract_source": project_path_text(CONTRACT_PATH) if contract_hash is not None else None,
        "contract_source_sha256": contract_hash,
        "task_route_source": project_path_text(TASK_ROUTE_PATH) if route_kind == "formal" else None,
        "task_route_source_sha256": sha256_path(TASK_ROUTE_PATH) if route_kind == "formal" else None,
        "controller_source": controller_source_entry(controller_id) if route_kind == "formal" else None,
        "task_route": {
            "boundary": route["boundary"],
            "runner_alias": route.get("runner_alias"),
            "runner_class": route["runner_class"],
            "runner_file": route["runner_file"],
        } if route_kind == "formal" else (
            {
                "configuration_kind": route["configuration_kind"],
                "driver": route["batch_driver_path"],
                "profile": route["batch_profile_path"],
                "contract": route["batch_contract_path"],
                "controllers": sorted(SEVEN_SCENARIO_CONTROLLER_IDS),
                "command": batch_command,
            } if batch_route else None
        ),
        "claim_boundary": (
            "Manual MWORKS configuration or batch execution plan only; no MWORKS simulation has been started and no evidence verdict is recorded."
            if batch_route else
            "Manual MWORKS configuration and generated harness only; no MWORKS simulation has been started and no evidence verdict is recorded."
        ),
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
