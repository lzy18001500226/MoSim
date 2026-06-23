下面完全沿用你上传的 **AirSim** 与 **MuJoCo** 文档结构，不再只讲“算法是什么”，而是讲清楚：它为什么这样设计、内部数据怎么流、和 PX4/ROS2/Gazebo 的关系、我们应该吸收什么，以及它在 MoSim 里的长期位置。

---

# 8. 项目概述：Fast-Planner

## 8.1 定位

Fast-Planner 是香港科技大学空中机器人团队提出的一套面向四旋翼的实时局部轨迹规划框架。

它的核心目标是：

> **在三维复杂环境中，根据当前无人机状态和局部障碍物地图，快速生成一条无碰撞、平滑且满足速度和加速度约束的飞行轨迹。**

Fast-Planner 不是普通的 A* 路径搜索器，也不是简单的避障算法。它完整包含：

```text
环境建图
    ↓
动力学路径搜索
    ↓
B样条轨迹优化
    ↓
时间调整
    ↓
轨迹重规划
```

其代表性论文采用 kinodynamic path search 生成动力学可行的初始轨迹，再利用欧氏距离场和 B-spline 优化轨迹的平滑性、障碍物间距与动力学约束。后续工作又加入拓扑路径，以减少梯度优化陷入局部极小值的问题。([arXiv](https://arxiv.org/abs/1907.01531?utm_source=chatgpt.com "Robust and Efficient Quadrotor Trajectory Generation for Fast Autonomous Flight"))

对我们的 MoSim 来说，Fast-Planner 的价值不是简单地“拿来飞”，而是研究：

```text
搜索算法如何理解无人机动力学？

离散搜索结果如何变成连续轨迹？

轨迹优化器如何同时处理：
    平滑性
    障碍物
    速度
    加速度
    时间

规划器如何不断滚动重规划？
```

Fast-Planner 在我们架构中的候选定位是：

```text
经典无人机局部轨迹规划基线

以及：
    Kinodynamic A*参考
    ESDF规划参考
    B-spline轨迹优化参考
    拓扑轨迹规划参考
```

而不是：

```text
全局任务规划器
多无人机任务分配器
飞行控制器
电机控制器
```

---

## 8.2 核心设计理念

| 设计原则       | 说明                                                       |
| -------------- | ---------------------------------------------------------- |
| 搜索与优化结合 | 搜索负责找到一条大致可行的路线，优化负责把路线变成平滑轨迹 |
| 动力学搜索     | 搜索节点不只有位置，还考虑速度、加速度等运动状态           |
| ESDF辅助优化   | 使用障碍物距离和梯度推动轨迹远离障碍                       |
| B-spline表示   | 用少量控制点表示连续、可求导的轨迹                         |
| 滚动重规划     | 无人机只执行轨迹前段，同时不断根据新地图重新计算           |
| 拓扑候选       | 同时考虑从障碍物不同方向绕行的轨迹                         |
| 轨迹与控制分离 | 规划器生成期望轨迹，控制器负责真正跟踪                     |

Fast-Planner 官方框架接收深度图或点云与里程计，更新概率体素地图并建立 ESDF，随后完成路径搜索与轨迹优化。([GitHub](https://github.com/HKUST-Aerial-Robotics/Fast-Planner/blob/master/README.md?utm_source=chatgpt.com "Fast-Planner/README.md at master · HKUST-Aerial-Robotics/Fast-Planner · GitHub"))

---

# 8.3 系统设计逻辑

## 8.3.1 第一性原理：为什么普通 A* 不够？

普通 A* 通常只考虑：

```text
当前位置
    ↓
向相邻栅格移动
    ↓
是否碰撞
```

这适合低速移动机器人，但无人机存在惯性。

假设无人机当前以 8 m/s 向前飞：

```text
普通A*：
    前面不能走
    立即向左移动

真实无人机：
    不能瞬间消除前向速度
    不能瞬间产生无限横向加速度
```

普通路径可能在几何上可行，但在动力学上根本无法跟踪。

所以 Fast-Planner 搜索的不是简单位置点，而是状态：

```text
状态：
    位置
    速度

输入：
    一段时间内的加速度
```

每次扩展节点时，它问的是：

```text
如果未来 Δt 时间内施加这个加速度，
无人机会到哪里？
速度是否超限？
这段运动是否碰撞？
```

这就是  **Kinodynamic Search** ：

```text
Kinematic：
    位置、速度、运动几何

Dynamic：
    加速度、控制输入和动力学约束
```

因此搜索出来的不只是一条折线路径，而是一条初步满足动力学的运动轨迹。Fast-Planner 论文将其描述为在离散控制空间中搜索安全、动力学可行且接近最短时间的初始轨迹。([arXiv](https://arxiv.org/abs/1907.01531?utm_source=chatgpt.com "Robust and Efficient Quadrotor Trajectory Generation for Fast Autonomous Flight"))

---

## 8.3.2 第二性原理：为什么搜索完还需要优化？

搜索空间是离散的。

例如加速度只能从有限集合中选择：

```text
ax ∈ {-2, 0, 2}
ay ∈ {-2, 0, 2}
az ∈ {-2, 0, 2}
```

这样搜索速度比较快，但轨迹可能出现：

```text
控制输入突然变化
转弯不自然
轨迹离障碍物过近
轨迹时间分配不合理
```

因此 Fast-Planner 采用：

```text
动力学搜索：
    给优化器一个可靠初值

B-spline优化：
    把初值打磨成高质量连续轨迹
```

可以类比为：

```text
搜索阶段：
    先用导航软件决定经过哪些道路

优化阶段：
    再决定方向盘怎么平滑转、什么时候加速和刹车
```

---

## 8.3.3 第三性原理：为什么需要 ESDF？

仅有占据地图只能回答：

```text
这里是空闲还是障碍物？
```

轨迹优化器还需要知道：

```text
当前位置距离最近障碍物多远？
往哪个方向移动可以离障碍物更远？
```

ESDF，即欧氏有符号距离场，可以为地图中每个位置提供近似距离值：

```text
距离障碍物：
    0.1 m
    0.5 m
    2.0 m
```

还可以根据距离变化求出梯度：

```text
∇d(x)
```

这个梯度相当于一支箭头：

```text
往这个方向移动
可以最快远离障碍物
```

于是轨迹优化器不需要盲目尝试，而可以沿梯度直接推动控制点。

---

# 8.4 Fast-Planner 的主要架构

```text
深度相机 / LiDAR
        │
        ▼
概率体素地图
        │
        ▼
ESDF距离场
        │
        ▼
Kinodynamic A*
        │
        ▼
动力学可行初始轨迹
        │
        ▼
B-spline控制点初始化
        │
        ▼
轨迹优化
├─ 平滑代价
├─ 障碍物代价
├─ 速度约束
├─ 加速度约束
└─ 终点约束
        │
        ▼
时间调整
        │
        ▼
最终轨迹
        │
        ▼
轨迹跟踪控制器
```

Fast-Planner 的优化目标可以抽象成：

```text
J =
    λs · 平滑代价
  + λc · 碰撞代价
  + λd · 动力学代价
  + λg · 目标代价
```

其中：

```text
平滑代价：
    避免控制点剧烈变化

碰撞代价：
    保持与障碍物的安全距离

动力学代价：
    限制速度和加速度

目标代价：
    保证轨迹到达局部目标
```

---

# 8.5 B-spline 为什么适合无人机？

B-spline 轨迹由控制点定义：

```text
Q0, Q1, Q2, Q3, ...
```

真实轨迹通常不会直接穿过每个控制点，而是被这些控制点平滑“拉动”。

它的优点包括：

```text
局部修改：
    移动一个控制点，只影响附近轨迹

连续可导：
    可以直接计算速度、加速度、jerk

变量较少：
    不需要优化轨迹上的每一个采样点

凸包性质：
    可以通过控制点差分约束速度和加速度
```

Fast-Planner 利用 B-spline 的凸包性质，将速度和加速度约束转化为对控制点差分的限制，并通过非均匀 B-spline 与迭代时间调整保证最终轨迹的动力学可行性。([arXiv](https://arxiv.org/abs/1907.01531?utm_source=chatgpt.com "Robust and Efficient Quadrotor Trajectory Generation for Fast Autonomous Flight"))

---

# 8.6 为什么还需要拓扑路径？

假设目标在墙后面：

```text
             墙
起点 ───── █████ ───── 目标
```

存在两种明显方案：

```text
从左绕
从右绕
```

梯度优化依赖初值。

如果初始轨迹压在墙中间，优化器可能只知道：

```text
我要离墙远一点
```

却不知道应该整体从左边还是右边绕。

Fast-Planner 后续的拓扑规划会先生成若干条属于不同拓扑类别的路径：

```text
候选1：从左绕
候选2：从右绕
候选3：从上方绕
```

再分别优化，最后选择质量最好的轨迹。这种“多条候选路径加引导优化”的设计，就是为了解决单次局部优化容易卡在错误绕行方向的问题。([GitHub](https://github.com/HKUST-Aerial-Robotics/TopoTraj?utm_source=chatgpt.com "GitHub - HKUST-Aerial-Robotics/TopoTraj: A robust UAV local planner based on the ICRA2020 paper: Robust Real-time UAV Replanning Using Guided Gradient-based Optimization and Topological Paths"))

---

# 8.7 Fast-Planner 与 PX4 的关系

Fast-Planner不负责姿态控制和电机控制。

它通常输出：

```text
期望位置 p(t)
期望速度 v(t)
期望加速度 a(t)
期望航向 yaw(t)，视实现而定
```

然后控制链为：

```text
Fast-Planner
    ↓
轨迹跟踪控制器
    ↓
期望推力和期望姿态
    ↓
PX4姿态控制
    ↓
角速度控制
    ↓
电机混控
```

所以 Fast-Planner 属于：

```text
运动规划层
```

PX4属于：

```text
飞行控制和执行层
```

两者之间必须有轨迹跟踪接口，不能让 Fast-Planner 直接输出四个电机转速。

---

# 8.8 Fast-Planner 与 ROS2、Gazebo、UE 的关系

Fast-Planner 官方开源工程主要基于 ROS1 catkin 工作空间，其原始测试和构建方式明显属于较早的 ROS1 技术栈。([GitHub](https://github.com/HKUST-Aerial-Robotics/Fast-Planner "GitHub - HKUST-Aerial-Robotics/Fast-Planner: A Robust and Efficient Trajectory Planner for Quadrotors · GitHub"))

在我们的架构中应理解为：

```text
Gazebo：
    生成无人机动力学和传感器数据

ROS2：
    发布点云、里程计和目标

Fast-Planner Adapter：
    转换ROS2消息
    调用规划核心
    发布统一轨迹

PX4：
    跟踪轨迹

UE：
    只显示规划结果和无人机状态
```

不应把 Fast-Planner 的 ROS1 消息接口直接变成 MoSim 的永久接口。

---

# 8.9 我们应该吸收 Fast-Planner 哪些设计？

## 吸收一：搜索和优化分层

```text
搜索：
    保证有路可走

优化：
    保证飞得好
```

单独使用搜索，轨迹太粗糙。

单独使用梯度优化，容易陷入局部极小值。

---

## 吸收二：动力学状态搜索

MoSim 的规划接口不能只考虑：

```text
position
```

还必须考虑：

```text
velocity
acceleration
```

否则高速情况下生成的路径没有意义。

---

## 吸收三：统一轨迹表示

需要定义通用轨迹对象：

```text
Trajectory
    start_time
    duration
    position(t)
    velocity(t)
    acceleration(t)
    jerk(t)
    yaw(t)
```

不同规划器都转换成这个统一格式。

---

## 吸收四：滚动重规划

规划器不应该一次生成整条路线后就不再更新。

应该采用：

```text
执行前段
    +
不断重新规划后段
```

---

## 吸收五：多拓扑候选

对于复杂环境，不能只优化一条初始轨迹。

MoSim应允许：

```text
generateCandidates()
optimizeCandidate()
selectBest()
```

---

# 8.10 我们不应该照搬 Fast-Planner 的地方

## 不照搬一：不要让 ESDF 成为所有规划器的唯一地图接口

Fast-Planner依赖 ESDF，但 EGO-Planner不依赖。

因此核心接口应该是：

```text
IMapQuery
```

然后可选实现：

```text
OccupancyQuery
DistanceFieldQuery
RaycastQuery
PointCloudQuery
SafeCorridorQuery
```

---

## 不照搬二：不要把 ROS1 消息写进规划核心

规划核心应只处理 C++ 数据结构。

ROS1、ROS2、仿真器接口放在 Adapter 层。

---

## 不照搬三：不要把规划器等同于完整自主系统

Fast-Planner不负责：

```text
定位
SLAM
任务分配
全局探索
控制器
故障管理
通信
```

---

## 不照搬四：不要默认球形无人机模型永远足够

很多规划器把无人机简化为：

```text
一个球
```

但 Sunray-150 加上 MID360、起落架和载荷后，真实包络可能不是球形。

MoSim应预留：

```text
Sphere
Ellipsoid
Cylinder
ConvexHull
```

等碰撞外形。

---

# 8.11 对 Fast-Planner 源码结构的理解

值得重点研究的模块大致包括：

```text
plan_env
    地图、ESDF、碰撞查询

path_searching
    Kinodynamic A*
    拓扑路径搜索

bspline_opt
    B-spline代价和优化器

plan_manage
    状态机
    重规划逻辑
    模块调度

traj_utils
    轨迹消息和数学工具

uav_simulator
    简化无人机和传感器仿真
```

真正值得吸收的不是包名，而是层次：

```text
地图
    ↓
搜索
    ↓
优化
    ↓
规划管理器
    ↓
轨迹执行
```

---

# 8.12 在 MoSim 长期架构中的位置

```text
感知 / 地图
      │
      ▼
FastPlannerAdapter
├─ Kinodynamic Search
├─ B-spline Optimizer
└─ Topological Candidate Generator
      │
      ▼
Unified Trajectory
      │
      ▼
Trajectory Validator
      │
      ▼
PX4 / Controller
```

Fast-Planner的定位是：

```text
经典局部规划器
算法对照基线
搜索与优化参考实现
```

不建议作为整个 MoSim 唯一的默认规划器。

---

# 8.13 最小研究任务

```text
1. 跑通官方 kino_replan 示例
2. 理清地图输入和里程计输入
3. 理清 Kinodynamic A* 状态和控制输入
4. 理清启发函数和终点连接
5. 理清 B-spline 控制点含义
6. 理清平滑、碰撞和动力学代价
7. 理清 ESDF 查询链路
8. 理清时间调整机制
9. 跑通拓扑路径版本
10. 将轨迹转换为统一 Trajectory 接口
11. 用 Gazebo 里程计和点云替换官方模拟输入
12. 对比 EGO-Planner 的计算时间和成功率
13. 写 Fast-Planner REVIEW.md
```

---

# 8.14 Fast-Planner REVIEW.md 应该写什么

```text
1. 项目定位
    四旋翼实时局部轨迹规划框架

2. 它解决什么问题
    三维避障
    动力学可行搜索
    平滑轨迹
    在线重规划

3. 核心设计
    Kinodynamic A*
    ESDF
    B-spline
    时间调整
    拓扑路径

4. 输入
    点云/深度
    里程计
    目标点
    动力学限制

5. 输出
    连续位置轨迹
    速度和加速度参考

6. 我们吸收什么
    搜索优化分层
    动力学搜索
    统一轨迹
    滚动重规划
    拓扑候选

7. 不照搬什么
    ROS1接口
    ESDF唯一依赖
    官方模拟器
    固定机体外形

8. 长期位置
    经典规划基线
```

---

# 8.15 对 Fast-Planner 的最终判断

```text
是否进入长期项目：
    是

是否作为唯一规划器：
    否

进入哪一层：
    局部轨迹规划层
    规划算法基准层

主要吸收：
    Kinodynamic Search
    ESDF轨迹优化
    B-spline
    拓扑候选
    滚动重规划

不承担：
    SLAM
    全局任务规划
    多机协同
    姿态和电机控制
```

一句话：

> **Fast-Planner 最值得我们学习的，是它把“找得到路”和“飞得动、飞得顺”拆成动力学搜索与连续轨迹优化两个阶段，构成了现代四旋翼局部规划的经典框架。**

---

# 9. 项目概述：EGO-Planner

## 9.1 定位

EGO-Planner 是浙江大学 FAST Lab 提出的一套轻量级四旋翼局部轨迹规划器。

EGO中的关键含义是：

```text
ESDF-free
Gradient-based
lOcal planner
```

它的核心目标是：

> **在不构建完整 ESDF 的情况下，仍然利用梯度优化快速生成无碰撞、平滑且动力学可行的 B-spline 轨迹。**

EGO-Planner的框架建立在 Fast-Planner 基础上，但删除了完整 ESDF 构建环节，并使用碰撞轨迹与无碰撞引导路径之间的关系构造避障梯度。官方仓库称其为轻量、无 ESDF 的梯度局部规划器，并在作者测试条件下报告了约毫秒级的规划时间。([GitHub](https://github.com/ZJU-FAST-Lab/ego-planner "GitHub - ZJU-FAST-Lab/ego-planner · GitHub"))

---

## 9.2 核心设计理念

| 设计原则         | 说明                                   |
| ---------------- | -------------------------------------- |
| 不构建完整ESDF   | 只提取当前轨迹真正需要的障碍物信息     |
| 直接优化B-spline | 控制点既是轨迹表示，也是主要优化变量   |
| 碰撞时再生成梯度 | 没有碰撞的轨迹区域不做多余距离场计算   |
| 引导路径辅助     | 用一条无碰撞路径告诉优化器应该向哪边绕 |
| 轻量优化器       | 使用 L-BFGS-Lite 等轻量数值优化工具    |
| 局部滚动规划     | 面向短时间范围持续重新生成轨迹         |

---

# 9.3 系统设计逻辑

## 9.3.1 第一性原理：为什么可以去掉 ESDF？

Fast-Planner的思路是：

```text
先计算地图里每个位置到障碍物的距离
再让轨迹优化器查询距离和梯度
```

但真实规划中，轨迹只经过地图的一小部分。

例如局部地图有几百万个体素，而轨迹只包含几十个控制点：

```text
完整ESDF：
    为几百万个位置计算障碍距离

实际优化：
    可能只查询几十或几百个位置
```

EGO-Planner认为：

> 没必要为了少量轨迹控制点，提前计算整个局部地图的距离场。

所以它改成：

```text
先生成轨迹
    ↓
检查轨迹是否碰撞
    ↓
如果碰撞
    才分析碰撞区域
    ↓
构造障碍物方向信息
    ↓
推动控制点离开障碍物
```

这相当于：

```text
Fast-Planner：
    先画完整地形等高线图再走路

EGO-Planner：
    遇到墙时才判断墙在哪边、应该往哪边绕
```

---

## 9.3.2 第二性原理：没有距离场，梯度从哪里来？

轨迹与障碍物相交时，单纯知道：

```text
这个点撞了
```

还不够。

优化器需要知道：

```text
应该往哪个方向移动？
```

EGO-Planner会构造一条无碰撞引导路径。

假设：

```text
当前B-spline控制点：
    在障碍物内部

引导路径：
    从障碍物左侧绕开
```

就可以根据控制点与引导路径之间的几何关系，构造：

```text
障碍物锚点
排斥方向
安全距离
```

然后产生类似的碰撞代价：

```text
Jcollision =
    当控制点离障碍方向过近时
    产生惩罚
```

论文的关键改进正是：通过比较碰撞轨迹和无碰撞引导路径来构造碰撞代价，而不需要全局 ESDF。([ResearchGate](https://www.researchgate.net/publication/343786586_EGO-Planner_An_ESDF-free_Gradient-based_Local_Planner_for_Quadrotors?utm_source=chatgpt.com "EGO-Planner: An ESDF-free Gradient-based Local Planner for Quadrotors | Request PDF"))

---

## 9.3.3 第三性原理：为什么 EGO 仍然需要初始轨迹？

梯度优化只能回答：

```text
当前解附近应该往哪里改
```

它不能保证自动发现所有完全不同的绕行方式。

例如：

```text
从柱子左边绕
从柱子右边绕
```

这是两个不同的解空间。

如果初始轨迹在柱子左侧，优化器通常只会在左侧继续调整。

因此 EGO-Planner虽然省掉了 ESDF，却没有消除：

```text
初值依赖
局部极小值
拓扑方向选择
```

它仍需要：

```text
合理的初始轨迹
碰撞检查
必要时生成引导路径
```

---

# 9.4 EGO-Planner 的主要架构

```text
局部占据地图
      │
      ▼
初始B-spline轨迹
      │
      ▼
控制点碰撞检查
      │
      ├── 无碰撞
      │      ↓
      │   直接优化
      │
      └── 有碰撞
             │
             ▼
       生成无碰撞引导路径
             │
             ▼
       提取障碍物锚点和方向
             │
             ▼
       构造碰撞代价
             │
             ▼
L-BFGS优化
├─ 平滑代价
├─ 障碍代价
├─ 速度约束
└─ 加速度约束
             │
             ▼
时间重分配
             │
             ▼
最终B-spline轨迹
```

---

# 9.5 EGO-Planner 和 Fast-Planner 的本质区别

| 维度       | Fast-Planner              | EGO-Planner            |
| ---------- | ------------------------- | ---------------------- |
| 障碍物梯度 | 主要来自 ESDF             | 来自碰撞轨迹与引导路径 |
| 地图预处理 | 较重                      | 较轻                   |
| 初值生成   | Kinodynamic Search 较完整 | 更强调快速局部优化     |
| 计算开销   | 地图距离场占一部分        | 避免完整ESDF           |
| 优化表示   | B-spline                  | B-spline               |
| 主要优势   | 搜索和优化链完整          | 轻量、快速             |

所以不是：

```text
EGO-Planner完全推翻Fast-Planner
```

而是：

```text
保留B-spline局部优化框架
        ↓
删除完整ESDF
        ↓
重构碰撞梯度来源
```

官方仓库也明确说明其框架基于 Fast-Planner。([GitHub](https://github.com/ZJU-FAST-Lab/ego-planner "GitHub - ZJU-FAST-Lab/ego-planner · GitHub"))

---

# 9.6 EGO-Planner 与地图的关系

EGO-Planner仍然需要地图。

“ESDF-free”并不等于：

```text
不需要地图
不需要碰撞检测
直接用原始点云规划
```

它通常仍需要：

```text
占据栅格地图
障碍物膨胀
控制点碰撞查询
射线或路径搜索
```

它省掉的是：

```text
整个局部空间的欧氏距离场构建
```

而不是省掉障碍物表示。

---

# 9.7 EGO-Planner 与 PX4 的关系

和 Fast-Planner 一样，EGO-Planner输出的是轨迹：

```text
p(t)
v(t)
a(t)
yaw(t)
```

完整链路仍然是：

```text
EGO-Planner
    ↓
Trajectory Server
    ↓
位置/速度控制器
    ↓
PX4姿态和角速度控制器
    ↓
电机
```

它不负责：

```text
电机混控
姿态稳定
状态估计
传感器驱动
```

---

# 9.8 我们应该吸收 EGO-Planner 哪些设计？

## 吸收一：按需计算障碍信息

不要为了少数规划查询，预先生成所有派生地图。

可以采用：

```text
lazy evaluation
按需查询
局部缓存
```

---

## 吸收二：地图接口与优化器解耦

优化器只需要知道：

```text
这个控制点是否碰撞
应该往哪个方向移动
安全距离是多少
```

不应该强制所有地图都提供完整 ESDF。

---

## 吸收三：优化器轻量化

规划问题每秒可能执行数十次。

需要避免：

```text
频繁内存分配
复杂对象构造
大规模矩阵重复创建
```

---

## 吸收四：失败诊断

规划器输出不应该只有：

```text
success / fail
```

还应有：

```text
INITIAL_PATH_FAILED
COLLISION_GRADIENT_FAILED
OPTIMIZATION_DIVERGED
DYNAMIC_LIMIT_EXCEEDED
TIME_REALLOCATION_FAILED
```

---

# 9.9 我们不应该照搬什么？

## 不照搬一：不要把软碰撞惩罚当成绝对安全保证

优化代价很大通常意味着轨迹会远离障碍，但：

```text
高惩罚 ≠ 数学上的绝对不可碰撞约束
```

MoSim需要独立的：

```text
TrajectoryValidator
```

在规划完成后重新进行连续碰撞检测。

---

## 不照搬二：不要只比较平均规划时间

需要同时记录：

```text
成功率
最小障碍距离
动力学违反次数
轨迹长度
飞行时间
轨迹平滑度
重规划失败次数
```

---

## 不照搬三：不要把官方约1 ms当成固定指标

这个数字取决于：

```text
CPU
地图密度
控制点数量
轨迹长度
参数
编译模式
```

它只能说明算法设计较轻量，不能直接作为我们平台的性能承诺。官方仓库的约毫秒级结果属于其特定实验条件。([GitHub](https://github.com/ZJU-FAST-Lab/ego-planner "GitHub - ZJU-FAST-Lab/ego-planner · GitHub"))

---

# 9.10 对 EGO-Planner 源码结构的理解

值得研究的模块通常包括：

```text
plan_env
    局部占据地图
    碰撞查询

bspline
    B-spline轨迹表示

bspline_opt
    平滑、碰撞、动力学代价

path_searching
    引导路径或局部搜索

plan_manage
    重规划状态机

traj_server
    轨迹执行和发布
```

最核心的调用链是：

```text
检测碰撞
    ↓
生成障碍方向
    ↓
设置控制点约束
    ↓
L-BFGS优化
```

---

# 9.11 在 MoSim 长期架构中的位置

```text
LocalMap
   │
   ▼
EGOPlannerAdapter
   │
   ├─ Initial Trajectory
   ├─ Collision Query
   ├─ Guide Path
   └─ B-spline Optimization
   │
   ▼
Unified Trajectory
   │
   ▼
Independent Validator
   │
   ▼
Controller / PX4
```

EGO-Planner适合成为：

```text
轻量单机局部规划基线
低算力规划测试对象
与Fast-Planner/SUPER对比的标准插件
```

---

# 9.12 最小研究任务

```text
1. 跑通官方 simple_run
2. 理清 B-spline 控制点初始化
3. 理清占据地图与碰撞检查
4. 找到障碍物方向生成代码
5. 理清引导路径如何影响控制点
6. 理清 L-BFGS 目标函数
7. 理清速度和加速度约束
8. 记录每次优化迭代的cost
9. 对比启用/禁用碰撞代价
10. 对比 Fast-Planner 的 ESDF 开销
11. 接入统一 Trajectory 接口
12. 增加独立连续碰撞验证器
13. 写 EGO-Planner REVIEW.md
```

---

# 9.13 对 EGO-Planner 的最终判断

```text
是否进入长期项目：
    是

进入哪一层：
    轻量局部轨迹规划器

主要吸收：
    ESDF-free思想
    按需障碍梯度
    B-spline优化
    轻量数值优化
    快速滚动重规划

不承担：
    全局路线
    多机任务管理
    飞行控制
    形式化安全保证
```

一句话：

> **EGO-Planner 最值得学习的，不只是“比 Fast-Planner 快”，而是它证明了轨迹优化并不一定需要整张 ESDF，只要能为碰撞控制点构造正确的绕障方向，就可以按需完成高效局部规划。**

---

# 10. 项目概述：EGO-Planner-Swarm / EGO-Swarm

## 10.1 定位

EGO-Planner-Swarm 是在 EGO-Planner 基础上扩展出的分布式多无人机自主导航系统。

它的核心目标是：

> **让每架无人机只依靠自己的机载感知、计算和邻机轨迹通信，在未知复杂环境中异步规划并避免与障碍物和其他无人机碰撞。**

它不是一台中央计算机同时求解所有无人机的联合优化问题，而是：

```text
每架无人机自己规划
每架无人机广播自己的轨迹
每架无人机根据邻机轨迹重新优化
```

官方论文将其描述为仅依赖机载资源、去中心化且异步的多机器人导航系统，并通过非线性轨迹优化处理机间碰撞风险，同时加入轻量拓扑轨迹生成以增强鲁棒性。([arXiv](https://arxiv.org/abs/2011.04183?utm_source=chatgpt.com "EGO-Swarm: A Fully Autonomous and Decentralized Quadrotor Swarm System in Cluttered Environments"))

---

## 10.2 核心设计理念

| 设计原则       | 说明                             |
| -------------- | -------------------------------- |
| 去中心化       | 不依赖中央规划服务器             |
| 异步规划       | 每架无人机按自己的节奏重规划     |
| 轨迹共享       | 广播未来一段时间的预测轨迹       |
| 时空避碰       | 比较同一时间下各无人机的位置     |
| 本地优化       | 每架无人机只优化自己的轨迹       |
| 不可靠通信容忍 | 允许通信延迟、丢失和不同步       |
| 轻量拓扑候选   | 必要时生成不同绕行方向的候选轨迹 |
| 单机兼容       | 多机系统也可以退化为单机规划     |

官方仓库说明该系统是 EGO-Planner 向多机导航的扩展，并提供 ROS2 分支；主仓库的标准构建流程仍以 ROS1 为主。([GitHub](https://github.com/ZJU-FAST-Lab/ego-planner-swarm "GitHub - ZJU-FAST-Lab/ego-planner-swarm: An efficient single/multi-agent trajectory planner for multicopters. · GitHub"))

---

# 10.3 系统设计逻辑

## 10.3.1 第一性原理：为什么不能把其他无人机当普通静态障碍物？

静态障碍物的位置是：

```text
p_obstacle
```

其他无人机的位置随时间变化：

```text
p_j(t)
```

假设两架无人机的几何路径交叉：

```text
UAV A：从西向东
UAV B：从南向北
```

几何路径相交不一定碰撞：

```text
A在第2秒通过交点
B在第5秒通过交点
```

但如果同时到达：

```text
A在第3秒通过
B也在第3秒通过
```

就会碰撞。

所以多机避碰必须处理：

```text
空间
+
时间
```

约束可以抽象为：

```text
||p_i(t) - p_j(t)|| ≥ d_safe
```

---

## 10.3.2 第二性原理：为什么要共享轨迹，而不只共享当前位置？

如果只知道邻机当前位置：

```text
UAV B现在在哪里
```

无法判断它下一步是：

```text
继续向前
突然转弯
悬停
返航
```

因此 EGO-Swarm共享的是未来轨迹：

```text
trajectory_j(t)
```

这样本机可以预测：

```text
未来0.5秒是否接近
未来1秒是否交叉
未来2秒是否需要提前绕开
```

这比只将邻机视为当前点障碍物更合理。

---

## 10.3.3 第三性原理：为什么采用分布式，而不是集中式？

集中式规划可以统一优化所有无人机：

```text
中央服务器
    ↓
同时计算UAV1、UAV2、UAV3……
```

但存在：

```text
计算量随无人机数量快速增长
中央节点故障会影响全队
通信必须稳定
所有无人机需要同步
```

分布式方案则是：

```text
每架无人机只优化自己
邻机轨迹作为外部约束
```

优点：

```text
容易扩展
没有唯一中央故障点
允许异步运行
更符合机载自主
```

缺点：

```text
没有全局最优保证
可能互相反复避让
可能出现决策振荡
依赖轨迹时间戳和通信质量
```

---

# 10.4 EGO-Swarm 的主要架构

```text
UAV i 本地传感器
        │
        ▼
本地占据地图
        │
        ▼
本机状态估计
        │
        ├──────────────┐
        │              │
        ▼              ▼
本机目标          接收邻机轨迹
        │              │
        └──────┬───────┘
               ▼
       本地轨迹优化器
       ├─ 静态障碍代价
       ├─ 邻机碰撞代价
       ├─ 平滑代价
       └─ 动力学约束
               │
               ▼
         本机B-spline轨迹
               │
       ┌───────┴────────┐
       ▼                ▼
发送给控制器       广播给其他无人机
```

---

# 10.5 异步规划是怎么工作的？

不是所有无人机同时执行：

```text
1、2、3，大家一起规划
```

而是：

```text
UAV1：
    地图变化 → 重规划 → 广播

UAV2：
    收到UAV1新轨迹 → 判断冲突 → 重规划

UAV3：
    继续执行原轨迹
    等达到自己的重规划条件再更新
```

所以每条轨迹必须携带：

```text
drone_id
trajectory_id
start_time
duration
control_points
time_interval
```

否则无法正确比较同一时刻的位置。

---

# 10.6 通信延迟会发生什么？

假设 UAV1 收到的是 UAV2 一秒以前的轨迹。

如果直接使用：

```text
p_2(t)
```

就会产生时间错位。

正确处理需要：

```text
消息时间戳
轨迹开始时间
当前仿真时间
轨迹剩余有效区间
超时判定
```

MoSim中应该显式模拟：

```text
延迟
丢包
乱序
带宽限制
通信中断
```

而不是只在完美局域网里验证多机规划。

EGO-Swarm论文专门强调其轨迹共享网络可以不可靠，并在系统中处理多机相对定位漂移。([arXiv](https://arxiv.org/abs/2011.04183?utm_source=chatgpt.com "EGO-Swarm: A Fully Autonomous and Decentralized Quadrotor Swarm System in Cluttered Environments"))

---

# 10.7 EGO-Swarm 不等于编队控制

它主要解决：

```text
多机各自到达目标
避开环境障碍物
避免互相碰撞
```

它不自动解决：

```text
谁去哪个目标
如何分配任务
保持V字队形
保持固定相对位置
领导者选择
区域覆盖
协同搜索
队伍重构
```

因此完整多机系统应该分层：

```text
Swarm Mission Layer
├─ 任务分配
├─ 队形管理
├─ 区域划分
└─ 全局协同

Swarm Trajectory Layer
└─ EGO-Swarm式轨迹去冲突

Control Layer
└─ 每架无人机独立跟踪
```

---

# 10.8 仿真中的 fake drone 问题

多机规划测试经常采用简化运动模型：

```text
规划器输出轨迹
    ↓
仿真器直接沿轨迹移动无人机
```

这种模式适合：

```text
测试10架、20架甚至更多无人机
验证轨迹冲突
测试规划时间
```

但它跳过了：

```text
位置控制误差
姿态动态
电机饱和
风扰
通信与飞控延迟
```

MoSim必须区分：

```text
Planner-only模式：
    完美轨迹跟踪

Full-dynamics模式：
    轨迹 → 控制器 → PX4 → 动力学
```

否则多机规划成功不代表真实无人机可以成功执行。

---

# 10.9 我们应该吸收哪些设计？

## 吸收一：轨迹是多机通信的一等数据

不能只发布：

```text
当前位置
```

必须定义：

```text
PredictedTrajectory
```

---

## 吸收二：统一多机时间基准

MoSim必须提供：

```text
simulation_clock
trajectory_start_time
message_timestamp
clock_offset
```

---

## 吸收三：本地规划与高层协同分离

任务分配器不要直接操作 B-spline 控制点。

它只输出：

```text
每架无人机的目标或走廊
```

---

## 吸收四：网络故障注入

规划测试必须包括：

```text
10 ms延迟
100 ms延迟
500 ms延迟
10%丢包
突发丢包
节点掉线
```

---

## 吸收五：邻机轨迹缓存

需要管理：

```text
每架无人机最新轨迹
轨迹版本
是否超时
预测终点
安全膨胀范围
```

---

# 10.10 我们不应该照搬什么？

## 不照搬一：不要认为局部互避等于全局协同

多个局部优化器可能产生：

```text
互相礼让
左右反复横跳
狭窄通道死锁
所有无人机同时绕向同一侧
```

还需要高层冲突管理。

---

## 不照搬二：不要默认通信永远存在

真实系统中必须设计：

```text
邻机轨迹超时后的保守策略
通信中断时的安全半径
失联无人机模型
紧急悬停或撤离
```

---

## 不照搬三：不要只在完美里程计下验证

多机相对位置误差会直接影响安全距离。

需要测试：

```text
固定偏差
随机漂移
时间同步误差
坐标系不一致
```

---

# 10.11 在 MoSim 长期架构中的位置

```text
Swarm Mission Manager
├─ Task Allocation
├─ Formation Manager
└─ Global Goals
          │
          ▼
EgoSwarmAdapter × N
├─ Local Map
├─ Neighbor Trajectory Cache
├─ Collision Optimizer
└─ Local Trajectory
          │
          ▼
Network Simulator
├─ Delay
├─ Loss
├─ Bandwidth
└─ Disconnect
          │
          ▼
Per-UAV Controller / PX4
```

---

# 10.12 最小研究任务

```text
1. 跑通2架无人机示例
2. 理清drone_id与命名空间
3. 找到邻机轨迹消息定义
4. 理清轨迹广播和接收链路
5. 理清机间碰撞代价
6. 跑4架、8架、16架规模测试
7. 注入固定通信延迟
8. 注入随机丢包
9. 注入里程计漂移
10. 比较fake drone与完整PX4动力学
11. 增加任务分配层
12. 测试狭窄通道死锁
13. 接入统一SwarmTrajectory接口
14. 写 EGO-Swarm REVIEW.md
```

---

# 10.13 对 EGO-Planner-Swarm 的最终判断

```text
是否进入长期项目：
    是

进入哪一层：
    多机局部轨迹去冲突层

主要吸收：
    去中心化规划
    异步重规划
    轨迹广播
    时空避碰
    邻机轨迹缓存
    不可靠通信测试

不承担：
    任务分配
    编队生成
    全局协同最优
    飞控和动力学
```

一句话：

> **EGO-Swarm 最值得学习的，是如何把单机轨迹优化扩展成“每架无人机独立规划、通过交换未来轨迹实现时空避碰”的分布式系统；但它只是多机轨迹层，不是完整的蜂群任务系统。**

---

# 11. 项目概述：FASTER

## 11.1 定位

FASTER，全称：

```text
Fast and Safe Trajectory Planner
```

是一套面向未知环境的高速安全轨迹规划器。

它要解决的核心矛盾是：

```text
飞得快：
    轨迹需要进入尚未完全观测的区域

绝对保守：
    轨迹只能待在已经确认安全的区域
```

传统安全规划器通常要求：

```text
轨迹必须全部位于已知自由空间
并在轨迹末端能够完全停止
```

这虽然安全，但会严重限制飞行速度。

FASTER的核心思想是：

> **允许主轨迹进入未知空间高速前进，但始终同时维护一条完全位于已知自由空间中的安全后备轨迹。**

其论文将环境划分为已知自由空间、占据空间和未知空间，主轨迹可以在已知自由与未知区域中优化，而安全后备轨迹始终保留在已知自由空间内。([arXiv](https://arxiv.org/abs/2001.04420?utm_source=chatgpt.com "FASTER: Fast and Safe Trajectory Planner for Navigation in Unknown Environments"))

---

## 11.2 核心设计理念

| 设计原则       | 说明                                     |
| -------------- | ---------------------------------------- |
| 双轨迹规划     | 同时维护高性能轨迹和安全后备轨迹         |
| 已知与未知分离 | 明确区分自由、占据和未知空间             |
| 安全提交机制   | 只有存在后备轨迹时才允许继续执行激进轨迹 |
| 凸安全走廊     | 将可行空间分解为若干凸区域               |
| MIQP优化       | 使用混合整数二次规划处理走廊和时间分配   |
| 动态时间分配   | 由求解器或启发式共同决定各轨迹段时间     |
| 轨迹滚动更新   | 每次重新观测环境后更新主轨迹和后备轨迹   |

---

# 11.3 系统设计逻辑

## 11.3.1 第一性原理：为什么“轨迹末端停止”很保守？

假设无人机的 LiDAR 只能看见前方20米。

传统安全规划器要求：

```text
在这20米已知区域内
生成一条最终速度为0的轨迹
```

这意味着无人机必须随时保证：

```text
在传感器可见范围内完全刹停
```

如果速度越来越快，制动距离越来越长：

```text
d_stop ≈ v² / 2a
```

当制动距离接近感知距离时，规划器就只能降低速度。

因此系统会出现：

```text
传感器看不远
    ↓
必须提前刹车
    ↓
无法高速飞行
```

---

## 11.3.2 第二性原理：为什么两条轨迹可以同时兼顾速度和安全？

FASTER将轨迹分成不同角色。

### Whole Trajectory

```text
高性能主轨迹
可以进入未知区域
追求速度和效率
```

### Safe Trajectory

```text
安全后备轨迹
完全位于已知自由空间
保证能够安全停止
```

### Committed Trajectory

```text
当前真正允许执行的轨迹段
```

逻辑类似于：

```text
主路线：
    继续高速向前探索

紧急出口：
    如果前面突然不可行
    立即沿已知安全路线停车
```

只有当新的后备轨迹求解成功后，才继续提交主轨迹的后续部分。

---

## 11.3.3 第三性原理：为什么需要安全走廊？

直接对轨迹上的每一点施加复杂障碍物约束很难求解。

FASTER先将自由空间表示成一系列凸多面体：

```text
Polyhedron 1
    ↓
Polyhedron 2
    ↓
Polyhedron 3
```

每段轨迹被约束在对应凸多面体中。

凸空间的好处是：

```text
两点之间的连线仍在空间内部
约束可以写成线性不等式
优化问题更容易求解
```

这比单纯使用障碍物软惩罚更适合构建明确的安全约束。

---

# 11.4 FASTER 的主要架构

```text
局部占据地图
      │
      ▼
空间分类
├─ Free Known
├─ Occupied
└─ Unknown
      │
      ▼
路径搜索
├─ 主路径：Free + Unknown
└─ 安全路径：仅Free
      │
      ▼
凸安全走廊生成
      │
      ▼
MIQP轨迹优化
├─ Whole Trajectory
└─ Safe Trajectory
      │
      ▼
安全提交检查
      │
      ├── 后备轨迹有效
      │      ↓
      │   执行主轨迹前段
      │
      └── 后备轨迹无效
             ↓
          继续安全轨迹
```

---

# 11.5 为什么使用 MIQP？

MIQP是：

```text
Mixed-Integer Quadratic Programming
混合整数二次规划
```

其中：

```text
连续变量：
    轨迹系数
    速度
    加速度
    时间

整数变量：
    某段轨迹属于哪个走廊
    某个离散模式是否启用
```

它的优势是可以表达：

```text
轨迹段必须选择某一个安全多面体
```

这种“二选一、多选一”的离散约束。

代价是：

```text
求解器依赖重
计算复杂度高
工程部署复杂
```

FASTER官方实现依赖 Gurobi，并主要测试于 ROS Kinetic、ROS Melodic 和对应的较早 Ubuntu 环境。([GitHub](https://github.com/mit-acl/faster "GitHub - mit-acl/faster: 3D Trajectory Planner in Unknown Environments · GitHub"))

---

# 11.6 FASTER 的安全保证应该怎么理解？

FASTER的安全不是无条件的。

它依赖假设：

```text
已知自由空间地图正确
障碍物膨胀合理
无人机能跟踪规划轨迹
动力学模型合理
规划和控制延迟受限
后备轨迹持续有效
```

如果发生：

```text
定位突然跳变
控制器严重跟踪失败
地图漏检障碍物
传感器时间戳错误
动态障碍物高速进入
```

原有保证可能不再成立。

所以 MoSim中必须将：

```text
规划安全
控制跟踪安全
感知可靠性
系统延迟
```

分开测试。

---

# 11.7 FASTER 与 EGO-Planner 的区别

| 维度       | EGO-Planner    | FASTER                 |
| ---------- | -------------- | ---------------------- |
| 核心目标   | 快速局部优化   | 高速下保留安全恢复能力 |
| 障碍处理   | 软碰撞代价为主 | 凸走廊硬约束为主       |
| 未知空间   | 通常偏保守处理 | 主轨迹可进入未知空间   |
| 后备轨迹   | 非核心机制     | 核心机制               |
| 优化器     | L-BFGS类       | MIQP/Gurobi            |
| 工程复杂度 | 较低           | 较高                   |
| 实时性能   | 通常更轻       | 求解开销较大           |

---

# 11.8 我们应该吸收 FASTER 哪些设计？

## 吸收一：主轨迹与后备轨迹分离

MoSim统一输出可以设计为：

```text
PlannerOutput
├─ nominal_trajectory
├─ backup_trajectory
├─ commit_horizon
└─ safety_status
```

---

## 吸收二：未知空间不是简单等于障碍物

地图状态应至少包含：

```text
FREE
OCCUPIED
UNKNOWN
```

不能把未知空间直接丢失。

---

## 吸收三：安全提交机制

轨迹生成成功不代表立刻执行。

必须经过：

```text
validate nominal
validate backup
check tracking envelope
commit prefix
```

---

## 吸收四：安全监督器独立于规划器

即使使用EGO或Diffusion Planner，也可以外挂：

```text
BackupTrajectoryGenerator
EmergencyStopPlanner
TrajectorySafetySupervisor
```

---

# 11.9 我们不应该照搬什么？

## 不照搬一：不要让 Gurobi 成为平台硬依赖

FASTER作为研究插件可以依赖 Gurobi。

但 MoSim 核心接口不应该要求：

```text
所有用户必须安装商业求解器
```

应允许：

```text
Gurobi
OSQP
qpOASES
其他优化后端
```

---

## 不照搬二：不要把双轨迹逻辑写死在一个规划器里

安全监督机制应该能服务：

```text
Fast-Planner
EGO-Planner
SUPER
Learning Planner
```

---

## 不照搬三：不要只测试静态未知环境

FASTER原始工作重点是未知环境中的高速安全导航。对于动态障碍物，还需要额外的预测与时空走廊机制。([arXiv](https://arxiv.org/abs/2001.04420?utm_source=chatgpt.com "FASTER: Fast and Safe Trajectory Planner for Navigation in Unknown Environments"))

---

# 11.10 在 MoSim 长期架构中的位置

```text
任意局部规划器
      │
      ▼
Nominal Trajectory
      │
      ▼
Trajectory Safety Supervisor
├─ Known-space check
├─ Stop-distance check
├─ Tracking-error inflation
├─ Backup trajectory
└─ Commit decision
      │
      ▼
Controller / PX4
```

FASTER在我们项目中的主要价值应当是：

```text
安全架构参考
双轨迹机制参考
未知空间处理参考
```

而不一定是默认规划器。

---

# 11.11 最小研究任务

```text
1. 跑通官方无人机仿真
2. 理清Free/Occupied/Unknown地图定义
3. 理清Whole/Safe/Committed轨迹关系
4. 理清凸多面体走廊生成
5. 理清MIQP变量和约束
6. 理清时间分配变量
7. 理清后备轨迹提交逻辑
8. 测试规划失败时的行为
9. 测试感知范围变化
10. 测试最大速度和制动距离关系
11. 抽取独立BackupTrajectory接口
12. 尝试替换非商业求解器
13. 写 FASTER REVIEW.md
```

---

# 11.12 对 FASTER 的最终判断

```text
是否进入长期项目：
    是

是否直接作为默认规划器：
    不一定

进入哪一层：
    安全轨迹研究插件
    Trajectory Safety Supervisor参考

主要吸收：
    双轨迹机制
    未知空间分类
    安全提交
    后备停车轨迹
    凸安全走廊

主要风险：
    Gurobi依赖
    ROS版本较旧
    求解复杂度高
    参数和模型假设较多
```

一句话：

> **FASTER 最重要的贡献不是某一种求解器，而是提出了“主轨迹负责快、后备轨迹负责活下来”的安全架构，这个思想可以独立于具体规划算法进入 MoSim。**

---

# 12. 项目概述：FAR Planner

## 12.1 定位

FAR Planner，全称：

```text
Fast, Attemptable Route Planner
```

是一套面向已知或未知大规模环境的高层路线规划器。

它与 Fast-Planner、EGO-Planner 最大的区别是：

```text
FAR Planner：
    决定从环境的哪条通道走
    输出全局路径或中间航点

EGO / Fast-Planner：
    决定未来几秒如何连续运动
    输出带时间的动力学轨迹
```

FAR Planner使用动态更新的可见性图，在导航过程中不断根据新观测增加或删除图边。它采用多边形环境表示，可以在已有地图中规划，也可以在未知环境中一边探索环境结构、一边尝试通向目标的路线。([arXiv](https://arxiv.org/abs/2110.09460?utm_source=chatgpt.com "FAR Planner: Fast, Attemptable Route Planner using Dynamic Visibility Update"))

---

## 12.2 核心设计理念

| 设计原则       | 说明                                      |
| -------------- | ----------------------------------------- |
| 高层路线规划   | 关注走哪条通道，不直接生成电机可执行轨迹  |
| 多边形环境表示 | 用障碍物边缘和多边形代替密集栅格          |
| 可见性图       | 两个节点之间若可直达，就建立图边          |
| 动态更新       | 新障碍出现时删除被遮挡的边                |
| Attemptable    | 地图不完整时仍尝试向目标推进              |
| 全局与局部分层 | FAR输出路线，下层局部规划器生成动力学轨迹 |
| 长距离导航     | 适合大型、复杂和未知环境                  |

---

# 12.3 系统设计逻辑

## 12.3.1 第一性原理：为什么大尺度规划不适合始终使用高分辨率体素A*？

假设地图尺寸为：

```text
1000 m × 1000 m × 100 m
```

如果使用0.1米体素，节点数量极其庞大。

而从全局角度看，很多局部细节并不重要。

例如绕过一栋建筑，只需要知道：

```text
建筑左边可以走
建筑右边可以走
两栋建筑之间存在通道
```

没有必要在全局搜索中遍历每个10厘米体素。

FAR Planner将环境抽象为：

```text
障碍物轮廓
关键边缘点
可见性关系
```

从而把密集空间变成稀疏图。

---

## 12.3.2 第二性原理：什么是可见性图？

节点通常来自障碍物边缘或轮廓关键点。

如果两个节点之间的直线没有被障碍物遮挡：

```text
Node A ───────── Node B
```

就建立一条可见性边。

于是路线搜索变成：

```text
起点
    ↓
可见节点1
    ↓
可见节点2
    ↓
目标
```

可见性图往往能够生成较短的折线路径，因为路径会沿障碍物边缘绕行。

---

## 12.3.3 第三性原理：“Attemptable”是什么意思？

未知环境中，规划器无法提前证明目标可达。

例如：

```text
当前只看见一条走廊入口
不知道里面是出口还是死胡同
```

传统规划器可能认为：

```text
未知 = 不可通行
```

然后直接报告目标不可达。

FAR的策略是：

```text
根据当前环境结构选择一条有希望的路线
    ↓
向前行驶
    ↓
获得新观测
    ↓
更新可见性图
    ↓
如果发现死路，尝试其他路线
```

所以它不是保证这条路线一定成功，而是：

```text
可以尝试
可以发现失败
可以快速重新选择
```

---

# 12.4 FAR Planner 的主要架构

```text
LiDAR点云
    │
    ▼
地形分析 / 可通行区域
    │
    ▼
障碍物边缘提取
    │
    ▼
多边形构建
    │
    ▼
动态可见性图
├─ 增加新节点
├─ 增加新可见边
└─ 删除被遮挡边
    │
    ▼
图搜索
    │
    ▼
全局路线 / 中间航点
    │
    ▼
局部轨迹规划器
    │
    ▼
控制器
```

官方系统明确将 FAR Planner 运行在导航系统高层，下层仍由地形分析、航点跟踪以及生成动力学可行轨迹的局部规划器完成实际运动。([远程规划师](https://www.far-planner.com/far-planner "FAR Planner"))

---

# 12.5 FAR Planner 和局部规划器的关系

正确组合是：

```text
FAR Planner
    ↓
生成全局路径
    ↓
选择当前局部目标
    ↓
EGO / Fast-Planner / SUPER
    ↓
生成未来数秒时间轨迹
```

不能这样使用：

```text
FAR Planner
    ↓
直接连接PX4电机控制
```

因为 FAR 路径通常缺少：

```text
时间参数
速度连续性
加速度连续性
姿态要求
电机约束
```

---

# 12.6 原始 FAR 与 Air-FAR 的关系

原始 FAR Planner重点是动态可见性图和高层路线规划。

后续 Air-FAR 将这一思路进一步扩展到面向空中机器人的大规模复杂三维未知环境，使用三维多面体和多层可见性图处理更完整的空中导航问题。([远程规划师](https://www.far-planner.com/air-far-planner?utm_source=chatgpt.com "Air-FAR Planner"))

因此对我们而言：

```text
FAR Planner：
    学习动态可见性图和高层分层思想

Air-FAR：
    更直接对应三维无人机全局路线
```

不要把原始 FAR 误认为已经完整解决了四旋翼三维动力学轨迹问题。

---

# 12.7 FAR Planner 与探索规划的区别

FAR解决的是：

```text
已知一个目标
设法找到到达目标的路线
```

探索规划解决的是：

```text
没有最终明确目标
选择哪里最值得继续观察
最大化未知区域信息增益
```

所以：

```text
FAR：
    Goal-directed route planning

Exploration Planner：
    Next-best-view / frontier selection
```

二者可以组合：

```text
探索器选择下一个frontier
    ↓
FAR规划到frontier的全局路线
    ↓
局部规划器生成轨迹
```

---

# 12.8 我们应该吸收哪些设计？

## 吸收一：全局路线与局部轨迹严格分层

定义两个接口：

```text
IGlobalRoutePlanner
ILocalTrajectoryPlanner
```

---

## 吸收二：稀疏拓扑图

大型环境不应始终使用高分辨率体素图做全局搜索。

可维护：

```text
Visibility Graph
Skeleton Graph
Topological Graph
Roadmap
```

---

## 吸收三：动态图更新

新观测到来时，不要每次重建整个全局图。

应支持：

```text
addVertex
removeVertex
addEdge
invalidateEdge
updateLocalRegion
```

---

## 吸收四：可尝试状态

规划结果不应只有：

```text
SUCCESS
FAILED
```

还可以有：

```text
REACHABLE
TEMPORARILY_BLOCKED
ATTEMPTING_UNKNOWN
DEAD_END
GOAL_UNCONFIRMED
```

---

# 12.9 我们不应该照搬什么？

## 不照搬一：不要让二维地形假设限制无人机

四旋翼需要考虑：

```text
上方通道
下方通道
垂直井道
立交结构
树冠和电线
```

因此最终需要真正的三维图表示。

---

## 不照搬二：不要将多边形提取写死在点云前端中

环境抽象应该可替换：

```text
2D polygon
3D polyhedron
voxel skeleton
mesh boundary
semantic corridor
```

---

## 不照搬三：不要认为全局路径一定可直接跟踪

全局路径必须经过：

```text
局部可行性检查
速度规划
轨迹平滑
安全走廊
```

---

# 12.10 在 MoSim 长期架构中的位置

```text
Mission Manager
      │
      ▼
FAR / Air-FAR Adapter
      │
      ▼
GlobalRoute
├─ route nodes
├─ corridor ids
├─ unknown flags
└─ route cost
      │
      ▼
Local Goal Selector
      │
      ▼
EGO / Fast-Planner / SUPER
      │
      ▼
Trajectory
```

---

# 12.11 最小研究任务

```text
1. 跑通官方开发环境
2. 理清点云到边缘点的过程
3. 理清多边形构建
4. 理清可见性节点和边
5. 理清双层数据结构
6. 理清新障碍如何删除旧边
7. 理清已知地图和未知地图两种模式
8. 查看FAR与局部规划器接口
9. 构造大型迷宫测试
10. 构造死胡同测试
11. 对比A*、D* Lite和FAR
12. 调研Air-FAR三维扩展
13. 定义统一GlobalRoute接口
14. 写 FAR Planner REVIEW.md
```

---

# 12.12 对 FAR Planner 的最终判断

```text
是否进入长期项目：
    是

进入哪一层：
    全局路线规划层

主要吸收：
    动态可见性图
    稀疏拓扑表示
    Attemptable导航
    全局局部分层
    增量图更新

不承担：
    连续动力学轨迹
    姿态控制
    电机控制
    完整探索决策
```

一句话：

> **FAR Planner 最重要的价值，是让我们明确“全局找通道”和“局部生成可执行轨迹”必须分成两层；它适合告诉无人机往哪里绕，但不负责告诉无人机每一毫秒具体怎么飞。**

---

# 13. 项目概述：Diffusion-Planner

## 13.1 定位

这里的 `diff` 指：

```text
ZhengYinan-AIR/Diffusion-Planner
```

它是一套基于扩散模型的自动驾驶规划器，而不是现成的无人机规划器。

它的核心目标是：

> **根据道路、周围交通参与者、自车历史状态和场景信息，利用条件扩散模型生成未来驾驶轨迹。**

该项目论文发表于 ICLR 2025，并获得 Oral。官方实现围绕 nuPlan 自动驾驶基准组织训练和闭环评测，模型采用基于 Transformer 的扩散规划框架，同时联合建模交通参与者预测和自车规划，并支持灵活的 guidance。([Zheng Yinan](https://zhengyinan-air.github.io/Diffusion-Planner/?utm_source=chatgpt.com "Diffusion-Planner"))

---

## 13.2 核心设计理念

| 设计原则     | 说明                             |
| ------------ | -------------------------------- |
| 数据驱动规划 | 从大量驾驶数据中学习规划行为     |
| 扩散生成     | 从噪声逐步恢复出合理未来轨迹     |
| 多模态行为   | 同一场景可以生成多种合理方案     |
| 预测规划联合 | 同时理解其他交通参与者和自车轨迹 |
| 条件引导     | 在采样过程中加入安全、风格等偏好 |
| 闭环评测     | 轨迹执行后继续影响后续场景       |
| 场景编码     | 将道路、车辆和历史状态编码为条件 |

---

# 13.3 系统设计逻辑

## 13.3.1 第一性原理：传统回归规划为什么容易“平均”多个方案？

假设车辆前方有慢车：

```text
方案一：
    跟车减速

方案二：
    向左变道

方案三：
    向右变道
```

三个方案都合理。

普通神经网络如果使用均方误差回归一条轨迹，可能学到：

```text
三种方案的平均值
```

结果可能是：

```text
既没有完全减速
也没有完成变道
轨迹位于车道线附近
```

扩散模型不是直接输出唯一答案，而是学习：

```text
合理轨迹的概率分布
```

因此可以表示多个可能的驾驶行为。

---

## 13.3.2 第二性原理：扩散模型怎么生成轨迹？

训练时：

```text
真实未来轨迹
    ↓
逐渐加入噪声
    ↓
得到带噪轨迹
```

模型学习：

```text
给定场景和带噪轨迹
如何预测去噪方向
```

推理时：

```text
随机噪声轨迹
    ↓
去噪一步
    ↓
再去噪一步
    ↓
……
    ↓
合理未来轨迹
```

可以抽象成：

```text
xT ~ Gaussian Noise

xT
 ↓ denoise
xT-1
 ↓ denoise
xT-2
 ↓
x0 = planned trajectory
```

---

## 13.3.3 第三性原理：什么是 Guidance？

基础扩散模型学习的是：

```text
人类驾驶轨迹分布
```

但当前任务可能需要强调：

```text
更安全
更舒适
更激进
更保守
离障碍物更远
尽量靠近参考路线
```

Guidance相当于在每一步去噪时增加一个偏好方向：

```text
生成分布的梯度
    +
安全/风格目标的梯度
```

这样不必为每一种行为风格训练完全独立的模型。

Diffusion-Planner论文强调通过灵活的 classifier guidance 调整规划行为，同时建模多模态驾驶行为。([arXiv](https://arxiv.org/abs/2501.15564?utm_source=chatgpt.com "Diffusion-Based Planning for Autonomous Driving with Flexible Guidance"))

---

# 13.4 Diffusion-Planner 的主要架构

```text
地图与车道信息
        │
周围交通参与者状态
        │
自车历史轨迹
        │
        ▼
场景编码器
        │
        ▼
条件特征
        │
        ├──────────────┐
        │              │
随机噪声轨迹      Guidance目标
        │              │
        └──────┬───────┘
               ▼
        Diffusion Transformer
               │
        多步轨迹去噪
               │
               ▼
        未来自车轨迹
               │
               ▼
          闭环仿真评测
```

---

# 13.5 为什么它不能直接用于四旋翼？

汽车与四旋翼的状态空间不同。

### 汽车

```text
主要在二维道路上运动
存在车道和交通规则
不能横向瞬移
控制量通常为：
    转向
    油门
    制动
```

### 四旋翼

```text
三维自由空间
没有固定车道
可以水平和垂直运动
状态包含：
    三维位置
    三维速度
    姿态
    角速度

需要满足：
    最大推力
    最大倾角
    最大角速度
    电机动态
```

汽车轨迹模型通常输出：

```text
x(t), y(t), heading(t)
```

无人机至少需要：

```text
x(t), y(t), z(t)
velocity(t)
acceleration(t)
yaw(t)
```

甚至需要进一步验证姿态和推力可行性。

---

# 13.6 把它改成无人机版本需要什么？

至少需要重新设计以下部分。

## 场景表示

汽车：

```text
车道
路口
车辆
行人
交通灯
```

无人机：

```text
三维占据地图
点云
安全走廊
局部ESDF
其他无人机
传感器视场
```

## 轨迹表示

```text
3D位置序列
+
速度/加速度
+
航向
```

## 数据集

需要采集：

```text
专家规划器轨迹
实机飞行轨迹
不同环境避障轨迹
不同速度和风扰轨迹
```

## 约束

需要加入：

```text
碰撞检查
动力学可行性
最大倾角
最大推力
制动距离
后备轨迹
```

---

# 13.7 Diffusion-Planner 与传统规划器的关系

不应该设计成：

```text
扩散模型替代所有传统模块
```

更稳妥的方式是：

```text
Diffusion Model
    ↓
生成多条候选轨迹
    ↓
传统验证器
├─ 碰撞检查
├─ 动力学检查
├─ 安全走廊检查
└─ 后备轨迹检查
    ↓
选择可执行轨迹
```

也可以让扩散模型只负责：

```text
初始轨迹
拓扑选择
行为决策
局部目标
```

然后交给传统优化器精修。

---

# 13.8 训练模式与部署模式

## 训练模式

```text
数据集
    ↓
轨迹与场景预处理
    ↓
PyTorch训练
    ↓
模型checkpoint
```

官方工程依赖 nuPlan 数据与开发工具，并提供数据预处理、训练、闭环模拟和模型检查点相关流程。([GitHub](https://github.com/ZhengYinan-AIR/Diffusion-Planner "GitHub - ZhengYinan-AIR/Diffusion-Planner: [ICLR 2025 Oral] The official implementation of &quot;Diffusion-Based Planning for Autonomous Driving with Flexible Guidance&quot; · GitHub"))

## 部署模式

```text
当前场景
    ↓
模型推理
    ↓
候选轨迹
    ↓
安全验证
    ↓
轨迹控制器
```

无人机实时部署还需要解决：

```text
推理延迟
模型确定性
GPU资源
异常输入
分布外环境
安全回退
```

---

# 13.9 我们应该吸收哪些设计？

## 吸收一：规划可以表示为概率分布

传统规划器通常只生成：

```text
一条最优轨迹
```

扩散模型可以生成：

```text
多种合理轨迹
```

这适合：

```text
不同拓扑绕行
多机交互
行为预测
不确定环境
```

---

## 吸收二：候选生成与安全验证分离

学习模型负责：

```text
提出方案
```

传统模块负责：

```text
审查方案
```

---

## 吸收三：联合预测与规划

其他移动对象的未来行为会影响规划。

长期可以建立：

```text
预测其他无人机
+
生成本机轨迹
```

的联合模型。

---

## 吸收四：Guidance接口

MoSim可以定义：

```text
Guidance
├─ obstacle_clearance
├─ energy
├─ speed
├─ comfort
├─ formation
└─ risk
```

---

# 13.10 我们不应该照搬什么？

## 不照搬一：不要直接使用汽车数据结构

nuPlan的车道、车辆和地图表示不能直接成为无人机接口。

---

## 不照搬二：不要把神经网络输出直接送给控制器

必须经过独立验证。

---

## 不照搬三：不要把高闭环得分等同于形式化安全

数据驱动方法的优秀平均性能不代表：

```text
所有极端场景都安全
```

---

## 不照搬四：不要一开始就训练端到端无人机规划器

应该先从：

```text
生成初始路径
生成局部目标
生成多拓扑候选
```

开始。

---

# 13.11 在 MoSim 长期架构中的位置

```text
Learning Planning/
└─ DiffusionTrajectoryGenerator
       │
       ▼
Candidate Trajectories
       │
       ▼
Trajectory Validator
├─ Collision
├─ Dynamics
├─ Visibility
├─ Tracking Envelope
└─ Backup Trajectory
       │
       ▼
Selected Trajectory
```

目录建议：

```text
Planning/
├─ Classical/
│  ├─ FastPlanner
│  ├─ EGO
│  ├─ FASTER
│  └─ SUPER
│
├─ Global/
│  └─ FAR
│
└─ Learning/
   └─ DiffusionPlanner
```

---

# 13.12 最小研究任务

```text
1. 跑通官方nuPlan闭环评测
2. 理清数据预处理格式
3. 理清场景编码输入
4. 理清未来轨迹表示
5. 理清噪声注入和去噪过程
6. 理清Transformer输入输出
7. 理清guidance实现
8. 生成多条轨迹并可视化差异
9. 统计推理时间
10. 用简化3D点机器人数据重训练
11. 加入传统碰撞验证器
12. 尝试用Fast-Planner轨迹构建训练集
13. 设计无人机DiffusionTrajectory接口
14. 写 Diffusion-Planner REVIEW.md
```

---

# 13.13 对 Diffusion-Planner 的最终判断

```text
是否进入长期项目：
    是，作为研究分支

是否直接进入当前无人机主链：
    否

进入哪一层：
    学习式候选轨迹生成
    行为和拓扑规划研究

主要吸收：
    多模态轨迹生成
    扩散式规划
    Guidance
    预测规划联合
    闭环评测

不承担：
    当前默认无人机局部规划
    直接安全保证
    电机和姿态控制
```

一句话：

> **Diffusion-Planner 对我们最大的意义，不是直接拿汽车模型控制无人机，而是提供一种“从数据中学习多种合理轨迹，再用传统安全模块筛选”的新规划范式。**

---

# 14. 项目概述：SUPER

## 14.1 定位

SUPER，全称：

```text
Safety-assured High-speed Navigation for MAVs
```

是一套面向微型无人机高速自主导航的完整系统。

它和前面项目最大的区别是：

```text
Fast-Planner / EGO：
    更偏单个规划算法框架

FASTER：
    更偏安全轨迹机制

SUPER：
    将地图、走廊、轨迹优化、安全后备、
    仿真、任务状态机和硬件平台组织成完整系统
```

SUPER论文发表于2025年的 Science Robotics。当前公开仓库提供规划模块、ROG-Map、仿真环境和任务管理等组件，并同时支持 ROS1 和 ROS2 构建；官方目前仍将 ROS1 Noetic 标为 Tier 1 支持平台，ROS2版本处于继续完善阶段。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

对我们的 Sunray-150 + MID360 + PX4 + ROS2 路线而言，SUPER是这一组项目中最接近我们最终目标的系统参考。

---

## 14.2 核心设计理念

| 设计原则        | 说明                                     |
| --------------- | ---------------------------------------- |
| 系统级高速导航  | 不只优化轨迹，还考虑地图、感知和执行     |
| LiDAR优先       | 依靠高频三维激光雷达在复杂环境中感知障碍 |
| Robocentric地图 | 重点维护无人机周围的局部高分辨率地图     |
| 安全走廊        | 将无碰撞空间转换为凸多面体序列           |
| 可微轨迹优化    | 使用高效连续优化生成高质量轨迹           |
| 双轨迹框架      | 同时维护性能轨迹与安全轨迹               |
| 任务状态机      | 管理起飞、规划、执行、重规划和异常状态   |
| 日志与调参      | 内置重规划和控制指令日志                 |
| ROS1/ROS2兼容   | 通过脚本选择编译目标                     |

SUPER官方仓库说明，其轨迹优化以 GCOPTER 为重要基础，CIRI建立在 FIRI 安全走廊方法之上，并吸收了 FASTER 双轨迹框架的思想。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

---

# 14.3 系统设计逻辑

## 14.3.1 第一性原理：为什么高速飞行不能只靠更快的优化器？

高速飞行时，问题不是单独的：

```text
规划速度不够快
```

而是完整链路都必须跟上：

```text
LiDAR看得够远吗？
点云更新够快吗？
里程计延迟多大？
地图能否实时更新？
路径能否快速生成？
轨迹能否满足动力学？
控制器能否跟踪？
出现新障碍时能否安全刹停？
```

如果任何一个环节延迟过大：

```text
总延迟 × 飞行速度 = 额外前进距离
```

例如：

```text
飞行速度：15 m/s
系统总延迟：0.2 s

延迟期间前进：
    3 m
```

所以高速导航必须是系统问题，而不是只替换一个规划算法。

---

## 14.3.2 第二性原理：为什么需要 Robocentric Map？

传统全局高分辨率体素地图需要维护：

```text
整个环境
```

但局部轨迹规划只关心：

```text
无人机附近
未来几秒可能经过的空间
```

ROG-Map采用机器人中心式占据地图：

```text
无人机位于地图局部窗口中心附近
无人机移动时地图窗口随之滑动
```

这样可以：

```text
保持固定内存规模
重点维护局部高分辨率
快速更新障碍膨胀
支持大型环境连续飞行
```

SUPER仓库将 ROG-Map作为核心映射组件，相关论文将其定位为面向大场景和高分辨率激光规划的高效机器人中心占据地图。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

---

## 14.3.3 第三性原理：为什么要先生成安全走廊，再优化轨迹？

如果直接对复杂点云中的每个障碍点建立约束：

```text
约束数量巨大
几何关系复杂
优化不稳定
```

安全走廊将环境简化为：

```text
一串无碰撞凸多面体
```

例如：

```text
[Poly 1] → [Poly 2] → [Poly 3]
```

轨迹只需要满足：

```text
第1段位于Poly 1
第2段位于Poly 2
第3段位于Poly 3
```

这样将：

```text
复杂点云避障问题
```

转换为：

```text
凸多面体约束下的轨迹优化问题
```

CIRI负责在配置空间中生成安全飞行走廊，而 SUPER 的 CIRI建立在 FIRI方法之上。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

---

## 14.3.4 第四性原理：为什么 SUPER 仍然需要双轨迹？

高速性能轨迹通常希望：

```text
尽量向前
速度更高
路径更直接
```

安全轨迹希望：

```text
始终可恢复
始终可停止
保留足够安全余量
```

两者目标并不完全一致。

SUPER吸收 FASTER 的双轨迹思想：

```text
Performance Trajectory
    追求高速和效率

Backup / Safe Trajectory
    负责异常情况下安全恢复
```

因此 SUPER 并不是简单地“把EGO调得更快”，而是：

```text
高速地图
+
安全走廊
+
连续轨迹优化
+
双轨迹安全逻辑
+
完整任务管理
```

---

# 14.4 SUPER 的主要架构

```text
MID360 / LiDAR
       │
       ▼
LiDAR-Inertial Odometry
FAST-LIO / FAST-LIVO等
       │
       ▼
世界坐标系点云
       │
       ▼
ROG-Map
├─ 局部占据地图
├─ 障碍物膨胀
├─ 地图滑动
└─ 可选距离查询
       │
       ▼
路径搜索
       │
       ▼
CIRI安全走廊
       │
       ▼
SUPER Trajectory Optimizer
├─ GCOPTER式可微优化
├─ 动力学约束
├─ 走廊约束
├─ 性能轨迹
└─ 安全轨迹
       │
       ▼
Mission Planner
├─ 状态管理
├─ 重规划
├─ 轨迹提交
└─ 异常处理
       │
       ▼
Trajectory Command
       │
       ▼
Controller / PX4
```

---

# 14.5 SUPER 的主要源码层次

官方仓库目前主要包含：

```text
mars_uav_sim
    无人机和点云地图仿真

mission_planner
    任务状态机
    目标管理
    系统调度

rog_map
    Robocentric占据地图

super_planner
    路径、走廊、轨迹优化和重规划核心

scripts
    ROS版本选择
    构建和辅助脚本
```

这一目录结构反映出：

```text
仿真环境
地图
轨迹算法
任务管理
```

已经被显式拆开，而不是全部塞入一个 ROS 节点。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

---

# 14.6 SUPER 与 FAST-LIO / FAST-LIVO 的关系

SUPER规划器需要：

```text
无人机状态
+
世界坐标系中的障碍物点云
```

状态估计系统可以是：

```text
FAST-LIO2
FAST-LIVO2
其他LiDAR-Inertial Odometry
仿真器真值
```

但要注意官方仓库当前有一个重要接口约束：

> 使用自己的仿真器或其他里程计系统时，输入 ROG-Map 的点云必须已经转换到世界坐标系；当前实现不会依靠 `frame_id` 或 TF 自动完成转换。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

这意味着我们接 Gazebo 时必须明确：

```text
Gazebo生成LiDAR点云
    ↓
传感器坐标系
    ↓
根据位姿转换
    ↓
世界坐标系点云
    ↓
ROG-Map
```

不能假设它会自动查 TF。

---

# 14.7 SUPER 与 PX4 的关系

SUPER规划器本身不等于完整PX4控制器。

它生成：

```text
位置
速度
加速度
航向
时间轨迹
```

后续仍需要：

```text
轨迹跟踪控制
姿态控制
角速度控制
电机控制
```

完整链路：

```text
SUPER
    ↓
Trajectory Command
    ↓
Position / SE(3) Controller
    ↓
PX4 Attitude Setpoint
    ↓
PX4 Rate Controller
    ↓
Motor Mixer
```

SUPER硬件生态中包含基于 PX4 的紧凑飞控平台参考，但公开规划仓库的控制模块文档目前仍不算完整，官方 TODO 也明确列出后续补充控制模块和真实硬件部署教程。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

---

# 14.8 SUPER 与 ROS2 的关系

SUPER仓库可通过脚本选择：

```text
ROS1
ROS2
```

当前公开说明是：

```text
ROS1 Noetic：
    Tier 1支持

ROS2 Foxy：
    已提供构建和示例
    仍在开发和完善
```

官方同时提醒 ROS2版本可能存在可视化等不稳定问题。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

因此我们的策略应该是：

```text
先研究算法核心和接口
    ↓
在隔离工作区跑通官方ROS2版本
    ↓
编写MoSim Adapter
    ↓
不要让SUPER的内部消息成为平台公共标准
```

---

# 14.9 SUPER 与 Gazebo 的关系

官方示例主要使用自己的 `mars_uav_sim` 和点云地图。

但 SUPER可以接入 Gazebo，只要我们提供：

```text
世界坐标系点云
正确里程计
目标点
正确时间戳
控制接口
```

推荐链路：

```text
Gazebo
├─ 飞行动力学
├─ MID360模拟
└─ 碰撞真值
       │
       ▼
ROS2点云和里程计
       │
       ▼
World-frame Cloud Adapter
       │
       ▼
SUPER
       │
       ▼
轨迹控制器 / PX4
```

---

# 14.10 SUPER 与 UE 的关系

UE不应该进入 SUPER 核心闭环。

推荐：

```text
Gazebo：
    物理和LiDAR权威

SUPER：
    地图和规划

PX4：
    控制

UE：
    高真实感展示
```

UE可以显示：

```text
ROG-Map
全局目标
搜索路径
安全走廊
主轨迹
后备轨迹
当前飞行状态
```

但不要让 UE Tick 决定规划时间。

---

# 14.11 SUPER 和前面几个项目的关系

```text
Fast-Planner：
    搜索 + B-spline + ESDF的经典路线

EGO-Planner：
    去掉ESDF，强调轻量梯度优化

FASTER：
    双轨迹和安全后备思想

SUPER：
    ROG-Map
    +
    CIRI安全走廊
    +
    GCOPTER式轨迹优化
    +
    FASTER式双轨迹
    +
    完整任务系统
```

SUPER官方仓库也明确列出 GCOPTER、FIRI、FASTER 等项目对其规划框架的基础作用。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

---

# 14.12 我们应该吸收 SUPER 哪些设计？

## 吸收一：规划系统而不是单一算法

MoSim不能只有：

```text
plan(start, goal)
```

还需要：

```text
Map Manager
Planner
Safety Manager
Mission FSM
Trajectory Server
Logger
```

---

## 吸收二：Robocentric局部地图

适合：

```text
MID360
高速局部避障
大范围连续飞行
固定内存预算
```

---

## 吸收三：安全走廊作为统一中间表示

不同规划器都可以使用：

```text
SafeCorridor
```

接口：

```text
polytopes
time_intervals
overlap
clearance
```

---

## 吸收四：双轨迹输出

```text
nominal_trajectory
backup_trajectory
```

应成为 MoSim 可选标准接口。

---

## 吸收五：任务状态机

例如：

```text
INIT
WAIT_ODOM
WAIT_MAP
TAKEOFF
IDLE
PLAN
EXECUTE
REPLAN
EMERGENCY_STOP
LAND
```

---

## 吸收六：日志系统

SUPER会记录控制指令和重规划日志，并提供轨迹质量分析工具。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

MoSim也应该记录：

```text
每次规划输入
规划耗时
失败原因
候选路径
轨迹cost
最小障碍距离
跟踪误差
后备轨迹状态
```

---

# 14.13 我们不应该照搬什么？

## 不照搬一：不要把所有SUPER参数暴露给平台用户

官方仓库也承认当前参数很多，调参工作量大。([GitHub](https://github.com/hku-mars/SUPER "GitHub - hku-mars/SUPER · GitHub"))

应划分：

```text
普通用户参数
高级规划参数
内部数值参数
```

---

## 不照搬二：不要默认所有点云已经在世界坐标系

Adapter层必须显式检查：

```text
source_frame
target_frame
timestamp
transform_valid
```

---

## 不照搬三：不要把 SUPER 变成唯一后端

MoSim还需要支持：

```text
EGO
Fast-Planner
FASTER
自研规划器
学习式规划器
```

---

## 不照搬四：不要让规划器内部状态机接管整个平台

MoSim应有更高层的统一 Mission Manager。

SUPER内部状态机作为插件子状态机运行。

---

## 不照搬五：不要忽略真实机体和跟踪误差

高速安全不仅是几何无碰撞。

还要考虑：

```text
无人机尺寸
MID360突出部分
跟踪误差
制动距离
最大推力
倾角限制
电机退化
风扰
```

---

# 14.14 在 MoSim 长期架构中的位置

```text
                     Mission Manager
                           │
                           ▼
┌─────────────────────────────────────────────┐
│              SUPER Adapter                  │
│                                             │
│  ROG-Map → Path → CIRI → Trajectory Opt    │
│                  │                          │
│                  ├─ Nominal Trajectory      │
│                  └─ Backup Trajectory       │
└──────────────────┬──────────────────────────┘
                   ▼
       MoSim Trajectory Safety Supervisor
                   ▼
           Unified Controller API
                   ▼
             PX4 / Custom Controller
                   ▼
                Gazebo Physics
```

SUPER适合作为：

```text
当前MID360无人机主参考系统
高级局部规划插件
高速安全导航实验基线
```

但平台架构仍应保持多规划器可替换。

---

# 14.15 最小研究任务

```text
1. 跑通click demo
2. 跑通dense benchmark
3. 跑通high-speed benchmark
4. 理清mission_planner状态机
5. 理清ROG-Map输入和地图滑动
6. 理清路径搜索
7. 理清CIRI安全走廊
8. 理清GCOPTER式轨迹优化
9. 理清双轨迹框架
10. 理清重规划触发条件
11. 使用自定义PCD地图
12. 读取cmd_logs和replan_logs
13. 跑通ROS2版本
14. 接入Gazebo世界坐标点云
15. 接入Sunray-150参数
16. 接入MID360扫描模型
17. 接入PX4轨迹跟踪
18. 测试高速、风扰和电机退化
19. 写 SUPER REVIEW.md
```

---

# 14.16 SUPER REVIEW.md 应该写什么

```text
1. 项目定位
    基于LiDAR的高速安全无人机导航系统

2. 它解决什么问题
    高速未知环境导航
    局部地图
    安全走廊
    双轨迹
    在线重规划

3. 核心组件
    mission_planner
    super_planner
    ROG-Map
    CIRI
    trajectory optimizer
    mars_uav_sim

4. 核心输入
    世界坐标点云
    里程计
    目标点
    动力学参数

5. 核心输出
    性能轨迹
    安全轨迹
    规划状态
    日志

6. 我们吸收什么
    系统级分层
    Robocentric地图
    安全走廊
    双轨迹
    任务状态机
    日志系统

7. 不照搬什么
    内部ROS消息
    过多参数
    世界坐标点云隐式假设
    唯一规划器架构

8. 第一阶段用途
    Gazebo + MID360 + PX4规划验证

9. 长期用途
    MoSim默认高级局部规划参考
```

---

# 14.17 对 SUPER 的最终判断

```text
是否进入长期项目：
    是，且优先级最高

是否作为唯一规划器：
    否

进入哪一层：
    高级局部导航系统
    高速安全规划参考实现

主要吸收：
    ROG-Map
    CIRI
    GCOPTER式轨迹优化
    双轨迹
    Mission FSM
    日志和调参体系
    ROS1/ROS2隔离适配

主要风险：
    参数很多
    ROS2仍在完善
    实机部署文档不完整
    点云坐标系接口严格
    完整控制模块仍需我们补齐
```

一句话：

> **SUPER 是目前最接近我们“Sunray-150 + MID360 + PX4 + ROS2 + Gazebo”目标的完整参考系统；我们应该把它作为主研究对象，但要拆解吸收其地图、走廊、双轨迹、状态机和日志设计，而不是让整个 MoSim 被 SUPER 的内部接口绑死。**

---

# 15. 这七个项目在 MoSim 中的最终分层

```text
任务层
│
├─ Mission Manager
│
▼
全局路线层
│
├─ FAR Planner
├─ Air-FAR
└─ A* / D* / Skeleton Planner
│
▼
局部轨迹层
│
├─ Fast-Planner
├─ EGO-Planner
├─ FASTER
├─ SUPER
└─ Diffusion Candidate Generator
│
▼
多机协调层
│
└─ EGO-Planner-Swarm
│
▼
安全监督层
│
├─ Trajectory Validator
├─ Backup Trajectory Generator
├─ Emergency Stop
└─ Commit Supervisor
│
▼
轨迹跟踪控制
│
▼
PX4
│
▼
Gazebo / 实机
```

最终可以这样理解：

```text
Fast-Planner：
    学习经典搜索 + 优化

EGO-Planner：
    学习轻量无ESDF优化

EGO-Planner-Swarm：
    学习分布式多机轨迹去冲突

FASTER：
    学习主轨迹 + 安全后备轨迹

FAR Planner：
    学习大尺度全局路线规划

Diffusion-Planner：
    学习数据驱动、多模态候选轨迹生成

SUPER：
    学习如何把地图、走廊、轨迹、安全和任务状态机
    组成真正可运行的高速无人机导航系统
```

我们的实际研究优先顺序应当是：

```text
第一阶段：
    Fast-Planner
    EGO-Planner
    SUPER

第二阶段：
    FASTER
    FAR / Air-FAR

第三阶段：
    EGO-Swarm
    Diffusion-Planner
```

其中当前主线最合理的是：

```text
FAR / Air-FAR
        ↓
SUPER
        ↓
MoSim Safety Supervisor
        ↓
轨迹跟踪控制器
        ↓
PX4
        ↓
Gazebo + MID360
```

而 Fast-Planner、EGO、FASTER 和 Diffusion-Planner作为可替换插件与对照基线长期保留。
