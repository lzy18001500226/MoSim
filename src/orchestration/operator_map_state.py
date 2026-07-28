"""Validate the run-bound Factory 2D operator-map state envelope."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


OPERATOR_MAP_STATE_SCHEMA = "mosim.operator_map_state.v1"
OPERATOR_MAP_TRANSPORT_MODES = frozenset({"live_ros1", "rosbag_replay"})
COORDINATE_CONTRACT_STATUSES = frozenset({"verified", "pending_runtime_validation", "rejected"})
IMAGE_COORDINATE_CONTRACT_SCHEMA = "mosim.operator_map_image_coordinate_contract.v1"
WORLD_TO_PIXEL_MATRIX_SCHEMA = "mosim.world_to_pixel.v1"
IMAGE_COORDINATE_RENDER_MODE = "axis_aligned_image_rect_v1"
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
PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


def _matrix_3x3(value: Any, reason_code: str) -> list[list[float]]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(reason_code)
    if any(not isinstance(row, list) or len(row) != 3 for row in value):
        raise ValueError(reason_code)
    matrix = [[float(item) if _finite_number(item) else math.nan for item in row] for row in value]
    if any(not math.isfinite(item) for row in matrix for item in row):
        raise ValueError(reason_code)
    if any(abs(matrix[2][index]) > 1e-9 for index in range(2)) or abs(matrix[2][2] - 1.0) > 1e-9:
        raise ValueError(reason_code)
    return matrix


def _matrix_multiply(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [sum(left[row][index] * right[index][column] for index in range(3)) for column in range(3)]
        for row in range(3)
    ]


def _matrix_inverse(matrix: list[list[float]], reason_code: str) -> list[list[float]]:
    a, b, tx = matrix[0]
    c, d, ty = matrix[1]
    determinant = a * d - b * c
    if abs(determinant) < 1e-12:
        raise ValueError(reason_code)
    inverse_linear = [[d / determinant, -b / determinant], [-c / determinant, a / determinant]]
    return [
        [inverse_linear[0][0], inverse_linear[0][1], -(inverse_linear[0][0] * tx + inverse_linear[0][1] * ty)],
        [inverse_linear[1][0], inverse_linear[1][1], -(inverse_linear[1][0] * tx + inverse_linear[1][1] * ty)],
        [0.0, 0.0, 1.0],
    ]


def _matrix_matches(left: list[list[float]], right: list[list[float]], tolerance: float = 1e-8) -> bool:
    return all(abs(left[row][column] - right[row][column]) <= tolerance for row in range(3) for column in range(3))


def _matrix_project(matrix: list[list[float]], x: float, y: float) -> tuple[float, float]:
    denominator = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2]
    if abs(denominator) < 1e-12:
        raise ValueError("operator_map_image_coordinate_contract_matrix_invalid")
    return (
        (matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]) / denominator,
        (matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]) / denominator,
    )


def _image_size(value: Any, reason_code: str) -> tuple[int, int]:
    size = _mapping(value, reason_code)
    width, height = size.get("width"), size.get("height")
    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or not isinstance(height, int)
        or isinstance(height, bool)
        or width <= 0
        or height <= 0
    ):
        raise ValueError(reason_code)
    return width, height


def _resolve_contract_path(project_root: Path, value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError("operator_map_image_coordinate_contract_path_invalid")
    root = project_root.resolve()
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("operator_map_image_coordinate_contract_path_invalid") from exc
    return resolved


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_image_coordinate_contract(
    snapshot: dict[str, Any], *, project_root: Path | None = None, check_source: bool = True
) -> dict[str, Any]:
    """Validate the image-pixel contract carried by a frozen operator-map snapshot.

    The Factory floorplan intentionally has image padding around the world
    bounds.  The duplicated matrices make that relation reviewable in the map
    catalog while the source-file hash prevents a stale or edited transform
    file from silently moving aircraft, paths, or mission overlays.
    """

    contract = _mapping(snapshot.get("image_coordinate_contract"), "operator_map_image_coordinate_contract_missing")
    if contract.get("schema") != IMAGE_COORDINATE_CONTRACT_SCHEMA:
        raise ValueError("operator_map_image_coordinate_contract_schema_invalid")
    if contract.get("matrix_schema") != WORLD_TO_PIXEL_MATRIX_SCHEMA:
        raise ValueError("operator_map_image_coordinate_contract_schema_invalid")
    if contract.get("render_mode") != IMAGE_COORDINATE_RENDER_MODE:
        raise ValueError("operator_map_image_coordinate_contract_layout_invalid")
    matrix_path = _required_string(
        contract.get("matrix_path"), "operator_map_image_coordinate_contract_fields_invalid"
    )
    matrix_sha256 = _required_string(
        contract.get("matrix_sha256"), "operator_map_image_coordinate_contract_fields_invalid"
    ).lower()
    if re.fullmatch(r"[0-9a-f]{64}", matrix_sha256) is None:
        raise ValueError("operator_map_image_coordinate_contract_fields_invalid")
    width, height = _image_size(contract.get("image_size_px"), "operator_map_image_coordinate_contract_image_size_invalid")
    world_to_pixel = _matrix_3x3(
        contract.get("world_to_pixel_3x3"), "operator_map_image_coordinate_contract_matrix_invalid"
    )
    pixel_to_world = _matrix_3x3(
        contract.get("pixel_to_world_3x3"), "operator_map_image_coordinate_contract_matrix_invalid"
    )
    inverse = _matrix_inverse(world_to_pixel, "operator_map_image_coordinate_contract_not_invertible")
    identity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    if not _matrix_matches(inverse, pixel_to_world) or not _matrix_matches(
        _matrix_multiply(world_to_pixel, pixel_to_world), identity
    ):
        raise ValueError("operator_map_image_coordinate_contract_inverse_mismatch")
    # The Plan View currently renders a QGC screen-aligned raster. A rotated or
    # sheared affine matrix needs a dedicated projected image item, not a quiet
    # bounding-box approximation.
    if abs(world_to_pixel[0][1]) > 1e-9 or abs(world_to_pixel[1][0]) > 1e-9:
        raise ValueError("operator_map_image_coordinate_contract_layout_invalid")

    bounds = _world_bounds(snapshot)
    for world_x, world_y in (
        (bounds["min_x_m"], bounds["min_y_m"]),
        (bounds["min_x_m"], bounds["max_y_m"]),
        (bounds["max_x_m"], bounds["min_y_m"]),
        (bounds["max_x_m"], bounds["max_y_m"]),
    ):
        pixel_x, pixel_y = _matrix_project(world_to_pixel, world_x, world_y)
        if pixel_x < -1e-6 or pixel_x > width + 1e-6 or pixel_y < -1e-6 or pixel_y > height + 1e-6:
            raise ValueError("operator_map_image_coordinate_contract_world_bounds_outside_image")

    normalized = {
        **contract,
        "matrix_sha256": matrix_sha256,
        "image_size_px": {"width": width, "height": height},
        "world_to_pixel_3x3": world_to_pixel,
        "pixel_to_world_3x3": pixel_to_world,
    }
    if not check_source:
        return normalized

    root = (project_root or PROJECT_ROOT).resolve()
    source_path = _resolve_contract_path(root, matrix_path)
    try:
        source_hash = _sha256_file(source_path)
        source = json.loads(source_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("operator_map_image_coordinate_contract_matrix_missing") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("operator_map_image_coordinate_contract_matrix_unreadable") from exc
    if source_hash != matrix_sha256:
        raise ValueError("operator_map_image_coordinate_contract_hash_mismatch")
    if not isinstance(source, dict) or source.get("schema") != WORLD_TO_PIXEL_MATRIX_SCHEMA:
        raise ValueError("operator_map_image_coordinate_contract_source_mismatch")
    if any(source.get(field) != snapshot.get(field) for field in ("map_id", "map_version", "world_frame")):
        raise ValueError("operator_map_image_coordinate_contract_source_mismatch")
    try:
        source_width, source_height = _image_size(
            source.get("image_size_px"), "operator_map_image_coordinate_contract_source_mismatch"
        )
        source_world_to_pixel = _matrix_3x3(
            source.get("world_to_pixel_3x3"), "operator_map_image_coordinate_contract_source_mismatch"
        )
        source_pixel_to_world = _matrix_3x3(
            source.get("pixel_to_world_3x3"), "operator_map_image_coordinate_contract_source_mismatch"
        )
    except ValueError as exc:
        raise ValueError("operator_map_image_coordinate_contract_source_mismatch") from exc
    if (
        (source_width, source_height) != (width, height)
        or not _matrix_matches(source_world_to_pixel, world_to_pixel)
        or not _matrix_matches(source_pixel_to_world, pixel_to_world)
        or source.get("bounds_m") != snapshot.get("world_bounds_m")
    ):
        raise ValueError("operator_map_image_coordinate_contract_source_mismatch")
    return normalized


def validate_operator_map_snapshot(
    snapshot: Any, *, project_root: Path | None = None, check_source: bool = True
) -> dict[str, Any]:
    """Validate a frozen map snapshot before it can enter a RunManifest or sidecar."""

    value = _mapping(snapshot, "operator_map_snapshot_invalid")
    for field in ("resource_url", *OPERATOR_MAP_IDENTITY_FIELDS):
        _required_string(value.get(field), "operator_map_contract_fields_missing")
    if value.get("coordinate_contract_status") not in COORDINATE_CONTRACT_STATUSES:
        raise ValueError("operator_map_coordinate_status_invalid")
    _world_bounds(value)
    validate_image_coordinate_contract(value, project_root=project_root, check_source=check_source)
    return value


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
    if _canonical_hash(snapshot) != snapshot_hash:
        raise ValueError("operator_map_manifest_snapshot_hash_mismatch")
    # Source-file integrity is checked at prepare and sidecar startup. Per-frame
    # telemetry validation stays in-memory and is still bound to this frozen hash.
    validate_operator_map_snapshot(snapshot, check_source=False)
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
