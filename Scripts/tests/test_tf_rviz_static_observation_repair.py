#!/usr/bin/env python3
"""Static checks for the 067 TF/RViz observation-prep repair."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "UE5" / "run_fastlio_rviz_replay_ros2.sh"
RVIZ = ROOT / "Config" / "rviz2" / "mosim_uav_fastlio_camera_init_output_only.rviz"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_runner_static_contract() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    required_phrases = [
        "DRY_RUN=\"${DRY_RUN:-1}\"",
        "ALLOW_LIVE_OBSERVATION",
        "live_graph_started",
        "ros_setup_sourced",
        "ros2_command_executed",
        "FASTLIO_OUTPUT_FIXED_FRAME=\"${FASTLIO_OUTPUT_FIXED_FRAME:-camera_init}\"",
        "OBSERVE_TOPICS=\"${OBSERVE_TOPICS:-/tf,/cloud_registered,/Odometry,/path}\"",
        "TF_REQUIRED_EDGES",
        "RAW_LIDAR_DISPLAY_GAP",
        "launch_profile_gap",
        "/position_cmd",
        "/mosim/planner/position_cmd",
        "/planning/bspline",
        "no TF/RViz readiness claim",
        "no localization or local-map quality claim",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"missing runner phrase: {phrase}")

    dry_run_block = text.split('if [[ "${DRY_RUN}" == "1" ]]; then', 1)[1].split("fi", 1)[0]
    forbidden_in_dry_run = ["source ", "ros2 ", "rviz2", "FAST-LIO"]
    for phrase in forbidden_in_dry_run:
        require(phrase not in dry_run_block, f"dry-run block must not contain {phrase!r}")

    unsafe_process_terms = ["MWORKS", "Sysplorer", "Syslab", "MCP wrapper", "Codex", "browser", "mworks"]
    for term in unsafe_process_terms:
        require(term not in text, f"runner must not carry broad process term: {term}")


def test_rviz_output_only_camera_init_config() -> None:
    text = RVIZ.read_text(encoding="utf-8")
    required_phrases = [
        "Fixed Frame: camera_init",
        "Target Frame: camera_init",
        "Class: rviz_default_plugins/TF",
        "Value: /cloud_registered",
        "Value: /Odometry",
        "Value: /path",
        "FAST-LIO Output Only",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"missing rviz phrase: {phrase}")

    forbidden_topics = ["/velodyne_points", "/mosim/lidar_points", "/mosim/livox/lidar"]
    for topic in forbidden_topics:
        require(topic not in text, f"output-only rviz config must not reference raw LiDAR gap topic: {topic}")

    forbidden_tools = ["/clicked_point", "PublishPoint"]
    for phrase in forbidden_tools:
        require(phrase not in text, f"output-only rviz config must not expose publish tool: {phrase}")


def main() -> int:
    test_runner_static_contract()
    test_rviz_output_only_camera_init_config()
    print("[OK] 067 TF/RViz static observation repair checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
