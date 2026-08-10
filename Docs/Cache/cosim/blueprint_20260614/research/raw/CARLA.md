# 39. 项目概述：CARLA

## 39.1 定位

CARLA 是一套面向自动驾驶研究、训练、验证和数据生成的开源仿真平台。

它的核心目标不是单纯提供一张城市地图，也不是只模拟一辆汽车，而是：

> **在一个包含道路([CARLA Simulator](https://carla.org/2025/09/16/release-0.9.16/?utm_source=chatgpt.com "CARLA 0.9.16 Release - CARLA Simulator"))场景。**

CARLA以Unreal Engine作为世界和渲染运行时，以OpenDRIVE描述道路拓扑，通过Python和C++ API对外提供世界控制、车辆控制、传感器采集与场景管理能力。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/start_introduction/?utm_source=chatgpt.com "Introduction - CARLA Simulator UE5"))A最合理的定位是：

```text
道路交通仿真后端
空地协同场景后端
自动驾驶感知数据生成后端
交通参与者与动态场景后端
```

而不是：

```text
默认无人机动力学后端
默认PX4仿真后端
通用三维机器人世界
无人机规划地图
单纯的UE地图资源库
```

---

# 39.2 当前版本必须先分清

截至  **2026年6月14日** ，CARLA实际上存在两条同时维护的主要技术路线。

## 39.2.1 CARLA 0.9.16

```text
Unreal Engine 4.26
成熟的0.9.x生态线
```

0.9.16于2025年9月发布，是当前UE4.26路线的最新正式版本。它新增了原生ROS2支持、左侧通行、NVIDIA NuRec与Cosmos Transfer集成、USD SimReady导出等能力。([CARLA Simulator](https://carla.org/2025/09/16/release-0.9.16/?utm_source=chatgpt.com "CARLA 0.9.16 Release - CARLA Simulator"))xt
历史功能更完整
地图和附加地图更多
ScenarioRunner等生态更成熟
大量论文和第三方项目基于0.9.x
ROS Bridge、SUMO、Chrono等资料较多

```

---

## 39.2.2 CARLA 0.10.0

```text
Unreal Engine 5.5
新一代UE5路线
```

0.10.0于2024年12月发布，完成了从UE4.26到UE5.5的迁移，引入Nanite、Lumen和Chaos物理，并重制了Town10及部分车辆。官方明确说明，UE4.26和UE5.5两条路线将在一段时间内并行存在，因为部分旧功能和资产尚未全部迁移。([GitHub](https://github.com/carla-simulator/carla/releases "Releases · carla-simulator/carla · GitHub"))xt
UE5.5
Nanite
Lumen
Chaos
更现代的渲染和资产管线
更适合长期UE5开发

```

但当前UE5官方目录中，主要地图只有：

```text
Town10
Mine01
```

说明UE5线在地图数量和部分生态完整度上仍不等于UE4成熟线。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/catalogue/?utm_source=chatgpt.com "Catalogue - CARLA Simulator UE5"))3 两条路线怎么选？

不是简单地：

```text
0.10.0 > 0.9.16
```

而是：

```text
想研究成熟自动驾驶生态：
    优先CARLA 0.9.16

想研究UE5源码、现代渲染和长期集成：
    优先CARLA 0.10.0 / ue5-dev
```

对CoSim来说：

```text
架构研究：
    研究ue5-dev

生态兼容实验：
    保留0.9.16

长期主分支参考：
    UE5

ScenarioRunner/旧项目复现：
    0.9.16
```

---

# 39.3 CARLA 的核心设计理念

| 设计原则          | 说明                                           |
| ----------------- | ---------------------------------------------- |
| 客户端—服务器    | UE服务器运行世界，Python/C++客户端控制实验     |
| Actor统一抽象     | 车辆、行人、传感器、交通灯都视为Actor          |
| Blueprint配置驱动 | 通过Blueprint配置车辆、传感器和Actor属性       |
| 地图双层结构      | UE三维场景负责视觉，OpenDRIVE负责道路逻辑      |
| 传感器即Actor     | 相机、LiDAR、IMU等可动态挂载和销毁             |
| 世界统一时钟      | 车辆、交通和传感器共享仿真帧                   |
| 同步与异步可选    | 支持实时浏览，也支持确定性算法实验             |
| 交通系统独立      | Traffic Manager集中管理大量NPC车辆             |
| 场景可重复        | Recorder、ScenarioRunner、固定随机种子支持复现 |
| 算法外置          | 自动驾驶算法通常运行在CARLA进程之外            |
| 可替换物理        | 默认车辆物理之外，可接Chrono和CarSim           |
| 开放资产与接口    | 提供城市、车辆、行人和开放API                  |

CARLA官方将服务器—客户端、World、Actor、Blueprint、Map和Sensor列为其基础概念。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/core_concepts/?utm_source=chatgpt.com "Core concepts - CARLA Simulator UE5"))统设计逻辑

## 39.4.1 第一性原理：为什么采用服务器—客户端架构？

如果把自动驾驶算法直接写进UE项目，会导致：

```text
算法和UE版本绑定
修改算法需要重编译UE
Python深度学习框架难接
无法轻松切换不同算法
多团队难以并行开发
批量实验不方便
```

CARLA将世界分成：

```text
CARLA Server
    运行UE世界
    处理物理
    生成传感器
    管理Actor

CARLA Client
    通过Python/C++ API连接
    创建车辆
    设置天气
    读取传感器
    控制车辆
```

数据链路是：

```text
Python / C++ Algorithm
        │
        │ 控制命令、场景命令
        ▼
CARLA Server / Unreal Engine
        │
        │ 世界状态、传感器数据
        ▼
Python / C++ Algorithm
```

这样同一个CARLA服务器可以服务于：

```text
手动控制客户端
自动驾驶客户端
数据记录客户端
交通生成客户端
可视化客户端
```

CARLA官方说明，服务器负责运行仿真，客户端负责获取信息并向世界发出修改请求；在多客户端模式中，应由一个主客户端管理同步Tick。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_synchrony_timestep/?utm_source=chatgpt.com "Synchrony and time-step - CARLA Simulator UE5"))2 第二性原理：为什么所有东西都叫Actor？

CARLA中的Actor包括：

```text
Vehicle
Walker
Sensor
Traffic Light
Traffic Sign
Spectator
Static Prop
```

表面上它们完全不同，但都具有共同生命周期：

```text
Blueprint
    ↓
Spawn
    ↓
Update / Control
    ↓
Query
    ↓
Destroy
```

因此CARLA可以统一处理：

```text
world.spawn_actor()
actor.get_transform()
actor.destroy()
```

例如传感器不是某个车辆类中的固定字段，而是可以像普通Actor一样动态创建并挂载到车辆：

```text
Camera Actor
    attach_to
Vehicle Actor
```

这使得传感器组合非常灵活。CARLA官方将车辆、行人、传感器、交通标志和观察者等都统一定义为Actor。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/core_actors/?utm_source=chatgpt.com "Actors - CARLA Simulator UE5"))3 第三性原理：Blueprint为什么重要？

Blueprint可以理解为：

```text
Actor的生产配方
```

车辆Blueprint中可能包含：

```text
车辆Mesh
骨骼
材质
车辆物理参数
颜色选项
轮数
角色名称
```

相机Blueprint中包含：

```text
分辨率
FOV
曝光
畸变
传感器频率
```

LiDAR Blueprint中包含：

```text
通道数
每秒点数
旋转频率
最大距离
上下视场角
噪声参数
```

所以CARLA不是写死：

```text
spawnCamera()
spawnLidar()
```

而是：

```text
找到Blueprint
    ↓
修改属性
    ↓
创建Actor
```

这种方式使得：

```text
代码定义平台能力
Blueprint定义实验配置
```

CARLA的Blueprint Library可按ID或通配符查询Blueprint，并修改颜色、LiDAR通道数、行人速度等可配置属性。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/core_actors/?utm_source=chatgpt.com "Actors - CARLA Simulator UE5"))4 第四性原理：地图为什么必须同时有UE场景和OpenDRIVE？

一个普通UE城市地图只知道：

```text
这里有一条道路Mesh
这里有一栋建筑
```

但自动驾驶算法需要知道：

```text
道路编号是什么？
车道中心线在哪里？
有几条车道？
车道方向是什么？
能不能变道？
哪里是路口？
哪个交通灯管理哪条车道？
```

因此CARLA地图由两层组成：

```text
视觉层
    UE Mesh
    建筑
    道路材质
    地形
    植被

道路逻辑层
    OpenDRIVE
    Road
    Lane
    Junction
    Signal
    Lane Marking
```

CARLA中的Waypoint不是普通三维路径点，而是OpenDRIVE车道上的有方向节点，包含：

```text
road_id
section_id
lane_id
s
lane_width
lane_change
junction
lane_marking
```

CARLA官方明确规定，地图同时包含城市场景的三维模型和基于OpenDRIVE 1.4的道路定义。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/core_map/?utm_source=chatgpt.com "Maps - CARLA Simulator UE5"))5 第五性原理：为什么必须有同步模式？

默认异步模式下：

```text
CARLA Server
    尽可能快地运行

Client
    有空就读取数据
```

如果算法推理很慢：

```text
仿真已经前进10帧
算法才处理完第1帧图像
```

就会出现：

```text
相机帧错位
控制指令滞后
训练数据不同步
实验不可重复
```

同步模式下：

```text
Client发送tick
        ↓
CARLA推进一个固定时间步
        ↓
生成本帧传感器数据
        ↓
Client处理完成
        ↓
再发送下一个tick
```

这样可以保证：

```text
第N帧世界
第N帧相机
第N帧LiDAR
第N帧车辆状态
```

属于同一仿真时刻。

CARLA官方说明，在同步模式中服务器等待客户端Tick后才推进下一帧；多客户端环境中只能由一个客户端负责Tick。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_synchrony_timestep/?utm_source=chatgpt.com "Synchrony and time-step - CARLA Simulator UE5"))ARLA 的整体架构

```text
┌──────────────────────────────────────────────┐
│             Unreal Engine World              │
│                                              │
│  Map / Buildings / Roads / Weather / Light  │
│  Vehicles / Walkers / Props / TrafficLight  │
│  Cameras / LiDAR / Radar / IMU / GNSS       │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│              CARLA Unreal Plugin             │
│                                              │
│ Actor管理 / Sensor生成 / World管理 / Physics │
│ OpenDRIVE / TrafficLight / Recorder          │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│                    LibCarla                  │
│                                              │
│ RPC / Streaming / Client API / Serialization│
│ Traffic Manager / Map / Commands            │
└───────────────┬───────────────────┬──────────┘
                │                   │
                ▼                   ▼
          Python API           C++ Client
                │                   │
                └─────────┬─────────┘
                          ▼
            Autonomous Driving Stack
           ROS2 / Autoware / Python / AI
```

另外还有相对独立的：

```text
Traffic Manager
ScenarioRunner
Recorder
ROS2 Native
ROS Bridge
SUMO Co-simulation
Chrono / CarSim
```

---

# 39.6 World、Map、Actor之间是什么关系？

这三个概念很容易混淆。

## 39.6.1 World

World表示当前正在运行的整个仿真世界。

它包含：

```text
当前地图
当前天气
所有Actor
当前时间
世界设置
调试绘图
```

一个仿真时刻只存在一个当前World。

加载新地图时：

```text
旧World销毁
    ↓
创建新World
```

---

## 39.6.2 Map

Map主要描述：

```text
当前城市场景
道路拓扑
车道和路口
出生点
OpenDRIVE信息
```

它偏向静态结构。

---

## 39.6.3 Actor

Actor是World中可创建、销毁或变化的对象：

```text
车辆
行人
传感器
交通灯
道具
```

关系可以理解为：

```text
World
├─ Map
├─ Weather
└─ Actors
   ├─ Vehicle
   ├─ Walker
   ├─ Sensor
   └─ Traffic Light
```

CARLA的World负责访问地图、天气、车辆、建筑和交通灯等仿真对象；更换地图会重新创建World。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/core_concepts/?utm_source=chatgpt.com "Core concepts - CARLA Simulator UE5"))辆系统

## 39.7.1 车辆控制输入

CARLA默认车辆控制为：

```text
throttle
steer
brake
hand_brake
reverse
gear
manual_gear_shift
```

这与无人机位置轨迹接口完全不同。

CARLA处理的是：

```text
驾驶层输入
```

而不是：

```text
四个车轮的独立电机电压
```

典型链路：

```text
Autonomous Planner
    ↓
Throttle / Steering / Brake
    ↓
CARLA Vehicle
    ↓
Vehicle Physics
    ↓
Vehicle State
```

---

## 39.7.2 车辆物理参数

`VehiclePhysicsControl`允许调整：

```text
质量
阻力系数
重心
转矩曲线
最大转速
变速箱
差速器
轮胎
轮半径
制动
悬架
转向角
```

每个车轮还可以有独立的 `WheelPhysicsControl`。CARLA UE5默认车辆物理已迁移至Chaos；0.9.x UE4路线原本使用PhysX。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/core_actors/?utm_source=chatgpt.com "Actors - CARLA Simulator UE5"))3 为什么CARLA默认车辆物理不是最高精度？

CARLA必须同时运行：

```text
数十辆汽车
大量行人
多个传感器
高分辨率渲染
交通系统
```

因此默认物理需要在：

```text
精度
实时性
并发数量
```

之间折中。

如果只测试一辆高保真车辆，可以接：

```text
CarSim
Project Chrono
```

CARLA的Chrono集成允许单辆车使用Chrono模板计算车辆、轮胎和动力总成，但官方当前说明其碰撞处理有限，发生碰撞时会回退到CARLA默认物理。([CARLA Simulator](https://carla.readthedocs.io/en/0.9.16/tuto_G_chrono/?utm_source=chatgpt.com "Chrono - CARLA Simulator"))ext
大量NPC：
CARLA默认物理或Hybrid模式

Ego Vehicle：
Chaos高精度参数
或Chrono / CarSim

```

---

# 39.8 传感器系统

CARLA传感器本身也是Actor。

典型使用过程：

```text
获取传感器Blueprint
        ↓
设置参数
        ↓
挂载到车辆
        ↓
注册回调
        ↓
接收SensorData
```

CARLA当前支持的主要传感器包括：

```text
RGB Camera
Depth Camera
Semantic Segmentation Camera
Instance Segmentation Camera
Optical Flow Camera
DVS Event Camera

LiDAR
Semantic LiDAR
Radar

IMU
GNSS

Collision Detector
Lane Invasion Detector
Obstacle Detector
```

([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/ref_sensors/?utm_source=chatgpt.com "Sensors reference - CARLA Simulator UE5"))1 相机

相机是CARLA最强的能力之一。

可以输出：

```text
RGB
深度
语义标签
实例标签
光流
事件流
```

这对：

```text
目标检测
语义分割
深度估计
视觉里程计
自动驾驶感知
数据集生成
```

非常有价值。

CARLA的视觉传感器来自UE渲染世界，因此它的优势不是物理测量本身，而是：

```text
同一世界
    ↓
同时生成多种像素级对齐标签
```

---

## 39.8.2 LiDAR

CARLA内置的是可配置旋转式LiDAR模型，可设置：

```text
channels
range
points_per_second
rotation_frequency
upper_fov
lower_fov
noise
```

输出通常包含：

```text
x
y
z
intensity
```

Semantic LiDAR还可以输出：

```text
object index
semantic tag
```

但它不是直接模拟Livox MID360的非重复扫描模式。

因此：

```text
CARLA内置LiDAR：
    适合汽车旋转式激光雷达

MID360：
    需要自定义扫描模型或插件
```

CARLA官方传感器参考将其LiDAR定义为旋转LiDAR，并提供通道、旋转与视场参数。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/ref_sensors/?utm_source=chatgpt.com "Sensors reference - CARLA Simulator UE5"))3 坐标系

CARLA和UE使用：

```text
X forward
Y right
Z up
左手坐标系
```

ROS常见：

```text
X forward
Y left
Z up
右手坐标系
```

因此点云、姿态和角度不能直接复制。

尤其需要注意：

```text
CARLA Rotation：
    pitch, yaw, roll

UE Editor显示：
    roll, pitch, yaw
```

CARLA官方特别警告，其Python API使用UE的Z-up左手坐标系，且旋转声明顺序与UE编辑器显示顺序不同。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/python_api/?utm_source=chatgpt.com "Python API - CARLA Simulator UE5"))raffic Manager

## 39.9.1 它是什么？

Traffic Manager负责控制设置为Autopilot的NPC车辆。

它的目标不是控制Ego Vehicle，而是：

```text
快速生成大量背景交通
```

例如：

```text
50辆普通汽车
10辆慢车
若干激进车辆
随机变道车辆
不遵守交通灯车辆
```

这些车辆共同构成自动驾驶测试环境。

---

## 39.9.2 Traffic Manager内部流程

Traffic Manager的控制循环主要包括：

```text
Localization Stage
    确定车辆当前道路和未来路径

Collision Stage
    预测与其他车辆、行人的冲突

Traffic Light Stage
    处理交通灯和路权

Motion Planner Stage
    生成速度和控制指令

Vehicle Lights Stage
    控制灯光
```

各阶段之间通过同步屏障保证同一帧中所有车辆完成一个阶段后，再进入下一阶段。最终指令以Batch方式发送给CARLA服务器。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_traffic_manager/?utm_source=chatgpt.com "Traffic Manager - CARLA Simulator UE5"))3 为什么Traffic Manager运行在客户端侧？

如果每辆NPC都频繁调用服务器查询：

```text
当前位置
其他车辆位置
交通灯
道路信息
```

网络开销会很大。

Traffic Manager将世界状态缓存到客户端内存中：

```text
Simulation State Cache
```

然后在本地并行计算大量车辆命令，最后一次性Batch提交。

这是一个非常值得CoSim学习的设计：

> **大量Agent的决策应尽量本地批处理，避免每个Agent反复跨进程查询世界。**

---

## 39.9.4 Hybrid Physics Mode

大量NPC全部开启完整物理，会消耗大量CPU。

Hybrid模式会：

```text
Ego附近车辆：
    正常物理

远处车辆：
    关闭大部分物理
    直接移动或近似更新
```

默认以标记为 `hero`的车辆为中心设置物理启用半径。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_traffic_manager/?utm_source=chatgpt.com "Traffic Manager - CARLA Simulator UE5"))warm中的：

```text
fake drone
完整动力学无人机
```

是同一种多保真思想。

---

## 39.9.5 Traffic Manager不是什么？

它不是高级自动驾驶算法。

它主要用于：

```text
生成看起来合理的NPC交通
```

而不是：

```text
研究最先进的预测规划
研究端到端自动驾驶
严格模拟真实驾驶员
```

它也不是SUMO。

```text
Traffic Manager：
    面向CARLA世界内部NPC控制

SUMO：
    专门的大规模交通流仿真器
```

---

# 39.10 行人系统

CARLA行人由：

```text
Walker Actor
+
Walker Controller
```

组成。

行人可以：

```text
随机行走
前往指定位置
设置最大速度
穿过道路
受交通环境影响
```

但CARLA行人行为主要用于生成交通参与者和感知目标，并不是完整的人群社会行为模拟。

对空地协同而言，行人系统可以用于：

```text
无人机搜救
人群检测
道路事故场景
低空配送避人
跨视角行人跟踪
```

---

# 39.11 ScenarioRunner

## 39.11.1 它解决什么问题？

直接写Python控制所有场景会变成：

```text
生成车辆A
等待5秒
让车辆B变道
检测碰撞
记录结果
销毁所有Actor
```

每个测试都要写大量重复代码。

ScenarioRunner将场景抽象成：

```text
初始条件
触发条件
参与者行为
结束条件
评估指标
```

例如：

```text
Ego车辆接近路口
        ↓
侧方车辆突然闯入
        ↓
检查Ego是否刹停
        ↓
判断是否碰撞
```

ScenarioRunner是CARLA官方维护的独立交通场景定义与执行引擎，当前0.9.x生态有对应0.9.16发布。([GitHub](https://github.com/carla-simulator/scenario_runner?utm_source=chatgpt.com "GitHub - carla-simulator/scenario_runner: Traffic scenario definition and execution engine · GitHub")).2 ScenarioRunner 与 Traffic Manager 的关系

```text
Traffic Manager：
    生成普通背景交通

ScenarioRunner：
    安排关键事件和危险场景
```

组合使用：

```text
Traffic Manager
    生成40辆背景车

ScenarioRunner
    控制一辆目标车辆突然切入

Ego Algorithm
    接受测试
```

---

## 39.11.3 ScenarioRunner 与UE5的关系

当前ScenarioRunner正式发布和大量资料主要围绕CARLA 0.9.x版本。

因此不能简单假定：

```text
ScenarioRunner 0.9.16
    直接兼容CARLA 0.10.0
```

接UE5版本时需要单独核对对应分支、API差异和场景支持状态。

---

# 39.12 Scenic

Scenic是一种用于概率化场景描述和场景生成的语言。

传统场景写法：

```text
把车A放在坐标(100, 20)
把车B放在坐标(120, 20)
```

Scenic更接近：

```text
在Ego前方20到30米
随机生成一辆慢车

在相邻车道
随机生成一辆可能切入的车辆

天气随机
光照随机
车辆颜色随机
```

同一个Scenic描述可以生成许多不同但符合约束的场景。CARLA官方文档提供了Scenic与ScenarioRunner的集成方式，用于从单个场景定义生成大量多样化场景。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/tuto_G_scenic/?utm_source=chatgpt.com "Scenic - CARLA Simulator UE5"))```text
Scenario不是一个固定文件
Scenario可以是概率分布

```

---

# 39.13 Recorder

CARLA Recorder可以记录一次仿真中的Actor状态和事件，并在之后重放。

它适合：

```text
事故复盘
算法失败分析
重放相同交通过程
更换传感器配置重新观察
查询碰撞和阻塞事件
```

Recorder由客户端启动，但记录文件保存在服务器侧。重放时，CARLA根据记录恢复或移动Actor。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_recorder/?utm_source=chatgpt.com "Recorder - CARLA Simulator UE5"))t
Recorder
记录世界和Actor演化

Dataset Recorder
保存RGB、Depth、LiDAR等原始数据

```

这两者不是一回事。

如果要训练神经网络，仍然需要单独保存：

```text
camera frames
point clouds
labels
calibration
timestamps
ego state
```

---

# 39.14 ROS2接口

CARLA目前有两类ROS接入方式。

## 39.14.1 传统ROS Bridge

```text
CARLA Server
    ↓ CARLA API
ROS Bridge进程
    ↓ ROS Topics
ROS1 / ROS2算法
```

优点：

```text
功能历史较完整
与已有ROS工具兼容
可控制仿真暂停、播放和同步
```

缺点：

```text
多一层进程
消息转换增加延迟
配置较复杂
```

传统ROS Bridge支持相机、LiDAR、Semantic LiDAR、GNSS、Radar、IMU以及车辆控制和交通灯等消息。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/ros_documentation/?utm_source=chatgpt.com "ROS Bridge - CARLA Simulator UE5")).2 Native ROS2

新版本CARLA可以直接在服务器内部发布ROS2消息。

启动时启用：

```text
CARLA Server --ros2
```

然后对传感器调用：

```text
sensor.enable_for_ros()
```

CARLA服务器可直接发布：

```text
/clock
sensor_msgs/Image
sensor_msgs/PointCloud2
sensor_msgs/Imu
sensor_msgs/NavSatFix
```

并订阅Ego Vehicle控制消息。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/ros2_native/?utm_source=chatgpt.com "ROS2 - CARLA Simulator UE5"))t
CARLA Server
├─ UE World
├─ Sensor
└─ Native DDS / ROS2
│
▼
ROS2 Algorithm

```

优点：

```text
减少Bridge层
延迟更低
时钟更直接
```

但它的当前控制消息仍然是汽车语义：

```text
throttle
steer
brake
gear
```

不是无人机控制接口。

---

## 39.14.3 对CoSim意味着什么？

CoSim不要直接把CARLA原生话题作为平台唯一标准。

应设计：

```text
CARLA Adapter
    ↓
CoSim UnifiedVehicleState
CoSim UnifiedSensorData
CoSim Scenario API
```

这样以后：

```text
CARLA
Gazebo
MuJoCo
JSBSim
```

都能接入统一接口。

---

# 39.15 地图系统

## 39.15.1 CARLA地图的完整组成

一个真正可工作的CARLA地图至少包含：

```text
UE Level
├─ 地形
├─ 道路Mesh
├─ 建筑
├─ 植被
├─ 材质
├─ 碰撞
├─ 交通灯Actor
└─ 道路设施

OpenDRIVE
├─ Roads
├─ Lanes
├─ Junctions
├─ Signals
├─ Lane Markings
└─ Georeference
```

仅有UE场景不够，因为Traffic Manager无法理解道路。

仅有OpenDRIVE也不够，因为画面可能只是一条自动生成的简陋道路Mesh。

---

## 39.15.2 OSM转CARLA为什么画面一般？

CARLA可以：

```text
OpenStreetMap .osm
    ↓
转换成OpenDRIVE .xodr
    ↓
CARLA生成道路世界
```

官方支持直接使用OSM或先将其转换为OpenDRIVE，并通过 `generate_opendrive_world()`生成道路Mesh。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/tuto_G_openstreetmap/?utm_source=chatgpt.com "Generate maps with OpenStreetMap - CARLA Simulator UE5"))`text
道路中心线
道路类型
部分路口
部分交通灯
地理信息

```

它通常不包含：

```text
高质量建筑Mesh
PBR材质
窗户细节
植被模型
城市家具
真实立面
```

因此可以推断：

> **OSM更适合生成“道路拓扑正确的仿真骨架”，而不是自动生成高质量UE城市。**

这正是你之前认为“还是用UE官方免费地图更有用”的根本原因。

---

## 39.15.3 自定义CARLA地图的真实工作量

流程一般包括：

```text
建立或导入道路
        ↓
生成OpenDRIVE
        ↓
制作道路Mesh
        ↓
制作建筑和地形
        ↓
设置碰撞
        ↓
设置语义标签
        ↓
放置交通灯与标志
        ↓
检查OpenDRIVE与视觉道路对齐
        ↓
导入CARLA
```

CARLA UE5提供自定义地图、道路绘制、建筑、地图包和源地图导入教程。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/maps_tutorials/?utm_source=chatgpt.com "Custom maps - CARLA Simulator UE5"))text
把FBX拖进UE

```

而是保证：

```text
道路Mesh
车道中心线
交通灯
出生点
碰撞
语义
```

全部一致。

---

# 39.16 CARLA地图与UE官方免费地图的关系

## 39.16.1 直接把City Sample放进CARLA行不行？

理论上可以迁移视觉资产，但不等于直接可用。

City Sample只有视觉世界时：

```text
CARLA车辆看到一条路
```

但Traffic Manager可能不知道：

```text
道路在哪里
车道怎么走
路口怎么连接
交通灯控制什么
```

还需要重新制作：

```text
OpenDRIVE
交通灯映射
道路语义
CARLA语义标签
Spawn Points
```

所以：

```text
UE免费地图
    ≠
CARLA地图
```

更准确地说：

```text
UE免费地图：
    视觉资产来源

CARLA地图：
    视觉资产 + 道路数字模型 + 交通逻辑
```

---

## 39.16.2 对无人机项目来说为什么可以跳过OpenDRIVE？

如果无人机只需要：

```text
在城市建筑之间飞行
读取RGB、Depth和语义图
```

那么：

```text
道路中心线
变道权限
Traffic Manager
路口拓扑
```

不一定重要。

因此对纯无人机视觉前端：

```text
UE官方地图
    +
自定义无人机Actor
    +
视觉传感器
```

往往比完整CARLA更合理。

只有当你需要：

```text
无人机看车辆
无人机辅助自动驾驶
城市交通动态目标
空地协同
```

CARLA的道路和交通体系才真正值回集成成本。

---

# 39.17 天气和环境系统

CARLA允许通过World设置：

```text
太阳高度
太阳方位
云量
降雨
积水
风
雾
湿度
尘土
```

天气会影响视觉表现，但并不意味着所有参数都会自动影响完整物理。

例如：

```text
视觉上有雨
```

不一定自动等于：

```text
轮胎摩擦真实降低
LiDAR真实雨滴散射
相机镜头积水
```

所以要区分：

```text
Visual Weather
Physical Weather
Sensor Degradation
```

CoSim应将它们拆开：

```text
天气视觉层
车辆物理层
传感器故障层
```

而不是认为调一个 `rain`参数就完成了雨天高保真仿真。

---

# 39.18 确定性与可重复实验

要让实验可重复，至少需要：

```text
synchronous_mode = true
fixed_delta_seconds = 固定值
Traffic Manager同步模式
固定随机种子
统一客户端Tick
固定Actor创建顺序
```

Traffic Manager只有在同步模式下才能实现确定性随机行为，世界重新加载后还要重新设置随机种子。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_traffic_manager/?utm_source=chatgpt.com "Traffic Manager - CARLA Simulator UE5"))否则：

```text
同一个算法跑两次
背景车辆路线不同
行人位置不同
传感器帧率不同
```

结果就没有严格可比性。

---

# 39.19 无渲染和离屏模式

CARLA提供三种常见运行方式。

## 正常渲染

```text
有服务器窗口
有画面
生成所有视觉传感器
```

适合开发和调试。

## Off-screen Rendering

```text
没有桌面显示窗口
仍然进行GPU渲染
仍然可以生成相机图像
```

适合服务器和容器运行。

## No Rendering Mode

```text
关闭主要渲染
不生成正常视觉画面
提高运行速度
```

适合只测试：

```text
交通
控制
状态
非视觉算法
```

CARLA官方文档区分了质量等级、无渲染和离屏渲染模式；Docker也支持在无显示设备的环境中运行CARLA服务器。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/adv_rendering_options/?utm_source=chatgpt.com "Rendering options - CARLA Simulator UE5"))CARLA 与 SUMO 的关系

SUMO擅长：

```text
上千辆车交通流
道路流量
路线规划
交通信号
宏观和微观交通行为
```

CARLA擅长：

```text
高保真三维世界
车辆物理
相机与LiDAR
自动驾驶算法闭环
```

二者联合：

```text
SUMO
    负责交通流和路线

CARLA
    负责三维世界和传感器
```

CARLA官方提供SUMO同步脚本，可同步车辆、交通灯和固定时间步。([CARLA Simulator](https://carla.readthedocs.io/en/0.9.12/adv_sumo/?utm_source=chatgpt.com "SUMO co-simulation - CARLA Simulator"))``text
大量背景交通：
SUMO

少量高保真Ego与周边车辆：
CARLA

```

类似于Traffic Manager的Hybrid Physics，但进一步把交通决策交给专门仿真器。

---

# 39.21 CARLA 与 Chrono / CarSim 的关系

默认CARLA：

```text
一体化方便
适合大量车辆
物理精度中等
```

Chrono / CarSim：

```text
更详细车辆动力学
轮胎和悬架模型更专业
计算成本更高
```

组合方式：

```text
CARLA：
    地图、交通、传感器

Chrono / CarSim：
    Ego Vehicle动力学
```

这说明CARLA并不坚持：

```text
所有能力都必须自己实现
```

它更像：

```text
自主驾驶仿真总环境
```

可以把专业模块接进来。

这和CoSim要做的多后端思想高度一致。

---

# 39.22 CARLA 与 Gazebo 的区别

| 维度         | CARLA                    | Gazebo               |
| ------------ | ------------------------ | -------------------- |
| 核心目标     | 自动驾驶、交通与数据生成 | 通用机器人系统仿真   |
| 世界结构     | 城市道路优先             | 通用SDF世界          |
| 车辆交通     | 强                       | 需要自行构建         |
| 行人         | 原生支持                 | 通常需要插件         |
| OpenDRIVE    | 核心                     | 非核心               |
| ROS2         | Native/Bridge            | 原生机器人生态更成熟 |
| LiDAR/相机   | 面向自动驾驶             | 面向通用机器人       |
| PX4          | 非主线                   | 官方无人机主流后端   |
| 无人机动力学 | 非核心                   | 更适合               |
| 道路自动驾驶 | 非常适合                 | 相对弱               |
| 地图资产     | 城市和道路               | 机器人测试世界       |
| 高保真交通   | 强                       | 弱                   |

所以：

```text
CARLA：
    汽车和城市交通世界

Gazebo：
    通用机器人和PX4工程世界
```

---

# 39.23 CARLA 与 AirSim 的区别

| 维度         | CARLA                 | AirSim                  |
| ------------ | --------------------- | ----------------------- |
| 核心对象     | 汽车、交通、行人      | 无人机和汽车            |
| 道路语义     | OpenDRIVE完整体系     | 较弱                    |
| 交通系统     | 强                    | 弱                      |
| 无人机       | 非原生核心            | 核心对象之一            |
| PX4          | 非主要路线            | 历史上支持较完整        |
| 视觉传感器   | 强                    | 强                      |
| 城市动态对象 | 强                    | 较弱                    |
| API重点      | World、Actor、Traffic | Vehicle、Sensor、Flight |
| 适合我们     | 空地协同              | 无人机UE接口参考        |

CarlaAir本质上就是尝试将两者合并：

```text
CARLA交通世界
    +
AirSim无人机能力
```

---

# 39.24 CARLA 与 PX4 的关系

CARLA本身没有为PX4设计标准飞控闭环。

CARLA的车辆控制是：

```text
steering
throttle
brake
```

PX4控制对象是：

```text
motor
servo
attitude
rate
position
```

因此不能直接：

```text
PX4
    ↓
CARLA VehicleControl
```

对于空地联合系统，正确设计应是：

```text
汽车：
    CARLA Vehicle Actor

无人机：
    Gazebo / JSBSim / AirSim式动力学
    或自定义CARLA UAV Actor

统一世界：
    同步到CARLA/UE进行显示和传感器生成
```

或者使用CarlaAir类似的单UE融合方式。

---

# 39.25 CARLA 源码结构

当前UE5仓库主要目录包括：

```text
CMake/
    构建系统

Docs/
    官方文档

Examples/
    示例

Import/
    资产和地图导入工具

LibCarla/
    客户端库
    RPC
    Streaming
    Map
    Traffic Manager
    数据结构

PythonAPI/
    Python绑定
    示例
    Agents
    工具脚本

Ros2Native/
    服务器内置ROS2接口

Unreal/
    CarlaUnreal工程
    CARLA UE插件
    Actor和Sensor实现

Util/
    构建和辅助工具
```

这些目录当前直接存在于官方 `ue5-dev`仓库。([GitHub](https://github.com/carla-simulator/carla "GitHub - carla-simulator/carla: Open-source simulator for autonomous driving research. · GitHub")).1 LibCarla

它是CARLA最值得研究的核心之一。

负责：

```text
客户端API
RPC命令
传感器数据流
数据序列化
OpenDRIVE地图
Traffic Manager
Actor句柄
```

可以理解为：

```text
UE世界和外部算法之间的中间语言
```

---

## 39.25.2 Unreal / CarlaUnreal

负责：

```text
真正运行世界
车辆Actor
行人Actor
传感器Actor
天气
交通灯
场景对象
Recorder
物理和渲染
```

---

## 39.25.3 PythonAPI

负责：

```text
Python绑定
示例脚本
手动控制
交通生成
数据采集
导航Agent
```

---

## 39.25.4 Ros2Native

负责：

```text
在CARLA服务器内部
直接发布ROS2传感器和时钟
接收汽车控制消息
```

---

# 39.26 当前编译和工程成本

CARLA UE5源码构建非常重。

官方UE5 Linux构建脚本如果没有已有引擎，会下载并构建CARLA定制的UE5.5，官方文档提示可能额外使用约225 GB磁盘空间；Windows构建流程同样会下载大量依赖和引擎源码。([CARLA Simulator](https://carla-ue5.readthedocs.io/en/latest/build_linux_ue5/?utm_source=chatgpt.com "Building CARLA in Linux with Unreal Engine 5.5 - CARLA Simulator UE5"))不应该一开始就：

```text
修改CARLA核心源码
```

更合理的顺序是：

```text
先用Release Package理解API
        ↓
用Python完成实验
        ↓
评估Native ROS2
        ↓
确实需要新Actor或新Sensor
        ↓
再构建源码
```

---

# 39.27 我们应该吸收CARLA哪些设计？

## 吸收一：World—Actor—Blueprint三层模型

```text
World：
    当前仿真上下文

Actor：
    运行中的实例

Blueprint：
    实例的配置模板
```

CoSim也可以设计：

```text
WorldDefinition
ActorDefinition
ActorInstance
```

---

## 吸收二：客户端—服务器解耦

```text
仿真内核运行在Server
算法和实验运行在Client
```

这样可以支持：

```text
本机仿真
远程仿真
云端仿真
多客户端观察
```

---

## 吸收三：传感器即Actor

不要把传感器固定写在车辆类里。

应该支持：

```text
spawnSensor()
attachSensor()
detachSensor()
destroySensor()
```

---

## 吸收四：批处理命令

大量Actor操作应采用：

```text
apply_batch()
```

而不是一次一次跨进程调用。

---

## 吸收五：同步模式

CoSim需要明确：

```text
谁是Clock Master
谁负责Tick
哪些模块必须完成后才能推进下一帧
```

---

## 吸收六：背景交通降保真

```text
Ego：
    高保真

近处NPC：
    正常物理

远处NPC：
    运动学或简化模型
```

---

## 吸收七：场景和地图分离

```text
Map：
    世界结构

Scenario：
    本次实验发生什么
```

同一地图可以运行：

```text
正常交通
追尾场景
鬼探头
事故救援
空地协同
```

---

## 吸收八：Recorder和Replay

任何复杂实验都应允许：

```text
记录
重放
事件查询
失败复盘
```

---

## 吸收九：道路语义独立于视觉Mesh

对于汽车场景：

```text
看起来像路
```

和：

```text
算法知道这是路
```

必须分开。

---

# 39.28 我们不应该照搬什么？

## 不照搬一：不要让OpenDRIVE成为CoSim通用地图标准

OpenDRIVE非常适合：

```text
公路
城市道路
车道
路口
```

但不适合：

```text
无人机三维空域
室内工厂
森林
矿井
机械臂工作区
水下环境
```

CoSim应该支持：

```text
OpenDRIVE：
    道路语义层

Voxel / ESDF：
    无人机规划层

NavMesh：
    地面机器人层

SDF：
    仿真世界层
```

---

## 不照搬二：不要把UE Actor当平台核心数据对象

CARLA的Actor是UE世界实例。

但CoSim还需要：

```text
Gazebo实体
MuJoCo模型
JSBSim航空器
真实机器人
```

所以核心应为中立对象：

```text
Entity
VehicleState
SensorState
```

UE Actor只是一个Adapter。

---

## 不照搬三：不要用Traffic Manager代替研究级规划算法

Traffic Manager适合生成NPC，不应成为：

```text
Ego Vehicle高级规划器
```

---

## 不照搬四：不要让所有实验依赖高保真渲染

控制、交通逻辑和场景筛选可以：

```text
No Rendering
```

只有视觉算法需要GPU渲染。

---

## 不照搬五：不要为了使用Town10而引入完整CARLA

如果任务只是：

```text
无人机飞过城市
```

直接使用UE地图更合理。

如果任务是：

```text
无人机追踪CARLA车辆
无人机辅助自动驾驶
无人机和地面汽车协同
```

才值得使用CARLA。

---

## 不照搬六：不要同时让CARLA和Gazebo控制同一车辆

错误架构：

```text
CARLA算汽车位姿
Gazebo也算汽车位姿
```

必须明确：

```text
CARLA是权威
或
Gazebo是权威
```

另一个世界只同步显示或传感器。

---

# 39.29 CARLA 在CoSim中的正确位置

```text
                           CoSim Scenario Manager
                                     │
                ┌────────────────────┴───────────────────┐
                ▼                                        ▼
        CARLA Backend                           UAV Backend
  道路 / 汽车 / 行人 / 交通              Gazebo / JSBSim / MuJoCo
                │                                        │
                └────────────────────┬───────────────────┘
                                     ▼
                           Unified World State
                                     │
                ┌────────────────────┴───────────────────┐
                ▼                                        ▼
          ROS2 Algorithms                         UE Visualization
```

CARLA承担：

```text
道路网络
车辆
行人
交通灯
汽车传感器
汽车Ego
交通场景
```

无人机主链仍然承担：

```text
PX4
MID360
FAST-LIO2
SUPER
无人机动力学
```

空地联合时：

```text
CARLA车辆状态
        +
无人机状态
        ↓
CoSim统一场景总线
```

---

# 39.30 推荐的CARLA Adapter

```text
CarlaBackend
├─ connect()
├─ loadMap()
├─ configureWorld()
├─ tick()
├─ spawnVehicle()
├─ spawnWalker()
├─ spawnSensor()
├─ setWeather()
├─ enableTraffic()
├─ startRecorder()
├─ replay()
└─ getSnapshot()
```

统一车辆接口：

```text
GroundVehicleState
├─ position
├─ orientation
├─ linear_velocity
├─ angular_velocity
├─ acceleration
├─ steering_angle
├─ throttle
├─ brake
├─ gear
└─ bounding_box
```

统一道路接口：

```text
RoadNetwork
├─ lanes
├─ junctions
├─ traffic_lights
├─ speed_limits
├─ spawn_points
└─ landmarks
```

统一交通参与者：

```text
TrafficActor
├─ id
├─ type
├─ pose
├─ velocity
├─ bounding_box
├─ semantic_class
└─ predicted_trajectory
```

---

# 39.31 CoSim中推荐的运行模式

## 模式一：CARLA独立自动驾驶模式

```text
CARLA
├─ Ego Car
├─ NPC Traffic
├─ Sensors
└─ Map

ROS2 / Python
└─ Autonomous Driving Stack
```

适合：

```text
纯自动驾驶研究
```

---

## 模式二：空地协同模式

```text
CARLA
├─ 汽车
├─ 行人
└─ 交通

Gazebo / PX4
└─ 无人机

CoSim Clock + State Bridge
└─ 统一同步
```

适合：

```text
无人机辅助交通
道路巡检
事故检测
跨视角感知
```

---

## 模式三：视觉数据生成模式

```text
CARLA
├─ 多天气
├─ 多相机
├─ RGB
├─ Depth
├─ Semantic
├─ Instance
└─ Optical Flow
```

适合：

```text
感知训练
视觉数据集
域随机化
```

---

## 模式四：交通背景模式

```text
CARLA / SUMO
    只负责动态车辆和行人

UE或其他后端
    负责整体展示
```

---

# 39.32 最小研究任务

```text
1. 分别下载CARLA 0.9.16和0.10.0发行包
2. 跑通Town10
3. 理解Client、World和Map
4. 理解Actor与Blueprint
5. 用Python生成一辆Ego Vehicle
6. 挂载RGB、Depth、Semantic和LiDAR
7. 理解SensorData中的frame和timestamp
8. 开启同步模式和固定时间步
9. 建立传感器队列并按frame对齐
10. 跑通Traffic Manager
11. 设置确定性随机种子
12. 测试Hybrid Physics Mode
13. 跑通Recorder和Replay
14. 跑通ScenarioRunner 0.9.16
15. 理解OpenDRIVE和Waypoint
16. 导出Town地图的OpenDRIVE
17. 用OSM生成一个简单道路世界
18. 对比OSM道路和完整视觉地图
19. 跑通传统ROS2 Bridge
20. 跑通Native ROS2
21. 理解/clock和仿真同步
22. 读取RGB、LiDAR和IMU ROS2消息
23. 测试CARLA车辆控制消息
24. 研究Chrono集成
25. 查看CARLA UE5源码目录
26. 理解LibCarla与Unreal Plugin边界
27. 写CarlaBackend最小Adapter
28. 将CARLA车辆状态转换为CoSim统一格式
29. 将无人机状态同步进CARLA场景
30. 写CARLA REVIEW.md
```

---

# 39.33 第一阶段成功标准

```text
版本：
    明确区分0.9.16和0.10.0

世界：
    能加载地图和设置天气

车辆：
    能创建Ego和NPC车辆

交通：
    Traffic Manager可重复运行

传感器：
    RGB、Depth、Semantic、LiDAR、IMU同步输出

时钟：
    固定步长和同步模式正确

ROS2：
    能发布/clock和传感器话题

场景：
    能记录、重放和运行ScenarioRunner

接口：
    能输出CoSim统一GroundVehicleState

空地：
    能将一架外部无人机同步到CARLA世界中
```

---

# 39.34 CARLA REVIEW.md 应该写什么

```text
1. 项目定位
    自动驾驶与城市交通仿真平台

2. 当前版本
    0.9.16 / UE4.26
    0.10.0 / UE5.5

3. 它解决什么问题
    道路交通
    自动驾驶感知
    车辆控制
    动态场景
    数据生成
    自动化评测

4. 核心架构
    Server / Client
    World
    Actor
    Blueprint
    Map
    Sensor
    Traffic Manager

5. 地图体系
    UE视觉地图
    OpenDRIVE道路逻辑
    Waypoint
    Traffic Light
    Custom Map

6. 传感器
    Camera
    LiDAR
    Radar
    IMU
    GNSS
    Semantic

7. 场景体系
    Traffic Manager
    ScenarioRunner
    Scenic
    Recorder

8. ROS2
    ROS Bridge
    Native ROS2
    Clock
    Vehicle Control

9. 我们吸收什么
    World—Actor—Blueprint
    Client—Server
    传感器Actor
    同步Tick
    背景交通降保真
    Recorder
    场景分离

10. 不照搬什么
    OpenDRIVE通用化
    UE Actor核心化
    Traffic Manager代替Ego规划
    CARLA作为无人机动力学
    为地图而接入整个CARLA

11. 在CoSim中的位置
    道路交通与空地协同后端
```

---

# 39.35 对CARLA的最终判断

```text
是否进入CoSim：
    是

是否作为无人机主干：
    否

进入哪一层：
    道路交通仿真后端
    自动驾驶数据后端
    空地协同场景后端

主要吸收：
    Client—Server
    World—Actor—Blueprint
    OpenDRIVE道路语义
    Traffic Manager
    同步模式
    传感器系统
    Recorder
    ScenarioRunner
    Native ROS2

主要用途：
    汽车自动驾驶
    交通流
    行人和动态道路场景
    跨视角感知
    无人机—车辆协同
    城市数据集生成

不承担：
    PX4无人机动力学
    MID360真实扫描
    LIO
    无人机轨迹规划
    通用机器人仿真
    单纯地图资产管理
```

最核心的一句话是：

> **CARLA真正值得CoSim吸收的，不是Town10这张城市地图，而是它把“城市世界、道路语义、交通参与者、车辆、传感器、时间同步和场景复现”组织成统一自动驾驶实验平台的方式。对于纯无人机项目，UE官方免费地图更直接；对于空地协同、动态交通和跨视角感知，CARLA才具有不可替代的系统价值。**
>
