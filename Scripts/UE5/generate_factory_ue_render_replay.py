#!/usr/bin/env python3
"""Generate a Factory UE render replay contract from a validated ROS1 run.

This script is a display bridge preparation step. It consumes existing
Factory Gazebo/PX4/MAVROS evidence files and writes a one-way UE render replay
JSONL plus manifest. It does not open Unreal Editor, send UDP packets, start
ROS, or feed anything back into Gazebo/PX4/planners/controllers.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_DIR = (
    ROOT
    / "Results"
    / "sunray_ros1"
    / "factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053"
)
DEFAULT_SCENE_ID = "factory"
DEFAULT_MAP_ID = "local_factoryenvironmentcollect"
FRAME_SCHEMA = "mosim.ue_render_frame.v1"
MANIFEST_SCHEMA = "mosim.ue_render_stream_manifest.v1"
VALIDATION_SCHEMA = "mosim.ue_render_stream_validation.v1"
SUMMARY_SCHEMA = "mosim.factory_l2_ue_render_replay_summary.v1"


@dataclass(frozen=True)
class VehicleRows:
    vehicle_id: str
    source_path: Path
    rows: list[dict[str, Any]]


@dataclass(frozen=True)
class VehiclePlanRows:
    vehicle_id: str
    source_path: Path
    rows: list[dict[str, Any]]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def finite_float(value: Any, fallback: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(out):
        return fallback
    return out


def parse_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    return float(value)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {rel(path)}")
    return data


def read_csv_rows(path: Path, vehicle_id: str) -> VehicleRows:
    required = ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"]
    if not path.exists() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"missing or empty source CSV: {rel(path)}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        missing = [name for name in required if name not in headers]
        if missing:
            raise ValueError(f"{rel(path)} missing required columns: {missing}")
        rows: list[dict[str, Any]] = []
        for raw in reader:
            rows.append(
                {
                    "t": parse_float(raw.get("t")),
                    "phase": raw.get("phase") or "",
                    "x": parse_float(raw.get("x")),
                    "y": parse_float(raw.get("y")),
                    "z": parse_float(raw.get("z")),
                    "vx": parse_float(raw.get("vx")),
                    "vy": parse_float(raw.get("vy")),
                    "vz": parse_float(raw.get("vz")),
                    "roll": parse_float(raw.get("roll")),
                    "pitch": parse_float(raw.get("pitch")),
                    "yaw": parse_float(raw.get("yaw")),
                }
            )
    rows = [row for row in rows if math.isfinite(float(row["t"]))]
    if not rows:
        raise ValueError(f"source CSV has no finite timestamp rows: {rel(path)}")
    rows.sort(key=lambda row: float(row["t"]))
    return VehicleRows(vehicle_id=vehicle_id, source_path=path, rows=rows)


def resolve_vehicle_csv_path(
    run_dir: Path,
    vehicle_id: str,
    source_name: str,
    vehicle_count: int,
) -> Path:
    """Resolve multi-UAV files first, then the established single-UAV layout."""
    vehicle_path = run_dir / f"{vehicle_id}_{source_name}.csv"
    if vehicle_path.exists() or vehicle_count != 1:
        return vehicle_path
    return run_dir / f"{source_name}.csv"


def read_plan_csv_rows(path: Path, vehicle_id: str) -> VehiclePlanRows:
    if not path.exists() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"missing or empty reference-plan CSV: {rel(path)}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        command_columns = ["cmd_x", "cmd_y", "cmd_z"]
        position_columns = command_columns if all(name in headers for name in command_columns) else ["x", "y", "z"]
        required = ["t", *position_columns]
        missing = [name for name in required if name not in headers]
        if missing:
            raise ValueError(f"{rel(path)} missing required columns: {missing}")
        rows: list[dict[str, Any]] = []
        for raw in reader:
            rows.append(
                {
                    "t": parse_float(raw.get("t")),
                    "phase": raw.get("phase") or "",
                    "x": parse_float(raw.get(position_columns[0])),
                    "y": parse_float(raw.get(position_columns[1])),
                    "z": parse_float(raw.get(position_columns[2])),
                }
            )
    rows = [row for row in rows if math.isfinite(float(row["t"]))]
    if not rows:
        raise ValueError(f"reference-plan CSV has no finite timestamp rows: {rel(path)}")
    rows.sort(key=lambda row: float(row["t"]))
    return VehiclePlanRows(vehicle_id=vehicle_id, source_path=path, rows=rows)


def interpolate_angle(a: float, b: float, alpha: float) -> float:
    if not math.isfinite(a):
        return b if math.isfinite(b) else 0.0
    if not math.isfinite(b):
        return a
    delta = (b - a + math.pi) % (2.0 * math.pi) - math.pi
    return a + alpha * delta


def interpolate_rows(left: dict[str, Any], right: dict[str, Any], t: float) -> dict[str, Any]:
    lt = finite_float(left.get("t"), t)
    rt = finite_float(right.get("t"), lt)
    alpha = 0.0 if rt <= lt else max(0.0, min(1.0, (t - lt) / (rt - lt)))
    row: dict[str, Any] = {"t": t, "phase": left.get("phase") if alpha < 0.5 else right.get("phase")}
    for name in ["x", "y", "z", "vx", "vy", "vz"]:
        lv = finite_float(left.get(name), math.nan)
        rv = finite_float(right.get(name), lv)
        row[name] = lv + alpha * (rv - lv) if math.isfinite(lv) and math.isfinite(rv) else finite_float(lv, 0.0)
    for name in ["roll", "pitch", "yaw"]:
        row[name] = interpolate_angle(finite_float(left.get(name), 0.0), finite_float(right.get(name), 0.0), alpha)
    return row


def interpolate_position_row(left: dict[str, Any], right: dict[str, Any], t: float) -> dict[str, Any]:
    lt = finite_float(left.get("t"), t)
    rt = finite_float(right.get("t"), lt)
    alpha = 0.0 if rt <= lt else max(0.0, min(1.0, (t - lt) / (rt - lt)))
    row: dict[str, Any] = {"t": t, "phase": left.get("phase") if alpha < 0.5 else right.get("phase")}
    for name in ["x", "y", "z"]:
        lv = finite_float(left.get(name), math.nan)
        rv = finite_float(right.get(name), lv)
        row[name] = lv + alpha * (rv - lv) if math.isfinite(lv) and math.isfinite(rv) else finite_float(lv, 0.0)
    return row


def resample_rows(rows: list[dict[str, Any]], rate_hz: float) -> list[dict[str, Any]]:
    if rate_hz <= 0.0 or len(rows) < 2:
        return rows
    start_t = finite_float(rows[0].get("t"))
    end_t = finite_float(rows[-1].get("t"), start_t)
    if end_t <= start_t:
        return rows
    step = 1.0 / rate_hz
    output: list[dict[str, Any]] = []
    source_index = 0
    t = start_t
    # Use a small epsilon so floating point accumulation includes the final bin.
    while t <= end_t + step * 0.25:
        while source_index + 1 < len(rows) and finite_float(rows[source_index + 1].get("t")) < t:
            source_index += 1
        left = rows[source_index]
        right = rows[min(source_index + 1, len(rows) - 1)]
        output.append(interpolate_rows(left, right, t))
        t += step
    return output


def resample_position_rows(rows: list[dict[str, Any]], rate_hz: float) -> list[dict[str, Any]]:
    if rate_hz <= 0.0 or len(rows) < 2:
        return rows
    start_t = finite_float(rows[0].get("t"))
    end_t = finite_float(rows[-1].get("t"), start_t)
    if end_t <= start_t:
        return rows
    step = 1.0 / rate_hz
    output: list[dict[str, Any]] = []
    source_index = 0
    t = start_t
    while t <= end_t + step * 0.25:
        while source_index + 1 < len(rows) and finite_float(rows[source_index + 1].get("t")) < t:
            source_index += 1
        left = rows[source_index]
        right = rows[min(source_index + 1, len(rows) - 1)]
        output.append(interpolate_position_row(left, right, t))
        t += step
    return output


def interpolate_plan_at_time(rows: list[dict[str, Any]], t: float) -> dict[str, Any] | None:
    if not rows:
        return None
    if t <= finite_float(rows[0].get("t")):
        return rows[0]
    if t >= finite_float(rows[-1].get("t")):
        return rows[-1]
    source_index = 0
    while source_index + 1 < len(rows) and finite_float(rows[source_index + 1].get("t")) < t:
        source_index += 1
    return interpolate_position_row(rows[source_index], rows[min(source_index + 1, len(rows) - 1)], t)


def rpy_to_quat_xyzw(roll: float, pitch: float, yaw: float) -> list[float]:
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    if norm <= 0.0 or not math.isfinite(norm):
        return [0.0, 0.0, 0.0, 1.0]
    return [qx / norm, qy / norm, qz / norm, qw / norm]


def round_vector(values: list[float], digits: int = 9) -> list[float]:
    return [round(finite_float(value), digits) for value in values]


def build_calibration_reference_points(
    start_row: dict[str, Any],
    *,
    xy_length_m: float,
    z_height_m: float,
) -> list[list[float]]:
    x0 = finite_float(start_row.get("x"))
    y0 = finite_float(start_row.get("y"))
    z0 = finite_float(start_row.get("z"))
    length = max(0.01, finite_float(xy_length_m, 1.0))
    height = max(0.01, finite_float(z_height_m, 0.5))
    return [
        round_vector([x0, y0, z0]),
        round_vector([x0 + length, y0, z0]),
        round_vector([x0 + length, y0 + length, z0]),
        round_vector([x0 + length, y0 + length, z0 + height]),
    ]


def build_synthetic_calibration_rows(
    start_row: dict[str, Any],
    *,
    xy_length_m: float,
    z_height_m: float,
    rate_hz: float,
    segment_duration_s: float,
) -> list[dict[str, Any]]:
    points = build_calibration_reference_points(
        start_row,
        xy_length_m=xy_length_m,
        z_height_m=z_height_m,
    )
    start_t = finite_float(start_row.get("t"))
    roll = finite_float(start_row.get("roll"))
    pitch = finite_float(start_row.get("pitch"))
    yaw = finite_float(start_row.get("yaw"))
    rate = max(1.0, finite_float(rate_hz, 10.0))
    duration = max(0.2, finite_float(segment_duration_s, 2.0))
    step = 1.0 / rate
    rows: list[dict[str, Any]] = []
    phases = ["calibration_x", "calibration_y", "calibration_z"]
    for segment_index in range(3):
        p0 = points[segment_index]
        p1 = points[segment_index + 1]
        segment_steps = max(1, int(math.ceil(duration * rate)))
        for sample_index in range(segment_steps):
            alpha = sample_index / segment_steps
            t = start_t + segment_index * duration + sample_index * step
            position = [
                p0[axis] + alpha * (p1[axis] - p0[axis])
                for axis in range(3)
            ]
            velocity = [
                (p1[axis] - p0[axis]) / duration
                for axis in range(3)
            ]
            rows.append(
                {
                    "t": t,
                    "phase": phases[segment_index],
                    "x": position[0],
                    "y": position[1],
                    "z": position[2],
                    "vx": velocity[0],
                    "vy": velocity[1],
                    "vz": velocity[2],
                    "roll": roll,
                    "pitch": pitch,
                    "yaw": yaw,
                }
            )
    rows.append(
        {
            "t": start_t + 3.0 * duration,
            "phase": "calibration_hold",
            "x": points[-1][0],
            "y": points[-1][1],
            "z": points[-1][2],
            "vx": 0.0,
            "vy": 0.0,
            "vz": 0.0,
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
    )
    return rows


def make_frame(
    *,
    row: dict[str, Any],
    run_id: str,
    sequence: int,
    vehicle_id: str,
    source_profile: str,
    source_csv: Path,
    controller_profile: str,
    planner_profile: str,
    scene_id: str,
    map_id: str,
    display_rate_hz: float,
    reference_row: dict[str, Any] | None = None,
    local_plan_points_m: list[list[float]] | None = None,
    local_plan_source: str = "",
) -> dict[str, Any]:
    roll = finite_float(row.get("roll"))
    pitch = finite_float(row.get("pitch"))
    yaw = finite_float(row.get("yaw"))
    frame = {
        "schema": FRAME_SCHEMA,
        "run_id": run_id,
        "sequence": sequence,
        "timestamp_ros_s": round(finite_float(row.get("t")), 6),
        "source_profile": source_profile,
        "vehicle_id": vehicle_id,
        "frame_id": "world",
        "child_frame_id": f"{vehicle_id}/base_link",
        "position_m": round_vector(
            [
                finite_float(row.get("x")),
                finite_float(row.get("y")),
                finite_float(row.get("z")),
            ]
        ),
        "reference_position_m": round_vector(
            [
                finite_float((reference_row or row).get("x")),
                finite_float((reference_row or row).get("y")),
                finite_float((reference_row or row).get("z")),
            ]
        ),
        "orientation_quat_xyzw": round_vector(rpy_to_quat_xyzw(roll, pitch, yaw), 12),
        "linear_velocity_mps": round_vector(
            [
                finite_float(row.get("vx")),
                finite_float(row.get("vy")),
                finite_float(row.get("vz")),
            ]
        ),
        "angular_velocity_radps": [0.0, 0.0, 0.0],
        "rpy_rad_display_source": round_vector([roll, pitch, yaw], 12),
        "phase": str(row.get("phase", "")),
        "trajectory_reference_id": f"{run_id}:{vehicle_id}:{source_profile}",
        "controller_profile": controller_profile,
        "planner_profile": planner_profile,
        "state_source_profile": source_profile,
        "display_profile": {
            "scene_id": scene_id,
            "map_id": map_id,
            "update_rate_hz": display_rate_hz,
            "trail_mode": "global_overview_attitude_trails",
        },
        "scene_id": scene_id,
        "map_id": map_id,
        "source_csv": rel(source_csv),
        "claim_boundary": "display_only_one_way_replay_no_feedback_to_runtime",
    }
    if local_plan_points_m:
        frame["local_plan"] = {
            "source": local_plan_source,
            "render_only": True,
            "evidence_backed": True,
            "valid": True,
            "points_m": local_plan_points_m,
        }
    return frame


def infer_run_metadata(run_dir: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    run_inputs = run_dir / "RUN_INPUTS.json"
    run_manifest = run_dir / "RUN_MANIFEST.json"
    metrics = run_dir / "EGO_SWARM_METRICS.json"
    if run_inputs.exists():
        metadata["run_inputs"] = read_json(run_inputs)
    if run_manifest.exists():
        metadata["run_manifest"] = read_json(run_manifest)
    if metrics.exists():
        metadata["metrics"] = read_json(metrics)
    return metadata


def build_manifest(
    *,
    run_dir: Path,
    output_dir: Path,
    run_id: str,
    vehicles: list[VehicleRows],
    frames_path: Path,
    validation_path: Path,
    source_profile: str,
    controller_profile: str,
    planner_profile: str,
    scene_id: str,
    map_id: str,
    display_rate_hz: float,
    frames: list[dict[str, Any]],
    metadata: dict[str, Any],
    plan_sources: dict[str, Path] | None = None,
    reference_overlay_sources: dict[str, str] | None = None,
    reference_overlay_source: str = "none",
) -> dict[str, Any]:
    times = [finite_float(frame.get("timestamp_ros_s")) for frame in frames]
    per_vehicle: dict[str, dict[str, Any]] = {}
    for vehicle in vehicles:
        vehicle_frames = [frame for frame in frames if frame.get("vehicle_id") == vehicle.vehicle_id]
        vehicle_times = [finite_float(frame.get("timestamp_ros_s")) for frame in vehicle_frames]
        per_vehicle[vehicle.vehicle_id] = {
            "source_file": rel(vehicle.source_path),
            "input_row_count": len(vehicle.rows),
            "frame_count": len(vehicle_frames),
            "time_start_ros_s": min(vehicle_times) if vehicle_times else None,
            "time_end_ros_s": max(vehicle_times) if vehicle_times else None,
        }
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "replay_contract_passed",
        "run_id": run_id,
        "source_bundle": rel(run_dir),
        "source_topics_or_files": {
            vehicle.vehicle_id: {
                "state": rel(vehicle.source_path),
                "reference_plan": rel(plan_sources[vehicle.vehicle_id])
                if plan_sources and vehicle.vehicle_id in plan_sources
                else None,
                "reference_overlay": reference_overlay_sources.get(vehicle.vehicle_id)
                if reference_overlay_sources and vehicle.vehicle_id in reference_overlay_sources
                else None,
            }
            for vehicle in vehicles
        },
        "scene_id": scene_id,
        "map_id": map_id,
        "vehicle_asset_profile": "Sunray150_with_MID360_display_mesh",
        "coordinate_transform_profile": {
            "source_frame": "ROS/Gazebo world, meters, radians, z-up",
            "frame_payload_units": "meters and radians retained for audit",
            "unreal_render_units": "centimeters on UE side",
            "ue_conversion_policy": "UE display component converts meters to centimeters and applies the project scene axis binding",
            "orientation_source": "roll/pitch/yaw radians converted to quaternion xyzw in bridge replay",
        },
        "timebase_profile": {
            "source_timestamps": "CSV t column from the source runtime run bundle",
            "output_rate_hz": display_rate_hz,
            "resampling": "linear interpolation for position/velocity; wrapped interpolation for roll/pitch/yaw",
            "frame_order": "global sequence sorted by timestamp then vehicle id",
        },
        "transport_profile": {
            "mode": "T0_jsonl_replay",
            "live_udp_sent": False,
            "ue_editor_opened": False,
            "feedback_to_runtime": False,
        },
        "drop_or_interpolation_policy": {
            "offline_replay": "all generated frames are retained",
            "future_live_sidecar": "UE may drop stale display frames and must not back-pressure ROS/Gazebo/PX4/MAVROS",
        },
        "controller_profile": controller_profile,
        "planner_profile": planner_profile,
        "state_source_profile": source_profile,
        "display_profile": {
            "first_target": f"{scene_id} Global Overview attitude trails at {display_rate_hz:g} Hz",
            "show_attitude_axes": True,
            "trail_sample_interval_frames": 1,
            "trail_time_window_s": 0,
            "reference_plan_overlay": reference_overlay_source != "none",
            "actual_trail_source": "state CSV position_m",
            "reference_trail_source": reference_overlay_source,
        },
        "outputs": {
            "frame_jsonl": rel(frames_path),
            "validation": rel(validation_path),
            "summary": rel(output_dir / "SUMMARY.md"),
        },
        "frame_count": len(frames),
        "vehicle_count": len(vehicles),
        "time_start_ros_s": min(times) if times else None,
        "time_end_ros_s": max(times) if times else None,
        "per_vehicle": per_vehicle,
        "evidence_links": {
            "source_run_manifest": rel(run_dir / "RUN_MANIFEST.json"),
            "source_run_inputs": rel(run_dir / "RUN_INPUTS.json"),
            "source_metrics": rel(run_dir / "EGO_SWARM_METRICS.json"),
            "factory_static_scene_profile": "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json",
            "factory_world": "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf",
        },
        "source_status": {
            "runtime_metrics_status": metadata.get("metrics", {}).get("status"),
            "runtime_blockers": metadata.get("metrics", {}).get("blockers"),
            "mission_exit_code": metadata.get("run_manifest", {}).get("mission_exit_code"),
        },
        "claim_boundary": [
            "F7a proves a one-way replay data contract from a source runtime run.",
            "It does not prove UE Editor/runtime visual acceptance until F7b/F7c evidence exists.",
            "It must not feed truth, control, planner target, estimator, or actor transforms back to Gazebo/PX4/MAVROS/planners.",
        ],
    }


def validate_frames(frames: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if manifest.get("schema") != MANIFEST_SCHEMA:
        issues.append("manifest schema mismatch")
    if not frames:
        issues.append("no frames generated")

    required = [
        "schema",
        "run_id",
        "sequence",
        "timestamp_ros_s",
        "source_profile",
        "vehicle_id",
        "frame_id",
        "child_frame_id",
        "position_m",
        "orientation_quat_xyzw",
        "linear_velocity_mps",
        "angular_velocity_radps",
        "trajectory_reference_id",
        "controller_profile",
        "planner_profile",
        "state_source_profile",
        "display_profile",
        "claim_boundary",
    ]
    previous_sequence = -1
    for index, frame in enumerate(frames):
        for field in required:
            if field not in frame:
                issues.append(f"frame {index} missing {field}")
        if frame.get("schema") != FRAME_SCHEMA:
            issues.append(f"frame {index} schema mismatch")
        sequence = int(frame.get("sequence", -1))
        if sequence <= previous_sequence:
            issues.append(f"frame {index} sequence is not strictly increasing")
        previous_sequence = sequence
        for vector_name, expected_len in [
            ("position_m", 3),
            ("reference_position_m", 3),
            ("orientation_quat_xyzw", 4),
            ("linear_velocity_mps", 3),
            ("angular_velocity_radps", 3),
        ]:
            vector = frame.get(vector_name)
            if not isinstance(vector, list) or len(vector) != expected_len:
                issues.append(f"frame {index} {vector_name} has invalid shape")
                continue
            if any(not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in vector):
                issues.append(f"frame {index} {vector_name} contains nonfinite value")
        quat = frame.get("orientation_quat_xyzw")
        if isinstance(quat, list) and len(quat) == 4:
            norm = math.sqrt(sum(float(value) * float(value) for value in quat))
            if abs(norm - 1.0) > 1e-6:
                issues.append(f"frame {index} quaternion norm {norm:.9f} is not unit length")
        local_plan = frame.get("local_plan")
        if local_plan is not None:
            if not isinstance(local_plan, dict):
                issues.append(f"frame {index} local_plan is not an object")
            else:
                points = local_plan.get("points_m")
                if not isinstance(points, list) or len(points) < 2:
                    issues.append(f"frame {index} local_plan has too few points")
                else:
                    for point_index, point in enumerate(points[:1000]):
                        if not isinstance(point, list) or len(point) != 3:
                            issues.append(f"frame {index} local_plan point {point_index} invalid shape")
                            break
                        if any(not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in point):
                            issues.append(f"frame {index} local_plan point {point_index} contains nonfinite value")
                            break

    return {
        "schema": VALIDATION_SCHEMA,
        "status": "passed" if not issues else "failed",
        "issue_count": len(issues),
        "issues": issues[:100],
        "frame_count": len(frames),
        "vehicle_count": manifest.get("vehicle_count"),
        "manifest_schema": manifest.get("schema"),
        "frame_schema": FRAME_SCHEMA,
        "claim_boundary": "schema/content validation only; no UE runtime display opened",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary(
    path: Path,
    *,
    manifest: dict[str, Any],
    validation: dict[str, Any],
    frame_jsonl: Path,
    validation_path: Path,
) -> None:
    lines = [
        "# Factory L2 UE Render Replay F7a",
        "",
        f"status: {validation['status']}",
        f"run_id: {manifest['run_id']}",
        f"source_bundle: {manifest['source_bundle']}",
        f"frame_jsonl: {rel(frame_jsonl)}",
        f"manifest: {rel(path.parent / 'UE_RENDER_STREAM_MANIFEST.json')}",
        f"validation: {rel(validation_path)}",
        f"scene_id: {manifest['scene_id']}",
        f"map_id: {manifest['map_id']}",
        f"vehicle_count: {manifest['vehicle_count']}",
        f"frame_count: {manifest['frame_count']}",
        f"time_start_ros_s: {manifest['time_start_ros_s']}",
        f"time_end_ros_s: {manifest['time_end_ros_s']}",
        "",
        "## Boundary",
        "",
        "- F7a validates the replay stream contract only.",
        "- UE Editor/runtime display is still pending until F7b/F7c.",
        "- The stream is display-only and must not feed back into Gazebo/PX4/MAVROS/planners/controllers.",
        "",
        "## Per Vehicle",
        "",
    ]
    for vehicle_id, info in manifest["per_vehicle"].items():
        lines.append(
            f"- {vehicle_id}: frames={info['frame_count']}, source={info['source_file']}, "
            f"t=[{info['time_start_ros_s']}, {info['time_end_ros_s']}]"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_replay(args: argparse.Namespace) -> dict[str, Any]:
    if args.include_reference_plan and args.calibration_reference_line:
        raise ValueError("--include-reference-plan and --calibration-reference-line are mutually exclusive")
    run_dir = repo_path(args.run_dir)
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run directory not found: {rel(run_dir)}")
    run_id = args.run_id or run_dir.name
    vehicle_ids = [item.strip() for item in args.vehicles.split(",") if item.strip()]
    if not vehicle_ids:
        raise ValueError("--vehicles produced an empty vehicle list")

    derived_source_profile = (
        f"factory_l2_synthetic_xyz_calibration_display_only_from_{args.state_source}_start"
        if args.synthetic_calibration_state
        else f"factory_l2_{args.state_source}_csv_display_only"
    )
    source_profile = args.source_profile or derived_source_profile
    vehicles: list[VehicleRows] = []
    plan_rows_by_vehicle: dict[str, list[dict[str, Any]]] = {}
    plan_sources: dict[str, Path] = {}
    local_plan_points_by_vehicle: dict[str, list[list[float]]] = {}
    local_plan_sources_by_vehicle: dict[str, str] = {}
    for vehicle_id in vehicle_ids:
        source_path = resolve_vehicle_csv_path(
            run_dir,
            vehicle_id,
            args.state_source,
            len(vehicle_ids),
        )
        vehicle = read_csv_rows(source_path, vehicle_id)
        if args.synthetic_calibration_state:
            synthetic_rows = build_synthetic_calibration_rows(
                vehicle.rows[0],
                xy_length_m=args.calibration_line_length_m,
                z_height_m=args.calibration_line_height_m,
                rate_hz=args.rate_hz,
                segment_duration_s=args.calibration_segment_duration_s,
            )
            vehicle = VehicleRows(vehicle_id=vehicle.vehicle_id, source_path=vehicle.source_path, rows=synthetic_rows)
        vehicles.append(vehicle)
        if args.include_reference_plan:
            plan_path = resolve_vehicle_csv_path(
                run_dir,
                vehicle_id,
                args.reference_plan_source,
                len(vehicle_ids),
            )
            plan = read_plan_csv_rows(plan_path, vehicle_id)
            resampled_plan = resample_position_rows(plan.rows, args.reference_plan_rate_hz or args.rate_hz)
            plan_rows_by_vehicle[vehicle_id] = resampled_plan
            plan_sources[vehicle_id] = plan.source_path
            local_plan_points_by_vehicle[vehicle_id] = [
                round_vector([
                    finite_float(row.get("x")),
                    finite_float(row.get("y")),
                    finite_float(row.get("z")),
                ])
                for row in resampled_plan
            ]
            local_plan_sources_by_vehicle[vehicle_id] = rel(plan.source_path)
        elif args.calibration_reference_line or args.synthetic_calibration_state:
            local_plan_points_by_vehicle[vehicle_id] = build_calibration_reference_points(
                vehicle.rows[0],
                xy_length_m=args.calibration_line_length_m,
                z_height_m=args.calibration_line_height_m,
            )
            local_plan_sources_by_vehicle[vehicle_id] = (
                "synthetic_xyz_calibration_reference_from_start"
                f":state_source={args.state_source}"
                f":xy_length_m={args.calibration_line_length_m:g}"
                f":z_height_m={args.calibration_line_height_m:g}"
            )

    output_dir = repo_path(args.output_dir) if args.output_dir else (
        ROOT
        / "Results"
        / "unreal_scene_mapping"
        / f"factory_l2_ue_render_mirror_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    all_frames: list[dict[str, Any]] = []
    for vehicle in vehicles:
        plan_rows = plan_rows_by_vehicle.get(vehicle.vehicle_id, [])
        local_plan_points = local_plan_points_by_vehicle.get(vehicle.vehicle_id, [])
        for row in resample_rows(vehicle.rows, args.rate_hz):
            reference_row = interpolate_plan_at_time(plan_rows, finite_float(row.get("t"))) if plan_rows else None
            all_frames.append(
                make_frame(
                    row=row,
                    run_id=run_id,
                    sequence=0,
                    vehicle_id=vehicle.vehicle_id,
                    source_profile=source_profile,
                    source_csv=vehicle.source_path,
                    controller_profile=args.controller_profile,
                    planner_profile=args.planner_profile,
                    scene_id=args.scene_id,
                    map_id=args.map_id,
                    display_rate_hz=args.rate_hz,
                    reference_row=reference_row,
                    local_plan_points_m=local_plan_points,
                    local_plan_source=local_plan_sources_by_vehicle.get(vehicle.vehicle_id, ""),
                )
            )
    all_frames.sort(key=lambda frame: (float(frame["timestamp_ros_s"]), str(frame["vehicle_id"])))
    for sequence, frame in enumerate(all_frames):
        frame["sequence"] = sequence

    frame_jsonl = output_dir / "ue_render_frame.jsonl"
    manifest_path = output_dir / "UE_RENDER_STREAM_MANIFEST.json"
    validation_path = output_dir / "UE_RENDER_STREAM_VALIDATION.json"
    summary_path = output_dir / "SUMMARY.md"

    metadata = infer_run_metadata(run_dir)
    manifest = build_manifest(
        run_dir=run_dir,
        output_dir=output_dir,
        run_id=run_id,
        vehicles=vehicles,
        frames_path=frame_jsonl,
        validation_path=validation_path,
        source_profile=source_profile,
        controller_profile=args.controller_profile,
        planner_profile=args.planner_profile,
        scene_id=args.scene_id,
        map_id=args.map_id,
        display_rate_hz=args.rate_hz,
        frames=all_frames,
        metadata=metadata,
        plan_sources=plan_sources if plan_sources else None,
        reference_overlay_sources=local_plan_sources_by_vehicle if local_plan_sources_by_vehicle else None,
        reference_overlay_source=(
            "position_cmd CSV when enabled"
            if args.include_reference_plan
            else "synthetic XYZ calibration line from state-source start"
            if args.calibration_reference_line or args.synthetic_calibration_state
            else "none"
        ),
    )
    validation = validate_frames(all_frames, manifest)

    with frame_jsonl.open("w", encoding="utf-8", newline="\n") as handle:
        for frame in all_frames:
            handle.write(json.dumps(frame, ensure_ascii=False, separators=(",", ":")) + "\n")
    write_json(manifest_path, manifest)
    write_json(validation_path, validation)
    write_summary(summary_path, manifest=manifest, validation=validation, frame_jsonl=frame_jsonl, validation_path=validation_path)

    summary = {
        "schema": SUMMARY_SCHEMA,
        "status": validation["status"],
        "output_dir": rel(output_dir),
        "frame_jsonl": rel(frame_jsonl),
        "manifest": rel(manifest_path),
        "validation": rel(validation_path),
        "frame_count": len(all_frames),
        "vehicle_count": len(vehicles),
        "run_id": run_id,
    }
    write_json(output_dir / "F7A_UE_RENDER_REPLAY_SUMMARY.json", summary)
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR), help="Factory runtime result directory")
    parser.add_argument("--output-dir", default=None, help="Output directory; default creates timestamped Results/unreal_scene_mapping dir")
    parser.add_argument("--run-id", default=None, help="Override run_id; defaults to run directory name")
    parser.add_argument("--vehicles", default="uav1,uav2,uav3", help="Comma-separated vehicle ids")
    parser.add_argument("--state-source", choices=["truth", "odom"], default="truth", help="Per-UAV CSV suffix to consume")
    parser.add_argument(
        "--source-profile",
        default=None,
        help="Explicit display-only state-source identity; defaults to the Factory replay convention.",
    )
    parser.add_argument("--include-reference-plan", action="store_true", help="Embed per-UAV position_cmd CSV as a display-only expected trajectory overlay")
    parser.add_argument("--reference-plan-source", default="position_cmd", help="Per-UAV CSV suffix used for the display-only expected trajectory")
    parser.add_argument("--reference-plan-rate-hz", type=float, default=0.0, help="Expected trajectory overlay resample rate; defaults to --rate-hz")
    parser.add_argument("--calibration-reference-line", action="store_true", help="Embed a synthetic X-Y-Z three-segment calibration reference from each vehicle start point")
    parser.add_argument("--synthetic-calibration-state", action="store_true", help="Replace vehicle state with a display-only synthetic X-Y-Z calibration path from the state-source start point")
    parser.add_argument("--calibration-line-length-m", type=float, default=1.0, help="Synthetic calibration X/Y segment length in meters")
    parser.add_argument("--calibration-line-height-m", type=float, default=0.5, help="Synthetic calibration Z segment height in meters")
    parser.add_argument("--calibration-segment-duration-s", type=float, default=2.0, help="Synthetic calibration segment duration in seconds")
    parser.add_argument("--rate-hz", type=float, default=10.0, help="Replay frame rate per vehicle")
    parser.add_argument("--scene-id", default=DEFAULT_SCENE_ID)
    parser.add_argument("--map-id", default=DEFAULT_MAP_ID)
    parser.add_argument("--controller-profile", default="l1_awff")
    parser.add_argument("--planner-profile", default="racer")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        summary = build_replay(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
