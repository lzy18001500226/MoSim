#!/usr/bin/env python3
"""Regression test for the P0 closed-loop gap matrix."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "summarize_p0_closed_loop_gap_matrix.py"
OUTPUT = ROOT / "Results" / "tmp" / "test_p0_closed_loop_gap_matrix.json"


def test_p0_gap_matrix_keeps_closed_loop_blocked() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--output-json",
            str(OUTPUT),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    matrix = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert matrix["schema"] == "mosim.p0_closed_loop_gap_matrix.v1"
    assert matrix["quality_status"] == "smoke_only"
    assert matrix["closed_loop_ready"] is False
    assert matrix["planner_ready"] is False
    assert "planner" not in matrix["claim_scope"]
    assert "closed_loop" not in matrix["claim_scope"]
    assert matrix["anti_regression_checks"]["claim_scope_excludes_planner"] is True
    assert matrix["anti_regression_checks"]["claim_scope_excludes_closed_loop"] is True
    assert matrix["anti_regression_checks"]["planner_global_truth_used_as_input"] is False
    assert matrix["gates"]["mworks_same_trace_consumption"]["blocking"] is True
    assert matrix["gates"]["mworks_same_trace_consumption"]["status"] == "blocked"
    assert matrix["gates"]["mworks_attitude_feedback_decoupling"]["blocking"] is True
    assert matrix["gates"]["mworks_attitude_feedback_decoupling"]["status"] == "rate_feedback_isolation_probe_passed"
    assert matrix["gates"]["mworks_attitude_feedback_decoupling"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json"
    )
    assert matrix["gates"]["mworks_sensor_bus_reconnect"]["blocking"] is True
    assert matrix["gates"]["mworks_sensor_bus_reconnect"]["status"] == "blocked_first_new_boundary_found"
    assert matrix["gates"]["mworks_sensor_bus_reconnect"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json"
    )
    assert matrix["gates"]["mworks_sensor_bus_reconnect"]["details"]["blocker_kind"] == (
        "simulate_failed_result_context_empty"
    )
    assert matrix["gates"]["mworks_sensor_bus_reconnect"]["details"]["error_6140_present"] is True
    assert matrix["gates"]["mworks_position_bridge"]["blocking"] is True
    assert matrix["gates"]["mworks_position_bridge"]["status"] == "display_position_bridge_probe_passed"
    assert matrix["gates"]["mworks_position_bridge"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json"
    )
    assert matrix["gates"]["mworks_position_bridge"]["details"]["bridge_passed"] is True
    assert matrix["gates"]["mworks_position_bridge"]["details"]["error_6140_present"] is False
    assert matrix["gates"]["mworks_position_bridge"]["details"]["factory_trace_consumption_claimed"] is False
    assert matrix["gates"]["mworks_next_sensor_display_group"]["blocking"] is True
    assert matrix["gates"]["mworks_next_sensor_display_group"]["status"] == "blocked_scope_exhausted"
    assert matrix["gates"]["mworks_next_sensor_display_group"]["source"] == "file_topology_inspection"
    assert matrix["gates"]["mworks_next_sensor_display_group"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017.json"
    )
    assert matrix["gates"]["mworks_next_sensor_display_group"]["details"]["blocker_kind"] == (
        "no_remaining_allowed_sensor_display_group"
    )
    assert matrix["gates"]["mworks_next_sensor_display_group"]["details"]["exactly_one_group_added"] is False
    assert matrix["gates"]["mworks_next_sensor_display_group"]["details"]["not_mworks_simulation_evidence"] is True
    assert any(
        item["target"] == "planningReference.position_command -> navigationDisplay.reference_position"
        and item["status"] == "already inherited in Iso23 from FactoryLiteTraceSmoke"
        for item in matrix["gates"]["mworks_next_sensor_display_group"]["details"]["topology_findings"]
    )
    assert "controller/control-feedback reconnect group" in matrix["gates"]["mworks_next_sensor_display_group"]["next"]
    assert matrix["gates"]["mworks_first_control_feedback_group"]["blocking"] is True
    assert matrix["gates"]["mworks_first_control_feedback_group"]["status"] == (
        "blocked_first_control_feedback_boundary_found"
    )
    assert matrix["gates"]["mworks_first_control_feedback_group"]["source"] == "MWORKS_MCP"
    assert matrix["gates"]["mworks_first_control_feedback_group"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018.json"
    )
    mworks_018_details = matrix["gates"]["mworks_first_control_feedback_group"]["details"]
    assert mworks_018_details["blocker_kind"] == "simulate_failed_result_context_empty"
    assert mworks_018_details["selected_group"].startswith("direct sensors1_1.AngleMea")
    assert mworks_018_details["exactly_one_group_added"] is True
    assert mworks_018_details["iso23_display_bridge_preserved"] is True
    assert mworks_018_details["check_model_status"] == "pass"
    assert mworks_018_details["simulate_model_status"] == "failed"
    assert mworks_018_details["simulate_model_data"] is False
    assert mworks_018_details["get_var_times_count"] == 0
    assert mworks_018_details["aliases_available"] is False
    assert mworks_018_details["error_6140_present"] is False
    assert "direct AngleMea attitude feedback" in mworks_018_details["first_new_boundary"]
    assert "attitude-feedback bridge task" in matrix["gates"]["mworks_first_control_feedback_group"]["next"]
    assert matrix["gates"]["mworks_attitude_feedback_bridge"]["blocking"] is True
    assert matrix["gates"]["mworks_attitude_feedback_bridge"]["status"] == "attitude_feedback_bridge_probe_passed"
    assert matrix["gates"]["mworks_attitude_feedback_bridge"]["source"] == "MWORKS_MCP"
    assert matrix["gates"]["mworks_attitude_feedback_bridge"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json"
    )
    mworks_019_details = matrix["gates"]["mworks_attitude_feedback_bridge"]["details"]
    assert "sampled/held" in mworks_019_details["selected_bridge_variant"]
    assert mworks_019_details["bridge_passed"] is True
    assert mworks_019_details["iso23_display_bridge_preserved"] is True
    assert mworks_019_details["get_var_times_count"] == 1001
    assert mworks_019_details["error_6140_present"] is False
    assert mworks_019_details["factory_trace_consumption_claimed"] is False
    assert "Iso25" in matrix["gates"]["mworks_attitude_feedback_bridge"]["next"]
    assert matrix["gates"]["mworks_actuator_to_wrench_bridge"]["blocking"] is True
    assert matrix["gates"]["mworks_actuator_to_wrench_bridge"]["status"] == "completed_minimal_bridge_smoke"
    assert matrix["gates"]["mworks_actuator_to_wrench_bridge"]["quality_status"] == (
        "minimal_actuator_to_wrench_bridge_smoke_passed"
    )
    assert matrix["gates"]["mworks_actuator_to_wrench_bridge"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json"
    )
    mworks_bridge_details = matrix["gates"]["mworks_actuator_to_wrench_bridge"]["details"]
    assert mworks_bridge_details["model_name"].endswith(
        ".FactoryTraceIso28ActuatorToWrenchBridgeSmoke"
    )
    assert mworks_bridge_details["check_model_status"] == "pass"
    assert mworks_bridge_details["simulate_status"] == "pass"
    assert mworks_bridge_details["get_var_times_count"] == 251
    assert mworks_bridge_details["bridge_command_error_abs_sum_end"] == 0.0
    assert mworks_bridge_details["force_application_error_at_samples"] == [0.0, 0.0, 0.0]
    assert mworks_bridge_details["torque_application_error_at_samples"] == [0.0, 0.0, 0.0]
    assert mworks_bridge_details["minimal_actuator_to_wrench_bridge_smoke"] is True
    assert mworks_bridge_details["factory_trace_consumption"] is False
    assert mworks_bridge_details["full_actuator_or_plant_closure"] is False
    assert matrix["gates"]["mworks_external_frame_boundary"]["blocking"] is True
    assert matrix["gates"]["mworks_external_frame_boundary"]["status"] == "completed_external_frame_boundary_smoke"
    assert matrix["gates"]["mworks_external_frame_boundary"]["quality_status"] == (
        "minimal_external_frame_boundary_smoke_passed"
    )
    assert matrix["gates"]["mworks_external_frame_boundary"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json"
    )
    mworks_external_details = matrix["gates"]["mworks_external_frame_boundary"]["details"]
    assert mworks_external_details["model_name"].endswith(
        ".FactoryTraceIso29ExternalFrameWrenchBoundarySmoke"
    )
    assert mworks_external_details["check_model_status"] == "pass"
    assert mworks_external_details["simulate_status"] == "pass"
    assert mworks_external_details["get_var_times_count"] == 251
    assert mworks_external_details["external_body_component"] == "external_test_body"
    assert mworks_external_details["external_force_torque_component"] == "external_force_and_torque"
    assert mworks_external_details["bridge_command_error_abs_sum_end"] == 0.0
    assert mworks_external_details["external_boundary_gate_error_end"] == 0.0
    assert mworks_external_details["external_force_application_error_at_samples"] == [0.0, 0.0, 0.0]
    assert mworks_external_details["external_torque_application_error_at_samples"] == [0.0, 0.0, 0.0]
    assert mworks_external_details["external_force_matches_adapter_error_at_samples"] == [0.0, 0.0, 0.0]
    assert mworks_external_details["external_torque_matches_adapter_error_at_samples"] == [0.0, 0.0, 0.0]
    assert mworks_external_details["minimal_external_frame_boundary_smoke"] is True
    assert mworks_external_details["factory_trace_consumption"] is False
    assert mworks_external_details["quadchassis_or_full_plant_closure"] is False
    assert matrix["gates"]["ros2_real_planner_runtime"]["blocking"] is True
    assert matrix["gates"]["ros2_real_planner_input_gate"]["blocking"] is True
    assert matrix["gates"]["ros2_real_planner_input_gate"]["status"] == "real_planner_input_gate_blocked"
    assert matrix["gates"]["ros2_real_planner_input_gate"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018.json"
    )
    assert matrix["gates"]["ros2_real_planner_input_gate"]["details"]["real_odometry_present_now"] is False
    assert matrix["gates"]["ros2_real_planner_input_gate"]["details"]["real_cloud_registered_present_now"] is False
    assert (
        matrix["gates"]["ros2_real_planner_input_gate"]["details"][
            "runtime_disabled_false_may_be_safely_attempted_later"
        ]
        is False
    )
    assert matrix["gates"]["ros2_odom_cloud_restore"]["blocking"] is True
    assert matrix["gates"]["ros2_odom_cloud_restore"]["status"] == "odom_cloud_restore_ready_for_later_startup_gate"
    assert matrix["gates"]["ros2_odom_cloud_restore"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019.json"
    )
    odom_cloud_details = matrix["gates"]["ros2_odom_cloud_restore"]["details"]
    assert odom_cloud_details["ready_for_later_separate_runtime_disabled_false_startup_probe"] is True
    assert odom_cloud_details["planner_ready"] is False
    assert odom_cloud_details["closed_loop_ready"] is False
    assert odom_cloud_details["position_command_recorder_allowed"] is False
    assert odom_cloud_details["planner_startup_executed"] is False
    assert odom_cloud_details["odometry_count"] == 93
    assert odom_cloud_details["cloud_registered_count"] == 92
    assert odom_cloud_details["truth_status"] == "pass"
    assert odom_cloud_details["truth_position_rmse_m"] == 0.305369
    assert matrix["gates"]["ros2_long_source_startup_discipline"]["blocking"] is True
    assert matrix["gates"]["ros2_long_source_startup_discipline"]["status"] == (
        "completed_long_source_no_goal_precondition_passed"
    )
    assert matrix["gates"]["ros2_long_source_startup_discipline"]["quality_status"] == (
        "no_goal_long_source_startup_discipline_precondition_passed"
    )
    assert matrix["gates"]["ros2_long_source_startup_discipline"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-LONG-SOURCE-STARTUP-DISCIPLINE-RERUN-20260606-031.json"
    )
    long_source_details = matrix["gates"]["ros2_long_source_startup_discipline"]["details"]
    assert long_source_details["source_frame_count"] == 120
    assert long_source_details["source_coordinate_frame"] == "body_lidar_m_z_up"
    assert long_source_details["startup_order"] == "FAST-LIO -> first Livox frame -> IMU"
    assert long_source_details["livox_count"] == 39
    assert long_source_details["imu_count"] == 781
    assert long_source_details["odometry_count"] == 19
    assert long_source_details["cloud_registered_count"] == 19
    assert long_source_details["loopback_total"] == 0
    assert long_source_details["no_effective_points"] == 0
    assert long_source_details["position_cmd_forbidden_topic_present"] is False
    assert long_source_details["planning_bspline_forbidden_topic_present"] is False
    assert long_source_details["cleanup"] == "no_matching_processes"
    assert matrix["gates"]["ros2_planner_startup_probe"]["blocking"] is True
    assert matrix["gates"]["ros2_planner_startup_probe"]["status"] == "planner_startup_surface_not_accepted"
    assert matrix["gates"]["ros2_planner_startup_probe"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-STARTUP-PROBE-20260606-020.json"
    )
    startup_details = matrix["gates"]["ros2_planner_startup_probe"]["details"]
    assert startup_details["fresh_restore_ready"] is True
    assert startup_details["planner_surface_initialized"] is True
    assert startup_details["planner_consumed_inputs"] is False
    assert startup_details["planner_ready"] is False
    assert startup_details["closed_loop_ready"] is False
    assert startup_details["position_command_recorder_allowed"] is False
    assert startup_details["odometry_count"] == 149
    assert startup_details["cloud_registered_count"] == 148
    assert startup_details["odometry_publisher_count_during_planner"] == 0
    assert startup_details["cloud_publisher_count_during_planner"] == 0
    assert startup_details["planning_bspline_accepted_runtime_evidence"] is False
    assert "stable-source input-consumption retry" in matrix["gates"]["ros2_planner_startup_probe"]["next"]
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["blocking"] is True
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["status"] == "completed"
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["quality_status"] == "runtime_disabled_smoke_passed"
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["launch_config_quality_status"] == "runtime_disabled_static_config_only"
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["runtime_disabled_guard_smoke_passed"] is True
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["ready_for_later_runtime_disabled_smoke"] is True
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["ready_for_real_planner_runtime"] is False
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["ready_for_runtime_recorder"] is False
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["guard_message_seen"] is True
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["runtime_disabled_launch_exit_code"] == 0
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["details"]["ros2_run_or_launch_executed"] is True
    assert matrix["gates"]["ros2_planner_dependency_surfaces"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-SMOKE-20260606-017.json"
    )
    assert matrix["gates"]["ros2_no_goal_odom_tf_rviz_preflight_dispatch"]["blocking"] is True
    assert matrix["gates"]["ros2_no_goal_odom_tf_rviz_preflight_dispatch"]["status"] == "blocked_before_goal"
    assert matrix["gates"]["ros2_no_goal_odom_tf_rviz_preflight_dispatch"]["source"] == (
        "ROS2_REALSTACK_NO_GOAL_PREFLIGHT"
    )
    assert matrix["gates"]["ros2_no_goal_odom_tf_rviz_preflight_dispatch"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-ROS2-RUNTIME-B1-NO-GOAL-ODOM-TF-RVIZ-PREFLIGHT-20260606-032.json"
    )
    preflight_details = matrix["gates"]["ros2_no_goal_odom_tf_rviz_preflight_dispatch"]["details"]
    assert preflight_details["summary"]["path"].endswith("no_goal_odom_tf_rviz_preflight_summary.json")
    assert preflight_details["observed"]["loopback_total"] == 3
    assert preflight_details["observed"]["odometry_count"] == 0
    assert preflight_details["observed"]["cloud_registered_count"] == 0
    assert preflight_details["rviz2_cli_available"] is True
    assert preflight_details["truth_to_fastlio_bridge_observed"] is False
    assert preflight_details["prior_dispatch_surface_blockers"]["resolved_by_noop_recovery"] is True
    assert preflight_details["prior_dispatch_surface_blockers"]["pmo_dispatch_blocker"]["path"].endswith(
        "PMO-ROS2-R3-DISPATCH-SURFACE-20260606-032.json"
    )
    assert matrix["gates"]["ue_runtime_command_ack"]["blocking"] is True
    assert matrix["gates"]["ue_live_echo_acceptance_fixture"]["blocking"] is True
    assert matrix["gates"]["ue_live_echo_acceptance_fixture"]["status"] == "completed"
    assert matrix["gates"]["ue_live_echo_acceptance_fixture"]["quality_status"] == (
        "source_static_live_echo_acceptance_fixture_contract_passed"
    )
    assert matrix["gates"]["ue_live_echo_acceptance_fixture"]["source"] == "UE_SOURCE_STATIC_CONTRACT"
    assert matrix["gates"]["ue_live_echo_acceptance_fixture"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-ACCEPTANCE-FIXTURE-CONTRACT-20260606-008.json"
    )
    ue_fixture_details = matrix["gates"]["ue_live_echo_acceptance_fixture"]["details"]
    assert ue_fixture_details["input_schema"] == "mosim.ue_command_echo.v1"
    assert ue_fixture_details["valid_future_live_accepted_rows"] == 5
    assert ue_fixture_details["non_live_runtime_leaks"] == 0
    assert ue_fixture_details["malformed_runtime_leaks"] == 0
    assert ue_fixture_details["rejected_runtime_leaks"] == 0
    assert ue_fixture_details["runtime_receiver_implemented"] is False
    assert ue_fixture_details["ui_asset_binding_implemented"] is False
    assert matrix["gates"]["sunray150_material_review"]["blocking"] is True
    assert matrix["gates"]["sunray150_material_review"]["status"] == (
        "completed_path_hygiene_ready_manual_review_pending"
    )
    assert matrix["gates"]["sunray150_material_review"]["quality_status"] == (
        "path_hygiene_ready_manual_visual_review_pending"
    )
    assert matrix["gates"]["sunray150_material_review"]["source"] == "SUNRAY150_ASSET_REVIEW_PACKAGE"
    assert matrix["gates"]["sunray150_material_review"]["evidence"]["path"].endswith(
        "RFLY-MOSIM-SUNRAY150-REVIEW-MANIFEST-PATH-HYGIENE-20260606-004.json"
    )
    sunray_details = matrix["gates"]["sunray150_material_review"]["details"]
    assert sunray_details["manual_review_required"] is True
    assert sunray_details["manual_review_status"] == "pending_pmo_wechat_review"
    assert sunray_details["source_manifest_all_outputs_have_project_relative_path"] is True
    assert sunray_details["source_manifest_legacy_absolute_path_field_count"] == 20
    assert sunray_details["legacy_absolute_fields_status"] == "quarantined_existing_manifest_only"
    assert sunray_details["battery_present"] is True
    assert sunray_details["battery_non_flat"] is True
    assert sunray_details["guard_landing_gear_present"] is True
    assert sunray_details["guard_landing_gear_non_flat"] is True
    assert not any(path.endswith("RATE-FEEDBACK-ISOLATION-20260606-014.json") for path in matrix["next_packets_to_consume"])
    assert not any(path.endswith("YAW-RATE-DECOUPLING-20260606-013.json") for path in matrix["next_packets_to_consume"])
    assert not any(path.endswith("PITCH-DECOUPLING-20260606-012.json") for path in matrix["next_packets_to_consume"])
    assert not any(path.endswith("RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json") for path in matrix["next_packets_to_consume"])
    assert not any(path.endswith("RUNTIME-DISABLED-SMOKE-20260606-017.json") for path in matrix["next_packets_to_consume"])
    assert not any(path.endswith("RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json") for path in matrix["next_packets_to_consume"])
    assert not any(path.endswith("PLANMANAGE-LINK-PREFLIGHT-20260606-014.json") for path in matrix["next_packets_to_consume"])


if __name__ == "__main__":
    test_p0_gap_matrix_keeps_closed_loop_blocked()
    print("[OK] P0 closed-loop gap matrix")
