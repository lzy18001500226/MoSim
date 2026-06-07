# QuadrotorExperiments Organization Implementation Strategy

Request: `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-ORGANIZATION-20260606-004`

This is a read-only plan for a later write task. It does not edit `package.mo`, `package.order`, or any `.mo` file.

## Core Diagnosis

The current package already has category packages, but they are compatibility alias packages. The flat legacy classes still appear because `Models/QuadrotorExperiments/package.order` lists 11 category packages followed by 104 flat entries. The category aliases mostly extend `QuadrotorExperiments.<FlatClass>`, so deleting or moving the flat class definitions now would break the category entries and historical evidence paths.

Static audit found 100 of 104 flat entries already have category alias coverage. The four alias gaps are `FactoryTraceIso22SensorDisplayReconnectSmoke`, `FactoryTraceIso28ActuatorToWrenchBridgeSmoke`, `FactoryTraceIso29ExternalFrameWrenchBoundarySmoke`, and `FactoryTraceIso30ExternalBodyStateBoundarySmoke`; all four are protected evidence-chain models, not deletion candidates.

`package.order` only controls browser display order. Removing a line from `package.order` may reduce display clutter in the library browser, but it does not delete, hide from all lookup paths, unload, or migrate a class definition. True organization requires a staged compatibility strategy.

## Recommended Write-Phase Strategy

### Phase 0: Freeze And Reference Search

- Keep all flat paths loadable.
- Run a full project reference search excluding `Results/tmp` as advisory history and including configs, scripts, docs, formal result packets, and current scenario files.
- Produce a machine-readable path migration allowlist for each class whose canonical path will change.
- Keep `FactoryTraceIso*`, Sunray dynamics/wrench, complete-system, planning, scene-trace, support, and formation entries protected until R1 or PMO explicitly retires their evidence chains.

### Phase 1: Fill Missing Category Aliases

- Add missing category aliases for flat entries that are currently in `package.order` but not represented by a category alias.
- Highest-priority missing aliases are `FactoryTraceIso22SensorDisplayReconnectSmoke`, `FactoryTraceIso28ActuatorToWrenchBridgeSmoke`, `FactoryTraceIso29ExternalFrameWrenchBoundarySmoke`, and `FactoryTraceIso30ExternalBodyStateBoundarySmoke`.
- Keep each alias extending the existing flat class during this phase.
- Do not move real definitions yet.

### Phase 2: Browser Cleanup Without Breaking Compatibility

- Option A, conservative: keep categories first and leave flat entries loadable as public compatibility paths until a release-style verification pass is complete.
- Option B, practical: remove selected flat entries from `package.order` only after confirming Sysplorer still loads them by full path and category aliases still check. This is display cleanup only, not deletion.
- Do not remove flat entries for classes still named in current configs, scripts, formal result packets, or R1 active evidence.

### Phase 3: True Subpackage Migration, Separate Task

- Create real subdirectories only in a dedicated write task following the Modelica package style guide.
- Each subpackage requires its own `package.mo` and `package.order`.
- Move one low-risk family at a time, update `within` paths, add backwards-compatible flat aliases, then run targeted static checks and R1-approved `check_model` gates.
- Do not start with FactoryTrace or DynamicsUpgrade because current evidence chains depend heavily on old flat paths.

### Phase 4: Deprecation Review

- A class can become a deprecated/hide candidate only after full reference search, category alias coverage, and model-check validation.
- Deletion is a separate PMO-approved task and must prove no configs, scripts, docs, result packets, package aliases, or active evidence depend on the old path.

## Minimum Verification Gates For Later Write Task

1. Static parse: every `package.order` entry resolves to a sibling `.mo`, embedded definition, or real subpackage.
2. Alias parse: every category alias extends a valid target.
3. Reference migration: configs/scripts/docs/formal result packets either retain flat path intentionally or are updated to the new canonical path.
4. Sysplorer load/check: run through R1 or an approved MWORKS evidence owner, not this static R2 task.
5. GUI/manual review: schedule separately and do not run concurrently with R1 simulation evidence.
6. Regression protection: preserve old flat names as aliases until at least one full release-style verification pass confirms category paths are stable.

## Recommended First Write Slice

Start with a no-move, no-delete cleanup: add missing category aliases for current protected entries and optionally adjust `package.order` display order only after confirming loadability. Do not migrate real definitions or delete flat entries in the first write slice.
