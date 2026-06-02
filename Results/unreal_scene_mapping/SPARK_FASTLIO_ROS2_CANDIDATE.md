# SPARK FAST-LIO ROS2 Candidate

- result: `building`
- phase: `build`
- repo: `https://github.com/MIT-SPARK/spark-fast-lio.git` @ `main`
- package_dir: `Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio`
- livox_msg_pkg: `Scripts/ros/livox_ros_driver2`
- mosim_scene_replay_pkg: `Scripts/ros/mosim_scene_replay`
- mosim_dense_lidar_cpp_pkg: `Scripts/ros/mosim_dense_lidar_cpp`
- workspace: `Results/tmp/spark_fast_lio_ros2_ws`
- apt_overlay_dir: `Results/tmp/ros2_overlay_pcl_ros`
- overlay_used: `true`
- ready_to_build: `true`
- runtime_claimable: `false`
- missing_ros2_packages: none
- manual_apt_packages: none

## Commands

- dry_run: `DRY_RUN=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh`
- preflight: `Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh`
- preflight_without_overlay: `AUTO_APT_OVERLAY=0 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh`
- build: `BUILD=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh`
- clean_build: `CLEAN_BUILD=1 BUILD=1 Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh`
- patch_readiness: `python3 Scripts/UE5/check_spark_fastlio_livox_patch_readiness.py --write`
- source_overlay_after_download: `export AMENT_PREFIX_PATH=Results/tmp/ros2_overlay_pcl_ros/opt/ros/humble:${AMENT_PREFIX_PATH}; export CMAKE_PREFIX_PATH=Results/tmp/ros2_overlay_pcl_ros/opt/ros/humble:${CMAKE_PREFIX_PATH:-${AMENT_PREFIX_PATH}}; export LD_LIBRARY_PATH=Results/tmp/ros2_overlay_pcl_ros/opt/ros/humble/lib:${LD_LIBRARY_PATH}`
- launch_after_build: `FASTLIO_ROS2_LAUNCH_CMD='set +u; source /opt/ros/humble/setup.bash; source Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash; ros2 launch spark_fast_lio mapping_mit_campus.launch.yaml start_rviz:=false scene_id:=mosim robot_name:=base base_frame:=base map_frame:=ue_world' START_FASTLIO=1 START_RVIZ=0 MAX_FRAMES=120 LOOP=1 FPS=10 FASTLIO_LIDAR_TOPIC=/mosim/livox/lidar FASTLIO_POINTCLOUD_TOPIC=/mosim/lidar_points FASTLIO_IMU_TOPIC=/mosim/forward/imu FASTLIO_LIDAR_FRAME=base/velodyne_link FASTLIO_IMU_FRAME=base/forward_imu_optical_frame Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect`

## Claim Boundary

- This prepares a ROS2 FAST-LIO2-family candidate only.
- It does not install apt packages into the system and does not store credentials.
- When AUTO_APT_OVERLAY=1, missing known ROS2 deb packages may be downloaded and extracted under Results/tmp only.
- runtime_claimable remains false until colcon build succeeds and live /cloud_registered plus odometry/path outputs are recorded.
- spark_fast_lio publishes odometry on relative topic odometry, so MoSim checks must account for /odometry or remap/namespace policy before claiming /Odometry.

## Note

colcon build has started. If the process is interrupted, inspect Results/tmp/spark_fast_lio_ros2_ws/log/latest_build.
