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

from Scripts.ui.runtime_sidecar import (
    build_operator_map_state_or_rejected,
    project_live_operator_map_frame,
    resolve_runtime_operator_map,
)
from src.orchestration.operator_map_replay import (
    build_bag_id,
    build_replay_manifest,
    derive_replay_frames,
    load_coordinate_evidence,
    sha256_file,
)
from src.orchestration.runtime_sidecar_contract import atomic_write_json, build_operator_runtime_status


MAX_TASK_PATH_POINTS = 1200
TASK_PATH_RECORD_TYPES = {"expected_path": "expected", "future_path": "future"}


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


def _path_metadata(profile_id: str, vehicle_count: int, kind: str) -> tuple[str, str]:
    if kind == "future":
        return "planner_sampled_future_trajectory", "uav1" if vehicle_count == 1 else "planner_default"
    if profile_id == "factory_l2_three_uav_swarm_formation_v1":
        return "formation_center_reference", "formation_center"
    if profile_id == "factory_l2_fuel_fixed64_exploration_v1":
        return "exploration_target_sequence", "uav1"
    return "mission_reference", "uav1" if vehicle_count == 1 else "all_vehicles"


def _header_source_timestamp(header: Any) -> float | None:
    stamp = getattr(header, "stamp", None)
    if stamp is None:
        return None
    candidate = _time_to_seconds(stamp, "operator_map_replay_header_time_invalid")
    return candidate if candidate > 0.0 else None


def _bounded_message_points(points: Any, reason_code: str) -> list[dict[str, float]]:
    if not isinstance(points, (list, tuple)):
        raise ValueError(reason_code)
    stride = max(1, math.ceil(len(points) / MAX_TASK_PATH_POINTS))
    return [_vector(point, reason_code) for point in points[::stride]][:MAX_TASK_PATH_POINTS]


def _bounded_json_points(points: Any, reason_code: str) -> list[dict[str, float]]:
    if not isinstance(points, list):
        raise ValueError(reason_code)
    stride = max(1, math.ceil(len(points) / MAX_TASK_PATH_POINTS))
    normalized: list[dict[str, float]] = []
    for point in points[::stride][:MAX_TASK_PATH_POINTS]:
        if not isinstance(point, dict):
            raise ValueError(reason_code)
        try:
            coordinates = {axis: float(point[axis]) for axis in ("x", "y", "z")}
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(reason_code) from exc
        if any(not math.isfinite(value) for value in coordinates.values()):
            raise ValueError(reason_code)
        normalized.append(coordinates)
    return normalized


def _task_path_event(
    *,
    kind: str,
    bag_time_s: float,
    source_timestamp_s: float | None,
    frame_id: str,
    points: list[dict[str, float]],
    source_topic: str,
    profile_id: str,
    vehicle_count: int,
) -> dict[str, Any]:
    if kind not in {"expected", "future"}:
        raise ValueError("operator_map_replay_task_path_kind_invalid")
    if not math.isfinite(bag_time_s) or bag_time_s < 0.0:
        raise ValueError("operator_map_replay_bag_time_invalid")
    if source_timestamp_s is not None and (
        not math.isfinite(source_timestamp_s) or source_timestamp_s < 0.0
    ):
        raise ValueError("operator_map_replay_source_time_invalid")
    if not frame_id:
        raise ValueError("operator_map_replay_task_path_frame_missing")
    if not source_topic.startswith("/"):
        raise ValueError("operator_map_replay_task_path_topic_invalid")
    semantics, vehicle_scope = _path_metadata(profile_id, vehicle_count, kind)
    return {
        "kind": kind,
        "bag_time_s": bag_time_s,
        "source_timestamp_s": source_timestamp_s,
        "semantics": semantics,
        "vehicle_scope": vehicle_scope,
        "source_topic": source_topic,
        "frame_id": frame_id,
        "points": points,
    }


def _expected_path_event_from_message(
    message: Any,
    bag_time: Any,
    *,
    source_topic: str,
    profile_id: str,
    vehicle_count: int,
) -> dict[str, Any]:
    header = getattr(message, "header", None)
    frame_id = str(getattr(header, "frame_id", ""))
    poses = getattr(message, "poses", None)
    points = _bounded_message_points(
        [getattr(getattr(pose, "pose", None), "position", None) for pose in poses]
        if isinstance(poses, (list, tuple))
        else poses,
        "operator_map_replay_expected_path_message_invalid",
    )
    return _task_path_event(
        kind="expected",
        bag_time_s=_time_to_seconds(bag_time, "operator_map_replay_bag_time_invalid"),
        source_timestamp_s=_header_source_timestamp(header),
        frame_id=frame_id,
        points=points,
        source_topic=source_topic,
        profile_id=profile_id,
        vehicle_count=vehicle_count,
    )


def _future_path_event_from_marker(
    message: Any,
    bag_time: Any,
    *,
    source_topic: str,
    profile_id: str,
    vehicle_count: int,
) -> dict[str, Any] | None:
    add_action = getattr(message, "ADD", None)
    if (
        add_action is None
        or getattr(message, "action", None) != add_action
        or getattr(message, "ns", None) != "B-Spline"
        or getattr(message, "id", 50) >= 50
        or not getattr(message, "points", None)
    ):
        return None
    header = getattr(message, "header", None)
    return _task_path_event(
        kind="future",
        bag_time_s=_time_to_seconds(bag_time, "operator_map_replay_bag_time_invalid"),
        source_timestamp_s=_header_source_timestamp(header),
        frame_id=str(getattr(header, "frame_id", "")),
        points=_bounded_message_points(getattr(message, "points", None), "operator_map_replay_future_path_message_invalid"),
        source_topic=source_topic,
        profile_id=profile_id,
        vehicle_count=vehicle_count,
    )


def _load_rosbag_records(
    path: Path,
    *,
    topics_by_vehicle: dict[str, str],
    expected_path_topic: str,
    future_marker_topic: str,
    profile_id: str,
    vehicle_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read odometry and optional task-path events from one ROS1 bag.

    The event time is the bag record time.  A path is not exposed to the map
    before its own record has appeared in replay, which prevents a later plan
    update from being displayed as if it were known at takeoff.
    """

    try:
        import rosbag  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ValueError("operator_map_replay_rosbag_python_unavailable") from exc

    topic_to_vehicle = {topic: vehicle_id for vehicle_id, topic in topics_by_vehicle.items()}
    requested_topics = list(topic_to_vehicle)
    if expected_path_topic:
        requested_topics.append(expected_path_topic)
    if future_marker_topic:
        requested_topics.append(future_marker_topic)
    samples: list[dict[str, Any]] = []
    task_path_events: list[dict[str, Any]] = []
    try:
        with rosbag.Bag(str(path), "r") as bag:
            for topic, message, bag_time in bag.read_messages(topics=requested_topics):
                if topic in topic_to_vehicle:
                    samples.append(_sample_from_odom(topic_to_vehicle[topic], message, bag_time))
                elif topic == expected_path_topic:
                    task_path_events.append(
                        _expected_path_event_from_message(
                            message,
                            bag_time,
                            source_topic=topic,
                            profile_id=profile_id,
                            vehicle_count=vehicle_count,
                        )
                    )
                elif topic == future_marker_topic:
                    event = _future_path_event_from_marker(
                        message,
                        bag_time,
                        source_topic=topic,
                        profile_id=profile_id,
                        vehicle_count=vehicle_count,
                    )
                    if event is not None:
                        task_path_events.append(event)
    except ValueError:
        raise
    except Exception as exc:  # rosbag exposes several reader-specific exception types.
        raise ValueError("operator_map_replay_rosbag_read_failed") from exc
    return samples, task_path_events


def _normalize_jsonl_task_path_event(
    value: dict[str, Any],
    *,
    kind: str,
    profile_id: str,
    vehicle_count: int,
) -> dict[str, Any]:
    try:
        bag_time_s = float(value["bag_time_s"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("operator_map_replay_bag_time_invalid") from exc
    source_timestamp_raw = value.get("source_timestamp_s")
    if source_timestamp_raw is None:
        source_timestamp_s = None
    else:
        try:
            source_timestamp_s = float(source_timestamp_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("operator_map_replay_source_time_invalid") from exc
    return _task_path_event(
        kind=kind,
        bag_time_s=bag_time_s,
        source_timestamp_s=source_timestamp_s,
        frame_id=str(value.get("frame_id", "")),
        points=_bounded_json_points(value.get("points"), "operator_map_replay_task_path_points_invalid"),
        source_topic=str(value.get("source_topic", "")),
        profile_id=profile_id,
        vehicle_count=vehicle_count,
    )


def _load_jsonl_records(
    path: Path, *, profile_id: str, vehicle_count: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    samples: list[dict[str, Any]] = []
    task_path_events: list[dict[str, Any]] = []
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
        record_type = value.get("record_type", "odom")
        if record_type == "odom":
            sample = dict(value)
            sample.pop("record_type", None)
            samples.append(sample)
            continue
        kind = TASK_PATH_RECORD_TYPES.get(record_type)
        if kind is None:
            raise ValueError(f"operator_map_replay_records_type_invalid:{line_number}")
        try:
            task_path_events.append(
                _normalize_jsonl_task_path_event(
                    value,
                    kind=kind,
                    profile_id=profile_id,
                    vehicle_count=vehicle_count,
                )
            )
        except ValueError as exc:
            raise ValueError(f"{exc}:{line_number}") from exc
    return samples, task_path_events


def _event_to_raw_task_path(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "available",
        "semantics": event["semantics"],
        "vehicle_scope": event["vehicle_scope"],
        "source_topic": event["source_topic"],
        "frame_id": event["frame_id"],
        "updated_at": event["source_timestamp_s"]
        if event["source_timestamp_s"] is not None
        else event["bag_time_s"],
        "points": event["points"],
    }


def _project_replay_task_paths(
    raw_task_paths: dict[str, dict[str, Any]],
    *,
    coordinate_evidence: dict[str, Any] | None,
    run_id: str,
) -> dict[str, dict[str, Any]]:
    _, projected_paths, _ = project_live_operator_map_frame(
        vehicles=[],
        task_paths=raw_task_paths,
        coordinate_evidence=coordinate_evidence,
        run_id=run_id,
    )
    return projected_paths


def _replay_timeline(
    frames: list[dict[str, Any]], task_path_events: list[tuple[int, dict[str, Any]]]
) -> list[float]:
    """Return every telemetry-update time from odometry and recorded paths."""

    times = {float(frame["bag_time_s"]) for frame in frames}
    times.update(float(event["bag_time_s"]) for _, event in task_path_events)
    timeline = sorted(times)
    if not timeline:
        raise ValueError("operator_map_replay_samples_missing")
    return timeline


def _display_update_times(timeline: list[float], max_update_rate_hz: float) -> list[float]:
    """Select bounded UI write times while retaining every raw replay event.

    The caller still walks the complete timeline to retain the latest recorded
    state and task-path events. Geometry validation, actual-track sampling, and
    cross-process telemetry writes are bounded to these display times.
    """

    if max_update_rate_hz <= 0.0 or len(timeline) <= 2:
        return timeline
    minimum_interval_s = 1.0 / max_update_rate_hz
    selected = [timeline[0]]
    for bag_time_s in timeline[1:-1]:
        if bag_time_s - selected[-1] + 1e-9 >= minimum_interval_s:
            selected.append(bag_time_s)
    if timeline[-1] != selected[-1]:
        selected.append(timeline[-1])
    return selected


def _telemetry_payload(manifest: dict[str, Any], map_state: dict[str, Any], *, now: float) -> dict[str, Any]:
    vehicles = map_state["vehicles"]
    playback_state = str(map_state["transport"]["playback_state"])
    runtime_state = "completed" if playback_state == "completed" else "replaying"
    readiness = {
        "schema": "mosim.runtime_status.v1",
        "run_id": manifest["run_id"],
        "status": runtime_state,
        "reason_code": "operator_map_rosbag_replay",
        "vehicle_count": manifest["vehicle_count"],
        "updated_at": now,
    }
    payload = {
        "schema": "mosim.runtime_telemetry.v2",
        "run_id": manifest["run_id"],
        "timestamp": now,
        "vehicle_count": manifest["vehicle_count"],
        "readiness": readiness,
        "vehicles": vehicles,
        "task_paths": map_state["task_paths"],
        "map_state": map_state,
        "mission_status": {
            "transport_state": "replay",
            "fresh": True,
            "terminal": runtime_state == "completed",
            "reason_code": "rosbag_replay_display_only",
        },
    }
    if manifest.get("controller_backend"):
        payload["operator_runtime_status"] = build_operator_runtime_status(
            manifest=manifest,
            state=runtime_state,
            reason_code="operator_map_rosbag_replay",
            updated_at_unix_s=now,
        )
    return payload


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
    expected_path_topic = str(getattr(args, "expected_path_topic", ""))
    future_marker_topic = str(getattr(args, "future_marker_topic", ""))
    source_path = args.bag or args.records_jsonl
    if source_path is None or not source_path.is_file():
        raise ValueError("operator_map_replay_source_missing")
    if args.bag is not None:
        samples, task_path_events = _load_rosbag_records(
            source_path,
            topics_by_vehicle=topics_by_vehicle,
            expected_path_topic=expected_path_topic,
            future_marker_topic=future_marker_topic,
            profile_id=str(manifest.get("experiment_profile_id", "")),
            vehicle_count=vehicle_count,
        )
        source_kind = "ros1_bag"
    else:
        samples, task_path_events = _load_jsonl_records(
            source_path,
            profile_id=str(manifest.get("experiment_profile_id", "")),
            vehicle_count=vehicle_count,
        )
        source_kind = "normalized_rosbag_export_test_only"
    source_sha256 = sha256_file(source_path)
    bag_id = build_bag_id(source_path, source_sha256)
    frames = derive_replay_frames(samples, vehicle_count=vehicle_count, coordinate_evidence=coordinate_evidence)
    task_path_events = sorted(
        enumerate(task_path_events), key=lambda item: (float(item[1]["bag_time_s"]), item[0])
    )
    task_path_topics = {
        kind: topic
        for kind, topic in (("expected", expected_path_topic), ("future", future_marker_topic))
        if topic
    }
    timeline = _replay_timeline(frames, task_path_events)
    try:
        max_update_rate_hz = float(getattr(args, "max_update_rate_hz", 0.0))
    except (TypeError, ValueError) as exc:
        raise ValueError("operator_map_replay_update_rate_invalid") from exc
    if not math.isfinite(max_update_rate_hz) or max_update_rate_hz < 0.0:
        raise ValueError("operator_map_replay_update_rate_invalid")
    display_times = set(_display_update_times(timeline, max_update_rate_hz))
    timeline_start_s = timeline[0]
    timeline_duration_s = timeline[-1] - timeline_start_s
    replay_manifest = build_replay_manifest(
        manifest=manifest,
        source_kind=source_kind,
        source_path=source_path,
        source_sha256=source_sha256,
        bag_id=bag_id,
        odom_topics=topics_by_vehicle,
        task_path_topics=task_path_topics,
        coordinate_evidence=coordinate_evidence,
        coordinate_evidence_sha256=coordinate_evidence_sha256,
        frames=frames,
        timeline_frame_count=len(timeline),
        timeline_duration_s=timeline_duration_s,
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
            "raw_timeline_frame_count": len(timeline),
            "display_update_rate_hz": max_update_rate_hz,
            "updated_at": time.time(),
        },
    )

    sequence = 0
    previous_bag_time_s = timeline_start_s
    frames_by_bag_time = {float(frame["bag_time_s"]): frame for frame in frames}
    task_path_event_index = 0
    active_task_paths: dict[str, dict[str, Any]] = {}
    projected_task_paths: dict[str, dict[str, Any]] = {}
    actual_tracks: dict[str, dict[str, Any]] = {}
    last_vehicles: list[dict[str, Any]] = []
    last_source_timestamp_s: float | None = None
    last_playback_time_s = 0.0
    for bag_time_s in timeline:
        playback_time_s = bag_time_s - timeline_start_s
        if not args.no_wait:
            delay = max(0.0, bag_time_s - previous_bag_time_s) / args.speed
            if delay > 0.0:
                time.sleep(delay)
        previous_bag_time_s = bag_time_s
        frame = frames_by_bag_time.get(bag_time_s)
        if frame is not None:
            last_vehicles = frame["vehicles"]
            if frame["source_timestamp_s"] is not None:
                last_source_timestamp_s = frame["source_timestamp_s"]
        now = time.time()
        while (
            task_path_event_index < len(task_path_events)
            and float(task_path_events[task_path_event_index][1]["bag_time_s"]) <= bag_time_s
        ):
            event = task_path_events[task_path_event_index][1]
            active_task_paths[str(event["kind"])] = _event_to_raw_task_path(event)
            if event["source_timestamp_s"] is not None:
                last_source_timestamp_s = event["source_timestamp_s"]
            task_path_event_index += 1
        if task_path_event_index > 0:
            projected_task_paths = _project_replay_task_paths(
                active_task_paths,
                coordinate_evidence=coordinate_evidence,
                run_id=str(manifest["run_id"]),
            )
        if bag_time_s not in display_times:
            last_playback_time_s = playback_time_s
            continue
        sequence += 1
        map_state, actual_tracks = build_operator_map_state_or_rejected(
            manifest=manifest,
            map_snapshot=map_snapshot,
            transport_mode="rosbag_replay",
            sequence=sequence,
            received_at_unix_s=now,
            source_timestamp_s=last_source_timestamp_s,
            playback_state="playing",
            playback_time_s=playback_time_s,
            bag_id=bag_id,
            vehicles=last_vehicles,
            task_paths=projected_task_paths,
            actual_tracks=actual_tracks,
            map_data_status={"state": "accepted", "reason_code": ""},
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
                "playback_time_s": playback_time_s,
                "raw_timeline_frame_count": len(timeline),
                "display_update_rate_hz": max_update_rate_hz,
                "updated_at": now,
            },
        )
        last_playback_time_s = playback_time_s

    sequence += 1
    now = time.time()
    completed_state, actual_tracks = build_operator_map_state_or_rejected(
        manifest=manifest,
        map_snapshot=map_snapshot,
        transport_mode="rosbag_replay",
        sequence=sequence,
        received_at_unix_s=now,
        source_timestamp_s=last_source_timestamp_s,
        playback_state="completed",
        playback_time_s=last_playback_time_s,
        bag_id=bag_id,
        vehicles=last_vehicles,
        task_paths=projected_task_paths,
        actual_tracks=actual_tracks,
        map_data_status={"state": "accepted", "reason_code": ""},
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
            "playback_time_s": last_playback_time_s,
            "raw_timeline_frame_count": len(timeline),
            "display_update_rate_hz": max_update_rate_hz,
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
    parser.add_argument(
        "--expected-path-topic",
        default="",
        help="Optional ROS1 nav_msgs/Path topic recorded in the bag for task expected trajectory.",
    )
    parser.add_argument(
        "--future-marker-topic",
        default="",
        help="Optional ROS1 visualization_msgs/Marker topic recorded in the bag for future planner trajectory.",
    )
    parser.add_argument("--coordinate-evidence", type=Path)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument(
        "--max-update-rate-hz",
        type=float,
        default=0.0,
        help="Maximum QGC telemetry-write rate; 0 keeps every recorded update.",
    )
    parser.add_argument("--no-wait", action="store_true", help="Write frames immediately for deterministic tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not math.isfinite(args.speed) or args.speed <= 0.0:
        raise SystemExit("operator_map_replay_speed_invalid")
    if not math.isfinite(args.max_update_rate_hz) or args.max_update_rate_hz < 0.0:
        raise SystemExit("operator_map_replay_update_rate_invalid")
    try:
        return run_replay(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
