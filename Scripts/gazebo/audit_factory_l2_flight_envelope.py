#!/usr/bin/env python3
"""Audit Factory L2 flight envelope from UE collision truth.

This is a source/static audit. It does not launch Gazebo, ROS, PX4, MAVROS,
RViz, FUEL, RACER, or UE. The output is a conservative contract for later
runtime gates: where the Factory has floor support, what XY bounds are usable,
and what Z policy should be used before full-map exploration.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
DEFAULT_SCENE_PROFILE = ROOT / "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json"

FLOOR_TERMS = (
    "factoryfloorlarge",
    "concretefloor",
    "rubberfloor",
    "floormat",
    "floormatsmerged",
    "pedestrianpath",
    "paintboxfloor",
)
STRUCTURE_TERMS = (
    "wall",
    "fence",
    "pillar",
    "column",
    "beam",
    "platform",
    "railing",
    "assemblyline",
    "container",
    "locker",
    "truck",
    "tower",
    "pipe",
    "cables",
    "storage",
    "hangar",
    "background",
)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def actor_name(proxy: dict[str, Any]) -> str:
    return str(proxy.get("source_actor") or proxy.get("source_mesh") or proxy.get("collision_proxy_id") or "")


def has_any_term(name: str, terms: tuple[str, ...]) -> bool:
    lower = name.lower()
    return any(term in lower for term in terms)


def is_low_floor(proxy: dict[str, Any]) -> bool:
    name = actor_name(proxy)
    min_m = proxy.get("min_m", [0.0, 0.0, 0.0])
    max_m = proxy.get("max_m", [0.0, 0.0, 0.0])
    size_m = proxy.get("size_m", [0.0, 0.0, 0.0])
    if not has_any_term(name, FLOOR_TERMS):
        return False
    if len(min_m) < 3 or len(max_m) < 3 or len(size_m) < 3:
        return False
    # Factory floor plates are broad and thin near z=0. This rejects lockers,
    # platforms, and other non-floor meshes with "floor" in their name.
    return (
        float(min_m[2]) <= 0.25
        and float(max_m[2]) <= 0.35
        and float(size_m[0]) >= 2.0
        and float(size_m[1]) >= 2.0
        and float(size_m[2]) <= 1.0
    )


def is_low_structure(proxy: dict[str, Any]) -> bool:
    name = actor_name(proxy)
    min_m = proxy.get("min_m", [0.0, 0.0, 0.0])
    max_m = proxy.get("max_m", [0.0, 0.0, 0.0])
    if len(min_m) < 3 or len(max_m) < 3:
        return False
    if float(max_m[2]) < 0.2 or float(min_m[2]) > 4.5:
        return False
    return has_any_term(name, STRUCTURE_TERMS)


def rect(proxy: dict[str, Any]) -> tuple[float, float, float, float]:
    min_m = proxy["min_m"]
    max_m = proxy["max_m"]
    return float(min_m[0]), float(min_m[1]), float(max_m[0]), float(max_m[1])


def rect_area(r: tuple[float, float, float, float]) -> float:
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


def rects_touch(a: tuple[float, float, float, float], b: tuple[float, float, float, float], gap: float) -> bool:
    return not (a[2] < b[0] - gap or b[2] < a[0] - gap or a[3] < b[1] - gap or b[3] < a[1] - gap)


def connected_components(rectangles: list[tuple[float, float, float, float]], gap: float) -> list[list[int]]:
    parent = list(range(len(rectangles)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(rectangles)):
        for j in range(i + 1, len(rectangles)):
            if rects_touch(rectangles[i], rectangles[j], gap):
                union(i, j)
    out: dict[int, list[int]] = {}
    for i in range(len(rectangles)):
        out.setdefault(find(i), []).append(i)
    return list(out.values())


def bounds_from_rects(rectangles: list[tuple[float, float, float, float]]) -> dict[str, Any]:
    min_x = min(r[0] for r in rectangles)
    min_y = min(r[1] for r in rectangles)
    max_x = max(r[2] for r in rectangles)
    max_y = max(r[3] for r in rectangles)
    return {
        "min_xy_m": [min_x, min_y],
        "max_xy_m": [max_x, max_y],
        "size_xy_m": [max_x - min_x, max_y - min_y],
        "center_xy_m": [(min_x + max_x) * 0.5, (min_y + max_y) * 0.5],
        "area_bbox_m2": (max_x - min_x) * (max_y - min_y),
        "area_sum_m2": sum(rect_area(r) for r in rectangles),
    }


def point_in_rect(point_xy: list[float], r: tuple[float, float, float, float], margin: float = 0.0) -> bool:
    return (
        r[0] - margin <= point_xy[0] <= r[2] + margin
        and r[1] - margin <= point_xy[1] <= r[3] + margin
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "index",
        "source_actor",
        "min_x_m",
        "min_y_m",
        "min_z_m",
        "max_x_m",
        "max_y_m",
        "max_z_m",
        "size_x_m",
        "size_y_m",
        "size_z_m",
        "xy_area_m2",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for index, row in enumerate(rows):
            min_m = row["min_m"]
            max_m = row["max_m"]
            size_m = row["size_m"]
            writer.writerow({
                "index": index,
                "source_actor": actor_name(row),
                "min_x_m": min_m[0],
                "min_y_m": min_m[1],
                "min_z_m": min_m[2],
                "max_x_m": max_m[0],
                "max_y_m": max_m[1],
                "max_z_m": max_m[2],
                "size_x_m": size_m[0],
                "size_y_m": size_m[1],
                "size_z_m": size_m[2],
                "xy_area_m2": float(size_m[0]) * float(size_m[1]),
            })


def default_spawns(scene_profile: dict[str, Any]) -> list[dict[str, Any]]:
    spawns = scene_profile.get("default_spawn_points", [])
    if not isinstance(spawns, list):
        return []
    return [spawn for spawn in spawns if isinstance(spawn, dict)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--scene-profile", type=Path, default=DEFAULT_SCENE_PROFILE)
    parser.add_argument("--result-dir", type=Path, default=None)
    parser.add_argument("--floor-gap-m", type=float, default=0.25)
    parser.add_argument("--boundary-margin-m", type=float, default=2.0)
    parser.add_argument("--recommended-fixed-z-m", type=float, default=1.2)
    parser.add_argument("--recommended-min-z-m", type=float, default=0.9)
    parser.add_argument("--recommended-max-z-m", type=float, default=1.6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scene_truth = project_path(args.scene_truth)
    scene_profile_path = project_path(args.scene_profile)
    result_dir = (
        project_path(args.result_dir)
        if args.result_dir is not None
        else ROOT / "Results/unreal_scene_mapping" / f"factory_l2_flight_envelope_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    truth = read_json(scene_truth)
    scene_profile = read_json(scene_profile_path)
    proxies = [p for p in truth.get("collision_proxies", []) if isinstance(p, dict)]
    floor_proxies = [p for p in proxies if is_low_floor(p)]
    structure_proxies = [p for p in proxies if is_low_structure(p)]
    floor_rects = [rect(p) for p in floor_proxies]
    components = connected_components(floor_rects, args.floor_gap_m) if floor_rects else []
    component_reports: list[dict[str, Any]] = []
    for component_index, indexes in enumerate(components):
        component_rects = [floor_rects[i] for i in indexes]
        component_reports.append({
            "component_index": component_index,
            "floor_count": len(indexes),
            "bounds": bounds_from_rects(component_rects),
            "floor_actors_sample": [actor_name(floor_proxies[i]) for i in indexes[:20]],
        })
    component_reports.sort(key=lambda item: float(item["bounds"]["area_sum_m2"]), reverse=True)

    spawns = default_spawns(scene_profile)
    spawn_reports: list[dict[str, Any]] = []
    for spawn in spawns:
        point = [float(spawn.get("x", 0.0)), float(spawn.get("y", 0.0))]
        containing = [
            actor_name(proxy)
            for proxy, floor_rect in zip(floor_proxies, floor_rects)
            if point_in_rect(point, floor_rect, margin=0.05)
        ]
        spawn_reports.append({
            "uav": int(spawn.get("uav", len(spawn_reports) + 1)),
            "xyz_m": [float(spawn.get("x", 0.0)), float(spawn.get("y", 0.0)), float(spawn.get("z", 0.0))],
            "yaw_rad": float(spawn.get("yaw", 0.0)),
            "on_floor": bool(containing),
            "floor_actors": containing[:10],
        })

    largest = component_reports[0] if component_reports else None
    status = "passed" if largest and all(row["on_floor"] for row in spawn_reports[:1]) else "blocked_no_valid_floor_envelope"
    recommended_boundary = None
    if largest:
        b = largest["bounds"]
        recommended_boundary = {
            "basis": "largest_connected_low_floor_component_minus_margin",
            "margin_m": args.boundary_margin_m,
            "min_x_m": float(b["min_xy_m"][0]) + args.boundary_margin_m,
            "max_x_m": float(b["max_xy_m"][0]) - args.boundary_margin_m,
            "min_y_m": float(b["min_xy_m"][1]) + args.boundary_margin_m,
            "max_y_m": float(b["max_xy_m"][1]) - args.boundary_margin_m,
        }
        recommended_boundary["size_x_m"] = recommended_boundary["max_x_m"] - recommended_boundary["min_x_m"]
        recommended_boundary["size_y_m"] = recommended_boundary["max_y_m"] - recommended_boundary["min_y_m"]
        recommended_boundary["center_x_m"] = (recommended_boundary["min_x_m"] + recommended_boundary["max_x_m"]) * 0.5
        recommended_boundary["center_y_m"] = (recommended_boundary["min_y_m"] + recommended_boundary["max_y_m"]) * 0.5

    z_max_values = [float(proxy["max_m"][2]) for proxy in structure_proxies if "max_m" in proxy]
    z_min_values = [float(proxy["min_m"][2]) for proxy in floor_proxies if "min_m" in proxy]
    z_policy = {
        "initial_policy": "fixed_world_z_band",
        "fixed_z_m": args.recommended_fixed_z_m,
        "min_cmd_z_m": args.recommended_min_z_m,
        "max_cmd_z_m": args.recommended_max_z_m,
        "floor_reference": "low floor proxies have top_z near 0.05 m; use world-z altitude until a terrain-aware policy is explicitly required",
        "why_not_free_z_yet": [
            "FUEL/RACER full-map exploration must first prove stable map and frontier behavior.",
            "Factory contains high pipes, platforms, walls, and background structures; allowing unconstrained Z can create vertical excursions that look like exploration but are unsafe for control review.",
            "If source audit later proves floor height changes materially along the accepted boundary, promote to a tiled or terrain-aware altitude policy before runtime expansion.",
        ],
        "floor_min_z_range_m": [min(z_min_values) if z_min_values else None, max(z_min_values) if z_min_values else None],
        "low_structure_max_z_sample_stats_m": {
            "count": len(z_max_values),
            "max": max(z_max_values) if z_max_values else None,
            "p95_approx": sorted(z_max_values)[min(len(z_max_values) - 1, int(math.floor(0.95 * len(z_max_values))))] if z_max_values else None,
        },
    }

    floor_csv = result_dir / "factory_l2_low_floor_candidates.csv"
    structure_csv = result_dir / "factory_l2_low_structure_candidates.csv"
    write_csv(floor_csv, sorted(floor_proxies, key=lambda p: float(p["size_m"][0]) * float(p["size_m"][1]), reverse=True))
    write_csv(structure_csv, sorted(structure_proxies, key=lambda p: float(p["size_m"][0]) * float(p["size_m"][1]), reverse=True))

    packet = {
        "schema": "mosim.factory_l2_flight_envelope_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_boundary": [
            "Source/static flight-envelope audit only.",
            "This does not prove Gazebo/PX4/MAVROS/RViz runtime success.",
            "This does not prove FUEL/RACER exploration coverage or controller performance.",
            "The recommended boundary is an engineering runtime envelope derived from low-floor AABBs, not a semantic map of every wall or door.",
        ],
        "inputs": {
            "scene_truth": rel(scene_truth),
            "scene_profile": rel(scene_profile_path),
        },
        "counts": {
            "collision_proxy_count": len(proxies),
            "low_floor_candidate_count": len(floor_proxies),
            "low_structure_candidate_count": len(structure_proxies),
            "floor_component_count": len(component_reports),
        },
        "floor_selector": {
            "terms": list(FLOOR_TERMS),
            "max_floor_top_z_m": 0.35,
            "min_floor_xy_size_m": 2.0,
            "max_floor_thickness_m": 1.0,
            "component_gap_m": args.floor_gap_m,
        },
        "floor_components": component_reports[:20],
        "default_spawn_checks": spawn_reports,
        "recommended_exploration_boundary": recommended_boundary,
        "z_policy": z_policy,
        "outputs": {
            "low_floor_candidates_csv": rel(floor_csv),
            "low_structure_candidates_csv": rel(structure_csv),
        },
        "runtime_gate_recommendation": {
            "single_uav_first": True,
            "multi_uav_after_single_pass": True,
            "start_with_tiled_or_windowed_exploration": True,
            "reason": "Largest floor component is hundreds of meters wide; one monolithic FUEL SDF map is likely memory/latency risky. Validate per-tile/window first, then expand only if metrics stay bounded.",
            "minimum_metrics": [
                "all UAVs stay inside recommended_exploration_boundary",
                "truth and odom z stay inside z_policy min/max with small tolerance",
                "no roll/pitch safety violation",
                "planner publishes nonempty frontier/bspline/position_cmd evidence",
                "accumulated point cloud and occupancy counts increase without unbounded RViz/Gazebo failure",
            ],
        },
    }
    packet_path = result_dir / "FACTORY_L2_FLIGHT_ENVELOPE_AUDIT.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path = result_dir / "SUMMARY.md"
    summary_path.write_text(
        "\n".join([
            "# Factory L2 Flight Envelope Audit",
            "",
            f"- status: `{status}`",
            f"- low floor candidates: `{len(floor_proxies)}`",
            f"- low structure candidates: `{len(structure_proxies)}`",
            f"- floor components: `{len(component_reports)}`",
            f"- recommended boundary: `{recommended_boundary}`",
            f"- z policy: `{z_policy}`",
            f"- packet: `{rel(packet_path)}`",
            f"- floor csv: `{rel(floor_csv)}`",
            f"- structure csv: `{rel(structure_csv)}`",
            "",
            "This is source/static evidence only. Runtime exploration gates must still be rerun.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": status, "packet": rel(packet_path), "summary": rel(summary_path)}, ensure_ascii=False, indent=2))
    return 0 if status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
