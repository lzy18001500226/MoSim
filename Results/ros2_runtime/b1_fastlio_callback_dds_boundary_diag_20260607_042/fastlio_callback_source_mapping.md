# FAST-LIO Callback / Source Stamp Mapping

Request: RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-CALLBACK-DDS-BOUNDARY-DIAG-20260607-042

Scope: static-only diagnosis. No ROS graph probe was run for 042.

## Source Publisher Stamp Origin

- `Scripts/ros/mosim_dense_lidar_cpp/src/dense_lidar_replay_node.cpp:213` sets `PointCloud2.header.stamp = now()`.
- `Scripts/ros/mosim_dense_lidar_cpp/src/dense_lidar_replay_node.cpp:215` copies the same stamp into `Livox CustomMsg.header.stamp`.
- `Scripts/ros/mosim_dense_lidar_cpp/src/dense_lidar_replay_node.cpp:216-218` derives `Livox CustomMsg.timebase` from that header stamp in nanoseconds.
- `Scripts/ros/mosim_mworks_state_imu_replay_node.cpp:201` uses `const auto stamp = now()`.
- `Scripts/ros/mosim_mworks_state_imu_replay_node.cpp:215`, `:233`, and `:255` stamp IMU, truth odom, and TF from that `now()` value.

Implication: the ROS header stamps observed by recorders and FAST-LIO are runtime node-clock stamps, not the source JSONL frame `time` values.

## FAST-LIO Callback State

- `Results/tmp/fastlio_ros2_candidates_import/FAST_LIO_ROS2-ros2/src/laserMapping.cpp:91` declares `last_timestamp_lidar` and `last_timestamp_imu`.
- `laserMapping.cpp:318-342` handles Livox CustomMsg in `livox_pcl_cbk`, computes `cur_time` from `msg->header.stamp`, compares it to `last_timestamp_lidar`, and updates `last_timestamp_lidar`.
- `laserMapping.cpp:366-397` handles IMU in `imu_cbk`, computes `timestamp` from `msg_in->header.stamp`, compares it to `last_timestamp_imu`, and updates `last_timestamp_imu`.
- `laserMapping.cpp:946` subscribes to the Livox topic with queue depth 20.
- `laserMapping.cpp:952` subscribes to the IMU topic with queue depth 10.
- `Config/ros2/mosim_fast_lio_ros2_mid360.yaml:15-16` keeps `time_sync_en: false` and `time_offset_lidar_to_imu: 0.0`.

Implication: FAST-LIO loop-back messages are callback-local comparisons against persistent `last_timestamp_*` state. They are not equivalent to a bounded recorder saying the prefix it sampled was monotonic.

## Boundary Classification

041 is best classified as a full-window callback/DDS/replay-boundary issue, not as a contradiction in the 041 active recorder. The active recorder sampled a monotonic prefix. FAST-LIO remained subscribed through more of the finite replay and observed callback-local regressions after that prefix.
