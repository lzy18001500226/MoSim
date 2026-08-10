继续讲  **ROS2 / ros_gz / px4_ros_com** 。如果说 Gazebo 解决“世界怎么仿真”，PX4 解决“飞机怎么飞控”，那 ROS2 解决的就是：

> **所有模块怎么连起来。**

# 3. 项目概述：ROS2 / ros_gz / px4_ros_com

## 3.1 定位

ROS2 不是仿真器，也不是飞控，也不是渲染器。它的定位是 **机器人系统中间件和模块通信生态** 。

在你们的长期项目里，ROS2 应该作为系统总线：

```text
Gazebo：
    负责真值仿真世界

PX4：
    负责飞控闭环

UE：
    负责高真实感展示

Simulink：
    可选控制器开发工具

ROS2：
    负责把 Gazebo、PX4、UE、规划器、控制器、SLAM、日志、强化学习策略连接起来
```

ROS2 官方文档里，node 是 ROS graph 的参与者，节点之间可以通过 topic、service、action、parameter 通信；节点可以在同一个进程、不同进程，甚至不同机器上运行。这正是你们这种“仿真器、飞控、规划器、渲染器分布在不同模块里”的系统需要的能力。([ROS Docs](https://docs.ros.org/en/foxy/Concepts.html?utm_source=chatgpt.com "Concepts — ROS 2 Documentation: Foxy documentation"))

对你们来说，ROS2 的角色可以概括为：

```text
ROS2 = 无人机仿真生态的公共插座板
```

它负责：

```text
传感器数据流
状态数据流
规划轨迹流
控制命令流
仿真事件流
日志记录
模块启动
坐标变换
仿真器与算法桥接
PX4 与外部算法桥接
UE 状态同步
```

它不负责：

```text
飞控控制律本体
四旋翼动力学求解
高真实感渲染
地图资产制作
控制器理论设计
```

---

## 3.2 核心设计理念

| 设计原则     | 说明                                                                    |
| ------------ | ----------------------------------------------------------------------- |
| 节点化       | 每个功能拆成独立 node，例如 LiDAR 节点、规划节点、控制节点、UE 同步节点 |
| 消息驱动     | 模块之间通过 topic/service/action 交换数据，而不是互相硬调用            |
| 分布式       | 节点可以运行在不同进程、不同机器上                                      |
| 接口优先     | 先定义消息接口，再替换算法实现                                          |
| 松耦合       | 规划器、控制器、传感器、仿真器可以独立替换                              |
| 可记录可回放 | rosbag 可以记录 topic 数据并回放，便于复现实验                          |
| 生态复用     | 复用已有 SLAM、规划、传感器、可视化、桥接工具                           |

ROS2 的 node/topic/service/action/parameter 不是附属概念，而是它的架构核心。ROS2 文档说明，一个 node 应该负责单一模块化目的，例如控制电机或发布激光雷达数据；节点可以通过 topic、service、action 或 parameter 发送/接收数据。([ROS Docs](https://docs.ros.org/en/foxy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html?utm_source=chatgpt.com "Understanding nodes — ROS 2 Documentation"))

---

## 3.3 系统设计逻辑

### 3.3.1 第一性原理：为什么需要 ROS2？

如果没有 ROS2，你们系统会变成这样：

```text
Gazebo 要直接连 PX4
PX4 要直接连规划器
规划器要直接连 UE
UE 要直接连 Gazebo
SLAM 要直接连传感器
强化学习要直接连仿真器
日志系统还要到处抓数据
```

最后会变成一张乱网：

```text
A 调 B
B 调 C
C 调 D
D 又调 A
```

这会导致：

```text
模块难替换
接口难统一
日志难记录
问题难排查
仿真和实机难迁移
强化学习环境难封装
```

ROS2 的作用就是把这些点对点连接变成公共通信层：

```text
Gazebo 发布传感器和状态
PX4 发布飞控状态
规划器订阅状态和地图
控制器订阅轨迹和状态
UE 订阅位姿和事件
日志系统订阅所有关键 topic
```

这样所有模块只需要面对 ROS2 接口，不需要互相强耦合。

---

### 3.3.2 第二性原理：为什么 ROS2 比“自己写 UDP/TCP”更适合主干？

你当然可以自己写 UDP/TCP：

```text
Gazebo -> UDP -> UE
PX4 -> UDP -> 控制器
规划器 -> TCP -> Gazebo
```

这个短期能跑，但长期会出问题：

```text
消息格式谁定义？
时间戳怎么统一？
坐标系怎么统一？
日志怎么录？
多机怎么扩展？
丢包怎么处理？
模块怎么发现？
topic 怎么可视化？
仿真怎么回放？
```

ROS2 已经给了标准工具链：

```text
topic：
    连续数据流，例如 odom、pointcloud、trajectory

service：
    短请求，例如重置仿真、查询状态

action：
    长任务，例如导航到目标点、执行任务

parameter：
    配置参数，例如控制增益、传感器频率

rosbag：
    记录和回放 topic

launch：
    启动系统

tf2：
    管理坐标变换
```

ROS2 文档明确区分了 services 和 actions：service 适合快速返回的远程过程调用，action 适合长时间任务，并且 action 支持 goal、feedback、result 和取消。([ROS Docs](https://docs.ros.org/en/foxy/How-To-Guides/Topics-Services-Actions.html?utm_source=chatgpt.com "Topics vs Services vs Actions"))

所以长期项目里：

```text
ROS2 是主干
UDP/TCP 是局部桥接
```

比如 UE 同步可以先用 UDP，但系统主干仍然应该是 ROS2。

---

### 3.3.3 第三性原理：为什么 ROS2 是“接口标准”，不是“算法本体”？

ROS2 不会自动帮你规划路径，也不会自动帮你控制飞机。

它提供的是接口和生态：

```text
SLAM 算法可以做成 ROS2 node
规划器可以做成 ROS2 node
控制器可以做成 ROS2 node
UE bridge 可以做成 ROS2 node
Gazebo bridge 可以做成 ROS2 node
PX4 bridge 可以做成 ROS2 node
```

所以你们长期项目应该先定义接口：

```text
/state
/odom
/imu
/lidar/points
/local_map
/goal
/trajectory
/setpoint
/actuator_cmd
/collision_event
/task_status
```

然后再决定每个 topic 背后的算法是谁：

```text
/local_map:
    可以来自 Fast-LIO
    可以来自 Cartographer
    可以来自自研 mapping

/trajectory:
    可以来自 EGO-Planner
    可以来自 MPC planner
    可以来自 RL policy
    可以来自人工航点

/setpoint:
    可以来自 PX4 Offboard
    可以来自 Simulink 生成控制器
    可以来自 C++ 控制器
```

这就是 ROS2 的价值：**它把“算法实现”与“系统接口”分开。**

---

## 3.4 ROS2 的核心组件

### 3.4.1 Node

Node 是最小功能单元。

你们可以这样拆：

```text
gazebo_bridge_node
    Gazebo 与 ROS2 数据桥

px4_interface_node
    PX4 状态和命令接口

lidar_preprocess_node
    MID360 点云预处理

mapping_node
    建图/局部地图

planner_node
    局部规划

controller_node
    轨迹跟踪控制

ue_bridge_node
    把 ROS2 状态同步到 UE

logger_node
    日志与指标记录

rl_env_node
    强化学习环境封装
```

每个 node 只做一类事情，不要写成一个巨型 `main_node`。

---

### 3.4.2 Topic

Topic 适合连续数据流。

你们最核心的 topic 应该包括：

```text
/vehicle/odometry
/vehicle/pose
/vehicle/velocity
/imu/data
/lidar/points
/camera/image
/local_map
/goal
/trajectory
/setpoint
/motor_speed
/collision_event
/task_status
```

ROS2 topic 的设计适合“发布者不知道订阅者是谁，订阅者也不关心发布者内部怎么实现”的场景。

例如：

```text
Gazebo 发布 /lidar/points
Fast-LIO 订阅 /lidar/points
RViz 也订阅 /lidar/points
logger 也订阅 /lidar/points
```

Gazebo 不需要知道后面有几个消费者。

---

### 3.4.3 Service

Service 适合短命令：

```text
/reset_simulation
/spawn_vehicle
/delete_vehicle
/set_wind
/set_motor_fault
/get_vehicle_state
```

比如你们要做实验管理：

```text
实验管理器调用 /reset_simulation
Gazebo 重置世界
返回 success
```

这种就适合 service。

---

### 3.4.4 Action

Action 适合长任务：

```text
/fly_to_goal
/execute_mission
/scan_area
/follow_trajectory
```

因为 action 有：

```text
goal
feedback
result
cancel
```

例如：

```text
发送任务：
    飞到目标点

持续反馈：
    当前距离目标点 3.2m
    当前进度 60%

最终结果：
    成功 / 失败 / 超时 / 碰撞
```

这比 service 更适合无人机任务。

---

### 3.4.5 Parameter

Parameter 适合配置：

```text
controller.kp
controller.ki
controller.kd
planner.max_velocity
planner.max_acceleration
lidar.range
wind.speed
vehicle.mass
```

但注意：机型大参数最好还是放在 yaml/model 文件里，ROS2 parameter 用来管理运行时配置更合适。

---

### 3.4.6 rosbag

rosbag 是你们做实验复现的关键。

ROS2 文档说明，`ros2 bag` 可以记录系统中 topic 发布的数据并保存到数据库，也可以回放以复现实验结果。([ROS Docs](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html?utm_source=chatgpt.com "Recording and playing back data — ROS 2 Documentation"))

你们必须从第一阶段就记录：

```text
/vehicle/odometry
/trajectory
/setpoint
/imu/data
/lidar/points
/local_map
/collision_event
/task_status
```

没有 rosbag，你们后面很难判断：

```text
为什么撞了？
规划器哪里抖了？
控制器哪里饱和了？
UE 画面和 Gazebo 真值是否一致？
```

---

## 3.5 ros_gz：ROS2 和 Gazebo 的桥

### 3.5.1 定位

`ros_gz`，尤其是 `ros_gz_bridge`，是 ROS2 与 Gazebo Transport 之间的桥。

官方文档说明，`ros_gz_bridge` 提供 network bridge，使 ROS 和 Gazebo Transport 之间可以交换消息；Gazebo 的 ROS2 integration 文档也说明，`ros_gz_bridge` 负责 ROS2 与 Gazebo Transport 的消息交换，但支持的消息类型有限。([ROS Docs](https://docs.ros.org/en/iron/p/ros_gz_bridge/?utm_source=chatgpt.com "ros_gz_bridge 0.254.2 documentation"))

对你们来说，它的定位是：

```text
Gazebo 世界
    ↓
ros_gz_bridge
    ↓
ROS2 总线
```

它负责把 Gazebo 中的状态、传感器、仿真时钟等变成 ROS2 topic。

---

### 3.5.2 ros_gz 解决什么问题？

Gazebo 有自己的 Transport 系统，ROS2 有自己的 DDS 通信系统。

如果没有桥：

```text
Gazebo 里有 LiDAR 数据
ROS2 节点拿不到

Gazebo 里有仿真时钟
ROS2 节点不知道

Gazebo 里有模型状态
UE bridge 节点拿不到
```

有了 `ros_gz_bridge`：

```text
Gazebo topic
    ↔
ROS2 topic
```

比如：

```text
Gazebo LiDAR
    → ROS2 /lidar/points

Gazebo camera
    → ROS2 /camera/image

Gazebo clock
    → ROS2 /clock

ROS2 command
    → Gazebo model control
```

---

### 3.5.3 ros_gz 的边界

`ros_gz_bridge` 不是万能桥。

它的限制是：

```text
只支持特定消息类型
复杂自定义消息需要自己写转换
高频大点云要关注性能
时间同步要自己设计
坐标系仍然要自己管理
```

所以你们不能指望：

```text
装了 ros_gz，所有东西自动对齐
```

真正的工作是：

```text
定义 topic
定义消息类型
定义 frame_id
定义时间戳
定义桥接方向
定义数据频率
测试延迟
```

---

## 3.6 px4_ros_com / px4_msgs：PX4 和 ROS2 的桥

### 3.6.1 定位

PX4 和 ROS2 的现代集成主线是 uXRCE-DDS。PX4 官方文档说明，PX4 使用 uXRCE-DDS 让 uORB 消息可以在伴随计算机上像 ROS2 topic 一样发布和订阅，从而让 ROS2 应用更容易获取车辆信息并发送命令。([PX4 文档](https://docs.px4.io/main/en/middleware/uxrce_dds?utm_source=chatgpt.com "uXRCE-DDS (PX4-ROS 2/DDS Bridge) | PX4 Guide (main)"))

`px4_msgs` 提供 PX4 uORB 消息在 ROS2 里的消息定义。PX4 ROS2 user guide 也强调，ROS2 需要使用与 PX4 固件中 uXRCE-DDS client 模块一致的 message definitions，才能解释消息。([PX4 文档](https://docs.px4.io/main/en/ros2/user_guide?utm_source=chatgpt.com "ROS 2 User Guide - PX4 Docs"))

对你们来说，这一层负责：

```text
PX4 uORB
    ↔
uXRCE-DDS
    ↔
ROS2 topic
```

---

### 3.6.2 它解决什么问题？

没有 PX4-ROS2 桥时，ROS2 规划器想控制 PX4，需要绕 MAVLink/MAVROS 或自己解析协议。

有了 PX4-ROS2 集成：

```text
ROS2 可以订阅：
    VehicleOdometry
    VehicleStatus
    VehicleAttitude
    SensorCombined

ROS2 可以发布：
    OffboardControlMode
    TrajectorySetpoint
    VehicleCommand
```

这样你们的规划器就可以这样工作：

```text
planner_node 订阅：
    /fmu/out/vehicle_odometry

planner_node 发布：
    /fmu/in/trajectory_setpoint
    /fmu/in/offboard_control_mode
    /fmu/in/vehicle_command

PX4：
    接收外部期望轨迹
    执行 Offboard 控制
```

---

### 3.6.3 px4_ros_com 的边界

PX4-ROS2 桥不是规划器，也不是控制器。

它只是桥：

```text
PX4 消息 ↔ ROS2 消息
```

你们还需要自己写：

```text
offboard_control_node
planner_node
trajectory_converter_node
failsafe_monitor_node
```

另外一定要注意版本一致：

```text
PX4 固件版本
px4_msgs 版本
px4_ros_com 版本
ROS2 发行版
uXRCE-DDS agent 版本
```

如果消息定义不一致，最容易出现：

```text
topic 有但字段不对
能编译但运行异常
Offboard 发了但 PX4 不响应
```

---

## 3.7 ROS2 在你们架构里的位置

你们长期项目应该长这样：

```text
                 ┌────────────────────┐
                 │        UE 前台       │
                 │ 高真实感显示/演示画面 │
                 └─────────↑──────────┘
                           │
                     ue_bridge_node
                           │
┌──────────────────────────┴──────────────────────────┐
│                    ROS2 总线                          │
│ odom / tf / lidar / map / trajectory / setpoint / log │
└───────────────↑──────────────────────────↓───────────┘
                │                          │
        ros_gz_bridge                 planner/controller
                │                          │
          Gazebo/gz-sim              C++ / Python / Simulink生成
                │                          │
                └──────── PX4 / uXRCE-DDS ─┘
```

ROS2 不是某个模块，而是整个系统的数据层。

---

## 3.8 我们应该吸收 ROS2 哪些设计？

### 吸收 1：节点化

每个功能单独 node：

```text
gazebo_bridge_node
px4_bridge_node
mapping_node
planner_node
controller_node
ue_bridge_node
logger_node
experiment_manager_node
```

不要一个大程序全干。

---

### 吸收 2：topic 作为系统接口

你们要定义自己的 topic 规范：

```text
/mosim/vehicle/odometry
/mosim/lidar/points
/mosim/local_map
/mosim/planner/trajectory
/mosim/controller/setpoint
/mosim/event/collision
/mosim/task/status
```

长期项目换名字后，把 `mosim` 换掉即可。

---

### 吸收 3：tf 坐标树

无人机系统最容易错的是坐标系。

你们必须定义：

```text
map
odom
base_link
imu_link
lidar_link
camera_link
ue_world
gazebo_world
```

还要明确：

```text
PX4 NED
ROS ENU
Gazebo Z-up
UE 坐标系
```

不要等出问题再补。

---

### 吸收 4：rosbag 实验复现

所有实验必须能录、能回放。

```text
rosbag record:
    odom
    trajectory
    setpoint
    lidar
    map
    collision
    task_status
```

这会成为后面论文、比赛、调参、bug复现的基础。

---

### 吸收 5：launch 组织系统

不要手动开十几个终端。

长期项目应该有：

```text
launch/sitl_gazebo.launch.py
launch/ue_display.launch.py
launch/planner_test.launch.py
launch/rl_env.launch.py
launch/full_stack.launch.py
```

---

### 吸收 6：action 管理任务

长任务用 action：

```text
/fly_to_goal
/execute_mission
/follow_trajectory
/run_experiment
```

这样可以有 feedback、cancel、result。

---

## 3.9 我们不应该照搬 ROS2 的地方

### 不照搬 1：不要什么都拆成 node

ROS2 鼓励模块化，但过度拆分会带来通信开销和调试复杂度。

比如高频控制回路，如果 500Hz 以上，不一定适合拆得太散。可以用 composition 或进程内通信优化。

ROS2 组件化 node composition 的研究也说明，composition 可以在保持代码关注点分离的同时减少资源开销，对传感器处理管线等场景有性能价值。([arXiv](https://arxiv.org/abs/2305.09933?utm_source=chatgpt.com "Impact of ROS 2 Node Composition in Robotic Systems"))

---

### 不照搬 2：不要把 ROS2 当实时控制内核

ROS2 可以做工程通信，但它不是硬实时内核。

底层电机控制、超高频姿态环还是交给 PX4。

ROS2 更适合：

```text
传感器
建图
规划
中高层控制
任务管理
日志
UE 同步
```

---

### 不照搬 3：不要把所有大数据都无脑过 ROS2

例如高频点云、图像、深度图，传输压力很大。要控制：

```text
频率
压缩
QoS
消息类型
是否需要下采样
是否需要共享内存
```

---

### 不照搬 4：不要忽视 QoS

ROS2 基于 DDS，QoS 对传感器和控制很重要。

不同数据应该用不同 QoS：

```text
控制命令：
    低延迟，可靠性按需求权衡

图像/点云：
    可以 best effort，避免阻塞

任务状态：
    reliable

参数和服务：
    reliable
```

---

## 3.10 ROS2 与强化学习的关系

ROS2 不是 RL 框架，但可以作为 RL 环境和仿真世界之间的接口。

结构可以是：

```text
Gymnasium Env
    ↓
ROS2 action/service 控制仿真 reset
    ↓
ROS2 topic 获取 observation
    ↓
ROS2 topic/action 发送 action
    ↓
Gazebo/PX4 执行一步或一段时间
    ↓
计算 reward
```

已有研究里，gym-gazebo2 就是基于 ROS2 和 Gazebo 的强化学习工具包，目标是让机器人 RL 能在相同虚拟条件下比较不同技术和算法。([arXiv](https://arxiv.org/abs/1903.06278?utm_source=chatgpt.com "gym-gazebo2, a toolkit for reinforcement learning using ROS 2 and Gazebo"))

但注意：Gazebo+ROS2 适合真实工程验证，不一定适合大规模高速训练。后续可以再接 MuJoCo/Genesis/Flightmare 这种更快的训练后端。

---

## 3.11 最小落地任务

ROS2 这一层，你们第一阶段要做这些：

```text
1. 确定 ROS2 发行版
2. 建立 workspace
3. 建立基础包结构
4. 跑通 ros_gz_bridge
5. 跑通 PX4 uXRCE-DDS / px4_msgs
6. 能订阅 PX4 vehicle_odometry
7. 能发布 PX4 Offboard setpoint
8. 能订阅 Gazebo LiDAR / camera / clock
9. 建立 tf 树
10. 建立 UE bridge node
11. 建立 logger node
12. 建立 rosbag 记录脚本
13. 建立 launch 文件
```

第一阶段成功标准：

```text
ROS2 能看到 Gazebo 数据
ROS2 能看到 PX4 数据
ROS2 能向 PX4 发指令
UE 能通过 ROS2/UDP 获得状态
rosbag 能记录关键 topic
一次实验可以通过 launch 一键启动
```

---

## 3.12 ROS2 REVIEW.md 应该写什么

```text
1. 项目定位
    机器人系统中间件和模块通信生态

2. 它解决什么问题
    模块通信、数据流、任务接口、日志、启动、坐标变换、仿真/实机统一接口

3. 它不解决什么问题
    飞控、动力学、渲染、规划算法本体、强化学习算法本体

4. 核心设计
    node、topic、service、action、parameter、tf、rosbag、launch

5. 我们要吸收什么
    节点化、接口标准化、topic 数据流、rosbag 复现、tf 坐标树、launch 系统管理

6. 关键桥接
    ros_gz_bridge
    px4_msgs / px4_ros_com / uXRCE-DDS
    UE bridge

7. 风险
    坐标系复杂
    QoS 设置错误
    高频数据压力大
    PX4 消息版本不一致
    topic 命名失控
    launch 文件混乱

8. 第一阶段任务
    Gazebo + PX4 + ROS2 + UE 状态同步

9. 长期用途
    作为整个仿真生态的系统总线
```

---

## 3.13 对 ROS2 / ros_gz / px4_ros_com 的最终判断

```text
是否进入主干：
    是

进入哪一层：
    系统总线层 / 模块通信层 / 实验记录层

主要吸收：
    node/topic/service/action
    tf 坐标树
    rosbag 记录与回放
    launch 系统启动
    ros_gz Gazebo 桥
    PX4 uXRCE-DDS / px4_msgs 接口

不承担：
    飞控
    动力学
    渲染
    算法本体
    大规模 RL 高速训练后端

和 Gazebo 的关系：
    ros_gz 把 Gazebo 数据桥接到 ROS2

和 PX4 的关系：
    px4_msgs/uXRCE-DDS 把 PX4 uORB 映射到 ROS2

和 UE 的关系：
    ROS2 通过 bridge node 把状态同步给 UE

和 Simulink 的关系：
    Simulink 生成的 ROS2 node 可以接入 ROS2 总线，但不是必需
```

一句话：

> **ROS2 是你们长期项目的“系统神经网络”。Gazebo 提供世界，PX4 提供飞控，UE 提供展示，而 ROS2 负责把这些模块变成一个可扩展、可记录、可复现、可替换的无人机仿真生态。**

下一篇建议讲  **AirSim / UE 路线** ，因为你们现在非常关心“展示效果”和“UE 高真实感地图”，AirSim 正好是理解 UE 无人机仿真路线的关键参考。
