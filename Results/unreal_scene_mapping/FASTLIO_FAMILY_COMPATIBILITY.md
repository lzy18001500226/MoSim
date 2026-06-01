# FAST-LIO Family Compatibility

- can_claim_fastlio_ros2_runtime: `false`
- ros2_candidate_count: `0`
- ros1_catkin_only_count: `3`
- mixed_candidate_count: `0`
- degradation: `no_local_ros2_fastlio_family_source`, `local_fastlio_family_sources_are_ros1_catkin`

## Candidates

| Path | Package | Verdict | Key Markers | Topics Found |
|---|---|---|---|---|
| `References/Lab/FAST_LIO` | `fast_lio` | `ros1_catkin_only` | has_catkin, has_ros1_launch_xml | /Laser_map, /Odometry, /cloud_registered, /imu/data, /livox/imu, /livox/lidar, /path, /velodyne_points |
| `References/Lab/FAST-LIVO2` | `fast_livo` | `ros1_catkin_only` | has_catkin, has_ros1_launch_xml | /Laser_map, /Odometry, /cloud_registered, /livox/imu, /livox/lidar, /path |
| `References/Lab/Point-LIO-point-lio-with-grid-map` | `point_lio` | `ros1_catkin_only` | has_catkin, has_ros1_launch_xml | /Laser_map, /Odometry, /cloud_registered, /imu/data, /livox/imu, /livox/lidar, /path, /velodyne_points |

## Claim Boundary

- This scan only inspects local source metadata and ROS2 package visibility.
- It does not build FAST-LIO, launch ROS, record topics, or evaluate localization.
- FAST-LIO localization remains unclaimed until a real runtime publishes /cloud_registered and /Odometry and is recorded/evaluated.

## Recommended Next Actions

- Keep ROS2/RViz2 replay as the primary Ubuntu 22.04 map-review route.
- Add or review a ROS2 Humble FAST-LIO-family package before enabling START_FASTLIO=1 in the ROS2 wrapper.
- If using the current local ROS1/Catkin sources, use an explicitly approved ROS1 bridge/container route and record equivalent output topics.
