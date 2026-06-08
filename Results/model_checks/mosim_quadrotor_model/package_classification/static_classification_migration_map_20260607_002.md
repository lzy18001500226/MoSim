# MoSimQuadrotorModel static classification migration map 002

Request: `PMO-MWORKS-R2-MOSIMQUAD-PACKAGE-CLASSIFICATION-RENAME-PLAN-20260607-002`

Scope: static file/package organization only after current-turn GUI sentinel and background screenshot preflight. No MWORKS MCP, no `check_model`, no simulation, no Smart Layout, no GUI review, and no `.mo` source edits were performed.

## Current Package Tree Audit

`Models/MoSimQuadrotorModel/package.order` exposes 11 formal categories:

1. `Baseline`
2. `Dynamics`
3. `Missions`
4. `Controllers`
5. `Robustness`
6. `Planning`
7. `SceneTrace`
8. `System`
9. `Formation`
10. `Support`
11. `LegacyCompatibility`

`Models/MoSimQuadrotorModel/package.mo` is a formal project-owned package skeleton using `Modelica`, `QuadrotorModel`, and `QuadrotorExperiments`. Its category packages are currently alias/wrapper entry points, not completed namespace migration.

`Models/QuadrotorExperiments/package.order` exposes 11 compatibility categories and no longer lists the old flat sibling classes at top level. The directory still contains 94 flat sibling `.mo` model files, which must remain as compatibility load paths until scenario YAML, scripts, docs, and targeted MWORKS checks migrate.

## Classification Map

| Legacy source family | Formal target package | Migration action |
|---|---|---|
| Official Example1/2/3 AWFF/INDI/L1/LinearMPC and figure-eight missions | `MoSimQuadrotorModel.Missions` | Keep current extends alias first, then migrate scenario YAML to formal names after targeted checks. |
| Embedded AWFF, improved PID, enhanced PID baselines | `MoSimQuadrotorModel.Controllers` | Keep controller baseline aliases; do not move embedded controller definitions before live package/check evidence. |
| Mass, wind, QPNMPC safety, rotor-loss, fault-allocation scenarios | `MoSimQuadrotorModel.Robustness` | Migrate in robustness batches; old flat paths remain aliases for report reproducibility. |
| Quintic reference, navigation display, open-blocks and corridor-gate planning | `MoSimQuadrotorModel.Planning` | Migrate planner/map review configs after alias check; do not claim planner readiness. |
| UE Factory/Derelict accepted scene smokes | `MoSimQuadrotorModel.SceneTrace.AcceptedScenes` | Keep trace scene aliases; future live checks must not claim Factory trace consumption unless separately proven. |
| Factory trace isolation Iso01-Iso30 and FactoryLite | `MoSimQuadrotorModel.SceneTrace.Isolation` | Preserve Iso chain order; future work can promote individual passing isolation nodes, not full Factory closure. |
| Sunray150 rotor dynamics, wrapper surface, wrench adapter and smoke tests | `MoSimQuadrotorModel.Dynamics` | Promote dynamics wrappers only after batch check_model/simulation evidence; do not edit official baseline. |
| Complete-system graphical model and failure-mode wrappers | `MoSimQuadrotorModel.System.Architecture` | Requires later R2 graphical review for missing wires, disconnected blocks, routing readability, and active-window screenshots. |
| Perception, flight controller, mission computer, supervisor, battery, ESC, AWFF, motor, sensor modules | `MoSimQuadrotorModel.System.Modules` | Keep as module aliases; future true migration must preserve Sysblock ports and line annotations. |
| Trace references, lookup smoke, echo MCP state smoke | `MoSimQuadrotorModel.Support` | Keep as support aliases; echo evidence remains non-live unless a later live task proves it. |
| Formation triangle figure-eight LinearMPC | `MoSimQuadrotorModel.Formation` | Keep as P2 formation alias pending separate formation validation. |
| Full `QuadrotorExperiments` pool | `MoSimQuadrotorModel.LegacyCompatibility` | Retain until all current configs/scripts/docs use formal paths and selected old names are explicitly retired. |

## Rename Batches

Batch 0 is the current safe state: no source edits, no real moves, only static classification planning.

Batch 1 should validate `MoSimQuadrotorModel.Baseline.*` and `MoSimQuadrotorModel.Dynamics.*` aliases, then update only the references that pass targeted MWORKS checks.

Batch 2 should migrate official mission and controller config references from `QuadrotorExperiments.*` to `MoSimQuadrotorModel.Missions.*` and `MoSimQuadrotorModel.Controllers.*`.

Batch 3 should migrate robustness scenarios: mass, wind, QPNMPC safety, rotor-loss, L1 allocation, LinearMPC online allocation, and multi-fault isolation.

Batch 4 should migrate planning and scene-trace aliases, keeping Factory isolation claims scoped to individual Iso evidence.

Batch 5 should migrate system architecture, system modules, support models, and formation aliases after graphical/layout review.

Batch 6 may retire selected legacy aliases only after configs, scripts, docs, evidence references, and targeted MWORKS checks no longer depend on the old flat names.

## Future Graphical Review Plan

Every future live review must start with fresh GUI sentinel plus background screenshot evidence, then use phase screenshots after package load/check or graphical review. R2 should inspect: package browser category visibility, wrong active window, license/login/error prompts, missing wires, disconnected blocks, unreadable routing, overlapping icons/text, hidden helper-window risk, and Sysblock port consistency.

Priority graphical review candidates:

1. `MoSimQuadrotorModel.System.Architecture.CompleteSystemGraphical`
2. `MoSimQuadrotorModel.System.Modules.*`
3. `MoSimQuadrotorModel.SceneTrace.Isolation.Iso01` through `Iso30`
4. `MoSimQuadrotorModel.Planning.NavigationDisplay` and OpenBlocks/ColorMap review
5. `MoSimQuadrotorModel.Dynamics.WrapperSurface` and `PhysicalWrenchAdapter`

Claim boundary: this static map is not model-check evidence, simulation evidence, graphical/layout acceptance, controller performance, planner readiness, live runtime ack, Factory trace consumption, plant tracking, parameter identification, or closed-loop evidence.
