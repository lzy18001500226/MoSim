#!/usr/bin/env python3
"""Publish same-run ROS readiness, telemetry, and audited physical injections."""

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.runtime_sidecar_contract import (
    atomic_write_json,
    evaluate_readiness_status,
    load_contract,
    resolve_gazebo_body_name,
    validate_command,
)
from src.orchestration.operator_map_state import (
    COORDINATE_CONTRACT_STATUSES,
    OPERATOR_MAP_IDENTITY_FIELDS,
    OPERATOR_MAP_STATE_SCHEMA,
    OPERATOR_MAP_TRANSPORT_MODES,
    validate_operator_map_state,
)
from src.orchestration.operator_map_replay import (
    load_coordinate_evidence,
    transform_operator_map_orientation,
    transform_operator_map_points,
    transform_operator_map_vector,
)


OPERATOR_MAP_SNAPSHOT_REQUIRED_FIELDS = (
    "resource_url",
    *OPERATOR_MAP_IDENTITY_FIELDS,
    "coordinate_contract_status",
)


def _canonical_hash(value: Any) -> str:
    import hashlib

    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _json_copy(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _validate_operator_map_snapshot(snapshot: dict[str, Any]) -> None:
    if any(not isinstance(snapshot.get(key), str) or not snapshot[key] for key in OPERATOR_MAP_SNAPSHOT_REQUIRED_FIELDS):
        raise ValueError("operator_map_contract_fields_missing")
    if snapshot["coordinate_contract_status"] not in COORDINATE_CONTRACT_STATUSES:
        raise ValueError("operator_map_coordinate_status_invalid")
    bounds = snapshot.get("world_bounds_m")
    if not isinstance(bounds, dict):
        raise ValueError("operator_map_bounds_invalid")
    try:
        valid_bounds = (
            float(bounds["min_x_m"]) < float(bounds["max_x_m"])
            and float(bounds["min_y_m"]) < float(bounds["max_y_m"])
        )
    except (KeyError, TypeError, ValueError):
        valid_bounds = False
    if not valid_bounds:
        raise ValueError("operator_map_bounds_invalid")


def load_operator_map_snapshot(catalog_path: Path, map_id: str) -> dict[str, Any]:
    """Resolve a registry entry for profile-validation and test fixtures only."""
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("operator_map_catalog_unreadable") from exc
    if catalog.get("schema") != "mosim.operator_map_catalog.v1":
        raise ValueError("operator_map_catalog_schema_invalid")
    maps = catalog.get("maps")
    if not isinstance(maps, list):
        raise ValueError("operator_map_catalog_entries_invalid")
    entry = next(
        (
            item for item in maps
            if isinstance(item, dict) and item.get("map_id") == map_id and item.get("enabled") is True
        ),
        None,
    )
    if entry is None:
        raise ValueError("operator_map_not_enabled")
    _validate_operator_map_snapshot(entry)
    return _json_copy(entry)


def load_manifest_operator_map_snapshot(manifest: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Load the immutable map selected during prepare_run, never a mutable catalog default."""
    snapshot = manifest.get("operator_map_snapshot")
    snapshot_hash = manifest.get("operator_map_snapshot_hash")
    if not isinstance(snapshot, dict) or not snapshot:
        raise ValueError("operator_map_manifest_snapshot_missing")
    if not isinstance(snapshot_hash, str) or not snapshot_hash:
        raise ValueError("operator_map_manifest_snapshot_hash_missing")
    _validate_operator_map_snapshot(snapshot)
    if _canonical_hash(snapshot) != snapshot_hash:
        raise ValueError("operator_map_manifest_snapshot_hash_mismatch")
    return _json_copy(snapshot), snapshot_hash


def resolve_runtime_operator_map(
    manifest: dict[str, Any],
    *,
    requested_map_id: str = "",
    requested_coordinate_contract_id: str = "",
    coordinate_contract_status: str = "",
) -> tuple[dict[str, Any], str]:
    """Apply only runtime validation status to the frozen map identity."""
    snapshot, snapshot_hash = load_manifest_operator_map_snapshot(manifest)
    if requested_map_id and requested_map_id != snapshot["map_id"]:
        raise ValueError("operator_map_cli_map_override_mismatch")
    if requested_coordinate_contract_id and requested_coordinate_contract_id != snapshot["coordinate_contract_id"]:
        raise ValueError("operator_map_cli_coordinate_contract_override_mismatch")
    if coordinate_contract_status and coordinate_contract_status not in COORDINATE_CONTRACT_STATUSES:
        raise ValueError("operator_map_coordinate_status_invalid")
    if coordinate_contract_status == "verified":
        raise ValueError("operator_map_coordinate_evidence_required")
    state_map = _json_copy(snapshot)
    if coordinate_contract_status:
        state_map["coordinate_contract_status"] = coordinate_contract_status
    return state_map, snapshot_hash


def ros_source_timestamp(message: Any) -> float | None:
    """Return a ROS header timestamp without treating local receipt time as source time."""
    header = getattr(message, "header", None)
    stamp = getattr(header, "stamp", None)
    if stamp is None:
        return None
    try:
        value = float(stamp.to_sec()) if hasattr(stamp, "to_sec") else float(stamp.secs) + float(stamp.nsecs) / 1e9
    except (AttributeError, TypeError, ValueError):
        return None
    return value if math.isfinite(value) and value > 0.0 else None


def build_operator_map_state(
    *,
    manifest: dict[str, Any],
    map_snapshot: dict[str, Any],
    transport_mode: str,
    sequence: int,
    received_at_unix_s: float,
    source_timestamp_s: float | None,
    playback_state: str,
    playback_time_s: float | None,
    bag_id: str,
    vehicles: list[dict[str, Any]],
    task_paths: dict[str, dict[str, Any]],
    map_data_status: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Project runtime telemetry into the strict 2D operator-map envelope."""
    if transport_mode not in OPERATOR_MAP_TRANSPORT_MODES:
        raise ValueError("operator_map_transport_mode_invalid")
    if sequence <= 0 or not math.isfinite(received_at_unix_s):
        raise ValueError("operator_map_transport_sequence_or_receive_time_invalid")
    if map_snapshot.get("coordinate_contract_status") not in COORDINATE_CONTRACT_STATUSES:
        raise ValueError("operator_map_coordinate_status_invalid")
    frozen_map, snapshot_hash = load_manifest_operator_map_snapshot(manifest)
    if any(map_snapshot.get(field) != frozen_map.get(field) for field in OPERATOR_MAP_IDENTITY_FIELDS):
        raise ValueError("operator_map_snapshot_identity_mismatch")
    profile_id = manifest.get("experiment_profile_id")
    profile_hash = manifest.get("experiment_profile_hash")
    run_id = manifest.get("run_id")
    if not all(isinstance(value, str) and value for value in (run_id, profile_id, profile_hash)):
        raise ValueError("operator_map_manifest_identity_invalid")
    if transport_mode == "live_ros1":
        playback_state = "live"
        playback_time_s = None
        bag_id = ""
    elif playback_state not in {"playing", "paused", "completed", "failed"}:
        raise ValueError("operator_map_replay_state_invalid")
    elif not bag_id:
        raise ValueError("operator_map_replay_bag_id_missing")
    elif not isinstance(playback_time_s, (int, float)) or not math.isfinite(float(playback_time_s)) or playback_time_s < 0.0:
        raise ValueError("operator_map_replay_time_invalid")

    scenario = manifest.get("scenario_snapshot")
    scenario = scenario if isinstance(scenario, dict) else {}
    state: dict[str, Any] = {
        "schema": OPERATOR_MAP_STATE_SCHEMA,
        "run_id": run_id,
        "profile_id": profile_id,
        "profile_hash": profile_hash,
        "transport": {
            "mode": transport_mode,
            "sequence": sequence,
            "received_at_unix_s": received_at_unix_s,
            "source_timestamp_s": source_timestamp_s,
            "playback_state": playback_state,
            "playback_time_s": playback_time_s,
            "bag_id": bag_id,
        },
        "map": {**dict(map_snapshot), "operator_map_snapshot_hash": snapshot_hash},
        "vehicles": vehicles,
        "task_paths": task_paths,
    }
    if map_data_status is not None:
        state["map_data_status"] = dict(map_data_status)
    boundary = scenario.get("exploration_boundary")
    if isinstance(boundary, dict):
        state["task_boundary"] = boundary
    formation = scenario.get("formation")
    if isinstance(formation, dict) and isinstance(formation.get("target_center_xy_m"), list):
        state["formation_target"] = {"target_center_xy_m": formation["target_center_xy_m"]}
    validate_operator_map_state(state, manifest=manifest)
    return state


def _vector(value: Any) -> dict[str, float]:
    return {axis: float(getattr(value, axis)) for axis in ("x", "y", "z")}


def _quaternion(value: Any) -> dict[str, float]:
    return {axis: float(getattr(value, axis)) for axis in ("w", "x", "y", "z")}


def _sample(message: Any = None) -> tuple[Any, float] | None:
    return None if message is None else (message, time.time())


def _map_vehicle_skeleton(vehicle: dict[str, Any]) -> dict[str, Any]:
    """Keep connection state while withholding unprojected ROS geometry."""

    source_state = vehicle.get("state")
    source_state = source_state if isinstance(source_state, dict) else {}
    return {
        "vehicle_id": str(vehicle.get("vehicle_id", "")),
        "state": {"connected": bool(source_state.get("connected", False))},
    }


def _project_map_vehicle(
    vehicle: dict[str, Any], coordinate_evidence: dict[str, Any]
) -> dict[str, Any]:
    """Convert one telemetry vehicle to the frozen operator-map world frame."""

    projected = _map_vehicle_skeleton(vehicle)
    source_state = vehicle.get("state")
    source_state = source_state if isinstance(source_state, dict) else {}
    position = source_state.get("position")
    if position is None:
        return projected

    source_frame_id = source_state.get("position_frame")
    if source_frame_id != coordinate_evidence["source_frame_id"]:
        raise ValueError("operator_map_coordinate_evidence_source_frame_mismatch")

    target_state = projected["state"]
    target_state["position"] = transform_operator_map_vector(
        coordinate_evidence, position, translate=True
    )
    target_state["position_frame"] = coordinate_evidence["target_frame_id"]
    orientation = source_state.get("orientation")
    if orientation is not None:
        transformed_orientation = transform_operator_map_orientation(coordinate_evidence, orientation)
        if transformed_orientation is not None:
            target_state["orientation"] = transformed_orientation

    for field, pseudovector in (("linear_velocity", False), ("angular_velocity", True)):
        value = source_state.get(field)
        source_velocity_frame = source_state.get(f"{field}_frame")
        # Odometry twist may be body-frame data. It is not safe to display as
        # a Factory-world vector unless the producer explicitly declares the
        # same source frame as the coordinate evidence.
        if value is not None and source_velocity_frame == coordinate_evidence["source_frame_id"]:
            target_state[field] = transform_operator_map_vector(
                coordinate_evidence, value, translate=False, pseudovector=pseudovector
            )
            target_state[f"{field}_frame"] = coordinate_evidence["target_frame_id"]
    return projected


def _path_metadata(path: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    result = {
        key: path[key]
        for key in ("semantics", "vehicle_scope", "source_topic", "updated_at")
        if key in path
    }
    result["run_id"] = run_id
    return result


def _project_map_task_paths(
    task_paths: dict[str, dict[str, Any]],
    *,
    coordinate_evidence: dict[str, Any] | None,
    run_id: str,
) -> dict[str, dict[str, Any]]:
    """Project only paths that explicitly declare the evidence source frame."""

    projected: dict[str, dict[str, Any]] = {}
    for kind in ("expected", "future"):
        path = task_paths.get(kind)
        if not isinstance(path, dict):
            continue
        metadata = _path_metadata(path, run_id=run_id)
        if coordinate_evidence is None:
            projected[kind] = {
                **metadata,
                "status": "pending_coordinate_evidence",
                "reason_code": "operator_map_coordinate_evidence_missing",
            }
            continue
        source_frame_id = path.get("frame_id")
        points = path.get("points")
        if not isinstance(source_frame_id, str) or not isinstance(points, list):
            projected[kind] = {
                **metadata,
                "status": "rejected",
                "reason_code": "operator_map_task_path_source_invalid",
            }
            continue
        try:
            target_points = transform_operator_map_points(
                points,
                source_frame_id=source_frame_id,
                coordinate_evidence=coordinate_evidence,
            )
        except ValueError as exc:
            projected[kind] = {**metadata, "status": "rejected", "reason_code": str(exc)}
            continue
        projected[kind] = {
            **metadata,
            "status": "available",
            "frame_id": coordinate_evidence["target_frame_id"],
            "points": target_points,
        }
    return projected


def project_live_operator_map_frame(
    *,
    vehicles: list[dict[str, Any]],
    task_paths: dict[str, dict[str, Any]],
    coordinate_evidence: dict[str, Any] | None,
    run_id: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, str]]:
    """Build display-only live map data without changing control telemetry.

    A source-frame failure rejects the current map frame, but returns a valid
    empty geometry envelope. The caller can therefore keep publishing runtime
    readiness and flight telemetry without turning a display contract failure
    into a process restart or a control intervention.
    """

    map_paths = _project_map_task_paths(
        task_paths, coordinate_evidence=coordinate_evidence, run_id=run_id
    )
    if coordinate_evidence is None:
        return (
            [_map_vehicle_skeleton(vehicle) for vehicle in vehicles],
            map_paths,
            {"state": "accepted", "reason_code": ""},
        )
    try:
        map_vehicles = [_project_map_vehicle(vehicle, coordinate_evidence) for vehicle in vehicles]
    except ValueError as exc:
        return (
            [_map_vehicle_skeleton(vehicle) for vehicle in vehicles],
            map_paths,
            {"state": "rejected", "reason_code": str(exc)},
        )
    return map_vehicles, map_paths, {"state": "accepted", "reason_code": ""}


def load_mission_status(
    path: Path,
    *,
    expected_run_id: str,
    expected_vehicle_ids: list[str],
    now: float,
    max_age_s: float,
) -> dict[str, Any]:
    unavailable = {
        "transport_state": "unavailable",
        "fresh": False,
        "terminal": False,
        "reason_code": "mission_status_missing",
    }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return unavailable
    except (OSError, json.JSONDecodeError):
        return {**unavailable, "reason_code": "mission_status_unreadable"}

    vehicles = payload.get("vehicles")
    vehicle_ids = (
        [str(item.get("vehicle_id", "")) for item in vehicles if isinstance(item, dict)]
        if isinstance(vehicles, list)
        else []
    )
    valid = (
        payload.get("schema") == "mosim.mission_status.v1"
        and payload.get("run_id") == expected_run_id
        and isinstance(payload.get("adapter_id"), str)
        and isinstance(payload.get("phase"), str)
        and isinstance(payload.get("state"), str)
        and isinstance(payload.get("terminal"), bool)
        and (payload.get("accepted") is None or isinstance(payload.get("accepted"), bool))
        and sorted(vehicle_ids) == sorted(expected_vehicle_ids)
        and isinstance(payload.get("updated_at"), (int, float))
    )
    if not valid:
        return {**unavailable, "reason_code": "mission_status_contract_invalid"}

    age_s = now - float(payload["updated_at"])
    if age_s < -1.0:
        return {**unavailable, "reason_code": "mission_status_clock_invalid"}
    terminal = bool(payload["terminal"])
    fresh = age_s <= max_age_s
    return {
        **payload,
        "transport_state": "terminal" if terminal else ("fresh" if fresh else "stale"),
        "fresh": fresh,
        "source_age_s": max(0.0, age_s),
    }


class RosRuntimeSidecar:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from gazebo_msgs.msg import ModelStates
        from gazebo_msgs.srv import ApplyBodyWrench
        from geometry_msgs.msg import Point, Wrench
        from mavros_msgs.msg import AttitudeTarget, State
        from nav_msgs.msg import Odometry, Path as RosPath
        from quadrotor_msgs.msg import PositionCommand
        from std_msgs.msg import Float64MultiArray
        from visualization_msgs.msg import Marker

        self.rospy = rospy
        self.ApplyBodyWrench = ApplyBodyWrench
        self.Wrench = Wrench
        self.Point = Point
        self.Float64MultiArray = Float64MultiArray
        self.args = args
        self.run_dir = args.run_dir
        self.manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        self.profile_id = str(self.manifest.get("experiment_profile_id", ""))
        self.contract = load_contract(args.contract)
        self.operator_map, self.operator_map_snapshot_hash = resolve_runtime_operator_map(
            self.manifest,
            requested_map_id=args.map_id,
            requested_coordinate_contract_id=args.coordinate_contract_id,
            coordinate_contract_status=args.coordinate_contract_status,
        )
        self.coordinate_evidence: dict[str, Any] | None = None
        self.coordinate_evidence_sha256 = ""
        coordinate_evidence_path = getattr(args, "coordinate_evidence", None)
        if coordinate_evidence_path is not None:
            self.coordinate_evidence, self.coordinate_evidence_sha256 = load_coordinate_evidence(
                coordinate_evidence_path,
                map_snapshot=self.operator_map,
                snapshot_hash=self.operator_map_snapshot_hash,
            )
            # The frozen map identity remains unchanged. Only a separately
            # audited evidence artifact can lift the display state to verified.
            self.operator_map = dict(self.operator_map)
            self.operator_map["coordinate_contract_status"] = "verified"
        manifest_count = self.manifest.get("vehicle_count", args.vehicle_count)
        if manifest_count != args.vehicle_count:
            raise ValueError("sidecar_vehicle_count_manifest_mismatch")
        self.vehicle_ids = [f"uav{index}" for index in range(1, args.vehicle_count + 1)]
        self.started_at = time.time()
        self.ever_ready = False
        self.map_sequence = 0
        self.model_names: list[str] = []
        self.active_injections: dict[str, dict[str, Any]] = {}
        self.processed_commands: set[str] = set()
        self.task_paths: dict[str, dict[str, Any]] = {}
        self.vehicles: dict[str, dict[str, Any]] = {
            vehicle_id: {
                "state": None,
                "odom": None,
                "target_attitude": None,
                "position_command": None,
                "actuator": None,
                "effectiveness": [1.0] * 4,
                "wind_speed_mps": 0.0,
                "wind_direction_deg": 0.0,
            }
            for vehicle_id in self.vehicle_ids
        }
        self.command_pubs: dict[str, Any] = {}

        for vehicle_id in self.vehicle_ids:
            topics = self._topics(vehicle_id)
            self.command_pubs[vehicle_id] = rospy.Publisher(
                topics["actuator_command"], Float64MultiArray, queue_size=5
            )
            rospy.Subscriber(topics["state"], State, self._store, (vehicle_id, "state"), queue_size=20)
            rospy.Subscriber(topics["odom"], Odometry, self._store, (vehicle_id, "odom"), queue_size=50)
            rospy.Subscriber(
                topics["target_attitude"], AttitudeTarget, self._store,
                (vehicle_id, "target_attitude"), queue_size=50,
            )
            rospy.Subscriber(
                topics["position_command"], PositionCommand, self._store,
                (vehicle_id, "position_command"), queue_size=50,
            )
            rospy.Subscriber(
                topics["actuator_telemetry"], Float64MultiArray, self._store,
                (vehicle_id, "actuator"), queue_size=50,
            )
        rospy.Subscriber(args.model_states_topic, ModelStates, self._models_cb, queue_size=10)
        if args.expected_path_topic:
            rospy.Subscriber(
                args.expected_path_topic, RosPath, self._expected_path_cb,
                callback_args=args.expected_path_topic, queue_size=2,
            )
        if args.future_marker_topic:
            rospy.Subscriber(
                args.future_marker_topic, Marker, self._future_marker_cb,
                callback_args=args.future_marker_topic, queue_size=10,
            )
        self.wrench = rospy.ServiceProxy(args.wrench_service, ApplyBodyWrench)

    @staticmethod
    def _bounded_points(points: list[Any], max_points: int = 1200) -> list[dict[str, float]]:
        if not points:
            return []
        stride = max(1, math.ceil(len(points) / max_points))
        return [_vector(point) for point in points[::stride]][:max_points]

    def _expected_path_cb(self, msg: Any, source_topic: str) -> None:
        if self.profile_id == "factory_l2_three_uav_swarm_formation_v1":
            semantics = "formation_center_reference"
            vehicle_scope = "formation_center"
        elif self.profile_id == "factory_l2_fuel_fixed64_exploration_v1":
            semantics = "exploration_target_sequence"
            vehicle_scope = "uav1"
        else:
            semantics = "mission_reference"
            vehicle_scope = "uav1" if len(self.vehicle_ids) == 1 else "all_vehicles"
        self.task_paths["expected"] = {
            "status": "available",
            "semantics": semantics,
            "vehicle_scope": vehicle_scope,
            "source_topic": source_topic,
            "frame_id": str(msg.header.frame_id),
            "updated_at": time.time(),
            "points": self._bounded_points([pose.pose.position for pose in msg.poses]),
        }

    def _future_marker_cb(self, msg: Any, source_topic: str) -> None:
        if msg.action != msg.ADD or msg.ns != "B-Spline" or msg.id >= 50 or not msg.points:
            return
        self.task_paths["future"] = {
            "status": "available",
            "semantics": "planner_sampled_future_trajectory",
            "vehicle_scope": "uav1" if len(self.vehicle_ids) == 1 else "planner_default",
            "source_topic": source_topic,
            "frame_id": str(msg.header.frame_id),
            "updated_at": time.time(),
            "points": self._bounded_points(list(msg.points)),
        }

    def _topics(self, vehicle_id: str) -> dict[str, str]:
        if self.args.vehicle_count == 1:
            return {
                "state": self.args.state_topic,
                "odom": self.args.odom_topic,
                "target_attitude": self.args.target_attitude_topic,
                "position_command": self.args.position_command_topic,
                "actuator_command": self.args.actuator_command_topic,
                "actuator_telemetry": self.args.actuator_telemetry_topic,
            }
        return {
            "state": f"/{vehicle_id}/mavros/state",
            "odom": f"/{vehicle_id}/mavros/local_position/odom",
            "target_attitude": f"/{vehicle_id}/mavros/setpoint_raw/target_attitude",
            "position_command": f"/{vehicle_id}/position_cmd",
            "actuator_command": f"/{vehicle_id}/mosim/ftc_actuator_command",
            "actuator_telemetry": f"/{vehicle_id}/mosim/ftc_actuator_telemetry",
        }

    def _store(self, msg: Any, target: tuple[str, str]) -> None:
        vehicle_id, field = target
        self.vehicles[vehicle_id][field] = _sample(msg)

    def _models_cb(self, msg: Any) -> None:
        self.model_names = list(msg.name)

    def _vehicle_missing(self, vehicle_id: str, now: float) -> list[str]:
        vehicle = self.vehicles[vehicle_id]
        missing = []
        state = vehicle["state"]
        if state is None or not state[0].connected or now - state[1] > 2.0:
            missing.append("mavros_connected")
        required_samples = [
            ("odom", "mavros_odom_fresh"),
        ]
        if not self.args.skip_controller_command_readiness:
            required_samples.append(("target_attitude", "controller_command_fresh"))
        if not self.args.skip_actuator_telemetry_readiness:
            required_samples.append(("actuator", "actuator_plugin_telemetry_fresh"))
        for field, reason in required_samples:
            sample = vehicle[field]
            if sample is None or now - sample[1] > 1.0:
                missing.append(reason)
        return [f"{vehicle_id}:{reason}" for reason in missing]

    def _ready(self, now: float) -> tuple[bool, list[str]]:
        missing = [reason for vehicle_id in self.vehicle_ids for reason in self._vehicle_missing(vehicle_id, now)]
        return not missing, missing

    def _publish_effectiveness(self, vehicle_id: str) -> None:
        msg = self.Float64MultiArray()
        msg.data = [0.0, *self.vehicles[vehicle_id]["effectiveness"], 0.0, 0.0, 0.0, 0.0]
        self.command_pubs[vehicle_id].publish(msg)

    def _body_name(self, vehicle_id: str) -> str | None:
        configured = self.args.body_name if self.args.vehicle_count == 1 else ""
        return resolve_gazebo_body_name(configured, self.model_names, vehicle_id)

    def _apply_wind_force(self, vehicle_id: str) -> tuple[bool, str]:
        vehicle = self.vehicles[vehicle_id]
        if vehicle["wind_speed_mps"] <= 0.0:
            return True, "wind_zero"
        body_name = self._body_name(vehicle_id)
        if not body_name:
            return False, "gazebo_vehicle_body_not_found"
        angle = math.radians(vehicle["wind_direction_deg"])
        force = self.args.wind_force_coefficient * vehicle["wind_speed_mps"] ** 2
        wrench = self.Wrench()
        wrench.force.x = force * math.cos(angle)
        wrench.force.y = force * math.sin(angle)
        try:
            response = self.wrench(
                body_name=body_name,
                reference_frame="world",
                reference_point=self.Point(),
                wrench=wrench,
                start_time=self.rospy.Time(0),
                duration=self.rospy.Duration(0.15),
            )
        except Exception as exc:
            return False, f"gazebo_apply_body_wrench_failed:{exc}"
        reason = str(response.status_message).strip()
        if response.success and not reason:
            reason = "wind_wrench_applied"
        return bool(response.success), reason

    def _ack(self, command: dict[str, Any], *, accepted: bool, reason: str, applied_value: Any = None) -> None:
        payload = {
            "schema": "mosim.runtime_injection_ack.v1",
            "command_id": command.get("command_id", ""),
            "run_id": self.manifest["run_id"],
            "vehicle_id": command.get("vehicle_id"),
            "target": command.get("target", ""),
            "rotor_index": command.get("rotor_index"),
            "apply_mode": command.get("apply_mode", ""),
            "source": command.get("source", ""),
            "accepted": accepted,
            "reason_code": reason,
            "requested_value": command.get("value"),
            "applied_value": applied_value,
            "applied_at": time.time(),
        }
        atomic_write_json(self.run_dir / "injection_acks" / f"{command.get('command_id', 'invalid')}.json", payload)

    def _consume_commands(self) -> None:
        command_dir = self.run_dir / "injection_commands"
        command_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(command_dir.glob("inj-*.json")):
            if path.name in self.processed_commands:
                continue
            self.processed_commands.add(path.name)
            raw: dict[str, Any] = {}
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                command = validate_command(raw, manifest=self.manifest, contract=self.contract)
            except (OSError, ValueError, TypeError) as exc:
                self._ack(raw, accepted=False, reason=str(exc))
                continue
            vehicle_id = command["vehicle_id"]
            vehicle = self.vehicles[vehicle_id]
            target = command["target"]
            value = float(command["value"])
            if target == "motor_effectiveness":
                vehicle["effectiveness"][int(command["rotor_index"]) - 1] = value
                self._publish_effectiveness(vehicle_id)
                self.active_injections[f"{vehicle_id}:{target}:{command['rotor_index']}"] = command
                self._ack(command, accepted=True, reason="motor_effectiveness_published", applied_value=value)
            elif target == "wind_direction_deg":
                vehicle["wind_direction_deg"] = value
                self.active_injections[f"{vehicle_id}:{target}"] = command
                self._ack(command, accepted=True, reason="wind_direction_applied", applied_value=value)
            elif target == "wind_speed_mps":
                vehicle["wind_speed_mps"] = value
                ok, reason = self._apply_wind_force(vehicle_id)
                if ok:
                    self.active_injections[f"{vehicle_id}:{target}"] = command
                self._ack(command, accepted=ok, reason=reason, applied_value=value if ok else None)

    def _vehicle_telemetry(self, vehicle_id: str) -> dict[str, Any]:
        vehicle = self.vehicles[vehicle_id]
        telemetry: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "state": {},
            "reference": None,
            "command": None,
            "injection_state": {
                "wind_speed_mps": vehicle["wind_speed_mps"],
                "wind_direction_deg": vehicle["wind_direction_deg"],
                "motor_effectiveness": vehicle["effectiveness"],
            },
            "rotor_state": None,
            "attitude_error": None,
            "control_output": None,
            "module_diagnostics": {"active_controller_command": vehicle["target_attitude"] is not None},
            "safety_intervention": False,
        }
        if vehicle["state"]:
            msg = vehicle["state"][0]
            telemetry["state"] = {"connected": bool(msg.connected), "armed": bool(msg.armed), "mode": msg.mode}
        if vehicle["odom"]:
            msg = vehicle["odom"][0]
            velocity_frame = str(getattr(msg, "child_frame_id", "") or msg.header.frame_id)
            telemetry["state"].update({
                "position": _vector(msg.pose.pose.position),
                "position_frame": str(msg.header.frame_id),
                "orientation": _quaternion(msg.pose.pose.orientation),
                "linear_velocity": _vector(msg.twist.twist.linear),
                "angular_velocity": _vector(msg.twist.twist.angular),
                "linear_velocity_frame": velocity_frame,
                "angular_velocity_frame": velocity_frame,
            })
        if vehicle["position_command"]:
            msg = vehicle["position_command"][0]
            telemetry["reference"] = {
                "position": _vector(msg.position), "velocity": _vector(msg.velocity),
                "acceleration": _vector(msg.acceleration), "yaw": float(msg.yaw), "yaw_dot": float(msg.yaw_dot),
            }
        if vehicle["target_attitude"]:
            msg = vehicle["target_attitude"][0]
            telemetry["command"] = {
                "orientation": _quaternion(msg.orientation), "body_rate": _vector(msg.body_rate),
                "thrust": float(msg.thrust), "type_mask": int(msg.type_mask),
            }
            telemetry["control_output"] = {"body_rate": _vector(msg.body_rate), "thrust": float(msg.thrust)}
        if vehicle["odom"] and vehicle["target_attitude"]:
            actual = vehicle["odom"][0].pose.pose.orientation
            desired = vehicle["target_attitude"][0].orientation
            dot = abs(actual.w * desired.w + actual.x * desired.x + actual.y * desired.y + actual.z * desired.z)
            telemetry["attitude_error"] = 2.0 * math.acos(max(0.0, min(1.0, dot)))
        if vehicle["odom"] and vehicle["position_command"]:
            actual = vehicle["odom"][0].pose.pose.position
            desired = vehicle["position_command"][0].position
            telemetry["position_error_m"] = {
                "x": float(desired.x - actual.x), "y": float(desired.y - actual.y), "z": float(desired.z - actual.z),
            }
        if vehicle["actuator"] and len(vehicle["actuator"][0].data) == 18:
            values = list(vehicle["actuator"][0].data)
            telemetry["rotor_state"] = {
                "sim_time_s": values[0], "raw_command": values[1:5], "physical_speed_ratio": values[5:9],
                "effective_response": values[9:13], "effectiveness": values[13:17],
                "override_enabled": bool(values[17] >= 0.5),
            }
        return telemetry

    def _latest_map_source_timestamp(self) -> float | None:
        source_times = []
        for vehicle in self.vehicles.values():
            odom = vehicle["odom"]
            if odom is not None:
                timestamp = ros_source_timestamp(odom[0])
                if timestamp is not None:
                    source_times.append(timestamp)
        return max(source_times) if source_times else None

    def _write_status_and_telemetry(self) -> None:
        now = time.time()
        ready, missing = self._ready(now)
        status, reason_code, self.ever_ready = evaluate_readiness_status(
            ready=ready,
            ever_ready=self.ever_ready,
            elapsed_s=now - self.started_at,
            timeout_s=self.args.ready_timeout_s,
        )
        status_payload = {
            "schema": "mosim.runtime_status.v1", "run_id": self.manifest["run_id"], "status": status,
            "reason_code": reason_code,
            "vehicle_count": len(self.vehicle_ids), "missing_readiness": missing, "updated_at": now,
        }
        atomic_write_json(self.run_dir / "RUNTIME_STATUS.json", status_payload)
        vehicles = [self._vehicle_telemetry(vehicle_id) for vehicle_id in self.vehicle_ids]
        map_vehicles, map_task_paths, map_data_status = project_live_operator_map_frame(
            vehicles=vehicles,
            task_paths=self.task_paths,
            coordinate_evidence=self.coordinate_evidence,
            run_id=self.manifest["run_id"],
        )
        self.map_sequence += 1
        map_state = build_operator_map_state(
            manifest=self.manifest,
            map_snapshot=self.operator_map,
            transport_mode=self.args.transport_mode,
            sequence=self.map_sequence,
            received_at_unix_s=now,
            source_timestamp_s=self._latest_map_source_timestamp(),
            playback_state=self.args.replay_state,
            playback_time_s=self.args.replay_time_s,
            bag_id=self.args.replay_bag_id,
            vehicles=map_vehicles,
            task_paths=map_task_paths,
            map_data_status=map_data_status,
        )
        telemetry: dict[str, Any] = {
            "schema": "mosim.runtime_telemetry.v2", "run_id": self.manifest["run_id"], "timestamp": now,
            "vehicle_count": len(vehicles), "readiness": status_payload, "vehicles": vehicles,
            "task_paths": self.task_paths,
            "map_state": map_state,
            "operator_map_coordinate_evidence": {
                "status": "verified" if self.coordinate_evidence is not None else "pending_runtime_validation",
                "evidence_id": self.coordinate_evidence.get("evidence_id", "")
                if self.coordinate_evidence is not None else "",
                "sha256": self.coordinate_evidence_sha256,
            },
            "mission_status": load_mission_status(
                self.run_dir / "mission_status.json",
                expected_run_id=self.manifest["run_id"],
                expected_vehicle_ids=self.vehicle_ids,
                now=now,
                max_age_s=self.args.mission_status_max_age_s,
            ),
        }
        if len(vehicles) == 1:
            telemetry.update({key: value for key, value in vehicles[0].items() if key != "vehicle_id"})
        atomic_write_json(self.run_dir / "telemetry.json", telemetry)

    def run(self) -> None:
        rate = self.rospy.Rate(self.args.rate_hz)
        while not self.rospy.is_shutdown():
            self._consume_commands()
            for vehicle_id in self.vehicle_ids:
                self._publish_effectiveness(vehicle_id)
                if self.vehicles[vehicle_id]["wind_speed_mps"] > 0.0:
                    self._apply_wind_force(vehicle_id)
            self._write_status_and_telemetry()
            rate.sleep()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--vehicle-count", type=int, choices=range(1, 10), default=1)
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--ready-timeout-s", type=float, default=90.0)
    parser.add_argument("--mission-status-max-age-s", type=float, default=2.5)
    parser.add_argument("--wind-force-coefficient", type=float, default=0.025)
    parser.add_argument("--body-name", default=os.environ.get("MOSIM_GAZEBO_BODY_NAME", ""))
    parser.add_argument("--state-topic", default="/uav1/mavros/state")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--target-attitude-topic", default="/uav1/mavros/setpoint_raw/target_attitude")
    parser.add_argument("--position-command-topic", default="/position_cmd")
    parser.add_argument("--actuator-command-topic", default="/uav1/mosim/ftc_actuator_command")
    parser.add_argument("--actuator-telemetry-topic", default="/uav1/mosim/ftc_actuator_telemetry")
    parser.add_argument("--expected-path-topic", default="")
    parser.add_argument("--future-marker-topic", default="")
    parser.add_argument(
        "--map-id",
        default="",
        help="Optional assertion only; it must match the map frozen in RUN_MANIFEST.json.",
    )
    parser.add_argument("--coordinate-contract-id", default="")
    parser.add_argument(
        "--coordinate-evidence",
        type=Path,
        help=(
            "Reviewed mosim.operator_map_coordinate_evidence.v1 bound to the frozen "
            "RunManifest map snapshot. Required before live geometry is drawable."
        ),
    )
    parser.add_argument(
        "--coordinate-contract-status",
        choices=tuple(sorted(COORDINATE_CONTRACT_STATUSES)),
        default="",
    )
    parser.add_argument("--transport-mode", choices=tuple(sorted(OPERATOR_MAP_TRANSPORT_MODES)), default="live_ros1")
    parser.add_argument("--replay-bag-id", default="")
    parser.add_argument(
        "--replay-state",
        choices=("playing", "paused", "completed", "failed"),
        default="playing",
    )
    parser.add_argument("--replay-time-s", type=float)
    parser.add_argument(
        "--skip-controller-command-readiness",
        action="store_true",
        help="Do not require a controller setpoint for operator ground-standby profiles.",
    )
    parser.add_argument(
        "--skip-actuator-telemetry-readiness",
        action="store_true",
        help="Do not require FTC plugin telemetry for profiles that do not enable actuator faults.",
    )
    parser.add_argument("--model-states-topic", default="/gazebo/model_states")
    parser.add_argument("--wrench-service", default="/gazebo/apply_body_wrench")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate_hz <= 0.0 or args.ready_timeout_s <= 0.0 or args.mission_status_max_age_s <= 0.0:
        raise SystemExit("rate and timeout must be positive")
    if args.transport_mode == "live_ros1" and (args.replay_bag_id or args.replay_time_s is not None):
        raise SystemExit("live_ros1 map transport cannot declare rosbag replay fields")
    if args.transport_mode == "rosbag_replay" and not args.replay_bag_id:
        raise SystemExit("rosbag_replay map transport requires --replay-bag-id")
    if args.coordinate_evidence is not None and args.coordinate_contract_status:
        raise SystemExit("coordinate evidence cannot be combined with a status override")
    args.run_dir.mkdir(parents=True, exist_ok=True)
    import rospy
    rospy.init_node("mosim_orchestrator_runtime_sidecar", anonymous=False)
    RosRuntimeSidecar(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
