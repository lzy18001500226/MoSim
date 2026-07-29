#!/usr/bin/env python3
"""Run bounded duration regressions after a RotorCommand runner-base change.

The helper reuses the G2 MWORKS execution path but writes an isolated,
duration-specific matrix and result tree.  It never changes the frozen G2
matrix or its historical run records.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_phase2_full_48_climbpath as phase2


T1_ROOT = (
    ROOT
    / "Results"
    / "control_platform"
    / "phase2_full_48_climbpath"
    / "g3_repair"
    / "t1_official_pid_continuous_command"
)
MATRIX_SCHEMA = "mosim.t1_rotor_command_harness_regression_matrix.v1"
RUN_SCHEMA = "mosim.t1_rotor_command_harness_regression_run.v1"
STATUS_SCHEMA = "mosim.t1_rotor_command_harness_regression_status.v1"


def duration_label(duration_s: float) -> str:
    return f"{duration_s:g}s"


def scenario_id(duration_s: float) -> str:
    return f"climb_path_{duration_label(duration_s)}"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def configure_phase2(output_root: Path, duration_s: float) -> None:
    phase2.RESULT_ROOT = output_root
    phase2.MATRIX_PATH = output_root / "T1_MATRIX.json"
    phase2.STATUS_PATH = output_root / "T1_STATUS.json"
    phase2.CONTRACT_PATH = output_root / "T1_EXECUTION_CONTRACT.json"
    phase2.STOP_TIME_S = duration_s
    phase2.SIMULATION_TIMEOUT_S = 120.0
    phase2.SCHEMA = RUN_SCHEMA
    phase2.MATRIX_SCHEMA = MATRIX_SCHEMA
    phase2.STATUS_SCHEMA = STATUS_SCHEMA


def build_matrix(rows: list[dict[str, Any]], duration_s: float) -> dict[str, Any]:
    return {
        "schema": MATRIX_SCHEMA,
        "generated_at": phase2.now_iso(),
        "scope": {
            "task": "T1-FIX RotorCommand continuous-command harness regression",
            "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
            "duration_s": duration_s,
            "scenario_injection": "none",
            "controller_count": len(rows),
            "harness_change": (
                "FormalRotorCommandRunnerBase retains 100 Hz reference and measurement holds, "
                "but connects controller.rotor_command continuously to plant.rotor_command."
            ),
            "frozen_g2_matrix": {
                "path": "Results/control_platform/phase2_full_48_climbpath/G2_MATRIX.json",
                "sha256": phase2.sha256(
                    ROOT / "Results" / "control_platform" / "phase2_full_48_climbpath" / "G2_MATRIX.json"
                ),
            },
        },
        "rows": rows,
    }


def stable_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in matrix.items() if key != "generated_at"}


def freeze_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    if phase2.MATRIX_PATH.is_file():
        existing = read_json(phase2.MATRIX_PATH)
        if stable_matrix(existing) != stable_matrix(matrix):
            raise RuntimeError("T1 matrix identity differs from the existing duration-specific regression matrix")
        return existing
    write_json(phase2.MATRIX_PATH, matrix)
    return matrix


def write_contract(matrix: dict[str, Any]) -> None:
    write_json(
        phase2.CONTRACT_PATH,
        {
            "schema": "mosim.t1_rotor_command_harness_regression_contract.v1",
            "generated_at": phase2.now_iso(),
            "matrix": {
                "path": relative(phase2.MATRIX_PATH),
                "sha256": phase2.sha256(phase2.MATRIX_PATH),
            },
            "scope": matrix["scope"],
            "acceptance": {
                "status_values": ["pass", "fail"],
                "terminal_position_error_limit_m": phase2.TERMINAL_ERROR_LIMIT_M,
                "source_change": "FormalRotorCommandRunnerBase command-side ZOH removal only",
                "no_controller_gain_tuning": True,
                "no_plant_change": True,
                "no_seven_scenario_run": True,
                "g2_evidence_mutation": "forbidden",
            },
        },
    )


def selected_rows(controllers: set[str]) -> list[dict[str, Any]]:
    full = phase2.build_matrix()
    rows = [row for row in full["rows"] if str(row["controller_id"]) in controllers]
    missing = controllers - {str(row["controller_id"]) for row in rows}
    if missing:
        raise ValueError(f"unknown formal controller ID(s): {sorted(missing)}")
    return rows


def relabel_duration_specific_artifacts(run_dir: Path, duration_s: float) -> None:
    """Replace inherited G2 50 s labels in this isolated T1 evidence bundle."""
    label = duration_label(duration_s)
    scene = scenario_id(duration_s)
    record_path = run_dir / "RUN_RECORD.json"
    if not record_path.is_file():
        return

    record = read_json(record_path)
    record["scenario_id"] = scene
    record["duration_s"] = duration_s
    observations = record.get("mworks_phase_observations")
    if isinstance(observations, list):
        record["mworks_phase_observations"] = [
            item.replace("50 s ClimbPath", f"{label} ClimbPath") if isinstance(item, str) else item
            for item in observations
        ]

    metrics_path = run_dir / "metrics" / "METRICS.json"
    if metrics_path.is_file():
        metrics = read_json(metrics_path)
        metrics["scene_id"] = scene
        metrics["evidence_level"] = "formal_mworks_t1_rotor_command_harness_regression_v1"
        write_json(metrics_path, metrics)

    metrics_csv_path = run_dir / "metrics" / "metrics.csv"
    if metrics_csv_path.is_file():
        with metrics_csv_path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.reader(source))
        for row in rows:
            if len(row) != 2:
                continue
            if row[0] == "scene_id":
                row[1] = scene
            elif row[0] == "evidence_level":
                row[1] = "formal_mworks_t1_rotor_command_harness_regression_v1"
        with metrics_csv_path.open("w", encoding="utf-8", newline="") as destination:
            csv.writer(destination).writerows(rows)

    config_path = run_dir / "RUN_CONFIG.json"
    if config_path.is_file():
        config = read_json(config_path)
        config["schema"] = "mosim.t1_rotor_command_harness_regression_run_config.v1"
        config["scenario_id"] = scene
        config["task"] = "T1-FIX RotorCommand continuous-command harness regression"
        write_json(config_path, config)

    # The inherited helper stores artifact checksums in the record. Rebuild the
    # list after relabeling metrics so every checksum remains current.
    record["artifact_refs"] = []
    phase2.artifact_refs(record, run_dir, run_dir / "logs" / "mcp.jsonl")
    write_json(record_path, record)
    phase2.write_route_status(record, run_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controllers", required=True, help="comma-separated G2 controller IDs")
    parser.add_argument("--duration-s", required=True, type=float, help="simulation duration in seconds")
    parser.add_argument("--rerun", action="store_true", help="archive an existing T1 terminal record before replay")
    parser.add_argument("--wrapper", help="optional explicit project-local Sysplorer MCP wrapper")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.duration_s <= 0:
        raise ValueError("--duration-s must be positive")
    controllers = {item.strip() for item in args.controllers.split(",") if item.strip()}
    if not controllers:
        raise ValueError("--controllers must name at least one controller")

    output_root = T1_ROOT / "runs" / duration_label(args.duration_s)
    output_root.mkdir(parents=True, exist_ok=True)
    configure_phase2(output_root, args.duration_s)
    matrix = freeze_matrix(build_matrix(selected_rows(controllers), args.duration_s))
    write_contract(matrix)
    matrix_hash = phase2.sha256(phase2.MATRIX_PATH)

    for row in matrix["rows"]:
        run_dir = phase2.run_dir_for(row)
        if not args.rerun and phase2.existing_terminal_record(run_dir):
            relabel_duration_specific_artifacts(run_dir, args.duration_s)
            continue
        try:
            phase2.source_observations(row, "before_route")
        except Exception as exc:
            phase2.static_failure(row, matrix_hash, str(exc))
            continue
        phase2.run_route(row, matrix_hash, rerun=args.rerun, wrapper=args.wrapper)
        relabel_duration_specific_artifacts(run_dir, args.duration_s)

    status = phase2.write_status(matrix)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
