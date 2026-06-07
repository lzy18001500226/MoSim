# RFLY-MOSIM-MWORKS-DYNAMICS-MIN-UPGRADE-20260606-005

Date: 2026-06-06 CST

Status: completed as minimal project-owned MWORKS/Sysplorer dynamics smoke.

Source label: `source=MWORKS_MCP`.

## Scope

This task returned the P0 line from command echo work to the Sunray150/MoSim
quadrotor dynamics boundary. It verified the existing project-owned minimal
dynamics upgrade under `Models/QuadrotorExperiments/package.mo` and did not
edit the official baseline `References/MWORKS/QuadrotorModel/package.mo`.

The result is a dynamics smoke and source-labeled seeded-parameter model slice.
It is not parameter identification, controller performance evidence,
`closed_loop`, planner readiness, plant tracking, or mission success.

## Department-Local Goal

Confirm that a project-owned MWORKS dynamics slice contains the minimum
RflySim-style actuator/rotor structure needed for the Sunray150 P0 line:
command-to-speed mapping, first-order motor lag, `Ct * omega^2` thrust, yaw
reaction torque, and rotor-center arm moment from accepted DAE rotor centers.

## Model Evidence

Project-owned model:

```text
QuadrotorExperiments.Sunray150RflyStyleRotorDynamics
QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke
QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke
```

Relevant source lines in `Models/QuadrotorExperiments/package.mo`:

```text
Sunray150RflyStyleRotorDynamics: line 1321
moment_constant source label: line 1327
rotor_center source label and DAE-reviewed centers: line 1335
der(omega) first-order motor lag: line 1362
thrust = lift_coefficient * omega^2: line 1363
yaw_reaction_moment = yaw_direction * moment_constant * thrust: line 1364
rotor_arm_moment from r x F: lines 1365-1367
Hover smoke model: line 1376
Yaw-step smoke model: line 1388
```

## Dynamics Term Matrix

| Term | Status | Evidence / boundary |
|---|---|---|
| command-to-speed mapping | present in project-owned smoke | `motor_command[4]` drives signed visual rotor speed commands in `Sunray150RflyStyleRotorDynamics`. |
| first-order motor lag | present in project-owned smoke | `der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]`; `time_constant_up/down` are `source=SDF_migration` seeds. |
| `Ct * omega^2` thrust | present in project-owned smoke | `thrust[i] = lift_coefficient * omega[i] * omega[i]`; coefficient is seeded, not identified truth. |
| yaw reaction torque | present in project-owned smoke | `yaw_reaction_moment[i] = yaw_direction[i] * moment_constant * thrust[i]`; yaw convention still needs later validation before allocation claims. |
| rotor-center arm moment | present in project-owned smoke and base plant geometry | Project smoke computes `r x F`; official `QuadChassis` also applies per-rotor world forces at `Dronefixed1..4` rotor centers. |
| rotor gyroscopic moment | missing / follow-up | Not implemented in this minimum slice. |
| body drag | missing / follow-up | Not implemented in this minimum slice. |
| angular damping | missing / follow-up | Not implemented in this minimum slice. |

## Parameter Provenance

| Parameter | Current value / source |
|---|---|
| rotor centers | `source=user-reviewed DAE screw-pair fit`, mapped to MWORKS `Dronefixed1..4` order. |
| mass | `1.0 kg`, `source=SDF_migration`; not identified Sunray150 truth. |
| lift coefficient | `0.000854858`, `source=SDF_migration`; Sunray motor constant scaled by `rotorVelocitySlowdownSim^2` for MWORKS visual rotor speed. |
| yaw moment ratio | `0.06`, `source=SDF_migration`; Gazebo/Sunray seed, not ULog identified. |
| motor lag constants | `timeConstantUp=0.0125`, `timeConstantDown=0.025`, `source=SDF_migration`. |

## MCP Gate Results

Minimal Sysplorer MCP probe:

```text
session_manager(action=probe): ok=true
dedicated_sysplorer_port=49152
cached_driver_probe_ok=true
```

Loaded files:

```text
References/MWORKS/QuadrotorModel/package.mo: OpenModelFile ok=true
Models/QuadrotorExperiments/package.mo: OpenModelFile ok=true
```

Model checks:

```text
check_model QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke: ok=true
check_model QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke: ok=true
check_model QuadrotorModel.Mechanics.QuadChassis: ok=true
```

Smoke simulations:

| Model | Probe | End value |
|---|---|---:|
| `QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke` | `dynamics.hover_thrust_error` | `1.7763568394002505e-15 N` |
| `QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke` | `dynamics.total_moment_body[3]` | `0.06153801695664962 N.m` |

## File Integrity

Targeted Git diff checks before writing this evidence:

```text
References/MWORKS/QuadrotorModel/package.mo: baseline_diff=clean
Models/QuadrotorExperiments/package.mo: experiments_diff=clean
```

No official baseline edit was performed. No ROS2, UE, PositionCommand recorder,
20 Hz adapter, planner runtime, or live echo downlink runtime was started.

## Next Gates

1. Connect the checked actuator/rotor structure into a project-owned plant
   wrapper or chassis interface without replacing the official baseline.
2. Validate yaw sign and PX4/Sunray motor order before allocation or fault
   isolation claims.
3. Add rotor gyroscopic moment, body drag, and angular damping as separate
   source-labeled follow-up modules.
4. Keep every future controller or closed-loop claim gated by MWORKS MCP
   `check_model` before `simulate_model` and a run manifest that names consumed
   traces and source labels.
