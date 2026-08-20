#!/usr/bin/env python3
"""Build and evaluate the Phase 1 multi-UAV RViz-to-QGC display packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MANUAL_TEST_SCHEMA = "mosim.rviz_qgc_display_phase1_swarm_manual_test.v1"
ACCEPTANCE_SCHEMA = "mosim.rviz_qgc_display_phase1_swarm_acceptance.v1"
ROUTER_SCHEMA = "mosim.rviz_diff_swarm_goal_router.v2"


def _object(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _count(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _available_path(value: Any) -> bool:
    path = _object(value)
    return path.get("status") == "available" and isinstance(path.get("points"), list) and len(path["points"]) >= 2


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_manual_test_packet(
    *,
    run_id: str,
    profile_id: str,
    runtime_profile_id: str,
    pointcloud_rviz_config: str,
    grid_rviz_config: str,
    result_directory: str,
    operator_run_directory: str,
    uav_num: int = 3,
) -> dict[str, Any]:
    if uav_num not in (2, 3):
        raise ValueError("uav_num must be 2 or 3")
    return {
        "schema": MANUAL_TEST_SCHEMA,
        "run_id": run_id,
        "phase": "phase_1_rviz_formation_goal_to_qgc_display",
        "status": "awaiting_rviz_formation_center_goal",
        "profile_id": profile_id,
        "runtime_profile_id": runtime_profile_id,
        "vehicle_count": uav_num,
        "entrypoints": {
            "rviz_pointcloud_config": pointcloud_rviz_config,
            "rviz_grid3d_config": grid_rviz_config,
            "rviz_tool": "2D Nav Goal",
            "rviz_goal_topic": "/move_base_simple/goal",
            "rviz_goal_frame": "world",
            "planner_goal_topic_template": "/uav{uid}/goal_with_id",
            "router": "Scripts/sunray/diff_swarm_rviz_goal_router.py",
            "qgc_data_path": f"{operator_run_directory}/telemetry.json",
            "qgc_actual_track_odom_topic_template": "/uav{uid}/mosim/diff_swarm/planner_odom_world",
            "qgc_future_polytraj_topic_template": "/drone_{drone_id}_planning/trajectory",
        },
        "required_human_actions": [
            "Use RViz 2D Nav Goal for one or more obstacle-free Factory L2 waypoints.",
            "Confirm one same-stamp fixed-offset goal batch is recorded for every UAV.",
            "Observe the same run's multi-UAV future path and actual tracks in QGC.",
        ],
        "must_not_do": [
            "Do not select QGC Plan Goal in Phase 1.",
            "Do not treat fixed-offset expansion as global collision-aware swarm planning.",
            "Do not treat this display test as flight or controller acceptance.",
        ],
        "sensor_contract": {
            "planner_cloud_topic_template": "/uav{uid}/livox_world",
            "planner_cloud_source": "time-synchronized radar PointCloud2 transformed to the common world frame",
            "fastlio_xy_topic_template": "/uav{uid}/mosim/diff_swarm/fastlio/aligned_cloud",
            "fastlio_odom_topic_template": "/uav{uid}/mosim/diff_swarm/fastlio/aligned_odom",
            "fastlio_xy_role": "planner_input_when_enabled_after_alignment_gate",
            "claim_boundary": "FAST-LIO alignment and planner-input transport are recorded here; localization quality, controller success, and flight remain separate gates.",
        },
        "evidence_paths": {
            "result_directory": result_directory,
            "mission_metrics": f"{result_directory}/EGO_SWARM_METRICS.json",
            "rviz_goal_router": f"{result_directory}/DIFF_SWARM_RVIZ_GOAL_ROUTER.json",
            "operator_telemetry": f"{operator_run_directory}/telemetry.json",
        },
        "claim_boundary": (
            "The packet proves only readiness for one human RViz formation-center input, fixed-offset per-UAV routing, "
            "and same-run QGC map observation surfaces. It cannot prove QGC-originated planning, global collision-aware "
            "swarm planning, flight, controller acceptance, or FAST-LIO localization quality."
        ),
    }


def build_phase1_swarm_acceptance(
    *,
    run_id: str,
    metrics: dict[str, Any],
    router: dict[str, Any],
    telemetry: dict[str, Any],
    vehicle_count: int = 3,
    schema: str = ACCEPTANCE_SCHEMA,
) -> dict[str, Any]:
    blockers: list[str] = []
    if metrics.get("status") != "passed":
        blockers.append("interactive_swarm_mission_not_passed")
    if metrics.get("blockers"):
        blockers.append("interactive_swarm_mission_has_blockers")
    if _count(metrics.get("uav_num")) != vehicle_count:
        blockers.append("swarm_vehicle_count_mismatch")

    interactive = _object(metrics.get("interactive_goal_review"))
    batch = _object(interactive.get("goal_batch"))
    targets = _object(batch.get("targets"))
    expected_uavs = {f"uav{uid}" for uid in range(1, vehicle_count + 1)}
    if interactive.get("enabled") is not True:
        blockers.append("interactive_swarm_goal_review_not_enabled")
    if set(targets) != expected_uavs:
        blockers.append("same_stamp_per_uav_goal_batch_missing")

    if router.get("schema") != ROUTER_SCHEMA:
        blockers.append("rviz_swarm_router_schema_invalid")
    if router.get("goal_input_topic") != "/move_base_simple/goal":
        blockers.append("rviz_swarm_goal_topic_mismatch")
    if _count(router.get("goal_count")) < 1:
        blockers.append("rviz_swarm_center_goal_missing")
    if _count(router.get("forwarded_batch_count")) < 1:
        blockers.append("rviz_swarm_goal_batch_not_forwarded")
    if _count(router.get("uav_num")) != vehicle_count:
        blockers.append("rviz_swarm_router_vehicle_count_mismatch")
    if _object(router.get("last_batch")).get("planner_targets") is None:
        blockers.append("rviz_swarm_per_uav_targets_missing")

    if telemetry.get("run_id") != run_id or _count(telemetry.get("vehicle_count")) != vehicle_count:
        blockers.append("operator_swarm_telemetry_identity_mismatch")
    map_state = _object(telemetry.get("map_state"))
    if map_state.get("run_id") != run_id:
        blockers.append("operator_swarm_map_run_identity_mismatch")
    if _object(map_state.get("map")).get("coordinate_contract_status") != "verified":
        blockers.append("operator_swarm_map_coordinate_contract_unverified")
    if _object(map_state.get("map_data_status")).get("state") != "accepted":
        blockers.append("operator_swarm_map_frame_not_accepted")
    if not _available_path(_object(map_state.get("task_paths")).get("future")):
        blockers.append("operator_swarm_future_path_missing")
    future_paths = _object(map_state.get("task_paths")).get("future_paths")
    if not isinstance(future_paths, dict):
        blockers.append("operator_swarm_future_paths_missing")
    else:
        for vehicle_id in sorted(expected_uavs):
            if not _available_path(future_paths.get(vehicle_id)):
                blockers.append(f"operator_swarm_future_path_missing:{vehicle_id}")
    actual_tracks = _object(map_state.get("actual_tracks"))
    for vehicle_id in sorted(expected_uavs):
        if not _available_path(actual_tracks.get(vehicle_id)):
            blockers.append(f"operator_swarm_actual_track_missing:{vehicle_id}")

    status = "automated_evidence_ready" if not blockers else "blocked"
    return {
        "schema": schema,
        "run_id": run_id,
        "vehicle_count": vehicle_count,
        "status": status,
        "reason_code": (
            "rviz_qgc_display_phase1_swarm_automated_evidence_ready"
            if not blockers
            else "rviz_qgc_display_phase1_swarm_automated_evidence_unverified"
        ),
        "blockers": blockers,
        "manual_observation": {
            "required": True,
            "status": "pending" if not blockers else "not_ready",
            "surface": "QGC",
            "requirement": "A human must observe the same run's multi-UAV future path and actual tracks in QGC.",
        },
        "claim_boundary": (
            "Automated evidence records RViz center-goal transport, fixed-offset per-UAV expansion, planner output, "
            "and same-run QGC map data. It does not prove human QGC observation, global collision-aware planning, "
            "flight, controller acceptance, or FAST-LIO localization quality."
        ),
    }


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{path}")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("manual-packet", "evaluate"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--profile-id")
    parser.add_argument("--runtime-profile-id")
    parser.add_argument("--pointcloud-rviz-config")
    parser.add_argument("--grid-rviz-config")
    parser.add_argument("--result-directory")
    parser.add_argument("--operator-run-directory")
    parser.add_argument("--uav-num", type=int, default=3)
    parser.add_argument("--metrics")
    parser.add_argument("--router")
    parser.add_argument("--telemetry")
    parser.add_argument("--schema", default=ACCEPTANCE_SCHEMA)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    try:
        if args.command == "manual-packet":
            required = (
                args.profile_id,
                args.runtime_profile_id,
                args.pointcloud_rviz_config,
                args.grid_rviz_config,
                args.result_directory,
                args.operator_run_directory,
            )
            if not all(required):
                raise ValueError("manual_packet_arguments_missing")
            payload = build_manual_test_packet(
                run_id=args.run_id,
                profile_id=str(args.profile_id),
                runtime_profile_id=str(args.runtime_profile_id),
                pointcloud_rviz_config=str(args.pointcloud_rviz_config),
                grid_rviz_config=str(args.grid_rviz_config),
                result_directory=str(args.result_directory),
                operator_run_directory=str(args.operator_run_directory),
                uav_num=args.uav_num,
            )
        else:
            if not args.metrics or not args.router or not args.telemetry:
                raise ValueError("acceptance_arguments_missing")
            payload = build_phase1_swarm_acceptance(
                run_id=args.run_id,
                metrics=_read_object(Path(args.metrics)),
                router=_read_object(Path(args.router)),
                telemetry=_read_object(Path(args.telemetry)),
                vehicle_count=args.uav_num,
                schema=args.schema,
            )
            payload["evidence"] = {
                "mission_metrics": args.metrics,
                "rviz_goal_router": args.router,
                "operator_telemetry": args.telemetry,
            }
        _atomic_write_json(output, payload)
        return 0 if args.command == "manual-packet" or not payload["blockers"] else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
