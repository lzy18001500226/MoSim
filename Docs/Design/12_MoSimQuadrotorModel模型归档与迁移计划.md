# 12 MoSimQuadrotorModel模型归档与迁移计划

Status: active migration plan, 2026-06-07 CST.

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

`MoSimQuadrotorModel` is allowed to start as an alias/extends layer. That is a
controlled compatibility step, not final acceptance of every model. A class
becomes canonical only after its new name, source labels, scenario/script
references, and MWORKS checks are complete.

## 2. Category Tree

| Category | Chinese role | First source |
|---|---|---|
| `Baseline` | 官方基线适配 | `QuadrotorModel.Examples.*`, `QuadrotorModel.Mechanics.QuadChassis` |
| `Dynamics` | Sunray150动力学升级 | `QuadrotorExperiments.DynamicsUpgrade` |
| `Missions` | 正式任务场景 | `QuadrotorExperiments.OfficialScenarios` |
| `Controllers` | 控制器基线与对比 | `QuadrotorExperiments.ControllerBaselines` |
| `Robustness` | 鲁棒、故障、安全与扰动 | `QuadrotorExperiments.RobustFaultScenarios` |
| `Planning` | 规划与地图场景 | `QuadrotorExperiments.PlanningScenarios` |
| `SceneTrace` | UE场景trace与显示隔离 | `QuadrotorExperiments.SceneTraceScenarios`, `TraceIsolation` |
| `System` | 系统级图形和硬件抽象 | `QuadrotorExperiments.SystemArchitecture`, `SystemModules` |
| `Formation` | 编队扩展 | `QuadrotorExperiments.FormationScenarios` |
| `Support` | 支撑/trace/MCP工具模型 | `QuadrotorExperiments.SupportModels` |
| `LegacyCompatibility` | 旧入口兼容 | full `QuadrotorExperiments` alias |

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

## 4. Batch Order

1. Baseline adapter: verify `MoSimQuadrotorModel.Baseline.*` loads after
   `QuadrotorModel`.
2. Dynamics upgrade: verify `MoSimQuadrotorModel.Dynamics.*` aliases and then
   migrate the real wrapper implementation.
3. Missions/controllers: migrate official Example1/2/3 and controller
   comparison aliases.
4. Robustness/planning: migrate fault, wind, safety, planning, and map review
   scenarios after their configs are updated.
5. SceneTrace/system/formation/support: migrate remaining trace isolation,
   complete-system graphical models, formation, and helper models.
6. Legacy cleanup: only after all current configs/scripts use
   `MoSimQuadrotorModel`, decide which old flat names remain permanently for
   report reproducibility.

## 5. Acceptance Gates

For each migration batch:

- MWORKS department preflight: activation sentinel plus background screenshot
  classification in the same turn.
- Static gate: no broken package names, missing `package.order` entries, or
  duplicate class definitions.
- Live gate when used: `check_model` for every new canonical class in the
  batch; simulation/metrics where the batch claims behavior.
- Reference gate: changed YAML/scripts/docs do not point to retired names.
- Evidence gate: return packet lists actual `.mo`/`package.mo` edits,
  `check_model`/simulation/layout evidence, and old-to-new class mapping.

JSON packets, ledger rows, and progress notes alone do not count as model
migration progress.
