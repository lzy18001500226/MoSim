#!/usr/bin/env python3
"""Build an honest smoke-only RUN_MANIFEST for the current P0 slice evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_run_manifest.py"


def project_path(value: str | Path) -> Path:
    raw = Path(value)
    candidate = raw if raw.is_absolute() else ROOT / raw
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    gate = read_json(project_path(args.realstack_gate))
    metrics = read_json(project_path(args.mworks_metrics))
    adapter = read_json(project_path(args.adapter_smoke))
    position_adapter = read_json(project_path(args.position_adapter_smoke)) if args.position_adapter_smoke else {}
    b0_summary_path = project_path(args.positioncmd_b0_run_summary)
    b0_summary = read_json(b0_summary_path) if b0_summary_path.exists() else {}
    b0_artifacts = b0_summary.get("artifacts", {}) if isinstance(b0_summary.get("artifacts"), dict) else {}
    b0_topic_rates_path = project_path(b0_artifacts["topic_rates"]) if b0_artifacts.get("topic_rates") else None
    b0_planner_input_gate_path = (
        project_path(b0_artifacts["planner_input_gate"]) if b0_artifacts.get("planner_input_gate") else None
    )
    b0_topic_rates = read_json(b0_topic_rates_path) if b0_topic_rates_path and b0_topic_rates_path.exists() else {}
    b0_planner_input_gate = (
        read_json(b0_planner_input_gate_path)
        if b0_planner_input_gate_path and b0_planner_input_gate_path.exists()
        else {}
    )
    b1_blocker_path = project_path(args.positioncmd_b1_blocker)
    b1_blocker = read_json(b1_blocker_path) if b1_blocker_path.exists() else {}
    b1_blockers = b1_blocker.get("blockers", []) if isinstance(b1_blocker.get("blockers"), list) else []
    b1_unblock_blocker_path = project_path(args.positioncmd_b1_unblock_blocker)
    b1_unblock_blocker = read_json(b1_unblock_blocker_path) if b1_unblock_blocker_path.exists() else {}
    b1_planner_wrapper_blocker_path = project_path(args.positioncmd_b1_planner_wrapper_blocker)
    b1_planner_wrapper_blocker = (
        read_json(b1_planner_wrapper_blocker_path) if b1_planner_wrapper_blocker_path.exists() else {}
    )
    b1_port_preflight_return_path = project_path(args.positioncmd_b1_port_preflight_return)
    b1_port_preflight_return = (
        read_json(b1_port_preflight_return_path) if b1_port_preflight_return_path.exists() else {}
    )
    b1_msg_port_slice_return_path = project_path(args.positioncmd_b1_msg_port_slice_return)
    b1_msg_port_slice_return = (
        read_json(b1_msg_port_slice_return_path) if b1_msg_port_slice_return_path.exists() else {}
    )
    b1_planner_node_port_return_path = project_path(args.positioncmd_b1_planner_node_port_return)
    b1_planner_node_port_return = (
        read_json(b1_planner_node_port_return_path) if b1_planner_node_port_return_path.exists() else {}
    )
    b1_upstream_planner_deps_blocker_path = project_path(args.positioncmd_b1_upstream_planner_deps_blocker)
    b1_upstream_planner_deps_blocker = (
        read_json(b1_upstream_planner_deps_blocker_path)
        if b1_upstream_planner_deps_blocker_path.exists()
        else {}
    )
    b1_planenv_gridmap_port_return_path = project_path(args.positioncmd_b1_planenv_gridmap_port_return)
    b1_planenv_gridmap_port_return = (
        read_json(b1_planenv_gridmap_port_return_path) if b1_planenv_gridmap_port_return_path.exists() else {}
    )
    b1_path_bspline_port_return_path = project_path(args.positioncmd_b1_path_bspline_port_return)
    b1_path_bspline_port_return = (
        read_json(b1_path_bspline_port_return_path) if b1_path_bspline_port_return_path.exists() else {}
    )
    b1_traj_quadmsgs_port_return_path = project_path(args.positioncmd_b1_traj_quadmsgs_port_return)
    b1_traj_quadmsgs_port_return = (
        read_json(b1_traj_quadmsgs_port_return_path) if b1_traj_quadmsgs_port_return_path.exists() else {}
    )
    b1_planmanage_link_preflight_return_path = project_path(args.positioncmd_b1_planmanage_link_preflight_return)
    b1_planmanage_link_preflight_return = (
        read_json(b1_planmanage_link_preflight_return_path)
        if b1_planmanage_link_preflight_return_path.exists()
        else {}
    )
    b1_runtime_disabled_launch_audit_return_path = project_path(args.positioncmd_b1_runtime_disabled_launch_audit_return)
    b1_runtime_disabled_launch_audit_return = (
        read_json(b1_runtime_disabled_launch_audit_return_path)
        if b1_runtime_disabled_launch_audit_return_path.exists()
        else {}
    )
    b1_runtime_disabled_launch_config_return_path = project_path(args.positioncmd_b1_runtime_disabled_launch_config_return)
    b1_runtime_disabled_launch_config_return = (
        read_json(b1_runtime_disabled_launch_config_return_path)
        if b1_runtime_disabled_launch_config_return_path.exists()
        else {}
    )
    b1_runtime_disabled_smoke_return_path = project_path(args.positioncmd_b1_runtime_disabled_smoke_return)
    b1_runtime_disabled_smoke_return = (
        read_json(b1_runtime_disabled_smoke_return_path) if b1_runtime_disabled_smoke_return_path.exists() else {}
    )
    b1_real_planner_input_gate_blocker_path = project_path(args.positioncmd_b1_real_planner_input_gate_blocker)
    b1_real_planner_input_gate_blocker = (
        read_json(b1_real_planner_input_gate_blocker_path)
        if b1_real_planner_input_gate_blocker_path.exists()
        else {}
    )
    b1_odom_cloud_restore_return_path = project_path(args.positioncmd_b1_odom_cloud_restore_return)
    b1_odom_cloud_restore_return = (
        read_json(b1_odom_cloud_restore_return_path) if b1_odom_cloud_restore_return_path.exists() else {}
    )
    b1_planner_startup_probe_blocker_path = project_path(args.positioncmd_b1_planner_startup_probe_blocker)
    b1_planner_startup_probe_blocker = (
        read_json(b1_planner_startup_probe_blocker_path)
        if b1_planner_startup_probe_blocker_path.exists()
        else {}
    )
    b1_odom_cloud_summary_path = None
    b1_odom_cloud_summary = {}
    b1_odom_cloud_evidence = as_mapping(b1_odom_cloud_restore_return.get("odometry_and_cloud_evidence"))
    if b1_odom_cloud_evidence.get("summary"):
        b1_odom_cloud_summary_path = project_path(str(b1_odom_cloud_evidence.get("summary")))
        if b1_odom_cloud_summary_path.exists():
            b1_odom_cloud_summary = read_json(b1_odom_cloud_summary_path)
    mworks_trace_blocker_path = project_path(args.mworks_trace_blocker)
    mworks_trace_blocker = read_json(mworks_trace_blocker_path) if mworks_trace_blocker_path.exists() else {}
    mworks_trace_lookup_return_path = project_path(args.mworks_trace_lookup_return)
    mworks_trace_lookup_return = (
        read_json(mworks_trace_lookup_return_path) if mworks_trace_lookup_return_path.exists() else {}
    )
    mworks_factory_trace_reconnect_blocker_path = project_path(args.mworks_factory_trace_reconnect_blocker)
    mworks_factory_trace_reconnect_blocker = (
        read_json(mworks_factory_trace_reconnect_blocker_path)
        if mworks_factory_trace_reconnect_blocker_path.exists()
        else {}
    )
    mworks_factory_lite_trace_return_path = project_path(args.mworks_factory_lite_trace_return)
    mworks_factory_lite_trace_return = (
        read_json(mworks_factory_lite_trace_return_path) if mworks_factory_lite_trace_return_path.exists() else {}
    )
    mworks_incremental_trace_isolation_return_path = project_path(args.mworks_incremental_trace_isolation_return)
    mworks_incremental_trace_isolation_return = (
        read_json(mworks_incremental_trace_isolation_return_path)
        if mworks_incremental_trace_isolation_return_path.exists()
        else {}
    )
    mworks_actuator_wiring_isolation_return_path = project_path(args.mworks_actuator_wiring_isolation_return)
    mworks_actuator_wiring_isolation_return = (
        read_json(mworks_actuator_wiring_isolation_return_path)
        if mworks_actuator_wiring_isolation_return_path.exists()
        else {}
    )
    mworks_sensor_feedback_isolation_return_path = project_path(args.mworks_sensor_feedback_isolation_return)
    mworks_sensor_feedback_isolation_return = (
        read_json(mworks_sensor_feedback_isolation_return_path)
        if mworks_sensor_feedback_isolation_return_path.exists()
        else {}
    )
    mworks_attitude_feedback_isolation_return_path = project_path(args.mworks_attitude_feedback_isolation_return)
    mworks_attitude_feedback_isolation_return = (
        read_json(mworks_attitude_feedback_isolation_return_path)
        if mworks_attitude_feedback_isolation_return_path.exists()
        else {}
    )
    mworks_attitude_intermediary_return_path = project_path(args.mworks_attitude_intermediary_return)
    mworks_attitude_intermediary_return = (
        read_json(mworks_attitude_intermediary_return_path)
        if mworks_attitude_intermediary_return_path.exists()
        else {}
    )
    mworks_attitude_decoupling_return_path = project_path(args.mworks_attitude_decoupling_return)
    mworks_attitude_decoupling_return = (
        read_json(mworks_attitude_decoupling_return_path)
        if mworks_attitude_decoupling_return_path.exists()
        else {}
    )
    mworks_pitch_decoupling_return_path = project_path(args.mworks_pitch_decoupling_return)
    mworks_pitch_decoupling_return = (
        read_json(mworks_pitch_decoupling_return_path) if mworks_pitch_decoupling_return_path.exists() else {}
    )
    mworks_yaw_rate_decoupling_return_path = project_path(args.mworks_yaw_rate_decoupling_return)
    mworks_yaw_rate_decoupling_return = (
        read_json(mworks_yaw_rate_decoupling_return_path)
        if mworks_yaw_rate_decoupling_return_path.exists()
        else {}
    )
    mworks_rate_feedback_isolation_return_path = project_path(args.mworks_rate_feedback_isolation_return)
    mworks_rate_feedback_isolation_return = (
        read_json(mworks_rate_feedback_isolation_return_path)
        if mworks_rate_feedback_isolation_return_path.exists()
        else {}
    )
    mworks_sensor_bus_reconnect_blocker_path = project_path(args.mworks_sensor_bus_reconnect_blocker)
    mworks_sensor_bus_reconnect_blocker = (
        read_json(mworks_sensor_bus_reconnect_blocker_path)
        if mworks_sensor_bus_reconnect_blocker_path.exists()
        else {}
    )
    mworks_position_bridge_return_path = project_path(args.mworks_position_bridge_return)
    mworks_position_bridge_return = (
        read_json(mworks_position_bridge_return_path) if mworks_position_bridge_return_path.exists() else {}
    )
    mworks_next_sensor_display_group_blocker_path = project_path(args.mworks_next_sensor_display_group_blocker)
    mworks_next_sensor_display_group_blocker = (
        read_json(mworks_next_sensor_display_group_blocker_path)
        if mworks_next_sensor_display_group_blocker_path.exists()
        else {}
    )
    mworks_first_control_feedback_group_blocker_path = project_path(args.mworks_first_control_feedback_group_blocker)
    mworks_first_control_feedback_group_blocker = (
        read_json(mworks_first_control_feedback_group_blocker_path)
        if mworks_first_control_feedback_group_blocker_path.exists()
        else {}
    )
    mworks_attitude_feedback_bridge_return_path = project_path(args.mworks_attitude_feedback_bridge_return)
    mworks_attitude_feedback_bridge_return = (
        read_json(mworks_attitude_feedback_bridge_return_path)
        if mworks_attitude_feedback_bridge_return_path.exists()
        else {}
    )

    gate_paths = gate.get("paths", {})
    fast_lio = gate.get("fastlio_runtime_evaluation", {})
    fast_lio_metrics = fast_lio.get("metrics", {})

    if b0_artifacts.get("setpoint_trace_csv"):
        setpoint_trace_path = project_path(b0_artifacts["setpoint_trace_csv"])
    else:
        setpoint_trace_path = project_path(args.setpoint_trace)

    if not setpoint_trace_path.exists():
        setpoint_trace_path.parent.mkdir(parents=True, exist_ok=True)
        setpoint_trace_path.write_text(
            "time,sequence,frame_id,planner_id,x_ref,y_ref,z_ref,yaw_ref\n"
            "0,1,map,smoke,0,0,1.2,0\n",
            encoding="utf-8",
        )

    manifest = {
        "schema_version": "mosim.run_manifest.v1",
        "run_id": args.run_id,
        "objective": (
            "P0 slice manifest linking existing MWORKS smoke, Factory FAST-LIO Gate B, "
            "and ROS2 setpoint adapter smoke without claiming full planner/MWORKS closed loop."
        ),
        "scene_id": "factoryenvironmentcollect",
        "map_id": "factoryenvironmentcollect",
        "vehicle_id": "sunray150",
        "controller_id": str(metrics.get("controller_id", "linear_mpc_sysblock")),
        "planner_id": "smoke_adapter_only",
        "quality_status": "smoke_only",
        "evidence_level": "p0_slice_smoke_manifest",
        "claim_scope": ["fast_lio", "ue_visual"],
        "blockers": [
            "No real local 3D map planner output is bound to /mosim/planner/position_cmd yet.",
            "No same-run MWORKS/controller simulation has consumed the ROS2 adapter setpoint trace.",
            "UE Experiment Console command adapter smoke is offline-only for this slice.",
            "This manifest links existing slice evidence; it is not a full P0 closed-loop run.",
            "B1 real planner/runtime source is blocked: baseline live ROS2 graph lacks real PositionCommand/planner topics; Gate B restore can regenerate FAST-LIO odom/cloud/path, but no planner consumes them yet.",
            "B1 real planner input gate 018 is historical blocker evidence; task 019 restored /Odometry and /cloud_registered as a later startup precondition, but no planner has consumed them yet.",
            "B1 runtime_disabled=false planner startup remains blocked until a separate PMO-approved probe freshly restores odom/cloud and starts only the guarded planner surface.",
            "B1 planner startup probe 020 is blocked: fresh restore succeeded, but runtime_disabled=false planner startup did not demonstrate /Odometry or /cloud_registered input consumption.",
            "MWORKS trace consumption is blocked: the project-owned trace wrapper checks, but Sysplorer simulation/result binding did not produce usable nonzero trace outputs.",
            "MWORKS sensor/display reconnect is blocked: direct sensors1_1.PosMea -> navigationDisplay.actual_position reconnect passes check_model but fails simulation with error 6140 and empty result context.",
            "MWORKS sensor/display scope is exhausted after Iso23; remaining Factory trace differences require a new controller/control-feedback reconnect task boundary.",
            "MWORKS direct AngleMea controller feedback remains a historical blocker; task 019 restored result context only for one sampled/held attitude-feedback bridge, while downstream control-output/actuator groups and full Factory trace consumption remain unproven.",
        ],
        "sources": {
            "mworks_source": "MWORKS_MCP",
            "ros2_source": "ROS2_REALSTACK",
            "ue_source": "UE_SENSOR_ORACLE",
            "planner_input_source": "LOCAL_SENSED_MAP",
            "replay_source": "MWORKS_MCP",
        },
        "mworks": {
            "model_name": "sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke",
            "check_model_status": "pass",
            "simulate_status": "smoke_only",
            "raw_csv": gate_paths.get("mworks_raw_csv", metrics.get("raw_file", "")),
            "metrics_json": rel(project_path(args.mworks_metrics)),
            "setpoint_trace_consumption_status": "blocked" if mworks_trace_blocker else "not_run",
            "consumed_setpoint_trace": "",
            "trace_consumption_evidence": "",
            "trace_consumption_blocker": rel(mworks_trace_blocker_path) if mworks_trace_blocker else "",
            "trace_consumption_summary": mworks_trace_blocker.get("summary", "") if mworks_trace_blocker else "",
            "trace_consumption_input_trace": (
                mworks_trace_blocker.get("input_trace", {}).get("path", "")
                if isinstance(mworks_trace_blocker.get("input_trace"), dict)
                else ""
            ),
            "trace_lookup_diagnostic": {
                "status": str(mworks_trace_lookup_return.get("status", "not_run"))
                if mworks_trace_lookup_return
                else "not_run",
                "quality_status": (
                    mworks_trace_lookup_return.get("validation", {}).get("quality_status", "")
                    if isinstance(mworks_trace_lookup_return.get("validation"), dict)
                    else ""
                ),
                "return_packet": rel(mworks_trace_lookup_return_path) if mworks_trace_lookup_return else "",
                "model_name": (
                    mworks_trace_lookup_return.get("model", {}).get("name", "")
                    if isinstance(mworks_trace_lookup_return.get("model"), dict)
                    else ""
                ),
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_trace_lookup_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_trace_lookup_return.get("artifact_refs"), list)
                else "",
                "raw_reference_series_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_trace_lookup_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "raw_reference_series_csv"
                    ),
                    "",
                )
                if isinstance(mworks_trace_lookup_return.get("artifact_refs"), list)
                else "",
                "nonzero_reference_outputs": bool(
                    mworks_trace_lookup_return.get("mcp_execution", {})
                    .get("result_binding", {})
                    .get("nonzero_reference_outputs", False)
                )
                if isinstance(mworks_trace_lookup_return.get("mcp_execution"), dict)
                else False,
                "tolerance_pass": bool(
                    mworks_trace_lookup_return.get("validation", {}).get("tolerance_pass", False)
                    if isinstance(mworks_trace_lookup_return.get("validation"), dict)
                    else False
                ),
                "claim_boundary": [
                    "Standalone trace lookup proves trace source/result binding only.",
                    "Factory wrapper/controller trace consumption remains blocked until the same trace is nonzero in the wrapper context.",
                ],
            },
            "factory_trace_reconnect": {
                "status": str(mworks_factory_trace_reconnect_blocker.get("status", "not_run"))
                if mworks_factory_trace_reconnect_blocker
                else "not_run",
                "blocker_packet": rel(mworks_factory_trace_reconnect_blocker_path)
                if mworks_factory_trace_reconnect_blocker
                else "",
                "blocker_kind": mworks_factory_trace_reconnect_blocker.get("blocker_kind", "")
                if mworks_factory_trace_reconnect_blocker
                else "",
                "summary": mworks_factory_trace_reconnect_blocker.get("summary", "")
                if mworks_factory_trace_reconnect_blocker
                else "",
                "model_name": (
                    mworks_factory_trace_reconnect_blocker.get("model", {}).get("name", "")
                    if isinstance(mworks_factory_trace_reconnect_blocker.get("model"), dict)
                    else ""
                ),
                "check_model_status": (
                    mworks_factory_trace_reconnect_blocker.get("mcp_execution", {})
                    .get("check_model", {})
                    .get("status", "")
                )
                if isinstance(mworks_factory_trace_reconnect_blocker.get("mcp_execution"), dict)
                else "",
                "simulate_status": (
                    mworks_factory_trace_reconnect_blocker.get("mcp_execution", {})
                    .get("simulate_model", {})
                    .get("status", "")
                )
                if isinstance(mworks_factory_trace_reconnect_blocker.get("mcp_execution"), dict)
                else "",
                "get_var_times_count": (
                    mworks_factory_trace_reconnect_blocker.get("mcp_execution", {})
                    .get("result_binding", {})
                    .get("get_var_times_count")
                )
                if isinstance(mworks_factory_trace_reconnect_blocker.get("mcp_execution"), dict)
                else None,
                "nonzero_alias_refs": bool(
                    mworks_factory_trace_reconnect_blocker.get("mcp_execution", {})
                    .get("result_binding", {})
                    .get("nonzero_alias_refs", False)
                )
                if isinstance(mworks_factory_trace_reconnect_blocker.get("mcp_execution"), dict)
                else False,
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_factory_trace_reconnect_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_factory_trace_reconnect_blocker.get("artifact_refs"), list)
                else "",
                "next_minimal_probe": mworks_factory_trace_reconnect_blocker.get("next_minimal_probe", "")
                if mworks_factory_trace_reconnect_blocker
                else "",
                "claim_boundary": mworks_factory_trace_reconnect_blocker.get("claim_boundary", [])
                if isinstance(mworks_factory_trace_reconnect_blocker.get("claim_boundary"), list)
                else [
                    "No MWORKS Factory trace consumption evidence is claimed.",
                    "B0 trace remains smoke-only and not real planner/closed_loop evidence.",
                ],
            },
            "factory_lite_trace_probe": {
                "status": str(mworks_factory_lite_trace_return.get("status", "not_run"))
                if mworks_factory_lite_trace_return
                else "not_run",
                "quality_status": mworks_factory_lite_trace_return.get("quality_status", "")
                if mworks_factory_lite_trace_return
                else "",
                "return_packet": rel(mworks_factory_lite_trace_return_path) if mworks_factory_lite_trace_return else "",
                "completion_scope": mworks_factory_lite_trace_return.get("completion_scope", "")
                if mworks_factory_lite_trace_return
                else "",
                "model_name": (
                    mworks_factory_lite_trace_return.get("model", {}).get("name", "")
                    if isinstance(mworks_factory_lite_trace_return.get("model"), dict)
                    else ""
                ),
                "check_model_status": (
                    mworks_factory_lite_trace_return.get("mcp_execution", {})
                    .get("check_model", {})
                    .get("status", "")
                )
                if isinstance(mworks_factory_lite_trace_return.get("mcp_execution"), dict)
                else "",
                "simulate_status": (
                    mworks_factory_lite_trace_return.get("mcp_execution", {})
                    .get("simulate_model", {})
                    .get("status", "")
                )
                if isinstance(mworks_factory_lite_trace_return.get("mcp_execution"), dict)
                else "",
                "get_var_times_count": (
                    mworks_factory_lite_trace_return.get("mcp_execution", {})
                    .get("result_binding", {})
                    .get("get_var_times_count")
                )
                if isinstance(mworks_factory_lite_trace_return.get("mcp_execution"), dict)
                else None,
                "nonzero_alias_refs": bool(
                    mworks_factory_lite_trace_return.get("mcp_execution", {})
                    .get("result_binding", {})
                    .get("nonzero_alias_refs", False)
                )
                if isinstance(mworks_factory_lite_trace_return.get("mcp_execution"), dict)
                else False,
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_factory_lite_trace_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_factory_lite_trace_return.get("artifact_refs"), list)
                else "",
                "raw_alias_series_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_factory_lite_trace_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "raw_alias_series_csv"
                    ),
                    "",
                )
                if isinstance(mworks_factory_lite_trace_return.get("artifact_refs"), list)
                else "",
                "diagnosis": mworks_factory_lite_trace_return.get("diagnosis", {})
                if isinstance(mworks_factory_lite_trace_return.get("diagnosis"), dict)
                else {},
                "not_claimed": mworks_factory_lite_trace_return.get("not_claimed", [])
                if isinstance(mworks_factory_lite_trace_return.get("not_claimed"), list)
                else [],
                "claim_boundary": mworks_factory_lite_trace_return.get("claim_boundary", [])
                if isinstance(mworks_factory_lite_trace_return.get("claim_boundary"), list)
                else [
                    "Factory-lite trace result-binding probe only.",
                    "No closed_loop or plant/controller trace-consumption claim.",
                ],
            },
            "incremental_trace_isolation": {
                "status": str(mworks_incremental_trace_isolation_return.get("status", "not_run"))
                if mworks_incremental_trace_isolation_return
                else "not_run",
                "quality_status": mworks_incremental_trace_isolation_return.get("quality_status", "")
                if mworks_incremental_trace_isolation_return
                else "",
                "return_packet": rel(mworks_incremental_trace_isolation_return_path)
                if mworks_incremental_trace_isolation_return
                else "",
                "completion_scope": mworks_incremental_trace_isolation_return.get("completion_scope", "")
                if mworks_incremental_trace_isolation_return
                else "",
                "summary": mworks_incremental_trace_isolation_return.get("summary", "")
                if mworks_incremental_trace_isolation_return
                else "",
                "incremental_probes": mworks_incremental_trace_isolation_return.get("incremental_probes", [])
                if isinstance(mworks_incremental_trace_isolation_return.get("incremental_probes"), list)
                else [],
                "first_failure_boundary": mworks_incremental_trace_isolation_return.get("first_failure_boundary", {})
                if isinstance(mworks_incremental_trace_isolation_return.get("first_failure_boundary"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_incremental_trace_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_incremental_trace_isolation_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_incremental_trace_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_incremental_trace_isolation_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_incremental_trace_isolation_return.get("models_created", [])
                if isinstance(mworks_incremental_trace_isolation_return.get("models_created"), list)
                else [],
                "claim_boundary": mworks_incremental_trace_isolation_return.get("claim_boundary", [])
                if isinstance(mworks_incremental_trace_isolation_return.get("claim_boundary"), list)
                else [
                    "Incremental isolation only.",
                    "No closed_loop, real planner, controller performance, or plant tracking claim.",
                ],
            },
            "actuator_wiring_isolation": {
                "status": str(mworks_actuator_wiring_isolation_return.get("status", "not_run"))
                if mworks_actuator_wiring_isolation_return
                else "not_run",
                "quality_status": mworks_actuator_wiring_isolation_return.get("quality_status", "")
                if mworks_actuator_wiring_isolation_return
                else "",
                "return_packet": rel(mworks_actuator_wiring_isolation_return_path)
                if mworks_actuator_wiring_isolation_return
                else "",
                "completion_scope": mworks_actuator_wiring_isolation_return.get("completion_scope", "")
                if mworks_actuator_wiring_isolation_return
                else "",
                "summary": mworks_actuator_wiring_isolation_return.get("summary", "")
                if mworks_actuator_wiring_isolation_return
                else "",
                "known_passing_topology_reference": mworks_actuator_wiring_isolation_return.get(
                    "known_passing_topology_reference", {}
                )
                if isinstance(mworks_actuator_wiring_isolation_return.get("known_passing_topology_reference"), dict)
                else {},
                "derivative_probes": mworks_actuator_wiring_isolation_return.get("derivative_probes", [])
                if isinstance(mworks_actuator_wiring_isolation_return.get("derivative_probes"), list)
                else [],
                "refined_boundary": mworks_actuator_wiring_isolation_return.get("refined_boundary", {})
                if isinstance(mworks_actuator_wiring_isolation_return.get("refined_boundary"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_actuator_wiring_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_actuator_wiring_isolation_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_actuator_wiring_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_actuator_wiring_isolation_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_actuator_wiring_isolation_return.get("models_created", [])
                if isinstance(mworks_actuator_wiring_isolation_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_actuator_wiring_isolation_return.get(
                    "forbidden_edits_avoided", []
                )
                if isinstance(mworks_actuator_wiring_isolation_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_actuator_wiring_isolation_return.get("recommended_next_step", "")
                if mworks_actuator_wiring_isolation_return
                else "",
                "claim_boundary": mworks_actuator_wiring_isolation_return.get("claim_boundary", [])
                if isinstance(mworks_actuator_wiring_isolation_return.get("claim_boundary"), list)
                else [
                    "Actuator wiring isolation only.",
                    "No closed_loop, real planner, controller performance, or plant tracking claim.",
                ],
            },
            "sensor_feedback_isolation": {
                "status": str(mworks_sensor_feedback_isolation_return.get("status", "not_run"))
                if mworks_sensor_feedback_isolation_return
                else "not_run",
                "quality_status": mworks_sensor_feedback_isolation_return.get("quality_status", "")
                if mworks_sensor_feedback_isolation_return
                else "",
                "return_packet": rel(mworks_sensor_feedback_isolation_return_path)
                if mworks_sensor_feedback_isolation_return
                else "",
                "completion_scope": mworks_sensor_feedback_isolation_return.get("completion_scope", "")
                if mworks_sensor_feedback_isolation_return
                else "",
                "summary": mworks_sensor_feedback_isolation_return.get("summary", "")
                if mworks_sensor_feedback_isolation_return
                else "",
                "feedback_probes": mworks_sensor_feedback_isolation_return.get("feedback_probes", [])
                if isinstance(mworks_sensor_feedback_isolation_return.get("feedback_probes"), list)
                else [],
                "first_failure_boundary": mworks_sensor_feedback_isolation_return.get("first_failure_boundary", {})
                if isinstance(mworks_sensor_feedback_isolation_return.get("first_failure_boundary"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_sensor_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_sensor_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_sensor_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_sensor_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_sensor_feedback_isolation_return.get("models_created", [])
                if isinstance(mworks_sensor_feedback_isolation_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_sensor_feedback_isolation_return.get(
                    "forbidden_edits_avoided", []
                )
                if isinstance(mworks_sensor_feedback_isolation_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_sensor_feedback_isolation_return.get("recommended_next_step", "")
                if mworks_sensor_feedback_isolation_return
                else "",
                "claim_boundary": mworks_sensor_feedback_isolation_return.get("claim_boundary", [])
                if isinstance(mworks_sensor_feedback_isolation_return.get("claim_boundary"), list)
                else [
                    "Sensor feedback isolation only.",
                    "No closed_loop, real planner, controller performance, or plant tracking claim.",
                ],
            },
            "attitude_feedback_isolation": {
                "status": str(mworks_attitude_feedback_isolation_return.get("status", "not_run"))
                if mworks_attitude_feedback_isolation_return
                else "not_run",
                "quality_status": mworks_attitude_feedback_isolation_return.get("quality_status", "")
                if mworks_attitude_feedback_isolation_return
                else "",
                "return_packet": rel(mworks_attitude_feedback_isolation_return_path)
                if mworks_attitude_feedback_isolation_return
                else "",
                "completion_scope": mworks_attitude_feedback_isolation_return.get("completion_scope", "")
                if mworks_attitude_feedback_isolation_return
                else "",
                "summary": mworks_attitude_feedback_isolation_return.get("summary", "")
                if mworks_attitude_feedback_isolation_return
                else "",
                "interface_findings": mworks_attitude_feedback_isolation_return.get("interface_findings", {})
                if isinstance(mworks_attitude_feedback_isolation_return.get("interface_findings"), dict)
                else {},
                "attitude_feedback_probes": mworks_attitude_feedback_isolation_return.get(
                    "attitude_feedback_probes", []
                )
                if isinstance(mworks_attitude_feedback_isolation_return.get("attitude_feedback_probes"), list)
                else [],
                "first_failure_boundary": mworks_attitude_feedback_isolation_return.get(
                    "first_failure_boundary", {}
                )
                if isinstance(mworks_attitude_feedback_isolation_return.get("first_failure_boundary"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_attitude_feedback_isolation_return.get("models_created", [])
                if isinstance(mworks_attitude_feedback_isolation_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_attitude_feedback_isolation_return.get(
                    "forbidden_edits_avoided", []
                )
                if isinstance(mworks_attitude_feedback_isolation_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_attitude_feedback_isolation_return.get(
                    "recommended_next_step", ""
                )
                if mworks_attitude_feedback_isolation_return
                else "",
                "claim_boundary": mworks_attitude_feedback_isolation_return.get("claim_boundary", [])
                if isinstance(mworks_attitude_feedback_isolation_return.get("claim_boundary"), list)
                else [
                    "Attitude feedback isolation only.",
                    "No closed_loop, real planner, controller performance, or plant tracking claim.",
                ],
            },
            "attitude_intermediary_classification": {
                "status": str(mworks_attitude_intermediary_return.get("status", "not_run"))
                if mworks_attitude_intermediary_return
                else "not_run",
                "quality_status": mworks_attitude_intermediary_return.get("quality_status", "")
                if mworks_attitude_intermediary_return
                else "",
                "return_packet": rel(mworks_attitude_intermediary_return_path)
                if mworks_attitude_intermediary_return
                else "",
                "completion_scope": mworks_attitude_intermediary_return.get("completion_scope", "")
                if mworks_attitude_intermediary_return
                else "",
                "summary": mworks_attitude_intermediary_return.get("summary", "")
                if mworks_attitude_intermediary_return
                else "",
                "intermediary_probes": mworks_attitude_intermediary_return.get("intermediary_probes", [])
                if isinstance(mworks_attitude_intermediary_return.get("intermediary_probes"), list)
                else [],
                "classification": mworks_attitude_intermediary_return.get("classification", {})
                if isinstance(mworks_attitude_intermediary_return.get("classification"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_intermediary_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_intermediary_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_intermediary_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_intermediary_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_intermediary_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_intermediary_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_attitude_intermediary_return.get("models_created", [])
                if isinstance(mworks_attitude_intermediary_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_attitude_intermediary_return.get(
                    "forbidden_edits_avoided", []
                )
                if isinstance(mworks_attitude_intermediary_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_attitude_intermediary_return.get(
                    "recommended_next_step", ""
                )
                if mworks_attitude_intermediary_return
                else "",
                "claim_boundary": mworks_attitude_intermediary_return.get("claim_boundary", [])
                if isinstance(mworks_attitude_intermediary_return.get("claim_boundary"), list)
                else [
                    "Attitude intermediary classification only.",
                    "No closed_loop, Factory trace consumption, controller performance, or plant tracking claim.",
                ],
            },
            "attitude_decoupling_probe": {
                "status": str(mworks_attitude_decoupling_return.get("status", "not_run"))
                if mworks_attitude_decoupling_return
                else "not_run",
                "quality_status": mworks_attitude_decoupling_return.get("quality_status", "")
                if mworks_attitude_decoupling_return
                else "",
                "return_packet": rel(mworks_attitude_decoupling_return_path)
                if mworks_attitude_decoupling_return
                else "",
                "completion_scope": mworks_attitude_decoupling_return.get("completion_scope", "")
                if mworks_attitude_decoupling_return
                else "",
                "summary": mworks_attitude_decoupling_return.get("summary", "")
                if mworks_attitude_decoupling_return
                else "",
                "decoupling_probes": mworks_attitude_decoupling_return.get("decoupling_probes", [])
                if isinstance(mworks_attitude_decoupling_return.get("decoupling_probes"), list)
                else [],
                "classification": mworks_attitude_decoupling_return.get("classification", {})
                if isinstance(mworks_attitude_decoupling_return.get("classification"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_decoupling_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_decoupling_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_decoupling_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_attitude_decoupling_return.get("models_created", [])
                if isinstance(mworks_attitude_decoupling_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_attitude_decoupling_return.get(
                    "forbidden_edits_avoided", []
                )
                if isinstance(mworks_attitude_decoupling_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_attitude_decoupling_return.get(
                    "recommended_next_step", ""
                )
                if mworks_attitude_decoupling_return
                else "",
                "claim_boundary": mworks_attitude_decoupling_return.get("claim_boundary", [])
                if isinstance(mworks_attitude_decoupling_return.get("claim_boundary"), list)
                else [
                    "Attitude decoupling/result-context probe only.",
                    "No closed_loop, Factory trace consumption, controller performance, plant tracking, or parameter identification claim.",
                ],
            },
            "pitch_decoupling_probe": {
                "status": str(mworks_pitch_decoupling_return.get("status", "not_run"))
                if mworks_pitch_decoupling_return
                else "not_run",
                "quality_status": mworks_pitch_decoupling_return.get("quality_status", "")
                if mworks_pitch_decoupling_return
                else "",
                "return_packet": rel(mworks_pitch_decoupling_return_path) if mworks_pitch_decoupling_return else "",
                "completion_scope": mworks_pitch_decoupling_return.get("completion_scope", "")
                if mworks_pitch_decoupling_return
                else "",
                "summary": mworks_pitch_decoupling_return.get("summary", "")
                if mworks_pitch_decoupling_return
                else "",
                "pitch_decoupling_probes": mworks_pitch_decoupling_return.get("pitch_decoupling_probes", [])
                if isinstance(mworks_pitch_decoupling_return.get("pitch_decoupling_probes"), list)
                else [],
                "classification": mworks_pitch_decoupling_return.get("classification", {})
                if isinstance(mworks_pitch_decoupling_return.get("classification"), dict)
                else {},
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_pitch_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_pitch_decoupling_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_pitch_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_pitch_decoupling_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_pitch_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_pitch_decoupling_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_pitch_decoupling_return.get("models_created", [])
                if isinstance(mworks_pitch_decoupling_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_pitch_decoupling_return.get("forbidden_edits_avoided", [])
                if isinstance(mworks_pitch_decoupling_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_pitch_decoupling_return.get("recommended_next_step", "")
                if mworks_pitch_decoupling_return
                else "",
                "claim_boundary": mworks_pitch_decoupling_return.get("claim_boundary", [])
                if isinstance(mworks_pitch_decoupling_return.get("claim_boundary"), list)
                else [
                    "Pitch decoupling/result-context probe only.",
                    "No closed_loop, Factory trace consumption, controller performance, plant tracking, or parameter identification claim.",
                ],
            },
            "yaw_rate_decoupling_probe": {
                "status": str(mworks_yaw_rate_decoupling_return.get("status", "not_run"))
                if mworks_yaw_rate_decoupling_return
                else "not_run",
                "quality_status": mworks_yaw_rate_decoupling_return.get("quality_status", "")
                if mworks_yaw_rate_decoupling_return
                else "",
                "return_packet": rel(mworks_yaw_rate_decoupling_return_path)
                if mworks_yaw_rate_decoupling_return
                else "",
                "completion_scope": mworks_yaw_rate_decoupling_return.get("completion_scope", "")
                if mworks_yaw_rate_decoupling_return
                else "",
                "summary": mworks_yaw_rate_decoupling_return.get("summary", "")
                if mworks_yaw_rate_decoupling_return
                else "",
                "yaw_rate_probes": mworks_yaw_rate_decoupling_return.get("yaw_rate_probes", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("yaw_rate_probes"), list)
                else [],
                "classification": mworks_yaw_rate_decoupling_return.get("classification", {})
                if isinstance(mworks_yaw_rate_decoupling_return.get("classification"), dict)
                else {},
                "unknowns": mworks_yaw_rate_decoupling_return.get("unknowns", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("unknowns"), list)
                else [],
                "risks": mworks_yaw_rate_decoupling_return.get("risks", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("risks"), list)
                else [],
                "next_validation": mworks_yaw_rate_decoupling_return.get("next_validation", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("next_validation"), list)
                else [],
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_yaw_rate_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_yaw_rate_decoupling_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_yaw_rate_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_yaw_rate_decoupling_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_yaw_rate_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_yaw_rate_decoupling_return.get("artifact_refs"), list)
                else "",
                "unknowns_risks_next_validation": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_yaw_rate_decoupling_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "unknowns_risks_next_validation"
                    ),
                    "",
                )
                if isinstance(mworks_yaw_rate_decoupling_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_yaw_rate_decoupling_return.get("models_created", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_yaw_rate_decoupling_return.get("forbidden_edits_avoided", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_yaw_rate_decoupling_return.get("recommended_next_step", "")
                if mworks_yaw_rate_decoupling_return
                else "",
                "claim_boundary": mworks_yaw_rate_decoupling_return.get("claim_boundary", [])
                if isinstance(mworks_yaw_rate_decoupling_return.get("claim_boundary"), list)
                else [
                    "Yaw/rate decoupling result-context probe only.",
                    "No closed_loop, Factory trace consumption, controller performance, plant tracking, or parameter identification claim.",
                ],
            },
            "rate_feedback_isolation_probe": {
                "status": str(mworks_rate_feedback_isolation_return.get("status", "not_run"))
                if mworks_rate_feedback_isolation_return
                else "not_run",
                "quality_status": mworks_rate_feedback_isolation_return.get("quality_status", "")
                if mworks_rate_feedback_isolation_return
                else "",
                "return_packet": rel(mworks_rate_feedback_isolation_return_path)
                if mworks_rate_feedback_isolation_return
                else "",
                "completion_scope": mworks_rate_feedback_isolation_return.get("completion_scope", "")
                if mworks_rate_feedback_isolation_return
                else "",
                "summary": mworks_rate_feedback_isolation_return.get("summary", "")
                if mworks_rate_feedback_isolation_return
                else "",
                "rate_feedback_probes": mworks_rate_feedback_isolation_return.get("rate_feedback_probes", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("rate_feedback_probes"), list)
                else [],
                "classification": mworks_rate_feedback_isolation_return.get("classification", {})
                if isinstance(mworks_rate_feedback_isolation_return.get("classification"), dict)
                else {},
                "unknowns": mworks_rate_feedback_isolation_return.get("unknowns", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("unknowns"), list)
                else [],
                "risks": mworks_rate_feedback_isolation_return.get("risks", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("risks"), list)
                else [],
                "next_validation": mworks_rate_feedback_isolation_return.get("next_validation", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("next_validation"), list)
                else [],
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_rate_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_rate_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_rate_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_rate_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_rate_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_rate_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "unknowns_risks_next_validation": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_rate_feedback_isolation_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "unknowns_risks_next_validation"
                    ),
                    "",
                )
                if isinstance(mworks_rate_feedback_isolation_return.get("artifact_refs"), list)
                else "",
                "models_created": mworks_rate_feedback_isolation_return.get("models_created", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("models_created"), list)
                else [],
                "forbidden_edits_avoided": mworks_rate_feedback_isolation_return.get("forbidden_edits_avoided", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("forbidden_edits_avoided"), list)
                else [],
                "recommended_next_step": mworks_rate_feedback_isolation_return.get("recommended_next_step", "")
                if mworks_rate_feedback_isolation_return
                else "",
                "claim_boundary": mworks_rate_feedback_isolation_return.get("claim_boundary", [])
                if isinstance(mworks_rate_feedback_isolation_return.get("claim_boundary"), list)
                else [
                    "Rate alias/result-context isolation probe only.",
                    "No external rate-feedback controller, closed_loop, Factory trace consumption, controller performance, plant tracking, or parameter identification claim.",
                ],
            },
            "sensor_bus_reconnect_probe": {
                "status": str(mworks_sensor_bus_reconnect_blocker.get("status", "not_run"))
                if mworks_sensor_bus_reconnect_blocker
                else "not_run",
                "quality_status": mworks_sensor_bus_reconnect_blocker.get("quality_status", "")
                if mworks_sensor_bus_reconnect_blocker
                else "",
                "blocker_packet": rel(mworks_sensor_bus_reconnect_blocker_path)
                if mworks_sensor_bus_reconnect_blocker
                else "",
                "blocker_kind": mworks_sensor_bus_reconnect_blocker.get("blocker_kind", "")
                if mworks_sensor_bus_reconnect_blocker
                else "",
                "source": mworks_sensor_bus_reconnect_blocker.get("source", "")
                if mworks_sensor_bus_reconnect_blocker
                else "",
                "summary": mworks_sensor_bus_reconnect_blocker.get("summary", "")
                if mworks_sensor_bus_reconnect_blocker
                else "",
                "models_created": mworks_sensor_bus_reconnect_blocker.get("models_created", [])
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("models_created"), list)
                else [],
                "probe_results": mworks_sensor_bus_reconnect_blocker.get("probe_results", [])
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("probe_results"), list)
                else [],
                "unknowns": mworks_sensor_bus_reconnect_blocker.get("unknowns", [])
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("unknowns"), list)
                else [],
                "risks": mworks_sensor_bus_reconnect_blocker.get("risks", [])
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("risks"), list)
                else [],
                "next_validation": mworks_sensor_bus_reconnect_blocker.get("next_validation", [])
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("next_validation"), list)
                else [],
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_sensor_bus_reconnect_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("artifact_refs"), list)
                else "",
                "probe_summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_sensor_bus_reconnect_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_sensor_bus_reconnect_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("artifact_refs"), list)
                else "",
                "forbidden_actions_confirmed": mworks_sensor_bus_reconnect_blocker.get(
                    "forbidden_actions_confirmed", []
                )
                if isinstance(mworks_sensor_bus_reconnect_blocker.get("forbidden_actions_confirmed"), list)
                else [],
                "claim_boundary": [
                    "Sensor/display reconnect boundary probe only.",
                    "Direct PosMea display reconnect is blocked; no Factory trace consumption, closed_loop, controller performance, plant tracking, or parameter identification claim is made.",
                ],
            },
            "position_bridge_probe": {
                "status": str(mworks_position_bridge_return.get("status", "not_run"))
                if mworks_position_bridge_return
                else "not_run",
                "quality_status": mworks_position_bridge_return.get("quality_status", "")
                if mworks_position_bridge_return
                else "",
                "return_packet": rel(mworks_position_bridge_return_path)
                if mworks_position_bridge_return
                else "",
                "source": mworks_position_bridge_return.get("source", "")
                if mworks_position_bridge_return
                else "",
                "summary": mworks_position_bridge_return.get("summary", "")
                if mworks_position_bridge_return
                else "",
                "models_created": mworks_position_bridge_return.get("models_created", [])
                if isinstance(mworks_position_bridge_return.get("models_created"), list)
                else [],
                "probe_results": mworks_position_bridge_return.get("probe_results", [])
                if isinstance(mworks_position_bridge_return.get("probe_results"), list)
                else [],
                "unknowns": mworks_position_bridge_return.get("unknowns", [])
                if isinstance(mworks_position_bridge_return.get("unknowns"), list)
                else [],
                "risks": mworks_position_bridge_return.get("risks", [])
                if isinstance(mworks_position_bridge_return.get("risks"), list)
                else [],
                "next_validation": mworks_position_bridge_return.get("next_validation", [])
                if isinstance(mworks_position_bridge_return.get("next_validation"), list)
                else [],
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_position_bridge_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_position_bridge_return.get("artifact_refs"), list)
                else "",
                "alias_samples_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_position_bridge_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "alias_samples_csv"
                    ),
                    "",
                )
                if isinstance(mworks_position_bridge_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_position_bridge_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_position_bridge_return.get("artifact_refs"), list)
                else "",
                "claim_boundary": mworks_position_bridge_return.get("claim_boundary", "")
                if mworks_position_bridge_return
                else "",
                "forbidden_actions_confirmed": mworks_position_bridge_return.get(
                    "forbidden_actions_confirmed", []
                )
                if isinstance(mworks_position_bridge_return.get("forbidden_actions_confirmed"), list)
                else [],
            },
            "next_sensor_display_group_probe": {
                "status": str(mworks_next_sensor_display_group_blocker.get("status", "not_run"))
                if mworks_next_sensor_display_group_blocker
                else "not_run",
                "quality_status": mworks_next_sensor_display_group_blocker.get("quality_status", "")
                if mworks_next_sensor_display_group_blocker
                else "",
                "blocker_packet": rel(mworks_next_sensor_display_group_blocker_path)
                if mworks_next_sensor_display_group_blocker
                else "",
                "blocker_kind": mworks_next_sensor_display_group_blocker.get("blocker_kind", "")
                if mworks_next_sensor_display_group_blocker
                else "",
                "source": mworks_next_sensor_display_group_blocker.get("source", "")
                if mworks_next_sensor_display_group_blocker
                else "",
                "summary": mworks_next_sensor_display_group_blocker.get("summary", "")
                if mworks_next_sensor_display_group_blocker
                else "",
                "topology_findings": mworks_next_sensor_display_group_blocker.get("topology_findings", [])
                if isinstance(mworks_next_sensor_display_group_blocker.get("topology_findings"), list)
                else [],
                "artifact_refs": mworks_next_sensor_display_group_blocker.get("artifact_refs", [])
                if isinstance(mworks_next_sensor_display_group_blocker.get("artifact_refs"), list)
                else [],
                "topology_comparison": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_next_sensor_display_group_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "topology_comparison"
                    ),
                    "",
                )
                if isinstance(mworks_next_sensor_display_group_blocker.get("artifact_refs"), list)
                else "",
                "prior_passing_mworks_mcp_evidence": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_next_sensor_display_group_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "prior_passing_mworks_mcp_evidence"
                    ),
                    "",
                )
                if isinstance(mworks_next_sensor_display_group_blocker.get("artifact_refs"), list)
                else "",
                "unknowns": mworks_next_sensor_display_group_blocker.get("unknowns", [])
                if isinstance(mworks_next_sensor_display_group_blocker.get("unknowns"), list)
                else [],
                "risks": mworks_next_sensor_display_group_blocker.get("risks", [])
                if isinstance(mworks_next_sensor_display_group_blocker.get("risks"), list)
                else [],
                "next_validation": mworks_next_sensor_display_group_blocker.get("next_validation", [])
                if isinstance(mworks_next_sensor_display_group_blocker.get("next_validation"), list)
                else [],
                "claim_boundary": mworks_next_sensor_display_group_blocker.get("claim_boundary", "")
                if mworks_next_sensor_display_group_blocker
                else "",
                "forbidden_actions_confirmed": mworks_next_sensor_display_group_blocker.get(
                    "forbidden_actions_confirmed", []
                )
                if isinstance(mworks_next_sensor_display_group_blocker.get("forbidden_actions_confirmed"), list)
                else [],
                "exactly_one_group_added": bool(
                    mworks_next_sensor_display_group_blocker.get("exactly_one_group_added", False)
                )
                if mworks_next_sensor_display_group_blocker
                else False,
            },
            "first_control_feedback_group_probe": {
                "status": str(mworks_first_control_feedback_group_blocker.get("status", "not_run"))
                if mworks_first_control_feedback_group_blocker
                else "not_run",
                "quality_status": mworks_first_control_feedback_group_blocker.get("quality_status", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "blocker_packet": rel(mworks_first_control_feedback_group_blocker_path)
                if mworks_first_control_feedback_group_blocker
                else "",
                "blocker_kind": mworks_first_control_feedback_group_blocker.get("blocker_kind", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "source": mworks_first_control_feedback_group_blocker.get("source", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "summary": mworks_first_control_feedback_group_blocker.get("summary", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "models_created": as_list(mworks_first_control_feedback_group_blocker.get("models_created")),
                "models_modified": as_list(mworks_first_control_feedback_group_blocker.get("models_modified")),
                "selected_group": mworks_first_control_feedback_group_blocker.get("selected_group", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "exactly_one_group_added": bool(
                    mworks_first_control_feedback_group_blocker.get("exactly_one_group_added", False)
                )
                if mworks_first_control_feedback_group_blocker
                else False,
                "iso23_display_bridge_preserved": bool(
                    mworks_first_control_feedback_group_blocker.get("iso23_display_bridge_preserved", False)
                )
                if mworks_first_control_feedback_group_blocker
                else False,
                "check_model": as_mapping(mworks_first_control_feedback_group_blocker.get("check_model")),
                "simulate_model": as_mapping(mworks_first_control_feedback_group_blocker.get("simulate_model")),
                "get_var_times": as_mapping(mworks_first_control_feedback_group_blocker.get("get_var_times")),
                "aliases": as_mapping(mworks_first_control_feedback_group_blocker.get("aliases")),
                "error_6140_present": mworks_first_control_feedback_group_blocker.get("error_6140_present")
                if mworks_first_control_feedback_group_blocker
                else None,
                "first_new_boundary": mworks_first_control_feedback_group_blocker.get("first_new_boundary", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "artifact_refs": as_list(mworks_first_control_feedback_group_blocker.get("artifact_refs")),
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_first_control_feedback_group_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_first_control_feedback_group_blocker.get("artifact_refs"), list)
                else "",
                "summary_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_first_control_feedback_group_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "summary_csv"
                    ),
                    "",
                )
                if isinstance(mworks_first_control_feedback_group_blocker.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_first_control_feedback_group_blocker.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_first_control_feedback_group_blocker.get("artifact_refs"), list)
                else "",
                "unknowns": as_list(mworks_first_control_feedback_group_blocker.get("unknowns")),
                "risks": as_list(mworks_first_control_feedback_group_blocker.get("risks")),
                "next_validation": as_list(mworks_first_control_feedback_group_blocker.get("next_validation")),
                "claim_boundary": mworks_first_control_feedback_group_blocker.get("claim_boundary", "")
                if mworks_first_control_feedback_group_blocker
                else "",
                "forbidden_actions_confirmed": as_list(
                    mworks_first_control_feedback_group_blocker.get("forbidden_actions_confirmed")
                ),
            },
            "attitude_feedback_bridge_probe": {
                "status": str(mworks_attitude_feedback_bridge_return.get("status", "not_run"))
                if mworks_attitude_feedback_bridge_return
                else "not_run",
                "quality_status": mworks_attitude_feedback_bridge_return.get("quality_status", "")
                if mworks_attitude_feedback_bridge_return
                else "",
                "return_packet": rel(mworks_attitude_feedback_bridge_return_path)
                if mworks_attitude_feedback_bridge_return
                else "",
                "source": mworks_attitude_feedback_bridge_return.get("source", "")
                if mworks_attitude_feedback_bridge_return
                else "",
                "summary": mworks_attitude_feedback_bridge_return.get("summary", "")
                if mworks_attitude_feedback_bridge_return
                else "",
                "selected_bridge_variant": mworks_attitude_feedback_bridge_return.get(
                    "selected_bridge_variant", ""
                )
                if mworks_attitude_feedback_bridge_return
                else "",
                "models_created": as_list(mworks_attitude_feedback_bridge_return.get("models_created")),
                "models_modified": as_list(mworks_attitude_feedback_bridge_return.get("models_modified")),
                "probe_results": as_list(mworks_attitude_feedback_bridge_return.get("probe_results")),
                "artifact_refs": as_list(mworks_attitude_feedback_bridge_return.get("artifact_refs")),
                "probe_json": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_feedback_bridge_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "probe_json"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_feedback_bridge_return.get("artifact_refs"), list)
                else "",
                "alias_samples_csv": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_feedback_bridge_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "alias_samples_csv"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_feedback_bridge_return.get("artifact_refs"), list)
                else "",
                "mcp_log": next(
                    (
                        str(item.get("path", ""))
                        for item in mworks_attitude_feedback_bridge_return.get("artifact_refs", [])
                        if isinstance(item, dict) and item.get("role") == "mcp_log"
                    ),
                    "",
                )
                if isinstance(mworks_attitude_feedback_bridge_return.get("artifact_refs"), list)
                else "",
                "unknowns": as_list(mworks_attitude_feedback_bridge_return.get("unknowns")),
                "risks": as_list(mworks_attitude_feedback_bridge_return.get("risks")),
                "next_validation": as_list(mworks_attitude_feedback_bridge_return.get("next_validation")),
                "claim_boundary": mworks_attitude_feedback_bridge_return.get("claim_boundary", "")
                if mworks_attitude_feedback_bridge_return
                else "",
                "forbidden_actions_confirmed": as_list(
                    mworks_attitude_feedback_bridge_return.get("forbidden_actions_confirmed")
                ),
            },
            "trace_consumption_claim_boundary": [
                "A project-owned wrapper/check_model attempt is not counted as consumed setpoint trace.",
                "closed_loop remains excluded until MWORKS produces raw/metrics evidence from the same planner setpoint trace.",
            ],
        },
        "ros2": {
            "bag_or_summary": rel(project_path(args.realstack_gate)),
            "imu_rate_hz": float(gate.get("rates_hz", {}).get("imu_required", 200.0)),
            "lidar_rate_hz": float(gate.get("rates_hz", {}).get("lidar_required", 10.0)),
            "tf_status": "pass",
            "timestamp_monotonic": bool(gate.get("mworks_state", {}).get("monotonic_time", False))
            and gate.get("lidar", {}).get("nonmonotonic_time_pairs", 1) == 0,
            "fast_lio_eval": {
                "status": fast_lio.get("status", ""),
                "position_rmse_m": fast_lio_metrics.get("position_rmse_m"),
                "max_error_m": fast_lio_metrics.get("max_position_error_m"),
                "aligned_samples": fast_lio_metrics.get("aligned_samples"),
                "runtime_recording": gate_paths.get("runtime_recording", ""),
                "runtime_evaluation": gate_paths.get("runtime_evaluation", ""),
            },
            "adapter_smoke": {
                "status": "pass" if adapter.get("pass") is True else "needs_iteration",
                "setpoint_count": adapter.get("setpoint_count", 0),
                "status_count": adapter.get("status_count", 0),
                "position_command_converter_status": (
                    "pass" if position_adapter.get("pass") is True else "not_run"
                ),
                "position_command_converted_count": position_adapter.get("converted_count", 0),
            },
            "position_command_b0_contract_replay": {
                "status": str(b0_summary.get("quality_status", "not_run")),
                "smoke_only": bool(
                    b0_summary.get("b0_contract_replay", {}).get("smoke_only", False)
                    if isinstance(b0_summary.get("b0_contract_replay"), dict)
                    else False
                ),
                "not_planner_closure": bool(
                    b0_summary.get("b0_contract_replay", {}).get("not_planner_closure", False)
                    if isinstance(b0_summary.get("b0_contract_replay"), dict)
                    else False
                ),
                "run_summary": rel(b0_summary_path) if b0_summary else "",
                "topic_rates": rel(b0_topic_rates_path) if b0_topic_rates_path else "",
                "planner_input_gate": rel(b0_planner_input_gate_path) if b0_planner_input_gate_path else "",
                "source_available": bool(b0_summary.get("source_available", False)),
                "accepted_ratio": b0_summary.get("accepted_ratio"),
                "stale_samples": b0_summary.get("stale_samples"),
                "rates_ok": bool(b0_summary.get("rates_ok", False)),
                "timestamp_ok": bool(b0_summary.get("timestamp_ok", False)),
                "frame_ok": bool(b0_summary.get("frame_ok", False)),
                "source_topic": b0_summary.get("source_topic", ""),
                "converted_topic": b0_summary.get("converted_topic", ""),
                "setpoint_topic": b0_summary.get("setpoint_topic", ""),
                "setpoint_trace_csv": rel(setpoint_trace_path),
                "measured_rates_hz": b0_topic_rates.get("rates_hz", {}),
                "planner_input_gate_status": {
                    "global_truth_used_as_input": b0_planner_input_gate.get("global_truth_used_as_input"),
                    "local_map_runtime_source": b0_planner_input_gate.get("local_map_runtime_source", ""),
                    "notes": b0_planner_input_gate.get("notes", ""),
                },
                "claim_boundary": [
                    "B0 proves PositionCommand contract replay, converter, adapter rate, and recorder behavior only.",
                    "B0 does not prove a real local-map planner or closed-loop MWORKS/controller consumption.",
                ],
            },
            "position_command_b1_real_planner": {
                "status": str(b1_blocker.get("status", "not_run")) if b1_blocker else "not_run",
                "b1_executable_now": bool(
                    b1_blocker.get("decision", {}).get("b1_executable_now", False)
                    if isinstance(b1_blocker.get("decision"), dict)
                    else False
                ),
                "blocker_packet": rel(b1_blocker_path) if b1_blocker else "",
                "summary": b1_blocker.get("summary", "") if b1_blocker else "",
                "missing_from_live_graph": (
                    b1_blocker.get("live_ros2_graph_probe", {}).get("missing_from_live_graph", [])
                    if isinstance(b1_blocker.get("live_ros2_graph_probe"), dict)
                    else []
                ),
                "topics_seen": (
                    b1_blocker.get("live_ros2_graph_probe", {}).get("topics_seen", [])
                    if isinstance(b1_blocker.get("live_ros2_graph_probe"), dict)
                    else []
                ),
                "nodes_seen": (
                    b1_blocker.get("live_ros2_graph_probe", {}).get("nodes_seen", [])
                    if isinstance(b1_blocker.get("live_ros2_graph_probe"), dict)
                    else []
                ),
                "blocker_ids": [
                    str(item.get("id", ""))
                    for item in b1_blockers
                    if isinstance(item, dict) and item.get("id")
                ],
                "claim_boundary": [
                    "B1 requires real runtime odom plus local sensed map/cloud/voxel planner input.",
                    "B0 contract replay and offline UE handoff remain excluded from B1 planner closure.",
                ],
            },
            "position_command_b1_unblock": {
                "status": str(b1_unblock_blocker.get("status", "not_run")) if b1_unblock_blocker else "not_run",
                "blocker_packet": rel(b1_unblock_blocker_path) if b1_unblock_blocker else "",
                "summary": b1_unblock_blocker.get("summary", "") if b1_unblock_blocker else "",
                "fast_lio_runtime_restored": bool(
                    b1_unblock_blocker.get("decision", {}).get("fast_lio_runtime_restored", False)
                    if isinstance(b1_unblock_blocker.get("decision"), dict)
                    else False
                ),
                "local_sensed_cloud_candidate_restored": bool(
                    b1_unblock_blocker.get("decision", {}).get("local_sensed_cloud_candidate_restored", False)
                    if isinstance(b1_unblock_blocker.get("decision"), dict)
                    else False
                ),
                "planner_position_command_source_restored": bool(
                    b1_unblock_blocker.get("decision", {}).get("planner_position_command_source_restored", False)
                    if isinstance(b1_unblock_blocker.get("decision"), dict)
                    else False
                ),
                "restored_topics": (
                    b1_unblock_blocker.get("new_current_fast_lio_recording", {}).get("restored_topics", {})
                    if isinstance(b1_unblock_blocker.get("new_current_fast_lio_recording"), dict)
                    else {}
                ),
                "current_recording": (
                    b1_unblock_blocker.get("new_current_fast_lio_recording", {}).get("output_dir", "")
                    if isinstance(b1_unblock_blocker.get("new_current_fast_lio_recording"), dict)
                    else ""
                ),
                "truth_evaluation": (
                    b1_unblock_blocker.get("new_current_fast_lio_recording", {}).get("truth_evaluation", {})
                    if isinstance(b1_unblock_blocker.get("new_current_fast_lio_recording"), dict)
                    else {}
                ),
                "candidate_local_sensed_cloud": (
                    b1_unblock_blocker.get("candidate_local_sensed_map_or_cloud", {})
                    if isinstance(b1_unblock_blocker.get("candidate_local_sensed_map_or_cloud"), dict)
                    else {}
                ),
                "candidate_odom_source": (
                    b1_unblock_blocker.get("candidate_odom_source", {})
                    if isinstance(b1_unblock_blocker.get("candidate_odom_source"), dict)
                    else {}
                ),
                "candidate_planner_runtime_package": (
                    b1_unblock_blocker.get("candidate_planner_runtime_package", {})
                    if isinstance(b1_unblock_blocker.get("candidate_planner_runtime_package"), dict)
                    else {}
                ),
                "claim_boundary": [
                    "Restored FAST-LIO/current recording alone is not B1 planner closure.",
                    "B1 remains blocked until a real planner emits sustained PositionCommand from local sensed map/odom input.",
                ],
            },
            "position_command_b1_planner_wrapper": {
                "status": str(b1_planner_wrapper_blocker.get("status", "not_run"))
                if b1_planner_wrapper_blocker
                else "not_run",
                "blocker_packet": rel(b1_planner_wrapper_blocker_path) if b1_planner_wrapper_blocker else "",
                "summary": b1_planner_wrapper_blocker.get("summary", "") if b1_planner_wrapper_blocker else "",
                "wrapper_safe_to_add_now": bool(
                    b1_planner_wrapper_blocker.get("decision", {}).get("wrapper_safe_to_add_now", False)
                    if isinstance(b1_planner_wrapper_blocker.get("decision"), dict)
                    else False
                ),
                "selected_planner_candidate": (
                    b1_planner_wrapper_blocker.get("decision", {}).get("selected_planner_candidate", "")
                    if isinstance(b1_planner_wrapper_blocker.get("decision"), dict)
                    else ""
                ),
                "can_directly_ros2_build_or_run": bool(
                    b1_planner_wrapper_blocker.get("decision", {}).get("can_directly_ros2_build_or_run", False)
                    if isinstance(b1_planner_wrapper_blocker.get("decision"), dict)
                    else False
                ),
                "can_directly_run_ros1_catkin_now": bool(
                    b1_planner_wrapper_blocker.get("decision", {}).get("can_directly_run_ros1_catkin_now", False)
                    if isinstance(b1_planner_wrapper_blocker.get("decision"), dict)
                    else False
                ),
                "current_authoritative_inputs": b1_planner_wrapper_blocker.get("current_authoritative_inputs", {})
                if isinstance(b1_planner_wrapper_blocker.get("current_authoritative_inputs"), dict)
                else {},
                "missing_to_execute_ids": [
                    str(item.get("id", ""))
                    for item in b1_planner_wrapper_blocker.get("missing_to_execute", [])
                    if isinstance(item, dict) and item.get("id")
                ]
                if isinstance(b1_planner_wrapper_blocker.get("missing_to_execute"), list)
                else [],
                "rejected_shortcuts": [
                    str(item.get("shortcut", ""))
                    for item in b1_planner_wrapper_blocker.get("rejected_shortcuts", [])
                    if isinstance(item, dict) and item.get("shortcut")
                ]
                if isinstance(b1_planner_wrapper_blocker.get("rejected_shortcuts"), list)
                else [],
                "next_route": (
                    b1_planner_wrapper_blocker.get("next_exact_setup_build_launch_commands", {})
                    .get("route_b1_ros2_port_preflight", {})
                    .get("purpose", "")
                )
                if isinstance(b1_planner_wrapper_blocker.get("next_exact_setup_build_launch_commands"), dict)
                else "",
                "claim_boundary": [
                    "006 selected real EGO/Sunray/FUEL planner behavior but found no executable ROS2 planner package.",
                    "Do not convert FAST-LIO /path or scripted waypoints into PositionCommand as a B1 shortcut.",
                ],
            },
            "position_command_b1_port_preflight": {
                "status": str(b1_port_preflight_return.get("status", "not_run"))
                if b1_port_preflight_return
                else "not_run",
                "return_packet": rel(b1_port_preflight_return_path) if b1_port_preflight_return else "",
                "summary": b1_port_preflight_return.get("summary", "") if b1_port_preflight_return else "",
                "port_preflight_completed": bool(
                    b1_port_preflight_return.get("decision", {}).get("port_preflight_completed", False)
                    if isinstance(b1_port_preflight_return.get("decision"), dict)
                    else False
                ),
                "runtime_position_cmd_ready": bool(
                    b1_port_preflight_return.get("decision", {}).get("runtime_position_cmd_ready", False)
                    if isinstance(b1_port_preflight_return.get("decision"), dict)
                    else False
                ),
                "can_enter_real_position_cmd_recorder": bool(
                    b1_port_preflight_return.get("decision", {}).get("can_enter_real_position_cmd_recorder", False)
                    if isinstance(b1_port_preflight_return.get("decision"), dict)
                    else False
                ),
                "recommended_route": (
                    b1_port_preflight_return.get("decision", {}).get("recommended_route", "")
                    if isinstance(b1_port_preflight_return.get("decision"), dict)
                    else ""
                ),
                "port_effort": (
                    b1_port_preflight_return.get("decision", {}).get("port_effort", {})
                    if isinstance(b1_port_preflight_return.get("decision"), dict)
                    and isinstance(b1_port_preflight_return.get("decision", {}).get("port_effort"), dict)
                    else {}
                ),
                "copied_workspace": (
                    b1_port_preflight_return.get("copied_candidate_workspace", {}).get("workspace", "")
                    if isinstance(b1_port_preflight_return.get("copied_candidate_workspace"), dict)
                    else ""
                ),
                "build_log": (
                    b1_port_preflight_return.get("build_preflight", {}).get("log", "")
                    if isinstance(b1_port_preflight_return.get("build_preflight"), dict)
                    else ""
                ),
                "first_actionable_error": (
                    b1_port_preflight_return.get("build_preflight", {}).get("first_actionable_error", "")
                    if isinstance(b1_port_preflight_return.get("build_preflight"), dict)
                    else ""
                ),
                "route_classification": b1_port_preflight_return.get("route_classification", {})
                if isinstance(b1_port_preflight_return.get("route_classification"), dict)
                else {},
                "runtime_recorder_gate": b1_port_preflight_return.get("runtime_recorder_gate", {})
                if isinstance(b1_port_preflight_return.get("runtime_recorder_gate"), dict)
                else {},
                "claim_boundary": [
                    "007 is a source-port preflight classification, not a running planner.",
                    "Do not start the B1 PositionCommand recorder until a real planner/local-map chain publishes /position_cmd.",
                ],
            },
            "position_command_b1_msg_port_slice": {
                "status": str(b1_msg_port_slice_return.get("status", "not_run"))
                if b1_msg_port_slice_return
                else "not_run",
                "return_packet": rel(b1_msg_port_slice_return_path) if b1_msg_port_slice_return else "",
                "summary": b1_msg_port_slice_return.get("summary", "") if b1_msg_port_slice_return else "",
                "message_strategy": b1_msg_port_slice_return.get("message_strategy", {})
                if isinstance(b1_msg_port_slice_return.get("message_strategy"), dict)
                else {},
                "changed_isolated_workspace_files": b1_msg_port_slice_return.get(
                    "changed_isolated_workspace_files", []
                )
                if isinstance(b1_msg_port_slice_return.get("changed_isolated_workspace_files"), list)
                else [],
                "colcon_build_status": b1_msg_port_slice_return.get("colcon_build_status", {})
                if isinstance(b1_msg_port_slice_return.get("colcon_build_status"), dict)
                else {},
                "interface_verification": b1_msg_port_slice_return.get("interface_verification", {})
                if isinstance(b1_msg_port_slice_return.get("interface_verification"), dict)
                else {},
                "remaining_blocker_ids": [
                    str(item.get("id", ""))
                    for item in b1_msg_port_slice_return.get("remaining_blockers", [])
                    if isinstance(item, dict) and item.get("id")
                ]
                if isinstance(b1_msg_port_slice_return.get("remaining_blockers"), list)
                else [],
                "can_start_planner_node_porting": (
                    b1_msg_port_slice_return.get("can_start_planner_node_porting", {})
                    if isinstance(b1_msg_port_slice_return.get("can_start_planner_node_porting"), dict)
                    else {}
                ),
                "can_start_runtime_recorder": (
                    b1_msg_port_slice_return.get("can_start_runtime_recorder", {})
                    if isinstance(b1_msg_port_slice_return.get("can_start_runtime_recorder"), dict)
                    else {}
                ),
                "artifacts": b1_msg_port_slice_return.get("artifacts", [])
                if isinstance(b1_msg_port_slice_return.get("artifacts"), list)
                else [],
                "claim_boundary": [
                    "008 builds only internal ROS2 messages in an isolated workspace.",
                    "No planner node logic is ported and no /position_cmd runtime topic is published yet.",
                ],
            },
            "position_command_b1_planner_node_port_preflight": {
                "status": str(b1_planner_node_port_return.get("status", "not_run"))
                if b1_planner_node_port_return
                else "not_run",
                "quality_status": b1_planner_node_port_return.get("quality_status", "")
                if b1_planner_node_port_return
                else "",
                "return_packet": rel(b1_planner_node_port_return_path) if b1_planner_node_port_return else "",
                "summary": b1_planner_node_port_return.get("summary", {})
                if isinstance(b1_planner_node_port_return.get("summary"), dict)
                else {},
                "changed_isolated_workspace_files": b1_planner_node_port_return.get(
                    "changed_isolated_workspace_files", []
                )
                if isinstance(b1_planner_node_port_return.get("changed_isolated_workspace_files"), list)
                else [],
                "converted_stub_node_files": b1_planner_node_port_return.get("converted_stub_node_files", [])
                if isinstance(b1_planner_node_port_return.get("converted_stub_node_files"), list)
                else [],
                "node_contract": b1_planner_node_port_return.get("node_contract", {})
                if isinstance(b1_planner_node_port_return.get("node_contract"), dict)
                else {},
                "build_status": b1_planner_node_port_return.get("build_status", {})
                if isinstance(b1_planner_node_port_return.get("build_status"), dict)
                else {},
                "evidence_artifacts": b1_planner_node_port_return.get("evidence_artifacts", [])
                if isinstance(b1_planner_node_port_return.get("evidence_artifacts"), list)
                else [],
                "forbidden_actions_confirmed": b1_planner_node_port_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_planner_node_port_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "remaining_blockers": b1_planner_node_port_return.get("remaining_blockers", [])
                if isinstance(b1_planner_node_port_return.get("remaining_blockers"), list)
                else [],
                "claim_boundary": [
                    "009 compiles an isolated traj_server ROS2 surface/stub only.",
                    "No planner runtime was launched, no /position_cmd was published, and no runtime recorder was run.",
                ],
            },
            "position_command_b1_upstream_planner_deps": {
                "status": str(b1_upstream_planner_deps_blocker.get("status", "not_run"))
                if b1_upstream_planner_deps_blocker
                else "not_run",
                "quality_status": b1_upstream_planner_deps_blocker.get("quality_status", "")
                if b1_upstream_planner_deps_blocker
                else "",
                "blocker_packet": rel(b1_upstream_planner_deps_blocker_path)
                if b1_upstream_planner_deps_blocker
                else "",
                "summary": b1_upstream_planner_deps_blocker.get("summary", "")
                if b1_upstream_planner_deps_blocker
                else "",
                "preferred_bspline_producer": (
                    b1_upstream_planner_deps_blocker.get("upstream_bspline_producer_candidates", [{}])[0]
                    if isinstance(b1_upstream_planner_deps_blocker.get("upstream_bspline_producer_candidates"), list)
                    and b1_upstream_planner_deps_blocker.get("upstream_bspline_producer_candidates")
                    else {}
                ),
                "first_blocker": b1_upstream_planner_deps_blocker.get("first_blocker", {})
                if isinstance(b1_upstream_planner_deps_blocker.get("first_blocker"), dict)
                else {},
                "current_isolated_workspace_state": b1_upstream_planner_deps_blocker.get(
                    "current_isolated_workspace_state", {}
                )
                if isinstance(b1_upstream_planner_deps_blocker.get("current_isolated_workspace_state"), dict)
                else {},
                "dependency_surface": b1_upstream_planner_deps_blocker.get("dependency_surface", {})
                if isinstance(b1_upstream_planner_deps_blocker.get("dependency_surface"), dict)
                else {},
                "artifacts": b1_upstream_planner_deps_blocker.get("artifacts", {})
                if isinstance(b1_upstream_planner_deps_blocker.get("artifacts"), dict)
                else {},
                "can_reach_real_planning_bspline_next": b1_upstream_planner_deps_blocker.get(
                    "can_reach_real_planning_bspline_next", {}
                )
                if isinstance(b1_upstream_planner_deps_blocker.get("can_reach_real_planning_bspline_next"), dict)
                else {},
                "forbidden_actions_confirmed": b1_upstream_planner_deps_blocker.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_upstream_planner_deps_blocker.get("forbidden_actions_confirmed"), dict)
                else {},
                "claim_boundary": [
                    "010 identified EGOReplanFSM as the preferred /planning/bspline producer.",
                    "Real Bspline runtime remains blocked until plan_env/GridMap and required dependencies are ROS2-buildable and wired to /Odometry plus /cloud_registered.",
                ],
            },
            "position_command_b1_planenv_gridmap_port": {
                "status": str(b1_planenv_gridmap_port_return.get("status", "not_run"))
                if b1_planenv_gridmap_port_return
                else "not_run",
                "quality_status": b1_planenv_gridmap_port_return.get("quality_status", "")
                if b1_planenv_gridmap_port_return
                else "",
                "return_packet": rel(b1_planenv_gridmap_port_return_path)
                if b1_planenv_gridmap_port_return
                else "",
                "summary": b1_planenv_gridmap_port_return.get("summary", {})
                if isinstance(b1_planenv_gridmap_port_return.get("summary"), dict)
                else {},
                "changed_files": b1_planenv_gridmap_port_return.get("changed_files", [])
                if isinstance(b1_planenv_gridmap_port_return.get("changed_files"), list)
                else [],
                "ros2_api_surface_now_present": b1_planenv_gridmap_port_return.get(
                    "ros2_api_surface_now_present", []
                )
                if isinstance(b1_planenv_gridmap_port_return.get("ros2_api_surface_now_present"), list)
                else [],
                "still_blocking_or_deferred_inside_plan_env": b1_planenv_gridmap_port_return.get(
                    "still_blocking_or_deferred_inside_plan_env", []
                )
                if isinstance(b1_planenv_gridmap_port_return.get("still_blocking_or_deferred_inside_plan_env"), list)
                else [],
                "build_status": b1_planenv_gridmap_port_return.get("build_status", {})
                if isinstance(b1_planenv_gridmap_port_return.get("build_status"), dict)
                else {},
                "classification_logs": b1_planenv_gridmap_port_return.get("classification_logs", [])
                if isinstance(b1_planenv_gridmap_port_return.get("classification_logs"), list)
                else [],
                "workspace_package_state_after_011": b1_planenv_gridmap_port_return.get(
                    "workspace_package_state_after_011", {}
                )
                if isinstance(b1_planenv_gridmap_port_return.get("workspace_package_state_after_011"), dict)
                else {},
                "runtime_contract_preserved": b1_planenv_gridmap_port_return.get("runtime_contract_preserved", {})
                if isinstance(b1_planenv_gridmap_port_return.get("runtime_contract_preserved"), dict)
                else {},
                "forbidden_actions_confirmed": b1_planenv_gridmap_port_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_planenv_gridmap_port_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "exact_next_command": b1_planenv_gridmap_port_return.get("exact_next_command", {})
                if isinstance(b1_planenv_gridmap_port_return.get("exact_next_command"), dict)
                else {},
                "claim_boundary": [
                    "011 proves only the isolated plan_env/GridMap ROS2 build/API surface.",
                    "No planner runtime, /planning/bspline, /position_cmd, runtime recorder, or local-map quality claim is made.",
                ],
            },
            "position_command_b1_path_bspline_port": {
                "status": str(b1_path_bspline_port_return.get("status", "not_run"))
                if b1_path_bspline_port_return
                else "not_run",
                "quality_status": b1_path_bspline_port_return.get("quality_status", "")
                if b1_path_bspline_port_return
                else "",
                "return_packet": rel(b1_path_bspline_port_return_path)
                if b1_path_bspline_port_return
                else "",
                "summary": b1_path_bspline_port_return.get("summary", {})
                if isinstance(b1_path_bspline_port_return.get("summary"), dict)
                else {},
                "changed_isolated_files": b1_path_bspline_port_return.get("changed_isolated_files", [])
                if isinstance(b1_path_bspline_port_return.get("changed_isolated_files"), list)
                else [],
                "ros2_api_surface_now_present": b1_path_bspline_port_return.get(
                    "ros2_api_surface_now_present", []
                )
                if isinstance(b1_path_bspline_port_return.get("ros2_api_surface_now_present"), list)
                else [],
                "build_status": b1_path_bspline_port_return.get("build_status", {})
                if isinstance(b1_path_bspline_port_return.get("build_status"), dict)
                else {},
                "installed_artifacts": b1_path_bspline_port_return.get("installed_artifacts", [])
                if isinstance(b1_path_bspline_port_return.get("installed_artifacts"), list)
                else [],
                "classification_logs": b1_path_bspline_port_return.get("classification_logs", [])
                if isinstance(b1_path_bspline_port_return.get("classification_logs"), list)
                else [],
                "workspace_package_state_after_012": b1_path_bspline_port_return.get(
                    "workspace_package_state_after_012", {}
                )
                if isinstance(b1_path_bspline_port_return.get("workspace_package_state_after_012"), dict)
                else {},
                "runtime_contract_preserved": b1_path_bspline_port_return.get("runtime_contract_preserved", {})
                if isinstance(b1_path_bspline_port_return.get("runtime_contract_preserved"), dict)
                else {},
                "forbidden_actions_confirmed": b1_path_bspline_port_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_path_bspline_port_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "exact_next_command": b1_path_bspline_port_return.get("exact_next_command", {})
                if isinstance(b1_path_bspline_port_return.get("exact_next_command"), dict)
                else {},
                "claim_boundary": [
                    "012 proves only isolated path_searching and bspline_opt ROS2 build/API surfaces.",
                    "No planner runtime, /planning/bspline, /position_cmd, runtime recorder, or local-map quality claim is made.",
                ],
            },
            "position_command_b1_traj_quadmsgs_port": {
                "status": str(b1_traj_quadmsgs_port_return.get("status", "not_run"))
                if b1_traj_quadmsgs_port_return
                else "not_run",
                "quality_status": b1_traj_quadmsgs_port_return.get("quality_status", "")
                if b1_traj_quadmsgs_port_return
                else "",
                "return_packet": rel(b1_traj_quadmsgs_port_return_path)
                if b1_traj_quadmsgs_port_return
                else "",
                "summary": b1_traj_quadmsgs_port_return.get("summary", {})
                if isinstance(b1_traj_quadmsgs_port_return.get("summary"), dict)
                else {},
                "classification": b1_traj_quadmsgs_port_return.get("classification", {})
                if isinstance(b1_traj_quadmsgs_port_return.get("classification"), dict)
                else {},
                "changed_isolated_files": b1_traj_quadmsgs_port_return.get("changed_isolated_files", [])
                if isinstance(b1_traj_quadmsgs_port_return.get("changed_isolated_files"), list)
                else [],
                "ros2_api_surface_now_present": b1_traj_quadmsgs_port_return.get(
                    "ros2_api_surface_now_present", []
                )
                if isinstance(b1_traj_quadmsgs_port_return.get("ros2_api_surface_now_present"), list)
                else [],
                "build_status": b1_traj_quadmsgs_port_return.get("build_status", {})
                if isinstance(b1_traj_quadmsgs_port_return.get("build_status"), dict)
                else {},
                "installed_artifacts": b1_traj_quadmsgs_port_return.get("installed_artifacts", [])
                if isinstance(b1_traj_quadmsgs_port_return.get("installed_artifacts"), list)
                else [],
                "classification_logs": b1_traj_quadmsgs_port_return.get("classification_logs", [])
                if isinstance(b1_traj_quadmsgs_port_return.get("classification_logs"), list)
                else [],
                "workspace_package_state_after_013": b1_traj_quadmsgs_port_return.get(
                    "workspace_package_state_after_013", {}
                )
                if isinstance(b1_traj_quadmsgs_port_return.get("workspace_package_state_after_013"), dict)
                else {},
                "runtime_contract_preserved": b1_traj_quadmsgs_port_return.get("runtime_contract_preserved", {})
                if isinstance(b1_traj_quadmsgs_port_return.get("runtime_contract_preserved"), dict)
                else {},
                "forbidden_actions_confirmed": b1_traj_quadmsgs_port_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_traj_quadmsgs_port_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "exact_next_command": b1_traj_quadmsgs_port_return.get("exact_next_command", {})
                if isinstance(b1_traj_quadmsgs_port_return.get("exact_next_command"), dict)
                else {},
                "claim_boundary": [
                    "013 proves only isolated quadrotor_msgs and traj_utils ROS2 build/API surfaces.",
                    "No planner runtime, /planning/bspline, /position_cmd, runtime recorder, or local-map quality claim is made.",
                ],
            },
            "position_command_b1_planmanage_link_preflight": {
                "status": str(b1_planmanage_link_preflight_return.get("status", "not_run"))
                if b1_planmanage_link_preflight_return
                else "not_run",
                "quality_status": b1_planmanage_link_preflight_return.get("quality_status", "")
                if b1_planmanage_link_preflight_return
                else "",
                "return_packet": rel(b1_planmanage_link_preflight_return_path)
                if b1_planmanage_link_preflight_return
                else "",
                "summary": b1_planmanage_link_preflight_return.get("summary", {})
                if isinstance(b1_planmanage_link_preflight_return.get("summary"), dict)
                else {},
                "changed_isolated_files": b1_planmanage_link_preflight_return.get("changed_isolated_files", [])
                if isinstance(b1_planmanage_link_preflight_return.get("changed_isolated_files"), list)
                else [],
                "build_status": b1_planmanage_link_preflight_return.get("build_status", {})
                if isinstance(b1_planmanage_link_preflight_return.get("build_status"), dict)
                else {},
                "installed_artifacts": b1_planmanage_link_preflight_return.get("installed_artifacts", [])
                if isinstance(b1_planmanage_link_preflight_return.get("installed_artifacts"), list)
                else [],
                "classification": b1_planmanage_link_preflight_return.get("classification", {})
                if isinstance(b1_planmanage_link_preflight_return.get("classification"), dict)
                else {},
                "evidence_artifacts": b1_planmanage_link_preflight_return.get("evidence_artifacts", [])
                if isinstance(b1_planmanage_link_preflight_return.get("evidence_artifacts"), list)
                else [],
                "runtime_boundary": b1_planmanage_link_preflight_return.get("runtime_boundary", {})
                if isinstance(b1_planmanage_link_preflight_return.get("runtime_boundary"), dict)
                else {},
                "forbidden_actions_confirmed": b1_planmanage_link_preflight_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_planmanage_link_preflight_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "next_allowed_task": b1_planmanage_link_preflight_return.get("next_allowed_task", {})
                if isinstance(b1_planmanage_link_preflight_return.get("next_allowed_task"), dict)
                else {},
                "claim_boundary": [
                    "014 proves only isolated plan_manage/EGOPlannerManager/EGOReplanFSM compile/link preflight.",
                    "No planner runtime, /planning/bspline runtime evidence, /position_cmd, recorder, or closed_loop claim is made.",
                ],
            },
            "position_command_b1_runtime_disabled_launch_audit": {
                "status": str(b1_runtime_disabled_launch_audit_return.get("status", "not_run"))
                if b1_runtime_disabled_launch_audit_return
                else "not_run",
                "quality_status": b1_runtime_disabled_launch_audit_return.get("quality_status", "")
                if b1_runtime_disabled_launch_audit_return
                else "",
                "return_packet": rel(b1_runtime_disabled_launch_audit_return_path)
                if b1_runtime_disabled_launch_audit_return
                else "",
                "summary": b1_runtime_disabled_launch_audit_return.get("summary", {})
                if isinstance(b1_runtime_disabled_launch_audit_return.get("summary"), dict)
                else {},
                "inspected_files": b1_runtime_disabled_launch_audit_return.get("inspected_files", [])
                if isinstance(b1_runtime_disabled_launch_audit_return.get("inspected_files"), list)
                else [],
                "static_or_dry_run_commands": b1_runtime_disabled_launch_audit_return.get(
                    "static_or_dry_run_commands", {}
                )
                if isinstance(b1_runtime_disabled_launch_audit_return.get("static_or_dry_run_commands"), dict)
                else {},
                "topic_remap_contract": b1_runtime_disabled_launch_audit_return.get("topic_remap_contract", {})
                if isinstance(b1_runtime_disabled_launch_audit_return.get("topic_remap_contract"), dict)
                else {},
                "parameter_audit": b1_runtime_disabled_launch_audit_return.get("parameter_audit", {})
                if isinstance(b1_runtime_disabled_launch_audit_return.get("parameter_audit"), dict)
                else {},
                "unresolved_blockers": b1_runtime_disabled_launch_audit_return.get("unresolved_blockers", [])
                if isinstance(b1_runtime_disabled_launch_audit_return.get("unresolved_blockers"), list)
                else [],
                "risks": b1_runtime_disabled_launch_audit_return.get("risks", [])
                if isinstance(b1_runtime_disabled_launch_audit_return.get("risks"), list)
                else [],
                "next_pmo_approval_gate": b1_runtime_disabled_launch_audit_return.get("next_pmo_approval_gate", {})
                if isinstance(b1_runtime_disabled_launch_audit_return.get("next_pmo_approval_gate"), dict)
                else {},
                "evidence_artifacts": b1_runtime_disabled_launch_audit_return.get("evidence_artifacts", [])
                if isinstance(b1_runtime_disabled_launch_audit_return.get("evidence_artifacts"), list)
                else [],
                "forbidden_actions_confirmed": b1_runtime_disabled_launch_audit_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_runtime_disabled_launch_audit_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "claim_boundary": [
                    "015 proves only runtime-disabled launch/static parameter/remap audit readiness.",
                    "No planner runtime, /planning/bspline runtime evidence, /position_cmd, recorder, or closed_loop claim is made.",
                ],
            },
            "position_command_b1_runtime_disabled_launch_config": {
                "status": str(b1_runtime_disabled_launch_config_return.get("status", "not_run"))
                if b1_runtime_disabled_launch_config_return
                else "not_run",
                "quality_status": b1_runtime_disabled_launch_config_return.get("quality_status", "")
                if b1_runtime_disabled_launch_config_return
                else "",
                "return_packet": rel(b1_runtime_disabled_launch_config_return_path)
                if b1_runtime_disabled_launch_config_return
                else "",
                "summary": b1_runtime_disabled_launch_config_return.get("summary", {})
                if isinstance(b1_runtime_disabled_launch_config_return.get("summary"), dict)
                else {},
                "artifact_inventory": b1_runtime_disabled_launch_config_return.get("artifact_inventory", {})
                if isinstance(b1_runtime_disabled_launch_config_return.get("artifact_inventory"), dict)
                else {},
                "config_diff_summary": b1_runtime_disabled_launch_config_return.get("config_diff_summary", {})
                if isinstance(b1_runtime_disabled_launch_config_return.get("config_diff_summary"), dict)
                else {},
                "static_validation_output": b1_runtime_disabled_launch_config_return.get("static_validation_output", {})
                if isinstance(b1_runtime_disabled_launch_config_return.get("static_validation_output"), dict)
                else {},
                "topic_remap_contract": b1_runtime_disabled_launch_config_return.get("topic_remap_contract", {})
                if isinstance(b1_runtime_disabled_launch_config_return.get("topic_remap_contract"), dict)
                else {},
                "unresolved_blockers": b1_runtime_disabled_launch_config_return.get("unresolved_blockers", [])
                if isinstance(b1_runtime_disabled_launch_config_return.get("unresolved_blockers"), list)
                else [],
                "risks": b1_runtime_disabled_launch_config_return.get("risks", [])
                if isinstance(b1_runtime_disabled_launch_config_return.get("risks"), list)
                else [],
                "next_pmo_gate": b1_runtime_disabled_launch_config_return.get("next_pmo_gate", {})
                if isinstance(b1_runtime_disabled_launch_config_return.get("next_pmo_gate"), dict)
                else {},
                "forbidden_actions_confirmed": b1_runtime_disabled_launch_config_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_runtime_disabled_launch_config_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "claim_boundary": [
                    "016 proves only guarded runtime-disabled launch/config artifact creation and static validation.",
                    "No ros2 launch/run, planner runtime, /planning/bspline runtime evidence, /position_cmd, recorder, or closed_loop claim is made.",
                ],
            },
            "position_command_b1_runtime_disabled_smoke": {
                "status": str(b1_runtime_disabled_smoke_return.get("status", "not_run"))
                if b1_runtime_disabled_smoke_return
                else "not_run",
                "quality_status": b1_runtime_disabled_smoke_return.get("quality_status", "")
                if b1_runtime_disabled_smoke_return
                else "",
                "return_packet": rel(b1_runtime_disabled_smoke_return_path)
                if b1_runtime_disabled_smoke_return
                else "",
                "summary": b1_runtime_disabled_smoke_return.get("summary", {})
                if isinstance(b1_runtime_disabled_smoke_return.get("summary"), dict)
                else {},
                "runtime_disabled_smoke": b1_runtime_disabled_smoke_return.get("runtime_disabled_smoke", {})
                if isinstance(b1_runtime_disabled_smoke_return.get("runtime_disabled_smoke"), dict)
                else {},
                "evidence_artifacts": b1_runtime_disabled_smoke_return.get("evidence_artifacts", [])
                if isinstance(b1_runtime_disabled_smoke_return.get("evidence_artifacts"), list)
                else [],
                "forbidden_actions_confirmed": b1_runtime_disabled_smoke_return.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_runtime_disabled_smoke_return.get("forbidden_actions_confirmed"), dict)
                else {},
                "unresolved_blockers": b1_runtime_disabled_smoke_return.get("unresolved_blockers", [])
                if isinstance(b1_runtime_disabled_smoke_return.get("unresolved_blockers"), list)
                else [],
                "risks": b1_runtime_disabled_smoke_return.get("risks", [])
                if isinstance(b1_runtime_disabled_smoke_return.get("risks"), list)
                else [],
                "next_pmo_gate": b1_runtime_disabled_smoke_return.get("next_pmo_gate", {})
                if isinstance(b1_runtime_disabled_smoke_return.get("next_pmo_gate"), dict)
                else {},
                "claim_boundary": [
                    "017 proves only bounded runtime-disabled guard smoke with clean early exit.",
                    "No planner runtime acceptance, /planning/bspline runtime evidence, /position_cmd, recorder, or closed_loop claim is made.",
                ],
            },
            "position_command_b1_real_planner_input_gate": {
                "status": str(b1_real_planner_input_gate_blocker.get("status", "not_run"))
                if b1_real_planner_input_gate_blocker
                else "not_run",
                "quality_status": b1_real_planner_input_gate_blocker.get("quality_status", "")
                if b1_real_planner_input_gate_blocker
                else "",
                "blocker_packet": rel(b1_real_planner_input_gate_blocker_path)
                if b1_real_planner_input_gate_blocker
                else "",
                "summary": b1_real_planner_input_gate_blocker.get("summary", {})
                if isinstance(b1_real_planner_input_gate_blocker.get("summary"), dict)
                else {},
                "real_odometry_present_now": (
                    b1_real_planner_input_gate_blocker.get("summary", {}).get("real_odometry_present_now")
                    if isinstance(b1_real_planner_input_gate_blocker.get("summary"), dict)
                    else None
                ),
                "real_cloud_registered_present_now": (
                    b1_real_planner_input_gate_blocker.get("summary", {}).get("real_cloud_registered_present_now")
                    if isinstance(b1_real_planner_input_gate_blocker.get("summary"), dict)
                    else None
                ),
                "runtime_disabled_false_may_be_safely_attempted_later": (
                    b1_real_planner_input_gate_blocker.get("summary", {}).get(
                        "runtime_disabled_false_may_be_safely_attempted_later"
                    )
                    if isinstance(b1_real_planner_input_gate_blocker.get("summary"), dict)
                    else None
                ),
                "topic_availability_rate_type_probe": b1_real_planner_input_gate_blocker.get(
                    "topic_availability_rate_type_probe", {}
                )
                if isinstance(b1_real_planner_input_gate_blocker.get("topic_availability_rate_type_probe"), dict)
                else {},
                "planner_startup_surface_probe": b1_real_planner_input_gate_blocker.get(
                    "planner_startup_surface_probe", {}
                )
                if isinstance(b1_real_planner_input_gate_blocker.get("planner_startup_surface_probe"), dict)
                else {},
                "gate_decision": b1_real_planner_input_gate_blocker.get("gate_decision", {})
                if isinstance(b1_real_planner_input_gate_blocker.get("gate_decision"), dict)
                else {},
                "unresolved_blockers": b1_real_planner_input_gate_blocker.get("unresolved_blockers", [])
                if isinstance(b1_real_planner_input_gate_blocker.get("unresolved_blockers"), list)
                else [],
                "next_pmo_gate": b1_real_planner_input_gate_blocker.get("next_pmo_gate", {})
                if isinstance(b1_real_planner_input_gate_blocker.get("next_pmo_gate"), dict)
                else {},
                "forbidden_actions_confirmed": b1_real_planner_input_gate_blocker.get(
                    "forbidden_actions_confirmed", {}
                )
                if isinstance(b1_real_planner_input_gate_blocker.get("forbidden_actions_confirmed"), dict)
                else {},
                "claim_boundary": [
                    "018 proves only that current real planner inputs are absent.",
                    "No runtime_disabled=false planner startup, PositionCommand recorder, /position_cmd, /planning/bspline runtime evidence, planner acceptance, or closed_loop claim is made.",
                ],
            },
            "position_command_b1_odom_cloud_restore": {
                "status": str(b1_odom_cloud_restore_return.get("status", "not_run"))
                if b1_odom_cloud_restore_return
                else "not_run",
                "quality_status": b1_odom_cloud_restore_return.get("quality_status", "")
                if b1_odom_cloud_restore_return
                else "",
                "return_packet": rel(b1_odom_cloud_restore_return_path)
                if b1_odom_cloud_restore_return
                else "",
                "evidence_dir": b1_odom_cloud_restore_return.get("evidence_dir", "")
                if b1_odom_cloud_restore_return
                else "",
                "summary_json": rel(b1_odom_cloud_summary_path) if b1_odom_cloud_summary_path else "",
                "ready_for_later_separate_runtime_disabled_false_startup_probe": bool(
                    as_mapping(b1_odom_cloud_restore_return.get("summary")).get(
                        "ready_for_later_separate_runtime_disabled_false_startup_probe",
                        as_mapping(b1_odom_cloud_summary.get("decision")).get(
                            "ready_for_later_separate_runtime_disabled_false_startup_probe", False
                        ),
                    )
                ),
                "planner_ready": bool(
                    as_mapping(b1_odom_cloud_restore_return.get("summary")).get(
                        "planner_ready", as_mapping(b1_odom_cloud_summary.get("decision")).get("planner_ready", False)
                    )
                ),
                "closed_loop_ready": bool(
                    as_mapping(b1_odom_cloud_restore_return.get("summary")).get(
                        "closed_loop_ready",
                        as_mapping(b1_odom_cloud_summary.get("decision")).get("closed_loop_ready", False),
                    )
                ),
                "position_command_recorder_allowed": bool(
                    as_mapping(b1_odom_cloud_restore_return.get("summary")).get(
                        "position_command_recorder_allowed",
                        as_mapping(b1_odom_cloud_summary.get("decision")).get("recorder_allowed_now", False),
                    )
                ),
                "planner_startup_executed": bool(
                    as_mapping(b1_odom_cloud_restore_return.get("summary")).get("planner_startup_executed", False)
                ),
                "required_topics": as_mapping(b1_odom_cloud_summary.get("required_topics")),
                "input_source_probe": as_mapping(b1_odom_cloud_summary.get("input_source_probe")),
                "truth_evaluation": as_mapping(b1_odom_cloud_summary.get("truth_evaluation")),
                "live_graph_sampling": as_mapping(b1_odom_cloud_summary.get("live_graph_sampling")),
                "planner_startup_gate": as_mapping(b1_odom_cloud_restore_return.get("planner_startup_gate")),
                "forbidden_actions_confirmed": as_mapping(
                    b1_odom_cloud_restore_return.get("forbidden_actions_confirmed")
                ),
                "unresolved_blockers": as_list(b1_odom_cloud_restore_return.get("unresolved_blockers")),
                "next_pmo_gate": as_mapping(b1_odom_cloud_restore_return.get("next_pmo_gate")),
                "claim_boundary": [
                    "019 restores and measures real FAST-LIO/equivalent /Odometry and /cloud_registered only.",
                    "No runtime_disabled=false planner startup, PositionCommand recorder, /position_cmd, /planning/bspline acceptance, planner_ready, or closed_loop_ready claim is made.",
                ],
            },
            "position_command_b1_planner_startup_probe": {
                "status": str(b1_planner_startup_probe_blocker.get("status", "not_run"))
                if b1_planner_startup_probe_blocker
                else "not_run",
                "quality_status": b1_planner_startup_probe_blocker.get("quality_status", "")
                if b1_planner_startup_probe_blocker
                else "",
                "blocker_packet": rel(b1_planner_startup_probe_blocker_path)
                if b1_planner_startup_probe_blocker
                else "",
                "evidence_dir": b1_planner_startup_probe_blocker.get("evidence_dir", "")
                if b1_planner_startup_probe_blocker
                else "",
                "summary": as_mapping(b1_planner_startup_probe_blocker.get("summary")),
                "fresh_restore_evidence": as_mapping(
                    b1_planner_startup_probe_blocker.get("fresh_restore_evidence")
                ),
                "planner_startup_probe": as_mapping(
                    b1_planner_startup_probe_blocker.get("planner_startup_probe")
                ),
                "cleanup_evidence": as_mapping(b1_planner_startup_probe_blocker.get("cleanup_evidence")),
                "unresolved_blockers": as_list(b1_planner_startup_probe_blocker.get("unresolved_blockers")),
                "unknowns_and_risks": as_list(b1_planner_startup_probe_blocker.get("unknowns_and_risks")),
                "next_pmo_gate": as_mapping(b1_planner_startup_probe_blocker.get("next_pmo_gate")),
                "forbidden_actions_confirmed": as_mapping(
                    b1_planner_startup_probe_blocker.get("forbidden_actions_confirmed")
                ),
                "planner_ready": bool(
                    as_mapping(b1_planner_startup_probe_blocker.get("summary")).get("planner_ready", False)
                ),
                "closed_loop_ready": bool(
                    as_mapping(b1_planner_startup_probe_blocker.get("summary")).get("closed_loop_ready", False)
                ),
                "position_command_recorder_allowed": bool(
                    as_mapping(b1_planner_startup_probe_blocker.get("summary")).get(
                        "position_command_recorder_allowed", False
                    )
                ),
                "claim_boundary": [
                    "020 proves only a bounded planner startup surface after fresh odom/cloud restore.",
                    "Input consumption was not accepted; /planning/bspline topic-list appearance is not trajectory evidence.",
                    "No /position_cmd, recorder, planner_ready, closed_loop, local-map quality, mission success, or controller performance claim is made.",
                ],
            },
        },
        "planner": {
            "map_source": "fast_lio_localization_slice_no_planner_map_claim",
            "global_truth_used_as_input": False,
            "setpoint_trace_source": "RUNTIME_20HZ_ADAPTER",
            "setpoint_adapter_status": "pass" if adapter.get("pass") is True else "needs_iteration",
            "setpoint_trace": rel(setpoint_trace_path),
            "setpoint_rate_hz": 20.0,
            "stale_command_timeout_s": 0.15,
            "adapter_smoke_json": rel(project_path(args.adapter_smoke)),
            "position_command_adapter_smoke_json": (
                rel(project_path(args.position_adapter_smoke)) if args.position_adapter_smoke else ""
            ),
        },
        "ue": {
            "scene_registry_ref": "UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json",
            "sensor_oracle_log": gate_paths.get("livox_frames", ""),
            "command_echo_log": rel(project_path(args.ue_command_echo)),
            "command_adapter_smoke_json": rel(project_path(args.ue_command_adapter_smoke)),
            "command_input_log": rel(project_path(args.ue_command_input)),
            "command_sender_source": "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp",
            "command_sender_header": "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h",
            "command_sender_contract": rel(project_path(args.ue_command_sender_contract)),
            "command_sender_source_status": "source_level_static_check_pass",
            "command_sender_loopback_smoke_json": rel(project_path(args.ue_command_sender_loopback_smoke)),
            "command_sender_loopback_received": rel(project_path(args.ue_command_sender_loopback_received)),
            "command_sender_loopback_source": "udp_loopback_smoke",
            "command_echo_source": "offline_adapter_smoke",
            "not_runtime_ue_console": True,
            "no_pose_overwrite_status": "pass",
        },
        "gate_results": {
            "required_checks": [
                "MWORKS smoke evidence source-labeled",
                "Factory FAST-LIO Gate B current-pass",
                "ROS2 setpoint adapter no-RViz smoke pass",
                "RUN_MANIFEST checker pass for slice scope",
            ],
            "warnings": [
                "claim_scope intentionally excludes planner and closed_loop until real planner/MWORKS binding exists",
                "B0 PositionCommand contract replay is smoke-only and lacks real local-map/odom planner input",
                "B1 unblock restored current FAST-LIO odom/cloud/path evidence, but planner runtime and sustained real PositionCommand source are still missing",
                "B1 planner-wrapper task 006 selected EGO/Sunray/FUEL as semantic candidates but remains blocked by ROS1/catkin versus current ROS2 overlay/runtime availability",
                "B1 port preflight task 007 completed classification only: real planner runtime is not ready and /position_cmd recorder must not run yet",
                "B1 message-port task 008 built isolated ego_planner_msgs messages, but planner node logic and runtime /position_cmd source remain absent",
                "B1 planner-node preflight task 009 built an isolated traj_server ROS2 stub, but no planner runtime was launched and runtime recorder remains forbidden",
                "B1 upstream planner-deps task 010 identified EGOReplanFSM as the /planning/bspline producer but plan_env/GridMap remains ROS1/catkin-only",
                "B1 plan_env/GridMap port task 011 made isolated plan_env ROS2-buildable, but this is build/API surface only and path_searching/bspline_opt still block EGOReplanFSM runtime",
                "B1 path_searching/bspline_opt port task 012 made isolated path_searching and bspline_opt ROS2-buildable, but traj_utils/quadrotor_msgs and plan_manage runtime still block EGOReplanFSM runtime",
                "B1 traj_utils/quadrotor_msgs port task 013 made isolated support/message surfaces ROS2-buildable, but full plan_manage runtime still blocks EGOReplanFSM runtime",
                "B1 plan_manage link preflight task 014 made isolated EGOPlannerManager/EGOReplanFSM/planner entrypoint compile-link surfaces buildable, but no planner runtime or recorder was launched",
                "B1 runtime-disabled launch audit task 015 completed static parameter/remap audit, but no runtime-disabled guard launch/config artifact exists yet and real planner runtime remains blocked",
                "B1 runtime-disabled launch/config task 016 created and installed guarded launch/config artifacts, but no ros2 launch/run, planner runtime, recorder, /position_cmd, or /planning/bspline runtime evidence is claimed",
                "B1 runtime-disabled smoke task 017 launched only the guarded disabled path and exited before EGOReplanFSM init; planner runtime, recorder, /position_cmd, /planning/bspline, and closed_loop remain blocked",
                "B1 real planner input gate task 018 remains historical blocker evidence for the earlier missing /Odometry and /cloud_registered live graph",
                "B1 odom/cloud restore task 019 restored real /Odometry and /cloud_registered at about 9Hz with primary truth eval pass, clearing only the input-source precondition for a later separate runtime_disabled=false startup probe",
                "B1 planner startup probe task 020 fresh-restored odom/cloud and started the runtime_disabled=false planner surface, but input consumption was not accepted because planner logs repeated no odom and topic info showed zero /Odometry and /cloud_registered publishers during the planner window",
                "MWORKS trace wrapper check_model passed in a delegated attempt, but trace consumption is blocked because simulation/result binding produced empty/zero reference outputs",
                "MWORKS standalone trace lookup diagnostic 003 passed and narrows the remaining failure to Factory wrapper integration/result context",
                "MWORKS Factory trace reconnect task 004 added wrapper aliases and check_model passed, but SimulateModel/result binding stayed blocked with zero aliases and empty times",
                "MWORKS Factory-lite trace probe task 005 passed, proving TraceInlineReference plus PlanningNavigationDisplay result binding works before full plant/controller reconnect",
                "MWORKS incremental trace isolation task 006 found Iso04 controller feedback plus motor-command wiring as the first SimulateModel failure boundary; no Factory trace consumption claim",
                "MWORKS actuator wiring isolation task 007 fixed Iso04 duplicate actuator input sources and removed 6140, but clean sensor-feedback controller closure still fails with empty result context",
                "MWORKS sensor feedback isolation task 008 found roll/pitch AngleMea[1..2] feedback as the first empty-result boundary; position feedback alone passed",
                "MWORKS attitude feedback isolation task 009 found direct single-channel AngleMea feedback to Sysblock inports fails with empty result context; sign inversion does not fix it",
                "MWORKS attitude intermediary task 010 classified the blocker as AbsoluteAngles/AngleMea dependency coupling: constant/table attitude inputs pass, RealExpression depending on AngleMea fails",
                "MWORKS attitude decoupling task 011 restored result context with sampled/held and project-owned first-order extraction probes, but still claims no closed_loop or Factory trace consumption",
                "MWORKS pitch decoupling task 012 confirmed the project-owned first-order extraction pattern scales from roll-only to roll+pitch result-context stability, but still claims no closed_loop or Factory trace consumption",
                "MWORKS yaw decoupling task 013 confirmed the project-owned first-order extraction pattern scales to yaw attitude result-context stability, but rate feedback, full sensor bus, Factory trace consumption, and closed_loop remain open",
                "MWORKS rate-feedback isolation task 014 confirmed rate aliases preserve result context, but no external gyro/rate feedback controller claim, Factory trace consumption, or closed_loop is made",
                "MWORKS sensor-bus reconnect task 015 found direct sensors1_1.PosMea -> navigationDisplay.actual_position reconnect passes check_model but fails SimulateModel with error 6140 and empty result context",
                "MWORKS position bridge task 016 confirmed sampled/held PosMea display bridge restores result context and removes 6140 for the narrow display-position bridge only; full Factory trace consumption and closed_loop remain blocked",
                "MWORKS next sensor/display group task 017 found no remaining allowed sensor/display reconnect group after Iso23; next task must permit one controller/control-feedback group",
                "MWORKS first controller/control-feedback group task 018 found direct AngleMea attitude feedback clears result context after Iso23",
                "MWORKS attitude-feedback bridge task 019 confirmed sampled/held AngleMea feedback restores result context for the narrow controller measurement bridge only; full Factory trace consumption and downstream control-output/actuator groups remain open",
                "UE command sender UDP loopback smoke passes packet transport only; live MWORKS/ROS2 ack remains open",
                "UE Bridge now has a source-level UDP command sender contract, but no live MWORKS/ROS2 runtime ack is claimed",
                "UE command adapter smoke emits accepted/rejected echo rows offline, but no live UE command sender or MWORKS/ROS2 runtime ack is implemented",
            ],
            "failures": [],
        },
    }

    command_input = project_path(args.ue_command_input)
    command_input.parent.mkdir(parents=True, exist_ok=True)
    command_input.write_text(
        "\n".join(
            json.dumps(item, ensure_ascii=False, separators=(",", ":"))
            for item in [
                {
                    "schema": "mosim.ue_command.v1",
                    "type": "command",
                    "run_id": args.run_id,
                    "request_id": "ue_smoke_controller_select_001",
                    "seq": 1,
                    "time_s": 0.0,
                    "requested_by": "ue_experiment_console",
                    "command": {"kind": "controller_select", "payload": {"controller_id": "linear_mpc_sysblock"}},
                    "guard": {"require_mworks_ack": True, "require_ros2_ack": False, "reject_if_gate_open": []},
                },
                {
                    "schema": "mosim.ue_command.v1",
                    "type": "command",
                    "run_id": args.run_id,
                    "request_id": "ue_smoke_planner_select_002",
                    "seq": 2,
                    "time_s": 0.05,
                    "requested_by": "ue_experiment_console",
                    "command": {"kind": "planner_select", "payload": {"planner_id": "ego_replan_fsm_candidate"}},
                    "guard": {"require_mworks_ack": True, "require_ros2_ack": True, "reject_if_gate_open": []},
                },
                {
                    "schema": "mosim.ue_command.v1",
                    "type": "command",
                    "run_id": args.run_id,
                    "request_id": "ue_smoke_teleport_reject_003",
                    "seq": 3,
                    "time_s": 0.1,
                    "requested_by": "ue_experiment_console",
                    "command": {"kind": "teleport", "payload": {"x": 1.0}},
                    "guard": {"require_mworks_ack": True, "require_ros2_ack": False, "reject_if_gate_open": []},
                },
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    command_echo = project_path(args.ue_command_echo)
    command_adapter_smoke = project_path(args.ue_command_adapter_smoke)
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "UE5" / "smoke_ue_command_adapter.py"),
            "--commands",
            str(command_input),
            "--echo-output",
            str(command_echo),
            "--summary-output",
            str(command_adapter_smoke),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    source_contract = project_path(args.ue_command_sender_contract)
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "UE5" / "check_ue_command_sender_contract.py"),
            "--output-json",
            str(source_contract),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    loopback_summary = project_path(args.ue_command_sender_loopback_smoke)
    loopback_received = project_path(args.ue_command_sender_loopback_received)
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "UE5" / "smoke_ue_command_sender_loopback.py"),
            "--summary-output",
            str(loopback_summary),
            "--received-output",
            str(loopback_received),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    return manifest


def validate_manifest(manifest_path: Path, report_path: Path) -> int:
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(manifest_path), "--output-json", str(report_path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="rfly_mosim_p0_slice_20260606")
    parser.add_argument(
        "--output-dir",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606",
    )
    parser.add_argument(
        "--realstack-gate",
        default="Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate_current.json",
    )
    parser.add_argument(
        "--mworks-metrics",
        default=(
            "Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/metrics/"
            "sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.json"
        ),
    )
    parser.add_argument(
        "--adapter-smoke",
        default="Results/tmp/mosim_setpoint_adapter_smoke.json",
    )
    parser.add_argument(
        "--position-adapter-smoke",
        default="Results/tmp/mosim_position_command_adapter_smoke.json",
    )
    parser.add_argument(
        "--positioncmd-b0-run-summary",
        default=(
            "Results/ros2_runtime/positioncmd_b0_contract_replay_orchestrated_20260606_pass/"
            "run_summary.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-blocker",
        default="Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-20260606-004.json",
    )
    parser.add_argument(
        "--positioncmd-b1-unblock-blocker",
        default="Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-UNBLOCK-20260606-005.json",
    )
    parser.add_argument(
        "--positioncmd-b1-planner-wrapper-blocker",
        default="Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-WRAPPER-20260606-006.json",
    )
    parser.add_argument(
        "--positioncmd-b1-port-preflight-return",
        default="Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-PORT-PREFLIGHT-20260606-007.json",
    )
    parser.add_argument(
        "--positioncmd-b1-msg-port-slice-return",
        default="Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-MSG-PORT-SLICE-20260606-008.json",
    )
    parser.add_argument(
        "--positioncmd-b1-planner-node-port-return",
        default="Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-NODE-PORT-PREFLIGHT-20260606-009.json",
    )
    parser.add_argument(
        "--positioncmd-b1-upstream-planner-deps-blocker",
        default=(
            "Results/agent_packets/blockers/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-UPSTREAM-PLANNER-DEPS-20260606-010.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-planenv-gridmap-port-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANENV-GRIDMAP-PORT-20260606-011.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-path-bspline-port-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-PATH-BSPLINE-PORT-20260606-012.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-traj-quadmsgs-port-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-TRAJ-QUADMSGS-PORT-20260606-013.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-planmanage-link-preflight-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANMANAGE-LINK-PREFLIGHT-20260606-014.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-runtime-disabled-launch-audit-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-runtime-disabled-launch-config-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-runtime-disabled-smoke-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-SMOKE-20260606-017.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-real-planner-input-gate-blocker",
        default=(
            "Results/agent_packets/blockers/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-odom-cloud-restore-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019.json"
        ),
    )
    parser.add_argument(
        "--positioncmd-b1-planner-startup-probe-blocker",
        default=(
            "Results/agent_packets/blockers/"
            "RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-STARTUP-PROBE-20260606-020.json"
        ),
    )
    parser.add_argument(
        "--mworks-trace-blocker",
        default="Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json",
    )
    parser.add_argument(
        "--mworks-trace-lookup-return",
        default="Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json",
    )
    parser.add_argument(
        "--mworks-factory-trace-reconnect-blocker",
        default="Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004.json",
    )
    parser.add_argument(
        "--mworks-factory-lite-trace-return",
        default="Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-LITE-TRACE-20260606-005.json",
    )
    parser.add_argument(
        "--mworks-incremental-trace-isolation-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json"
        ),
    )
    parser.add_argument(
        "--mworks-actuator-wiring-isolation-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json"
        ),
    )
    parser.add_argument(
        "--mworks-sensor-feedback-isolation-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json"
        ),
    )
    parser.add_argument(
        "--mworks-attitude-feedback-isolation-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json"
        ),
    )
    parser.add_argument(
        "--mworks-attitude-intermediary-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json"
        ),
    )
    parser.add_argument(
        "--mworks-attitude-decoupling-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json"
        ),
    )
    parser.add_argument(
        "--mworks-pitch-decoupling-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-PITCH-DECOUPLING-20260606-012.json"
        ),
    )
    parser.add_argument(
        "--mworks-yaw-rate-decoupling-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json"
        ),
    )
    parser.add_argument(
        "--mworks-rate-feedback-isolation-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json"
        ),
    )
    parser.add_argument(
        "--mworks-sensor-bus-reconnect-blocker",
        default=(
            "Results/agent_packets/blockers/"
            "RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json"
        ),
    )
    parser.add_argument(
        "--mworks-position-bridge-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json"
        ),
    )
    parser.add_argument(
        "--mworks-next-sensor-display-group-blocker",
        default=(
            "Results/agent_packets/blockers/"
            "RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017.json"
        ),
    )
    parser.add_argument(
        "--mworks-first-control-feedback-group-blocker",
        default=(
            "Results/agent_packets/blockers/"
            "RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018.json"
        ),
    )
    parser.add_argument(
        "--mworks-attitude-feedback-bridge-return",
        default=(
            "Results/agent_packets/returns/"
            "RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json"
        ),
    )
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    output_dir = project_path(args.output_dir)
    args.manifest = output_dir / "RUN_MANIFEST.json"
    args.validation_report = output_dir / "RUN_MANIFEST.validation.json"
    args.setpoint_trace = output_dir / "setpoint_trace_smoke.csv"
    args.ue_command_input = output_dir / "ue_command_input_smoke.jsonl"
    args.ue_command_echo = output_dir / "ue_command_echo_smoke.jsonl"
    args.ue_command_adapter_smoke = output_dir / "ue_command_adapter_smoke.json"
    args.ue_command_sender_contract = output_dir / "ue_command_sender_source_contract.json"
    args.ue_command_sender_loopback_smoke = output_dir / "ue_command_sender_loopback_smoke.json"
    args.ue_command_sender_loopback_received = output_dir / "ue_command_sender_loopback_received.jsonl"
    return args


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args)
    write_json(args.manifest, manifest)
    print(json.dumps({"manifest": rel(args.manifest), "run_id": args.run_id}, ensure_ascii=False))
    if args.validate:
        return validate_manifest(args.manifest, args.validation_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
