#!/usr/bin/env python3
"""Regression checks for ROS/RViz/FAST-LIO runtime environment preflight."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "check_ros_mapping_runtime_env.py"
    spec = importlib.util.spec_from_file_location("check_ros_mapping_runtime_env", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_ros_mapping_runtime_env"] = module
    spec.loader.exec_module(module)
    return module


def test_env_report_contract() -> None:
    module = load_module()
    args = type(
        "Args",
        (),
        {
            "fast_lio_package": "fast_lio",
        },
    )()
    report = module.build_report(args)
    if report["schema"] != "mosim.ros_mapping_runtime_env.v1":
        raise AssertionError(report)
    if "HTML is not an accepted active point-cloud/map review window." not in report["claim_boundary"]:
        raise AssertionError(report)
    if "fast_lio" not in report["packages"]:
        raise AssertionError(report)
    if "rviz_config" not in report["project_assets"]:
        raise AssertionError(report)

    temp_root = ROOT / "Results" / "tmp" / "ros_mapping_runtime_env_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        md_path = temp_root / "ROS_MAPPING_RUNTIME_ENV.md"
        module.write_markdown(md_path, report)
        text = md_path.read_text(encoding="utf-8")
        for phrase in (
            "ready_for_native_mapping_runtime",
            "Recommended setup sequence",
            "Claim boundary",
            "HTML is not an accepted active point-cloud/map review window",
        ):
            if phrase not in text:
                raise AssertionError(text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_env_report_contract()
    print("[OK] ROS mapping runtime environment regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
