from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REDUCER = ROOT / "Scripts" / "UE5" / "smoke_ue_command_echo_state_reducer.py"


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def command(seq: int, request_id: str, kind: str) -> dict[str, object]:
    return {
        "schema": "mosim.ue_command.v1",
        "type": "command",
        "run_id": "run_echo_state",
        "request_id": request_id,
        "seq": seq,
        "time_s": seq * 0.05,
        "requested_by": "ue_experiment_console",
        "command": {"kind": kind, "payload": {}},
        "guard": {
            "require_mworks_ack": True,
            "require_ros2_ack": kind in {"planner_select", "scene_switch", "sensor_mode", "start_goal_update"},
            "reject_if_gate_open": [],
        },
    }


def echo(seq: int, request_id: str, kind: str, status: str, *, source: str = "offline_adapter_smoke") -> dict[str, object]:
    return {
        "schema": "mosim.ue_command_echo.v1",
        "source": source,
        "status": status,
        "reason": "ok" if status == "accepted" else "runtime_gate_rejected",
        "run_id": "run_echo_state",
        "request_id": request_id,
        "seq": seq,
        "time_s": seq * 0.05,
        "ack_authority": "MWORKS_ROS2" if kind in {"planner_select", "scene_switch"} else "MWORKS",
        "no_pose_overwrite_status": "pass",
        "command": {"kind": kind, "payload": {}},
    }


def run_reducer(commands: Path, echoes: Path, tmp_path: Path) -> tuple[subprocess.CompletedProcess[str], list[dict[str, object]], dict[str, object]]:
    states = tmp_path / "states.json"
    summary = tmp_path / "summary.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(REDUCER),
            "--commands",
            str(commands),
            "--echoes",
            str(echoes),
            "--state-output",
            str(states),
            "--summary-output",
            str(summary),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    state_rows = json.loads(states.read_text(encoding="utf-8")) if states.exists() else []
    summary_payload = json.loads(summary.read_text(encoding="utf-8")) if summary.exists() else {}
    return completed, state_rows, summary_payload


def test_commands_start_pending_and_matching_echoes_update_state(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echoes = tmp_path / "echoes.jsonl"
    write_jsonl(
        commands,
        [
            command(1, "cmd_pending", "controller_select"),
            command(2, "cmd_accepted", "controller_select"),
            command(3, "cmd_rejected", "planner_select"),
        ],
    )
    write_jsonl(
        echoes,
        [
            echo(2, "cmd_accepted", "controller_select", "accepted"),
            echo(3, "cmd_rejected", "planner_select", "rejected"),
        ],
    )

    completed, states, summary = run_reducer(commands, echoes, tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    by_id = {row["request_id"]: row for row in states}
    assert by_id["cmd_pending"]["ui_state"] == "pending"
    assert by_id["cmd_pending"]["state_source"] == "ue_command_request"
    assert by_id["cmd_accepted"]["ui_state"] == "accepted"
    assert by_id["cmd_rejected"]["ui_state"] == "rejected"
    assert summary["pending"] == 1
    assert summary["accepted"] == 1
    assert summary["rejected"] == 1
    assert summary["planner_ready"] is False
    assert summary["closed_loop_ready"] is False


def test_orphan_echo_does_not_create_ui_state(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echoes = tmp_path / "echoes.jsonl"
    write_jsonl(commands, [command(1, "cmd_real", "controller_select")])
    write_jsonl(echoes, [echo(2, "cmd_orphan", "controller_select", "accepted")])

    completed, states, summary = run_reducer(commands, echoes, tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert states[0]["request_id"] == "cmd_real"
    assert states[0]["ui_state"] == "pending"
    assert summary["orphan_echoes"][0]["request_id"] == "cmd_orphan"


def test_seq_or_kind_mismatch_does_not_update_state(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echoes = tmp_path / "echoes.jsonl"
    write_jsonl(commands, [command(1, "cmd_mismatch", "controller_select")])
    write_jsonl(echoes, [echo(9, "cmd_mismatch", "planner_select", "accepted")])

    completed, states, summary = run_reducer(commands, echoes, tmp_path)
    assert completed.returncode == 1
    assert states[0]["ui_state"] == "pending"
    assert summary["ok"] is False
    reasons = {row["reason"] for row in summary["invalid_echoes"]}
    assert "seq_mismatch" in reasons or "command_kind_mismatch" in reasons


def test_offline_echo_updates_fixture_state_but_not_runtime_ack(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echoes = tmp_path / "echoes.jsonl"
    write_jsonl(commands, [command(1, "cmd_smoke", "controller_select")])
    write_jsonl(echoes, [echo(1, "cmd_smoke", "controller_select", "accepted", source="offline_adapter_smoke")])

    completed, states, summary = run_reducer(commands, echoes, tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert states[0]["ui_state"] == "accepted"
    assert states[0]["quality_status"] == "smoke_only"
    assert states[0]["accepted_as_runtime_ack"] is False
    assert states[0]["not_live_ue_runtime_ack"] is True
    assert summary["not_live_ue_runtime_ack"] is True
