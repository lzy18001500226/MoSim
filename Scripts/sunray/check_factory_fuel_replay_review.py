#!/usr/bin/env python3
"""Check that one P4 Factory FUEL replay bundle reached all display consumers.

This checker is deliberately read-only. It binds the offline rosbag bundle,
isolated RViz replay, Factory 2D operator-map replay, and one-way UE replay to
the same run id. It does not start any simulator, ROS node, renderer, or QGC.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.runtime_sidecar_contract import atomic_write_json


DISPLAY_TRUTH_TOPIC = "/uav1/sunray/gazebo_pose"
STATUS_FILENAME = "P4_DISPLAY_REPLAY_STATUS.json"


def read_object(path: Path, issues: list[dict[str, str]]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append({"code": "p4_replay_status_unreadable", "path": str(path), "detail": str(exc)})
        return {}
    if not isinstance(data, dict):
        issues.append({"code": "p4_replay_status_not_object", "path": str(path), "detail": "JSON root must be object"})
        return {}
    return data


def expect(
    condition: bool,
    issues: list[dict[str, str]],
    code: str,
    path: Path,
    detail: str,
) -> None:
    if not condition:
        issues.append({"code": code, "path": str(path), "detail": detail})


def resolve_run_dir(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def evaluate(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    issues: list[dict[str, str]] = []
    bundle_path = run_dir / "P4_REPLAY_BUNDLE_STATUS.json"
    manifest_path = run_dir / "RUN_MANIFEST.json"
    coordinate_path = run_dir / "OPERATOR_MAP_COORDINATE_EVIDENCE.json"
    rviz_path = run_dir / "rviz_replay" / "RVIZ_REPLAY_STATUS.json"
    map_manifest_path = run_dir / "OPERATOR_MAP_REPLAY_MANIFEST.json"
    map_status_path = run_dir / "OPERATOR_MAP_REPLAY_STATUS.json"
    ue_validation_path = run_dir / "ue_render" / "UE_RENDER_STREAM_VALIDATION.json"
    ue_receiver_path = run_dir / "ue_render" / "ue_receiver_metrics.json"
    ue_frame_path = run_dir / "ue_render" / "ue_frame_metrics.json"

    bundle = read_object(bundle_path, issues)
    manifest = read_object(manifest_path, issues)
    coordinate = read_object(coordinate_path, issues)
    rviz = read_object(rviz_path, issues)
    map_manifest = read_object(map_manifest_path, issues)
    map_status = read_object(map_status_path, issues)
    ue_validation = read_object(ue_validation_path, issues)
    ue_receiver = read_object(ue_receiver_path, issues)
    ue_frame = read_object(ue_frame_path, issues)

    run_id = str(bundle.get("run_id", ""))
    expect(bool(run_id), issues, "p4_replay_run_id_missing", bundle_path, "P4 replay bundle has no run_id")
    expect(bundle.get("status") == "prepared", issues, "p4_replay_bundle_not_prepared", bundle_path, "bundle preparation status must be prepared")
    expect(
        bundle.get("display_pose_source") == DISPLAY_TRUTH_TOPIC,
        issues,
        "p4_replay_display_truth_topic_wrong",
        bundle_path,
        f"display pose must use {DISPLAY_TRUTH_TOPIC}",
    )
    expect(
        bundle.get("display_state_kind") == "gazebo_world_truth",
        issues,
        "p4_replay_display_state_kind_wrong",
        bundle_path,
        "display state must remain Gazebo world truth",
    )
    expect(manifest.get("run_id") == run_id, issues, "p4_replay_manifest_run_id_mismatch", manifest_path, "RUN_MANIFEST run_id differs")
    expect(coordinate.get("source_frame_id") == "world", issues, "p4_replay_coordinate_source_frame_wrong", coordinate_path, "source frame must be world")
    expect(coordinate.get("target_frame_id") == "mworks_world", issues, "p4_replay_coordinate_target_frame_wrong", coordinate_path, "target frame must be mworks_world")

    expect(rviz.get("state") == "completed", issues, "p4_replay_rviz_not_completed", rviz_path, "isolated RViz replay did not complete")
    for field in ("bag_exit_code", "pointcloud_probe_exit_code", "occupancy_probe_exit_code", "truth_path_probe_exit_code"):
        expect(rviz.get(field) == 0, issues, "p4_replay_rviz_exit_nonzero", rviz_path, f"{field} must be 0")

    expect(map_status.get("state") == "completed", issues, "p4_replay_operator_map_not_completed", map_status_path, "operator-map replay did not complete")
    expect(map_status.get("run_id") == run_id, issues, "p4_replay_operator_map_run_id_mismatch", map_status_path, "operator-map status run_id differs")
    expect(int(map_status.get("sequence", 0) or 0) > 0, issues, "p4_replay_operator_map_empty", map_status_path, "operator-map replay wrote no state frame")
    expect(
        map_manifest.get("source", {}).get("odom_topics", {}).get("uav1") == DISPLAY_TRUTH_TOPIC,
        issues,
        "p4_replay_operator_map_truth_topic_wrong",
        map_manifest_path,
        f"uav1 must consume {DISPLAY_TRUTH_TOPIC}",
    )

    expect(ue_validation.get("status") == "passed", issues, "p4_replay_ue_contract_invalid", ue_validation_path, "UE render stream validation did not pass")
    expect(ue_receiver.get("run_id") == run_id, issues, "p4_replay_ue_receiver_run_id_mismatch", ue_receiver_path, "UE receiver run_id differs")
    expect(float(ue_receiver.get("receive_rate_hz", 0.0) or 0.0) > 0.0, issues, "p4_replay_ue_receiver_empty", ue_receiver_path, "UE receiver rate must be positive")
    expect(int(ue_receiver.get("sequence_gap_count", -1) or 0) == 0, issues, "p4_replay_ue_sequence_gap", ue_receiver_path, "UE receiver observed sequence gaps")
    expect(float(ue_frame.get("ue_fps", 0.0) or 0.0) > 0.0, issues, "p4_replay_ue_frame_metrics_empty", ue_frame_path, "UE frame rate must be positive")

    visual_capture_limitation = (
        "WSLg RAIL windows may reject Win32 PrintWindow capture. RViz topic replay and window launch are "
        "verified here, but this record does not assert an RViz pixel-level visual acceptance."
    )
    return {
        "schema": "mosim.sunray_p4_factory_fuel_display_replay_status.v1",
        "status": "blocked" if issues else "completed_with_rviz_window_capture_limitation",
        "run_id": run_id or None,
        "display_data_status": "blocked" if issues else "passed",
        "components": {
            "bundle": {"path": str(bundle_path), "status": bundle.get("status")},
            "rviz": {"path": str(rviz_path), "status": rviz.get("state")},
            "operator_map": {"path": str(map_status_path), "status": map_status.get("state")},
            "ue": {"validation": ue_validation.get("status"), "receive_rate_hz": ue_receiver.get("receive_rate_hz"), "ue_fps": ue_frame.get("ue_fps")},
        },
        "rviz_visual_capture": {"status": "limited", "reason": visual_capture_limitation},
        "issues": issues,
        "claim_boundary": (
            "Historical FUEL rosbag display replay only. This result does not claim a live Gazebo/PX4/MAVROS "
            "flight, FUEL planner execution, controller performance, fault tolerance, or QGC command success."
        ),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="P4 replay bundle directory, relative to the repository or absolute.")
    args = parser.parse_args(argv)
    run_dir = resolve_run_dir(args.run_dir)
    report = evaluate(run_dir)
    atomic_write_json(run_dir / STATUS_FILENAME, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
