from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_command_echo_contract.py"


def run_checker(path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path), *extra],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_placeholder_is_smoke_only_not_runtime_ack(tmp_path: Path) -> None:
    echo = tmp_path / "ue_command_echo.jsonl"
    write_jsonl(
        echo,
        [
            {
                "schema": "mosim.ue_command_echo.placeholder.v1",
                "status": "not_runtime_ue_console",
                "no_pose_overwrite_status": "pass",
            }
        ],
    )

    completed = run_checker(echo)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["placeholder_rows"] == 1
    assert report["runtime_ack_rows"] == 0
    assert any("smoke-only" in item for item in report["warnings"])

    runtime_required = run_checker(echo, "--require-runtime-ack")
    assert runtime_required.returncode == 1
    assert "requires at least one" in runtime_required.stdout


def test_runtime_ack_requires_mworks_or_ros2_authority(tmp_path: Path) -> None:
    echo = tmp_path / "ue_command_echo.jsonl"
    write_jsonl(
        echo,
        [
            {
                "schema": "mosim.ue_command_echo.v1",
                "status": "accepted",
                "run_id": "run_1",
                "request_id": "cmd_1",
                "ack_authority": "MWORKS_ROS2",
                "no_pose_overwrite_status": "pass",
                "command": {"kind": "controller_select", "payload": {"controller_id": "linear_mpc"}},
            },
            {
                "schema": "mosim.ue_command_echo.v1",
                "status": "rejected",
                "run_id": "run_1",
                "request_id": "cmd_2",
                "ack_authority": "ROS2",
                "no_pose_overwrite_status": "pass",
                "command_kind": "planner_select",
            },
        ],
    )

    completed = run_checker(echo, "--require-runtime-ack")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["runtime_ack_rows"] == 2
    assert report["placeholder_rows"] == 0


def test_pose_override_commands_are_rejected(tmp_path: Path) -> None:
    echo = tmp_path / "ue_command_echo.jsonl"
    write_jsonl(
        echo,
        [
            {
                "schema": "mosim.ue_command_echo.v1",
                "status": "accepted",
                "run_id": "run_1",
                "request_id": "cmd_bad",
                "ack_authority": "MWORKS",
                "no_pose_overwrite_status": "pass",
                "command": {"kind": "teleport", "payload": {"x": 1.0}},
                "pose_override": True,
            }
        ],
    )

    completed = run_checker(echo)
    assert completed.returncode == 1
    assert "forbidden UE command kind" in completed.stdout
    assert "pose_override/teleport=true" in completed.stdout


def test_rejected_forbidden_pose_command_is_valid_rejection_evidence(tmp_path: Path) -> None:
    echo = tmp_path / "ue_command_echo.jsonl"
    write_jsonl(
        echo,
        [
            {
                "schema": "mosim.ue_command_echo.v1",
                "status": "rejected",
                "reason": "forbidden_pose_command",
                "run_id": "run_1",
                "request_id": "cmd_rejected",
                "ack_authority": "MWORKS",
                "no_pose_overwrite_status": "pass",
                "command": {"kind": "teleport", "payload": {"x": 1.0}},
            }
        ],
    )

    completed = run_checker(echo, "--require-runtime-ack")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["runtime_ack_rows"] == 1
