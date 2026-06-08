# Model Ownership Classification

Request: `PMO-MWORKS-R2-MOSIMQUAD-STATIC-CLASSIFICATION-LIVE-AUDIT-QUEUE-20260608-015`

This is static-only evidence. It classifies current package ownership and future audit surfaces without opening MWORKS, calling MCP, or editing model implementation files.

## Ownership Summary

- `References/MWORKS/QuadrotorModel`: official_upstream_baseline; policy: read_only_do_not_destructively_rewrite; use: baseline adapters under MoSimQuadrotorModel.Baseline and regression reference.
- `Models/MoSimQuadrotorModel`: formal_project_package_surface; policy: formal wrapper/package surface; real migration requires later scoped task; use: 11 top-level categories and package/order surfaces for user navigation and future audit.
- `Models/QuadrotorExperiments`: legacy_experiment_pool_and_compatibility_source; policy: preserve old paths and flat compatibility aliases until migration batches pass live gates; use: actual legacy implementations and categorized source surfaces for experiments/smokes.
- `Models/QuadrotorControllerBlocks`: controller_block_library_and_package_shell; policy: preserve flat controller implementations and backup dirs; formal controller surface via category package aliases; use: controller block categories consumed by MoSimQuadrotorModel.Controllers.

## Formal MoSimQuadrotorModel Categories

| Order | Category | Role | Source/dependency | Entries | State |
|---:|---|---|---|---:|---|
| 1 | `MoSimQuadrotorModel.Baseline` | 官方基线适配 | `QuadrotorModel` | 4 | formal wrapper aliases only |
| 2 | `MoSimQuadrotorModel.Dynamics` | Sunray150动力学升级 | `QuadrotorExperiments.DynamicsUpgrade` | 9 | formal wrapper aliases only |
| 3 | `MoSimQuadrotorModel.Missions` | 正式任务场景 | `QuadrotorExperiments.OfficialScenarios` | 15 | formal wrapper aliases only |
| 4 | `MoSimQuadrotorModel.Controllers` | 控制器基线与对比 | `QuadrotorExperiments.ControllerBaselines + QuadrotorControllerBlocks` | 7 | formal wrapper/category aliases only |
| 5 | `MoSimQuadrotorModel.Robustness` | 鲁棒、故障、安全与扰动 | `QuadrotorExperiments.RobustFaultScenarios` | 12 | formal wrapper aliases only |
| 6 | `MoSimQuadrotorModel.Planning` | 规划与地图场景 | `QuadrotorExperiments.PlanningScenarios` | 7 | formal wrapper aliases only |
| 7 | `MoSimQuadrotorModel.SceneTrace` | UE场景trace与显示隔离 | `QuadrotorExperiments.SceneTraceScenarios + TraceIsolation` | 2 | aggregate package aliases |
| 8 | `MoSimQuadrotorModel.System` | 系统级图形和硬件抽象 | `QuadrotorExperiments.SystemArchitecture + SystemModules` | 2 | aggregate package aliases |
| 9 | `MoSimQuadrotorModel.Formation` | 编队扩展 | `QuadrotorExperiments.FormationScenarios` | 1 | formal wrapper aliases only |
| 10 | `MoSimQuadrotorModel.Support` | 支撑/trace/MCP工具模型 | `QuadrotorExperiments.SupportModels` | 4 | formal wrapper aliases only |
| 11 | `MoSimQuadrotorModel.LegacyCompatibility` | 旧入口兼容 | `QuadrotorExperiments` | 1 | compatibility aggregate only |

## Legacy Pools

- `Models/QuadrotorExperiments`: 11 category directories, 109 category `.mo` files observed; root flat compatibility aliases remain in `package.mo`.
- `Models/QuadrotorControllerBlocks`: 19 flat controller `.mo` files and 5 backup directories preserved; category package shell remains the public controller surface.
- `References/MWORKS/QuadrotorModel`: official upstream baseline remains read-only; formal adapters live under `MoSimQuadrotorModel.Baseline`.

## Boundary

No live package-browser, layout, wiring, check_model, simulation, controller performance, planner readiness, runtime ack, mission success, or closed_loop claim is made by this artifact.
