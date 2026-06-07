#!/usr/bin/env python3
"""Offline smoke for the MWORKS-owned command echo producer contract.

This is a schema/static mapping smoke only. It does not call Sysplorer, MWORKS,
ROS2, UE, or any UAV actor. Runtime acceptance still requires MWORKS_MCP or
MWORKS_GUI evidence from a future adapter/model gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"

MWORKS_OWNED_KINDS = {
    "controller_select",
    "wind_profile",
    "motor_fault",
    "scenario_reset",
    "recording",
}
ROS2_OR_SHARED_KINDS = {
    "planner_select",
    "sensor_mode",
    "scene_switch",
    "start_goal_update",
}
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


def command_kind(row: dict[str, Any]) -> str:
    command = row.get("command")
    if isinstance(command, dict):
        return str(command.get("kind") or "")
    return ""


def validate_mworks_command(row: dict[str, Any], *, open_gates: set[str]) -> tuple[str, str]:
    if str(row.get("schema") or "") != COMMAND_SCHEMA:
        return "rejected", "unsupported_schema"
    if str(row.get("type") or "") != "command":
        return "rejected", "unsupported_type"
    if str(row.get("requested_by") or "") != "ue_experiment_console":
        return "rejected", "unsupported_request_source"

    command = row.get("command")
    if not isinstance(command, dict):
        return "rejected", "missing_command"
    kind = command_kind(row)
    if kind in FORBIDDEN_KINDS:
        return "rejected", "forbidden_pose_command"
    if row.get("pose_override") is True or row.get("teleport") is True:
        return "rejected", "pose_override_not_allowed"
    if kind in ROS2_OR_SHARED_KINDS:
        return "rejected", "requires_ros2_or_mworks_ros2_authority"
    if kind not in MWORKS_OWNED_KINDS:
        return "rejected", "unsupported_command_kind"

    guard = row.get("guard")
    if not isinstance(guard, dict):
        return "rejected", "missing_guard"
    if guard.get("require_mworks_ack") is not True:
        return "rejected", "missing_mworks_ack_guard"

    reject_if_gate_open = guard.get("reject_if_gate_open", [])
    rejected_gates = []
    if isinstance(reject_if_gate_open, list):
        rejected_gates = [str(gate) for gate in reject_if_gate_open if str(gate) in open_gates]
    if rejected_gates:
        return "rejected", f"gate_open:{','.join(rejected_gates)}"

    payload = command.get("payload", {})
    if not isinstance(payload, dict):
        return "rejected", "payload_must_be_object"

    if kind == "controller_select" and not payload.get("controller_id"):
        return "rejected", "missing_controller_id"
    if kind == "wind_profile" and not payload.get("wind_profile_id"):
        return "rejected", "missing_wind_profile_id"
    if kind == "motor_fault":
        rotor = payload.get("rotor")
        severity = payload.get("severity", payload.get("efficiency"))
        if rotor is None or severity is None:
            return "rejected", "missing_motor_fault_target_or_severity"
    if kind == "scenario_reset" and not payload.get("scenario_id"):
        return "rejected", "missing_scenario_id"
    if kind == "recording" and not payload.get("recording_state"):
        return "rejected", "missing_recording_state"

    return "accepted", "ok"


def mworks_echo_payload(row: dict[str, Any], *, status: str, reason: str) -> dict[str, Any]:
    command = row.get("command") if isinstance(row.get("command"), dict) else {}
    payload = command.get("payload", {}) if isinstance(command, dict) else {}
    if not isinstance(payload, dict):
        payload = {}
    kind = command_kind(row)
    echo: dict[str, Any] = {
        "schema": ECHO_SCHEMA,
        "source": "offline_adapter_smoke",
        "status": status,
        "reason": reason,
        "run_id": str(row.get("run_id") or ""),
        "request_id": str(row.get("request_id") or f"seq_{row.get('seq', row.get('_line_number', 0))}"),
        "seq": int(row.get("seq") or row.get("_line_number", 0)),
        "time_s": float(row.get("time_s") or 0.0),
        "ack_authority": "MWORKS",
        "no_pose_overwrite_status": "pass",
        "command": {
            "kind": kind,
            "payload": payload,
        },
        "mworks_echo": {
            "active_controller_id": payload.get("controller_id") if kind == "controller_select" and status == "accepted" else None,
            "active_wind_profile_id": payload.get("wind_profile_id") if kind == "wind_profile" and status == "accepted" else None,
            "active_fault_id": payload.get("fault_id") if kind == "motor_fault" and status == "accepted" else None,
            "accepted_scenario_id": payload.get("scenario_id") if kind == "scenario_reset" and status == "accepted" else None,
            "recording_state": payload.get("recording_state") if kind == "recording" and status == "accepted" else None,
            "evidence_level": "offline_schema_smoke_only",
            "not_runtime_mworks_ack": True,
        },
        "claim_boundary": [
            "Offline MWORKS command echo producer smoke only.",
            "Does not call Sysplorer, MWORKS, ROS2, UE, or UAV actor pose.",
            "Accepted rows validate schema/static mapping only and are not live runtime acknowledgement.",
        ],
    }
    if kind == "motor_fault" and status == "accepted":
        echo["mworks_echo"]["affected_rotor"] = payload.get("rotor")
        echo["mworks_echo"]["fault_severity"] = payload.get("severity", payload.get("efficiency"))
    return echo


def adapt_commands(rows: list[dict[str, Any]], *, open_gates: set[str]) -> list[dict[str, Any]]:
    echoes: list[dict[str, Any]] = []
    for row in rows:
        status, reason = validate_mworks_command(row, open_gates=open_gates)
        echoes.append(mworks_echo_payload(row, status=status, reason=reason))
    return echoes


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def summarize(echoes: list[dict[str, Any]], command_path: Path, echo_path: Path) -> dict[str, Any]:
    accepted = sum(1 for row in echoes if row.get("status") == "accepted")
    rejected = sum(1 for row in echoes if row.get("status") == "rejected")
    ros2_owned_rejected = sum(
        1 for row in echoes
        if row.get("reason") == "requires_ros2_or_mworks_ros2_authority"
    )
    return {
        "schema": "mosim.mworks_command_echo_producer_smoke.v1",
        "source": "offline_adapter_smoke",
        "ok": bool(echoes)
        and all(row.get("ack_authority") == "MWORKS" for row in echoes)
        and all(row.get("no_pose_overwrite_status") == "pass" for row in echoes),
        "command_jsonl": command_path.as_posix(),
        "echo_jsonl": echo_path.as_posix(),
        "total_commands": len(echoes),
        "accepted": accepted,
        "rejected": rejected,
        "ros2_or_shared_commands_rejected": ros2_owned_rejected,
        "not_runtime_mworks_ack": True,
        "not_live_ue_console": True,
        "not_closed_loop": True,
        "not_controller_performance": True,
        "not_planner_ready": True,
        "claim_boundary": [
            "Offline MWORKS command echo producer smoke only.",
            "Accepted rows are schema/static mapping evidence, not runtime MWORKS acknowledgement.",
            "ROS2-owned or shared commands must not be accepted by this MWORKS-only smoke.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commands", required=True, help="Input mosim.ue_command.v1 JSONL")
    parser.add_argument("--echo-output", required=True, help="Output MWORKS echo JSONL")
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
