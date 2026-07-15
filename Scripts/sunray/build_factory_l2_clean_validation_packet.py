#!/usr/bin/env python3
"""Build a unified Factory L2 clean-map backend validation packet."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENVELOPE = ROOT / "Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"

DEFAULT_RUNS = {
    "single_uav_fuel_local": ROOT
    / "Results/sunray_ros1/factory_l2_f5c_fuel_tile_summary_20260703/FACTORY_L2_FUEL_TILE_SUMMARY.json",
    "multi_uav_racer_exploration": ROOT
    / "Results/sunray_ros1/factory_l2_f5c3_racer_swarm_clean_staggered_range35_fix_20260703_0605",
    "single_uav_diff_fixed_goal": ROOT
    / "Results/sunray_ros1/factory_l2_clean_diff_single_directgoal_allowocc_",
    "multi_uav_diff_fixed_goal": ROOT
    / "Results/sunray_ros1/factory_l2_clean_diff_swarm_3uav_direct_20260703_0707",
}


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_first_existing(base: Path, names: list[str]) -> Path | None:
    for name in names:
        path = base / name
        if path.exists():
            return path
    return None


def metric_file(base: Path) -> Path | None:
    return find_first_existing(base, ["EGO_SWARM_METRICS.json", "EGO_SINGLE_METRICS.json"])


def load_metric_summary(base: Path) -> dict[str, Any]:
    metric_path = metric_file(base)
    manifest_path = base / "RUN_MANIFEST.json"
    inputs_path = base / "RUN_INPUTS.json"
    audit_path = base / "planner_runtime_log_audit.json"
    metric = read_json(metric_path) if metric_path else {}
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    inputs = read_json(inputs_path) if inputs_path.exists() else {}
    audit = read_json(audit_path) if audit_path.exists() else {}
    return {
        "result_dir": rel(base),
        "metric_path": rel(metric_path) if metric_path else None,
        "manifest_path": rel(manifest_path) if manifest_path.exists() else None,
        "inputs_path": rel(inputs_path) if inputs_path.exists() else None,
        "status": metric.get("status"),
        "blockers": metric.get("blockers", []),
        "mission_exit_code": manifest.get("mission_exit_code", metric.get("mission_exit_code")),
        "world_file": manifest.get("world_file") or inputs.get("world_file"),
        "planner_variant": manifest.get("planner_variant") or inputs.get("planner_variant"),
        "controller_core_profile": manifest.get("controller_core_profile"),
        "execute_target_error_m": metric.get("execute_target_error_m"),
        "min_inter_uav_distance_m": metric.get("min_inter_uav_distance_m"),
        "runtime_log_audit": metric.get("runtime_log_audit") or audit,
    }


def read_truth_bounds(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []

    def get_float(row: dict[str, str], names: list[str]) -> float | None:
        for name in names:
            value = row.get(name)
            if value not in (None, ""):
                try:
                    return float(value)
                except ValueError:
                    return None
        return None

    with path.open(newline="", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            x = get_float(row, ["x", "position.x", "pose.position.x"])
            y = get_float(row, ["y", "position.y", "pose.position.y"])
            z = get_float(row, ["z", "position.z", "pose.position.z"])
            if x is None or y is None or z is None:
                continue
            xs.append(x)
            ys.append(y)
            zs.append(z)
    if not xs:
        return None
    return {
        "samples": len(xs),
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "min_z": min(zs),
        "max_z": max(zs),
    }


def truth_bounds_for_run(base: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    single = read_truth_bounds(base / "truth.csv")
    if single:
        out["uav1"] = single
    for uid in (1, 2, 3):
        bounds = read_truth_bounds(base / f"uav{uid}_truth.csv")
        if bounds:
            out[f"uav{uid}"] = bounds
    return out


def check_bounds(
    truth: dict[str, Any],
    boundary: dict[str, float],
    z_policy: dict[str, float],
    xy_tolerance_m: float,
    z_tolerance_m: float,
) -> dict[str, Any]:
    per_uav: dict[str, Any] = {}
    violations: list[str] = []
    for uav, values in truth.items():
        xy_ok = (
            values["min_x"] >= boundary["min_x_m"] - xy_tolerance_m
            and values["max_x"] <= boundary["max_x_m"] + xy_tolerance_m
            and values["min_y"] >= boundary["min_y_m"] - xy_tolerance_m
            and values["max_y"] <= boundary["max_y_m"] + xy_tolerance_m
        )
        # Include takeoff/landing in the recorded truth bounds. Low Z during
        # ground phases is expected, so only enforce upper command safety here.
        z_upper_ok = values["max_z"] <= z_policy["max_cmd_z_m"] + z_tolerance_m
        if not xy_ok:
            violations.append(f"{uav}:xy_outside_boundary")
        if not z_upper_ok:
            violations.append(f"{uav}:z_above_policy")
        per_uav[uav] = {
            **values,
            "xy_inside_boundary": xy_ok,
            "z_upper_inside_policy": z_upper_ok,
        }
    return {"per_uav": per_uav, "violations": violations}


def build_packet(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    envelope = read_json(args.envelope)
    boundary = envelope["exploration_boundary"]
    z_policy = envelope["z_policy"]
    clean_world = (ROOT / envelope["world_path"]).resolve()
    clean_world_posix = clean_world.as_posix()

    runs: dict[str, Any] = {}

    fuel_summary = read_json(args.single_uav_fuel_local)
    runs["single_uav_fuel_local"] = {
        "source": rel(args.single_uav_fuel_local),
        "status": fuel_summary.get("status"),
        "claim_boundary": "local/tiled single-UAV FUEL evidence only; not full Factory coverage",
        "passed_runs": sum(1 for item in fuel_summary.get("runs", []) if item.get("status") == "passed"),
        "blocked_runs": sum(1 for item in fuel_summary.get("runs", []) if item.get("status") != "passed"),
        "runs": fuel_summary.get("runs", []),
    }

    for key in (
        "multi_uav_racer_exploration",
        "single_uav_diff_fixed_goal",
        "multi_uav_diff_fixed_goal",
    ):
        base = getattr(args, key)
        summary = load_metric_summary(base)
        truth = truth_bounds_for_run(base)
        bounds = check_bounds(
            truth,
            boundary,
            z_policy,
            args.xy_tolerance_m,
            args.z_tolerance_m,
        )
        summary["truth_bounds"] = bounds
        summary["world_is_clean_factory"] = (
            bool(summary.get("world_file"))
            and Path(str(summary["world_file"]).replace("/mnt/c/Users/HP/Desktop/MoSim", str(ROOT))).resolve()
            == clean_world
        )
        runs[key] = summary

    blockers: list[str] = []
    review_warnings: list[str] = []

    if runs["single_uav_fuel_local"]["status"] != "passed_representative_tiles_only":
        blockers.append("single_uav_fuel_local_summary_not_accepted")
    review_warnings.append("single_uav_fuel_is_local_tiled_evidence_not_full_boundary_coverage")

    for key in (
        "multi_uav_racer_exploration",
        "single_uav_diff_fixed_goal",
        "multi_uav_diff_fixed_goal",
    ):
        item = runs[key]
        if item.get("status") != "passed":
            blockers.append(f"{key}:status_not_passed")
        if item.get("blockers"):
            blockers.append(f"{key}:blockers_present")
        if item.get("mission_exit_code") not in (0, "0"):
            blockers.append(f"{key}:mission_exit_code_nonzero")
        if not item.get("world_is_clean_factory"):
            blockers.append(f"{key}:world_not_clean_factory")
        for violation in item.get("truth_bounds", {}).get("violations", []):
            blockers.append(f"{key}:{violation}")
        audit = item.get("runtime_log_audit") or {}
        if isinstance(audit, dict) and audit.get("fatal_event_count", 0):
            blockers.append(f"{key}:fatal_runtime_events")

    status = "review_ready_with_limitations" if not blockers else "blocked"
    packet = {
        "schema": "mosim.factory_l2_clean_runtime_validation_packet.v1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "blockers": blockers,
        "review_warnings": review_warnings,
        "claim_boundary": [
            "Clean Factory L2 is the active runtime validation scene.",
            "FUEL currently proves only local/tiled single-UAV exploration plumbing.",
            "RACER currently proves three-UAV autonomous exploration smoke on the clean Factory scene.",
            "Diff single/multi fixed-goal runs prove fixed-target navigation, not autonomous coverage.",
            "UE is display/review only and must cite these backend run ids.",
        ],
        "envelope": {
            "profile": rel(args.envelope),
            "world_path": envelope["world_path"],
            "clean_world_abs": clean_world_posix,
            "gazebo_model_path": envelope["gazebo_model_path"],
            "boundary": boundary,
            "z_policy": z_policy,
        },
        "runs": runs,
        "next_review_action": (
            "Open RViz/UE visual review tied to the listed clean-Factory run ids."
            if not blockers
            else "Do not open visual review; fix or classify the listed blockers first."
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = args.output_dir / "FACTORY_L2_CLEAN_RUNTIME_VALIDATION.json"
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary(args.output_dir / "SUMMARY.md", packet)
    return packet_path, packet


def write_summary(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Factory L2 Clean Runtime Validation",
        "",
        f"status: `{packet['status']}`",
        "",
        "## Boundary",
        "",
        f"- world: `{packet['envelope']['world_path']}`",
        f"- x: `{packet['envelope']['boundary']['min_x_m']}` to `{packet['envelope']['boundary']['max_x_m']}` m",
        f"- y: `{packet['envelope']['boundary']['min_y_m']}` to `{packet['envelope']['boundary']['max_y_m']}` m",
        f"- z command: `{packet['envelope']['z_policy']['min_cmd_z_m']}` to `{packet['envelope']['z_policy']['max_cmd_z_m']}` m",
        "",
        "## Gates",
        "",
        "| Gate | Status | Key Metric | Evidence |",
        "|---|---|---|---|",
    ]
    fuel = packet["runs"]["single_uav_fuel_local"]
    lines.append(
        f"| FUEL single local/tiled | {fuel['status']} | passed={fuel['passed_runs']}, blocked={fuel['blocked_runs']} | `{fuel['source']}` |"
    )
    for key, label in [
        ("multi_uav_racer_exploration", "RACER three-UAV exploration"),
        ("single_uav_diff_fixed_goal", "Diff single fixed-goal"),
        ("multi_uav_diff_fixed_goal", "Diff three-UAV fixed-goal"),
    ]:
        item = packet["runs"][key]
        metric = item.get("execute_target_error_m")
        if metric is None:
            metric = item.get("min_inter_uav_distance_m")
        lines.append(
            f"| {label} | {item.get('status')} | {metric} | `{item.get('result_dir')}` |"
        )
    lines.extend(["", "## Blockers", ""])
    if packet["blockers"]:
        lines.extend(f"- `{item}`" for item in packet["blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Review Warnings", ""])
    lines.extend(f"- `{item}`" for item in packet["review_warnings"])
    lines.extend(["", "## Next Action", "", packet["next_review_action"], ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--single-uav-fuel-local", type=Path, default=DEFAULT_RUNS["single_uav_fuel_local"])
    parser.add_argument("--multi-uav-racer-exploration", type=Path, default=DEFAULT_RUNS["multi_uav_racer_exploration"])
    parser.add_argument("--single-uav-diff-fixed-goal", type=Path, default=DEFAULT_RUNS["single_uav_diff_fixed_goal"])
    parser.add_argument("--multi-uav-diff-fixed-goal", type=Path, default=DEFAULT_RUNS["multi_uav_diff_fixed_goal"])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT
        / f"factory_l2_clean_runtime_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    )
    parser.add_argument("--xy-tolerance-m", type=float, default=2.0)
    parser.add_argument("--z-tolerance-m", type=float, default=0.05)
    return parser.parse_args()


def main() -> int:
    packet_path, packet = build_packet(parse_args())
    print(rel(packet_path))
    print(packet["status"])
    if packet["blockers"]:
        print("\n".join(packet["blockers"]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
