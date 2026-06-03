#!/usr/bin/env python3
"""Regression checks for MoSim FAST-LIO runtime candidate ranking."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "check_fastlio_runtime_candidates.py"
    spec = importlib.util.spec_from_file_location("check_fastlio_runtime_candidates", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_fastlio_runtime_candidates"] = module
    spec.loader.exec_module(module)
    return module


def test_runtime_candidate_decision_contract() -> None:
    module = load_module()
    report = module.build_report(list(module.DEFAULT_CANDIDATES))
    if report["schema"] != "mosim.fastlio_runtime_candidates.v1":
        raise AssertionError(report["schema"])
    if report["preferred_ros2_mid360_count"] != 0:
        raise AssertionError(report)
    if report["patchable_ros2_livox_count"] < 1:
        raise AssertionError(report)
    if report["strong_ros1_mid360_reference_count"] < 1:
        raise AssertionError(report)
    if report["external_candidate_count"] < 1:
        raise AssertionError(report)
    if report["decision"] != "evaluate_external_ros2_mid360_fastlio_candidate_first":
        raise AssertionError(report["decision"])
    external = report["external_candidates"][0]
    if external["name"] != "Ericsii/FAST_LIO_ROS2":
        raise AssertionError(external)
    if "not_yet_built_in_mosim_workspace" not in external["blockers"]:
        raise AssertionError(external)

    by_path = {item["path"]: item for item in report["ranked_candidates"]}
    spark = by_path["Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio"]
    if spark["role"] != "ros2_candidate_needs_patch":
        raise AssertionError(spark)
    if "pointcloud2_path_rejects_livox_lidar_type" not in spark["blockers"]:
        raise AssertionError(spark)
    if not spark["support"]["livox_ros_driver2_custom_msg"]:
        raise AssertionError(spark)

    fast_lio = by_path["References/Lab/FAST_LIO"]
    if fast_lio["role"] != "strong_ros1_mid360_reference":
        raise AssertionError(fast_lio)
    if not fast_lio["support"]["livox_ros_driver_custom_msg"]:
        raise AssertionError(fast_lio)
    if not fast_lio["support"]["mid360_markers"]:
        raise AssertionError(fast_lio)

    sunray_sensor = by_path["References/Sunray/simulation/gazebo_plugin/livox_laser_simulation"]
    if sunray_sensor["role"] != "sensor_semantics_reference":
        raise AssertionError(sunray_sensor)
    if not sunray_sensor["support"]["local_livox_custom_msg"]:
        raise AssertionError(sunray_sensor)
    if not sunray_sensor["support"]["sunray_scan_csv"]:
        raise AssertionError(sunray_sensor)

    mosim_transport = by_path["Scripts/ros/mosim_dense_lidar_cpp"]
    if mosim_transport["role"] != "mosim_transport_probe":
        raise AssertionError(mosim_transport)

    temp_root = ROOT / "Results" / "tmp" / "fastlio_runtime_candidates_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        md_path = temp_root / "FASTLIO_RUNTIME_CANDIDATES.md"
        module.write_markdown(md_path, report)
        text = md_path.read_text(encoding="utf-8")
        for phrase in (
            "evaluate_external_ros2_mid360_fastlio_candidate_first",
            "Ericsii/FAST_LIO_ROS2",
            "ros2_candidate_needs_patch",
            "strong_ros1_mid360_reference",
            "Velodyne/Ouster PointCloud2 smoke does not satisfy",
        ):
            if phrase not in text:
                raise AssertionError(text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_runtime_candidate_decision_contract()
    print("[OK] FAST-LIO runtime candidate regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
