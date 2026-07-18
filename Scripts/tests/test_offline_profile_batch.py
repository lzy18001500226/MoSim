from __future__ import annotations

import json
from pathlib import Path

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
