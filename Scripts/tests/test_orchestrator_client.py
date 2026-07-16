from __future__ import annotations

import json
from pathlib import Path

from Scripts.ui import orchestrator_client


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
