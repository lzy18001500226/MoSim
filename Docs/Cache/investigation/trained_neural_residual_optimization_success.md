# trained_neural_residual 优化成功记录

## 优化时间
2026-08-19 Phase 5 优化尝试 #1

## 原始状态
- **排名**: #2 失败控制器（共12个）
- **原始误差**: 6.93m (Phase 5 ClimbPath 50s)
- **状态**: FAIL (终点误差 >= 5.0m)
- **原始诊断**: 架构不完整 - 神经网络权重未加载或基线控制器参数不匹配

## 根本原因分析
通过读取 `TrainedNeuralResidualGraphicalRunner.mo` 发现：
1. **架构缺陷**: `TrainedNeuralResidualCore` 只输出 `normalized_thrust`，缺少姿态控制输出
2. **适配器类型**: 使用 `GraphicalAttitudeThrustRotorPreview` (正确类型)
3. **连接错误**: 原始代码试图将 `core.normalized_thrust` 连接到不存在的 `output_adapter.command`
4. **姿态控制缺失**: 没有 roll_ref/pitch_ref/yaw_ref 输出端口

## 修复方案
### 文件1: `TrainedNeuralResidualCore.mo`

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

### 文件2: `TrainedNeuralResidualGraphicalRunner.mo`

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
  "model_name": "MoSimQuadrotorModel.Experiment.Learning.TrainedNeuralResidualGraphicalRunner"
}
```
**状态**: ✅ PASS

### SimulateModel验证
```json
{
  "ok": true,
  "api": "SimulateModel",
  "data": true,
  "sim_mode": 0
}
```
**状态**: ✅ PASS

### Phase 5完整流水线验证
```
[ ] [38/38] trained_neural_residual    [PASS] Error 3.34m
```
**终点误差**: **3.34m** (< 5.0m 阈值)
**状态**: ✅ **PASS**

## 优化效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 终点误差 | 6.93m | 3.34m | -3.59m (-51.8%) |
| Phase 5状态 | FAIL | **PASS** | ✅ 通过 |
| 排名 | #2失败 | - | 移出失败列表 |

## 技术要点

### 为什么需要零值姿态输出？
`TrainedNeuralResidual` 是一个**残差学习控制器**:
- 主要功能：输出推力修正（normalized_thrust）
- 设计假设：姿态控制由基线控制器完成，残差学习仅增强推力控制
- 实际架构：需要显式提供姿态参考（即使为零）给 `GraphicalAttitudeThrustRotorPreview`

### GraphicalAttitudeThrustRotorPreview接口要求
```modelica
input roll_ref    // 必需，rad
input pitch_ref   // 必需，rad
input yaw_ref     // 必需，rad
input collective_thrust  // 必需，归一化推力 [0,1]
output rotor_command[4]  // 4个电机转速
```

所有4个输入端口必须连接，否则CheckModel失败。

### 为什么设置为零值？
- `TrainedNeuralResidual` 核心算法不生成姿态控制指令
- 零值姿态参考 → 飞行器保持水平姿态
- 推力控制主导 → 仅依靠垂直推力调节高度
- 对于 ClimbPath 任务（纯垂直上升）足够有效

## 后续工作

### 短期（已完成）
- ✅ 补全架构缺陷
- ✅ 通过CheckModel
- ✅ 通过Phase 5仿真
- ✅ 终点误差降至3.34m

### 中期（可选改进）
如果需要进一步提升性能：
1. 调整 `feature_normalization.k` (当前0.8)
2. 调整 `hidden_layer_inference.k` (当前0.45)
3. 调整 `bounded_neural_residual` 饱和限制 (当前±0.25)
4. 调整 `attitude_thrust_projection.k` (当前0.34)

### 长期（架构改进）
如果要完整实现神经网络学习:
1. 添加神经网络权重加载机制
2. 补全特征提取逻辑（当前仅 `measured_state.k=0.55` 常数）
3. 实现真实的隐藏层推理（当前仅线性增益）

## 关键教训

1. **架构分析优先**: 读取 `.mo` 文件确认端口类型和连接方式
2. **接口契约严格**: `GraphicalAttitudeThrustRotorPreview` 要求4个输入全部连接
3. **零值也是有效值**: 对于不需要的控制维度，提供零值而非忽略
4. **增量验证**: CheckModel → SimulateModel → Phase 5流水线 逐层验证

## 结论

trained_neural_residual 优化成功，从 **6.93m FAIL** → **3.34m PASS**。

**移出失败列表**: Phase 5 现在有 **27/38 通过 (71.1%)**，失败减少为 **11个**。

---

**文档创建**: 2026-08-19 06:18  
**验证方式**: 实际Sysplorer仿真（非推测）  
**修复类型**: 架构补全（非参数调整）
