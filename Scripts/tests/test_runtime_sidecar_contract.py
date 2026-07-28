from __future__ import annotations

from pathlib import Path

import pytest

from src.orchestration.runtime_sidecar_contract import (
    evaluate_readiness_status,
    load_contract,
    resolve_gazebo_body_name,
    validate_command,
)


CONTRACT = Path("Config/control_platform/factory_injection_contract.json")


def command(**overrides):
    value = {
        "command_id": "inj-contract-test",
        "run_id": "run-test",
        "profile_hash": "hash-test",
        "target": "motor_effectiveness",
        "requested_at": 1.0,
        "apply_mode": "set",
        "value": 0.6,
        "ramp_s": 0.0,
        "duration_s": 0.0,
        "restore_policy": "manual",
        "source": "test",
        "rotor_index": 2,
    }
    value.update(overrides)
    return value


def test_contract_normalizes_restore_to_physical_nominal() -> None:
    normalized = validate_command(
        command(apply_mode="restore", value=0.0),
        manifest={"run_id": "run-test", "experiment_profile_hash": "hash-test"},
        contract=load_contract(CONTRACT),
    )
    assert normalized["value"] == 1.0
    assert normalized["vehicle_id"] == "uav1"


def test_readiness_timeout_only_applies_before_first_ready_sample() -> None:
    assert evaluate_readiness_status(ready=False, ever_ready=False, elapsed_s=211.0, timeout_s=210.0) == (
        "blocked", "runtime_readiness_timeout", False
    )
    assert evaluate_readiness_status(ready=True, ever_ready=False, elapsed_s=30.0, timeout_s=210.0) == (
        "running", "runtime_ready", True
    )
    assert evaluate_readiness_status(ready=False, ever_ready=True, elapsed_s=300.0, timeout_s=210.0) == (
        "running", "runtime_readiness_degraded", True
    )


def test_multi_uav_injection_requires_an_in_range_vehicle_id() -> None:
    manifest = {"run_id": "run-test", "experiment_profile_hash": "hash-test", "vehicle_count": 3}
    with pytest.raises(ValueError, match="injection_vehicle_id_invalid"):
        validate_command(command(), manifest=manifest, contract=load_contract(CONTRACT))
    normalized = validate_command(command(vehicle_id="uav3"), manifest=manifest, contract=load_contract(CONTRACT))
    assert normalized["vehicle_id"] == "uav3"
    with pytest.raises(ValueError, match="injection_vehicle_id_invalid"):
        validate_command(command(vehicle_id="uav4"), manifest=manifest, contract=load_contract(CONTRACT))


@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"value": 1.2}, "injection_value_out_of_range"),
        ({"rotor_index": 5}, "injection_rotor_index_invalid"),
        ({"run_id": "run-other"}, "injection_run_id_mismatch"),
    ],
)
def test_contract_rejects_invalid_commands(override, reason) -> None:
    with pytest.raises(ValueError, match=reason):
        validate_command(
            command(**override),
            manifest={"run_id": "run-test", "experiment_profile_hash": "hash-test"},
            contract=load_contract(CONTRACT),
        )


def test_runtime_wrapper_starts_sidecar_and_reuses_ftc_plugin() -> None:
    wrapper = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    assert "runtime_sidecar.py" in wrapper
    assert "wait_for_mission_terminal_sync()" in wrapper
    assert wrapper.count("wait_for_mission_terminal_sync\n") == 3
    assert 'mission.get("transport_state") == "terminal"' in wrapper
    assert "build_p7_ftc_actuator_plugin.sh" in wrapper
    assert 'MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN="true"' in wrapper
    assert "factoryenvironmentcollect_l2_static_review_clean.sdf" in wrapper
    assert "factory_l2_sunray_px4_gazebo.launch" in wrapper
    assert 'MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}"' in wrapper
    assert 'ORCHESTRATOR_RUNTIME_READY_TIMEOUT_S="${ORCHESTRATOR_RUNTIME_READY_TIMEOUT_S:-210}"' in wrapper
    assert "ensure_px4ctrl_generated_backend.sh" in wrapper
    assert 'generated_backend="pid_attitude_thrust"' in wrapper
    assert 'TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-540}"' in wrapper
    assert '--takeoff-timeout-s 90 --wall-timeout-s 480' in wrapper
    assert '--ready-timeout-s "${ready_timeout_s}"' in wrapper
    assert '--body-name "uav1::base_link"' in wrapper
    assert '--expected-path-topic "${expected_path_topic}"' in wrapper
    assert '--future-marker-topic "${future_marker_topic}"' in wrapper
    assert 'ORCHESTRATOR_MAP_COORDINATE_EVIDENCE' in wrapper
    assert 'sidecar_coordinate_args+=(--coordinate-evidence "${ORCHESTRATOR_MAP_COORDINATE_EVIDENCE}")' in wrapper
    assert 'start_sidecar 1 "/mosim/px4ctrl/reference_path"' in wrapper
    assert 'start_sidecar 1 "/mosim/goal4/target_path" "/planning_vis/trajectory"' in wrapper
    assert 'start_sidecar 3 "/mosim/goal5/target_path"' in wrapper
    assert 'ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY:-true' in wrapper
    assert 'sidecar_readiness_args+=(--skip-actuator-telemetry-readiness)' in wrapper
    assert 'export ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY="false"' in wrapper
    assert "assert_no_conflicting_runtime" in wrapper
    assert wrapper.index("assert_no_conflicting_runtime\n  local generated_backend") < wrapper.index(
        'start_sidecar 1 "/mosim/px4ctrl/reference_path"'
    )
    assert "Sunray ROS1 runtime process conflict" in wrapper
    assert 'source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"' in wrapper
    assert "sunray_ros1_runtime_lock_acquire\n  assert_no_conflicting_runtime" in wrapper
    assert "sunray_ros1_runtime_lock_release" in wrapper
    assert "start_sidecar 3" in wrapper
    assert "factory_l2_three_uav_swarm_formation" in wrapper
    assert 'PLANNER_VARIANT="swarm_formation"' in wrapper
    assert 'manifest.get("experiment_profile_id") != "factory_l2_three_uav_swarm_formation_v1"' in wrapper
    assert 'SWARM_FORMATION_D3_CENTER_X="${formation_values[1]}"' in wrapper
    assert "formation RunManifest is incomplete; refusing to launch" in wrapper


def test_display_helper_uses_argument_safe_shell_entrypoint() -> None:
    helper = Path("Scripts/ui/attach_orchestrated_displays.ps1").read_text(encoding="utf-8")
    launcher = Path("Scripts/ui/launch_ros1_display.sh").read_text(encoding="utf-8")
    assert "bash -lc" not in helper
    assert "launch_ros1_display.sh" in helper
    assert '"unreal_bridge", $hostAddress' in helper
    assert "px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash" in launcher
    assert "source \"${PX4CTRL_OVERLAY}\"" in launcher
    assert "exec rviz" in launcher
    assert 'state = "running"' in helper
    assert 'process_exited_during_startup' in helper


def test_wind_wrench_success_has_stable_reason_code() -> None:
    sidecar = Path("Scripts/ui/runtime_sidecar.py").read_text(encoding="utf-8")
    assert 'if response.success and not reason:' in sidecar
    assert 'reason = "wind_wrench_applied"' in sidecar


def test_sidecar_ack_keeps_the_fault_identity_for_qgc_readback() -> None:
    sidecar = Path("Scripts/ui/runtime_sidecar.py").read_text(encoding="utf-8")
    assert '"target": command.get("target", "")' in sidecar
    assert '"rotor_index": command.get("rotor_index")' in sidecar
    assert '"apply_mode": command.get("apply_mode", "")' in sidecar
    assert '"source": command.get("source", "")' in sidecar


def test_sidecar_can_skip_ftc_readiness_for_non_fault_profiles() -> None:
    sidecar = Path("Scripts/ui/runtime_sidecar.py").read_text(encoding="utf-8")
    assert "if not self.args.skip_actuator_telemetry_readiness:" in sidecar
    assert '"--skip-actuator-telemetry-readiness"' in sidecar


def test_sidecar_exports_only_real_reference_and_future_path_sources() -> None:
    sidecar = Path("Scripts/ui/runtime_sidecar.py").read_text(encoding="utf-8")
    assert '"task_paths": self.task_paths' in sidecar
    assert 'semantics = "formation_center_reference"' in sidecar
    assert 'semantics = "exploration_target_sequence"' in sidecar
    assert 'semantics = "mission_reference"' in sidecar
    assert '"vehicle_scope": vehicle_scope' in sidecar
    assert '"semantics": "planner_sampled_future_trajectory"' in sidecar
    assert 'msg.ns != "B-Spline"' in sidecar
    assert "msg.id >= 50" in sidecar
    assert '"mission_status": load_mission_status(' in sidecar
    assert 'payload.get("run_id") == expected_run_id' in sidecar
    assert '"transport_state": "terminal" if terminal' in sidecar
    assert '"--coordinate-evidence"' in sidecar
    assert "project_live_operator_map_frame(" in sidecar
    assert "coordinate evidence cannot be combined with a status override" in sidecar


def test_generated_backend_ensure_is_fail_closed() -> None:
    source = Path("Scripts/sunray/ensure_px4ctrl_generated_backend.sh").read_text(encoding="utf-8")
    assert "catkin_make --force-cmake" in source
    assert 'current}" != "${BACKEND}' in source
    assert 'legacy_px4ctrl) definition="MOSIM_PX4CTRL_GENERATED_BACKEND_LEGACY"' in source
    assert "PX4CTRL_BACKEND_ENSURE.json" in source
    assert "MOSIM_PX4CTRL_PID_ATTITUDE_THRUST_GENERATED_DIR" in source
    assert "runtime acknowledgement is required separately" in source


def test_px4ctrl_cmake_resolves_symlinked_source_before_project_root() -> None:
    cmake = Path(
        "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/CMakeLists.txt"
    ).read_text(encoding="utf-8")
    assert 'get_filename_component(MOSIM_PX4CTRL_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" REALPATH)' in cmake
    assert '"${MOSIM_PX4CTRL_SOURCE_DIR}/../../../../../../.." ABSOLUTE' in cmake


def test_gazebo_body_resolution_prefers_explicit_factory_vehicle() -> None:
    assert resolve_gazebo_body_name("uav1::base_link", ["sunray150_with_mid360"]) == "uav1::base_link"


def test_gazebo_body_resolution_prefers_runtime_uav_name() -> None:
    assert resolve_gazebo_body_name("", ["ground_plane", "sunray150_template", "uav1"]) == "uav1::base_link"


def test_gazebo_body_resolution_keeps_sunray_fallback() -> None:
    assert resolve_gazebo_body_name("", ["ground_plane", "sunray150_with_mid360"]) == (
        "sunray150_with_mid360::base_link"
    )


def test_gazebo_body_resolution_selects_requested_swarm_vehicle() -> None:
    assert resolve_gazebo_body_name("", ["uav1", "uav2", "uav3"], "uav2") == "uav2::base_link"


def test_atomic_json_transport_uses_python38_compatible_file_api() -> None:
    contract_source = Path("src/orchestration/runtime_sidecar_contract.py").read_text(encoding="utf-8")
    assert '.open("w", encoding="utf-8", newline="\\n")' in contract_source
    assert "write_text(json.dumps" not in contract_source
    assert "except PermissionError:" in contract_source
    assert "for attempt in range(10):" in contract_source
