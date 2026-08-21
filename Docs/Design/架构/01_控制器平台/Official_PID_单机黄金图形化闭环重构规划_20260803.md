# Official PID 单机黄金图形化闭环重构规划

版本：2026-08-03
状态：已完成（当前源 MWORKS 验收通过）
范围：MWORKS / Sysplorer 单机 Official PID 图形化入口

> **当前架构覆盖（2026-08-21）**：本文保留为 Official PID 黄金入口的历史设计记录。
> 当前源树已经完成新架构接入；活动入口、控制核心和兼容壳以
> `Models/README.md`、`Config/control_platform/model_studio_task_routes_v1.toml`
> 及 `Results/architecture_verification_20260821/ARCHITECTURE_LOCKED_REPORT.md`
> 为准。本文出现的 `Experiment.Runners.*` 路径是当时的规划/provenance，不能从归档
> 恢复到活动包树。

## 1. 目标与边界

本次工作的目标是建立一个可在 Sysplorer 中逐层展开、可检查、可仿真的
Official PID 单机黄金模型。它既是后续 `px4ctrl`、多机 Figure8 和其他控制器
图形化入口的组织模板，也是给评审者查看完整信号链的正式模型入口。

黄金模型必须满足以下闭环：

```text
ClimbPath 参考轨迹
  -> OfficialPIDGraphicalRotorAdapter / Vehicle.Blocks.Controller.Controller
  -> 电源与 ESC 的透明名义链
  -> 四路旋翼命令通道
  -> Sunray150Assembly
  -> 机体动力学 + 物理 Sensors + 视觉壳
  -> GPS/Mid360 导航接口
  -> Official PID 位置/姿态反馈
```

ORIN NX 任务计算机和 System Supervisor 作为同一顶层模型中的监视/任务支路
接入，展示任务参考、健康状态和电源状态，但不绕过 Official PID、替换
`Sunray150Assembly`，也不向控制回路注入未经批准的估计器或故障逻辑。

本次不做以下事情：

- 不修改 Official PID 控制律、参数、坐标约定、旋翼顺序或既有 FormalRunner 的
  仿真边界；
- 不把 `CompleteSystemGraphical` 视觉模板改造成第二套物理模型；
- 不实例化旧 `Vehicle.Electricals.Actuator` 作为第二套电机动力学；
- 不改变 48 条 Formal 入口目录、G2/G3 证据或 Gazebo/PX4/ROS 运行时；
- 不把图片、装饰框或未接线的模块当作控制成功证据。

## 2. 现状与问题定位

当前 Formal 入口的执行链是有效的：`OfficialPidFormalRunner` 继承
`RotorCommandRunner`，控制器使用 `OfficialPIDRotorAdapter`，机体使用共享的
`Sunray150Assembly`。该 Formal 适配器属于既有证据边界，本次不修改它。
黄金入口使用同一 `Vehicle.Blocks.Controller.Controller` 核心和等价参数映射的
`OfficialPIDGraphicalRotorAdapter`，把原适配器中写在方程区的旋翼映射拆成真实
可展开组件；这样图形化增强不会改变 FormalRunner 的源路径或证据。

官方 `MoSimQuadrotorModel.Vehicle.Examples.Example1` 提供的是图形组织方式：
参考轨迹、控制器、四个执行器、机体和 Sensors 均为可展开实例，并通过显式
`connect` 形成可读信号链。本项目采用这一组织方式，但保留项目自己的
`Sunray150Assembly`、参数 Profile 和 Official PID 控制实现。

因此本次改造分为两层：

1. **行为层**：继续使用当前已验证的 Official PID 核心和共享机体；新增的电源/ESC/旋翼
   通道在名义配置下是透明映射，不能改变基线输出。
2. **图形层**：为真实实例补充可读的层级、连接和图标；每个图标都对应一个
   实际信号或实际 Modelica 子模型，并在文档中注明监视支路与控制支路的边界。

## 3. 目标类结构

新增正式的黄金入口，不放入 48 条 Formal 目录：

```text
MoSimQuadrotorModel.Experiment.Runners.Golden.
  OfficialPidSingleUavGoldenRunner
```

目标展开层级如下：

```text
OfficialPidSingleUavGoldenRunner
├─ reference                         Guidance.Trajectories.ClimbPath
├─ controller                        Control.Adapters.OfficialPIDGraphicalRotorAdapter
│  ├─ core                           Vehicle.Blocks.Controller.Controller
│  │  ├─ 位置控制
│  │  ├─ 姿态控制
│  │  └─ 控制分配
│  └─ mapper                         Control.Allocation.OfficialPidRotorCommandMapper
├─ battery                           Templates.Modules.BatteryPower
├─ esc                               Templates.Modules.ESCDrive
├─ motor1..motor4                    Golden.Modules.RotorCommandChannel
├─ plant                             Vehicle.Sunray150Assembly
│  ├─ physical                       Vehicle.Dynamics.PhysicalWrenchAdapter
│  │  └─ wrapper / RotorActuatorCore
│  ├─ sensors                        Vehicle.Sensors.Sensors
│  └─ visual_shell                   Vehicle.Sunray150VisualShell
├─ perception                        Templates.Modules.PerceptionInterface
├─ mission_computer                  Templates.Modules.MissionComputer
└─ system_supervisor                 Templates.Modules.Supervisor
```

`motor1..motor4` 是实际命令/转速遥测边界：它们只做逐路信号透传并提供旋翼
图标，真正的推力、反扭矩、电机动态和故障注入仍由
`Sunray150Assembly.physical.wrapper` 计算。这样既能在顶层看到四个旋翼通道，
又不会重复实例化一套动力学。

`perception` 消费 `Sunray150Assembly` 内部真实 Sensors 输出的位置信号，并在
名义配置下原样提供本地位置给 Official PID。GPS/Mid360 图标表达导航接口和
信号来源，不声称当前离线模型已经完成真实 GPS、Mid360 点云或避障运行时部署。

`battery` 与 `esc` 位于控制命令到四路通道之间。黄金名义 Profile 中电源压降
关闭、命令限幅不触发，因此该链路等价于当前直接连接；后续可在同一入口中显式
打开电源或 ESC 故障，而不重构控制器和机体。

## 4. 资源与模型来源

| 顶层表现 | 实际来源 | 使用方式 | 证据边界 |
|---|---|---|---|
| Sunray150 机体 | `Vehicle.Sunray150Assembly`、`Vehicle.Sunray150VisualShell` | 真实物理机体、Sensors 和旋翼可视化 | MWORKS 离线模型 |
| GPS + Mid360 | `Templates.Modules.PerceptionInterface` | 位置导航接口与健康输出 | 不等同于真实点云/飞行部署 |
| V6X | `OfficialPIDGraphicalRotorAdapter` 的控制栈图标与标注 | 表示控制器在飞控侧的归属 | 不新增 V6X 硬件动力学 |
| ESC | `Templates.Modules.ESCDrive` | 名义透明命令调理 | 不替代机体内部 `RotorActuatorCore` |
| Battery | `Templates.Modules.BatteryPower` | 名义电源监视 | 不改变基线命令 |
| 四路电机 | `Golden.Modules.RotorCommandChannel` | 实际命令/转速信号通道与图标 | 动力学仍在共享机体内 |
| ORIN NX | `Templates.Modules.MissionComputer` | 任务参考与状态监视支路 | 不接管 Official PID |
| System Supervisor | `Templates.Modules.Supervisor` | 健康/模式监视支路 | 不作为性能判据 |

图标资源全部来自项目内的
`Models/MoSimQuadrotorModel/Vehicle/Resources/Images/`，使用
`modelica://MoSimQuadrotorModel/...` URI，不依赖用户电脑上的绝对路径。

## 5. 行为不变量

黄金模型完成后，以下量必须保持与现有 `RotorCommandRunner` / Official PID
路径一致：

1. `profile`、初始状态、参考轨迹和求解器设置不变；
2. `OfficialPIDRotorAdapter` 的 Formal 入口源文件保持不变；黄金图形适配器
   复用同一 `core`，并以四个显式增益保持原 `{y,-y1,y2,-y3}` 输出映射、悬停
   转速、命令缩放和 yaw authority 参数；
3. `Sunray150Assembly` 的质量、惯量、推力/反扭矩系数、旋翼位置、旋向和
   视觉转速顺序不变；
4. 名义电源/ESC/旋翼通道满足 `command_to_plant = controller.rotor_command`
   和 `speed_observation = plant.rotor_speed`；
   Golden 入口将 `nominal_esc_limit_abs` 固定为 `200 rad/s`，高于现有
   Official PID ClimbPath 基线原始结果四路命令的 `105.63 rad/s` 峰值；该值
   只用于证明名义透明边界，不改变共享 `ESCDriveModule`、控制律或 Plant。
6. 监视/任务支路没有回连到控制器输入或机体力/力矩输入。

任何不满足上述条件的改动必须作为单独的参数失配/故障实验，不得悄悄进入
黄金基线。

## 6. 实施阶段

### 阶段 A：图形化控制器边界

- 新增 `OfficialPidRotorCommandMapper`，把原适配器中的旋翼命令映射变成可展开
  的真实 Modelica 子模块；保留原适配器诊断变量和方程含义。
- 新增 `OfficialPIDGraphicalRotorAdapter`，复用同一 `Vehicle.Blocks.Controller.Controller`
  和参数映射；画出输入、PID 核心、四个原始符号增益、yaw authority 映射和四路输出。
- 保留 `OfficialPIDRotorAdapter` 原始方程和 FormalRunner 绑定，避免图形布局改动
  进入既有 48-route Formal 证据路径。

### 阶段 B：黄金单机入口

- 新增 `Experiment.Runners.Golden` 包和
  `OfficialPidSingleUavGoldenRunner`。
- 以 `RotorCommandRunner` 的真实连接为基准，插入透明 Battery/ESC/四路
  RotorCommandChannel，并接入 Perception、Mission、Supervisor 监视支路。
- 为所有顶层实例设置明确 Placement、端口名称和信号颜色。

### 阶段 C：共享机体展开

- 只补 `Sunray150Assembly` 的内部 Placement/Line 图形标注；不改其方程。
- 展开后能看到 `PhysicalWrenchAdapter`、`Sensors`、`Sunray150VisualShell`
  和 gust/故障参数边界。
- 若子类仍为空，再逐个补子类图形标注；不引入第二个 plant。

### 阶段 D：验证与推广

- 静态检查包路径、类名、资源 URI、连接端口和目录边界。
- 在已授权 MWORKS 环境中对黄金入口执行 `CheckModel`，记录错误/警告和图形
  展开截图。
- 使用与 Official PID 基线相同的 `ClimbPath 50 s` 设置运行一次，比较位置、
  姿态和四路旋翼命令；仅在结果一致后才把该入口作为后续图形化模板。
- 再将同一层级模式推广到 px4ctrl、三机 Figure8 和其他控制器；本阶段不提前
  修改它们。

## 7. 验收门槛

### 图形门槛

- 打开黄金入口后，顶层有参考、控制器、电源/ESC、四路旋翼、机体和传感器的
  可读图形与连线；
- 展开 `controller` 能看到 PID 核心和命令映射；
- 展开 `plant` 能看到物理力/矩、Sensors 和可视化壳；
- 展开 `perception` 能看到 GPS/Mid360 接口及真实位置输入；
- 不出现只有名称的空矩形、红色缺失类或无法追溯的虚假连接。

### 行为门槛

- `CheckModel` 通过；
- 黄金入口的名义 `ClimbPath 50 s` 结果与当前 Official PID 基线在既定数值
  容差内；
- 结果文件、CheckModel 输出和截图路径可回链；
- 不能用“图形完整”替代数值仿真证据。

## 8. 风险、回滚与后续

| 风险 | 控制措施 | 回滚方式 |
|---|---|---|
| Battery/ESC 透明链改变命令 | 名义压降为零、限幅上界高于基线范围，并比较四路命令 | 黄金入口退回直接 `controller -> plant` |
| 新映射模块改变变量求解 | 保留旧适配器变量和代数关系，先 CheckModel 再仿真 | 恢复适配器原方程，保留新入口文档 |
| 图形标注触发 MWORKS 写回噪声 | 只改目标类，立即检查 diff | 丢弃目标类的布局改动，不动其他文件 |
| 监视支路误接入控制回路 | 规划中明确只读方向，静态检查连接方向 | 删除监视支路实例，不影响控制核心 |
| 子模型仍为空 | 逐层补真实子类 Placement，不再增加外层壳 | 保留已通过的直接 Runner |

完成黄金入口后，下一步优先级为：

1. 让 `OfficialPidFormalRunner` 可选择打开黄金图形入口，同时保留原 Formal
   入口作为行为回归基线；
2. 按同样模式改造 `Px4CtrlFormalRunner`，把其 EquationBridge 与真实
   Sysblock 设计边界并列展示；
3. 再推广到三机 Figure8；
4. 最后处理其余控制器，逐个增加图形核心，不用一个空壳通用框代替。

## 9. 评审展示与复用标准

### 9.1 展示顺序与可主张内容

评审从 `MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner`
的顶层开始，只沿真实连线展开：`ClimbPath -> controller -> ESC -> 四路 Rotor
Channel -> Sunray150Assembly -> Sensors/Perception -> controller`。先说明
`OfficialPidFormalRunner` 是保持不变的数值回归基线，再说明 Golden 入口是本项目
新增的可展开模型入口；二者不能互相替代。

本项目不主张重新发明 Official PID 控制律。可以主张的工作是：把原来仅在
`OfficialPIDRotorAdapter` 方程区可见的四路符号、偏航投影、物理偏航权重、悬停
转速和旋向映射，拆为 `OfficialPIDGraphicalRotorAdapter` 与
`OfficialPidRotorCommandMapper` 中可逐层检查的真实 Modelica 块；并让它们通过
`PartialRotorCommandController` 接到同一个已验证的 `Sunray150Assembly`。这样，
评审者能核对每条命令和反馈，而不是只看到一张示意图。

建议现场展示四个层级：

1. 顶层闭环，说明参考、控制、执行、机体和反馈的真实方向；
2. `controller`，说明 PID 核心与四路显式符号增益；
3. `mapper`，说明先分离原混控中的偏航分量，再按共享机体的旋向和反扭矩参数映射；
4. `plant.physical.wrapper.RotorActuatorCore`，说明推力、反扭矩、旋翼位置和故障
   都只在共享物理机体中计算。

展示结果时，静态结构检查、MWORKS `CheckModel`、图形展开截图和 Golden 对 Formal
的同条件数值比较分别展示。静态检查或图片不能单独证明闭环性能。

### 9.2 Sysblock 与模型边界

这里的 `Sysblock` 指带有 MWORKS `SysblockVersion` / `BlockSystem` 元数据的块系统，
不能把所有带图标的 Modelica 类都称为 Sysblock。黄金 PID 中
`Vehicle.Blocks.Controller.Controller` 是现有的 Modelica PID 核心；它在本次重构中
未改写，也不是新增的独立 Sysblock 控制器。名称为
`Sunray150CompleteSystemGraphical_Sysblock` 的类是架构模板，Golden 仅通过
`Templates.Modules` 继承其中的导航、飞控、任务、供电和 ESC 接口模块，未把它
实例化为第二套机体或控制回路。

真正属于本次图形化改造的模型是 `OfficialPIDGraphicalRotorAdapter`、
`OfficialPidRotorCommandMapper`、`RotorCommandChannel` 和黄金 Runner 的接线。
其中 `RotorCommandChannel` 只透传命令和转速遥测；它不是电机动力学。真实执行器链
始终是 `PhysicalWrenchAdapter -> WrapperSurface -> RotorActuatorCore`。这一区分要在
评审时明确说出，避免把架构模板、监视支路或图片误称为控制器或物理模型。

### 9.3 接口为什么这样设计

控制器接口选择 `PartialRotorCommandController`，输入为位置、速度、加速度参考和
位置、速度、姿态测量，输出为四路有序的 `rotor_command[4]`。这样选是因为 Official
PID 的既有核心直接给出四路混控量，适配器只承担显式、可审计的单位缩放、悬停偏置、
旋向和偏航反扭矩映射，不把这些跨机体约定藏在 Runner 或图标中。

共享 Plant 是接口的另一端：它保有质量、惯量、旋翼坐标、旋向、推力/反扭矩和转速
遥测的唯一真值。`BatteryPower`、`ESCDrive` 和四路 Channel 在黄金名义配置下保持
透明；Perception、FlightController、MissionComputer、Supervisor 都是只读或监视支路，
不得回接到控制器或机体力/力矩输入。因此以后替换控制器时，Plant、参考轨迹和结果
变量保持可比较。

### 9.4 其他控制器的适配规则

后续控制器不得套一个空白外框后接入。每个控制器先按其天然输出选择一个已有接口：
直接给四路旋翼速度的实现使用 `PartialRotorCommandController`；给期望姿态与总推力的
实现使用 `PartialAttitudeThrustController`；给角速度与总推力的实现使用
`PartialBodyRateThrustController`；给机体系力/力矩的实现使用 `PartialWrenchController`。
若控制器是 Sysblock，则新增一个项目拥有的适配器，把其端口、坐标系、单位、采样周期
和分配关系显式转换到上述契约之一，而不修改共享 Plant 或伪造中间动力学。

每次推广都必须满足：保留原 FormalRunner 作为行为基线；一个控制器只有一个真实核心；
一个 Plant 只有一套执行器动力学；图形中每个块都有真实端口或方程；然后分别通过源码
结构门、MWORKS `CheckModel`、同工况数值比较和图形展开审查。只有全部满足后，才能将
该图形入口作为该控制器的黄金入口。

### 9.5 图片比例规则

模块矩形只表示边界和端口区域，不用于裁切或拉伸图片。每个 `Bitmap` 的显示宽高必须与
其原始 PNG 宽高比一致；当标签或端口空间不足时，只能等比缩小并平移图片，不能独立修改
宽或高。`check_official_pid_golden_surface.py` 现对黄金路径使用的位图进行原图宽高比
检查，显示比例相对误差上限为 `2e-4`。

## 10. 当前状态记录

本文件只记录设计与实施约束。未执行 MWORKS `CheckModel` 或仿真前，不宣称
黄金入口已经通过；最终状态必须由现场 MWORKS 输出、结果文件和图形截图共同
确认。

当前可重复的静态门为
`Scripts/mworks/check_official_pid_golden_surface.py`（schema
`mosim.official_pid_golden_surface.v4`），其单元测试为
`Scripts/tests/test_official_pid_golden_surface.py`。该静态门检查源码入口、
包注册、控制/电源/ESC/四路旋翼/Plant/监视支路的闭环连接、图形映射四路拓扑，
以及 `PhysicalWrenchAdapter -> WrapperSurface -> RotorActuatorCore` 共享执行器链和
Golden 顶层、物理力矩层、执行器层、可视化壳的可展开图形表面；
结果写入 `Results/mworks_live_gate/official_pid_golden_20260803/`。这些检查仍只证明
源码结构不变量，不替代 MWORKS `CheckModel`、图形展开截图或数值仿真。

2026-08-03 静态实现补充：`Sunray150Assembly` 已为外部命令/位置/姿态/转速端口、
`PhysicalWrenchAdapter`、真实 `Sensors`、`Sunray150VisualShell` 和 gust 支路补充
Diagram Placement 与物理帧/转速遥测连接线标注；这些改动只影响展开图形，不改变其
方程和参数。静态结果已写入
`Results/mworks_live_gate/official_pid_golden_20260803/OFFICIAL_PID_GOLDEN_STATIC_CHECK.json`，
结果为 `pass`，且确认 `OfficialPidFormalRunner` 仍使用原始
`OfficialPIDRotorAdapter`。

2026-08-03 当前轮 MWORKS sentinel 已记录于
`Results/mworks_live_gate/official_pid_golden_20260803/GUI_SENTINEL_BEFORE.json`。
该记录发现当前可见主窗口为 `Sysplorer [教育版]`。同一结果目录中已有的
`MWORKS_MCP` `post_yaw_fix` 50 s 导出可作为布局前回归证据，但不能代替当前
源的 `CheckModel`。本轮对可复用 MCP 会话的只读 `probe` 与带最终源重载的
有界 `CheckModel` 均超时，未返回模型错误或授权错误，因此不得将本轮静态通过
或历史结果写成当前源的 live 验收。以下“会话恢复后的下一步”是当时的历史行动项，
已经被 2026-08-21 架构锁定取代，不得再针对归档的
`MoSimQuadrotorModel.Experiment.Runners.Golden.*` 或 `Formal.*` 路径执行、恢复或复制
源码。当前入口和结构证据以 `Models/README.md` 与
`Results/architecture_verification_20260821/CHECKMODEL_MWORKS_MCP.json` 为准。

补充审计，2026-08-03：历史 `MWORKS_MCP` 结果包
`Results/mworks_live_gate/official_pid_golden_20260803/live_attempt_20260803_1911/`
包含 Golden `post_yaw_fix` 和不变的 Formal 基线各一份 50 s 原始导出。新增
`Scripts/mworks/verify_official_pid_golden_equivalence.py` 将 Golden 的 0.01 s
样本与 Formal 的同一时刻样本比较，并输出原始 CSV 哈希、最大差异和阈值。该比较
只证明该结果包的数值一致性；本轮对 MCP 的只读 `probe` 已有界超时，且随后图形
注解发生了布局改进，因此它不替代最终当前源的 `CheckModel`、图形截图或重新仿真。

2026-08-04 历史源验收记录：当时通过官方 Sysplorer MCP 对工作区源执行
`MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner`
的强制重载与 `CheckModel`，结果为 `true`；随后按 `0..50 s` 运行当前 Golden
仿真并通过 `GetVarTimes` / `GetVarsValues` 读回 5001 个样本。未修改的
`MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner` 同样
通过 `CheckModel` 和 50 s 仿真，读回 25001 个样本。当前源 Golden-Formal
等价检查通过：时间轴抽样步长为 5，位置/姿态字段最大差异均小于 `0.001`，
四路旋翼命令/转速最大差异均小于 `0.02`；Golden 终端位置误差为
`0.0065053545 m`，Formal 为 `0.0065070764 m`。

上述类名、文件路径和结果只保留为历史 provenance，不代表当前活动源仍有这些类；
不得据此把归档 Runner 搬回 `Models`。

本轮 MCP 导出的图形审阅文件位于
`Results/mworks_live_gate/official_pid_golden_20260803/direct_api_49152/current_turn_20260804/screenshots/`，
包含顶层、控制器、旋翼映射器和 `Sunray150Assembly` 展开图；当前源验收包、
原始 CSV 和逐字段指标位于同目录下的 `CURRENT_SOURCE_ACCEPTANCE_PACKET.json`、
`raw/` 和 `metrics/`。这些结果证明当前源的 MWORKS 结构、仿真执行、结果读回和
Golden-Formal 数值等价，不证明 ROS/PX4/Gazebo 部署、真实 GPS/Mid360 点云或
飞行运行时验收。原有 `OfficialPidFormalRunner` 与 `OfficialPIDRotorAdapter`
未发生 Git diff。
