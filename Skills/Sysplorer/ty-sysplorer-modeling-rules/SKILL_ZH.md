> 本文件仅用于中文审核参考，实际任务执行请调用 SKILL.md

# Sysplorer 建模必须遵守的规范（原路径分流与总规则）

## 必须遵守的要点

- **加载本 Skill（与 `SKILL.md` 的 `description` 一致）**：只要用户表达需**新建/搭建模型**，典型如「搭建模型」「搭一个」「建一个」「仿一个」及同类从零建模、新建模型再仿真等需求，**都要加载本 Skill** 并遵守下文规则；若用户要求 **Sysplorer + Sysblock 混合建模/混合仿真**（物理顶层嵌入已完成 Sysblock 控制器/算法模型），同样必须加载。
- 用户要**建模或改模型**时，**必须**在执行前按本 Skill 的 **`references/`** 与 **七门闸** 行事：范式判别、路径约定、**`get_lib_model_document` / `resources_retrieval` / `smart_layout`** 等工具分工均**不可跳过**。**工作路径**仅允许 **Agent 当前目录** 或 **`GetDirectory` 返回值**（见下节「建模工作路径」），**禁止**用 **MCP 程序 `main.py` 相关路径** 作为用户工程根。
- **Modelica 物理、纯文本建模**：`.mo` 中图解侧元数据（**`Placement`**、**`connect` 的 `Line` 等**、**`Icon` / `Diagram` 图元**）**必须**按 **`references/modelica_diagram_connect_semantics.md`** 与 **`modelica_style_guide.md` Part 3** 的语法与语义写全，作为后续 **`graph_json` / `smart_layout` 自动布局与布线** 的输入；**禁止**只有方程与裸 `connect` 而无合格图形层。
- **Modelica 物理：检查通过后的图解语义与智能布局（必须执行）** — **`check_model` 成功之后**、**`translate` / 首次长仿真之前**，**必须**根据 **`references/modelica_diagram_connect_semantics.md`** 审阅当前 **`.mo` 文本** 是否已包含**组件与连线的图形语义层**（例如实例的 **`Placement`**、**`connect` 上可供管线解析的 `Line` / 走线** 等；不仅是方程与无图解信息的裸 `connect`）。**若未添加或明显不足以作为 `graph_json` / 布局管线的输入**，**应首先**用 **`smart_layout`（智能布局）** 按 **`references/seven_gates_workflow.md` Gate 6** 落盘（如 **`writeback_mo` + `auto_layout=true`**，配合 `modelica_code`、`graph_json` / `graph_json_path`、`model_output_path` 等），**将图解语义补全或修正**；**若写回后 `.mo` 有变，须再次** `check_model` **至通过**。**然后再** 进入翻译/仿真与后续门闸。禁止在缺图解语义时跳过智能布局、直接把「仅拓扑先写上」的 `.mo` 当作图面已闭环。

### Modelica 物理：自动布局在流程中的位置（与 Gate 6 一致）

1. 写完/改完 `.mo` → **`check_model` 至通过**（Gate 3）。  
2. **立刻**对照 **`modelica_diagram_connect_semantics.md`** 判断：`.mo` 里是否已有**合格**的组件 **`Placement`** 与 `connect` 的图解侧注解（**`Line` 等**），足以驱动 **`smart_layout` / `graph_json`**。  
3. **若否** → **先** **`smart_layout`** 智能布局写回；写回后 **再** `check`（如适用）→ 再 **`translate` / 长仿真** 等。  
4. **若是**（已具备合格图形层）→ 仍按 Gate 6 在仿真前完成约定的布局/定稿（含必要时 `smart_layout`），见 **`seven_gates_workflow.md`**。
- 若未明确是 **Modelica 物理**、**Sysblock 框图** 还是 **混合建模**，**必须先**按 **`references/modeling_path_router.md`** 完成分流，再按本包 **`references/`** 中对应分支规范执行（含 **`modelica_style_guide.md`**、**`sysblock_style_guide.md`**、**`hybrid_modeling_workflow.md`** 等）。

## 判别要点

1. 出现 **Sysblock / 框图 / Embedded Coder / 程序化建块图** 等强信号：**走 Sysblock 分支**，按 **`modeling_path_router.md` §3** 与 **`sysblock_style_guide.md`** 执行；**禁止**再按 TY 物理库写 **`connect()`** 液压/机械拓扑。
2. 出现 **混合建模 / 混合仿真 / 物理 plant + Sysblock controller / 物理顶层嵌入 Sysblock** 等信号：**走混合分支**，按 **`modeling_path_router.md` §4** 与 **`hybrid_modeling_workflow.md`** 执行；先完成/检查 Sysblock 子模型，再写 Modelica 物理顶层。
3. **Modelica 物理**：先库优先预判（见 **`references/modeling_path_router.md` §0**），再 **`modelica_style_guide.md`**、**`modelica_diagram_connect_semantics.md`**、**`seven_gates_workflow.md`**。
4. **不确定**：向用户确认一句范式。

## 建模工作路径（必须遵守）

**所有**与建模相关、依赖文件系统路径的操作（读/写用户模型、脚本、导入导出目标等），**仅允许**使用以下两类路径来源（按优先级）；**禁止**把 MCP 服务端程序所在目录当作用户工程或默认工作区。

| 优先级 | 来源 | 说明 |
|--------|------|------|
| **1 — 最高** | **Agent 当前运行路径（工作目录）** | 当前会话/Agent 所报告的 CWD，作为本任务中相对路径、新建文件、当前工程解析的**默认基准**；建模产出应优先落在此类路径下。 |
| **2 — 次优** | **`GetDirectory`（MCP 返回）** | 当必须从工具链获得与 Sysplorer 或工程对齐的目录时，**仅**使用 **`GetDirectory`**（或服务器提供的等效目录工具）**返回**的路径。 |
| **禁止** | **MCP 程序运行路径（`main.py` 相关）** | **禁止**以 MCP 服务端**入口/安装/源码树**为建模或默认读写根路径：例如含 **`main.py`** 的目录、仅用于启动服务的 Python 包根、仅用于跑服务的 **`site-packages` 安装**、**仅用于启动 MCP 的仓库检出路径** 等。不得默认在该树内读写用户模型或项目产出。 |

**原因**：用户资产必须落在用户或 Agent 工作区，与服务端程序目录分离，避免误写代码树、权限与版本控制问题。

## 全局禁令

### 强制实现方式（必须遵守）

- **Modelica 物理模型**：**必须**以**纯文本直接编写 `.mo` 文件**（或直接写入等效源码文本）。**禁止**以 **call code** / 程序化 API 作为主要或唯一手段来搭建物理 Modelica 模型（禁止 API 优先或仅 API 的物理建模路径）。
- **Sysblock 框图建模**：**必须**通过 **call code** API（如 `run_script` / ModelingPy 等，见 **`references/sysblock_style_guide.md`**）建块与连线。**禁止**用**写/改 `.mo` 文本**的方式做 Sysblock 框图拓扑（含 **`SetModelText`** 或手写框图侧 `.mo`）。
- **混合建模**：Sysblock 子模型仍按 Sysblock 规则用官方 API 搭建；物理顶层仍按 Modelica 规则写 `.mo`。允许在物理顶层实例化已完成 Sysblock 模型并连接其 `Inport` / `Outport` 映射端口；这不是手写 Sysblock 拓扑或在 Sysblock 内嵌物理模型的许可。
- **混合平台边界**：不要把普通 `AddComponent` 同层插入失败总结成“Sysplorer 不支持混合模型”。实际边界是：同一个普通模型层直接混放 `SysplorerEmbeddedCoder` 基础块和 TY/Modelica 物理组件可能被拒绝；但已完成的 Sysblock 模型可以作为物理顶层中的 SEC 实例嵌入，常见形态保留 `__MWORKS(SECInstance=true)`。若顶层已有该实例，应读取其暴露端口并继续自动连接、检查、翻译、仿真；若没有，不要硬插基础块，应走受支持的 SEC 实例插入流程或让用户先提供已插入实例。

- **禁止** **`ClearAll`**、**`ChangeDirectory`**。
- Sysblock：**禁止** **`SetModelText`** 做拓扑；须用官方 API（见 **`references/sysblock_style_guide.md`**）（与上节 **强制实现方式** 一致）。
- 大块语料用 **`resources_retrieval`**，勿在会话开头全文扫描 `resources/`。

## 附录

**`references/`** 含范式与门禁等**必须遵守的**规范全文（含 **`modelica_diagram_connect_semantics.md`**：`connect`/Placement/Line 图解语义，以及 **`hybrid_modeling_workflow.md`**：混合建模工作流）及 **`sysblock-library-index.md`**；RAG 中对应 **`corpus_id=modeling_rules`**。七步闭环中：在 **`check` 成功之后**，**先**核对 `.mo` 是否已按 **`modelica_diagram_connect_semantics.md`** 具备图解语义；**若缺，须先用 `smart_layout`（智能布局）补全**，再继续后续步骤。智能布局须排在**翻译/长仿真之前**（见 **`seven_gates_workflow.md` Gate 6**），**不能**以「先仿真、后布局」为唯一主流程。
