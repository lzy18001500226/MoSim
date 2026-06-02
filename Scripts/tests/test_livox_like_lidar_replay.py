#!/usr/bin/env python3
"""Regression checks for Livox-like dense LiDAR replay generation."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_livox_like_lidar_replay_contract() -> None:
    temp_root = ROOT / "Results" / "tmp" / "livox_like_lidar_replay_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts" / "UE5" / "generate_livox_like_lidar_replay.py"),
                "--scene",
                "factoryenvironmentcollect",
                "--output-root",
                str(temp_root),
                "--max-frames",
                "1",
                "--points-per-frame",
                "2000",
                "--max-range-m",
                "35.0",
                "--raycast-step-m",
                "0.2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
        report = payload["reports"][0]
        if report["schema"] != "mosim.livox_like_lidar_replay_manifest.v1":
            raise AssertionError(report)
        if report["scene_id"] != "factoryenvironmentcollect":
            raise AssertionError(report)
        if report["frame_count"] != 1:
            raise AssertionError(report)
        if report["points_per_frame_avg"] < 1000:
            raise AssertionError(report)
        if "mid360-real-centr.csv" not in report["scan_mode_csv"]:
            raise AssertionError(report)
        jsonl_path = ROOT / report["output_jsonl"]
        if not jsonl_path.exists():
            jsonl_path = temp_root / "factoryenvironmentcollect" / "livox_like_lidar_frames.jsonl"
        frame = json.loads(jsonl_path.read_text(encoding="utf-8").splitlines()[0])
        if frame["schema"] != "mosim.livox_like_lidar_frame.v1":
            raise AssertionError(frame)
        if len(frame["points_m"]) != len(frame["point_attributes"]):
            raise AssertionError(frame)
        attrs = frame["point_attributes"][0]
        for key in ("offset_time_ns", "line", "reflectivity", "tag"):
            if key not in attrs:
                raise AssertionError(attrs)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_livox_like_lidar_replay_accepts_control_reference_pose_csv() -> None:
    temp_root = ROOT / "Results" / "tmp" / "livox_like_lidar_replay_ref_pose_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts" / "UE5" / "generate_livox_like_lidar_replay.py"),
                "--scene",
                "factoryenvironmentcollect",
                "--output-root",
                str(temp_root),
                "--pose-csv",
                str(ROOT / "Results/unreal_scene_mapping/factoryenvironmentcollect/control_reference.csv"),
                "--max-frames",
                "2",
                "--points-per-frame",
                "1000",
                "--max-range-m",
                "35.0",
                "--raycast-step-m",
                "0.25",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
        report = payload["reports"][0]
        if report["frame_count"] != 2:
            raise AssertionError(report)
        jsonl_path = temp_root / "factoryenvironmentcollect" / "livox_like_lidar_frames.jsonl"
        frames = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
        if frames[1]["time"] != 0.05:
            raise AssertionError(frames)
        if "control_reference.csv" not in report["pose_csv"]:
            raise AssertionError(report)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_livox_like_lidar_replay_can_emit_body_frame_truth_dataset() -> None:
    temp_root = ROOT / "Results" / "tmp" / "livox_like_lidar_replay_body_pose_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts" / "UE5" / "generate_livox_like_lidar_replay.py"),
                "--scene",
                "factoryenvironmentcollect",
                "--output-root",
                str(temp_root),
                "--pose-csv",
                str(ROOT / "Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv"),
                "--pose-stride",
                "2",
                "--pose-start-index",
                "1",
                "--max-frames",
                "2",
                "--points-per-frame",
                "1000",
                "--points-frame",
                "body",
                "--truth-dataset-name",
                "truth.jsonl",
                "--max-range-m",
                "35.0",
                "--raycast-step-m",
                "0.25",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
        report = payload["reports"][0]
        if report["points_frame"] != "body" or report["pose_stride"] != 2:
            raise AssertionError(report)
        if report["pose_start_index"] != 1:
            raise AssertionError(report)
        if not report["truth_dataset_jsonl"]:
            raise AssertionError(report)
        jsonl_path = temp_root / "factoryenvironmentcollect" / "livox_like_lidar_frames.jsonl"
        frames = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
        if frames[0]["coordinate_frame"] != "body_lidar_m_z_up":
            raise AssertionError(frames[0])
        truth_path = temp_root / "factoryenvironmentcollect" / "truth.jsonl"
        truth = [json.loads(line) for line in truth_path.read_text(encoding="utf-8").splitlines()]
        if truth[0]["schema"] != "mosim.fastlio_replay_frame.v1":
            raise AssertionError(truth[0])
        if truth[0]["time"] != 0.05 or truth[1]["time"] != 0.15:
            raise AssertionError(truth)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_livox_like_lidar_replay_contract()
    test_livox_like_lidar_replay_accepts_control_reference_pose_csv()
    test_livox_like_lidar_replay_can_emit_body_frame_truth_dataset()
    print("[OK] Livox-like LiDAR replay regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
