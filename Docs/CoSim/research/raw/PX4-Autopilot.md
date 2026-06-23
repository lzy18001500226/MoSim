# 2. 项目概述：PX4-Autopilot

## 2.1 定位

PX4 是一个开源无人机飞控软件栈，核心定位不是“仿真器”，也不是“渲染器”，而是 **无人机飞控标准层** 。它负责把无人机从“算法期望”变成“实际电机输出”，包括传感器融合、飞行模式、姿态控制、位置控制、控制分配、电机输出、安全保护、任务执行、通信接口等。PX4 官网将其定位为开源无人机和自主载具飞控软件，并强调它提供标准化的软件栈和硬件支持生态。([PX4 Autopilot](https://px4.io/?utm_source=chatgpt.com "PX4 Autopilot: Open Source Autopilot for Drones"))

对你们长期项目来说，PX4 的定位应该是：

```text
Gazebo：
    真值仿真世界

UE：
    高真实感展示世界

ROS2：
    系统总线和算法生态

PX4：
    飞控标准层

Simulink：
    可选控制器设计和代码生成入口
```

也就是说，PX4 在你们架构里不是“一个可有可无的软件”，而是决定平台是否接近真实无人机工程的核心模块。

它负责：

```text
飞行模式
解锁/上锁
failsafe
姿态控制
位置控制
速度控制
控制分配
电机输出
传感器融合
参数管理
任务执行
MAVLink 通信
ROS2/uORB 接口
SITL/HIL/实机一致性
```

它不负责：

```text
高真实感渲染
UE 地图显示
未知环境建图
局部路径规划主循环
MID360 点云处理
强化学习训练框架
```

所以一句话：

> **PX4 是无人机的“飞控大脑和执行标准”，不是仿真世界，也不是规划器。**

---

## 2.2 核心设计理念

| 设计原则          | 说明                                                             |
| ----------------- | ---------------------------------------------------------------- |
| 模块化飞控栈      | 姿态控制、位置控制、传感器融合、通信、控制分配等模块相互独立     |
| uORB 消息总线     | PX4 内部模块通过 uORB 发布/订阅消息，而不是直接函数耦合          |
| 飞行模式驱动      | Manual、Altitude、Position、Mission、Offboard 等模式决定控制入口 |
| 安全优先          | 解锁、failsafe、电池、电台、RC、GPS、传感器异常都有保护逻辑      |
| SITL/HIL/实机一致 | 同一套飞控代码可以在软件仿真、硬件在环和实机上运行               |
| 参数化配置        | 机型、电机方向、控制增益、传感器、failsafe 都通过参数配置        |
| 外部生态接入      | 通过 MAVLink、uXRCE-DDS、ROS2、MAVSDK 等和外部算法通信           |

PX4 官方文档说明其架构是模块化的，内部模块通信基于 uORB；PX4 GitHub 也强调 PX4 built around uORB，模块并行、线程安全、可裁剪配置。([PX4 文档](https://docs.px4.io/main/en/concept/architecture?utm_source=chatgpt.com "PX4 Architectural Overview | PX4 Guide (main)"))

这对你们很重要，因为你们不是要重新造飞控，而是要让自己的平台能够：

```text
接入真实飞控逻辑
接入真实飞控接口
将仿真控制器最终迁移到实机
```

---

## 2.3 系统设计逻辑

### 2.3.1 第一性原理：为什么要用 PX4，而不是自己写一个飞控？

你们完全可以自己写一个简单四旋翼控制器：

```text
轨迹输入
    ↓
位置 PID
    ↓
姿态 PID
    ↓
控制分配
    ↓
电机输出
```

这在论文 demo 或 Simulink 仿真里没问题。

但如果要做“真正项目”，问题就出来了：

```text
飞行模式谁管理？
解锁/上锁谁管理？
RC 丢失怎么办？
电池低电压怎么办？
传感器异常怎么办？
Offboard 超时怎么办？
电机输出限幅怎么办？
实机部署怎么办？
地面站怎么接？
日志怎么记录？
参数怎么管理？
```

这些不是控制器公式能解决的，而是飞控系统工程问题。

PX4 的价值就在这里：它提供了一整套已经被无人机生态验证过的飞控框架。你们不用从零开始写“无人机操作系统”，而是把自己的算法接到 PX4 的标准入口上。

所以对你们来说：

```text
自己写控制器：
    适合算法验证

PX4：
    适合工程闭环、仿真到实机迁移
```

---

### 2.3.2 第二性原理：PX4 的核心不是控制律，而是飞控系统栈

很多人一开始会误解 PX4，以为 PX4 就是几个 PID 控制器。其实不是。

PX4 更像一个完整飞控系统：

```text
传感器驱动
    ↓
状态估计
    ↓
飞行模式管理
    ↓
任务/Offboard/手动输入
    ↓
位置控制
    ↓
姿态控制
    ↓
角速度控制
    ↓
控制分配
    ↓
执行器输出
    ↓
日志/通信/failsafe
```

其中控制器只是中间一段。

真正让 PX4 有工程价值的是：

```text
模块化
消息总线
参数系统
安全系统
仿真/实机一致性
地面站生态
硬件生态
```

所以你们长期项目如果只做 Gazebo + UE + 自己写控制器，会很好看，但不够工程化。接上 PX4，平台就从“仿真动画”变成“飞控闭环仿真”。

---

### 2.3.3 第三性原理：uORB 是 PX4 内部的神经网络

PX4 内部不是所有模块互相调用，而是通过 uORB 消息发布/订阅。

可以这样理解：

```text
传感器模块发布：
    vehicle_imu
    sensor_combined

状态估计模块发布：
    vehicle_odometry
    vehicle_local_position
    vehicle_attitude

控制模块订阅：
    vehicle_local_position
    vehicle_attitude
    trajectory_setpoint

控制模块发布：
    vehicle_attitude_setpoint
    vehicle_rates_setpoint
    actuator_motors
    actuator_controls

通信模块发布/订阅：
    vehicle_command
    offboard_control_mode
    trajectory_setpoint
```

uORB 的好处是：

```text
模块之间低耦合
方便替换模块
方便日志记录
方便仿真和实机共用同一套数据流
方便 ROS2 映射
```

PX4 和 ROS2 的 uXRCE-DDS 集成就是把一部分 uORB 消息桥接到 ROS2，让外部 ROS2 节点能像订阅 ROS2 topic 一样订阅 PX4 信息，或者向 PX4 发布命令。PX4 官方文档明确说明，uXRCE-DDS 允许 uORB messages 在伴随计算机上像 ROS2 topics 一样发布和订阅。([PX4 文档](https://docs.px4.io/main/en/middleware/uxrce_dds?utm_source=chatgpt.com "uXRCE-DDS (PX4-ROS 2/DDS Bridge) | PX4 Guide (main)"))

这对你们平台非常关键：

```text
ROS2/C++ 规划器
    ↓
发布 trajectory_setpoint / offboard_control_mode
    ↓
PX4
    ↓
控制飞机
```

---

## 2.4 PX4 的飞控分层

### 2.4.1 高层输入

PX4 可以接受多种控制来源：

```text
遥控器输入
任务航点
地面站任务
Offboard 外部控制
Failsafe 自动逻辑
```

对你们项目最重要的是  **Offboard 模式** 。因为未知地图规划、EGO/MPC/RL policy 都不应该直接改 PX4 内部，而应该通过 Offboard 或 ROS2 接口发送 setpoint。

例如：

```text
规划器输出：
    p_des
    v_des
    a_des
    yaw_des

ROS2 节点发布：
    trajectory_setpoint
    offboard_control_mode
    vehicle_command

PX4 接收：
    外部期望轨迹

PX4 执行：
    位置/速度/姿态/电机控制
```

也就是说，PX4 给你们的规划器留了一个标准入口。

---

### 2.4.2 中层控制

PX4 内部控制大致可以理解成串级结构：

```text
位置控制器
    输入：期望位置/速度/加速度
    输出：期望姿态/推力

姿态控制器
    输入：期望姿态
    输出：期望角速度

角速度控制器
    输入：期望角速度
    输出：力矩/控制量

控制分配
    输入：总推力 + 三轴力矩
    输出：各电机命令
```

对你们项目来说，这里有两个选择：

```text
选择 A：
    保留 PX4 原生控制器
    你们只做规划器和 setpoint

选择 B：
    自己设计控制器
    通过 ROS2 node 或 PX4 module 替换某一层控制器
```

第一阶段建议选择 A。因为你们先要把系统跑通：

```text
Gazebo 真值世界
PX4 飞控
ROS2 状态
UE 展示
```

等平台稳定后，再研究：

```text
自定义轨迹跟踪控制器
Simulink 生成控制器
电机退化补偿控制器
抗风扰控制器
容错控制器
```

---

### 2.4.3 底层执行

PX4 最后要输出到执行器：

```text
电机
舵机
云台
其他 actuator
```

对于四旋翼，就是四个电机输出。PX4 会根据机型配置、控制分配矩阵、电机方向、限幅等，把期望推力/力矩变成电机命令。

这对你们做云纵 Sunray-150 非常重要：

```text
电机编号必须一致
电机旋转方向必须一致
坐标系必须一致
控制分配矩阵必须一致
推力系数必须一致
反扭矩方向必须一致
```

否则最常见的问题就是：

```text
一解锁就翻
yaw 方向反了
roll/pitch 互换
电机顺序错
控制器看似没问题但飞机炸
```

所以 PX4 接入不是简单“能启动就行”，而是要严格校验机型配置。

---

## 2.5 PX4 与 Gazebo 的关系

PX4 和 Gazebo 的关系可以理解为：

```text
PX4：
    我是飞控，我需要传感器数据，我输出电机命令。

Gazebo：
    我是仿真世界，我给你虚拟传感器，我根据电机命令算飞机运动。
```

在 SITL 中：

```text
PX4 软件进程
    ↓ 输出电机命令
Gazebo
    ↓ 计算动力学、传感器
PX4
    ↓ 根据虚拟传感器继续控制
```

PX4 官方 Gazebo 文档说明，Gazebo 是开源机器人仿真器，PX4 支持 quadrotor、plane、VTOL、rover 等车辆仿真；新版本 Gazebo/gz-sim 是 Ubuntu 22.04 及之后唯一支持的 Gazebo 版本。([PX4 文档](https://docs.px4.io/main/en/sim_gazebo_gz/?utm_source=chatgpt.com "Gazebo Simulation | PX4 Guide (main)"))

所以你们的长期项目如果选：

```text
Gazebo = 真值仿真世界
PX4 = 飞控闭环
```

这是很自然的路线。

---

## 2.6 PX4 与 ROS2 的关系

ROS2 是外部算法生态，PX4 是飞控执行生态。

二者关系应该是：

```text
ROS2：
    感知
    建图
    规划
    任务调度
    强化学习 policy
    日志/可视化
    UE 状态同步

PX4：
    飞控
    模式
    姿态/位置控制
    执行器输出
    failsafe
```

连接方式主要有两类：

```text
MAVLink / MAVROS / MAVSDK：
    传统方式，常见于 ROS1/旧生态/地面站/外部控制

uXRCE-DDS / ROS2：
    新的深度集成方式，把 uORB topic 映射到 ROS2
```

PX4 官方 ROS2 文档明确说，ROS2 是可与 PX4 Autopilot 一起使用的通用机器人库，官方强烈建议使用/迁移到 ROS2，因为它改善了与 PX4 的深度、低延迟集成。([PX4 文档](https://docs.px4.io/main/en/ros2/?utm_source=chatgpt.com "ROS 2 | PX4 Guide (main)"))

所以你们长期项目应该优先考虑：

```text
PX4 + ROS2 + uXRCE-DDS
```

而不是旧的 ROS1/MAVROS 主线。

---

## 2.7 PX4 与 UE 的关系

PX4 不关心 UE。

PX4 只关心：

```text
传感器数据
控制输入
状态估计
电机输出
飞行模式
failsafe
```

UE 只需要从 ROS2 或 bridge 拿到 PX4/Gazebo 的状态：

```text
vehicle pose
vehicle attitude
trajectory
mode
battery
warning
collision event
```

然后显示：

```text
无人机 Actor
桨叶动画
轨迹线
HUD
镜头
高真实感地图
```

所以：

```text
PX4 → Gazebo → ROS2 → UE
```

或者：

```text
PX4/Gazebo 状态 → UDP → UE
```

PX4 不应该直接依赖 UE。UE 是显示前端，不能成为飞控链路的硬依赖。

---

## 2.8 PX4 与 Simulink 的关系

Simulink 在长期项目里不是主干，但它可以和 PX4 有两种关系。

### 关系 A：Simulink 生成外部 ROS2 控制器

```text
Simulink 控制器
    ↓ 生成 ROS2 node
ROS2 node 订阅 PX4/Gazebo 状态
    ↓
发布 setpoint
    ↓
PX4 Offboard 接收
```

这种方式侵入性小，适合验证控制器。

### 关系 B：Simulink 生成 PX4 内部模块

```text
Simulink 控制器
    ↓ 生成 C/C++
    ↓
编译进 PX4
    ↓
通过 uORB 读状态、写控制输出
```

这种方式更接近实机部署，但工程难度更高。

你们如果工具箱授权不全，长期项目就不要强依赖这条线。可以把 Simulink 生成控制器作为“可选分支”，不作为主干。

---

## 2.9 PX4 的 SITL / HIL / 实机路径

PX4 最重要的工程价值之一是，它让你们可以按照真实无人机开发流程走：

```text
SITL：
    软件在环
    PX4 软件进程 + Gazebo 仿真世界

HIL/HITL：
    硬件在环
    真实飞控硬件运行 PX4
    Gazebo 或其他仿真器提供虚拟传感器和动力学

Real Flight：
    实机飞行
    真实传感器、真实电机、真实环境
```

PX4 官方 HIL 文档说明，HITL/HIL 是一种仿真模式，其中正常 PX4 firmware 运行在真实飞控硬件上，这样可以测试大部分实际飞行代码。([PX4 文档](https://docs.px4.io/main/en/simulation/hitl?utm_source=chatgpt.com "Hardware in the Loop Simulation (HITL) | PX4 Guide (main)"))

这说明 PX4 对你们的长期项目很关键：

```text
只做 Gazebo：
    是仿真平台

接入 PX4 SITL：
    是飞控仿真平台

支持 HIL：
    是准工程验证平台

能迁移实机：
    才是真正无人机平台
```

---

## 2.10 PX4 的系统设计方法论

### 2.10.1 模块化

PX4 不是一个巨大的 main 函数，而是一组模块：

```text
commander
navigator
mc_pos_control
mc_att_control
ekf2
mavlink
logger
sensors
control_allocator
```

模块之间通过 uORB 通信。

你们应该吸收这个思想：长期项目也要插件化，不要写成一个大程序。

```text
vehicle plugin
sensor plugin
planner plugin
controller plugin
logger plugin
ue_bridge plugin
```

---

### 2.10.2 参数化

PX4 几乎所有飞控关键行为都由参数控制：

```text
控制增益
限幅
failsafe
传感器配置
电机输出
机型配置
通信配置
```

你们平台也应该参数化，而不是写死：

```text
vehicle.yaml
motor.yaml
sensor.yaml
experiment.yaml
controller.yaml
planner.yaml
```

这点非常重要。否则后期切换云纵模型、换电机、换传感器、换规划器都会很痛苦。

---

### 2.10.3 标准消息流

PX4 的设计启发是：系统不是靠函数调用串起来，而是靠标准消息流串起来。

你们长期项目应该也这样：

```text
状态消息：
    odometry
    attitude
    velocity

传感器消息：
    pointcloud
    imu
    camera

规划消息：
    trajectory
    goal

控制消息：
    setpoint
    actuator

事件消息：
    collision
    failsafe
    task_status
```

这正好和 ROS2 的思想一致。

---

## 2.11 我们应该吸收 PX4 哪些设计？

### 吸收 1：飞控不要自己重写

长期项目不应该从零写完整飞控。你们应该把 PX4 作为默认飞控层。

```text
默认飞控：
    PX4

自定义控制器：
    作为 PX4 外部输入或内部模块
```

---

### 吸收 2：Offboard 接口

未知地图规划、EGO、MPC、RL policy 都应该优先通过 Offboard/setpoint 接入。

```text
planner
    ↓
trajectory_setpoint
    ↓
PX4 Offboard
    ↓
PX4 控制器
```

第一阶段不要直接改 PX4 内部控制器。

---

### 吸收 3：uORB / ROS2 映射思想

你们要建立自己的系统消息规范，借鉴 PX4 的 uORB 思路。

```text
内部模块解耦
消息驱动
日志可记录
仿真/实机一致
```

---

### 吸收 4：SITL/HIL/实机三阶段

项目验证路径必须明确：

```text
仿真算法验证
PX4 SITL
PX4 HIL
实机
```

这比单纯“仿真跑通”更有工程价值。

---

### 吸收 5：参数系统

所有机型、电机、传感器、控制器、实验场景都应该参数化。

```text
不要写死在代码里
不要依赖手动配置
不要每次改模型都重写逻辑
```

---

## 2.12 我们不应该照搬 PX4 的地方

### 不照搬 1：不要把所有算法都塞进 PX4

PX4 是飞控，不是你们全部算法容器。

不要把：

```text
SLAM
点云处理
EGO 规划
RL policy
地图构建
UE 同步
```

全部塞进 PX4。

这些应该在 ROS2/C++/Python 侧。

---

### 不照搬 2：不要一开始就改 PX4 内核

PX4 内核复杂，第一阶段改它很容易把问题搞乱。

第一阶段应该：

```text
PX4 原样跑
ROS2 外部发 setpoint
Gazebo 算真值
UE 显示
```

等链路稳定，再考虑自定义控制器或控制分配。

---

### 不照搬 3：不要把 PX4 当动力学仿真器

PX4 不负责物理世界。动力学由 Gazebo/CopterSim/其他后端算。PX4 输出控制，仿真器反馈传感器和状态。

---

### 不照搬 4：不要忽视坐标系

PX4 常用 NED，ROS/Gazebo 常用 ENU/Z-up。坐标系不统一，会导致很多诡异问题。

你们必须建立统一转换层：

```text
PX4 NED
ROS ENU
Gazebo world
UE world
```

---

## 2.13 在你们架构里的位置

最终架构应该是：

```text
                 ┌────────────────────┐
                 │        UE 前台       │
                 │ 高真实感显示/演示画面 │
                 └─────────↑──────────┘
                           │
                     状态同步桥
                           │
┌──────────────────────────┴──────────────────────────┐
│                    ROS2 总线                          │
│ odom / tf / lidar / trajectory / setpoint / log       │
└───────────────↑──────────────────────────↓───────────┘
                │                          │
          Gazebo/gz-sim                规划/控制节点
      真值物理/传感器/碰撞            C++ / Python / Simulink生成
                │                          │
                └──────────── PX4 ─────────┘
```

PX4 在里面的位置是：

```text
飞控闭环核心
```

它一边接 Gazebo 的传感器/状态，一边接 ROS2 的 setpoint/command，然后输出控制量给 Gazebo。

---

## 2.14 最小落地任务

针对 PX4，你们第一阶段应该做这些：

```text
1. 下载并能编译运行 PX4-Autopilot
2. 跑通 PX4 SITL + Gazebo quadrotor
3. 明确 PX4 和 Gazebo 之间的数据流
4. 用 ROS2 读取 PX4 状态
5. 用 ROS2 向 PX4 发送 Offboard setpoint
6. 跑通起飞、悬停、航点、轨迹跟踪
7. 记录 ulog / rosbag
8. 明确机型配置、电机顺序、坐标系
9. 后台 Gazebo，前台 UE 同步显示
10. 写 PX4 REVIEW.md
```

第一阶段成功标准：

```text
PX4 SITL 能启动
Gazebo 里飞机能起飞
ROS2 能读到状态
ROS2 能发送目标点
UE 能同步显示
日志能记录并回放
```

---

## 2.15 PX4 REVIEW.md 应该写什么

你们每个仓库都应该有一个 REVIEW.md。PX4 的 REVIEW.md 可以这样写：

```text
1. 项目定位
    开源无人机飞控软件栈

2. 它解决什么问题
    飞行模式、控制器、状态估计、执行器输出、安全保护、SITL/HIL

3. 它不解决什么问题
    高真实感渲染、未知地图规划、点云处理、强化学习训练

4. 核心设计
    uORB、模块化、参数系统、飞行模式、SITL/HIL

5. 可复用方式
    作为默认飞控层，不直接复制内部代码

6. 我们要接入的接口
    ROS2/uXRCE-DDS、MAVLink、Offboard、trajectory_setpoint、vehicle_odometry

7. 风险
    坐标系复杂
    电机顺序容易错
    模式/failsafe 容易导致 Offboard 退出
    直接改内部模块难度高

8. 第一阶段任务
    PX4 SITL + Gazebo + ROS2 Offboard 跑通

9. 长期用途
    SITL/HIL/实机迁移标准层
```

---

## 2.16 对 PX4 的最终判断

```text
是否进入主干：
    是

进入哪一层：
    飞控层 / 执行层 / 安全层

主要吸收：
    模块化飞控架构
    uORB 消息总线
    Offboard 接口
    SITL/HIL/实机一致路径
    参数系统
    日志系统
    failsafe 设计

不承担：
    渲染
    地图
    复杂规划
    点云处理
    RL 训练
    UE 展示

和 Gazebo 的关系：
    PX4 输出控制，Gazebo 计算运动和传感器

和 ROS2 的关系：
    ROS2 提供感知、规划、外部控制和系统集成

和 UE 的关系：
    UE 只显示 PX4/Gazebo 状态，不影响飞控

和 Simulink 的关系：
    Simulink 可生成控制器接入 PX4，但不是必需主干
```

一句话：

> **PX4 是你们长期项目的“飞控标准层”。Gazebo 负责让飞机在仿真世界里动起来，UE 负责让人看到漂亮画面，ROS2 负责让算法模块互相通信，而 PX4 负责让无人机按照真实飞控逻辑飞。**

下一篇建议讲  **ROS2 / ros_gz / px4_ros_com** ，因为 Gazebo 解决“世界”，PX4 解决“飞控”，ROS2 解决“生态模块怎么连起来”。
