# Default Behavior Preservation

Task: `PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-DEFAULT-INTEGRITY-STATIC-GATE-20260608-020`

## Optional Layer Defaults

`Sunray150OptionalDampingGyroLayer` keeps all optional effects disabled or zero
by default:

- `enable_rotor_gyro=false`
- `enable_body_drag=false`
- `enable_angular_damping=false`
- `rotor_polar_inertia[4]={0,0,0,0}`
- `body_drag_coefficient[3]={0,0,0}`
- `angular_damping_coefficient[3]={0,0,0}`

## Preserved Chain

The optional layer computes:

- `base_force_body={0,0,mapped_wrapper.total_thrust}`
- `base_moment_body=mapped_wrapper.total_moment_body`
- `total_force_body[j]=base_force_body[j]+optional_force_body[j]`
- `total_moment_body[j]=base_moment_body[j]+optional_moment_body[j]`

Because the enable flags are false and the coefficients are zero by default,
the optional terms are zero by construction. The exposed
`default_disabled_force_delta` and `default_disabled_moment_delta` are static
probes for this preservation boundary.

## Existing Dynamics Chain

020 did not edit the motor lag, thrust, yaw reaction moment, or rotor-center
moment sources. The preserved default chain remains:

normalized command mapper -> signed visual rotor speed -> existing wrapper
motor command -> first-order rotor lag -> `Ct*omega^2` thrust -> yaw reaction
moment -> rotor-center moment -> physical wrench adapter when used.

## Boundary

This is a static source claim only. It does not prove live `check_model`,
simulation, `.msr` result probes, or graphical acceptance.
