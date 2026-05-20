#!/usr/bin/env python3
"""Create a project-local migration package stub for a planned Unreal scene.

The stub contains metadata only. It is used to prepare the registry/proxy
contract before any large UE assets are migrated from a temporary project.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "results" / "rflysim" / "rflysim_vision_ring_migration_plan.json"
DEFAULT_OUTPUT_ROOT = ROOT / "unreal" / "migration_staging"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def registry_from_plan(plan: dict) -> dict:
    scene_id = plan["scene_id"]
    return {
        "schema": "quadrotor.scene_asset_registry.v1",
        "scene_id": f"{scene_id}_probe",
        "map_id": scene_id,
        "coordinate_system": {
            "mworks_units": "meters",
            "unreal_units": "centimeters",
            "axis_policy": "MWORKS X/Z kept, MWORKS Y sign inverted in Unreal unless measured scene profile overrides",
            "scale_status": "pending_manual_measurement",
        },
        "assets": [
            {
                "asset_id": f"{scene_id}_floor_reference",
                "semantic_type": "terrain",
                "source": {
                    "origin": "rflysim_migrated",
                    "source_path": plan["source_map"],
                    "license_status": "pending_review",
                },
                "unreal": {
                    "asset_path": f"/Game/Quadrotor/Migrated/{scene_id}/FloorReference",
                    "material_profile": "pending_migration",
                    "scale_m": [1.0, 1.0, 1.0],
                },
                "truth_binding": {
                    "geometry_id": f"{scene_id}_floor_reference",
                    "collision_proxy_id": f"proxy_{scene_id}_floor_reference",
                    "render_only": False,
                },
            },
            {
                "asset_id": f"{scene_id}_ring_gate_reference",
                "semantic_type": "ring",
                "source": {
                    "origin": "rflysim_migrated",
                    "source_path": plan["reference_sample"][0] if plan.get("reference_sample") else plan["source_map"],
                    "license_status": "pending_review",
                },
                "unreal": {
                    "asset_path": f"/Game/Quadrotor/Migrated/{scene_id}/RingGateReference",
                    "material_profile": "pending_migration",
                    "scale_m": [1.0, 1.0, 1.0],
                },
                "truth_binding": {
                    "geometry_id": f"{scene_id}_ring_gate_reference",
                    "collision_proxy_id": f"proxy_{scene_id}_ring_gate_reference",
                    "render_only": False,
                },
            },
        ],
        "collision_proxies": [
            {
                "collision_proxy_id": f"proxy_{scene_id}_floor_reference",
                "geometry_type": "box",
                "frame": "mworks_world",
                "bounds_m": {
                    "center": [0.0, 0.0, -0.025],
                    "size": [20.0, 20.0, 0.05],
                },
                "safety_margin_m": 0.0,
                "source_asset_id": f"{scene_id}_floor_reference",
            },
            {
                "collision_proxy_id": f"proxy_{scene_id}_ring_gate_reference",
                "geometry_type": "box",
                "frame": "mworks_world",
                "bounds_m": {
                    "center": [5.0, 0.0, 1.5],
                    "size": [0.25, 3.0, 3.0],
                },
                "safety_margin_m": 0.25,
                "source_asset_id": f"{scene_id}_ring_gate_reference",
            },
        ],
    }


def write_readme(plan: dict, package_dir: Path) -> None:
    lines = [
        f"# Migration Staging Package: {plan['scene_id']}",
        "",
        "This directory is a metadata-only staging package. It intentionally does",
        "not contain migrated RflySim assets yet.",
        "",
        "## Use",
        "",
        "1. Complete the temporary UE migration/manual review checklist.",
        "2. Replace placeholder `asset_path`, `source_path`, materials, scale, and",
        "   collision proxy bounds with measured values.",
        "3. Run:",
        "",
        "```bash",
        f"python3 scripts/check_unreal_migration_package.py --package-dir {package_dir.as_posix()}",
        "```",
        "",
        "Do not copy `.pak`, engine binaries, installers, or files over 100 MB into",
        "this package.",
    ]
    (package_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    plan = load_json(args.plan)
    package_dir = args.output_root / plan["scene_id"]
    package_dir.mkdir(parents=True, exist_ok=True)

    registry = registry_from_plan(plan)
    (package_dir / "scene_asset_registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_readme(plan, package_dir)
    print(f"[OK] wrote {package_dir / 'scene_asset_registry.json'}")
    print(f"[OK] wrote {package_dir / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
