# First Batch Audit Target Matrix

Status: readiness matrix prepared, live execution blocked.

Source queue: `Results/mworks_model_hygiene/20260608_021_mosimquad_r2_017_corrected_static_closeout/future_live_audit_queue_update.json`

## Live Route Gate

The first executable graphical/package audit needs an approved reusable no-start MWORKS/Sysplorer route. The available CoAgentOps route packet is still design-only, so 022 must not call `session_manager health/ensure`, package browser, `check_model`, Smart Layout, or any GUI operation.

## First Batch

| Order | Target | Acceptance Focus | Owner Split | Blocker |
|---|---|---|---|---|
| 1 | `MoSimQuadrotorModel` | Root package browser shows 12 categories; `Parameters` appears after `Dynamics`. | R2 package-browser observation only after route proof. | Missing approved no-start route, category count/order mismatch, helper/unknown/demo/login/error surface. |
| 2 | `MoSimQuadrotorModel.Dynamics` | 12 formal Dynamics entries visible: `RotorActuatorCore`, `HoverSmoke`, `YawStepSmoke`, `WrapperSurface`, `ActuatorCommandMapper`, `ActuatorMappedWrapperSurface`, `OptionalDampingGyroLayer`, `WrapperHoverSmoke`, `WrapperYawStepSmoke`, `PhysicalWrenchAdapter`, `PhysicalWrenchHoverSmoke`, `PhysicalWrenchYawStepSmoke`. | R2 observes package/browser/layout; R1 or separate live task owns `check_model`. | Missing entry, unapproved live route, diagram ambiguity requiring forbidden GUI operation. |
| 3 | `QuadrotorExperiments.DynamicsUpgrade` | 12 compatibility aliases visible; implementation-only `Sunray150*.mo` siblings stay out of public `package.order`. | R2 package-browser observation; R1 live check if assigned. | Compatibility alias missing or hidden implementation class exposed unexpectedly. |
| 4 | `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` | `Parameters` and provenance entry visible/load/check queued. | R2 visibility; R1/separate live task for check. | Treating visibility as parameter identification or needing live route before approval. |
| 5 | R2 graphical/layout/wiring review queue | Full-window diagram review for blank/white blocks, crossing lines, hidden ports, unreadable labels, and result-window only if later evidence exists. | R2 only after package/load/check gates. | Package/load/check incomplete, Smart Layout writeback needed, or no approved live route. |

## Claim Boundary

This file is not package-browser acceptance, graphical acceptance, layout acceptance, `check_model`, simulation, controller performance, planner readiness, runtime acknowledgement, mission success, or closed-loop evidence.
