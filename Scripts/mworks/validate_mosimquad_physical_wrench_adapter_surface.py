#!/usr/bin/env python3
"""Validate canonical ownership of PhysicalWrenchAdapter."""

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
    / "20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface"
)
PRIMARY_ANCHORS = [
    "inner Modelica.Mechanics.MultiBody.World world(",
    "WrapperSurface wrapper;",
    "Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque forceAndTorque(",
    "applied_force_body = {0, 0, wrapper.total_thrust}",
    "applied_torque_body = wrapper.total_moment_body",
    "forceAndTorque.force = applied_force_body",
    "forceAndTorque.torque = applied_torque_body",
    "connect(forceAndTorque.frame_b, body.frame_a)",
]


def validate():
    return support.validate_component(
        formal_name="PhysicalWrenchAdapter",
        legacy_alias_name="PhysicalWrenchAdapter",
        legacy_file_name="Sunray150PhysicalWrenchFrameAdapter.mo",
        legacy_file_model="Sunray150PhysicalWrenchFrameAdapter",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("wrapper", support.FORMAL_ROOT / "WrapperSurface.mo", ["model WrapperSurface", "motor_order_gate_error ="]),
        ],
    )


def generate(output_dir: Path):
    return support.generate_component(
        output_dir=output_dir,
        title="PhysicalWrenchAdapter Canonical Source Ownership",
        output_basename="physical_wrench_adapter_surface_check",
        formal_name="PhysicalWrenchAdapter",
        legacy_alias_name="PhysicalWrenchAdapter",
        legacy_file_name="Sunray150PhysicalWrenchFrameAdapter.mo",
        legacy_file_model="Sunray150PhysicalWrenchFrameAdapter",
        primary_anchors=PRIMARY_ANCHORS,
        related_sources=[
            ("wrapper", support.FORMAL_ROOT / "WrapperSurface.mo", ["model WrapperSurface", "motor_order_gate_error ="]),
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