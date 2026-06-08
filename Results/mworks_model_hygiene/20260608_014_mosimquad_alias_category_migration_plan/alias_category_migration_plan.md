# Alias Category Migration Plan

Request: `PMO-MWORKS-R2-MOSIMQUAD-ALIAS-CATEGORY-MIGRATION-PLAN-20260608-014`

This is a static-only package-surface migration plan. It creates explicit wrapper entries under `MoSimQuadrotorModel` for the six categories that 013 left as alias-only: `Missions`, `Robustness`, `Planning`, `Formation`, `Support`, and `LegacyCompatibility`.

## Department Local Goal

Converge the remaining alias-only MoSimQuadrotorModel categories into browsable local wrapper/package surfaces while preserving every legacy `QuadrotorExperiments` implementation file and load path.

## Category Decisions

| Category | Source surface | 014 static action | Local entries | Remaining blocker |
|---|---|---:|---:|---|
| `Missions` | `QuadrotorExperiments.OfficialScenarios` | explicit wrapper surface + package.order | 15 | live check_model/package-browser/layout deferred |
| `Robustness` | `QuadrotorExperiments.RobustFaultScenarios` | explicit wrapper surface + package.order | 12 | live check_model/package-browser/layout deferred |
| `Planning` | `QuadrotorExperiments.PlanningScenarios` | explicit wrapper surface + package.order | 7 | live check_model/package-browser/layout deferred |
| `Formation` | `QuadrotorExperiments.FormationScenarios` | explicit wrapper surface + package.order | 1 | live check_model/package-browser/layout deferred |
| `Support` | `QuadrotorExperiments.SupportModels` | explicit wrapper surface + package.order | 4 | live check_model/package-browser/layout deferred |
| `LegacyCompatibility` | `QuadrotorExperiments` | explicit wrapper surface + package.order | 1 | full legacy flattening deliberately deferred |

## Claim Boundary

014 may claim only static alias-category package-surface convergence and migration planning. It does not claim live Sysplorer package-browser acceptance, graphical/layout/wiring acceptance, `check_model`, simulation, controller performance, planner readiness, runtime acknowledgement, mission success, or closed loop.
