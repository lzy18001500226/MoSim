# Sunray150 Dynamics Upgrade Checkpoint

Date: 2026-06-05 CST

Status: experimental structure upgrade, not identified Sunray150 truth.

## Scope

This checkpoint adds a project-owned experimental dynamics core under:

```text
Models/QuadrotorExperiments/package.mo
Models/QuadrotorExperiments/Sunray150DynamicsUpgradeSmoke.mo
```

The official baseline `QuadrotorModel.Mechanics.QuadChassis` is not replaced.

## Current QuadChassis Audit

Current `QuadrotorModel.Mechanics.QuadChassis` already applies per-rotor
`WorldForce` at each DAE-reviewed rotor center. Therefore the rotor-arm moment
from `r x F` is present in the multibody plant through force application at
`Dronefixed1..4`.

Missing or weak in the current base plant:

- no explicit yaw reaction torque source was found;
- no explicit RflySim-style command-to-speed first-order motor lag module was
  found at the plant input boundary;
- no explicit rotor gyroscopic moment was added in this checkpoint;
- no body drag or angular damping was added in this checkpoint.

## Added Experimental Structure

`Sunray150RflyStyleRotorDynamics` implements:

```text
motor command -> first-order lagged omega
omega -> Ct * omega^2 thrust
thrust -> Cm * thrust yaw reaction moment
rotor center -> r x F arm moment
```

Two smoke models are included:

```text
QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke
QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke
```

## Parameter Provenance

| Field | Value/source |
|---|---|
| rotor centers | `source=user-reviewed DAE screw-pair fit` |
| mass/inertia seed | remains `source=SDF_migration` |
| lift coefficient | `source=SDF_migration`, Sunray `motorConstant` scaled by `rotorVelocitySlowdownSim^2` |
| yaw moment ratio | `source=SDF_migration`, Sunray `momentConstant=0.06` |
| motor lag constants | `source=SDF_migration`, Sunray `timeConstantUp=0.0125`, `timeConstantDown=0.025` |

No field in this checkpoint is promoted to `source=PX4_ULog_sysid`.

Engineering continuation rule: these Sunray/YunZong open-source seed values
are acceptable for structure checks, hover/yaw smoke tests, and controller
interface debugging. They are not accepted as measured Sunray150 flight truth
until a PX4 ULog or bench-identification bundle replaces the `SDF_migration`
labels.

## Open Issues

1. Confirm MWORKS positive yaw torque convention with a Sysplorer smoke
   simulation before using yaw response as controller evidence.
2. Confirm PX4/Sunray motor order and spin direction before using the yaw
   direction vector in allocation or fault-isolation claims.
3. Embed the tested torque/lag structure into a proper chassis or wrapper only
   after the standalone smoke checks pass.
4. Keep gyro, drag, and angular damping as separate follow-up modules after
   hover/yaw/step response is stable.

## Verification

Source label: `source=MWORKS_MCP` for the model checks and smoke simulations
below.

Sysplorer MCP status:

```text
session_manager(action=probe): ok=true
session_manager(action=ensure): ok=true, dedicated_sysplorer_port=49152
```

Loaded files:

```text
References/MWORKS/QuadrotorModel/package.mo
Models/QuadrotorExperiments/package.mo
```

Model checks:

```text
QuadrotorModel.Mechanics.QuadChassis: check_model ok=true
QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke: check_model ok=true
QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke: check_model ok=true
```

Smoke simulation results:

| Model | Probe | End value |
|---|---|---:|
| `Sunray150DynamicsUpgradeHoverSmoke` | `dynamics.hover_thrust_error` | `1.7763568394002505e-15 N` |
| `Sunray150DynamicsUpgradeYawStepSmoke` | `dynamics.total_thrust` | `9.810193917515512 N` |
| `Sunray150DynamicsUpgradeYawStepSmoke` | `dynamics.hover_thrust_error` | `0.00019391751551189884 N` |
| `Sunray150DynamicsUpgradeYawStepSmoke` | `dynamics.total_moment_body[1]` | `9.810193917515753e-05 N.m` |
| `Sunray150DynamicsUpgradeYawStepSmoke` | `dynamics.total_moment_body[2]` | `7.628541126475374e-05 N.m` |
| `Sunray150DynamicsUpgradeYawStepSmoke` | `dynamics.total_moment_body[3]` | `0.06153801695664962 N.m` |

Static test:

```text
python -m pytest Scripts/tests/test_sunray150_dynamics_upgrade_model.py -q
```

Result: passed.

WeChat notification:

The start packet was written to:

```text
Results/coagent_gateway/packets/sunray150_dynamics_upgrade_start_20260605.json
```

The bounded send attempt failed before cc-connect delivery with:

```text
OSError: [WinError 193] %1 is not a valid Win32 application
```

Local gateway health still reported `ok=true` for session/socket/context state,
so the blocker is the Windows-side adapter launch path for the cc-connect
script, not the current dynamics model work.

## 2026-06-06 PMO Recheck

Scope: answer the current PMO question and prepare the next implementation
slice without changing the official baseline.

Confirmed current parameter policy:

- DAE/Blender-reviewed rotor centers are already present in
  `QuadrotorModel.Mechanics.QuadChassis` as `Dronefixed1..4.r`.
- Mass, inertia, lift coefficient, yaw moment ratio, motor lag constants, drag,
  damping, and controller gains remain Sunray/Gazebo/SDF migration seeds or
  open modeling work; they are not identified Sunray150 truth.
- The user-approved working assumption is to keep those YunZong/Sunray/Gazebo
  seed values for now while model structure and wrapper integration are checked.

Current `QuadChassis` implementation detail:

```text
speedSensor.w -> product w*w -> gain lift_cofficient -> WorldForce.force[3]
WorldForce.frame_b -> Dronefixed1..4.frame_b
Dronefixed1..4.frame_a -> body.frame_b
```

This means rotor-center arm moments are represented by the multibody force
application at the accepted rotor centers. The base plant still does not expose
a complete Gazebo/RflySim-style actuator chain:

- no command-to-speed mapping block was found at the chassis input boundary;
- no first-order motor lag was found in the base plant;
- no explicit yaw reaction torque was found;
- no explicit rotor gyroscopic moment was found;
- no body drag or angular damping module was found.

Rechecked evidence:

```text
source=MWORKS_MCP
session_manager(action=probe): ok=true, dedicated_sysplorer_port=49152
model_manager(load_file Models/QuadrotorExperiments/package.mo): ok=true, cached=true
check_model QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke: ok=true
check_model QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke: ok=true
```

Next implementation slice:

```text
Create a project-owned wrapper/chassis that connects the checked
Sunray150RflyStyleRotorDynamics motor-lag/yaw-torque core to the existing
QuadChassis or a derived chassis interface. Do not overwrite the official
QuadrotorModel.Mechanics.QuadChassis baseline. First acceptance remains
hover/yaw/step response with source labels, then controller interface checks.
```
