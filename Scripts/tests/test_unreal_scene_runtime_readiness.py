#!/usr/bin/env python3
"""Regression checks for UE scene runtime readiness preflight."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_runtime_readiness_separates_file_loop_from_runtime_blockers() -> None:
    scene_pipeline = load_module(
        "scene_truth_pipeline",
        ROOT / "Scripts" / "UE5" / "scene_truth_pipeline.py",
    )
    fastlio = load_module(
        "prepare_fastlio_replay",
        ROOT / "Scripts" / "UE5" / "prepare_fastlio_replay.py",
    )
    navigation = load_module(
        "build_navigation_handoff",
        ROOT / "Scripts" / "UE5" / "build_navigation_handoff.py",
    )
    readiness = load_module(
        "check_unreal_scene_runtime_readiness",
        ROOT / "Scripts" / "UE5" / "check_unreal_scene_runtime_readiness.py",
    )
    temp_root = ROOT / "Results" / "tmp" / "unreal_scene_runtime_readiness_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        scene_id = "factoryenvironmentcollect"
        truth_path = scene_pipeline.scene_truth_path(scene_id)
        truth = scene_pipeline.load_truth(truth_path)
        profile = scene_pipeline.default_profile(str(truth["scene_id"]), truth_path)
        scene_pipeline.run_scene(profile, output_root)
        fastlio.prepare_scene(output_root / scene_id)
        navigation.build_scene_handoff(output_root / scene_id)
        (output_root / scene_id / "manual_review_packet.md").write_text(
            "# Manual Review Packet\n\nNative RViz point-cloud review route.\n",
            encoding="utf-8",
        )
        collision_dir = output_root / scene_id / "mworks_smoke" / "collision"
        collision_dir.mkdir(parents=True, exist_ok=True)
        (collision_dir / "mworks_scene_truth_collision.json").write_text(
            json.dumps({"pass": True}, indent=2) + "\n",
            encoding="utf-8",
        )
        args = type(
            "Args",
            (),
            {
                "scene": [scene_id],
                "output_root": output_root,
                "editor_host": "127.0.0.1",
                "editor_port": 1,
                "timeout_seconds": 0.01,
            },
        )()
        report = readiness.build_report(args)
        if not report["overall"]["file_loop_ready"]:
            raise AssertionError(report)
        if report["overall"]["runtime_ready"]:
            raise AssertionError(report)
        if report["window_policy"]["html_allowed_as_active_pointcloud_window"] is not False:
            raise AssertionError(report)
        if report["window_policy"]["global_truth_used_by_planner"] is not False:
            raise AssertionError(report)
        if "RViz/RViz2" not in report["window_policy"]["mapping_window"]:
            raise AssertionError(report)
        if "unreal_editor_listener_unavailable" not in report["overall"]["runtime_blockers"]:
            raise AssertionError(report)
        readiness.write_markdown(output_root / "UE_SCENE_RUNTIME_READINESS.md", report)
        text = (output_root / "UE_SCENE_RUNTIME_READINESS.md").read_text(encoding="utf-8")
        if "file_loop_ready" not in text or "runtime_blockers" not in text:
            raise AssertionError(text)
        for phrase in (
            "mapping_window",
            "html_active_pointcloud_window: `false`",
            "global_truth_used_by_planner: `false`",
            "RVIZ_PROFILE=split",
            "open_mapping_rviz_ros2.sh",
            "run_fastlio_rviz_replay_ros2.sh",
            "check_fastlio_ros2_topics.sh",
            "open_unreal_editor_mcp_listener.sh",
        ):
            if phrase not in text:
                raise AssertionError(text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_runtime_readiness_separates_file_loop_from_runtime_blockers()
    print("[OK] UE scene runtime readiness regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
