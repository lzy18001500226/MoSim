#!/usr/bin/env python3
"""Summarize the current P0 closed-loop gaps from manifest and audit evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def packet_state(path: str) -> dict[str, Any]:
    if not path:
        return {"path": "", "exists": False, "status": ""}
    packet_path = repo_path(path)
    state: dict[str, Any] = {"path": rel(packet_path), "exists": packet_path.exists(), "status": ""}
    if packet_path.exists() and packet_path.suffix.lower() == ".json":
        try:
            state["status"] = str(read_json(packet_path).get("status", ""))
        except Exception as exc:  # pragma: no cover - defensive for corrupt evidence files.
            state["status"] = f"unreadable: {exc}"
    return state


def build_gap_matrix(manifest: dict[str, Any], audit: dict[str, Any], manifest_path: Path, audit_path: Path) -> dict[str, Any]:
    claim_scope = [str(item) for item in as_list(manifest.get("claim_scope"))]
    blockers = [str(item) for item in as_list(manifest.get("blockers"))]
    mworks = as_mapping(manifest.get("mworks"))
    ros2 = as_mapping(manifest.get("ros2"))
    ue = as_mapping(manifest.get("ue"))
    planner = as_mapping(manifest.get("planner"))

    b1 = {
        "real_planner": as_mapping(ros2.get("position_command_b1_real_planner")),
        "planner_wrapper": as_mapping(ros2.get("position_command_b1_planner_wrapper")),
        "path_bspline_port": as_mapping(ros2.get("position_command_b1_path_bspline_port")),
        "traj_quadmsgs_port": as_mapping(ros2.get("position_command_b1_traj_quadmsgs_port")),
        "planmanage_link_preflight": as_mapping(ros2.get("position_command_b1_planmanage_link_preflight")),
        "runtime_disabled_launch_audit": as_mapping(ros2.get("position_command_b1_runtime_disabled_launch_audit")),
        "runtime_disabled_launch_config": as_mapping(ros2.get("position_command_b1_runtime_disabled_launch_config")),
        "runtime_disabled_smoke": as_mapping(ros2.get("position_command_b1_runtime_disabled_smoke")),
        "real_planner_input_gate": as_mapping(ros2.get("position_command_b1_real_planner_input_gate")),
        "odom_cloud_restore": as_mapping(ros2.get("position_command_b1_odom_cloud_restore")),
        "planner_startup_probe": as_mapping(ros2.get("position_command_b1_planner_startup_probe")),
        "long_source_startup_discipline": as_mapping(
            ros2.get("position_command_b1_long_source_startup_discipline_rerun")
        ),
        "no_goal_odom_tf_rviz_preflight_032": as_mapping(
            ros2.get("position_command_b1_no_goal_odom_tf_rviz_preflight_032")
        ),
    }
    mworks_attitude_intermediary = as_mapping(mworks.get("attitude_intermediary_classification"))
    mworks_attitude_decoupling = as_mapping(mworks.get("attitude_decoupling_probe"))
    mworks_pitch_decoupling = as_mapping(mworks.get("pitch_decoupling_probe"))
    mworks_yaw_rate_decoupling = as_mapping(mworks.get("yaw_rate_decoupling_probe"))
    mworks_rate_feedback_isolation = as_mapping(mworks.get("rate_feedback_isolation_probe"))
    mworks_sensor_bus_reconnect = as_mapping(mworks.get("sensor_bus_reconnect_probe"))
    mworks_position_bridge = as_mapping(mworks.get("position_bridge_probe"))
    mworks_next_sensor_display_group = as_mapping(mworks.get("next_sensor_display_group_probe"))
    mworks_first_control_feedback_group = as_mapping(mworks.get("first_control_feedback_group_probe"))
    mworks_attitude_feedback_bridge = as_mapping(mworks.get("attitude_feedback_bridge_probe"))
    mworks_actuator_to_wrench_bridge = as_mapping(mworks.get("actuator_to_wrench_bridge_smoke"))
    mworks_external_frame_boundary = as_mapping(mworks.get("external_frame_boundary_smoke"))
    ue_live_echo_acceptance_fixture = as_mapping(ue.get("live_echo_acceptance_fixture_contract"))
    sunray150_material_review = as_mapping(as_mapping(manifest.get("sunray150")).get("material_review"))
    mworks_attitude = (
        mworks_rate_feedback_isolation
        or mworks_yaw_rate_decoupling
        or mworks_pitch_decoupling
        or mworks_attitude_decoupling
        or mworks_attitude_intermediary
    )

    matrix = {
        "schema": "mosim.p0_closed_loop_gap_matrix.v1",
        "manifest": rel(manifest_path),
        "audit": rel(audit_path),
        "run_id": str(manifest.get("run_id", "")),
        "quality_status": str(manifest.get("quality_status", "")),
        "claim_scope": claim_scope,
        "closed_loop_ready": False,
        "planner_ready": False,
        "must_not_claim": [
            "planner",
            "closed_loop",
            "Factory trace consumption",
            "controller performance",
            "runtime UE Experiment Console",
        ],
        "gates": {
            "evidence_bundle": {
                "status": "pass_smoke_only" if audit.get("ok") is True else "failed",
                "source": "P0_BUNDLE_AUDIT",
                "blocking": audit.get("ok") is not True,
                "details": {
                    "audit_warnings": len(as_list(audit.get("warnings"))),
                    "audit_issues": len(as_list(audit.get("issues"))),
                },
            },
            "mworks_same_trace_consumption": {
                "status": str(mworks.get("setpoint_trace_consumption_status", "")),
                "source": "MWORKS_MCP",
                "blocking": str(mworks.get("setpoint_trace_consumption_status", "")) != "pass",
                "evidence": packet_state(str(mworks.get("trace_consumption_blocker", ""))),
                "next": "Wait for or execute MWORKS attitude decoupling 011, then reconnect the smallest passing group before full Factory retry.",
            },
            "mworks_attitude_feedback_decoupling": {
                "status": str(mworks_attitude.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": str(mworks.get("setpoint_trace_consumption_status", "")) != "pass",
                "evidence": packet_state(str(mworks_attitude.get("return_packet", ""))),
                "next": "Use the passing Iso21 rate-alias baseline to decide explicit-rate controller surface versus the next narrow sensor-bus/component reconnect before any full Factory retry.",
            },
            "mworks_sensor_bus_reconnect": {
                "status": str(mworks_sensor_bus_reconnect.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": True,
                "evidence": packet_state(str(mworks_sensor_bus_reconnect.get("blocker_packet", ""))),
                "details": {
                    "blocker_kind": mworks_sensor_bus_reconnect.get("blocker_kind", ""),
                    "first_new_boundary": next(
                        (
                            str(probe.get("first_new_boundary", ""))
                            for probe in as_list(mworks_sensor_bus_reconnect.get("probe_results"))
                            if isinstance(probe, dict)
                        ),
                        "",
                    ),
                    "error_6140_present": next(
                        (
                            probe.get("error_6140_present")
                            for probe in as_list(mworks_sensor_bus_reconnect.get("probe_results"))
                            if isinstance(probe, dict)
                        ),
                        None,
                    ),
                },
                "next": "Create Iso23 with a RealExpression or sampled/held position bridge before retrying any larger Factory trace wrapper.",
            },
            "mworks_position_bridge": {
                "status": str(mworks_position_bridge.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": str(mworks.get("setpoint_trace_consumption_status", "")) != "pass",
                "evidence": packet_state(str(mworks_position_bridge.get("return_packet", ""))),
                "details": {
                    "bridge_passed": any(
                        isinstance(probe, dict)
                        and probe.get("probe_id") == "iso23_position_sample_hold_bridge"
                        and probe.get("simulate_data") is True
                        for probe in as_list(mworks_position_bridge.get("probe_results"))
                    ),
                    "error_6140_present": next(
                        (
                            probe.get("error_6140_present")
                            for probe in as_list(mworks_position_bridge.get("probe_results"))
                            if isinstance(probe, dict)
                            and probe.get("probe_id") == "iso23_position_sample_hold_bridge"
                        ),
                        None,
                    ),
                    "factory_trace_consumption_claimed": False,
                },
                "next": "Use Iso23 as the passing display-position bridge baseline, then add one remaining sensor/display group at a time before any full Factory retry.",
            },
            "mworks_next_sensor_display_group": {
                "status": str(mworks_next_sensor_display_group.get("quality_status", "not_integrated")),
                "source": "file_topology_inspection",
                "blocking": True,
                "evidence": packet_state(str(mworks_next_sensor_display_group.get("blocker_packet", ""))),
                "details": {
                    "blocker_kind": mworks_next_sensor_display_group.get("blocker_kind", ""),
                    "exactly_one_group_added": mworks_next_sensor_display_group.get("exactly_one_group_added"),
                    "topology_comparison": mworks_next_sensor_display_group.get("topology_comparison", ""),
                    "prior_passing_mworks_mcp_evidence": mworks_next_sensor_display_group.get(
                        "prior_passing_mworks_mcp_evidence", ""
                    ),
                    "topology_findings": [
                        {
                            "target": item.get("target_connection", item.get("target_remaining_connections", "")),
                            "status": item.get("status", ""),
                        }
                        for item in as_list(mworks_next_sensor_display_group.get("topology_findings"))
                        if isinstance(item, dict)
                    ],
                    "not_mworks_simulation_evidence": True,
                },
                "next": "Open a new task permitting exactly one controller/control-feedback reconnect group from Iso23; preserve the sampled/held display-position bridge and avoid full Factory retry.",
            },
            "mworks_first_control_feedback_group": {
                "status": str(mworks_first_control_feedback_group.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": True,
                "evidence": packet_state(str(mworks_first_control_feedback_group.get("blocker_packet", ""))),
                "details": {
                    "blocker_kind": mworks_first_control_feedback_group.get("blocker_kind", ""),
                    "selected_group": mworks_first_control_feedback_group.get("selected_group", ""),
                    "exactly_one_group_added": mworks_first_control_feedback_group.get("exactly_one_group_added"),
                    "iso23_display_bridge_preserved": mworks_first_control_feedback_group.get(
                        "iso23_display_bridge_preserved"
                    ),
                    "check_model_status": as_mapping(mworks_first_control_feedback_group.get("check_model")).get(
                        "status"
                    ),
                    "simulate_model_status": as_mapping(mworks_first_control_feedback_group.get("simulate_model")).get(
                        "status"
                    ),
                    "simulate_model_data": as_mapping(mworks_first_control_feedback_group.get("simulate_model")).get(
                        "data"
                    ),
                    "get_var_times_count": as_mapping(mworks_first_control_feedback_group.get("get_var_times")).get(
                        "count"
                    ),
                    "aliases_available": as_mapping(mworks_first_control_feedback_group.get("aliases")).get(
                        "available"
                    ),
                    "error_6140_present": mworks_first_control_feedback_group.get("error_6140_present"),
                    "first_new_boundary": mworks_first_control_feedback_group.get("first_new_boundary", ""),
                },
                "next": "Open a narrow attitude-feedback bridge task: sampled/held or first-order controller measurement feedback on top of Iso23, still without full Factory retry or actuator/motor reconnect.",
            },
            "mworks_attitude_feedback_bridge": {
                "status": str(mworks_attitude_feedback_bridge.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": True,
                "evidence": packet_state(str(mworks_attitude_feedback_bridge.get("return_packet", ""))),
                "details": {
                    "selected_bridge_variant": mworks_attitude_feedback_bridge.get("selected_bridge_variant", ""),
                    "bridge_passed": any(
                        isinstance(probe, dict)
                        and probe.get("probe_id") == "iso25_sample_hold_attitude_feedback_bridge"
                        and probe.get("simulate_data") is True
                        and probe.get("result_context_restored") is True
                        for probe in as_list(mworks_attitude_feedback_bridge.get("probe_results"))
                    ),
                    "iso23_display_bridge_preserved": any(
                        isinstance(probe, dict)
                        and probe.get("probe_id") == "iso25_sample_hold_attitude_feedback_bridge"
                        and probe.get("iso23_display_bridge_preserved") is True
                        for probe in as_list(mworks_attitude_feedback_bridge.get("probe_results"))
                    ),
                    "get_var_times_count": next(
                        (
                            probe.get("get_var_times_count")
                            for probe in as_list(mworks_attitude_feedback_bridge.get("probe_results"))
                            if isinstance(probe, dict)
                            and probe.get("probe_id") == "iso25_sample_hold_attitude_feedback_bridge"
                        ),
                        None,
                    ),
                    "error_6140_present": next(
                        (
                            probe.get("error_6140_present")
                            for probe in as_list(mworks_attitude_feedback_bridge.get("probe_results"))
                            if isinstance(probe, dict)
                            and probe.get("probe_id") == "iso25_sample_hold_attitude_feedback_bridge"
                        ),
                        None,
                    ),
                    "factory_trace_consumption_claimed": False,
                },
                "next": "Use Iso25 only as the next narrow bridge baseline; add one downstream control-output, speedSensor, actuator, or motor wiring group at a time before any full Factory retry.",
            },
            "mworks_actuator_to_wrench_bridge": {
                "status": str(mworks_actuator_to_wrench_bridge.get("status", "not_integrated")),
                "quality_status": str(mworks_actuator_to_wrench_bridge.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": True,
                "evidence": packet_state(str(mworks_actuator_to_wrench_bridge.get("return_packet", ""))),
                "details": {
                    "model_name": mworks_actuator_to_wrench_bridge.get("model_name", ""),
                    "check_model_status": mworks_actuator_to_wrench_bridge.get("check_model_status", ""),
                    "simulate_status": mworks_actuator_to_wrench_bridge.get("simulate_status", ""),
                    "get_var_times_count": mworks_actuator_to_wrench_bridge.get("get_var_times_count"),
                    "command_domain_label": mworks_actuator_to_wrench_bridge.get("command_domain_label", ""),
                    "bridge_command_error_abs_sum_end": as_mapping(
                        mworks_actuator_to_wrench_bridge.get("result_summary")
                    ).get("bridge_command_error_abs_sum_end"),
                    "force_application_error_at_samples": as_mapping(
                        mworks_actuator_to_wrench_bridge.get("result_summary")
                    ).get("force_application_error_at_samples"),
                    "torque_application_error_at_samples": as_mapping(
                        mworks_actuator_to_wrench_bridge.get("result_summary")
                    ).get("torque_application_error_at_samples"),
                    "minimal_actuator_to_wrench_bridge_smoke": as_mapping(
                        mworks_actuator_to_wrench_bridge.get("claim_boundary")
                    ).get("minimal_actuator_to_wrench_bridge_smoke"),
                    "factory_trace_consumption": as_mapping(
                        mworks_actuator_to_wrench_bridge.get("claim_boundary")
                    ).get("factory_trace_consumption"),
                    "full_actuator_or_plant_closure": as_mapping(
                        mworks_actuator_to_wrench_bridge.get("claim_boundary")
                    ).get("full_actuator_or_plant_closure"),
                },
                "next": str(mworks_actuator_to_wrench_bridge.get("next", "")),
            },
            "mworks_external_frame_boundary": {
                "status": str(mworks_external_frame_boundary.get("status", "not_integrated")),
                "quality_status": str(mworks_external_frame_boundary.get("quality_status", "not_integrated")),
                "source": "MWORKS_MCP",
                "blocking": True,
                "evidence": packet_state(str(mworks_external_frame_boundary.get("return_packet", ""))),
                "details": {
                    "model_name": mworks_external_frame_boundary.get("model_name", ""),
                    "check_model_status": mworks_external_frame_boundary.get("check_model_status", ""),
                    "simulate_status": mworks_external_frame_boundary.get("simulate_status", ""),
                    "get_var_times_count": mworks_external_frame_boundary.get("get_var_times_count"),
                    "external_body_component": mworks_external_frame_boundary.get("external_body_component", ""),
                    "external_force_torque_component": mworks_external_frame_boundary.get(
                        "external_force_torque_component", ""
                    ),
                    "bridge_command_error_abs_sum_end": as_mapping(
                        mworks_external_frame_boundary.get("result_summary")
                    ).get("bridge_command_error_abs_sum_end"),
                    "external_boundary_gate_error_end": as_mapping(
                        mworks_external_frame_boundary.get("result_summary")
                    ).get("external_boundary_gate_error_end"),
                    "external_force_application_error_at_samples": as_mapping(
                        mworks_external_frame_boundary.get("result_summary")
                    ).get("external_force_application_error_at_samples"),
                    "external_torque_application_error_at_samples": as_mapping(
                        mworks_external_frame_boundary.get("result_summary")
                    ).get("external_torque_application_error_at_samples"),
                    "external_force_matches_adapter_error_at_samples": as_mapping(
                        mworks_external_frame_boundary.get("result_summary")
                    ).get("external_force_matches_adapter_error_at_samples"),
                    "external_torque_matches_adapter_error_at_samples": as_mapping(
                        mworks_external_frame_boundary.get("result_summary")
                    ).get("external_torque_matches_adapter_error_at_samples"),
                    "minimal_external_frame_boundary_smoke": as_mapping(
                        mworks_external_frame_boundary.get("claim_boundary")
                    ).get("minimal_external_frame_boundary_smoke"),
                    "factory_trace_consumption": as_mapping(
                        mworks_external_frame_boundary.get("claim_boundary")
                    ).get("factory_trace_consumption"),
                    "quadchassis_or_full_plant_closure": as_mapping(
                        mworks_external_frame_boundary.get("claim_boundary")
                    ).get("quadchassis_or_full_plant_closure"),
                },
                "next": str(mworks_external_frame_boundary.get("next", "")),
            },
            "ros2_real_planner_runtime": {
                "status": str(b1["real_planner"].get("status", "")),
                "source": "ROS2_REALSTACK",
                "blocking": b1["real_planner"].get("b1_executable_now") is not True,
                "evidence": packet_state(str(b1["real_planner"].get("blocker_packet", ""))),
                "next": "Consume ROS2 014 full plan_manage link preflight, then design a runtime-disabled launch smoke before any recorder.",
            },
            "ros2_real_planner_input_gate": {
                "status": str(b1["real_planner_input_gate"].get("quality_status", "not_integrated")),
                "source": "ROS2_REALSTACK",
                "blocking": True,
                "evidence": packet_state(str(b1["real_planner_input_gate"].get("blocker_packet", ""))),
                "details": {
                    "real_odometry_present_now": b1["real_planner_input_gate"].get("real_odometry_present_now"),
                    "real_cloud_registered_present_now": b1["real_planner_input_gate"].get(
                        "real_cloud_registered_present_now"
                    ),
                    "runtime_disabled_false_may_be_safely_attempted_later": b1["real_planner_input_gate"].get(
                        "runtime_disabled_false_may_be_safely_attempted_later"
                    ),
                },
                "next": "Use 018 as historical blocker context; consume 019 restored odom/cloud evidence before any runtime_disabled=false planner startup probe.",
            },
            "ros2_odom_cloud_restore": {
                "status": str(b1["odom_cloud_restore"].get("quality_status", "not_integrated")),
                "source": "ROS2_REALSTACK",
                "blocking": True,
                "evidence": packet_state(str(b1["odom_cloud_restore"].get("return_packet", ""))),
                "details": {
                    "ready_for_later_separate_runtime_disabled_false_startup_probe": b1["odom_cloud_restore"].get(
                        "ready_for_later_separate_runtime_disabled_false_startup_probe"
                    ),
                    "planner_ready": b1["odom_cloud_restore"].get("planner_ready"),
                    "closed_loop_ready": b1["odom_cloud_restore"].get("closed_loop_ready"),
                    "position_command_recorder_allowed": b1["odom_cloud_restore"].get(
                        "position_command_recorder_allowed"
                    ),
                    "planner_startup_executed": b1["odom_cloud_restore"].get("planner_startup_executed"),
                    "odometry_count": as_mapping(
                        as_mapping(b1["odom_cloud_restore"].get("required_topics")).get("/Odometry")
                    ).get("recorded_count"),
                    "odometry_rate_hz": as_mapping(
                        as_mapping(b1["odom_cloud_restore"].get("required_topics")).get("/Odometry")
                    ).get("estimated_recorded_rate_hz"),
                    "cloud_registered_count": as_mapping(
                        as_mapping(b1["odom_cloud_restore"].get("required_topics")).get("/cloud_registered")
                    ).get("recorded_count"),
                    "cloud_registered_rate_hz": as_mapping(
                        as_mapping(b1["odom_cloud_restore"].get("required_topics")).get("/cloud_registered")
                    ).get("estimated_recorded_rate_hz"),
                    "truth_status": as_mapping(b1["odom_cloud_restore"].get("truth_evaluation")).get("status"),
                    "truth_position_rmse_m": as_mapping(
                        as_mapping(b1["odom_cloud_restore"].get("truth_evaluation")).get("metrics")
                    ).get("position_rmse_m"),
                },
                "next": "Open a separate bounded runtime_disabled=false planner startup probe against freshly restored /Odometry and /cloud_registered; keep recorder and PositionCommand claims blocked.",
            },
            "ros2_long_source_startup_discipline": {
                "status": str(b1["long_source_startup_discipline"].get("status", "not_integrated")),
                "quality_status": str(
                    b1["long_source_startup_discipline"].get("quality_status", "not_integrated")
                ),
                "source": "ROS2_REALSTACK",
                "blocking": True,
                "evidence": packet_state(str(b1["long_source_startup_discipline"].get("return_packet", ""))),
                "details": {
                    "source_frame_count": b1["long_source_startup_discipline"].get("source_frame_count"),
                    "source_coordinate_frame": b1["long_source_startup_discipline"].get("source_coordinate_frame"),
                    "startup_order": b1["long_source_startup_discipline"].get("startup_order"),
                    "livox_count": b1["long_source_startup_discipline"].get("livox_count"),
                    "imu_count": b1["long_source_startup_discipline"].get("imu_count"),
                    "odometry_count": b1["long_source_startup_discipline"].get("odometry_count"),
                    "cloud_registered_count": b1["long_source_startup_discipline"].get("cloud_registered_count"),
                    "loopback_total": b1["long_source_startup_discipline"].get("loopback_total"),
                    "no_effective_points": b1["long_source_startup_discipline"].get("no_effective_points"),
                    "position_cmd_forbidden_topic_present": as_mapping(
                        b1["long_source_startup_discipline"].get("forbidden_topics_absent_or_zero")
                    ).get("/position_cmd"),
                    "planning_bspline_forbidden_topic_present": as_mapping(
                        b1["long_source_startup_discipline"].get("forbidden_topics_absent_or_zero")
                    ).get("/planning/bspline"),
                    "cleanup": b1["long_source_startup_discipline"].get("cleanup", ""),
                },
                "next": str(b1["long_source_startup_discipline"].get("next", "")),
            },
            "ros2_planner_startup_probe": {
                "status": str(b1["planner_startup_probe"].get("quality_status", "not_integrated")),
                "source": "ROS2_REALSTACK",
                "blocking": True,
                "evidence": packet_state(str(b1["planner_startup_probe"].get("blocker_packet", ""))),
                "details": {
                    "fresh_restore_ready": as_mapping(b1["planner_startup_probe"].get("summary")).get(
                        "fresh_restore_ready"
                    ),
                    "planner_surface_initialized": as_mapping(b1["planner_startup_probe"].get("summary")).get(
                        "planner_surface_initialized"
                    ),
                    "planner_consumed_inputs": as_mapping(b1["planner_startup_probe"].get("summary")).get(
                        "planner_consumed_inputs"
                    ),
                    "planner_ready": b1["planner_startup_probe"].get("planner_ready"),
                    "closed_loop_ready": b1["planner_startup_probe"].get("closed_loop_ready"),
                    "position_command_recorder_allowed": b1["planner_startup_probe"].get(
                        "position_command_recorder_allowed"
                    ),
                    "odometry_count": as_mapping(
                        as_mapping(b1["planner_startup_probe"].get("fresh_restore_evidence")).get("counts")
                    ).get("/Odometry"),
                    "cloud_registered_count": as_mapping(
                        as_mapping(b1["planner_startup_probe"].get("fresh_restore_evidence")).get("counts")
                    ).get("/cloud_registered"),
                    "odometry_publisher_count_during_planner": as_mapping(
                        as_mapping(
                            as_mapping(b1["planner_startup_probe"].get("planner_startup_probe")).get(
                                "topic_info_evidence"
                            )
                        ).get("/Odometry")
                    ).get("publisher_count"),
                    "cloud_publisher_count_during_planner": as_mapping(
                        as_mapping(
                            as_mapping(b1["planner_startup_probe"].get("planner_startup_probe")).get(
                                "topic_info_evidence"
                            )
                        ).get("/cloud_registered")
                    ).get("publisher_count"),
                    "planning_bspline_accepted_runtime_evidence": as_mapping(
                        as_mapping(
                            as_mapping(b1["planner_startup_probe"].get("planner_startup_probe")).get(
                                "topic_info_evidence"
                            )
                        ).get("/planning/bspline")
                    ).get("accepted_runtime_evidence"),
                },
                "next": "Run a separate PMO-approved stable-source input-consumption retry: keep /Odometry and /cloud_registered publishers alive, prove topic echo --once before and during planner startup, and still keep PositionCommand recorder blocked.",
            },
            "ros2_planner_dependency_surfaces": {
                "status": str(b1["runtime_disabled_smoke"].get("status", "not_integrated")),
                "source": "ROS2_REALSTACK",
                "blocking": True,
                "evidence": packet_state(str(b1["runtime_disabled_smoke"].get("return_packet", ""))),
                "details": {
                    "quality_status": b1["runtime_disabled_smoke"].get("quality_status", ""),
                    "launch_config_quality_status": b1["runtime_disabled_launch_config"].get("quality_status", ""),
                    "runtime_disabled_guard_smoke_passed": b1["runtime_disabled_smoke"].get("quality_status")
                    == "runtime_disabled_smoke_passed",
                    "ready_for_later_runtime_disabled_smoke": as_mapping(
                        b1["runtime_disabled_launch_config"].get("summary")
                    ).get("ready_for_later_pmo_approved_runtime_disabled_smoke"),
                    "ready_for_real_planner_runtime": as_mapping(b1["runtime_disabled_smoke"].get("summary")).get(
                        "ready_for_real_planner_runtime"
                    ),
                    "ready_for_runtime_recorder": as_mapping(b1["runtime_disabled_smoke"].get("summary")).get(
                        "ready_for_runtime_recorder"
                    ),
                    "guard_message_seen": as_mapping(b1["runtime_disabled_smoke"].get("runtime_disabled_smoke")).get(
                        "guard_message_seen"
                    ),
                    "runtime_disabled_launch_exit_code": as_mapping(
                        b1["runtime_disabled_smoke"].get("runtime_disabled_smoke")
                    ).get("launch_exit_code"),
                    "ros2_run_or_launch_executed": True,
                },
                "next": "Open a separate real planner runtime input gate only after real local sensed /Odometry plus /cloud_registered are present; recorder and PositionCommand evidence remain blocked.",
            },
            "ros2_no_goal_odom_tf_rviz_preflight_dispatch": {
                "status": str(b1["no_goal_odom_tf_rviz_preflight_032"].get("status", "not_integrated")),
                "quality_status": str(
                    b1["no_goal_odom_tf_rviz_preflight_032"].get("quality_status", "not_integrated")
                ),
                "source": "ROS2_REALSTACK_NO_GOAL_PREFLIGHT",
                "blocking": True,
                "evidence": packet_state(
                    str(b1["no_goal_odom_tf_rviz_preflight_032"].get("blocker_packet", ""))
                ),
                "details": {
                    "summary": packet_state(str(b1["no_goal_odom_tf_rviz_preflight_032"].get("summary", ""))),
                    "evidence_dir": packet_state(
                        str(b1["no_goal_odom_tf_rviz_preflight_032"].get("evidence_dir", ""))
                    ),
                    "prior_dispatch_surface_blockers": {
                        "coagentops_blocker": packet_state(
                            str(
                                as_mapping(
                                    b1["no_goal_odom_tf_rviz_preflight_032"].get(
                                        "prior_dispatch_surface_blockers"
                                    )
                                ).get("coagentops_blocker_packet", "")
                            )
                        ),
                        "pmo_dispatch_blocker": packet_state(
                            str(
                                as_mapping(
                                    b1["no_goal_odom_tf_rviz_preflight_032"].get(
                                        "prior_dispatch_surface_blockers"
                                    )
                                ).get("pmo_dispatch_blocker_packet", "")
                            )
                        ),
                        "resolved_by_noop_recovery": as_mapping(
                            b1["no_goal_odom_tf_rviz_preflight_032"].get("prior_dispatch_surface_blockers")
                        ).get("resolved_by_noop_recovery"),
                        "target_thread_id": as_mapping(
                            b1["no_goal_odom_tf_rviz_preflight_032"].get("prior_dispatch_surface_blockers")
                        ).get("target_thread_id", ""),
                    },
                    "observed": as_mapping(b1["no_goal_odom_tf_rviz_preflight_032"].get("observed")),
                    "blocking_gates": as_list(b1["no_goal_odom_tf_rviz_preflight_032"].get("blocking_gates")),
                    "rviz2_cli_available": b1["no_goal_odom_tf_rviz_preflight_032"].get("rviz2_cli_available"),
                    "rviz_gui_opened": b1["no_goal_odom_tf_rviz_preflight_032"].get("rviz_gui_opened"),
                    "truth_to_fastlio_bridge_observed": b1["no_goal_odom_tf_rviz_preflight_032"].get(
                        "truth_to_fastlio_bridge_observed"
                    ),
                },
                "next": str(b1["no_goal_odom_tf_rviz_preflight_032"].get("next", "")),
            },
            "ue_runtime_command_ack": {
                "status": str(ue.get("command_sender_source_status", "")),
                "source": "UE_SENSOR_ORACLE",
                "blocking": ue.get("not_runtime_ue_console") is True,
                "evidence": packet_state(str(ue.get("command_sender_contract", ""))),
                "next": "Wire UE command sender to live MWORKS/ROS2 ack before accepting runtime Experiment Console.",
            },
            "ue_live_echo_acceptance_fixture": {
                "status": str(ue_live_echo_acceptance_fixture.get("status", "not_integrated")),
                "quality_status": str(ue_live_echo_acceptance_fixture.get("quality_status", "not_integrated")),
                "source": "UE_SOURCE_STATIC_CONTRACT",
                "blocking": True,
                "evidence": packet_state(str(ue_live_echo_acceptance_fixture.get("return_packet", ""))),
                "details": {
                    "input_schema": ue_live_echo_acceptance_fixture.get("input_schema", ""),
                    "valid_future_live_accepted_rows": ue_live_echo_acceptance_fixture.get(
                        "valid_future_live_accepted_rows"
                    ),
                    "non_live_runtime_leaks": ue_live_echo_acceptance_fixture.get("non_live_runtime_leaks"),
                    "malformed_runtime_leaks": ue_live_echo_acceptance_fixture.get("malformed_runtime_leaks"),
                    "rejected_runtime_leaks": ue_live_echo_acceptance_fixture.get("rejected_runtime_leaks"),
                    "runtime_receiver_implemented": ue_live_echo_acceptance_fixture.get(
                        "runtime_receiver_implemented"
                    ),
                    "ui_asset_binding_implemented": ue_live_echo_acceptance_fixture.get(
                        "ui_asset_binding_implemented"
                    ),
                },
                "next": "Implement live receiver/UI accepted-state only after a separately scoped MWORKS/ROS2 live command-echo transport exists.",
            },
            "sunray150_material_review": {
                "status": str(sunray150_material_review.get("status", "not_integrated")),
                "quality_status": str(sunray150_material_review.get("quality_status", "not_integrated")),
                "source": "SUNRAY150_ASSET_REVIEW_PACKAGE",
                "blocking": True,
                "evidence": packet_state(str(sunray150_material_review.get("return_packet", ""))),
                "details": {
                    "manual_review_required": sunray150_material_review.get("manual_review_required"),
                    "manual_review_status": sunray150_material_review.get("manual_review_status", ""),
                    "source_manifest_all_outputs_have_project_relative_path": sunray150_material_review.get(
                        "source_manifest_all_outputs_have_project_relative_path"
                    ),
                    "source_manifest_legacy_absolute_path_field_count": sunray150_material_review.get(
                        "source_manifest_legacy_absolute_path_field_count"
                    ),
                    "legacy_absolute_fields_status": sunray150_material_review.get(
                        "legacy_absolute_fields_status", ""
                    ),
                    "battery_present": as_mapping(sunray150_material_review.get("battery_guard_readability")).get(
                        "battery_present"
                    ),
                    "battery_non_flat": as_mapping(
                        sunray150_material_review.get("battery_guard_readability")
                    ).get("battery_non_flat"),
                    "guard_landing_gear_present": as_mapping(
                        sunray150_material_review.get("battery_guard_readability")
                    ).get("guard_landing_gear_present"),
                    "guard_landing_gear_non_flat": as_mapping(
                        sunray150_material_review.get("battery_guard_readability")
                    ).get("guard_landing_gear_non_flat"),
                },
                "next": "Wait for human component material pass/fail review before any final material or UE import/export acceptance.",
            },
        },
        "anti_regression_checks": {
            "claim_scope_excludes_planner": "planner" not in " ".join(claim_scope),
            "claim_scope_excludes_closed_loop": "closed_loop" not in " ".join(claim_scope),
            "planner_global_truth_used_as_input": planner.get("global_truth_used_as_input"),
            "ue_not_runtime_console": ue.get("not_runtime_ue_console"),
            "active_blocker_count": len(blockers),
        },
        "next_packets_to_consume": [],
    }

    if "planner" in " ".join(claim_scope) or "closed_loop" in " ".join(claim_scope):
        matrix["closed_loop_ready"] = False
        matrix["planner_ready"] = False

    return matrix


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json",
    )
    parser.add_argument(
        "--audit",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json",
    )
    parser.add_argument(
        "--output-json",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json",
    )
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    audit_path = repo_path(args.audit)
    output_path = repo_path(args.output_json)
    matrix = build_gap_matrix(read_json(manifest_path), read_json(audit_path), manifest_path, audit_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": rel(output_path),
                "closed_loop_ready": matrix["closed_loop_ready"],
                "planner_ready": matrix["planner_ready"],
                "quality_status": matrix["quality_status"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
