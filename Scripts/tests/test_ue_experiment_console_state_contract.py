from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_experiment_console_state_contract.py"
HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"


def run_checker(tmp_path: Path) -> dict[str, object]:
    output = tmp_path / "console_state_contract.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), "--output-json", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(output.read_text(encoding="utf-8"))


def test_console_state_static_contract_passes(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["sender_remains_sender_only"] is True
    assert report["runtime_echo_receiver_implemented"] is False
    assert report["runtime_ack_required_before_acceptance"] is True
    assert report["pending_source"] == "mosim.ue_command.v1 request only"
    assert report["accepted_rejected_source"] == "matching mosim.ue_command_echo.v1 only"
    assert report["non_live_source_labels"] == [
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    ]
    assert all(report["non_live_source_coverage"].values())  # type: ignore[union-attr]
    assert report["non_live_quality_status"] == "smoke_only"
    assert report["non_live_accepted_as_runtime_ack"] is False
    assert report["planner_ready"] is False
    assert report["closed_loop_ready"] is False


def test_component_exposes_required_lifecycle_rows() -> None:
    header = HEADER.read_text(encoding="utf-8")
    for field in [
        "RunId",
        "RequestId",
        "Seq",
        "CommandKind",
        "UiState",
        "AckAuthority",
        "Reason",
        "Source",
        "QualityStatus",
        "bAcceptedAsRuntimeAck",
        "NoPoseOverwriteStatus",
    ]:
        assert field in header


def test_pending_and_echo_transition_rules_are_source_owned() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert "RecordPendingCommandFromPacketJson" in source
    assert "ApplyCommandEchoJson" in source
    assert "mosim.ue_command.v1" in source
    assert "mosim.ue_command_echo.v1" in source
    assert "awaiting_matching_echo" in source
    assert "no_matching_command_request" in source
    assert "missing_ack_authority" in source
    assert "no_pose_overwrite_not_pass" in source
    assert "seq_mismatch" in source
    assert "command_kind_mismatch" in source
    assert "smoke_only" in source
    assert "bAcceptedAsRuntimeAck = false" in source
    assert "MWORKS_MCP_result_adapter_smoke" in source
    assert "MWORKS_MCP_runtime_adapter_preflight" in source


def test_known_non_live_sources_are_downgraded_not_runtime_ack() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    smoke_source_start = source.index("bool IsSmokeSource")
    smoke_source_end = source.index("}\n}", smoke_source_start)
    smoke_source_body = source[smoke_source_start:smoke_source_end]
    for label in [
        "offline_adapter_smoke",
        "source_level_smoke",
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
    ]:
        assert f'TEXT("{label}")' in smoke_source_body
    assert 'TEXT("smoke_only")' in source
    assert "State->bAcceptedAsRuntimeAck = !IsSmokeSource(EchoSource);" in source


def test_component_does_not_expose_pose_or_runtime_receiver_paths() -> None:
    combined = HEADER.read_text(encoding="utf-8") + SOURCE.read_text(encoding="utf-8")
    for forbidden in [
        "SetActorLocation",
        "SetActorTransform",
        "TeleportTo",
        "AddActorWorldOffset",
        "BindAxis",
        "BindAction",
        "InputComponent",
        "EnhancedInput",
        "UInputAction",
        "RecvFrom(",
        "FUdpSocketReceiver",
    ]:
        assert forbidden not in combined
