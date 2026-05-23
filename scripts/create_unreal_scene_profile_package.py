#!/usr/bin/env python3
"""Create metadata-only Unreal scene profile staging packages.

The package is a planning and review contract. It intentionally contains no
large meshes, textures, paks, binaries, or imported third-party assets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json"
DEFAULT_OUTPUT_ROOT = ROOT / "unreal/migration_staging"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def profile_by_id(profiles_doc: dict[str, Any], profile_id: str) -> dict[str, Any]:
    for profile in profiles_doc.get("profiles", []):
        if profile.get("profile_id") == profile_id:
            return profile
    raise KeyError(f"profile not found: {profile_id}")


def semantic_to_asset_type(visual_class: str) -> str:
    token = visual_class.lower()
    if "uav" in token:
        return "uav"
    if "propeller" in token:
        return "propeller"
    if "terrain" in token or "floor" in token or "grass" in token:
        return "terrain"
    if "wall" in token:
        return "wall"
    if "gate" in token:
        return "gate"
    if "ring" in token:
        return "ring"
    if "tree" in token:
        return "tree"
    if "building" in token:
        return "building"
    if "pillar" in token or "box" in token or "obstacle" in token:
        return "obstacle"
    if "camera" in token or "radar" in token or "plan" in token or "trail" in token or "overlay" in token:
        return "marker"
    return "marker"


def proxy_for_visual(profile: dict[str, Any], visual_class: str) -> str:
    proxy_classes = profile.get("truth_geometry", {}).get("required_proxy_classes", [])
    visual = visual_class.lower()
    if "takeoff_pad" in visual or "landing_pad" in visual or visual.endswith("pad"):
        return next((str(proxy) for proxy in proxy_classes if "pad" in str(proxy).lower()), "")
    if "box" in visual or "boxes" in visual:
        return next((str(proxy) for proxy in proxy_classes if "box_obstacle" in str(proxy).lower()), "")
    for proxy in proxy_classes:
        proxy_lower = str(proxy).lower()
        if "terrain" in visual and ("terrain" in proxy_lower or "plane" in proxy_lower):
            return str(proxy)
        if "floor" in visual and ("floor" in proxy_lower or "terrain" in proxy_lower or "plane" in proxy_lower):
            return str(proxy)
        if "pillar" in visual and "pillar" in proxy_lower:
            return str(proxy)
        if "box" in visual and "box" in proxy_lower:
            return str(proxy)
        if "wall" in visual and "wall" in proxy_lower:
            return str(proxy)
        if ("gate" in visual or "frame" in visual) and "gate" in proxy_lower:
            return str(proxy)
        if "ring" in visual and "ring" in proxy_lower:
            return str(proxy)
        if "target" in visual and "target" in proxy_lower:
            return str(proxy)
        if "building" in visual and "building" in proxy_lower:
            return str(proxy)
        if "tree" in visual and "tree" in proxy_lower:
            return str(proxy)
        if "rock" in visual and "rock" in proxy_lower:
            return str(proxy)
    return ""


def is_runtime_visual(visual_class: str) -> bool:
    token = visual_class.lower()
    runtime_tokens = (
        "uav",
        "propeller",
        "axis",
        "camera",
        "radar",
        "plan",
        "trail",
        "overlay",
        "marker",
        "reference",
        "formation",
        "role",
    )
    return any(item in token for item in runtime_tokens)


def default_bounds_for_proxy(proxy_class: str) -> dict[str, Any]:
    proxy = proxy_class.lower()
    if "terrain" in proxy or "plane" in proxy or "floor" in proxy:
        return {"center": [0.0, 0.0, -0.025], "size": [20.0, 20.0, 0.05]}
    if "pad" in proxy:
        return {"center": [0.0, 0.0, 0.02], "size": [1.0, 1.0, 0.04]}
    if "wall" in proxy:
        return {"center": [0.0, 0.0, 1.5], "size": [6.0, 0.25, 3.0]}
    if "gate" in proxy or "ring" in proxy:
        return {"center": [5.0, 0.0, 1.5], "size": [0.25, 3.0, 3.0]}
    if "pillar" in proxy or "column" in proxy:
        return {"center": [0.0, 0.0, 1.5], "size": [0.4, 0.4, 3.0]}
    if "building" in proxy:
        return {"center": [0.0, 0.0, 2.0], "size": [4.0, 4.0, 4.0]}
    return {"center": [0.0, 0.0, 0.5], "size": [1.0, 1.0, 1.0]}


def registry_from_profile(profiles_doc: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    profile_id = profile["profile_id"]
    visual_classes = profile.get("render_world", {}).get("required_visual_classes", [])
    assets: list[dict[str, Any]] = []
    proxies: dict[str, dict[str, Any]] = {}
    for visual_class in visual_classes:
        proxy_class = proxy_for_visual(profile, visual_class)
        render_only = is_runtime_visual(visual_class) or not proxy_class
        asset_id = f"{profile_id}_{visual_class}"
        proxy_id = f"proxy_{profile_id}_{proxy_class}" if proxy_class and not render_only else ""
        assets.append(
            {
                "asset_id": asset_id,
                "semantic_type": semantic_to_asset_type(visual_class),
                "source": {
                    "origin": "project_generated",
                    "source_path": DEFAULT_PROFILES.relative_to(ROOT).as_posix(),
                    "license_status": "project_owned",
                },
                "unreal": {
                    "asset_path": f"/Game/Quadrotor/Scenes/{profile_id}/{visual_class}",
                    "material_profile": "profile_stub",
                    "scale_m": [1.0, 1.0, 1.0],
                },
                "truth_binding": {
                    "geometry_id": f"{profile_id}_{proxy_class}" if proxy_class and not render_only else "",
                    "collision_proxy_id": proxy_id,
                    "render_only": render_only,
                },
            }
        )
        if proxy_id and proxy_id not in proxies:
            proxies[proxy_id] = {
                "collision_proxy_id": proxy_id,
                "geometry_type": "box",
                "frame": "mworks_world",
                "bounds_m": default_bounds_for_proxy(proxy_class),
                "safety_margin_m": 0.2,
                "source_asset_id": asset_id,
            }

    return {
        "schema": "quadrotor.scene_asset_registry.v1",
        "scene_id": profile_id,
        "map_id": profile.get("map_ids", [profile_id])[0],
        "coordinate_system": {
            "mworks_units": "meters",
            "unreal_units": "centimeters",
            "axis_policy": profiles_doc.get("coordinate_frame", {}).get("unreal_conversion", ""),
            "scale_status": "profile_stub_pending_blockout_review",
        },
        "source_profile": DEFAULT_PROFILES.relative_to(ROOT).as_posix(),
        "stage_id": profile.get("stage_id", ""),
        "planner_visibility": profile.get("truth_geometry", {}).get("planner_visibility", ""),
        "global_map_available_to_planner": profile.get("truth_geometry", {}).get("global_map_available_to_planner"),
        "assets": assets,
        "collision_proxies": list(proxies.values()),
        "acceptance": profile.get("acceptance", []),
    }


def write_readme(profile: dict[str, Any], package_dir: Path) -> None:
    profile_id = profile["profile_id"]
    package_arg = package_dir.relative_to(ROOT).as_posix()
    lines = [
        f"# Scene Profile Staging Package: {profile_id}",
        "",
        "This package is metadata-only. It is the review contract before UE scene",
        "blockout work starts. It must not contain large meshes, textures, paks,",
        "engine binaries, or imported third-party assets.",
        "",
        "## Review Focus",
        "",
        f"- Stage: `{profile.get('stage_id', '')}`",
        f"- Purpose: {profile.get('purpose', '')}",
        f"- Planner visibility: `{profile.get('truth_geometry', {}).get('planner_visibility', '')}`",
        f"- Global map available to planner: `{profile.get('truth_geometry', {}).get('global_map_available_to_planner')}`",
        "",
        "## Validation",
        "",
        "```bash",
        f"python3 scripts/check_unreal_migration_package.py --package-dir {package_arg}",
        "```",
        "",
        "Replace placeholder bounds and asset paths only after the blockout is",
        "measured in Unreal and reviewed.",
    ]
    (package_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--profile-id", required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    profiles_doc = load_json(args.profiles)
    profile = profile_by_id(profiles_doc, args.profile_id)
    package_dir = args.output_root / args.profile_id
    package_dir.mkdir(parents=True, exist_ok=True)
    registry = registry_from_profile(profiles_doc, profile)
    (package_dir / "scene_asset_registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_readme(profile, package_dir)
    print(f"[OK] wrote {package_dir / 'scene_asset_registry.json'}")
    print(f"[OK] wrote {package_dir / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
