# 赛题与项目缺口清单

> 更新时间：2026-07-15
>
> 本文用于区分官方赛题要求、MoSim 项目扩展目标和当前证据状态。
> `implemented` 只表示代码或配置存在；只有有对应运行结果、指标和
> 可追溯 Manifest 才能进入 `measured` 或 `accepted`。

## 1. 当前结论

当前不能宣称赛题全部完成。控制器建模、生成代码离线门禁、基础
ROS1/Sunray/Gazebo 工程链路和部分历史轨迹/多机结果已经存在，但最终
提交还缺少统一的对比证据、鲁棒性实验收口、编队控制结论和提交包审计。

当前三机 RACER 任务占用共享 ROS/Gazebo/PX4/MAVROS 资源，因此本清单把
工作拆成两类：

```text
可立即完成：静态检查、离线生成代码、场景/Profile、指标/报告模板、
需求-证据矩阵、提交包审计。

必须独占运行：Gazebo/PX4/MAVROS 单机任务、风扰/故障运行验收、
G9 生成控制器真实回灌、三机编队/规划长任务。
```

## 2. 官方赛题要求

| 需求 | 当前状态 | 说明 |
| --- | --- | --- |
| MWORKS 四旋翼控制系统建模 | `implemented/measured_partial` | 模型、控制器和参数资产存在；需统一最终运行结果索引。 |
| 原始 PID 与优化控制器对比 | `measured_partial` | 有历史和离线结果；最终报告需要固定同一场景、同一指标和同一引用顺序。 |
| 起飞、悬停、降落 | `measured_partial` | 基线运行证据存在；G9 生成代码和最终提交包尚未统一验收。 |
| 阶跃、8 字、螺旋等典型任务 | `measured_partial` | 轨迹与脚本存在，需补齐统一指标、图表和可复现实验 Manifest。 |
| RMSE、最大误差、稳态误差、超调、调节时间 | `implemented/measured_partial` | 计算脚本存在，尚未形成最终控制器对比矩阵。 |
| 参数摄动、风扰或外部扰动鲁棒性 | `designed/measured_partial` | MWORKS robustness Profiles 已存在；需确认对应 raw/metrics/figure 是否形成成套证据。 |
| 多无人机编队控制及验证 | `integration_partial` | Diff-Planner 三机工程基线不能直接等同于自研编队控制算法完成。 |
| 用户手册、仿真分析报告、演示视频 | `in_progress` | 报告素材和部分图表存在，最终提交包尚未通过统一审计。 |

## 3. 当前项目扩展目标

| 扩展项 | 当前状态 | 边界 |
| --- | --- | --- |
| 六类 G9 生成控制器 | `offline_accepted/runtime_pending` | `official_pid` 有一次不完整真实运行；其余控制器缺少统一真实回灌证据。 |
| Gazebo/PX4/MAVROS 部署验证 | `baseline_partial` | 基础链路存在；不能把静态 adapter 或截图当作生成代码闭环。 |
| Gazebo 风扰执行 | `profile_ready/runtime_pending` | 当前风扰主要已有 MWORKS 场景定义，Gazebo 运行指标尚未成套验收。 |
| Gazebo 故障执行 | `profile_ready/runtime_pending` | 转子效率损失、控制分配和补偿代码存在，缺少最终故障前后运行包。 |
| FUEL/RACER/FALCON 探索 | `partial/historical` | 有局部和历史 smoke；不等同于完整自主探索完成。 |
| UE/前端实验平台 | `support_partial` | 属于展示和实验平台增强，不替代控制器或 Gazebo/PX4 证据。 |

## 4. 不依赖独占仿真的工作队列

### A. 现在执行

1. 保持 G9 生成 C 离线门禁、ABI 门禁和 ROS/Sunray adapter 静态门禁可重复。
2. 整理官方 PID、改进 PID、SE3、DFBC、SMC、PID-INDI、NMPC 的控制器登记表。
3. 统一基础轨迹和鲁棒性 Profile 的字段：场景、控制器、随机种子、扰动类型、
   开始时间、持续时间、强度、输出 raw、metrics、figure 和 Manifest。
4. 建立官方要求到实验结果的证据矩阵，明确每项是 `implemented`、`measured`
   还是 `accepted`。
5. 生成报告用指标表和图表清单，但不把缺失运行结果填成通过。
6. 审计提交包：模型、脚本、配置、文档、结果索引、许可证和复现命令。

### B. 资源释放后执行

1. 先跑 `official_pid` 的完整单机起飞-悬停-降落，确认运行时加载的确实是
   G9 generated C。
2. 按同一门禁依次跑其余五类 G9 控制器。
3. 运行官方典型轨迹和统一指标矩阵。
4. 运行 MWORKS 风扰/参数摄动对比；如要把风扰或故障声明为 Gazebo 部署能力，
   再运行对应 Gazebo/PX4 回灌并保留前后状态和恢复指标。
5. 单独验收三机规划、避碰和真正的编队控制，不把目标点到达结果改名为编队完成。

## 5. 已执行的无仿真检查

最近一次本地验证：

```text
G9 generated-C offline gate: passed
controllers: 6
cases: 450
failures: 0
tolerance: 1e-12
result: Results/g9/controller_family_attitude_thrust_v1/g9_family_generated_c_gate_20260715_210204

trajectory dynamics tests: 8 passed
selected quality scripts: Python compile passed
```

该结果只证明生成代码离线一致性和工程编译门禁，不证明 ROS、Gazebo、PX4、
MAVROS、RViz 或真实飞行任务成功。

## 6. 当前优先级

```text
P0  清理/结束占用共享资源的 RACER 任务后，完成 official_pid 单机闭环
P1  六类 G9 控制器统一回灌与典型轨迹指标
P1  MWORKS 风扰和参数摄动最终对比包
P1  报告/用户手册/演示视频/提交包审计
P2  Gazebo 故障注入回灌、故障恢复指标和三机故障重构
P2  自研编队控制与编队故障重构
P3  UE、探索平台和后置展示增强
```

## 7. 禁止的状态升级

- 不把 YAML/模型/代码存在升级为运行通过。
- 不把 MWORKS 风扰场景配置升级为 Gazebo 风扰验收。
- 不把转子故障模型或控制分配代码升级为故障容错完成。
- 不把 Diff-Planner 三机到达目标升级为自研编队控制完成。
- 不把历史结果和当前 G9 generated-runtime 结果混成一张排行榜。
