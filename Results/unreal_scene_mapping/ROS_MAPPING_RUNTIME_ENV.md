# ROS Mapping Runtime Environment

- ready_for_native_mapping_runtime: `true`
- blockers: none
- degraded: `missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`, `missing_catkin_build_tool`, `fast_lio_ros1_package_not_visible:fast_lio`, `no_local_ros2_fastlio_family_source`
- ros_generation: `ros2`
- ros2_replay_ready: `true`
- fastlio_ros2_runtime_claimable: `false`
- ROS_DISTRO: `humble`
- ROS_MASTER_URI: `None`

Commands:
- `ros2`: `/opt/ros/humble/bin/ros2`
- `roscore`: `None`
- `roslaunch`: `None`
- `rostopic`: `None`
- `rosnode`: `None`
- `rosparam`: `None`
- `rviz`: `None`
- `rviz2`: `/opt/ros/humble/bin/rviz2`
- `catkin_make`: `None`
- `catkin`: `None`
- `colcon`: `/usr/bin/colcon`
- `python3`: `/usr/bin/python3`
- `rospack`: `None`

Packages:
- `fast_lio`: visible=`false`, path=`None`
  error: `missing rospack; source ROS1 setup.bash first`
- `ros2:rviz2`: visible=`true`, path=`/opt/ros/humble`
- `ros2:sensor_msgs`: visible=`true`, path=`/opt/ros/humble`
- `ros2:nav_msgs`: visible=`true`, path=`/opt/ros/humble`
- `ros2:geometry_msgs`: visible=`true`, path=`/opt/ros/humble`
- `ros2:tf2_ros`: visible=`true`, path=`/opt/ros/humble`

Recommended setup sequence:
- Use Ubuntu 22.04 with ROS2 Humble as the primary runtime.
- source /opt/ros/humble/setup.bash
- Run Scripts/UE5/check_ros_mapping_runtime_env.py --write again.
- Run DRY_RUN=1 MAX_FRAMES=2 RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh <scene>.
- Run RVIZ_PROFILE=split Scripts/UE5/open_mapping_rviz_ros2.sh <scene> for native RViz2 input/map review.
- Run Scripts/UE5/run_fastlio_rviz_replay_ros2.sh <scene> for ROS2 input replay; keep START_FASTLIO=0 unless a real ROS2 FAST-LIO launch command is configured.
- Run Scripts/UE5/check_fastlio_ros2_topics.sh during the live ROS2 run.
- Run Scripts/UE5/check_fastlio_family_compatibility.py --write after adding or changing FAST-LIO-family sources.
- Treat local References/Lab/FAST_LIO as ROS1-only until a ROS2 FAST-LIO/FAST-LIO2 package is added or a containerized ROS1 bridge route is approved.

Claim boundary:
- This is only an environment preflight; it does not prove mapping runtime evidence.
- Runtime evidence still requires live ROS topics, RViz visibility, recording, and FAST-LIO evaluation.
- HTML is not an accepted active point-cloud/map review window.
- On Ubuntu 22.04, ROS2/RViz2 is the primary runtime. ROS1/Catkin FAST-LIO blockers are degraded compatibility blockers, not blockers for ROS2 replay input review.
- Do not claim FAST-LIO localization until a real ROS2 FAST-LIO-family package publishes /cloud_registered and /Odometry, or an approved ROS1 bridge route records equivalent outputs.
