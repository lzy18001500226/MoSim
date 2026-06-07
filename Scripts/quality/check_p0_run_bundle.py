#!/usr/bin/env python3
"""Audit a P0 MoSim RUN_MANIFEST bundle beyond schema-level checks.

This verifier is intentionally stricter about evidence paths and honest claim
boundaries than ``check_run_manifest.py``.  It does not decide controller
performance; it checks whether the bundle is recoverable and whether current
blockers are represented instead of hidden.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


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


def as_int(value: Any, default: int = -1) -> int:
    if value in {None, ""}:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def path_exists(value: Any) -> bool:
    if value in {None, ""}:
        return False
    return repo_path(value).exists()


def require_path(report: dict[str, Any], label: str, value: Any, *, required: bool = True) -> None:
    item = {"label": label, "path": str(value or ""), "exists": path_exists(value)}
    report["path_checks"].append(item)
    if required and not item["exists"]:
        report["issues"].append(f"missing required path: {label}={value or '<empty>'}")


def run_json_checker(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        data = {
            "ok": False,
            "issues": [f"checker did not return JSON: {completed.stdout[:400]} {completed.stderr[:400]}"],
            "warnings": [],
        }
    data["_returncode"] = completed.returncode
    if completed.stderr:
        data["_stderr"] = completed.stderr[-1000:]
    return data


def audit_bundle(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    report: dict[str, Any] = {
        "schema": "mosim.p0_run_bundle_audit.v1",
        "manifest": rel(manifest_path),
        "run_id": str(manifest.get("run_id", "")),
        "quality_status": str(manifest.get("quality_status", "")),
        "claim_scope": as_list(manifest.get("claim_scope")),
        "ok": False,
        "issues": [],
        "warnings": [],
        "path_checks": [],
        "manual_review": {},
    }

    blockers = as_list(manifest.get("blockers"))
    if report["quality_status"] == "pass" and blockers:
        report["issues"].append("quality_status=pass cannot have active blockers")
    if report["quality_status"] != "pass" and not blockers:
        report["issues"].append("non-pass P0 bundle must preserve explicit blockers")

    claim_scope_text = " ".join(str(item) for item in report["claim_scope"])
    if "planner" in claim_scope_text or "closed_loop" in claim_scope_text:
        report["issues"].append("P0 bundle audit expected current slice to exclude planner/closed_loop until B1 and MWORKS consumption pass")

    require_path(report, "manifest", rel(manifest_path))

    mworks = as_mapping(manifest.get("mworks"))
    require_path(report, "mworks.raw_csv", mworks.get("raw_csv"))
    require_path(report, "mworks.metrics_json", mworks.get("metrics_json"))
    trace_status = str(mworks.get("setpoint_trace_consumption_status", ""))
    if trace_status == "pass":
        require_path(report, "mworks.consumed_setpoint_trace", mworks.get("consumed_setpoint_trace"))
        require_path(report, "mworks.trace_consumption_evidence", mworks.get("trace_consumption_evidence"))
    else:
        require_path(report, "mworks.trace_consumption_blocker", mworks.get("trace_consumption_blocker"))
        if mworks.get("consumed_setpoint_trace") or mworks.get("trace_consumption_evidence"):
            report["issues"].append("blocked MWORKS trace consumption must not expose consumed trace/evidence paths")
    trace_lookup = as_mapping(mworks.get("trace_lookup_diagnostic"))
    if trace_lookup:
        require_path(report, "mworks.trace_lookup_diagnostic.return_packet", trace_lookup.get("return_packet"))
        require_path(report, "mworks.trace_lookup_diagnostic.probe_json", trace_lookup.get("probe_json"))
        require_path(
            report,
            "mworks.trace_lookup_diagnostic.raw_reference_series_csv",
            trace_lookup.get("raw_reference_series_csv"),
        )
        if trace_lookup.get("quality_status") == "diagnostic_pass":
            report["warnings"].append("MWORKS standalone trace lookup passed, but Factory wrapper trace consumption remains blocked")
        if trace_lookup.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("trace lookup diagnostic cannot be promoted to pass while trace consumption is blocked")
    factory_reconnect = as_mapping(mworks.get("factory_trace_reconnect"))
    if factory_reconnect:
        require_path(report, "mworks.factory_trace_reconnect.blocker_packet", factory_reconnect.get("blocker_packet"))
        require_path(report, "mworks.factory_trace_reconnect.probe_json", factory_reconnect.get("probe_json"))
        if factory_reconnect.get("status") == "blocked":
            report["warnings"].append("MWORKS Factory trace reconnect is blocked: aliases remain zero and result times are empty")
        if factory_reconnect.get("nonzero_alias_refs") is True and trace_status != "pass":
            report["issues"].append("Factory reconnect reports nonzero aliases but trace consumption status is still blocked; rerun manifest gate")
    factory_lite = as_mapping(mworks.get("factory_lite_trace_probe"))
    if factory_lite:
        require_path(report, "mworks.factory_lite_trace_probe.return_packet", factory_lite.get("return_packet"))
        require_path(report, "mworks.factory_lite_trace_probe.probe_json", factory_lite.get("probe_json"))
        require_path(report, "mworks.factory_lite_trace_probe.raw_alias_series_csv", factory_lite.get("raw_alias_series_csv"))
        if factory_lite.get("quality_status") == "factory_lite_trace_probe_pass":
            report["warnings"].append("MWORKS Factory-lite trace probe passed, but full Factory wrapper and closed_loop remain blocked")
        if factory_lite.get("nonzero_alias_refs") is True and trace_status == "pass":
            report["issues"].append("unexpected state: Factory-lite probe should not be equivalent to full trace consumption pass")
    incremental = as_mapping(mworks.get("incremental_trace_isolation"))
    if incremental:
        require_path(report, "mworks.incremental_trace_isolation.return_packet", incremental.get("return_packet"))
        require_path(report, "mworks.incremental_trace_isolation.probe_json", incremental.get("probe_json"))
        require_path(report, "mworks.incremental_trace_isolation.probe_summary_csv", incremental.get("probe_summary_csv"))
        boundary = as_mapping(incremental.get("first_failure_boundary"))
        if incremental.get("quality_status") == "isolation_boundary_found":
            report["warnings"].append("MWORKS incremental trace isolation found Iso04 controller/actuator wiring as the first SimulateModel failure boundary")
        if boundary.get("probe_id") != "iso04_controller_plant_wiring":
            report["issues"].append("incremental trace isolation must preserve the first failure boundary probe id")
        if boundary.get("failure_kind") != "simulate_failed_after_check_pass":
            report["issues"].append("incremental trace isolation failure kind must remain simulate_failed_after_check_pass")
        if incremental.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("incremental isolation cannot be promoted to pass while trace consumption remains blocked")
    actuator = as_mapping(mworks.get("actuator_wiring_isolation"))
    if actuator:
        require_path(report, "mworks.actuator_wiring_isolation.return_packet", actuator.get("return_packet"))
        require_path(report, "mworks.actuator_wiring_isolation.probe_json", actuator.get("probe_json"))
        require_path(report, "mworks.actuator_wiring_isolation.probe_summary_csv", actuator.get("probe_summary_csv"))
        refined = as_mapping(actuator.get("refined_boundary"))
        probes = as_list(actuator.get("derivative_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        if actuator.get("quality_status") == "topology_boundary_refined":
            report["warnings"].append("MWORKS actuator wiring isolation fixed duplicate actuator inputs and removed 6140, but sensor-feedback closure remains blocked")
        if "duplicate actuator input" not in str(refined.get("cause", "")):
            report["issues"].append("actuator wiring isolation must preserve duplicate actuator input as the resolved 6140 cause")
        if "sensor-feedback" not in str(refined.get("remaining_boundary", "")):
            report["issues"].append("actuator wiring isolation must preserve sensor-feedback closure as the remaining boundary")
        if probe_by_id.get("iso05_clean_hover_sum", {}).get("simulate_model") != "pass":
            report["issues"].append("actuator wiring isolation must preserve Iso05 clean hover-sum pass")
        if probe_by_id.get("iso06_clean_sensor_feedback_controller", {}).get("simulate_model") != "failed":
            report["issues"].append("actuator wiring isolation must preserve Iso06 sensor-feedback failure")
        if probe_by_id.get("iso07_clean_open_feedback_controller", {}).get("simulate_model") != "pass":
            report["issues"].append("actuator wiring isolation must preserve Iso07 open-feedback pass")
        if actuator.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("actuator wiring isolation cannot be promoted to pass while trace consumption remains blocked")
    sensor_feedback = as_mapping(mworks.get("sensor_feedback_isolation"))
    if sensor_feedback:
        require_path(report, "mworks.sensor_feedback_isolation.return_packet", sensor_feedback.get("return_packet"))
        require_path(report, "mworks.sensor_feedback_isolation.probe_json", sensor_feedback.get("probe_json"))
        require_path(report, "mworks.sensor_feedback_isolation.probe_summary_csv", sensor_feedback.get("probe_summary_csv"))
        boundary = as_mapping(sensor_feedback.get("first_failure_boundary"))
        probes = as_list(sensor_feedback.get("feedback_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        if sensor_feedback.get("quality_status") == "first_sensor_feedback_boundary_found":
            report["warnings"].append("MWORKS sensor-feedback isolation found roll/pitch AngleMea feedback as the first empty-result boundary")
        if probe_by_id.get("iso08_position_feedback", {}).get("simulate_model") != "pass":
            report["issues"].append("sensor feedback isolation must preserve Iso08 position-feedback pass")
        if probe_by_id.get("iso09_position_attitude_feedback", {}).get("simulate_model") != "failed":
            report["issues"].append("sensor feedback isolation must preserve Iso09 position+attitude feedback failure")
        if probe_by_id.get("iso09_position_attitude_feedback", {}).get("error_6140_present") is not False:
            report["issues"].append("sensor feedback isolation must preserve that error 6140 stayed absent")
        if "roll/pitch" not in str(boundary.get("feedback_group", "")):
            report["issues"].append("sensor feedback isolation must preserve roll/pitch attitude feedback as first failure group")
        if boundary.get("failure_kind") != "simulate_failed_empty_result_context":
            report["issues"].append("sensor feedback isolation failure kind must remain simulate_failed_empty_result_context")
        if sensor_feedback.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("sensor feedback isolation cannot be promoted to pass while trace consumption remains blocked")
    attitude_feedback = as_mapping(mworks.get("attitude_feedback_isolation"))
    if attitude_feedback:
        require_path(report, "mworks.attitude_feedback_isolation.return_packet", attitude_feedback.get("return_packet"))
        require_path(report, "mworks.attitude_feedback_isolation.probe_json", attitude_feedback.get("probe_json"))
        require_path(report, "mworks.attitude_feedback_isolation.probe_summary_csv", attitude_feedback.get("probe_summary_csv"))
        require_path(report, "mworks.attitude_feedback_isolation.mcp_log", attitude_feedback.get("mcp_log"))
        boundary = as_mapping(attitude_feedback.get("first_failure_boundary"))
        probes = as_list(attitude_feedback.get("attitude_feedback_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        if attitude_feedback.get("quality_status") == "attitude_feedback_sub_boundary_found":
            report["warnings"].append("MWORKS attitude-feedback isolation found direct single-channel AngleMea feedback as the empty-result boundary")
        for probe_id in [
            "iso10_roll_only_direct",
            "iso11_pitch_only_direct",
            "iso12_roll_only_negated",
            "iso13_pitch_only_negated",
        ]:
            if probe_by_id.get(probe_id, {}).get("check_model") != "pass":
                report["issues"].append(f"attitude feedback isolation must preserve {probe_id} check_model pass")
            if probe_by_id.get(probe_id, {}).get("simulate_model") != "failed":
                report["issues"].append(f"attitude feedback isolation must preserve {probe_id} simulate failure")
            if probe_by_id.get(probe_id, {}).get("get_var_times_count") != 0:
                report["issues"].append(f"attitude feedback isolation must preserve {probe_id} empty result times")
            if probe_by_id.get(probe_id, {}).get("error_6140_present") is not False:
                report["issues"].append(f"attitude feedback isolation must preserve {probe_id} 6140 absent")
        if boundary.get("probe_id") != "iso10_roll_only_direct":
            report["issues"].append("attitude feedback first boundary must remain iso10_roll_only_direct")
        if boundary.get("error_6140_present") is not False:
            report["issues"].append("attitude feedback first boundary must preserve 6140 absent")
        if "sign flip" not in str(boundary.get("sign_or_frame_result", "")):
            report["issues"].append("attitude feedback isolation must preserve sign-flip result")
        if attitude_feedback.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("attitude feedback isolation cannot be promoted to pass while trace consumption remains blocked")
    attitude_intermediary = as_mapping(mworks.get("attitude_intermediary_classification"))
    if attitude_intermediary:
        require_path(
            report,
            "mworks.attitude_intermediary_classification.return_packet",
            attitude_intermediary.get("return_packet"),
        )
        require_path(
            report,
            "mworks.attitude_intermediary_classification.probe_json",
            attitude_intermediary.get("probe_json"),
        )
        require_path(
            report,
            "mworks.attitude_intermediary_classification.probe_summary_csv",
            attitude_intermediary.get("probe_summary_csv"),
        )
        require_path(report, "mworks.attitude_intermediary_classification.mcp_log", attitude_intermediary.get("mcp_log"))
        classification = as_mapping(attitude_intermediary.get("classification"))
        probes = as_list(attitude_intermediary.get("intermediary_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        if attitude_intermediary.get("quality_status") == "absolute_angles_dependency_coupling_classified":
            report["warnings"].append("MWORKS attitude-intermediary classification found AbsoluteAngles/AngleMea dependency coupling; constant/table inputs pass, AngleMea-dependent RealExpression fails")
        for probe_id in ["iso14_constant_attitude_input", "iso15_table_attitude_input"]:
            if probe_by_id.get(probe_id, {}).get("check_model") != "pass":
                report["issues"].append(f"attitude intermediary must preserve {probe_id} check_model pass")
            if probe_by_id.get(probe_id, {}).get("simulate_model") != "pass":
                report["issues"].append(f"attitude intermediary must preserve {probe_id} simulate pass")
            if probe_by_id.get(probe_id, {}).get("get_var_times_count") != 1001:
                report["issues"].append(f"attitude intermediary must preserve {probe_id} 1001 result times")
            if probe_by_id.get(probe_id, {}).get("nonzero_alias_refs") is not True:
                report["issues"].append(f"attitude intermediary must preserve {probe_id} nonzero aliases")
        if probe_by_id.get("iso16_realexpression_angle_bridge", {}).get("check_model") != "pass":
            report["issues"].append("attitude intermediary must preserve iso16 check_model pass")
        if probe_by_id.get("iso16_realexpression_angle_bridge", {}).get("simulate_model") != "failed":
            report["issues"].append("attitude intermediary must preserve iso16 simulate failure")
        if probe_by_id.get("iso16_realexpression_angle_bridge", {}).get("get_var_times_count") != 0:
            report["issues"].append("attitude intermediary must preserve iso16 empty result times")
        if probe_by_id.get("iso16_realexpression_angle_bridge", {}).get("error_6140_present") is not False:
            report["issues"].append("attitude intermediary must preserve iso16 6140 absent")
        if classification.get("constant_attitude_inputs_pass") is not True:
            report["issues"].append("attitude intermediary classification must preserve constant_attitude_inputs_pass=true")
        if classification.get("time_table_attitude_inputs_pass") is not True:
            report["issues"].append("attitude intermediary classification must preserve time_table_attitude_inputs_pass=true")
        if classification.get("realexpression_anglemea_bridge_passes") is not False:
            report["issues"].append("attitude intermediary classification must preserve realexpression_anglemea_bridge_passes=false")
        if "AbsoluteAngles" not in str(classification.get("first_current_blocker", "")):
            report["issues"].append("attitude intermediary classification must preserve AbsoluteAngles/AngleMea as the current blocker")
        if attitude_intermediary.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("attitude intermediary classification cannot be promoted to pass while trace consumption remains blocked")
    attitude_decoupling = as_mapping(mworks.get("attitude_decoupling_probe"))
    if attitude_decoupling:
        require_path(report, "mworks.attitude_decoupling_probe.return_packet", attitude_decoupling.get("return_packet"))
        require_path(report, "mworks.attitude_decoupling_probe.probe_json", attitude_decoupling.get("probe_json"))
        require_path(
            report,
            "mworks.attitude_decoupling_probe.probe_summary_csv",
            attitude_decoupling.get("probe_summary_csv"),
        )
        require_path(report, "mworks.attitude_decoupling_probe.mcp_log", attitude_decoupling.get("mcp_log"))
        classification = as_mapping(attitude_decoupling.get("classification"))
        probes = as_list(attitude_decoupling.get("decoupling_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        if attitude_decoupling.get("quality_status") == "attitude_decoupling_probe_passed":
            report["warnings"].append("MWORKS attitude-decoupling probes restored result context, but full Factory trace consumption and closed_loop remain blocked")
        for probe_id in ["iso17_sample_hold_angle", "iso18_project_attitude_estimator"]:
            if probe_by_id.get(probe_id, {}).get("check_model") != "pass":
                report["issues"].append(f"attitude decoupling must preserve {probe_id} check_model pass")
            if probe_by_id.get(probe_id, {}).get("simulate_model") != "pass":
                report["issues"].append(f"attitude decoupling must preserve {probe_id} simulate pass")
            if probe_by_id.get(probe_id, {}).get("get_var_times_count") != 1001:
                report["issues"].append(f"attitude decoupling must preserve {probe_id} 1001 result times")
            if probe_by_id.get(probe_id, {}).get("nonzero_alias_refs") is not True:
                report["issues"].append(f"attitude decoupling must preserve {probe_id} nonzero aliases")
            if probe_by_id.get(probe_id, {}).get("error_6140_present") is not False:
                report["issues"].append(f"attitude decoupling must preserve {probe_id} 6140 absent")
        if classification.get("prior_010_direct_realexpression_anglemea_failed") is not True:
            report["issues"].append("attitude decoupling must preserve prior 010 direct RealExpression failure")
        if classification.get("sampled_held_decoupling_passes") is not True:
            report["issues"].append("attitude decoupling must preserve sampled_held_decoupling_passes=true")
        if classification.get("project_owned_attitude_extraction_passes") is not True:
            report["issues"].append("attitude decoupling must preserve project_owned_attitude_extraction_passes=true")
        if classification.get("absolute_angles_dependency_can_be_decoupled") is not True:
            report["issues"].append("attitude decoupling must preserve absolute_angles_dependency_can_be_decoupled=true")
        if "Iso18" not in str(classification.get("recommended_pattern", "")):
            report["issues"].append("attitude decoupling must preserve Iso18 as recommended pattern")
        if attitude_decoupling.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("attitude decoupling cannot be promoted to pass while trace consumption remains blocked")
    pitch_decoupling = as_mapping(mworks.get("pitch_decoupling_probe"))
    if pitch_decoupling:
        require_path(report, "mworks.pitch_decoupling_probe.return_packet", pitch_decoupling.get("return_packet"))
        require_path(report, "mworks.pitch_decoupling_probe.probe_json", pitch_decoupling.get("probe_json"))
        require_path(report, "mworks.pitch_decoupling_probe.probe_summary_csv", pitch_decoupling.get("probe_summary_csv"))
        require_path(report, "mworks.pitch_decoupling_probe.mcp_log", pitch_decoupling.get("mcp_log"))
        for index, model_path in enumerate(as_list(pitch_decoupling.get("models_created"))):
            require_path(report, f"mworks.pitch_decoupling_probe.model[{index}]", model_path)
        probes = as_list(pitch_decoupling.get("pitch_decoupling_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        iso19 = probe_by_id.get("iso19_roll_pitch_estimator", {})
        classification = as_mapping(pitch_decoupling.get("classification"))
        if pitch_decoupling.get("quality_status") == "pitch_decoupling_probe_passed":
            report["warnings"].append("MWORKS pitch-decoupling probe restored roll+pitch result context, but closed_loop and Factory trace consumption remain blocked")
        if iso19.get("check_model") != "pass":
            report["issues"].append("pitch decoupling must preserve Iso19 check_model pass")
        if iso19.get("simulate_model") != "pass":
            report["issues"].append("pitch decoupling must preserve Iso19 simulate pass")
        if iso19.get("get_var_times_count") != 1001:
            report["issues"].append("pitch decoupling must preserve Iso19 1001 result times")
        if iso19.get("nonzero_alias_refs") is not True:
            report["issues"].append("pitch decoupling must preserve Iso19 nonzero aliases")
        if iso19.get("roll_pitch_alias_available") is not True:
            report["issues"].append("pitch decoupling must preserve roll/pitch alias availability")
        if iso19.get("error_6140_present") is not False:
            report["issues"].append("pitch decoupling must preserve 6140 absent")
        if classification.get("prior_011_iso18_roll_extraction_passed") is not True:
            report["issues"].append("pitch decoupling must preserve prior 011 roll extraction pass")
        if classification.get("pitch_anglemea2_extraction_added") is not True:
            report["issues"].append("pitch decoupling must preserve pitch AngleMea[2] extraction")
        if classification.get("roll_pitch_project_owned_extraction_passes") is not True:
            report["issues"].append("pitch decoupling must preserve roll+pitch project-owned extraction pass")
        for forbidden_key in ["yaw_feedback_added", "rate_feedback_added", "full_sensor_bus_added", "full_factory_wrapper_retried"]:
            if classification.get(forbidden_key) is not False:
                report["issues"].append(f"pitch decoupling must preserve {forbidden_key}=false")
        if pitch_decoupling.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("pitch decoupling cannot be promoted to pass while trace consumption remains blocked")
    yaw_rate = as_mapping(mworks.get("yaw_rate_decoupling_probe"))
    if yaw_rate:
        require_path(report, "mworks.yaw_rate_decoupling_probe.return_packet", yaw_rate.get("return_packet"))
        require_path(report, "mworks.yaw_rate_decoupling_probe.probe_json", yaw_rate.get("probe_json"))
        require_path(report, "mworks.yaw_rate_decoupling_probe.probe_summary_csv", yaw_rate.get("probe_summary_csv"))
        require_path(report, "mworks.yaw_rate_decoupling_probe.mcp_log", yaw_rate.get("mcp_log"))
        require_path(
            report,
            "mworks.yaw_rate_decoupling_probe.unknowns_risks_next_validation",
            yaw_rate.get("unknowns_risks_next_validation"),
        )
        for index, model_path in enumerate(as_list(yaw_rate.get("models_created"))):
            require_path(report, f"mworks.yaw_rate_decoupling_probe.model[{index}]", model_path)
        probes = as_list(yaw_rate.get("yaw_rate_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        iso20 = probe_by_id.get("iso20_roll_pitch_yaw_estimator", {})
        classification = as_mapping(yaw_rate.get("classification"))
        if yaw_rate.get("quality_status") == "yaw_attitude_decoupling_probe_passed":
            report["warnings"].append("MWORKS yaw-decoupling probe restored yaw result context, but rate feedback and closed_loop remain blocked")
        if iso20.get("check_model") != "pass":
            report["issues"].append("yaw/rate decoupling must preserve Iso20 check_model pass")
        if iso20.get("simulate_model") != "pass":
            report["issues"].append("yaw/rate decoupling must preserve Iso20 simulate pass")
        if iso20.get("get_var_times_count") != 1001:
            report["issues"].append("yaw/rate decoupling must preserve Iso20 1001 result times")
        if iso20.get("nonzero_alias_refs") is not True:
            report["issues"].append("yaw/rate decoupling must preserve Iso20 nonzero aliases")
        if iso20.get("yaw_alias_available") is not True:
            report["issues"].append("yaw/rate decoupling must preserve yaw alias availability")
        if iso20.get("error_6140_present") is not False:
            report["issues"].append("yaw/rate decoupling must preserve 6140 absent")
        if iso20.get("rate_fallback_used") is not False:
            report["issues"].append("yaw/rate decoupling must preserve that rate fallback was not used")
        if classification.get("prior_012_roll_pitch_extraction_passed") is not True:
            report["issues"].append("yaw/rate decoupling must preserve prior 012 roll+pitch extraction pass")
        if classification.get("yaw_anglemea3_extraction_added") is not True:
            report["issues"].append("yaw/rate decoupling must preserve yaw AngleMea[3] extraction")
        if classification.get("yaw_attitude_extraction_passes") is not True:
            report["issues"].append("yaw/rate decoupling must preserve yaw attitude extraction pass")
        for forbidden_key in ["rate_feedback_added", "rate_fallback_needed", "full_sensor_bus_added", "full_factory_wrapper_retried"]:
            if classification.get(forbidden_key) is not False:
                report["issues"].append(f"yaw/rate decoupling must preserve {forbidden_key}=false")
        if yaw_rate.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("yaw/rate decoupling cannot be promoted to pass while trace consumption remains blocked")
    rate_feedback = as_mapping(mworks.get("rate_feedback_isolation_probe"))
    if rate_feedback:
        require_path(report, "mworks.rate_feedback_isolation_probe.return_packet", rate_feedback.get("return_packet"))
        require_path(report, "mworks.rate_feedback_isolation_probe.probe_json", rate_feedback.get("probe_json"))
        require_path(report, "mworks.rate_feedback_isolation_probe.probe_summary_csv", rate_feedback.get("probe_summary_csv"))
        require_path(report, "mworks.rate_feedback_isolation_probe.mcp_log", rate_feedback.get("mcp_log"))
        require_path(
            report,
            "mworks.rate_feedback_isolation_probe.unknowns_risks_next_validation",
            rate_feedback.get("unknowns_risks_next_validation"),
        )
        for index, model_path in enumerate(as_list(rate_feedback.get("models_created"))):
            require_path(report, f"mworks.rate_feedback_isolation_probe.model[{index}]", model_path)
        probes = as_list(rate_feedback.get("rate_feedback_probes"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        iso21 = probe_by_id.get("iso21_controller_rate_alias", {})
        classification = as_mapping(rate_feedback.get("classification"))
        if rate_feedback.get("quality_status") == "rate_feedback_isolation_probe_passed":
            report["warnings"].append("MWORKS rate-feedback isolation restored rate aliases only; external gyro/rate feedback and closed_loop remain blocked")
        if iso21.get("check_model") != "pass":
            report["issues"].append("rate-feedback isolation must preserve Iso21 check_model pass")
        if iso21.get("simulate_model") != "pass":
            report["issues"].append("rate-feedback isolation must preserve Iso21 simulate pass")
        if iso21.get("get_var_times_count") != 1001:
            report["issues"].append("rate-feedback isolation must preserve Iso21 1001 result times")
        if iso21.get("nonzero_alias_refs") is not True:
            report["issues"].append("rate-feedback isolation must preserve Iso21 nonzero reference aliases")
        if iso21.get("rate_alias_available") is not True:
            report["issues"].append("rate-feedback isolation must preserve rate alias availability")
        if iso21.get("error_6140_present") is not False:
            report["issues"].append("rate-feedback isolation must preserve 6140 absent")
        if classification.get("prior_013_yaw_extraction_passed") is not True:
            report["issues"].append("rate-feedback isolation must preserve prior 013 yaw extraction pass")
        if classification.get("narrow_rate_alias_group_added") is not True:
            report["issues"].append("rate-feedback isolation must preserve narrow rate alias group")
        if classification.get("rate_alias_group_passes") is not True:
            report["issues"].append("rate-feedback isolation must preserve rate alias group pass")
        for forbidden_key in ["current_controller_external_rate_inports", "external_rate_sensor_wired", "full_sensor_bus_added", "full_factory_wrapper_retried"]:
            if classification.get(forbidden_key) is not False:
                report["issues"].append(f"rate-feedback isolation must preserve {forbidden_key}=false")
        if rate_feedback.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("rate-feedback isolation cannot be promoted to pass while trace consumption remains blocked")

    sensor_bus = as_mapping(mworks.get("sensor_bus_reconnect_probe"))
    if sensor_bus:
        require_path(report, "mworks.sensor_bus_reconnect_probe.blocker_packet", sensor_bus.get("blocker_packet"))
        require_path(report, "mworks.sensor_bus_reconnect_probe.probe_json", sensor_bus.get("probe_json"))
        require_path(report, "mworks.sensor_bus_reconnect_probe.probe_summary_csv", sensor_bus.get("probe_summary_csv"))
        require_path(report, "mworks.sensor_bus_reconnect_probe.mcp_log", sensor_bus.get("mcp_log"))
        for index, model_path in enumerate(as_list(sensor_bus.get("models_created"))):
            require_path(report, f"mworks.sensor_bus_reconnect_probe.model[{index}]", model_path)
        probes = as_list(sensor_bus.get("probe_results"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        iso22 = probe_by_id.get("iso22_sensor_display_reconnect", {})
        if sensor_bus.get("quality_status") == "blocked_first_new_boundary_found":
            report["warnings"].append("MWORKS sensor-bus reconnect found direct PosMea display reconnect as the next blocked topology boundary")
        if sensor_bus.get("status") != "blocked":
            report["issues"].append("sensor-bus reconnect 015 must remain blocked")
        if sensor_bus.get("blocker_kind") != "simulate_failed_result_context_empty":
            report["issues"].append("sensor-bus reconnect 015 must preserve simulate_failed_result_context_empty")
        if iso22.get("check_model") != "pass":
            report["issues"].append("sensor-bus reconnect must preserve Iso22 check_model pass")
        if iso22.get("simulate_model") != "failed":
            report["issues"].append("sensor-bus reconnect must preserve Iso22 simulate failure")
        if iso22.get("simulate_data") is not False:
            report["issues"].append("sensor-bus reconnect must preserve Iso22 simulate_data=false")
        if iso22.get("get_var_times_count") != 0:
            report["issues"].append("sensor-bus reconnect must preserve Iso22 empty result times")
        if iso22.get("alias_values_available") is not False:
            report["issues"].append("sensor-bus reconnect must preserve unavailable aliases")
        if iso22.get("error_6140_present") is not True:
            report["issues"].append("sensor-bus reconnect must preserve 6140 as present")
        if "navigationDisplay.actual_position" not in str(iso22.get("first_new_boundary", "")):
            report["issues"].append("sensor-bus reconnect must preserve navigationDisplay.actual_position boundary")
        if sensor_bus.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("sensor-bus reconnect cannot be promoted to pass while trace consumption remains blocked")

    position_bridge = as_mapping(mworks.get("position_bridge_probe"))
    if position_bridge:
        require_path(report, "mworks.position_bridge_probe.return_packet", position_bridge.get("return_packet"))
        require_path(report, "mworks.position_bridge_probe.probe_json", position_bridge.get("probe_json"))
        require_path(report, "mworks.position_bridge_probe.alias_samples_csv", position_bridge.get("alias_samples_csv"))
        require_path(report, "mworks.position_bridge_probe.mcp_log", position_bridge.get("mcp_log"))
        for index, model_path in enumerate(as_list(position_bridge.get("models_created"))):
            require_path(report, f"mworks.position_bridge_probe.model[{index}]", model_path)
        probes = as_list(position_bridge.get("probe_results"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        iso23 = probe_by_id.get("iso23_position_sample_hold_bridge", {})
        if position_bridge.get("quality_status") == "display_position_bridge_probe_passed":
            report["warnings"].append("MWORKS position bridge restored display-position result context only; full Factory trace remains blocked")
        if position_bridge.get("status") != "completed":
            report["issues"].append("position bridge 016 must be completed if present")
        if iso23.get("check_model") != "pass":
            report["issues"].append("position bridge must preserve Iso23 check_model pass")
        if iso23.get("simulate_model") != "pass":
            report["issues"].append("position bridge must preserve Iso23 simulation pass")
        if iso23.get("simulate_data") is not True:
            report["issues"].append("position bridge must preserve Iso23 simulate_data=true")
        if iso23.get("get_var_times_count") != 1001:
            report["issues"].append("position bridge must preserve Iso23 1001 result times")
        if iso23.get("alias_values_available") is not True:
            report["issues"].append("position bridge must preserve available aliases")
        if iso23.get("error_6140_present") is not False:
            report["issues"].append("position bridge must preserve 6140 absent")
        if iso23.get("result_context_restored") is not True:
            report["issues"].append("position bridge must preserve restored result context")
        if position_bridge.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("position bridge cannot be promoted to pass while trace consumption remains blocked")

    attitude_bridge = as_mapping(mworks.get("attitude_feedback_bridge_probe"))
    if attitude_bridge:
        require_path(report, "mworks.attitude_feedback_bridge_probe.return_packet", attitude_bridge.get("return_packet"))
        require_path(report, "mworks.attitude_feedback_bridge_probe.probe_json", attitude_bridge.get("probe_json"))
        require_path(
            report,
            "mworks.attitude_feedback_bridge_probe.alias_samples_csv",
            attitude_bridge.get("alias_samples_csv"),
        )
        require_path(report, "mworks.attitude_feedback_bridge_probe.mcp_log", attitude_bridge.get("mcp_log"))
        for index, model_path in enumerate(as_list(attitude_bridge.get("models_created"))):
            require_path(report, f"mworks.attitude_feedback_bridge_probe.model[{index}]", model_path)
        probes = as_list(attitude_bridge.get("probe_results"))
        probe_by_id = {str(probe.get("probe_id", "")): as_mapping(probe) for probe in probes if isinstance(probe, dict)}
        iso25 = probe_by_id.get("iso25_sample_hold_attitude_feedback_bridge", {})
        if attitude_bridge.get("quality_status") == "attitude_feedback_bridge_probe_passed":
            report["warnings"].append("MWORKS attitude-feedback bridge 019 restored result context only for the narrow sampled/held bridge")
        if attitude_bridge.get("status") != "completed":
            report["issues"].append("attitude-feedback bridge 019 must be completed if present")
        if "sampled/held" not in str(attitude_bridge.get("selected_bridge_variant", "")):
            report["issues"].append("attitude-feedback bridge must preserve sampled/held selected variant")
        if iso25.get("check_model") != "pass":
            report["issues"].append("attitude-feedback bridge must preserve Iso25 check_model pass")
        if iso25.get("simulate_model") != "pass":
            report["issues"].append("attitude-feedback bridge must preserve Iso25 simulation pass")
        if iso25.get("simulate_data") is not True:
            report["issues"].append("attitude-feedback bridge must preserve Iso25 simulate_data=true")
        if iso25.get("get_var_times_count") != 1001:
            report["issues"].append("attitude-feedback bridge must preserve Iso25 1001 result times")
        if iso25.get("alias_values_available") is not True:
            report["issues"].append("attitude-feedback bridge must preserve readable aliases")
        if iso25.get("error_6140_present") is not False:
            report["issues"].append("attitude-feedback bridge must preserve 6140 absent")
        if iso25.get("result_context_restored") is not True:
            report["issues"].append("attitude-feedback bridge must preserve restored result context")
        if "Factory trace consumption" not in str(attitude_bridge.get("claim_boundary", "")):
            report["issues"].append("attitude-feedback bridge must explicitly exclude Factory trace consumption")
        if attitude_bridge.get("quality_status") == "pass" and trace_status != "pass":
            report["issues"].append("attitude-feedback bridge cannot be promoted to pass while trace consumption remains blocked")

    actuator_bridge = as_mapping(mworks.get("actuator_to_wrench_bridge_smoke"))
    if actuator_bridge:
        require_path(report, "mworks.actuator_to_wrench_bridge_smoke.return_packet", actuator_bridge.get("return_packet"))
        require_path(report, "mworks.actuator_to_wrench_bridge_smoke.evidence_dir", actuator_bridge.get("evidence_dir"))
        result_summary = as_mapping(actuator_bridge.get("result_summary"))
        boundary = as_mapping(actuator_bridge.get("claim_boundary"))
        if actuator_bridge.get("status") != "completed_minimal_bridge_smoke":
            report["issues"].append("actuator-to-wrench bridge 014 must remain completed_minimal_bridge_smoke")
        if actuator_bridge.get("quality_status") != "minimal_actuator_to_wrench_bridge_smoke_passed":
            report["issues"].append("actuator-to-wrench bridge 014 must remain minimal smoke evidence")
        if actuator_bridge.get("check_model_status") != "pass":
            report["issues"].append("actuator-to-wrench bridge 014 must preserve check_model pass")
        if actuator_bridge.get("simulate_status") != "pass":
            report["issues"].append("actuator-to-wrench bridge 014 must preserve simulation pass")
        if actuator_bridge.get("get_var_times_count") != 251:
            report["issues"].append("actuator-to-wrench bridge 014 must preserve 251 result times")
        if result_summary.get("bridge_command_error_abs_sum_end") != 0.0:
            report["issues"].append("actuator-to-wrench bridge 014 must preserve zero command bridge error")
        for key in ["force_application_error_at_samples", "torque_application_error_at_samples"]:
            if result_summary.get(key) != [0.0, 0.0, 0.0]:
                report["issues"].append(f"actuator-to-wrench bridge 014 must preserve zero {key}")
        if boundary.get("minimal_actuator_to_wrench_bridge_smoke") is not True:
            report["issues"].append("actuator-to-wrench bridge 014 must mark only minimal smoke true")
        for key in [
            "factory_trace_consumption",
            "full_factory_wrapper_retry",
            "closed_loop",
            "controller_performance",
            "plant_tracking",
            "parameter_identification",
            "planner_readiness",
            "live_runtime_ack",
            "full_actuator_or_plant_closure",
        ]:
            if boundary.get(key) is not False:
                report["issues"].append(f"actuator-to-wrench bridge 014 must keep claim_boundary.{key}=false")
        report["warnings"].append("MWORKS actuator-to-wrench bridge 014 is a minimal sidecar smoke only; Factory trace and full plant remain blocked")

    external_frame = as_mapping(mworks.get("external_frame_boundary_smoke"))
    if external_frame:
        require_path(report, "mworks.external_frame_boundary_smoke.return_packet", external_frame.get("return_packet"))
        require_path(report, "mworks.external_frame_boundary_smoke.evidence_dir", external_frame.get("evidence_dir"))
        result_summary = as_mapping(external_frame.get("result_summary"))
        boundary = as_mapping(external_frame.get("claim_boundary"))
        if external_frame.get("status") != "completed_external_frame_boundary_smoke":
            report["issues"].append("external-frame boundary 015 must remain completed_external_frame_boundary_smoke")
        if external_frame.get("quality_status") != "minimal_external_frame_boundary_smoke_passed":
            report["issues"].append("external-frame boundary 015 must remain minimal smoke evidence")
        if external_frame.get("check_model_status") != "pass":
            report["issues"].append("external-frame boundary 015 must preserve check_model pass")
        if external_frame.get("simulate_status") != "pass":
            report["issues"].append("external-frame boundary 015 must preserve simulation pass")
        if external_frame.get("get_var_times_count") != 251:
            report["issues"].append("external-frame boundary 015 must preserve 251 result times")
        if result_summary.get("bridge_command_error_abs_sum_end") != 0.0:
            report["issues"].append("external-frame boundary 015 must preserve zero bridge command error")
        if result_summary.get("external_boundary_gate_error_end") != 0.0:
            report["issues"].append("external-frame boundary 015 must preserve zero external boundary gate error")
        for key in [
            "external_force_application_error_at_samples",
            "external_torque_application_error_at_samples",
            "external_force_matches_adapter_error_at_samples",
            "external_torque_matches_adapter_error_at_samples",
        ]:
            if result_summary.get(key) != [0.0, 0.0, 0.0]:
                report["issues"].append(f"external-frame boundary 015 must preserve zero {key}")
        if boundary.get("minimal_external_frame_boundary_smoke") is not True:
            report["issues"].append("external-frame boundary 015 must mark only minimal external-frame smoke true")
        for key in [
            "factory_trace_consumption",
            "full_factory_wrapper_retry",
            "quadchassis_or_full_plant_closure",
            "closed_loop",
            "controller_performance",
            "full_plant_tracking",
            "mission_success",
            "parameter_identification",
            "planner_readiness",
            "live_runtime_ack",
            "dynamic_yaw_transient_acceptance",
            "allocation_or_fault_isolation_readiness",
        ]:
            if boundary.get(key) is not False:
                report["issues"].append(f"external-frame boundary 015 must keep claim_boundary.{key}=false")
        report["warnings"].append("MWORKS external-frame boundary 015 is a minimal external MultiBody test-body smoke only; full plant and Factory trace remain blocked")

    ros2 = as_mapping(manifest.get("ros2"))
    require_path(report, "ros2.bag_or_summary", ros2.get("bag_or_summary"))
    fast_lio = as_mapping(ros2.get("fast_lio_eval"))
    require_path(report, "ros2.fast_lio_eval.runtime_recording", fast_lio.get("runtime_recording"))
    require_path(report, "ros2.fast_lio_eval.runtime_evaluation", fast_lio.get("runtime_evaluation"))

    b0 = as_mapping(ros2.get("position_command_b0_contract_replay"))
    if b0:
        require_path(report, "ros2.b0.run_summary", b0.get("run_summary"))
        require_path(report, "ros2.b0.topic_rates", b0.get("topic_rates"))
        require_path(report, "ros2.b0.planner_input_gate", b0.get("planner_input_gate"))
        require_path(report, "ros2.b0.setpoint_trace_csv", b0.get("setpoint_trace_csv"))
        if b0.get("smoke_only") is not True or b0.get("not_planner_closure") is not True:
            report["issues"].append("B0 PositionCommand replay must be marked smoke_only and not_planner_closure")

    b1_blocker = as_mapping(ros2.get("position_command_b1_real_planner"))
    require_path(report, "ros2.b1_real_planner.blocker_packet", b1_blocker.get("blocker_packet"))

    b1_unblock = as_mapping(ros2.get("position_command_b1_unblock"))
    if b1_unblock:
        require_path(report, "ros2.b1_unblock.blocker_packet", b1_unblock.get("blocker_packet"))
        current_recording = b1_unblock.get("current_recording", "")
        require_path(report, "ros2.b1_unblock.current_recording", current_recording)
        if b1_unblock.get("fast_lio_runtime_restored") is True and b1_unblock.get("planner_position_command_source_restored") is not True:
            report["warnings"].append("FAST-LIO runtime is restored, but planner PositionCommand source is still absent")
        if b1_unblock.get("planner_position_command_source_restored") is True:
            report["issues"].append("planner source restored in manifest but planner/closed_loop scope is still excluded; rerun manifest gate with B1 evidence")
    b1_planner_wrapper = as_mapping(ros2.get("position_command_b1_planner_wrapper"))
    if b1_planner_wrapper:
        require_path(report, "ros2.b1_planner_wrapper.blocker_packet", b1_planner_wrapper.get("blocker_packet"))
        if b1_planner_wrapper.get("status") == "blocked":
            report["warnings"].append("B1 planner wrapper is blocked: selected EGO/Sunray/FUEL candidates are not executable in the current ROS2 overlay")
        if b1_planner_wrapper.get("wrapper_safe_to_add_now") is True and "planner" not in report["claim_scope"]:
            report["issues"].append("planner wrapper marked safe but planner claim is excluded; rerun B1 evidence before accepting manifest")
    b1_port_preflight = as_mapping(ros2.get("position_command_b1_port_preflight"))
    if b1_port_preflight:
        require_path(report, "ros2.b1_port_preflight.return_packet", b1_port_preflight.get("return_packet"))
        require_path(report, "ros2.b1_port_preflight.build_log", b1_port_preflight.get("build_log"))
        if b1_port_preflight.get("port_preflight_completed") is True:
            report["warnings"].append("B1 port preflight completed classification only; real planner runtime is not ready")
        if b1_port_preflight.get("can_enter_real_position_cmd_recorder") is True and "planner" not in report["claim_scope"]:
            report["issues"].append("B1 recorder marked runnable while planner claim remains excluded; rerun manifest after real runtime evidence")
    b1_msg_port_slice = as_mapping(ros2.get("position_command_b1_msg_port_slice"))
    if b1_msg_port_slice:
        require_path(report, "ros2.b1_msg_port_slice.return_packet", b1_msg_port_slice.get("return_packet"))
        for index, artifact in enumerate(as_list(b1_msg_port_slice.get("artifacts"))):
            require_path(report, f"ros2.b1_msg_port_slice.artifact[{index}]", artifact)
        can_start_recorder = as_mapping(b1_msg_port_slice.get("can_start_runtime_recorder"))
        if b1_msg_port_slice.get("status") == "completed_message_slice":
            report["warnings"].append("B1 message slice built internal ROS2 messages only; planner runtime is still absent")
        if can_start_recorder.get("allowed") is True and "planner" not in report["claim_scope"]:
            report["issues"].append("B1 runtime recorder marked allowed while planner claim remains excluded; rerun with real runtime evidence")
    b1_planner_node = as_mapping(ros2.get("position_command_b1_planner_node_port_preflight"))
    if b1_planner_node:
        require_path(report, "ros2.b1_planner_node.return_packet", b1_planner_node.get("return_packet"))
        build_status = as_mapping(b1_planner_node.get("build_status"))
        for index, log_path in enumerate(as_list(build_status.get("logs"))):
            require_path(report, f"ros2.b1_planner_node.build_log[{index}]", log_path)
        require_path(report, "ros2.b1_planner_node.installed_executable", build_status.get("installed_executable"))
        forbidden = as_mapping(b1_planner_node.get("forbidden_actions_confirmed"))
        if b1_planner_node.get("status") == "completed_preflight":
            report["warnings"].append("B1 planner-node preflight built a traj_server ROS2 stub only; runtime recorder remains forbidden")
        for key in [
            "edited_references",
            "planner_runtime_launched",
            "published_position_cmd",
            "runtime_recorder_run",
            "fastlio_path_used_as_planner_trajectory",
            "ue_global_truth_used_as_planner_input",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"planner-node preflight forbidden action not confirmed false: {key}")
    b1_upstream = as_mapping(ros2.get("position_command_b1_upstream_planner_deps"))
    if b1_upstream:
        require_path(report, "ros2.b1_upstream_planner_deps.blocker_packet", b1_upstream.get("blocker_packet"))
        artifacts = as_mapping(b1_upstream.get("artifacts"))
        for label in ["producer_scan", "dependency_surface_scan", "colcon_list", "plan_env_build_probe"]:
            require_path(report, f"ros2.b1_upstream_planner_deps.{label}", artifacts.get(label))
        preferred = as_mapping(b1_upstream.get("preferred_bspline_producer"))
        first_blocker = as_mapping(b1_upstream.get("first_blocker"))
        reachability = as_mapping(b1_upstream.get("can_reach_real_planning_bspline_next"))
        if b1_upstream.get("status") == "blocked_after_classification":
            report["warnings"].append("B1 upstream planner deps are blocked: EGOReplanFSM producer found, but plan_env/GridMap is still ROS1/catkin-only")
        if "EGOReplanFSM" not in str(preferred.get("candidate", "")):
            report["issues"].append("B1 upstream planner deps must preserve EGOReplanFSM as the preferred Bspline producer candidate")
        if first_blocker.get("package") != "plan_env":
            report["issues"].append("B1 upstream planner deps first blocker must remain plan_env until a new return supersedes it")
        if reachability.get("status") is not False:
            report["issues"].append("B1 upstream planner deps must not mark real /planning/bspline reachable yet")
        forbidden = as_mapping(b1_upstream.get("forbidden_actions_confirmed"))
        for key in [
            "published_position_cmd",
            "runtime_recorder_run",
            "planner_runtime_launched",
            "fastlio_path_converted_to_trajectory",
            "fake_pointcloud_or_grid_used",
            "ue_global_truth_used_as_planner_input",
            "keyboard_pose_used",
            "new_planner_algorithm_handwritten",
            "references_edited",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"upstream planner deps forbidden action not confirmed false: {key}")
    b1_planenv = as_mapping(ros2.get("position_command_b1_planenv_gridmap_port"))
    if b1_planenv:
        require_path(report, "ros2.b1_planenv_gridmap_port.return_packet", b1_planenv.get("return_packet"))
        build_status = as_mapping(b1_planenv.get("build_status"))
        require_path(report, "ros2.b1_planenv_gridmap_port.red_build_log", build_status.get("red_build_log"))
        for index, log_path in enumerate(as_list(build_status.get("post_patch_logs"))):
            require_path(report, f"ros2.b1_planenv_gridmap_port.post_patch_log[{index}]", log_path)
        for index, artifact in enumerate(as_list(build_status.get("installed_artifacts"))):
            require_path(report, f"ros2.b1_planenv_gridmap_port.installed_artifact[{index}]", artifact)
        for index, item in enumerate(as_list(b1_planenv.get("classification_logs"))):
            require_path(report, f"ros2.b1_planenv_gridmap_port.classification_log[{index}]", as_mapping(item).get("path"))
        summary = as_mapping(b1_planenv.get("summary"))
        package_state = as_mapping(b1_planenv.get("workspace_package_state_after_011"))
        contract = as_mapping(b1_planenv.get("runtime_contract_preserved"))
        if b1_planenv.get("status") == "completed_preflight":
            report["warnings"].append("B1 plan_env/GridMap port built the isolated ROS2 surface only; planner runtime remains blocked")
        if summary.get("plan_env_ros2_buildable") is not True:
            report["issues"].append("B1 plan_env/GridMap port must preserve plan_env_ros2_buildable=true")
        if "plan_env" in as_list(package_state.get("catkin_only_packages_remaining")):
            report["issues"].append("plan_env must no longer be listed as catkin-only after task 011")
        for package in ["path_searching", "bspline_opt"]:
            if package not in as_list(package_state.get("catkin_only_packages_remaining")):
                report["issues"].append(f"B1 plan_env task must preserve remaining blocker package: {package}")
        if contract.get("intended_odom_remap") != "/grid_map/odom:=/Odometry":
            report["issues"].append("B1 plan_env task must preserve /grid_map/odom:=/Odometry remap")
        if contract.get("intended_cloud_remap") != "/grid_map/cloud:=/cloud_registered":
            report["issues"].append("B1 plan_env task must preserve /grid_map/cloud:=/cloud_registered remap")
        forbidden = as_mapping(b1_planenv.get("forbidden_actions_confirmed"))
        for key in [
            "edited_references",
            "published_position_cmd",
            "runtime_recorder_run",
            "planner_runtime_launched",
            "claimed_planning_bspline_runtime",
            "fake_pointcloud_or_grid_used",
            "ue_global_truth_used_as_planner_input",
            "fastlio_path_converted_to_trajectory",
            "keyboard_pose_used",
            "replacement_planner_handwritten",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"plan_env port forbidden action not confirmed false: {key}")
        if "planner" not in report["claim_scope"] and b1_planenv.get("quality_status") != "build_surface_only":
            report["issues"].append("B1 plan_env task must remain build_surface_only while planner claim is excluded")
    b1_path_bspline = as_mapping(ros2.get("position_command_b1_path_bspline_port"))
    if b1_path_bspline:
        require_path(report, "ros2.b1_path_bspline_port.return_packet", b1_path_bspline.get("return_packet"))
        build_status = as_mapping(b1_path_bspline.get("build_status"))
        commands = as_list(build_status.get("commands"))
        for command_index, command_info in enumerate(commands):
            for log_index, log_path in enumerate(as_list(as_mapping(command_info).get("logs"))):
                require_path(report, f"ros2.b1_path_bspline_port.build_log[{command_index}][{log_index}]", log_path)
        for index, artifact in enumerate(as_list(b1_path_bspline.get("installed_artifacts"))):
            require_path(report, f"ros2.b1_path_bspline_port.installed_artifact[{index}]", artifact)
        for index, item in enumerate(as_list(b1_path_bspline.get("classification_logs"))):
            require_path(report, f"ros2.b1_path_bspline_port.classification_log[{index}]", as_mapping(item).get("path"))
        summary = as_mapping(b1_path_bspline.get("summary"))
        package_state = as_mapping(b1_path_bspline.get("workspace_package_state_after_012"))
        contract = as_mapping(b1_path_bspline.get("runtime_contract_preserved"))
        if b1_path_bspline.get("status") == "completed_preflight":
            report["warnings"].append("B1 path_searching/bspline_opt port built isolated ROS2 surfaces only; planner runtime remains blocked")
        if summary.get("path_searching_ros2_buildable") is not True:
            report["issues"].append("B1 path_searching/bspline_opt task must preserve path_searching_ros2_buildable=true")
        if summary.get("bspline_opt_ros2_buildable") is not True:
            report["issues"].append("B1 path_searching/bspline_opt task must preserve bspline_opt_ros2_buildable=true")
        for package in ["plan_env", "path_searching", "bspline_opt"]:
            if package not in as_list(package_state.get("ros2_ament_packages")):
                report["issues"].append(f"B1 path/bspline task must preserve ROS2 ament package: {package}")
            if package in as_list(package_state.get("catkin_only_packages_remaining")):
                report["issues"].append(f"{package} must no longer be listed as catkin-only after task 012")
        for package in ["traj_utils", "quadrotor_msgs"]:
            if package not in as_list(package_state.get("catkin_only_packages_remaining")):
                report["issues"].append(f"B1 path/bspline task must preserve remaining blocker package: {package}")
        if package_state.get("can_start_real_planning_bspline_runtime") is not False:
            report["issues"].append("B1 path/bspline task must not mark real /planning/bspline runtime startable")
        if package_state.get("can_enter_real_position_cmd_runtime_recorder") is not False:
            report["issues"].append("B1 path/bspline task must not mark real PositionCommand recorder startable")
        if contract.get("intended_odom_remap_from_011") != "/grid_map/odom:=/Odometry":
            report["issues"].append("B1 path/bspline task must preserve /grid_map/odom:=/Odometry remap")
        if contract.get("intended_cloud_remap_from_011") != "/grid_map/cloud:=/cloud_registered":
            report["issues"].append("B1 path/bspline task must preserve /grid_map/cloud:=/cloud_registered remap")
        forbidden = as_mapping(b1_path_bspline.get("forbidden_actions_confirmed"))
        for key in [
            "edited_references",
            "published_position_cmd",
            "runtime_recorder_run",
            "planner_runtime_launched",
            "claimed_planning_bspline_runtime",
            "fake_pointcloud_or_grid_used",
            "ue_global_truth_used_as_planner_input",
            "fastlio_path_converted_to_trajectory",
            "keyboard_pose_used",
            "replacement_planner_handwritten",
            "expanded_to_plan_manage_runtime",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"path/bspline port forbidden action not confirmed false: {key}")
        if "planner" not in report["claim_scope"] and b1_path_bspline.get("quality_status") != "build_surface_only":
            report["issues"].append("B1 path/bspline task must remain build_surface_only while planner claim is excluded")
    b1_traj_quadmsgs = as_mapping(ros2.get("position_command_b1_traj_quadmsgs_port"))
    if b1_traj_quadmsgs:
        require_path(report, "ros2.b1_traj_quadmsgs_port.return_packet", b1_traj_quadmsgs.get("return_packet"))
        build_status = as_mapping(b1_traj_quadmsgs.get("build_status"))
        for command_index, command_info in enumerate(as_list(build_status.get("commands"))):
            require_path(
                report,
                f"ros2.b1_traj_quadmsgs_port.red_build_log[{command_index}]",
                as_mapping(command_info).get("red_log"),
            )
            for log_index, log_path in enumerate(as_list(as_mapping(command_info).get("green_logs"))):
                require_path(report, f"ros2.b1_traj_quadmsgs_port.green_log[{command_index}][{log_index}]", log_path)
        for index, artifact in enumerate(as_list(b1_traj_quadmsgs.get("installed_artifacts"))):
            require_path(report, f"ros2.b1_traj_quadmsgs_port.installed_artifact[{index}]", artifact)
        for index, item in enumerate(as_list(b1_traj_quadmsgs.get("classification_logs"))):
            require_path(report, f"ros2.b1_traj_quadmsgs_port.classification_log[{index}]", as_mapping(item).get("path"))
        summary = as_mapping(b1_traj_quadmsgs.get("summary"))
        package_state = as_mapping(b1_traj_quadmsgs.get("workspace_package_state_after_013"))
        contract = as_mapping(b1_traj_quadmsgs.get("runtime_contract_preserved"))
        if b1_traj_quadmsgs.get("status") == "completed_preflight":
            report["warnings"].append("B1 traj_utils/quadrotor_msgs port built isolated ROS2 support surfaces only; full plan_manage runtime remains blocked")
        if summary.get("quadrotor_msgs_ros2_buildable") is not True:
            report["issues"].append("B1 traj/quadmsgs task must preserve quadrotor_msgs_ros2_buildable=true")
        if summary.get("traj_utils_ros2_buildable") is not True:
            report["issues"].append("B1 traj/quadmsgs task must preserve traj_utils_ros2_buildable=true")
        for package in ["plan_env", "path_searching", "bspline_opt", "quadrotor_msgs", "traj_utils"]:
            if package not in as_list(package_state.get("ros2_ament_packages")):
                report["issues"].append(f"B1 traj/quadmsgs task must preserve ROS2 ament package: {package}")
            if package in as_list(package_state.get("catkin_only_packages_remaining")):
                report["issues"].append(f"{package} must not remain catkin-only after task 013")
        if as_list(package_state.get("catkin_only_packages_remaining")):
            report["issues"].append("B1 traj/quadmsgs task must preserve empty catkin-only package list after 013")
        if package_state.get("can_start_real_planning_bspline_runtime") is not False:
            report["issues"].append("B1 traj/quadmsgs task must not mark real /planning/bspline runtime startable")
        if package_state.get("can_enter_real_position_cmd_runtime_recorder") is not False:
            report["issues"].append("B1 traj/quadmsgs task must not mark real PositionCommand recorder startable")
        if contract.get("external_position_command_rule", "").startswith("MoSim external command surface remains") is not True:
            report["issues"].append("B1 traj/quadmsgs task must preserve mosim_msgs/PositionCommand as external command surface")
        forbidden = as_mapping(b1_traj_quadmsgs.get("forbidden_actions_confirmed"))
        for key in [
            "edited_references",
            "published_position_cmd",
            "runtime_recorder_run",
            "planner_runtime_launched",
            "claimed_planning_bspline_runtime",
            "fake_pointcloud_or_grid_used",
            "ue_global_truth_used_as_planner_input",
            "fastlio_path_converted_to_trajectory",
            "keyboard_pose_used",
            "replacement_planner_handwritten",
            "expanded_to_plan_manage_runtime",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"traj/quadmsgs port forbidden action not confirmed false: {key}")
        if "planner" not in report["claim_scope"] and b1_traj_quadmsgs.get("quality_status") != "build_surface_only":
            report["issues"].append("B1 traj/quadmsgs task must remain build_surface_only while planner claim is excluded")
    b1_planmanage = as_mapping(ros2.get("position_command_b1_planmanage_link_preflight"))
    if b1_planmanage:
        require_path(report, "ros2.b1_planmanage_link_preflight.return_packet", b1_planmanage.get("return_packet"))
        build_status = as_mapping(b1_planmanage.get("build_status"))
        for command_index, command_info in enumerate(as_list(build_status.get("commands"))):
            command = as_mapping(command_info)
            if command.get("log"):
                require_path(
                    report,
                    f"ros2.b1_planmanage_link_preflight.build_log[{command_index}]",
                    command.get("log"),
                )
            for log_index, log_path in enumerate(as_list(command.get("logs"))):
                require_path(
                    report,
                    f"ros2.b1_planmanage_link_preflight.build_log[{command_index}][{log_index}]",
                    log_path,
                )
        for index, artifact in enumerate(as_list(b1_planmanage.get("installed_artifacts"))):
            require_path(report, f"ros2.b1_planmanage_link_preflight.installed_artifact[{index}]", artifact)
        for index, artifact in enumerate(as_list(b1_planmanage.get("evidence_artifacts"))):
            require_path(report, f"ros2.b1_planmanage_link_preflight.evidence_artifact[{index}]", artifact)
        summary = as_mapping(b1_planmanage.get("summary"))
        runtime = as_mapping(b1_planmanage.get("runtime_boundary"))
        forbidden = as_mapping(b1_planmanage.get("forbidden_actions_confirmed"))
        next_task = as_mapping(b1_planmanage.get("next_allowed_task"))
        if b1_planmanage.get("status") == "completed_preflight":
            report["warnings"].append("B1 plan_manage link preflight built isolated EGO planner surfaces only; planner runtime remains blocked")
        for key in [
            "full_plan_manage_link_preflight_passed",
            "ego_planner_manager_preflight_buildable",
            "ego_replan_fsm_preflight_buildable",
            "ego_planner_node_preflight_linkable",
        ]:
            if summary.get(key) is not True:
                report["issues"].append(f"B1 plan_manage link preflight must preserve {key}=true")
        if summary.get("runtime_reachability_claim") != "not_claimed":
            report["issues"].append("B1 plan_manage link preflight must not claim runtime reachability")
        if summary.get("planning_bspline_runtime_evidence") != "not_claimed":
            report["issues"].append("B1 plan_manage link preflight must not claim /planning/bspline runtime evidence")
        if summary.get("position_cmd_evidence") != "not_claimed":
            report["issues"].append("B1 plan_manage link preflight must not claim /position_cmd evidence")
        if build_status.get("status") != "passed_with_incremental_install":
            report["issues"].append("B1 plan_manage link preflight build status must remain passed_with_incremental_install")
        for key in [
            "planner_runtime_launched",
            "runtime_recorder_run",
            "position_cmd_published",
            "planning_bspline_published_as_evidence",
            "real_local_map_odom_runtime_validated",
            "closed_loop_claim",
        ]:
            if runtime.get(key) is not False:
                report["issues"].append(f"plan_manage runtime boundary must preserve {key}=false")
        for key in [
            "edited_references",
            "published_position_cmd",
            "published_planning_bspline_as_runtime_evidence",
            "runtime_recorder_run",
            "planner_runtime_launched",
            "fake_pointcloud_or_grid_used",
            "ue_global_truth_used_as_planner_input",
            "fastlio_path_converted_to_trajectory",
            "keyboard_pose_used",
            "replacement_planner_handwritten",
            "claimed_planner_or_closed_loop_acceptance",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"plan_manage preflight forbidden action not confirmed false: {key}")
        if next_task.get("can_enter_real_position_cmd_runtime_recorder") is not False:
            report["issues"].append("B1 plan_manage link preflight must not allow the PositionCommand recorder yet")
        if "runtime-disabled" not in str(next_task.get("recommended", "")):
            report["issues"].append("B1 plan_manage next task must stay runtime-disabled before recorder use")
        if "planner" not in report["claim_scope"] and b1_planmanage.get("quality_status") != "link_preflight_only":
            report["issues"].append("B1 plan_manage task must remain link_preflight_only while planner claim is excluded")
    b1_launch_audit = as_mapping(ros2.get("position_command_b1_runtime_disabled_launch_audit"))
    if b1_launch_audit:
        require_path(report, "ros2.b1_runtime_disabled_launch_audit.return_packet", b1_launch_audit.get("return_packet"))
        for index, file_path in enumerate(as_list(b1_launch_audit.get("inspected_files"))):
            require_path(report, f"ros2.b1_runtime_disabled_launch_audit.inspected_file[{index}]", file_path)
        for index, artifact in enumerate(as_list(b1_launch_audit.get("evidence_artifacts"))):
            require_path(report, f"ros2.b1_runtime_disabled_launch_audit.evidence_artifact[{index}]", artifact)
        summary = as_mapping(b1_launch_audit.get("summary"))
        commands = as_mapping(b1_launch_audit.get("static_or_dry_run_commands"))
        remaps = as_mapping(b1_launch_audit.get("topic_remap_contract"))
        params = as_mapping(b1_launch_audit.get("parameter_audit"))
        next_gate = as_mapping(b1_launch_audit.get("next_pmo_approval_gate"))
        forbidden = as_mapping(b1_launch_audit.get("forbidden_actions_confirmed"))
        if b1_launch_audit.get("status") == "completed_static_audit":
            report["warnings"].append("B1 runtime-disabled launch audit completed static review only; runtime guard/config artifact remains blocked")
        if summary.get("ready_for_later_pmo_approved_runtime_disabled_smoke") is not True:
            report["issues"].append("B1 launch audit must preserve readiness only for later PMO-approved runtime-disabled smoke")
        if summary.get("ready_for_real_planner_runtime") is not False:
            report["issues"].append("B1 launch audit must not mark real planner runtime ready")
        if summary.get("ready_for_runtime_recorder") is not False:
            report["issues"].append("B1 launch audit must not mark runtime recorder ready")
        if commands.get("ros2_run_or_launch_executed") is not False:
            report["issues"].append("B1 launch audit must preserve that no ros2 run/launch was executed")
        if "ros2 run ego_planner ego_planner_node_preflight" not in str(commands.get("candidate_command_text_not_executed", "")):
            report["issues"].append("B1 launch audit must preserve non-executed candidate command text")
        required_remaps = as_list(remaps.get("required_remaps_for_planner_node"))
        remap_pairs = {(as_mapping(item).get("from"), as_mapping(item).get("to")) for item in required_remaps}
        for pair in [("/odom_world", "/Odometry"), ("/grid_map/odom", "/Odometry"), ("/grid_map/cloud", "/cloud_registered")]:
            if pair not in remap_pairs:
                report["issues"].append(f"B1 launch audit must preserve required remap {pair[0]} -> {pair[1]}")
        if as_mapping(remaps.get("command_adapter_surface")).get("required_disabled_parameter") != "publish_enabled:=false":
            report["issues"].append("B1 launch audit must preserve traj_server publish_enabled:=false guard")
        if params.get("direct_legacy_xml_reuse_safe") is not False:
            report["issues"].append("B1 launch audit must preserve that legacy XML reuse is unsafe")
        next_gate_name = str(next_gate.get("gate_name", "")).lower().replace("-", "_")
        if "runtime_disabled" not in next_gate_name:
            report["issues"].append("B1 launch audit next gate must remain runtime-disabled")
        for key in [
            "edited_references",
            "launched_planner_runtime",
            "published_position_cmd",
            "published_planning_bspline_as_runtime_evidence",
            "ran_runtime_recorder",
            "used_fake_pointcloud_or_grid",
            "used_ue_global_truth_as_planner_input",
            "converted_fastlio_path_to_trajectory",
            "used_keyboard_pose",
            "claimed_planner_or_closed_loop_acceptance",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"runtime-disabled launch audit forbidden action not confirmed false: {key}")
        if "planner" not in report["claim_scope"] and b1_launch_audit.get("quality_status") != "runtime_disabled_static_audit_only":
            report["issues"].append("B1 launch audit must remain runtime_disabled_static_audit_only while planner claim is excluded")
    b1_launch_config = as_mapping(ros2.get("position_command_b1_runtime_disabled_launch_config"))
    if b1_launch_config:
        require_path(report, "ros2.b1_runtime_disabled_launch_config.return_packet", b1_launch_config.get("return_packet"))
        inventory = as_mapping(b1_launch_config.get("artifact_inventory"))
        require_path(report, "ros2.b1_runtime_disabled_launch_config.inventory", inventory.get("inventory_path"))
        for index, item in enumerate(as_list(inventory.get("source_artifacts"))):
            require_path(report, f"ros2.b1_runtime_disabled_launch_config.source_artifact[{index}]", as_mapping(item).get("path"))
        for index, item in enumerate(as_list(inventory.get("installed_artifacts"))):
            require_path(report, f"ros2.b1_runtime_disabled_launch_config.installed_artifact[{index}]", as_mapping(item).get("path"))
        diff_summary = as_mapping(b1_launch_config.get("config_diff_summary"))
        require_path(report, "ros2.b1_runtime_disabled_launch_config.config_diff_summary", diff_summary.get("summary_path"))
        validation = as_mapping(b1_launch_config.get("static_validation_output"))
        for index, command in enumerate(as_list(validation.get("commands_executed"))):
            command_map = as_mapping(command)
            if command_map.get("log"):
                require_path(report, f"ros2.b1_runtime_disabled_launch_config.validation_log[{index}]", command_map.get("log"))
            for log_index, log_path in enumerate(as_list(command_map.get("logs"))):
                require_path(
                    report,
                    f"ros2.b1_runtime_disabled_launch_config.validation_log[{index}][{log_index}]",
                    log_path,
                )
        summary = as_mapping(b1_launch_config.get("summary"))
        remaps = as_mapping(b1_launch_config.get("topic_remap_contract"))
        next_gate = as_mapping(b1_launch_config.get("next_pmo_gate"))
        forbidden = as_mapping(b1_launch_config.get("forbidden_actions_confirmed"))
        if b1_launch_config.get("status") == "completed":
            report["warnings"].append("B1 runtime-disabled launch/config artifact exists, but no ros2 launch/run or planner runtime evidence is claimed")
        if b1_launch_config.get("quality_status") != "runtime_disabled_static_config_only":
            report["issues"].append("B1 launch/config must remain runtime_disabled_static_config_only")
        if summary.get("ready_for_later_pmo_approved_runtime_disabled_smoke") is not True:
            report["issues"].append("B1 launch/config must preserve readiness only for later PMO-approved runtime-disabled smoke")
        if summary.get("ready_for_real_planner_runtime") is not False:
            report["issues"].append("B1 launch/config must not mark real planner runtime ready")
        if summary.get("ready_for_runtime_recorder") is not False:
            report["issues"].append("B1 launch/config must not mark runtime recorder ready")
        if summary.get("runtime_or_recorder_executed") is not False:
            report["issues"].append("B1 launch/config must preserve that no runtime or recorder was executed")
        if validation.get("ros2_launch_executed") is not False:
            report["issues"].append("B1 launch/config must preserve that no ros2 launch was executed")
        if validation.get("ros2_run_executed") is not False:
            report["issues"].append("B1 launch/config must preserve that no ros2 run was executed")
        encoded_pairs = {
            (as_mapping(item).get("from"), as_mapping(item).get("to"))
            for item in as_list(remaps.get("encoded_remaps"))
        }
        for pair in [("/odom_world", "/Odometry"), ("/grid_map/odom", "/Odometry"), ("/grid_map/cloud", "/cloud_registered")]:
            if pair not in encoded_pairs:
                report["issues"].append(f"B1 launch/config must preserve encoded remap {pair[0]} -> {pair[1]}")
        for forbidden_topic in ["/planning/bspline", "/position_cmd", "/mosim/planner/position_cmd"]:
            if forbidden_topic not in as_list(remaps.get("not_claimed_topics")):
                report["issues"].append(f"B1 launch/config must preserve not-claimed topic {forbidden_topic}")
        if next_gate.get("approval_required_before_running") is not True:
            report["issues"].append("B1 launch/config next smoke gate must require PMO approval before running")
        next_gate_name = str(next_gate.get("gate_name", "")).lower().replace("-", "_")
        if "runtime_disabled" not in next_gate_name:
            report["issues"].append("B1 launch/config next gate must remain runtime-disabled")
        for key in [
            "edited_references",
            "launched_planner_runtime",
            "published_position_cmd",
            "published_planning_bspline_as_runtime_evidence",
            "ran_runtime_recorder",
            "used_fake_pointcloud_or_grid",
            "used_ue_global_truth_as_planner_input",
            "converted_fastlio_path_to_trajectory",
            "used_keyboard_pose",
            "claimed_planner_or_closed_loop_acceptance",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"runtime-disabled launch/config forbidden action not confirmed false: {key}")
    b1_disabled_smoke = as_mapping(ros2.get("position_command_b1_runtime_disabled_smoke"))
    if b1_disabled_smoke:
        require_path(report, "ros2.b1_runtime_disabled_smoke.return_packet", b1_disabled_smoke.get("return_packet"))
        smoke = as_mapping(b1_disabled_smoke.get("runtime_disabled_smoke"))
        artifacts = as_mapping(smoke.get("artifacts"))
        require_path(report, "ros2.b1_runtime_disabled_smoke.script", artifacts.get("script"))
        require_path(report, "ros2.b1_runtime_disabled_smoke.command", artifacts.get("command"))
        require_path(report, "ros2.b1_runtime_disabled_smoke.log", artifacts.get("log"))
        require_path(report, "ros2.b1_runtime_disabled_smoke.wrapper_exit", artifacts.get("wrapper_exit"))
        for index, artifact in enumerate(as_list(b1_disabled_smoke.get("evidence_artifacts"))):
            require_path(report, f"ros2.b1_runtime_disabled_smoke.evidence_artifact[{index}]", artifact)
        summary = as_mapping(b1_disabled_smoke.get("summary"))
        forbidden = as_mapping(b1_disabled_smoke.get("forbidden_actions_confirmed"))
        forbidden_topics = as_mapping(smoke.get("forbidden_topics_seen"))
        if b1_disabled_smoke.get("quality_status") != "runtime_disabled_smoke_passed":
            report["issues"].append("B1 runtime-disabled smoke must remain runtime_disabled_smoke_passed")
        if smoke.get("launch_exit_code") != 0:
            report["issues"].append("B1 runtime-disabled smoke launch_exit_code must be 0")
        if smoke.get("guard_message_seen") is not True:
            report["issues"].append("B1 runtime-disabled smoke must preserve guard_message_seen=true")
        if smoke.get("clean_process_finish_seen") is not True:
            report["issues"].append("B1 runtime-disabled smoke must preserve clean process finish evidence")
        if smoke.get("planner_runtime_started") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark planner runtime started")
        if smoke.get("position_command_published") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark PositionCommand published")
        if smoke.get("planning_bspline_published_as_runtime_evidence") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark /planning/bspline runtime evidence published")
        if smoke.get("runtime_recorder_run") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark runtime recorder run")
        if smoke.get("closed_loop_claim") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark closed_loop claim")
        for topic in ["/planning/bspline", "/position_cmd", "/mosim/planner/position_cmd"]:
            if forbidden_topics.get(topic) is not False:
                report["issues"].append(f"B1 runtime-disabled smoke must preserve forbidden topic absent: {topic}")
        if summary.get("ready_for_real_planner_runtime") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark real planner runtime ready")
        if summary.get("ready_for_runtime_recorder") is not False:
            report["issues"].append("B1 runtime-disabled smoke must not mark runtime recorder ready")
        for key in [
            "edited_references",
            "launched_planner_runtime",
            "published_position_cmd",
            "published_planning_bspline_as_runtime_evidence",
            "ran_runtime_recorder",
            "used_fake_pointcloud_or_grid",
            "used_ue_global_truth_as_planner_input",
            "converted_fastlio_path_to_trajectory",
            "used_keyboard_pose",
            "claimed_planner_or_closed_loop_acceptance",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"runtime-disabled smoke forbidden action not confirmed false: {key}")
        report["warnings"].append("B1 runtime-disabled smoke passed guard/exiting path only; real planner runtime remains blocked")

    b1_input_gate = as_mapping(ros2.get("position_command_b1_real_planner_input_gate"))
    if b1_input_gate:
        require_path(report, "ros2.b1_real_planner_input_gate.blocker_packet", b1_input_gate.get("blocker_packet"))
        topic_probe = as_mapping(b1_input_gate.get("topic_availability_rate_type_probe"))
        require_path(report, "ros2.b1_real_planner_input_gate.probe_summary", topic_probe.get("probe_summary"))
        require_path(report, "ros2.b1_real_planner_input_gate.command_script", topic_probe.get("command_script"))
        require_path(report, "ros2.b1_real_planner_input_gate.topic_list_typed", topic_probe.get("topic_list_typed"))
        for topic, expected_type in [
            ("/Odometry", "nav_msgs/msg/Odometry"),
            ("/cloud_registered", "sensor_msgs/msg/PointCloud2"),
        ]:
            required = as_mapping(as_mapping(topic_probe.get("required_inputs")).get(topic))
            if required.get("present") is not False:
                report["issues"].append(f"B1 real planner input gate must preserve {topic} absent")
            if required.get("expected_type") != expected_type:
                report["issues"].append(f"B1 real planner input gate must preserve {topic} expected type")
            require_path(report, f"ros2.b1_real_planner_input_gate.{topic}.topic_info", required.get("topic_info_log"))
            require_path(report, f"ros2.b1_real_planner_input_gate.{topic}.topic_hz", required.get("topic_hz_log"))
        gate_decision = as_mapping(b1_input_gate.get("gate_decision"))
        forbidden = as_mapping(b1_input_gate.get("forbidden_actions_confirmed"))
        if b1_input_gate.get("status") != "blocked":
            report["issues"].append("B1 real planner input gate 018 must remain blocked")
        if b1_input_gate.get("quality_status") != "real_planner_input_gate_blocked":
            report["issues"].append("B1 real planner input gate must preserve real_planner_input_gate_blocked")
        if b1_input_gate.get("real_odometry_present_now") is not False:
            report["issues"].append("B1 real planner input gate must preserve real_odometry_present_now=false")
        if b1_input_gate.get("real_cloud_registered_present_now") is not False:
            report["issues"].append("B1 real planner input gate must preserve real_cloud_registered_present_now=false")
        if b1_input_gate.get("runtime_disabled_false_may_be_safely_attempted_later") is not False:
            report["issues"].append("B1 real planner input gate must not clear runtime_disabled=false startup")
        if gate_decision.get("can_attempt_runtime_disabled_false_in_later_separate_task") is not False:
            report["issues"].append("B1 input gate must preserve can_attempt_runtime_disabled_false=false")
        for key in [
            "ran_position_command_recorder",
            "published_position_cmd",
            "published_mosim_planner_position_cmd",
            "published_planning_bspline_as_runtime_evidence",
            "used_fake_pointcloud_or_grid",
            "used_ue_global_truth_as_planner_input",
            "converted_fastlio_path_to_trajectory",
            "used_keyboard_pose",
            "handwrote_replacement_planner",
            "claimed_planner_or_closed_loop_acceptance",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"B1 input gate forbidden action not confirmed false: {key}")
        report["warnings"].append("B1 real planner input gate 018 remains historical missing-input blocker evidence")

    b1_odom_cloud = as_mapping(ros2.get("position_command_b1_odom_cloud_restore"))
    if b1_odom_cloud:
        require_path(report, "ros2.b1_odom_cloud_restore.return_packet", b1_odom_cloud.get("return_packet"))
        require_path(report, "ros2.b1_odom_cloud_restore.evidence_dir", b1_odom_cloud.get("evidence_dir"))
        require_path(report, "ros2.b1_odom_cloud_restore.summary_json", b1_odom_cloud.get("summary_json"))
        required_topics = as_mapping(b1_odom_cloud.get("required_topics"))
        for topic, expected_type in [
            ("/Odometry", "nav_msgs/msg/Odometry"),
            ("/cloud_registered", "sensor_msgs/msg/PointCloud2"),
        ]:
            topic_info = as_mapping(required_topics.get(topic))
            if topic_info.get("present_in_runtime_recording") is not True:
                report["issues"].append(f"B1 odom/cloud restore must preserve {topic} present_in_runtime_recording=true")
            if topic_info.get("expected_type") != expected_type:
                report["issues"].append(f"B1 odom/cloud restore must preserve {topic} expected type")
            if float(topic_info.get("recorded_count", 0) or 0) <= 0:
                report["issues"].append(f"B1 odom/cloud restore must preserve nonzero {topic} recorded_count")
            require_path(report, f"ros2.b1_odom_cloud_restore.{topic}.sample_file", topic_info.get("sample_file"))
        truth_eval = as_mapping(b1_odom_cloud.get("truth_evaluation"))
        truth_metrics = as_mapping(truth_eval.get("metrics"))
        if truth_eval.get("status") != "pass":
            report["issues"].append("B1 odom/cloud restore must preserve primary truth_evaluation pass")
        if float(truth_metrics.get("position_rmse_m", 999.0) or 999.0) > 0.5:
            report["issues"].append("B1 odom/cloud restore primary position_rmse_m must remain within the input-gate threshold")
        input_probe = as_mapping(b1_odom_cloud.get("input_source_probe"))
        acceptance = as_mapping(input_probe.get("acceptance"))
        for key in ["livox_nonzero", "imu_nonzero", "livox_rate_ok", "imu_rate_ok", "time_delta_ok", "point_num_ok"]:
            if acceptance.get(key) is not True:
                report["issues"].append(f"B1 odom/cloud restore input probe must preserve acceptance.{key}=true")
        if b1_odom_cloud.get("ready_for_later_separate_runtime_disabled_false_startup_probe") is not True:
            report["issues"].append("B1 odom/cloud restore must preserve later separate startup probe readiness")
        if b1_odom_cloud.get("planner_ready") is not False:
            report["issues"].append("B1 odom/cloud restore must not mark planner_ready")
        if b1_odom_cloud.get("closed_loop_ready") is not False:
            report["issues"].append("B1 odom/cloud restore must not mark closed_loop_ready")
        if b1_odom_cloud.get("position_command_recorder_allowed") is not False:
            report["issues"].append("B1 odom/cloud restore must not allow PositionCommand recorder")
        if b1_odom_cloud.get("planner_startup_executed") is not False:
            report["issues"].append("B1 odom/cloud restore must preserve that no planner startup was executed")
        forbidden = as_mapping(b1_odom_cloud.get("forbidden_actions_confirmed"))
        for key in [
            "ran_position_command_recorder",
            "published_position_cmd",
            "published_mosim_planner_position_cmd",
            "ran_runtime_disabled_false_planner_startup",
            "published_planning_bspline_as_accepted_runtime_evidence",
            "used_fake_pointcloud_or_grid",
            "used_ue_global_truth_as_planner_input",
            "converted_fastlio_path_to_trajectory",
            "used_keyboard_pose",
            "handwrote_replacement_planner",
            "claimed_planner_ready",
            "claimed_closed_loop_ready",
        ]:
            if forbidden.get(key) is not False:
                report["issues"].append(f"B1 odom/cloud restore forbidden action not confirmed false: {key}")
        report["warnings"].append("B1 odom/cloud restore 019 restored /Odometry and /cloud_registered only; planner startup remains a separate blocked gate")

    b1_long_source = as_mapping(ros2.get("position_command_b1_long_source_startup_discipline_rerun"))
    if b1_long_source:
        require_path(report, "ros2.b1_long_source_startup_discipline.return_packet", b1_long_source.get("return_packet"))
        require_path(report, "ros2.b1_long_source_startup_discipline.evidence_dir", b1_long_source.get("evidence_dir"))
        forbidden_topics = as_mapping(b1_long_source.get("forbidden_topics_absent_or_zero"))
        if b1_long_source.get("status") != "completed_long_source_no_goal_precondition_passed":
            report["issues"].append("B1 long-source 031 must remain a completed no-goal precondition pass")
        if b1_long_source.get("quality_status") != "no_goal_long_source_startup_discipline_precondition_passed":
            report["issues"].append("B1 long-source 031 must remain a no-goal startup-discipline precondition")
        if b1_long_source.get("source_frame_count") != 120:
            report["issues"].append("B1 long-source 031 must preserve 120 source frames")
        if b1_long_source.get("startup_order") != "FAST-LIO -> first Livox frame -> IMU":
            report["issues"].append("B1 long-source 031 must preserve the 030 startup order")
        for key in ["livox_count", "imu_count", "odometry_count", "cloud_registered_count"]:
            if float(b1_long_source.get(key, 0) or 0) <= 0:
                report["issues"].append(f"B1 long-source 031 must preserve nonzero {key}")
        if b1_long_source.get("loopback_total") != 0:
            report["issues"].append("B1 long-source 031 must preserve zero loop-back events")
        if b1_long_source.get("no_effective_points") != 0:
            report["issues"].append("B1 long-source 031 must preserve zero No Effective Points")
        for topic in ["/position_cmd", "/mosim/planner/position_cmd", "/planning/bspline"]:
            if forbidden_topics.get(topic) is not False:
                report["issues"].append(f"B1 long-source 031 must preserve forbidden topic absent: {topic}")
        if b1_long_source.get("cleanup") != "no_matching_processes":
            report["issues"].append("B1 long-source 031 must preserve clean process cleanup")
        report["warnings"].append("B1 long-source 031 restored no-goal FAST-LIO outputs only; RViz, local map, planner, and PositionCommand remain blocked")

    b1_032 = as_mapping(ros2.get("position_command_b1_no_goal_odom_tf_rviz_preflight_032"))
    if b1_032:
        require_path(report, "ros2.b1_032.blocker_packet", b1_032.get("blocker_packet"))
        require_path(report, "ros2.b1_032.evidence_dir", b1_032.get("evidence_dir"))
        require_path(report, "ros2.b1_032.summary", b1_032.get("summary"))
        prior_dispatch = as_mapping(b1_032.get("prior_dispatch_surface_blockers"))
        require_path(report, "ros2.b1_032.prior_dispatch.coagentops_blocker_packet", prior_dispatch.get("coagentops_blocker_packet"))
        require_path(report, "ros2.b1_032.prior_dispatch.pmo_dispatch_blocker_packet", prior_dispatch.get("pmo_dispatch_blocker_packet"))
        observed = as_mapping(b1_032.get("observed"))
        forbidden_topics = as_mapping(b1_032.get("forbidden_topics_present"))
        forbidden_actions = as_mapping(b1_032.get("forbidden_actions"))
        if b1_032.get("status") != "blocked_before_goal":
            report["issues"].append("ROS2 032 must remain blocked_before_goal after the single no-goal runtime probe failed")
        if b1_032.get("quality_status") != "no_goal_odom_tf_rviz_preflight_blocked_before_goal":
            report["issues"].append("ROS2 032 must be classified as a no-goal odom/TF/RViz preflight technical blocker")
        if prior_dispatch.get("resolved_by_noop_recovery") is not True:
            report["issues"].append("ROS2 032 must preserve that prior dispatch-surface blockers were resolved by no-op recovery")
        if as_int(observed.get("loopback_total")) != 3:
            report["issues"].append("ROS2 032 must preserve loopback_total=3")
        if as_int(observed.get("odometry_count")) != 0:
            report["issues"].append("ROS2 032 must preserve odometry_count=0")
        if as_int(observed.get("cloud_registered_count")) != 0:
            report["issues"].append("ROS2 032 must preserve cloud_registered_count=0")
        if as_int(observed.get("livox_probe_count")) != 0:
            report["issues"].append("ROS2 032 must preserve livox_probe_count=0")
        if b1_032.get("rviz2_cli_available") is not True:
            report["issues"].append("ROS2 032 must preserve RViz2 CLI availability evidence")
        if b1_032.get("truth_to_fastlio_bridge_observed") is not False:
            report["issues"].append("ROS2 032 must preserve missing ue_world<->camera_init bridge risk")
        for topic in ["/position_cmd", "/mosim/planner/position_cmd", "/planning/bspline"]:
            if forbidden_topics.get(topic) is not False:
                report["issues"].append(f"ROS2 032 must preserve forbidden topic absent: {topic}")
        for action in ["position_command_recorder_ran", "adapter_20hz_started", "planner_goal_published", "rviz_gui_opened"]:
            if forbidden_actions.get(action) is not False:
                report["issues"].append(f"ROS2 032 must preserve forbidden action false: {action}")
        report["warnings"].append("ROS2 032 started after no-op recovery but blocked before goal; TF/RViz CLI evidence cannot override failed FAST-LIO/source gates")

    planner = as_mapping(manifest.get("planner"))
    require_path(report, "planner.setpoint_trace", planner.get("setpoint_trace"))
    if planner.get("global_truth_used_as_input") is not False:
        report["issues"].append("planner.global_truth_used_as_input must be false")

    ue = as_mapping(manifest.get("ue"))
    require_path(report, "ue.sensor_oracle_log", ue.get("sensor_oracle_log"))
    require_path(report, "ue.command_echo_log", ue.get("command_echo_log"))
    require_path(report, "ue.command_input_log", ue.get("command_input_log"))
    require_path(report, "ue.command_adapter_smoke_json", ue.get("command_adapter_smoke_json"))
    require_path(report, "ue.command_sender_source", ue.get("command_sender_source"))
    require_path(report, "ue.command_sender_header", ue.get("command_sender_header"))
    require_path(report, "ue.command_sender_contract", ue.get("command_sender_contract"))
    require_path(report, "ue.command_sender_loopback_smoke_json", ue.get("command_sender_loopback_smoke_json"))
    require_path(report, "ue.command_sender_loopback_received", ue.get("command_sender_loopback_received"))
    if str(ue.get("no_pose_overwrite_status", "")) != "pass":
        report["issues"].append("ue.no_pose_overwrite_status must be pass")
    if ue.get("not_runtime_ue_console") is not True:
        report["issues"].append("current P0 UE command adapter evidence must be marked not_runtime_ue_console=true")
    if ue.get("command_sender_source_status") != "source_level_static_check_pass":
        report["issues"].append("UE command sender source status must remain source_level_static_check_pass until live ack exists")
    if path_exists(ue.get("command_echo_log")):
        echo_report = run_json_checker(
            [
                sys.executable,
                str(ROOT / "Scripts" / "UE5" / "check_ue_command_echo_contract.py"),
                str(repo_path(ue.get("command_echo_log"))),
            ]
        )
        report["ue_command_echo_contract"] = echo_report
        if echo_report.get("ok") is not True:
            report["issues"].append("UE command echo contract failed: " + "; ".join(as_list(echo_report.get("issues"))))
        if int(echo_report.get("placeholder_rows", 0)) > 0:
            report["warnings"].append("UE command echo is placeholder-only; runtime command/ack implementation remains open")
        if int(echo_report.get("runtime_ack_rows", 0)) > 0 and ue.get("not_runtime_ue_console") is True:
            report["warnings"].append("UE command adapter smoke has accepted/rejected echo rows, but it is offline-only and not runtime UE console evidence")
        if int(echo_report.get("runtime_ack_rows", 0)) == 0 and "closed_loop" in report["claim_scope"]:
            report["issues"].append("closed_loop claim requires runtime UE command echo ack rows")
    if path_exists(ue.get("command_adapter_smoke_json")):
        smoke = read_json(repo_path(ue.get("command_adapter_smoke_json")))
        report["ue_command_adapter_smoke"] = smoke
        if smoke.get("not_runtime_ue_console") is not True:
            report["issues"].append("UE command adapter smoke summary must keep not_runtime_ue_console=true")
        if smoke.get("source") != "offline_adapter_smoke":
            report["issues"].append("UE command adapter smoke source must be offline_adapter_smoke")
        if smoke.get("no_pose_overwrite_status") != "pass":
            report["issues"].append("UE command adapter smoke must preserve no_pose_overwrite_status=pass")
    if path_exists(ue.get("command_sender_contract")):
        source_contract = read_json(repo_path(ue.get("command_sender_contract")))
        report["ue_command_sender_source_contract"] = source_contract
        if source_contract.get("ok") is not True:
            report["issues"].append(
                "UE command sender source contract failed: " + "; ".join(as_list(source_contract.get("issues")))
            )
        if source_contract.get("not_runtime_ue_console") is not True:
            report["issues"].append("UE command sender source contract must keep not_runtime_ue_console=true")
        if source_contract.get("runtime_ack_required_before_acceptance") is not True:
            report["issues"].append("UE command sender source contract must require runtime ack before acceptance")
        if source_contract.get("no_pose_overwrite_status") != "pass":
            report["issues"].append("UE command sender source contract must preserve no_pose_overwrite_status=pass")
        report["warnings"].append("UE command sender exists only as source-level UDP packet surface; runtime MWORKS/ROS2 ack remains open")
    if path_exists(ue.get("command_sender_loopback_smoke_json")):
        loopback = read_json(repo_path(ue.get("command_sender_loopback_smoke_json")))
        report["ue_command_sender_loopback_smoke"] = loopback
        if loopback.get("ok") is not True:
            report["issues"].append("UE command sender loopback smoke failed: " + "; ".join(as_list(loopback.get("issues"))))
        if loopback.get("source") != "udp_loopback_smoke":
            report["issues"].append("UE command sender loopback source must be udp_loopback_smoke")
        if loopback.get("not_runtime_ue_console") is not True:
            report["issues"].append("UE command sender loopback must keep not_runtime_ue_console=true")
        if loopback.get("not_mworks_or_ros2_ack") is not True:
            report["issues"].append("UE command sender loopback must keep not_mworks_or_ros2_ack=true")
        if loopback.get("no_pose_overwrite_status") != "pass":
            report["issues"].append("UE command sender loopback must preserve no_pose_overwrite_status=pass")
        if int(loopback.get("received_packets", 0)) < 1:
            report["issues"].append("UE command sender loopback must receive at least one packet")
        report["warnings"].append("UE command sender loopback proves only UDP packet transport; runtime MWORKS/ROS2 ack remains open")

    ue_live_fixture = as_mapping(ue.get("live_echo_acceptance_fixture_contract"))
    if ue_live_fixture:
        require_path(report, "ue.live_echo_acceptance_fixture.return_packet", ue_live_fixture.get("return_packet"))
        require_path(report, "ue.live_echo_acceptance_fixture.evidence_dir", ue_live_fixture.get("evidence_dir"))
        if ue_live_fixture.get("quality_status") != "source_static_live_echo_acceptance_fixture_contract_passed":
            report["issues"].append("UE 008 live echo fixture must remain source/static contract evidence")
        if ue_live_fixture.get("input_schema") != "mosim.ue_command_echo.v1":
            report["issues"].append("UE 008 live echo fixture must preserve mosim.ue_command_echo.v1")
        if int(ue_live_fixture.get("valid_future_live_accepted_rows", 0) or 0) != 5:
            report["issues"].append("UE 008 live echo fixture must preserve 5 valid future live rows")
        for key in ["non_live_runtime_leaks", "malformed_runtime_leaks", "rejected_runtime_leaks"]:
            if int(ue_live_fixture.get(key, -1)) != 0:
                report["issues"].append(f"UE 008 live echo fixture must preserve {key}=0")
        if ue_live_fixture.get("runtime_receiver_implemented") is not False:
            report["issues"].append("UE 008 live echo fixture must not imply runtime receiver implementation")
        if ue_live_fixture.get("ui_asset_binding_implemented") is not False:
            report["issues"].append("UE 008 live echo fixture must not imply UI asset binding implementation")
        report["warnings"].append("UE live-echo acceptance 008 is source/static fixture evidence only; live ack remains blocked")

    for label, schema_path in [
        ("ue.command_schema", ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"),
        ("ue.command_echo_schema", ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"),
    ]:
        require_path(report, label, rel(schema_path))

    sunray_material = as_mapping(as_mapping(manifest.get("sunray150")).get("material_review"))
    if sunray_material:
        require_path(report, "sunray150.material_review.return_packet", sunray_material.get("return_packet"))
        require_path(report, "sunray150.material_review.evidence_dir", sunray_material.get("evidence_dir"))
        require_path(report, "sunray150.material_review.path_hygiene_evidence", sunray_material.get("path_hygiene_evidence"))
        readability = as_mapping(sunray_material.get("battery_guard_readability"))
        if sunray_material.get("quality_status") != "path_hygiene_ready_manual_visual_review_pending":
            report["issues"].append("Sunray 004 must remain path hygiene with manual visual review pending")
        if sunray_material.get("manual_review_required") is not True:
            report["issues"].append("Sunray 004 must preserve manual_review_required=true")
        if sunray_material.get("manual_review_status") != "pending_pmo_wechat_review":
            report["issues"].append("Sunray 004 must preserve pending manual review status")
        if sunray_material.get("source_manifest_all_outputs_have_project_relative_path") is not True:
            report["issues"].append("Sunray 004 must preserve project-relative output coverage")
        if sunray_material.get("source_manifest_legacy_absolute_path_field_count") != 20:
            report["issues"].append("Sunray 004 must preserve legacy absolute path quarantine count")
        for key in ["battery_present", "battery_non_flat", "guard_landing_gear_present", "guard_landing_gear_non_flat"]:
            if readability.get(key) is not True:
                report["issues"].append(f"Sunray 004 must preserve {key}=true")
        report["warnings"].append("Sunray150 material review 004 is path hygiene/readability only; manual visual acceptance remains pending")

    gate = as_mapping(manifest.get("gate_results"))
    if as_list(gate.get("failures")):
        report["issues"].append("gate_results.failures must be empty for an accepted smoke bundle")
    if not as_list(gate.get("warnings")) and report["quality_status"] != "pass":
        report["warnings"].append("non-pass bundle has no gate warnings")

    review_packet = ROOT / "Results/coagent_gateway/packets/rfly_mosim_p0_current_blockers_integrated_20260606.json"
    latest_review_packet = ROOT / "Results/coagent_gateway/packets/rfly_mosim_p0_dispatched_ros2_021_20260606.json"
    recovery_note = ROOT / "Results/coagent_gateway/recovery/weixin_recovery_required_20260606_050850.json"
    report["manual_review"] = {
        "packet": rel(review_packet),
        "packet_exists": review_packet.exists(),
        "latest_packet": rel(latest_review_packet),
        "latest_packet_exists": latest_review_packet.exists(),
        "weixin_recovery_note": rel(recovery_note),
        "weixin_recovery_note_exists": recovery_note.exists(),
        "status": "latest_checkpoint_sent" if latest_review_packet.exists() else "packet_only",
    }
    if not review_packet.exists() and not latest_review_packet.exists():
        report["warnings"].append("missing sparse WeChat/manual-review packet")
    if recovery_note.exists() and not latest_review_packet.exists():
        report["warnings"].append("WeChat notification is degraded; user must send one normal message before one bounded retry")

    report["ok"] = not report["issues"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json",
        help="RUN_MANIFEST.json path",
    )
    parser.add_argument(
        "--output-json",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json",
        help="Where to write the audit report",
    )
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    output_path = repo_path(args.output_json)
    try:
        report = audit_bundle(manifest_path)
    except Exception as exc:
        report = {
            "schema": "mosim.p0_run_bundle_audit.v1",
            "manifest": rel(manifest_path),
            "run_id": "",
            "quality_status": "",
            "claim_scope": [],
            "ok": False,
            "issues": [str(exc)],
            "warnings": [],
            "path_checks": [],
            "manual_review": {},
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["ok", "run_id", "quality_status", "issues", "warnings"]}, ensure_ascii=False, indent=2))
    print(f"audit: {output_path}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
