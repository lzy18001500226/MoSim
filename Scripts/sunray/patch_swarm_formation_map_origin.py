#!/usr/bin/env python3
"""Patch a copied Swarm-Formation runtime workspace with optional map origin."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OLD_PARAMETERS = """  node_.param("grid_map/map_size_x", x_size, -1.0);
  node_.param("grid_map/map_size_y", y_size, -1.0);
  node_.param("grid_map/map_size_z", z_size, -1.0);
"""

NEW_PARAMETERS = """  node_.param("grid_map/map_size_x", x_size, -1.0);
  node_.param("grid_map/map_size_y", y_size, -1.0);
  node_.param("grid_map/map_size_z", z_size, -1.0);
  bool use_map_origin_override;
  double map_origin_x, map_origin_y;
  node_.param("grid_map/use_map_origin_override", use_map_origin_override, false);
  node_.param("grid_map/map_origin_x", map_origin_x, -x_size / 2.0);
  node_.param("grid_map/map_origin_y", map_origin_y, -y_size / 2.0);
"""

OLD_ORIGIN = "  mp_.map_origin_ = Eigen::Vector3d(-x_size / 2.0, -y_size / 2.0, mp_.ground_height_);\n"

NEW_ORIGIN = """  if (use_map_origin_override)
  {
    mp_.map_origin_ = Eigen::Vector3d(map_origin_x, map_origin_y, mp_.ground_height_);
  }
  else
  {
    mp_.map_origin_ = Eigen::Vector3d(-x_size / 2.0, -y_size / 2.0, mp_.ground_height_);
  }
"""


def is_reference_source(source: Path) -> bool:
    project_root = Path(__file__).resolve().parents[2]
    references_root = project_root / "References"
    try:
        source.relative_to(references_root)
    except ValueError:
        return False
    return True


def patch_source(source: Path) -> dict[str, object]:
    if is_reference_source(source):
        raise RuntimeError(f"refusing to patch authoritative reference source: {source}")

    original = source.read_text(encoding="utf-8")
    new_parameter_blocks = original.count(NEW_PARAMETERS)
    new_origin_blocks = original.count(NEW_ORIGIN)
    origin_override_conditions = original.count("if (use_map_origin_override)")

    # NEW_ORIGIN deliberately contains the legacy centered assignment in its
    # fallback branch. Check the complete patched structure before looking for
    # the old fragment, otherwise a second invocation nests the conditional.
    if new_parameter_blocks or new_origin_blocks or origin_override_conditions:
        if (
            new_parameter_blocks == 1
            and new_origin_blocks == 1
            and origin_override_conditions == 1
        ):
            return {
                "status": "already_patched",
                "source": str(source),
                "parameter_replacements": 0,
                "origin_replacements": 0,
                "fallback_origin": "centered_at_world_origin_when_override_disabled",
            }
        raise RuntimeError(
            "noncanonical optional map-origin patch state in "
            f"{source}: parameters={new_parameter_blocks}, origins={new_origin_blocks}, "
            f"conditions={origin_override_conditions}"
        )

    parameter_replacements = original.count(OLD_PARAMETERS)
    origin_replacements = original.count(OLD_ORIGIN)
    if parameter_replacements != 1:
        raise RuntimeError(
            f"expected one map-size parameter block in {source}, found {parameter_replacements}"
        )
    if origin_replacements != 1:
        raise RuntimeError(f"expected one map-origin assignment in {source}, found {origin_replacements}")

    patched = original.replace(OLD_PARAMETERS, NEW_PARAMETERS).replace(OLD_ORIGIN, NEW_ORIGIN)
    if (
        patched.count(NEW_PARAMETERS) != 1
        or patched.count(NEW_ORIGIN) != 1
        or patched.count("if (use_map_origin_override)") != 1
    ):
        raise RuntimeError(f"optional map-origin patch is missing from {source}")

    source.write_text(patched, encoding="utf-8")

    return {
        "status": "patched",
        "source": str(source),
        "parameter_replacements": parameter_replacements,
        "origin_replacements": origin_replacements,
        "fallback_origin": "centered_at_world_origin_when_override_disabled",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.is_file():
        raise SystemExit(f"source missing: {source}")
    print(json.dumps(patch_source(source), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())