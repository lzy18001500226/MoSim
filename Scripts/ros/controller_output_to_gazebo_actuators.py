#!/usr/bin/env python3
"""Convert MoSim ControllerOutput commands to Gazebo actuator velocities.

This adapter does not start ROS2, Gazebo, or publish motor commands itself.
The Gazebo+ROS2 smoke runner may use its generated Actuators payload for a
bounded actuator-topic handoff gate.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ROS_TOPIC = "/sunray150/gazebo/command/motor_speed"
DEFAULT_GZ_TOPIC = "/sunray150/gazebo/command/motor_speed"
DEFAULT_ACTUATOR_ORDER = ["rotor_0", "rotor_1", "rotor_2", "rotor_3"]
DEFAULT_MWORKS_SOURCE_ORDER = ["Dronefixed1", "Dronefixed2", "Dronefixed3", "Dronefixed4"]
DEFAULT_SPIN_SIGN = [1, 1, -1, -1]
DEFAULT_GAZEBO_TURNING_DIRECTION = ["ccw", "ccw", "cw", "cw"]


class AdapterError(ValueError):
    """Invalid controller-output command for the Gazebo actuator surface."""


@dataclass(frozen=True)
class AdapterConfig:
    ros_topic: str
    gz_topic: str
    actuator_order: list[str]
    mworks_source_order: list[str]
    spin_sign: list[int]
    gazebo_turning_direction: list[str]
    max_rot_velocity: float
    normalized_max_rot_velocity: float
    strict_signed_spin: bool
    expected_vehicle_id: str
    required_status: str
    max_command_age_s: float
    max_future_skew_s: float
    now_unix: float | None


def _finite_number(value: Any, index: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AdapterError(f"command[{index}] is not numeric") from exc
    if not math.isfinite(number):
        raise AdapterError(f"command[{index}] is not finite")
    return number


def _as_float_array(values: Any, actuator_count: int) -> list[float]:
    if not isinstance(values, list):
        raise AdapterError("command must be a list")
    if len(values) != actuator_count:
        raise AdapterError(f"command length {len(values)} does not match actuator_count {actuator_count}")
    return [_finite_number(item, index) for index, item in enumerate(values)]


def load_controller_output(path: Path | None, command: list[float] | None, command_type: str) -> dict[str, Any]:
    if path is not None:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise AdapterError("controller output JSON root must be an object")
        return data
    if command is None:
        raise AdapterError("either --input-json or --command is required")
    return {
        "schema": "mosim.controller_output_fixture.v1",
        "vehicle_id": "sunray150",
        "command_type": command_type,
        "command": command,
        "mode": "normal",
        "status": "valid",
        "backend": "fixture",
    }


def convert_command(data: dict[str, Any], config: AdapterConfig) -> tuple[list[float], list[str]]:
    issues: list[str] = []
    command_type = str(data.get("command_type", "")).strip()
    actuator_count = len(config.actuator_order)
    values = _as_float_array(data.get("command"), actuator_count)

    if command_type == "normalized_motor_speed":
        velocities = []
        for index, value in enumerate(values):
            if value < 0.0 or value > 1.0:
                raise AdapterError(f"normalized command[{index}] must be within [0, 1]")
            velocities.append(value * config.normalized_max_rot_velocity)
        return velocities, issues

    if command_type == "motor_speed":
        velocities = []
        for index, value in enumerate(values):
            if value < 0.0:
                raise AdapterError(f"motor_speed command[{index}] must be nonnegative for Gazebo velocity input")
            velocities.append(value)
        return velocities, issues

    if command_type == "mworks_signed_visual_motor_speed":
        velocities = []
        for index, value in enumerate(values):
            sign = config.spin_sign[index]
            if config.strict_signed_spin and value != 0.0 and math.copysign(1.0, value) != float(sign):
                raise AdapterError(
                    f"signed MWORKS command[{index}] sign does not match spin convention {sign}"
                )
            velocities.append(abs(value))
        return velocities, issues

    raise AdapterError(
        "unsupported command_type; expected motor_speed, normalized_motor_speed, "
        "or mworks_signed_visual_motor_speed"
    )


def validate_command_metadata(data: dict[str, Any], config: AdapterConfig) -> dict[str, Any]:
    vehicle_id = str(data.get("vehicle_id", "")).strip()
    status = str(data.get("status", "")).strip()
    now_unix = float(config.now_unix if config.now_unix is not None else time.time())
    metadata: dict[str, Any] = {
        "expected_vehicle_id": config.expected_vehicle_id,
        "required_status": config.required_status,
        "max_command_age_s": config.max_command_age_s,
        "max_future_skew_s": config.max_future_skew_s,
        "vehicle_id_checked": bool(config.expected_vehicle_id),
        "status_checked": bool(config.required_status),
        "age_checked": config.max_command_age_s > 0,
        "now_unix": now_unix if config.max_command_age_s > 0 else None,
        "issued_at_unix": None,
        "command_age_s": None,
    }
    if config.expected_vehicle_id and vehicle_id != config.expected_vehicle_id:
        raise AdapterError(
            f"vehicle_id {vehicle_id!r} does not match expected_vehicle_id {config.expected_vehicle_id!r}"
        )
    if config.required_status and status != config.required_status:
        raise AdapterError(f"status {status!r} does not match required_status {config.required_status!r}")
    if config.max_command_age_s > 0:
        raw_issued_at = data.get("issued_at_unix")
        if raw_issued_at is None:
            raise AdapterError("issued_at_unix is required when max_command_age_s is enabled")
        try:
            issued_at = float(raw_issued_at)
        except (TypeError, ValueError) as exc:
            raise AdapterError("issued_at_unix is not numeric") from exc
        if not math.isfinite(issued_at):
            raise AdapterError("issued_at_unix is not finite")
        command_age_s = now_unix - issued_at
        metadata["issued_at_unix"] = issued_at
        metadata["command_age_s"] = command_age_s
        if command_age_s > config.max_command_age_s:
            raise AdapterError(
                f"command age {command_age_s:.3f}s exceeds max_command_age_s {config.max_command_age_s:.3f}s"
            )
        if command_age_s < -config.max_future_skew_s:
            raise AdapterError(
                f"command timestamp is {-command_age_s:.3f}s in the future, "
                f"beyond max_future_skew_s {config.max_future_skew_s:.3f}s"
            )
    return metadata


def validate_config(config: AdapterConfig) -> None:
    actuator_count = len(config.actuator_order)
    if actuator_count != 4:
        raise AdapterError("the first Sunray150 Gazebo adapter requires exactly four actuators")
    if len(config.mworks_source_order) != actuator_count:
        raise AdapterError("mworks_source_order length must match actuator_order")
    if len(config.spin_sign) != actuator_count:
        raise AdapterError("spin_sign length must match actuator_order")
    if len(config.gazebo_turning_direction) != actuator_count:
        raise AdapterError("gazebo_turning_direction length must match actuator_order")
    if any(sign not in (-1, 1) for sign in config.spin_sign):
        raise AdapterError("spin_sign values must be -1 or 1")
    if config.max_rot_velocity <= 0 or config.normalized_max_rot_velocity <= 0:
        raise AdapterError("max rotational velocities must be positive")
    if config.max_command_age_s < 0:
        raise AdapterError("max_command_age_s must be nonnegative")
    if config.max_future_skew_s < 0:
        raise AdapterError("max_future_skew_s must be nonnegative")


def format_ros_cli_yaml(velocities: list[float]) -> str:
    values = ", ".join(f"{value:.12g}" for value in velocities)
    return f"{{position: [], velocity: [{values}], normalized: []}}"


def build_report(data: dict[str, Any], config: AdapterConfig) -> dict[str, Any]:
    validate_config(config)
    metadata_policy = validate_command_metadata(data, config)
    velocities, issues = convert_command(data, config)
    for index, value in enumerate(velocities):
        if value < 0:
            raise AdapterError(f"Gazebo velocity[{index}] is negative")
        if value > config.max_rot_velocity:
            raise AdapterError(f"Gazebo velocity[{index}] exceeds max_rot_velocity")

    return {
        "schema": "mosim.controller_output_to_gazebo_actuators.v1",
        "status": "actuator_payload_ready",
        "vehicle_id": str(data.get("vehicle_id", "sunray150")),
        "sequence": data.get("sequence"),
        "input_contract": "mosim_msgs/msg/ControllerOutput",
        "input_command_type": str(data.get("command_type", "")),
        "input_status": str(data.get("status", "")),
        "source_authority": str(data.get("source_authority", "")),
        "ros_topic": config.ros_topic,
        "gz_topic": config.gz_topic,
        "ros_type": "actuator_msgs/msg/Actuators",
        "gz_type": "gz.msgs.Actuators",
        "command_field": "velocity",
        "velocity": velocities,
        "ros_message": {
            "position": [],
            "velocity": velocities,
            "normalized": [],
        },
        "ros_cli_yaml": format_ros_cli_yaml(velocities),
        "actuator_order": config.actuator_order,
        "mworks_source_order": config.mworks_source_order,
        "mworks_spin_command_sign": config.spin_sign,
        "gazebo_turning_direction": config.gazebo_turning_direction,
        "signed_speed_policy": "magnitude_after_spin_sign_validation",
        "metadata_policy": metadata_policy,
        "command_age_s": metadata_policy.get("command_age_s"),
        "issues": issues,
        "claim_boundary": [
            "This adapter only builds a ROS2/Gazebo Actuators payload.",
            "A passing conversion does not prove Gazebo runtime, closed_loop, planner_ready, or controller performance.",
            "Motor constants and rotor geometry remain first-lane scaffold values until parameter identification evidence is recorded.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--command", nargs="*", type=float)
    parser.add_argument("--command-type", default="normalized_motor_speed")
    parser.add_argument("--ros-topic", default=DEFAULT_ROS_TOPIC)
    parser.add_argument("--gz-topic", default=DEFAULT_GZ_TOPIC)
    parser.add_argument("--actuator-order", nargs=4, default=DEFAULT_ACTUATOR_ORDER)
    parser.add_argument("--mworks-source-order", nargs=4, default=DEFAULT_MWORKS_SOURCE_ORDER)
    parser.add_argument("--spin-sign", nargs=4, type=int, default=DEFAULT_SPIN_SIGN)
    parser.add_argument("--gazebo-turning-direction", nargs=4, default=DEFAULT_GAZEBO_TURNING_DIRECTION)
    parser.add_argument("--max-rot-velocity", type=float, default=8000.0)
    parser.add_argument("--normalized-max-rot-velocity", type=float, default=8000.0)
    parser.add_argument("--allow-signed-spin-mismatch", action="store_true")
    parser.add_argument("--expected-vehicle-id", default="")
    parser.add_argument("--required-status", default="")
    parser.add_argument("--max-command-age-s", type=float, default=0.0)
    parser.add_argument("--max-future-skew-s", type=float, default=0.5)
    parser.add_argument("--now-unix", type=float)
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = AdapterConfig(
        ros_topic=args.ros_topic,
        gz_topic=args.gz_topic,
        actuator_order=list(args.actuator_order),
        mworks_source_order=list(args.mworks_source_order),
        spin_sign=list(args.spin_sign),
        gazebo_turning_direction=list(args.gazebo_turning_direction),
        max_rot_velocity=args.max_rot_velocity,
        normalized_max_rot_velocity=args.normalized_max_rot_velocity,
        strict_signed_spin=not args.allow_signed_spin_mismatch,
        expected_vehicle_id=args.expected_vehicle_id,
        required_status=args.required_status,
        max_command_age_s=args.max_command_age_s,
        max_future_skew_s=args.max_future_skew_s,
        now_unix=args.now_unix,
    )
    try:
        data = load_controller_output(args.input_json, args.command, args.command_type)
        report = build_report(data, config)
        rc = 0
    except Exception as exc:
        report = {
            "schema": "mosim.controller_output_to_gazebo_actuators.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "claim_boundary": [
                "No ROS2 or Gazebo command was published.",
                "This blocker does not prove or disprove controller performance.",
            ],
        }
        rc = 1

    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    print(text, end="")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
