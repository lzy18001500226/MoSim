"""Validate the run-bound Factory 2D operator-map state envelope."""

from __future__ import annotations

import math
import re
from typing import Any


OPERATOR_MAP_STATE_SCHEMA = "mosim.operator_map_state.v1"
OPERATOR_MAP_TRANSPORT_MODES = frozenset({"live_ros1", "rosbag_replay"})
COORDINATE_CONTRACT_STATUSES = frozenset({"verified", "pending_runtime_validation", "rejected"})
OPERATOR_MAP_IDENTITY_FIELDS = (
    "map_id",
    "map_version",
    "asset_sha256",
    "world_frame",
    "coordinate_contract_id",
)
REPLAY_STATES = frozenset({"playing", "paused", "completed", "failed"})
MAP_DATA_STATES = frozenset({"accepted", "rejected"})
VEHICLE_ID_PATTERN = re.compile(r"^uav([1-9])$")
MAX_PATH_POINTS = 1200


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _mapping(value: Any, reason_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(reason_code)
    return value


def _required_string(value: Any, reason_code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(reason_code)
    return value


def _world_bounds(snapshot: dict[str, Any]) -> dict[str, float]:
    raw = _mapping(snapshot.get("world_bounds_m"), "operator_map_bounds_invalid")
    keys = ("min_x_m", "max_x_m", "min_y_m", "max_y_m")
    if any(not _finite_number(raw.get(key)) for key in keys):
        raise ValueError("operator_map_bounds_invalid")
    bounds = {key: float(raw[key]) for key in keys}
    if bounds["min_x_m"] >= bounds["max_x_m"] or bounds["min_y_m"] >= bounds["max_y_m"]:
        raise ValueError("operator_map_bounds_invalid")
    return bounds


def _validate_point(point: Any, bounds: dict[str, float], reason_code: str) -> None:
    value = _mapping(point, reason_code)
    if not _finite_number(value.get("x")) or not _finite_number(value.get("y")):
        raise ValueError(reason_code)
    x = float(value["x"])
    y = float(value["y"])
    if x < bounds["min_x_m"] or x > bounds["max_x_m"] or y < bounds["min_y_m"] or y > bounds["max_y_m"]:
        raise ValueError(reason_code)
    if "z" in value and not _finite_number(value["z"]):
        raise ValueError(reason_code)


def _validate_vehicle_states(
    vehicles: Any,
    *,
    vehicle_count: int,
    bounds: dict[str, float],
    world_frame: str,
    coordinate_verified: bool,
) -> None:
    if not isinstance(vehicles, list):
        raise ValueError("operator_map_vehicle_count_invalid")
    # A newly opened live/replay session may not have produced its first frame.
    # The UI intentionally renders no aircraft in that state instead of inventing one.
    if not vehicles:
        return
    if len(vehicles) != vehicle_count:
        raise ValueError("operator_map_vehicle_count_invalid")
    expected_ids = {f"uav{index}" for index in range(1, vehicle_count + 1)}
    observed_ids: set[str] = set()
    for vehicle in vehicles:
        item = _mapping(vehicle, "operator_map_vehicle_invalid")
        vehicle_id = _required_string(item.get("vehicle_id"), "operator_map_vehicle_id_invalid")
        match = VEHICLE_ID_PATTERN.fullmatch(vehicle_id)
        if match is None or int(match.group(1)) > vehicle_count or vehicle_id in observed_ids:
            raise ValueError("operator_map_vehicle_id_invalid")
        observed_ids.add(vehicle_id)
        state = _mapping(item.get("state"), "operator_map_vehicle_state_invalid")
        if "connected" in state and not isinstance(state["connected"], bool):
            raise ValueError("operator_map_vehicle_state_invalid")
        position = state.get("position")
        if position is not None:
            _validate_point(position, bounds, "operator_map_vehicle_position_invalid")
            if coordinate_verified and state.get("position_frame") != world_frame:
                raise ValueError("operator_map_vehicle_frame_mismatch")
        orientation = state.get("orientation")
        if orientation is not None:
            quaternion = _mapping(orientation, "operator_map_vehicle_orientation_invalid")
            if any(not _finite_number(quaternion.get(axis)) for axis in ("w", "x", "y", "z")):
                raise ValueError("operator_map_vehicle_orientation_invalid")
    if observed_ids != expected_ids:
        raise ValueError("operator_map_vehicle_id_invalid")


def _validate_task_paths(
    value: Any,
    *,
    run_id: str,
    bounds: dict[str, float],
    world_frame: str,
    coordinate_verified: bool,
) -> None:
    paths = _mapping(value, "operator_map_task_paths_invalid")
    for kind in ("expected", "future"):
        if kind not in paths:
            continue
        path = _mapping(paths[kind], "operator_map_task_path_invalid")
        status = _required_string(path.get("status"), "operator_map_task_path_status_invalid")
        if status != "available":
            continue
        points = path.get("points")
        if not isinstance(points, list) or len(points) > MAX_PATH_POINTS:
            raise ValueError("operator_map_task_path_points_invalid")
        for point in points:
            _validate_point(point, bounds, "operator_map_task_path_points_invalid")
        if "run_id" in path and path["run_id"] != run_id:
            raise ValueError("operator_map_task_path_run_id_mismatch")
        if "updated_at" in path and not _finite_number(path["updated_at"]):
            raise ValueError("operator_map_task_path_timestamp_invalid")
        if coordinate_verified and points and path.get("frame_id") != world_frame:
            raise ValueError("operator_map_task_path_frame_mismatch")


def _validate_boundary(value: Any, *, bounds: dict[str, float]) -> None:
    boundary = _mapping(value, "operator_map_boundary_invalid")
    keys = ("min_x_m", "max_x_m", "min_y_m", "max_y_m")
    if any(not _finite_number(boundary.get(key)) for key in keys):
        raise ValueError("operator_map_boundary_invalid")
    min_x, max_x = float(boundary["min_x_m"]), float(boundary["max_x_m"])
    min_y, max_y = float(boundary["min_y_m"]), float(boundary["max_y_m"])
    if min_x >= max_x or min_y >= max_y:
        raise ValueError("operator_map_boundary_invalid")
    _validate_point({"x": min_x, "y": min_y}, bounds, "operator_map_boundary_invalid")
    _validate_point({"x": max_x, "y": max_y}, bounds, "operator_map_boundary_invalid")


def _validate_formation_target(value: Any, *, bounds: dict[str, float]) -> None:
    formation = _mapping(value, "operator_map_formation_target_invalid")
    target = formation.get("target_center_xy_m")
    if not isinstance(target, list) or len(target) != 2:
        raise ValueError("operator_map_formation_target_invalid")
    _validate_point({"x": target[0], "y": target[1]}, bounds, "operator_map_formation_target_invalid")


def _validate_map_data_status(value: Any) -> None:
    """Validate an optional per-frame display rejection without touching flight state."""

    if value is None:
        return
    status = _mapping(value, "operator_map_data_status_invalid")
    state = status.get("state")
    reason_code = status.get("reason_code", "")
    if state not in MAP_DATA_STATES or not isinstance(reason_code, str):
        raise ValueError("operator_map_data_status_invalid")
    if state == "rejected" and not reason_code:
        raise ValueError("operator_map_data_status_invalid")


def validate_operator_map_state(value: Any, *, manifest: dict[str, Any]) -> None:
    """Reject map frames that do not belong to the frozen run/map contract.

    This is deliberately a display-data gate, not a controller or planner gate.
    ``pending_runtime_validation`` frames remain valid but are hidden by QML;
    only a verified frame may carry drawable position/path geometry.
    """

    state = _mapping(value, "operator_map_state_invalid")
    if state.get("schema") != OPERATOR_MAP_STATE_SCHEMA:
        raise ValueError("operator_map_state_schema_invalid")

    run_id = _required_string(manifest.get("run_id"), "operator_map_manifest_identity_invalid")
    profile_id = _required_string(manifest.get("experiment_profile_id"), "operator_map_manifest_identity_invalid")
    profile_hash = _required_string(manifest.get("experiment_profile_hash"), "operator_map_manifest_identity_invalid")
    snapshot = _mapping(manifest.get("operator_map_snapshot"), "operator_map_manifest_snapshot_missing")
    snapshot_hash = _required_string(
        manifest.get("operator_map_snapshot_hash"), "operator_map_manifest_snapshot_hash_missing"
    )
    bounds = _world_bounds(snapshot)

    if state.get("run_id") != run_id:
        raise ValueError("operator_map_run_id_mismatch")
    if state.get("profile_id") != profile_id or state.get("profile_hash") != profile_hash:
        raise ValueError("operator_map_profile_identity_mismatch")

    transport = _mapping(state.get("transport"), "operator_map_transport_invalid")
    mode = transport.get("mode")
    if mode not in OPERATOR_MAP_TRANSPORT_MODES:
        raise ValueError("operator_map_transport_mode_invalid")
    sequence = transport.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= 0:
        raise ValueError("operator_map_transport_sequence_invalid")
    if not _finite_number(transport.get("received_at_unix_s")) or float(transport["received_at_unix_s"]) <= 0.0:
        raise ValueError("operator_map_transport_receive_time_invalid")
    source_timestamp = transport.get("source_timestamp_s")
    if source_timestamp is not None and (
        not _finite_number(source_timestamp) or float(source_timestamp) < 0.0
    ):
        raise ValueError("operator_map_transport_source_time_invalid")
    if mode == "live_ros1":
        if transport.get("playback_state") != "live" or transport.get("playback_time_s") is not None:
            raise ValueError("operator_map_live_transport_replay_fields_invalid")
        if transport.get("bag_id") not in (None, ""):
            raise ValueError("operator_map_live_transport_replay_fields_invalid")
    else:
        if transport.get("playback_state") not in REPLAY_STATES:
            raise ValueError("operator_map_replay_state_invalid")
        if not _finite_number(transport.get("playback_time_s")) or float(transport["playback_time_s"]) < 0.0:
            raise ValueError("operator_map_replay_time_invalid")
        _required_string(transport.get("bag_id"), "operator_map_replay_bag_id_missing")

    state_map = _mapping(state.get("map"), "operator_map_identity_invalid")
    if state_map.get("operator_map_snapshot_hash") != snapshot_hash:
        raise ValueError("operator_map_snapshot_hash_mismatch")
    for field in OPERATOR_MAP_IDENTITY_FIELDS:
        if state_map.get(field) != snapshot.get(field):
            raise ValueError("operator_map_identity_mismatch")
    coordinate_status = state_map.get("coordinate_contract_status")
    if coordinate_status not in COORDINATE_CONTRACT_STATUSES:
        raise ValueError("operator_map_coordinate_status_invalid")
    coordinate_verified = coordinate_status == "verified"
    world_frame = str(snapshot["world_frame"])

    vehicle_count = manifest.get("vehicle_count", 1)
    if not isinstance(vehicle_count, int) or isinstance(vehicle_count, bool) or not 1 <= vehicle_count <= 9:
        raise ValueError("operator_map_manifest_vehicle_count_invalid")
    _validate_vehicle_states(
        state.get("vehicles"),
        vehicle_count=vehicle_count,
        bounds=bounds,
        world_frame=world_frame,
        coordinate_verified=coordinate_verified,
    )
    _validate_task_paths(
        state.get("task_paths"),
        run_id=run_id,
        bounds=bounds,
        world_frame=world_frame,
        coordinate_verified=coordinate_verified,
    )
    _validate_map_data_status(state.get("map_data_status"))
    if "task_boundary" in state:
        _validate_boundary(state["task_boundary"], bounds=bounds)
    if "formation_target" in state:
        _validate_formation_target(state["formation_target"], bounds=bounds)
