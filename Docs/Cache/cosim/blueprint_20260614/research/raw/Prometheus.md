# 15. 项目概述：Prometheus 自主无人机平台

## 15.1 定位

Prometheus 是阿木实验室维护的开源自主无人机软件平台。它建立在 **PX4 飞控、ROS/ROS2、Gazebo/AirSim 和机载计算机**之上，目标是给无人机开发者提供一套可以直接用于控制、定位、规划、目标检测、集群控制、仿真和实机部署的上层软件系统。官方仓库将其描述为面向智能与自主飞行的完整解决方案，而不是单独的控制器、规划器或仿真器。([GitHub](https://github.com/amov-lab/Prometheus "GitHub - amov-lab/Prometheus: Open source software for autonomous drones. · GitHub"))

Prometheus 在整个无人机技术栈中的位置可以理解为：

```text
传感器与仿真世界
    Gazebo / AirSim / 真实相机 / 真实雷达
                ↓
定位与感知
    Fast-LIO / 视觉检测 / 地图
                ↓
规划与任务
    EGO-Planner / 航点 / 编队 / 搜索
                ↓
Prometheus控制与通信中间层
                ↓
PX4
    位置、姿态、角速度、电机控制
                ↓
仿真无人机或真实无人机
```

因此 Prometheus 不是：

```text
物理引擎
渲染器
飞控固件本体
单一规划算法
强化学习训练平台
```

它更像：

> **PX4 和 ROS 自主算法之间的一套无人机应用中间层、功能集成平台和教学开发框架。**

从当前仓库结构看，它已经把控制、通信、Fast-LIO、EGO-Planner-Swarm、集群控制、编队、地面车控制、MATLAB Bridge、仿真工具和案例实验集中在同一项目中；仿真部分又包含 Gazebo、AirSim、Livox、RealSense 和 Velodyne 等适配内容。([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Modules "Prometheus/Modules at main · amov-lab/Prometheus · GitHub"))

---

## 15.2 核心设计理念

| 设计原则               | 说明                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| 机载计算机平台化       | 不让每个开发者重新实现 PX4 通信、状态获取和基础控制                                        |
| PX4 与上层算法分离     | PX4 保持飞控职责，规划、感知和任务运行在机载计算机                                         |
| 命令接口统一           | 将位置、速度、加速度、姿态、轨迹等控制形式包装成较统一的接口                               |
| 仿真与实机共用上层软件 | 上层模块尽量不关心下方是 Gazebo、AirSim 还是真实飞行器                                     |
| 模块集成优先           | 集成定位、规划、目标检测、集群等已有开源算法                                               |
| 功能 Demo 驱动         | 通过起降、轨迹、避障、编队等完整案例降低学习门槛                                           |
| 传感器适配             | 为 Livox、RealSense、Velodyne 等传感器准备仿真或软件接口                                   |
| 单机与集群并存         | 同时考虑单机控制、集群控制、编队和协同任务                                                 |
| 教学和工程落地导向     | 不只提供算法源代码，还提供部署文档、仿真环境和配套硬件流程                                 |
| 渐进式 ROS2 迁移       | 旧主线明显继承 ROS1/MAVROS，新的 Prometheus V3 文档已加入 ROS2 Humble、DDS 和 Mavros2 路线 |

旧版 PX4 文档将 Prometheus 描述为基于 ROS 1、面向建图、定位、规划、控制和目标检测，并与 Gazebo 集成的自主无人机软件包集合；当前 Prometheus 手册则已经增加 Prometheus V3、Ubuntu 22.04、ROS2 Humble、XRCE-DDS 和 Mavros2 部署内容。([PX4 文档](https://docs.px4.io/v1.13/zh/ros/ros1 "使用 ROS | PX4 自动驾驶用户指南 (v1.13)"))

---

# 15.3 系统设计逻辑

## 15.3.1 第一性原理：为什么还需要 Prometheus？

有了 PX4 和 ROS，并不意味着自主无人机系统会自动形成。

直接使用原始组件时，开发者需要自己处理：

```text
PX4状态消息
MAVLink或DDS通信
解锁和模式切换
Offboard心跳
位置、速度、姿态命令转换
坐标系转换
遥控器接管
传感器数据
规划器轨迹转换
仿真与实机配置
故障和安全状态
```

如果每个规划器、检测器和控制器都直接连接 PX4，就会形成：

```text
EGO-Planner直接理解PX4消息
视觉节点直接理解MAVROS
集群节点直接操作飞行模式
地面站直接依赖每个算法内部结构
```

最后所有算法都会和某个 PX4 版本、某组 MAVROS topic 以及某套坐标系绑定。

Prometheus 试图增加一个中间层：

```text
上层算法
    只表达“我要飞到哪里、以什么速度飞、执行什么任务”
            ↓
Prometheus控制与通信层
    处理命令类型、飞行状态、PX4接口和安全逻辑
            ↓
PX4
```

核心洞察是：

> **自主算法不应该直接承担飞控通信和模式管理；这些公共能力应该被平台统一封装。**

---

## 15.3.2 第二性原理：为什么把它定位为机载计算机软件？

PX4 通常运行在飞控硬件上，负责高频、确定性和安全敏感的任务：

```text
传感器采集
状态估计
位置与姿态控制
角速度控制
控制分配
飞行模式
Failsafe
电机输出
```

但以下任务通常更适合运行在机载计算机：

```text
点云处理
Fast-LIO
目标检测
深度学习
局部地图
路径规划
编队和任务分配
人机交互
数据处理
```

Prometheus 官方明确把项目定位为 PX4 配套的机载计算机端软件系统。([GitHub](https://github.com/amov-lab/Prometheus "GitHub - amov-lab/Prometheus: Open source software for autonomous drones. · GitHub"))

因此它采用的是：

```text
飞控硬件：
    PX4

机载计算机：
    Prometheus
    ROS / ROS2
    感知
    定位
    规划
    任务

传感器：
    LiDAR
    Camera
    IMU
    GPS / RTK / UWB 等
```

这与我们规划的长期架构基本一致。

---

## 15.3.3 第三性原理：为什么需要统一控制命令层？

上层算法可能输出不同层级的目标：

```text
航点规划器：
    目标位置

局部规划器：
    位置、速度、加速度、航向

避障算法：
    期望速度

视觉跟踪：
    机体系速度

高级控制器：
    姿态和推力

编队算法：
    相对位置或速度
```

如果 PX4 接口只允许一种命令，上层算法就必须反复做转换。

Prometheus 的控制模块和相关产品文档公开了位置、速度、加速度、姿态以及轨迹、集群控制等多类入口，这表明其设计重点之一就是让不同自主算法通过统一控制层进入 PX4。([AmovLab Docs](https://docs.amovlab.com/prometheus-wiki/?utm_source=chatgpt.com "阿木实验室-Prometheus使用手册"))

其抽象逻辑应当是：

```text
Command
    type:
        position
        velocity
        acceleration
        attitude
        trajectory
        takeoff
        land

    frame:
        world
        body
        geographic

    reference:
        具体目标量
```

然后由控制中间层选择：

```text
发布PX4位置目标
发布速度目标
发布姿态目标
执行模式切换
执行起飞或降落状态机
```

这比每个算法直接发布 PX4 原始 topic 更容易维护。

---

## 15.3.4 第四性原理：为什么集成完整 Demo，而不是只提供库？

一个自主无人机功能通常跨越很多模块。

例如 MID360 避障：

```text
MID360仿真或驱动
    ↓
点云预处理
    ↓
定位
    ↓
局部地图
    ↓
EGO-Planner
    ↓
轨迹
    ↓
控制模块
    ↓
PX4
```

只发布一个规划算法仓库，并不能证明整条链路能运行。

Prometheus 当前手册提供控制、目标检测、EGO-Planner-Swarm，以及 D435i、二维激光雷达和 MID360 单机或多机避障示例；仓库也把 Fast-LIO、EGO-Planner-Swarm、控制、通信和仿真插件组织在同一项目中。([AmovLab Docs](https://docs.amovlab.com/prometheus-wiki/?utm_source=chatgpt.com "阿木实验室-Prometheus使用手册"))

因此它的工程思路是：

```text
单个算法
    +
输入输出适配
    +
启动配置
    +
仿真场景
    +
控制链路
    +
完整Demo
```

这对形成生态很重要。

---

# 15.4 仓库架构

当前 Prometheus 仓库顶层主要包括：

```text
Experiment/
Modules/
Scripts/
Simulator/
```

并提供分模块编译脚本，例如控制、通信、规划、集群、MATLAB Bridge 和地面车控制。([GitHub](https://github.com/amov-lab/Prometheus "GitHub - amov-lab/Prometheus: Open source software for autonomous drones. · GitHub"))

可以把它理解为四层。

## 15.4.1 Modules：功能模块层

当前 `Modules` 中包括：

```text
FAST_LIO
common
communication
ego_planner_swarm
future_aircraft
global_planner_ugv
matlab_bridge
motion_planning
searching_pkg
simulator_utils
swarm_control
swarm_formation
tutorial_demo
uav_control
uav_control_fmt
ugv_control
```

([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Modules "Prometheus/Modules at main · amov-lab/Prometheus · GitHub"))

这些模块大致可分为：

```text
基础设施：
    common
    communication
    simulator_utils

无人机控制：
    uav_control
    uav_control_fmt

定位与建图：
    FAST_LIO

规划：
    motion_planning
    ego_planner_swarm

集群：
    swarm_control
    swarm_formation
    searching_pkg

其他载具：
    ugv_control
    global_planner_ugv
    future_aircraft

外部工具：
    matlab_bridge

教学：
    tutorial_demo
```

它体现的是“功能生态型仓库”，而不是一个纯粹的小型核心库。

---

## 15.4.2 Simulator：仿真与传感器适配层

当前 `Simulator` 目录包括：

```text
airsim_simulator
gazebo_simulator
livox_laser_gazebo_plugins
realsense_gazebo_plugin
velodyne_gazebo_plugins
```

([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Simulator "Prometheus/Simulator at main · amov-lab/Prometheus · GitHub"))

这说明 Prometheus 并没有把自己绑定为一个物理引擎，而是围绕不同仿真器和传感器建立适配层。

其抽象逻辑可以理解为：

```text
算法模块
    不应关心点云来自真实雷达还是Gazebo插件

控制模块
    不应关心无人机运行在Gazebo、AirSim还是实机

仿真适配层
    负责提供与真实系统相近的消息和接口
```

这与我们要做的多后端系统有明显共性。

---

## 15.4.3 Experiment：案例和任务层

`Experiment` 适合放：

```text
完整任务
组合配置
实验场景
验证案例
```

平台代码与实验代码分开是正确方向。

长期项目中也应区分：

```text
platform/
    通用功能

experiments/
    特定实验

benchmarks/
    可重复评价
```

否则一个成功 Demo 中的临时逻辑很容易进入平台核心。

---

## 15.4.4 Scripts：部署和构建层

脚本层承担：

```text
环境编译
模块选择
仿真启动
软件部署
```

Prometheus 还提供分功能的编译脚本，表明它试图避免强制用户每次构建整个巨型仓库。([GitHub](https://github.com/amov-lab/Prometheus "GitHub - amov-lab/Prometheus: Open source software for autonomous drones. · GitHub"))

这一思想可以进一步升级为：

```text
CMake Presets
colcon mixins
Docker
Dev Container
CI
可选Feature
插件清单
```

---

# 15.5 uav_control：控制中间层

## 15.5.1 定位

`uav_control` 不是 PX4 姿态环的替代品。

它更接近：

```text
上层任务命令
        ↓
命令检查和状态机
        ↓
PX4 Offboard/MAVROS/DDS接口
        ↓
PX4内部控制器
```

它应当负责：

```text
起飞和降落流程
解锁和模式切换
位置、速度、姿态等命令封装
坐标系和机体系转换
命令超时
状态监控
控制模式切换
安全或人工接管
```

而不是重新完成：

```text
IMU采样
EKF
角速度环
电机PWM
飞控Failsafe
```

---

## 15.5.2 为什么要使用控制状态机？

起飞并不是简单发布：

```text
z = 1.5m
```

完整过程可能包含：

```text
检查定位有效
检查飞控连接
切换Offboard
保持心跳
解锁
缓慢抬升
确认离地
进入悬停
```

降落也可能包含：

```text
下降
检测接地
降低推力
上锁
退出Offboard
```

把这些过程写进每个 Demo 会产生大量重复。

因此平台应提供：

```text
ControlStateMachine
    INIT
    READY
    ARMED
    TAKEOFF
    HOVER
    TRACKING
    LANDING
    EMERGENCY
```

上层规划器只需要表达任务目标。

---

## 15.5.3 对我们的借鉴

我们应建立平台无关的：

```text
VehicleCommand
VehicleStatus
ControlMode
SafetyState
```

然后分别实现：

```text
PX4DDSAdapter
PX4MavrosAdapter
SimulationDirectAdapter
ReplayAdapter
```

不要让规划器直接包含：

```text
/fmu/in/...
/mavros/setpoint_...
```

这些后端细节。

---

# 15.6 通信层

## 15.6.1 旧版本路线

Prometheus 的经典路线建立在：

```text
ROS1
MAVROS
MAVLink
PX4
```

PX4 v1.13 官方文档也是这样描述该项目的。([PX4 文档](https://docs.px4.io/v1.13/zh/ros/ros1 "使用 ROS | PX4 自动驾驶用户指南 (v1.13)"))

链路为：

```text
Prometheus ROS Node
    ↓ ROS topic
MAVROS
    ↓ MAVLink
PX4
```

优点：

```text
成熟
教程多
兼容旧PX4生态
方便接QGroundControl
```

缺点：

```text
ROS1已经退出主流
多机命名空间复杂
DDS集成程度低
大量消息要经过MAVLink映射
```

---

## 15.6.2 新版本路线

当前官方手册已经提供 Prometheus V3 的 ROS2 Humble 配置，并允许选择：

```text
XRCE-DDS
或
Mavros2
```

([AmovLab Docs](https://docs.amovlab.com/prometheus-wiki/?utm_source=chatgpt.com "阿木实验室-Prometheus使用手册"))

这意味着现代化架构可以有两种接入：

```text
方案A：
Prometheus ROS2 Node
    ↓ px4_msgs / DDS
PX4 uORB

方案B：
Prometheus ROS2 Node
    ↓ Mavros2 / MAVLink
PX4
```

建议我们的主线优先：

```text
ROS2 + px4_msgs + uXRCE-DDS
```

而将 Mavros2 保留为：

```text
旧系统兼容
通用MAVLink设备兼容
某些地面站或第三方飞控接口
```

---

## 15.6.3 不能直接复制 Prometheus topic 命名

Prometheus 的旧接口常包含类似：

```text
/uav1/...
/uav2/...
```

或 MAVROS 命名空间。

我们的长期接口应更明确地区分：

```text
平台公共接口
PX4原始接口
传感器原始接口
算法内部接口
```

例如：

```text
/platform/uav_0/state
/platform/uav_0/command
/platform/uav_0/trajectory

/fmu/out/...
/fmu/in/...

/sensors/mid360/points
/planning/local_trajectory
```

这样将来替换 PX4 或使用 MuJoCo 时，上层算法不必改 topic。

---

# 15.7 定位、感知和规划

## 15.7.1 Fast-LIO

当前仓库把 Fast-LIO 放入 `Modules`，说明 Prometheus 选择直接集成成熟的 LiDAR—IMU 里程计，而不是重新编写定位算法。([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Modules "Prometheus/Modules at main · amov-lab/Prometheus · GitHub"))

典型链路：

```text
MID360 point cloud
    +
IMU
    ↓
Fast-LIO
    ↓
Odometry
Local Map
```

对我们而言，应吸收“第三方算法适配层”而不是把 Fast-LIO 源码永久混入平台核心：

```text
LocalizationBackend
    FastLIOAdapter
    GroundTruthAdapter
    PX4EKFAdapter
    VIOAdapter
```

---

## 15.7.2 EGO-Planner-Swarm

仓库将 `ego_planner_swarm` 作为模块，官方手册还提供单机和多机、D435i、二维激光雷达和 MID360 避障示例。([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Modules "Prometheus/Modules at main · amov-lab/Prometheus · GitHub"))

其位置应当是：

```text
Localization
    ↓
Local Map
    ↓
EGO-Planner-Swarm
    ↓
Trajectory
    ↓
Control Adapter
    ↓
PX4
```

关键点是：

```text
EGO输出轨迹
Prometheus负责轨迹进入控制系统
PX4负责低层跟踪和飞行安全
```

不要让 EGO-Planner 直接管理电机或 PX4 模式。

---

## 15.7.3 目标检测

Prometheus 集成了目标检测方向，当前手册中也有 SpireCV ROS 模块、NVIDIA 驱动、CUDA、TensorRT 和图像流相关部署内容。([AmovLab Docs](https://docs.amovlab.com/prometheus-wiki/?utm_source=chatgpt.com "阿木实验室-Prometheus使用手册"))

这体现了平台化项目需要同时处理：

```text
算法模型
推理运行时
相机数据
结果消息
硬件加速
部署环境
```

但我们不应该让平台核心依赖某个具体检测框架。

应抽象为：

```text
DetectionBackend
    SpireCV
    YOLO
    TensorRT
    OpenVINO
    OtherModel
```

公共输出为：

```text
DetectionArray
TrackingResult
TargetPose
```

---

# 15.8 仿真器与传感器插件

## 15.8.1 Gazebo

Prometheus 使用 Gazebo 构建无人机和传感器仿真，并提供控制、规划和视觉功能的仿真流程。([AmovLab Docs](https://docs.amovlab.com/prometheus-wiki/?utm_source=chatgpt.com "阿木实验室-Prometheus使用手册"))

它的作用是：

```text
物理
碰撞
无人机状态
传感器
环境
```

Prometheus 则在 Gazebo 之上运行上层算法。

---

## 15.8.2 AirSim

当前仓库保留 `airsim_simulator`，说明其设计并未将 Gazebo 作为唯一仿真环境。([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Simulator "Prometheus/Simulator at main · amov-lab/Prometheus · GitHub"))

这可以用于：

```text
视觉算法
高真实感环境
相机数据
展示
```

但不能默认 Gazebo 与 AirSim 同时是权威真值源。

合理方式是：

```text
Gazebo实验：
    Gazebo是真值

AirSim实验：
    AirSim是真值

UE显示模式：
    UE只镜像Gazebo状态
```

---

## 15.8.3 Livox、RealSense 和 Velodyne 插件

Prometheus 仿真目录包含：

```text
livox_laser_gazebo_plugins
realsense_gazebo_plugin
velodyne_gazebo_plugins
```

([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Simulator "Prometheus/Simulator at main · amov-lab/Prometheus · GitHub"))

这体现了一个重要思想：

> **传感器应通过统一算法接口接入，但其仿真模型仍应按设备类型独立实现。**

不过要注意：

```text
“存在Livox插件”
    不等于
“完整复现MID360所有扫描和时间特性”
```

我们仍需单独验证：

```text
视场
点频
扫描模式
逐点时间戳
噪声
盲区
量程
强度
运动畸变
消息格式
```

---

# 15.9 集群功能

当前仓库包含：

```text
swarm_control
swarm_formation
ego_planner_swarm
searching_pkg
```

([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Modules "Prometheus/Modules at main · amov-lab/Prometheus · GitHub"))

这说明 Prometheus 不只考虑单机，还希望提供：

```text
编队
集群轨迹
多机避障
协同搜索
任务控制
```

其分层应当是：

```text
Swarm Mission
    ↓
Task Assignment
    ↓
Per-UAV Goal
    ↓
Per-UAV Planner
    ↓
Per-UAV Control
    ↓
Per-UAV PX4
```

不要让 `swarm_control` 直接承担：

```text
所有无人机定位
所有局部规划
所有底层飞控
```

否则中心节点会成为性能和可靠性瓶颈。

---

# 15.10 Prometheus 与 XTDrone 的区别

两者都基于 PX4、ROS 和 Gazebo，但侧重点不同。

| 维度         | Prometheus                                 | XTDrone                           |
| ------------ | ------------------------------------------ | --------------------------------- |
| 主要定位     | 机载计算机自主无人机软件平台               | 自主无人机与集群仿真集成平台      |
| 风格         | 工程、教学、软硬件配套                     | 学术仿真、案例和集群研究          |
| 控制封装     | 强调统一无人机控制与命令接口               | 更强调多模块和多机系统集成        |
| 传感器配套   | Livox、RealSense、Velodyne 等较直接        | 视觉、SLAM和规划案例丰富          |
| 硬件落地     | 与阿木实验室无人机和机载计算机结合较深     | 更偏通用PX4仿真和研究             |
| 规划         | 集成 EGO-Planner-Swarm 等                  | 集成多种规划和集群案例            |
| 当前迁移     | 已提供 Prometheus V3 ROS2/DDS/Mavros2 文档 | XTDrone2 正在迁移 ROS2 与新Gazebo |
| 我们主要学习 | 中间件、控制封装和仿真实机一致             | 自主系统分层、多实例和集群组织    |

Prometheus 更像：

```text
可以装进机载计算机的软件产品框架
```

XTDrone 更像：

```text
用于自主算法研究和多机实验的平台框架
```

我们需要同时吸收：

```text
Prometheus：
    设备和控制接口封装

XTDrone：
    系统分层与多机架构
```

---

# 15.11 Prometheus 与我们长期项目的关系

Prometheus 最接近我们长期项目中的：

```text
Autonomy Middleware
```

也就是：

```text
传感器、定位、规划、控制命令、PX4接口
之间的标准中间层
```

但我们不应直接把整个 Prometheus 仓库作为长期项目核心。

更合理的是提炼：

```text
Vehicle Manager
Command Manager
PX4 Adapter
Localization Adapter
Planner Adapter
Sensor Adapter
Swarm Manager
Experiment Manager
```

其位置可以设计为：

```text
                  UE展示前端
                       ↑
                 Display Bridge
                       ↑
┌───────────────────────────────────────┐
│         Autonomy Middleware           │
│ Vehicle / Command / Mission / Safety  │
└────────↑───────────────↑──────────────┘
         │               │
  Perception/Planning   PX4 Adapter
         │               │
       ROS2             PX4
         │               │
       Gazebo ←──────────┘
```

---

# 15.12 我们应该吸收哪些设计？

## 吸收一：统一无人机命令接口

至少定义：

```text
TakeoffCommand
LandCommand
PositionCommand
VelocityCommand
AccelerationCommand
AttitudeCommand
TrajectoryCommand
EmergencyCommand
```

并明确：

```text
参考坐标系
时间戳
无人机ID
命令超时
优先级
控制模式
```

---

## 吸收二：Vehicle Manager

每架无人机应由统一管理器维护：

```text
连接状态
飞行模式
解锁状态
定位状态
电池
当前位置
当前任务
当前命令
故障状态
```

而不是让每个算法自己订阅几十个 PX4 topic。

---

## 吸收三：仿真和实机使用相同的上层接口

```text
仿真：
    Gazebo + PX4 SITL

实机：
    真实PX4 + MID360

上层：
    Localization / Planner / Mission
    尽量不改
```

---

## 吸收四：功能模块通过 Adapter 接入

```text
LocalizationAdapter
PlannerAdapter
DetectorAdapter
ControllerAdapter
SimulatorAdapter
```

不要把 Fast-LIO 或 EGO 源码结构变成平台公共接口。

---

## 吸收五：完整 Demo 是交付的一部分

平台至少应随代码提供：

```text
起飞悬停
轨迹跟踪
MID360定位
单机避障
目标追踪
两机编队
风扰测试
电机退化测试
```

每个 Demo 都应具备：

```text
配置
启动
数据记录
评价指标
预期结果
```

---

## 吸收六：传感器仿真与真实驱动对齐

例如：

```text
MID360 Simulation Adapter
MID360 Hardware Adapter
```

二者都输出统一：

```text
PointCloud
IMU
Timestamp
Frame
```

---

## 吸收七：ROS1、ROS2和不同PX4接口隔离

```text
PX4DDSAdapter
Mavros2Adapter
LegacyMavrosAdapter
```

平台核心不直接依赖其中任何一种。

---

## 吸收八：地面站与ROS总线解耦

官方产品文档提到 Prometheus 地面站采用 Qt，并使用 TCP/UDP 进行通信，以避免 ROS1 多机通信配置复杂。([AmovLab Docs](https://docs.amovlab.com/p250u-v2/?utm_source=chatgpt.com "阿木实验室"))

这个思路值得吸收：

```text
内部工程通信：
    ROS2

外部地面站：
    独立协议 / WebSocket / gRPC / UDP

二者通过Gateway连接
```

不要要求所有地面站电脑加入完整 ROS2 网络。

---

# 15.13 不应该照搬什么？

## 不照搬一：不要把全部第三方源码放进一个巨型仓库

Prometheus 当前把 Fast-LIO、EGO-Planner-Swarm、集群模块和多个传感器插件集中在一个仓库中，便于教学和一键运行，但长期容易产生：

```text
版本锁定
补丁难回上游
许可证混合
更新冲突
仓库体积膨胀
依赖难审计
```

更适合我们的方式是：

```text
核心仓库
    只放接口和平台

第三方算法
    独立包或依赖锁定

集成仓库
    用manifest管理版本
```

---

## 不照搬二：不要绑定阿木硬件和默认参数

Prometheus 与阿木实验室的机架、机载计算机、传感器和配套产品结合较深。([GitHub](https://github.com/amov-lab/Prometheus "GitHub - amov-lab/Prometheus: Open source software for autonomous drones. · GitHub"))

我们应将硬件抽象为：

```text
VehicleProfile
ComputeProfile
SensorProfile
```

当前默认实现：

```text
Sunray-150
MID360
指定机载计算机
```

但不能写死品牌和设备。

---

## 不照搬三：不要保留 ROS1/MAVROS 作为长期核心

旧系统可以作为兼容层，长期主线应优先：

```text
ROS2 Humble/Jazzy或后续LTS
PX4 DDS
新Gazebo
```

Prometheus V3 自身也已经开始提供 ROS2 Humble、DDS 和 Mavros2 路线。([AmovLab Docs](https://docs.amovlab.com/prometheus-wiki/?utm_source=chatgpt.com "阿木实验室-Prometheus使用手册"))

---

## 不照搬四：不要长期维护自定义 PX4 Fork

Prometheus 有配套的 `Prometheus_PX4` 仓库，公开结果显示其基于 PX4 1.12.3 分支。([GitHub](https://github.com/amov-lab/Prometheus_PX4?utm_source=chatgpt.com "GitHub - amov-lab/Prometheus_PX4"))

自定义 PX4 Fork 的风险是：

```text
无法及时获得上游修复
ROS2消息版本不一致
新硬件支持落后
长期合并成本高
安全补丁滞后
```

我们的原则应是：

```text
尽量使用上游PX4
必要修改做独立模块
补丁尽量提交上游
严格记录版本和差异
```

---

## 不照搬五：不要将 MATLAB Bridge 变成必需依赖

仓库包含 `matlab_bridge`，也提供相应编译脚本。([GitHub](https://github.com/amov-lab/Prometheus/tree/main/Modules "Prometheus/Modules at main · amov-lab/Prometheus · GitHub"))

它可以作为：

```text
可选控制器研究接口
```

但不能成为平台启动必需项。

---

## 不照搬六：不要忽略许可证冲突

Prometheus 仓库根目录的 `LICENSE` 是标准 Apache 2.0，明确授予复制、修改、分发和商业使用相关权利；但 README 同时写有“仅限个人使用、请勿用于商业用途”的附加声明。两者在表面上并不一致。([GitHub](https://github.com/amov-lab/Prometheus/blob/main/LICENSE "Prometheus/LICENSE at main · amov-lab/Prometheus · GitHub"))

因此我们的处理应是：

```text
学习架构：
    没有问题

复制或修改代码：
    记录具体文件来源和许可证

商业分发：
    在使用前向权利方确认
    或只复现设计，不直接复制存在争议的代码

第三方子模块：
    分别检查各自LICENSE
```

这不是法律结论，但足以说明：不能只看 GitHub 页面顶部的许可证标签。

---

## 不照搬七：不要把“功能集成”理解为“所有功能都默认启动”

真正的平台应该按需加载：

```text
控制模式：
    只启动PX4和Vehicle Manager

规划模式：
    增加定位和规划

视觉模式：
    增加检测

集群模式：
    增加Swarm Manager

训练模式：
    不启动高成本传感器和UE
```

否则系统会过重，难以调试。

---

# 15.14 在长期架构中的位置

Prometheus 的设计应进入我们的 **自主中间件层** ：

```text
┌───────────────────────────────────────────┐
│                 Mission Layer             │
│ Task / Goal / Swarm / Operator Command    │
└─────────────────────┬─────────────────────┘
                      ↓
┌───────────────────────────────────────────┐
│          Autonomy Middleware              │
│ Vehicle Manager                           │
│ Command Manager                           │
│ Safety Supervisor                         │
│ Localization / Planner Adapters            │
└───────────┬───────────────────┬───────────┘
            ↓                   ↓
      ROS2 Algorithms        PX4 Adapter
            ↓                   ↓
    MID360 / Fast-LIO          PX4
    EGO / Detection             ↓
            └────────────── Gazebo
                               ↓
                         Unified State
                               ↓
                              UE
```

Prometheus 提供的核心启发是：

```text
自主算法与PX4之间
应该有一层标准化、可监控、可切换的无人机中间件
```

---

# 15.15 最小研究任务

针对 Prometheus，建议依次完成：

```text
1. 画出Prometheus总体模块图
2. 梳理Modules、Simulator、Experiment和Scripts
3. 找到uav_control的命令结构
4. 追踪一条位置命令到PX4的完整链路
5. 追踪起飞和降落状态机
6. 找到无人机状态汇总逻辑
7. 理清world frame、body frame和PX4坐标系
8. 理清旧MAVROS通信层
9. 理清Prometheus V3 DDS路线
10. 理清Prometheus V3 Mavros2路线
11. 对比两种ROS2接入方式
12. 跑通Gazebo起飞和悬停
13. 跑通轨迹控制
14. 跑通Fast-LIO数据接口
15. 跑通EGO-Planner-Swarm单机链路
16. 跑通MID360仿真避障示例
17. 研究Livox Gazebo插件
18. 研究AirSim适配层
19. 研究swarm_control和swarm_formation
20. 研究地面站通信协议
21. 列出所有第三方子模块及LICENSE
22. 标记Prometheus自研代码和第三方代码边界
23. 提炼统一VehicleCommand
24. 提炼统一VehicleStatus
25. 提炼PX4Adapter接口
26. 写Prometheus REVIEW.md
```

最关键的源码追踪链是：

```text
Planner / User Command
        ↓
Prometheus Command
        ↓
Control State Machine
        ↓
PX4 Adapter
        ↓
MAVROS / DDS
        ↓
PX4
        ↓
Vehicle State
        ↓
Prometheus State
        ↓
Planner / Ground Station
```

只要把这条链完全理清，就掌握了 Prometheus 的核心价值。

---

# 15.16 Prometheus REVIEW.md 建议结构

```text
1. 项目定位
    PX4配套的自主无人机机载计算机软件平台

2. 它解决什么问题
    PX4通信封装
    控制命令统一
    起降和模式状态机
    定位、规划和检测集成
    Gazebo/AirSim仿真
    单机和集群任务
    仿真实机统一

3. 它不解决什么问题
    物理引擎
    飞控固件核心
    高真实感渲染
    高速GPU强化学习
    精确Sunray动力学
    完整MID360物理扫描模型

4. 核心设计
    Modules
    Simulator
    Experiment
    uav_control
    communication
    Fast-LIO
    EGO-Planner-Swarm
    sensor plugins
    swarm modules

5. 我们吸收什么
    Autonomy Middleware
    Vehicle Manager
    Command Manager
    PX4 Adapter
    控制状态机
    仿真实机一致接口
    完整Demo交付
    传感器适配层

6. 是否进入主干
    原仓库不整体进入
    中间件思想和部分模块选择性迁移

7. 风险
    旧ROS1/MAVROS历史包袱
    自定义PX4版本
    第三方代码聚合
    许可证声明不一致
    硬件绑定
    模块版本锁定
    巨型仓库维护成本

8. 第一阶段用途
    研究PX4控制封装
    MID360 + Fast-LIO + EGO完整链
    单机任务管理
    ROS2迁移

9. 长期用途
    自主中间件
    多传感器适配
    任务和安全管理
    集群控制接口
    地面站Gateway
```

---

# 15.17 最终判断

```text
是否进入长期项目：
    设计思想必须进入

是否直接作为项目主干：
    不建议整体照搬

进入哪一层：
    自主中间件层
    PX4适配层
    控制命令层
    算法集成层
    仿真实机切换层

主要吸收：
    机载计算机平台定位
    统一控制命令
    Vehicle Manager
    控制状态机
    PX4适配
    Fast-LIO/EGO集成范式
    传感器仿真与实机对齐
    单机与集群Demo
    地面站Gateway思想

不承担：
    物理后端
    最终渲染
    PX4飞控核心
    GPU训练
    唯一规划器
    唯一传感器模型
```

一句话总结：

> **RotorS 教我们如何建模无人机，XTDrone 教我们如何组织完整自主系统，而 Prometheus 最值得学习的是如何在 PX4 与上层自主算法之间建立一套真正可部署到机载计算机的控制、通信和任务中间层。我们的长期项目应吸收它的 Vehicle Manager、统一命令、控制状态机、仿真实机一致和完整 Demo 思想，但要用 ROS2、上游 PX4、插件式依赖和清晰许可证体系重新实现。**
>
