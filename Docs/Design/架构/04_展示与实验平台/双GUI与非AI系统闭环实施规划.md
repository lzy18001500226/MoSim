# MoSim双GUI与非AI系统闭环实施规划

> 状态：长期Goal实施入口，2026-07-17。
>
> 本文冻结MoSim Model Studio、MoSim Flight Console和Orchestrator的产品边界、
> 实施顺序与验收门禁。当前Goal不实现AI助手，只预留上下文和受控操作接口。

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

### 3.1 第一版页面

Model Studio不显示庞大模型树，采用级联下拉框和少量标签页：

```text
场景 -> 任务/轨迹 -> 控制器族 -> 控制器 -> 增强层 -> 安全层
     -> 状态源 -> 参数预设 -> 车辆数量

标签页:
  实验配置
  仿真摘要
  结果曲线
  代码生成
  运行回传
```

### 3.2 必须实现

- 从Registry和Profile Catalog读取可选项，不硬编码算法列表；
- 按兼容性和证据等级过滤、禁用或拒绝组合；
- 读取和保存受控`ParameterSet`；
- 调用Sysplorer模型检查与MWORKS MIL/SIL；
- 显示关键指标和项目标准曲线；
- 一键打开当前run对应的MWORKS原生结果与动画查看器；
- 调用已冻结的codegen和等价性门禁；
- 向Orchestrator提交实验并接收运行结果；
- 从失败run打开对应模型、参数、异常时间段和证据目录。

### 3.3 明确不做

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

## 7. 实施阶段与验收

### D0 文档与现状冻结

- 本文、功能矩阵、数据契约和目录边界完成；
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

### D4 Model Studio MVP

- 原生Syslab APP使用Registry驱动下拉框；
- 完成一个控制器的MIL/SIL/codegen；
- 可提交和读取同一`run_id`。

### D5 Flight Console MVP

- 复用上游飞控能力并接入MoSim专属页面；
- 完成运行控制、遥测、注入、证据和三机禁用/启用逻辑；
- RViz/UE至少达到受控外部窗口，不能只提供文档或假视图。

### D6 单机完整纵向闭环

推荐首条链：Factory L2、单机、已验收MWORKS generated-C控制器、PX4融合状态、
起飞/悬停/8字/降落、风扰与单电机效能实验。必须完成模型到代码、运行、指标、
回到模型上下文的同一run证据。

### D7 三机完整纵向闭环

- 车辆数选择为3；
- 三机启动、状态、轨迹、注入、RViz/UE和证据统一显示；
- 不把三机到达目标冒充编队算法通过。

### D8 3至9机编队扩展

按4、5、6、7、8、9逐级验收，不一次性解除全部禁用。每级至少验证启动资源、
通信命名空间、最小间距、编队误差、障碍穿越、安全介入、运行稳定性和显示性能。

## 8. AI预留但不实现

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

## 9. 产品目录

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

## 10. 完成定义

本Goal只有同时满足以下条件才可关闭：

1. Model Studio是可启动的MWORKS.Syslab原生APP；
2. Flight Console来自审计后的开源底座并在项目自有源码路径二次开发；
3. 两个GUI通过真实Orchestrator共享同一Profile、run和证据；
4. 单机和3机非AI纵向闭环均有可复现运行证据；
5. RViz和UE均可从Flight Console受控打开/绑定，且显示失败不阻塞runtime；
6. 控制器和3至9机禁用逻辑由机器状态驱动；
7. 3至9机编队完成逐级可行性研究和有界运行验证；
8. 所有任务自有改动完成测试、精确提交、推送和上游验证。
