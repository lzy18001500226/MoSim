# MoSimQuadrotorModel.Control 包架构规则（Codex 硬约束）

> 版本：2026-08-17  
> 状态：**已落地**，与当前代码库一致，Codex 必须严格遵守

---

## 一、Control 包顶层结构

```
MoSimQuadrotorModel.Control
├── Adapters/          # 传感器/执行器接口适配层（不含控制逻辑）
├── PID/               # OfficialPid baseline + 共用旋翼映射器
├── Px4Ctrl/           # Px4Ctrl baseline 完整家族
├── Allocation/        # 旋翼力矩分配（与具体控制器无关）
├── Implementations/   # G6 新控制器实现（6个子目录，见第三节）
└── Interfaces/        # 共用接口/抽象基类
```

`Control/package.order` 加载顺序已固定为上述顺序，**不得随意增删或改变顺序**。

---

## 二、各子包边界规则

### 2.1 `PID/` — OfficialPid baseline

**保留内容（8个类）**：
```
OfficialPidGraphicalCore
OfficialPidContinuousMapper
OfficialPidSysblockMapperDiagnostics
BaselineRotorMapper
YawDampedAmplitudeRouter
BodyFramePreprocessor
WorldFramePassthrough
CodexOfficialPidInPackageProbe019e9868
```

**硬规则**：
- `BaselineRotorMapper`（原 `Px4CtrlBaselineMapper`）是 OfficialPid 和 Px4Ctrl 共用的旋翼混控映射器，语义上归属 PID 包，Px4CtrlRunner 通过全限定名复用它
- **禁止**把任何 `Px4Ctrl*` 类放回此目录
- 新增 OfficialPid 变体放在此目录

### 2.2 `Px4Ctrl/` — Px4Ctrl baseline 完整家族

**包含内容（10个类）**：
```
Px4CtrlBaselineCore
Px4CtrlInputSampler
Px4CtrlOutputBridge
Px4CtrlBaselineMapperDiagnostics
Px4CtrlCoreSysblock
Px4CtrlOuterLoopGraphicalSysblock
Px4CtrlAttitudeThrustSysblockAdapter
Px4CtrlRotorAllocator
Px4CtrlAttitudeThrustSysblockRt1Smoke
Px4CtrlReferenceCompensator
```

**硬规则**：
- 所有 `within` 子句必须为 `within MoSimQuadrotorModel.Control.Px4Ctrl;`
- Px4Ctrl 系列的新增类（变体、诊断、适配器）统一放在此目录
- 不得引用 `Control.PID.Px4Ctrl*`（旧路径已作废）

### 2.3 `Implementations/` — G6 新控制器（6个家族）

每个家族独立子包，**尚未实现，目录结构已预留**：

| 子包名 | 控制器家族 | 典型算法 |
|--------|-----------|---------|
| `PidFamily/` | pid_family | Cascade PID、串级姿态 |
| `LinearRobustStateFeedback/` | linear_robust_state_feedback | LQR、H∞ |
| `NonlinearAdaptive/` | nonlinear_adaptive | DFBC、反步自适应 |
| `SlidingMode/` | sliding_mode | Super-Twisting SMC |
| `OptimizationPredictive/` | optimization_predictive | Linear MPC、NMPC |
| `GeometricFlatness/` | geometric_flatness | 几何控制、微分平坦 |

**硬规则**：
- 新控制器**必须**放在对应家族子包，禁止直接放在 `Control/` 或 `Control/PID/`
- 每个子包需有自己的 `package.mo`（含 `within MoSimQuadrotorModel.Control.Implementations;`）和 `package.order`
- Runner 文件放在 `Experiment/` 对应目录，**不放在** `Control/`

---

## 三、G6 Champion 候选控制器放置规则

| 控制器 | 归属子包 | 备注 |
|--------|---------|------|
| `cascade_pid` | `Implementations/PidFamily/` | 串级 PID |
| `dfbc_high_order_attitude` | `Implementations/NonlinearAdaptive/` | 反步 |
| `linear_mpc` | `Implementations/OptimizationPredictive/` | |
| `lqr_baseline` | `Implementations/LinearRobustStateFeedback/` | |
| `super_twisting_smc` | `Implementations/SlidingMode/` | |
| `trained_neural_residual` | `Implementations/NonlinearAdaptive/` 或单独 `Learning/` | 待定 |

---

## 四、全限定名规范

| 场景 | 正确写法 |
|------|---------|
| OfficialPid 核心 | `MoSimQuadrotorModel.Control.PID.OfficialPidGraphicalCore` |
| 共用旋翼映射器 | `MoSimQuadrotorModel.Control.PID.BaselineRotorMapper` |
| Px4Ctrl 核心 | `MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore` |
| Px4Ctrl 适配器 | `MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlAttitudeThrustSysblockAdapter` |
| 新 LQR 控制器 | `MoSimQuadrotorModel.Control.Implementations.LinearRobustStateFeedback.LqrBaseline` |

**禁止写法**：`Control.PID.Px4Ctrl*`（旧路径，已迁移，Sysplorer 会报找不到类）

---

## 五、标定链冻结（任何重构都不得修改）

```
kp_attitude = 14.142
kd_attitude = 1.414
kp_yaw      = 5
hover_1..4  k = 64.7923778389665
command_scale k = 4.632854053414571
```

---

## 六、Codex 操作禁令

1. **禁止**将 `Px4Ctrl*` 类放回 `Control/PID/`
2. **禁止**在 `Control/` 根目录直接放控制器实现类
3. **禁止**修改上述标定链数值
4. **禁止** git commit/stage/push（由人工完成）
5. 新增类后必须同步更新对应包的 `package.order`
6. 移动文件后必须同步更新 `within` 子句和所有引用方
