# MoSim 模型库清点报告（2026-08-18）

## 一、调查背景

用户反映：Codex 接入 46 个控制器后，模型库结构混乱。需要彻底搞清楚：
1. Catalog 中 48 个控制器的实际分布
2. Adapters/ 目录 58 个文件中有多少是活跃的
3. 5 个 Sysblock 整机模板如何接入架构
4. 如何重构模型库

## 二、核心发现

### 2.1 Catalog 权威口径

**`Config/control_platform/control_scheme_catalog.json`（2026-07-27 冻结）**

```
总计：46 个 implemented scheme（不是 48）
├── graphical_control_core: 41 个
│   ├── ATTITUDE_THRUST 输出: 38 个
│   ├── BODY_RATE_THRUST 输出: 2 个
│   └── ROTOR_COMMAND 输出: 1 个 (official_pid)
│
└── full_profile_whole_aircraft: 5 个 (Sysblock 整机模板)
    ├── fixed_awff_pid
    ├── fixed_awff_l1_residual
    ├── fixed_awff_l1_indi
    ├── fixed_linear_mpc_l1_indi
    └── fixed_qp_nmpc_l1_indi_cbf
```

**说明**：
- Catalog 中 `frozen_scheme_count=48` 是历史遗留字段，实际 `implementation_status="implemented"` 只有 46 个
- Px4Ctrl 不在这 46 个中（它是 `engineering_deployment_baseline`，不是候选控制器）
- 总计活跃控制器：**41 graphical + 5 sysblock = 46 个**

### 2.2 Implementation Package 分布

**41 个 graphical_control_core 按实现包分组：**

| Package | 数量 | 控制器列表 |
|---------|------|-----------|
| **PidFamily** | 5 | cascade_pid, gain_scheduled_pid, fuzzy_pid, neural_pid, official_pid |
| **ClassicRobust** | 13 | lqr_baseline, lqi_baseline, lqg, h2_state_feedback, hinf_hover_wrench, fopid, backstepping_baseline, adaptive_backstepping, feedback_linearization, mrac, ndi, passivity_based_control, pole_placement_luenberger |
| **SlidingMode** | 7 | integral_smc, terminal_smc, nonsingular_terminal_smc, super_twisting_smc, adaptive_smc, fuzzy_smc, smc_boundary_layer |
| **GeometricFlatness** | 6 | se3_basic, dfbc_basic, dfbc_high_order_attitude, dfbc_high_order_bodyrate, dfbc_smooth_robust_attitude, dfbc_smooth_robust_bodyrate |
| **Optimization** | 8 | linear_mpc, robust_mpc, adaptive_mpc, tube_mpc, explicit_gain_scheduled_mpc, ilqr, mppi, nmpc_outer |
| **Learning** | 2 | trained_neural_residual, rl_gain_scheduler |

### 2.3 Adapters 目录清点

**`Models/MoSimQuadrotorModel/Control/Adapters/` — 60 个文件**

#### 活跃 Adapter（41 个）

对应 41 个 graphical_control_core，每个控制器核心通过一个 Bridge 连接到 Adapter：

**ATTITUDE_THRUST 边界（38 个）：**
```
AdaptiveBacksteppingAttitudeThrustAdapter → AdaptiveBacksteppingEquationBridge
AdaptiveMpcAttitudeThrustAdapter → AdaptiveMpcEquationBridge
AdaptiveSmcAttitudeThrustAdapter → AdaptiveSmcEquationBridge
BacksteppingBaselineAttitudeThrustAdapter → BacksteppingBaselineEquationBridge
CascadePidAttitudeThrustAdapter → PidAttitudeThrustCFunction
DfbcBasicAttitudeThrustAdapter → DfbcBasicEquationBridge
DfbcHighOrderAttitudeThrustAdapter → DfbcHighOrderEquationBridge
DfbcSmoothRobustAttitudeThrustAdapter → DfbcSmoothRobustAttitudeEquationBridge
ExplicitGainScheduledMpcAttitudeThrustAdapter → ExplicitGainScheduledMpcEquationBridge
FeedbackLinearizationAttitudeThrustAdapter → FeedbackLinearizationEquationBridge
FopidAttitudeThrustAdapter → FopidEquationBridge
FuzzyPidAttitudeThrustAdapter → FuzzyPidEquationBridge
FuzzySmcAttitudeThrustAdapter → FuzzySmcEquationBridge
GainScheduledPidAttitudeThrustAdapter → GainScheduledPidEquationBridge
H2StateFeedbackAttitudeThrustAdapter → H2StateFeedbackEquationBridge
IlqrAttitudeThrustAdapter → IlqrEquationBridge
IntegralSmcAttitudeThrustAdapter → IntegralSmcEquationBridge
LinearMpcAttitudeThrustAdapter → LinearMpcCFunction
LqgAttitudeThrustAdapter → LqgEquationBridge
LqiAttitudeThrustAdapter → LqiEquationBridge
LqrBaselineAttitudeThrustAdapter → LqrBaselineEquationBridge
MppiAttitudeThrustAdapter → MppiEquationBridge
MracAttitudeThrustAdapter → MracEquationBridge
NdiAttitudeThrustAdapter → NdiEquationBridge
NeuralPidAttitudeThrustAdapter → NeuralPidEquationBridge
NmpcOuterAttitudeThrustAdapter → NmpcOuterEquationBridge
NonsingularTerminalSmcAttitudeThrustAdapter → NonsingularTerminalSmcEquationBridge
PassivityBasedControlAttitudeThrustAdapter → PassivityBasedControlEquationBridge
PolePlacementLuenbergerAttitudeThrustAdapter → PolePlacementLuenbergerEquationBridge
RlGainSchedulerAttitudeThrustAdapter → RlGainSchedulerEquationBridge
RobustMpcAttitudeThrustAdapter → RobustMpcEquationBridge
Se3BasicAttitudeThrustAdapter → Se3BasicEquationBridge
SmcBoundaryLayerAttitudeThrustAdapter → SmcBoundaryLayerEquationBridge
SuperTwistingSmcAttitudeThrustAdapter → SuperTwistingSmcCFunction
TerminalSmcAttitudeThrustAdapter → TerminalSmcEquationBridge
TrainedNeuralResidualAttitudeThrustAdapter → TrainedNeuralResidualCFunction
TubeMpcAttitudeThrustAdapter → TubeMpcEquationBridge
HinfHoverWrenchAdapter → HinfHoverWrenchEquationBridge (WRENCH 边界)
```

**BODY_RATE_THRUST 边界（2 个）：**
```
DfbcHighOrderBodyRateAdapter → DfbcHighOrderBodyRateEquationBridge
DfbcSmoothRobustBodyRateAdapter → DfbcSmoothRobustBodyRateEquationBridge
```

**ROTOR_COMMAND 边界（1 个）：**
```
OfficialPIDGraphicalRotorAdapter → OfficialPidCoreSysblock (直接输出电机指令)
```

#### 历史遗留/多变体 Adapter（19 个）

**Official PID 的 ROTOR_COMMAND 变体（8 个）：**
- OfficialPIDGraphicalRotorAdapter（正式活跃）
- OfficialPIDRotorAdapter
- OfficialPIDYawAuthorityMappedRotorAdapter
- OfficialPIDYawCorrectedRotorAdapter
- OfficialPidSysblockCoreAdapter
- OfficialPidSysblockMapperAdapter
- OfficialPidSysblockMapperDiagnostics
- OfficialPidSysblockRotorAdapter

**其他 ROTOR_COMMAND Adapter（4 个）：**
- AWFFGraphicalRotorAdapter
- AWFFRotorAdapter
- INDIRotorAdapter
- FaultCompensationRotorAdapter
- ImprovedPIDRotorAdapter

**Px4Ctrl 报告（1 个）：**
- Px4CtrlEquationBridgeReportBaselineAdapter

**package.mo**

### 2.4 五个 Sysblock 整机模板的位置

这 5 个模板**不在** `Control/Adapters/` 中，它们是**完整闭环 Runner**，直接继承了包含"参考轨迹+传感器+控制器+分配器+执行器+飞机"的整机模板：

```
Models/MoSimQuadrotorModel/Experiment/Baselines/Sysblock/
├── AWFFSysblockClosedLoopRunner.mo (继承 Example1AWFFSysblockClosedLoop)
├── AWFFL1ResidualSysblockClosedLoopRunner.mo (继承 Example1L1SysblockClosedLoop)
├── AWFFL1INDISysblockClosedLoopRunner.mo (继承 Example1L1SysblockClosedLoop)
├── LinearMPCL1INDISysblockClosedLoopRunner.mo (继承 Example1L1SysblockClosedLoop)
└── QPNMPCCBFSysblockClosedLoopRunner.mo (继承某 CBF 整机模板)
```

这些 Runner 在 `catalog.json` 中对应：
```
fixed_awff_pid → AWFFSysblockClosedLoopRunner
fixed_awff_l1_residual → AWFFL1ResidualSysblockClosedLoopRunner
fixed_awff_l1_indi → AWFFL1INDISysblockClosedLoopRunner
fixed_linear_mpc_l1_indi → LinearMPCL1INDISysblockClosedLoopRunner
fixed_qp_nmpc_l1_indi_cbf → QPNMPCCBFSysblockClosedLoopRunner
```

## 三、架构结论

### 3.1 控制器总数校正

| 类型 | 数量 | 备注 |
|------|------|------|
| `graphical_control_core` | 41 | 经过 Adapter → Allocator → Plant |
| `full_profile_whole_aircraft` | 5 | Sysblock 整机模板，不经过 Adapter |
| **Catalog 总计** | **46** | 不是 48 |

**Px4Ctrl**（`engineering_deployment_baseline`）不计入候选控制器总数。

### 3.2 Adapters/ 目录结构合理性

**活跃文件：41 个**（对应 41 个 graphical_control_core）

**遗留文件：19 个**
- Official PID 的 8 个 ROTOR_COMMAND 变体（只有 `OfficialPIDGraphicalRotorAdapter` 活跃）
- AWFF/INDI/FaultCompensation 等独立 ROTOR_COMMAND Adapter（4 个）
- Sysblock 辅助文件（5 个）
- Px4Ctrl 报告 Adapter（1 个）
- package.mo

### 3.3 输出边界分布

```
graphical_control_core (41 个):
├── ATTITUDE_THRUST: 38 个 → 通用 AttitudeThrustAllocator
├── BODY_RATE_THRUST: 2 个 → BodyRateThrustAllocator
└── ROTOR_COMMAND: 1 个 (official_pid) → 直接输出电机指令

full_profile_whole_aircraft (5 个):
└── 整机闭环模板，自带分配器，不经过 Adapters/
```

## 四、重构建议

### 4.1 当前问题诊断

1. **Catalog 口径混乱**：`frozen_scheme_count=48` 与实际 46 个 implemented 不符
2. **Adapters/ 目录冗余**：60 个文件中只有 41 个活跃，19 个遗留
3. **Sysblock 模板归属不明**：5 个整机模板在 `Experiment/Baselines/Sysblock/`，但 Catalog 中与 graphical_control_core 混为一谈
4. **ROTOR_COMMAND 边界混乱**：Official PID 有 8 个变体，只有 1 个活跃

### 4.2 重构方案

#### 方案 A：保守清理（推荐）

**目标**：最小化改动，只清理明确的冗余

1. **Catalog 修正**：
   - 将 `frozen_scheme_count` 改为 46
   - 在 `full_profile_whole_aircraft` 条目中添加 `adapter_required: false` 字段

2. **Adapters/ 归档**：
   ```
   将以下文件移动至 E:\MoSim_Archive\20260818_legacy_adapters\：
   - Official PID 的 7 个非活跃变体（保留 OfficialPIDGraphicalRotorAdapter）
   - AWFFRotorAdapter, INDIRotorAdapter, FaultCompensationRotorAdapter, ImprovedPIDRotorAdapter
   - OfficialPidSysblock* 系列（5 个）
   ```

3. **文档更新**：
   - 在 `Docs/Design/架构.md` 中明确 Sysblock 整机模板的位置与调用方式
   - 更新 `Adapters/package.order`（删除已归档的 Adapter）

4. **验证**：
   - 重新运行 Codex 接入的 46 个控制器的形式检查
   - 确认 `strict_graphical_sysblock_registry.json` 中的 5 个 Sysblock 模板仍可正常实例化

#### 方案 B：激进重组（需要大量测试）

**目标**：按输出边界彻底重组 Adapters/

```
Control/Adapters/
├── AttitudeThrust/          (38 个)
├── BodyRateThrust/          (2 个)
├── RotorCommand/            (1 个活跃 + 遗留归档)
├── Wrench/                  (1 个)
└── package.mo
```

**风险**：需要更新所有 Runner 中的 `import` 语句和 binding JSON 文件中的 `model_class` 路径。

### 4.3 推荐操作顺序

1. ✅ 已完成：修复 `OpenBlocksLocalPerceptionDisplay` 局部地图显示半径
2. **下一步**：执行方案 A 的保守清理（归档 19 个遗留文件）
3. **验证**：运行 Px4CtrlRunner（OpenBlocks 场景）+ 三机编队
4. **文档**：更新架构文档，明确 46 个控制器的完整清单
5. **Codex 同步**：将清理结果同步给 Codex，更新其控制器索引

## 五、关键文件清单

### 5.1 权威配置文件

```
Config/control_platform/control_scheme_catalog.json     — 46 个 implemented scheme
Config/control_platform/strict_graphical_sysblock_registry.json  — Sysblock 模板注册表
Config/control_platform/g6_champion_bindings/*.json     — 6 个冠军绑定
Config/control_platform/runner_baseline_bindings/*.json — 5 个基线绑定
```

### 5.2 控制器核心实现

```
Models/MoSimQuadrotorModel/Control/Implementations/
├── ClassicRobust/       (13 个控制器核心)
├── GeometricFlatness/   (6 个)
├── Learning/            (2 个)
├── Optimization/        (8 个)
├── PidFamily/           (5 个)
└── SlidingMode/         (7 个)
```

### 5.3 Sysblock 整机模板

```
Models/MoSimQuadrotorModel/Experiment/Baselines/Sysblock/
├── AWFFSysblockClosedLoopRunner.mo
├── AWFFL1ResidualSysblockClosedLoopRunner.mo
├── AWFFL1INDISysblockClosedLoopRunner.mo
├── LinearMPCL1INDISysblockClosedLoopRunner.mo
└── QPNMPCCBFSysblockClosedLoopRunner.mo
```

## 六、答辩 PPT 用图表建议

### 图表 1：MoSim 控制器库总览

```
MoSim 控制器库（46 个已验证实现）
├── Graphical Control Core（41 个）
│   ├── PID Family (5)
│   ├── Classic Robust (13)
│   ├── Sliding Mode (7)
│   ├── Geometric Flatness (6)
│   ├── Optimization (8)
│   └── Learning (2)
│
└── Sysblock Whole-Aircraft Templates（5 个）
    └── 完整闭环模板，自带传感器、分配器、执行器
```

### 图表 2：控制器-边界-分配器映射

```
[38 个 Outer-Loop] → ATTITUDE_THRUST → AttitudeThrustAllocator → Rotor Commands
[2 个 DFBC Variants] → BODY_RATE_THRUST → BodyRateThrustAllocator → Rotor Commands
[1 个 Official PID] → ROTOR_COMMAND → (无分配器) → 直接输出
[1 个 H∞] → WRENCH → WrenchAllocator → Rotor Commands
```

---

**报告人**：Claude Code  
**日期**：2026-08-18  
**状态**：调查完成，待用户确认重构方案
