from __future__ import annotations

import json
from pathlib import Path

from Scripts.sunray.mission_status_channel import MissionStatusChannel
from Scripts.ui.runtime_sidecar import load_mission_status


def test_channel_publishes_phase_vehicle_and_terminal_ack(tmp_path: Path) -> None:
    output = tmp_path / "mission_status.json"
    channel = MissionStatusChannel(
        "goal5_swarm_formation_mission",
        ["uav1", "uav2", "uav3"],
        run_id="run-test",
        output_path=output,
        minimum_write_interval_s=0.0,
    )
    channel.update_phase("takeoff")
    channel.update_vehicle("uav2", connected=True, armed=True, mode="OFFBOARD")
    channel.finish(result_status="passed", accepted=True)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == "mosim.mission_status.v1"
    assert payload["run_id"] == "run-test"
    assert payload["adapter_id"] == "goal5_swarm_formation_mission"
    assert payload["phase"] == "takeoff"
    assert payload["terminal"] is True
    assert payload["accepted"] is True
    assert payload["vehicles"][1]["vehicle_id"] == "uav2"
    assert payload["vehicles"][1]["connected"] is True
    assert payload["vehicles"][1]["armed"] is True
    assert payload["vehicles"][1]["mode"] == "OFFBOARD"


def test_channel_write_failure_does_not_interrupt_mission(tmp_path: Path) -> None:
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("file", encoding="utf-8")
    channel = MissionStatusChannel(
        "adapter",
        ["uav1"],
        run_id="run-test",
        output_path=blocked_parent / "mission_status.json",
    )
    channel.update_phase("takeoff")
    assert channel.last_error


def _status_payload(*, run_id: str, updated_at: float, terminal: bool = False) -> dict:
    return {
        "schema": "mosim.mission_status.v1",
        "run_id": run_id,
        "adapter_id": "px4ctrl_basic_mission",
        "phase": "done" if terminal else "takeoff",
        "state": "passed" if terminal else "running",
        "terminal": terminal,
        "accepted": True if terminal else None,
        "reason_code": "mission_result_passed" if terminal else "mission_phase_takeoff",
        "blockers": [],
        "vehicles": [{
            "vehicle_id": "uav1",
            "connected": True,
            "armed": not terminal,
            "mode": "OFFBOARD",
            "updated_at": updated_at,
        }],
        "updated_at": updated_at,
    }


def test_sidecar_accepts_only_current_fresh_run(tmp_path: Path) -> None:
    path = tmp_path / "mission_status.json"
    path.write_text(json.dumps(_status_payload(run_id="run-test", updated_at=100.0)), encoding="utf-8")

    fresh = load_mission_status(
        path, expected_run_id="run-test", expected_vehicle_ids=["uav1"], now=101.0, max_age_s=2.5
    )
    assert fresh["transport_state"] == "fresh"
    assert fresh["fresh"] is True

    stale = load_mission_status(
        path, expected_run_id="run-test", expected_vehicle_ids=["uav1"], now=104.0, max_age_s=2.5
    )
    assert stale["transport_state"] == "stale"
    assert stale["fresh"] is False

    wrong_run = load_mission_status(
        path, expected_run_id="run-other", expected_vehicle_ids=["uav1"], now=101.0, max_age_s=2.5
    )
    assert wrong_run["transport_state"] == "unavailable"
    assert wrong_run["reason_code"] == "mission_status_contract_invalid"


def test_sidecar_retains_valid_terminal_ack_after_source_stops(tmp_path: Path) -> None:
    path = tmp_path / "mission_status.json"
    path.write_text(
        json.dumps(_status_payload(run_id="run-test", updated_at=100.0, terminal=True)), encoding="utf-8"
    )
    terminal = load_mission_status(
        path, expected_run_id="run-test", expected_vehicle_ids=["uav1"], now=300.0, max_age_s=2.5
    )
    assert terminal["transport_state"] == "terminal"
    assert terminal["fresh"] is False
    assert terminal["accepted"] is True
