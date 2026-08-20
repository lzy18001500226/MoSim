# MoSim 目录清理与归档计划

生成时间：2026-08-19  
状态：待执行

---

## 问题总结

1. **IntegratedChains 缺失 1 个 Core**：`Control/IntegratedChains/FixedAwffPid/` 只有空 package.mo
2. **Runner 文件冗余**：实际 74 个，预期 48 个（多出 26 个）
3. **旧目录未归档**：`Templates/`, 重复的家族目录

---

## 归档清单

### 一、Experiment 目录冗余（需要归档）

#### 1. 重复的家族目录（26个冗余 Runner）

**LinearRobustStateFeedback/** (6个) - 已在 ClassicRobust/
- H2StateFeedbackGraphicalRunner.mo
- HinfHoverWrenchGraphicalRunner.mo
- LqgGraphicalRunner.mo
- LqiBaselineGraphicalRunner.mo
- LqrBaselineGraphicalRunner.mo
- PolePlacementLuenbergerGraphicalRunner.mo

**NonlinearAdaptive/** (6个) - 已在 ClassicRobust/
- AdaptiveBacksteppingGraphicalRunner.mo
- BacksteppingBaselineGraphicalRunner.mo
- FeedbackLinearizationGraphicalRunner.mo
- MracGraphicalRunner.mo
- NdiGraphicalRunner.mo
- PassivityBasedControlGraphicalRunner.mo

**OptimizationPredictive/** (8个) - 已在 Optimization/
- AdaptiveMpcGraphicalRunner.mo
- ExplicitGainScheduledMpcGraphicalRunner.mo
- IlqrGraphicalRunner.mo
- LinearMpcGraphicalRunner.mo
- MppiGraphicalRunner.mo
- NmpcOuterGraphicalRunner.mo
- RobustMpcGraphicalRunner.mo
- TubeMpcGraphicalRunner.mo

**建议**：移动到归档目录 `E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/`

#### 2. Formation 目录（3个文件，不在48控制器范围）

**Formation/Px4Ctrl/** (3个三机编队 Runner)
- ThreeUavHeterogeneousOpenBlocksRunner.mo
- ThreeUavPx4CtrlFormationRunner.mo
- ThreeUavPx4CtrlOpenBlocksRunner.mo

**建议**：保留！三机编队是独立功能，不属于48单机控制器。

#### 3. 冗余的 PID 相关文件

**PidFamily/** 冗余文件：
- ❌ OfficialPidGraphicalRunner.mo (重复，正确的在 Baselines/)
- ❌ OfficialPidFamilyRunner.mo (重复)
- ❌ FopidGraphicalRunner.mo (应该在 ClassicRobust，已重复)

**AwffControllers/** 冗余文件：
- ❌ AwffPidGraphicalRunner.mo (多余，应该在 Templates/IntegratedChains/)

**建议**：归档冗余文件

#### 4. Templates 目录（旧测试模板）

**Templates/Official/** (21个文件)
- 旧的测试闭环模板
- 已被新的统一架构 Runner 替代

**Templates/IntegratedChains/** (2个文件)
- FixedAwffPid.mo (仍在 harness_map 中引用！需保留)
- package.mo

**建议**：
- `Templates/Official/` 归档
- `Templates/IntegratedChains/` 暂时保留（harness_map 仍引用 FixedAwffPid.mo）

---

### 二、Control 目录问题

#### 1. IntegratedChains 缺失的 Core

**Control/IntegratedChains/FixedAwffPid/**
- 状态：只有空 package.mo，缺少 FixedAwffPidCore.mo
- 原因：Phase 3 报告显示 fixed_awff_pid 是 "pure_graphical" (19.5 KB)
- 问题：可能文件丢失或未正确恢复

**需要行动**：检查 E 盘归档是否有原始文件，或者确认该控制器是否需要 Core

#### 2. Sysblocks 目录（保留）

**Control/Sysblocks/** (29个 equation-based Sysblock 定义)
- 状态：IntegratedChains 的 4 个 equation-based 核心依赖这些定义
- 内容：AWFF_INDIControllerEquation_Sysblock, AWFF_L1ResidualControllerEquation_Sysblock 等

**建议**：**必须保留**！不要归档。

---

## 正确的目录结构

### Control/ (48个核心)
```
Control/
├── PidFamily/              (5个) ✓
├── ClassicRobust/          (13个) ✓
├── SlidingMode/            (7个) ✓
├── Optimization/           (8个) ✓
├── GeometricFlatness/      (6个) ✓
├── Learning/               (2个) ✓
├── IntegratedChains/       (5个: 1图形 + 4equation) ⚠️ 缺1个
├── Px4Ctrl/                (1个) ✓
├── PID/                    (1个 Official) ✓
└── Sysblocks/              (equation定义，保留) ✓
```

### Experiment/ (48个 Runner)
```
Experiment/
├── PidFamily/              (5个) ✓
├── ClassicRobust/          (13个) ✓
├── SlidingMode/            (7个) ✓
├── Optimization/           (8个) ✓
├── GeometricFlatness/      (6个) ✓
├── Learning/               (2个) ✓
├── IntegratedChains/       (4个 equation-based) ✓
├── AwffControllers/        (1个: pid_awff_linear_eso) ✓
├── Px4Ctrl/                (1个) ✓
├── Baselines/              (1个: official_pid) ✓
├── Formation/              (3个三机编队，独立功能) ✓ 保留
└── Templates/              (待清理)
    ├── Official/           ❌ 归档
    └── IntegratedChains/   ⚠️ 暂时保留（FixedAwffPid.mo被引用）
```

### 需要删除的冗余目录
```
Experiment/
├── LinearRobustStateFeedback/    ❌ 归档（与ClassicRobust重复）
├── NonlinearAdaptive/            ❌ 归档（与ClassicRobust重复）
└── OptimizationPredictive/       ❌ 归档（与Optimization重复）
```

---

## 执行计划

### 阶段 1：归档冗余 Runner 目录
```bash
# 移动到归档目录
mkdir -p "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
mv Models/MoSimQuadrotorModel/Experiment/LinearRobustStateFeedback \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
mv Models/MoSimQuadrotorModel/Experiment/NonlinearAdaptive \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
mv Models/MoSimQuadrotorModel/Experiment/OptimizationPredictive \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
```

### 阶段 2：清理冗余的单个文件
```bash
# PidFamily 冗余文件
mv Models/MoSimQuadrotorModel/Experiment/PidFamily/OfficialPidGraphicalRunner.mo \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
mv Models/MoSimQuadrotorModel/Experiment/PidFamily/OfficialPidFamilyRunner.mo \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
mv Models/MoSimQuadrotorModel/Experiment/PidFamily/FopidGraphicalRunner.mo \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"

# AwffControllers 冗余文件
mv Models/MoSimQuadrotorModel/Experiment/AwffControllers/AwffPidGraphicalRunner.mo \
   "E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/"
```

### 阶段 3：归档旧 Templates
```bash
# Templates/Official
mv Models/MoSimQuadrotorModel/Experiment/Templates/Official \
   "E:/刘致远18001500226/MoSim_Archive/legacy_templates/"
```

### 阶段 4：解决 FixedAwffPid Core 缺失问题
1. 检查 E 盘归档是否有原始的 `FixedAwffPidCore.mo`
2. 如果找到，恢复到 `Control/IntegratedChains/FixedAwffPid/`
3. 如果没有，确认该控制器是否真的需要独立 Core（可能直接用 Sysblock）

---

## 验证清单

完成清理后验证：
- [ ] Control/ 核心数量：47个纯文件 + Sysblocks 目录
- [ ] Experiment/ Runner 数量：48个（不含 Formation）
- [ ] harness_map 路径全部正确
- [ ] 冗余目录已归档到 E 盘
- [ ] Formation 目录保留（三机编队独立功能）
- [ ] Sysblocks 目录保留（equation-based 依赖）

---

## 注意事项

1. **不要删除 Formation/**：三机编队是独立功能，不在48单机控制器范围
2. **不要删除 Sysblocks/**：IntegratedChains equation-based 核心依赖这些定义
3. **暂时保留 Templates/IntegratedChains/**：harness_map 仍引用 FixedAwffPid.mo
4. **归档而非删除**：所有文件移动到 E 盘归档目录，不直接删除
