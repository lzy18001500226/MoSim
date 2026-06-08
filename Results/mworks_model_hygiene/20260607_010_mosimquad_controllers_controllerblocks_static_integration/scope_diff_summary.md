# Scope Diff Summary

Request: `PMO-MWORKS-R2-MOSIMQUAD-CONTROLLERS-CONTROLLERBLOCKS-STATIC-INTEGRATION-20260607-010`

## 010 Model Package Edits

- `Models/MoSimQuadrotorModel/package.mo`: added `QuadrotorControllerBlocks` to the static `uses(...)` dependency annotation because `MoSimQuadrotorModel.Controllers` now extends classes from that package.
- `Models/MoSimQuadrotorModel/Controllers/package.mo`: preserved `extends QuadrotorExperiments.ControllerBaselines;` and added 7 Chinese-described formal category package entries that extend `QuadrotorControllerBlocks.<Category>`.
- `Models/MoSimQuadrotorModel/Controllers/package.order`: added the 7 formal controller category entries in the same order as `Models/QuadrotorControllerBlocks/package.order`.

## Preserved Compatibility

- Existing `QuadrotorExperiments.ControllerBaselines` compatibility inheritance remains in `MoSimQuadrotorModel.Controllers`.
- Existing `QuadrotorExperiments` folder/category migration changes are present in the worktree as prior context; 010 did not edit that package.

## Out Of Scope

- No controller implementation `.mo` files under `Models/QuadrotorControllerBlocks` were edited.
- No `within` clauses were added to controller implementation files.
- No files were moved, deleted, renamed, staged, committed, or pushed.
- No MWORKS/Sysplorer/Syslab GUI/MCP/check_model/simulation/Smart Layout/diagram writeback was used.

## Static Validation Snapshot

- Formal category count: 7.
- Source child controller wrapper count: 19.
- Main controller implementation hash mismatches vs 009 guard: 0.
- `package.order` exact match: True.
