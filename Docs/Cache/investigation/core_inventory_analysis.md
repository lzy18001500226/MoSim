# Core Inventory Analysis

## Discovery

经过对归档的完整扫描，发现：

### 1. 真正的 Core 文件（9个）

这些文件 extends Controller 接口，可以直接作为 Core 使用：

```
Graphical/AWFF/AwffFullControllerCoreSysblock.mo          → fixed_awff_pid
Graphical/AWFF/AwffL1IndiControllerCoreSysblock.mo        → fixed_awff_l1_indi
Graphical/AWFF/AwffL1ResidualControllerCoreSysblock.mo    → fixed_awff_l1_residual
Graphical/LinearMPC/LinearMpcL1IndiControllerCoreSysblock.mo → fixed_linear_mpc_l1_indi
Graphical/PID/OfficialPidCoreSysblock.mo                  → official_pid
Graphical/PID/OfficialPidNativeSysblockCore.mo            → (官方PID变体)
Graphical/PID/OfficialPidSysblockCore.mo                  → (官方PID变体)
Graphical/ProjectOwned/AWFFCoreSysblock.mo                → (项目自有AWFF)
Graphical/QPNMPC/QpNmpcL1IndiCbfControllerCoreSysblock.mo → fixed_qp_nmpc_l1_indi_cbf
```

### 2. Sysblock 实现（3类，对应37个控制器）

#### 2.1 ClassicRobust 家族的 CFunction Sysblock（3个文件覆盖多个控制器）

**MoSim_WaveA_CFunction_Sysblock.mo**：
- 特征：有完整的端口定义（31输入+16输出），内部实例化 `CFunction` 模块
- 不 extends Controller，所以不是 Core
- 对应控制器：lqr_baseline, lqi_baseline, backstepping_baseline

**MoSim_Classic_CFunction_Sysblock.mo**：
- 覆盖：fopid, h2_state_feedback, pole_placement_luenberger, mrac, ndi

**MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock.mo**：
- 覆盖：hinf_hover_wrench

**MoSim_P2_*_GRAPHICAL_Sysblock**（推测存在但未找到）：
- 覆盖：lqg, adaptive_backstepping, feedback_linearization, passivity_based_control

#### 2.2 SlidingMode 家族（7个控制器）

推测有类似的 Sysblock 实现：
- integral_smc, terminal_smc, nonsingular_terminal_smc, super_twisting_smc
- adaptive_smc, fuzzy_smc, smc_boundary_layer

#### 2.3 Optimization 家族（8个控制器）

推测有类似的 Sysblock 实现：
- linear_mpc, robust_mpc, adaptive_mpc, tube_mpc
- explicit_gain_scheduled_mpc, ilqr, mppi, nmpc_outer

#### 2.4 GeometricFlatness 家族（6个控制器）

**MoSim_P10_DFBC_Family_CFunction_Sysblock.mo**：
- 覆盖：dfbc_high_order_attitude, dfbc_high_order_bodyrate
- 覆盖：dfbc_smooth_robust_attitude, dfbc_smooth_robust_bodyrate

推测还有：
- se3_basic, dfbc_basic

#### 2.5 PID 家族（4个控制器）

MIL 文件实例化了具体的 Sysblock：
- cascade_pid, gain_scheduled_pid, fuzzy_pid, neural_pid

#### 2.6 Learning 家族（2个控制器）

- trained_neural_residual, rl_gain_scheduler

### 3. 关键发现

**这些 Sysblock 都不是 Core**，因为：
- 它们不 extends Controller 接口
- 它们是"实现"，而 Core 应该是"封装+接口适配"

**真正的架构应该是**：
1. Sysblock 实现存放在 `Control/Sysblocks/`（已完成）
2. 每个控制器需要一个薄的 Core 封装，extends Controller 并实例化对应的 Sysblock

## 结论

**用户之前验证的46个控制器，实际上只有9个有完整的 Core**（Graphical/ 下的那些）。

其余37个控制器，都只有：
- Sysblock 实现（已经在 Control/Sysblocks/ 中）
- MIL 测试模型（展示如何实例化 Sysblock）

**但没有封装为 Core 的版本**。

## 下一步方案

有两个选择：

### 方案A：仅恢复9个已有 Core

- 优点：这些是已验证的完整实现
- 缺点：放弃了37个控制器

### 方案B：为37个控制器创建 Core

需要为每个 Sysblock 创建一个薄封装：

```modelica
within MoSimQuadrotorModel.Control.LqrBaseline;
model LqrBaseline_Core
  extends MoSimQuadrotorModel.Vehicle.Blocks.Controller.Controller;
  extends ModelWorkspace;
  
  MoSimQuadrotorModel.Control.Sysblocks.MoSim_WaveA_CFunction_Sysblock controller
    annotation(Placement(...));
  
  // 端口连接逻辑
  ...
  
  annotation(__MWORKS(version="26.3.0", modelType=Control, BlockSystem(...)));
  
  model ModelWorkspace
    annotation(__MWORKS(hide=true, BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
end LqrBaseline_Core;
```

### 推荐

**先执行方案A**，恢复9个已验证的 Core，让这9个控制器先跑起来。

37个控制器的 Core 创建是大工程，需要：
1. 理解每个 Sysblock 的端口定义
2. 编写端口映射逻辑
3. 逐个测试验证

这应该是后续任务。
