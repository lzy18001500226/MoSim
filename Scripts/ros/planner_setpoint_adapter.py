#!/usr/bin/env python3
"""Build a 20Hz MWORKS planner setpoint trace from runtime-style commands.

This is the headless contract for the future ROS2 adapter. It does not publish
ROS2 messages and must not be used as proof of live closed-loop integration.
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
REQUIRED_COLUMNS = {
    "time",
    "sequence",
    "frame_id",
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
}
TRACE_FIELDS = [
    "time",
    "sequence",
    "source_time",
    "age_s",
    "accepted",
    "stale",
    "reject_reason",
    "mode",
    "frame_id",
    "planner_id",
    "x_ref",
    "y_ref",
    "z_ref",
    "vx_ref",
    "vy_ref",
    "vz_ref",
    "ax_ref",
    "ay_ref",
    "az_ref",
    "yaw_ref",
    "yaw_rate_ref",
]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def as_float(row: dict[str, str], key: str, line_number: int) -> float:
    try:
        value = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid {key} at command row {line_number}") from exc
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key} at command row {line_number}")
    return value


def read_commands(path: Path, expected_frame: str) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"planner command CSV missing columns {sorted(missing)}: {path}")
        rows: list[dict[str, Any]] = []
        last_time: float | None = None
        last_sequence: int | None = None
        for index, raw in enumerate(reader, start=2):
            frame_id = str(raw.get("frame_id", ""))
            if frame_id != expected_frame:
                raise ValueError(f"frame_id mismatch at command row {index}: {frame_id} != {expected_frame}")
            time_s = as_float(raw, "time", index)
            if last_time is not None and time_s <= last_time:
                raise ValueError(f"command time must be strictly increasing at row {index}")
            sequence = int(as_float(raw, "sequence", index))
            if last_sequence is not None and sequence <= last_sequence:
                raise ValueError(f"sequence must be strictly increasing at row {index}")
            rows.append(
                {
                    "time": time_s,
                    "sequence": sequence,
                    "frame_id": frame_id,
                    "planner_id": raw.get("planner_id", "unknown"),
                    "trajectory_status": raw.get("trajectory_status", "active"),
                    "x": as_float(raw, "x", index),
                    "y": as_float(raw, "y", index),
                    "z": as_float(raw, "z", index),
                    "vx": as_float(raw, "vx", index),
                    "vy": as_float(raw, "vy", index),
                    "vz": as_float(raw, "vz", index),
                    "ax": as_float(raw, "ax", index),
                    "ay": as_float(raw, "ay", index),
                    "az": as_float(raw, "az", index),
                    "yaw": as_float(raw, "yaw", index),
                    "yaw_rate": as_float(raw, "yaw_rate", index),
                }
            )
            last_time = time_s
            last_sequence = sequence
    if not rows:
        raise ValueError(f"planner command CSV is empty: {path}")
    return rows


def fmt(value: float) -> str:
    if abs(value) < 5e-13:
        value = 0.0
    return f"{value:.12g}"


def build_trace(
    commands: list[dict[str, Any]],
    *,
    rate_hz: float,
    stale_timeout_s: float,
    stop_time_s: float | None,
) -> list[dict[str, str]]:
    if rate_hz <= 0.0:
        raise ValueError("rate_hz must be positive")
    if stale_timeout_s <= 0.0:
        raise ValueError("stale_timeout_s must be positive")
    dt = 1.0 / rate_hz
    start = commands[0]["time"]
    stop = stop_time_s if stop_time_s is not None else commands[-1]["time"]
    if stop < start:
        raise ValueError("stop_time_s must be after first command")

    trace: list[dict[str, str]] = []
    command_index = 0
    latest = commands[0]
    steps = int(math.floor((stop - start) / dt + 1e-9)) + 1
    for sample_index in range(steps):
        sample_time = start + sample_index * dt
        while command_index + 1 < len(commands) and commands[command_index + 1]["time"] <= sample_time + 1e-12:
            command_index += 1
            latest = commands[command_index]
        age = max(0.0, sample_time - float(latest["time"]))
        stale = age > stale_timeout_s + 1e-12
        reject_reason = "stale_command" if stale else ""
        trace.append(
            {
                "time": fmt(sample_time),
                "sequence": str(latest["sequence"]),
                "source_time": fmt(float(latest["time"])),
                "age_s": fmt(age),
                "accepted": str(not stale).lower(),
                "stale": str(stale).lower(),
                "reject_reason": reject_reason,
                "mode": "hold" if stale else "track",
                "frame_id": str(latest["frame_id"]),
                "planner_id": str(latest["planner_id"]),
                "x_ref": fmt(float(latest["x"])),
                "y_ref": fmt(float(latest["y"])),
                "z_ref": fmt(float(latest["z"])),
                "vx_ref": fmt(float(latest["vx"])),
                "vy_ref": fmt(float(latest["vy"])),
                "vz_ref": fmt(float(latest["vz"])),
                "ax_ref": fmt(float(latest["ax"])),
                "ay_ref": fmt(float(latest["ay"])),
                "az_ref": fmt(float(latest["az"])),
                "yaw_ref": fmt(float(latest["yaw"])),
                "yaw_rate_ref": fmt(float(latest["yaw_rate"])),
            }
        )
    return trace


def write_trace(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_echo(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(
                    {
                        "schema": "mosim.setpoint_adapter_echo.v1",
                        "time": float(row["time"]),
                        "sequence": int(row["sequence"]),
                        "accepted": row["accepted"] == "true",
                        "stale": row["stale"] == "true",
                        "reject_reason": row["reject_reason"],
                        "mode": row["mode"],
                        "frame_id": row["frame_id"],
                        "planner_id": row["planner_id"],
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )


def summarize(args: argparse.Namespace, commands: list[dict[str, Any]], trace: list[dict[str, str]]) -> dict[str, Any]:
    stale_count = sum(1 for row in trace if row["stale"] == "true")
    rejected_count = sum(1 for row in trace if row["accepted"] != "true")
    duration = float(trace[-1]["time"]) - float(trace[0]["time"]) if len(trace) > 1 else 0.0
    return {
        "schema": "mosim.planner_setpoint_adapter_dryrun.v1",
        "source": "runtime_style_planner_command_csv",
        "claim_boundary": [
            "Headless adapter contract only; no ROS2 messages were published.",
            "This trace may support RUN_MANIFEST only when bound to a real runtime planner and MWORKS run.",
            "Offline UE navigation handoff remains a separate interface package and is not this runtime adapter.",
        ],
        "setpoint_trace_source": "RUNTIME_20HZ_ADAPTER",
        "setpoint_adapter_status": "pass" if stale_count == 0 and rejected_count == 0 else "needs_iteration",
        "command_count": len(commands),
        "trace_samples": len(trace),
        "rate_hz": float(args.rate_hz),
        "duration_s": round(duration, 9),
        "expected_frame_id": args.expected_frame,
        "stale_command_timeout_s": float(args.stale_timeout_s),
        "stale_samples": stale_count,
        "rejected_samples": rejected_count,
        "output_trace": rel(project_path(args.output_trace)) if args.output_trace else "",
        "echo_log": rel(project_path(args.echo_log)) if args.echo_log else "",
        "topics_contract": {
            "input": "/mosim/planner/position_cmd",
            "output": "/mosim/planner/setpoint",
            "status": "/mosim/planner/setpoint_adapter_status",
        },
        "output_fields": TRACE_FIELDS,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", required=True, help="Runtime-style planner command CSV")
    parser.add_argument("--output-trace", required=True, help="20Hz setpoint trace CSV to write")
    parser.add_argument("--echo-log", required=True, help="Accepted/rejected echo JSONL to write")
    parser.add_argument("--summary-json", help="Optional summary JSON path")
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--stale-timeout-s", type=float, default=0.15)
    parser.add_argument("--stop-time-s", type=float)
    parser.add_argument("--expected-frame", default="map")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        commands = read_commands(project_path(args.input_csv), args.expected_frame)
        trace = build_trace(
            commands,
            rate_hz=float(args.rate_hz),
            stale_timeout_s=float(args.stale_timeout_s),
            stop_time_s=args.stop_time_s,
        )
        write_trace(project_path(args.output_trace), trace)
        write_echo(project_path(args.echo_log), trace)
        summary = summarize(args, commands, trace)
        if args.summary_json:
            summary_path = project_path(args.summary_json)
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
