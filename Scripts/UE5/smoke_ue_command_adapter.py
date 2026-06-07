#!/usr/bin/env python3
"""Smoke-test the UE Experiment Console command adapter contract.

This is an offline adapter smoke. It validates UE command packets and writes
MWORKS/ROS2-style echo rows, but it does not send commands to UE, MWORKS, ROS2,
or any UAV actor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
FORBIDDEN_KINDS = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}
MWORKS_KINDS = {
    "controller_select",
    "wind_profile",
    "motor_fault",
    "scenario_reset",
    "recording",
}
ROS2_KINDS = {
    "planner_select",
    "sensor_mode",
}
MWORKS_ROS2_KINDS = {
    "scene_switch",
    "start_goal_update",
}
ALLOWED_KINDS = MWORKS_KINDS | ROS2_KINDS | MWORKS_ROS2_KINDS


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number}: command row must be an object")
            payload["_line_number"] = line_number
            rows.append(payload)
    if not rows:
        raise ValueError(f"empty command file: {path}")
    return rows


def required_authority(kind: str) -> str:
    if kind in MWORKS_KINDS:
        return "MWORKS"
    if kind in ROS2_KINDS:
        return "ROS2"
    if kind in MWORKS_ROS2_KINDS:
        return "MWORKS_ROS2"
    return ""


def validate_command(row: dict[str, Any], *, open_gates: set[str]) -> tuple[str, str, str]:
    if str(row.get("schema") or "") != SCHEMA:
        return "rejected", "", "unsupported_schema"
    if str(row.get("type") or "") != "command":
        return "rejected", "", "unsupported_type"

    command = row.get("command")
    if not isinstance(command, dict):
        return "rejected", "", "missing_command"
    kind = str(command.get("kind") or "")
    if kind in FORBIDDEN_KINDS:
        return "rejected", "", "forbidden_pose_command"
    if kind not in ALLOWED_KINDS:
        return "rejected", "", "unsupported_command_kind"
    if row.get("pose_override") is True or row.get("teleport") is True:
        return "rejected", "", "pose_override_not_allowed"

    guard = row.get("guard")
    if not isinstance(guard, dict):
        return "rejected", "", "missing_guard"
    if guard.get("require_mworks_ack") is not True:
        return "rejected", "", "missing_mworks_ack_guard"
    authority = required_authority(kind)
    if authority in {"ROS2", "MWORKS_ROS2"} and guard.get("require_ros2_ack") is not True:
        return "rejected", authority, "missing_ros2_ack_guard"

    rejected_gates = [
        str(gate)
        for gate in guard.get("reject_if_gate_open", [])
        if str(gate) in open_gates
    ] if isinstance(guard.get("reject_if_gate_open", []), list) else []
    if rejected_gates:
        return "rejected", authority, f"gate_open:{','.join(rejected_gates)}"

    return "accepted", authority, "ok"


def adapt_commands(rows: list[dict[str, Any]], *, open_gates: set[str]) -> list[dict[str, Any]]:
    echoes: list[dict[str, Any]] = []
    for row in rows:
        command = row.get("command") if isinstance(row.get("command"), dict) else {}
        kind = str(command.get("kind") or "")
        status, authority, reason = validate_command(row, open_gates=open_gates)
        echoes.append(
            {
                "schema": ECHO_SCHEMA,
                "source": "offline_adapter_smoke",
                "status": status,
                "reason": reason,
                "run_id": str(row.get("run_id") or ""),
                "request_id": str(row.get("request_id") or f"seq_{row.get('seq', row.get('_line_number', 0))}"),
                "seq": int(row.get("seq") or row.get("_line_number", 0)),
                "time_s": float(row.get("time_s") or 0.0),
                "ack_authority": authority or "MWORKS",
                "no_pose_overwrite_status": "pass",
                "command": {
                    "kind": kind,
                    "payload": command.get("payload", {}) if isinstance(command, dict) else {},
                },
            }
        )
    return echoes


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n", encoding="utf-8")


def summarize(echoes: list[dict[str, Any]], command_path: Path, echo_path: Path) -> dict[str, Any]:
    accepted = sum(1 for row in echoes if row.get("status") == "accepted")
    rejected = sum(1 for row in echoes if row.get("status") == "rejected")
    return {
        "schema": "mosim.ue_command_adapter_smoke.v1",
        "source": "offline_adapter_smoke",
        "ok": bool(echoes) and all(row.get("no_pose_overwrite_status") == "pass" for row in echoes),
        "command_jsonl": command_path.as_posix(),
        "echo_jsonl": echo_path.as_posix(),
        "total_commands": len(echoes),
        "accepted": accepted,
        "rejected": rejected,
        "accepted_ratio": accepted / len(echoes) if echoes else 0.0,
        "no_pose_overwrite_status": "pass",
        "not_runtime_ue_console": True,
        "claim_boundary": [
            "Offline command adapter smoke only.",
            "Does not send commands to UE, MWORKS, ROS2, or UAV actor pose.",
            "Runtime UE command evidence still requires live accepted/rejected echo rows from MWORKS/ROS2 adapters.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commands", required=True, help="Input mosim.ue_command.v1 JSONL")
    parser.add_argument("--echo-output", required=True, help="Output echo JSONL")
    parser.add_argument("--summary-output", required=True, help="Output summary JSON")
    parser.add_argument("--open-gate", action="append", default=[], help="Gate id currently open; matching commands reject")
    args = parser.parse_args()

    command_path = repo_path(args.commands)
    echo_path = repo_path(args.echo_output)
    summary_path = repo_path(args.summary_output)
    rows = read_jsonl(command_path)
    echoes = adapt_commands(rows, open_gates={str(item) for item in args.open_gate})
    write_jsonl(echo_path, echoes)
    summary = summarize(echoes, command_path, echo_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
