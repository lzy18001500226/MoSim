from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "check_g6_controller_execution_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("g6_controller_evidence_audit", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def reconciled_fixture(tmp_path: Path):
    module = load_module()
    module.ROOT = tmp_path
    scheme_id = "reconciled_route"
    source = tmp_path / "Models" / "Controller.mo"
    source.parent.mkdir(parents=True)
    source.write_text("model Controller end Controller;\n", encoding="utf-8")
    source_hash = module.sha256(source)
    source_path = module.relative(source)
    run_root = tmp_path / "Results" / "g6" / "runs" / scheme_id
    report_path = tmp_path / "Docs" / "report" / "reconciled_route.png"
    result_capture = run_root / "screenshots" / "02_result_window.png"
    result_capture.parent.mkdir(parents=True)
    result_capture.write_bytes(b"current native result window")
    capture_hash = module.sha256(result_capture)
    report_path.parent.mkdir(parents=True)
    report_path.write_bytes(result_capture.read_bytes())
    native_result = run_root / "raw" / "native" / "Result.msr"
    native_result.parent.mkdir(parents=True)
    native_result.write_bytes(b"native result")
    metrics = run_root / "metrics" / "metrics.json"
    write_json(metrics, {"valid": True, "row_count": 11})
    cleanup_log = run_root / "logs" / "session_cleanup.json"
    write_json(cleanup_log, {"verified_closed": True})
    screenshot_manifest = run_root / "logs" / "screenshot_manifest.json"
    capture = {
        "phase": "result_window",
        "destination": module.relative(result_capture),
        "destination_sha256": capture_hash,
    }
    write_json(screenshot_manifest, {"scheme_id": scheme_id, "captures": [capture]})

    report_before = b"prior unbound report image"
    archive_dir = run_root / "superseded" / "report_asset_reconciliation" / "one"
    archived_report = archive_dir / "report_result_before_reconciliation.png"
    archived_report.parent.mkdir(parents=True)
    archived_report.write_bytes(report_before)
    cleanup = {
        "log": module.relative(cleanup_log),
        "requested": True,
        "verified_closed": True,
        "finished_at": "2026-07-26T00:00:00+08:00",
    }
    post_shutdown = {
        "phase": "after_session_shutdown",
        "state": "passed",
        "verified_target_sha256": source_hash,
        "protected_source_sha256": {source_path: source_hash},
    }
    row = {
        "scheme_id": scheme_id,
        "result_root": module.relative(run_root),
        "target": {"model_file": source_path, "model_sha256": source_hash},
        "controller_core": {"model_file": source_path, "model_sha256": source_hash},
        "model_load_prerequisites": [],
        "required_artifacts": {"report_result_screenshot": module.relative(report_path)},
    }
    previous_error = f"Refusing to replace a different report result screenshot: {module.relative(report_path)}"
    reconciliation = {
        "schema": module.REPORT_RESULT_RECONCILIATION_SCHEMA,
        "scheme_id": scheme_id,
        "reconciled_at": "2026-07-26T00:01:00+08:00",
        "mode": module.REPORT_RESULT_RECONCILIATION_MODE,
        "scope": module.REPORT_RESULT_RECONCILIATION_SCOPE,
        "previous_status": "result_binding_failed",
        "previous_error": {"message": previous_error},
        "report_asset_before": {
            "path": module.relative(report_path),
            "sha256": sha256_bytes(report_before),
            "bytes": len(report_before),
        },
        "archived_report_asset": module.relative(archived_report),
        "current_native_result_capture": {
            "path": module.relative(result_capture),
            "sha256": capture_hash,
            "bytes": result_capture.stat().st_size,
        },
        "native_result": module.relative(native_result),
        "metrics": module.relative(metrics),
        "screenshot_manifest": module.relative(screenshot_manifest),
        "post_session_source_validation": post_shutdown,
        "session_cleanup": cleanup,
    }
    archive_manifest = archive_dir / "REPORT_RESULT_ASSET_ARCHIVE_MANIFEST.json"
    write_json(archive_manifest, reconciliation)
    record = {
        "scheme_id": scheme_id,
        "status": "passed",
        "matrix": {"target": row["target"]},
        "verified_target_sha256": source_hash,
        "session_cleanup": cleanup,
        "post_session_source_validation": post_shutdown,
        "result_readiness": {
            "state": "ready",
            "attempts": [{"time_reaches_expected_stop": True, "full_series_ready": True}],
        },
        "native_result_locator": module.relative(native_result),
        "mworks_phase_screenshots": [capture],
        "report_result_screenshot": {
            "source": module.relative(result_capture),
            "destination": module.relative(report_path),
            "sha256": capture_hash,
            "bytes": result_capture.stat().st_size,
            "reconciliation": {
                "archive_manifest": module.relative(archive_manifest),
                "archived_report_asset": module.relative(archived_report),
                "previous_report_sha256": sha256_bytes(report_before),
                "previous_status": "result_binding_failed",
                "mode": module.REPORT_RESULT_RECONCILIATION_MODE,
            },
        },
        "report_result_binding_reconciliation": reconciliation,
        "report_result_binding_reconciled_at": "2026-07-26T00:01:00+08:00",
    }
    declared_sources = [{"path": source_path, "expected_sha256": source_hash, "roles": ["target", "controller_core"]}]
    observations = [
        {"phase": phase, "expected_sha256": source_hash, "sha256": source_hash, "matches_frozen_source": True}
        for phase in sorted(module.PROTECTED_SOURCE_HASH_PHASES - {"before_record"})
    ]
    return module, row, record, run_root, declared_sources, observations


def test_accepts_only_the_verified_after_shutdown_reconciliation_gap(tmp_path: Path) -> None:
    module, row, record, run_root, declared_sources, observations = reconciled_fixture(tmp_path)
    errors: list[str] = []

    assert module.report_result_reconciliation_valid(
        record,
        row,
        run_root,
        declared_sources,
        row["target"]["model_sha256"],
        errors,
        row["scheme_id"],
    )
    assert module.protected_observations_valid(
        observations,
        row["target"]["model_sha256"],
        errors,
        row["scheme_id"],
        row["target"]["model_file"],
        allow_reconciled_before_record_gap=True,
    )
    assert not errors

    strict_errors: list[str] = []
    assert not module.protected_observations_valid(
        observations,
        row["target"]["model_sha256"],
        strict_errors,
        row["scheme_id"],
        row["target"]["model_file"],
    )
    assert "phase coverage is incomplete" in strict_errors[0]


def test_reconciliation_rejects_a_changed_archived_report_asset(tmp_path: Path) -> None:
    module, row, record, run_root, declared_sources, _ = reconciled_fixture(tmp_path)
    archive = tmp_path / record["report_result_binding_reconciliation"]["archived_report_asset"]
    archive.write_bytes(b"tampered archive")
    errors: list[str] = []

    assert not module.report_result_reconciliation_valid(
        record,
        row,
        run_root,
        declared_sources,
        row["target"]["model_sha256"],
        errors,
        row["scheme_id"],
    )
    assert any("archived report hash differs" in error for error in errors)
