#!/usr/bin/env python3
"""Publish a bounded single-UAV figure-8 PositionCommand stream.

The generated path is a horizontal figure-8 around the light Gazebo obstacle
field. It is a mission/reference publisher, not a planner acceptance claim by
itself.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROS_LOG_DIR = ROOT / "Results" / "tmp" / "ros_logs"
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


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


def ensure_ros_log_dir() -> None:
    log_dir = Path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    resolved = project_path(log_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(resolved)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    output = project_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    output = project_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def make_stamp(stamp_type: Any, stamp_ns: int) -> Any:
    stamp = stamp_type()
    stamp.sec = int(stamp_ns // 1_000_000_000)
    stamp.nanosec = int(stamp_ns % 1_000_000_000)
    return stamp


def figure8_state(
    t: float,
    *,
    x_amp: float,
    y_amp: float,
    z_m: float,
    period_s: float,
    x_offset_m: float = 0.0,
    y_offset_m: float = 0.0,
) -> dict[str, Any]:
    omega = 2.0 * math.pi / period_s
    s = math.sin(omega * t)
    c = math.cos(omega * t)
    x = x_offset_m + x_amp * s
    y = y_offset_m + y_amp * s * c
    vx = x_amp * omega * c
    vy = y_amp * omega * (c * c - s * s)
    ax = -x_amp * omega * omega * s
    ay = -4.0 * y_amp * omega * omega * s * c
    return {
        "position": [x, y, z_m],
        "velocity": [vx, vy, 0.0],
        "acceleration": [ax, ay, 0.0],
        "yaw": 0.0,
        "yaw_dot": 0.0,
    }


def smoothstep(value: float) -> tuple[float, float, float]:
    u = max(0.0, min(1.0, value))
    position = u * u * (3.0 - 2.0 * u)
    velocity = 6.0 * u * (1.0 - u)
    acceleration = 6.0 - 12.0 * u
    return position, velocity, acceleration


def vertical_ramp_state(
    t: float,
    *,
    duration_s: float,
    x_m: float,
    y_m: float,
    start_z_m: float,
    end_z_m: float,
    yaw_rad: float = 0.0,
) -> dict[str, Any]:
    if duration_s <= 0.0:
        return hold_state(x_m=x_m, y_m=y_m, z_m=end_z_m, yaw_rad=yaw_rad)
    u = t / duration_s
    s, ds_du, d2s_du2 = smoothstep(u)
    dz = end_z_m - start_z_m
    return {
        "position": [x_m, y_m, start_z_m + dz * s],
        "velocity": [0.0, 0.0, dz * ds_du / duration_s],
        "acceleration": [0.0, 0.0, dz * d2s_du2 / (duration_s * duration_s)],
        "yaw": yaw_rad,
        "yaw_dot": 0.0,
    }


def hold_state(
    *,
    x_m: float,
    y_m: float,
    z_m: float,
    yaw_rad: float = 0.0,
) -> dict[str, Any]:
    return {
        "position": [x_m, y_m, z_m],
        "velocity": [0.0, 0.0, 0.0],
        "acceleration": [0.0, 0.0, 0.0],
        "yaw": yaw_rad,
        "yaw_dot": 0.0,
    }


def parse_obstacle(raw: str) -> tuple[float, float, float]:
    parts = [float(item) for item in raw.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("obstacle must be x,y,radius")
    if not all(math.isfinite(item) for item in parts) or parts[2] <= 0.0:
        raise argparse.ArgumentTypeError("obstacle values must be finite and radius positive")
    return parts[0], parts[1], parts[2]


def clearance_xy(position: list[float], obstacles: list[tuple[float, float, float]]) -> float | None:
    if not obstacles:
        return None
    x, y = position[0], position[1]
    return min(math.hypot(x - ox, y - oy) - radius for ox, oy, radius in obstacles)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="/position_cmd")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--planner-id", default="mosim_figure8_static_obstacle_reference")
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--duration-s", type=float, default=30.0)
    parser.add_argument("--period-s", type=float, default=20.0)
    parser.add_argument("--x-amplitude-m", type=float, default=2.4)
    parser.add_argument("--y-amplitude-m", type=float, default=2.8)
    parser.add_argument("--x-offset-m", type=float, default=0.0)
    parser.add_argument("--y-offset-m", type=float, default=0.0)
    parser.add_argument("--altitude-m", type=float, default=1.2)
    parser.add_argument("--start-delay-s", type=float, default=0.0)
    parser.add_argument("--takeoff-s", type=float, default=0.0)
    parser.add_argument("--hold-s", type=float, default=0.0)
    parser.add_argument("--post-figure8-hold-s", type=float, default=0.0)
    parser.add_argument("--land-s", type=float, default=0.0)
    parser.add_argument("--final-hold-s", type=float, default=0.0)
    parser.add_argument("--ground-altitude-m", type=float, default=0.05)
    parser.add_argument(
        "--truth-sync-stdin",
        action="store_true",
        help="Advance the mission clock from Gazebo truth samples on stdin instead of wall time.",
    )
    parser.add_argument("--truth-sync-model-name", default="sunray150_assembled")
    parser.add_argument("--truth-sync-topic", default="")
    parser.add_argument("--truth-sync-frame-id", default="world")
    parser.add_argument(
        "--truth-sync-epoch-s",
        type=float,
        default=None,
        help="Use truth_time - epoch as mission elapsed instead of using the first received truth sample as epoch.",
    )
    parser.add_argument("--kx", nargs=3, type=float, default=[1.0, 1.0, 1.0])
    parser.add_argument("--kv", nargs=3, type=float, default=[0.2, 0.2, 0.2])
    parser.add_argument("--obstacle", action="append", type=parse_obstacle, default=[])
    parser.add_argument("--report-json", required=True, type=Path)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    return parser.parse_args()


def state_for_elapsed(elapsed: float, args: argparse.Namespace) -> tuple[dict[str, Any], str, float]:
    mission_time = max(0.0, elapsed - args.start_delay_s)
    figure8_start_s = args.takeoff_s + args.hold_s
    figure8_end_s = max(
        figure8_start_s,
        args.duration_s
        - args.start_delay_s
        - args.post_figure8_hold_s
        - args.land_s
        - args.final_hold_s,
    )
    figure8_duration_s = max(0.0, figure8_end_s - figure8_start_s)
    post_figure8_hold_end_s = figure8_end_s + args.post_figure8_hold_s
    last_figure8_state = figure8_state(
        figure8_duration_s,
        x_amp=args.x_amplitude_m,
        y_amp=args.y_amplitude_m,
        z_m=args.altitude_m,
        period_s=args.period_s,
        x_offset_m=args.x_offset_m,
        y_offset_m=args.y_offset_m,
    )
    landing_x = float(last_figure8_state["position"][0])
    landing_y = float(last_figure8_state["position"][1])
    landing_yaw = float(last_figure8_state["yaw"])
    land_end_s = post_figure8_hold_end_s + args.land_s
    if elapsed < args.start_delay_s:
        return hold_state(x_m=args.x_offset_m, y_m=args.y_offset_m, z_m=args.ground_altitude_m), "pre_takeoff_hold", 0.0
    if mission_time < args.takeoff_s:
        return (
            vertical_ramp_state(
                mission_time,
                duration_s=args.takeoff_s,
                x_m=args.x_offset_m,
                y_m=args.y_offset_m,
                start_z_m=args.ground_altitude_m,
                end_z_m=args.altitude_m,
            ),
            "takeoff",
            0.0,
        )
    if mission_time < figure8_start_s:
        return hold_state(x_m=args.x_offset_m, y_m=args.y_offset_m, z_m=args.altitude_m), "pre_figure8_hold", 0.0
    if mission_time < figure8_end_s:
        trajectory_time = mission_time - figure8_start_s
        return (
            figure8_state(
                trajectory_time,
                x_amp=args.x_amplitude_m,
                y_amp=args.y_amplitude_m,
                z_m=args.altitude_m,
                period_s=args.period_s,
                x_offset_m=args.x_offset_m,
                y_offset_m=args.y_offset_m,
            ),
            "figure8",
            trajectory_time,
        )
    if mission_time < post_figure8_hold_end_s:
        return (
            hold_state(x_m=landing_x, y_m=landing_y, z_m=args.altitude_m, yaw_rad=landing_yaw),
            "post_figure8_hold",
            figure8_duration_s,
        )
    if mission_time < land_end_s:
        land_t = mission_time - post_figure8_hold_end_s
        return (
            vertical_ramp_state(
                land_t,
                duration_s=args.land_s,
                x_m=landing_x,
                y_m=landing_y,
                start_z_m=args.altitude_m,
                end_z_m=args.ground_altitude_m,
                yaw_rad=landing_yaw,
            ),
            "land",
            figure8_duration_s,
        )
    return (
        hold_state(x_m=landing_x, y_m=landing_y, z_m=args.ground_altitude_m, yaw_rad=landing_yaw),
        "post_land_hold",
        figure8_duration_s,
    )


def main() -> int:
    args = parse_args()
    ensure_ros_log_dir()
    if args.rate_hz <= 0.0 or args.duration_s <= 0.0 or args.period_s <= 0.0:
        raise SystemExit("rate-hz, duration-s, and period-s must be positive")
    if args.start_delay_s < 0.0 or not math.isfinite(args.start_delay_s):
        raise SystemExit("start-delay-s must be finite and non-negative")
    if args.truth_sync_epoch_s is not None and not math.isfinite(float(args.truth_sync_epoch_s)):
        raise SystemExit("truth-sync-epoch-s must be finite when provided")
    for key in ("takeoff_s", "hold_s", "post_figure8_hold_s", "land_s", "final_hold_s"):
        if float(getattr(args, key)) < 0.0 or not math.isfinite(float(getattr(args, key))):
            raise SystemExit(f"{key} must be finite and non-negative")
    for key in ("x_amplitude_m", "y_amplitude_m", "x_offset_m", "y_offset_m", "altitude_m"):
        if not math.isfinite(float(getattr(args, key))):
            raise SystemExit(f"{key} must be finite")

    import rclpy
    from geometry_msgs.msg import Point, Vector3
    from mosim_msgs.msg import PositionCommand
    if args.truth_sync_stdin:
        from gazebo_truth_planner_setpoint_tracker import (  # noqa: PLC0415
            has_timed_truth,
            iter_stdin_message_chunks,
            parse_truth_samples,
        )

    report_path = project_path(args.report_json)
    trace_path = project_path(args.trace_jsonl)
    if trace_path.exists():
        trace_path.unlink()

    rclpy.init()
    node = rclpy.create_node("mosim_figure8_position_command")
    pub = node.create_publisher(PositionCommand, args.topic, 10)
    period = 1.0 / args.rate_hz
    start_wall = time.monotonic()
    start_stamp_ns = int(node.get_clock().now().nanoseconds)
    next_tick = start_wall
    published = 0
    min_clearance: float | None = None
    first_publish_wall: float | None = None
    last_publish_wall: float | None = None
    try:
        def publish_elapsed(elapsed: float) -> None:
            nonlocal published, min_clearance, first_publish_wall, last_publish_wall
            state, phase, trajectory_time = state_for_elapsed(elapsed, args)
            msg = PositionCommand()
            if args.truth_sync_stdin:
                msg.header.stamp = node.get_clock().now().to_msg()
            else:
                msg.header.stamp = make_stamp(type(msg.header.stamp), start_stamp_ns + int(elapsed * 1_000_000_000))
            msg.header.frame_id = args.frame_id
            msg.position = Point(x=state["position"][0], y=state["position"][1], z=state["position"][2])
            msg.velocity = Vector3(x=state["velocity"][0], y=state["velocity"][1], z=state["velocity"][2])
            msg.acceleration = Vector3(x=state["acceleration"][0], y=state["acceleration"][1], z=state["acceleration"][2])
            msg.yaw = float(state["yaw"])
            msg.yaw_dot = float(state["yaw_dot"])
            msg.kx = [float(item) for item in args.kx]
            msg.kv = [float(item) for item in args.kv]
            msg.trajectory_id = published + 1
            msg.trajectory_flag = 1
            pub.publish(msg)
            rclpy.spin_once(node, timeout_sec=0.0)
            published += 1
            now = time.monotonic()
            first_publish_wall = now if first_publish_wall is None else first_publish_wall
            last_publish_wall = now
            clearance = clearance_xy(state["position"], args.obstacle)
            if clearance is not None:
                min_clearance = clearance if min_clearance is None else min(min_clearance, clearance)
            append_jsonl(
                trace_path,
                {
                    "schema": "mosim.figure8_position_command_sample.v1",
                    "sequence": published,
                    "elapsed_s": round(elapsed, 6),
                    "mission_time_s": round(max(0.0, elapsed - args.start_delay_s), 6),
                    "mission_phase": phase,
                    "trajectory_time_s": round(trajectory_time, 6),
                    "frame_id": args.frame_id,
                    "position_m": [round(float(item), 6) for item in state["position"]],
                    "velocity_mps": [round(float(item), 6) for item in state["velocity"]],
                    "acceleration_mps2": [round(float(item), 6) for item in state["acceleration"]],
                    "yaw_rad": round(float(state["yaw"]), 6),
                    "min_obstacle_clearance_m": round(clearance, 6) if clearance is not None else None,
                    "planner_id": args.planner_id,
                    "time_source": "gazebo_truth" if args.truth_sync_stdin else "wall_time",
                },
            )
        if args.truth_sync_stdin:
            first_truth_time: float | None = None
            truth_epoch = float(args.truth_sync_epoch_s) if args.truth_sync_epoch_s is not None else None
            last_publish_sim_elapsed = -1e9
            for chunk in iter_stdin_message_chunks(sys.stdin):
                stop = False
                for sample in parse_truth_samples(
                    chunk,
                    model_name=args.truth_sync_model_name,
                    topic=args.truth_sync_topic,
                    frame_id=args.truth_sync_frame_id,
                ):
                    if not has_timed_truth(sample):
                        continue
                    truth_time = float(sample["time"])
                    if truth_epoch is None and first_truth_time is None:
                        first_truth_time = truth_time
                    epoch = truth_epoch if truth_epoch is not None else first_truth_time
                    sim_elapsed = max(0.0, truth_time - float(epoch))
                    if sim_elapsed + 1e-9 < last_publish_sim_elapsed + period:
                        continue
                    publish_elapsed(sim_elapsed)
                    last_publish_sim_elapsed = sim_elapsed
                    if sim_elapsed >= args.duration_s:
                        stop = True
                        break
                if stop:
                    break
        else:
            while time.monotonic() - start_wall < args.duration_s:
                publish_elapsed(time.monotonic() - start_wall)
                next_tick += period
                time.sleep(max(0.0, next_tick - time.monotonic()))
    finally:
        node.destroy_node()
        rclpy.shutdown()

    publish_duration = 0.0
    if first_publish_wall is not None and last_publish_wall is not None:
        publish_duration = max(0.0, last_publish_wall - first_publish_wall)
    measured_rate = (published - 1) / publish_duration if published > 1 and publish_duration > 0.0 else 0.0
    gate_passed = published >= max(1, int(args.duration_s * args.rate_hz * 0.8))
    report = {
        "schema": "mosim.figure8_position_command_gate.v1",
        "status": "published" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "topic": args.topic,
        "frame_id": args.frame_id,
        "planner_id": args.planner_id,
        "trajectory": {
            "type": "horizontal_figure8",
            "duration_s": args.duration_s,
            "period_s": args.period_s,
            "x_amplitude_m": args.x_amplitude_m,
            "y_amplitude_m": args.y_amplitude_m,
            "x_offset_m": args.x_offset_m,
            "y_offset_m": args.y_offset_m,
            "altitude_m": args.altitude_m,
            "ground_altitude_m": args.ground_altitude_m,
            "start_delay_s": args.start_delay_s,
            "takeoff_s": args.takeoff_s,
            "hold_s": args.hold_s,
            "post_figure8_hold_s": args.post_figure8_hold_s,
            "land_s": args.land_s,
            "final_hold_s": args.final_hold_s,
            "figure8_start_s": args.start_delay_s + args.takeoff_s + args.hold_s,
            "figure8_duration_s": max(
                0.0,
                args.duration_s
                - args.start_delay_s
                - args.takeoff_s
                - args.hold_s
                - args.post_figure8_hold_s
                - args.land_s
                - args.final_hold_s,
            ),
            "time_source": "gazebo_truth" if args.truth_sync_stdin else "wall_time",
            "truth_sync_epoch_s": args.truth_sync_epoch_s,
        },
        "counts": {"published": published},
        "measured_rate_hz": measured_rate,
        "obstacles_xy_radius": [list(item) for item in args.obstacle],
        "reference_min_obstacle_clearance_m": min_clearance,
        "outputs": {"trace_jsonl": rel(trace_path)},
        "claim_boundary": [
            "bounded reference PositionCommand stream only",
            "no planner_ready, tracking success, actuator success, final closed_loop, or controller performance is claimed by this publisher alone",
        ],
    }
    write_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if gate_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
