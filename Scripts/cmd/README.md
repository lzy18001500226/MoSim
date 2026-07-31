# Windows Command Entrypoints

`Scripts/cmd/` is the only Windows double-click entry directory. Every C99
entry keeps its terminal visible: terminal output and the newly created
`Results/sunray_ros1/<run_id>/` directory are the first error surfaces.
The four C99 entries resolve the repository from their own location and map it
to `Ubuntu-20.04` with `wslpath`; do not edit a personal absolute path into
these files.

## Current C99 Baseline

Run `00_准备C99单机环境.cmd` after a clean clone or after changing local
runtime sources. Then select exactly one demonstration entrypoint.

| Purpose | Entrypoint | Expected result |
| --- | --- | --- |
| Build and preflight the local C99 runtime | `00_准备C99单机环境.cmd` | Local PX4 SITL and ROS1 workspace build/preflight complete |
| Nominal C99 lifecycle | `01_运行C99单机起飞悬停降落.cmd` | `PX4CTRL_BASIC_MISSION_METRICS.json` reports `status=passed` |
| C99 bounded wind demonstration | `02_运行C99风扰闭环.cmd` | `DEMO_STATUS.json` and `WIND_INJECTION_EVIDENCE.json` report `status=passed` |
| C99 motor-efficiency fault and recovery | `03_运行C99电机故障恢复闭环.cmd` | `DEMO_STATUS.json` and `MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json` report `status=passed` |
| Open MoSim Ground Control | `启动MoSim地面站.cmd` | Ground Control starts independently; it does not start or control the C99 mission |
| Stop managed simulation processes | `停止所有仿真.cmd` | Stops the explicitly managed processes after a failed or aborted run |

The C99 routes use `graphical_px4ctrl_c99`, `PX4CTRL_CORE_PROFILE=graphical_c99`,
FAST-LIO to PX4 external vision to MAVROS local odometry, and the recorded
`PX4CTRL_HOVER_PERCENTAGE=0.456` runtime map. The controller reads only
`/uav1/mavros/local_position/odom`; Gazebo truth is not a direct controller
input.

These scripts reproduce an operational lifecycle and bounded injection
acknowledgement. They do not claim strict tracking performance, full
fault-tolerance, planner success, or QGC/UE display acceptance.

## Archived Entrypoints

`Archive/legacy_unverified/` contains prior FUEL, Diff, three-UAV, calibration,
and generic startup wrappers. They are retained for trace-back only and are not
current supported entrypoints. Do not use them as a substitute for the C99
baseline above.
