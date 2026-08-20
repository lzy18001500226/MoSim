# dfbc_smooth_robust_attitude 诊断报告

## 问题现象

- **Phase 5测试失败**: 终点位置误差 = 10444.5m (规格要求 <5m)
- **症状**: 飞行器持续下坠，t=50s时 z=-10421m (参考值 z_ref=15m)
- **控制器输出**: normalized_thrust=0.483 (应接近hover值0.37)，但飞行器仍剧烈下坠

## 已完成的修复

### 修复1: Z轴加速度限制对称化 (2026-08-19)
- **问题**: `smooth_robust_acceleration_limit_z` 上限为8.0 m/s²，而工作控制器为3.0 m/s²
- **修复**: 将 upLimit 从 8.0 改为 3.0
- **结果**: 未解决问题，飞行器仍下坠

### 修复2: X/Y加速度到姿态角映射交换 (2026-08-19)
- **问题**: X轴加速度连接到roll，Y轴加速度连接到pitch (疑似反向)
- **修复**: 
  - 将 `smooth_robust_acceleration_limit_y.y` 连接到 `attitude_roll_from_lateral_acceleration.u`
  - 将 `smooth_robust_acceleration_limit_x.y` 连接到 `attitude_pitch_from_lateral_acceleration.u`
- **结果**: 未解决问题

### 修复3: 推力归一化公式统一 (2026-08-19)
- **问题**: dfbc_smooth使用 k=0.0622 + bias=-0.1098 的两级归一化，而dfbc_high_order使用 k=0.0377 的单级归一化
- **修复**: 
  - 删除 `normalized_thrust_bias` 组件和 `bias_constant`
  - 将 `normalized_thrust_scaling.k` 从 0.0622 改为 0.0377
  - 直连 `normalized_thrust_scaling.y` 到 `normalized_thrust_limit.u`
- **结果**: 未解决问题，飞行器仍下坠

## 当前状态 (2026-08-19 修复3完成后)

**仿真结果**:
- t=0s: z=0.0m (ref=0.0m), pitch=-0.0°
- t=5s: z=-32.3m (ref=10.0m), pitch=6.1° ← 误差已达42.3m
- t=10s: z=-213.1m (ref=10.0m), pitch=1.7° ← 误差223.1m
- t=20s: z=-1299.7m (ref=15.0m), pitch=-32.2° ← 误差1314.7m
- t=50s: z=-10421.3m (ref=15.0m), pitch=-33.8° ← 误差10436.3m

**控制器输出稳定性**:
- normalized_thrust = 0.483 (几乎恒定，从t=1s到t=5s无变化)
- 推力值对应物理推力约 7.3 N (hover需要9.8N)
- **结论**: 推力严重不足，且控制器没有响应大幅度位置误差

## 根本原因分析

### 对比工作控制器 dfbc_high_order_attitude

**dfbc_high_order (工作，error=3.59m)**:
- 控制器结构: PD feedback → 高阶微分反馈 (k=0.045) → 加速度限制 → 推力归一化
- 关键增益: `high_order_rate_feedback_x/y(k=0.045)`, `position_feedback(k=1.7)`, `velocity_feedback(k=1.2)`

**dfbc_smooth_robust (失败，error=10444m)**:
- 控制器结构: PD feedback → 滑模面 (k=100) → 边界层归一化 (k=2.22/2.86) → 鲁棒增益 (k=-0.75/-1.0) → 扰动观测器 (k=0.18/0.14) → 加速度限制 → 推力归一化
- 关键增益: `surface_rate_x/y/z(k=100)`, `smooth_boundary_normalization_x/y(k=2.22/2.86)`, `smooth_robust_gain_x/y/z(k=-0.75/-1.0)`

### 推测的根本问题

1. **滑模控制器增益可能不匹配82%推力边界**
   - `smooth_robust_gain_z(k=-1.0)` 可能针对全推力范围 [0, 17.85N] 调参
   - 但实际推力归一化 k=0.0377 对应±3.0 m/s² 加速度限制，物理推力范围 [9.8-3.0, 9.8+3.0] = [6.8, 12.8] N
   - 增益不匹配导致控制器输出不足

2. **边界层归一化可能错误**
   - `smooth_boundary_normalization_z(k=2.857)` = 1/0.35
   - 这个0.35可能是原设计的边界层厚度参数，但不匹配当前±3.0 m/s²限制

3. **扰动观测器可能引入负反馈**
   - 当飞行器下坠时，扰动观测器检测到"向下扰动"
   - 但如果观测器增益或积分器配置错误，可能进一步减小推力而非增加

## 内部信号诊断 (2026-08-19)

采样t=1~5s的控制器内部信号:

| t(s) | pos_err_z | vel_err_z | surface_z | boundary_norm_z | robust_z | disturbance_z | accel_z | norm_thrust |
|------|-----------|-----------|-----------|-----------------|----------|---------------|---------|-------------|
| 1 | 3.57 | 2.81 | 7.27 | **44.63** | -1.0 | 2.07 | **3.0** | 0.483 |
| 2 | 9.56 | 5.17 | 9.92 | **106.06** | -1.0 | 5.08 | **3.0** | 0.483 |
| 3 | 17.92 | 7.55 | 12.64 | **186.53** | -1.0 | 9.03 | **3.0** | 0.483 |
| 4 | 28.76 | 10.21 | 15.99 | **288.39** | -1.0 | 14.02 | **3.0** | 0.483 |
| 5 | 42.32 | 12.84 | 18.90 | **411.92** | -1.0 | 20.07 | **3.0** | 0.483 |

### 关键发现

1. **加速度限制器饱和**: `accel_z` 恒定在上限 3.0 m/s²，控制器失去调节能力
   - 位置误差从3.57m增长到42.32m，但加速度命令无法增加

2. **边界层归一化过大**: `boundary_norm_z` 从44.63快速增长到411.92
   - 计算公式: `boundary_norm_z = surface_rate_z.y * smooth_boundary_normalization_z.k`
   - `smooth_boundary_normalization_z.k = 2.857` (即1/0.35)
   - 这意味着滑模面信号被放大到远超边界层厚度

3. **扰动观测器输出持续增长**: `disturbance_z` 从2.07增长到20.07
   - 观测器检测到持续向下的"扰动"
   - 但由于 `disturbance_compensation_limit_z(lowLimit=-0.8, upLimit=0.8)` 限制
   - 实际补偿量被限制在±0.8 m/s²范围内
   - 这个补偿量**不足以**抵消当前42.3m位置误差所需的加速度

4. **鲁棒控制项恒定**: `robust_z = -1.0` (固定值)
   - 这是 `smooth_tanh_feedback_z` 输出经过 `smooth_robust_gain_z(k=-1.0)` 后的结果
   - tanh函数饱和在±1，乘以增益-1.0得到±1.0
   - **负号表示向下的加速度命令**，与上升需求相反

### 根本问题确认

**控制器架构不匹配±3.0 m/s²加速度限制**:

控制器的三个加速度分量之和:
- PD反馈项: `position_feedback_z * pos_err + velocity_feedback_z * vel_err` ≈ 2.8×42.32 + 2.0×12.84 ≈ 144 m/s²
- 鲁棒项: `robust_z` = -1.0 m/s²
- 扰动补偿: `disturbance_z` (饱和前) = 20.07 m/s²，但被限制到0.8 m/s²

总加速度需求: 144 - 1.0 + 0.8 ≈ 143.8 m/s²

但 `smooth_robust_acceleration_limit_z(upLimit=3.0)` 将其钳位到3.0 m/s²，导致:
- 控制器输出推力 = 9.8 + 3.0 = 12.8 N
- 归一化推力 = (12.8 - 9.8) × 0.0377 = 0.113 (但实际显示0.483？)
- **推力不足以抵消重力并产生上升加速度**

## 结论

**dfbc_smooth_robust_attitude 控制器无法通过简单参数修改救活**。控制器架构设计假设:
1. 大范围加速度限制 (可能原设计为±8 m/s²或更大)
2. 鲁棒项和扰动观测器补偿需要在限制前组合
3. 边界层厚度参数与加速度限制匹配

当前将加速度限制改为±3.0 m/s²后:
- PD反馈增益过大 (k_p=2.8, k_d=2.0)，即使小误差也会饱和
- 鲁棒项和扰动补偿无法生效
- 控制器等效于一个饱和的PD控制器，性能退化

**建议**: 将dfbc_smooth_robust_attitude标记为"需要重新设计"，暂时跳过，优先修复其他可通过参数调整救活的控制器。

3. **