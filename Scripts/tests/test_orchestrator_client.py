from __future__ import annotations

import json
from pathlib import Path

from Scripts.ui import orchestrator_client


def _args(**overrides):
    values = {
        "action": "list_controllers",
        "request_id": None,
        "profile_path": None,
        "prompt": None,
        "controller_id": None,
        "vehicle_count": None,
        "wind_speed_mps": 0.0,
        "run_id": None,
        "session_id": None,
        "operation_id": None,
        "connection_preflight_id": None,
        "target_host": "127.0.0.1",
        "rt1_udp_port": 49020,
        "ros_master_uri": "http://127.0.0.1:11311",
        "defer_ros_master": False,
        "local_advertised_ip": "auto",
        "requested_rate_hz": 200,
        "preflight_timeout_s": 0.35,
        "preflight_sample_count": 5,
        "target": None,
        "value": None,
        "rotor_index": None,
        "vehicle_id": None,
        "ramp_s": 0.0,
        "duration_s": 0.0,
        "display": [],
    }
    values.update(overrides)
    return type("Args", (), values)()


def test_client_builds_catalog_and_operation_requests_without_implicit_fields(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator_client, "ACTIVE_RUN", tmp_path / "active.json")
    assert orchestrator_client.build_payload(_args(request_id="catalog-fixed")) == {
        "schema": "mosim.orchestrator.request.v1",
        "action": "list_controllers",
        "request_id": "catalog-fixed",
    }
    operation = orchestrator_client.build_payload(
        _args(action="get_operation_progress", run_id="run-test", operation_id="op-test")
    )
    assert operation["run_id"] == "run-test"
    assert operation["operation_id"] == "op-test"


def test_client_builds_bounded_operator_task_proposal() -> None:
    payload = orchestrator_client.build_payload(
        _args(action="propose_operator_task", request_id="agent-fixed", prompt="运行三机编队避障")
    )
    assert payload == {
        "schema": "mosim.orchestrator.request.v1",
        "action": "propose_operator_task",
        "request_id": "agent-fixed",
        "prompt": "运行三机编队避障",
    }


def test_client_builds_staged_fault_apply_and_restore_requests() -> None:
    staged = orchestrator_client.build_payload(
        _args(
            action="stage_injection",
            run_id="run-test",
            target="motor_effectiveness",
            value=0.65,
            rotor_index=2,
            vehicle_id="uav1",
        )
    )
    assert staged["action"] == "stage_injection"
    assert staged["run_id"] == "run-test"
    assert staged["command"]["target"] == "motor_effectiveness"
    assert staged["command"]["value"] == 0.65
    assert staged["command"]["rotor_index"] == 2
    assert staged["command"]["vehicle_id"] == "uav1"

    applied = orchestrator_client.build_payload(_args(action="apply_staged_injection", run_id="run-test"))
    assert applied == {
        "schema": "mosim.orchestrator.request.v1",
        "action": "apply_staged_injection",
        "run_id": "run-test",
    }

    restored = orchestrator_client.build_payload(
        _args(action="restore_normal", run_id="run-test", vehicle_id="uav1")
    )
    assert restored == {
        "schema": "mosim.orchestrator.request.v1",
        "action": "restore_normal",
        "run_id": "run-test",
        "vehicle_id": "uav1",
    }


def test_connection_preflight_can_defer_ros_master_for_orchestrator_cold_start() -> None:
    payload = orchestrator_client.build_payload(
        _args(
            action="preflight_connection",
            profile_path="profile.json",
            controller_id="official_pid",
            vehicle_count=1,
            defer_ros_master=True,
        )
    )
    assert payload["ros_master_uri"] == ""


def test_preflight_payload_carries_endpoint_and_target_rate() -> None:
    payload = orchestrator_client.build_payload(
        _args(
            action="preflight_connection",
            request_id="preflight-fixed",
            profile_path="Config/profiles/experiments/mworks_live_official_pid_hover_50hz_v2.json",
            controller_id="official_pid",
            vehicle_count=1,
            target_host="192.168.10.20",
            ros_master_uri="http://192.168.10.20:11311",
            local_advertised_ip="192.168.10.5",
            requested_rate_hz=200,
            preflight_sample_count=7,
        )
    )

    assert payload["action"] == "preflight_connection"
    assert payload["target_host"] == "192.168.10.20"
    assert payload["requested_rate_hz"] == 200
    assert payload["sample_count"] == 7


def test_client_writes_request_and_reports_pending_without_service(tmp_path: Path, monkeypatch) -> None:
    request_dir = tmp_path / "requests"
    response_dir = tmp_path / "responses"
    monkeypatch.setattr(orchestrator_client, "REQUEST_DIR", request_dir)
    monkeypatch.setattr(orchestrator_client, "RESPONSE_DIR", response_dir)
    monkeypatch.setattr(orchestrator_client, "ACTIVE_RUN", tmp_path / "active.json")
    result = orchestrator_client.submit({"action": "get_run_state", "run_id": "run-test"}, timeout_s=0)
    assert result["reason_code"] == "orchestrator_response_pending"
    request = json.loads(next(request_dir.glob("*.json")).read_text(encoding="utf-8"))
    assert request["action"] == "get_run_state"


def test_client_records_accepted_active_run(tmp_path: Path, monkeypatch) -> None:
    request_dir = tmp_path / "requests"
    response_dir = tmp_path / "responses"
    active = tmp_path / "active.json"
    response_dir.mkdir()
    monkeypatch.setattr(orchestrator_client, "REQUEST_DIR", request_dir)
    monkeypatch.setattr(orchestrator_client, "RESPONSE_DIR", response_dir)
    monkeypatch.setattr(orchestrator_client, "ACTIVE_RUN", active)
    payload = {"request_id": "fixed", "action": "prepare_run"}
    (response_dir / "fixed.response.json").write_text(
        json.dumps({"accepted": True, "reason_code": "run_prepared", "run_id": "run-accepted", "profile_hash": "abc"}),
        encoding="utf-8",
    )
    result = orchestrator_client.submit(payload, timeout_s=0.2)
    assert result["accepted"] is True
    assert json.loads(active.read_text(encoding="utf-8"))["run_id"] == "run-accepted"
