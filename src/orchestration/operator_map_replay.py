"""Deterministic rosbag-to-Factory-map replay helpers.

The helpers in this module deliberately operate on normalized odometry records
instead of importing ROS.  The ROS1 entry point owns rosbag decoding; this
module owns the frozen-run, coordinate-evidence, and timeline rules that are
also exercised on Windows by unit tests.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


COORDINATE_EVIDENCE_SCHEMA = "mosim.operator_map_coordinate_evidence.v1"
REPLAY_MANIFEST_SCHEMA = "mosim.operator_map_replay_manifest.v1"
VEHICLE_ID_PATTERN = re.compile(r"^uav([1-9])$")
MAP_IDENTITY_FIELDS = (
    "map_id",
    "map_version",
    "asset_sha256",
    "world_frame",
    "coordinate_contract_id",
)


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_bag_id(path: Path, sha256: str) -> str:
    if not isinstance(sha256, str) or len(sha256) != 64:
        raise ValueError("operator_map_replay_bag_sha256_invalid")
    return f"rosbag:{path.name}:{sha256[:16]}"


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


def _vector(value: Any, reason_code: str) -> dict[str, float]:
    raw = _mapping(value, reason_code)
    if any(not _finite_number(raw.get(axis)) for axis in ("x", "y", "z")):
        raise ValueError(reason_code)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _quaternion(value: Any, reason_code: str) -> dict[str, float]:
    raw = _mapping(value, reason_code)
    if any(not _finite_number(raw.get(axis)) for axis in ("w", "x", "y", "z")):
        raise ValueError(reason_code)
    norm = math.sqrt(sum(float(raw[axis]) ** 2 for axis in ("w", "x", "y", "z")))
    if norm < 1e-9:
        raise ValueError(reason_code)
    return {axis: float(raw[axis]) / norm for axis in ("w", "x", "y", "z")}


def _determinant_3x3(matrix: list[list[float]]) -> float:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def _transform_matrix(value: Any) -> list[list[float]]:
    if not isinstance(value, list) or len(value) != 4 or any(not isinstance(row, list) or len(row) != 4 for row in value):
        raise ValueError("operator_map_coordinate_evidence_matrix_invalid")
    matrix = [[float(element) if _finite_number(element) else math.nan for element in row] for row in value]
    if any(not math.isfinite(element) for row in matrix for element in row):
        raise ValueError("operator_map_coordinate_evidence_matrix_invalid")
    if any(abs(matrix[3][index]) > 1e-8 for index in range(3)) or abs(matrix[3][3] - 1.0) > 1e-8:
        raise ValueError("operator_map_coordinate_evidence_matrix_invalid")
    rotation = [row[:3] for row in matrix[:3]]
    if abs(abs(_determinant_3x3(rotation)) - 1.0) > 1e-5:
        raise ValueError("operator_map_coordinate_evidence_matrix_invalid")
    for row in rotation:
        if abs(sum(value * value for value in row) - 1.0) > 1e-5:
            raise ValueError("operator_map_coordinate_evidence_matrix_invalid")
    for left in range(3):
        for right in range(left + 1, 3):
            if abs(sum(rotation[left][index] * rotation[right][index] for index in range(3))) > 1e-5:
                raise ValueError("operator_map_coordinate_evidence_matrix_invalid")
    return matrix


def validate_coordinate_evidence(
    value: Any,
    *,
    map_snapshot: dict[str, Any],
    snapshot_hash: str,
) -> dict[str, Any]:
    """Validate an externally produced coordinate-validation artifact.

    An operator cannot turn a pending map contract into ``verified`` by merely
    passing a CLI flag.  A replay therefore needs this separately reviewable
    evidence bound to the exact frozen map snapshot.
    """

    evidence = _mapping(value, "operator_map_coordinate_evidence_invalid")
    if evidence.get("schema") != COORDINATE_EVIDENCE_SCHEMA:
        raise ValueError("operator_map_coordinate_evidence_schema_invalid")
    if evidence.get("status") != "verified":
        raise ValueError("operator_map_coordinate_evidence_not_verified")
    _required_string(evidence.get("evidence_id"), "operator_map_coordinate_evidence_id_missing")
    if evidence.get("operator_map_snapshot_hash") != snapshot_hash:
        raise ValueError("operator_map_coordinate_evidence_snapshot_mismatch")
    for field in MAP_IDENTITY_FIELDS:
        if evidence.get(field) != map_snapshot.get(field):
            raise ValueError("operator_map_coordinate_evidence_identity_mismatch")
    source_frame = _required_string(evidence.get("source_frame_id"), "operator_map_coordinate_evidence_frame_missing")
    target_frame = _required_string(evidence.get("target_frame_id"), "operator_map_coordinate_evidence_frame_missing")
    if target_frame != map_snapshot.get("world_frame"):
        raise ValueError("operator_map_coordinate_evidence_target_frame_mismatch")
    matrix = _transform_matrix(evidence.get("transform_target_from_source_4x4"))
    normalized = dict(evidence)
    normalized["source_frame_id"] = source_frame
    normalized["target_frame_id"] = target_frame
    normalized["transform_target_from_source_4x4"] = matrix
    return normalized


def load_coordinate_evidence(
    path: Path,
    *,
    map_snapshot: dict[str, Any],
    snapshot_hash: str,
) -> tuple[dict[str, Any], str]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("operator_map_coordinate_evidence_missing") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("operator_map_coordinate_evidence_unreadable") from exc
    return validate_coordinate_evidence(raw, map_snapshot=map_snapshot, snapshot_hash=snapshot_hash), sha256_file(path)


def normalize_replay_sample(value: Any, *, vehicle_count: int) -> dict[str, Any]:
    sample = _mapping(value, "operator_map_replay_sample_invalid")
    vehicle_id = _required_string(sample.get("vehicle_id"), "operator_map_replay_vehicle_id_invalid")
    match = VEHICLE_ID_PATTERN.fullmatch(vehicle_id)
    if match is None or int(match.group(1)) > vehicle_count:
        raise ValueError("operator_map_replay_vehicle_id_invalid")
    if not _finite_number(sample.get("bag_time_s")) or float(sample["bag_time_s"]) < 0.0:
        raise ValueError("operator_map_replay_bag_time_invalid")
    source_timestamp = sample.get("source_timestamp_s")
    if source_timestamp is not None and (not _finite_number(source_timestamp) or float(source_timestamp) < 0.0):
        raise ValueError("operator_map_replay_source_time_invalid")
    normalized: dict[str, Any] = {
        "vehicle_id": vehicle_id,
        "bag_time_s": float(sample["bag_time_s"]),
        "source_timestamp_s": None if source_timestamp is None else float(source_timestamp),
        "frame_id": _required_string(sample.get("frame_id"), "operator_map_replay_sample_frame_missing"),
        "position": _vector(sample.get("position"), "operator_map_replay_position_invalid"),
    }
    for key in ("orientation", "linear_velocity", "angular_velocity"):
        if key not in sample or sample[key] is None:
            continue
        normalized[key] = (
            _quaternion(sample[key], "operator_map_replay_orientation_invalid")
            if key == "orientation"
            else _vector(sample[key], "operator_map_replay_velocity_invalid")
        )
    return normalized


def _matrix_vector(matrix: list[list[float]], vector: dict[str, float], *, translate: bool) -> dict[str, float]:
    values = [vector["x"], vector["y"], vector["z"]]
    return {
        axis: sum(matrix[row][column] * values[column] for column in range(3))
        + (matrix[row][3] if translate else 0.0)
        for row, axis in enumerate(("x", "y", "z"))
    }


def _quaternion_rotate_vector(quaternion: dict[str, float], vector: dict[str, float]) -> dict[str, float]:
    w, x, y, z = (quaternion[axis] for axis in ("w", "x", "y", "z"))
    vx, vy, vz = (vector[axis] for axis in ("x", "y", "z"))
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return {
        "x": vx + w * tx + (y * tz - z * ty),
        "y": vy + w * ty + (z * tx - x * tz),
        "z": vz + w * tz + (x * ty - y * tx),
    }


def _yaw_quaternion(forward: dict[str, float]) -> dict[str, float] | None:
    horizontal = math.hypot(forward["x"], forward["y"])
    if horizontal < 1e-9:
        return None
    half_yaw = math.atan2(forward["y"], forward["x"]) / 2.0
    return {"w": math.cos(half_yaw), "x": 0.0, "y": 0.0, "z": math.sin(half_yaw)}


def replay_vehicle_from_sample(sample: dict[str, Any], coordinate_evidence: dict[str, Any] | None) -> dict[str, Any]:
    """Project one normalized odometry sample into a drawable vehicle state."""

    state: dict[str, Any] = {"connected": True}
    frame_id = sample["frame_id"]
    position = dict(sample["position"])
    linear_velocity = sample.get("linear_velocity")
    angular_velocity = sample.get("angular_velocity")
    orientation = sample.get("orientation")
    if coordinate_evidence is not None:
        if frame_id != coordinate_evidence["source_frame_id"]:
            raise ValueError("operator_map_coordinate_evidence_source_frame_mismatch")
        matrix = coordinate_evidence["transform_target_from_source_4x4"]
        position = _matrix_vector(matrix, position, translate=True)
        frame_id = coordinate_evidence["target_frame_id"]
        if linear_velocity is not None:
            linear_velocity = _matrix_vector(matrix, linear_velocity, translate=False)
        if angular_velocity is not None:
            rotation = [row[:3] for row in matrix[:3]]
            determinant = _determinant_3x3(rotation)
            angular_velocity = {
                axis: determinant * value
                for axis, value in _matrix_vector(matrix, angular_velocity, translate=False).items()
            }
        if orientation is not None:
            forward = _quaternion_rotate_vector(orientation, {"x": 1.0, "y": 0.0, "z": 0.0})
            orientation = _yaw_quaternion(_matrix_vector(matrix, forward, translate=False))
    state["position"] = position
    state["position_frame"] = frame_id
    if orientation is not None:
        state["orientation"] = orientation
    if linear_velocity is not None:
        state["linear_velocity"] = linear_velocity
    if angular_velocity is not None:
        state["angular_velocity"] = angular_velocity
    return {"vehicle_id": sample["vehicle_id"], "state": state}


def derive_replay_frames(
    samples: list[dict[str, Any]],
    *,
    vehicle_count: int,
    coordinate_evidence: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Build a time-ordered state sequence without inventing missing vehicles."""

    if not samples:
        raise ValueError("operator_map_replay_samples_missing")
    normalized = [normalize_replay_sample(sample, vehicle_count=vehicle_count) for sample in samples]
    normalized = sorted(enumerate(normalized), key=lambda item: (item[1]["bag_time_s"], item[0]))
    expected_ids = [f"uav{index}" for index in range(1, vehicle_count + 1)]
    first_time = normalized[0][1]["bag_time_s"]
    current: dict[str, dict[str, Any]] = {}
    frames: list[dict[str, Any]] = []
    index = 0
    while index < len(normalized):
        bag_time = normalized[index][1]["bag_time_s"]
        source_times: list[float] = []
        while index < len(normalized) and normalized[index][1]["bag_time_s"] == bag_time:
            sample = normalized[index][1]
            current[sample["vehicle_id"]] = replay_vehicle_from_sample(sample, coordinate_evidence)
            if sample["source_timestamp_s"] is not None:
                source_times.append(sample["source_timestamp_s"])
            index += 1
        frames.append(
            {
                "playback_time_s": bag_time - first_time,
                "source_timestamp_s": max(source_times) if source_times else None,
                "vehicles": [current[vehicle_id] for vehicle_id in expected_ids]
                if all(vehicle_id in current for vehicle_id in expected_ids)
                else [],
            }
        )
    if set(current) != set(expected_ids):
        raise ValueError("operator_map_replay_vehicle_samples_incomplete")
    return frames


def build_replay_manifest(
    *,
    manifest: dict[str, Any],
    source_kind: str,
    source_path: Path,
    source_sha256: str,
    bag_id: str,
    odom_topics: dict[str, str],
    coordinate_evidence: dict[str, Any] | None,
    coordinate_evidence_sha256: str,
    frames: list[dict[str, Any]],
) -> dict[str, Any]:
    if not frames:
        raise ValueError("operator_map_replay_samples_missing")
    return {
        "schema": REPLAY_MANIFEST_SCHEMA,
        "run_id": manifest.get("run_id"),
        "profile_id": manifest.get("experiment_profile_id"),
        "profile_hash": manifest.get("experiment_profile_hash"),
        "operator_map_snapshot_hash": manifest.get("operator_map_snapshot_hash"),
        "source": {
            "kind": source_kind,
            "path": str(source_path),
            "sha256": source_sha256,
            "bag_id": bag_id,
            "odom_topics": dict(odom_topics),
        },
        "coordinate_evidence": {
            "status": "verified" if coordinate_evidence is not None else "pending_runtime_validation",
            "evidence_id": coordinate_evidence.get("evidence_id", "") if coordinate_evidence else "",
            "sha256": coordinate_evidence_sha256,
        },
        "frame_count": len(frames),
        "duration_s": frames[-1]["playback_time_s"],
        "output": {"telemetry_path": "telemetry.json", "transport_mode": "rosbag_replay"},
    }
