#!/usr/bin/env python3
"""Bounded Gazebo-truth planner-setpoint tracker.

This node is a narrow single-UAV pre-acceptance bridge:

Gazebo truth pose + /mosim/planner/setpoint -> ControllerOutput

It is not a production controller, does not arm a vehicle, and must not be used
to claim final closed-loop or controller-performance acceptance.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
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


# Rotor order and positions in Config/gazebo/models/sunray150_assembled/model.sdf:
# 0 front-right, 1 back-left, 2 front-left, 3 back-right.
ROLL_MIX = [-1.0, 1.0, 1.0, -1.0]
PITCH_MIX = [-1.0, 1.0, -1.0, 1.0]
# Current sunray150_assembled Gazebo motor-axis probes showed this sign is the
# stable yaw-correction direction for the ccw/ccw/cw/cw rotor convention.
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
        quaternion = [float(item) for item in values]
    except (TypeError, ValueError):
        return 0.0, 0.0, 0.0
    if not all(math.isfinite(item) for item in quaternion):
        return 0.0, 0.0, 0.0
    return quaternion_to_euler_xyzw(quaternion)


def iter_stdin_message_chunks(lines: Iterable[str]) -> Iterable[str]:
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic-name", default="/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info")
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--truth-frame-id", default="world")
    parser.add_argument("--setpoint-topic", default="/mosim/planner/setpoint")
    parser.add_argument("--output-topic", default="/mosim/sunray150/controller_output")
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--expected-frame", default="map")
    parser.add_argument("--internal-figure8-reference", action="store_true")
    parser.add_argument("--figure8-period-s", type=float, default=20.0)
    parser.add_argument("--figure8-x-amplitude-m", type=float, default=2.4)
    parser.add_argument("--figure8-y-amplitude-m", type=float, default=2.8)
    parser.add_argument("--figure8-altitude-m", type=float, default=1.2)
    parser.add_argument("--figure8-start-delay-s", type=float, default=0.0)
    parser.add_argument("--figure8-time-scale", type=float, default=1.0)
    parser.add_argument("--hover-command", type=float, default=0.05470)
    parser.add_argument("--kp-x", type=float, default=1.2e-4)
    parser.add_argument("--kd-x", type=float, default=2.0e-4)
    parser.add_argument("--kp-y", type=float, default=1.2e-4)
    parser.add_argument("--kd-y", type=float, default=2.0e-4)
    parser.add_argument("--kp-z", type=float, default=2.0e-4)
    parser.add_argument("--kd-z", type=float, default=8.0e-4)
    parser.add_argument("--ki-z", type=float, default=0.0)
    parser.add_argument("--kp-roll", type=float, default=0.003)
    parser.add_argument("--kd-roll", type=float, default=0.0008)
    parser.add_argument("--kp-pitch", type=float, default=0.003)
    parser.add_argument("--kd-pitch", type=float, default=0.0008)
    parser.add_argument("--kp-yaw", type=float, default=0.0)
    parser.add_argument("--kd-yaw", type=float, default=0.0)
    parser.add_argument("--attitude-command-limit", type=float, default=0.002)
    parser.add_argument("--low-altitude-xy-scale-start-m", type=float, default=0.35)
    parser.add_argument("--low-altitude-xy-scale-full-m", type=float, default=0.85)
    parser.add_argument("--takeoff-xy-enable-altitude-m", type=float, default=0.9)
    parser.add_argument("--takeoff-stable-z-error-m", type=float, default=0.25)
    parser.add_argument("--takeoff-stable-s", type=float, default=0.8)
    parser.add_argument("--xy-error-limit-m", type=float, default=0.8)
    parser.add_argument("--xy-velocity-error-limit-mps", type=float, default=0.5)
    parser.add_argument("--integral-limit-m-s", type=float, default=1.0)
    parser.add_argument("--command-min", type=float, default=0.05250)
    parser.add_argument("--command-max", type=float, default=0.05750)
    parser.add_argument("--setpoint-timeout-s", type=float, default=0.35)
    parser.add_argument("--max-publish-hz", type=float, default=20.0)
    parser.add_argument("--duration-s", type=float, default=12.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    parser.add_argument("--poll-command", default="")
    parser.add_argument("--poll-sleep-s", type=float, default=0.05)
    parser.add_argument("--poll-sample-timeout-s", type=float, default=1.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    for key, value in vars(args).items():
        if key.endswith(("_command", "_x", "_y", "_z", "_roll", "_pitch", "_yaw", "_s", "_hz", "_min", "_max", "_limit")):
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"{key} must be finite")
    if not (0.0 < args.command_min < args.command_max <= 1.0):
        raise ValueError("command bounds must satisfy 0 < command_min < command_max <= 1")
    if not (args.command_min <= args.hover_command <= args.command_max):
        raise ValueError("hover_command must be within command bounds")
    if args.setpoint_timeout_s <= 0.0 or args.max_publish_hz <= 0.0 or args.duration_s <= 0.0:
        raise ValueError("timeouts, rates, and duration must be positive")
    if args.low_altitude_xy_scale_start_m < 0.0:
        raise ValueError("low-altitude XY scale start must be non-negative")
    if args.low_altitude_xy_scale_full_m <= args.low_altitude_xy_scale_start_m:
        raise ValueError("low-altitude XY scale full threshold must exceed start threshold")
    if args.takeoff_xy_enable_altitude_m < args.low_altitude_xy_scale_start_m:
        raise ValueError("takeoff XY enable altitude must not be below low-altitude XY scale start")
    if args.takeoff_stable_z_error_m <= 0.0 or args.takeoff_stable_s < 0.0:
        raise ValueError("takeoff stable z error must be positive and stable time must be non-negative")
    if args.xy_error_limit_m <= 0.0 or args.xy_velocity_error_limit_mps <= 0.0:
        raise ValueError("XY error and velocity-error limits must be positive")
    if args.integral_limit_m_s < 0.0:
        raise ValueError("integral limit must be non-negative")
    if args.internal_figure8_reference:
        if args.figure8_period_s <= 0.0 or args.figure8_time_scale <= 0.0:
            raise ValueError("figure8 period and time scale must be positive")
        for key in ("figure8_x_amplitude_m", "figure8_y_amplitude_m", "figure8_altitude_m", "figure8_start_delay_s"):
            value = float(getattr(args, key))
            if not math.isfinite(value):
                raise ValueError(f"{key} must be finite")


def dry_run_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": "mosim.gazebo_truth_planner_setpoint_tracker.dry_run.v1",
        "status": "ready",
        "input_truth_topic": args.input_topic_name,
        "setpoint_topic": args.setpoint_topic,
        "output_topic": args.output_topic,
        "expected_frame": args.expected_frame,
        "vehicle_id": args.vehicle_id,
        "duration_s": args.duration_s,
        "setpoint_timeout_s": args.setpoint_timeout_s,
        "poll_command": args.poll_command,
        "reference_mode": "internal_figure8" if args.internal_figure8_reference else "ros_planner_setpoint",
        "claim_boundary": [
            "dry-run only; no ROS2 graph or Gazebo stream was touched",
            "single-UAV planner-setpoint tracking pre-acceptance bridge only",
            "no final closed_loop, controller performance, planner_ready, or multi-UAV readiness is claimed",
        ],
    }


def figure8_state(t: float, *, x_amp: float, y_amp: float, z_m: float, period_s: float) -> dict[str, Any]:
    omega = 2.0 * math.pi / period_s
    s = math.sin(omega * t)
    c = math.cos(omega * t)
    x = x_amp * s
    y = y_amp * s * c
    vx = x_amp * omega * c
    vy = y_amp * omega * (c * c - s * s)
    ax = -x_amp * omega * omega * s
    ay = -4.0 * y_amp * omega * omega * s * c
    yaw = math.atan2(vy, vx) if abs(vx) + abs(vy) > 1e-9 else 0.0
    return {
        "position": [x, y, z_m],
        "velocity": [vx, vy, 0.0],
        "acceleration": [ax, ay, 0.0],
        "yaw": yaw,
        "yaw_rate": 0.0,
    }


def iter_truth_chunks(args: argparse.Namespace) -> Iterable[str]:
    if not args.poll_command:
        yield from iter_stdin_message_chunks(sys.stdin)
        return
    deadline = time.monotonic() + float(args.duration_s) + float(args.setpoint_timeout_s) + 2.0
    while time.monotonic() < deadline:
        try:
            completed = subprocess.run(
                [args.poll_command, "topic", "-e", "-t", args.input_topic_name, "-n", "1"],
                check=False,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=max(0.1, float(args.poll_sample_timeout_s)),
            )
        except subprocess.TimeoutExpired:
            time.sleep(max(0.0, float(args.poll_sleep_s)))
            continue
        if completed.stdout.strip():
            yield completed.stdout
        time.sleep(max(0.0, float(args.poll_sleep_s)))


def run_tracker(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput, PlannerSetpoint
        from rclpy.node import Node
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_truth_planner_setpoint_tracker.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "claim_boundary": ["No ControllerOutput message was published."],
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    class TrackerNode(Node):
        def __init__(self) -> None:
            super().__init__("mosim_gazebo_truth_planner_setpoint_tracker")
            self.publisher = self.create_publisher(ControllerOutput, args.output_topic, 10)
            self.subscription = self.create_subscription(PlannerSetpoint, args.setpoint_topic, self.on_setpoint, 10)
            self.latest_setpoint: PlannerSetpoint | None = None
            self.latest_setpoint_wall = 0.0
            self.accepted_setpoints = 0
            self.rejected_setpoints = 0
            self.internal_setpoints = 0

        def on_setpoint(self, message: PlannerSetpoint) -> None:
            if message.frame_id != args.expected_frame:
                self.rejected_setpoints += 1
                return
            values = list(message.position_m) + list(message.velocity_mps) + list(message.acceleration_mps2)
            values += [message.yaw_rad, message.yaw_rate_radps]
            if not all(math.isfinite(float(item)) for item in values):
                self.rejected_setpoints += 1
                return
            self.latest_setpoint = message
            self.latest_setpoint_wall = time.time()
            self.accepted_setpoints += 1

        def internal_setpoint(self, sample_time: float, start_time: float) -> Any:
            state = figure8_state(
                max(0.0, (sample_time - start_time) * args.figure8_time_scale - args.figure8_start_delay_s),
                x_amp=args.figure8_x_amplitude_m,
                y_amp=args.figure8_y_amplitude_m,
                z_m=args.figure8_altitude_m,
                period_s=args.figure8_period_s,
            )
            self.internal_setpoints += 1
            return {
                "sequence": self.internal_setpoints,
                "position_m": state["position"],
                "velocity_mps": state["velocity"],
                "acceleration_mps2": state["acceleration"],
                "yaw_rad": state["yaw"],
                "yaw_rate_radps": state["yaw_rate"],
                "age_s": 0.0,
            }

    rclpy.init()
    node = TrackerNode()
    published_count = 0
    truth_sample_count = 0
    header_stamp_sample_count = 0
    skipped_no_setpoint = 0
    skipped_stale_setpoint = 0
    skipped_by_rate = 0
    first_header_time: float | None = None
    last_header_time: float | None = None
    last_sample_time: float | None = None
    last_position: list[float] | None = None
    last_roll: float | None = None
    last_pitch: float | None = None
    last_yaw: float | None = None
    last_publish_wall = 0.0
    min_z: float | None = None
    max_z: float | None = None
    max_xy_error = 0.0
    max_z_error = 0.0
    last_trace: dict[str, Any] | None = None
    xy_tracking_enabled = False
    altitude_stable_since: float | None = None
    control_phase_counts: dict[str, int] = {}
    integral_z_error = 0.0

    try:
        discovery_deadline = time.time() + 0.8
        while time.time() < discovery_deadline:
            rclpy.spin_once(node, timeout_sec=0.05)

        for chunk in iter_truth_chunks(args):
            samples = parse_truth_samples(
                chunk,
                model_name=args.model_name,
                topic=args.input_topic_name,
                frame_id=args.truth_frame_id,
            )
            if not samples:
                continue
            for sample in samples:
                rclpy.spin_once(node, timeout_sec=0.0)
                truth_sample_count += 1
                if not has_timed_truth(sample):
                    continue
                header_stamp_sample_count += 1
                sample_time = float(sample["time"])
                if first_header_time is None:
                    first_header_time = sample_time
                last_header_time = sample_time
                position = [float(item) for item in sample["position_m"]]
                min_z = position[2] if min_z is None else min(min_z, position[2])
                max_z = position[2] if max_z is None else max(max_z, position[2])
                roll, pitch, yaw = sample_orientation(sample)

                dt = 0.0
                velocity = [0.0, 0.0, 0.0]
                roll_rate = 0.0
                pitch_rate = 0.0
                yaw_rate = 0.0
                if last_sample_time is not None and last_position is not None and sample_time > last_sample_time:
                    dt = sample_time - last_sample_time
                    velocity = [(position[i] - last_position[i]) / dt for i in range(3)]
                    if last_roll is not None:
                        roll_rate = angle_wrap(roll - last_roll) / dt
                    if last_pitch is not None:
                        pitch_rate = angle_wrap(pitch - last_pitch) / dt
                    if last_yaw is not None:
                        yaw_rate = angle_wrap(yaw - last_yaw) / dt
                last_sample_time = sample_time
                last_position = position
                last_roll = roll
                last_pitch = pitch
                last_yaw = yaw

                if args.internal_figure8_reference:
                    setpoint = node.internal_setpoint(sample_time, first_header_time)
                    setpoint_age = float(setpoint["age_s"])
                    target_position = [float(item) for item in setpoint["position_m"]]
                    target_velocity = [float(item) for item in setpoint["velocity_mps"]]
                    setpoint_sequence = int(setpoint["sequence"])
                    setpoint_yaw = float(setpoint["yaw_rad"])
                    setpoint_yaw_rate = float(setpoint["yaw_rate_radps"])
                else:
                    setpoint = node.latest_setpoint
                    if setpoint is None:
                        skipped_no_setpoint += 1
                        continue
                    setpoint_age = time.time() - node.latest_setpoint_wall
                    if setpoint_age > args.setpoint_timeout_s:
                        skipped_stale_setpoint += 1
                        continue
                    target_position = [float(item) for item in setpoint.position_m]
                    target_velocity = [float(item) for item in setpoint.velocity_mps]
                    setpoint_sequence = int(setpoint.sequence)
                    setpoint_yaw = float(setpoint.yaw_rad)
                    setpoint_yaw_rate = float(setpoint.yaw_rate_radps)
                now = time.time()
                if published_count > 0 and now - last_publish_wall < 1.0 / args.max_publish_hz:
                    skipped_by_rate += 1
                    continue

                error = [target_position[i] - position[i] for i in range(3)]
                velocity_error = [target_velocity[i] - velocity[i] for i in range(3)]
                xy_error = math.hypot(error[0], error[1])
                z_error = error[2]
                if dt > 0.0:
                    integral_z_error = bounded(
                        integral_z_error + z_error * dt,
                        -abs(args.integral_limit_m_s),
                        abs(args.integral_limit_m_s),
                    )
                max_xy_error = max(max_xy_error, xy_error)
                max_z_error = max(max_z_error, abs(z_error))
                altitude_xy_scale = bounded(
                    (position[2] - args.low_altitude_xy_scale_start_m)
                    / (args.low_altitude_xy_scale_full_m - args.low_altitude_xy_scale_start_m),
                    0.0,
                    1.0,
                )
                altitude_is_stable = (
                    position[2] >= args.takeoff_xy_enable_altitude_m
                    and abs(z_error) <= args.takeoff_stable_z_error_m
                )
                if altitude_is_stable:
                    if altitude_stable_since is None:
                        altitude_stable_since = sample_time
                    if sample_time - altitude_stable_since >= args.takeoff_stable_s:
                        xy_tracking_enabled = True
                else:
                    altitude_stable_since = None

                if position[2] <= args.low_altitude_xy_scale_start_m:
                    xy_tracking_enabled = False

                control_phase = "xy_track" if xy_tracking_enabled else "takeoff_altitude_hold"
                if position[2] <= args.low_altitude_xy_scale_start_m:
                    control_phase = "altitude_recovery"
                control_phase_counts[control_phase] = control_phase_counts.get(control_phase, 0) + 1
                phase_xy_scale = 1.0 if control_phase == "xy_track" else 0.0
                xy_control_scale = altitude_xy_scale * phase_xy_scale
                xy_error_for_control = [
                    bounded(error[0], -args.xy_error_limit_m, args.xy_error_limit_m),
                    bounded(error[1], -args.xy_error_limit_m, args.xy_error_limit_m),
                ]
                xy_velocity_error_for_control = [
                    bounded(velocity_error[0], -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps),
                    bounded(velocity_error[1], -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps),
                ]

                base_command = bounded(
                    args.hover_command
                    + args.kp_z * z_error
                    + args.kd_z * velocity_error[2]
                    + args.ki_z * integral_z_error,
                    args.command_min,
                    args.command_max,
                )
                # Axis probes on sunray150_assembled show positive roll
                # differential moves the plant toward -Y, while the current
                # pre-acceptance plant traces require the same inverted
                # position mapping on X to avoid runaway after ground contact.
                roll_command = bounded(
                    xy_control_scale
                    * (-args.kp_y * xy_error_for_control[1] - args.kd_y * xy_velocity_error_for_control[1])
                    - args.kp_roll * roll
                    - args.kd_roll * roll_rate,
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                pitch_command = bounded(
                    xy_control_scale
                    * (-args.kp_x * xy_error_for_control[0] - args.kd_x * xy_velocity_error_for_control[0])
                    - args.kp_pitch * pitch
                    - args.kd_pitch * pitch_rate,
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                yaw_error = angle_wrap(setpoint_yaw - yaw)
                yaw_command = bounded(
                    args.kp_yaw * yaw_error + args.kd_yaw * (setpoint_yaw_rate - yaw_rate),
                    -args.attitude_command_limit,
                    args.attitude_command_limit,
                )
                commands = [
                    bounded(
                        base_command
                        + ROLL_MIX[i] * roll_command
                        + PITCH_MIX[i] * pitch_command
                        + YAW_MIX[i] * yaw_command,
                        args.command_min,
                        args.command_max,
                    )
                    for i in range(4)
                ]

                message = ControllerOutput()
                message.header.stamp = node.get_clock().now().to_msg()
                message.header.frame_id = "body_motor_order_rotor_0_1_2_3"
                message.sequence = published_count + 1
                message.vehicle_id = args.vehicle_id
                message.command_type = "normalized_motor_speed"
                message.command = [float(command) for command in commands]
                message.command_frame = "body_motor_order_rotor_0_1_2_3"
                message.mode = "planner_setpoint_track_pre_acceptance"
                message.status = "valid"
                message.backend = "gazebo_truth_planner_setpoint_tracker"
                message.saturation = any(command <= args.command_min or command >= args.command_max for command in commands)
                message.source_authority = "bounded_gazebo_truth_planner_setpoint_tracker"
                node.publisher.publish(message)
                rclpy.spin_once(node, timeout_sec=0.01)
                published_count += 1
                last_publish_wall = now

                last_trace = {
                    "schema": "mosim.gazebo_truth_planner_setpoint_tracker_sample.v1",
                    "sequence": published_count,
                    "truth_time_s": sample_time,
                    "position_m": [round(item, 6) for item in position],
                    "target_position_m": [round(item, 6) for item in target_position],
                    "position_error_m": [round(item, 6) for item in error],
                    "xy_error_m": round(xy_error, 6),
                    "z_error_m": round(z_error, 6),
                    "setpoint_sequence": setpoint_sequence,
                    "setpoint_age_s": round(setpoint_age, 6),
                    "reference_mode": "internal_figure8" if args.internal_figure8_reference else "ros_planner_setpoint",
                    "command": [round(float(command), 9) for command in commands],
                    "saturation": bool(message.saturation),
                    "integral_z_error_m_s": round(integral_z_error, 6),
                    "xy_control_scale": round(xy_control_scale, 6),
                    "altitude_xy_scale": round(altitude_xy_scale, 6),
                    "control_phase": control_phase,
                    "xy_tracking_enabled": bool(xy_tracking_enabled),
                    "xy_error_for_control_m": [round(item, 6) for item in xy_error_for_control],
                    "xy_velocity_error_for_control_mps": [
                        round(item, 6) for item in xy_velocity_error_for_control
                    ],
                }
                append_jsonl(args.trace_jsonl, last_trace)

                if first_header_time is not None:
                    if sample_time - first_header_time >= args.duration_s:
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
    blockers: list[str] = []
    if not args.internal_figure8_reference and node.accepted_setpoints <= 0:
        blockers.append("no_valid_planner_setpoint_received")
    if published_count <= 0:
        blockers.append("no_controller_output_published")
    if header_stamp_sample_count <= 0:
        blockers.append("no_header_stamp_truth_samples")
    status = "completed" if not blockers else "blocked"
    report = {
        "schema": "mosim.gazebo_truth_planner_setpoint_tracker.v1",
        "status": status,
        "input_truth_topic": args.input_topic_name,
        "setpoint_topic": args.setpoint_topic,
        "output_topic": args.output_topic,
        "vehicle_id": args.vehicle_id,
        "expected_frame": args.expected_frame,
        "reference_mode": "internal_figure8" if args.internal_figure8_reference else "ros_planner_setpoint",
        "internal_figure8_reference": {
            "enabled": bool(args.internal_figure8_reference),
            "period_s": args.figure8_period_s,
            "x_amplitude_m": args.figure8_x_amplitude_m,
            "y_amplitude_m": args.figure8_y_amplitude_m,
            "altitude_m": args.figure8_altitude_m,
            "start_delay_s": args.figure8_start_delay_s,
            "time_scale": args.figure8_time_scale,
        },
        "counts": {
            "truth_samples": truth_sample_count,
            "header_stamp_samples": header_stamp_sample_count,
            "accepted_setpoints": node.accepted_setpoints,
            "rejected_setpoints": node.rejected_setpoints,
            "internal_setpoints": node.internal_setpoints,
            "published": published_count,
            "skipped_no_setpoint": skipped_no_setpoint,
            "skipped_stale_setpoint": skipped_stale_setpoint,
            "skipped_by_rate": skipped_by_rate,
        },
        "duration_s": round(duration_s, 6),
        "z_range_m": {
            "min": round(min_z, 6) if min_z is not None else None,
            "max": round(max_z, 6) if max_z is not None else None,
        },
        "tracking_errors": {
            "max_xy_error_m": round(max_xy_error, 6),
            "max_abs_z_error_m": round(max_z_error, 6),
        },
        "control_phase_counts": control_phase_counts,
        "control_guards": {
            "takeoff_xy_enable_altitude_m": args.takeoff_xy_enable_altitude_m,
            "takeoff_stable_z_error_m": args.takeoff_stable_z_error_m,
            "takeoff_stable_s": args.takeoff_stable_s,
            "low_altitude_xy_scale_start_m": args.low_altitude_xy_scale_start_m,
            "low_altitude_xy_scale_full_m": args.low_altitude_xy_scale_full_m,
            "xy_error_limit_m": args.xy_error_limit_m,
            "xy_velocity_error_limit_mps": args.xy_velocity_error_limit_mps,
            "integral_limit_m_s": args.integral_limit_m_s,
        },
        "last_sample": last_trace,
        "blockers": blockers,
        "outputs": {
            "trace_jsonl": rel(project_path(args.trace_jsonl)) if args.trace_jsonl else "",
        },
        "claim_boundary": [
            "bounded single-UAV Gazebo truth-feedback planner-setpoint tracking pre-acceptance only",
            "ControllerOutput is published only from valid, fresh /mosim/planner/setpoint samples",
            "no final closed_loop, competition controller performance, planner_ready, or multi-UAV readiness is claimed",
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
        return run_tracker(args)
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_truth_planner_setpoint_tracker.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(getattr(args, "output_json", None), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
