# Next Minimal Dynamics Upgrade Plan

Task: PMO-MWORKS-R1-MOSIMQUAD-RFLYSIM-DYNAMICS-GAP-STATIC-AUDIT-20260608-016

This is an implementation plan only. No model source was edited by 016.

## Recommended Order

1. Live revalidation gate after MCP attach recovery
   - Reuse the existing MWORKS/Sysplorer session only.
   - Load project packages with targeted `model_manager(load_file,
     force_reload=true)` when allowed by a future live task.
   - Run `check_model` on the formal `MoSimQuadrotorModel.Dynamics` entries.
   - Run only the shortest eligible Hover/Yaw smoke after all checks pass.
   - Read thrust, yaw moment, r x F moment, and wrench application variables.

2. Add explicit actuator command mapper
   - Keep `Sunray150RflyStyleRotorDynamics.motor_command` as signed visual
     rotor speed internal command.
   - Add a separate project-owned mapper for controller/actuator command to
     visual speed target.
   - Include saturation/min/max gates and source labels.
   - Do not change official baseline parameters.

3. Keep current rotor dynamics core as the nominal chain
   - Preserve command lag, Ct*omega^2 thrust, yaw reaction torque, and r x F.
   - Keep current SDF/DAE provenance labels.
   - Use gate variables for motor order and yaw direction.

4. Add optional modules only after the nominal chain is live-stable
   - Rotor gyroscopic moment module: disabled by default or clearly
     source-labeled.
   - Translational body drag module: wrapper-level tunable module.
   - Angular damping module: wrapper-level tunable module.
   - Contact/ground support: separate scenario wrapper, not nominal core.
   - Fault/dynamic parameter changes: scenario wrappers, not hard-coded base
     constants.

## Minimal Future Live Evidence

The next live task should produce:

- `check_model` results for the selected formal entries.
- Minimal HoverSmoke and YawStepSmoke result locators if check passes.
- Result probes for:
  - `total_thrust`
  - `hover_thrust_error`
  - `total_moment_body[1..3]`
  - `yaw_reaction_moment[1..4]`
  - `rotor_arm_moment[1..4,1..3]`
  - wrapper force/torque application errors when using the wrench adapter.
- Claim boundary that excludes controller performance, plant tracking,
  planner readiness, runtime ack, mission success, parameter identification,
  graphical/layout acceptance, and closed loop.

## Blocker Conditions For Implementation

Write a blocker instead of implementing if:

- The next boundary requires editing `References/MWORKS/QuadrotorModel`.
- The implementation needs unidentified mass/inertia/Ct/Cm/lag/drag/damping
  values to be promoted as truth.
- Motor command domain is not explicit: PWM, normalized actuator command,
  rad/s visual speed, physical rotor speed, and sign convention are mixed.
- Reusable MWORKS session attach is still unsafe for live check/simulation.
- Any live task observes demo/login/authorization/error-report or unknown
  blocking GUI state.
