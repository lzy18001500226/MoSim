# Real UAV Stack Minimum Loop Gate

- status: `ready_for_manual_rviz_ue_review`
- errors: `0`
- warnings: `0`
- FAST-LIO input contract: `claimable_input_ready`
- FAST-LIO runtime counts: `{'odometry': 80, 'path': 8, 'registered_cloud': 80}`
- FAST-LIO evaluation: `{'status': 'pass', 'metrics': {'truth_frames': 40, 'odometry_samples': 80, 'odometry_samples_after_time_sort': 80, 'aligned_samples': 42, 'position_rmse_m': 0.39454, 'max_position_error_m': 0.611542, 'yaw_rmse_rad': 0.017802}}`

## Required Rates

- truth/controller: `20.0` / `20.0` Hz
- IMU: `200.0` Hz
- LiDAR: `10.0` Hz baseline

## Findings

No blocking findings.
