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
| 当前 MWORKS 建模质量 | `1.0 kg`，用于已完成单机控制器复测 |
| 惯量 | `Ixx=0.0085, Iyy=0.0085, Izz=0.012` |
| 旋翼位置 | `±0.065 m` |
| Mid360 安装位置 | `{0.036, -0.0155, 0.075}` |
| 原始电机常数 | `8.54858e-06 N/(rad/s)^2` |
| SDF 视觉减速 | `rotorVelocitySlowdownSim=10` |
| MWORKS 折算升力系数 | `0.000854858` |
| MWORKS 悬停轴转速 | `53.56 rad/s` |

注意：`150.dae` 为约 `139 MB`，超过 GitHub 单文件限制。当前仓库内迁移的是轻量 STL/参数和 MWORKS 可视化资源，不应提交原始 DAE 大文件。

## 联网核验的硬件参数

### Sunray-150

公开产品页显示 Sunray-150 是面向科研的实验平台，开源代码覆盖控制、SLAM、规划和目标检测等方向。该信息可作为报告中“实物平台背景”的来源，而不是直接替代 MWORKS 动力学辨识。

| 型号 | 轴距 | 重量 | 续航 | 最大载重 | 尺寸 | 电池 | 飞控/主控 | 传感器 |
|---|---:|---:|---:|---:|---|---|---|---|
| Sunray150 基础款 | `150 mm` | `约 750 g` | `约 17 min` | `400 g` | `210 x 210 x 100 mm` | `4500 mAh` | `STM32H743VIH6`，PX4 开源版本 | 无前视单目、无三维激光雷达 |
| Sunray150 激光雷达款 | `150 mm` | `约 1080 g` | `约 11 min` | `200 g` | `210 x 210 x 100 mm` | `4500 mAh` | `STM32H743VIH6`，PX4 开源版本 | 前视单目 + `MID-360` |

Source: [云纵 Sunray-150 科研无人机](https://www.yundrone.cn/products/sunray-150).

相关电机公开配件参数：

| 项 | 数值 |
|---|---|
| 电机规格 | `2104` |
| KV | `3000` |
| 单电机重量 | `15.9 g` |
| 电池芯数 | `3-4S` |

Source: [云纵产品中心 - Sunray150 无刷电机](https://www.yundrone.cn/products).

迁移判断：当前 MWORKS 模型质量 `1.0 kg` 与公开激光雷达款 `约 1080 g` 接近，可继续作为控制器复测模型；报告中应写成“参考 Sunray150 激光雷达款量级并结合 SDF 参数折算”，不要写成完整实物辨识。

### Livox Mid-360

| 项 | 数值 |
|---|---|
| FOV | 水平 `360°`，垂直 `-7° ~ 52°`，最大垂直 `59°` |
| 探测距离 | `40 m @ 10%` 反射率，`70 m @ 80%` 反射率 |
| 近处盲区 | `0.1 m` |
| 距离随机误差 | `≤ 2 cm @ 10 m`，`≤ 3 cm @ 0.2 m` |
| 角度随机误差 | `≤ 0.15°` |
| 点频 | `200,000 points/s` |
| 帧率 | `10 Hz` 典型；本项目规划/安全层统一按 `20 Hz` 局部栅格更新抽象建模 |
| IMU | 内置 ICM40609，IMU 信息推送 `200 Hz` |
| 数据接口 | `100 BASE-TX Ethernet` |
| 同步 | IEEE 1588-2008 PTP v2、GPS |
| 防护 | `IP67` |
| 功耗 | `6.5 W`，低温自加热峰值可到 `14 W` |
| 供电 | `9-27 V DC` |
| 尺寸/重量 | `65 x 65 x 60 mm`，约 `265 g` |

Sources: [Livox Mid-360 中文产品页](https://www.livoxtech.com/cn/mid-360), [Livox Mid-360 User Manual PDF](https://www.sachtleben-technology.com/wp-content/uploads/2024/07/LivoxMid-360UserManual.pdf).

迁移判断：硬件物理资料按官方 `10 Hz` 典型帧率记录；Sysplorer 中为匹配当前控制器与 raw 输出节拍，先抽象为 `20 Hz` 局部栅格/点云更新源，噪声采用距离随机误差和角度随机误差的一阶近似；不直接复现 Livox 非重复扫描细节，除非后续要做感知算法对比。

### CUAV Pixhawk V6X / PX6C 级飞控

| 项 | 数值/说明 |
|---|---|
| 主处理器 | STM32H753，Cortex-M7，`480 MHz`，`2 MB Flash`，`1 MB RAM` |
| IO/协处理器 | STM32F103 / Cortex-M3 |
| IMU | ICM-42688-P / ICM-20649 / BMI088，三冗余 IMU |
| 磁罗盘 | RM3100 |
| 气压计 | ICP-20100 x2 / 双冗余气压计 |
| 输出 | `16 PWM` |
| 接口 | `TELEM x3`、`GPS x2`、`CAN x2`、`Ethernet x1`、`USB x2`、`SPI`、`ADIO`、`UART4`、TF 卡槽等 |
| 供电 | 额定 `4.75~5.70 V`；USB `4.75~5.25 V`；舵机轨 `0~9.9 V` |
| 工作温度 | `-20 ~ 85 °C` |
| 尺寸/重量 | `45.0 x 90.0 x 29.2 mm`，控制器约 `99 g` |
| 冗余设计 | 三冗余 IMU、双冗余气压计、独立总线/电源、多电源输入、双 GPS |

Sources: [CUAV Pixhawk V6X 文档](https://doc.cuav.net/controller/pixhawk-v6x/en/), [CUAV Official Store V6X specifications](https://store.cuav.net/shop/cuav-v6x/), [CUAV 中文产品页](https://www.cuav.net/v6x/).

迁移判断：Sysplorer 飞控状态机应建模“传感器健康度、IMU/气压计冗余切换、电源/通信异常、Offboard 控制丢失”这些行为；不需要迁移 MAVLink 驱动。

### 当前 Sysplorer 完整机体抽象

`QuadrotorModel.Mechanics.QuadChassis` 当前已包含：

| 子系统 | 当前实现 | 说明 |
|---|---|---|
| Sunray150 机体 | `sunray150_mid360_body.stl` | 质量 `1.0 kg`、惯量 `Ixx=0.0085, Iyy=0.0085, Izz=0.012` |
| 四旋翼旋翼/电机 | 4 个 propeller STL + 转速传感器 + 升力模型 | `lift_cofficient=0.000854858`，折算 `rotorVelocitySlowdownSim=10` |
| Mid360 | 机体前上方球形可视化件 + `mid360_update_rate_Hz=20` | 表达传感器安装位置与规划/安全层更新节拍，不做真实扫描线仿真 |
| V6X/PX6C 飞控 | 机体上方盒状可视化件 + `flight_controller_update_rate_Hz=20` | 表达飞控硬件和控制/模式管理节拍，不迁移 MAVLink 驱动 |
| GPS/GNSS | 机体顶部圆盘可视化件 + `gps_update_rate_Hz=20` | 表达导航输入和后续 failsafe 状态机接口 |
| ORIN NX 机载计算 | 机体上方盒状可视化件 + `onboard_computer_update_rate_Hz=20` | 表达规划、局部栅格和安全监督计算平台 |
| 地面/动画 | 原生 MWORKS MultiBody 动画 | 用于人工审核和视频素材 |

CUAV/Livox 实物图片仅作为报告和答辩硬件说明素材：

| 图片 | 用途 |
|---|---|
| `references/CUAV/V6X.png` | 飞控硬件说明 |
| `references/CUAV/GPS.png` | GPS/GNSS 硬件说明 |
| `references/CUAV/MId360.png` | Mid360 激光雷达硬件说明 |
| `references/CUAV/ORIN NX.jpg` | 机载计算平台说明 |

Sysplorer 模型内使用轻量几何体而非直接贴图，以保证仿真和动画稳定。

2026-05-14 最小 `QuadrotorModel.Examples.Example1` 检查曾触发授权限制：

```text
当前授权不允许变量方程数大于 300
```

该结果说明当前 MCP/授权环境无法检查完整官方模型，不作为新增几何件的模型错误结论。后续在授权恢复后需重新执行 `check_model`。

### PX4 Offboard / Failsafe

PX4 Offboard 模式要求外部控制器持续提供 `>2 Hz` 的 proof-of-life 信号；切入 Offboard 前需先接收超过 `1 s` 的有效 setpoint/OffboardControlMode 流。若外部控制信号低于 `2 Hz`，PX4 会在 `COM_OF_LOSS_T` 超时后退出 Offboard，并按 `COM_OBL_RC_ACT` 执行 Position/Altitude/Manual/Return/Land 等动作。

关键参数：

| 参数 | 建模含义 |
|---|---|
| `COM_OF_LOSS_T` | Offboard 连接丢失后的超时时间 |
| `COM_OBL_RC_ACT` | Offboard 丢失后的模式切换动作，包含 Position、Altitude、Manual、Return、Land |
| `COM_RCL_EXCEPT` | 可设置在 Offboard 模式下忽略 RC loss |
| `COM_FAIL_ACT_T` | 触发 failsafe 到执行动作之间的反应延迟 |
| `COM_LOW_BAT_ACT` / `BAT_LOW_THR` / `BAT_CRIT_THR` / `BAT_EMERGEN_THR` | 低电量告警、返航、紧急降落阈值 |
| `COM_DLL_EXCEPT` | 数据链路丢失例外模式 |

Sources: [PX4 Offboard Mode](https://docs.px4.io/main/en/flight_modes/offboard), [PX4 Safety/Failsafe Configuration](https://docs.px4.io/main/en/config/safety).

迁移判断：后续安全返航/降落闭环可以按 `NORMAL -> OFFBOARD_ACTIVE -> OFFBOARD_LOSS_HOLD -> RETURN -> LAND` 建模；单机控制器仍接收连续轨迹参考，多机/规划层负责触发模式切换和安全目标生成。

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

## 是否还需要下载其他仓库

暂时不建议继续下载大型 Gazebo/PX4/算法仓库。当前 `references/Sunray` 已包含：

- EGO-Planner-Swarm；
- FUEL；
- ORCA / formation control；
- grid map、A*、B-spline、trajectory server；
- PX4/MAVROS 控制接口参考；
- Sunray150 / Sunray300 SDF 与传感器配置。

如果后续确实需要补仓库，优先级如下：

| 优先级 | 仓库/资料 | 何时需要 |
|---|---|---|
| P1 | 不再补仓库，直接用当前 Sunray 内置 EGO/FUEL/ORCA | 当前 Sysplorer 迁移阶段 |
| P2 | Livox ROS Driver 2 | 只有在要复现真实 Mid360 点云话题和驱动接口时 |
| P2 | PX4-Autopilot 官方仓库 | 只有在要核对 PX4 源码级 failsafe 状态机时 |
| P3 | EGO-Planner 或 FUEL 原始上游仓库 | 只有当 Sunray 内置版本缺文件或需要追溯算法论文实现差异时 |

当前工作重点应该是把已有 Sunray 代码里的接口和算法迁移成 MWORKS/Sysplorer 模块，而不是继续堆仓库。

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
