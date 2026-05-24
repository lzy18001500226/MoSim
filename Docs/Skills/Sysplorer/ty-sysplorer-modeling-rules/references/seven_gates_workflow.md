# MWorks 建模全局规则与执行闭环

> 本文为本技能包内「全局工程规则（7 Gates）」与「AI 自主执行闭环」的权威说明。与同 skill `references/` 下其它规范一并使用；若与工作区 `resources/` 树中其它副本不一致，以工作区为准。

## 全局工程规则（7 Gates）

> 所有 Gate 均为硬性约束，不可跳过。违反即为流程错误，不允许以"疏忽"为由。

**Gate 0: 规范优先** — 创建/修改 `.mo` 前需了解代码风格和库结构。豁免：已记录的类型、会话已读过、仅改参数。必须读：新库结构时读 **`modelica_style_guide.md`**（本 skill `references/`）。**Sysblock 路径**（`modeling_path_router.md` §1.2）以 **`sysblock_style_guide.md`**（同目录）为准。**混合路径**（§1.3）还须读 **`hybrid_modeling_workflow.md`**，并按子模型分别套用 Sysblock 与 Modelica 规则。禁止从 `src/` 现有代码推断风格。

**⛔ Gate 1: Library First（每次建模前必检查）** — 须先按 `modeling_path_router.md` **§1** 完成路径分流。**Modelica 物理路径（§1.1）**：写任何 **该路径下** `.mo` 组件代码前，先确认是否有 TY/TA 私有库版本；**搭建类还须先做 §0**：从用户描述提取域/部件关键词 → 对照 quickref §1 与 `MetaDataLib.json` → 判断能否优先用同元内置库实现；能则后续选型与 `uses()` 以此为准。查询顺序：① `private_lib_quickref.md` → ② `load_library`（尚未加载时）+ `get_lib_model_document(full_class_name=...)` → ③ 才考虑 MSL。私有库有则**必须用**。豁免：quickref 已覆盖或任务明确要求自建。**Sysblock 路径（§1.2）**：**不适用 §0**；块图「Library First」指优先 **`SysplorerEmbeddedCoder.*`**，配合 `sysblock_model_library` 语料与 `get_lib_model_document`；**禁止**为搭框图去装配 `TYHydraulics` 等 **Modelica 物理库** 作为主路径。**混合路径（§1.3）**：Sysblock 子模型按 §1.2 预热 `SysplorerEmbeddedCoder`；物理 plant / 顶层按 §1.1 与 §0 做物理库优先判断。**总述**：Sysblock 搭框图**禁止** `SetModelText` / `setmodeltext` 及任意文本覆写，**须全程**用 Sysplorer **官方建模 API**（`run_script` / ModelingPy，`get_api_document` 核对，细则见 `sysblock_style_guide.md`）。

**Gate 2: 零幻觉连线** — **Modelica 物理路径**：`connect(a, b)` 前确认两侧**物理连接器**类型一致。豁免：会话上下文已明确。必须读：未覆盖的连接器类型查 quickref。绝不编造不存在的类名或端口名。**Sysblock 路径**：以块图端口与 API 为准，本条不指块间信号连线的手工 `connect()` 臆造。**混合路径**：跨域连接前必须确认 Sysblock `Inport` / `Outport` 映射到物理侧 `Real` / `Integer` / Bus 的类型和维度一致。

**Gate 3: 编译驱动** — 新建/修改 `.mo` 后**必须立即** `check_model`。严禁运行有编译错误的模型。失败必须进入闭环修复：同一失败点允许最多 3 轮直接自修复；第 3 轮仍未通过时，**不得结束流程或继续盲猜**，必须升级为根因诊断（查类文档/端口/参数、做最小复现或组件级验证、分层隔离问题），诊断后继续回到失败 Gate 复验。只有在缺少用户需求信息、需要改变用户指定拓扑/关键组件、或工具/环境不可用时，才暂停并向用户说明具体阻塞与所需决策。**混合路径**须分层检查：Sysblock 子模型先通过，再检查物理 plant（如独立存在），最后检查混合顶层模型。

**Gate 4: Testbench Required** — 变更后**必须**在 `tests/` 添加/更新测试台并 `simulate_model`（仅实例化不算完成）。

**Gate 5: 物理 KPI 验证** — 仿真后**必须**通过 `result_manager`（`action=get_var_values` 等）验证。变量名三级决策：① quickref §8 直接填 → ② 推断后猜测，报错再 `action=get_result_variables` → ③ 黑盒组件用 `get_result_variables` 取列表。硬性约束：p > 0, T > 0；冷却稳态温度 ≥ 冷却介质入口温度。

**⛔ Gate 6: Auto-Layout Required（系统级，每次建模前必检查）** — **时序硬性约束：须在 `check_model` 已成功通过之后、在 `translate` / 首次长仿真（或等价 `fast_workflow` 中的翻译+仿真主段）之前完成**；**禁止**把系统级智能布局/图面定稿**只**放在首轮仿真成功之后作为唯一主流程。**仅 Modelica 物理路径（§1.1）**：系统级 `.mo` **唯一推荐写入路径**为 `smart_layout`，`mode=writeback_mo`（别名 `writeback` / `generate`），`auto_layout=true`。**纯文本**编写拓扑时，必须先按 **`modelica_diagram_connect_semantics.md`** 与 **`modelica_style_guide.md` Part 3** 把 `Placement`、`connect` 的 `Line`（及必要 `Icon`/`Diagram` 图元）写规范，使 `graph_json` / 管线能解析并做自动布局与布线；须配合 `modelica_code` + `graph_json`（或 `graph_json_path`）及 `model_output_path` 等；`graph_json.children` 含 `world` 节点（如有 inner World），否则无 Placement。若 `writeback_mo` 改动了 `.mo`，**须再次** `check_model` 通过后再进入翻译/长仿真。交付含布局状态。**Sysblock 路径**：不适用 `writeback_mo` 的同一套主路径，但**仍须**在 **`check` 通过之后、在 `translate` 与 `simulate` 之前** 完成该路径允许的连线/图面优化（见 **`sysblock_style_guide.md`**）；块图主搭建仍以 `run_script` / 块图 API 为准。**混合路径**：顶层 `.mo` 属于 Modelica 图面验收范围，必须检查 Sysblock 实例、物理组件与跨域 `connect()` 的 `Placement` / `Line`；必要时对顶层执行 `smart_layout`，写回后复检。

**Gate 7: Delivery Evidence** — 最终回复输出证据（系统级 `layout` 必填）：
```json
{"target_status":"met | not_met | blocked","minimum_loop_ok":true,"objective_met":true,"lib_document":{"queried_classes":[],"ok":true},"mapping":{"used":[],"rejected":{}},"check":{"ok":true,"errors":[]},"sim":{"ok":true},"kpi":{"var":"value"},"layout":"ok | skipped(component-level)","repair_summary":[],"remaining_gaps":[]}
```

## Workflow / AI 自主执行闭环

无专用领域 workflow 更适合时，使用本默认流程。全程遵守上方 7 Gates；任一 Step 的 Checkpoint 未通过，不得进入下一 Step。

**闭环终止条件**：流程只能在以下情况下结束：① 用户最终目标已经达成并完成 Gate 7 证据；② 用户明确要求停止；③ 存在必须由用户决策的硬阻塞（例如需求缺失、目标冲突、需要改变用户指定拓扑/关键组件、工具或环境不可用）。任何 Gate 失败都不能直接结束，必须进入 Step 11，修复并回到失败 Step / Gate 复验。

### Step 0: Session Health

**GATE**：开始任何 Sysplorer 建模、检查、翻译或仿真前。

**Goal**：确保 Sysplorer 驱动可用。

Execution rules:

- 执行 `session_manager(action="health")`。
- 若不可用，执行 `session_manager(action="restart")` 或 `session_manager(action="ensure")`，直至驱动可用或确认工具/环境硬阻塞。

**Checkpoint**：Sysplorer 会话健康，或已记录硬阻塞并转 Step 11 / Gate 7。

---

### Step 1: Source And Requirement Understanding

**GATE**：用户已提供任务文本、模型文件、文档或明确目标。

**Goal**：把输入转成可执行建模目标，明确最终成功标准。

Execution rules:

- 解析需求 / 读文档 / PDF；保留原始路径和关键信息来源。
- 必须识别：模型对象、建模目的、路径类型候选、关键部件、关键参数、待观测变量、仿真目标、交付物、成功标准。
- 若只需解释、查询或局部参数修改，记录豁免项；若为搭建或扩展模型，继续 Step 2。

**Checkpoint**：能回答“建什么、为什么建、用什么路径/库、看哪些结果、什么算成功”。否则暂停向用户索取缺失决策。

---

### Step 2: Modeling Path Routing

**GATE**：Step 1 完成，且任务涉及新建、搭建、扩展或修复模型。

**Goal**：按 `modeling_path_router.md` 完成路径分流，防止把 Modelica、Sysblock、混合路径混用。

Execution rules:

- 先读并执行 **`modeling_path_router.md` §1**。
- **判为混合（§1.3）**：进入 `hybrid_modeling_workflow.md`，并继续套用本 workflow 的检查、布局、仿真、交付闭环。
- **判为 Sysblock（§1.2）**：读取 `sysblock_style_guide.md`，不执行 `modeling_path_router.md` §0；禁止文本建模。
- **判为 Modelica 物理（§1.1）**：再执行 **`modeling_path_router.md` §0**，然后继续 Step 3。

**Checkpoint**：路径已明确，且后续工具、库、建模方式与该路径一致。

---

### Step 3: Library And Component Evidence

**GATE**：Step 2 已完成路径分流。

**Goal**：落实 Gate 1 / Gate 2，确认库、类、端口、连接器和替代方案有证据。

Execution rules:

- **Modelica 物理**：quickref 未覆盖时，对已选类名执行 `load_library`（若需）+ `get_lib_model_document`；旁置语料用 `resources_retrieval(action="search")` 等，**不**再使用已移除的元数据索引类 tool。
- **Sysblock**：块类型与文档以 `SysplorerEmbeddedCoder` + `get_lib_model_document` / `sysblock_model_library` 为主。
- **混合**：同时完成 Sysblock 子模型选块与物理 plant 选库，确认跨域端口类型和维度。
- 写任何 `connect(a, b)` 前，必须确认两侧连接器或信号端口类型一致。
- 记录使用的类、拒绝的候选、替代原因和未解决风险。

**Checkpoint**：关键类、端口、连接器、库加载和替代选择均有证据；不存在未解释的类名、端口名或连接器臆造。

---

### Step 4: Model Construction

**GATE**：Step 3 通过，核心参数可用或假设已明确。

**Goal**：构建最小可运行、可审查的模型实体。

Execution rules:

- **Modelica 物理**：编写含物理 `connect()` 的 `.mo`；图解侧元数据须满足 **`modelica_diagram_connect_semantics.md`** 与 **`modelica_style_guide.md` Part 3**（`Placement`、`Line` 等），作为后续 `graph_json` / `smart_layout` 输入。
- **Sysblock**：用 `call_code(mode="run_script")` 和官方建模 API 建块图；禁止 `setmodeltext` / `SetModelText` 进行任何形式的文本建模。
- **混合**：先实现并检查 Sysblock 子模型，再写物理 plant / 顶层 `.mo` 实例化该子模型并连接边界端口。
- 新增 `.mo` 后在父目录 `package.order` 追加类名。
- 若组件行为、端口、参数或连接方式不清楚，先做文档核对或组件级最小验证，不继续扩大完整模型。

**Checkpoint**：目标模型实体存在，关键拓扑、参数、连接和图解语义已实现；可进入检查。

---

### Step 5: Check

**GATE**：Step 4 完成，且待检查对象是最新模型。

**Goal**：落实 Gate 3，确认模型可实例化/编译检查通过。

Execution rules:

- 对目标模型执行 `check_model` 直至通过。
- 混合模型按“Sysblock 子模型 → 物理 plant → 混合顶层”分层检查。
- 若检查失败，立即进入 Step 11；同一失败点直接自修复最多 3 轮，仍失败时升级根因诊断，不退出。

**Checkpoint**：最新模型 `check_model` 通过；若后续写回或修改模型，必须重新回到本 Step。

---

### Step 6: Layout And Diagram Acceptance

**GATE**：Step 5 已通过，且尚未进入 `translate` / 首次长仿真。

**Goal**：落实 Gate 6，使系统级模型图面可审查、可交付。

Execution rules:

- **Modelica 物理**：系统级 `.mo` 使用 `smart_layout(mode="writeback_mo", auto_layout=true)`（或别名 `writeback` / `generate`），配合 `modelica_code` + `graph_json`（或 `graph_json_path`）+ `model_output_path`。
- 若 `smart_layout` 写回 `.mo`，必须回 Step 5 再次 `check_model` 通过。
- **Sysblock**：不套用 `writeback_mo` 主路径；在 `check` 通过后、`translate` / `simulate` 前，按 `sysblock_style_guide.md` 完成允许的连线/图面优化。
- **混合**：对顶层 `.mo` 检查 Sysblock 实例、物理组件与跨域 `connect()` 的 `Placement` / `Line`，必要时布局写回并复检。
- 若图面不可审查、关键 `Placement` / `Line` 缺失或布局与最新连线不一致，返回 Step 4 或 Step 5 修复。

**Checkpoint**：布局状态可写入 Gate 7 `layout` 字段；若写回有变更，复检已通过。

---

### Step 7: Testbench And Translate

**GATE**：Step 6 通过，且模型已具备最新检查结果和布局状态。

**Goal**：落实 Gate 4 的测试台要求，并确认模型可翻译。

Execution rules:

- 变更后必须在 `tests/` 添加或更新测试台；仅实例化不算完成。
- 可用 `translate_model`，或在满足前置 Gate 的前提下使用 `call_code(mode="fast_workflow", payload={...})`。
- 如果上一步已单独做过 `check` / layout，叙述中不得把布局说成“仅仿真后”才做。
- 翻译失败进入 Step 11；先查连接、端口维度、参数、初始化、图解写回后复检状态，不以删除关键拓扑作为默认修复。

**Checkpoint**：测试台存在且翻译通过；可进入仿真。

---

### Step 8: Simulate

**GATE**：Step 7 通过。

**Goal**：运行仿真并生成可读取结果。

Execution rules:

- 使用 `simulate_model` 或 `fast_workflow` 的仿真段。
- 混合路径仿真对象为混合顶层模型，变量可使用嵌套路径。
- 仿真失败进入 Step 11；先检查初始化、边界、步长、求解器、参数量级和测试台连接。

**Checkpoint**：仿真完成，结果文件/结果会话可由 `result_manager` 读取。

---

### Step 9: KPI And Result Verify

**GATE**：Step 8 完成且仿真结果可读取。

**Goal**：落实 Gate 5，判断结果是否满足真实任务目标。

Execution rules:

- 通过 `result_manager(action="get_var_values")`、`get_var_value_at`、`get_vars_values` 等读取关键变量。
- 变量名按三级决策：quickref §8 直接填 → 推断后探测 → 黑盒组件取 `get_result_variables` 列表。
- 验证硬性 KPI：例如 `p > 0`、`T > 0`、冷却稳态温度 ≥ 冷却介质入口温度；并验证用户指定目标。
- 若仿真通过但 KPI、趋势、稳态/动态行为或用户目标不满足，进入 Step 10.5，而不是直接交付。

**Checkpoint**：结果变量已读取，KPI 结论明确，可判断 `minimum_loop_ok` 与 `objective_met`。

---

### Step 10: Delivery Evidence

**GATE**：Step 9 完成，且最小闭环已可评价。

**Goal**：落实 Gate 7，交付模型状态与证据。

Execution rules:

- 最终回复必须包含 Gate 7 证据；系统级 `layout` 必填。
- `minimum_loop_ok=true` 只表示 `check -> layout -> translate -> simulate -> KPI读取` 链路成立，不等于最终目标达成。
- 若 `objective_met=false` 或 `target_status!="met"`，不得把当前状态描述为最终完成，必须进入 Step 10.5 或说明硬阻塞。
- 默认不额外生成过程报告文件，除非用户明确要求。

**Checkpoint**：若 `target_status="met"` 且 `objective_met=true`，workflow 可结束；否则继续 Step 10.5 或 Step 11。

---

### Step 10.5: Optimization Toward Final Requirement

**GATE**：Step 10 表明最小闭环可运行，但最终目标尚未达成。

**Goal**：继续迭代，直到用户目标达成或出现必须用户决策的硬阻塞。

Execution rules:

- `check`、`layout`、`translate`、`simulate` 通过只表示最小闭环可运行，不等于用户最终目标达成。
- 如果 KPI、稳态/动态行为、图面可审查性、交付文件位置、测试台覆盖或用户指定目标仍不满足，回到参数补全、模型结构、仿真设置、布局或 KPI 验证步骤继续迭代。
- 每轮优化后必须重跑受影响链路：通常为 `check -> Gate 6 layout/复检 -> translate -> simulate -> KPI`；若仅改后处理，可只重跑结果读取与 KPI 验证。
- 最终交付必须明确 `objective_met=true`；若不能达成，必须把 `target_status` 标为 `blocked` 或 `not_met`，并列出 `remaining_gaps` 与下一步需要的用户决策。

**Checkpoint**：最终目标已达成，或已形成明确硬阻塞证据。

---

### Step 11: Repair Loop

**GATE**：任一前序 Step / Gate 失败，或结果异常但根因未明。

**Goal**：诊断失败原因、修复、复验，并回到串行 workflow。

Execution rules:

- 先定位失败 Step / Gate 与最近一次有效输入，不把后续 Step 的失败误归因给当前步骤。
- 提取可验证证据：错误日志、检查信息、翻译信息、仿真异常、KPI 偏差、布局缺失、端口/参数文档。
- 分类根因：需求不清 / 库映射错误 / 类或端口不存在 / 连接器类型不匹配 / 参数缺失或量纲错误 / 图解语义缺失 / 检查失败 / 翻译失败 / 仿真失败 / KPI 未达标 / 工具调用失败。
- 直接修复仅限于根因明确的局部问题；同一失败点连续 3 轮仍未通过时，停止继续改完整模型，转为文档核对、组件级最小模型、分层隔离或工具调用最小验证。
- 修复后必须重新加载或强制重载受影响模型，并从失败 Step / Gate 开始复验；如果修复影响了前置 Gate（例如连接、参数、图解语义），必须回退到相应前置 Step。
- 不允许为通过检查、翻译或仿真而删除用户要求的关键拓扑、关键组件或关键 KPI；确需替换或简化时，必须证明原方案不可行并获得用户确认。
- 只有遇到必须用户决策的硬阻塞时才暂停：例如用户目标互相冲突、必要参数无法假设、改变用户指定拓扑、商业库缺失、Sysplorer 工具不可用。

**Checkpoint**：失败 Step / Gate 已修复并通过；返回串行 workflow 的对应下一 Step。

> **调用次数目标**：在仍满足 ⛔ 门禁的前提下，尽量压缩 **「检查（可能含布局后复验）→ 翻译/仿真 / KPI / 示图」** 的调用次数；**不得**为省调用而把 Gate 6 挪到「首轮仿真之后」当唯一主序。

## 建模加速规则

**规则 A: 跳过踏脚石模型** — 建模前必读 quickref，直接构建目标系统模型。仅在 quickref 未覆盖且 `get_lib_model_document` / 端口探测仍不足以确定连接器、或需最小化复现编译错误时才用踏脚石。

**规则 B: 预热 .mol 库** — **Modelica 物理**：TY/TA 私有库首次加载 10-30s，写代码前并行 `load_library`。`LoadLibrary` 返回 False 不等于失败，用 `check_model` 验证。**Sysblock**：优先预热 **`SysplorerEmbeddedCoder`**（及任务依赖），勿用 TY 物理库顶替块图库。**混合**：同时预热控制器块图库和物理 plant 所需库。

## 关键技术要点

- **MSL 版本**：`4.0.0.TY.1`。`uses()` 必须写 `Modelica(version = "4.0.0.TY.1")`，写 `"4.0.0"` 会加载失败
- **`when` 块**：同一 discrete 变量用 `when ... elsewhen ...` 单块，避免多块冲突
- **simMode**：`0`=自动（默认）、`1`=独立、`2`=实时
- **仿真结果**：`Result.msr`，路径 `C:\Users\<用户>\Documents\MWORKS\Simulation\<模型名>\Result.msr`

## 速查指针

→ **`private_lib_quickref.md`**（由工作区/部署随附，路径以实际工程为准）：§1 域→库映射、§2 inner 声明、§3 参数差异、§4 连接器类型、§5 典型拓扑、§8 KPI 变量名

→ **Sysplorer 实时文档（非 RAG）**：已加载库类说明 / 端口 / 参数用 `get_lib_model_document`；Python 建模 API（`call_code` 的 `run_script` 模式 / ModelingPy）用 `get_api_document`。
