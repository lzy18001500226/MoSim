#!/usr/bin/env python3
"""Smoke-test the UE command sender packet over UDP loopback.

This is an executable packet/transport contract for the UE Experiment Console
uplink shape. It sends mosim.ue_command.v1 rows to a local UDP socket and
validates the received packets. It does not run Unreal, MWORKS, ROS2, or any
runtime acknowledgement adapter.
"""

from __future__ import annotations

import argparse
import json
import socket
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mosim.ue_command.v1"
FORBIDDEN_KINDS = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def command(seq: int, kind: str, *, require_ros2: bool = False, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "type": "command",
        "run_id": "ue_sender_loopback_smoke",
        "request_id": f"loopback_cmd_{seq}",
        "seq": seq,
        "time_s": seq * 0.05,
        "requested_by": "ue_experiment_console",
        "command": {"kind": kind, "payload": payload or {}},
        "guard": {
            "require_mworks_ack": True,
            "require_ros2_ack": require_ros2,
            "reject_if_gate_open": ["p0_closed_loop_missing"],
        },
    }


def receive_udp(sock: socket.socket, expected_count: int, timeout_s: float) -> list[dict[str, Any]]:
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


def validate_received(rows: list[dict[str, Any]], expected_count: int) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if len(rows) != expected_count:
        issues.append(f"expected {expected_count} UDP packets, received {len(rows)}")
    for row in rows:
        if row.get("schema") != SCHEMA:
            issues.append("received packet has unsupported schema")
        if row.get("type") != "command":
            issues.append("received packet has unsupported type")
        if row.get("requested_by") != "ue_experiment_console":
            issues.append("received packet has unsupported requested_by")
        command_obj = row.get("command")
        if not isinstance(command_obj, dict):
            issues.append("received packet missing command object")
            continue
        kind = str(command_obj.get("kind") or "")
        if kind in FORBIDDEN_KINDS:
            issues.append(f"forbidden command kind was sent: {kind}")
        guard = row.get("guard")
        if not isinstance(guard, dict):
            issues.append("received packet missing guard object")
            continue
        if guard.get("require_mworks_ack") is not True:
            issues.append("received packet missing require_mworks_ack=true")
        if kind in {"planner_select", "sensor_mode", "scene_switch", "start_goal_update"} and guard.get("require_ros2_ack") is not True:
            issues.append(f"received {kind} without require_ros2_ack=true")
    return not issues, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary-output", required=True)
    parser.add_argument("--received-output", required=True)
    parser.add_argument("--timeout-s", type=float, default=2.0)
    args = parser.parse_args()

    rows = [
        command(1, "controller_select", payload={"controller_id": "linear_mpc_sysblock"}),
        command(2, "planner_select", require_ros2=True, payload={"planner_id": "ego_replan_fsm_candidate"}),
        command(3, "motor_fault", payload={"rotor": 1, "efficiency": 0.7}),
        command(4, "scene_switch", require_ros2=True, payload={"scene_id": "factoryenvironmentcollect"}),
    ]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind(("127.0.0.1", 0))
        port = int(receiver.getsockname()[1])
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            for row in rows:
                payload = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                sender.sendto(payload, ("127.0.0.1", port))
        received = receive_udp(receiver, len(rows), args.timeout_s)

    ok, issues = validate_received(received, len(rows))
    received_path = repo_path(args.received_output)
    received_path.parent.mkdir(parents=True, exist_ok=True)
    received_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in received) + "\n",
        encoding="utf-8",
    )
    summary = {
        "schema": "mosim.ue_command_sender_loopback_smoke.v1",
        "ok": ok,
        "source": "udp_loopback_smoke",
        "sent_packets": len(rows),
        "received_packets": len(received),
        "received_jsonl": display_path(received_path),
        "no_pose_overwrite_status": "pass" if ok else "unknown",
        "not_runtime_ue_console": True,
        "not_mworks_or_ros2_ack": True,
        "claim_boundary": [
            "UDP loopback packet smoke only.",
            "Does not run Unreal, MWORKS, ROS2, or any runtime acknowledgement adapter.",
            "Accepted state still requires mosim.ue_command_echo.v1 from MWORKS/ROS2 authority.",
        ],
        "issues": issues,
    }
    summary_path = repo_path(args.summary_output)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
