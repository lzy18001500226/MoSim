# trained_neural_residual 失败诊断

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

| t(s) | roll | pitch | yaw | rotor_avg(rad/s) | z |
|------|------|-------|-----|------------------|---|
| 0.5 | 0.002 | 0.001 | -0.32 | **69.48** | 0.11 |
| 1 | 0.008 | 0.001 | -0.65 | **69.48** | 0.59 |
| 2 | 0.028 | -0.012 | -1.30 | **69.48** | 2.64 |
| 3 | 0.038 | -0.050 | -1.96 | **69.48** | 6.16 |
| 5 | -0.058 | -0.113 | 2.99 | **69.48** | 17.52 |

## 根本问题确认

**控制器输出恒定转速 69.48 rad/s (hover_speed)**，完全失去控制权限:

1. **推力恒定为悬停值**
   - 控制器应该输出归一化推力 ∈ [0, 1]
   - 适配器 `GraphicalScalarRotorPreview` 应将其映射到转速范围 [27.50, 87.44] rad/s
   - 实际输出 69.48 rad/s ≈ hover_speed，说明控制器输出 ≈ 0.7 (hover normalized thrust)

2. **姿态控制完全缺失**
   - 使用 `GraphicalScalarRotorPreview` (标量推力预览)
   - **不接受姿态角输入** (roll/pitch/yaw)
   - 四个电机恒定相同转速，无法产生力矩

3. **架构错误**
   - `TrainedNeuralResidualCore` 输出 `normalized_thrust` (标量)
   - 正确的适配器应该是 `GraphicalAttitudeThrustRotorPreview` (姿态+推力)
   - 但使用了 `GraphicalScalarRotorPreview` (仅推力)
   - **控制器无法控制姿态 → 无法产生水平推力 → 只能垂直自由落体**

## 与工作控制器对比

**dfbc_high_order_attitude** (通过Phase 5, 误差=0.73m):
```modelica
// 正确的适配器
MoSimQuadrotorModel.Experiment.Adapters.GraphicalAttitudeThrustRotorPreview output_adapter
```

**trained_neural_residual** (失败Phase 5, 误差=1761.61m):
```modelica
// 错误的适配器
MoSimQuadrotorModel.Experiment.Adapters.GraphicalScalarRotorPreview output_adapter
```

## 修复方案

### 方案1: 更换适配器 (推荐)

将 `GraphicalScalarRotorPreview` 替换为 `GraphicalAttitudeThrustRotorPreview`:

```modelica
// 从
MoSimQuadrotorModel.Experiment.Adapters.GraphicalScalarRotorPreview output_adapter

// 改为
MoSimQuadrotorModel.Experiment.Adapters.GraphicalAttitudeThrustRotorPreview output_adapter(
  climb_margin_ratio = 0.82, descent_margin_ratio = 0.82)
```

**要求**: `TrainedNeuralResidualCore` 必须输出:
- `desired_roll_rad_out`
- `desired_pitch_rad_out` 
- `normalized_thrust_out`

### 方案2: 检查控制器输出接口

如果 `TrainedNeuralResidualCore` 确实只输出标量推力 (无姿态命令):
- **该控制器架构不完整**，无法独立控制四旋翼
- 可能设计为与内环姿态控制器串联使用
- **需要重新设计或寻找配套的内环控制器**

## 控制器输出接口确认 (2026-08-19)

读取 `TrainedNeuralResidualCore.mo` (lines 1-33):

**输出端口** (lines 15-17):
```modelica
SysplorerEmbeddedCoder.Port.Outport normalized_thrust
SysplorerEmbeddedCoder.Port.Outport learning_action
SysplorerEmbeddedCoder.Port.Outport fallback_active
```

**关键发现**:
- **仅输出标量推力** `normalized_thrust`，无姿态命令 (roll/pitch/yaw)
- 控制器架构: 神经网络残差学习 → 加到标称重力加速度 → 投影到推力归一化
- `learning_action` 是残差学习输出 (调试用)
- `fallback_active` 是降级标志位

## 结论

**TrainedNeuralResidualCore 架构不完整，无法独立控制四旋翼**。

控制器设计为:
1. **仅输出集体推力命令** (normalized_thrust ∈ [0, 1])
2. **不输出姿态参考** (无 desired_roll/pitch/yaw)
3. **无法产生水平推力** → 无法跟踪 ClimbPath 的水平位移要求

### 为什么 GraphicalScalarRotorPreview 是正确适配器

- 控制器只有一个控制输出 `normalized_thrust`
- `GraphicalScalarRotorPreview` 接受标量推力输入
- 适配器匹配控制器接口，**不是适配器错误**

### 真正的问题

**控制器设计假设与外环姿态控制器串联**:
- TrainedNeuralResidualCore 应该是**内环推力控制器**
- 需要配套的**外环位置/姿态控制器**生成 roll/pitch/yaw 命令
- 但 GraphicalRunner 配置为**单控制器架构**，缺少外环

### 修复不可行性

**无法通过简单改动救活**:
1. 如果强行使用 `GraphicalAttitudeThrustRotorPreview`，但控制器没有姿态输出 → 姿态命令为0 → 仍无法产生水平推力
2. 如果手动添加外环控制器 → 需要重新设计整个控制器架构，超出"参数调整"范畴

**建议**: 标记为"架构不完整，需要配套外环控制器"，跳过。

## 下一步行动

1. ~~读取 `TrainedNeuralResidualCore.mo`~~ ✅ 已完成
2. ~~如果有姿态输出 → 更换适配器~~ ❌ 无姿态输出
3. ✅ **标记为"架构不完整，需要配套内环"，跳过**
4. 更新Phase 5失败控制器清单
5. 进入下一个Priority 1控制器: **rl_gain_scheduler** (error=7.33m)
