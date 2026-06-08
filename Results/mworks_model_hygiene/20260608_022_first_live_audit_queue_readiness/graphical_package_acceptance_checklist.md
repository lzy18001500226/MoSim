# Graphical And Package Acceptance Checklist

This checklist is for the next serialized live task after PMO/CoAgentOps proves an approved reusable no-start MWORKS/Sysplorer route.

## Preconditions

- Consume the latest CoAgentOps activation/window-health patrol when available.
- If activation/login/license state is being accepted, use foreground or maximized target-main-window visual evidence; background `PrintWindow` evidence is auxiliary only.
- Prove attach-existing/no-start route before any package browser, load, check, result viewer, or layout work.
- Record before/after process, window, and port inventory; reject the run if a new `mworks.exe`, Sysplorer/Syslab window, or shared port appears.
- Do not call `session_manager(action="health")` or `ensure` as reusable-session proof.

## Package Browser Items

- Root `MoSimQuadrotorModel` package shows exactly the 12 expected categories.
- `MoSimQuadrotorModel.Dynamics` shows the 12 formal Dynamics public entries from the 021 queue.
- `QuadrotorExperiments.DynamicsUpgrade` shows the 12 public compatibility aliases, while implementation-only sibling files remain non-public.
- `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` is visible/load/check queued without claiming identified parameter truth.

## Diagram/Layout/Wiring Items

- The open diagram title/class matches the target row.
- Full-window capture shows the whole target diagram surface, not only a cropped helper/proxy area.
- Blank or white blocks are classified by source or marked as blockers; do not silently accept them.
- Crossed wires, hidden lines, overlapping annotations, unreadable labels, and ambiguous port directions are recorded as layout risks.
- Any Smart Layout writeback, model save, or package/source edit requires a new PMO task.

## Stop Conditions

- Demo, login, activation, authorization, license error, GUI error-report, visible unknown MWORKS/Sysplorer/Syslab window.
- Helper/proxy surface obstructs the target review and cannot be classified without PMO/CoAgentOps intervention.
- Package/browser/check/layout work would require closing, restarting, opening a new window, saving, or clicking login/activation/error-report UI.
- Approved attach-existing/no-start route is missing or the route creates a new process, window, or port.

## Claims Not Allowed From This Checklist

- Final package-browser acceptance.
- `check_model` or simulation success.
- Graphical/layout/wiring acceptance.
- Controller performance, planner readiness, runtime acknowledgement, mission success, or closed-loop success.
