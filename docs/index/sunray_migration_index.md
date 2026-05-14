# Sunray 迁移索引

> 目的：把 `references/Sunray` 中和本项目后续 Sysplorer 迁移有关的代码、模型、配置和风险集中到一个检索入口。本文只做索引和迁移判断，不把 ROS/Gazebo 代码等同于 MWORKS 证据。

## 当前迁移方向

本项目后续不再以 Gazebo 部署为主线，而是把 Sunray 的高价值模块迁移到 Sysplorer/MWORKS：

1. 机体与传感器：以 `sunray150_with_mid360` 为当前主机体来源。
2. 飞控与硬件背景：按雷迅 PX6C / CUAV V6X 级别飞控建模，图片素材位于 `references/CUAV/GPS.png`、`references/CUAV/V6X.png`。
3. 任务层：栅格地图、单机路径规划避障、多机编队避障迁移到 Sysplorer 图形化/方程化模型。
4. 控制层：继续以现有单机鲁棒位姿控制器为主线，规划和编队作为上层参考生成与约束管理模块。

## 高优先级目录

| 方向 | 路径 | 用途 | 迁移建议 |
|---|---|---|---|
| Sunray 消息和公共工具 | `references/Sunray/General_Module/sunray_common` | `sunray_msgs`、几何/控制工具、日志工具 | 只抽取消息字段和数学工具，不迁移 ROS 依赖 |
| 无人机控制接口 | `references/Sunray/General_Module/sunray_uav_control` | PX4/MAVROS 控制节点、UAVControlCMD、位置控制器、参数文件 | 用于定义 Sysplorer 控制接口和飞控模式状态机 |
| 规划桥接 | `references/Sunray/General_Module/sunray_planner_utils` | EGO/FUEL 输出到 Sunray 控制指令的桥接 | 迁移为 Sysplorer `PlannerCommand -> ControllerReference` 接口 |
| EGO-Planner-Swarm | `references/Sunray/External_Module/ego-planner-swarm` | 局部地图、A*/B-spline 优化、多机轨迹广播 | 抽取 A*/B-spline/栅格地图思想，重写为 MWORKS 模块 |
| FUEL | `references/Sunray/External_Module/FUEL` | 主动探索、frontier、拓扑路径、TSP | P2/P3 拓展；不进入当前单机控制器收尾主线 |
| 编队控制 | `references/Sunray/sunray_formation/formation_control` | 静态队形、动态队形、leader-follower、任务命令 | 迁移为 Sysplorer 多机编队状态机和队形参考生成 |
| ORCA 避碰 | `references/Sunray/sunray_formation/sunray_orca` | RVO2/ORCA 多智能体速度避障 | 迁移为多机安全约束/速度投影层，可与 CBF 对照 |
| 机体模型 | `references/Sunray/simulation/sunray_simulator/models/drone_models` | Sunray150/300 SDF、STL、传感器安装位 | 已采用 `sunray150_with_mid360`；大网格文件不要直接迁入 Git |
| 风扰/传感器插件 | `references/Sunray/simulation/gazebo_plugin` | wind_zone、Livox、Realsense 插件 | 只抽取参数和模型假设，Sysplorer 内重建扰动模型 |

## 已采用机体源

| 项 | 路径 / 数值 |
|---|---|
| 主机体源 | `references/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360` |
| 质量 | `1.0 kg` |
| 惯量 | `Ixx=0.0085, Iyy=0.0085, Izz=0.012` |
| 旋翼位置 | `±0.065 m` |
| Mid360 安装位置 | `{0.036, -0.0155, 0.075}` |
| 原始电机常数 | `8.54858e-06 N/(rad/s)^2` |
| SDF 视觉减速 | `rotorVelocitySlowdownSim=10` |
| MWORKS 折算升力系数 | `0.000854858` |
| MWORKS 悬停轴转速 | `53.56 rad/s` |

注意：`150.dae` 为约 `139 MB`，超过 GitHub 单文件限制。当前仓库内迁移的是轻量 STL/参数和 MWORKS 可视化资源，不应提交原始 DAE 大文件。

## 单机路径规划索引

### EGO-Planner-Swarm

| 模块 | 路径 | 关注点 |
|---|---|---|
| 重规划 FSM | `External_Module/ego-planner-swarm/src/planner/plan_manage` | 触发重规划、轨迹执行状态 |
| B-spline 优化 | `External_Module/ego-planner-swarm/src/planner/bspline_opt` | 平滑、碰撞、可行性代价 |
| 路径搜索 | `External_Module/ego-planner-swarm/src/planner/path_searching` | 动态 A* |
| 地图环境 | `External_Module/ego-planner-swarm/src/planner/plan_env` | 栅格地图、raycast、障碍膨胀 |
| 轨迹消息 | `External_Module/ego-planner-swarm/src/planner/traj_utils` | B-spline 轨迹数据结构 |
| 多机广播 | `External_Module/ego-planner-swarm/src/planner/rosmsg_tcp_bridge` | 多机 B-spline / odom 交换 |

### Sunray 桥接层

| 文件 | 作用 | 迁移关注点 |
|---|---|---|
| `General_Module/sunray_planner_utils/src/positionCmd2sunray.cpp` | 把 `PositionCommand` 转为 `UAVControlCMD` | 参考位置、速度、加速度、yaw 接口 |
| `General_Module/sunray_planner_utils/src/goal2swarm.cpp` | 把 RViz/航点目标扩展为多机目标 | 多机目标偏置、队形初始目标 |
| `General_Module/sunray_planner_utils/launch/sunray_ego_single_mid360.launch` | 单机 Mid360 + EGO 规划链路 | 地图尺寸、分辨率、膨胀、速度/加速度限制 |
| `General_Module/sunray_planner_utils/launch/sunray_ego_swarm.launch` | 三机 EGO swarm 链路 | 多机目标、点云变换、多机规划参数 |
| `General_Module/sunray_planner_utils/launch/sunray_fuel_mid360.launch` | Mid360 + FUEL 探索链路 | 后续主动探索任务 |

已发现注意点：

- `positionCmd2sunray.cpp` 在连续 `XyzPosYaw` 指令重复时会跳过发布，迁移到 Sysplorer 时不应简单照搬。
- `goal2swarm.cpp` 里存在硬编码 `/home/yundrone/Sunray/...` 路径，必须参数化。
- 多机 launch 中存在 `run_in_single.launch` 引用，需要后续核对文件实际位置。

## 多机编队与避障索引

| 模块 | 路径 | 作用 |
|---|---|---|
| 编队控制主类 | `sunray_formation/formation_control/src/formation_control.cpp` | 接收 formation_cmd，发布 ORCA 目标和 UAV 控制命令 |
| 编队配置 | `sunray_formation/formation_control/config/*.yaml` | 静态/动态队形、8 字、圆形、航点 |
| leader-follower | `sunray_formation/formation_control/leader_follower` | Leader 任务、Follower 目标偏置、ORCA 指令 |
| ORCA 节点 | `sunray_formation/sunray_orca/src/orca.cpp`、`orca_node.cpp` | 20 Hz 多智能体速度避碰 |
| ORCA 参数 | `sunray_formation/sunray_orca/launch/orca*.launch` | `neighborDist`、`timeHorizon`、`radius`、`maxSpeed`、`time_step` |
| RViz 多机仿真 | `sunray_formation/formation_sim` | 轻量级编队可视化参考 |

已发现注意点：

- `formation_control.cpp` 的 `orca_cmd_callback` 中存在疑似条件错误：`if (state != ... || GOAL)` 形式会导致 ORCA 回调可能一直提前返回。迁移前必须修正为明确的状态/类型判断。
- `leader_follower` 中通信超时变量命名和语义不够清楚，迁移时应重写为 `communication_ok` / `timeout` 两个状态。
- 多机避障不应直接依赖 ROS topic；在 Sysplorer 中应建模为 `agent_state_bus -> safety_velocity_projection -> formation_reference`。

## PX4 / 飞控接口索引

| 文件/目录 | 用途 |
|---|---|
| `General_Module/sunray_uav_control/config/px4_config.yaml` | PX4/MAVROS 配置参考 |
| `General_Module/sunray_uav_control/config/uav_control_param*.yaml` | 控制器参数、模式参数 |
| `General_Module/sunray_uav_control/uav_control/UAVControl.cpp` | Sunray UAV 控制命令执行主逻辑 |
| `General_Module/sunray_uav_control/uav_control/pos_controller/pos_controller_pid.h` | 位置控制器参考 |
| `General_Module/sunray_uav_control/mavlink` | MAVLink 串口/接口封装 |
| `Comunication_Module/sunray_communication_bridge` | 通信桥、PX4 参数管理 |

迁移策略：

1. 不迁移 MAVROS/MAVLink 通信代码。
2. 抽取飞控模式、命令类型、约束、故障状态，建立 Sysplorer 飞控状态机。
3. 用 PX6C/V6X 作为硬件背景和报告对象，不把硬件驱动作为当前仿真必要条件。

## 栅格地图与障碍物索引

| 来源 | 路径 | 可迁移内容 |
|---|---|---|
| EGO plan_env | `External_Module/ego-planner-swarm/src/planner/plan_env` | 占据栅格、局部更新、障碍膨胀 |
| FUEL plan_env | `External_Module/FUEL/fuel_planner/plan_env` | SDF/EDT 地图、探索环境 |
| map_generator | `simulation/simulator_utils/map_generator`、`External_Module/*/map_generator` | 随机障碍、仿真地图生成 |
| sunray_simulator worlds | `simulation/sunray_simulator/worlds` | 场景/障碍布局参考 |
| gazebo_plugin random cylinder | `simulation/gazebo_plugin/random_cylinder_plugin` | 随机圆柱障碍参数参考 |

Sysplorer 迁移建议：

- P1：二维/三维栅格地图数据结构 + A* 路径搜索 + minimum-snap/B-spline 平滑。
- P2：局部障碍膨胀 + 速度/加速度约束 + CBF/ORCA 安全投影。
- P3：FUEL frontier 探索与 TSP 任务排序。

## 当前不建议迁入 Git 的内容

| 路径 | 原因 |
|---|---|
| `simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/150.dae` | 约 139 MB，超过 GitHub 单文件限制 |
| `simulation/sunray_simulator/models/drone_models/sunray150_D435i/meshes/150.dae` | 约 139 MB，超过 GitHub 单文件限制 |
| `External_Module/sunray_detection/yolov7/model/yolov7.plan` | 约 76 MB，当前任务不需要深度学习推理引擎 |
| `simulation/gazebo_plugin/livox_laser_simulation/scan_mode/*.csv` | 每个约 25-35 MB，Sysplorer 只需要抽象扫描模型 |
| ROS build/devel/log 产物 | 可再生成，不应作为源文件提交 |

## 还建议补充下载/提供的资料

当前 Sunray 已足够支撑“机体、PX4接口、单机规划、多机编队避障”的迁移设计。若要把 PX6C/V6X 背景建模得更完整，建议后续再补：

1. 雷迅 PX6C 或 CUAV V6X 官方参数手册 PDF：尺寸、质量、IMU、接口、供电、冗余特性。
2. Mid360 官方参数手册：扫描频率、视场角、量程、点频、噪声。
3. sunray150_with_mid360 对应实物或官方配置说明：机臂长度、电机/桨叶型号、电池质量。
4. 如果要做更像真实飞控的状态机：PX4 flight mode / failsafe / offboard control 官方文档或参数表。

暂时不建议继续下载大型 Gazebo/PX4 仓库。当前工作重点应该是把已有 Sunray 代码里的接口和算法迁移成 MWORKS/Sysplorer 模块。

## 后续迁移任务清单

| 优先级 | 任务 | 输出位置 |
|---|---|---|
| P0 | 维持单机控制器结果收尾和人工审核清单更新 | `results/人工审核清单.csv`、`docs/simulation_report.md` |
| P1 | 建立 `PlannerCommand`、`GridMap`、`TrajectoryReference`、`FormationCommand` 标准接口 | `Design/02_模型接口与运行流程.md`、`docs/index/variable_mapping.md` |
| P1 | 从 EGO 抽取 A*/B-spline/minimum-snap 迁移设计 | `Design/05_路径规划与轨迹生成.md` |
| P1 | 从 ORCA/formation_control 抽取多机避障和队形状态机 | `Design/06_多机编队控制.md` |
| P2 | 建立 Sysplorer 图形化单机避障规划模型 | `models/QuadrotorPlanning*` |
| P2 | 建立 Sysplorer 三机编队与 ORCA/CBF 安全层模型 | `models/QuadrotorFormation*` |
| P2 | 增加多机指标：队形 RMSE、最小机间距、避障约束违反数 | `scripts/calc_metrics.py`、`Design/08_仿真指标与自动评估.md` |
