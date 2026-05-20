#!/usr/bin/env python3
"""Generate an implementation plan from project-owned Unreal scene profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json"
DEFAULT_RFLYSIM_REGISTRY = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/rflysim_scene_registry.json"
DEFAULT_JSON = ROOT / "results/unreal/unreal_scene_profile_implementation_plan.json"
DEFAULT_MD = ROOT / "results/unreal/unreal_scene_profile_implementation_plan.md"

PROFILE_RFLYSIM_REFERENCES = {
    "dense_forest": ["rflysim_neighborhood_park", "rflysim_mountain_terrain"],
    "maze_building": ["rflysim_challenge_map", "rflysim_old_factory"],
    "old_factory": ["rflysim_old_factory"],
    "gate_ring_indoor": ["rflysim_vision_ring", "rflysim_vision_ring_blank"],
    "open_grass_wind": ["rflysim_grasslands_3d_display", "rflysim_grasslands"],
}

PROFILE_PROXY_BINDINGS = {
    "dense_forest": {
        "terrain": "terrain_heightfield",
        "tree_trunks": "tree_trunk_capsule_or_box",
        "rocks": "rock_box",
    },
    "maze_building": {
        "walls": "wall_box",
        "doors_or_passages": "passage_box",
        "floor": "floor_plane",
    },
    "old_factory": {
        "buildings": "building_box",
        "pipes": "pipe_capsule",
        "columns": "column_box",
        "inspection_targets": "target_marker",
    },
    "gate_ring_indoor": {
        "tilted_gate": "gate_frame_boxes",
        "ring": "ring_proxy",
        "indoor_floor": "safe_corridor",
    },
    "open_grass_wind": {
        "grass_field": "terrain_plane",
        "gust_zone": "optional_boundary",
    },
}

RUNTIME_VISUAL_CLASSES = {
    "actual_trail",
    "local_known_map",
    "local_plan",
    "metric_overlay",
    "radar_sector",
    "smooth_reference",
    "trail",
    "trajectory_trail",
    "UAV",
    "waypoint_markers",
    "wind_vector_overlay",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_json(path)


def matched_rflysim_scenes(profile_id: str, registry: dict[str, Any]) -> list[dict[str, Any]]:
    scene_by_id = {scene.get("scene_id"): scene for scene in registry.get("scenes", [])}
    matched = []
    for scene_id in PROFILE_RFLYSIM_REFERENCES.get(profile_id, []):
        scene = scene_by_id.get(scene_id)
        if not scene:
            continue
        matched.append(
            {
                "scene_id": scene_id,
                "priority": scene.get("priority"),
                "source_map": scene.get("relative_path"),
                "purpose": scene.get("purpose"),
                "direct_use_supported": scene.get("direct_use_supported"),
                "direct_editor_open_supported": scene.get("direct_editor_open_supported"),
                "migration_status": scene.get("migration_status"),
            }
        )
    return matched


def reconstruction_units(profile: dict[str, Any]) -> list[dict[str, Any]]:
    profile_id = profile.get("profile_id", "")
    visual_classes = profile.get("render_world", {}).get("required_visual_classes", [])
    proxy_bindings = PROFILE_PROXY_BINDINGS.get(profile_id, {})
    units = []
    for visual_class in visual_classes:
        proxy_class = proxy_bindings.get(visual_class, "")
        if visual_class in RUNTIME_VISUAL_CLASSES:
            source = "bridge_runtime_visual"
            action = "render from MWORKS UDP/replay packet; not a static scene asset"
        elif proxy_class:
            source = "project_owned_geometry"
            action = "create visible asset and bind to matching collision/world_geometry proxy"
        else:
            source = "project_owned_visual_only"
            action = "create visual asset; mark render_only unless later linked to a proxy"
        units.append(
            {
                "visual_class": visual_class,
                "proxy_class": proxy_class,
                "source": source,
                "action": action,
            }
        )
    return units


def profile_plan(profile: dict[str, Any], index: int, registry: dict[str, Any]) -> dict[str, Any]:
    render_world = profile.get("render_world", {})
    truth_geometry = profile.get("truth_geometry", {})
    return {
        "order": index,
        "profile_id": profile["profile_id"],
        "priority": profile.get("priority", "P1"),
        "purpose": profile.get("purpose", ""),
        "source_strategy": render_world.get("source_strategy", ""),
        "required_visual_classes": render_world.get("required_visual_classes", []),
        "required_proxy_classes": truth_geometry.get("required_proxy_classes", []),
        "planner_visibility": truth_geometry.get("planner_visibility", ""),
        "global_map_available_to_planner": truth_geometry.get("global_map_available_to_planner"),
        "rflysim_reference_scenes": matched_rflysim_scenes(profile["profile_id"], registry),
        "reconstruction_units": reconstruction_units(profile),
        "implementation_steps": [
            "create or select authorized visual assets",
            "use RflySim runtime only as visual/layout reference unless direct_editor_open_supported is later verified true",
            "write scene_asset_registry entry with source and license note",
            "create matching world_geometry/collision proxies",
            "add scenario profile and planner visibility rule",
            "run Unreal bridge checks",
            "run short MWORKS playback or dry-run stream",
            "perform manual viewport/video review",
        ],
        "acceptance": profile.get("acceptance", []),
    }


def build_plan(profiles_doc: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    profiles = profiles_doc.get("profiles", [])
    ordered = sorted(
        profiles,
        key=lambda item: (
            {"P0": 0, "P1": 1, "P2": 2}.get(item.get("priority", "P1"), 9),
            item.get("profile_id", ""),
        ),
    )
    return {
        "schema": "quadrotor.unreal_scene_profile_implementation_plan.v1",
        "source_profiles": str(DEFAULT_PROFILES.relative_to(ROOT)),
        "truth_policy": profiles_doc.get("truth_policy", ""),
        "coordinate_frame": profiles_doc.get("coordinate_frame", {}),
        "runtime_targets": profiles_doc.get("runtime_targets", {}),
        "rflysim_registry": str(DEFAULT_RFLYSIM_REGISTRY.relative_to(ROOT)),
        "rflysim_direct_use_supported": registry.get("direct_use_supported"),
        "rflysim_direct_editor_open_supported": registry.get("direct_editor_open_supported"),
        "profile_count": len(ordered),
        "profiles": [profile_plan(profile, index, registry) for index, profile in enumerate(ordered, start=1)],
        "next_recommended_task": (
            "Implement gate_ring_indoor first if the goal is attitude-control video; "
            "implement maze_building first if the goal is local perception and replanning."
        ),
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    lines = [
        "# Unreal Scene Profile Implementation Plan",
        "",
        f"- Source profiles: `{plan['source_profiles']}`",
        f"- RflySim registry: `{plan['rflysim_registry']}`",
        f"- RflySim direct use supported: `{plan['rflysim_direct_use_supported']}`",
        f"- RflySim direct editor open supported: `{plan['rflysim_direct_editor_open_supported']}`",
        f"- Profile count: `{plan['profile_count']}`",
        f"- Next recommended task: {plan['next_recommended_task']}",
        "",
        "## Runtime Targets",
        "",
    ]
    for key, value in plan.get("runtime_targets", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines += [
        "",
        "## Profiles",
        "",
        "| Order | Profile | Priority | Planner visibility | Visual classes | Proxy classes |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for profile in plan["profiles"]:
        visual = ", ".join(f"`{item}`" for item in profile["required_visual_classes"])
        proxies = ", ".join(f"`{item}`" for item in profile["required_proxy_classes"])
        lines.append(
            f"| {profile['order']} | `{profile['profile_id']}` | {profile['priority']} | "
            f"`{profile['planner_visibility']}` | {visual} | {proxies} |"
        )
    lines += ["", "## Acceptance Gates", ""]
    for profile in plan["profiles"]:
        lines.append(f"### `{profile['profile_id']}`")
        lines.append("")
        if profile.get("rflysim_reference_scenes"):
            lines.append("RflySim runtime references:")
            lines.append("")
            for scene in profile["rflysim_reference_scenes"]:
                lines.append(
                    f"- `{scene['scene_id']}` -> `{scene['source_map']}` "
                    f"(direct_use={scene['direct_use_supported']}, editor_open={scene['direct_editor_open_supported']})"
                )
            lines.append("")
        lines.append("Reconstruction units:")
        lines.append("")
        lines.append("| Visual class | Proxy class | Source | Action |")
        lines.append("| --- | --- | --- | --- |")
        for unit in profile["reconstruction_units"]:
            lines.append(
                f"| `{unit['visual_class']}` | `{unit['proxy_class']}` | "
                f"`{unit['source']}` | {unit['action']} |"
            )
        lines.append("")
        lines.append("Acceptance:")
        lines.append("")
        for item in profile["acceptance"]:
            lines.append(f"- {item}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--rflysim-registry", type=Path, default=DEFAULT_RFLYSIM_REGISTRY)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-output", type=Path, default=DEFAULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profiles_doc = load_json(args.profiles)
    registry = load_json_optional(args.rflysim_registry)
    plan = build_plan(profiles_doc, registry)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, args.md_output)
    print(f"[OK] wrote {args.json_output}")
    print(f"[OK] wrote {args.md_output}")
    print(plan["next_recommended_task"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
