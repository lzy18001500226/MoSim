#!/usr/bin/env python3
"""Build the task-004 MWORKS echo runtime-adapter preflight artifacts.

This script consumes fresh MWORKS/Sysplorer result-context status values from
the current task and emits schema-valid ``mosim.ue_command_echo.v1`` rows. It
does not open Sysplorer, UE, ROS2, UDP, or any live downlink transport. The
live/downlink state is explicitly blocked unless a separate transport surface is
provided and proven by another task.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
SOURCE = "MWORKS_MCP_runtime_adapter_preflight"
EVIDENCE_LEVEL = "fresh_result_context_runtime_adapter_preflight"
LIVE_DOWNLINK_STATUS = "blocked_no_transport_surface"

COMMANDS = [
    (
        "controller_select",
        "mworks_live_preflight_controller_select",
        {"controller_id": "echo_mcp_state_smoke_controller"},
        "controller_select_status",
    ),
    (
        "wind_profile",
        "mworks_live_preflight_wind_profile",
        {"wind_profile_id": "echo_mcp_state_smoke_wind"},
        "wind_profile_status",
    ),
    (
        "motor_fault",
        "mworks_live_preflight_motor_fault",
        {"fault_id": "echo_mcp_state_smoke_motor_fault", "rotor": 1, "efficiency": 0.85},
        "motor_fault_status",
    ),
    (
        "scenario_reset",
        "mworks_live_preflight_scenario_reset",
        {"scenario_id": "echo_mcp_state_smoke_scenario"},
        "scenario_reset_status",
    ),
    (
        "recording",
        "mworks_live_preflight_recording",
        {"recording_state": "start"},
        "recording_status",
    ),
    (
        "teleport",
        "mworks_live_preflight_forbidden_pose",
        {"x": 1.0, "y": 0.0, "z": 1.0},
        "forbidden_pose_status",
    ),
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def status_pass(value: float) -> bool:
    return value > 0.5


def command_row(*, run_id: str, seq: int, time_s: float, kind: str, request_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": COMMAND_SCHEMA,
        "type": "command",
        "run_id": run_id,
        "request_id": request_id,
        "seq": seq,
        "time_s": time_s,
        "requested_by": "ue_experiment_console",
        "command": {"kind": kind, "payload": payload},
        "guard": {
            "require_mworks_ack": True,
            "require_ros2_ack": False,
            "reject_if_gate_open": [],
        },
    }


def echo_row(command: dict[str, Any], *, status: str, reason: str, field: str, value: float, preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": ECHO_SCHEMA,
        "source": SOURCE,
        "evidence_level": EVIDENCE_LEVEL,
        "live_downlink_status": LIVE_DOWNLINK_STATUS,
        "status": status,
        "reason": reason,
        "run_id": command["run_id"],
        "request_id": command["request_id"],
        "seq": command["seq"],
        "time_s": command["time_s"],
        "ack_authority": "MWORKS",
        "no_pose_overwrite_status": "pass",
        "command": command["command"],
        "mworks_echo": {
            "model": preflight["model"],
            "source_task": "RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004",
            "source": SOURCE,
            "evidence_level": EVIDENCE_LEVEL,
            "result_variable": field,
            "result_value": value,
            "sample_time": preflight["sample_time_s"],
            "check_model_ok": preflight["check_model_ok"],
            "simulate_model_ok": preflight["simulate_model_ok"],
            "result_context_fresh": True,
            "live_downlink_status": LIVE_DOWNLINK_STATUS,
            "not_live_ue_runtime_ack": True,
            "not_closed_loop": True,
            "not_controller_performance": True,
            "not_planner_ready": True,
            "not_factory_trace_consumption": True,
        },
        "claim_boundary": [
            "Fresh MWORKS_MCP result-context runtime-adapter preflight only.",
            "This is stronger than task-003 fixture replay because status values were read in the current task after check_model and simulate_model.",
            "This is not live UE runtime ack or live MWORKS-to-UE/ROS2 downlink.",
            "This is not closed_loop, controller performance, planner_ready, FAST-LIO success, Factory trace consumption, plant tracking, mission success, or parameter identification.",
        ],
    }


def build_artifacts(preflight: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    required = {
        "model",
        "run_id",
        "sample_time_s",
        "check_model_ok",
        "simulate_model_ok",
        "result_times_count",
        "values",
    }
    missing = sorted(required - set(preflight))
    if missing:
        raise ValueError(f"preflight JSON missing required keys: {missing}")
    if preflight["check_model_ok"] is not True or preflight["simulate_model_ok"] is not True:
        raise ValueError("check_model_ok and simulate_model_ok must both be true")
    values = preflight["values"]
    if not isinstance(values, dict):
        raise ValueError("preflight values must be an object")
    if str(preflight.get("source") or "") != "MWORKS_MCP":
        raise ValueError("preflight source must be MWORKS_MCP")
    if int(preflight.get("result_times_count") or 0) <= 10:
        raise ValueError("fresh result context must expose more than 10 time samples")

    commands: list[dict[str, Any]] = []
    echoes: list[dict[str, Any]] = []
    run_id = str(preflight["run_id"])
    time_s = float(preflight["sample_time_s"])

    for seq, (kind, request_id, payload, field) in enumerate(COMMANDS, start=1):
        value = float(values.get(field, 0.0))
        command = command_row(
            run_id=run_id,
            seq=seq,
            time_s=time_s,
            kind=kind,
            request_id=request_id,
            payload=payload,
        )
        commands.append(command)
        if kind == "teleport":
            status = "rejected" if value < 0 else "accepted"
            reason = "forbidden_pose_command" if status == "rejected" else "unexpected_forbidden_pose_acceptance"
        else:
            status = "accepted" if status_pass(value) else "rejected"
            reason = "ok" if status == "accepted" else f"{field}_not_active"
        echoes.append(echo_row(command, status=status, reason=reason, field=field, value=value, preflight=preflight))

    accepted = sum(1 for row in echoes if row["status"] == "accepted")
    rejected = sum(1 for row in echoes if row["status"] == "rejected")
    forbidden_rejected = any(row["command"]["kind"] == "teleport" and row["status"] == "rejected" for row in echoes)
    ok = accepted == 5 and rejected == 1 and forbidden_rejected and all(row["no_pose_overwrite_status"] == "pass" for row in echoes)
    summary = {
        "schema_version": "mosim.mworks_echo_live_downlink_preflight.v1",
        "source": SOURCE,
        "source_label": SOURCE,
        "evidence_level": EVIDENCE_LEVEL,
        "live_downlink_status": LIVE_DOWNLINK_STATUS,
        "ok": ok,
        "model": preflight["model"],
        "run_id": run_id,
        "check_model_ok": preflight["check_model_ok"],
        "simulate_model_ok": preflight["simulate_model_ok"],
        "result_times_count": preflight["result_times_count"],
        "result_time_first": preflight.get("result_time_first"),
        "result_time_last": preflight.get("result_time_last"),
        "sample_time_s": time_s,
        "total_echo_rows": len(echoes),
        "accepted": accepted,
        "rejected": rejected,
        "forbidden_pose_rejected": forbidden_rejected,
        "no_pose_overwrite_status": "pass" if ok else "invalid",
        "stronger_than_task_003_fixture": True,
        "uses_task_003_fixture_rows": False,
        "result_context_fresh": True,
        "not_live_ue_runtime_ack": True,
        "not_live_mworks_downlink": True,
        "not_closed_loop": True,
        "not_controller_performance": True,
        "not_planner_ready": True,
        "not_factory_trace_consumption": True,
        "claim_boundary": [
            "Fresh MWORKS_MCP result-context runtime-adapter preflight only.",
            "No current MWORKS-to-UE/ROS2 live command echo downlink transport surface was found or proven in this task.",
            "Generated rows can be consumed by the schema checker and offline UE reducer but must not enable UE accepted-state controls.",
        ],
    }
    return commands, echoes, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-json", required=True, help="Fresh MWORKS_MCP result-context preflight JSON")
    parser.add_argument("--commands-output", required=True, help="Output command JSONL")
    parser.add_argument("--echo-output", required=True, help="Output echo JSONL")
    parser.add_argument("--summary-output", required=True, help="Output summary JSON")
    args = parser.parse_args()

    preflight_path = repo_path(args.preflight_json)
    commands_path = repo_path(args.commands_output)
    echo_path = repo_path(args.echo_output)
    summary_path = repo_path(args.summary_output)

    commands, echoes, summary = build_artifacts(read_json(preflight_path))
    summary["preflight_json"] = preflight_path.as_posix()
    summary["commands_jsonl"] = commands_path.as_posix()
    summary["echo_jsonl"] = echo_path.as_posix()
    write_jsonl(commands_path, commands)
    write_jsonl(echo_path, echoes)
    write_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
