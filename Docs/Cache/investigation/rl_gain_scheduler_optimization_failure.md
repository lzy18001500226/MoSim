# rl_gain_scheduler 优化失败记录

## 优化时间
2026-08-19 Phase 5 优化尝试 #2

## 原始状态
- **排名**: #3 失败控制器（共12个）
- **原始误差**: 7.33m (Phase 5 ClimbPath 50s)
- **状态**: FAIL (终点误差 >= 5.0m)
- **原始诊断**: 架构不完整 - 强化学习策略未正确配置

## 修复方案（与 trained_neural_residual 相同）

### 文件1: `RlGainSchedulerCore.mo`

**添加姿态输出端口**（在 line 15-18 之后）:
```modelica
SysplorerEmbeddedCoder.Port.Outport roll_ref annotation(...);
SysplorerEmbeddedCoder.Port.Outport pitch_ref annotation(...);
SysplorerEmbeddedCoder.Port.Outport yaw_ref annotation(...);
```

**添加零值常数源**（在 line 18 之后）:
```modelica
SysplorerEmbeddedCoder.Sources.Constant roll_zero(k=0.0) annotation(...);
SysplorerEmbeddedCoder.Sources.Constant pitch_zero(k=0.0) annotation(...);
SysplorerEmbeddedCoder.Sources.Constant yaw_zero(k=0.0) annotation(...);
```

**添加连接语句**（在 equation section）:
```modelica
connect(roll_zero.y,roll_ref) annotation(...);
connect(pitch_zero.y,pitch_ref) annotation(...);
connect(yaw_zero.y,yaw_ref) annotation(...);
```

**调整输出端口位置**:
- `learning_action`: y=10 → y=-10（为新增端口腾出空间）

### 文件2: `RlGainSchedulerGraphicalRunner.mo`

**切换适配器类型**（line 26-27）:
```modelica
// 原: GraphicalScalarRotorPreview
// 改为: GraphicalAttitudeThrustRotorPreview
```

**修正适配器连接**（line 69-73）:
```modelica
connect(core.normalized_thrust, output_adapter.collective_thrust)
connect(core.roll_ref, output_adapter.roll_ref)
connect(core.pitch_ref, output_adapter.pitch_ref)
connect(core.yaw_ref, output_adapter.yaw_ref)
```

原始错误: `connect(core.normalized_thrust, output_adapter.command)` (端口不存在)

## 验证结果

### CheckModel验证
```json
{
  "ok": true,
  "api": "CheckModel",
  "data": true,
  "model_name": "MoSimQuadrotorModel.Experiment.Learning.RlGainSchedulerGraphicalRunner"
}
```
**状态**: ✅ PASS

### SimulateModel验证
```json
{
  "ok": true,
  "api": "SimulateModel",
  "data": true,
  "sim_mode": 1
}
```
**状态**: ✅ PASS

### Phase 5完整流水线验证
```
[ ] [36/38] rl_gain_scheduler    [FAIL] Error 9.99m
```
**终点误差**: **9.99m** (仍然 >= 5.0m 阈值)
**状态**: ❌ **FAIL**

## 优化效果

| 指标 | 优化前 | 优化后 | 改变 |
|------|--------|--------|------|
| 终点误差 | 7.33m | 9.99m | +2.66m (+36.3%) |
| Phase 5状态 | FAIL | **仍然FAIL** | ❌ 未通过 |
| 排名 | #3失败 | - | 仍在失败列表 |

## 问题分析

### 为什么修复失败？

与 `trained_neural_residual` 不同，`rl_gain_scheduler` 的架构修复虽然通过了 CheckModel 和 SimulateModel，但**终点误差反而增大**（7.33m → 9.99m）。

可能原因：
1. **控制增益不匹配**: 原始设计假设使用 `GraphicalScalarRotorPreview` 的特定增益关系
2. **姿态控制干扰**: 零值姿态参考可能与 RL 策略的预期行为冲突
3. **适配器映射差异**: `GraphicalScalarRotorPreview` 与 `GraphicalAttitudeThrustRotorPreview` 的推力映射关系不同
4. **RL 策略未正确冻结**: `frozen_policy_inference` 常数增益（k=0.35）可能不是真实的策略权重

### 关键参数对比

| 参数 | trained_neural_residual | rl_gain_scheduler |
|------|------------------------|-------------------|
| 特征提取增益 | 0.8 (feature_normalization) | 0.75 (state_feature_vector) |
| 策略推理增益 | 0.45 (hidden_layer_inference) | 0.35 (frozen_policy_inference) |
| 残差饱和限制 | ±0.25 | ±0.25 |
| 推力投影增益 | 0.34 | 0.34 |
| 标称加速度 | 9.80665 m/s² | 9.80665 m/s² |

增益差异较小，问题可能在于：
- RL 策略本身未正确训练或加载
- 适配器切换破坏了原始设计的闭环特性

## 结论

rl_gain_scheduler 架构修复**失败**，误差从 **7.33m → 9.99m**。

**问题根源**: 不是简单的端口缺失问题，而是控制器核心算法与适配器类型的深层耦合。

### 下一步行动

1. **放弃 rl_gain_scheduler 优化**: 需要重新训练 RL 策略或重新设计适配器
2. **跳过相同模式的控制器**: 检查其他失败控制器是否有类似的学习型架构
3. **优先处理非学习型控制器**: 如 `official_pid`（参数传递问题）、`fopid`（轨迹配置问题）

---

**文档创建**: 2026-08-19 06:24  
**验证方式**: 实际Sysplorer仿真（非推测）  
**修复类型**: 架构补全（失败）  
**失败原因**: 适配器切换导致性能恶化
