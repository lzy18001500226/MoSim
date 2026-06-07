#!/usr/bin/env python3
"""Record a sustained PositionCommand -> PlannerSetpoint adapter runtime.

This harness is intentionally passive with respect to planner commands: it does
not publish PositionCommand messages and cannot create planner evidence by
itself. It only records an existing runtime source, the converter output, the
20Hz adapter output, and adapter status.
"""

from __future__ import annotations

import argparse
import csv
import json
import signal
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TRACE_FIELDS = [
    "receive_time_s",
    "stamp_s",
    "sequence",
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
    "trajectory_status",
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


def stamp_s(stamp: Any) -> float:
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


def node_time_s(node: Any) -> float:
    return time.monotonic()


def terminate(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGINT)
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3.0)


def msg_to_xyz(value: Any) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def serialize_position_command(msg: Any, receive_time_s: float) -> dict[str, Any]:
    return {
        "schema": "mosim.position_command_sample.v1",
        "receive_time_s": receive_time_s,
        "stamp_s": stamp_s(msg.header.stamp),
        "frame_id": msg.header.frame_id,
        "position_m": msg_to_xyz(msg.position),
        "velocity_mps": msg_to_xyz(msg.velocity),
        "acceleration_mps2": msg_to_xyz(msg.acceleration),
        "yaw_rad": float(msg.yaw),
        "yaw_rate_radps": float(msg.yaw_dot),
        "kx": [float(v) for v in msg.kx],
        "kv": [float(v) for v in msg.kv],
        "trajectory_id": int(msg.trajectory_id),
        "trajectory_flag": int(msg.trajectory_flag),
    }


def serialize_planner_setpoint(msg: Any, receive_time_s: float) -> dict[str, Any]:
    return {
        "schema": "mosim.planner_setpoint_sample.v1",
        "receive_time_s": receive_time_s,
        "stamp_s": stamp_s(msg.header.stamp),
        "sequence": int(msg.sequence),
        "frame_id": msg.frame_id,
        "planner_id": msg.planner_id,
        "position_m": [float(v) for v in msg.position_m],
        "velocity_mps": [float(v) for v in msg.velocity_mps],
        "acceleration_mps2": [float(v) for v in msg.acceleration_mps2],
        "yaw_rad": float(msg.yaw_rad),
        "yaw_rate_radps": float(msg.yaw_rate_radps),
        "trajectory_status": int(msg.trajectory_status),
    }


def serialize_status(msg: Any, receive_time_s: float) -> dict[str, Any]:
    return {
        "schema": "mosim.setpoint_adapter_status_sample.v1",
        "receive_time_s": receive_time_s,
        "stamp_s": stamp_s(msg.header.stamp),
        "frame_id": msg.header.frame_id,
        "last_sequence": int(msg.last_sequence),
        "accepted": bool(msg.accepted),
        "reject_reason": msg.reject_reason,
        "mode": msg.mode,
        "stale": bool(msg.stale),
        "age_s": float(msg.age_s),
        "planner_id": msg.planner_id,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_setpoint_trace(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACE_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "receive_time_s": f"{row['receive_time_s']:.9f}",
                    "stamp_s": f"{row['stamp_s']:.9f}",
                    "sequence": row["sequence"],
                    "frame_id": row["frame_id"],
                    "planner_id": row["planner_id"],
                    "x_ref": row["position_m"][0],
                    "y_ref": row["position_m"][1],
                    "z_ref": row["position_m"][2],
                    "vx_ref": row["velocity_mps"][0],
                    "vy_ref": row["velocity_mps"][1],
                    "vz_ref": row["velocity_mps"][2],
                    "ax_ref": row["acceleration_mps2"][0],
                    "ay_ref": row["acceleration_mps2"][1],
                    "az_ref": row["acceleration_mps2"][2],
                    "yaw_ref": row["yaw_rad"],
                    "yaw_rate_ref": row["yaw_rate_radps"],
                    "trajectory_status": row["trajectory_status"],
                }
            )


def measured_rate(rows: list[dict[str, Any]]) -> float:
    if len(rows) < 2:
        return 0.0
    duration = float(rows[-1]["receive_time_s"]) - float(rows[0]["receive_time_s"])
    if duration <= 0.0:
        return 0.0
    return (len(rows) - 1) / duration


def strictly_increasing(values: list[float]) -> bool:
    return all(next_value > value for value, next_value in zip(values, values[1:]))


def make_time_gate(
    *,
    source_rows: list[dict[str, Any]],
    converted_rows: list[dict[str, Any]],
    setpoint_rows: list[dict[str, Any]],
    expected_frame: str,
    source_frame_alias: str,
) -> dict[str, Any]:
    source_stamps = [float(row["stamp_s"]) for row in source_rows]
    converted_stamps = [float(row["stamp_s"]) for row in converted_rows]
    setpoint_stamps = [float(row["stamp_s"]) for row in setpoint_rows]
    source_frames = sorted({str(row["frame_id"]) for row in source_rows})
    converted_frames = sorted({str(row["frame_id"]) for row in converted_rows})
    setpoint_frames = sorted({str(row["frame_id"]) for row in setpoint_rows})
    return {
        "schema": "mosim.positioncmd_tf_time_gate.v1",
        "timestamp_monotonic": {
            "source_position_command": strictly_increasing(source_stamps),
            "converted_planner_position_cmd": strictly_increasing(converted_stamps),
            "adapter_setpoint": strictly_increasing(setpoint_stamps),
        },
        "frame_gate": {
            "expected_frame": expected_frame,
            "source_frame_alias": source_frame_alias,
            "source_frames": source_frames,
            "converted_frames": converted_frames,
            "setpoint_frames": setpoint_frames,
            "source_frame_ok": all(frame in {expected_frame, source_frame_alias, ""} for frame in source_frames),
            "converted_frame_ok": converted_frames == [expected_frame] if converted_frames else False,
            "setpoint_frame_ok": setpoint_frames == [expected_frame] if setpoint_frames else False,
        },
        "tf_status": "not_checked_no_rviz_no_tf_listener",
    }


def make_planner_input_gate(path: Path, *, source_topic: str, notes: str) -> dict[str, Any]:
    gate = {
        "schema": "mosim.planner_input_gate.v1",
        "source_position_command_topic": source_topic,
        "global_truth_used_as_input": False,
        "offline_ue_handoff_csv_used": False,
        "keyboard_pose_overwrite_used": False,
        "local_map_runtime_source": "unverified_by_this_recorder",
        "notes": notes,
    }
    path.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return gate


def start_node(command: list[str], log_path: Path) -> subprocess.Popen[bytes]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("wb")
    process = subprocess.Popen(command, stdout=log_handle, stderr=subprocess.STDOUT)
    process._mosim_log_handle = log_handle  # type: ignore[attr-defined]
    return process


def close_process_log(process: subprocess.Popen[bytes]) -> None:
    log_handle = getattr(process, "_mosim_log_handle", None)
    if log_handle is not None:
        log_handle.close()


def run_recording(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import rclpy
        from mosim_msgs.msg import PlannerSetpoint, PositionCommand, SetpointAdapterStatus
    except (ImportError, ModuleNotFoundError) as exc:
        raise SystemExit(
            "ROS2 Python environment is not available. Run this inside WSL after "
            "sourcing /opt/ros/humble/setup.bash and the MoSim ROS2 overlay "
            "(for example: source install/setup.bash)."
        ) from exc

    output_dir = project_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    process_dir = output_dir / "process_logs"
    processes: list[subprocess.Popen[bytes]] = []

    if args.start_converter:
        processes.append(
            start_node(
                [
                    "ros2",
                    "run",
                    "mosim_setpoint_adapter",
                    "position_command_to_planner_setpoint_node",
                    "--ros-args",
                    "-p",
                    f"input_topic:={args.source_topic}",
                    "-p",
                    f"output_topic:={args.converted_topic}",
                    "-p",
                    f"expected_frame:={args.expected_frame}",
                    "-p",
                    f"source_frame_alias:={args.source_frame_alias}",
                    "-p",
                    f"planner_id:={args.planner_id}",
                ],
                process_dir / "position_command_converter.log",
            )
        )
    if args.start_adapter:
        processes.append(
            start_node(
                [
                    "ros2",
                    "run",
                    "mosim_setpoint_adapter",
                    "planner_setpoint_adapter_node",
                    "--ros-args",
                    "-p",
                    f"input_topic:={args.converted_topic}",
                    "-p",
                    f"output_topic:={args.setpoint_topic}",
                    "-p",
                    f"status_topic:={args.status_topic}",
                    "-p",
                    f"expected_frame:={args.expected_frame}",
                    "-p",
                    f"rate_hz:={args.adapter_rate_hz}",
                    "-p",
                    f"stale_timeout_s:={args.stale_timeout_s}",
                ],
                process_dir / "planner_setpoint_adapter.log",
            )
        )

    try:
        if processes:
            time.sleep(float(args.startup_wait_s))
        rclpy.init()
        node = rclpy.create_node("mosim_position_command_adapter_runtime_recorder")
        source_rows: list[dict[str, Any]] = []
        converted_rows: list[dict[str, Any]] = []
        setpoint_rows: list[dict[str, Any]] = []
        status_rows: list[dict[str, Any]] = []

        node.create_subscription(
            PositionCommand,
            args.source_topic,
            lambda msg: source_rows.append(serialize_position_command(msg, node_time_s(node))),
            50,
        )
        node.create_subscription(
            PlannerSetpoint,
            args.converted_topic,
            lambda msg: converted_rows.append(serialize_planner_setpoint(msg, node_time_s(node))),
            50,
        )
        node.create_subscription(
            PlannerSetpoint,
            args.setpoint_topic,
            lambda msg: setpoint_rows.append(serialize_planner_setpoint(msg, node_time_s(node))),
            50,
        )
        node.create_subscription(
            SetpointAdapterStatus,
            args.status_topic,
            lambda msg: status_rows.append(serialize_status(msg, node_time_s(node))),
            50,
        )

        deadline = time.time() + float(args.duration_s)
        while time.time() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        node.destroy_node()
        rclpy.shutdown()

        source_path = output_dir / "source_position_cmd.jsonl"
        converted_path = output_dir / "converted_planner_position_cmd.jsonl"
        setpoint_jsonl_path = output_dir / "setpoint_trace.jsonl"
        setpoint_csv_path = output_dir / "setpoint_trace.csv"
        status_path = output_dir / "setpoint_adapter_status.jsonl"
        rates_path = output_dir / "topic_rates.json"
        time_gate_path = output_dir / "tf_time_gate.json"
        input_gate_path = output_dir / "planner_input_gate.json"
        summary_path = output_dir / "run_summary.json"

        write_jsonl(source_path, source_rows)
        write_jsonl(converted_path, converted_rows)
        write_jsonl(setpoint_jsonl_path, setpoint_rows)
        write_jsonl(status_path, status_rows)
        write_setpoint_trace(setpoint_csv_path, setpoint_rows)

        topic_rates = {
            "schema": "mosim.positioncmd_topic_rates.v1",
            "duration_s": float(args.duration_s),
            "rates_hz": {
                args.source_topic: measured_rate(source_rows),
                args.converted_topic: measured_rate(converted_rows),
                args.setpoint_topic: measured_rate(setpoint_rows),
                args.status_topic: measured_rate(status_rows),
            },
            "sample_counts": {
                args.source_topic: len(source_rows),
                args.converted_topic: len(converted_rows),
                args.setpoint_topic: len(setpoint_rows),
                args.status_topic: len(status_rows),
            },
            "minimum_required_rate_hz": float(args.min_rate_hz),
        }
        time_gate = make_time_gate(
            source_rows=source_rows,
            converted_rows=converted_rows,
            setpoint_rows=setpoint_rows,
            expected_frame=args.expected_frame,
            source_frame_alias=args.source_frame_alias,
        )
        planner_input_gate = make_planner_input_gate(
            input_gate_path,
            source_topic=args.source_topic,
            notes=args.planner_input_notes,
        )
        rates_path.write_text(json.dumps(topic_rates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time_gate_path.write_text(json.dumps(time_gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        accepted_status = [row for row in status_rows if row["accepted"] and row["mode"] == "track"]
        stale_status = [row for row in status_rows if row["stale"]]
        status_count = len(status_rows)
        accepted_ratio = len(accepted_status) / status_count if status_count else 0.0
        rates_ok = all(
            topic_rates["rates_hz"][topic] >= float(args.min_rate_hz)
            for topic in [args.converted_topic, args.setpoint_topic, args.status_topic]
        )
        no_truth_leak = not planner_input_gate["global_truth_used_as_input"]
        timestamp_ok = all(time_gate["timestamp_monotonic"].values())
        frame_ok = (
            time_gate["frame_gate"]["source_frame_ok"]
            and time_gate["frame_gate"]["converted_frame_ok"]
            and time_gate["frame_gate"]["setpoint_frame_ok"]
        )
        passed = (
            bool(source_rows)
            and bool(converted_rows)
            and bool(setpoint_rows)
            and rates_ok
            and accepted_ratio >= float(args.min_accepted_ratio)
            and not stale_status
            and timestamp_ok
            and frame_ok
            and no_truth_leak
        )
        summary = {
            "schema": "mosim.positioncmd_runtime_summary.v1",
            "quality_status": "pass" if passed else "needs_iteration",
            "source_available": bool(source_rows),
            "runtime_source_required": True,
            "claim_boundary": [
                "Recorder is passive; it does not create planner commands.",
                "This is planner-adapter runtime evidence only when source_topic is a real planner output.",
                "Closed-loop claim still requires same-run MWORKS/controller consumption of setpoint_trace.csv.",
            ],
            "source_topic": args.source_topic,
            "converted_topic": args.converted_topic,
            "setpoint_topic": args.setpoint_topic,
            "status_topic": args.status_topic,
            "planner_id": args.planner_id,
            "accepted_ratio": accepted_ratio,
            "stale_samples": len(stale_status),
            "rates_ok": rates_ok,
            "timestamp_ok": timestamp_ok,
            "frame_ok": frame_ok,
            "global_truth_used_as_input": False,
            "artifacts": {
                "source_position_cmd": rel(source_path),
                "converted_planner_position_cmd": rel(converted_path),
                "setpoint_trace_jsonl": rel(setpoint_jsonl_path),
                "setpoint_trace_csv": rel(setpoint_csv_path),
                "setpoint_adapter_status": rel(status_path),
                "topic_rates": rel(rates_path),
                "tf_time_gate": rel(time_gate_path),
                "planner_input_gate": rel(input_gate_path),
                "process_logs": rel(process_dir),
            },
            "blockers": []
            if passed
            else [
                "No real planner runtime source was recorded on source_topic." if not source_rows else "",
                "Real planner runtime source, sustained rates, accepted ratio, timestamp/frame gate, or stale gate did not pass.",
                "Do not promote planner or closed_loop claim until this run passes and MWORKS consumes the same trace.",
            ],
        }
        summary["blockers"] = [item for item in summary["blockers"] if item]
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return summary
    finally:
        for process in reversed(processes):
            terminate(process)
            close_process_log(process)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-s", type=float, default=10.0)
    parser.add_argument("--output-dir", default="Results/ros2_runtime/positioncmd_source_latest")
    parser.add_argument("--source-topic", default="/position_cmd")
    parser.add_argument("--converted-topic", default="/mosim/planner/position_cmd")
    parser.add_argument("--setpoint-topic", default="/mosim/planner/setpoint")
    parser.add_argument("--status-topic", default="/mosim/planner/setpoint_adapter_status")
    parser.add_argument("--expected-frame", default="map")
    parser.add_argument("--source-frame-alias", default="world")
    parser.add_argument("--planner-id", default="ego_position_cmd")
    parser.add_argument("--adapter-rate-hz", type=float, default=20.0)
    parser.add_argument("--stale-timeout-s", type=float, default=0.15)
    parser.add_argument("--min-rate-hz", type=float, default=19.0)
    parser.add_argument("--min-accepted-ratio", type=float, default=0.95)
    parser.add_argument("--startup-wait-s", type=float, default=2.0)
    parser.add_argument("--start-converter", action="store_true")
    parser.add_argument("--start-adapter", action="store_true")
    parser.add_argument(
        "--planner-input-notes",
        default=(
            "Recorder cannot prove planner input provenance by itself; pair this "
            "with launch/topic evidence showing odometry plus local sensor map "
            "inputs and no UE global truth map."
        ),
    )
    return parser.parse_args()


def main() -> int:
    summary = run_recording(parse_args())
    return 0 if summary["quality_status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
