#!/usr/bin/env python3
"""Regression tests for the P0 RUN_MANIFEST bundle audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "Scripts" / "quality" / "check_p0_run_bundle.py"
MANIFEST = ROOT / "Results" / "p0_runs" / "rfly_mosim_p0_slice_20260606" / "RUN_MANIFEST.json"
REPORT = ROOT / "Results" / "tmp" / "test_p0_run_bundle_audit.json"


def test_current_p0_run_bundle_is_recoverable_but_not_closed_loop() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(AUDIT),
            str(MANIFEST),
            "--output-json",
            str(REPORT),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["ok"] is False
    expected_missing = {
        "mworks.pitch_decoupling_probe.model[0]",
        "mworks.yaw_rate_decoupling_probe.model[0]",
        "mworks.rate_feedback_isolation_probe.model[0]",
        "mworks.sensor_bus_reconnect_probe.model[0]",
        "mworks.position_bridge_probe.model[0]",
        "mworks.attitude_feedback_bridge_probe.model[0]",
        "ros2.b1_032.prior_dispatch.legacy ops patrol_blocker_packet",
    }
    assert {
        issue.removeprefix("missing required path: ").split("=", 1)[0]
        for issue in report["issues"]
    } == expected_missing
    assert not any("ROS2 032 must preserve odometry_count=0" in item for item in report["issues"])
    assert not any("ROS2 032 must preserve cloud_registered_count=0" in item for item in report["issues"])
    assert not any("ROS2 032 must preserve livox_probe_count=0" in item for item in report["issues"])
    assert report["quality_status"] == "smoke_only"
    assert "planner" not in report["claim_scope"]
    assert "closed_loop" not in report["claim_scope"]
    assert any("FAST-LIO runtime is restored" in item for item in report["warnings"])
    assert any("B1 planner wrapper is blocked" in item for item in report["warnings"])
    assert any("B1 port preflight completed" in item for item in report["warnings"])
    assert any("B1 message slice built" in item for item in report["warnings"])
    assert any("B1 upstream planner deps are blocked" in item for item in report["warnings"])
    assert any("B1 plan_env/GridMap port built" in item for item in report["warnings"])
    assert any("B1 path_searching/bspline_opt port built" in item for item in report["warnings"])
    assert any("B1 traj_utils/quadrotor_msgs port built" in item for item in report["warnings"])
    assert any("B1 plan_manage link preflight built" in item for item in report["warnings"])
    assert any("MWORKS standalone trace lookup passed" in item for item in report["warnings"])
    assert any("MWORKS Factory trace reconnect is blocked" in item for item in report["warnings"])
    assert any("MWORKS Factory-lite trace probe passed" in item for item in report["warnings"])
    assert any("MWORKS incremental trace isolation found" in item for item in report["warnings"])
    assert any("MWORKS actuator wiring isolation fixed" in item for item in report["warnings"])
    assert any("MWORKS sensor-feedback isolation found" in item for item in report["warnings"])
    assert any("MWORKS attitude-feedback isolation found" in item for item in report["warnings"])
    assert any("MWORKS attitude-intermediary classification found" in item for item in report["warnings"])
    assert any("MWORKS attitude-decoupling probes restored" in item for item in report["warnings"])
    assert any("MWORKS pitch-decoupling probe restored" in item for item in report["warnings"])
    assert any("MWORKS yaw-decoupling probe restored" in item for item in report["warnings"])
    assert any("MWORKS rate-feedback isolation restored rate aliases only" in item for item in report["warnings"])
    assert any("MWORKS sensor-bus reconnect found" in item for item in report["warnings"])
    assert any("MWORKS actuator-to-wrench bridge 014" in item for item in report["warnings"])
    assert any("B1 runtime-disabled launch audit completed static review only" in item for item in report["warnings"])
    assert any("B1 runtime-disabled launch/config artifact exists" in item for item in report["warnings"])
    assert any("B1 real planner input gate 018 remains historical" in item for item in report["warnings"])
    assert any("B1 odom/cloud restore 019 restored" in item for item in report["warnings"])
    assert any("B1 long-source 031 restored" in item for item in report["warnings"])
    assert any("ROS2 032 started after no-op recovery" in item for item in report["warnings"])
    assert any("UE command adapter smoke has accepted/rejected echo rows" in item for item in report["warnings"])
    assert any("UE live-echo acceptance 008" in item for item in report["warnings"])
    assert any("Sunray150 material review 004" in item for item in report["warnings"])
    assert report["ue_command_echo_contract"]["ok"] is True
    assert report["ue_command_echo_contract"]["placeholder_rows"] == 0
    assert report["ue_command_echo_contract"]["runtime_ack_rows"] == 3
    assert report["ue_command_adapter_smoke"]["source"] == "offline_adapter_smoke"
    assert report["ue_command_adapter_smoke"]["not_runtime_ue_console"] is True
    assert report["ue_command_adapter_smoke"]["accepted"] == 2
    assert report["ue_command_adapter_smoke"]["rejected"] == 1
    assert report["ue_command_sender_source_contract"]["ok"] is True
    assert report["ue_command_sender_source_contract"]["source"] == "source_level_static_check"
    assert report["ue_command_sender_source_contract"]["not_runtime_ue_console"] is True
    assert report["ue_command_sender_source_contract"]["runtime_ack_required_before_acceptance"] is True
    assert report["ue_command_sender_loopback_smoke"]["ok"] is True
    assert report["ue_command_sender_loopback_smoke"]["source"] == "udp_loopback_smoke"
    assert report["ue_command_sender_loopback_smoke"]["not_runtime_ue_console"] is True
    assert report["ue_command_sender_loopback_smoke"]["not_mworks_or_ros2_ack"] is True
    assert report["ue_command_sender_loopback_smoke"]["received_packets"] == 4
    assert report["manual_review"]["packet_exists"] is True
    required = {item["label"]: item["exists"] for item in report["path_checks"]}
    assert required["mworks.trace_consumption_blocker"] is True
    assert required["mworks.trace_lookup_diagnostic.return_packet"] is True
    assert required["mworks.trace_lookup_diagnostic.probe_json"] is True
    assert required["mworks.trace_lookup_diagnostic.raw_reference_series_csv"] is True
    assert required["mworks.factory_trace_reconnect.blocker_packet"] is True
    assert required["mworks.factory_trace_reconnect.probe_json"] is True
    assert required["mworks.factory_lite_trace_probe.return_packet"] is True
    assert required["mworks.factory_lite_trace_probe.probe_json"] is True
    assert required["mworks.factory_lite_trace_probe.raw_alias_series_csv"] is True
    assert required["mworks.incremental_trace_isolation.return_packet"] is True
    assert required["mworks.incremental_trace_isolation.probe_json"] is True
    assert required["mworks.incremental_trace_isolation.probe_summary_csv"] is True
    assert required["mworks.actuator_wiring_isolation.return_packet"] is True
    assert required["mworks.actuator_wiring_isolation.probe_json"] is True
    assert required["mworks.actuator_wiring_isolation.probe_summary_csv"] is True
    assert required["mworks.sensor_feedback_isolation.return_packet"] is True
    assert required["mworks.sensor_feedback_isolation.probe_json"] is True
    assert required["mworks.sensor_feedback_isolation.probe_summary_csv"] is True
    assert required["mworks.attitude_feedback_isolation.return_packet"] is True
    assert required["mworks.attitude_feedback_isolation.probe_json"] is True
    assert required["mworks.attitude_feedback_isolation.probe_summary_csv"] is True
    assert required["mworks.attitude_feedback_isolation.mcp_log"] is True
    assert required["mworks.attitude_intermediary_classification.return_packet"] is True
    assert required["mworks.attitude_intermediary_classification.probe_json"] is True
    assert required["mworks.attitude_intermediary_classification.probe_summary_csv"] is True
    assert required["mworks.attitude_intermediary_classification.mcp_log"] is True
    assert required["mworks.attitude_decoupling_probe.return_packet"] is True
    assert required["mworks.attitude_decoupling_probe.probe_json"] is True
    assert required["mworks.attitude_decoupling_probe.probe_summary_csv"] is True
    assert required["mworks.attitude_decoupling_probe.mcp_log"] is True
    assert required["mworks.pitch_decoupling_probe.return_packet"] is True
    assert required["mworks.pitch_decoupling_probe.probe_json"] is True
    assert required["mworks.pitch_decoupling_probe.probe_summary_csv"] is True
    assert required["mworks.pitch_decoupling_probe.mcp_log"] is True
    assert required["mworks.pitch_decoupling_probe.model[0]"] is False
    assert required["mworks.yaw_rate_decoupling_probe.return_packet"] is True
    assert required["mworks.yaw_rate_decoupling_probe.probe_json"] is True
    assert required["mworks.yaw_rate_decoupling_probe.probe_summary_csv"] is True
    assert required["mworks.yaw_rate_decoupling_probe.mcp_log"] is True
    assert required["mworks.yaw_rate_decoupling_probe.unknowns_risks_next_validation"] is True
    assert required["mworks.yaw_rate_decoupling_probe.model[0]"] is False
    assert required["mworks.rate_feedback_isolation_probe.return_packet"] is True
    assert required["mworks.rate_feedback_isolation_probe.probe_json"] is True
    assert required["mworks.rate_feedback_isolation_probe.probe_summary_csv"] is True
    assert required["mworks.rate_feedback_isolation_probe.mcp_log"] is True
    assert required["mworks.rate_feedback_isolation_probe.unknowns_risks_next_validation"] is True
    assert required["mworks.rate_feedback_isolation_probe.model[0]"] is False
    assert required["mworks.sensor_bus_reconnect_probe.blocker_packet"] is True
    assert required["mworks.sensor_bus_reconnect_probe.probe_json"] is True
    assert required["mworks.sensor_bus_reconnect_probe.probe_summary_csv"] is True
    assert required["mworks.sensor_bus_reconnect_probe.mcp_log"] is True
    assert required["mworks.sensor_bus_reconnect_probe.model[0]"] is False
    assert required["mworks.position_bridge_probe.return_packet"] is True
    assert required["mworks.position_bridge_probe.probe_json"] is True
    assert required["mworks.position_bridge_probe.alias_samples_csv"] is True
    assert required["mworks.position_bridge_probe.mcp_log"] is True
    assert required["mworks.position_bridge_probe.model[0]"] is False
    assert required["mworks.attitude_feedback_bridge_probe.model[0]"] is False
    assert required["mworks.actuator_to_wrench_bridge_smoke.return_packet"] is True
    assert required["mworks.actuator_to_wrench_bridge_smoke.evidence_dir"] is True
    assert required["mworks.external_frame_boundary_smoke.return_packet"] is True
    assert required["mworks.external_frame_boundary_smoke.evidence_dir"] is True
    assert required["ros2.b1_unblock.blocker_packet"] is True
    assert required["ros2.b1_planner_wrapper.blocker_packet"] is True
    assert required["ros2.b1_port_preflight.return_packet"] is True
    assert required["ros2.b1_port_preflight.build_log"] is True
    assert required["ros2.b1_msg_port_slice.return_packet"] is True
    assert required["ros2.b1_msg_port_slice.artifact[0]"] is True
    assert required["ros2.b1_msg_port_slice.artifact[1]"] is True
    assert required["ros2.b1_planner_node.return_packet"] is True
    assert required["ros2.b1_planner_node.build_log[0]"] is True
    assert required["ros2.b1_planner_node.build_log[1]"] is True
    assert required["ros2.b1_planner_node.build_log[2]"] is True
    assert required["ros2.b1_planner_node.installed_executable"] is True
    assert required["ros2.b1_upstream_planner_deps.blocker_packet"] is True
    assert required["ros2.b1_upstream_planner_deps.producer_scan"] is True
    assert required["ros2.b1_upstream_planner_deps.dependency_surface_scan"] is True
    assert required["ros2.b1_upstream_planner_deps.colcon_list"] is True
    assert required["ros2.b1_upstream_planner_deps.plan_env_build_probe"] is True
    assert required["ros2.b1_planenv_gridmap_port.return_packet"] is True
    assert required["ros2.b1_planenv_gridmap_port.red_build_log"] is True
    assert required["ros2.b1_planenv_gridmap_port.post_patch_log[0]"] is True
    assert required["ros2.b1_planenv_gridmap_port.post_patch_log[4]"] is True
    assert required["ros2.b1_planenv_gridmap_port.installed_artifact[0]"] is True
    assert required["ros2.b1_planenv_gridmap_port.installed_artifact[2]"] is True
    assert required["ros2.b1_planenv_gridmap_port.classification_log[0]"] is True
    assert required["ros2.b1_planenv_gridmap_port.classification_log[1]"] is True
    assert required["ros2.b1_path_bspline_port.return_packet"] is True
    assert required["ros2.b1_path_bspline_port.build_log[0][0]"] is True
    assert required["ros2.b1_path_bspline_port.build_log[0][1]"] is True
    assert required["ros2.b1_path_bspline_port.build_log[1][2]"] is True
    assert required["ros2.b1_path_bspline_port.installed_artifact[0]"] is True
    assert required["ros2.b1_path_bspline_port.installed_artifact[3]"] is True
    assert required["ros2.b1_path_bspline_port.classification_log[0]"] is True
    assert required["ros2.b1_path_bspline_port.classification_log[2]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.return_packet"] is True
    assert required["ros2.b1_traj_quadmsgs_port.red_build_log[0]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.green_log[0][5]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.red_build_log[1]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.green_log[1][1]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.installed_artifact[0]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.installed_artifact[4]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.classification_log[0]"] is True
    assert required["ros2.b1_traj_quadmsgs_port.classification_log[2]"] is True
    assert required["ros2.b1_planmanage_link_preflight.return_packet"] is True
    assert required["ros2.b1_planmanage_link_preflight.build_log[0]"] is True
    assert required["ros2.b1_planmanage_link_preflight.build_log[5][1]"] is True
    assert required["ros2.b1_planmanage_link_preflight.installed_artifact[0]"] is True
    assert required["ros2.b1_planmanage_link_preflight.installed_artifact[2]"] is True
    assert required["ros2.b1_planmanage_link_preflight.evidence_artifact[0]"] is True
    assert required["ros2.b1_planmanage_link_preflight.evidence_artifact[10]"] is True
    assert required["ros2.b1_runtime_disabled_launch_audit.return_packet"] is True
    assert required["ros2.b1_runtime_disabled_launch_audit.inspected_file[0]"] is True
    assert required["ros2.b1_runtime_disabled_launch_audit.inspected_file[10]"] is True
    assert required["ros2.b1_runtime_disabled_launch_audit.evidence_artifact[0]"] is True
    assert required["ros2.b1_runtime_disabled_launch_audit.evidence_artifact[4]"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.return_packet"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.inventory"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.source_artifact[0]"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.source_artifact[1]"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.installed_artifact[0]"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.installed_artifact[2]"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.config_diff_summary"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.validation_log[0]"] is True
    assert required["ros2.b1_runtime_disabled_launch_config.validation_log[4]"] is True
    assert required["ros2.b1_runtime_disabled_smoke.return_packet"] is True
    assert required["ros2.b1_runtime_disabled_smoke.script"] is True
    assert required["ros2.b1_runtime_disabled_smoke.command"] is True
    assert required["ros2.b1_runtime_disabled_smoke.log"] is True
    assert required["ros2.b1_runtime_disabled_smoke.wrapper_exit"] is True
    assert required["ros2.b1_runtime_disabled_smoke.evidence_artifact[4]"] is True
    assert required["ros2.b1_real_planner_input_gate.blocker_packet"] is True
    assert required["ros2.b1_real_planner_input_gate.probe_summary"] is True
    assert required["ros2.b1_real_planner_input_gate.command_script"] is True
    assert required["ros2.b1_real_planner_input_gate.topic_list_typed"] is True
    assert required["ros2.b1_real_planner_input_gate./Odometry.topic_info"] is True
    assert required["ros2.b1_real_planner_input_gate./Odometry.topic_hz"] is True
    assert required["ros2.b1_real_planner_input_gate./cloud_registered.topic_info"] is True
    assert required["ros2.b1_real_planner_input_gate./cloud_registered.topic_hz"] is True
    assert required["ros2.b1_odom_cloud_restore.return_packet"] is True
    assert required["ros2.b1_odom_cloud_restore.evidence_dir"] is True
    assert required["ros2.b1_odom_cloud_restore.summary_json"] is True
    assert required["ros2.b1_odom_cloud_restore./Odometry.sample_file"] is True
    assert required["ros2.b1_odom_cloud_restore./cloud_registered.sample_file"] is True
    assert required["ros2.b1_long_source_startup_discipline.return_packet"] is True
    assert required["ros2.b1_long_source_startup_discipline.evidence_dir"] is True
    assert required["ros2.b1_032.blocker_packet"] is True
    assert required["ros2.b1_032.evidence_dir"] is True
    assert required["ros2.b1_032.summary"] is True
    assert required["ros2.b1_032.prior_dispatch.legacy ops patrol_blocker_packet"] is False
    assert required["ros2.b1_032.prior_dispatch.pmo_dispatch_blocker_packet"] is True
    assert required["planner.setpoint_trace"] is True
    assert required["ue.command_echo_log"] is True
    assert required["ue.command_input_log"] is True
    assert required["ue.command_adapter_smoke_json"] is True
    assert required["ue.command_sender_source"] is True
    assert required["ue.command_sender_header"] is True
    assert required["ue.command_sender_contract"] is True
    assert required["ue.command_sender_loopback_smoke_json"] is True
    assert required["ue.command_sender_loopback_received"] is True
    assert required["ue.live_echo_acceptance_fixture.return_packet"] is True
    assert required["ue.live_echo_acceptance_fixture.evidence_dir"] is True
    assert required["ue.command_schema"] is True
    assert required["ue.command_echo_schema"] is True
    assert required["sunray150.material_review.return_packet"] is True
    assert required["sunray150.material_review.evidence_dir"] is True
    assert required["sunray150.material_review.path_hygiene_evidence"] is True
    assert any("B1 planner-node preflight built" in item for item in report["warnings"])
    assert any("source-level UDP packet surface" in item for item in report["warnings"])
    assert any("loopback proves only UDP packet transport" in item for item in report["warnings"])


if __name__ == "__main__":
    test_current_p0_run_bundle_is_recoverable_but_not_closed_loop()
    print("[OK] P0 run bundle audit")
