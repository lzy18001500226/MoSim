from pathlib import Path


RUNNER = (
    Path(__file__).resolve().parents[1] / "sunray/run_px4ctrl_ego_swarm_gate.sh"
)
FACTORY_WRAPPER = (
    Path(__file__).resolve().parents[1]
    / "sunray/run_factory_l2_indoor_racer_swarm_coverage_gate.sh"
)
SAFETY_ADAPTER = (
    Path(__file__).resolve().parents[1] / "sunray/goal4_position_cmd_safety_adapter.py"
)
SWARM_MISSION = (
    Path(__file__).resolve().parents[1] / "sunray/px4ctrl_ego_swarm_mission_node.py"
)
RACER_LAUNCH = (
    Path(__file__).resolve().parents[1] / "sunray/racer_swarm_px4ctrl_d3.launch"
)


def test_swarm_runner_exposes_consistent_command_dynamics() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    for name in (
        "EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION",
        "EGO_CMD_SAFETY_MAX_VELOCITY_MPS",
        "EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2",
        "EGO_CMD_SAFETY_MAX_LATERAL_ACCELERATION_MPS2",
        "EGO_CMD_SAFETY_MAX_JERK_MPS3",
    ):
        assert name in source

    assert '_recompute_velocity_from_position:="${EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION}"' in source
    assert '_max_velocity_mps:="${EGO_CMD_SAFETY_MAX_VELOCITY_MPS}"' in source
    assert '"recompute_velocity_from_position": ${EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION}' in source


def test_swarm_runner_isolates_ros_logs_per_result_directory() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    result_dir_setup = source.index('mkdir -p "${RESULT_DIR}"')
    ros_log_setup = source.index(
        'ROS_LOG_DIR="${ROS_LOG_DIR:-${RESULT_DIR}/ros_logs}"'
    )
    gazebo_start = source.index("start_gazebo_world()")

    assert result_dir_setup < ros_log_setup < gazebo_start
    assert 'mkdir -p "${ROS_LOG_DIR}"' in source
    assert "export ROS_LOG_DIR" in source


def test_mavros_readiness_uses_one_persistent_subscription() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    start = source.index("wait_mavros_connected()")
    end = source.index("request_stream_rate()", start)
    readiness = source[start:end]

    assert "rospy.Subscriber(topic, State, state_callback, queue_size=1)" in readiness
    assert "rospy.wait_for_message" not in readiness
    assert readiness.count('with open(output, "w", encoding="utf-8")') == 2
    assert '"mosim_wait_mavros_connected_${RUN_ID}_uav${uid}"' in readiness
    assert 'pkill -f "mosim_wait_mavros_connected_${RUN_ID}_uav"' in source


def test_factory_wrapper_forwards_command_dynamics_overrides() -> None:
    source = FACTORY_WRAPPER.read_text(encoding="utf-8")
    for name in (
        "EGO_CMD_SAFETY_SMOOTHING_ENABLE",
        "EGO_CMD_SAFETY_MAX_TARGET_DISTANCE_FROM_ODOM_M",
        "EGO_CMD_SAFETY_MAX_XY_TARGET_DISTANCE_FROM_ODOM_M",
        "EGO_CMD_SAFETY_ZERO_ALL_DYNAMICS",
        "EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION",
        "EGO_CMD_SAFETY_MAX_VELOCITY_MPS",
        "EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2",
        "EGO_CMD_SAFETY_MAX_LATERAL_ACCELERATION_MPS2",
        "EGO_CMD_SAFETY_MAX_JERK_MPS3",
    ):
        assert f'{name}="${{{name}:-' in source

    assert (
        'EGO_CMD_SAFETY_MAX_TARGET_DISTANCE_FROM_ODOM_M='
        '"${EGO_CMD_SAFETY_MAX_TARGET_DISTANCE_FROM_ODOM_M:-0.75}"'
    ) in source
    assert (
        'EGO_CMD_SAFETY_MAX_XY_TARGET_DISTANCE_FROM_ODOM_M='
        '"${EGO_CMD_SAFETY_MAX_XY_TARGET_DISTANCE_FROM_ODOM_M:-0.60}"'
    ) in source


def test_repeated_enable_does_not_reset_command_continuity_baseline() -> None:
    source = SAFETY_ADAPTER.read_text(encoding="utf-8")
    assert "was_enabled = self.enabled" in source
    assert "if self.enabled and not was_enabled:" in source


def test_factory_racer_uses_explicit_obstacle_inflation() -> None:
    wrapper = FACTORY_WRAPPER.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    launch = RACER_LAUNCH.read_text(encoding="utf-8")

    assert 'RACER_D3_OBSTACLES_INFLATION="${RACER_D3_OBSTACLES_INFLATION:-0.35}"' in wrapper
    assert 'd3_obstacles_inflation:="${RACER_D3_OBSTACLES_INFLATION}"' in runner
    assert '"obstacles_inflation_m": ${RACER_D3_OBSTACLES_INFLATION}' in runner
    assert launch.count(
        '<param name="sdf_map/obstacles_inflation" '
        'value="$(arg d3_obstacles_inflation)" type="double"/>'
    ) == 3


def test_swarm_home_is_latched_after_pre_takeoff_settle() -> None:
    source = SWARM_MISSION.read_text(encoding="utf-8")
    settle = source.index("if not self.wait_pre_takeoff_settle(rate):")
    home_latch = source.index("uav.home_odom_z = float(uav.odom[\"z\"])")
    takeoff = source.index('self.phase = "takeoff"', settle)

    assert settle < home_latch < takeoff
