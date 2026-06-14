#!/usr/bin/env python3
"""Profile rotor-1 15% efficiency-loss tracking errors.

This is a read-only offline diagnostic. It reads existing scenario YAML,
raw CSV, and metrics JSON artifacts. It does not call MWORKS, Sysplorer, MCP,
check_model, SimulateModel, ROS2, UE, or GUI/window tools.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260611_rotor1_loss15_error_profile"
SCENARIOS = [
    "Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml",
]
PHASES = [
    ("startup", 0.0, 5.0),
    ("pre_fault", 5.0, 15.0),
    ("fault_window", 15.0, 19.0),
    ("recovery", 19.0, 35.0),
    ("late_tracking", 35.0, 50.0),
]

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_scenario import read_yaml  # noqa: E402


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {value!r}")
    return number


def read_rows(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"time", "x", "y", "z", "x_ref", "y_ref", "z_ref"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"{rel(path)} missing columns: {', '.join(missing)}")
        for row in reader:
            item = {key: finite_float(row[key]) for key in required}
            item["ex"] = item["x"] - item["x_ref"]
            item["ey"] = item["y"] - item["y_ref"]
            item["ez"] = item["z"] - item["z_ref"]
            item["position_error"] = math.sqrt(item["ex"] ** 2 + item["ey"] ** 2 + item["ez"] ** 2)
            rows.append(item)
    if not rows:
        raise ValueError(f"{rel(path)} has no data rows")
    return rows


def rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def phase_profile(rows: list[dict[str, float]], phase_name: str, start_s: float, end_s: float) -> dict[str, Any]:
    window = [row for row in rows if start_s <= row["time"] < end_s]
    if not window:
        return {
            "phase": phase_name,
            "start_s": start_s,
            "end_s": end_s,
            "row_count": 0,
        }

    peak = max(window, key=lambda row: row["position_error"])
    axis_rmse = {
        "x": rmse([row["ex"] for row in window]),
        "y": rmse([row["ey"] for row in window]),
        "z": rmse([row["ez"] for row in window]),
    }
    dominant_axis = max(axis_rmse, key=axis_rmse.get)
    return {
        "phase": phase_name,
        "start_s": start_s,
        "end_s": end_s,
        "row_count": len(window),
        "position_rmse_m": rmse([row["position_error"] for row in window]),
        "axis_rmse_m": axis_rmse,
        "dominant_axis": dominant_axis,
        "max_position_error_m": peak["position_error"],
        "max_error_time_s": peak["time"],
        "max_axis_error_m": {
            "x": peak["ex"],
            "y": peak["ey"],
            "z": peak["ez"],
        },
    }


def scenario_profile(path_text: str) -> dict[str, Any]:
    scenario_path = repo_path(path_text)
    config = read_yaml(scenario_path)
    result = config.get("result", {})
    if not isinstance(result, dict):
        result = {}
    raw_path = repo_path(result.get("raw_file", ""))
    metrics_path = repo_path(result.get("metrics_file", ""))
    metrics = read_json(metrics_path)
    rows = read_rows(raw_path)
    phases = [phase_profile(rows, name, start, end) for name, start, end in PHASES]
    worst_phase = max(
        [phase for phase in phases if phase.get("row_count", 0) > 0],
        key=lambda phase: phase.get("position_rmse_m", 0.0),
    )
    return {
        "scenario": rel(scenario_path),
        "experiment_id": config.get("experiment_id"),
        "controller_id": config.get("controller_id"),
        "raw_file": rel(raw_path),
        "metrics_file": rel(metrics_path),
        "quality_status": metrics.get("quality_status"),
        "quality_pass": metrics.get("quality_pass"),
        "position_rmse_m": metrics.get("position_rmse_m"),
        "total_health_score": metrics.get("total_health_score"),
        "steady_state_error_m": metrics.get("steady_state_error_m"),
        "disturbance_recovery_time_s": metrics.get("disturbance_recovery_time_s"),
        "phase_profiles": phases,
        "worst_phase": worst_phase["phase"],
        "worst_phase_position_rmse_m": worst_phase["position_rmse_m"],
        "dominant_axis_overall": max(
            {
                "x": rmse([row["ex"] for row in rows]),
                "y": rmse([row["ey"] for row in rows]),
                "z": rmse([row["ez"] for row in rows]),
            },
            key=lambda axis: {
                "x": rmse([row["ex"] for row in rows]),
                "y": rmse([row["ey"] for row in rows]),
                "z": rmse([row["ez"] for row in rows]),
            }[axis],
        ),
    }


def compare_profiles(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    by_controller = {str(item["controller_id"]): item for item in profiles}
    baseline = by_controller.get("pid_baseline")
    awff = by_controller.get("awff_sysblock")
    if not baseline or not awff:
        return {"available": False, "reason": "pid_baseline and awff_sysblock profiles are required"}

    baseline_rmse = float(baseline["position_rmse_m"])
    awff_rmse = float(awff["position_rmse_m"])
    improvement_pct = (baseline_rmse - awff_rmse) / baseline_rmse * 100.0 if baseline_rmse else 0.0
    phase_deltas: list[dict[str, Any]] = []
    baseline_phases = {phase["phase"]: phase for phase in baseline["phase_profiles"]}
    awff_phases = {phase["phase"]: phase for phase in awff["phase_profiles"]}
    for name, _, _ in PHASES:
        if name not in baseline_phases or name not in awff_phases:
            continue
        b = baseline_phases[name]
        a = awff_phases[name]
        b_rmse = float(b.get("position_rmse_m", 0.0))
        a_rmse = float(a.get("position_rmse_m", 0.0))
        phase_deltas.append(
            {
                "phase": name,
                "pid_position_rmse_m": b_rmse,
                "awff_position_rmse_m": a_rmse,
                "awff_delta_rmse_m": a_rmse - b_rmse,
                "awff_improvement_pct": (b_rmse - a_rmse) / b_rmse * 100.0 if b_rmse else 0.0,
            }
        )
    return {
        "available": True,
        "rmse_improvement_pct": improvement_pct,
        "health_score_delta": float(awff["total_health_score"]) - float(baseline["total_health_score"]),
        "phase_deltas": phase_deltas,
    }


def build_profile(paths: list[str]) -> dict[str, Any]:
    profiles = [scenario_profile(path) for path in paths]
    comparison = compare_profiles(profiles)
    focus = [
        "Both current rotor1_loss15 artifacts remain quality_status=needs_iteration.",
        "The profile is read-only historical evidence; it does not prove a new live MWORKS run.",
        "Use the phase and dominant-axis profile to choose the smallest next controller/model change after a fresh rerun.",
        "Stop before multi-UAV formation work.",
    ]
    return {
        "schema": "mosim.mworks.rotor1_loss15_error_profile.v1",
        "status": "diagnostic_profile_ready",
        "static_read_only": True,
        "live_mworks_touched": False,
        "scope": "single_uav_rotor1_loss15_diagnostics_before_multi_uav",
        "scenario_count": len(profiles),
        "profiles": profiles,
        "comparison": comparison,
        "next_engineering_focus": focus,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, profile: dict[str, Any]) -> None:
    lines = [
        "# Rotor1 Loss15 Error Profile",
        "",
        f"Status: `{profile['status']}`",
        "",
        "Read-only diagnostic profile. It does not run MWORKS and does not modify controller/model files.",
        "",
        "## Scenario Profiles",
        "",
    ]
    for item in profile["profiles"]:
        lines.append(
            f"- `{item['scenario']}`: controller=`{item['controller_id']}`, "
            f"quality=`{item['quality_status']}`, rmse=`{item['position_rmse_m']:.6f}`, "
            f"health=`{item['total_health_score']:.6f}`, worst_phase=`{item['worst_phase']}`, "
            f"dominant_axis=`{item['dominant_axis_overall']}`"
        )
        for phase in item["phase_profiles"]:
            if phase.get("row_count", 0) <= 0:
                continue
            lines.append(
                f"  - {phase['phase']}: rmse=`{phase['position_rmse_m']:.6f}`, "
                f"max_error=`{phase['max_position_error_m']:.6f}` at `{phase['max_error_time_s']:.2f}s`, "
                f"dominant_axis=`{phase['dominant_axis']}`"
            )
    comparison = profile["comparison"]
    lines.extend(["", "## AWFF vs PID", ""])
    if comparison.get("available"):
        lines.append(f"- RMSE improvement: `{comparison['rmse_improvement_pct']:.3f}%`")
        lines.append(f"- Health score delta: `{comparison['health_score_delta']:.6f}`")
        for phase in comparison["phase_deltas"]:
            lines.append(
                f"- {phase['phase']}: delta_rmse=`{phase['awff_delta_rmse_m']:.6f}`, "
                f"improvement=`{phase['awff_improvement_pct']:.3f}%`"
            )
    else:
        lines.append(f"- Comparison unavailable: {comparison.get('reason')}")
    lines.extend(["", "## Next Engineering Focus", ""])
    lines.extend(f"- {item}" for item in profile["next_engineering_focus"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenarios", nargs="*", default=SCENARIOS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    profile = build_profile(args.scenarios)
    write_json(output_dir / "rotor1_loss15_error_profile.json", profile)
    write_markdown(output_dir / "rotor1_loss15_error_profile.md", profile)
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
