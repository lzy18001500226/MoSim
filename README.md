# 面向复杂任务场景的四旋翼无人机自适应鲁棒位姿控制与智能仿真验证系统

本项目面向 A8 四旋翼无人机位姿控制系统设计优化赛题，基于 MWORKS.Sysplorer、Sysblock 和 Syslab 构建可复现的仿真验证工程。

当前证据口径：项目目标以 **MWORKS.Sysblock 控制器仿真为主线**，Sysplorer/Modelica 闭环仿真和脚本指标计算为辅助。现阶段已经完成多组真实 Sysplorer MCP 性能证据；Sysblock 方向已完成 AWFF PID 高度环最小模型、位置环、姿态环、电机分配、三层组合控制器 `AWFF_FullController_Sysblock` 和单层扁平图形化控制器 `AWFF_FullControllerFlatGraphical_Sysblock` 的真实 MCP 验证，并完成 `AWFF_FullControllerEquation_Sysblock` 接入官方 Example1/2/3 整机的全时长闭环证据。当前 Sysblock 主线已覆盖阶梯爬升、螺旋爬升、8 字轨迹、质量摄动、横向阵风、旋翼退化和 L1-inspired 残差补偿控制器首轮消融。

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
scenarios/smoke/example1_pid_mcp_smoke.yaml    0-1 s MCP 链路烟雾测试
scenarios/smoke/example1_awff_sysblock_mcp_smoke.yaml  0-1 s Sysblock 整机闭环烟雾测试
```

`results/smoke/example1_mcp/pid_baseline_smoke/raw/mworks_mcp_example1_pid_smoke.csv` 只用于 0-1 s 真实 MCP 链路验证，不作为完整官方 baseline 指标。

按场景 YAML 运行真实 Sysplorer MCP 证据链：

```bash
python scripts/run_mworks_scenario.py scenarios/smoke/example1_pid_mcp_smoke.yaml
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
Sysblock 真实证据：AWFF_PID_Sysblock_Demo 已通过 load_file/check_model/simulate_model/result_manager；位置环、姿态环、电机分配、三层组合控制器和单层扁平图形化控制器已通过真实 MCP load_file/check_model/simulate_model。当前 Sysplorer 编译器不支持图形化 Sysblock 控制器作为 Modelica 整机子组件时的内部多输入端口解析，因此官方整机性能证据使用等价 `AWFF_FullControllerEquation_Sysblock` 接入 QuadrotorExperiments.Example1/2/3AWFFSysblockClosedLoop，并已完成 Example1 50 s、Example2 50 s、Example3 120 s 全时长真实 Sysplorer MCP 仿真。
P1 创新控制器证据：AWFF_L1ResidualControllerEquation_Sysblock 已覆盖 Example1、8 字形、质量 +20%、横向阵风和旋翼退化真实 Sysplorer MCP 仿真；其中 Example1、8 字形、质量 +20% 和横向阵风均通过质量门。已知效率退化控制分配补偿 `AWFF_L1FaultAllocationControllerEquation_Sysblock` 在 1 号旋翼 85% 场景中通过质量门，RMSE 相比 AWFF Sysblock 降低 33.793%。在线效率估计补偿 `AWFF_L1OnlineFaultAllocationControllerEquation_Sysblock` 已输出 `eta_hat` 诊断列并通过质量门，RMSE 相比 AWFF Sysblock 降低 29.363%，`eta_hat` 末值约 0.904。多旋翼隔离雏形 `AWFF_L1MultiFaultIsolationControllerEquation_Sysblock` 已输出 `eta_hat1..4` 和 `fault_index`，在 rotor1 85% 退化场景中通过质量门，5-50 s `fault_index=1` 正确率为 100%。
后续优先级：补 rotor2/3/4 效率退化场景，验证 `eta_hat[4]` 和 `fault_index` 的跨旋翼泛化；随后启动 INDI 或线性 MPC 外环最小可运行模型。
```

## QA 检查

```bash
python scripts/qa_check.py
```

`qa_check.py` 只检查工程骨架、关键文档和 MCP wrapper 可见性，不验证 MWORKS 模型正确性。
