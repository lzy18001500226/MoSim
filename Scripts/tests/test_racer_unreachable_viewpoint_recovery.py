from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_racer_patch_has_bounded_fallback_and_backoff() -> None:
    source = (ROOT / "sunray" / "patch_racer_unreachable_viewpoint_recovery.py").read_text(
        encoding="utf-8"
    )
    assert "[RACER_UNREACHABLE_RETRY]" in source
    assert "[RACER_UNREACHABLE_SELECT]" in source
    assert "[RACER_ALL_FRONTIER_FALLBACK]" in source
    assert "const int attempt_limit = 8" in source
    assert "const ros::Duration duration(8.0)" in source
    assert "ed_->n_points_" in source
    assert "frontier_ids" in source
    assert "sdf_map_->getRegion" in source


def test_racer_wrapper_applies_and_builds_patch_before_runtime() -> None:
    source = (ROOT / "sunray" / "run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")
    assert "prepare_racer_planner_workspace" in source
    assert "patch_racer_unreachable_viewpoint_recovery.py" in source
    assert 'cmake --build "${RACER_WS}/build" --target exploration_node -- -j2' in source
    assert "catkin_make --only-pkg-with-deps exploration_manager" in source
    assert source.index("prepare_racer_planner_workspace\n") < source.index(
        "prepare_racer_fastlio_workspace\n"
    )
