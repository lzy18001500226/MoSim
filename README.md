# 面向复杂任务场景的四旋翼无人机自适应鲁棒位姿控制与智能仿真验证系统

本项目面向 A8 四旋翼无人机位姿控制系统设计优化赛题，基于 MWORKS.Sysplorer、Sysblock 和 Syslab 构建可复现的仿真验证工程。

当前证据口径：项目目标以 **MWORKS.Sysblock 控制器仿真为主线**，Sysplorer/Modelica 闭环仿真和脚本指标计算为辅助。现阶段已经完成多组真实 Sysplorer MCP 性能证据；Sysblock 方向已完成 AWFF PID 高度环最小模型、位置环、姿态环、电机分配、三层组合控制器 `AWFF_FullController_Sysblock`、单层扁平图形化控制器 `AWFF_FullControllerFlatGraphical_Sysblock`，以及 L1/INDI/故障隔离图形化控制器包 `AWFF_InnovationGraphicalControllers` 的真实 MCP `load_file/check_model` 验证，并完成 `AWFF_FullControllerEquation_Sysblock` 接入官方 Example1/2/3 整机的全时长闭环证据。当前 Sysblock 主线已覆盖阶梯爬升、螺旋爬升、8 字轨迹、质量摄动、横向阵风、旋翼退化、L1-inspired 残差补偿、L1-inspired + INDI-like 组合控制器、LinearMPC-style 外环和在线效率估计控制分配消融。


当前机体迁移状态：`QuadrotorModel.Mechanics.QuadChassis` 已迁移到项目内本地源 `references/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360` 的参数和可视化资源，机体质量 `1.0 kg`、惯量 `Ixx=0.0085, Iyy=0.0085, Izz=0.012`、旋翼位置 `±0.065 m`、升力系数 `0.01253887049854549`，并加入 Mid360 安装位置的轻量可视化件。此前基于旧机体生成的 full-run 指标保留为历史证据；正式控制器结论需要基于新机体重新跑 Sysplorer/MWORKS 结果。

核心闭环：

```text
复杂任务场景
→ 可跟踪轨迹规划
→ 自适应鲁棒位姿控制
→ 安全/故障降级
→ 编队协同
→ Syslab/MCP 自动评估
→ 控制器结构图、指标报告和可选视频素材
```

## 快速入口

| 内容 | 路径 |
|---|---|
| Agent 操作规范 | `AGENTS.md` |
| 设计文档总览 | `Design/README.md` |
| 用户手册 | `docs/user_manual.md` |
| 仿真分析报告 | `docs/simulation_report.md` |
| 文档索引 | `docs/index/doc_index.md` |
| API 索引 | `docs/index/api_index.md` |
| 工作流索引 | `docs/index/workflow_index.md` |
| 预提交检查 | `workflows/pre_submit_check.md` |

面向 Codex 的 MWORKS 专用 skills 位于 `Skills/Mworks/`。它们由 MathWorks/Simulink 原始 skills 转译而来，只保留本项目需要的模型上下文、仿真证据、Syslab 迁移、MCP 操作、运行诊断、测试质量和报告展示规则。

官方案例复现入口：

```text
scenarios/official/example1_pid_baseline.yaml  阶梯爬升
scenarios/official/example2_pid_baseline.yaml  螺旋爬升
scenarios/official/example3_pid_baseline.yaml  8字形运动
scenarios/official/example1_awff_sysblock.yaml  Sysblock AWFF 阶梯爬升
scenarios/official/example2_awff_sysblock.yaml  Sysblock AWFF 螺旋爬升
scenarios/official/example3_awff_sysblock.yaml  Sysblock AWFF 8字形运动
scenarios/official/example1_awff_indi_sysblock.yaml  Sysblock AWFF + L1-inspired + INDI-like 阶梯爬升
scenarios/official/example2_awff_indi_sysblock_helix_tuned.yaml  Sysblock AWFF + L1-inspired + INDI-like 螺旋爬升
scenarios/official/example3_awff_indi_sysblock.yaml  Sysblock AWFF + L1-inspired + INDI-like 8字形消融
scenarios/official/example1_l1_residual_sysblock.yaml  Sysblock AWFF + L1-inspired 残差补偿
scenarios/official/example3_l1_residual_sysblock.yaml  Sysblock L1 8字形消融
scenarios/robustness/example1_mass20_l1_residual_sysblock.yaml  Sysblock L1 质量+20%消融
scenarios/robustness/example1_wind_gust_l1_residual_sysblock.yaml  Sysblock L1 横向阵风消融
scenarios/robustness/example1_rotor1_loss15_l1_residual_sysblock.yaml  Sysblock L1 旋翼退化消融
scenarios/robustness/example1_rotor1_loss15_l1_fault_allocation_sysblock.yaml  Sysblock L1 + 已知效率控制分配补偿
scenarios/robustness/example1_rotor1_loss15_l1_online_fault_allocation_sysblock.yaml  Sysblock L1 + 在线 eta_hat 估计控制分配补偿
scenarios/robustness/example1_rotor1_loss15_l1_multi_fault_isolation_sysblock.yaml  Sysblock L1 + eta_hat[4] 多旋翼故障隔离
scenarios/robustness/example1_rotor2_loss15_l1_multi_fault_isolation_sysblock.yaml  Sysblock L1 + eta_hat[4] 2号旋翼退化隔离验证
scenarios/robustness/example1_rotor3_loss15_l1_multi_fault_isolation_sysblock.yaml  Sysblock L1 + eta_hat[4] 3号旋翼退化隔离验证
scenarios/robustness/example1_rotor4_loss15_l1_multi_fault_isolation_sysblock.yaml  Sysblock L1 + eta_hat[4] 4号旋翼退化隔离验证
scenarios/official/example1_linear_mpc_sysblock.yaml  Sysblock LinearMPC-style 阶梯爬升
scenarios/official/example2_linear_mpc_sysblock.yaml  Sysblock LinearMPC-style 螺旋爬升
scenarios/official/example3_linear_mpc_sysblock.yaml  Sysblock LinearMPC-style 8字形运动
scenarios/robustness/example1_mass20_linear_mpc_sysblock.yaml  Sysblock LinearMPC-style 质量+20%消融
scenarios/robustness/example1_wind_gust_linear_mpc_sysblock.yaml  Sysblock LinearMPC-style 横向阵风消融
scenarios/robustness/example1_rotor1_loss15_linear_mpc_sysblock.yaml  Sysblock LinearMPC-style 无故障分配旋翼退化边界案例
scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml  Sysblock LinearMPC-style + 在线 eta_hat 控制分配补偿
```

按场景 YAML 运行真实 Sysplorer MCP 证据链：

```bash
python scripts/run_mworks_scenario.py scenarios/official/example1_pid_baseline.yaml
```

该入口会读取模型名、时长和输出路径，调用 `check_model`、`simulate_model`、`result_manager`，再生成 metrics、SVG 图表和 replay JSON。HTML 回放不作为控制器仿真证据，只有场景 YAML 显式设置 `generate_replay_html: true` 时才生成。

批量复现已有场景：

```bash
python scripts/run_mworks_batch.py --skip-existing scenarios/official/*.yaml
```

先检查将要执行的命令：

```bash
python scripts/run_mworks_batch.py --dry-run scenarios/official/*.yaml
```

## 目录约定

```text
controllers/   控制器模块和参数
planners/      路径规划与轨迹生成模块
scenarios/     场景和扰动配置
scripts/       指标、绘图、批量实验脚本
docs/          用户手册、报告、索引和图件
workflows/     可复现操作流程
tests/         单元测试、烟雾测试和回归测试
results/       仿真结果和报告素材，按实际输出创建子目录
```

不要为了占位提前创建空目录；只有放入配置、脚本、模型、结果或说明文件时再创建对应目录。MWORKS 官方资料已经提取到 `docs/mworks/converted/` 和索引文件，项目运行不再依赖原始资料包。

## 当前实现主线

```text
P0：官方 PID baseline + 改进 PID + 数据导出 + 指标计算 + 控制器结构/指标图
P1-A：Sysblock 控制器主仿真链路 + MPC/NMPC-INDI-L1 主控制链路 + 扰动识别
P1-B：Safety Filter + 电机故障注入 + 容错/降级策略
P2：可跟踪性感知路径规划 + 三机协同任务 + 健康度评分 + MCP 批量评估
```

当前完成状态：

```text
Sysplorer/Modelica 真实仿真：官方 baseline、Improved PID、Enhanced PID、AWFF PID、质量/风扰/旋翼退化消融已完成多组证据。
Sysblock 真实证据：AWFF_PID_Sysblock_Demo 已通过 load_file/check_model/simulate_model/result_manager；位置环、姿态环、电机分配、三层组合控制器和单层扁平图形化控制器已通过真实 MCP load_file/check_model/simulate_model；`AWFF_InnovationGraphicalControllers` 中的 L1 residual、L1+INDI、L1+已知效率分配、L1+多旋翼故障隔离四个图形化控制器已通过真实 MCP load_file/check_model。当前 Sysplorer 编译器不支持图形化 Sysblock 控制器作为 Modelica 整机子组件时的内部多输入端口解析，因此官方整机性能证据暂由 Equation Sysblock 接入 QuadrotorExperiments 闭环模型；这只是整机接入约束，不降低图形化 Sysblock 对应模型的交付要求。
P1 创新控制器证据：AWFF_L1ResidualControllerEquation_Sysblock 已覆盖 Example1、8 字形、质量 +20%、横向阵风和旋翼退化真实 Sysplorer MCP 仿真；其中 Example1、8 字形、质量 +20% 和横向阵风均通过质量门。`AWFF_INDIControllerEquation_Sysblock` 当前实现为 AWFF + L1-inspired 残差外环 + INDI-like 姿态增量组合控制器，已在 Example1、Example2 helix-tuned 和 Example3 8 字形通过质量门。已知效率退化控制分配补偿、在线效率估计补偿和多旋翼隔离雏形均已完成 rotor1 85% 退化场景验证。`AWFF_LinearMPCOuterLoopControllerEquation_Sysblock` 当前实现为 finite-horizon linear MPC-style 外环 + L1-inspired residual feedforward + INDI-like 姿态内环，已完成 Example1 50 s、Example2 50 s、Example3 120 s 全时长真实 Sysplorer MCP 仿真并通过质量门；相对 L1+INDI 对应基线的 RMSE 分别降低 0.828%、0.574% 和 1.882%。LinearMPC-style 外环的质量 +20% 和横向阵风鲁棒场景也已通过质量门；纯外环在 1 号旋翼 85% 退化下健康分不足，加入在线 `eta_hat` 效率估计与控制分配补偿后质量门通过，RMSE 相对纯 LinearMPC 降低 17.778%。
后续优先级：把 LinearMPC + 在线故障分配结果补成图形化 Sysblock 人工审核素材；随后补 rotor2/3/4 效率退化场景的报告表格和视频素材。
```

## QA 检查

```bash
python scripts/qa_check.py
```

`qa_check.py` 只检查工程骨架、关键文档和 MCP wrapper 可见性，不验证 MWORKS 模型正确性。
