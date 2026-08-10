#!/usr/bin/env python3
"""Static contract checks for the PX4CTRL OpenBlocks single-UAV runner."""

from __future__ import annotations

import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning"
REFERENCE = PLANNING / "OpenBlocksPx4CtrlReference.mo"
RUNNER = PLANNING / "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop.mo"
PACKAGE = PLANNING / "package.mo"
PACKAGE_ORDER = PLANNING / "package.order"


def parse_array(source: str, name: str) -> list[float]:
    match = re.search(rf"{re.escape(name)}\s*=\s*\{{(.*?)\}}\s*(?:,|\))", source, re.S)
    if not match:
        raise AssertionError(f"missing {name} assignment")
    return [float(value.strip()) for value in match.group(1).split(",") if value.strip()]


def quintic_second_derivative(tau: float, duration: float) -> float:
    ratio = min(1.0, max(0.0, tau / max(1e-9, duration)))
    return (60.0 * ratio - 180.0 * ratio * ratio + 120.0 * ratio ** 3) / duration ** 2


def test_reference_provides_the_px4ctrl_pva_contract() -> None:
    source = REFERENCE.read_text(encoding="utf-8")
    for token in (
        "extends PlannedQuinticReference(",
        "n_segments = 53",
        "Modelica.Blocks.Interfaces.RealOutput velocity_command[3]",
        "Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]",
        "function smoothstepSecondDerivative",
        "velocity_command[1] = piecewiseRate(p_x, time, n_segments, segment_duration);",
        "acceleration_command[3] = piecewiseAcceleration(p_z, time, n_segments, segment_duration);",
    ):
        assert token in source


def test_reference_arrays_are_complete_and_have_finite_quintic_acceleration() -> None:
    source = REFERENCE.read_text(encoding="utf-8")
    p_x = parse_array(source, "p_x")
    p_y = parse_array(source, "p_y")
    p_z = parse_array(source, "p_z")
    durations = parse_array(source, "segment_duration")

    assert len(p_x) == len(p_y) == len(p_z) == 91
    assert len(durations) == 90
    assert p_x[0:2] == [-41.0, -41.0]
    assert p_y[0:2] == [-26.0, -26.0]
    assert p_z[0] == 1.5
    assert p_x[53] == 41.0
    assert p_y[53] == 26.0
    assert math.isclose(p_z[53], 0.68, abs_tol=1e-12)
    assert math.isclose(sum(durations[:53]), 80.1247340259, rel_tol=0.0, abs_tol=1e-8)
    assert all(duration > 0.0 for duration in durations[:53])
    assert all(math.isfinite(quintic_second_derivative(0.5 * duration, duration)) for duration in durations[:53])


def test_runner_preserves_the_formal_px4ctrl_boundary_and_map_review_surface() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    for token in (
        "extends MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner(",
        "redeclare model Trajectory = OpenBlocksPx4CtrlReference",
        "plant(initial_position_m = initial_position_m)",
        "The graphical PX4CTRL outer loop owns its 100 Hz sample boundary.",
        "OpenBlocksMapTruthDisplay navigationDisplay(",
        "p_x = reference.p_x",
        "Canonical full-map truth with a separate 6 m local sensing overlay.",
        "connect(plant.position, navigationDisplay.actual_position);",
        "connect(reference.position_command, navigationDisplay.reference_position);",
        "StopTime = 80.1247340259",
    ):
        assert token in source


def test_public_alias_and_package_order_are_complete() -> None:
    package_source = PACKAGE.read_text(encoding="utf-8")
    package_order = PACKAGE_ORDER.read_text(encoding="utf-8").splitlines()
    assert "model OpenBlocksPx4Ctrl" in package_source
    assert "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop" in package_source
    for name in (
        "OpenBlocksPx4CtrlReference",
        "OpenBlocksMapTruthDisplay",
        "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop",
    ):
        assert name in package_order


def main() -> int:
    test_reference_provides_the_px4ctrl_pva_contract()
    test_reference_arrays_are_complete_and_have_finite_quintic_acceleration()
    test_runner_preserves_the_formal_px4ctrl_boundary_and_map_review_surface()
    test_public_alias_and_package_order_are_complete()
    print("[OK] PX4CTRL OpenBlocks MWORKS surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
