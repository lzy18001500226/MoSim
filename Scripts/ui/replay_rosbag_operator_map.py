#!/usr/bin/env python3
"""Replay a ROS1 rosbag into the frozen QGC Factory-map telemetry envelope.

This is an offline display replay.  It never publishes ROS messages, arms a
vehicle, or starts Gazebo/PX4.  QGC consumes only the produced telemetry file.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ui.runtime_sidecar import build_operator_map_state, resolve_runtime_operator_map
from src.orchestration.operator_map_replay import (
    build_bag_id,
    build_replay_manifest,
    derive_replay_frames,
    load_coordinate_evidence,
    sha256_file,
)
from src.orchestration.runtime_sidecar_contract import atomic_write_json


def _time_to_seconds(value: Any, reason_code: str) -> float:
    try:
        seconds = float(value.to_sec()) if hasattr(value, "to_sec") else float(value.secs) + float(value.nsecs) / 1e9
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(reason_code) from exc
    if not math.isfinite(seconds) or seconds < 0.0:
        raise ValueError(reason_code)
    return seconds


def _vector(value: Any, reason_code: str) -> dict[str, float]:
    try:
        result = {axis: float(getattr(value, axis)) for axis in ("x", "y", "z")}
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(reason_code) from exc
    if any(not math.isfinite(component) for component in result.values()):
        raise ValueError(reason_code)
    return result


def _quaternion(value: Any) -> dict[str, float]:
    try:
        return {axis: float(getattr(value, axis)) for axis in ("w", "x", "y", "z")}
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("operator_map_replay_orientation_invalid") from exc


def _parse_odom_topics(values: list[str], vehicle_count: int) -> dict[str, str]:
    expected = {f"uav{index}" for index in range(1, vehicle_count + 1)}
    if not values:
        return {vehicle_id: f"/{vehicle_id}/mavros/local_position/odom" for vehicle_id in sorted(expected)}
    result: dict[str, str] = {}
    for value in values:
        vehicle_id, separator, topic = value.partition("=")
        if separator != "=" or vehicle_id not in expected or not topic.startswith("/") or vehicle_id in result:
            raise ValueError("operator_map_replay_odom_topic_mapping_invalid")
        result[vehicle_id] = topic
    if set(result) != expected:
        raise ValueError("operator_map_replay_odom_topic_mapping_incomplete")
    return result


def _sample_from_odom(vehicle_id: str, message: Any, bag_time: Any) -> dict[str, Any]:
    header = getattr(message, "header", None)
    frame_id = str(getattr(header, "frame_id", ""))
    if not frame_id:
        raise ValueError("operator_map_replay_sample_frame_missing")
    source_timestamp: float | None = None
    stamp = getattr(header, "stamp", None)
    if stamp is not None:
        candidate = _time_to_seconds(stamp, "operator_map_replay_header_time_invalid")
        source_timestamp = candidate if candidate > 0.0 else None
    pose = getattr(getattr(message, "pose", None), "pose", None)
    twist = getattr(getattr(message, "twist", None), "twist", None)
    if pose is None or twist is None:
        raise ValueError("operator_map_replay_odom_message_invalid")
    return {
        "vehicle_id": vehicle_id,
        "bag_time_s": _time_to_seconds(bag_time, "operator_map_replay_bag_time_invalid"),
        "source_timestamp_s": source_timestamp,
        "frame_id": frame_id,
        "position": _vector(getattr(pose, "position", None), "operator_map_replay_position_invalid"),
        "orientation": _quaternion(getattr(pose, "orientation", None)),
        "linear_velocity": _vector(getattr(twist, "linear", None), "operator_map_replay_velocity_invalid"),
        "angular_velocity": _vector(getattr(twist, "angular", None), "operator_map_replay_velocity_invalid"),
    }


def _load_rosbag_samples(path: Path, topics_by_vehicle: dict[str, str]) -> list[dict[str, Any]]:
    try:
        import rosbag  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ValueError("operator_map_replay_rosbag_python_unavailable") from exc
    topic_to_vehicle = {topic: vehicle_id for vehicle_id, topic in topics_by_vehicle.items()}
    samples: list[dict[str, Any]] = []
    try:
        with rosbag.Bag(str(path), "r") as bag:
            for topic, message, bag_time in bag.read_messages(topics=list(topic_to_vehicle)):
                samples.append(_sample_from_odom(topic_to_vehicle[topic], message, bag_time))
    except ValueError:
        raise
    except Exception as exc:  # rosbag exposes several reader-specific exception types.
        raise ValueError("operator_map_replay_rosbag_read_failed") from exc
    return samples


def _load_jsonl_samples(path: Path) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError("operator_map_replay_records_unreadable") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"operator_map_replay_records_json_invalid:{line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"operator_map_replay_records_json_invalid:{line_number}")
        samples.append(value)
    return samples


def _telemetry_payload(manifest: dict[str, Any], map_state: dict[str, Any], *, now: float) -> dict[str, Any]:
    vehicles = map_state["vehicles"]
    return {
        "schema": "mosim.runtime_telemetry.v2",
        "run_id": manifest["run_id"],
        "timestamp": now,
        "vehicle_count": manifest["vehicle_count"],
        "readiness": {
            "schema": "mosim.runtime_status.v1",
            "run_id": manifest["run_id"],
            "status": "replaying",
            "reason_code": "operator_map_rosbag_replay",
            "vehicle_count": manifest["vehicle_count"],
            "updated_at": now,
        },
        "vehicles": vehicles,
        "task_paths": map_state["task_paths"],
        "map_state": map_state,
        "mission_status": {
            "transport_state": "replay",
            "fresh": True,
            "terminal": map_state["transport"]["playback_state"] == "completed",
            "reason_code": "rosbag_replay_display_only",
        },
    }


def _write_status(run_dir: Path, payload: dict[str, Any]) -> None:
    atomic_write_json(run_dir / "OPERATOR_MAP_REPLAY_STATUS.json", payload)


def run_replay(args: argparse.Namespace) -> int:
    manifest_path = args.manifest or args.run_dir / "RUN_MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("operator_map_replay_manifest_unreadable") from exc
    vehicle_count = manifest.get("vehicle_count")
    if not isinstance(vehicle_count, int) or not 1 <= vehicle_count <= 9:
        raise ValueError("operator_map_replay_manifest_vehicle_count_invalid")
    map_snapshot, snapshot_hash = resolve_runtime_operator_map(manifest)
    coordinate_evidence = None
    coordinate_evidence_sha256 = ""
    if args.coordinate_evidence is not None:
        coordinate_evidence, coordinate_evidence_sha256 = load_coordinate_evidence(
            args.coordinate_evidence, map_snapshot=map_snapshot, snapshot_hash=snapshot_hash
        )
        map_snapshot = dict(map_snapshot)
        map_snapshot["coordinate_contract_status"] = "verified"

    topics_by_vehicle = _parse_odom_topics(args.odom_topic, vehicle_count)
    source_path = args.bag or args.records_jsonl
    if source_path is None or not source_path.is_file():
        raise ValueError("operator_map_replay_source_missing")
    if args.bag is not None:
        samples = _load_rosbag_samples(source_path, topics_by_vehicle)
        source_kind = "ros1_bag"
    else:
        samples = _load_jsonl_samples(source_path)
        source_kind = "normalized_rosbag_export_test_only"
    source_sha256 = sha256_file(source_path)
    bag_id = build_bag_id(source_path, source_sha256)
    frames = derive_replay_frames(samples, vehicle_count=vehicle_count, coordinate_evidence=coordinate_evidence)
    replay_manifest = build_replay_manifest(
        manifest=manifest,
        source_kind=source_kind,
        source_path=source_path,
        source_sha256=source_sha256,
        bag_id=bag_id,
        odom_topics=topics_by_vehicle,
        coordinate_evidence=coordinate_evidence,
        coordinate_evidence_sha256=coordinate_evidence_sha256,
        frames=frames,
    )
    args.run_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(args.run_dir / "OPERATOR_MAP_REPLAY_MANIFEST.json", replay_manifest)
    _write_status(
        args.run_dir,
        {
            "schema": "mosim.operator_map_replay_status.v1",
            "run_id": manifest["run_id"],
            "state": "playing",
            "source_kind": source_kind,
            "bag_id": bag_id,
            "frame_count": len(frames),
            "updated_at": time.time(),
        },
    )

    sequence = 0
    previous_playback_time = 0.0
    last_frame = frames[-1]
    for frame in frames:
        if not args.no_wait:
            delay = max(0.0, frame["playback_time_s"] - previous_playback_time) / args.speed
            if delay > 0.0:
                time.sleep(delay)
        previous_playback_time = frame["playback_time_s"]
        sequence += 1
        now = time.time()
        map_state = build_operator_map_state(
            manifest=manifest,
            map_snapshot=map_snapshot,
            transport_mode="rosbag_replay",
            sequence=sequence,
            received_at_unix_s=now,
            source_timestamp_s=frame["source_timestamp_s"],
            playback_state="playing",
            playback_time_s=frame["playback_time_s"],
            bag_id=bag_id,
            vehicles=frame["vehicles"],
            task_paths={},
        )
        atomic_write_json(args.run_dir / "telemetry.json", _telemetry_payload(manifest, map_state, now=now))
        _write_status(
            args.run_dir,
            {
                "schema": "mosim.operator_map_replay_status.v1",
                "run_id": manifest["run_id"],
                "state": "playing",
                "bag_id": bag_id,
                "sequence": sequence,
                "playback_time_s": frame["playback_time_s"],
                "updated_at": now,
            },
        )

    sequence += 1
    now = time.time()
    completed_state = build_operator_map_state(
        manifest=manifest,
        map_snapshot=map_snapshot,
        transport_mode="rosbag_replay",
        sequence=sequence,
        received_at_unix_s=now,
        source_timestamp_s=last_frame["source_timestamp_s"],
        playback_state="completed",
        playback_time_s=last_frame["playback_time_s"],
        bag_id=bag_id,
        vehicles=last_frame["vehicles"],
        task_paths={},
    )
    atomic_write_json(args.run_dir / "telemetry.json", _telemetry_payload(manifest, completed_state, now=now))
    _write_status(
        args.run_dir,
        {
            "schema": "mosim.operator_map_replay_status.v1",
            "run_id": manifest["run_id"],
            "state": "completed",
            "bag_id": bag_id,
            "sequence": sequence,
            "playback_time_s": last_frame["playback_time_s"],
            "updated_at": now,
        },
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bag", type=Path, help="ROS1 .bag input; run under an environment with python rosbag.")
    source.add_argument("--records-jsonl", type=Path, help="Test-only normalized rosbag export.")
    parser.add_argument("--odom-topic", action="append", default=[], metavar="UAV=TOPIC")
    parser.add_argument("--coordinate-evidence", type=Path)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--no-wait", action="store_true", help="Write frames immediately for deterministic tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not math.isfinite(args.speed) or args.speed <= 0.0:
        raise SystemExit("operator_map_replay_speed_invalid")
    try:
        return run_replay(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
