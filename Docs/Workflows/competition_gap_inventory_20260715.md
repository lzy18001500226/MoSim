# 赛题与项目缺口清单

> 更新时间：2026-07-18
>
> 本文用于区分官方赛题要求、MoSim 项目扩展目标和当前证据状态。
> `implemented` 只表示代码或配置存在；只有有对应运行结果、指标和
> 可追溯 Manifest 才能进入 `measured` 或 `accepted`。

## 1. 当前结论

当前不能宣称赛题全部完成，但控制平台已经从“多数仅有源码/离线证据”
推进到统一 67 行矩阵：27 项 accepted、25 项 executed-blocked、15 项
not-run。P2-P8 的新增实现、生成代码和运行证据均已提交并推送；P9 的
Neural Residual 与 RL Gain Scheduler 已完成 3x3 真实运行，但严格性能门禁
未通过。LQR、LQI、SO(3) 与 Backstepping 已完成 generated-C Gazebo 有界
执行并保留为 executed-blocked。剩余主线不再受 RACER 任务占用，重点是高价值控制器补跑、统一
A/B、最终需求证据矩阵和提交包，而不是继续扩展前端或自主探索。

## 2. 官方赛题要求

| 需求 | 当前状态 | 说明 |
| --- | --- | --- |
| MWORKS 四旋翼控制系统建模 | `measured_partial` | 多族控制器已有真实图形 MIL、官方代码生成和 SIL；仍需最终索引与少量证据阶梯补齐。 |
| 原始 PID 与优化控制器对比 | `measured_partial` | 67 行控制器矩阵已形成；仍缺统一七场景 A/B 和最终推荐结论。 |
| 起飞、悬停、降落 | `measured_partial` | 27 行已 accepted，25 行真实执行后阻塞，15 行待补跑或终态分类。 |
| 阶跃、8 字、螺旋等典型任务 | `measured_partial` | 部分代表控制器已有轨迹结果；最终七场景矩阵仍未闭合。 |
| RMSE、最大误差、稳态误差、超调、调节时间 | `implemented/measured_partial` | 计算链与多批结果存在；需生成最终跨场景对比表和报告图。 |
| 参数摄动、风扰或外部扰动鲁棒性 | `measured_partial` | P9 已有 nominal/wind/parameter-mismatch 3x3；最终推荐控制器统一 A/B 仍待完成。 |
| 多无人机编队控制及验证 | `accepted_bounded` | 九种编队模式均有三机 Gazebo/PX4/MAVROS/px4ctrl accepted 证据；不宣称自主探索。 |
| 安全与故障容错 | `accepted_bounded` | 七种安全模式和 rotor-1 效率 0.65 的检测、隔离、接管、降落已验收；不宣称完全停转或多电机恢复。 |
| 用户手册、仿真分析报告、演示视频 | `in_progress` | 最终需求证据矩阵、图表、手册、演示清单和提交包尚未统一收口。 |

## 3. 当前项目扩展目标

| 扩展项 | 当前状态 | 边界 |
| --- | --- | --- |
| 六类 G9 生成控制器 | `runtime_blocked_partial` | official_pid 同运行生成代码闭环已执行，但 XY RMSE 超门限；其余五类按 fail-closed 规则未运行。 |
| Gazebo/PX4/MAVROS 部署验证 | `measured_partial` | 多族控制器已有同运行生成代码来源与任务指标；逐行状态以 67 行矩阵为准。 |
| Gazebo 风扰执行 | `measured_partial` | P9 已有风扰 A/B；最终推荐控制器七场景 A/B 仍待完成。 |
| Gazebo 故障执行 | `accepted_bounded` | P7 已完成 rotor-1 35% 效率损失闭环；完整停转和多电机故障保持未声明。 |
| FUEL/RACER/FALCON 探索 | `frozen_support` | 不再继续覆盖率调参，不属于本轮提交阻塞。 |
| UE/前端实验平台 | `excluded_from_goal` | 已有成果保留，但本轮不继续开发，也不替代控制与运行证据。 |

## 4. 当前收口队列

1. 对 15 个 not-run 行做终态分诊：优先 G9 五类；随后审计 DFBC、
   L1/AWFF 和 DOB/ESO；对缺动态 `musyn` 的
   mu-Synthesis、无冻结数据/模型的 Neural-SMC 保持明确 blocker。
2. 对 25 个 executed-blocked 行只做有报告价值且能保持同一门限的有界重试；
   不通过调低门限、拼接不同 run 来源或覆盖失败结果提高通过数。
3. 选择官方 PID 和最终推荐控制器，完成悬停、阶跃、8 字、螺旋、风扰、
   参数摄动、电机效率故障的同配置 A/B、指标、图和 Manifest。
4. 汇总 P6 安全、P7 FTC、P8 编队、P9 学习控制的边界与结果，不重复跑已经
   accepted 且不可变的专用门禁。
5. 生成最终需求证据矩阵、结果索引、仿真分析、用户手册、演示素材清单和
   可复现提交包，并完成许可证、秘密、大文件和 Git 上游审计。

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
P0  高价值 not-run 分诊与 G9/经典控制器有界运行
P0  官方 PID 与推荐控制器七场景统一 A/B
P1  最终需求证据矩阵、报告图表与仿真分析
P1  用户手册、演示素材清单、可复现提交包和 QA
P2  已有 executed-blocked 控制器的报告价值重试
P3  完全停转、多电机故障、无数据集神经控制器等明确扩展项
排除 前端、UE/RViz 嵌入、继续 FUEL/RACER 覆盖率调参
```

## 7. 禁止的状态升级

- 不把 YAML/模型/代码存在升级为运行通过。
- 不把 MWORKS 风扰场景配置升级为 Gazebo 风扰验收。
- 不把转子故障模型或控制分配代码升级为故障容错完成。
- 不把 Diff-Planner 三机到达目标升级为自研编队控制完成。
- 不把历史结果和当前 G9 generated-runtime 结果混成一张排行榜。
