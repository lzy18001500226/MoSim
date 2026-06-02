# Factory FAST-LIO Failure Diagnosis

- scene_id: `factoryenvironmentcollect`
- status: `not_claimable`
- truth_dataset: `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_replay_dataset.jsonl`
- fastlio_config: `Config/ros2/mosim_spark_fast_lio_velodyne.yaml`

## Summary

Factory FAST-LIO is not blocked by topic plumbing: existing recordings contain
odometry, path, and registered-cloud summaries. It is blocked by localization
quality and input-contract mismatches.

## Runtime Results

### fastlio_runtime

- status: `failed_error_threshold`
- position_rmse_m: `10.203006`
- max_position_error_m: `17.70852`
- yaw_rmse_rad: `0.014247`
- odometry nonmonotonic_pairs: `2`
- registered_cloud_points_avg: `509.543`

### fastlio_runtime_scan099

- status: `failed_error_threshold`
- position_rmse_m: `9.760564`
- max_position_error_m: `18.547103`
- yaw_rmse_rad: `0.050424`
- odometry nonmonotonic_pairs: `59`
- registered_cloud_points_avg: `509.286`

## Key Input Contract

- config lidar_type: `2`
- config scan_line: `16`
- config scan_rate: `10`
- config extrinsic_est_en: `False`
- truth points/frame avg: `509.433`
- truth synthetic IMU frames: `314`
- truth fixed_yaw: `True`

## Findings

- `critical` FAST-LIO sensor model: config lidar_type=2, while target Mid360/Livox-style data should use Livox serial semantics.
  Recommendation: Create a Livox/Mid360 FAST-LIO config path (`lidar_type=1`, `scan_line=4`) or route through a FAST-LIO variant confirmed to accept current PointCloud2 fields.
- `high` FAST-LIO scan lines: config scan_line=16; Sunray/Mid360 references use 4 lines, and the dense replay path emits line values 0-3.
  Recommendation: Align scan_line with the actual Mid360/Livox replay contract before retesting localization.
- `medium` LiDAR/IMU extrinsics: extrinsic_est_en=false and extrinsic_T is identity/zero.
  Recommendation: Keep identity only for a controlled synthetic frame; otherwise define the Sunray150 LiDAR-to-IMU mount or enable a validated calibration route.
- `critical` IMU source: 314 replay frames use synthetic IMU; sources=['finite_difference_from_scene_truth_replay'].
  Recommendation: Generate/export measured high-rate MWORKS IMU at about 200Hz or a physically consistent simulated IMU before claiming FAST-LIO quality.
- `critical` LiDAR density: FAST-LIO truth replay averages 509.433 points/frame; adapter max is 512.
  Recommendation: Replace the low-density legacy replay with the dense Livox-like C++ transport or a UE C++ raycast sensor before localization tuning.
- `high` Per-point timing: fastlio_replay_dataset.jsonl has no point_attributes in sampled frames, so per-point offset_time/line/tag are absent from the evaluated dataset.
  Recommendation: Use the Livox-like replay frames with offset_time/tag/line, or generate a FAST-LIO dataset that preserves those attributes.
- `medium` Motion excitation: truth yaw span is 0.0 rad and adapter fixed_yaw_for_fastlio_input=True.
  Recommendation: Add realistic yaw and acceleration excitation after the sensor contract is fixed, then evaluate whether observability improves.
- `critical` Runtime quality: fastlio_runtime: status=failed_error_threshold, RMSE=10.203006m, max_error=17.70852m.
  Recommendation: Do not use this Factory run as localization evidence; rerun only after sensor/config/time fixes.
- `high` Odometry timestamps: fastlio_runtime: nonmonotonic_pairs=2, raw_samples=339, unique_timestamps=339.
  Recommendation: Fix replay/runtime timestamp monotonicity before evaluating controller or mapper quality.
- `critical` Runtime quality: fastlio_runtime_scan099: status=failed_error_threshold, RMSE=9.760564m, max_error=18.547103m.
  Recommendation: Do not use this Factory run as localization evidence; rerun only after sensor/config/time fixes.
- `high` Odometry timestamps: fastlio_runtime_scan099: nonmonotonic_pairs=59, raw_samples=2998, unique_timestamps=2703.
  Recommendation: Fix replay/runtime timestamp monotonicity before evaluating controller or mapper quality.
- `info` Dense transport status: Livox-like manifest averages 20507.6 points/frame at 10.0Hz, but this is not the evaluated FAST-LIO dataset.
  Recommendation: Promote the dense Livox-like dataset into the FAST-LIO runtime path after config and IMU synchronization are corrected.

## Next Actions

1. Stop treating Factory FAST-LIO as claimable evidence until RMSE/max-error pass the runtime gate.
2. Move Factory runtime input from low-density legacy replay to dense Livox/Mid360-shaped data with per-point timing fields.
3. Create a Mid360/Livox FAST-LIO config path and test lidar_type/scan_line/timestamp_unit against the selected ROS2 FAST-LIO implementation.
4. Replace synthetic finite-difference IMU with high-rate MWORKS IMU or a physically consistent simulated IMU synchronized to LiDAR.
5. Fix nonmonotonic odometry/replay timestamp behavior and rerun runtime evaluation.
6. Only after localization passes, reconnect local 3D map and planner review windows.
