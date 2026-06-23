#!/usr/bin/env python3
"""Simple Gazebo truth-feedback takeoff-hover-land plant sanity controller."""

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


ROLL_MIX = [-1.0, 1.0, 1.0, -1.0]
PITCH_MIX = [-1.0, 1.0, -1.0, 1.0]
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
        return quaternion_to_euler_xyzw([float(item) for item in values])
    except (TypeError, ValueError):
        return 0.0, 0.0, 0.0


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


def target_altitude(
    elapsed: float,
    *,
    start_altitude: float,
    hover_altitude: float,
    takeoff_s: float,
    hover_s: float,
    land_s: float,
    landed_altitude: float,
) -> tuple[float, str]:
    if elapsed < takeoff_s:
        ratio = bounded(elapsed / takeoff_s, 0.0, 1.0)
        return start_altitude + ratio * (hover_altitude - start_altitude), "takeoff"
    if elapsed < takeoff_s + hover_s:
        return hover_altitude, "hover"
    if elapsed < takeoff_s + hover_s + land_s:
        ratio = bounded((elapsed - takeoff_s - hover_s) / land_s, 0.0, 1.0)
        return hover_altitude + ratio * (landed_altitude - hover_altitude), "land"
    return landed_altitude, "settle"


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
    parser.add_argument("--input-topic-name", default="/world/sunray150_single_uav_competition_light/dynamic_pose/info")
    parser.add_argument("--output-topic", default="/mosim/sunray150/controller_output")
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--hover-altitude-m", type=float, default=1.0)
    parser.add_argument("--landed-altitude-m", type=float, default=0.12)
    parser.add_argument("--takeoff-duration-s", type=float, default=6.0)
    parser.add_argument("--hover-duration-s", type=float, default=8.0)
    parser.add_argument("--land-duration-s", type=float, default=7.0)
    parser.add_argument("--settle-duration-s", type=float, default=2.0)
    parser.add_argument("--hover-command", type=float, default=0.0552)
    parser.add_argument("--kp-z", type=float, default=1.0e-3)
    parser.add_argument("--kd-z", type=float, default=2.0e-3)
    parser.add_argument("--ki-z", type=float, default=2.0e-4)
    parser.add_argument("--kp-x", type=float, default=1.2e-4)
    parser.add_argument("--kd-x", type=float, default=2.0e-4)
    parser.add_argument("--kp-y", type=float, default=1.2e-4)
    parser.add_argument("--kd-y", type=float, default=2.0e-4)
    parser.add_argument("--kp-roll", type=float, default=0.010)
    parser.add_argument("--kd-roll", type=float, default=0.002)
    parser.add_argument("--kp-pitch", type=float, default=0.010)
    parser.add_argument("--kd-pitch", type=float, default=0.002)
    parser.add_argument("--kp-yaw", type=float, default=0.0)
    parser.add_argument("--kd-yaw", type=float, default=0.0)
    parser.add_argument("--roll-control-sign", type=float, choices=(-1.0, 1.0), default=-1.0)
    parser.add_argument("--pitch-control-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--low-altitude-xy-scale-start-m", type=float, default=0.35)
    parser.add_argument("--low-altitude-xy-scale-full-m", type=float, default=0.85)
    parser.add_argument("--xy-error-limit-m", type=float, default=0.8)
    parser.add_argument("--xy-velocity-error-limit-mps", type=float, default=0.5)
    parser.add_argument("--integral-limit-m-s", type=float, default=1.0)
    parser.add_argument("--attitude-command-limit", type=float, default=0.002)
    parser.add_argument("--command-min", type=float, default=0.0528)
    parser.add_argument("--command-max", type=float, default=0.0562)
    parser.add_argument("--land-command-max", type=float, default=0.0552)
    parser.add_argument("--max-publish-hz", type=float, default=20.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    return parser.parse_args(argv)


def run_controller(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput
        from rclpy.node import Node
    except Exception as exc:
        report = {"schema": "mosim.gazebo_truth_takeoff_hover_land_controller.v1", "status": "blocked", "error": f"{type(exc).__name__}: {exc}"}
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    class Controller(Node):
        def __init__(self) -> None:
            super().__init__("mosim_gazebo_truth_takeoff_hover_land_controller")
            self.publisher = self.create_publisher(ControllerOutput, args.output_topic, 10)

    rclpy.init()
    node = Controller()
    published = 0
    skipped = 0
    chunks = 0
    truth_samples = 0
    header_samples = 0
    first_time: float | None = None
    last_time: float | None = None
    start_altitude: float | None = None
    target_xy: list[float] | None = None
    target_yaw: float | None = None
    last_position: list[float] | None = None
    last_roll: float | None = None
    last_pitch: float | None = None
    last_yaw: float | None = None
    last_sample_time: float | None = None
    last_publish_wall = 0.0
    integral_error = 0.0
    phase_counts: dict[str, int] = {}
    min_z: float | None = None
    max_z: float | None = None
    max_xy_error = 0.0
    max_tilt = 0.0
    min_command: float | None = None
    max_command: float | None = None
    total_duration = args.takeoff_duration_s + args.hover_duration_s + args.land_duration_s + args.settle_duration_s

    try:
        for chunk in iter_stdin_message_chunks(sys.stdin):
            chunks += 1
            samples = parse_truth_samples(chunk, model_name=args.model_name, topic=args.input_topic_name, frame_id=args.frame_id)
            for sample in samples:
                truth_samples += 1
                if not has_timed_truth(sample):
                    continue
                header_samples += 1
                sample_time = float(sample["time"])
                position = [float(item) for item in sample["position_m"]]
                roll, pitch, yaw = sample_orientation(sample)
                if first_time is None:
                    first_time = sample_time
                    start_altitude = position[2]
                    target_xy = [position[0], position[1]]
                    target_yaw = yaw
                last_time = sample_time
                elapsed = sample_time - first_time
                target_z, phase = target_altitude(
                    elapsed,
                    start_altitude=float(start_altitude),
                    hover_altitude=args.hover_altitude_m,
                    takeoff_s=args.takeoff_duration_s,
                    hover_s=args.hover_duration_s,
                    land_s=args.land_duration_s,
                    landed_altitude=args.landed_altitude_m,
                )
                phase_counts[phase] = phase_counts.get(phase, 0) + 1
                min_z = position[2] if min_z is None else min(min_z, position[2])
                max_z = position[2] if max_z is None else max(max_z, position[2])
                tilt = math.hypot(roll, pitch)
                max_tilt = max(max_tilt, tilt)
                dt = 0.0
                vx = vy = vz = 0.0
                roll_rate = pitch_rate = yaw_rate = 0.0
                if last_sample_time is not None and last_position is not None and sample_time > last_sample_time:
                    dt = sample_time - last_sample_time
                    vx = (position[0] - last_position[0]) / dt
                    vy = (position[1] - last_position[1]) / dt
                    vz = (position[2] - last_position[2]) / dt
                    roll_rate = angle_wrap(roll - (last_roll or 0.0)) / dt
                    pitch_rate = angle_wrap(pitch - (last_pitch or 0.0)) / dt
                    yaw_rate = angle_wrap(yaw - (last_yaw or 0.0)) / dt
                last_sample_time = sample_time
                last_position = position
                last_roll = roll
                last_pitch = pitch
                last_yaw = yaw

                z_error = target_z - position[2]
                if dt > 0.0 and phase != "settle":
                    integral_error = bounded(integral_error + z_error * dt, -abs(args.integral_limit_m_s), abs(args.integral_limit_m_s))
                elif phase == "settle":
                    integral_error = 0.0
                x_error = float(target_xy[0]) - position[0]
                y_error = float(target_xy[1]) - position[1]
                xy_error = math.hypot(x_error, y_error)
                max_xy_error = max(max_xy_error, xy_error)
                xy_scale = bounded((position[2] - args.low_altitude_xy_scale_start_m) / (args.low_altitude_xy_scale_full_m - args.low_altitude_xy_scale_start_m), 0.0, 1.0)
                desired_x = args.kp_x * bounded(x_error, -args.xy_error_limit_m, args.xy_error_limit_m) + args.kd_x * bounded(-vx, -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps)
                desired_y = args.kp_y * bounded(y_error, -args.xy_error_limit_m, args.xy_error_limit_m) + args.kd_y * bounded(-vy, -args.xy_velocity_error_limit_mps, args.xy_velocity_error_limit_mps)
                roll_command = bounded(xy_scale * args.roll_control_sign * desired_y - args.kp_roll * roll - args.kd_roll * roll_rate, -args.attitude_command_limit, args.attitude_command_limit)
                pitch_command = bounded(xy_scale * args.pitch_control_sign * desired_x - args.kp_pitch * pitch - args.kd_pitch * pitch_rate, -args.attitude_command_limit, args.attitude_command_limit)
                yaw_error = angle_wrap(float(target_yaw) - yaw)
                yaw_command = bounded(args.kp_yaw * yaw_error - args.kd_yaw * yaw_rate, -args.attitude_command_limit, args.attitude_command_limit)
                phase_command_max = min(args.command_max, args.land_command_max) if phase in {"land", "settle"} else args.command_max
                base_command = bounded(args.hover_command + args.kp_z * z_error - args.kd_z * vz + args.ki_z * integral_error, args.command_min, phase_command_max)
                commands = [
                    bounded(base_command + ROLL_MIX[i] * roll_command + PITCH_MIX[i] * pitch_command + YAW_MIX[i] * yaw_command, args.command_min, phase_command_max)
                    for i in range(4)
                ]
                now = time.time()
                if published > 0 and now - last_publish_wall < 1.0 / args.max_publish_hz:
                    skipped += 1
                    continue
                message = ControllerOutput()
                message.header.stamp = node.get_clock().now().to_msg()
                message.header.frame_id = "body_motor_order_rotor_0_1_2_3"
                message.sequence = published + 1
                message.vehicle_id = args.vehicle_id
                message.command_type = "normalized_motor_speed"
                message.command = [float(item) for item in commands]
                message.command_frame = "body_motor_order_rotor_0_1_2_3"
                message.mode = f"takeoff_hover_land_{phase}"
                message.status = "valid"
                message.backend = "gazebo_truth_takeoff_hover_land_controller"
                message.saturation = any(command <= args.command_min or command >= phase_command_max for command in commands)
                message.source_authority = "bounded_gazebo_truth_takeoff_hover_land_plant_sanity"
                node.publisher.publish(message)
                rclpy.spin_once(node, timeout_sec=0.01)
                published += 1
                last_publish_wall = now
                min_command = min(commands) if min_command is None else min(min_command, min(commands))
                max_command = max(commands) if max_command is None else max(max_command, max(commands))
                append_jsonl(
                    args.trace_jsonl,
                    {
                        "schema": "mosim.gazebo_truth_takeoff_hover_land_controller_sample.v1",
                        "sequence": published,
                        "truth_time_s": round(sample_time, 6),
                        "elapsed_s": round(elapsed, 6),
                        "phase": phase,
                        "position_m": [round(item, 6) for item in position],
                        "target_position_m": [round(float(target_xy[0]), 6), round(float(target_xy[1]), 6), round(target_z, 6)],
                        "position_error_m": [round(x_error, 6), round(y_error, 6), round(z_error, 6)],
                        "velocity_mps": [round(vx, 6), round(vy, 6), round(vz, 6)],
                        "euler_rpy_rad": [round(roll, 6), round(pitch, 6), round(yaw, 6)],
                        "base_command": round(base_command, 9),
                        "command": [round(item, 9) for item in commands],
                    },
                )
                if elapsed >= total_duration:
                    raise StopIteration
    except StopIteration:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    duration = 0.0 if first_time is None or last_time is None else last_time - first_time
    status = "completed" if published > 0 and header_samples > 0 else "blocked"
    report = {
        "schema": "mosim.gazebo_truth_takeoff_hover_land_controller.v1",
        "status": status,
        "input_topic_name": args.input_topic_name,
        "output_topic": args.output_topic,
        "model_name": args.model_name,
        "vehicle_id": args.vehicle_id,
        "profile": {
            "hover_altitude_m": args.hover_altitude_m,
            "landed_altitude_m": args.landed_altitude_m,
            "takeoff_duration_s": args.takeoff_duration_s,
            "hover_duration_s": args.hover_duration_s,
            "land_duration_s": args.land_duration_s,
            "settle_duration_s": args.settle_duration_s,
        },
        "counts": {
            "chunks": chunks,
            "truth_samples": truth_samples,
            "header_stamp_samples": header_samples,
            "published": published,
            "skipped_by_rate": skipped,
            "phase_counts": phase_counts,
        },
        "duration_s": round(duration, 6),
        "z_range_m": {"min": round(min_z, 6) if min_z is not None else None, "max": round(max_z, 6) if max_z is not None else None},
        "max_xy_error_m": round(max_xy_error, 6),
        "max_tilt_rad": round(max_tilt, 6),
        "command_range": {"min": round(min_command, 9) if min_command is not None else None, "max": round(max_command, 9) if max_command is not None else None},
        "outputs": {"trace_jsonl": rel(project_path(args.trace_jsonl)) if args.trace_jsonl else ""},
        "claim_boundary": [
            "bounded Gazebo plant sanity controller only",
            "proves neither competition controller performance nor MWORKS controller deployment",
        ],
    }
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


def main(argv: list[str]) -> int:
    return run_controller(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
