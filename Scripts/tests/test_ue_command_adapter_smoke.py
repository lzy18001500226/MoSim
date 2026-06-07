from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / "Scripts" / "UE5" / "smoke_ue_command_adapter.py"
CHECK_ECHO = ROOT / "Scripts" / "UE5" / "check_ue_command_echo_contract.py"


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def command(seq: int, kind: str, *, require_ros2: bool = False, payload: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "schema": "mosim.ue_command.v1",
        "type": "command",
        "run_id": "run_1",
        "request_id": f"cmd_{seq}",
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


def test_ue_command_adapter_smoke_accepts_and_rejects_without_pose_override(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echo = tmp_path / "echo.jsonl"
    summary = tmp_path / "summary.json"
    write_jsonl(
        commands,
        [
            command(1, "controller_select", payload={"controller_id": "linear_mpc"}),
            command(2, "planner_select", require_ros2=True, payload={"planner_id": "ego"}),
            command(3, "scene_switch", require_ros2=True, payload={"scene_id": "factory"}),
            command(4, "motor_fault", payload={"rotor": 1, "efficiency": 0.7}),
            command(5, "teleport", payload={"x": 1.0}),
            {**command(6, "sensor_mode", require_ros2=False), "request_id": "cmd_missing_ros2_guard"},
        ],
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--commands",
            str(commands),
            "--echo-output",
            str(echo),
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
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["accepted"] == 4
    assert payload["rejected"] == 2
    assert payload["not_runtime_ue_console"] is True

    check = subprocess.run(
        [sys.executable, str(CHECK_ECHO), str(echo), "--require-runtime-ack"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr
    report = json.loads(check.stdout)
    assert report["runtime_ack_rows"] == 6
    rows = [json.loads(line) for line in echo.read_text(encoding="utf-8").splitlines()]
    reasons = {row["request_id"]: row["reason"] for row in rows}
    assert reasons["cmd_5"] == "forbidden_pose_command"
    assert reasons["cmd_missing_ros2_guard"] == "missing_ros2_ack_guard"


def test_ue_command_adapter_smoke_rejects_open_gate(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echo = tmp_path / "echo.jsonl"
    summary = tmp_path / "summary.json"
    write_jsonl(commands, [command(1, "controller_select")])
    completed = subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--commands",
            str(commands),
            "--echo-output",
            str(echo),
            "--summary-output",
            str(summary),
            "--open-gate",
            "p0_closed_loop_missing",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    rows = [json.loads(line) for line in echo.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["status"] == "rejected"
    assert rows[0]["reason"] == "gate_open:p0_closed_loop_missing"
