# UE渲染镜像桥接方案

> 状态：展示与实验平台专题设计，2026-07-01。
>
> 本文回答“MoSim是否采用AirSim式UE仿真、Gazebo+PX4与UE如何分工、第一版桥接怎么做”。

## 1. 目标和边界

MoSim第一版UE路线是单向渲染镜像，不是替换Gazebo/PX4/Sunray的仿真内核：

```text
Gazebo / PX4 / MAVROS / ROS1 / Sunray
  -> 产生plant、飞控、状态、轨迹、点云、地图、日志和metrics
  -> ROS1 sidecar或日志回放桥接
  -> UE只消费状态帧并渲染机体、场景、轨迹、相机和多机总览
```

权威边界：

| 层 | 拥有权威 | 不拥有权威 |
| --- | --- | --- |
| Gazebo/Sunray/PX4/MAVROS/ROS1 | plant、传感器、飞控状态、控制闭环、truth、日志和metrics | 高质量最终展示画面 |
| RViz | 点云、TF、轨迹、局部地图和FAST-LIO/规划审核 | 控制器成功指标 |
| UE | 渲染、视频、第一视角、多机总览、场景一致性人工审核 | 控制、定位、规划、truth指标和闭环成功 |
| QGC/Web | 操作、状态观察、Profile选择入口 | 绕过Orchestrator直接改控制权 |

因此，AirSim、RflySim3D和本地`References/UE_ROS/`项目只作为设计参考：学习坐标转换、actor同步、相机/传感器组织、ROS消息绑定和渲染解耦模式。当前不把AirSim或ROS2 UE插件切换成MoSim主线运行内核。

## 2. 为什么先做单向镜像

AirSim/PX4/ROS联合仿真常把UE作为渲染和传感器场景，并由PX4/ROS承担飞控与上层算法。MoSim当前已经冻结为ROS1 Sunray/Gazebo/PX4/MAVROS/px4ctrl最小大系统闭环；如果直接把UE接进控制或传感器闭环，会引入三个风险：

```text
1. 控制闭环权威漂移：漂亮UE画面容易被误当成Gazebo/PX4成功；
2. 通信和时间同步复杂度过早上升：UE帧率、渲染卡顿和编辑器状态不应阻塞控制；
3. 路线漂移：项目会从MWORKS控制平台变成通用UE机器人仿真项目。
```

第一版只做单向镜像，可以先得到展示价值，同时保留当前可验收的控制/定位/规划证据链。

## 3. 总体分层

UE展示平台不要按“导出一张离线地图”理解，而要按“数据驱动展示运行时”设计。
第一版拆成四个互相解耦的子系统：

| 子系统 | 责任 | 不负责 |
| --- | --- | --- |
| Scene Base | Factory静态场景、坐标原点、可视背景、可选碰撞/占据对齐 | 产生运行状态、控制闭环或planner truth |
| Data Bridge | 从ROS1/Gazebo/PX4/MAVROS/Sunray读取状态帧、轨迹、事件和profile，并转成UE可消费流 | 反写setpoint、模式、参数、truth或actor transform |
| UE Runtime Display | 按数据流渲染每机第三视角、Global Overview、姿态残影、轨迹线、目标点和事件标记 | 修改控制、定位、规划或评价结果 |
| Evidence Export | 输出UE截图/视频/manifest，并与RViz/log/metrics证据绑定 | 用漂亮画面替代工程证据 |

关键设计原则：

```text
map_import_is_scene_base_only: true
data_bridge_is_required_for_runtime_display: true
ue_is_consumer_only: true
control_feedback_from_ue: forbidden in Stage 1
```

因此，Factory L2静态导入只是展示/实验平台的底座；没有Data Bridge，UE就是空场景。
反过来，即使Factory L2尚未完全通过，也可以先用简单场景或占位背景验证真实run的
replay和live mirror数据链路。不要让地图导入阻塞UE数据桥接设计。

## 4. 第一阶段数据流

第一阶段推荐两种输入模式，优先做离线/旁路验证，再进入实时旁路：

```text
Mode A: log replay
  ROS/PX4/Gazebo run bundle
    -> extract state/trajectory/vehicle frames
    -> bridge replay file or UDP/WebSocket stream
    -> UE playback actor
    -> screenshot/video/manifest

Mode B: live sidecar mirror
  ROS1 topics
    -> bridge sidecar subscribes selected topics
    -> timestamped frame stream
    -> UE actor pose and display components
  -> optional recording
```

推荐顺序：

```text
1. replay file first:
   existing run bundle -> ue_render_frame.jsonl -> UE playback actor

2. live sidecar second:
   ROS1 topics -> bridge sidecar -> UDP/WebSocket/TCP stream -> UE runtime actor

3. scene base alignment in parallel:
   Factory map/import assets -> scene_id/map_id binding -> visual review background
```

这样做的原因是：replay文件能在不碰实时控制链路、不依赖UE窗口稳定性、不阻塞Gazebo/PX4
的情况下验证坐标、时间戳、姿态和多机轨迹。live sidecar只在replay契约稳定后进入。

第一阶段不得出现以下反向链路：

```text
UE直接发布MAVROS setpoint；
UE直接改PX4模式、解锁或参数；
UE truth直接喂FAST-LIO、planner或controller；
UE actor transform反写Gazebo/PX4状态；
UE截图或视频替代RViz/topic/log/metric证据。
```

## 5. 桥接帧契约

桥接帧至少包含：

```text
schema: mosim.ue_render_frame.v1
run_id
sequence
timestamp_ros_s
source_profile
vehicle_id
frame_id
child_frame_id
position_m
orientation_quat_xyzw
linear_velocity_mps
angular_velocity_radps
trajectory_reference_id
controller_profile
planner_profile
state_source_profile
display_profile
claim_boundary
```

可选字段：

```text
motor_command
safety_state
planner_state
camera_pose
point_cloud_summary
map_id
scene_id
event_markers
```

桥接输出必须保留原始时间戳和profile信息。UE端可以插值、丢帧或平滑显示，但不得改写原始运行证据。

每个stream还必须有manifest，至少记录：

```text
schema: mosim.ue_render_stream_manifest.v1
run_id
source_bundle
source_topics_or_files
scene_id
map_id
vehicle_asset_profile
coordinate_transform_profile
timebase_profile
transport_profile
drop_or_interpolation_policy
evidence_links
claim_boundary
```

桥接帧和manifest是UE显示链路的最小可验收产物。没有manifest，UE截图只能算临时观察，
不能进入正式review bundle。

## 6. 坐标、单位和时间

第一版必须把转换集中在bridge adapter或UE显示组件里，不改Gazebo/ROS/PX4/MWORKS原始语义。

最低要求：

```text
ROS/Gazebo/PX4侧保持米、弧度、ROS时间戳和原始frame语义；
UE侧使用厘米和UE坐标系；
每个stream manifest记录坐标转换、单位转换、map/scene绑定和外参版本；
每帧保留sequence和timestamp，UE渲染慢时丢弃旧帧，不反压控制链路；
同一次run中不得混用未标注的ENU/NED/body/world速度语义。
```

如果要把UE场景几何导出给Gazebo/RViz/PCD/occupancy，必须进入第二阶段场景真值契约；不能在第一阶段镜像里让planner读取UE全局地图。

## 7. 传输方式选择

第一版不要一开始就把UE做成完整ROS节点。先按调试难度和风险分三档：

| 档位 | 方式 | 适用场景 | 风险 |
| --- | --- | --- | --- |
| T0 | JSONL replay文件 | 最小验证、离线视频、坐标/时间契约调试 | 非实时 |
| T1 | UDP/WebSocket/TCP sidecar | 10-30Hz姿态轨迹、低耦合live mirror | 需要丢帧/重连策略 |
| T2 | UE内ROS插件/节点 | 后续复杂互动、传感器或ROS生态深集成 | 容易引入ROS2/UE平台漂移 |

当前默认：

```text
first_target: T0 replay
second_target: T1 live sidecar; 10Hz is the minimum contract and 30Hz is the current Factory review default
defer: T2 UE-native ROS plugin adoption
```

T1只传显示所需状态帧。若UE帧率低于输入速率，UE端丢弃旧帧并显示最新帧，不允许反压ROS、
Gazebo、PX4、MAVROS或planner进程。

## 8. 本地参考项目怎么用

`References/UE_ROS/`下的项目只作为实现模式参考：

| 参考 | 可借鉴 | 当前不直接采用的原因 |
| --- | --- | --- |
| `TempoROS` | UE5内ROS节点、topic/actor绑定、坐标转换和消息封装 | 偏ROS2/Humble；当前P0是ROS1 |
| `rclUE` | UE插件式ROS2通信、Actor组件组织 | 偏ROS2；不应重开当前主线 |
| `RapyutaSimulationPlugins` | 机器人Actor、ROS接口和仿真资产组织 | 偏大型ROS2仿真框架；当前只需镜像旁路 |
| `turtlebot3-UE-devel` | 简单机器人UE/ROS集成模式 | 场景和机器人域不匹配，只作最小示例 |

当前优先实现ROS1 sidecar到UE的窄桥接，而不是把UE直接变成ROS2仿真平台。

## 9. 验收门禁

第一阶段通过标准：

```text
1. 同一个run_id有Gazebo/PX4/MAVROS/RViz/log/metrics证据；
2. bridge manifest记录输入topic或replay文件、转换策略、UE map和vehicle asset；
3. UE视频或截图显示的机体运动与run日志时间范围、起降/轨迹阶段一致；
4. UE端卡顿、丢帧或窗口问题不会影响控制、定位、规划进程；
5. 交付报告明确写明UE evidence is display-only。
```

失败或禁止声明：

```text
只有UE非空画面，不能声明闭环成功；
只有UE轨迹线，不能声明planner成功；
UE显示坐标修正，不能声明ROS/Gazebo状态源修正；
UE truth导出未通过契约，不能进入规划或评价；
ROS2 UE插件跑通，不能替代当前ROS1/Sunray/Gazebo/PX4主线。
```

## 10. 阶段顺序

Factory是第一张正式UE地图，但UE平台不能只做离线地图导入。Stage 0和Stage 1
可以并行推进：Stage 0解决场景底座，Stage 1解决真实run数据如何进入UE。若两者冲突，
优先保证Stage 1的数据契约和replay链路，因为没有数据桥接的UE只是空壳。

阶段推进顺序：

```text
Stage 0: Factory L2 static import to Gazebo
  -> UE visual mesh / collision mesh / semantic manifest
  -> Gazebo world/model assets
  -> RViz PCD/occupancy alignment
  -> user review bundle

Stage 1: one-way UE rendering mirror and Global Overview
  -> T0 log replay and ue_render_frame.jsonl
  -> UE playback actor
  -> multi-UAV attitude trail display
  -> T1 live sidecar mirror at the declared review rate (Factory default 30Hz)
  -> video/review manifest

Stage 2: UE scene truth export and alignment
  -> optional improved scene validation artifacts
  -> not used as live truth source

Stage 3: optional UE sensor回灌
  -> RGB/depth/LiDAR/semantic frame
  -> timestamp/extrinsic/delay/noise contract
  -> 不通过门禁不得进入FAST-LIO/planner/controller

Stage 4: QGC/UE experiment console
  -> Profile选择和状态显示
  -> 只发送受Orchestrator校验的命令
  -> 所有状态以ROS/PX4/MWORKS echo为准
```

任何阶段都不得改变当前事实：控制、plant、定位、规划和评价先由Gazebo/PX4/MAVROS/ROS1/RViz/logs证明；UE负责让结果可看、可演示、可审核。

Factory L2导入和UE Global Overview的详细门禁见
`Docs/Design/架构/04_展示与实验平台/Factory地图导入与全局态势视图.md`。
