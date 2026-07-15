# MoSim控制器族论文与链路位置调研讨论稿

> 状态：cache讨论稿，不是正式设计冻结文档。
> 日期：2026-06-24
> 目的：扩展MoSim控制器族视野，覆盖经典、非线性、鲁棒、自适应、学习、
> 模糊、安全和故障容错控制，并判断它们在PX4/MoSim闭环中的插入位置。

## 1. 设计原则

MoSim最终不是只做一个控制器，而是做一个可选择、可组合、可评价的无人机
控制实验系统。控制器族文档不能只列算法名称，必须回答：

```text
该方法属于主控制器、增强模块、调参/增益调度、观测器、安全过滤、
故障检测还是控制分配；
它插入PX4/MoSim控制链路的哪一环；
它的输入输出层级是什么；
它是否适合第一阶段ATTITUDE_THRUST；
它是否需要BODY_RATE、WRENCH或ROTOR级接口；
它是否适合MWORKS建模、Sysblock代码生成和C++部署；
它在最终前端中应该作为控制器选项、模块开关、参数Profile还是实验环境配置。
```

## 2. 控制器族总览

| 控制族 | MoSim定位 | 典型插入层 | 第一阶段可做性 | MWORKS适配判断 |
| --- | --- | --- | --- | --- |
| PID/增益调度PID | 基线控制器 | 位置/速度/高度外环 | 高 | 高 |
| LQR/LQI | 线性现代控制 | 线性化外环或姿态环 | 高 | 高 |
| SE3/SO3几何控制 | 非线性外环 | 几何姿态/推力生成 | 高 | 中高 |
| DFBC | 微分平坦跟踪 | 外环到body-rate/wrench | 中 | 中 |
| Backstepping | 非线性递推控制 | 外环+姿态环 | 中 | 中高 |
| SMC/STSMC/TSMC | 鲁棒非线性控制 | 外环或姿态环 | 中 | 中 |
| MPC/LMPC/NMPC | 优化控制 | 外环、body-rate或wrench | 中 | 中，需算力评估 |
| INDI | 增量动态逆增强 | 内环/body-rate/加速度层 | 低到中 | 中，需高频和导数估计 |
| L1 adaptive | 自适应补偿 | 外环或内环增强 | 中 | 中 |
| DOB/ESO/ADRC | 扰动观测补偿 | 状态/扰动估计层 | 高 | 高 |
| H-infinity | 鲁棒控制 | 姿态/位置鲁棒环 | 中 | 中 |
| Fuzzy/Fuzzy PID | 模糊调参或控制器 | 外环或姿态调参 | 中 | 中高 |
| Neural/RBF adaptive | 学习增强/逼近器 | 外环补偿或调参 | 中 | 中，需部署约束 |
| RL | 策略控制/调参/残差控制 | 不宜一开始直接替代全链路 | 低到中 | 需严格约束 |
| CBF/Safety Filter | 安全过滤 | 参考或控制输出后处理 | 中 | 高 |
| Fault-tolerant allocation | 故障容错 | 控制分配/执行器层 | 低到中 | 中，需低层接口 |

## 3. 经典与现代线性控制

### 3.1 PID/增强PID

定位：

```text
基线控制器；
外环位置/速度/高度控制；
可用于验证统一接口、参数Profile、调参流程和前端控制器选择器。
```

适合第一阶段：

```text
ATTITUDE_THRUST
```

MWORKS适配：

```text
非常适合Sysblock建模和C/C++代码生成。
```

### 3.2 LQR/LQI

定位：

```text
线性化模型下的状态反馈；
LQI增加积分状态，适合稳态误差抑制；
可以作为PID和MPC之间的中间控制器。
```

插入层：

```text
位置/速度外环；
姿态环线性化版本；
不天然需要jerk/snap；
不应直接消费故障状态，除非扩展为故障感知版本。
```

MWORKS适配：

```text
适合矩阵化建模、参数Profile和自动生成代码。
```

## 4. 几何、微分平坦和Backstepping

### 4.1 SE3/SO3几何控制

定位：

```text
非线性几何控制；
适合四旋翼姿态和推力生成；
可以第一阶段输出ATTITUDE_THRUST，也可后续输出BODY_RATE_THRUST。
```

文档重点：

```text
旋转矩阵/四元数误差；
推力方向；
yaw处理；
是否复用PX4姿态内环。
```

### 4.2 DFBC

定位：

```text
微分平坦轨迹跟踪；
低阶版本可以输出姿态和推力；
高阶版本使用jerk/snap生成body-rate、角加速度或wrench前馈。
```

注意：

```text
jerk/snap只属于DFBC高阶版本、部分NMPC和rotor/wrench级控制；
不能要求普通PID/LQI/SMC都支持。
```

### 4.3 Backstepping

定位：

```text
基于Lyapunov递推设计的非线性控制；
可用于位置/姿态两层；
也常与SMC、ESO、神经网络或模糊控制结合。
```

MWORKS适配：

```text
如果公式清楚，适合在MWORKS中建模；
但要避免过度复杂的符号推导直接塞进实时路径。
```

## 5. 滑模控制族

### 5.1 SMC/STSMC/TSMC

定位：

```text
鲁棒控制器；
可用于位置环、姿态环或两者组合；
对模型不确定性和外部扰动有优势。
```

典型问题：

```text
抖振；
边界层和平滑化；
高频执行器负担；
参数调节敏感。
```

MoSim建议：

```text
第一版做外环SMC或super-twisting SMC，输出ATTITUDE_THRUST；
后续再研究姿态环/body-rate层的SMC。
```

### 5.2 Fuzzy-SMC

定位：

```text
模糊控制不一定独立作为主控制器；
更适合用于SMC边界层/增益自适应，降低抖振。
```

前端表达：

```text
控制器：SMC
增强模块：Fuzzy gain tuning
```

而不是把“Fuzzy”和“SMC”混成无法定位的单一大类。

## 6. MPC族

### 6.1 LMPC

定位：

```text
线性模型预测控制；
可以作为外环优化控制器；
适合在固定工作点或弱非线性范围内做状态/输入约束。
```

输出层级：

```text
acceleration；
ATTITUDE_THRUST；
BODY_RATE_THRUST；
具体取决于建模对象。
```

### 6.2 NMPC

定位：

```text
非线性优化控制；
适合约束、多目标、激进轨迹；
但实时算力、求解器稳定性和代码生成是核心风险。
```

MoSim建议：

```text
先做外环NMPC或低维NMPC；
不要一开始做全状态rotor级NMPC；
前端可作为高级控制器选项，但需要标记算力和求解状态。
```

## 7. 扰动、自适应和观测器

### 7.1 INDI

定位：

```text
增量动态逆；
更接近内环/加速度控制增强；
需要高频测量、角加速度或加速度估计、控制有效性矩阵。
```

MoSim建议：

```text
不应第一阶段强行塞进ATTITUDE_THRUST；
更适合作为BODY_RATE_THRUST或更低层接口阶段的增强模块。
```

### 7.2 L1 adaptive

定位：

```text
自适应补偿；
可叠加在外环或内环；
用于模型不确定性和扰动补偿。
```

注意：

```text
L1不是“控制器下拉框里的普通控制器”；
更合理是作为某些控制器Profile的增强模块。
```

### 7.3 DOB/ESO/ADRC

定位：

```text
扰动观测与补偿；
可估计总扰动、未建模动态或输入等效扰动；
可配合PID/SE3/SMC/Backstepping。
```

MoSim建议：

```text
作为增强模块优先实现；
适合MWORKS建模；
不直接等同于故障状态输入。
```

### 7.4 H-infinity

定位：

```text
鲁棒控制；
适合模型不确定性和扰动抑制；
可作为姿态环或外环鲁棒控制候选。
```

MoSim建议：

```text
列为后续鲁棒控制候选；
先不放进第一批实现，避免和SMC/DOB/ESO路线重复过多。
```

## 8. 模糊控制和神经网络增强

### 8.1 Fuzzy Control

定位：

```text
可以是主控制器，也可以是PID/SMC增益调度器；
在无人机中常用于处理非线性、规则型调参和不确定性。
```

MoSim建议：

```text
优先做Fuzzy PID或Fuzzy-SMC增益调度；
不建议第一版做完全黑箱模糊控制替代整个飞控链路。
```

### 8.2 RBF/NN adaptive

定位：

```text
函数逼近器；
通常用于补偿未知非线性或辅助Backstepping/SMC。
```

MWORKS注意：

```text
需要明确网络规模、推理代码生成能力、实时性和参数冻结方式；
不能把训练过程放到实时闭环里。
```

## 9. 强化学习控制

RL必须谨慎设计，不能简单说“上RL控制器”。

### 9.1 RL可放的位置

| RL角色 | 说明 | 风险 |
| --- | --- | --- |
| 端到端电机/RPM策略 | 状态直接到电机命令 | 风险最高，难解释，真机风险大 |
| body-rate或attitude residual | 在传统控制器基础上输出残差 | 风险较低，适合渐进式研究 |
| 增益调度 | 学习PID/SMC/MPC参数调节 | 更适合工程落地 |
| 轨迹/运动生成 | RL生成轨迹或时间分配，控制器仍传统 | 与EGO/规划层结合 |
| 故障容错策略 | 根据故障/状态选择补偿或分配策略 | 需要大量故障仿真 |
| 安全监督 | 选择模式、限制动作、触发fallback | 适合和Safety Filter结合 |

### 9.2 MoSim对RL的约束

```text
训练必须基于MWORKS/Gazebo可复现仿真环境；
实时部署路径必须明确：C++推理、ONNX/TensorRT或生成代码；
必须保留传统控制器fallback；
必须先做仿真评估，再考虑真机；
RL策略不能绕过PX4安全状态机；
RL不能作为第一阶段基准控制器。
```

### 9.3 推荐RL切入点

```text
第一候选：RL gain scheduler
  输入：任务类型、误差、速度、扰动估计、故障/风扰Profile
  输出：PID/SMC/MPC部分参数或权重

第二候选：RL residual controller
  输入：传统控制器状态和误差
  输出：小幅补偿项
  安全边界：Safety Filter裁剪

第三候选：RL trajectory/time allocation
  与EGO/Diff-Planner结合，控制器仍由px4ctrl/SE3/NMPC执行。
```

## 10. 安全过滤和故障容错

### 10.1 CBF/Safety Filter

定位：

```text
安全过滤层；
可作用于参考轨迹、速度命令、加速度命令或控制输出；
不应被归类为普通控制器。
```

前端表达：

```text
安全过滤开关；
安全距离；
速度/倾角/推力约束；
是否启用fallback。
```

### 10.2 Fault Allocation

定位：

```text
控制分配/执行器层；
用于电机失效、推力衰减、饱和时重新分配力矩/推力。
```

注意：

```text
它通常需要WRENCH或ROTOR层级；
第一阶段ATTITUDE_THRUST不适合直接宣称完成故障分配。
```

## 11. 面向前端的控制器组织方式

最终界面不应是一个简单下拉框，而应按层级组织：

```text
主控制器：
  px4ctrl、PID、LQI、SE3、DFBC、Backstepping、SMC、LMPC、NMPC、Fuzzy PID

增强模块：
  AWFF、DOB/ESO、L1、INDI、Fuzzy gain、NN/RBF compensation、RL residual

安全模块：
  CBF、Safety Filter、Reference Governor、Fallback Controller

故障模块：
  故障注入、FDI、Fault Allocation、control effectiveness update

学习模块：
  RL gain scheduler、RL residual、RL planner/time allocation
```

界面需要根据控制层级自动过滤：

```text
ATTITUDE_THRUST阶段：
  允许px4ctrl/PID/LQI/SE3基础版/SMC外环/LMPC外环/NMPC外环/AWFF/DOB-ESO。

BODY_RATE_THRUST阶段：
  允许DFBC高阶版/INDI/部分NMPC/SMC姿态环。

WRENCH/ROTOR阶段：
  允许Fault Allocation、rotor-level RL、full NMPC、控制分配重构。
```

## 12. 建议纳入正式控制器文档的对象

建议正式文档至少覆盖：

```text
controllers/
  px4ctrl.md
  PID.md
  Gain-Scheduled-PID.md
  LQI.md
  SE3.md
  DFBC.md
  Backstepping.md
  SMC.md
  Fuzzy-PID.md
  LMPC.md
  NMPC.md

modules/
  AWFF.md
  DOB-ESO.md
  L1-Adaptive.md
  INDI.md
  Fuzzy-Gain.md
  NN-RBF-Compensation.md
  RL-Gain-Scheduler.md
  RL-Residual-Control.md
  Safety-Filter.md
  CBF.md
  Fault-Allocation.md
  FDI.md
```

不建议一开始为每个小变种建独立正式文档。例如STSMC、TSMC、Fuzzy-SMC
可以先作为`SMC.md`内的变体；未来进入实现批次再拆。

## 13. 初步实现优先级

### 第一批：模板和基线

```text
px4ctrl
PID
SE3 Basic
DOB/ESO基础扰动观测
```

### 第二批：代表性高级控制器

```text
LQI
SMC外环
DFBC基础版
LMPC外环
```

### 第三批：高阶和鲁棒增强

```text
NMPC
Backstepping
AWFF
L1
Fuzzy PID / Fuzzy gain
```

### 第四批：低层接口和故障容错

```text
INDI
BODY_RATE_THRUST接口
Safety Filter / CBF
Fault Allocation
FDI
```

### 第五批：学习控制

```text
RL gain scheduler
RL residual controller
RL trajectory/time allocation
```

RL不应作为第一批主控制器，必须依附MWORKS/Gazebo仿真、传统控制器fallback
和安全过滤。

## 14. 参考资料

以下是候选阅读入口。正式架构文档只能引用已经读过并确认过的论文原文、
DOI页面、arXiv原文、官方仓库或官方文档；搜索聚合页和转载PDF只能用于
定位原文，不能作为最终技术结论来源。

1. Control of a Quadrotor with Reinforcement Learning
   https://arxiv.org/abs/1707.05110
2. What Matters in Learning A Zero-Shot Sim-to-Real RL Policy for Quadrotor Control
   https://arxiv.org/html/2412.11764
3. Accurate Tracking of Aggressive Quadrotor Trajectories Using INDI and Differential Flatness
   https://www.ezratal.net/files/CDC18_1876.pdf
4. A Comparative Study of Nonlinear MPC and Differential-Flatness-Based Control for Quadrotor Agile Flight
   https://arxiv.org/abs/2109.01365
5. Trajectory tracking of a quadrotor using sliding mode control
   https://pure.ups.edu.ec/en/publications/trajectory-tracking-of-a-quadrotor-using-sliding-mode-control-6/
6. Super Twisting Sliding Mode Control with Fuzzy PID Surface for quadrotor trajectory tracking
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11581241/
7. Backstepping trajectory tracking control of a quadrotor
   https://ieeexplore.ieee.org/document/7340523/
8. Quadrotor trajectory tracking based on backstepping control and RBF neural networks
   https://doaj.org/article/9ee420da192c4775b3ba122d61f28594
9. Backstepping/Nonlinear H-infinity Control for Path Tracking of a QuadRotor UAV
   https://scispace.com/pdf/backstepping-nonlinear-h-control-for-path-tracking-of-a-1kz8uv8t7d.pdf
10. Trajectory Tracking of AR.Drone Quadrotor Using Fuzzy Logic Controller
    https://www.academia.edu/52287544/Trajectory_Tracking_of_AR_Drone_Quadrotor_Using_Fuzzy_Logic_Controller
11. Learning-Based Control for Nano-Drones Flight
    https://amslaurea.unibo.it/id/eprint/36244/1/main.pdf
12. Reinforcement Learning-based Fault-Tolerant Control for Quadrotor
    https://dartmouthrobotics.github.io/icra-2025-robots-wild/spotlight-papers/icra-2025-robots-wild-13.pdf
