#!/usr/bin/env python3
"""Audit a Diff-Planner waypoint sequence from recorded Goal4 CSV outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any


DEFAULT_SOURCES = (
    "truth.csv",
    "odom.csv",
    "planner_position_cmd_raw.csv",
    "position_cmd.csv",
)


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def row_xyz(row: dict[str, str]) -> tuple[float, float, float] | None:
    values = [finite_float(row.get(axis)) for axis in ("x", "y", "z")]
    if any(value is None for value in values):
        return None
    return (float(values[0]), float(values[1]), float(values[2]))


def parse_waypoints_arg(value: str) -> list[tuple[float, float, float]]:
    waypoints: list[tuple[float, float, float]] = []
    for item in value.split(";"):
        item = item.strip()
        if not item:
            continue
        parts = [part.strip() for part in item.split(",")]
        if len(parts) < 3:
            raise ValueError(f"waypoint must have at least x,y,z: {item!r}")
        parsed = tuple(float(part) for part in parts[:3])
        waypoints.append((parsed[0], parsed[1], parsed[2]))
    if not waypoints:
        raise ValueError("no waypoints parsed")
    return waypoints


def parse_waypoints_yaml(path: Path, section: str) -> list[tuple[float, float, float]]:
    if not path.exists():
        raise FileNotFoundError(path)
    waypoints: list[tuple[float, float, float]] = []
    in_section = False
    section_re = re.compile(rf"^\s*{re.escape(section)}\s*:\s*$")
    next_section_re = re.compile(r"^\s*[A-Za-z0-9_]+\s*:\s*$")
    waypoint_re = re.compile(r"^\s*-\s*\[([^\]]+)\]\s*(?:#.*)?$")
    for line in path.read_text(encoding="utf-8").splitlines():
        if section_re.match(line):
            in_section = True
            continue
        if in_section and next_section_re.match(line):
            break
        if not in_section:
            continue
        match = waypoint_re.match(line)
        if not match:
            continue
        parts = [part.strip() for part in match.group(1).split(",")]
        if len(parts) < 3:
            continue
        waypoint = tuple(float(part) for part in parts[:3])
        waypoints.append((waypoint[0], waypoint[1], waypoint[2]))
    if not waypoints:
        raise ValueError(f"no waypoints found in section {section!r} of {path}")
    return waypoints


def nearest_ordered_hits(
    rows: list[dict[str, str]],
    waypoints: list[tuple[float, float, float]],
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    search_start = 0
    last_index = -1
    for idx, waypoint in enumerate(waypoints, start=1):
        best: dict[str, Any] | None = None
        for sample_index in range(search_start, len(rows)):
            point = row_xyz(rows[sample_index])
            if point is None:
                continue
            xyz_error = math.dist(point, waypoint)
            xy_error = math.dist(point[:2], waypoint[:2])
            z_error = point[2] - waypoint[2]
            if best is None or xyz_error < best["min_xyz_error_m"]:
                best = {
                    "waypoint_index": idx,
                    "target": list(waypoint),
                    "min_xyz_error_m": xyz_error,
                    "min_xy_error_m": xy_error,
                    "abs_z_error_m": abs(z_error),
                    "z_error_m": z_error,
                    "sample_index": sample_index,
                    "t": finite_float(rows[sample_index].get("t")),
                    "phase": rows[sample_index].get("phase"),
                    "x": point[0],
                    "y": point[1],
                    "z": point[2],
                    "order_ok": sample_index > last_index,
                }
        if best is None:
            hits.append(
                {
                    "waypoint_index": idx,
                    "target": list(waypoint),
                    "missing": True,
                    "order_ok": False,
                }
            )
            continue
        hits.append(best)
        last_index = int(best["sample_index"])
        search_start = last_index + 1
    return hits


def source_threshold(source_name: str, args: argparse.Namespace) -> tuple[float, float]:
    if source_name in {"planner_position_cmd_raw.csv", "position_cmd.csv"}:
        return args.max_cmd_xyz_error_m, args.max_cmd_z_error_m
    return args.max_state_xyz_error_m, args.max_state_z_error_m


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--waypoints", default="")
    parser.add_argument("--waypoint-yaml", default="")
    parser.add_argument("--waypoint-section", default="test1")
    parser.add_argument("--sources", nargs="*", default=list(DEFAULT_SOURCES))
    parser.add_argument("--max-state-xyz-error-m", type=float, default=0.20)
    parser.add_argument("--max-state-z-error-m", type=float, default=0.12)
    parser.add_argument("--max-cmd-xyz-error-m", type=float, default=0.10)
    parser.add_argument("--max-cmd-z-error-m", type=float, default=0.08)
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    output_json = Path(args.output_json) if args.output_json else result_dir / "DIFF_SINGLE_123_WAYPOINT_AUDIT.json"
    if args.waypoints:
        waypoints = parse_waypoints_arg(args.waypoints)
    elif args.waypoint_yaml:
        waypoints = parse_waypoints_yaml(Path(args.waypoint_yaml), args.waypoint_section)
    else:
        waypoints = parse_waypoints_arg("2.0,0.0,1.0;3.0,0.5,1.0;4.0,1.0,1.0")

    blockers: list[str] = []
    warnings: list[str] = []
    source_reports: dict[str, Any] = {}
    for source_name in args.sources:
        rows = read_csv_rows(result_dir / source_name)
        hits = nearest_ordered_hits(rows, waypoints)
        max_xyz, max_z = source_threshold(source_name, args)
        source_blockers: list[str] = []
        if not rows:
            source_blockers.append("source_missing_or_empty")
        for hit in hits:
            if hit.get("missing"):
                source_blockers.append(f"waypoint_{hit['waypoint_index']}_missing")
                continue
            if not hit.get("order_ok"):
                source_blockers.append(f"waypoint_{hit['waypoint_index']}_order")
            if hit["min_xyz_error_m"] > max_xyz:
                source_blockers.append(f"waypoint_{hit['waypoint_index']}_xyz_error")
            if hit["abs_z_error_m"] > max_z:
                source_blockers.append(f"waypoint_{hit['waypoint_index']}_z_error")
        if source_blockers:
            blockers.extend(f"{source_name}:{item}" for item in source_blockers)
        source_reports[source_name] = {
            "rows": len(rows),
            "thresholds": {
                "max_xyz_error_m": max_xyz,
                "max_z_error_m": max_z,
            },
            "waypoint_hits": hits,
            "blockers": source_blockers,
        }
        if rows and len(rows) < len(waypoints):
            warnings.append(f"{source_name}:few_rows")

    output = {
        "schema": "mosim.sunray_ros1.diff_waypoint_audit.v1",
        "result_dir": str(result_dir),
        "waypoints": [list(point) for point in waypoints],
        "sources": source_reports,
        "status": "passed" if not blockers else "blocked",
        "blockers": blockers,
        "warnings": warnings,
    }
    output_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(output_json)
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
