#!/usr/bin/env python3
"""Regression checks for the headless planner-to-MWORKS setpoint adapter."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Scripts" / "ros" / "planner_setpoint_adapter.py"
TMP_ROOT = ROOT / "Results" / "tmp" / "planner_setpoint_adapter_test"


def write_commands(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "time",
        "sequence",
        "frame_id",
        "planner_id",
        "trajectory_status",
        "x",
        "y",
        "z",
        "vx",
        "vy",
        "vz",
        "ax",
        "ay",
        "az",
        "yaw",
        "yaw_rate",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_adapter(tmp_path: Path, command_rows: list[dict[str, object]], *extra_args: str) -> tuple[dict, Path, Path]:
    commands = tmp_path / "planner_commands.csv"
    trace = tmp_path / "setpoint_trace.csv"
    echo = tmp_path / "setpoint_echo.jsonl"
    write_commands(commands, command_rows)
    result = subprocess.run(
        [
            sys.executable,
            str(ADAPTER),
            "--input-csv",
            str(commands),
            "--output-trace",
            str(trace),
            "--echo-log",
            str(echo),
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout), trace, echo


def command(time_s: float, sequence: int, x: float = 0.0) -> dict[str, object]:
    return {
        "time": time_s,
        "sequence": sequence,
        "frame_id": "map",
        "planner_id": "ego_style",
        "trajectory_status": "active",
        "x": x,
        "y": 0.0,
        "z": 1.2,
        "vx": 1.0,
        "vy": 0.0,
        "vz": 0.0,
        "ax": 0.0,
        "ay": 0.0,
        "az": 0.0,
        "yaw": 0.1,
        "yaw_rate": 0.0,
    }


def clean_case(name: str) -> Path:
    path = TMP_ROOT / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_planner_setpoint_adapter_generates_20hz_runtime_trace() -> None:
    tmp_path = clean_case("runtime_trace")
    summary, trace, echo = run_adapter(
        tmp_path,
        [command(0.0, 1, 0.0), command(0.05, 2, 0.05), command(0.10, 3, 0.10)],
        "--stop-time-s",
        "0.10",
    )
    if summary["schema"] != "mosim.planner_setpoint_adapter_dryrun.v1":
        raise AssertionError(summary)
    if summary["setpoint_trace_source"] != "RUNTIME_20HZ_ADAPTER":
        raise AssertionError(summary)
    if summary["setpoint_adapter_status"] != "pass":
        raise AssertionError(summary)
    if summary["rate_hz"] != 20.0 or summary["trace_samples"] != 3:
        raise AssertionError(summary)
    rows = list(csv.DictReader(trace.open(newline="", encoding="utf-8")))
    if [row["time"] for row in rows] != ["0", "0.05", "0.1"]:
        raise AssertionError(rows)
    if rows[-1]["x_ref"] != "0.1" or rows[-1]["accepted"] != "true":
        raise AssertionError(rows[-1])
    echoes = [json.loads(line) for line in echo.read_text(encoding="utf-8").splitlines()]
    if len(echoes) != 3 or any(item["stale"] for item in echoes):
        raise AssertionError(echoes)
    shutil.rmtree(tmp_path)


def test_planner_setpoint_adapter_records_stale_timeout() -> None:
    tmp_path = clean_case("stale_timeout")
    summary, trace, echo = run_adapter(
        tmp_path,
        [command(0.0, 1, 0.0)],
        "--stop-time-s",
        "0.20",
        "--stale-timeout-s",
        "0.09",
    )
    if summary["setpoint_adapter_status"] != "needs_iteration":
        raise AssertionError(summary)
    if summary["stale_samples"] == 0 or summary["rejected_samples"] == 0:
        raise AssertionError(summary)
    rows = list(csv.DictReader(trace.open(newline="", encoding="utf-8")))
    stale_rows = [row for row in rows if row["stale"] == "true"]
    if not stale_rows or stale_rows[0]["mode"] != "hold":
        raise AssertionError(rows)
    if "stale_command" not in echo.read_text(encoding="utf-8"):
        raise AssertionError(echo.read_text(encoding="utf-8"))
    shutil.rmtree(tmp_path)


def test_planner_setpoint_adapter_rejects_bad_frame_and_nan() -> None:
    tmp_path = clean_case("rejects_bad_input")
    commands = tmp_path / "bad_commands.csv"
    trace = tmp_path / "trace.csv"
    echo = tmp_path / "echo.jsonl"
    write_commands(commands, [{**command(0.0, 1), "frame_id": "ue_world"}])
    result = subprocess.run(
        [
            sys.executable,
            str(ADAPTER),
            "--input-csv",
            str(commands),
            "--output-trace",
            str(trace),
            "--echo-log",
            str(echo),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0 or "frame_id mismatch" not in result.stderr:
        raise AssertionError(result.stderr)

    write_commands(commands, [{**command(0.0, 1), "ax": "nan"}])
    result = subprocess.run(
        [
            sys.executable,
            str(ADAPTER),
            "--input-csv",
            str(commands),
            "--output-trace",
            str(trace),
            "--echo-log",
            str(echo),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0 or "non-finite ax" not in result.stderr:
        raise AssertionError(result.stderr)
    shutil.rmtree(tmp_path)


def main() -> int:
    test_planner_setpoint_adapter_generates_20hz_runtime_trace()
    test_planner_setpoint_adapter_records_stale_timeout()
    test_planner_setpoint_adapter_rejects_bad_frame_and_nan()
    if TMP_ROOT.exists():
        shutil.rmtree(TMP_ROOT)
    print("[OK] planner setpoint adapter regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
