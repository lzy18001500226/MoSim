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


def main() -> int:
    test_livox_like_lidar_replay_contract()
    print("[OK] Livox-like LiDAR replay regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
