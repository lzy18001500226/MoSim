#!/usr/bin/env python3
"""Publish bounded ControllerOutput from Gazebo truth pose for hover-hold smoke.

This is a first executable closed-loop pre-acceptance controller. It consumes
Gazebo transport dynamic-pose text from stdin and publishes the project
`mosim_msgs/msg/ControllerOutput` ABI. It is intentionally narrow: bounded
truth-feedback hover hold only, no planner setpoints, no arming surface, and no
controller-performance claim.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
GAZEBO_HELPERS = ROOT / "Scripts" / "gazebo"
if str(GAZEBO_HELPERS) not in sys.path:
    sys.path.insert(0, str(GAZEBO_HELPERS))

from capture_gazebo_state_truth_topic import parse_samples as parse_state_samples  # noqa: E402
from record_gazebo_pose_truth import parse_samples as parse_pose_samples  # noqa: E402


DEFAULT_INPUT_TOPIC = "/world/mosim_factory_minimal/dynamic_pose/info"
DEFAULT_OUTPUT_TOPIC = "/mosim/sunray150/controller_output"
# Rotor order and positions in Config/gazebo/models/sunray150_assembled/model.sdf:
# 0 front-right, 1 back-left, 2 front-left, 3 back-right.
ROLL_MIX = [-1.0, 1.0, 1.0, -1.0]
PITCH_MIX = [-1.0, 1.0, -1.0, 1.0]
# Gazebo MulticopterMotorModel with current ccw/ccw/cw/cw SDF convention
# responds to this differential sign for positive yaw correction in truth
# feedback. Keep this controller-local until a dedicated motor-axis gate
# promotes the convention to shared controller code.
YAW_MIX = [-1.0, -1.0, 1.0, 1.0]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def finite(value: float, *, name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def bounded(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def angle_wrap(value: float) -> float:
    while value > math.pi:
        value -= 2.0 * math.pi
    while value < -math.pi:
        value += 2.0 * math.pi
    return value


def quaternion_to_euler_xyzw(values: list[float]) -> tuple[float, float, float]:
    x, y, z, w = values
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 0.0:
        return 0.0, 0.0, 0.0
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    sin_pitch = 2.0 * (w * y - z * x)
    pitch = math.asin(max(-1.0, min(1.0, sin_pitch)))
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


def sample_orientation(sample: dict[str, Any]) -> tuple[float, float, float]:
    values = sample.get("orientation_xyzw")
    if not isinstance(values, list) or len(values) != 4:
        return 0.0, 0.0, 0.0
    try:
        quaternion = [float(values[0]), float(values[1]), float(values[2]), float(values[3])]
    except (TypeError, ValueError):
        return 0.0, 0.0, 0.0
    if not all(math.isfinite(item) for item in quaternion):
        return 0.0, 0.0, 0.0
    return quaternion_to_euler_xyzw(quaternion)


def iter_stdin_message_chunks(lines: Iterable[str]) -> Iterable[str]:
    """Yield Gazebo `ign topic -e` chunks as text.

    Fortress usually separates messages with `---`. Some builds emit repeated
    `header {` blocks without separators, so a new top-level header also starts
    a new chunk after the first buffered message.
    """

    buffer: list[str] = []
    seen_header = False
    header_pattern = re.compile(r"^header\s*\{")
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            chunk = "".join(buffer).strip()
            if chunk:
                yield chunk
            buffer = []
            seen_header = False
            continue
        if header_pattern.match(line) and buffer and seen_header:
            chunk = "".join(buffer).strip()
            if chunk:
                yield chunk
            buffer = [line]
            seen_header = True
            continue
        if header_pattern.match(line):
            seen_header = True
        buffer.append(line)
    chunk = "".join(buffer).strip()
    if chunk:
        yield chunk


def parse_truth_samples(chunk: str, *, model_name: str, topic: str, frame_id: str) -> list[dict[str, Any]]:
    samples = parse_pose_samples(chunk, model_name=model_name, topic=topic, frame_id=frame_id)
    if samples:
        return samples
    return parse_state_samples(chunk, model_name=model_name, topic=topic, frame_id=frame_id)


def has_timed_truth(sample: dict[str, Any]) -> bool:
    return sample.get("time_source") in {"header_stamp", "state_stats_sim_time"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic-name", default=DEFAULT_INPUT_TOPIC)
    parser.add_argument("--output-topic", default=DEFAULT_OUTPUT_TOPIC)
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--model-name", default="sunray150")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--target-altitude-m", type=float, default=1.2)
    parser.add_argument("--hover-command", type=float, default=0.05485)
    parser.add_argument("--kp-z", type=float, default=8.0e-5)
    parser.add_argument("--kd-z", type=float, default=3.0e-5)
    parser.add_argument("--ki-z", type=float, default=0.0)
    parser.add_argument("--kp-x", type=float, default=1.2e-4)
    parser.add_argument("--kd-x", type=float, default=2.0e-4)
    parser.add_argument("--kp-y", type=float, default=1.2e-4)
    parser.add_argument("--kd-y", type=float, default=2.0e-4)
    parser.add_argument("--kp-roll", type=float, default=0.018)
    parser.add_argument("--kd-roll", type=float, default=0.004)
    parser.add_argument("--kp-pitch", type=float, default=0.018)
    parser.add_argument("--kd-pitch", type=float, default=0.004)
    parser.add_argument("--kp-yaw", type=float, default=0.0)
    parser.add_argument("--kd-yaw", type=float, default=0.0)
    parser.add_argument("--attitude-command-limit", type=float, default=0.012)
    parser.add_argument("--xy-control-sign", type=float, choices=(-1.0, 1.0), default=-1.0)
    parser.add_argument("--roll-control-sign", type=float, choices=(-1.0, 1.0), default=None)
    parser.add_argument("--pitch-control-sign", type=float, choices=(-1.0, 1.0), default=None)
    parser.add_argument("--low-altitude-xy-scale-start-m", type=float, default=0.35)
    parser.add_argument("--low-altitude-xy-scale-full-m", type=float, default=0.85)
    parser.add_argument("--xy-error-limit-m", type=float, default=0.8)
    parser.add_argument("--xy-velocity-error-limit-mps", type=float, default=0.5)
    parser.add_argument("--integral-limit-m-s", type=float, default=1.0)
    parser.add_argument("--command-min", type=float, default=0.05480)
    parser.add_argument("--command-max", type=float, default=0.05490)
    parser.add_argument("--max-publish-hz", type=float, default=20.0)
    parser.add_argument("--duration-s", type=float, default=12.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    for field in [
        "target_altitude_m",
        "hover_command",
        "kp_z",
        "kd_z",
        "ki_z",
        "kp_x",
        "kd_x",
        "kp_y",
        "kd_y",
        "kp_roll",
        "kd_roll",
        "kp_pitch",
        "kd_pitch",
        "kp_yaw",
        "kd_yaw",
        "attitude_command_limit",
        "low_altitude_xy_scale_start_m",
        "low_altitude_xy_scale_full_m",
        "xy_error_limit_m",
        "xy_velocity_error_limit_mps",
        "integral_limit_m_s",
        "command_min",
        "command_max",
        "max_publish_hz",
        "duration_s",
    ]:
        finite(getattr(args, field), name=field)
    if args.command_min <= 0.0 or args.command_max > 1.0 or args.command_min >= args.command_max:
        raise ValueError("command bounds must satisfy 0 < command_min < command_max <= 1")
    if not (args.command_min <= args.hover_command <= args.command_max):
        raise ValueError("hover_command must be inside command bounds")
    if args.max_publish_hz <= 0.0:
        raise ValueError("max_publish_hz must be positive")
    if args.duration_s <= 0.0:
        raise ValueError("duration_s must be positive")
    if args.attitude_command_limit < 0.0:
        raise ValueError("attitude_command_limit must be non-negative")
    if args.low_altitude_xy_scale_start_m < 0.0:
        raise ValueError("low_altitude_xy_scale_start_m must be non-negative")
    if args.low_altitude_xy_scale_full_m <= args.low_altitude_xy_scale_start_m:
        raise ValueError("low_altitude_xy_scale_full_m must exceed low_altitude_xy_scale_start_m")
    if args.xy_error_limit_m <= 0.0 or args.xy_velocity_error_limit_mps <= 0.0:
        raise ValueError("XY error and velocity-error limits must be positive")


def write_json(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = project_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = project_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def dry_run_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": "mosim.gazebo_truth_hover_hold_controller.dry_run.v1",
        "status": "ready",
        "input_topic_name": args.input_topic_name,
        "output_topic": args.output_topic,
        "vehicle_id": args.vehicle_id,
        "model_name": args.model_name,
        "target_altitude_m": args.target_altitude_m,
        "hover_command": args.hover_command,
        "gains": {
            "kp_z": args.kp_z,
            "kd_z": args.kd_z,
            "ki_z": args.ki_z,
            "kp_x": args.kp_x,
            "kd_x": args.kd_x,
            "kp_y": args.kp_y,
            "kd_y": args.kd_y,
            "kp_roll": args.kp_roll,
            "kd_roll": args.kd_roll,
            "kp_pitch": args.kp_pitch,
            "kd_pitch": args.kd_pitch,
            "kp_yaw": args.kp_yaw,
            "kd_yaw": args.kd_yaw,
        },
        "attitude_command_limit": args.attitude_command_limit,
        "command_bounds": [args.command_min, args.command_max],
        "max_publish_hz": args.max_publish_hz,
        "duration_s": args.duration_s,
        "claim_boundary": [
            "dry-run only; no ROS2 graph was touched",
            "bounded altitude-hold pre-acceptance controller only",
            "no planner setpoint, trajectory tracking, controller performance, final closed_loop acceptance, or multi-UAV readiness is claimed",
        ],
    }


def run_controller(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput
        from rclpy.node import Node
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_truth_hover_hold_controller.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "claim_boundary": [
                "No ControllerOutput message was published.",
                "This blocker does not prove or disprove Gazebo, hover, closed_loop, or controller performance.",
            ],
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    class HoverHoldNode(Node):
        def __init__(self) -> None:
            super().__init__("mosim_gazebo_truth_hover_hold_controller")
            self.publisher = self.create_publisher(ControllerOutput, args.output_topic, 10)

    rclpy.init()
    node = HoverHoldNode()
    published_count = 0
    chunk_count = 0
    truth_sample_count = 0
    header_stamp_sample_count = 0
    synthetic_sample_count = 0
    skipped_by_rate = 0
    first_header_time: float | None = None
    last_header_time: float | None = None
    last_sample_time: float | None = None
    target_position: list[float] | None = None
    last_z: float | None = None
    last_position: list[float] | None = None
    last_roll: float | None = None
    last_pitch: float | None = None
    last_yaw: float | None = None
    target_yaw: float | None = None
    last_publish_wall = 0.0
    integral_error = 0.0
    min_z: float | None = None
    max_z: float | None = None
    max_xy_error = 0.0
    max_abs_yaw_error = 0.0
    min_command: float | None = None
    max_command: float | None = None
    last_trace: dict[str, Any] | None = None

    try:
        discovery_deadline = time.time() + 0.8
        while time.time() < discovery_deadline:
            rclpy.spin_once(node, timeout_sec=0.05)

        for chunk in iter_stdin_message_chunks(sys.stdin):
            chunk_count += 1
            samples = parse_truth_samples(
                chunk,
                model_name=args.model_name,
                topic=args.input_topic_name,
                frame_id=args.frame_id,
            )
            if not samples:
                continue
            for sample in samples:
                truth_sample_count += 1
                time_source = str(sample.get("time_source", ""))
                if has_timed_truth(sample):
                    header_stamp_sample_count += 1
                    sample_time = float(sample["time"])
                    if first_header_time is None:
                        first_header_time = sample_time
                    last_header_time = sample_time
                else:
                    synthetic_sample_count += 1
                    sample_time = float(sample.get("time", 0.0))

                position = [float(item) for item in sample["position_m"]]
                roll, pitch, yaw = sample_orientation(sample)
                timed_truth = has_timed_truth(sample)
                if target_yaw is None and timed_truth:
                    target_yaw = yaw
                if target_position is None and timed_truth:
                    target_position = [position[0], position[1], args.target_altitude_m]
                z = position[2]
                min_z = z if min_z is None else min(min_z, z)
                max_z = z if max_z is None else max(max_z, z)

                dt = 0.0
                vz = 0.0
                vx = 0.0
                vy = 0.0
                roll_rate = 0.0
                pitch_rate = 0.0
                yaw_rate = 0.0
                if (
                    timed_truth
                    and last_sample_time is not None
                    and last_position is not None
                    and sample_time > last_sample_time
                ):
                    dt = sample_time - last_sample_time
                    vx = (position[0] - last_position[0]) / dt
                    vy = (position[1] - last_position[1]) / dt
                    vz = (position[2] - last_position[2]) / dt
                    if last_roll is not None:
                        roll_rate = angle_wrap(roll - last_roll) / dt
                    if last_pitch is not None:
                        pitch_rate = angle_wrap(pitch - last_pitch) / dt
                    if last_yaw is not None:
                        yaw_rate = angle_wrap(yaw - last_yaw) / dt
                if timed_truth:
                    last_sample_time = sample_time
                    last_z = z
                    last_position = position
                    last_roll = roll
                    last_pitch = pitch
                    last_yaw = yaw

                z_error = args.target_altitude_m - z
                xy_target = target_position if target_position is not None else [position[0], position[1], args.target_altitude_m]
                x_error = xy_target[0] - position[0]
                y_error = xy_target[1] - position[1]
                xy_error = math.hypot(x_error, y_error)
                max_xy_error = max(max_xy_error, xy_error)
                if dt > 0.0:
                    integral_error = bounded(
                        integral_error + z_error * dt,
                        -abs(args.integral_limit_m_s),
                        abs(args.integral_limit_m_s),
                    )
                raw_command = (
                    args.hover_command
                    + args.kp_z * z_error
                    - args.kd_z * vz
                    + args.ki_z * integral_error
                )
                base_command = bounded(raw_command, args.command_min, args.command_max)
                yaw_error = angle_wrap((target_yaw if target_yaw is not None else 0.0) - yaw)
                max_abs_yaw_error = max(max_abs_yaw_error, abs(yaw_error))
                xy_control_scale = bounded(
                    (z - args.low_altitude_xy_scale_start_m)
                    / (args.low_altitude_xy_scale_full_m - args.low_altitude_xy_scale_start_m),
                    0.0,
                    1.0,
                )
                x_error_for_control = bounded(x_error, -args.xy_error_limit_m, args.xy_error_limit_m)
                y_error_for_control = bounded(y_error, -args.xy_error_limit_m, args.xy_error_limit_m)
                vx_error_for_control = bounded(-vx, -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps)
                vy_error_for_control = bounded(-vy, -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps)
                roll_control_sign = (
                    args.roll_control_sign if args.roll_control_sign is not None else args.xy_control_sign
                )
                pitch_control_sign = (
                    args.pitch_control_sign if args.pitch_control_sign is not None else args.xy_control_sign
                )
                desired_x = args.kp_x * x_error_for_control + args.kd_x * vx_error_for_control
                desired_y = args.kp_y * y_error_for_control + args.kd_y * vy_error_for_control
                roll_command = bounded(
                    xy_control_scale * roll_control_sign * desired_y
                    - args.kp_roll * roll
                    - args.kd_roll * roll_rate,
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                pitch_command = bounded(
                    xy_control_scale * pitch_control_sign * desired_x
                    - args.kp_pitch * pitch
                    - args.kd_pitch * pitch_rate,
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                yaw_command = bounded(
                    args.kp_yaw * yaw_error - args.kd_yaw * yaw_rate,
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                commands = [
                    bounded(
                        base_command
                        + ROLL_MIX[index] * roll_command
                        + PITCH_MIX[index] * pitch_command
                        + YAW_MIX[index] * yaw_command,
                        args.command_min,
                        args.command_max,
                    )
                    for index in range(4)
                ]

                now = time.time()
                if published_count > 0 and now - last_publish_wall < 1.0 / args.max_publish_hz:
                    skipped_by_rate += 1
                    continue

                message = ControllerOutput()
                message.header.stamp = node.get_clock().now().to_msg()
                message.header.frame_id = "body_motor_order_rotor_0_1_2_3"
                message.sequence = published_count + 1
                message.vehicle_id = args.vehicle_id
                message.command_type = "normalized_motor_speed"
                message.command = [float(command) for command in commands]
                message.command_frame = "body_motor_order_rotor_0_1_2_3"
                message.mode = "hover_hold_pre_acceptance"
                message.status = "valid"
                message.backend = "gazebo_truth_hover_hold_controller"
                message.saturation = raw_command != base_command or any(
                    command <= args.command_min or command >= args.command_max for command in commands
                )
                message.source_authority = "bounded_gazebo_truth_hover_hold_pre_acceptance"
                node.publisher.publish(message)
                rclpy.spin_once(node, timeout_sec=0.01)

                published_count += 1
                last_publish_wall = now
                min_command = min(commands) if min_command is None else min(min_command, min(commands))
                max_command = max(commands) if max_command is None else max(max_command, max(commands))
                trace = {
                    "schema": "mosim.gazebo_truth_hover_hold_controller_sample.v1",
                    "sequence": published_count,
                    "truth_seq": sample.get("seq"),
                    "truth_time_s": sample_time,
                    "truth_time_source": time_source,
                    "position_m": [round(value, 6) for value in position],
                    "target_position_m": [round(value, 6) for value in xy_target],
                    "position_error_m": [round(x_error, 6), round(y_error, 6), round(z_error, 6)],
                    "xy_error_m": round(xy_error, 6),
                    "velocity_mps": [round(vx, 6), round(vy, 6), round(vz, 6)],
                    "euler_rpy_rad": [round(roll, 6), round(pitch, 6), round(yaw, 6)],
                    "target_yaw_rad": round(target_yaw, 6) if target_yaw is not None else None,
                    "yaw_error_rad": round(yaw_error, 6),
                    "target_altitude_m": args.target_altitude_m,
                    "z_error_m": round(z_error, 6),
                    "vertical_velocity_m_s": round(vz, 6),
                    "angular_rate_rpy_rad_s": [round(roll_rate, 6), round(pitch_rate, 6), round(yaw_rate, 6)],
                    "integral_error_m_s": round(integral_error, 6),
                    "raw_command": round(raw_command, 9),
                    "base_command": round(base_command, 9),
                    "attitude_command": {
                        "roll": round(roll_command, 9),
                        "pitch": round(pitch_command, 9),
                        "yaw": round(yaw_command, 9),
                    },
                    "xy_control_scale": round(xy_control_scale, 6),
                    "command": [round(float(command), 9) for command in commands],
                    "saturation": message.saturation,
                    "published_at_unix": now,
                }
                last_trace = trace
                append_jsonl(args.trace_jsonl, trace)

                if first_header_time is not None and last_header_time is not None:
                    if last_header_time - first_header_time >= args.duration_s:
                        raise StopIteration
    except StopIteration:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    duration_s = (
        float(last_header_time - first_header_time)
        if first_header_time is not None and last_header_time is not None
        else 0.0
    )
    status = "completed" if published_count > 0 and header_stamp_sample_count > 0 else "blocked"
    report = {
        "schema": "mosim.gazebo_truth_hover_hold_controller.v1",
        "status": status,
        "input_topic_name": args.input_topic_name,
        "output_topic": args.output_topic,
        "vehicle_id": args.vehicle_id,
        "model_name": args.model_name,
        "target_altitude_m": args.target_altitude_m,
        "hover_command": args.hover_command,
        "gains": {
            "kp_z": args.kp_z,
            "kd_z": args.kd_z,
            "ki_z": args.ki_z,
            "kp_x": args.kp_x,
            "kd_x": args.kd_x,
            "kp_y": args.kp_y,
            "kd_y": args.kd_y,
            "kp_roll": args.kp_roll,
            "kd_roll": args.kd_roll,
            "kp_pitch": args.kp_pitch,
            "kd_pitch": args.kd_pitch,
            "kp_yaw": args.kp_yaw,
            "kd_yaw": args.kd_yaw,
        },
        "attitude_command_limit": args.attitude_command_limit,
        "command_bounds": [args.command_min, args.command_max],
        "counts": {
            "chunks": chunk_count,
            "truth_samples": truth_sample_count,
            "header_stamp_samples": header_stamp_sample_count,
            "synthetic_samples": synthetic_sample_count,
            "published": published_count,
            "skipped_by_rate": skipped_by_rate,
        },
        "duration_s": round(duration_s, 6),
        "z_range_m": {
            "min": round(min_z, 6) if min_z is not None else None,
            "max": round(max_z, 6) if max_z is not None else None,
        },
        "target_position_m": [round(value, 6) for value in target_position] if target_position is not None else None,
        "position_hold": {
            "max_xy_error_m": round(max_xy_error, 6),
            "max_abs_yaw_error_rad": round(max_abs_yaw_error, 6),
            "low_altitude_xy_scale_start_m": args.low_altitude_xy_scale_start_m,
            "low_altitude_xy_scale_full_m": args.low_altitude_xy_scale_full_m,
            "xy_error_limit_m": args.xy_error_limit_m,
            "xy_velocity_error_limit_mps": args.xy_velocity_error_limit_mps,
            "xy_control_sign": args.xy_control_sign,
            "roll_control_sign": args.roll_control_sign if args.roll_control_sign is not None else args.xy_control_sign,
            "pitch_control_sign": args.pitch_control_sign if args.pitch_control_sign is not None else args.xy_control_sign,
        },
        "command_range": {
            "min": round(min_command, 9) if min_command is not None else None,
            "max": round(max_command, 9) if max_command is not None else None,
        },
        "last_sample": last_trace,
        "outputs": {
            "trace_jsonl": rel(project_path(args.trace_jsonl)) if args.trace_jsonl else "",
        },
        "claim_boundary": [
            "This is a bounded Gazebo-truth altitude-hold pre-acceptance controller.",
            "It publishes ControllerOutput only; it does not publish planner setpoints or position_cmd.",
            "It does not prove trajectory tracking, controller performance, final closed_loop acceptance, or multi-UAV readiness.",
        ],
    }
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        validate_args(args)
        if args.dry_run:
            report = dry_run_report(args)
            write_json(args.output_json, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        return run_controller(args)
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_truth_hover_hold_controller.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(getattr(args, "output_json", None), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
