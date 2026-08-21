# MoSim 全图形化 Sysblock 建模与组合平台规范

> 状态：目标架构与迁移准入规范。
>
> 范围：当前 48 个活动条目，即 47 个 MWORKS Control Profile 与 `px4ctrl`
> 工程/部署基线。本文定义后续模型迁移、Model Studio 组装和评审展示的硬约束；
> 不把目录、静态图或当前源面记录写成任何控制器的仿真、部署或飞行通过结论。

> **当前源树覆盖（2026-08-21）**：本文后文的旧目标目录图仅用于解释迁移约束，
> 不再作为当前文件位置或恢复指令。当前入口以 `Models/README.md` 为准：控制核心
> 在 `Control/<family>/<controller>/`，单机 Runner 在
> `Experiment/SingleUav/<family>/`，顶层同名族目录是兼容壳；`Experiment/Runners`
> 不属于活动包树，禁止从归档恢复。

## 1. 目标

评审者在 MWORKS/Sysplorer 中打开任何已晋级的整机入口时，必须能逐层展开到真正
参与运算的控制器图形网络。控制律不得依赖可切换文字、空白占位框、图片、未接线
装饰，或把核心算法藏在项目自定义的文本方程、`CFunction`、`EquationBridge` 中。

本目标不等于“仓库中没有文本文件”。Modelica 保存格式、标准块的内部实现和共享
多体 Plant 的物理方程仍然存在。约束对象是**项目拥有的控制律核心**：它必须由可审查
的原生 Sysblock/批准的基础图形块组成，并能在 GUI 中递归展开。

`OfficialPidFormalRunner` 和各路线现有 FormalRunner 保留为数值回归基线。它们不能
替代严格图形入口，也不得因图形迁移而被修改、删除或重新解释。

## 2. 严格图形化定义

一个控制器只有同时满足以下条件，才可标为 `strict_graphical_sysblock`：

1. 核心类带有 MWORKS `SysblockVersion` 和 `BlockSystem` 元数据；根图及递归子图可在
   MWORKS GUI 中打开，并以人工证据确认控制器节点不能切换到“文本”视图。源码文件
   的存在、类名和元数据本身不能替代这一 GUI 判据。
2. 项目控制律由显式端口、原生基础块、状态块、矩阵/逻辑块和 `connect` 连线构成。
   所有控制计算路径从公开输入端口或参数进入，到公开输出端口结束。
3. `equation` 区只允许连接拓扑、端口别名、监测量和 Plant/物理边界的必要声明；
   不允许在严格核心中以手写方程计算控制律。
4. 严格核心及其递归控制子图不得实例化项目自定义 `CFunction`、`EquationBridge`、
   `external` 函数或等价的黑盒算法块。它们可作为历史 Formal 基线、诊断对照或
   明确标记的非严格路线存在，但不得进入严格核心的执行路径。
5. 每个图形实例都必须拥有真实类、可见端口和实际连线。图片、文本标签和未接线
   图标不计入模型结构；空白 Diagram、缺失类、悬空端口和只含外壳的子模型一律失败。
   整机入口可受控继承已审查的图形 Runner，但派生类必须显式声明该继承关系，并在
   SG-0 同时检查派生源和基类源；基类必须包含共享 Plant、控制器实例及完整连接，
   且 GUI 必须从派生类实际打开复核。不能以未检查的祖先或只含名称的壳类补足此项。
6. 共享 `Sunray150Assembly` 是唯一整机 Plant；控制器迁移不得复制 Plant、执行器
   动力学或使用视觉壳替代真实动力学。
7. 旧图形候选不能仅凭类名、端口或增益相同而复用。迁移审计必须逐项映射 Formal
   核的状态演化、微分或滤波、限幅、抗饱和、复位、采样时间和输出符号。未经 SG-3
   验证，直接增益不得替代微分支路，离散积分不得替代连续或抗饱和积分路径，省略的
   约束也不得视为等价。若批准图形原语无法保持这些语义，路线必须保留明确例外分类。

标准库块可以被使用，但必须在图形中可见、接口可追溯且不绕开上述约束。对分数阶、
完整优化求解、神经网络推理等算法，若批准基础块不能无损表达其语义，则该路线应保持
`transparent_function_backed` 或 `research_only`，不得伪称为严格图形化。

## 3. 评审与晋级门

每条路线都必须按顺序通过下列门。后门失败不能由前门通过抵消。

| 门 | 必须证明的事实 | 失败示例 |
| --- | --- | --- |
| SG-0 源面 | 类、包注册、元数据、端口、连接和禁用黑盒依赖符合严格核心规则；使用 `Scripts/mworks/check_strict_graphical_sysblock_surface.py` | `CFunction` 被包在图形外壳内 |
| SG-1 GUI 展开 | 整机、控制器、关键子模块均能原生打开，且没有空白 Diagram、缺失类或假连线；控制器节点的“文本”入口不可用或不存在 | 顶层有图，点进控制器后为空或可切换文本 |
| SG-2 人工图审 | 输入、状态、限幅、分配、输出与每一条控制信号可读且可追溯 | 只画算法名称或用图片代替逻辑 |
| SG-3 行为等价 | 与不变的 Formal 基线在同一输入、参数、求解器和 Plant 下比较关键输出 | 图形模型可检查但改变了控制律 |
| SG-4 整机运行 | `CheckModel`、有界仿真、原生 `Result.msr`、位置/姿态/电机曲线和三维动画均存在 | 只有固定输入探针或静态截图 |
| SG-5 发布边界 | 记录模型哈希、参数 Profile、场景、截图、原始数据、指标和声明上限 | 用另一控制器或历史结果替代当前路线 |

SG-1 证明评委可查看真实图形，SG-3 和 SG-4 才证明该图形确实执行并形成对应整机
结果。任何 UI 截图、静态扫描或代码生成记录均不能单独越级。

## 4. 模型与文件归类

迁移不进行批量移动或删除。现有目录、包名、FormalRunner 和历史证据均保持可读取；
每完成一条路线才以 package-aware 的方式迁移其项目拥有的严格图形核心，并更新唯一
Registry 映射。

目标源树如下：

```text
Models/MoSimQuadrotorModel/
  Control/
    Implementations/
      Graphical/
        Common/                 # 受审计的基础图形模块
        PID/
        ProjectOwned/           # px4ctrl、AWFF、L1、INDI、项目 MPC/分配等
        LinearRobust/
        NonlinearAdaptive/
        SlidingMode/
        GeometricFlatness/
        Optimization/
        Learning/
    Adapters/                   # 只做公开接口、单位、坐标系和采样转换
    Bridges/                    # Formal/非严格对照，不可被严格核心依赖
  Experiment/Runners/
    Formal/                     # 不变的数值回归基线
    Golden/                     # Official PID 等可展示基准入口
    Graphical/                  # 通过 SG-0 至 SG-4 的其它整机入口
  Experiment/Scenarios/         # 只放场景和故障，不复制控制器核心
```

每条迁移路线至少拥有一个 package、一个严格核心、一个接口 Adapter、一个整机入口和
一个机器可读映射记录。文件名使用稳定的 `ProfileId`/`scheme_id`，不以“new”、
“final”、日期或截图用途命名。`package.mo`、`package.order`、类全名、Registry 和
引用入口必须在同一变更中校验。禁止用多个同名副本承载不同控制律。

## 5. Model Studio 自动组合

APP 的自由组合不是切换说明文字，也不是为所有组合复制模型。它必须执行以下流程：

```text
选择完整 Profile 或受控候选
  -> Registry 解析名义控制器、允许的增强/安全/分配槽位与输出边界
  -> 类型、单位、坐标系、采样周期、复位语义和 Plant owner 校验
  -> 生成一次性整机 wrapper 与参数快照
  -> 打开该 wrapper 中真实实例化的图形核心
  -> 记录哈希、场景与结果
```

生成器只能编排模型实例、连接和参数绑定；不得生成或替换控制律文本。若组合没有已批准
的接口映射、严格核心或整机入口，APP 必须显示阻断原因，不能退化为只改名称的示意图。
用户改变控制器或参数后必须生成新的 wrapper/manifest 并重新走 SG-0 至 SG-4；同一份
`Result.msr` 永远只归属一个配置快照。

标准 UI 以完整 Profile 为主。高级模式只能组合 Registry 明确允许的槽位，不允许将
47 个 MWORKS Profile 与增强、安全、场景做无约束笛卡尔积。

## 6. 实施顺序

### 波次 0：共同基础

1. 建立严格核心静态检查、GUI 展开清单、禁止依赖清单和证据包合同。
2. 建立 `Graphical/Common` 的受审计原语库与 Adapter/Runner 生成接口。
3. 将 Registry 增加每条路线的 `graphical_tier`、严格核心类、整机入口、GUI 审阅状态
   和 Formal 等价状态；未登记即不可在 APP 中宣称严格图形化。

### 波次 1：Golden PID

1. 新建完全由图形块构成的 `OfficialPidCoreSysblock`，替代 Golden 入口对既有文本
   PID 核的执行依赖。
2. 保持 `OfficialPidFormalRunner` 与 `OfficialPIDRotorAdapter` 不变，使用相同
   `Sunray150Assembly`、轨迹、参数和求解器比较位置、姿态、四路命令与转速。
3. Golden PID 通过 SG-0 至 SG-4 后，才作为后续路线的目录、图审和等价模板。

### 波次 2：项目拥有控制器

按输出边界和复用关系处理：`px4ctrl`，AWFF PID/ESO，L1 残差，INDI，线性 MPC，
故障补偿与在线分配。每条均先拆出一个唯一严格核心，再通过 Adapter 进入共享 Plant。
QP/NMPC 安全投影仅在固定维度、固定迭代的原生图形语义得到验证后晋级；不得把
“QP/NMPC-style”称为完整通用 QP/NMPC 求解器。

### 波次 3：低至中等复杂度

按 `PID 与智能 PID`、`线性与鲁棒状态反馈`、`滑模`、`非线性与自适应`、
`几何与微分平坦` 的顺序迁移。每条路线先把固定常量输入改成公开的真实输入端口，
再接 Adapter、整机 Runner 与 Formal 对照；不得因已有固定输入图而跳过整机门。

### 波次 4：高复杂度与显式例外

最后评估 MPC/NMPC/MPPI/iLQR、分数阶和学习路线。每条先进行“批准基础块是否保持原
算法语义”的能力审计：可等价表达才进入严格图形化；否则保留透明函数对照并明确其
非严格等级或研究状态。禁止用简化算法继续使用原 Profile 名称。

## 7. 完成判定与声明规则

“48 条完成”只在每个活动条目都有：严格核心或明确例外分类、非空的整机图形入口、
SG-0 至 SG-4 记录、模型/参数/场景哈希及当前结果包时成立。不能由历史目录数量、
固定输入探针、图标数量、截图或相邻控制器的结果推断完成。

评审展示顺序固定为：Profile 配置快照 -> 整机图 -> 控制器递归展开 -> Formal 对照
说明 -> 当前运行的曲线、动画和指标。展示中不隐藏 Formula/Function-backed 路线；
它们必须被明确标记为非严格，而不是通过文本切换伪装为 Sysblock。

## 8. 当前起点

当前 Golden PID **不是**本规范的通过模板。`OfficialPidCoreSysblock` 只是继承
`Vehicle.Blocks.Controller.Controller` 的 Modelica 控制器图并添加 Sysblock 元数据；
原控制律仍位于可切换文本的基类中，因此它不能通过严格 SG-0。此前的
`OfficialPIDGraphicalRotorAdapter`、`OfficialPidSingleUavGoldenRunner`、Formal 对照、
`Result.msr` 与曲线证明的是一个可运行的 Modelica 图形闭环，不证明原生 Sysblock
控制器已经接入整机。

原生 `OfficialPidNativeSysblockCore` 已用 `SysplorerEmbeddedCoder` 的端口、数学、连续
状态和饱和块重建原 Official PID 的位置环、姿态环与四路混控，但当前项目文件仍是手写
源面：它有 74 条 `connect` 而没有 `annotation(Line)`，已被严格源面门禁拒绝。由官方
API 回读的临时模型在 `Results/mworks_live_gate/native_sysblock_modelica_embedding_20260805/`
中具备可见 `Line`，但尚未落入项目 PID 包，也尚未通过 SG-1 的 GUI 人工验收。

此前的桥接阻断包记录了原生 Sysblock 展平到共享 Modelica Plant 时的端口解析失败。源码
探针后来加入了 `__MWORKS(SECInstance=true)` 路径，但没有在当前有效 MWORKS 许可证和
GUI 门禁下重新验证，因此组合能力仍为 `unverified`。Golden PID 以及后续 47 条路线
继续保持未晋级状态；不能用元数据包装、静态截图或历史数值结果跨过 SG-0 至 SG-4。
