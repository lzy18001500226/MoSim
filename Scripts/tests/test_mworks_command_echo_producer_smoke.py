from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / "Scripts" / "mworks" / "smoke_mworks_command_echo_producer.py"
CHECK_ECHO = ROOT / "Scripts" / "UE5" / "check_ue_command_echo_contract.py"


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def command(
    seq: int,
    kind: str,
    *,
    payload: dict[str, object] | None = None,
    require_ros2: bool = False,
) -> dict[str, object]:
    return {
        "schema": "mosim.ue_command.v1",
        "type": "command",
        "run_id": "mworks_echo_smoke_run",
        "request_id": f"mworks_cmd_{seq}",
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


def run_smoke(commands: Path, echo: Path, summary: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SMOKE),
            "--commands",
            str(commands),
            "--echo-output",
            str(echo),
            "--summary-output",
            str(summary),
            *extra,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_mworks_echo_producer_accepts_only_mworks_owned_commands(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echo = tmp_path / "mworks_echo.jsonl"
    summary = tmp_path / "summary.json"
    write_jsonl(
        commands,
        [
            command(1, "controller_select", payload={"controller_id": "awff"}),
            command(2, "wind_profile", payload={"wind_profile_id": "factory_gust_x"}),
            command(3, "motor_fault", payload={"fault_id": "rotor1_loss15", "rotor": 1, "efficiency": 0.85}),
            command(4, "scenario_reset", payload={"scenario_id": "factory_trace_smoke"}),
            command(5, "recording", payload={"recording_state": "start"}),
            command(6, "planner_select", require_ros2=True, payload={"planner_id": "ego"}),
            command(7, "sensor_mode", require_ros2=True, payload={"sensor_mode": "fastlio"}),
            command(8, "scene_switch", require_ros2=True, payload={"scene_id": "factory"}),
            command(9, "start_goal_update", require_ros2=True, payload={"goal": [1.0, 2.0, 1.0]}),
            command(10, "teleport", payload={"x": 1.0}),
        ],
    )

    completed = run_smoke(commands, echo, summary)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["accepted"] == 5
    assert payload["rejected"] == 5
    assert payload["ros2_or_shared_commands_rejected"] == 4
    assert payload["not_runtime_mworks_ack"] is True
    assert payload["not_live_ue_console"] is True
    assert payload["not_closed_loop"] is True
    assert payload["not_controller_performance"] is True
    assert payload["not_planner_ready"] is True

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
    rows = [json.loads(line) for line in echo.read_text(encoding="utf-8").splitlines()]
    assert {row["ack_authority"] for row in rows} == {"MWORKS"}
    reasons = {row["request_id"]: row["reason"] for row in rows}
    assert reasons["mworks_cmd_6"] == "requires_ros2_or_mworks_ros2_authority"
    assert reasons["mworks_cmd_10"] == "forbidden_pose_command"


def test_mworks_echo_producer_rejects_open_gate(tmp_path: Path) -> None:
    commands = tmp_path / "commands.jsonl"
    echo = tmp_path / "mworks_echo.jsonl"
    summary = tmp_path / "summary.json"
    write_jsonl(commands, [command(1, "controller_select", payload={"controller_id": "awff"})])
    completed = run_smoke(
        commands,
        echo,
        summary,
        "--open-gate",
        "p0_closed_loop_missing",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    rows = [json.loads(line) for line in echo.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["status"] == "rejected"
    assert rows[0]["reason"] == "gate_open:p0_closed_loop_missing"
