"""Versioned RunManifest helpers for Config/Results consumers.

The project has several historical manifest shapes. This module keeps those
files readable while defining the small, forward-facing ``v2`` record used by
new operator runs. It intentionally does not start a runtime, discover
artifacts by guesswork, or promote an artifact into evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import json
import re
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any


RUN_MANIFEST_V2_SCHEMA = "mosim.run_manifest.v2"
RUN_INDEX_V1_SCHEMA = "mosim.run_index.v1"
OPERATOR_RUN_MANIFEST_V1_SCHEMA = "mosim.operator_run_manifest.v1"
LEGACY_RUN_MANIFEST_V1_SCHEMA = "mosim.run_manifest.v1"

ARTIFACT_SLOTS = (
    "mworks_model",
    "native_result_msr",
    "raw_csv",
    "metrics_json",
    "rosbag",
    "px4_ulog",
    "operator_map_replay",
    "telemetry",
    "logs_directory",
)
OPEN_ACTION_SLOTS = (
    "open_model",
    "open_native_result",
    "replay_rviz",
    "replay_operator_map",
    "open_result_directory",
)
ARTIFACT_STATUSES = {"not_requested", "pending", "declared", "available", "missing", "not_applicable"}
RUN_STATUSES = {"prepared", "running", "replaying", "completed", "failed", "cancelled", "archived"}
MAP_SCENARIO_STATUSES = {"frozen", "pending", "not_applicable"}
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def _is_object(value: Any) -> bool:
    return isinstance(value, dict)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_PATTERN.fullmatch(value))


def _is_relative_path(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if not value:
        return True
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        return False
    return ".." not in posix.parts and ".." not in windows.parts


def _is_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        # Ubuntu 20.04 ships Python 3.8, which lacks the later suffix helper.
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _string_or_empty(value: Any) -> bool:
    return isinstance(value, str)


def run_manifest_v2_issues(manifest: Mapping[str, Any]) -> list[str]:
    """Return deterministic, human-readable v2 contract violations."""

    issues: list[str] = []
    if not _is_object(manifest):
        return ["manifest_object_required"]
    if manifest.get("schema") != RUN_MANIFEST_V2_SCHEMA:
        issues.append("schema_must_be_mosim.run_manifest.v2")
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_PATTERN.fullmatch(run_id):
        issues.append("run_id_invalid")
    if not _nonempty_string(manifest.get("run_kind")):
        issues.append("run_kind_required")
    if not _is_utc_timestamp(manifest.get("created_at")):
        issues.append("created_at_must_be_utc_rfc3339")
    if manifest.get("status") not in RUN_STATUSES:
        issues.append("status_invalid")
    vehicle_count = manifest.get("vehicle_count")
    if not isinstance(vehicle_count, int) or isinstance(vehicle_count, bool) or not 1 <= vehicle_count <= 9:
        issues.append("vehicle_count_invalid")
    if not _nonempty_string(manifest.get("claim_boundary")):
        issues.append("claim_boundary_required")

    profile = manifest.get("profile")
    if not _is_object(profile):
        issues.append("profile_object_required")
    else:
        if not _nonempty_string(profile.get("id")):
            issues.append("profile.id_required")
        if not _is_sha256(profile.get("sha256")):
            issues.append("profile.sha256_invalid")
        for key in ("controller_id", "controller_profile", "runtime_profile_id"):
            if key in profile and not _string_or_empty(profile[key]):
                issues.append(f"profile.{key}_must_be_string")

    for section_name in ("map", "scenario"):
        section = manifest.get(section_name)
        if not _is_object(section):
            issues.append(f"{section_name}_object_required")
            continue
        if section.get("status") not in MAP_SCENARIO_STATUSES:
            issues.append(f"{section_name}.status_invalid")
        for key in ("id", "path"):
            if key in section and not _string_or_empty(section[key]):
                issues.append(f"{section_name}.{key}_must_be_string")
        snapshot = section.get("snapshot")
        if not _is_object(snapshot):
            issues.append(f"{section_name}.snapshot_object_required")
        snapshot_hash = section.get("snapshot_sha256")
        if snapshot_hash and not _is_sha256(snapshot_hash):
            issues.append(f"{section_name}.snapshot_sha256_invalid")
        if section.get("status") == "frozen" and not _is_sha256(snapshot_hash):
            issues.append(f"{section_name}.snapshot_sha256_required_when_frozen")

    if not _is_object(manifest.get("source_state")):
        issues.append("source_state_object_required")

    artifacts = manifest.get("artifacts")
    if not _is_object(artifacts):
        issues.append("artifacts_object_required")
    else:
        for slot in ARTIFACT_SLOTS:
            artifact = artifacts.get(slot)
            if not _is_object(artifact):
                issues.append(f"artifacts.{slot}_object_required")
                continue
            if artifact.get("status") not in ARTIFACT_STATUSES:
                issues.append(f"artifacts.{slot}.status_invalid")
            if "path" in artifact and not _is_relative_path(artifact["path"]):
                issues.append(f"artifacts.{slot}.path_invalid")
            if artifact.get("sha256") and not _is_sha256(artifact["sha256"]):
                issues.append(f"artifacts.{slot}.sha256_invalid")

    open_actions = manifest.get("open_actions")
    if not _is_object(open_actions):
        issues.append("open_actions_object_required")
    else:
        for action in OPEN_ACTION_SLOTS:
            metadata = open_actions.get(action)
            if not _is_object(metadata):
                issues.append(f"open_actions.{action}_object_required")
                continue
            if not isinstance(metadata.get("enabled"), bool):
                issues.append(f"open_actions.{action}.enabled_required")
            if not _nonempty_string(metadata.get("reason_code")):
                issues.append(f"open_actions.{action}.reason_code_required")
            if "path" in metadata and not _is_relative_path(metadata["path"]):
                issues.append(f"open_actions.{action}.path_invalid")

    if manifest.get("run_kind") == "operator_runtime":
        _operator_v2_issues(manifest, issues)
    return issues


def _operator_v2_issues(manifest: Mapping[str, Any], issues: list[str]) -> None:
    """Keep operator v2 manifests consumable by the existing QGC/replay path."""

    profile = manifest.get("profile")
    map_section = manifest.get("map")
    required_strings = (
        "experiment_profile_id",
        "experiment_profile_hash",
        "runtime_profile_id",
        "controller_backend",
        "controller_id",
        "state",
        "operator_map_snapshot_hash",
    )
    for key in required_strings:
        if not _nonempty_string(manifest.get(key)):
            issues.append(f"operator.{key}_required")
    if not _is_object(manifest.get("operator_map_snapshot")):
        issues.append("operator.operator_map_snapshot_object_required")
    if not _is_object(manifest.get("scenario_snapshot")):
        issues.append("operator.scenario_snapshot_object_required")
    if _is_object(profile):
        if manifest.get("experiment_profile_id") != profile.get("id"):
            issues.append("operator.experiment_profile_id_mismatch")
        if manifest.get("experiment_profile_hash") != profile.get("sha256"):
            issues.append("operator.experiment_profile_hash_mismatch")
        if manifest.get("runtime_profile_id") != profile.get("runtime_profile_id"):
            issues.append("operator.runtime_profile_id_mismatch")
    if _is_object(map_section):
        if manifest.get("operator_map_snapshot") != map_section.get("snapshot"):
            issues.append("operator.operator_map_snapshot_mismatch")
        if manifest.get("operator_map_snapshot_hash") != map_section.get("snapshot_sha256"):
            issues.append("operator.operator_map_snapshot_hash_mismatch")


def validate_run_manifest_v2(manifest: Mapping[str, Any]) -> None:
    """Raise one stable error string when a v2 manifest violates its contract."""

    issues = run_manifest_v2_issues(manifest)
    if issues:
        raise ValueError("run_manifest_v2_invalid:" + ",".join(issues))


def artifact_slot(*, status: str, path: str = "", sha256: str = "") -> dict[str, str]:
    """Build one v2 artifact slot without claiming availability."""

    value: dict[str, str] = {"status": status}
    if path:
        value["path"] = path
    if sha256:
        value["sha256"] = sha256
    return value


def open_action(*, enabled: bool, reason_code: str, path: str = "") -> dict[str, Any]:
    """Build metadata for a future UI action without executing it."""

    value: dict[str, Any] = {"enabled": enabled, "reason_code": reason_code}
    if path:
        value["path"] = path
    return value


def normalize_run_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize v2 and supported historical shapes for the derived run index.

    The return value is descriptive rather than an inferred runtime verdict.
    Missing artifacts remain ``not_requested``; this reader never searches for
    substitute files.
    """

    if not _is_object(manifest):
        raise ValueError("run_manifest_object_required")
    if manifest.get("schema") == RUN_MANIFEST_V2_SCHEMA:
        validate_run_manifest_v2(manifest)
        return _normalize_v2(manifest)
    if manifest.get("schema") == OPERATOR_RUN_MANIFEST_V1_SCHEMA:
        return _normalize_operator_v1(manifest)
    wrapped = manifest.get("run_manifest")
    if _is_object(wrapped):
        return _normalize_wrapped_legacy(wrapped)
    if manifest.get("schema_version") == LEGACY_RUN_MANIFEST_V1_SCHEMA:
        return _normalize_legacy_p0(manifest)
    raise ValueError("run_manifest_schema_unsupported")


def _empty_artifacts() -> dict[str, dict[str, str]]:
    return {slot: artifact_slot(status="not_requested") for slot in ARTIFACT_SLOTS}


def _declared_artifact(path: Any) -> dict[str, str]:
    return artifact_slot(status="declared" if _nonempty_string(path) else "not_requested", path=str(path or ""))


def _record(
    *,
    manifest_format: str,
    run_id: Any,
    run_kind: str,
    status: str,
    created_at: Any,
    profile_id: Any,
    profile_hash: Any,
    vehicle_count: Any,
    map_id: Any,
    controller_id: Any,
    planner_id: Any,
    artifacts: dict[str, dict[str, str]],
    claim_boundary: Any,
) -> dict[str, Any]:
    if not _nonempty_string(run_id):
        raise ValueError("run_manifest_run_id_missing")
    return {
        "run_id": str(run_id),
        "manifest_format": manifest_format,
        "run_kind": run_kind,
        "status": status,
        "created_at": str(created_at or ""),
        "profile_id": str(profile_id or ""),
        "profile_hash": str(profile_hash or ""),
        "vehicle_count": vehicle_count if isinstance(vehicle_count, int) and not isinstance(vehicle_count, bool) else None,
        "map_id": str(map_id or ""),
        "controller_id": str(controller_id or ""),
        "planner_id": str(planner_id or ""),
        "artifacts": artifacts,
        "claim_boundary": str(claim_boundary or "Historical manifest normalized for discovery only."),
    }


def _normalize_v2(manifest: Mapping[str, Any]) -> dict[str, Any]:
    profile = manifest["profile"]
    map_section = manifest["map"]
    scenario = manifest["scenario"]
    artifacts = manifest["artifacts"]
    assert isinstance(profile, dict)
    assert isinstance(map_section, dict)
    assert isinstance(scenario, dict)
    assert isinstance(artifacts, dict)
    return _record(
        manifest_format=RUN_MANIFEST_V2_SCHEMA,
        run_id=manifest["run_id"],
        run_kind=str(manifest["run_kind"]),
        status=str(manifest["status"]),
        created_at=manifest["created_at"],
        profile_id=profile["id"],
        profile_hash=profile["sha256"],
        vehicle_count=manifest["vehicle_count"],
        map_id=map_section.get("id", ""),
        controller_id=profile.get("controller_id", manifest.get("controller_id", "")),
        planner_id=manifest.get("planner_profile", scenario.get("id", "")),
        artifacts={slot: dict(artifacts[slot]) for slot in ARTIFACT_SLOTS},
        claim_boundary=manifest["claim_boundary"],
    )


def _normalize_operator_v1(manifest: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = _empty_artifacts()
    artifacts["operator_map_replay"] = _declared_artifact("OPERATOR_MAP_REPLAY_MANIFEST.json")
    artifacts["telemetry"] = _declared_artifact("telemetry.json")
    artifacts["logs_directory"] = _declared_artifact("logs")
    snapshot = manifest.get("operator_map_snapshot")
    map_id = snapshot.get("map_id", "") if _is_object(snapshot) else ""
    return _record(
        manifest_format=OPERATOR_RUN_MANIFEST_V1_SCHEMA,
        run_id=manifest.get("run_id"),
        run_kind="operator_runtime",
        status=str(manifest.get("state", "historical_unknown")),
        created_at=manifest.get("prepared_at_unix_s", ""),
        profile_id=manifest.get("experiment_profile_id", ""),
        profile_hash=manifest.get("experiment_profile_hash", ""),
        vehicle_count=manifest.get("vehicle_count"),
        map_id=map_id,
        controller_id=manifest.get("controller_id", ""),
        planner_id=manifest.get("planner_profile", ""),
        artifacts=artifacts,
        claim_boundary=manifest.get("claim_boundary", ""),
    )


def _normalize_wrapped_legacy(payload: Mapping[str, Any]) -> dict[str, Any]:
    evidence = payload.get("evidence") if _is_object(payload.get("evidence")) else {}
    controller = payload.get("controller") if _is_object(payload.get("controller")) else {}
    trajectory = payload.get("trajectory_contract") if _is_object(payload.get("trajectory_contract")) else {}
    assert isinstance(evidence, dict)
    assert isinstance(controller, dict)
    assert isinstance(trajectory, dict)
    artifacts = _empty_artifacts()
    artifacts["metrics_json"] = _declared_artifact(evidence.get("metrics", ""))
    artifacts["raw_csv"] = _declared_artifact(evidence.get("tracking_log", ""))
    artifacts["logs_directory"] = _declared_artifact(evidence.get("logs", ""))
    return _record(
        manifest_format="legacy_wrapped_run_manifest",
        run_id=payload.get("run_id"),
        run_kind="historical_runtime",
        status="historical_unknown",
        created_at="",
        profile_id=payload.get("experiment_profile_id", ""),
        profile_hash=payload.get("experiment_profile_hash", ""),
        vehicle_count=payload.get("vehicle_count"),
        map_id=payload.get("map_id", ""),
        controller_id=controller.get("controller_id", ""),
        planner_id=trajectory.get("trajectory_profile", ""),
        artifacts=artifacts,
        claim_boundary="Historical wrapped manifest normalized for discovery only; it is not revalidated or upgraded.",
    )


def _normalize_legacy_p0(manifest: Mapping[str, Any]) -> dict[str, Any]:
    mworks = manifest.get("mworks") if _is_object(manifest.get("mworks")) else {}
    assert isinstance(mworks, dict)
    artifacts = _empty_artifacts()
    artifacts["raw_csv"] = _declared_artifact(mworks.get("raw_csv", ""))
    artifacts["metrics_json"] = _declared_artifact(mworks.get("metrics_json", ""))
    return _record(
        manifest_format=LEGACY_RUN_MANIFEST_V1_SCHEMA,
        run_id=manifest.get("run_id"),
        run_kind="historical_p0",
        status=str(manifest.get("quality_status", "historical_unknown")),
        created_at="",
        profile_id=manifest.get("experiment_profile_id", ""),
        profile_hash=manifest.get("experiment_profile_hash", ""),
        vehicle_count=manifest.get("vehicle_count"),
        map_id=manifest.get("map_id", ""),
        controller_id=manifest.get("controller_id", ""),
        planner_id=manifest.get("planner_id", ""),
        artifacts=artifacts,
        claim_boundary="Historical P0 manifest normalized for discovery only; its original checker remains authoritative.",
    )


def canonical_json(value: Any) -> str:
    """Expose a stable serializer for narrow contract tests and tooling."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
