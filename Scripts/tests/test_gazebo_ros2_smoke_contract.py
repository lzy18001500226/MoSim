from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_gazebo_ros2_smoke_contract.py"
RUNNER = ROOT / "Scripts" / "gazebo" / "run_sunray150_gazebo_ros2_smoke.sh"
DEPENDENCY_CHECK = ROOT / "Scripts" / "gazebo" / "check_gazebo_ros2_dependencies.sh"
DEPENDENCY_SETUP = ROOT / "Scripts" / "gazebo" / "setup_gazebo_ros2_dependencies.sh"
SCENARIO = ROOT / "Config" / "scenarios" / "system" / "sunray150_gazebo_ros2_smoke.yaml"
LOCAL_MAP = ROOT / "Scripts" / "ros" / "pointcloud_to_local_voxel_map_ros2.py"
FASTLIO_INPUT_ADAPTER = ROOT / "Scripts" / "ros" / "gazebo_fastlio_planner_input_adapter.py"
FASTLIO_IMU_PASSTHROUGH = ROOT / "Scripts" / "ros" / "gazebo_fastlio_imu_passthrough.py"
RUNTIME_STATUS = ROOT / "Scripts" / "quality" / "build_gazebo_ros2_runtime_status.py"
HOVER_HOLD_RUNNER = ROOT / "Scripts" / "gazebo" / "run_sunray150_hover_hold_closed_loop.sh"
HOVER_HOLD_CONTROLLER = ROOT / "Scripts" / "ros" / "gazebo_truth_hover_hold_controller.py"
HOVER_HOLD_EVALUATOR = ROOT / "Scripts" / "quality" / "evaluate_gazebo_hover_hold_closed_loop.py"
FIGURE8_RUNNER = ROOT / "Scripts" / "gazebo" / "run_sunray150_figure8_obstacle_gate.sh"
PLANNER_SETPOINT_TRACKER = ROOT / "Scripts" / "ros" / "gazebo_truth_planner_setpoint_tracker.py"
POSITION_CONTROLLER = ROOT / "Scripts" / "ros" / "gazebo_truth_position_controller.py"


def write_fastlio_planner_input_fixture(tmp_path: Path, *, include_forbidden: bool = False) -> None:
    observed_topics = [
        "/mosim/gazebo/imu",
        "/mosim/gazebo/lidar_points/points",
        "/mosim/fastlio/livox/lidar",
        "/mosim/fastlio/livox/imu",
        "/mosim/spark_fastlio/livox/lidar",
        "/uav1/livox/lidar",
        "/uav1/livox/imu",
        "/uav1/global_points",
        "/mosim/planner/global_points",
        "/uav1/sunray/gazebo_pose",
        "/mosim/planner/odom",
        "/tf_static",
    ]
    if include_forbidden:
        observed_topics.extend(["/position_cmd", "/mosim/sunray150/controller_output"])
    (tmp_path / "ros2_topic_list.txt").write_text("\n".join(observed_topics) + "\n", encoding="utf-8")
    sample_frames = {
        "mosim_gazebo_lidar_points_points": "sunray150_assembled/base_link/mid360_lidar",
        "mosim_gazebo_imu": "sunray150_assembled/base_link/forward_imu",
        "mosim_fastlio_livox_lidar": "sunray150_assembled/base_link/mid360_lidar",
        "mosim_fastlio_livox_imu": "sunray150_assembled/base_link/forward_imu",
        "mosim_spark_fastlio_livox_lidar": "sunray150_assembled/base_link/mid360_lidar",
        "uav1_livox_lidar": "sunray150_assembled/base_link/mid360_lidar",
        "uav1_livox_imu": "sunray150_assembled/base_link/forward_imu",
        "uav1_global_points": "map",
        "mosim_planner_global_points": "map",
        "uav1_sunray_gazebo_pose": "map",
        "mosim_planner_odom": "map",
        "tf_static": "map",
    }
    for key, frame_id in sample_frames.items():
        if key == "mosim_spark_fastlio_livox_lidar":
            sample_text = (
                f"header:\n  frame_id: {frame_id}\n"
                "timebase: 1000000000\n"
                "point_num: 4\n"
                "points:\n"
                "- offset_time: 0\n"
                "  line: 0\n"
                "  x: 1.0\n"
                "  y: 0.0\n"
                "  z: 0.0\n"
                "- offset_time: 33333333\n"
                "  line: 1\n"
                "  x: 1.0\n"
                "  y: 0.1\n"
                "  z: 0.0\n"
                "- offset_time: 66666667\n"
                "  line: 2\n"
                "  x: 1.0\n"
                "  y: 0.2\n"
                "  z: 0.0\n"
                "- offset_time: 100000000\n"
                "  line: 3\n"
                "  x: 1.0\n"
                "  y: 0.3\n"
                "  z: 0.0\n"
            )
        else:
            sample_text = f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n"
        (tmp_path / f"topic_{key}_once.txt").write_text(sample_text, encoding="utf-8")
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_fastlio_livox_lidar", 9.0),
        ("mosim_fastlio_livox_imu", 180.0),
        ("mosim_spark_fastlio_livox_lidar", 9.0),
        ("uav1_global_points", 3.0),
        ("mosim_planner_global_points", 3.0),
        ("uav1_sunray_gazebo_pose", 15.0),
        ("mosim_planner_odom", 15.0),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")
    counts = {
        "lidar_received": 2,
        "fastlio_lidar_published": 2,
        "spark_livox_custom_published": 2,
        "sunray_lidar_published": 2,
        "planner_global_points_published": 2,
        "mosim_planner_global_points_published": 2,
        "planner_odom_published": 2,
        "mosim_planner_odom_published": 2,
        "tf_lookup_failures": 0,
        "frame_mismatch_count": 0,
    }
    (tmp_path / "fastlio_planner_input_adapter.json").write_text(
        json.dumps({"schema": "mosim.fastlio_planner_input_adapter.v1", "status": "active", "counts": counts}),
        encoding="utf-8",
    )
    imu_counts = {
        "imu_received": 360,
        "fastlio_imu_published": 360,
        "sunray_imu_published": 360,
        "frame_mismatch_count": 0,
    }
    (tmp_path / "fastlio_imu_passthrough.json").write_text(
        json.dumps(
            {
                "schema": "mosim.fastlio_imu_passthrough.v1",
                "status": "active",
                "counts": imu_counts,
                "observed_input_average_hz": 180.0,
            }
        ),
        encoding="utf-8",
    )
    forbidden_present = ["/position_cmd", "/mosim/sunray150/controller_output"] if include_forbidden else []
    (tmp_path / "forbidden_topic_presence.json").write_text(
        json.dumps(
            {
                "schema": "mosim.planner_handoff_forbidden_topic_presence.v1",
                "gate_profile": "planner_handoff_without_setpoint_publication",
                "forbidden_topics": [
                    "/mosim/planner/setpoint",
                    "/mosim/planner/setpoint_adapter_status",
                    "/position_cmd",
                    "/mosim/planner/position_cmd",
                    "/mosim/sunray150/controller_output",
                    "/sunray150/gazebo/command/motor_speed",
                ],
                "forbidden_present": forbidden_present,
                "all_forbidden_absent": not forbidden_present,
            }
        ),
        encoding="utf-8",
    )


def write_ego_style_planner_output_fixture(tmp_path: Path, *, include_forbidden: bool = False) -> None:
    write_fastlio_planner_input_fixture(tmp_path, include_forbidden=False)
    observed_topics = (tmp_path / "ros2_topic_list.txt").read_text(encoding="utf-8").splitlines()
    observed_topics.extend(
        [
            "/position_cmd",
            "/mosim/planner/position_cmd",
            "/mosim/planner/setpoint",
            "/mosim/planner/setpoint_adapter_status",
        ]
    )
    if include_forbidden:
        observed_topics.extend(["/mosim/sunray150/controller_output", "/sunray150/gazebo/command/motor_speed"])
    (tmp_path / "ros2_topic_list.txt").write_text("\n".join(observed_topics) + "\n", encoding="utf-8")
    samples = {
        "position_cmd": "header:\n  frame_id: map\nposition:\n  x: 2.0\n  y: 0.0\n  z: 1.2\n",
        "mosim_planner_position_cmd": "header:\n  frame_id: map\nsequence: 1\nframe_id: map\nposition_m:\n- 2.0\n- 0.0\n- 1.2\n",
        "mosim_planner_setpoint": "header:\n  frame_id: map\nsequence: 1\nframe_id: map\nposition_m:\n- 2.0\n- 0.0\n- 1.2\n",
        "mosim_planner_setpoint_adapter_status": "header:\n  frame_id: map\nlast_sequence: 1\naccepted: true\nmode: track\nstale: false\n",
    }
    for key, text in samples.items():
        (tmp_path / f"topic_{key}_once.txt").write_text(text, encoding="utf-8")
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("position_cmd", 5.0),
        ("mosim_planner_position_cmd", 5.0),
        ("mosim_planner_setpoint", 18.0),
        ("mosim_planner_setpoint_adapter_status", 18.0),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")
    report = {
        "schema": "mosim.ego_style_planner_output_gate.v1",
        "status": "planner_output_surface_passed",
        "gate_passed": True,
        "counts": {
            "odom": 20,
            "global_points": 5,
            "position_cmd": 30,
            "mosim_position_cmd": 30,
        },
        "blockers": [],
    }
    (tmp_path / "EGO_STYLE_PLANNER_OUTPUT_GATE.json").write_text(
        json.dumps(report, ensure_ascii=False),
        encoding="utf-8",
    )


def test_gazebo_ros2_smoke_contract_passes() -> None:
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(SCENARIO)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["artifacts"]["world"] == "Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf"
    assert report["artifacts"]["model"] == "Config/gazebo/models/sunray150_assembled/model.sdf"
    assert report["artifacts"]["local_map_script"] == "Scripts/ros/pointcloud_to_local_voxel_map_ros2.py"
    assert report["artifacts"]["map_review_recorder_script"] == "Scripts/ros/record_gazebo_ros2_map_review.py"
    assert report["artifacts"]["fastlio_planner_input_script"] == "Scripts/ros/gazebo_fastlio_planner_input_adapter.py"
    assert report["artifacts"]["spark_fastlio_launch_file"] == "Scripts/ros/mosim_scene_replay/launch/spark_fast_lio_mosim.launch.py"
    assert report["artifacts"]["spark_fastlio_config_path"] == "Config/ros2/mosim_spark_fast_lio_mid360.yaml"
    assert report["artifacts"]["spark_fastlio_recorder_script"] == "Scripts/UE5/record_fastlio_ros2_runtime.py"
    assert report["artifacts"]["controller_adapter_script"] == "Scripts/ros/controller_output_to_gazebo_actuators.py"
    assert report["artifacts"]["hover_hold_runner"] == "Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh"
    assert report["artifacts"]["hover_hold_controller_script"] == "Scripts/ros/gazebo_truth_hover_hold_controller.py"
    assert report["artifacts"]["hover_hold_eval_script"] == "Scripts/quality/evaluate_gazebo_hover_hold_closed_loop.py"
    assert report["artifacts"]["runtime_status_checker"] == "Scripts/quality/build_gazebo_ros2_runtime_status.py"
    assert report["artifacts"]["runtime_status"] == "Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUNTIME_STATUS.json"
    assert "fortress_ignition6" in SCENARIO.read_text(encoding="utf-8")
    world_text = (ROOT / report["artifacts"]["world"]).read_text(encoding="utf-8")
    assert "ignition-gazebo-sensors-system" in world_text
    assert "<render_engine>ogre</render_engine>" in world_text
    assert "<render_engine>ogre2</render_engine>" not in world_text
    assert "gz-sim-sensors-system" not in world_text


def test_gazebo_ros2_runner_has_bounded_claims() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "DRY_RUN" in text
    assert "RUN_GAZEBO" in text
    assert "RUN_LOCAL_MAP" in text
    assert "RUN_MAP_REVIEW_CAPTURE" in text
    assert 'if [[ "${RUN_LOCAL_MAP}" == "1" && "${RUN_STATIC_TF}" != "1" ]]; then' in text
    assert "record_gazebo_ros2_map_review.py" in text
    assert "GAZEBO_ROS2_MAP_REVIEW.json" in (ROOT / "Scripts/ros/record_gazebo_ros2_map_review.py").read_text(encoding="utf-8")
    assert "RUN_RATE_CHECK" in text
    assert "RUN_TF_CHECK" in text
    assert "RUN_FASTLIO_PLANNER_INPUT_ADAPTER" in text
    assert "RUN_SPARK_FASTLIO" in text
    assert "RUN_GAZEBO_TRUTH_POSE" in text
    assert "RUN_PLANT_RESPONSE_EVAL" in text
    assert "RUN_ACTUATOR_BRIDGE" in text
    assert "RUN_CONTROLLER_COMMAND" in text
    assert "RUN_CONTROLLER_OUTPUT_NODE" in text
    assert "RUN_CONTROLLER_OUTPUT_FIXTURE" in text
    assert "RUN_ACTUATOR_COMMAND_CHECK" in text
    assert "RUNTIME_GATE_PROFILE" in text
    assert "GAZEBO_RENDER_ENGINE_SERVER" in text
    assert "START_GAZEBO_PAUSED" in text
    assert "UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND" in text
    assert "gazebo_world_control.json" in text
    assert "gazebo_world_control_unpause.rc" in text
    assert 'local service="/world/${GAZEBO_WORLD_NAME:-yunzong_planning_test_sunray150_assembled}/control"' in text
    assert 'GAZEBO_WORLD_NAME="$(python3' in text
    assert "--start-gazebo-paused" in text
    assert "--unpause-gazebo-after-controller-command" in text
    assert "BUILD_MOSIM_ROS2_MSGS" in text
    assert "MOSIM_ROS2_WS" in text
    assert "CONTROLLER_OUTPUT_NODE_MAX_MESSAGES" in text
    assert "CONTROLLER_COMMAND_RATE_HZ" in text
    assert "CONTROLLER_COMMAND_TIMES" in text
    assert "FASTLIO_PLANNER_INPUT_SCRIPT" in text
    assert "FASTLIO_IMU_PASSTHROUGH_SCRIPT" in text
    assert "SPARK_FASTLIO_SETUP" in text
    assert "SPARK_FASTLIO_LAUNCH_FILE" in text
    assert "SPARK_FASTLIO_RECORDER_SCRIPT" in text


def test_figure8_runner_can_capture_same_run_raw_lidar_and_local_map_review() -> None:
    text = FIGURE8_RUNNER.read_text(encoding="utf-8")
    assert "ENABLE_SAME_RUN_MAP_REVIEW" in text
    assert "MAP_REVIEW_RECORDER_SCRIPT" in text
    assert "LOCAL_MAP_SCRIPT" in text
    assert "ROS_LIDAR_POINTS_TOPIC" in text
    assert "ROS_LOCAL_VOXEL_TOPIC" in text
    assert "ROS_LOCAL_GRID_TOPIC" in text
    assert "PointCloud2@gz.msgs.PointCloudPacked" in text
    assert "static_transform_publisher" in text
    assert "pointcloud_to_local_voxel_map_ros2.py" in text or "ros2.local_map_adapter.script" in text
    assert "record_gazebo_ros2_map_review.py" in text
    assert "GAZEBO_ROS2_MAP_REVIEW.json" in text
    assert "same_run_map_review_enabled" in text
    assert "same_run_map_review_not_passed" in text
    assert "No same-run point-cloud, voxel-map, or occupancy-grid evidence is claimed" in text
    assert 'bridge_args=("${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators")' in text


def test_dependency_check_is_read_only() -> None:
    text = DEPENDENCY_CHECK.read_text(encoding="utf-8")
    assert "DEPENDENCY_STATUS.json" in text
    assert "apt-cache policy" in text
    assert "ros2 pkg prefix" in text
    assert "gz-fortress" in text
    assert "ignition-fortress" in text
    assert "gazebo_sim_cli_command" in text
    assert "missing_command:gazebo_sim_cli(gz_or_ign)" in text
    assert "sudo" not in text
    assert "apt install" not in text
    assert "gz sim -r" not in text
    assert "ign gazebo -r" not in text
    assert "ros2 run ros_gz_bridge parameter_bridge" not in text


def test_dependency_setup_requires_explicit_install_guards() -> None:
    text = DEPENDENCY_SETUP.read_text(encoding="utf-8")
    assert "DEPENDENCY_SETUP_PLAN.json" in text
    assert "DEPENDENCY_SETUP_RESULT.json" in text
    assert 'EXECUTE="${EXECUTE:-0}"' in text
    assert 'MOSIM_ALLOW_WSL_PACKAGE_INSTALL="${MOSIM_ALLOW_WSL_PACKAGE_INSTALL:-0}"' in text
    assert 'if [[ "${EXECUTE}" != "1" || "${MOSIM_ALLOW_WSL_PACKAGE_INSTALL}" != "1" ]]' in text
    assert 'write_plan "plan_only" "not_executed"' in text
    assert 'sudo apt-get update' in text
    assert 'sudo apt-get install -y "${PACKAGE_LIST[@]}"' in text
    assert 'write_plan "execute_requested" "starting" "both_guards_present"' in text
    assert 'write_plan "execute_requested" "starting" "both_guards_present" >' not in text
    assert "gazebo_sim_cli_command" in text
    assert "missing_command:gazebo_sim_cli(gz_or_ign)_after_install" in text


def test_gazebo_ros2_scenario_forbids_overclaims() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    for forbidden_claim in [
        "competition_controller_performance",
        "fast_lio_localization_success",
        "planner_ready",
        "closed_loop",
        "multi_uav_readiness",
    ]:
        assert forbidden_claim in text


def test_gazebo_ros2_scenario_declares_truth_and_frame_boundaries() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "optional_truth_topic_not_in_smoke_gate" in text
    assert "rate_gate_min_fraction" in text
    assert "map_frame: map" in text
    assert "lidar_scan: /mosim/gazebo/lidar_points" in text
    assert "lidar_points: /mosim/gazebo/lidar_points/points" in text
    assert "sensor_frame: sunray150_assembled/base_link/mid360_lidar" in text
    assert "input_cloud_transformed_to_map_with_same_run_tf" in text
    assert "input_frame_policy: transform_input_frame_to_map_with_tf" in text
    assert "runtime_frame_gate: same_run_pointcloud2_header_frame_id_plus_tf_chain_to_map_required" in text


def test_gazebo_ros2_scenario_declares_controller_actuator_adapter() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "source_contract: ControllerOutput" in text
    assert "ros_message: mosim_msgs/msg/ControllerOutput" in text
    assert "message_package: Scripts/ros/mosim_msgs" in text
    assert "adapter_script: Scripts/ros/controller_output_to_gazebo_actuators.py" in text
    assert "node_script: Scripts/ros/controller_output_to_gazebo_actuators_node.py" in text
    assert "fixture_publisher_script: Scripts/ros/publish_controller_output_fixture.py" in text
    assert "ros_type: actuator_msgs/msg/Actuators" in text
    assert "gz_type: gz.msgs.Actuators" in text
    assert "mworks_source_order: [Dronefixed1, Dronefixed2, Dronefixed3, Dronefixed4]" in text
    assert "mworks_spin_command_sign: [1, 1, -1, -1]" in text
    assert "runtime_gate: bounded_ros2_gazebo_actuator_topic_handoff" in text
    assert "node_runtime_gate: bounded_controller_output_node_to_gazebo_actuator_handoff" in text
    assert "runtime_gate_claim: topic_visibility_only_no_flight_no_closed_loop" in text
    assert "controller_output_topic" in text
    assert "required_echoes:" in text


def test_gazebo_ros2_scenario_declares_plant_response_gate() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "single_uav_plant_response_pre_acceptance:" in text
    assert "script: Scripts/quality/evaluate_gazebo_plant_response.py" in text
    assert "output_json: GAZEBO_PLANT_RESPONSE_EVAL.json" in text
    assert "runtime_gate: bounded_single_uav_controller_output_to_gazebo_plant_response_pre_acceptance" in text
    assert "runtime_gate_claim: measurable_gazebo_pose_response_only_no_hover_no_trajectory_no_closed_loop" in text
    assert "gazebo_truth_pose.jsonl" in text
    assert "GAZEBO_TRUTH_POSE_RECORDING.json" in text
    assert "min_z_delta_m: 0.05" in text
    assert "min_3d_delta_m: 0.05" in text
    for forbidden in [
        "hover_success",
        "trajectory_tracking",
        "planner_ready",
        "setpoint_publication",
        "closed_loop",
        "controller_performance",
        "multi_uav_readiness",
    ]:
        assert forbidden in text


def test_gazebo_ros2_scenario_declares_hover_hold_closed_loop_pre_acceptance() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "single_uav_hover_hold_closed_loop_pre_acceptance:" in text
    assert "runner_script: Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh" in text
    assert "controller_script: Scripts/ros/gazebo_truth_hover_hold_controller.py" in text
    assert "eval_script: Scripts/quality/evaluate_gazebo_hover_hold_closed_loop.py" in text
    assert "output_json: GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json" in text
    assert "runtime_gate: bounded_single_uav_gazebo_truth_feedback_hover_hold_pre_acceptance" in text
    assert "runtime_gate_claim: gazebo_truth_feedback_controller_output_actuator_loop_pre_acceptance_no_final_closed_loop_no_controller_performance" in text
    assert "hover_command:" in text
    assert "kp_roll:" in text
    assert "kd_pitch:" in text
    assert "attitude_command_limit: 0.002" in text
    assert "command_min:" in text
    assert "command_max:" in text
    assert "max_xy_distance_m: 1.50" in text
    assert "max_tilt_rad: 0.70" in text
    assert "hover_hold_controller_trace.jsonl" in text
    assert "controller_output_adapter_node.trace.jsonl" in text
    for forbidden in [
        "competition_controller_performance",
        "trajectory_tracking",
        "planner_ready",
        "setpoint_publication",
        "final_closed_loop_acceptance",
        "fast_lio_localization_success",
        "multi_uav_readiness",
    ]:
        assert forbidden in text


def test_hover_hold_runner_has_bounded_runtime_contract() -> None:
    text = HOVER_HOLD_RUNNER.read_text(encoding="utf-8")
    assert "single_uav_hover_hold_closed_loop_pre_acceptance" in text
    assert "ros2 run ros_gz_bridge parameter_bridge" in text
    assert "controller_output_adapter_node.trace.jsonl" in text
    assert "hover_hold_controller.json" in text
    assert "hover_hold_controller_trace.jsonl" in text
    assert "HOVER_EVAL_OUTPUT" in text
    assert "HOVER_KP_ROLL" in text
    assert "HOVER_MAX_XY_DISTANCE_M" in text
    assert "gazebo_world_control.json" in text
    assert "RUN_MANIFEST.json" in text
    assert "RUNTIME_STATUS.json" in text
    assert "BLOCKER.json" in text
    assert "bounded single-UAV Gazebo truth-feedback hover-hold pre-acceptance only" in text
    assert "multi-UAV readiness" in text
    assert "final closed_loop" in text


def test_hover_hold_controller_dry_run() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(HOVER_HOLD_CONTROLLER),
            "--dry-run",
            "--target-altitude-m",
            "1.2",
            "--hover-command",
            "0.05485",
            "--command-min",
            "0.05250",
            "--command-max",
            "0.05750",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema"] == "mosim.gazebo_truth_hover_hold_controller.dry_run.v1"
    assert report["status"] == "ready"
    assert report["command_bounds"] == [0.0525, 0.0575]
    assert "multi-UAV readiness" in " ".join(report["claim_boundary"])


def test_figure8_runner_passes_tracker_control_parameters_from_scenario() -> None:
    text = FIGURE8_RUNNER.read_text(encoding="utf-8")
    for token in [
        "TRACKER_CONFIG_NODE",
        "TRACKER_HOVER_COMMAND",
        "TRACKER_KP_X",
        "TRACKER_KD_X",
        "TRACKER_KA_X",
        "TRACKER_KP_Y",
        "TRACKER_KD_Y",
        "TRACKER_KA_Y",
        "TRACKER_KP_Z",
        "TRACKER_KD_Z",
        "TRACKER_KI_Z",
        "TRACKER_KP_ROLL",
        "TRACKER_KD_ROLL",
        "TRACKER_KP_PITCH",
        "TRACKER_KD_PITCH",
        "TRACKER_ATTITUDE_COMMAND_LIMIT",
        "TRACKER_COMMAND_MIN",
        "TRACKER_COMMAND_MAX",
        "TRACKER_HOVER_COMMAND_OVERRIDE",
        "TRACKER_KA_X_OVERRIDE",
        "TRACKER_KA_Y_OVERRIDE",
        "TRACKER_KP_Z_OVERRIDE",
        "TRACKER_KD_Z_OVERRIDE",
        "TRACKER_KI_Z_OVERRIDE",
        "TRACKER_ATTITUDE_COMMAND_LIMIT_OVERRIDE",
        "TRACKER_COMMAND_MAX_OVERRIDE",
        "TRACKER_TAKEOFF_XY_ENABLE_ALTITUDE_M",
        "TRACKER_TAKEOFF_STABLE_Z_ERROR_M",
        "TRACKER_TAKEOFF_STABLE_S",
        "TRACKER_XY_ERROR_LIMIT_M",
        "TRACKER_XY_VELOCITY_ERROR_LIMIT_MPS",
        "TRACKER_INTEGRAL_LIMIT_M_S",
        "--takeoff-xy-enable-altitude-m",
        "--takeoff-stable-z-error-m",
        "--takeoff-stable-s",
        "--xy-error-limit-m",
        "--xy-velocity-error-limit-mps",
        "--integral-limit-m-s",
        "FIGURE_DURATION_S_OVERRIDE",
        "FIGURE_PERIOD_S_OVERRIDE",
        "FIGURE_X_AMP_OVERRIDE",
        "FIGURE_Y_AMP_OVERRIDE",
        "FIGURE_X_OFFSET_OVERRIDE",
        "FIGURE_Y_OFFSET_OVERRIDE",
        "FIGURE_ALTITUDE_OVERRIDE",
        "FIGURE_START_DELAY_S_OVERRIDE",
        "TRACKER_DURATION_S_OVERRIDE",
        "CONTROLLER_FIXTURE_SCRIPT",
        "pre_unpause_hover_fixture",
        "unpause_gazebo_world",
        "gazebo_world_control.json",
        "ign topic -e -t",
        "--hover-command",
        "--kp-z",
        "--ka-x",
        "--ka-y",
        "--ki-z",
        "--command-min",
        "--command-max",
        "--x-offset-m",
        "--y-offset-m",
        "--start-delay-s",
    ]:
        assert token in text
    assert "--internal-figure8-reference" not in text
    assert "tracker_reference_mode\": \"external_planner_setpoint\"" in text
    assert "TRACKER_TRUTH_INPUT_MODE" in text
    assert 'TRACKER_TRUTH_INPUT_MODE="${TRACKER_TRUTH_INPUT_MODE_OVERRIDE:-stream}"' in text
    assert "--poll-command ign" in text
    assert "TRACKER_HOLD_LAST_SETPOINT_WHEN_TRUTH_BUFFERED" in text
    assert "--hold-last-setpoint-when-truth-buffered" in text


def test_gazebo_truth_position_controller_dry_run_requires_external_setpoint() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(POSITION_CONTROLLER),
            "--dry-run",
            "--hover-command",
            "0.05520",
            "--command-min",
            "0.05350",
            "--command-max",
            "0.05635",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema"] == "mosim.gazebo_truth_position_controller.dry_run.v1"
    assert report["required_reference_mode"] == "external_planner_setpoint"
    assert "no internal figure-8 reference" in " ".join(report["claim_boundary"])
    assert "multi-UAV readiness" in " ".join(report["claim_boundary"])


def test_gazebo_truth_position_controller_axis_probe_signs_are_encoded() -> None:
    text = POSITION_CONTROLLER.read_text(encoding="utf-8")
    assert "current motor/mixer path" in text
    assert "reduces positive world-frame X/Y error with negative" in text
    assert "xy_scale * (-desired_y)" in text
    assert "xy_scale * (-desired_x)" in text


def test_gazebo_truth_position_controller_stale_setpoint_uses_sim_time_stamp() -> None:
    text = POSITION_CONTROLLER.read_text(encoding="utf-8")
    assert "latest_setpoint_stamp_s" in text
    assert "sample_time - setpoint_stamp_s" in text
    assert "setpoint_age_source" in text
    assert "sim_time_header_stamp" in text


def test_planner_setpoint_tracker_duration_uses_first_header_time() -> None:
    text = PLANNER_SETPOINT_TRACKER.read_text(encoding="utf-8")
    assert "sample_time - first_header_time >= args.duration_s" in text
    assert "last_header_time - first_header_time >= args.duration_s" not in text


def test_planner_setpoint_tracker_axis_probe_signs_are_encoded() -> None:
    text = PLANNER_SETPOINT_TRACKER.read_text(encoding="utf-8")
    assert "positive roll" in text
    assert "toward -Y" in text
    assert "pre-acceptance plant traces" in text
    assert "xy_control_scale" in text
    assert "control_phase" in text
    assert "takeoff_altitude_hold" in text
    assert "altitude_recovery" in text
    assert "-args.kp_y * xy_error_for_control[1] - args.kd_y * xy_velocity_error_for_control[1]" in text
    assert "-args.kp_x * xy_error_for_control[0] - args.kd_x * xy_velocity_error_for_control[0]" in text


def test_gazebo_ros2_scenario_declares_fastlio_planner_input_adapter() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "fastlio_planner_input_adapter:" in text
    assert "script: Scripts/ros/gazebo_fastlio_planner_input_adapter.py" in text
    assert "fastlio_lidar_topic: /mosim/fastlio/livox/lidar" in text
    assert "fastlio_imu_topic: /mosim/fastlio/livox/imu" in text
    assert "spark_livox_custom_topic: /mosim/spark_fastlio/livox/lidar" in text
    assert "spark_livox_scan_lines: 4" in text
    assert "spark_livox_scan_rate_hz: 10" in text
    assert "spark_livox_line_policy: source_pointcloud_row_bucketed_to_scan_lines" in text
    assert "spark_livox_offset_time_policy: retained_point_ordinal_spread_over_one_scan_period_nanoseconds" in text
    assert "spark_livox_point_count_field: point_num" in text
    assert "sunray_lidar_topic: /uav1/livox/lidar" in text
    assert "sunray_imu_topic: /uav1/livox/imu" in text
    assert "planner_global_points_topic: /uav1/global_points" in text
    assert "planner_odom_topic: /uav1/sunray/gazebo_pose" in text
    assert "runtime_gate: bounded_fastlio_planner_input_surface_only" in text
    assert "runtime_gate_claim: topic_frame_rate_input_shape_only_no_fastlio_no_planner_ready_no_setpoint" in text
    for forbidden in [
        "fast_lio_localization_success",
        "ego_planner_runtime_success",
        "planner_ready",
        "setpoint_publication",
        "command_acknowledgement",
        "closed_loop",
    ]:
        assert forbidden in text


def test_gazebo_ros2_scenario_declares_planner_handoff_without_setpoint_gate() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "planner_handoff_without_setpoint_publication:" in text
    assert "runtime_gate: bounded_planner_handoff_without_setpoint_publication" in text
    assert "runtime_gate_claim: planner_input_handoff_topics_only_no_setpoint_no_controller_no_actuator_no_closed_loop" in text
    assert "forbidden_topic_evidence: forbidden_topic_presence.json" in text
    for required in [
        "/uav1/global_points",
        "/mosim/planner/global_points",
        "/uav1/sunray/gazebo_pose",
        "/mosim/planner/odom",
    ]:
        assert required in text
    for forbidden in [
        "/mosim/planner/setpoint",
        "/mosim/planner/setpoint_adapter_status",
        "/position_cmd",
        "/mosim/planner/position_cmd",
        "/mosim/sunray150/controller_output",
        "/sunray150/gazebo/command/motor_speed",
    ]:
        assert forbidden in text


def test_gazebo_ros2_scenario_declares_spark_fastlio_runtime_gate() -> None:
    text = SCENARIO.read_text(encoding="utf-8")
    assert "spark_fastlio_runtime:" in text
    assert "package: spark_fast_lio" in text
    assert "executable: spark_lio_mapping" in text
    assert "workspace_setup: Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash" in text
    assert "launch_file: Scripts/ros/mosim_scene_replay/launch/spark_fast_lio_mosim.launch.py" in text
    assert "config_path: Config/ros2/mosim_spark_fast_lio_mid360.yaml" in text
    assert "recorder_script: Scripts/UE5/record_fastlio_ros2_runtime.py" in text
    assert "input_lidar_topic: /mosim/spark_fastlio/livox/lidar" in text
    assert "input_imu_topic: /mosim/fastlio/livox/imu" in text
    assert "output_registered_cloud_topic: /cloud_registered" in text
    assert "output_odometry_topic: /odometry" in text
    assert "output_path_topic: /path" in text
    assert "map_frame: map" in text
    assert "base_frame: sunray150_assembled/base_link" in text
    assert "visualization_frame: base" in text
    assert "lidar_frame: sunray150_assembled/base_link/mid360_lidar" in text
    assert "imu_frame: sunray150_assembled/base_link/forward_imu" in text
    assert "runtime_gate: bounded_spark_fastlio_output_surface" in text
    assert "runtime_gate_claim: real_spark_fastlio_output_topics_recorded_no_truth_quality_no_planner_no_setpoint" in text
    for forbidden in [
        "fast_lio_localization_quality",
        "planner_ready",
        "setpoint_publication",
        "command_acknowledgement",
        "closed_loop",
    ]:
        assert forbidden in text


def test_gazebo_model_declares_four_motor_plugins() -> None:
    text = (ROOT / "Config/gazebo/models/sunray150_assembled/model.sdf").read_text(encoding="utf-8")
    assert text.count('name="gz::sim::systems::MulticopterMotorModel"') == 4
    for index in range(4):
        assert f'<link name="rotor_{index}">' in text
        assert f'<joint name="rotor_{index}_joint" type="revolute">' in text
        assert f"<motorNumber>{index}</motorNumber>" in text
        assert f"<actuator_number>{index}</actuator_number>" in text
        assert f"<motorSpeedPubTopic>motor_speed/{index}</motorSpeedPubTopic>" in text
    assert "<commandSubTopic>gazebo/command/motor_speed</commandSubTopic>" in text


def test_gazebo_ros2_runner_uses_scenario_controller_id() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert 'CONTROLLER_ID="$(python3 - <<PY' in text
    assert '"controller_id": "${CONTROLLER_ID}"' in text
    assert '"controller_id": "behavior_equivalent_ros2_controller_node_pending"' not in text


def test_pointcloud_to_local_voxel_map_dry_run_contract() -> None:
    completed = subprocess.run(
        [sys.executable, str(LOCAL_MAP), "--dry-run"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema"] == "mosim.pointcloud_to_local_voxel_map_dryrun.v1"
    assert report["outputs"]["local_voxels"].startswith("sensor_msgs/msg/PointCloud2")
    assert report["outputs"]["local_2d_grid"].startswith("nav_msgs/msg/OccupancyGrid")
    assert report["input_frame_policy"] == "require_input_frame_equals_map_frame"
    assert report["expected_input_frame"] == "map"
    assert report["local_map_center_source"] == "map_origin"
    assert any("no FAST-LIO" in item for item in report["claim_boundary"])
    assert any("header.frame_id" in item for item in report["claim_boundary"])


def test_fastlio_planner_input_adapter_dry_run_contract() -> None:
    completed = subprocess.run(
        [sys.executable, str(FASTLIO_INPUT_ADAPTER), "--dry-run"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema"] == "mosim.fastlio_planner_input_adapter.dryrun.v1"
    assert report["outputs"]["sunray_lidar"] == "/uav1/livox/lidar"
    assert report["outputs"]["spark_livox_custom"] == "/mosim/spark_fastlio/livox/lidar"
    assert report["outputs"]["planner_odom"] == "/uav1/sunray/gazebo_pose"
    assert report["frames"]["sensor_frame"] == "sunray150_assembled/base_link/mid360_lidar"
    assert report["livox_custom_shape"]["spark_livox_scan_lines"] == 4
    assert report["livox_custom_shape"]["spark_livox_scan_rate_hz"] == 10.0
    assert report["livox_custom_shape"]["line_policy"] == "source_pointcloud_row_bucketed_to_scan_lines"
    assert "planner_ready" in " ".join(report["claim_boundary"])
    assert "closed_loop" in " ".join(report["claim_boundary"])


def test_fastlio_planner_input_adapter_dry_run_can_disable_spark_livox_custom_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(FASTLIO_INPUT_ADAPTER),
            "--dry-run",
            "--disable-spark-livox-custom-output",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema"] == "mosim.fastlio_planner_input_adapter.dryrun.v1"
    assert report["outputs"]["spark_livox_custom"] is None
    assert report["livox_custom_shape"]["enabled"] is False


def test_fastlio_imu_passthrough_dry_run_contract() -> None:
    completed = subprocess.run(
        [sys.executable, str(FASTLIO_IMU_PASSTHROUGH), "--dry-run"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema"] == "mosim.fastlio_imu_passthrough.dryrun.v1"
    assert report["outputs"]["fastlio_imu"] == "/mosim/fastlio/livox/imu"
    assert report["outputs"]["sunray_imu"] == "/uav1/livox/imu"
    assert report["frames"]["imu_frame"] == "sunray150_assembled/base_link/forward_imu"
    claim_boundary = " ".join(report["claim_boundary"])
    assert "not LiDAR-gated" in claim_boundary
    assert "closed_loop" in claim_boundary


def test_runtime_status_gate_blocks_without_runtime_evidence(tmp_path: Path) -> None:
    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "runtime_smoke_blocked"
    assert "gazebo_process_not_alive" in report["blockers"]
    assert any(item.startswith("missing_topic_sample:lidar_points") for item in report["blockers"])
    assert "topic_rates" in report
    assert "planner readiness" in " ".join(report["claim_boundary"])


def test_runtime_status_accepts_ros2_hz_timeout_when_average_rate_exists(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n"
        "  transform:\n"
        "    translation:\n"
        "      x: 0.0\n"
        "      y: 0.0\n"
        "      z: 1.2\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "true",
            "--run-ros2-bridge",
            "true",
            "--run-local-map",
            "true",
            "--run-topic-check",
            "true",
            "--run-rate-check",
            "true",
            "--run-tf-check",
            "true",
            "--gazebo-alive",
            "true",
            "--bridge-alive",
            "true",
            "--local-map-alive",
            "true",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["blockers"] == []
    assert report["topic_rates"]["imu"]["rate_returncode"] == 124
    assert report["topic_rates"]["imu"]["rate_recorded"] is True
    assert "timeout_returncode_accepted" in report["topic_rates"]["imu"]["rate_returncode_note"]
    assert report["topic_samples"]["lidar_points"]["frame_id"] == "sunray150_assembled/base_link/mid360_lidar"
    assert report["topic_samples"]["lidar_points"]["sample_point_count"] == 1
    assert report["topic_samples"]["local_occupancy_voxels"]["sample_point_count"] == 1
    assert report["local_map_frame_boundary"]["expected_input_frame"] == "sunray150_assembled/base_link/mid360_lidar"
    assert report["tf_chain"]["chain_to_map_verified"] is True


def test_runtime_status_accepts_sensor_header_rate_when_wall_rate_is_slow(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 3.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")
    (tmp_path / "topic_mosim_gazebo_lidar_points_points_header_rate.json").write_text(
        json.dumps(
            {
                "schema": "mosim.ros2_topic_header_rate.v1",
                "status": "recorded",
                "topic": "/mosim/gazebo/lidar_points/points",
                "type": "sensor_msgs/msg/PointCloud2",
                "header_stamp_rate": {
                    "sample_count": 40,
                    "duration_s": 3.9,
                    "average_rate_hz": 10.0,
                    "negative_delta_count": 0,
                },
                "receive_wall_rate": {
                    "sample_count": 40,
                    "duration_s": 12.0,
                    "average_rate_hz": 3.25,
                    "negative_delta_count": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "true",
            "--run-ros2-bridge",
            "true",
            "--run-local-map",
            "true",
            "--run-topic-check",
            "true",
            "--run-rate-check",
            "true",
            "--run-tf-check",
            "true",
            "--gazebo-alive",
            "true",
            "--bridge-alive",
            "true",
            "--local-map-alive",
            "true",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    lidar_rate = report["topic_rates"]["lidar_points"]
    assert lidar_rate["average_rate_hz"] == 3.0
    assert lidar_rate["header_stamp_average_rate_hz"] == 10.0
    assert any("header_stamp_rate_passed" in item for item in report["warnings"])


def test_runtime_status_keeps_sample_evidence_when_topic_list_snapshot_is_empty(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text("", encoding="utf-8")
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "true",
            "--run-ros2-bridge",
            "true",
            "--run-local-map",
            "true",
            "--run-topic-check",
            "true",
            "--run-rate-check",
            "true",
            "--run-tf-check",
            "true",
            "--gazebo-alive",
            "true",
            "--bridge-alive",
            "true",
            "--local-map-alive",
            "true",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["topic_list"]["snapshot_recorded"] is False
    assert report["topic_list"]["observed_count"] == 0
    assert "/mosim/gazebo/lidar_points/points" in report["topic_list"]["observed_by_sample_or_rate"]
    assert report["topic_samples"]["lidar_points"]["observed"] is True
    assert any("topic_list_snapshot_empty_but_samples_or_rates_recorded" in item for item in report["warnings"])


def test_runtime_status_accepts_lidar_sample_from_map_review_recorder(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_mosim_gazebo_lidar_points_points_once.rc").write_text("124\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")
    map_review_dir = tmp_path / "map_review"
    map_review_dir.mkdir()
    (map_review_dir / "GAZEBO_ROS2_MAP_REVIEW.json").write_text(
        json.dumps(
            {
                "gate_passed": True,
                "artifacts": {
                    "lidar_pointcloud": {
                        "topic": "/mosim/gazebo/lidar_points/points",
                        "frame_id": "sunray150_assembled/base_link/mid360_lidar",
                        "width": 360,
                        "height": 32,
                        "raw_point_count": 11520,
                        "finite_point_count": 7000,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--local-map-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["blockers"] == []
    lidar_sample = report["topic_samples"]["lidar_points"]
    assert lidar_sample["sample_recorded_by_map_review"] is True
    assert lidar_sample["sample_point_count"] == 11520


def test_runtime_status_accepts_map_review_grid_fallback(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "sunray150_assembled/base_link/forward_imu"),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_local_occupancy_voxels", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    map_review_dir = tmp_path / "map_review"
    map_review_dir.mkdir(parents=True, exist_ok=True)
    (map_review_dir / "GAZEBO_ROS2_MAP_REVIEW.json").write_text(
        json.dumps(
            {
                "gate_passed": True,
                "artifacts": {
                    "lidar_pointcloud": {
                        "topic": "/mosim/gazebo/lidar_points/points",
                        "frame_id": "sunray150_assembled/base_link/mid360_lidar",
                        "width": 20,
                        "height": 10,
                        "raw_point_count": 200,
                        "finite_point_count": 180,
                    },
                    "local_occupancy_voxels": {
                        "topic": "/mosim/local_occupancy_voxels",
                        "frame_id": "map",
                        "width": 42,
                        "height": 1,
                        "raw_point_count": 42,
                        "finite_point_count": 42,
                    },
                    "local_occupancy_grid": {
                        "topic": "/mosim/local_occupancy_grid",
                        "frame_id": "map",
                        "width": 120,
                        "height": 120,
                        "occupied_count": 88,
                        "free_count": 999,
                        "unknown_count": 333,
                    },
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "runtime_status.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--local-map-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    grid_sample = report["topic_samples"]["local_occupancy_grid"]
    assert grid_sample["observed"] is True
    assert grid_sample["sample_recorded_by_map_review"] is True
    assert grid_sample["sample_point_count"] == 120 * 120


def test_runtime_status_accepts_bounded_actuator_command_handoff(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/sunray150/gazebo/command/motor_speed",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    velocity = [4000.0, 4000.0, 4000.0, 4000.0]
    (tmp_path / "controller_actuator_command.json").write_text(
        json.dumps({"status": "actuator_payload_ready", "velocity": velocity}),
        encoding="utf-8",
    )
    (tmp_path / "controller_command.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity:\n- 4000.0\n- 4000.0\n- 4000.0\n- 4000.0\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity: 4000\nvelocity: 4000\nvelocity: 4000\nvelocity: 4000\n",
        encoding="utf-8",
    )
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-actuator-command-check",
            "1",
            "--gate-profile",
            "actuator_handoff",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--local-map-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_profile"] == "actuator_handoff"
    assert report["actuator_command"]["requested"] is True
    assert report["actuator_command"]["ros_velocity_matches_expected"] is True
    assert report["actuator_command"]["gz_velocity_matches_expected"] is True
    assert report["actuator_command"]["ros_echo"]["velocity"] == velocity
    assert report["actuator_command"]["gz_echo"]["velocity"] == velocity
    assert "bounded ROS2/Gazebo actuator topic visibility" in " ".join(report["claim_boundary"])


def test_runtime_status_accepts_controller_output_node_handoff(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/sunray150/controller_output",
                "/sunray150/gazebo/command/motor_speed",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_mosim_sunray150_controller_output_once.txt").write_text(
        "sequence: 1\n"
        "vehicle_id: sunray150\n"
        "command_type: normalized_motor_speed\n"
        "command:\n"
        "- 0.5\n"
        "- 0.5\n"
        "- 0.5\n"
        "- 0.5\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_mosim_sunray150_controller_output_once.rc").write_text("0\n", encoding="utf-8")
    velocity = [4000.0, 4000.0, 4000.0, 4000.0]
    (tmp_path / "controller_output_fixture.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "controller_output_adapter_node.json").write_text(
        json.dumps(
            {
                "status": "published",
                "input_command_type": "normalized_motor_speed",
                "input_command": [0.5, 0.5, 0.5, 0.5],
                "velocity": velocity,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "controller_output_node.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity:\n- 4000.0\n- 4000.0\n- 4000.0\n- 4000.0\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity: 4000\nvelocity: 4000\nvelocity: 4000\nvelocity: 4000\n",
        encoding="utf-8",
    )
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-actuator-command-check",
            "1",
            "--run-controller-output-node",
            "1",
            "--run-controller-output-fixture",
            "1",
            "--gate-profile",
            "controller_output_node_handoff",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_profile"] == "controller_output_node_handoff"
    assert report["controller_output"]["sample_recorded"] is True
    assert report["controller_output"]["node_status"] == "published"
    assert report["controller_output"]["node_velocity"] == velocity
    assert report["actuator_command"]["ros_velocity_matches_expected"] is True
    assert report["actuator_command"]["gz_velocity_matches_expected"] is True
    assert "ControllerOutput topic to Actuators topic visibility" in " ".join(report["claim_boundary"])


def write_command_ack_fixture(tmp_path: Path, *, stale_guard: bool = True) -> None:
    velocity = [4000.0, 4000.0, 4000.0, 4000.0]
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/sunray150/controller_output",
                "/sunray150/gazebo/command/motor_speed",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_mosim_sunray150_controller_output_once.txt").write_text(
        "sequence: 1\n"
        "vehicle_id: sunray150\n"
        "command_type: normalized_motor_speed\n"
        "command:\n"
        "- 0.5\n"
        "- 0.5\n"
        "- 0.5\n"
        "- 0.5\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_mosim_sunray150_controller_output_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "controller_output_fixture.json").write_text(
        json.dumps({"status": "published", "published_count": 5}),
        encoding="utf-8",
    )
    (tmp_path / "controller_output_fixture.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "controller_output_adapter_node.json").write_text(
        json.dumps(
            {
                "status": "published",
                "input_sequence": 1,
                "input_vehicle_id": "sunray150",
                "input_command_type": "normalized_motor_speed",
                "input_command": [0.5, 0.5, 0.5, 0.5],
                "velocity": velocity,
                "command_age_s": 0.25,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "controller_output_node.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity:\n- 4000.0\n- 4000.0\n- 4000.0\n- 4000.0\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity: 4000\nvelocity: 4000\nvelocity: 4000\nvelocity: 4000\n",
        encoding="utf-8",
    )
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")
    stale_negative_path = {
        "report_status": "blocked",
        "error": "AdapterError: command age 10.000s exceeds max_command_age_s 2.000s",
        "blocked_as_expected": stale_guard,
        "report": "stale_controller_output_report.json",
    }
    (tmp_path / "command_ack_guard_report.json").write_text(
        json.dumps(
            {
                "schema": "mosim.command_ack_guard.v1",
                "gate_profile": "command_acknowledgement_without_closed_loop",
                "positive_path": {
                    "fixture_status": "published",
                    "node_status": "published",
                    "node_sequence": 1,
                    "node_vehicle_id": "sunray150",
                    "node_command_age_s": 0.25,
                    "node_velocity": velocity,
                },
                "stale_negative_path": stale_negative_path,
            }
        ),
        encoding="utf-8",
    )


def write_plant_response_fixture(tmp_path: Path, *, moving: bool = True) -> None:
    write_command_ack_fixture(tmp_path)
    samples = []
    for index in range(30):
        z = 0.004 * index if moving else 0.0
        samples.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": index,
                "time": round(index * 0.1, 6),
                "frame_id": "world",
                "source_topic": "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info",
                "model_name": "sunray150",
                "position_m": [0.0, 0.0, round(z, 6)],
                "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
        )
    (tmp_path / "gazebo_truth_pose.jsonl").write_text(
        "\n".join(json.dumps(item) for item in samples) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "GAZEBO_TRUTH_POSE_RECORDING.json").write_text(
        json.dumps(
            {
                "schema": "mosim.gazebo_pose_truth_recording.v1",
                "status": "recorded",
                "topic": "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info",
                "model_name": "sunray150",
                "frame_id": "world",
                "count": len(samples),
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "gazebo_truth_pose_recorder.rc").write_text("0\n", encoding="utf-8")
    plant_blockers = [] if moving else ["plant_z_response_below_min:0.000000<0.050000"]
    (tmp_path / "GAZEBO_PLANT_RESPONSE_EVAL.json").write_text(
        json.dumps(
            {
                "schema": "mosim.gazebo_plant_response_eval.v1",
                "status": "passed" if moving else "blocked",
                "gate_passed": moving,
                "blockers": plant_blockers,
                "warnings": [],
                "truth_recording": {
                    "summary_status": "recorded",
                    "summary_count": len(samples),
                    "valid_sample_count": len(samples),
                    "duration_s": 2.9,
                    "model_name": "sunray150",
                    "frame_id": "world",
                },
                "plant_response": {
                    "z_delta_m": 0.09 if moving else 0.0,
                    "max_3d_delta_m": 0.116 if moving else 0.0,
                    "max_z_delta_m": 0.116 if moving else 0.0,
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "gazebo_plant_response_eval.rc").write_text("0\n" if moving else "1\n", encoding="utf-8")


def run_runtime_status(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    output = tmp_path / "RUNTIME_STATUS.json"
    return subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_runtime_status_accepts_command_acknowledgement_without_closed_loop(tmp_path: Path) -> None:
    write_command_ack_fixture(tmp_path)
    completed = run_runtime_status(
        tmp_path,
        "--run-gazebo",
        "1",
        "--run-ros2-bridge",
        "1",
        "--run-actuator-command-check",
        "1",
        "--run-controller-output-node",
        "1",
        "--run-controller-output-fixture",
        "1",
        "--run-command-ack-guard",
        "1",
        "--gate-profile",
        "command_acknowledgement_without_closed_loop",
        "--gazebo-alive",
        "1",
        "--bridge-alive",
        "1",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads((tmp_path / "RUNTIME_STATUS.json").read_text(encoding="utf-8"))
    assert report["gate_profile"] == "command_acknowledgement_without_closed_loop"
    assert report["command_acknowledgement_without_closed_loop"]["guard_report_recorded"] is True
    assert report["command_acknowledgement_without_closed_loop"]["stale_negative_path"]["blocked_as_expected"] is True
    assert report["actuator_command"]["ros_velocity_matches_expected"] is True
    assert report["actuator_command"]["gz_velocity_matches_expected"] is True
    assert report["blockers"] == []
    assert "stale-command rejection" in " ".join(report["claim_boundary"])


def test_runtime_status_blocks_command_ack_without_stale_guard(tmp_path: Path) -> None:
    write_command_ack_fixture(tmp_path, stale_guard=False)
    completed = run_runtime_status(
        tmp_path,
        "--run-gazebo",
        "1",
        "--run-ros2-bridge",
        "1",
        "--run-actuator-command-check",
        "1",
        "--run-controller-output-node",
        "1",
        "--run-controller-output-fixture",
        "1",
        "--run-command-ack-guard",
        "1",
        "--gate-profile",
        "command_acknowledgement_without_closed_loop",
        "--gazebo-alive",
        "1",
        "--bridge-alive",
        "1",
    )
    assert completed.returncode == 1
    report = json.loads((tmp_path / "RUNTIME_STATUS.json").read_text(encoding="utf-8"))
    assert "command_ack_stale_negative_guard_missing" in report["blockers"]


def test_runtime_status_accepts_single_uav_plant_response_pre_acceptance(tmp_path: Path) -> None:
    write_plant_response_fixture(tmp_path)
    completed = run_runtime_status(
        tmp_path,
        "--run-gazebo",
        "1",
        "--run-ros2-bridge",
        "1",
        "--run-actuator-command-check",
        "1",
        "--run-controller-output-node",
        "1",
        "--run-controller-output-fixture",
        "1",
        "--run-gazebo-truth-pose",
        "1",
        "--run-plant-response-eval",
        "1",
        "--gate-profile",
        "single_uav_plant_response_pre_acceptance",
        "--gazebo-alive",
        "1",
        "--bridge-alive",
        "1",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads((tmp_path / "RUNTIME_STATUS.json").read_text(encoding="utf-8"))
    assert report["gate_profile"] == "single_uav_plant_response_pre_acceptance"
    assert report["plant_response_pre_acceptance"]["gate_passed"] is True
    assert report["plant_response_pre_acceptance"]["truth_recording_count"] == 30
    assert report["actuator_command"]["ros_velocity_matches_expected"] is True
    assert report["actuator_command"]["gz_velocity_matches_expected"] is True
    assert "measurable Gazebo truth-pose response" in " ".join(report["claim_boundary"])
    assert "closed_loop" in " ".join(report["claim_boundary"])


def test_runtime_status_blocks_single_uav_plant_response_without_motion(tmp_path: Path) -> None:
    write_plant_response_fixture(tmp_path, moving=False)
    completed = run_runtime_status(
        tmp_path,
        "--run-gazebo",
        "1",
        "--run-ros2-bridge",
        "1",
        "--run-actuator-command-check",
        "1",
        "--run-controller-output-node",
        "1",
        "--run-controller-output-fixture",
        "1",
        "--run-gazebo-truth-pose",
        "1",
        "--run-plant-response-eval",
        "1",
        "--gate-profile",
        "single_uav_plant_response_pre_acceptance",
        "--gazebo-alive",
        "1",
        "--bridge-alive",
        "1",
    )
    assert completed.returncode == 1
    report = json.loads((tmp_path / "RUNTIME_STATUS.json").read_text(encoding="utf-8"))
    assert "plant_response_gate_not_passed" in report["blockers"]
    assert any(item.startswith("plant_response:plant_z_response_below_min") for item in report["blockers"])


def test_runtime_status_accepts_fastlio_planner_input_gate(tmp_path: Path) -> None:
    observed_topics = [
        "/mosim/gazebo/imu",
        "/mosim/gazebo/lidar_points/points",
        "/mosim/fastlio/livox/lidar",
        "/mosim/fastlio/livox/imu",
        "/mosim/spark_fastlio/livox/lidar",
        "/uav1/livox/lidar",
        "/uav1/livox/imu",
        "/uav1/global_points",
        "/mosim/planner/global_points",
        "/uav1/sunray/gazebo_pose",
        "/mosim/planner/odom",
        "/tf_static",
    ]
    (tmp_path / "ros2_topic_list.txt").write_text("\n".join(observed_topics) + "\n", encoding="utf-8")
    sample_frames = {
        "mosim_gazebo_lidar_points_points": "sunray150_assembled/base_link/mid360_lidar",
        "mosim_gazebo_imu": "sunray150_assembled/base_link/forward_imu",
        "mosim_fastlio_livox_lidar": "sunray150_assembled/base_link/mid360_lidar",
        "mosim_fastlio_livox_imu": "sunray150_assembled/base_link/forward_imu",
        "mosim_spark_fastlio_livox_lidar": "sunray150_assembled/base_link/mid360_lidar",
        "uav1_livox_lidar": "sunray150_assembled/base_link/mid360_lidar",
        "uav1_livox_imu": "sunray150_assembled/base_link/forward_imu",
        "uav1_global_points": "map",
        "mosim_planner_global_points": "map",
        "uav1_sunray_gazebo_pose": "map",
        "mosim_planner_odom": "map",
        "tf_static": "map",
    }
    for key, frame_id in sample_frames.items():
        if key == "mosim_spark_fastlio_livox_lidar":
            sample_text = (
                f"header:\n  frame_id: {frame_id}\n"
                "timebase: 1000000000\n"
                "point_num: 4\n"
                "points:\n"
                "- offset_time: 0\n"
                "  line: 0\n"
                "  x: 1.0\n"
                "  y: 0.0\n"
                "  z: 0.0\n"
                "- offset_time: 33333333\n"
                "  line: 1\n"
                "  x: 1.0\n"
                "  y: 0.1\n"
                "  z: 0.0\n"
                "- offset_time: 66666667\n"
                "  line: 2\n"
                "  x: 1.0\n"
                "  y: 0.2\n"
                "  z: 0.0\n"
                "- offset_time: 100000000\n"
                "  line: 3\n"
                "  x: 1.0\n"
                "  y: 0.3\n"
                "  z: 0.0\n"
            )
        else:
            sample_text = f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n"
        (tmp_path / f"topic_{key}_once.txt").write_text(sample_text, encoding="utf-8")
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_fastlio_livox_lidar", 9.0),
        ("mosim_fastlio_livox_imu", 180.0),
        ("mosim_spark_fastlio_livox_lidar", 9.0),
        ("uav1_global_points", 3.0),
        ("mosim_planner_global_points", 3.0),
        ("uav1_sunray_gazebo_pose", 15.0),
        ("mosim_planner_odom", 15.0),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")
    counts = {
        "lidar_received": 2,
        "fastlio_lidar_published": 2,
        "spark_livox_custom_published": 2,
        "sunray_lidar_published": 2,
        "planner_global_points_published": 2,
        "mosim_planner_global_points_published": 2,
        "planner_odom_published": 2,
        "mosim_planner_odom_published": 2,
        "tf_lookup_failures": 0,
        "frame_mismatch_count": 0,
    }
    (tmp_path / "fastlio_planner_input_adapter.json").write_text(
        json.dumps({"schema": "mosim.fastlio_planner_input_adapter.v1", "status": "active", "counts": counts}),
        encoding="utf-8",
    )
    imu_counts = {
        "imu_received": 360,
        "fastlio_imu_published": 360,
        "sunray_imu_published": 360,
        "frame_mismatch_count": 0,
    }
    (tmp_path / "fastlio_imu_passthrough.json").write_text(
        json.dumps({"schema": "mosim.fastlio_imu_passthrough.v1", "status": "active", "counts": imu_counts}),
        encoding="utf-8",
    )

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--gate-profile",
            "fastlio_planner_input",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
            "--fastlio-imu-passthrough-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_profile"] == "fastlio_planner_input"
    assert report["gate_passed"] is True
    assert report["fastlio_planner_input"]["adapter_status"] == "active"
    assert report["topic_samples"]["planner_global_points"]["frame_id"] == "map"
    assert report["topic_samples"]["fastlio_lidar"]["sample_point_count"] == 1
    assert report["topic_samples"]["spark_fastlio_livox"]["sample_point_count"] == 4
    assert report["topic_samples"]["spark_fastlio_livox"]["sample_point_count_source"] == "point_num"
    assert report["topic_samples"]["spark_fastlio_livox"]["sample_line_values"] == [0, 1, 2, 3]
    assert "topic/frame/rate/input-shape visibility" in " ".join(report["claim_boundary"])


def test_runtime_status_accepts_fastlio_planner_input_from_adapter_report_when_ros_graph_snapshot_is_sparse(
    tmp_path: Path,
) -> None:
    write_fastlio_planner_input_fixture(tmp_path)
    (tmp_path / "ros2_topic_list.txt").write_text("", encoding="utf-8")
    for key in [
        "mosim_fastlio_livox_lidar",
        "mosim_fastlio_livox_imu",
        "mosim_spark_fastlio_livox_lidar",
        "uav1_livox_lidar",
        "uav1_livox_imu",
        "uav1_global_points",
        "mosim_planner_global_points",
        "uav1_sunray_gazebo_pose",
        "mosim_planner_odom",
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text("", encoding="utf-8")
        (tmp_path / f"topic_{key}_once.rc").write_text("2\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.txt").write_text("average rate: 0.1\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--gate-profile",
            "fastlio_planner_input",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["topic_samples"]["fastlio_lidar"]["sample_recorded_by_adapter_report"] is True
    assert report["topic_samples"]["planner_global_points"]["frame_id_source"] == "adapter_report"
    assert report["topic_samples"]["planner_global_points"]["sample_point_count_source"] == "adapter_report_counter"
    assert "fastlio_planner_input_evidence_covers_adapter_report_surface" in report["warnings"]
    assert "spark_livox_line_values_covered_by_adapter_report" in report["warnings"]
    assert "spark_livox_offset_time_values_covered_by_adapter_report" in report["warnings"]
    assert "spark_livox_line_values_missing" not in report["blockers"]
    assert "spark_livox_offset_time_values_missing" not in report["blockers"]


def test_runtime_status_accepts_planner_handoff_without_setpoint_publication(tmp_path: Path) -> None:
    write_fastlio_planner_input_fixture(tmp_path)

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--gate-profile",
            "planner_handoff_without_setpoint_publication",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
            "--fastlio-imu-passthrough-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_profile"] == "planner_handoff_without_setpoint_publication"
    assert report["gate_passed"] is True
    handoff = report["planner_handoff_without_setpoint_publication"]
    assert handoff["all_forbidden_absent"] is True
    assert "/mosim/planner/setpoint" in handoff["forbidden_topics"]
    assert report["controller_output"]["observed_by_topic_list_or_sample"] is False
    assert report["actuator_command"]["ros_echo"]["topic_present"] is False
    assert "forbidden setpoint/controller/actuator topic absence" in " ".join(report["claim_boundary"])


def test_runtime_status_blocks_planner_handoff_when_forbidden_topic_present(tmp_path: Path) -> None:
    write_fastlio_planner_input_fixture(tmp_path, include_forbidden=True)

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--gate-profile",
            "planner_handoff_without_setpoint_publication",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
            "--fastlio-imu-passthrough-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "planner_handoff_forbidden_topic_observed:/position_cmd" in report["blockers"]
    assert (
        "planner_handoff_forbidden_topic_observed:/mosim/sunray150/controller_output"
        in report["blockers"]
    )


def test_runtime_status_blocks_spark_livox_custom_msg_without_point_num(tmp_path: Path) -> None:
    observed_topics = [
        "/mosim/gazebo/imu",
        "/mosim/gazebo/lidar_points/points",
        "/mosim/fastlio/livox/lidar",
        "/mosim/fastlio/livox/imu",
        "/mosim/spark_fastlio/livox/lidar",
        "/uav1/livox/lidar",
        "/uav1/livox/imu",
        "/uav1/global_points",
        "/mosim/planner/global_points",
        "/uav1/sunray/gazebo_pose",
        "/mosim/planner/odom",
        "/tf_static",
    ]
    (tmp_path / "ros2_topic_list.txt").write_text("\n".join(observed_topics) + "\n", encoding="utf-8")
    for key, frame_id in [
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_gazebo_imu", "sunray150_assembled/base_link/forward_imu"),
        ("mosim_fastlio_livox_lidar", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_fastlio_livox_imu", "sunray150_assembled/base_link/forward_imu"),
        ("uav1_livox_lidar", "sunray150_assembled/base_link/mid360_lidar"),
        ("uav1_livox_imu", "sunray150_assembled/base_link/forward_imu"),
        ("uav1_global_points", "map"),
        ("mosim_planner_global_points", "map"),
        ("uav1_sunray_gazebo_pose", "map"),
        ("mosim_planner_odom", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: 1\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_mosim_spark_fastlio_livox_lidar_once.txt").write_text(
        "header:\n  frame_id: sunray150_assembled/base_link/mid360_lidar\n"
        "points:\n"
        "- offset_time: 0\n"
        "  line: 0\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_mosim_spark_fastlio_livox_lidar_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_fastlio_livox_lidar", 9.0),
        ("mosim_fastlio_livox_imu", 180.0),
        ("mosim_spark_fastlio_livox_lidar", 9.0),
        ("uav1_global_points", 3.0),
        ("mosim_planner_global_points", 3.0),
        ("uav1_sunray_gazebo_pose", 15.0),
        ("mosim_planner_odom", 15.0),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")
    counts = {
        "lidar_received": 2,
        "fastlio_lidar_published": 2,
        "spark_livox_custom_published": 2,
        "sunray_lidar_published": 2,
        "planner_global_points_published": 2,
        "mosim_planner_global_points_published": 2,
        "planner_odom_published": 2,
        "mosim_planner_odom_published": 2,
        "tf_lookup_failures": 0,
        "frame_mismatch_count": 0,
    }
    (tmp_path / "fastlio_planner_input_adapter.json").write_text(
        json.dumps({"schema": "mosim.fastlio_planner_input_adapter.v1", "status": "active", "counts": counts}),
        encoding="utf-8",
    )
    imu_counts = {
        "imu_received": 360,
        "fastlio_imu_published": 360,
        "sunray_imu_published": 360,
        "frame_mismatch_count": 0,
    }
    (tmp_path / "fastlio_imu_passthrough.json").write_text(
        json.dumps({"schema": "mosim.fastlio_imu_passthrough.v1", "status": "active", "counts": imu_counts}),
        encoding="utf-8",
    )

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--gate-profile",
            "fastlio_planner_input",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
            "--fastlio-imu-passthrough-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "missing_pointcloud_dimensions:spark_fastlio_livox" in report["blockers"]


def test_runtime_status_blocks_fastlio_planner_input_without_adapter_report(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "/mosim/gazebo/imu\n/mosim/gazebo/lidar_points/points\n",
        encoding="utf-8",
    )
    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--gate-profile",
            "fastlio_planner_input",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "fastlio_planner_input_adapter_report_missing" in report["blockers"]
    assert any(item.startswith("missing_observed_topic:fastlio_lidar") for item in report["blockers"])


def test_runtime_status_blocks_controller_output_node_handoff_without_input_sample(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "/sunray150/gazebo/command/motor_speed\n",
        encoding="utf-8",
    )
    velocity = [4000.0, 4000.0, 4000.0, 4000.0]
    (tmp_path / "controller_output_fixture.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "controller_output_adapter_node.json").write_text(
        json.dumps({"status": "published", "input_command": [0.5, 0.5, 0.5, 0.5], "velocity": velocity}),
        encoding="utf-8",
    )
    (tmp_path / "controller_output_node.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity: [4000, 4000, 4000, 4000]\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.txt").write_text(
        "velocity: 4000\nvelocity: 4000\nvelocity: 4000\nvelocity: 4000\n",
        encoding="utf-8",
    )
    (tmp_path / "gz_topic_sunray150_gazebo_command_motor_speed_once.rc").write_text("0\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-actuator-command-check",
            "1",
            "--run-controller-output-node",
            "1",
            "--run-controller-output-fixture",
            "1",
            "--gate-profile",
            "controller_output_node_handoff",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "missing_observed_topic:controller_output:/mosim/sunray150/controller_output" in report["blockers"]
    assert "missing_topic_sample:controller_output:/mosim/sunray150/controller_output" in report["blockers"]


def test_runtime_status_blocks_empty_local_voxel_pointcloud(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id, width in [
        ("mosim_gazebo_imu", "base_link", 1),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar", 1),
        ("mosim_local_occupancy_voxels", "map", 0),
        ("mosim_local_occupancy_grid", "map", 120),
        ("tf_static", "map", 1),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nheight: 1\nwidth: {width}\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    (tmp_path / "topic_tf_static_once.txt").write_text(
        "transforms:\n"
        "- header:\n"
        "    frame_id: map\n"
        "  child_frame_id: sunray150_assembled/base_link/mid360_lidar\n",
        encoding="utf-8",
    )
    (tmp_path / "topic_tf_static_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--local-map-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "empty_pointcloud_sample:local_occupancy_voxels" in report["blockers"]


def test_runtime_status_blocks_lidar_frame_mismatch(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_gazebo_lidar_points_points", "base/mid360_link"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--local-map-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert "topic_frame_mismatch:lidar_points:base/mid360_link!=sunray150_assembled/base_link/mid360_lidar" in report["blockers"]


def test_runtime_status_blocks_missing_tf_chain_for_sensor_frame(tmp_path: Path) -> None:
    (tmp_path / "ros2_topic_list.txt").write_text(
        "\n".join(
            [
                "/mosim/gazebo/imu",
                "/mosim/gazebo/lidar_points/points",
                "/mosim/local_occupancy_voxels",
                "/mosim/local_occupancy_grid",
                "/tf_static",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for key, frame_id in [
        ("mosim_gazebo_imu", "base_link"),
        ("mosim_gazebo_lidar_points_points", "sunray150_assembled/base_link/mid360_lidar"),
        ("mosim_local_occupancy_voxels", "map"),
        ("mosim_local_occupancy_grid", "map"),
        ("tf_static", "map"),
    ]:
        (tmp_path / f"topic_{key}_once.txt").write_text(
            f"header:\n  frame_id: {frame_id}\nsample: ok\n",
            encoding="utf-8",
        )
        (tmp_path / f"topic_{key}_once.rc").write_text("0\n", encoding="utf-8")
    for key, rate in [
        ("mosim_gazebo_imu", 180.0),
        ("mosim_gazebo_lidar_points_points", 9.0),
        ("mosim_local_occupancy_voxels", 2.5),
    ]:
        (tmp_path / f"topic_{key}_hz.txt").write_text(f"average rate: {rate}\n", encoding="utf-8")
        (tmp_path / f"topic_{key}_hz.rc").write_text("124\n", encoding="utf-8")

    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-local-map",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--local-map-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert "missing_tf_edges" in report["blockers"]
    assert report["tf_chain"]["chain_to_map_verified"] is False


def test_runtime_status_accepts_ego_style_planner_output_without_actuation(tmp_path: Path) -> None:
    write_ego_style_planner_output_fixture(tmp_path)
    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--run-ego-style-planner-output",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gate-profile",
            "ego_style_planner_output_without_actuation",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
            "--fastlio-imu-passthrough-alive",
            "1",
            "--ego-style-planner-alive",
            "0",
            "--position-command-converter-alive",
            "0",
            "--planner-setpoint-adapter-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["ego_style_planner_output_without_actuation"]["report_gate_passed"] is True
    assert report["ego_style_planner_output_without_actuation"]["all_forbidden_absent"] is True


def test_runtime_status_blocks_ego_style_planner_output_with_actuation_topics(tmp_path: Path) -> None:
    write_ego_style_planner_output_fixture(tmp_path, include_forbidden=True)
    output = tmp_path / "RUNTIME_STATUS.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNTIME_STATUS),
            "--scenario",
            str(SCENARIO),
            "--result-dir",
            str(tmp_path),
            "--output-json",
            str(output),
            "--run-gazebo",
            "1",
            "--run-ros2-bridge",
            "1",
            "--run-fastlio-planner-input-adapter",
            "1",
            "--run-ego-style-planner-output",
            "1",
            "--run-topic-check",
            "1",
            "--run-rate-check",
            "1",
            "--run-tf-check",
            "1",
            "--gate-profile",
            "ego_style_planner_output_without_actuation",
            "--gazebo-alive",
            "1",
            "--bridge-alive",
            "1",
            "--fastlio-planner-input-alive",
            "1",
            "--fastlio-imu-passthrough-alive",
            "1",
            "--ego-style-planner-alive",
            "0",
            "--position-command-converter-alive",
            "0",
            "--planner-setpoint-adapter-alive",
            "1",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert "ego_style_planner_forbidden_topic_observed:/mosim/sunray150/controller_output" in report["blockers"]

