# 12. 项目组概述：NVIDIA Isaac Sim、Isaac Lab 与 Pegasus Simulator

这一组需要放在一起理解，因为它们分别对应三个层次：

```text
Isaac Sim
    通用机器人仿真、GPU物理、RTX传感器、场景与合成数据平台

Isaac Lab
    基于 Isaac Sim 的机器人学习、强化学习与模仿学习框架

Pegasus Simulator
    基于 Isaac Sim 构建的多旋翼无人机专用扩展
    补充四旋翼动力学、传感器、PX4和控制接口
```

可以把三者类比成：

```text
Isaac Sim
    是 GPU 机器人仿真基础设施和三维世界

Isaac Lab
    是建立在世界之上的机器人训练场和任务框架

Pegasus Simulator
    是面向无人机搭建的专用飞行套件
```

对我们的长期项目而言，这一组的价值很高，但不能简单得出：

```text
以后全部改用 Isaac Sim
```

更准确的定位是：

```text
Gazebo + PX4 + ROS2
    当前开源工程主线

Isaac Sim + Pegasus
    高保真GPU仿真和无人机验证分支

Isaac Lab
    高保真强化学习和多模态训练分支

UE
    最终展示前端或特定高质量视觉前端
```

---

## 12.1 项目定位

### 12.1.1 Isaac Sim

Isaac Sim 是 NVIDIA 面向机器人和 Physical AI 的仿真平台。它将以下能力组合在同一个体系中：

```text
OpenUSD场景和资产
GPU物理
机器人模型
相机、LiDAR和其他传感器
RTX渲染
ROS2桥接
合成数据生成
Python/C++扩展
强化学习接入
```

当前官方文档将其定位为机器人仿真和合成数据生成平台，可使用 PhysX 或 Newton 物理后端、物理型和RTX传感器、ROS2接口，并为 Isaac Lab 提供仿真基础。([Isaac Sim 文档](https://docs.isaacsim.omniverse.nvidia.com/?utm_source=chatgpt.com "What Is Isaac Sim? — Isaac Sim Documentation"))

它并不是单纯的“好看版Gazebo”，而是：

> **以OpenUSD组织场景，以Omniverse Kit组织软件扩展，以GPU物理和RTX渲染生成机器人状态与传感器数据的平台。**

---

### 12.1.2 Isaac Lab

Isaac Lab 是建立在 Isaac Sim 之上的官方机器人学习框架，面向：

```text
强化学习
模仿学习
运动规划
域随机化
并行环境
多模态传感器训练
sim-to-real
```

Isaac Sim负责世界、物理、传感器和渲染，Isaac Lab负责把这些能力组织成：

```text
环境
动作
观测
奖励
终止条件
命令
课程学习
随机化事件
训练与评估流程
```

官方将 Isaac Lab 描述为 Isaac Sim 的开源机器人学习参考框架，并支持大规模、多模态机器人学习。([Isaac Sim 文档](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/isaac_lab_tutorials/index.html?utm_source=chatgpt.com "Isaac Lab — Isaac Sim Documentation"))

---

### 12.1.3 Pegasus Simulator

Pegasus Simulator 是建立在 Isaac Sim 之上的多旋翼无人机专用框架。

它补充了 Isaac Sim 本身缺少的无人机专用能力：

```text
多旋翼动力学
旋翼推力和反扭矩
IMU等传感器
多无人机
PX4 MAVLink接口
自定义Python控制器
控制与通信Backend
无人机GUI配置
```

官方文档明确表示，Pegasus目前主要支持多旋翼，提供PX4仿真接口和自定义Python控制接口；其源码采用BSD-3-Clause许可证。([Pegasus Simulator](https://pegasussimulator.github.io/PegasusSimulator/ "Pegasus Simulator — Pegasus Simulator  documentation"))

所以这一组的分工是：

```text
Isaac Sim：
    通用仿真平台

Isaac Lab：
    学习任务和训练平台

Pegasus：
    无人机专用仿真层
```

---

# 12.2 开源程度与许可证边界

这是我们特别需要注意的部分。

## 12.2.1 Isaac Sim是不是开源？

当前NVIDIA官方页面说明，Isaac Sim可以免费使用，代码以Apache 2.0许可证开放并可在GitHub获取。([NVIDIA Developer](https://developer.nvidia.com/Isaac-sim "Isaac Sim - Robotics Simulation and Synthetic Data Generation | NVIDIA Developer"))

但这不代表整个发布链都没有额外边界。

官方同时说明：

```text
Isaac Sim源码：
    Apache 2.0开源

在自己的产品中重新分发Omniverse Kit：
    可能需要单独的NVIDIA许可
```

也就是说，对于个人研究、学校研究和内部开发，开源程度已经很高；但如果以后把它整体封装成自己的商业软件再分发，需要单独检查Omniverse Kit及附带资产的许可。([NVIDIA Developer](https://developer.nvidia.com/Isaac-sim "Isaac Sim - Robotics Simulation and Synthetic Data Generation | NVIDIA Developer"))

所以不能简单写成：

```text
Isaac Sim完全没有许可证问题
```

更准确是：

> **Isaac Sim源代码是开源的，但其完整运行生态仍和Omniverse Kit、NVIDIA驱动、RTX组件及部分附带资产存在许可与平台依赖。**

---

## 12.2.2 Isaac Lab和Pegasus

Isaac Lab的公开代码和文档采用BSD-3-Clause许可证；Pegasus Simulator同样采用BSD-3-Clause。([Isaac Sim](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_base_env.html "Creating a Manager-Based Base Environment — Isaac Lab Documentation"))

因此从代码学习和二次开发角度看：

```text
Isaac Lab：
    许可证宽松

Pegasus：
    许可证宽松

真正需要额外审核的：
    Isaac Sim附带组件
    Omniverse Kit再分发
    场景资产
    第三方机器人模型
```

---

# 12.3 Isaac Sim的核心设计理念

| 设计原则            | 说明                                                                |
| ------------------- | ------------------------------------------------------------------- |
| OpenUSD作为场景语言 | 机器人、环境、材质、碰撞、传感器和属性都组织在USD场景树中           |
| 场景组合优先        | 通过Layer、Reference、Variant和Override组合大型场景，而不是复制模型 |
| 扩展式应用          | Isaac Sim建立在Omniverse Kit扩展体系上，各项能力以Extension组合     |
| 物理与场景解耦      | USD描述物理语义，运行时再生成PhysX或Newton对象                      |
| GPU物理与渲染       | 尽可能在GPU上完成物理、传感器和RTX渲染                              |
| OmniGraph数据流     | ROS2、传感器、控制器、Replicator和UI通过计算图连接                  |
| 合成数据优先        | 把RGB、深度、分割、包围框等标注作为平台一级能力                     |
| 多环境和无头运行    | 同一场景模板可以复制大量环境，用于训练和自动化测试                  |
| Python自动化        | 场景构造、实验控制、传感器配置和任务运行都可脚本化                  |
| ROS2接入            | 通过ROS2 Bridge将仿真机器人接入外部机器人系统                       |

---

# 12.4 第一性原理：为什么Isaac Sim使用OpenUSD？

## 12.4.1 传统模型文件的问题

Gazebo通常使用SDF，机器人生态也大量使用URDF。

这些格式非常适合描述：

```text
link
joint
collision
visual
sensor
plugin
```

但当场景越来越复杂时，会出现：

```text
城市地图很大
材质很多
多个团队同时修改
机器人有多个配置版本
场景有不同天气
同一资产需要高模和低模
同一架无人机需要不同传感器组合
```

如果每种组合都复制一份完整场景，就会产生大量重复资产。

---

## 12.4.2 USD的核心思想：组合，而不是复制

Isaac Sim使用USD描述机器人和环境。USD支持：

```text
Layer：
    将不同修改放在不同层

Reference：
    引用外部资产

Variant：
    同一资产的不同版本

Override：
    在不修改原文件的情况下覆盖属性

Prim：
    场景树中的基本对象
```

官方文档说明，USD是Isaac Sim描述机器人和环境的语言，其Layer和Variant能力允许不同工具和人员协同修改同一场景，而不必覆盖原始资产。([Isaac Sim 文档](https://docs.isaacsim.omniverse.nvidia.com/latest/omniverse_usd/open_usd.html "OpenUSD Fundamentals — Isaac Sim Documentation"))

例如Sunray-150可以组织成：

```text
sunray150_base.usd
    机体外观
    旋翼
    基本坐标层级

sunray150_physics.usd
    质量
    惯量
    碰撞
    物理材质

sunray150_mid360.usd
    MID360安装位姿
    LiDAR传感器

sunray150_camera.usd
    相机传感器

sunray150_training.usd
    RL随机化属性
```

最后组合成：

```text
Sunray-150 + MID360
Sunray-150 + Camera
Sunray-150 + MID360 + Camera
```

不需要复制三套完整模型。

---

## 12.4.3 USD对我们的启发

我们长期项目也应吸收“资产组合”思路。

但不应直接把USD变成唯一参数真源。

更合理的是：

```text
中立参数源：
    vehicle.yaml
    motors.yaml
    sensors.yaml
    aerodynamics.yaml
    mesh assets

后端生成：
    Gazebo SDF
    MuJoCo MJCF
    Isaac USD
    UE资产配置
```

这样可以同时利用USD的场景组合优势，又避免整个项目被Isaac生态锁死。

---

# 12.5 第二性原理：为什么采用Extension架构？

Isaac Sim不是一个固定、不可拆分的单体程序。

它建立在Omniverse Kit之上，通过Extension组合功能：

```text
物理扩展
传感器扩展
ROS2 Bridge
Replicator
资产导入
UI
Python脚本
机器人控制
自定义工具
```

可以把它理解为：

```text
Omniverse Kit
    是应用框架

Isaac Sim
    是一组机器人仿真扩展的组合

Pegasus
    是再安装到Isaac Sim上的无人机扩展
```

这种方式的好处是：

```text
不修改Isaac Sim核心
即可增加无人机、传感器或工具

功能可以单独启用和关闭
应用可以按需求裁剪
第三方项目可以发布自己的扩展
```

Pegasus正是这种理念的典型结果：它不是fork整个Isaac Sim，而是作为Extension和Python包，增加多旋翼动力学、传感器、PX4和GUI能力。([Pegasus Simulator](https://pegasussimulator.github.io/PegasusSimulator/ "Pegasus Simulator — Pegasus Simulator  documentation"))

对我们的项目，应该吸收为：

```text
core/
    标准接口和数据结构

plugins/
    vehicles/sunray150
    sensors/mid360
    backends/gazebo
    backends/isaac
    controllers/px4
    renderers/unreal
    training/isaac_lab
```

---

# 12.6 OmniGraph：Isaac Sim内部的系统总线

## 12.6.1 定位

OmniGraph是Omniverse中的可视化计算图和数据流框架。

在Isaac Sim里，它用于连接：

```text
传感器
ROS2 Bridge
控制器
Replicator
外部输入设备
UI
仿真时钟
自定义节点
```

官方文档明确说明，OmniGraph是Isaac Sim中Replicator、ROS2 Bridge、传感器访问、控制器和外部设备等能力的主要执行框架。([Isaac Sim 文档](https://docs.isaacsim.omniverse.nvidia.com/latest/omnigraph/index.html?utm_source=chatgpt.com "OmniGraph — Isaac Sim Documentation"))

---

## 12.6.2 它和ROS2有什么区别？

OmniGraph是Isaac Sim**进程内部**的数据流。

ROS2是机器人系统**跨进程、跨设备**的通信总线。

可以这样理解：

```text
OmniGraph：
    Isaac Sim身体内部的神经网络

ROS2：
    整个机器人系统之间的通信网络
```

典型链路：

```text
Isaac Sim相机
    ↓ OmniGraph
ROS2 Camera Publisher
    ↓ DDS
ROS2视觉节点
```

或者：

```text
ROS2控制指令
    ↓ ROS2 Bridge
OmniGraph
    ↓
Isaac Sim机器人执行器
```

因此我们不应尝试用OmniGraph替代ROS2。

---

## 12.6.3 对我们的启发

Isaac后端内部可以使用：

```text
OmniGraph
```

但整个项目外部接口仍应统一为：

```text
ROS2
Python API
统一VehicleState
统一SensorData
```

也就是：

```text
后端内部技术
    可以不同

后端外部接口
    必须统一
```

---

# 12.7 物理系统：PhysX与Newton

## 12.7.1 PhysX

PhysX长期以来是Isaac Sim默认物理后端。

它负责：

```text
刚体
碰撞
关节
多关节机器人
接触
车辆动力学
GPU加速
```

Isaac Sim会读取USD Physics Schema，根据场景属性创建对应的物理对象。当前官方文档仍将PhysX列为默认后端。([Isaac Sim 文档](https://docs.isaacsim.omniverse.nvidia.com/latest/physics/index.html?utm_source=chatgpt.com "Physics — Isaac Sim Documentation"))

---

## 12.7.2 Newton

当前Isaac Sim还在引入Newton作为新的实验物理后端。Newton是由NVIDIA、Google DeepMind和Disney Research等合作推进的开源GPU物理项目，基于NVIDIA Warp和OpenUSD，并计划与Isaac Lab、MuJoCo Playground等学习框架结合。([NVIDIA Developer](https://developer.nvidia.com/Isaac-sim "Isaac Sim - Robotics Simulation and Synthetic Data Generation | NVIDIA Developer"))

这反映了Isaac生态的一个重要方向：

```text
场景：
    继续使用OpenUSD

物理后端：
    不再永远固定为PhysX
```

这与我们正在设计的：

```text
统一场景和状态接口
    +
可替换物理后端
```

高度一致。

---

## 12.7.3 对四旋翼的意义

PhysX或Newton只会解决：

```text
刚体如何受力
位置和姿态如何更新
碰撞如何处理
```

它们不会自动知道：

```text
四旋翼电机推力曲线
桨叶反扭矩
电机时间常数
机身空气阻力
下洗效应
电池衰减
电机故障
```

这些仍要由Pegasus或我们自己的无人机动力学层实现。

所以：

```text
Isaac Sim有GPU物理
    ≠
自动拥有高保真四旋翼模型
```

---

# 12.8 传感器与合成数据设计

## 12.8.1 传感器类型

Isaac Sim的传感器系统包括：

```text
RGB相机
深度
语义分割
实例分割
2D/3D包围框
LiDAR
Radar
IMU
接触传感器
物理状态传感器
```

其传感器系统可生成真值型和物理型数据；当前文档也将物理传感器和RTX传感器列为核心能力。([Isaac Sim 文档](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/sensors/index.html?utm_source=chatgpt.com "Sensors — Isaac Sim Documentation"))

---

## 12.8.2 RTX传感器的基本逻辑

传统Gazebo LiDAR通常基于光栅化或几何射线计算。

Isaac RTX传感器利用RTX光线追踪场景：

```text
发射虚拟射线
    ↓
和USD场景几何求交
    ↓
获取距离、法线、材质等信息
    ↓
生成LiDAR/Radar数据
```

它的优势是：

```text
复杂场景
大规模网格
高质量遮挡
传感器与RTX视觉共享场景
```

但RTX传感器输出是否等同于真实设备，仍取决于：

```text
扫描模式
光束分布
噪声
反射率
时间戳
运动畸变
设备特性
```

---

## 12.8.3 MID360问题

Isaac Sim中存在LiDAR和RTX传感器能力，但这不意味着已经拥有完整的Livox MID360模型。

我们仍需实现或校准：

```text
MID360视场
非重复扫描模式
点频
盲区
量程
逐点时间戳
运动畸变
强度
噪声
ROS2 PointCloud2或Livox消息
```

因此合理定位是：

```text
Isaac RTX LiDAR：
    提供高质量射线和场景求交基础

MID360适配层：
    提供真实设备扫描规律和消息格式
```

---

## 12.8.4 Replicator

Isaac Sim的Replicator主要用于合成数据生成和域随机化：

```text
随机光照
随机材质
随机物体位置
随机相机
随机天气
自动生成标注
```

官方页面列出的标注能力包括RGB、包围框、实例分割和语义分割，并可导出COCO、KITTI等格式。([NVIDIA Developer](https://developer.nvidia.com/Isaac-sim "Isaac Sim - Robotics Simulation and Synthetic Data Generation | NVIDIA Developer"))

对我们未来的意义包括：

```text
无人机目标检测数据集
障碍物识别
视觉定位
语义导航
sim-to-real图像随机化
```

---

# 12.9 Isaac Lab的环境设计

## 12.9.1 为什么还需要Isaac Lab？

Isaac Sim解决的是：

```text
场景怎么加载
物理怎么算
相机怎么渲染
机器人怎么运动
```

但它本身不会自动定义：

```text
策略观察什么
策略输出什么
奖励怎么算
何时终止
如何随机化
如何组织4096个环境
如何训练PPO
```

Isaac Lab就是补齐这一层。

---

## 12.9.2 Manager-Based架构

Isaac Lab非常值得我们学习的是Manager-Based Environment。

一个环境被拆成多个Manager：

```text
Scene Manager
    管理机器人、地面和障碍物

Observation Manager
    生成策略观测

Action Manager
    将策略动作映射到执行器

Event Manager
    管理reset、随机化和运行事件

Command Manager
    生成目标速度、目标位置等任务命令

Reward Manager
    计算各奖励项

Termination Manager
    判断成功、失败和超时

Curriculum Manager
    调节训练难度
```

官方文档说明，基础Manager环境包含scene、action、observation和event管理器；RL环境进一步增加reward、termination、curriculum和command generation。([Isaac Sim](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_base_env.html "Creating a Manager-Based Base Environment — Isaac Lab Documentation"))

这比把所有逻辑写进一个巨大的 `step()`更清楚。

---

## 12.9.3 对无人机环境的映射

### Scene

```text
Sunray-150
障碍物
目标点
地面
风场
其他无人机
```

### Observation

```text
位置误差
速度
姿态
角速度
目标相对位置
电机状态
LiDAR距离
上一时刻动作
```

### Action

```text
速度目标
姿态和推力
总推力和三轴力矩
四电机命令
```

### Events

```text
重置位置
随机质量
随机惯量
随机风场
随机电机效率
随机传感器偏置
```

### Rewards

```text
位置跟踪
姿态稳定
控制平滑
能耗
安全距离
碰撞惩罚
任务完成奖励
```

### Terminations

```text
碰撞
翻转
飞出边界
高度过低
任务成功
超时
```

这种分解正适合我们的多后端统一RL接口。

---

## 12.9.4 多频率设计

Isaac Lab环境允许区分：

```text
physics dt
environment step
control frequency
render interval
sensor frequency
```

例如官方Manager环境教程用 `decimation`表示一次环境动作跨越多少个物理步。([Isaac Sim](https://isaac-sim.github.io/IsaacLab/v2.0.2/source/tutorials/03_envs/create_manager_base_env.html?utm_source=chatgpt.com "Creating a Manager-Based Base Environment — Isaac Lab Documentation"))

映射到无人机：

```text
物理：
    240 Hz

控制器：
    60 Hz

策略：
    30 Hz

相机：
    20 Hz

渲染：
    30 FPS
```

这与Flightmare、Project AirSim和我们前面确定的多时钟设计完全一致。

---

# 12.10 Pegasus Simulator的架构

## 12.10.1 为什么需要Pegasus？

Isaac Sim能导入无人机外形，也能给刚体施加力。

但它不天然提供完整的：

```text
旋翼动力学
电机模型
四旋翼控制接口
PX4 MAVLink
多无人机管理
无人机传感器链路
```

Pegasus就是在Isaac Sim上增加这层无人机语义。

---

## 12.10.2 核心模块

Pegasus可以概括为：

```text
Multirotor Vehicle
    无人机状态和组件

Dynamics
    旋翼推力、反扭矩和机体动力学

Thrusters
    单个或多个旋翼模型

Sensors
    IMU、GPS、气压计、相机等

Control Backend
    Python控制器、PX4、其他外部飞控

Environment
    Isaac Sim USD场景

Interface / GUI
    创建车辆、配置PX4和运行仿真
```

---

## 12.10.3 Backend设计

Pegasus最值得吸收的设计之一是Backend抽象。

每个Backend在仿真运行时可以接收：

```text
车辆状态
传感器数据
图形传感器数据
每一步dt
```

并向无人机返回：

```text
期望旋翼角速度
```

它还具有：

```text
initialize
start
stop
reset
update
update_state
update_sensor
input_reference
```

等生命周期接口。官方Backend文档明确描述，每个物理步都会向Backend传递车辆状态和传感器数据，Backend的 `input_reference()`则返回希望施加到各个旋翼的角速度。([Pegasus Simulator](https://pegasussimulator.github.io/PegasusSimulator/source/api/backends.backend.html "Backend — Pegasus Simulator  documentation"))

这意味着：

```text
飞行器物理
    不关心命令来自PX4还是自定义控制器

Backend
    不关心物理内部如何计算
```

这是非常干净的解耦。

---

## 12.10.4 PX4 Backend

Pegasus通过 `PX4MavlinkBackend`连接PX4。

典型链路是：

```text
Pegasus传感器和状态
    ↓ MAVLink
PX4 SITL
    ↓ 电机/旋翼命令
Pegasus Backend
    ↓
各旋翼期望转速
    ↓
Isaac Sim/Pegasus动力学
```

官方实现还支持：

```text
自动启动和停止PX4 SITL
MAVLink网络连接
lockstep
多架无人机的不同vehicle_id和端口
旋翼输入缩放
更新频率配置
```

文档示例中的默认配置使用4个旋翼、lockstep和250 Hz更新率，但这些只是默认示例参数，并不应直接套用到Sunray-150。([Pegasus Simulator](https://pegasussimulator.github.io/PegasusSimulator/source/features/px4_integration.html "PX4 Integration — Pegasus Simulator  documentation"))

---

## 12.10.5 为什么Backend比直接写PX4代码更好？

错误做法：

```text
Multirotor类里面写死：
    if PX4
    if Python PID
    if RL policy
    if ArduPilot
```

Pegasus做法：

```text
Multirotor
    只负责车辆和物理

Backend
    负责控制来源和通信
```

于是可以扩展：

```text
PX4MavlinkBackend
PythonControllerBackend
ROS2Backend
RLPolicyBackend
ReplayBackend
ArduPilotBackend
```

而不修改四旋翼动力学核心。

---

# 12.11 Pegasus与RflySim的对照

二者在设计思想上很接近。

```text
RflySim：
    CopterSim负责动力学
    PX4负责飞控
    RflySim3D/UE负责显示

Pegasus：
    Isaac Sim/Pegasus负责动力学和渲染
    PX4负责飞控
    Backend负责连接
```

主要区别：

| 维度       | RflySim                | Pegasus                                 |
| ---------- | ---------------------- | --------------------------------------- |
| 仿真基础   | CopterSim/Simulink模型 | Isaac Sim/PhysX/USD                     |
| 控制器开发 | 强依赖Simulink         | Python、PX4、ROS2更自然                 |
| 渲染       | RflySim3D/UE           | Isaac RTX                               |
| 场景格式   | 自有/UE场景            | OpenUSD                                 |
| RL         | 不是主要强项           | 可进入Isaac Lab                         |
| PX4接口    | 平台核心               | PX4 Mavlink Backend                     |
| 开源程度   | 完整平台并非全部开放   | Pegasus代码BSD，Isaac Sim源码Apache 2.0 |
| GPU并行    | 非主要设计             | Isaac Sim/Isaac Lab重要能力             |

对我们的项目，Pegasus比RflySim更接近：

```text
开源代码
Python
GPU仿真
强化学习
高质量传感器
```

但在真实PX4工程和国产硬件链路方面，仍然需要我们自己验证。

---

# 12.12 Isaac Sim与Gazebo的区别

| 维度       | Isaac Sim                    | Gazebo                                |
| ---------- | ---------------------------- | ------------------------------------- |
| 场景格式   | OpenUSD                      | SDF/URDF                              |
| 物理       | PhysX，逐步引入Newton        | DART/Bullet/ODE等后端及gz-physics生态 |
| 渲染       | RTX、Omniverse               | Gazebo Rendering/OGRE                 |
| GPU依赖    | 强                           | 相对弱                                |
| ROS2       | 有官方Bridge                 | ros_gz生态更自然                      |
| PX4        | 通过Pegasus或其他适配        | PX4官方主流仿真路线                   |
| 合成数据   | 很强                         | 基础能力                              |
| 多环境RL   | Isaac Lab强                  | 不是核心目标                          |
| 场景资产   | USD/CAD/Omniverse生态        | SDF/mesh机器人生态                    |
| 运行成本   | 较高                         | 相对更轻                              |
| 开放性     | 源码开放但NVIDIA生态依赖明显 | 更中立的开源机器人生态                |
| 我们的用途 | 高保真GPU验证与RL            | 主工程仿真后端                        |

因此不是简单二选一：

```text
Gazebo：
    主工程链

Isaac Sim：
    高保真和GPU学习链
```

---

# 12.13 Isaac Sim与UE的关系

Isaac Sim本身已经提供高质量RTX渲染，所以使用Isaac Sim时未必还需要UE。

有三种可能路线。

## 路线一：Isaac Sim自己完成物理和显示

```text
Pegasus/Isaac Sim：
    物理
    传感器
    渲染
    PX4

不再额外使用UE
```

优点：

```text
一个世界
不需要双地图
不需要状态同步
视觉和物理共用USD场景
```

缺点：

```text
依赖NVIDIA GPU和Omniverse生态
场景资产与UE生态不同
不能直接使用大量UE现成地图
```

---

## 路线二：Gazebo主干，UE最终展示

这是我们当前主线：

```text
Gazebo：
    工程物理和传感器

UE：
    高质量展示
```

Isaac Sim只作为独立验证和RL分支。

---

## 路线三：Isaac Sim训练，UE展示

```text
Isaac Sim / Isaac Lab：
    训练策略

Gazebo + PX4：
    工程验证

UE：
    最终展示
```

这更符合我们“集各家之所长”的思路。

不建议第一阶段同时运行：

```text
Gazebo
Isaac Sim
UE
```

三个三维世界。

因为这会同时产生：

```text
三套场景资产
三套坐标转换
三套时间同步
三套碰撞和传感器定义
```

除非有明确实验需求，否则没有必要。

---

# 12.14 云纵Sunray-150如何进入Isaac/Pegasus

## 12.14.1 资产层

首先建立USD资产：

```text
sunray150.usd
    机体外观
    四个电机
    桨叶
    MID360
    相机
```

但外观只是第一步。

---

## 12.14.2 物理层

必须配置：

```text
总质量
质心
惯量矩阵
碰撞体
电机位置
旋翼轴向
旋转方向
推力系数
反扭矩系数
最大转速
电机时间常数
机身阻力
```

---

## 12.14.3 Pegasus车辆层

可以有两种方法：

```text
方法A：
    配置Pegasus Multirotor
    使用其现有动力学和Backend

方法B：
    编写Sunray150Vehicle或自定义Dynamics
    更精确地模拟真实机参数
```

第一阶段先用方法A验证接口，第二阶段再逐步替换动力学。

---

## 12.14.4 PX4层

需要校验：

```text
电机编号
旋转方向
控制输入缩放
PX4机架配置
MAVLink端口
坐标系
lockstep
更新频率
```

Pegasus自带PX4 Backend可以减少大量重复工作，但其默认Iris参数不能直接代表Sunray-150。

---

## 12.14.5 传感器层

需要配置：

```text
IMU
气压计
GPS，可选
MID360
前视相机
深度相机，可选
```

MID360仍需要自定义扫描与消息适配层。

---

# 12.15 Isaac Lab中的Sunray环境

可以建立以下任务。

## Hover

```text
目标：
    固定位置悬停

动作：
    四电机
    或推力—力矩
    或姿态—推力

观测：
    位置误差
    速度
    姿态
    角速度
    上一次动作
```

## Trajectory Tracking

```text
参考：
    圆
    八字
    B样条
    真实飞行轨迹
```

## Motor Degradation

```text
随机：
    故障电机
    效率比例
    故障时间
```

## Wind Rejection

```text
随机：
    风向
    平均风速
    阵风
    气动参数
```

## Visual Navigation

```text
观测：
    RGB
    Depth
    Segmentation
    LiDAR

动作：
    速度目标
```

第一阶段建议先做：

```text
状态观测
    +
姿态—推力或速度动作
```

不要一开始同时做视觉导航和电机级控制。

---

# 12.16 我们应该吸收哪些设计？

## 吸收一：OpenUSD的分层资产系统

```text
基础模型
物理属性
传感器配置
训练配置
显示配置
```

通过引用与变体组合，而不是复制完整资产。

---

## 吸收二：Extension机制

无人机、传感器、后端和工具以插件扩展，不修改平台核心。

---

## 吸收三：OmniGraph的数据流思想

后端内部用计算图组织：

```text
传感器
ROS2
控制
数据采集
时钟
```

但对外仍统一为ROS2和标准API。

---

## 吸收四：Isaac Lab Manager架构

将环境拆成：

```text
Scene
Action
Observation
Reward
Termination
Event
Command
Curriculum
```

这非常适合作为我们统一RL任务规范。

---

## 吸收五：Pegasus Backend接口

控制来源和物理解耦：

```text
PX4 Backend
Python Backend
RL Backend
Replay Backend
```

Backend统一接收状态/传感器并返回旋翼命令。

---

## 吸收六：多频率传感器和控制

物理、控制、策略、传感器和渲染频率全部独立。

---

## 吸收七：合成数据与随机化

视觉标注、域随机化和数据采集不应写成临时脚本，而应成为平台模块。

---

## 吸收八：多环境复制

同一场景模板可以快速复制多个训练环境，参数和状态使用批量结构。

---

# 12.17 我们不应该照搬什么？

## 不照搬一：不要把USD作为唯一模型真源

USD适合Isaac场景，但Gazebo和MuJoCo还有自己的语义。

继续维护中立参数源，再生成USD、SDF和MJCF。

---

## 不照搬二：不要把NVIDIA GPU变成全项目硬依赖

主工程链仍应能在没有高端RTX显卡的设备上运行。

```text
基础模式：
    ROS2 + Gazebo + PX4

高端模式：
    Isaac Sim + Pegasus + Isaac Lab
```

---

## 不照搬三：不要认为RTX传感器等同真实传感器

特别是MID360，必须补充设备级扫描、噪声、时间戳和消息模型。

---

## 不照搬四：不要直接依赖Pegasus默认Iris模型

要建立自己的Sunray-150参数和USD资产。

---

## 不照搬五：不要忽略版本强绑定

Pegasus不同版本明确绑定对应Isaac Sim版本，官方发布说明多次注明新版本与旧Isaac Sim不兼容。([GitHub](https://github.com/PegasusSimulator/PegasusSimulator "GitHub - PegasusSimulator/PegasusSimulator: A framework built on top of NVIDIA Isaac Sim for simulating drones with PX4 support and much more · GitHub"))

因此必须维护：

```text
Isaac Sim版本
Pegasus版本
Isaac Lab版本
ROS2版本
PX4版本
NVIDIA驱动版本
```

组成的兼容矩阵。

---

## 不照搬六：不要把全部算法放进Isaac Sim

SLAM、规划、任务管理和工程控制仍应运行在：

```text
ROS2
C++
Python
PX4
```

Isaac Sim是后端，不应成为所有算法的唯一容器。

---

## 不照搬七：不要同时维护过多真值世界

Gazebo、Isaac Sim和UE不能在没有必要时同时承担完整世界。

必须明确每次实验谁是权威：

```text
Gazebo实验：
    Gazebo是真值

Isaac实验：
    Isaac Sim是真值

UE：
    默认只做展示
```

---

# 12.18 在长期架构中的位置

```text
                           UE最终展示前端
                                  ↑
                         统一VehicleState
                                  ↑
┌──────────────────────────────────────────────────────────┐
│                  Core Simulation API                     │
│ Model / State / Action / Sensor / Clock / Experiment     │
└────────────↑────────────────────↑────────────────────────┘
             │                    │
        Gazebo Backend       Isaac Backend
        工程主链             高保真GPU分支
             │                    │
         ROS2 + PX4      Pegasus + Isaac Lab
             │                    │
       MID360 / EGO       RL / Synthetic Data
```

更加具体地说：

```text
Gazebo：
    日常工程开发
    PX4 SITL
    ROS2感知规划
    MID360
    轻量复现

Isaac Sim + Pegasus：
    RTX视觉和LiDAR实验
    多无人机高保真仿真
    GPU物理
    合成数据
    PX4替代验证

Isaac Lab：
    多环境RL
    域随机化
    多模态策略
    sim-to-real研究
```

---

# 12.19 最小研究任务

针对你们已经下载的Isaac Sim和Pegasus Simulator，建议按顺序完成：

```text
1. 跑通Isaac Sim基础场景
2. 理解Stage、Prim、Layer、Reference和Variant
3. 导入URDF或简单USD机器人
4. 配置刚体、质量、惯量和碰撞
5. 理解PhysX Scene和仿真时间
6. 跑通ROS2 Bridge
7. 跑通RGB、Depth和LiDAR传感器
8. 跑通Replicator基础数据采集
9. 安装并运行Pegasus示例多旋翼
10. 理解Vehicle、Dynamics、Sensor和Backend
11. 跑通Python控制器悬停
12. 跑通PX4MavlinkBackend
13. 验证lockstep和电机命令数据流
14. 创建Sunray-150简化USD
15. 替换质量、惯量和旋翼参数
16. 添加MID360安装位姿
17. 建立基础Isaac Lab悬停任务
18. 建立风扰和电机退化随机化
19. 比较Pegasus、Gazebo和MuJoCo的同一控制器结果
20. 建立版本兼容矩阵
21. 写Isaac-Pegasus REVIEW.md
```

最小成功标准：

```text
Sunray-150简化模型：
    能在Isaac Sim中加载
    能由Pegasus动力学驱动
    能由Python控制器悬停
    能接PX4 SITL

ROS2：
    能获得状态和基础传感器

Isaac Lab：
    能批量创建悬停环境
    能随机质量、风和电机效率
    能完成一个基础策略训练

数据：
    能生成RGB、Depth或LiDAR
    能导出训练数据
```

---

# 12.20 REVIEW.md建议结构

```text
1. 项目定位
    Isaac Sim：
        OpenUSD + GPU物理 + RTX传感器机器人仿真平台

    Isaac Lab：
        大规模机器人学习和sim-to-real框架

    Pegasus：
        Isaac Sim上的多旋翼和PX4扩展

2. 它们解决什么问题
    高保真机器人场景
    GPU物理
    传感器
    合成数据
    多环境RL
    无人机动力学
    PX4仿真

3. 它们不直接解决什么问题
    完整MID360设备模型
    Gazebo轻量工程生态
    平台无关模型格式
    UE现成地图直接复用
    所有硬件平台兼容

4. 核心设计
    OpenUSD
    Extension
    OmniGraph
    PhysX/Newton
    RTX Sensors
    Replicator
    Manager-Based Environment
    Pegasus Backend

5. 我们吸收什么
    USD分层资产
    插件机制
    统一Backend
    Manager任务架构
    多频率仿真
    批量环境
    合成数据
    PX4 Lockstep

6. 是否进入主干
    Gazebo仍是第一工程主干
    Isaac/Pegasus作为重要高保真与RL后端

7. 风险
    NVIDIA GPU依赖
    版本强绑定
    Omniverse Kit再分发许可
    运行环境复杂
    资源消耗大
    MID360仍需自建
    多后端参数一致性

8. 第一阶段用途
    PX4多旋翼高保真验证
    RTX传感器
    基础RL
    合成视觉数据

9. 长期用途
    多模态强化学习
    sim-to-real
    合成数据集
    多无人机
    高保真传感器验证
```

---

# 12.21 最终判断

```text
是否进入长期项目：
    是

是否替代当前主干：
    否

进入哪一层：
    高保真GPU仿真后端
    无人机PX4验证后端
    强化学习训练后端
    合成数据后端

主要吸收：
    OpenUSD资产分层
    Extension架构
    OmniGraph
    PhysX/Newton多物理后端
    RTX传感器
    Replicator
    Isaac Lab Manager架构
    Pegasus Backend
    PX4 Lockstep
    多环境训练

不承担：
    当前唯一工程后端
    唯一场景格式
    唯一渲染方案
    默认MID360真值模型
    所有设备的低成本复现
```

一句话：

> **Isaac Sim提供OpenUSD、GPU物理、RTX传感器和合成数据；Isaac Lab把这些能力组织成可批量训练的机器人学习环境；Pegasus再补上多旋翼动力学和PX4接口。它们非常适合成为我们的高保真无人机与强化学习分支，但由于NVIDIA生态依赖、版本绑定和运行成本，当前仍不应替代ROS2 + Gazebo + PX4的开放工程主线。**
>
