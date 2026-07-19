from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.orchestration import MoSimOrchestrator
from src.orchestration.service import OrchestratorService, exclusive_service_lock


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


def test_service_preserves_nested_injection_command(tmp_path: Path) -> None:
    class RecordingOrchestrator:
        def __init__(self) -> None:
            self.received = None

        def apply_injection(self, **arguments):
            self.received = arguments
            return {"accepted": True, "reason_code": "recorded"}

        def _response(self, request_id, accepted, reason_code, **extra):
            return {"request_id": request_id, "accepted": accepted, "reason_code": reason_code, **extra}

    request = tmp_path / "inject.json"
    command = {"command_id": "inj-test", "target": "wind_speed_mps", "value": 2.0}
    request.write_text(
        json.dumps(
            {
                "action": "apply_injection",
                "request_id": "inject-1",
                "run_id": "run-test",
                "command": command,
            }
        ),
        encoding="utf-8",
    )
    orchestrator = RecordingOrchestrator()
    response = OrchestratorService(orchestrator, tmp_path, tmp_path / "responses").process_request(request)
    assert response["accepted"] is True
    assert orchestrator.received == {"request_id": "inject-1", "run_id": "run-test", "command": command}


def test_service_lock_rejects_a_second_process(tmp_path: Path) -> None:
    lock_path = tmp_path / "orchestrator.lock"
    probe = (
        "from pathlib import Path; "
        "from src.orchestration.service import exclusive_service_lock; "
        f"p=Path({str(lock_path)!r}); "
        "ctx=exclusive_service_lock(p); "
        "ctx.__enter__()"
    )
    with exclusive_service_lock(lock_path):
        result = subprocess.run(
            [sys.executable, "-c", probe], cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True
        )
    assert result.returncode != 0
    assert "orchestrator_service_already_running" in result.stderr
