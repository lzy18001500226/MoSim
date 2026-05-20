#!/usr/bin/env python3
"""Build a small UE5 scene registry from the local RflySim map audit.

The registry is project-owned metadata. It does not copy RflySim assets and it
does not read the external RflySim installation. Run scripts/audit_rflysim_maps.py
first when the local RflySim install changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "results" / "rflysim" / "rflysim_map_audit.json"
DEFAULT_OUTPUT = (
    ROOT
    / "unreal"
    / "MworksUnrealRenderer"
    / "Content"
    / "MworksData"
    / "rflysim_scene_registry.json"
)

TARGET_SCENES = [
    {
        "scene_id": "rflysim_vision_ring",
        "relative_path": "Vision/Maps/VisionRing.umap",
        "priority": "P0",
        "purpose": "ring/gate and high-attitude-control visual demo",
    },
    {
        "scene_id": "rflysim_vision_ring_blank",
        "relative_path": "Vision/Maps/VisionRingBlank.umap",
        "priority": "P0",
        "purpose": "clean ring/gate scene for controller-focused video",
    },
    {
        "scene_id": "rflysim_grasslands_3d_display",
        "relative_path": "Grasslands/Maps/Grasslands/3DDisplay.umap",
        "priority": "P0",
        "purpose": "open wind, motor-efficiency, and long-range trajectory scene",
    },
    {
        "scene_id": "rflysim_grasslands",
        "relative_path": "Grasslands/Maps/Grasslands/Grasslands.umap",
        "priority": "P0",
        "purpose": "open terrain scene and reusable landscape material source",
    },
    {
        "scene_id": "rflysim_old_factory",
        "relative_path": "OldFactory/Maps/OldFactory.umap",
        "priority": "P0",
        "purpose": "industrial patrol, wall occlusion, and obstacle navigation",
    },
    {
        "scene_id": "rflysim_neighborhood_park",
        "relative_path": "ModularNeighborhood/Maps/NeighborhoodPark.umap",
        "priority": "P0",
        "purpose": "park patrol with trees, roads, buildings, and low-altitude routing",
    },
    {
        "scene_id": "rflysim_challenge_map",
        "relative_path": "RobotMissionChallenge/Map/ChallengeMap.umap",
        "priority": "P1",
        "purpose": "maze-like challenge scene for local planning stress tests",
    },
    {
        "scene_id": "rflysim_mountain_terrain",
        "relative_path": "MountainTerrain/Maps/MountainTerrain.umap",
        "priority": "P1",
        "purpose": "terrain following and outdoor altitude-hold visual review",
    },
    {
        "scene_id": "rflysim_exhibition_hall",
        "relative_path": "ExhibitionHall/Maps/ExhibitionHall.umap",
        "priority": "P1",
        "purpose": "indoor assets, props, towers, and structured-object sources",
    },
]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing audit file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def collect_direct_editor_blockers(audit: dict) -> list[str]:
    blockers: list[str] = []
    for item in audit.get("project_module_status", []):
        module = item.get("module", "<unknown>")
        if not item.get("has_source_build_cs") and not item.get("has_win64_dll"):
            blockers.append(f"project module {module} has no Source Build.cs and no Win64 editor DLL")

    for plugin in audit.get("plugin_status", []):
        missing_modules = [
            module.get("module", "<unknown>")
            for module in plugin.get("modules", [])
            if not module.get("has_source_build_cs") and not module.get("has_win64_dll")
        ]
        if missing_modules:
            blockers.append(
                f"plugin {plugin.get('plugin', '<unknown>')} missing source/DLL for modules: "
                + ", ".join(missing_modules)
            )
    return blockers


def build_registry(audit: dict) -> dict:
    maps_by_path = {item["relative_path"]: item for item in audit.get("maps", [])}
    direct_editor_blockers = collect_direct_editor_blockers(audit)
    scenes = []
    for target in TARGET_SCENES:
        audit_item = maps_by_path.get(target["relative_path"], {})
        scenes.append(
            {
                **target,
                "source_engine_association": audit.get("engine_association"),
                "target_engine_association": "5.7",
                "source_project": audit.get("rflysim_project"),
                "direct_use_supported": False,
                "direct_editor_open_supported": not direct_editor_blockers,
                "direct_editor_blocker_count": len(direct_editor_blockers),
                "migration_status": "audit_only",
                "asset_import_status": "pending",
                "collision_proxy_status": "pending",
                "map_size_bytes": audit_item.get("size_bytes"),
                "reference_sample": audit_item.get("reference_sample", [])[:8],
                "notes": (
                    "RflySim UE4.27 .umap/.uasset dependency source. "
                    "Migrate through a temporary UE project and derive project-owned "
                    "UE5 assets/collision proxies before using in final playback."
                ),
            }
        )

    return {
        "schema": "quadrotor.rflysim_scene_registry.v1",
        "source_audit": "results/rflysim/rflysim_map_audit.json",
        "source_project": audit.get("rflysim_project"),
        "source_engine_association": audit.get("engine_association"),
        "target_engine_association": "5.7",
        "direct_use_supported": False,
        "direct_editor_open_supported": not direct_editor_blockers,
        "direct_editor_open_blockers": direct_editor_blockers,
        "direct_use_reason": audit.get("direct_use_conclusion"),
        "editor_source_conclusion": audit.get("editor_source_conclusion"),
        "enabled_plugin_sample": audit.get("enabled_plugins", []),
        "project_module_status": audit.get("project_module_status", []),
        "plugin_status": audit.get("plugin_status", []),
        "recommended_migration_order": [scene["scene_id"] for scene in scenes],
        "scenes": scenes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    registry = build_registry(load_json(args.audit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] wrote {args.output}")
    print(f"[OK] scenes: {len(registry['scenes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
