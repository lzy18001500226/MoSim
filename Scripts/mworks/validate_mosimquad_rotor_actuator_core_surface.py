#!/usr/bin/env python3
"""Validate canonical ownership of RotorActuatorCore dynamics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosimquad_canonical_dynamics_surface as support


DEFAULT_OUTPUT_DIR = (
    support.ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260608_025_mosimquad_rotor_actuator_core_formal_source_surface"
)
PRIMARY_ANCHORS = [
    "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
    "thrust[i] = fault_effectiveness[i] * thrust_effectiveness[i] * nominal_thrust[i]",
    "yaw_reaction_moment[i] = fault_effectiveness[i] * yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust_effectiveness[i] * nominal_thrust[i]",
    "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
    "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
    "total_thrust = sum(thrust)",
    "minimum_thrust_effectiveness = min({fault_effectiveness[i] * thrust_effectiveness[i] for i in 1:4})",
    "minimum_reaction_moment_effectiveness = min({fault_effectiveness[i] * reaction_moment_effectiveness[i] for i in 1:4})",
]


def validate():
    return support.validate_component(
        formal_name="RotorActuatorCore",
        legacy_alias_name="RotorDynamicsCore",
        legacy_file_name="Sunray150RflyStyleRotorDynamics.mo",
        legacy_file_model="Sunray150RflyStyleRotorDynamics",
        primary_anchors=PRIMARY_ANCHORS,
    )


def generate(output_dir: Path):
    return support.generate_component(
        output_dir=output_dir,
        title="RotorActuatorCore Canonical Source Ownership",
        output_basename="rotor_actuator_core_surface_check",
        formal_name="RotorActuatorCore",
        legacy_alias_name="RotorDynamicsCore",
        legacy_file_name="Sunray150RflyStyleRotorDynamics.mo",
        legacy_file_model="Sunray150RflyStyleRotorDynamics",
        primary_anchors=PRIMARY_ANCHORS,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else support.ROOT / args.output_dir
    summary = generate(output_dir)
    print(summary)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
