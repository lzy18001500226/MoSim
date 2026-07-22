import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "smoke_mworks_echo_live_downlink_preflight.py"
CHECK_ECHO = ROOT / "Scripts" / "UE5" / "check_ue_command_echo_contract.py"
REDUCER = ROOT / "Scripts" / "UE5" / "smoke_ue_command_echo_state_reducer.py"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)


def fresh_preflight_payload() -> dict:
    return {
        "schema_version": "mosim.mworks_echo_live_downlink_preflight_input.v1",
        "source": "MWORKS_MCP",
        "model": "MoSimQuadrotorModel.Support.Models.EchoMcpStateSmoke",
        "run_id": "mworks_mcp_live_downlink_preflight_20260606_004",
        "check_model_ok": True,
        "simulate_model_ok": True,
        "result_times_count": 101,
        "result_time_first": 0.0,
        "result_time_last": 1.0,
        "sample_time_s": 1.0,
        "values": {
            "controller_select_status": 1.0,
            "wind_profile_status": 1.0,
            "motor_fault_status": 1.0,
            "scenario_reset_status": 1.0,
            "recording_status": 1.0,
            "forbidden_pose_status": -1.0,
            "no_pose_overwrite_status": 1.0,
            "accepted_mworks_owned_count": 5.0,
            "rejected_non_mworks_count": 2.0,
            "not_live_ue_runtime_ack": 1.0,
            "not_closed_loop": 1.0,
            "echo_state_keepalive": 0.007,
        },
    }


def test_live_downlink_preflight_builds_fresh_runtime_adapter_rows(tmp_path: Path) -> None:
    preflight = tmp_path / "preflight.json"
    commands = tmp_path / "commands.jsonl"
    echoes = tmp_path / "echoes.jsonl"
    summary = tmp_path / "summary.json"
    contract = tmp_path / "contract.json"
    states = tmp_path / "states.json"
    reducer_summary = tmp_path / "reducer.json"

    preflight.write_text(json.dumps(fresh_preflight_payload(), indent=2) + "\n", encoding="utf-8")
    run_command([
        sys.executable,
        str(SCRIPT),
        "--preflight-json",
        str(preflight),
        "--commands-output",
        str(commands),
        "--echo-output",
        str(echoes),
        "--summary-output",
        str(summary),
    ])
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["source"] == "MWORKS_MCP_runtime_adapter_preflight"
    assert payload["live_downlink_status"] == "blocked_no_transport_surface"
    assert payload["stronger_than_task_003_fixture"] is True
    assert payload["uses_task_003_fixture_rows"] is False
    assert payload["accepted"] == 5
    assert payload["rejected"] == 1
    assert payload["not_live_mworks_downlink"] is True

    rows = [json.loads(line) for line in echoes.read_text(encoding="utf-8").splitlines()]
    assert {row["source"] for row in rows} == {"MWORKS_MCP_runtime_adapter_preflight"}
    assert all(row["no_pose_overwrite_status"] == "pass" for row in rows)
    assert any(row["command"]["kind"] == "teleport" and row["reason"] == "forbidden_pose_command" for row in rows)

    run_command([
        sys.executable,
        str(CHECK_ECHO),
        str(echoes),
        "--require-runtime-ack",
        "--output-json",
        str(contract),
    ])
    contract_payload = json.loads(contract.read_text(encoding="utf-8"))
    assert contract_payload["ok"] is True
    assert contract_payload["runtime_ack_rows"] == 6

    run_command([
        sys.executable,
        str(REDUCER),
        "--commands",
        str(commands),
        "--echoes",
        str(echoes),
        "--state-output",
        str(states),
        "--summary-output",
        str(reducer_summary),
    ])
    reducer = json.loads(reducer_summary.read_text(encoding="utf-8"))
    assert reducer["ok"] is True
    assert reducer["accepted"] == 5
    assert reducer["rejected"] == 1
    reduced_states = json.loads(states.read_text(encoding="utf-8"))
    assert all(row["accepted_as_runtime_ack"] is False for row in reduced_states)


def test_live_downlink_preflight_rejects_non_mworks_mcp_source(tmp_path: Path) -> None:
    preflight = fresh_preflight_payload()
    preflight["source"] = "MWORKS_MCP_result_adapter_smoke"
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(preflight) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--preflight-json",
            str(preflight_path),
            "--commands-output",
            str(tmp_path / "commands.jsonl"),
            "--echo-output",
            str(tmp_path / "echoes.jsonl"),
            "--summary-output",
            str(tmp_path / "summary.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "preflight source must be MWORKS_MCP" in result.stderr
