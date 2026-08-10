"""Validate a QGC Plan against the Factory L2 offline coordinate gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from factory_map_coordinates import (  # type: ignore  # noqa: E402
        coordinate_for_world,
        horizontal_distance_m,
        world_distance_m,
        world_for_coordinate,
    )
else:
    from .factory_map_coordinates import (  # noqa: E402
        coordinate_for_world,
        horizontal_distance_m,
        world_distance_m,
        world_for_coordinate,
    )


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAP_CONFIG = ROOT / "Config" / "control_platform" / "operator_map_catalog.json"
SUPPORTED_GLOBAL_FRAMES = frozenset({0, 3, 5, 6, 11})
SUPPORTED_COORDINATE_COMMANDS = frozenset({16, 19, 21, 22, 84, 85})


class ValidationError(ValueError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason
        self.message = message


def _finite(value: Any, reason: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(reason, f"{reason}: value is not numeric") from exc
    if not math.isfinite(number):
        raise ValidationError(reason, f"{reason}: value is not finite")
    return number


def _read_json(path: Path, reason: str) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(reason, f"{reason}: unable to read {path}") from exc
    if not isinstance(value, dict):
        raise ValidationError(reason, f"{reason}: root must be an object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _map_entry(catalog: Mapping[str, Any], map_id: str) -> Mapping[str, Any]:
    if catalog.get("schema") != "mosim.operator_map_catalog.v1":
        raise ValidationError("map_catalog_schema_invalid", "operator map catalog schema is not supported")
    maps = catalog.get("maps")
    if not isinstance(maps, list):
        raise ValidationError("map_catalog_maps_missing", "operator map catalog maps must be an array")
    for entry in maps:
        if isinstance(entry, dict) and entry.get("map_id") == map_id:
            return entry
    raise ValidationError("map_id_not_found", f"operator map {map_id!r} is not registered")


def _coordinate(value: Any, reason: str) -> Dict[str, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValidationError(reason, f"{reason}: QGC coordinate must be [lat, lon, alt]")
    return {
        "latitude_deg": _finite(value[0], f"{reason}_latitude"),
        "longitude_deg": _finite(value[1], f"{reason}_longitude"),
        "altitude_m": _finite(value[2], f"{reason}_altitude"),
    }


def _bounds(entry: Mapping[str, Any], key: str) -> Mapping[str, float]:
    value = entry.get(key)
    if not isinstance(value, dict):
        raise ValidationError("map_bounds_missing", f"map entry is missing {key}")
    result = {
        "min_x_m": _finite(value.get("min_x_m"), f"{key}_min_x_m"),
        "max_x_m": _finite(value.get("max_x_m"), f"{key}_max_x_m"),
        "min_y_m": _finite(value.get("min_y_m"), f"{key}_min_y_m"),
        "max_y_m": _finite(value.get("max_y_m"), f"{key}_max_y_m"),
    }
    if result["min_x_m"] >= result["max_x_m"] or result["min_y_m"] >= result["max_y_m"]:
        raise ValidationError("map_bounds_invalid", f"{key} has inverted bounds")
    return result


def _inside(point: Mapping[str, float], bounds: Mapping[str, float]) -> bool:
    return (
        bounds["min_x_m"] <= point["x_m"] <= bounds["max_x_m"]
        and bounds["min_y_m"] <= point["y_m"] <= bounds["max_y_m"]
    )


def _item_coordinate(item: Mapping[str, Any], index: int) -> Tuple[int, int, Dict[str, float]]:
    item_type = item.get("type")
    if item_type != "SimpleItem":
        raise ValidationError(
            "unsupported_qgc_mission_item",
            f"mission item {index} has type {item_type!r}; only SimpleItem waypoints are supported",
        )
    try:
        command = int(item["command"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("qgc_command_missing", f"mission item {index} has no integer command") from exc
    if command not in SUPPORTED_COORDINATE_COMMANDS:
        raise ValidationError(
            "unsupported_qgc_command",
            f"mission item {index} command {command} is outside the waypoint gate",
        )
    try:
        frame = int(item["frame"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("qgc_frame_missing", f"mission item {index} has no integer frame") from exc
    if frame not in SUPPORTED_GLOBAL_FRAMES:
        raise ValidationError(
            "qgc_frame_not_global",
            f"mission item {index} frame {frame} is not a supported global frame",
        )
    params = item.get("params")
    if not isinstance(params, list) or len(params) < 7:
        raise ValidationError(
            "qgc_params_missing",
            f"mission item {index} must contain seven QGC params",
        )
    coordinate = {
        "latitude_deg": _finite(params[4], f"mission_item_{index}_latitude"),
        "longitude_deg": _finite(params[5], f"mission_item_{index}_longitude"),
        "altitude_m": _finite(params[6], f"mission_item_{index}_altitude"),
    }
    if "Altitude" in item:
        stored_altitude = _finite(item["Altitude"], f"mission_item_{index}_Altitude")
        if abs(stored_altitude - coordinate["altitude_m"]) > 1.0e-6:
            raise ValidationError(
                "qgc_altitude_field_mismatch",
                f"mission item {index} Altitude does not match params[6]",
            )
    return index, frame, coordinate


def _coordinate_record(
    anchor: Mapping[str, Any],
    coordinate: Mapping[str, float],
    map_bounds: Mapping[str, float],
    task_bounds: Mapping[str, float],
    tolerance_m: float,
    label: str,
    require_task_boundary: bool,
) -> Dict[str, Any]:
    world = world_for_coordinate(anchor, coordinate["latitude_deg"], coordinate["longitude_deg"])
    if not _inside(world, map_bounds):
        raise ValidationError("waypoint_outside_map_bounds", f"{label} maps outside Factory L2 bounds")
    inside_task = _inside(world, task_bounds)
    if require_task_boundary and not inside_task:
        raise ValidationError("waypoint_outside_task_boundary", f"{label} maps outside the task overlay bounds")

    round_trip_coordinate = coordinate_for_world(
        anchor,
        world["x_m"],
        world["y_m"],
        altitude_m=coordinate["altitude_m"],
    )
    round_trip_world = world_for_coordinate(
        anchor,
        round_trip_coordinate["latitude_deg"],
        round_trip_coordinate["longitude_deg"],
    )
    horizontal_error = horizontal_distance_m(coordinate, round_trip_coordinate)
    world_error = world_distance_m(world, round_trip_world)
    altitude_error = abs(coordinate["altitude_m"] - round_trip_coordinate["altitude_m"])
    if horizontal_error > tolerance_m or world_error > tolerance_m or altitude_error > 1.0e-6:
        raise ValidationError("coordinate_round_trip_error", f"{label} exceeds the offline round-trip tolerance")
    return {
        "input_coordinate": dict(coordinate),
        "world": world,
        "round_trip_coordinate": round_trip_coordinate,
        "round_trip_world": round_trip_world,
        "horizontal_error_m": horizontal_error,
        "world_error_m": world_error,
        "altitude_error_m": altitude_error,
        "inside_task_overlay": inside_task,
    }


def validate_plan(
    plan_path: Path,
    map_config_path: Path = DEFAULT_MAP_CONFIG,
    map_id: str = "factory_l2",
    tolerance_m: float = 0.05,
    require_task_boundary: bool = False,
) -> Dict[str, Any]:
    """Validate a current QGC Plan without connecting to a vehicle."""

    if tolerance_m <= 0.0 or not math.isfinite(tolerance_m):
        raise ValidationError("round_trip_tolerance_invalid", "round-trip tolerance must be finite and positive")
    plan_path = Path(plan_path)
    map_config_path = Path(map_config_path)
    plan = _read_json(plan_path, "qgc_plan_read_failed")
    catalog = _read_json(map_config_path, "map_catalog_read_failed")
    entry = _map_entry(catalog, map_id)
    if plan.get("fileType") != "Plan" or plan.get("version") != 1:
        raise ValidationError("qgc_plan_header_invalid", "QGC plan must use fileType=Plan and version=1")
    if plan.get("groundStation") != "QGroundControl":
        raise ValidationError("qgc_ground_station_invalid", "QGC plan groundStation is not QGroundControl")

    mission = plan.get("mission")
    if not isinstance(mission, dict) or mission.get("version") != 2:
        raise ValidationError("qgc_mission_schema_invalid", "QGC plan mission must use version=2")
    items = mission.get("items")
    if not isinstance(items, list) or not items:
        raise ValidationError("qgc_mission_items_missing", "QGC plan must contain at least one mission item")
    home = _coordinate(mission.get("plannedHomePosition"), "planned_home_position")

    anchor = entry.get("simulation_geodetic_anchor")
    if not isinstance(anchor, dict):
        raise ValidationError("geodetic_anchor_missing", "operator map has no simulation geodetic anchor")
    map_bounds = _bounds(entry, "world_bounds_m")
    task_bounds = _bounds(entry, "indoor_task_overlay_bounds_m")
    publication = entry.get("mission_publication")
    if not isinstance(publication, dict):
        raise ValidationError("mission_publication_contract_missing", "operator map has no mission publication contract")

    home_record = _coordinate_record(
        anchor,
        home,
        map_bounds,
        task_bounds,
        tolerance_m,
        "planned home",
        False,
    )
    home_tolerance = _finite(publication.get("required_home_tolerance_m"), "required_home_tolerance_m")
    home_error = horizontal_distance_m(
        home,
        {
            "latitude_deg": _finite(anchor["latitude_deg"], "anchor_latitude_deg"),
            "longitude_deg": _finite(anchor["longitude_deg"], "anchor_longitude_deg"),
            "altitude_m": _finite(anchor.get("altitude_m", 0.0), "anchor_altitude_m"),
        },
    )
    if home_error > home_tolerance:
        raise ValidationError("planned_home_outside_anchor_tolerance", "planned home is not within the map anchor tolerance")

    map_item_records: List[Dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError("qgc_mission_item_invalid", f"mission item {index} is not an object")
        item_index, frame, coordinate = _item_coordinate(item, index)
        record = _coordinate_record(
            anchor,
            coordinate,
            map_bounds,
            task_bounds,
            tolerance_m,
            f"mission item {index}",
            require_task_boundary,
        )
        record.update(
            {
                "item_index": item_index,
                "do_jump_id": item.get("doJumpId"),
                "command": int(item["command"]),
                "frame": frame,
                "altitude_reference": {
                    0: "absolute",
                    3: "relative",
                    5: "absolute_int",
                    6: "relative_int",
                    11: "terrain",
                }[frame],
            }
        )
        map_item_records.append(record)

    publication_status = str(publication.get("status", ""))
    contract_status = str(entry.get("coordinate_contract_status", ""))
    anchor_status = str(anchor.get("status", ""))
    publication_blockers = []
    if publication_status != "verified":
        publication_blockers.append("mission_publication_status_not_verified")
    if contract_status != "verified":
        publication_blockers.append("coordinate_contract_status_not_verified")
    if anchor_status not in {"verified", "runtime_verified", "runtime_confirmed"}:
        publication_blockers.append("simulation_geodetic_anchor_not_runtime_verified")

    max_horizontal_error = max(record["horizontal_error_m"] for record in map_item_records)
    max_world_error = max(record["world_error_m"] for record in map_item_records)
    max_altitude_error = max(record["altitude_error_m"] for record in map_item_records)
    return {
        "schema": "mosim.qgc_factory_waypoint_round_trip.v1",
        "status": "offline_round_trip_passed",
        "source": "offline_script",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "qgc_plan": {
            "path": str(plan_path.resolve()),
            "sha256": _sha256(plan_path),
            "file_type": plan.get("fileType"),
            "version": plan.get("version"),
            "mission_version": mission.get("version"),
            "mission_item_count": len(map_item_records),
        },
        "operator_map": {
            "map_id": entry.get("map_id"),
            "map_version": entry.get("map_version"),
            "coordinate_contract_id": entry.get("coordinate_contract_id"),
            "coordinate_contract_status": contract_status,
            "map_config_path": str(map_config_path.resolve()),
            "map_config_sha256": _sha256(map_config_path),
        },
        "offline_gate": {
            "status": "passed",
            "round_trip_tolerance_m": tolerance_m,
            "require_task_boundary": require_task_boundary,
            "home_anchor_error_m": home_error,
            "home_anchor_tolerance_m": home_tolerance,
            "max_horizontal_error_m": max_horizontal_error,
            "max_world_error_m": max_world_error,
            "max_altitude_error_m": max_altitude_error,
            "home": home_record,
            "items": map_item_records,
        },
        "mission_publication": {
            "allowed": not publication_blockers,
            "status": publication_status,
            "blockers": publication_blockers,
            "note": "Offline geometry validation does not prove runtime geodetic origin or authorize QGC upload.",
        },
        "claim_boundary": [
            "This is offline_script evidence only; it is not MWORKS, Gazebo, PX4, MAVROS, or live QGC evidence.",
            "The validator covers QGC SimpleItem global waypoint-style commands and rejects unsupported complex items.",
            "A passed offline round trip leaves mission publication blocked until the runtime anchor and coordinate contract are verified.",
        ],
    }


def _write_result(path: Optional[Path], result: Mapping[str, Any]) -> None:
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--map-config", type=Path, default=DEFAULT_MAP_CONFIG)
    parser.add_argument("--map-id", default="factory_l2")
    parser.add_argument("--tolerance-m", type=float, default=0.05)
    parser.add_argument("--require-task-boundary", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_plan(
            args.plan,
            map_config_path=args.map_config,
            map_id=args.map_id,
            tolerance_m=args.tolerance_m,
            require_task_boundary=args.require_task_boundary,
        )
    except ValidationError as exc:
        result = {
            "schema": "mosim.qgc_factory_waypoint_round_trip.v1",
            "status": "failed",
            "source": "offline_script",
            "reason": exc.reason,
            "message": exc.message,
            "claim_boundary": ["Validation failed before any vehicle or QGC upload action."],
        }
        _write_result(args.output, result)
        return 2
    _write_result(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
