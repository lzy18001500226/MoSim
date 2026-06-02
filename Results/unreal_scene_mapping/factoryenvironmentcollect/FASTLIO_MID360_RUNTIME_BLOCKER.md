# Factory FAST-LIO Mid360 Runtime Blocker

Date: 2026-06-02

## Summary

The dense Factory Mid360 replay is ready as sensor-like input, but the current
ROS2 `spark-fast-lio` runtime cannot consume it as a claimable Mid360/Livox
FAST-LIO input path.

The blocking issue is implementation compatibility, not RViz point size and not
only point-cloud density:

- MoSim dense input publishes Livox-like `PointCloud2` fields on
  `/mosim/lidar_points`.
- The selected Mid360 config sets `lidar_type=1`, `scan_line=4`.
- The local ROS2 `spark-fast-lio` `PointCloud2` preprocessing path handles
  only `OUST64`, `KMOUST64`, and `VELO16`.
- Livox/AVIA handling is behind `LIVOX_ROS_DRIVER_FOUND` and expects
  `livox_ros_driver::CustomMsg`, not the current `sensor_msgs/PointCloud2`
  path.

## Runtime Evidence

Runtime output directory:

```text
Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_mid360_dense_smoke
```

`FASTLIO_RUNTIME_RECORDING.json` recorded zero output messages:

```text
odometry: 0
path: 0
registered_cloud: 0
```

The launch log includes:

```text
[FATAL] [Preprocess]: Error LiDAR Type
[WARN] [lio_mapping]: No point, skip this scan!
Warning: TF_OLD_DATA ignoring data from the past for frame base_link
```

## Source Evidence

Local source:

```text
Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio/src/preprocess.cpp
Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio/include/preprocess.h
```

`Preprocess::process(sensor_msgs::msg::PointCloud2)` switches only over
`OUST64`, `KMOUST64`, and `VELO16`, then reports `Error LiDAR Type` for the
default branch. The Livox path is compiled only when `LIVOX_ROS_DRIVER_FOUND`
is available and uses `livox_ros_driver::CustomMsg`.

## Decision

Do not spend time tuning RViz, grid steps, or point size on this path. The next
runtime decision must be one of:

1. emit Livox `CustomMsg` and rebuild a compatible FAST-LIO runtime with Livox
   message support;
2. switch to a FAST-LIO/FAST-LIO2/Livox-capable implementation already present
   in local references or bring in a suitable ROS2 fork;
3. use Velodyne-compatible mode only as a degraded smoke test, explicitly not
   as Mid360/云纵150 evidence.

Also fix timestamp policy before the next runtime proof: live ROS2 replay must
not mix wall-time stamps and replay-time TF stamps.
