# 38. 项目概述：JSBSim

## 38.1 定位

JSBSim 是一个面向航空器的开源飞行动力学模型库，英文全称可以理解为：

```text
JSB Flight Dynamics Model
```

它不是完整的三维飞行模拟器，也不是类似 Gazebo、AirSim、FlightGear 的完整虚拟世界。它的核心定位是：

> **根据航空器质量、惯量、气动系数、发动机、操纵面、起落架、环境和控制输入，计算航空器下一时刻的位置、姿态、速度和角速度。**

JSBSim 是一个用 C++ 编写的、数据驱动的、非线性六自由度飞行动力学内核。它既可以独立以批处理或软实时方式运行，也可以被嵌入 FlightGear、Unreal Engine、MATLAB/Simulink、Python 或其他仿真平台。具体飞机通常不写死在 C++ 中，而是通过 XML 文件描述。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/ "JSBSim Flight Dynamics Model: JSBSim"))

截至  **2026年6月14日** ，JSBSim 官方最新发布版本是  **1.3.1，发布于2026年5月17日** 。官方提供 Windows 安装程序、Ubuntu 22.04/24.04 软件包以及 Python 3.10—3.14 的 wheel。([GitHub](https://github.com/JSBSim-Team/jsbsim?utm_source=chatgpt.com "GitHub - JSBSim-Team/jsbsim: An open source flight dynamics &amp; control software library · GitHub"))

对 CoSim 来说，JSBSim 最合理的位置是：

```text
固定翼动力学后端
大型无人机动力学后端
复合翼 / VTOL动力学研究后端
火箭与航空航天器动力学后端
飞控和控制律验证后端
```

而不是：

```text
高真实感地图系统
LiDAR仿真器
ROS2机器人传感器平台
无人机三维规划器
默认四旋翼工程仿真后端
```

---

## 38.2 最容易产生的误解

JSBSim名称里虽然有“Sim”，但它本身更接近：

```text
一套航空器动力学计算库
```

而不是：

```text
一个带机场、天空、驾驶舱和画面的游戏
```

可以把完整飞行模拟器拆成：

```text
┌─────────────────────────────────┐
│        地图、地形、天空和画面      │
│      FlightGear / UE / 其他引擎   │
└─────────────────▲───────────────┘
                  │ 位姿
┌─────────────────┴───────────────┐
│             JSBSim              │
│ 气动 / 发动机 / 质量 / 运动方程   │
└─────────────────▲───────────────┘
                  │ 控制输入
┌─────────────────┴───────────────┐
│  飞行员 / PX4 / 自研控制器 / RL   │
└─────────────────────────────────┘
```

所以：

```text
FlightGear：
    让你看见飞机和世界

JSBSim：
    决定飞机为什么这样运动
```

JSBSim最初就是为FlightGear而创建，但它一直保持独立运行和嵌入其他平台的能力。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/ "JSBSim Flight Dynamics Model: JSBSim"))

---

# 38.3 核心设计理念

| 设计原则       | 说明                                             |
| -------------- | ------------------------------------------------ |
| 专用航空动力学 | 重点解决飞机、旋翼机和航天器六自由度运动         |
| 数据驱动       | 飞机参数主要写在XML中，而不是重新编译C++         |
| 力和力矩统一   | 气动、发动机、重力、起落架等最终都转换成力和力矩 |
| 非线性六自由度 | 同时求解三维平移和三维旋转                       |
| 航空环境建模   | 包含大气、重力、地球自转和WGS84地理坐标          |
| 模块化子模型   | 气动、推进、质量、地面反力、控制系统分别建模     |
| Property Tree  | 所有模块通过统一属性树交换状态和控制量           |
| 无渲染依赖     | 可以完全无界面运行，适合批量仿真和控制研究       |
| 多语言接口     | 提供C++、Python、MATLAB/Simulink等接口           |
| 可嵌入         | 可以作为FlightGear、UE或其他平台中的物理内核     |

JSBSim官方将其定义为轻量、数据驱动、非线性六自由度飞行动力学应用；其航空器模型通过JSBSim-ML格式描述，而不是针对每架飞机编写专用程序代码。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/?utm_source=chatgpt.com "Home - JSBSim Manual"))

---

# 38.4 系统设计逻辑

## 38.4.1 第一性原理：飞行动力学模拟到底在算什么？

航空器运动的本质是：

```text
所有力
    ↓
产生线加速度

所有力矩
    ↓
产生角加速度
```

平移动力学可以简化写成：

```text
m(v̇ + ω × v) = F
```

旋转动力学可以简化写成：

```text
Iω̇ + ω × (Iω) = M
```

其中：

```text
m：
    航空器质量

I：
    转动惯量矩阵

v：
    机体速度

ω：
    机体角速度

F：
    所有外力总和

M：
    所有外力矩总和
```

JSBSim的工作就是在每个仿真时间步中：

```text
读取当前状态和控制输入
        ↓
计算大气状态和空速
        ↓
计算气动力与气动力矩
        ↓
计算发动机推力与反作用力矩
        ↓
计算重力和地面接触力
        ↓
累加所有力和力矩
        ↓
求解加速度与角加速度
        ↓
数值积分
        ↓
得到新位置、速度和姿态
```

官方对JSBSim的描述也是：接受控制输入，计算环境和控制造成的力与力矩，并以离散时间步推进速度、姿态和位置状态。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/user/overview/?utm_source=chatgpt.com "Overview - JSBSim Manual"))

---

## 38.4.2 第二性原理：为什么航空器需要专门的动力学引擎？

一个普通刚体引擎天然知道：

```text
质量
惯量
重力
碰撞
外力
```

但它并不知道：

```text
机翼迎角变化后升力怎么变化
失速以后升力和阻力如何变化
升降舵偏转产生多大俯仰力矩
侧滑角如何产生侧向力
螺旋桨在不同空速下产生多少推力
喷气发动机推力如何随高度变化
地面效应如何改变气动力
```

这些航空器特性不能仅靠“机翼是一个Mesh”自动算出来。

Gazebo或UE看到的是：

```text
一块机翼形状的几何体
```

JSBSim看到的是：

```text
CL(α, δe, Mach, ...)
CD(α, β, Mach, ...)
Cm(α, q, δe, ...)
```

也就是：

```text
升力系数
阻力系数
俯仰力矩系数
侧向力系数
滚转力矩系数
偏航力矩系数
```

因此JSBSim的核心优势不在接触物理，而在 **航空气动和飞行力学模型组织方式** 。

---

## 38.4.3 第三性原理：为什么飞机模型写在XML，而不是C++？

如果每增加一架飞机都要修改：

```text
AircraftA.cpp
AircraftB.cpp
AircraftC.cpp
```

会导致：

```text
代码和飞机数据绑死
无法由气动工程师独立修改
改变一个系数也需要重新编译
难以批量生成机型
```

JSBSim的做法是：

```text
通用C++动力学求解器
        +
每架航空器的XML数据
```

例如一架飞机的模型文件会描述：

```text
尺寸
参考机翼面积
翼展
平均气动弦长
质量
重心
惯量
发动机
油箱
起落架
操纵面
气动系数
控制系统
```

这样同一个动力学内核可以加载：

```text
Cessna 172
F-16
波音737
大型运输机
四旋翼
直升机
火箭
```

而不需要为每种航空器重新编译内核。官方文档明确说明，JSBSim不在程序代码中硬编码具体航空器，而使用XML定义质量、几何、推进、控制系统和气动稳定导数。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/ "JSBSim Flight Dynamics Model: JSBSim"))

---

## 38.4.4 第四性原理：为什么需要Property Tree？

大型航空器模型中可能有成百上千个变量：

```text
当前高度
空速
迎角
发动机转速
襟翼角度
升降舵指令
自动驾驶输出
燃油重量
起落架压缩量
```

如果所有模块都通过专用C++接口互相调用：

```text
Aerodynamics.getAngleOfAttack()
Engine.getRPM()
Autopilot.setElevator()
```

随着系统扩展，模块之间会严重耦合。

JSBSim使用类似文件系统的属性树：

```text
position/h-sl-ft
velocities/vc-kts
aero/alpha-rad
fcs/elevator-cmd-norm
propulsion/engine[0]/rpm
```

任意模块、脚本、Python程序、网络接口或UE蓝图，都可以通过属性名称读取或写入值。

可以理解为：

```text
Property Tree
    =
航空器内部的统一数据总线
```

JSBSim Property Manager允许运行时动态创建属性，飞控组件、脚本和外部程序均可通过统一的层级属性名交换数据。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/user/concepts/properties/ "Properties - JSBSim Manual"))

---

# 38.5 JSBSim 的整体架构

```text
控制输入
├─ 副翼
├─ 升降舵
├─ 方向舵
├─ 油门
├─ 襟翼
├─ 起落架
└─ 电机命令
        │
        ▼
Flight Control System
├─ 增益
├─ 滤波器
├─ PID
├─ 开关
├─ 限幅
└─ 控制分配
        │
        ▼
┌──────────────────────────────────────┐
│              物理子模型               │
│                                      │
│  Atmosphere       大气               │
│  Winds            风场               │
│  Mass Balance     质量、重心、惯量    │
│  Aerodynamics     气动力和气动力矩    │
│  Propulsion       发动机和推力系统    │
│  Ground Reactions 起落架与地面反力    │
│  External Forces  外部附加力          │
└─────────────────┬────────────────────┘
                  ▼
             力和力矩累加
                  │
                  ▼
             Accelerations
                  │
                  ▼
               Propagate
        位置、速度、姿态数值积分
                  │
                  ▼
              Aircraft State
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Property Tree          Output / Socket
```

JSBSim中的核心调度对象是：

```text
FGFDMExec
```

它负责加载模型、初始化各子模块并逐步执行仿真；其公开接口可以访问气动、推进、质量平衡、地面反力等主要模块。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/python/FGFDMExec.html?utm_source=chatgpt.com "FGFDMExec — JSBSim 1.3.1 documentation"))

---

# 38.6 主要物理子模块

## 38.6.1 Atmosphere：大气模型

大气模型为飞行动力学提供：

```text
空气密度
温度
气压
声速
黏度
```

这些量会随：

```text
高度
温度偏差
天气条件
```

变化。

气动力一般包含动压：

```text
q̄ = 1/2 ρV²
```

因此：

```text
空气密度变小
    ↓
相同空速下动压变小
    ↓
升力、阻力和操纵面效果变化
```

JSBSim还包含地球旋转、科里奥利效应、离心加速度、椭球地球和WGS84地理坐标等模型，因此比只在一个局部平面中飞行的简单刚体模型更适合长距离和高空航空器。([GitHub](https://github.com/JSBSim-Team/jsbsim?utm_source=chatgpt.com "GitHub - JSBSim-Team/jsbsim: An open source flight dynamics &amp; control software library · GitHub"))

---

## 38.6.2 Mass Balance：质量、重心和惯量

质量模块管理：

```text
空机重量
燃油重量
乘员
货物
外挂载荷
重心位置
惯量矩阵
```

当燃油消耗或载荷变化时：

```text
总质量变化
重心变化
惯量变化
```

飞行特性也会随之变化。

JSBSim的FGMassBalance不仅计算总质量，还维护惯量矩阵、逆惯量矩阵和各点质量对惯量的贡献。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/classJSBSim_1_1FGMassBalance.html?utm_source=chatgpt.com "JSBSim Flight Dynamics Model: FGMassBalance Class Reference"))

对CoSim来说，这非常适合模拟：

```text
载荷投放
燃油消耗
货物位置变化
重心偏移故障
传感器或吊舱外挂
```

---

## 38.6.3 Aerodynamics：气动力模型

典型固定翼升力可以写成：

```text
L = q̄ S CL
```

阻力为：

```text
D = q̄ S CD
```

俯仰力矩为：

```text
M = q̄ S c̄ Cm
```

其中系数不是固定值，而可能依赖：

```text
迎角 α
侧滑角 β
马赫数
副翼偏转
升降舵偏转
方向舵偏转
角速度 p、q、r
襟翼状态
起落架状态
```

JSBSim允许通过函数和一维、二维或三维查表定义这些系数，因此可以直接把风洞数据、飞行试验数据或公开气动模型转成查表形式。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/user/concepts/math/?utm_source=chatgpt.com "Math - JSBSim Manual"))

一个简化的气动定义可以理解为：

```xml
<aerodynamics>
  <axis name="LIFT">
    <function name="aero/force/Lift">
      <product>
        <property>aero/qbar-psf</property>
        <property>metrics/Sw-sqft</property>
        <table>
          <independentVar>aero/alpha-rad</independentVar>
          ...
        </table>
      </product>
    </function>
  </axis>
</aerodynamics>
```

它表达的是：

```text
读取迎角
    ↓
查找升力系数
    ↓
乘以动压和机翼面积
    ↓
得到升力
```

---

## 38.6.4 Propulsion：推进系统

JSBSim把推进系统拆成：

```text
Engine：
    产生机械功率或喷流能量

Thruster：
    将功率转换为实际推力
```

例如：

```text
活塞发动机
    ↓
螺旋桨
    ↓
推力

涡轮发动机
    ↓
喷口
    ↓
推力

无刷电机
    ↓
旋翼/螺旋桨
    ↓
推力
```

当前JSBSim引擎类型包括活塞、涡轮、涡桨、火箭和电动发动机；最新代码还包含无刷直流电机模型。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/classJSBSim_1_1FGBrushLessDCMotor.html?utm_source=chatgpt.com "JSBSim Flight Dynamics Model: FGBrushLessDCMotor Class Reference"))

推进系统还可以管理：

```text
多个发动机
多个油箱
油箱到发动机的供油关系
燃油消耗
氧化剂
推力位置
推力方向
```

FGPropulsion会根据XML创建发动机和油箱，并在每个运行周期调用各发动机模型计算推力和消耗。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/python/FGPropulsion.html?utm_source=chatgpt.com "FGPropulsion — JSBSim 1.3.1 documentation"))

---

## 38.6.5 Ground Reactions：起落架和地面接触

JSBSim可以定义：

```text
主起落架位置
前轮或尾轮位置
轮胎刚度
阻尼
摩擦
制动
转向
结构接触点
```

它适合模拟：

```text
滑跑
起飞
着陆
刹车
起落架压缩
地面转弯
硬着陆
```

但它不是一个通用复杂碰撞引擎。

例如：

```text
飞机撞上复杂建筑
机翼断裂
多物体碎片碰撞
柔性结构破坏
```

并不是JSBSim的主要目标。

FGGroundReactions是JSBSim的独立调度模型，专门处理地面接触与反力。([JSBSim Team](https://jsbsim-team.github.io/jsbsim/classJSBSim_1_1FGGroundReactions.html?utm_source=chatgpt.com "JSBSim Flight Dynamics Model: FGGroundReactions Class Reference"))

---

## 38.6.6 External Reactions：外部附加力

JSBSim还允许外部系统施加：

```text
外部力
外部力矩
挂载力
缆绳力
弹射器力
阻拦索力
空气动力之外的扰动力
```

这对CoSim非常重要。

我们可以从外部注入：

```text
随机阵风
外挂吊载摆动力
碰撞冲量
故障附加力矩
编队尾流影响
甲板弹射力
```

而无需直接修改航空器核心模型。

---

# 38.7 Flight Control System：配置式控制系统

JSBSim不只模拟物理，还允许使用XML搭建飞控和航空器系统。

可以使用的基本组件包括：

```text
增益
求和器
限幅器
死区
开关
PID
积分器
滤波器
查表
传感器
延迟
控制面缩放
```

例如升降舵控制链可以写成：

```text
驾驶杆指令
    ↓
与配平指令求和
    ↓
限幅
    ↓
缩放为舵面角度
    ↓
升降舵实际偏角
```

JSBSim官方手册展示了使用summer、aerosurface_scale和pure_gain等组件，以属性连接的方式搭建飞控通道；同一套组件也可以构建自动驾驶和其他航空器系统。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/user/concepts/properties/ "Properties - JSBSim Manual"))

这意味着JSBSim内部可以同时存在两种使用方式。

### 方式一：内部控制器

```text
飞行员指令
    ↓
JSBSim XML Flight Control System
    ↓
操纵面
```

### 方式二：外部控制器

```text
PX4 / Simulink / C++ Controller
    ↓
直接写JSBSim控制属性
    ↓
操纵面和发动机
```

对CoSim来说，第二种更重要，因为我们需要比较：

```text
PX4控制器
Simulink生成控制器
自研MPC
强化学习控制器
JSBSim内部基线控制器
```

---

# 38.8 JSBSim 的模型文件体系

一个完整项目通常包含：

```text
aircraft/
engine/
systems/
scripts/
```

官方发行包和MATLAB接口也明确依赖这些目录。([GitHub](https://github.com/JSBSim-Team/jsbsim/blob/master/matlab/README.md "jsbsim/matlab/README.md at master · JSBSim-Team/jsbsim · GitHub"))

---

## 38.8.1 aircraft：航空器主模型

主航空器XML通常包含：

```text
metrics
    几何参考量

mass_balance
    质量、重心、惯量

ground_reactions
    起落架和接触点

propulsion
    发动机、油箱和推力器

flight_control
    操纵系统

system
    其他航空器系统

aerodynamics
    气动力和力矩
```

目录结构可以是：

```text
aircraft/
└─ custom_uav/
   ├─ custom_uav.xml
   ├─ custom_fcs.xml
   └─ custom_system.xml
```

---

## 38.8.2 engine：发动机与螺旋桨

推进系统通常拆成：

```text
发动机模型
    +
推力器模型
```

例如螺旋桨飞机可能需要：

```text
engine/
├─ motor.xml
└─ propeller.xml
```

官方Aeromatic说明，一个完整航空器至少需要主航空器文件和发动机文件；螺旋桨飞机还需要独立的螺旋桨定义。([JSBSim Team](https://jsbsim-team.github.io/aeromatic/?utm_source=chatgpt.com "Aeromatic for the JSBSim Open Source Flight Dynamics Model"))

---

## 38.8.3 systems：可复用系统

`systems`适合存放：

```text
自动驾驶
飞控通道
液压系统
电气系统
起落架逻辑
襟翼逻辑
发动机控制
```

这样多个航空器可以复用同一套控制或系统模型。

---

## 38.8.4 scripts：实验脚本

Script文件描述：

```text
加载哪架飞机
初始高度
初始速度
经纬度
初始姿态
仿真步长
何时改变控制量
何时结束
记录哪些数据
```

例如：

```text
0秒：
    油门设为巡航

10秒：
    升降舵施加阶跃

20秒：
    恢复中立

60秒：
    结束实验
```

因此JSBSim很适合：

```text
开环响应测试
阶跃响应
配平分析
稳定性分析
控制器回归测试
参数扫描
```

---

# 38.9 Aeromatic 是什么？

Aeromatic是JSBSim配套的初始飞机模型生成器。

用户输入：

```text
飞机类型
重量
翼展
翼面积
发动机类型
发动机数量
大致性能
```

它生成：

```text
航空器XML
发动机XML
螺旋桨XML
```

当前JSBSim Windows安装包会同时安装 `aeromatic.exe`，官方也提供Web版Aeromatic。([GitHub](https://github.com/JSBSim-Team/jsbsim "GitHub - JSBSim-Team/jsbsim: An open source flight dynamics &amp; control software library · GitHub"))

但要正确理解：

> **Aeromatic生成的是模型起点，不是经过风洞和飞行试验验证的高保真最终模型。**

合理流程是：

```text
Aeromatic生成初始模型
        ↓
根据技术手册修正质量和惯量
        ↓
填入公开气动数据
        ↓
做配平和稳定性测试
        ↓
与实测飞行数据对比
        ↓
系统辨识和参数校正
```

---

# 38.10 配平 Trim 为什么重要？

对于固定翼，不能随便给一个速度和姿态就开始仿真。

稳定平飞要求：

```text
升力 ≈ 重力
推力 ≈ 阻力
俯仰力矩 ≈ 0
滚转力矩 ≈ 0
偏航力矩 ≈ 0
```

配平就是求解：

```text
迎角
油门
升降舵
副翼
方向舵
```

使航空器处于稳态。

如果初始状态没有配平：

```text
一开始就快速抬头
突然下坠
发动机推力不足
控制面需要很大补偿
```

JSBSim和官方Python示例支持配平包线、迎角—空速分析和不同飞行路径角下的配平研究。([GitHub](https://github.com/JSBSim-Team/jsbsim "GitHub - JSBSim-Team/jsbsim: An open source flight dynamics &amp; control software library · GitHub"))

对CoSim来说，需要建立：

```text
Trim Service
├─ level_flight
├─ climb
├─ descent
├─ coordinated_turn
└─ hover / VTOL equilibrium
```

---

# 38.11 JSBSim 与固定翼的关系

JSBSim最擅长的是：

```text
固定翼
喷气式飞机
螺旋桨飞机
大型无人机
高空长航时无人机
火箭
航天器
```

原因是它原生就围绕：

```text
气动系数
发动机
燃油
操纵面
大气
地球模型
配平
稳定性
```

组织。

如果CoSim未来要支持：

```text
垂直起降固定翼
倾转旋翼
飞翼无人机
大型物流无人机
低空载人航空器
eVTOL
```

JSBSim的价值会明显高于只使用简单刚体加几个经验外力。

---

# 38.12 JSBSim 与四旋翼的关系

JSBSim并不是只能模拟固定翼。

官方航空器目录中包含F450等旋翼机模型，当前推进系统还包含电机和旋翼相关实现；PX4的JSBSim仿真文档也列出四旋翼和六旋翼目标。([GitHub](https://github.com/JSBSim-Team/jsbsim/tree/master/aircraft "jsbsim/aircraft at master · JSBSim-Team/jsbsim · GitHub"))

但对于普通四旋翼，JSBSim并不一定是最合适的第一选择。

原因是四旋翼的基础模型相对直接：

```text
四个电机推力
    ↓
总推力和三轴力矩
    ↓
刚体运动
```

Gazebo、MuJoCo、AirSim甚至自研刚体求解器都能完成。

JSBSim的优势要在以下场景才更明显：

```text
旋翼气动较复杂
需要地球和大气模型
需要复合翼模式切换
需要固定翼和多旋翼统一模型
需要详细推进系统
需要航空器级飞控系统
```

因此对当前：

```text
Sunray-150 + MID360
```

主线而言，仍应优先使用：

```text
Gazebo：
    动力学、碰撞、LiDAR和PX4联调
```

JSBSim更适合作为后续：

```text
固定翼 / VTOL / 大型航空器后端
```

---

# 38.13 JSBSim 与复合翼 / VTOL 的关系

复合翼航空器同时存在：

```text
低速悬停阶段：
    旋翼主导

过渡阶段：
    旋翼和机翼共同作用

高速巡航阶段：
    机翼和前进发动机主导
```

JSBSim可以通过：

```text
多个发动机
多个推力器
气动查表
控制系统切换
状态相关函数
```

表达这种混合动力学。

例如：

```text
空速较低：
    垂直电机推力较大
    机翼升力较小

空速增加：
    机翼升力逐渐增加
    垂直电机逐渐降功率

进入巡航：
    前进发动机主导
```

这比在普通刚体引擎里手写大量条件判断更容易形成可配置、可追踪的航空器模型。

但高保真VTOL仍需要可靠的：

```text
过渡段气动数据
旋翼—机翼干扰
下洗影响
推进效率
舵面低速效率
```

JSBSim只提供表达和求解框架，不会自动生成这些数据。

---

# 38.14 JSBSim 与 PX4 的关系

JSBSim可以作为PX4 SITL的动力学后端：

```text
PX4
    ↓
电机 / 舵面控制输出
    ↓
JSBSim
    ↓
计算航空器运动
    ↓
模拟传感器 / 状态
    ↓
PX4
```

PX4现有文档列出：

```text
Standard Plane
Quadrotor
Hexarotor
```

并可选使用FlightGear显示。([PX4 文档](https://docs.px4.io/main/en/sim_jsbsim/index "JSBSim Simulation | PX4 Guide (main)"))

但必须注意，PX4官方当前明确将JSBSim仿真标记为：

```text
community supported
```

并提示它可能无法和当前PX4版本正常工作；现有ROS说明仍基于旧的ROS1 catkin和 `px4-jsbsim-bridge`。([PX4 文档](https://docs.px4.io/main/en/sim_jsbsim/index "JSBSim Simulation | PX4 Guide (main)"))

所以对CoSim来说，不应直接假定：

```text
PX4当前主分支
    +
旧px4-jsbsim-bridge
    =
开箱即用
```

更合理的是将JSBSim封装为自己的：

```text
JSBSimBackend
```

然后实现现代化的PX4适配层。

---

## 38.14.1 建议的PX4—JSBSim接口

```text
PX4输出
├─ actuator_motors
├─ actuator_servos
└─ vehicle commands
        │
        ▼
PX4JSBSimAdapter
├─ 电机归一化映射
├─ 舵面偏转映射
├─ 油门和混控映射
└─ 时间同步
        │
        ▼
JSBSim Properties
        │
        ▼
JSBSim Step
        │
        ▼
Truth State
├─ position
├─ velocity
├─ attitude
├─ angular rate
└─ acceleration
        │
        ▼
Sensor Simulator
├─ IMU
├─ GPS
├─ magnetometer
├─ barometer
└─ airspeed
        │
        ▼
PX4
```

这里必须把：

```text
JSBSim真值
```

和：

```text
PX4接收到的带噪传感器
```

区分开。

否则PX4会直接获得完美位置姿态，失去状态估计测试意义。

---

# 38.15 JSBSim 与 MATLAB / Simulink 的关系

JSBSim官方提供 MATLAB S-Function，可将JSBSim动力学模型作为Simulink中的被控对象。官方Windows安装程序包含相关构建资源，当前README还给出了Windows和macOS的编译与测试流程。([GitHub](https://github.com/JSBSim-Team/jsbsim/blob/master/matlab/README.md "jsbsim/matlab/README.md at master · JSBSim-Team/jsbsim · GitHub"))

典型链路：

```text
Simulink Controller
        │
        ▼
JSBSim S-Function
        │
        ▼
Aircraft State
        │
        └────反馈到控制器
```

这非常符合你现在的方向：

```text
MATLAB / Simulink：
    设计控制器
    调参
    稳定性分析
    生成控制代码

JSBSim：
    提供航空器被控对象
```

可以研究：

```text
姿态控制
高度控制
空速控制
航向控制
自动着陆
固定翼MPC
复合翼过渡控制
发动机失效控制
```

因此JSBSim对CoSim最大的一个实际价值，就是给未来固定翼和VTOL控制器提供一个比简化传递函数更完整的非线性航空器对象。

---

# 38.16 JSBSim 与 Python 的关系

官方Python包可以直接通过：

```text
pip install jsbsim
```

安装，并通过 `FGFDMExec`加载模型、设置属性、运行一个时间步和读取状态。官方wheel内包含默认航空器数据和示例脚本。([GitHub](https://github.com/JSBSim-Team/jsbsim "GitHub - JSBSim-Team/jsbsim: An open source flight dynamics &amp; control software library · GitHub"))

适合用于：

```text
批量参数扫描
蒙特卡洛仿真
控制器测试
强化学习
气动模型辨识
配平包线计算
故障注入
自动回归测试
```

Python模式下不需要启动任何三维画面：

```text
Python
    ↓
JSBSim
    ↓
数十倍或更高于实时速度运行
```

这比每次启动UE或FlightGear更适合算法开发。

---

# 38.17 JSBSim 与 Unreal Engine 的关系

JSBSim官方仓库包含一个UE5参考应用和 `JSBSimFlightDynamicsModel`插件。

该参考项目最初来自Epic Games的Antoinette Project，目的是展示UE5的双精度坐标和图形能力可以用于严肃飞行模拟，并通过插件将JSBSim封装进UE。当前README声明该示例兼容UE5.0至UE5.6。([GitHub](https://github.com/JSBSim-Team/jsbsim/tree/master/UnrealEngine "jsbsim/UnrealEngine at master · JSBSim-Team/jsbsim · GitHub"))

其结构大致是：

```text
UE5
├─ 飞机Mesh
├─ 地形
├─ 相机
├─ 驾驶舱
├─ 输入
└─ JSBSim Plugin
      ├─ 动态库
      ├─ aircraft模型
      ├─ engine模型
      └─ system模型
```

运行链路：

```text
UE输入
    ↓
写入JSBSim Property
    ↓
JSBSim执行动力学步
    ↓
读取经纬度、姿态和速度
    ↓
更新UE Aircraft Actor
```

官方参考应用将JSBSim以伪固定的120 Hz运行，通过在每个游戏帧中执行若干动力学子步，使动力学频率与渲染帧率解耦。([GitHub](https://github.com/JSBSim-Team/jsbsim/tree/master/UnrealEngine "jsbsim/UnrealEngine at master · JSBSim-Team/jsbsim · GitHub"))

---

## 38.17.1 对我们UE架构的启发

UE不应该自己用Tick直接积分飞机动力学：

```text
错误：

UE Tick
    ↓
随帧率变化的动力学计算
```

正确方式：

```text
固定步长Physics Clock
    ↓
JSBSim Step若干次
    ↓
得到最新状态
    ↓
UE只插值和显示
```

因此CoSim的UE前端可以直接参考官方插件的：

```text
动态库封装
资源模型打包
Property访问
固定频率动力学
Actor状态同步
```

不过我们的长期设计仍应让JSBSim位于统一Physics Backend层，而不是让它永远只能嵌入UE插件。

---

# 38.18 JSBSim 与 FlightGear 的关系

FlightGear是JSBSim最经典的显示前端。

```text
JSBSim：
    飞机如何运动

FlightGear：
    地球、机场、天空、驾驶舱和画面
```

JSBSim会把：

```text
经度
纬度
高度
滚转
俯仰
偏航
操纵面状态
发动机状态
```

传给FlightGear，FlightGear负责显示。

对于CoSim，FlightGear的价值主要是：

```text
快速验证固定翼模型
观察航空器运动
使用成熟机场和地球场景
无需先开发UE前端
```

但长期高保真前端仍可以是UE。

---

# 38.19 JSBSim 与 Gazebo 的区别

| 维度       | JSBSim                         | Gazebo                 |
| ---------- | ------------------------------ | ---------------------- |
| 核心定位   | 航空器飞行动力学               | 通用机器人系统仿真     |
| 气动       | 强，数据驱动气动系数           | 通常依赖插件或简化模型 |
| 发动机     | 航空发动机、油箱、螺旋桨较完整 | 通常自行建模           |
| 地球模型   | WGS84、地球旋转、高空飞行      | 通常局部世界           |
| 接触碰撞   | 起落架和地面反力为主           | 通用三维碰撞与接触更强 |
| LiDAR/相机 | 不负责                         | 工程传感器生态强       |
| ROS2       | 非核心，需要适配               | 原生生态较成熟         |
| PX4        | 有社区接口                     | 当前主流工程后端       |
| 固定翼     | 强                             | 取决于气动插件         |
| 多机器人   | 不是首要目标                   | 更自然                 |
| 地图       | 没有高保真世界                 | 支持SDF世界和传感器    |

所以不是：

```text
JSBSim替代Gazebo
```

而是：

```text
固定翼 / 航空器：
    JSBSim动力学更专业

机器人传感器 / 碰撞 / ROS2：
    Gazebo更完整
```

---

# 38.20 JSBSim 与 MuJoCo 的区别

| 维度         | JSBSim                 | MuJoCo                 |
| ------------ | ---------------------- | ---------------------- |
| 核心对象     | 航空器                 | 通用多关节刚体         |
| 气动体系     | 原生航空气动系数和查表 | 需要自行实现           |
| 接触         | 起落架等航空接触       | 通用接触和约束更强     |
| 多关节机器人 | 非重点                 | 强                     |
| 强化学习     | 可用Python接口         | MJX批量训练更强        |
| 飞行控制研究 | 固定翼、VTOL非常合适   | 四旋翼、机械系统更自然 |
| 发动机与燃油 | 原生航空模型           | 通常自定义             |
| 地球与大气   | 强                     | 通常简化               |
| GPU批量      | 非主要方向             | MJX/Warp强             |

因此：

```text
JSBSim：
    航空器专业模型

MuJoCo：
    通用控制与强化学习高速模型
```

CoSim应同时保留，两者解决的问题不同。

---

# 38.21 JSBSim 与 AirSim 的区别

| 维度       | JSBSim         | AirSim                  |
| ---------- | -------------- | ----------------------- |
| 本质       | 飞行动力学库   | UE无人机/汽车仿真平台   |
| 渲染       | 无             | UE                      |
| 地图       | 无             | UE地图                  |
| 视觉传感器 | 无             | 强                      |
| 气动模型   | 航空系数体系强 | 主要服务无人机/车辆仿真 |
| 固定翼     | 强             | 非核心                  |
| PX4        | 有社区桥接     | 有历史SITL/HITL支持     |
| Python API | 操作动力学属性 | 控制车辆和读取传感器    |
| 适合用途   | 飞行性能和控制 | 视觉、场景与自主系统    |

二者可以组合成类似：

```text
JSBSim：
    固定翼动力学

UE / AirSim式前端：
    相机、地图和显示
```

---

# 38.22 JSBSim 的时间管理

JSBSim每次执行：

```text
Run()
```

就按配置的：

```text
Δt
```

推进一个动力学时间步。

它可以：

```text
实时运行
慢于实时运行
快于实时批处理运行
由外部程序一步一步调用
```

对CoSim最正确的设计是：

```text
SimulationClock
    ↓
确定本次需要推进的step数量
    ↓
JSBSim.Run()
    ↓
发布带统一仿真时间戳的状态
```

不要让：

```text
UE帧率
ROS2消息到达速度
显示器刷新率
```

决定动力学时间。

推荐时间结构：

```text
JSBSim Physics：
    120～1000 Hz，视航空器和控制需求

PX4 / Controller：
    50～400 Hz

传感器：
    各自独立频率

UE Rendering：
    30～120 Hz
```

这些频率应共享同一个仿真时钟，但不必相同。

---

# 38.23 坐标系问题

JSBSim使用典型航空坐标约定。

局部导航坐标通常包含：

```text
North
East
Down
```

机体速度和角速度使用航空器机体系，方向类似：

```text
X：
    向前

Y：
    向右

Z：
    向下
```

此外，航空器XML中几何位置还使用结构坐标系，结构原点不一定就是重心。JSBSim官方手册专门区分结构坐标系、机体坐标系、局部坐标系和气动坐标系。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/user/concepts/frames-of-reference/?utm_source=chatgpt.com "Frames of reference - JSBSim Manual"))

这与PX4较接近：

```text
PX4：
    NED + FRD
```

但与ROS2常见的：

```text
ENU + FLU
```

不同。

所以CoSim必须统一转换：

```text
JSBSim NED / Body
        ↓
Coordinate Adapter
        ↓
ROS2 ENU / FLU
        ↓
UE左手坐标
```

不能只交换三个位置数值而不交换坐标语义。

---

# 38.24 模型精度取决于数据，不取决于引擎名字

使用JSBSim不代表飞机自动高保真。

模型精度取决于：

```text
质量和惯量是否准确
重心是否准确
气动导数是否准确
失速数据是否准确
发动机模型是否准确
螺旋桨模型是否准确
操纵面效率是否准确
起落架参数是否准确
```

官方发行包中的真实机型名称模型也主要来自公开教材、技术报告、NASA文档和公开数据，并明确属于教育或娱乐用途的近似模型，不应默认等同于制造商认证数据。([JSBSim Team](https://jsbsim-team.github.io/jsbsim-reference-manual/user/?utm_source=chatgpt.com "User Manual - JSBSim Manual"))

因此建模流程必须包括：

```text
公开资料初始模型
    ↓
气动软件或风洞数据
    ↓
实机静态参数
    ↓
飞行数据
    ↓
系统辨识
    ↓
模型验证
```

---

# 38.25 我们应该吸收JSBSim哪些设计？

## 吸收一：动力学内核与显示彻底分离

```text
Physics Backend
    不知道UE画面

UE Renderer
    不负责积分飞行动力学
```

---

## 吸收二：航空器模型数据驱动

CoSim可以定义中立航空器模型：

```text
AircraftModel
├─ Geometry
├─ MassProperties
├─ Aerodynamics
├─ Propulsion
├─ LandingGear
├─ ControlEffectors
└─ Systems
```

再生成：

```text
JSBSim XML
Gazebo SDF插件参数
MuJoCo MJCF
UE可视资产配置
```

---

## 吸收三：Property Tree

CoSim可以设计统一属性系统：

```text
vehicle/velocity
vehicle/angle_of_attack
engine/0/rpm
actuator/elevator
environment/wind
```

用于：

```text
调试
脚本
故障注入
UI
日志
控制器
```

---

## 吸收四：推进系统模块化

不要把：

```text
发动机
螺旋桨
油箱
电池
电机
```

全部写在一个对象中。

应拆为：

```text
EnergySource
Engine / Motor
Transmission
Thruster
```

---

## 吸收五：脚本化实验

CoSim应支持：

```text
10秒时发动机失效
20秒时侧风增加
30秒时切换自动驾驶
40秒时投放载荷
```

而不是每次手动操作。

---

## 吸收六：配平与性能分析

航空器后端必须提供：

```text
trim()
linearize()
sweep()
simulate_step_response()
```

否则只能“飞起来看看”，无法做严肃控制研究。

---

## 吸收七：统一日志属性

通过属性选择需要记录的数据：

```text
位置
速度
迎角
侧滑角
升阻力
舵偏
发动机状态
控制器输出
```

而不是在代码里到处插打印语句。

---

# 38.26 我们不应该照搬什么？

## 不照搬一：不要让XML成为CoSim唯一模型源

JSBSim使用XML很合理，但CoSim还有：

```text
Gazebo SDF
MuJoCo MJCF
ROS URDF
UE资产
```

长期应维护中立参数源，再生成JSBSim XML。

---

## 不照搬二：不要把Property Tree变成无类型全局变量仓库

JSBSim属性灵活，但大型平台如果完全靠字符串：

```text
position/h-sl-ft
```

容易出现：

```text
拼写错误
单位错误
运行时才发现错误
难以重构
```

CoSim核心接口仍应有：

```text
强类型C++数据结构
```

Property Tree作为：

```text
配置、脚本和调试层
```

---

## 不照搬三：不要让JSBSim负责机器人传感器

JSBSim输出真值后，应交给独立传感器模块生成：

```text
IMU
GPS
磁力计
气压计
空速计
LiDAR
Camera
```

特别是LiDAR和相机不应塞进飞行动力学内核。

---

## 不照搬四：不要让JSBSim和Gazebo同时计算同一架飞机的刚体状态

错误架构：

```text
JSBSim算飞机位姿
Gazebo也算飞机位姿
```

会形成两个物理权威。

正确架构必须二选一：

```text
方案A：
    JSBSim是物理权威
    Gazebo/UE只接受位姿并生成传感器

方案B：
    Gazebo是物理权威
    JSBSim仅作为离线控制和模型研究工具
```

---

## 不照搬五：不要默认旧PX4桥接长期可维护

当前PX4官方已明确提示JSBSim接口属于社区维护，现有文档和ROS桥接技术栈也较旧。([PX4 文档](https://docs.px4.io/main/en/sim_jsbsim/index "JSBSim Simulation | PX4 Guide (main)"))

因此应自己定义稳定的：

```text
PX4PhysicsBackendInterface
```

---

# 38.27 JSBSim 在CoSim长期架构中的位置

```text
                         UE高真实感前端
                                ▲
                                │ Unified VehicleState
                                │
┌────────────────────────────────────────────────────┐
│                CoSim Core Simulation API           │
│ Model / State / Clock / Sensor / Actuator / Fault │
└──────────▲─────────────────▲────────────────▲──────┘
           │                 │                │
           │                 │                │
    Gazebo Backend     MuJoCo Backend   JSBSim Backend
    多旋翼/传感器      RL/控制研究      固定翼/VTOL/火箭
           │                 │                │
        ROS2/PX4        Python/JAX       PX4/Simulink
```

建议后端定位：

```text
GazeboBackend：
    Sunray-150
    MID360
    PX4
    ROS2
    工程传感器

MuJoCoBackend：
    强化学习
    控制器训练
    快速多实例

JSBSimBackend：
    固定翼
    复合翼
    eVTOL
    大型航空器
    火箭
    飞行性能与控制律
```

---

# 38.28 JSBSim Backend接口建议

```text
IFlightDynamicsBackend
├─ loadModel(model)
├─ initialize(initialCondition)
├─ setControlInputs(inputs)
├─ setEnvironment(environment)
├─ applyExternalForce(force)
├─ step(dt)
├─ getState()
├─ getAerodynamicState()
├─ getPropulsionState()
├─ trim(condition)
├─ reset()
└─ getProperties()
```

控制输入：

```text
AircraftControlInput
├─ aileron
├─ elevator
├─ rudder
├─ throttle[]
├─ flap
├─ spoiler
├─ brake
├─ gear
└─ motor_commands[]
```

输出状态：

```text
AircraftState
├─ geodetic_position
├─ local_position
├─ orientation
├─ body_velocity
├─ angular_rate
├─ acceleration
├─ airspeed
├─ angle_of_attack
├─ sideslip
├─ mach
└─ load_factor
```

扩展状态：

```text
AerodynamicState
PropulsionState
LandingGearState
FuelState
ControlSurfaceState
```

---

# 38.29 推荐的两种运行模式

## 模式一：控制研究模式

```text
Simulink / Python Controller
          │
          ▼
       JSBSim
          │
          ▼
CSV / Plot / Evaluation
```

特点：

```text
不启动UE
不启动Gazebo
运行快
适合参数扫描
适合控制器开发
```

---

## 模式二：完整飞行仿真模式

```text
PX4 SITL / Controller
          │
          ▼
   CoSim JSBSim Adapter
          │
          ▼
       JSBSim
          │
          ├─ 真值状态 → Sensor Simulator → PX4
          │
          └─ 位姿 → UE高真实感显示
```

如果需要相机或LiDAR：

```text
JSBSim位姿
    ↓
同步到UE/Gazebo传感器世界
    ↓
生成Camera / LiDAR
```

此时必须保证：

```text
同一时钟
同一坐标
同一地形高度
同一碰撞定义
```

---

# 38.30 最小研究任务

```text
1. 安装JSBSim 1.3.1
2. 跑通C172示例脚本
3. 理解FGFDMExec加载和Run流程
4. 理解Property Tree
5. 理清aircraft、engine、systems、scripts目录
6. 理清metrics和mass_balance
7. 理清气动轴与机体轴
8. 理清升力、阻力和六个气动力/力矩轴
9. 理清活塞、涡轮、电机和螺旋桨模型
10. 理清起落架和地面反力
11. 完成平飞配平
12. 做升降舵阶跃响应
13. 用Python读取和修改Properties
14. 跑通MATLAB S-Function
15. 用Simulink实现高度和空速控制
16. 跑通UEReferenceApp
17. 理清UE插件如何固定步长执行JSBSim
18. 构建一个自定义固定翼无人机模型
19. 构建一个简化复合翼模型
20. 接入CoSim统一VehicleState
21. 设计PX4—JSBSim现代适配器
22. 写JSBSim REVIEW.md
```

---

# 38.31 第一阶段成功标准

```text
模型：
    自定义固定翼模型可以加载

初始化：
    能求出稳定平飞配平点

控制：
    能接收副翼、升降舵、方向舵和油门

动力学：
    能完成起飞、爬升、巡航、转弯和着陆

接口：
    Python和Simulink均可驱动

显示：
    UE能够读取并显示同一状态

平台：
    输出统一CoSim VehicleState

验证：
    关键飞行性能与理论或公开数据基本一致
```

---

# 38.32 JSBSim REVIEW.md 应该写什么

```text
1. 项目定位
    数据驱动的航空器六自由度飞行动力学内核

2. 它解决什么问题
    固定翼气动
    推进系统
    质量和重心
    飞行控制系统
    配平
    地球与大气
    起落架

3. 它不解决什么问题
    高真实感渲染
    LiDAR和相机
    ROS2机器人生态
    通用复杂碰撞
    三维路径规划

4. 核心架构
    FGFDMExec
    Property Tree
    Aerodynamics
    Propulsion
    Mass Balance
    Ground Reactions
    FCS
    Propagate

5. 模型体系
    aircraft
    engine
    systems
    scripts

6. 我们吸收什么
    数据驱动航空器
    力和力矩统一
    Property Tree
    推进系统分层
    配平分析
    脚本化实验
    固定步长后端

7. 不照搬什么
    XML唯一模型源
    弱类型属性作为核心接口
    旧PX4桥接
    传感器写进FDM

8. 是否进入主干
    作为固定翼/VTOL专用物理后端
    不替代Gazebo多旋翼工程后端

9. 长期用途
    固定翼
    复合翼
    eVTOL
    大型无人机
    控制律
    火箭
```

---

# 38.33 对JSBSim的最终判断

```text
是否进入CoSim：
    是

是否作为第一默认物理后端：
    否

进入哪一层：
    专用飞行动力学后端

最适合：
    固定翼
    复合翼
    eVTOL
    大型无人机
    火箭
    飞控与控制律验证

主要吸收：
    六自由度航空动力学
    数据驱动气动模型
    发动机和螺旋桨体系
    Property Tree
    配平与性能分析
    MATLAB/Simulink接口
    UE插件参考

不承担：
    MID360仿真
    SLAM
    规划
    ROS2机器人传感器
    通用高保真碰撞
    地图和视觉世界
```

最核心的一句话是：

> **JSBSim不是用来替代Gazebo或UE的完整仿真器，而是CoSim未来固定翼、复合翼、eVTOL和航空器控制研究所需要的专业飞行动力学内核。当前Sunray-150多旋翼主线仍以Gazebo为主，但一旦CoSim扩展到固定翼和低空航空器，JSBSim就应该成为与Gazebo、MuJoCo并列的第三个核心物理后端。**
>
