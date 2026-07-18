#!/usr/bin/env python3
"""Summarize the official-PID versus recommended-controller seven-scenario A/B."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROFILES = ("official_pid", "gain_scheduled_pid")
SCENARIOS = (
    "hover",
    "step",
    "figure8",
    "spiral",
    "wind",
    "parameter_mismatch",
    "motor_efficiency_fault",
)
TRAJECTORY_SCENARIOS = {"step", "figure8", "spiral"}


def nested(payload: dict, group: str, name: str):
    value = payload.get(group)
    return value.get(name) if isinstance(value, dict) else None


def load_status(path: Path) -> tuple[str, dict]:
    if not path.is_file():
        return "missing", {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("status", "missing")), payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--csv-out", type=Path, required=True)
    args = parser.parse_args()
    rows: list[dict] = []
    execution_errors: list[str] = []
    acceptance_blockers: list[str] = []

    for profile in PROFILES:
        for scenario in SCENARIOS:
            run_dir = args.result_root / f"{profile}_{scenario}"
            metrics_status, metrics = load_status(run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json")
            provenance_name = (
                "G9_GENERATED_RUNTIME_PROVENANCE.json"
                if profile == "official_pid"
                else "PID_GENERATED_RUNTIME_PROVENANCE.json"
            )
            provenance_status, provenance = load_status(run_dir / provenance_name)
            injection_status = "not_applicable"
            if scenario == "wind":
                injection_status, _ = load_status(run_dir / "WIND_INJECTION_EVIDENCE.json")
            elif scenario == "motor_efficiency_fault":
                injection_status, _ = load_status(
                    run_dir / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json"
                )

            injection_ok = injection_status in {"passed", "not_applicable"}
            execution_complete = bool(metrics) and provenance_status == "passed" and injection_ok
            landing_disarm = nested(metrics, "landing_disarm", "success")
            accepted = execution_complete and metrics_status == "passed" and landing_disarm is True
            row_status = "accepted" if accepted else ("executed_blocked" if execution_complete else "not_run")
            trajectory_rmse = nested(metrics, "trajectory", "xyz_rmse_m")
            all_reference_rmse = nested(metrics, "all_reference_tracking", "xyz_rmse_m")
            primary_rmse = trajectory_rmse if scenario in TRAJECTORY_SCENARIOS else all_reference_rmse
            row = {
                "profile": profile,
                "scenario": scenario,
                "mission": metrics.get("mission"),
                "status": row_status,
                "mission_status": metrics_status,
                "mission_reason": metrics.get("reason"),
                "provenance_status": provenance_status,
                "runtime_loaded_symbol": provenance.get("runtime_loaded_symbol"),
                "injection_status": injection_status,
                "landing_disarm": landing_disarm,
                "hover_xy_rmse_m": nested(metrics, "steady_hover", "xy_rmse_m"),
                "hover_z_rmse_m": nested(metrics, "steady_hover", "z_abs_rmse_m"),
                "trajectory_xyz_rmse_m": trajectory_rmse,
                "all_reference_xyz_rmse_m": all_reference_rmse,
                "primary_rmse_m": primary_rmse,
                "run_dir": str(run_dir),
            }
            rows.append(row)
            if not execution_complete:
                execution_errors.append(
                    f"{profile}/{scenario}: metrics={bool(metrics)} provenance={provenance_status} "
                    f"injection={injection_status}"
                )
            elif not accepted:
                acceptance_blockers.append(
                    f"{profile}/{scenario}: {metrics_status}: {metrics.get('reason')}"
                )

    official = {
        row["scenario"]: row for row in rows if row["profile"] == "official_pid"
    }
    for row in rows:
        baseline = official.get(row["scenario"])
        baseline_rmse = baseline.get("primary_rmse_m") if baseline else None
        current_rmse = row.get("primary_rmse_m")
        row["rmse_improvement_vs_official_fraction"] = (
            (baseline_rmse - current_rmse) / baseline_rmse
            if row["profile"] != "official_pid"
            and isinstance(baseline_rmse, (int, float))
            and baseline_rmse > 0.0
            and isinstance(current_rmse, (int, float))
            else None
        )

    counts = {state: sum(row["status"] == state for row in rows) for state in (
        "accepted", "executed_blocked", "not_run"
    )}
    execution_status = "passed" if counts["not_run"] == 0 and not execution_errors else "blocked"
    output = {
        "schema": "mosim.control_platform.final_controller_seven_scenario_ab.v1",
        "status": "closed" if execution_status == "passed" else "incomplete",
        "execution_status": execution_status,
        "acceptance_status": "passed" if counts["accepted"] == len(rows) else "blocked",
        "baseline_controller": "official_pid",
        "recommended_controller": "gain_scheduled_pid",
        "selection_basis": (
            "Same PID-family architecture, accepted MWORKS generated-C Gazebo route, "
            "best existing accepted P1 nominal hover XY RMSE, and lower Z RMSE than cascade PID."
        ),
        "profiles": list(PROFILES),
        "scenarios": list(SCENARIOS),
        "counts": counts,
        "rows": rows,
        "execution_errors": execution_errors,
        "acceptance_blockers": acceptance_blockers,
        "claim_boundary": (
            "Each row uses one bounded ROS1/Gazebo/PX4/MAVROS run with same-run generated-C "
            "provenance. Threshold failures remain executed_blocked; observed RMSE changes do not "
            "by themselves establish general controller superiority."
        ),
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8", newline="\n")
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else ["profile", "scenario", "status"]
    with args.csv_out.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(args.json_out)
    return 0 if execution_status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
