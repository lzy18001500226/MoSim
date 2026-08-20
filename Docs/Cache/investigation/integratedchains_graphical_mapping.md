# IntegratedChains 图形化控制器映射关系

生成时间：2026-08-19  
任务：将 IntegratedChains Core 文件替换为真正的图形化实现

---

## 问题根源

之前的"转换"只是将 `extends` 改为实例化 equation-based Sysblock，但这些 Sysblock **内部仍然是纯 equation 实现**，没有图形化结构。

**用户反馈**：在 Sysplorer 中打开 Runner 后，`core` 模块显示为**空白白框**，无法看到内部结构。

**正确目标**：Core 文件应该使用 `AWFF_InnovationGraphicalControllers.mo` 中的**图形化 Sysblock**，这些 Sysblock 内部由 80+ 个图形模块和 connect() 语句组成。

---

## 已找到的图形化 Sysblock 实现

**文件位置**：`Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_InnovationGraphicalControllers.mo`

| 行号 | 模型名称 | 用途 |
|------|---------|------|
| 590 | `AWFF_L1ResidualControllerGraphical_Sysblock` | L1 残差 + PID 姿态 |
| 633 | `AWFF_INDIControllerGraphical_Sysblock` | L1 残差 + INDI 姿态 |
| 676 | `AWFF_L1FaultAllocationControllerGraphical_Sysblock` | L1 + 已知故障分配 |
| 719 | `AWFF_FaultCompensationControllerGraphical_Sysblock` | AWFF + 故障补偿 |
| 766 | `AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock` | L1 + 多故障隔离 |
| 826 | `AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock` | L1 + 在线故障分配 |
| 1096 | `AWFF_LinearMPCControllerGraphical_Sysblock` | 线性 MPC + INDI |
| 1139 | `AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock` | MPC + 在线故障分配 |

这些都是**真正的图形化实现**，内部包含：
- `L1ResidualOuterLoopBlock`（外环）
- `PIDAttitudeInnerLoopBlock` 或 `INDIAttitudeInnerLoopBlock`（内环）
- `MotorMixerBlock`（电机混合器）
- 完整的 `connect()` 语句连接各模块

---

## IntegratedChains 控制器映射

| IntegratedChains 控制器 | 对应的图形化 Sysblock | 状态 |
|-------------------------|----------------------|------|
| **AwffL1Residual** | `AWFF_L1ResidualControllerGraphical_Sysblock` | ✅ 找到 |
| **AwffL1Indi** | `AWFF_INDIControllerGraphical_Sysblock` | ✅ 找到 |
| **LinearMpcL1Indi** | `AWFF_LinearMPCControllerGraphical_Sysblock` | ✅ 找到 |
| **QpNmpcL1IndiCbf** | `AWFF_QPNMPCSafetyController_Sysblock` | ⚠️ 仅 equation 版本 |
| **AwffPid** (FixedAwffPid) | `AWFF_FullController_Sysblock` | ✅ 已在 Runner 中 |

---

## 详细对应分析

### 1. AwffL1Residual ✅

**当前错误实现**：`Control/IntegratedChains/AwffL1Residual/AwffL1ResidualCore.mo`
```modelica
MoSimQuadrotorModel.Control.Sysblocks.AWFF_L1ResidualControllerEquation_Sysblock controller
```
- 这是 equation-based Sysblock（154行纯 equation）
- 在 Sysplorer 中显示为空白白框

**正确的图形化实现**：`AWFF_L1ResidualControllerGraphical_Sysblock`（行590-631）
```modelica
L1ResidualOuterLoopBlock l1_outer annotation(Placement(...));
PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(...));
MotorMixerBlock motor_mixer annotation(Placement(...));
equation
  connect(x_error, l1_outer.x_error) annotation(Line(...));
  connect(l1_outer.roll_ref, attitude_loop.roll_ref) annotation(Line(...));
  // ... 完整的图形化连接
```

**修复方案**：将 Core 文件改为实例化 `AWFF_L1ResidualControllerGraphical_Sysblock`

---

### 2. AwffL1Indi ✅

**当前错误实现**：`Control/IntegratedChains/AwffL1Indi/AwffL1IndiCore.mo`
```modelica
MoSimQuadrotorModel.Control.Sysblocks.AWFF_INDIControllerEquation_Sysblock controller
```

**正确的图形化实现**：`AWFF_INDIControllerGraphical_Sysblock`（行633-674）
```modelica
L1ResidualOuterLoopBlock l1_outer annotation(Placement(...));
INDIAttitudeInnerLoopBlock attitude_loop annotation(Placement(...));  // 注意：INDI 内环
MotorMixerBlock motor_mixer annotation(Placement(...));
```

**修复方案**：将 Core 文件改为实例化 `AWFF_INDIControllerGraphical_Sysblock`

---

### 3. LinearMpcL1Indi ✅

**当前错误实现**：`Control/IntegratedChains/LinearMpcL1Indi/LinearMpcL1IndiCore.mo`
```modelica
MoSimQuadrotorModel.Control.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller
```

**正确的图形化实现**：`AWFF_LinearMPCControllerGraphical_Sysblock`（行1096+）

**修复方案**：将 Core 文件改为实例化 `AWFF_LinearMPCControllerGraphical_Sysblock`

---

### 4. QpNmpcL1IndiCbf ⚠️

**当前实现**：`Control/IntegratedChains/QpNmpcL1IndiCbf/QpNmpcL1IndiCbfCore.mo`
```modelica
MoSimQuadrotorModel.Control.Sysblocks.AWFF_QPNMPCSafetyController_Sysblock controller
```

**问题**：`AWFF_QPNMPCSafetyController_Sysblock` **本身就是 equation-based 实现**：
- 第50行：实例化了 `AWFF_LinearMPCOuterLoopControllerEquation_Sysblock nominal_mpc`
- 第77-100行：150+ 行纯 equation 逻辑（QP 投影、NMPC 缩放、CBF 约束、模态切换）

**结论**：这个控制器**没有纯图形化版本**。它的复杂安全逻辑（QP 二次规划、NMPC 非线性预测、CBF 控制屏障函数、多模态切换）必须用 equation 实现。

**处理方案**：保持当前 Core 文件不变，接受其为 equation-based 实现（这是技术上的必然，不是遗漏）

---

### 5. AwffPid ✅

**当前实现**：`Experiment/Templates/IntegratedChains/FixedAwffPid.mo`（172行完整 Runner）
```modelica
MoSimQuadrotorModel.Control.Sysblocks.AWFF_FullController_Sysblock controller
```

**状态**：已经是正确的实现，Runner 文件直接实例化了控制器 Sysblock（类似 Px4CtrlRunner 模式）

**无需修改**

---

## 修复计划

### 需要修复的文件（3个）

1. **AwffL1ResidualCore.mo**
   - 替换：`AWFF_L1ResidualControllerEquation_Sysblock` 
   - 改为：`AWFF_L1ResidualControllerGraphical_Sysblock`

2. **AwffL1IndiCore.mo**
   - 替换：`AWFF_INDIControllerEquation_Sysblock`
   - 改为：`AWFF_INDIControllerGraphical_Sysblock`

3. **LinearMpcL1IndiCore.mo**
   - 替换：`AWFF_LinearMPCOuterLoopControllerEquation_Sysblock`
   - 改为：`AWFF_LinearMPCControllerGraphical_Sysblock`

### 不需要修改的文件（2个）

4. **QpNmpcL1IndiCbfCore.mo** - 保持 equation-based 实现（技术限制）
5. **FixedAwffPid.mo** - 已经正确（完整 Runner 模式）

---

## 验证标准

修复后，在 Sysplorer 中打开 Runner 文件（例如 `AwffL1ResidualGraphicalRunner.mo`），双击 `core` 模块：

**应该看到**：
- ✅ 3个大型子模块（外环 + 内环 + 混合器）
- ✅ 清晰的连接线
- ✅ 可以继续双击子模块查看内部的 80+ 个图形块

**不应该看到**：
- ❌ 空白白框
- ❌ 单个黑盒模块没有内部结构

---

## 技术说明

### 为什么 QpNmpcL1IndiCbf 没有图形化版本？

QP-NMPC-CBF 控制器包含：
- **二次规划（QP）投影**：需要条件判断和迭代求解
- **非线性模型预测控制（NMPC）缩放**：动态缩放因子计算
- **控制屏障函数（CBF）约束**：实时安全约束检查
- **多模态切换**：正常/安全/应急/返航/降落 5种模式

这些逻辑**无法用基础 Sysblock 图形块（Gain、Sum、Saturation）直观表达**，必须用 equation 实现。

即使在 Simulink 中，类似的优化控制器也会用 MATLAB Function Block（本质是代码）实现，而非纯 Simulink 块。

### 图形化 vs Equation-based 的判断标准

**适合图形化**：
- 线性增益、求和、饱和、积分器
- 串级 PID、前馈补偿、滤波器
- 固定拓扑的控制器（PID、LQR、SMC）

**必须用 Equation**：
- 在线优化求解（MPC、iLQR）
- 条件逻辑和模态切换
- 非线性函数和矩阵运算
- 实时约束检查（CBF）

---

## 下一步

1. 修复 3个 Core 文件（AwffL1Residual、AwffL1Indi、LinearMpcL1Indi）
2. 在 Sysplorer 中验证：打开 Runner → 双击 core → 应看到完整图形结构
3. 更新完成报告，说明 QpNmpcL1IndiCbf 保持 equation-based 的技术原因