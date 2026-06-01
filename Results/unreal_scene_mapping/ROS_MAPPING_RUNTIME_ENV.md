# ROS Mapping Runtime Environment

- ready_for_native_mapping_runtime: `false`
- blockers: `missing_ros1_commands:roscore,roslaunch,rostopic,rosnode,rosparam,rviz`, `missing_catkin_build_tool`, `ros_environment_not_sourced`, `fast_lio_package_not_visible:fast_lio`
- ROS_DISTRO: `None`
- ROS_MASTER_URI: `None`

Commands:
- `roscore`: `None`
- `roslaunch`: `None`
- `rostopic`: `None`
- `rosnode`: `None`
- `rosparam`: `None`
- `rviz`: `None`
- `rviz2`: `None`
- `catkin_make`: `None`
- `catkin`: `None`
- `colcon`: `None`
- `python3`: `/usr/bin/python3`
- `rospack`: `None`

Packages:
- `fast_lio`: visible=`false`, path=`None`
  error: `missing rospack; source ROS1 setup.bash first`

Recommended setup sequence:
- Install or open a WSL environment with ROS1 Noetic-compatible tools.
- source /opt/ros/noetic/setup.bash
- Run Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh to wire References/Lab/FAST_LIO into Results/tmp/fastlio_ros1_ws and build it.
- source Results/tmp/fastlio_ros1_ws/devel/setup.bash
- Run Scripts/UE5/check_ros_mapping_runtime_env.py --write again.
- Run Scripts/UE5/run_fastlio_rviz_replay_ros1.sh <scene>.
- Run Scripts/UE5/check_fastlio_ros1_topics.sh during the live run.

Claim boundary:
- This is only an environment preflight; it does not prove mapping runtime evidence.
- Runtime evidence still requires live ROS topics, RViz visibility, recording, and FAST-LIO evaluation.
- HTML is not an accepted active point-cloud/map review window.
