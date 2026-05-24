#!/usr/bin/env python3
"""Export or validate MoSim planning truth from an editable Unreal scene.

Run ``export`` inside Unreal Editor Python. Run ``validate`` with normal Python.
The exported truth is an explicit collision proxy artifact; it is separate from
visual assets and can be consumed by planners, mappers, and review scripts.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "UE5/MworksUnrealRenderer/Content/MworksData/scene_truth"
SCHEMA = "mosim.unreal_scene_truth.v1"
UNREAL_CM_PER_M = 100.0
SEMANTIC_KEYWORDS = {
    "terrain": ("terrain", "landscape", "ground", "floor", "road"),
    "tree": ("tree", "forest", "trunk", "branch", "foliage"),
    "building": ("building", "factory", "warehouse", "house", "wall", "corridor", "room"),
    "wall": ("wall", "fence", "barrier"),
    "gate": ("gate", "ring", "frame", "window"),
    "obstacle": ("obstacle", "prop", "rock", "crate", "box", "pillar", "column"),
    "sensor": ("lidar", "radar", "camera", "sensor"),
    "marker": ("marker", "start", "goal", "target"),
}


def slug(value: str, fallback: str = "item") -> str:
    text = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_").lower()
    return text or fallback


def rounded(value: float, digits: int = 5) -> float:
    return round(float(value), digits)


def cm_to_m(value: float) -> float:
    return float(value) / UNREAL_CM_PER_M


def unreal_vector_to_mworks_m(vector: Any) -> list[float]:
    """Convert Unreal cm XYZ to project MWORKS m XYZ.

    Current MoSim renderer convention keeps X/Z and flips Y when converting
    between MWORKS and Unreal.
    """
    return [rounded(cm_to_m(vector.x)), rounded(-cm_to_m(vector.y)), rounded(cm_to_m(vector.z))]


def unreal_extent_to_size_m(extent: Any) -> list[float]:
    """Convert Unreal box half-extents in cm to full box size in meters."""
    return [
        rounded(2.0 * cm_to_m(abs(extent.x))),
        rounded(2.0 * cm_to_m(abs(extent.y))),
        rounded(2.0 * cm_to_m(abs(extent.z))),
    ]


def min_max_from_center_size(center_m: list[float], size_m: list[float]) -> tuple[list[float], list[float]]:
    min_m = [rounded(center_m[i] - 0.5 * size_m[i]) for i in range(3)]
    max_m = [rounded(center_m[i] + 0.5 * size_m[i]) for i in range(3)]
    return min_m, max_m


def infer_semantic(*parts: str) -> str:
    text = " ".join(part.lower() for part in parts if part)
    for semantic, keywords in SEMANTIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return semantic
    return "obstacle"


def build_payload(
    *,
    scene_id: str,
    map_id: str,
    project_path: str,
    level_name: str,
    assets: list[dict[str, Any]],
    collision_proxies: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scene_id": scene_id,
        "map_id": map_id,
        "source": {
            "exporter": "Scripts/UE5/export_unreal_scene_truth.py",
            "project_path": project_path,
            "level_name": level_name,
            "truth_method": "component_world_aabb_collision_proxy_v1",
        },
        "coordinate_system": {
            "unreal_units": "centimeters",
            "mworks_units": "meters",
            "axis_policy": "mworks_x=unreal_x, mworks_y=-unreal_y, mworks_z=unreal_z",
            "frame": "mworks_world",
        },
        "assets": assets,
        "collision_proxies": collision_proxies,
    }


def validate_truth_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    for field in ("scene_id", "map_id", "coordinate_system", "assets", "collision_proxies"):
        if field not in payload:
            errors.append(f"missing top-level field: {field}")
    if not isinstance(payload.get("assets", []), list):
        errors.append("assets must be a list")
    proxies = payload.get("collision_proxies", [])
    if not isinstance(proxies, list):
        errors.append("collision_proxies must be a list")
        return errors
    if not proxies:
        errors.append("collision_proxies must not be empty")
    seen_ids: set[str] = set()
    for index, proxy in enumerate(proxies):
        if not isinstance(proxy, dict):
            errors.append(f"collision_proxies[{index}] must be an object")
            continue
        proxy_id = str(proxy.get("collision_proxy_id", ""))
        if not proxy_id:
            errors.append(f"collision_proxies[{index}] missing collision_proxy_id")
        elif proxy_id in seen_ids:
            errors.append(f"duplicate collision_proxy_id: {proxy_id}")
        seen_ids.add(proxy_id)
        if proxy.get("geometry_type") != "box":
            errors.append(f"{proxy_id or index}: geometry_type must be box")
        for field in ("center_m", "size_m", "min_m", "max_m"):
            value = proxy.get(field)
            if not (isinstance(value, list) and len(value) == 3 and all(isinstance(v, (int, float)) for v in value)):
                errors.append(f"{proxy_id or index}: {field} must be a numeric length-3 list")
    return errors


def export_from_unreal(scene_id: str, map_id: str, output: Path, include_no_collision: bool = False) -> dict[str, Any]:
    try:
        import unreal  # type: ignore
    except ImportError as exc:
        raise RuntimeError("The export command must run inside Unreal Editor Python.") from exc

    world = unreal.EditorLevelLibrary.get_editor_world()
    level_name = world.get_map_name() if world else ""
    project_path = unreal.Paths.project_dir()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    assets: list[dict[str, Any]] = []
    proxies: list[dict[str, Any]] = []

    for actor in actors:
        actor_label = actor.get_actor_label()
        actor_name = actor.get_name()
        tags = [str(tag) for tag in getattr(actor, "tags", [])]
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        for component in components:
            try:
                collision_enabled = str(component.get_collision_enabled())
            except Exception:
                collision_enabled = str(component.get_editor_property("collision_enabled"))
            if (not include_no_collision) and "NO_COLLISION" in collision_enabled.upper():
                continue
            mesh = component.static_mesh
            mesh_path = mesh.get_path_name() if mesh else ""
            origin, extent, _ = component.get_component_bounds()
            center_m = unreal_vector_to_mworks_m(origin)
            size_m = unreal_extent_to_size_m(extent)
            if min(size_m) <= 0.0:
                continue
            min_m, max_m = min_max_from_center_size(center_m, size_m)
            component_name = component.get_name()
            semantic = infer_semantic(actor_label, actor_name, component_name, mesh_path, " ".join(tags))
            index = len(proxies) + 1
            base_id = slug(f"{semantic}_{actor_label}_{component_name}", fallback=f"proxy_{index:05d}")
            collision_proxy_id = f"{map_id}_{index:05d}_{base_id}"
            asset_id = f"asset_{collision_proxy_id}"
            proxies.append(
                {
                    "collision_proxy_id": collision_proxy_id,
                    "geometry_type": "box",
                    "semantic_type": semantic,
                    "frame": "mworks_world",
                    "center_m": center_m,
                    "size_m": size_m,
                    "min_m": min_m,
                    "max_m": max_m,
                    "source_asset_id": asset_id,
                    "source_actor": actor_label,
                    "source_component": component_name,
                    "source_mesh": mesh_path,
                    "collision_enabled": collision_enabled,
                }
            )
            assets.append(
                {
                    "asset_id": asset_id,
                    "semantic_type": semantic,
                    "actor_label": actor_label,
                    "actor_name": actor_name,
                    "component_name": component_name,
                    "unreal_asset_path": mesh_path,
                    "truth_binding": {
                        "collision_proxy_id": collision_proxy_id,
                        "render_only": False,
                    },
                }
            )

    payload = build_payload(
        scene_id=scene_id,
        map_id=map_id,
        project_path=project_path,
        level_name=level_name,
        assets=assets,
        collision_proxies=proxies,
    )
    errors = validate_truth_payload(payload)
    if errors:
        raise RuntimeError("Invalid exported truth: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def validate_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_truth_payload(payload)
    return {
        "path": str(path),
        "ok": not errors,
        "errors": errors,
        "scene_id": payload.get("scene_id", ""),
        "map_id": payload.get("map_id", ""),
        "asset_count": len(payload.get("assets", [])) if isinstance(payload.get("assets"), list) else 0,
        "collision_proxy_count": len(payload.get("collision_proxies", []))
        if isinstance(payload.get("collision_proxies"), list)
        else 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Run inside Unreal Editor Python and export current level truth.")
    export_parser.add_argument("--scene-id", required=True)
    export_parser.add_argument("--map-id", required=True)
    export_parser.add_argument("--output", type=Path, default=None)
    export_parser.add_argument("--include-no-collision", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate an exported truth JSON file.")
    validate_parser.add_argument("path", type=Path)
    validate_parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "export":
        output = args.output or DEFAULT_OUTPUT_DIR / f"{slug(args.map_id)}_collision_truth.json"
        payload = export_from_unreal(args.scene_id, args.map_id, output, args.include_no_collision)
        print(
            f"Wrote {output}: assets={len(payload['assets'])} "
            f"collision_proxies={len(payload['collision_proxies'])}"
        )
        return 0

    result = validate_file(args.path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        state = "OK" if result["ok"] else "FAIL"
        print(
            f"{state} {args.path}: assets={result['asset_count']} "
            f"collision_proxies={result['collision_proxy_count']}"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
