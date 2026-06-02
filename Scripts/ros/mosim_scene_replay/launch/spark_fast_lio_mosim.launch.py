"""Launch spark-fast-lio with MoSim synthetic sensor frames.

The upstream MIT launch file embeds dataset-specific TF:
`base -> velodyne_link = [0.13, 0, 0.52]` and a rotated base/map transform.
MoSim replay points are generated in the UAV body/LiDAR frame with identity
LiDAR/IMU extrinsics, so this launch keeps base, LiDAR, and IMU frames aligned.
"""

from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("start_rviz", default_value="false"),
            DeclareLaunchArgument("lidar_topic", default_value="/mosim/livox/lidar"),
            DeclareLaunchArgument("imu_topic", default_value="/mosim/forward/imu"),
            DeclareLaunchArgument("map_frame", default_value="ue_world"),
            DeclareLaunchArgument("base_frame", default_value="base"),
            DeclareLaunchArgument("use_base_extrinsics", default_value="true"),
            DeclareLaunchArgument("lidar_frame", default_value="base/mid360_link"),
            DeclareLaunchArgument("imu_frame", default_value="base/forward_imu_optical_frame"),
            DeclareLaunchArgument(
                "config_path",
                default_value="/mnt/c/Users/HP/Desktop/MoSim/Config/ros2/mosim_spark_fast_lio_mid360.yaml",
            ),
            DeclareLaunchArgument(
                "rviz_path",
                default_value="/mnt/c/Users/HP/Desktop/MoSim/Config/rviz2/mosim_uav_fastlio_pointcloud.rviz",
            ),
            Node(
                package="spark_fast_lio",
                executable="spark_lio_mapping",
                name="lio_mapping",
                output="screen",
                remappings=[
                    ("lidar", LaunchConfiguration("lidar_topic")),
                    ("imu", LaunchConfiguration("imu_topic")),
                ],
                parameters=[
                    {
                        "common.lidar_frame": LaunchConfiguration("lidar_frame"),
                        "common.imu_frame": LaunchConfiguration("imu_frame"),
                        "common.map_frame": LaunchConfiguration("map_frame"),
                        "common.base_frame": PythonExpression(
                            [
                                "'",
                                LaunchConfiguration("base_frame"),
                                "' if '",
                                LaunchConfiguration("use_base_extrinsics"),
                                "' == 'true' else ''",
                            ]
                        ),
                        "common.visualization_frame": LaunchConfiguration("base_frame"),
                        "gravity_alignment.enable_gravity_alignment": False,
                    },
                    LaunchConfiguration("config_path"),
                ],
            ),
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "run",
                    "tf2_ros",
                    "static_transform_publisher",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    LaunchConfiguration("base_frame"),
                    LaunchConfiguration("lidar_frame"),
                ],
                output="screen",
            ),
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "run",
                    "tf2_ros",
                    "static_transform_publisher",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    LaunchConfiguration("base_frame"),
                    LaunchConfiguration("imu_frame"),
                ],
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2_spark_fast_lio_mosim",
                arguments=["-d", LaunchConfiguration("rviz_path")],
                condition=IfCondition(LaunchConfiguration("start_rviz")),
                output="screen",
            ),
        ]
    )
