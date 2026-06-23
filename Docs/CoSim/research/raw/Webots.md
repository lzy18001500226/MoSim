# 40. 项目概述：Webots

## 40.1 定位

Webots 是由 Cyberbotics 长期维护的一套开源、跨平台、通用机器人仿真器。

它的核心定位是：

> **在一个集成式桌面环境中，完成机器人模型搭建、世界编辑、刚体物理、传感器仿真、控制器编程、实验运行和结果展示。**

Webots不是单独的物理引擎，也不是单独的机器人模型库，而是把下面这些功能整合在一个软件中：

```text
三维世界编辑器
    +
机器人模型系统
    +
刚体与接触物理
    +
相机、LiDAR、IMU等传感器
    +
电机、关节等执行器
    +
C/C++/Python/Java/MATLAB控制器
    +
ROS2接口
    +
实验监督与自动化
```

Cyberbotics将Webots描述为完整的机器人建模、编程和仿真开发环境；其核心由Qt界面、ODE分支物理引擎和名为WREN的OpenGL 3.3渲染引擎组成。([Cyberbotics](https://www.cyberbotics.com/index.php "Cyberbotics: Robotics simulation with Webots"))

对CoSim而言，Webots最合理的位置是：

```text
快速机器人原型后端
教学与算法验证后端
多类型机器人统一演示后端
ROS2功能测试后端
轻量级跨平台仿真后端
```

而不是：

```text
最高保真无人机动力学后端
UE级高真实感渲染前端
大规模GPU强化学习后端
PX4官方主力仿真后端
复杂航空气动求解器
```

---

# 40.2 当前版本与开源状态

截至  **2026年6月14日** ，Webots最新正式稳定版仍是：

```text
Webots R2025a
发布时间：2025年1月31日
```

官方开发文档中已经出现R2025b的变更记录，但仍标记为未正式发布日期；GitHub同时持续发布nightly build，因此研究和生产环境应优先使用R2025a稳定版，而不是直接依赖每日构建。([Cyberbotics](https://www.cyberbotics.com/doc/reference/changelog-r2025?tab-language=c&utm_source=chatgpt.com "Webots documentation: Webots R2025 Change Log"))

Webots核心源码采用Apache 2.0许可证，可以免费用于研究、教学和商业项目。不过，Webots附带的某些机器人、物体和PROTO资产可能使用单独的Webots Assets许可证或贡献者许可证，因此模型资产仍需逐项检查。([Cyberbotics](https://cyberbotics.com/doc/guide/webots-license-agreement?utm_source=chatgpt.com "Webots documentation: License Agreement"))

当前官方主要支持：

```text
Windows 10 / 11
Ubuntu 22.04 / 24.04
macOS 12—14
```

官方稳定文档对应R2025a。([Cyberbotics](https://www.cyberbotics.com/doc/guide/system-requirements?utm_source=chatgpt.com "Webots documentation: System Requirements"))

---

# 40.3 Webots最容易被误解的地方

很多人第一次看到Webots，会认为它只是：

```text
一个比Gazebo更简单的机器人仿真器
```

其实它真正的特点是：

> **Webots把机器人仿真需要的几乎所有基础环节，都做成了一个高度集成的桌面应用。**

它不像Gazebo那样主要依靠：

```text
SDF
插件
ROS节点
外部工具链
```

来组合系统。

Webots更像：

```text
机器人版MATLAB Simulink
    +
简化版UE编辑器
    +
物理引擎
    +
机器人控制IDE
```

打开一个Webots项目后，用户可以直接看到：

```text
左侧：
    场景树

中间：
    三维世界

下方：
    控制器代码、日志和控制台

顶部：
    暂停、单步、实时、快速运行
```

所以Webots最大的优势不是某一个单独模块特别强，而是：

```text
上手快
系统完整
修改直观
实验可直接运行
```

---

# 40.4 核心设计理念

| 设计原则             | 说明                                       |
| -------------------- | ------------------------------------------ |
| 世界与控制器分离     | `.wbt`描述世界，控制程序负责机器人行为   |
| 场景树建模           | 所有对象以层级Node组织                     |
| PROTO复用            | 用模板封装复杂机器人和场景对象             |
| 每机器人独立控制器   | 每个机器人对应一个独立进程                 |
| 传感器与执行器节点化 | Camera、Lidar、Motor等都直接挂在机器人树上 |
| 固定仿真时间步       | 物理世界按照 `basicTimeStep`推进         |
| Supervisor特权控制   | 独立管理场景、重置、生成对象和评测         |
| 配置与算法解耦       | 机器人结构放在场景中，算法放在Controller中 |
| 跨语言控制           | 支持C、C++、Python、Java、MATLAB           |
| 外部控制器           | 控制程序可以脱离Webots进程甚至远程运行     |
| 资产复用             | 官方提供大量机器人、传感器和物体PROTO      |
| ROS2优先             | 当前官方生态已明确转向ROS2                 |

Webots项目通常包含世界文件、PROTO、控制器和可选插件；每个机器人控制器由Webots作为独立进程启动。([Cyberbotics](https://www.cyberbotics.com/doc/guide/introduction-to-webots?version=cyberbotics%3AR2019a&utm_source=chatgpt.com "Webots documentation: Introduction to Webots"))

---

# 40.5 系统设计逻辑

## 40.5.1 第一性原理：为什么世界文件和控制程序必须分离？

假设我们建立一个轮式机器人。

如果把这些内容全部写在同一个程序中：

```text
机器人外形
轮子位置
传感器位置
墙壁位置
机器人控制算法
```

那么每次换地图、换传感器或者换控制算法，都要修改大量代码。

Webots把它拆成：

```text
World / Robot Model
    描述世界是什么

Controller
    描述机器人怎么行动
```

例如：

```text
warehouse.wbt
    描述仓库、货架、机器人和传感器

navigation_controller.py
    描述导航算法
```

这样可以实现：

```text
同一个机器人
    换不同世界

同一个世界
    换不同算法

同一个算法
    控制多台机器人
```

世界文件只记录控制器名称，不直接包含控制器源代码。([Cyberbotics](https://www.cyberbotics.com/doc/guide/introduction-to-webots?version=cyberbotics%3AR2019a&utm_source=chatgpt.com "Webots documentation: Introduction to Webots"))

---

## 40.5.2 第二性原理：为什么使用场景树？

Webots世界不是平铺的一堆对象，而是层级结构：

```text
Robot
├─ Body
├─ LeftWheel
│  ├─ HingeJoint
│  └─ RotationalMotor
├─ RightWheel
├─ Camera
├─ Lidar
└─ InertialUnit
```

这种层级关系可以直接表达：

```text
相机安装在机器人上
轮子通过关节连接车体
传感器跟随机体运动
关节内部包含电机
```

如果相机属于机器人子节点，那么机器人移动时，相机会自动跟随。

这与UE的Actor Component、URDF Link-Joint结构和MuJoCo的Body Tree，本质上是同一种思想：

> **复杂机器人不是一堆没有关系的物体，而是一棵有父子约束的结构树。**

Webots世界继承了VRML风格的层级节点体系，世界中的位置、姿态、几何、外观和物理属性都保存在场景树中。([Cyberbotics](https://www.cyberbotics.com/doc/guide/introduction-to-webots?version=cyberbotics%3AR2019a&utm_source=chatgpt.com "Webots documentation: Introduction to Webots"))

---

## 40.5.3 第三性原理：为什么需要PROTO？

假设每次使用TurtleBot，都要在世界文件中展开：

```text
底盘
轮子
电机
相机
LiDAR
碰撞体
质量
惯量
材质
```

世界文件会非常庞大。

PROTO相当于：

```text
机器人模板
```

它把复杂节点树封装成一个新节点类型：

```text
TurtleBot3 {
    translation 0 0 0
    controller "navigation"
    camera TRUE
    lidar TRUE
}
```

而内部可能包含几十甚至几百个节点。

PROTO接口可以暴露：

```text
颜色
控制器名称
传感器开关
轮胎摩擦
机器人名称
外部扩展槽
```

同时隐藏内部细节。

可以类比为：

```text
C++ Class：
    封装代码对象

Webots PROTO：
    封装场景对象
```

PROTO可以由内置Node或其他PROTO组合而成，并像原生节点一样在场景树中实例化。([Cyberbotics](https://cyberbotics.com/doc/reference/proto?version=R2021b&utm_source=chatgpt.com "Webots documentation: PROTO"))

---

## 40.5.4 第四性原理：为什么每个机器人使用独立控制器进程？

Webots不会把所有机器人的算法都强制编译进主程序。

默认情况下，每台机器人对应一个控制器进程：

```text
Webots Physics Process
    │
    ├── Robot 1 Controller
    ├── Robot 2 Controller
    └── Robot 3 Controller
```

每个控制器只看到自己的：

```text
传感器
执行器
机器人时间步
```

这很接近真实机器人：

```text
每台机器人都有自己的计算机
通过传感器读取世界
通过执行器影响世界
```

优点是：

```text
机器人算法相互隔离
控制器崩溃不一定破坏主仿真器
可使用不同编程语言
容易模拟多机器人独立计算
```

缺点是：

```text
机器人数量很多时进程开销增加
大量进程通信需要管理
不适合数千机器人高吞吐训练
```

官方说明，同一个控制器代码可供多台机器人使用，但每台机器人仍会启动独立控制器进程。([Cyberbotics](https://www.cyberbotics.com/doc/guide/introduction-to-webots?version=cyberbotics%3AR2019a&utm_source=chatgpt.com "Webots documentation: Introduction to Webots"))

---

## 40.5.5 第五性原理：为什么需要Supervisor？

普通机器人只能通过自己的传感器理解环境。

例如它不应该直接知道：

```text
障碍物真实坐标
其他机器人真值位置
整个场景树
```

但自动化实验系统需要一个“上帝视角”：

```text
重置机器人
改变目标位置
随机生成障碍物
读取真值
判断任务是否完成
保存视频
结束仿真
```

Webots将这种特权程序称为：

```text
Supervisor Controller
```

可以理解为：

```text
普通Controller：
    被测试的机器人

Supervisor：
    实验管理员和裁判
```

Supervisor可以访问和修改场景节点，并执行普通机器人在真实世界中无法执行的操作。([Cyberbotics](https://www.cyberbotics.com/doc/guide/introduction-to-webots?version=cyberbotics%3AR2019a&utm_source=chatgpt.com "Webots documentation: Introduction to Webots"))

这对CoSim非常有价值，因为它直接对应：

```text
Experiment Manager
Scenario Manager
Ground Truth Manager
Evaluation Manager
```

---

# 40.6 Webots整体架构

```text
┌─────────────────────────────────────────┐
│              Webots GUI                 │
│ Scene Tree / 3D View / Editor / Console │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│              Simulation Core            │
│                                         │
│ World Nodes / PROTO / Physics / WREN    │
│ Devices / Robot / Supervisor / Clock    │
└─────────┬───────────────┬───────────────┘
          │               │
          ▼               ▼
    Controller 1      Controller 2
 C/C++/Python/...   C/C++/Python/...
          │               │
          └───────┬───────┘
                  ▼
        Sensors and Actuators
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
  External Controller      ROS2 Driver
```

从CoSim视角看，Webots自身已经包含：

```text
World Backend
Physics Backend
Sensor Backend
Robot Runtime
Scenario Supervisor
Visualization Frontend
```

所以它是一套完整仿真器，而不只是一个子模块。

---

# 40.7 Webots项目目录结构

典型项目：

```text
my_webots_project/
├─ worlds/
│  └─ warehouse.wbt
│
├─ protos/
│  ├─ MyRobot.proto
│  └─ CustomLidar.proto
│
├─ controllers/
│  ├─ robot_controller/
│  │  └─ robot_controller.py
│  └─ supervisor/
│     └─ supervisor.py
│
├─ plugins/
│  ├─ physics/
│  ├─ robot_windows/
│  └─ remote_controls/
│
├─ libraries/
├─ motions/
└─ worlds/.warehouse.wbproj
```

其中：

```text
worlds：
    世界文件

protos：
    可复用机器人和物体模板

controllers：
    机器人控制程序

plugins：
    物理、界面或远程控制扩展

libraries：
    控制器共享库
```

官方项目规范将世界、PROTO和控制器放在对应子目录中。([Cyberbotics](https://www.cyberbotics.com/doc/guide/the-standard-file-hierarchy-of-a-project?version=master&utm_source=chatgpt.com "Webots documentation: The Standard File Hierarchy of a Project"))

---

# 40.8 World文件

Webots世界文件扩展名为：

```text
.wbt
```

它记录：

```text
世界基础时间步
重力
背景天空
地面
灯光
机器人
物体
关节
传感器
碰撞体
物理属性
```

简化示意：

```text
WorldInfo {
  basicTimeStep 16
}

Viewpoint {
  position 3 3 2
}

RectangleArena {
  floorSize 10 10
}

MyRobot {
  translation 0 0 0.2
  controller "my_controller"
}
```

它与Gazebo SDF的关系可以理解为：

```text
Webots .wbt：
    Webots原生世界描述

Gazebo .sdf：
    Gazebo原生世界描述
```

两者都在描述：

```text
世界中有什么
物体在哪里
物理属性是什么
```

但语法、节点和运行时完全不同。

---

# 40.9 Node体系

Webots内置节点大体可以分为：

## 场景节点

```text
WorldInfo
Viewpoint
Background
Fog
DirectionalLight
```

## 几何与外观

```text
Shape
Appearance
PBRAppearance
Mesh
Box
Sphere
Cylinder
IndexedFaceSet
```

## 物理对象

```text
Solid
Physics
BoundingObject
ContactProperties
```

## 机器人结构

```text
Robot
Solid
Slot
Joint
HingeJoint
SliderJoint
```

## 传感器

```text
Camera
Lidar
RangeFinder
GPS
InertialUnit
Gyro
Accelerometer
Compass
DistanceSensor
TouchSensor
Radar
```

## 执行器

```text
RotationalMotor
LinearMotor
Brake
LED
Speaker
Display
```

Webots机器人和物体都是这些基础节点组合出来的。

---

# 40.10 视觉几何与碰撞几何分离

与Gazebo、UE和MuJoCo一样，Webots也区分：

```text
给人看的几何
```

与：

```text
给物理引擎算碰撞的几何
```

例如：

```text
Shape {
  geometry Mesh {
    url "detailed_robot.dae"
  }
}

boundingObject Box {
  size 0.5 0.3 0.2
}
```

含义是：

```text
显示：
    使用复杂机器人Mesh

碰撞：
    使用简单Box
```

这么做的原因是复杂三角网格碰撞：

```text
计算慢
接触不稳定
容易卡住
```

所以机器人仿真通常应该：

```text
视觉Mesh精细
碰撞模型简单
```

这与你之前理解Gazebo中：

```text
visual
collision
```

是完全一致的。

---

# 40.11 物理系统

## 40.11.1 核心物理引擎

Webots使用其维护的ODE分支作为物理基础。ODE负责：

```text
刚体运动
关节约束
碰撞检测
接触力
摩擦
重力
```

Cyberbotics官方明确说明Webots核心采用ODE fork。([Cyberbotics](https://www.cyberbotics.com/index.php?utm_source=chatgpt.com "Cyberbotics: Robotics simulation with Webots"))

物理对象通常需要定义：

```text
mass
centerOfMass
density
inertiaMatrix
boundingObject
friction
bounce
```

---

## 40.11.2 Webots物理的优势

```text
结构直观
参数配置简单
轮式、机械臂和教育机器人容易搭建
与场景树高度集成
接触和关节模型足够通用
```

特别适合：

```text
轮式机器人
机械臂
腿式机器人基础仿真
服务机器人
教育机器人
简单无人机
```

---

## 40.11.3 Webots物理的局限

Webots物理主循环依赖单线程ODE执行，因此复杂接触、大量机器人和高分辨率碰撞体时，CPU扩展能力有限。官方建模文档明确指出Webots物理需要单线程运行。([Cyberbotics](https://www.cyberbotics.com/doc/guide/modeling?version=R2019b-rev1&utm_source=chatgpt.com "Webots documentation: Modeling"))

这意味着：

```text
增加CPU核心
    不一定线性增加物理速度
```

尤其在以下场景中可能受限：

```text
大量机器人
大量接触
复杂轮胎
高自由度机械臂
大规模碎片
几百个动态物体
```

因此Webots不适合承担：

```text
数千环境并行RL
大规模GPU物理
极高保真接触研究
```

---

# 40.12 时间管理

Webots使用：

```text
WorldInfo.basicTimeStep
```

定义基础物理步长。

例如：

```text
basicTimeStep = 16 ms
```

意味着物理引擎以约：

```text
62.5 Hz
```

推进。

机器人控制器通常调用：

```text
robot.step(timeStep)
```

控制器在每一个控制周期中：

```text
读取传感器
    ↓
执行算法
    ↓
设置执行器
    ↓
调用step
    ↓
等待下一仿真时刻
```

Webots提供：

```text
Pause
Step
Real-time
Run
Fast
```

等模式；Fast模式尽可能快运行，而Real-time模式尽量保持虚拟时间和现实时间一致。渲染也可以关闭以提高运行速度。([Cyberbotics](https://www.cyberbotics.com/doc/guide/the-user-interface?version=omichel%3Amaster&utm_source=chatgpt.com "Webots documentation: The User Interface"))

这说明Webots天然支持：

```text
实时演示
单步调试
快于实时测试
无渲染批量运行
```

---

# 40.13 渲染系统

Webots使用：

```text
WREN
```

作为渲染引擎，底层基于OpenGL 3.3。([Cyberbotics](https://www.cyberbotics.com/index.php?utm_source=chatgpt.com "Cyberbotics: Robotics simulation with Webots"))

它支持：

```text
PBR材质
阴影
纹理
灯光
天空
相机
深度
分割
```

画面质量明显好于传统纯调试级仿真器，但整体定位仍然是：

```text
机器人仿真渲染
```

而不是：

```text
UE5影视级渲染
```

所以：

```text
Webots：
    足够清晰、稳定、轻量

UE5：
    高真实感、复杂光照、大规模资产
```

如果目标是：

```text
验证导航和机器人行为
```

Webots完全够用。

如果目标是：

```text
比赛展示
高质量视觉域随机化
真实城市和自然环境
```

UE仍然更合适。

---

# 40.14 传感器系统

Webots最大的优点之一，是传感器直接成为机器人节点。

例如：

```text
Robot
├─ Camera
├─ Lidar
├─ GPS
├─ InertialUnit
├─ Gyro
└─ Accelerometer
```

控制器通过统一API获取设备：

```python
camera = robot.getDevice("camera")
lidar = robot.getDevice("lidar")
```

然后设置周期：

```python
camera.enable(time_step)
lidar.enable(time_step)
```

这种设计非常直观。

---

## 40.14.1 Camera

可配置：

```text
分辨率
视场角
曝光
焦距
噪声
识别功能
分割
```

可用于：

```text
目标检测
视觉导航
车道识别
SLAM
视觉控制
```

---

## 40.14.2 Lidar

可配置：

```text
层数
水平分辨率
垂直视场
最大距离
扫描周期
噪声
点云输出
```

它适合通用旋转式或规则扫描LiDAR。

但与CARLA一样，Webots默认LiDAR模型并不自动等于MID360的非重复扫描模式。

若要真实模拟MID360，需要扩展：

```text
扫描方向随时间变化
逐点时间戳
Livox扫描花纹
反射噪声
盲区
点云分包
```

---

## 40.14.3 IMU体系

Webots通常将IMU拆成多个设备：

```text
InertialUnit：
    姿态

Gyro：
    角速度

Accelerometer：
    加速度

Compass：
    磁场方向

GPS：
    位置和速度
```

这与真实系统的传感器分工接近。

但如果要测试FAST-LIO2、PX4 EKF2，需要自己加入更真实的：

```text
零偏
随机游走
时间延迟
饱和
温漂
噪声密度
```

不能直接把完美真值传感器当成真实IMU。

---

# 40.15 执行器系统

Webots常见执行器包括：

```text
RotationalMotor
LinearMotor
Brake
LED
Speaker
Display
Emitter
```

Motor可以工作在不同模式：

```text
位置控制
速度控制
力矩控制
```

例如轮式机器人：

```text
setPosition(INFINITY)
setVelocity(5.0)
```

表示：

```text
不做位置控制
直接控制轮速
```

机械臂则可能使用：

```text
目标关节角度
```

无人机则需要：

```text
各旋翼转速或推力
```

再通过物理模型生成总力和力矩。

---

# 40.16 Controller控制器体系

Webots控制器可使用：

```text
C
C++
Python
Java
MATLAB
```

官方也提供ROS和ROS2接口。([Cyberbotics](https://www.cyberbotics.com/index.php "Cyberbotics: Robotics simulation with Webots"))

控制器典型结构：

```python
from controller import Robot

robot = Robot()
time_step = int(robot.getBasicTimeStep())

motor = robot.getDevice("motor")
sensor = robot.getDevice("sensor")

sensor.enable(time_step)

while robot.step(time_step) != -1:
    value = sensor.getValue()
    motor.setVelocity(compute_command(value))
```

核心模式就是：

```text
初始化
    ↓
获得设备
    ↓
启用传感器
    ↓
循环step
    ↓
读取—计算—控制
```

这对教学非常友好，因为用户不需要首先理解：

```text
ROS节点
DDS
插件生命周期
SDF系统插件
```

就可以直接编写机器人算法。

---

# 40.17 外部Controller

机器人 `controller`字段可以设为：

```text
<extern>
```

此时Webots不会自动启动控制器，而是等待一个外部程序连接。

外部控制器可以：

```text
独立在IDE中调试
独立从命令行启动
运行在另一台计算机
连接不同Webots实例
控制指定机器人
```

官方支持通过TCP将外部控制器运行在远程机器上，并可通过端口和机器人名称区分多个仿真实例。([Cyberbotics](https://www.cyberbotics.com/doc/guide/running-extern-robot-controllers?version=R2023b&utm_source=chatgpt.com "Webots documentation: Running Extern Robot Controllers"))

这对CoSim非常重要，因为它意味着：

```text
Webots可以只做仿真服务器
算法运行在外部
```

而不是必须将算法写入Webots项目。

---

# 40.18 Supervisor系统

Supervisor可以：

```text
读取场景节点
修改节点字段
移动机器人
创建或删除对象
重置仿真
改变控制器
记录视频
获取真值位置
控制仿真运行模式
```

典型用途：

```text
随机场景生成
自动评分
强化学习reset
任务成功判断
机器人碰撞检测
批量实验
竞赛管理
```

例如：

```text
每个episode：
    随机生成障碍物
    重置机器人
    设置目标点
    启动仿真
    计算得分
    结束后重新开始
```

Webots在线机器人竞赛和robotbenchmark也大量依赖Supervisor管理规则和评测。([Cyberbotics](https://www.cyberbotics.com/index.php "Cyberbotics: Robotics simulation with Webots"))

---

# 40.19 PROTO资产生态

从R2022b开始，Webots官方资产主要通过：

```text
webots.cloud
```

提供与检索。

资产包括：

```text
机器人
车辆
无人机
机械臂
传感器
执行器
家具
道路
建筑
材质
```

任何人也可以将托管在公开GitHub仓库中的PROTO注册到webots.cloud。([Cyberbotics](https://cyberbotics.com/doc/guide/assets?utm_source=chatgpt.com "Webots documentation: Assets"))

Webots在“机器人模型资产”方面，比Gazebo更集中、更容易搜索。

它特别适合快速找到：

```text
TurtleBot
e-puck
Nao
TIAGo
UR机械臂
Clearpath机器人
DJI无人机
汽车
教育机器人
```

官方还维护 `webots-projects`仓库，用于提供额外世界、控制器和PROTO，但需要与对应Webots主版本匹配。([GitHub](https://github.com/cyberbotics/webots-projects?utm_source=chatgpt.com "GitHub - cyberbotics/webots-projects: Additional Webots projects (PROTO files, controllers, simulation worlds, etc.) officially released by Cyberbotics."))

---

# 40.20 Webots的地图能力

Webots可以创建：

```text
室内房间
仓库
工厂
道路
城市
森林
竞技场
水下环境
```

也支持导入：

```text
Blender/CAD模型
URDF
OpenStreetMap道路
```

官方强调Webots可导入CAD、URDF和OpenStreetMap地图。([Cyberbotics](https://www.cyberbotics.com/index.php "Cyberbotics: Robotics simulation with Webots"))

但与刚才讲CARLA和UE一样，需要分清：

```text
Webots世界
```

和：

```text
高质量地图资产
```

Webots世界更注重：

```text
机器人可以运动
碰撞正确
传感器可工作
场景容易编辑
```

而不是：

```text
影视级建筑
超高质量自然环境
Nanite资产
Lumen光照
```

所以Webots地图适合：

```text
机器人实验
教学
导航测试
算法验证
```

而不是作为CoSim最终UE高保真地图来源。

---

# 40.21 URDF与Webots模型的关系

Webots可以导入URDF，也可以将机器人模型导出为URDF。官方命令行还支持将PROTO转换为URDF、WBO或WRL。([Cyberbotics](https://www.cyberbotics.com/doc/reference/robot?version=2a3f8c3&utm_source=chatgpt.com "Webots documentation: Robot"))

但需要注意：

```text
URDF：
    主要描述Link和Joint
    不擅长复杂场景模板

PROTO：
    可以描述机器人
    也可以描述家具、建筑和完整模块
    支持参数化和嵌套
```

因此：

```text
URDF适合机器人结构交换

PROTO适合Webots内部资产复用
```

不能简单认为：

```text
PROTO就是URDF换了一种语法
```

PROTO的抽象能力更接近：

```text
参数化Prefab
```

---

# 40.22 ROS2体系

## 40.22.1 webots_ros2

官方维护：

```text
cyberbotics/webots_ros2
```

用于将Webots接入ROS2消息、服务和Action体系。

当前ROS2软件包线已经对应Webots R2025a，并发布到Humble、Jazzy、Kilted、Rolling等ROS2发行版文档中。([ROS 文档](https://docs.ros.org/en/ros2_packages/humble/api/webots_ros2/index.html?utm_source=chatgpt.com "webots_ros2 — webots_ros2: Humble 2025.0.1 documentation"))

主要组件包括：

```text
webots_ros2_driver
webots_ros2_control
webots_ros2_importer
Ros2Supervisor
各种机器人示例
```

---

## 40.22.2 webots_ros2_driver

其作用可以理解为：

```text
Webots Robot
      │
      ▼
webots_ros2_driver
      │
      ├─ 发布Sensor Topics
      ├─ 订阅Motor Commands
      ├─ 发布TF
      ├─ 发布JointState
      └─ 连接自定义Plugin
```

这样ROS2算法不需要直接调用Webots原生Python API。

---

## 40.22.3 Ros2Supervisor

它将Webots Supervisor功能暴露给ROS2。

可以通过ROS2：

```text
生成机器人
删除机器人
重置仿真
获取节点
修改场景
```

这非常适合：

```text
Nav2测试
自动化集成测试
强化学习环境
多机器人实验
```

ROS2官方教程也直接提供Webots和Ros2Supervisor的使用方法。([ROS 文档](https://docs.ros.org/en/iron/Tutorials/Advanced/Simulators/Webots/Simulation-Webots.html?utm_source=chatgpt.com "Webots — ROS 2 Documentation: Iron documentation"))

---

## 40.22.4 ROS1状态

Webots R2025a官方已经明确建议用户转向ROS2，并提到原有 `webots_ros`进入弃用阶段。([Cyberbotics](https://www.cyberbotics.com/doc/blog/Webots-2025-a-release?tab-language=python&utm_source=chatgpt.com "Webots Blog: Version R2025a Released"))

因此对CoSim来说：

```text
只研究ROS2主链
```

即可，没有必要再投入大量时间建设新的ROS1接口。

---

# 40.23 Webots与PX4的关系

当前PX4官方核心支持的仿真器主要是：

```text
Gazebo
SIH
```

Gazebo Classic已转为社区维护；PX4当前官方支持列表中没有将Webots列为核心支持后端。([PX4 文档](https://docs.px4.io/main/en/simulation/index "Simulation | PX4 Guide (main)"))

因此必须明确：

> **Webots不是当前PX4官方主力仿真器。**

理论上仍然可以建立：

```text
PX4 SITL
    ↓ 电机或舵面输出
Webots Adapter
    ↓
Webots动力学
    ↓ IMU/GPS/磁力计/气压计
PX4
```

实现方式可以使用：

```text
MAVLink Simulator API
HIL_SENSOR
HIL_GPS
HIL_STATE_QUATERNION
HIL_ACTUATOR_CONTROLS
```

PX4官方说明大多数外部仿真器可以通过Simulator MAVLink API交换传感器和执行器数据。([PX4 文档](https://docs.px4.io/main/en/simulation/index "Simulation | PX4 Guide (main)"))

但这需要我们自行完成：

```text
PX4—Webots桥接
坐标转换
传感器噪声
时间同步
电机映射
锁步
```

所以它不是开箱即用路线。

---

# 40.24 Webots与无人机

Webots支持飞行机器人和无人机资产，官方资产库也包括无人机模型，并展示DJI Mavic 2 Pro等飞行机器人示例。([Cyberbotics](https://www.cyberbotics.com/index.php "Cyberbotics: Robotics simulation with Webots"))

无人机模型一般包含：

```text
机体刚体
四个或多个旋翼
旋翼推力模型
IMU
GPS
Camera
Lidar
控制器
```

典型动力学链：

```text
Motor Command
    ↓
Rotor Thrust / Torque
    ↓
Webots ODE Rigid Body
    ↓
Position / Attitude
```

Webots适合：

```text
无人机控制教学
简单四旋翼控制
视觉导航
多机算法演示
基础避障
```

但对你们的Sunray-150主线，存在几个问题：

```text
没有PX4官方主力接口
MID360扫描需要自定义
四旋翼气动较简化
高速飞行精度需要验证
LIO与规划生态不如Gazebo自然
```

因此它更适合成为：

```text
轻量算法验证后端
```

而不是替代：

```text
Gazebo + PX4 + MID360
```

---

# 40.25 Webots与Gazebo的区别

| 维度         | Webots                   | Gazebo               |
| ------------ | ------------------------ | -------------------- |
| 核心定位     | 集成式机器人开发与教学   | 模块化机器人系统仿真 |
| GUI          | 强，场景树和编辑器一体化 | 更偏仿真运行与插件   |
| 模型格式     | WBT / PROTO              | SDF / URDF           |
| 物理         | ODE分支                  | gz-physics多后端     |
| ROS2         | 官方webots_ros2          | ROS2和PX4生态更强    |
| 机器人资产   | webots.cloud集中         | Fuel等生态更分散     |
| 控制器       | Webots独立进程           | 通常ROS节点/插件     |
| Supervisor   | 原生强大                 | 需系统插件或ROS节点  |
| PX4          | 非官方主力               | 官方默认后端         |
| 上手难度     | 低                       | 较高                 |
| 系统扩展性   | 中等                     | 较强                 |
| 大型工程集成 | 一般                     | 更适合               |
| 教学         | 非常适合                 | 相对复杂             |

可以概括为：

```text
Webots：
    把机器人仿真做好用

Gazebo：
    把机器人系统做好扩展
```

---

# 40.26 Webots与MuJoCo的区别

| 维度           | Webots                     | MuJoCo               |
| -------------- | -------------------------- | -------------------- |
| 核心目标       | 完整机器人仿真开发环境     | 高效动力学、控制与RL |
| GUI            | 完整世界编辑器             | Viewer偏调试         |
| 传感器         | Camera、LiDAR、GPS等较完整 | 主要力学和状态传感器 |
| ROS2           | 官方支持                   | 需要自行适配         |
| 接触优化       | 通用ODE                    | MuJoCo优化型接触更强 |
| GPU批量        | 弱                         | MJX/Warp强           |
| 场景编辑       | 方便                       | MJCF更偏文本模型     |
| 教学           | 强                         | 更适合控制和RL研究   |
| 机器人算法演示 | 强                         | 一般                 |
| 大规模训练     | 不适合                     | 更适合               |

所以：

```text
Webots：
    快速搭建一个完整机器人世界

MuJoCo：
    快速运行大量控制和学习实验
```

---

# 40.27 Webots与UE的区别

| 维度       | Webots           | Unreal Engine              |
| ---------- | ---------------- | -------------------------- |
| 本质       | 机器人仿真器     | 通用游戏与实时渲染引擎     |
| 机器人结构 | 原生支持         | 需插件和自定义             |
| 传感器     | 原生机器人传感器 | 视觉强，机器人传感器需开发 |
| 物理       | ODE，面向机器人  | Chaos，面向通用实时交互    |
| 渲染       | 工程级           | 高真实感                   |
| ROS2       | 官方包           | 依赖rclUE等桥接            |
| 场景资产   | 较少但实用       | 极丰富                     |
| 算法接入   | 简单             | 需要架构设计               |
| 教学       | 强               | 门槛高                     |

因此：

```text
Webots：
    开箱即用的机器人实验室

UE：
    高质量但需要自己搭建机器人实验室
```

---

# 40.28 Webots的最大优势

## 优势一：真正一体化

从模型到控制器都在一个软件里完成。

---

## 优势二：入门成本低

不需要先学习：

```text
Gazebo插件系统
ROS2通信
复杂构建系统
UE C++
```

就能让机器人运动。

---

## 优势三：机器人资产丰富

尤其适合快速测试不同机器人。

---

## 优势四：Supervisor非常成熟

自动化实验和教学竞赛非常方便。

---

## 优势五：跨平台

Windows、Linux和macOS都能原生运行。

---

## 优势六：控制器语言丰富

Python和MATLAB用户也容易使用。

---

## 优势七：确定性和版本兼容重视较高

官方强调Webots的确定性、文档和版本兼容测试。([Cyberbotics](https://www.cyberbotics.com/index.php "Cyberbotics: Robotics simulation with Webots"))

---

# 40.29 Webots的主要局限

## 局限一：物理引擎较传统

ODE足够成熟，但不是当前最先进的GPU或优化型物理引擎。

---

## 局限二：物理单线程瓶颈

复杂大场景和大量机器人性能有限。

---

## 局限三：渲染不及UE

不适合作为最高真实感视觉仿真主干。

---

## 局限四：PX4生态不强

不是当前PX4官方主要仿真方案。

---

## 局限五：高端航空动力学不足

固定翼、复合翼和eVTOL更适合JSBSim。

---

## 局限六：大规模RL不适合

Webots多进程控制器和单线程物理不适合数千环境并行。

---

## 局限七：项目容易被Webots格式锁定

如果大量模型全部只存在于：

```text
PROTO / WBT
```

以后迁移Gazebo、MuJoCo和UE会产生重复工作。

---

# 40.30 我们应该吸收Webots哪些设计？

## 吸收一：World—Robot—Device结构

```text
World
└─ Robot
   ├─ Sensor
   ├─ Actuator
   └─ Controller
```

这种层级很适合CoSim的统一对象模型。

---

## 吸收二：PROTO式参数化资产

CoSim可以建立：

```text
VehicleTemplate
SensorTemplate
EnvironmentTemplate
```

再实例化：

```text
Sunray150 {
    lidar = mid360
    camera = front_camera
    controller = px4
}
```

---

## 吸收三：Controller与仿真器分进程

算法不应该写死在仿真器内部。

---

## 吸收四：Supervisor

CoSim必须有独立：

```text
ExperimentSupervisor
```

负责：

```text
reset
spawn
randomize
record
evaluate
terminate
```

---

## 吸收五：设备统一API

例如：

```text
SensorBase
MotorBase
JointBase
```

不同后端都通过统一设备接口。

---

## 吸收六：基础时间步

所有后端都应明确：

```text
physics_step
control_step
sensor_step
render_step
```

---

## 吸收七：外部Controller模式

算法应支持：

```text
本地进程
远程进程
容器
另一台机器
```

---

## 吸收八：资产浏览体系

CoSim长期可以建立类似：

```text
cosim.assets
```

管理：

```text
车辆
传感器
地图
控制器
场景
```

---

# 40.31 我们不应该照搬什么？

## 不照搬一：不要让PROTO成为全平台唯一模型格式

CoSim还有：

```text
URDF
SDF
MJCF
JSBSim XML
UE Assets
```

应该维护中立参数源。

---

## 不照搬二：不要让每个机器人必然启动独立进程

小规模仿真可以这样做。

大规模仿真应允许：

```text
同进程批量控制
线程池
GPU Policy
集中式Swarm Controller
```

---

## 不照搬三：不要让场景树对象直接成为公共接口

Webots Node只属于Webots后端。

CoSim公共层应使用：

```text
Entity
RobotModel
SensorDescription
VehicleState
```

---

## 不照搬四：不要依赖Webots真值传感器做最终验证

需要加入真实噪声、延迟和失效模型。

---

## 不照搬五：不要让Webots替代Gazebo主链

对于当前PX4、MID360、FAST-LIO2和SUPER路线，Gazebo仍然更合适。

---

# 40.32 Webots在CoSim中的位置

推荐结构：

```text
                            CoSim Core
        Model / State / Sensor / Clock / Scenario / Logger
                                  │
          ┌─────────────┬─────────┼──────────┬─────────────┐
          ▼             ▼         ▼          ▼             ▼
     GazeboBackend  WebotsBackend MuJoCo  JSBSimBackend  UEFrontend
        工程主干      快速原型       RL       航空动力学     高保真显示
```

WebotsBackend主要承担：

```text
教育和教学
快速原型
普通轮式机器人
机械臂
多类型机器人演示
跨平台算法测试
ROS2 Nav2测试
轻量多机器人场景
```

而不是：

```text
Sunray-150最终PX4仿真
MID360最高保真仿真
UE高真实感前端
大规模GPU训练
```

---

# 40.33 Webots Backend接口建议

```text
IWebotsBackend
├─ loadWorld()
├─ resetWorld()
├─ step()
├─ spawnProto()
├─ removeNode()
├─ getRobot()
├─ getDevice()
├─ setController()
├─ setSupervisor()
├─ startRecording()
└─ exportAnimation()
```

统一机器人描述：

```text
RobotDefinition
├─ model
├─ pose
├─ controller
├─ sensors
├─ actuators
├─ collision
└─ physics
```

统一实验监督：

```text
ExperimentSupervisor
├─ reset()
├─ randomize()
├─ setGoal()
├─ getGroundTruth()
├─ evaluate()
└─ terminate()
```

---

# 40.34 推荐的运行模式

## 模式一：纯Webots快速开发

```text
Webots World
    +
Webots Controller
```

适合：

```text
入门
教学
算法验证
快速调试
```

---

## 模式二：ROS2模式

```text
Webots
    ↓
webots_ros2_driver
    ↓
ROS2
    ↓
Nav2 / SLAM / Control
```

适合：

```text
ROS2导航
机械臂控制
多机器人
```

---

## 模式三：外部Controller模式

```text
Webots Server
    ↓ TCP
External Controller
```

适合：

```text
IDE调试
远程计算
容器化算法
```

---

## 模式四：CoSim适配模式

```text
CoSim Scenario
    ↓
WebotsBackend
    ↓
统一VehicleState / SensorData
```

适合：

```text
跨仿真器算法对比
```

---

# 40.35 对当前无人机项目的判断

针对：

```text
Sunray-150
MID360
PX4
FAST-LIO2
SUPER
ROS2
```

Webots不应该替代：

```text
Gazebo
```

但可以作为一个非常有价值的第二验证平台。

例如：

```text
同一套ROS2规划算法
    ├─ Gazebo运行
    └─ Webots运行
```

如果算法在两个不同物理与传感器实现中都能工作，说明系统不太可能只对某一个仿真器过拟合。

Webots可以用于：

```text
简单无人机避障
控制算法教学
规划算法快速验证
多机器人通信测试
地图与场景随机化
```

不适合第一阶段承担：

```text
PX4完整SITL
MID360高保真扫描
FAST-LIO2最终验证
高速SUPER导航
```

---

# 40.36 最小研究任务

```text
1. 安装Webots R2025a
2. 跑通官方Guided Tour
3. 理解Scene Tree
4. 理解WorldInfo和basicTimeStep
5. 创建一个简单.wbt世界
6. 创建Solid、Shape和Physics
7. 分离visual和boundingObject
8. 创建两轮机器人
9. 加入RotationalMotor
10. 加入Camera和Lidar
11. 编写Python Controller
12. 理解robot.step()
13. 使用同一Controller控制多台机器人
14. 编写Supervisor
15. 用Supervisor随机生成障碍物
16. 创建第一个PROTO
17. 理解PROTO字段和实例化
18. 从webots.cloud导入机器人
19. 导入URDF
20. 导出Webots机器人URDF
21. 运行Fast和No Rendering模式
22. 跑通extern Controller
23. 跑通远程extern Controller
24. 安装webots_ros2
25. 跑通TurtleBot/Nav2示例
26. 理解webots_ros2_driver
27. 理解Ros2Supervisor
28. 创建简单四旋翼模型
29. 加入IMU、GPS和Camera
30. 研究PX4 MAVLink桥接可行性
31. 将Webots状态转换为CoSim统一接口
32. 写Webots REVIEW.md
```

---

# 40.37 第一阶段成功标准

```text
世界：
    能独立创建和修改.wbt世界

模型：
    能创建参数化PROTO机器人

物理：
    碰撞、质量、摩擦和关节工作正常

传感器：
    Camera、LiDAR、IMU、GPS能够输出

控制：
    Python和C++ Controller能够运行

监督：
    Supervisor能够重置和随机化场景

ROS2：
    能发布传感器、TF和JointState

自动化：
    能无渲染快速运行批量实验

平台：
    能输出CoSim统一RobotState和SensorData
```

---

# 40.38 Webots REVIEW.md 应该写什么

```text
1. 项目定位
    集成式通用机器人仿真平台

2. 当前版本
    R2025a
    Apache 2.0
    资产需单独检查许可证

3. 它解决什么问题
    机器人模型
    世界编辑
    物理
    传感器
    控制器
    ROS2
    自动实验

4. 核心架构
    WBT
    Node Tree
    PROTO
    Controller
    Supervisor
    ODE
    WREN

5. 项目结构
    worlds
    protos
    controllers
    plugins
    libraries

6. 传感器和执行器
    Camera
    Lidar
    IMU
    GPS
    Motor
    Joint

7. ROS2
    webots_ros2_driver
    webots_ros2_control
    Ros2Supervisor

8. 我们吸收什么
    PROTO
    Supervisor
    设备API
    控制器分进程
    固定时间步
    资产体系

9. 不照搬什么
    PROTO唯一模型源
    每机器人独立进程
    Webots Node作为核心接口
    Webots替代Gazebo主干

10. 在CoSim中的位置
    快速原型与教学仿真后端
```

---

# 40.39 对Webots的最终判断

```text
是否进入CoSim：
    是

是否作为默认主后端：
    否

进入哪一层：
    通用机器人快速仿真后端
    教学和算法原型后端
    ROS2功能验证后端

主要优势：
    一体化
    易上手
    PROTO资产
    Supervisor
    多语言Controller
    ROS2
    跨平台

主要不足：
    ODE物理较传统
    单线程物理
    渲染不及UE
    PX4非官方主线
    不适合大规模GPU训练
    无人机高保真能力一般

最适合：
    轮式机器人
    机械臂
    教育机器人
    服务机器人
    Nav2
    多机器人演示
    简单无人机控制

不承担：
    UE高保真视觉
    JSBSim航空动力学
    MuJoCo大规模RL
    Gazebo PX4/MID360工程主链
```

最核心的一句话是：

> **Webots最值得CoSim吸收的，不是某个物理算法，而是它如何把世界、机器人、设备、控制器、PROTO资产和实验Supervisor整合成一个低门槛但完整的机器人开发环境。它不应该替代Gazebo，而应该成为CoSim中用于快速原型、教学、ROS2测试和跨仿真器验证的轻量通用后端。**
>
