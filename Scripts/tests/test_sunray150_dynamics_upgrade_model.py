from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "Models" / "QuadrotorExperiments" / "package.mo"


def test_dynamics_upgrade_keeps_parameter_provenance_labels() -> None:
    text = MODEL.read_text(encoding="utf-8")
    block_start = text.index("model Sunray150RflyStyleRotorDynamics")
    block_end = text.index("end Sunray150RflyStyleRotorDynamics;", block_start)
    block = text[block_start:block_end]

    assert "source=SDF_migration" in block
    assert "source=user-reviewed DAE screw-pair fit" in block
    assert "PX4_ULog_sysid" not in block
    assert "not ULog identified" in block


def test_dynamics_upgrade_contains_minimum_rfly_style_structure() -> None:
    text = MODEL.read_text(encoding="utf-8")
    required = [
        "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
        "thrust[i] = lift_coefficient * omega[i] * omega[i]",
        "yaw_reaction_moment[i] = yaw_direction[i] * moment_constant * thrust[i]",
        "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
        "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
        "total_moment_body[3]",
    ]
    for snippet in required:
        assert snippet in text


def test_hover_and_yaw_step_reference_math() -> None:
    mass_kg = 1.0
    gravity = 9.81
    lift_coefficient = 0.000854858
    moment_constant = 0.06
    yaw_delta_omega2 = 300.0
    rotor_center = [
        (0.053745, -0.053740, -0.014052),
        (0.053746, 0.053759, -0.014052),
        (-0.053761, 0.053760, -0.014052),
        (-0.053761, -0.053739, -0.014052),
    ]
    yaw_direction = [1.0, -1.0, 1.0, -1.0]

    hover_speed = math.sqrt(mass_kg * gravity / (4.0 * lift_coefficient))
    hover_thrust = [lift_coefficient * hover_speed**2 for _ in range(4)]
    assert math.isclose(sum(hover_thrust), mass_kg * gravity, rel_tol=0, abs_tol=1e-12)

    yaw_step_thrust = [
        lift_coefficient * (hover_speed**2 + direction * yaw_delta_omega2)
        for direction in yaw_direction
    ]
    yaw_moment = sum(
        direction * moment_constant * thrust
        for direction, thrust in zip(yaw_direction, yaw_step_thrust)
    )
    assert yaw_moment > 0.0
    assert math.isclose(sum(yaw_step_thrust), mass_kg * gravity, rel_tol=0, abs_tol=1e-12)

    roll_arm_moment = sum(center[1] * thrust for center, thrust in zip(rotor_center, yaw_step_thrust))
    pitch_arm_moment = sum(-center[0] * thrust for center, thrust in zip(rotor_center, yaw_step_thrust))
    assert abs(roll_arm_moment) > 0.0
    assert abs(pitch_arm_moment) > 0.0
