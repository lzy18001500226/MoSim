#!/usr/bin/env python3
"""Build and evaluate the Phase 1 RViz-to-QGC display test packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MANUAL_TEST_SCHEMA = "mosim.rviz_qgc_display_phase1_manual_test.v1"
ACCEPTANCE_SCHEMA = "mosim.rviz_qgc_display_phase1_acceptance.v1"
ADAPTER_SCHEMA = "mosim.sunray_ros1.goal4_clicked_goal_adapter.v1"


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


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_manual_test_packet(
    *,
    run_id: str,
    profile_id: str,
    runtime_profile_id: str,
    rviz_config: str,
    result_directory: str,
    operator_run_directory: str,
) -> dict[str, Any]:
    return {
        "schema": MANUAL_TEST_SCHEMA,
        "run_id": run_id,
        "phase": "phase_1_rviz_goal_to_qgc_display",
        "status": "awaiting_rviz_goal",
        "profile_id": profile_id,
        "runtime_profile_id": runtime_profile_id,
        "entrypoints": {
            "rviz_config": rviz_config,
            "rviz_tool": "2D Nav Goal",
            "rviz_goal_topic": "/move_base_simple/goal",
            "planner_goal_topic": "/goal_with_id",
            "qgc_data_path": f"{operator_run_directory}/telemetry.json",
        },
        "required_human_actions": [
            "Use RViz 2D Nav Goal once on an obstacle-free Factory L2 location.",
            "Observe the same run's future path and actual track in QGC.",
        ],
        "must_not_do": [
            "Do not select QGC Plan Goal in Phase 1.",
            "Do not treat this display test as QGC input, flight, or controller acceptance.",
        ],
        "evidence_paths": {
            "result_directory": result_directory,
            "mission_metrics": f"{result_directory}/runtime/EGO_SINGLE_METRICS.json",
            "rviz_goal_adapter": f"{result_directory}/runtime/clicked_goal_adapter.json",
            "operator_telemetry": f"{operator_run_directory}/telemetry.json",
        },
        "claim_boundary": (
            "The packet proves only readiness for a human RViz input and QGC visual observation. "
            "It cannot prove that QGC originated a goal, that a human observed the display, "
            "or that the controller or vehicle passed acceptance."
        ),
    }


def build_phase1_acceptance(
    *,
    run_id: str,
    metrics: dict[str, Any],
    adapter: dict[str, Any],
    telemetry: dict[str, Any],
    schema: str = ACCEPTANCE_SCHEMA,
) -> dict[str, Any]:
    blockers: list[str] = []

    if metrics.get("run_terminal_status") != "interactive_passed" or metrics.get("status") != "passed":
        blockers.append("interactive_mission_not_passed")
    if metrics.get("blockers"):
        blockers.append("interactive_mission_has_blockers")
    if _count(metrics.get("forwarded_goal_count")) < 1:
        blockers.append("planner_forwarded_goal_missing")
    counts = _object(metrics.get("counts"))
    if _count(counts.get("polytraj")) < 1:
        blockers.append("planner_future_polytraj_missing")
    if _count(counts.get("planner_position_cmd")) < 1:
        blockers.append("planner_position_command_missing")
    handoffs = metrics.get("interactive_goal_handoffs")
    if not isinstance(handoffs, list) or not handoffs:
        blockers.append("interactive_goal_handoff_missing")
    final_hover = _object(metrics.get("interactive_final_hover"))
    if final_hover.get("reached") is not True:
        blockers.append("interactive_final_hover_not_reached")

    if adapter.get("schema") != ADAPTER_SCHEMA:
        blockers.append("rviz_goal_adapter_schema_invalid")
    if adapter.get("nav_goal_topic") != "/move_base_simple/goal":
        blockers.append("rviz_goal_topic_mismatch")
    if adapter.get("output_goal_topic") != "/goal_with_id":
        blockers.append("planner_goal_topic_mismatch")
    if _count(adapter.get("nav_goal_count")) < 1:
        blockers.append("rviz_nav_goal_missing")
    if _count(adapter.get("published_goal_count")) < 1:
        blockers.append("rviz_goal_not_forwarded")
    last_goal = _object(adapter.get("last_goal"))
    if last_goal.get("source") != "nav_goal":
        blockers.append("rviz_goal_source_not_recorded")

    map_state = _object(telemetry.get("map_state"))
    if telemetry.get("run_id") != run_id or map_state.get("run_id") != run_id:
        blockers.append("operator_map_run_identity_mismatch")
    map_info = _object(map_state.get("map"))
    if map_info.get("coordinate_contract_status") != "verified":
        blockers.append("operator_map_coordinate_contract_unverified")
    map_data_status = _object(map_state.get("map_data_status"))
    if map_data_status.get("state") != "accepted":
        blockers.append("operator_map_frame_not_accepted")
    task_paths = _object(map_state.get("task_paths"))
    if not _available_path(task_paths.get("expected")):
        blockers.append("operator_expected_path_missing")
    if not _available_path(task_paths.get("future")):
        blockers.append("operator_future_path_missing")
    actual_tracks = _object(map_state.get("actual_tracks"))
    if not _available_path(actual_tracks.get("uav1")):
        blockers.append("operator_actual_track_missing")

    status = "automated_evidence_ready" if not blockers else "blocked"
    return {
        "schema": schema,
        "run_id": run_id,
        "status": status,
        "reason_code": (
            "rviz_qgc_display_phase1_automated_evidence_ready"
            if not blockers
            else "rviz_qgc_display_phase1_automated_evidence_unverified"
        ),
        "blockers": blockers,
        "manual_observation": {
            "required": True,
            "status": "pending" if not blockers else "not_ready",
            "surface": "QGC",
            "requirement": "A human must observe the same run's future path and actual track in QGC.",
        },
        "claim_boundary": (
            "Automated evidence records RViz-topic transport, planner output, and sidecar map data. "
            "It does not prove a human observed QGC, that QGC originated a goal, flight success, "
            "or controller acceptance."
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
    parser.add_argument("--rviz-config")
    parser.add_argument("--result-directory")
    parser.add_argument("--operator-run-directory")
    parser.add_argument("--metrics")
    parser.add_argument("--adapter")
    parser.add_argument("--telemetry")
    parser.add_argument("--schema", default=ACCEPTANCE_SCHEMA)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    try:
        if args.command == "manual-packet":
            required = (args.profile_id, args.runtime_profile_id, args.rviz_config, args.result_directory, args.operator_run_directory)
            if not all(required):
                raise ValueError("manual_packet_arguments_missing")
            payload = build_manual_test_packet(
                run_id=args.run_id,
                profile_id=str(args.profile_id),
                runtime_profile_id=str(args.runtime_profile_id),
                rviz_config=str(args.rviz_config),
                result_directory=str(args.result_directory),
                operator_run_directory=str(args.operator_run_directory),
            )
            atomic_write_json(output, payload)
            return 0

        if not args.metrics or not args.adapter or not args.telemetry:
            raise ValueError("acceptance_arguments_missing")
        payload = build_phase1_acceptance(
            run_id=args.run_id,
            metrics=_read_object(Path(args.metrics)),
            adapter=_read_object(Path(args.adapter)),
            telemetry=_read_object(Path(args.telemetry)),
            schema=args.schema,
        )
        payload["evidence"] = {
            "mission_metrics": args.metrics,
            "rviz_goal_adapter": args.adapter,
            "operator_telemetry": args.telemetry,
        }
        atomic_write_json(output, payload)
        return 0 if not payload["blockers"] else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
