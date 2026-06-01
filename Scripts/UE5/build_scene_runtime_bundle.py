#!/usr/bin/env python3
"""Build executable runtime bundles for accepted UE scene simulation loops.

The bundle is not a new simulation result. It is a launch and acceptance
contract that ties together the rendered UE window, the native RViz/FAST-LIO
window, runtime recording/evaluation, and manual review gates for each accepted
scene.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


SCENE_RUNTIME = {
    "factoryenvironmentcollect": {
        "scene_source_id": "local_factoryenvironmentcollect",
        "map_package": "/Game/Maps/Demonstration",
        "map_id": "local_factoryenvironmentcollect",
        "accepted_scene_label": "Factory Environment Collect",
    },
    "derelictcorridormegascans": {
        "scene_source_id": "local_derelictcorridormegascans",
        "map_package": "/Game/DerelictCorridor/Maps/DerelictCorridor",
        "map_id": "local_derelictcorridormegascans",
        "accepted_scene_label": "Derelict Corridor Megascans",
    },
}


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def count_csv_rows(path: Path) -> int:
    return max(0, sum(1 for _ in path.read_text(encoding="utf-8").splitlines()) - 1)


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(item) for item in parts)


def require_file(scene_dir: Path, relative_name: str) -> Path:
    path = scene_dir / relative_name
    if not path.exists() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"missing/empty runtime bundle input: {path}")
    return path


def build_scene_bundle(output_root: Path, scene_id: str) -> dict[str, Any]:
    scene_key = scene_id.lower()
    if scene_key not in SCENE_RUNTIME:
        raise ValueError(f"unsupported scene: {scene_id}")
    info = SCENE_RUNTIME[scene_key]
    scene_dir = output_root / scene_key
    planner_path = require_file(scene_dir, "planner_summary.json")
    fastlio_manifest_path = require_file(scene_dir, "fastlio_adapter_manifest.json")
    navigation_path = require_file(scene_dir, "navigation_control_handoff.json")
    runtime_readiness_path = output_root / "UE_SCENE_RUNTIME_READINESS.json"
    if not runtime_readiness_path.exists():
        raise FileNotFoundError(f"missing runtime readiness report: {runtime_readiness_path}")

    required_artifacts = {
        "render_replay_csv": require_file(scene_dir, "render_replay.csv"),
        "local_known_map_frames_jsonl": require_file(scene_dir, "local_known_map_frames.jsonl"),
        "local_plan_frames_jsonl": require_file(scene_dir, "local_plan_frames.jsonl"),
        "lidar_point_frames_jsonl": require_file(scene_dir, "lidar_point_frames.jsonl"),
        "fastlio_replay_dataset_jsonl": require_file(scene_dir, "fastlio_replay_dataset.jsonl"),
        "pointcloud_merged_ply": require_file(scene_dir, "pointcloud_merged.ply"),
        "manual_review_packet_md": require_file(scene_dir, "manual_review_packet.md"),
        "control_reference_csv": require_file(scene_dir, "control_reference.csv"),
        "control_interface_package_json": require_file(scene_dir, "control_interface_package.json"),
        "planned_quintic_reference_params_json": require_file(scene_dir, "planned_quintic_reference_params.json"),
    }
    planner = read_json(planner_path)
    fastlio_manifest = read_json(fastlio_manifest_path)
    navigation = read_json(navigation_path)
    readiness = read_json(runtime_readiness_path)

    truth_policy_ok = (
        planner.get("global_truth_available_to_planner") is False
        and planner.get("collision_free_against_truth") is True
        and planner.get("buffered_collision_free_against_truth") is True
        and navigation.get("truth_policy", {}).get("global_truth_available_to_planner") is False
    )
    if not truth_policy_ok:
        raise ValueError(f"truth/planning policy is not safe for {scene_key}")

    runtime_blockers = list(readiness.get("overall", {}).get("runtime_blockers", []))
    runtime_blockers.extend(
        blocker
        for blocker in (
            "blocked_missing_ros1_runtime"
            if fastlio_manifest.get("status") == "blocked_missing_ros1_runtime"
            else None,
        )
        if blocker and blocker not in runtime_blockers
    )

    ue_review_command = (
        "OPEN_UE=1 OPEN_RVIZ=0 STREAM_LOOP_COUNT=1 STREAM_FPS=12 WAIT_UDP_SECONDS=45 "
        f"Scripts/UE5/review_scene_mapping_loop.sh {scene_key}"
    )
    rviz_review_command = f"Scripts/UE5/open_mapping_rviz_ros1.sh {scene_key}"
    fastlio_command = f"Scripts/UE5/run_fastlio_rviz_replay_ros1.sh {scene_key}"
    fastlio_bootstrap_command = "Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh"
    unreal_mcp_command = "Scripts/UE5/open_unreal_editor_mcp_listener.sh"
    record_command = (
        "python3 Scripts/UE5/record_fastlio_ros1_runtime.py "
        f"--scene-id {scene_key} "
        f"--output-dir Results/unreal_scene_mapping/{scene_key}/fastlio_runtime "
        "--duration-seconds 20"
    )
    evaluate_command = (
        "python3 Scripts/UE5/evaluate_fastlio_runtime.py "
        f"--scene-id {scene_key} "
        f"--truth-dataset Results/unreal_scene_mapping/{scene_key}/fastlio_replay_dataset.jsonl "
        f"--odometry-jsonl Results/unreal_scene_mapping/{scene_key}/fastlio_runtime/fastlio_odometry.jsonl "
        f"--output-json Results/unreal_scene_mapping/{scene_key}/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.json "
        f"--output-md Results/unreal_scene_mapping/{scene_key}/fastlio_runtime/FASTLIO_RUNTIME_EVALUATION.md "
        "--fail-on-threshold"
    )

    bundle = {
        "schema": "mosim.ue_scene_runtime_bundle.v1",
        "scene_id": scene_key,
        "accepted_scene_label": info["accepted_scene_label"],
        "status": "blocked_runtime_dependencies" if runtime_blockers else "ready_for_native_runtime_review",
        "runtime_blockers": runtime_blockers,
        "window_policy": {
            "rendered_scene_window": "Unreal/MoSimSceneLibrary",
            "mapping_window": "RViz/RViz2 or equivalent native robotics viewer",
            "html_allowed_as_active_pointcloud_window": False,
            "global_truth_used_by_planner": False,
        },
        "scene_runtime": {
            "scene_source_id": info["scene_source_id"],
            "map_package": info["map_package"],
            "map_id": info["map_id"],
            "ue_udp_port": 5005,
        },
        "counts": {
            "render_replay_frames": count_csv_rows(required_artifacts["render_replay_csv"]),
            "local_known_map_frames": count_jsonl(required_artifacts["local_known_map_frames_jsonl"]),
            "local_plan_frames": count_jsonl(required_artifacts["local_plan_frames_jsonl"]),
            "lidar_point_frames": count_jsonl(required_artifacts["lidar_point_frames_jsonl"]),
            "fastlio_replay_frames": count_jsonl(required_artifacts["fastlio_replay_dataset_jsonl"]),
            "path_cells": planner.get("path_cells"),
            "lidar_points": planner.get("merged_lidar_point_count"),
        },
        "truth_and_planning_policy": {
            "planner_policy": planner.get("planner_policy"),
            "global_truth_available_to_planner": planner.get("global_truth_available_to_planner"),
            "collision_free_against_truth": planner.get("collision_free_against_truth"),
            "buffered_collision_free_against_truth": planner.get("buffered_collision_free_against_truth"),
            "control_tracking_buffer_cells": planner.get("control_tracking_buffer_cells"),
        },
        "artifacts": {name: rel(path) for name, path in required_artifacts.items()},
        "commands": {
            "dry_run_ue_review": f"OPEN_UE=0 REVIEW_DRY_RUN=1 Scripts/UE5/review_scene_mapping_loop.sh {scene_key}",
            "unreal_editor_mcp_listener": unreal_mcp_command,
            "ue_rendered_scene_review": ue_review_command,
            "fastlio_ros1_workspace_bootstrap": fastlio_bootstrap_command,
            "rviz_mapping_window": rviz_review_command,
            "fastlio_rviz_runtime": fastlio_command,
            "fastlio_topic_check": "Scripts/UE5/check_fastlio_ros1_topics.sh",
            "fastlio_runtime_record": record_command,
            "fastlio_runtime_evaluate": evaluate_command,
        },
        "manual_acceptance": [
            "UE window shows the accepted real rendered scene, not a blockout/STL/blank map.",
            "UAV body follows the replay inside valid scene bounds without wall penetration.",
            "RViz/RViz2 shows PointCloud2, local occupancy/grid map, TF, local plan, and UAV path.",
            "FAST-LIO outputs /cloud_registered and /Odometry during a live ROS runtime run.",
            "evaluate_fastlio_runtime.py passes against replay truth before any localization claim.",
            "Planner has no access to global truth; exported truth is used only for validation.",
        ],
        "claim_boundary": [
            "This bundle is an execution contract and launch package, not proof that runtime already ran.",
            "HTML is not an accepted active point-cloud/map window.",
            "FAST-LIO localization remains unclaimed until ROS runtime topics are recorded and evaluated.",
            "MWORKS dynamics/control evidence remains separate from UE/RViz visual runtime evidence.",
        ],
    }
    bundle_path = scene_dir / "runtime_review_bundle.json"
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bundle


def write_scene_markdown(scene_dir: Path, bundle: dict[str, Any]) -> None:
    lines = [
        f"# Runtime Review Bundle: {bundle['scene_id']}",
        "",
        f"- status: `{bundle['status']}`",
        f"- runtime_blockers: {', '.join(f'`{item}`' for item in bundle['runtime_blockers']) or 'none'}",
        f"- rendered_scene_window: `{bundle['window_policy']['rendered_scene_window']}`",
        f"- mapping_window: `{bundle['window_policy']['mapping_window']}`",
        f"- html_active_pointcloud_window: `{str(bundle['window_policy']['html_allowed_as_active_pointcloud_window']).lower()}`",
        f"- global_truth_used_by_planner: `{str(bundle['window_policy']['global_truth_used_by_planner']).lower()}`",
        "",
        "Commands:",
    ]
    for name, command in bundle["commands"].items():
        lines.append(f"- `{name}`: `{command}`")
    lines.extend(["", "Manual acceptance:"])
    for item in bundle["manual_acceptance"]:
        lines.append(f"- {item}")
    lines.extend(["", "Claim boundary:"])
    for item in bundle["claim_boundary"]:
        lines.append(f"- {item}")
    (scene_dir / "runtime_review_bundle.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_wrapper(scene_dir: Path, bundle: dict[str, Any]) -> None:
    path = scene_dir / "run_native_runtime_review.sh"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "PROJECT_ROOT=\"/mnt/c/Users/HP/Desktop/MoSim\"",
        "cd \"${PROJECT_ROOT}\"",
        "",
        "# This wrapper opens native runtime review surfaces only.",
        "# UE is the rendered-scene window; RViz is the point-cloud/map window.",
        "# Browser HTML is not used.",
        "",
        f"SCENE_ID={shlex.quote(bundle['scene_id'])}",
        "START_UE=${START_UE:-1}",
        "START_RVIZ=${START_RVIZ:-1}",
        "START_FASTLIO=${START_FASTLIO:-0}",
        "RECORD_FASTLIO=${RECORD_FASTLIO:-0}",
        "WAIT_FOR_WINDOWS=${WAIT_FOR_WINDOWS:-1}",
        "PIDS=()",
        "",
        "wait_for_background() {",
        "  local status=0",
        "  for pid in \"${PIDS[@]:-}\"; do",
        "    if ! wait \"${pid}\"; then",
        "      status=1",
        "    fi",
        "  done",
        "  return \"${status}\"",
        "}",
        "",
        "if [[ \"${START_UE}\" == \"1\" ]]; then",
        f"  {bundle['commands']['ue_rendered_scene_review']} &",
        "  PIDS+=(\"$!\")",
        "fi",
        "",
        "if [[ \"${START_RVIZ}\" == \"1\" ]]; then",
        f"  {bundle['commands']['rviz_mapping_window']} &",
        "  PIDS+=(\"$!\")",
        "fi",
        "",
        "if [[ \"${START_FASTLIO}\" == \"1\" ]]; then",
        f"  {bundle['commands']['fastlio_rviz_runtime']} &",
        "  PIDS+=(\"$!\")",
        "fi",
        "",
        "if [[ \"${RECORD_FASTLIO}\" == \"1\" ]]; then",
        f"  {bundle['commands']['fastlio_runtime_record']}",
        f"  {bundle['commands']['fastlio_runtime_evaluate']}",
        "fi",
        "",
        "if [[ \"${WAIT_FOR_WINDOWS}\" == \"1\" ]]; then",
        "  wait_for_background",
        "fi",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)


def write_summary(output_root: Path, bundles: list[dict[str, Any]]) -> None:
    lines = [
        "# UE Scene Runtime Bundle Status",
        "",
        "| Scene | Status | Frames | LiDAR Points | Runtime Blockers | Mapping Window |",
        "|---|---|---:|---:|---|---|",
    ]
    for bundle in bundles:
        blockers = "<br>".join(f"`{item}`" for item in bundle["runtime_blockers"]) or "none"
        lines.append(
            f"| `{bundle['scene_id']}` | `{bundle['status']}` | "
            f"{bundle['counts']['render_replay_frames']} | {bundle['counts']['lidar_points']} | "
            f"{blockers} | `{bundle['window_policy']['mapping_window']}` |"
        )
    lines.extend(
        [
            "",
            "This status file is an execution contract summary, not runtime evidence.",
            "Runtime evidence requires native UE/RViz windows plus FAST-LIO topic recording/evaluation.",
        ]
    )
    (output_root / "UE_SCENE_RUNTIME_BUNDLE_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = project_path(args.output_root)
    scene_ids = args.scene or list(DEFAULT_SCENES)
    bundles = []
    for scene_id in scene_ids:
        scene_key = scene_id.lower()
        scene_dir = output_root / scene_key
        bundle = build_scene_bundle(output_root, scene_key)
        write_scene_markdown(scene_dir, bundle)
        write_wrapper(scene_dir, bundle)
        bundles.append(bundle)
        print(f"{scene_key}: {bundle['status']} blockers={','.join(bundle['runtime_blockers']) or 'none'}")
    write_summary(output_root, bundles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
