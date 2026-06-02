# FAST-LIO Input Contract Check

- status: `dense_lidar_ready_but_fastlio_input_blocked`
- dense_lidar_ready: `True`
- errors: `3`
- warnings: `0`

## Config

- path: `Config/ros2/mosim_spark_fast_lio_mid360.yaml`
- lidar_type: `1`
- scan_line: `4`
- scan_rate: `10`
- lidar topic: `/mosim/lidar_points`
- imu topic: `/mosim/forward/imu`

## Dense LiDAR Sample

- avg points/frame: `24290.8`
- observed lines: `[0, 1, 2, 3]`
- attributes: `['line', 'offset_time_ns', 'reflectivity', 'tag']`

## Findings

### ERROR - FAST-LIO replay dataset

legacy dataset avg points/frame=512.0 below 15000.

Action: Route FAST-LIO input through the dense Mid360 transport, not the old 512-point adapter.

### ERROR - FAST-LIO replay dataset

legacy dataset has no per-point Livox attributes.

Action: Do not use this file as the claimable FAST-LIO input.

### ERROR - IMU source

sample includes 5 synthetic IMU frames.

Action: Feed MWORKS/PX4-equivalent high-rate IMU into ROS2 before localization claims.
