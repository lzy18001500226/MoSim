# Resource Lock And Serialization Plan

## Lock

Use exactly one reusable existing MWORKS/Sysplorer main session for future live work. Do not run R1 and R2 live MWORKS tasks in parallel.

## Serialized Order

1. CoAgentOps/PMO proves a reusable attach-existing/no-start/foreground route.
2. CoAgentOps/PMO records before/after process, window, and port inventory with no new MWORKS/Sysplorer process/window/port.
3. R1 or a separately scoped live validation runs package load/check gates where requested.
4. R2 runs package-browser screenshot review for root, Dynamics, DynamicsUpgrade, and Parameters provenance.
5. R2 runs diagram/layout/wiring review only for targets that passed package/load/check gates.

## Parallel Work Allowed

Static evidence preparation and checklist refinement can proceed without MWORKS. Live package-browser, `check_model`, result-viewer, and graphical review cannot run in parallel because they share the same MWORKS/Sysplorer session and window surface.

## Blocker Propagation

If any live phase observes demo/login/license/authorization/error-report/visible-unknown state, or if the route starts a new session, the live queue stops and returns an infrastructure blocker. Do not continue with solver, layout, Smart Layout, or model edits.
