#!/usr/bin/env python3
"""Analyze FUEL selected viewpoints versus committed local goals.

This is an offline diagnostic helper for Factory L2 FUEL coverage work. It
parses the planner log and reports whether low coverage is caused by startup
failure, frontier starvation, far-goal truncation, or narrow committed motion.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from statistics import median
from typing import Any


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
FLOAT = r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?"


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"samples": 0}
    ordered = sorted(values)
    return {
        "samples": len(values),
        "min": ordered[0],
        "max": ordered[-1],
        "mean": sum(values) / len(values),
        "median": median(values),
        "p95": ordered[min(len(ordered) - 1, int(math.ceil(0.95 * len(ordered))) - 1)],
        "first": values[0],
        "last": values[-1],
    }


def xy_dist(a: dict[str, float], b: dict[str, float]) -> float:
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def xyz_dist(a: dict[str, float], b: dict[str, float]) -> float:
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2)


def parse_point(text: str, prefix: str) -> dict[str, float] | None:
    m = re.search(prefix + rf"=\(({FLOAT}), ({FLOAT}), ({FLOAT})\)", text)
    if not m:
        return None
    return {"x": float(m.group(1)), "y": float(m.group(2)), "z": float(m.group(3))}


def parse_log(log_path: Path) -> dict[str, Any]:
    next_view_re = re.compile(rf"Next view:\s*({FLOAT})\s+({FLOAT})\s+({FLOAT}),\s*({FLOAT})")
    span_after_re = re.compile(
        rf"span_after_goal x=\[({FLOAT}), ({FLOAT})\] y=\[({FLOAT}), ({FLOAT})\] "
        rf"selected=\(({FLOAT}), ({FLOAT}), ({FLOAT})\) "
        rf"committed_goal=\(({FLOAT}), ({FLOAT}), ({FLOAT})\)"
    )
    candidate_pool_re = re.compile(
        rf"candidate_pool n=(\d+) pos=\(({FLOAT}), ({FLOAT}), ({FLOAT})\) "
        rf"view_x=\[({FLOAT}), ({FLOAT})\] view_y=\[({FLOAT}), ({FLOAT})\]"
    )
    frontier_re = re.compile(r"Frontier:\s*(\d+).*?viewpoint:\s*(\d+)")
    replan_re = re.compile(r"Replan:\s*([^=]+)")

    next_views: list[dict[str, float]] = []
    committed: list[dict[str, Any]] = []
    candidate_pools: list[dict[str, float]] = []
    frontier_counts: list[float] = []
    viewpoint_counts: list[float] = []
    replan_reasons: dict[str, int] = {}
    far_goal_count = 0
    mid_goal_count = 0
    no_frontier_count = 0
    no_path_count = 0

    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = ANSI_RE.sub("", raw).strip()
            if not line:
                continue
            m = next_view_re.search(line)
            if m:
                next_views.append(
                    {
                        "x": float(m.group(1)),
                        "y": float(m.group(2)),
                        "z": float(m.group(3)),
                        "yaw": float(m.group(4)),
                    }
                )
            m = span_after_re.search(line)
            if m:
                selected = {"x": float(m.group(5)), "y": float(m.group(6)), "z": float(m.group(7))}
                goal = {"x": float(m.group(8)), "y": float(m.group(9)), "z": float(m.group(10))}
                committed.append(
                    {
                        "span_x_min": float(m.group(1)),
                        "span_x_max": float(m.group(2)),
                        "span_y_min": float(m.group(3)),
                        "span_y_max": float(m.group(4)),
                        "selected": selected,
                        "committed": goal,
                        "selected_to_committed_xy_m": xy_dist(selected, goal),
                        "selected_to_committed_xyz_m": xyz_dist(selected, goal),
                    }
                )
            m = candidate_pool_re.search(line)
            if m:
                candidate_pools.append(
                    {
                        "n": float(m.group(1)),
                        "pos_x": float(m.group(2)),
                        "pos_y": float(m.group(3)),
                        "pos_z": float(m.group(4)),
                        "view_x_min": float(m.group(5)),
                        "view_x_max": float(m.group(6)),
                        "view_y_min": float(m.group(7)),
                        "view_y_max": float(m.group(8)),
                    }
                )
            m = frontier_re.search(line)
            if m:
                frontier_counts.append(float(m.group(1)))
                viewpoint_counts.append(float(m.group(2)))
            m = replan_re.search(line)
            if m:
                key = m.group(1).strip()
                replan_reasons[key] = replan_reasons.get(key, 0) + 1
            if "Far goal" in line:
                far_goal_count += 1
            elif "Mid goal" in line:
                mid_goal_count += 1
            if "No coverable frontier" in line:
                no_frontier_count += 1
            if "No path to next viewpoint" in line or "No path" in line:
                no_path_count += 1

    committed_steps = [
        xy_dist(prev["committed"], cur["committed"]) for prev, cur in zip(committed, committed[1:])
    ]
    selected_steps = [
        xy_dist(prev, cur) for prev, cur in zip(next_views, next_views[1:])
    ]
    committed_bounds: dict[str, Any] = {"samples": len(committed)}
    if committed:
        xs = [row["committed"]["x"] for row in committed]
        ys = [row["committed"]["y"] for row in committed]
        zs = [row["committed"]["z"] for row in committed]
        committed_bounds.update(
            {
                "x_min": min(xs),
                "x_max": max(xs),
                "x_range_m": max(xs) - min(xs),
                "y_min": min(ys),
                "y_max": max(ys),
                "y_range_m": max(ys) - min(ys),
                "z_min": min(zs),
                "z_max": max(zs),
                "z_range_m": max(zs) - min(zs),
                "first": committed[0]["committed"],
                "last": committed[-1]["committed"],
            }
        )

    candidate_summary: dict[str, Any] = {"samples": len(candidate_pools)}
    if candidate_pools:
        candidate_summary.update(
            {
                "candidate_count": stats([row["n"] for row in candidate_pools]),
                "last": candidate_pools[-1],
                "last_view_width": {
                    "x_m": candidate_pools[-1]["view_x_max"] - candidate_pools[-1]["view_x_min"],
                    "y_m": candidate_pools[-1]["view_y_max"] - candidate_pools[-1]["view_y_min"],
                },
            }
        )

    return {
        "schema": "mosim.factory_l2.fuel_committed_goal_log_analysis.v1",
        "log_path": str(log_path),
        "counts": {
            "next_view": len(next_views),
            "committed_goal": len(committed),
            "far_goal": far_goal_count,
            "mid_goal": mid_goal_count,
            "no_coverable_frontier": no_frontier_count,
            "no_path": no_path_count,
        },
        "frontier": {
            "frontier_counts": stats(frontier_counts),
            "viewpoint_counts": stats(viewpoint_counts),
        },
        "candidate_pool": candidate_summary,
        "selected_to_committed_xy_m": stats([row["selected_to_committed_xy_m"] for row in committed]),
        "selected_to_committed_xyz_m": stats([row["selected_to_committed_xyz_m"] for row in committed]),
        "committed_goal_step_xy_m": stats(committed_steps),
        "selected_view_step_xy_m": stats(selected_steps),
        "committed_goal_bounds": committed_bounds,
        "replan_reasons": replan_reasons,
        "interpretation": {
            "frontier_starvation": len(frontier_counts) > 0 and no_frontier_count > 0,
            "all_goals_truncated": len(committed) > 0 and far_goal_count == len(committed),
            "dominant_replan_reason": max(replan_reasons.items(), key=lambda item: item[1])[0]
            if replan_reasons
            else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    log_path = args.run_dir / "ego_single_px4ctrl_goal4.log"
    if not log_path.exists():
        raise SystemExit(f"missing log: {log_path}")
    result = parse_log(log_path)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out + "\n", encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
