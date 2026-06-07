from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Scripts" / "mworks" / "smoke_mworks_mcp_echo_result_adapter.py"
CHECK_ECHO = ROOT / "Scripts" / "UE5" / "check_ue_command_echo_contract.py"
REDUCER = ROOT / "Scripts" / "UE5" / "smoke_ue_command_echo_state_reducer.py"
PROBE = ROOT / "Results" / "mworks_echo_producer_smoke" / "20260606_002_mcp_state" / "echo_mcp_state_probe.json"
SAMPLES = ROOT / "Results" / "mworks_echo_producer_smoke" / "20260606_002_mcp_state" / "echo_mcp_state_samples.csv"


def run_adapter(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, object]]:
    commands = tmp_path / "commands.jsonl"
    echoes = tmp_path / "echoes.jsonl"
    summary = tmp_path / "summary.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(ADAPTER),
            "--probe-json",
            str(PROBE),
            "--samples-csv",
            str(SAMPLES),
            "--commands-output",
            str(commands),
            "--echo-output",
            str(echoes),
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
    return commands, echoes, summary, payload


def test_adapter_generates_non_live_mworks_mcp_echo_rows(tmp_path: Path) -> None:
    _commands, echoes, _summary, payload = run_adapter(tmp_path)
    assert payload["ok"] is True
    assert payload["source"] == "MWORKS_MCP_result_adapter_smoke"
    assert payload["accepted"] == 5
    assert payload["rejected"] == 1
    assert payload["forbidden_pose_rejected"] is True
    assert payload["not_live_ue_runtime_ack"] is True
    assert payload["not_live_mworks_downlink"] is True
    rows = [json.loads(line) for line in echoes.read_text(encoding="utf-8").splitlines()]
    assert {row["source"] for row in rows} == {"MWORKS_MCP_result_adapter_smoke"}
    assert {row["ack_authority"] for row in rows} == {"MWORKS"}
    assert {row["no_pose_overwrite_status"] for row in rows} == {"pass"}
    by_kind = {row["command"]["kind"]: row for row in rows}
    assert by_kind["teleport"]["status"] == "rejected"
    assert by_kind["teleport"]["reason"] == "forbidden_pose_command"


def test_adapter_rows_pass_contract_checker_and_reducer_as_smoke_only(tmp_path: Path) -> None:
    commands, echoes, _summary, _payload = run_adapter(tmp_path)
    contract_report = tmp_path / "contract_report.json"
    contract = subprocess.run(
        [
            sys.executable,
            str(CHECK_ECHO),
            str(echoes),
            "--require-runtime-ack",
            "--output-json",
            str(contract_report),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert contract.returncode == 0, contract.stdout + contract.stderr
    contract_payload = json.loads(contract_report.read_text(encoding="utf-8"))
    assert contract_payload["ok"] is True
    assert contract_payload["runtime_ack_rows"] == 6

    state_output = tmp_path / "states.json"
    reducer_summary = tmp_path / "reducer_summary.json"
    reducer = subprocess.run(
        [
            sys.executable,
            str(REDUCER),
            "--commands",
            str(commands),
            "--echoes",
            str(echoes),
            "--state-output",
            str(state_output),
            "--summary-output",
            str(reducer_summary),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert reducer.returncode == 0, reducer.stdout + reducer.stderr
    summary_payload = json.loads(reducer_summary.read_text(encoding="utf-8"))
    assert summary_payload["accepted"] == 5
    assert summary_payload["rejected"] == 1
    assert summary_payload["not_live_ue_runtime_ack"] is True
    states = json.loads(state_output.read_text(encoding="utf-8"))
    assert {row["quality_status"] for row in states} == {"smoke_only"}
    assert {row["accepted_as_runtime_ack"] for row in states} == {False}
