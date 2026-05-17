# 面向复杂任务场景的四旋翼无人机自适应鲁棒位姿控制与智能仿真验证系统

本项目面向 A8 四旋翼无人机位姿控制系统设计优化赛题，基于 MWORKS.Sysplorer、Sysblock 和 Syslab 构建可复现的仿真验证工程。

当前证据口径：项目目标以 **MWORKS.Sysblock 控制器仿真为主线**，Sysplorer/Modelica 闭环仿真和脚本指标计算为辅助。现阶段已经完成多组真实 Sysplorer MCP 性能证据；Sysblock 方向已完成 AWFF PID 高度环最小模型、位置环、姿态环、电机分配、三层组合控制器 `AWFF_FullController_Sysblock`、单层扁平图形化控制器 `AWFF_FullControllerFlatGraphical_Sysblock`，以及 L1/INDI/故障隔离图形化控制器包 `AWFF_InnovationGraphicalControllers` 的真实 MCP `load_file/check_model` 验证。图形化 Sysblock 控制器作为 Modelica 整机子组件时，当前编译器会在内部多输入端口解析处失败，因此整机性能主线使用等价 Equation Sysblock 控制器接入 `QuadrotorExperiments.*SysblockClosedLoop`；图形化模型仍是控制器结构、信号流、离散状态、限幅和模式逻辑的主表达形式，Equation 版只作为当前整机混合接入的桥接实现。

当前正式场景矩阵共 `76` 个，均已完成结果生成并通过 evidence bundle 审计；其中 `59` 个为可支撑结论的 `pass` evidence，`17` 个为已标注的边界/负样本证据。负样本主要用于证明 PID/AWFF/纯 L1/纯 LinearMPC 在旋翼退化下不够，需要故障隔离、在线效率估计或控制分配补偿。当前 Sysblock 主线已覆盖阶梯爬升、螺旋爬升、8 字轨迹、质量摄动、横向阵风、旋翼退化、L1-inspired 残差补偿、L1-inspired + INDI-like 组合控制器、LinearMPC-style 外环、在线效率估计控制分配、QP/NMPC-style 安全投影、CBF-style Safety Filter、模式切换、event_log、安全返航/降落闭环、Sunray150 规划避障闭环、GPS dropout 系统级降级场景，以及平面/螺旋 8 字轨迹留痕可视化审查场景。


当前机体迁移状态：`QuadrotorModel.Mechanics.QuadChassis` 已迁移到项目内本地源 `references/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360` 的参数和可视化资源，机体质量 `1.0 kg`、惯量 `Ixx=0.0085, Iyy=0.0085, Izz=0.012`、旋翼位置 `±0.065 m`，并加入 Mid360 安装位置的轻量可视化件。SDF 原始电机常数为 `8.54858e-06 N/(rad/s)^2`，`rotorVelocitySlowdownSim=10`；MWORKS 机体使用按可视化轴转速折算后的升力系数 `0.000854858`。旧轻量机架 full-run 指标只作为历史证据；当前单无人机主结论已经切换到 Sunray150_with_mid360 后的真实 Sysplorer/MWORKS 结果。

当前单机规划状态：已完成 `planner_astar_min_snap` 的最小闭环实现，包含标准地图配置、2D/2.5D A*、直线可见性简化、五次多项式平滑、速度/加速度/jerk/tilt/障碍距离预检查、`reference.csv`、`trackability_report.json` 和 `map_preview.svg` 输出。`map_open_blocks` 与 `map_corridor_gate` 两个 P1 标准地图均已通过离线可跟踪性预检查，并已接入 Sunray150 MWORKS 控制闭环。AWFF 版本在规划轨迹跟踪中作为负样本保留；LinearMPC-style 外环已在两个规划场景中通过真实 Sysplorer MCP 质量门。

## 尺寸与参数速查

当前 `planning_open_blocks` 地图、障碍物和无人机尺寸不要从动画里估算，统一从下面这些文件读取：

| 类别 | 当前值 | 数据位置 |
|---|---|---|
| 地图范围 | `90 m x 60 m`，`x=[-45,45]`，`y=[-30,30]`，`z=[0,3.5]` | `planners/astar_min_snap/map_open_blocks.yaml` |
| 规划栅格 | A*/碰撞检查分辨率 `0.4 m`；安全裕度 `0.35 m` | `planners/astar_min_snap/map_open_blocks.yaml` |
| 局部感知 | 半径 `3.0 m`；局部显示/传感细格 `0.20 m`；更新周期 `0.05 s`，即 `20 Hz` | `planners/astar_min_snap/map_open_blocks.yaml`、`scripts/update_planning_open_blocks_model.py` |
| 地面起伏 | 每个地形柱横截面 `0.20 m x 0.20 m`；高度 `0.10-1.50 m`；高度量化 `0.01 m`；底面固定 `z=0` | `scripts/generate_static_planning_map.py` |
| 随机障碍碰撞真值 | `1000` 处障碍簇；每簇 `4-10` 根小柱；小柱横截面 `0.20 m x 0.20 m`；高度 `2.8-3.5 m`；当前展开为 `7102` 根 box 小柱 | `planners/astar_min_snap/map_open_blocks.yaml`、`results/planning/single_obstacle_astar_awff/metrics/trackability_report.json` |
| 随机障碍 GUI 显示 | 与碰撞真值共用同一批小柱；当前 STL 包含 `1000` 处障碍簇、`7102` 根 `0.20 m x 0.20 m` 小柱 | `scripts/generate_static_planning_map.py`、`QuadrotorModel/Resources/Visualization/map_open_blocks_static_obstacle_columns_0p2_h2p8_3p5.stl` |
| L/T 墙体 | `8` 组墙，展开为 `16` 个 box；长边 `18 m`，短边 `6 m`，厚度 `0.32 m`，高度 `3.5 m`；`L` 为短墙端点接长墙端点，`T` 为短墙中点接长墙端点 | `planners/astar_min_snap/map_open_blocks.yaml`、`scripts/check_wall_group_bboxes.py` |
| Sunray150 物理参数 | 质量 `1.0 kg`；惯量 `Ixx=0.0085`、`Iyy=0.0085`、`Izz=0.012`；旋翼安装偏移 `±0.065 m` | `QuadrotorModel/package.mo` |
| Sunray150 可视化尺寸 | 机身 STL 当前显示包络约 `0.25 m x 0.25 m x 0.19 m`；桨叶显示包络约 `0.10 m` 级别；公开实物尺寸约 `210 x 210 x 100 mm`、重量约 `1080 g` | `QuadrotorModel/Resources/Visualization/*.stl`、`docs/index/sunray_migration_index.md` |

说明：地面总起伏现在为 `1.40 m`，飞行高度参考采用 `terrain_follow_agl`，即相对当前地面约 `1.0 m` AGL。显示层和规划碰撞真值已经统一到同一批 `0.20 m` 小柱；后续若再调障碍物尺寸、地形高度或墙体高度，必须同时重新生成 reference、trackability report、静态 STL 和闭环模型同步结果。

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
| 设计文档 | `Design/00_系统总体设计.md` 至 `Design/08_仿真指标与自动评估.md` |
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
scenarios/robustness/example1_rotor{1..4}_loss15_wind_gust_linear_mpc_online_fault_allocation_sysblock.yaml  Sysblock LinearMPC-style + eta_hat[4] 复合故障在线分配对照
scenarios/official/example1_qp_nmpc_safety_sysblock.yaml  Sysblock QP/NMPC-style + CBF Safety Filter 阶梯爬升
scenarios/official/example1_qp_nmpc_safety_return_land_sysblock.yaml  Sysblock QP/NMPC-style + CBF Safety Filter + 返航/降落闭环
scenarios/planning/sunray150_planning_open_blocks_linear_mpc_sysblock.yaml  Sunray150 局部感知避障 + 实时重规划 LinearMPC-style 闭环
scenarios/planning/sunray150_planning_corridor_gate_linear_mpc_sysblock.yaml  Sunray150 A* 通道门避障 LinearMPC-style 闭环
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

生成并检查单机规划 reference：

```bash
python scripts/plan_astar_min_snap.py planners/astar_min_snap/map_open_blocks.yaml
python scripts/plan_astar_min_snap.py planners/astar_min_snap/map_corridor_gate.yaml
python scripts/check_reference_outputs.py
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
P1 创新控制器证据：AWFF_L1ResidualControllerEquation_Sysblock 已覆盖 Example1、8 字形、质量 +20%、横向阵风和旋翼退化真实 Sysplorer MCP 仿真；其中 Example1、8 字形、质量 +20% 和横向阵风均通过质量门。`AWFF_INDIControllerEquation_Sysblock` 当前实现为 AWFF + L1-inspired 残差外环 + INDI-like 姿态增量组合控制器，已在 Example1、Example2 helix-tuned 和 Example3 8 字形通过质量门。已知效率退化控制分配补偿、在线效率估计补偿和多旋翼隔离雏形均已完成 rotor1-4 单旋翼退化和 rotor1-4 单旋翼退化叠加横向阵风复合鲁棒验证，所有 `l1_multi_fault_isolation_sysblock` 对应场景均通过质量门，`fault_index` 在 `5-50 s` 内正确率为 `100%`。Sunray150_with_mid360 迁移后，所有单无人机实验包装模型均加入悬停电机速度偏置与控制增量缩放，避免 Equation Sysblock 控制器输出直接接入新机体电机速度域。`AWFF_LinearMPCOuterLoopControllerEquation_Sysblock` 当前实现为 finite-horizon linear MPC-style 外环 + L1-inspired residual feedforward + INDI-like 姿态内环，已完成 Example1 50 s、Example2 50 s、Example3 120 s 全时长真实 Sysplorer MCP 仿真并通过质量门，Sunray 后 RMSE 分别为 `0.1350 m`、`0.4291 m`、`0.0846 m`。LinearMPC-style 外环的质量 +20% 和横向阵风鲁棒场景也已通过质量门；纯外环在 1 号旋翼 85% 退化下健康分不足，加入在线 `eta_hat` 效率估计与控制分配补偿后质量门通过。新增 `AWFF_LinearMPCMultiFaultAllocationController_Sysblock` 已完成 rotor1-4 单旋翼退化叠加横向阵风复合鲁棒对照，AWFF 边界样本均为 `needs_iteration`，LinearMPC 多旋翼在线分配均为 `pass`，`fault_index` 在 rotor2-4 场景中正确率为 `100%`。新增 `AWFF_QPNMPCSafetyController_Sysblock` 已完成 Example1 nominal 和 return/land 两个 50 s 真实 Sysplorer MCP 场景：nominal RMSE `0.2398 m`、健康分 `55.891`；返航/降落场景 RMSE `0.2084 m`、健康分 `56.146`，event_log 包含 `NORMAL -> SAFETY_FILTER_ACTIVE -> DEGRADED_RETURN -> EMERGENCY_LAND`，50 s 末端高度稳定在 `0.15 m`。该实现是固定迭代投影式 QP/NMPC-style 在线安全优化，不是通用 dense QP 库或完整多重 shooting NMPC NLP 求解器。
单无人机控制收尾状态：截至 2026-05-15，正式场景矩阵 76 项均有结果，59 项为 `pass`，17 项为保留的边界/负样本；单机主控制、鲁棒、故障分配、安全返航/降落闭环、规划避障闭环和系统级 GPS dropout 降级场景可以进入报告和录屏素材整理。后续再考虑瞬态故障切换、多旋翼同时故障或编队扩展。
单机规划闭环状态：`planners/astar_min_snap/map_open_blocks.yaml` 和 `planners/astar_min_snap/map_corridor_gate.yaml` 已生成 `results/planning/*/raw/reference.csv`、`metrics/trackability_report.json` 和 `figures/map_preview.svg`。`planning_open_blocks` 是正式局部感知实时重规划场景：固定随机种子生成 `7118` 个真值障碍，其中 `1000` 处随机障碍簇展开为 `7102` 根小柱，另有 `16` 个 L/T 墙体 box；规划器只使用局部窗口内已发现障碍，最终发现 `847` 个障碍，滚动重规划 `113` 次，最小障碍距离 `0.356 m`，相对 `0.35 m` 最终安全裕度仍有正裕度。当前 reference 已切换为地形跟随高度剖面，参考高度范围约 `1.22-2.47 m`，规划参考时长约 `324.30 s`。Sunray150 MWORKS LinearMPC-style 闭环已重新通过质量门：RMSE `0.1133 m`，最大误差 `0.2521 m`，最大倾角 `0.0878 rad`，健康分 `93.821`，结果 `6548` 行，原生结果位于 `results/native_result_cache/sunray150_planning_open_blocks_linear_mpc_sysblock/Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop/Result.msr`。`planning_corridor_gate` 作为静态窄门对照，RMSE `0.1257 m`、最大误差 `0.2996 m`、最大倾角 `0.1003 rad`，为历史 `quality_status=pass`。AWFF 规划闭环出现横向发散，保留为控制器适用性负样本。
```

## 设计文档

| 文件 | 主题 |
|---|---|
| `Design/00_系统总体设计.md` | 总体架构、创新点、模块关系、参考路线 |
| `Design/01_需求范围与验收.md` | 需求、P0/P1/P2、验收指标、实现计划 |
| `Design/02_模型接口与运行流程.md` | 模型接口、MWORKS 替换位置、信号接口、运行流程 |
| `Design/03_控制系统架构.md` | PID、MPC/NMPC、INDI、L1-inspired 补偿 |
| `Design/04_安全故障与容错.md` | 安全过滤、故障注入、执行器容错 |
| `Design/05_路径规划与轨迹生成.md` | 多种规划算法、轨迹平滑、动态可行性 |
| `Design/06_多机编队控制.md` | 多机编队、队形切换、机间避碰 |
| `Design/07_场景扰动与测试矩阵.md` | 场景库、扰动库、测试矩阵 |
| `Design/08_仿真指标与自动评估.md` | 仿真流程、指标体系、图表设计、Codex/MCP 自动化评估 |

为避免文档口径漂移，Design 目录不再保留单独 README；项目总览、当前状态和文档入口统一维护在本文件。

## QA 检查

```bash
python scripts/qa_check.py
```

`qa_check.py` 只检查工程骨架、关键文档和 MCP wrapper 可见性，不验证 MWORKS 模型正确性。
