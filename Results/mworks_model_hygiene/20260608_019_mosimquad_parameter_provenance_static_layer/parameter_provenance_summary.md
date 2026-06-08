# MoSimQuadrotorModel Parameter Provenance Static Layer

Task: `PMO-MWORKS-R1-MOSIMQUAD-PARAMETER-PROVENANCE-STATIC-LAYER-20260608-019`

## Source Change

Added a project-owned static package:

- `Models/MoSimQuadrotorModel/Parameters/package.mo`
- `Models/MoSimQuadrotorModel/Parameters/package.order`

The package exposes `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`, a record-only source/provenance table. It has no equations, connectors, component instances, or behavior-changing links into the current dynamics chain.

Top-level package exposure was limited to:

- `Models/MoSimQuadrotorModel/package.order`

`Models/MoSimQuadrotorModel/package.mo` was not changed because `MoSimQuadrotorModel` already extends `Modelica.Icons.Package` and the new child package is discoverable through `package.order`.

## Provenance Boundary

Accepted geometry:

- Rotor centers are from the user-reviewed DAE/Blender screw-pair assembly manifest.
- The values are recorded in MWORKS `Dronefixed1..4` order.
- This is geometry/assembly provenance only.

Non-geometry seeds:

- Mass, inertia, SDF motor constant, MWORKS visual-speed lift coefficient, yaw moment ratio, motor lag constants, spin/yaw signs, normalized-command bounds, optional rotor gyro, drag, and damping values remain source-labeled seeds.
- These values are not promoted to Sunray150 truth and are not parameter identification evidence.

## Static Values Recorded

Rotor centers, MWORKS `Dronefixed1..4` order:

| Index | x m | y m | z m | Source |
|---|---:|---:|---:|---|
| Dronefixed1 | 0.053745 | -0.053740 | -0.014052 | user-reviewed DAE screw-pair fit |
| Dronefixed2 | 0.053746 | 0.053759 | -0.014052 | user-reviewed DAE screw-pair fit |
| Dronefixed3 | -0.053761 | 0.053760 | -0.014052 | user-reviewed DAE screw-pair fit |
| Dronefixed4 | -0.053761 | -0.053739 | -0.014052 | user-reviewed DAE screw-pair fit |

Primary non-geometry seeds:

| Parameter | Value | Source label | Boundary |
|---|---:|---|---|
| `mass_kg` | 1.0 | `SDF_migration` | not measured takeoff mass |
| `body_inertia_diagonal_kg_m2` | `{0.0085, 0.0085, 0.012}` | `SDF_migration` | not identified inertia |
| `sdf_motor_constant` | `8.54858e-06` | Sunray/Gazebo SDF seed | not identified thrust curve |
| `rotor_velocity_slowdown_sim` | `10` | Sunray/Gazebo SDF visual slowdown seed | visual simulation scale only |
| `mworks_lift_coefficient` | `0.000854858` | `SDF_migration` | SDF motor constant scaled for MWORKS visual speed |
| `yaw_moment_ratio_seed` | `0.06` | Sunray/Gazebo SDF seed | not identified yaw torque coefficient |
| `motor_time_constant_up_s` | `0.0125` | Sunray/Gazebo SDF seed | not ESC/RPM bench identified |
| `motor_time_constant_down_s` | `0.025` | Sunray/Gazebo SDF seed | not ESC/RPM bench identified |

Optional layer seeds from 018 remain disabled or zero:

- `enable_rotor_gyro_default=false`
- `enable_body_drag_default=false`
- `enable_angular_damping_default=false`
- `rotor_polar_inertia_seed={0,0,0,0}`
- `body_drag_coefficient_seed={0,0,0}`
- `angular_damping_coefficient_seed={0,0,0}`

## Claim Boundary

019 claims only static project-owned parameter provenance organization.

019 does not claim live MWORKS load, `check_model`, `SimulateModel`, native result, `.msr`, graphical/layout acceptance, package-browser acceptance, controller performance, planner readiness, runtime ack, mission success, parameter identification, or `closed_loop`.
