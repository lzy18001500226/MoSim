# FAST-LIO Input Contract Check

- status: `claimable_input_ready`
- dense_lidar_ready: `True`
- errors: `0`
- warnings: `1`

## Config

- path: `Config/ros2/mosim_spark_fast_lio_mid360.yaml`
- lidar_type: `1`
- scan_line: `4`
- scan_rate: `10`
- lidar topic: `/mosim/lidar_points`
- imu topic: `/mosim/forward/imu`

## FAST-LIO Implementation Support

- spark-fast-lio root: `Results/tmp/fastlio_ros2_candidates/spark-fast-lio`
- PointCloud2 supported lidar types: `['OUST64', 'KMOUST64', 'VELO16']`
- PointCloud2 Livox supported: `False`
- Livox CustomMsg path guarded: `True`

## Dense LiDAR Sample

- avg points/frame: `20507.6`
- observed lines: `[0, 1, 2, 3]`
- attributes: `['line', 'offset_time_ns', 'reflectivity', 'tag']`

## Findings

### WARNING - legacy FAST-LIO dataset

legacy fastlio_replay_dataset is present but is no longer the claimable Mid360 input path.

Action: Use dense Livox CustomMsg plus MWORKS/ROS2 IMU for runtime gates; keep legacy dataset only as a degraded historical reference.
