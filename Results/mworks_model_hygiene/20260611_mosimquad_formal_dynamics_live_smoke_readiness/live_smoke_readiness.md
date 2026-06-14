# Formal Dynamics Live Smoke Readiness

Status: `ready_but_blocked_by_gui`
Live gate state: `blocked_by_current_gui_surface`

This is a static readiness guard. It does not call MWORKS, Sysplorer, MCP, `check_model`, or `SimulateModel`.

## Current GUI Classifier

```json
{
  "status": "incident_detected",
  "error_kind": "gui_blocked",
  "license_state_hint": "upgrade_model_surface_blocked",
  "upgrade_model_window_count": 1,
  "all_window_license_gate": "blocked"
}
```

## Scenarios

- `Config/scenarios/diagnostics/mosimquad_dynamics_hover_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.HoverSmoke`
- `Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_hover_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke`
- `Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke`
- `Config/scenarios/diagnostics/mosimquad_dynamics_rotor_effectiveness_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke`
- `Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_hover_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke`
- `Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_yaw_step_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke`
- `Config/scenarios/diagnostics/mosimquad_dynamics_yaw_step_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.YawStepSmoke`

## Claim Boundary

- This readiness guard validates executable preparation only.
- It does not run MWORKS, check_model, SimulateModel, result extraction, controller performance, mission success, or closed_loop.
- Live execution remains blocked while current_gui_classifier reports upgrade_model_surface_blocked.

## Findings

- none
