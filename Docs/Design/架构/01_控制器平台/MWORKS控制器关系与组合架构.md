# MWORKS控制器关系与组合架构

> 状态：当前控制关系和组合语义权威，2026-07-21。
>
> 本文回答“控制器在整机链路的哪个位置、能替换什么、如何组合、APP 当前实际能
> 配置和运行什么”。它以项目控制责任、`Model Studio` 源码和已登记 Profile 为准；
> APP 的控件名称不是架构层级的唯一来源。接口字段、Registry、验收门和逐路线证据
> 分别仍以 `控制平台接口与闭环实施规范.md`、
> `Config/control_platform/control_module_registry.json` 和 `控制器证据矩阵.md` 为准。

## 1. 先看一张关系图

MoSim 不是把 67 条路线平铺成 67 个可互换的“控制器”。固定的是飞机、状态、
参考和下游责任；可替换的是有明确输入输出合同的槽位。

```text
任务 / 轨迹 / 场景
  -> 单机原始参考 -----------------------------------------------------+
  -> 编队参考 (可选，多机状态 -> 每机参考)                            |
  -> 参考约束 (可选，如 Reference Governor)                           |
                                                                          v
状态 / 传感器 -> [位置 / 平动外环: 恰好一个] -> 期望姿态 + 总推力
  -> [普通增强/消融: 0..1；或控制方案内部的固定集成链]
  -> [命令安全: 一项已声明策略] -> [姿态/角速度 owner: 恰好一个]
                                                                          |
                                                                          v
                    [分配 owner: 由输出边界决定] -> [Adapter] -> 电机 -> 机体 / 传感器

故障侧链：扰动/故障注入 -> 执行器响应与健康 -> FDI -> 重构分配或安全动作
          它横向观察并干预上述链路，不是另一个并列的名义控制器。
```

这张图同时适用于 MWORKS 离线整机模型、MWORKS Live 和 ROS1/PX4 运行链。不同
后端的差异只能发生在已声明的 owner 和 Adapter，不能靠 UI 名称或模型文件名推断。

### 1.1 已冻结的方案数：49

报告和后续 Model Studio 只使用一个“完整控制方案”数字：**49**。机器可读权威是
`Config/control_platform/control_scheme_catalog.json`，由
`Scripts/quality/check_control_scheme_catalog.py` 固定校验。

| 组成 | 数量 | 计入原因 |
| --- | ---: | --- |
| 67 条证据矩阵中可独立承担名义控制职责的路线 | 43 | 每次运行恰好选择一条主跟踪控制律 |
| `px4ctrl` 工程基线 | 1 | 当前 ROS1/Sunray/PX4 主线需要单独可见，且不在 43 条比赛矩阵中 |
| 有固定顺序、接口、限幅、fallback 和源配置的集成链 | 5 | 每条链作为一个完整方案，而不是把其内部模块另行相乘 |
| 合计 | **49** | 唯一对外的方案数 |

五条固定集成链依次为：抗积分饱和与参考前馈 PID；该 PID 加 L1 启发式残差；该 PID
加 L1 残差与 INDI 姿态校正；线性 MPC 外环加 L1 残差与 INDI 姿态校正；QP/NMPC 外环
加 L1、INDI 与 CBF 风格安全投影（可见但数值门通过前禁用）。`MPC/NMPC` 是名义优化
外环家族，不是增强层复选框。通用 AWFF、L1、INDI、ADRC、ILC 等只用于受控消融或已
命名固定链；安全、故障、编队、规划、注入、分配器和 Adapter 都不作为乘法维度。

## 2. 槽位、替换边界与当前事实

| 责任槽位 | 运行中数量 | 输入 -> 输出 | 可替换边界 | 当前事实 |
| --- | ---: | --- | --- | --- |
| 任务/轨迹 | 1 | 场景、时间 -> `ReferenceFrame` | 更换任务、轨迹或规划器 | 不是控制器；APP 的地图、任务轨迹属于此处 |
| 编队参考 | 0..1 | 多机状态/编队目标 -> 每机 `ReferenceFrame` | 更换编队参考算法 | 只有多机才可启用；当前三机案例是固定规模领航-跟随参考，不等于分布式通信证明 |
| 参考约束 | 0..1 | 原始参考/约束 -> 受约束参考 | 如 Reference Governor | 逻辑上在名义控制器前；即使 Registry 将其归入 safety，也不能画到命令末端 |
| 位置/平动外环 | 恰好 1 | 状态、参考 -> `CommandFrame` | 替换主跟踪控制律 | PID、改进 PID、Linear MPC、fault compensation 等在当前 APP 中由此槽位选择 |
| 增强/扰动补偿 | 标准选择 0..1 | 状态、参考、候选命令 -> 修正项/命令 | 只能挂到模块声明的作用点 | AWFF、PID-INDI、L1 等不替代外环；多模块只允许作为已登记固定链内部结构，不能在标准 UI 任意叠加 |
| 命令安全 | 1 项已声明策略 | 参考或候选命令 -> 通过/修改/拒绝 | 参考侧或命令侧必须显式标注 | 当前已认证组合使用 `basic_limiter`；CBF 等待独立兼容和数值门 |
| 姿态/角速度内环 | 恰好 1 owner | 姿态误差/姿态参考 -> 角速度参考或力矩语义 | 可以由 MWORKS 模型或 PX4 后端拥有 | 离线预设使用“模型内部姿态/角速度环”；当前 Live 合同使用 PX4 内置姿态/角速度环 |
| 控制分配 | 由输出决定 | `WRENCH` -> `ROTOR_COMMAND` | WRENCH/ROTOR 路线必须声明 allocator owner | 当前离线预设标记 `px4_control_allocator`；不能据此推断已替换 ROS1/PX4 实时分配器 |
| Command Adapter | 恰好 1 | 类型化 `CommandFrame` -> 后端命令 | 只做语义、坐标、单位和时序映射 | 不得偷偷改变控制律 |
| 植物/传感器 | 1 | 电机命令 -> 状态/观测 | 后端或场景替换，不是控制器替换 | MWORKS 离线模型与 Gazebo/PX4 是不同证据层 |
| 故障管理侧链 | 0..1 管理策略 | 健康/响应 -> 事件、重构或安全动作 | 需同时具备注入、检测、隔离和响应合同 | 当前 APP 的“风扰/电机效率下降”首先是场景注入，不自动证明 FDI 或 FTC |

### 2.1 PX4 串联基线

评委应先理解 PX4 的串联控制链，再看 MoSim 的替换点：

```text
位置/速度参考
  -> 位置/平动外环
  -> 期望姿态 + 总推力
  -> 姿态环
  -> 角速度环
  -> 力矩/总推力
  -> 控制分配
  -> 四电机
  -> 四旋翼动力学
```

MoSim 当前最成熟的项目侧替换点是“位置/平动外环”。因此一个
`ATTITUDE_THRUST` 项目控制器的语义是“状态和参考 -> 期望姿态 + 物理总推力”，
不是“已经替换 PX4 所有内环和电机分配”。

## 3. 输出边界决定后端责任

| 输出边界 | 项目控制器负责到哪里 | PX4/后端仍负责什么 | 当前 APP/证据口径 |
| --- | --- | --- | --- |
| `ATTITUDE_THRUST` | 位置/平动跟踪、姿态和总推力指令生成 | PX4 姿态环、角速度环、分配和执行 | 当前唯一允许准备 Live 的单机合同；必须是 `official_pid` + PX4 inner + MAVROS attitude/thrust |
| `BODY_RATE_THRUST` | 角速度参考和总推力生成 | PX4 角速度环、分配和执行 | APP 可见为平台能力；当前不是 Live 可启动合同 |
| `WRENCH` | 力矩/总推力生成 | 已明确的 allocator、执行器后端 | 只有 allocator 和 Adapter 都被验证后才可运行，离线存在不等于 ROS1 可启动 |
| `ROTOR_COMMAND` | 离线整机链可包含完整到转子命令的控制链 | 取决于离线模型的内部 owner | 当前 MWORKS 认证预设的离线输出；不与 PX4 实时 owner 一一等同 |

任何报告都必须同时写出“模块名 + 输出边界 + 下游 owner”。例如：

```text
 official_pid (position/translation outer loop)
   -> ATTITUDE_THRUST
   -> PX4 built-in attitude/rate inner loops and allocator
```

## 3.1 模型库边界与入口

控制责任和文件位置必须同时说明。当前四个模型根目录不是四份相同模型，也不能
互相替代：

```text
Models/MoSimQuadrotorModel/
  正式项目包：Baseline、Controllers、Dynamics、ExperimentRunner、
  Formation、Missions、Planning、Robustness、System 等命名空间

Models/QuadrotorControllerBlocks/
  可复用 Sysblock/方程控制器源码；正式包的 Controllers 命名空间提供部分包装入口

Models/QuadrotorExperiments/
  现有场景和实现兼容池；许多已登记的闭环模型仍在这里，暂不能按目录名删除

Models/MworksLive/
  RT0/RT1 实时探针、桥接资源和遥测范围模型；不属于离线整机模型
```

离线 Profile 的推荐打开链路是：

```text
Model Studio
  -> MoSimQuadrotorModel.ExperimentRunner.Runners.*
  -> typed Adapter
  -> controller wrapper/source
  -> shared plant/result contract
```

当 Profile 仍绑定 `QuadrotorExperiments.*` 时，这表示“现有实现兼容”，不表示
迁移已经完成；当模型位于 `MworksLive.*` 时，只能作实时探针证据，不能当成离线
控制器或飞行闭环证据。

## 4. 当前 Model Studio 与统一目标

`apps/model_studio/src/app.jl` 当前仍使用“快速预设 / 自定义组合”和多个下拉框。
统一后的界面语义改为“主控制器选择 + 环路职责自动解析”。本节区分当前实现和
目标合同，避免把目标 UI 当成已经完成的代码。

当前实现核对（2026-07-21）：

```text
当前仍存在：ProfileDropDown、PositionDropDown、AttitudeDropDown、
AugmentationDropDown、SafetyDropDown、FaultDropDown、FormationDropDown、
OutputDropDown；OFFLINE_PROFILES 仍有 fault 字段。

因此当前 APP 仍是旧的多下拉候选配置界面，不是下面的“主控制器先选、
环路 owner 自动解析”实现。本文本轮只统一文档口径，未声称 APP 已完成改造。
```

APP 改造完成前，任何报告、截图或 agent 回报都必须使用“目标设计”与“当前实现”
两个标签；不能因为文档已经定义了目标交互，就宣称故障下拉已经删除或环路 owner
已经由 Registry 自动解析。

| UI 字段/目标控件 | 它映射的项目概念 | 不是什么 |
| --- | --- | --- |
| 主控制器 / 控制器方案 | 从 49 条完整方案中选择一个；内部 owner 与固定链由目录解析 | 不是所有环路的无条件总开关，也不是 43 x N 个任意组合 |
| UAV 数量、地图、任务轨迹 | 场景和参考来源 | 控制器槽位 |
| 位置环、速度环、姿态环、角速度环 | 从 Registry/Profile 解析出的职责 owner；默认禁用且只读 | 四个可以随意拼接的名义控制器 |
| 控制分配/输出边界 | 命令类型和下游 owner | 单纯的显示格式 |
| 内部固定链 / 受控消融 | 自动显示所选方案的固定内部模块；研究消融最多声明一个已兼容模块 | 可任意叠加的控制器列表 |
| 安全层 | 一项安全策略 | 一般轨迹跟踪控制器 |
| 场景扰动 / 故障注入 | 风扰、电机效率等实验条件；默认关闭但可见 | 已完成的 FDI/FTC/重构证明 |
| 编队控制层 | 0..1 编队参考生成器 | 每架机的电机级协同控制 |

当前 Registry 已提供 `kind`、`output_variant`、`backend_owner` 等字段，但还没有
完整的四环 owner 元数据。因此在补齐以下字段之前，APP 不得根据控制器名称自动
猜测职责：

```json
{
  "loop_ownership": {
    "position": "controller_or_backend_owner",
    "velocity": "controller_or_backend_owner",
    "attitude": "controller_or_backend_owner",
    "body_rate": "controller_or_backend_owner",
    "allocation": "controller_or_backend_owner"
  },
  "display_role": "nominal_controller|inner_controller|augmentation|safety|scenario_injection"
}
```

字段补齐前，文档只能使用源码、Adapter 和已冻结 Profile 的审计结论；不能把
`nominal_controller` 直接等同于“同时拥有位置、速度、姿态和角速度四个环路”。

统一目标中的标准页面顺序为：

```text
主控制器 / 控制器方案       [可选]
位置环                      [自动解析，只读/禁用]
速度环                      [自动解析，只读/禁用]
姿态环                      [自动解析，只读/禁用]
角速度环                    [自动解析，只读/禁用]
控制分配 / 输出边界          [自动解析，只读/禁用]
内部固定链 / 受控消融        [自动解析，只读；研究候选另走兼容性门]
安全约束                    [默认基础限幅]
场景扰动 / 故障注入          [可见，默认关闭]
编队参考                    [UAV 数量大于 1 时启用]
```

“只读/禁用”是有意的可见状态：用户仍能看到当前控制器到底负责哪一个环路，
但不会误以为可以把四个环路任意拼接。高级自由组合可以作为显式的高级模式，
开启后也必须通过 Registry、Adapter 和兼容性门禁。

标准控制链不再设置独立的“故障容错层”下拉框。已有故障管理源码和证据暂不删除，
但它们只能在明确声明 FDI、隔离、重构和安全动作合同的实验 Profile 中使用；普通
风扰/电机效率实验只进入“场景扰动 / 故障注入”侧栏，并且必须区分 requested 和
applied 值。

### 4.1 自定义组合、认证预设和可运行性是三件事

| 状态 | APP 当前实际行为 | 可作出的结论 |
| --- | --- | --- |
| 研究候选组合 | 标准 UI 不提供多增强复选；候选必须保存为显式配置并精确匹配已解析的 Registry/Adapter 链 | 只说明候选组合被描述，不能计入 49，也不能说明已仿真、已代码生成或可运行 |
| 认证/验证预设 | 选择预设会填充所有字段；只有字段仍与该预设完全匹配，离线 MIL 才可启动 | 该精确组合的认证记录可追溯；改任一字段即成为新候选 |
| 当前禁用预设 | `QP/NMPC Safety` 等候选仍可见禁用；场景注入控件也默认关闭 | 不能通过改名或换 UI 位置绕过门禁 |
| Live 可准备 | 还需连接预检和实时合同通过 | 当前只允许单机、无编队、`official_pid`、PX4 inner、`ATTITUDE_THRUST` 的 50 Hz 合同 |

因此，“APP 支持自由组合”的准确表述是：**可以记录受控研究候选，并由兼容性、预设
一致性和后端合同决定能否运行**；不是任意笛卡尔积，也不是标准 UI 的多增强选择。对外
方案数始终保持 49，候选只有在形成新的固定拓扑、源配置和独立证据后才可申请进入目录。

### 4.2 当前离线认证预设

以下是源码中已登记的离线预设，不是未来规划清单：

```text
Official PID 爬升                  改进 PID 爬升
AWFF 爬升                          PID-INDI 爬升
Linear MPC 爬升                    L1/AWFF 爬升
L1/AWFF 风扰                       故障补偿：电机 1 效率 85%
三机 Linear MPC 三角编队 8 字      Custom：改进 PID + 轻风扰
Custom：故障补偿 + 轻风扰          QP/NMPC Safety（当前禁用）
```

各单机/三机预设的实际字段组合以 `app.jl` 中 `OFFLINE_PROFILES` 为准；每一个预设都
必须能追溯到其 `profile` 和 `Results/mworks_generated_profiles/...` 证据目录。

## 5. 组合前的最小检查表

一个组合只有同时回答下面的问题，才允许进入验证：

1. 每个控制责任槽位是否只有一个明确 owner，外环是否恰好一个？
2. 参考、命令和输出边界是否类型、单位、坐标系、采样时间、复位语义一致？
3. 增强模块的作用点、顺序、限幅和 fallback 是否被声明？
4. 安全策略是限制参考还是限制候选命令，触发后做 pass/modify/reject 的哪一种？
5. 故障字段是“注入场景”还是已有 FDI/FTC 模块？若后者，检测和响应证据在哪里？
6. `ATTITUDE_THRUST`、`BODY_RATE_THRUST`、`WRENCH` 或 `ROTOR_COMMAND` 的下游
   owner 和 Adapter 是否已明确？
7. 该组合是仅可配置、已通过离线预设、还是已经满足当前 Live 合同？

以下做法一律无效：两个外环同时写同一命令；把 AWFF/L1/INDI 当成另一名义外环；
把故障注入当作容错闭环；把 MWORKS 动画当作 PX4/Gazebo 运行时成功；或用相邻
Profile 的结果提升新组合的证据等级。

## 6. 67 条路线怎样放进这张图

当前证据矩阵的 67 条路线按责任槽位归类如下：

| 类别 | 路线数 | 报告时的正确说法 |
| --- | ---: | --- |
| 名义控制 | 43 | 主跟踪控制候选；一次运行只选择一个 |
| 增强/补偿 | 12 | 挂接在明确名义控制器上的消融/补偿路线 |
| 姿态到角速度 | 1 | 姿态到角速度参考模块，不等于替换 PX4 角速度环 |
| 编队参考 | 9 | 多机参考生成；每架机仍需下游单机控制器 |
| 安全聚合 | 1 | 约束和 fallback 路线，按触发行为验收 |
| 故障聚合 | 1 | 故障管理路线，必须区分注入、检测、隔离和响应 |

矩阵的当前计数是 `accepted=27`、`executed_blocked=33`、`not_run=7`；其中
`65/67` 只是通过相应 codegen/SIL 门的路线数，不是 65 个同级且已接受的整机控制器。
具体状态、首个 blocker 和声明上限只在 `控制器证据矩阵.md` 与其 JSON 权威中维护。

因此 `67` 和 `49` 并不冲突：前者是覆盖名义控制、增强、安全、故障、编队等责任层的
证据矩阵，后者是让评委和 APP 能够选择、解释和比较的完整控制方案目录。

## 7. 文档分工与阅读顺序

为避免同一控制链在多份文件中反复改写，今后按下面分工维护：

| 需要回答的问题 | 唯一主入口 |
| --- | --- |
| 控制器在 PX4/MWORKS 链路的哪个位置、APP 字段如何映射、组合是否合法 | 本文 |
| Frame、Registry、参数冻结、Adapter、升级门 | `控制平台接口与闭环实施规范.md` |
| 67 条路线的证据状态、实验类型和报告声明上限 | `控制器证据矩阵.md` |
| MWORKS 母模型、原生结果、曲线和动画证据 | `控制器组合与整机动画闭环设计.md` |
| 算法家族、专题背景和旧的控制器目录索引 | `控制体系总览.md` |
| Live 双 GUI、实时合同和操作流程 | `../04_展示与实验平台/MWORKS实时联合仿真与双GUI接口设计.md` |

建议评委或新开发者按“本文 -> 已验证预设/证据矩阵 -> 具体模型或运行工作流”的顺序阅读。
不要从算法家族目录、文件名或旧截图反推当前可执行控制关系。
