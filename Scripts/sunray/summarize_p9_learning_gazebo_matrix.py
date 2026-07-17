#!/usr/bin/env python3
"""Summarize P9 runtime A/B without promoting offline improvements."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROFILES = ("cascade_pid", "trained_neural_residual", "rl_gain_scheduler")
CONDITIONS = ("nominal", "wind", "parameter_mismatch")


def metric(payload: dict, group: str, name: str):
    value = payload.get(group)
    return value.get(name) if isinstance(value, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--csv-out", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    execution_errors = []
    acceptance_errors = []
    for profile in PROFILES:
        for condition in CONDITIONS:
            run_dir = args.result_root / f"{profile}_{condition}"
            metrics_path = run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json"
            if not metrics_path.is_file():
                execution_errors.append(f"missing metrics: {metrics_path}")
                continue
            payload = json.loads(metrics_path.read_text(encoding="utf-8"))
            provenance_status = "baseline_not_applicable"
            runtime_symbol = None
            if profile != "cascade_pid":
                provenance_path = run_dir / "LEARNING_GENERATED_RUNTIME_PROVENANCE.json"
                if not provenance_path.is_file():
                    execution_errors.append(f"missing provenance: {provenance_path}")
                    provenance_status = "missing"
                else:
                    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
                    provenance_status = provenance.get("status")
                    runtime_symbol = provenance.get("runtime_loaded_symbol")
                    if provenance_status != "passed":
                        execution_errors.append(f"{profile}/{condition}: provenance not passed")
            wind_status = "not_applicable"
            if condition == "wind":
                wind_path = run_dir / "WIND_INJECTION_EVIDENCE.json"
                wind_status = (
                    json.loads(wind_path.read_text(encoding="utf-8")).get("status")
                    if wind_path.is_file() else "missing"
                )
                if wind_status != "passed":
                    execution_errors.append(f"{profile}/{condition}: wind injection not passed")
            row = {
                "profile": profile,
                "condition": condition,
                "mission_status": payload.get("status"),
                "mission_reason": payload.get("reason"),
                "steady_hover_xy_rmse_m": metric(payload, "steady_hover", "xy_rmse_m"),
                "steady_hover_z_rmse_m": metric(payload, "steady_hover", "z_abs_rmse_m"),
                "all_reference_xyz_rmse_m": metric(payload, "all_reference_tracking", "xyz_rmse_m"),
                "landing_disarm": metric(payload, "landing_disarm", "success"),
                "runtime_provenance": provenance_status,
                "runtime_loaded_symbol": runtime_symbol,
                "wind_injection": wind_status,
                "run_dir": str(run_dir),
            }
            rows.append(row)
            if row["mission_status"] != "passed":
                acceptance_errors.append(
                    f"{profile}/{condition}: mission {row['mission_status']}: {row['mission_reason']}"
                )
            if not row["landing_disarm"]:
                acceptance_errors.append(f"{profile}/{condition}: landing/disarm not accepted")

    baselines = {row["condition"]: row for row in rows if row["profile"] == "cascade_pid"}
    for row in rows:
        baseline = baselines.get(row["condition"])
        current = row["all_reference_xyz_rmse_m"]
        reference = baseline.get("all_reference_xyz_rmse_m") if baseline else None
        row["xyz_rmse_change_vs_cascade_fraction"] = (
            (reference - current) / reference
            if row["profile"] != "cascade_pid" and reference and current is not None else None
        )

    execution_status = (
        "passed"
        if len(rows) == len(PROFILES) * len(CONDITIONS) and not execution_errors
        else "blocked"
    )
    acceptance_status = (
        "passed"
        if execution_status == "passed" and not acceptance_errors
        else "blocked"
    )
    output = {
        "schema": "mosim.control_platform.p9_learning_gazebo_ab.v2",
        "status": acceptance_status,
        "execution_status": execution_status,
        "acceptance_status": acceptance_status,
        "artifact_sha256": "4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45",
        "profiles": list(PROFILES),
        "conditions": list(CONDITIONS),
        "rows": rows,
        "execution_errors": execution_errors,
        "acceptance_errors": acceptance_errors,
        "claim_boundary": "Same-mission ROS1 Gazebo/PX4/MAVROS A/B. Positive offline training metrics are not treated as runtime superiority; each runtime comparison is reported as observed.",
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else ["profile", "condition"]
    with args.csv_out.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(args.json_out)
    return 0 if acceptance_status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
