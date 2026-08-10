import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "src" / "control" / "runtime_adapters" / "px4ctrl"
CODEGEN = ROOT / "src" / "control" / "codegen" / "px4ctrl"
PREPARE = ROOT / "Scripts" / "sunray" / "prepare_local_ros1_workspace.sh"
GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_basic_gate.sh"
FASTLIO_GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_fastlio_hover_gate.sh"
OPERATOR_LIVE_GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_fastlio_operator_live_gate.sh"
RUNTIME_BACKEND_CATALOG = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
MULTIUAV_GATE = ROOT / "Scripts" / "sunray" / "run_c99_multiuav_planner_gate.sh"
FACTORY_DIFF_GATE = ROOT / "Scripts" / "sunray" / "start_factory_diff_swarm_coverage_probe.ps1"
FORMATION_GATE = ROOT / "Scripts" / "sunray" / "run_factory_l2_swarm_formation_obstacle_gate.ps1"


def test_graphical_c99_backend_has_a_project_local_build_path() -> None:
    cmake = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")

    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "graphical_px4ctrl_c99"' in cmake
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_GRAPHICAL_PX4CTRL_C99" in cmake
    assert "px4ctrl_graphical_generated_shared.c" in cmake
    assert "MOSIM_PX4CTRL_CONTROL_SOURCE_DIR" in cmake
    assert "Results/" not in cmake


def test_graphical_wrapper_uses_private_init_step_symbols() -> None:
    wrapper = (CODEGEN / "px4ctrl_graphical_generated_shared.c").read_text(
        encoding="utf-8"
    )

    assert "#define Init MosimPx4ctrlGraphicalGeneratedInit" in wrapper
    assert "#define Step MosimPx4ctrlGraphicalGeneratedStep" in wrapper
    assert "MosimPx4ctrlGeneratedGraphConfigure" in wrapper
    assert "raphical_sysblockGbDw.k_hb = kp_x" in wrapper
    assert "raphical_sysblockGbDw.k_x = kp_z" in wrapper
    assert "raphical_sysblockGbDw.k_ea = kv_z" in wrapper
    assert "MosimPx4ctrlGeneratedGraphStepScalar" in wrapper


def test_ros_adapter_uses_physical_acceleration_for_runtime_thrust_mapping() -> None:
    controller = (PX4CTRL / "src" / "controller.cpp").read_text(encoding="utf-8")
    start = controller.index("LinearControl::calculateGraphicalC99Control")
    end = controller.index("LinearControl::usingGeneratedCore", start)
    graphical = controller[start:end]

    assert "MosimPx4ctrlGeneratedGraphConfigure" in graphical
    assert "param_.gain.Kp0, param_.gain.Kv0" in graphical
    assert "param_.gain.Kp2, param_.gain.Kv2" in graphical
    assert "param_.thr_map.hover_percentage" in graphical
    assert "MosimPx4ctrlGeneratedGraphStepScalar" in graphical
    assert "computeDesiredCollectiveThrustSignal(generated_des_acc)" in graphical
    assert "u.thrust = generated_normalized_thrust" not in graphical
    assert "bodyrateAttitudeFeedback" in graphical

def test_source_local_entry_requires_a_matching_graphical_build() -> None:
    prepare = PREPARE.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    fastlio = FASTLIO_GATE.read_text(encoding="utf-8")

    assert "--px4ctrl-backend" in prepare
    assert "graphical_px4ctrl_c99" in prepare
    assert "graphical_c99" in gate
    assert "capture_px4ctrl_build_backend" in gate
    assert "PX4CTRL_EXPECTED_BUILD_BACKEND" in gate
    assert "PX4CTRL_BUILD_BACKEND=graphical_px4ctrl_c99" not in gate
    assert "PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99" in fastlio


def test_factory_c99_fastlio_alignment_origin_is_bound_to_factory_spawn() -> None:
    catalog = json.loads(RUNTIME_BACKEND_CATALOG.read_text(encoding="utf-8"))
    backend = next(
        item
        for item in catalog["runtime_profiles"]
        if item["operation_id"] == "factory_l2_graphical_px4ctrl_c99_figure8"
    )
    environment = backend["operator_invocation"]["shell_environment"]
    gate = OPERATOR_LIVE_GATE.read_text(encoding="utf-8")

    assert environment["FASTLIO_ALIGNMENT_ORIGIN_X"] == environment["SUNRAY_UAV_INIT_X"]
    assert environment["FASTLIO_ALIGNMENT_ORIGIN_Y"] == environment["SUNRAY_UAV_INIT_Y"]
    assert environment["FASTLIO_ALIGNMENT_ORIGIN_Z"] == "0.035"
    assert environment["ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY"] == "false"
    assert 'FASTLIO_ALIGNMENT_ORIGIN_X="${FASTLIO_ALIGNMENT_ORIGIN_X:-${SUNRAY_UAV_INIT_X}}"' in gate
    assert 'FASTLIO_ALIGNMENT_ORIGIN_Y="${FASTLIO_ALIGNMENT_ORIGIN_Y:-${SUNRAY_UAV_INIT_Y}}"' in gate
    assert 'FASTLIO_ALIGNMENT_ORIGIN_XYZ="${FASTLIO_ALIGNMENT_ORIGIN_X} ${FASTLIO_ALIGNMENT_ORIGIN_Y} ${FASTLIO_ALIGNMENT_ORIGIN_Z}"' in gate
    assert "validate_factory_l2_fastlio_alignment_origin" in gate
    assert gate.index("validate_factory_l2_fastlio_alignment_origin") < gate.index("source /opt/ros/noetic/setup.bash")
    assert 'export FASTLIO_ALIGNMENT_ORIGIN_XYZ' in gate
    assert 'RUNTIME_RESULT_DIR="${RESULT_DIR}/runtime"' in gate
    assert 'RESULT_DIR="${RUNTIME_RESULT_DIR}" exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${MISSION}"' in gate
    assert 'metrics_path = runtime_root / "PX4CTRL_BASIC_MISSION_METRICS.json"' in gate
    assert 'QGC_SIDECAR_READINESS_ARGS+=(--skip-actuator-telemetry-readiness)' in gate
    assert '"${QGC_SIDECAR_READINESS_ARGS[@]}"' in gate


def test_c99_multi_uav_routes_default_to_the_preloaded_world() -> None:
    multi_uav = MULTIUAV_GATE.read_text(encoding="utf-8")
    factory_diff = FACTORY_DIFF_GATE.read_text(encoding="utf-8")
    formation = FORMATION_GATE.read_text(encoding="utf-8")

    assert 'STAGGERED_SPAWN="${STAGGERED_SPAWN:-false}"' in multi_uav
    assert 'PRELOAD_GAZEBO_MODELS="${PRELOAD_GAZEBO_MODELS:-true}"' in multi_uav
    assert '"PRELOAD_GAZEBO_MODELS=$preloadGazeboModelsValue"' in factory_diff
    assert '"PRELOAD_GAZEBO_MODELS=true"' in formation
    assert '"STAGGERED_SPAWN=false"' in formation


def test_c99_multi_uav_gate_checks_the_declared_ros1_runtime_lane_first() -> None:
    multi_uav = MULTIUAV_GATE.read_text(encoding="utf-8")

    assert "check_sunray_ros1_runtime_preflight.sh" in multi_uav
    assert '"${RESULT_DIR}/runtime_preflight.log"' in multi_uav


def test_c99_diff_target_contract_is_exported_to_the_shared_mission_gate() -> None:
    multi_uav = MULTIUAV_GATE.read_text(encoding="utf-8")

    assert "export START1_X START1_Y START2_X START2_Y START3_X START3_Y" in multi_uav
    assert "export TARGET1_X TARGET1_Y TARGET1_Z TARGET2_X TARGET2_Y TARGET2_Z TARGET3_X TARGET3_Y TARGET3_Z" in multi_uav
    assert "export C99_DIFF_MAVROS_ODOM_FRAME" in multi_uav
    assert 'C99_DIFF_MAVROS_ODOM_FRAME="${C99_DIFF_MAVROS_ODOM_FRAME:-common_world}"' in multi_uav
