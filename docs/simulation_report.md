# 仿真分析报告

> 当前 `results/raw/smoke_official_example1_pid_baseline.csv` 仅为 0-1 s smoke 数据，用于验证 MCP 结果读取、CSV 导出和指标计算链路。完整官方 baseline 必须重新运行 `scenarios/official/*.yaml` 中的完整仿真时长后再写入结论。

本文档用于汇总算法设计、实验场景、指标结果和结论。当前为骨架版本，后续由批量实验结果和报告图表逐步填充。

## 1. 算法主线

```text
官方 PID baseline
→ 改进 PID
→ PID-INDI / MPC-INDI
→ L1-inspired 扰动补偿
→ Safety / Fault Reallocation
→ Trackability-aware Planning
→ Formation
```

## 2. 核心对比实验

| 场景 | 对比对象 | 指标 |
|---|---|---|
| hover_nominal | PID vs improved PID | steady_error, control_energy |
| step_nominal | PID vs improved PID | overshoot, settling_time |
| figure8_nominal | baseline vs optimized | RMSE, max_error |
| figure8_wind | with/without compensation | recovery_time, RMSE |
| motor_fault_eta70 | with/without reallocation | max_error, saturation_ratio |
| obstacle_formation_replay | planning/formation | trackability_score, min_inter_uav_distance |

## 3. 必备图表

```text
3D 参考/实际轨迹
位置误差曲线
姿态误差曲线
电机输入曲线
RMSE 对比柱状图
风扰恢复曲线
故障事件时间轴
健康度评分雷达图
```

## 4. 数据来源

所有报告结论必须来自：

```text
results/raw/
results/metrics/
results/figures/
mcp_log.json
```
