#!/usr/bin/env python3
"""Forward a fresh QGC Plan View target into the live ROS1 planner input.

QGC writes one request under the active run directory. This bridge validates
that request against the frozen run, the active-run pointer, and the verified
Factory coordinate evidence before it publishes exactly one standard
``geometry_msgs/PoseStamped`` on the planner's RViz-compatible goal topic.

The bridge never consumes rosbag data and never publishes a PX4, MAVROS, or
motor command. A ``forwarded`` status means the ROS publisher observed a
subscriber and published the planner input. It is not planner, controller, or
flight acceptance.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ui.factory_map_coordinates import world_for_coordinate
from src.orchestration.operator_map_replay import (
    canonical_json_hash,
    load_coordinate_evidence,
)
from src.orchestration.run_manifest_contract import validate_run_manifest_v2


GOAL_REQUEST_SCHEMA = "mosim.qgc_realtime_goal_request.v1"
WAYPOINT_PLAN_REQUEST_SCHEMA = "mosim.qgc_realtime_goal_request.v2"
GOAL_STATUS_SCHEMA = "mosim.qgc_realtime_goal_status.v1"
ACTIVE_POINTER_SCHEMA = "mosim.qgc_active_run_pointer.v1"
SINGLE_GOAL_SOURCE = "qgc_plan_view"
WAYPOINT_PLAN_SOURCE = "qgc_mission_waypoint_plan"
MAX_WAYPOINT_PLAN_ITEMS = 64
MAP_IDENTITY_FIELDS = (
    "map_id",
    "map_version",
    "asset_sha256",
    "world_frame",
    "coordinate_contract_id",
)
REQUEST_ID_PATTERN = re.compile(r"^qgc-goal-[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")


def _mapping(value: Any, reason_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(reason_code)
    return value


def _required_string(value: Any, reason_code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(reason_code)
    return value


def _finite(value: Any, reason_code: str) -> float:
    if isinstance(value, bool):
        raise ValueError(reason_code)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(reason_code) from exc
    if not math.isfinite(number):
        raise ValueError(reason_code)
    return number


def ros_time_seconds(value: Any, reason_code: str) -> float:
    """Return a ROS time value in seconds without accepting an invalid clock."""

    to_sec = getattr(value, "to_sec", None)
    return _finite(to_sec() if callable(to_sec) else value, reason_code)


def read_json_object(path: Path, reason_code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(reason_code) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(reason_code) from exc
    return _mapping(value, reason_code)


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(dict(value), stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def validate_active_pointer(active: Any, *, manifest: Mapping[str, Any]) -> dict[str, Any]:
    pointer = _mapping(active, "qgc_realtime_goal_active_pointer_invalid")
    run_id = _required_string(manifest.get("run_id"), "qgc_realtime_goal_manifest_run_id_missing")
    if (
        pointer.get("schema") != ACTIVE_POINTER_SCHEMA
        or pointer.get("state") != "running"
        or pointer.get("run_id") != run_id
        or pointer.get("run_directory") != f"Results/runs/{run_id}"
        or pointer.get("experiment_profile_id") != manifest.get("experiment_profile_id")
        or pointer.get("experiment_profile_hash") != manifest.get("experiment_profile_hash")
        or pointer.get("runtime_profile_id") != manifest.get("runtime_profile_id")
    ):
        raise ValueError("qgc_realtime_goal_active_run_not_running")
    return pointer


def _normalize_waypoint(value: Any, *, reason_prefix: str, sequence: int) -> dict[str, Any]:
    waypoint = _mapping(value, f"{reason_prefix}_invalid")
    latitude = _finite(waypoint.get("latitude_deg"), f"{reason_prefix}_latitude_invalid")
    longitude = _finite(waypoint.get("longitude_deg"), f"{reason_prefix}_longitude_invalid")
    qgc_altitude = _finite(waypoint.get("qgc_altitude_m"), f"{reason_prefix}_altitude_invalid")
    if not -90.0 <= latitude <= 90.0 or not -180.0 <= longitude <= 180.0:
        raise ValueError("qgc_realtime_goal_request_coordinate_out_of_range")
    return {
        "sequence": sequence,
        "latitude_deg": latitude,
        "longitude_deg": longitude,
        "qgc_altitude_m": qgc_altitude,
    }


def _normalize_waypoint_plan(raw: Mapping[str, Any]) -> list[dict[str, Any]]:
    waypoints = raw.get("waypoints")
    if not isinstance(waypoints, list) or not waypoints:
        raise ValueError("qgc_realtime_waypoint_plan_items_missing")
    if len(waypoints) > MAX_WAYPOINT_PLAN_ITEMS:
        raise ValueError("qgc_realtime_waypoint_plan_items_exceed_limit")

    normalized: list[dict[str, Any]] = []
    previous_sequence = 0
    for index, waypoint in enumerate(waypoints):
        raw_waypoint = _mapping(waypoint, "qgc_realtime_waypoint_plan_item_invalid")
        sequence_value = _finite(
            raw_waypoint.get("sequence"),
            "qgc_realtime_waypoint_plan_sequence_invalid",
        )
        if not sequence_value.is_integer():
            raise ValueError("qgc_realtime_waypoint_plan_sequence_invalid")
        sequence = int(sequence_value)
        if sequence < 1 or sequence <= previous_sequence:
            raise ValueError("qgc_realtime_waypoint_plan_sequence_invalid")
        normalized.append(
            _normalize_waypoint(
                raw_waypoint,
                reason_prefix=f"qgc_realtime_waypoint_plan_item_{index}",
                sequence=sequence,
            )
        )
        previous_sequence = sequence
    return normalized


def _task_bounds(snapshot: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, float]]:
    """Read the frozen Factory L2 task overlay that bounds live QGC goals."""

    if snapshot.get("map_id") != "factory_l2":
        raise ValueError("qgc_realtime_goal_map_not_factory_l2")
    anchor = _mapping(
        snapshot.get("simulation_geodetic_anchor"),
        "qgc_realtime_goal_geodetic_anchor_missing",
    )
    raw_bounds = _mapping(
        snapshot.get("indoor_task_overlay_bounds_m"),
        "qgc_realtime_goal_task_boundary_missing",
    )
    bounds = {
        "min_x_m": _finite(raw_bounds.get("min_x_m"), "qgc_realtime_goal_task_boundary_invalid"),
        "max_x_m": _finite(raw_bounds.get("max_x_m"), "qgc_realtime_goal_task_boundary_invalid"),
        "min_y_m": _finite(raw_bounds.get("min_y_m"), "qgc_realtime_goal_task_boundary_invalid"),
        "max_y_m": _finite(raw_bounds.get("max_y_m"), "qgc_realtime_goal_task_boundary_invalid"),
    }
    if bounds["min_x_m"] >= bounds["max_x_m"] or bounds["min_y_m"] >= bounds["max_y_m"]:
        raise ValueError("qgc_realtime_goal_task_boundary_invalid")
    return anchor, bounds


def _validate_task_boundary(goals: list[dict[str, Any]], snapshot: Mapping[str, Any]) -> None:
    """Reject QGC targets outside the Factory L2 task overlay before ROS publication."""

    anchor, bounds = _task_bounds(snapshot)
    for goal in goals:
        try:
            world = world_for_coordinate(anchor, goal["latitude_deg"], goal["longitude_deg"])
        except (KeyError, ValueError) as exc:
            raise ValueError("qgc_realtime_goal_coordinate_conversion_invalid") from exc
        if not (
            bounds["min_x_m"] <= world["x_m"] <= bounds["max_x_m"]
            and bounds["min_y_m"] <= world["y_m"] <= bounds["max_y_m"]
        ):
            raise ValueError("qgc_realtime_goal_request_outside_task_boundary")


def normalize_goal_request(request: Any, *, manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate QGC planner-input requests without importing ROS.

    QGC altitude remains an audit value. The outgoing topic is equivalent to
    RViz 2D Nav Goal, so the running planner adapter owns the flight height.
    A waypoint plan is released one item at a time by the live ready signal.
    """

    raw = _mapping(request, "qgc_realtime_goal_request_invalid")
    run_id = _required_string(manifest.get("run_id"), "qgc_realtime_goal_manifest_run_id_missing")
    snapshot = _mapping(
        manifest.get("operator_map_snapshot"),
        "qgc_realtime_goal_manifest_map_snapshot_missing",
    )
    snapshot_hash = _required_string(
        manifest.get("operator_map_snapshot_hash"),
        "qgc_realtime_goal_manifest_map_snapshot_hash_missing",
    )
    if canonical_json_hash(snapshot) != snapshot_hash:
        raise ValueError("qgc_realtime_goal_manifest_map_snapshot_hash_mismatch")
    request_id = _required_string(raw.get("request_id"), "qgc_realtime_goal_request_id_missing")
    if REQUEST_ID_PATTERN.fullmatch(request_id) is None:
        raise ValueError("qgc_realtime_goal_request_id_invalid")

    schema = raw.get("schema")
    source = raw.get("source")
    is_single_goal = schema == GOAL_REQUEST_SCHEMA and source == SINGLE_GOAL_SOURCE
    is_waypoint_plan = schema == WAYPOINT_PLAN_REQUEST_SCHEMA and source == WAYPOINT_PLAN_SOURCE
    if (
        not (is_single_goal or is_waypoint_plan)
        or raw.get("state") != "submitted"
        or raw.get("run_id") != run_id
        or raw.get("experiment_profile_id") != manifest.get("experiment_profile_id")
        or raw.get("experiment_profile_hash") != manifest.get("experiment_profile_hash")
        or raw.get("runtime_profile_id") != manifest.get("runtime_profile_id")
    ):
        raise ValueError("qgc_realtime_goal_request_identity_mismatch")

    request_map = _mapping(raw.get("operator_map"), "qgc_realtime_goal_request_map_missing")
    if request_map.get("operator_map_snapshot_hash") != snapshot_hash:
        raise ValueError("qgc_realtime_goal_request_map_snapshot_mismatch")
    for field in MAP_IDENTITY_FIELDS:
        if request_map.get(field) != snapshot.get(field):
            raise ValueError("qgc_realtime_goal_request_map_identity_mismatch")

    if is_single_goal:
        goals = [
            _normalize_waypoint(
                raw.get("goal"),
                reason_prefix="qgc_realtime_goal_request_goal",
                sequence=1,
            )
        ]
        request_kind = "single_goal"
    else:
        goals = _normalize_waypoint_plan(raw)
        request_kind = "waypoint_plan"

    _validate_task_boundary(goals, snapshot)
    submitted_at = _finite(raw.get("submitted_at_unix_s"), "qgc_realtime_goal_request_time_invalid")
    if submitted_at <= 0.0:
        raise ValueError("qgc_realtime_goal_request_time_invalid")
    normalized = {
        "schema": schema,
        "state": "submitted",
        "request_id": request_id,
        "run_id": run_id,
        "experiment_profile_id": manifest["experiment_profile_id"],
        "experiment_profile_hash": manifest["experiment_profile_hash"],
        "runtime_profile_id": manifest["runtime_profile_id"],
        "submitted_at_unix_s": submitted_at,
        "source": source,
        "request_kind": request_kind,
        "operator_map": dict(request_map),
        "goals": goals,
        # Keep the v1-compatible alias for consumers that only need the first point.
        "goal": goals[0],
    }
    if is_waypoint_plan:
        # Revalidation before each ROS publication uses this normalized object.
        normalized["waypoints"] = goals
    return normalized


def validate_request_freshness(
    request: Mapping[str, Any],
    *,
    now_unix_s: float,
    max_request_age_s: float,
    max_future_skew_s: float,
) -> float:
    submitted_at = _finite(request.get("submitted_at_unix_s"), "qgc_realtime_goal_request_time_invalid")
    now = _finite(now_unix_s, "qgc_realtime_goal_clock_invalid")
    if max_request_age_s <= 0.0 or max_future_skew_s < 0.0:
        raise ValueError("qgc_realtime_goal_request_age_policy_invalid")
    age_s = now - submitted_at
    if age_s > max_request_age_s:
        raise ValueError("qgc_realtime_goal_request_stale")
    if age_s < -max_future_skew_s:
        raise ValueError("qgc_realtime_goal_request_from_future")
    return max(0.0, age_s)


def waypoint_plan_progress(
    *,
    started_sim_time_s: float,
    current_sim_time_s: float,
    started_wall_time_s: float,
    current_wall_time_s: float,
    last_sim_time_s: float,
    last_sim_progress_wall_time_s: float,
    max_sim_duration_s: float,
    max_wall_stall_s: float,
) -> dict[str, float | str]:
    """Measure a released waypoint plan in the simulator's clock domain.

    The request submission timestamp remains a wall-clock freshness guard until
    the first waypoint is released. Once the mission owns the sequence, a
    slower-than-realtime Gazebo run must consume the plan budget in ROS time.
    A separate wall-clock stall limit still rejects a stopped /clock stream.
    """

    values = (
        started_sim_time_s,
        current_sim_time_s,
        started_wall_time_s,
        current_wall_time_s,
        last_sim_time_s,
        last_sim_progress_wall_time_s,
        max_sim_duration_s,
        max_wall_stall_s,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("qgc_realtime_waypoint_plan_clock_invalid")
    if max_sim_duration_s <= 0.0 or max_wall_stall_s <= 0.0:
        raise ValueError("qgc_realtime_waypoint_plan_clock_policy_invalid")

    sim_elapsed_s = current_sim_time_s - started_sim_time_s
    wall_elapsed_s = current_wall_time_s - started_wall_time_s
    if sim_elapsed_s < 0.0 or wall_elapsed_s < 0.0 or current_sim_time_s < last_sim_time_s:
        raise ValueError("qgc_realtime_waypoint_plan_clock_regressed")
    if current_sim_time_s > last_sim_time_s:
        last_sim_time_s = current_sim_time_s
        last_sim_progress_wall_time_s = current_wall_time_s
    sim_clock_stall_s = current_wall_time_s - last_sim_progress_wall_time_s
    if sim_clock_stall_s < 0.0:
        raise ValueError("qgc_realtime_waypoint_plan_clock_regressed")
    actual_rtf = sim_elapsed_s / wall_elapsed_s if wall_elapsed_s > 0.0 else 0.0
    if sim_elapsed_s > max_sim_duration_s:
        state = "sim_duration_exceeded"
    elif sim_clock_stall_s >= max_wall_stall_s:
        state = "sim_clock_stalled"
    else:
        state = "running"
    return {
        "state": state,
        "sim_elapsed_s": sim_elapsed_s,
        "wall_elapsed_s": wall_elapsed_s,
        "actual_rtf": actual_rtf,
        "sim_clock_stall_s": sim_clock_stall_s,
        "last_observed_sim_time_s": last_sim_time_s,
        "last_sim_progress_wall_time_s": last_sim_progress_wall_time_s,
    }


def _target_to_source(
    position: Mapping[str, float],
    *,
    matrix: list[list[float]],
) -> dict[str, float]:
    """Invert a validated rigid target-from-source transform."""

    shifted = [
        float(position["x"]) - matrix[0][3],
        float(position["y"]) - matrix[1][3],
        float(position["z"]) - matrix[2][3],
    ]
    return {
        axis: sum(matrix[column][row] * shifted[column] for column in range(3))
        for row, axis in enumerate(("x", "y", "z"))
    }


def build_live_goal(
    request: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    coordinate_evidence: Mapping[str, Any],
    goal_frame: str,
    ground_z_m: float,
    waypoint_index: int = 0,
) -> dict[str, Any]:
    """Convert the QGC geographic point into the standard ROS planner goal."""

    snapshot = _mapping(
        manifest.get("operator_map_snapshot"),
        "qgc_realtime_goal_manifest_map_snapshot_missing",
    )
    anchor = _mapping(
        snapshot.get("simulation_geodetic_anchor"),
        "qgc_realtime_goal_geodetic_anchor_missing",
    )
    normalized = normalize_goal_request(request, manifest=manifest)
    goals = normalized["goals"]
    if not isinstance(waypoint_index, int) or waypoint_index < 0 or waypoint_index >= len(goals):
        raise ValueError("qgc_realtime_waypoint_plan_index_invalid")
    qgc_goal = goals[waypoint_index]
    world = world_for_coordinate(
        anchor,
        qgc_goal["latitude_deg"],
        qgc_goal["longitude_deg"],
    )
    target_frame = _required_string(
        coordinate_evidence.get("target_frame_id"),
        "qgc_realtime_goal_coordinate_target_frame_missing",
    )
    source_frame = _required_string(
        coordinate_evidence.get("source_frame_id"),
        "qgc_realtime_goal_coordinate_source_frame_missing",
    )
    if target_frame != snapshot.get("world_frame"):
        raise ValueError("qgc_realtime_goal_coordinate_target_frame_mismatch")
    requested_goal_frame = _required_string(goal_frame, "qgc_realtime_goal_output_frame_missing")
    target_position = {
        "x": _finite(world.get("x_m"), "qgc_realtime_goal_world_coordinate_invalid"),
        "y": _finite(world.get("y_m"), "qgc_realtime_goal_world_coordinate_invalid"),
        "z": _finite(ground_z_m, "qgc_realtime_goal_ground_z_invalid"),
    }
    if requested_goal_frame == target_frame:
        output_position = target_position
    elif requested_goal_frame == source_frame:
        matrix = coordinate_evidence.get("transform_target_from_source_4x4")
        if not isinstance(matrix, list) or len(matrix) != 4:
            raise ValueError("qgc_realtime_goal_coordinate_matrix_invalid")
        output_position = _target_to_source(target_position, matrix=matrix)
    else:
        raise ValueError("qgc_realtime_goal_output_frame_not_evidence_bound")
    return {
        "request_id": normalized["request_id"],
        "run_id": normalized["run_id"],
        "request_kind": normalized["request_kind"],
        "waypoint_index": waypoint_index,
        "waypoint_count": len(goals),
        "frame_id": requested_goal_frame,
        "position": output_position,
        "qgc_goal": qgc_goal,
        "map_world_position": target_position,
    }


def build_goal_status(
    *,
    manifest: Mapping[str, Any],
    state: str,
    reason_code: str,
    request_id: str = "",
    details: Mapping[str, Any] | None = None,
    now_unix_s: float | None = None,
) -> dict[str, Any]:
    run_id = _required_string(manifest.get("run_id"), "qgc_realtime_goal_manifest_run_id_missing")
    if state not in {"ready", "awaiting_subscriber", "awaiting_mission_ready", "forwarded", "rejected"}:
        raise ValueError("qgc_realtime_goal_status_state_invalid")
    result: dict[str, Any] = {
        "schema": GOAL_STATUS_SCHEMA,
        "run_id": run_id,
        "request_id": request_id,
        "state": state,
        "reason_code": reason_code,
        "updated_at_unix_s": time.time() if now_unix_s is None else float(now_unix_s),
        "claim_boundary": (
            "Live ROS1 planner-input transport only. This does not prove planner acceptance, "
            "trajectory freshness, controller tracking, PX4/MAVROS output, or flight success."
        ),
    }
    if details:
        result["details"] = dict(details)
    return result


def load_runtime_context(
    *,
    run_dir: Path,
    coordinate_evidence_path: Path,
    active_pointer_path: Path,
) -> dict[str, Any]:
    manifest = read_json_object(run_dir / "RUN_MANIFEST.json", "qgc_realtime_goal_manifest_unreadable")
    validate_run_manifest_v2(manifest)
    validate_active_pointer(
        read_json_object(active_pointer_path, "qgc_realtime_goal_active_pointer_unreadable"),
        manifest=manifest,
    )
    snapshot = _mapping(
        manifest.get("operator_map_snapshot"),
        "qgc_realtime_goal_manifest_map_snapshot_missing",
    )
    snapshot_hash = _required_string(
        manifest.get("operator_map_snapshot_hash"),
        "qgc_realtime_goal_manifest_map_snapshot_hash_missing",
    )
    evidence, evidence_sha256 = load_coordinate_evidence(
        coordinate_evidence_path,
        map_snapshot=snapshot,
        snapshot_hash=snapshot_hash,
    )
    return {
        "manifest": manifest,
        "coordinate_evidence": evidence,
        "coordinate_evidence_sha256": evidence_sha256,
    }


class RealtimeGoalBridge:
    """ROS-dependent delivery loop, deliberately separated from pure checks."""

    def __init__(
        self,
        *,
        args: argparse.Namespace,
        rospy: Any,
        pose_stamped_type: Any,
        bool_type: Any | None = None,
        uint16_type: Any | None = None,
    ) -> None:
        self.args = args
        self.rospy = rospy
        self.pose_stamped_type = pose_stamped_type
        self.run_dir = args.run_dir.resolve()
        self.request_path = self.run_dir / "operator_goal" / "REQUEST.json"
        self.status_path = self.run_dir / "operator_goal" / "STATUS.json"
        self.publisher = rospy.Publisher(args.goal_topic, pose_stamped_type, queue_size=1, latch=False)
        self.waypoint_plan_size_type = uint16_type
        self.waypoint_plan_size_publisher = (
            rospy.Publisher(args.waypoint_plan_size_topic, uint16_type, queue_size=1, latch=False)
            if uint16_type is not None
            else None
        )
        self.context = load_runtime_context(
            run_dir=self.run_dir,
            coordinate_evidence_path=args.coordinate_evidence.resolve(),
            active_pointer_path=args.active_pointer.resolve(),
        )
        self._seen_request_id = self._current_request_id()
        self._pending: tuple[dict[str, Any], dict[str, Any]] | None = None
        self._pending_waypoint_index = 0
        self._pending_observed_not_ready = False
        self._pending_waypoint_plan_size_published = False
        self._waypoint_plan_started_sim_time_s: float | None = None
        self._waypoint_plan_started_wall_time_s: float | None = None
        self._waypoint_plan_last_sim_time_s: float | None = None
        self._waypoint_plan_last_sim_progress_wall_time_s: float | None = None
        self._mission_ready: bool | None = None
        self._bridge_ready = False
        self._waiting_for_subscriber_reported = False
        self._retry_ready_pending = False
        self._retry_ready_requires_mission_ready = False
        if bool_type is not None:
            rospy.Subscriber(
                args.mission_ready_topic,
                bool_type,
                self._on_mission_ready,
                queue_size=5,
            )
        self._refresh_idle_readiness()

    def _on_mission_ready(self, message: Any) -> None:
        self._mission_ready = bool(getattr(message, "data", False))
        if not self._mission_ready:
            self._pending_observed_not_ready = True

    def _current_request_id(self) -> str:
        try:
            value = read_json_object(self.request_path, "qgc_realtime_goal_request_unreadable")
        except ValueError:
            return ""
        request_id = value.get("request_id")
        return request_id if isinstance(request_id, str) else ""

    def _write_status(
        self,
        state: str,
        reason_code: str,
        *,
        request_id: str = "",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        atomic_write_json(
            self.status_path,
            build_goal_status(
                manifest=self.context["manifest"],
                state=state,
                reason_code=reason_code,
                request_id=request_id,
                details=details,
            ),
        )

    def _request_details(
        self,
        request: Mapping[str, Any],
        *,
        forwarded_waypoint_count: int,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        goals = request.get("goals")
        waypoint_count = len(goals) if isinstance(goals, list) else 0
        details: dict[str, Any] = {
            "request_kind": request.get("request_kind"),
            "waypoint_count": waypoint_count,
            "forwarded_waypoint_count": forwarded_waypoint_count,
            "mission_ready_topic": self.args.mission_ready_topic,
            "mission_ready": self._mission_ready,
            "waypoint_plan_size_topic": self.args.waypoint_plan_size_topic,
        }
        if self.waypoint_plan_size_publisher is not None:
            details["waypoint_plan_size_subscriber_count"] = int(
                self.waypoint_plan_size_publisher.get_num_connections()
            )
        if 0 <= self._pending_waypoint_index < waypoint_count:
            waypoint = goals[self._pending_waypoint_index]
            if isinstance(waypoint, dict):
                details["next_waypoint_sequence"] = waypoint.get("sequence")
        if extra:
            details.update(extra)
        return details

    def _waypoint_plan_clock_details(self) -> dict[str, float | str]:
        if (
            self._waypoint_plan_started_sim_time_s is None
            or self._waypoint_plan_started_wall_time_s is None
            or self._waypoint_plan_last_sim_time_s is None
            or self._waypoint_plan_last_sim_progress_wall_time_s is None
        ):
            return {}
        details = waypoint_plan_progress(
            started_sim_time_s=self._waypoint_plan_started_sim_time_s,
            current_sim_time_s=ros_time_seconds(
                self.rospy.Time.now(),
                "qgc_realtime_waypoint_plan_sim_clock_invalid",
            ),
            started_wall_time_s=self._waypoint_plan_started_wall_time_s,
            current_wall_time_s=time.time(),
            last_sim_time_s=self._waypoint_plan_last_sim_time_s,
            last_sim_progress_wall_time_s=self._waypoint_plan_last_sim_progress_wall_time_s,
            max_sim_duration_s=self.args.max_waypoint_plan_duration_s,
            max_wall_stall_s=self.args.max_waypoint_plan_wall_stall_s,
        )
        self._waypoint_plan_last_sim_time_s = float(details["last_observed_sim_time_s"])
        self._waypoint_plan_last_sim_progress_wall_time_s = float(
            details["last_sim_progress_wall_time_s"]
        )
        return details

    def _clear_waypoint_plan_clock(self) -> None:
        self._waypoint_plan_started_sim_time_s = None
        self._waypoint_plan_started_wall_time_s = None
        self._waypoint_plan_last_sim_time_s = None
        self._waypoint_plan_last_sim_progress_wall_time_s = None

    def _cancel_waypoint_plan(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Release the mission-side sequence gate after a rejected plan."""

        if (
            request.get("request_kind") != "waypoint_plan"
            or not self._pending_waypoint_plan_size_published
            or self.waypoint_plan_size_publisher is None
            or self.waypoint_plan_size_type is None
        ):
            return {}
        message = self.waypoint_plan_size_type()
        message.data = 0
        self.waypoint_plan_size_publisher.publish(message)
        self._pending_waypoint_plan_size_published = False
        return {
            "waypoint_plan_cancel_published": True,
            "waypoint_plan_size_topic": self.args.waypoint_plan_size_topic,
            "waypoint_plan_size": 0,
        }

    def _reject_pending_request(
        self,
        request: Mapping[str, Any],
        reason_code: str,
        *,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        cancellation = self._cancel_waypoint_plan(request)
        self._retry_ready_pending = True
        self._retry_ready_requires_mission_ready = bool(
            cancellation.get("waypoint_plan_cancel_published")
        )
        self._write_status(
            "rejected",
            reason_code,
            request_id=request["request_id"],
            details=self._request_details(
                request,
                forwarded_waypoint_count=self._pending_waypoint_index,
                extra={**dict(extra or {}), **cancellation} or None,
            ),
        )
        self._pending = None
        self._clear_waypoint_plan_clock()

    def _refresh_idle_readiness(self) -> None:
        """Expose Plan Goal only after the live planner subscribes."""

        if self._bridge_ready:
            if (
                self._retry_ready_pending
                and self._pending is None
                and (
                    not self._retry_ready_requires_mission_ready
                    or self._mission_ready is True
                )
            ):
                self._write_status(
                    "ready",
                    "waiting_for_new_qgc_goal_after_rejection",
                    details={
                        "goal_topic": self.args.goal_topic,
                        "subscriber_count": int(self.publisher.get_num_connections()),
                    },
                )
                self._retry_ready_pending = False
                self._retry_ready_requires_mission_ready = False
            return
        subscriber_count = int(self.publisher.get_num_connections())
        if subscriber_count >= 1:
            if (
                self.waypoint_plan_size_publisher is not None
                and int(self.waypoint_plan_size_publisher.get_num_connections()) < 1
            ):
                self._write_status(
                    "awaiting_subscriber",
                    "qgc_realtime_goal_waypoint_plan_size_subscriber_missing",
                    details={
                        "goal_topic": self.args.goal_topic,
                        "subscriber_count": subscriber_count,
                        "waypoint_plan_size_topic": self.args.waypoint_plan_size_topic,
                        "waypoint_plan_size_subscriber_count": int(
                            self.waypoint_plan_size_publisher.get_num_connections()
                        ),
                    },
                )
                return
            self._bridge_ready = True
            self._write_status(
                "ready",
                "waiting_for_new_qgc_goal",
                details={
                    "goal_topic": self.args.goal_topic,
                    "subscriber_count": subscriber_count,
                },
            )
        elif not self._waiting_for_subscriber_reported:
            self._waiting_for_subscriber_reported = True
            self._write_status(
                "awaiting_subscriber",
                "qgc_realtime_goal_planner_subscriber_missing",
                details={
                    "goal_topic": self.args.goal_topic,
                    "subscriber_count": subscriber_count,
                },
            )

    def _load_validated_request_context(
        self,
        request: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Bind a request to the runtime context immediately before use."""

        context = load_runtime_context(
            run_dir=self.run_dir,
            coordinate_evidence_path=self.args.coordinate_evidence.resolve(),
            active_pointer_path=self.args.active_pointer.resolve(),
        )
        return normalize_goal_request(request, manifest=context["manifest"]), context

    def _read_new_request(self) -> None:
        try:
            raw = read_json_object(self.request_path, "qgc_realtime_goal_request_unreadable")
        except ValueError:
            return
        request_id = raw.get("request_id")
        if not isinstance(request_id, str) or request_id == self._seen_request_id:
            return
        self._seen_request_id = request_id
        if self._pending is not None:
            previous_request, _ = self._pending
            self._cancel_waypoint_plan(previous_request)
            self._pending = None
        self._retry_ready_pending = False
        self._retry_ready_requires_mission_ready = False
        try:
            request, context = self._load_validated_request_context(raw)
            self.context = context
        except ValueError as exc:
            self._write_status("rejected", str(exc), request_id=request_id)
            return
        self._pending = (request, context)
        self._pending_waypoint_index = 0
        self._pending_observed_not_ready = self._mission_ready is False
        self._pending_waypoint_plan_size_published = False
        self._clear_waypoint_plan_clock()

    def _forward_pending_request(self) -> None:
        if self._pending is None:
            return
        request, context = self._pending
        request_id = request["request_id"]
        try:
            # A goal may wait for a planner subscription. Do not release it if
            # the active run or coordinate evidence changed during that wait.
            request, context = self._load_validated_request_context(request)
            self._pending = (request, context)
        except ValueError as exc:
            self.context = context
            self._reject_pending_request(request, str(exc))
            return
        clock_details: dict[str, float | str] = {}
        try:
            if request.get("request_kind") == "waypoint_plan" and self._pending_waypoint_index > 0:
                clock_details = self._waypoint_plan_clock_details()
                if clock_details["state"] == "sim_duration_exceeded":
                    raise ValueError("qgc_realtime_waypoint_plan_sim_duration_exceeded")
                if clock_details["state"] == "sim_clock_stalled":
                    raise ValueError("qgc_realtime_waypoint_plan_sim_clock_stalled")
                age_s = 0.0
            else:
                age_s = validate_request_freshness(
                    request,
                    now_unix_s=time.time(),
                    max_request_age_s=self.args.max_request_age_s,
                    max_future_skew_s=self.args.max_future_skew_s,
                )
        except ValueError as exc:
            self.context = context
            self._reject_pending_request(request, str(exc), extra=clock_details)
            return
        subscriber_count = int(self.publisher.get_num_connections())
        if subscriber_count < 1:
            self.context = context
            self._write_status(
                "awaiting_subscriber",
                "qgc_realtime_goal_planner_subscriber_missing",
                request_id=request_id,
                details=self._request_details(
                    request,
                    forwarded_waypoint_count=self._pending_waypoint_index,
                    extra={
                        "goal_topic": self.args.goal_topic,
                        "subscriber_count": subscriber_count,
                        "request_age_s": age_s,
                    },
                ),
            )
            return
        if (
            self.waypoint_plan_size_publisher is not None
            and not self._pending_waypoint_plan_size_published
        ):
            plan_size_subscriber_count = int(self.waypoint_plan_size_publisher.get_num_connections())
            if plan_size_subscriber_count < 1:
                self.context = context
                self._write_status(
                    "awaiting_subscriber",
                    "qgc_realtime_goal_waypoint_plan_size_subscriber_missing",
                    request_id=request_id,
                    details=self._request_details(
                        request,
                        forwarded_waypoint_count=self._pending_waypoint_index,
                        extra={
                            "goal_topic": self.args.goal_topic,
                            "subscriber_count": subscriber_count,
                        },
                    ),
                )
                return
            goals = request.get("goals")
            if not isinstance(goals, list) or not goals:
                self.context = context
                self._reject_pending_request(request, "qgc_realtime_waypoint_plan_size_invalid")
                return
            message = self.waypoint_plan_size_type()
            message.data = len(goals)
            self.waypoint_plan_size_publisher.publish(message)
            self._pending_waypoint_plan_size_published = True
        if request.get("request_kind") == "waypoint_plan":
            waiting_for_ready_cycle = (
                self._mission_ready is not True
                or (self._pending_waypoint_index > 0 and not self._pending_observed_not_ready)
            )
            if waiting_for_ready_cycle:
                self.context = context
                self._write_status(
                    "awaiting_mission_ready",
                    "qgc_realtime_waypoint_plan_mission_not_ready",
                    request_id=request_id,
                    details=self._request_details(
                        request,
                        forwarded_waypoint_count=self._pending_waypoint_index,
                        extra={
                            "goal_topic": self.args.goal_topic,
                            "subscriber_count": subscriber_count,
                            "request_age_s": age_s,
                            "waiting_for_ready_cycle": self._pending_waypoint_index > 0,
                            **clock_details,
                        },
                    ),
                )
                return
        try:
            outgoing = build_live_goal(
                request,
                manifest=context["manifest"],
                coordinate_evidence=context["coordinate_evidence"],
                goal_frame=self.args.goal_frame,
                ground_z_m=self.args.ground_z_m,
                waypoint_index=self._pending_waypoint_index,
            )
        except ValueError as exc:
            self.context = context
            self._reject_pending_request(request, str(exc))
            return
        message = self.pose_stamped_type()
        message.header.stamp = self.rospy.Time.now()
        message.header.frame_id = outgoing["frame_id"]
        message.pose.position.x = outgoing["position"]["x"]
        message.pose.position.y = outgoing["position"]["y"]
        message.pose.position.z = outgoing["position"]["z"]
        message.pose.orientation.w = 1.0
        self.publisher.publish(message)
        self.context = context
        forwarded_waypoint_count = self._pending_waypoint_index + 1
        if request.get("request_kind") == "waypoint_plan" and self._waypoint_plan_started_sim_time_s is None:
            started_sim_time_s = ros_time_seconds(
                self.rospy.Time.now(),
                "qgc_realtime_waypoint_plan_sim_clock_invalid",
            )
            started_wall_time_s = time.time()
            self._waypoint_plan_started_sim_time_s = started_sim_time_s
            self._waypoint_plan_started_wall_time_s = started_wall_time_s
            self._waypoint_plan_last_sim_time_s = started_sim_time_s
            self._waypoint_plan_last_sim_progress_wall_time_s = started_wall_time_s
            clock_details = self._waypoint_plan_clock_details()
        self._write_status(
            "forwarded",
            (
                "qgc_realtime_waypoint_plan_ros_published"
                if request.get("request_kind") == "waypoint_plan"
                else "qgc_realtime_goal_ros_published"
            ),
            request_id=request_id,
            details=self._request_details(
                request,
                forwarded_waypoint_count=forwarded_waypoint_count,
                extra={
                    "transport": "live_ros1",
                    "goal_topic": self.args.goal_topic,
                    "subscriber_count": subscriber_count,
                    "request_age_s": age_s,
                    "coordinate_evidence_sha256": context["coordinate_evidence_sha256"],
                    "goal": outgoing,
                    **clock_details,
                },
            ),
        )
        goals = request.get("goals")
        goal_count = len(goals) if isinstance(goals, list) else 0
        if forwarded_waypoint_count >= goal_count:
            self._pending = None
            self._clear_waypoint_plan_clock()
            return
        self._pending_waypoint_index = forwarded_waypoint_count
        self._pending_observed_not_ready = False

    def spin(self) -> None:
        # rospy.Rate follows /clock when use_sim_time is enabled. The stall
        # watchdog must continue polling when that clock is frozen.
        poll_interval_s = 1.0 / self.args.poll_hz
        while not self.rospy.is_shutdown():
            self._refresh_idle_readiness()
            self._read_new_request()
            self._forward_pending_request()
            time.sleep(poll_interval_s)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--coordinate-evidence", type=Path, required=True)
    parser.add_argument(
        "--active-pointer",
        type=Path,
        default=ROOT / "Results" / "ui_platform" / "qgc_active_run.json",
    )
    parser.add_argument("--goal-topic", default="/move_base_simple/goal")
    parser.add_argument("--goal-frame", default="world")
    parser.add_argument("--mission-ready-topic", default="/mosim/goal4/interactive_goal_ready")
    parser.add_argument("--waypoint-plan-size-topic", default="/mosim/goal4/interactive_goal_waypoint_count")
    parser.add_argument(
        "--ground-z-m",
        type=float,
        default=0.0,
        help="Ground-plane Z for the RViz-compatible input; planner adapters own flight height.",
    )
    parser.add_argument("--poll-hz", type=float, default=10.0)
    parser.add_argument("--max-request-age-s", type=float, default=5.0)
    parser.add_argument("--max-waypoint-plan-duration-s", type=float, default=600.0)
    parser.add_argument("--max-waypoint-plan-wall-stall-s", type=float, default=120.0)
    parser.add_argument("--max-future-skew-s", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if (
        not args.goal_topic
        or not args.goal_frame
        or not args.mission_ready_topic
        or not args.waypoint_plan_size_topic
        or not math.isfinite(args.ground_z_m)
        or not math.isfinite(args.poll_hz)
        or args.poll_hz <= 0.0
        or not math.isfinite(args.max_request_age_s)
        or args.max_request_age_s <= 0.0
        or not math.isfinite(args.max_waypoint_plan_duration_s)
        or args.max_waypoint_plan_duration_s <= 0.0
        or not math.isfinite(args.max_waypoint_plan_wall_stall_s)
        or args.max_waypoint_plan_wall_stall_s <= 0.0
        or not math.isfinite(args.max_future_skew_s)
        or args.max_future_skew_s < 0.0
    ):
        print(json.dumps({"status": "blocked", "reason_code": "qgc_realtime_goal_arguments_invalid"}))
        return 2
    try:
        import rospy
        from geometry_msgs.msg import PoseStamped
        from std_msgs.msg import Bool, UInt16
    except ImportError:
        print(json.dumps({"status": "blocked", "reason_code": "qgc_realtime_goal_ros1_unavailable"}))
        return 2
    try:
        rospy.init_node("mosim_qgc_realtime_goal_bridge", anonymous=False)
        RealtimeGoalBridge(
            args=args,
            rospy=rospy,
        pose_stamped_type=PoseStamped,
        bool_type=Bool,
        uint16_type=UInt16,
        ).spin()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason_code": str(exc)}, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
