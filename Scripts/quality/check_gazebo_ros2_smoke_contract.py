#!/usr/bin/env python3
"""Validate the project-owned Gazebo+ROS2 single-UAV smoke scaffold."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover - reported as runtime checker issue
    yaml = None
    YAML_IMPORT_ERROR = exc
else:
    YAML_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = ROOT / "Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError(f"PyYAML unavailable: {YAML_IMPORT_ERROR}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def xml_root(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def find_texts(root: ET.Element, name: str) -> list[str]:
    return [item.text or "" for item in root.iter(name)]


def sensor_signature(root: ET.Element) -> dict[str, dict[str, str]]:
    signature: dict[str, dict[str, str]] = {}
    for sensor in root.iter("sensor"):
        name = sensor.attrib.get("name", "")
        if not name:
            continue
        signature[name] = {
            "type": sensor.attrib.get("type", ""),
            "topic": (sensor.findtext("topic") or "").strip(),
            "update_rate": (sensor.findtext("update_rate") or "").strip(),
            "pose": (sensor.findtext("pose") or "").strip(),
        }
    return signature


def world_name(root: ET.Element) -> str:
    world = root.find("world")
    if world is None:
        return ""
    return world.attrib.get("name", "")


def validate(scenario_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    scenario = read_yaml(scenario_path)
    vehicle_id = str(scenario.get("vehicle_id", "sunray150") or "sunray150")
    expected_base_frame = f"{vehicle_id}/base_link"
    expected_lidar_frame = f"{expected_base_frame}/mid360_lidar"
    expected_imu_frame = f"{expected_base_frame}/forward_imu"

    gazebo = scenario.get("gazebo") if isinstance(scenario.get("gazebo"), dict) else {}
    ros2 = scenario.get("ros2") if isinstance(scenario.get("ros2"), dict) else {}
    outputs = scenario.get("outputs") if isinstance(scenario.get("outputs"), dict) else {}
    claim_boundary = scenario.get("claim_boundary") if isinstance(scenario.get("claim_boundary"), dict) else {}
    current_lane_boundary = (
        scenario.get("current_lane_boundary")
        if isinstance(scenario.get("current_lane_boundary"), dict)
        else {}
    )
    motor_plugin_disabled = "disabled" in str(
        current_lane_boundary.get("motor_plugin_state", "")
    ).lower()
    local_map = ros2.get("local_map_adapter") if isinstance(ros2.get("local_map_adapter"), dict) else {}
    map_review_capture = (
        ros2.get("map_review_capture") if isinstance(ros2.get("map_review_capture"), dict) else {}
    )
    fastlio_planner_input = (
        ros2.get("fastlio_planner_input_adapter")
        if isinstance(ros2.get("fastlio_planner_input_adapter"), dict)
        else {}
    )
    fastlio_imu_passthrough = (
        ros2.get("fastlio_imu_passthrough")
        if isinstance(ros2.get("fastlio_imu_passthrough"), dict)
        else {}
    )
    planner_handoff_without_setpoint = (
        ros2.get("planner_handoff_without_setpoint_publication")
        if isinstance(ros2.get("planner_handoff_without_setpoint_publication"), dict)
        else {}
    )
    spark_fastlio_runtime = (
        ros2.get("spark_fastlio_runtime")
        if isinstance(ros2.get("spark_fastlio_runtime"), dict)
        else {}
    )
    gazebo_truth_pose = (
        ros2.get("gazebo_truth_pose") if isinstance(ros2.get("gazebo_truth_pose"), dict) else {}
    )
    fastlio_truth_error_eval = (
        ros2.get("fastlio_truth_error_eval")
        if isinstance(ros2.get("fastlio_truth_error_eval"), dict)
        else {}
    )
    controller_adapter = (
        ros2.get("controller_adapter") if isinstance(ros2.get("controller_adapter"), dict) else {}
    )
    command_ack = (
        ros2.get("command_acknowledgement_without_closed_loop")
        if isinstance(ros2.get("command_acknowledgement_without_closed_loop"), dict)
        else {}
    )
    plant_response = (
        ros2.get("single_uav_plant_response_pre_acceptance")
        if isinstance(ros2.get("single_uav_plant_response_pre_acceptance"), dict)
        else {}
    )
    hover_bracket = (
        ros2.get("single_uav_hover_command_bracket")
        if isinstance(ros2.get("single_uav_hover_command_bracket"), dict)
        else {}
    )
    hover_hold = (
        ros2.get("single_uav_hover_hold_closed_loop_pre_acceptance")
        if isinstance(ros2.get("single_uav_hover_hold_closed_loop_pre_acceptance"), dict)
        else {}
    )

    required_top = [
        "experiment_id",
        "scene_id",
        "map_id",
        "vehicle_id",
        "controller_id",
        "planner_id",
        "gazebo",
        "ros2",
        "outputs",
        "claim_boundary",
    ]
    for key in required_top:
        if key not in scenario:
            issues.append(f"missing scenario field: {key}")

    world_path = repo_path(str(gazebo.get("world", "")))
    model_path = repo_path(str(gazebo.get("model", "")))
    model_config_path = repo_path(str(gazebo.get("model_config", "")))
    sensor_path = repo_path(str(gazebo.get("sensor_fragment", "")))
    local_map_script = repo_path(str(local_map.get("script", "")))
    map_review_recorder_script = repo_path(str(map_review_capture.get("script", "")))
    fastlio_planner_input_script = repo_path(str(fastlio_planner_input.get("script", "")))
    fastlio_imu_passthrough_script = repo_path(str(fastlio_imu_passthrough.get("script", "")))
    spark_fastlio_setup = repo_path(str(spark_fastlio_runtime.get("workspace_setup", "")))
    spark_fastlio_launch_file = repo_path(str(spark_fastlio_runtime.get("launch_file", "")))
    spark_fastlio_config_path = repo_path(str(spark_fastlio_runtime.get("config_path", "")))
    spark_fastlio_recorder_script = repo_path(str(spark_fastlio_runtime.get("recorder_script", "")))
    gazebo_truth_recorder_script = repo_path(str(gazebo_truth_pose.get("recorder_script", "")))
    fastlio_truth_eval_script = repo_path(str(fastlio_truth_error_eval.get("script", "")))
    plant_response_eval_script = repo_path(str(plant_response.get("script", "")))
    hover_bracket_runner = repo_path(str(hover_bracket.get("runner_script", "")))
    hover_bracket_eval_script = repo_path(str(hover_bracket.get("eval_script", "")))
    hover_hold_runner = repo_path(str(hover_hold.get("runner_script", "")))
    hover_hold_controller_script = repo_path(str(hover_hold.get("controller_script", "")))
    hover_hold_eval_script = repo_path(str(hover_hold.get("eval_script", "")))
    controller_adapter_script = repo_path(str(controller_adapter.get("adapter_script", "")))
    controller_node_script = repo_path(str(controller_adapter.get("node_script", "")))
    controller_fixture_script = repo_path(str(controller_adapter.get("fixture_publisher_script", "")))
    mosim_msgs_package = repo_path(str(controller_adapter.get("message_package", "")))
    runner = ROOT / "Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh"
    dependency_check = ROOT / "Scripts/gazebo/check_gazebo_ros2_dependencies.sh"

    for label, path in [
        ("world", world_path),
        ("model", model_path),
        ("model_config", model_config_path),
        ("sensor_fragment", sensor_path),
        ("local_map_script", local_map_script),
        ("map_review_recorder_script", map_review_recorder_script),
        ("fastlio_planner_input_script", fastlio_planner_input_script),
        ("fastlio_imu_passthrough_script", fastlio_imu_passthrough_script),
        ("spark_fastlio_setup", spark_fastlio_setup),
        ("spark_fastlio_launch_file", spark_fastlio_launch_file),
        ("spark_fastlio_config_path", spark_fastlio_config_path),
        ("spark_fastlio_recorder_script", spark_fastlio_recorder_script),
        ("gazebo_truth_recorder_script", gazebo_truth_recorder_script),
        ("fastlio_truth_eval_script", fastlio_truth_eval_script),
        ("plant_response_eval_script", plant_response_eval_script),
        ("hover_bracket_runner", hover_bracket_runner),
        ("hover_bracket_eval_script", hover_bracket_eval_script),
        ("hover_hold_runner", hover_hold_runner),
        ("hover_hold_controller_script", hover_hold_controller_script),
        ("hover_hold_eval_script", hover_hold_eval_script),
        ("controller_adapter_script", controller_adapter_script),
        ("controller_node_script", controller_node_script),
        ("controller_fixture_script", controller_fixture_script),
        ("mosim_msgs_package", mosim_msgs_package),
        ("runner", runner),
        ("dependency_check", dependency_check),
    ]:
        if not path.exists():
            issues.append(f"missing {label}: {rel(path)}")

    if str(gazebo.get("backend", "")) != "fortress_ignition6":
        issues.append("gazebo.backend must be fortress_ignition6 for the current Humble validation lane")
    reuse_boundary = (
        gazebo.get("yunzong_reuse_boundary") if isinstance(gazebo.get("yunzong_reuse_boundary"), dict) else {}
    )
    reusable = reuse_boundary.get("reusable") if isinstance(reuse_boundary.get("reusable"), list) else []
    not_reused = (
        reuse_boundary.get("not_reused_as_authority")
        if isinstance(reuse_boundary.get("not_reused_as_authority"), list)
        else []
    )
    if not any("SDF" in str(item) for item in reusable):
        issues.append("gazebo.yunzong_reuse_boundary.reusable must include SDF/world/model assets")
    if not any("ROS1/MAVROS/PX4" in str(item) for item in not_reused):
        issues.append("gazebo.yunzong_reuse_boundary.not_reused_as_authority must exclude ROS1/MAVROS/PX4 command ownership")

    if world_path.exists():
        root = xml_root(world_path)
        text = world_path.read_text(encoding="utf-8")
        current_world_name = world_name(root)
        if root.tag != "sdf":
            issues.append("world root must be <sdf>")
        if "model://sunray150" not in text:
            issues.append("world must include model://sunray150")
        plugin_names = "\n".join(find_texts(root, "plugin"))
        for required_plugin in [
            "ignition-gazebo-physics-system",
            "ignition-gazebo-user-commands-system",
            "ignition-gazebo-scene-broadcaster-system",
            "ignition-gazebo-sensors-system",
            "ignition-gazebo-imu-system",
        ]:
            if required_plugin not in text:
                issues.append(f"world missing Fortress plugin: {required_plugin}")
        if "<render_engine>ogre</render_engine>" not in text:
            issues.append("world Sensors render_engine must be ogre for the current WSL headless smoke lane")
        if not current_world_name:
            issues.append("world must declare a nonempty name")
        if plugin_names == "":
            warnings.append("world plugin text check used raw XML text because plugin nodes have attributes")

    if model_path.exists():
        text = model_path.read_text(encoding="utf-8")
        root = xml_root(model_path)
        if root.tag != "sdf":
            issues.append("model root must be <sdf>")
        for required in [
            "base_link",
            "mid360_lidar",
            "/mosim/gazebo/lidar_points",
            "forward_imu",
            "/mosim/gazebo/imu",
        ]:
            if required not in text:
                issues.append(f"model missing required token: {required}")
        if "<update_rate>200</update_rate>" not in text:
            issues.append("model IMU update_rate must be 200 Hz")
        if "<update_rate>10</update_rate>" not in text:
            issues.append("model LiDAR update_rate must be 10 Hz")
        link_names = {link.attrib.get("name", "") for link in root.iter("link")}
        joint_nodes = {joint.attrib.get("name", ""): joint for joint in root.iter("joint")}
        for index in range(4):
            rotor = f"rotor_{index}"
            joint_name = f"{rotor}_joint"
            if rotor not in link_names:
                issues.append(f"model missing motor rotor link: {rotor}")
            joint = joint_nodes.get(joint_name)
            if joint is None:
                issues.append(f"model missing motor rotor joint: {joint_name}")
            else:
                if joint.attrib.get("type") != "revolute":
                    issues.append(f"{joint_name} must be a revolute joint")
                if (joint.findtext("parent") or "").strip() != "base_link":
                    issues.append(f"{joint_name} parent must be base_link")
                if (joint.findtext("child") or "").strip() != rotor:
                    issues.append(f"{joint_name} child must be {rotor}")
        motor_plugins = [
            plugin
            for plugin in root.iter("plugin")
            if plugin.attrib.get("name") == "gz::sim::systems::MulticopterMotorModel"
        ]
        if len(motor_plugins) != 4 and not motor_plugin_disabled:
            issues.append("model must declare four MulticopterMotorModel plugins")
        if len(motor_plugins) != 4 and motor_plugin_disabled:
            warnings.append(
                "MulticopterMotorModel plugins are disabled by current_lane_boundary; "
                "this scenario can only support scaffold/pre-acceptance claims."
            )
        motor_numbers: list[int] = []
        motor_speed_topics: list[str] = []
        turning_directions: list[str] = []
        if str(gazebo.get("backend", "")) == "fortress_ignition6":
            allowed_motor_plugin_filenames = {
                "ignition-gazebo-multicopter-motor-model-system",
                "gz-sim-multicopter-motor-model-system",
            }
        else:
            allowed_motor_plugin_filenames = {"gz-sim-multicopter-motor-model-system"}
        for plugin in motor_plugins:
            filename = plugin.attrib.get("filename", "")
            if filename not in allowed_motor_plugin_filenames:
                issues.append(
                    "motor plugin filename must match the current Gazebo backend "
                    f"({', '.join(sorted(allowed_motor_plugin_filenames))}), got {filename}"
                )
            motor_number_text = (plugin.findtext("motorNumber") or "").strip()
            try:
                motor_numbers.append(int(motor_number_text))
            except ValueError:
                issues.append(f"motor plugin motorNumber must be integer, got {motor_number_text!r}")
            command_topic = (plugin.findtext("commandSubTopic") or "").strip()
            if command_topic != "gazebo/command/motor_speed":
                issues.append("motor plugin commandSubTopic must be gazebo/command/motor_speed")
            motor_speed_topics.append((plugin.findtext("motorSpeedPubTopic") or "").strip())
            turning_directions.append((plugin.findtext("turningDirection") or "").strip())
            for required_field in [
                "robotNamespace",
                "jointName",
                "linkName",
                "maxRotVelocity",
                "motorConstant",
                "momentConstant",
                "rotorDragCoefficient",
                "rollingMomentCoefficient",
                "motorType",
            ]:
                if not (plugin.findtext(required_field) or "").strip():
                    issues.append(f"motor plugin missing {required_field}")
        if sorted(motor_numbers) != [0, 1, 2, 3] and not motor_plugin_disabled:
            issues.append("motor plugin motorNumber values must be 0..3")
        if sorted(motor_speed_topics) != [f"motor_speed/{index}" for index in range(4)] and not motor_plugin_disabled:
            issues.append("motor plugin motorSpeedPubTopic values must be motor_speed/0..3")
        if turning_directions != ["ccw", "ccw", "cw", "cw"] and not motor_plugin_disabled:
            issues.append("motor plugin turningDirection values must match [ccw, ccw, cw, cw]")

    if sensor_path.exists():
        text = sensor_path.read_text(encoding="utf-8")
        for required in ["mid360_lidar", "forward_imu", "gpu_lidar", "/mosim/gazebo/lidar_points"]:
            if required not in text:
                issues.append(f"sensor fragment missing required token: {required}")
    if model_path.exists() and sensor_path.exists():
        model_sensors = sensor_signature(xml_root(model_path))
        fragment_sensors = sensor_signature(xml_root(sensor_path))
        for sensor_name in ["forward_imu", "mid360_lidar"]:
            if sensor_name not in model_sensors:
                issues.append(f"model missing sensor signature: {sensor_name}")
                continue
            if sensor_name not in fragment_sensors:
                issues.append(f"sensor fragment missing sensor signature: {sensor_name}")
                continue
            for field in ["type", "topic", "update_rate", "pose"]:
                if model_sensors[sensor_name].get(field, "") != fragment_sensors[sensor_name].get(field, ""):
                    issues.append(f"sensor fragment drift: {sensor_name}.{field}")

    topics = ros2.get("topics") if isinstance(ros2.get("topics"), dict) else {}
    for key in [
        "controller_output",
        "actuator_command",
        "imu",
        "lidar_scan",
        "lidar_points",
        "tf",
        "tf_static",
        "local_occupancy_voxels",
        "local_occupancy_grid",
        "fastlio_lidar",
        "fastlio_imu",
        "spark_fastlio_livox",
        "sunray_fastlio_lidar",
        "sunray_fastlio_imu",
        "planner_global_points",
        "mosim_planner_global_points",
        "planner_odom",
        "mosim_planner_odom",
        "spark_fastlio_registered_cloud",
        "spark_fastlio_odometry",
        "spark_fastlio_path",
    ]:
        if not str(topics.get(key, "")).startswith("/"):
            issues.append(f"ros2.topics.{key} must be an absolute ROS topic")

    if str(ros2.get("distro", "")) != "humble":
        issues.append("ros2.distro must be humble for the current WSL route")
    commands = ros2.get("required_commands") if isinstance(ros2.get("required_commands"), list) else []
    for command in ["ros2", "colcon", "gz"]:
        if command not in commands:
            issues.append(f"ros2.required_commands missing {command}")
    bridge = ros2.get("bridge") if isinstance(ros2.get("bridge"), dict) else {}
    if str(bridge.get("package", "")) != "ros_gz_bridge":
        issues.append("ros2.bridge.package must be ros_gz_bridge")
    if str(bridge.get("required_executable", "")) != "parameter_bridge":
        issues.append("ros2.bridge.required_executable must be parameter_bridge")
    topic_gates = ros2.get("topic_gates") if isinstance(ros2.get("topic_gates"), dict) else {}
    if str(topic_gates.get("truth_pose", "")) != "optional_truth_topic_not_in_smoke_gate":
        issues.append("ros2.topic_gates.truth_pose must mark truth pose as optional outside smoke gate")
    expected_truth_poses: set[str] = set()
    if world_path.exists():
        current_world_name = world_name(xml_root(world_path))
    if current_world_name:
        expected_truth_poses.add(f"/world/{current_world_name}/dynamic_pose/info")
        expected_truth_poses.add(f"/world/{current_world_name}/state")
    if vehicle_id:
        expected_truth_poses.add(f"/model/{vehicle_id}/truth_pose")
        expected_truth_poses.add(f"/model/{vehicle_id}/pose")
    if expected_truth_poses and str(topics.get("truth_pose", "")) not in expected_truth_poses:
        issues.append(
            "ros2.topics.truth_pose must use one of "
            + ", ".join(sorted(expected_truth_poses))
        )
    if str(topics.get("lidar_scan", "")) != "/mosim/gazebo/lidar_points":
        issues.append("ros2.topics.lidar_scan must preserve the Gazebo LaserScan topic")
    if str(topics.get("lidar_points", "")) != "/mosim/gazebo/lidar_points/points":
        issues.append("ros2.topics.lidar_points must use the Gazebo-generated PointCloudPacked topic")
    target_rates = ros2.get("target_rates_hz") if isinstance(ros2.get("target_rates_hz"), dict) else {}
    for key in ["imu", "lidar_points", "local_occupancy_voxels"]:
        try:
            if float(target_rates.get(key, 0)) <= 0:
                issues.append(f"ros2.target_rates_hz.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"ros2.target_rates_hz.{key} must be numeric")
    for key in ["fastlio_lidar", "fastlio_imu", "planner_global_points", "planner_odom"]:
        try:
            if float(target_rates.get(key, 0)) <= 0:
                issues.append(f"ros2.target_rates_hz.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"ros2.target_rates_hz.{key} must be numeric")
    try:
        if float(target_rates.get("spark_fastlio_livox", 0)) <= 0:
            issues.append("ros2.target_rates_hz.spark_fastlio_livox must be positive")
    except (TypeError, ValueError):
        issues.append("ros2.target_rates_hz.spark_fastlio_livox must be numeric")
    for key in ["spark_fastlio_registered_cloud", "spark_fastlio_odometry", "spark_fastlio_path"]:
        try:
            if float(target_rates.get(key, 0)) <= 0:
                issues.append(f"ros2.target_rates_hz.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"ros2.target_rates_hz.{key} must be numeric")
    try:
        min_fraction = float(ros2.get("rate_gate_min_fraction", 0))
        if min_fraction <= 0 or min_fraction > 1:
            issues.append("ros2.rate_gate_min_fraction must be within (0, 1]")
    except (TypeError, ValueError):
        issues.append("ros2.rate_gate_min_fraction must be numeric")

    if str(local_map.get("input_topic", "")) != str(topics.get("lidar_points", "")):
        issues.append("local_map_adapter.input_topic must match ros2.topics.lidar_points")
    if str(local_map.get("voxel_topic", "")) != str(topics.get("local_occupancy_voxels", "")):
        issues.append("local_map_adapter.voxel_topic must match ros2.topics.local_occupancy_voxels")
    if str(local_map.get("grid_topic", "")) != str(topics.get("local_occupancy_grid", "")):
        issues.append("local_map_adapter.grid_topic must match ros2.topics.local_occupancy_grid")
    if str(local_map.get("map_frame", "")) != "map":
        issues.append("local_map_adapter.map_frame must be map for the first smoke lane")
    if str(local_map.get("sensor_frame", "")) != expected_lidar_frame:
        issues.append(f"local_map_adapter.sensor_frame must be {expected_lidar_frame} for the current Gazebo smoke lane")
    if str(local_map.get("frame_assumption", "")) != "input_cloud_transformed_to_map_with_same_run_tf":
        issues.append("local_map_adapter.frame_assumption must declare same-run TF transform to map")
    if str(local_map.get("input_frame_policy", "")) != "transform_input_frame_to_map_with_tf":
        issues.append("local_map_adapter.input_frame_policy must require TF transform to map")
    if str(local_map.get("expected_input_frame", "")) != str(local_map.get("sensor_frame", "")):
        issues.append("local_map_adapter.expected_input_frame must match sensor_frame for the TF smoke adapter")
    if str(local_map.get("local_map_center_source", "")) != "tf_translation_in_map":
        issues.append("local_map_adapter.local_map_center_source must track the TF translation in map")
    try:
        if float(local_map.get("tf_lookup_timeout_s", 0)) <= 0:
            issues.append("local_map_adapter.tf_lookup_timeout_s must be positive")
    except (TypeError, ValueError):
        issues.append("local_map_adapter.tf_lookup_timeout_s must be numeric")
    if str(local_map.get("runtime_frame_gate", "")) != "same_run_pointcloud2_header_frame_id_plus_tf_chain_to_map_required":
        issues.append("local_map_adapter.runtime_frame_gate must require same-run PointCloud2 frame plus TF chain evidence")
    try:
        voxel_size = float(local_map.get("voxel_size_m", 0))
        local_radius = float(local_map.get("local_radius_m", 0))
    except (TypeError, ValueError):
        voxel_size = 0.0
        local_radius = 0.0
    if voxel_size <= 0:
        issues.append("local_map_adapter.voxel_size_m must be positive")
    if local_radius <= 0:
        issues.append("local_map_adapter.local_radius_m must be positive")
    if local_map_script.exists():
        script_text = local_map_script.read_text(encoding="utf-8")
        for token in [
            "PointCloud2",
            "OccupancyGrid",
            "voxelize",
            "dry-run only",
            "no FAST-LIO",
            "input_frame_policy",
            "input PointCloud2 frame mismatch",
            "transform_input_frame_to_map_with_tf",
            "lookup_transform",
        ]:
            if token not in script_text:
                issues.append(f"local map script missing token: {token}")

    if not map_review_capture:
        issues.append("missing ros2.map_review_capture")
    else:
        if str(map_review_capture.get("script", "")) != "Scripts/ros/record_gazebo_ros2_map_review.py":
            issues.append("map_review_capture.script must use the Gazebo/ROS2 runtime map review recorder")
        sources = map_review_capture.get("sources") if isinstance(map_review_capture.get("sources"), dict) else {}
        if str(sources.get("lidar_pointcloud", "")) != str(topics.get("lidar_points", "")):
            issues.append("map_review_capture.sources.lidar_pointcloud must match ros2.topics.lidar_points")
        if str(sources.get("local_occupancy_voxels", "")) != str(topics.get("local_occupancy_voxels", "")):
            issues.append("map_review_capture.sources.local_occupancy_voxels must match ros2.topics.local_occupancy_voxels")
        if str(sources.get("local_occupancy_grid", "")) != str(topics.get("local_occupancy_grid", "")):
            issues.append("map_review_capture.sources.local_occupancy_grid must match ros2.topics.local_occupancy_grid")
        if "no_ue_truth_substitution" not in str(map_review_capture.get("runtime_gate_claim", "")):
            issues.append("map_review_capture.runtime_gate_claim must forbid UE truth substitution")
        not_claimed = set(map(str, map_review_capture.get("not_claimed", [])))
        for forbidden in ["planner_ready", "closed_loop", "controller_performance", "multi_uav_readiness"]:
            if forbidden not in not_claimed:
                issues.append(f"map_review_capture.not_claimed missing {forbidden}")

    expected_fastlio_topics = {
        "input_lidar_topic": topics.get("lidar_points"),
        "input_imu_topic": topics.get("imu"),
        "fastlio_lidar_topic": topics.get("fastlio_lidar"),
        "fastlio_imu_topic": topics.get("fastlio_imu"),
        "spark_livox_custom_topic": topics.get("spark_fastlio_livox"),
        "sunray_lidar_topic": topics.get("sunray_fastlio_lidar"),
        "sunray_imu_topic": topics.get("sunray_fastlio_imu"),
        "planner_global_points_topic": topics.get("planner_global_points"),
        "mosim_planner_global_points_topic": topics.get("mosim_planner_global_points"),
        "planner_odom_topic": topics.get("planner_odom"),
        "mosim_planner_odom_topic": topics.get("mosim_planner_odom"),
    }
    for field, expected in expected_fastlio_topics.items():
        if str(fastlio_planner_input.get(field, "")) != str(expected):
            issues.append(f"fastlio_planner_input_adapter.{field} must match ros2.topics")
    if str(fastlio_planner_input.get("script", "")) != "Scripts/ros/gazebo_fastlio_planner_input_adapter.py":
        issues.append("fastlio_planner_input_adapter.script must be Scripts/ros/gazebo_fastlio_planner_input_adapter.py")
    if str(fastlio_planner_input.get("map_frame", "")) != "map":
        issues.append("fastlio_planner_input_adapter.map_frame must be map")
    if str(fastlio_planner_input.get("global_frame", "")) != "map":
        issues.append("fastlio_planner_input_adapter.global_frame must be map for the first input gate")
    if str(fastlio_planner_input.get("sensor_frame", "")) != expected_lidar_frame:
        issues.append("fastlio_planner_input_adapter.sensor_frame must match the current Gazebo MID360 frame")
    if str(fastlio_planner_input.get("imu_frame", "")) != expected_imu_frame:
        issues.append("fastlio_planner_input_adapter.imu_frame must match the current Gazebo IMU frame")
    try:
        spark_livox_scan_lines = int(fastlio_planner_input.get("spark_livox_scan_lines", 0))
    except (TypeError, ValueError):
        spark_livox_scan_lines = 0
    if spark_livox_scan_lines != 4:
        issues.append("fastlio_planner_input_adapter.spark_livox_scan_lines must be 4 to match the Spark MID360 config")
    try:
        spark_livox_scan_rate_hz = float(fastlio_planner_input.get("spark_livox_scan_rate_hz", 0))
    except (TypeError, ValueError):
        spark_livox_scan_rate_hz = 0.0
    if spark_livox_scan_rate_hz != 10.0:
        issues.append("fastlio_planner_input_adapter.spark_livox_scan_rate_hz must be 10 to match the Spark MID360 config")
    if str(fastlio_planner_input.get("spark_livox_line_policy", "")) != "source_pointcloud_row_bucketed_to_scan_lines":
        issues.append("fastlio_planner_input_adapter.spark_livox_line_policy must declare source-row bucketing")
    if (
        str(fastlio_planner_input.get("spark_livox_offset_time_policy", ""))
        != "retained_point_ordinal_spread_over_one_scan_period_nanoseconds"
    ):
        issues.append("fastlio_planner_input_adapter.spark_livox_offset_time_policy must declare nanosecond scan-period offsets")
    if str(fastlio_planner_input.get("spark_livox_point_count_field", "")) != "point_num":
        issues.append("fastlio_planner_input_adapter.spark_livox_point_count_field must be point_num")
    if str(fastlio_planner_input.get("runtime_gate", "")) != "bounded_fastlio_planner_input_surface_only":
        issues.append("fastlio_planner_input_adapter.runtime_gate must be bounded_fastlio_planner_input_surface_only")
    if str(fastlio_planner_input.get("runtime_gate_claim", "")) != "topic_frame_rate_input_shape_only_no_fastlio_no_planner_ready_no_setpoint":
        issues.append("fastlio_planner_input_adapter.runtime_gate_claim must preserve no-overclaim boundary")
    if str(fastlio_planner_input.get("imu_output_policy", "")) != "separate_high_rate_passthrough":
        issues.append("fastlio_planner_input_adapter.imu_output_policy must be separate_high_rate_passthrough")
    expected_imu_passthrough = {
        "input_imu_topic": topics.get("imu"),
        "fastlio_imu_topic": topics.get("fastlio_imu"),
        "sunray_imu_topic": topics.get("sunray_fastlio_imu"),
    }
    for field, expected in expected_imu_passthrough.items():
        if str(fastlio_imu_passthrough.get(field, "")) != str(expected):
            issues.append(f"fastlio_imu_passthrough.{field} must match ros2.topics")
    if str(fastlio_imu_passthrough.get("script", "")) != "Scripts/ros/gazebo_fastlio_imu_passthrough.py":
        issues.append("fastlio_imu_passthrough.script must be Scripts/ros/gazebo_fastlio_imu_passthrough.py")
    if str(fastlio_imu_passthrough.get("imu_frame", "")) != expected_imu_frame:
        issues.append("fastlio_imu_passthrough.imu_frame must match the current Gazebo IMU frame")
    if str(fastlio_imu_passthrough.get("runtime_gate", "")) != "bounded_high_rate_imu_passthrough_for_fastlio_input":
        issues.append("fastlio_imu_passthrough.runtime_gate must be bounded_high_rate_imu_passthrough_for_fastlio_input")
    if str(fastlio_imu_passthrough.get("runtime_gate_claim", "")) != "imu_topic_frame_rate_only_no_fastlio_no_planner_ready_no_setpoint":
        issues.append("fastlio_imu_passthrough.runtime_gate_claim must preserve no-overclaim boundary")
    not_claimed_imu = (
        fastlio_imu_passthrough.get("not_claimed")
        if isinstance(fastlio_imu_passthrough.get("not_claimed"), list)
        else []
    )
    for forbidden in [
        "fast_lio_localization_success",
        "planner_ready",
        "setpoint_publication",
        "command_acknowledgement",
        "closed_loop",
    ]:
        if forbidden not in not_claimed_imu:
            issues.append(f"fastlio_imu_passthrough.not_claimed must include {forbidden}")
    if fastlio_imu_passthrough_script.exists():
        passthrough_text = fastlio_imu_passthrough_script.read_text(encoding="utf-8")
        for token in [
            "sensor_msgs.msg",
            "Imu",
            "fastlio_imu_passthrough",
            "observed_input_average_hz",
            "not LiDAR-gated",
            "closed_loop",
        ]:
            if token not in passthrough_text:
                issues.append(f"FAST-LIO IMU passthrough script missing token: {token}")
    compatible_refs = (
        fastlio_planner_input.get("compatible_reference_inputs")
        if isinstance(fastlio_planner_input.get("compatible_reference_inputs"), dict)
        else {}
    )
    fast_lio_ref = compatible_refs.get("fast_lio") if isinstance(compatible_refs.get("fast_lio"), dict) else {}
    ego_ref = compatible_refs.get("ego_planner") if isinstance(compatible_refs.get("ego_planner"), dict) else {}
    if fast_lio_ref.get("lid_topic") != "/uav1/livox/lidar" or fast_lio_ref.get("imu_topic") != "/uav1/livox/imu":
        issues.append("fastlio_planner_input_adapter.compatible_reference_inputs.fast_lio must preserve Sunray MID360 topics")
    if ego_ref.get("odom_topic") != "/uav1/sunray/gazebo_pose" or ego_ref.get("global_pointcloud_topic") != "/uav1/global_points":
        issues.append("fastlio_planner_input_adapter.compatible_reference_inputs.ego_planner must preserve Sunray EGO input topics")
    not_claimed_fastlio = (
        fastlio_planner_input.get("not_claimed")
        if isinstance(fastlio_planner_input.get("not_claimed"), list)
        else []
    )
    for forbidden in [
        "fast_lio_localization_success",
        "ego_planner_runtime_success",
        "planner_ready",
        "setpoint_publication",
        "command_acknowledgement",
        "closed_loop",
    ]:
        if forbidden not in not_claimed_fastlio:
            issues.append(f"fastlio_planner_input_adapter.not_claimed must include {forbidden}")
    required_handoff_topics = (
        planner_handoff_without_setpoint.get("required_topics")
        if isinstance(planner_handoff_without_setpoint.get("required_topics"), list)
        else []
    )
    forbidden_handoff_topics = (
        planner_handoff_without_setpoint.get("forbidden_topics")
        if isinstance(planner_handoff_without_setpoint.get("forbidden_topics"), list)
        else []
    )
    for topic in [
        topics.get("planner_global_points"),
        topics.get("mosim_planner_global_points"),
        topics.get("planner_odom"),
        topics.get("mosim_planner_odom"),
    ]:
        if topic not in required_handoff_topics:
            issues.append(f"planner_handoff_without_setpoint_publication.required_topics missing {topic}")
    for topic in [
        topics.get("planner_setpoint"),
        topics.get("planner_setpoint_adapter_status"),
        topics.get("reference_position_cmd"),
        topics.get("mosim_planner_position_cmd"),
        topics.get("controller_output"),
        topics.get("actuator_command"),
    ]:
        if topic not in forbidden_handoff_topics:
            issues.append(f"planner_handoff_without_setpoint_publication.forbidden_topics missing {topic}")
    if (
        str(planner_handoff_without_setpoint.get("runtime_gate", ""))
        != "bounded_planner_handoff_without_setpoint_publication"
    ):
        issues.append("planner_handoff_without_setpoint_publication.runtime_gate must declare bounded planner handoff")
    if (
        str(planner_handoff_without_setpoint.get("runtime_gate_claim", ""))
        != "planner_input_handoff_topics_only_no_setpoint_no_controller_no_actuator_no_closed_loop"
    ):
        issues.append("planner_handoff_without_setpoint_publication.runtime_gate_claim must preserve no-setpoint boundary")
    if str(planner_handoff_without_setpoint.get("forbidden_topic_evidence", "")) != "forbidden_topic_presence.json":
        issues.append("planner_handoff_without_setpoint_publication.forbidden_topic_evidence must be forbidden_topic_presence.json")
    not_claimed_handoff = (
        planner_handoff_without_setpoint.get("not_claimed")
        if isinstance(planner_handoff_without_setpoint.get("not_claimed"), list)
        else []
    )
    for forbidden in [
        "planner_ready",
        "setpoint_publication",
        "command_acknowledgement",
        "controller_output_publication",
        "actuator_command_publication",
        "closed_loop",
    ]:
        if forbidden not in not_claimed_handoff:
            issues.append(f"planner_handoff_without_setpoint_publication.not_claimed must include {forbidden}")
    if fastlio_planner_input_script.exists():
        script_text = fastlio_planner_input_script.read_text(encoding="utf-8")
        for token in [
            "FAST-LIO/planner input adapter only",
            "planner_ready",
            "closed_loop",
            "setpoint",
            "PointCloud2",
            "Odometry",
            "lookup_transform",
            "/uav1/livox/lidar",
            "/uav1/sunray/gazebo_pose",
            "/uav1/global_points",
            "fastlio_planner_input_adapter.json",
            "livox_ros_driver2.msg",
            "spark_livox_scan_lines",
            "spark_livox_scan_rate_hz",
            "source_pointcloud_row_bucketed_to_scan_lines",
            "point_num",
        ]:
            if token not in script_text:
                issues.append(f"fastlio planner input adapter script missing token: {token}")

    expected_spark_topics = {
        "input_lidar_topic": topics.get("spark_fastlio_livox"),
        "input_imu_topic": topics.get("fastlio_imu"),
        "output_registered_cloud_topic": topics.get("spark_fastlio_registered_cloud"),
        "output_odometry_topic": topics.get("spark_fastlio_odometry"),
        "output_path_topic": topics.get("spark_fastlio_path"),
    }
    for field, expected in expected_spark_topics.items():
        if str(spark_fastlio_runtime.get(field, "")) != str(expected):
            issues.append(f"spark_fastlio_runtime.{field} must match ros2.topics")
    if str(spark_fastlio_runtime.get("package", "")) != "spark_fast_lio":
        issues.append("spark_fastlio_runtime.package must be spark_fast_lio")
    if str(spark_fastlio_runtime.get("executable", "")) != "spark_lio_mapping":
        issues.append("spark_fastlio_runtime.executable must be spark_lio_mapping")
    if str(spark_fastlio_runtime.get("map_frame", "")) != "map":
        issues.append("spark_fastlio_runtime.map_frame must be map")
    if str(spark_fastlio_runtime.get("base_frame", "")) != expected_base_frame:
        issues.append(f"spark_fastlio_runtime.base_frame must be {expected_base_frame}")
    if str(spark_fastlio_runtime.get("visualization_frame", "")) not in {"base", "lidar", "imu"}:
        issues.append("spark_fastlio_runtime.visualization_frame must be a Spark enum: base, lidar, or imu")
    if str(spark_fastlio_runtime.get("visualization_frame", "")) == str(spark_fastlio_runtime.get("base_frame", "")):
        issues.append("spark_fastlio_runtime.visualization_frame must not be a ROS frame id")
    if str(spark_fastlio_runtime.get("lidar_frame", "")) != expected_lidar_frame:
        issues.append("spark_fastlio_runtime.lidar_frame must match the current Gazebo MID360 frame")
    if str(spark_fastlio_runtime.get("imu_frame", "")) != expected_imu_frame:
        issues.append("spark_fastlio_runtime.imu_frame must match the current Gazebo IMU frame")
    if str(spark_fastlio_runtime.get("runtime_gate", "")) != "bounded_spark_fastlio_output_surface":
        issues.append("spark_fastlio_runtime.runtime_gate must be bounded_spark_fastlio_output_surface")
    if (
        str(spark_fastlio_runtime.get("runtime_gate_claim", ""))
        != "real_spark_fastlio_output_topics_recorded_no_truth_quality_no_planner_no_setpoint"
    ):
        issues.append("spark_fastlio_runtime.runtime_gate_claim must preserve no-overclaim boundary")
    not_claimed_spark = (
        spark_fastlio_runtime.get("not_claimed")
        if isinstance(spark_fastlio_runtime.get("not_claimed"), list)
        else []
    )
    for forbidden in [
        "fast_lio_localization_quality",
        "planner_ready",
        "setpoint_publication",
        "command_acknowledgement",
        "closed_loop",
    ]:
        if forbidden not in not_claimed_spark:
            issues.append(f"spark_fastlio_runtime.not_claimed must include {forbidden}")
    if spark_fastlio_launch_file.exists():
        launch_text = spark_fastlio_launch_file.read_text(encoding="utf-8")
        for token in [
            "lidar_topic",
            "imu_topic",
            "map_frame",
            "base_frame",
            "visualization_frame",
            "spark_lio_mapping",
            "common.visualization_frame",
        ]:
            if token not in launch_text:
                issues.append(f"spark FAST-LIO launch missing token: {token}")
    if spark_fastlio_config_path.exists():
        config_text = spark_fastlio_config_path.read_text(encoding="utf-8")
        for token in [
            "lidar_type: 1",
            "scan_line: 4",
            "scan_rate: 10",
            "extrinsic_est_en: false",
        ]:
            if token not in config_text:
                issues.append(f"spark FAST-LIO config missing token: {token}")
        if spark_livox_scan_lines and f"scan_line: {spark_livox_scan_lines}" not in config_text:
            issues.append("fastlio_planner_input_adapter.spark_livox_scan_lines must match spark FAST-LIO config scan_line")
        if spark_livox_scan_rate_hz and f"scan_rate: {int(spark_livox_scan_rate_hz)}" not in config_text:
            issues.append("fastlio_planner_input_adapter.spark_livox_scan_rate_hz must match spark FAST-LIO config scan_rate")
    if spark_fastlio_recorder_script.exists():
        recorder_text = spark_fastlio_recorder_script.read_text(encoding="utf-8")
        for token in [
            "FASTLIO_RUNTIME_RECORDING.json",
            "fastlio_odometry.jsonl",
            "fastlio_path.jsonl",
            "fastlio_registered_cloud_summary.jsonl",
            "cloud_registered",
            "odometry",
            "path",
        ]:
            if token not in recorder_text:
                issues.append(f"spark FAST-LIO recorder missing token: {token}")
    if str(gazebo_truth_pose.get("topic", "")) != str(topics.get("truth_pose", "")):
        issues.append("gazebo_truth_pose.topic must match ros2.topics.truth_pose")
    truth_model_name = str(gazebo_truth_pose.get("model_name", ""))
    allowed_truth_model_names = {vehicle_id, "base_link"} if vehicle_id else {"base_link"}
    if truth_model_name not in allowed_truth_model_names:
        issues.append(
            "gazebo_truth_pose.model_name must be one of "
            + ", ".join(sorted(name for name in allowed_truth_model_names if name))
        )
    allowed_truth_recorders = {
        "Scripts/gazebo/record_gazebo_pose_truth.py",
        "Scripts/gazebo/capture_gazebo_pose_truth_topic.py",
        "Scripts/gazebo/capture_gazebo_state_truth_topic.py",
        "Scripts/ros/record_pose_array_truth.py",
    }
    if str(gazebo_truth_pose.get("recorder_script", "")) not in allowed_truth_recorders:
        issues.append("gazebo_truth_pose.recorder_script must be a supported Gazebo truth recorder")
    if str(gazebo_truth_pose.get("recorder_script", "")) == "Scripts/ros/record_pose_array_truth.py":
        if not str(gazebo_truth_pose.get("ros_topic", "")):
            issues.append("ROS2 PoseArray truth recorder requires gazebo_truth_pose.ros_topic")
        if str(gazebo_truth_pose.get("ros_message", "")) != "geometry_msgs/msg/PoseArray":
            issues.append("ROS2 PoseArray truth recorder requires ros_message=geometry_msgs/msg/PoseArray")
        if str(gazebo_truth_pose.get("gz_message", "")) != "gz.msgs.Pose_V":
            issues.append("ROS2 PoseArray truth recorder requires gz_message=gz.msgs.Pose_V")
    if gazebo_truth_recorder_script.exists():
        truth_text = gazebo_truth_recorder_script.read_text(encoding="utf-8")
        required_truth_tokens = ["model_name", "position_m"]
        if str(gazebo_truth_pose.get("recorder_script", "")) == "Scripts/gazebo/capture_gazebo_pose_truth_topic.py":
            required_truth_tokens.extend(["parse_samples", "bounded_ign_topic_n1_retry"])
        elif str(gazebo_truth_pose.get("recorder_script", "")) == "Scripts/gazebo/capture_gazebo_state_truth_topic.py":
            required_truth_tokens.extend(["SerializedStepMap", "bounded_ign_state_topic_n1_retry"])
        else:
            required_truth_tokens.append("mosim.gazebo_pose_truth_sample.v1")
        for token in required_truth_tokens:
            if token not in truth_text:
                issues.append(f"gazebo truth recorder missing token: {token}")
    if str(fastlio_truth_error_eval.get("script", "")) != "Scripts/quality/evaluate_fastlio_truth_error.py":
        issues.append("fastlio_truth_error_eval.script must be Scripts/quality/evaluate_fastlio_truth_error.py")
    if str(fastlio_truth_error_eval.get("runtime_gate", "")) != "bounded_spark_fastlio_truth_error_eval":
        issues.append("fastlio_truth_error_eval.runtime_gate must be bounded_spark_fastlio_truth_error_eval")
    if fastlio_truth_eval_script.exists():
        eval_text = fastlio_truth_eval_script.read_text(encoding="utf-8")
        for token in [
            "FASTLIO_TRUTH_ERROR_EVAL",
            "nearest_neighbor_by_time",
            "origin_aligned",
            "planner_ready",
            "closed_loop",
        ]:
            if token not in eval_text:
                issues.append(f"FAST-LIO truth eval script missing token: {token}")

    if str(controller_adapter.get("source_contract", "")) != "ControllerOutput":
        issues.append("controller_adapter.source_contract must be ControllerOutput")
    if str(controller_adapter.get("ros_message", "")) != "mosim_msgs/msg/ControllerOutput":
        issues.append("controller_adapter.ros_message must be mosim_msgs/msg/ControllerOutput")
    if str(controller_adapter.get("message_package", "")) != "Scripts/ros/mosim_msgs":
        issues.append("controller_adapter.message_package must be Scripts/ros/mosim_msgs")
    if str(controller_adapter.get("node_script", "")) != "Scripts/ros/controller_output_to_gazebo_actuators_node.py":
        issues.append("controller_adapter.node_script must be Scripts/ros/controller_output_to_gazebo_actuators_node.py")
    if str(controller_adapter.get("fixture_publisher_script", "")) != "Scripts/ros/publish_controller_output_fixture.py":
        issues.append("controller_adapter.fixture_publisher_script must be Scripts/ros/publish_controller_output_fixture.py")
    if str(controller_adapter.get("input_topic", "")) != str(topics.get("controller_output", "")):
        issues.append("controller_adapter.input_topic must match ros2.topics.controller_output")
    if str(controller_adapter.get("ros_actuator_topic", "")) != str(topics.get("actuator_command", "")):
        issues.append("controller_adapter.ros_actuator_topic must match ros2.topics.actuator_command")
    if str(controller_adapter.get("gz_actuator_topic", "")) != str(topics.get("actuator_command", "")):
        issues.append("controller_adapter.gz_actuator_topic must match ros2.topics.actuator_command")
    if str(controller_adapter.get("ros_type", "")) != "actuator_msgs/msg/Actuators":
        issues.append("controller_adapter.ros_type must be actuator_msgs/msg/Actuators")
    if str(controller_adapter.get("gz_type", "")) != "gz.msgs.Actuators":
        issues.append("controller_adapter.gz_type must be gz.msgs.Actuators")
    if str(controller_adapter.get("command_field", "")) != "velocity":
        issues.append("controller_adapter.command_field must be velocity")
    if controller_adapter.get("actuator_count") != 4:
        issues.append("controller_adapter.actuator_count must be 4")
    if controller_adapter.get("actuator_order") != [f"rotor_{index}" for index in range(4)]:
        issues.append("controller_adapter.actuator_order must be rotor_0..rotor_3")
    if controller_adapter.get("mworks_source_order") != [
        "Dronefixed1",
        "Dronefixed2",
        "Dronefixed3",
        "Dronefixed4",
    ]:
        issues.append("controller_adapter.mworks_source_order must match Dronefixed1..4")
    if controller_adapter.get("mworks_spin_command_sign") != [1, 1, -1, -1]:
        issues.append("controller_adapter.mworks_spin_command_sign must be [1, 1, -1, -1]")
    if controller_adapter.get("gazebo_turning_direction") != ["ccw", "ccw", "cw", "cw"]:
        issues.append("controller_adapter.gazebo_turning_direction must be [ccw, ccw, cw, cw]")
    supported_command_types = (
        controller_adapter.get("command_types_supported")
        if isinstance(controller_adapter.get("command_types_supported"), list)
        else []
    )
    for command_type in ["motor_speed", "normalized_motor_speed", "mworks_signed_visual_motor_speed"]:
        if command_type not in supported_command_types:
            issues.append(f"controller_adapter.command_types_supported missing {command_type}")
    if str(controller_adapter.get("signed_speed_policy", "")) != "magnitude_after_spin_sign_validation":
        issues.append("controller_adapter.signed_speed_policy must be magnitude_after_spin_sign_validation")
    if str(controller_adapter.get("runtime_gate", "")) != "bounded_ros2_gazebo_actuator_topic_handoff":
        issues.append("controller_adapter.runtime_gate must be bounded_ros2_gazebo_actuator_topic_handoff")
    if str(controller_adapter.get("node_runtime_gate", "")) != "bounded_controller_output_node_to_gazebo_actuator_handoff":
        issues.append("controller_adapter.node_runtime_gate must be bounded_controller_output_node_to_gazebo_actuator_handoff")
    if str(controller_adapter.get("runtime_gate_claim", "")) != "topic_visibility_only_no_flight_no_closed_loop":
        issues.append("controller_adapter.runtime_gate_claim must keep actuator handoff limited to topic visibility")
    bounded_command = (
        controller_adapter.get("bounded_runtime_command")
        if isinstance(controller_adapter.get("bounded_runtime_command"), dict)
        else {}
    )
    if bounded_command.get("command_type") != "normalized_motor_speed":
        issues.append("bounded_runtime_command.command_type must be normalized_motor_speed")
    if bounded_command.get("command") != [0.5, 0.5, 0.5, 0.5]:
        issues.append("bounded_runtime_command.command must be [0.5, 0.5, 0.5, 0.5]")
    if bounded_command.get("required_echoes") != [
        "controller_output_topic",
        "ros2_actuator_topic",
        "gazebo_actuator_topic",
    ]:
        issues.append("bounded_runtime_command.required_echoes must require ControllerOutput, ROS2, and Gazebo echoes")
    if str(command_ack.get("runtime_gate", "")) != "bounded_command_acknowledgement_without_closed_loop":
        issues.append("command_acknowledgement_without_closed_loop.runtime_gate must be bounded_command_acknowledgement_without_closed_loop")
    if str(command_ack.get("guard_report", "")) != "command_ack_guard_report.json":
        issues.append("command_acknowledgement_without_closed_loop.guard_report must be command_ack_guard_report.json")
    required_positive_evidence = (
        command_ack.get("required_positive_evidence")
        if isinstance(command_ack.get("required_positive_evidence"), list)
        else []
    )
    for required in [
        "controller_output_fixture.json",
        "topic_mosim_sunray150_controller_output_once.txt",
        "controller_output_adapter_node.json",
        "topic_sunray150_gazebo_command_motor_speed_once.txt",
        "gz_topic_sunray150_gazebo_command_motor_speed_once.txt",
        "command_ack_guard_report.json",
    ]:
        if required not in required_positive_evidence:
            issues.append(f"command_acknowledgement_without_closed_loop.required_positive_evidence missing {required}")
    required_negative_evidence = (
        command_ack.get("required_negative_evidence")
        if isinstance(command_ack.get("required_negative_evidence"), list)
        else []
    )
    for required in ["stale_controller_output.json", "stale_controller_output_report.json"]:
        if required not in required_negative_evidence:
            issues.append(f"command_acknowledgement_without_closed_loop.required_negative_evidence missing {required}")
    command_ack_forbidden_topics = (
        command_ack.get("forbidden_topics")
        if isinstance(command_ack.get("forbidden_topics"), list)
        else []
    )
    for forbidden_topic in [
        "/mosim/planner/setpoint",
        "/mosim/planner/setpoint_adapter_status",
        "/position_cmd",
        "/mosim/planner/position_cmd",
    ]:
        if forbidden_topic not in command_ack_forbidden_topics:
            issues.append(f"command_acknowledgement_without_closed_loop.forbidden_topics missing {forbidden_topic}")
    command_ack_not_claimed = (
        command_ack.get("not_claimed") if isinstance(command_ack.get("not_claimed"), list) else []
    )
    for forbidden_claim in ["hover_success", "planner_ready", "setpoint_publication", "closed_loop", "controller_performance", "multi_uav_readiness"]:
        if forbidden_claim not in command_ack_not_claimed:
            issues.append(f"command_acknowledgement_without_closed_loop.not_claimed missing {forbidden_claim}")
    if str(plant_response.get("runtime_gate", "")) != "bounded_single_uav_controller_output_to_gazebo_plant_response_pre_acceptance":
        issues.append("single_uav_plant_response_pre_acceptance.runtime_gate must be bounded_single_uav_controller_output_to_gazebo_plant_response_pre_acceptance")
    if str(plant_response.get("runtime_gate_claim", "")) != "measurable_gazebo_pose_response_only_no_hover_no_trajectory_no_closed_loop":
        issues.append("single_uav_plant_response_pre_acceptance.runtime_gate_claim must keep plant response below closed-loop claims")
    if str(plant_response.get("output_json", "")) != "GAZEBO_PLANT_RESPONSE_EVAL.json":
        issues.append("single_uav_plant_response_pre_acceptance.output_json must be GAZEBO_PLANT_RESPONSE_EVAL.json")
    if str(plant_response.get("script", "")) != "Scripts/quality/evaluate_gazebo_plant_response.py":
        issues.append("single_uav_plant_response_pre_acceptance.script must be Scripts/quality/evaluate_gazebo_plant_response.py")
    plant_required_evidence = (
        plant_response.get("required_evidence")
        if isinstance(plant_response.get("required_evidence"), list)
        else []
    )
    for required in [
        "controller_output_fixture.json",
        "topic_mosim_sunray150_controller_output_once.txt",
        "controller_output_adapter_node.json",
        "topic_sunray150_gazebo_command_motor_speed_once.txt",
        "gz_topic_sunray150_gazebo_command_motor_speed_once.txt",
        "gazebo_truth_pose.jsonl",
        "GAZEBO_TRUTH_POSE_RECORDING.json",
        "GAZEBO_PLANT_RESPONSE_EVAL.json",
    ]:
        if required not in plant_required_evidence:
            issues.append(f"single_uav_plant_response_pre_acceptance.required_evidence missing {required}")
    plant_not_claimed = (
        plant_response.get("not_claimed") if isinstance(plant_response.get("not_claimed"), list) else []
    )
    for forbidden_claim in ["hover_success", "trajectory_tracking", "planner_ready", "setpoint_publication", "closed_loop", "controller_performance", "multi_uav_readiness"]:
        if forbidden_claim not in plant_not_claimed:
            issues.append(f"single_uav_plant_response_pre_acceptance.not_claimed missing {forbidden_claim}")
    for key in ["min_samples", "min_duration_s", "min_z_delta_m", "min_3d_delta_m", "expected_actuator_count"]:
        try:
            if float(plant_response.get(key, 0)) <= 0:
                issues.append(f"single_uav_plant_response_pre_acceptance.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"single_uav_plant_response_pre_acceptance.{key} must be numeric")
    if str(hover_bracket.get("runtime_gate", "")) != "bounded_single_uav_gazebo_hover_command_bracket":
        issues.append("single_uav_hover_command_bracket.runtime_gate must be bounded_single_uav_gazebo_hover_command_bracket")
    if str(hover_bracket.get("runtime_gate_claim", "")) != "open_loop_thrust_scale_bracket_only_no_closed_loop_no_controller_performance":
        issues.append("single_uav_hover_command_bracket.runtime_gate_claim must keep hover bracket below closed-loop/controller claims")
    if str(hover_bracket.get("runner_script", "")) != "Scripts/gazebo/run_sunray150_hover_command_bracket.sh":
        issues.append("single_uav_hover_command_bracket.runner_script must be Scripts/gazebo/run_sunray150_hover_command_bracket.sh")
    if str(hover_bracket.get("eval_script", "")) != "Scripts/quality/evaluate_gazebo_hover_bracket.py":
        issues.append("single_uav_hover_command_bracket.eval_script must be Scripts/quality/evaluate_gazebo_hover_bracket.py")
    if str(hover_bracket.get("output_json", "")) != "GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json":
        issues.append("single_uav_hover_command_bracket.output_json must be GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json")
    if hover_bracket.get("start_gazebo_paused") is not True:
        issues.append("single_uav_hover_command_bracket.start_gazebo_paused must be true")
    if hover_bracket.get("unpause_after_controller_command") is not True:
        issues.append("single_uav_hover_command_bracket.unpause_after_controller_command must be true")
    if "ground" not in str(hover_bracket.get("free_flight_gate_note", "")).lower():
        issues.append("single_uav_hover_command_bracket.free_flight_gate_note must document ground-settling avoidance")
    commands = hover_bracket.get("commands") if isinstance(hover_bracket.get("commands"), list) else []
    if len(commands) < 3:
        issues.append("single_uav_hover_command_bracket.commands must contain at least 3 samples")
    for value in commands:
        try:
            number = float(value)
        except (TypeError, ValueError):
            issues.append("single_uav_hover_command_bracket.commands values must be numeric")
            continue
        if number <= 0 or number >= 1:
            issues.append("single_uav_hover_command_bracket.commands must be normalized values within (0,1)")
    theoretical_hover = (
        hover_bracket.get("theoretical_hover_estimate")
        if isinstance(hover_bracket.get("theoretical_hover_estimate"), dict)
        else {}
    )
    for key in ["total_mass_kg", "rotor_count", "gravity_m_s2", "motor_constant", "max_rot_velocity", "normalized_hover_command"]:
        try:
            if float(theoretical_hover.get(key, 0)) <= 0:
                issues.append(f"single_uav_hover_command_bracket.theoretical_hover_estimate.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"single_uav_hover_command_bracket.theoretical_hover_estimate.{key} must be numeric")
    classification = (
        hover_bracket.get("classification")
        if isinstance(hover_bracket.get("classification"), dict)
        else {}
    )
    for key in [
        "near_hover_abs_z_delta_m",
        "near_hover_max_z_excursion_m",
        "near_hover_max_3d_excursion_m",
        "over_climb_z_delta_m",
        "over_climb_max_z_m",
        "grounded_max_z_delta_m",
        "min_valid_samples",
    ]:
        try:
            if float(classification.get(key, 0)) <= 0:
                issues.append(f"single_uav_hover_command_bracket.classification.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"single_uav_hover_command_bracket.classification.{key} must be numeric")
    hover_not_claimed = (
        hover_bracket.get("not_claimed") if isinstance(hover_bracket.get("not_claimed"), list) else []
    )
    for forbidden_claim in ["hover_success", "trajectory_tracking", "planner_ready", "setpoint_publication", "closed_loop", "controller_performance", "multi_uav_readiness"]:
        if forbidden_claim not in hover_not_claimed:
            issues.append(f"single_uav_hover_command_bracket.not_claimed missing {forbidden_claim}")
    if str(hover_hold.get("runtime_gate", "")) != "bounded_single_uav_gazebo_truth_feedback_hover_hold_pre_acceptance":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.runtime_gate must be bounded_single_uav_gazebo_truth_feedback_hover_hold_pre_acceptance")
    if str(hover_hold.get("runtime_gate_claim", "")) != "gazebo_truth_feedback_controller_output_actuator_loop_pre_acceptance_no_final_closed_loop_no_controller_performance":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.runtime_gate_claim must keep the gate below final closed-loop/controller claims")
    if str(hover_hold.get("runner_script", "")) != "Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.runner_script must be Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh")
    if str(hover_hold.get("controller_script", "")) != "Scripts/ros/gazebo_truth_hover_hold_controller.py":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.controller_script must be Scripts/ros/gazebo_truth_hover_hold_controller.py")
    if str(hover_hold.get("eval_script", "")) != "Scripts/quality/evaluate_gazebo_hover_hold_closed_loop.py":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.eval_script must be Scripts/quality/evaluate_gazebo_hover_hold_closed_loop.py")
    if str(hover_hold.get("output_json", "")) != "GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.output_json must be GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json")
    if hover_hold.get("start_gazebo_paused") is not True:
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.start_gazebo_paused must be true")
    if hover_hold.get("unpause_after_controller_ready") is not True:
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.unpause_after_controller_ready must be true")
    if str(hover_hold.get("truth_source", "")) != "gazebo_truth_pose":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.truth_source must be gazebo_truth_pose")
    if str(hover_hold.get("controller_output", "")) != "ControllerOutput":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.controller_output must be ControllerOutput")
    if str(hover_hold.get("command_type", "")) != "normalized_motor_speed":
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance.command_type must be normalized_motor_speed")
    for key in ["target_altitude_m", "hover_command", "command_min", "command_max", "duration_s", "publish_rate_hz"]:
        try:
            if float(hover_hold.get(key, 0)) <= 0:
                issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.{key} must be numeric")
    for key in ["kp_z", "kd_z", "ki_z"]:
        try:
            float(hover_hold.get(key, "nan"))
        except (TypeError, ValueError):
            issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.{key} must be numeric")
    for key in ["kp_roll", "kd_roll", "kp_pitch", "kd_pitch", "kp_yaw", "kd_yaw", "attitude_command_limit"]:
        try:
            float(hover_hold.get(key, "nan"))
        except (TypeError, ValueError):
            issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.{key} must be numeric")
    try:
        command_min = float(hover_hold.get("command_min", 0))
        command_max = float(hover_hold.get("command_max", 0))
        hover_command = float(hover_hold.get("hover_command", 0))
        if not (0 < command_min < hover_command < command_max <= 1):
            issues.append("single_uav_hover_hold_closed_loop_pre_acceptance command bounds must satisfy 0 < min < hover_command < max <= 1")
    except (TypeError, ValueError):
        issues.append("single_uav_hover_hold_closed_loop_pre_acceptance command bounds must be numeric")
    hover_hold_required = (
        hover_hold.get("required_evidence")
        if isinstance(hover_hold.get("required_evidence"), list)
        else []
    )
    for required in [
        "hover_hold_controller.json",
        "hover_hold_controller_trace.jsonl",
        "controller_output_adapter_node.json",
        "controller_output_adapter_node.trace.jsonl",
        "topic_mosim_sunray150_controller_output_once.txt",
        "topic_sunray150_gazebo_command_motor_speed_once.txt",
        "gz_topic_sunray150_gazebo_command_motor_speed_once.txt",
        "gazebo_truth_pose.jsonl",
        "GAZEBO_TRUTH_POSE_RECORDING.json",
        "GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json",
        "RUNTIME_STATUS.json",
        "RUN_MANIFEST.json",
    ]:
        if required not in hover_hold_required:
            issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.required_evidence missing {required}")
    hover_hold_thresholds = (
        hover_hold.get("evaluation_thresholds")
        if isinstance(hover_hold.get("evaluation_thresholds"), dict)
        else {}
    )
    for key in [
        "min_controller_samples",
        "min_adapter_samples",
        "min_truth_samples",
        "min_duration_s",
        "max_final_abs_z_error_m",
        "max_abs_z_error_m",
        "min_allowed_z_m",
        "max_allowed_z_m",
        "max_xy_distance_m",
        "max_tilt_rad",
    ]:
        try:
            if float(hover_hold_thresholds.get(key, 0)) <= 0:
                issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.{key} must be positive")
        except (TypeError, ValueError):
            issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.{key} must be numeric")
    hover_hold_not_claimed = (
        hover_hold.get("not_claimed") if isinstance(hover_hold.get("not_claimed"), list) else []
    )
    for forbidden_claim in [
        "competition_controller_performance",
        "trajectory_tracking",
        "planner_ready",
        "setpoint_publication",
        "final_closed_loop_acceptance",
        "fast_lio_localization_success",
        "multi_uav_readiness",
    ]:
        if forbidden_claim not in hover_hold_not_claimed:
            issues.append(f"single_uav_hover_hold_closed_loop_pre_acceptance.not_claimed missing {forbidden_claim}")
    try:
        if float(controller_adapter.get("max_rot_velocity", 0)) <= 0:
            issues.append("controller_adapter.max_rot_velocity must be positive")
        if float(controller_adapter.get("normalized_max_rot_velocity", 0)) <= 0:
            issues.append("controller_adapter.normalized_max_rot_velocity must be positive")
    except (TypeError, ValueError):
        issues.append("controller_adapter velocity bounds must be numeric")
    if controller_adapter_script.exists():
        adapter_text = controller_adapter_script.read_text(encoding="utf-8")
        for token in [
            "ControllerOutput",
            "actuator_msgs/msg/Actuators",
            "gz.msgs.Actuators",
            "mworks_signed_visual_motor_speed",
            "normalized_motor_speed",
            "signed_speed_policy",
            "ros_cli_yaml",
            "closed_loop",
            "planner_ready",
        ]:
            if token not in adapter_text:
                issues.append(f"controller adapter script missing token: {token}")
    if controller_node_script.exists():
        node_text = controller_node_script.read_text(encoding="utf-8")
        for token in [
            "mosim_msgs.msg",
            "ControllerOutput",
            "actuator_msgs.msg",
            "Actuators",
            "create_subscription",
            "create_publisher",
            "controller_output_to_gazebo_actuators_node",
            "closed_loop",
            "planner_ready",
        ]:
            if token not in node_text:
                issues.append(f"controller node script missing token: {token}")
    if controller_fixture_script.exists():
        fixture_text = controller_fixture_script.read_text(encoding="utf-8")
        for token in [
            "mosim_msgs.msg",
            "ControllerOutput",
            "bounded fixture",
            "source_authority",
            "closed_loop",
            "planner_ready",
        ]:
            if token not in fixture_text:
                issues.append(f"controller fixture script missing token: {token}")
    if plant_response_eval_script.exists():
        plant_eval_text = plant_response_eval_script.read_text(encoding="utf-8")
        for token in [
            "mosim.gazebo_plant_response_eval.v1",
            "truth_pose_jsonl",
            "controller_report_json",
            "fixture_report_json",
            "plant_z_response_below_min",
            "plant_3d_response_below_min",
            "plant_max_z_response_below_min",
            "ControllerOutput-to-Gazebo plant response",
            "closed_loop",
            "multi-UAV readiness",
        ]:
            if token not in plant_eval_text:
                issues.append(f"plant response eval script missing token: {token}")
    if hover_bracket_eval_script.exists():
        hover_eval_text = hover_bracket_eval_script.read_text(encoding="utf-8")
        for token in [
            "mosim.gazebo_hover_command_bracket_eval.v1",
            "near_hover_candidate",
            "over_climb",
            "grounded_or_under_thrust",
            "open-loop Gazebo thrust-scale bracket",
            "closed_loop",
            "multi-UAV readiness",
        ]:
            if token not in hover_eval_text:
                issues.append(f"hover bracket eval script missing token: {token}")
    if hover_bracket_runner.exists():
        hover_runner_text = hover_bracket_runner.read_text(encoding="utf-8")
        for token in [
            "RUN_GAZEBO=1",
            "RUN_ROS2_BRIDGE=1",
            "RUN_CONTROLLER_OUTPUT_NODE=1",
            "RUN_CONTROLLER_OUTPUT_FIXTURE=1",
            "RUN_GAZEBO_TRUTH_POSE=1",
            "RUN_PLANT_RESPONSE_EVAL=1",
            "CONTROLLER_COMMAND_VALUES",
            "GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json",
            "single_uav_hover_command_bracket",
            "START_GAZEBO_PAUSED",
            "UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND",
            "closed_loop",
        ]:
            if token not in hover_runner_text:
                issues.append(f"hover bracket runner missing token: {token}")
    if hover_hold_controller_script.exists():
        hover_hold_controller_text = hover_hold_controller_script.read_text(encoding="utf-8")
        for token in [
            "mosim.gazebo_truth_hover_hold_controller.v1",
            "ControllerOutput",
            "normalized_motor_speed",
            "target_altitude_m",
            "hover_command",
            "command_bounds",
            "attitude_command_limit",
            "bounded Gazebo-truth altitude-hold pre-acceptance controller",
            "closed_loop",
            "multi-UAV readiness",
        ]:
            if token not in hover_hold_controller_text:
                issues.append(f"hover-hold controller script missing token: {token}")
    if hover_hold_eval_script.exists():
        hover_hold_eval_text = hover_hold_eval_script.read_text(encoding="utf-8")
        for token in [
            "mosim.gazebo_hover_hold_closed_loop_eval.v1",
            "truth_samples",
            "controller_samples",
            "adapter_published",
            "final_abs_z_error_above_max",
            "max_xy_distance_above_max",
            "max_tilt_above_max",
            "bounded single-UAV Gazebo truth-feedback hover-hold pre-acceptance loop",
            "closed_loop",
            "multi-UAV readiness",
        ]:
            if token not in hover_hold_eval_text:
                issues.append(f"hover-hold eval script missing token: {token}")
    if hover_hold_runner.exists():
        hover_hold_runner_text = hover_hold_runner.read_text(encoding="utf-8")
        for token in [
            "run_sunray150_hover_hold_closed_loop",
            "single_uav_hover_hold_closed_loop_pre_acceptance",
            "ros2 run ros_gz_bridge parameter_bridge",
            "controller_output_adapter_node.trace.jsonl",
            "hover_hold_controller.json",
            "hover_hold_controller_trace.jsonl",
            "GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json",
            "HOVER_KP_ROLL",
            "HOVER_MAX_XY_DISTANCE_M",
            "gazebo_world_control.json",
            "RUN_MANIFEST.json",
            "RUNTIME_STATUS.json",
            "BLOCKER.json",
            "closed_loop",
            "multi-UAV readiness",
        ]:
            if token not in hover_hold_runner_text:
                issues.append(f"hover-hold runner missing token: {token}")

    not_claimed = claim_boundary.get("not_claimed") if isinstance(claim_boundary.get("not_claimed"), list) else []
    for forbidden_claim in ["closed_loop", "planner_ready", "multi_uav_readiness"]:
        if forbidden_claim not in not_claimed:
            issues.append(f"claim_boundary.not_claimed must include {forbidden_claim}")

    for key in ["result_dir", "run_manifest", "blocker", "preflight_json", "topic_contract_json", "runtime_status_json"]:
        if not outputs.get(key):
            issues.append(f"outputs.{key} is required")

    if runner.exists():
        runner_text = runner.read_text(encoding="utf-8")
        for token in [
            "DRY_RUN",
            "RUN_GAZEBO",
            "RUN_LOCAL_MAP",
            "RUN_RATE_CHECK",
            "RUN_TF_CHECK",
            "RUN_FASTLIO_PLANNER_INPUT_ADAPTER",
            "RUN_SPARK_FASTLIO",
            "RUN_FASTLIO_TRUTH_EVAL",
            "RUN_GAZEBO_TRUTH_POSE",
            "RUN_PLANT_RESPONSE_EVAL",
            "RUN_ACTUATOR_BRIDGE",
            "RUN_CONTROLLER_COMMAND",
            "RUN_CONTROLLER_OUTPUT_NODE",
            "RUN_CONTROLLER_OUTPUT_FIXTURE",
            "RUN_ACTUATOR_COMMAND_CHECK",
            "RUN_COMMAND_ACK_GUARD",
            "RUNTIME_GATE_PROFILE",
            "GAZEBO_RENDER_ENGINE_SERVER",
            "BUILD_MOSIM_ROS2_MSGS",
            "MOSIM_ROS2_WS",
            "CONTROLLER_OUTPUT_NODE_MAX_MESSAGES",
            "CONTROLLER_COMMAND_RATE_HZ",
            "CONTROLLER_COMMAND_TIMES",
            "COMMAND_ACK_MAX_AGE_S",
            "COMMAND_ACK_STALE_AGE_S",
            "CONTROLLER_ID",
            "FASTLIO_PLANNER_INPUT_SCRIPT",
            "FASTLIO_IMU_PASSTHROUGH_SCRIPT",
            "SPARK_FASTLIO_SETUP",
            "SPARK_FASTLIO_LAUNCH_FILE",
            "SPARK_FASTLIO_RECORDER_SCRIPT",
            "GAZEBO_TRUTH_RECORDER_SCRIPT",
            "FASTLIO_TRUTH_EVAL_SCRIPT",
            "FASTLIO_TRUTH_ERROR_EVAL",
            "GAZEBO_PLANT_RESPONSE_EVAL",
            "PLANT_RESPONSE_EVAL_SCRIPT",
            "CONTROLLER_ADAPTER_SCRIPT",
            "CONTROLLER_NODE_SCRIPT",
            "CONTROLLER_FIXTURE_SCRIPT",
            "MOSIM_MSGS_PACKAGE",
            "ROS_CONTROLLER_OUTPUT_TOPIC",
            "ROS_ACTUATOR_TOPIC",
            "CONTROLLER_ACTUATOR_ROS_TYPE",
            "CONTROLLER_ACTUATOR_GZ_TYPE",
            "ROS_LIDAR_POINTS_TOPIC",
            "ROS_LOCAL_VOXEL_TOPIC",
            "ROS_LOCAL_GRID_TOPIC",
            "ROS_FASTLIO_LIDAR_TOPIC",
            "ROS_FASTLIO_IMU_TOPIC",
            "ROS_SPARK_FASTLIO_LIVOX_TOPIC",
            "ROS_PLANNER_GLOBAL_POINTS_TOPIC",
            "ROS_PLANNER_ODOM_TOPIC",
            "ROS_SPARK_FASTLIO_REGISTERED_CLOUD_TOPIC",
            "ROS_SPARK_FASTLIO_ODOMETRY_TOPIC",
            "ROS_SPARK_FASTLIO_PATH_TOPIC",
            "PLANNER_HANDOFF_FORBIDDEN_TOPIC_EVIDENCE",
            "write_forbidden_topic_presence",
            "planner_handoff_without_setpoint_publication",
            "forbidden_topic_presence.json",
            "LOCAL_MAP_EXPECTED_INPUT_FRAME",
            "FASTLIO_PLANNER_INPUT_ARGS",
            "RUNTIME_STATUS.json",
            "BLOCKER.json",
            "RUN_MANIFEST.json",
            "LOCAL_MAP_FRAME_BOUNDARY_JSON",
            "LOCAL_MAP_FRAME_ARGS",
            "--input-frame-policy",
            "--expected-input-frame",
            "--tf-lookup-timeout-s",
            "--local-map-center-source",
            'rm -f "${RUN_MANIFEST}"',
            "ros2 run ros_gz_bridge parameter_bridge",
            "actuator_msgs/msg/Actuators@gz.msgs.Actuators",
            "controller_actuator_command.json",
            "controller_output_adapter_node.json",
            "controller_output_fixture.json",
            "command_ack_guard_report.json",
            "stale_controller_output_report.json",
            "gazebo_plant_response_eval.rc",
            "GAZEBO_PLANT_RESPONSE_EVAL.json",
            "mosim_msgs_colcon.stdout.log",
            "controller_command.rc",
            "controller_output_node.rc",
            "controller_output_fixture.rc",
            "fastlio_planner_input_adapter.json",
            "fastlio_imu_passthrough.json",
            "ign topic -e",
            "--run-actuator-command-check",
            "--run-controller-output-node",
            "--run-controller-output-fixture",
            "--run-command-ack-guard",
            "--run-fastlio-planner-input-adapter",
            "--fastlio-planner-input-alive",
            "--fastlio-imu-passthrough-alive",
            "--gate-profile",
            "--headless-rendering",
            "--render-engine-server",
            "tf2_msgs/msg/TFMessage",
            "fastlio_planner_input",
            "spark_fastlio_localization",
            "spark_fastlio_recorder.rc",
            "command_acknowledgement_without_closed_loop",
            "single_uav_plant_response_pre_acceptance",
            "--run-gazebo-truth-pose",
            "--run-plant-response-eval",
        ]:
            if token not in runner_text:
                issues.append(f"runner missing token: {token}")
        if "closed_loop" not in runner_text:
            issues.append("runner must explicitly bound closed_loop claims")
    if dependency_check.exists():
        dep_text = dependency_check.read_text(encoding="utf-8")
        for token in ["DEPENDENCY_STATUS.json", "apt-cache policy", "ros2 pkg prefix", "read-only"]:
            if token not in dep_text:
                issues.append(f"dependency check missing token: {token}")
        for forbidden in ["sudo", "apt install", "gz sim -r", "ign gazebo -r", "ros2 run ros_gz_bridge parameter_bridge"]:
            if forbidden in dep_text:
                issues.append(f"dependency check must not contain runtime/install token: {forbidden}")
    runtime_status = ROOT / "Scripts/quality/build_gazebo_ros2_runtime_status.py"
    if not runtime_status.exists():
        issues.append(f"missing runtime status checker: {rel(runtime_status)}")
    else:
        runtime_status_text = runtime_status.read_text(encoding="utf-8")
        for token in [
            "topic_rates",
            "topic_samples",
            "rate_gate_min_fraction",
            "rate_below_threshold",
            "tf_check_not_requested",
            "runtime_smoke_passed",
            "extract_frame_id",
            "topic_frame_mismatch",
            "missing_topic_frame_id",
            "local_map_frame_boundary",
            "missing_tf_chain",
            "tf_chain",
            "actuator_command",
            "controller_output",
            "controller_output_node_handoff",
            "controller_output_adapter_node_failed",
            "actuator_ros_velocity_mismatch",
            "actuator_gazebo_velocity_mismatch",
            "extract_float_values_for_field",
            "gate_profile",
            "actuator_handoff",
            "fastlio_planner_input",
            "planner_handoff_without_setpoint_publication",
            "planner_handoff_forbidden_topic_observed",
            "planner_handoff_forbidden_topic_evidence_missing",
            "forbidden_topic_presence",
            "command_acknowledgement_without_closed_loop",
            "command_ack_guard_report",
            "command_ack_stale_negative_guard_missing",
            "command acknowledgement, when requested",
            "single_uav_plant_response_pre_acceptance",
            "plant_response_pre_acceptance",
            "plant_response_gate_not_passed",
            "plant_response_eval_missing",
            "gazebo_truth_pose_recording_not_requested",
            "plant response pre-acceptance, when requested",
            "fastlio_planner_input_adapter_process_not_alive",
            "fastlio_imu_passthrough_process_not_alive",
            "fastlio_planner_input_adapter_counter_zero",
            "fastlio_imu_passthrough_counter_zero",
            "FAST-LIO/planner input handoff",
        ]:
            if token not in runtime_status_text:
                issues.append(f"runtime status checker missing token: {token}")

    return {
        "ok": not issues,
        "scenario": rel(scenario_path),
        "issues": issues,
        "warnings": warnings,
        "artifacts": {
            "world": rel(world_path),
            "model": rel(model_path),
            "sensor_fragment": rel(sensor_path),
            "local_map_script": rel(local_map_script),
            "map_review_recorder_script": rel(map_review_recorder_script),
            "fastlio_planner_input_script": rel(fastlio_planner_input_script),
            "fastlio_imu_passthrough_script": rel(fastlio_imu_passthrough_script),
            "spark_fastlio_setup": rel(spark_fastlio_setup),
            "spark_fastlio_launch_file": rel(spark_fastlio_launch_file),
            "spark_fastlio_config_path": rel(spark_fastlio_config_path),
            "spark_fastlio_recorder_script": rel(spark_fastlio_recorder_script),
            "controller_adapter_script": rel(controller_adapter_script),
            "hover_hold_runner": rel(hover_hold_runner),
            "hover_hold_controller_script": rel(hover_hold_controller_script),
            "hover_hold_eval_script": rel(hover_hold_eval_script),
            "runner": rel(runner),
            "dependency_check": rel(dependency_check),
            "runtime_status_checker": rel(ROOT / "Scripts/quality/build_gazebo_ros2_runtime_status.py"),
            "run_manifest": str(outputs.get("run_manifest", "")),
            "blocker": str(outputs.get("blocker", "")),
            "runtime_status": str(outputs.get("runtime_status_json", "")),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", default=str(DEFAULT_SCENARIO))
    parser.add_argument("--output-json")
    args = parser.parse_args()

    try:
        report = validate(repo_path(args.scenario))
    except Exception as exc:
        report = {
            "ok": False,
            "scenario": str(args.scenario),
            "issues": [f"{exc.__class__.__name__}: {exc}"],
            "warnings": [],
            "artifacts": {},
        }

    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
