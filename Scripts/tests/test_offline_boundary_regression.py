from __future__ import annotations

import json
from pathlib import Path

from Scripts.quality import check_offline_boundary_regression as checker


def accepted_record(root: Path, variant: str) -> None:
    run_dir = root / "run"
    run_dir.mkdir(parents=True)
    for name in ("result.csv", "metrics.json", "mcp.jsonl", "Result.msr"):
        (run_dir / name).write_text("ok\n", encoding="utf-8")
    record = {
        "run_id": "run-1",
        "output_variant": variant,
        "status": "accepted",
        "acceptance": {key: True for key in checker.REQUIRED_ACCEPTANCE},
        "session_cleanup": {"shutdown_recorded": True},
        "artifacts": {
            "raw_csv": "run/result.csv",
            "metrics_json": "run/metrics.json",
            "mcp_log": "run/mcp.jsonl",
            "native_result": "run/Result.msr",
        },
    }
    (root / "record.json").write_text(
        json.dumps(record), encoding="utf-8"
    )


def test_audit_record_accepts_complete_evidence(tmp_path: Path) -> None:
    accepted_record(tmp_path, "WRENCH")
    result = checker.audit_record(
        tmp_path,
        {"output_variant": "WRENCH", "record": "record.json", "evidence_kind": "test"},
    )
    assert result["status"] == "accepted"
    assert result["reasons"] == []


def test_audit_record_accepts_current_worktree_status(tmp_path: Path) -> None:
    accepted_record(tmp_path, "BODY_RATE_THRUST")
    record_path = tmp_path / "record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["status"] = "accepted_current_worktree"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    result = checker.audit_record(
        tmp_path,
        {"output_variant": "BODY_RATE_THRUST", "record": "record.json", "evidence_kind": "test"},
    )
    assert result["status"] == "accepted"


def test_audit_record_preserves_cleanup_blocker(tmp_path: Path) -> None:
    accepted_record(tmp_path, "ATTITUDE_THRUST")
    record_path = tmp_path / "record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["session_cleanup"] = {"shutdown_recorded": False}
    record_path.write_text(json.dumps(record), encoding="utf-8")
    result = checker.audit_record(
        tmp_path,
        {"output_variant": "ATTITUDE_THRUST", "record": "record.json", "evidence_kind": "test"},
    )
    assert result["status"] == "blocked"
    assert "task_owned_session_cleanup_missing" in result["reasons"]
