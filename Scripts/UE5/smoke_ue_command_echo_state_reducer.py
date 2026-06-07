#!/usr/bin/env python3
"""Reduce UE command requests plus echo rows into pending/accepted/rejected UI state.

This is an offline fixture smoke. It does not open UE, send UDP, run MWORKS,
publish ROS2 topics, or prove live runtime acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
ALLOWED_ECHO_STATUS = {"accepted", "rejected"}
SMOKE_SOURCES = {
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
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
                raise ValueError(f"{path}:{line_number}: JSONL row must be an object")
            payload["_line_number"] = line_number
            rows.append(payload)
    return rows


def command_kind(row: dict[str, Any]) -> str:
    command = row.get("command")
    if isinstance(command, dict):
        return str(command.get("kind") or "")
    return str(row.get("command_kind") or row.get("kind") or "")


def command_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("run_id") or ""), str(row.get("request_id") or "")


def command_seq(row: dict[str, Any]) -> int | None:
    value = row.get("seq")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def initial_state(command: dict[str, Any]) -> dict[str, Any]:
    run_id, request_id = command_key(command)
    return {
        "run_id": run_id,
        "request_id": request_id,
        "seq": command_seq(command),
        "command_kind": command_kind(command),
        "ui_state": "pending",
        "state_source": "ue_command_request",
        "ack_authority": "",
        "reason": "awaiting_matching_echo",
        "quality_status": "pending_no_runtime_echo",
        "accepted_as_runtime_ack": False,
        "not_live_ue_runtime_ack": True,
        "no_pose_overwrite_status": "pass",
        "echo_source": "",
    }


def validate_command(row: dict[str, Any]) -> str:
    if str(row.get("schema") or "") != COMMAND_SCHEMA:
        return "unsupported_command_schema"
    if str(row.get("type") or "") != "command":
        return "unsupported_command_type"
    if not command_key(row)[0] or not command_key(row)[1]:
        return "missing_run_id_or_request_id"
    if not isinstance(row.get("command"), dict):
        return "missing_command"
    return ""


def validate_echo(row: dict[str, Any]) -> str:
    if str(row.get("schema") or "") != ECHO_SCHEMA:
        return "unsupported_echo_schema"
    if str(row.get("status") or "") not in ALLOWED_ECHO_STATUS:
        return "unsupported_echo_status"
    if not command_key(row)[0] or not command_key(row)[1]:
        return "missing_run_id_or_request_id"
    if str(row.get("no_pose_overwrite_status") or "") != "pass":
        return "no_pose_overwrite_not_pass"
    if not str(row.get("ack_authority") or ""):
        return "missing_ack_authority"
    return ""


def matching_issue(command: dict[str, Any], echo: dict[str, Any]) -> str:
    command_seq_value = command_seq(command)
    echo_seq_value = command_seq(echo)
    if command_seq_value is not None and echo_seq_value is not None and command_seq_value != echo_seq_value:
        return "seq_mismatch"
    echo_kind = command_kind(echo)
    if echo_kind and echo_kind != command_kind(command):
        return "command_kind_mismatch"
    return ""


def reduce_state(commands: list[dict[str, Any]], echoes: list[dict[str, Any]]) -> dict[str, Any]:
    states: dict[tuple[str, str], dict[str, Any]] = {}
    issues: list[str] = []
    orphan_echoes: list[dict[str, Any]] = []
    invalid_echoes: list[dict[str, Any]] = []
    duplicate_commands: list[dict[str, Any]] = []

    for command in commands:
        issue = validate_command(command)
        if issue:
            issues.append(f"command line {command.get('_line_number', 0)}: {issue}")
            continue
        key = command_key(command)
        if key in states:
            duplicate_commands.append({"run_id": key[0], "request_id": key[1], "reason": "duplicate_command_request"})
            continue
        states[key] = initial_state(command)

    for echo in echoes:
        issue = validate_echo(echo)
        if issue:
            invalid_echoes.append(
                {
                    "run_id": str(echo.get("run_id") or ""),
                    "request_id": str(echo.get("request_id") or ""),
                    "reason": issue,
                }
            )
            continue
        key = command_key(echo)
        state = states.get(key)
        if state is None:
            orphan_echoes.append(
                {
                    "run_id": key[0],
                    "request_id": key[1],
                    "status": str(echo.get("status") or ""),
                    "reason": "no_matching_command_request",
                }
            )
            continue
        command_stub = {
            "seq": state["seq"],
            "command": {"kind": state["command_kind"]},
        }
        issue = matching_issue(command_stub, echo)
        if issue:
            invalid_echoes.append({"run_id": key[0], "request_id": key[1], "reason": issue})
            continue

        source = str(echo.get("source") or "")
        smoke_only = source in SMOKE_SOURCES or source == ""
        state.update(
            {
                "ui_state": str(echo.get("status") or ""),
                "state_source": "mosim.ue_command_echo.v1",
                "ack_authority": str(echo.get("ack_authority") or ""),
                "reason": str(echo.get("reason") or ""),
                "quality_status": "smoke_only" if smoke_only else "runtime_echo_fixture",
                "accepted_as_runtime_ack": not smoke_only,
                "not_live_ue_runtime_ack": True,
                "no_pose_overwrite_status": str(echo.get("no_pose_overwrite_status") or ""),
                "echo_source": source or "unspecified_smoke_fixture",
            }
        )

    state_rows = list(states.values())
    summary = {
        "schema": "mosim.ue_command_echo_state_reducer_smoke.v1",
        "source": "offline_reducer_smoke",
        "ok": not issues and not invalid_echoes,
        "total_commands": len(commands),
        "tracked_commands": len(state_rows),
        "pending": sum(1 for row in state_rows if row["ui_state"] == "pending"),
        "accepted": sum(1 for row in state_rows if row["ui_state"] == "accepted"),
        "rejected": sum(1 for row in state_rows if row["ui_state"] == "rejected"),
        "orphan_echoes": orphan_echoes,
        "invalid_echoes": invalid_echoes,
        "duplicate_commands": duplicate_commands,
        "issues": issues,
        "not_live_ue_runtime_ack": True,
        "planner_ready": False,
        "closed_loop_ready": False,
        "claim_boundary": [
            "Pending state originates only from UE command requests.",
            "Accepted/rejected UI state originates only from matching mosim.ue_command_echo.v1 rows.",
            "Offline reducer smoke does not prove live UE, MWORKS, ROS2, planner, or closed-loop runtime acknowledgement.",
        ],
    }
    return {"summary": summary, "states": state_rows}


def write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commands", required=True, help="Input mosim.ue_command.v1 JSONL")
    parser.add_argument("--echoes", required=True, help="Input mosim.ue_command_echo.v1 JSONL")
    parser.add_argument("--state-output", required=True, help="Output reduced UI state JSON")
    parser.add_argument("--summary-output", required=True, help="Output summary JSON")
    args = parser.parse_args()

    commands_path = repo_path(args.commands)
    echoes_path = repo_path(args.echoes)
    state_path = repo_path(args.state_output)
    summary_path = repo_path(args.summary_output)

    reduced = reduce_state(read_jsonl(commands_path), read_jsonl(echoes_path))
    write_json(state_path, reduced["states"])
    write_json(summary_path, reduced["summary"])
    print(json.dumps(reduced["summary"], ensure_ascii=False, indent=2))
    return 0 if reduced["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
