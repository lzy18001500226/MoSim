# Optional Dynamics Boundary

Task: PMO-MWORKS-R1-MOSIMQUAD-OPTIONAL-DAMPING-GYRO-STATIC-LAYER-20260608-018

## New Formal Entry

Formal project surface:

```text
MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer
```

Compatibility surface:

```text
QuadrotorExperiments.DynamicsUpgrade.OptionalDampingGyroLayer
```

Implementation source:

```text
Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150OptionalDampingGyroLayer.mo
```

## Inputs

- `normalized_actuator_command[4]`: forwarded to the existing 017 mapper.
- `body_velocity_body[3]`: body-frame translational velocity for optional drag.
- `body_angular_velocity_body[3]`: body-frame angular velocity for optional
  rotor gyro and angular damping terms.

## Outputs

Base outputs preserved from the 017 mapped wrapper:

- `base_force_body = {0, 0, mapped_wrapper.total_thrust}`
- `base_moment_body = mapped_wrapper.total_moment_body`

Optional outputs:

- `rotor_gyro_total_moment_body[3]`
- `body_drag_force_body[3]`
- `angular_damping_moment_body[3]`
- `optional_force_body[3]`
- `optional_moment_body[3]`

Final boundary outputs:

- `total_force_body = base_force_body + optional_force_body`
- `total_moment_body = base_moment_body + optional_moment_body`

## Equations And Source Labels

Rotor gyro:

```text
rotor_angular_momentum_body_z[i]
  = rotor_polar_inertia[i] * gyro_axis_sign[i] * omega[i]

rotor_gyro_moment_body[i,1]
  = gyro_convention_sign * body_angular_velocity_body[2]
    * rotor_angular_momentum_body_z[i]

rotor_gyro_moment_body[i,2]
  = -gyro_convention_sign * body_angular_velocity_body[1]
    * rotor_angular_momentum_body_z[i]
```

This is disabled unless `enable_rotor_gyro=true`; rotor inertia defaults to
zero and remains an unidentified seed.

Body drag:

```text
body_drag_force_body[j] = -body_drag_coefficient[j] * body_velocity_body[j]
```

This is disabled unless `enable_body_drag=true`; coefficients default to zero
and are not identified Sunray150 truth.

Angular damping:

```text
angular_damping_moment_body[j]
  = -angular_damping_coefficient[j] * body_angular_velocity_body[j]
```

This is disabled unless `enable_angular_damping=true`; coefficients default to
zero and are not identified Sunray150 truth.

## Static Preservation Gate

At defaults:

```text
optional_force_body = {0,0,0}
optional_moment_body = {0,0,0}
default_disabled_force_delta = 0
default_disabled_moment_delta = 0
```

This means the existing 017 mapper-wrapper-core force/moment boundary is not
changed unless a future scenario explicitly enables optional terms and provides
source-labeled coefficients.

## Required Future Live Gate

Future live MWORKS validation must run only after the reusable no-start attach
route is proven. It should check/load the new formal entry and inspect
`default_disabled_force_delta`, `default_disabled_moment_delta`,
`optional_force_norm`, and `optional_moment_norm` before any plant/controller
claim.
