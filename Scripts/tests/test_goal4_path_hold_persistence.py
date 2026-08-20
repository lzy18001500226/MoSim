from pathlib import Path


PATH_HOLD = Path("Scripts/sunray/goal4_path_hold_from_csv.py")


def test_goal4_path_hold_keeps_the_last_nonempty_path_during_source_gaps() -> None:
    source = PATH_HOLD.read_text(encoding="utf-8")

    assert "last_truth_path: RosPath | None = None" in source
    assert "if truth.poses:\n            last_truth_path = truth" in source
    assert "if last_truth_path is not None:\n            last_truth_path.header.stamp = rospy.Time.now()" in source
    assert "Do not replace a real path with an empty fallback" in source


def test_goal4_path_hold_latches_persistent_body_axes() -> None:
    source = PATH_HOLD.read_text(encoding="utf-8")

    assert "MarkerArray, queue_size=1, latch=True" in source
    assert "marker.lifetime = rospy.Duration(0)" in source
