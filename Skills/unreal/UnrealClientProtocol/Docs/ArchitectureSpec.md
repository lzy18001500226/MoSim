# UCP 架构规范

本文档定义 UnrealClientProtocol 的核心设计原则与架构约束。所有新功能的开发必须遵守这些原则——如果一个设计违反了其中任何一条，说明方向错了。

## 核心哲学

**不替 Agent 做决策，给它能力。**

UCP 的定位不是"自动化工具"，而是"能力协议"。它不预设 Agent 能做什么、该怎么做，而是把引擎的原子能力暴露出来，信任 Agent 自身对 UE 的理解来组合这些能力。

## 设计原则

### 原则 1：反射驱动，不硬编码

**规则：** 能通过 UE 反射系统（UFunction / UPROPERTY / UClass）解决的问题，不写特化代码。

**原因：** 硬编码意味着每新增一种类型就要改 C++ 代码。反射驱动意味着引擎自身的扩展（新的类、新的函数）自动对 Agent 可用，无需改动 UCP。

**检查方法：** 问自己——"如果引擎新增了一个 XXX 类/函数，UCP 不改代码能支持吗？"如果答案是否，说明设计过于特化。

**例外：** 当 UE 反射系统本身不提供区分手段时（例如布局属性和逻辑属性在反射层面没有任何标记区别），允许有限的显式列表。但这些列表必须集中管理，不分散在各处。

**现有案例：**
- 协议层：`call` 命令通过反射调用任意 UFunction——零特化
- 属性读写：`SetObjectProperty` / `GetObjectProperty` 通过反射操作任意 UPROPERTY——零特化
- 类名解析：统一的 `FNodeCodeClassCache` 单例通过 `RegisterBaseClass` + `GetDerivedClasses` 自动发现所有蓝图节点类、材质表达式类、Widget 类、Niagara 节点类——零特化
- Skip 属性列表：集中在 `NodeCodePropertyUtils` 的共享静态 set 中（EdGraphNode / MaterialExpression / Widget / NiagaraNode）——受限的例外
- UFunction 参数自动转换：`FUCPParamConverter` 自动将字符串路径解析为 UObject 指针——UFunction 的参数应直接声明为 UObject 指针类型，不应在函数内部手动 `LoadObject`

### 原则 2：注册式扩展，不改核心代码

**规则：** 新增对某类节点/属性/图类型的支持时，通过注册机制插入，不修改已有的核心逻辑。

**原因：** 核心代码是所有图类型共享的基础设施。每次为特定类型改核心代码，都在增加所有类型的维护负担和回归风险。

**检查方法：** 问自己——"我是在改一个通用的 for 循环，还是在注册一个特定类型的处理器？"如果是前者，考虑抽取为注册式。

**现有案例：**
- `INodeCodeSectionHandler` 注册表：新增图类型只需注册新 handler，不改 `NodeCodeEditingLibrary`。Niagara 通过注册 `FNiagaraSectionHandler` 接入，核心层零修改
- `IBlueprintNodeEncoder` 注册表：新增蓝图节点语义编码只需注册 encoder，不改 Serializer/Differ
- `INiagaraNodeEncoder` 注册表：Niagara 领域内部的节点编码器，模式与蓝图完全一致
- `IMaterialPropertyHandler` 注册表：新增材质特殊属性处理只需注册 handler，不改 Differ

### 原则 3：特化逻辑的归属边界

**规则：** 特化逻辑放在它所属的领域 handler 内部，不上浮到核心层。

**原因：** 蓝图的语义编码（`CallFunction:PrintString`）是蓝图特有的概念，材质不需要。材质的 `FExpressionInput` 连接模型是材质特有的，蓝图用的是 `UEdGraphPin`。如果把这些特化放到核心层，核心层就变成了"所有领域特殊情况的集合"，违背了分层原则。

**检查方法：** 问自己——"这个接口的参数类型是通用的（`UObject*`、`FString`）还是领域特有的（`UEdGraphNode*`、`UMaterialExpression*`）？"如果是后者，它属于领域 handler 内部，不属于核心层。

**现有案例：**
- `IBlueprintNodeEncoder`：参数是 `UEdGraphNode*`、`UBlueprint*`——放在蓝图 handler 内部
- `IMaterialPropertyHandler`：参数是 `UMaterialExpression*`——放在材质 handler 内部
- `INodeCodeSectionHandler`：参数是 `UObject*`、`FString`——放在核心层（通用）

### 原则 4：Section = 物理隔离的图

**规则：** NodeCode 的 Section 必须对应物理隔离的数据边界。不对同一份数据做虚拟切片。

**原因：** 虚拟切片（例如按材质输出引脚分 Scope）会导致同一个节点出现在多个 Section 中。当 Agent 在某个 Section 中删除了这个节点，其他 Section 的引用会断裂——这是一个架构层面的 bug，不是实现层面的 bug。

**检查方法：** 问自己——"一个节点/对象能同时属于两个 Section 吗？"如果答案是能，说明 Section 划分错了。

**现有案例：**
- 蓝图：每个 `UEdGraph` 是一个 Section（EventGraph / Function / Macro），节点物理隔离——正确
- 材质：`[Material]` = 完整主图，`[Composite:Name]` = 子图，节点不跨 Section——正确
- Widget Blueprint：`[WidgetTree]` = 完整 widget 层级树，与图表 Section（EventGraph/Function）物理隔离——正确
- Niagara：按 `ENiagaraScriptUsage` 切分 Section（`[ParticleSpawn]`、`[EmitterUpdate]` 等），虽然多个 Usage 共享同一个物理 `UNiagaraGraph`，但节点不跨 Usage 链共享，通过 `BuildTraversal(Usage)` 提取——**正确，物理隔离在逻辑层面成立**
- Niagara 旧方案：一个 GraphSource = 一个 Section（整图读写），Agent 一次看到所有阶段的所有节点——**可行但粒度过粗，已改为按 Usage 切分**
- 材质旧设计：按输出引脚分 Scope，TextureSample 同时出现在 BaseColor 和 Roughness——**错误，已废弃**

### 原则 5：读写语义对称

**规则：** ReadGraph 返回的文本直接可以用于 WriteGraph，不需要 Agent 做格式转换。读什么范围就写什么范围，范围内是完整覆写，范围外不动。

**原因：** Agent 的工作流是 Read → 修改 → Write。如果读出来的格式和写回去的格式不同，Agent 要做额外的格式转换，增加出错概率。如果写的范围和读的范围不一致，Agent 要推理"我的修改会影响哪些我没读到的东西"，这超出了 Agent 的可靠推理范围。

**检查方法：** 拿 ReadGraph 的原样输出直接喂给 WriteGraph，结果应该是零变更（diff 为空）。

### 原则 6：属性值用宽松 JSON

**规则：** 属性值的序列化/反序列化采用"宽松 JSON"策略——先尝试 JSON 解析，失败则 fallback 到 UE 原生 `ImportText`。

**原因：**
- JSON 是 LLM 训练数据中最多的结构化格式，生成准确率最高
- UE 的 `ImportText` 格式（`(X=1.0,Y=2.0,Z=3.0)`）LLM 也能生成，但不如 JSON 稳定
- 两者兼容意味着 Agent 可以选择最自然的方式写，不需要记两套格式规则

**检查方法：** 序列化输出使用 `FNodeCodePropertyUtils::FormatPropertyValue`（偏向 JSON 格式），反序列化使用 `SetObjectProperty` 的逻辑（JSON 优先，fallback ImportText）。

### 原则 7：GUID 是节点身份的唯一可靠标识

**规则：** 增量 diff 的节点匹配以 GUID 为第一优先级。GUID 丢失时的 fallback 匹配（ClassName + 属性指纹、ClassName alone）是尽力而为，不保证正确。

**原因：** 同类型的多个节点（两个 `Multiply`、两个 `CallFunction:PrintString`）在 GUID 丢失后无法可靠区分。这不是实现 bug，而是信息丢失的必然后果。

**对 Skill 的要求：** Skill 必须强调"保留 GUID 是 Agent 的核心职责"。Agent 在修改 NodeCode 时必须保持已有节点的 `#guid` 不变。

### 原则 8：事务安全

**规则：** 所有写操作必须包裹在 `FScopedTransaction` 中，确保 Undo/Redo 可用。

**原因：** Agent 可能犯错。用户必须能一键撤销 Agent 的任何操作。如果写操作不在事务中，撤销行为不完整，用户会丢失信任。

## 架构层次

```
┌─────────────────────────────────────────────────┐
│                   Agent (LLM)                   │
│         读 SKILL.md → 构建 JSON → 调用          │
├─────────────────────────────────────────────────┤
│                  Skills 层                       │
│  SKILL.md 文件描述协议格式和领域知识              │
├─────────────────────────────────────────────────┤
│                  API 层                          │
│  UNodeCodeEditingLibrary  (Outline/Read/Write)  │
│  UObjectOperationLibrary  (Get/Set/Describe)    │
│  UAssetEditorOperationLibrary                   │
│  UNiagaraOperationLibrary (Niagara 结构操作)     │
├─────────────────────────────────────────────────┤
│               Handler 注册表                     │
│  FNodeCodeSectionHandlerRegistry                │
│    ├─ FBlueprintSectionHandler                  │
│    │    ├─ IBlueprintNodeEncoder 注册表          │
│    │    └─ 蓝图 Serializer / Differ             │
│    ├─ FMaterialSectionHandler                   │
│    │    ├─ IMaterialPropertyHandler 注册表       │
│    │    └─ 材质 Serializer / Differ             │
│    ├─ FWidgetTreeSectionHandler                 │
│    │    └─ WidgetTreeSerializer                 │
│    └─ FNiagaraSectionHandler                    │
│         ├─ INiagaraNodeEncoder 注册表            │
│         ├─ Niagara Serializer / Differ          │
│         └─ → UNiagaraOperationLibrary (写回)     │
├─────────────────────────────────────────────────┤
│             NodeCode 核心层                      │
│  NodeCodeTypes (IR 结构)                        │
│  NodeCodeTextFormat (文本 ↔ IR)                 │
│  NodeCodePropertyUtils (属性过滤/格式化)         │
│  NodeCodeClassCache (统一类名缓存/多基类注册)      │
├─────────────────────────────────────────────────┤
│             公共工具层                           │
│  UCPJsonUtils (JSON 序列化/对象加载)              │
├─────────────────────────────────────────────────┤
│              协议传输层                          │
│  FUCPServer (TCP)                               │
│  FUCPRequestHandler (JSON → call → JSON)        │
│  FUCPFunctionInvoker (反射调用)                  │
│  FUCPParamConverter (JSON ↔ UPROPERTY)          │
└─────────────────────────────────────────────────┘
```

### 各层职责

| 层 | 职责 | 不应做的事 |
|----|------|-----------|
| 协议传输层 | TCP 监听、JSON 解析、反射调用、日志捕获 | 不应知道蓝图/材质的存在 |
| 公共工具层 | JSON 序列化、对象加载等跨模块共享的工具函数 | 不应包含业务逻辑 |
| NodeCode 核心层 | IR 结构定义、文本格式解析/序列化、属性过滤、类名缓存 | 不应包含蓝图/材质/Niagara 的特化逻辑 |
| Handler 注册表 | Section 类型路由、handler 生命周期管理 | 不应包含具体的序列化/diff 逻辑 |
| 领域 Handler | 特定图类型的序列化、diff、节点创建、连接管理 | 不应修改核心层代码 |
| 领域 OperationLibrary | 封装引擎内部 API 为 UFunction，同时服务于 Handler 内部调用和 Agent 直接调用 | 不应包含序列化/diff 逻辑 |
| API 层 | UFunction 暴露、参数验证、handler 分发 | 不应包含业务逻辑 |
| Skills 层 | 协议格式描述、工作流指导、领域知识 | 不应包含需要编译的逻辑 |

## 扩展新图类型的检查清单

当需要支持新的图类型（如 Niagara、AnimBP、Widget）时，按以下清单检查：

### 1. Section 模型设计

- [ ] 确认图的物理隔离边界——每个 Section 对应一个独立的 `UEdGraph` 或等价的数据容器
- [ ] 确认没有跨 Section 共享节点的情况
- [ ] 确定 Section Type 名（如 `NiagaraEmitter`）和 Name 来源（如 `ParticleSpawn`）
- [ ] 确定是否需要 `[Properties]` 或 `[Variables]` 等数据 Section

### 2. 节点编码

- [ ] 节点类名是否自描述？如果每种节点类型有唯一的 UClass，直接用类名（像材质）
- [ ] 如果同一个 UClass 表示多种语义（像蓝图的 `UK2Node_CallFunction`），需要注册领域内部的 encoder
- [ ] encoder 放在领域 handler 内部，不放核心层

### 3. 属性序列化

- [ ] 使用 `FNodeCodePropertyUtils::ShouldSkipProperty` 做第一层过滤
- [ ] 如果需要额外的 skip set，继承 `GetEdGraphNodeSkipSet()` 或创建新的共享 set，放在 `NodeCodePropertyUtils` 中
- [ ] 如果有特殊属性（内嵌连接指针、动态数组等），注册领域内部的 property handler

### 4. 连接模型

- [ ] 确认连接是 pin-based（`UEdGraphPin`）还是 expression-based（`FExpressionInput`）
- [ ] pin-based 的图可以直接复用蓝图 Differ 的连接逻辑
- [ ] expression-based 需要在领域 Differ 中实现

### 5. 后处理

- [ ] 写操作后需要哪些后处理？（重编译、relayout、刷新编辑器 UI）
- [ ] 所有后处理在领域 handler 的 `Write()` 内部完成

### 6. 数据可达性审计

- [ ] 哪些数据在 UObject 的一级 UPROPERTY 上？（反射可达，不需要 Section）
- [ ] 哪些数据在嵌套 USTRUCT 上？（反射不可达，需要 Properties Section 封装）
- [ ] 哪些数据是编译产物？（需要调用引擎 API 提取，通过只读 Section 暴露）
- [ ] 哪些数据在 `FParameterStore` 等特殊容器中？（需要专用 API）
- [ ] 子对象（渲染器、模拟阶段等）是 UObject 吗？（如果是，反射可达其详细属性）

### 7. 操作复杂度评估

- [ ] 哪些操作是简单属性赋值？（Properties Section 写回即可）
- [ ] 哪些操作需要调用复杂内部 API？（需要 OperationLibrary 封装）
- [ ] OperationLibrary 的函数参数应直接声明为 UObject 指针类型，利用 UCP 的自动参数转换
- [ ] 如果 Differ 也需要调用这些操作，OperationLibrary 应设计为可被 Differ 内部调用

### 8. 集成

- [ ] 创建 `INodeCodeSectionHandler` 实现
- [ ] 在 `NodeCodeEditingLibrary.cpp` 的自动注册块中注册
- [ ] Build.cs 中添加所需的模块依赖
- [ ] 创建 `Skills/unreal-<domain>-editing/SKILL.md`
- [ ] 如需 OperationLibrary，创建领域专属的 `U<Domain>OperationLibrary`
- [ ] 公共工具函数使用 `UCPJsonUtils.h`，不重复定义

### 9. 自检

- [ ] 新代码中没有修改核心层的任何文件（`NodeCodePropertyUtils` 的 skip set 除外）
- [ ] 特化接口的参数类型是领域特有的，不是通用的
- [ ] ReadGraph 的输出直接喂给 WriteGraph 产生零变更
- [ ] 所有写操作在 `FScopedTransaction` 内
- [ ] UFunction 参数使用 UObject 指针类型，不手动 `LoadObject`
- [ ] 没有重复定义 `JsonObjectToString` 等工具函数

## 新模式（Niagara 实现中发现）

### 模式 1：OperationLibrary 双重角色

**场景：** 当引擎子系统（如 Niagara）的核心操作不是简单的属性赋值，而是需要调用复杂的内部 API（创建图节点、管理参数存储、触发重编译等）时。

**模式：** 创建领域专属的 `OperationLibrary`（如 `UNiagaraOperationLibrary`），它同时服务于两个调用方：
1. **Handler/Differ 内部调用** — `WriteGraph` 解析 diff 后调用 OperationLibrary 执行变更
2. **Agent 直接调用** — 作为 UFunction 暴露，Agent 通过 UCP `call` 使用

**检查方法：** 如果某个操作只在 Differ 中使用，不需要暴露为 UFunction；如果 Agent 需要直接做这个操作（而不是通过 ReadGraph/WriteGraph），则暴露为 UFunction。

**现有案例：** `UNiagaraOperationLibrary` 的 `AddModule` / `SetModuleInputValue` / `GetModules` 等——Agent 可以直接调用管理模块栈，Differ 也可以调用来执行图变更。

### 模式 2：Properties Section 替代反射不可达的数据

**场景：** 当数据存储在 USTRUCT 嵌套结构中（如 `FVersionedNiagaraEmitterData` 在 `UNiagaraEmitter::VersionData[0]` 上），而 `GetObjectProperty` 只支持 UObject 的一级属性名，无法通过路径访问嵌套结构成员时。

**模式：** 在 NodeCode 的 Properties Section（如 `[EmitterProperties]`）中，由 Serializer 内部通过 C++ 代码访问嵌套结构成员，序列化为键值对文本。WriteGraph 时由 Handler 内部解析键值对并写回嵌套结构。

**检查方法：** 如果 `GetObjectProperty(path, "PropertyName")` 能直接访问，不需要 Properties Section；如果需要路径表达式（如 `VersionData[0].SimTarget`）才能访问，应通过 Properties Section 封装。

**现有案例：**
- `[EmitterProperties]`：SimTarget、bLocalSpace、FixedBounds 等在 `FVersionedNiagaraEmitterData` 上
- `[ParticleAttributes]`：编译产物，需要调用 `GatherCompiledParticleAttributes()`
- `[UserParameters]`：在 `FNiagaraUserRedirectionParameterStore` 上，需要特殊 API
- 对比：渲染器的详细属性（Material 等）在 `UNiagaraRendererProperties`（UObject）上，反射可达，不需要 Properties Section

### 模式 3：分层按需展开

**场景：** 当资产包含大量嵌套子对象（如 System 内嵌多个 Emitter，每个 Emitter 有多个阶段），一次性展开所有 Section 会导致信息过载。

**模式：** 父资产的 Outline 只列出自身的 Section + 子对象引用（ObjectPath），Agent 通过子对象的 ObjectPath 再调用 Outline 按需展开。

**现有案例：** System 的 `[Emitters]` Section 提供每个内嵌 Emitter 的 ObjectPath，Agent 用该路径调用 `Outline` 获取 Emitter 自己的 Section 列表，而不是在 System 的 Outline 中列出所有 Emitter 的所有 Section。

### 模式 4：逻辑隔离等价于物理隔离

**场景：** 当多个 Section 共享同一个物理数据容器（如 Niagara 的一个 `UNiagaraGraph` 包含多个 `UNiagaraNodeOutput`），但节点实际上不跨 Section 共享时。

**规则扩展：** 原则 4（Section = 物理隔离的图）可以放宽为"逻辑隔离等价于物理隔离"——只要能证明没有节点同时属于两个 Section，就可以用逻辑切分（如 `BuildTraversal(Usage)`）替代物理隔离。

**检查方法：** 验证引擎的节点添加 API 是否保证节点只连接到单一 Usage 链。Niagara 的 `AddScriptModuleToStack` 接受 `TargetOutputNode` 参数，模块只连入该 Output 的链条。

**风险：** Differ 写回时必须只操作目标 Usage 的节点，不能误删其他 Usage 的节点。实现方式是 Differ 的"旧 IR"也通过 `BuildTraversal` 生成，与 Read 对称。

## 反模式

以下是过去犯过的错误，未来必须避免：

| 反模式 | 描述 | 正确做法 |
|--------|------|---------|
| 虚拟切片 | 按材质输出引脚分 Scope，导致共享节点跨 Section | Section = 物理隔离边界（或可证明的逻辑隔离） |
| 核心层特化 | 把 `IBlueprintNodeEncoder` 放在 NodeCode 核心层 | 特化接口放领域 handler 内部 |
| if-else 链 | `if (ClassName.StartsWith("CallFunction:"))` 嵌入 Differ 主体 | 注册式 encoder/handler |
| 分散 skip 列表 | 每个 Serializer 维护自己的 skip 属性列表 | 集中在 `NodeCodePropertyUtils` 的共享 set |
| 直接赋值 pin 默认值 | `Pin->DefaultValue = Pair.Value` | 通过 `Schema::TrySetDefaultValue` 走类型分发 |
| 双向连接语法 | `>` 和 `<` 同时存在 | 只保留 `>` 方向，消除冗余 |
| WriteMode 参数 | 引入 merge/replace/delta 模式增加复杂度 | Section 粒度的 Read → Write 覆写，语义天然明确 |
| 手动加载对象 | 在 UFunction 内部 `StaticFindObject` / `StaticLoadObject` | UFunction 参数直接声明为 UObject 指针类型，UCP 的 `FUCPParamConverter` 自动解析路径 |
| 重复工具函数 | 每个 .cpp 文件各自定义 `JsonObjectToString`、加载对象的 static 函数 | 公共工具放 `UCPJsonUtils.h`，通过 `UCPUtils::` 命名空间调用 |
| 一次性铺开所有子对象 | System 的 Outline 列出所有 Emitter 的所有 Section | 分层按需展开——父对象暴露子对象 ObjectPath，Agent 按需 Outline |
