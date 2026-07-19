from __future__ import annotations

import json
from pathlib import Path

from Scripts.sunray.safe_stop_channel import SAFE_STOP_ACK_SCHEMA, SafeStopChannel


def test_safe_stop_channel_accepts_only_matching_run_request(tmp_path: Path) -> None:
    channel = SafeStopChannel("run-test")
    channel.root = tmp_path
    request_path = tmp_path / "request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema": "mosim.safe_stop.request.v1",
                "run_id": "wrong-run",
                "request_id": "request-1",
                "operation_id": "operation-1",
            }
        ),
        encoding="utf-8",
    )
    assert channel.requested() is False

    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload["run_id"] = "run-test"
    request_path.write_text(json.dumps(payload), encoding="utf-8")
    assert channel.requested() is True


def test_safe_stop_channel_ack_preserves_request_identity(tmp_path: Path) -> None:
    channel = SafeStopChannel("run-test")
    channel.root = tmp_path
    (tmp_path / "request.json").write_text(
        json.dumps(
            {
                "schema": "mosim.safe_stop.request.v1",
                "run_id": "run-test",
                "request_id": "request-1",
                "operation_id": "operation-1",
            }
        ),
        encoding="utf-8",
    )
    assert channel.requested() is True
    channel.acknowledge("completed", 150, terminal=True, accepted=True)

    ack = json.loads((tmp_path / "ack.json").read_text(encoding="utf-8"))
    assert ack["schema"] == SAFE_STOP_ACK_SCHEMA
    assert ack["run_id"] == "run-test"
    assert ack["request_id"] == "request-1"
    assert ack["operation_id"] == "operation-1"
    assert ack["stage"] == "completed"
    assert ack["progress_percent"] == 100
    assert ack["terminal"] is True
