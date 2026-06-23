#!/usr/bin/env python3
"""Record numeric diagnostics for the live EGO/RViz review topics.

The review windows are for human inspection. This recorder adds a small JSON
sidecar with frame, point count, dimensions, and finite XYZ bounds for each
topic so visual issues can be tied back to a concrete source.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROS_LOG_DIR = ROOT / "Results" / "tmp" / "ros_logs"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def ensure_ros_log_dir() -> None:
    log_dir = Path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    resolved = project_path(log_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(resolved)


def rel(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return value.as_posix()


def field_offsets(msg: Any) -> dict[str, int]:
    offsets = {str(field.name): int(field.offset) for field in msg.fields}
    for name in ("x", "y", "z"):
        if name not in offsets:
            raise ValueError(f"PointCloud2 missing {name} field")
    return offsets


def summarize_cloud(msg: Any, *, topic: str, max_points: int) -> dict[str, Any]:
    offsets = field_offsets(msg)
    intensity_offset = offsets.get("intensity")
    point_step = int(msg.point_step)
    width = int(msg.width)
    height = int(msg.height)
    raw_count = width * height
    total = min(raw_count, max_points)
    data = bytes(msg.data)
    endian = ">" if msg.is_bigendian else "<"

    finite_count = 0
    nonfinite_count = 0
    min_x = min_y = min_z = math.inf
    max_x = max_y = max_z = -math.inf
    intensity_count = 0
    min_intensity = math.inf
    max_intensity = -math.inf
    sum_intensity = 0.0

    for index in range(total):
        base = index * point_step
        try:
            x = struct.unpack_from(endian + "f", data, base + offsets["x"])[0]
            y = struct.unpack_from(endian + "f", data, base + offsets["y"])[0]
            z = struct.unpack_from(endian + "f", data, base + offsets["z"])[0]
            intensity = (
                struct.unpack_from(endian + "f", data, base + intensity_offset)[0]
                if intensity_offset is not None and base + intensity_offset + 4 <= len(data)
                else math.nan
            )
        except struct.error:
            break
        if math.isfinite(x) and math.isfinite(y) and math.isfinite(z):
            finite_count += 1
            min_x = min(min_x, float(x))
            min_y = min(min_y, float(y))
            min_z = min(min_z, float(z))
            max_x = max(max_x, float(x))
            max_y = max(max_y, float(y))
            max_z = max(max_z, float(z))
            if math.isfinite(intensity):
                intensity_count += 1
                min_intensity = min(min_intensity, float(intensity))
                max_intensity = max(max_intensity, float(intensity))
                sum_intensity += float(intensity)
        else:
            nonfinite_count += 1

    payload: dict[str, Any] = {
        "topic": topic,
        "frame_id": str(msg.header.frame_id),
        "stamp": {
            "sec": int(msg.header.stamp.sec),
            "nanosec": int(msg.header.stamp.nanosec),
        },
        "width": width,
        "height": height,
        "raw_point_count": raw_count,
        "sampled_point_count": total,
        "finite_point_count": finite_count,
        "nonfinite_point_count": nonfinite_count,
        "point_step": point_step,
        "fields": [str(field.name) for field in msg.fields],
    }
    if finite_count > 0:
        payload["bounds_m"] = {
            "x": [min_x, max_x],
            "y": [min_y, max_y],
            "z": [min_z, max_z],
        }
        payload["max_abs_xy_m"] = max(abs(min_x), abs(max_x), abs(min_y), abs(max_y))
        payload["max_abs_xyz_m"] = max(
            abs(min_x), abs(max_x), abs(min_y), abs(max_y), abs(min_z), abs(max_z)
        )
        payload["z_distribution_m"] = {
            "min": min_z,
            "max": max_z,
            "span": max_z - min_z,
        }
    if intensity_count > 0:
        payload["intensity"] = {
            "sample_count": intensity_count,
            "min": min_intensity,
            "max": max_intensity,
            "mean": sum_intensity / intensity_count,
        }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--duration-seconds", type=float, default=45.0)
    parser.add_argument("--max-points", type=int, default=250000)
    parser.add_argument("--raw-lidar-topic", default="/mosim/gazebo/lidar_points/points")
    parser.add_argument("--planner-cloud-topic", default="/mosim/planner/global_points")
    parser.add_argument("--review-cloud-topic", default="/mosim/review/lidar_points_map")
    parser.add_argument("--review-accumulated-cloud-topic", default="/mosim/review/lidar_points_map_accumulated")
    parser.add_argument("--ego-occupancy-topic", default="/grid_map/occupancy")
    parser.add_argument("--ego-inflate-topic", default="/grid_map/occupancy_inflate")
    parser.add_argument("--actual-path-topic", default="/mosim/review/actual_path")
    parser.add_argument("--reference-path-topic", default="/mosim/review/reference_path")
    parser.add_argument("--ego-goal-topic", default="/goal_point")
    parser.add_argument("--ego-optimal-topic", default="/optimal_list")
    parser.add_argument("--ego-global-topic", default="/global_list")
    parser.add_argument("--position-command-topic", default="/position_cmd")
    parser.add_argument("--planner-setpoint-topic", default="/mosim/planner/setpoint")
    parser.add_argument("--controller-output-topic", default="/mosim/sunray150/controller_output")
    parser.add_argument("--position-command-trace-jsonl", default="")
    parser.add_argument("--planner-setpoint-trace-jsonl", default="")
    parser.add_argument("--controller-output-trace-jsonl", default="")
    parser.add_argument("--skip-ego-topics", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_ros_log_dir()
    try:
        import rclpy  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from mosim_msgs.msg import ControllerOutput, PlannerSetpoint, PositionCommand  # type: ignore
        from nav_msgs.msg import Path as NavPath  # type: ignore
        from sensor_msgs.msg import PointCloud2  # type: ignore
        from visualization_msgs.msg import Marker  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    output_json = project_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    topics = {
        "raw_gazebo_lidar": args.raw_lidar_topic,
        "review_cloud_map_frame": args.review_cloud_topic,
        "review_accumulated_cloud_map_frame": args.review_accumulated_cloud_topic,
        "planner_cloud_map_frame": args.planner_cloud_topic,
    }
    if not args.skip_ego_topics:
        topics.update(
            {
                "ego_occupancy": args.ego_occupancy_topic,
                "ego_occupancy_inflate": args.ego_inflate_topic,
            }
        )
    samples: dict[str, dict[str, Any]] = {}
    message_counts = {key: 0 for key in topics}
    path_topics = {
        "actual_path": args.actual_path_topic,
        "reference_path": args.reference_path_topic,
    }
    marker_topics = {
        "ego_goal": args.ego_goal_topic,
        "ego_optimal": args.ego_optimal_topic,
        "ego_global": args.ego_global_topic,
    }
    command_topics = {
        "position_cmd": args.position_command_topic,
        "planner_setpoint": args.planner_setpoint_topic,
        "controller_output": args.controller_output_topic,
    }
    path_samples: dict[str, dict[str, Any]] = {}
    marker_samples: dict[str, dict[str, Any]] = {}
    command_samples: dict[str, dict[str, Any]] = {}
    path_message_counts = {key: 0 for key in path_topics}
    marker_message_counts = {key: 0 for key in marker_topics}
    command_message_counts = {key: 0 for key in command_topics}
    first_message_time = {key: None for key in topics}
    last_message_time = {key: None for key in topics}
    first_command_time = {key: None for key in command_topics}
    last_command_time = {key: None for key in command_topics}
    errors: list[str] = []
    trace_paths = {
        "position_cmd": project_path(args.position_command_trace_jsonl) if args.position_command_trace_jsonl else None,
        "planner_setpoint": project_path(args.planner_setpoint_trace_jsonl) if args.planner_setpoint_trace_jsonl else None,
        "controller_output": project_path(args.controller_output_trace_jsonl) if args.controller_output_trace_jsonl else None,
    }
    trace_handles = {}
    for key, path in trace_paths.items():
        if path is None:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        trace_handles[key] = path.open("w", encoding="utf-8", newline="\n")

    def write_trace(key: str, payload: dict[str, Any]) -> None:
        handle = trace_handles.get(key)
        if handle is None:
            return
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()

    rclpy.init()
    node = rclpy.create_node("mosim_real_ego_rviz_review_topic_recorder")
    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=5,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )

    empty_counts = {key: 0 for key in topics}

    def should_replace_sample(key: str, candidate: dict[str, Any]) -> bool:
        current = samples.get(key)
        if current is None:
            return True
        candidate_finite = int(candidate.get("finite_point_count", 0))
        current_finite = int(current.get("finite_point_count", 0))
        if key == "review_accumulated_cloud_map_frame":
            return candidate_finite >= current_finite
        if key in {"ego_occupancy", "ego_occupancy_inflate"}:
            return candidate_finite > 0
        return False

    def make_callback(key: str, topic: str) -> Any:
        def callback(msg: Any) -> None:
            now = time.monotonic()
            message_counts[key] += 1
            if first_message_time[key] is None:
                first_message_time[key] = now
            last_message_time[key] = now
            try:
                sample = summarize_cloud(msg, topic=topic, max_points=int(args.max_points))
                if int(sample.get("finite_point_count", 0)) <= 0:
                    empty_counts[key] += 1
                    return
                if should_replace_sample(key, sample):
                    samples[key] = sample
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{key}:{exc.__class__.__name__}:{exc}")

        return callback

    for key, topic in topics.items():
        node.create_subscription(PointCloud2, topic, make_callback(key, topic), qos)

    def make_path_callback(key: str, topic: str) -> Any:
        def callback(msg: Any) -> None:
            path_message_counts[key] += 1
            positions = []
            for pose in list(msg.poses)[:5]:
                positions.append(
                    [
                        float(pose.pose.position.x),
                        float(pose.pose.position.y),
                        float(pose.pose.position.z),
                    ]
                )
            path_samples[key] = {
                "topic": topic,
                "frame_id": str(msg.header.frame_id),
                "pose_count": len(msg.poses),
                "first_positions_m": positions,
            }

        return callback

    def make_marker_callback(key: str, topic: str) -> Any:
        def callback(msg: Any) -> None:
            marker_message_counts[key] += 1
            marker_samples[key] = {
                "topic": topic,
                "frame_id": str(msg.header.frame_id),
                "type": int(msg.type),
                "point_count": len(msg.points),
                "scale": {
                    "x": float(msg.scale.x),
                    "y": float(msg.scale.y),
                    "z": float(msg.scale.z),
                },
            }

        return callback

    def make_position_command_callback(key: str, topic: str) -> Any:
        def callback(msg: Any) -> None:
            now = time.monotonic()
            command_message_counts[key] += 1
            if first_command_time[key] is None:
                first_command_time[key] = now
            last_command_time[key] = now
            command_samples[key] = {
                "topic": topic,
                "frame_id": str(msg.header.frame_id),
                "stamp": {
                    "sec": int(msg.header.stamp.sec),
                    "nanosec": int(msg.header.stamp.nanosec),
                },
                "position_m": [
                    float(msg.position.x),
                    float(msg.position.y),
                    float(msg.position.z),
                ],
                "velocity_mps": [
                    float(msg.velocity.x),
                    float(msg.velocity.y),
                    float(msg.velocity.z),
                ],
                "acceleration_mps2": [
                    float(msg.acceleration.x),
                    float(msg.acceleration.y),
                    float(msg.acceleration.z),
                ],
                "yaw_rad": float(msg.yaw),
                "yaw_rate_radps": float(msg.yaw_dot),
                "trajectory_id": int(msg.trajectory_id),
                "trajectory_flag": int(msg.trajectory_flag),
            }
            write_trace(key, command_samples[key])

        return callback

    def make_planner_setpoint_callback(key: str, topic: str) -> Any:
        def callback(msg: Any) -> None:
            now = time.monotonic()
            command_message_counts[key] += 1
            if first_command_time[key] is None:
                first_command_time[key] = now
            last_command_time[key] = now
            command_samples[key] = {
                "topic": topic,
                "frame_id": str(msg.frame_id),
                "header_frame_id": str(msg.header.frame_id),
                "stamp": {
                    "sec": int(msg.header.stamp.sec),
                    "nanosec": int(msg.header.stamp.nanosec),
                },
                "sequence": int(msg.sequence),
                "position_m": [float(item) for item in msg.position_m],
                "velocity_mps": [float(item) for item in msg.velocity_mps],
                "acceleration_mps2": [float(item) for item in msg.acceleration_mps2],
                "yaw_rad": float(msg.yaw_rad),
                "yaw_rate_radps": float(msg.yaw_rate_radps),
                "trajectory_status": int(msg.trajectory_status),
                "planner_id": str(msg.planner_id),
            }
            write_trace(key, command_samples[key])

        return callback

    def make_controller_output_callback(key: str, topic: str) -> Any:
        def callback(msg: Any) -> None:
            now = time.monotonic()
            command_message_counts[key] += 1
            if first_command_time[key] is None:
                first_command_time[key] = now
            last_command_time[key] = now
            command_samples[key] = {
                "topic": topic,
                "frame_id": str(msg.header.frame_id),
                "stamp": {
                    "sec": int(msg.header.stamp.sec),
                    "nanosec": int(msg.header.stamp.nanosec),
                },
                "sequence": int(msg.sequence),
                "vehicle_id": str(msg.vehicle_id),
                "command_type": str(msg.command_type),
                "command": [float(item) for item in msg.command],
                "command_frame": str(msg.command_frame),
                "mode": str(msg.mode),
                "status": str(msg.status),
                "backend": str(msg.backend),
                "saturation": bool(msg.saturation),
                "source_authority": str(msg.source_authority),
            }
            write_trace(key, command_samples[key])

        return callback

    for key, topic in path_topics.items():
        node.create_subscription(NavPath, topic, make_path_callback(key, topic), qos)
    for key, topic in marker_topics.items():
        node.create_subscription(Marker, topic, make_marker_callback(key, topic), qos)
    node.create_subscription(
        PositionCommand,
        command_topics["position_cmd"],
        make_position_command_callback("position_cmd", command_topics["position_cmd"]),
        qos,
    )
    node.create_subscription(
        PlannerSetpoint,
        command_topics["planner_setpoint"],
        make_planner_setpoint_callback("planner_setpoint", command_topics["planner_setpoint"]),
        qos,
    )
    node.create_subscription(
        ControllerOutput,
        command_topics["controller_output"],
        make_controller_output_callback("controller_output", command_topics["controller_output"]),
        qos,
    )

    deadline = time.monotonic() + max(float(args.duration_seconds), 0.1)
    try:
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        for handle in trace_handles.values():
            handle.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    optional_empty_topics = {"ego_occupancy"}
    required_topics = [key for key in topics if key not in optional_empty_topics]
    missing = [key for key in required_topics if key not in samples]
    blockers = [f"missing_sample:{key}" for key in missing]
    warnings = [f"missing_optional_sample:{key}" for key in topics if key in optional_empty_topics and key not in samples]
    blockers.extend(errors)
    for key, sample in samples.items():
        if key not in optional_empty_topics and int(sample.get("finite_point_count", 0)) <= 0:
            blockers.append(f"empty_finite_points:{key}")
        elif key in optional_empty_topics and int(sample.get("finite_point_count", 0)) <= 0:
            warnings.append(f"empty_optional_finite_points:{key}")
    if path_message_counts["actual_path"] <= 0 or int(path_samples.get("actual_path", {}).get("pose_count", 0)) < 2:
        blockers.append("actual_path_insufficient_points")
    if path_message_counts["reference_path"] <= 0 or int(path_samples.get("reference_path", {}).get("pose_count", 0)) < 2:
        blockers.append("reference_path_insufficient_points")
    if marker_message_counts["ego_optimal"] <= 0 and marker_message_counts["ego_global"] <= 0:
        warnings.append("ego_marker_samples_missing")

    measured_rates_hz: dict[str, float | None] = {}
    for key in topics:
        first_time = first_message_time[key]
        last_time = last_message_time[key]
        if first_time is None or last_time is None or message_counts[key] <= 1 or last_time <= first_time:
            measured_rates_hz[key] = None
        else:
            measured_rates_hz[key] = (message_counts[key] - 1) / (last_time - first_time)
    command_rates_hz: dict[str, float | None] = {}
    for key in command_topics:
        first_time = first_command_time[key]
        last_time = last_command_time[key]
        if first_time is None or last_time is None or command_message_counts[key] <= 1 or last_time <= first_time:
            command_rates_hz[key] = None
        else:
            command_rates_hz[key] = (command_message_counts[key] - 1) / (last_time - first_time)
    merged_message_counts = dict(message_counts)
    merged_message_counts.update(command_message_counts)

    report = {
        "schema": "mosim.real_ego_rviz_review_topics.v1",
        "status": "ready" if not blockers else "blocked",
        "gate_passed": not blockers,
        "duration_seconds": float(args.duration_seconds),
        "output_json": rel(output_json),
        "topics": topics,
        "samples": samples,
        "message_counts": merged_message_counts,
        "pointcloud_message_counts": message_counts,
        "path_topics": path_topics,
        "path_message_counts": path_message_counts,
        "path_samples": path_samples,
        "marker_topics": marker_topics,
        "marker_message_counts": marker_message_counts,
        "marker_samples": marker_samples,
        "command_topics": command_topics,
        "command_message_counts": command_message_counts,
        "command_samples": command_samples,
        "command_trace_jsonl": {
            key: rel(path) for key, path in trace_paths.items() if path is not None
        },
        "measured_rates_hz": measured_rates_hz,
        "command_rates_hz": command_rates_hz,
        "ignored_empty_message_counts": empty_counts,
        "blockers": blockers,
        "warnings": warnings,
        "interpretation_notes": [
        "raw_gazebo_lidar is the Gazebo MID360 PointCloud2 before map-frame transform.",
        "review_cloud_map_frame is the unfiltered map-frame LiDAR review cloud.",
        "review_accumulated_cloud_map_frame is a human-review-only multi-frame accumulated cloud.",
        "planner_cloud_map_frame is the filtered map-frame cloud for EGO input.",
            "ego_occupancy and ego_occupancy_inflate are EGO grid-map PointCloud2 voxel-center outputs, so RViz Boxes are expected there only.",
            "Do not judge LiDAR range from EGO occupancy topics because EGO currently applies local update and max-ray-length limits.",
            "ego_occupancy may be empty in the current EGO port; ego_occupancy_inflate is the required grid-review sample.",
        ],
    }
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
