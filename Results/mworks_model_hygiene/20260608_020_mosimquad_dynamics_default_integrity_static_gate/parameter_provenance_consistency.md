# Parameter Provenance Consistency

Task: `PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-DEFAULT-INTEGRITY-STATIC-GATE-20260608-020`

## Geometry

`MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` records
`rotor_center_mworks_dronefixed[4,3]` as user-reviewed DAE/Blender screw-pair
assembly geometry:

- `[0.053745, -0.053740, -0.014052]`
- `[0.053746,  0.053759, -0.014052]`
- `[-0.053761, 0.053760, -0.014052]`
- `[-0.053761, -0.053739, -0.014052]`

The claim boundary says this is geometry/assembly only.

## Non-Geometry Seeds

The record keeps these as source-labeled non-identified seeds:

- `mass_kg=1.0`
- `body_inertia_diagonal_kg_m2={0.0085,0.0085,0.012}`
- `sdf_motor_constant=8.54858e-06`
- `rotor_velocity_slowdown_sim=10`
- `mworks_lift_coefficient=0.000854858`
- `yaw_moment_ratio_seed=0.06`
- `motor_time_constant_up_s=0.0125`
- `motor_time_constant_down_s=0.025`
- optional drag/damping/gyro flags false and coefficient seeds zero

## Integrity Decision

The current source keeps the required boundary:

DAE/Blender rotor centers are geometry evidence only. Mass, inertia, Ct/Cm,
motor lag, drag, damping, gyro, PWM/RPM/ESC mapping, and controller values are
not Sunray150 identified truth and require future PX4 ULog, bench, weighing, or
validated system-identification evidence before promotion.
