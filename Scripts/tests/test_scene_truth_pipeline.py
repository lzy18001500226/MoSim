#!/usr/bin/env python3
"""Regression checks for UE scene truth mapping/planning artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "scene_truth_pipeline.py"
    spec = importlib.util.spec_from_file_location("scene_truth_pipeline", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load scene_truth_pipeline.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["scene_truth_pipeline"] = module
    spec.loader.exec_module(module)
    return module


def test_validated_scenes_produce_unknown_map_planning_handoff() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "scene_truth_pipeline_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        reports = []
        for scene_id in ("factoryenvironmentcollect", "derelictcorridormegascans"):
            truth_path = module.scene_truth_path(scene_id)
            truth = module.load_truth(truth_path)
            profile = module.default_profile(str(truth["scene_id"]), truth_path)
            reports.append(module.run_scene(profile, output_root))

        module.write_run_summary(output_root / "RUN_SUMMARY.md", reports)

        for report in reports:
            scene_dir = output_root / report["scene_id"]
            if report["global_truth_available_to_planner"]:
                raise AssertionError(report)
            if not report["collision_free_against_truth"]:
                raise AssertionError(report)
            if not report["buffered_collision_free_against_truth"]:
                raise AssertionError(report)
            if report["control_tracking_buffer_cells"] < 1:
                raise AssertionError(report)
            if report["path_cells"] < 10:
                raise AssertionError(report)
            if report["merged_lidar_point_count"] <= 0:
                raise AssertionError(report)

            fastlio = json.loads((scene_dir / "fastlio_handoff.json").read_text(encoding="utf-8"))
            if fastlio["status"] != "offline_simulated_sensor_handoff_ready":
                raise AssertionError(fastlio)
            generated = fastlio["generated_inputs"]
            for key in ("trajectory_csv", "render_replay_csv", "local_known_map_jsonl", "local_plan_jsonl", "lidar_point_frames_jsonl", "merged_pointcloud_ply", "viewer_html", "lidar_frames_dir"):
                if key not in generated:
                    raise AssertionError(fastlio)

            render_replay = scene_dir / "render_replay.csv"
            with render_replay.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            if len(rows) != report["path_cells"]:
                raise AssertionError((render_replay, len(rows), report["path_cells"]))
            required_columns = {"time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "roll", "pitch", "yaw", "u1", "u2", "u3", "u4"}
            if set(rows[0]) != required_columns:
                raise AssertionError(rows[0])

            local_known_map = scene_dir / "local_known_map_frames.jsonl"
            frames = [json.loads(line) for line in local_known_map.read_text(encoding="utf-8").splitlines() if line]
            if len(frames) != report["path_cells"]:
                raise AssertionError((local_known_map, len(frames), report["path_cells"]))
            if not frames[0]["evidence_backed"] or frames[0]["render_only"]:
                raise AssertionError(frames[0])
            states = {cell["state"] for frame in frames for cell in frame["cells"]}
            if "observed_free" not in states or "observed_occupied" not in states:
                raise AssertionError(states)

            local_plan_path = scene_dir / "local_plan_frames.jsonl"
            plan_frames = [json.loads(line) for line in local_plan_path.read_text(encoding="utf-8").splitlines() if line]
            if len(plan_frames) != report["path_cells"]:
                raise AssertionError((local_plan_path, len(plan_frames), report["path_cells"]))
            if plan_frames[0]["global_truth_available_to_planner"]:
                raise AssertionError(plan_frames[0])
            if not plan_frames[0]["evidence_backed"] or plan_frames[0]["render_only"]:
                raise AssertionError(plan_frames[0])
            if len(plan_frames[0]["points_m"]) < 2:
                raise AssertionError(plan_frames[0])

            lidar_frames_path = scene_dir / "lidar_point_frames.jsonl"
            lidar_frames = [json.loads(line) for line in lidar_frames_path.read_text(encoding="utf-8").splitlines() if line]
            if len(lidar_frames) != report["path_cells"]:
                raise AssertionError((lidar_frames_path, len(lidar_frames), report["path_cells"]))
            if not lidar_frames[0]["evidence_backed"] or lidar_frames[0]["render_only"]:
                raise AssertionError(lidar_frames[0])
            if not any(frame["points_m"] for frame in lidar_frames):
                raise AssertionError("no frame-level lidar points")

            merged_ply = scene_dir / "pointcloud_merged.ply"
            if merged_ply.stat().st_size <= 128:
                raise AssertionError(merged_ply)

        if "FAST-LIO artifacts are input handoff files" not in (output_root / "RUN_SUMMARY.md").read_text(encoding="utf-8"):
            raise AssertionError("run summary missing FAST-LIO policy")
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_validated_scenes_produce_unknown_map_planning_handoff()
    print("[OK] UE scene truth pipeline regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
