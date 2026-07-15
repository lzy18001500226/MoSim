# PX4/MoSim完整控制技术栈调研讨论稿

> 状态：cache讨论稿，不是正式架构冻结文档。
> 日期：2026-06-24
> 目的：先把PX4无人机控制技术栈、MoSim控制器插入位置、自由组合规则和
> 文档架构思路讨论清楚，再决定正式文档如何重构。

## 1. 核心结论

MoSim不能按“高级控制器清单”设计。正确入口应是完整无人机闭环：

```text
场景/地图/扰动/故障配置
        ↓
Gazebo/Sunray Plant + 传感器
        ↓
状态估计层
        ↓
任务/轨迹层
        ↓
控制器层
        ↓
增强/安全/故障模块
        ↓
PX4 Offboard Adapter
        ↓
PX4姿态环/角速度环/控制分配
        ↓
电机/执行器/Plant
        ↓
RViz/Gazebo/UE/前端/指标评价
```

每个控制器或模块必须先回答：

```text
它插入哪一层；
它替换PX4哪一环或复用PX4哪一环；
它消费哪些状态和参考；
它输出哪个控制层级；
它能否与当前ATTITUDE_THRUST第一阶段兼容；
它是否需要后续BODY_RATE、WRENCH或ROTOR层级；
它在最终界面上是控制器、增强模块、安全模块、故障模块还是实验环境开关。
```

不能要求每个控制器都需要`jerk/snap`，也不能把故障状态塞给所有控制器。
这些信号只属于部分层级和部分算法。

## 2. PX4完整控制栈理解

PX4飞控栈包括传感器、估计器、模式/导航、控制器、控制分配和执行器。
官方架构说明将其定义为guidance、navigation、control和actuator的完整链路。

多旋翼控制是级联控制结构：

```text
状态估计 EKF2
        ↓
位置/速度控制
        ↓
姿态设定
        ↓
姿态控制
        ↓
角速度设定
        ↓
角速度控制
        ↓
控制分配/混控
        ↓
执行器
```

这意味着外部控制器有多种接入层级。接入越低，外部控制器承担的飞控责任越多；
接入越高，更多PX4内环被保留。

## 3. PX4 Offboard层级

PX4 Offboard允许外部系统设置位置、速度、加速度、姿态、角速度、
推力/力矩或直接执行器等设定值。`OffboardControlMode`字段有优先级：

```text
position
velocity
acceleration
attitude
body_rate
thrust_and_torque
direct_actuator
```

MoSim第一阶段冻结为：

```text
ATTITUDE_THRUST
```

这不是PX4能力限制，而是MoSim主动收缩第一阶段范围。后续BODY_RATE、WRENCH、
ROTOR必须作为新阶段，不应混入第一阶段验收。

## 4. 状态源和FAST-LIO位置

状态源层应独立于控制器层。

建议固定四类状态源Profile：

| Profile | 用途 | 是否作为控制输入 |
| --- | --- | --- |
| PX4/MAVROS融合状态 | 当前基准控制输入 | 是 |
| Gazebo truth | 评价真值、调试对照 | 默认否 |
| FAST-LIO direct | 对照实验，诊断FAST-LIO输出质量 | 可选实验 |
| FAST-LIO -> PX4 EKF2 -> MAVROS | 最终推荐状态源替换路线 | 是，需门禁 |

FAST-LIO不应因为RViz点云可见就进入控制闭环。它至少需要完成：

```text
点云正常；
IMU正常；
时间戳正常；
坐标系正常；
外参/安装方向合理；
里程计连续；
与Gazebo truth对齐评价；
经PX4 EKF2融合后输出稳定的本地状态；
再做px4ctrl闭环A/B对比。
```

## 5. 控制器和模块插入位置

### 5.1 外环控制器

这些控制器主要作用在位置/速度/加速度跟踪层，第一阶段优先输出
`ATTITUDE_THRUST`：

| 对象 | 典型位置 | 输入 | 输出 | 是否天然需要jerk/snap |
| --- | --- | --- | --- | --- |
| px4ctrl | 外环 | p/v/a/yaw、状态、质量、重力 | attitude + thrust | 否 |
| PID | 位置/速度/高度外环 | p/v参考与状态 | acceleration或attitude + thrust | 否 |
| LQI | 增广状态反馈外环 | 状态、积分误差、参考 | acceleration或attitude + thrust | 否 |
| SE3 | 几何外环 | p/v/a/yaw、姿态 | thrust + attitude，可扩展body-rate | 通常否 |
| SMC | 鲁棒外环或姿态环 | 状态、参考、滑模面 | acceleration、attitude或body-rate | 否 |
| LMPC | 线性优化外环 | 状态、参考、约束 | acceleration、attitude或body-rate | 通常否 |
| NMPC | 非线性优化控制 | 全状态、约束、参考 | acceleration、attitude、body-rate或wrench | 视模型而定 |
| DFBC | 微分平坦控制 | p/v/a/yaw，激进版本含jerk/snap | attitude、body-rate、wrench | 高阶版本需要 |

### 5.2 增强/补偿模块

这些对象不一定是独立“控制器”，更像控制器增强模块：

| 对象 | 典型位置 | 作用 | 不应误解为 |
| --- | --- | --- | --- |
| INDI | 内环或高动态外环增强 | 用增量动态逆提高跟踪和抗扰 | 普通外环PID替代品 |
| L1 | 自适应补偿 | 处理模型不确定性或扰动 | 任意层都可直接开关的万能模块 |
| AWFF | 加速度/扰动前馈 | 减少跟踪滞后和稳态偏差 | 不需要状态/模型审计的调参项 |
| DOB/ESO | 扰动观测 | 估计总扰动或扩展状态 | 故障标签输入 |

### 5.3 安全和故障模块

故障注入和故障处理要分开：

```text
故障注入：
  属于实验环境/Plant层，在Gazebo或执行器模型中注入推力衰减、失效、
  饱和、延迟等。

故障检测/估计：
  属于FDI/DOB/ESO/L1等估计层，输出故障估计或扰动估计。

故障分配：
  属于控制分配/执行器层，使用执行器有效性、故障估计和约束重新分配
  推力/力矩。

安全过滤：
  属于参考或控制输出后处理层，约束位置、速度、倾角、推力、安全距离等。
```

因此，普通控制器文档不应强制包含“故障状态输入”。只有故障感知控制器、
安全过滤器、FDI、Fault Allocation等对象需要该项。

## 6. 轨迹信号的分层

轨迹层可以保存高阶信息，但控制器是否使用取决于插入层级。

| 信号 | 用途 | 谁需要 |
| --- | --- | --- |
| position | 位置目标 | 几乎所有轨迹跟踪控制器 |
| velocity | 速度前馈/误差 | px4ctrl、PID、SE3、DFBC、MPC |
| acceleration | 加速度前馈 | px4ctrl、SE3、DFBC、MPC、AWFF |
| jerk | body-rate/高阶前馈 | 高阶DFBC、部分NMPC/轨迹评估 |
| snap | 角加速度/力矩/rotor级前馈 | 高阶DFBC、wrench/rotor级控制 |
| yaw/yaw_rate | 航向控制 | 多数控制器 |

PX4 `TrajectorySetpoint`虽然包含jerk字段，但官方说明该字段用于日志，不等价于PX4
内置位置控制器会消费jerk。因此MoSim的Trajectory Server可以保留jerk/snap，
但控制器文档不能一刀切要求它们作为输入。

## 7. 自由搭配的正确方式：兼容性矩阵

最终前端应支持自由选择，但不是任意组合。系统必须有兼容性矩阵。

### 7.1 选择维度

```text
场景/地图：
  空场、柱体、窄通道、多障碍、UE真值地图

状态源：
  PX4/MAVROS融合、FAST-LIO经PX4融合、FAST-LIO direct对照、Gazebo truth评价

任务：
  起飞、悬停、降落、阶跃、8字、螺旋、圆形、目标点、EGO、Swarm

控制器：
  px4ctrl、PID、LQI、SE3、DFBC、SMC、LMPC、NMPC

增强模块：
  INDI、L1、AWFF、DOB/ESO

安全模块：
  Safety Filter、CBF、Reference Governor

故障/扰动：
  风扰、阵风、负载变化、推力衰减、电机失效、延迟、饱和

输出层级：
  ATTITUDE_THRUST、BODY_RATE_THRUST、WRENCH、ROTOR
```

### 7.2 兼容性原则

```text
如果输出层级是ATTITUDE_THRUST：
  允许px4ctrl、PID、LQI、SE3基础版、部分SMC/LMPC/NMPC。
  不允许需要wrench/rotor级输出的控制分配实验。

如果输出层级是BODY_RATE_THRUST：
  可研究DFBC高阶版本、INDI增强、部分NMPC。
  需要重新定义Adapter和PX4接口验收。

如果输出层级是WRENCH/ROTOR：
  才进入故障分配、控制分配重构、电机失效恢复等任务。
  不应与第一阶段px4ctrl基准混为一谈。

如果任务是EGO/Swarm：
  规划器输出轨迹，控制器消费Trajectory Server求值结果。
  规划器不直接拥有MAVROS控制权。

如果开启故障/风扰：
  这是实验环境配置，不应默认成为所有控制器输入。
  只有声明支持故障感知或扰动估计的模块才消费估计结果。
```

## 8. 前端/界面应表达的系统对象

最终界面建议围绕实验配置Profile，而不是围绕某个脚本。

必要面板：

```text
1. 场景面板
   地图选择、障碍物Profile、UE/Gazebo场景选择。

2. 任务面板
   起飞/悬停/降落、8字、螺旋、阶跃、目标点、EGO、Swarm。

3. 状态源面板
   当前使用的状态源Profile、FAST-LIO/PX4融合状态、truth评价状态。

4. 控制器面板
   控制器选择、输出层级、参数Profile、是否可用于当前任务。

5. 增强模块面板
   INDI、L1、AWFF、DOB/ESO开关和参数。

6. 安全/故障/扰动面板
   风速、风向、阵风、推力衰减、电机失效、故障时刻、安全距离、倾角限制。

7. 可视化面板
   RViz点云累计地图、栅格地图、飞机三轴、轨迹、Gazebo动画、
   多机摄像头第一视角、UE展示。

8. 指标面板
   RMSE、Max误差、稳态误差、清障距离、恢复时间、控制输出、能耗或推力统计。
```

界面必须展示兼容性结果。例如选择`ATTITUDE_THRUST`时，`Fault Allocation`
可以显示为后续不可用，而不是允许用户打开后产生假实验。

## 9. 文档架构建议

正式文档不应继续以长文档堆叠为主。建议组织为：

```text
Docs/Design/
  README.md
  赛题.md

  00_系统架构与任务/
    系统架构.md
    任务路线图.md
    实验平台对象矩阵.md
    兼容性矩阵.md

  01_运行基线与状态源/
    Sunray_Gazebo_PX4_MAVROS基线.md
    状态源与坐标系.md
    FASTLIO定位闭环.md

  02_控制器平台/
    统一控制接口.md
    Adapter与PX4接口.md
    控制器Profile与管理.md
    controllers/
      px4ctrl.md
      PID.md
      LQI.md
      SE3.md
      DFBC.md
      SMC.md
      LMPC.md
      NMPC.md
    modules/
      INDI.md
      L1.md
      AWFF.md
      DOB-ESO.md
      Safety-Filter.md
      Fault-Allocation.md

  03_规划与集群/
    轨迹接口与TrajectoryServer.md
    planners/
      EGO-Planner-v1.md
      EGO-Planner-v2.md
      Diff-Planner.md
      EGO-Swarm.md

  04_实验评估与展示/
    控制器测试矩阵.md
    扰动故障测试矩阵.md
    RViz_Gazebo_UE_前端展示规范.md
    报告与交付物规范.md

  cache/
```

## 10. 每类文档不应共用同一个模板

### 控制器文档

```text
算法目标
控制链路位置
输入信号
输出层级
是否复用PX4内环
是否需要高阶轨迹信号
是否需要状态估计/扰动估计
可用任务
不可用任务
前端选择方式
验收指标
当前实现状态
禁止声明
```

### 增强模块文档

```text
增强对象
插入位置
所需估计量
对控制器的兼容性
开启/关闭策略
参数Profile
对指标的预期改善
失败风险
```

### 安全/故障文档

```text
作用层级
约束或故障模型
是否属于Plant注入、检测估计、控制过滤或控制分配
前端控件
实验场景
恢复策略
验收指标
```

### 规划器文档

```text
地图输入
状态输入
目标输入
轨迹输出
是否依赖FAST-LIO
是否支持多机
是否直接控制MAVROS：必须为否
Trajectory Server适配
验收场景
```

## 11. 当前执行建议

先不要立刻铺开所有控制器实现。建议顺序：

```text
1. 先冻结系统分层和兼容性矩阵。
2. 再重构正式文档结构。
3. 先完成px4ctrl/PID/SE3三个代表性模板。
4. 再用该模板逐个释放LQI、DFBC、SMC、LMPC、NMPC。
5. 增强模块INDI/L1/AWFF/DOB-ESO按兼容性接入，不作为普通控制器平铺。
6. Safety Filter和Fault Allocation等到BODY_RATE/WRENCH/ROTOR层级清楚后再实现。
7. 前端从一开始按实验Profile设计，避免后期硬拼UI。
```

## 12. 参考资料

1. PX4 Architectural Overview
   https://docs.px4.io/main/en/concept/architecture
2. PX4 Controller Diagrams
   https://docs.px4.io/main/en/flight_stack/controller_diagrams
3. PX4 Offboard Mode
   https://docs.px4.io/main/en/flight_modes/offboard
4. PX4 Modules Reference: Controller
   https://docs.px4.io/main/en/modules/modules_controller
5. PX4 External Position Estimation
   https://docs.px4.io/main/en/ros/external_position_estimation
6. PX4 Visual Inertial Odometry / EKF2 external position tuning
   https://docs.px4.io/main/en/computer_vision/visual_inertial_odometry
7. PX4 EKF2 tuning and external vision uncertainty
   https://docs.px4.io/main/en/advanced_config/tuning_the_ecl_ekf
8. FAST-LIO: A Fast, Robust LiDAR-inertial Odometry Package
   https://arxiv.org/abs/2010.08196
9. FAST-LIO2: Fast Direct LiDAR-inertial Odometry
   https://arxiv.org/abs/2107.06829
10. EGO-Planner repository and paper entry
    https://github.com/ZJU-FAST-Lab/ego-planner
11. EGO-Swarm paper
    https://arxiv.org/abs/2011.04183
12. Accurate Tracking of Aggressive Quadrotor Trajectories Using INDI and Differential Flatness
    https://www.ezratal.net/files/CDC18_1876.pdf
13. A Comparative Study of Nonlinear MPC and Differential-Flatness-Based Control for Quadrotor Agile Flight
    https://arxiv.org/abs/2109.01365
