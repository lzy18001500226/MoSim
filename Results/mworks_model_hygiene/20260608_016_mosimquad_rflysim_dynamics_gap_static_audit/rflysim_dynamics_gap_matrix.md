# RflySim-Like Dynamics Gap Matrix

Task: PMO-MWORKS-R1-MOSIMQUAD-RFLYSIM-DYNAMICS-GAP-STATIC-AUDIT-20260608-016

Scope: static source audit only. No MWORKS window, MCP, check_model,
SimulateModel, Smart Layout, screenshot, package edit, parameter edit, or
solver work was performed in this task.

## Summary

`MoSimQuadrotorModel.Dynamics` is currently a formal alias surface over
`QuadrotorExperiments.DynamicsUpgrade`. The project-owned implementation already
covers the minimum RflySim-like free-flight rotor force/moment chain:

```text
signed visual rotor speed command
  -> first-order lagged omega
  -> Ct * omega^2 thrust
  -> yaw reaction moment
  -> rotor-center r x F moment
  -> wrapper total force/torque
  -> explicit MultiBody WorldForceAndTorque adapter
```

The main remaining structure gaps are a normalized actuator/PWM-to-speed map,
rotor gyroscopic moment, body aerodynamic drag, angular damping, and scenario
parameter layers for fault/contact/dynamic modification. Current parameters are
source-labeled seed values, not identified Sunray150 truth.

## Gap Matrix

| Feature | Static classification | Current implementation | Source anchors | Gap / boundary | Next minimal action |
|---|---|---|---|---|---|
| Formal MoSim dynamics surface | Implemented as alias surface | `MoSimQuadrotorModel.Dynamics` aliases formal entries to `QuadrotorExperiments.DynamicsUpgrade`. | `Models/MoSimQuadrotorModel/Dynamics/package.mo:5-48`; `Models/QuadrotorExperiments/DynamicsUpgrade/package.mo:6-58` | Alias surface is not final migration of implementation files. | Keep alias for compatibility until live check and package migration plan approve file moves. |
| Command-to-speed mapping | Partially implemented | Core exposes `motor_command[4]` as signed visual rotor speed command in rad/s, with sign convention parameters. | `Sunray150RflyStyleRotorDynamics.mo:22-28`; wrapper command side at `Sunray150DynamicsWrapperSurface.mo:13-20` | No normalized PWM/actuator command to speed target map, min/max throttle gate, saturation, or voltage model. | Add a separate project-owned actuator-command mapper before the rotor core; keep current signed-speed command as the internal boundary. |
| Motor first-order lag | Implemented structurally | Asymmetric up/down time constants select `motor_tau`, and `der(omega) = (motor_command - omega) / motor_tau`. | `Sunray150RflyStyleRotorDynamics.mo:10-13`, `42-43` | Time constants are SDF migration seeds, not ULog/bench identified. | Preserve source label; later replace only from PX4 ULog/bench evidence. |
| Ct * omega^2 thrust | Implemented structurally | Per-rotor thrust is `lift_coefficient * omega^2`; wrapper also exposes command-side algebraic thrust. | `Sunray150RflyStyleRotorDynamics.mo:6`, `31-32`, `44`, `50`; `Sunray150DynamicsWrapperSurface.mo:15-16`, `39`, `49` | Ct is a visual-speed coefficient seed derived from SDF motorConstant and slowdown convention. | Keep coefficient and speed convention explicit; do not mix with RflySim numeric Ct. |
| Cm / yaw reaction torque | Implemented structurally | `yaw_reaction_moment = yaw_direction * moment_constant * thrust`; yaw component enters `total_moment_body[3]`. | `Sunray150RflyStyleRotorDynamics.mo:8`, `24-25`, `33-34`, `45`, `48`, `53`; wrapper at `Sunray150DynamicsWrapperSurface.mo:17-18`, `40`, `52`, `54-55` | Moment ratio and sign order are source-labeled and need PX4/motor-order validation before allocation claims. | Retain sign/order gate variables; next live task should read yaw gate variables but not claim controller performance. |
| Rotor-center r x F moment | Implemented structurally | Uses per-rotor center and thrust to compute roll/pitch moments plus yaw reaction. | `Sunray150RflyStyleRotorDynamics.mo:16-21`, `35-36`, `46-53`; wrapper command side at `Sunray150DynamicsWrapperSurface.mo:19-20`, `41-43`, `50-52` | Rotor centers are DAE geometry anchors only; geometry does not identify mass/inertia/thrust/yaw parameters. | Keep DAE centers as geometry; verify order/sign in live smoke before integrating into larger plant. |
| Explicit physical wrench application | Implemented structurally | `Sunray150PhysicalWrenchFrameAdapter` applies wrapper force/torque with `WorldForceAndTorque` to a MultiBody body. | `Sunray150PhysicalWrenchFrameAdapter.mo:31-58` | This 016 task did not run live check/sim. Prior 005 live evidence exists but is not revalidated here. | Use this as the next live boundary only after reusable-session MCP attach is fixed. |
| Rotor gyroscopic moment | Missing | No source term found using rotor inertia, body rates, rotor direction, and omega. | Negative static search in `DynamicsUpgrade` for gyro terms; reference workflow `identify_quadrotor_parameters.md:793` | Optional RflySim-like module; should follow validated thrust/yaw/r x F chain. | Add as disabled/tunable optional module after live hover/yaw/wrench checks are stable. |
| Body aerodynamic drag | Missing | No translational drag force term in current `DynamicsUpgrade` source. | Negative static search in `DynamicsUpgrade` for drag terms; reference workflow `identify_quadrotor_parameters.md:794` | Drag coefficients not identified; DAE/visual data cannot supply them. | Add a wrapper-level optional drag module with null/source labels; require ULog translational excitation before truth claims. |
| Angular damping | Missing | No rotational damping moment term in current `DynamicsUpgrade` source. | Negative static search in `DynamicsUpgrade` for damping terms; reference workflow `identify_quadrotor_parameters.md:795` | Coefficients not identified. | Add after basic physical wrench chain; tune only as scenario seed until identification. |
| Contact / ground support | Out of current wrapper scope | Official baseline has `TouchModel`, but `DynamicsUpgrade` free-flight wrapper does not include contact. | `References/MWORKS/QuadrotorModel/package.mo:2122-2252`; workflow `identify_quadrotor_parameters.md:796` | Contact should not be buried in the nominal free-flight rotor core. | Keep as separate takeoff/landing/contact scenario wrapper. |
| Fault / dynamic parameter layers | Missing from core, should remain separate | Current core has fixed source-labeled seed parameters. | workflow `identify_quadrotor_parameters.md:797`, `861-869` | Do not hard-code fault/dynamic parameter changes into nominal core. | Add scenario-level modifiers or wrappers after nominal chain is validated. |
| Parameter identification status | Not implemented as truth | Source labels distinguish DAE geometry and SDF migration seeds. | `identify_quadrotor_parameters.md:34-45`, `250-251`, `908-915`; DAE manifest lines 5-22 | No PX4 ULog/sysid evidence bundle is present for identified Sunray150 truth. | Keep all non-geometry values source-labeled until ULog/bench bundle exists. |
| Live verification state for 016 | Not run by design | 016 is static-only. | Task packet `mworks_live_gate.live_mworks_touched=false` | No new check_model, simulation, result, layout, or activation claim is made. | Next live task must wait for CoAgentOps/PMO reusable-session attach route or write blocker. |

## Static Conclusion

The current project-owned dynamics structure has moved beyond the official
force-only `QuadChassis` baseline for the narrow rotor dynamics chain, because
it statically implements motor lag, thrust, yaw reaction torque, rotor-center
moments, wrapper totals, and an external wrench adapter. It is not yet a full
RflySim/CopterSim plant, and it is not a validated or identified Sunray150
truth model.
