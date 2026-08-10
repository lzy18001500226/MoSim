from __future__ import annotations

import inspect
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MWORKS_DIR = ROOT / "Scripts" / "mworks"
if str(MWORKS_DIR) not in sys.path:
    sys.path.insert(0, str(MWORKS_DIR))

import run_g6_formal_champion as closure  # noqa: E402


def assert_source_hashes(binding: dict) -> None:
    assert all(source["expected_sha256"] for source in binding["source_bindings"])
    for source in binding["source_bindings"]:
        source_path = ROOT / source["path"]
        assert source_path.is_file(), source_path
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == source["expected_sha256"]


def test_shared_runner_baseline_bindings_are_hash_bound_and_not_champion_claims() -> None:
    binding_dir = ROOT / "Config" / "control_platform" / "runner_baseline_bindings"
    bindings = [
        (path, closure.read_binding(path))
        for path in sorted(binding_dir.glob("*.json"))
        if closure.read_binding(path)["controller_category"] == "runner_boundary_fixture"
    ]
    assert [path.stem for path, _ in bindings] == ["attitude_thrust", "body_rate_thrust", "rotor_command", "wrench"]

    expected_boundaries = {"ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"}
    expected_shared_chain = {
        "shared_plant",
        "physical_wrench_adapter",
        "wrapper_surface",
        "rotor_actuator_core",
        "plant_sensor_surface",
        "virtual_px4_classic_profile",
        "climb_path_reference",
    }
    actual_boundaries: set[str] = set()
    for path, binding in bindings:
        assert binding["execution_metadata"]["kind"] == "runner_boundary_baseline"
        assert binding["execution_metadata"]["status_file_name"] == "RUNNER_BASELINE_STATUS.json"
        assert binding["formal_adapter"]["output_boundary"] in expected_boundaries
        actual_boundaries.add(binding["formal_adapter"]["output_boundary"])
        assert_source_hashes(binding)
        runner_source = (ROOT / binding["target"]["model_file"]).read_text(encoding="utf-8")
        assert "replaceable model Trajectory" in runner_source
        assert "connect(reference.velocity_command, controller.velocity_ref)" in runner_source
        assert "connect(reference.acceleration_command, controller.acceleration_ref)" in runner_source
        roles = {source["role"] for source in binding["source_bindings"]}
        assert expected_shared_chain.issubset(roles)
        assert "visual_chassis" not in roles

    assert actual_boundaries == expected_boundaries


def test_px4ctrl_engineering_baseline_is_hash_bound_separately_from_shared_runner_fixtures() -> None:
    binding = closure.read_binding(
        ROOT / "Config" / "control_platform" / "runner_baseline_bindings" / "px4ctrl.json"
    )

    assert binding["controller_id"] == "px4ctrl"
    assert binding["controller_category"] == "engineering_deployment_baseline"
    assert binding["execution_metadata"]["kind"] == "runner_boundary_baseline"
    assert binding["formal_adapter"]["output_boundary"] == "ATTITUDE_THRUST"
    assert_source_hashes(binding)

    public_runner_source = (ROOT / binding["target"]["model_file"]).read_text(encoding="utf-8")
    effective_runner_source = (
        ROOT / binding["formal_harness_feedback_boundary"]["effective_model_file"]
    ).read_text(encoding="utf-8")
    assert "extends Px4CtrlEquationBridgeFormalRunner;" in public_runner_source
    assert "replaceable model Trajectory" in effective_runner_source
    assert "connect(reference.velocity_command, sampled_velocity_ref.u)" in effective_runner_source
    assert "connect(reference.acceleration_command, sampled_acceleration_ref.u)" in effective_runner_source
    roles = {source["role"] for source in binding["source_bindings"]}
    assert {
        "shared_sunray150_assembly",
        "physical_wrench_adapter",
        "wrapper_surface",
        "rotor_actuator_core",
        "plant_sensor_surface",
        "virtual_px4_classic_profile",
        "climb_path_reference",
    }.issubset(roles)
    assert "visual_chassis" not in roles


def test_offline_runner_contract_declares_forward_references() -> None:
    contract_path = ROOT / "Config" / "control_platform" / "offline_runner_interface_contract_v1.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    input_names = {item["name"] for item in contract["shared_controller_inputs"]}

    assert {"position_ref", "velocity_ref", "acceleration_ref"}.issubset(input_names)
    assert contract["live_runner_baseline_evidence"]["current_source_replay_required"] is True


def test_formal_champion_preloads_project_root_before_leaf_load() -> None:
    source = inspect.getsource(closure.main)

    assert "record[\"base_package_preload\"] = preload_base_packages(client)" in source
    assert source.index("record[\"base_package_preload\"] = preload_base_packages(client)") < source.index(
        "load = client.call_tool("
    )
