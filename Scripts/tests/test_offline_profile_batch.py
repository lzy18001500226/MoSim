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
    )
    assert manifest["status"] == "blocked"
    assert manifest["records"][0]["reason_code"] == "certification_failed"
    assert manifest["records"][0]["return_code"] == 7


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
