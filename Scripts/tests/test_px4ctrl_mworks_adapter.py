#!/usr/bin/env python3
"""Static contract checks for the px4ctrl MWORKS ATTITUDE_THRUST adapter."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / "Px4CtrlAttitudeThrustAdapter.mo"
PACKAGE_ORDER = ADAPTER.with_name("package.order")


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


def test_px4ctrl_adapter_is_registered_in_the_package_order() -> None:
    assert "Px4CtrlAttitudeThrustAdapter" in PACKAGE_ORDER.read_text(encoding="utf-8").splitlines()


def main() -> int:
    test_px4ctrl_adapter_uses_the_shared_attitude_thrust_contract()
    test_px4ctrl_adapter_shares_odometry_and_imu_quaternions()
    test_px4ctrl_adapter_emits_newton_increment_about_hover()
    test_px4ctrl_adapter_is_registered_in_the_package_order()
    print("[OK] px4ctrl MWORKS adapter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
