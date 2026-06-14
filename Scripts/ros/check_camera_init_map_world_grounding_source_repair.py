#!/usr/bin/env python3
"""File-only checker for the 080 camera_init map/world grounding repair surface.

This checker does not import ROS libraries, source ROS setup, run ros2, start
RViz2/FAST-LIO/planner/controller, publish TF, or consume a live probe. It
materializes the source/static repair gate for the next authorized probe:
the probe must use a non-fake source/config map-frame anchor and must still
prove the camera_init-to-map/world/ue_world chain from same-run raw evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REQUEST_ID = "PMO-ROS2-R3-CAMERA-INIT-MAP-WORLD-GROUNDING-SOURCE-REPAIR-20260609-080"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ROUTE_077 = (
    PROJECT_ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_grounding_source_route_design_20260609_077"
    / "camera_init_map_world_source_route_matrix.json"
)
FIELD_LIST_078 = (
    PROJECT_ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_same_run_tf_chain_capture_contract_20260609_078"
    / "future_evidence_bundle_field_list_078.json"
)
TF_GROUNDING_079 = (
    PROJECT_ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_same_run_tf_chain_evidence_probe_20260609_079"
    / "tf_chain_grounding_evidence_079.json"
)
FASTLIO_AUDIT_079 = (
    PROJECT_ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_camera_init_map_world_same_run_tf_chain_evidence_probe_20260609_079"
    / "fastlio_invocation_audit.json"
)
SPARK_LAUNCH = (
    PROJECT_ROOT
    / "Scripts"
    / "ros"
    / "mosim_scene_replay"
    / "launch"
    / "spark_fast_lio_mosim.launch.py"
)
SCENE_REPLAY_LAUNCH = (
    PROJECT_ROOT
    / "Scripts"
    / "ros"
    / "mosim_scene_replay"
    / "launch"
    / "mosim_scene_replay.launch.py"
)
SETPOINT_ADAPTER = (
    PROJECT_ROOT
    / "Scripts"
    / "ros"
    / "mosim_setpoint_adapter"
    / "src"
    / "planner_setpoint_adapter_node.cpp"
)
POSITION_CONVERTER = (
    PROJECT_ROOT
    / "Scripts"
    / "ros"
    / "mosim_setpoint_adapter"
    / "src"
    / "position_command_to_planner_setpoint_node.cpp"
)
DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT
    / "Results"
    / "ros2_runtime"
    / "camera_init_map_world_grounding_source_repair_20260609_080"
)

FORBIDDEN_SHORTCUTS = [
    "arbitrary camera_init->map/world/ue_world static TF",
    "header.frame_id rename from camera_init to map/world/ue_world",
    "fake odometry, map, point cloud, or TF",
    "keyboard pose",
    "UE truth shortcut",
    "RViz display state or world alias treated as transform evidence",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_file(errors: list[str], path: Path) -> None:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(PROJECT_ROOT)}")


def text_has(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8", errors="replace")


def build_repair_matrix() -> list[dict[str, Any]]:
    return [
        {
            "route_id": "future_single_probe_raw_tf_chain_with_source_config_anchor",
            "classification": "adopt",
            "current_status": "not_run_in_080_future_gate_only",
            "provenance": [
                str(ROUTE_077.relative_to(PROJECT_ROOT)),
                str(FIELD_LIST_078.relative_to(PROJECT_ROOT)),
                str(TF_GROUNDING_079.relative_to(PROJECT_ROOT)),
            ],
            "route_design": [
                "Select an adapt/adopt source/config anchor before the live probe.",
                "Capture raw /tf and /tf_static events in the same run.",
                "Accept only a derived camera_init-to-map/world/ue_world chain with evidence_path and non_fake_basis=true.",
            ],
            "current_boundary": "080 adopts this as the only future proof route, but does not run or authorize the live proof.",
        },
        {
            "route_id": "079_upstream_fast_lio_mapping_launch",
            "classification": "reference_only",
            "current_status": "observed_in_079_but_not_grounded",
            "provenance": [str(FASTLIO_AUDIT_079.relative_to(PROJECT_ROOT))],
            "facts": {
                "launch": load_json(FASTLIO_AUDIT_079).get("launch"),
                "config": load_json(FASTLIO_AUDIT_079).get("config"),
                "079_dynamic_edges": load_json(TF_GROUNDING_079).get("dynamic_edges"),
                "079_static_edges": load_json(TF_GROUNDING_079).get("static_edges"),
                "079_grounding_status": load_json(TF_GROUNDING_079)
                .get("camera_init_map_world_grounding", {})
                .get("status"),
            },
            "repair_decision": "Do not repeat this exact route as grounding proof unless a new source/config anchor is added and same-run raw TF/static TF proves the chain.",
        },
        {
            "route_id": "project_spark_fast_lio_map_frame_binding",
            "classification": "adapt",
            "current_status": "source_static_repair_surface_available_not_runtime_proven",
            "provenance": [str(SPARK_LAUNCH.relative_to(PROJECT_ROOT))],
            "source_static_facts": {
                "declares_map_frame_default_ue_world": text_has(SPARK_LAUNCH, 'DeclareLaunchArgument("map_frame", default_value="ue_world")'),
                "passes_common_map_frame": text_has(SPARK_LAUNCH, '"common.map_frame": LaunchConfiguration("map_frame")'),
                "passes_common_base_frame": text_has(SPARK_LAUNCH, '"common.base_frame": PythonExpression'),
                "publishes_only_base_to_lidar_imu_static_extrinsics": text_has(SPARK_LAUNCH, "static_transform_publisher")
                and text_has(SPARK_LAUNCH, 'LaunchConfiguration("base_frame")')
                and text_has(SPARK_LAUNCH, 'LaunchConfiguration("lidar_frame")')
                and text_has(SPARK_LAUNCH, 'LaunchConfiguration("imu_frame")'),
            },
            "future_single_probe_requirement": [
                "Invoke a FAST-LIO route that records the selected map_frame/base_frame/lidar_frame/imu_frame source/config anchor.",
                "Capture raw /tf and /tf_static events in the same run.",
                "Accept grounding only if the derived chain connects camera_init to map, world, or ue_world.",
                "If the map_frame parameter remains internal and no TF/output chain appears, keep blocked_absent.",
            ],
        },
        {
            "route_id": "scene_replay_external_fastlio_launch_cmd_binding",
            "classification": "adapt",
            "current_status": "source_static_hook_available_requires_explicit_invocation_audit",
            "provenance": [str(SCENE_REPLAY_LAUNCH.relative_to(PROJECT_ROOT))],
            "source_static_facts": {
                "has_fastlio_launch_cmd_argument": text_has(SCENE_REPLAY_LAUNCH, 'DeclareLaunchArgument("fastlio_launch_cmd", default_value="")'),
                "starts_fastlio_only_when_enabled": text_has(SCENE_REPLAY_LAUNCH, '"start_fastlio"') and text_has(SCENE_REPLAY_LAUNCH, '"fastlio_launch_cmd"'),
                "passes_source_lidar_frame": text_has(SCENE_REPLAY_LAUNCH, '"--lidar-frame"'),
                "passes_source_imu_frame": text_has(SCENE_REPLAY_LAUNCH, '"--imu-frame"'),
            },
            "future_single_probe_requirement": [
                "Record the full FASTLIO_ROS2_LAUNCH_CMD or equivalent invocation audit.",
                "The audit must name the source/config map-frame anchor; a bare upstream mapping.launch.py audit is insufficient.",
            ],
        },
        {
            "route_id": "controller_map_world_policy",
            "classification": "reference_only",
            "current_status": "confirmed_not_grounding",
            "provenance": [
                str(SETPOINT_ADAPTER.relative_to(PROJECT_ROOT)),
                str(POSITION_CONVERTER.relative_to(PROJECT_ROOT)),
            ],
            "source_static_facts": {
                "adapter_expected_frame_map": text_has(SETPOINT_ADAPTER, 'declare_parameter<std::string>("expected_frame", "map")'),
                "converter_accepts_world_alias": text_has(POSITION_CONVERTER, 'declare_parameter<std::string>("source_frame_alias", "world")'),
                "converter_normalizes_to_map": text_has(POSITION_CONVERTER, "setpoint.header.frame_id = expected_frame_"),
            },
            "repair_decision": "Keep as controller-side policy only; it cannot ground camera_init before a real TF/evidence chain exists.",
        },
        {
            "route_id": "arbitrary_static_tf_header_rename_or_truth_shortcut",
            "classification": "reject",
            "current_status": "forbidden",
            "rejected_shortcuts": FORBIDDEN_SHORTCUTS,
            "reason": "These shortcuts fabricate or relabel the missing transform instead of proving source/config and same-run raw evidence.",
        },
    ]


def build_future_gate() -> dict[str, Any]:
    field_list = load_json(FIELD_LIST_078)
    return {
        "schema": "mosim.ros2_runtime.camera_init_map_world_grounding_source_repair_future_gate_080.v1",
        "request_id": REQUEST_ID,
        "gate_name": "future_single_probe_non_fake_camera_init_map_world_grounding_gate_080",
        "pre_probe_source_static_requirements": [
            "selected_route_id is project_spark_fast_lio_map_frame_binding or another declared adapt/adopt route with source/config provenance",
            "invocation audit records selected map_frame/base_frame/lidar_frame/imu_frame or equivalent non-fake source/config anchor",
            "bare upstream fast_lio mapping.launch.py without map-frame binding audit is reference_only for grounding",
            "no arbitrary camera_init->map/world static TF, header rename, fake odom/map/cloud/TF, keyboard pose, or UE truth shortcut",
        ],
        "future_bundle_required_fields_from_078": field_list.get("tf_required_fields", []),
        "same_run_consistency_fields_from_078": field_list.get("same_run_consistency_fields", []),
        "acceptance_status": "real_same_run_evidence",
        "acceptance_requires_all": [
            "raw /tf event path and raw /tf_static event path are present",
            "dynamic_edges and static_edges are derived from raw event files",
            "chain connects camera_init to map, world, or ue_world in the same run",
            "camera_init_map_world_grounding.evidence_path is present",
            "camera_init_map_world_grounding.non_fake_basis is true",
            "forbidden planner/controller/setpoint topics are absent",
            "cleanup reports no non-task process kill and no residue",
            "base validator and route-specific validator are ok=true",
        ],
        "remain_blocked_when": [
            "selected route is reference_only or reject",
            "079-style dynamic_edges remain camera_init->body only and static_edges remain empty",
            "map_frame exists only as a parameter but no same-run TF/output chain links camera_init to map/world/ue_world",
            "grounding uses fake, arbitrary, header-only, alias-only, GUI-only, or UE-truth basis",
        ],
        "claim_boundary": [
            "080 is source/static repair readiness only.",
            "080 does not authorize a live probe, planner/controller handoff, setpoint publication, planner_ready, or closed_loop.",
        ],
    }


def build_summary(errors: list[str], matrix: list[dict[str, Any]], future_gate: dict[str, Any]) -> dict[str, Any]:
    route_counts: dict[str, int] = {}
    for route in matrix:
        route_counts[route["classification"]] = route_counts.get(route["classification"], 0) + 1
    tf_079 = load_json(TF_GROUNDING_079)
    return {
        "schema": "mosim.ros2_runtime.camera_init_map_world_grounding_source_repair_summary_080.v1",
        "request_id": REQUEST_ID,
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "ok": not errors,
        "mode": "source_static_repair_checker_only",
        "errors": errors,
        "route_counts": route_counts,
        "source_static_repair_surface": "project_spark_fast_lio_map_frame_binding",
        "precise_blocker_from_079": {
            "grounding_status": tf_079.get("camera_init_map_world_grounding", {}).get("status"),
            "dynamic_edges": tf_079.get("dynamic_edges"),
            "static_edges": tf_079.get("static_edges"),
            "basis": tf_079.get("camera_init_map_world_grounding", {}).get("basis"),
        },
        "future_single_probe_gate": future_gate["gate_name"],
        "can_claim_current_grounding": False,
        "can_authorize_live_probe_from_080": False,
        "can_authorize_controller_handoff_from_080": False,
        "live_actions": {
            "sourced_ros_setup": False,
            "ran_ros2": False,
            "started_rviz2": False,
            "started_fast_lio": False,
            "published_tf_or_setpoint": False,
            "consumed_live_probe": False,
        },
    }


def write_report(output_dir: Path, matrix: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# 080 camera_init map/world grounding source repair",
        "",
        "080 is a source/static repair checker. It does not run ROS2 or prove current grounding.",
        "",
        "## 079 blocker",
        "",
        f"- grounding_status: `{summary['precise_blocker_from_079']['grounding_status']}`",
        f"- dynamic_edges: `{summary['precise_blocker_from_079']['dynamic_edges']}`",
        f"- static_edges: `{summary['precise_blocker_from_079']['static_edges']}`",
        "",
        "## Route matrix",
        "",
    ]
    for route in matrix:
        lines.append(f"- `{route['route_id']}`: `{route['classification']}`")
    lines.extend(
        [
            "",
            "## Future gate",
            "",
            "The next authorized single probe must record a non-fake source/config map-frame anchor and still prove the raw same-run TF/static TF chain.",
            "A map_frame parameter, header rename, arbitrary static TF, GUI view, or truth shortcut alone is not grounding.",
            "",
            "## Claim boundary",
            "",
            "080 may claim only source/static repair readiness. It does not authorize a live probe, controller handoff, planner_ready, or closed_loop.",
            "",
        ]
    )
    (output_dir / "camera_init_map_world_grounding_source_repair_report_080.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def run(output_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    for path in [
        ROUTE_077,
        FIELD_LIST_078,
        TF_GROUNDING_079,
        FASTLIO_AUDIT_079,
        SPARK_LAUNCH,
        SCENE_REPLAY_LAUNCH,
        SETPOINT_ADAPTER,
        POSITION_CONVERTER,
    ]:
        require_file(errors, path)
    if errors:
        output_dir.mkdir(parents=True, exist_ok=True)
        summary = build_summary(errors, [], {"gate_name": "unavailable"})
        (output_dir / "camera_init_map_world_grounding_source_repair_summary_080.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return summary

    matrix = build_repair_matrix()
    future_gate = build_future_gate()

    routes = {route["route_id"]: route for route in matrix}
    spark = routes["project_spark_fast_lio_map_frame_binding"]["source_static_facts"]
    if not all(spark.values()):
        errors.append("project_spark_fast_lio_map_frame_binding source/static facts are incomplete")
    scene = routes["scene_replay_external_fastlio_launch_cmd_binding"]["source_static_facts"]
    if not scene["has_fastlio_launch_cmd_argument"]:
        errors.append("scene replay launch cannot pass an explicit FAST-LIO launch command")
    if load_json(TF_GROUNDING_079).get("camera_init_map_world_grounding", {}).get("status") != "blocked_absent":
        errors.append("079 grounding status is not blocked_absent; update this checker before reuse")
    if "mapping.launch.py" not in str(load_json(FASTLIO_AUDIT_079).get("launch", "")):
        errors.append("079 FAST-LIO audit did not preserve the expected upstream launch blocker")

    source_manifest = {
        "schema": "mosim.ros2_runtime.camera_init_map_world_grounding_source_manifest_080.v1",
        "request_id": REQUEST_ID,
        "files": {
            str(path.relative_to(PROJECT_ROOT)): {"sha256": sha256(path)}
            for path in [ROUTE_077, FIELD_LIST_078, TF_GROUNDING_079, FASTLIO_AUDIT_079, SPARK_LAUNCH, SCENE_REPLAY_LAUNCH]
        },
    }
    summary = build_summary(errors, matrix, future_gate)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "camera_init_map_world_grounding_source_repair_matrix_080.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "camera_init_map_world_grounding_future_single_probe_gate_080.json").write_text(
        json.dumps(future_gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "camera_init_map_world_grounding_source_manifest_080.json").write_text(
        json.dumps(source_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "camera_init_map_world_grounding_source_repair_summary_080.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_report(output_dir, matrix, summary)
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    summary = run(args.output_dir)
    print(json.dumps({"ok": summary["ok"], "errors": summary["errors"]}, ensure_ascii=False))
    return 0 if summary["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
