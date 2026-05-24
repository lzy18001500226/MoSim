# PX4 Reference Index

> Purpose: index the local PX4 source tree for the MWORKS quadrotor project. This file is a navigation and migration map, not a copy of PX4 implementation.

## 1. Local Source Boundary

```text
References/PX4/
```

Current repository check:

```text
largest file checked: 26.8 MB
files > 50 MB: none found
```

The PX4 tree is used as an engineering reference for flight-mode logic, failsafe semantics, estimator/control interfaces, actuator and battery abstractions. It is not a build dependency of the current MWORKS model.

## 2. High-Value PX4 Modules

| PX4 area | Local path | Use in this project |
|---|---|---|
| Commander | `References/PX4/src/modules/commander/` | arming, navigation state, health checks, mode transitions |
| Failsafe | `References/PX4/src/modules/commander/failsafe/` | failsafe flag handling and degraded-action selection |
| Health and arming checks | `References/PX4/src/modules/commander/HealthAndArmingChecks/` | battery, estimator, ESC, GNSS, offboard, mission, wind checks |
| Flight mode manager | `References/PX4/src/modules/flight_mode_manager/` | mapping navigation state to flight task / setpoint generator |
| Multicopter position control | `References/PX4/src/modules/mc_pos_control/` | trajectory setpoint consumption, takeoff, position-control limits |
| Control allocator | `References/PX4/src/modules/control_allocator/` | actuator allocation and saturation diagnostics |
| Battery status | `References/PX4/src/modules/battery_status/` | voltage, remaining capacity, warning levels |
| ESC battery / actuator simulation | `References/PX4/src/modules/esc_battery/`, `References/PX4/src/modules/simulation/` | electric power and actuator-health abstraction ideas |
| EKF2 | `References/PX4/src/modules/ekf2/` | future estimator interface reference; do not port full EKF initially |

## 3. Key Message Interfaces

| PX4 message | Local path | Project mapping |
|---|---|---|
| `VehicleStatus` | `References/PX4/msg/versioned/VehicleStatus.msg` | `flight_mode`, `arming_state`, `failsafe`, `nav_state` |
| `FailsafeFlags` | `References/PX4/msg/FailsafeFlags.msg` | `safety_status`, `health_status`, mode-degradation triggers |
| `VehicleControlMode` | `References/PX4/msg/versioned/VehicleControlMode.msg` | control mode enable flags |
| `TrajectorySetpoint` | `References/PX4/msg/versioned/TrajectorySetpoint.msg` | planner/controller setpoint: position, velocity, acceleration, yaw, yawspeed |
| `OffboardControlMode` | `References/PX4/msg/OffboardControlMode.msg` | GUI/offboard selector for position/velocity/acceleration/attitude/direct actuator modes |
| `VehicleLocalPosition` | `References/PX4/msg/versioned/VehicleLocalPosition.msg` | `estimated_state` position/velocity source |
| `VehicleOdometry` | `References/PX4/msg/versioned/VehicleOdometry.msg` | future estimator state bus |
| `VehicleAttitude` | `References/PX4/msg/versioned/VehicleAttitude.msg` | attitude estimator output |
| `ActuatorMotors` | `References/PX4/msg/versioned/ActuatorMotors.msg` | normalized motor command and saturation interface |
| `BatteryStatus` | `References/PX4/msg/versioned/BatteryStatus.msg` | battery voltage, warning, remaining capacity, power scale |
| `HomePosition` | `References/PX4/msg/versioned/HomePosition.msg` | return-to-home / land target reference |
| `PositionSetpointTriplet` | `References/PX4/msg/PositionSetpointTriplet.msg` | previous/current/next setpoint pattern for mission-style navigation |

## 4. PX4 Navigation State Subset For This Project

Use a compact subset in MWORKS instead of importing the full PX4 state space.

| Project mode | PX4 reference | Meaning |
|---|---|---|
| `INIT` | pre-arm / boot logic | system initialized, no motor command |
| `ARM` | `ARMING_STATE_ARMED` | motors can accept commands |
| `TAKEOFF` | `NAVIGATION_STATE_AUTO_TAKEOFF` | vertical takeoff ramp and setpoint initialization |
| `MISSION` | `NAVIGATION_STATE_AUTO_MISSION` / `OFFBOARD` | normal planned trajectory tracking |
| `AVOID` | local path-planning enabled | local obstacle avoidance / replanning active |
| `RETURN` | `NAVIGATION_STATE_AUTO_RTL` | return-to-home / degraded navigation return |
| `LAND` | `NAVIGATION_STATE_AUTO_LAND` / `DESCEND` | controlled descent and landing |
| `FAILSAFE` | `failsafe=true`, `FailsafeFlags` | fallback action active |
| `DISARM` | `ARMING_STATE_DISARMED` | stop motors after landing |

## 5. Failsafe Triggers To Mirror

| Trigger | PX4 reference field | MWORKS signal |
|---|---|---|
| local position invalid | `FailsafeFlags.local_position_invalid` | `estimator_quality`, `gps_valid`, `mid360_valid` |
| offboard lost | `FailsafeFlags.offboard_control_signal_lost` | GUI/MCP/offboard heartbeat loss |
| home invalid | `FailsafeFlags.home_position_invalid` | `home_position_valid` |
| battery warning | `FailsafeFlags.battery_warning`, `BatteryStatus.warning` | `system_voltage_margin`, `battery_warning` |
| battery unhealthy | `FailsafeFlags.battery_unhealthy` | `power_ok=false` |
| motor failure | `FailsafeFlags.fd_motor_failure` | `eta_hat`, `fault_index`, ESC health |
| altitude loss | `FailsafeFlags.fd_alt_loss` | altitude error + descent rate |
| geofence breached | `FailsafeFlags.geofence_breached` | map bounds violation |
| mission failure | `FailsafeFlags.mission_failure` | planner failure / no feasible local path |
| wind limit exceeded | `FailsafeFlags.wind_limit_exceeded` | wind residual or control saturation |

## 6. Current MWORKS Mapping

| Project component | Current file/model | PX4-inspired role |
|---|---|---|
| `PerceptionInterfaceModule` | `Models/QuadrotorExperiments/package.mo` | GPS/Mid360 validity and obstacle margin |
| `V6XFlightControllerModule` | `Models/QuadrotorExperiments/package.mo` | simple state estimator and estimator quality |
| `ORINNXMissionComputerModule` | `Models/QuadrotorExperiments/package.mo` | flight mode, setpoint source, safety status |
| `SystemSupervisorModule` | `Models/QuadrotorExperiments/package.mo` | exported failsafe/status evidence |
| `BatteryPowerModule` | `Models/QuadrotorExperiments/package.mo` | voltage, power ok, voltage margin |
| `ESCDriveModule` | `Models/QuadrotorExperiments/package.mo` | motor command limiting, ESC health, saturation estimate |
| `AWFFControllerModule` | `Models/QuadrotorExperiments/package.mo` | controller + hover trim + motor command scaling |

## 7. Implementation Priority

1. Freeze a PX4-like `system_status_bus` in `Docs/Design/02_模型接口与运行流程.md`.
2. Add formal `battery_warning`, `home_position_valid`, `offboard_heartbeat_ok`, `mission_feasible`, and `geofence_ok` signals.
3. Extend `SystemSupervisorModule` from GPS dropout only to multi-trigger failsafe.
4. Add scenarios for battery low, offboard loss, planner failure, and geofence breach.
5. Record `event_log` for mode transitions and failsafe actions.
6. Keep PX4 source as reference; implement the MWORKS version as a compact, explainable subset.

## 8. Do Not Port Initially

| PX4 item | Reason |
|---|---|
| full EKF2 | too large; use simplified estimator interface first |
| full commander state machine | too broad; use compact competition-focused state subset |
| PX4 build system | not part of MWORKS deliverable |
| MAVLink drivers | not needed for current Sysplorer evidence |
| Gazebo bridge | optional future comparison, not current mainline |
