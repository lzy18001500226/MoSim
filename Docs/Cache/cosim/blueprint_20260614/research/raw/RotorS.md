# 13. 项目概述：RotorS

## 13.1 定位

RotorS 是由 ETH Zurich Autonomous Systems Lab 开发的、基于 **ROS 1 + Gazebo Classic** 的多旋翼无人机仿真框架。它提供 AscTec Hummingbird、Pelican、Firefly 等多旋翼模型，同时包含 IMU、真值里程计、VI-Sensor、基础控制器、场景、手柄接口、HIL 接口和 Gazebo 插件。项目采用 Apache 2.0 许可证。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

它不是像 Gazebo 那样的通用仿真引擎，而是：

> **在 Gazebo 之上补齐多旋翼无人机模型、电机动力学、传感器、控制接口和 ROS 工程结构的一套无人机仿真参考框架。**

可以理解成：

```text
Gazebo Classic
    提供通用刚体、碰撞、世界和渲染
        ↓
RotorS
    补充多旋翼模型
    电机与桨叶作用
    无人机传感器
    ROS消息
    控制器
    HIL接口
```

RotorS 当前最重要的价值已经不是“直接作为新项目主干运行”。ROS Index 将其相关软件包标为 `UNMAINTAINED`，仓库的官方安装说明仍围绕 Ubuntu 14.04/16.04、ROS Indigo/Kinetic、Catkin 和 Gazebo Classic 展开。([ROS Index](https://index.ros.org/p/rotors_gazebo_plugins/ "rotors_gazebo_plugins - ROS Package Overview"))

对我们的长期项目来说，RotorS 的定位应当是：

```text
经典无人机Gazebo架构教材
多旋翼电机插件参考
无人机模型目录参考
控制器—仿真器接口参考
传感器插件参考
HIL和ROS分层参考
```

而不是：

```text
新的ROS2主干
新的Gazebo Harmonic主项目
最终PX4仿真后端
强化学习高速后端
高真实感展示前端
```

---

## 13.2 核心设计理念

| 设计原则             | 说明                                                             |
| -------------------- | ---------------------------------------------------------------- |
| 建立在通用仿真器之上 | 不重新开发碰撞、刚体、世界和渲染，而是在 Gazebo 上增加无人机语义 |
| 飞行器模型模块化     | 机体、电机、传感器和控制接口分别描述和组合                       |
| 电机级输入           | 仿真器可以直接接收各个旋翼的角速度命令                           |
| ROS消息解耦          | 控制器、仿真器、传感器和评估工具通过 ROS topic 连接              |
| 插件式物理扩展       | 电机、IMU、里程计、空气动力和接口能力通过 Gazebo Plugin 实现     |
| 模型与控制器分离     | 同一飞行器模型可以替换不同控制器                                 |
| 传感器可挂载         | IMU、里程计、VI-Sensor 等可作为组件装到不同机型上                |
| 仿真与硬件接口预留   | 单独提供 HIL 接口，将仿真世界与真实飞控连接                      |
| 研究复现优先         | 提供场景、控制器、启动文件、评估包和记录工具                     |

RotorS 仓库不是一个单独的可执行程序，而是由 `rotors_description`、`rotors_gazebo`、`rotors_gazebo_plugins`、`rotors_control`、`rotors_comm`、`rotors_evaluation`、`rotors_hil_interface`、`rotors_joy_interface` 和 `rqt_rotors` 等 ROS 包组成。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

这体现的是一种非常典型的 ROS 工程思想：

```text
不要写一个巨型无人机仿真程序

而是拆成：
    模型
    物理插件
    消息
    控制器
    硬件接口
    评估工具
    GUI
```

---

# 13.3 系统设计逻辑

## 13.3.1 第一性原理：为什么不直接修改 Gazebo？

Gazebo 本身只理解这些通用概念：

```text
刚体
质量
惯量
关节
碰撞
外力
外力矩
传感器
世界
```

它并不知道：

```text
什么叫四旋翼
哪个电机顺时针
哪个电机逆时针
转速如何产生推力
桨叶如何产生反扭矩
控制器输出如何变成电机命令
```

RotorS 的思路不是修改 Gazebo 内核，而是在 Gazebo 之上添加插件：

```text
Gazebo通用物理
        +
RotorS电机模型插件
        +
RotorS传感器插件
        +
ROS消息接口
        =
多旋翼仿真器
```

这样既复用 Gazebo，又避免把多旋翼逻辑写死进 Gazebo 核心。

这对我们尤其重要。长期平台也不应该 fork Gazebo 后直接在核心代码里写：

```text
if model == Sunray150:
    ...
```

更合理的是：

```text
Gazebo Backend
    加载 Sunray-150 模型

Motor Plugin
    负责旋翼力和力矩

Sensor Plugin
    负责IMU/MID360等

ROS2 Adapter
    负责消息接口
```

---

## 13.3.2 第二性原理：为什么控制器通过电机转速控制飞机？

RotorS 的基础使用方式允许向 `/firefly/command/motor_speed` 发布 `mav_msgs/Actuators`，其中数组长度与电机数量一致。也就是说，仿真器的基础输入是每个旋翼的角速度，而不是直接修改无人机位置。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

完整闭环为：

```text
期望轨迹
    ↓
位置控制器
    ↓
姿态/角速度控制器
    ↓
控制分配
    ↓
各电机目标角速度
    ↓
RotorS电机插件
    ↓
推力和反扭矩
    ↓
Gazebo刚体动力学
    ↓
位置、姿态和速度
```

这一点非常关键。

错误的“飞行仿真”是：

```text
规划器输出一个位置
    ↓
直接把模型传送到该位置
```

这只是动画，不是飞行动力学仿真。

RotorS 要求：

```text
目标
    → 控制器
    → 电机
    → 力和力矩
    → 机体运动
```

因此它对我们建设真正四旋翼平台非常有参考价值。

---

## 13.3.3 第三性原理：为什么模型、插件和控制器分开？

假设一套四旋翼模型把控制器直接写进 Gazebo Plugin：

```text
Sunray模型
    自带PID
```

那么以后想换成：

```text
PX4
几何控制
MPC
Simulink生成控制器
强化学习策略
```

就必须修改模型插件。

RotorS 把它们分开：

```text
rotors_description
    飞机是什么

rotors_gazebo_plugins
    飞机在仿真中怎么受力、怎么测量

rotors_control
    飞机应该如何控制

rotors_comm
    模块之间传什么消息
```

同一个 Firefly 模型既可以接受直接电机转速，也可以由示例控制器控制，还可以接 MAVLink 或 HIL 链路。仓库同时提供直接电机命令、真值里程计悬停、手柄和键盘等入口。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

这正是我们应吸收的：

> **机型不能绑定控制器，动力学不能绑定算法，渲染不能绑定状态来源。**

---

# 13.4 软件包架构

## 13.4.1 rotors_description

该包负责无人机和传感器的描述资产。

它应当包含或组织：

```text
飞行器几何
link和joint
visual mesh
collision geometry
质量和惯量
旋翼安装位置
旋翼方向
传感器安装位姿
模型参数
```

其作用类似我们长期项目中的：

```text
vehicles/
    sunray150/
        model
        geometry
        inertia
        motor_layout
        sensor_mounts
```

这里最值得学习的是 **机型资产独立化** 。

云纵 Sunray-150 不应该散落在：

```text
Gazebo插件代码
PX4配置
UE蓝图
强化学习脚本
```

中分别写一遍。

而应该有一个明确的机型资产目录，再生成各个后端需要的文件。

---

## 13.4.2 rotors_gazebo

`rotors_gazebo` 负责场景、模型启动和 Gazebo 运行组织。

官方仓库中，启动文件位于 `rotors_gazebo/launch`，场景文件位于 `rotors_gazebo/worlds`；启动时通过 `mav_name` 选择飞行器，通过 `world_name` 选择 `.world` 场景。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

其本质是：

```text
选择机型
    +
选择传感器
    +
选择世界
    +
选择控制方式
    ↓
构造一次仿真实验
```

这对我们的实验组织有直接启发：

```text
vehicle:
    sunray150

world:
    indoor_lab

sensors:
    mid360
    imu

controller:
    px4

experiment:
    obstacle_avoidance
```

不应该为了换场景重新编译代码。

---

## 13.4.3 rotors_gazebo_plugins

这是 RotorS 最值得深入阅读的部分。

它负责将无人机特有行为写成 Gazebo 插件，例如：

```text
电机模型
里程计
IMU
传感器
空气动力
MAVLink/ROS接口
```

ROS Index 显示该包采用 Apache 2.0 许可证和 Catkin 构建，不过其正式发布状态已标为不再维护。([ROS Index](https://index.ros.org/p/rotors_gazebo_plugins/ "rotors_gazebo_plugins - ROS Package Overview"))

我们应该从中研究两个问题：

```text
一个Gazebo插件如何绑定某个link或joint？

插件如何从ROS/Gazebo消息获得电机命令，
再向机体施加力和力矩？
```

这比直接复制插件代码更有价值。

---

## 13.4.4 rotors_control

该包提供示例控制器和控制库，其消息依赖包括 `geometry_msgs`、`mav_msgs`、`nav_msgs` 和 `sensor_msgs`。历史更新中也加入过 `MultiDOFJointTrajectory` 和 Pose waypoint 输入。([ROS Index](https://index.ros.org/p/rotors_control/ "rotors_control - ROS Package Overview"))

它的定位是：

```text
展示如何从：
    轨迹
    里程计
    飞行器参数

计算：
    推力
    姿态
    电机命令
```

我们不一定直接使用这些旧控制器，但要学习其控制器接口。

长期项目的控制器接口可以定义为：

```text
输入：
    VehicleState
    TrajectoryReference
    VehicleParameters

输出：
    ActuatorCommand
```

控制器可以是：

```text
PX4Controller
GeometricController
PIDController
MPCController
RLController
```

---

## 13.4.5 rotors_comm

该包承担公共消息和服务。

它的意义不是某几个消息字段，而是：

> **将无人机控制、传感器和实验管理的协议独立出来。**

如果消息定义散落在每个包里，会导致：

```text
控制器使用一种电机数组
仿真器使用另一种电机数组
日志工具又使用第三种格式
```

RotorS 使用公共通信包，让不同模块共享接口。

我们长期项目也应建立：

```text
interfaces/
    VehicleState
    ActuatorCommand
    Trajectory
    SensorPacket
    SimulationEvent
    FaultCommand
```

ROS2 中可以表现为：

```text
msg/
srv/
action/
```

Python/Gym 后端则有对应的数据类。

---

## 13.4.6 rotors_evaluation

该包负责实验结果评价和数据分析。

这是很多仿真项目容易忽略的模块。

大多数项目只实现：

```text
飞机飞起来了
```

但研究平台需要回答：

```text
跟踪误差是多少？
控制输入是否饱和？
算法是否稳定？
重复十次成功率如何？
不同控制器哪个好？
```

因此我们也应设置独立：

```text
evaluation/
    trajectory_metrics
    control_metrics
    safety_metrics
    planner_metrics
    batch_report
```

而不是把指标计算临时写在某个控制器脚本里。

---

## 13.4.7 rotors_hil_interface

该包预留硬件在环接口。

这说明 RotorS 的目标不仅是软件动画，还考虑：

```text
仿真动力学
    ↔
真实飞控硬件
```

虽然 RotorS 的 HIL 技术栈较旧，但其边界设计依然值得吸收：

```text
HIL Adapter
    输入仿真传感器
    发送给飞控

HIL Adapter
    接收飞控执行器输出
    发送给仿真器
```

我们的现代版本应该优先面向：

```text
PX4 SITL
PX4 HITL
ROS2
uXRCE-DDS
MAVLink
```

---

## 13.4.8 rotors_joy_interface 与 rqt_rotors

这些包分别服务手柄输入和 GUI 调试。

它们提示我们：

```text
仿真平台不能只有算法接口
还要有人工调试入口
```

长期项目应保留：

```text
键盘/手柄控制
手动目标点
紧急停止
模式切换
参数查看
状态面板
```

不过新系统不一定继续使用 ROS1 rqt，可以用：

```text
ROS2工具
RViz2 Panel
Web UI
UE HUD
独立Qt前端
```

---

# 13.5 飞行器模型的组合方式

## 13.5.1 机体不是一个不可拆分网格

合理的多旋翼模型应拆为：

```text
base_link
    机体主体

rotor_0_link
rotor_1_link
rotor_2_link
rotor_3_link

imu_link
lidar_link
camera_link
```

每个部分承担不同意义：

```text
visual：
    外观

collision：
    碰撞

inertial：
    质量和惯量

joint：
    连接和相对位姿

plugin：
    物理或传感器行为
```

旋翼 link 的位置不是纯视觉问题，它决定推力的作用点。

---

## 13.5.2 为什么旋翼作用点很重要？

设机体质心为 (O)，第 (i) 个电机位置为 (\mathbf r_i)，产生推力 (\mathbf F_i)。

该电机对质心产生的力矩为：

[
\boldsymbol{\tau}_i=\mathbf r_i\times\mathbf F_i
]

因此：

```text
前后电机差动
    产生俯仰力矩

左右电机差动
    产生滚转力矩

顺逆旋翼反扭矩差
    产生偏航力矩
```

如果模型中旋翼位置写错，即使总推力正确，也会产生错误的滚转和俯仰响应。

所以 Sunray-150 模型必须明确：

```text
每个电机相对质心的三维坐标
推力轴方向
旋转方向
电机编号
```

---

# 13.6 电机模型

## 13.6.1 基本计算链

RotorS 的电机模型思想可概括为：

```text
目标电机转速
    ↓
电机动态/一阶滤波
    ↓
实际转速
    ↓
平方推力模型
    ↓
推力、反扭矩和气动效应
    ↓
施加到旋翼位置
```

典型推力关系为：

[
T_i=k_f\omega_i^2
]

反扭矩关系可写为：

[
Q_i=s_i k_m\omega_i^2
]

其中：

```text
ω_i：
    第i个电机角速度

k_f：
    推力系数

k_m：
    反扭矩系数

s_i：
    旋翼方向符号
```

RotorS 相关控制代码也使用 `rotor_force_constant × rotor_velocity²` 表达旋翼力。([GitHub](https://github.com/ethz-asl/mav_control_rw?utm_source=chatgpt.com "GitHub - ethz-asl/mav_control_rw: Control strategies for rotary wing Micro Aerial Vehicles using ROS"))

---

## 13.6.2 为什么需要电机响应时间？

真实电机不能瞬间从：

```text
0 rad/s
```

跳到：

```text
1000 rad/s
```

因此应使用类似一阶模型：

[
\tau_m\dot{\omega} *i+\omega_i=\omega* {i,\mathrm{cmd}}
]

或者离散形式：

```text
ω_actual逐步追踪ω_command
```

这会影响：

```text
姿态环带宽
超调
高频振荡
电机饱和
控制器稳定裕度
故障响应
```

如果忽略电机动态，仿真控制器通常会显得比实机更强。

---

## 13.6.3 Rotor Velocity Slowdown

Gazebo 中为了避免视觉旋翼高速旋转导致数值和渲染问题，常使用一个仿真转速缩放因子。

需要区分：

```text
关节在Gazebo中的显示/模拟转速

真实用于计算推力的等效旋翼转速
```

新 Gazebo 的多旋翼电机系统中仍可看到类似设计：推力根据恢复后的真实电机速度平方乘以电机常数计算。([GitHub](https://github.com/gazebosim/gz-sim/issues/2637?utm_source=chatgpt.com "High Thrust Calculation in Motor Model Plugin · Issue #2637 · gazebosim/gz-sim · GitHub"))

这对我们意味着：

> **桨叶动画转速不能直接等同于动力学转速。**

UE 中的桨叶可以只做视觉模糊或循环动画，但动力学后端必须保存真实电机状态。

---

## 13.6.4 电机参数不能照抄

RotorS 现成模型的：

```text
motor_constant
moment_constant
max_rot_velocity
time_constant_up
time_constant_down
rotor_drag_coefficient
rolling_moment_coefficient
```

都是针对特定飞机的。

社区中长期存在如何由电机 KV、最大电压、最大推力和桨径计算这些参数的讨论，这也说明新机型不能简单复制默认值。([GitHub](https://github.com/ethz-asl/rotors_simulator/issues/422?utm_source=chatgpt.com "Documentation: What is the math behind the Motor Model Plugin? · Issue #422 · ethz-asl/rotors_simulator · GitHub"))

对 Sunray-150，应优先通过：

```text
电机—桨叶台架数据
厂家推力表
实测悬停油门
阶跃响应
飞行日志
```

获得参数。

建议参数源：

```text
motors.yaml

motor_count
motor_positions
rotation_directions
kv
max_voltage
max_speed
thrust_curve
torque_curve
time_constant_up
time_constant_down
drag_coefficients
```

---

# 13.7 空气动力模型

RotorS 不只是“电机向上施加一个力”，其 Gazebo 插件体系还考虑了更现实的空气动力效应。ETH ASL 对项目的介绍提到 RotorS 提供物理模型、传感器模型、Gazebo 世界 OctoMap 生成和现实空气动力模拟。([GitHub](https://github.com/ethz-asl/ethz-asl.github.io?utm_source=chatgpt.com "GitHub - ethz-asl/ethz-asl.github.io: Github page for the Autonomous Systems Lab, containing info and documentation about our open source projects."))

可抽象为：

```text
旋翼推力
    k_fω²

反扭矩
    k_mω²

机体阻力
    与相对气流有关

旋翼侧向阻力
    飞行速度影响旋翼作用

滚转力矩
    旋翼气动产生附加力矩

风场
    改变相对空气速度
```

这对高速飞行特别重要。

低速悬停时，简化模型可能足够；高速前飞时，如果只有理想推力模型，仿真会低估：

```text
速度衰减
倾角需求
横向耦合
控制能耗
风扰影响
```

---

# 13.8 传感器模型

RotorS 自带的传感器至少包括 IMU、通用里程计和 VI-Sensor，并允许将传感器挂载在不同多旋翼模型上。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

## 13.8.1 真值与测量值必须分开

应明确：

```text
Ground Truth：
    Gazebo内部真实位置、姿态、速度

Odometry Sensor：
    可能含频率、噪声和延迟

IMU：
    加速度和角速度测量

Estimator Output：
    定位算法估计的状态
```

错误设计是让控制器永远直接读取 Gazebo 真值。

合理设计应支持：

```text
调试模式：
    使用Ground Truth

传感器模式：
    使用IMU + GPS/视觉/LiDAR

真实算法模式：
    使用Fast-LIO或PX4 EKF输出
```

---

## 13.8.2 频率和仿真时钟

RotorS 的历史讨论表明，里程计插件可以按仿真步发布，但控制器能否收到期望频率，还取决于 Gazebo 物理步长、ROS 仿真时钟以及整个处理链是否正确使用 `/clock`。([GitHub](https://github.com/ethz-asl/rotors_simulator/issues/423?utm_source=chatgpt.com "Increase Odometry sensor rate · Issue #423 · ethz-asl/rotors_simulator"))

这说明：

```text
插件设置1000 Hz
```

并不自动意味着：

```text
控制器稳定收到1000 Hz数据
```

还要检查：

```text
physics_step
real_time_factor
sensor_update_rate
ROS callback
消息队列
计算负载
时间源
```

这正是我们后续多时钟系统必须统一管理的原因。

---

# 13.9 控制器与通信接口

## 13.9.1 最低层：Motor Speed

```text
输入：
    各电机目标转速

优点：
    能研究控制分配
    能研究电机退化
    能研究执行器饱和
    能接飞控固件输出

缺点：
    控制器开发难度最高
```

---

## 13.9.2 中间层：推力与力矩

```text
输入：
    collective thrust
    roll torque
    pitch torque
    yaw torque

控制分配器：
    转换成各电机转速
```

适合：

```text
几何控制
MPC
容错控制
```

---

## 13.9.3 高层：轨迹

RotorS 的控制包历史上支持 `MultiDOFJointTrajectory` 和航点输入。([ROS Index](https://index.ros.org/p/rotors_control/ "rotors_control - ROS Package Overview"))

轨迹可以包含：

```text
位置
速度
加速度
姿态或航向
时间
```

由轨迹跟踪控制器向下转换。

---

## 13.9.4 对我们的启发：必须保留多层接口

长期项目不应只有一个 `/cmd_vel`。

建议定义：

```text
/control/waypoint
/control/trajectory
/control/velocity_setpoint
/control/attitude_setpoint
/control/wrench
/control/motor_command
```

不同控制器选择不同层接入。

PX4 模式下，可以由适配器映射到：

```text
TrajectorySetpoint
VehicleAttitudeSetpoint
VehicleRatesSetpoint
ActuatorMotors
```

---

# 13.10 RotorS 与 PX4 Gazebo 的关系

历史上的 PX4 Gazebo Classic 仿真大量继承了 RotorS 的模型和插件思想。旧 `sitl_gazebo` 仓库说明，其电机模型和其他组成部分来自 RotorS，只是该仓库主要使用 MAVLink 且不依赖 ROS。([GitHub](https://github.com/osrf/sitl_gazebo?utm_source=chatgpt.com "GitHub - osrf/sitl_gazebo: Gazebo Sim Plugin · GitHub"))

两者区别可以概括为：

| 维度           | RotorS                      | PX4 Gazebo 仿真               |
| -------------- | --------------------------- | ----------------------------- |
| 核心目标       | ROS无人机研究框架           | PX4 SITL/HITL仿真             |
| 控制器         | ROS示例控制器、直接电机命令 | PX4飞控软件栈                 |
| 通信           | ROS消息为主                 | MAVLink或PX4仿真接口          |
| 飞行模式与安全 | 较简单                      | PX4 Commander、failsafe、mode |
| 模型/插件思想  | 原始重要来源之一            | 吸收并演进                    |
| 当前技术栈     | ROS1 + Gazebo Classic       | 当前应转向新 Gazebo + PX4     |

因此我们不应在 RotorS 和 PX4 之间二选一。

正确关系是：

```text
RotorS：
    学无人机Gazebo模型与插件设计

PX4：
    作为实际飞控和当前工程主线
```

---

# 13.11 RotorS 与 Flightmare 的关系

两者都来自 ETH/苏黎世无人机研究生态，但定位不同：

```text
RotorS：
    Gazebo + ROS
    强调机器人系统、传感器、控制器和物理插件

Flightmare：
    轻量C++动力学 + Unity
    强调高速四旋翼、视觉和RL
```

可以理解为：

```text
RotorS解决：
    一架无人机如何进入ROS/Gazebo工程系统

Flightmare解决：
    四旋翼动力学和高质量渲染如何解耦并高速运行
```

对我们的吸收关系是：

```text
从RotorS吸收：
    机型和插件

从Flightmare吸收：
    统一VehicleState和独立Renderer
```

---

# 13.12 RotorS 与 RflySim 的关系

```text
RotorS：
    Gazebo负责物理
    ROS控制器
    Gazebo GUI显示

RflySim：
    CopterSim负责物理
    PX4/Simulink负责控制
    RflySim3D/UE负责显示
```

RotorS 的优点是开源、模块直接可读；RflySim 的优势是 Simulink—代码生成—PX4—HIL 的完整工具链。

我们应该组合两者思想：

```text
RotorS：
    学模型和物理插件

RflySim：
    学MIL/SIL/HIL验证流程

Flightmare：
    学仿真与渲染解耦

PX4：
    提供真实飞控栈
```

---

# 13.13 我们应该吸收 RotorS 的哪些设计？

## 吸收一：无人机模型按功能分包

```text
vehicle description
gazebo plugin
controller
communication
evaluation
hardware interface
```

不要所有内容塞进一个仓库目录。

---

## 吸收二：旋翼是独立物理组件

每个旋翼都应配置：

```text
position
axis
direction
motor constant
moment constant
max speed
time constant
drag
```

而不是只给整架飞机一个总推力。

---

## 吸收三：支持多层控制入口

```text
trajectory
velocity
attitude
wrench
motor speed
```

这会让传统控制、PX4、RL 和故障控制共享一个平台。

---

## 吸收四：传感器可挂载

传感器应作为可组合组件：

```text
Sunray-150
    + MID360
    + Front Camera
    + IMU
```

而不是为每种组合复制一整套飞机模型。

---

## 吸收五：控制器和仿真器通过消息解耦

控制器不应直接获得 Gazebo 内部对象指针。

它只能通过标准状态和命令接口工作。

这保证同一个控制器可以进入：

```text
Gazebo
MuJoCo
Genesis
实机
```

---

## 吸收六：评估模块独立

评价指标不能依附于某一个控制器。

所有控制器都经过同一个评价模块。

---

## 吸收七：HIL是平台原生能力

从一开始就为：

```text
SITL
HITL
实机
```

预留相同数据边界。

---

## 吸收八：场景和机型通过启动配置组合

现代实现应从 ROS1 Launch/XML 转成：

```text
ROS2 launch
YAML实验配置
场景清单
插件注册
```

但组合思想不变。

---

# 13.14 我们不应该照搬什么？

## 不照搬一：不要直接把 RotorS 当新项目基础

原因是其官方栈仍围绕 ROS Indigo/Kinetic、Catkin 和 Gazebo Classic，ROS Index 也标记为不再维护。([GitHub](https://github.com/ethz-asl/rotors_simulator "GitHub - ethz-asl/rotors_simulator: RotorS is a UAV gazebo simulator · GitHub"))

应该：

```text
读源码
提炼设计
重新实现到 ROS2 + gz-sim
```

而不是长期修补旧栈。

---

## 不照搬二：不要复制默认机型参数

Hummingbird、Pelican、Firefly 和 Iris 都不是 Sunray-150。

只能参考参数字段和模型结构，不能照抄数值。

---

## 不照搬三：不要依赖 Gazebo Ground Truth 完成所有控制

真实项目必须逐步切换为：

```text
PX4 EKF
Fast-LIO
真实传感器估计
```

真值只用于：

```text
评估
调试
仿真监控
```

---

## 不照搬四：不要继续使用ROS1消息作为永久接口

应转换成：

```text
ROS2标准消息
px4_msgs
自定义少量接口
```

并明确 QoS、时间戳和 frame。

---

## 不照搬五：不要把电机模型当成高保真空气动力

平方推力 + 简单阻力是工程近似。

它不会自动覆盖：

```text
桨叶复杂气流
旋翼间干扰
电池电压变化
电调控制
地面效应细节
高速非定常空气动力
```

这些需要通过实测和更高阶模型逐步补充。

---

## 不照搬六：不要让Gazebo渲染成为最终展示

RotorS 所处年代通常直接使用 Gazebo GUI。

我们的系统应保持：

```text
Gazebo：
    后台工程真值

UE：
    前台高质量显示
```

---

# 13.15 在长期架构中的位置

RotorS 不一定直接作为运行时依赖，而是作为我们 Gazebo 无人机后端的设计来源：

```text
                         UE高保真前端
                                ↑
                       Unified VehicleState
                                ↑
┌────────────────────────────────────────────────────┐
│                ROS2 / Core Interfaces              │
│ State / Trajectory / Wrench / Motors / Sensors     │
└──────────────↑──────────────────────↑──────────────┘
               │                      │
        Gazebo UAV Backend       Controller Backend
        吸收RotorS插件设计       PX4/C++/RL/Simulink
               │
     Sunray Motor / Sensor Plugins
               │
          gz-sim Physics
```

RotorS 给我们的不是一个最终后端，而是一张参考蓝图：

```text
RotorS Motor Model
    → 新Gazebo Motor System

RotorS Sensor Plugin
    → ROS2 Sensor System

RotorS Description
    → Sunray资产生成系统

RotorS Control Interface
    → Unified Controller API

RotorS Evaluation
    → Experiment Metrics

RotorS HIL
    → PX4 SITL/HITL Adapter
```

---

# 13.16 最小研究任务

针对 RotorS，建议按这个顺序解剖：

```text
1. 梳理九个ROS包之间的关系
2. 找到Firefly/Hummingbird/Iris模型描述
3. 理清base_link、rotor_link和sensor_link
4. 找到GazeboMotorModel插件
5. 追踪motor_speed topic到Gazebo施力的完整链路
6. 理清motor_constant和moment_constant
7. 理清time_constant_up/down
8. 理清rotor_velocity_slowdown
9. 理清rotor_drag和rolling moment
10. 找到IMU和odometry插件
11. 理清Ground Truth和Sensor Output差异
12. 跑通直接电机转速输入
13. 跑通示例悬停控制器
14. 研究MultiDOFJointTrajectory接口
15. 阅读HIL接口的数据流
16. 对比PX4 Gazebo Classic继承的插件
17. 将核心设计映射到gz-sim System Plugin
18. 建立Sunray-150电机参数表
19. 建立Sunray-150模型结构草案
20. 写RotorS REVIEW.md
```

最关键的源码追踪任务是：

```text
ROS motor command
    ↓
Motor Model Plugin
    ↓
motor dynamics
    ↓
thrust / reaction torque
    ↓
Gazebo Link force
    ↓
vehicle motion
    ↓
odometry / IMU
    ↓
controller feedback
```

只要把这条链完整追通，就掌握了 RotorS 的核心。

---

# 13.17 RotorS REVIEW.md 建议结构

```text
1. 项目定位
    ROS1 + Gazebo Classic多旋翼仿真框架

2. 它解决什么问题
    多旋翼模型
    电机动力学
    传感器仿真
    ROS控制接口
    示例控制器
    HIL和评估

3. 它不解决什么问题
    ROS2现代主干
    新Gazebo长期维护
    高真实感展示
    高速GPU RL
    完整PX4飞控系统
    MID360真实扫描模型

4. 核心设计
    description
    gazebo plugins
    controller
    communication
    evaluation
    HIL
    joy/rqt

5. 我们吸收什么
    旋翼插件
    机型资产分层
    传感器可挂载
    多层控制接口
    消息解耦
    评估与HIL分包

6. 是否进入主干
    原项目不直接进入
    设计和部分算法迁移到ROS2/gz-sim后端

7. 风险
    ROS1和Gazebo Classic过时
    项目不再维护
    默认模型参数不适用Sunray
    电机参数难以准确获得
    传感器模型有限
    坐标系和时间同步问题

8. 第一阶段用途
    源码解剖
    电机插件研究
    Sunray模型参考
    控制器接口参考

9. 长期用途
    新Gazebo无人机后端
    多旋翼模型生成器
    故障和气动插件
    PX4 SITL/HITL接口
```

---

# 13.18 最终判断

```text
是否进入长期项目：
    设计思想进入
    旧代码选择性参考

是否作为当前主干：
    否

进入哪一层：
    Gazebo无人机模型参考
    电机与气动插件参考
    ROS控制接口参考
    HIL和评估架构参考

主要吸收：
    模型/插件/控制器分离
    单旋翼物理组件
    motor_speed底层接口
    多层控制入口
    可挂载传感器
    ROS消息解耦
    独立评估包
    独立HIL接口

不承担：
    ROS2主总线
    当前PX4主仿真
    最终UE展示
    GPU强化学习
    MID360完整仿真
```

一句话总结：

> **RotorS 是现代开源无人机仿真的“祖传教材”之一。它最值得我们学习的不是旧版 ROS1 启动方法，而是如何在 Gazebo 通用物理之上，把机型描述、单旋翼动力学、传感器、控制器、通信、评估和 HIL 拆成相互独立的模块。我们应当把这些思想迁移到 ROS2 + gz-sim + PX4 + Sunray-150，而不是直接继续维护 RotorS 本身。**
>
