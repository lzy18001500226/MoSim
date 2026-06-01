#!/usr/bin/env python3
"""Regression checks for FAST-LIO runtime recording/evaluation tooling."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_fake_odometry(truth_path: Path, output_path: Path, offset: float = 0.0) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with truth_path.open(encoding="utf-8") as source, output_path.open("w", encoding="utf-8", newline="\n") as target:
        for index, line in enumerate(source):
            if index >= 6:
                break
            frame = json.loads(line)
            position = [float(value) + offset for value in frame["pose_world_m"]]
            payload = {
                "schema": "mosim.fastlio_odometry_sample.v1",
                "seq": index,
                "time": frame["time"],
                "frame_id": frame["world_frame_id"],
                "child_frame_id": frame["body_frame_id"],
                "position_m": position,
                "yaw_rad": frame["rpy_rad"][2],
            }
            target.write(json.dumps(payload, separators=(",", ":")) + "\n")


def test_runtime_evaluator_pass_and_fail() -> None:
    scene_pipeline = load_module("scene_truth_pipeline", "Scripts/UE5/scene_truth_pipeline.py")
    prepare = load_module("prepare_fastlio_replay", "Scripts/UE5/prepare_fastlio_replay.py")
    evaluator = load_module("evaluate_fastlio_runtime", "Scripts/UE5/evaluate_fastlio_runtime.py")
    temp_root = ROOT / "Results" / "tmp" / "fastlio_runtime_evaluation_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        scene_id = "factoryenvironmentcollect"
        truth_path = scene_pipeline.scene_truth_path(scene_id)
        truth = scene_pipeline.load_truth(truth_path)
        profile = scene_pipeline.default_profile(str(truth["scene_id"]), truth_path)
        scene_pipeline.run_scene(profile, output_root)
        manifest = prepare.prepare_scene(output_root / scene_id)
        dataset = output_root / scene_id / Path(manifest["generated_outputs"]["fastlio_replay_dataset_jsonl"]).name

        good_odom = output_root / scene_id / "fastlio_runtime" / "good_odom.jsonl"
        write_fake_odometry(dataset, good_odom, offset=0.0)
        args = type(
            "Args",
            (),
            {
                "scene_id": scene_id,
                "truth_dataset": dataset,
                "odometry_jsonl": good_odom,
                "align_start_time": True,
                "max_time_delta": 0.2,
                "max_position_rmse": 0.05,
                "max_position_error": 0.1,
                "max_samples_reported": 10,
            },
        )()
        good = evaluator.evaluate(args)
        if good["status"] != "pass" or good["metrics"]["aligned_samples"] <= 0:
            raise AssertionError(good)

        bad_odom = output_root / scene_id / "fastlio_runtime" / "bad_odom.jsonl"
        write_fake_odometry(dataset, bad_odom, offset=5.0)
        args.odometry_jsonl = bad_odom
        bad = evaluator.evaluate(args)
        if bad["status"] != "failed_error_threshold":
            raise AssertionError(bad)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_runtime_recorder_dry_run_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "Scripts/UE5/record_fastlio_ros1_runtime.py",
            "--scene-id",
            "factoryenvironmentcollect",
            "--output-dir",
            "Results/tmp/fastlio_runtime_recorder_dryrun",
            "--dry-run",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    if payload["schema"] != "mosim.fastlio_runtime_record_dryrun.v1":
        raise AssertionError(payload)
    if "no ROS topics" not in payload["claim"]:
        raise AssertionError(payload)


def main() -> int:
    test_runtime_evaluator_pass_and_fail()
    test_runtime_recorder_dry_run_contract()
    print("[OK] FAST-LIO runtime evaluation regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
