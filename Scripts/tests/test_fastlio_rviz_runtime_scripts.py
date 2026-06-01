#!/usr/bin/env python3
"""Regression checks for native FAST-LIO/RViz runtime wrappers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = None
    if env:
        import os

        merged_env = os.environ.copy()
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=ROOT,
        env=merged_env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_fastlio_rviz_replay_wrapper_dry_run() -> None:
    for scene_id in ("factoryenvironmentcollect", "derelictcorridormegascans"):
        result = run(
            [
                "bash",
                "Scripts/UE5/run_fastlio_rviz_replay_ros1.sh",
                scene_id,
            ],
            env={"DRY_RUN": "1", "MAX_FRAMES": "2", "LOOP": "0", "START_RVIZ": "0"},
        )
        if "mosim.fastlio_ros1_publish_dryrun.v1" not in result.stdout:
            raise AssertionError(result.stdout)
        if "mosim.ros1_mapping_replay_dryrun.v1" not in result.stdout:
            raise AssertionError(result.stdout)
        if "browser" in result.stdout.lower() or "html" in result.stdout.lower():
            raise AssertionError(result.stdout)


def test_fastlio_topic_checker_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/check_fastlio_ros1_topics.sh"],
        env={"DRY_RUN": "1"},
    )
    payload = json.loads(result.stdout)
    required = set(payload["required_topics"])
    for topic in ("/velodyne_points", "/imu/data", "/cloud_registered", "/Odometry"):
        if topic not in required:
            raise AssertionError(payload)


def test_fastlio_workspace_bootstrap_dry_run_contract() -> None:
    result = run(
        ["bash", "Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh"],
        env={"DRY_RUN": "1", "BUILD": "0"},
    )
    payload = json.loads(result.stdout)
    if payload.get("schema") != "mosim.fastlio_ros1_workspace_bootstrap_dryrun.v1":
        raise AssertionError(payload)
    if "Results/tmp/fastlio_ros1_ws" not in payload.get("catkin_ws", ""):
        raise AssertionError(payload)
    if "no workspace files were created" not in payload.get("claim", ""):
        raise AssertionError(payload)


def main() -> int:
    test_fastlio_rviz_replay_wrapper_dry_run()
    test_fastlio_topic_checker_dry_run_contract()
    test_fastlio_workspace_bootstrap_dry_run_contract()
    print("[OK] FAST-LIO/RViz runtime script regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
