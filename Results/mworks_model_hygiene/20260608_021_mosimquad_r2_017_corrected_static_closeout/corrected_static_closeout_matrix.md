# Corrected R2 017 Static Findings

021 corrected closeout result: `passed_static_corrected_closeout`.

## What Was Corrected

- Old R2 017 reported `12` unresolved extends rows and `12` unresolved alias chains.
- The current 021 parser indexes embedded declarations, child package directories, and sibling `.mo` classes.
- The 12 `QuadrotorExperiments.DynamicsUpgrade.Sunray150*` targets are present as same-directory `.mo` implementation files.
- They are intentionally not public `package.order` entries; they are hidden implementation targets behind the 12 public `DynamicsUpgrade` aliases.

## Current Static Result

- Corrected unresolved extends count: `0`.
- Corrected unresolved Dynamics alias chain count: `0`.
- Corrected 017 false-positive alias chain count: `12`.
- `MoSimQuadrotorModel/package.order` has `12` root categories and no duplicates.
- Current ordered MoSim child entries across category packages: `68`.

## Claim Boundary

This is static source/package reasoning only. It does not prove live package-browser acceptance, graphical/layout/wiring acceptance, `check_model`, `SimulateModel`, controller performance, planner readiness, runtime acknowledgement, mission success, or closed loop.
