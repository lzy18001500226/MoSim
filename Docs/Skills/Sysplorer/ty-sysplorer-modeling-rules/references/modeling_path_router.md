# 建模路径分流规则（Modelica 物理模型 / Sysblock 框图 / 混合建模）

> **用户原话已明确要求 Sysblock、框图、方框图、Embedded Coder、SysplorerEmbeddedCoder，或以 `run_script` / ModelingPy 做程序化建块图**（与 §1.2 同义）时：立即锁定 **§1.2 → §3**；**禁止**再执行 §0，禁止把 `TYHydraulics` 等物理库当主路径，禁止按**液压/机械等 Modelica 物理建模范式**写物理 `connect()` 拓扑。
>
> **用户明确要求混合建模/混合仿真、物理模型加 Sysblock 控制器、物理 plant + Sysblock controller、在 Modelica 顶层嵌入 Sysblock 子模型**时：锁定 **§1.3 → §4**。混合建模不是把两套范式混写在同一层；必须先完成/检查 Sysblock 子模型，再在 Modelica 物理顶层实例化并连接它。普通 `AddComponent` 同层混放被拒绝时，不要误判为混合模型整体不受支持；应检查是否存在或需要插入 Sysplorer 识别的 SEC 实例（常见标记 `__MWORKS(SECInstance=true)`）。
>
> 当用户意图为**搭建、编辑模型**且**未**出现上述强信号时，须**先按 §1** 完成 **Modelica 物理模型**、**Sysblock 框图** 与 **混合建模** 路径判别（不确定则按 §1.4 向用户确认），再执行对应分支规范。**不要**在未判别前混用两套流程。

### 路径约定（MCP 打包 exe 时必读）

- **查阅文档**：`resources/` 语料默认在 **MCP 部署目录（exe 同目录）** 下，由 `get_resources_root` / `MCP_RESOURCES_DIR` 决定，**不是**建模输出目录。
- **建模产物**：`.mo`、`src/`、`private_lib/` 等必须落在 **工作区根**（`MCP_WORKSPACE_DIR` 或 `--workspace-dir`，未设置时 frozen 下为启动 MCP 时的 **当前工作目录**）。**勿**写到 exe 目录。
- **Sysplorer 工作目录与会话安全**：凡在 Sysplorer 侧新建/保存到磁盘、或路径相对于 Sysplorer「当前目录」解析时，须先通过 API **`GetDirectory()`** 确认当前目录，并将新建文件与目录建在该目录下（或基于该路径的显式绝对路径）。**禁止**调用 **`ClearAll`**（会清空已加载库、翻译缓存、结果等，破坏用户环境）、**`ChangeDirectory`** 或以其它方式修改 Sysplorer 工作目录；卸载模型/类时使用 MCP **`model_manager`**（`unload`，底层 `EraseClasses`）等细粒度接口。需要固定落盘位置时使用绝对路径（含 MCP 工作区根），不要依赖「先改目录再写相对路径」。
- 不确定时查看 `session_manager(action="health")` 返回 JSON 中 `paths.workspace_root` 与 `paths.resources_root`。

---

## 分流顺序（硬性）

1. **先做 §1**。若用户表述或任务书出现 **§1.3** 中的混合信号，**直接走 §4**；混合路径内部再分别执行 Sysblock 子模型规则与 Modelica 物理顶层规则。
2. 若用户表述或任务书出现 **§1.2** 中的强信号（如 Sysblock、框图、方框图、信号流、Embedded Coder、SysplorerEmbeddedCoder、**以 `run_script` / ModelingPy 程序化建块图**、`NewModel(..., restriction="Sysblock")` 等），且目标不是物理顶层混合模型，**直接走 §3**，**跳过 §0**。
3. **仅当已确定走 §1.1（Modelica 物理模型）** 时，再执行 **§0**，随后走 **§2**。
4. **禁止**在 Sysblock 任务上套用 §0 的结论去装配 **TY/TA 物理库**、手写整页 **`connect()` 液压/多体拓扑**，或**以 `SetModelText` / `setmodeltext` 做任何形式的文本建模**（整段或片段覆写均不允许）；Sysblock **须全程**用 **Sysplorer 官方建模 API**（`run_script` / ModelingPy，`get_api_document` 核对），详见 **`sysblock_style_guide.md`**「文本建模禁令与官方 API 全流程」。
5. **混合路径例外只限边界实例化**：允许在 Modelica 物理顶层 `.mo` 中实例化已完成的 Sysblock 模型，并通过其 `Inport` / `Outport` 暴露端口与 `Modelica.Blocks.Interfaces.*` 或物理模型信号端口连接；这不允许手写 Sysblock 内部拓扑，也不允许在 Sysblock 模型内嵌入物理组件。
6. **不要把同层 `AddComponent` 限制扩大化**：若直接向 Sysblock 模型插入 TY 物理组件、或向普通 Modelica 物理模型直接插入 `SysplorerEmbeddedCoder` 基础块失败，只能说明普通同层混放路径不成立。混合建模的可行路径是已封装 Sysblock 模型作为 SEC 实例嵌入物理顶层；若顶层已有该实例，先查询端口并继续接线、检查、翻译、仿真；若没有，不要硬插基础块，应使用受支持的 SEC 实例插入流程或请用户提供已插入实例。

---

## 0. 同元内置库优先预判（仅 §1.1 Modelica 物理路径）

> **适用范围**：已进入 **§1.1 Modelica 物理模型** 分支、且意图为**搭建或扩展**该路径下的模型（尚未定组件清单或尚未定稿 `.mo`）时执行本节。**已进入 §1.2 Sysblock 的不要执行 §0。** 本节用自然语言做关键词提取与同元库匹配，避免默认用纯 MSL 或手写方程「重造」已有商业库能力。

### 0.1 从用户表述中提取什么

从用户原话中抽取（中英同义均可）并简要记下：

- **物理域**：液压 / 气动 / 热液压 / 机械多体 / 热 / 电气 / 流体 / 传动等  
- **部件与现象**：缸、泵、阀、管路、关节、连杆、齿轮、电机、换热器、冷却、介质（油/气）等  
- **建模形态线索**：是否强调传递函数、离散控制、纯信号链（可能与 §1.2 Sysblock 重叠，需与路径判别结合）

### 0.2 能否优先用同元内置库（判断规则）

1. **查域→库映射**：对照工作区随附的 **`private_lib_quickref.md` §1（域→库）**，将 §0.1 的关键词映射到 **TY / TA 等同元商业库** 包名。  
2. **查本工程可用类**：读工作区 **`private_lib/MetaDataLib.json`**，按关键词缩小候选 **`fqname`**；对候选类 **`load_library`（若未加载）+ `get_lib_model_document(full_class_name)`** 确认说明与端口是否覆盖用户需求。  
3. **语料补强（按需）**：映射或类名仍不确定时，对 **`commercial_library`** 或 `resources_manifest.json` 中登记的**域相关补充语料**（如 `modeling_skill_*` 类 **`corpus_id`**，以清单为准）做 **`resources_retrieval`**，**不要**仅凭记忆臆造包名或类名。

**结论**（仅对 §1.1 有效）：若 §0.2 表明存在**合理覆盖**的同元库组件 → **必须优先采用**（与 **Gate 1: Library First** 在 Modelica 物理分支中的含义一致）；仅在用户明确要求自建 / 教学极简方程 / 已验证库中无可用类时，再退回到 MSL 或自写方程。

### 0.3 关键词→域的快捷提示（非穷尽，以 quickref 为准）

| 用户表述中的典型词 | 优先想到的同元库方向（示例） |
|-------------------|------------------------------|
| 液压、油缸、伺服阀、节流、溢流、换向阀、油箱 | `TYHydraulics`，含热效应时 `TYThermalHydraulics` |
| 气动、气缸、气阀、压缩空气 | `TYPneumatics` |
| 多体、关节、连杆、刚体、约束、齿轮箱（机械拓扑） | `TYMultibody` 等（以 quickref §1 与 `MetaDataLib.json` 为准） |
| 换热器、冷却回路、热网络（与流体耦合） | 热流体 / 热相关 TY 库（见 quickref） |
| 纯控制、PID、方框图、状态空间、离散传递函数 | 倾向 §1.2 **Sysblock** 或 `Modelica.Blocks`；与物理库预判并行考虑 |

完成 **§1** 后：若走 **§1.3** → 执行 **§4**；若走 **§1.2** → 执行 **§3**；若走 **§1.1** → 须完成 **§0** 再进入 **§2**。进入 **§2** 或 **§4 的物理顶层阶段**后，组件清单与 `uses()` 须体现 §0 的结论（优先同元库，而非默认 MSL）。

---

## 1. 判别流程

### 1.1 Modelica 物理模型（连续/多物理域方程与连接器）

优先归为此类，当用户明确涉及：

- `.mo` 文本模型、`package` / `model` / `equation` / `connect()`、物理连接器（电气、热、流体、多体等）
- 私有库 / MSL 组件、参数与单位、DAE 与仿真工况在 Modelica 层配置

### 1.2 Sysblock 框图模型（SysplorerEmbeddedCoder 块图）

归为此类，当用户明确涉及：

- **Sysblock**、**框图**、**方框图**、**信号流**、**Embedded Coder**、**SysplorerEmbeddedCoder**
- 用 **Python / ModelingPy（或 Sysblock API）** 在工具里**程序化建图、改块、设参数**，或 **`run_script` + `NewModel(..., restriction="Sysblock")`**，而非手写 **Modelica 物理** `.mo` 拓扑（`connect()` 物理连接器等）

### 1.3 混合建模（Modelica 物理顶层 + Sysblock 子模型）

归为此类，当用户明确涉及：

- **混合建模**、**混合仿真**、**Sysplorer 与 Sysblock 混合**、物理模型中嵌入/调用 Sysblock 控制器或算法
- **物理 plant / 机械臂 / Buck 电路 / 热控对象** 与 **Sysblock 控制策略 / PID / 状态机 / 离散传递函数 / 代码生成控制器** 联调
- 顶层模型需要同时含物理组件和一个或多个已封装的 Sysblock 模型实例，由 `Inport` / `Outport` 映射出的信号端口完成连接

混合路径的结构是：**Sysblock 子模型内部仍是 Sysblock 路径**，**物理顶层仍是 Modelica 物理路径**。当前规则只支持**物理模型内嵌套已搭建完成的 Sysblock 模型**；不支持 Sysblock 模型内嵌套物理模型，也不支持在同一模型层直接混放物理组件与 Sysblock 基础块。

注意：这里的“同一模型层直接混放”指普通组件插入/基础块混插路径，不等于否定 SEC 实例嵌入。若物理顶层中已存在带 `__MWORKS(SECInstance=true)` 语义的 Sysblock 控制器实例，应将其视为受支持的混合边界实例，继续用其暴露的 `Inport` / `Outport` 映射端口完成顶层连接。

### 1.4 不确定时

**必须**向用户确认一句：目标是否为 **Sysblock 框图（基于 SysplorerEmbeddedCoder）**、**传统 Modelica 物理模型（.mo）**，还是 **物理顶层 + Sysblock 控制器/算法的混合模型**。

---

## 2. Modelica 物理模型分支

1. **必读**：**`modelica_style_guide.md`**（本 skill `references/`；RAG 仍用 `corpus_id=modeling_rules` 检索同目录四文）。
2. **执行**：按 `seven_gates_workflow.md` 中的 **7 Gates**、编译驱动开发、testbench、KPI；多组件 / 多 **`connect()`** 模型在逻辑完成后须执行 **Smart Layout**（`smart_layout`，`mode=writeback_mo`，`graph_json`，见 Gate 6），随后 **`model_manager`**（`action=export_model_diagram`，别名 `export_diagram`；底层 `ExportDiagram`）导出原理图并做 **视觉验收与迭代修复**（见 Gate 6 后续）。
3. **检索补充**：组件选型前须已完成 **§0 同元内置库优先预判**（本节仅 §1.1）。在此基础上先查工作区 **`private_lib/MetaDataLib.json`** 定候选 **`fqname`**；对已安装 **库模型类** 的说明、参数与端口，调用 **`get_lib_model_document(full_class_name)`**（经 Sysplorer `ClassExist` / `LoadLibrary` / `ExportDocumentation`）；辅以商业库语料 RAG 等。**不要**再从 `resources/` 翻 Markdown 代替 Sysplorer 导出的类文档。

---

## 3. Sysblock 框图模型分支

**库约束**：在必须使用 Sysplorer 块图库的前提下，**默认模型库为 `SysplorerEmbeddedCoder`**（任务书另行指定其他库时除外）。

**系统库名字符串**：Sysblock 框图依赖的**系统库**顶层包名**固定为 `SysplorerEmbeddedCoder`**。所有需要传「库名」的操作（脚本内 `LoadLibrary`、**`load_library`** 等）**必须**使用 **`SysplorerEmbeddedCoder`**，**不要**误用 **`Sysblock`**（后者仅用于 `NewModel` 的 **`restriction="Sysblock"`**，表示块图模型类型，**不是**库名）。详见 `sysblock_style_guide.md` 文首「系统库名称（硬性约定）」。

1. **必读**：**`sysblock_style_guide.md`**（本 skill `references/`；**Run Script 前 Sysplorer 必须已启动且驱动已连接**；**禁止 `SetModelText` 文本建模，全程官方 API**；**编写脚本前先完成组件/布局/连线/参数设计**；`NewModel(restriction="Sysblock")`、新建/编辑脚本分离、package 级 `parent`、以 **`check_model` 成功**为建图循环结束条件、仿真与 Modelica 共用 MCP 工具链）。
2. **执行**：下文 3.1–3.4 与本文档表格中的语料路径；Run Script 细节以 `sysblock_style_guide.md` 为准。

### 3.1 查阅资料（RAG）

| 目的 | 操作 |
|------|------|
| **具体模块怎么用**（功能说明、端口、参数语义、示例、子库索引） | 对 **`resources/SysblockModelLibrary/`** 语料检索：`resources_retrieval(action="corpora", corpus_id="sysblock_model_library")` 取解析路径，再 `action="search", query=..., sources=<上述路径>, index_path="resources/indexes/sysblock_model_library_index.json", rebuild_index=按需)`；可按块名或子库关键词（如 `Continuous`、`PIDController`）检索，各子目录下的 `*_Main.md` 为该类模块总览 |
| **库模型类文档**（Modelica 全名类的说明、参数、端口等，含 `SysplorerEmbeddedCoder.*` 等已加载库） | 调用 **`get_lib_model_document(full_class_name)`**（Sysplorer `ClassExist` → 必要时 `LoadLibrary` → `ExportDocumentation`）；**不要**用 `resources/SysplorerAPI/` 下的 Markdown 代替从 Sysplorer 导出的类文档 |
| API 用法、函数名、调用顺序（`call_code` 的 `run_script` 模式 / ModelingPy） | 调用 **`get_api_document(api_function_name)`**（官方 `Help(cmd)`）；**不要**再用 `resources/SysplorerAPI/` 语料检索代替本工具 |
| 各块**参数合法名称**（API 键名） | 若随包存在，直接打开 **`resources/SysplorerAPI/SysblockParameters.md`**（**非 RAG**，未列入 `resources_manifest.json`）；**与上表配合**：块级语义与端口以 `sysblock_model_library` 与/或 `get_lib_model_document` 为准；脚本 API 细节可 **`get_api_document`** 核对 |

说明：`sysblock_model_library` **未**列入 `resources_manifest.json` 的 `default_sources`，默认合并检索不会扫模块库全文；查块用法时**必须**显式传入该语料的 `sources`（及建议的专用 `index_path`），避免与默认索引混淆。

### 3.2 编写建模脚本

- **先读** `sysblock_style_guide.md`：**文本建模禁令**（**禁止** **`SetModelText` / `setmodeltext`**；**全程**仅允许 **Sysplorer 官方建模 API**）、**Part 0**（调用 `run_script` 模式前 **`session_manager(action="health")` / `ensure` 等确保就绪**）、**Part 1**（**先设计** `SysplorerEmbeddedCoder` 组件清单、布局、连线表、参数表，**再写脚本**）、**新建脚本 / 编辑脚本分离**、**`NewModel(..., restriction="Sysblock")`**、**`parent` 传父包全名**、循环结束以 **`check_model` 成功**为准。
- 使用 **`get_api_document`** 核对的 **Sysplorer 官方 Python / ModelingPy 建模接口**生成或修改框图；**不得**用文本覆写替代块图操作。
- 块类型、参数名须与 **`SysplorerEmbeddedCoder.*`** 及 `SysblockParameters.md` 一致，避免臆造。

### 3.3 运行与调试循环（RunScript）

0. **大前提**：调用 **`call_code`**（`mode="run_script"`）**之前**，须已通过 **`session_manager(action="health")`**（或等价步骤）确认 **Sysplorer 已启动且 `driver_ready`**；失败时依次 **`action="ensure"`**、**`action="restart"`**（必要时 **`restart_mode="full_reset"`**）等，详见 `sysblock_style_guide.md` Part 0 与 `seven_gates_workflow.md` 中「AI 自主执行闭环」Step 0。
1. 调用 MCP 工具 **`call_code`**，`mode="run_script"`，`payload` 含 `python_source` 或 `script_path`（与当前 Sysplorer 会话同进程；路径白名单同旧约定）。
2. 根据返回 JSON 中的 **`stdout` / `stderr` / `exception` / `traceback`** 以及可选的全局返回值 **`RUN_SCRIPT_RESULT`** 修改脚本。
3. **重复**「`run_script` 调用 → 修脚本」直到 **`ok` 为 true** 且无未处理异常（必要时先 `session_manager` 做 health/ensure/restart）。
4. **建图阶段结束**：在脚本侧稳定后，还须 **`check_model`（或 `call_code` 的 `fast_workflow` 模式中的检查）通过**，才算完成 Sysblock 建图—编辑循环；详见 `sysblock_style_guide.md` Part 5。

说明：部署若设置环境变量 **`MWORKS_RUN_SCRIPT_DISABLED=1`**，`run_script` 模式会拒绝执行。

### 3.4 后续仿真（与 Modelica 统一）

脚本侧建图/编译通过后，**仿真、扫参、读结果、KPI** 等环节回到与 Modelica 项目相同的 MCP 工具链（例如 `check_model`、`simulate_model`、`call_code`（`mode="fast_workflow"`）、`result_manager` 等，按任务选用），**不再单独搞一套仿真规范**。

---

## 4. 混合建模分支

**必读**：**`hybrid_modeling_workflow.md`**，并按子模型类型分别读取 **`sysblock_style_guide.md`**、**`modelica_style_guide.md`**、**`modelica_diagram_connect_semantics.md`** 与 **`seven_gates_workflow.md`**。

### 4.1 执行顺序（硬性）

1. **定义边界**：先列出物理模型与控制器/算法之间交换的信号、类型、维度、采样周期与变量名。Sysblock 侧用 `Inport` / `Outport` 暴露边界；物理侧用 `Modelica.Blocks.Interfaces.RealInput/RealOutput`、`IntegerInput/IntegerOutput`、Bus 或结构一致连接器承接。
2. **先完成 Sysblock 子模型**：按 **§3** 与 `sysblock_style_guide.md` 用 `call_code(mode="run_script")` / ModelingPy 官方 API 新建或编辑 Sysblock 模型，禁止 `SetModelText`。子模型必须先 `check_model` 通过。
3. **再完成物理 plant / 顶层**：按 **§0 + §2** 选择物理库并以纯文本 `.mo` 编写物理对象和顶层 wrapper。顶层可实例化已完成的 Sysblock 模型；该实例通常应保留 Sysplorer 产生的 Sysblock 实例语义（样例中为 `__MWORKS(SECInstance=true)`）。
4. **确认 SEC 实例边界**：若顶层已有 Sysblock/SEC 实例，先用模型内省读取组件与端口，确认端口名、方向、类型和维度；若没有该实例，不要用普通同层 `AddComponent` 强插 Sysblock 基础块，应使用受支持的混合实例插入流程或让用户提供已插入实例。
5. **连接边界端口**：在物理顶层用普通 Modelica `connect()` 连接 Sysblock 实例暴露出的 `Inport` / `Outport` 映射端口与物理信号端口；这些 `connect()` 必须带合格 `Line` 图解注解。
6. **分层检查**：先检查 Sysblock 子模型，再检查物理 plant（如独立存在），最后检查混合顶层模型。顶层通过后，Gate 6 对顶层 `.mo` 做图解语义/布局验收；写回有变化则再 `check_model`。
7. **只仿真顶层混合模型**：联调仿真应面向物理顶层/混合顶层模型；结果变量可使用嵌套路径，如 `controller.gain.y`、`plant.y`、`controller.outport`。

### 4.2 类型与结构约束

- `float` / `double` 映射到物理侧 `Real`；整数类映射到 `Integer`；`Bus` 只连接到结构一致的连接器。
- 连接两端数据维度与长度必须一致；需要数组分量时，在物理侧或框图侧显式选择分量。
- 物理建模环境中的 `BusCreator` / `BusSelector` 类型与维度通常需手动设置，不能依赖自动猜测。
- Sysblock 子模型可以位于物理顶层或物理子系统内；禁止反向在 Sysblock 模型内嵌物理模型。

### 4.3 参考样例（本地 Sysplorer 安装）

- 快速入门：`Docs/Sysblock/Samples/Sysblock/SysblockQuickStart/HybridSimulation/Model_TC.mo` 与 `Model_Mix_TC.mo`。
- Buck 控制：`Docs/Sysblock/Samples/Sysblock/ApplicationCase/Demo_BuckCircuit/Buck_Contrl/`，关注 `Buck_ctrl*.mo`、`SynchronousBuck_new*.mo`、`top_model.mo`。
- 机械臂控制：`Docs/Sysblock/Samples/Sysblock/ApplicationCase/Demo_RobotArm/Default5/`，关注 `NewRobot/Control/robot_Ctrl.mo` 与 `NewRobot/NewRobot_main.mo`。

---

## 5. 语料与清单对应

| 路径 | 说明 |
|------|------|
| `modeling_skills/ty-sysplorer-modeling-rules/references/modeling_path_router.md` | 本文（分流 + Sysblock + 混合流程） |
| `modeling_skills/ty-sysplorer-modeling-rules/references/modelica_style_guide.md` | Modelica 分支完整规范 |
| `modeling_skills/ty-sysplorer-modeling-rules/references/modelica_diagram_connect_semantics.md` | 组件/连接图解 `annotation` 语法与语义（`Placement`、`Line` 等），供纯文本与 `graph_json` / `smart_layout` 协同 |
| `modeling_skills/ty-sysplorer-modeling-rules/references/sysblock_style_guide.md` | Sysblock 分支 Run Script / ModelingPy 脚本规范 |
| `modeling_skills/ty-sysplorer-modeling-rules/references/hybrid_modeling_workflow.md` | Modelica 物理顶层嵌入 Sysblock 子模型的混合建模工作流 |
| `modeling_skills/ty-sysplorer-modeling-rules/references/seven_gates_workflow.md` | 7 Gates 与执行闭环 |
| `SysplorerAPI/`（磁盘可选） | **未**编入 RAG 索引；示例 Markdown 仅人工查阅；**API 说明**以 **`get_api_document`** 为准 |
| `SysplorerAPI/SysblockParameters.md`（磁盘可选） | Sysblock 参数名速查（非 RAG） |
| `resources/private_lib/`（磁盘可选） | **未**编入 RAG；工程内私有库与元数据在工作区 **`private_lib/`**，读 **`MetaDataLib.json`** 并用 **`get_lib_model_document(fqname)`** 核对类文档 |
| `SysblockModelLibrary/` | Sysblock 各子库**模块说明文档**（用法、端口、参数释义、示例）；RAG 语料 id：`sysblock_model_library`，索引文件：`indexes/sysblock_model_library_index.json` |

在 `resources_manifest.json` 中，**`modeling_rules`** 语料目录已指向本 skill 的 **`references/`**（含 **Modelica 风格 / 分流 / 七门闸 / Sysblock / `modelica_diagram_connect_semantics` 等** 规范 Markdown 多篇）。**`design_opt_mpe_api`** 等其它类别路径与 `corpus_id` 以清单内登记为准。其余 RAG 类别除 **`sysblock_model_library`**、**`cad_toolbox_api`**、**`simulink_importer_api`**、**`commercial_library`** 外，另含若干 **`modeling_skill_*`** 补充语料（见清单内 `resource_categories` 与 `corpus_id`）。`default_sources` **不含** `sysblock_model_library` 与各 `modeling_skill_*`，需查块说明或**按任务域**补强检索时，须按 §3.1 / 任务需要显式指定 `corpus_id` 或 `sources` 与索引。**`SysplorerAPI/`** 与 **`resources/private_lib/`** 已从清单与索引中移除；**类级文档**用 **`get_lib_model_document`**，**API 帮助**用 **`get_api_document`**，**私有库候选与 fqname** 来自工作区 **`private_lib/MetaDataLib.json`**（无 MCP 元数据检索工具）。
