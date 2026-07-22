#!/usr/bin/env python3
"""Validate canonical ownership of ActuatorMappedWrapperSurface."""

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
    / "20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface"
)
PRIMARY_ANCHORS = [
    "ActuatorCommandMapper actuator_mapper(",
    "WrapperSurface wrapper(",
    "input Real normalized_actuator_command[4]",
    "actuator_mapper.normalized_command = normalized_actuator_command",
    "wrapper.motor_command = actuator_mapper.signed_visual_rotor_speed_command",
    "signed_visual_rotor_speed_command = actuator_mapper.signed_visual_rotor_speed_command",
]


def validate():
    return support.validate_component(
        formal_name="ActuatorMappedWrapperSurface",
        legacy_alias_name="ActuatorMappedWrapperSurface",
        legacy_file_name="Sunray150ActuatorMappedWrapperSurface.mo",
        legacy_file_model="Sunray150ActuatorMappedWrapperSurface",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("command mapper", support.FORMAL_ROOT / "ActuatorCommandMapper.mo", ["model ActuatorCommandMapper", "signed_visual_rotor_speed_command[i] ="]),
            ("wrapper", support.FORMAL_ROOT / "WrapperSurface.mo", ["model WrapperSurface", "total_moment_body = dynamics.total_moment_body"]),
        ],
    )


def generate(output_dir: Path):
    return support.generate_component(
        output_dir=output_dir,
        title="ActuatorMappedWrapperSurface Canonical Source Ownership",
        output_basename="actuator_mapped_wrapper_surface_check",
        formal_name="ActuatorMappedWrapperSurface",
        legacy_alias_name="ActuatorMappedWrapperSurface",
        legacy_file_name="Sunray150ActuatorMappedWrapperSurface.mo",
        legacy_file_model="Sunray150ActuatorMappedWrapperSurface",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("command mapper", support.FORMAL_ROOT / "ActuatorCommandMapper.mo", ["model ActuatorCommandMapper", "signed_visual_rotor_speed_command[i] ="]),
            ("wrapper", support.FORMAL_ROOT / "WrapperSurface.mo", ["model WrapperSurface", "total_moment_body = dynamics.total_moment_body"]),
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