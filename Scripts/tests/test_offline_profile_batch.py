from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from Scripts.mworks import run_offline_profile_batch as batch


def test_resolve_profile_rejects_disabled_and_multi_uav_entries() -> None:
    catalog = {
        "certified_profiles": [
            {"profile_id": "ok", "vehicle_count": 1},
            {"profile_id": "multi", "vehicle_count": 3},
        ],
        "disabled_profiles": [
            {"profile_id": "disabled", "vehicle_count": 1, "certification_state": "blocked_current_run"}
        ],
    }
    assert batch.resolve_profile(catalog, "ok")["profile_id"] == "ok"
    for profile_id, reason in (("disabled", "profile_disabled"), ("multi", "batch_requires_single_uav_profile")):
        try:
            batch.resolve_profile(catalog, profile_id)
        except ValueError as error:
            assert str(error).startswith(reason)
        else:
            raise AssertionError(f"{profile_id} was not rejected")


def test_run_one_records_acceptance_and_logs(monkeypatch, tmp_path: Path) -> None:
    class Completed:
        returncode = 0
        stdout = '{"status":"accepted"}\n'
        stderr = ""

    captured: list[str] = []

    def fake_run(*args, **kwargs):
        assert kwargs["cwd"] == batch.ROOT
        captured.extend(args[0])
        return Completed()

    monkeypatch.setattr(batch.subprocess, "run", fake_run)
    record = batch.run_one(
        "official_pid",
        {"controller_id": "official_pid", "output_variant": "ROTOR_COMMAND"},
        "batch-test",
        1,
        reuse_generated=True,
        record_only=True,
        timeout_s=12,
        output_dir=tmp_path,
    )
    assert record["status"] == "accepted"
    assert record["return_code"] == 0
    assert "--reuse-generated" in captured
    assert "--record-only" in captured


def test_batch_manifest_schema_is_json_serializable(tmp_path: Path) -> None:
    manifest = {
        "schema": "mosim.model_studio.offline_batch.v1",
        "status": "blocked",
        "records": [],
    }
    path = tmp_path / "BATCH_MANIFEST.json"
    batch.write_json(path, manifest)
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == "mosim.model_studio.offline_batch.v1"


def test_preflight_blocker_writes_a_manifest(tmp_path: Path) -> None:
    manifest = batch.write_batch_manifest(
        tmp_path,
        "batch-blocked",
        ["missing"],
        [batch.blocked_record("missing", "profile_not_allowlisted:missing")],
        started="2026-07-19T12:00:00+08:00",
        reuse_generated=False,
        record_only=False,
        timeout_s=10,
        lineage={"root_batch_id": "batch-blocked", "retry_of": None, "attempt": 1},
    )
    assert manifest["status"] == "blocked"
    record = json.loads((tmp_path / "BATCH_MANIFEST.json").read_text(encoding="utf-8"))["records"][0]
    assert record["reason_code"] == "profile_not_allowlisted:missing"
    assert record["run_id"] is None


def test_run_one_failure_is_recorded_and_batch_can_be_audited(monkeypatch, tmp_path: Path) -> None:
    class Failed:
        returncode = 7
        stdout = ""
        stderr = "solver_failed"

    monkeypatch.setattr(batch.subprocess, "run", lambda *args, **kwargs: Failed())
    record = batch.run_one(
        "official_pid",
        {"controller_id": "official_pid", "output_variant": "ATTITUDE_THRUST"},
        "batch-failed",
        1,
        reuse_generated=False,
        record_only=False,
        timeout_s=10,
        output_dir=tmp_path,
    )
    manifest = batch.write_batch_manifest(
        tmp_path,
        "batch-failed",
        ["official_pid"],
        [record],
        started="2026-07-19T12:00:00+08:00",
        reuse_generated=False,
        record_only=False,
        timeout_s=10,
        lineage={"root_batch_id": "batch-failed", "retry_of": None, "attempt": 1},
    )
    assert manifest["status"] == "blocked"
    assert manifest["records"][0]["reason_code"] == "certification_failed"
    assert manifest["records"][0]["return_code"] == 7


def test_retry_source_and_index_preserve_lineage(tmp_path: Path) -> None:
    batch_root = tmp_path / "batches"
    source_dir = batch_root / "source"
    source_dir.mkdir(parents=True)
    batch.write_batch_manifest(
        source_dir,
        "source",
        ["official_pid"],
        [batch.blocked_record("official_pid", "certification_failed")],
        started="2026-07-19T12:00:00+08:00",
        reuse_generated=False,
        record_only=False,
        timeout_s=10,
        lineage={"root_batch_id": "source", "retry_of": None, "attempt": 1},
        batch_root=batch_root,
    )
    source = batch.load_retry_source(batch_root, "source")
    retry_dir = batch_root / "retry"
    retry_dir.mkdir()
    batch.write_batch_manifest(
        retry_dir,
        "retry",
        source["requested_profiles"],
        [batch.blocked_record("official_pid", "certification_timeout")],
        started="2026-07-19T12:01:00+08:00",
        reuse_generated=False,
        record_only=False,
        timeout_s=10,
        lineage={"root_batch_id": "source", "retry_of": "source", "attempt": 2},
        batch_root=batch_root,
    )
    index = json.loads((batch_root / batch.BATCH_INDEX_NAME).read_text(encoding="utf-8"))
    assert index["summary"] == {
        "batch_count": 2,
        "accepted_count": 0,
        "blocked_count": 2,
        "index_error_count": 0,
    }
    assert index["latest_batch_id"] == "retry"
    assert index["entries"][-1]["lineage"]["attempt"] == 2


def test_main_retry_inherits_profiles_and_writes_attempt_two(monkeypatch, tmp_path: Path) -> None:
    batch_root = tmp_path / "batches"
    source_dir = batch_root / "source"
    source_dir.mkdir(parents=True)
    batch.write_batch_manifest(
        source_dir,
        "source",
        ["official_pid"],
        [batch.blocked_record("official_pid", "certification_failed")],
        started="2026-07-19T12:00:00+08:00",
        reuse_generated=False,
        record_only=False,
        timeout_s=10,
        lineage={"root_batch_id": "source", "retry_of": None, "attempt": 1},
        batch_root=batch_root,
    )
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps({"certified_profiles": [{"profile_id": "official_pid", "vehicle_count": 1}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(batch, "BATCH_ROOT", batch_root)
    monkeypatch.setattr(batch, "CATALOG", catalog_path)
    captured: list[str] = []

    class Completed:
        returncode = 7
        stdout = ""
        stderr = "retry_failed"

    def fake_run(*args, **kwargs):
        captured.extend(args[0])
        return Completed()

    monkeypatch.setattr(batch.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_offline_profile_batch.py", "--retry-batch-id", "source", "--batch-id", "retry-cli"],
    )
    assert batch.main() == 2
    assert "--certified-profile-id" in captured
    manifest = json.loads((batch_root / "retry-cli" / "BATCH_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["requested_profiles"] == ["official_pid"]
    assert manifest["lineage"] == {"root_batch_id": "source", "retry_of": "source", "attempt": 2}


def test_model_studio_uses_retry_lineage_and_result_index() -> None:
    source = (batch.ROOT / "apps" / "model_studio" / "src" / "app.jl").read_text(encoding="utf-8")
    assert '"--retry-batch-id"' in source
    assert "BATCH_INDEX.json" in source
    assert "LastOfflineBatchId" in source


@pytest.mark.parametrize(
    ("profile_id", "profile", "reason"),
    [
        ("disabled", {"certification_state": "blocked_current_run", "vehicle_count": 1}, "profile_disabled"),
        ("multi", {"vehicle_count": 3}, "batch_requires_single_uav_profile"),
        ("direct", {"vehicle_count": 1, "execution_kind": "direct_model"}, "batch_wrapper_required_for_profile"),
    ],
)
def test_main_preflight_failures_write_blocked_manifest(
    monkeypatch, tmp_path: Path, profile_id: str, profile: dict, reason: str
) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps({"certified_profiles": [{"profile_id": profile_id, **profile}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(batch, "CATALOG", catalog_path)
    monkeypatch.setattr(batch, "BATCH_ROOT", tmp_path / "batches")
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_offline_profile_batch.py", "--profile-id", profile_id, "--batch-id", f"test-{profile_id}"],
    )
    assert batch.main() == 2
    manifest = json.loads(
        (tmp_path / "batches" / f"test-{profile_id}" / "BATCH_MANIFEST.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "blocked"
    assert manifest["completed_profiles"] == []
    assert manifest["records"][0]["reason_code"].startswith(reason)


def test_main_unknown_profile_writes_blocked_manifest(monkeypatch, tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps({"certified_profiles": []}), encoding="utf-8")
    monkeypatch.setattr(batch, "CATALOG", catalog_path)
    monkeypatch.setattr(batch, "BATCH_ROOT", tmp_path / "batches")
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_offline_profile_batch.py", "--profile-id", "missing", "--batch-id", "test-missing"],
    )
    assert batch.main() == 2
    manifest = json.loads(
        (tmp_path / "batches" / "test-missing" / "BATCH_MANIFEST.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "blocked"
    assert manifest["records"][0]["reason_code"] == "profile_not_allowlisted:missing"
