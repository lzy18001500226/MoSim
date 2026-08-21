from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh"
PREFLIGHT = ROOT / "Scripts" / "sunray" / "check_sunray_ros1_runtime_preflight.sh"
QGC_WRAPPER = ROOT / "Scripts" / "sunray" / "run_qgc_diff_realtime_goal_gate.sh"
FACTORY_LAUNCH = ROOT / "Scripts" / "sunray" / "factory_l2_sunray_px4_gazebo.launch"


def test_factory_world_runtime_overlay_is_opt_in_and_records_its_manifest() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert 'SUNRAY_FACTORY_WORLD_RUNTIME_OVERLAY="${SUNRAY_FACTORY_WORLD_RUNTIME_OVERLAY:-false}"' in source
    assert 'materialize_gazebo_world_overlay.py' in source
    assert 'SUNRAY_GAZEBO_LAUNCH_FILE}" != *"factory_l2_sunray_px4_gazebo.launch"' in source
    assert 'WORLD_FILE="${RUNTIME_WORLD_FILE}"' in source
    assert '"factory_world_runtime_overlay": "${SUNRAY_FACTORY_WORLD_RUNTIME_OVERLAY}"' in source


def test_single_diff_gate_syncs_against_the_selected_livox_plugin_workspace() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert '--local-ros1-ws "${LIVOX_PLUGIN_WS}"' in source


def test_factory_launch_prefers_generated_drone_models_for_vehicle_resolution() -> None:
    source = FACTORY_LAUNCH.read_text(encoding="utf-8")

    assert source.index("$(arg sunray_model_path)/drone_models") < source.index(
        "$(arg factory_model_path)"
    )
    assert source.index("$(arg sunray_model_path)/sensor_models") < source.index(
        "$(arg factory_model_path)"
    )


def test_factory_ab_runner_keeps_gpu_build_and_runtime_workspace_identical() -> None:
    source = (ROOT / "Scripts" / "sunray" / "run_factory_l2_realtime_ab_case.sh").read_text(
        encoding="utf-8"
    )

    assert 'AB_LIVOX_PLUGIN_WS="${PROJECT_ROOT}/Results/sunray_ros1/workspaces/factory_l2_ab_gpu_livox_plugin_ws"' in source
    assert 'export GPU_LIVOX_PLUGIN_WS="${AB_LIVOX_PLUGIN_WS}"' in source
    assert 'SUNRAY_LIVOX_PLUGIN_FILENAME="${AB_LIVOX_PLUGIN_WS}/devel/lib/libmosim_gpu_livox_pointcloud.so"' in source
    assert 'GPU_VISUAL_OVERLAY="${PROJECT_ROOT}/Results/sunray_ros1/performance_overlays/factory_l2_gpu_visual_lite_10pct/models"' in source
    assert 'FACTORY_MODEL_OVERLAY="${GPU_VISUAL_OVERLAY}"' in source
    assert 'FACTORY_MODEL_OVERLAY="${COLLISION_OVERLAY}"' in source
    assert 'control_gpu_visual)' in source
    assert 'OVERLAY_PROFILE=gpu_visual_lite' in source
    assert 'gpu2x2)' in source
    assert 'OUTER_RAY_HORIZONTAL_SAMPLES=2' in source
    assert 'OUTER_RAY_VERTICAL_SAMPLES=2' in source
    assert 'gpu_full_physics400)' in source
    assert 'gpu_full2x2)' in source
    assert 'gpu_full_physics400' in source
    assert 'gpu_full2x2' in source
    assert 'FACTORY_MODEL_OVERLAY_KIND="${RAY_BACKEND}_full_factory_review_models"' in source
    assert 'export QGC_DIFF_GAZEBO_MODEL_OVERLAY="${FACTORY_MODEL_OVERLAY}"' in source


def test_factory_ab_runner_rejects_unsupported_400_hz_before_ros_startup() -> None:
    source = (ROOT / "Scripts" / "sunray" / "run_factory_l2_realtime_ab_case.sh").read_text(
        encoding="utf-8"
    )

    assert "validate_lockstep_pacing_contract()" in source
    assert "valid_rate = (rate > 0 && rate == int(rate) && (int(rate) % 250) == 0)" in source
    assert "400 Hz is unsupported by libgazebo_mavlink_interface" in source
    assert source.index("validate_lockstep_pacing_contract") < source.index(
        "source /opt/ros/noetic/setup.bash"
    )


def test_gpu_preflight_selects_the_gpu_plugin_instead_of_the_ode_plugin() -> None:
    source = PREFLIGHT.read_text(encoding="utf-8")

    assert 'SUNRAY_MID360_RAY_BACKEND="${SUNRAY_MID360_RAY_BACKEND:-ode}"' in source
    assert 'libmosim_gpu_livox_pointcloud.so' in source
    assert 'src/simulation/gazebo/plugins/sunray/gpu_livox_pointcloud' in source
    assert 'setup_sunray_gpu_livox_pointcloud_plugin.sh' in source


def test_gpu_plugin_setup_refreshes_copied_source_timestamps() -> None:
    source = (ROOT / "Scripts" / "sunray" / "setup_sunray_gpu_livox_pointcloud_plugin.sh").read_text(
        encoding="utf-8"
    )

    assert 'cp -a --no-preserve=timestamps "${SRC_PKG}/." "${DST_PKG}/"' in source


def test_qgc_wrapper_starts_roscore_on_the_selected_master_port() -> None:
    source = QGC_WRAPPER.read_text(encoding="utf-8")

    assert 'QGC_DIFF_ROS_MASTER_PORT="${ROS_MASTER_URI##*:}"' in source
    assert 'roscore -p "$QGC_DIFF_ROS_MASTER_PORT"' in source
