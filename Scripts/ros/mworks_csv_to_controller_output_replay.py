#!/usr/bin/env python3
"""Convert an accepted MWORKS CSV result into ControllerOutput replay samples.

This bridge preserves the MWORKS controller output shape while making the
command explicit for the Gazebo actuator adapter. It does not run MWORKS,
Gazebo, or claim closed-loop controller performance by itself.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUT_CSV = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260612_rotor1_loss15_param_smoke"
    / "raw"
    / "rotor1_loss15_linear_mpc_online_fault_allocation_param_smoke.csv"
)
DEFAULT_OUTPUT_JSONL = (
    ROOT
    / "Results"
    / "gazebo_ros2"
    / "mworks_controller_output_replay"
    / "controller_output_replay.jsonl"
)
DEFAULT_MANIFEST = DEFAULT_OUTPUT_JSONL.with_name("MWORKS_CONTROLLER_OUTPUT_REPLAY_MANIFEST.json")

DEFAULT_SIGNED_HOVER = [1.0, -1.0, 1.0, -1.0]
DEFAULT_LEGACY_HOVER_CMD = 13.985413115099604
DEFAULT_MWORKS_HOVER_CMD = 53.562090367172424
DEFAULT_GAZEBO_HOVER_NORMALIZED = 0.05520


def project_path(value: str | Path) -> Path:
    raw = Path(value)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def finite_float(value: str, *, column: str, row_index: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_index} column {column!r} is not numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"row {row_index} column {column!r} is not finite")
    return number


def bounded(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def should_emit(t: float, last_t: float | None, max_rate_hz: float) -> bool:
    if last_t is None:
        return True
    if max_rate_hz <= 0.0:
        return True
    return (t - last_t) >= (1.0 / max_rate_hz) - 1e-12


def convert_row(
    row: dict[str, str],
    *,
    row_index: int,
    sequence: int,
    time_column: str,
    command_columns: list[str],
    signed_hover: list[float],
    motor_command_scale: float,
    mworks_hover_cmd: float,
    gazebo_hover_normalized: float,
    command_min: float,
    command_max: float,
    vehicle_id: str,
    command_frame: str,
    mode: str,
    backend: str,
    source_authority: str,
    status: str,
    command_type: str,
    base_unix: float,
) -> dict[str, Any]:
    t = finite_float(row[time_column], column=time_column, row_index=row_index)
    deltas = [finite_float(row[column], column=column, row_index=row_index) for column in command_columns]
    signed_mworks_visual_speed = [
        sign * mworks_hover_cmd + motor_command_scale * delta
        for sign, delta in zip(signed_hover, deltas, strict=True)
    ]
    raw_normalized = [
        abs(value) / mworks_hover_cmd * gazebo_hover_normalized
        for value in signed_mworks_visual_speed
    ]
    command = [bounded(value, command_min, command_max) for value in raw_normalized]
    saturation = any(abs(a - b) > 1e-12 for a, b in zip(raw_normalized, command, strict=True))
    return {
        "schema": "mosim.controller_output_replay_sample.v1",
        "sequence": sequence,
        "time_s": t,
        "vehicle_id": vehicle_id,
        "command_type": command_type,
        "command": command,
        "command_frame": command_frame,
        "mode": mode,
        "status": status,
        "backend": backend,
        "saturation": saturation,
        "source_authority": source_authority,
        "issued_at_unix": base_unix + t,
        "mworks_source": {
            "row_index": row_index,
            "time_column": time_column,
            "command_columns": command_columns,
            "controller_delta_command": deltas,
            "signed_hover_motor_speed_cmd": signed_hover,
            "legacy_hover_motor_speed_cmd": DEFAULT_LEGACY_HOVER_CMD,
            "mworks_hover_motor_speed_cmd": mworks_hover_cmd,
            "motor_command_scale": motor_command_scale,
            "signed_mworks_visual_motor_speed": signed_mworks_visual_speed,
            "raw_gazebo_normalized_command": raw_normalized,
        },
    }


def summarize(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not samples:
        return {
            "sample_count": 0,
            "duration_s": 0.0,
            "command_min": None,
            "command_max": None,
            "saturation_count": 0,
        }
    values = [value for sample in samples for value in sample["command"]]
    return {
        "sample_count": len(samples),
        "duration_s": float(samples[-1]["time_s"]) - float(samples[0]["time_s"]),
        "time_start_s": samples[0]["time_s"],
        "time_end_s": samples[-1]["time_s"],
        "command_min": min(values),
        "command_max": max(values),
        "saturation_count": sum(1 for sample in samples if sample["saturation"]),
        "first_command": samples[0]["command"],
        "last_command": samples[-1]["command"],
    }


def build_samples(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    input_csv = project_path(args.input_csv)
    command_columns = list(args.command_columns)
    if len(command_columns) != 4:
        raise SystemExit("--command-columns must name exactly four columns")
    if len(args.signed_hover) != 4:
        raise SystemExit("--signed-hover must have exactly four signs")
    if args.legacy_hover_motor_speed_cmd <= 0.0 or args.mworks_hover_motor_speed_cmd <= 0.0:
        raise SystemExit("hover motor speed commands must be positive")
    if args.gazebo_hover_normalized_command <= 0.0:
        raise SystemExit("--gazebo-hover-normalized-command must be positive")
    if args.command_min < 0.0 or args.command_max > 1.0 or args.command_min > args.command_max:
        raise SystemExit("--command-min/--command-max must stay within [0, 1] and min <= max")
    if args.max_rate_hz < 0.0:
        raise SystemExit("--max-rate-hz must be nonnegative")

    motor_command_scale = args.mworks_hover_motor_speed_cmd / args.legacy_hover_motor_speed_cmd
    samples: list[dict[str, Any]] = []
    last_emit_time: float | None = None
    with input_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = [args.time_column, *command_columns]
        missing = [column for column in required if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"missing required CSV columns: {missing}")
        for row_index, row in enumerate(reader, start=1):
            t = finite_float(row[args.time_column], column=args.time_column, row_index=row_index)
            if not should_emit(t, last_emit_time, args.max_rate_hz):
                continue
            sample = convert_row(
                row,
                row_index=row_index,
                sequence=len(samples) + 1,
                time_column=args.time_column,
                command_columns=command_columns,
                signed_hover=[float(item) for item in args.signed_hover],
                motor_command_scale=motor_command_scale,
                mworks_hover_cmd=args.mworks_hover_motor_speed_cmd,
                gazebo_hover_normalized=args.gazebo_hover_normalized_command,
                command_min=args.command_min,
                command_max=args.command_max,
                vehicle_id=args.vehicle_id,
                command_frame=args.command_frame,
                mode=args.mode,
                backend=args.backend,
                source_authority=args.source_authority,
                status=args.status,
                command_type=args.command_type,
                base_unix=args.base_unix,
            )
            samples.append(sample)
            last_emit_time = t

    summary = summarize(samples)
    manifest = {
        "schema": "mosim.mworks_controller_output_replay_manifest.v1",
        "status": "ready" if samples else "blocked",
        "source": "MWORKS_MCP_result_csv",
        "source_csv": rel(input_csv),
        "vehicle_id": args.vehicle_id,
        "command_type": args.command_type,
        "command_frame": args.command_frame,
        "mapping": {
            "formula": "signed_speed_i = sign_i*mworks_hover_motor_speed_cmd + (mworks_hover_motor_speed_cmd/legacy_hover_motor_speed_cmd)*controller_delta_i; gazebo_normalized_i = abs(signed_speed_i)/mworks_hover_motor_speed_cmd*gazebo_hover_normalized_command",
            "time_column": args.time_column,
            "command_columns": command_columns,
            "signed_hover": [float(item) for item in args.signed_hover],
            "legacy_hover_motor_speed_cmd": args.legacy_hover_motor_speed_cmd,
            "mworks_hover_motor_speed_cmd": args.mworks_hover_motor_speed_cmd,
            "motor_command_scale": motor_command_scale,
            "gazebo_hover_normalized_command": args.gazebo_hover_normalized_command,
            "command_min": args.command_min,
            "command_max": args.command_max,
            "max_rate_hz": args.max_rate_hz,
        },
        "summary": summary,
        "claim_boundary": [
            "This artifact converts an existing MWORKS result CSV into the MoSim ControllerOutput ABI.",
            "It does not run MWORKS, does not run Gazebo, and does not prove closed-loop controller performance.",
            "Replaying a MWORKS closed-loop trace into Gazebo is an actuator-interface deployment check unless a same-run Gazebo feedback controller is used.",
        ],
    }
    return samples, manifest


def write_outputs(args: argparse.Namespace, samples: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    output_jsonl = project_path(args.output_jsonl)
    output_manifest = project_path(args.output_manifest)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8", newline="\n") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest["output_jsonl"] = rel(output_jsonl)
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def publish_samples(args: argparse.Namespace, samples: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput
    except Exception as exc:
        return {
            "schema": "mosim.mworks_controller_output_replay_publish.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }

    if args.publish_rate_hz <= 0.0:
        raise SystemExit("--publish-rate-hz must be positive")

    rclpy.init()
    node = rclpy.create_node("mosim_mworks_controller_output_replay")
    publisher = node.create_publisher(ControllerOutput, args.topic, 10)
    published = 0
    try:
        deadline = time.time() + args.discovery_wait_s
        while time.time() < deadline:
            rclpy.spin_once(node, timeout_sec=0.05)

        period = 1.0 / args.publish_rate_hz
        next_tick = time.monotonic()
        for sample in samples:
            now_msg = node.get_clock().now().to_msg()
            message = ControllerOutput()
            message.header.stamp = now_msg
            message.header.frame_id = sample["command_frame"]
            message.sequence = int(sample["sequence"])
            message.vehicle_id = str(sample["vehicle_id"])
            message.command_type = str(sample["command_type"])
            message.command = [float(item) for item in sample["command"]]
            message.command_frame = str(sample["command_frame"])
            message.mode = str(sample["mode"])
            message.status = str(sample["status"])
            message.backend = str(sample["backend"])
            message.saturation = bool(sample["saturation"])
            message.source_authority = str(sample["source_authority"])
            publisher.publish(message)
            published += 1
            rclpy.spin_once(node, timeout_sec=0.0)
            next_tick += period
            time.sleep(max(0.0, next_tick - time.monotonic()))
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return {
        "schema": "mosim.mworks_controller_output_replay_publish.v1",
        "status": "published",
        "topic": args.topic,
        "type": "mosim_msgs/msg/ControllerOutput",
        "published_count": published,
        "claim_boundary": "publish result only; Gazebo runtime and closed-loop performance require separate evidence",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT_CSV)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--output-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--time-column", default="time")
    parser.add_argument("--command-columns", nargs=4, default=["u1", "u2", "u3", "u4"])
    parser.add_argument("--signed-hover", nargs=4, type=float, default=DEFAULT_SIGNED_HOVER)
    parser.add_argument("--legacy-hover-motor-speed-cmd", type=float, default=DEFAULT_LEGACY_HOVER_CMD)
    parser.add_argument("--mworks-hover-motor-speed-cmd", type=float, default=DEFAULT_MWORKS_HOVER_CMD)
    parser.add_argument("--gazebo-hover-normalized-command", type=float, default=DEFAULT_GAZEBO_HOVER_NORMALIZED)
    parser.add_argument("--command-min", type=float, default=0.0)
    parser.add_argument("--command-max", type=float, default=1.0)
    parser.add_argument("--max-rate-hz", type=float, default=20.0)
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--command-type", default="normalized_motor_speed")
    parser.add_argument("--command-frame", default="body_motor_order_rotor_0_1_2_3")
    parser.add_argument("--mode", default="mworks_csv_replay")
    parser.add_argument("--status", default="valid")
    parser.add_argument("--backend", default="mworks_csv_replay")
    parser.add_argument("--source-authority", default="mworks_accepted_csv_delta_hover_mapper_bridge")
    parser.add_argument("--base-unix", type=float, default=0.0)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--topic", default="/mosim/sunray150/controller_output")
    parser.add_argument("--publish-rate-hz", type=float, default=20.0)
    parser.add_argument("--publish-report-json", type=Path)
    parser.add_argument("--discovery-wait-s", type=float, default=0.8)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    samples, manifest = build_samples(args)
    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0 if samples else 1

    write_outputs(args, samples, manifest)
    if args.publish:
        publish_report = publish_samples(args, samples)
        manifest["publish"] = publish_report
        project_path(args.output_manifest).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if args.publish_report_json is not None:
            project_path(args.publish_report_json).write_text(
                json.dumps(publish_report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(publish_report, ensure_ascii=False, indent=2))
        return 0 if publish_report.get("status") == "published" else 1

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if samples else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
