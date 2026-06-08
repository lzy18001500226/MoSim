# Parameter Provenance Boundary

Task: PMO-MWORKS-R1-MOSIMQUAD-RFLYSIM-DYNAMICS-GAP-STATIC-AUDIT-20260608-016

This task is a static audit. It does not upgrade any parameter provenance and
does not identify Sunray150 physical truth.

## Current Source Classes

| Parameter or structure | Current source class | Boundary |
|---|---|---|
| Rotor centers | user-reviewed DAE screw-pair geometry | Geometry/assembly only. Valid for rotor-center placement and r x F geometry; not evidence for mass, inertia, thrust, yaw, lag, drag, damping, gyro, or controller parameters. |
| Mass | SDF migration seed | Current `1.0 kg` value is not measured Sunray150 takeoff mass. |
| Inertia | SDF migration seed | Current `Ixx=0.0085`, `Iyy=0.0085`, `Izz=0.012` seed is payload/battery sensitive and not ULog identified. |
| Rotor lift coefficient / Ct equivalent | SDF migration seed with visual-speed scaling | Current MWORKS `0.000854858` is a visual rotor speed coefficient; it depends on `rotorVelocitySlowdownSim` convention. |
| Yaw moment ratio / Cm equivalent | SDF migration seed | Current `0.06` moment ratio is not ULog identified and sign/order must be validated before allocation claims. |
| Motor lag constants | SDF migration seed | Current up/down time constants are source-labeled seeds, not motor bench identification. |
| Spin/yaw direction signs | SDF-to-MWORKS order convention | Useful for smoke gates only until PX4 motor order / actuator mapping is confirmed. |
| Rotor gyro moment | missing | Requires rotor inertia, body rates, rotor speeds, and sign conventions. |
| Body drag | missing | Requires translational excitation and identification or conservative scenario seed. |
| Angular damping | missing | Requires angular-rate excitation and identification or conservative scenario seed. |
| Fault/contact/dynamic parameter layers | not nominal-core truth | Should be scenario wrappers/modifiers, not hard-coded into nominal rotor core. |

## Do-Not-Promote Rules

- Do not copy RflySim numeric parameters into Sunray150 truth.
- Do not treat DAE/Blender geometry as mass, inertia, Ct, Cm, motor lag, drag,
  damping, or gyro identification.
- Do not label current seed parameters as `source=PX4_ULog_sysid` without a
  saved ULog/sysid bundle, selected windows, output YAML, and MWORKS
  verification result.
- Do not silently overwrite the official `References/MWORKS/QuadrotorModel`
  baseline.
- Do not use a successful static audit as check_model, simulation, controller,
  planner, runtime, or closed-loop evidence.

## Evidence Needed To Upgrade Provenance

Minimum evidence before any `identified Sunray150 truth` claim:

1. PX4 ULog or bench data for hover/throttle excitation.
2. PX4 ULog or bench data for roll/pitch/yaw rate excitation.
3. Translational excitation logs for drag if drag is claimed.
4. Exact vehicle mass with battery and payload.
5. Motor/ESC mapping, PX4 motor order, PWM/actuator normalization, and RPM or
   tachometer evidence when available.
6. Project-owned identified-parameter YAML with provenance, units, selected
   windows, and fit report.
7. Targeted MWORKS hover/yaw/step verification after applying identified values
   to a project-owned model variant.
