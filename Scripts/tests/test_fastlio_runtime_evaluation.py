#!/usr/bin/env python3
"""Regression checks for FAST-LIO runtime recording/evaluation tooling."""

from __future__ import annotations

import importlib.util
import json
import math
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


def write_fake_odometry(
    truth_path: Path,
    output_path: Path,
    *,
    constant_offset: float = 0.0,
    odom_to_truth_yaw_offset_rad: float = 0.0,
    drift_per_sample: float = 0.0,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    with truth_path.open(encoding="utf-8") as source:
        for index, line in enumerate(source):
            if index >= 6:
                break
            frames.append(json.loads(line))
    first_position = [float(value) for value in frames[0]["pose_world_m"]]
    cos_yaw = math.cos(-odom_to_truth_yaw_offset_rad)
    sin_yaw = math.sin(-odom_to_truth_yaw_offset_rad)

    with output_path.open("w", encoding="utf-8", newline="\n") as target:
        for index, frame in enumerate(frames):
            world_position = [float(value) for value in frame["pose_world_m"]]
            delta = [world_position[axis] - first_position[axis] for axis in range(3)]
            local_delta = [
                delta[0] * cos_yaw - delta[1] * sin_yaw,
                delta[0] * sin_yaw + delta[1] * cos_yaw,
                delta[2],
            ]
            position = [
                first_position[axis] + constant_offset + local_delta[axis] + drift_per_sample * index
                for axis in range(3)
            ]
            payload = {
                "schema": "mosim.fastlio_odometry_sample.v1",
                "seq": index,
                "time": frame["time"],
                "frame_id": frame["world_frame_id"],
                "child_frame_id": frame["body_frame_id"],
                "position_m": position,
                "yaw_rad": float(frame["rpy_rad"][2]) - odom_to_truth_yaw_offset_rad,
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
        write_fake_odometry(dataset, good_odom, constant_offset=0.0)
        args = type(
            "Args",
            (),
            {
                "scene_id": scene_id,
                "truth_dataset": dataset,
                "odometry_jsonl": good_odom,
                "align_start_time": True,
                "align_start_position": True,
                "align_start_yaw": True,
                "max_time_delta": 0.2,
                "max_position_rmse": 0.05,
                "max_position_error": 0.1,
                "max_samples_reported": 10,
            },
        )()
        good = evaluator.evaluate(args)
        if good["status"] != "pass" or good["metrics"]["aligned_samples"] <= 0:
            raise AssertionError(good)
        if good["metrics"]["odometry_samples_after_time_sort"] <= 0:
            raise AssertionError(good)
        if good["odometry_time_quality"]["nonmonotonic_pairs"] != 0:
            raise AssertionError(good["odometry_time_quality"])

        offset_odom = output_root / scene_id / "fastlio_runtime" / "offset_odom.jsonl"
        write_fake_odometry(dataset, offset_odom, constant_offset=5.0)
        args.odometry_jsonl = offset_odom
        offset_good = evaluator.evaluate(args)
        if offset_good["status"] != "pass":
            raise AssertionError(offset_good)
        if offset_good["position_offset_m"] != [5.0, 5.0, 5.0]:
            raise AssertionError(offset_good)

        rotated_odom = output_root / scene_id / "fastlio_runtime" / "rotated_odom.jsonl"
        write_fake_odometry(
            dataset,
            rotated_odom,
            constant_offset=5.0,
            odom_to_truth_yaw_offset_rad=math.pi / 4.0,
        )
        args.odometry_jsonl = rotated_odom
        rotated_good = evaluator.evaluate(args)
        if rotated_good["status"] != "pass":
            raise AssertionError(rotated_good)
        if abs(rotated_good["yaw_offset_rad"] - math.pi / 4.0) > 1e-6:
            raise AssertionError(rotated_good)

        bad_odom = output_root / scene_id / "fastlio_runtime" / "bad_odom.jsonl"
        write_fake_odometry(dataset, bad_odom, constant_offset=0.0, drift_per_sample=1.0)
        args.odometry_jsonl = bad_odom
        bad = evaluator.evaluate(args)
        if bad["status"] != "failed_error_threshold":
            raise AssertionError(bad)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_runtime_evaluator_sorts_nonmonotonic_odometry() -> None:
    evaluator = load_module("evaluate_fastlio_runtime_sort", "Scripts/UE5/evaluate_fastlio_runtime.py")
    temp_root = ROOT / "Results" / "tmp" / "fastlio_runtime_evaluation_sort_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    temp_root.mkdir(parents=True)
    try:
        truth_path = temp_root / "truth.jsonl"
        odom_path = temp_root / "odom.jsonl"
        truth_rows = [
            {
                "schema": "mosim.fastlio_replay_frame.v1",
                "time": time_value,
                "pose_world_m": [float(index), 0.0, 0.0],
                "rpy_rad": [0.0, 0.0, 0.0],
            }
            for index, time_value in enumerate((0.0, 0.1, 0.2))
        ]
        odom_rows = [
            {
                "schema": "mosim.fastlio_odometry_sample.v1",
                "seq": 0,
                "time": 100.0,
                "position_m": [0.0, 0.0, 0.0],
                "yaw_rad": 0.0,
            },
            {
                "schema": "mosim.fastlio_odometry_sample.v1",
                "seq": 2,
                "time": 100.2,
                "position_m": [2.0, 0.0, 0.0],
                "yaw_rad": 0.0,
            },
            {
                "schema": "mosim.fastlio_odometry_sample.v1",
                "seq": 1,
                "time": 100.1,
                "position_m": [1.0, 0.0, 0.0],
                "yaw_rad": 0.0,
            },
        ]
        with truth_path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in truth_rows:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
        with odom_path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in odom_rows:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
        args = type(
            "Args",
            (),
            {
                "scene_id": "sort_test",
                "truth_dataset": truth_path,
                "odometry_jsonl": odom_path,
                "align_start_time": True,
                "align_start_position": True,
                "align_start_yaw": True,
                "max_time_delta": 0.2,
                "max_position_rmse": 0.05,
                "max_position_error": 0.1,
                "max_samples_reported": 10,
            },
        )()
        report = evaluator.evaluate(args)
        if report["status"] != "pass":
            raise AssertionError(report)
        if report["odometry_time_quality"]["nonmonotonic_pairs"] != 1:
            raise AssertionError(report["odometry_time_quality"])
        if report["metrics"]["odometry_samples_after_time_sort"] != 3:
            raise AssertionError(report["metrics"])
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_runtime_recorder_dry_run_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "Scripts/UE5/record_fastlio_ros2_runtime.py",
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
    if payload["schema"] != "mosim.fastlio_ros2_runtime_record_dryrun.v1":
        raise AssertionError(payload)
    if "no ROS2 topics" not in payload["claim"]:
        raise AssertionError(payload)


def main() -> int:
    test_runtime_evaluator_pass_and_fail()
    test_runtime_evaluator_sorts_nonmonotonic_odometry()
    test_runtime_recorder_dry_run_contract()
    print("[OK] FAST-LIO runtime evaluation regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
