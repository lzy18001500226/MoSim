#!/usr/bin/env python3
"""Regression checks for local FAST-LIO-family ROS compatibility detection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "check_fastlio_family_compatibility.py"
    spec = importlib.util.spec_from_file_location("check_fastlio_family_compatibility", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_fastlio_family_compatibility"] = module
    spec.loader.exec_module(module)
    return module


def test_fastlio_family_report_contract() -> None:
    module = load_module()
    report = module.build_report(list(module.DEFAULT_CANDIDATES))
    if report["schema"] != "mosim.fastlio_family_compatibility.v1":
        raise AssertionError(report)
    if report["can_claim_fastlio_ros2_runtime"]:
        raise AssertionError(report)
    if report["ros1_catkin_only_count"] < 3:
        raise AssertionError(report)
    if report["ros2_candidate_count"] != 0:
        raise AssertionError(report)
    if "no_local_ros2_fastlio_family_source" not in report["degradation"]:
        raise AssertionError(report)

    by_path = {item["path"]: item for item in report["candidates"]}
    fast_lio = by_path["References/Lab/FAST_LIO"]
    if fast_lio["verdict"] != "ros1_catkin_only":
        raise AssertionError(fast_lio)
    for marker in ("has_catkin", "has_ros1_launch_xml"):
        if not fast_lio["markers"][marker]:
            raise AssertionError(fast_lio)
    for topic in ("/cloud_registered", "/Odometry"):
        if topic not in fast_lio["topics_found"]:
            raise AssertionError(fast_lio)

    temp_root = ROOT / "Results" / "tmp" / "fastlio_family_compatibility_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        md_path = temp_root / "FASTLIO_FAMILY_COMPATIBILITY.md"
        module.write_markdown(md_path, report)
        text = md_path.read_text(encoding="utf-8")
        for phrase in (
            "can_claim_fastlio_ros2_runtime",
            "ros1_catkin_only",
            "no_local_ros2_fastlio_family_source",
            "FAST-LIO localization remains unclaimed",
        ):
            if phrase not in text:
                raise AssertionError(text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_fastlio_family_report_contract()
    print("[OK] FAST-LIO-family compatibility regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
