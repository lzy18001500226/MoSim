# WF-01 px4ctrl Golden Slice 架构冻结决策草案

> 日期：2026-06-21
> 位置：`Docs/Design/cache/`
> 性质：架构冻结决策草案，供人工审核后并入
> `Docs/Design/MoSim研发工作流与Agent任务编排规范.md` 和
> `Docs/Design/MoSim控制体系总览.md`。
>
> 本文不是正式执行规范。正式生效前不得替代 WF-01 和 CTRL-01。

## 1. 冻结结论

第一阶段正式收缩为：

```text
px4ctrl Golden Vertical Slice
+ ATTITUDE_THRUST
+ PX4/MAVROS融合状态源
+ Sunray/Gazebo plant权威
```

px4ctrl 是第一阶段一切控制器、接口、频率、状态源、推力映射、EGO接入和后续 MWORKS 代码生成验证的基准。

第一阶段不实现：

```text
BODY_RATE_THRUST
WRENCH
ROTOR_THRUST
ROTOR_SPEED
完整Controller Manager
完整PX4 Module板载部署
自研编队控制
FAST-LIO定位闭环参与基准调参
```

这些内容只在文档和接口枚举中保留规划，不建立实际 Adapter，不放入第一阶段 MWORKS 端口，不要求 Agent 测试。

## 2. 当前状态源冻结

当前控制闭环使用 PX4/MAVROS 融合状态，不直接使用 Gazebo Truth，不直接使用 Sunray `uav_state` 数值字段作为控制核心输入。

| 数据 | 当前用途 | Topic |
| --- | --- | --- |
| 位置、速度、姿态 | 控制器主要状态输入 | `/mavros/local_position/odom` |
| 机体系角速度、IMU相关输入 | 控制器角速度输入 | `/mavros/imu/data` |
| 飞行模式、解锁、定位有效性、前端展示 | 状态机与运行包装层 | `/sunray/uav_state` |
| 评价真值 | 误差评价、定位算法对照 | Gazebo truth pose / truth odometry |

冻结 Profile：

```yaml
state_source:
  id: px4_mavros_fused_v1

  pose_velocity:
    topic: /mavros/local_position/odom

  angular_velocity:
    topic: /mavros/imu/data

  system_status:
    topic: /sunray/uav_state

  evaluation_truth:
    topic: <actual_gazebo_truth_topic>
    control_input_allowed: false
```

硬规则：

```text
Gazebo Truth 只用于评价，不输入控制器。
Sunray uav_state 只用于状态机、有效性、展示和诊断，不作为控制核心数值输入。
调参过程中不得在不同状态源之间切换。
FAST-LIO接入时必须新建 State Source Profile。
```

## 3. Plant权威冻结

当前 `References/Sunray` / Gazebo Classic / Sunray 机型是 plant 权威。

MWORKS 模型后续应向 Sunray/Gazebo 参数靠拢，而不是强行要求 Sunray/Gazebo 完全匹配已有 MWORKS 理想模型。

当前参数一致性优先级：

```text
Sunray/Gazebo plant 实际参数
  > PX4/Sunray运行配置
  > MWORKS模型参数
  > 报告中的抽象参数
```

MWORKS 的职责是：

```text
控制器建模
MIL仿真
参数扫描
控制器重建
代码生成
SIL一致性
性能分析
```

Sunray/Gazebo/PX4 的职责是：

```text
真实接口闭环
飞控状态机
姿态与角速度内环
控制分配
执行器动态
传感器
碰撞和环境
运行可视化
```

## 4. px4ctrl双基准冻结

px4ctrl 必须冻结两个版本，不能只选其一。

### 4.1 上游算法权威

```text
PX4CTRL_UPSTREAM_REFERENCE
ZJU-FAST-Lab/Fast-Drone-250
src/realflight_modules/px4ctrl
```

用途：

```text
算法来源
原始状态机和控制律审计
论文及许可证追溯
判断Sunray版本修改内容
```

### 4.2 当前工程运行基准

```text
PX4CTRL_SUNRAY_BASELINE
References/Sunray 中的 px4ctrl
```

用途：

```text
当前Sunray Gazebo实际运行
Topic和消息适配
启动配置
机型参数
推力映射
```

### 4.3 必须建立差异报告

进入 px4ctrl Golden Slice 前，必须产出：

```text
px4ctrl_upstream_commit.txt
px4ctrl_sunray_commit.txt
px4ctrl_source_hashes.json
px4ctrl_upstream_vs_sunray.diff
px4ctrl_lineage_report.md
```

术语冻结：

```text
原始px4ctrl复现
= ZJU Fast-Drone-250上游固定Commit

Sunray px4ctrl基线
= 当前 References/Sunray 固定版本

MoSim px4ctrl Golden Slice
= 以Sunray可运行链路为工程输入，
   以上游实现为算法追溯依据，
   完成差异审计后抽取的 px4ctrl_core
```

## 5. 第一阶段控制输出层级冻结

第一阶段唯一实际实现输出层级：

```text
ATTITUDE_THRUST
```

第一版实际链路：

```text
轨迹参考
p_d、v_d、a_d、yaw_d
        ↓
MWORKS / MoSim外部控制器
        ↓
期望姿态 q_d
物理总推力 T_d
        ↓
统一ATTITUDE_THRUST Adapter
        ↓
MAVROS setpoint_raw/attitude
        ↓
PX4姿态环
        ↓
PX4角速度环
        ↓
PX4控制分配
        ↓
Gazebo电机模型
```

硬规则：

```text
MWORKS输出物理总推力 N。
MWORKS不直接输出 MAVROS 0~1 归一化油门。
归一化推力映射放在公共 ATTITUDE_THRUST Adapter 中。
第一阶段不得为 BODY_RATE_THRUST/WRENCH/ROTOR_* 建立实际 Adapter。
```

这不是 PX4 能力限制，而是 MoSim 主动收缩第一阶段范围。

## 6. MWORKS控制器核心接口冻结

第一阶段 MWORKS 控制器核心输入固定为：

```text
当前状态：
position
velocity
attitude
angular_velocity

轨迹参考：
position_reference
velocity_reference
acceleration_reference
yaw_reference
yaw_rate_reference（可选）

模型参数：
mass
gravity

运行参数：
dt
reset
enable
```

输出固定为：

```text
desired_attitude_quaternion
desired_collective_thrust_N
controller_status
controller_diagnostics
```

px4ctrl 必须拆成两层：

```text
MWORKS负责的控制核心：
位置误差
速度误差
积分或反馈项
加速度前馈
重力补偿
期望合力
期望姿态计算
物理总推力计算

ROS/PX4运行包装层负责：
ROS订阅和发布
Offboard状态机
解锁和模式切换
遥控器逻辑
自动起降逻辑
超时检测
坐标转换
消息时间同步
MAVROS归一化推力
日志和安全回退
```

禁止把整个 px4ctrl 塞进 MWORKS。

## 7. 推力映射Profile

复现原始 px4ctrl 时，必须先保留：

```text
px4ctrl_original_profile
```

其目标是严格复现原有推力映射。

随后建立：

```text
px4ctrl_mosim_profile
```

其目标是将控制核心和推力映射拆开。

两者经过一致性验证后，后续控制器统一使用 MoSim 接口和公共推力映射。

推力比较规则：

```text
控制核心一致性比较物理总推力 N。
MAVROS normalized thrust 属于 Adapter 层测试。
不得用某个版本内部的 0~1 油门值评价控制核心一致性。
```

## 8. 频率Profile冻结

第一阶段统一冻结为 100 Hz ATTITUDE_THRUST。

```yaml
frequency_profile:
  id: attitude_thrust_100hz_v1

  controller_rate_hz: 100
  command_publish_rate_hz: 100
  trajectory_evaluation_rate_hz: 100

  planner_nominal_rate_hz: 20

  control_period_s: 0.01
  state_timeout_s: 0.05
  reference_timeout_s: 0.10
```

说明：

```text
EGO重规划频率可以是约10~20Hz或事件触发。
Trajectory Server必须在每个100Hz控制周期对带时间参数的轨迹函数/B样条求值。
不得把EGO的20Hz离散位置点简单线性插值为100Hz控制命令。
```

状态原始频率可以不同：

```text
Gazebo Truth：保留原频率
Sunray uav_state：保留约200Hz
MAVROS状态：约100Hz
```

进入控制器前，由 StateAdapter 按 100 Hz 控制时刻进行时间对齐。

## 9. px4ctrl Golden Slice 顺序

黄金纵向切片正式命名为：

```text
PX4CTRL Golden Vertical Slice
```

完整顺序：

```text
P0  冻结PX4/MAVROS融合状态源
        ↓
P1  冻结ZJU上游px4ctrl版本
        ↓
P2  冻结Sunray px4ctrl工程版本
        ↓
P3  上游与Sunray版本差异审计
        ↓
P4  Sunray px4ctrl闭环跑通并调优
        ├──────────────┐
        ↓              ↓
P5A 抽取core       P5B EGO单机官方链路
        ↓              ↓
P6  core离线对齐   EGO-Swarm S0/S1
        ↓
P7  MWORKS重建
        ↓
P8  MWORKS模型离线对齐
        ↓
P9  生成C代码
        ↓
P10 四方离线一致性
        ↓
P11 接回原ROS包装层
        ↓
P12 Gazebo闭环对齐
        ↓
P13 EGO使用MWORKS版px4ctrl_core
        ↓
P14 FAST-LIO独立定位评价
        ↓
P15 FAST-LIO经PX4融合后替换状态源
        ↓
P16 冻结ATTITUDE_THRUST模板V1
        ↓
P17 官方PID单控制器替换
        ↓
P18 SE3 Basic单控制器替换
        ↓
P19 根据结果逐个释放后续控制器
```

关键规则：

```text
必须先证明抽取 core 没有改变原 px4ctrl。
抽取 core 未离线对齐前，不得进入 MWORKS 重建。
MWORKS模型未离线对齐前，不得生成代码进入Gazebo。
生成代码四方一致性未通过前，不得接回Gazebo闭环。
```

## 10. 离线一致性门禁

强制门禁：

```text
G-PX4CTRL-OFFLINE
px4ctrl离线一致性门禁
```

必须四方对齐：

```text
A. 原始px4ctrl包装层中的原控制逻辑
B. 抽取后的px4ctrl_core C++
C. MWORKS Sysblock模型
D. MWORKS生成C代码
```

使用完全相同的离线输入序列：

```text
时间戳和dt
当前位置
当前速度
当前姿态
当前角速度
参考位置
参考速度
参考加速度
参考Yaw
控制器Reset与Enable状态
```

比较输出：

```text
期望姿态q_d
物理总推力T_d
积分状态
期望合力
误差项
饱和标志
控制器状态码
```

四元数比较不得直接逐元素比较，应使用：

```text
几何姿态误差角
或
min(||q1 - q2||, ||q1 + q2||)
```

首版建议容差：

```text
float64模型：
姿态几何误差 <= 1e-6 rad
推力绝对差 <= 1e-5 N
积分状态绝对差 <= 1e-6
状态码完全一致

float32生成代码：
姿态几何误差 <= 1e-4 rad
推力绝对差 <= 1e-3 N
积分状态绝对差 <= 1e-4
状态码完全一致
```

实际容差可根据 MWORKS 生成数据类型和输入量级修正，但修正必须记录原因。

## 11. EGO与EGO-Swarm阶段边界

EGO 与 MWORKS px4ctrl Golden Slice 在 Sunray px4ctrl 能稳定运行后并行推进。

主线A：

```text
px4ctrl Golden Slice
抽取core
→ 离线对齐
→ MWORKS
→ 代码生成
→ Gazebo回灌
```

支线B：

```text
EGO单机
→ px4ctrl
→ PX4
→ Gazebo
→ EGO-Swarm 2机
→ EGO-Swarm 3机
```

两条支线汇合点：

```text
MWORKS生成的px4ctrl_core
替换
原始px4ctrl_core

然后重新运行同一套EGO单机链路。
```

### EGO-S0：上游官方Demo

目标：

```text
官方ego-planner-swarm固定Commit
官方launch
2/3机正常运行
```

### EGO-S1：MoSim工程集成基线

目标：

```text
EGO-Swarm
→ 每机Trajectory Adapter
→ 每机px4ctrl
→ 每机MAVROS
→ 每机PX4 SITL
→ Gazebo
```

验收范围：

```text
2机正常启动
3机正常启动
每机PX4实例隔离
每机MAVROS实例隔离
每机px4ctrl实例隔离
规划Topic隔离
轨迹Topic隔离
状态Topic隔离
日志隔离
能够完成目标点导航
无碰撞
多次启动可重复
```

当前不做：

```text
MoSim自研Leader-Follower
虚拟结构
一致性控制
固定队形保持
任务分配
CBF
故障成员退出
队形重构
异构控制器集群
```

术语规则：

```text
EGO-S0 可以称为官方Demo。
EGO-S1 使用官方规划算法，但已经属于 MoSim 工程接入版本，不能表述为未经修改的官方完整链路。
```

## 12. FAST-LIO阶段边界

FAST-LIO分两阶段。

### 阶段一：独立定位和建图验证

只要求：

```text
MID360点云正常
IMU正常
FAST-LIO初始化正常
点云地图正常
里程计连续
坐标系正确
时间同步正确
```

与 Gazebo Truth 比较：

```text
位置ATE
姿态误差
相对位姿误差RPE
速度误差
延迟
更新频率
丢帧率
初始化时间
```

### 阶段二：经PX4融合后替换状态源

主对比路线：

```text
当前Gazebo仿真传感器
        ↓
PX4估计器
        ↓
/mavros/local_position/odom
        ↓
px4ctrl
```

替换为：

```text
FAST-LIO
        ↓
PX4外部里程计融合
        ↓
/mavros/local_position/odom
        ↓
同一个px4ctrl
```

这样控制器订阅 Topic、接口、频率和参数都不变，只改变 PX4 估计器的观测来源。

可保留附加实验：

```text
FAST-LIO直接输出
→ px4ctrl
```

但该实验属于直接外部里程计控制实验，不能与 PX4 融合状态主排行榜混为一组。

硬规则：

```text
FAST-LIO结果不参与px4ctrl基准参数是否调好的初始验收。
px4ctrl必须先在理想/融合状态下达到最优。
之后FAST-LIO造成的性能下降才有分析价值。
```

## 13. 后续控制器释放规则

以下列表定义为候选队列：

```text
ATTITUDE_THRUST_CONTROLLER_BACKLOG
```

候选：

```text
官方PID
增强PID
LQI
SE3 Basic
DFBC Basic
LMPC Attitude-Thrust
NMPC Attitude-Thrust
```

第一阶段唯一硬目标：

```text
PX4CTRL Golden Slice完整贯通
```

Golden Slice通过后，先做两个模板验证控制器：

### 第一个替换控制器：官方PID

原因：

```text
已有MWORKS模型
算法简单
便于验证生成代码模板
便于发现接口是否过度依赖px4ctrl
```

路线：

```text
MWORKS官方PID
→ 生成代码
→ 替换px4ctrl_core位置
→ 同一个Adapter
→ Gazebo
```

### 第二个替换控制器：SE3 Basic

原因：

```text
通常需要重新建立MWORKS模型
数学结构与PID不同
能够验证新控制器开发路线
仍然输出ATTITUDE_THRUST
```

只有下面三条都完成：

```text
px4ctrl Golden Slice通过
官方PID替换通过
SE3 Basic替换通过
```

才能确认模板具备批量扩展能力。

之后从 Backlog 中一次只释放一个或两个控制器任务，不提前承诺全部完成时间。

## 14. 答辩主线

最终答辩建议分四层：

### 核心层：MWORKS

```text
控制器建模
控制器参数优化
模型级仿真
代码自动生成
算法性能分析
编队控制模型
```

这是比赛主体。

### 工程验证层：PX4 + Gazebo + Sunray

```text
完整飞控闭环
真实消息接口
执行器动态
SITL
HITL
板载部署
真实机型验证
```

说明 MWORKS 中的算法不仅停留在模型中。

### 自主飞行扩展层：FAST-LIO + EGO + EGO-Swarm

```text
激光定位
实时建图
未知环境规划
多机无碰撞规划
```

说明控制器可以接入完整自主飞行系统。

### 平台展示层：UE + 前端

```text
高质量场景
运行控制
控制器切换
地图切换
多机状态
曲线和报告
```

答辩中不得说：

```text
在MWORKS中实现了FAST-LIO和EGO
```

应表述为：

```text
基于MWORKS完成控制系统的建模、仿真、优化与代码生成，
并通过标准接口接入PX4/Gazebo以及FAST-LIO、EGO等开源自主飞行组件，
形成从控制算法设计到复杂环境自主飞行验证的完整闭环。
```

## 15. 需要并入正式文档的位置

建议并入：

| 内容 | 并入目标 |
| --- | --- |
| 冻结结论、状态源、当前禁止项 | `MoSim控制体系总览.md` 顶部当前执行索引 |
| P0-P19顺序、并行支线、门禁 | `MoSim研发工作流与Agent任务编排规范.md` |
| MWORKS输入输出、ATTITUDE_THRUST范围 | `MoSim统一控制接口规范.md` |
| px4ctrl core拆分、控制核心职责 | `MoSim单机控制器实现规范.md` |
| 推力映射、代码生成、四方一致性 | `MoSim控制器代码生成与PX4部署规范.md` |
| 频率、状态源、误差比较 | `MoSim控制器调参与参数优化规范.md` |
| EGO/EGO-Swarm边界 | `MoSim规划与编队控制接口规范.md` |
| FAST-LIO误差对照与验收 | `MoSim控制系统测试与评价规范.md` |

## 16. 人工审核问题

正式并入前只剩一个需要用户确认的执行问题：

```text
是否允许把本文的 P0-P19 作为 WF-01 当前主线，替换原 WF-01 中较泛化的 P0-P14 阶段总览？
```

如果允许，WF-01 应保留泛化路线作为后续章节，但顶部当前阶段必须以本文 P0-P19 为准。
