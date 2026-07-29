from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_swarm_review_uses_live_three_uav_topics_not_legacy_diff_relays() -> None:
    launcher = (ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_review.ps1").read_text(encoding="utf-8")
    cloud_config = (ROOT / "Config/rviz/sunray_ros1_swarm_formation_pointcloud_review.rviz").read_text(encoding="utf-8")
    grid_config = (ROOT / "Config/rviz/sunray_ros1_swarm_formation_grid3d_review.rviz").read_text(encoding="utf-8")

    assert "sunray_ros1_swarm_formation_pointcloud_review.rviz" in launcher
    assert "sunray_ros1_swarm_formation_grid3d_review.rviz" in launcher
    assert 'AcceptedRunId = "factory_l2_swarm_formation_maporigin_r54_runtime_20260722"' in launcher
    assert "sunray_ros1_goal5_diff_swarm_pointcloud_review.rviz" not in launcher
    assert "sunray_ros1_goal5_diff_swarm_grid3d_review.rviz" not in launcher
    for uid in range(1, 4):
        assert f"/uav{uid}/livox/lidar" in launcher
        assert f"/uav{uid}/sunray/gazebo_pose" in launcher
        assert f"/mosim/swarm_formation/uav{uid}/livox_world_accumulated" in cloud_config
        assert f"mosim_swarm_formation_uav{uid}_pointcloud_review" in launcher
    for drone_id in range(3):
        assert f"/drone_{drone_id}/ego_planner_node/grid_map/occupancy_inflate" in grid_config
    assert "/mosim/goal5/" not in cloud_config
    assert "/mosim/goal5/" not in grid_config


def test_pointcloud_review_node_accepts_unique_ros_node_names() -> None:
    source = (ROOT / "Scripts/sunray/px4ctrl_pointcloud_review_node.py").read_text(encoding="utf-8")

    assert 'parser.add_argument("--node-name", default="mosim_px4ctrl_pointcloud_review")' in source
    assert "rospy.init_node(args.node_name, anonymous=False)" in source
