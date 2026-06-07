from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_live_echo_receiver_boundary.py"
STATE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp"


def run_checker(tmp_path: Path) -> dict[str, object]:
    output = tmp_path / "boundary.json"
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


def test_boundary_checker_passes_source_label_patch_but_keeps_runtime_blocker(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["blockers"] == []
    assert report["source_labels"]["non_live_sources_missing_from_state_component"] == []  # type: ignore[index]
    assert report["source_labels"]["non_live_sources_covered_by_state_component"] == [  # type: ignore[index]
        "MWORKS_MCP_result_adapter_smoke",
        "MWORKS_MCP_runtime_adapter_preflight",
        "offline_adapter_smoke",
        "source_level_smoke",
    ]
    assert report["source_labels"]["non_live_source_quality_status"] == "smoke_only"  # type: ignore[index]
    assert report["source_labels"]["non_live_accepted_as_runtime_ack"] is False  # type: ignore[index]
    assert report["receiver_boundary_decision"]["current_live_echo_receiver_present"] is False  # type: ignore[index]
    assert report["receiver_boundary_decision"]["safe_to_implement_runtime_receiver_next"] is False  # type: ignore[index]
    assert report["claim_boundary"]["not_live_ue_runtime_ack"] is True  # type: ignore[index]
    assert report["claim_boundary"]["planner_ready"] is False  # type: ignore[index]
    assert report["claim_boundary"]["closed_loop_ready"] is False  # type: ignore[index]


def test_existing_udp_receiver_is_frame_only_not_command_echo_receiver() -> None:
    source = FRAME_RECEIVER_SOURCE.read_text(encoding="utf-8")
    assert "quadrotor.unreal_state." in source
    assert "mosim.ue_command_echo.v1" not in source
    assert "ApplyCommandEchoJson" not in source


def test_current_state_component_downgrades_known_preflight_labels() -> None:
    source = STATE_SOURCE.read_text(encoding="utf-8")
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
