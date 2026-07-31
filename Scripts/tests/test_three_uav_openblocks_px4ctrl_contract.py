#!/usr/bin/env python3
"""Static contract for the three-UAV OpenBlocks PX4CTRL MWORKS entry point."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning"
MODEL = PLANNING / "ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl.mo"
VEHICLE = PLANNING / "OpenBlocksPx4CtrlVehicle.mo"
REFERENCE = PLANNING / "PlannedQuinticPx4CtrlReference.mo"
PACKAGE = PLANNING / "package.mo"
ORDER = PLANNING / "package.order"


def component_body(source: str, component_name: str) -> str:
    match = re.search(rf"(?s)\b{re.escape(component_name)}\s*\((.*?)\)\s*annotation", source)
    if not match:
        raise AssertionError(f"Missing component declaration: {component_name}")
    return match.group(1)


def literal_vector(body: str, field_name: str) -> list[str]:
    match = re.search(rf"\b{re.escape(field_name)}\s*=\s*\{{", body)
    if not match:
        raise AssertionError(f"Missing vector binding: {field_name}")
    start = match.end()
    depth = 1
    cursor = start
    while cursor < len(body) and depth:
        if body[cursor] == "{":
            depth += 1
        elif body[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise AssertionError(f"Unclosed vector binding: {field_name}")
    return re.findall(r"(?<![A-Za-z_])[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?", body[start : cursor - 1])


def assert_connection(source: str, left: str, right: str) -> None:
    needle = f"connect({left}, {right})"
    if needle not in source:
        raise AssertionError(f"Missing connection: {needle}")


def main() -> int:
    model = MODEL.read_text(encoding="utf-8")
    vehicle = VEHICLE.read_text(encoding="utf-8")
    reference = REFERENCE.read_text(encoding="utf-8")
    package = PACKAGE.read_text(encoding="utf-8")
    order = ORDER.read_text(encoding="utf-8").splitlines()

    assert "model ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl" in model
    assert "LinearMPC" not in model
    assert model.count("PlannedQuinticPx4CtrlReference reference") == 3
    assert model.count("OpenBlocksPx4CtrlVehicle vehicle") == 3
    assert "OpenBlocksMapTruthDisplay navigationDisplay" in model

    for index in (1, 2, 3):
        component = component_body(model, f"reference{index}")
        for field, expected_length in (("p_x", 91), ("p_y", 91), ("p_z", 91), ("segment_duration", 90)):
            assert len(literal_vector(component, field)) == expected_length, (index, field)
        assert_connection(model, f"reference{index}.position_command", f"vehicle{index}.position_reference")
        assert_connection(model, f"reference{index}.velocity_command", f"vehicle{index}.velocity_reference")
        assert_connection(model, f"reference{index}.acceleration_command", f"vehicle{index}.acceleration_reference")

    assert_connection(model, "vehicle1.position", "navigationDisplay.actual_position")
    assert_connection(model, "reference1.position_command", "navigationDisplay.reference_position")
    for channel in ("pair_distance_12_m", "pair_distance_13_m", "pair_distance_23_m", "min_inter_uav_distance_m"):
        assert channel in model

    for required in (
        "Px4CtrlAttitudeThrustAdapter controller",
        "OfflineAttitudeRateAllocator allocator",
        "Sunray150Assembly plant",
        "connect(sampled_position_ref.y, controller.position_ref)",
        "connect(sampled_velocity_ref.y, controller.velocity_ref)",
        "connect(sampled_acceleration_ref.y, controller.acceleration_ref)",
        "connect(allocator.rotor_command, plant.rotor_command)",
    ):
        assert required in vehicle, required

    for required in (
        "extends PlannedQuinticReference;",
        "RealOutput velocity_command[3]",
        "RealOutput acceleration_command[3]",
        "velocity_command[1] = piecewiseRate(p_x, time, n_segments, segment_duration);",
        "acceleration_command[1] = piecewiseAcceleration(p_x, time, n_segments, segment_duration);",
    ):
        assert required in reference, required

    assert "model OpenBlocksThreeUavPx4CtrlFormation" in package
    assert "extends MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl;" in package
    for entry in (
        "PlannedQuinticPx4CtrlReference",
        "OpenBlocksPx4CtrlVehicle",
        "ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl",
    ):
        assert order.count(entry) == 1, entry

    print("[OK] Three-UAV OpenBlocks PX4CTRL source contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
