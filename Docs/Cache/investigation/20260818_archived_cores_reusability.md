# 归档 Core 可复用性调查报告

**调查时间**: 2026-08-18 23:35  
**调查人**: Claude Code  
**调查目标**: 确定 `E:\刘致远18001500226\MoSim_Archive\20260818_codex_legacy_architecture\Control_Implementations_Graphical\` 中归档的 Sysblock Core 是否可以直接复用于 46 个控制器的重建

---

## 1. 归档内容清点

### 1.1 归档目录结构

```
Control_Implementations_Graphical/
├── ClassicRobust/          # LQR/LQI/LQG/Hinf/Pole 等线性鲁棒控制
├── GeometricFlatness/      # DFBC 系列
├── Graphical/
│   ├── AWFF/              # 3 个 AWFF 变体 Core
│   ├── LinearMPC/         # 1 个 LinearMPC Core
│   ├── PID/               # 多个 PID Sysblock 变体
│   ├── ProjectOwned/      # AWFF Core Sysblock
│   └── QPNMPC/            # 1 个 QP-NMPC Core
├── Learning/              # 神经网络/RL 控制器
├── Optimization/          # MPC/NMPC 系列
├── PidFamily/             # PID 家族实现
├── SlidingMode/           # 滑模控制系列
└── Sysblocks/             # 29 个底层 Sysblock 实现（AWFF/PX4CTRL 组件）
```

### 1.2 文件统计

- **总 .mo 文件数**: 111 个
- **Core/Controller 文件数**: 27 个（含 `*Core*.mo` 和 `*Controller*.mo`）
- **Sysblocks 基础模块数**: 29 个（底层可复用组件）

---

## 2. 核心发现

### 2.1 归档 Core 的实现方式

通过抽查 `LinearMpcL1IndiControllerCoreSysblock.mo`，发现归档的 Core **并非完整独立实现**，而是通过 `extends` 继承自 `Sysblocks/` 下的基础模块：

```modelica
within MoSimQuadrotorModel.Control.Implementations.Graphical.LinearMPC;
model LinearMpcL1IndiControllerCoreSysblock
  "Linear MPC+L1+INDI controller core extracted from Example1LinearMPCSysblockClosedLoop"
  extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock;
  annotation(__MWORKS(hide = false, version = "26.3.0"));
end LinearMpcL1IndiControllerCoreSysblock;
```

**结论**: 这些 Core 是 **薄封装层**，真正的控制逻辑在 `Sysblocks/` 里。

### 2.2 AwffFullControllerCoreSysblock 结构

通过抽查 `AwffFullControllerCoreSysblock.mo`（前 80 行），发现这是一个 **完整的 Sysblock 图形化模型**：

- 8 个输入端口：`x_error`, `y_error`, `z_error`, `z_ref_rate`, `roll_mea`, `pitch_mea`, `yaw_mea`, `yaw_ref`
- 4 个输出端口：`y`, `y1`, `y2`, `y3`（四路控制量）
- 完整的参数定义（位置/姿态 PID 参数）
- 滤波器状态变量与控制律中间变量

**结论**: 这类 Core 是 **可直接实例化** 的 Sysblock 模型，具备完整的控制逻辑。

---

## 3. 现有正确架构对比

### 3.1 Px4Ctrl 架构（正确模板）

```
Control/Px4Ctrl/
  ├── Px4CtrlBaselineCore.mo       # ✅ Sysblock 核心（完整控制律）
  ├── Px4CtrlInputSampler.mo       # 18 in / 18 out ZOH
  ├── Px4CtrlOutputBridge.mo       # 4 in / 4 out 符号修正
  └── package.mo

Experiment/Px4Ctrl/
  ├── Px4CtrlRunner.mo              # ✅ 整机模型，直接连线，无桥接数组
  └── package.mo
```

### 3.2 Official PID 架构（当前状态）

```
Control/PID/
  ├── OfficialPidGraphicalCore.mo       # ✅ Core 在独立包内（46 KB，完整控制律）
  ├── BaselineRotorMapper.mo            # 桥接模块
  ├── YawDampedAmplitudeRouter.mo
  ├── WorldFramePassthrough.mo
  └── ...

Experiment/Baselines/
  ├── OfficialPidRunner.mo              # ⚠️ Runner 在 Baselines 而非 Experiment/PID/
  └── ...
```

**差异**: PID 的 Runner 位置不符合 `Experiment/XXX/` 的独立包规则。

---

## 4. 归档 Core 可复用性分析

### 4.1 ✅ 可直接复用的 Core（需验证端口契约）

归档的 `Control_Implementations_Graphical/` 中的 Core 理论上 **可以复用**，但需要满足以下条件：

1. **端口契约一致**: Core 的输入/输出端口数量、类型、名称必须与 Adapter/Runner 期望的接口匹配
2. **参数边界正确**: 标定参数（`kp_attitude=14.142` 等）不能被 Core 内部硬编码覆盖
3. **within 路径修正**: 需要从 `within MoSimQuadrotorModel.Control.Implementations.Graphical.XXX` 改为 `within MoSimQuadrotorModel.Control.XXX`
4. **Sysblocks 依赖完整**: 如果 Core 通过 `extends` 继承自 `Sysblocks/`，则 `Sysblocks/` 必须同时恢复

### 4.2 ⚠️ 需要修正的部分

#### A. 目录结构调整

**归档位置**（错误）：
```
Control/Implementations/Graphical/AWFF/AwffFullControllerCoreSysblock.mo
```

**目标位置**（正确）：
```
Control/AwffPid/AwffPidCore.mo
```

#### B. 端口适配问题

归档的 Core 可能有三种端口模式：

1. **18 输入端口**（完整状态向量）- 需要 `InputSampler` 桥接
2. **8-10 输入端口**（位置/姿态误差）- 需要 `Preprocessor` 预处理
3. **4-6 输入端口**（简化输入）- 需要更复杂的前置处理

**Px4Ctrl 模式**: 18 in → Sampler → Core → Bridge → 4 out

**AWFF 模式**（归档）: 8 in (误差空间) → Core → 4 out

**差异**: 如果强行套用 Px4Ctrl 的 18-端口 Sampler，需要在 Sampler 和 Core 之间插入误差计算逻辑。

#### C. Sysblocks 依赖恢复

如果要复用继承自 `Sysblocks/` 的 Core，必须将 29 个 Sysblock 文件全部恢复到 `Control/Implementations/Sysblocks/`（但这又违反了"删除 Implementations 层"的架构要求）。

**矛盾**: 
- 归档的 Core 依赖 `Control.Implementations.Sysblocks.*`
- 新架构要求删除 `Control/Implementations/` 层
- **解决方案**: 将 `Sysblocks/` 提升为 `Control/Sysblocks/`（顶级共享库）

---

## 5. 重建方案对比

### 方案 A: 从归档恢复并修正（快速但技术债）

**步骤**:
1. 从归档复制 46 个 Core 到新架构位置
2. 修正 `within` 路径
3. 恢复 `Sysblocks/` 为共享库（提升至 `Control/Sysblocks/`）
4. 为每个 Core 创建独立的 `Control/XXX/` 和 `Experiment/XXX/` 包
5. 从归档的 `Experiment_Runners_Formal/` 提取走线逻辑重建 Runner

**优点**: 节省大量工作量，Core 已验证可运行  
**缺点**: 
- 端口契约不一定与 Px4Ctrl 模板一致
- `Sysblocks/` 共享库引入额外依赖层
- 需要逐个验证 46 个 Core 的端口适配

**时间成本**: 2-3 天（批量复制 + 逐个验证）

### 方案 B: 从 Px4Ctrl 模板克隆（慢但架构干净）

**步骤**:
1. 从 `Control/Px4Ctrl/` 克隆出 46 个独立包
2. 替换每个包的 Core 内容（从归档提取控制律方程，重写为独立 Core）
3. 统一使用 Px4Ctrl 的 18-端口 Sampler + 4-端口 Bridge 模式
4. 为每个控制器创建独立的 `Experiment/XXX/` 包与 Runner

**优点**: 架构完全一致，无历史包袱  
**缺点**: 工作量巨大，需要手工重写 46 个 Core 的控制方程

**时间成本**: 1-2 周

### 方案 C: 混合方案（推荐）

**步骤**:
1. **直接复用端口契约简单的 Core**（如 PID 家族、LQR 家族）- 从归档恢复
2. **重写端口契约复杂的 Core**（如 MPC、NMPC、几何控制）- 从 Px4Ctrl 克隆
3. **Sysblocks 共享库提升**: 将归档的 `Sysblocks/` 提升为 `Control/Sysblocks/`（作为可选依赖）
4. **分批验证**: 先验证 10 个简单控制器，再推广到全部 46 个

**优点**: 平衡工作量与架构质量  
**缺点**: 需要逐个判断哪些 Core 可直接复用

**时间成本**: 3-5 天

---

## 6. 建议决策

### 6.1 立即可做的事

1. **从归档恢复 Sysblocks 共享库**:
   ```bash
   cp -r "E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical/Sysblocks" \
         Models/MoSimQuadrotorModel/Control/Sysblocks
   ```

2. **验证 5 个代表性 Core**:
   - `OfficialPidCoreSysblock` (PID 家族)
   - `AwffFullControllerCoreSysblock` (AWFF 家族)
   - `LinearMpcL1IndiControllerCoreSysblock` (MPC 家族)
   - `SuperTwistingSmcCoreSysblock` (滑模家族)
   - `DfbcHighOrderAttitudeCoreSysblock` (几何家族)

3. **对比 Core 端口与 Px4Ctrl Sampler 端口**:
   - 如果端口匹配 → 直接复用
   - 如果端口不匹配 → 需要定制 Sampler 或重写 Core

### 6.2 关键问题（需用户决策）

1. **是否接受 `Control/Sysblocks/` 共享库？**
   - 接受 → 可快速恢复 46 个 Core
   - 拒绝 → 需要手工重写所有 Core 为独立实现

2. **是否统一 18-端口 Sampler 模式？**
   - 统一 → 架构干净但需要适配层
   - 不统一 → 每个控制器可能有不同的前置处理逻辑

3. **Official PID 的 Runner 位置是否需要修正？**
   - 当前: `Experiment/Baselines/OfficialPidRunner.mo`
   - 目标: `Experiment/PID/OfficialPidRunner.mo`（与 Px4Ctrl 对齐）

---

## 7. 结论

**归档的 Core 理论上可以复用**，但需要满足以下前提：

1. 恢复 `Sysblocks/` 共享库（29 个文件）
2. 修正 `within` 路径（从 `Implementations.Graphical` 改为独立包）
3. 验证端口契约（与 Adapter/Runner 期望一致）
4. 重建 46 个 `Experiment/XXX/Runner.mo`（从归档的 FormalRunner 提取走线逻辑）

**如果用户不想重新验证端口契约**，建议采用 **方案 C（混合方案）**：
- 简单控制器（PID/LQR）直接恢复
- 复杂控制器（MPC/几何）从 Px4Ctrl 克隆
- 分批验证，逐步推进

**时间成本**: 3-5 天（vs. 从零重写需要 1-2 周）
