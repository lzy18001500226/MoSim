#!/usr/bin/env python3
"""Adapt task-002 MWORKS_MCP echo-state samples into command-echo rows.

This is a result-context adapter smoke. It reads already-produced MWORKS_MCP
state evidence and emits ``mosim.ue_command_echo.v1`` fixture rows for contract
and reducer checks. It does not call MWORKS, Sysplorer, ROS2, UE, UDP, or any
live downlink.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
SOURCE = "MWORKS_MCP_result_adapter_smoke"
EVIDENCE_LEVEL = "result_context_adapter_smoke"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def read_samples(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path}: no sample rows")
    parsed: list[dict[str, float]] = []
    for row in rows:
        parsed.append({key: float(value) for key, value in row.items() if key and value not in {None, ""}})
    return parsed


def status_is_pass(value: float) -> bool:
    return value > 0.5


def command_row(
    *,
    run_id: str,
    seq: int,
    time_s: float,
    request_id: str,
    kind: str,
    payload: dict[str, Any],
    require_ros2_ack: bool = False,
) -> dict[str, Any]:
    return {
        "schema": COMMAND_SCHEMA,
        "type": "command",
        "run_id": run_id,
        "request_id": request_id,
        "seq": seq,
        "time_s": time_s,
        "requested_by": "ue_experiment_console",
        "command": {
            "kind": kind,
            "payload": payload,
        },
        "guard": {
            "require_mworks_ack": True,
            "require_ros2_ack": require_ros2_ack,
            "reject_if_gate_open": [],
        },
    }


def echo_row(
    command: dict[str, Any],
    *,
    status: str,
    reason: str,
    probe_path: Path,
    samples_path: Path,
    mworks_fields: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": ECHO_SCHEMA,
        "source": SOURCE,
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
            "evidence_level": EVIDENCE_LEVEL,
            "source_task": "RFLY-MOSIM-MWORKS-ECHO-MCP-STATE-SMOKE-20260606-002",
            "source_probe_json": probe_path.as_posix(),
            "source_samples_csv": samples_path.as_posix(),
            "not_live_mworks_downlink": True,
            "not_live_ue_runtime_ack": True,
            **mworks_fields,
        },
        "claim_boundary": [
            "MWORKS_MCP result-context adapter smoke only.",
            "Rows are adapted from task-002 result samples and are not live UE runtime ack.",
            "Rows are not live MWORKS downlink, closed_loop, controller performance, planner_ready, Factory trace consumption, plant tracking, or parameter identification.",
        ],
    }


def build_rows(probe: dict[str, Any], samples: list[dict[str, float]], *, probe_path: Path, samples_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if str(probe.get("source") or "") != "MWORKS_MCP":
        raise ValueError("task-002 probe source must be MWORKS_MCP")
    if str(probe.get("quality_status") or "") != "mworks_mcp_state_smoke_passed":
        raise ValueError("task-002 probe quality_status must be mworks_mcp_state_smoke_passed")
    latest = max(samples, key=lambda row: row["time"])
    if not status_is_pass(latest.get("no_pose_overwrite_status", 0.0)):
        raise ValueError("task-002 no_pose_overwrite_status is not pass-like")

    run_id = "mworks_mcp_result_adapter_smoke_20260606_003"
    commands = [
        command_row(
            run_id=run_id,
            seq=1,
            time_s=latest["time"],
            request_id="mworks_mcp_result_controller_select",
            kind="controller_select",
            payload={"controller_id": "mworks_mcp_state_smoke_controller"},
        ),
        command_row(
            run_id=run_id,
            seq=2,
            time_s=latest["time"],
            request_id="mworks_mcp_result_wind_profile",
            kind="wind_profile",
            payload={"wind_profile_id": "mworks_mcp_state_smoke_wind"},
        ),
        command_row(
            run_id=run_id,
            seq=3,
            time_s=latest["time"],
            request_id="mworks_mcp_result_motor_fault",
            kind="motor_fault",
            payload={"fault_id": "mworks_mcp_state_smoke_motor_fault", "rotor": 1, "efficiency": 0.85},
        ),
        command_row(
            run_id=run_id,
            seq=4,
            time_s=latest["time"],
            request_id="mworks_mcp_result_scenario_reset",
            kind="scenario_reset",
            payload={"scenario_id": "mworks_mcp_state_smoke_scenario"},
        ),
        command_row(
            run_id=run_id,
            seq=5,
            time_s=latest["time"],
            request_id="mworks_mcp_result_recording",
            kind="recording",
            payload={"recording_state": "start"},
        ),
        command_row(
            run_id=run_id,
            seq=6,
            time_s=latest["time"],
            request_id="mworks_mcp_result_forbidden_pose",
            kind="teleport",
            payload={"x": 1.0, "y": 0.0, "z": 1.0},
        ),
    ]
    status_by_kind = {
        "controller_select": ("controller_select_status", "accepted", "ok"),
        "wind_profile": ("wind_profile_status", "accepted", "ok"),
        "motor_fault": ("motor_fault_status", "accepted", "ok"),
        "scenario_reset": ("scenario_reset_status", "accepted", "ok"),
        "recording": ("recording_status", "accepted", "ok"),
        "teleport": ("forbidden_pose_status", "rejected", "forbidden_pose_command"),
    }

    echoes: list[dict[str, Any]] = []
    for command in commands:
        kind = command["command"]["kind"]
        field, accepted_status, accepted_reason = status_by_kind[kind]
        value = latest.get(field, 0.0)
        if kind == "teleport":
            status = "rejected" if value < 0.0 else "accepted"
            reason = "forbidden_pose_command" if status == "rejected" else "unexpected_forbidden_pose_acceptance"
        else:
            status = accepted_status if status_is_pass(value) else "rejected"
            reason = accepted_reason if status == "accepted" else f"{field}_not_active"
        echoes.append(
            echo_row(
                command,
                status=status,
                reason=reason,
                probe_path=probe_path,
                samples_path=samples_path,
                mworks_fields={
                    "result_variable": field,
                    "result_value": value,
                    "sample_time": latest["time"],
                },
            )
        )
    return commands, echoes


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def summarize(
    *,
    commands: list[dict[str, Any]],
    echoes: list[dict[str, Any]],
    probe_path: Path,
    samples_path: Path,
    commands_path: Path,
    echoes_path: Path,
) -> dict[str, Any]:
    accepted = sum(1 for row in echoes if row.get("status") == "accepted")
    rejected = sum(1 for row in echoes if row.get("status") == "rejected")
    forbidden_rejected = any(
        row.get("status") == "rejected"
        and row.get("reason") == "forbidden_pose_command"
        and row.get("command", {}).get("kind") == "teleport"
        for row in echoes
    )
    ok = (
        len(commands) == len(echoes) == 6
        and accepted == 5
        and rejected == 1
        and forbidden_rejected
        and all(row.get("source") == SOURCE for row in echoes)
        and all(row.get("ack_authority") == "MWORKS" for row in echoes)
        and all(row.get("no_pose_overwrite_status") == "pass" for row in echoes)
    )
    return {
        "schema_version": "mosim.mworks_mcp_echo_result_adapter_smoke.v1",
        "source": SOURCE,
        "evidence_level": EVIDENCE_LEVEL,
        "ok": ok,
        "input_probe_json": probe_path.as_posix(),
        "input_samples_csv": samples_path.as_posix(),
        "command_jsonl": commands_path.as_posix(),
        "echo_jsonl": echoes_path.as_posix(),
        "total_commands": len(commands),
        "total_echo_rows": len(echoes),
        "accepted": accepted,
        "rejected": rejected,
        "forbidden_pose_rejected": forbidden_rejected,
        "no_pose_overwrite_status": "pass" if all(row.get("no_pose_overwrite_status") == "pass" for row in echoes) else "invalid",
        "not_live_ue_runtime_ack": True,
        "not_live_mworks_downlink": True,
        "not_closed_loop": True,
        "not_controller_performance": True,
        "not_planner_ready": True,
        "not_factory_trace_consumption": True,
        "claim_boundary": [
            "This adapts existing task-002 MWORKS_MCP result-context evidence into schema-valid echo rows.",
            "This is not a live UE runtime ack or live MWORKS ack/downlink.",
            "This is not closed_loop, controller performance, planner_ready, FAST-LIO success, Factory trace consumption, plant tracking, or parameter identification.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-json", required=True, help="Task-002 probe JSON")
    parser.add_argument("--samples-csv", required=True, help="Task-002 samples CSV")
    parser.add_argument("--commands-output", required=True, help="Output mosim.ue_command.v1 JSONL")
    parser.add_argument("--echo-output", required=True, help="Output mosim.ue_command_echo.v1 JSONL")
    parser.add_argument("--summary-output", required=True, help="Output adapter summary JSON")
    args = parser.parse_args()

    probe_path = repo_path(args.probe_json)
    samples_path = repo_path(args.samples_csv)
    commands_path = repo_path(args.commands_output)
    echoes_path = repo_path(args.echo_output)
    summary_path = repo_path(args.summary_output)

    commands, echoes = build_rows(
        read_json(probe_path),
        read_samples(samples_path),
        probe_path=probe_path,
        samples_path=samples_path,
    )
    write_jsonl(commands_path, commands)
    write_jsonl(echoes_path, echoes)
    summary = summarize(
        commands=commands,
        echoes=echoes,
        probe_path=probe_path,
        samples_path=samples_path,
        commands_path=commands_path,
        echoes_path=echoes_path,
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
