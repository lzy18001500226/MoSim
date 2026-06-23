# 5. 项目概述：Cosys-AirSim

## 5.1 定位

Cosys-AirSim 是经典 Microsoft AirSim 的社区增强分支，核心目标不是彻底重写 AirSim，而是：

> **在保留 AirSim 原有 UE 仿真架构、车辆 API 和飞控接口的基础上，继续维护 UE5 兼容性，并扩展更多传感器、车辆类型和工业场景能力。**

它基于 Microsoft AirSim 最后公开版本继续开发，使用与原项目相同的 MIT 许可证；官方仓库和文档显示，它提供 Unreal Engine 5 支持，并继续扩展传感器类型、车辆和外部 API。([Cosys-Lab](https://cosys-lab.github.io/Cosys-AirSim/?utm_source=chatgpt.com "Home - Cosys-AirSim"))

对我们来说，Cosys-AirSim 的定位不是：

```text
长期项目的唯一仿真主干
```

而是：

```text
UE5 高真实感前端的重点参考实现
视觉/雷达/特殊传感器仿真的候选组件
经典 AirSim 的可维护替代分支
```

它比经典 AirSim 更值得实际试用，因为经典 AirSim 已经进入归档/社区维护阶段，而 Cosys-AirSim 仍在维护 UE5 版本和发布版本。微软研究页面也明确说明，经典开源 AirSim 项目已完成其研究使命并进入归档阶段。([Microsoft](https://www.microsoft.com/en-us/research/project/airsim-high-fidelity-visual-and-physical-simulation-for-autonomous-vehicles/overview/?utm_source=chatgpt.com "Aerial Informatics and Robotics Platform - Microsoft Research"))

---

## 5.2 核心设计理念

| 设计原则         | 说明                                                       |
| ---------------- | ---------------------------------------------------------- |
| 延续 AirSim 架构 | 保留 AirLib、UE 插件、车辆 API、传感器配置和外部客户端模式 |
| UE5 现代化       | 将经典 AirSim 从 UE4 时代迁移到 UE5 生态                   |
| 传感器扩展优先   | 增加新的传感器模态，服务 SLAM、导航和工业检测              |
| 工业应用导向     | 不只考虑无人机演示，也考虑机器人、车辆、船舶和复杂环境     |
| 开源延续         | 在 AirSim 停止主要维护后，由社区继续演进                   |
| 配置驱动         | 延续 settings 配置方式，减少修改核心代码的需要             |
| 多 API 入口      | 提供 Python、ROS/ROS2、MATLAB 等接口版本或配套客户端       |
| 高保真实时仿真   | 继续利用 Unreal 的场景、材质、光照和渲染能力               |

Cosys-AirSim 的论文将其定位为一个扩展后的实时开源仿真框架，重点补充新的传感器模态、车辆类型、可变化环境和复杂工业应用，并用于 SLAM、自主导航和迁移学习。([arXiv](https://arxiv.org/abs/2303.13381?utm_source=chatgpt.com "Cosys-AirSim: A Real-Time Simulation Framework Expanded for Complex Industrial Applications"))

---

# 5.3 系统设计逻辑

## 5.3.1 第一性原理：为什么不从零重写，而要基于 AirSim 分叉？

经典 AirSim 已经解决了非常昂贵的基础问题：

```text
UE 插件怎么组织
车辆状态如何进入 UE Actor
PX4/MAVLink 如何接入
Python/C++ API 如何暴露
相机、深度、分割和 LiDAR 如何生成
仿真时钟如何管理
settings.json 如何配置车辆和传感器
```

如果从零重写，首先需要投入大量时间重复这些基础设施。

Cosys-AirSim 的选择是：

```text
继承 AirSim 已验证架构
        ↓
修复 UE 新版本兼容问题
        ↓
扩展传感器和车辆
        ↓
服务更复杂的工业需求
```

这是一种典型的开源演进策略：

> **保留稳定核心，针对原项目停止维护和功能不足的部分持续扩展。**

这对我们也有启发。我们没有必要重新实现完整的 UE 传感器插件框架，可以优先研究 Cosys-AirSim 已经做好的部分，再决定直接复用、裁剪还是重新封装。

---

## 5.3.2 第二性原理：为什么它强调传感器扩展？

对于普通演示，RGB 相机和一个无人机模型就够了。

但真实自主系统需要更多传感器：

```text
RGB camera
depth camera
segmentation
LiDAR
radar
IMU
GPS
distance sensor
特殊工业传感器
```

不同算法需要完全不同的数据模型：

```text
视觉定位：
    RGB + depth

SLAM：
    LiDAR + IMU

目标识别：
    RGB + segmentation

低能见度环境：
    radar

工业检测：
    特定距离、反射或回波传感器
```

Cosys-AirSim 的核心扩展方向正是让传感器成为可插拔模块，而不是仅限经典 AirSim 内置的几类传感器。论文也明确将新传感器模态、SLAM、自主导航和机器学习应用作为扩展重点。([arXiv](https://arxiv.org/abs/2303.13381?utm_source=chatgpt.com "Cosys-AirSim: A Real-Time Simulation Framework Expanded for Complex Industrial Applications"))

对我们来说，这一思路可以转化为：

```text
UE 前端不是只负责好看
UE 前端还可以成为高真实感感知数据源
```

但要分阶段：

```text
第一阶段：
    UE 只显示

第二阶段：
    UE 输出 RGB / Depth / Segmentation

第三阶段：
    再研究 UE LiDAR / Radar / 特殊传感器
```

---

## 5.3.3 第三性原理：为什么需要 UE5，而不是一直停留在 UE4？

经典 AirSim 主要建立在 UE4 时代。随着地图资产、渲染管线和插件生态向 UE5 迁移，继续停留在旧版本会带来：

```text
新地图无法直接使用
插件难维护
构建工具链老化
新渲染能力无法利用
与当前 Unreal 生态脱节
```

Cosys-AirSim 的官方仓库提供 UE5 版本，并特别提供 UE 5.2.1 长期支持构建；其下载页面也提供更新版本 UE 插件。([GitHub](https://github.com/Cosys-Lab/Cosys-AirSim?utm_source=chatgpt.com "GitHub - Cosys-Lab/Cosys-AirSim: AirSim is a simulator for drones, cars and more, built on Unreal Engine. We expand it with new implementations and sensor modalities. · GitHub"))

这对我们很重要，因为我们关注的正是：

```text
现成 UE 地图
高质量材质
真实光照
大规模城市/厂区/森林场景
```

所以从 UE 前端参考价值看：

```text
经典 AirSim：
    看架构

Cosys-AirSim：
    看现代 UE5 落地
```

---

# 5.4 Cosys-AirSim 的整体架构

它仍然沿用 AirSim 的基本分层：

```text
┌────────────────────────────────────────────┐
│               Unreal Engine 5              │
│ 地图 / 材质 / Actor / 光照 / 相机 / UI      │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│             Cosys-AirSim Plugin            │
│ 车辆 / 传感器 / API / 碰撞 / 时钟 / 配置    │
└──────────────┬───────────────┬─────────────┘
               │               │
        内置车辆/飞控       PX4 / 外部飞控
               │               │
               └───────┬───────┘
                       │
             Python / ROS2 / MATLAB API
                       │
                外部算法和数据采集
```

它和经典 AirSim 的区别主要在：

```text
核心骨架相近
但 UE 版本、传感器、车辆和应用范围继续扩展
```

---

# 5.5 对我们最有价值的模块

## 5.5.1 UE5 插件迁移经验

我们后续如果自己做 UE 前端，最麻烦的不是“让飞机动”，而是：

```text
插件如何编译
UE 版本怎么管理
核心库如何和 UE 模块隔离
第三方依赖怎么链接
蓝图和 C++ 如何交互
打包版本如何发布
```

Cosys-AirSim 已经处理了大量 UE5 迁移问题。

我们应该重点看：

```text
Build.cs
Target.cs
plugin descriptor
AirLib 与 UE 模块边界
传感器 Actor 生命周期
UE Tick 与仿真时钟关系
打包和发布结构
```

这个价值甚至可能比直接使用它的飞行动力学还高。

---

## 5.5.2 传感器基类和扩展机制

我们要研究：

```text
传感器如何注册
传感器配置如何读取
更新频率如何设置
噪声如何加入
数据如何序列化
Python/ROS2 如何获取数据
传感器与车辆坐标如何绑定
```

长期项目里应该抽象出类似结构：

```text
SensorBase
    initialize()
    update(sim_time)
    reset()
    get_output()
    set_noise_model()
```

具体实现：

```text
RgbCameraSensor
DepthCameraSensor
SegmentationSensor
LidarSensor
RadarSensor
ImuSensor
GpsSensor
```

---

## 5.5.3 多车辆类型

Cosys-AirSim 的定位已经不只限于无人机和汽车，官方介绍还强调可支持更多机器人和自主载具类型。([Cosys-Airsim](https://cosys-airsim.com/?utm_source=chatgpt.com "Home - Cosys-Airsim"))

虽然我们第一阶段只做云纵四旋翼，但长期架构可以吸收它的思想：

```text
VehicleBase
    pose
    velocity
    sensors
    control interface
    reset
    update
```

然后：

```text
QuadrotorVehicle
FixedWingVehicle
GroundVehicle
BoatVehicle
```

但当前只实现：

```text
Sunray150Vehicle
```

不要一开始就铺太多机型。

---

## 5.5.4 多客户端 API

Cosys-AirSim 发布说明和文档提到，配套提供 ROS/ROS2、Python 和 MATLAB API 客户端。([Cosys-Lab](https://cosys-lab.github.io/Cosys-AirSim/run_packaged/?utm_source=chatgpt.com "Download and run - Cosys-AirSim"))

这说明平台不应该只支持一种调用方式。

我们长期项目可以定义：

```text
ROS2 API：
    工程机器人主接口

Python API：
    强化学习、自动化实验、数据采集

C++ API：
    高频算法、底层扩展

UDP/WebSocket：
    UE 状态同步和外部可视化
```

MATLAB API 不应成为必须依赖，只作为可选兼容层。

---

# 5.6 Cosys-AirSim 与经典 AirSim 的区别

| 维度             | 经典 AirSim             | Cosys-AirSim        |
| ---------------- | ----------------------- | ------------------- |
| 来源             | Microsoft Research      | Cosys-Lab 社区分支  |
| 当前状态         | 已归档/社区维护         | 仍有社区维护和发布  |
| Unreal 版本      | 以 UE4 为主             | 重点支持 UE5        |
| 许可证           | MIT                     | 延续 MIT            |
| 传感器           | 基础相机、LiDAR、IMU 等 | 扩展更多传感器模态  |
| 车辆             | 无人机、汽车为主        | 扩展更多车辆/机器人 |
| 工业应用         | 研究原型为主            | 更强调复杂工业应用  |
| ROS2             | 有扩展/Wrapper          | 提供配套 ROS2 API   |
| 是否值得实际试跑 | 架构研究价值高          | 更适合实际 UE5 验证 |

所以我们不应该把它们当成两个完全独立的项目，而应该理解为：

```text
AirSim = 原始架构母体
Cosys-AirSim = 面向 UE5 和复杂传感器的社区延续
```

---

# 5.7 Cosys-AirSim 与 Project AirSim 的区别

这两个项目虽然都在“延续 AirSim”，但路线不同。

## Cosys-AirSim

```text
思路：
    保持经典 AirSim 架构和 API 习惯
    持续修复、迁移和增加功能

特点：
    对老 AirSim 用户迁移较自然
    UE5 支持
    传感器和车辆扩展
    更像持续维护的增强 fork
```

## Project AirSim

```text
思路：
    重新设计新一代自主系统仿真平台
    不追求经典 AirSim API 严格兼容

特点：
    更强调配置、服务、平台化
    架构变化更大
    不等于旧 AirSim 的直接升级版
```

Project AirSim 文档明确说明，它不把严格保持经典 AirSim API 向后兼容作为目标。([IAmAISim](https://iamaisim.github.io/ProjectAirSim/api.html?utm_source=chatgpt.com "API Overview — Project Airsim 0.1 documentation"))

因此：

```text
想复用经典 AirSim 经验：
    重点研究 Cosys-AirSim

想研究下一代平台架构：
    重点研究 Project AirSim
```

---

# 5.8 Cosys-AirSim 对我们“双世界架构”的价值

我们现在设计的是：

```text
Gazebo：
    物理和传感器真值

UE：
    高保真显示

ROS2：
    系统总线

PX4：
    飞控
```

Cosys-AirSim 可以有三种使用方式。

## 方式一：只作为源码参考

这是最稳的。

```text
我们自己做 UE Bridge
但参考 Cosys-AirSim 的：
    UE5 插件
    车辆 Actor
    相机
    传感器
    Python/ROS2 API
```

优点：

```text
架构完全由我们控制
不会被 AirSim API 绑死
Gazebo 仍是唯一真值
```

## 方式二：作为 UE 高保真显示前端

```text
Gazebo/PX4 状态
        ↓
ROS2/UDP
        ↓
Cosys-AirSim/UE 中车辆 Actor
```

此时禁用或忽略 Cosys-AirSim 自己的车辆物理，仅使用其：

```text
UE 地图
车辆模型
相机
UI
部分传感器
```

但需要做较深修改，因为它原本假设自身参与车辆仿真。

## 方式三：作为独立视觉仿真分支

```text
Gazebo 分支：
    机器人真值、LiDAR、PX4、规划验证

Cosys-AirSim 分支：
    高真实感视觉、数据集、目标检测、语义分割
```

两个分支不强制同时运行，只共享：

```text
云纵模型
场景坐标
任务轨迹
传感器配置
```

这是后期可能更容易维护的方式。

---

# 5.9 我们应该吸收的设计

## 吸收一：社区接管停更项目的方法

Cosys-AirSim 表明，当上游停止维护后，可以：

```text
冻结稳定核心
维护新引擎版本
增加兼容层
扩展传感器
发布预编译版本
维护独立文档
```

长期项目也要避免完全依赖单一上游。

---

## 吸收二：引擎适配层隔离

核心仿真逻辑不要写死在 UE 里。

应该分成：

```text
core/
    平台无关数据结构、API、时间、传感器定义

adapters/
    gazebo/
    unreal/
    mujoco/
    genesis/
```

这样以后换 UE 或增加 Godot，不会重写整个系统。

---

## 吸收三：传感器注册机制

传感器应由配置实例化：

```text
sensors:
  - type: rgb_camera
    name: front_camera
    pose: [...]
    update_rate: 30

  - type: lidar
    name: mid360
    pose: [...]
    update_rate: 10
```

而不是写死：

```text
if vehicle == drone:
    create camera
    create lidar
```

---

## 吸收四：多语言客户端

核心运行时与使用接口分离：

```text
服务器：
    C++/UE/Gazebo

客户端：
    ROS2
    Python
    C++
```

强化学习尤其需要 Python 客户端，但工程主链仍然用 ROS2。

---

## 吸收五：预编译发布

长期项目如果想形成生态，不能要求所有用户都从源码编译 UE 插件。

应逐渐提供：

```text
源码版
Docker/环境配置
预编译仿真后端
预打包 UE 场景
示例项目
```

Cosys-AirSim 提供预构建下载和版本化插件，这一点值得学习。([Cosys-Airsim](https://cosys-airsim.com/download/?utm_source=chatgpt.com "Download - Cosys-Airsim"))

---

# 5.10 不应该照搬的地方

## 不照搬一：不要继续把经典 AirSim API 当永久标准

经典 API 有历史包袱。

我们应该吸收它的功能，但重新定义更适合自己的统一 API：

```text
SimulationAPI
VehicleAPI
SensorAPI
WorldAPI
ExperimentAPI
```

---

## 不照搬二：不要让 UE 同时成为物理权威

如果我们保留 Gazebo 主干：

```text
Gazebo = 物理权威
UE/Cosys-AirSim = 显示或视觉权威
```

不要让两边同时决定位姿。

---

## 不照搬三：不要把全部传感器都迁到 UE

适合 UE 的：

```text
RGB
Depth
Segmentation
Optical Flow
视觉相关传感器
```

更适合 Gazebo/专用模型的：

```text
IMU
基础 LiDAR
接触
碰撞
动力学相关传感器
```

雷达、复杂 LiDAR 可以按真实性要求单独评估。

---

## 不照搬四：不要被 UE 版本追着跑

UE 版本升级会带来：

```text
插件 API 变化
构建工具变化
依赖变化
地图资产兼容变化
```

长期项目应固定一个稳定版本作为 LTS 基线，不要每个 UE 新版本都立即升级。

Cosys-AirSim 当前专门保留 UE 5.2.1 长期支持版本，正说明版本稳定性是重要工程问题。([GitHub](https://github.com/Cosys-Lab/Cosys-AirSim?utm_source=chatgpt.com "GitHub - Cosys-Lab/Cosys-AirSim: AirSim is a simulator for drones, cars and more, built on Unreal Engine. We expand it with new implementations and sensor modalities. · GitHub"))

---

# 5.11 最小研究任务

针对 Cosys-AirSim，建议完成：

```text
1. 编译或运行一个官方 UE5 示例环境
2. 理清它和经典 AirSim 的目录差异
3. 理清 UE5 Plugin 的 Build.cs 和依赖
4. 找到车辆 Actor 与 AirLib 状态同步路径
5. 找到传感器注册和工厂机制
6. 跑通 RGB、Depth、Segmentation、LiDAR 中至少两类
7. 调用 Python API 读取状态和图像
8. 调研 ROS2 API 结构
9. 测试外部位姿驱动车辆 Actor 是否可行
10. 写 Cosys-AirSim REVIEW.md
```

第一阶段不需要接 PX4，也不需要和 Gazebo 同时运行。先验证：

```text
它能不能作为我们的 UE5 前端参考？
它的传感器层是否值得复用？
它的 API 是否容易裁剪？
```

---

# 5.12 REVIEW.md 建议结构

```text
1. 项目定位
    AirSim 的 UE5 社区增强分支

2. 它解决什么问题
    经典 AirSim 停更、UE5 迁移、传感器扩展、工业场景支持

3. 它不解决什么问题
    ROS2 全栈、Gazebo 真值同步、统一多后端训练、大规模并行 RL

4. 核心设计
    AirSim 架构延续
    UE5 插件
    传感器扩展
    配置驱动
    多语言 API

5. 我们吸收什么
    UE5 插件组织
    传感器抽象
    外部 API
    预编译发布
    版本管理

6. 是否进入主干
    不作为默认真值后端
    候选 UE 前端技术来源

7. 使用方式
    源码参考 / 视觉传感器分支 / 高保真前端

8. 风险
    UE 版本依赖
    AirSim 历史架构包袱
    双物理世界
    API 与 ROS2 主干不统一

9. 第一阶段任务
    UE5 示例、传感器、外部位姿驱动测试

10. 长期用途
    UE 前端、视觉仿真、数据集生成、sim-to-real
```

---

# 5.13 最终判断

```text
是否进入主干：
    不直接作为默认真值仿真后端

进入哪一层：
    UE5 高保真前端候选
    视觉传感器实现参考
    AirSim 社区延续参考

主要吸收：
    UE5 插件迁移
    AirLib/UE 分层
    传感器扩展
    Python/ROS2 API
    配置驱动
    预编译发布
    工业应用扩展

不承担：
    ROS2 总线
    默认物理真值
    PX4 官方主仿真路线
    高速并行 RL 训练

和 Gazebo 的关系：
    Gazebo 保持物理权威，Cosys-AirSim 可提供高保真视觉前端

和 PX4 的关系：
    可以接 PX4，但不是我们第一阶段接入重点

和 ROS2 的关系：
    可提供 ROS2 API，但应接入我们统一 ROS2 接口，而不是反过来绑架主干

和经典 AirSim 的关系：
    继承并现代化经典 AirSim

和 Project AirSim 的关系：
    一个是延续增强，一个是新架构重构
```

一句话：

> **Cosys-AirSim 最值得我们学习的是：如何在经典 AirSim 停更之后，把它迁移到 UE5、继续扩展传感器，并维持可用的 Python/ROS2 接口。对我们而言，它更像“UE 高保真前端技术库”，而不是替代 Gazebo 的主仿真器。**

下一项建议讲  **Project AirSim** ，因为它与 Cosys-AirSim 的区别非常有价值：一个代表“维护和增强旧架构”，另一个代表“重新设计下一代仿真平台”。
