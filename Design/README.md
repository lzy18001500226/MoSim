# A8 四旋翼无人机鲁棒位姿控制与智能仿真验证系统设计文档包

本设计包把系统拆成多个可独立实现、可裁剪、可替换的模块。设计目标不是“只写一个控制器”，而是形成完整闭环：

```text
复杂任务 → 模式决策 → 可跟踪轨迹规划 → 自适应鲁棒位姿控制
       → 安全/故障降级 → 编队协同 → 自动化评估 → 三维回放/报告/视频
```

## 当前仿真主线状态

目标口径必须保持清晰：

```text
主线：MWORKS.Sysblock 控制器建模与仿真
辅助：Sysplorer/Modelica 派生模型闭环仿真、Syslab/Python 指标与图表
```

截至当前版本，Sysplorer/Modelica 已经形成可复现性能证据；Sysblock 已完成 AWFF PID 高度环最小模型 `AWFF_PID_Sysblock_Demo` 的 `load_file/check_model/simulate_model/result_manager` 验证，并完成位置环、姿态环、电机分配三个分层 Sysblock 模型的 `load_file/check_model`。组合模型 `AWFF_FullController_Sysblock` 已经把三段控制器接入同一控制链，并通过真实 MCP `load_file/check_model/simulate_model/result_manager`。完整 Sysblock 四旋翼闭环尚未完成，后续实现应优先把组合控制器接入官方主模型，再用 MCP 跑主模型 `check_model/simulate_model/result_manager`，避免把控制器独立仿真当作整机闭环性能证据。

## 主创新口径

项目名称保留为：

**面向复杂任务场景的四旋翼无人机自适应鲁棒位姿控制与智能仿真验证系统**

作品创新不按“算法清单”展开，而按系统能力展开：

1. **自适应鲁棒位姿控制**：MPC/NMPC 外环、INDI 姿态内环、L1-inspired 加速度残差补偿和安全过滤形成统一控制链路。
2. **可跟踪性感知轨迹规划**：规划器不仅绕障，还根据速度、加速度、jerk、倾角和控制饱和风险调整轨迹。
3. **扰动识别与控制模式切换**：根据风扰、质量变化、电机效率退化和传感器噪声残差切换控制模式。
4. **故障诊断与降级容错**：完成故障注入、残差检测、控制分配重构和安全返航/降落策略。
5. **智能仿真评估与三维回放**：自动输出指标、健康度评分、事件日志和数据驱动三维视频素材。

## 文档清单

| 文件 | 主题 |
|---|---|
| 00_系统总体设计.md | 总体架构、创新点、模块关系、参考路线 |
| 01_需求范围与验收.md | 需求、P0/P1/P2、验收指标、实现计划 |
| 02_模型接口与运行流程.md | 模型接口、MWORKS 替换位置、信号接口、运行流程 |
| 03_控制系统架构.md | PID、MPC/NMPC、INDI、L1-inspired 补偿 |
| 04_安全故障与容错.md | 安全过滤、故障注入、执行器容错 |
| 05_路径规划与轨迹生成.md | 多种规划算法、轨迹平滑、动态可行性 |
| 06_多机编队控制.md | 多机编队、队形切换、机间避碰 |
| 07_场景扰动与测试矩阵.md | 场景库、扰动库、测试矩阵 |
| 08_仿真指标与自动评估.md | 仿真流程、指标体系、图表设计、Codex/MCP 自动化评估 |

## 推荐实现优先级

```text
P0：官方 PID baseline + 改进 PID + 数据导出 + 指标计算 + 三维回放素材
P1-A：Sysblock 控制器主仿真链路 + MPC/NMPC-INDI-L1 主控制链路 + 扰动识别
P1-B：Safety Filter + 电机故障注入 + 容错/降级策略
P2：可跟踪性感知路径规划 + 三机协同任务 + 健康度评分 + MCP 批量评估
P3：完整局部重规划、RL、完整 ROS/EGO-Planner 移植，作为展望
```

## Codex/MCP 自动化入口

当前已接入两组 MCP：

```text
syslab:
  evaluate_julia_code / run_julia_file / read_syslab_doc / search_syslab_docs

sysplorer_mcp:
  session_manager / model_manager / check_model / simulate_model / result_manager / plot_manager
```

Codex 后续实现和验证时优先按以下顺序操作：

```text
查文档
→ 打开/检查模型
→ 运行仿真
→ 读取结果
→ 执行 Julia 指标脚本
→ 生成 figures/summary/replay
→ 记录 mcp_log.json
```

详细工具职责、调用模板和日志格式见 `08_仿真指标与自动评估.md` 第 17 节。

## 最小可交付闭环

```text
官方 PID baseline
→ 改进 PID
→ PID-INDI 或轻量 MPC-INDI
→ 风扰/质量变化对比
→ 8字/螺旋/风扰实验
→ RMSE/超调/调节时间/控制能量
→ 用户手册 + 仿真分析报告 + 演示视频
```

## 完整高分闭环

```text
任务管理与模式切换
+ NMPC/MPC-INDI-L1
+ Safety Filter
+ 电机效率退化与控制分配重构
+ Trackability-aware A*/RRT*/Minimum Snap/B-spline
+ 三机 Leader-Follower 协同任务与队形切换
+ Syslab/MCP 批量仿真、健康度评分与三维回放
```

## 报告与视频建议

仿真分析报告主线：

```text
官方 PID 问题分析
→ 改进 PID/PID-INDI/MPC-INDI 设计
→ 扰动补偿和鲁棒性验证
→ Safety/Fault/Planning/Formation 加分展示
→ 指标对比和消融结论
```

7 分钟视频建议：

| 时间 | 内容 |
|---|---|
| 0:00-0:30 | 项目概述 |
| 0:30-1:10 | 架构和主线 |
| 1:10-2:00 | baseline vs improved/MPC-INDI 对比 |
| 2:00-2:50 | 风扰走廊：模式切换 + 扰动补偿 |
| 2:50-3:40 | 物流投递：质量变化 + 自适应补偿 |
| 3:40-4:30 | 电机故障：容错重构 + 降级返航 |
| 4:30-5:25 | 障碍规划/编队切换：可跟踪规划 + 三维回放 |
| 5:25-6:20 | 自动指标、健康度评分和图表 |
| 6:20-7:00 | 创新点总结 |

## 五个王牌展示场景

| 场景 | 核心看点 | 关键证据 |
|---|---|---|
| baseline_vs_mpc_indi | 官方 PID 与优化控制器对比 | RMSE、最大误差、3D 轨迹 |
| wind_corridor | 风扰识别、模式切换、补偿恢复 | controller_mode、disturbance_hat、recovery_time |
| delivery_mass_change | 投递导致质量突变后的自适应 | event_log、steady_error、质量变化前后误差 |
| motor_fault_return | 电机效率下降后的容错和降级返航 | eta、fault_type、return_or_land_status |
| obstacle_formation_replay | 可跟踪规划、队形切换、三维回放 | trackability_score、min_inter_uav_distance、replay.json |
