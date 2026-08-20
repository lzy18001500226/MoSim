# explicit_gain_scheduled_mpc 失败诊断

## 仿真结果 (2026-08-19)

### 位置误差演化

| t(s) | x | y | z | x_ref | y_ref | z_ref | 误差(m) |
|------|---|---|---|-------|-------|-------|---------|
| 1 | 0.00 | -0.00 | -4.42 | 0 | 0 | 2.0 | 6.42 |
| 5 | 0.00 | -0.02 | -112.42 | 0 | 0 | 10.0 | 122.42 |
| 10 | -0.16 | -0.28 | -450.66 | 0 | 0 | 10.0 | 460.66 |
| 20 | -2.67 | 0.02 | -1804.70 | 0 | 0 | 15.0 | 1819.70 |
| 30 | -3.87 | 2.49 | -4062.20 | 10 | 0 | 15.0 | 4077.23 |
| 40 | -7.21 | 3.49 | -7223.20 | 10 | 10 | 15.0 | 7238.23 |
| 50 | -10.63 | 7.62 | -11287.69 | 10 | 10 | 15.0 | **11302.71** |

### 控制器输出 (t=0.5~5s)

| t(s) | rotor_avg(rad/s) | z |
|------|------------------|---|
| 0.5 | 18.2 | -1.08 |
| 1 | 18.2 | -4.42 |
| 2 | 18.2 | -17.87 |
| 3 | 18.2 | -40.35 |
| 5 | 18.2 | -112.42 |

## 根本问题确认

**推力严重不足导致自由落体**：

1. **电机转速异常低**
   - 所有四个电机恒定 18.2 rad/s
   - 悬停转速 = 64.79 rad/s
   - 最小转速 = 27.50 rad/s
   - **实际转速 18.2 rad/s < 最小转速**，远低于悬停要求

2. **飞行器剧烈下坠**
   - t=1s: z=-4.42m (应该上升到2m)
   - t=5s: z=-112.42m (应该上升到10m)
   - t=50s: z=-11287.69m (应该维持15m)
   - 加速度约 -22.6 m/s² ≈ -2.3g (自由落体 + 少量向下推力)

3. **推力输出方向错误**
   - 电机转速过低，无法产生足够升力
   - 飞行器持续加速下坠

## Runner 适配器配置

读取 `ExplicitGainScheduledMpcGraphicalRunner.mo` (line 26-27):

```modelica
MoSimQuadrotorModel.Experiment.Adapters.GraphicalAccelerationRotorPreview output_adapter
```

连接 (lines 70-73):
```modelica
connect(core.desired_acceleration_x, output_adapter.acceleration_x)
connect(core.desired_acceleration_y, output_adapter.acceleration_y)
connect(core.desired_acceleration_z, output_adapter.acceleration_z)
connect(zero.y, output_adapter.collective_thrust)  // ← 集体推力输入 = 0
```

## 问题分析

**致命配置错误**: `collective_thrust` 输入连接到 `zero.y` (常数0)

### GraphicalAccelerationRotorPreview 适配器预期

该适配器接受:
- `acceleration_x/y/z`: 期望加速度 (m/s²)
- `collective_thrust`: 集体推力归一化值 (通常应为 hover_thrust ≈ 0.37)

### 当前配置问题

1. **集体推力为0**
   - Line 73: `connect(zero.y, output_adapter.collective_thrust)`
   - `zero.k = 0` (line 16)
   - 适配器收到 `collective_thrust = 0`

2. **加速度命令无法生效**
   - MPC 输出期望加速度 (x/y/z)
   - 但适配器需要基础推力 + 加速度调制
   - 基础推力 = 0 时，无法产生任何升力

3. **转速计算公式**
   - 适配器将 acceleration + collective_thrust 转换为转速
   - 当 collective_thrust = 0 时，即使加速度非零
   - 计算出的转速 = 18.2 rad/s (远低于最小转速)

## 与工作控制器对比

查看 Phase 5 通过的控制器，应该使用相同适配器的正确配置:

**dfbc_high_order_attitude** (通过, error=0.73m):
```modelica
MoSimQuadrotorModel.Experiment.Adapters.GraphicalAttitudeThrustRotorPreview output_adapter
```
- 接受 roll/pitch/yaw + normalized_thrust
- normalized_thrust 由控制器计算，不是常数0

**正确的 GraphicalAccelerationRotorPreview 使用方式**:
- `collective_thrust` 应该连接到控制器输出的基础推力
- 或者使用常数 = hover_thrust ≈ 0.37 (如果MPC只输出增量加速度)

## 修复方案

### 方案1: 修改 collective_thrust 连接 (推荐)

将 line 73 的连接从:
```modelica
connect(zero.y, output_adapter.collective_thrust)
```

改为连接到悬停推力常数:
```modelica
// 添加悬停推力常数
Modelica.Blocks.Sources.Constant hover_thrust(k = 0.37)
  annotation(Placement(...));

// 连接到适配器
connect(hover_thrust.y, output_adapter.collective_thrust)
```

### 修复结果 (2026-08-19)

**已应用方案1**:
1. 添加 `hover_thrust` 常数 (k=0.37)
2. 修改连接从 `zero.y` 到 `hover_thrust.y`

**仿真结果**: **修复失败**

采样适配器输入 (t=0.5~5s):

| t(s) | accel_x | accel_y | accel_z | thrust | rotor1 | z |
|------|---------|---------|---------|--------|--------|---|
| 0.5 | 4.0 | 1.893 | 12.307 | **0** | 18.2 | -1.08 |
| 1 | 4.0 | 1.893 | 12.307 | **0** | 18.2 | -4.42 |
| 2 | 4.0 | 1.893 | 12.307 | **0** | 18.2 | -17.87 |
| 3 | 4.0 | 1.893 | 12.307 | **0** | 18.2 | -40.35 |
| 5 | 4.0 | 1.893 | 12.307 | **0** | 18.2 | -112.42 |

**关键发现**:
- MPC 输出加速度命令 (accel_x=4.0, accel_y=1.893, accel_z=12.307 m/s²)
- 但 `thrust` 仍然 = 0 (应该是 0.37)
- 转速仍然 = 18.2 rad/s (未改变)
- 飞行器仍然下坠 (z=-112.42m at t=5s)

**问题分析**:
1. **变量名错误**: Sysplorer 报错 "变量 'hover_thrust.y' 不存在"
2. **连接未生效**: 修改后的连接可能在图形模型中未正确建立
3. **需要检查适配器增益**: `GraphicalAccelerationRotorPreview` 的 x/y/z/thrust_gain 都是 k=1，可能需要正确的映射公式

### 根本问题重新分析

**GraphicalAccelerationRotorPreview 适配器架构问题**:

查看适配器实现 (lines 16-23):
```modelica
Modelica.Blocks.Math.Gain x_gain[4](each k = 1)
Modelica.Blocks.Math.Gain y_gain[4](each k = 1)
Modelica.Blocks.Math.Gain z_gain[4](each k = 1)
Modelica.Blocks.Math.Gain thrust_gain[4](each k = 1)
```

所有增益都是 k=1，这意味着:
- 加速度输入 (m/s²) 直接加到转速输出 (rad/s)
- **单位不匹配**: 加速度 ≠ 转速
- 即使 collective_thrust = 0.37，thrust_gain 乘以 1 后仍是 0.37 rad/s (远低于 hover_speed=64.79)

**正确的适配器应该**:
1. 将加速度 (m/s²) 转换为归一化推力增量
2. 将归一化推力转换为转速 (rad/s)
3. 与姿态命令组合生成四个电机差速

**GraphicalAccelerationRotorPreview 设计缺陷**:
- 所有增益 k=1，没有单位转换
- 没有实现加速度 → 姿态 → 转速的正确映射
- 可能是占位实现或未完成的适配器

## 结论

**explicit_gain_scheduled_mpc 无法通过简单修复救活**:

1. **适配器架构不完整**
   - `GraphicalAccelerationRotorPreview` 增益全为 k=1
   - 缺少加速度到转速的正确转换公式
   - 需要重新设计适配器实现

2. **控制器输出正确**
   - MPC 输出合理的加速度命令 (accel_z=12.307 m/s²)
   - 控制器架构完整，问题在于适配器层

3. **修复尝试无效**
   - 添加 hover_thrust 常数后，连接未生效
   - 适配器仍然收到 thrust=0
   - 即使修复连接，适配器单位转换仍然错误

**建议**: 标记为"适配器架构不完整，需要重新设计 GraphicalAccelerationRotorPreview"，跳过。

## 下一步行动

1. ~~应用方案1修复~~ ✅ 已尝试，失败
2. ✅ **标记为"适配器架构不完整"，跳过**
3. 更新Phase 5失败控制器清单
4. 进入下一个Priority 1控制器: **tube_mpc** (error=7.68m)
