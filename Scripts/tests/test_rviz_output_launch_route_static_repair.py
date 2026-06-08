#!/usr/bin/env python3
"""Static checks for the 069 RViz output launch route repair."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FASTLIO_WRAPPER = ROOT / "Scripts" / "UE5" / "run_fastlio_rviz_replay_ros2.sh"
REPLAY_WRAPPER = ROOT / "Scripts" / "UE5" / "run_mosim_scene_replay_launch_ros2.sh"
RVIZ = ROOT / "Config" / "rviz2" / "mosim_uav_fastlio_camera_init_output_only.rviz"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_fastlio_wrapper_exports_explicit_rviz_config_route() -> None:
    text = FASTLIO_WRAPPER.read_text(encoding="utf-8")
    required = [
        "DRY_RUN=\"${DRY_RUN:-1}\"",
        "ALLOW_LIVE_OBSERVATION",
        "RVIZ_CONFIG=\"${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_fastlio_camera_init_output_only.rviz}\"",
        "RVIZ_ROUTE_MODE=\"${RVIZ_ROUTE_MODE:-explicit_rviz_config_pass_through}\"",
        "rviz_route_mode",
        "launch_profile_gap_resolved",
        "launch_route_repair",
        "export RVIZ_CONFIG RVIZ_ROUTE_MODE RVIZ_PROFILE START_RVIZ START_FASTLIO",
        "exec bash \"${RUNNER}\" \"${SCENE_ID}\"",
    ]
    for phrase in required:
        require(phrase in text, f"missing FAST-LIO wrapper route phrase: {phrase}")

    dry_run_block = text.split('if [[ "${DRY_RUN}" == "1" ]]; then', 1)[1].split("fi", 1)[0]
    for phrase in ["source ", "ros2 ", "rviz2 -d", "colcon "]:
        require(phrase not in dry_run_block, f"FAST-LIO wrapper dry-run must not contain {phrase!r}")


def test_replay_wrapper_explicit_config_bypasses_old_profile_rviz() -> None:
    text = REPLAY_WRAPPER.read_text(encoding="utf-8")
    required = [
        "RVIZ_CONFIG=\"${RVIZ_CONFIG:-}\"",
        "EXPLICIT_RVIZ_CONFIG",
        "EXPLICIT_RVIZ_ROUTE",
        "LAUNCH_START_RVIZ_ARG=\"false\"",
        "start_rviz:=${LAUNCH_START_RVIZ_ARG}",
        "explicit_rviz_route",
        "rviz_config_exists",
        "rviz2 -d \"${EXPLICIT_RVIZ_CONFIG}\" &",
        "cleanup_explicit_rviz",
    ]
    for phrase in required:
        require(phrase in text, f"missing replay wrapper explicit config phrase: {phrase}")

    require(
        '"start_rviz:=${START_RVIZ_ARG}"' not in text,
        "old launch profile RViz path must not receive START_RVIZ_ARG directly",
    )

    broad_process_terms = ["MWORKS", "Sysplorer", "Syslab", "MCP wrapper", "Codex", "browser"]
    for term in broad_process_terms:
        require(term not in text, f"replay wrapper must not add broad process cleanup term: {term}")


def test_output_only_rviz_config_contract() -> None:
    text = RVIZ.read_text(encoding="utf-8")
    required = [
        "Fixed Frame: camera_init",
        "Target Frame: camera_init",
        "Class: rviz_default_plugins/TF",
        "Value: /cloud_registered",
        "Value: /Odometry",
        "Value: /path",
        "FAST-LIO Output Only",
    ]
    for phrase in required:
        require(phrase in text, f"missing output-only RViz phrase: {phrase}")

    forbidden = [
        "/velodyne_points",
        "/mosim/lidar_points",
        "/mosim/livox/lidar",
        "/clicked_point",
        "PublishPoint",
        "/position_cmd",
        "/mosim/planner/position_cmd",
        "/planning/bspline",
    ]
    for phrase in forbidden:
        require(phrase not in text, f"output-only RViz config must not reference {phrase}")


def main() -> int:
    test_fastlio_wrapper_exports_explicit_rviz_config_route()
    test_replay_wrapper_explicit_config_bypasses_old_profile_rviz()
    test_output_only_rviz_config_contract()
    print("[OK] 069 RViz output launch route static repair checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
