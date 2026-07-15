#!/usr/bin/env python3
"""Offline reducer for the Factory wind and motor-effectiveness contract."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "Config" / "control_platform" / "factory_injection_contract.json"


@dataclass
class InjectionState:
    wind_speed_mps: float = 0.0
    wind_direction_deg: float = 0.0
    motor_effectiveness: list[float] = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def validate_command(command: dict[str, Any], contract: dict[str, Any]) -> str:
    missing = [field for field in contract["required_command_fields"] if field not in command]
    if missing:
        return f"missing_fields:{','.join(missing)}"
    target = str(command["target"])
    if target not in contract["targets"]:
        return "unsupported_target"
    if command["apply_mode"] not in contract["apply_modes"]:
        return "unsupported_apply_mode"
    if command["restore_policy"] not in contract["restore_policies"]:
        return "unsupported_restore_policy"
    try:
        value = float(command["value"])
        ramp_s = float(command["ramp_s"])
        duration_s = float(command["duration_s"])
    except (TypeError, ValueError):
        return "non_numeric_value_or_timing"
    bounds = contract["targets"][target]
    if command["apply_mode"] == "set" and not bounds["minimum"] <= value <= bounds["maximum"]:
        return "value_out_of_range"
    if ramp_s < 0.0 or duration_s < 0.0:
        return "negative_timing"
    if bounds.get("requires_rotor_index"):
        rotor_index = command.get("rotor_index")
        if not isinstance(rotor_index, int) or not bounds["rotor_index_min"] <= rotor_index <= bounds["rotor_index_max"]:
            return "invalid_rotor_index"
    return ""


def apply_command(state: InjectionState, command: dict[str, Any], contract: dict[str, Any]) -> list[dict[str, Any]]:
    reason = validate_command(command, contract)
    base = {
        "schema": "mosim.factory_injection_event.v1",
        "command_id": command.get("command_id", ""),
        "run_id": command.get("run_id", ""),
        "profile_hash": command.get("profile_hash", ""),
        "target": command.get("target", ""),
        "requested_at": command.get("requested_at", 0.0),
    }
    if reason:
        return [{**base, "event_state": "rejected", "reason": reason, "applied_value": None}]
    target = str(command["target"])
    restore = command["apply_mode"] == "restore"
    value = float(command["value"])
    if target == "wind_speed_mps":
        state.wind_speed_mps = 0.0 if restore else value
        applied = state.wind_speed_mps
    elif target == "wind_direction_deg":
        state.wind_direction_deg = 0.0 if restore else value
        applied = state.wind_direction_deg
    else:
        rotor = int(command["rotor_index"]) - 1
        state.motor_effectiveness[rotor] = 1.0 if restore else value
        applied = state.motor_effectiveness[rotor]
    terminal = "restored" if restore else "applied"
    return [
        {**base, "event_state": "accepted", "reason": "contract_valid", "applied_value": None},
        {**base, "event_state": terminal, "reason": "offline_reducer", "applied_value": applied},
    ]


def curve_row(state: InjectionState, command: dict[str, Any], event: dict[str, Any], columns: Iterable[str]) -> dict[str, Any]:
    row: dict[str, Any] = {column: "" for column in columns}
    row.update({
        "stamp_s": command.get("requested_at", 0.0),
        "command_id": command.get("command_id", ""),
        "event_state": event["event_state"],
        "requested_value": command.get("value", ""),
        "applied_value": event.get("applied_value", ""),
        "wind_speed_mps": state.wind_speed_mps,
        "wind_direction_deg": state.wind_direction_deg,
        "rotor_1_effectiveness": state.motor_effectiveness[0],
        "rotor_2_effectiveness": state.motor_effectiveness[1],
        "rotor_3_effectiveness": state.motor_effectiveness[2],
        "rotor_4_effectiveness": state.motor_effectiveness[3],
    })
    return row


def replay(commands: Iterable[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    contract = load_contract()
    output_dir.mkdir(parents=True, exist_ok=True)
    state = InjectionState()
    events: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    command_count = 0
    for command in commands:
        command_count += 1
        command_events = apply_command(state, command, contract)
        events.extend(command_events)
        rows.extend(curve_row(state, command, event, contract["curve_columns"]) for event in command_events)
    with (output_dir / "events.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for event in events:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    with (output_dir / "curves.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=contract["curve_columns"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "schema": "mosim.factory_injection_replay.v1",
        "status": "offline_contract_passed_runtime_not_accepted",
        "actual_factory_injection_accepted": False,
        "command_count": command_count,
        "event_count": len(events),
        "rejected_count": sum(event["event_state"] == "rejected" for event in events),
        "final_state": {
            "wind_speed_mps": state.wind_speed_mps,
            "wind_direction_deg": state.wind_direction_deg,
            "motor_effectiveness": state.motor_effectiveness,
        },
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "claim_ceiling": contract["runtime_boundary"],
    }
    with (output_dir / "G6_REPLAY_SUMMARY.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("commands_jsonl", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    commands = [json.loads(line) for line in args.commands_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = replay(commands, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
