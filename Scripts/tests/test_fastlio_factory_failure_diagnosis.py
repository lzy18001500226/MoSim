#!/usr/bin/env python3
"""Regression checks for the Factory FAST-LIO failure diagnosis report."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "diagnose_fastlio_factory_failure.py"
    spec = importlib.util.spec_from_file_location("diagnose_fastlio_factory_failure", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["diagnose_fastlio_factory_failure"] = module
    spec.loader.exec_module(module)
    return module


def test_factory_diagnosis_contract() -> None:
    module = load_module()
    args = type(
        "Args",
        (),
        {
            "scene_dir": ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect",
            "config": ROOT / "Config" / "ros2" / "mosim_spark_fast_lio_velodyne.yaml",
            "runtime_dirs": ["fastlio_runtime", "fastlio_runtime_scan099"],
        },
    )()
    report = module.diagnose(args)
    if report["schema"] != "mosim.fastlio_factory_failure_diagnosis.v1":
        raise AssertionError(report["schema"])
    if report["status"] != "not_claimable":
        raise AssertionError(report["status"])
    if report["fastlio_config"]["lidar_type"] != 2:
        raise AssertionError(report["fastlio_config"])
    if report["fastlio_config"]["scan_line"] != 16:
        raise AssertionError(report["fastlio_config"])
    if report["truth_lidar_and_imu"]["points_per_frame_avg"] >= 1000:
        raise AssertionError(report["truth_lidar_and_imu"])
    if report["truth_lidar_and_imu"]["synthetic_imu_frames"] <= 0:
        raise AssertionError(report["truth_lidar_and_imu"])
    if not report["truth_motion"]["fixed_yaw"]:
        raise AssertionError(report["truth_motion"])

    surfaces = {item["surface"] for item in report["findings"]}
    required = {
        "FAST-LIO sensor model",
        "FAST-LIO scan lines",
        "IMU source",
        "LiDAR density",
        "Per-point timing",
        "Motion excitation",
        "Runtime quality: fastlio_runtime",
        "Runtime quality: fastlio_runtime_scan099",
    }
    missing = required - surfaces
    if missing:
        raise AssertionError(sorted(missing))
    runtime_statuses = {item["name"]: item["status"] for item in report["runtime_summaries"]}
    if set(runtime_statuses.values()) != {"failed_error_threshold"}:
        raise AssertionError(runtime_statuses)


def test_factory_diagnosis_writes_reports() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "fastlio_factory_failure_diagnosis_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    temp_root.mkdir(parents=True)
    try:
        args = type(
            "Args",
            (),
            {
                "scene_dir": ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect",
                "config": ROOT / "Config" / "ros2" / "mosim_spark_fast_lio_velodyne.yaml",
                "runtime_dirs": ["fastlio_runtime"],
            },
        )()
        report = module.diagnose(args)
        output_json = temp_root / "diagnosis.json"
        output_md = temp_root / "diagnosis.md"
        output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        module.write_markdown(output_md, report)
        loaded = json.loads(output_json.read_text(encoding="utf-8"))
        text = output_md.read_text(encoding="utf-8")
        if loaded["status"] != "not_claimable":
            raise AssertionError(loaded)
        for phrase in ("not blocked by topic plumbing", "lidar_type", "Runtime quality"):
            if phrase not in text:
                raise AssertionError(text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_factory_diagnosis_contract()
    test_factory_diagnosis_writes_reports()
    print("[OK] FAST-LIO Factory failure diagnosis regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
