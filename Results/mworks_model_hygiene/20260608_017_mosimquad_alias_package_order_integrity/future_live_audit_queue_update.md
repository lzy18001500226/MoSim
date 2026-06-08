# Future Live Audit Queue Update

Static 017 outcome: no live MWORKS/Sysplorer/Syslab action was performed. The next live audit queue must be refreshed before package-browser/check_model work because R1 017/018/019 changed the formal surface.

## Priority Updates

1. `MoSimQuadrotorModel` package-browser visibility: root now has 12 ordered categories, with `Parameters` inserted after `Dynamics`.
2. `MoSimQuadrotorModel.Dynamics` package-browser visibility: audit the 12 ordered formal aliases, especially `ActuatorCommandMapper`, `ActuatorMappedWrapperSurface`, and `OptionalDampingGyroLayer`.
3. `QuadrotorExperiments.DynamicsUpgrade` compatibility browser visibility: confirm the same 12 compatibility aliases still display and resolve.
4. `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`: package-browser visibility plus record-only `check_model`/load gate when live MWORKS is authorized.
5. Graphical/layout review remains deferred: these source/package-order checks do not prove diagram readability, missing wires, package-browser acceptance, or simulation readiness.

## Resource Lock

Use one reusable MWORKS/Sysplorer session only. Serialize R1 live check_model/smoke work and R2 package-browser/layout review. Stop immediately on demo/login/authorization/error-report/unknown live evidence.

## Claim Boundary

This queue update is static planning only. It is not package-browser acceptance, graphical/layout acceptance, wiring acceptance, `check_model`, `SimulateModel`, controller performance, planner readiness, runtime acknowledgement, mission success, or closed-loop evidence.
