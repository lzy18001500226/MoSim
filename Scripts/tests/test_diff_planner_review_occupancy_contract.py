from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh"
GRID_CONFIG = ROOT / "Config" / "rviz" / "sunray_ros1_goal4_diff_grid3d_review.rviz"
POINTCLOUD_CONFIG = ROOT / "Config" / "rviz" / "sunray_ros1_goal4_diff_pointcloud_review.rviz"
CONTINUOUS_NODE = ROOT / "Scripts" / "ros" / "continuous_occupancy_review.py"


def _block(text: str, topic: str) -> str:
    blocks = text.split("    - ")[1:]
    for block in blocks:
        if f"Topic: {topic}\n" in block or block.endswith(f"Topic: {topic}"):
            return block
    raise AssertionError(f"missing RViz display for {topic}")


def test_diff_planner_uses_a_dedicated_continuous_review_default() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    node = CONTINUOUS_NODE.read_text(encoding="utf-8")

    assert 'DIFF_ENABLE_CONTINUOUS_OCCUPANCY_REVIEW="${DIFF_ENABLE_CONTINUOUS_OCCUPANCY_REVIEW:-true}"' in runner
    assert 'ENABLE_CONTINUOUS_OCCUPANCY_REVIEW="${DIFF_ENABLE_CONTINUOUS_OCCUPANCY_REVIEW}"' in runner
    assert 'continuous_occupancy_review.py' in runner
    assert '--input-topic "${CONTINUOUS_OCCUPANCY_REVIEW_SOURCE_TOPIC}"' in runner
    assert '--output-topic "${CONTINUOUS_OCCUPANCY_REVIEW_TOPIC}"' in runner
    assert 'default="/mosim/goal4/livox_world_accumulated"' in node
    assert 'default="/mosim/goal4/occupancy_object_review"' in node
    assert '"scope": "review_only_not_planner_input"' in node


def test_goal4_grid_defaults_to_continuous_map_and_keeps_planner_empty_maps_diagnostic() -> None:
    config = GRID_CONFIG.read_text(encoding="utf-8")
    continuous = _block(config, "/mosim/goal4/occupancy_object_review")
    raw = _block(config, "/drone_0_ego_planner_node/grid_map/occupancy")
    accumulated = _block(config, "/mosim/goal4/occupancy_accumulated")
    inflated = _block(config, "/drone_0_ego_planner_node/grid_map/occupancy_inflate")

    assert "Enabled: true" in continuous
    assert "Value: true" in continuous
    assert "Style: Boxes" in continuous
    for diagnostic in (raw, accumulated, inflated):
        assert "Enabled: false" in diagnostic
        assert "Value: false" in diagnostic


def test_goal4_review_views_follow_the_uav_local_frame() -> None:
    for config in (POINTCLOUD_CONFIG, GRID_CONFIG):
        text = config.read_text(encoding="utf-8")

        assert "Fixed Frame: world" in text
        assert "Target Frame: uav1/base_link" in text
