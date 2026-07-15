"""Validate a completed MoSim run evidence directory.

The checker validates files under Results/runs/<run_id>. It is offline and
does not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from check_experiment_profile import canonical_hash
from collect_runtime_evidence import DEFAULT_RUNTIME_LOG_EXPORTS, get_runtime_log_profile, load_runtime_log_profiles


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS_SCHEMA = ROOT / "Config" / "profiles" / "metrics_schema.json"
DEFAULT_PROFILE_CATALOG = ROOT / "Config" / "profiles" / "catalog.json"
TRACKING_COLUMNS = {
    "time_s",
    "ref_x_m",
    "ref_y_m",
    "ref_z_m",
    "truth_x_m",
    "truth_y_m",
    "truth_z_m",
}
PLACEHOLDER_PREFIX = "<"
PLACEHOLDER_SUFFIX = ">"
IGNORED_DIRECTORY_FILES = {".gitkeep", ".keep", "README.md"}


def file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def load_json(path: Path, errors: list[dict[str, str]], code: str) -> dict[str, Any] | None:
    if not path.is_file():
        add_error(errors, code, f"required JSON file is missing: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_error(errors, code, f"invalid JSON file {path}: {exc}")
        return None


def evidence_path(run_dir: Path, manifest: dict[str, Any], key: str, default: str) -> Path:
    evidence = manifest.get("evidence", {})
    value = evidence.get(key, default)
    path = Path(value)
    return path if path.is_absolute() else run_dir / path


def displayed_path_to_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def run_relative_path(run_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.exists() or path.parts[:2] == ("Results", "runs"):
        return root_relative
    return run_dir / path


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped.startswith(PLACEHOLDER_PREFIX) and stripped.endswith(PLACEHOLDER_SUFFIX)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    return False


def check_manifest_placeholders(manifest: dict[str, Any], errors: list[dict[str, str]]) -> None:
    if has_placeholder(manifest):
        add_error(errors, "R-PLACEHOLDER-01", "RUN_MANIFEST.json still contains template placeholder values")


def check_run_id_consistency(run_dir: Path, manifest: dict[str, Any], errors: list[dict[str, str]]) -> None:
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        add_error(errors, "R-RUNID-01", "RUN_MANIFEST.json must contain a non-empty run_id")
        return
    if run_dir.name != run_id:
        add_error(errors, "R-RUNID-02", f"run directory name {run_dir.name} does not match manifest run_id {run_id}")


def check_required_artifacts(run_dir: Path, manifest: dict[str, Any], errors: list[dict[str, str]]) -> None:
    for artifact in manifest.get("evidence", {}).get("required_artifacts", []):
        path = run_dir / artifact
        if not path.exists():
            add_error(errors, "R-ARTIFACT-01", f"required run artifact is missing: {artifact}")


def check_runtime_log_manifest(
    run_dir: Path,
    manifest: dict[str, Any],
    row_count: int,
    runtime_log_profiles_path: Path,
    errors: list[dict[str, str]],
) -> None:
    runtime_manifest_path = evidence_path(run_dir, manifest, "runtime_log_manifest", "runtime_log_manifest.json")
    runtime_packet = load_json(runtime_manifest_path, errors, "R-RUNTIME-JSON-01")
    if runtime_packet is None:
        return

    run_id = manifest.get("run_id")
    experiment_id = manifest.get("experiment_profile_id")
    if runtime_packet.get("run_id") != run_id:
        add_error(errors, "R-RUNTIME-01", "runtime_log_manifest.json run_id does not match RUN_MANIFEST.json")
    if runtime_packet.get("experiment_profile_id") != experiment_id:
        add_error(errors, "R-RUNTIME-02", "runtime_log_manifest.json experiment_profile_id does not match RUN_MANIFEST.json")

    profile_id = runtime_packet.get("runtime_log_profile")
    if not isinstance(profile_id, str) or not profile_id:
        add_error(errors, "R-RUNTIME-03", "runtime_log_manifest.json must contain runtime_log_profile")
        return
    try:
        profile = get_runtime_log_profile(load_runtime_log_profiles(runtime_log_profiles_path), profile_id)
    except ValueError as exc:
        add_error(errors, "R-RUNTIME-04", str(exc))
        return

    compatible_ids = profile.get("compatible_experiment_ids", ["*"])
    if "*" not in compatible_ids and experiment_id not in compatible_ids:
        add_error(errors, "R-RUNTIME-05", f"runtime log profile {profile_id} is not compatible with {experiment_id}")

    artifacts = runtime_packet.get("artifacts")
    if not isinstance(artifacts, list):
        add_error(errors, "R-RUNTIME-ARTIFACT-01", "runtime_log_manifest.json must contain artifacts list")
        return

    artifacts_by_slot = {item.get("slot"): item for item in artifacts if isinstance(item, dict)}
    profile_artifacts = profile.get("artifacts", {})
    for slot in sorted(set(artifacts_by_slot) - set(profile_artifacts)):
        add_error(errors, "R-RUNTIME-ARTIFACT-02", f"runtime_log_manifest.json contains unknown artifact slot: {slot}")

    for slot, spec in profile_artifacts.items():
        item = artifacts_by_slot.get(slot)
        if spec.get("required", False) and item is None:
            add_error(errors, "R-RUNTIME-ARTIFACT-03", f"required runtime artifact slot is missing: {slot}")
            continue
        if item is None:
            continue
        destination = item.get("destination")
        if not isinstance(destination, str) or not destination:
            add_error(errors, "R-RUNTIME-ARTIFACT-04", f"runtime artifact {slot} missing destination")
            continue
        artifact_path = displayed_path_to_path(destination)
        expected_path = (run_dir / str(spec.get("destination", ""))).resolve()
        if artifact_path.resolve() != expected_path:
            add_error(errors, "R-RUNTIME-ARTIFACT-05", f"runtime artifact {slot} destination does not match profile")
        if not artifact_path.is_file():
            add_error(errors, "R-RUNTIME-ARTIFACT-06", f"runtime artifact file is missing: {destination}")
            continue
        actual_bytes = artifact_path.stat().st_size
        if actual_bytes <= 0:
            add_error(errors, "R-RUNTIME-ARTIFACT-07", f"runtime artifact file is empty: {destination}")
        if item.get("bytes") != actual_bytes:
            add_error(errors, "R-RUNTIME-ARTIFACT-08", f"runtime artifact {slot} byte count mismatch")
        actual_sha256 = file_sha256(artifact_path)
        if item.get("sha256") != actual_sha256:
            add_error(errors, "R-RUNTIME-ARTIFACT-09", f"runtime artifact {slot} sha256 mismatch")

    review = runtime_packet.get("review")
    if isinstance(review, dict) and isinstance(review.get("destination"), str):
        review_path = displayed_path_to_path(review["destination"])
        if review_path.is_file():
            if review.get("bytes") != review_path.stat().st_size:
                add_error(errors, "R-RUNTIME-REVIEW-01", "review byte count does not match runtime_log_manifest.json")
            if review.get("sha256") != file_sha256(review_path):
                add_error(errors, "R-RUNTIME-REVIEW-02", "review sha256 does not match runtime_log_manifest.json")

    tracking = runtime_packet.get("tracking")
    if not isinstance(tracking, dict):
        add_error(errors, "R-RUNTIME-TRACK-01", "runtime_log_manifest.json must contain tracking object")
        return
    expected_tracking_source = profile.get("tracking_source_profile")
    if expected_tracking_source and tracking.get("tracking_source_profile") != expected_tracking_source:
        add_error(errors, "R-RUNTIME-TRACK-02", "tracking_source_profile does not match RuntimeLogProfile")
    tracking_csv = tracking.get("tracking_csv")
    if not isinstance(tracking_csv, str):
        add_error(errors, "R-RUNTIME-TRACK-03", "runtime tracking entry must contain tracking_csv")
    else:
        tracking_path = displayed_path_to_path(tracking_csv)
        expected_tracking_path = evidence_path(run_dir, manifest, "tracking_log", "tracking.csv").resolve()
        if tracking_path.resolve() != expected_tracking_path:
            add_error(errors, "R-RUNTIME-TRACK-04", "runtime tracking_csv path does not match RUN_MANIFEST evidence.tracking_log")
    if tracking.get("aligned_rows") != row_count:
        add_error(errors, "R-RUNTIME-TRACK-05", "runtime tracking aligned_rows does not match tracking.csv row count")
    report_path_value = tracking.get("tracking_alignment_report")
    if not isinstance(report_path_value, str) or not displayed_path_to_path(report_path_value).is_file():
        add_error(errors, "R-RUNTIME-TRACK-06", "tracking_alignment_report is missing")


def load_runtime_export_profile(catalog_path: Path, profile_id: str, errors: list[dict[str, str]]) -> dict[str, Any] | None:
    catalog = load_json(catalog_path, errors, "R-EXPORT-CATALOG-01")
    if catalog is None:
        return None
    profiles = catalog.get("runtime_export_profiles")
    if not isinstance(profiles, dict):
        add_error(errors, "R-EXPORT-CATALOG-02", "profile catalog must contain runtime_export_profiles object")
        return None
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        add_error(errors, "R-EXPORT-CATALOG-03", f"unknown runtime export profile: {profile_id}")
        return None
    if not isinstance(profile.get("exported_artifacts"), dict):
        add_error(errors, "R-EXPORT-CATALOG-04", f"runtime export profile {profile_id} must contain exported_artifacts object")
        return None
    return profile


def check_runtime_export_manifest(
    run_dir: Path,
    manifest: dict[str, Any],
    catalog_path: Path,
    errors: list[dict[str, str]],
) -> None:
    export_contract = manifest.get("runtime_export")
    if export_contract is None:
        return
    if not isinstance(export_contract, dict):
        add_error(errors, "R-EXPORT-01", "RUN_MANIFEST.json runtime_export must be an object")
        return
    profile_id = export_contract.get("runtime_export_profile")
    if not isinstance(profile_id, str) or not profile_id:
        add_error(errors, "R-EXPORT-02", "RUN_MANIFEST.json runtime_export must declare runtime_export_profile")
        return

    profile = load_runtime_export_profile(catalog_path, profile_id, errors)
    export_manifest_path = evidence_path(run_dir, manifest, "runtime_export_manifest", "runtime_export_manifest.json")
    export_packet = load_json(export_manifest_path, errors, "R-EXPORT-JSON-01")
    if profile is None or export_packet is None:
        return

    runtime = manifest.get("runtime", {})
    expected_runtime_profile = runtime.get("runtime_profile") if isinstance(runtime, dict) else None
    expected_runtime_log_profile = export_contract.get("runtime_log_profile") or profile.get("runtime_log_profile")
    expected_tracking_source_profile = export_contract.get("tracking_source_profile") or profile.get("tracking_source_profile")

    expected_fields = {
        "run_id": manifest.get("run_id"),
        "experiment_profile_id": manifest.get("experiment_profile_id"),
        "runtime_profile": expected_runtime_profile,
        "runtime_export_profile": profile_id,
        "runtime_log_profile": expected_runtime_log_profile,
        "tracking_source_profile": expected_tracking_source_profile,
    }
    for field, expected in expected_fields.items():
        if expected and export_packet.get(field) != expected:
            add_error(errors, "R-EXPORT-03", f"runtime_export_manifest.json {field} does not match RUN_MANIFEST.json")

    if profile.get("runtime_profile") and expected_runtime_profile and profile.get("runtime_profile") != expected_runtime_profile:
        add_error(errors, "R-EXPORT-04", "RuntimeExportProfile runtime_profile does not match RUN_MANIFEST.json")
    if profile.get("runtime_log_profile") and expected_runtime_log_profile and profile.get("runtime_log_profile") != expected_runtime_log_profile:
        add_error(errors, "R-EXPORT-05", "RuntimeExportProfile runtime_log_profile does not match RUN_MANIFEST.json")
    if profile.get("tracking_source_profile") and expected_tracking_source_profile and profile.get("tracking_source_profile") != expected_tracking_source_profile:
        add_error(errors, "R-EXPORT-06", "RuntimeExportProfile tracking_source_profile does not match RUN_MANIFEST.json")

    required_slots = profile.get("required_artifact_slots", [])
    if not isinstance(required_slots, list):
        add_error(errors, "R-EXPORT-ARTIFACT-01", "RuntimeExportProfile required_artifact_slots must be a list")
        required_slots = []
    packet_required_slots = export_packet.get("required_artifact_slots")
    if packet_required_slots != required_slots:
        add_error(errors, "R-EXPORT-ARTIFACT-02", "runtime_export_manifest.json required_artifact_slots does not match RuntimeExportProfile")

    source_artifacts = export_packet.get("source_artifacts")
    if not isinstance(source_artifacts, list):
        add_error(errors, "R-EXPORT-ARTIFACT-03", "runtime_export_manifest.json must contain source_artifacts list")
        return
    artifacts_by_slot = {item.get("slot"): item for item in source_artifacts if isinstance(item, dict)}
    exported_specs = profile.get("exported_artifacts", {})
    for slot in sorted(set(artifacts_by_slot) - set(exported_specs)):
        add_error(errors, "R-EXPORT-ARTIFACT-04", f"runtime_export_manifest.json contains unknown artifact slot: {slot}")

    runtime_manifest_value = export_packet.get("runtime_log_manifest")
    if not isinstance(runtime_manifest_value, str) or not runtime_manifest_value:
        add_error(errors, "R-EXPORT-RUNTIME-01", "runtime_export_manifest.json must contain runtime_log_manifest")
        runtime_manifest_path = run_dir / "runtime_log_manifest.json"
    else:
        runtime_manifest_path = run_relative_path(run_dir, runtime_manifest_value)
    runtime_packet = load_json(runtime_manifest_path, errors, "R-EXPORT-RUNTIME-JSON-01")
    if runtime_packet is not None:
        expected_runtime_hash = export_packet.get("runtime_log_report_sha256")
        if expected_runtime_hash != file_sha256(runtime_manifest_path):
            add_error(errors, "R-EXPORT-RUNTIME-02", "runtime_log_report_sha256 does not match runtime_log_manifest.json")
        if runtime_packet.get("runtime_log_profile") != expected_runtime_log_profile:
            add_error(errors, "R-EXPORT-RUNTIME-03", "runtime_log_manifest profile does not match runtime_export_manifest.json")
        runtime_tracking = runtime_packet.get("tracking")
        export_tracking = export_packet.get("tracking")
        if isinstance(runtime_tracking, dict) and isinstance(export_tracking, dict):
            for field in ("tracking_source_profile", "tracking_csv", "tracking_alignment_report", "aligned_rows"):
                if runtime_tracking.get(field) != export_tracking.get(field):
                    add_error(errors, "R-EXPORT-RUNTIME-04", f"runtime export tracking field does not match runtime log: {field}")

    runtime_artifacts = runtime_packet.get("artifacts", []) if isinstance(runtime_packet, dict) else []
    runtime_artifacts_by_slot = {item.get("slot"): item for item in runtime_artifacts if isinstance(item, dict)}
    for slot in required_slots:
        item = artifacts_by_slot.get(slot)
        if item is None:
            add_error(errors, "R-EXPORT-ARTIFACT-05", f"required runtime export source artifact is missing: {slot}")
            continue
        spec = exported_specs.get(slot, {})
        for field in ("source", "destination", "bytes", "sha256"):
            if field not in item:
                add_error(errors, "R-EXPORT-ARTIFACT-06", f"runtime export source artifact {slot} missing {field}")
        destination = item.get("destination")
        expected_destination = spec.get("destination")
        if expected_destination and destination != expected_destination:
            add_error(errors, "R-EXPORT-ARTIFACT-07", f"runtime export artifact {slot} destination does not match RuntimeExportProfile")

        source_value = item.get("source")
        if isinstance(source_value, str) and source_value:
            source_path = Path(source_value)
            if not source_path.is_file():
                add_error(errors, "R-EXPORT-ARTIFACT-08", f"runtime export source file is missing: {source_value}")
            else:
                if item.get("bytes") != source_path.stat().st_size:
                    add_error(errors, "R-EXPORT-ARTIFACT-09", f"runtime export source artifact {slot} byte count mismatch")
                if item.get("sha256") != file_sha256(source_path):
                    add_error(errors, "R-EXPORT-ARTIFACT-10", f"runtime export source artifact {slot} sha256 mismatch")

        if isinstance(destination, str) and destination:
            destination_path = run_relative_path(run_dir, destination)
            if not destination_path.is_file():
                add_error(errors, "R-EXPORT-ARTIFACT-11", f"runtime export destination artifact is missing: {destination}")
            else:
                if item.get("bytes") != destination_path.stat().st_size:
                    add_error(errors, "R-EXPORT-ARTIFACT-12", f"runtime export destination artifact {slot} byte count mismatch")
                if item.get("sha256") != file_sha256(destination_path):
                    add_error(errors, "R-EXPORT-ARTIFACT-13", f"runtime export destination artifact {slot} sha256 mismatch")

        runtime_item = runtime_artifacts_by_slot.get(slot)
        if isinstance(runtime_item, dict):
            runtime_destination = runtime_item.get("destination")
            if isinstance(runtime_destination, str) and isinstance(destination, str):
                if run_relative_path(run_dir, runtime_destination).resolve() != run_relative_path(run_dir, destination).resolve():
                    add_error(errors, "R-EXPORT-ARTIFACT-14", f"runtime export destination for {slot} does not match runtime_log_manifest.json")

    review_requirements = profile.get("review_requirements", [])
    if review_requirements and export_packet.get("review_requirements") != review_requirements:
        add_error(errors, "R-EXPORT-REVIEW-01", "runtime_export_manifest.json review_requirements does not match RuntimeExportProfile")
    required_topics = profile.get("required_topics", [])
    if required_topics and export_packet.get("required_topics") != required_topics:
        add_error(errors, "R-EXPORT-TOPIC-01", "runtime_export_manifest.json required_topics does not match RuntimeExportProfile")


def check_launch_plan_hash(run_dir: Path, manifest: dict[str, Any], errors: list[dict[str, str]]) -> None:
    launch_plan_path = evidence_path(run_dir, manifest, "launch_plan", "LaunchPlan.json")
    launch_plan = load_json(launch_plan_path, errors, "R-LAUNCH-01")
    if launch_plan is None:
        return
    payload = launch_plan.get("launch_plan", launch_plan)
    if payload.get("run_id") != manifest.get("run_id"):
        add_error(errors, "R-RUNID-03", "LaunchPlan.json run_id does not match RUN_MANIFEST.json")
    expected = manifest.get("launch_plan_hash")
    actual = canonical_hash(payload)
    if expected and actual != expected:
        add_error(errors, "R-HASH-01", f"LaunchPlan hash mismatch: expected {expected}, actual {actual}")


def check_tracking_csv(path: Path, errors: list[dict[str, str]]) -> int:
    if not path.is_file():
        add_error(errors, "R-TRACK-01", f"tracking log is missing: {path}")
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(TRACKING_COLUMNS - columns)
        if missing:
            add_error(errors, "R-TRACK-02", "tracking log is missing columns: " + ", ".join(missing))
            return 0
        row_count = sum(1 for _ in reader)
    if row_count <= 0:
        add_error(errors, "R-TRACK-03", "tracking log has no rows")
    return row_count


def check_metrics(
    metrics_path: Path,
    manifest: dict[str, Any],
    metrics_schema: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    metrics_packet = load_json(metrics_path, errors, "R-METRIC-JSON-01")
    if metrics_packet is None:
        return
    if metrics_packet.get("run_id") != manifest.get("run_id"):
        add_error(errors, "R-METRIC-01", "metrics.json run_id does not match RUN_MANIFEST.json")
    metric_values = metrics_packet.get("metrics")
    if not isinstance(metric_values, dict):
        add_error(errors, "R-METRIC-02", "metrics.json must contain a metrics object")
        return

    definitions = metrics_schema.get("metric_definitions", {})
    required_metrics = manifest.get("evaluation", {}).get("required_metrics", [])
    for metric_name in required_metrics:
        if metric_name not in metric_values:
            add_error(errors, "R-METRIC-03", f"required metric is missing from metrics.json: {metric_name}")

    for metric_name, metric_body in metric_values.items():
        definition = definitions.get(metric_name)
        if definition is None:
            add_error(errors, "R-METRIC-04", f"metric is not defined in metrics schema: {metric_name}")
            continue
        if not isinstance(metric_body, dict) or "value" not in metric_body or "unit" not in metric_body:
            add_error(errors, "R-METRIC-05", f"metric must contain value and unit: {metric_name}")
            continue
        expected_unit = str(definition.get("unit", ""))
        actual_unit = str(metric_body.get("unit", ""))
        allowed_units = {part.strip() for part in expected_unit.split("or")}
        if actual_unit not in allowed_units:
            add_error(errors, "R-METRIC-06", f"metric {metric_name} unit {actual_unit} does not match schema unit {expected_unit}")


def check_threshold_report(run_dir: Path, manifest: dict[str, Any], errors: list[dict[str, str]]) -> bool | None:
    threshold_path = evidence_path(run_dir, manifest, "threshold_report", "threshold_report.json")
    threshold_packet = load_json(threshold_path, errors, "R-THRESHOLD-JSON-01")
    if threshold_packet is None:
        return None
    if threshold_packet.get("run_id") != manifest.get("run_id"):
        add_error(errors, "R-THRESHOLD-01", "threshold_report.json run_id does not match RUN_MANIFEST.json")
    if "accepted" not in threshold_packet:
        add_error(errors, "R-THRESHOLD-02", "threshold_report.json must contain accepted field")
        return None
    if not isinstance(threshold_packet.get("accepted"), bool):
        add_error(errors, "R-THRESHOLD-03", "threshold_report.json accepted field must be boolean")
        return None
    return bool(threshold_packet.get("accepted"))


def check_review(run_dir: Path, manifest: dict[str, Any], errors: list[dict[str, str]]) -> None:
    review_path = evidence_path(run_dir, manifest, "review", "review.md")
    if not review_path.is_file():
        add_error(errors, "R-REVIEW-01", f"review file is missing: {review_path}")
        return
    if review_path.name.endswith(".template.md"):
        add_error(errors, "R-REVIEW-03", f"review file is still a template: {review_path}")
        return
    text = review_path.read_text(encoding="utf-8")
    if not text.strip():
        add_error(errors, "R-REVIEW-02", "review file is empty")
    lowered = text.lower()
    for claim in manifest.get("forbidden_claims", []):
        if str(claim).lower() in lowered:
            add_error(errors, "R-CLAIM-01", f"review contains forbidden claim: {claim}")


def check_directory_artifact(run_dir: Path, manifest: dict[str, Any], key: str, default: str, errors: list[dict[str, str]]) -> None:
    path = evidence_path(run_dir, manifest, key, default)
    if not path.is_dir():
        add_error(errors, "R-DIR-01", f"{key} directory is missing: {path}")
        return
    usable_files = [
        child
        for child in path.iterdir()
        if child.is_file() and child.name not in IGNORED_DIRECTORY_FILES and child.stat().st_size > 0
    ]
    if not usable_files:
        add_error(errors, "R-DIR-02", f"{key} directory is empty: {path}")


def check_source_state(run_dir: Path, manifest: dict[str, Any], errors: list[dict[str, str]]) -> None:
    source_state = manifest.get("source_state")
    if not isinstance(source_state, dict):
        add_error(errors, "R-SOURCE-01", "RUN_MANIFEST.json must contain source_state object")
        return

    for field in ("git_commit", "git_dirty", "source_hashes", "source_hashes_sha256", "source_hashes_aggregate_sha256"):
        if field not in source_state:
            add_error(errors, "R-SOURCE-02", f"source_state missing field: {field}")

    source_hashes_value = source_state.get("source_hashes")
    if not isinstance(source_hashes_value, str):
        add_error(errors, "R-SOURCE-03", "source_state.source_hashes must be a path")
        return
    source_hashes_path = Path(source_hashes_value)
    if not source_hashes_path.is_absolute():
        source_hashes_path = ROOT / source_hashes_path
    source_packet = load_json(source_hashes_path, errors, "R-SOURCE-JSON-01")
    if source_packet is None:
        return

    expected_packet_hash = source_state.get("source_hashes_sha256")
    actual_packet_hash = canonical_hash(source_packet)
    if expected_packet_hash != actual_packet_hash:
        add_error(errors, "R-SOURCE-04", "source_hashes_sha256 does not match source_hashes.json")

    expected_aggregate = source_state.get("source_hashes_aggregate_sha256")
    actual_aggregate = source_packet.get("aggregate_sha256")
    if expected_aggregate != actual_aggregate:
        add_error(errors, "R-SOURCE-05", "source_hashes aggregate hash does not match RUN_MANIFEST.json")

    sources = source_packet.get("sources")
    if not isinstance(sources, list) or not sources:
        add_error(errors, "R-SOURCE-06", "source_hashes.json must contain nonempty sources list")


def validate_run(
    run_dir: Path,
    metrics_schema_path: Path,
    runtime_log_profiles_path: Path,
    profile_catalog_path: Path = DEFAULT_PROFILE_CATALOG,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    manifest_path = run_dir / "RUN_MANIFEST.json"
    manifest_packet = load_json(manifest_path, errors, "R-MANIFEST-01")
    metrics_schema = load_json(metrics_schema_path, errors, "R-SCHEMA-01")
    if manifest_packet is None or metrics_schema is None:
        return {"ok": False, "run_dir": str(run_dir), "errors": errors, "warnings": []}

    manifest = manifest_packet.get("run_manifest")
    if not isinstance(manifest, dict):
        add_error(errors, "R-MANIFEST-02", "RUN_MANIFEST.json must contain run_manifest object")
        return {"ok": False, "run_dir": str(run_dir), "errors": errors, "warnings": []}

    check_manifest_placeholders(manifest, errors)
    check_run_id_consistency(run_dir, manifest, errors)
    check_source_state(run_dir, manifest, errors)
    check_required_artifacts(run_dir, manifest, errors)
    check_launch_plan_hash(run_dir, manifest, errors)
    tracking_path = evidence_path(run_dir, manifest, "tracking_log", "tracking.csv")
    row_count = check_tracking_csv(tracking_path, errors)
    check_runtime_log_manifest(run_dir, manifest, row_count, runtime_log_profiles_path, errors)
    check_runtime_export_manifest(run_dir, manifest, profile_catalog_path, errors)
    metrics_path = evidence_path(run_dir, manifest, "metrics", "metrics.json")
    check_metrics(metrics_path, manifest, metrics_schema, errors)
    threshold_accepted = check_threshold_report(run_dir, manifest, errors)
    check_review(run_dir, manifest, errors)
    check_directory_artifact(run_dir, manifest, "screenshots", "screenshots/", errors)
    check_directory_artifact(run_dir, manifest, "logs", "logs/", errors)

    return {
        "ok": not errors,
        "run_dir": str(run_dir),
        "run_id": manifest.get("run_id"),
        "experiment_profile_id": manifest.get("experiment_profile_id"),
        "tracking_rows": row_count,
        "threshold_accepted": threshold_accepted,
        "errors": errors,
        "warnings": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="Results/runs/<run_id> directory")
    parser.add_argument("--metrics-schema", default=str(DEFAULT_METRICS_SCHEMA), help="Metric schema JSON path")
    parser.add_argument(
        "--runtime-log-profiles",
        default=str(DEFAULT_RUNTIME_LOG_EXPORTS),
        help="RuntimeLogProfile registry JSON path",
    )
    parser.add_argument("--catalog", default=str(DEFAULT_PROFILE_CATALOG), help="Profile catalog JSON path")
    parser.add_argument("--report", help="Optional JSON report output path")
    args = parser.parse_args(argv)

    report = validate_run(Path(args.run_dir), Path(args.metrics_schema), Path(args.runtime_log_profiles), Path(args.catalog))
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
