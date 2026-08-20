from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.sunray.diff_swarm_goal_geometry import (
    default_formation_offsets,
    minimum_pairwise_distance,
    parse_vector_list,
    route_center_goal,
)


def test_three_uav_rviz_center_expands_to_separated_world_targets() -> None:
    targets = route_center_goal((10.0, 20.0, 1.0), default_formation_offsets(3))

    assert targets == ((10.0, 19.0, 1.0), (10.0, 21.0, 1.0), (10.0, 20.0, 1.0))
    assert minimum_pairwise_distance(targets) == 1.0


def test_common_world_goal_is_converted_to_each_uav_local_planner_frame() -> None:
    targets = route_center_goal(
        (10.0, 20.0, 1.0),
        default_formation_offsets(2),
        world_to_local_offsets=((6.0, 15.0, 0.0), (7.0, 15.0, 0.0)),
    )

    assert targets == ((4.0, 4.0, 1.0), (3.0, 6.0, 1.0))


def test_two_uav_common_world_goal_uses_only_two_spawn_offsets() -> None:
    targets = route_center_goal(
        (10.0, 20.0, 1.0),
        default_formation_offsets(2),
        world_to_local_offsets=((0.0, -1.0, 0.0), (0.0, 1.0, 0.0)),
    )

    assert targets == ((10.0, 20.0, 1.0), (10.0, 20.0, 1.0))


def test_world_goal_router_rejects_offset_count_that_does_not_match_vehicle_count() -> None:
    try:
        parse_vector_list("0,-1,0;0,1,0;0,0,0", expected_count=2, field="world_to_local_offsets")
    except ValueError as exc:
        assert str(exc) == "world_to_local_offsets must contain 2 vectors"
    else:
        raise AssertionError("three spawn offsets were accepted for a two-UAV batch")


def test_router_geometry_rejects_malformed_offset_count() -> None:
    try:
        parse_vector_list("0,-1,0;0,1,0", expected_count=3, field="formation_offsets")
    except ValueError as exc:
        assert str(exc) == "formation_offsets must contain 3 vectors"
    else:
        raise AssertionError("malformed offset count was accepted")


def test_swarm_gate_wires_manual_router_and_interactive_mission_mode() -> None:
    gate = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")
    mission = (ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py").read_text(encoding="utf-8")
    router = (ROOT / "Scripts/sunray/diff_swarm_rviz_goal_router.py").read_text(encoding="utf-8")
    fastlio_adapter = (ROOT / "Scripts/sunray/fastlio_odom_alignment_adapter.py").read_text(encoding="utf-8")

    assert "diff_swarm_rviz_goal_router.py" in gate
    assert "DIFF_SWARM_INTERACTIVE_GOAL_REVIEW" in gate
    assert "--world-to-local-offsets" in gate
    assert "--interactive-goal-review" in gate
    assert "--interactive-goal-idle-timeout-s" in gate
    assert 'DIFF_SWARM_GOAL_OUTPUT_FRAME="${DIFF_SWARM_GOAL_OUTPUT_FRAME:-local}"' in gate
    assert 'parser.add_argument("--output-frame", default="local")' in router
    assert "/mosim/diff_swarm/interactive_goal_ready" in mission
    assert "same-stamp per-UAV goal batch" in mission
    assert "latch=False" in router
    assert "collision-aware swarm planning" in router
    assert 'self.phase not in {\n            "interactive_wait_for_goal",\n            "ego_execute",\n        }' in mission
    assert "run_interactive_goal_session" in mission
    assert "interactive_goal_completion_history" in mission
    assert "DIFF_GOAL5_FASTLIO_INPUT_ENABLED" in gate
    assert "start_diff_fastlio_frontend" in gate
    assert "DIFF_GOAL5_FASTLIO_ALIGNED_ODOM_TOPIC_TEMPLATE" in gate
    assert "DIFF_GOAL5_FASTLIO_ALIGNED_CLOUD_TOPIC_TEMPLATE" in gate
    assert 'ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"' in gate
    assert "ensure_ros_master" in gate
    assert 'roscore -p "${ROS_MASTER_PORT}"' in gate
    assert "diff_odom_input" in gate
    assert "FAST-LIO aligned PointCloud2 and odometry" in gate
    assert 'choices=["fastlio", "local", "truth", "truth_delta"]' in fastlio_adapter


def test_router_bootstraps_project_root_for_absolute_script_execution() -> None:
    router = (ROOT / "Scripts/sunray/diff_swarm_rviz_goal_router.py").read_text(encoding="utf-8")

    assert "PROJECT_ROOT = Path(__file__).resolve().parents[2]" in router
    assert "sys.path.insert(0, str(PROJECT_ROOT))" in router


def test_swarm_phase1_launcher_allows_multiple_rviz_waypoints_with_a_bounded_session() -> None:
    launcher = (ROOT / "Scripts/sunray/start_factory_l2_rviz_qgc_phase1_swarm.sh").read_text(encoding="utf-8")
    display = (ROOT / "Scripts/sunray/start_factory_l2_rviz_qgc_phase1_swarm_display.sh").read_text(encoding="utf-8")

    assert 'DIFF_SWARM_INTERACTIVE_GOAL_TIMEOUT_S="${DIFF_SWARM_INTERACTIVE_GOAL_TIMEOUT_S:-900}"' in launcher
    assert 'DIFF_SWARM_INTERACTIVE_GOAL_IDLE_TIMEOUT_S="${DIFF_SWARM_INTERACTIVE_GOAL_IDLE_TIMEOUT_S:-10}"' in launcher
    assert 'TOTAL_TIMEOUT_S="${PHASE1_SWARM_TOTAL_TIMEOUT_S:-1800}"' in launcher
    assert 'RUNTIME_OVERLAY_WORKSPACE="${PROJECT_ROOT}/build/ros1/runtime_overlays/${RUN_ID}"' in launcher
    assert 'prepare_local_ros1_runtime_overlay.sh' in launcher
    assert 'source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"' in launcher
    assert 'export SUNRAY_PX4_DIR="${PROJECT_ROOT}/src/flight_stack/px4/PX4-Autopilot"' in launcher
    assert 'export PX4_BUILD_DIR="${PROJECT_ROOT}/build/px4/px4_sitl_default"' in launcher
    assert 'ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"' in launcher
    assert "one or more RViz 2D Nav Goals" in launcher
    assert "one or more waypoints" in display


def test_phase1_swarm_uses_aligned_fastlio_cloud_as_planner_input_and_keeps_review_topic_stable() -> None:
    gate = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")
    launcher = (ROOT / "Scripts/sunray/start_factory_l2_rviz_qgc_phase1_swarm.sh").read_text(encoding="utf-8")
    packet = (ROOT / "Scripts/sunray/rviz_qgc_display_phase1_swarm.py").read_text(encoding="utf-8")

    assert 'FASTLIO_WS="${FASTLIO_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/fastlio_ws}"' in gate
    assert 'DIFF_GOAL5_FASTLIO_INPUT_ENABLED="${DIFF_GOAL5_FASTLIO_INPUT_ENABLED:-true}"' in launcher
    assert 'DIFF_GOAL5_FASTLIO_ALIGNED_CLOUD_TOPIC_TEMPLATE' in gate
    assert 'topic_tools relay "${planner_cloud_topic}" "/uav${uid}/livox_world"' in gate
    assert '"fastlio_xy_role": "planner_input_when_enabled_after_alignment_gate"' in packet
    assert '"fastlio_aligned_cloud_topic_template": "/uav{uid}/mosim/diff_swarm/fastlio/aligned_cloud"' in launcher


def test_swarm_qgc_sidecar_uses_common_world_odometry_for_actual_tracks() -> None:
    sidecar = (ROOT / "Scripts/ui/runtime_sidecar.py").read_text(encoding="utf-8")
    launcher = (ROOT / "Scripts/sunray/start_factory_l2_rviz_qgc_phase1_swarm_display.sh").read_text(encoding="utf-8")
    packet = (ROOT / "Scripts/sunray/rviz_qgc_display_phase1_swarm.py").read_text(encoding="utf-8")

    assert '"--odom-topic-template"' in sidecar
    assert 'self.args.odom_topic_template.format(uid=vehicle_id[3:]' in sidecar
    assert "--odom-topic-template /uav{uid}/mosim/diff_swarm/planner_odom_world" in launcher
    assert '"qgc_actual_track_odom_topic_template": "/uav{uid}/mosim/diff_swarm/planner_odom_world"' in packet


def test_fastlio_alignment_consumes_body_cloud_in_both_swarm_frontends() -> None:
    gate = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")

    racer_section = gate.split("start_racer_fastlio_frontend()", 1)[1].split(
        "start_diff_fastlio_frontend()", 1
    )[0]
    diff_section = gate.split("start_diff_fastlio_frontend()", 1)[1].split(
        "wait_topic_sample()", 1
    )[0]

    assert 'cloud_registered_body_topic' in racer_section
    assert '--cloud-input-topic "${raw_cloud_body}"' in racer_section
    assert '--cloud-input-topic "${raw_cloud}"' not in racer_section
    assert 'cloud_registered_body_topic' in diff_section
    assert '--cloud-input-topic "${raw_cloud_body}"' in diff_section
    assert '--cloud-input-topic "${raw_cloud}"' not in diff_section


def test_fastlio_source_declares_world_and_body_cloud_frames() -> None:
    source = (ROOT / "src/perception/fast_lio/src/laserMapping.cpp").read_text(encoding="utf-8")

    world_publish = source.split("void publish_frame_world", 1)[1].split(
        "void publish_frame_body", 1
    )[0]
    body_publish = source.split("void publish_frame_body", 1)[1].split(
        "void publish_effect_world", 1
    )[0]
    assert 'laserCloudmsg.header.frame_id = "camera_init"' in world_publish
    assert 'laserCloudmsg.header.frame_id = "body"' in body_publish


def test_swarm_gate_builds_world_to_local_offsets_for_the_selected_vehicle_count() -> None:
    gate = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")

    assert 'DIFF_SWARM_WORLD_TO_LOCAL_OFFSETS="${START1_X},${START1_Y},0;${START2_X},${START2_Y},0"' in gate
    assert 'if [[ "${UAV_NUM}" == "3" ]]; then' in gate
    assert 'DIFF_SWARM_WORLD_TO_LOCAL_OFFSETS+=";${START3_X},${START3_Y},0"' in gate
    assert '"planner_xy_source": "FAST-LIO aligned PointCloud2 and odometry"' in gate
    assert "json_topic_array()" in gate
    assert '"raw_lidar": $(json_topic_array \'/uav{uid}/livox/lidar\')' in gate
    assert '"goal": $(json_topic_array "${PLANNER_GOAL_TOPIC_TEMPLATE}")' in gate
