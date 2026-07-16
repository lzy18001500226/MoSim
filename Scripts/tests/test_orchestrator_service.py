from __future__ import annotations

import json
from pathlib import Path

from src.orchestration import MoSimOrchestrator
from src.orchestration.service import OrchestratorService


PROFILE = "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json"


def test_service_preserves_orchestrator_state_across_requests(tmp_path: Path) -> None:
    requests = tmp_path / "requests"
    responses = tmp_path / "responses"
    requests.mkdir()
    service = OrchestratorService(MoSimOrchestrator(run_root=tmp_path / "runs"), requests, responses)
    (requests / "001.json").write_text(
        json.dumps(
            {
                "schema": "mosim.orchestrator.request.v1",
                "request_id": "prepare-1",
                "action": "prepare_run",
                "profile_path": PROFILE,
                "controller_id": "px4ctrl",
                "vehicle_count": 1,
            }
        ),
        encoding="utf-8",
    )
    assert service.process_once() == 1
    prepared = json.loads((responses / "001.response.json").read_text(encoding="utf-8"))
    assert prepared["accepted"] is True

    (requests / "002.json").write_text(
        json.dumps(
            {
                "request_id": "state-1",
                "action": "get_run_state",
                "run_id": prepared["run_id"],
            }
        ),
        encoding="utf-8",
    )
    assert service.process_once() == 1
    state = json.loads((responses / "002.response.json").read_text(encoding="utf-8"))
    assert state["manifest"]["run_id"] == prepared["run_id"]
    assert service.process_once() == 0


def test_service_rejects_unsupported_and_malformed_requests(tmp_path: Path) -> None:
    requests = tmp_path / "requests"
    responses = tmp_path / "responses"
    requests.mkdir()
    service = OrchestratorService(MoSimOrchestrator(run_root=tmp_path / "runs"), requests, responses)
    (requests / "bad.json").write_text("[]", encoding="utf-8")
    (requests / "unsupported.json").write_text(json.dumps({"action": "_save"}), encoding="utf-8")
    assert service.process_once() == 2
    bad = json.loads((responses / "bad.response.json").read_text(encoding="utf-8"))
    unsupported = json.loads((responses / "unsupported.response.json").read_text(encoding="utf-8"))
    assert bad["reason_code"] == "request_must_be_object"
    assert unsupported["reason_code"] == "unsupported_action"
