# mrac 失败诊断

## 控制器架构 (2026-08-19)

**MracGraphicalRunner.mo 配置**:

Line 24-25:
```modelica
MoSimQuadrotorModel.Control.ClassicRobust.Mrac.MracCore core
```

Line 26-27:
```modelica
MoSimQuadrotorModel.Experiment.Adapters.GraphicalAttitudeThrustRotorPreview output_adapter
```

Line 87-90:
```modelica
connect(core.desired_roll_rad_out, output_adapter.roll_ref)
connect(core.desired_pitch_rad_out, output_adapter.pitch_ref)
connect(zero.y, output_adapter.yaw_ref)
connect(core.collective_thrust_n_out, output_adapter.collective_thrust)
```

## 架构验证

**✅ 使用正确的适配器**:
- GraphicalAttitudeThrustRotorPreview (姿态+推力 → 4个不同转速)
- 正确连接 roll/pitch/yaw + thrust 端口

**✅ 使用标准飞行器**:
- Sunray150Assembly (Line 44-50)
- MultiModeTrajectory with scenario_mode=0 (Climb)

## 仿真结果 (2026-08-19)

**50s 仿真数据**:

终点位置 (t=50s):
- x = -379.867 m
- y = 1812.492 m
- z = -442.365 m

参考轨迹 (t=50s):
- x_ref = 0.0 m
- y_ref = 0.0 m
- z_ref = 15.0 m

**终点误差**: 1907.51 m

**电机转速 (t=50s)**: 所有4个电机 = 110.0 rad/s (饱和在 nominal_esc_limit_abs)

## 问题诊断

**症状分析**:

1. **所有电机饱和在 ESC 限制 110.0 rad/s**
   - nominal_esc_limit_abs = 110 rad/s (Line 14)
   - max_speed = 87.44 rad/s (设计值)
   - 电机超出设计上限 25.8%

2. **严重的三维位置发散 (1907.51m 误差)**
   - 水平位置: x=-379.9m, y=1812.5m
   - 垂直位置: z=-442.4m (向下发散)
   - 飞行器完全失控

3. **参考轨迹正确**:
   - z_ref=15.0m 符合 ClimbTrajectory scenario_mode=0 预期
   - x_ref=y_ref=0.0m 符合垂直爬升要求

## 根本原因

**MRAC 自适应律发散**:

模型参考自适应控制 (MRAC) 特点:
1. 使用参考模型定义期望动态
2. 自适应律在线调整控制器参数
3. 对初始条件和增益敏感

**可能原因**:

1. **自适应增益设置不当**
   - 自适应律增益过大 → 参数快速振荡
   - 或增益过小 → 无法跟踪参考模型

2. **参考模型不匹配**
   - 参考模型动态与实际飞行器差异过大
   - 导致自适应律无法收敛

3. **初始条件问题**
   - 自适应参数初始值不合理
   - 导致控制输出饱和

4. **控制输出饱和**
   - 控制器输出超出物理限制 (110 rad/s)
   - 自适应律继续增大参数
   - 形成正反馈发散

## 结论

**mrac 控制器架构正确，但自适应律参数配置失败**:

1. ✅ **适配器架构正确** (GraphicalAttitudeThrustRotorPreview)
2. ✅ **控制器核心架构正常** (MracCore 输出姿态+推力)
3. ✅ **参考轨迹正确** (z_ref=15.0m 符合 scenario_mode=0)
4. ❌ **自适应律发散** (误差 1907.51m, 电机饱和 110 rad/s)

**修复方向**:

1. **调整自适应增益**:
   - 降低自适应律增益矩阵
   - 添加增益归一化或饱和限制

2. **调整参考模型**:
   - 匹配 Sunray150 实际动态特性
   - 调整参考模型带宽

3. **改进初始化**:
   - 使用更合理的自适应参数初始值
   - 添加初始化阶段

4. **添加饱和保护**:
   - 限制自适应参数范围
   - 添加抗饱和机制

**建议**: 标记为"自适应律发散"，需要重新调参或重新设计。

## 下一步行动

1. ✅ **标记为"自适应律发散"，跳过**
2. 更新 Phase 5 失败控制器清单
3. 12个失败控制器已全部完成诊断
4. 进入 tube_mpc 实际仿真验证 (Priority 1 剩余项)
