from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_single_uav_evidence_bundle.py"
OUTPUT = ROOT / "Results" / "tmp" / "test_single_uav_evidence_bundle"
REPORT = OUTPUT / "SINGLE_UAV_EVIDENCE_BUNDLE.json"
CURRENT_SAME_RUN_DIR = "Results/gazebo_ros2/default_48s_same_run_current_recheck_20260618_072626"


def run_builder() -> dict:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(OUTPUT.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_single_uav_evidence_bundle_collects_core_gates() -> None:
    report = run_builder()

    assert report["schema"] == "mosim.single_uav_evidence_bundle.v1"
    assert report["status"] in {
        "single_uav_evidence_bundle_ready",
        "single_uav_evidence_bundle_ready_with_status_drift",
    }
    gates = {gate["gate_id"]: gate for gate in report["gates"]}
    for gate_id in [
        "mworks_single_uav_pre_multi_uav_closeout",
        "ue_truth_replay_contract",
        "offline_ue_truth_local_voxel_fixture",
        "gazebo_ros2_sensor_local_map",
        "gazebo_ros2_controller_output_node_handoff",
        "gazebo_ros2_fastlio_planner_input",
        "spark_fastlio_output_surface",
        "fastlio_vs_gazebo_truth_error",
        "command_acknowledgement_without_closed_loop",
        "gazebo_truth_feedback_hover_hold_pre_acceptance",
    ]:
        assert gate_id in gates

    sensor_gate = gates["gazebo_ros2_sensor_local_map"]
    assert sensor_gate["evidence_state"] in {
        "current_runtime_status_passed",
        "drift_detected_prior_pass_log_available",
    }
    if sensor_gate["evidence_state"] == "drift_detected_prior_pass_log_available":
        assert sensor_gate["prior_gate_passed"] is True
    figure8_gate = gates["gazebo_figure8_static_obstacle_pre_acceptance"]
    assert figure8_gate["primary_artifact"] == f"{CURRENT_SAME_RUN_DIR}/RUNTIME_STATUS.json"


def test_single_uav_evidence_bundle_outputs_review_visuals_and_boundaries() -> None:
    report = run_builder()

    visuals = report["visuals"]
    visual_kinds = {visual["kind"] for visual in visuals}
    assert "gazebo_runtime_lidar_pointcloud_3d" in visual_kinds
    assert "gazebo_runtime_local_occupancy_voxels_3d" in visual_kinds
    assert "gazebo_runtime_local_occupancy_grid_2d" in visual_kinds
    assert "figure8_truth_reference_topdown_animation_gif" in visual_kinds
    assert not any("ue_truth" in visual["kind"] for visual in visuals)
    for visual in visuals:
        assert visual["path"], visual
        output = ROOT / visual["path"]
        assert output.is_file(), visual
        assert output.stat().st_size > 1000, visual
    assert all(
        CURRENT_SAME_RUN_DIR in visual["source"]
        for visual in visuals
        if visual["kind"].startswith("gazebo_runtime_")
    )

    boundary = "\n".join(report["claim_boundary"])
    assert "does not start or rerun MWORKS, UE, ROS2, Gazebo" in boundary
    assert "does not prove planner_ready" in boundary
    assert "multi-UAV readiness" in boundary
    assert report["subagent_plan"]["decision"] in {"used", "unavailable", "available_but_not_useful", "unsafe"}
    assert report["mworks_summary"]["current_rerun_accepted"] is True
