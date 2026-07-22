#!/usr/bin/env python3
"""Validate canonical ownership of WrapperSurface dynamics."""

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
    / "20260608_026_mosimquad_wrapper_surface_formal_source_surface"
)
PRIMARY_ANCHORS = [
    "RotorActuatorCore dynamics;",
    "dynamics.motor_command = motor_command",
    "commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
    "commanded_total_moment_body[3]",
    "motor_order_gate_error =",
    "yaw_direction_gate_error =",
]


def validate():
    return support.validate_component(
        formal_name="WrapperSurface",
        legacy_alias_name="WrapperSurface",
        legacy_file_name="Sunray150DynamicsWrapperSurface.mo",
        legacy_file_model="Sunray150DynamicsWrapperSurface",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("rotor core", support.FORMAL_ROOT / "RotorActuatorCore.mo", ["model RotorActuatorCore", "total_moment_body[3]"]),
        ],
    )


def generate(output_dir: Path):
    return support.generate_component(
        output_dir=output_dir,
        title="WrapperSurface Canonical Source Ownership",
        output_basename="wrapper_surface_check",
        formal_name="WrapperSurface",
        legacy_alias_name="WrapperSurface",
        legacy_file_name="Sunray150DynamicsWrapperSurface.mo",
        legacy_file_model="Sunray150DynamicsWrapperSurface",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("rotor core", support.FORMAL_ROOT / "RotorActuatorCore.mo", ["model RotorActuatorCore", "total_moment_body[3]"]),
        ],
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