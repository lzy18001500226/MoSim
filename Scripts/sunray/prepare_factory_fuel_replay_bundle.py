#!/usr/bin/env python3
"""Build a bounded, evidence-bound Factory L2 FUEL rosbag replay bundle.

This entry point is intentionally offline.  It reads one historical rosbag and
emits a small clip plus normalized display inputs.  It never starts ROS nodes,
Gazebo, PX4, MAVROS, RViz, QGC, or UE, and it never publishes a command.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ui.runtime_sidecar import load_operator_map_snapshot
from src.orchestration.operator_map_replay import (
    canonical_json_hash,
    sha256_file,
    validate_coordinate_evidence,
)
from src.orchestration.runtime_sidecar_contract import atomic_write_json


DEFAULT_SOURCE_RUN_DIR = (
    ROOT
    / "Results"
    / "sunray_ros1"
    / "factory_l2_fuel_single_exploration_full600_record_20260714_143553"
)
DEFAULT_SOURCE_BAG = DEFAULT_SOURCE_RUN_DIR / "factory_fuel_review.bag"
DEFAULT_SCENARIO = ROOT / "Config" / "scenarios" / "ui" / "factory_l2_fuel_fixed64_exploration.json"
DEFAULT_MAP_CATALOG = ROOT / "Config" / "control_platform" / "operator_map_catalog.json"

MAVROS_ODOM_TOPIC = "/uav1/mavros/local_position/odom"
# The P4 renderer consumes recorded Gazebo world truth.  MAVROS local odometry
# stays in the bundle as an audit source and must not be mislabeled as truth.
DISPLAY_TRUTH_TOPIC = "/uav1/sunray/gazebo_pose"
POSITION_COMMAND_TOPIC = "/position_cmd"
EXPECTED_PATH_TOPIC = "/mosim/goal4/position_cmd_path"
FUTURE_MARKER_TOPIC = "/mosim/fuel/planning_vis/trajectory_world"
POINT_CLOUD_TOPIC = "/mosim/goal4/livox_world_accumulated"
OCCUPANCY_TOPIC = "/mosim/goal4/occupancy_accumulated"

SELECTED_TOPICS = (
    "/clock",
    "/tf",
    "/tf_static",
    "/uav1/mavros/state",
    MAVROS_ODOM_TOPIC,
    DISPLAY_TRUTH_TOPIC,
    POSITION_COMMAND_TOPIC,
    EXPECTED_PATH_TOPIC,
    FUTURE_MARKER_TOPIC,
    POINT_CLOUD_TOPIC,
    OCCUPANCY_TOPIC,
    "/mosim/goal4/truth_path",
    "/mosim/goal4/body_axes",
)
REQUIRED_TOPICS = (
    MAVROS_ODOM_TOPIC,
    DISPLAY_TRUTH_TOPIC,
    POSITION_COMMAND_TOPIC,
    EXPECTED_PATH_TOPIC,
    FUTURE_MARKER_TOPIC,
    POINT_CLOUD_TOPIC,
    OCCUPANCY_TOPIC,
)


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def time_to_seconds(value: Any) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        seconds = float(value)
    elif hasattr(value, "to_sec"):
        seconds = float(value.to_sec())
    else:
        seconds = float(value.secs) + float(value.nsecs) / 1.0e9
    if not math.isfinite(seconds):
        raise ValueError("p4_replay_timestamp_invalid")
    return seconds


def finite_component(value: Any, reason_code: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(reason_code) from exc
    if not math.isfinite(result):
        raise ValueError(reason_code)
    return result


def vector_xyz(value: Any, reason_code: str) -> tuple[float, float, float]:
    try:
        return tuple(finite_component(getattr(value, axis), reason_code) for axis in ("x", "y", "z"))
    except AttributeError as exc:
        raise ValueError(reason_code) from exc


def quaternion_to_rpy(value: Any) -> tuple[float, float, float]:
    try:
        x = finite_component(value.x, "p4_replay_quaternion_invalid")
        y = finite_component(value.y, "p4_replay_quaternion_invalid")
        z = finite_component(value.z, "p4_replay_quaternion_invalid")
        w = finite_component(value.w, "p4_replay_quaternion_invalid")
    except AttributeError as exc:
        raise ValueError("p4_replay_quaternion_invalid") from exc
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm < 1.0e-9:
        raise ValueError("p4_replay_quaternion_invalid")
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    sinp = 2.0 * (w * y - z * x)
    pitch = math.copysign(math.pi / 2.0, sinp) if abs(sinp) >= 1.0 else math.asin(sinp)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def odom_to_csv_row(message: Any, bag_time_s: float, clip_start_s: float) -> dict[str, float | str]:
    pose = getattr(getattr(message, "pose", None), "pose", None)
    twist = getattr(getattr(message, "twist", None), "twist", None)
    if pose is None or twist is None:
        raise ValueError("p4_replay_odom_invalid")
    x, y, z = vector_xyz(getattr(pose, "position", None), "p4_replay_odom_position_invalid")
    vx, vy, vz = vector_xyz(getattr(twist, "linear", None), "p4_replay_odom_velocity_invalid")
    roll, pitch, yaw = quaternion_to_rpy(getattr(pose, "orientation", None))
    t = time_to_seconds(bag_time_s) - clip_start_s
    if t < -1.0e-6:
        raise ValueError("p4_replay_odom_before_window")
    return {
        "t": max(0.0, t),
        "phase": "rosbag_replay",
        "x": x,
        "y": y,
        "z": z,
        "vx": vx,
        "vy": vy,
        "vz": vz,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
    }


def position_command_to_csv_row(message: Any, bag_time_s: float, clip_start_s: float) -> dict[str, float | str]:
    x, y, z = vector_xyz(getattr(message, "position", None), "p4_replay_position_command_invalid")
    t = time_to_seconds(bag_time_s) - clip_start_s
    if t < -1.0e-6:
        raise ValueError("p4_replay_position_command_before_window")
    return {"t": max(0.0, t), "phase": "recorded_position_cmd", "x": x, "y": y, "z": z}


def load_json_object(path: Path, reason_code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(reason_code) from exc
    if not isinstance(value, dict):
        raise ValueError(reason_code)
    return value


def build_run_manifest(
    *,
    run_id: str,
    scenario: dict[str, Any],
    map_snapshot: dict[str, Any],
    source_run_dir: Path,
    source_bag: Path,
    source_bag_sha256: str,
    clip_start_s: float,
    clip_end_s: float,
    topic_counts: dict[str, int],
) -> dict[str, Any]:
    profile_id = scenario.get("id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("p4_replay_scenario_id_missing")
    return {
        "schema": "mosim.run_manifest.v1",
        "run_id": run_id,
        "experiment_profile_id": profile_id,
        "experiment_profile_hash": canonical_json_hash(scenario),
        "vehicle_count": 1,
        "controller_backend": "historical_px4ctrl_l1_awff_replay_display_only",
        "scenario_snapshot": scenario,
        "operator_map_snapshot": map_snapshot,
        "operator_map_snapshot_hash": canonical_json_hash(map_snapshot),
        "source_bundle": {
            "source_run_dir": repo_rel(source_run_dir),
            "source_bag": repo_rel(source_bag),
            "source_bag_sha256": source_bag_sha256,
            "clip_start_bag_time_s": clip_start_s,
            "clip_end_bag_time_s": clip_end_s,
            "clip_duration_s": clip_end_s - clip_start_s,
            "selected_topics": list(SELECTED_TOPICS),
            "selected_topic_message_counts": topic_counts,
        },
        "claim_boundary": (
            "Historical FUEL rosbag replay bundle only. It preserves recorded display data; it does not "
            "claim current controller, planner, PX4, MAVROS, Gazebo, QGC, RViz, or UE live-runtime success."
        ),
        "created_at": utc_now(),
    }


def build_coordinate_evidence(
    *,
    run_id: str,
    map_snapshot: dict[str, Any],
    source_frame_id: str,
    source_bag: Path,
    clip_start_s: float,
    clip_end_s: float,
) -> dict[str, Any]:
    if source_frame_id != "world":
        raise ValueError(f"p4_replay_odom_frame_not_world:{source_frame_id}")
    evidence = {
        "schema": "mosim.operator_map_coordinate_evidence.v1",
        "status": "verified",
        "evidence_id": f"{run_id}:factory_l2_fuel_rosbag_world_identity",
        "operator_map_snapshot_hash": canonical_json_hash(map_snapshot),
        "map_id": map_snapshot["map_id"],
        "map_version": map_snapshot["map_version"],
        "asset_sha256": map_snapshot["asset_sha256"],
        "world_frame": map_snapshot["world_frame"],
        "coordinate_contract_id": map_snapshot["coordinate_contract_id"],
        "source_frame_id": source_frame_id,
        "target_frame_id": map_snapshot["world_frame"],
        "transform_target_from_source_4x4": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        "verification_basis": {
            "source_bag": repo_rel(source_bag),
            "source_truth_topic": DISPLAY_TRUTH_TOPIC,
            "observed_truth_header_frame_id": source_frame_id,
            "clip_bag_time_s": [clip_start_s, clip_end_s],
            "static_contract": "Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json",
            "contract_summary": "Gazebo world and MWORKS world use meters and z-up; only the UE display conversion applies centimetres and Y inversion.",
        },
        "claim_boundary": "Verified rosbag world-to-MWORKS-world identity for this replay clip only; UE conversion remains display-only.",
        "created_at": utc_now(),
    }
    validate_coordinate_evidence(
        evidence,
        map_snapshot=map_snapshot,
        snapshot_hash=str(evidence["operator_map_snapshot_hash"]),
    )
    return evidence


def write_csv(path: Path, rows: list[dict[str, float | str]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"p4_replay_csv_rows_missing:{path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_rosbag() -> tuple[Any, Any]:
    try:
        import rosbag  # type: ignore[import-not-found]
        import rospy  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("p4_replay_ros1_python_unavailable: source /opt/ros/noetic/setup.bash") from exc
    return rosbag, rospy


def select_window(
    *,
    bag: Any,
    rospy: Any,
    duration_s: float,
    start_offset_s: float | None,
    pre_roll_s: float,
) -> tuple[float, float, str]:
    bag_start_s = time_to_seconds(bag.get_start_time())
    bag_end_s = time_to_seconds(bag.get_end_time())
    if duration_s <= 0.0 or not math.isfinite(duration_s):
        raise ValueError("p4_replay_duration_invalid")
    if start_offset_s is not None:
        clip_start_s = bag_start_s + start_offset_s
        selector = "user_start_offset"
    else:
        candidate_s: float | None = None
        selector = "first_position_command"
        for _, message, bag_time in bag.read_messages(topics=[POSITION_COMMAND_TOPIC]):
            if int(getattr(message, "trajectory_id", 0)) > 0:
                candidate_s = time_to_seconds(bag_time)
                selector = "first_position_command_trajectory_id_gt_zero"
                break
            if candidate_s is None:
                candidate_s = time_to_seconds(bag_time)
        if candidate_s is None:
            raise ValueError("p4_replay_position_command_missing")
        clip_start_s = candidate_s - pre_roll_s
    clip_start_s = max(bag_start_s, clip_start_s)
    clip_end_s = min(bag_end_s, clip_start_s + duration_s)
    if clip_end_s - clip_start_s < min(5.0, duration_s):
        raise ValueError("p4_replay_window_too_short")
    return clip_start_s, clip_end_s, selector


def extract_bundle(
    *,
    source_run_dir: Path,
    source_bag: Path,
    output_dir: Path,
    run_id: str,
    duration_s: float,
    start_offset_s: float | None,
    pre_roll_s: float,
    scenario_path: Path,
    map_catalog_path: Path,
) -> dict[str, Any]:
    if not source_bag.is_file() or source_bag.stat().st_size <= 0:
        raise FileNotFoundError(f"p4_replay_source_bag_missing:{source_bag}")
    scenario = load_json_object(scenario_path, "p4_replay_scenario_unreadable")
    map_snapshot = load_operator_map_snapshot(map_catalog_path, "factory_l2")
    rosbag, rospy = _load_rosbag()

    output_dir.mkdir(parents=True, exist_ok=True)
    clip_bag = output_dir / "factory_fuel_review_clip.bag"
    if clip_bag.exists():
        raise FileExistsError(f"p4_replay_output_bag_exists:{clip_bag}")

    with rosbag.Bag(str(source_bag), "r") as input_bag:
        clip_start_s, clip_end_s, selector = select_window(
            bag=input_bag,
            rospy=rospy,
            duration_s=duration_s,
            start_offset_s=start_offset_s,
            pre_roll_s=pre_roll_s,
        )

    topic_counts = {topic: 0 for topic in SELECTED_TOPICS}
    display_truth_rows: list[dict[str, float | str]] = []
    mavros_odom_rows: list[dict[str, float | str]] = []
    command_rows: list[dict[str, float | str]] = []
    display_truth_frames: set[str] = set()
    mavros_odom_frames: set[str] = set()
    start_time = rospy.Time.from_sec(clip_start_s)
    end_time = rospy.Time.from_sec(clip_end_s)
    with rosbag.Bag(str(source_bag), "r") as input_bag, rosbag.Bag(
        str(clip_bag), "w", compression=rosbag.Compression.LZ4
    ) as output_bag:
        for topic, message, bag_time in input_bag.read_messages(
            topics=list(SELECTED_TOPICS), start_time=start_time, end_time=end_time
        ):
            output_bag.write(topic, message, bag_time)
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            bag_time_s = time_to_seconds(bag_time)
            if topic in {MAVROS_ODOM_TOPIC, DISPLAY_TRUTH_TOPIC}:
                frame_id = str(getattr(getattr(message, "header", None), "frame_id", ""))
                if not frame_id:
                    raise ValueError("p4_replay_odom_frame_missing")
                row = odom_to_csv_row(message, bag_time_s, clip_start_s)
                if topic == DISPLAY_TRUTH_TOPIC:
                    display_truth_frames.add(frame_id)
                    display_truth_rows.append(row)
                else:
                    mavros_odom_frames.add(frame_id)
                    mavros_odom_rows.append(row)
            elif topic == POSITION_COMMAND_TOPIC:
                command_rows.append(position_command_to_csv_row(message, bag_time_s, clip_start_s))

    missing_topics = [topic for topic in REQUIRED_TOPICS if topic_counts.get(topic, 0) <= 0]
    if missing_topics:
        raise ValueError(f"p4_replay_required_topics_missing:{','.join(missing_topics)}")
    if len(display_truth_frames) != 1:
        raise ValueError(f"p4_replay_display_truth_frame_inconsistent:{sorted(display_truth_frames)}")
    if len(mavros_odom_frames) != 1:
        raise ValueError(f"p4_replay_mavros_odom_frame_inconsistent:{sorted(mavros_odom_frames)}")
    source_frame_id = next(iter(display_truth_frames))
    coordinate_evidence = build_coordinate_evidence(
        run_id=run_id,
        map_snapshot=map_snapshot,
        source_frame_id=source_frame_id,
        source_bag=source_bag,
        clip_start_s=clip_start_s,
        clip_end_s=clip_end_s,
    )

    # Hashing the complete historical source binds the short clip to the exact original recording.
    source_bag_sha256 = sha256_file(source_bag)
    manifest = build_run_manifest(
        run_id=run_id,
        scenario=scenario,
        map_snapshot=map_snapshot,
        source_run_dir=source_run_dir,
        source_bag=source_bag,
        source_bag_sha256=source_bag_sha256,
        clip_start_s=clip_start_s,
        clip_end_s=clip_end_s,
        topic_counts=topic_counts,
    )
    write_csv(
        output_dir / "uav1_truth.csv",
        display_truth_rows,
        ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"],
    )
    write_csv(
        output_dir / "uav1_mavros_local_odom.csv",
        mavros_odom_rows,
        ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"],
    )
    write_csv(output_dir / "uav1_position_cmd.csv", command_rows, ["t", "phase", "x", "y", "z"])
    atomic_write_json(output_dir / "RUN_MANIFEST.json", manifest)
    atomic_write_json(output_dir / "OPERATOR_MAP_COORDINATE_EVIDENCE.json", coordinate_evidence)
    summary = {
        "schema": "mosim.sunray_p4_factory_fuel_replay_bundle_status.v1",
        "status": "prepared",
        "run_id": run_id,
        "output_dir": repo_rel(output_dir),
        "clip_bag": repo_rel(clip_bag),
        "clip_bag_sha256": sha256_file(clip_bag),
        "source_bag": repo_rel(source_bag),
        "source_bag_sha256": source_bag_sha256,
        "window": {
            "selector": selector,
            "start_bag_time_s": clip_start_s,
            "end_bag_time_s": clip_end_s,
            "duration_s": clip_end_s - clip_start_s,
        },
        "message_counts": topic_counts,
        "display_pose_source": DISPLAY_TRUTH_TOPIC,
        "display_state_kind": "gazebo_world_truth",
        "display_truth_csv": "uav1_truth.csv",
        "display_truth_row_count": len(display_truth_rows),
        "mavros_odom_row_count": len(mavros_odom_rows),
        "position_command_row_count": len(command_rows),
        "source_frame_id": source_frame_id,
        "mavros_odom_frame_id": next(iter(mavros_odom_frames)),
        "coordinate_evidence": "OPERATOR_MAP_COORDINATE_EVIDENCE.json",
        "next_steps": [
            "Run Scripts/ui/replay_rosbag_operator_map.py with uav1 mapped to /uav1/sunray/gazebo_pose.",
            "Run Scripts/UE5/generate_factory_ue_render_replay.py with --state-source truth against this run directory.",
            "Only then launch optional RViz/UE display consumers for bounded review.",
        ],
        "claim_boundary": "Prepared offline replay inputs only; no display consumer or live runtime was started.",
        "created_at": utc_now(),
    }
    atomic_write_json(output_dir / "P4_REPLAY_BUNDLE_STATUS.json", summary)
    return summary


def default_output_dir(run_id: str) -> Path:
    return ROOT / "Results" / "sunray_ros1" / run_id


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=f"sunray_ros1_p4_factory_fuel_replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--source-run-dir", default=str(DEFAULT_SOURCE_RUN_DIR))
    parser.add_argument("--source-bag", default=str(DEFAULT_SOURCE_BAG))
    parser.add_argument("--scenario", default=str(DEFAULT_SCENARIO))
    parser.add_argument("--map-catalog", default=str(DEFAULT_MAP_CATALOG))
    parser.add_argument("--duration-s", type=float, default=45.0)
    parser.add_argument("--start-offset-s", type=float, default=None)
    parser.add_argument("--pre-roll-s", type=float, default=5.0)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir(args.run_id)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    try:
        summary = extract_bundle(
            source_run_dir=Path(args.source_run_dir),
            source_bag=Path(args.source_bag),
            output_dir=output_dir,
            run_id=args.run_id,
            duration_s=args.duration_s,
            start_offset_s=args.start_offset_s,
            pre_roll_s=args.pre_roll_s,
            scenario_path=Path(args.scenario),
            map_catalog_path=Path(args.map_catalog),
        )
    except Exception as exc:
        output_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(
            output_dir / "P4_REPLAY_BUNDLE_STATUS.json",
            {
                "schema": "mosim.sunray_p4_factory_fuel_replay_bundle_status.v1",
                "status": "blocked",
                "run_id": args.run_id,
                "reason_code": str(exc),
                "claim_boundary": "Replay bundle preparation did not complete; no display or live runtime claim is available.",
                "created_at": utc_now(),
            },
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
