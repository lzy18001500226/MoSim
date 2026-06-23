#!/usr/bin/env python3
"""Tests for the Sunray runtime-tier refactor inventory."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_tier_refactor_audit() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "Scripts" / "quality" / "audit_runtime_tier_refactor.py")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    by_id = {item["id"]: item for item in payload["inventory"]}

    required = {
        "px4ctrl_core_cpp",
        "px4ctrl_core_c_abi",
        "fastlio_odom_alignment_adapter",
        "fastlio_frame_transform_cpp_math",
        "px4_external_odometry_publisher",
        "trajectory_reference_server",
        "pointcloud_to_world_bridge",
        "position_cmd_safety_adapter",
    }
    missing = sorted(required - set(by_id))
    if missing:
        raise AssertionError({"missing_inventory_ids": missing, "payload": payload})

    if by_id["px4ctrl_core_cpp"]["status"] != "ready":
        raise AssertionError(by_id["px4ctrl_core_cpp"])
    if by_id["px4ctrl_core_c_abi"]["status"] != "ready":
        raise AssertionError(by_id["px4ctrl_core_c_abi"])
    if by_id["fastlio_frame_transform_cpp_math"]["status"] != "ready":
        raise AssertionError(by_id["fastlio_frame_transform_cpp_math"])
    if by_id["px4_external_odometry_publisher"]["status"] != "ready":
        raise AssertionError(by_id["px4_external_odometry_publisher"])

    expected_debt = {
        "fastlio_odom_alignment_adapter",
        "trajectory_reference_server",
        "pointcloud_to_world_bridge",
        "position_cmd_safety_adapter",
    }
    debt = set(payload["prototype_debt"])
    if not expected_debt.issubset(debt):
        raise AssertionError({"expected_debt": sorted(expected_debt), "actual_debt": sorted(debt)})

    if not any("Static inventory only" in item for item in payload["claim_boundary"]):
        raise AssertionError(payload)


if __name__ == "__main__":
    test_runtime_tier_refactor_audit()
    print("[OK] runtime tier refactor audit")
