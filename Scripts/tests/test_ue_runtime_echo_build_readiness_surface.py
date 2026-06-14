from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "UE5" / "check_ue_runtime_echo_build_readiness_surface.py"

EXPECTED_SYMBOLS = {
    "BuildPendingRequestCaptureJson",
    "BuildRuntimeProbeManifestJson",
    "BuildAuthoritativeEchoCaptureJson",
    "BuildRequestEchoMatchReportJson",
    "BuildNoPoseOverwriteReportJson",
    "BuildFalseAckNegativeReportJson",
    "BuildTimeoutCleanupManifestJson",
}

EXPECTED_DEPENDENCIES = {
    "Core",
    "CoreUObject",
    "Engine",
    "Json",
    "JsonUtilities",
    "Networking",
    "Sockets",
}


def run_checker(tmp_path: Path) -> dict:
    output_json = tmp_path / "runtime_echo_build_readiness_surface.json"
    output_md = tmp_path / "runtime_echo_build_readiness_surface.md"
    output_matrix = tmp_path / "runtime_echo_build_readiness_surface_matrix.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--output-matrix",
            str(output_matrix),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert output_json.exists()
    assert output_md.exists()
    assert output_matrix.exists()
    return json.loads(output_json.read_text(encoding="utf-8"))


def test_build_readiness_is_source_static_only(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    assert report["ok"] is True
    assert report["scope_classification"] == "source-static build-readiness checker"
    assert report["next_gate_classification"] == "build_only_gate_ready"
    assert report["build_only_gate_ready"] is True
    assert report["source_static_fix_needed"] is False
    assert report["blocked"] is False
    assert report["unreal_build_executed"] is False
    assert report["unreal_editor_opened"] is False
    assert report["ue_runtime_started"] is False
    assert report["socket_listener_timer_thread_or_background_loop_started"] is False
    assert report["live_command_echo_probe_executed"] is False
    assert report["live_attempt_consumed"] is False
    assert report["runtime_route_ready_now"] is False
    assert report["authoritative_runtime_ack_claimable_now"] is False
    assert report["runtime_ack_leaks_now"] == 0


def test_required_static_symbols_are_ready_for_build_gate(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["build_symbol_rows"]
    assert {row["symbol"] for row in rows} == EXPECTED_SYMBOLS
    assert all(row["declared_in_header"] is True for row in rows)
    assert all(row["defined_in_source"] is True for row in rows)
    assert all(row["artifact_literal_present"] is True for row in rows)
    assert all(row["schema_literal_present"] is True for row in rows)
    assert all(row["accepted_as_runtime_ack_literal_present"] is True for row in rows)
    assert all(row["runtime_ready_now"] is False for row in rows)
    assert all(row["accepted_as_runtime_ack_now"] is False for row in rows)


def test_module_dependencies_cover_static_json_and_transport_symbols(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = report["module_dependency_rows"]
    assert {row["dependency"] for row in rows} == EXPECTED_DEPENDENCIES
    assert all(row["declared_in_build_cs"] is True for row in rows)


def test_schema_anchors_keep_ack_authority_and_pose_boundary(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    rows = {row["name"]: row for row in report["schema_anchor_rows"]}
    assert rows["command_schema"]["schema_matches"] is True
    assert rows["command_schema"]["runtime_ack_is_required_for_acceptance"] is True
    assert rows["echo_schema"]["schema_matches"] is True
    assert rows["echo_schema"]["ack_authorities_present"] is True
    assert rows["echo_schema"]["forbidden_pose_kinds_present"] is True


def test_034_and_036_boundaries_are_preserved(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    prior = report["prior_evidence_consumed"]
    assert prior["ue_034_status"] == "blocked"
    assert prior["ue_034_live_attempt_consumed"] is False
    assert prior["ue_034_runtime_probe_executed"] is False
    assert prior["ue_036_status"] == "completed"
    assert prior["ue_036_source_static_ready"] is True
    assert prior["ue_036_runtime_route_ready_now"] is False
    assert prior["ue_036_runtime_ack_leaks_now"] == 0


def test_static_rows_are_not_runtime_ack(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = report["no_live_ack_boundary"]
    for source in [
        "034_no_side_effect_preflight_blocker",
        "build_success",
        "checker_success",
        "sender_result_bSent",
        "udp_send_success",
        "fixture_only_echo",
        "operator_intent",
        "quadrotor.unreal_state.frame",
        "quadrotor.unreal_state.v1",
    ]:
        assert source in boundary["static_sources_rejected_as_runtime_ack"]
    assert boundary["build_success_is_not_runtime_ack"] is True
    assert boundary["checker_success_is_not_runtime_ack"] is True
    assert boundary["sender_success_is_not_runtime_ack"] is True
    assert boundary["fixture_echo_is_not_runtime_ack"] is True
    assert boundary["operator_intent_is_not_runtime_ack"] is True
    assert boundary["accepted_as_runtime_ack_from_static_rows"] is False


def test_next_gate_requires_separate_authorization(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    requires = "\n".join(report["next_gate_requires"])
    for phrase in [
        "separate build-only task packet",
        "classified as build evidence only",
        "PMO authorization",
        "authoritative producer identity",
        "pending request capture",
        "authoritative echo capture",
        "timeout cleanup evidence",
    ]:
        assert phrase in requires


def test_claim_boundary_forbids_overclaiming(tmp_path: Path) -> None:
    report = run_checker(tmp_path)
    boundary = "\n".join(report["claim_boundary"])
    for phrase in [
        "source/static UE build-readiness",
        "does not run Unreal build",
        "does not edit UE source",
        "not build success",
        "not live runtime ack",
        "live_attempt_consumed=false",
        "does not prove live UE runtime ack",
        "MWORKS downlink",
        "ROS2 runtime echo",
        "final UI acceptance",
        "planner_ready",
        "controller performance",
        "mission success",
        "closed_loop",
    ]:
        assert phrase in boundary
