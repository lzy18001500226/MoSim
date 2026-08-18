from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from Scripts.ui.runtime_sidecar import resolve_runtime_operator_map
from src.orchestration.run_manifest_contract import RUN_MANIFEST_V2_SCHEMA, validate_run_manifest_v2


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "ui" / "prepare_operator_run.py"


def _module():
    spec = importlib.util.spec_from_file_location("prepare_operator_run", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_prepare_operator_run_uses_python38_compatible_atomic_json_write() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert '.open("w", encoding="utf-8", newline="\\n")' in source
    assert "temporary.write_text(" not in source


def _fixture_root(tmp_path: Path) -> Path:
    _write_json(
        tmp_path / "Config/profiles/operator_profiles.json",
        {
            "profiles": [
                {
                    "profile_id": "factory_demo_v1",
                    "profile_path": "Config/profiles/experiments/factory_demo_v1.json",
                    "enabled": True,
                    "operator_mode": "mission_adapter",
                }
            ]
        },
    )
    _write_json(
        tmp_path / "Config/profiles/experiments/factory_demo_v1.json",
        {
            "experiment_profile": {
                "id": "factory_demo_v1",
                "vehicle_count": 3,
                "operator_map_id": "factory_l2",
                "controller_profile": "px4ctrl_attitude_thrust_v1",
                "controller_backend": "fixture_controller_backend_v1",
                "planner_profile": "swarm_formation",
                "safety_profile": "basic_limiter_v1",
                "fault_profile": "none",
                "scenario_path": "Config/scenarios/factory_demo.json",
            }
        },
    )
    _write_json(tmp_path / "Config/scenarios/factory_demo.json", {"formation": {"type": "leader_follower"}})
    source_catalog = json.loads(
        (ROOT / "Config/control_platform/operator_map_catalog.json").read_text(encoding="utf-8")
    )
    factory_map = source_catalog["maps"][0]
    _write_json(
        tmp_path / "Config/control_platform/operator_map_catalog.json",
        {"schema": source_catalog["schema"], "maps": [factory_map]},
    )
    matrix_relative = Path(factory_map["image_coordinate_contract"]["matrix_path"])
    matrix_target = tmp_path / matrix_relative
    matrix_target.parent.mkdir(parents=True, exist_ok=True)
    matrix_target.write_bytes((ROOT / matrix_relative).read_bytes())
    _write_json(
        tmp_path / "Config/control_platform/runtime_backend_catalog.json",
        {
            "runtime_profiles": [
                {
                    "runtime_profile_id": "factory_demo_runtime_v1",
                    "operation_id": "factory_demo",
                    "experiment_profile_ids": ["factory_demo_v1"],
                    "controller_ids": ["px4ctrl"],
                    "operator_invocation": {"schema": "mosim.operator_invocation.v1"},
                }
            ]
        },
    )
    return tmp_path


def test_prepare_freezes_profile_map_and_pointer(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)

    result = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-test-run",
        now=123.0,
    )

    profile_path = root / "Config/profiles/experiments/factory_demo_v1.json"
    manifest = json.loads((result["run_directory"] / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    pointer = json.loads((root / "Results/ui_platform/qgc_active_run.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == "qgc-test-run"
    assert manifest["schema"] == RUN_MANIFEST_V2_SCHEMA
    assert manifest["run_kind"] == "operator_runtime"
    assert manifest["status"] == "prepared"
    validate_run_manifest_v2(manifest)
    assert manifest["experiment_profile_id"] == "factory_demo_v1"
    assert manifest["experiment_profile_hash"] == hashlib.sha256(profile_path.read_bytes()).hexdigest()
    assert manifest["controller_backend"] == "fixture_controller_backend_v1"
    assert manifest["vehicle_count"] == 3
    assert manifest["operator_map_snapshot"]["map_id"] == "factory_l2"
    assert manifest["scenario_snapshot"]["formation"]["type"] == "leader_follower"
    assert manifest["profile"]["id"] == manifest["experiment_profile_id"]
    assert manifest["map"]["snapshot"] == manifest["operator_map_snapshot"]
    assert manifest["artifacts"]["telemetry"]["path"] == "telemetry.json"
    resolved_snapshot, resolved_hash = resolve_runtime_operator_map(manifest)
    assert resolved_snapshot["map_id"] == "factory_l2"
    assert resolved_hash == manifest["operator_map_snapshot_hash"]
    assert pointer["state"] == "launch_prepared"
    assert pointer["run_directory"] == "Results/runs/qgc-test-run"


def test_prepare_records_the_independent_terminal_that_created_the_run(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)

    result = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-standalone-terminal-run",
        prepared_by="terminal_rviz_qgc_display_phase1",
        now=1.0,
    )

    manifest = json.loads((result["run_directory"] / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    pointer = json.loads((root / "Results/ui_platform/qgc_active_run.json").read_text(encoding="utf-8"))
    assert manifest["prepared_by"] == "terminal_rviz_qgc_display_phase1"
    assert manifest["source_state"]["prepared_by"] == "terminal_rviz_qgc_display_phase1"
    assert pointer["source"] == "terminal_rviz_qgc_display_phase1"


def test_prepare_rejects_an_unregistered_preparation_source(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)

    with pytest.raises(ValueError, match="operator_run_prepared_by_invalid"):
        module.prepare_run(
            root=root,
            profile_id="factory_demo_v1",
            runtime_profile_id="factory_demo_runtime_v1",
            run_id="qgc-invalid-source-run",
            prepared_by="unregistered_terminal",
        )


def test_prepare_refuses_to_replace_a_live_pointer_until_operator_clears_it(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)
    module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-first-run",
        now=1.0,
    )

    with pytest.raises(ValueError, match="operator_run_already_active"):
        module.prepare_run(
            root=root,
            profile_id="factory_demo_v1",
            runtime_profile_id="factory_demo_runtime_v1",
            run_id="qgc-second-run",
            now=2.0,
        )

    cleared = module.clear_active_run(root=root, now=3.0)
    assert cleared["state"] == "cleared"
    result = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-second-run",
        now=4.0,
    )
    assert result["run_id"] == "qgc-second-run"


def test_activate_only_advances_the_matching_prepared_run_after_launcher_readiness(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)
    prepared = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-activate-run",
        now=1.0,
    )

    activated = module.activate_active_run(
        root=root,
        expected_run_id="qgc-activate-run",
        source="test_runtime_ready",
        now=2.0,
    )

    pointer = json.loads((root / "Results/ui_platform/qgc_active_run.json").read_text(encoding="utf-8"))
    manifest = json.loads((prepared["run_directory"] / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert activated["state"] == "running"
    assert pointer["state"] == "running"
    assert pointer["activated_at_unix_s"] == 2.0
    assert pointer["source"] == "test_runtime_ready"
    assert manifest["state"] == "launch_prepared"

    with pytest.raises(ValueError, match="operator_run_active_pointer_not_launch_prepared"):
        module.activate_active_run(
            root=root,
            expected_run_id="qgc-activate-run",
            source="test_runtime_ready",
            now=3.0,
        )


def test_prepare_can_write_an_isolated_audit_pointer_without_replacing_default(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)

    result = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-isolated-audit-run",
        active_pointer_relative_path="Results/ui_platform/audits/qgc_isolated_audit_pointer.json",
        now=1.0,
    )

    pointer_path = root / "Results/ui_platform/audits/qgc_isolated_audit_pointer.json"
    assert result["pointer_path"] == pointer_path
    assert json.loads(pointer_path.read_text(encoding="utf-8"))["run_id"] == "qgc-isolated-audit-run"
    assert not (root / "Results/ui_platform/qgc_active_run.json").exists()


def test_finalize_marks_the_last_map_frame_terminal_and_releases_the_next_run(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)
    prepared = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-terminal-run",
        now=1.0,
    )
    _write_json(
        prepared["run_directory"] / "telemetry.json",
        {
            "schema": "mosim.runtime_telemetry.v2",
            "run_id": "qgc-terminal-run",
            "timestamp": 2.0,
            "readiness": {"status": "running"},
        },
    )

    final = module.finalize_active_run(
        root=root,
        expected_run_id="qgc-terminal-run",
        terminal_state="completed",
        reason_code="factory_l2_fault_demo_completed",
        source="test_terminal",
        now=3.0,
    )

    pointer = json.loads((root / "Results/ui_platform/qgc_active_run.json").read_text(encoding="utf-8"))
    telemetry = json.loads((prepared["run_directory"] / "telemetry.json").read_text(encoding="utf-8"))
    runtime_status = json.loads((prepared["run_directory"] / "RUNTIME_STATUS.json").read_text(encoding="utf-8"))
    assert final["telemetry_present"] is True
    assert pointer["state"] == "completed"
    assert pointer["terminal_reason_code"] == "factory_l2_fault_demo_completed"
    assert runtime_status["status"] == "completed"
    assert telemetry["operator_runtime_status"]["state"] == "completed"
    assert telemetry["mission_status"]["terminal"] is True

    next_run = module.prepare_run(
        root=root,
        profile_id="factory_demo_v1",
        runtime_profile_id="factory_demo_runtime_v1",
        run_id="qgc-after-terminal-run",
        now=4.0,
    )
    assert next_run["run_id"] == "qgc-after-terminal-run"


def test_prepare_rejects_non_matching_runtime_backend(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)

    with pytest.raises(ValueError, match="operator_run_runtime_backend_mismatch"):
        module.prepare_run(
            root=root,
            profile_id="factory_demo_v1",
            runtime_profile_id="other_runtime_v1",
            run_id="qgc-invalid-runtime",
        )


def test_prepare_rejects_disabled_operator_profile_before_creating_a_run_directory(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)
    profiles_path = root / "Config/profiles/operator_profiles.json"
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    profiles["profiles"][0]["enabled"] = False
    profiles_path.write_text(json.dumps(profiles), encoding="utf-8")

    with pytest.raises(ValueError, match="operator_run_profile_disabled"):
        module.prepare_run(
            root=root,
            profile_id="factory_demo_v1",
            runtime_profile_id="factory_demo_runtime_v1",
            run_id="qgc-disabled-profile",
        )

    assert not (root / "Results/runs/qgc-disabled-profile").exists()


def test_prepare_validates_scenario_before_creating_a_run_directory(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)
    profile_path = root / "Config/profiles/experiments/factory_demo_v1.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile["experiment_profile"]["scenario_path"] = "Config/scenarios/missing.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")

    with pytest.raises(ValueError, match="operator_run_scenario_file_missing"):
        module.prepare_run(
            root=root,
            profile_id="factory_demo_v1",
            runtime_profile_id="factory_demo_runtime_v1",
            run_id="qgc-no-directory-on-error",
        )

    assert not (root / "Results/runs/qgc-no-directory-on-error").exists()


def test_prepare_rejects_a_tampered_image_coordinate_contract(tmp_path: Path) -> None:
    module = _module()
    root = _fixture_root(tmp_path)
    catalog_path = root / "Config/control_platform/operator_map_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["maps"][0]["image_coordinate_contract"]["matrix_sha256"] = "0" * 64
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    with pytest.raises(ValueError, match="operator_map_image_coordinate_contract_hash_mismatch"):
        module.prepare_run(
            root=root,
            profile_id="factory_demo_v1",
            runtime_profile_id="factory_demo_runtime_v1",
            run_id="qgc-tampered-image-contract",
        )

    assert not (root / "Results/runs/qgc-tampered-image-contract").exists()
