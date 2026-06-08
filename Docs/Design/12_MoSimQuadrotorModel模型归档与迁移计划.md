# 12 MoSimQuadrotorModel模型归档与迁移计划

Status: active migration plan, 2026-06-08 CST. R2 023/024 static
organization findings are now the canonical migration-plan baseline.

Purpose: move useful project-owned quadrotor experiments into a formal package
without breaking existing scenario YAML, result scripts, reports, or evidence
references in one large rename.

## 1. Decision

The project-owned formal quadrotor package is:

```text
Models/MoSimQuadrotorModel/package.mo
```

Package roles:

| Package | Role |
|---|---|
| `QuadrotorModel` | Official/upstream baseline and regression dependency. Do not destructively rewrite. |
| `MoSimQuadrotorModel` | Formal MoSim/Sunray150 model package. New formal work should enter here. |
| `QuadrotorExperiments` | Legacy experiment pool and compatibility layer during migration. |
| `QuadrotorControllerBlocks` | Controller block library consumed through `MoSimQuadrotorModel.Controllers`; do not treat private backup/upgrade files as public package surface. |

`MoSimQuadrotorModel` is allowed to start as an alias/extends layer. That is a
controlled compatibility step, not final acceptance of every model. A class
becomes canonical only after its new name, source labels, scenario/script
references, and MWORKS checks are complete.

## 2. Category Tree

| Category | Chinese role | First source |
|---|---|---|
| `Baseline` | 官方基线适配 | `QuadrotorModel.Examples.*`, `QuadrotorModel.Mechanics.QuadChassis` |
| `Dynamics` | Sunray150动力学升级 | `QuadrotorExperiments.DynamicsUpgrade` |
| `Parameters` | 参数来源与标定记录 | `MoSimQuadrotorModel.Parameters` |
| `Missions` | 正式任务场景 | `QuadrotorExperiments.OfficialScenarios` |
| `Controllers` | 控制器基线与对比 | `QuadrotorExperiments.ControllerBaselines` |
| `Robustness` | 鲁棒、故障、安全与扰动 | `QuadrotorExperiments.RobustFaultScenarios` |
| `Planning` | 规划与地图场景 | `QuadrotorExperiments.PlanningScenarios` |
| `SceneTrace` | UE场景trace与显示隔离 | `QuadrotorExperiments.SceneTraceScenarios`, `TraceIsolation` |
| `System` | 系统级图形和硬件抽象 | `QuadrotorExperiments.SystemArchitecture`, `SystemModules` |
| `Formation` | 编队扩展 | `QuadrotorExperiments.FormationScenarios` |
| `Support` | 支撑/trace/MCP工具模型 | `QuadrotorExperiments.SupportModels` |
| `LegacyCompatibility` | 旧入口兼容 | full `QuadrotorExperiments` alias |

Current static package surface from R2 023:

- `MoSimQuadrotorModel/package.order` has 12 top-level categories:
  `Baseline`, `Dynamics`, `Parameters`, `Missions`, `Controllers`,
  `Robustness`, `Planning`, `SceneTrace`, `System`, `Formation`, `Support`,
  and `LegacyCompatibility`.
- `QuadrotorExperiments` remains the legacy implementation and compatibility
  source during migration. R2 023 counted 11 legacy category directories and
  about 140 implementation `.mo` files excluding `package.mo`.
- `QuadrotorControllerBlocks` remains a separate controller library with 19
  public flat controller `.mo` files and 6 private backup/upgrade `.mo`
  files. Formal browsing should go through `MoSimQuadrotorModel.Controllers`,
  while private backup/upgrade files stay out of the public package surface.
- Static package classification does not prove package-browser visibility,
  diagram layout, wiring quality, `check_model`, simulation, controller
  performance, or closed-loop behavior.

## 3. Rename Policy

Use descriptive names under the new package and keep old names as aliases until
the migration batch is verified.

Example pattern:

```text
QuadrotorExperiments.Example1AWFFSysblockClosedLoop
  -> MoSimQuadrotorModel.Missions.Example1AWFF

QuadrotorExperiments.Sunray150RflyStyleRotorDynamics
  -> MoSimQuadrotorModel.Dynamics.RotorActuatorCore

QuadrotorModel.Examples.Example1
  -> MoSimQuadrotorModel.Baseline.OfficialExample1
```

Do not rename by broad search/replace. Each batch must update:

1. package tree and `package.order`;
2. scenario YAML references;
3. scripts that load/check/simulate the class;
4. docs and result references where the new name is authoritative;
5. compatibility aliases for old evidence names;
6. targeted MWORKS `check_model` or simulation evidence.

## 3.1 Legacy Disposition Policy

R2 023 divides the old `QuadrotorExperiments` surface into migration,
reference, diagnostic, review-helper, and support buckets. The rule is to keep
legacy names alive until the new formal entry has both static references and
the required live check evidence.

| Legacy surface | Canonical target | Disposition |
|---|---|---|
| `OfficialScenarios` | `MoSimQuadrotorModel.Missions` | Migrate to formal mission surface after live load/check evidence. |
| `ControllerBaselines` | `MoSimQuadrotorModel.Controllers` plus legacy baseline entry | Keep as baseline/reference; do not present PID/AWFF comparison files as new control contributions. |
| `RobustFaultScenarios` | `MoSimQuadrotorModel.Robustness` | Migrate in nested batches for mass, wind, safety, and rotor-loss scenarios. |
| `RobustFaultScenarios.PIDBaselines` | `MoSimQuadrotorModel.Robustness.PIDBaselines` | Keep as comparison baseline, not as improved-control evidence. |
| `PlanningScenarios` | `MoSimQuadrotorModel.Planning` | Migrate closed-loop planning scenarios; keep display/color-map review helpers separate from controller acceptance. |
| `SceneTraceScenarios` | `MoSimQuadrotorModel.SceneTrace.AcceptedScenes` | Migrate only after live scene/package review; do not claim UE runtime acceptance from static wrappers. |
| `TraceIsolation` | `MoSimQuadrotorModel.SceneTrace.Isolation` | Keep as diagnostic ladder; do not expose `FactoryTraceIso01..30` as primary user mission entries. |
| `DynamicsUpgrade` | `MoSimQuadrotorModel.Dynamics` | Formal source migration belongs to separate scoped source tasks; no broad source move in this plan. |
| `SystemArchitecture` and `SystemModules` | `MoSimQuadrotorModel.System` | Alias first, then R2 live graphical/port/wiring review before canonical acceptance. |
| `SupportModels` | `MoSimQuadrotorModel.Support` | Keep as tool/support surface, not as mission/control-result surface. |
| `FormationScenarios` | `MoSimQuadrotorModel.Formation` | Migrate after single-UAV mission, robustness, and planning gates are stable. |

Rejected or non-primary public surfaces:

- `FactoryTraceIso01..30` are trace-isolation diagnostics, not formal mission
  scenarios.
- `PlanningNavigationDisplay` and
  `Sunray150PlanningOpenBlocksColorMapReview` are review/display helpers, not
  controller or planner acceptance evidence.
- White/blank package-browser or diagram tiles cannot be accepted by static
  source review. They require a future R2 live graphical audit after a
  validated reusable no-start MWORKS route exists.
- `QuadrotorControllerBlocks` backup/upgrade files remain private recovery
  material unless a future scoped task explicitly promotes one.

## 4. Batch Order

1. Baseline adapter: verify `MoSimQuadrotorModel.Baseline.*` loads after
   `QuadrotorModel`.
2. Dynamics source surface: continue narrow source tasks such as
   `Dynamics.RotorActuatorCore` without moving legacy implementations until
   each wrapper/source boundary is explicit.
3. Missions authority references: migrate YAML/scripts/docs authoritative
   references from `QuadrotorExperiments.OfficialScenarios` to
   `MoSimQuadrotorModel.Missions` only after live package load/check succeeds.
4. Robustness nested review: split Mass20, WindGust, Safety, and RotorLoss
   batches; keep PID baselines labelled as baselines.
5. Planning helper separation: migrate closed-loop planning scenarios and keep
   `NavigationDisplay` / color-map helpers in review/support roles.
6. SceneTrace diagnostic folding: keep `TraceIsolation` as a diagnostic ladder
   and live-review only representative isolation stages before any broader
   acceptance claim.
7. System graphical audit: queue `CompleteSystemGraphical`, GPS dropout,
   battery-low, offboard-loss, mission-failure, geofence-breach, and system
   module diagrams for R2 live layout/wiring review after a no-start attach
   route is approved.
8. Formation migration: start after single-UAV mission/robustness/planning
   surfaces are stable.
9. Legacy cleanup: only after all current configs/scripts use
   `MoSimQuadrotorModel`, decide which old flat names remain permanently for
   report reproducibility.

## 5. Acceptance Gates

For each migration batch:

- Static gate: no broken package names, missing `package.order` entries,
  duplicate class definitions, or unreviewed public/private package-surface
  leaks.
- Documentation gate: migration disposition, Chinese category wording, and
  old-to-new mapping are updated in this plan and the task evidence.
- Live MWORKS gate when live work is actually used: follow the current
  CoAgentOps/PMO activation and reusable-window route in `AGENTS.md` and
  `Docs/Workflows/new_conversation_context.md`; do not start or attach through
  a route that may silently create a new Sysplorer window.
- Live gate when used: `check_model` for every new canonical class in the
  batch; simulation/metrics where the batch claims behavior.
- Reference gate: changed YAML/scripts/docs do not point to retired names.
- Evidence gate: return packet lists actual `.mo`/`package.mo` edits,
  `check_model`/simulation/layout evidence, and old-to-new class mapping.

JSON packets, ledger rows, and progress notes alone do not count as model
migration progress.

## 6. Next Live Audit Queue

The first future R2 live graphical/package audit queue from R2 023 is:

1. `MoSimQuadrotorModel` root package browser: confirm the 12 top categories
   are visible and that old flat legacy clutter does not dominate the surface.
2. `MoSimQuadrotorModel.Missions`: confirm official mission wrappers are
   distinguishable by Example1/2/3 and trajectory variant.
3. `MoSimQuadrotorModel.Robustness`: confirm PID baselines, rotor-loss nested
   packages, mass/wind/safety entries, and user-facing labels are not
   confusing.
4. `MoSimQuadrotorModel.Planning`: confirm closed-loop scenarios are separated
   from display/review helpers.
5. `MoSimQuadrotorModel.SceneTrace`: confirm accepted-scene and isolation
   labels do not make the diagnostic ladder look like the main product flow.
6. `MoSimQuadrotorModel.System.Architecture.CompleteSystemGraphical`: open the
   diagram and review blank/white surface risk, wiring, ports, subsystem
   layout, and labels. Do not run Smart Layout writeback unless a future task
   explicitly permits it.
7. `QuadrotorExperiments` legacy root: confirm legacy category packages and
   compatibility aliases do not clutter the public browser.

This queue is not live acceptance. It is blocked until PMO approves a reusable
MWORKS/Sysplorer main-window route that proves no new window/session startup.
