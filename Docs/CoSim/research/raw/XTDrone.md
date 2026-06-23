# 14. 项目概述：XTDrone 与 XTDrone2

## 14.1 定位

XTDrone 是建立在 **PX4、ROS、Gazebo** 之上的无人机自主系统仿真平台。它并不重新实现 Gazebo 物理，也不重新写完整飞控，而是把：

```text
Gazebo
    动力学、场景、碰撞、传感器

PX4 SITL
    状态估计、姿态控制、位置控制、飞行模式

ROS
    感知、建图、规划、编队、任务分配、通信

QGroundControl / RViz / rqt
    人机交互、监控和调试
```

组织成一个能够验证无人机自主算法的完整系统。原始 XTDrone 支持多旋翼、固定翼、复合翼以及无人车、无人船、空中机械臂等对象，并展示了 SLAM、运动规划、目标检测、多机编队、精准降落等案例。仓库采用 MIT 许可证。([GitHub](https://github.com/robin-shaun/XTDrone "GitHub - robin-shaun/XTDrone: UAV Simulation Platform based on PX4, ROS and Gazebo · GitHub"))

它与 RotorS 的区别可以先概括成：

```text
RotorS：
    更关注“无人机模型如何在 Gazebo 中运动”

XTDrone：
    更关注“感知、规划、控制、编队和任务如何组成完整自主系统”
```

所以 RotorS 更像无人机仿真的 **底层模型教材** ，XTDrone 更像无人机自主系统的 **集成框架与示例集合** 。

---

# 14.2 核心设计理念

| 设计原则             | 说明                                                       |
| -------------------- | ---------------------------------------------------------- |
| 使用成熟组件组合系统 | Gazebo 算物理，PX4 跑低层飞控，ROS 运行高层算法            |
| 分层架构             | 通信、仿真、低层控制、高层控制、协同和人机交互各自独立     |
| 消息接口标准化       | 算法模块只依赖标准化 topic 和消息，不直接依赖内部实现      |
| 单机到集群扩展       | 先建立完整单机链路，再复制和增加协调层                     |
| 高低保真并存         | 既提供 Gazebo 仿真，也提供简化仿真器快速验证集群算法       |
| 锁步运行             | 不要求仿真始终与现实时间等速，弱机器可以慢速但保持逻辑同步 |
| 算法可替换           | SLAM、检测、规划、控制和协同算法均可按接口替换             |
| 仿真到实机迁移       | 高层 ROS 算法和 PX4 飞控接口尽量保持仿真与实机一致         |
| 日志双体系           | ROS 数据用 rosbag，飞控内部数据用 PX4 ULog                 |
| 多载具统一组织       | 多旋翼、固定翼、VTOL和地面机器人共享上层架构               |

XTDrone 论文明确将系统划分为通信、仿真、低层控制、高层控制、协调和人机交互六层；各层中的任务分配、SLAM、检测、轨迹生成、控制器等模块通过定义好的输入输出接口进行替换。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

---

# 14.3 第一性原理：为什么 XTDrone 不重新制造飞控和仿真器？

如果从零开发一套无人机自主平台，需要同时解决：

```text
四旋翼动力学
碰撞和传感器
状态估计
姿态与位置控制
飞行模式
外部通信
SLAM
路径规划
任务管理
多机通信
地面站
日志分析
```

任何一个方向本身都可以成为大型项目。

XTDrone 的选择是：

```text
物理仿真：
    使用 Gazebo

飞控：
    使用 PX4

系统通信：
    使用 ROS + MAVLink + MAVROS

人机交互：
    使用 QGroundControl、RViz、rqt

平台自身：
    重点组织接口、案例和集群算法
```

论文中也明确说明，XTDrone 选择 ROS、Gazebo、PX4 和 QGroundControl 作为基础，并以 Python 为主要开发语言，同时整合部分 C++ 开源算法。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

这种思路对我们非常重要：

> **真正的生态平台不应该把所有已有能力重新写一遍，而应该重点解决各组件如何统一配置、统一通信和统一验证。**

---

# 14.4 六层架构

## 14.4.1 通信层

通信层是所有其他层的基础，负责：

```text
单机内部模块通信
多机之间通信
无人机与地面站通信
ROS算法与PX4通信
```

原 XTDrone 使用：

```text
ROS Topic
MAVLink
MAVROS
```

并封装复杂协议、统一 topic 名称，使算法开发者不必直接处理所有底层通信细节。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

它的设计逻辑是：

```text
规划器不需要理解 MAVLink
编队算法不需要理解 Gazebo Transport
目标检测不需要直接调用 PX4 内部函数

它们只需要：
    订阅标准状态
    发布标准目标或命令
```

这正是我们长期项目中 `Core Interfaces` 层应承担的职责。

---

## 14.4.2 仿真层

仿真层负责：

```text
飞行器动力学模型
传感器模型
三维场景
障碍物
其他机器人
仿真时间
```

XTDrone 主仿真器是 Gazebo，同时提供一个基于 Matplotlib 的简化仿真器，用于在早期快速调试大规模集群算法。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

这其实是非常先进的一种多保真思想：

```text
简化仿真器：
    快
    适合编队、任务分配、通信算法初步验证

Gazebo：
    较慢
    包含动力学、传感器和三维障碍

实机：
    成本最高
    用于最终验证
```

也就是：

```text
简模筛选
    ↓
高保真仿真
    ↓
实机验证
```

这与我们设计 MuJoCo、Genesis、Gazebo、UE 多后端链路的思想是一致的。

---

## 14.4.3 低层控制层

低层控制层主要交给 PX4 SITL，负责：

```text
状态估计
位置控制
速度控制
姿态控制
角速度控制
飞行模式
执行器输出
安全逻辑
```

XTDrone 原论文明确表示，低层控制层完全基于 PX4 SITL，平台更关注高层控制和集群协调；只有需要研究飞控内部算法的开发者才需要深入修改 PX4。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

这给我们的启发是：

```text
第一阶段：
    不改PX4
    用PX4原生控制器

研究重点：
    感知
    建图
    规划
    任务
    集群

后续确有需要：
    再替换PX4某个控制层
```

否则一开始同时调：

```text
动力学
状态估计
姿态控制
路径规划
传感器
```

出现问题时几乎无法定位。

---

## 14.4.4 高层控制层

高层控制负责单架无人机的智能行为：

```text
目标检测
目标追踪
SLAM
视觉惯性定位
局部地图
运动规划
避障
轨迹生成
```

XTDrone 仓库和文档展示了双目 SLAM、视觉惯性导航、稠密重建、二维/三维激光 SLAM、运动规划、目标检测和追踪等示例。([GitHub](https://github.com/robin-shaun/XTDrone "GitHub - robin-shaun/XTDrone: UAV Simulation Platform based on PX4, ROS and Gazebo · GitHub"))

这层通常运行在：

```text
ROS节点
C++
Python
伴随计算机
```

而不是运行在 PX4 飞控 MCU 内。

放到我们的平台就是：

```text
MID360
    ↓
Fast-LIO / Localization
    ↓
Local Map
    ↓
EGO / Planner
    ↓
Trajectory
    ↓
PX4 Offboard
```

---

## 14.4.5 协调层

协调层只在多机任务中出现，负责：

```text
任务分配
协同搜索
编队
一致性控制
队形变换
多机避碰
通信拓扑
集群任务规划
```

XTDrone 的多机论文给出了协同搜索和分布式编队案例，其中编队案例包含一致性控制、任务分配和避障。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

需要注意一个层次问题：

```text
低层控制：
    一架飞机如何稳定飞行

高层控制：
    一架飞机如何完成自己的局部任务

协调层：
    多架飞机如何决定各自应该完成什么任务
```

例如协同搜索：

```text
协调层：
    将搜索区域分成六块

高层规划：
    每架无人机规划自己负责区域的轨迹

PX4：
    跟踪对应轨迹
```

三层不能混成一个算法。

---

## 14.4.6 人机交互层

人机交互层负责：

```text
地面站
任务设置
状态监控
参数调整
手动控制
轨迹和地图显示
日志分析
```

XTDrone 使用 QGroundControl 监控 PX4 低层状态，通过 ROS 工具、RViz、rqt 和键盘控制器监控高层及协调层；论文还强调 ROSBag 和 PX4 ULog 的双重日志作用。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

我们的平台可对应为：

```text
QGroundControl：
    PX4与飞控参数

RViz2：
    点云、地图、轨迹、TF

UE：
    高质量任务展示

Web / Qt Panel：
    实验管理和指标

rosbag2：
    ROS2数据

ULog：
    PX4内部飞控数据
```

---

# 14.5 XTDrone 最重要的设计：单机先完整，再扩展多机

很多集群项目一上来就创建几十架无人机，但单机链路都没有跑通。

XTDrone 的论文明确提出，它首先是单机仿真平台，然后才扩展成多机仿真平台。([arXiv](https://arxiv.org/abs/2005.01125 "Implementation of UAV Coordination Based on a Hierarchical Multi-UAV Simulation Platform"))

正确顺序是：

```text
单机动力学
    ↓
单机PX4控制
    ↓
单机感知
    ↓
单机定位
    ↓
单机规划
    ↓
单机任务成功
    ↓
复制多机实例
    ↓
增加协调层
```

错误顺序是：

```text
先启动20架无人机
    ↓
再同时排查：
    端口
    命名空间
    坐标
    控制
    地图
    通信
    算法
```

对我们的长期项目来说，应规定：

```text
M1：
    Sunray-150单机闭环

M2：
    单机MID360 + 建图 + 规划

M3：
    两机独立运行

M4：
    两机避碰和通信

M5：
    编队与协同任务

M6：
    大规模集群简化仿真
```

---

# 14.6 多机系统中真正困难的不是“复制模型”

启动十架无人机不只是复制十份 Gazebo 模型。

每架飞机都需要独立的：

```text
PX4 SITL instance
MAVLink端口
ROS namespace
vehicle_id
tf frame
topic
初始位置
参数文件
日志目录
控制节点
```

例如概念上：

```text
/uav_0/
    odometry
    trajectory
    setpoint
    lidar

/uav_1/
    odometry
    trajectory
    setpoint
    lidar
```

同时还需要全局层：

```text
/swarm/
    mission
    formation
    assignment
    neighbor_graph
    global_map
```

XTDrone 的真正价值之一，就是将多机仿真从“复制若干模型”提升成了 **分层、命名空间化和任务化的系统组织问题** 。

---

# 14.7 锁步模式的意义

XTDrone 强调 lockstep：不同求解器和控制模块保持同步，计算机性能不足时仿真可以慢于现实，但不能让模块各自跑散。([arXiv](https://arxiv.org/abs/2003.09700 "XTDrone: A Customizable Multi-Rotor UAVs Simulation Platform"))

例如：

```text
理想实时：
    现实1秒 = 仿真1秒

电脑性能不足：
    现实3秒 = 仿真1秒
```

虽然运行慢了，但仿真时间中仍然保持：

```text
传感器在 t=1.00 s
规划器在 t=1.00 s
PX4在 t=1.00 s
Gazebo在 t=1.00 s
```

而不是：

```text
Gazebo在 t=1.00
PX4在 t=1.08
ROS在 t=0.92
```

这对于多机尤其重要，否则不同车辆之间的同步、避碰和编队结果不可信。

我们应吸收为统一的：

```text
SimulationClock
    pause
    resume
    step
    reset
    real_time_factor
    simulation_time
    step_id
```

---

# 14.8 简化仿真器的真正价值

XTDrone 的简化仿真器并不是为了替代 Gazebo，而是为了提前回答：

```text
编队算法逻辑对不对？
任务分配是否收敛？
通信拓扑是否合理？
队形切换是否发生冲突？
数十架无人机的高层行为是否正确？
```

这些问题不一定需要：

```text
每个桨叶
每个IMU
每个碰撞网格
每个PX4实例
```

都完整运行。

所以可先使用简化模型：

```text
点质量
或
简化运动学

状态：
    位置
    速度

控制：
    期望速度
```

高层算法通过后，再进入 Gazebo 验证动力学和传感器影响。

这正是我们可以采用的三层多机体系：

```text
Level 1：简化集群仿真
    Python/C++二维或三维运动学

Level 2：高速动力学
    MuJoCo / Genesis / PyBullet

Level 3：工程仿真
    Gazebo + PX4 + ROS2
```

---

# 14.9 XTDrone 仓库结构体现了什么？

当前原始仓库顶层包含：

```text
communication
control
coordination
motion_planning
sensing
sitl_config
ros2/formation_demo
```

等目录。([GitHub](https://github.com/robin-shaun/XTDrone "GitHub - robin-shaun/XTDrone: UAV Simulation Platform based on PX4, ROS and Gazebo · GitHub"))

这体现了它并不是按“某个技术库”分类，而是按自主系统功能分类：

```text
感知
规划
控制
协同
通信
仿真配置
```

这种组织方式适合教学和案例阅读，但对大型长期平台还应再加一层“接口与后端隔离”。

我们可以改造成：

```text
core/
    interfaces
    time
    state
    config

backends/
    gazebo
    mujoco
    genesis
    unreal

autonomy/
    perception
    localization
    mapping
    planning
    control

swarm/
    communication
    assignment
    formation
    avoidance

tools/
    visualization
    logging
    evaluation
```

这样既保留 XTDrone 的功能分层，又适应多后端架构。

---

# 14.10 XTDrone2：现代化迁移

原 XTDrone 以 ROS1 和旧 Gazebo 技术栈为主。其主仓库目前已经指向 ROS2 版本 XTDrone2；XTDrone2 的官方仓库说明，它采用  **PX4、ROS2 和 Gazebo Ignition** ，当前使用 PX4 1.15，并将代码拆分成通信、控制、Gazebo仿真、启动、消息和测试等包。([GitHub](https://github.com/robin-shaun/XTDrone "GitHub - robin-shaun/XTDrone: UAV Simulation Platform based on PX4, ROS and Gazebo · GitHub"))

XTDrone2 当前目录包括：

```text
xtd2_communication
xtd2_control
xtd2_gz_sim
xtd2_launch
xtd2_msgs
xtd2_test
xtd2_third_party_pkgs
```

这比原版更接近现代 ROS2 包结构。([GitHub](https://github.com/andy-zhuo-02/XTDrone2 "GitHub - andy-zhuo-02/XTDrone2: UAV Simulation Platform based on PX4, ROS2 and Gazebo Ignition · GitHub"))

但其仓库也明确标注：

```text
仍处于前期开发迭代阶段
文档和代码可能频繁变化
```

并把固定翼、无人车通信适配、EGO-Planner-Swarm 和多机控制列为后续功能。([GitHub](https://github.com/andy-zhuo-02/XTDrone2 "GitHub - andy-zhuo-02/XTDrone2: UAV Simulation Platform based on PX4, ROS2 and Gazebo Ignition · GitHub"))

因此对我们来说：

```text
原XTDrone：
    学完整架构和丰富案例

XTDrone2：
    学ROS2迁移和新Gazebo包结构

都不应该：
    原封不动成为我们的项目底座
```

---

# 14.11 XTDrone 与我们项目的关系

## 14.11.1 它比 RotorS 更接近我们的“系统层”

RotorS 重点回答：

```text
电机命令如何变成Gazebo中的力？
```

XTDrone 重点回答：

```text
SLAM、规划、PX4、Gazebo、地面站和多机算法如何组成一套系统？
```

因此：

```text
RotorS：
    参考仿真后端

XTDrone：
    参考自主系统集成
```

---

## 14.11.2 它比 RflySim 更开源生态化

RflySim 主要围绕：

```text
Simulink
PX4
CopterSim
HIL
RflySim3D
```

XTDrone 主要围绕：

```text
ROS
Gazebo
PX4
开源SLAM和规划算法
```

我们长期项目显然更接近 XTDrone 方向，但要进一步现代化为：

```text
ROS2
新Gazebo
PX4 uXRCE-DDS
多后端训练
独立UE前端
```

---

## 14.11.3 它与我们的 UE 双世界路线不冲突

XTDrone 原本主要使用 Gazebo 显示，但其真正核心是自主算法分层，而不是 Gazebo 画面。

我们可以保留：

```text
XTDrone式：
    感知—规划—控制—协同分层
```

同时替换显示层：

```text
Gazebo：
    后台真值

UE：
    前台展示
```

---

# 14.12 我们应该吸收 XTDrone 的哪些设计？

## 吸收一：六层自主系统架构

建议转化为：

```text
L0 仿真和硬件层
    Gazebo、传感器、实机

L1 飞控层
    PX4

L2 单机自主层
    定位、建图、规划

L3 集群协调层
    任务分配、编队、避碰

L4 系统通信层
    ROS2、DDS、MAVLink

L5 人机交互层
    QGC、RViz2、UE、Web UI
```

通信层虽然逻辑上贯穿全部层，但在代码上应成为独立基础设施。

---

## 吸收二：单机算法与集群算法分离

```text
单机规划器：
    只负责本机局部可行轨迹

集群协调器：
    负责分配目标、队形和优先级
```

不要写一个巨型“集群规划器”同时管理所有细节。

---

## 吸收三：简化仿真与高保真仿真共存

```text
高层逻辑：
    简化仿真快速测试

动力学与飞控：
    Gazebo + PX4测试
```

这与我们的多后端设计天然兼容。

---

## 吸收四：标准化命名空间

必须统一：

```text
vehicle_id
namespace
frame_prefix
PX4 instance
MAVLink port
ROS2 domain/topic
log path
```

否则多机规模稍大就会失控。

---

## 吸收五：日志双通道

```text
rosbag2：
    感知、地图、规划、任务、集群

ULog：
    PX4估计、控制、执行器和failsafe
```

两者通过统一实验 ID 关联。

---

## 吸收六：算法模块可替换

例如：

```text
LocalizationBackend
    Fast-LIO
    VIO
    PX4 EKF
    GroundTruth

PlannerBackend
    EGO
    A*
    MPC
    RL

CoordinatorBackend
    Leader-Follower
    Consensus
    Task Allocation
```

---

## 吸收七：从仿真到实机保持接口

仿真中：

```text
Gazebo LiDAR
PX4 SITL
```

实机中：

```text
真实MID360
真实PX4
```

上层定位和规划节点的接口尽量不变。

---

# 14.13 不应该照搬什么？

## 不照搬一：不要沿用原 ROS1/MAVROS 主架构

长期主线应优先采用：

```text
ROS2
PX4 uXRCE-DDS
px4_msgs
新Gazebo
```

MAVLink/MAVSDK 可以保留为兼容接口，但不必成为所有内部数据的唯一通道。PX4 当前官方 ROS 页面已将 ROS2、uXRCE-DDS 和 ROS2 多机仿真列为主要集成路线，而 ROS1 已进入 deprecated 部分。([PX4 文档](https://docs.px4.io/main/en/ros/ "PX4 Guide (main)"))

---

## 不照搬二：不要把案例脚本当平台接口

原项目中很多代码以具体演示为中心。

我们需要将其进一步抽象为：

```text
接口
插件
配置
测试
```

而不是不断增加：

```text
demo_1.py
demo_2.py
demo_final_new.py
```

---

## 不照搬三：不要让所有多机数据集中经过一个中心节点

小规模演示可以由一个地面站管理所有无人机。

大规模集群应区分：

```text
中心式任务管理
分布式邻居通信
本地自主决策
```

否则中心节点会成为性能和可靠性瓶颈。

---

## 不照搬四：不要同时为每架无人机运行所有高成本模块

例如十架无人机都运行：

```text
高分辨率相机
MID360
SLAM
目标检测
Gazebo渲染
UE渲染
```

计算成本会迅速失控。

需要支持：

```text
传感器按需启用
算法进程按需启用
共享地图
简化代理机
混合保真集群
```

---

## 不照搬五：不要把“可迁移实机”当作自动成立

使用 ROS 和 PX4 确实有利于迁移，但还必须处理：

```text
算力
实时性
网络
传感器驱动
坐标系
时间同步
安全逻辑
硬件接口
模型误差
```

仿真接口相同只是迁移的必要条件，不是充分条件。

---

# 14.14 在长期架构中的位置

XTDrone 不需要作为一个完整运行时依赖，而应作为 **自主系统层和集群层的设计来源** ：

```text
                         UE展示前端
                              ↑
                    Human Interaction Layer
                              ↑
┌──────────────────────────────────────────────────┐
│                ROS2 Communication Layer          │
│ State / Map / Trajectory / Mission / Swarm       │
└───────↑────────────────↑────────────────↑────────┘
        │                │                │
    Simulation       Autonomy        Coordination
 Gazebo/PX4      SLAM/Planning     Formation/Task
        │                │                │
        └──────── Unified Interfaces ─────┘
```

XTDrone 给我们最重要的不是某个算法，而是：

```text
系统怎么分层
多机怎么组织
算法怎么替换
低层PX4与高层自主怎么分工
简模和高保真仿真怎么配合
```

---

# 14.15 最小研究任务

针对 XTDrone 和 XTDrone2，建议依次完成：

```text
1. 画出XTDrone六层架构
2. 追踪单机完整数据流
3. 理清ROS、MAVROS、MAVLink和PX4的边界
4. 理清Gazebo、PX4 SITL和QGroundControl的关系
5. 分析communication目录
6. 分析control目录
7. 分析sensing目录
8. 分析motion_planning目录
9. 分析coordination目录
10. 跑通单机位置控制
11. 跑通单机传感器和规划示例
12. 跑通两机独立控制
13. 理清多PX4实例的端口配置
14. 理清namespace和tf隔离
15. 跑通简化集群仿真
16. 对比简模与Gazebo编队结果
17. 阅读XTDrone2包结构
18. 追踪XTDrone2 ROS2通信接口
19. 追踪XTDrone2与新Gazebo的桥接
20. 对比XTDrone与XTDrone2的接口变化
21. 提炼我们自己的Autonomy API
22. 提炼我们自己的Swarm API
23. 写XTDrone REVIEW.md
```

最关键的两条链路是：

```text
单机：
Sensor
    → Localization
    → Planning
    → PX4
    → Gazebo
    → Sensor
```

以及：

```text
多机：
Mission
    → Coordination
    → Per-UAV Goal
    → Per-UAV Planner
    → Per-UAV PX4
```

---

# 14.16 REVIEW.md 建议结构

```text
1. 项目定位
    PX4 + ROS + Gazebo自主无人机与集群仿真平台

2. 它解决什么问题
    单机自主系统集成
    SLAM和规划验证
    多机编队与任务协调
    多载具仿真
    仿真到实机接口复用

3. 它不解决什么问题
    新Gazebo底层物理设计
    高速GPU强化学习
    高保真UE展示
    精确Sunray动力学
    完整MID360设备模型

4. 核心设计
    六层架构
    PX4低层控制
    ROS高层智能
    Gazebo仿真
    Lockstep
    简化集群仿真
    标准消息
    双日志系统

5. 我们吸收什么
    系统分层
    单机到多机演进
    简模和高保真共存
    命名空间和多实例
    算法可替换
    协调层设计
    仿真实机统一接口

6. 是否进入主干
    设计思想进入
    原项目案例选择性参考
    ROS2实现优先参考XTDrone2

7. 风险
    原版ROS1和Gazebo Classic依赖
    XTDrone2仍处早期迭代
    多机资源消耗
    案例接口不够统一
    版本和端口配置复杂
    算法与平台耦合

8. 第一阶段用途
    单机自主链路
    两机控制
    多机命名空间
    集群架构设计

9. 长期用途
    集群任务
    编队
    协同搜索
    多机避障
    混合载具系统
```

---

# 14.17 最终判断

```text
是否进入长期项目：
    架构思想必须进入

是否直接作为项目主干：
    不直接照搬

进入哪一层：
    自主系统集成层
    多机协调层
    多实例管理层
    算法示例参考层

主要吸收：
    六层架构
    ROS/PX4/Gazebo分工
    单机到多机演进
    简化仿真器
    Lockstep
    命名空间管理
    协调层
    日志和人机交互

不承担：
    最终物理内核
    最终UE渲染
    GPU大规模RL
    Sunray精确动力学
    MID360完整仿真
```

一句话总结：

> **RotorS 教我们怎么让多旋翼在 Gazebo 里“飞”；XTDrone 教我们怎么把感知、建图、规划、PX4、Gazebo、地面站和多机协调组织成一个完整自主系统。我们应吸收它的分层、多实例和简化—高保真两级验证思想，再使用 ROS2、新 Gazebo、PX4 uXRCE-DDS 和独立 UE 前端重新实现。**
>
