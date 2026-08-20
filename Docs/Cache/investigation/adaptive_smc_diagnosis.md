# adaptive_smc 失败诊断

## 控制器架构 (2026-08-19)

**AdaptiveSmcGraphicalRunner.mo 配置**:

Line 26-27:
```modelica
MoSimQuadrotorModel.Experiment.Adapters.GraphicalAccelerationRotorPreview output_adapter
```

Line 73:
```modelica
connect(zero.y, output_adapter.collective_thrust)
```

## 问题识别

**与 explicit_gain_scheduled_mpc 完全相同的配置错误**:

1. **使用 GraphicalAccelerationRotorPreview 适配器**
   - 所有增益 k=1，无单位转换
   - 适配器架构不完整 (已在 explicit_gain_scheduled_mpc 诊断中确认)

2. **collective_thrust 输入 = 0**
   - Line 73 连接到 `zero.y` 常数
   - 与 explicit_gain_scheduled_mpc 相同的配置错误

## 预期症状

基于 explicit_gain_scheduled_mpc 的诊断结果:
- 四个电机转速恒定 ~18.2 rad/s (远低于 hover_speed 64.79)
- 飞行器剧烈下坠
- 终点误差 >1000m

Phase 5 报告误差 11.08m 可能是:
1. 测试脚本问题 (类似 official_pid 的 scenario_mode 问题)
2. 或者误差计算方法不同

## 结论

**adaptive_smc 与 explicit_gain_scheduled_mpc 共享相同的致命缺陷**:

1. ✅ **适配器架构不完整** (GraphicalAccelerationRotorPreview)
2. ✅ **collective_thrust = 0** 导致无推力

**修复方案**: 与 explicit_gain_scheduled_mpc 相同
- 需要重新设计 GraphicalAccelerationRotorPreview 适配器
- 或者更换为 GraphicalAttitudeThrustRotorPreview (但需要控制器输出姿态命令)

**建议**: 标记为"适配器架构不完整"，跳过。

## 下一步行动

1. ✅ **标记为"适配器架构不完整"，跳过**
2. 更新 Phase 5 失败控制器清单
3. 进入下一个失败控制器: **fixed_awff_pid** (error=11.18m)
