# MoSim FAST-LIO定位闭环与规划复现基础方案

> 本文冻结 Sunray ROS1 / Gazebo Classic / MID360 / FAST-LIO / PX4 / MAVROS
> / px4ctrl / EGO 系列规划复现的定位与坐标系基础。它是后续起飞悬停降落、
> 8字、螺旋、阶跃、EGO、EGO-Planner-v2、Diff-Planner、EGO-Swarm
> 仿真的前置设计文档。

## 1. 目标

当前问题不是单独的控制器调参问题，而是闭环状态源边界必须先冻结：

```text
MID360点云与IMU
  -> FAST-LIO
  -> 雷达/机体坐标系对齐
  -> PX4 EKF external vision / odometry 融合
  -> MAVROS local_position
  -> px4ctrl
  -> Gazebo plant
  -> planner / controller / localization 指标分层评价
```

本文的目标是：

1. 明确之前 EGO、EGO-Planner-v2、Diff-Planner 复现的状态源边界。
2. 明确 FAST-LIO 输出如何转换到飞控中心 `base_link`。
3. 明确 yaw、高度、速度、时间戳如何进入 PX4 EKF。
4. 明确先做哪些最小闭环，再恢复 planner 和集群。
5. 防止后续把 planner 通过、Gazebo truth 辅助定位、FAST-LIO 定位闭环三类证据混在一起。

## 2. 当前事实边界

### 2.1 已完成的planner复现是什么

截至当前，以下结果属于 planner 工程链路复现：

```text
EGO:
  Results/sunray_ros1/sunray_ros1_goal4_ego_single_pcfilter_infl020_20260623_023345

EGO-Planner-v2:
  Results/sunray_ros1/sunray_ros1_goal4_egov2_single_20260623_031346

Diff-Planner:
  Results/sunray_ros1/sunray_ros1_goal4_diff_single_landfix_20260623_041031
```

它们证明：

```text
raw MID360 PointCloud2
  -> pointcloud_to_world
  -> planner occupancy/grid
  -> planner position_cmd / bspline
  -> px4ctrl
  -> MAVROS/PX4
  -> Gazebo
```

但它们没有证明：

```text
FAST-LIO定位闭环
FAST-LIO输出状态源替换PX4/Gazebo辅助定位
FAST-LIO高度或yaw已进入PX4 EKF
最终自主飞行定位链路
多机定位/规划隔离已完成
```

### 2.2 当前planner复现的坐标系来源

当前 planner 复现中的栅格地图来自：

```text
/uav1/livox/lidar
  -> pointcloud_to_world
  -> /uav1/livox_world
  -> EGO / EGOv2 / Diff-Planner内部grid/occupancy
```

`pointcloud_to_world` 使用的是当前无人机位姿，把雷达点云转到 world/map
系。该当前位姿来自 MAVROS/PX4 local position，而不是 FAST-LIO
`/Odometry`。

因此，当前 planner 复现不是“FAST-LIO地图驱动planner”，而是：

```text
Gazebo/PX4/MAVROS状态支撑的点云转world + planner工程链路复现
```

### 2.3 当前MAVROS local position是什么意思

`/uav1/mavros/local_position/pose`、
`/uav1/mavros/local_position/velocity_local`、
`/uav1/mavros/local_position/odom`
是 PX4 EKF 输出到 MAVROS 的本地估计状态，不是一个独立传感器。

在当前 Sunray/Gazebo 仿真中，`external_fusion` 可使用
`/uav1/sunray/gazebo_pose` 作为外部定位源，并通过
`/uav1/mavros/vision_pose/pose` 把外部位姿送入 PX4。因此当前
MAVROS local position 在仿真里可以被 Gazebo truth 外部视觉支撑。

这不是最终雷达定位闭环；它是仿真中用于先跑通控制器和planner的基准状态源。

### 2.4 2026-06-22 FAST-LIO直连控制事故结论

最新失败包：

```text
Results/agent_packets/blockers/SUNRAY-ROS1-FASTLIO-DIRECT-CONTROL-BLOCKER-20260622-001.json
```

该失败不是 px4ctrl 基准控制律本身失效，而是把候选 FAST-LIO 状态源直接喂给
px4ctrl 后，定位输出发散并被控制器放大：

```text
控制状态源:
  /mosim/fastlio/odom_aligned

结果:
  trajectory_xyz_rmse_m = 6.103786
  trajectory_xyz_max_m  = 6.684608
  steady_hover_z_rmse_m = 0.909472
  debug_des_thr_magnitude = 1e161
  mavros_armed_during_figure8 = false

诊断:
  control_odom.csv 约到 x=71.09, y=-173.67
  Gazebo/Sunray truth 约在 x=6.41, y=3.62
```

因此当前结论冻结为：

```text
/uav1/mavros/local_position/odom:
  当前基准控制状态源，可继续用于px4ctrl、EGO、EGOv2、Diff-Planner工程复现。

/mosim/fastlio/odom_aligned:
  当前只能作为被测定位候选和评价对象。
  在G-FL0/G-FL1/G-FL2/G-FL3通过前，禁止作为px4ctrl控制输入。
```

当前不是“XY永远没法用”，而是：

```text
FAST-LIO aligned XY尚未通过定位门禁，不能用于控制闭环。
FAST-LIO点云、累计地图和RViz可见性不能替代定位误差验证。
```

之前没有暴露该问题的原因：

1. 之前基准控制、8字、螺旋和 EGO 单机主要使用
   `/uav1/mavros/local_position/odom`，FAST-LIO没有进入控制闭环。
2. 之前 planner 复现使用 MAVROS/PX4 状态把点云转到 world/map，并不等于
   FAST-LIO odom 驱动 planner 或控制器。
3. RViz中点云、累计地图或轨迹可见，只证明显示/建图链路有数据，不证明
   odom 与飞控中心、Gazebo truth、PX4 local frame 一致。
4. 只做起点 offset 对齐会掩盖初始误差，但不能证明飞行过程中的 yaw、roll、
   pitch、速度frame、时间戳和外参都正确。
5. 一旦把错误定位输入 px4ctrl，控制器会按“飞机偏差巨大”计算姿态和推力，
   所以错误会从定位层放大成炸机/解锁失败。

## 3. 术语冻结

| 名称 | 含义 | 当前用途 |
|---|---|---|
| Gazebo truth | `/uav1/sunray/gazebo_pose` 或 Gazebo model state | 评价真值；也可作为当前仿真基准external vision来源 |
| MAVROS local position | PX4 EKF输出的本地位置/速度/姿态 | px4ctrl当前默认状态源 |
| FAST-LIO raw odom | FAST-LIO `/Odometry` | 雷达/IMU body在`camera_init`中的位姿，不可直接当飞控中心 |
| FAST-LIO aligned odom | `/mosim/fastlio/odom_aligned` | 经过mount和初始对齐后的`world/map -> base_link`候选位姿 |
| planner world cloud | `/uav1/livox_world` | raw LiDAR通过当前状态源转到world/map后的planner输入 |
| occupancy/grid | EGO内部局部栅格地图 | 规划器内部避障地图，不等于FAST-LIO累计地图 |

## 4. 坐标系设计

### 4.1 FAST-LIO输出不可直接喂PX4

FAST-LIO `/Odometry` 表示：

```text
camera_init -> Livox / LiDAR / IMU body
```

px4ctrl / PX4 需要的是：

```text
world/map -> UAV base_link / flight-control body center
```

MID360 不在飞控中心，且当前装配姿态为：

```text
base_link -> livox_mid360::base_link
xyz = -0.000005 0.032295 0.050167
rpy = 0 0 4.712389
```

因此对齐关系应为：

```text
T_world_base = T_world_livox * inverse(T_base_livox)
```

不能把 FAST-LIO `/Odometry` 直接发布到 MAVROS。

展开到位置和姿态时，必须使用完整SE(3)变换：

```text
R_world_base = R_world_livox * inverse(R_base_livox)
p_world_base = p_world_livox - R_world_base * p_base_livox
q_world_base = q_world_livox * inverse(q_base_livox)
```

其中 `p_base_livox` 和 `q_base_livox` 来自装配外参。由于 MID360 不在飞机
正中心，不能只传yaw，也不能用固定world偏移替代外参补偿。进入PX4的姿态必须
是完整 `q_world_base` 四元数；yaw只是G-FL1/G-FL3里重点检查的投影指标。

### 4.2 yaw对齐原则

视觉外壳朝向不能证明传感器坐标系方向。必须通过运动验证：

```text
机头向前移动 -> base_link x应增加
机体向左移动 -> base_link y应增加
升高 -> base_link z应增加
正yaw旋转 -> yaw方向与PX4/MAVROS ENU语义一致
```

FAST-LIO yaw 进入 PX4 的方式不是硬覆盖，而是：

```text
FAST-LIO aligned pose quaternion
  -> /uav1/mavros/vision_pose/pose 或 odometry接口
  -> PX4 EKF external vision yaw fusion
  -> /uav1/mavros/local_position/odom
```

也就是说，PX4 EKF融合 yaw，而不是绕过 EKF 强制改飞控姿态。

## 5. 高度与速度策略

当前阶段允许保留 Gazebo Z 作为仿真中的“激光定高替身”进入控制状态源。这个
策略不是任意使用真值作弊，而是对齐真机 Sunray150/云纵机型可挂载定高激光雷达
的工程事实：真机高度可以由独立下视测距传感器约束，不一定完全依赖FAST-LIO高度。

但必须显式标注：

```text
z_source = gazebo_rangefinder_surrogate
```

不能把该结果说成 FAST-LIO全状态定位。

### 5.1 Profile FZ-1：FAST-LIO XY/Yaw + Gazebo Z

首个工程闭环候选：

```text
x, y, yaw:
  FAST-LIO aligned odom

z position:
  Gazebo Z作为定高激光雷达替身

z velocity:
  优先使用 MAVROS local velocity 或 aligned odom中经过验证的vz

roll, pitch:
  使用FAST-LIO aligned quaternion或PX4/MAVROS姿态，按实际EKF融合接口决定
```

用途：

```text
验证FAST-LIO水平定位、yaw和坐标系转换
降低规则柱体环境下高度退化对第一阶段闭环的干扰
对齐真机可使用下视定高激光雷达的工程条件
```

限制：

```text
不能宣称为FAST-LIO全状态定位
不能宣称已经验证真实定高激光雷达驱动和PX4 range aid
必须在结果manifest中写明Gazebo Z作为rangefinder surrogate参与状态源
```

### 5.2 Profile FZ-2：全FAST-LIO XYZ/Yaw

第二个对照候选：

```text
x, y, z, yaw:
  FAST-LIO aligned odom
```

用途：

```text
评估FAST-LIO自身高度是否足够
判断规则柱体环境和MID360视场是否造成Z轴漂移/退化
```

若 FZ-2 与 FZ-1 误差接近，则高度不是主因，应回到控制器或PX4 EKF参数。
若 FZ-2 明显变差，则保留 FZ-1 作为仿真展示/对照策略，并把最终无真值定位作为后续工作。

### 5.3 禁止的混合方式

禁止在没有manifest说明时混用：

```text
FAST-LIO x/y
Gazebo z
MAVROS yaw
PX4 velocity
```

任何混合状态源必须在 `RUN_MANIFEST.json` 中写清：

```text
position_x_source
position_y_source
position_z_source
velocity_source
yaw_source
attitude_source
truth_control_input_allowed
```

### 5.4 FAST-LIO进入PX4的数据字段冻结

FAST-LIO进入飞控的对象不是点云地图，而是经过坐标系、安装位姿和初始对齐后的
外部视觉/里程计观测。

### 5.4.1 数据源能力矩阵

后续不能再按“缺什么补什么”的方式接线。当前链路中每个数据源的职责冻结如下：

| 数据源 | 本地证据/典型Topic | 提供的数据 | 第一阶段消费者 | 是否直接进PX4 EKF |
|---|---|---|---|---|
| MID360原始点云 | `/uav1/livox/lidar` 或FAST-LIO配置的 `lid_topic` | 点云、点时间/扫描信息 | FAST-LIO、planner、RViz | 否 |
| MID360/Livox IMU | `/uav1/livox/imu` 或FAST-LIO配置的 `imu_topic` | 雷达IMU角速度/加速度 | FAST-LIO内部去畸变和LIO估计 | 否 |
| PX4/飞控IMU | `/uav1/mavros/imu/data` | 飞控角速度、姿态相关IMU输出 | PX4 EKF、px4ctrl状态辅助 | 已在PX4内部使用，不由FAST-LIO替换 |
| FAST-LIO `/Odometry` | `camera_init -> body` | LIO位姿、可能的速度/协方差 | FAST-LIO对齐Adapter | 原始不可直接进PX4 |
| FAST-LIO `/cloud_registered` | `camera_init` | 当前帧配准点云 | RViz/诊断 | 否 |
| FAST-LIO `/Laser_map` | `camera_init` | FAST-LIO累计地图 | RViz/地图质量评价 | 否 |
| FAST-LIO `/path` | `camera_init` | FAST-LIO估计轨迹 | RViz/评价 | 否 |
| 对齐后 `/mosim/fastlio/odom_aligned` | `local/map -> base_link` | 飞控中心6DoF位姿、候选速度、质量状态 | PX4 external odom adapter、评价 | 通过门禁后才能进 |
| MAVROS local position | `/uav1/mavros/local_position/odom` | PX4 EKF融合后的本地状态 | px4ctrl控制状态源 | 是PX4输出，不是输入 |

结论：

```text
雷达IMU只喂FAST-LIO。
飞控IMU仍然是PX4 EKF惯性传播来源。
FAST-LIO给PX4的是外部视觉/里程计观测，不是替换飞控IMU。
点云、累计地图、栅格地图、planner轨迹不能直接喂PX4 EKF。
```

### 5.4.2 姿态字段冻结：不能只传yaw

正式工程结论是：不能只传yaw。FAST-LIO对齐后必须形成完整的
`base_link` 位姿：

```text
position:  x, y, z
attitude:  q_world_base = [w, x, y, z]
```

原因：

1. MID360不在飞控中心，且装配有yaw安装角。外参补偿是完整SE(3)问题，不是
   单独yaw偏置问题。
2. 线速度如果要进入PX4 ODOMETRY，必须知道完整姿态，才能判断速度字段属于
   world/local系还是body系，并做正确旋转。
3. PX4 EKF参数层面可以选择只融合外部视觉yaw，但输入消息里的姿态仍必须是
   完整四元数。roll/pitch不能随便置零，否则会把一个物理上错误的传感器姿态
   发给飞控，只是当前EKF可能没有显式融合这两个角而已。
4. RViz中无人机三轴、轨迹中心、FAST-LIO里程计和Gazebo truth的姿态对齐，都
   必须基于完整四元数验证。yaw只是其中一个投影指标。

因此第一阶段姿态策略冻结为：

```text
发送给PX4的消息：
  必须携带完整 q_world_base 四元数

PX4 EKF实际融合：
  由EKF2_EV_CTRL / EKF2_AID_MASK等参数决定，第一阶段至少允许融合yaw

飞控roll/pitch估计：
  仍主要由PX4飞控IMU约束；FAST-LIO roll/pitch先作为外部观测随四元数发送、
  记录和对比，不单独绕过EKF强制覆盖

禁止：
  从FAST-LIO只提取yaw，再拼一个roll=0、pitch=0的假四元数作为正式输入
```

第一阶段必须区分两种接口能力：

| 接口 | 可进入PX4 EKF的核心信息 | 当前定位 |
|---|---|---|
| `/uav1/mavros/vision_pose/pose` | position + quaternion/yaw | pose-only冒烟与保守首跑 |
| `/uav1/mavros/odometry/out` 或 Sunray直接MAVLink ODOMETRY | position + quaternion/yaw + linear velocity + covariance/status能力 | 推荐的正式FAST-LIO闭环候选 |

因此，建议分层冻结为：

```text
必须传给PX4 EKF:
  aligned position x/y
  aligned quaternion / yaw
  timestamp
  frame_id / child_frame_id

FZ-1诊断策略:
  z position 使用Gazebo truth
  z velocity 使用PX4/MAVROS local velocity，或验证后的aligned odom vz

FZ-2正式对照:
  aligned z
  aligned linear velocity vx/vy/vz

必须记录/评估:
  covariance或等效噪声参数
  quality/status
  delay
  drop/frame gap
  FAST-LIO odom rate
```

不传给PX4 EKF、只给规划器/RViz/评价使用：

```text
FAST-LIO累计点云地图
raw MID360 PointCloud2
局部栅格/occupancy
planner path/bspline
```

FAST-LIO/ROS odometry字段处理矩阵：

| 字段/数据 | 是否传给PX4 | 处理原则 |
|---|---|---|
| `header.stamp` | 是 | 使用FAST-LIO测量时间，记录delay；不能一律替换成当前ROS时间 |
| `header.frame_id` | 是 | 输入通常是 `camera_init`，进入PX4前必须转换成PX4可解释的local/world语义 |
| `child_frame_id` | 是 | 输入通常是 `body`，输出应明确为 `base_link` 或 MAVLink FRD body语义 |
| `pose.position` | 是 | 先从Livox/FAST-LIO body转换到飞控中心；FZ-1只用x/y，z用Gazebo诊断值 |
| `pose.orientation` | 是 | 作为yaw/四元数观测进入EKF；必须通过G-FL1确认无90/180度偏差 |
| `twist.linear` | 推荐传 | 正式ODOMETRY闭环传；必须确认世界系/机体系语义，必要时旋转到PX4要求的frame |
| `twist.angular` | 第一阶段不传 | PX4姿态/角速度估计仍由飞控IMU主导；先记录，不进入控制闭环 |
| `pose.covariance` | 推荐传，但需验证 | 本地FAST-LIO源码当前在publish之后才写入pose covariance，不能默认认为订阅帧有效 |
| `twist.covariance` | 推荐补齐 | 若FAST-LIO没有可靠速度协方差，由adapter按实测噪声给保守默认值 |
| `reset_counter` | 推荐补齐 | FAST-LIO重初始化、地图重置或起点重置时递增，避免EKF把跳变当连续运动 |
| `estimator_type` | 推荐补齐 | 使用vision/laser odometry语义，便于日志和飞控侧诊断 |
| `quality/status` | 推荐补齐 | 丢帧、退化、初始化未完成时禁止继续发布有效定位给PX4 |
| `/cloud_registered`、`/Laser_map`、`/path` | 否 | 给建图、规划、RViz和评价使用，不给PX4 EKF |

不应从FAST-LIO替换飞控原始IMU：

```text
PX4 EKF惯性传播仍使用飞控IMU
FAST-LIO内部使用雷达IMU完成自身里程计
FAST-LIO输出作为external vision/odometry观测进入PX4
```

如果发布的是已经转换到飞控中心 `base_link` 的位姿，则 `EKF2_EV_POS_X/Y/Z`
应按“外部观测点已经在机体中心”处理，避免再次把MID360安装偏移写进PX4造成
二次补偿。若改为发布传感器原点位姿，则必须反过来设置PX4的EV位置参数或
MAVROS odometry TF，二者不能同时补偿。

### 5.4.3 Sunray现有external_fusion能力与风险

Sunray当前 `externalFusion/ExternalPosition.h` 已经提供两条外部定位发送路径：

```text
use_vision_pose=true:
  nav_msgs/Odometry 或 PoseStamped
  -> geometry_msgs/PoseStamped
  -> /uav1/mavros/vision_pose/pose

use_vision_pose=false:
  nav_msgs/Odometry 或 PoseStamped
  -> sunray_msgs/ExternalOdom
  -> MAVLink ODOMETRY
```

但不能直接把 `use_vision_pose=false` 当成正式FAST-LIO闭环，因为本地代码还
必须先修正或验证以下点：

| 项目 | 当前风险 | 门禁要求 |
|---|---|---|
| 时间戳 | `mavlink_odom.time_usec` 当前按 `toSec()*1000` 填写，语义上不像微秒 | 明确改成PX4期望的时间单位，并记录measurement time与ROS/Gazebo clock差值 |
| 速度坐标系 | 位置做了ENU->NED转换，但速度字段当前直接赋值 | 确认PX4/MAVLink ODOMETRY期望的速度frame；必要时做ENU->NED或world->body旋转 |
| 协方差 | 当前pose/velocity covariance填NAN | 正式ODOMETRY路径必须给保守协方差，或明确PX4使用EKF2噪声参数替代 |
| 角速度 | rollspeed/pitchspeed/yawspeed为NAN | 第一阶段允许不传，但必须记录“不使用FAST-LIO角速度” |
| frame_id/child_frame_id | 当前直接使用MAVLink frame枚举 | 必须与PX4文档和MAVROS配置一致，确认local/world与body语义 |
| 质量状态 | 只靠Sunray `odom_valid/fusion_success`不足以表达FAST-LIO退化 | Adapter必须输出初始化、丢帧、延迟、跳变、退化状态 |

因此正式实施顺序是：

```text
先用 vision_pose 路径做最小冒烟：
  position + 完整quaternion

再修正/验证 ODOMETRY 路径：
  position + 完整quaternion + linear velocity + covariance/status

ODOMETRY路径未过字段门禁前：
  禁止直接起飞，禁止直接8字，禁止宣称FAST-LIO定位闭环完成
```

## 6. PX4 EKF融合设计

第一阶段控制器仍然是 px4ctrl。`external_fusion`、`vision_pose`、
MAVLink ODOMETRY 都不是 Sunray 原控制器，也不是 px4ctrl 的替代品，它们只属于：

```text
外部定位观测
  -> PX4 EKF
  -> MAVROS local_position
  -> px4ctrl状态输入
```

因此“控制状态源”在本文中只指 px4ctrl 实际读取的状态：

```text
/uav1/mavros/local_position/odom
```

而“定位输入源”指进入PX4 EKF之前的观测，例如：

```text
Gazebo pose / Gazebo rangefinder surrogate
FAST-LIO aligned odom
vision_pose
MAVLink ODOMETRY
```

二者不能混用术语。

第一阶段可以复用或绕开 Sunray `external_fusion`，但不改变控制器归属：
px4ctrl仍是唯一控制器。

保守冒烟接口：

```text
/uav1/mavros/vision_pose/pose
```

该接口适合确认位置、姿态、yaw、坐标系方向和PX4是否开始融合，但不能证明
FAST-LIO速度进入PX4。它对应pose-only路径，Sunray当前 `use_vision_pose=true`
就是这种形式。

正式FAST-LIO定位闭环候选应评估：

```text
/uav1/mavros/odometry/out
```

或使用Sunray现有 `use_vision_pose=false` 时的 MAVLink ODOMETRY 发送路径，
但必须补齐并验证：

```text
position frame语义
orientation frame语义
linear velocity frame语义；若 `child_frame_id=base_link`，twist必须是机体系速度
timestamp
covariance / noise
companion or estimator status
```

第一阶段不直接让 px4ctrl 订阅 FAST-LIO odom。px4ctrl仍然订阅：

```text
/uav1/mavros/local_position/odom
```

这样可以保持：

```text
px4ctrl接口不变
PX4姿态/角速度内环不变
planner输出不变
只替换PX4 EKF外部定位输入
```

PX4 EKF参数必须随版本实测确认。旧PX4常见为 `EKF2_AID_MASK`，
新PX4常见为 `EKF2_EV_CTRL`、`EKF2_HGT_REF`、`EKF2_EV_POS_X/Y/Z`
等。不得只发布 topic 就宣称 PX4 已融合 external vision。

## 7. 执行门禁

### 7.0 FAST-LIO定位问题分层排查矩阵

后续不得再直接从“点云能显示”跳到“FAST-LIO可入控”。所有定位问题按下表逐层
排查；上一层未通过时，下一层禁止执行。

| 层级 | 排查对象 | 主要问题 | 必须记录 | 失败时优先动作 |
|---|---|---|---|---|
| D-FL0 输入源 | `/uav1/livox/lidar`、`/uav1/livox/imu` | 是否是真正装配后的MID360；点云/IMU是否非空、同clock、时间戳单调 | topic类型、frame_id、rate、字段、stamp、代表样本 | 修SDF/plugin/launch/time，不改控制器 |
| D-FL1 FAST-LIO输入格式 | PointCloud2 vs `livox_ros_driver/CustomMsg` | 是否缺少每点时间；是否绕过Livox CustomMsg桥 | 点云字段、CustomMsg字段、FAST-LIO log、sync warning | 优先恢复/验证livox_custom链路，不直接调PID |
| D-FL2 外参与坐标系 | `lidar/imu/body/base_link/world` | 轴向、90/180度yaw、roll/pitch固定偏差、雷达不在飞控中心 | `T_base_livox`、完整四元数、三轴marker、单轴运动方向表 | 修SE(3)变换和frame语义，不只加yaw offset |
| D-FL3 静态定位 | FAST-LIO aligned vs truth，原地不飞或短悬停 | 原地漂移、地图跟飞机走、z/yaw跳变 | 60s漂移、yaw漂移、z漂移、drop/gap | 查时间戳、退化、外参、scan模式 |
| D-FL4 单轴运动 | X/Y/Z/yaw小动作 | X/Y互换、正负号反、尺度错、速度frame错、延迟 | 每轴相关性、符号、比例、delay、速度frame | 修frame和速度转换，禁止8字 |
| D-FL5 独立定位误差 | `/mosim/fastlio/odom_aligned` vs truth | XY/Z/yaw误差是否可控 | RMSE/P95/max、yaw error、delay、rate | 未达标则FAST-LIO只做显示/建图，不入EKF |
| D-FL6 PX4 EKF融合 | FAST-LIO external odom -> MAVROS local position | topic发出但PX4未融合；EKF reject；yaw错 | vision/odometry输入、PX4参数、local_position跟随性、fusion状态 | 修EKF参数/消息字段/协方差/时间戳 |
| D-FL7 闭环控制 | px4ctrl读取MAVROS local position | 定位误差是否被控制器放大 | 起飞悬停降落指标、控制输出、failsafe、落地滑移 | 先回定位/EKF，最后才调控制器 |

当前失败属于 D-FL1 到 D-FL6 未完成时直接进入 D-FL7。后续必须先证明：

```text
FAST-LIO aligned odom 本身对 truth 是稳定的
        ↓
PX4 EKF 确实融合该外部定位
        ↓
MAVROS local_position 跟随融合结果
        ↓
px4ctrl 仍只读取 MAVROS local_position
```

第一阶段禁止路线：

```text
/Odometry 或 /mosim/fastlio/odom_aligned
  -> px4ctrl 直接订阅
  -> 8字/螺旋/EGO
```

第一阶段允许路线：

```text
FAST-LIO并行定位
  -> 独立对比Gazebo/Sunray truth
  -> 通过后作为PX4 external vision / odometry观测
  -> PX4 EKF
  -> /uav1/mavros/local_position/odom
  -> px4ctrl
```

正式闭环中的状态转换、外参补偿、PX4 external odometry发布和质量状态应实现为
C++ ROS节点或可编译组件；Python仅保留为诊断、记录、离线评价和一次性数据整理
脚本。这样后续才能迁移到 Orin NX / 雷迅V6X 真机部署环境。

### G-FL0：静态话题与参数门禁

要求：

```text
/uav1/livox/lidar 非空
/uav1/livox/imu 非空
/Odometry 非空
/mosim/fastlio/odom_aligned 非空
/uav1/mavros/vision_pose/pose 非空
/uav1/mavros/odometry/out 或 Sunray MAVLink ODOMETRY路径能力已判定
/uav1/mavros/local_position/odom 非空
PX4 external vision / yaw / height参数快照已记录
```

同时必须记录字段级样本：

```text
FAST-LIO raw /Odometry:
  stamp
  frame_id
  child_frame_id
  position
  full quaternion
  linear velocity
  covariance是否有效

Adapter /mosim/fastlio/odom_aligned:
  stamp
  frame_id
  child_frame_id
  base_link position
  base_link full quaternion
  roll/pitch/yaw
  velocity frame说明
  mount transform
  initial alignment transform
  quality/status

PX4/MAVROS输出:
  /uav1/mavros/local_position/odom
  /uav1/mavros/imu/data
  EKF external vision参数快照
```

禁止：

```text
无话题数据时继续跑8字
只凭RViz可见点云宣称定位通过
```

### G-FL1：坐标系方向门禁

要求用小运动或短程仿真验证：

```text
forward -> x+
left -> y+
up -> z+
positive yaw -> yaw+
base_link三轴与轨迹中心重合
roll/pitch在静止水平地面时接近0且不出现90/180度固定偏差
四元数归一化，且q和-q等价处理
```

输出：

```text
FAST-LIO aligned vs Gazebo truth 的方向表
初始yaw offset
初始roll/pitch offset
mount transform应用记录
速度frame验证记录
```

若出现以下任一情况，禁止进入G-FL3/G-FL4：

```text
只验证yaw，未验证roll/pitch/full quaternion
三轴marker不在飞控中心轨迹上
速度字段没有说明world/body语义
Sunray ODOMETRY路径时间戳单位未确认
FAST-LIO raw body被当成UAV base_link
```

### G-FL2：FAST-LIO独立定位误差门禁

不进入控制闭环，只比较：

```text
/mosim/fastlio/odom_aligned
vs
/uav1/sunray/gazebo_pose
```

指标：

```text
origin-aligned position RMSE
yaw error
z error
delay
drop/frame gap
LiDAR rate
IMU rate
FAST-LIO odom rate
```

### G-FL3：PX4 EKF融合门禁

启动 external vision 后比较：

```text
/mosim/fastlio/odom_aligned
/uav1/mavros/vision_pose/pose
/uav1/mavros/odometry/out 或 ODOMETRY发送诊断
/uav1/mavros/local_position/pose
/uav1/sunray/gazebo_pose
```

必须证明：

```text
vision pose已发布
若使用ODOMETRY路径，速度字段和frame语义已验证
PX4 local position跟随 external vision
yaw没有90/180度偏差
roll/pitch没有被错误外参注入明显固定偏差
EKF没有持续reject或preflight yaw error
```

G-FL3的核心判断不是“topic发出去了”，而是：

```text
external odom变化
  -> PX4 EKF状态变化
  -> MAVROS local_position变化
  -> px4ctrl仍只看MAVROS local_position
```

如果PX4 local_position没有跟随external odom，说明只是发布成功，不是融合成功。

### G-FL4：起飞悬停降落

第一项闭环任务必须是：

```text
takeoff_hover_land
```

禁止直接上：

```text
8字
螺旋
EGO
EGO-Swarm
```

验收窗口：

```text
steady hover last 8s
XY RMSE <= 0.02m
XY max <= 0.05m
Z RMSE <= 0.02m
Z max <= 0.05m
final disarmed
no post-land sliding
```

若 FZ-1 通过、FZ-2 失败，记录为高度退化/鲁棒性问题。
若 FZ-1 也失败，优先查坐标系、yaw、EKF融合、时间戳，不先调PID。

### G-FL5：基础控制任务重跑

在 G-FL4 通过后，按顺序重跑：

```text
8字
螺旋
step_x
step_y
step_z
```

每项输出：

```text
reference path
actual path
time-sync RMSE/P95/max
nearest-path RMSE/P95/max
hover窗口误差
landing slip
yaw final error
```

### G-FL6：EGO系列重跑

G-FL5 通过后，重跑：

```text
EGO
EGO-Planner-v2
Diff-Planner
```

此时 planner 输入不再使用 Gazebo/PX4辅助定位状态作为默认解释，必须写明：

```text
pointcloud_to_world pose source
occupancy/grid source
planner odom source
controller state source
FAST-LIO是否进入PX4 EKF
Z策略是FZ-1还是FZ-2
```

### G-FL7：EGO-Swarm

单机全部通过后才进入：

```text
EGO-Swarm 2机
EGO-Swarm 3机
```

第一阶段只做官方规划链路加工程接入，不做自研编队控制：

```text
每机PX4实例隔离
每机MAVROS实例隔离
每机FAST-LIO/状态源隔离
每机planner topic隔离
无碰撞
轨迹不冲突
```

## 8. 当前下一步

立即执行顺序：

```text
1. 固化 fastlio_odom_alignment_adapter 输出manifest字段。
2. 实现/确认 FZ-1：FAST-LIO aligned x/y/yaw + Gazebo truth z。
3. 静态运行 G-FL0/G-FL1，不飞或短飞，确认坐标轴和yaw。
4. 跑 G-FL2 独立定位误差。
5. 跑 G-FL3 PX4 EKF融合检查。
6. 跑 G-FL4 起飞悬停降落。
7. 通过后再跑8字、螺旋、阶跃。
8. 最后重跑 EGO、EGOv2、Diff-Planner、EGO-Swarm。
```

如果任何一步发现：

```text
yaw偏90/180度
vision pose未被PX4融合
FAST-LIO aligned和truth方向不一致
post-land仍滑行
hover误差明显超过基准
```

则停止后续planner复现，先修定位/状态源。

## 9. 答辩表述边界

正确表述：

```text
MoSim先用Gazebo truth支撑的PX4 local state跑通控制器和planner工程链路；
随后切换为FAST-LIO对齐后进入PX4 EKF的定位闭环，并对比Gazebo truth评价误差。
```

不能表述：

```text
此前EGO/EGOv2/Diff-Planner已经完成FAST-LIO定位闭环
栅格地图来自FAST-LIO累计地图
MAVROS local position就是FAST-LIO定位
Gazebo truth完全没有参与状态源
```

最终目标表述：

```text
MID360/FAST-LIO提供定位与建图基础，EGO系列规划器基于点云/栅格地图生成轨迹，
px4ctrl/MWorks生成控制器通过统一接口跟踪轨迹，PX4/Gazebo完成飞控闭环验证。
```

## 10. 调研依据与当前代码风险清单

### 10.1 本地源码依据

FAST-LIO本地源码：

```text
References/Lab/FAST_LIO/src/laserMapping.cpp
```

已确认：

```text
输入:
  common/lid_topic
  common/imu_topic

输出:
  /cloud_registered
  /cloud_registered_body
  /Laser_map
  /Odometry
  /path

/Odometry:
  header.frame_id = camera_init
  child_frame_id = body
```

因此 `/Odometry` 是FAST-LIO body在 `camera_init` 中的估计，不是飞控中心。

Sunray外部定位源码：

```text
References/Sunray/General_Module/sunray_uav_control/externalFusion/ExternalPosition.h
```

已确认：

```text
OdomCallback:
  读取position
  读取linear velocity
  读取完整orientation quaternion
  计算roll/pitch/yaw

use_vision_pose=true:
  发布 /uav1/mavros/vision_pose/pose
  只带position + full quaternion

use_vision_pose=false:
  生成MAVLink ODOMETRY
  带position + full quaternion + linear velocity
  rollspeed/pitchspeed/yawspeed为NAN
  covariance为NAN
```

当前不能直接复用的风险：

```text
MAVLink ODOMETRY timestamp单位需要修正/验证
MAVLink ODOMETRY velocity坐标系需要修正/验证
covariance不能长期保持NAN而不声明PX4噪声参数来源
FAST-LIO raw body不能绕过mount transform直接发给PX4
```

### 10.2 官方资料依据

PX4 external vision / MAVROS路线要求重点：

```text
/mavros/vision_pose/pose:
  对应外部视觉pose路径，适合pose-only冒烟

/mavros/odometry/out:
  对应ODOMETRY路径，可以带pose、orientation、linear velocity等完整里程计信息

MAVROS odometry:
  frame_id / child_frame_id 和 TF需要能解释到PX4使用的odom_ned / base_link_frd语义

PX4 EKF:
  external vision可配置水平位置、垂直位置、速度、yaw等融合项
  协方差可从MAVLink ODOMETRY来，也可由EKF参数提供
```

FAST-LIO官方说明重点：

```text
FAST-LIO是LiDAR-Inertial Odometry，融合LiDAR点和IMU数据，输出实时里程计和地图。
这说明雷达IMU属于FAST-LIO内部估计输入，不等于PX4飞控IMU替代源。
```

### 10.3 第一阶段最终决策

当前阶段的正确闭环不是：

```text
FAST-LIO yaw
  -> 强制覆盖PX4 yaw
```

而是：

```text
MID360 point cloud + MID360/Livox IMU
  -> FAST-LIO
  -> raw camera_init/body odom
  -> mount transform + initial alignment
  -> base_link full pose, optional velocity, covariance/status
  -> PX4 external vision / ODOMETRY fusion
  -> MAVROS local_position
  -> px4ctrl
```

第一阶段最低可飞Profile：

```text
vision_pose冒烟:
  base_link position
  base_link full quaternion
  timestamp
  quality gate
```

正式Profile：

```text
ODOMETRY:
  base_link position
  base_link full quaternion
  linear velocity with verified frame
  covariance/noise source
  reset/status/quality
```

roll/pitch是否“融合”由PX4 EKF参数和实现决定，但roll/pitch对应的完整四元数必须
被正确计算、发送、记录和对比；不能把姿态降级成yaw-only。
