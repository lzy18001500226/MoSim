# 4. 项目概述：AirSim / Project AirSim

## 4.1 定位

AirSim 是微软研究院推出的高真实感自动驾驶与无人机仿真平台，核心定位是：

> **把 Unreal Engine 或 Unity 的高保真三维环境，包装成一个可供无人机、汽车、视觉算法、飞控和自主系统调用的仿真平台。**

它不是单纯的 UE 地图，也不是单纯的飞行动力学库，而是介于“游戏引擎”和“机器人仿真器”之间的一层。

AirSim 官方文档将其描述为一个面向无人机、汽车等载具的开源跨平台仿真器，主要构建在 Unreal Engine 上，同时曾提供实验性的 Unity 版本；它支持 PX4、ArduPilot 等飞控的软件在环，也支持 PX4 硬件在环。([微软 GitHub](https://microsoft.github.io/AirSim/?utm_source=chatgpt.com "Home - AirSim"))

对我们来说，AirSim 的价值不是直接作为长期项目唯一底座，而是研究以下问题：

```text
如何让 UE 从“漂亮地图”变成“可编程仿真环境”？

如何把无人机、相机、深度、LiDAR、碰撞和飞控接口封装成统一 API？

如何把渲染、车辆模型、飞控通信和外部算法解耦？

如何让 Python/C++ 算法控制 UE 场景中的无人机？

如何组织高保真视觉仿真和数据集生成？
```

AirSim 在我们架构里的候选定位是：

```text
高真实感展示与视觉传感器参考平台

而不是：
    默认物理真值后端
    ROS2 系统总线
    唯一飞控平台
    大规模强化学习训练核心
```

---

## 4.2 AirSim 与 Project AirSim 的关系

这里必须区分两个项目。

### AirSim

经典的 `microsoft/AirSim`：

```text
主要特点：
    UE4 为主
    无人机/汽车
    SimpleFlight
    PX4 / ArduPilot
    相机、深度、分割、LiDAR
    Python/C++ API
    SITL / HITL
```

微软官方 AirSim 文档已说明，团队后来把主要精力转向新的 Project AirSim。与此同时，PX4 当前文档将 AirSim 标记为“社区支持和维护”，并提醒它可能无法与当前版本 PX4 正常兼容。([微软 GitHub](https://microsoft.github.io/AirSim/?utm_source=chatgpt.com "Home - AirSim"))

这意味着经典 AirSim：

```text
非常值得研究架构
非常适合复用历史经验
但不应该不加评估地直接作为长期主干
```

### Project AirSim

Project AirSim 是 AirSim 的后续演化方向，定位为用于构建、训练和测试自主系统的高保真仿真平台。当前公开版本由 IAMAI 发布在 GitHub，并说明它源于微软 Project AirSim，采用开放仓库形式。其 API 文档明确指出，不以严格兼容经典 AirSim API 为目标。([GitHub](https://github.com/iamaisim/ProjectAirSim?utm_source=chatgpt.com "GitHub - iamaisim/ProjectAirSim: Project AirSim is Microsoft's evolution of AirSim, an advanced simulation platform for building, training, and testing autonomous systems in high-fidelity virtual environments · GitHub"))

所以两者关系可以理解为：

```text
AirSim：
    第一代高保真无人机/汽车仿真平台

Project AirSim：
    更平台化、更强调自主系统开发的新架构

关系：
    设计思想延续
    API 和架构不保证直接兼容
```

对于我们：

```text
AirSim：
    学习成熟无人机接口、传感器 API、UE 集成方式

Project AirSim：
    学习新一代平台配置、服务化、机器人模型和运行时架构
```

---

## 4.3 核心设计理念

| 设计原则           | 说明                                                                 |
| ------------------ | -------------------------------------------------------------------- |
| 游戏引擎复用       | 不自己重写高保真渲染，而是复用 UE 的地图、材质、光照和资产生态       |
| 仿真逻辑与场景解耦 | AirSim 核心作为插件加载进 UE 项目，场景和仿真功能相互独立            |
| 统一车辆 API       | 无论是 SimpleFlight、PX4 还是其他飞控，外部程序尽量通过统一 API 控制 |
| 物理与飞控可替换   | 可以使用 AirSim 自带 SimpleFlight，也可以接 PX4/ArduPilot            |
| 传感器优先         | 相机、深度、语义分割、LiDAR、IMU、GPS 等是平台核心能力               |
| 外部算法优先       | Python/C++ 算法通过 RPC/API 访问仿真，而不是强制写进 UE 蓝图         |
| 高保真视觉优先     | 重点服务视觉感知、自动驾驶、数据生成和高质量展示                     |
| 网络解耦           | 飞控、仿真器和算法可以通过 TCP/UDP/MAVLink 等方式分进程运行          |

AirSim 的代码结构文档显示，它将不同飞控支持放在独立目录中，例如 SimpleFlight、PX4 和 ArduPilot，并通过适配层与 UE 中的 AirSim 组件连接。这体现的正是“飞控可替换、仿真接口统一”的思想。([微软 GitHub](https://microsoft.github.io/AirSim//code_structure/?utm_source=chatgpt.com "Code Structure - AirSim"))

---

# 4.4 系统设计逻辑

## 4.4.1 第一性原理：为什么 AirSim 选择 UE，而不是自己写渲染器？

高真实感视觉仿真最贵的部分，不只是画一个无人机，而是：

```text
大规模城市地图
建筑物
道路
植被
材质
光照
天气
阴影
反射
后处理
摄像机
动画
资产编辑工具
```

如果仿真器自己写一套渲染引擎，成本极高。

AirSim 的选择是：

```text
不重新造完整图形引擎
        ↓
复用 Unreal Engine
        ↓
自己补车辆、传感器、飞控、通信和 API
```

因此 AirSim 本质上不是“替代 UE”，而是：

```text
给 UE 加上一层无人机/汽车仿真能力
```

这正是我们需要研究的地方。

我们现在想做的是：

```text
Gazebo 算真值
UE 做高保真展示
ROS2 做通信
PX4 做飞控
```

AirSim 则告诉我们：

```text
UE 不一定只能被动显示
还可以通过插件变成一个可编程传感器和车辆环境
```

---

## 4.4.2 第二性原理：为什么要把飞控和仿真器解耦？

AirSim 支持两类主要飞控路线。

### SimpleFlight

AirSim 自带的简化飞控：

```text
优点：
    配置简单
    不需要额外启动 PX4
    适合快速测试 API 和场景

缺点：
    不等于真实 PX4 工程链
    不适合验证完整真实飞控栈
```

### PX4 / ArduPilot

外部真实飞控软件：

```text
PX4 算飞控
AirSim 算车辆/传感器/环境
两者通过网络和飞控协议连接
```

AirSim 的 PX4 设置文档明确指出，PX4 配置并不简单；如果用户缺乏 PX4 经验，官方建议先使用默认的 SimpleFlight。([微软 GitHub](https://microsoft.github.io/AirSim/px4_setup/?utm_source=chatgpt.com "PX4 Setup for AirSim - AirSim"))

这体现了一个重要设计思想：

```text
仿真器不应该把飞控写死
```

对我们也是一样：

```text
默认可以用 PX4
后续也允许：
    自定义 C++ 控制器
    Simulink 生成控制器
    RL policy
    其他飞控
```

但平台接口要统一。

---

## 4.4.3 第三性原理：为什么传感器是 AirSim 的核心，而不是附加功能？

对于高真实感仿真，人看画面只是一个用途。

更重要的是让算法看到：

```text
RGB 图像
深度图
语义分割图
表面法线
光流
LiDAR
IMU
GPS
碰撞事件
```

AirSim 的价值在于，它把 UE 的渲染场景转换成算法可以使用的数据。

例如：

```text
UE 场景
    ↓
AirSim Camera
    ↓
RGB / Depth / Segmentation
    ↓
Python/C++ 算法
```

所以 AirSim 不是简单“无人机在 UE 里飞”，而是：

> **让 UE 地图成为可查询、可控制、可生成传感器数据的仿真世界。**

这对我们长期项目尤其重要。因为如果后面要做视觉导航、深度学习、目标检测、语义分割或 sim-to-real，仅仅将 Gazebo 位姿同步到 UE 是不够的。

我们最终可能需要：

```text
UE 相机图像
UE 深度图
UE 语义标签
UE 光流
```

AirSim 就是这条路线最重要的参考。

---

## 4.4.4 第四性原理：外部算法为什么通过 API，而不是写进 UE？

如果把规划和控制都写成 UE 蓝图或 UE C++ 逻辑，会导致：

```text
算法和场景绑死
研究人员必须熟悉 UE
难以接 Python
难以接强化学习
难以做批量实验
难以切换仿真后端
```

AirSim 采用客户端 API：

```text
Python/C++ Client
        ↓ RPC
AirSim Server / UE Plugin
        ↓
车辆、传感器、场景
```

这样算法可以运行在 UE 之外。

AirSim API 文档提供了大量控制车辆、读取图像、设置对象材质以及执行 UE console command 等接口，这说明其核心思想是将 UE 仿真能力通过程序接口暴露给外部算法。([微软 GitHub](https://microsoft.github.io/AirSim/api_docs/html/?utm_source=chatgpt.com "airsim — airsim 1.8.1 documentation"))

对我们的启发是：

```text
规划器不要写死在 UE
控制器不要写死在 UE
RL policy 不要写死在 UE

UE 只提供：
    显示
    高保真视觉传感器
    场景交互
```

算法仍然放在：

```text
ROS2
C++
Python
PX4
```

---

# 4.5 AirSim 的主要架构

AirSim 可以简化成以下结构：

```text
┌────────────────────────────────────┐
│            UE 场景与渲染             │
│ 地图 / 材质 / 光照 / Actor / Camera │
└─────────────────┬──────────────────┘
                  │
┌─────────────────▼──────────────────┐
│            AirSim UE Plugin         │
│ 车辆 / 传感器 / 碰撞 / API / 时钟   │
└───────┬───────────┬───────────────┘
        │           │
        │           └──────────────┐
        ▼                          ▼
  SimpleFlight                PX4 / ArduPilot
  内置简化飞控                 外部真实飞控栈
        │                          │
        └──────────┬───────────────┘
                   ▼
           Python / C++ Client
       规划 / 控制 / 数据采集 / AI
```

如果接 PX4：

```text
PX4
    ↓ 电机/控制输出
AirSim
    ↓ 动力学、环境、虚拟传感器
PX4
    ↓ 状态
外部算法 / QGroundControl
```

PX4 官方目前仍保留 AirSim SITL/HITL 文档，但同时明确提醒 AirSim 是社区支持项目，可能不能适配当前 PX4 版本。([PX4 文档](https://docs.px4.io/main/en/sim_airsim/index.html?utm_source=chatgpt.com "AirSim Simulation | PX4 Guide (main)"))

---

# 4.6 AirSim 的时间管理设计

## 4.6.1 为什么需要 Lockstep？

如果 PX4 按自己的时钟运行，而 AirSim/UE 按渲染帧率运行，会发生：

```text
PX4 已经走了 10 个控制周期
AirSim 才更新了 2 帧

或者：

UE 卡顿
但飞控时间仍继续走
```

这样仿真不可重复。

AirSim 提供 Lockstep 和 SteppableClock 机制。官方文档建议，在 PX4 SITL lockstep 模式下，让 AirSim 使用 `SteppableClock`，并启用 TCP 和 LockStep。([微软 GitHub](https://microsoft.github.io/AirSim/px4_lockstep/?utm_source=chatgpt.com "PX4 Lockstep - AirSim"))

其核心逻辑是：

```text
PX4 请求下一步
AirSim 完成这一步物理和传感器
双方确认
再进入下一步
```

这对我们非常重要。

如果我们未来做 Gazebo + UE 双世界，至少要区分：

```text
弱同步：
    UE 只做显示
    每帧读取最新 Gazebo 状态

强同步：
    UE 要生成相机/深度/LiDAR
    必须和 Gazebo/PX4 共用仿真时间
```

AirSim 的 Lockstep 设计就是强同步的重要参考。

---

# 4.7 AirSim 的配置思想

AirSim 大量使用 `settings.json` 配置：

```text
车辆类型
飞控类型
PX4 地址
传感器
相机
时钟类型
锁步模式
车辆初始位置
网络接口
```

这意味着仿真行为尽可能通过配置修改，而不是改源码。

对我们的长期项目也应该如此：

```text
project.yaml
vehicle.yaml
sensor.yaml
world.yaml
bridge.yaml
experiment.yaml
```

例如：

```text
vehicle:
    type: sunray_150
    autopilot: px4

physics:
    backend: gazebo

render:
    backend: unreal

sensors:
    lidar: mid360
    camera: front_rgb

time:
    synchronization: lockstep
```

核心思想是：

> **把平台能力写在代码里，把具体实验写在配置里。**

---

# 4.8 AirSim 与 Gazebo 的根本区别

| 维度         | AirSim                           | Gazebo/gz-sim                 |
| ------------ | -------------------------------- | ----------------------------- |
| 核心目标     | 高真实感视觉和自动驾驶仿真       | 通用机器人物理与传感器仿真    |
| 渲染         | UE 为主                          | Gazebo Rendering / OGRE2      |
| 场景资产     | UE 地图资产生态                  | SDF/mesh/primitive            |
| 机器人生态   | 相对有限                         | ROS/Gazebo 机器人生态强       |
| PX4          | 支持 SITL/HITL，但当前兼容需评估 | PX4 官方主流仿真路线          |
| ROS2         | 非原生核心，需要桥接             | ros_gz 原生生态更成熟         |
| 视觉传感器   | 强                               | 可用，但视觉真实感通常弱于 UE |
| LiDAR/IMU    | 支持                             | 工程机器人传感器生态更自然    |
| 强化学习     | 可接 Python API                  | 可接 ROS/Gym，但速度不一定高  |
| 适合作为主干 | 不建议直接作为唯一主干           | 建议作为真值后端              |
| 适合作为前端 | 很适合                           | 一般                          |

所以不是：

```text
AirSim 和 Gazebo 二选一
```

而是可以吸收：

```text
Gazebo：
    机器人真值后端

AirSim：
    UE 高真实感和传感器 API 参考
```

---

# 4.9 AirSim 与我们“双世界架构”的关系

我们现在规划的是：

```text
Gazebo：
    真值物理
    碰撞
    MID360
    PX4
    ROS2

UE：
    高保真地图
    实时展示
    后续视觉传感器
```

AirSim 提供了两种可借鉴方案。

## 方案一：只借 AirSim 的显示和 API 思想

```text
Gazebo 算位置姿态
        ↓
ROS2 / UDP
        ↓
UE Actor
        ↓
实时高保真展示
```

这时不直接运行 AirSim，只参考它的：

```text
UE 插件架构
车辆 Actor 组织
相机 API
对象 API
传感器组织
坐标转换
```

这是目前最稳的路线。

## 方案二：让 AirSim/Project AirSim 成为 UE 感知前端

```text
Gazebo 算真值
        ↓
同步位姿到 AirSim/UE
        ↓
AirSim 生成 RGB/Depth/Segmentation
        ↓
ROS2 感知节点
```

这时：

```text
Gazebo：
    物理权威

AirSim/UE：
    视觉权威
```

但会产生强同步、地图一致性、重复物理、坐标转换等问题。

## 方案三：AirSim 直接替代 Gazebo

```text
PX4 + AirSim + UE
```

这条路线展示好，但对于我们的目标存在问题：

```text
ROS2/Gazebo 生态被削弱
MID360/SLAM/规划工程接口需要额外适配
当前 PX4 兼容性存在维护风险
长期项目受 UE 和 AirSim 技术版本影响
```

因此不推荐作为默认主干。

---

# 4.10 我们应该吸收 AirSim 哪些设计？

## 吸收一：高保真渲染与算法分离

```text
UE：
    地图、画面、视觉传感器

算法：
    Python/C++/ROS2

二者通过 API 通信
```

不要把算法写进 UE 场景逻辑。

---

## 吸收二：统一车辆 API

AirSim 不要求外部程序理解所有 UE 内部对象，而是暴露统一接口。

我们的长期项目也应该有统一 API：

```text
reset()
pause()
step()
spawn_vehicle()
set_vehicle_pose()
get_vehicle_state()
get_sensor_data()
set_weather()
set_fault()
load_world()
```

这会直接服务后续：

```text
强化学习
自动测试
场景生成
批量实验
外部客户端
```

---

## 吸收三：传感器抽象

传感器不应该散落在代码里。

建议统一定义：

```text
SensorBase
    update()
    get_data()
    reset()
    set_noise()
    set_rate()
```

具体传感器：

```text
CameraSensor
DepthSensor
SegmentationSensor
LidarSensor
ImuSensor
GpsSensor
```

---

## 吸收四：配置驱动

车辆、传感器、网络、场景、时钟都应由配置定义。

不要为了换相机位置去改 C++。

---

## 吸收五：锁步同步

如果 UE 以后生成视觉数据，必须有：

```text
step_id
simulation_time
sensor_timestamp
state_timestamp
```

不能只靠 UE 的 `Tick()` 和当前帧率。

---

## 吸收六：场景与仿真插件分离

同一套仿真插件应该能加载到不同 UE 地图：

```text
室内实验室
城市
森林
厂区
低空园区
```

地图不应该和无人机仿真逻辑绑死。

---

# 4.11 我们不应该照搬 AirSim 的地方

## 不照搬一：不要把 UE 变成唯一仿真后端

如果所有物理、传感器和地图都只存在于 UE：

```text
平台会被 UE 锁死
Gazebo/ROS2 生态难以利用
无头运行和批量实验更复杂
开源程度受 UE 许可证影响
```

---

## 不照搬二：不要依赖旧版 AirSim API 作为长期标准

经典 AirSim 已经不再是微软主要投入方向，而 Project AirSim 又明确不保证经典 API 的严格兼容。([微软 GitHub](https://microsoft.github.io/AirSim/?utm_source=chatgpt.com "Home - AirSim"))

所以我们可以参考其 API，但不应该直接把自己平台的永久公共接口设计成 AirSim API 的翻版。

---

## 不照搬三：不要让 UE 帧率决定仿真时间

高真实感地图复杂时，帧率会波动。

必须让：

```text
仿真时间
控制周期
传感器周期
渲染周期
```

相互解耦。

---

## 不照搬四：不要让显示碰撞替代仿真碰撞

第一阶段：

```text
Gazebo 碰撞 = 权威
UE 碰撞 = 展示辅助
```

否则会产生双主世界。

---

## 不照搬五：不要把强化学习训练直接绑在高保真 UE

UE 场景适合：

```text
验证
视觉训练
数据集生成
展示
```

但不一定适合几千个并行环境的高吞吐 RL。

大规模训练更适合：

```text
MuJoCo
Genesis
Isaac Lab
MJX
其他 GPU 并行后端
```

UE/AirSim 更适合最终高保真验证。

---

# 4.12 对 AirSim 源码结构的理解

AirSim 中比较值得研究的模块大致包括：

```text
AirLib
    与 UE 相对独立的核心仿真、车辆、传感器和 API 逻辑

Unreal/Plugins/AirSim
    UE 插件层

MavLinkCom
    MAVLink 通信

Multirotor
    多旋翼车辆与飞控适配

SimpleFlight
    内置简化飞控

PythonClient
    Python API 与示例

ros
    ROS 接口相关代码

settings
    配置解析
```

它的重要设计不是目录名，而是分层：

```text
核心仿真库
    ↓
引擎适配层
    ↓
车辆/飞控适配层
    ↓
网络 API 层
    ↓
外部算法客户端
```

这比把所有逻辑写进 UE Actor 更成熟。

---

# 4.13 Project AirSim 值得研究的地方

Project AirSim 更值得研究的是“平台化配置和服务化”。

根据其公开仓库和文档，Project AirSim 重点涉及：

```text
机器人配置
环境配置
客户端 API
仿真服务
场景和传感器配置
可扩展自动系统测试
```

它明确不追求与经典 AirSim API 的严格兼容，说明它试图重新设计平台，而不是只给经典 AirSim 打补丁。([GitHub](https://github.com/iamaisim/ProjectAirSim?utm_source=chatgpt.com "GitHub - iamaisim/ProjectAirSim: Project AirSim is Microsoft's evolution of AirSim, an advanced simulation platform for building, training, and testing autonomous systems in high-fidelity virtual environments · GitHub"))

对我们来说应该重点研究：

```text
配置系统怎么设计
机器人模型怎么注册
客户端和服务端怎么分离
仿真生命周期怎么管理
如何支持多机器人
如何批量运行
如何组织传感器数据
```

但不应默认它可以直接替代我们已经选定的 ROS2/Gazebo/PX4 主干。

---

# 4.14 在我们长期架构里的位置

推荐位置：

```text
                         ┌──────────────────────┐
                         │    UE 高保真前端       │
                         │ 可参考 AirSim 插件架构 │
                         └──────────↑───────────┘
                                    │
                             状态/传感器同步
                                    │
┌───────────────────────────────────┴────────────────────────────┐
│                         ROS2 系统总线                           │
└──────────────↑──────────────────────────────↓─────────────────┘
               │                              │
        Gazebo 真值后端                 感知/规划/控制节点
               │                              │
               └──────────── PX4 ─────────────┘
```

AirSim 不一定直接处于运行主链，但其设计进入：

```text
UE 前端架构
视觉传感器接口
车辆 API
场景 API
时间同步
外部算法接口
```

---

# 4.15 最小研究任务

针对 AirSim / Project AirSim，我们不急着先跑完整系统，先完成源码解剖。

```text
1. 理清 AirLib、UE Plugin、MavLinkCom、SimpleFlight 的边界
2. 理清 UE 如何加载 AirSim 插件
3. 理清车辆 Actor 与 AirLib 状态如何同步
4. 理清 PythonClient RPC 链路
5. 理清相机、深度、分割和 LiDAR 数据生成过程
6. 理清 PX4 SITL/HITL 接口
7. 理清 SteppableClock 和 Lockstep
8. 理清 settings.json 配置体系
9. 对比经典 AirSim 和 Project AirSim 架构
10. 写 AirSim REVIEW.md
```

不要先投入大量精力修旧版 AirSim 的编译问题。因为 PX4 已明确提醒其当前兼容性属于社区维护状态。([PX4 文档](https://docs.px4.io/main/en/sim_airsim/index.html?utm_source=chatgpt.com "AirSim Simulation | PX4 Guide (main)"))

---

# 4.16 AirSim REVIEW.md 应该写什么

```text
1. 项目定位
    基于 UE 的高真实感无人机/车辆仿真平台

2. 它解决什么问题
    高保真视觉、车辆仿真、传感器数据、外部控制 API、PX4 接入

3. 它不解决什么问题
    ROS2 全栈生态、通用机器人模型、长期 PX4 官方主线、大规模高速 RL

4. 核心设计
    UE 插件
    AirLib
    统一车辆 API
    传感器抽象
    SimpleFlight/PX4 可替换
    配置驱动
    Lockstep

5. 我们吸收什么
    UE 插件架构
    高保真视觉传感器
    客户端 API
    场景与算法分离
    时间同步
    配置系统

6. 是否进入主干
    不直接作为默认仿真主干
    作为 UE 前端和视觉仿真参考

7. 风险
    经典项目维护减弱
    当前 PX4 兼容性不稳定
    UE 版本依赖
    编译环境复杂
    ROS2 接入不是天然主线

8. 第一阶段用途
    源码和架构研究
    提炼 UE 前端设计

9. 长期用途
    高真实感显示
    视觉传感器
    sim-to-real
    数据集生成
```

---

# 4.17 对 AirSim / Project AirSim 的最终判断

```text
是否进入主干：
    不作为默认真值后端

进入哪一层：
    高真实感前端参考
    视觉传感器参考
    API 与场景服务设计参考

主要吸收：
    UE 插件架构
    统一车辆 API
    Python/C++ 客户端
    PX4 飞控适配
    传感器抽象
    Lockstep
    配置驱动
    场景与算法解耦

不承担：
    默认物理真值
    ROS2 总线
    长期唯一飞控接口
    大规模 RL 训练后端

和 Gazebo 的关系：
    Gazebo 算真值，AirSim 思想帮助构建 UE 感知与展示前端

和 PX4 的关系：
    AirSim 可接 PX4 SITL/HITL，但当前兼容性需单独验证

和 ROS2 的关系：
    可桥接，但不是其原生核心架构

和 UE 的关系：
    AirSim 本质上是把 UE 变成可编程无人机仿真环境
```

一句话：

> **AirSim 最值得我们学习的，不是“直接拿来当最终平台”，而是它如何把 UE 的漂亮地图、车辆、传感器、PX4 和外部 Python/C++ 算法组织成一个可编程仿真系统。我们可以保留 Gazebo 作为真值后端，同时吸收 AirSim 的 UE 插件、视觉传感器、统一 API 和锁步同步设计。**

下一篇应继续讲 **Cosys-AirSim / AirSimExtensions / ProjectAirSim** 这一组分支，因为这些项目就是在解决经典 AirSim 停更、UE5 迁移和功能扩展问题。
