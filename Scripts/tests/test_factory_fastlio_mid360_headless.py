#!/usr/bin/env python3
"""Regression checks for the Factory Mid360 FAST-LIO headless gate."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "UE5" / "run_factory_fastlio_mid360_headless_ros2.sh"
PROBE = ROOT / "Scripts" / "UE5" / "probe_livox_custommsg_ros2.py"


def test_headless_script_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for required in (
        "record_fastlio_ros2_runtime.py",
        "evaluate_fastlio_runtime.py",
        "rviz:=false",
        "mosim_fast_lio_ros2_mid360.yaml",
        "LIVOX_UNDERLAY_SETUP",
        "livox_ros_driver2/share/livox_ros_driver2/local_setup.bash",
        "fast_lio/share/fast_lio/local_setup.bash",
        "mosim_dense_lidar_cpp/share/mosim_dense_lidar_cpp/local_setup.bash",
        "/mosim/livox/lidar",
        "/mosim/forward/imu",
        "dense_lidar_replay_node",
        "mworks_state_imu_replay_node",
        "livox_imu_probe_node",
        "IMU_RATE_HZ=\"${IMU_RATE_HZ:-200.0}\"",
        "probe_cpp.stdout.json",
        "LIVOX_CUSTOMMSG_PROBE.json",
        "FIRST_MESSAGE_TIMEOUT_SECONDS",
        "MIN_LIVOX_POINTS",
        'MWORKS_RAW="${MWORKS_RAW:-',
        'LIVOX_FRAMES="${LIVOX_FRAMES:-',
        'TRUTH_DATASET="${TRUTH_DATASET:-',
        "wait_for_topic_once /mosim/livox/lidar livox_ros_driver2/msg/CustomMsg first_livox_message",
        "wait_for_topic_once /mosim/forward/imu sensor_msgs/msg/Imu first_imu_message",
    ):
        if required not in text:
            raise AssertionError(f"missing headless contract marker: {required}")
    if "rviz2 " in text or "START_RVIZ" in text:
        raise AssertionError("headless gate must not open RViz")
    if text.index('source "${DENSE_LIDAR_SETUP}"') < text.index('source "${FASTLIO_IMPORT_SETUP}"'):
        raise AssertionError("MoSim dense LiDAR overlay must be sourced after FAST-LIO underlay")


def test_headless_dry_run() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        env={"DRY_RUN": "1"},
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)
    if payload["schema"] != "mosim.factory_fastlio_mid360_headless_dryrun.v1":
        raise AssertionError(payload)
    for phase in ("livox_input_probe", "fast_lio", "runtime_record", "truth_evaluation"):
        if phase not in payload["phases"]:
            raise AssertionError(payload)


def test_livox_probe_dry_run() -> None:
    result = subprocess.run(
        ["python3", str(PROBE), "--dry-run"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)
    if payload["schema"] != "mosim.livox_custommsg_probe_dryrun.v1":
        raise AssertionError(payload)
    if payload["topics"]["livox"] != "/mosim/livox/lidar":
        raise AssertionError(payload)
    if payload["topics"]["imu"] != "/mosim/forward/imu":
        raise AssertionError(payload)


def main() -> int:
    test_headless_script_contract()
    test_headless_dry_run()
    test_livox_probe_dry_run()
    print("[OK] Factory Mid360 FAST-LIO headless gate regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
