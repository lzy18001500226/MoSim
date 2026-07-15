#!/usr/bin/env python3
"""Build a Factory L2 FUEL suitability decision packet from completed runs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path outside MoSim workspace: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def nested(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def count_log_patterns(path: Path) -> dict[str, int]:
    log_path = path / "ego_single_px4ctrl_goal4.log"
    if not log_path.is_file():
        return {}
    text = log_path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "open_set_empty": r"open set empty",
        "search_fail": r"search\s+\d+\s+fail",
        "kino_no_path": r"Kino replan.*Can't find path",
        "plan_fail": r"plan fail",
        "frontier_reports": r"Frontier:",
        "fsm_plan_traj": r"state:\s+PLAN_TRAJ",
        "fsm_exec_traj": r"state:\s+EXEC_TRAJ",
    }
    return {key: len(re.findall(pattern, text, flags=re.IGNORECASE)) for key, pattern in patterns.items()}


def summarize_run(path: Path) -> dict[str, Any]:
    metrics = load_json(path / "EGO_SINGLE_METRICS.json")
    manifest = load_json(path / "RUN_MANIFEST.json")
    counts = metrics.get("counts") if isinstance(metrics.get("counts"), dict) else {}
    max_points = metrics.get("max_point_counts") if isinstance(metrics.get("max_point_counts"), dict) else {}
    last_points = metrics.get("last_point_counts") if isinstance(metrics.get("last_point_counts"), dict) else {}
    fuel = manifest.get("fuel") if isinstance(manifest.get("fuel"), dict) else {}
    target = manifest.get("target") if isinstance(manifest.get("target"), dict) else {}
    exploration = metrics.get("exploration") if isinstance(metrics.get("exploration"), dict) else {}
    phase = metrics.get("phase_peak_summary") if isinstance(metrics.get("phase_peak_summary"), dict) else {}
    truth_explore = nested(phase, "truth", "exploration_execute")
    if not isinstance(truth_explore, dict):
        truth_explore = {}
    return {
        "run_id": path.name,
        "path": rel(path),
        "status": metrics.get("status"),
        "blockers": metrics.get("blockers", []),
        "world_file": manifest.get("world_file"),
        "target": {
            "x": target.get("x"),
            "y": target.get("y"),
            "z": target.get("z"),
        },
        "fuel": {
            "map_size": fuel.get("map_size"),
            "grid_resolution_m": fuel.get("grid_resolution_m"),
            "ray_model": fuel.get("ray_model"),
            "frontier": fuel.get("frontier"),
            "box_min": fuel.get("box_min"),
            "box_max": fuel.get("box_max"),
            "frame_bridge": fuel.get("frame_bridge"),
        },
        "counts": {
            "raw_lidar": counts.get("raw_lidar"),
            "world_cloud": counts.get("world_cloud"),
            "occupancy": counts.get("occupancy_inflate"),
            "bspline": counts.get("bspline"),
            "planner_position_cmd": counts.get("planner_position_cmd"),
        },
        "point_counts": {
            "occupancy_last": metrics.get("occupancy_last_points"),
            "occupancy_max": max_points.get("occupancy_inflate"),
            "raw_lidar_last": last_points.get("raw_lidar"),
            "world_cloud_last": last_points.get("world_cloud"),
        },
        "exploration": {
            "duration_s": exploration.get("duration_s"),
            "truth_z_min": truth_explore.get("min_z_m"),
            "truth_z_max": truth_explore.get("max_z_m"),
            "truth_max_speed_mps": truth_explore.get("max_speed_mps"),
            "truth_max_roll_pitch_deg": truth_explore.get("max_abs_roll_pitch_deg"),
        },
        "log_patterns": count_log_patterns(path),
    }


def classify(rows: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not rows:
        return "blocked_no_runs", ["no_completed_fuel_tile_runs"], warnings

    passed = [row for row in rows if row.get("status") == "passed" and not row.get("blockers")]
    blocked = [row for row in rows if row not in passed]
    search_fail_runs = [
        row["run_id"]
        for row in rows
        if int(nested(row, "log_patterns", "open_set_empty") or 0) > 0
        or int(nested(row, "log_patterns", "search_fail") or 0) > 0
        or int(nested(row, "log_patterns", "kino_no_path") or 0) > 0
    ]
    zero_occ_runs = [
        row["run_id"]
        for row in rows
        if number(nested(row, "point_counts", "occupancy_max")) == 0
        or number(nested(row, "point_counts", "occupancy_last")) == 0
    ]
    no_bspline_runs = [row["run_id"] for row in rows if number(nested(row, "counts", "bspline")) == 0]

    pass_ratio = len(passed) / len(rows)
    if pass_ratio < 0.5:
        blockers.append("representative_tile_pass_ratio_below_50_percent")
    if search_fail_runs:
        blockers.append("fuel_kino_search_failed_in_representative_tile")
    if zero_occ_runs:
        blockers.append("fuel_occupancy_empty_or_zero_in_representative_tile")
    if no_bspline_runs:
        blockers.append("fuel_bspline_absent_in_representative_tile")

    if blockers:
        status = "not_suitable_as_factory_full_map_primary"
    elif blocked:
        status = "needs_more_tile_diagnosis"
        warnings.append("some_representative_tiles_blocked")
    else:
        status = "candidate_for_factory_tile_sweep"

    if passed:
        warnings.append("passed_tiles_remain_local_plumbing_evidence_not_coverage")
    return status, blockers, warnings


def write_summary(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Factory L2 FUEL Suitability Decision",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Decision",
        "",
        packet["decision"],
        "",
        "## Evidence",
        "",
    ]
    for row in packet["runs"]:
        counts = row["counts"]
        points = row["point_counts"]
        patterns = row["log_patterns"]
        lines.append(
            "- `{}`: status={}, blockers={}, bspline={}, planner_cmd={}, "
            "raw_lidar={}, world_cloud={}, occ_last={}, occ_max={}, "
            "open_set_empty={}, search_fail={}".format(
                row["run_id"],
                row["status"],
                row.get("blockers", []),
                counts.get("bspline"),
                counts.get("planner_position_cmd"),
                counts.get("raw_lidar"),
                counts.get("world_cloud"),
                points.get("occupancy_last"),
                points.get("occupancy_max"),
                patterns.get("open_set_empty", 0),
                patterns.get("search_fail", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Next Route",
            "",
            "- Keep FUEL as a local single-UAV exploration/plumbing baseline.",
            "- Do not spend runtime on a monolithic all-map FUEL run for Factory L2.",
            "- Use RACER as the active multi-UAV autonomous exploration baseline.",
            "- Keep Diff single/multi fixed-goal regression for known-target navigation checks.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="Results/sunray_ros1/factory_l2_fuel_suitability_decision_20260703",
    )
    parser.add_argument("runs", nargs="+")
    args = parser.parse_args()

    run_dirs = [repo_path(item) for item in args.runs]
    rows = [summarize_run(path) for path in run_dirs]
    status, blockers, warnings = classify(rows)
    decision = (
        "FUEL is not suitable as the primary Factory L2 full-map autonomous "
        "exploration route based on the current representative clean-map tile "
        "evidence. It remains useful as a local single-UAV exploration/plumbing "
        "baseline."
        if status == "not_suitable_as_factory_full_map_primary"
        else "FUEL needs additional Factory L2 tile diagnosis before promotion."
    )
    packet = {
        "schema": "mosim.factory_l2_fuel_suitability_decision.v1",
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "decision": decision,
        "claim_boundary": [
            "This packet decides FUEL suitability for Factory L2 full-map exploration from completed clean-map tile evidence.",
            "It does not judge RACER suitability.",
            "It does not change the accepted clean Factory coordinate or Z policy.",
            "It does not claim quantitative full-boundary coverage.",
        ],
        "minimum_promotion_requirements": [
            "representative tile pass ratio >= 50 percent before any full tile sweep",
            "nonempty raw lidar and world cloud",
            "nonempty occupancy output at the end of exploration",
            "nonzero bspline and planner position command output",
            "no open set empty, search fail, or Kino no-path events in representative tiles",
            "truth Z remains inside the fixed command band",
        ],
        "runs": rows,
    }

    out_dir = repo_path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "FACTORY_L2_FUEL_SUITABILITY_DECISION.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )
    write_summary(out_dir / "SUMMARY.md", packet)
    print(json.dumps({"status": status, "output_dir": rel(out_dir), "blockers": blockers}, ensure_ascii=False))
    return 0 if status else 1


if __name__ == "__main__":
    raise SystemExit(main())
