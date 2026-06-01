#!/usr/bin/env python3
"""Regression checks for UE scene native runtime review bundles."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]
SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_fake_readiness(output_root: Path) -> None:
    payload = {
        "schema": "mosim.unreal_scene_runtime_readiness.v1",
        "overall": {
            "file_loop_ready": True,
            "runtime_ready": False,
            "runtime_blockers": [
                "missing_ros1_rviz_catkin_runtime",
                "unreal_editor_listener_unavailable",
            ],
        },
        "window_policy": {
            "rendered_scene_window": "Unreal/MoSimSceneLibrary",
            "mapping_window": "RViz/RViz2 or equivalent native robotics viewer",
            "html_allowed_as_active_pointcloud_window": False,
            "global_truth_used_by_planner": False,
        },
    }
    (output_root / "UE_SCENE_RUNTIME_READINESS.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_runtime_bundle_contract() -> None:
    scene_pipeline = load_module("scene_truth_pipeline", "Scripts/UE5/scene_truth_pipeline.py")
    fastlio = load_module("prepare_fastlio_replay", "Scripts/UE5/prepare_fastlio_replay.py")
    navigation = load_module("build_navigation_handoff", "Scripts/UE5/build_navigation_handoff.py")
    bundle_builder = load_module("build_scene_runtime_bundle", "Scripts/UE5/build_scene_runtime_bundle.py")

    temp_root = ROOT / "Results" / "tmp" / "scene_runtime_bundle_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        for scene_id in SCENES:
            truth_path = scene_pipeline.scene_truth_path(scene_id)
            truth = scene_pipeline.load_truth(truth_path)
            profile = scene_pipeline.default_profile(str(truth["scene_id"]), truth_path)
            scene_pipeline.run_scene(profile, output_root)
            fastlio.prepare_scene(output_root / scene_id)
            navigation.build_scene_handoff(output_root / scene_id)
            (output_root / scene_id / "manual_review_packet.md").write_text(
                "# Manual Review Packet\n\nRViz/native point-cloud window required.\n",
                encoding="utf-8",
            )
        write_fake_readiness(output_root)

        bundles = []
        for scene_id in SCENES:
            scene_dir = output_root / scene_id
            bundle = bundle_builder.build_scene_bundle(output_root, scene_id)
            bundle_builder.write_scene_markdown(scene_dir, bundle)
            bundle_builder.write_wrapper(scene_dir, bundle)
            bundles.append(bundle)
        bundle_builder.write_summary(output_root, bundles)

        summary = (output_root / "UE_SCENE_RUNTIME_BUNDLE_STATUS.md").read_text(encoding="utf-8")
        if "RViz/RViz2 or equivalent native robotics viewer" not in summary:
            raise AssertionError(summary)
        if "not runtime evidence" not in summary:
            raise AssertionError(summary)

        for bundle in bundles:
            scene_id = bundle["scene_id"]
            scene_dir = output_root / scene_id
            if bundle["window_policy"]["html_allowed_as_active_pointcloud_window"] is not False:
                raise AssertionError(bundle)
            if bundle["window_policy"]["global_truth_used_by_planner"] is not False:
                raise AssertionError(bundle)
            if "missing_ros1_rviz_catkin_runtime" not in bundle["runtime_blockers"]:
                raise AssertionError(bundle)
            if "unreal_editor_listener_unavailable" not in bundle["runtime_blockers"]:
                raise AssertionError(bundle)
            if bundle["status"] != "blocked_runtime_dependencies":
                raise AssertionError(bundle)
            if bundle["counts"]["render_replay_frames"] <= 0:
                raise AssertionError(bundle)
            if bundle["counts"]["fastlio_replay_frames"] <= 0:
                raise AssertionError(bundle)
            for command_name in (
                "unreal_editor_mcp_listener",
                "ue_rendered_scene_review",
                "fastlio_ros1_workspace_bootstrap",
                "rviz_mapping_window",
                "rviz_planning_grid_window",
                "rviz_fastlio_pointcloud_window",
                "fastlio_rviz_runtime",
                "fastlio_runtime_record",
                "fastlio_runtime_evaluate",
            ):
                if command_name not in bundle["commands"]:
                    raise AssertionError(bundle)
            if "open_mapping_rviz_ros1.sh" not in bundle["commands"]["rviz_mapping_window"]:
                raise AssertionError(bundle)
            if "RVIZ_PROFILE=split" not in bundle["commands"]["rviz_mapping_window"]:
                raise AssertionError(bundle)
            if "RVIZ_PROFILE=planning_grid" not in bundle["commands"]["rviz_planning_grid_window"]:
                raise AssertionError(bundle)
            if "RVIZ_PROFILE=fastlio_pointcloud" not in bundle["commands"]["rviz_fastlio_pointcloud_window"]:
                raise AssertionError(bundle)
            if "run_fastlio_rviz_replay_ros1.sh" not in bundle["commands"]["fastlio_rviz_runtime"]:
                raise AssertionError(bundle)
            if "bootstrap_fastlio_ros1_workspace.sh" not in bundle["commands"]["fastlio_ros1_workspace_bootstrap"]:
                raise AssertionError(bundle)
            if "open_unreal_editor_mcp_listener.sh" not in bundle["commands"]["unreal_editor_mcp_listener"]:
                raise AssertionError(bundle)

            md = (scene_dir / "runtime_review_bundle.md").read_text(encoding="utf-8")
            if "html_active_pointcloud_window: `false`" not in md:
                raise AssertionError(md)
            wrapper = (scene_dir / "run_native_runtime_review.sh").read_text(encoding="utf-8")
            if "Browser HTML is not used" not in wrapper:
                raise AssertionError(wrapper)
            if "RVIZ_PROFILE=split" not in wrapper:
                raise AssertionError(wrapper)
            if "PIDS=()" not in wrapper or "wait_for_background" not in wrapper:
                raise AssertionError(wrapper)
            if "review_scene_mapping_loop.sh" not in wrapper or "&" not in wrapper:
                raise AssertionError(wrapper)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_runtime_bundle_contract()
    print("[OK] UE scene runtime bundle regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
