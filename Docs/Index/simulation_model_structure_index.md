# Simulation Model Structure Index

> Status: canonical single-root model map, 2026-07-25 CST.

## 1. One Formal Entry

审查、复现和 MWORKS 载入只使用一个入口：

```text
Models/MoSimQuadrotorModel/package.mo
```

该包已经包含基线 Plant、控制器、场景、实验执行器和 LiveIntegration 资源。不得再加载外部 Plant 包、旧兼容包或单独的控制器文件作为第二根；这样会产生重复定义或让审查者无法判断实际来源。

本索引只说明文件所有权与打开路径，不声明 `check_model`、仿真、控制性能、代码生成或 ROS/Gazebo 运行成功。

## 2. Top-Level Map

| Path | Role | Review rule |
|---|---|---|
| `Models/MoSimQuadrotorModel/` | 唯一正式 Modelica 实现根 | 打开根目录的 `package.mo`，再按命名空间选择模型。 |
| `Config/scenarios/` | 场景和实验配置 | 配置中的模型类必须指向正式根。 |
| `Config/control_platform/` | 控制方案、入口映射和接口配置 | 冻结的 48 个活动条目、47 个 MWORKS Control Profile、46 条当前 MWORKS 路线和冠军测试壳状态以机器可读映射为准。 |
| `Scripts/mworks/` | MWORKS 检查、执行、结果提取脚本 | 先读对应工作流，再运行最小检查。 |
| `Scripts/quality/` | 结构和证据质量门 | `consolidate_mosimquad_model_root.py --check` 检查单根布局。 |
| `Results/` | 结果、日志、截图和审查包 | 结果只能证明其明确记录的证据层。 |
| `Docs/Cache/` | 自动恢复副本和历史迁移材料 | 不得作为 MWORKS 加载目录或当前模型来源。 |

## 3. Canonical Package Map

```text
MoSimQuadrotorModel
  Parameters/         source-labeled Sunray150 and runtime parameter sets
  Vehicle/            physical plant, actuators, sensors, resources and examples
  Control/            baseline, graphical, robust, learning and adapter modules
  Experiment/         typed runners, templates, probes and scenario test shells
  Guidance/           trajectory, planning and formation reference modules
  Deployment/         live I/O, code-generation and transport resource surface
  Visualization/      graphical scenario and diagnostic visualization models
  Common/             shared limits and support models
```

| Namespace | Use it for | Do not infer |
|---|---|---|
| `MoSimQuadrotorModel.Parameters.*` | 参数来源、版本和虚拟 PX4/Gazebo 对齐记录 | 参数已由实物飞行辨识确认。 |
| `MoSimQuadrotorModel.Vehicle.Examples.*` | 官方机体/任务基线和资源审查 | 已完成控制器优化或部署验证。 |
| `MoSimQuadrotorModel.Control.*` | 控制器源、Sysblock、图形化核心、接口、分配器与适配器 | 图形化核心已具备整机闭环。 |
| `MoSimQuadrotorModel.Experiment.Runners.*` | 输出边界和正式测试壳 | 与 PX4 运行时 owner 等价。 |
| `MoSimQuadrotorModel.Experiment.Templates.*` | 单机正式任务模板 | 其他场景的性能结论。 |
| `MoSimQuadrotorModel.Experiment.Scenarios.Robustness.*` | 扰动、安全、故障实验 | 已完成 FDI/FTC 闭环。 |
| `MoSimQuadrotorModel.Guidance.Planning.*` | 路径/轨迹/障碍场景 | 在线规划或真实传感闭环。 |
| `MoSimQuadrotorModel.Guidance.Formation.*` | 多机参考与编队场景 | 分布式通信或集群避障已验证。 |
| `MoSimQuadrotorModel.Deployment.*` | 实时 I/O 探针 | 车辆控制或飞行验收。 |
| `MoSimQuadrotorModel.Visualization.*` | 图形化场景和诊断显示 | GUI 可读性或原生窗口审查已通过。 |
| `MoSimQuadrotorModel.Common.*` | 跨层限制和公共支撑模型 | 独立控制或仿真闭环。 |

## 4. G4 Current Model Entry Mapping and Non-destructive Refactor Contract

G4 Current Model Entry Mapping and Non-destructive Refactor Contract uses
`Config/control_platform/current_model_entry_map.json` as the frozen entry
registry. The operation catalog is not the 48-profile current-model-entry registry;
it only lists allowlisted Model Studio operations.

G4 is non-destructive: it migrates qualified namespaces and updates references
without asserting a controller result. It does not open MWORKS, call
`CheckModel`, or create a simulation record. A graphical controller core is
tracked as an `internal_graphical_probe` until it has an explicit runner and
plant-coupled evidence record.

The current registry distinguishes 46 resolved MWORKS routes, one planned ESO
Profile without a model, and the separate pending-MWORKS-equivalent `px4ctrl`
engineering/deployment baseline. The 46 resolved routes split into 41 graphical controller cores and five named whole-aircraft profiles. The 47-Profile
catalog is not a retroactive claim that every Profile already has a current
MWORKS run. A winner from any of the seven semantic families cannot enter A/B
testing until its champion-specific core/Adapter/plant binding has passed the
required minimum whole-aircraft closure.

## 5. Reproduction Sequence

```text
1. Load Models/MoSimQuadrotorModel/package.mo once.
2. Resolve the desired canonical class from Config or this index.
3. Check the model or run the declared experiment profile.
4. Bind the resulting native file/log/metrics to the exact class and scenario.
5. State the evidence layer and any remaining blocker.
```

For controller experiments, the expected chain is:

```text
scenario configuration
  -> canonical model class
  -> Experiment Runner and whole-aircraft harness when required
  -> MWORKS result/native artifact
  -> metrics and review screenshot
```

The formal-root checker is:

```text
python Scripts/quality/consolidate_mosimquad_model_root.py --check
```

It confirms only layout and active-reference hygiene. Use the relevant MWORKS workflow for live `CheckModel`, simulation, graphical review, and result evidence.

## 6. Scenario Configs

```text
Config/scenarios/
  diagnostics/
  official/
  robustness/
  planning/
  formation/
  system/
```

Each runnable claim must bind one scenario configuration to one canonical class, one runner command, raw output, metrics, and figure/review evidence. A source file or a package load is not a simulation claim.

The current 48-profile mapping and formal-harness distinction are maintained by:

```text
Config/control_platform/control_scheme_catalog.json
Config/control_platform/current_model_entry_map.json
Config/control_platform/formal_closed_loop_harness_map.json
Docs/Workflows/controller_evidence_closeout.md
```

## 7. Historical Material

Historical results may retain the model names recorded when they were produced. They are provenance only and must never be used as an opening instruction or a substitute for a current canonical run. Automatic MWORKS crash-recovery copies likewise remain outside `Models/`; they are recovery cache, not source or a second package root.

## 8. Maintenance Rule

Update this index whenever a canonical package, current scenario binding, formal runner, or stable result location changes. Do not add aliases, duplicate roots, empty placeholder directories, or a flat experiment pool to make an old command work. Update the command/configuration to the canonical namespace instead.
