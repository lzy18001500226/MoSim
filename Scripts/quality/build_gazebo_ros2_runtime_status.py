#!/usr/bin/env python3
"""Build a machine-readable Gazebo+ROS2 smoke runtime status report.

The runner writes topic-list, topic-sample, and rate-check files. This helper
turns those files into one gate result so a dry-run or partial ROS graph cannot
be mistaken for a successful Gazebo/PointCloud2/local-map validation run.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    yaml = None
    YAML_IMPORT_ERROR = exc
else:
    YAML_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[2]


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


def bool_arg(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "on"}


def topic_key(topic: str) -> str:
    cleaned = topic.strip().strip("/")
    if not cleaned:
        return "root"
    return re.sub(r"[^A-Za-z0-9_]+", "_", cleaned.replace("/", "_"))


def read_rc(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def file_nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def read_json_file(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists() or path.stat().st_size == 0:
        return {}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, f"{exc.__class__.__name__}: {exc}"
    return data if isinstance(data, dict) else {}, None


def read_header_rate(result_dir: Path, topic: str) -> tuple[dict[str, Any] | None, str | None]:
    path = result_dir / f"topic_{topic_key(topic)}_header_rate.json"
    data, error = read_json_file(path)
    if not data and error is None:
        return None, None
    if error:
        return None, error
    return data, None


def extract_frame_id(text: str) -> str | None:
    patterns = [
        r"frame_id:\s*[\"']?([^\"'\n\r]+)",
        r"frame_id=['\"]([^'\"]+)['\"]",
        r'"frame_id"\s*:\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def extract_top_level_int_field(text: str, field_name: str) -> int | None:
    pattern = rf"^{re.escape(field_name)}:\s*([0-9]+)\s*$"
    for line in text.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            return int(match.group(1))
    return None


def extract_int_values_for_field(text: str, field_name: str) -> list[int]:
    values: list[int] = []
    json_match = re.search(rf'"{re.escape(field_name)}"\s*:\s*\[([^\]]*)\]', text)
    if json_match:
        return [int(item) for item in re.findall(r"[-+]?\d+", json_match.group(1))]

    for line in text.splitlines():
        stripped = line.strip()
        scalar = re.match(rf"^(?:-\s*)?{re.escape(field_name)}:\s*([-+]?\d+)\s*$", stripped)
        if scalar:
            values.append(int(scalar.group(1)))
    return values


def extract_float_values_for_field(text: str, field_name: str) -> list[float]:
    values: list[float] = []
    json_match = re.search(rf'"{re.escape(field_name)}"\s*:\s*\[([^\]]*)\]', text)
    if json_match:
        return [
            float(item)
            for item in re.findall(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", json_match.group(1))
        ]

    lines = text.splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        inline = re.match(
            rf"^{re.escape(field_name)}:\s*\[([^\]]*)\]\s*$",
            stripped,
        )
        if inline:
            values.extend(
                float(item)
                for item in re.findall(
                    r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",
                    inline.group(1),
                )
            )
            index += 1
            continue

        scalar = re.match(
            rf"^{re.escape(field_name)}:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$",
            stripped,
        )
        if scalar:
            values.append(float(scalar.group(1)))
            index += 1
            continue

        if re.match(rf"^{re.escape(field_name)}:\s*$", stripped):
            lookahead = index + 1
            while lookahead < len(lines):
                item = lines[lookahead].strip()
                list_item = re.match(
                    r"^-\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$",
                    item,
                )
                if not list_item:
                    break
                values.append(float(list_item.group(1)))
                lookahead += 1
            index = lookahead
            continue

        index += 1
    return values


def lists_close(left: list[float], right: list[float], tolerance: float = 1e-6) -> bool:
    if len(left) != len(right):
        return False
    return all(abs(a - b) <= tolerance for a, b in zip(left, right))


def extract_tf_edges(text: str) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    parent: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        parent_match = re.match(r"frame_id:\s*[\"']?([^\"'\n\r]+)", stripped)
        if parent_match:
            parent = parent_match.group(1).strip()
            continue
        child_match = re.match(r"child_frame_id:\s*[\"']?([^\"'\n\r]+)", stripped)
        if child_match and parent:
            child = child_match.group(1).strip()
            edges.append((parent, child))
            parent = None
    return edges


def tf_chain_exists(edges: list[tuple[str, str]], source_frame: str, target_frame: str) -> bool:
    if not source_frame or not target_frame:
        return False
    if source_frame == target_frame:
        return True
    graph: dict[str, set[str]] = {}
    for parent, child in edges:
        if not parent or not child:
            continue
        graph.setdefault(parent, set()).add(child)
        graph.setdefault(child, set()).add(parent)
    frontier = [source_frame]
    seen = {source_frame}
    while frontier:
        frame = frontier.pop(0)
        for next_frame in graph.get(frame, set()):
            if next_frame == target_frame:
                return True
            if next_frame not in seen:
                seen.add(next_frame)
                frontier.append(next_frame)
    return False


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    scenario_path = repo_path(args.scenario)
    result_dir = repo_path(args.result_dir)
    scenario = read_yaml(scenario_path)
    ros2 = scenario.get("ros2") if isinstance(scenario.get("ros2"), dict) else {}
    topics = ros2.get("topics") if isinstance(ros2.get("topics"), dict) else {}
    target_rates = ros2.get("target_rates_hz") if isinstance(ros2.get("target_rates_hz"), dict) else {}
    topic_gates = ros2.get("topic_gates") if isinstance(ros2.get("topic_gates"), dict) else {}
    local_map = ros2.get("local_map_adapter") if isinstance(ros2.get("local_map_adapter"), dict) else {}
    controller_adapter = (
        ros2.get("controller_adapter") if isinstance(ros2.get("controller_adapter"), dict) else {}
    )
    try:
        rate_gate_min_fraction = float(ros2.get("rate_gate_min_fraction", 0.5))
    except (TypeError, ValueError):
        rate_gate_min_fraction = 0.5
    gate_profile = str(args.gate_profile or "sensor_local_map")
    planner_handoff_gate_required = gate_profile == "planner_handoff_without_setpoint_publication"
    ego_style_planner_gate_required = gate_profile == "ego_style_planner_output_without_actuation"
    command_ack_gate_required = gate_profile == "command_acknowledgement_without_closed_loop"
    plant_response_gate_required = gate_profile == "single_uav_plant_response_pre_acceptance"
    hover_bracket_gate_required = gate_profile == "single_uav_hover_command_bracket"
    gazebo_truth_pose_only_gate_required = gate_profile == "gazebo_truth_pose_only"
    rate_gate_required = gate_profile == "sensor_local_map"
    topic_samples_required = gate_profile == "sensor_local_map"
    tf_gate_required = gate_profile == "sensor_local_map"
    local_map_gate_required = gate_profile == "sensor_local_map"
    fastlio_planner_input_gate_required = (
        gate_profile in {
            "fastlio_planner_input",
            "planner_handoff_without_setpoint_publication",
            "ego_style_planner_output_without_actuation",
        }
        or args.run_fastlio_planner_input_adapter
    )
    spark_fastlio_gate_required = gate_profile == "spark_fastlio_localization" or args.run_spark_fastlio
    if fastlio_planner_input_gate_required:
        rate_gate_required = True
        topic_samples_required = True
        tf_gate_required = True
    if spark_fastlio_gate_required:
        rate_gate_required = False
        topic_samples_required = True
        fastlio_planner_input_gate_required = True
    controller_output_node_gate_required = (
        gate_profile == "controller_output_node_handoff"
        or command_ack_gate_required
        or plant_response_gate_required
        or hover_bracket_gate_required
        or args.run_controller_output_node
        or args.run_controller_output_fixture
    )
    actuator_gate_required = (
        gate_profile in {"actuator_handoff", "controller_output_node_handoff", "command_acknowledgement_without_closed_loop", "single_uav_plant_response_pre_acceptance", "single_uav_hover_command_bracket"}
        or args.run_actuator_command_check
    )
    local_map_frame_boundary = {
        "map_frame": local_map.get("map_frame", "map"),
        "sensor_frame": local_map.get("sensor_frame", ""),
        "frame_assumption": local_map.get("frame_assumption", ""),
        "input_frame_policy": local_map.get("input_frame_policy", ""),
        "expected_input_frame": local_map.get("expected_input_frame", local_map.get("map_frame", "map")),
        "tf_lookup_timeout_s": local_map.get("tf_lookup_timeout_s", 0.2),
        "local_map_center_source": local_map.get("local_map_center_source", "map_origin"),
        "runtime_frame_gate": local_map.get("runtime_frame_gate", ""),
    }

    topic_list_path = result_dir / "ros2_topic_list.txt"
    observed_topics = []
    if topic_list_path.exists():
        observed_topics = [
            line.strip()
            for line in topic_list_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]

    required_samples: list[tuple[str, str, bool]] = []
    if gate_profile == "sensor_local_map":
        required_samples.extend(
            [
                ("imu", str(topics.get("imu", "")), True),
                ("lidar_points", str(topics.get("lidar_points", "")), True),
            ]
        )
    if fastlio_planner_input_gate_required:
        required_samples.extend(
            [
                ("lidar_points", str(topics.get("lidar_points", "")), True),
                ("fastlio_lidar", str(topics.get("fastlio_lidar", "")), True),
                ("fastlio_imu", str(topics.get("fastlio_imu", "")), True),
                ("spark_fastlio_livox", str(topics.get("spark_fastlio_livox", "")), True),
                ("sunray_fastlio_lidar", str(topics.get("sunray_fastlio_lidar", "")), True),
                ("sunray_fastlio_imu", str(topics.get("sunray_fastlio_imu", "")), True),
                ("planner_odom", str(topics.get("planner_odom", "")), True),
                ("mosim_planner_odom", str(topics.get("mosim_planner_odom", "")), True),
            ]
        )
        if gate_profile in {
            "fastlio_planner_input",
            "planner_handoff_without_setpoint_publication",
            "ego_style_planner_output_without_actuation",
        }:
            required_samples.extend(
                [
                    ("planner_global_points", str(topics.get("planner_global_points", "")), True),
                    ("mosim_planner_global_points", str(topics.get("mosim_planner_global_points", "")), True),
                ]
            )
    if ego_style_planner_gate_required:
        required_samples.extend(
            [
                ("reference_position_cmd", str(topics.get("reference_position_cmd", "/position_cmd")), False),
                (
                    "mosim_planner_position_cmd",
                    str(topics.get("mosim_planner_position_cmd", "/mosim/planner/position_cmd")),
                    False,
                ),
                ("planner_setpoint", str(topics.get("planner_setpoint", "/mosim/planner/setpoint")), False),
                (
                    "planner_setpoint_adapter_status",
                    str(topics.get("planner_setpoint_adapter_status", "/mosim/planner/setpoint_adapter_status")),
                    True,
                ),
            ]
        )
    if spark_fastlio_gate_required:
        required_samples.extend(
            [
                ("spark_fastlio_registered_cloud", str(topics.get("spark_fastlio_registered_cloud", "")), True),
                ("spark_fastlio_odometry", str(topics.get("spark_fastlio_odometry", "")), True),
                ("spark_fastlio_path", str(topics.get("spark_fastlio_path", "")), True),
            ]
        )
    if args.run_local_map:
        required_samples.extend(
            [
                ("local_occupancy_voxels", str(topics.get("local_occupancy_voxels", "")), True),
                ("local_occupancy_grid", str(topics.get("local_occupancy_grid", "")), True),
            ]
        )
    if args.run_tf_check:
        required_samples.append(("tf_static", str(topics.get("tf_static") or topics.get("tf", "")), True))

    sample_results: dict[str, Any] = {}
    for name, topic, required in required_samples:
        key = topic_key(topic)
        stdout_path = result_dir / f"topic_{key}_once.txt"
        stderr_path = result_dir / f"topic_{key}_once.stderr.txt"
        rc_path = result_dir / f"topic_{key}_once.rc"
        rc = read_rc(rc_path)
        sample_text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
        sample_recorded = rc == 0 and file_nonempty(stdout_path)
        sample_results[name] = {
            "topic": topic,
            "required": required,
            "topic_present": topic in observed_topics,
            "sample_stdout": rel(stdout_path),
            "sample_stderr": rel(stderr_path),
            "sample_returncode": rc,
            "sample_bytes": stdout_path.stat().st_size if stdout_path.exists() else 0,
            "sample_recorded": sample_recorded,
            "frame_id": extract_frame_id(sample_text),
            "sample_width": extract_top_level_int_field(sample_text, "width"),
            "sample_height": extract_top_level_int_field(sample_text, "height"),
            "sample_point_num": extract_top_level_int_field(sample_text, "point_num"),
            "sample_line_values": extract_int_values_for_field(sample_text, "line")[:32],
            "sample_offset_time_values": extract_int_values_for_field(sample_text, "offset_time")[:32],
            "tf_edges": extract_tf_edges(sample_text) if name in {"tf", "tf_static"} else [],
        }
        width = sample_results[name]["sample_width"]
        height = sample_results[name]["sample_height"]
        point_num = sample_results[name]["sample_point_num"]
        if isinstance(width, int) and isinstance(height, int):
            sample_results[name]["sample_point_count"] = int(width) * int(height)
            sample_results[name]["sample_point_count_source"] = "width_times_height"
        elif isinstance(point_num, int):
            sample_results[name]["sample_point_count"] = int(point_num)
            sample_results[name]["sample_point_count_source"] = "point_num"
        else:
            sample_results[name]["sample_point_count"] = None
            sample_results[name]["sample_point_count_source"] = None
        sample_results[name]["observed"] = bool(sample_results[name]["topic_present"]) or sample_recorded

    def observed_by_sample_or_rate(topic: str) -> bool:
        if not topic:
            return False
        key = topic_key(topic)
        sample_path = result_dir / f"topic_{key}_once.txt"
        sample_rc = read_rc(result_dir / f"topic_{key}_once.rc")
        if sample_rc == 0 and file_nonempty(sample_path):
            return True
        rate_path = result_dir / f"topic_{key}_hz.txt"
        rate_rc = read_rc(result_dir / f"topic_{key}_hz.rc")
        if rate_path.exists() and rate_rc in {0, 124}:
            rate_text = rate_path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"average\s+rate:\s*[0-9.]+", rate_text):
                return True
        header_rate_path = result_dir / f"topic_{key}_header_rate.json"
        header_rate, header_rate_error = read_json_file(header_rate_path)
        if header_rate_error is None and isinstance(header_rate, dict):
            header_stamp_rate = header_rate.get("header_stamp_rate", {})
            receive_wall_rate = header_rate.get("receive_wall_rate", {})
            if (
                isinstance(header_stamp_rate, dict)
                and isinstance(header_stamp_rate.get("average_rate_hz"), (int, float))
            ):
                return True
            if (
                isinstance(receive_wall_rate, dict)
                and isinstance(receive_wall_rate.get("average_rate_hz"), (int, float))
            ):
                return True
        return False

    map_review_path = result_dir / "map_review" / "GAZEBO_ROS2_MAP_REVIEW.json"
    map_review, _map_review_error = read_json_file(map_review_path)
    if isinstance(map_review, dict) and map_review.get("gate_passed") is True:
        artifacts = map_review.get("artifacts", {}) if isinstance(map_review.get("artifacts"), dict) else {}
        lidar_artifact = artifacts.get("lidar_pointcloud", {}) if isinstance(artifacts, dict) else {}
        voxel_artifact = artifacts.get("local_occupancy_voxels", {}) if isinstance(artifacts, dict) else {}
        grid_artifact = artifacts.get("local_occupancy_grid", {}) if isinstance(artifacts, dict) else {}
        if "lidar_points" in sample_results and not sample_results["lidar_points"].get("sample_recorded"):
            if isinstance(lidar_artifact, dict) and lidar_artifact.get("topic") == sample_results["lidar_points"].get("topic"):
                sample_results["lidar_points"].update(
                    {
                        "sample_recorded": True,
                        "observed": True,
                        "sample_recorded_by_map_review": True,
                        "sample_source": rel(map_review_path),
                        "frame_id": lidar_artifact.get("frame_id"),
                        "sample_width": lidar_artifact.get("width"),
                        "sample_height": lidar_artifact.get("height"),
                        "sample_point_count": lidar_artifact.get("raw_point_count"),
                        "sample_point_count_source": "map_review_raw_point_count",
                        "finite_point_count": lidar_artifact.get("finite_point_count"),
                    }
                )
        if "local_occupancy_voxels" in sample_results and not sample_results["local_occupancy_voxels"].get("sample_recorded"):
            if isinstance(voxel_artifact, dict) and voxel_artifact.get("topic") == sample_results["local_occupancy_voxels"].get("topic"):
                sample_results["local_occupancy_voxels"].update(
                    {
                        "sample_recorded": True,
                        "observed": True,
                        "sample_recorded_by_map_review": True,
                        "sample_source": rel(map_review_path),
                        "frame_id": voxel_artifact.get("frame_id"),
                        "sample_width": voxel_artifact.get("width"),
                        "sample_height": voxel_artifact.get("height"),
                        "sample_point_count": voxel_artifact.get("raw_point_count"),
                        "sample_point_count_source": "map_review_raw_point_count",
                        "finite_point_count": voxel_artifact.get("finite_point_count"),
                    }
                )
        if "local_occupancy_grid" in sample_results and not sample_results["local_occupancy_grid"].get("sample_recorded"):
            if isinstance(grid_artifact, dict) and grid_artifact.get("topic") == sample_results["local_occupancy_grid"].get("topic"):
                sample_results["local_occupancy_grid"].update(
                    {
                        "sample_recorded": True,
                        "observed": True,
                        "sample_recorded_by_map_review": True,
                        "sample_source": rel(map_review_path),
                        "frame_id": grid_artifact.get("frame_id"),
                        "sample_width": grid_artifact.get("width"),
                        "sample_height": grid_artifact.get("height"),
                        "sample_point_count": int(grid_artifact.get("width", 0)) * int(grid_artifact.get("height", 0)),
                        "sample_point_count_source": "map_review_grid_dimensions",
                    }
                )

    controller_output_topic = str(controller_adapter.get("input_topic") or topics.get("controller_output", ""))
    controller_output_key = topic_key(controller_output_topic)
    controller_output_stdout = result_dir / f"topic_{controller_output_key}_once.txt"
    controller_output_stderr = result_dir / f"topic_{controller_output_key}_once.stderr.txt"
    controller_output_text = (
        controller_output_stdout.read_text(encoding="utf-8", errors="replace")
        if controller_output_stdout.exists()
        else ""
    )
    controller_output_command = extract_float_values_for_field(controller_output_text, "command")
    controller_output: dict[str, Any] = {
        "requested": controller_output_node_gate_required,
        "topic": controller_output_topic,
        "type": str(controller_adapter.get("ros_message", "mosim_msgs/msg/ControllerOutput")),
        "topic_present": controller_output_topic in observed_topics,
        "sample_stdout": rel(controller_output_stdout),
        "sample_stderr": rel(controller_output_stderr),
        "sample_returncode": read_rc(result_dir / f"topic_{controller_output_key}_once.rc"),
        "sample_bytes": controller_output_stdout.stat().st_size if controller_output_stdout.exists() else 0,
        "sample_recorded": read_rc(result_dir / f"topic_{controller_output_key}_once.rc") == 0
        and file_nonempty(controller_output_stdout),
        "command": controller_output_command,
        "fixture_report": rel(result_dir / "controller_output_fixture.json"),
        "fixture_returncode": read_rc(result_dir / "controller_output_fixture.rc"),
        "node_report": rel(result_dir / "controller_output_adapter_node.json"),
        "node_trace": rel(result_dir / "controller_output_adapter_node.trace.jsonl"),
        "node_returncode": read_rc(result_dir / "controller_output_node.rc"),
        "node_status": None,
        "node_input_command_type": None,
        "node_input_command": None,
        "node_velocity": None,
    }
    controller_output["observed_by_topic_list_or_sample"] = (
        bool(controller_output["topic_present"]) or bool(controller_output["sample_recorded"])
    )
    controller_output["observed"] = controller_output["observed_by_topic_list_or_sample"]

    node_report_path = result_dir / "controller_output_adapter_node.json"
    node_velocity: list[float] = []
    if node_report_path.exists():
        try:
            node_report = json.loads(node_report_path.read_text(encoding="utf-8"))
            node_velocity = [float(item) for item in node_report.get("velocity", [])]
            controller_output["node_status"] = node_report.get("status")
            controller_output["node_input_command_type"] = node_report.get("input_command_type")
            controller_output["node_input_command"] = node_report.get("input_command")
            controller_output["node_velocity"] = node_velocity
        except Exception as exc:
            controller_output["node_report_error"] = f"{exc.__class__.__name__}: {exc}"

    actuator_command_topic = str(controller_adapter.get("ros_actuator_topic") or topics.get("actuator_command", ""))
    controller_report_path = (
        result_dir / "controller_output_adapter_node.json"
        if controller_output_node_gate_required
        else result_dir / "controller_actuator_command.json"
    )
    actuator_command: dict[str, Any] = {
        "requested": args.run_actuator_command_check,
        "ros_topic": actuator_command_topic,
        "gz_topic": str(controller_adapter.get("gz_actuator_topic") or topics.get("actuator_command", "")),
        "ros_type": str(controller_adapter.get("ros_type", "actuator_msgs/msg/Actuators")),
        "gz_type": str(controller_adapter.get("gz_type", "gz.msgs.Actuators")),
        "controller_report": rel(controller_report_path),
        "controller_publish_stdout": rel(
            result_dir
            / ("controller_output_fixture.stdout.log" if controller_output_node_gate_required else "controller_command.stdout.txt")
        ),
        "controller_publish_stderr": rel(
            result_dir
            / ("controller_output_fixture.stderr.log" if controller_output_node_gate_required else "controller_command.stderr.txt")
        ),
        "controller_publish_returncode": (
            read_rc(result_dir / "controller_output_fixture.rc")
            if controller_output_node_gate_required
            else read_rc(result_dir / "controller_command.rc")
        ),
        "expected_velocity": None,
        "ros_echo": {},
        "gz_echo": {},
        "ros_velocity_matches_expected": False,
        "gz_velocity_matches_expected": False,
    }
    expected_velocity: list[float] = []
    if controller_report_path.exists():
        try:
            controller_report = json.loads(controller_report_path.read_text(encoding="utf-8"))
            expected_velocity = [float(item) for item in controller_report.get("velocity", [])]
            actuator_command["expected_velocity"] = expected_velocity
            actuator_command["controller_report_status"] = controller_report.get("status")
            actuator_command["controller_input_command_type"] = controller_report.get("input_command_type")
        except Exception as exc:
            actuator_command["controller_report_error"] = f"{exc.__class__.__name__}: {exc}"

    if actuator_command_topic:
        ros_key = topic_key(actuator_command_topic)
        ros_stdout = result_dir / f"topic_{ros_key}_once.txt"
        ros_stderr = result_dir / f"topic_{ros_key}_once.stderr.txt"
        ros_text = ros_stdout.read_text(encoding="utf-8", errors="replace") if ros_stdout.exists() else ""
        ros_velocity = extract_float_values_for_field(ros_text, "velocity")
        actuator_command["ros_echo"] = {
            "topic": actuator_command_topic,
            "topic_present": actuator_command_topic in observed_topics,
            "sample_stdout": rel(ros_stdout),
            "sample_stderr": rel(ros_stderr),
            "sample_returncode": read_rc(result_dir / f"topic_{ros_key}_once.rc"),
            "sample_bytes": ros_stdout.stat().st_size if ros_stdout.exists() else 0,
            "sample_recorded": read_rc(result_dir / f"topic_{ros_key}_once.rc") == 0 and file_nonempty(ros_stdout),
            "velocity": ros_velocity,
        }
        actuator_command["ros_velocity_matches_expected"] = (
            bool(expected_velocity) and lists_close(ros_velocity, expected_velocity)
        )

    gz_topic = str(actuator_command["gz_topic"])
    if gz_topic:
        gz_key = topic_key(gz_topic)
        gz_stdout = result_dir / f"gz_topic_{gz_key}_once.txt"
        gz_stderr = result_dir / f"gz_topic_{gz_key}_once.stderr.txt"
        gz_text = gz_stdout.read_text(encoding="utf-8", errors="replace") if gz_stdout.exists() else ""
        gz_velocity = extract_float_values_for_field(gz_text, "velocity")
        actuator_command["gz_echo"] = {
            "topic": gz_topic,
            "sample_stdout": rel(gz_stdout),
            "sample_stderr": rel(gz_stderr),
            "sample_returncode": read_rc(result_dir / f"gz_topic_{gz_key}_once.rc"),
            "sample_bytes": gz_stdout.stat().st_size if gz_stdout.exists() else 0,
            "sample_recorded": read_rc(result_dir / f"gz_topic_{gz_key}_once.rc") == 0 and file_nonempty(gz_stdout),
            "velocity": gz_velocity,
        }
    actuator_command["gz_velocity_matches_expected"] = (
            bool(expected_velocity) and lists_close(gz_velocity, expected_velocity)
        )

    fastlio_adapter = (
        ros2.get("fastlio_planner_input_adapter")
        if isinstance(ros2.get("fastlio_planner_input_adapter"), dict)
        else {}
    )
    fastlio_imu_passthrough_cfg = (
        ros2.get("fastlio_imu_passthrough")
        if isinstance(ros2.get("fastlio_imu_passthrough"), dict)
        else {}
    )
    fastlio_report_path = result_dir / "fastlio_planner_input_adapter.json"
    fastlio_report: dict[str, Any] = {
        "requested": fastlio_planner_input_gate_required,
        "adapter_report": rel(fastlio_report_path),
        "adapter_status": None,
        "adapter_counts": {},
        "adapter_report_recorded": fastlio_report_path.exists() and fastlio_report_path.stat().st_size > 0,
        "runtime_gate": fastlio_adapter.get("runtime_gate", ""),
        "runtime_gate_claim": fastlio_adapter.get("runtime_gate_claim", ""),
        "compatible_reference_inputs": fastlio_adapter.get("compatible_reference_inputs", {}),
    }
    if fastlio_report_path.exists():
        try:
            parsed_fastlio_report = json.loads(fastlio_report_path.read_text(encoding="utf-8"))
            fastlio_report["adapter_status"] = parsed_fastlio_report.get("status")
            fastlio_report["adapter_counts"] = parsed_fastlio_report.get("counts", {})
            fastlio_report["adapter_frames"] = parsed_fastlio_report.get("frames", {})
            fastlio_report["adapter_outputs"] = parsed_fastlio_report.get("outputs", {})
            fastlio_report["imu_output"] = parsed_fastlio_report.get("imu_output", {})
        except Exception as exc:
            fastlio_report["adapter_report_error"] = f"{exc.__class__.__name__}: {exc}"
    fastlio_imu_passthrough_path = result_dir / "fastlio_imu_passthrough.json"
    fastlio_imu_passthrough_report: dict[str, Any] = {
        "requested": fastlio_planner_input_gate_required,
        "adapter_report": rel(fastlio_imu_passthrough_path),
        "adapter_status": None,
        "adapter_counts": {},
        "adapter_report_recorded": (
            fastlio_imu_passthrough_path.exists() and fastlio_imu_passthrough_path.stat().st_size > 0
        ),
        "runtime_gate": fastlio_imu_passthrough_cfg.get("runtime_gate", ""),
        "runtime_gate_claim": fastlio_imu_passthrough_cfg.get("runtime_gate_claim", ""),
    }
    if fastlio_imu_passthrough_path.exists():
        try:
            parsed_fastlio_imu_report = json.loads(fastlio_imu_passthrough_path.read_text(encoding="utf-8"))
            fastlio_imu_passthrough_report["adapter_status"] = parsed_fastlio_imu_report.get("status")
            fastlio_imu_passthrough_report["adapter_counts"] = parsed_fastlio_imu_report.get("counts", {})
            fastlio_imu_passthrough_report["adapter_frames"] = parsed_fastlio_imu_report.get("frames", {})
            fastlio_imu_passthrough_report["adapter_outputs"] = parsed_fastlio_imu_report.get("outputs", {})
            fastlio_imu_passthrough_report["observed_input_average_hz"] = parsed_fastlio_imu_report.get(
                "observed_input_average_hz"
            )
        except Exception as exc:
            fastlio_imu_passthrough_report["adapter_report_error"] = f"{exc.__class__.__name__}: {exc}"

    planner_handoff_cfg = (
        ros2.get("planner_handoff_without_setpoint_publication")
        if isinstance(ros2.get("planner_handoff_without_setpoint_publication"), dict)
        else {}
    )
    forbidden_topic_evidence_name = str(
        planner_handoff_cfg.get("forbidden_topic_evidence", "forbidden_topic_presence.json")
    )
    forbidden_topic_evidence_path = result_dir / forbidden_topic_evidence_name
    forbidden_topic_evidence: dict[str, Any] = {}
    forbidden_topic_evidence_error: str | None = None
    if forbidden_topic_evidence_path.exists() and forbidden_topic_evidence_path.stat().st_size > 0:
        try:
            forbidden_topic_evidence = json.loads(forbidden_topic_evidence_path.read_text(encoding="utf-8"))
        except Exception as exc:
            forbidden_topic_evidence_error = f"{exc.__class__.__name__}: {exc}"
    configured_required_topics = (
        planner_handoff_cfg.get("required_topics")
        if isinstance(planner_handoff_cfg.get("required_topics"), list)
        else []
    )
    configured_forbidden_topics = (
        planner_handoff_cfg.get("forbidden_topics")
        if isinstance(planner_handoff_cfg.get("forbidden_topics"), list)
        else []
    )
    forbidden_topics = [str(item) for item in configured_forbidden_topics if str(item)]
    forbidden_present_from_evidence = (
        forbidden_topic_evidence.get("forbidden_present")
        if isinstance(forbidden_topic_evidence.get("forbidden_present"), list)
        else []
    )
    forbidden_present = sorted(
        {
            str(item)
            for item in forbidden_present_from_evidence
            if str(item)
        }
        | {topic for topic in forbidden_topics if topic in observed_topics}
    )
    planner_handoff_report: dict[str, Any] = {
        "requested": planner_handoff_gate_required,
        "runtime_gate": planner_handoff_cfg.get("runtime_gate", ""),
        "runtime_gate_claim": planner_handoff_cfg.get("runtime_gate_claim", ""),
        "required_topics": [str(item) for item in configured_required_topics],
        "forbidden_topics": forbidden_topics,
        "forbidden_topic_evidence": rel(forbidden_topic_evidence_path),
        "forbidden_topic_evidence_recorded": (
            forbidden_topic_evidence_path.exists() and forbidden_topic_evidence_path.stat().st_size > 0
        ),
        "forbidden_topic_evidence_error": forbidden_topic_evidence_error,
        "forbidden_present": forbidden_present,
        "all_forbidden_absent": not forbidden_present,
        "not_claimed": planner_handoff_cfg.get("not_claimed", []),
    }

    command_ack_cfg = (
        ros2.get("command_acknowledgement_without_closed_loop")
        if isinstance(ros2.get("command_acknowledgement_without_closed_loop"), dict)
        else {}
    )
    command_ack_report_path = result_dir / str(
        command_ack_cfg.get("guard_report", "command_ack_guard_report.json")
    )
    command_ack_report: dict[str, Any] = {}
    command_ack_error: str | None = None
    if command_ack_report_path.exists() and command_ack_report_path.stat().st_size > 0:
        try:
            command_ack_report = json.loads(command_ack_report_path.read_text(encoding="utf-8"))
        except Exception as exc:
            command_ack_error = f"{exc.__class__.__name__}: {exc}"
    command_ack_forbidden_topics = [
        str(item)
        for item in command_ack_cfg.get("forbidden_topics", [])
        if str(item)
    ] if isinstance(command_ack_cfg.get("forbidden_topics"), list) else []
    command_ack_forbidden_present = sorted(
        topic for topic in command_ack_forbidden_topics if topic in observed_topics
    )
    command_acknowledgement: dict[str, Any] = {
        "requested": command_ack_gate_required,
        "runtime_gate": command_ack_cfg.get("runtime_gate", ""),
        "runtime_gate_claim": command_ack_cfg.get("runtime_gate_claim", ""),
        "guard_report": rel(command_ack_report_path),
        "guard_report_recorded": command_ack_report_path.exists() and command_ack_report_path.stat().st_size > 0,
        "guard_report_error": command_ack_error,
        "positive_path": (
            command_ack_report.get("positive_path", {})
            if isinstance(command_ack_report.get("positive_path"), dict)
            else {}
        ),
        "stale_negative_path": (
            command_ack_report.get("stale_negative_path", {})
            if isinstance(command_ack_report.get("stale_negative_path"), dict)
            else {}
        ),
        "forbidden_topics": command_ack_forbidden_topics,
        "forbidden_present": command_ack_forbidden_present,
        "all_forbidden_absent": not command_ack_forbidden_present,
        "not_claimed": command_ack_cfg.get("not_claimed", []),
    }

    ego_cfg = (
        ros2.get("ego_style_planner_output_without_actuation")
        if isinstance(ros2.get("ego_style_planner_output_without_actuation"), dict)
        else {}
    )
    ego_report_path = result_dir / str(ego_cfg.get("output_json", "EGO_STYLE_PLANNER_OUTPUT_GATE.json"))
    ego_report_data, ego_report_error = read_json_file(ego_report_path)
    ego_forbidden_topics = [
        str(item)
        for item in ego_cfg.get("forbidden_topics", [])
        if str(item)
    ] if isinstance(ego_cfg.get("forbidden_topics"), list) else []
    ego_required_input_topics = [
        str(item)
        for item in ego_cfg.get("required_input_topics", [])
        if str(item)
    ] if isinstance(ego_cfg.get("required_input_topics"), list) else []
    ego_required_output_topics = [
        str(item)
        for item in ego_cfg.get("required_output_topics", [])
        if str(item)
    ] if isinstance(ego_cfg.get("required_output_topics"), list) else []
    ego_forbidden_present = sorted(topic for topic in ego_forbidden_topics if topic in observed_topics)
    ego_counts = ego_report_data.get("counts", {}) if isinstance(ego_report_data.get("counts"), dict) else {}
    ego_style_planner: dict[str, Any] = {
        "requested": ego_style_planner_gate_required,
        "runtime_gate": ego_cfg.get("runtime_gate", ""),
        "runtime_gate_claim": ego_cfg.get("runtime_gate_claim", ""),
        "report": rel(ego_report_path),
        "report_recorded": ego_report_path.exists() and ego_report_path.stat().st_size > 0,
        "report_error": ego_report_error,
        "report_status": ego_report_data.get("status"),
        "report_gate_passed": bool(ego_report_data.get("gate_passed", False)),
        "counts": ego_counts,
        "required_input_topics": ego_required_input_topics,
        "required_output_topics": ego_required_output_topics,
        "forbidden_topics": ego_forbidden_topics,
        "forbidden_present": ego_forbidden_present,
        "all_forbidden_absent": not ego_forbidden_present,
        "min_position_cmd_samples": int(ego_cfg.get("min_position_cmd_samples", 0) or 0),
        "min_setpoint_samples": int(ego_cfg.get("min_setpoint_samples", 0) or 0),
        "not_claimed": ego_cfg.get("not_claimed", []),
    }

    spark_fastlio_runtime = (
        ros2.get("spark_fastlio_runtime")
        if isinstance(ros2.get("spark_fastlio_runtime"), dict)
        else {}
    )
    spark_output_dir = result_dir / str(spark_fastlio_runtime.get("output_dir", "fastlio_runtime"))
    spark_recording_path = spark_output_dir / "FASTLIO_RUNTIME_RECORDING.json"
    spark_recorder_rc = read_rc(result_dir / "spark_fastlio_recorder.rc")
    spark_recording: dict[str, Any] = {}
    spark_recording_error: str | None = None
    if spark_recording_path.exists() and spark_recording_path.stat().st_size > 0:
        try:
            spark_recording = json.loads(spark_recording_path.read_text(encoding="utf-8"))
        except Exception as exc:
            spark_recording_error = f"{exc.__class__.__name__}: {exc}"
    spark_fastlio_report: dict[str, Any] = {
        "requested": spark_fastlio_gate_required,
        "runtime_gate": spark_fastlio_runtime.get("runtime_gate", ""),
        "runtime_gate_claim": spark_fastlio_runtime.get("runtime_gate_claim", ""),
        "workspace_setup": spark_fastlio_runtime.get("workspace_setup", ""),
        "launch_file": spark_fastlio_runtime.get("launch_file", ""),
        "config_path": spark_fastlio_runtime.get("config_path", ""),
        "recorder_script": spark_fastlio_runtime.get("recorder_script", ""),
        "input_topics": {
            "lidar": spark_fastlio_runtime.get("input_lidar_topic", ""),
            "imu": spark_fastlio_runtime.get("input_imu_topic", ""),
        },
        "output_topics": {
            "registered_cloud": spark_fastlio_runtime.get(
                "output_registered_cloud_topic", topics.get("spark_fastlio_registered_cloud", "")
            ),
            "odometry": spark_fastlio_runtime.get(
                "output_odometry_topic", topics.get("spark_fastlio_odometry", "")
            ),
            "path": spark_fastlio_runtime.get("output_path_topic", topics.get("spark_fastlio_path", "")),
        },
        "frames": {
            "map_frame": spark_fastlio_runtime.get("map_frame", "map"),
            "base_frame": spark_fastlio_runtime.get("base_frame", ""),
            "lidar_frame": spark_fastlio_runtime.get("lidar_frame", ""),
            "imu_frame": spark_fastlio_runtime.get("imu_frame", ""),
        },
        "output_dir": rel(spark_output_dir),
        "recording": rel(spark_recording_path),
        "recording_recorded": spark_recording_path.exists() and spark_recording_path.stat().st_size > 0,
        "recording_error": spark_recording_error,
        "recorder_returncode": spark_recorder_rc,
        "recording_counts": spark_recording.get("counts", {}) if isinstance(spark_recording, dict) else {},
        "recording_outputs": spark_recording.get("outputs", {}) if isinstance(spark_recording, dict) else {},
    }
    gazebo_truth_pose_cfg = (
        ros2.get("gazebo_truth_pose")
        if isinstance(ros2.get("gazebo_truth_pose"), dict)
        else {}
    )
    fastlio_truth_eval_cfg = (
        ros2.get("fastlio_truth_error_eval")
        if isinstance(ros2.get("fastlio_truth_error_eval"), dict)
        else {}
    )
    truth_recording_path = result_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    truth_recording: dict[str, Any] = {}
    truth_recording_error: str | None = None
    if truth_recording_path.exists() and truth_recording_path.stat().st_size > 0:
        try:
            truth_recording = json.loads(truth_recording_path.read_text(encoding="utf-8"))
        except Exception as exc:
            truth_recording_error = f"{exc.__class__.__name__}: {exc}"
    fastlio_truth_eval_path = result_dir / "FASTLIO_TRUTH_ERROR_EVAL.json"
    fastlio_truth_eval: dict[str, Any] = {}
    fastlio_truth_eval_error: str | None = None
    if fastlio_truth_eval_path.exists() and fastlio_truth_eval_path.stat().st_size > 0:
        try:
            fastlio_truth_eval = json.loads(fastlio_truth_eval_path.read_text(encoding="utf-8"))
        except Exception as exc:
            fastlio_truth_eval_error = f"{exc.__class__.__name__}: {exc}"
    fastlio_truth_error_report = {
        "requested": args.run_fastlio_truth_eval,
        "runtime_gate": fastlio_truth_eval_cfg.get("runtime_gate", ""),
        "runtime_gate_claim": fastlio_truth_eval_cfg.get("runtime_gate_claim", ""),
        "truth_topic": gazebo_truth_pose_cfg.get("topic", ""),
        "truth_model_name": gazebo_truth_pose_cfg.get("model_name", ""),
        "truth_recorder_script": gazebo_truth_pose_cfg.get("recorder_script", ""),
        "truth_recording": rel(truth_recording_path),
        "truth_recording_recorded": truth_recording_path.exists() and truth_recording_path.stat().st_size > 0,
        "truth_recording_returncode": read_rc(result_dir / "gazebo_truth_pose_recorder.rc"),
        "truth_recording_error": truth_recording_error,
        "truth_recording_count": truth_recording.get("count") if isinstance(truth_recording, dict) else None,
        "eval_script": fastlio_truth_eval_cfg.get("script", ""),
        "eval_json": rel(fastlio_truth_eval_path),
        "eval_recorded": fastlio_truth_eval_path.exists() and fastlio_truth_eval_path.stat().st_size > 0,
        "eval_returncode": read_rc(result_dir / "fastlio_truth_error_eval.rc"),
        "eval_error": fastlio_truth_eval_error,
        "eval_status": fastlio_truth_eval.get("status") if isinstance(fastlio_truth_eval, dict) else None,
        "gate_passed": bool(fastlio_truth_eval.get("gate_passed")) if isinstance(fastlio_truth_eval, dict) else False,
        "metrics": fastlio_truth_eval.get("metrics", {}) if isinstance(fastlio_truth_eval, dict) else {},
        "alignment": fastlio_truth_eval.get("alignment", {}) if isinstance(fastlio_truth_eval, dict) else {},
        "blockers": fastlio_truth_eval.get("blockers", []) if isinstance(fastlio_truth_eval, dict) else [],
        "warnings": fastlio_truth_eval.get("warnings", []) if isinstance(fastlio_truth_eval, dict) else [],
    }
    plant_response_cfg = (
        ros2.get("single_uav_plant_response_pre_acceptance")
        if isinstance(ros2.get("single_uav_plant_response_pre_acceptance"), dict)
        else {}
    )
    plant_response_eval_path = result_dir / str(
        plant_response_cfg.get("output_json", "GAZEBO_PLANT_RESPONSE_EVAL.json")
    )
    plant_response_eval: dict[str, Any] = {}
    plant_response_eval_error: str | None = None
    if plant_response_eval_path.exists() and plant_response_eval_path.stat().st_size > 0:
        try:
            plant_response_eval = json.loads(plant_response_eval_path.read_text(encoding="utf-8"))
        except Exception as exc:
            plant_response_eval_error = f"{exc.__class__.__name__}: {exc}"
    plant_response_report = {
        "requested": plant_response_gate_required or args.run_plant_response_eval,
        "runtime_gate": plant_response_cfg.get("runtime_gate", ""),
        "runtime_gate_claim": plant_response_cfg.get("runtime_gate_claim", ""),
        "truth_topic": gazebo_truth_pose_cfg.get("topic", ""),
        "truth_model_name": gazebo_truth_pose_cfg.get("model_name", ""),
        "truth_recorder_script": gazebo_truth_pose_cfg.get("recorder_script", ""),
        "truth_recording": rel(truth_recording_path),
        "truth_recording_recorded": truth_recording_path.exists() and truth_recording_path.stat().st_size > 0,
        "truth_recording_returncode": read_rc(result_dir / "gazebo_truth_pose_recorder.rc"),
        "truth_recording_error": truth_recording_error,
        "truth_recording_count": truth_recording.get("count") if isinstance(truth_recording, dict) else None,
        "eval_script": plant_response_cfg.get("script", ""),
        "eval_json": rel(plant_response_eval_path),
        "eval_recorded": plant_response_eval_path.exists() and plant_response_eval_path.stat().st_size > 0,
        "eval_returncode": read_rc(result_dir / "gazebo_plant_response_eval.rc"),
        "eval_error": plant_response_eval_error,
        "eval_status": plant_response_eval.get("status") if isinstance(plant_response_eval, dict) else None,
        "gate_passed": bool(plant_response_eval.get("gate_passed")) if isinstance(plant_response_eval, dict) else False,
        "plant_response": plant_response_eval.get("plant_response", {}) if isinstance(plant_response_eval, dict) else {},
        "truth_summary": plant_response_eval.get("truth_recording", {}) if isinstance(plant_response_eval, dict) else {},
        "blockers": plant_response_eval.get("blockers", []) if isinstance(plant_response_eval, dict) else [],
        "warnings": plant_response_eval.get("warnings", []) if isinstance(plant_response_eval, dict) else [],
        "not_claimed": plant_response_cfg.get("not_claimed", []),
    }
    world_control_path = result_dir / "gazebo_world_control.json"
    world_control_data, world_control_error = read_json_file(world_control_path)
    world_control_report = {
        "requested": args.start_gazebo_paused or args.unpause_gazebo_after_controller_command,
        "start_gazebo_paused": args.start_gazebo_paused,
        "unpause_after_controller_command": args.unpause_gazebo_after_controller_command,
        "report": rel(world_control_path),
        "recorded": world_control_path.exists() and world_control_path.stat().st_size > 0,
        "returncode": read_rc(result_dir / "gazebo_world_control_unpause.rc"),
        "status": world_control_data.get("status") if isinstance(world_control_data, dict) else None,
        "action": world_control_data.get("action") if isinstance(world_control_data, dict) else None,
        "service": world_control_data.get("service") if isinstance(world_control_data, dict) else None,
        "error": world_control_error,
        "claim_boundary": "world-control evidence only; this does not prove hover, closed_loop, planner_ready, or controller performance",
    }

    tf_edges: list[tuple[str, str]] = []
    for name in ["tf", "tf_static"]:
        for parent, child in sample_results.get(name, {}).get("tf_edges", []):
            tf_edges.append((parent, child))

    rate_results: dict[str, Any] = {}
    rate_topics = [
        ("imu", str(topics.get("imu", ""))),
        ("lidar_points", str(topics.get("lidar_points", ""))),
    ]
    if args.run_local_map:
        rate_topics.append(("local_occupancy_voxels", str(topics.get("local_occupancy_voxels", ""))))
    if fastlio_planner_input_gate_required and rate_gate_required:
        rate_topics.extend(
            [
                ("fastlio_lidar", str(topics.get("fastlio_lidar", ""))),
                ("fastlio_imu", str(topics.get("fastlio_imu", ""))),
                ("spark_fastlio_livox", str(topics.get("spark_fastlio_livox", ""))),
                ("planner_global_points", str(topics.get("planner_global_points", ""))),
                ("mosim_planner_global_points", str(topics.get("mosim_planner_global_points", ""))),
                ("planner_odom", str(topics.get("planner_odom", ""))),
                ("mosim_planner_odom", str(topics.get("mosim_planner_odom", ""))),
            ]
        )
    if spark_fastlio_gate_required:
        rate_topics.extend(
            [
                ("spark_fastlio_registered_cloud", str(topics.get("spark_fastlio_registered_cloud", ""))),
                ("spark_fastlio_odometry", str(topics.get("spark_fastlio_odometry", ""))),
                ("spark_fastlio_path", str(topics.get("spark_fastlio_path", ""))),
            ]
        )
    for name, topic in rate_topics:
        key = topic_key(topic)
        stdout_path = result_dir / f"topic_{key}_hz.txt"
        stderr_path = result_dir / f"topic_{key}_hz.stderr.txt"
        rc_path = result_dir / f"topic_{key}_hz.rc"
        rc = read_rc(rc_path)
        text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
        matches = re.findall(r"average rate:\s*([0-9.]+)", text)
        average_rate = float(matches[-1]) if matches else None
        try:
            target_rate = float(target_rates.get(name, 0))
        except (TypeError, ValueError):
            target_rate = 0.0
        minimum_rate = target_rate * rate_gate_min_fraction if target_rate > 0 else None
        rate_recorded = bool(matches)
        header_rate, header_rate_error = read_header_rate(result_dir, topic)
        header_stamp_rate = {}
        receive_wall_rate = {}
        if isinstance(header_rate, dict):
            header_stamp_rate = (
                header_rate.get("header_stamp_rate", {})
                if isinstance(header_rate.get("header_stamp_rate"), dict)
                else {}
            )
            receive_wall_rate = (
                header_rate.get("receive_wall_rate", {})
                if isinstance(header_rate.get("receive_wall_rate"), dict)
                else {}
            )
        rate_results[name] = {
            "topic": topic,
            "rate_stdout": rel(stdout_path),
            "rate_stderr": rel(stderr_path),
            "rate_returncode": rc,
            "average_rate_hz": average_rate,
            "receive_wall_average_rate_hz": average_rate,
            "target_rate_hz": target_rate if target_rate > 0 else None,
            "minimum_rate_hz": minimum_rate,
            "rate_recorded": rate_recorded,
            "header_rate_json": rel(result_dir / f"topic_{key}_header_rate.json"),
            "header_rate_error": header_rate_error,
            "header_stamp_average_rate_hz": header_stamp_rate.get("average_rate_hz"),
            "header_stamp_sample_count": header_stamp_rate.get("sample_count"),
            "header_stamp_duration_s": header_stamp_rate.get("duration_s"),
            "header_stamp_negative_delta_count": header_stamp_rate.get("negative_delta_count"),
            "receive_wall_header_recorder_rate_hz": receive_wall_rate.get("average_rate_hz"),
            "rate_returncode_note": (
                "timeout_returncode_accepted_when_average_rate_is_present"
                if rc == 124 and rate_recorded
                else ""
            ),
            "rate_meets_threshold": (
                average_rate is not None
                and minimum_rate is not None
                and average_rate >= minimum_rate
            ),
        }

    blockers: list[str] = []
    warnings: list[str] = []
    if not args.run_gazebo:
        blockers.append("gazebo_runtime_not_requested")
    elif not args.gazebo_alive:
        blockers.append("gazebo_process_not_alive")

    if args.unpause_gazebo_after_controller_command:
        if not world_control_report["recorded"]:
            blockers.append("gazebo_world_control_unpause_missing")
        elif world_control_report.get("returncode") != 0:
            blockers.append("gazebo_world_control_unpause_failed")
        elif world_control_report.get("status") != "unpaused":
            blockers.append(f"gazebo_world_control_status_not_unpaused:{world_control_report.get('status')}")

    if not args.run_ros2_bridge and not gazebo_truth_pose_only_gate_required:
        blockers.append("ros2_bridge_not_requested")
    elif args.run_ros2_bridge and not args.bridge_alive:
        blockers.append("ros2_bridge_process_not_alive")

    if args.run_local_map and not args.local_map_alive:
        blockers.append("local_map_adapter_process_not_alive")
    if args.run_fastlio_planner_input_adapter and not args.fastlio_planner_input_alive:
        blockers.append("fastlio_planner_input_adapter_process_not_alive")
    if fastlio_planner_input_gate_required and not args.fastlio_imu_passthrough_alive:
        blockers.append("fastlio_imu_passthrough_process_not_alive")
    if args.run_spark_fastlio and not args.spark_fastlio_alive:
        blockers.append("spark_fastlio_process_not_alive")

    if not args.run_topic_check and topic_samples_required:
        blockers.append("topic_sample_check_not_requested")
    elif args.run_topic_check:
        for name, item in sample_results.items():
            if item["required"] and not item.get("observed"):
                if observed_by_sample_or_rate(str(item["topic"])):
                    item["observed_by_sample_or_rate"] = True
                    continue
                blockers.append(f"missing_observed_topic:{name}:{item['topic']}")
            if item["required"] and not item["sample_recorded"]:
                rate_item = rate_results.get(name, {})
                if name in {"imu", "fastlio_imu", "sunray_fastlio_imu"} and rate_item.get("rate_meets_threshold"):
                    warnings.append(
                        "sensor_topic_sample_missing_but_rate_gate_passed:"
                        f"{name}:{item['topic']}:{rate_item.get('average_rate_hz')}"
                    )
                    item["sample_recorded_by_rate_gate"] = True
                    continue
                blockers.append(f"missing_topic_sample:{name}:{item['topic']}")
        if (
            topic_list_path.exists()
            and topic_list_path.stat().st_size == 0
            and any(observed_by_sample_or_rate(str(item.get("topic"))) for item in sample_results.values())
        ):
            warnings.append("topic_list_snapshot_empty_but_samples_or_rates_recorded")

    if not args.run_rate_check and rate_gate_required:
        blockers.append("topic_rate_check_not_requested")
    elif args.run_rate_check and rate_gate_required:
        for name, item in rate_results.items():
            if not item["rate_recorded"]:
                blockers.append(f"missing_topic_rate:{name}:{item['topic']}")
            elif not item["rate_meets_threshold"]:
                header_rate = item.get("header_stamp_average_rate_hz")
                minimum_rate = item.get("minimum_rate_hz")
                if (
                    isinstance(header_rate, (int, float))
                    and isinstance(minimum_rate, (int, float))
                    and header_rate >= minimum_rate
                    and int(item.get("header_stamp_negative_delta_count") or 0) == 0
                ):
                    warnings.append(
                        "receive_wall_rate_below_threshold_but_header_stamp_rate_passed:"
                        f"{name}:{item['topic']}:"
                        f"wall={item['average_rate_hz']}<{minimum_rate}:"
                        f"header={header_rate}"
                    )
                    continue
                blockers.append(
                    "rate_below_threshold:"
                    f"{name}:{item['topic']}:"
                    f"{item['average_rate_hz']}<{item['minimum_rate_hz']}"
                )

    if not args.run_tf_check and tf_gate_required:
        blockers.append("tf_check_not_requested")

    if controller_output_node_gate_required:
        if not args.run_controller_output_node:
            blockers.append("controller_output_node_not_requested")
        if not args.run_controller_output_fixture:
            blockers.append("controller_output_fixture_not_requested")
        if not controller_output.get("observed"):
            blockers.append(f"missing_observed_topic:controller_output:{controller_output_topic}")
        if not controller_output.get("sample_recorded"):
            blockers.append(f"missing_topic_sample:controller_output:{controller_output_topic}")
        if controller_output.get("fixture_returncode") != 0:
            blockers.append("controller_output_fixture_publish_failed")
        if controller_output.get("node_returncode") != 0:
            blockers.append("controller_output_adapter_node_failed")
        if controller_output.get("node_status") != "published":
            blockers.append("controller_output_adapter_node_did_not_publish")
        if not controller_output.get("node_velocity"):
            blockers.append("missing_controller_output_adapter_node_velocity")
        if controller_output.get("sample_recorded") and controller_output.get("node_input_command"):
            if not lists_close(
                [float(item) for item in controller_output.get("command", [])],
                [float(item) for item in controller_output.get("node_input_command", [])],
            ):
                blockers.append("controller_output_topic_command_mismatch")

    fastlio_adapter_report_evidence_ok = False
    fastlio_imu_report_evidence_ok = False
    if fastlio_planner_input_gate_required:
        if not args.run_fastlio_planner_input_adapter:
            blockers.append("fastlio_planner_input_adapter_not_requested")
        if not fastlio_report.get("adapter_report_recorded"):
            blockers.append("fastlio_planner_input_adapter_report_missing")
        status = str(fastlio_report.get("adapter_status") or "")
        if status in {"blocked"}:
            blockers.append("fastlio_planner_input_adapter_blocked")
        imu_passthrough_status = str(fastlio_imu_passthrough_report.get("adapter_status") or "")
        if not fastlio_imu_passthrough_report.get("adapter_report_recorded"):
            blockers.append("fastlio_imu_passthrough_report_missing")
        if imu_passthrough_status in {"blocked"}:
            blockers.append("fastlio_imu_passthrough_blocked")
        counts = fastlio_report.get("adapter_counts") if isinstance(fastlio_report.get("adapter_counts"), dict) else {}
        required_counters = [
            "lidar_received",
            "fastlio_lidar_published",
            "spark_livox_custom_published",
            "sunray_lidar_published",
        ]
        if gate_profile != "spark_fastlio_localization":
            required_counters.extend(
                [
                    "planner_odom_published",
                    "mosim_planner_odom_published",
                ]
            )
        if gate_profile in {"fastlio_planner_input", "planner_handoff_without_setpoint_publication"}:
            required_counters.extend(
                [
                    "planner_global_points_published",
                    "mosim_planner_global_points_published",
                ]
            )
        for counter in required_counters:
            try:
                count = int(counts.get(counter, 0))
            except (TypeError, ValueError):
                count = 0
            if count <= 0:
                blockers.append(f"fastlio_planner_input_adapter_counter_zero:{counter}")
        imu_passthrough_counts = (
            fastlio_imu_passthrough_report.get("adapter_counts")
            if isinstance(fastlio_imu_passthrough_report.get("adapter_counts"), dict)
            else {}
        )
        for counter in ["imu_received", "fastlio_imu_published", "sunray_imu_published"]:
            try:
                count = int(imu_passthrough_counts.get(counter, 0))
            except (TypeError, ValueError):
                count = 0
            if count <= 0:
                blockers.append(f"fastlio_imu_passthrough_counter_zero:{counter}")
        if int(imu_passthrough_counts.get("frame_mismatch_count", 0) or 0) > 0:
            blockers.append("fastlio_imu_passthrough_frame_mismatch")
        if int(counts.get("frame_mismatch_count", 0) or 0) > 0:
            blockers.append("fastlio_planner_input_adapter_frame_mismatch")
        if gate_profile != "spark_fastlio_localization" and int(counts.get("tf_lookup_failures", 0) or 0) > 0:
            blockers.append("fastlio_planner_input_adapter_tf_lookup_failure")
        fastlio_adapter_report_evidence_ok = (
            fastlio_report.get("adapter_report_recorded")
            and status == "active"
            and all(
                int(counts.get(counter, 0) or 0) > 0
                for counter in required_counters
            )
            and int(counts.get("frame_mismatch_count", 0) or 0) == 0
            and (gate_profile == "spark_fastlio_localization" or int(counts.get("tf_lookup_failures", 0) or 0) == 0)
        )
        fastlio_imu_report_evidence_ok = (
            fastlio_imu_passthrough_report.get("adapter_report_recorded")
            and imu_passthrough_status == "active"
            and all(
                int(imu_passthrough_counts.get(counter, 0) or 0) > 0
                for counter in ["imu_received", "fastlio_imu_published", "sunray_imu_published"]
            )
            and int(imu_passthrough_counts.get("frame_mismatch_count", 0) or 0) == 0
        )
        if fastlio_adapter_report_evidence_ok:
            for name in [
                "fastlio_lidar",
                "spark_fastlio_livox",
                "sunray_fastlio_lidar",
                "planner_odom",
                "mosim_planner_odom",
                "planner_global_points",
                "mosim_planner_global_points",
            ]:
                if name in sample_results:
                    sample_results[name]["adapter_report_recorded"] = True
                    sample_results[name]["adapter_report_evidence_ok"] = True
                    sample_results[name]["sample_recorded"] = True
                    sample_results[name]["sample_recorded_by_adapter_report"] = True
                    sample_results[name]["observed"] = True
        if fastlio_imu_report_evidence_ok:
            for name in ["fastlio_imu", "sunray_fastlio_imu"]:
                if name in sample_results:
                    sample_results[name]["adapter_report_recorded"] = True
                    sample_results[name]["adapter_report_evidence_ok"] = True
                    sample_results[name]["sample_recorded"] = True
                    sample_results[name]["sample_recorded_by_adapter_report"] = True
                    sample_results[name]["observed"] = True
        sensor_frame = str(fastlio_adapter.get("sensor_frame", local_map_frame_boundary.get("sensor_frame", "")))
        imu_frame = str(fastlio_adapter.get("imu_frame", ""))
        global_frame = str(fastlio_adapter.get("global_frame", "map"))
        frame_expectations = {
            "lidar_points": sensor_frame,
            "fastlio_lidar": sensor_frame,
            "spark_fastlio_livox": sensor_frame,
            "sunray_fastlio_lidar": sensor_frame,
            "planner_odom": global_frame,
            "mosim_planner_odom": global_frame,
        }
        if gate_profile in {
            "fastlio_planner_input",
            "planner_handoff_without_setpoint_publication",
            "ego_style_planner_output_without_actuation",
        }:
            frame_expectations.update(
                {
                    "planner_global_points": global_frame,
                    "mosim_planner_global_points": global_frame,
                }
            )
        if imu_frame:
            frame_expectations["fastlio_imu"] = imu_frame
            frame_expectations["sunray_fastlio_imu"] = imu_frame
        for name, expected_frame in frame_expectations.items():
            sample = sample_results.get(name, {})
            observed_frame = str(sample.get("frame_id") or "")
            if not observed_frame and sample.get("adapter_report_evidence_ok"):
                sample["frame_id_source"] = "adapter_report"
                sample["frame_id"] = expected_frame
                observed_frame = expected_frame
            if not observed_frame:
                blockers.append(f"missing_topic_frame_id:{name}")
            elif observed_frame != expected_frame:
                blockers.append(f"topic_frame_mismatch:{name}:{observed_frame}!={expected_frame}")
        expected_scan_lines = int(fastlio_adapter.get("spark_livox_scan_lines", 0) or 0)
        spark_sample = sample_results.get("spark_fastlio_livox", {})
        spark_lines = spark_sample.get("sample_line_values") if isinstance(spark_sample, dict) else []
        if expected_scan_lines <= 0:
            blockers.append("spark_livox_scan_lines_not_declared")
        elif isinstance(spark_lines, list) and spark_lines:
            invalid_lines = [
                int(item)
                for item in spark_lines
                if int(item) < 0 or int(item) >= expected_scan_lines
            ]
            if invalid_lines:
                blockers.append(f"spark_livox_line_out_of_range:first_invalid={invalid_lines[0]}:scan_lines={expected_scan_lines}")
        elif spark_sample.get("sample_recorded"):
            if spark_sample.get("sample_recorded_by_adapter_report"):
                warnings.append("spark_livox_line_values_covered_by_adapter_report")
            else:
                blockers.append("spark_livox_line_values_missing")
        spark_offsets = spark_sample.get("sample_offset_time_values") if isinstance(spark_sample, dict) else []
        if isinstance(spark_offsets, list) and len(spark_offsets) >= 2:
            if any(int(right) < int(left) for left, right in zip(spark_offsets, spark_offsets[1:])):
                blockers.append("spark_livox_offset_time_not_monotonic_in_sample")
        elif spark_sample.get("sample_recorded"):
            if spark_sample.get("sample_recorded_by_adapter_report"):
                warnings.append("spark_livox_offset_time_values_covered_by_adapter_report")
            else:
                blockers.append("spark_livox_offset_time_values_missing")
        required_pointcloud_samples = [
            "lidar_points",
            "fastlio_lidar",
            "spark_fastlio_livox",
            "sunray_fastlio_lidar",
        ]
        if gate_profile in {
            "fastlio_planner_input",
            "planner_handoff_without_setpoint_publication",
            "ego_style_planner_output_without_actuation",
        }:
            required_pointcloud_samples.extend(
                [
                    "planner_global_points",
                    "mosim_planner_global_points",
                ]
            )
        for name in required_pointcloud_samples:
            sample = sample_results.get(name, {})
            point_count = sample.get("sample_point_count")
            if (
                name == "spark_fastlio_livox"
                and sample.get("sample_returncode") == 0
                and not isinstance(sample.get("sample_point_num"), int)
            ):
                blockers.append(f"missing_pointcloud_dimensions:{name}")
                continue
            if point_count is None and sample.get("adapter_report_evidence_ok"):
                sample["sample_point_count_source"] = "adapter_report_counter"
                sample["sample_point_count"] = 1
                point_count = 1
            if point_count is None:
                blockers.append(f"missing_pointcloud_dimensions:{name}")
            elif int(point_count) <= 0:
                blockers.append(f"empty_pointcloud_sample:{name}")

        if fastlio_adapter_report_evidence_ok or fastlio_imu_report_evidence_ok:
            adapter_covered_topics = {
                "fastlio_lidar",
                "spark_fastlio_livox",
                "sunray_fastlio_lidar",
                "planner_odom",
                "mosim_planner_odom",
                "planner_global_points",
                "mosim_planner_global_points",
                "fastlio_imu",
                "sunray_fastlio_imu",
            }
            filtered_blockers: list[str] = []
            for blocker in blockers:
                covered = False
                if fastlio_adapter_report_evidence_ok and blocker == "fastlio_planner_input_adapter_process_not_alive":
                    covered = True
                elif fastlio_imu_report_evidence_ok and blocker == "fastlio_imu_passthrough_process_not_alive":
                    covered = True
                elif fastlio_adapter_report_evidence_ok:
                    for name in [
                        "fastlio_lidar",
                        "spark_fastlio_livox",
                        "sunray_fastlio_lidar",
                        "planner_odom",
                        "mosim_planner_odom",
                        "planner_global_points",
                        "mosim_planner_global_points",
                    ]:
                        if (
                            name == "spark_fastlio_livox"
                            and blocker.startswith("missing_pointcloud_dimensions:spark_fastlio_livox")
                            and sample_results.get("spark_fastlio_livox", {}).get("sample_returncode") == 0
                        ):
                            continue
                        if blocker.startswith(
                            (
                                f"missing_observed_topic:{name}:",
                                f"missing_topic_sample:{name}:",
                                f"rate_below_threshold:{name}:",
                                f"missing_topic_frame_id:{name}",
                                f"missing_pointcloud_dimensions:{name}",
                            )
                        ):
                            covered = True
                            break
                if not covered and fastlio_imu_report_evidence_ok:
                    for name in ["fastlio_imu", "sunray_fastlio_imu"]:
                        if blocker.startswith(
                            (
                                f"missing_observed_topic:{name}:",
                                f"missing_topic_sample:{name}:",
                                f"rate_below_threshold:{name}:",
                                f"missing_topic_frame_id:{name}",
                            )
                        ):
                            covered = True
                            break
                if not covered:
                    filtered_blockers.append(blocker)
            if len(filtered_blockers) != len(blockers):
                warnings.append("fastlio_planner_input_evidence_covers_adapter_report_surface")
            blockers = filtered_blockers

    if planner_handoff_gate_required:
        if not planner_handoff_report.get("forbidden_topic_evidence_recorded"):
            blockers.append("planner_handoff_forbidden_topic_evidence_missing")
        if planner_handoff_report.get("forbidden_topic_evidence_error"):
            blockers.append("planner_handoff_forbidden_topic_evidence_invalid_json")
        for topic in planner_handoff_report.get("required_topics", []):
            if topic and topic not in observed_topics and not observed_by_sample_or_rate(topic):
                blockers.append(f"planner_handoff_required_topic_missing:{topic}")
        for topic in planner_handoff_report.get("forbidden_topics", []):
            if topic and topic in observed_topics:
                blockers.append(f"planner_handoff_forbidden_topic_observed:{topic}")
        for topic in planner_handoff_report.get("forbidden_present", []):
            blocker = f"planner_handoff_forbidden_topic_observed:{topic}"
            if blocker not in blockers:
                blockers.append(blocker)

    if ego_style_planner_gate_required:
        if not args.run_ego_style_planner_output:
            blockers.append("ego_style_planner_output_not_requested")
        if not args.run_fastlio_planner_input_adapter:
            blockers.append("ego_style_planner_missing_fastlio_planner_input_adapter")
        if not args.ego_style_planner_alive and not ego_style_planner.get("report_gate_passed"):
            blockers.append("ego_style_planner_process_not_alive_or_completed_without_pass")
        if not args.position_command_converter_alive and not ego_style_planner.get("report_gate_passed"):
            blockers.append("position_command_converter_process_not_alive_or_completed_without_pass")
        if not args.planner_setpoint_adapter_alive:
            blockers.append("planner_setpoint_adapter_process_not_alive")
        if not ego_style_planner.get("report_recorded"):
            blockers.append("ego_style_planner_report_missing")
        if ego_style_planner.get("report_error"):
            blockers.append("ego_style_planner_report_invalid_json")
        if not ego_style_planner.get("report_gate_passed"):
            blockers.append("ego_style_planner_gate_not_passed")
            for item in ego_report_data.get("blockers", []) if isinstance(ego_report_data.get("blockers"), list) else []:
                blockers.append(f"ego_style_planner:{item}")
        for topic in ego_style_planner.get("required_input_topics", []):
            if topic and topic not in observed_topics and not observed_by_sample_or_rate(topic):
                blockers.append(f"ego_style_planner_required_input_topic_missing:{topic}")
        for topic in ego_style_planner.get("required_output_topics", []):
            if topic and topic not in observed_topics and not observed_by_sample_or_rate(topic):
                blockers.append(f"ego_style_planner_required_output_topic_missing:{topic}")
        min_position_cmd = int(ego_style_planner.get("min_position_cmd_samples", 0) or 0)
        min_setpoint = int(ego_style_planner.get("min_setpoint_samples", 0) or 0)
        position_count = int(ego_counts.get("position_cmd", 0) or 0)
        mosim_position_count = int(ego_counts.get("mosim_position_cmd", 0) or 0)
        if min_position_cmd and position_count < min_position_cmd:
            blockers.append("ego_style_planner_position_cmd_count_below_minimum")
        if min_position_cmd and mosim_position_count < min_position_cmd:
            blockers.append("ego_style_planner_mosim_position_cmd_count_below_minimum")
        setpoint_status_sample = sample_results.get("planner_setpoint_adapter_status", {})
        if min_setpoint and not setpoint_status_sample.get("sample_recorded"):
            blockers.append("ego_style_planner_setpoint_adapter_status_sample_missing")
        for topic in ego_style_planner.get("forbidden_topics", []):
            if topic and topic in observed_topics:
                blockers.append(f"ego_style_planner_forbidden_topic_observed:{topic}")
        for topic in ego_style_planner.get("forbidden_present", []):
            blocker = f"ego_style_planner_forbidden_topic_observed:{topic}"
            if blocker not in blockers:
                blockers.append(blocker)

    if command_ack_gate_required:
        if not args.run_command_ack_guard:
            blockers.append("command_ack_guard_not_requested")
        if not command_acknowledgement.get("guard_report_recorded"):
            blockers.append("command_ack_guard_report_missing")
        if command_acknowledgement.get("guard_report_error"):
            blockers.append("command_ack_guard_report_invalid_json")
        positive_path = command_acknowledgement.get("positive_path", {})
        if not isinstance(positive_path, dict) or positive_path.get("node_status") != "published":
            blockers.append("command_ack_positive_node_not_published")
        if not isinstance(positive_path, dict) or positive_path.get("fixture_status") != "published":
            blockers.append("command_ack_fixture_not_published")
        if not isinstance(positive_path, dict) or positive_path.get("node_vehicle_id") != "sunray150":
            blockers.append("command_ack_vehicle_id_mismatch")
        stale_negative_path = command_acknowledgement.get("stale_negative_path", {})
        if not isinstance(stale_negative_path, dict) or not stale_negative_path.get("blocked_as_expected"):
            blockers.append("command_ack_stale_negative_guard_missing")
        for topic in command_acknowledgement.get("forbidden_topics", []):
            if topic and topic in observed_topics:
                blockers.append(f"command_ack_forbidden_topic_observed:{topic}")

    if spark_fastlio_gate_required:
        if not args.run_spark_fastlio:
            blockers.append("spark_fastlio_not_requested")
        if not args.run_fastlio_planner_input_adapter:
            blockers.append("spark_fastlio_missing_input_adapter")
        if not spark_fastlio_report.get("recording_recorded"):
            blockers.append("spark_fastlio_runtime_recording_missing")
        if spark_fastlio_report.get("recorder_returncode") != 0:
            blockers.append("spark_fastlio_runtime_recorder_failed")
        if spark_fastlio_report.get("recording_error"):
            blockers.append("spark_fastlio_runtime_recording_invalid_json")
        spark_counts = (
            spark_fastlio_report.get("recording_counts")
            if isinstance(spark_fastlio_report.get("recording_counts"), dict)
            else {}
        )
        for name in ["odometry", "path", "registered_cloud"]:
            try:
                count = int(spark_counts.get(name, 0))
            except (TypeError, ValueError):
                count = 0
            if count <= 0:
                blockers.append(f"spark_fastlio_runtime_count_zero:{name}")
        map_frame = str(spark_fastlio_runtime.get("map_frame", "map"))
        frame_expectations = {
            "spark_fastlio_registered_cloud": map_frame,
            "spark_fastlio_odometry": map_frame,
            "spark_fastlio_path": map_frame,
        }
        for name, expected_frame in frame_expectations.items():
            sample = sample_results.get(name, {})
            observed_frame = str(sample.get("frame_id") or "")
            if not observed_frame:
                blockers.append(f"missing_topic_frame_id:{name}")
            elif observed_frame != expected_frame:
                blockers.append(f"topic_frame_mismatch:{name}:{observed_frame}!={expected_frame}")
        sample = sample_results.get("spark_fastlio_registered_cloud", {})
        point_count = sample.get("sample_point_count")
        if point_count is None:
            blockers.append("missing_pointcloud_dimensions:spark_fastlio_registered_cloud")
        elif int(point_count) <= 0:
            blockers.append("empty_pointcloud_sample:spark_fastlio_registered_cloud")

    if args.run_fastlio_truth_eval:
        if not args.run_spark_fastlio:
            blockers.append("fastlio_truth_eval_requires_spark_fastlio")
        if not fastlio_truth_error_report.get("truth_recording_recorded"):
            blockers.append("gazebo_truth_pose_recording_missing")
        if fastlio_truth_error_report.get("truth_recording_returncode") != 0:
            blockers.append("gazebo_truth_pose_recorder_failed")
        if fastlio_truth_error_report.get("truth_recording_error"):
            blockers.append("gazebo_truth_pose_recording_invalid_json")
        try:
            truth_count = int(fastlio_truth_error_report.get("truth_recording_count") or 0)
        except (TypeError, ValueError):
            truth_count = 0
        if truth_count <= 0:
            blockers.append("gazebo_truth_pose_count_zero")
        if not fastlio_truth_error_report.get("eval_recorded"):
            blockers.append("fastlio_truth_error_eval_missing")
        if fastlio_truth_error_report.get("eval_returncode") != 0:
            blockers.append("fastlio_truth_error_eval_failed")
        if fastlio_truth_error_report.get("eval_error"):
            blockers.append("fastlio_truth_error_eval_invalid_json")
        if not fastlio_truth_error_report.get("gate_passed"):
            blockers.append("fastlio_truth_error_gate_not_passed")
            for item in fastlio_truth_error_report.get("blockers", []):
                blockers.append(f"fastlio_truth_error:{item}")

    if gazebo_truth_pose_only_gate_required:
        if not args.run_gazebo_truth_pose:
            blockers.append("gazebo_truth_pose_recording_not_requested")
        if not fastlio_truth_error_report.get("truth_recording_recorded"):
            blockers.append("gazebo_truth_pose_recording_missing")
        if fastlio_truth_error_report.get("truth_recording_returncode") != 0:
            blockers.append("gazebo_truth_pose_recorder_failed")
        if fastlio_truth_error_report.get("truth_recording_error"):
            blockers.append("gazebo_truth_pose_recording_invalid_json")
        try:
            truth_count = int(fastlio_truth_error_report.get("truth_recording_count") or 0)
        except (TypeError, ValueError):
            truth_count = 0
        if truth_count <= 0:
            blockers.append("gazebo_truth_pose_count_zero")

    if plant_response_gate_required or hover_bracket_gate_required:
        if not args.run_gazebo_truth_pose:
            blockers.append("gazebo_truth_pose_recording_not_requested")
        if not args.run_plant_response_eval:
            blockers.append("plant_response_eval_not_requested")
        if not plant_response_report.get("truth_recording_recorded"):
            blockers.append("gazebo_truth_pose_recording_missing")
        if plant_response_report.get("truth_recording_returncode") != 0:
            blockers.append("gazebo_truth_pose_recorder_failed")
        if plant_response_report.get("truth_recording_error"):
            blockers.append("gazebo_truth_pose_recording_invalid_json")
        try:
            truth_count = int(plant_response_report.get("truth_recording_count") or 0)
        except (TypeError, ValueError):
            truth_count = 0
        if truth_count <= 0:
            blockers.append("gazebo_truth_pose_count_zero")
        if not plant_response_report.get("eval_recorded"):
            blockers.append("plant_response_eval_missing")
        if plant_response_report.get("eval_returncode") != 0:
            blockers.append("plant_response_eval_failed")
        if plant_response_report.get("eval_error"):
            blockers.append("plant_response_eval_invalid_json")
        if not plant_response_report.get("gate_passed"):
            if plant_response_gate_required:
                blockers.append("plant_response_gate_not_passed")
            else:
                warnings.append("hover_bracket_sample_plant_response_threshold_not_met")
            for item in plant_response_report.get("blockers", []):
                if plant_response_gate_required:
                    blockers.append(f"plant_response:{item}")
                else:
                    warnings.append(f"hover_bracket_sample_plant_response:{item}")

    if actuator_gate_required:
        if not args.run_actuator_command_check:
            blockers.append("actuator_command_check_not_requested")
        if not actuator_command.get("expected_velocity"):
            blockers.append("missing_controller_actuator_command_report")
        if actuator_command.get("controller_publish_returncode") != 0:
            blockers.append("controller_actuator_publish_failed")
        ros_echo = actuator_command.get("ros_echo", {})
        if not ros_echo.get("topic_present"):
            blockers.append(f"missing_observed_topic:actuator_command:{actuator_command_topic}")
        if not ros_echo.get("sample_recorded"):
            blockers.append(f"missing_topic_sample:actuator_command:{actuator_command_topic}")
        if ros_echo.get("sample_recorded") and not actuator_command.get("ros_velocity_matches_expected"):
            blockers.append("actuator_ros_velocity_mismatch")
        gz_echo = actuator_command.get("gz_echo", {})
        if not gz_echo.get("sample_recorded"):
            blockers.append(f"missing_gazebo_topic_sample:actuator_command:{gz_topic}")
        if gz_echo.get("sample_recorded") and not actuator_command.get("gz_velocity_matches_expected"):
            blockers.append("actuator_gazebo_velocity_mismatch")

    if local_map_gate_required and args.run_local_map and args.run_topic_check:
        expected_input_frame = str(local_map_frame_boundary.get("expected_input_frame") or "")
        frame_policy = str(local_map_frame_boundary.get("input_frame_policy") or "")
        map_frame = str(local_map_frame_boundary.get("map_frame") or "")
        if frame_policy == "require_input_frame_equals_map_frame":
            lidar_sample = sample_results.get("lidar_points", {})
            observed_lidar_frame = str(lidar_sample.get("frame_id") or "")
            if not observed_lidar_frame:
                blockers.append("missing_topic_frame_id:lidar_points")
            elif observed_lidar_frame != expected_input_frame:
                blockers.append(
                    "topic_frame_mismatch:"
                    f"lidar_points:{observed_lidar_frame}!={expected_input_frame}"
                )
            for name in ["local_occupancy_voxels", "local_occupancy_grid"]:
                sample = sample_results.get(name, {})
                observed_output_frame = str(sample.get("frame_id") or "")
                if not observed_output_frame:
                    blockers.append(f"missing_topic_frame_id:{name}")
                elif observed_output_frame != str(local_map_frame_boundary.get("map_frame")):
                    blockers.append(
                        "topic_frame_mismatch:"
                        f"{name}:{observed_output_frame}!={local_map_frame_boundary.get('map_frame')}"
                    )
        elif frame_policy == "transform_input_frame_to_map_with_tf":
            lidar_sample = sample_results.get("lidar_points", {})
            observed_lidar_frame = str(lidar_sample.get("frame_id") or "")
            if not observed_lidar_frame:
                blockers.append("missing_topic_frame_id:lidar_points")
            elif expected_input_frame and observed_lidar_frame != expected_input_frame:
                blockers.append(
                    "topic_frame_mismatch:"
                    f"lidar_points:{observed_lidar_frame}!={expected_input_frame}"
                )
            if not args.run_tf_check:
                blockers.append("tf_chain_check_not_requested")
            elif not tf_edges:
                blockers.append("missing_tf_edges")
            elif not tf_chain_exists(tf_edges, observed_lidar_frame or expected_input_frame, map_frame):
                blockers.append(
                    "missing_tf_chain:"
                    f"{observed_lidar_frame or expected_input_frame}->{map_frame}"
                )
            for name in ["local_occupancy_voxels", "local_occupancy_grid"]:
                sample = sample_results.get(name, {})
                observed_output_frame = str(sample.get("frame_id") or "")
                if not observed_output_frame:
                    blockers.append(f"missing_topic_frame_id:{name}")
                elif observed_output_frame != map_frame:
                    blockers.append(
                        "topic_frame_mismatch:"
                        f"{name}:{observed_output_frame}!={map_frame}"
                    )

        for name in ["lidar_points", "local_occupancy_voxels"]:
            sample = sample_results.get(name, {})
            point_count = sample.get("sample_point_count")
            if point_count is None:
                blockers.append(f"missing_pointcloud_dimensions:{name}")
            elif int(point_count) <= 0:
                blockers.append(f"empty_pointcloud_sample:{name}")

    if local_map_gate_required and args.run_local_map and not any(
        item["sample_recorded"] for key, item in sample_results.items() if key == "local_occupancy_voxels"
    ):
        warnings.append("local voxel output was requested but no occupied-voxel sample was recorded")

    gate_passed = not blockers
    return {
        "schema": "mosim.gazebo_ros2_runtime_status.v1",
        "scenario": rel(scenario_path),
        "result_dir": rel(result_dir),
        "status": "runtime_smoke_passed" if gate_passed else "runtime_smoke_blocked",
        "gate_passed": gate_passed,
        "gate_profile": gate_profile,
        "blockers": blockers,
        "warnings": warnings,
        "requested_checks": {
            "run_gazebo": args.run_gazebo,
            "run_ros2_bridge": args.run_ros2_bridge,
            "run_local_map": args.run_local_map,
            "run_topic_check": args.run_topic_check,
            "run_rate_check": args.run_rate_check,
            "run_tf_check": args.run_tf_check,
            "run_fastlio_planner_input_adapter": args.run_fastlio_planner_input_adapter,
            "run_ego_style_planner_output": args.run_ego_style_planner_output,
            "run_spark_fastlio": args.run_spark_fastlio,
            "run_fastlio_truth_eval": args.run_fastlio_truth_eval,
            "run_gazebo_truth_pose": args.run_gazebo_truth_pose,
            "run_plant_response_eval": args.run_plant_response_eval,
            "run_actuator_command_check": args.run_actuator_command_check,
            "run_controller_output_node": args.run_controller_output_node,
            "run_controller_output_fixture": args.run_controller_output_fixture,
            "run_command_ack_guard": args.run_command_ack_guard,
        },
        "topic_gates": {
            "truth_pose": topic_gates.get("truth_pose", "unspecified"),
        },
        "local_map_frame_boundary": local_map_frame_boundary,
        "tf_chain": {
            "edges": [{"parent": parent, "child": child} for parent, child in tf_edges],
            "source_frame": sample_results.get("lidar_points", {}).get("frame_id"),
            "target_frame": local_map_frame_boundary.get("map_frame"),
            "chain_to_map_verified": tf_chain_exists(
                tf_edges,
                str(sample_results.get("lidar_points", {}).get("frame_id") or ""),
                str(local_map_frame_boundary.get("map_frame") or ""),
            ),
        },
        "rate_gate_min_fraction": rate_gate_min_fraction,
        "process_alive": {
            "gazebo": args.gazebo_alive,
            "ros2_bridge": args.bridge_alive,
            "local_map_adapter": args.local_map_alive,
            "fastlio_planner_input_adapter": args.fastlio_planner_input_alive,
            "fastlio_imu_passthrough": args.fastlio_imu_passthrough_alive,
            "ego_style_planner": args.ego_style_planner_alive,
            "position_command_converter": args.position_command_converter_alive,
            "planner_setpoint_adapter": args.planner_setpoint_adapter_alive,
            "spark_fastlio": args.spark_fastlio_alive,
        },
        "topic_list": {
            "path": rel(topic_list_path),
            "snapshot_recorded": topic_list_path.exists() and topic_list_path.stat().st_size > 0,
            "observed_count": len(observed_topics),
            "observed_topics": observed_topics,
            "observed_by_sample_or_rate": sorted(
                {
                    item["topic"]
                    for item in sample_results.values()
                    if isinstance(item, dict)
                    and item.get("topic")
                    and (item.get("sample_recorded") or observed_by_sample_or_rate(str(item.get("topic"))))
                }
            ),
        },
        "topic_samples": sample_results,
        "topic_rates": rate_results,
        "fastlio_planner_input": fastlio_report,
        "fastlio_imu_passthrough": fastlio_imu_passthrough_report,
        "ego_style_planner_output_without_actuation": ego_style_planner,
        "planner_handoff_without_setpoint_publication": planner_handoff_report,
        "command_acknowledgement_without_closed_loop": command_acknowledgement,
        "spark_fastlio_runtime": spark_fastlio_report,
        "fastlio_truth_error": fastlio_truth_error_report,
        "plant_response_pre_acceptance": plant_response_report,
        "gazebo_world_control": world_control_report,
        "controller_output": controller_output,
        "actuator_command": actuator_command,
        "claim_boundary": [
            f"{gate_profile} is only a bounded Gazebo+ROS2 validation gate",
            "controller output node handoff, when requested, proves only ControllerOutput topic to Actuators topic visibility",
            "actuator handoff, when requested, proves only bounded ROS2/Gazebo actuator topic visibility",
            "FAST-LIO/planner input handoff, when requested, proves only topic/frame/rate/input-shape visibility",
            "Spark FAST-LIO runtime, when requested, proves only real output topic samples and recorder counts unless truth-error evaluation is present",
            "FAST-LIO truth-error evaluation, when requested, is only estimator-vs-Gazebo-pose evidence and does not authorize planner or setpoint claims",
            "planner handoff without setpoint publication, when requested, proves only planner input topics and forbidden setpoint/controller/actuator topic absence",
            "EGO-style planner output without actuation, when requested, proves only same-run planner output and setpoint-surface publication without controller or actuator topics",
            "command acknowledgement, when requested, proves only ControllerOutput receipt, metadata guard, adapter conversion, actuator echo, and stale-command rejection",
            "plant response pre-acceptance, when requested, proves only measurable Gazebo truth-pose response to a bounded ControllerOutput command",
            "hover command bracket, when requested, proves only open-loop thrust-scale sampling and may keep low-motion samples as under-thrust evidence",
            "it does not prove MWORKS/Syslab competition metrics",
            "it does not prove hover, trajectory tracking, FAST-LIO localization, planner readiness, closed_loop, controller performance, or multi-UAV readiness",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--run-gazebo", type=bool_arg, default=False)
    parser.add_argument("--run-ros2-bridge", type=bool_arg, default=False)
    parser.add_argument("--run-local-map", type=bool_arg, default=False)
    parser.add_argument("--run-topic-check", type=bool_arg, default=False)
    parser.add_argument("--run-rate-check", type=bool_arg, default=False)
    parser.add_argument("--run-tf-check", type=bool_arg, default=False)
    parser.add_argument("--run-fastlio-planner-input-adapter", type=bool_arg, default=False)
    parser.add_argument("--run-ego-style-planner-output", type=bool_arg, default=False)
    parser.add_argument("--run-spark-fastlio", type=bool_arg, default=False)
    parser.add_argument("--run-fastlio-truth-eval", type=bool_arg, default=False)
    parser.add_argument("--run-gazebo-truth-pose", type=bool_arg, default=False)
    parser.add_argument("--run-plant-response-eval", type=bool_arg, default=False)
    parser.add_argument("--run-actuator-command-check", type=bool_arg, default=False)
    parser.add_argument("--run-controller-output-node", type=bool_arg, default=False)
    parser.add_argument("--run-controller-output-fixture", type=bool_arg, default=False)
    parser.add_argument("--run-command-ack-guard", type=bool_arg, default=False)
    parser.add_argument("--start-gazebo-paused", type=bool_arg, default=False)
    parser.add_argument("--unpause-gazebo-after-controller-command", type=bool_arg, default=False)
    parser.add_argument("--gate-profile", default="sensor_local_map")
    parser.add_argument("--gazebo-alive", type=bool_arg, default=False)
    parser.add_argument("--bridge-alive", type=bool_arg, default=False)
    parser.add_argument("--local-map-alive", type=bool_arg, default=False)
    parser.add_argument("--fastlio-planner-input-alive", type=bool_arg, default=False)
    parser.add_argument("--fastlio-imu-passthrough-alive", type=bool_arg, default=False)
    parser.add_argument("--ego-style-planner-alive", type=bool_arg, default=False)
    parser.add_argument("--position-command-converter-alive", type=bool_arg, default=False)
    parser.add_argument("--planner-setpoint-adapter-alive", type=bool_arg, default=False)
    parser.add_argument("--spark-fastlio-alive", type=bool_arg, default=False)
    args = parser.parse_args()

    try:
        report = build_report(args)
    except Exception as exc:
        report = {
            "schema": "mosim.gazebo_ros2_runtime_status.v1",
            "status": "runtime_status_error",
            "gate_passed": False,
            "blockers": [f"{exc.__class__.__name__}: {exc}"],
        }

    output = repo_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
