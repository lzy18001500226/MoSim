#!/usr/bin/env python3
"""Check runtime readiness for the accepted UE scene mapping loop.

This is a non-invasive preflight. It does not launch UE, ROS, RViz, FAST-LIO,
or MWORKS. It separates file-level closed-loop readiness from runtime blockers
so we do not claim localization/navigation evidence that has not run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import socket
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


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


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def count_jsonl_rows(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def command_map() -> dict[str, str | None]:
    return {
        name: shutil.which(name)
        for name in ("ros2", "roscore", "roslaunch", "rostopic", "rviz", "rviz2", "catkin_make", "colcon")
    }


def tcp_probe(host: str, port: int, timeout_s: float) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return {"host": host, "port": port, "ok": True}
    except OSError as exc:
        return {"host": host, "port": port, "ok": False, "error": f"{exc.__class__.__name__}: {exc}"}


def file_status(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def ros_mapping_runtime_env() -> dict[str, Any]:
    path = ROOT / "Scripts/UE5/check_ros_mapping_runtime_env.py"
    spec = importlib.util.spec_from_file_location("check_ros_mapping_runtime_env", path)
    if spec is None or spec.loader is None:
        return {
            "schema": "mosim.ros_mapping_runtime_env.v1",
            "ready_for_native_mapping_runtime": False,
            "blockers": [f"unable_to_load:{rel(path)}"],
        }
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_ros_mapping_runtime_env"] = module
    spec.loader.exec_module(module)
    args = type("Args", (), {"fast_lio_package": "fast_lio"})()
    return module.build_report(args)


def scene_status(output_root: Path, scene_id: str) -> dict[str, Any]:
    scene_dir = output_root / scene_id
    planner_path = scene_dir / "planner_summary.json"
    fastlio_path = scene_dir / "fastlio_adapter_manifest.json"
    handoff_path = scene_dir / "navigation_control_handoff.json"
    collision_path = scene_dir / "mworks_smoke" / "collision" / "mworks_scene_truth_collision.json"
    required = {
        "planner_summary": planner_path,
        "render_replay_csv": scene_dir / "render_replay.csv",
        "local_known_map_frames": scene_dir / "local_known_map_frames.jsonl",
        "local_plan_frames": scene_dir / "local_plan_frames.jsonl",
        "lidar_point_frames": scene_dir / "lidar_point_frames.jsonl",
        "pointcloud_merged": scene_dir / "pointcloud_merged.ply",
        "fastlio_replay_dataset": scene_dir / "fastlio_replay_dataset.jsonl",
        "fastlio_manifest": fastlio_path,
        "navigation_handoff": handoff_path,
        "manual_review_packet": scene_dir / "manual_review_packet.md",
        "mworks_collision": collision_path,
    }
    issues: list[str] = []
    for label, path in required.items():
        if not path.exists() or path.stat().st_size <= 0:
            issues.append(f"missing_or_empty:{label}:{rel(path)}")

    planner = read_json(planner_path) if planner_path.exists() else {}
    fastlio = read_json(fastlio_path) if fastlio_path.exists() else {}
    handoff = read_json(handoff_path) if handoff_path.exists() else {}
    collision = read_json(collision_path) if collision_path.exists() else {}

    if planner.get("global_truth_available_to_planner") is not False:
        issues.append("planner_global_truth_not_hidden")
    if planner.get("collision_free_against_truth") is not True:
        issues.append("planner_reference_not_collision_free")
    if planner.get("buffered_collision_free_against_truth") is not True:
        issues.append("planner_buffered_reference_not_collision_free")
    if handoff.get("status") != "ready_for_mworks_controller_interface_smoke":
        issues.append(f"navigation_handoff_status:{handoff.get('status')}")
    if collision.get("pass") is not True:
        issues.append("mworks_collision_gate_not_passed")

    return {
        "scene_id": scene_id,
        "file_loop_ready": not issues,
        "issues": issues,
        "planner": {
            "path_cells": planner.get("path_cells"),
            "replans": planner.get("replan_count"),
            "lidar_points": planner.get("merged_lidar_point_count"),
            "global_truth_available_to_planner": planner.get("global_truth_available_to_planner"),
            "buffered_collision_free_against_truth": planner.get("buffered_collision_free_against_truth"),
        },
        "fastlio": {
            "status": fastlio.get("status", "missing"),
            "ros1_ready": bool(fastlio.get("ros_environment", {}).get("ros1_ready")),
            "ros2_replay_ready": bool(fastlio.get("ros_environment", {}).get("ros2_replay_ready")),
        },
        "counts": {
            "render_replay_rows": count_csv_rows(scene_dir / "render_replay.csv"),
            "local_known_map_frames": count_jsonl_rows(scene_dir / "local_known_map_frames.jsonl"),
            "local_plan_frames": count_jsonl_rows(scene_dir / "local_plan_frames.jsonl"),
            "lidar_point_frames": count_jsonl_rows(scene_dir / "lidar_point_frames.jsonl"),
            "fastlio_replay_frames": count_jsonl_rows(scene_dir / "fastlio_replay_dataset.jsonl"),
        },
        "artifacts": {label: file_status(path) for label, path in required.items()},
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    output_root = project_path(args.output_root)
    commands = command_map()
    ros1_ready = all(commands[name] for name in ("roscore", "roslaunch", "rostopic", "rviz", "catkin_make"))
    ros2_ready = all(commands[name] for name in ("ros2", "rviz2", "colcon"))
    ue_project = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
    bridge = ROOT / "UE5/Bridge/QuadrotorMworksBridge.uplugin"
    rviz_pointcloud_config = ROOT / "Config/rviz/mosim_uav_fastlio_pointcloud.rviz"
    rviz2_pointcloud_config = ROOT / "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz"
    fastlio_bootstrap = ROOT / "Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh"
    fastlio_rviz_runner = ROOT / "Scripts/UE5/run_fastlio_rviz_replay_ros1.sh"
    fastlio_topic_checker = ROOT / "Scripts/UE5/check_fastlio_ros1_topics.sh"
    factory_headless_runner = ROOT / "Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh"
    fastlio_ros2_topic_checker = ROOT / "Scripts/UE5/check_fastlio_ros2_topics.sh"
    mworks_uav_bridge = ROOT / "Scripts/ros/publish_mworks_uav_state_ros2.py"
    unreal_mcp_opener = ROOT / "Scripts/UE5/open_unreal_editor_mcp_listener.sh"
    fast_lio_repo = ROOT / "References/Lab/FAST_LIO/package.xml"
    ros_env = ros_mapping_runtime_env()
    scene_reports = [scene_status(output_root, scene.lower()) for scene in args.scene]
    runtime_blockers: list[str] = []
    runtime_degraded = list(ros_env.get("degraded", []))
    if not ros2_ready:
        runtime_blockers.append("missing_ros2_rviz2_runtime")
    if not ros1_ready:
        runtime_degraded.append("missing_ros1_rviz_catkin_runtime")
    for blocker in ros_env.get("blockers", []):
        prefixed = f"ros_env:{blocker}"
        if prefixed not in runtime_blockers:
            runtime_blockers.append(prefixed)
    if not fast_lio_repo.exists():
        runtime_blockers.append("missing_fast_lio_reference_repo")
    editor_listener = tcp_probe(args.editor_host, args.editor_port, args.timeout_seconds)
    if not editor_listener["ok"]:
        runtime_blockers.append("unreal_editor_listener_unavailable")
    if any(not scene["file_loop_ready"] for scene in scene_reports):
        runtime_blockers.append("scene_file_loop_not_ready")

    return {
        "schema": "mosim.unreal_scene_runtime_readiness.v1",
        "window_policy": {
            "rendered_scene_window": "Unreal/MoSimSceneLibrary",
            "mapping_window": "RViz/RViz2 or equivalent native robotics viewer",
            "html_role": "offline_report_preview_only",
            "html_allowed_as_active_pointcloud_window": False,
            "ue_overlay_replaces_rviz": False,
            "global_truth_used_by_planner": False,
        },
        "claim_boundary": [
            "This is a preflight report, not a new simulation result.",
            "file_loop_ready=true means required artifacts and validation gates exist.",
            "The primary point-cloud/map review route is a native ROS/RViz window, not browser HTML.",
            "UE rendered overlays and file previews do not replace RViz/RViz2 mapping evidence.",
            "Global scene truth is a validation oracle only and is not a planner input.",
            "Keyboard/mouse controls are for UE/RViz view movement only; UAV pose must come from MWORKS/controller state.",
            "runtime_ready=true additionally requires ROS2/RViz2 runtime and live UE editor listener when interactive editor automation is needed.",
            "FAST-LIO localization remains unclaimed until a real ROS2 FAST-LIO-family package or approved ROS1 bridge publishes /cloud_registered and /Odometry.",
        ],
        "overall": {
            "file_loop_ready": all(scene["file_loop_ready"] for scene in scene_reports),
            "runtime_ready": not runtime_blockers,
            "runtime_blockers": runtime_blockers,
            "runtime_degraded": runtime_degraded,
        },
        "project": {
            "ue_project": file_status(ue_project),
            "bridge_plugin": file_status(bridge),
            "rviz_fastlio_pointcloud_config": file_status(rviz_pointcloud_config),
            "rviz2_fastlio_pointcloud_config": file_status(rviz2_pointcloud_config),
            "fastlio_workspace_bootstrap": file_status(fastlio_bootstrap),
            "fastlio_rviz_runner": file_status(fastlio_rviz_runner),
            "fastlio_topic_checker": file_status(fastlio_topic_checker),
            "factory_fastlio_mid360_headless_runner": file_status(factory_headless_runner),
            "mworks_uav_state_ros2_bridge": file_status(mworks_uav_bridge),
            "fastlio_ros2_topic_checker": file_status(fastlio_ros2_topic_checker),
            "unreal_editor_mcp_listener_opener": file_status(unreal_mcp_opener),
            "fast_lio_reference_package": file_status(fast_lio_repo),
        },
        "runtime": {
            "commands": commands,
            "ros1_ready": ros1_ready,
            "ros2_ready": ros2_ready,
            "ros_mapping_runtime_env": ros_env,
            "editor_listener": editor_listener,
        },
        "scenes": scene_reports,
        "next_commands": [
            "python3 Scripts/UE5/summarize_scene_closed_loop.py --fail-on-issue",
            "python3 Scripts/ros/publish_mworks_uav_state_ros2.py --dry-run --mworks-raw-csv Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv --lidar-point-frames-jsonl Results/unreal_scene_mapping/factoryenvironmentcollect/livox_like_lidar_frames_mworks_body.jsonl --max-frames 2",
            "DRY_RUN=1 Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh",
            "DRY_RUN=1 Scripts/UE5/check_fastlio_ros2_topics.sh",
            "DRY_RUN=1 Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh",
            "DRY_RUN=1 Scripts/UE5/open_unreal_editor_mcp_listener.sh",
            "python3 Scripts/UE5/check_ros_mapping_runtime_env.py --write",
            "source /opt/ros/humble/setup.bash",
            "Scripts/UE5/open_unreal_editor_mcp_listener.sh  # opens UE Editor and waits up to 60s for UnrealMCP listener",
            "rviz2 -d Config/rviz2/mosim_uav_fastlio_pointcloud.rviz  # view/camera controls only; UAV motion is not keyboard-driven",
            "Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh  # Factory MWORKS/Livox/FAST-LIO headless gate",
            "Scripts/UE5/check_fastlio_ros2_topics.sh  # during a live ROS2 run; REQUIRE_FASTLIO_OUTPUTS=0 checks inputs only",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# UE Scene Runtime Readiness",
        "",
        "This is a preflight report, not a new simulation result.",
        "The primary point-cloud/map review route is a native ROS/RViz window, not browser HTML.",
        "UE overlays and native file previews do not replace RViz/RViz2 evidence.",
        "Global scene truth is a validation oracle only and is not a planner input.",
        "Keyboard/mouse controls are view controls only; they must not drive UAV pose.",
        "",
        f"- file_loop_ready: `{str(report['overall']['file_loop_ready']).lower()}`",
        f"- runtime_ready: `{str(report['overall']['runtime_ready']).lower()}`",
        f"- runtime_blockers: {', '.join(f'`{item}`' for item in report['overall']['runtime_blockers']) or 'none'}",
        f"- runtime_degraded: {', '.join(f'`{item}`' for item in report['overall'].get('runtime_degraded', [])) or 'none'}",
        f"- mapping_window: `{report['window_policy']['mapping_window']}`",
        f"- html_active_pointcloud_window: `{str(report['window_policy']['html_allowed_as_active_pointcloud_window']).lower()}`",
        f"- global_truth_used_by_planner: `{str(report['window_policy']['global_truth_used_by_planner']).lower()}`",
        "",
        "| Scene | File Loop | Path Cells | LiDAR Points | FAST-LIO | Frames | Issues |",
        "|---|---|---:|---:|---|---:|---|",
    ]
    for scene in report["scenes"]:
        frames = scene["counts"]["render_replay_rows"]
        issues = "<br>".join(f"`{item}`" for item in scene["issues"]) if scene["issues"] else ""
        lines.append(
            f"| `{scene['scene_id']}` | `{str(scene['file_loop_ready']).lower()}` | "
            f"{scene['planner']['path_cells']} | {scene['planner']['lidar_points']} | "
            f"`{scene['fastlio']['status']}` | {frames} | {issues} |"
        )
    lines.extend([
        "",
        "Runtime commands:",
    ])
    for name, value in report["runtime"]["commands"].items():
        lines.append(f"- `{name}`: `{value}`")
    lines.extend([
        "",
        "Next commands:",
    ])
    for command in report["next_commands"]:
        lines.append(f"- `{command}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[], help="Scene id. Default: accepted Factory and Derelict scenes.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--editor-host", default="127.0.0.1")
    parser.add_argument("--editor-port", type=int, default=55557)
    parser.add_argument("--timeout-seconds", type=float, default=1.0)
    parser.add_argument("--write", action="store_true", help="Write JSON/Markdown readiness reports under the output root.")
    parser.add_argument("--fail-on-runtime-blocker", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.scene = args.scene or list(DEFAULT_SCENES)
    report = build_report(args)
    output_root = project_path(args.output_root)
    if args.write:
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "UE_SCENE_RUNTIME_READINESS.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_markdown(output_root / "UE_SCENE_RUNTIME_READINESS.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_runtime_blocker and report["overall"]["runtime_blockers"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
