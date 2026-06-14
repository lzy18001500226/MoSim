#!/usr/bin/env python3
"""Smoke-test the accepted MWORKS run UE state stream over UDP loopback.

This proves the replay packets can be sent and captured through a real local
UDP socket. It does not run Unreal, MWORKS, ROS2, or any runtime acknowledgement
adapter.
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = (
    ROOT
    / "Results"
    / "ue_replay_input"
    / "20260612_rotor1_loss15_linear_mpc_online_fault_allocation"
    / "ue_replay_input_bundle.json"
)


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {rel(path)}")
    return payload


def receive_packets(sock: socket.socket, expected_count: int, timeout_s: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    deadline = time.monotonic() + timeout_s
    while len(rows) < expected_count and time.monotonic() < deadline:
        sock.settimeout(max(0.01, deadline - time.monotonic()))
        try:
            data, _addr = sock.recvfrom(65535)
        except socket.timeout:
            break
        rows.append(json.loads(data.decode("utf-8")))
    return rows


def run_loopback(
    *,
    bundle_path: Path,
    output_dir: Path,
    max_frames: int,
    timeout_s: float,
) -> dict[str, Any]:
    bundle = read_json(bundle_path)
    raw_path = repo_path(bundle["artifacts"]["raw"]["path"])
    scene_id = str(bundle["scene_binding"]["scene_id"])
    map_id = str(bundle["scene_binding"]["map_id"])
    expected_packets = max_frames + 2
    output_dir.mkdir(parents=True, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind(("127.0.0.1", 0))
        port = int(receiver.getsockname()[1])
        command = [
            sys.executable,
            "Scripts/UE5/stream_unreal_udp.py",
            rel(raw_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--scene-id",
            scene_id,
            "--map-id",
            map_id,
            "--max-frames",
            str(max_frames),
            "--no-sleep",
            "--disable-visual-helpers",
        ]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout_s)
        received = receive_packets(receiver, expected_packets, timeout_s)

    received_path = output_dir / "received_ue_state_packets.jsonl"
    received_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in received) + "\n",
        encoding="utf-8",
    )
    packet_types = [str(row.get("type", "")) for row in received]
    frames = [row for row in received if row.get("type") == "frame"]
    frame_scene_ids = sorted({str(row.get("scene_id", "")) for row in frames})
    frame_map_ids = sorted({str(row.get("map_id", "")) for row in frames})
    issues: list[str] = []
    if completed.returncode != 0:
        issues.append(f"stream_unreal_udp.py returned {completed.returncode}")
    if len(received) != expected_packets:
        issues.append(f"expected {expected_packets} UDP packets, received {len(received)}")
    if packet_types[:1] != ["hello"]:
        issues.append("first packet is not hello")
    if packet_types[-1:] != ["end"]:
        issues.append("last packet is not end")
    if len(frames) != max_frames:
        issues.append(f"expected {max_frames} frame packets, received {len(frames)}")
    if frame_scene_ids != [scene_id]:
        issues.append(f"frame scene_id mismatch: {frame_scene_ids}")
    if frame_map_ids != [map_id]:
        issues.append(f"frame map_id mismatch: {frame_map_ids}")
    for frame in frames:
        uav = frame.get("uav", {})
        if not isinstance(uav, dict) or "position_m" not in uav or "rpy_rad" not in uav:
            issues.append("frame missing uav pose fields")
            break
        if frame.get("status", {}).get("evidence_level") not in {"render_only_preview", "scene_truth_pipeline_replay"}:
            issues.append("frame status has unexpected evidence_level")
            break

    summary = {
        "schema": "mosim.mworks_accepted_run_ue_state_stream_loopback.v1",
        "ok": not issues,
        "bundle": rel(bundle_path),
        "raw_csv": rel(raw_path),
        "scene_id": scene_id,
        "map_id": map_id,
        "max_frames": max_frames,
        "stream_command": " ".join(command),
        "process_exit_code": completed.returncode,
        "received_packets": len(received),
        "received_frames": len(frames),
        "received_jsonl": rel(received_path),
        "packet_types": packet_types,
        "ue_editor_opened": False,
        "ue_runtime_started": False,
        "mworks_started": False,
        "ros2_started": False,
        "not_runtime_ue_ack": True,
        "not_controller_performance_evidence": True,
        "claim_boundary": [
            "Local UDP transport smoke for quadrotor.unreal_state.v1 replay packets only.",
            "Does not run Unreal Editor, UE runtime, MWORKS, ROS2, RViz, or command-echo acknowledgement.",
            "MWORKS metrics remain the controller-performance source.",
        ],
        "stdout_tail": (completed.stdout or "")[-1200:],
        "stderr_tail": (completed.stderr or "")[-1200:],
        "issues": issues,
    }
    (output_dir / "ue_state_stream_loopback.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# UE State Stream Loopback",
        "",
        f"Status: `{'pass' if summary['ok'] else 'fail'}`",
        f"Scene: `{scene_id}`",
        f"Map: `{map_id}`",
        f"Received packets: `{len(received)}`",
        f"Received frames: `{len(frames)}`",
        "",
        "This smoke used a real local UDP socket and did not open Unreal Editor or start UE runtime.",
        "",
        "## Boundary",
        "",
        "- Not UE runtime acknowledgement.",
        "- Not controller-performance evidence.",
        "- Not planner-ready or closed-loop evidence.",
    ]
    (output_dir / "ue_state_stream_loopback.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT
        / "Results"
        / "ue_replay_input"
        / "20260612_rotor1_loss15_linear_mpc_online_fault_allocation",
    )
    parser.add_argument("--max-frames", type=int, default=8)
    parser.add_argument("--timeout-s", type=float, default=8.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_frames <= 0:
        raise ValueError("--max-frames must be positive")
    summary = run_loopback(
        bundle_path=repo_path(args.bundle),
        output_dir=repo_path(args.output_dir),
        max_frames=args.max_frames,
        timeout_s=args.timeout_s,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
