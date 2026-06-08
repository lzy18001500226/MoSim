#!/usr/bin/env python3
"""Static checks for the 071 LiDAR/IMU/odom 20 Hz sync contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "Results" / "ros2_runtime" / "b1_lidar_imu_odom_20hz_sync_contract_static_gate_20260608_071"
CONTRACT = EVIDENCE / "lidar_imu_odom_20hz_sync_contract.json"
CHECK_SUMMARY = EVIDENCE / "static_sync_contract_check_summary.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_071_contract_lidar_imu_rates_and_boundary() -> None:
    contract = load_json(CONTRACT)
    lidar = contract["sync_contract"]["lidar_20hz_source"]
    imu = contract["sync_contract"]["imu_source"]

    assert contract["mode"] == "source_static_contract_only"
    assert all(value is False for value in contract["live_actions"].values())
    assert lidar["classification"] == "adapt_replay_time_only_not_true_sensor_capture"
    assert lidar["topic"] == "/mosim/livox/lidar"
    assert lidar["frame_id"] == "base/mid360_link"
    assert lidar["frame_count"] == 120
    assert abs(float(lidar["observed_rate_hz_from_stamps"]) - 20.0) < 0.5
    assert lidar["monotonic"] is True
    assert lidar["regression_count"] == 0
    assert lidar["point_content_modification"] == "none"

    assert imu["topic"] == "/mosim/forward/imu"
    assert imu["frame_id"] == "base/forward_imu_optical_frame"
    assert abs(float(imu["observed_rate_hz_from_stamps"]) - 200.0) < 2.0
    assert imu["imu_samples_per_20hz_contract_period"] == 10
    assert imu["monotonic"] is True
    assert imu["regression_count"] == 0

    boundary = "\n".join(contract["claim_boundary"])
    assert "does not prove true 20 Hz sensor capture" in boundary
    assert "does not claim TF/RViz readiness" in boundary


def test_071_fastlio_output_and_controller_handoff_are_static_only() -> None:
    contract = load_json(CONTRACT)
    output = contract["sync_contract"]["fastlio_output_odom"]
    handoff = contract["sync_contract"]["controller_20hz_handoff"]

    assert output["classification"] == "reference_only_until_next_bounded_runtime_gate"
    assert output["fixed_frame_for_output_only_review"] == "camera_init"
    assert output["topics"]["/Odometry"]["frame_id"] == "camera_init"
    assert output["topics"]["/cloud_registered"]["frame_id"] == "camera_init"
    assert output["dynamic_tf_edges_observed"] == ["camera_init->body"]
    assert output["required_no_quality_claim"] is True

    assert handoff["classification"] == "static_contract_only_not_run"
    assert handoff["source_static_adapter"]["adapter_rate_hz"] == 20.0
    assert handoff["source_static_adapter"]["stale_timeout_s"] == 0.15
    assert handoff["source_static_adapter"]["expected_frame"] == "map"
    assert "/position_cmd" in handoff["forbidden_in_071"]
    assert "/planning/bspline" in handoff["forbidden_in_071"]
    assert "camera_init" in handoff["frame_gap"]
    assert "map" in handoff["frame_gap"]


def test_071_candidate_classification_and_static_source_checks() -> None:
    contract = load_json(CONTRACT)
    summary = load_json(CHECK_SUMMARY)

    classes = {item["candidate_id"]: item["classification"] for item in contract["candidate_classification"]}
    assert classes["accepted_lidar_jsonl_replay_time_20hz"] == "adapt"
    assert classes["bounded_imu_200hz_source"] == "adopt"
    assert classes["fastlio_camera_init_outputs"] == "reference_only"
    assert classes["planner_setpoint_adapter_20hz"] == "reference_only"
    assert classes["duplicate_or_interpolated_pointclouds"] == "reject"
    assert classes["fake_odom_tf_keyboard_pose_ue_truth_shortcut"] == "reject"

    assert summary["ok"] is True
    assert all(summary["gates"].values())
    for checks in contract["source_static_checks"].values():
        assert all(checks.values())


def main() -> int:
    test_071_contract_lidar_imu_rates_and_boundary()
    test_071_fastlio_output_and_controller_handoff_are_static_only()
    test_071_candidate_classification_and_static_source_checks()
    print("[OK] 071 LiDAR/IMU/odom 20Hz sync contract static gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
