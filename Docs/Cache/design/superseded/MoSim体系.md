> 状态：旧版研究草案。
>
> 本文只作为 MoSim 控制体系早期设计输入，不作为当前执行依据。
> 当前正式执行依据为 `MoSim控制体系总览.md`、`MoSim研发工作流与Agent任务编排规范.md`
> 以及 `MoSim-CTRL-02` 至 `MoSim-CTRL-09` 系列规范。若本文与正式规范冲突，
> 以正式规范和 WF-01 当前阶段冻结规则为准。

---

不考虑开发时间，**MoSim不应该只做一个“控制器文件夹集合”**，而应该建设成完整的四旋翼：

> **轨迹生成—规划—单机跟踪—鲁棒增强—控制分配—故障容错—编队协同—安全监督—自动测试体系。**

这里要先纠正命名：EGO-Planner、Fast-Planner、SUPER属于**规划器**；PID、SE(3)、DFBC、MPC、NMPC才是轨迹跟踪控制器；INDI、L1、AWFF通常属于控制增强模块；故障隔离和控制分配又是另一层。

PX4本身也是按照位置、速度、姿态、角速度和控制分配的串级架构组织，位置和速度外环可被绕过。MoSim最好采用类似的分层接口，但允许每一层自由替换。([PX4文档][1])

---

# 一、MoSim完整控制体系总图

```text
任务与场景
目标点、航点、队形、障碍物
              ↓
┌──────────────────────────────┐
│ 1. 参考轨迹与在线规划层       │
│ 轨迹发生器 / EGO / FAST / SUPER│
└──────────────────────────────┘
              ↓
统一轨迹接口
p、v、a、jerk、snap、yaw
              ↓
┌──────────────────────────────┐
│ 2. 编队与多机协同层           │
│ 虚拟结构 / 一致性 / DMPC      │
└──────────────────────────────┘
              ↓
┌──────────────────────────────┐
│ 3. 安全过滤层                 │
│ 限幅 / CBF-QP / 防碰撞        │
└──────────────────────────────┘
              ↓
┌──────────────────────────────┐
│ 4. 单机轨迹跟踪控制层         │
│ PID / LQR / SE3 / DFBC / MPC  │
└──────────────────────────────┘
              ↓
期望姿态、角速度、推力或力矩
              ↓
┌──────────────────────────────┐
│ 5. 鲁棒与自适应增强层         │
│ INDI / L1 / AWFF / ESO / DOB  │
└──────────────────────────────┘
              ↓
┌──────────────────────────────┐
│ 6. 姿态与角速度内环           │
│ Quaternion / SO3 / PID / INDI │
└──────────────────────────────┘
              ↓
期望总推力和三轴力矩
              ↓
┌──────────────────────────────┐
│ 7. 故障容错与控制分配层       │
│ FDI / QP分配 / 在线重构       │
└──────────────────────────────┘
              ↓
各电机推力、转速或电压
              ↓
┌──────────────────────────────┐
│ 8. 电机、电调与四旋翼模型     │
└──────────────────────────────┘
```

另外必须有一个独立的：

```text
Controller Manager
健康监测、模式切换、降级控制、无扰切换、应急控制
```

---

# 二、参考轨迹与规划体系

严格说这不是控制器，但必须包含在MoSim控制系统上游。

## 1. 基础参考轨迹发生器

这些用于严格测试控制器，不能被在线规划器取代：

```text
悬停
阶跃
斜坡
正弦
圆形
椭圆
螺旋爬升
8字
多段航点
Minimum-Jerk
Minimum-Snap
高加速度激进轨迹
动力学不可行轨迹
```

每条轨迹统一输出：

```text
position
velocity
acceleration
jerk
snap
yaw
yaw_rate
yaw_acceleration
```

## 2. 单机在线规划器

建议全部接入，但通过适配器运行，不重写成Sysblock：

| 类型        | MoSim规划器                     |
| --------- | ---------------------------- |
| 搜索与轨迹优化基线 | Fast-Planner                 |
| 快速局部规划    | EGO-Planner                  |
| 单机/多机规划   | EGO-Planner-Swarm            |
| 高速安全导航    | SUPER                        |
| 拓扑引导规划    | TGK-Planner                  |
| 通用轨迹优化    | GCOPTER                      |
| 大规模集群规划   | Primitive-Swarm              |
| 特技飞行      | Aerobatic-Planner            |
| 目标跟踪规划    | Fast-Tracker、Elastic-Tracker |

EGO-Swarm本身是面向单机和多机的轨迹规划框架；Primitive-Swarm则面向大规模集群的轻量规划。它们负责生成安全轨迹，不等同于底层编队控制器。([GitHub][2])

## 3. 学习式规划接口

保留接口但不作为MoSim核心：

```text
Diffusion Planner Adapter
Learning-based Trajectory Generator
Neural Cost Map
Neural Collision Predictor
```

完整强化学习训练和固定翼扩展仍放到未来CoSim。

---

# 三、单机基础轨迹跟踪控制器

这一层才是通常意义上的“位姿控制器”。

## A. 经典控制家族

### C01 原始PID

保持官方模型不变：

```text
pid_baseline
```

用途：

* 官方基线；
* 参数优化前后对照；
* 所有实验的最低参照。

### C02 完整串级PID

```text
位置P/PI
  ↓
速度PID
  ↓
加速度到姿态和推力
  ↓
姿态P
  ↓
角速度PID
```

应支持：

* 前馈；
* 微分滤波；
* 抗积分饱和；
* 输出限幅；
* 增益调度；
* 两自由度PID；
* 设定值加权；
* 无扰切换。

PX4的多旋翼控制就是位置P、速度PID、姿态P和角速度PID构成的典型串级体系，因此它可以作为MoSim的工程级PID参考。([PX4文档][1])

### C03 自动整定PID

```text
Ziegler-Nichols
继电反馈整定
频域整定
粒子群PSO
遗传算法GA
贝叶斯优化
多目标优化
```

它不是新控制器，而是PID参数设计模块。

### C04 增益调度PID

根据以下状态切换或插值参数：

```text
飞行速度
负载质量
电池电压
高度
风速
故障程度
飞行阶段
```

### C05 模糊PID

模糊系统在线调节：

```text
Kp、Ki、Kd
```

适合作为赛题要求中的智能算法代表。

---

## B. 线性现代控制家族

### C06 LQR

基于悬停点或轨迹附近线性化模型：

```text
状态反馈
u = -Kx
```

支持：

* 全状态LQR；
* 解耦位置和姿态LQR；
* 离散LQR；
* 时变LQR。

### C07 LQI

在LQR基础上加入位置、航向等误差积分，用于消除稳态误差。

### C08 LQG

```text
Kalman Filter + LQR
```

用于测试状态噪声、估计误差和传感器扰动。

### C09 H∞鲁棒控制

用于系统化测试：

* 模型参数不确定性；
* 外部扰动；
* 测量噪声；
* 频域鲁棒性。

### C10 极点配置与状态反馈

作为教学和理论验证控制器：

```text
Pole Placement
State Feedback
Integral State Feedback
```

---

# 四、非线性控制家族

## C11 反馈线性化

通过动力学逆变换，将非线性系统转换为近似线性误差系统。

## C12 非线性动态逆NDI

根据期望加速度和角加速度反算推力与力矩，是INDI的基础对照。

## C13 Backstepping反步控制

按照位置、速度、姿态和角速度逐层构造Lyapunov控制律。

## C14 滑模控制SMC

完整体系应包含：

```text
经典一阶SMC
边界层SMC
自适应SMC
积分滑模
终端滑模
非奇异终端滑模
```

## C15 Super-Twisting SMC

用于减轻传统滑模的抖振，同时保持强扰动抑制能力。

## C16 SO(3)姿态控制

直接在旋转群上定义姿态误差，不对欧拉角独立控制。

至少实现：

```text
标准SO(3)姿态控制
解耦Yaw的SO(3)控制
倾斜优先姿态控制
```

FDCL公开了标准几何控制和解耦航向控制的多语言实现，`se3quad`还提供MATLAB/Simulink版本，可以直接作为MWORKS实现参考。([GitHub][3])

## C17 SE(3)几何位姿控制

完整控制位置和姿态：

[
p,v,R,\Omega
\rightarrow
T,M
]

它应成为MoSim的核心非线性基线。

## C18 微分平坦控制DFBC

分为三级：

```text
DFBC-Basic
位置、速度、加速度 → 姿态和推力

DFBC-Jerk
加入角速度前馈

DFBC-Full
加入jerk、snap、角加速度前馈、阻力补偿
```

## C19 倾斜优先DFBC

当推力或力矩受限时：

```text
优先保证Roll/Pitch
其次保证总推力
最后保证Yaw
```

适合激进飞行和执行器饱和场景。

Agilicious已经将几何控制、串级PID、MPC和INDI置于同一个模块化飞行控制框架中，可以作为MoSim插件式控制架构的主要参考。([GitHub][4])

---

# 五、优化控制体系

## C20 线性MPC

你已有：

```text
linear_mpc_sysblock
```

应进一步扩展为：

```text
定常LMPC
LTV-MPC
增量MPC
带积分MPC
输出反馈MPC
```

约束至少包含：

```text
位置
速度
加速度
姿态
角速度
推力
力矩
电机推力
控制变化率
```

ETH的`mav_control_rw`同时公开了线性MPC、非线性MPC、低层PID和扰动观测器，是这一部分非常合适的参考。([GitHub][5])

## C21 非线性MPC

你需要将现有：

```text
nmpc_indi_l1
```

拆成纯NMPC和增强模块。

完整NMPC支持：

```text
全非线性刚体模型
四元数姿态
单旋翼推力输入
电机动态
气动阻力
软约束
终端代价
在线参数更新
Warm Start
求解失败降级
```

`acados`面向实时和嵌入式非线性最优控制，提供C内核以及Python、MATLAB和Octave接口，适合作为MoSim NMPC求解与代码生成后端。([GitHub][6])

## C22 鲁棒MPC

```text
Tube MPC
Min-Max MPC
约束收缩MPC
扰动集MPC
```

用于保证参数不确定和有界扰动下的约束满足。

## C23 自适应MPC

在线估计：

```text
质量
惯量
推力系数
阻力参数
电机时间常数
```

并实时更新预测模型。

## C24 随机MPC

将风扰和状态误差建模为概率分布：

```text
Chance-Constrained MPC
Scenario MPC
```

## C25 分层MPC

```text
外层轨迹MPC
内层姿态/角速度控制
```

用于和全模型NMPC进行计算量与性能比较。

## C26 iLQR/DDP

作为有限时域非线性最优控制的另一条技术路线：

```text
iLQR
DDP
Constrained iLQR
```

## C27 MPPI采样控制

基于大量采样轨迹进行模型预测控制，适合未来GPU控制和复杂非光滑代价研究。

---

# 六、鲁棒、自适应和补偿模块

这些**不是独立轨迹控制器**，应作为任意基础控制器的插件。

## A01 前馈模块

```text
速度前馈
加速度前馈
jerk前馈
snap前馈
角速度前馈
角加速度前馈
```

## A02 气动补偿

```text
线性阻力
二次阻力
机体系各向异性阻力
桨叶气动效应
高速推力衰减
```

## A03 地面效应补偿

用于起飞、降落和低空悬停。

## A04 负载与质心补偿

```text
载荷质量变化
质心偏移
吊载影响
```

## A05 Disturbance Observer

```text
线性DOB
非线性DOB
Kalman扰动观测器
扩张状态观测器
```

`mav_control_rw`包含基于Kalman Filter的外部扰动观测器，用于无静差轨迹跟踪。([GitHub][5])

## A06 ADRC/ESO

```text
Tracking Differentiator
Extended State Observer
Nonlinear State Error Feedback
```

## A07 INDI

INDI设计为通用内环插件：

```text
PID + INDI
SE3 + INDI
DFBC + INDI
MPC + INDI
NMPC + INDI
```

## A08 L1自适应

同样独立于基础控制器：

```text
SE3 + L1
PID + L1
MPC + L1
NMPC + L1
```

L1Quad就是在几何控制基础上增加L1自适应增强的开源参考。([GitHub][7])

## A09 AWFF

你的AWFF具体缩写和算法含义仍需由内部模型确认，但结构上应放入：

```text
augmentation/awff
```

内部再分：

```text
awff_estimator
awff_compensator
awff_indi
awff_fault_compensation
```

## A10 延迟补偿

```text
Smith Predictor
状态前向预测
时间戳对齐
网络延迟补偿
执行器延迟补偿
```

## A11 饱和处理

```text
Anti-Windup
Reference Governor
Command Governor
推力优先级
倾角限幅
速率限幅
```

---

# 七、姿态、角速度和电机内环体系

不要默认所有外环都必须共用同一个内环。

## 姿态控制器

```text
Euler PID
Quaternion P
Quaternion PD
SO(3) Geometric
Tilt-Prioritized Attitude Control
NDI Attitude Control
```

## 角速度控制器

```text
Rate PID
Rate PI + Feedforward
Angular Acceleration Control
NDI
INDI
Sliding-Mode Rate Control
MPC Rate Control
```

## 推力与电机控制

```text
固定油门—推力映射
电池电压补偿
在线推力系数估计
电机转速闭环
电机动态逆
RPM前馈
电调延迟补偿
```

这样可形成多个控制接口层级：

```text
Position Control Interface
Attitude + Thrust Interface
Body Rate + Thrust Interface
Torque + Thrust Interface
Individual Rotor Thrust Interface
Rotor Speed Interface
```

---

# 八、控制分配体系

这是你当前故障控制中非常重要的一部分。

## CA01 直接逆分配

[
u=G^{-1}
\begin{bmatrix}
T\M
\end{bmatrix}
]

作为基准。

## CA02 伪逆分配

用于冗余执行器、多旋翼和秩变化系统。

## CA03 加权最小二乘

不同通道设置不同优先级：

```text
Roll/Pitch > Thrust > Yaw
```

## CA04 约束QP控制分配

考虑：

```text
最小/最大推力
电机变化率
故障效率
电池能力
力矩优先级
```

## CA05 分层优先级分配

```text
姿态稳定
   >
高度保持
   >
航向控制
```

## CA06 动态控制分配

将电机响应动态纳入分配器，而不是只使用静态矩阵。

## CA07 故障感知分配

实时使用电机效率矩阵：

[
G_f=G\Lambda
]

重新分配剩余控制能力。

PX4当前也将控制器输出和具体电机布局通过独立控制分配模块解耦，这种设计应直接借鉴到MoSim。([PX4文档][8])

---

# 九、故障诊断与容错控制体系

完整链路应为：

```text
故障注入
  ↓
残差生成
  ↓
故障检测
  ↓
故障隔离
  ↓
故障程度估计
  ↓
控制器重构
  ↓
控制分配重构
  ↓
降级飞行
```

## 1. 故障注入

### 执行器故障

```text
效率下降
卡死
偏置
响应变慢
间歇故障
单旋翼失效
多旋翼部分失效
```

### 传感器故障

```text
偏置
漂移
噪声增大
数据冻结
丢包
延迟
完全失效
```

### 系统故障

```text
质心偏移
载荷脱落
结构损伤
通信中断
电池衰减
```

## 2. 残差生成

```text
模型残差
观测器残差
奇偶空间残差
Kalman创新残差
L1预测残差
多模型残差
```

## 3. 故障检测与隔离

```text
阈值检测
CUSUM
GLR
多模型识别
贝叶斯故障判断
多故障联合隔离
```

## 4. 容错控制

```text
被动容错
主动容错
控制器增益重构
模型在线切换
控制分配重构
旋翼失效降级控制
失去Yaw后的旋转飞行控制
安全迫降
```

UZH公开的容错飞行控制器包含单旋翼完全失效后的控制与状态估计，可作为电机完全失效场景的参考。([GitHub][9])

## 5. 你的现有文件映射

```text
l1_residual_sysblock
→ fault_tolerance/residual_generation/l1

l1_multi_fault_isolation_sysblock
→ fault_tolerance/isolation/l1_multi_fault

l1_fault_allocation_sysblock
→ control_allocation/fault_aware_l1

l1_online_fault_allocation_sysblock
→ control_allocation/online_reconfiguration

linear_mpc_online_fault_allocation_sysblock
→ profile/lmpc_fault_aware
```

---

# 十、安全关键控制体系

安全控制应当独立于名义控制器：

```text
名义控制器
PID / SE3 / MPC / 编队控制
          ↓
安全过滤器
          ↓
最终安全控制命令
```

## S01 约束检查器

```text
最大速度
最大加速度
最大倾角
最大角速度
最大推力
最低高度
地理围栏
```

## S02 CBF-QP

控制屏障函数负责：

* 障碍物避碰；
* 多机防碰撞；
* 飞行区域约束；
* 输入约束；
* 最小高度和最大高度；
* 安全速度限制。

`safe_control`公开实现了CBF-QP、MPC-CBF等安全控制器，并包含ROS 2和PX4四旋翼实验接口。([GitHub][10])

## S03 MPC-CBF

同时优化性能和安全约束。

## S04 Backup Controller

当主控制器失败时切换到：

```text
安全悬停
低速PID
定高模式
自动返航
自动降落
```

## S05 可达集与安全包络

```text
Forward Reachability
安全飞行走廊
碰撞时间预测
执行器剩余能力评估
```

---

# 十一、完整编队与集群控制体系

编队层输出每架飞机的参考轨迹，底层仍由单机控制器执行。

## F01 虚拟结构

将整个编队看作一个刚体：

```text
整体位置
整体航向
各无人机固定相对位置
```

支持：

```text
一字
V形
三角形
方形
圆形
三维立方体
字母和图案
```

## F02 Leader-Follower

```text
单领航
多领航
分层领航
领航机切换
故障领航机替换
```

`PX4_Swarm_Controller`和CrazyChoir均提供了Leader-Follower类多机控制与仿真参考。([GitHub][11])

## F03 一致性控制

```text
位置一致性
速度一致性
航向一致性
二阶一致性
带领航者一致性
```

支持不同拓扑：

```text
全连接
链式
环式
星形
时变拓扑
有向图
```

## F04 编队形状控制

```text
距离保持
位移保持
方位角保持
刚性图控制
```

## F05 包含控制

多个领航机形成区域，跟随机保持在领航机凸包内。

## F06 Flocking

组合：

```text
聚合
速度一致
碰撞排斥
障碍物避让
```

## F07 分布式MPC

每架无人机独立预测并优化：

```text
自身轨迹
邻机轨迹
编队误差
碰撞约束
输入约束
通信约束
```

## F08 编队CBF安全过滤

解决编队控制与防碰撞冲突：

```text
尽量保持队形
但安全约束优先
```

## F09 编队重构

```text
穿越狭窄空间
队形切换
无人机退出
新无人机加入
故障成员隔离
领航机重选
```

## F10 任务分配

```text
拍卖算法
匈牙利算法
分布式任务分配
区域覆盖
目标分配
航点分配
```

## F11 大规模集群规划

接入：

```text
EGO-Swarm
EGO-Planner-v2
Primitive-Swarm
```

它们负责多机安全轨迹生成；一致性和虚拟结构等模块负责队形关系，两者应组合而不是互相替代。([GitHub][12])

---

# 十二、控制器管理系统

完整平台不能只靠手动替换模型。

## Controller Manager应负责

```text
控制器注册
控制器加载
参数加载
运行时切换
控制接口检查
状态初始化
积分器复位
Warm Start
故障降级
求解超时处理
输出合法性检查
无扰切换
日志和性能统计
```

## 控制器状态

```text
UNINITIALIZED
STANDBY
ACTIVE
DEGRADED
FAILED
FALLBACK
```

## 切换策略

例如：

```text
正常飞行：NMPC
求解超时：SE3
状态估计异常：低增益PID
电机故障：Fault-Tolerant SE3
定位丢失：Land
```

---

# 十三、统一控制接口

这是MoSim架构最重要的部分。

## 1. 轨迹输入

```text
TrajectoryReference
├── timestamp
├── position
├── velocity
├── acceleration
├── jerk
├── snap
├── yaw
├── yaw_rate
└── yaw_acceleration
```

## 2. 状态输入

```text
VehicleState
├── position
├── velocity
├── quaternion
├── angular_velocity
├── angular_acceleration
├── motor_speed
├── battery_voltage
├── disturbance_estimate
└── actuator_effectiveness
```

## 3. 控制器输出

允许多级输出：

```text
POSITION_SETPOINT
ACCELERATION_SETPOINT
ATTITUDE_THRUST
BODYRATE_THRUST
TORQUE_THRUST
ROTOR_THRUST
ROTOR_SPEED
```

## 4. 控制器能力描述

```text
ControllerCapability
├── required_state
├── required_reference_order
├── output_level
├── supports_constraints
├── supports_faults
├── supports_codegen
└── real_time_requirement
```

---

# 十四、最终目录结构

```text
MoSim/
└── Config/
    └── controllers/
        ├── reference/
        │   ├── step/
        │   ├── circle/
        │   ├── spiral/
        │   ├── figure8/
        │   ├── minimum_jerk/
        │   ├── minimum_snap/
        │   └── aggressive/
        │
        ├── planning/
        │   ├── fast_planner_adapter/
        │   ├── ego_planner_adapter/
        │   ├── ego_swarm_adapter/
        │   ├── super_adapter/
        │   ├── gcopter_adapter/
        │   └── primitive_swarm_adapter/
        │
        ├── tracking/
        │   ├── classical/
        │   │   ├── pid_baseline/
        │   │   ├── pid_cascade/
        │   │   ├── pid_gain_scheduled/
        │   │   └── fuzzy_pid/
        │   ├── linear/
        │   │   ├── lqr/
        │   │   ├── lqi/
        │   │   ├── lqg/
        │   │   └── hinfinity/
        │   ├── nonlinear/
        │   │   ├── feedback_linearization/
        │   │   ├── ndi/
        │   │   ├── backstepping/
        │   │   ├── smc/
        │   │   ├── super_twisting_smc/
        │   │   ├── so3/
        │   │   ├── se3/
        │   │   └── dfbc/
        │   └── optimal/
        │       ├── lmpc/
        │       ├── ltv_mpc/
        │       ├── nmpc/
        │       ├── tube_mpc/
        │       ├── adaptive_mpc/
        │       ├── stochastic_mpc/
        │       ├── ilqr/
        │       └── mppi/
        │
        ├── augmentation/
        │   ├── feedforward/
        │   ├── drag_compensation/
        │   ├── ground_effect/
        │   ├── disturbance_observer/
        │   ├── eso_adrc/
        │   ├── indi/
        │   ├── l1_adaptive/
        │   ├── awff/
        │   ├── delay_compensation/
        │   └── anti_windup/
        │
        ├── inner_loop/
        │   ├── attitude/
        │   ├── rate/
        │   ├── angular_acceleration/
        │   ├── thrust_mapping/
        │   └── motor_speed/
        │
        ├── control_allocation/
        │   ├── direct_inverse/
        │   ├── pseudoinverse/
        │   ├── weighted_least_squares/
        │   ├── qp/
        │   ├── priority/
        │   ├── dynamic/
        │   └── fault_aware/
        │
        ├── fault_tolerance/
        │   ├── fault_injection/
        │   ├── residual_generation/
        │   ├── detection/
        │   ├── isolation/
        │   ├── effectiveness_estimation/
        │   ├── active_ftc/
        │   ├── passive_ftc/
        │   └── degraded_control/
        │
        ├── safety/
        │   ├── constraint_checker/
        │   ├── reference_governor/
        │   ├── cbf_qp/
        │   ├── mpc_cbf/
        │   ├── geofence/
        │   └── backup_controller/
        │
        ├── formation/
        │   ├── virtual_structure/
        │   ├── leader_follower/
        │   ├── consensus/
        │   ├── shape_control/
        │   ├── containment/
        │   ├── flocking/
        │   ├── dmpc/
        │   ├── formation_cbf/
        │   ├── reconfiguration/
        │   └── task_allocation/
        │
        ├── manager/
        │   ├── controller_registry/
        │   ├── controller_switcher/
        │   ├── health_monitor/
        │   ├── fallback_manager/
        │   └── bumpless_transfer/
        │
        └── profiles/
            ├── pid_baseline/
            ├── pid_enhanced/
            ├── se3_nominal/
            ├── dfbc_indi/
            ├── se3_l1/
            ├── lmpc_nominal/
            ├── nmpc_nominal/
            ├── nmpc_indi_l1/
            ├── fault_tolerant_se3/
            ├── formation_consensus/
            └── formation_consensus_cbf/
```

---

# 十五、你现有目录怎么迁移

| 当前目录                                          | 新位置                                            |
| --------------------------------------------- | ---------------------------------------------- |
| `pid`                                         | `tracking/classical/pid_baseline`              |
| `enhanced_pid`                                | 合并到`pid_cascade`配置                             |
| `improved_pid`                                | 合并到`pid_cascade`配置                             |
| `awff_pid`                                    | `profiles/pid_awff`                            |
| `awff_sysblock`                               | `augmentation/awff`                            |
| `awff_indi_sysblock`                          | `profiles/awff_indi`                           |
| `awff_fault_compensation_sysblock`            | `fault_tolerance/active_ftc/awff`              |
| `awff_complete_system`                        | `profiles/awff_complete`                       |
| `linear_mpc_sysblock`                         | `tracking/optimal/lmpc`                        |
| `linear_mpc_online_fault_allocation_sysblock` | `profiles/lmpc_fault_aware`                    |
| `nmpc_indi_l1`                                | `profiles/nmpc_indi_l1`                        |
| `l1_residual_sysblock`                        | `fault_tolerance/residual_generation/l1`       |
| `l1_multi_fault_isolation_sysblock`           | `fault_tolerance/isolation/l1`                 |
| `l1_fault_allocation_sysblock`                | `control_allocation/fault_aware/l1`            |
| `l1_online_fault_allocation_sysblock`         | `control_allocation/online_reconfiguration/l1` |

关键原则是：

> **控制器目录只保存原子算法，完整组合只保存在profiles中。**

---

# 十六、MoSim最终应具有的代表性组合

虽然基础模块很多，最终用于答辩和统一测试的代表组合可以固定为：

```text
P01 官方PID
P02 增强串级PID
P03 模糊增益调度PID
P04 LQI
P05 H∞
P06 Backstepping
P07 Super-Twisting SMC
P08 SE(3)
P09 DFBC
P10 DFBC + INDI
P11 SE(3) + L1
P12 LMPC
P13 NMPC
P14 NMPC + INDI
P15 NMPC + INDI + L1
P16 SE(3) + DOB + QP Allocation
P17 Fault-Tolerant SE(3)
P18 Fault-Tolerant NMPC
P19 Consensus + SE(3)
P20 Consensus + CBF + SE(3)
P21 Formation DMPC
P22 EGO-Swarm + DFBC
P23 SUPER + NMPC
P24 Primitive-Swarm + Consensus + CBF
```

这样MoSim最终形成的不是“做了多少个控制器”，而是六条完整技术线：

```text
经典控制线：
PID → 增强PID → 模糊PID

现代控制线：
LQR → LQI → LQG → H∞

非线性控制线：
Backstepping → SMC → SO3 → SE3 → DFBC

优化控制线：
LMPC → LTV-MPC → NMPC → 鲁棒/自适应MPC

鲁棒容错线：
DOB → ADRC → INDI → L1 → FDI → 故障分配

多机协同线：
虚拟结构 → Leader-Follower → 一致性 → DMPC → CBF安全编队
```

这才是**完整的MoSim四旋翼控制器体系**。它覆盖赛题要求的位姿控制、经典控制、现代控制、智能补偿、鲁棒性、故障容错、编队控制、模块替换和扩展接口，同时仍然严格限定在四旋翼和MWORKS阶段，不提前把未来CoSim的固定翼、强化学习训练和多域无人系统全部塞进来。

[1]: https://docs.px4.io/main/en/flight_stack/controller_diagrams.html?utm_source=chatgpt.com "Controller Diagrams | PX4 Guide (main)"
[2]: https://github.com/ZJU-FAST-Lab/ego-planner-swarm?utm_source=chatgpt.com "GitHub - ZJU-FAST-Lab/ego-planner-swarm: An efficient single/multi-agent trajectory planner for multicopters. · GitHub"
[3]: https://github.com/fdcl-gwu/uav_geometric_control?utm_source=chatgpt.com "GitHub - fdcl-gwu/uav_geometric_control: Geometric controllers developed at FDCL for UAVs"
[4]: https://github.com/uzh-rpg/agilicious?utm_source=chatgpt.com "GitHub - uzh-rpg/agilicious: Agile flight done right! · GitHub"
[5]: https://github.com/ethz-asl/mav_control_rw?utm_source=chatgpt.com "GitHub - ethz-asl/mav_control_rw: Control strategies for rotary wing Micro Aerial Vehicles using ROS"
[6]: https://github.com/acados/acados?utm_source=chatgpt.com "GitHub - acados/acados: Fast and embedded solvers for nonlinear optimal control and nonlinear model predictive control · GitHub"
[7]: https://github.com/sigma-pi/L1Quad?utm_source=chatgpt.com "GitHub - sigma-pi/L1Quad: Implementation of L1 adaptive control with ardupilot firmware."
[8]: https://docs.px4.io/v1.15/en/concept/control_allocation.html?utm_source=chatgpt.com "Control Allocation (Mixing) | PX4 Guide (v1.15)"
[9]: https://github.com/uzh-rpg/fault_tolerant_control?utm_source=chatgpt.com "GitHub - uzh-rpg/fault_tolerant_control: Vision-based quadrotor fault-tolerant flight controller. · GitHub"
[10]: https://github.com/tkkim-robot/safe_control?utm_source=chatgpt.com "GitHub - tkkim-robot/safe_control: Safety-critical controllers for single/multi robotic navigation: CBF-QP, MPC-CBF, and etc. · GitHub"
[11]: https://github.com/artastier/PX4_Swarm_Controller?utm_source=chatgpt.com "GitHub - artastier/PX4_Swarm_Controller: The aim of this ROS2 package is to facilitate the implementation of a drone swarm controller through simulation on Gazebo. · GitHub"
[12]: https://github.com/ZJU-FAST-Lab/Primitive-Planner?utm_source=chatgpt.com "GitHub - ZJU-FAST-Lab/Primitive-Planner: Primitive-Swarm: An Ultra-lightweight and Scalable Planner for Large-scale Aerial Swarms · GitHub"
