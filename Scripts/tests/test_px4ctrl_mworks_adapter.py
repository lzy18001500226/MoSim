#!/usr/bin/env python3
"""Static contract checks for the px4ctrl MWORKS ATTITUDE_THRUST adapter."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / "Px4CtrlAttitudeThrustAdapter.mo"
REPORT_BASELINE_ADAPTER = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Control"
    / "Adapters"
    / "Px4CtrlEquationBridgeReportBaselineAdapter.mo"
)
PACKAGE_ORDER = ADAPTER.with_name("package.order")
RUNNER = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Formal" / "Px4CtrlFormalRunner.mo"
RUNNER_PACKAGE_ORDER = RUNNER.with_name("package.order")
BASELINE_BINDING = ROOT / "Config" / "control_platform" / "runner_baseline_bindings" / "px4ctrl.json"
SUNRAY150_ASSEMBLY = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Sunray150Assembly.mo"
PHYSICAL_WRENCH_ADAPTER = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Dynamics" / "PhysicalWrenchAdapter.mo"
ROTOR_ACTUATOR_CORE = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Dynamics" / "RotorActuatorCore.mo"
VIRTUAL_PX4_CLASSIC_PROFILE = ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters" / "Sunray150VirtualPx4Classic.mo"


def test_px4ctrl_adapter_uses_the_shared_attitude_thrust_contract() -> None:
    source = ADAPTER.read_text(encoding="utf-8")

    for token in (
        "extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController",
        "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock core",
        "roll_mea = -attitude_mea[1]",
        "pitch_mea = attitude_mea[2]",
        "yaw_mea = attitude_mea[3]",
        "core.px = position_mea[1]",
        "core.py = position_mea[2]",
        "core.pz = position_mea[3]",
        "core.vx = velocity_mea[1]",
        "core.vy = velocity_mea[2]",
        "core.vz = velocity_mea[3]",
        "core.ref_px = position_ref[1]",
        "core.ref_py = position_ref[2]",
        "core.ref_pz = position_ref[3]",
        "core.ref_vx = velocity_ref[1]",
        "core.ref_vy = velocity_ref[2]",
        "core.ref_vz = velocity_ref[3]",
        "core.ref_ax = acceleration_ref[1]",
        "core.ref_ay = acceleration_ref[2]",
        "core.ref_az = acceleration_ref[3]",
        "core.ref_yaw = 0",
    ):
        assert token in source


def test_px4ctrl_adapter_shares_odometry_and_imu_quaternions() -> None:
    source = ADAPTER.read_text(encoding="utf-8")

    for token in (
        "core.qw = q_w",
        "core.qx = q_x",
        "core.qy = q_y",
        "core.qz = q_z",
        "core.imu_qw = q_w",
        "core.imu_qx = q_x",
        "core.imu_qy = q_y",
        "core.imu_qz = q_z",
        "core.qd_w",
        "core.qd_x",
        "core.qd_y",
        "core.qd_z",
    ):
        assert token in source


def test_px4ctrl_adapter_emits_newton_increment_about_hover() -> None:
    source = ADAPTER.read_text(encoding="utf-8")

    assert "profile.mworks_visual_thrust_coefficient" in source
    assert "profile.mworks_hover_visual_rotor_speed_rad_s ^ 2" in source
    assert "collective_thrust_delta = core.collective_thrust_n - hover_collective_thrust_n" in source


def test_px4ctrl_adapter_keeps_inverse_sine_evaluations_inside_the_real_domain() -> None:
    source = ADAPTER.read_text(encoding="utf-8")

    for token in (
        "parameter Real pitch_argument_domain_margin",
        "pitch_argument_safe = min(1 - pitch_argument_domain_margin",
        "max(-1 + pitch_argument_domain_margin, pitch_argument))",
        "pitch_argument_clipped = abs(pitch_argument - pitch_argument_safe) > 0",
        "else asin(pitch_argument_safe)",
    ):
        assert token in source


def test_px4ctrl_report_baseline_adapter_uses_the_report_pitch_branch() -> None:
    source = REPORT_BASELINE_ADAPTER.read_text(encoding="utf-8")

    assert "extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController" in source
    assert "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock core" in source
    assert "else asin(pitch_argument);" in source
    assert "pitch_argument_safe" not in source


def test_px4ctrl_adapter_is_registered_in_the_package_order() -> None:
    assert "Px4CtrlAttitudeThrustAdapter" in PACKAGE_ORDER.read_text(encoding="utf-8").splitlines()


def test_px4ctrl_formal_runner_is_registered_in_the_package_order() -> None:
    assert "Px4CtrlFormalRunner" in RUNNER_PACKAGE_ORDER.read_text(encoding="utf-8").splitlines()


def test_px4ctrl_formal_runner_uses_the_equation_bridge_baseline() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "extends Px4CtrlEquationBridgeFormalRunner;" in source
    assert "extends Px4CtrlGraphicalRealStateFormalRunner;" not in source


def test_px4ctrl_baseline_binding_declares_the_shared_sampled_boundary() -> None:
    binding = json.loads(BASELINE_BINDING.read_text(encoding="utf-8"))

    assert binding["schema"] == "mosim.runner_boundary_baseline_binding.v1"
    assert binding["controller_id"] == "px4ctrl"
    assert binding["target"]["model_class"] == "MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner"
    assert binding["formal_adapter"]["model_class"] == (
        "MoSimQuadrotorModel.Control.Adapters.Px4CtrlEquationBridgeReportBaselineAdapter"
    )
    assert binding["formal_adapter"]["role"] == "active_formal_runner_baseline"
    assert binding["formal_harness_feedback_boundary"]["kind"] == "sampled_controller_inputs"
    assert binding["formal_harness_feedback_boundary"]["effective_model_file"] == (
        "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/"
        "Px4CtrlEquationBridgeFormalRunner.mo"
    )
    assert binding["formal_harness_feedback_boundary"]["signals"] == [
        "reference.position_command -> controller.position_ref",
        "reference.velocity_command -> controller.velocity_ref",
        "reference.acceleration_command -> controller.acceleration_ref",
        "plant.position -> controller.position_mea",
        "plant.attitude -> controller.attitude_mea",
    ]
    assert binding["formal_harness_feedback_boundary"]["continuous_inner_loop_signals"] == [
        "plant.attitude -> offline_inner_allocator.attitude_mea",
    ]
    assert binding["report_export_binding"]["roll"] == "-controller.roll_mea"


def test_px4ctrl_active_plant_preserves_lift_coefficient_units() -> None:
    declaration = 'parameter Real lift_coefficient(unit = "N.s2/rad2")'

    for source in (SUNRAY150_ASSEMBLY, PHYSICAL_WRENCH_ADAPTER, ROTOR_ACTUATOR_CORE):
        assert declaration in source.read_text(encoding="utf-8")
    assert 'mworks_visual_thrust_coefficient(unit = "N.s2/rad2")' in VIRTUAL_PX4_CLASSIC_PROFILE.read_text(encoding="utf-8")


def main() -> int:
    test_px4ctrl_adapter_uses_the_shared_attitude_thrust_contract()
    test_px4ctrl_adapter_shares_odometry_and_imu_quaternions()
    test_px4ctrl_adapter_emits_newton_increment_about_hover()
    test_px4ctrl_adapter_keeps_inverse_sine_evaluations_inside_the_real_domain()
    test_px4ctrl_report_baseline_adapter_uses_the_report_pitch_branch()
    test_px4ctrl_adapter_is_registered_in_the_package_order()
    test_px4ctrl_formal_runner_is_registered_in_the_package_order()
    test_px4ctrl_formal_runner_uses_the_equation_bridge_baseline()
    test_px4ctrl_baseline_binding_declares_the_shared_sampled_boundary()
    test_px4ctrl_active_plant_preserves_lift_coefficient_units()
    print("[OK] px4ctrl MWORKS adapter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
