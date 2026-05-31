#!/usr/bin/env python3
"""Regression checks for the FAST-LIO replay adapter handoff."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_prepare_module():
    path = ROOT / "Scripts" / "UE5" / "prepare_fastlio_replay.py"
    spec = importlib.util.spec_from_file_location("prepare_fastlio_replay", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load prepare_fastlio_replay.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["prepare_fastlio_replay"] = module
    spec.loader.exec_module(module)
    return module


def test_fastlio_replay_adapter_outputs() -> None:
    scene_pipeline_path = ROOT / "Scripts" / "UE5" / "scene_truth_pipeline.py"
    scene_spec = importlib.util.spec_from_file_location("scene_truth_pipeline", scene_pipeline_path)
    if scene_spec is None or scene_spec.loader is None:
        raise RuntimeError("Unable to load scene_truth_pipeline.py")
    scene_pipeline = importlib.util.module_from_spec(scene_spec)
    sys.modules["scene_truth_pipeline"] = scene_pipeline
    scene_spec.loader.exec_module(scene_pipeline)

    temp_root = ROOT / "Results" / "tmp" / "fastlio_replay_adapter_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        for scene_id in ("factoryenvironmentcollect", "derelictcorridormegascans"):
            truth_path = scene_pipeline.scene_truth_path(scene_id)
            truth = scene_pipeline.load_truth(truth_path)
            profile = scene_pipeline.default_profile(str(truth["scene_id"]), truth_path)
            scene_pipeline.run_scene(profile, output_root)

        module = load_prepare_module()
        manifests = [
            module.prepare_scene(output_root / scene_id)
            for scene_id in ("factoryenvironmentcollect", "derelictcorridormegascans")
        ]
        module.write_status_markdown(output_root / "FASTLIO_REPLAY_STATUS.md", manifests)

        for manifest in manifests:
            if "FAST-LIO input adapter" not in " ".join(manifest["claim_boundary"]):
                raise AssertionError(manifest)
            if manifest["status"] not in {"ros1_runtime_ready", "blocked_missing_ros1_runtime"}:
                raise AssertionError(manifest["status"])
            dataset_path = ROOT / manifest["generated_outputs"]["fastlio_replay_dataset_jsonl"]
            if not dataset_path.exists():
                dataset_path = output_root / manifest["generated_outputs"]["fastlio_replay_dataset_jsonl"].split("/")[-1]
            frames = [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line]
            if not frames or frames[0]["schema"] != "mosim.fastlio_replay_frame.v1":
                raise AssertionError(dataset_path)
            if not frames[0]["points_lidar_m"]:
                raise AssertionError(frames[0])
            if frames[0]["synthetic_imu"]["is_measured_imu"]:
                raise AssertionError(frames[0])

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Scripts" / "UE5" / "publish_fastlio_replay_ros1.py"),
                    "--dataset",
                    str(dataset_path),
                    "--dry-run",
                    "--max-frames",
                    "2",
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            dryrun = json.loads(result.stdout)
            if dryrun["claim"] != "dry-run only; no ROS messages were published":
                raise AssertionError(dryrun)
            if dryrun["frames"] != 2 or dryrun["points"] <= 0:
                raise AssertionError(dryrun)

        status_text = (output_root / "FASTLIO_REPLAY_STATUS.md").read_text(encoding="utf-8")
        if "not a FAST-LIO localization result" not in status_text:
            raise AssertionError(status_text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_fastlio_replay_adapter_outputs()
    print("[OK] FAST-LIO replay adapter regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
