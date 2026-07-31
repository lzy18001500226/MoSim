from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from src.orchestration.run_manifest_contract import (
    ARTIFACT_SLOTS,
    RUN_MANIFEST_V2_SCHEMA,
    artifact_slot,
    normalize_run_manifest,
    open_action,
    validate_run_manifest_v2,
)


def test_timestamp_validator_stays_compatible_with_ros1_python38_runtime() -> None:
    source = Path("src/orchestration/run_manifest_contract.py").read_text(encoding="utf-8")

    assert ".removesuffix(" not in source


ROOT = Path(__file__).resolve().parents[2]
INDEX_SCRIPT = ROOT / "Scripts" / "results" / "build_run_index.py"
SCHEMA_PATH = ROOT / "Config" / "schemas" / "mosim_run_manifest_v2.schema.json"


def _index_module():
    spec = importlib.util.spec_from_file_location("build_run_index", INDEX_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _v2_manifest(run_id: str = "run-v2-fixture") -> dict[str, object]:
    return {
        "schema": RUN_MANIFEST_V2_SCHEMA,
        "run_id": run_id,
        "run_kind": "offline_mworks",
        "created_at": "2026-07-28T01:02:03Z",
        "status": "completed",
        "profile": {
            "id": "offline_official_pid_climb_v1",
            "sha256": "a" * 64,
            "controller_id": "official_pid",
            "controller_profile": "official_pid_attitude_thrust_v1",
            "runtime_profile_id": "offline_mworks_v1",
        },
        "map": {"status": "not_applicable", "id": "", "snapshot": {}, "snapshot_sha256": ""},
        "scenario": {
            "status": "frozen",
            "id": "climb",
            "path": "Config/scenarios/climb.json",
            "snapshot": {"kind": "climb"},
            "snapshot_sha256": "b" * 64,
        },
        "vehicle_count": 1,
        "source_state": {"model_root": "Models/MoSimQuadrotorModel/package.mo"},
        "artifacts": {
            "mworks_model": artifact_slot(status="available", path="GeneratedProfile.mo"),
            "native_result_msr": artifact_slot(status="available", path="native_result/Model/Result.msr"),
            "raw_csv": artifact_slot(status="available", path="raw/result.csv"),
            "metrics_json": artifact_slot(status="available", path="metrics/metrics.json"),
            "rosbag": artifact_slot(status="not_applicable"),
            "px4_ulog": artifact_slot(status="not_applicable"),
            "operator_map_replay": artifact_slot(status="not_applicable"),
            "telemetry": artifact_slot(status="not_applicable"),
            "logs_directory": artifact_slot(status="available", path="logs"),
        },
        "open_actions": {
            "open_model": open_action(enabled=True, reason_code="model_available", path="GeneratedProfile.mo"),
            "open_native_result": open_action(
                enabled=True,
                reason_code="native_result_available",
                path="native_result/Model/Result.msr",
            ),
            "replay_rviz": open_action(enabled=False, reason_code="rosbag_not_applicable"),
            "replay_operator_map": open_action(enabled=False, reason_code="rosbag_not_applicable"),
            "open_result_directory": open_action(enabled=True, reason_code="run_directory_available", path="."),
        },
        "claim_boundary": "Fixture only; declared artifacts are not independently accepted.",
    }


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_v2_contract_accepts_declared_artifact_slots_and_normalizes_for_discovery() -> None:
    manifest = _v2_manifest()
    validate_run_manifest_v2(manifest)
    normalized = normalize_run_manifest(manifest)

    assert normalized["manifest_format"] == RUN_MANIFEST_V2_SCHEMA
    assert normalized["run_id"] == "run-v2-fixture"
    assert set(normalized["artifacts"]) == set(ARTIFACT_SLOTS)
    assert normalized["artifacts"]["native_result_msr"]["path"].endswith("Result.msr")


def test_v2_contract_rejects_parent_traversal_and_missing_frozen_hash() -> None:
    manifest = _v2_manifest()
    artifacts = manifest["artifacts"]
    scenario = manifest["scenario"]
    assert isinstance(artifacts, dict) and isinstance(scenario, dict)
    artifacts["raw_csv"] = artifact_slot(status="available", path="../outside.csv")
    scenario["snapshot_sha256"] = ""

    with pytest.raises(ValueError) as error:
        validate_run_manifest_v2(manifest)

    assert "artifacts.raw_csv.path_invalid" in str(error.value)
    assert "scenario.snapshot_sha256_required_when_frozen" in str(error.value)


def test_legacy_wrapped_manifest_remains_readable_without_rewrite() -> None:
    legacy = {
        "run_manifest": {
            "run_id": "g10c_legacy_fixture",
            "experiment_profile_id": "g10c_profile",
            "experiment_profile_hash": "c" * 64,
            "controller": {"controller_id": "official_pid"},
            "trajectory_contract": {"trajectory_profile": "figure8_v1"},
            "evidence": {"metrics": "metrics.json", "tracking_log": "tracking.csv", "logs": "logs"},
        }
    }

    normalized = normalize_run_manifest(legacy)

    assert normalized["manifest_format"] == "legacy_wrapped_run_manifest"
    assert normalized["status"] == "historical_unknown"
    assert normalized["artifacts"]["metrics_json"]["path"] == "metrics.json"


def test_v2_schema_is_valid_json_and_names_the_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == RUN_MANIFEST_V2_SCHEMA
    assert "artifacts" in schema["required"]
    assert "native_result_msr" in schema["properties"]["artifacts"]["required"]


def test_index_builder_scans_only_run_manifests_and_reports_invalid_entries(tmp_path: Path) -> None:
    module = _index_module()
    runs_root = tmp_path / "Results" / "runs"
    _write_manifest(runs_root / "valid" / "RUN_MANIFEST.json", _v2_manifest("run-index-valid"))
    _write_manifest(runs_root / "invalid" / "RUN_MANIFEST.json", {})
    ignored = tmp_path / "Results" / "mworks_generated_profiles" / "ignored" / "RUN_MANIFEST.json"
    ignored.parent.mkdir(parents=True)
    ignored.write_text("{}", encoding="utf-8")

    index = module.build_run_index(
        runs_root=runs_root,
        project_root=tmp_path,
        generated_at="2026-07-28T01:02:03Z",
    )

    assert index["run_count"] == 1
    assert index["status"] == "partial"
    assert index["runs"][0]["run_id"] == "run-index-valid"
    assert index["issues"][0]["path"] == "Results/runs/invalid/RUN_MANIFEST.json"


def test_index_builder_detects_duplicate_run_ids_without_editing_bundles(tmp_path: Path) -> None:
    module = _index_module()
    runs_root = tmp_path / "Results" / "runs"
    _write_manifest(runs_root / "one" / "RUN_MANIFEST.json", _v2_manifest("run-index-duplicate"))
    _write_manifest(runs_root / "two" / "RUN_MANIFEST.json", _v2_manifest("run-index-duplicate"))

    index = module.build_run_index(runs_root=runs_root, project_root=tmp_path)

    assert index["run_count"] == 1
    assert index["status"] == "partial"
    assert "duplicate_run_id" in index["issues"][0]["reason_code"]
    assert (runs_root / "two" / "RUN_MANIFEST.json").is_file()
