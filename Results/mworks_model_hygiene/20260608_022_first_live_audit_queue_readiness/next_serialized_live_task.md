# Next Serialized Live Task

## Required PMO/CoAgentOps Task Before R2 Live Audit

Authorize and validate an attach-existing/no-start MWORKS/Sysplorer route.

Minimum acceptance:

1. Record process/window/port inventory before attach.
2. Enumerate existing Sysplorer shared ports without starting Sysplorer.
3. Bind to an explicit existing port using an approved `attach_existing` or equivalent no-start route.
4. Prove `driver_ready=true`, cached driver present, selected existing port recorded, and startup attempted/started are false.
5. Record process/window/port inventory after attach.
6. Confirm no new `mworks.exe`, Sysplorer/Syslab main/helper window, or shared port was created.
7. Stop on demo/login/license/authorization/error-report/visible-unknown evidence.

## First R2 Business Task After Route Proof

Run a package-browser-only audit for:

- `MoSimQuadrotorModel` root category visibility.
- `MoSimQuadrotorModel.Dynamics` 12 formal entries.
- `QuadrotorExperiments.DynamicsUpgrade` 12 compatibility aliases.
- `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` visibility.

Do not combine this with Smart Layout, model edits, broad `check_model`, simulation, result-viewer, controller performance, planner readiness, runtime acknowledgement, mission success, or closed-loop claims.
