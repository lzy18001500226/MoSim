# fuzzy_pid 失败诊断

## 控制器架构 (2026-08-19)

**FuzzyPidGraphicalRunner.mo 配置**:

Line 24-25:
```modelica
MoSimQuadrotorModel.Control.PidFamily.FuzzyPid.FuzzyPidCore core
```

Line 26-27:
```modelica
MoSimQuadrotorModel.Experiment.Adapters.GraphicalScalarRotorPreview output_adapter
```

Line 70:
```modelica
connect(core.command, output_adapter.command)
```

## 问题识别

**与 gain_scheduled_pid 完全相同的架构缺陷**:

1. **使用 GraphicalScalarRotorPreview 适配器**
   - 输入: 单个标量 `command` (归一化推力 0~1)
   - 输出: 4个相同的转速 `rotor_command[1:4]`
   - 映射公式: `speed = min_speed + command × (max_speed - min_speed)`

2. **控制器输出**:
   - FuzzyPidCore 输出单个标量 `command`
   - **无姿态控制输出** (无 roll/pitch/yaw 端口)

## 致命缺陷

**GraphicalScalarRotorPreview 无法控制姿态**:

**正常姿态控制链**:
- 控制器输出: roll/pitch/yaw + thrust → 4个不同的转速
- 通过差动控制4个电机实现姿态调整

**GraphicalScalarRotorPreview 架构**:
- 控制器输出: 单个标量 → 4个**相同**的转速
- **所有电机转速相同** → 无法产生姿态力矩
- 飞行器只能垂直上升/下降，无法稳定姿态

## 预期症状

基于 GraphicalScalarRotorPreview 的物理限制:
- 4个电机转速始终相同
- 无法抵抗姿态扰动
- 飞行器姿态失控翻滚
- 水平位置发散
- 终点误差 >10m

Phase 5 报告误差 14.51m 符合预期。

## 结论

**fuzzy_pid 使用了错误的适配器架构**:

1. ✅ **控制器核心可能工作正常** (模糊PID)
2. ❌ **适配器架构根本性缺陷** (GraphicalScalarRotorPreview)
3. ❌ **无法控制姿态** (4个电机转速恒定相同)
4. ❌ **需要重新设计适配器或控制器输出接口**

**修复方案**: 
- 方案1: 将 GraphicalScalarRotorPreview 替换为 GraphicalAttitudeThrustRotorPreview
  - 需要控制器输出姿态命令 (roll/pitch/yaw + thrust)
  - 需要修改 FuzzyPidCore 架构
- 方案2: 重新设计 GraphicalScalarRotorPreview 以支持姿态控制
  - 需要添加内部姿态反馈环
  - 本质上变成完整的姿态控制器

**建议**: 标记为"适配器架构缺陷"，跳过。

## 下一步行动

1. ✅ **标记为"适配器架构缺陷"，跳过**
2. 更新 Phase 5 失败控制器清单
3. 进入下一个失败控制器: **mrac** (error=14.99m)
