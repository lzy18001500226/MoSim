# fixed_awff_pid 失败诊断

## 控制器架构 (2026-08-19)

**FixedAwffPidFamilyRunner 继承链**:

1. `FixedAwffPidFamilyRunner` → 继承自 
2. `FixedAwffPid` → 继承自 
3. `Example1AWFFSysblockClosedLoop`

## 架构分析

**Example1AWFFSysblockClosedLoop.mo 配置**:

Line 10:
```modelica
MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath climbePath(gain(k = 1));
```

Line 11:
```modelica
MoSimQuadrotorModel.Vehicle.Mechanics.QuadChassis quadChassisTest17_1;
```

Line 37:
```modelica
AWFF_FullControllerEquation_Sysblock controller3_2;
```

**关键特征**:
1. **使用 ClimbPath 轨迹生成器** (不是 MultiModeTrajectory)
2. **使用 QuadChassis 机械模型** (不是 Sunray150Assembly)
3. **使用 Actuator 驱动器模型** (不是 ESCDrive + RotorCommandChannel)
4. **使用 AWFF_FullControllerEquation_Sysblock 控制器核心**

## 问题识别

**与其他 38 个控制器使用完全不同的飞行器模型**:

**标准模板** (其他 38 个控制器):
- 轨迹: `MultiModeTrajectory` (scenario_mode 参数化)
- 飞行器: `Sunray150Assembly` (完整的 Gazebo SDF 物理模型)
- 驱动: `ESCDrive` + `RotorCommandChannel`
- 传感器: `PerceptionInterface` + `FlightController`

**fixed_awff_pid 模板**:
- 轨迹: `ClimbPath` (固定爬升轨迹)
- 飞行器: `QuadChassis` (简化机械模型)
- 驱动: `Actuator` (直接电机模型)
- 传感器: `Sensors` (简化传感器)

## 兼容性问题

**ClimbPath vs MultiModeTrajectory**:
- ClimbPath 可能有不同的高度参数或时间参数
- 需要检查 ClimbPath 的终点高度是否 = 15m

**QuadChassis vs Sunray150Assembly**:
- 简化模型可能缺少气动阻力、陀螺效应、螺旋桨干扰等
- 可能导致控制性能差异

**Phase 5 测试兼容性**:
- Phase 5 测试脚本可能假设所有控制器使用相同的模板
- fixed_awff_pid 使用不同的模板可能导致测试失败

## 结论

**fixed_awff_pid 使用遗留的 Example1 模板架构**:

1. ✅ **控制器核心可能工作正常** (AWFF PID)
2. ❌ **飞行器模型不一致** (QuadChassis vs Sunray150Assembly)
3. ❌ **轨迹生成器不一致** (ClimbPath vs MultiModeTrajectory)
4. ❌ **需要重新适配到标准模板**

**误差 11.18m 的可能原因**:
- ClimbPath 终点高度不是 15m
- QuadChassis 物理特性差异导致跟踪误差
- 控制器增益针对 QuadChassis 调优，不适合 Sunray150Assembly

**建议**: 标记为"需要重新适配到标准模板"，跳过。

## 下一步行动

1. ✅ **标记为"模板架构不一致"，跳过**
2. 更新 Phase 5 失败控制器清单
3. 进入下一个失败控制器: **gain_scheduled_pid** (error=11.53m)
