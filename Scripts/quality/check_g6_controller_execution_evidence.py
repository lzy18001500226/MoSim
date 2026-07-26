#!/usr/bin/env python3
"""Fail closed on missing or stale evidence from the current G6 batch.

This checker is intentionally a file/evidence audit. It does not open MWORKS
or promote an internal controller probe into a whole-aircraft or runtime claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "control_platform" / "g6_controller_execution_20260724"
OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT
MATRIX_PATH = OUTPUT_ROOT / "G6_EXECUTION_MATRIX.json"
STATUS_PATH = OUTPUT_ROOT / "G6_EXECUTION_STATUS.json"
OUTPUT_PATH = OUTPUT_ROOT / "G6_EXECUTION_EVIDENCE_AUDIT.json"
SCHEMA = "mosim.g6_controller_execution_evidence_audit.v1"
REPORT_RESULT_RECONCILIATION_SCHEMA = "mosim.g6_report_result_binding_reconciliation.v1"
REPORT_RESULT_RECONCILIATION_MODE = "offline_explicit_report_slot_reconciliation"
REPORT_RESULT_RECONCILIATION_SCOPE = (
    "Archive the existing unbound report image and bind a completed current native MWORKS result-window capture. "
    "No MWORKS session, model source, controller source, or result data was changed."
)

TARGET_HASH_PHASES = {
    "before_load",
    "after_load",
    "after_check",
    "after_open",
    "after_simulation",
    "before_record",
    "after_session_shutdown",
}
PROTECTED_SOURCE_HASH_PHASES = {
    "before_load",
    "after_prerequisite_load",
    "after_load",
    "after_check",
    "after_open",
    "after_simulation",
    "before_record",
    "after_session_shutdown",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return data


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def configure_output_root(value: Path | None) -> None:
    """Select a current evidence root while retaining historical audit outputs."""

    global OUTPUT_ROOT, MATRIX_PATH, STATUS_PATH, OUTPUT_PATH
    candidate = DEFAULT_OUTPUT_ROOT if value is None else value
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        candidate.relative_to(results_root)
    except ValueError as exc:
        raise ValueError("output root must remain below Results/") from exc
    OUTPUT_ROOT = candidate
    MATRIX_PATH = OUTPUT_ROOT / "G6_EXECUTION_MATRIX.json"
    STATUS_PATH = OUTPUT_ROOT / "G6_EXECUTION_STATUS.json"
    OUTPUT_PATH = OUTPUT_ROOT / "G6_EXECUTION_EVIDENCE_AUDIT.json"


def repo_path(path_text: str, errors: list[str], label: str) -> Path | None:
    candidate = ROOT / path_text
    try:
        candidate.resolve().relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label}: path leaves repository: {path_text}")
        return None
    return candidate


def add_if_missing(path: Path | None, errors: list[str], label: str) -> bool:
    if path is None or not path.is_file():
        errors.append(f"{label}: required file is missing")
        return False
    return True


def csv_is_readable(path: Path, errors: list[str], scheme_id: str) -> int:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or "time" not in reader.fieldnames:
                errors.append(f"{scheme_id}: raw CSV has no time column")
                return 0
            return sum(1 for _ in reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        errors.append(f"{scheme_id}: raw CSV is unreadable: {exc}")
        return 0


def declared_protected_sources(matrix_row: dict[str, Any], errors: list[str], scheme_id: str) -> list[dict[str, Any]]:
    """Derive the target/core/prerequisite source set frozen by a G6 route."""

    candidates: list[tuple[str, Any]] = [
        ("target", matrix_row.get("target")),
        ("controller_core", matrix_row.get("controller_core")),
    ]
    prerequisites = matrix_row.get("model_load_prerequisites", [])
    if not isinstance(prerequisites, list):
        errors.append(f"{scheme_id}: matrix model_load_prerequisites is not a list")
        prerequisites = []
    candidates.extend((f"model_load_prerequisite[{index}]", item) for index, item in enumerate(prerequisites))

    sources: dict[str, dict[str, Any]] = {}
    for role, candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append(f"{scheme_id}: matrix {role} source is incomplete")
            continue
        path_text = candidate.get("model_file")
        expected_hash = candidate.get("model_sha256")
        if not isinstance(path_text, str) or not isinstance(expected_hash, str):
            errors.append(f"{scheme_id}: matrix {role} source binding is incomplete")
            continue
        source = sources.get(path_text)
        if source is None:
            source = {"path": path_text, "expected_sha256": expected_hash, "roles": []}
            sources[path_text] = source
        elif source["expected_sha256"] != expected_hash:
            errors.append(f"{scheme_id}: matrix protected source has conflicting hashes: {path_text}")
            continue
        source["roles"].append(role)
    return list(sources.values())


def protected_observations_valid(
    observations: Any,
    expected_hash: str,
    errors: list[str],
    scheme_id: str,
    path_text: str,
    *,
    allow_reconciled_before_record_gap: bool = False,
) -> bool:
    """Validate all lifecycle observations for one new protected source record."""

    if not isinstance(observations, list) or not observations:
        errors.append(f"{scheme_id}: protected source has no hash observations: {path_text}")
        return False
    required_phases = set(PROTECTED_SOURCE_HASH_PHASES)
    if allow_reconciled_before_record_gap:
        required_phases.remove("before_record")
    observed = {str(item.get("phase")) for item in observations if isinstance(item, dict)}
    if not required_phases.issubset(observed):
        errors.append(f"{scheme_id}: protected source phase coverage is incomplete: {path_text}")
        return False
    for observation in observations:
        if not isinstance(observation, dict) or observation.get("expected_sha256") != expected_hash:
            errors.append(f"{scheme_id}: protected source expected hash differs: {path_text}")
            return False
        if observation.get("matches_frozen_source") is True and observation.get("sha256") == expected_hash:
            continue
        if not (
            observation.get("native_whitespace_only") is True
            and observation.get("restored_sha256") == expected_hash
            and observation.get("normalized_source_restored") is True
            and observation.get("frozen_snapshot_sha256") == expected_hash
            and observation.get("frozen_whitespace_normalized_sha256")
            == observation.get("whitespace_normalized_sha256")
        ):
            errors.append(f"{scheme_id}: protected source observation is not source-bound: {path_text}")
            return False
    return True


def report_result_reconciliation_valid(
    record: dict[str, Any],
    matrix_row: dict[str, Any],
    run_root: Path | None,
    declared_sources: list[dict[str, Any]],
    target_hash: str | None,
    errors: list[str],
    scheme_id: str,
) -> bool:
    """Validate the narrow offline repair that may leave only ``before_record`` absent.

    A guarded report-slot conflict can occur after a route has completed its
    MWORKS result read but before the terminal record phase is written.  The
    reconciliation tool never manufactures that historic observation.  This
    verifier accepts the gap only when the archived prior image, current native
    capture, result provenance, post-session source hashes, and cleanup record
    still prove the completed run.
    """

    reconciliation = record.get("report_result_binding_reconciliation")
    if reconciliation is None:
        return False
    start_error_count = len(errors)
    if not isinstance(reconciliation, dict):
        errors.append(f"{scheme_id}: report-result reconciliation is not an object")
        return False
    if run_root is None:
        errors.append(f"{scheme_id}: reconciliation has no route result root")
        return False

    required_artifacts = matrix_row.get("required_artifacts")
    report_path_text = (
        required_artifacts.get("report_result_screenshot") if isinstance(required_artifacts, dict) else None
    )
    report_path = repo_path(report_path_text, errors, f"{scheme_id}: reconciled report screenshot") if isinstance(report_path_text, str) else None
    if report_path is None:
        errors.append(f"{scheme_id}: reconciliation matrix report screenshot is absent")

    if reconciliation.get("schema") != REPORT_RESULT_RECONCILIATION_SCHEMA:
        errors.append(f"{scheme_id}: reconciliation schema is invalid")
    if reconciliation.get("scheme_id") != scheme_id:
        errors.append(f"{scheme_id}: reconciliation scheme_id differs")
    if reconciliation.get("mode") != REPORT_RESULT_RECONCILIATION_MODE:
        errors.append(f"{scheme_id}: reconciliation mode is invalid")
    if reconciliation.get("scope") != REPORT_RESULT_RECONCILIATION_SCOPE:
        errors.append(f"{scheme_id}: reconciliation scope differs")
    if reconciliation.get("previous_status") != "result_binding_failed":
        errors.append(f"{scheme_id}: reconciliation does not originate from result_binding_failed")
    if not isinstance(reconciliation.get("reconciled_at"), str) or not reconciliation["reconciled_at"]:
        errors.append(f"{scheme_id}: reconciliation timestamp is absent")
    if record.get("status") != "passed" or "error" in record:
        errors.append(f"{scheme_id}: reconciled record is not a clean passed transition")
    if not isinstance(record.get("report_result_binding_reconciled_at"), str):
        errors.append(f"{scheme_id}: reconciled record timestamp is absent")

    expected_error = (
        f"Refusing to replace a different report result screenshot: {relative(report_path)}" if report_path else None
    )
    previous_error = reconciliation.get("previous_error")
    if not isinstance(previous_error, dict) or previous_error.get("message") != expected_error:
        errors.append(f"{scheme_id}: reconciliation previous error is not the guarded report-slot conflict")

    report = record.get("report_result_screenshot")
    if not isinstance(report, dict):
        errors.append(f"{scheme_id}: reconciled report result binding is absent")
        report = {}
    current_capture_path = run_root / "screenshots" / "02_result_window.png"
    current_capture = reconciliation.get("current_native_result_capture")
    if not isinstance(current_capture, dict):
        errors.append(f"{scheme_id}: reconciliation current native capture is absent")
        current_capture = {}
    if current_capture.get("path") != relative(current_capture_path):
        errors.append(f"{scheme_id}: reconciliation native capture path differs")
    if not current_capture_path.is_file():
        errors.append(f"{scheme_id}: reconciliation native capture is missing")
    else:
        current_capture_hash = sha256(current_capture_path)
        if current_capture.get("sha256") != current_capture_hash:
            errors.append(f"{scheme_id}: reconciliation native capture hash differs")
        if current_capture.get("bytes") != current_capture_path.stat().st_size:
            errors.append(f"{scheme_id}: reconciliation native capture byte count differs")
        if report_path is not None and report_path.is_file():
            if report.get("destination") != relative(report_path) or report.get("sha256") != current_capture_hash:
                errors.append(f"{scheme_id}: reconciled report binding differs from current native capture")
            elif sha256(report_path) != current_capture_hash:
                errors.append(f"{scheme_id}: reconciled report screenshot differs from current native capture")

    report_before = reconciliation.get("report_asset_before")
    archived_asset_text = reconciliation.get("archived_report_asset")
    archived_asset = repo_path(archived_asset_text, errors, f"{scheme_id}: reconciled archived report asset") if isinstance(archived_asset_text, str) else None
    if not isinstance(report_before, dict) or report_path is None:
        errors.append(f"{scheme_id}: reconciliation prior report asset metadata is absent")
    else:
        if report_before.get("path") != relative(report_path):
            errors.append(f"{scheme_id}: reconciliation prior report path differs")
        if archived_asset is None or not archived_asset.is_file():
            errors.append(f"{scheme_id}: reconciliation archived report asset is missing")
        else:
            if report_before.get("sha256") != sha256(archived_asset):
                errors.append(f"{scheme_id}: reconciliation archived report hash differs")
            if report_before.get("bytes") != archived_asset.stat().st_size:
                errors.append(f"{scheme_id}: reconciliation archived report byte count differs")
            archive_root = (run_root / "superseded" / "report_asset_reconciliation").resolve()
            try:
                archived_asset.resolve().relative_to(archive_root)
            except ValueError:
                errors.append(f"{scheme_id}: reconciliation archived report asset leaves the route archive")

    report_reconciliation = report.get("reconciliation") if isinstance(report, dict) else None
    archive_manifest = archived_asset.parent / "REPORT_RESULT_ASSET_ARCHIVE_MANIFEST.json" if archived_asset else None
    if not isinstance(report_reconciliation, dict) or archive_manifest is None:
        errors.append(f"{scheme_id}: reconciled report binding archive metadata is absent")
    else:
        if report_reconciliation.get("archive_manifest") != relative(archive_manifest):
            errors.append(f"{scheme_id}: reconciled report binding archive manifest differs")
        if report_reconciliation.get("archived_report_asset") != archived_asset_text:
            errors.append(f"{scheme_id}: reconciled report binding archive asset differs")
        if report_reconciliation.get("previous_status") != "result_binding_failed":
            errors.append(f"{scheme_id}: reconciled report binding previous status differs")
        if report_reconciliation.get("mode") != REPORT_RESULT_RECONCILIATION_MODE:
            errors.append(f"{scheme_id}: reconciled report binding mode differs")
        if report_before and report_reconciliation.get("previous_report_sha256") != report_before.get("sha256"):
            errors.append(f"{scheme_id}: reconciled report binding prior hash differs")
        if not archive_manifest.is_file():
            errors.append(f"{scheme_id}: reconciliation archive manifest is missing")
        else:
            try:
                if read_json(archive_manifest) != reconciliation:
                    errors.append(f"{scheme_id}: reconciliation archive manifest does not match the run record")
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{scheme_id}: reconciliation archive manifest is invalid: {exc}")

    session_cleanup = record.get("session_cleanup")
    if reconciliation.get("session_cleanup") != session_cleanup:
        errors.append(f"{scheme_id}: reconciliation session cleanup differs from the run record")
    if not isinstance(session_cleanup, dict) or session_cleanup.get("verified_closed") is not True:
        errors.append(f"{scheme_id}: reconciliation dedicated session closure is not verified")
    else:
        cleanup_path_text = session_cleanup.get("log")
        cleanup_path = repo_path(cleanup_path_text, errors, f"{scheme_id}: reconciliation cleanup log") if isinstance(cleanup_path_text, str) else None
        add_if_missing(cleanup_path, errors, f"{scheme_id}: reconciliation cleanup log")

    post_shutdown = record.get("post_session_source_validation")
    if reconciliation.get("post_session_source_validation") != post_shutdown:
        errors.append(f"{scheme_id}: reconciliation post-session validation differs from the run record")
    expected_protected_hashes = {str(item["path"]): str(item["expected_sha256"]) for item in declared_sources}
    if not isinstance(post_shutdown, dict) or post_shutdown.get("phase") != "after_session_shutdown" or post_shutdown.get("state") != "passed":
        errors.append(f"{scheme_id}: reconciliation post-session validation is not passed")
    else:
        if post_shutdown.get("verified_target_sha256") != target_hash:
            errors.append(f"{scheme_id}: reconciliation post-session target hash differs")
        if post_shutdown.get("protected_source_sha256") != expected_protected_hashes:
            errors.append(f"{scheme_id}: reconciliation post-session protected-source hashes differ")

    readiness = record.get("result_readiness")
    attempts = readiness.get("attempts") if isinstance(readiness, dict) else None
    if not isinstance(readiness, dict) or readiness.get("state") != "ready" or not isinstance(attempts, list) or not any(
        isinstance(attempt, dict)
        and attempt.get("time_reaches_expected_stop") is True
        and attempt.get("full_series_ready") is True
        for attempt in attempts
    ):
        errors.append(f"{scheme_id}: reconciliation completed native result readiness is absent")

    native_result_text = record.get("native_result_locator")
    native_result = repo_path(native_result_text, errors, f"{scheme_id}: reconciliation native result") if isinstance(native_result_text, str) else None
    if reconciliation.get("native_result") != native_result_text or not add_if_missing(native_result, errors, f"{scheme_id}: reconciliation native result"):
        errors.append(f"{scheme_id}: reconciliation native result provenance differs")
    metrics_path = run_root / "metrics" / "metrics.json"
    screenshot_manifest_path = run_root / "logs" / "screenshot_manifest.json"
    if reconciliation.get("metrics") != relative(metrics_path) or not metrics_path.is_file():
        errors.append(f"{scheme_id}: reconciliation metrics provenance differs")
    if reconciliation.get("screenshot_manifest") != relative(screenshot_manifest_path) or not screenshot_manifest_path.is_file():
        errors.append(f"{scheme_id}: reconciliation screenshot manifest provenance differs")

    capture_binding = {
        "phase": "result_window",
        "destination": relative(current_capture_path),
        "destination_sha256": current_capture.get("sha256"),
    }
    phase_captures = record.get("mworks_phase_screenshots")
    if not isinstance(phase_captures, list) or not any(
        isinstance(capture, dict) and all(capture.get(key) == value for key, value in capture_binding.items())
        for capture in phase_captures
    ):
        errors.append(f"{scheme_id}: reconciliation run record does not bind the current native capture")
    try:
        manifest = read_json(screenshot_manifest_path)
        captures = manifest.get("captures") if isinstance(manifest, dict) else None
        if manifest.get("scheme_id") != scheme_id or not isinstance(captures, list) or not any(
            isinstance(capture, dict) and all(capture.get(key) == value for key, value in capture_binding.items())
            for capture in captures
        ):
            errors.append(f"{scheme_id}: reconciliation screenshot manifest does not bind the current native capture")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{scheme_id}: reconciliation screenshot manifest is invalid: {exc}")

    return len(errors) == start_error_count


def audit() -> dict[str, Any]:
    errors: list[str] = []
    rows_out: list[dict[str, Any]] = []
    matrix = read_json(MATRIX_PATH)
    status = read_json(STATUS_PATH)
    rows = matrix.get("rows")
    if not isinstance(rows, list) or len(rows) != 46:
        errors.append("matrix must contain exactly 46 routes")
        rows = []
    status_rows = {
        str(row.get("scheme_id")): row
        for row in status.get("rows", [])
        if isinstance(row, dict)
    }
    if status.get("summary", {}).get("passed_count") != 46:
        errors.append("G6 status does not report 46 passed routes")

    phase_bound_count = 0
    after_shutdown_reconciled_phase_count = 0
    legacy_reconciled_count = 0
    protected_phase_bound_count = 0
    protected_after_shutdown_reconciled_count = 0
    protected_legacy_reconciled_count = 0
    result_screenshot_count = 0
    for matrix_row in rows:
        if not isinstance(matrix_row, dict):
            errors.append("matrix contains a non-object route")
            continue
        scheme_id = str(matrix_row.get("scheme_id") or "")
        target = matrix_row.get("target") if isinstance(matrix_row.get("target"), dict) else {}
        target_file_text = target.get("model_file")
        target_hash = target.get("model_sha256")
        row_errors_before = len(errors)
        source_current_hash = None
        if not isinstance(target_file_text, str) or not isinstance(target_hash, str):
            errors.append(f"{scheme_id}: matrix target is incomplete")
        else:
            target_file = repo_path(target_file_text, errors, f"{scheme_id}: target")
            if add_if_missing(target_file, errors, f"{scheme_id}: target"):
                source_current_hash = sha256(target_file)
                if source_current_hash != target_hash:
                    errors.append(f"{scheme_id}: current target source hash differs from frozen matrix")

        declared_sources = declared_protected_sources(matrix_row, errors, scheme_id)
        protected_current_hashes: dict[str, str | None] = {}
        for declared in declared_sources:
            path_text = str(declared["path"])
            expected_hash = str(declared["expected_sha256"])
            source_file = repo_path(path_text, errors, f"{scheme_id}: protected source")
            if add_if_missing(source_file, errors, f"{scheme_id}: protected source"):
                current_hash = sha256(source_file)
                protected_current_hashes[path_text] = current_hash
                if current_hash != expected_hash:
                    errors.append(f"{scheme_id}: current protected source differs from frozen matrix: {path_text}")
            else:
                protected_current_hashes[path_text] = None

        run_root_text = matrix_row.get("result_root")
        run_root = repo_path(str(run_root_text), errors, f"{scheme_id}: result root") if isinstance(run_root_text, str) else None
        record_path = run_root / "RUN_RECORD.json" if run_root else None
        record: dict[str, Any] = {}
        if add_if_missing(record_path, errors, f"{scheme_id}: run record"):
            try:
                record = read_json(record_path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{scheme_id}: invalid run record: {exc}")
        protected_hash_binding = "absent"
        hash_binding = "legacy_current_source_reconciled"
        if record:
            if record.get("status") != "passed":
                errors.append(f"{scheme_id}: run record status is not passed")
            if status_rows.get(scheme_id, {}).get("status") != "passed":
                errors.append(f"{scheme_id}: status table is not passed")
            record_target = record.get("matrix", {}).get("target") if isinstance(record.get("matrix"), dict) else {}
            if record_target != target:
                errors.append(f"{scheme_id}: run record target does not equal current frozen target")
            if record.get("verified_target_sha256") != target_hash:
                errors.append(f"{scheme_id}: pre-load target hash is missing or differs")
            reconciliation_valid = report_result_reconciliation_valid(
                record,
                matrix_row,
                run_root,
                declared_sources,
                target_hash if isinstance(target_hash, str) else None,
                errors,
                scheme_id,
            )
            observations = record.get("target_hash_observations")
            if isinstance(observations, list) and observations:
                observed_phases = {str(item.get("phase")) for item in observations if isinstance(item, dict)}
                reconciliation_gap_used = reconciliation_valid and "before_record" not in observed_phases
                required_phases = set(TARGET_HASH_PHASES)
                if reconciliation_gap_used:
                    required_phases.remove("before_record")
                if not required_phases.issubset(observed_phases):
                    errors.append(f"{scheme_id}: phase-bound target hash observations are incomplete")
                else:
                    target_observations_ok = True
                    for item in observations:
                        if not isinstance(item, dict) or item.get("expected_sha256") != target_hash:
                            target_observations_ok = False
                            break
                        matches_target = item.get("matches_frozen_target")
                        if matches_target is None:
                            # New protected-source records share the target
                            # observation list but name the generic boundary.
                            matches_target = item.get("matches_frozen_source")
                        if matches_target is not True:
                            target_observations_ok = False
                            break
                        if item.get("sha256") == target_hash:
                            continue
                        if not (
                            item.get("native_whitespace_only") is True
                            and item.get("restored_sha256") == target_hash
                            and item.get("normalized_source_restored") is True
                            and (
                                item.get("whitespace_normalized_sha256") == target_hash
                                or (
                                    item.get("frozen_snapshot_sha256") == target_hash
                                    and item.get("frozen_whitespace_normalized_sha256")
                                    == item.get("whitespace_normalized_sha256")
                                )
                            )
                        ):
                            target_observations_ok = False
                            break
                    if target_observations_ok:
                        if reconciliation_gap_used:
                            after_shutdown_reconciled_phase_count += 1
                            hash_binding = "phase_bound_after_shutdown_reconciled"
                        else:
                            phase_bound_count += 1
                            hash_binding = "phase_bound"
                    else:
                        errors.append(f"{scheme_id}: a phase-bound target hash observation differs")
            else:
                # These records predate per-phase hashing. Their frozen input
                # and persistent current source are still checked above, but
                # they remain explicitly distinguishable from new phase-bound
                # records instead of being silently upgraded.
                legacy_reconciled_count += 1

            protected_records = record.get("protected_sources")
            if isinstance(protected_records, list) and protected_records:
                protected_hash_binding = "phase_bound_protected"
                protected_reconciliation_gap_used = False
                record_by_path = {
                    item.get("path"): item
                    for item in protected_records
                    if isinstance(item, dict) and isinstance(item.get("path"), str)
                }
                if len(record_by_path) != len(protected_records):
                    errors.append(f"{scheme_id}: protected source record contains an invalid path")
                for declared in declared_sources:
                    path_text = str(declared["path"])
                    expected_hash = str(declared["expected_sha256"])
                    protected_record = record_by_path.get(path_text)
                    if not isinstance(protected_record, dict):
                        errors.append(f"{scheme_id}: protected source record is missing: {path_text}")
                        continue
                    if protected_record.get("expected_sha256") != expected_hash:
                        errors.append(f"{scheme_id}: protected source record hash differs: {path_text}")
                    if set(protected_record.get("roles", [])) != set(declared["roles"]):
                        errors.append(f"{scheme_id}: protected source record roles differ: {path_text}")
                    snapshot = protected_record.get("frozen_snapshot")
                    snapshot_path = None
                    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("path"), str):
                        errors.append(f"{scheme_id}: protected source snapshot is absent: {path_text}")
                    else:
                        snapshot_path = repo_path(snapshot["path"], errors, f"{scheme_id}: protected source snapshot")
                        if add_if_missing(snapshot_path, errors, f"{scheme_id}: protected source snapshot"):
                            snapshot_hash = sha256(snapshot_path)
                            if snapshot_hash != expected_hash or snapshot.get("sha256") != expected_hash:
                                errors.append(f"{scheme_id}: protected source snapshot hash differs: {path_text}")
                    protected_observations = protected_record.get("hash_observations")
                    observed_protected_phases = {
                        str(item.get("phase"))
                        for item in protected_observations
                        if isinstance(item, dict)
                    } if isinstance(protected_observations, list) else set()
                    protected_gap_used = reconciliation_valid and "before_record" not in observed_protected_phases
                    protected_reconciliation_gap_used = protected_reconciliation_gap_used or protected_gap_used
                    protected_observations_valid(
                        protected_observations,
                        expected_hash,
                        errors,
                        scheme_id,
                        path_text,
                        allow_reconciled_before_record_gap=protected_gap_used,
                    )
                extra_paths = set(record_by_path) - {str(item["path"]) for item in declared_sources}
                if extra_paths:
                    errors.append(f"{scheme_id}: protected source record has undeclared paths")
                if protected_reconciliation_gap_used:
                    protected_after_shutdown_reconciled_count += 1
                    protected_hash_binding = "phase_bound_after_shutdown_reconciled"
                else:
                    protected_phase_bound_count += 1
            else:
                protected_hash_binding = "legacy_current_source_reconciled"
                protected_legacy_reconciled_count += 1

            session_cleanup = record.get("session_cleanup")
            if not isinstance(session_cleanup, dict):
                errors.append(f"{scheme_id}: post-session cleanup provenance is absent")
            elif session_cleanup.get("verified_closed") is not True:
                errors.append(f"{scheme_id}: dedicated MWORKS session was not verified closed")
            else:
                cleanup_path_text = session_cleanup.get("log")
                cleanup_path = (
                    repo_path(cleanup_path_text, errors, f"{scheme_id}: session cleanup log")
                    if isinstance(cleanup_path_text, str)
                    else None
                )
                if add_if_missing(cleanup_path, errors, f"{scheme_id}: session cleanup log"):
                    try:
                        cleanup_data = read_json(cleanup_path)
                        if cleanup_data.get("verified_closed") is not True:
                            errors.append(f"{scheme_id}: session cleanup log does not verify closure")
                    except (OSError, json.JSONDecodeError, ValueError) as exc:
                        errors.append(f"{scheme_id}: session cleanup log is invalid: {exc}")

            raw_path = run_root / "raw" / "result.csv" if run_root else None
            if add_if_missing(raw_path, errors, f"{scheme_id}: raw CSV"):
                row_count = csv_is_readable(raw_path, errors, scheme_id)
                if row_count <= 10:
                    errors.append(f"{scheme_id}: raw CSV has {row_count} rows, expected > 10")
            else:
                row_count = 0
            metrics_path = run_root / "metrics" / "metrics.json" if run_root else None
            if add_if_missing(metrics_path, errors, f"{scheme_id}: metrics"):
                try:
                    metrics = read_json(metrics_path)
                    if metrics.get("valid") is not True or int(metrics.get("row_count", 0)) <= 10:
                        errors.append(f"{scheme_id}: metrics do not report a valid result with > 10 rows")
                except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
                    errors.append(f"{scheme_id}: metrics are invalid: {exc}")
            native_locator = record.get("native_result_locator")
            native_path = repo_path(native_locator, errors, f"{scheme_id}: native result") if isinstance(native_locator, str) else None
            add_if_missing(native_path, errors, f"{scheme_id}: native result")
            result_screenshot = run_root / "screenshots" / "02_result_window.png" if run_root else None
            if add_if_missing(result_screenshot, errors, f"{scheme_id}: result screenshot"):
                result_screenshot_count += 1
            screenshot_manifest = run_root / "logs" / "screenshot_manifest.json" if run_root else None
            if add_if_missing(screenshot_manifest, errors, f"{scheme_id}: screenshot manifest"):
                try:
                    screenshot_data = read_json(screenshot_manifest)
                    if screenshot_data.get("scheme_id") != scheme_id:
                        errors.append(f"{scheme_id}: screenshot manifest identity mismatch")
                    captures = screenshot_data.get("captures")
                    if not isinstance(captures, list) or not any(
                        isinstance(capture, dict) and capture.get("phase") == "result_window"
                        for capture in captures
                    ):
                        errors.append(f"{scheme_id}: screenshot manifest has no result-window capture")
                except (OSError, json.JSONDecodeError, ValueError) as exc:
                    errors.append(f"{scheme_id}: screenshot manifest is invalid: {exc}")
            report = record.get("report_result_screenshot")
            if not isinstance(report, dict):
                errors.append(f"{scheme_id}: report result screenshot binding is absent")
            else:
                destination_text = report.get("destination")
                destination = repo_path(destination_text, errors, f"{scheme_id}: report screenshot") if isinstance(destination_text, str) else None
                if add_if_missing(destination, errors, f"{scheme_id}: report screenshot") and result_screenshot and result_screenshot.is_file():
                    if sha256(destination) != sha256(result_screenshot):
                        errors.append(f"{scheme_id}: report screenshot differs from bound native capture")

        rows_out.append(
            {
                "scheme_id": scheme_id,
                "evidence_class": matrix_row.get("evidence_class"),
                "current_target_sha256": source_current_hash,
                "current_protected_source_sha256": protected_current_hashes,
                "hash_binding": hash_binding,
                "protected_hash_binding": protected_hash_binding,
                "row_ok": len(errors) == row_errors_before,
            }
        )

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matrix": {"path": relative(MATRIX_PATH), "sha256": sha256(MATRIX_PATH)},
        "status": {"path": relative(STATUS_PATH), "sha256": sha256(STATUS_PATH)},
        "summary": {
            "route_count": len(rows),
            "passed_count": sum(1 for row in rows_out if row["row_ok"]),
            "phase_bound_hash_count": phase_bound_count,
            "after_shutdown_reconciled_phase_count": after_shutdown_reconciled_phase_count,
            "legacy_current_source_reconciled_count": legacy_reconciled_count,
            "protected_phase_bound_hash_count": protected_phase_bound_count,
            "protected_after_shutdown_reconciled_count": protected_after_shutdown_reconciled_count,
            "protected_legacy_current_source_reconciled_count": protected_legacy_reconciled_count,
            "result_screenshot_count": result_screenshot_count,
        },
        "rows": rows_out,
        "errors": errors,
        "ok": not errors,
        "claim_boundary": "File and provenance audit only. It verifies current G6 evidence binding; it does not expand internal probes into whole-aircraft, code-generation, Gazebo, or flight-runtime acceptance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the audit JSON beside the G6 matrix")
    parser.add_argument(
        "--output-root",
        type=Path,
        help="project-local Results directory containing the frozen G6 matrix",
    )
    args = parser.parse_args()
    configure_output_root(args.output_root)
    try:
        report = audit()
    except Exception as exc:
        report = {"schema": SCHEMA, "ok": False, "errors": [f"audit failed: {type(exc).__name__}: {exc}"]}
    if args.write:
        OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report.get("ok"), "summary": report.get("summary"), "errors": report.get("errors")}, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
