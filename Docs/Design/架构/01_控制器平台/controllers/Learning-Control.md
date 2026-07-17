# 冻结学习控制路线

Status: P9 report-ready implementation closeout, runtime acceptance blocked, 2026-07-17 CST.

## 1. 两条路线

P9 保留两条具有独立报告价值、同时可转换为确定性固定尺寸 C 的学习控制路线：

1. `trained_neural_residual`：冻结 MLP 输出三轴有界加速度残差，叠加在 Cascade PID 外环。
2. `rl_gain_scheduler`：冻结 PPO actor 输出三轴 `[0, 0.25]` 有界增益调度量，不在飞行时继续训练。

两条路线共用 `ATTITUDE_THRUST`、100 Hz、Cascade PID fallback、运行时质量/重力/
悬停推力/倾角/总推力边界输入，以及直接供 px4ctrl 使用的 `normalized_thrust` 输出。
训练产物固定在 `Config/control_platform/learning_control_artifact.json`，SHA256 为
`4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45`。

## 2. 闭环证据

| Gate | 结果 | 权威证据 |
|---|---|---|
| 训练与 held-out A/B | 通过 | `Results/control_platform/p9_learning_training_20260717/TRAINING_SUMMARY.json` |
| 固定尺寸 C、冻结哈希与 fallback | 通过 | `Results/control_platform/p9_learning_offline_gate_20260717/P9_LEARNING_CONTROL_OFFLINE_GATE.json` |
| ATTITUDE_THRUST 物理接口 | 通过 | `Results/control_platform/p9_learning_attitude_thrust_gate_20260717/P9_LEARNING_ATTITUDE_THRUST_GATE.json` |
| Sysplorer MWORKS MIL | 3 个 CheckModel、2 条 MIL 通过 | `Results/control_platform/p9_learning_mworks_20260717/MWORKS_MIL_EVIDENCE.json` |
| MWORKS 官方代码生成 | 通过 | `Results/control_platform/p9_learning_mworks_20260717/generate_model_code_result.json` |
| generated-C SIL | 2 路、每路 19 列、最大差值 0 | `Results/control_platform/p9_learning_mworks_20260717/sil/P9_GENERATED_SIL_EQUIVALENCE.json` |
| px4ctrl 生成核装载 | 6 个学习 case 全部通过 runtime ACK | `Results/control_platform/p9_learning_gazebo_r4_20260717/` |
| Gazebo/PX4/MAVROS 3x3 A/B | 执行通过，严格性能验收阻塞 | `Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json` |

## 3. 真实运行结论

r4 在同一任务、同一物理注入和同一指标合同下运行 Cascade、Neural、RL 的
`nominal / wind / parameter_mismatch` 九个 case。九例均完成降落解锁，六个学习
case 均确认 MWORKS 生成符号进入 px4ctrl。矩阵 `execution_status=passed`，但
`acceptance_status=blocked`。

风扰条件下，Neural 和 RL 相对 Cascade 的全参考 XYZ RMSE 分别改善 `9.81%` 和
`8.80%`，具有报告价值。与此同时，Neural 在 nominal 与参数失配下分别劣化
`13.04%`、`29.53%`；RL 分别劣化 `5.38%`、`19.58%`。r3 Neural nominal 单例曾
通过严格门禁，但 r4 重复矩阵未通过，不能用一次通过记录替代稳定性结论。

因此两个 Profile 当前均为 `implemented/selectable=false`：可以复现实验、生成
对比图表并在报告中讨论鲁棒收益与泛化不足，但不能作为正式可选控制器或宣称全面
优于 Cascade PID。后续若要晋级，必须重新设计训练分布/奖励并使用新 artifact
哈希重复 MIL、codegen、SIL 和至少两轮完整 3x3，不得覆盖本次冻结证据。
