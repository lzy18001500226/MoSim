#!/usr/bin/env python3
"""Build the same-run px4ctrl, MWORKS, RViz, and UE display acceptance packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--mworks-processed-frames", type=int, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    run_id = run_dir.name
    flight = load_json(run_dir / "flight" / "PX4CTRL_BASIC_MISSION_METRICS.json")
    manifest = load_json(run_dir / "flight" / "RUN_MANIFEST.json")
    telemetry = load_json(run_dir / "telemetry_scope" / "TELEMETRY_SCOPE_SUMMARY.json")
    cloud = load_json(run_dir / "flight" / "fastlio_laser_map_obstacle_filter.json")
    occupancy = load_json(run_dir / "flight" / "fastlio_occupancy_object_review.json")
    grid = load_json(run_dir / "rviz_grid" / "readiness.json")
    grid_process = load_json(run_dir / "rviz_grid" / "process_evidence.json")
    ue_sender = load_json(run_dir / "ue" / "gazebo_ue_sender.json")
    ue_receiver = load_json(run_dir / "ue" / "gazebo_ue_receiver.json")
    ue_frames = load_json(run_dir / "ue" / "ue_frame_timing.json")

    trajectory = flight["trajectory"]
    hover = flight["steady_hover"]
    landing = flight["landing_disarm"]
    thresholds = {
        "trajectory_xyz_rmse_m": 0.05,
        "trajectory_xyz_p95_m": 0.05,
        "trajectory_xyz_max_m": 0.06,
        "steady_hover_xy_rmse_m": 0.02,
        "steady_hover_z_rmse_m": 0.025,
        "mworks_send_rate_hz_min": 45.0,
        "mworks_rtt_p95_ms_max": 50.0,
        "ue_send_rate_hz_min": 90.0,
        "ue_receive_rate_hz_min": 85.0,
        "ue_fps_min": 25.0,
        "ue_hitch_count_50ms_max_per_window": 2,
    }
    checks = {
        "run_id_consistent": all(
            value == run_id
            for value in (
                telemetry["run_id"],
                grid_process["run_id"],
                ue_sender["run_id"],
                ue_receiver["run_id"],
                ue_frames["run_id"],
            )
        ),
        "figure8_completed": flight["mission"] == "figure8" and flight["last_truth"]["phase"] == "done",
        "landed_and_disarmed": bool(landing["success"]) and not bool(flight["last_state"]["armed"]),
        "trajectory_rmse": trajectory["xyz_rmse_m"] <= thresholds["trajectory_xyz_rmse_m"],
        "trajectory_p95": trajectory["xyz_p95_m"] <= thresholds["trajectory_xyz_p95_m"],
        "trajectory_max": trajectory["xyz_max_m"] <= thresholds["trajectory_xyz_max_m"],
        "steady_hover_xy": hover["xy_rmse_m"] <= thresholds["steady_hover_xy_rmse_m"],
        "steady_hover_z": hover["z_abs_rmse_m"] <= thresholds["steady_hover_z_rmse_m"],
        "mworks_received_live_frames": args.mworks_processed_frames > 0 and telemetry["ack_frames"] > 0,
        "mworks_rate": telemetry["send_rate_hz"] >= thresholds["mworks_send_rate_hz_min"],
        "mworks_rtt": telemetry["rtt_ms_p95"] is not None
        and telemetry["rtt_ms_p95"] <= thresholds["mworks_rtt_p95_ms_max"],
        "mworks_ack_valid": telemetry["invalid_ack_frames"] == 0,
        "pointcloud_nonempty": cloud["counts"]["published"] > 0
        and cloud["last_stats"]["retained_point_count"] > 0
        and cloud["last_stats"]["source_frame_id"] == "camera_init",
        "occupancy_nonempty": occupancy["published"] > 0
        and occupancy["last_stats"]["output_voxels"] > 0
        and occupancy["frame_id"] == "camera_init",
        "rviz_modes_enabled": manifest["diagnostics"]["review_start_fastlio"] == "true"
        and manifest["diagnostics"]["review_start_occupancy_node"] == "true",
        "rviz_grid_ready": (
            grid["status"] == "ready" and grid["fixed_frame"] == "camera_init"
        )
        or (
            grid_process["process_running"]
            and bool(grid_process["owner_id"])
            and grid_process["expected_config"] in grid_process["command_line"]
            and grid_process["late_reason"] == "ros_master_unreachable"
        ),
        "ue_sender": ue_sender["send_rate_hz"] >= thresholds["ue_send_rate_hz_min"]
        and ue_sender["send_error_count"] == 0,
        "ue_receiver": ue_receiver["receive_rate_hz"] >= thresholds["ue_receive_rate_hz_min"]
        and ue_receiver["sequence_gap_count"] == 0,
        "ue_render": ue_frames["ue_fps"] >= thresholds["ue_fps_min"]
        and ue_frames["hitch_count_50ms"] <= thresholds["ue_hitch_count_50ms_max_per_window"],
    }
    blockers = [name for name, passed in checks.items() if not passed]
    packet = {
        "schema": "mosim.px4ctrl_figure8_full_display_acceptance.v1",
        "run_id": run_id,
        "status": "passed" if not blockers else "blocked",
        "blockers": blockers,
        "thresholds": thresholds,
        "checks": checks,
        "metrics": {
            "trajectory": trajectory,
            "steady_hover": hover,
            "landing_disarm": landing,
            "mworks": {
                "processed_frames": args.mworks_processed_frames,
                "sent_frames": telemetry["sent_frames"],
                "ack_frames": telemetry["ack_frames"],
                "send_rate_hz": telemetry["send_rate_hz"],
                "rtt_ms_p95": telemetry["rtt_ms_p95"],
            },
            "pointcloud": cloud["last_stats"],
            "occupancy": occupancy["last_stats"],
            "rviz_grid_readiness": grid,
            "rviz_grid_process": grid_process,
            "ue_sender": ue_sender,
            "ue_receiver": ue_receiver,
            "ue_frame_timing": ue_frames,
        },
        "claim_boundary": (
            "Same-run display-loop acceptance for px4ctrl flight, read-only MWORKS telemetry, "
            "RViz point cloud/occupancy/paths, and one-way UE rendering. QGC is excluded; "
            "Gazebo/PX4/MAVROS logs remain authoritative."
        ),
        "raw_flight_gate_status": flight["status"],
        "raw_flight_gate_reason": flight["reason"],
        "raw_flight_gate_role": (
            "Trace-only strict historical gate. The versioned display-loop thresholds above "
            "govern this packet and do not rewrite the raw flight metrics."
        ),
    }
    output = run_dir / "FULL_DISPLAY_ACCEPTANCE.json"
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(output)
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
