from pathlib import Path


MISSION_NODE = (
    Path(__file__).resolve().parents[1]
    / "sunray"
    / "px4ctrl_ego_single_mission_node.py"
)


def test_interactive_review_does_not_reclaim_released_position_command_publisher() -> None:
    source = MISSION_NODE.read_text(encoding="utf-8")
    start = source.index("if self.args.interactive_goal_review:")
    end = source.index('        self.phase = "ego_triggered"', start)
    review = source[start:end]

    ownership_guard = "mission_owns_position_command = not self.hover_cmd_publisher_released"
    assert ownership_guard in review
    assert review.index(ownership_guard) < review.index("if self.last_forwarded_goal is None")
    assert "if mission_owns_position_command:" in review
