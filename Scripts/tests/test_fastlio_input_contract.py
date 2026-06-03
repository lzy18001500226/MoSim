#!/usr/bin/env python3
"""Regression checks for MoSim Mid360 FAST-LIO input contracts."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "check_fastlio_input_contract.py"
    spec = importlib.util.spec_from_file_location("check_fastlio_input_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_fastlio_input_contract"] = module
    spec.loader.exec_module(module)
    return module


def test_mid360_config_contract_uses_dense_livox_runtime_path() -> None:
    module = load_module()
    args = type(
        "Args",
        (),
        {
            "scene_dir": ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect",
            "config": ROOT / "Config" / "ros2" / "mosim_spark_fast_lio_mid360.yaml",
            "manifest": "",
            "livox_frames": "",
            "fastlio_dataset": "",
            "sample_frames": 5,
            "min_dense_points": 15000,
            "min_fastlio_points": 15000,
            "spark_fastlio_root": ROOT / "Results" / "tmp" / "fastlio_ros2_candidates" / "spark-fast-lio",
        },
    )()
    report = module.evaluate(args)
    if report["schema"] != "mosim.fastlio_input_contract.v1":
        raise AssertionError(report["schema"])
    if report["config"]["preprocess"]["lidar_type"] != 1:
        raise AssertionError(report["config"])
    if report["config"]["preprocess"]["scan_line"] != 4:
        raise AssertionError(report["config"])
    if not report["dense_lidar_ready"]:
        raise AssertionError(report)
    if report["status"] != "claimable_input_ready":
        raise AssertionError(report["status"])
    surfaces = {finding["surface"] for finding in report["findings"]}
    for required in ("legacy FAST-LIO dataset",):
        if required not in surfaces:
            raise AssertionError(report["findings"])
    support = report["implementation_support"]["spark_fast_lio"]
    if support["pointcloud2_livox_supported"]:
        raise AssertionError(support)
    if "VELO16" not in support["pointcloud2_supported_lidar_types"]:
        raise AssertionError(support)
    if not support["livox_ros2_custommsg_supported"]:
        raise AssertionError(support)
    if report["livox_frame_sample"]["points_per_frame_avg"] < 15000:
        raise AssertionError(report["livox_frame_sample"])
    if report["livox_frame_sample"]["observed_lines"] != [0, 1, 2, 3]:
        raise AssertionError(report["livox_frame_sample"])


def test_velodyne_config_remains_not_claimable_for_mid360() -> None:
    module = load_module()
    args = type(
        "Args",
        (),
        {
            "scene_dir": ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect",
            "config": ROOT / "Config" / "ros2" / "mosim_spark_fast_lio_velodyne.yaml",
            "manifest": "",
            "livox_frames": "",
            "fastlio_dataset": "",
            "sample_frames": 2,
            "min_dense_points": 15000,
            "min_fastlio_points": 15000,
            "spark_fastlio_root": ROOT / "Results" / "tmp" / "fastlio_ros2_candidates" / "spark-fast-lio",
        },
    )()
    report = module.evaluate(args)
    if report["status"] == "claimable_input_ready":
        raise AssertionError(report)
    surfaces = {finding["surface"] for finding in report["findings"]}
    if "FAST-LIO config" not in surfaces:
        raise AssertionError(report["findings"])


def main() -> int:
    test_mid360_config_contract_uses_dense_livox_runtime_path()
    test_velodyne_config_remains_not_claimable_for_mid360()
    print("[OK] FAST-LIO input contract regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
