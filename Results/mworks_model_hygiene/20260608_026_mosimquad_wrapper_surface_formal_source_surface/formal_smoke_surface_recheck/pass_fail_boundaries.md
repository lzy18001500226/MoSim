# Formal Smoke Surface Pass/Fail Boundaries

## Global Boundaries

- Future live work must complete all queued `check_model` targets before any `SimulateModel` smoke.
- Any license, login, activation, authorization, GUI error, visible unknown, unavailable, or unknown state is a blocker.
- Missing expected result variables in a future live result is a smoke-surface blocker.
- This static 023 artifact does not claim `check_model`, simulation, graphical acceptance, controller performance, runtime ack, or closed loop.
- Parameter provenance remains source-labeled: geometry is DAE/Blender assembly evidence; non-geometry values are seeds, not identified truth.

## Target Boundaries

- `MoSimQuadrotorModel.Dynamics.RotorActuatorCore`: check_model must accept command lag, Ct*omega^2 thrust, yaw reaction torque, rotor-center moment, and exposed total force/moment variables.
- `MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper`: future live result probe must show normalized command saturation and signed visual rotor speed outputs are present; no PWM/RPM truth is claimed.
- `MoSimQuadrotorModel.Dynamics.WrapperSurface`: future live check must preserve wrapper command-side and lagged force/moment observability before any plant integration claim.
- `MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface`: future live probe may claim only normalized command to signed visual speed to wrapper feedthrough, not closed-loop control.
- `MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer`: future live probe must see default-disabled deltas at zero or write a blocker; 023 does not claim live numeric deltas.
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter`: future live validation may claim only wrapper force/torque application to the explicit minimal MultiBody body, not full plant integration.
- `MoSimQuadrotorModel.Dynamics.HoverSmoke`: simulate only after all check_model targets pass; probe hover thrust/moment variables without claiming controller or plant performance.
- `MoSimQuadrotorModel.Dynamics.YawStepSmoke`: simulate only after all check_model targets pass; yaw response observation is a source-level smoke, not dynamic yaw acceptance.
- `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke`: probe wrapper hover observability only; no full plant, controller, or Factory trace claim.
- `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke`: probe wrapper yaw moment variables only; no dynamic yaw transient acceptance.
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke`: probe explicit adapter/body force/torque variables only; no QuadChassis or full plant closure.
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke`: probe explicit physical-wrench yaw application only; no full plant tracking or closed loop claim.
