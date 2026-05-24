# Sysplorer + Sysblock 混合建模工作流

> 适用范围：物理 Modelica 模型作为顶层或 plant，嵌入一个或多个已完成的 Sysblock 控制器/算法模型，通过 Sysblock `Inport` / `Outport` 暴露出的信号端口与物理模型连接。
>
> 本文不替代 `modeling_path_router.md`、`sysblock_style_guide.md`、`modelica_style_guide.md`、`modelica_diagram_connect_semantics.md` 和 `seven_gates_workflow.md`。混合建模只是把两条路径按层级组合起来：**Sysblock 子模型用官方 API 搭建**，**Modelica 物理顶层用 `.mo` 文本搭建**。

## 核心结构

- **Sysblock 子模型**：只包含 Sysblock 块图、子系统、状态机、离散控制、传递函数、PID、CCaller 等控制/算法结构；通过 `SysplorerEmbeddedCoder.Port.Inport` 和 `SysplorerEmbeddedCoder.Port.Outport` 暴露边界。
- **Modelica 物理模型 / 顶层模型**：包含物理 plant、Modelica 信号源/接口、商业物理库组件、已完成的 Sysblock 模型实例，以及顶层 `connect()`。
- **允许方向**：物理模型内嵌套已搭建完成的 Sysblock 模型。
- **禁止方向**：Sysblock 模型内嵌套物理模型；同一模型层直接混放物理组件与 Sysblock 基础块；用手写 `.mo` 替代 Sysblock 内部拓扑 API。

## 平台边界：同层混放 vs SECInstance 嵌入

不要把普通建模 API 的同层插入限制误总结为“Sysplorer 不支持混合模型”。当前经验边界应写成：

- 普通 `AddComponent` 路径下，在同一个普通模型层直接插入 `SysplorerEmbeddedCoder` 基础块和 `TYHydraulics` / Modelica 物理组件，可能被平台拒绝。例如 Sysblock 模型层拒绝物理液压组件，Modelica 物理模型层也可能拒绝直接插入 Sysblock 基础块。
- 可行混合路径是**分层封装**：先独立完成并检查 Sysblock 控制器/算法模型，再在 Modelica 物理顶层中把该模型作为 Sysplorer 识别的 SEC 实例嵌入；样例形态通常保留 `annotation(...,__MWORKS(SECInstance=true))`。
- 若用户或工具已经在物理顶层插入了 SEC 实例，例如 `HydraulicPositionClosedLoop` 中的 `HydraulicPositionSysblockController hydraulicPositionSysblockController annotation (...,__MWORKS(SECInstance=true));`，agent 应继续读取该实例暴露出的 `Inport` / `Outport` 映射端口并完成顶层连接、参数设置、检查、翻译与仿真。
- 若物理顶层尚无 SEC 实例，不要用普通 `AddComponent` 硬插 Sysblock 基础块来“混放”。应使用 Sysplorer 支持的混合实例插入流程，或请用户先提供/插入已封装的 Sysblock 实例，再进行自动接线和联调。

液压位置闭环案例的成功模式是：`HydraulicPositionSysblockController` 负责阶跃指令、误差、PID、限幅和显示；`HydraulicPositionClosedLoop` 作为物理顶层，包含 `TYHydraulics` 泵、溢流阀、换向阀、液压缸与机械负载，并只通过 SEC 实例暴露端口连接 `x_meas`、`valve_cmd` 等边界信号。

## 建模顺序

1. **定义接口契约**  
   写清每个跨域信号：名称、方向、类型、维度、采样周期、单位/物理含义。控制器输入/输出优先用稳定、可读的名称，如 `V_ref`、`V_feedback`、`outport`、`Target`、`Initial`。

2. **构建 Sysblock 子模型**  
   按 `sysblock_style_guide.md`：先设计组件/布局/连线/参数表，再用 `call_code(mode="run_script")` 与 ModelingPy 官方 API 创建或编辑。必须显式 `NewModel(..., restriction="Sysblock")`，加载库名使用 `SysplorerEmbeddedCoder`。禁止 `SetModelText` / 文本覆写。子模型必须先 `check_model` 通过。

3. **构建或准备物理 plant**  
   按 `modeling_path_router.md` 的 Modelica 物理分支先做库优先判断。物理模型用纯文本 `.mo` 编写，物理连接器、信号接口、`Placement` 与 `Line` 图解语义按 `modelica_style_guide.md` 和 `modelica_diagram_connect_semantics.md`。

4. **构建混合顶层 `.mo`**  
   在物理顶层实例化已完成的 Sysblock 模型。样例中 Sysblock 实例带有 `annotation(...,__MWORKS(SECInstance=true))`，用于保留 Sysplorer 对 Sysblock 实例的识别语义；不要手工改写 Sysblock 内部块图，只在顶层连接其暴露端口。

   若顶层已经存在该 SEC 实例，优先复用并查询其端口；若不存在，不要把普通 `AddComponent` 拒绝同层混放当作混合建模失败，应改走支持 SEC 实例嵌入的路径或要求用户先插入该实例。

5. **连接与图解注解**  
   顶层 `connect()` 是 Modelica 物理顶层的一部分，必须带 `annotation(Line(...))`。信号连接常见颜色约定：Real 信号多见 `{0,0,127}`，普通/框图信号多见 `{0,0,0}`；以现有模型和 Sysplorer 导出结果为准。

6. **分层检查与仿真**  
   先 `check_model` Sysblock 子模型，再检查物理 plant（如独立存在），最后检查混合顶层模型。顶层检查通过后执行 Gate 6：审查/修复顶层 `.mo` 的图解语义与布局；若 `smart_layout` 写回了 `.mo`，重新 `check_model`。联调仿真只对混合顶层模型运行。

## 类型与维度规则

| Sysblock 侧 | Modelica / 物理侧 |
|-------------|-------------------|
| `float` / `double` | `Real` / `Modelica.Blocks.Interfaces.RealInput` / `RealOutput` |
| `int8` / `uint8` / `int16` / `uint16` / `int32` / `uint32` | `Integer` / `IntegerInput` / `IntegerOutput` |
| `fixdt` | 按任务和工具支持情况显式确认，禁止猜测 |
| `enum` | 无通用自动映射；需显式设计转换 |
| `Bus` | 结构一致的连接器；物理侧 `BusCreator` / `BusSelector` 类型与维度需手动设置 |

- 连接两端数据维度与长度必须一致。
- 物理或框图端口都可选择数组分量连接；选择规则必须在接口契约中写清。
- 不确定端口类型时，用 `get_lib_model_document`、`sysblock_model_library` 语料和模型检查结果交叉确认。

## 顶层模式示例

### 温控入门模式

- Sysblock 子模型：`Target`、`Initial` 两个 `Inport`，`outport` 一个 `Outport`；内部由 `Sum`、`Gain`、`Sum` 实现控制计算。
- 物理/顶层模型：`Modelica.Blocks.Sources.Constant` 提供目标值和初值；Sysblock 实例接收输入并输出到 `RealOutput`。
- 样例文件：`Docs/Sysblock/Samples/Sysblock/SysblockQuickStart/HybridSimulation/Model_TC.mo` 与 `Model_Mix_TC.mo`。

### Buck 控制模式

- Sysblock 子模型：控制器暴露 `V_ref`、`V_feedback`、`outport1`；可用 `DiscretePIDController`、`DiscreteTransferFcn` 或 `CCaller`。
- 物理 plant：Buck 电路模型暴露控制输入 `u` 和反馈输出 `y`。
- 顶层连接：`V_ref.y -> controller.V_ref`，`controller.outport1 -> plant.u`，`plant.y -> controller.V_feedback`。
- 样例目录：`Docs/Sysblock/Samples/Sysblock/ApplicationCase/Demo_BuckCircuit/Buck_Contrl/`。

### 机械臂控制模式

- Sysblock 子模型：状态机、动作编组、Bus/DeMux、单位延迟、类型转换等控制逻辑。
- 物理 plant：多体机械臂模型通过 `IntegerInput` / `RealOutput` 暴露舵机角度与末端位置。
- 数据准备：基础工作区与模型工作区 JSON 参数是仿真前依赖，缺失时应先导入或确认等效参数已存在。
- 样例目录：`Docs/Sysblock/Samples/Sysblock/ApplicationCase/Demo_RobotArm/Default5/`。

## 验收清单

- [ ] 已明确混合边界信号：名称、方向、类型、维度、采样周期、单位/含义。
- [ ] Sysblock 子模型按官方 API 创建/编辑，未使用 `SetModelText` 或手写 `.mo` 拓扑。
- [ ] Sysblock 子模型已 `check_model` 通过。
- [ ] 物理 plant / 顶层按 Modelica 纯文本规则编写，物理库选择已做库优先判断。
- [ ] 混合顶层只实例化已完成的 Sysblock 模型，并通过暴露端口连接；未在 Sysblock 内嵌物理模型。
- [ ] 若顶层依赖 SEC 实例，该实例已存在或已通过受支持流程插入，且保留类似 `__MWORKS(SECInstance=true)` 的识别语义；未使用普通同层 `AddComponent` 强行混放 Sysblock 基础块与物理组件。
- [ ] 已读取并核对 SEC 实例暴露端口，例如控制输入、反馈输入、控制输出和显示输出，顶层连接只使用这些边界端口。
- [ ] 顶层 `connect()` 均带合格 `Line` 图解注解，实例带可用 `Placement`。
- [ ] 混合顶层已 `check_model` 通过；Gate 6 布局/图解验收已完成，必要时 `smart_layout` 后已复检。
- [ ] 仿真对象是混合顶层模型，KPI/结果变量使用顶层或嵌套变量路径验证。
