# 17. 项目组概述：rclUE、RapyutaSimulationPlugins、TempoROS、turtlebot3-UE

这四个项目不能并列理解。它们实际属于两条不同路线：

```text
Rapyuta 路线
├── rclUE
│   ROS 2 与 Unreal Engine 的底层通信插件
├── RapyutaSimulationPlugins
│   建立在 rclUE 上的机器人、传感器和仿真框架
└── turtlebot3-UE
    使用前两者构建的完整示例、测试和演示工程

Tempo 路线
└── TempoROS
    另一套将 ROS 2 直接嵌入 Unreal Engine 的底层插件
```

最简单的类比是：

```text
rclUE ≈ UE里的ROS 2通信基础库
RapyutaSimulationPlugins ≈ UE机器人仿真框架
turtlebot3-UE ≈ 完整样板工程

TempoROS ≈ rclUE的另一种现代实现路线
```

这四者中，真正可能成为 CoSim 运行依赖的是：

```text
TempoROS
或
rclUE
```

RapyutaSimulationPlugins更适合作为高层架构参考，`turtlebot3-UE`则主要用于学习、验证和抄作业式源码追踪，不应该成为 CoSim 的基础依赖。

---

# 17.1 它们解决的核心问题

CoSim已经确定：

```text
Gazebo / JSBSim / MuJoCo
    负责权威动力学

UE
    负责高质量显示、动画和可选视觉传感器
```

于是必须解决：

```text
仿真器里的车辆状态
    如何进入UE？

UE里的相机、LiDAR、交互事件
    如何进入ROS 2？

UE怎样发布/clock和TF？

UE怎样动态生成机器人？

多个机器人怎样命名、发现和控制？

UE在Windows，ROS在Linux时怎么通信？
```

这正是这四个项目覆盖的范围。

但必须先区分两种架构。

## 直接嵌入ROS 2

```text
UE进程
├── Unreal Engine
├── ROS 2 Client Library
├── DDS
└── ROS节点
```

优点：

```text
UE本身就是ROS 2节点
不需要独立转换进程
可以直接使用topic、service、action和TF
```

缺点：

```text
ROS 2库必须和UE一起编译、链接和打包
容易出现依赖、编译器、RTTI、异常和DLL冲突
UE崩溃会同时带走ROS通信
```

`rclUE`和 `TempoROS`都属于这条路线。

## 外部Bridge

```text
UE
    ↓ 自定义UDP / Shared Memory / gRPC
Bridge进程
    ↓ ROS 2
ROS系统
```

优点：

```text
UE完全不依赖ROS
Windows和Linux更容易解耦
UE或ROS升级不会直接影响另一边
```

缺点：

```text
多一次序列化和进程通信
需要维护自己的协议
TF、QoS、Service等需要重新封装
```

CoSim最终不应二选一，而应同时保留两种模式：

```text
CoSim Renderer Protocol
    永远存在、与ROS无关

CoSim ROS Bridge
    可选启用
```

---

# 17.2 rclUE

## 17.2.1 定位

rclUE是Rapyuta Robotics开发的ROS 2—Unreal Engine插件。它不依赖外部 `rosbridge` WebSocket进程，而是把ROS 2客户端能力直接放进UE插件中，并将ROS节点、发布器、订阅器、服务和Action映射成UE可以管理的对象。项目采用Apache 2.0许可证。([GitHub](https://github.com/rapyuta-robotics/rclUE "GitHub - rapyuta-robotics/rclUE · GitHub"))

核心关系是：

```text
UE Actor
    ↓ 挂载
UROS2NodeComponent
    ├── Publisher
    ├── Subscriber
    ├── Service Client
    ├── Service Server
    ├── Action Client
    └── Action Server
```

rclUE的文档明确把ROS 2 Node实现成UE的 `ActorComponent`，而Publisher、Subscriber等则封装成 `UObject` 或相应的ActorComponent，并通过UE Delegate触发回调。([rclUE](https://rclue.readthedocs.io/en/latest/design.html "rclUE Design — rclUE 0.1 documentation"))

---

## 17.2.2 为什么rclUE选择rcl/rclc，而不是rclcpp？

这是rclUE最重要的设计决策。

Unreal Engine有自己的：

```text
UObject
Actor
ActorComponent
反射系统
垃圾回收
UPROPERTY
Blueprint
```

而 `rclcpp` 本身也大量使用：

```text
C++继承
智能指针
模板
执行器
RTTI
异常
```

rclUE认为两套高度“有主见”的C++对象体系直接叠加容易冲突，因此选择较低层的C接口 `rcl/rclc`，然后自己建立适合UE对象模型的包装层。([rclUE](https://rclue.readthedocs.io/en/latest/design.html "rclUE Design — rclUE 0.1 documentation"))

可以理解为：

```text
ROS 2底层C API
    ↓
rclUE包装
    ↓
UObject / ActorComponent
    ↓
Blueprint / UE Editor
```

这样更贴合UE生命周期，但代价是：

```text
很多rclcpp现成能力要自己重新包装
消息、服务和Action需要生成UE对应类型
维护成本更高
```

---

## 17.2.3 消息支持方式

rclUE仓库包含一套裁剪和预编译的ROS 2库，相关ROS库及消息代码由独立的 `UE_tools` 项目自动生成。它不是直接链接电脑中 `/opt/ros/...` 下的完整ROS安装。([GitHub](https://github.com/rapyuta-robotics/rclUE "GitHub - rapyuta-robotics/rclUE · GitHub"))

结构大致为：

```text
UE_tools
    ↓
构建ROS 2库
生成消息C/C++代码
生成UE包装类型
    ↓
rclUE/ThirdParty/ros
```

这使rclUE可以随UE项目一起分发，但也带来一个明显问题：

> 更换ROS版本或增加自定义消息，不只是重新 `colcon build`，还可能需要重新生成并打包rclUE中的ROS依赖。

---

## 17.2.4 当前平台兼容性

rclUE官方仓库当前仍将Linux作为主要平台，明确写着Windows暂不支持。官方分支说明主要围绕ROS 2 Foxy/Humble、Ubuntu 20.04/22.04和UE 5.1附近展开，同时存在实验性Jazzy相关分支；其配套 `turtlebot3-UE` 分支矩阵则列出了UE 5.1、5.3、5.4和5.5组合。([GitHub](https://github.com/rapyuta-robotics/rclUE "GitHub - rapyuta-robotics/rclUE · GitHub"))

对你的情况，这一点很关键：

```text
UE运行在Windows：
    rclUE不是优先选择

UE运行在Ubuntu：
    可以研究和使用
```

此外，rclUE仓库没有正式GitHub Release，主要依赖分支组合确定兼容版本，因此版本锁定和源码构建管理会比较重要。([GitHub](https://github.com/rapyuta-robotics/rclUE "GitHub - rapyuta-robotics/rclUE · GitHub"))

---

## 17.2.5 rclUE值得CoSim吸收什么？

### ROS对象与UE对象对应关系

```text
ROS Node
    → ActorComponent

Publisher / Subscriber
    → UObject或ActorComponent

回调
    → UE Delegate
```

这种设计让ROS通信能够自然挂载到任意UE Actor。

### Blueprint支持

ROS发布器、订阅器和服务可以通过UE组件和Blueprint使用，非ROS开发者不必理解完整的rclcpp编程模型。([rclUE](https://rclue.readthedocs.io/en/latest/examples.html?utm_source=chatgpt.com "Examples — rclUE 0.1 documentation"))

### 低层ROS与高层机器人框架分离

rclUE只解决ROS通信，不负责具体机器人、传感器和仿真世界。这种边界是正确的：

```text
rclUE：
    通信

RapyutaSimulationPlugins：
    机器人仿真
```

CoSim也应该保持：

```text
CoSimROS：
    通信

CoSimView：
    车辆与场景

CoSimRendererProtocol：
    平台内部显示协议
```

---

## 17.2.6 rclUE不应照搬什么？

### 不要让消息类型侵入UE业务代码

如果每个Actor都直接操作：

```text
geometry_msgs
sensor_msgs
nav_msgs
```

那么UE前端会和ROS 2强耦合。

建议改为：

```text
ROS Message
    ↓ CoSimROS Converter
CoSim RenderState
    ↓
UE Actor
```

### 不要由rclUE负责CoSim权威时间

rclUE只是通信插件。CoSim的时间必须来自：

```text
CoSim Orchestrator
```

而不是由UE编辑器帧率决定。

### 不要为Windows强行维护rclUE私有Fork

你们UE大概率需要Windows开发和运行。为了使rclUE支持Windows而维护大量第三方库、DLL和编译器兼容补丁，成本可能高于直接选择TempoROS或使用外部Bridge。

---

# 17.3 RapyutaSimulationPlugins

## 17.3.1 定位

RapyutaSimulationPlugins建立在rclUE之上，提供机器人Actor、ROS接口、移动底盘、关节、摄像头、2D/3D LiDAR、仿真管理、实体生成、固定步长和分布式仿真等高层功能。它同样采用Apache 2.0许可证。([GitHub](https://github.com/rapyuta-robotics/RapyutaSimulationPlugins "GitHub - rapyuta-robotics/RapyutaSimulationPlugins · GitHub"))

可以理解成：

```text
rclUE
    提供ROS 2通信

RapyutaSimulationPlugins
    提供机器人仿真语义
```

---

## 17.3.2 机器人组成方式

一个典型机器人由三部分组成：

```text
ARRBaseRobot
    机器人Actor本体

URRRobotROS2Interface
    ROS 2节点、Publisher、Subscriber、Service、Action

ARRBaseRobotROSController
    控制ROS接口启动和机器人控制权限
```

官方设计中，机器人可以直接放入UE场景，也可以通过 `/SpawnEntity` 服务从ROS侧动态生成，并传入机器人名称、Namespace和JSON参数。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/devel/overview.html "Overview: Robot and GameMode — RapyutaSimulationPlugins 0.1 documentation"))

这个设计非常适合CoSim未来的动态实体系统：

```text
CoSim Orchestrator
    ↓ SpawnEntity
UE
    动态创建固定翼、四旋翼、小车或机器狗Actor
```

---

## 17.3.3 基础机器人接口

Rapyuta基础机器人已经提供：

```text
/cmd_vel
/odom
/joint_states
/joint_commands
```

并鼓励开发者通过继承扩展自己的ROS API。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/devel/overview.html "Overview: Robot and GameMode — RapyutaSimulationPlugins 0.1 documentation"))

这套接口对TurtleBot和机械臂很合理，但对CoSim不能直接照搬。

因为：

```text
固定翼：
    不适合/cmd_vel

四旋翼：
    可能需要VehicleState、Trajectory或MotorState

机器狗：
    需要JointState、FootContact、BodyCommand
```

所以CoSim需要的是领域化接口：

```text
AerialActorInterface
GroundActorInterface
LeggedActorInterface
```

而不是所有机器人统一成 `/cmd_vel`。

---

## 17.3.4 移动系统

RapyutaSimulationPlugins同时提供：

```text
非物理运动组件
    直接移动机器人位姿

物理差速驱动组件
    使用UE物理模拟轮子

运动关节组件
    直接按速度移动关节

物理关节组件
    使用UE Physics Constraint
```

官方文档明确区分了纯运动学移动和考虑物理的差速驱动、运动学关节和物理约束关节。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/latest/components.html "Components and main C++ classes — RapyutaSimulationPlugins 0.1 documentation"))

这对CoSim的启发是：

```text
同一个UE模型可以有不同运行模式

Mirror模式：
    外部物理状态直接驱动Actor

UEPhysics模式：
    UE自己计算运动

Replay模式：
    日志驱动Actor
```

但CoSim默认应该选择：

```text
Mirror模式
```

也就是Gazebo、JSBSim或MuJoCo提供状态，UE只镜像。

---

# 17.4 传感器系统

RapyutaSimulationPlugins提供了可作为机器人组件或独立Actor的传感器，包括：

```text
Camera
    发布sensor_msgs/Image

2D LiDAR
    发布sensor_msgs/LaserScan

3D LiDAR
    发布sensor_msgs/PointCloud2
```

同时提供传感器基类和Publisher基类，方便扩展新的传感器类型。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/latest/components.html "Components and main C++ classes — RapyutaSimulationPlugins 0.1 documentation"))

它的继承结构值得学习：

```text
URRROS2BaseSensorComponent
    ├── Camera
    ├── 2D LiDAR
    └── 3D LiDAR
```

CoSim可以采用类似方式：

```text
UCoSimSensorComponent
    ├── UCoSimCamera
    ├── UCoSimDepthCamera
    ├── UCoSimSemanticCamera
    ├── UCoSimLidar
    └── UCoSimRadar
```

不过不能直接把其3D LiDAR当成MID360完整模型。

Rapyuta提供的是一般化PointCloud2输出框架，而MID360还涉及：

```text
非重复扫描模式
逐点时间戳
视场分布
运动畸变
回波与强度
Livox消息格式
```

所以更适合作为传感器框架参考。

---

# 17.5 仿真世界管理

## 17.5.1 SimulationState

RapyutaSimulationPlugins提供一个仿真管理层，可以通过ROS服务完成：

```text
GetEntityState
SetEntityState
SpawnEntity
SpawnEntities
DeleteEntity
Attach / Detach
```

并使用 `ASimulationState` 管理场景实体。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/devel/overview.html "Overview: Robot and GameMode — RapyutaSimulationPlugins 0.1 documentation"))

这一部分和CoSim Orchestrator非常接近。

CoSim可以吸收为：

```text
CoSimEntityService
    spawn
    delete
    attach
    detach
    query
    reset
```

但其内部调用不应只依赖ROS Service，而应首先是Core接口：

```text
CoSim Core Entity API
    ├── gRPC
    ├── ROS 2 Service
    ├── CLI
    └── UE内部调用
```

ROS只是其中一个适配器。

---

## 17.5.2 固定步长与RTF

RapyutaSimulationPlugins提供自定义固定时间步组件，并允许限制Real Time Factor；它还可以每个仿真Tick发布 `/clock`。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/devel/overview.html "Overview: Robot and GameMode — RapyutaSimulationPlugins 0.1 documentation"))

这证明UE并非只能按显示帧率随意运行，也可以构建固定步长仿真循环。

但CoSim中必须明确：

```text
UE为权威物理：
    UE可以发布/clock

Gazebo、JSBSim为权威物理：
    UE不能发布/clock
```

否则会出现：

```text
Gazebo发布/clock
TempoROS又发布/clock
Rapyuta插件又发布/clock
```

而ROS仿真系统中 `/clock`只能有一个权威发布者。

---

# 17.6 分布式多机器人仿真

RapyutaSimulationPlugins利用UE原生多人游戏的Client—Server架构实现分布式仿真，将机器人放到不同UE客户端中，并通过UE服务器同步世界和管理机器人，从而把负载分散到不同机器。([RapyutaSimulationPlugins](https://rapyutasimulationplugins.readthedocs.io/en/devel/distributed_simulation.html?utm_source=chatgpt.com "Distrubuted Simulation — RapyutaSimulationPlugins 0.1 documentation"))

其逻辑是：

```text
UE Dedicated Server
    管理世界和网络状态

UE Client 1
    机器人1及其ROS节点

UE Client 2
    机器人2及其ROS节点

UE Client N
    机器人N及其ROS节点
```

这对于以下场景非常有价值：

```text
大型仓库
大量移动机器人
多相机渲染
多个独立ROS应用
```

但它不等于CoSim的多后端协同。

CoSim可能是：

```text
固定翼：
    JSBSim

四旋翼：
    Gazebo

机器狗：
    MuJoCo

UE：
    只显示全部实体
```

Rapyuta的分布式方案主要仍然以UE世界为核心，而CoSim的权威状态来自多个后端。

因此可以吸收：

```text
UE网络同步
Actor分区
多客户端渲染
动态机器人生成
```

但不要让UE Multiplayer成为CoSim主调度器。

---

# 17.7 turtlebot3-UE

## 17.7.1 定位

`turtlebot3-UE`不是一个通用ROS—UE库，而是使用rclUE和RapyutaSimulationPlugins构建的完整UE参考项目。它采用Apache 2.0许可证。([GitHub](https://github.com/rapyuta-robotics/turtlebot3-UE "GitHub - rapyuta-robotics/turtlebot3-UE · GitHub"))

它的价值主要在于：

```text
告诉你前两个插件最终应该怎样装进一个真实工程
```

---

## 17.7.2 它演示了什么？

当前项目包含：

```text
ROS 2 Topic示例
ROS 2 Service示例
ROS 2 Action示例

TurtleBot3 Burger
TurtleBot3 Waffle
Nav2导航

机械臂示例
UR10
Panda
MoveIt 2

大型地面场景
分布式多机器人测试
自动化测试地图
```

其中Burger用C++实现，Waffle用Blueprint实现，还包含MoveIt 2机械臂和自动化测试场景。([GitHub](https://github.com/rapyuta-robotics/turtlebot3-UE "GitHub - rapyuta-robotics/turtlebot3-UE · GitHub"))

因此它非常适合研究：

```text
C++机器人如何写
Blueprint机器人如何写
Nav2怎样把UE当作仿真器
MoveIt怎样控制UE机械臂
如何做自动测试
如何打包不同地图
```

---

## 17.7.3 Nav2链路

其Nav2示例的逻辑是：

```text
Nav2
    认为外部已有机器人仿真器

UE TurtleBot
    发布里程计、TF和传感器

Nav2
    发布/cmd_vel

UE
    驱动TurtleBot
```

官方示例启动Nav2时明确使用 `use_simulator:=False`，因为真正的模拟器是UE，而不是Gazebo。([GitHub](https://github.com/rapyuta-robotics/turtlebot3-UE "GitHub - rapyuta-robotics/turtlebot3-UE · GitHub"))

这说明UE完全可以作为ROS机器人仿真后端。

但对CoSim：

```text
小车：
    可以考虑UE物理模式

多旋翼和固定翼：
    默认仍是外部物理镜像模式
```

---

## 17.7.4 Fast DDS Discovery Server

`turtlebot3-UE`提供Fast DDS Discovery Server配置，用来减少复杂网络中的DDS发现问题。([GitHub](https://github.com/rapyuta-robotics/turtlebot3-UE "GitHub - rapyuta-robotics/turtlebot3-UE · GitHub"))

这对多机UE仿真很有价值，因为DDS默认发现可能产生较多广播和连接。

但CoSim需要把它做成部署配置：

```yaml
ros2:
  discovery:
    mode: multicast
    # 或
    mode: discovery_server
```

不能把某一种DDS发现方式写死进平台。

---

## 17.7.5 对CoSim的真正价值

`turtlebot3-UE`最值得做的是源码解剖，而不是成为依赖。

重点追踪：

```text
一个Actor怎样创建ROS Node
一个/cmd_vel怎样进入MovementComponent
里程计怎样发布
TF怎样组织
传感器怎样挂载
SpawnEntity怎样创建机器人
自动化测试怎样启动UE和ROS节点
```

完成这些追踪后，这个仓库的使命就结束了。

---

# 17.8 TempoROS

## 17.8.1 定位

TempoROS是Tempo Simulation开发的ROS 2—Unreal Engine插件，采用Apache 2.0许可证。它和rclUE一样把ROS 2直接嵌入UE，但选择使用 `rclcpp`，而不是rcl/rclc。它可以独立使用，不要求安装完整Tempo插件套件。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

当前官方兼容范围包括：

```text
Windows 10 / 11
Ubuntu 22.04 / 24.04
Apple Silicon macOS

Unreal Engine 5.4～5.7
ROS 2 Humble
```

这使它比rclUE更适合当前Windows UE开发环境。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

---

## 17.8.2 为什么TempoROS选择rclcpp？

TempoROS希望直接使用ROS 2完整C++生态：

```text
rclcpp
tf2
image_transport
QoS
Service
自定义IDL
DDS共享内存
```

它认为直接在UE中使用ROS消息，可以避免外部桥接导致的额外序列化、反序列化和网络传输，并且能够复用ROS现有库。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

结构为：

```text
UE
    ↓
UTempoROSNode
    ↓
rclcpp
    ↓
RMW
    ↓
DDS
```

---

## 17.8.3 为什么这件事很难？

`rclcpp`和UE都携带大量第三方依赖，而且对C++编译环境有不同假设。

TempoROS为解决这个问题：

```text
维护自定义rclcpp构建
尽量复用UE自己的第三方库
要求启用C++异常
修改rclcpp头文件中的RTTI使用
建立自己的代码生成和环境脚本
```

官方文档明确说明，依赖冲突、异常、RTTI以及rclcpp目录和链接假设，是该集成最困难的部分。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

因此TempoROS的优势与风险是同一个东西：

```text
优势：
    完整rclcpp能力

风险：
    必须维护定制rclcpp和UE兼容层
```

---

# 17.9 TempoROS的关键能力

## 17.9.1 原生UE类型转换

TempoROS允许直接发布和订阅：

```text
FVector
FQuat
FTransform
FString
自定义UE结构
```

通过模板转换器映射到ROS消息。

例如官方 `FVector` 转换会完成：

```text
厘米 → 米
UE左手系 → ROS右手系
Y轴取反
```

也就是：

```text
ROS.x = 0.01 × UE.X
ROS.y = -0.01 × UE.Y
ROS.z = 0.01 × UE.Z
```

([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

这比每个Actor自己写转换更可靠。

但CoSim仍然不应直接依赖TempoROS的坐标定义作为平台真值，而应让：

```text
CoSim CoordinateTransformService
    负责标准变换

TempoROS Converter
    只负责UE与CoSim/ROS之间最后一层转换
```

---

## 17.9.2 C++与Blueprint

TempoROS将ROS Node包装为 `UTempoROSNode`，可以在C++和Blueprint中创建发布器、订阅器和服务，并为Blueprint自动生成非模板接口。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

这适合：

```text
Blueprint快速场景交互
按键触发ROS消息
调试状态显示
简单虚拟传感器
```

但CoSim核心车辆同步仍建议使用C++，因为高频状态、线程和大量实体更需要明确的性能和生命周期控制。

---

## 17.9.3 自定义消息生成

TempoROS允许在UE模块的 `msg` 和 `srv` 目录中放置ROS IDL，并在构建前自动生成对应C++代码。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

这对CoSim自定义接口很方便，例如：

```text
cosim_msgs/EntityState
cosim_msgs/RenderEntity
cosim_msgs/AnimationState
cosim_msgs/SimulationEvent
```

不过仍需防止UE直接依赖全部CoSim内部数据模型。

推荐只暴露：

```text
显示需要的数据
UE传感器输出的数据
交互控制数据
```

---

## 17.9.4 TF2

TempoROS直接提供动态TF、静态TF和TF查询接口，并支持Blueprint。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

对CoSim而言可用于：

```text
world → vehicle
vehicle → lidar
vehicle → camera
vehicle → gimbal
```

但需要明确谁是TF权威源。

如果Gazebo或机器人状态发布器已经发布：

```text
world → base_link
```

UE不应再发布相同TF。

推荐规则：

```text
权威动力学后端：
    发布动态车辆TF

CoSim车辆资产：
    发布静态传感器安装TF

UE：
    默认只订阅TF并更新Actor
```

---

## 17.9.5 image_transport

TempoROS在发布 `sensor_msgs/Image` 时可以自动使用ROS `image_transport`，从而使用压缩等传输插件。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

对于UE相机非常有用：

```text
本机视觉算法：
    raw或shared memory

网络传输：
    compressed

记录与显示：
    根据需求选择
```

但注意：

```text
4K RGB
深度
语义分割
多相机
```

仍可能产生极高带宽，不能认为使用ROS就自动解决性能问题。

---

## 17.9.6 Shared Memory

TempoROS在Linux上支持通过CycloneDDS与iceoryx进行共享内存传输，需要运行 `iox-roudi`。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

适合：

```text
UE与ROS节点在同一Linux主机
高分辨率图像
点云
大消息
```

不适合：

```text
UE在Windows
ROS在另一台Linux主机
```

跨机器仍然要经过DDS网络传输。

---

## 17.9.7 /clock

TempoROS默认创建 `/clock` 服务子系统，并在每个UE帧发布仿真时间。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

这对于“UE就是仿真器”的项目很方便，但对CoSim默认架构是风险。

因为CoSim中：

```text
Gazebo或JSBSim
    才是权威仿真时钟

UE
    只是显示端
```

因此CoSim使用TempoROS时必须：

```text
禁用TempoROS自动/clock
或
让它订阅CoSim时钟而不是自行产生时钟
```

否则整个ROS系统会错误地跟随UE帧率。

---

# 17.10 rclUE与TempoROS的本质差异

| 维度        | rclUE                                            | TempoROS                                          |
| ----------- | ------------------------------------------------ | ------------------------------------------------- |
| ROS底层     | rcl / rclc                                       | rclcpp                                            |
| UE对象映射  | Node为ActorComponent，Pub/Sub为UObject/Component | Node封装为UObject                                 |
| ROS能力     | Topic、Service、Action                           | Topic、Service、TF2、image_transport、自定义IDL等 |
| 依赖处理    | 预生成、裁剪ROS库                                | 定制rclcpp构建                                    |
| Blueprint   | 支持                                             | 支持                                              |
| Windows     | 官方不支持                                       | 官方支持Windows 10/11                             |
| Linux       | 支持                                             | 支持                                              |
| macOS       | 未作为主支持                                     | 支持Apple Silicon                                 |
| UE版本重心  | 5.1～5.5分支体系                                 | 5.4～5.7                                          |
| ROS版本重心 | Foxy/Humble，Jazzy实验                           | Humble                                            |
| 坐标转换    | 主要由Rapyuta工具层完成                          | 内建常用UE类型转换                                |
| TF2         | 需要自己封装/上层实现                            | 直接集成                                          |
| 图像传输    | 上层实现                                         | 集成image_transport                               |
| 共享内存    | 取决于其ROS构建和DDS                             | 明确支持Linux CycloneDDS+iceoryx                  |
| 生态上层    | RapyutaSimulationPlugins                         | Tempo插件套件，可独立使用                         |
| 许可证      | Apache 2.0                                       | Apache 2.0                                        |

---

# 17.11 哪个更适合CoSim？

## 结论

**CoSim第一选择：TempoROS。**

主要原因不是它“绝对更好”，而是更符合你们当前环境：

```text
UE 5新版本
Windows开发
ROS 2 Humble
需要TF2
需要image_transport
需要自定义消息
需要Blueprint
```

TempoROS当前官方支持UE 5.4～5.7、Windows 10/11、Ubuntu 22.04/24.04和ROS 2 Humble，而rclUE官方仍以Linux和较旧分支组合为主。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

但不能让CoSim直接把TempoROS写死成唯一方案。

正确结构是：

```text
CoSimViewCore
    与ROS无关

CoSimViewTransport
    ├── SharedMemory
    ├── UDP
    ├── gRPC
    └── ROS2

CoSimViewROS2
    第一实现使用TempoROS
```

这样即使TempoROS以后停止维护，也只需替换ROS适配层。

---

# 17.12 CoSim推荐的UE通信架构

```text
                       CoSim Orchestrator
                               │
                 CoSim Renderer Protocol
                               │
             ┌─────────────────┴────────────────┐
             │                                  │
      High-rate Data Plane               Control Plane
      Shared Memory / UDP                gRPC / TCP
             │                                  │
             └─────────────────┬────────────────┘
                               ↓
                         CoSim UE Runtime
                         ├── Entity Manager
                         ├── Actor Factory
                         ├── State Interpolator
                         ├── Animation System
                         ├── Sensor Manager
                         └── Scene Manager
                               │
                 Optional TempoROS Adapter
                         ├── ROS Topics
                         ├── TF2
                         ├── Images
                         ├── Services
                         └── Debug Interfaces
```

核心原则：

```text
实时显示状态：
    不强制经过ROS

ROS调试和算法接口：
    可使用TempoROS

大型视觉数据：
    根据部署位置选择共享内存或image_transport

管理命令：
    使用可靠控制通道
```

---

# 17.13 为什么车辆状态不建议全部走ROS？

UE显示需要的数据通常是：

```text
几十到数百个实体
每个实体30～120 Hz
位置
姿态
速度
舵面
桨叶
关节
灯光
特效
```

ROS 2当然能够传，但CoSim还要支持：

```text
无ROS固定翼模式
日志回放
JSBSim独立模式
远程演示
Windows单独显示机
```

如果UE只支持ROS：

```text
固定翼无ROS模式
    仍然被迫启动ROS网关

日志回放
    仍然被迫转成ROS消息

以后替换中间件
    UE也要修改
```

因此应先定义：

```text
CoSim Render Packet
```

例如：

```cpp
struct RenderEntityState {
    EntityId id;
    Timestamp timestamp;
    Pose3D pose;
    Twist3D velocity;
    AnimationState animation;
};
```

TempoROS只负责把ROS状态转换成这个结构。

---

# 17.14 UE线程与ROS线程

无论使用rclUE还是TempoROS，都必须处理一个重要问题：

```text
ROS回调线程
    不能随意直接修改UE Actor
```

推荐流程：

```text
ROS / Network Callback
    ↓
Lock-Free Queue
    ↓
UE Game Thread
    ↓
Actor Update
```

也就是：

```text
通信线程：
    接收、解析、入队

Game Thread：
    更新Transform、Material、Animation

Render Thread：
    UE内部渲染
```

不要在DDS回调中直接：

```cpp
Actor->SetActorTransform(...)
```

否则容易产生线程安全、生命周期和崩溃问题。

rclUE使用UE Delegate与ActorComponent包装回调，TempoROS则通过UObject封装Node；两者都表明ROS生命周期必须适配UE对象与垃圾回收体系。([rclUE](https://rclue.readthedocs.io/en/latest/design.html "rclUE Design — rclUE 0.1 documentation"))

---

# 17.15 状态插值

物理状态频率和UE渲染频率可能不同：

```text
Gazebo：
    500 Hz

状态输出：
    100 Hz

UE：
    60 FPS
```

UE不能简单使用“收到一帧就瞬移一次”。

需要：

```text
State Buffer
    保存最近若干时间戳状态

Interpolator
    在渲染时刻计算平滑位姿
```

模式包括：

```text
Interpolation
    在两个已知状态之间插值

Short Extrapolation
    使用速度短时间外推

Snap
    时间差过大时直接同步
```

CoSim UE应维护：

```text
source_timestamp
receive_timestamp
render_timestamp
sequence_id
```

这部分不应交给TempoROS或rclUE解决，它属于CoSim View Runtime。

---

# 17.16 坐标转换方案

不能同时依赖：

```text
TempoROS自动转换
Rapyuta ConversionUtils
CoSim Core转换
Blueprint手工转换
```

否则会发生两次转换。

推荐唯一流程：

```text
Backend原始坐标
    ↓
CoSim CoordinateTransformService
    ↓
CoSim ENU / FLU标准状态
    ↓
CoSim UE Converter
    ↓
UE左手系、厘米
```

最后一层转换固定为：

```text
CoSim:
    X前
    Y左
    Z上
    米
    右手系

UE:
    X前
    Y右
    Z上
    厘米
    左手系
```

概念映射：

```text
UE.X = 100 × CoSim.X
UE.Y = -100 × CoSim.Y
UE.Z = 100 × CoSim.Z
```

TempoROS官方常用 `FVector` 转换也是这一思路。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

四元数、角速度、叉乘方向和舵面旋转轴还需要单独测试，不能只转换位置。

---

# 17.17 TF设计

建议TF只表达机器人和传感器的逻辑关系，不承担所有UE场景Actor关系。

```text
map
└── odom
    └── base_link
        ├── imu_link
        ├── lidar_link
        ├── camera_link
        └── gimbal_link
```

UE内部可能还有：

```text
AircraftActor
├── VisualMesh
├── LeftAileron
├── RightAileron
├── LandingGear
└── EngineEffect
```

这些纯视觉骨骼不一定需要全部进入ROS TF。

规则是：

```text
算法需要的坐标：
    发布TF

纯UE动画骨骼：
    不发布TF
```

否则战斗机几十个舵面、起落架部件和视觉节点全部进入TF树，会让ROS系统变得混乱。

---

# 17.18 UE传感器输出设计

## Camera

```text
UE SceneCapture
    ↓
Render Target
    ↓
Image Buffer
    ↓
CoSim Sensor Frame
    ├── Shared Memory
    ├── ROS image_transport
    └── Dataset Writer
```

TempoROS可以直接利用 `image_transport`，这是它相较rclUE路线的重要优势。([GitHub](https://github.com/tempo-sim/TempoROS "GitHub - tempo-sim/TempoROS: Tempo UnrealEngine ROS Integration Plugin · GitHub"))

## LiDAR

```text
UE Raycast / GPU Sensor
    ↓
Point Buffer
    ↓
CoSim PointCloud
    ├── Shared Memory
    ├── PointCloud2
    └── Binary Dataset
```

对于MID360：

```text
UE只负责射线与场景求交
CoSim MID360 Model负责扫描模式和时间戳
TempoROS负责可选PointCloud2发布
```

## Ground Truth

UE可以输出：

```text
实例分割
语义分割
深度
光流
包围框
可见性
```

这些通常更适合：

```text
CoSim Dataset Writer
```

而不是全部实时发布ROS。

---

# 17.19 从Rapyuta路线应吸收什么？

## 吸收一：低层通信与高层仿真框架分离

```text
rclUE
    通信

RapyutaSimulationPlugins
    机器人与传感器
```

CoSim也应分为：

```text
CoSimROS
CoSimView
```

## 吸收二：动态实体服务

```text
Spawn
Delete
Attach
Detach
Set State
Get State
```

## 吸收三：机器人ROS接口组件化

不同Actor挂载不同ROS组件，而不是在GameMode中集中写死全部topic。

## 吸收四：固定时间步和RTF控制

UE可以作为受控仿真器，但必须服从CoSim的时钟权威规则。

## 吸收五：传感器基类

所有传感器共享：

```text
频率
时间戳
frame_id
QoS
启停
噪声
输出适配器
```

## 吸收六：分布式多机器人思路

UE Multiplayer可作为未来大型场景和多客户端渲染研究方向。

---

# 17.20 从TempoROS应吸收什么？

## 吸收一：直接rclcpp集成

可以使用ROS成熟C++能力，而不是重新包装所有功能。

## 吸收二：UE原生类型转换

UE业务代码尽量使用：

```text
FVector
FQuat
FTransform
```

由转换器处理ROS类型。

## 吸收三：TF2与image_transport

不用重新实现ROS标准生态。

## 吸收四：自定义IDL代码生成

CoSim显示接口可以自动生成ROS消息类型。

## 吸收五：跨平台

尤其适合：

```text
Windows UE
Linux ROS 2
```

的开发环境。

## 吸收六：共享内存可选加速

适合同机Linux视觉仿真。

---

# 17.21 不应该照搬什么？

## 不照搬Rapyuta的所有机器人基类

它的基础接口偏向：

```text
移动机器人
机械臂
/cmd_vel
JointState
```

而CoSim需要覆盖固定翼和多旋翼。

## 不照搬UE权威物理假设

RapyutaSimulationPlugins可以使用UE物理驱动机器人，但CoSim默认物理在Gazebo、JSBSim或MuJoCo。

## 不让TempoROS自动掌握/clock

CoSim Orchestrator才是主时钟。

## 不让ROS消息成为UE内部数据模型

UE内部使用：

```text
CoSim RenderState
```

ROS只是一种输入输出。

## 不同时维护两套完整ROS插件

不建议生产环境同时维护：

```text
rclUE
TempoROS
```

可以都研究，但主线只选一个。

## 不以turtlebot3-UE为项目模板直接扩展

它适合作为示例，但其项目结构、分支组合和机器人假设都围绕Rapyuta生态，不适合作为CoSim UE长期工程底座。

---

# 17.22 CoSim最终选型

```text
主ROS—UE插件：
    TempoROS

架构和源码参考：
    rclUE

机器人、传感器、实体管理参考：
    RapyutaSimulationPlugins

完整案例和测试参考：
    turtlebot3-UE
```

更加准确地说：

```text
直接依赖：
    TempoROS，可选

选择性迁移设计：
    RapyutaSimulationPlugins

不直接依赖：
    turtlebot3-UE

仅研究或备用：
    rclUE
```

---

# 17.23 CoSim UE插件建议结构

```text
CoSimUE/
├── CoSimViewCore/
│   ├── EntityManager
│   ├── ActorFactory
│   ├── StateBuffer
│   ├── StateInterpolator
│   ├── AnimationSystem
│   ├── SceneManager
│   └── CoordinateConverter
│
├── CoSimViewTransport/
│   ├── SharedMemoryClient
│   ├── UdpClient
│   ├── GrpcClient
│   └── ReplayClient
│
├── CoSimViewROS/
│   ├── TempoROSAdapter
│   ├── TfAdapter
│   ├── ImageAdapter
│   ├── PointCloudAdapter
│   └── RosDebugInterface
│
├── CoSimSensors/
│   ├── Camera
│   ├── DepthCamera
│   ├── SemanticCamera
│   ├── Lidar
│   ├── Mid360
│   └── Radar
│
├── CoSimVehicles/
│   ├── MultirotorActor
│   ├── FixedWingActor
│   ├── GroundVehicleActor
│   └── LeggedActor
│
└── CoSimTools/
    ├── SpawnPanel
    ├── ConnectionPanel
    ├── TfDebugger
    ├── SensorPreview
    └── NetworkStats
```

---

# 17.24 第一阶段实施路线

## 阶段一：只做状态镜像

```text
CoSim Core
    ↓ UDP
UE
```

实现：

```text
SpawnEntity
DeleteEntity
UpdatePose
UpdateAnimation
Reconnect
```

此阶段不接ROS。

## 阶段二：加入TempoROS

实现：

```text
订阅VehicleState
订阅TF
发布UE状态
ROS诊断
```

但 `/clock`关闭。

## 阶段三：加入视觉传感器

```text
RGB
Depth
Semantic
```

先输出本地文件，再加入ROS `image_transport`。

## 阶段四：LiDAR

先做普通3D LiDAR，再做MID360扫描适配。

## 阶段五：动态实体与多机

```text
ROS Service / gRPC
    Spawn
    Delete
    Attach
    Reset
```

## 阶段六：分布式和性能

研究：

```text
UE Dedicated Server
多UE客户端
Shared Memory
DDS Discovery Server
多GPU渲染
```

---

# 17.25 最小研究任务

```text
1. 跑通TempoROS Publisher和Subscriber
2. 在Windows UE连接Linux ROS 2
3. 测试QoS可靠与Best Effort
4. 跑通自定义msg代码生成
5. 跑通TF发布和查询
6. 跑通image_transport
7. 检查TempoROS自动/clock并关闭
8. 建立CoSim ENU到UE转换单元测试
9. 阅读rclUE Node、Publisher、Subscriber类
10. 理解rcl/rclc为何更适合UE对象模型
11. 阅读Rapyuta的ARRBaseRobot
12. 阅读URRRobotROS2Interface
13. 追踪/cmd_vel到MovementComponent
14. 追踪Camera到sensor_msgs/Image
15. 追踪3D LiDAR到PointCloud2
16. 追踪SpawnEntity服务
17. 阅读固定时间步和RTF实现
18. 跑通turtlebot3-UE Nav2示例
19. 跑通MoveIt机械臂示例
20. 阅读其自动化测试脚本
21. 建立CoSimViewCore
22. 建立独立UDP Renderer Protocol
23. 再把TempoROS作为可选Adapter接入
```

---

# 17.26 最终判断

```text
rclUE：
    值得深入研究
    不建议作为Windows主线依赖

RapyutaSimulationPlugins：
    值得吸收实体、传感器、时钟和分布式设计
    不建议整体迁入CoSim

turtlebot3-UE：
    值得作为完整示例和测试教材
    不进入CoSim运行时

TempoROS：
    最适合成为CoSim当前可选ROS—UE插件
    但必须包在CoSim Adapter后面
```

一句话总结：

> **rclUE提供了一套遵循UE对象体系的低层ROS 2集成方法，RapyutaSimulationPlugins在其上建立了完整机器人、传感器和仿真管理框架，turtlebot3-UE证明了这套体系能够运行Nav2、MoveIt和多机器人示例；TempoROS则使用更现代、跨平台的rclcpp直连路线。CoSim应以TempoROS作为当前ROS—UE首选适配器，以rclUE和Rapyuta项目作为架构参考，但UE的核心状态通道、时间、坐标和实体模型必须保持与ROS无关。**
>
