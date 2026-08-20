# rl_gain_scheduler 失败诊断

## 仿真结果 (2026-08-19)

### 位置误差演化

| t(s) | x | y | z | x_ref | y_ref | z_ref | 误差(m) |
|------|---|---|---|-------|-------|-------|---------|
| 1 | 0.00 | -0.01 | 0.59 | 0 | 0 | 2.0 | 1.41 |
| 5 | -2.68 | -2.22 | 17.52 | 0 | 0 | 10.0 | 8.28 |
| 10 | -16.30 | 8.69 | 69.90 | 0 | 0 | 10.0 | 62.69 |
| 20 | -49.04 | 39.22 | 275.88 | 0 | 0 | 15.0 | 268.33 |
| 30 | -103.74 | 95.93 | 623.34 | 10 | 0 | 15.0 | 626.27 |
| 40 | -174.37 | 174.70 | 1109.21 | 10 | 10 | 15.0 | 1121.79 |
| 50 | -267.38 | 279.60 | 1733.62 | 10 | 10 | 15.0 | **1761.61** |

### 控制器输出 (t=0.5~5s)

| t(s) | thrust | rotor_avg(rad/s) | z |
|------|--------|------------------|---|
| 0.5 | 1.0 | 69.48 | 0.11 |
| 1 | 1.0 | 69.48 | 0.59 |
| 2 | 1.0 | 69.48 | 2.64 |
| 3 | 1.0 | 69.48 | 6.16 |
| 5 | 1.0 | 69.48 | 17.52 |

## 根本问题确认

**与 trained_neural_residual 完全相同的症状**：控制器输出恒定转速 69.48 rad/s (hover_speed)，完全失去控制权限。

### 控制器输出接口确认

读取 `RlGainSchedulerCore.mo` (lines 1-33):

**输出端口** (lines 15-17):
```modelica
SysplorerEmbeddedCoder.Port.Outport normalized_thrust
SysplorerEmbeddedCoder.Port.Outport learning_action
SysplorerEmbeddedCoder.Port.Outport fallback_active
```

**架构分析**:
- 控制器架构: 状态特征向量 → 冻结策略推理 → 增益调度边界 → 标称增益调制 → 推力归一化
- **仅输出标量推力** `normalized_thrust` ∈ [0, 1]
- **无姿态命令** (roll/pitch/yaw)
- `learning_action` 是增益调度输出 (调试用)
- `fallback_active` 是降级标志位

### Runner 适配器配置

读取 `RlGainSchedulerGraphicalRunner.mo` (line 26-27):

```modelica
MoSimQuadrotorModel.Experiment.Adapters.GraphicalScalarRotorPreview output_adapter
```

连接 (line 70):
```modelica
connect(core.normalized_thrust, output_adapter.command)
```

### 问题分析

**与 trained_neural_residual 完全相同的架构缺陷**:

1. **控制器设计为标量推力输出**
   - 只能控制集体推力 (所有电机转速相同)
   - 无法产生姿态力矩 (roll/pitch/yaw)
   - 无法生成水平推力分量

2. **适配器选择正确但架构不完整**
   - `GraphicalScalarRotorPreview` 匹配控制器输出接口
   - 但单独的标量推力控制器无法完成位置跟踪任务

3. **控制器输出异常**
   - `normalized_thrust = 1.0` (饱和在上限)
   - 转速恒定 69.48 rad/s = hover_speed
   - 推力计算公式疑似错误

## 仿真数据矛盾分析

**关键矛盾**: 控制器输出 `normalized_thrust = 1.0`，但四个电机转速 = 69.48 rad/s (hover速度)

### 推力归一化公式验证

根据 `GraphicalScalarRotorPreview` 适配器 (假设与 `GraphicalAttitudeThrustRotorPreview` 相同):

```
rotor_speed = min_speed + normalized_thrust × speed_range
            = 27.50 + 1.0 × 59.94
            = 87.44 rad/s  (应该是最大转速)
```

但实际输出 = 69.48 rad/s ≈ hover_speed

**可能原因**:
1. `GraphicalScalarRotorPreview` 使用不同的归一化公式
2. 适配器内部有额外的限制或偏置
3. ESC 或电机模块对高转速命令进行了限制

### 推力异常输出

控制器输出 `normalized_thrust = 1.0` (饱和) 可能原因:

1. **控制器增益配置错误**
   - `attitude_thrust_projection.k = 0.34` 可能不匹配平台参数
   - `bounded_gain_schedule` 范围 [-0.25, 0.25] 可能过小

2. **强化学习策略未正确训练**
   - `frozen_policy_inference.k = 0.35` 可能是占位参数
   - 实际策略网络权重缺失或未加载

3. **状态输入错误**
   - `measured_state.k = 0.55` 是常数，不是真实状态
   - 控制器没有接收位置/速度反馈

## 结论

**rl_gain_scheduler 与 trained_neural_residual 共享相同的架构缺陷**：

1. **标量推力控制器设计**
   - 只能控制垂直运动，无法产生水平推力
   - 需要配套的外环姿态控制器

2. **控制器输出异常**
   - `normalized_thrust = 1.0` 饱和
   - 但实际电机转速 = hover_speed (未达到最大)
   - 需要进一步检查适配器实现

3. **架构不完整**
   - 单独的标量推力控制器无法完成 ClimbPath 任务
   - 需要重新设计为完整的位置-姿态控制器架构

**建议**: 标记为"架构不完整，需要配套外环控制器"，跳过。

## 下一步行动

1. ~~读取 `RlGainSchedulerCore.mo`~~ ✅ 已完成
2. ~~确认输出接口~~ ✅ 仅标量推力输出
3. ✅ **标记为"架构不完整，需要配套外环控制器"，跳过**
4. 更新Phase 5失败控制器清单
5. 进入下一个Priority 1控制器: **explicit_gain_scheduled_mpc** (error=7.45m)
