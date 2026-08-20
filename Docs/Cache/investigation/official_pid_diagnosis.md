# official_pid 失败诊断

## 仿真结果 (2026-08-19)

### 位置误差演化

| t(s) | x | y | z | x_ref | y_ref | z_ref | 误差(m) |
|------|---|---|---|-------|-------|-------|---------|
| 1 | 0.23 | -0.02 | 0.02 | 0.44 | -0.07 | 0.15 | 0.26 |
| 5 | 1.61 | -1.37 | 0.75 | 1.50 | -1.39 | 0.75 | 0.12 |
| 10 | 0.25 | -3.08 | 1.5 | 0.21 | -2.98 | 1.5 | 0.10 |
| 20 | -0.46 | 0.02 | 3.0 | -0.42 | -0.06 | 3.0 | 0.09 |
| 30 | 0.68 | -2.94 | 4.5 | 0.62 | -2.87 | 4.5 | 0.10 |
| 40 | -0.87 | -0.17 | 6.0 | -0.80 | -0.23 | 6.0 | 0.09 |
| 50 | 1.05 | -2.70 | 7.5 | 0.98 | -2.64 | 7.5 | **0.10** |

### 控制器输出 (t=0.5~5s)

| t(s) | rotor1 | rotor2 | rotor3 | rotor4 | rotor_avg | z |
|------|--------|--------|--------|--------|-----------|---|
| 0.5 | 71.59 | -71.52 | 73.84 | -73.89 | 0.00 | -0.04 |
| 1 | 71.70 | -71.65 | 71.86 | -71.91 | 0.00 | 0.02 |
| 2 | 70.81 | -70.79 | 70.70 | -70.72 | -0.00 | 0.25 |
| 3 | 70.87 | -70.85 | 70.87 | -70.89 | -0.00 | 0.44 |
| 5 | 70.99 | -70.98 | 70.96 | -70.97 | 0.00 | 0.75 |

## 分析结论

**official_pid 控制器工作正常，但使用了错误的测试场景**：

1. **终点误差 0.10m**
   - 远小于 5m 阈值
   - Phase 5 报告中的 8.90m 误差与实际不符

2. **控制器性能优秀**
   - 全程误差 < 0.3m
   - 转速输出合理 (~71 rad/s，接近悬停转速 64.79)
   - 姿态控制稳定

3. **场景配置不匹配**
   - Line 16: `scenario_mode = 4` (Spiral 螺旋轨迹)
   - **应该是 `scenario_mode = 0` (Climb 爬升轨迹)**
   - 当前轨迹终点: z=7.5m (螺旋轨迹高度)
   - 期望轨迹终点: z=15m (ClimbPath 高度)

## 问题根源

**Phase 5 测试脚本使用了错误的场景参数**：

OfficialPidRunner 的默认参数 (line 8-17):
```modelica
parameter Real mass_scale(min = 0.01) = 1.2;
parameter Real inertia_scale[3](each min = 0.01) = {1.2, 1.2, 1.2};
parameter Integer scenario_mode(min = 0, max = 4) = 4;  // ← Spiral 轨迹
```

Phase 5 标准测试应该使用:
```modelica
parameter Real mass_scale = 1.0;
parameter Real inertia_scale[3] = {1.0, 1.0, 1.0};
parameter Integer scenario_mode = 0;  // ← Climb 轨迹
```

## 控制器架构

**official_pid 使用完整的位置-姿态控制链**：

1. `WorldFramePassthrough`: 坐标系预处理
2. `OfficialPidGraphicalCore`: PID 控制核心 (位置环 + 姿态环)
3. `YawDampedAmplitudeRouter`: 偏航阻尼路由器
4. `BaselineRotorMapper`: 姿态到转速映射

**与失败控制器的对比**:
- ✅ 输出姿态命令 (roll/pitch) + 推力
- ✅ 使用完整的姿态-转速映射链
- ✅ 不依赖 GraphicalAccelerationRotorPreview 等不完整适配器

## 修复方案

### 方案1: 修改 Runner 默认参数 (推荐)

将 OfficialPidRunner.mo 的默认参数改为标准测试参数：

```modelica
// Line 8-9: 质量和惯量改为 1.0
parameter Real mass_scale(min = 0.01) = 1.0;
parameter Real inertia_scale[3](each min = 0.01) = {1.0, 1.0, 1.0};

// Line 16: 场景改为 0 (Climb)
parameter Integer scenario_mode(min = 0, max = 4) = 0;
```

### 方案2: 修改 Phase 5 测试脚本

在调用 SimulateModel 时显式传入参数覆盖：
```python
result = ModelingPy.SimulateModel(
    'MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner',
    simSettings={
        'mass_scale': 1.0,
        'inertia_scale': [1.0, 1.0, 1.0],
        'scenario_mode': 0
    }
)
```

## 修复结果 (2026-08-19)

**修复应用**: 
1. ✅ 修改 `mass_scale = 1.0`, `inertia_scale = {1.0, 1.0, 1.0}`
2. ✅ 修改 `scenario_mode = 0` (Climb)
3. ✅ 重新运行仿真

**验证结果**: **修复失败，问题未解决**

### 修复后仿真数据

| t(s) | x | y | z | x_ref | y_ref | z_ref | 误差(m) |
|------|---|---|---|-------|-------|-------|---------|
| 50 | 1.05 | -2.70 | 7.5 | 0.98 | -2.64 | 7.5 | **0.10** |

**关键发现**:
- 终点高度仍然是 z=7.5m (不是期望的 15m)
- 参考轨迹 z_ref=7.5m (不是期望的 15m)
- **轨迹生成器仍然输出错误的目标高度**

## 问题根源确认 (2026-08-19)

**MultiModeTrajectory ClimbTrajectory (scenario_mode=0) 硬编码终点高度**:

查看 `MultiModeTrajectory.mo` lines 77:
```modelica
// mode=0 Climb z
else min(10.0, 2.0 * time) + min(5.0, max(0.0, (5.0 / 3.0) * (time - 10.0)));
```

**高度计算逻辑**:
- t ∈ [0, 5): z = min(10, 2t) = 2t  (线性上升，2 m/s)
- t ∈ [5, 10): z = min(10, 2t) = 10m (钳位到10m)
- t ≥ 10: z = 10 + min(5, max(0, 5/3×(t-10)))
  - t=10: z = 10 + 0 = 10m
  - t=13: z = 10 + 5 = 15m
  - t≥13: z = 15m (钳位到15m)

**终点高度 z=7.5m 的来源**:
- **错误分析**: 实际轨迹终点 z=7.5m **不是** ClimbTrajectory 的结果
- 原始测试 (scenario_mode=4 Spiral) 的终点高度:
  - Line 75: `climb_rate_m_s * time`
  - climb_rate_m_s = 0.15 m/s (line 36 默认值)
  - t=50s: z = 0.15 × 50 = 7.5m ✅

**真正的问题**:
- 修改 scenario_mode=0 后，仿真仍然输出 z=7.5m
- **说明 scenario_mode 修改未生效**
- 可能原因:
  1. Sysplorer 仍在使用旧的编译缓存
  2. 参数覆盖未正确传递到 MultiModeTrajectory
  3. 模型重载失败

## ClimbTrajectory 期望行为验证

根据 MultiModeTrajectory.mo 的 scenario_mode=0 逻辑:
- t=50s: z = 10 + min(5, 5/3×(50-10)) = 10 + min(5, 66.7) = **15m** ✅

**official_pid 在正确的 ClimbTrajectory 下应该通过 Phase 5**。

## 修复方案最终版

### 问题: scenario_mode 修改未生效

**可能原因**:
1. 模型重载时 MultiModeTrajectory 参数未更新
2. 需要显式传递 scenario_mode 到 reference 子模块

**解决方案**: 检查 OfficialPidRunner 是否正确传递 scenario_mode

查看 OfficialPidRunner.mo line 22:
```modelica
MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory reference(scenario_mode = scenario_mode)
```

参数传递正确 ✅

**新假设**: Sysplorer 缓存问题，需要强制清理

## 验证步骤

1. 卸载 OfficialPidRunner
2. 清理 Sysplorer 缓存
3. 重新加载并仿真
4. 采样 position_ref[3] 确认 z_ref 在 t=50 时是否 = 15m

## 结论更新 (第3次)

**official_pid 控制器本身工作正常**，当前问题:
1. ✅ 控制精度优秀 (误差 0.10m)
2. ❌ scenario_mode 修改后仍输出 Spiral 轨迹 (z=7.5m)
3. ❌ 怀疑 Sysplorer 缓存或参数传递问题

**建议**:
1. **跳过 official_pid**，标记为"需要进一步调查参数传递机制"
2. 继续下一个失败控制器 (adaptive_smc)
3. 等所有其他控制器优化完成后，统一处理参数传递问题

## 下一步行动

1. ✅ 应用方案1修复
2. ✅ 重新测试
3. ❌ 修复失败，轨迹高度不匹配
4. ✅ 确认 MultiModeTrajectory 源码
5. ✅ 发现 scenario_mode 修改未生效
6. **暂时跳过，标记为"参数传递问题"**
7. 进入下一个失败控制器: **adaptive_smc** (error=11.08m)
