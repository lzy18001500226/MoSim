"""Verify Factory L2 Diff-Swarm target arrival and dwell from runtime artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def workspace_path(value: Path) -> Path:
    path = value if value.is_absolute() else ROOT / value
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path outside MoSim workspace: {value}")
    return resolved


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def number(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric, got {value!r}") from exc


def vector(value: Any, field: str) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{field} must be a three-element vector")
    return tuple(number(item, field) for item in value)


def read_odom_rows(path: Path) -> list[dict[str, float]]:
    required = ("t", "x", "y", "z", "vx", "vy", "vz")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or any(field not in reader.fieldnames for field in required):
            raise ValueError(f"odom CSV is missing required columns: {path}")
        rows: list[dict[str, float]] = []
        for index, row in enumerate(reader, start=2):
            try:
                rows.append({field: number(row[field], f"{path.name}:{index}:{field}") for field in required})
            except KeyError as exc:
                raise ValueError(f"odom CSV field missing at {path}:{index}: {exc}") from exc
    if not rows:
        raise ValueError(f"odom CSV has no data rows: {path}")
    return rows


def row_metrics(row: dict[str, float], target: tuple[float, float, float]) -> tuple[float, float, float]:
    error = math.dist((row["x"], row["y"], row["z"]), target)
    speed = math.sqrt(row["vx"] ** 2 + row["vy"] ** 2 + row["vz"] ** 2)
    return error, speed, abs(row["vz"])


def snapshot_passes(snapshot: Any, radius_m: float, max_speed_mps: float, max_vz_mps: float) -> bool:
    if not isinstance(snapshot, dict):
        return False
    try:
        error = number(snapshot.get("error_xyz_m"), "snapshot.error_xyz_m")
        speed = number(snapshot.get("speed_mps"), "snapshot.speed_mps")
        abs_vz = number(snapshot.get("abs_vz_mps"), "snapshot.abs_vz_mps")
    except ValueError:
        return False
    return error <= radius_m + 1e-6 and speed <= max_speed_mps + 1e-6 and abs_vz <= max_vz_mps + 1e-6


def csv_data_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def audit_target(
    round_index: int,
    uav: str,
    target_value: Any,
    hold: Any,
    odom_rows: list[dict[str, float]],
    min_target_hold_s: float,
) -> dict[str, Any]:
    if not isinstance(hold, dict):
        raise ValueError(f"round {round_index} {uav} target hold is missing")
    target = vector(target_value, f"round {round_index} {uav} target")
    required_s = number(hold.get("required_s"), f"round {round_index} {uav} required_s")
    recorded_duration_s = number(hold.get("duration_s"), f"round {round_index} {uav} duration_s")
    hold_start_t = number(hold.get("hold_start_t"), f"round {round_index} {uav} hold_start_t")
    hold_end_t = number(hold.get("hold_end_t"), f"round {round_index} {uav} hold_end_t")
    radius_m = number(hold.get("radius_m"), f"round {round_index} {uav} radius_m")
    max_speed_mps = number(hold.get("max_speed_mps"), f"round {round_index} {uav} max_speed_mps")
    max_vz_mps = number(hold.get("max_vz_mps"), f"round {round_index} {uav} max_vz_mps")
    observed_duration_s = max(0.0, hold_end_t - hold_start_t)
    interval_rows = [row for row in odom_rows if hold_start_t <= row["t"] <= hold_end_t]
    interval_metrics = [row_metrics(row, target) for row in interval_rows]
    strict_rows_passed = bool(interval_metrics) and all(
        error <= radius_m + 1e-6 and speed <= max_speed_mps + 1e-6 and abs_vz <= max_vz_mps + 1e-6
        for error, speed, abs_vz in interval_metrics
    )
    first_snapshot = hold.get("first_reached_snapshot")
    end_snapshot = hold.get("end_snapshot")
    checks = {
        "reached": hold.get("reached") is True,
        "simulation_time_basis": hold.get("duration_time_basis") == "ros_simulation_time",
        "configured_dwell_at_least_minimum": required_s >= min_target_hold_s,
        "observed_dwell_at_least_required": observed_duration_s + 1e-6 >= required_s,
        "recorded_duration_matches_interval": abs(recorded_duration_s - observed_duration_s) <= 0.02,
        "first_arrival_snapshot": snapshot_passes(first_snapshot, radius_m, max_speed_mps, max_vz_mps),
        "end_snapshot": snapshot_passes(end_snapshot, radius_m, max_speed_mps, max_vz_mps),
        "raw_odom_interval": strict_rows_passed,
        "round_index_matches": hold.get("chain_round_index") == round_index,
    }
    return {
        "round_index": round_index,
        "uav": uav,
        "target_world_m": list(target),
        "passed": all(checks.values()),
        "checks": checks,
        "target_hold": {
            "required_s": required_s,
            "observed_s": observed_duration_s,
            "recorded_s": recorded_duration_s,
            "radius_m": radius_m,
            "max_speed_mps": max_speed_mps,
            "max_vz_mps": max_vz_mps,
            "time_basis": hold.get("duration_time_basis"),
            "first_error_m": None if not isinstance(first_snapshot, dict) else first_snapshot.get("error_xyz_m"),
            "end_error_m": None if not isinstance(end_snapshot, dict) else end_snapshot.get("error_xyz_m"),
        },
        "raw_odom_interval": {
            "samples": len(interval_rows),
            "max_error_m": max((item[0] for item in interval_metrics), default=None),
            "max_speed_mps": max((item[1] for item in interval_metrics), default=None),
            "max_abs_vz_mps": max((item[2] for item in interval_metrics), default=None),
        },
        "end_snapshot": end_snapshot,
    }


def endpoint(snapshot: Any) -> tuple[float, float, float]:
    if not isinstance(snapshot, dict):
        raise ValueError("target hold end snapshot is missing")
    return tuple(number(snapshot.get(axis), f"end_snapshot.{axis}") for axis in ("x", "y", "z"))


def build_audit(run_dir: Path, min_target_hold_s: float, min_route_motion_m: float) -> dict[str, Any]:
    chain_path = run_dir / "SWARM_TARGET_CHAIN_PROBE.json"
    metrics_path = run_dir / "EGO_SWARM_METRICS.json"
    probe_path = run_dir / "FACTORY_L2_DIFF_SWARM_COVERAGE_PROBE.json"
    for path in (chain_path, metrics_path, probe_path):
        if not path.is_file():
            raise ValueError(f"required runtime artifact is missing: {relative_path(path)}")
    chain = load_object(chain_path)
    metrics = load_object(metrics_path)
    probe = load_object(probe_path)
    rounds = chain.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        raise ValueError("target-chain rounds are missing")

    odom_cache: dict[str, list[dict[str, float]]] = {}
    raw_command_rows: dict[str, int] = {}
    per_target: list[dict[str, Any]] = []
    endpoint_history: dict[str, list[tuple[float, float, float]]] = {}
    for round_item in rounds:
        if not isinstance(round_item, dict):
            raise ValueError("target-chain round is not an object")
        round_index = int(round_item.get("round_index", 0))
        targets = round_item.get("targets")
        holds = round_item.get("target_holds")
        if not isinstance(targets, dict) or not isinstance(holds, dict):
            raise ValueError(f"round {round_index} is missing targets or target_holds")
        for uav, target in targets.items():
            if uav not in odom_cache:
                odom_path = run_dir / f"{uav}_odom.csv"
                raw_command_path = run_dir / f"{uav}_raw_position_cmd.csv"
                if not odom_path.is_file() or not raw_command_path.is_file():
                    raise ValueError(f"runtime CSV artifacts are missing for {uav}")
                odom_cache[uav] = read_odom_rows(odom_path)
                raw_command_rows[uav] = csv_data_row_count(raw_command_path)
            record = audit_target(round_index, uav, target, holds.get(uav), odom_cache[uav], min_target_hold_s)
            per_target.append(record)
            endpoint_history.setdefault(uav, []).append(endpoint(record["end_snapshot"]))

    route_motion = {}
    for uav, points in sorted(endpoint_history.items()):
        target_points = [record["target_world_m"] for record in per_target if record["uav"] == uav]
        target_path_m = sum(math.dist(tuple(left), tuple(right)) for left, right in zip(target_points, target_points[1:]))
        endpoint_path_m = sum(math.dist(left, right) for left, right in zip(points, points[1:]))
        route_motion[uav] = {
            "held_target_count": len(points),
            "unique_targets": len({tuple(point) for point in target_points}),
            "target_path_m": target_path_m,
            "observed_endpoint_path_m": endpoint_path_m,
            "passed": len(points) >= 2 and endpoint_path_m >= min_route_motion_m,
        }

    landing = metrics.get("landing") if isinstance(metrics.get("landing"), dict) else {}
    chain_lengths = chain.get("chain_lengths") if isinstance(chain.get("chain_lengths"), dict) else {}
    checks = {
        "launcher_exit": probe.get("backend_exit_code") == 0,
        "target_chain_status": chain.get("status") == "passed",
        "round_statuses": all(item.get("status") == "passed" for item in rounds if isinstance(item, dict)),
        "all_target_arrival_and_dwell": bool(per_target) and all(item["passed"] for item in per_target),
        "multi_target_route": bool(route_motion) and all(item["passed"] for item in route_motion.values()) and all(
            int(value) >= 2 for value in chain_lengths.values()
        ),
        "raw_planner_commands": bool(raw_command_rows) and all(count >= 10 for count in raw_command_rows.values()),
        "mission_metrics": metrics.get("status") == "passed" and not metrics.get("blockers"),
        "controlled_landing": landing.get("completed") is True
        and landing.get("exit_reason") == "all_uavs_landed_and_disarmed",
    }
    return {
        "schema": "mosim.sunray_ros1.factory_l2_diff_swarm_target_chain_arrival_dwell_audit.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "passed" if all(checks.values()) else "blocked",
        "checks": checks,
        "source_run": {
            "result_dir": relative_path(run_dir),
            "probe": relative_path(probe_path),
            "target_chain": relative_path(chain_path),
            "metrics": relative_path(metrics_path),
        },
        "acceptance": {
            "minimum_target_hold_s": min_target_hold_s,
            "minimum_route_motion_m": min_route_motion_m,
            "target_count": len(per_target),
            "chain_lengths": chain_lengths,
            "raw_planner_command_rows": raw_command_rows,
            "minimum_inter_uav_distance_m": metrics.get("min_inter_uav_distance_m"),
            "inter_uav_emergency_events": (metrics.get("inter_uav_emergency_hold") or {}).get("events", []),
            "landing": landing,
        },
        "per_target": per_target,
        "route_motion": route_motion,
        "claim_boundary": {
            "proves": "A bounded Factory L2 three-UAV Diff-Planner target-chain run reached and dwelled at every recorded target using ROS simulation time and recorded MAVROS odometry.",
            "does_not_prove": "Unknown autonomous exploration, full-factory coverage, visual RViz acceptance, generalized swarm safety, MWORKS acceptance, or hardware flight performance.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-target-hold-s", type=float, default=5.0)
    parser.add_argument("--min-route-motion-m", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = workspace_path(args.run_dir)
    if not run_dir.is_dir():
        raise SystemExit(f"run directory is missing: {run_dir}")
    output = workspace_path(args.output) if args.output else run_dir / "TARGET_CHAIN_ARRIVAL_DWELL_AUDIT.json"
    audit = build_audit(run_dir, args.min_target_hold_s, args.min_route_motion_m)
    output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(relative_path(output))
    print(audit["status"])
    return 0 if audit["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
