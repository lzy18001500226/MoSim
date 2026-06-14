from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "Models" / "QuadrotorExperiments" / "package.mo"
CORE_MODEL = (
    ROOT
    / "Models"
    / "QuadrotorExperiments"
    / "DynamicsUpgrade"
    / "Sunray150RflyStyleRotorDynamics.mo"
)


def test_dynamics_upgrade_keeps_parameter_provenance_labels() -> None:
    block = CORE_MODEL.read_text(encoding="utf-8")

    assert "source=SDF_migration" in block
    assert "source=user-reviewed DAE screw-pair fit" in block
    assert "PX4_ULog_sysid" not in block
    assert "not ULog identified" in block


def test_dynamics_upgrade_contains_minimum_rfly_style_structure() -> None:
    text = CORE_MODEL.read_text(encoding="utf-8")
    required = [
        "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
        "thrust[i] = thrust_effectiveness[i] * lift_coefficient * omega[i] * omega[i]",
        "yaw_reaction_moment[i] = yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust[i]",
        "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
        "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
        "minimum_thrust_effectiveness = min(thrust_effectiveness)",
        "minimum_reaction_moment_effectiveness = min(reaction_moment_effectiveness)",
        "total_moment_body[3]",
    ]
    for snippet in required:
        assert snippet in text


def test_top_level_package_keeps_deprecated_alias() -> None:
    text = MODEL.read_text(encoding="utf-8")

    assert "model Sunray150RflyStyleRotorDynamics" in text
    assert "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150RflyStyleRotorDynamics" in text


def test_hover_and_yaw_step_reference_math() -> None:
    mass_kg = 1.0
    gravity = 9.81
    lift_coefficient = 0.000854858
    moment_constant = 0.06
    thrust_effectiveness = [1.0, 1.0, 1.0, 1.0]
    reaction_moment_effectiveness = [1.0, 1.0, 1.0, 1.0]
    yaw_delta_omega2 = 300.0
    rotor_center = [
        (0.053745, -0.053740, -0.014052),
        (0.053746, 0.053759, -0.014052),
        (-0.053761, 0.053760, -0.014052),
        (-0.053761, -0.053739, -0.014052),
    ]
    yaw_direction = [1.0, -1.0, 1.0, -1.0]

    hover_speed = math.sqrt(mass_kg * gravity / (4.0 * lift_coefficient))
    hover_thrust = [effectiveness * lift_coefficient * hover_speed**2 for effectiveness in thrust_effectiveness]
    assert math.isclose(sum(hover_thrust), mass_kg * gravity, rel_tol=0, abs_tol=1e-12)

    yaw_step_thrust = [
        thrust_eff * lift_coefficient * (hover_speed**2 + direction * yaw_delta_omega2)
        for thrust_eff, direction in zip(thrust_effectiveness, yaw_direction)
    ]
    yaw_moment = sum(
        direction * reaction_eff * moment_constant * thrust
        for direction, reaction_eff, thrust in zip(
            yaw_direction, reaction_moment_effectiveness, yaw_step_thrust
        )
    )
    assert yaw_moment > 0.0
    assert math.isclose(sum(yaw_step_thrust), mass_kg * gravity, rel_tol=0, abs_tol=1e-12)

    roll_arm_moment = sum(center[1] * thrust for center, thrust in zip(rotor_center, yaw_step_thrust))
    pitch_arm_moment = sum(-center[0] * thrust for center, thrust in zip(rotor_center, yaw_step_thrust))
    assert abs(roll_arm_moment) > 0.0
    assert abs(pitch_arm_moment) > 0.0
