#!/usr/bin/env python3
"""Static contracts for the separated PX4CTRL 7.2c and 7.2d evidence paths."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
GRAPHICAL_DIR = MODEL_ROOT / "Experiment" / "Runners" / "Graphical"
FORMAL_RUNNER = MODEL_ROOT / "Experiment" / "Runners" / "Formal" / "Px4CtrlFormalRunner.mo"
EQUATION_BRIDGE_RUNNER = MODEL_ROOT / "Experiment" / "Runners" / "Formal" / "Px4CtrlEquationBridgeFormalRunner.mo"
REAL_STATE_RUNNER = MODEL_ROOT / "Experiment" / "Runners" / "Formal" / "Px4CtrlGraphicalRealStateFormalRunner.mo"
QUATERNION_HARNESS = GRAPHICAL_DIR / "Px4CtrlGraphicalQuaternionOrderValidationHarness.mo"
GRAPHICAL_ORDER = GRAPHICAL_DIR / "package.order"
REAL_STATE_SCRIPT = ROOT / "Scripts" / "mworks" / "run_px4ctrl_graphical_real_state_equivalence.py"
QUATERNION_SCRIPT = ROOT / "Scripts" / "mworks" / "run_px4ctrl_graphical_quaternion_order_validation.py"


def section(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def test_7_2c_uses_real_sensor_ports_and_keeps_the_baseline_runner() -> None:
    source = REAL_STATE_RUNNER.read_text(encoding="utf-8")
    baseline = FORMAL_RUNNER.read_text(encoding="utf-8")
    equation_bridge = EQUATION_BRIDGE_RUNNER.read_text(encoding="utf-8")

    for token in (
        "connect(plant.VelMea[1], graphical_outer.vx);",
        "connect(plant.VelMea[2], graphical_outer.vy);",
        "connect(plant.VelMea[3], graphical_outer.vz);",
        "quat_xyzw = plant.QuatMea;",
        "quat_wxyz = {quat_xyzw[4], quat_xyzw[1], quat_xyzw[2], quat_xyzw[3]};",
        "connect(plant.BodyRateMea, offline_inner_allocator.body_rate_mea);",
    ):
        assert token in source
    assert "extends Px4CtrlEquationBridgeFormalRunner;" in baseline
    assert "extends Px4CtrlGraphicalRealStateFormalRunner;" not in baseline
    assert "Px4CtrlEquationBridgeReportBaselineAdapter controller" in equation_bridge


def test_7_2d_has_an_isolated_graphical_harness() -> None:
    source = QUATERNION_HARNESS.read_text(encoding="utf-8")

    for token in (
        "Px4CtrlGraphicalRealStateFormalRunner graphical_formal",
        "reorder_identity_error = quat_wxyz - {quat_xyzw[4], quat_xyzw[1], quat_xyzw[2], quat_xyzw[3]};",
        "yaw_to_graphical_sysblock = graphical_formal.sampled_attitude[3].y;",
    ):
        assert token in source
    assert "Px4CtrlEquationBridgeFormalRunner" not in source
    assert "Px4CtrlGraphicalQuaternionOrderValidationHarness" in GRAPHICAL_ORDER.read_text(encoding="utf-8").splitlines()


def test_extractors_use_the_canonical_root_and_do_not_mix_7_2d_into_7_2c() -> None:
    real_state_source = REAL_STATE_SCRIPT.read_text(encoding="utf-8")
    quaternion_source = QUATERNION_SCRIPT.read_text(encoding="utf-8")
    signal_groups = section(real_state_source, "def build_signal_groups()", "def unique_names(")

    assert "OpenModelFile(str(package_path))" in real_state_source
    assert "OpenModelFile(str(package_path))" in quaternion_source
    assert "MWORKS_DIRECT_API" in real_state_source
    assert "MWORKS_DIRECT_API" in quaternion_source
    assert "quaternion_wxyz" not in signal_groups
    assert "quaternion_order_boundary" in real_state_source
    assert "Px4CtrlGraphicalQuaternionOrderValidationHarness" in quaternion_source
    assert "quaternion_order_7_2d_metrics.v1" in quaternion_source


def main() -> int:
    test_7_2c_uses_real_sensor_ports_and_keeps_the_baseline_runner()
    test_7_2d_has_an_isolated_graphical_harness()
    test_extractors_use_the_canonical_root_and_do_not_mix_7_2d_into_7_2c()
    print("[OK] px4ctrl graphical real-state evidence contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
