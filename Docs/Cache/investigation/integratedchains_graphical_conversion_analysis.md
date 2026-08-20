# IntegratedChains 纯图形化转换分析

生成时间：2026-08-19 23:38  
状态：调查完成，待执行转换

---

## 问题确认

### 当前架构问题

**用户要求**："肯定要改成纯图形的仿真啊"

**当前状态**：4个 IntegratedChains 控制器使用 **equation-based Sysblock**，不符合纯图形化要求

| 控制器 | Core文件 | 架构类型 | 问题 |
|--------|---------|---------|------|
| `awff_l1_indi` | AwffL1IndiCore.mo | equation-based | ✅ 存在，使用 `extends AWFF_INDIControllerEquation_Sysblock` |
| `awff_l1_residual` | AwffL1ResidualCore.mo | equation-based | ✅ 存在，使用 equation Sysblock |
| `linear_mpc_l1_indi` | LinearMpcL1IndiCore.mo | equation-based | ✅ 存在，使用 equation Sysblock |
| `qp_nmpc_l1_indi_cbf` | QpNmpcL1IndiCbfCore.mo | equation-based | ✅ 存在，使用 equation Sysblock |
| `awff_pid` | FixedAwffPidCore.mo | ❌ **缺失** | ❌ Control/IntegratedChains/FixedAwffPid/ 只有空 package.mo |

---

## E盘归档调查结果

### 搜索结果

**搜索位置**：`E:/刘致远18001500226/MoSim_Archive/`

**发现的 awff_pid 相关文件**：
1. `20260811_consolidation/Models/.../Experiment/Templates/IntegratedChains/FixedAwffPid.mo`
   - **类型**: Runner 文件（不是 Core）
   - **内容**: `extends MoSimQuadrotorModel.Experiment.Templates.Official.Example1AWFFSysblockClosedLoop`
   - **结论**: 这是旧版闭环测试模板，不是控制器核心

2. `20260818_codex_legacy_architecture/Control_Adapters/AwffPidRotorCommandAdapter.mo`
   - **类型**: Adapter 文件
   - **结论**: 适配器，不是控制器核心

3. `legacy_experiment_runners/AwffControllers_redundant/AwffPidGraphicalRunner.mo`
   - **类型**: Runner 文件
   - **结论**: 刚归档的冗余文件

**关键发现**：❌ **E盘归档中不存在 FixedAwffPidCore.mo 纯图形化实现**

---

## Equation-based Sysblock 分析

### 示例：AWFF_INDIControllerEquation_Sysblock

**文件**: `Control/Sysblocks/AWFF_INDIControllerEquation_Sysblock.mo`

**架构特点**：
- 210行 Modelica equation 代码
- 44个参数（kp_x, kd_x, kp_z, ki_z, l1_model_decay, indi_roll_gain 等）
- 8个输入端口（x_error, y_error, z_error, z_ref_rate, roll_mea, pitch_mea, yaw_mea, yaw_ref）
- 4个输出端口（y, y1, y2, y3）
- 使用 `extends ModelWorkspace` + 完整的微分方程系统

**控制逻辑**：
1. **AWFF外环**：位置误差 → L1残差补偿 → 姿态参考指令
2. **INDI内环**：姿态误差 → 角加速度估计 → 增量控制 → 力矩指令
3. **状态滤波器链**：position_derivative_filter → attitude_rate_filter → angular_accel_filter

**问题**：这是复杂的微分方程组，**无法直接用拖拽式图形块实现**

---

## 纯图形化 vs Equation-based 对比

### Phase 3 恢复的 38个纯图形控制器

**示例架构**（如 CascadePidCore.mo）：
```modelica
within MoSimQuadrotorModel.Control.PidFamily.CascadePid;
model CascadePidCore "cascade_pid graphical control core"
  // 纯 Sysblock 图形建模
  PID_Module outer_x;
  PID_Module outer_y;
  PID_Module altitude_pid;
  PID_Module roll_pid;
  PID_Module pitch_pid;
  PID_Module yaw_pid;
  // ... 图形连接
  annotation(__MWORKS(SECInstance = true, hide = false, version = "26.3.0"));
end CascadePidCore;
```

**特点**：
- 使用现成的 Sysblock 图形模块（PID_Module, Gain, Sum 等）
- 图形化连接（connect语句或GUI拖拽）
- 可以直接在 Sysplorer 中双击打开查看图形

### IntegratedChains 的 Equation-based 架构

**当前架构**（如 AwffL1IndiCore.mo）：
```modelica
within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi;
model AwffL1IndiCore "awff_l1_indi graphical control core"
  extends MoSimQuadrotorModel.Control.Sysblocks.AWFF_INDIControllerEquation_Sysblock;
  annotation(__MWORKS(SECInstance = true, hide = false, version = "26.3.0"));
end AwffL1IndiCore;
```

**特点**：
- 仅继承 equation Sysblock
- 双击打开只看到空壳和 extends 语句
- 实际控制逻辑在 Sysblocks/ 的 equation 定义中

---

## 转换策略分析

### 方案 1：完全分解为基础图形块（技术上不可行）

**理论方法**：
- 将 210行 equation 拆解为独立的 Gain、Sum、Integrator、Derivative、Limiter、Filter 模块
- 用图形连接重建所有微分方程

**问题**：
1. ❌ **复杂度爆炸**：44个参数 × 50+个中间状态变量 × 数十个微分方程
2. ❌ **可维护性极差**：图形模型会变成数百个模块的"意大利面条"
3. ❌ **与 Phase 3 恢复方法论冲突**：Phase 3 只恢复了**单环PID/SMC/MPC**等标准控制器，而 IntegratedChains 是**多级联级控制链**

### 方案 2：保留 Equation Sysblock 作为"黑盒"图形模块（推荐）

**实现方法**：
- 保留 `Control/Sysblocks/AWFF_INDIControllerEquation_Sysblock.mo` 等定义
- 将其**视为单个原子Sysblock模块**（类似 Simulink 中的 S-Function）
- 在 Core 文件中实例化为图形块，并可拖拽使用

**修改示例**（AwffL1IndiCore.mo）：
```modelica
within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi;
model AwffL1IndiCore "awff_l1_indi graphical control core"
  // 从 extends 改为实例化
  MoSimQuadrotorModel.Control.Sysblocks.AWFF_INDIControllerEquation_Sysblock controller;
  
  // 端口暴露
  input Real x_error;
  input Real y_error;
  // ... 8个输入
  output Real y;
  output Real y1;
  // ... 4个输出
  
equation
  // 端口连接
  controller.x_error = x_error;
  controller.y_error = y_error;
  // ... 连接语句
  y = controller.y;
  y1 = controller.y1;
  
  annotation(__MWORKS(SECInstance = true, hide = false, version = "26.3.0"));
end AwffL1IndiCore;
```

**优点**：
- ✅ 保留完整控制逻辑
- ✅ 可在 Sysplorer 中双击查看"一个大块"
- ✅ 符合黑盒封装理念
- ✅ 工作量小

**缺点**：
- ⚠️ 仍然不是"纯拖拽式图形"（内部是 equation）
- ⚠️ 需要确认这是否符合用户预期

### 方案 3：awff_pid 特殊处理（需要澄清）

**当前状态**：
- Phase 3 报告显示 `fixed_awff_pid` 为 `"pure_graphical"`, `19.5 KB`
- 但实际 Core 文件缺失，只有空 package.mo
- E盘归档中没有找到原始实现

**可能原因**：
1. Phase 3 脚本误报（实际未恢复）
2. 文件在某个未检查的归档位置
3. awff_pid 本应使用不同的架构（可能是 AwffControllers/PidAwffLinearEsoGraphicalRunner.mo？）

**需要行动**：
- 检查 `AwffControllers/PidAwffLinearEsoGraphicalRunner.mo` 是否实际就是 awff_pid
- 或者需要从零重建 awff_pid 纯图形实现

---

## 推荐执行路径

### 第一步：澄清用户预期

**关键问题**："纯图形的仿真"的定义是什么？

**选项 A**：Equation Sysblock 作为原子模块仍然算"纯图形"
- 优点：工作量小，逻辑完整
- 缺点：内部仍是 equation

**选项 B**：必须完全分解为基础图形块
- 优点：真正纯拖拽
- 缺点：技术上极其困难，可维护性极差

### 第二步：根据澄清执行

**如果选项 A（推荐）**：
1. 修改 4个 IntegratedChains Core 文件：将 `extends` 改为实例化 + 端口连接
2. 解决 awff_pid 缺失问题（重建或映射到现有实现）
3. 验证所有控制器可以在 Sysplorer 中双击打开

**如果选项 B（不推荐）**：
1. 分析 AWFF_INDIControllerEquation_Sysblock 的 210行 equation
2. 设计对应的图形模块拓扑
3. 手动重建每个微分方程为 Integrator + Gain + Sum 连接
4. 测试验证（极其耗时）

---

## 待办清单

- [ ] **向用户澄清**："纯图形"是否允许 equation Sysblock 作为黑盒模块
- [ ] 调查 awff_pid 与 pid_awff_linear_eso 的关系
- [ ] 根据用户反馈选择方案 A 或方案 B
- [ ] 执行对应的转换工作
- [ ] 更新 harness_map 和 Runner 文件
- [ ] CheckModel 验证
