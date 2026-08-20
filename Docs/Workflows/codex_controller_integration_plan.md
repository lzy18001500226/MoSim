# Codex 控制器接入方案

> **目标**：将 46 个已验证控制器正确接入到 MoSim 运行环境
> **执行者**：Codex（按本方案严格执行）
> **日期**：2026-08-18

---

## 一、架构边界（禁止违反）

### 1.1 控制器分类（总计 46 个）

| 类型 | 数量 | 执行路径 | 是否经过 Adapter |
|------|------|----------|------------------|
| `graphical_control_core` | 41 | Control 核心 → Adapter → Actuator Mapper | **是** |
| `full_profile_whole_aircraft` | 5 | Templates/IntegratedChains 整机模板 | **否** |

### 1.2 输出边界分布（41 个 graphical_control_core）

| 输出边界 | 控制器数量 | Adapter Base | 示例 |
|----------|-----------|--------------|------|
| ATTITUDE_THRUST | 38 | FormalAttitudeThrustRunnerBase | CascadePid, LQR, LinearMPC, ... |
| BODY_RATE_THRUST | 2 | FormalBodyRateThrustRunnerBase | dfbc_high_order_bodyrate, dfbc_smooth_robust_bodyrate |
| ROTOR_COMMAND | 1 | FormalRotorCommandRunnerBase | official_pid |
| WRENCH | 0 | FormalWrenchRunnerBase | *(hinf_hover_wrench 已归档)* |

### 1.3 五个整机模板的特殊性

这 5 个 scheme **不是**普通的控制器核心，而是**完整的闭环系统模板**：

```
fixed_awff_pid → Templates/IntegratedChains/FixedAwffPid
  └─ extends Example1AWFFSysblockClosedLoop
     └─ 包含：Trajectory + Sensors + Controller + Actuators + Plant

fixed_awff_l1_residual → Templates/IntegratedChains/FixedAwffL1Residual
  └─ extends Example1L1SysblockClosedLoop

fixed_awff_l1_indi → Templates/IntegratedChains/FixedAwffL1Indi
  └─ extends Example1L1SysblockClosedLoop

fixed_linear_mpc_l1_indi → Templates/IntegratedChains/FixedLinearMpcL1Indi
  └─ extends Example1L1SysblockClosedLoop

fixed_qp_nmpc_l1_indi_cbf → Templates/IntegratedChains/FixedQpNmpcL1IndiCbf
  └─ extends Example1L1SysblockClosedLoop
```

**关键特征**：
- 直接实例化整个飞行器+控制器的闭环系统
- 内部 Sysblock 控制器（如 `AWFF_FullControllerEquation_Sysblock`）直接输出电机增量指令
- 不经过 Control/Adapters/ 层
- 不使用 Actuator Mapper
- 已经包含 `motor_command_scale` 和 hover 补偿逻辑

---

## 二、41 个 graphical_control_core 的接入流程

### 2.1 输入清单（权威来源）

**文件**：`Config/control_platform/control_scheme_catalog.json`

```python
# 提取 41 个 graphical_control_core
graphical_schemes = [s for s in catalog['schemes'] 
                     if s['execution_kind'] == 'graphical_control_core'
                     and s['implementation_status'] == 'implemented']
```

**字段说明**：
- `scheme_id`: 控制器唯一标识（如 `cascade_pid`, `lqr_baseline`）
- `implementation_package`: 控制器所属包（如 `PidFamily`, `ClassicRobust`）
- `output_boundary`: 输出边界类型（如 `ATTITUDE_THRUST`）

### 2.2 核心接入规则

#### 规则 1：每个控制器必须有对应的 Adapter

**Adapter 命名规范**：
```
{ControllerName}{OutputBoundary}Adapter

示例：
  cascade_pid + ATTITUDE_THRUST → CascadePidAttitudeThrustAdapter
  dfbc_high_order_bodyrate + BODY_RATE_THRUST → DfbcHighOrderBodyrateThrustAdapter
  official_pid + ROTOR_COMMAND → OfficialPIDGraphicalRotorAdapter
```

**Adapter 位置**：`Models/MoSimQuadrotorModel/Control/Adapters/`

**Adapter 必须继承的 Base 类**：
```
ATTITUDE_THRUST → Control.Interfaces.AttitudeThrustAdapterBase
BODY_RATE_THRUST → Control.Interfaces.BodyRateThrustAdapterBase
ROTOR_COMMAND → Control.Interfaces.RotorCommandAdapterBase
WRENCH → Control.Interfaces.WrenchAdapterBase
```

#### 规则 2：每个控制器必须有 Formal Runner

**Runner 命名规范**：
```
{ControllerName}FormalRunner

示例：
  cascade_pid → CascadePidFormalRunner
  lqr_baseline → LqrBaselineFormalRunner
```

**Runner 位置**：
- 按 `implementation_package` 分组存放
- `ClassicRobust` → `Experiment/ClassicRobust/`
- `PidFamily` → `Experiment/PidFamily/`
- `Optimization` → `Experiment/OptimizationPredictive/`
- `SlidingMode` → `Experiment/SlidingMode/`
- `GeometricFlatness` → `Experiment/GeometricFlatness/`
- `Learning` → `Experiment/Learning/`

**Runner 必须继承的 Base 类**：
```
ATTITUDE_THRUST → Experiment.Runners.Base.FormalAttitudeThrustRunnerBase
BODY_RATE_THRUST → Experiment.Runners.Base.FormalBodyRateThrustRunnerBase
ROTOR_COMMAND → Experiment.Runners.Base.FormalRotorCommandRunnerBase
WRENCH → Experiment.Runners.Base.FormalWrenchRunnerBase
```

**Runner 必须实现的 redeclare**：
```modelica
redeclare MoSimQuadrotorModel.Control.Adapters.{AdapterName} formal_adapter
```

#### 规则 3：Formal Binding JSON 文件（可选，推荐）

**文件路径**：
```
Config/control_platform/g6_champion_bindings/{scheme_id}.json
或
Config/control_platform/runner_baseline_bindings/{scheme_id}.json
```

**JSON 结构**：
```json
{
  "scheme_id": "cascade_pid",
  "output_boundary": "ATTITUDE_THRUST",
  "formal_runner": {
    "model_class": "MoSimQuadrotorModel.Experiment.PidFamily.CascadePidFormalRunner"
  },
  "formal_adapter": {
    "model_class": "MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter"
  }
}
```

### 2.3 接入检查清单（每个控制器必须完成）

对于每个 `graphical_control_core` 控制器，Codex 必须确认：

- [ ] **Adapter 文件存在**：`Control/Adapters/{AdapterName}.mo`
- [ ] **Adapter 继承正确的 Base 类**
- [ ] **Adapter 在 package.order 中注册**
- [ ] **Runner 文件存在**：`Experiment/{Package}/{ControllerName}FormalRunner.mo`
- [ ] **Runner 继承正确的 Base 类**
- [ ] **Runner redeclare 了正确的 Adapter**
- [ ] **Runner 在对应 package.order 中注册**
- [ ] **可以通过 Sysplorer CheckModel 编译**

### 2.4 当前已完成的控制器（11 个）

以下控制器已有完整的 Adapter + Runner + Binding：

**Champion bindings (6 个)**：
1. cascade_pid
2. dfbc_high_order_attitude
3. linear_mpc
4. lqr_baseline
5. super_twisting_smc
6. trained_neural_residual

**Baseline bindings (5 个)**：
1. attitude_thrust (通用测试基线)
2. body_rate_thrust (通用测试基线)
3. px4ctrl
4. rotor_command (通用测试基线)
5. wrench (通用测试基线)

### 2.5 待接入的控制器（30 个）

**ClassicRobust (剩余 11 个)**：
- fopid, lqi_baseline, robust_h2, robust_hinf, robust_mu_synthesis
- adaptive_lqr, gain_scheduled_lqr, optimal_h2, pid_lqr_hybrid
- robust_servo_lqr, state_observer_lqr

**GeometricFlatness (剩余 5 个)**：
- se3_basic, dfbc_basic, dfbc_smooth_robust_attitude, dfbc_high_order_bodyrate, dfbc_smooth_robust_bodyrate

**Optimization (剩余 7 个)**：
- robust_mpc, adaptive_mpc, stochastic_mpc, economic_mpc
- explicit_mpc, distributed_mpc, tube_mpc

**PidFamily (剩余 3 个)**：
- gain_scheduled_pid, fuzzy_pid, neural_pid

**SlidingMode (剩余 6 个)**：
- integral_smc, terminal_smc, nonsingular_terminal_smc
- adaptive_smc, higher_order_smc, disturbance_observer_smc

**Learning (剩余 1 个)**：
- rl_gain_scheduler

---

## 三、5 个整机模板的接入流程

### 3.1 当前问题

这 5 个整机模板**不能**直接用于当前的 Formal Runner 架构，因为：

1. 它们是**完整闭环系统**（Trajectory + Sensors + Controller + Actuators + Plant）
2. 内部 Sysblock 控制器直接输出电机增量指令
3. 不经过 `Control/Adapters/` 层
4. 不使用 `ActuatorMapper`
5. 场景切换（如 OpenBlocks、三机编队）需要整个模板重写

### 3.2 解决方案：拆解整机模板

**目标**：将 Sysblock 控制器从整机模板中提取出来，封装为标准的 `graphical_control_core`

#### 步骤 1：提取 Sysblock 控制器核心

以 `fixed_awff_pid` 为例：

**原始整机模板**（`Example1AWFFSysblockClosedLoop`）：
```modelica
AWFF_FullControllerEquation_Sysblock controller3_2;

// 直接连接到 motor delta
connect(controller3_2.y, motor1_delta_scale.u);
connect(controller3_2.y1, motor2_delta_scale.u);
connect(controller3_2.y2, motor3_delta_scale.u);
connect(controller3_2.y3, motor4_delta_scale.u);
```

**提取后的控制器核心**（`Control/PidFamily/AwffSysblockCore.mo`）：
```modelica
within MoSimQuadrotorModel.Control.PidFamily;
model AwffSysblockCore
  "AWFF Sysblock controller core (extracted from whole-aircraft template)"
  
  // 输入接口（标准化）
  Modelica.Blocks.Interfaces.RealInput x_error;
  Modelica.Blocks.Interfaces.RealInput y_error;
  Modelica.Blocks.Interfaces.RealInput z_error;
  Modelica.Blocks.Interfaces.RealInput z_ref_rate;
  Modelica.Blocks.Interfaces.RealInput roll_mea;
  Modelica.Blocks.Interfaces.RealInput pitch_mea;
  Modelica.Blocks.Interfaces.RealInput yaw_mea;
  Modelica.Blocks.Interfaces.RealInput yaw_ref;
  
  // 输出接口（ROTOR_COMMAND 边界）
  Modelica.Blocks.Interfaces.RealOutput motor_delta[4];
  
  // 内部 Sysblock 控制器
  AWFF_FullControllerEquation_Sysblock controller;
  
equation
  // 输入映射
  connect(x_error, controller.x_error);
  connect(y_error, controller.y_error);
  connect(z_error, controller.z_error);
  connect(z_ref_rate, controller.z_ref_rate);
  connect(roll_mea, controller.roll_mea);
  connect(pitch_mea, controller.pitch_mea);
  connect(yaw_mea, controller.yaw_mea);
  connect(yaw_ref, controller.yaw_ref);
  
  // 输出映射
  motor_delta[1] = controller.y;
  motor_delta[2] = controller.y1;
  motor_delta[3] = controller.y2;
  motor_delta[4] = controller.y3;
  
end AwffSysblockCore;
```

#### 步骤 2：创建 Adapter

**文件**：`Control/Adapters/AwffSysblockRotorAdapter.mo`

```modelica
within MoSimQuadrotorModel.Control.Adapters;
model AwffSysblockRotorAdapter
  "Adapter for AWFF Sysblock controller (ROTOR_COMMAND boundary)"
  extends MoSimQuadrotorModel.Control.Interfaces.RotorCommandAdapterBase;
  
  // 实例化控制器核心
  MoSimQuadrotorModel.Control.PidFamily.AwffSysblockCore controller_core;
  
equation
  // 输入映射（从传感器到控制器核心）
  connect(sensed_state, controller_core.x_error);  // 需要展开适配
  connect(reference_trajectory, controller_core.x_ref);  // 需要展开适配
  
  // 输出映射（从控制器核心到执行器）
  connect(controller_core.motor_delta, rotor_command_output);
  
end AwffSysblockRotorAdapter;
```

#### 步骤 3：创建 Formal Runner

**文件**：`Experiment/PidFamily/AwffSysblockFormalRunner.mo`

```modelica
within MoSimQuadrotorModel.Experiment.PidFamily;
model AwffSysblockFormalRunner
  "Formal runner for AWFF Sysblock controller"
  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalRotorCommandRunnerBase(
    redeclare MoSimQuadrotorModel.Control.Adapters.AwffSysblockRotorAdapter formal_adapter
  );
end AwffSysblockFormalRunner;
```

#### 步骤 4：更新 catalog

将 `execution_kind` 从 `full_profile_whole_aircraft` 改为 `graphical_control_core`：

```json
{
  "scheme_id": "awff_sysblock",
  "execution_kind": "graphical_control_core",
  "implementation_package": "PidFamily",
  "output_boundary": "ROTOR_COMMAND",
  "implementation_status": "implemented"
}
```

### 3.3 五个整机模板的拆解计划

| 原 scheme_id | 新 scheme_id | Controller Core | Output Boundary | 优先级 |
|--------------|--------------|-----------------|-----------------|--------|
| fixed_awff_pid | awff_sysblock | AwffSysblockCore | ROTOR_COMMAND | P1 |
| fixed_awff_l1_residual | awff_l1_residual_sysblock | AwffL1ResidualSysblockCore | ROTOR_COMMAND | P2 |
| fixed_awff_l1_indi | awff_l1_indi_sysblock | AwffL1IndiSysblockCore | ROTOR_COMMAND | P2 |
| fixed_linear_mpc_l1_indi | linear_mpc_l1_indi_sysblock | LinearMpcL1IndiSysblockCore | ROTOR_COMMAND | P2 |
| fixed_qp_nmpc_l1_indi_cbf | qp_nmpc_l1_indi_cbf_sysblock | QpNmpcL1IndiCbfSysblockCore | ROTOR_COMMAND | P3 |

**注意**：
- 原始整机模板文件**保留**在 `Templates/IntegratedChains/` 作为历史参考
- 新的拆解后控制器作为 `graphical_control_core` 接入标准流程

---

## 四、Codex 执行指令

### 4.1 优先级排序

**P0（已完成）**：
- ✅ 清理 19 个遗留 Adapter

**P1（高优先级，立即执行）**：
1. 完成剩余 30 个 `graphical_control_core` 的接入（Adapter + Runner）
2. 拆解 `fixed_awff_pid` 整机模板（作为示例）

**P2（中优先级）**：
3. 拆解剩余 4 个整机模板

**P3（低优先级）**：
4. 为所有 41 个控制器生成 Formal Binding JSON

### 4.2 执行约束（Codex 必须遵守）

#### 硬约束（违反则失败）

1. **禁止修改已标定参数**（CLAUDE.md 第4节）
   ```
   kp_attitude=14.142, kd_attitude=1.414, kp_yaw=5, iner_limit=7
   command_scale=hover_speed/13.985413115099604
   Kv=Kp=1.5, m=1, g=9.80665, hover=0.37
   ```

2. **禁止 git 操作**
   - 不得执行 `git add/commit/push/stage`

3. **Adapter 必须继承正确的 Base 类**
   - 不得创建不继承 Base 的 Adapter

4. **Runner 必须 redeclare formal_adapter**
   - 不得省略 redeclare 语句

5. **文件必须在 package.order 中注册**
   - 新增文件必须同步更新对应的 package.order

#### 软约束（推荐遵守）

1. **优先使用已有的 Adapter 模式**
   - 参考 `CascadePidAttitudeThrustAdapter` 的实现
   - 参考 `DfbcHighOrderAttitudeThrustAdapter` 的实现

2. **命名规范**
   - Adapter: `{ControllerName}{OutputBoundary}Adapter`
   - Runner: `{ControllerName}FormalRunner`
   - 使用 PascalCase

3. **文档注释**
   - 每个 Adapter/Runner 必须有一行 description
   - 格式：`"<Controller Name> adapter/runner for <output boundary> interface"`

### 4.3 验证流程

Codex 每完成一批控制器（建议每 5 个）后，必须执行：

```python
# 1. 检查文件完整性
assert os.path.exists(f"Control/Adapters/{adapter_name}.mo")
assert os.path.exists(f"Experiment/{package}/{runner_name}.mo")

# 2. 检查 package.order 注册
assert adapter_name in open("Control/Adapters/package.order").read()
assert runner_name in open(f"Experiment/{package}/package.order").read()

# 3. Sysplorer CheckModel（关键）
# 使用 mcp__sysplorer__check_model 工具
check_result = check_model(model_name=f"MoSimQuadrotorModel.Experiment.{package}.{runner_name}")
assert check_result['ok'] == True
```

### 4.4 输出要求

Codex 每完成一批后，必须生成报告：

**文件**：`Docs/Cache/controller_integration_progress.md`

**格式**：
```markdown
# 控制器接入进度报告

## 已完成（XX/41）

| scheme_id | Adapter | Runner | CheckModel | 备注 |
|-----------|---------|--------|------------|------|
| cascade_pid | ✅ | ✅ | ✅ | 已验证 |
| lqr_baseline | ✅ | ✅ | ✅ | 已验证 |
| fopid | ✅ | ✅ | ⏳ | 待验证 |

## 失败项

| scheme_id | 失败原因 | 解决方案 |
|-----------|----------|----------|
| xxx | CheckModel 报错：missing dependency | 需要添加 XXX 库 |

## 下一步

- [ ] 完成剩余 XX 个控制器
- [ ] 拆解整机模板
```

---

## 五、常见问题与解决方案

### Q1：控制器核心找不到怎么办？

**检查顺序**：
1. 在 `Control/{Package}/` 下搜索 `*.mo` 文件
2. 在 `Control/Cores/` 下搜索（部分控制器核心可能独立存放）
3. 查看 catalog 的 `implementation_package` 字段
4. 如果确实不存在，标记为 `missing_core` 并跳过

### Q2：输出边界不明确怎么办？

**判断规则**：
- 如果控制器输出是 `[roll_cmd, pitch_cmd, yaw_rate_cmd, thrust_cmd]` → ATTITUDE_THRUST
- 如果控制器输出是 `[p_cmd, q_cmd, r_cmd, thrust_cmd]` → BODY_RATE_THRUST
- 如果控制器输出是 `[motor1_cmd, motor2_cmd, motor3_cmd, motor4_cmd]` → ROTOR_COMMAND
- 如果控制器输出是 `[fx, fy, fz, mx, my, mz]` → WRENCH

**如果仍不确定**：
- 参考 catalog 中的 `output_boundary` 字段（如果有）
- 参考同一 package 下其他控制器的边界
- 标记为 `unclear_boundary` 并询问用户

### Q3：CheckModel 报错怎么办？

**常见错误与解决方案**：

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Class XXX not found` | 控制器核心路径错误 | 检查 package 声明和 import |
| `Type mismatch in connection` | 接口类型不匹配 | 检查 Adapter 的输入输出接口定义 |
| `Missing redeclare` | Runner 未 redeclare Adapter | 添加 redeclare 语句 |
| `Circular dependency` | 继承链循环 | 检查 extends 关系 |

**调试流程**：
1. 单独 CheckModel Adapter
2. 单独 CheckModel Runner（不连接 Plant）
3. CheckModel 完整的 Runner（连接 Plant）

### Q4：整机模板拆解遇到接口不兼容？

**症状**：
- Sysblock 控制器的输入输出接口与标准 Adapter 不匹配
- 例如：Sysblock 期望 `x_error`, `y_error` 分离输入，但 Adapter 提供 `position_error[3]`

**解决方案**：
- 在 Adapter 内部添加信号转换逻辑
- 示例：
  ```modelica
  equation
    controller_core.x_error = sensed_state.position[1] - reference_trajectory.position[1];
    controller_core.y_error = sensed_state.position[2] - reference_trajectory.position[2];
    controller_core.z_error = sensed_state.position[3] - reference_trajectory.position[3];
  ```

---

## 六、关键文件清单

### Codex 必须熟悉的文件

1. **权威配置**：
   - `Config/control_platform/control_scheme_catalog.json` — 控制器清单
   
2. **Adapter Base 类**：
   - `Control/Interfaces/AttitudeThrustAdapterBase.mo`
   - `Control/Interfaces/BodyRateThrustAdapterBase.mo`
   - `Control/Interfaces/RotorCommandAdapterBase.mo`
   - `Control/Interfaces/WrenchAdapterBase.mo`
   
3. **Runner Base 类**：
   - `Experiment/Runners/Base/FormalAttitudeThrustRunnerBase.mo`
   - `Experiment/Runners/Base/FormalBodyRateThrustRunnerBase.mo`
   - `Experiment/Runners/Base/FormalRotorCommandRunnerBase.mo`
   - `Experiment/Runners/Base/FormalWrenchRunnerBase.mo`
   
4. **参考实现**（标杆）：
   - `Control/Adapters/CascadePidAttitudeThrustAdapter.mo`
   - `Experiment/PidFamily/CascadePidFormalRunner.mo`
   - `Config/control_platform/g6_champion_bindings/cascade_pid.json`

### Codex 禁止修改的文件

1. **标定参数**（CLAUDE.md 第4节列出的所有参数）
2. **Base 类**（除非发现设计缺陷且经过用户确认）
3. **已归档文件**（`E:\刘致远18001500226\MoSim_Archive\`）

---

## 七、成功标准

当满足以下条件时，认为接入工作完成：

1. **41 个 graphical_control_core**：
   - ✅ 每个都有对应的 Adapter（在 `Control/Adapters/`）
   - ✅ 每个都有对应的 Runner（在 `Experiment/{Package}/`）
   - ✅ 所有 Runner 都能通过 CheckModel
   - ✅ 所有文件都在 package.order 中注册

2. **5 个整机模板**：
   - ✅ 控制器核心已提取到 `Control/{Package}/`
   - ✅ 已创建对应的 Adapter 和 Runner
   - ✅ 能通过 CheckModel
   - ✅ 原始整机模板文件保留作为参考

3. **文档齐全**：
   - ✅ `controller_integration_progress.md` 包含完整进度
   - ✅ `control_scheme_catalog.json` 已更新
   - ✅ 所有新增文件都有注释

4. **用户验证**：
   - ✅ 用户运行 `Px4CtrlRunner`（OpenBlocks 场景）无报错
   - ✅ 用户运行 `ThreeUavPx4CtrlFormationRunner`（三机编队）无报错
   - ✅ 用户随机抽查 5 个新接入的 Runner 能正常仿真

---

## 八、Codex 启动清单

在开始接入工作前，Codex 必须完成：

- [ ] 读取 `CLAUDE.md` 和 `AGENTS.md`（了解硬约束）
- [ ] 读取 `Config/control_platform/control_scheme_catalog.json`（获取权威清单）
- [ ] 读取 4 个 Adapter Base 类（理解接口契约）
- [ ] 读取 4 个 Runner Base 类（理解继承关系）
- [ ] 读取 `CascadePidAttitudeThrustAdapter.mo`（参考实现）
- [ ] 读取 `CascadePidFormalRunner.mo`（参考实现）
- [ ] 读取本文档（理解完整流程）

---

## 九、联系方式

如果 Codex 遇到以下情况，必须停止并询问用户：

1. **控制器核心文件找不到**（搜索了所有 package 后仍未找到）
2. **输出边界无法判断**（控制器输出格式不符合任何已知边界）
3. **CheckModel 报错无法解决**（尝试了所有常见方案后仍失败）
4. **需要修改 Base 类**（发现 Base 类设计缺陷）
5. **需要修改标定参数**（控制器实现依赖不同的参数值）

**停止信号格式**：
```
🛑 Codex 请求用户介入

**问题**：[简短描述]
**控制器**：[scheme_id]
**已尝试方案**：[列出已尝试的 2-3 个方案]
**建议方案**：[Codex 的建议]

请用户确认是否继续。
```

---

## 附录 A：输出边界接口规范

### ATTITUDE_THRUST

**输出信号**：
```modelica
Modelica.Blocks.Interfaces.RealOutput roll_cmd;      // rad
Modelica.Blocks.Interfaces.RealOutput pitch_cmd;     // rad
Modelica.Blocks.Interfaces.RealOutput yaw_rate_cmd;  // rad/s
Modelica.Blocks.Interfaces.RealOutput thrust_cmd;    // N
```

### BODY_RATE_THRUST

**输出信号**：
```modelica
Modelica.Blocks.Interfaces.RealOutput p_cmd;      // rad/s (roll rate)
Modelica.Blocks.Interfaces.RealOutput q_cmd;      // rad/s (pitch rate)
Modelica.Blocks.Interfaces.RealOutput r_cmd;      // rad/s (yaw rate)
Modelica.Blocks.Interfaces.RealOutput thrust_cmd; // N
```

### ROTOR_COMMAND

**输出信号**：
```modelica
Modelica.Blocks.Interfaces.RealOutput motor_cmd[4];  // rad/s (motor speed commands)
```

### WRENCH

**输出信号**：
```modelica
Modelica.Blocks.Interfaces.RealOutput force[3];   // [fx, fy, fz] in N
Modelica.Blocks.Interfaces.RealOutput moment[3];  // [mx, my, mz] in N·m
```

---

**文档版本**：v1.0  
**创建日期**：2026-08-18  
**作者**：Claude Code  
**审核者**：待用户确认
