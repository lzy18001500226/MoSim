# 6. 项目概述：Project AirSim

## 6.1 定位

Project AirSim 是经典 AirSim 的后续演化项目，目标不是简单把旧版 AirSim 修到 UE5，而是重新设计一套面向无人机、机器人和其他自主系统的高保真仿真平台。

它的核心定位可以概括为：

> **以 Unreal Engine 5 提供高真实感场景与渲染，以独立仿真库定义机器人、传感器、控制器、执行器和仿真时钟，再通过网络客户端 API 对外提供控制、数据采集和实验管理能力。**

官方文档把 Project AirSim 描述为面向无人机、机器人及其他自主系统的仿真平台。它在 UE5 上提供高真实感视觉，同时允许接入自定义物理、控制器、执行器和传感器。官方将整体划分为 Sim Libs、宿主插件和客户端库三层。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/?utm_source=chatgpt.com "Project AirSim — Project Airsim 0.1 documentation"))

对我们来说，它的价值主要不是“直接替换 Gazebo”，而是研究：

```text
如何把仿真核心和 Unreal Engine 隔离？

如何用配置文件定义机器人、场景、控制器和传感器？

如何让物理、控制器、执行器、传感器可以运行时组合？

如何用统一客户端 API 管理 World、Robot 和 Simulation Clock？

如何把高真实感仿真包装成可自动运行、可单步、可批量采集数据的平台？
```

在我们的长期项目中，Project AirSim 更适合定位为：

```text
高真实感自主系统仿真架构参考
UE 前端与仿真核心分层参考
仿真生命周期和客户端 API 参考
视觉数据采集与场景随机化参考
```

而不是：

```text
立即替换 Gazebo
成为唯一物理真值后端
成为 ROS2 总线
成为强化学习唯一训练后端
```

---

## 6.2 与经典 AirSim、Cosys-AirSim 的区别

三者关系必须先理清。

### 经典 AirSim

```text
基本路线：
    在 UE4/Unity 上增加车辆、传感器、物理和 RPC API

特点：
    架构成熟
    Python/C++ API 使用广泛
    PX4/ArduPilot 接口清晰
    但上游已经归档
```

### Cosys-AirSim

```text
基本路线：
    延续经典 AirSim 的代码和 API
    修复 UE5 兼容性
    扩展传感器、车辆和工业场景

本质：
    旧架构的现代化维护和增强分支
```

### Project AirSim

```text
基本路线：
    继承 AirSim 经验
    重新设计平台层次、配置系统和运行时接口
    不追求严格兼容经典 AirSim API

本质：
    新一代架构重构
```

Project AirSim 官方 API 文档明确说明，严格保持经典 AirSim API 的向后兼容并不是项目目标；它会继承熟悉概念，但会根据旧项目经验更新 API。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/api.html?utm_source=chatgpt.com "API Overview — Project Airsim 0.1 documentation"))

因此：

```text
想研究旧项目如何继续维护：
    看 Cosys-AirSim

想研究新平台应该如何重新设计：
    看 Project AirSim
```

---

# 6.3 核心设计理念

| 设计原则               | 说明                                                           |
| ---------------------- | -------------------------------------------------------------- |
| 仿真核心与宿主引擎分离 | 核心机器人结构、场景 tick 和接口放在 Sim Libs；UE 只是当前宿主 |
| 组件运行时组合         | 物理、控制器、执行器、传感器不固定写死，可按机器人场景配置组合 |
| 配置驱动               | 使用 JSONC 分别定义场景、机器人、传感器、控制器和物理参数      |
| 客户端—服务器架构     | 仿真后端独立运行，外部 Python/C++ 客户端通过网络 API 控制      |
| 实体抽象               | 外部程序通过 Client、World、Drone 等实体与仿真交互             |
| 仿真时钟独立           | 不直接依赖 UE 编辑器 Tick，提供专门的 Sim Clock API            |
| 自动系统优先           | 不只是手动飞行，而是服务自主算法、训练、测试和数据采集         |
| 高保真数据生成         | 支持相机、传感器、场景变化和数据采集模块                       |
| 旧 API 去包袱          | 不为保持旧 AirSim 兼容而牺牲新架构                             |

官方架构把 Project AirSim 分为：

```text
1. Project AirSim Sim Libs
   定义通用机器人结构和场景仿真 tick 基础设施

2. Project AirSim Plugin
   当前由 Unreal Plugin 承担宿主
   连接特定机器人场景所需的控制器、物理和渲染组件

3. Project AirSim Client Library
   外部程序通过网络连接控制仿真和读取数据
```

([IAmAISim](https://iamaisim.github.io/ProjectAirSim/?utm_source=chatgpt.com "Project AirSim — Project Airsim 0.1 documentation"))

---

# 6.4 系统设计逻辑

## 6.4.1 第一性原理：为什么要把 Sim Libs 和 UE Plugin 分开？

经典 AirSim 虽然已经做了一定程度的 AirLib 与 UE 插件分离，但长期演进中仍然存在较强的历史结构和引擎依赖。

Project AirSim 进一步明确：

```text
仿真概念不等于 Unreal Actor
机器人不等于 UE Pawn
传感器不等于 UE Component
控制器不等于 UE Blueprint
```

因此它把通用概念放进 Sim Libs：

```text
Robot
Sensor
Actuator
Controller
Physics
Scene
Simulation Clock
Tick Loop
```

然后让 UE Plugin 负责：

```text
把这些抽象连接到 UE 场景
把机器人映射为 UE 中的可视对象
把渲染数据传回传感器
把场景和资产加载进来
```

这种设计解决了一个根本问题：

> **自主系统平台的核心模型不应该被某一种渲染引擎的数据结构绑死。**

对我们的长期项目，这一点非常重要。我们也应该把核心数据结构分开：

```text
core/
    vehicle
    sensor
    actuator
    controller
    simulation clock
    experiment
    world interface

adapters/
    gazebo
    unreal
    mujoco
    genesis
```

这样 Gazebo、UE、MuJoCo 可以是不同后端，不需要重新定义整个平台。

---

## 6.4.2 第二性原理：为什么 Project AirSim 强调运行时组件组合？

传统仿真器常把一套无人机写死成：

```text
固定动力学
固定控制器
固定执行器
固定传感器
固定场景
```

这会导致换一个控制器或传感器就要改源码。

Project AirSim 更倾向于：

```text
Robot
    ├── Physics
    ├── Controller
    ├── Actuators
    └── Sensors
```

这些组件由机器人配置文件决定。

官方机器人配置文档提供了四旋翼基础配置，并允许配置控制器、传感器和与 PX4 的通信参数。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/config_robot.html?utm_source=chatgpt.com "Robot Configuration Settings — Project Airsim 0.1 documentation"))

对我们来说，可以转化成：

```text
Sunray150
    physics_backend:
        gazebo
        custom_quadrotor
        mujoco

    controller:
        px4
        geometric
        pid
        rl_policy

    sensors:
        imu
        mid360
        camera

    renderer:
        unreal
        gazebo
```

核心不是照抄配置字段，而是吸收：

> **机器人是一组可组合组件，不是一整个不可拆分的固定类。**

---

## 6.4.3 第三性原理：为什么需要 Client / World / Robot 三层 API？

Project AirSim 的客户端 API 把外部交互抽象成三个主要对象：

```text
Client
World
Robot，例如 Drone
```

官方文档的定义是：

```text
Client：
    管理用户代码与仿真后端的网络连接

World：
    管理场景、时钟、天气等仿真环境

Drone：
    管理机器人控制和传感器数据
```

([IAmAISim](https://iamaisim.github.io/ProjectAirSim/api.html?utm_source=chatgpt.com "API Overview — Project Airsim 0.1 documentation"))

这比把所有函数堆进一个巨大的 RPC Client 更清楚。

例如：

```text
client.connect()

world.load_scene()
world.pause()
world.step()
world.set_weather()

drone.arm()
drone.move_by_velocity()
drone.get_state()
drone.get_sensor_data()
```

这种层次对我们很有启发。

我们自己的 API 可以拆为：

```text
SimulationClient
WorldAPI
VehicleAPI
SensorAPI
ExperimentAPI
```

其中：

```text
WorldAPI：
    reset
    pause
    step
    load_world
    set_weather
    spawn_object

VehicleAPI：
    arm
    set_control
    set_pose
    get_state

SensorAPI：
    get_image
    get_pointcloud
    set_noise
```

这样强化学习、自动测试和外部工具都能复用同一套接口。

---

## 6.4.4 第四性原理：为什么仿真时钟不能直接等于 UE Tick？

UE 的 Tick 是为了游戏和渲染服务的，其周期受帧率、场景复杂度和系统性能影响。

但自主系统仿真需要：

```text
固定步长
暂停
单步执行
倍速运行
确定性回放
传感器时间戳统一
控制周期同步
```

Project AirSim 将 Simulation Clock 作为场景配置和执行的核心组件，并明确说明，不应使用 UE 编辑器内置的暂停、恢复或单步按钮来控制 Project AirSim；应该通过专门的 Sim Clock API 管理。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/development/scene/sim_clock_internal.html?utm_source=chatgpt.com "Simulation Clock — Project Airsim 0.1 documentation"))

这说明它把：

```text
渲染时钟
仿真时钟
控制时钟
```

视为不同概念。

这正是我们 Gazebo + UE 双世界架构最需要吸收的设计。

我们的系统应该规定：

```text
Gazebo / Physics Clock：
    权威仿真时钟

PX4 Clock：
    跟随仿真时间或锁步

ROS2 Clock：
    使用 /clock 和 sim time

UE Rendering Clock：
    只负责显示帧率

UE Sensor Clock：
    若生成视觉传感器，必须跟随仿真时钟
```

---

# 6.5 配置系统

## 6.5.1 为什么使用 JSONC？

Project AirSim 使用 JSONC，也就是允许注释的 JSON，定义场景和机器人配置。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/config.html?utm_source=chatgpt.com "Configuration JSONC Settings — Project Airsim 0.1 documentation"))

优点：

```text
结构化
机器容易解析
允许注释
适合版本管理
适合嵌套机器人和传感器配置
```

缺点：

```text
复杂配置可读性一般
继承和复用能力有限
长配置容易重复
```

对我们来说不一定必须选 JSONC，也可以用 YAML，但要吸收其分层方式。

建议我们拆成：

```text
config/
    project.yaml
    worlds/
        indoor_lab.yaml
    vehicles/
        sunray150.yaml
    sensors/
        mid360.yaml
    controllers/
        px4.yaml
    experiments/
        obstacle_avoidance.yaml
```

不要把所有配置塞进一个大文件。

---

## 6.5.2 场景配置

Project AirSim 的 scene 配置负责定义：

```text
场景
Actor
机器人实例
仿真时钟
环境
机器人配置文件引用
```

官方场景配置支持在仿真运行时通过 API 重新加载配置。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/config_scene.html?utm_source=chatgpt.com "Scene Configuration Settings — Project Airsim 0.1 documentation"))

这对批量实验非常有价值：

```text
实验 1：
    室内走廊

实验 2：
    森林

实验 3：
    城市峡谷

不需要重新编译 UE
只需要加载不同配置
```

我们也应该让世界和实验配置可热切换。

---

## 6.5.3 机器人配置

机器人配置负责：

```text
机器人类型
物理参数
控制器
执行器
传感器
初始状态
飞控通信
```

Project AirSim 的 PX4 配置中，PX4 SITL 会通过两个独立通信通道与仿真平台交换数据：

```text
模拟器通道：
    主要传输传感器数据

控制/API 通道：
    传输执行器设置和飞控控制数据
```

([IAmAISim](https://iamaisim.github.io/ProjectAirSim/config_robot.html?utm_source=chatgpt.com "Robot Configuration Settings — Project Airsim 0.1 documentation"))

这体现了一个重要思想：

> **仿真器—飞控之间的传感器链路和上层控制/API链路应该区分。**

对我们的 PX4 + ROS2 架构，也应该明确：

```text
Gazebo ↔ PX4：
    动力学、传感器、执行器闭环

ROS2 ↔ PX4：
    状态监控、Offboard、任务和规划命令
```

不要把两种链路混成一个接口。

---

# 6.6 控制器设计

Project AirSim 支持不同控制器类型。

官方控制器文档包括：

```text
Simple Flight Controller
PX4
Manual Controller
```

其中 Simple Flight 用于快速让无人机飞起来；PX4 支持 SITL/HITL；Manual Controller 则允许 API 完全手动设置控制输出。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/controllers/simple_flight.html?utm_source=chatgpt.com "Simple Flight Controller for Drones — Project Airsim 0.1 documentation"))

这体现了三层需求：

```text
快速演示：
    Simple Flight

真实飞控验证：
    PX4

底层实验：
    Manual Controller
```

我们可以吸收成：

```text
ControllerBackend
    ├── PX4Controller
    ├── GeometricController
    ├── ManualController
    ├── ROS2ExternalController
    └── RLController
```

这样平台不把飞控写死成 PX4，但 PX4仍是默认工程标准。

---

# 6.7 物理设计

Project AirSim 强调可以集成自定义 physics、controllers、actuators 和 sensors。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/?utm_source=chatgpt.com "Project AirSim — Project Airsim 0.1 documentation"))

这意味着它不是只提供一个固定物理引擎，而是提供物理接口。

对我们来说，最重要的启发是：

```text
PhysicsBackend
    initialize()
    reset()
    apply_actuator_commands()
    step(dt)
    get_state()
```

不同实现可以是：

```text
GazeboPhysicsBackend
MuJoCoPhysicsBackend
CustomQuadrotorBackend
GenesisPhysicsBackend
```

这正符合“集各家之所长”的目标。

不过我们不应一开始就实现多个后端。第一阶段只做：

```text
GazeboPhysicsBackend
```

等统一接口稳定后再做 MuJoCo 或 Genesis。

---

# 6.8 数据采集设计

Project AirSim 提供独立的数据采集 API 和配置机制，用于自动执行数据采集任务。其文档还支持图像级增强、资产级配置和自动化采集脚本。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/datacollection/api.html?utm_source=chatgpt.com "Data Generation API Overview — Project Airsim 0.1 documentation"))

这说明它不只是实时飞行仿真器，还是：

```text
自动数据生成平台
```

典型用途：

```text
生成 RGB 数据
生成深度图
生成语义分割
改变天气和光照
改变物体材质
改变场景对象
批量生成训练集
```

对我们未来的价值很大：

```text
无人机视觉导航
目标检测
语义分割
sim-to-real
域随机化
强化学习视觉观测
```

我们应该吸收其独立数据采集模块思想：

```text
DataCollector
    trigger
    capture
    label
    augment
    store
    metadata
```

而不是把截图逻辑直接写进 UE。

---

# 6.9 Project AirSim 与 ROS2 的关系

Project AirSim 自身主要采用客户端—服务器 API，不是以 ROS2 为中心构建。

这与我们的主干路线不同：

```text
Project AirSim：
    Client API 是核心外部接口

我们的长期项目：
    ROS2 是工程系统总线
    Python API 是补充接口
```

因此不能直接照搬它的 API 中心化路线。

更合理的方式是：

```text
Project AirSim 设计思想
        ↓
提炼 World / Vehicle / Sensor API
        ↓
分别映射为：
    ROS2 topic/service/action
    Python client API
```

例如：

```text
world.reset()
    对应 ROS2 service /world/reset

drone.move_by_velocity()
    对应 ROS2 action 或 PX4 trajectory setpoint

drone.get_sensor_data()
    对应 ROS2 sensor topic
```

这样既保留 ROS2 生态，又吸收 Project AirSim 清晰的对象 API。

---

# 6.10 Project AirSim 与 Gazebo 的关系

两者不是同一类取向。

| 维度           | Project AirSim             | Gazebo                         |
| -------------- | -------------------------- | ------------------------------ |
| 核心定位       | 高保真自主系统仿真平台     | 通用机器人仿真平台             |
| 渲染           | Unreal Engine 5            | Gazebo Rendering               |
| 外部接口       | Client / World / Robot API | Gazebo Transport + ROS2 bridge |
| 配置           | JSONC                      | SDF/world/model                |
| 机器人生态     | 相对集中于自主系统场景     | ROS机器人生态更强              |
| 物理           | 可接入自定义物理组件       | 内置/插件式物理后端            |
| 数据采集       | 高度重视高保真数据生成     | 更偏工程传感器仿真             |
| ROS2           | 非架构中心                 | 可通过 ros_gz 深度集成         |
| 展示效果       | 强                         | 一般                           |
| 适合我们哪一层 | UE高保真前端和平台API参考  | 主真值仿真后端                 |

我们当前不应该做：

```text
Project AirSim 替换 Gazebo
```

而应该做：

```text
Gazebo：
    主真值后端

UE 前端：
    吸收 Project AirSim 的分层、时钟、配置、API 和数据采集设计
```

---

# 6.11 Project AirSim 与强化学习的关系

Project AirSim 可以作为高真实感 RL 验证环境，但不一定适合大规模并行训练。

优势：

```text
视觉真实
场景丰富
可改变天气、材质和环境
可以控制仿真时钟
有客户端 API
```

不足：

```text
UE 开销大
并行环境成本高
训练吞吐不如 MuJoCo/MJX/Genesis/Isaac Lab
```

所以在我们系统里：

```text
MuJoCo / Genesis：
    快速训练

Gazebo / PX4：
    工程验证

UE / Project AirSim 思想：
    高保真视觉验证与数据生成
```

这构成多保真仿真链：

```text
低成本快速训练
        ↓
中等保真工程验证
        ↓
高保真视觉验证
        ↓
实机
```

---

# 6.12 我们应该吸收哪些设计？

## 吸收一：三层架构

```text
Core Simulation Libraries
Host Adapter / Plugin
Client API
```

转换为我们的架构：

```text
core/
    统一数据、时间、模型和实验接口

backends/
    gazebo
    unreal
    mujoco

clients/
    ros2
    python
    c++
```

---

## 吸收二：World / Robot / Sensor 对象层级

让 API 更清晰：

```text
WorldAPI
VehicleAPI
SensorAPI
ExperimentAPI
```

不要所有功能都塞进一个 Client。

---

## 吸收三：独立 Sim Clock

必须支持：

```text
pause
resume
step
set_rate
reset
get_sim_time
```

并与 UE 渲染帧分离。

---

## 吸收四：配置驱动的组件组合

机器人由配置选择：

```text
physics
controller
actuators
sensors
renderer
```

不要写死在源码里。

---

## 吸收五：仿真器与飞控双通道

```text
传感器/执行器闭环
任务/API控制链路
```

二者职责分离。

---

## 吸收六：数据采集系统独立化

数据生成、标签、增强、元数据、存储应该成为独立模块。

---

## 吸收七：不为了旧 API 兼容牺牲架构

我们现在尚未发布稳定 API，因此应该趁早定义清晰接口，不要把临时实验接口变成永久包袱。

---

# 6.13 我们不应该照搬什么？

## 不照搬一：不要让 Client API 替代 ROS2

Project AirSim 适合通过网络 Client 控制，但我们的机器人生态仍然应以 ROS2 为主。

```text
ROS2：
    工程模块通信

Python Client：
    实验管理和强化学习
```

两者都要，但 ROS2 是主干。

---

## 不照搬二：不要默认 UE 是唯一宿主

即使 Project AirSim 在概念上做了核心与宿主分离，目前实际宿主仍然主要是 Unreal Plugin。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/?utm_source=chatgpt.com "Project AirSim — Project Airsim 0.1 documentation"))

我们的核心接口必须真正能适配 Gazebo、MuJoCo 和 UE。

---

## 不照搬三：不要立刻重构整个系统

Project AirSim 架构很漂亮，但如果我们一开始就照着做完整的：

```text
Sim Libs
Plugin System
Client SDK
Configuration Compiler
Data Collector
Multiple Physics Backends
```

项目会被基础设施拖死。

第一阶段只吸收关键原则：

```text
统一状态结构
统一时钟
统一配置
统一后端接口
统一车辆接口
```

---

## 不照搬四：不要把 UE 高保真等同于物理高可信

画面真实不代表：

```text
电机模型真实
空气动力真实
LiDAR真实
控制时延真实
碰撞真实
```

物理和视觉必须分别验证。

---

# 6.14 在我们长期架构中的位置

```text
                     ┌──────────────────────┐
                     │       UE 前端          │
                     │ 吸收 Project AirSim：  │
                     │ Plugin / Clock / API   │
                     │ Sensors / Data Capture │
                     └──────────↑───────────┘
                                │
                         UE Adapter / Bridge
                                │
┌───────────────────────────────┴─────────────────────────────┐
│                         Core API                             │
│ World / Vehicle / Sensor / Clock / Experiment / State       │
└──────────────↑──────────────────────────────↓───────────────┘
               │                              │
        Gazebo Backend                 ROS2 / Python Client
               │                              │
        PX4 / Sensors              Planner / Controller / RL
```

Project AirSim 不一定直接进入运行时，但它的架构思想可以进入：

```text
核心接口层
UE 后端适配层
仿真时钟
配置系统
数据采集系统
客户端 API
```

---

# 6.15 最小研究任务

针对 Project AirSim，建议逐项完成：

```text
1. 阅读 Architecture Overview
2. 理清 Sim Libs、Unreal Plugin、Client Library 三层边界
3. 找到 Robot、Sensor、Actuator、Controller、Physics 抽象
4. 理清场景 tick loop
5. 理清 Simulation Clock
6. 理清 Scene JSONC 与 Robot JSONC 的引用关系
7. 理清 Client / World / Drone API
8. 跑通 Simple Flight 示例
9. 跑通 PX4 SITL 示例或至少梳理双通信通道
10. 跑通一次数据采集
11. 写 Project AirSim REVIEW.md
12. 提炼我们自己的 Core API 草案
```

---

# 6.16 REVIEW.md 建议结构

```text
1. 项目定位
    AirSim 的新一代高保真自主系统仿真平台

2. 它解决什么问题
    UE5 高保真仿真
    通用机器人配置
    物理/控制器/传感器组合
    客户端 API
    仿真时钟
    数据采集

3. 它不解决什么问题
    ROS2 生态中心化
    高吞吐大规模并行 RL
    Gazebo 通用机器人生态
    完全独立于 UE 的成熟多宿主实现

4. 核心设计
    Sim Libs
    Host Plugin
    Client Library
    World/Robot/Sensor API
    JSONC 配置
    Simulation Clock

5. 我们吸收什么
    核心与宿主分离
    配置化组件组合
    独立仿真时钟
    对象化客户端 API
    独立数据采集模块
    双通信通道

6. 是否进入主干
    不直接作为默认仿真后端
    其设计进入核心 API 和 UE 前端架构

7. 风险
    API 尚在演进
    不兼容经典 AirSim
    UE 依赖
    系统复杂度高
    与 ROS2 主干需要额外映射

8. 第一阶段任务
    架构解剖
    时钟与配置研究
    API 提炼
    数据采集研究

9. 长期用途
    UE 高保真前端
    视觉数据生成
    仿真服务
    自动化实验
```

---

# 6.17 最终判断

```text
是否进入主干：
    不作为默认物理真值后端

进入哪一层：
    核心接口设计参考
    UE 宿主适配参考
    仿真时钟参考
    配置系统参考
    数据采集参考

主要吸收：
    Sim Libs / Plugin / Client 三层架构
    World / Robot / Sensor 实体 API
    组件运行时组合
    JSONC 配置系统
    独立 Sim Clock
    PX4 双通信通道
    数据采集和增强

不承担：
    ROS2 主总线
    默认 Gazebo 物理后端
    高吞吐强化学习训练
    唯一飞控接口

和 Gazebo 的关系：
    Gazebo继续作为主真值后端，Project AirSim提供平台分层和UE前端设计启发

和 PX4 的关系：
    支持 PX4 SITL/HITL，其通信分层值得吸收

和 ROS2 的关系：
    需要将其客户端 API 思想映射到 ROS2 topic/service/action

和 Cosys-AirSim 的关系：
    Cosys 是旧架构延续，Project AirSim 是新架构重构
```

一句话：

> **Project AirSim 最值得我们学习的，不是某个无人机模型，而是它把仿真核心、Unreal 宿主和外部客户端彻底分层，并通过配置组合物理、控制器、执行器和传感器。我们应该把这种分层思想吸收到自己的核心 API、仿真时钟和 UE 前端中，但仍保留 ROS2 + Gazebo + PX4 作为当前主干。**
>
