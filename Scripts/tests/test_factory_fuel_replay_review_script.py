from pathlib import Path


def test_factory_fuel_replay_uses_an_isolated_display_only_master() -> None:
    script = Path("Scripts/sunray/run_factory_fuel_replay_review.sh").read_text(encoding="utf-8")

    assert "MASTER_PORT=11320" in script
    assert "ROS_MASTER_URI=\"http://127.0.0.1:${MASTER_PORT}\"" in script
    assert "roscore -p \"${MASTER_PORT}\"" in script
    assert "rosbag play --clock --delay=0.5" in script
    assert "sunray_ros1_factory_fuel_pointcloud_review.rviz" in script
    assert "sunray_ros1_factory_fuel_grid3d_review.rviz" in script
    assert "/mosim/goal4/livox_world_accumulated" in script
    assert "/mosim/goal4/occupancy_accumulated" in script
    assert "/mosim/goal4/truth_path" in script


def test_factory_fuel_replay_does_not_start_or_publish_to_the_flight_stack() -> None:
    script = Path("Scripts/sunray/run_factory_fuel_replay_review.sh").read_text(encoding="utf-8")

    # The claim boundary intentionally names the flight stack. Check executable
    # launch/publish forms instead of rejecting that explanatory text.
    forbidden_commands = (
        "gazebo --",
        "gzserver ",
        "px4 ",
        "px4ctrl ",
        "roslaunch ",
        "rostopic pub ",
        "rosservice call ",
    )
    assert not any(token in script.lower() for token in forbidden_commands)
