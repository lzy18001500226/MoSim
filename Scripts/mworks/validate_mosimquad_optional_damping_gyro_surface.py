#!/usr/bin/env python3
"""Validate canonical ownership of OptionalDampingGyroLayer."""

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
    / "20260609_026_mosimquad_optional_damping_gyro_formal_source_surface"
)
PRIMARY_ANCHORS = [
    "parameter Boolean enable_rotor_gyro = false",
    "parameter Boolean enable_body_drag = false",
    "parameter Boolean enable_angular_damping = false",
    "ActuatorMappedWrapperSurface mapped_wrapper;",
    "optional_force_body[j] = body_drag_force_body[j]",
    "default_disabled_force_delta =",
    "default_disabled_moment_delta =",
]


def validate():
    return support.validate_component(
        formal_name="OptionalDampingGyroLayer",
        legacy_alias_name="OptionalDampingGyroLayer",
        legacy_file_name="Sunray150OptionalDampingGyroLayer.mo",
        legacy_file_model="Sunray150OptionalDampingGyroLayer",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("mapped wrapper", support.FORMAL_ROOT / "ActuatorMappedWrapperSurface.mo", ["model ActuatorMappedWrapperSurface", "total_moment_body = wrapper.total_moment_body"]),
        ],
    )


def generate(output_dir: Path):
    return support.generate_component(
        output_dir=output_dir,
        title="OptionalDampingGyroLayer Canonical Source Ownership",
        output_basename="optional_damping_gyro_surface_check",
        formal_name="OptionalDampingGyroLayer",
        legacy_alias_name="OptionalDampingGyroLayer",
        legacy_file_name="Sunray150OptionalDampingGyroLayer.mo",
        legacy_file_model="Sunray150OptionalDampingGyroLayer",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("mapped wrapper", support.FORMAL_ROOT / "ActuatorMappedWrapperSurface.mo", ["model ActuatorMappedWrapperSurface", "total_moment_body = wrapper.total_moment_body"]),
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