#!/usr/bin/env python3
"""Validate canonical ownership of ActuatorCommandMapper."""

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
    / "20260608_027_mosimquad_actuator_command_mapper_formal_source_surface"
)
PRIMARY_ANCHORS = [
    "input Real normalized_command[4]",
    "saturated_normalized_command[i] =",
    "actuator_saturation_error[i] = normalized_command[i] - saturated_normalized_command[i]",
    "visual_rotor_speed_unsigned[i] =",
    "signed_visual_rotor_speed_command[i] =",
    "hover_command_error[i] =",
]


def validate():
    return support.validate_component(
        formal_name="ActuatorCommandMapper",
        legacy_alias_name="ActuatorCommandMapper",
        legacy_file_name="Sunray150ActuatorCommandMapper.mo",
        legacy_file_model="Sunray150ActuatorCommandMapper",
        primary_anchors=PRIMARY_ANCHORS,
    )


def generate(output_dir: Path):
    return support.generate_component(
        output_dir=output_dir,
        title="ActuatorCommandMapper Canonical Source Ownership",
        output_basename="actuator_command_mapper_surface_check",
        formal_name="ActuatorCommandMapper",
        legacy_alias_name="ActuatorCommandMapper",
        legacy_file_name="Sunray150ActuatorCommandMapper.mo",
        legacy_file_model="Sunray150ActuatorCommandMapper",
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