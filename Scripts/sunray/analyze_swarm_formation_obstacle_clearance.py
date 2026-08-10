#!/usr/bin/env python3
"""Gate actual UAV detours against Factory collision-proxy truth.

This is a post-flight evidence check.  It never supplies collision truth to a
planner or controller: the live MID360 -> world cloud -> grid-map route remains
the only obstacle input at runtime.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts" / "sunray"))
import generate_factory_l2_clearance_route_waypoints as clearance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--scene-truth", default="")
    parser.add_argument("--output", default="")
    parser.add_argument(
        "--uav-ids",
        default="1,2,3",
        help="Comma-separated member IDs to evaluate; defaults to the complete formation.",
    )
    parser.add_argument(
        "--truth-file-template",
        default="uav{uid}_truth.csv",
        help="Run-relative truth CSV name, optionally containing {uid}.",
    )
    parser.add_argument(
        "--execute-phases",
        default="ego_execute",
        help="Comma-separated truth phases that constitute obstacle traversal.",
    )
    parser.add_argument("--planner-clearance-m", type=float, default=0.20)
    parser.add_argument("--vertical-margin-m", type=float, default=0.0)
    parser.add_argument("--max-segment-sample-m", type=float, default=0.05)
    parser.add_argument("--max-execute-start-error-m", type=float, default=0.80)
    parser.add_argument("--max-execute-end-error-m", type=float, default=0.55)
    parser.add_argument("--min-detour-excess-m", type=float, default=0.25)
    parser.add_argument("--max-truth-gap-s", type=float, default=0.15)
    return parser.parse_args()


def resolve_path(value: str, scenario_path: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    for base in (ROOT, scenario_path.parent):
        path = (base / candidate).resolve()
        if path.exists():
            return path
    return (ROOT / candidate).resolve()


def parse_csv_tokens(raw: str, label: str) -> list[str]:
    values = [token.strip() for token in raw.split(",") if token.strip()]
    if not values:
        raise SystemExit(f"{label} must contain at least one value")
    return values


def parse_uav_ids(raw: str) -> list[str]:
    values = parse_csv_tokens(raw, "uav IDs")
    invalid = [value for value in values if value not in {"1", "2", "3"}]
    if invalid:
        raise SystemExit(f"unsupported UAV IDs: {', '.join(invalid)}")
    return list(dict.fromkeys(values))


def read_execute_rows(path: Path, execute_phases: set[str]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            if raw.get("phase") not in execute_phases:
                continue
            try:
                rows.append({axis: float(raw[axis]) for axis in ("t", "x", "y", "z")})
            except (KeyError, TypeError, ValueError):
                continue
    return rows


def sampled_rows(rows: list[dict[str, float]], max_segment_sample_m: float) -> list[dict[str, float]]:
    if not rows:
        return []
    samples = [rows[0]]
    for previous, current in zip(rows, rows[1:]):
        distance = math.dist(
            (previous["x"], previous["y"], previous["z"]),
            (current["x"], current["y"], current["z"]),
        )
        parts = max(1, math.ceil(distance / max_segment_sample_m))
        for index in range(1, parts + 1):
            fraction = index / parts
            samples.append(
                {
                    axis: previous[axis] + (current[axis] - previous[axis]) * fraction
                    for axis in ("t", "x", "y", "z")
                }
            )
    return samples


def point_clearance_components_m(x: float, y: float, rect: clearance.Rect) -> tuple[float, float]:
    """Return the gate's AABB clearance and Euclidean diagnostic clearance.

    ``point_clear_of_rect`` uses an axis-aligned inflated rectangle.  A point
    is safe only when either axis escapes the inflated rectangle, therefore
    the gate quantity is ``max(dx, dy)``.  The Euclidean distance is retained
    only as a geometric diagnostic: at a rectangle corner it can exceed the
    margin while the AABB gate still correctly rejects the point.
    """
    dx = max(rect.min_x - x, 0.0, x - rect.max_x)
    dy = max(rect.min_y - y, 0.0, y - rect.max_y)
    return max(dx, dy), math.hypot(dx, dy)


def z_overlaps(point_z: float, obstacle: clearance.Proxy, vertical_margin_m: float) -> bool:
    return obstacle.min_z - vertical_margin_m <= point_z <= obstacle.max_z + vertical_margin_m


def obstacle_hits(
    samples: list[dict[str, float]],
    obstacles: list[clearance.Proxy],
    planner_clearance_m: float,
    vertical_margin_m: float,
) -> tuple[list[dict], dict[str, dict[str, float | None]]]:
    violations: list[dict] = []
    minimums: dict[str, dict[str, float | None]] = {
        obstacle.actor: {"axis_linf": None, "euclidean": None} for obstacle in obstacles
    }
    for sample in samples:
        for obstacle in obstacles:
            if not z_overlaps(sample["z"], obstacle, vertical_margin_m):
                continue
            axis_linf, euclidean = point_clearance_components_m(sample["x"], sample["y"], obstacle.rect)
            previous = minimums[obstacle.actor]
            if previous["axis_linf"] is None or axis_linf < previous["axis_linf"]:
                previous["axis_linf"] = axis_linf
            if previous["euclidean"] is None or euclidean < previous["euclidean"]:
                previous["euclidean"] = euclidean
            if not clearance.point_clear_of_rect(sample["x"], sample["y"], obstacle.rect, planner_clearance_m):
                violations.append(
                    {
                        "actor": obstacle.actor,
                        "t": sample["t"],
                        "x": sample["x"],
                        "y": sample["y"],
                        "z": sample["z"],
                        "axis_linf_clearance_m": axis_linf,
                        "euclidean_clearance_m": euclidean,
                    }
                )
    return violations, minimums


def path_length_m(rows: list[dict[str, float]]) -> float:
    return sum(
        math.dist((left["x"], left["y"]), (right["x"], right["y"]))
        for left, right in zip(rows, rows[1:])
    )


def obstacle_args() -> argparse.Namespace:
    return argparse.Namespace(
        flight_obstacle_min_z_m=0.70,
        flight_obstacle_max_z_m=1.70,
        obstacle_z_inflation_m=0.0,
        overhead_obstacle_max_min_z_m=0.0,
    )


def main() -> None:
    args = parse_args()
    if args.planner_clearance_m <= 0.0 or args.max_segment_sample_m <= 0.0:
        raise SystemExit("planner clearance and segment sample spacing must be positive")
    selected_uav_ids = parse_uav_ids(args.uav_ids)
    execute_phases = set(parse_csv_tokens(args.execute_phases, "execute phases"))

    run_dir = Path(args.run).resolve()
    scenario_path = Path(args.scenario).resolve()
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    output_path = Path(args.output).resolve() if args.output else run_dir / "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json"
    source_truth = args.scene_truth or str(scenario.get("source_truth") or "")
    if not source_truth:
        raise SystemExit("scenario has no source_truth and --scene-truth was not supplied")
    scene_truth_path = resolve_path(source_truth, scenario_path)
    truth = clearance.read_json(scene_truth_path)
    proxies = [
        proxy
        for raw in truth.get("collision_proxies", [])
        if isinstance(raw, dict) and (proxy := clearance.proxy_from_raw(raw)) is not None
    ]
    flight_obstacles = clearance.flight_obstacle_proxies(proxies, obstacle_args())
    obstacles_by_name = {obstacle.actor: obstacle for obstacle in flight_obstacles}

    formation = scenario.get("formation") or {}
    start_positions = formation.get("start_positions_xy_m") or {}
    target_positions = formation.get("target_positions_xy_m") or {}
    contract = scenario.get("obstacle_crossing_contract") or {}
    member_hits = contract.get("member_intersecting_proxies") or {}
    expected_blocked_uavs = [uid for uid in selected_uav_ids if member_hits.get(uid)]
    blockers: list[str] = []
    if not contract.get("direct_center_segment_blocked"):
        blockers.append("scenario_does_not_require_obstacle_detour")
    if not expected_blocked_uavs:
        blockers.append("scenario_has_no_member_obstacle_crossing")

    per_uav: dict[str, dict] = {}
    all_violations: list[dict] = []
    direct_contract: dict[str, dict] = {}
    for uid in selected_uav_ids:
        try:
            truth_relative = Path(args.truth_file_template.format(uid=uid))
        except (KeyError, ValueError) as error:
            raise SystemExit(f"invalid truth file template: {error}") from error
        if truth_relative.is_absolute() or ".." in truth_relative.parts:
            raise SystemExit("truth file template must resolve under the run directory")
        truth_csv = run_dir / truth_relative
        if not truth_csv.exists():
            blockers.append(f"uav{uid}_truth_csv_missing")
            continue
        rows = read_execute_rows(truth_csv, execute_phases)
        if len(rows) < 2:
            blockers.append(f"uav{uid}_execute_truth_missing")
            continue
        samples = sampled_rows(rows, args.max_segment_sample_m)
        violations, minimums = obstacle_hits(
            samples, flight_obstacles, args.planner_clearance_m, args.vertical_margin_m
        )
        start = start_positions.get(uid)
        target = target_positions.get(uid)
        start_error = None
        end_error = None
        direct_distance = None
        detour_excess = None
        if isinstance(start, list) and len(start) >= 2 and isinstance(target, list) and len(target) >= 2:
            start_xy = (float(start[0]), float(start[1]))
            target_xy = (float(target[0]), float(target[1]))
            start_error = math.dist((rows[0]["x"], rows[0]["y"]), start_xy)
            end_error = math.dist((rows[-1]["x"], rows[-1]["y"]), target_xy)
            direct_distance = math.dist(start_xy, target_xy)
            detour_excess = path_length_m(rows) - direct_distance
            static_hits = [
                obstacle.actor
                for obstacle in flight_obstacles
                if clearance.segment_intersects_rect(
                    start_xy,
                    target_xy,
                    obstacle.rect,
                    float(contract.get("clearance_margin_m") or 0.0),
                )
            ]
        else:
            static_hits = []
            blockers.append(f"uav{uid}_scenario_endpoint_missing")
        expected_names = [str(name) for name in member_hits.get(uid, [])]
        missing_expected = [name for name in expected_names if name not in obstacles_by_name]
        if missing_expected:
            blockers.append(f"uav{uid}_scenario_proxy_missing")
        if expected_names and not set(expected_names).issubset(static_hits):
            blockers.append(f"uav{uid}_static_direct_path_contract_mismatch")
        if start_error is not None and start_error > args.max_execute_start_error_m:
            blockers.append(f"uav{uid}_execute_start_mismatch")
        if end_error is not None and end_error > args.max_execute_end_error_m:
            blockers.append(f"uav{uid}_execute_end_mismatch")
        max_truth_gap_s = max((right["t"] - left["t"] for left, right in zip(rows, rows[1:])), default=0.0)
        if max_truth_gap_s > args.max_truth_gap_s:
            blockers.append(f"uav{uid}_truth_gap_exceeds_gate")
        if violations:
            blockers.append(f"uav{uid}_obstacle_clearance_violation")
            all_violations.extend({"uav": int(uid), **entry} for entry in violations[:20])
        if uid in expected_blocked_uavs and (detour_excess is None or detour_excess < args.min_detour_excess_m):
            blockers.append(f"uav{uid}_detour_not_observed")
        finite_minimums = [
            (actor, distances["axis_linf"], distances["euclidean"])
            for actor, distances in minimums.items()
            if distances["axis_linf"] is not None and distances["euclidean"] is not None
        ]
        nearest_obstacles = [
            {
                "actor": actor,
                "axis_linf_clearance_m": axis_linf,
                "euclidean_clearance_m": euclidean,
            }
            for actor, axis_linf, euclidean in sorted(finite_minimums, key=lambda item: item[1])[:8]
        ]
        per_uav[uid] = {
            "execute_rows": len(rows),
            "resampled_rows": len(samples),
            "max_truth_gap_s": max_truth_gap_s,
            "start_error_m": start_error,
            "end_error_m": end_error,
            "path_length_m": path_length_m(rows),
            "direct_distance_m": direct_distance,
            "detour_excess_m": detour_excess,
            "expected_blocked_proxy_names": expected_names,
            "static_direct_path_proxy_names": static_hits,
            "minimum_axis_linf_clearance_m": min((axis_linf for _, axis_linf, _ in finite_minimums), default=None),
            "minimum_euclidean_clearance_m": min((euclidean for _, _, euclidean in finite_minimums), default=None),
            "expected_proxy_minimum_axis_linf_clearance_m": {
                name: minimums.get(name, {}).get("axis_linf") for name in expected_names
            },
            "expected_proxy_minimum_euclidean_clearance_m": {
                name: minimums.get(name, {}).get("euclidean") for name in expected_names
            },
            "nearest_obstacle_clearances_m": nearest_obstacles,
            "clearance_violation_count": len(violations),
            "clearance_violations": violations[:20],
        }
        direct_contract[uid] = {
            "expected_blocked_proxy_names": expected_names,
            "static_direct_path_proxy_names": static_hits,
        }

    packet = {
        "schema": "mosim.sunray_ros1.swarm_formation_obstacle_clearance_gate.v3",
        "status": "passed" if not blockers else "blocked",
        "blockers": list(dict.fromkeys(blockers)),
        "scenario": str(scenario_path),
        "scene_truth": str(scene_truth_path),
        "planner_clearance_m": args.planner_clearance_m,
        "vertical_margin_m": args.vertical_margin_m,
        "max_segment_sample_m": args.max_segment_sample_m,
        "selected_uav_ids": selected_uav_ids,
        "truth_file_template": args.truth_file_template,
        "execute_phases": sorted(execute_phases),
        "expected_blocked_uavs": expected_blocked_uavs,
        "flight_obstacle_proxy_count": len(flight_obstacles),
        "direct_path_contract": direct_contract,
        "per_uav": per_uav,
        "violation_samples": all_violations,
        "claim_boundary": (
            "Static collision truth is used only as a post-flight clearance oracle. "
            "It is not an input to the live planner or controller; runtime obstacle evidence remains "
            "per-UAV MID360 world-cloud and grid-map publication."
        ),
    }
    output_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(output_path)
    raise SystemExit(0 if not blockers else 1)


if __name__ == "__main__":
    main()
