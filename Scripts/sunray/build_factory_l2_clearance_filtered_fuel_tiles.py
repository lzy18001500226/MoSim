#!/usr/bin/env python3
"""Build clearance-filtered Factory L2 FUEL tile/window centers.

This is a source-truth guard for FUEL rolling/tile coverage probes. It does
not launch Gazebo, PX4, MAVROS, FUEL, RViz, or UE. It filters candidate
start/window centers against the accepted Factory indoor boundary, stable
floor support, spawn-footprint blockers, and flight-height collision-truth
AABBs before runtime is attempted.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENVELOPE = ROOT / "Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json"
DEFAULT_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/sunray_ros1"

FLOOR_TERMS = (
    "factoryfloorlarge",
    "concretefloor",
    "rubberfloor",
)


@dataclass(frozen=True)
class Rect:
    min_x: float
    min_y: float
    max_x: float
    max_y: float


@dataclass(frozen=True)
class Proxy:
    proxy_id: str
    actor: str
    semantic_type: str
    rect: Rect
    min_z: float
    max_z: float
    size_z: float


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    x: float
    y: float
    yaw: float
    row_index: int
    column_index: int


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


def has_floor_term(name: str) -> bool:
    lower = name.lower()
    return any(term in lower for term in FLOOR_TERMS)


def proxy_from_raw(proxy: dict[str, Any]) -> Proxy | None:
    min_m = proxy.get("min_m")
    max_m = proxy.get("max_m")
    size_m = proxy.get("size_m")
    if not isinstance(min_m, list) or not isinstance(max_m, list) or len(min_m) < 3 or len(max_m) < 3:
        return None
    if not isinstance(size_m, list) or len(size_m) < 3:
        size_m = [float(max_m[0]) - float(min_m[0]), float(max_m[1]) - float(min_m[1]), float(max_m[2]) - float(min_m[2])]
    return Proxy(
        proxy_id=str(proxy.get("collision_proxy_id", "")),
        actor=actor_name(proxy),
        semantic_type=str(proxy.get("semantic_type", "")),
        rect=Rect(float(min_m[0]), float(min_m[1]), float(max_m[0]), float(max_m[1])),
        min_z=float(min_m[2]),
        max_z=float(max_m[2]),
        size_z=float(size_m[2]),
    )


def is_low_floor(proxy: Proxy) -> bool:
    return (
        has_floor_term(proxy.actor)
        and proxy.min_z <= 0.25
        and proxy.max_z <= 0.35
        and (proxy.rect.max_x - proxy.rect.min_x) >= 2.0
        and (proxy.rect.max_y - proxy.rect.min_y) >= 2.0
        and proxy.size_z <= 1.0
    )


def point_inside_rect(x: float, y: float, rect: Rect, shrink: float = 0.0) -> bool:
    return (
        rect.min_x + shrink <= x <= rect.max_x - shrink
        and rect.min_y + shrink <= y <= rect.max_y - shrink
    )


def point_clear_of_rect(x: float, y: float, rect: Rect, margin: float) -> bool:
    return not (
        rect.min_x - margin <= x <= rect.max_x + margin
        and rect.min_y - margin <= y <= rect.max_y + margin
    )


def xy_distance_to_rect(x: float, y: float, rect: Rect) -> float:
    dx = max(rect.min_x - x, 0.0, x - rect.max_x)
    dy = max(rect.min_y - y, 0.0, y - rect.max_y)
    return math.hypot(dx, dy)


def clamp(value: float, lo: float, hi: float) -> float:
    return min(max(value, lo), hi)


def boundary_from_envelope(envelope: dict[str, Any]) -> dict[str, float]:
    boundary = envelope.get("exploration_boundary", {})
    if not isinstance(boundary, dict):
        raise ValueError("envelope.exploration_boundary must be an object")
    return {
        "min_x": float(boundary["min_x_m"]),
        "max_x": float(boundary["max_x_m"]),
        "min_y": float(boundary["min_y_m"]),
        "max_y": float(boundary["max_y_m"]),
        "center_x": float(boundary.get("center_x_m", (float(boundary["min_x_m"]) + float(boundary["max_x_m"])) * 0.5)),
        "center_y": float(boundary.get("center_y_m", (float(boundary["min_y_m"]) + float(boundary["max_y_m"])) * 0.5)),
    }


def generate_candidates(boundary: dict[str, float], args: argparse.Namespace) -> list[Candidate]:
    window_half_xy = max(0.0, args.fuel_window_xy_m * 0.5)
    effective_boundary_margin = max(args.boundary_margin_m, window_half_xy + args.window_boundary_margin_m)
    min_x = boundary["min_x"] + effective_boundary_margin
    max_x = boundary["max_x"] - effective_boundary_margin
    min_y = boundary["min_y"] + effective_boundary_margin
    max_y = boundary["max_y"] - effective_boundary_margin
    if min_x > max_x or min_y > max_y:
        raise ValueError("boundary margin is larger than the exploration boundary")

    candidates: list[Candidate] = []
    if args.pattern == "forward_strip":
        row_offsets = [0.0, args.step_y_m, -args.step_y_m, 2.0 * args.step_y_m, -2.0 * args.step_y_m, 3.0 * args.step_y_m, -3.0 * args.step_y_m]
        for row_index, row_offset in enumerate(row_offsets):
            y = clamp(boundary["center_y"] + row_offset, min_y, max_y)
            direction = 1.0 if row_index % 2 == 0 else -1.0
            x = boundary["center_x"]
            column_index = 0
            while min_x <= x <= max_x:
                yaw = args.tile_yaw_rad
                candidates.append(Candidate(f"cand_r{row_index:02d}_c{column_index:03d}", round(x, 6), round(y, 6), yaw, row_index, column_index))
                x += direction * args.step_x_m
                column_index += 1
            if direction > 0 and x > max_x and column_index == 0:
                candidates.append(Candidate(f"cand_r{row_index:02d}_c000", round(max_x, 6), round(y, 6), args.tile_yaw_rad, row_index, 0))
            if direction < 0 and x < min_x and column_index == 0:
                candidates.append(Candidate(f"cand_r{row_index:02d}_c000", round(min_x, 6), round(y, 6), args.tile_yaw_rad, row_index, 0))
        return candidates

    y = min_y
    row_index = 0
    while y <= max_y + 1e-6:
        direction = 1.0 if row_index % 2 == 0 else -1.0
        x = min_x if direction > 0 else max_x
        column_index = 0
        while (direction > 0 and x <= max_x + 1e-6) or (direction < 0 and x >= min_x - 1e-6):
            yaw = args.tile_yaw_rad
            candidates.append(Candidate(f"cand_r{row_index:02d}_c{column_index:03d}", round(x, 6), round(y, 6), yaw, row_index, column_index))
            x += direction * args.step_x_m
            column_index += 1
        y += args.step_y_m
        row_index += 1
    return candidates


def evaluate_candidate(
    candidate: Candidate,
    floor_proxies: list[Proxy],
    flight_obstacle_proxies: list[Proxy],
    spawn_obstacle_proxies: list[Proxy],
    args: argparse.Namespace,
) -> dict[str, Any]:
    floor_hits = [p for p in floor_proxies if point_inside_rect(candidate.x, candidate.y, p.rect, args.floor_edge_margin_m)]
    nearest_floor_edge = None
    for floor in floor_hits:
        edge = min(candidate.x - floor.rect.min_x, floor.rect.max_x - candidate.x, candidate.y - floor.rect.min_y, floor.rect.max_y - candidate.y)
        nearest_floor_edge = edge if nearest_floor_edge is None else max(nearest_floor_edge, edge)

    flight_overlapping = [
        p
        for p in flight_obstacle_proxies
        if not point_clear_of_rect(candidate.x, candidate.y, p.rect, args.clearance_margin_m)
    ]
    spawn_overlapping = [
        p
        for p in spawn_obstacle_proxies
        if not point_clear_of_rect(candidate.x, candidate.y, p.rect, args.spawn_clearance_margin_m)
    ]
    nearest_obstacle = None
    nearest_distance = None
    for obstacle in list(flight_obstacle_proxies) + list(spawn_obstacle_proxies):
        distance = xy_distance_to_rect(candidate.x, candidate.y, obstacle.rect)
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_obstacle = obstacle

    reasons: list[str] = []
    if not floor_hits:
        reasons.append("no_low_floor_support")
    if flight_overlapping:
        reasons.append("flight_height_obstacle_overlap")
    if spawn_overlapping:
        reasons.append("spawn_footprint_obstacle_overlap")

    accepted = not reasons
    return {
        "candidate_id": candidate.candidate_id,
        "accepted": accepted,
        "tile_id": None,
        "x": candidate.x,
        "y": candidate.y,
        "yaw": round(candidate.yaw, 6),
        "row_index": candidate.row_index,
        "column_index": candidate.column_index,
        "reasons": reasons,
        "floor_support_count": len(floor_hits),
        "floor_support_sample": [p.actor for p in floor_hits[:5]],
        "nearest_floor_edge_margin_m": round(nearest_floor_edge, 6) if nearest_floor_edge is not None else None,
        "overlap_count": len(flight_overlapping) + len(spawn_overlapping),
        "flight_overlap_count": len(flight_overlapping),
        "spawn_overlap_count": len(spawn_overlapping),
        "overlap_sample": [
            {
                "actor": p.actor,
                "proxy_id": p.proxy_id,
                "min_z_m": p.min_z,
                "max_z_m": p.max_z,
            }
            for p in (spawn_overlapping + flight_overlapping)[:8]
        ],
        "nearest_low_obstacle": {
            "distance_xy_m": round(nearest_distance, 6) if nearest_distance is not None else None,
            "actor": nearest_obstacle.actor if nearest_obstacle is not None else None,
            "proxy_id": nearest_obstacle.proxy_id if nearest_obstacle is not None else None,
            "min_z_m": nearest_obstacle.min_z if nearest_obstacle is not None else None,
            "max_z_m": nearest_obstacle.max_z if nearest_obstacle is not None else None,
        },
    }


def write_tile_csv(path: Path, accepted: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tile_id", "x", "y", "yaw"])
        writer.writeheader()
        for row in accepted:
            writer.writerow({
                "tile_id": row["tile_id"],
                "x": row["x"],
                "y": row["y"],
                "yaw": row["yaw"],
            })


def write_candidate_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "candidate_id",
            "accepted",
            "tile_id",
            "x",
            "y",
            "yaw",
            "row_index",
            "column_index",
            "reasons",
            "floor_support_count",
            "overlap_count",
            "flight_overlap_count",
            "spawn_overlap_count",
            "nearest_low_obstacle_distance_xy_m",
            "nearest_low_obstacle_actor",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            nearest = row["nearest_low_obstacle"]
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "accepted": row["accepted"],
                "tile_id": row["tile_id"],
                "x": row["x"],
                "y": row["y"],
                "yaw": row["yaw"],
                "row_index": row["row_index"],
                "column_index": row["column_index"],
                "reasons": ";".join(row["reasons"]),
                "floor_support_count": row["floor_support_count"],
                "overlap_count": row["overlap_count"],
                "flight_overlap_count": row["flight_overlap_count"],
                "spawn_overlap_count": row["spawn_overlap_count"],
                "nearest_low_obstacle_distance_xy_m": nearest["distance_xy_m"],
                "nearest_low_obstacle_actor": nearest["actor"],
            })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--scene-truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--pattern", choices=["forward_strip", "lawnmower"], default="lawnmower")
    parser.add_argument("--max-accepted", type=int, default=8)
    parser.add_argument("--step-x-m", type=float, default=10.0)
    parser.add_argument("--step-y-m", type=float, default=10.0)
    parser.add_argument("--tile-yaw-rad", type=float, default=0.0)
    parser.add_argument("--boundary-margin-m", type=float, default=2.0)
    parser.add_argument("--fuel-window-xy-m", type=float, default=16.0)
    parser.add_argument("--window-boundary-margin-m", type=float, default=0.0)
    parser.add_argument("--floor-edge-margin-m", type=float, default=0.5)
    parser.add_argument("--clearance-margin-m", type=float, default=1.25)
    parser.add_argument("--spawn-clearance-margin-m", type=float, default=1.25)
    parser.add_argument("--spawn-obstacle-min-z-m", type=float, default=0.15)
    parser.add_argument("--spawn-obstacle-max-z-m", type=float, default=0.65)
    parser.add_argument("--low-obstacle-min-z-m", type=float, default=0.2)
    parser.add_argument("--low-obstacle-max-z-m", type=float, default=1.7)
    parser.add_argument("--flight-obstacle-min-z-m", type=float, default=0.7)
    parser.add_argument("--max-candidates", type=int, default=500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_accepted <= 0:
        raise SystemExit("--max-accepted must be positive")
    if args.step_x_m <= 0.0 or args.step_y_m <= 0.0:
        raise SystemExit("--step-x-m and --step-y-m must be positive")
    if args.fuel_window_xy_m <= 0.0:
        raise SystemExit("--fuel-window-xy-m must be positive")

    envelope_path = project_path(args.envelope)
    truth_path = project_path(args.scene_truth)
    output_dir = (
        project_path(args.output_dir)
        if args.output_dir is not None
        else DEFAULT_OUTPUT_ROOT / f"factory_l2_fuel_clearance_filtered_tiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    envelope = read_json(envelope_path)
    truth = read_json(truth_path)
    boundary = boundary_from_envelope(envelope)

    proxies = [proxy_from_raw(p) for p in truth.get("collision_proxies", []) if isinstance(p, dict)]
    proxies = [p for p in proxies if p is not None]
    floor_proxies = [p for p in proxies if is_low_floor(p)]
    flight_obstacle_proxies = [
        p
        for p in proxies
        if not is_low_floor(p)
        and p.max_z >= args.low_obstacle_min_z_m
        and p.max_z >= args.flight_obstacle_min_z_m
        and p.min_z <= args.low_obstacle_max_z_m
    ]
    spawn_obstacle_proxies = [
        p
        for p in proxies
        if not is_low_floor(p)
        and p.max_z >= args.spawn_obstacle_min_z_m
        and p.min_z <= args.spawn_obstacle_max_z_m
    ]

    candidates = generate_candidates(boundary, args)[: args.max_candidates]
    rows: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    for candidate in candidates:
        row = evaluate_candidate(candidate, floor_proxies, flight_obstacle_proxies, spawn_obstacle_proxies, args)
        if row["accepted"] and len(accepted) < args.max_accepted:
            row["tile_id"] = f"win{len(accepted) + 1:02d}"
            accepted.append(row)
        rows.append(row)
        if len(accepted) >= args.max_accepted:
            break

    tile_csv = output_dir / "clearance_filtered_fuel_tiles.csv"
    candidate_csv = output_dir / "clearance_filtered_fuel_candidates.csv"
    packet_path = output_dir / "FACTORY_L2_FUEL_CLEARANCE_FILTERED_TILES.json"
    write_tile_csv(tile_csv, accepted)
    write_candidate_csv(candidate_csv, rows)

    packet = {
        "schema": "mosim.factory_l2_fuel_clearance_filtered_tiles.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if len(accepted) >= args.max_accepted else "review_required_insufficient_safe_tiles",
        "claim_boundary": [
            "Source/static candidate filtering only.",
            "This proves candidate start/window centers have stable floor support, keep the configured FUEL local window inside the indoor boundary, and do not overlap configured spawn-footprint or flight-height collision-truth AABBs under the configured margins.",
            "This does not prove FUEL will complete coverage or that the full path is collision-free.",
            "Runtime promotion still requires Gazebo/PX4/MAVROS/FUEL metrics and merged coverage evidence.",
        ],
        "inputs": {
            "envelope": rel(envelope_path),
            "scene_truth": rel(truth_path),
        },
        "parameters": {
            "pattern": args.pattern,
            "max_accepted": args.max_accepted,
            "step_x_m": args.step_x_m,
            "step_y_m": args.step_y_m,
            "tile_yaw_rad": args.tile_yaw_rad,
            "boundary_margin_m": args.boundary_margin_m,
            "fuel_window_xy_m": args.fuel_window_xy_m,
            "window_boundary_margin_m": args.window_boundary_margin_m,
            "effective_boundary_margin_m": max(
                args.boundary_margin_m,
                args.fuel_window_xy_m * 0.5 + args.window_boundary_margin_m,
            ),
            "floor_edge_margin_m": args.floor_edge_margin_m,
            "clearance_margin_m": args.clearance_margin_m,
            "spawn_clearance_margin_m": args.spawn_clearance_margin_m,
            "spawn_obstacle_min_z_m": args.spawn_obstacle_min_z_m,
            "spawn_obstacle_max_z_m": args.spawn_obstacle_max_z_m,
            "low_obstacle_min_z_m": args.low_obstacle_min_z_m,
            "low_obstacle_max_z_m": args.low_obstacle_max_z_m,
            "flight_obstacle_min_z_m": args.flight_obstacle_min_z_m,
            "max_candidates": args.max_candidates,
        },
        "boundary": boundary,
        "counts": {
            "collision_proxy_count": len(proxies),
            "low_floor_proxy_count": len(floor_proxies),
            "flight_obstacle_proxy_count": len(flight_obstacle_proxies),
            "spawn_obstacle_proxy_count": len(spawn_obstacle_proxies),
            "evaluated_candidate_count": len(rows),
            "accepted_tile_count": len(accepted),
            "rejected_candidate_count": len([row for row in rows if not row["accepted"]]),
        },
        "accepted_tiles": [
            {
                "tile_id": row["tile_id"],
                "x": row["x"],
                "y": row["y"],
                "yaw": row["yaw"],
                "floor_support_sample": row["floor_support_sample"],
                "nearest_low_obstacle": row["nearest_low_obstacle"],
                "fuel_window_bounds": {
                    "min_x": round(row["x"] - args.fuel_window_xy_m * 0.5, 6),
                    "max_x": round(row["x"] + args.fuel_window_xy_m * 0.5, 6),
                    "min_y": round(row["y"] - args.fuel_window_xy_m * 0.5, 6),
                    "max_y": round(row["y"] + args.fuel_window_xy_m * 0.5, 6),
                },
            }
            for row in accepted
        ],
        "rejection_summary": {
            "no_low_floor_support": len([row for row in rows if "no_low_floor_support" in row["reasons"]]),
            "flight_height_obstacle_overlap": len([row for row in rows if "flight_height_obstacle_overlap" in row["reasons"]]),
            "spawn_footprint_obstacle_overlap": len([row for row in rows if "spawn_footprint_obstacle_overlap" in row["reasons"]]),
        },
        "outputs": {
            "tile_csv": rel(tile_csv),
            "candidate_csv": rel(candidate_csv),
            "packet": rel(packet_path),
        },
        "next_runtime_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"C:\\Users\\HP\\Desktop\\MoSim\\Scripts\\sunray\\start_factory_fuel_tile_coverage_probe.ps1\" "
            f"-RunId factory_l2_fuel_clearance_filtered_runtime_YYYYMMDD_HHMMSS "
            f"-TileCsv \"{tile_csv}\" -MaxTiles {len(accepted)}"
        ),
    }
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": packet["status"], "packet": str(packet_path), "tile_csv": str(tile_csv), "accepted": len(accepted)}, ensure_ascii=False))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
