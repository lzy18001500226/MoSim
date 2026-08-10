from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "sunray" / "run_diff_swarm_core_fixture.sh"
PROBE = ROOT / "Scripts" / "sunray" / "probe_diff_swarm_core_fixture.py"
LAUNCH = ROOT / "Scripts" / "sunray" / "diff_swarm_px4ctrl_goal5.launch"
OFFSET_BRIDGE = ROOT / "Scripts" / "ros" / "ros1_coordinate_offset_bridge.py"
SWARM_GATE = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_swarm_gate.sh"


def test_diff_swarm_launch_exposes_per_uav_planner_frame_topics() -> None:
    launch = LAUNCH.read_text(encoding="utf-8")

    for uid in (1, 2, 3):
        assert f'name="uav{uid}_odom_topic"' in launch
        assert f'name="uav{uid}_global_pointcloud_topic"' in launch
        assert f'name="uav{uid}_position_cmd_topic"' in launch
        assert f'name="uav{uid}_goal_topic"' in launch
    assert 'value="$(arg uav1_odom_topic)"' in launch
    assert 'value="$(arg uav2_position_cmd_topic)"' in launch
    assert 'value="$(arg uav3_goal_topic)"' in launch


def test_diff_swarm_common_world_fixture_stays_in_planner_core_scope() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    probe = PROBE.read_text(encoding="utf-8")

    assert "without Gazebo, PX4, QGC, or UE" in runner
    assert "diff_swarm_px4ctrl_goal5.launch" in runner
    assert "planner_odom_world" in runner
    assert "planner_cloud_world" in runner
    assert "planner_goal_world" in runner
    assert "planner_position_cmd_world" in runner
    assert "from traj_utils.msg import MINCOTraj, PolyTraj" in probe
    assert "transparent_single_ros_master_common_world" in probe
    assert "planner_broadcast_from_missing" in probe
    assert "It does not prove FAST-LIO, MID360" in probe


def test_coordinate_offset_bridge_supports_diff_planner_position_commands() -> None:
    bridge = OFFSET_BRIDGE.read_text(encoding="utf-8")

    assert "from quadrotor_msgs.msg import PositionCommand" in bridge
    assert 'self.message_type == "position_cmd"' in bridge
    assert "def on_position_cmd" in bridge
    assert "out.position.x, out.position.y, out.position.z = self.shifted" in bridge
    assert "pose, odom, cloud, position_cmd, marker, or marker_array" in bridge


def test_diff_swarm_c99_gate_wires_common_world_frame_without_sensor_tuning() -> None:
    gate = SWARM_GATE.read_text(encoding="utf-8")

    assert 'sed "s/{uid}/' in gate
    assert 's/{drone_id}/' in gate
    assert '/uav{uid/mosim' not in gate
    assert "DIFF_GOAL5_PLANNER_ODOM_TOPIC_TEMPLATE:-/uav{uid}" not in gate
    assert "DIFF_GOAL5_PLANNER_GOAL_TOPIC_TEMPLATE:-/uav{uid}" not in gate
    assert "DIFF_GOAL5_PLANNER_POSITION_CMD_TOPIC_TEMPLATE:-/uav{uid}" not in gate
    assert "DIFF_GOAL5_PLANNER_ODOM_TOPIC_TEMPLATE='/uav{uid}/mosim/diff_swarm/planner_odom_world'" in gate
    assert "DIFF_GOAL5_PLANNER_GOAL_TOPIC_TEMPLATE='/uav{uid}/mosim/diff_swarm/planner_goal_world'" in gate
    assert "DIFF_GOAL5_PLANNER_CLOUD_TOPIC_TEMPLATE='/uav{uid}/mosim/diff_swarm/planner_cloud_world'" in gate
    assert (
        "DIFF_GOAL5_PLANNER_POSITION_CMD_TOPIC_TEMPLATE='/uav{uid}/mosim/diff_swarm/planner_position_cmd_world'"
        in gate
    )

    assert 'DIFF_GOAL5_COMMON_WORLD_FRAME="${DIFF_GOAL5_COMMON_WORLD_FRAME:-false}"' in gate
    assert "_message_type:=odom" in gate
    assert "_message_type:=cloud" in gate
    assert "_message_type:=pose" in gate
    assert "_message_type:=position_cmd" in gate
    assert "_direction:=local_to_world" in gate
    assert "_direction:=world_to_local" in gate
    assert "DIFF_GOAL5_PLANNER_ODOM_TOPIC_TEMPLATE" in gate
    assert "DIFF_GOAL5_PLANNER_CLOUD_TOPIC_TEMPLATE" in gate
    assert "DIFF_GOAL5_PLANNER_GOAL_TOPIC_TEMPLATE" in gate
    assert "DIFF_GOAL5_PLANNER_POSITION_CMD_TOPIC_TEMPLATE" in gate
    assert "point-cloud and grid-map parameters are unchanged" in gate
    assert 'DIFF_GOAL5_FLIGHT_TYPE="${DIFF_GOAL5_FLIGHT_TYPE:-1}"' in gate
    assert 'DIFF_GOAL5_PLANNER_TARGET_MODE="${DIFF_GOAL5_PLANNER_TARGET_MODE:-goal}"' in gate
