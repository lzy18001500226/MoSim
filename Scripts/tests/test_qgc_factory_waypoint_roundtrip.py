from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from Scripts.ui.factory_map_coordinates import (
    coordinate_for_world,
    horizontal_distance_m,
    world_distance_m,
    world_for_coordinate,
)
from Scripts.ui.validate_qgc_factory_waypoint_roundtrip import ValidationError, validate_plan


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "operator_map_catalog.json"
FIXTURE = ROOT / "Scripts" / "tests" / "fixtures" / "factory_l2_qgc_waypoint_roundtrip.plan"


def _plan() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_factory_l2_qgc_fixture_passes_offline_gate_but_not_publication() -> None:
    result = validate_plan(FIXTURE, map_config_path=CATALOG, require_task_boundary=True)

    assert result["status"] == "offline_round_trip_passed"
    assert result["source"] == "offline_script"
    assert result["offline_gate"]["status"] == "passed"
    assert result["qgc_plan"]["file_type"] == "Plan"
    assert result["qgc_plan"]["mission_version"] == 2
    assert result["qgc_plan"]["mission_item_count"] == 4
    assert result["offline_gate"]["max_horizontal_error_m"] < 0.05
    assert result["offline_gate"]["max_world_error_m"] < 0.05
    assert result["offline_gate"]["max_altitude_error_m"] == 0.0
    assert result["mission_publication"]["allowed"] is False
    assert "simulation_geodetic_anchor_not_runtime_verified" in result["mission_publication"]["blockers"]


def test_local_transform_round_trips_representative_factory_points() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    anchor = catalog["maps"][0]["simulation_geodetic_anchor"]
    for x_m, y_m in ((-90.0, -45.0), (0.0, 0.0), (70.0, 10.0)):
        coordinate = coordinate_for_world(anchor, x_m, y_m, altitude_m=20.0)
        world = world_for_coordinate(anchor, coordinate["latitude_deg"], coordinate["longitude_deg"])
        assert world_distance_m(world, {"x_m": x_m, "y_m": y_m}) < 1.0e-6
        round_trip = coordinate_for_world(anchor, world["x_m"], world["y_m"], altitude_m=20.0)
        assert horizontal_distance_m(coordinate, round_trip) < 1.0e-6


def test_validator_rejects_complex_items_without_claiming_a_partial_pass(tmp_path: Path) -> None:
    plan = _plan()
    plan["mission"]["items"][0]["type"] = "ComplexItem"
    path = tmp_path / "complex.plan"
    path.write_text(json.dumps(plan), encoding="utf-8")

    with pytest.raises(ValidationError, match="only SimpleItem") as error:
        validate_plan(path, map_config_path=CATALOG)
    assert error.value.reason == "unsupported_qgc_mission_item"


def test_validator_rejects_home_outside_runtime_anchor_tolerance(tmp_path: Path) -> None:
    plan = _plan()
    plan["mission"]["plannedHomePosition"][0] += 0.001
    path = tmp_path / "bad-home.plan"
    path.write_text(json.dumps(plan), encoding="utf-8")

    with pytest.raises(ValidationError, match="planned home") as error:
        validate_plan(path, map_config_path=CATALOG)
    assert error.value.reason == "planned_home_outside_anchor_tolerance"


def test_validator_rejects_waypoint_outside_task_boundary_when_requested(tmp_path: Path) -> None:
    plan = _plan()
    plan["mission"]["items"][0]["params"][4:6] = [47.3985, 8.545594]
    path = tmp_path / "outside-task.plan"
    path.write_text(json.dumps(plan), encoding="utf-8")

    with pytest.raises(ValidationError, match="outside the task overlay") as error:
        validate_plan(path, map_config_path=CATALOG, require_task_boundary=True)
    assert error.value.reason == "waypoint_outside_task_boundary"


def test_validator_rejects_altitude_field_drift(tmp_path: Path) -> None:
    plan = copy.deepcopy(_plan())
    plan["mission"]["items"][0]["Altitude"] += 1.0
    path = tmp_path / "bad-altitude.plan"
    path.write_text(json.dumps(plan), encoding="utf-8")

    with pytest.raises(ValidationError, match="Altitude does not match") as error:
        validate_plan(path, map_config_path=CATALOG)
    assert error.value.reason == "qgc_altitude_field_mismatch"

