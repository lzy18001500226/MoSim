# MWORKS控制器关系与组合架构

> 状态：当前控制关系和组合语义权威，2026-07-26。
>
> 本文回答“控制器在整机链路的哪个位置、能替换什么、如何组合、APP 当前实际能
> 配置和运行什么”。它以项目控制责任、`Model Studio` 源码和已登记 Profile 为准；
> APP 的控件名称不是架构层级的唯一来源。接口字段、Registry、验收门和逐路线证据
> 分别仍以 `控制平台接口与闭环实施规范.md`、
> `Config/control_platform/control_module_registry.json` 和 `控制器证据矩阵.md` 为准。

## 1. 先看一张关系图

MoSim 不把历史 67 条分层证据路线平铺成 67 个可互换的“控制器”。固定的是飞机、状态、
参考和下游责任；可替换的是有明确输入输出合同的槽位。

```text
任务 / 轨迹 / 场景
  -> 单机原始参考 -----------------------------------------------------+
  -> 编队参考 (可选，多机状态 -> 每机参考)                            |
  -> 参考约束 (可选，如 Reference Governor)                           |
                                                                          v
状态 / 传感器 -> [AWFF / 参考前馈: Profile 内可选]
  -> [名义位置 / 平动控制器: 恰好一个] -> 期望姿态 + 总推力
  -> [残差补偿: 最多一个，L1 或 ESO 或学习残差]
  -> [INDI: Profile 内可选，且位于残差补偿之后]
  -> [固定物理限幅 / 安全检查] -> [姿态 / 角速度 owner: 恰好一个]
                                                                          |
                                                                          v
                    [分配 owner: 由输出边界决定] -> [Adapter] -> 电机 -> 机体 / 传感器

电机效率下降、风扰和参数失配首先是场景注入。它们不能自动推导出 FDI、
故障隔离、故障重构或主动容错已经完成。
```

这张图同时适用于 MWORKS 离线整机模型、MWORKS Live 和 ROS1/PX4 运行链。不同
后端的差异只能发生在已声明的 owner 和 Adapter，不能靠 UI 名称或模型文件名推断。

### 1.1 目标目录：47 个 Control Profile，七个控制器族

对外比较和后续报告使用的对象是完整、可命名、可追溯的 **Control Profile**，不是把
名义控制器、增强模块和场景做笛卡尔积。批准后的目标目录为 47 个 Profile：

| 控制器族 | 目标数量 | 目录归属与组成 |
| --- | ---: | --- |
| PID 与智能 PID | 10 | 当前五个 PID 路线、FOPID、三个 PID 固定链，以及计划中的 `PidAwffLinearEso` |
| 线性与鲁棒状态反馈 | 6 | LQR、LQI、LQG、H2、H-infinity、极点配置 / Luenberger |
| 非线性与自适应控制 | 6 | 反步、反馈线性化、MRAC、NDI、无源控制等 |
| 滑模控制 | 7 | 边界层、积分、终端、超扭曲、自适应和模糊滑模等 |
| 最优与预测控制 | 10 | 当前八条优化路线，以及两个已命名的 MPC/NMPC 固定 Profile |
| 几何与微分平坦控制 | 6 | SE(3) 与 DFBC 系列 |
| 智能与学习残差控制 | 2 | RL 增益调度与训练后神经残差 |
| 合计 | **47** | 一个运行一次只选择一个完整 Profile |

`Official PID` 属于 PID 族，`role=reference_baseline`；`px4ctrl` 是 ROS1/PX4
部署基线，不计入 MWORKS 的 47 个比赛 Profile。原 `fixed_integrated` 不再是一个
控制器族：PID 固定链归入 PID 族，MPC/NMPC 固定链归入最优与预测控制族。

原子迁移时，旧 `fixed_integrated` 标识按下表改为语义化 Profile 名，而不是保留一个
平行目录：

| 当前 `scheme_id` | 目标 `profile_id` | 归属 |
| --- | --- | --- |
| `fixed_awff_pid` | `PidAwff` | PID 与智能 PID |
| `fixed_awff_l1_residual` | `PidAwffL1Residual` | PID 与智能 PID |
| `fixed_awff_l1_indi` | `PidAwffL1Indi` | PID 与智能 PID |
| `fixed_linear_mpc_l1_indi` | `LinearMpcL1Indi` | 最优与预测控制 |
| `fixed_qp_nmpc_l1_indi_cbf` | `QpNmpcL1IndiCbf` | 最优与预测控制，`research_only` |
| 新增 | `PidAwffLinearEso` | PID 与智能 PID，冻结标签 `planned`；当前源/Runner 已物化 |

当前 `Config/control_platform/controller_route_interface_matrix.json` 的 46 条记录是
历史迁移分类快照，保留用于追溯，不能作为当前“未实现数量”。第 47 条
`PidAwffLinearEso` 的项目源、Adapter、FormalRunner 和 50 s 运行记录均已存在；
其终端误差 3412.36 m，属于性能失败而非实现缺失。`current_model_entry_map.json`
中的 `planned/not_runnable` 仍是冻结兼容字段，不能覆盖当前源面和运行证据。
因此 **47 是当前 MWORKS Profile 目录数，48 是含 `px4ctrl` 基线的活动条目数**；
“已实现/已运行”和“性能通过/正式选择资格”必须分开表述。

每个 Profile 至少声明 `profile_id`、`family`、`role`、`nominal_controller`、
`augmentation_chain`、输出边界、Adapter、场景和 `implementation_status`。其中
`role` 只能说明 `reference_baseline`、`candidate`、`planned` 或 `research_only`，
不能代替闭环、代码生成或部署证据。

批准的增强组合语法固定为：

```text
trajectory/reference
  -> AWFF/reference feedforward
  -> exactly one nominal controller
  -> at most one residual compensator: L1 OR ESO OR learned residual
  -> optional INDI after residual compensation
  -> fixed physical limiter / safety check
  -> Adapter / Plant
```

禁止 `L1 + ESO`、`ESO + neural residual`、`L1 + neural residual`、两个名义控制器
串联，以及标准界面中的任意多增强勾选。`CBF` 保留为体系结构和研究候选；在没有真实
约束场景及触发证据前，`fixed_qp_nmpc_l1_indi_cbf` 不得宣称安全收益或进入冠军比较。

## 2. 槽位、替换边界与当前事实

| 责任槽位 | 运行中数量 | 输入 -> 输出 | 可替换边界 | 当前事实 |
| --- | ---: | --- | --- | --- |
| 任务/轨迹 | 1 | 场景、时间 -> `ReferenceFrame` | 更换任务、轨迹或规划器 | 不是控制器；APP 的地图、任务轨迹属于此处 |
| 编队参考 | 0..1 | 多机状态/编队目标 -> 每机 `ReferenceFrame` | 更换编队参考算法 | 只有多机才可启用；当前三机案例是固定规模领航-跟随参考，不等于分布式通信证明 |
| 参考约束 | 0..1 | 原始参考/约束 -> 受约束参考 | 如 Reference Governor | 逻辑上在名义控制器前；即使 Registry 将其归入 safety，也不能画到命令末端 |
| 位置/平动外环 | 恰好 1 | 状态、参考 -> `CommandFrame` | 替换主跟踪控制律 | PID、改进 PID、Linear MPC、fault compensation 等在当前 APP 中由此槽位选择 |
| 前馈、残差与内环增强 | 仅按已命名 Profile 解析 | 状态、参考、候选命令 -> 修正项/命令 | 只能挂到声明的作用点和顺序 | AWFF 位于名义控制前；L1、ESO、学习残差三选一；INDI 只可位于残差之后；标准 UI 不提供任意叠加 |
| 命令安全 | 1 项已声明策略 | 参考或候选命令 -> 通过/修改/拒绝 | 参考侧或命令侧必须显式标注 | 当前已认证组合使用 `basic_limiter`；CBF 等待独立兼容和数值门 |
| 姿态/角速度内环 | 恰好 1 owner | 姿态误差/姿态参考 -> 角速度参考或力矩语义 | 可以由 MWORKS 模型或 PX4 后端拥有 | 离线预设使用“模型内部姿态/角速度环”；当前 Live 合同使用 PX4 内置姿态/角速度环 |
| 控制分配 | 由输出决定 | `WRENCH` -> `ROTOR_COMMAND` | WRENCH/ROTOR 路线必须声明 allocator owner | 当前离线预设标记 `px4_control_allocator`；不能据此推断已替换 ROS1/PX4 实时分配器 |
| Command Adapter | 恰好 1 | 类型化 `CommandFrame` -> 后端命令 | 只做语义、坐标、单位和时序映射 | 不得偷偷改变控制律 |
| 植物/传感器 | 1 | 电机命令 -> 状态/观测 | 后端或场景替换，不是控制器替换 | MWORKS 离线模型与 Gazebo/PX4 是不同证据层 |
| 故障管理侧链 | 0..1 管理策略 | 健康/响应 -> 事件、重构或安全动作 | 需同时具备注入、检测、隔离和响应合同 | 当前七场景中的风扰、电机效率下降首先是场景注入，不自动证明 FDI 或 FTC |

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

控制责任和文件位置必须同时说明。当前正式 Modelica 实现只有一个根，审查和复现只加载
这个根的 `package.mo`：

```text
Models/MoSimQuadrotorModel/
  唯一活动实现与正式加载入口：Baseline、Controllers、Dynamics、
  ExperimentRunner、LiveIntegration、Formation、Missions、Parameters、
  Planning、Robustness、SceneTrace、Support、System、Plant
```

离线 Profile 的推荐打开链路是：

```text
Model Studio
  -> MoSimQuadrotorModel.Experiment.Runners.*
  -> typed Adapter
  -> controller wrapper/source
  -> shared plant/result contract
```

活动 Profile、脚本、配置和人工打开操作必须使用 `MoSimQuadrotorModel.*`。历史 Results、
旧运行记录和已归档证据中的旧全限定名保留其原样作为当时的 provenance，但不能重新作为
当前正式加载入口。

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
| 主控制器 / 控制器方案 | 从 47 个目标 Profile 中选择一个；内部 owner 与固定链由目录解析 | 不是所有环路的无条件总开关，也不是任意组合 |
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
| 研究候选组合 | 标准 UI 不提供多增强复选；候选必须保存为显式配置并精确匹配已解析的 Registry/Adapter 链 | 只说明候选组合被描述，不能计入 47，也不能说明已仿真、已代码生成或可运行 |
| 认证/验证预设 | 选择预设会填充所有字段；只有字段仍与该预设完全匹配，离线 MIL 才可启动 | 该精确组合的认证记录可追溯；改任一字段即成为新候选 |
| 当前禁用预设 | `QP/NMPC Safety` 等候选仍可见禁用；场景注入控件也默认关闭 | 不能通过改名或换 UI 位置绕过门禁 |
| Live 可准备 | 还需连接预检和实时合同通过 | 当前只允许单机、无编队、`official_pid`、PX4 inner、`ATTITUDE_THRUST` 的 50 Hz 合同 |

因此，“APP 支持自由组合”的准确表述是：**可以记录受控研究候选，并由兼容性、预设
一致性和后端合同决定能否运行**；不是任意笛卡尔积，也不是标准 UI 的多增强选择。目标
目录固定为 47 个 Profile；候选只有在形成新的固定拓扑、源配置和独立证据后才可申请进入
目录。

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

## 6. 历史 67 条路线怎样放进这张图

历史证据矩阵的 67 条路线按责任槽位归类如下：

| 类别 | 路线数 | 报告时的正确说法 |
| --- | ---: | --- |
| 名义控制 | 43 | 主跟踪控制候选；一次运行只选择一个 |
| 增强/补偿 | 12 | 挂接在明确名义控制器上的消融/补偿路线 |
| 姿态到角速度 | 1 | 姿态到角速度参考模块，不等于替换 PX4 角速度环 |
| 编队参考 | 9 | 多机参考生成；每架机仍需下游单机控制器 |
| 安全聚合 | 1 | 约束和 fallback 路线，按触发行为验收 |
| 故障聚合 | 1 | 故障管理路线，必须区分注入、检测、隔离和响应 |

历史矩阵的冻结计数是 `accepted=27`、`executed_blocked=33`、`not_run=7`；其中
`65/67` 只是通过相应 codegen/SIL 门的路线数，不是 65 个同级且已接受的整机控制器。
具体状态、首个 blocker 和声明上限只在 `控制器证据矩阵.md` 与其 JSON 权威中维护。

因此历史 `67` 条路线与目标 `47` 个 Profile 并不冲突：前者是覆盖名义控制、增强、
安全、故障、编队等责任层的证据路线，后者是将当前 46 条路线按控制责任重新归族并加入
一个已物化但性能待评估的 ESO Profile 后，用于选择、解释和比较的完整目录。两者不是一一映射，也不能
由历史图形探针直接推导整机闭环、代码生成或部署状态。

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
