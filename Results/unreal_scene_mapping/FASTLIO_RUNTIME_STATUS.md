# FAST-LIO Runtime Status

Last updated: 2026-06-01.

## Environment

Native ROS2 Humble is working on the Ubuntu 22.04 WSL2 host.

```text
ROS_DISTRO=humble
ros2=/opt/ros/humble/bin/ros2
rviz2=/opt/ros/humble/bin/rviz2
colcon=/usr/bin/colcon
ROS apt key=/usr/share/keyrings/ros-archive-keyring.gpg
ROS apt source=https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy main
```

The ROS apt key problem is resolved. Do not reinstall ROS2 unless these checks
fail again.

ROS2 runtime logs must stay inside the project:

```text
ROS_LOG_DIR=Results/tmp/ros_logs
```

This avoids failures when `/home/linux/.ros/log` is read-only in the active
agent sandbox.

## Runtime Claim

The `spark-fast-lio` ROS2 candidate builds under
`Results/tmp/spark_fast_lio_ros2_ws` and produces real runtime outputs on:

```text
/cloud_registered
/odometry
/path
```

MoSim uses `Scripts/ros/mosim_scene_replay/launch/spark_fast_lio_mosim.launch.py`
with identity LiDAR/IMU extrinsics. The upstream MIT campus launch transform is
not valid for the current synthetic MoSim sensor frames.

## Current Evaluation

| Scene | Status | RMSE | Max Error | Acceptance |
|---|---:|---:|---:|---|
| `factoryenvironmentcollect` | `failed_error_threshold` | 9.761 m | 18.547 m | fail / degraded |
| `derelictcorridormegascans` | `pass` | 0.814 m | 1.938 m | pass with warnings |

Thresholds:

```text
max_position_rmse_m=1.0
max_position_error_m=3.0
```

Factory localization is degraded and cannot be claimed. Derelict passes the
current numeric threshold using the `scan099` run, but the runtime log still
contains IMU sufficiency warnings and odometry timestamps are partly
nonmonotonic. Treat it as a real ROS2 FAST-LIO runtime pass with quality
warnings, not as final production-grade localization.

Evidence:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_scan099/
Results/unreal_scene_mapping/derelictcorridormegascans/fastlio_runtime_scan099/
```

Current best runtime settings:

```text
SCAN_DURATION_S=0.099
IMU_SUBSTEPS_PER_FRAME=12
IMU_SPAN_S=0.099
IMU_LEAD_SLEEP_S=0.01
FASTLIO_LIDAR_TOPIC=/mosim/lidar_points
FASTLIO_IMU_TOPIC=/mosim/forward/imu
FASTLIO_LIDAR_FRAME=base/velodyne_link
FASTLIO_IMU_FRAME=base/forward_imu_optical_frame
```
