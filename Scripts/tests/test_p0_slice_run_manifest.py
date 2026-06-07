#!/usr/bin/env python3
"""Regression checks for the P0 slice RUN_MANIFEST builder."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_p0_slice_run_manifest.py"


def test_p0_slice_manifest_builder_keeps_smoke_boundary() -> None:
    run_id = f"test_p0_slice_{uuid4().hex}"
    output_dir = ROOT / "Results" / "tmp" / run_id
    completed = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--run-id",
            run_id,
            "--output-dir",
            str(output_dir),
            "--validate",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    manifest_path = output_dir / "RUN_MANIFEST.json"
    report_path = output_dir / "RUN_MANIFEST.validation.json"
    assert manifest_path.exists()
    assert report_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert manifest["quality_status"] == "smoke_only"
    assert "closed_loop" not in manifest["claim_scope"]
    assert "planner" not in manifest["claim_scope"]
    assert manifest["planner"]["setpoint_trace_source"] == "RUNTIME_20HZ_ADAPTER"
    assert manifest["planner"]["setpoint_adapter_status"] == "pass"
    assert manifest["planner"]["global_truth_used_as_input"] is False
    ue = manifest["ue"]
    assert ue["command_echo_log"].endswith("ue_command_echo_smoke.jsonl")
    assert ue["command_input_log"].endswith("ue_command_input_smoke.jsonl")
    assert ue["command_adapter_smoke_json"].endswith("ue_command_adapter_smoke.json")
    assert ue["command_echo_source"] == "offline_adapter_smoke"
    assert ue["command_sender_source"].endswith("QuadrotorMworksUdpCommandSenderComponent.cpp")
    assert ue["command_sender_header"].endswith("QuadrotorMworksUdpCommandSenderComponent.h")
    assert ue["command_sender_contract"].endswith("ue_command_sender_source_contract.json")
    assert ue["command_sender_source_status"] == "source_level_static_check_pass"
    assert ue["command_sender_loopback_smoke_json"].endswith("ue_command_sender_loopback_smoke.json")
    assert ue["command_sender_loopback_received"].endswith("ue_command_sender_loopback_received.jsonl")
    assert ue["command_sender_loopback_source"] == "udp_loopback_smoke"
    assert ue["not_runtime_ue_console"] is True
    assert ue["no_pose_overwrite_status"] == "pass"
    b0_replay = manifest["ros2"]["position_command_b0_contract_replay"]
    assert b0_replay["status"] == "pass"
    assert b0_replay["smoke_only"] is True
    assert b0_replay["not_planner_closure"] is True
    assert b0_replay["source_available"] is True
    assert b0_replay["rates_ok"] is True
    assert b0_replay["timestamp_ok"] is True
    assert b0_replay["frame_ok"] is True
    assert b0_replay["stale_samples"] == 0
    assert b0_replay["setpoint_trace_csv"].endswith("/setpoint_trace.csv")
    assert b0_replay["planner_input_gate_status"]["local_map_runtime_source"] == "unverified_by_this_recorder"
    assert any("does not prove" in item for item in b0_replay["claim_boundary"])
    b1_real_planner = manifest["ros2"]["position_command_b1_real_planner"]
    assert b1_real_planner["status"] == "blocked"
    assert b1_real_planner["b1_executable_now"] is False
    assert "missing_real_position_command_source" in b1_real_planner["blocker_ids"]
    assert "missing_fast_lio_or_equivalent_odom" in b1_real_planner["blocker_ids"]
    assert "/position_cmd" in b1_real_planner["missing_from_live_graph"]
    assert any("B1 requires real runtime odom" in item for item in b1_real_planner["claim_boundary"])
    b1_unblock = manifest["ros2"]["position_command_b1_unblock"]
    assert b1_unblock["status"] == "blocked"
    assert b1_unblock["fast_lio_runtime_restored"] is True
    assert b1_unblock["local_sensed_cloud_candidate_restored"] is True
    assert b1_unblock["planner_position_command_source_restored"] is False
    assert b1_unblock["restored_topics"]["odometry"] == "/Odometry"
    assert b1_unblock["candidate_local_sensed_cloud"]["topic"] == "/cloud_registered"
    assert "not_visible" in b1_unblock["candidate_planner_runtime_package"]
    b1_planner_wrapper = manifest["ros2"]["position_command_b1_planner_wrapper"]
    assert b1_planner_wrapper["status"] == "blocked"
    assert b1_planner_wrapper["wrapper_safe_to_add_now"] is False
    assert b1_planner_wrapper["can_directly_ros2_build_or_run"] is False
    assert b1_planner_wrapper["can_directly_run_ros1_catkin_now"] is False
    assert "EGO" in b1_planner_wrapper["selected_planner_candidate"]
    assert "missing_ros2_planner_port_or_package" in b1_planner_wrapper["missing_to_execute_ids"]
    assert "missing_upstream_bspline_or_real_planner_output" in b1_planner_wrapper["missing_to_execute_ids"]
    assert "Convert FAST-LIO /path directly into PositionCommand" in b1_planner_wrapper["rejected_shortcuts"]
    assert any("Do not convert FAST-LIO /path" in item for item in b1_planner_wrapper["claim_boundary"])
    b1_port_preflight = manifest["ros2"]["position_command_b1_port_preflight"]
    assert b1_port_preflight["status"] == "completed_preflight_blocked_for_runtime"
    assert b1_port_preflight["port_preflight_completed"] is True
    assert b1_port_preflight["runtime_position_cmd_ready"] is False
    assert b1_port_preflight["can_enter_real_position_cmd_recorder"] is False
    assert b1_port_preflight["port_effort"]["classification"] == "medium_to_large_port"
    assert b1_port_preflight["build_log"].endswith("colcon_build_preflight.log")
    assert "catkinConfig.cmake" in b1_port_preflight["first_actionable_error"]
    assert b1_port_preflight["runtime_recorder_gate"]["can_run_now"] is False
    assert any("not a running planner" in item for item in b1_port_preflight["claim_boundary"])
    b1_msg_port_slice = manifest["ros2"]["position_command_b1_msg_port_slice"]
    assert b1_msg_port_slice["status"] == "completed_message_slice"
    assert b1_msg_port_slice["message_strategy"]["external_position_command_surface"] == "reuse_mosim_msgs_PositionCommand"
    assert "ego_planner_msgs/msg/Bspline.msg" in b1_msg_port_slice["message_strategy"]["internal_messages_added"]
    assert b1_msg_port_slice["colcon_build_status"]["ego_planner_msgs"]["status"] == "pass_with_clock_skew_warnings"
    assert b1_msg_port_slice["interface_verification"]["status"] == "pass"
    assert "planner_node_logic_not_ported" in b1_msg_port_slice["remaining_blocker_ids"]
    assert b1_msg_port_slice["can_start_planner_node_porting"]["allowed_next"] is True
    assert b1_msg_port_slice["can_start_runtime_recorder"]["allowed"] is False
    assert any("No planner node logic" in item for item in b1_msg_port_slice["claim_boundary"])
    b1_planner_node = manifest["ros2"]["position_command_b1_planner_node_port_preflight"]
    assert b1_planner_node["status"] == "completed_preflight"
    assert b1_planner_node["quality_status"] == "build_surface_only"
    assert b1_planner_node["node_contract"]["output_message"] == "mosim_msgs/msg/PositionCommand"
    assert b1_planner_node["node_contract"]["publish_enabled_default"] is False
    assert b1_planner_node["node_contract"]["runtime_recorder_allowed"] is False
    assert b1_planner_node["build_status"]["status"] == "passed_after_incremental_retry"
    assert b1_planner_node["build_status"]["installed_executable"].endswith("traj_server_ros2_node")
    assert b1_planner_node["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_planner_node["forbidden_actions_confirmed"]["runtime_recorder_run"] is False
    assert any("No planner runtime" in item for item in b1_planner_node["claim_boundary"])
    b1_upstream = manifest["ros2"]["position_command_b1_upstream_planner_deps"]
    assert b1_upstream["status"] == "blocked_after_classification"
    assert b1_upstream["quality_status"] == "classification_and_build_probe_only"
    assert b1_upstream["preferred_bspline_producer"]["candidate"] == "EGO plan_manage/EGOReplanFSM"
    assert b1_upstream["preferred_bspline_producer"]["output_topic"] == "/planning/bspline"
    assert b1_upstream["first_blocker"]["package"] == "plan_env"
    assert b1_upstream["first_blocker"]["status"] == "ros1_catkin_only"
    assert b1_upstream["can_reach_real_planning_bspline_next"]["status"] is False
    assert "plan_env" in b1_upstream["current_isolated_workspace_state"]["catkin_only_packages_remaining"]
    assert b1_upstream["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_upstream["forbidden_actions_confirmed"]["runtime_recorder_run"] is False
    assert any("EGOReplanFSM" in item for item in b1_upstream["claim_boundary"])
    b1_planenv = manifest["ros2"]["position_command_b1_planenv_gridmap_port"]
    assert b1_planenv["status"] == "completed_preflight"
    assert b1_planenv["quality_status"] == "build_surface_only"
    assert b1_planenv["summary"]["plan_env_ros2_buildable"] is True
    assert b1_planenv["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANENV-GRIDMAP-PORT-20260606-011.json"
    )
    assert b1_planenv["build_status"]["status"] == "passed_after_incremental_install_retry"
    assert any(path.endswith("green_colcon_build_plan_env_incremental_install.log") for path in b1_planenv["build_status"]["post_patch_logs"])
    assert any(path.endswith("install/plan_env/lib/libplan_env.a") for path in b1_planenv["build_status"]["installed_artifacts"])
    assert "plan_env" in b1_planenv["workspace_package_state_after_011"]["ros2_ament_packages"]
    assert "plan_env" not in b1_planenv["workspace_package_state_after_011"]["catkin_only_packages_remaining"]
    assert "path_searching" in b1_planenv["workspace_package_state_after_011"]["catkin_only_packages_remaining"]
    assert "bspline_opt" in b1_planenv["workspace_package_state_after_011"]["catkin_only_packages_remaining"]
    assert b1_planenv["runtime_contract_preserved"]["intended_odom_remap"] == "/grid_map/odom:=/Odometry"
    assert b1_planenv["runtime_contract_preserved"]["intended_cloud_remap"] == "/grid_map/cloud:=/cloud_registered"
    assert b1_planenv["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_planenv["forbidden_actions_confirmed"]["runtime_recorder_run"] is False
    assert "path_searching" in b1_planenv["exact_next_command"]["next_engineering_task"]
    assert any("build/API surface" in item for item in b1_planenv["claim_boundary"])
    b1_path_bspline = manifest["ros2"]["position_command_b1_path_bspline_port"]
    assert b1_path_bspline["status"] == "completed_preflight"
    assert b1_path_bspline["quality_status"] == "build_surface_only"
    assert b1_path_bspline["summary"]["path_searching_ros2_buildable"] is True
    assert b1_path_bspline["summary"]["bspline_opt_ros2_buildable"] is True
    assert b1_path_bspline["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-PATH-BSPLINE-PORT-20260606-012.json"
    )
    assert b1_path_bspline["build_status"]["status"] == "passed_after_incremental_retries"
    assert any(
        path.endswith("green_colcon_build_path_searching_incremental.log")
        for command in b1_path_bspline["build_status"]["commands"]
        for path in command["logs"]
    )
    assert any(
        path.endswith("green_colcon_build_bspline_opt_incremental_2.log")
        for command in b1_path_bspline["build_status"]["commands"]
        for path in command["logs"]
    )
    assert any(path.endswith("install/path_searching/lib/libpath_searching.a") for path in b1_path_bspline["installed_artifacts"])
    assert any(path.endswith("install/bspline_opt/lib/libbspline_opt.a") for path in b1_path_bspline["installed_artifacts"])
    assert "path_searching" in b1_path_bspline["workspace_package_state_after_012"]["ros2_ament_packages"]
    assert "bspline_opt" in b1_path_bspline["workspace_package_state_after_012"]["ros2_ament_packages"]
    assert "path_searching" not in b1_path_bspline["workspace_package_state_after_012"]["catkin_only_packages_remaining"]
    assert "bspline_opt" not in b1_path_bspline["workspace_package_state_after_012"]["catkin_only_packages_remaining"]
    assert "traj_utils" in b1_path_bspline["workspace_package_state_after_012"]["catkin_only_packages_remaining"]
    assert "quadrotor_msgs" in b1_path_bspline["workspace_package_state_after_012"]["catkin_only_packages_remaining"]
    assert b1_path_bspline["workspace_package_state_after_012"]["can_start_real_planning_bspline_runtime"] is False
    assert b1_path_bspline["workspace_package_state_after_012"]["can_enter_real_position_cmd_runtime_recorder"] is False
    assert b1_path_bspline["runtime_contract_preserved"]["intended_odom_remap_from_011"] == "/grid_map/odom:=/Odometry"
    assert b1_path_bspline["runtime_contract_preserved"]["intended_cloud_remap_from_011"] == "/grid_map/cloud:=/cloud_registered"
    assert b1_path_bspline["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_path_bspline["forbidden_actions_confirmed"]["runtime_recorder_run"] is False
    assert "traj_utils" in b1_path_bspline["exact_next_command"]["next_engineering_task"]
    assert any("build/API surfaces" in item for item in b1_path_bspline["claim_boundary"])
    b1_traj_quadmsgs = manifest["ros2"]["position_command_b1_traj_quadmsgs_port"]
    assert b1_traj_quadmsgs["status"] == "completed_preflight"
    assert b1_traj_quadmsgs["quality_status"] == "build_surface_only"
    assert b1_traj_quadmsgs["summary"]["quadrotor_msgs_ros2_buildable"] is True
    assert b1_traj_quadmsgs["summary"]["traj_utils_ros2_buildable"] is True
    assert b1_traj_quadmsgs["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-TRAJ-QUADMSGS-PORT-20260606-013.json"
    )
    assert b1_traj_quadmsgs["build_status"]["status"] == "passed_after_incremental_retries"
    assert any(
        path.endswith("green_colcon_build_quadrotor_msgs_after_cleanup.log")
        for command in b1_traj_quadmsgs["build_status"]["commands"]
        for path in command["green_logs"]
    )
    assert any(
        path.endswith("green_colcon_build_traj_utils_incremental.log")
        for command in b1_traj_quadmsgs["build_status"]["commands"]
        for path in command["green_logs"]
    )
    assert any(path.endswith("install/quadrotor_msgs/share/quadrotor_msgs/msg/PositionCommand.msg") for path in b1_traj_quadmsgs["installed_artifacts"])
    assert any(path.endswith("install/traj_utils/lib/libtraj_utils.a") for path in b1_traj_quadmsgs["installed_artifacts"])
    package_state_013 = b1_traj_quadmsgs["workspace_package_state_after_013"]
    assert "quadrotor_msgs" in package_state_013["ros2_ament_packages"]
    assert "traj_utils" in package_state_013["ros2_ament_packages"]
    assert package_state_013["catkin_only_packages_remaining"] == []
    assert package_state_013["can_start_real_planning_bspline_runtime"] is False
    assert package_state_013["can_enter_real_position_cmd_runtime_recorder"] is False
    assert b1_traj_quadmsgs["runtime_contract_preserved"]["intended_odom_remap_from_011"] == "/grid_map/odom:=/Odometry"
    assert b1_traj_quadmsgs["runtime_contract_preserved"]["intended_cloud_remap_from_011"] == "/grid_map/cloud:=/cloud_registered"
    assert b1_traj_quadmsgs["runtime_contract_preserved"]["external_position_command_rule"].startswith(
        "MoSim external command surface remains"
    )
    assert b1_traj_quadmsgs["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_traj_quadmsgs["forbidden_actions_confirmed"]["runtime_recorder_run"] is False
    assert b1_traj_quadmsgs["forbidden_actions_confirmed"]["planner_runtime_launched"] is False
    assert "Full plan_manage link preflight" in b1_traj_quadmsgs["exact_next_command"]["next_engineering_task"]
    assert any("build/API surfaces" in item for item in b1_traj_quadmsgs["claim_boundary"])
    b1_planmanage = manifest["ros2"]["position_command_b1_planmanage_link_preflight"]
    assert b1_planmanage["status"] == "completed_preflight"
    assert b1_planmanage["quality_status"] == "link_preflight_only"
    assert b1_planmanage["summary"]["full_plan_manage_link_preflight_passed"] is True
    assert b1_planmanage["summary"]["ego_planner_manager_preflight_buildable"] is True
    assert b1_planmanage["summary"]["ego_replan_fsm_preflight_buildable"] is True
    assert b1_planmanage["summary"]["ego_planner_node_preflight_linkable"] is True
    assert b1_planmanage["summary"]["runtime_reachability_claim"] == "not_claimed"
    assert b1_planmanage["summary"]["planning_bspline_runtime_evidence"] == "not_claimed"
    assert b1_planmanage["summary"]["position_cmd_evidence"] == "not_claimed"
    assert b1_planmanage["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANMANAGE-LINK-PREFLIGHT-20260606-014.json"
    )
    assert b1_planmanage["build_status"]["status"] == "passed_with_incremental_install"
    assert any(
        path.endswith("final_cmake_install_ego_planner_full_link_preflight.log")
        for command in b1_planmanage["build_status"]["commands"]
        for path in ([command["log"]] if "log" in command else command.get("logs", []))
    )
    assert any(path.endswith("libego_planner_manager_preflight.a") for path in b1_planmanage["installed_artifacts"])
    assert any(path.endswith("libego_replan_fsm_preflight.a") for path in b1_planmanage["installed_artifacts"])
    assert any(path.endswith("ego_planner_node_preflight") for path in b1_planmanage["installed_artifacts"])
    assert b1_planmanage["runtime_boundary"]["planner_runtime_launched"] is False
    assert b1_planmanage["runtime_boundary"]["runtime_recorder_run"] is False
    assert b1_planmanage["runtime_boundary"]["position_cmd_published"] is False
    assert b1_planmanage["runtime_boundary"]["closed_loop_claim"] is False
    assert b1_planmanage["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_planmanage["forbidden_actions_confirmed"]["planner_runtime_launched"] is False
    assert b1_planmanage["forbidden_actions_confirmed"]["claimed_planner_or_closed_loop_acceptance"] is False
    assert "runtime-disabled" in b1_planmanage["next_allowed_task"]["recommended"]
    assert b1_planmanage["next_allowed_task"]["can_enter_real_position_cmd_runtime_recorder"] is False
    assert any("compile/link preflight" in item for item in b1_planmanage["claim_boundary"])
    b1_launch_audit = manifest["ros2"]["position_command_b1_runtime_disabled_launch_audit"]
    assert b1_launch_audit["status"] == "completed_static_audit"
    assert b1_launch_audit["quality_status"] == "runtime_disabled_static_audit_only"
    assert b1_launch_audit["summary"]["ready_for_later_pmo_approved_runtime_disabled_smoke"] is True
    assert b1_launch_audit["summary"]["ready_for_real_planner_runtime"] is False
    assert b1_launch_audit["summary"]["ready_for_runtime_recorder"] is False
    assert b1_launch_audit["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json"
    )
    assert b1_launch_audit["static_or_dry_run_commands"]["ros2_run_or_launch_executed"] is False
    assert b1_launch_audit["topic_remap_contract"]["command_adapter_surface"]["required_disabled_parameter"] == (
        "publish_enabled:=false"
    )
    assert b1_launch_audit["parameter_audit"]["direct_legacy_xml_reuse_safe"] is False
    assert "runtime-disabled" in b1_launch_audit["next_pmo_approval_gate"]["gate_name"]
    assert b1_launch_audit["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_launch_audit["forbidden_actions_confirmed"]["claimed_planner_or_closed_loop_acceptance"] is False
    b1_launch_config = manifest["ros2"]["position_command_b1_runtime_disabled_launch_config"]
    assert b1_launch_config["status"] == "completed"
    assert b1_launch_config["quality_status"] == "runtime_disabled_static_config_only"
    assert b1_launch_config["summary"]["ready_for_later_pmo_approved_runtime_disabled_smoke"] is True
    assert b1_launch_config["summary"]["ready_for_real_planner_runtime"] is False
    assert b1_launch_config["summary"]["ready_for_runtime_recorder"] is False
    assert b1_launch_config["summary"]["runtime_or_recorder_executed"] is False
    assert b1_launch_config["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json"
    )
    source_artifacts = b1_launch_config["artifact_inventory"]["source_artifacts"]
    assert any(item["path"].endswith("runtime_disabled_preflight.launch.py") for item in source_artifacts)
    assert any(item["path"].endswith("runtime_disabled_preflight.yaml") for item in source_artifacts)
    assert b1_launch_config["static_validation_output"]["ros2_launch_executed"] is False
    assert b1_launch_config["static_validation_output"]["ros2_run_executed"] is False
    encoded_pairs = {
        (item["from"], item["to"])
        for item in b1_launch_config["topic_remap_contract"]["encoded_remaps"]
    }
    assert ("/odom_world", "/Odometry") in encoded_pairs
    assert ("/grid_map/odom", "/Odometry") in encoded_pairs
    assert ("/grid_map/cloud", "/cloud_registered") in encoded_pairs
    assert "/planning/bspline" in b1_launch_config["topic_remap_contract"]["not_claimed_topics"]
    assert "/position_cmd" in b1_launch_config["topic_remap_contract"]["not_claimed_topics"]
    assert b1_launch_config["next_pmo_gate"]["approval_required_before_running"] is True
    assert "runtime-disabled" in b1_launch_config["next_pmo_gate"]["gate_name"]
    assert b1_launch_config["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_launch_config["forbidden_actions_confirmed"]["claimed_planner_or_closed_loop_acceptance"] is False
    b1_disabled_smoke = manifest["ros2"]["position_command_b1_runtime_disabled_smoke"]
    assert b1_disabled_smoke["status"] == "completed"
    assert b1_disabled_smoke["quality_status"] == "runtime_disabled_smoke_passed"
    assert b1_disabled_smoke["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-SMOKE-20260606-017.json"
    )
    smoke = b1_disabled_smoke["runtime_disabled_smoke"]
    assert smoke["launch_exit_code"] == 0
    assert smoke["guard_message_seen"] is True
    assert smoke["clean_process_finish_seen"] is True
    assert smoke["planner_runtime_started"] is False
    assert smoke["position_command_published"] is False
    assert smoke["planning_bspline_published_as_runtime_evidence"] is False
    assert smoke["runtime_recorder_run"] is False
    assert smoke["closed_loop_claim"] is False
    assert smoke["forbidden_topics_seen"]["/position_cmd"] is False
    assert smoke["forbidden_topics_seen"]["/planning/bspline"] is False
    assert b1_disabled_smoke["summary"]["ready_for_real_planner_runtime"] is False
    assert b1_disabled_smoke["summary"]["ready_for_runtime_recorder"] is False
    assert any(item.endswith("smoke_stdout_stderr.log") for item in b1_disabled_smoke["evidence_artifacts"])
    assert b1_disabled_smoke["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_disabled_smoke["forbidden_actions_confirmed"]["claimed_planner_or_closed_loop_acceptance"] is False
    b1_input_gate = manifest["ros2"]["position_command_b1_real_planner_input_gate"]
    assert b1_input_gate["status"] == "blocked"
    assert b1_input_gate["quality_status"] == "real_planner_input_gate_blocked"
    assert b1_input_gate["real_odometry_present_now"] is False
    assert b1_input_gate["real_cloud_registered_present_now"] is False
    assert b1_input_gate["runtime_disabled_false_may_be_safely_attempted_later"] is False
    assert b1_input_gate["gate_decision"]["can_attempt_runtime_disabled_false_in_later_separate_task"] is False
    assert b1_input_gate["topic_availability_rate_type_probe"]["required_inputs"]["/Odometry"]["present"] is False
    assert b1_input_gate["topic_availability_rate_type_probe"]["required_inputs"]["/cloud_registered"]["present"] is False
    assert b1_input_gate["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_input_gate["forbidden_actions_confirmed"]["claimed_planner_or_closed_loop_acceptance"] is False
    assert any("current real planner inputs are absent" in item for item in b1_input_gate["claim_boundary"])
    b1_odom_cloud = manifest["ros2"]["position_command_b1_odom_cloud_restore"]
    assert b1_odom_cloud["status"] == "completed_input_gate"
    assert b1_odom_cloud["quality_status"] == "odom_cloud_restore_ready_for_later_startup_gate"
    assert b1_odom_cloud["return_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019.json"
    )
    assert b1_odom_cloud["summary_json"].endswith("odom_cloud_restore_summary.json")
    assert b1_odom_cloud["ready_for_later_separate_runtime_disabled_false_startup_probe"] is True
    assert b1_odom_cloud["planner_ready"] is False
    assert b1_odom_cloud["closed_loop_ready"] is False
    assert b1_odom_cloud["position_command_recorder_allowed"] is False
    assert b1_odom_cloud["planner_startup_executed"] is False
    assert b1_odom_cloud["required_topics"]["/Odometry"]["present_in_runtime_recording"] is True
    assert b1_odom_cloud["required_topics"]["/Odometry"]["expected_type"] == "nav_msgs/msg/Odometry"
    assert b1_odom_cloud["required_topics"]["/Odometry"]["recorded_count"] == 93
    assert b1_odom_cloud["required_topics"]["/cloud_registered"]["present_in_runtime_recording"] is True
    assert b1_odom_cloud["required_topics"]["/cloud_registered"]["expected_type"] == "sensor_msgs/msg/PointCloud2"
    assert b1_odom_cloud["required_topics"]["/cloud_registered"]["recorded_count"] == 92
    assert b1_odom_cloud["truth_evaluation"]["status"] == "pass"
    assert b1_odom_cloud["truth_evaluation"]["metrics"]["position_rmse_m"] == 0.305369
    assert b1_odom_cloud["input_source_probe"]["acceptance"]["livox_nonzero"] is True
    assert b1_odom_cloud["input_source_probe"]["acceptance"]["imu_nonzero"] is True
    assert b1_odom_cloud["forbidden_actions_confirmed"]["ran_position_command_recorder"] is False
    assert b1_odom_cloud["forbidden_actions_confirmed"]["ran_runtime_disabled_false_planner_startup"] is False
    assert b1_odom_cloud["forbidden_actions_confirmed"]["claimed_planner_ready"] is False
    assert b1_odom_cloud["forbidden_actions_confirmed"]["claimed_closed_loop_ready"] is False
    assert any("No runtime_disabled=false planner startup" in item for item in b1_odom_cloud["claim_boundary"])
    b1_planner_startup = manifest["ros2"]["position_command_b1_planner_startup_probe"]
    assert b1_planner_startup["status"] == "blocked_after_bounded_startup_probe"
    assert b1_planner_startup["quality_status"] == "planner_startup_surface_not_accepted"
    assert b1_planner_startup["blocker_packet"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-STARTUP-PROBE-20260606-020.json"
    )
    assert b1_planner_startup["summary"]["fresh_restore_ready"] is True
    assert b1_planner_startup["summary"]["planner_surface_initialized"] is True
    assert b1_planner_startup["summary"]["planner_consumed_inputs"] is False
    assert b1_planner_startup["planner_ready"] is False
    assert b1_planner_startup["closed_loop_ready"] is False
    assert b1_planner_startup["position_command_recorder_allowed"] is False
    assert b1_planner_startup["fresh_restore_evidence"]["counts"]["/Odometry"] == 149
    assert b1_planner_startup["fresh_restore_evidence"]["counts"]["/cloud_registered"] == 148
    assert b1_planner_startup["planner_startup_probe"]["topic_info_evidence"]["/Odometry"]["publisher_count"] == 0
    assert (
        b1_planner_startup["planner_startup_probe"]["topic_info_evidence"]["/cloud_registered"]["publisher_count"]
        == 0
    )
    assert (
        b1_planner_startup["planner_startup_probe"]["topic_info_evidence"]["/planning/bspline"][
            "accepted_runtime_evidence"
        ]
        is False
    )
    assert b1_planner_startup["forbidden_actions_confirmed"]["ran_position_command_recorder"] is False
    assert b1_planner_startup["forbidden_actions_confirmed"]["published_position_cmd"] is False
    assert b1_planner_startup["forbidden_actions_confirmed"]["claimed_planner_ready"] is False
    assert b1_planner_startup["forbidden_actions_confirmed"]["claimed_closed_loop_ready"] is False
    assert any("Input consumption was not accepted" in item for item in b1_planner_startup["claim_boundary"])
    mworks = manifest["mworks"]
    assert mworks["setpoint_trace_consumption_status"] == "blocked"
    assert mworks["consumed_setpoint_trace"] == ""
    assert mworks["trace_consumption_evidence"] == ""
    assert mworks["trace_consumption_blocker"].endswith("RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json")
    trace_lookup = mworks["trace_lookup_diagnostic"]
    assert trace_lookup["status"] == "completed"
    assert trace_lookup["quality_status"] == "diagnostic_pass"
    assert trace_lookup["model_name"] == "QuadrotorExperiments.TraceLookupStandaloneSmoke"
    assert trace_lookup["nonzero_reference_outputs"] is True
    assert trace_lookup["tolerance_pass"] is True
    assert trace_lookup["probe_json"].endswith("trace_lookup_standalone_probe.json")
    assert trace_lookup["raw_reference_series_csv"].endswith("trace_lookup_standalone_raw.csv")
    assert any("Standalone trace lookup proves" in item for item in trace_lookup["claim_boundary"])
    factory_reconnect = mworks["factory_trace_reconnect"]
    assert factory_reconnect["status"] == "blocked"
    assert factory_reconnect["blocker_kind"] == "factory_wrapper_result_binding_failed"
    assert factory_reconnect["check_model_status"] == "pass"
    assert factory_reconnect["simulate_status"] == "blocked"
    assert factory_reconnect["get_var_times_count"] == 0
    assert factory_reconnect["nonzero_alias_refs"] is False
    assert factory_reconnect["probe_json"].endswith("factory_trace_reconnect_probe.json")
    assert "Factory-lite" in factory_reconnect["next_minimal_probe"]
    assert any("No MWORKS Factory trace consumption evidence" in item for item in factory_reconnect["claim_boundary"])
    factory_lite = mworks["factory_lite_trace_probe"]
    assert factory_lite["status"] == "completed"
    assert factory_lite["quality_status"] == "factory_lite_trace_probe_pass"
    assert factory_lite["model_name"] == "QuadrotorExperiments.FactoryLiteTraceSmoke"
    assert factory_lite["check_model_status"] == "pass"
    assert factory_lite["simulate_status"] == "pass"
    assert factory_lite["get_var_times_count"] == 41
    assert factory_lite["nonzero_alias_refs"] is True
    assert factory_lite["probe_json"].endswith("factory_lite_trace_probe.json")
    assert factory_lite["raw_alias_series_csv"].endswith("factory_lite_trace_raw.csv")
    assert "closed_loop" in factory_lite["not_claimed"]
    assert any("Factory-lite trace result-binding probe only" in item for item in factory_lite["claim_boundary"])
    incremental = mworks["incremental_trace_isolation"]
    assert incremental["status"] == "completed"
    assert incremental["quality_status"] == "isolation_boundary_found"
    assert incremental["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json"
    )
    assert len(incremental["incremental_probes"]) == 4
    assert incremental["incremental_probes"][0]["verdict"] == "pass"
    assert incremental["first_failure_boundary"]["probe_id"] == "iso04_controller_plant_wiring"
    assert incremental["first_failure_boundary"]["failure_kind"] == "simulate_failed_after_check_pass"
    assert "motor-command wiring" in incremental["first_failure_boundary"]["component_group"]
    assert incremental["probe_json"].endswith("incremental_trace_isolation_probe.json")
    assert incremental["probe_summary_csv"].endswith("incremental_trace_isolation_summary.csv")
    assert any("No closed_loop" in item for item in incremental["claim_boundary"])
    actuator = mworks["actuator_wiring_isolation"]
    assert actuator["status"] == "completed"
    assert actuator["quality_status"] == "topology_boundary_refined"
    assert actuator["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json"
    )
    assert actuator["known_passing_topology_reference"]["model"].endswith("Example1LinearMPCSysblockClosedLoop.mo")
    assert len(actuator["derivative_probes"]) == 3
    probe_by_id = {probe["probe_id"]: probe for probe in actuator["derivative_probes"]}
    assert probe_by_id["iso05_clean_hover_sum"]["simulate_model"] == "pass"
    assert probe_by_id["iso05_clean_hover_sum"]["error_6140_present"] is False
    assert probe_by_id["iso06_clean_sensor_feedback_controller"]["simulate_model"] == "failed"
    assert probe_by_id["iso06_clean_sensor_feedback_controller"]["get_var_times_count_after_failed_simulate"] == 0
    assert probe_by_id["iso07_clean_open_feedback_controller"]["simulate_model"] == "pass"
    assert "duplicate actuator input sources" in actuator["refined_boundary"]["cause"]
    assert "sensor-feedback" in actuator["refined_boundary"]["remaining_boundary"]
    assert actuator["probe_json"].endswith("actuator_wiring_isolation_probe.json")
    assert actuator["probe_summary_csv"].endswith("actuator_wiring_isolation_summary.csv")
    assert any("No closed_loop" in item for item in actuator["claim_boundary"])
    sensor_feedback = mworks["sensor_feedback_isolation"]
    assert sensor_feedback["status"] == "completed"
    assert sensor_feedback["quality_status"] == "first_sensor_feedback_boundary_found"
    assert sensor_feedback["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json"
    )
    assert len(sensor_feedback["feedback_probes"]) == 2
    feedback_by_id = {probe["probe_id"]: probe for probe in sensor_feedback["feedback_probes"]}
    assert feedback_by_id["iso08_position_feedback"]["simulate_model"] == "pass"
    assert feedback_by_id["iso08_position_feedback"]["error_6140_present"] is False
    assert feedback_by_id["iso09_position_attitude_feedback"]["simulate_model"] == "failed"
    assert feedback_by_id["iso09_position_attitude_feedback"]["get_var_times_count_after_failed_simulate"] == 0
    assert feedback_by_id["iso09_position_attitude_feedback"]["error_6140_present"] is False
    assert sensor_feedback["first_failure_boundary"]["probe_id"] == "iso09_position_attitude_feedback"
    assert sensor_feedback["first_failure_boundary"]["failure_kind"] == "simulate_failed_empty_result_context"
    assert "roll/pitch" in sensor_feedback["first_failure_boundary"]["feedback_group"]
    assert sensor_feedback["probe_json"].endswith("sensor_feedback_isolation_probe.json")
    assert sensor_feedback["probe_summary_csv"].endswith("sensor_feedback_isolation_summary.csv")
    assert any("No closed_loop" in item for item in sensor_feedback["claim_boundary"])
    attitude_feedback = mworks["attitude_feedback_isolation"]
    assert attitude_feedback["status"] == "completed"
    assert attitude_feedback["quality_status"] == "attitude_feedback_sub_boundary_found"
    assert attitude_feedback["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json"
    )
    assert len(attitude_feedback["attitude_feedback_probes"]) == 4
    attitude_by_id = {probe["probe_id"]: probe for probe in attitude_feedback["attitude_feedback_probes"]}
    for probe_id in [
        "iso10_roll_only_direct",
        "iso11_pitch_only_direct",
        "iso12_roll_only_negated",
        "iso13_pitch_only_negated",
    ]:
        assert attitude_by_id[probe_id]["check_model"] == "pass"
        assert attitude_by_id[probe_id]["simulate_model"] == "failed"
        assert attitude_by_id[probe_id]["get_var_times_count"] == 0
        assert attitude_by_id[probe_id]["error_6140_present"] is False
    assert attitude_feedback["first_failure_boundary"]["probe_id"] == "iso10_roll_only_direct"
    assert attitude_feedback["first_failure_boundary"]["error_6140_present"] is False
    assert "sign flip" in attitude_feedback["first_failure_boundary"]["sign_or_frame_result"]
    assert attitude_feedback["probe_json"].endswith("attitude_feedback_isolation_probe.json")
    assert attitude_feedback["probe_summary_csv"].endswith("attitude_feedback_isolation_summary.csv")
    assert attitude_feedback["mcp_log"].endswith("attitude_feedback_mcp_log.json")
    assert any("No closed_loop" in item for item in attitude_feedback["claim_boundary"])
    attitude_intermediary = mworks["attitude_intermediary_classification"]
    assert attitude_intermediary["status"] == "completed"
    assert attitude_intermediary["quality_status"] == "absolute_angles_dependency_coupling_classified"
    assert attitude_intermediary["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json"
    )
    intermediary_by_id = {probe["probe_id"]: probe for probe in attitude_intermediary["intermediary_probes"]}
    for probe_id in ["iso14_constant_attitude_input", "iso15_table_attitude_input"]:
        assert intermediary_by_id[probe_id]["check_model"] == "pass"
        assert intermediary_by_id[probe_id]["simulate_model"] == "pass"
        assert intermediary_by_id[probe_id]["get_var_times_count"] == 1001
        assert intermediary_by_id[probe_id]["nonzero_alias_refs"] is True
    assert intermediary_by_id["iso16_realexpression_angle_bridge"]["check_model"] == "pass"
    assert intermediary_by_id["iso16_realexpression_angle_bridge"]["simulate_model"] == "failed"
    assert intermediary_by_id["iso16_realexpression_angle_bridge"]["get_var_times_count"] == 0
    assert intermediary_by_id["iso16_realexpression_angle_bridge"]["error_6140_present"] is False
    classification = attitude_intermediary["classification"]
    assert classification["constant_attitude_inputs_pass"] is True
    assert classification["time_table_attitude_inputs_pass"] is True
    assert classification["realexpression_anglemea_bridge_passes"] is False
    assert "AbsoluteAngles" in classification["first_current_blocker"]
    assert attitude_intermediary["probe_json"].endswith("attitude_intermediary_probe.json")
    assert attitude_intermediary["probe_summary_csv"].endswith("attitude_intermediary_summary.csv")
    assert attitude_intermediary["mcp_log"].endswith("attitude_intermediary_mcp_log.json")
    assert any("No closed_loop" in item for item in attitude_intermediary["claim_boundary"])
    attitude_decoupling = mworks["attitude_decoupling_probe"]
    assert attitude_decoupling["status"] == "completed"
    assert attitude_decoupling["quality_status"] == "attitude_decoupling_probe_passed"
    assert attitude_decoupling["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json"
    )
    decoupling_by_id = {probe["probe_id"]: probe for probe in attitude_decoupling["decoupling_probes"]}
    for probe_id in ["iso17_sample_hold_angle", "iso18_project_attitude_estimator"]:
        assert decoupling_by_id[probe_id]["check_model"] == "pass"
        assert decoupling_by_id[probe_id]["simulate_model"] == "pass"
        assert decoupling_by_id[probe_id]["get_var_times_count"] == 1001
        assert decoupling_by_id[probe_id]["nonzero_alias_refs"] is True
        assert decoupling_by_id[probe_id]["error_6140_present"] is False
    decoupling_classification = attitude_decoupling["classification"]
    assert decoupling_classification["prior_010_direct_realexpression_anglemea_failed"] is True
    assert decoupling_classification["sampled_held_decoupling_passes"] is True
    assert decoupling_classification["project_owned_attitude_extraction_passes"] is True
    assert decoupling_classification["absolute_angles_dependency_can_be_decoupled"] is True
    assert "Iso18" in decoupling_classification["recommended_pattern"]
    assert attitude_decoupling["probe_json"].endswith("attitude_decoupling_probe.json")
    assert attitude_decoupling["probe_summary_csv"].endswith("attitude_decoupling_summary.csv")
    assert attitude_decoupling["mcp_log"].endswith("attitude_decoupling_mcp_log.json")
    assert any("No closed_loop" in item for item in attitude_decoupling["claim_boundary"])
    pitch_decoupling = mworks["pitch_decoupling_probe"]
    assert pitch_decoupling["status"] == "completed"
    assert pitch_decoupling["quality_status"] == "pitch_decoupling_probe_passed"
    assert pitch_decoupling["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-PITCH-DECOUPLING-20260606-012.json"
    )
    pitch_by_id = {probe["probe_id"]: probe for probe in pitch_decoupling["pitch_decoupling_probes"]}
    iso19 = pitch_by_id["iso19_roll_pitch_estimator"]
    assert iso19["check_model"] == "pass"
    assert iso19["simulate_model"] == "pass"
    assert iso19["get_var_times_count"] == 1001
    assert iso19["nonzero_alias_refs"] is True
    assert iso19["roll_pitch_alias_available"] is True
    assert iso19["error_6140_present"] is False
    pitch_classification = pitch_decoupling["classification"]
    assert pitch_classification["prior_011_iso18_roll_extraction_passed"] is True
    assert pitch_classification["pitch_anglemea2_extraction_added"] is True
    assert pitch_classification["roll_pitch_project_owned_extraction_passes"] is True
    assert pitch_classification["yaw_feedback_added"] is False
    assert pitch_classification["rate_feedback_added"] is False
    assert pitch_classification["full_sensor_bus_added"] is False
    assert pitch_classification["full_factory_wrapper_retried"] is False
    assert pitch_decoupling["probe_json"].endswith("pitch_decoupling_probe.json")
    assert pitch_decoupling["probe_summary_csv"].endswith("pitch_decoupling_summary.csv")
    assert pitch_decoupling["mcp_log"].endswith("pitch_decoupling_mcp_log.json")
    assert any("No closed_loop" in item for item in pitch_decoupling["claim_boundary"])
    yaw_rate = mworks["yaw_rate_decoupling_probe"]
    assert yaw_rate["status"] == "completed"
    assert yaw_rate["quality_status"] == "yaw_attitude_decoupling_probe_passed"
    assert yaw_rate["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json"
    )
    yaw_by_id = {probe["probe_id"]: probe for probe in yaw_rate["yaw_rate_probes"]}
    iso20 = yaw_by_id["iso20_roll_pitch_yaw_estimator"]
    assert iso20["check_model"] == "pass"
    assert iso20["simulate_model"] == "pass"
    assert iso20["get_var_times_count"] == 1001
    assert iso20["nonzero_alias_refs"] is True
    assert iso20["yaw_alias_available"] is True
    assert iso20["rate_fallback_used"] is False
    assert iso20["error_6140_present"] is False
    yaw_classification = yaw_rate["classification"]
    assert yaw_classification["prior_012_roll_pitch_extraction_passed"] is True
    assert yaw_classification["yaw_anglemea3_extraction_added"] is True
    assert yaw_classification["yaw_attitude_extraction_passes"] is True
    assert yaw_classification["rate_feedback_added"] is False
    assert yaw_classification["rate_fallback_needed"] is False
    assert yaw_classification["full_sensor_bus_added"] is False
    assert yaw_classification["full_factory_wrapper_retried"] is False
    assert yaw_rate["probe_json"].endswith("yaw_rate_decoupling_probe.json")
    assert yaw_rate["probe_summary_csv"].endswith("yaw_rate_decoupling_summary.csv")
    assert yaw_rate["mcp_log"].endswith("yaw_rate_decoupling_mcp_log.json")
    assert yaw_rate["unknowns_risks_next_validation"].endswith("yaw_rate_decoupling_unknowns_risks.md")
    assert any("No rate feedback claim" in item for item in yaw_rate["claim_boundary"])
    assert any("No closed_loop" in item for item in yaw_rate["claim_boundary"])
    rate_feedback = mworks["rate_feedback_isolation_probe"]
    assert rate_feedback["status"] == "completed"
    assert rate_feedback["quality_status"] == "rate_feedback_isolation_probe_passed"
    assert rate_feedback["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json"
    )
    rate_by_id = {probe["probe_id"]: probe for probe in rate_feedback["rate_feedback_probes"]}
    iso21 = rate_by_id["iso21_controller_rate_alias"]
    assert iso21["check_model"] == "pass"
    assert iso21["simulate_model"] == "pass"
    assert iso21["get_var_times_count"] == 1001
    assert iso21["nonzero_alias_refs"] is True
    assert iso21["rate_alias_available"] is True
    assert iso21["error_6140_present"] is False
    rate_classification = rate_feedback["classification"]
    assert rate_classification["prior_013_yaw_extraction_passed"] is True
    assert rate_classification["narrow_rate_alias_group_added"] is True
    assert rate_classification["current_controller_external_rate_inports"] is False
    assert rate_classification["external_rate_sensor_wired"] is False
    assert rate_classification["rate_alias_group_passes"] is True
    assert rate_classification["full_sensor_bus_added"] is False
    assert rate_classification["full_factory_wrapper_retried"] is False
    assert rate_feedback["probe_json"].endswith("rate_feedback_isolation_probe.json")
    assert rate_feedback["probe_summary_csv"].endswith("rate_feedback_isolation_summary.csv")
    assert rate_feedback["mcp_log"].endswith("rate_feedback_isolation_mcp_log.json")
    assert rate_feedback["unknowns_risks_next_validation"].endswith("rate_feedback_isolation_unknowns_risks.md")
    assert any("No external rate-feedback controller claim" in item for item in rate_feedback["claim_boundary"])
    assert any("No closed_loop" in item for item in rate_feedback["claim_boundary"])
    sensor_bus = mworks["sensor_bus_reconnect_probe"]
    assert sensor_bus["status"] == "blocked"
    assert sensor_bus["quality_status"] == "blocked_first_new_boundary_found"
    assert sensor_bus["blocker_kind"] == "simulate_failed_result_context_empty"
    assert sensor_bus["blocker_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json"
    )
    sensor_by_id = {probe["probe_id"]: probe for probe in sensor_bus["probe_results"]}
    iso22 = sensor_by_id["iso22_sensor_display_reconnect"]
    assert iso22["check_model"] == "pass"
    assert iso22["simulate_model"] == "failed"
    assert iso22["simulate_data"] is False
    assert iso22["get_var_times_count"] == 0
    assert iso22["alias_values_available"] is False
    assert iso22["error_6140_present"] is True
    assert "navigationDisplay.actual_position" in iso22["first_new_boundary"]
    assert sensor_bus["probe_json"].endswith("sensor_bus_reconnect_probe.json")
    assert sensor_bus["probe_summary_csv"].endswith("sensor_bus_reconnect_summary.csv")
    assert sensor_bus["mcp_log"].endswith("sensor_bus_reconnect_mcp_log.json")
    assert any("Sensor/display reconnect boundary probe only" in item for item in sensor_bus["claim_boundary"])
    position_bridge = mworks["position_bridge_probe"]
    assert position_bridge["status"] == "completed"
    assert position_bridge["quality_status"] == "display_position_bridge_probe_passed"
    assert position_bridge["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json"
    )
    position_by_id = {probe["probe_id"]: probe for probe in position_bridge["probe_results"]}
    iso23 = position_by_id["iso23_position_sample_hold_bridge"]
    assert iso23["check_model"] == "pass"
    assert iso23["simulate_model"] == "pass"
    assert iso23["simulate_data"] is True
    assert iso23["get_var_times_count"] == 1001
    assert iso23["alias_values_available"] is True
    assert iso23["error_6140_present"] is False
    assert iso23["result_context_restored"] is True
    assert position_bridge["probe_json"].endswith("position_bridge_probe.json")
    assert position_bridge["alias_samples_csv"].endswith("position_bridge_alias_samples.csv")
    assert position_bridge["mcp_log"].endswith("position_bridge_mcp_log.json")
    assert "Display-position bridge" in position_bridge["claim_boundary"]
    next_sensor_display = mworks["next_sensor_display_group_probe"]
    assert next_sensor_display["status"] == "blocked"
    assert next_sensor_display["quality_status"] == "blocked_scope_exhausted"
    assert next_sensor_display["blocker_kind"] == "no_remaining_allowed_sensor_display_group"
    assert next_sensor_display["source"] == "file_topology_inspection"
    assert next_sensor_display["blocker_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017.json"
    )
    assert next_sensor_display["topology_comparison"].endswith("topology_comparison_summary.json")
    assert next_sensor_display["prior_passing_mworks_mcp_evidence"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json"
    )
    assert next_sensor_display["exactly_one_group_added"] is False
    assert any(
        "not sensor/display-only" in item["status"]
        for item in next_sensor_display["topology_findings"]
        if isinstance(item, dict)
    )
    assert "topology/scope evidence only" in next_sensor_display["claim_boundary"]
    assert any("no actuator/control reconnect was added" in item for item in next_sensor_display["forbidden_actions_confirmed"])
    assert any("controller/control-feedback reconnect group" in item for item in next_sensor_display["next_validation"])
    first_control_feedback = mworks["first_control_feedback_group_probe"]
    assert first_control_feedback["status"] == "blocked"
    assert first_control_feedback["quality_status"] == "blocked_first_control_feedback_boundary_found"
    assert first_control_feedback["blocker_kind"] == "simulate_failed_result_context_empty"
    assert first_control_feedback["source"] == "MWORKS_MCP"
    assert first_control_feedback["blocker_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018.json"
    )
    assert first_control_feedback["selected_group"].startswith("direct sensors1_1.AngleMea")
    assert first_control_feedback["exactly_one_group_added"] is True
    assert first_control_feedback["iso23_display_bridge_preserved"] is True
    assert first_control_feedback["check_model"]["status"] == "pass"
    assert first_control_feedback["simulate_model"]["status"] == "failed"
    assert first_control_feedback["simulate_model"]["data"] is False
    assert first_control_feedback["get_var_times"]["count"] == 0
    assert first_control_feedback["aliases"]["available"] is False
    assert first_control_feedback["error_6140_present"] is False
    assert "direct AngleMea attitude feedback" in first_control_feedback["first_new_boundary"]
    assert first_control_feedback["probe_json"].endswith("first_control_feedback_probe.json")
    assert first_control_feedback["summary_csv"].endswith("first_control_feedback_summary.csv")
    assert first_control_feedback["mcp_log"].endswith("first_control_feedback_mcp_log.json")
    assert any("first-order extraction" in item for item in first_control_feedback["next_validation"])
    assert "One incremental controller/control-feedback group blocker only" in first_control_feedback["claim_boundary"]
    attitude_bridge = mworks["attitude_feedback_bridge_probe"]
    assert attitude_bridge["status"] == "completed"
    assert attitude_bridge["quality_status"] == "attitude_feedback_bridge_probe_passed"
    assert attitude_bridge["source"] == "MWORKS_MCP"
    assert attitude_bridge["return_packet"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json"
    )
    assert "sampled/held" in attitude_bridge["selected_bridge_variant"]
    assert attitude_bridge["probe_json"].endswith("attitude_feedback_probe.json")
    assert attitude_bridge["alias_samples_csv"].endswith("attitude_feedback_alias_samples.csv")
    assert attitude_bridge["mcp_log"].endswith("attitude_feedback_mcp_log.json")
    bridge_by_id = {probe["probe_id"]: probe for probe in attitude_bridge["probe_results"]}
    iso25 = bridge_by_id["iso25_sample_hold_attitude_feedback_bridge"]
    assert iso25["exactly_one_bridge_group_added"] is True
    assert iso25["iso23_display_bridge_preserved"] is True
    assert iso25["check_model"] == "pass"
    assert iso25["simulate_model"] == "pass"
    assert iso25["simulate_data"] is True
    assert iso25["get_var_times_count"] == 1001
    assert iso25["alias_values_available"] is True
    assert iso25["error_6140_present"] is False
    assert iso25["result_context_restored"] is True
    assert "not closed_loop" in attitude_bridge["claim_boundary"]
    assert any("not counted as consumed" in item for item in mworks["trace_consumption_claim_boundary"])
    assert any("B0 PositionCommand contract replay is smoke-only" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 unblock restored current FAST-LIO" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 planner-wrapper task 006" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 port preflight task 007" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 message-port task 008" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 planner-node preflight task 009" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 upstream planner-deps task 010" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 plan_env/GridMap port task 011" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 path_searching/bspline_opt port task 012" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 traj_utils/quadrotor_msgs port task 013" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 plan_manage link preflight task 014" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 runtime-disabled launch audit task 015" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 runtime-disabled launch/config task 016" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 runtime-disabled smoke task 017" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 real planner input gate task 018" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 odom/cloud restore task 019" in item for item in manifest["gate_results"]["warnings"])
    assert any("B1 planner startup probe task 020" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS trace wrapper check_model passed" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS standalone trace lookup diagnostic 003 passed" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS Factory trace reconnect task 004" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS Factory-lite trace probe task 005 passed" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS incremental trace isolation task 006" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS actuator wiring isolation task 007" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS sensor feedback isolation task 008" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS attitude feedback isolation task 009" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS attitude intermediary task 010" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS attitude decoupling task 011" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS pitch decoupling task 012" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS yaw decoupling task 013" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS rate-feedback isolation task 014" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS sensor-bus reconnect task 015" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS position bridge task 016" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS next sensor/display group task 017" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS first controller/control-feedback group task 018" in item for item in manifest["gate_results"]["warnings"])
    assert any("MWORKS attitude-feedback bridge task 019" in item for item in manifest["gate_results"]["warnings"])
    assert any("UE command sender UDP loopback smoke passes" in item for item in manifest["gate_results"]["warnings"])
    assert any("source-level UDP command sender" in item for item in manifest["gate_results"]["warnings"])
    assert manifest["blockers"]
    assert any("No real local 3D map planner output" in item for item in manifest["blockers"])
    assert any("Gate B restore can regenerate FAST-LIO" in item for item in manifest["blockers"])
    assert any("task 019 restored /Odometry" in item for item in manifest["blockers"])
    assert any("runtime_disabled=false planner startup remains blocked" in item for item in manifest["blockers"])
    assert any("planner startup probe 020 is blocked" in item for item in manifest["blockers"])
    assert any("MWORKS trace consumption is blocked" in item for item in manifest["blockers"])
    assert any("direct sensors1_1.PosMea" in item for item in manifest["blockers"])
    assert any("sensor/display scope is exhausted after Iso23" in item for item in manifest["blockers"])
    assert any("sampled/held attitude-feedback bridge" in item for item in manifest["blockers"])


def main() -> int:
    test_p0_slice_manifest_builder_keeps_smoke_boundary()
    print("[OK] P0 slice RUN_MANIFEST builder regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
