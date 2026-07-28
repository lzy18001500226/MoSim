from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


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
    _write_json(
        tmp_path / "Config/control_platform/operator_map_catalog.json",
        {"maps": [{"map_id": "factory_l2", "enabled": True, "world_bounds_m": {"min_x_m": -1, "max_x_m": 1}}]},
    )
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
    assert manifest["experiment_profile_id"] == "factory_demo_v1"
    assert manifest["experiment_profile_hash"] == hashlib.sha256(profile_path.read_bytes()).hexdigest()
    assert manifest["controller_backend"] == "fixture_controller_backend_v1"
    assert manifest["vehicle_count"] == 3
    assert manifest["operator_map_snapshot"]["map_id"] == "factory_l2"
    assert manifest["scenario_snapshot"]["formation"]["type"] == "leader_follower"
    assert pointer["state"] == "launch_prepared"
    assert pointer["run_directory"] == "Results/runs/qgc-test-run"


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
