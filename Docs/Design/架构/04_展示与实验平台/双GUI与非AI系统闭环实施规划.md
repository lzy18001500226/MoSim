# MoSim双GUI与非AI系统闭环实施规划

> 状态：长期Goal实施入口，2026-07-17。
>
> 本文冻结MoSim Model Studio、MoSim Flight Console和Orchestrator的产品边界、
> 实施顺序与验收门禁。当前Goal不实现AI助手，只预留上下文和受控操作接口。
> 任务算法、地图注册、QGC二维地图和地图切换的权威接口见
> `Docs/Design/架构/00_架构与任务/任务算法与场景地图注册接口.md`；Flight Console
> 布局、QGC复用审计、二维任务编辑和坐标/发布合同见
> `Docs/Design/架构/04_展示与实验平台/Flight Console与二维任务地图详细设计.md`。

## 1. 冻结决策

1. 现有已验收控制器足够打通系统纵向闭环；控制器家族扩充与GUI开发并行，
   不等待所有控制器完成。
2. Model Studio必须使用MWORKS.Syslab原生`TyAppDesigner` APP开发，并保持轻量。复杂图形化建模、
   拖拽编辑和完整调参仍属于Sysplorer/Syslab原生工具，不在Model Studio中重做。
3. Flight Console必须先调研本地和GitHub开源项目，再选择可复用底座。选中后复制到
   项目自有产品路径二次开发，不直接修改`References/`中的参考仓库。
4. 控制器和多机数量由机器注册表驱动。界面预留3至9机和全部控制器，但首版只开放
   已通过相应证据门禁的控制器以及3机；其他选项显示禁用原因。
5. RViz、UE和MWORKS结果查看器是专业显示工具。两个GUI负责选择、编排、状态、
   证据和窗口/流会话管理，不重复实现其核心渲染能力。
6. AI助手是后续亮点，不进入本Goal的完成标准。当前只冻结AI上下文、建议、确认和
   审计接口，禁止AI直接拥有飞行控制权。
7. MWORKS不进入Gazebo快速控制回路。主线是模型/MIL/SIL/codegen、生成控制核心进入
   PX4/Gazebo/Sunray运行时、结果回流MWORKS分析；在线UDP联合仿真只保留为后续可选研究。

## 2. 产品组成

```text
MWORKS.Syslab原生APP: MoSim Model Studio
  -> 选择实验、控制器和参数集
  -> 模型检查、MIL/SIL、结果查看、codegen
  -> 向Orchestrator提交已验证实验

MoSim Orchestrator
  -> Profile与兼容性门禁
  -> run_id、hash、Launch Plan和运行状态
  -> MWORKS/codegen、Gazebo/PX4/MAVROS、显示会话与证据编排

项目自有Flight Console源码
  -> 运行控制、飞控状态、注入、遥测、RViz/UE和证据入口

Gazebo/PX4/MAVROS/控制器运行时
  -> plant、飞控、状态融合、控制与运行日志权威

RViz/UE/MWORKS结果查看器
  -> 工程审核、场景展示、动画、曲线和视频，不拥有性能判定权
```

## 3. Model Studio范围

### 3.1 最终页面结构

Model Studio不显示庞大模型树，采用“推荐Profile + 高级组合器”和少量标签页。所有算法
必须先按控制链角色分类，不能把名义控制器、增强、安全、故障和编队算法塞进同一个
“控制器”下拉框：

```text
基础实验:
  场景 -> 任务/轨迹 -> 规划器 -> 状态源 -> 车辆数量 -> 参数预设

控制链:
  编队层 -> Reference Governor -> 名义控制器 -> 有序增强链
         -> 姿态/角速度内环 -> Safety Filter -> Fault Manager
         -> Control Allocator -> Command Adapter

标签页:
  实验配置
  仿真摘要
  结果曲线
  代码生成
  运行回传
```

### 3.2 普通模式与高级模式

普通模式是默认入口，只显示已经冻结和验收的组合Profile，例如：

```text
官方PID基线
增强Cascade PID
PID + INDI
NMPC + INDI + L1 + Safety Filter
故障容错控制
三机Leader-Follower + Formation CBF
```

选择Profile后必须显示不可编辑的控制链摘要、证据等级、支持场景、支持车辆数和运行后端。
普通模式不要求用户理解模型文件名，也不能静默替换用户选中的模块。

高级模式面向算法开发和消融实验，按插槽逐层选择原子模块。每次选择后立即运行兼容性
解析，并显示以下三种结果：

```text
compatible                 可保存并继续模型检查
compatible_but_gate_pending 可保存研究配置，但不能进入更高证据层
incompatible               拒绝组合，并指出冲突插槽和原因
```

高级模式生成的组合也必须先保存为版本化Profile并计算hash，不能从GUI直接临时拼接后绕过
MIL/SIL/codegen或runtime门禁。

### 3.3 控制链插槽与算法归属

Model Studio和Flight Console使用同一套组合语义。场景、任务、轨迹、规划器、状态源和
车辆数来自ExperimentProfile/Profile Catalog；从`formation_controller`到`command_adapter`
的控制插槽以`Config/control_platform/control_module_registry.json`为权威。界面分类至少覆盖：

| 插槽 | 代表算法或模块 | 组合规则 |
| --- | --- | --- |
| ExperimentProfile `reference_trajectory` | 阶跃、悬停、8字、螺旋、轨迹回放、Diff-Planner、FUEL/RACER等规划输出 | 恰好一个参考来源；规划器不直接输出电机命令 |
| `formation_controller` | Leader-Follower、Virtual Structure、Consensus、Containment、Formation Tracking、Formation Reconfiguration、Fault-Tolerant Formation、Formation CBF、Distributed MPC | 单机为空；多机最多一个，输出每架飞机的名义参考 |
| `reference_governor` | Reference Governor、Geofence参考整形、动力学/速度/加速度约束 | 零或一个，位于名义控制器之前 |
| `nominal_controller` | 增益调度/Fuzzy/Neural/Cascade PID，LQG、mu-Synthesis、Feedback Linearization、Passivity-Based、Adaptive Backstepping，Integral/Terminal/Non-singular Terminal/Super-Twisting/Adaptive/Fuzzy/Neural SMC，Linear/Robust/Adaptive/Tube/Learning/Explicit-Gain-Scheduled MPC、iLQR/MPPI、NMPC Outer | 恰好一个；同一时刻只能有一个最终名义控制生产者 |
| `augmentation` | Anti-windup、Feedforward Profile、L1、AWFF、完整ADRC、标准化INDI、参数调度、Fuzzy/ANFIS、RBF/NN、ILC、RL增益调度与受限残差 | 零到多个，必须声明执行顺序、作用接口、限幅和reset语义 |
| `attitude_rate_inner` | PX4姿态/角速度内环、PID、SO3、INDI内环 | 恰好一个；允许由backend拥有，但必须在Profile中显式声明 |
| `safety_filter` | Safety Filter、CBF、命令限幅、状态有效性门禁 | 恰好一个，包括显式`pass_through`；拥有发布前最终否决权 |
| `fault_manager` | FDI、Passive FTC、Active FTC、单电机安全降落、多故障估计与重构、Failsafe状态机、Return-and-Land、Emergency Stop | 零或一个管理器，可触发降级、切换、悬停或降落 |
| `control_allocator` | PX4默认分配、故障感知分配、伪逆/WLS/QP重构 | `WRENCH`或`ROTOR_COMMAND`链路必须显式选择；与名义控制器解耦 |
| `command_adapter` | ATTITUDE_THRUST、BODY_RATE_THRUST、WRENCH、ROTOR_COMMAND到PX4/MAVROS的适配 | 恰好一个，负责坐标、单位、推力语义和消息边界 |

`INDI`、`CBF`和`Distributed MPC`等名称可能出现在不同论文层级。注册时必须用`kind`和
`stage`确定实际插槽，UI按机器字段显示，不按算法名称猜测。Neural PID、Neural-SMC、
RBF/NN和RL调度属于受控算法模块，不等于第9节的AI助手。

### 3.4 控制链可视化与参数交互

选中Profile后，Model Studio在配置区固定显示从左到右的控制链，不显示自由连线画布：

```text
[任务/规划]
  -> [编队/单机直通]
  -> [Reference Governor]
  -> [Nominal Controller]
  -> [Augmentation 1] -> [Augmentation 2]
  -> [Attitude Inner]
  -> [Safety]
  -> [Fault Manager / Allocator]
  -> [PX4 Adapter]
```

每个块显示状态徽标：`accepted`、`implemented`、`runtime_pending`、`blocked`或`research`。
点击块只打开受控参数摘要、证据、模型入口和禁用原因；详细连线和完整调参仍打开Sysplorer/
Syslab原生工具。增强链支持受控排序，但任何顺序变化都会产生新的Profile和hash。

### 3.5 Profile到图形化模型和运行后端的映射

不得为每种组合复制一套完整无人机模型。采用统一顶层实验Harness和可替换插槽：

```text
QuadrotorExperimentHarness
  Scenario
  TrajectoryOrPlanner
  FormationController
  ReferenceGovernor
  NominalController
  AugmentationChain
  AttitudeRateInner
  SafetyFilter
  FaultManager
  ControlAllocator
  PlantAndSensors
```

原子模块统一使用`StateFrame`、`ReferenceFrame`、`CommandFrame`、`ModuleDiagnostics`、
`LifecycleContext`和`ParameterSet`。完整组合只存在于Profile，不复制算法源码。

点击“打开图形化模型”时，Profile Resolver必须：

1. 验证插槽数量、输入输出variant、坐标、单位、状态源和车辆数；
2. 解析每个模块对应的Sysblock/Modelica模型、生成代码core和runtime backend；
3. 打开与当前Profile一致的顶层Harness和参数集；
4. 记录模型hash、参数hash、生成代码hash和证据等级；
5. 任一映射缺失时停止，不允许用相似模型或默认控制器替换。

### 3.6 控制器切换边界

默认切换发生在实验开始前：选择或生成新Profile，重新执行模型检查、MIL/SIL、codegen和
对应runtime门禁，然后创建新run。Flight Console不得提供“任意算法立即热切换”。

飞行中切换只由Controller Manager按已验收切换图执行，至少经过：目标Profile校验、参数
加载、状态初始化、影子运行、输出合法性检查、状态迁移、安全点或渐变接管。以下情况必须
拒绝热切换并要求悬停/降落后新建run：

- 输出variant或控制层级不同且没有专用迁移器；
- 积分器、观测器、优化器或神经网络状态无法确定初始化；
- 当前姿态、速度、定位或执行器状态超出切换安全包络；
- 目标Profile缺少对应场景和车辆数的runtime证据；
- 切换会产生两个最终命令生产者，或绕过Safety/Fault Manager。

所有切换、拒绝、回退和降级事件必须写入同一`run_id`时间线。代表性自动降级链可以是
`NMPC -> SE3 -> safe PID -> hover -> land`，但只有每一条边通过验证后才能启用。

### 3.7 必须实现

- 从Registry和Profile Catalog读取可选项，不硬编码算法列表；
- 按兼容性和证据等级过滤、禁用或拒绝组合；
- 读取和保存受控`ParameterSet`；
- 调用Sysplorer模型检查与MWORKS MIL/SIL；
- 显示关键指标和项目标准曲线；
- 一键打开当前run对应的MWORKS原生结果与动画查看器；
- 调用已冻结的codegen和等价性门禁；
- 向Orchestrator提交实验并接收运行结果；
- 从失败run打开对应模型、参数、异常时间段和证据目录。

### 3.8 明确不做

- 不重做Sysplorer图形化模型编辑器；
- 不在APP内实现复杂模型拖拽连线；
- 不重做MWORKS三维动画引擎；
- 不允许跳过MIL/SIL/codegen门禁直接部署；
- 不直接启动ROS命令或发布MAVROS setpoint。

## 4. Flight Console范围

### 4.1 开源优先门禁

正式选型前必须比较至少以下候选类别：

- QGroundControl及其已维护fork/插件模式；
- PX4或ROS无人机地面站/仿真控制台；
- 支持Qt/QML多视图、视频流、MAVLink和自定义面板的开源项目；
- RViz RenderPanel、远程流或受控外部窗口方案；
- UE共享纹理、原生窗口、Pixel Streaming/WebRTC方案。

评价字段至少包括：许可证、维护状态、stars/社区、Windows支持、MAVLink/PX4复用、
Qt/QML扩展性、RViz/UE接入方式、多机支持、打包难度和上游同步成本。

第一版选型已经冻结：Flight Console必须在主窗口内真正嵌入UE，不能把受控外部UE窗口
作为正式产品形态。实现先采用Qt容器接管Windows原生UE渲染窗口；若实测存在不可接受的
闪烁、焦点、DPI或缩放问题，再升级为GPU共享纹理。Pixel Streaming/WebRTC不作为本机
默认路线，受控外部窗口仅保留为调试和显示故障降级路径。

### 4.2 源码边界

```text
References/<candidate>/
  = 只读上游审计和对照

apps/flight_console/vendor/<selected_upstream>/
  = 经许可证和体积审计后复制的冻结上游基线

apps/flight_console/mosim/
  = MoSim自有页面、插件、适配器和资源
```

不得在`References/`直接二次开发。复制必须记录上游URL、commit、许可证、复制清单和
后续同步策略；不得把无关历史、构建产物和大缓存一起复制。

### 4.3 第一版功能

- ExperimentProfile选择、校验和拒绝原因；
- PX4/MAVROS/状态源/控制器健康状态；
- 启动、停止、复位、录制和人工急停入口；
- 参考、实际状态、控制量、姿态误差和安全介入遥测；
- 风速/风向和单电机效能注入，分别显示请求值与实际施加值；
- RViz与UE的准备、绑定、布局、健康、截图和录制；
- 运行事件时间线、指标摘要和证据目录；
- 返回Model Studio并打开对应run。

### 4.4 最终主工作区

Flight Console默认直接进入MoSim工作区，传统QGC Fly/Plan页面放入高级入口，不作为比赛
演示主流程。最终布局冻结为：

```text
顶部: run_id | Profile | Gazebo/PX4/MAVROS/定位/控制器状态 | 录制 | 急停
左侧: 运行准备 | 启动/停止/复位 | 解锁/起飞/任务/降落 | Profile摘要
中央: UE主视图 | 自由/环绕/跟随视角 | 距离调节 | 飞机切换
右侧: 遥测 | 扰动注入 | 故障注入 | 安全/Failsafe | ACK
底部: 事件时间线 | 告警 | 指标摘要 | 截图/录像 | 证据目录
```

UE是主展示视图；点云RViz和三维栅格RViz通过独立按钮受控打开，不常驻挤占中央区域。
无人机生成前保持自由视角，生成后默认环绕跟随。视角模式、目标飞机和环绕距离是三个
独立设置。UE/RViz失败只改变显示健康状态，不能中断控制和日志。

Flight Console可以选择已经发布且通过当前runtime门禁的Profile，但不能编辑原子模块、
底层参数或生成新的控制组合。需要修改组合时必须返回Model Studio。

### 4.5 二维任务地图与场景切换

保留QGC二维地图能力，但使用项目自有`MoSimMapView`和离线地图Provider，不依赖在线地图。
中央区域支持`UE 3D`、`2D Mission Map`和`UE + 2D split view`。地图、任务算法和图层完全
由SceneMapRegistry、MissionAlgorithmRegistry和当前ExperimentProfile驱动。

第一张二维地图为Factory L2，显示静态结构、任务边界、出生点、目标、逐机位置、实际/
规划轨迹，以及算法实际提供的frontier、coverage、assignment和formation图层。后续城市
地图通过新增注册项、资产包和坐标合同扩展，不修改页面结构。

二维地图同时是正式任务编辑面：默认作为右上角`mini_monitor`监视，点击后进入
`expanded_plan`或`expanded_monitor`。放大模式提供目标点、航点、探索/覆盖区域、Geofence、
禁飞区、起飞/降落/返航点、编队中心路线、测距、图层、校验和发布工具。所有编辑先形成
`MissionDraft`，经Profile Validator和Orchestrator后才进入任务Adapter。普通航点、围栏和
Rally Point继续复用QGC原生Mission数据、交互、MAVLink上传下载和ACK能力，由
`PX4MissionAdapter`在Orchestrator授权后执行；FUEL、覆盖、RACER和编队任务分别进入对应
Planner/Formation Adapter。Orchestrator不重写QGC任务系统或规划算法，只统一任务所有权、
校验、适配、幂等提交和证据。QML不得绕过该流程直接发布ROS/MAVROS setpoint或任意
MAVLink控制命令。详细行为和验收见
`Flight Console与二维任务地图详细设计.md`。

QGC完整静态底图是`operator_display_map`，未知探索算法只能读取`live_occupancy_map`。
界面显示先验不代表算法获得先验；该隔离必须由Profile Validator和Run Manifest证明。
地图切换只允许在run开始前进行，并必须同时切换Gazebo world、UE level、QGC底图、坐标
变换、出生点、任务边界、高度带和Geofence。

## 5. 动态禁用规则

### 5.1 控制器

```text
accepted + compatible + runtime evidence valid
  -> enabled

implemented但缺当前运行门禁
  -> visible_disabled(runtime_evidence_pending)

blocked/planned/audit_only
  -> research view only
```

### 5.2 车辆数量

```text
3 UAV:
  第一版enabled；必须使用已验收三机Profile。

4-9 UAV:
  第一版visible_disabled(scale_gate_pending)。
  只有对应数量通过spawn、通信、控制、避障/编队、分离、安全和性能门禁后逐个开放。
```

车辆数量改变必须生成新的Scenario/Profile/hash，不得在运行中无审计热增减。

## 6. Orchestrator最低职责

现有离线适配器只作为契约基线。真实Orchestrator必须实现：

```text
validate_experiment_profile
prepare_run
start_run
stop_run
reset_run
apply_injection
restore_injection
prepare_display_session
attach_display
detach_display
capture_display_evidence
get_run_state
get_telemetry
get_result_packet
open_model_context
```

每次run必须冻结：

```text
run_id
experiment_profile_hash
controller_id/controller_model_hash
parameter_set_hash
generated_code_hash
scenario_id
vehicle_count
state_source_profile
fault/disturbance profile
coordinate/display contract hash
evidence paths
```

GUI进程、显示进程和控制进程必须解耦；任何GUI或显示故障不得阻塞控制和日志。

### 6.1 统一运行状态机与操作权限

Model Studio、Flight Console、Orchestrator和runtime backend必须共享同一个权威运行状态，
GUI不得根据进程存在、窗口可见或单个topic非空自行推断飞行状态。第一版状态机冻结为：

```text
draft
  -> validated
  -> prepared
  -> starting
  -> ready
  -> armed
  -> airborne
  -> mission_running
  -> holding
  -> landing
  -> completed

任一运行态
  -> degraded
  -> failed
  -> emergency
```

状态转换由Orchestrator根据结构化ACK和runtime readiness推进。每次转换至少记录
`run_id`、旧状态、新状态、原因、来源、时间戳和相关证据。超时、非法转换或状态源过期
必须拒绝操作，不得通过GUI本地改状态掩盖。

这里的状态是面向用户和任务的`run_state`，不能替代各子系统自己的生命周期。现有
runtime backend、任务算法和显示会话继续保留各自状态，并由Orchestrator归并：

| 子系统状态 | 含义 | 对`run_state`的影响 |
| --- | --- | --- |
| backend `starting` | ROS/Gazebo/PX4/MAVROS正在启动 | `run_state=starting` |
| backend `running` | 后端进程和基础readiness通过 | 只允许推进到`ready`，不等于已解锁或已起飞 |
| planner `ready/running/degraded` | 规划输入输出合同状态 | 决定任务能否开始或是否进入`holding/degraded` |
| display `healthy/degraded/detached` | UE/RViz/录像状态 | 默认不改变飞行状态，只改变显示证据等级 |
| PX4 armed/landed与高度门禁 | 真实飞行阶段 | 推进`armed/airborne/landing/completed` |

禁止把backend `running`直接显示成“任务运行中”，也禁止用UE飞机可见、Gazebo模型存在或
MAVROS单独连接推进到`airborne`。

| 状态 | 主操作 | 必须禁用的操作 |
| --- | --- | --- |
| `draft/validated` | 编辑或校验Profile | 解锁、起飞、任务、注入 |
| `prepared/starting` | 取消启动、查看预检 | 解锁、起飞、任务、注入 |
| `ready` | 解锁、停止、复位 | 开始任务、飞行中切换控制器 |
| `armed` | 起飞、降落、急停 | 修改地图、车辆数、控制链 |
| `airborne/holding` | 开始/恢复任务、悬停、降落、受控注入 | 复位、切换地图、任意热切换 |
| `mission_running` | 暂停/悬停、降落、受控注入、急停 | 修改Profile、状态源或车辆数 |
| `landing` | 急停、查看状态 | 新任务、普通注入、复位 |
| `completed/failed` | 生成结果、打开证据、基于原Profile新建run | 复用旧run重新飞行 |
| `emergency` | 确定性Failsafe拥有控制权 | 所有非安全操作 |

Flight Console默认只显示一个随状态变化的主操作按钮，并保留独立的悬停、降落和急停。
工程模式可以显示完整状态转换，但不能获得普通模式没有的飞行权限。

### 6.2 运行权威、重连与幂等

Orchestrator是`run_id`、Profile、进程、注入、显示会话和结果包的唯一所有者。两个GUI都是
可重启客户端：GUI退出不得终止runtime，GUI重启后必须通过`run_id`重新附着并读取当前状态，
不得创建同名第二个run或重复发送上一次成功请求。

所有有副作用请求必须携带：

```text
request_id
run_id
expected_run_state
profile_hash
client_timestamp
action
payload
```

Orchestrator必须对同一`request_id`返回相同结果，对过期`expected_run_state`返回冲突，且在
重启后能从run manifest和runtime探针恢复为`attached`、`degraded`或`orphaned`。不能确认
所有权时停止写操作，只允许只读诊断和人工选择接管或清理。

### 6.3 实时遥测数据合同

界面字段不能只写“姿态”“误差”或“控制量”。每个遥测字段必须在机器可读字典中声明：

```text
signal_id
vehicle_id
source_topic_or_artifact
source_layer
frame_id
unit
source_timestamp
receive_timestamp
sample_rate_hz
display_rate_hz
freshness_limit_ms
validity / quality_flags
evaluation_allowed
```

至少区分四类数据：

| 类别 | 示例 | GUI规则 |
| --- | --- | --- |
| 控制输入状态 | PX4融合位置、速度、姿态、角速度 | 明确显示控制器实际使用的来源 |
| 参考和命令 | 规划轨迹、位置指令、姿态推力、执行器命令 | 保留原始参考与安全/故障层修改后命令 |
| 评价truth | Gazebo位置、姿态、碰撞、物理施加值 | 标记`evaluation_only`，不得冒充控制输入 |
| 显示状态 | UE镜像帧、RViz显示健康、视频帧率 | 不进入控制性能指标 |

Flight Console可以降采样显示，但结果包必须保留评价所需的原始时间戳数据。多机遥测按
`vehicle_id`隔离，并同时提供团队级最小间距、编队误差、通信新鲜度和安全状态。字段过期时
显示`stale`，不得保持最后一个正常值而继续显示绿色健康状态。

### 6.4 注入事务与物理ACK

风扰、电机效能、传感器退化和其他故障统一建模为`InjectionTransaction`，而不是GUI滑块
直接写topic。每个事务至少声明：

```text
injection_id
run_id
vehicle_ids
kind
target
waveform: step | ramp | pulse | profile
requested_value
unit
start_condition
duration
ramp_time
composition_rule
safety_limit
restore_policy
```

事务状态为：

```text
requested -> validated -> scheduled -> applied -> verified
          -> restoring -> restored
          -> rejected / partial / failed
```

`request accepted`只说明Orchestrator接收请求，不能显示为故障已经生效。`applied/verified`
必须来自Gazebo插件、wrench service、PX4参数回读或等价物理执行端ACK，并记录实际施加值、
目标对象和生效时间。多个注入只有在Profile声明`composition_rule`时才能叠加；进入
`landing/emergency/failed`后按`restore_policy`自动撤销非安全必需注入。Safety/Failsafe
始终可以否决注入，但必须保留拒绝原因和事件证据。

### 6.5 Profile版本、发布与证据失效

ExperimentProfile、ParameterSet、地图、控制器模型、生成代码和runtime adapter均采用不可变
发布版本。已发布Profile不得原地修改；任何参数、模块顺序、地图、状态源、车辆数或生成代码
变化都必须创建新版本和新hash。

Model Studio至少提供：

- 从已发布Profile复制为草稿；
- 查看字段级diff和依赖hash变化；
- 回滚为历史版本的新副本；
- 显示旧证据因何失效；
- 拒绝使用已不存在、hash不匹配或证据层级不足的依赖。

失效规则至少覆盖：控制器源码或参数变化使其MIL/SIL/codegen证据失效；生成代码或adapter
变化使runtime证据失效；地图坐标合同、碰撞资产或车辆数变化使场景运行证据失效；纯显示
布局变化不得无理由使控制性能证据失效。

### 6.6 显示降级与会话恢复

UE、RViz、MWORKS结果查看器和录像器均是可选显示/证据消费者。显示会话状态与runtime状态
分离：

```text
unprepared -> prepared -> attached -> healthy
                         -> degraded -> detached
```

UE或RViz启动失败时，Flight Console必须显示具体失败原因并允许runtime继续；显示重连消费
最新状态或同一run回放，不向ROS/Gazebo反压。录像失败只降低媒体证据等级，不改变飞行结果。
但当前Profile若把某显示证据声明为人工验收硬门禁，则run结束后状态为`review_required`，
不能静默升级为accepted。

### 6.7 部署拓扑与传感器扩展边界

第一版只保证当前比赛电脑的一键预检、启动、停止、重连和残留清理。部署拓扑是Windows上的
Model Studio、Flight Console、Orchestrator和嵌入式UE，加WSL Ubuntu-20.04中的
ROS1/Gazebo/PX4/MAVROS；本阶段不承担跨机器通用安装器、自动迁移或远程部署验收。
Orchestrator接口不得假定所有进程永久位于同一主机；运行描述中
预留`host_id`、`clock_domain`、`transport`、`endpoint`和`latency_budget_ms`，为后续独立UE
渲染机、远程Gazebo、HIL和真机保留兼容路径。

第一版正式进程间通信冻结为仅绑定`127.0.0.1`的本机Loopback控制API：低频、有副作用的
控制请求使用HTTP/JSON请求响应，实时遥测和状态事件使用版本化WebSocket，UE位姿/渲染更新
使用带`run_id`、时间戳和序号的独立单向低延迟流，结果与证据继续落文件。这里的HTTP是
Windows/WSL及不同语言进程之间的本机IPC实现，不代表网页、浏览器、云服务或外网依赖。

`SensorProfile`继续作为可扩展注册接口，至少能描述MID360、IMU、GPS、定高、RGB/Depth
Camera和真机USB Camera的频率、噪声、延迟、外参、frame与来源。当前Goal不实现视觉闭环，
但GUI、Profile和数据合同不得把传感器集合硬编码为MID360-only。

## 7. 最终用户端到端操作流程

### 7.1 模型设计、MIL和SIL

1. 启动MoSim Model Studio并选择“新建实验”或已验收推荐Profile；
2. 选择场景、任务/轨迹、状态源、车辆数、控制链和参数预设；
3. 查看控制链摘要和兼容性结果，点击“打开图形化模型”；
4. 在Sysplorer中检查顶层Harness和模块连线，点击“模型检查”；
5. 点击“运行MIL”，在MWORKS结果/动画查看器审核轨迹、姿态、控制量和指标；
6. 点击“运行SIL”和“MIL/SIL对比”；失败时返回模型和参数，不进入代码生成。

### 7.2 代码生成与Profile发布

1. 点击“生成代码”，执行固定尺寸C/C++生成、编译、ABI和离线等价性门禁；
2. 页面分别显示MIL、SIL、codegen和目标runtime门禁状态；
3. 通过后点击“发布运行配置”，冻结ExperimentProfile、ParameterSet和全部hash；
4. 点击“进入飞行仿真”，将同一Profile提交给Orchestrator并打开Flight Console；
5. 两个GUI共享同一Profile和run上下文，不要求用户重复选择。

### 7.3 Gazebo/PX4运行与UE/RViz审核

1. Flight Console点击“环境预检”，检查WSL/ROS1、Factory、Gazebo、PX4、MAVROS、状态源、
   控制器、规划器、端口、共享锁和残留进程；
2. 预检通过后点击“启动仿真”，Orchestrator按Launch Plan依次启动真实runtime、显示会话和证据记录；
3. 状态门禁全部就绪后，用户依次点击“解锁”“起飞”“开始任务”；
4. UE中央视图显示Factory和实际飞机状态，Flight Console显示遥测、控制误差和安全状态；
5. 需要工程审核时点击“点云RViz”或“栅格RViz”，关闭显示不影响飞行；
6. 用户可对指定飞机施加风扰、电机效能或故障，界面同时显示请求值、实际值和ACK；
7. 安全操作只通过“悬停”“返航”“降落”“急停”等受控动作进入Orchestrator。

### 7.4 结束、证据回传和再次优化

1. 任务结束后点击“降落”和“结束实验”；
2. Orchestrator停止记录、提取日志、计算指标、保存截图/视频并检查残留；
3. Flight Console显示结果摘要、告警、证据目录和“返回MWORKS分析”；
4. Model Studio按同一`run_id`并列显示MIL、SIL、generated-C和Gazebo/PX4结果；
5. 效果不满足指标时打开对应模型、参数和失败时间段，产生新版本Profile后重复流程。

已验收Profile的普通演示可以从Flight Console直接开始“环境预检”，不强制每次重跑MIL/SIL；
新增控制器、修改控制组合、参数或生成代码时必须从Model Studio完整进入。

### 7.5 基线对比与比赛展示

Model Studio必须提供固定的实验对比入口，而不是要求用户手工打开多份结果。对比组只允许
选择场景、任务、车辆数、状态源、扰动/故障和评价Profile一致的run；不一致字段必须显式
标出，默认不得计算控制器优劣结论。

第一版标准对比为：

```text
官方PID或冻结基线
  vs
选定改进控制器/增强链

相同ScenarioProfile
相同Reference/MissionProfile
相同Disturbance/FaultProfile与随机种子
相同EvaluationProfile
```

标准指标至少包括XYZ和姿态RMSE、峰值误差、稳态误差、超调、调节时间、控制能量、任务
完成率、安全介入次数、故障检测/恢复时间。每个指标可追溯到原始信号、计算版本和run证据；
界面动画和UE视频只作为并列展示，不参与数值排名。比较结果可以生成比赛图表和摘要，但
不得自动改写控制器状态或把单场最好结果升级为普遍结论。

## 8. 实施阶段与验收

### D0 文档与现状冻结

- 本文、功能矩阵、数据契约和目录边界完成；
- 统一运行状态机、按钮权限、幂等重连、遥测字典、注入事务和证据失效规则完成；
- 基线对比指标、显示降级和第一版部署拓扑完成；
- 明确哪些现有控制器用于第一条纵向闭环；
- 不修改并行控制器任务文件。

### D1 Syslab APP可行性门禁

最小原生APP必须证明：窗口、下拉框、禁用态、参数输入、曲线、调用Sysplorer、
读取结果、打开结果查看器、访问本地Orchestrator接口。任一关键能力不存在时停止，
先查官方资料和本地示例，不静默改用Web或Qt替代Model Studio。

当前本机已确认Syslab 26.3.1.7499提供`TyAppDesigner 1.0.9`和
`TyAppBundler 1.0.6`。原生下拉框没有逐项`Enable`接口，因此第一版以“选项可见、
选择后由能力门禁拒绝后续请求、状态区显示原因”实现不可用项。用户重新选择已验收项后
才允许创建请求；不得静默替换用户选择，也不得因此开放未验收组合。

### D2 Flight Console开源选型

- 完成候选审计和评分；
- 冻结上游commit和许可证；
- 形成最小复制清单；
- 完成产品路径下可独立构建的源码副本。

### D3 Orchestrator MVP

- 离线Profile、生命周期、注入和显示会话测试通过；
- 一个已验收控制器可通过同一API进入真实runtime；
- 失败、停止和残留检查可复现。

当前实施状态（2026-07-17）：D3a离线契约已通过，证据位于
`Results/ui_platform/orchestrator_d3a_gate_20260717/`。该切片统一使用`ready`生命周期，
校验Profile与控制器/车辆数一致性，限制CLI命令白名单和项目内证据路径，并确保未配置
真实backend时`start_run`明确返回`runtime_backend_unconfigured`。它没有启动共享
Gazebo/PX4，也不构成D3真实runtime验收。D3仍需绑定声明式、白名单化的项目运行脚本，
完成一次已验收控制器的真实启动、停止、残留检查和同一`run_id`证据后才能关闭。

D3b源码切片已增加`runtime_backend_catalog.json`、固定WSL launcher和stop helper。
当前只允许`px4ctrl_figure8_baseline_v1 + px4ctrl + 1 UAV`映射到项目已有
`run_px4ctrl_basic_gate.sh`；catalog不接受任意`command`或`arguments`。backend创建进程后
首先进入`starting`，不会把“进程存在”冒充`running`。该切片仍需由长驻Orchestrator服务
持有进程，并在共享runtime释放后补MAVROS readiness、停止cleanup和残留实测。

D3c已增加项目内JSON文件队列的长驻服务。两个GUI写入
`Results/ui_platform/orchestrator_requests/`，服务以同一个Orchestrator/backend实例串行处理，
原子写入`orchestrator_responses/`，从而保留run、进程和显示会话所有权。服务限制请求大小、
拒绝符号链接、非对象JSON、未知动作和参数不匹配；同名请求已有响应时不重复执行。
该文件队列是D3契约验证、恢复和诊断通道，不是最终实时主链。正式GUI接入按6.7节迁移到
本机Loopback HTTP控制API和WebSocket遥测；迁移完成前不得用文件轮询延迟声明实时闭环通过。
当前Model Studio D1请求格式尚未携带完整Profile和request id，必须在D4升级后才能接入。

### D4 Model Studio MVP

- 原生Syslab APP使用Registry驱动下拉框；
- 可提交Profile并读取同一`run_id`；
- 可请求打开模型上下文并在结果尚未产生时明确返回不可用；
- MWORKS MIL/SIL/codegen的真实执行归入D6纵向闭环，不由轻量APP重复实现。

当前实施状态（2026-07-17）：D4已通过。Syslab原生APP版本`0.2.0`已从干净目录
打包，Registry/Profile Catalog级联选择、单机与三机`px4ctrl`Profile、4至9机及未验收
控制器拒绝均已验证。三机请求得到稳定`run_id`与Profile hash，模型上下文请求被接受，
无结果时返回`result_packet_not_available`。证据位于
`Results/ui_platform/model_studio_d4_gate_20260717/`。该结论仅覆盖APP、Orchestrator
prepare/context/result边界，不证明Gazebo运行或控制性能。

原生GUI复核进一步在干净Syslab Julia REPL中启动当前
`apps/model_studio/native_app/app.jl`。窗口、Registry/Profile目录和单机选择正常显示，
`Prepare run`通过正式文件队列返回`true / run_prepared`，生成
`run-20260717-071006-ec0378d8`。复核同时修复了Julia `Cmd`不接受
`Vector{AbstractString}`的真实回调错误，所有动态参数在构造命令前转为`String`。
截图证据位于`Results/ui_platform/model_studio_native_review_20260717/`。同一REPL重复执行
含`@oodef App`的文件会产生常量重定义，运行流程必须使用干净REPL首次加载，不能以连续
F5替代重启。

### D5 Flight Console MVP

- 复用上游飞控能力并接入MoSim专属页面；
- 完成运行控制、遥测、注入、证据和三机禁用/启用逻辑；
- RViz/UE至少达到受控外部窗口，不能只提供文档或假视图。

当前实施状态（2026-07-17）：D5原生构建与GUI门禁已通过。MoSim已使用QGroundControl
`v5.0.8`官方custom-build扩展点，在`apps/flight_console/mosim/custom/`实现Run、
Telemetry、Injection、Displays和Evidence界面，并通过固定Orchestrator客户端提交请求。
生成overlay不计入冻结上游SHA清单，2638个上游文件仍通过校验。CMake已识别
`Enabling custom build`。项目私有`.tools/flight-console/`已冻结Qt 6.8.3、Ninja 1.13.0、
GStreamer 1.22.12和兼容QGC v5.0.8的PX4-GPSDrivers提交
`8fdef3bc0cb7820119abdb7320ad3992af2e440f`，未污染系统PATH。VS2022 Community、
MSVC 14.44和Windows SDK 10.0.26100参与真实Release构建，最终完成325/325并生成
`build/flight-console-qgc/Release/MoSimFlightConsole.exe`。一键入口
`Scripts/ui/run_flight_console.ps1`从预检清单注入项目私有运行依赖并复用已有实例。

原生窗口首次启动后完成Windows位置/防火墙和QGC公制/多旋翼初始化门禁；Run、Telemetry、
Inject、Displays、Evidence五页均在2560x1440、125% DPI下完成可见性复核，没有重叠或截断。
Windows位置权限按当前仿真定位边界拒绝，Flight Console联网按MAVLink/Orchestrator需求允许。
构建与源码回归10项通过，证据位于
`Results/ui_platform/flight_console_native_review_20260717/`。D5状态提升为
`native_review_passed`。该结论不证明MAVLink已连接、Gazebo飞行、实时注入、RViz/UE绑定或
D6同一run闭环；这些仍必须在D6运行验收中单独证明。

### D6 单机完整纵向闭环

推荐首条链：Factory L2、单机、已验收MWORKS generated-C控制器、PX4融合状态、
起飞/悬停/8字/降落、风扰与单电机效能实验。必须完成模型到代码、运行、指标、
回到模型上下文的同一run证据。

当前实施状态（2026-07-17）：首条generated-C启动链的源码与Profile门禁已接通。
新增`cascade_pid_figure8_generated_c_v1`，只允许已验收`cascade_pid`控制器和单机，
并映射到白名单operation `cascade_pid_figure8_single`；operation复用真实Sunray
`run_px4ctrl_basic_gate.sh figure8`，以`PX4CTRL_CORE_PROFILE=cascade_pid`选择现有
MWORKS generated-C后端。Profile Validator和Orchestrator定向测试通过。该门禁不证明
本轮Gazebo飞行、实时注入、指标回传或D6闭环完成；原生Flight Console构建和同一run
Gazebo证据仍是进入D6运行验收的必要条件。

D6运行编排切片已进一步接入run-local sidecar。backend只有在sidecar同时观察到
MAVROS connected、新鲜里程计、控制器指令和现有P7执行器插件遥测后，才把生命周期从
`starting`提升为`running`；sidecar持续写`RUNTIME_STATUS.json`和`telemetry.json`。
风速通过Gazebo ROS官方`/gazebo/apply_body_wrench`持续施加等效气动力，电机效能复用
P7的`mosim_gazebo_ftc_actuator_plugin`，两类注入均使用run-local命令和ACK区分请求值与
实际施加值。显示会话也已拆成`prepare`与`attach/detach`，后者只调用固定RViz/UE启动器，
显示失败不改变runtime状态。D6场景现由
`Config/scenarios/ui/factory_l2_single_figure8.json`显式冻结Factory world、模型路径、起点和
局部8字范围，不再沿用旧柱状地图口径。当前定向源码测试通过，但共享ROS/Gazebo/PX4
运行时正被P8三机任务占用，因此本轮尚未执行同一run飞行、注入和显示人工验收，D6仍为
`source_ready_live_gate_blocked`。

Factory单机运行时的Gazebo模型名是`uav1`，风扰必须明确施加到`uav1::base_link`；sidecar
仅在未显式配置时才按`uav1`、`sunray150`顺序从`/gazebo/model_states`回退解析。D6 live
gate必须保存`apply_body_wrench`成功ACK及注入前后遥测，不能用命令投递成功替代物理施加成功。

首次有界live尝试`run-20260717-055004-819a3654`在启动ROS/Gazebo前由共享运行锁拒绝：
P8的`p8_formation_mode1_gazebo_r5_20260717`已取得Sunray ROS1运行权，D6 wrapper以退出码11
结束。证据位于`Results/ui_platform/flight_console_d6_single_runtime_gate_20260717/`。该结果
仅证明并发保护有效，不是控制器、注入、遥测或闭环失败；必须等待P8自然释放后新建run重测。

共享运行锁不能作为唯一冲突真值：P8 r5运行期间曾出现Gazebo、PX4、MAVROS与px4ctrl仍
存活但锁文件已消失。Orchestrator wrapper因此在底层gate和sidecar启动前增加关键进程
冲突门禁；只有锁与关键进程均释放时才允许新run进入D6/D7 live gate。

D6第二次live尝试`run-20260717-055731-c936a31f`进入真实启动后暴露两个集成缺口：sidecar
使用了Ubuntu 20.04 Python 3.8不支持的`Path.write_text(newline=...)`，且wrapper只设置
Factory world却仍沿用Sunray默认planning launch。修复口径是使用Python 3.8兼容的文件
写入API，并同时冻结Factory world与项目内`factory_l2_sunray_px4_gazebo.launch`；本次
退出码4发生在MAVROS连接前，不构成控制器跟踪或注入结论。

D6第三次live尝试`run-20260717-060951-d59bbeb1`在已确认共享进程释放后发起，但P8
`p8_formation_mode2_gazebo_r1_20260717`几乎同时取得共享runtime。wrapper的关键进程门禁
检测到`gzserver/rosmaster/PX4/MAVROS/sunray_gate`后以退出码11拒绝，未启动第二套ROS master。
run-local证据位于
`Results/ui_platform/orchestrator_runs/run-20260717-060951-d59bbeb1/`。该次仍只证明并发保护，
D6 live验收继续等待共享runtime自然释放后重跑。

D6第四次live尝试`run-20260717-061615-1289d12e`又与P8
`p8_formation_mode3_gazebo_r1_20260717`在检查后、底层gate启动前发生竞争，并被进程门禁
以退出码11安全拒绝。这证明单独的“先检查进程再启动”存在TOCTOU窗口。Orchestrator wrapper
现先原子获取项目共享runtime lock，再检查关键进程；底层basic/swarm gate通过继承同一nonce
安全进入，父wrapper在cleanup时统一释放。P8运行期间的只读锁探针能够返回其真实`run_id`
与owner PID，且不会启动sidecar或ROS进程。后续D6/D7 live必须使用该原子预留路径。

### D7 三机完整纵向闭环

- 车辆数选择为3；
- 三机启动、状态、轨迹、注入、RViz/UE和证据统一显示；
- 不把三机到达目标冒充编队算法通过。

当前源码门禁（2026-07-17）：Orchestrator已白名单化
`factory_l2_three_uav_swarm_formation_v1`，固定调用现有
`run_px4ctrl_ego_swarm_gate.sh`的Factory L2三机Swarm-Formation入口。sidecar按
`uav1/uav2/uav3`独立订阅MAVROS状态、里程计、px4ctrl目标姿态、位置指令和执行器插件遥测，
readiness要求三机全部满足；`telemetry.json`按`vehicles[]`输出逐机状态。风扰与电机效能
命令在三机运行时必须携带合法`vehicle_id`，Gazebo wrench body和执行器command topic均只
指向所选飞机，ACK也回写`vehicle_id`。Flight Console注入页已增加目标飞机选择，4至9机
仍保持禁用。定向源码回归35项通过；尚未完成三机同一run启动、逐机注入ACK、RViz/UE绑定
和人工审核，因此D7状态是`source_ready_live_gate_pending`，不得声明三机GUI闭环完成。

### D8 3至9机编队扩展

按4、5、6、7、8、9逐级验收，不一次性解除全部禁用。每级至少验证启动资源、
通信命名空间、最小间距、编队误差、障碍穿越、安全介入、运行稳定性和显示性能。

## 9. AI助手产品设计与权限边界

### 9.1 单一助手、双入口

AI助手不是第三个独立GUI。Model Studio和Flight Console右上角显示同一个助手入口，打开
一致的侧边栏并共享当前Profile、run和证据上下文，但根据运行阶段使用不同权限：

```text
Model Studio:
  解释模型与控制链
  分析MIL/SIL/Gazebo差异
  定位失败时间段
  对比控制器和参数
  形成参数/Profile修改建议

Flight Console:
  汇总遥测、告警和安全介入
  解释扰动/故障响应
  建议打开相关RViz或证据
  建议悬停、返航、降落或结束实验
  生成本次实验摘要
```

Neural PID、Neural-SMC、RBF/NN和RL调度是控制算法模块，进入Registry、模型、codegen和
runtime证据链；AI助手是人机协作和实验分析层，两者不得混报。

### 9.2 上下文、建议、确认和审计

预留只读上下文：当前Profile、模型、参数、run、指标、事件和证据。预留受控建议对象：

```text
analysis_request
diagnosis_report
proposed_parameter_patch
proposed_experiment_profile
human_confirmation
execution_audit
```

当前Goal不接入模型服务、不实现聊天窗口、不允许AI直接修改模型或启动飞行。

后续实现也必须遵循：

```text
只读上下文
  -> 结构化分析
  -> proposed_parameter_patch / proposed_experiment_profile / proposed_safe_action
  -> 人工确认
  -> Orchestrator重新校验
  -> 受控执行
  -> execution_audit
```

AI永远不能直接发布setpoint、控制电机、绕过Profile Validator、解除Safety/Failsafe、修改
已发布Profile或在飞行中任意切换控制器。紧急状态下AI只能提示，既有确定性Failsafe仍是
安全权威。

## 10. 产品目录

```text
apps/
  model_studio/          Syslab原生APP源码、资源和打包入口
  flight_console/
    vendor/              选中上游的冻结最小副本
    mosim/               MoSim自有Qt/QML/插件代码

src/
  orchestration/         GUI无关的真实Orchestrator

Config/
  control_platform/      Registry、handoff和注入契约
  profiles/              ExperimentProfile及兼容性

Results/ui_platform/     PoC、测试、截图、延迟和验收包
```

在目录迁移完成前，现有`Scripts/control_platform/`可作为兼容入口，但新产品GUI代码
不得继续散落到根目录CMD或`References/`。

## 11. 完成定义

本Goal只有同时满足以下条件才可关闭：

1. Model Studio是可启动的MWORKS.Syslab原生APP；
2. Flight Console来自审计后的开源底座并在项目自有源码路径二次开发；
3. 两个GUI通过真实Orchestrator共享同一Profile、run和证据；
4. 单机和3机非AI纵向闭环均有可复现运行证据；
5. RViz和UE均可从Flight Console受控打开/绑定，且显示失败不阻塞runtime；
6. 控制器和3至9机禁用逻辑由机器状态驱动；
7. 3至9机编队完成逐级可行性研究和有界运行验证；
8. 所有任务自有改动完成测试、精确提交、推送和上游验证。
9. 两个GUI遵循同一运行状态机、遥测字典、注入事务和幂等恢复合同；
10. Model Studio能对满足同场景约束的基线与改进run生成可追溯指标对比。
