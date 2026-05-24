# Result Variable Mapping

This file records how MWORKS/Sysplorer result variable names map to the project-standard CSV schema.

The `Model Result Variable` column below is a candidate mapping derived from `references/MWORKS/QuadrotorModel/package.mo`.
After the first successful Sysplorer MCP simulation, confirm the exact names with `result_manager`.

| Standard Name | Model Result Variable | Required | Notes |
|---|---|---:|---|
| `time` | `time` | yes | Simulation time axis |
| `x` | `sensors1_1.PosMea[1]` | yes | World position x, from `Sensors.AbsolutePosition.r[1]` |
| `y` | `sensors1_1.PosMea[2]` | yes | World position y, from `Sensors.AbsolutePosition.r[2]` |
| `z` | `sensors1_1.PosMea[3]` | yes | World position z, from `Sensors.AbsolutePosition.r[3]` |
| `vx` | candidate unavailable | recommended | Query `quadChassisTest17_1.*.v*` or derivative of position after first result export |
| `vy` | candidate unavailable | recommended | Query `quadChassisTest17_1.*.v*` or derivative of position after first result export |
| `vz` | candidate unavailable | recommended | Query `quadChassisTest17_1.*.v*` or derivative of position after first result export |
| `roll` | `sensors1_1.AngleMea[1]` | recommended | Angle sequence is `{1,2,3}` in `Sensors.AbsoluteAngles` |
| `pitch` | `sensors1_1.AngleMea[2]` | recommended | Angle sequence is `{1,2,3}` in `Sensors.AbsoluteAngles` |
| `yaw` | `sensors1_1.AngleMea[3]` | recommended | Angle sequence is `{1,2,3}` in `Sensors.AbsoluteAngles` |
| `u1` | `controller3_2.y` | recommended | Motor command 1 to `actuator1_1.u` |
| `u2` | `controller3_2.y1` | recommended | Motor command 2 to `actuator1_2.u` |
| `u3` | `controller3_2.y2` | recommended | Motor command 3 to `actuator1_3.u` |
| `u4` | `controller3_2.y3` | recommended | Motor command 4 to `actuator1_4.u` |
| `motor_speed_1` | `speedSensor[1].w` | optional | Rotational speed sensor attached to motor 1 flange |
| `motor_speed_2` | `speedSensor[2].w` | optional | Rotational speed sensor attached to motor 2 flange |
| `motor_speed_3` | `speedSensor[3].w` | optional | Rotational speed sensor attached to motor 3 flange |
| `motor_speed_4` | `speedSensor[4].w` | optional | Rotational speed sensor attached to motor 4 flange |
| `x_ref` | `climbePath.position_command[1]` | yes | Reference x; component name is `climbePath` in all official examples |
| `y_ref` | `climbePath.position_command[2]` | yes | Reference y; component name is `climbePath` in all official examples |
| `z_ref` | `climbePath.position_command[3]` | yes | Reference z; component name is `climbePath` in all official examples |
| `x_ref` | `planningReference.position_command[1]` | yes | A*/quintic planning reference in `Sunray150Planning*SysblockClosedLoop` models |
| `y_ref` | `planningReference.position_command[2]` | yes | A*/quintic planning reference in `Sunray150Planning*SysblockClosedLoop` models |
| `z_ref` | `planningReference.position_command[3]` | yes | A*/quintic planning reference in `Sunray150Planning*SysblockClosedLoop` models |
| `x_ref` | `mission_ref_x.y` | yes | Custom mission reference for return/land-only review models |
| `y_ref` | `mission_ref_y.y` | yes | Custom mission reference for return/land-only review models |
| `z_ref` | `mission_ref_z.y` | yes | Custom mission reference for return/land-only review models |
| `controller_mode` | custom controller only | optional | Mode switching and video annotation |
| `event_log` | custom exporter only | optional | Event-driven replay and report evidence |

## Official Example Components

The three official examples use the same component names for result extraction:

| Example | Model | Path Component | Sensor Component | Controller Component |
|---|---|---|---|---|
| Example1 | `QuadrotorModel.Examples.Example1` | `climbePath` (`PathPlanning.ClimbPath`) | `sensors1_1` | `controller3_2` |
| Example2 | `QuadrotorModel.Examples.Example2` | `climbePath` (`PathPlanning.CirclePath`) | `sensors1_1` | `controller3_2` |
| Example3 | `QuadrotorModel.Examples.Example3` | `climbePath` (`PathPlanning.EightPath`) | `sensors1_1` | `controller3_2` |
| Planning | `QuadrotorExperiments.Sunray150Planning*SysblockClosedLoop` | `planningReference` (`PlannedQuinticReference`) | `sensors1_1` | `controller3_2` |

First `result_manager` query list:

```text
time
sensors1_1.PosMea[1]
sensors1_1.PosMea[2]
sensors1_1.PosMea[3]
sensors1_1.AngleMea[1]
sensors1_1.AngleMea[2]
sensors1_1.AngleMea[3]
climbePath.position_command[1]
climbePath.position_command[2]
climbePath.position_command[3]
controller3_2.y
controller3_2.y1
controller3_2.y2
controller3_2.y3
speedSensor[1].w
speedSensor[2].w
speedSensor[3].w
speedSensor[4].w
```

## Update Procedure

1. Run or open a result file with Sysplorer MCP `result_manager`.
2. Query the candidate variables above first.
3. If a candidate name is rejected, list available variables and update this file.
4. Use the standard names when exporting `results/{group}/{scene}/{experiment}/raw/*.csv`.
5. Keep non-obvious mappings in experiment logs under `results/{group}/{scene}/{experiment}/logs/`.
