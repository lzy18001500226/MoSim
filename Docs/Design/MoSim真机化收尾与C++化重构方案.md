# MoSim真机化收尾与C++化重构方案

> 本文冻结当前 Sunray ROS1 / Gazebo Classic / PX4 / MAVROS / px4ctrl /
> FAST-LIO / EGO 基准之后的收尾重构方向。目标不是推倒重来，而是把后续
> 可部署到机载计算机和真实飞控的链路边界先设计清楚。

## 1. 总体决策

当前不做大重写。

正确动作是：

```text
保留已经跑通的基准链路
  -> 明确哪些代码只是仿真/诊断工具
  -> 把实时闭环关键节点收口为C/C++或可编译组件
  -> 增加真机传感器等价约束
  -> 再继续FAST-LIO、EGO、EGOv2、Diff-Planner和集群
```

不得继续出现：

```text
为了跑通结果临时手写Python控制器
Python节点直接承担正式控制律
Python节点直接绕过PX4写Gazebo电机/执行器
只看漂亮仿真参数而不记录状态源、传感器、时钟和部署边界
```

本文的核心原则：

```text
控制器核心可生成、可编译、可离线一致性测试。
实时状态源和PX4适配层可编译、可部署、可诊断。
Python保留为实验编排、指标统计、可视化和离线工具。
仿真必须逐步逼近真机传感器与飞控链路，而不是只追求单场景最优参数。
```

## 2. 目标硬件边界

当前面向的真机部署约束：

```text
机载计算:
  Orin NX 16G级别伴随计算机

飞控:
  雷迅 / CUAV V6X级别 PX4 飞控

主定位/建图传感器:
  MID360级别3D LiDAR + 内置IMU

高度辅助:
  下视激光/测距传感器等价约束

视觉:
  前视/下视/多机第一视角摄像头，主要服务展示、感知扩展和后续任务
```

真机上不会运行“无限算力仿真脚本”。因此，凡是进入在线闭环的模块都必须考虑：

```text
CPU占用
内存占用
消息频率
实时性
延迟
丢帧
初始化状态
异常回退
日志可诊断性
```

## 3. 代码分层冻结

### 3.1 T0：控制器核心层

必须使用 C/C++ 或由 MWORKS 生成的标准 C/C++。

范围：

```text
px4ctrl_core
MWORKS生成的PID / SE3 / DFBC / NMPC / INDI / L1等控制器核心
控制器状态机中必须与控制律强绑定的reset、enable、integrator、saturation逻辑
```

要求：

```text
不依赖ROS消息类型
不依赖Gazebo API
不依赖Python运行时
输入输出使用统一ControllerInput / ControllerOutput或等价结构体
先离线一致性测试，再进入Gazebo闭环
```

### 3.2 T1：实时适配层

正式闭环中应使用 C++ ROS 节点或可编译组件。

范围：

```text
FAST-LIO odom对齐与base_link转换
PX4 external vision / odometry发布
trajectory server在线轨迹求值
Controller Adapter：物理推力到MAVROS/PX4归一化推力
状态源选择与质量门禁
safety / failsafe / stale-command monitor
多机topic命名、实例隔离和状态聚合
```

这些模块直接影响控制状态、控制输出或飞行安全，不能长期停留在临时 Python
节点中。

### 3.3 T2：上游C++自主飞行组件

保留上游 C++ 工程，不重写：

```text
FAST-LIO
EGO-Planner
EGO-Planner-v2
Diff-Planner
EGO-Swarm
px4ctrl原始上游/工程版
```

MoSim负责：

```text
固定版本
写清接口
配置适配
记录输入输出证据
建立与MWORKS生成控制器的边界
```

不把完整FAST-LIO、EGO或EGO-Swarm搬进 MWORKS。

### 3.4 T3：Python工具层

Python允许保留在非实时工具层。

允许：

```text
launch/批处理包装
日志解析
指标计算
CSV/JSON整理
画图
RViz/Gazebo review包生成
离线对齐测试
一次性迁移脚本
文档/报告生成
```

不允许长期作为正式闭环：

```text
控制律计算
姿态/推力实时输出
PX4 external odometry正式发布
FAST-LIO odom正式坐标转换
多机实时状态调度
安全回退控制
```

如果某个 Python 节点当前已经承担 T1/T0 职责，应标记为：

```text
prototype_only
must_port_to_cpp_before_flight_like_claim
```

## 4. 当前代码收尾清单

### 4.1 保留但标注为工具层

以下类型继续保留 Python：

```text
Scripts/sunray/*metrics*
Scripts/sunray/*review*
Scripts/sunray/*record*
Scripts/sunray/*audit*
Scripts/sunray/*plot*
```

它们可以作为证据工具，不作为控制器部署证据。

### 4.2 需要C++化或生成代码化的候选

优先级从高到低：

| 优先级 | 模块 | 当前风险 | 收尾目标 |
|---|---|---|---|
| P0 | MWORKS生成控制器core包装 | 控制器不能停留在脚本等价替代 | 生成C/C++ + C++ IController wrapper |
| P0 | FAST-LIO aligned odom adapter | 直接决定状态源，错误会炸机 | C++节点，输出base_link完整pose、velocity、quality |
| P0 | PX4 external odometry publisher | 直接影响EKF融合 | C++节点，修正timestamp、frame、velocity、covariance/status |
| P1 | trajectory server | 轨迹求值频率和相位影响控制误差 | C++或复用上游C++ traj server，100Hz解析求值 |
| P1 | Controller Adapter | 推力归一化、坐标系、Offboard消息 | C++节点，统一ATTITUDE_THRUST语义 |
| P1 | pointcloud_to_world在线桥 | planner输入地图依赖位姿转换 | 若进入正式在线planner链路，应C++/PCL化 |
| P2 | 多机状态聚合与review路径 | 影响展示和验收 | 可先Python，正式多机在线控制前C++化 |

### 4.3 当前重构审计入口

当前第一阶段不直接替换已跑通的 Sunray/PX4/Gazebo 基线，而是先用静态审计
冻结实时闭环代码分层：

```text
python Scripts/quality/audit_runtime_tier_refactor.py
python Scripts/tests/test_runtime_tier_refactor_audit.py
python Scripts/quality/check_sunray_cpp_frame_transform.py
python Scripts/tests/test_sunray_cpp_frame_transform.py
```

审计输出：

```text
Results/refactor/runtime_tiers/runtime_tier_refactor_audit.json
Results/refactor/runtime_tiers/runtime_tier_refactor_audit.md
```

当前已识别的状态：

| ID | 层级 | 当前状态 | 处理原则 |
|---|---|---|---|
| px4ctrl_core_cpp | T0 | C++ core 已存在 | 保持 ROS-free，继续离线一致性测试 |
| px4ctrl_core_c_abi | T0 | C ABI 已存在 | 作为 MWORKS/生成代码一致性桥接形态 |
| px4_external_odometry_publisher | T1 | Sunray external_fusion C++ 基线已存在 | 优先复用，不急于重写 |
| fastlio_frame_transform_cpp_math | T1 | C++ helper 已存在 | 作为 FAST-LIO 对齐节点 C++化的数学基础 |
| fastlio_odom_alignment_adapter | T1 | Python prototype | P0，必须 C++化后才能作为飞行级状态源适配 |
| trajectory_reference_server | T1 | Python prototype | P1，正式在线轨迹求值应 C++化或复用上游 C++ |
| pointcloud_to_world_bridge | T1 | Python prototype | P1，正式 planner 在线输入应 C++/PCL化 |
| position_cmd_safety_adapter | T1 | Python prototype | P1，planner 命令安全门禁应 C++化 |
| metrics_and_review_recorders | T3 | Python工具层 | 可继续保留 |

任何 `prototype_only_must_port` 项都可以继续支持当前 review/prototype 运行，
但不得被写成“可真机部署”或“飞行级闭环”证据。迁移顺序优先：

```text
FAST-LIO odom alignment
  -> trajectory reference server
  -> pointcloud_to_world bridge
  -> position_cmd safety adapter
```

其中 FAST-LIO odom alignment 的第一步已经拆出纯 C++ 数学 helper：

```text
Scripts/sunray/cpp/mosim_sunray_runtime_adapters/include/
  mosim_sunray_runtime_adapters/fastlio_frame_transform.hpp
```

该 helper 只证明坐标变换数学可以在 C++ 中编译和单元检查，不等于
ROS1 `fastlio_odom_alignment_adapter.py` 已被替换。

## 5. 真机化仿真约束

当前仿真不能只看“误差小”。必须逐步加入真机等价约束。

### 5.1 MID360约束

MID360相关仿真应记录：

```text
LiDAR频率
点数/帧
有效距离
盲区
FOV
点时间/scan模式
内置IMU频率
LiDAR与IMU时间同步
LiDAR-IMU外参
LiDAR到飞控中心外参
```

FAST-LIO能否入控不由RViz点云是否可见决定，而由：

```text
FAST-LIO aligned odom
vs
Gazebo/Sunray truth
```

的误差、延迟、稳定性和PX4 EKF融合结果决定。

### 5.2 Z高度策略

当前可以使用 Gazebo Z 作为下视定高传感器替身，但必须显式标注：

```text
z_source = gazebo_rangefinder_surrogate
truth_control_input_allowed = true_for_rangefinder_surrogate_only
```

后续应替换为更接近真机的仿真测距链路：

```text
Gazebo ray / range sensor
  -> rangefinder topic
  -> noise / delay / range limit
  -> PX4 EKF height aiding 或控制状态源
```

禁止把 Gazebo truth Z 静默混进 FAST-LIO 定位结果后宣称“全FAST-LIO定位”。

### 5.3 摄像头与多机展示

三机展示目标：

```text
RViz窗口1:
  FAST-LIO累计点云地图 + 每机机体三轴/轨迹

RViz窗口2:
  局部/全局栅格地图 + planner轨迹 + 多机目标/障碍

摄像头窗口:
  每架飞机一个第一视角窗口
```

三机时展示窗口数量为：

```text
2个RViz窗口 + 3个相机窗口 = 5个窗口
```

该窗口结构属于地面站/演示PC，不要求机载 Orin 同时渲染所有窗口。机载端只需发布
必要图像流、状态、点云、里程计和诊断。

### 5.4 鲁棒性优先于单场景最优

真机参数一定会重新调，因此仿真阶段不能只追求某一组参数漂亮。

控制器验收应增加：

```text
质量扰动
惯量扰动
推力系数扰动
电机响应延迟
风扰
传感器噪声
状态估计延迟
LiDAR丢帧
定位跳变
电池电压/推力裕度变化
```

如果一个控制器只有在精确仿真参数下才能满足指标，则不能称为鲁棒控制器。

## 6. 最小收尾Gate

### G-CLOSE-0：代码职责审计

输出：

```text
Results/refactor/runtime_tiers/runtime_tier_refactor_audit.json
Results/refactor/runtime_tiers/runtime_tier_refactor_audit.md
```

命令：

```text
python Scripts/quality/audit_runtime_tier_refactor.py
python Scripts/tests/test_runtime_tier_refactor_audit.py
```

判定每个关键脚本/节点属于 T0/T1/T2/T3 哪一层，并固定哪些 Python
节点只是 prototype。该 Gate 只做静态职责审计，不启动 ROS、Gazebo、PX4、
RViz 或 MWORKS。

### G-CLOSE-1：FAST-LIO状态源冻结

复用：

```text
Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md
```

先完成 D-FL0 到 D-FL6，再允许进入闭环控制。

### G-CLOSE-2：控制器正式路径冻结

每个控制器必须有：

```text
MWORKS模型或上游C++来源
离线一致性测试
C/C++ core
C++ adapter
Gazebo闭环结果
manifest中明确状态源和输出接口
```

### G-CLOSE-3：真机化传感器Profile

每个可展示场景必须记录：

```text
MID360 profile
rangefinder/Z profile
camera profile
noise/delay/drop profile
state source profile
```

### G-CLOSE-4：多机展示Profile

冻结：

```text
每机命名空间
每机PX4/MAVROS实例
每机FAST-LIO/状态源
每机camera topic
两个RViz review config
N个camera first-person窗口
```

## 7. 文档关系

本方案是以下文档的执行补充：

```text
Docs/Design/架构.md
Docs/Design/MoSim控制体系总览.md
Docs/Design/MoSim控制器代码生成与PX4部署规范.md
Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
```

后续如果新增或迁移实时节点，必须同时更新本方案的职责层级或对应执行Gate。

## 8. 外部资料依据

当前硬件边界引用：

```text
云纵 MID360 文档:
  https://wiki.yundrone.cn/docs/san-wei-ji-guang-lei-da

Livox MID-360 官方页面:
  https://www.livoxtech.com/cn/mid-360

CUAV Pixhawk V6X / V6X V2:
  https://www.cuav.net/v6x/
```

这些资料只用于冻结真机化传感器和飞控约束；具体仿真参数仍以本项目当前
Sunray/Gazebo模型、SDF、launch、PX4参数和同次运行证据为准。
