# MoSim规划与编队控制接口规范

> 文档编号：MoSim-CTRL-05
> 文档名称：MoSim规划与编队控制接口规范
> 适用项目：MoSim四旋翼多领域建模、控制与联合仿真平台
> 当前版本：V0.1 Draft
> 依赖文档：
>
> * MoSim-CTRL-01《MoSim控制体系总览》
> * MoSim-CTRL-02《MoSim统一控制接口规范》
> * MoSim-CTRL-03《MoSim单机控制器实现规范》
> * MoSim-CTRL-04《MoSim控制增强与容错规范》
>
> 后续关联文档：
>
> * MoSim-CTRL-06《MoSim控制器管理与配置规范》
> * MoSim-CTRL-07《MoSim控制器代码生成与PX4部署规范》
> * MoSim-CTRL-08《MoSim控制系统测试与评价规范》

---

# 0. 当前阶段规划与编队边界

EGO 与 EGO-Swarm 当前只作为官方规划链路和 MoSim 工程接入基线，不作为自研编队控制成果。

当前允许：

```text
EGO单机官方链路
EGO-Swarm 2机官方Demo
EGO-Swarm 3机官方Demo
EGO-Swarm经Trajectory Adapter、px4ctrl、MAVROS、PX4、Gazebo的MoSim工程接入
MWORKS版px4ctrl_core替换原始core后重复EGO单机链路
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

轨迹服务器硬规则：

```text
EGO可以约10~20Hz或事件触发重规划。
控制器和Trajectory Server按100Hz运行。
Trajectory Server必须对带时间参数的轨迹函数或B样条求值。
不得把EGO的20Hz离散位置点简单线性插值为100Hz控制命令。
```

---

# 1. 文档目的

本文档规定MoSim中任务管理、轨迹规划、编队控制、多机通信、轨迹执行、安全过滤和单机控制器之间的接口及职责边界。

主要解决以下问题：

```text
EGO、Fast-Planner、SUPER等规划器怎样统一接入
编队控制和多机避碰分别由谁负责
规划器输出怎样转换为控制器输入
B样条、多项式和离散轨迹怎样统一表达
轨迹重新规划时怎样平滑切换
单机与多机系统怎样共享同一套接口
规划器失败、通信中断和成员故障时怎样处理
ROS 1、Gazebo、MAVROS和PX4之间怎样连接
```

本文档不规定具体控制器的控制律，也不要求将所有规划器重写为MWORKS模块。

---

# 2. 核心设计原则

## 2.1 规划器不等于控制器

规划器回答：

```text
无人机接下来应该沿什么轨迹飞
```

控制器回答：

```text
为了跟踪该轨迹，现在需要什么姿态、推力或力矩
```

标准链路：

```text
地图、障碍物和任务目标
          ↓
规划器
          ↓
连续时间轨迹
          ↓
轨迹服务器
          ↓
p、v、a、jerk、snap、yaw
          ↓
单机控制器
          ↓
姿态、角速度、推力或力矩
```

规划器不得直接发布：

```text
电机PWM
单电机转速
单电机推力
PX4执行器命令
```

---

## 2.2 编队控制不等于多机规划

编队控制负责：

```text
队形结构
成员相对位置
编队质心运动
速度一致性
队形切换
领航关系
```

多机规划负责：

```text
障碍物避让
无人机之间的轨迹防碰撞
动力学可行轨迹生成
局部重新规划
```

推荐链路：

```text
编队任务
   ↓
编队控制器
生成每架无人机的名义目标或队形约束
   ↓
多机规划器
生成可行、无碰撞轨迹
   ↓
单机轨迹控制器
```

不得简单使用：

```text
编队控制器输出位置
          ↓
直接发送电机命令
```

---

## 2.3 原生算法通过适配器接入

外部规划器保留其原生实现。

```text
EGO Planner
Fast-Planner
SUPER
GCOPTER
Primitive-Planner
Swarm-Formation
```

统一通过：

```text
Planner Adapter
```

转换为MoSim接口。

不得在初期为了统一接口而重写规划算法。

---

## 2.4 规划轨迹和执行参考分离

规划器输出低频连续轨迹：

```text
5～30 Hz重新规划
```

轨迹服务器高频求值：

```text
50～200 Hz生成控制参考
```

单机控制器只读取当前参考点或参考时域，不直接解析各规划器内部数据结构。

---

## 2.5 统一世界坐标与时间

MoSim规划和编队核心统一使用：

```text
世界坐标：ENU
机体坐标：FLU
单位：SI
时间：统一仿真时间或单调系统时间
```

外部规划器、MAVROS和PX4的坐标转换只能在适配层完成。

---

# 3. 系统总体架构

```text
用户任务 / 测试场景 / 前端
              ↓
┌─────────────────────────────┐
│ Mission Manager             │
│ 航点、目标、任务阶段         │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Formation Manager           │
│ 队形、槽位、成员和拓扑       │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Planner Manager             │
│ 规划器选择、调度和恢复       │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Planner Adapter             │
│ EGO / FAST / SUPER / GCOPTER│
└─────────────────────────────┘
              ↓
候选连续轨迹
              ↓
┌─────────────────────────────┐
│ Trajectory Validator        │
│ 动力学、碰撞和连续性检查     │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Trajectory Server           │
│ 激活、拼接、采样和时域输出   │
└─────────────────────────────┘
              ↓
TrajectoryReference / Horizon
              ↓
┌─────────────────────────────┐
│ Safety Filter               │
│ CBF、限幅、机间安全距离      │
└─────────────────────────────┘
              ↓
单机控制器
              ↓
PX4 / Gazebo / MWORKS动力学
```

---

# 4. 模块职责划分

## 4.1 Mission Manager

负责：

```text
任务创建
任务开始、暂停和取消
航点序列
目标区域
任务阶段切换
返航和降落任务
单机与多机任务分发
```

不负责：

```text
局部避障
队形误差反馈
电机控制
```

---

## 4.2 Formation Manager

负责：

```text
队形定义
成员分配
领航机定义
拓扑管理
队形缩放
队形旋转
队形切换
故障成员退出
新成员加入
```

---

## 4.3 Planner Manager

负责：

```text
规划器注册
规划器选择
规划请求管理
规划超时
候选轨迹仲裁
重新规划
规划器回退
运行状态监控
```

---

## 4.4 Planner Adapter

负责：

```text
MoSim消息转换为规划器原生消息
规划器原生轨迹转换为MoSim轨迹
坐标转换
时间转换
参数转换
原生错误状态映射
```

---

## 4.5 Trajectory Validator

负责检查：

```text
轨迹是否有限
时间是否单调
起点是否匹配
速度是否超限
加速度是否超限
jerk是否超限
推力需求是否可达
轨迹是否碰撞
机间距离是否满足
```

---

## 4.6 Trajectory Server

负责：

```text
保存当前有效轨迹
切换新轨迹
连续时间轨迹求值
发布当前参考点
发布预测时域
处理轨迹结束
轨迹超时
安全保持轨迹
```

---

## 4.7 Safety Filter

负责：

```text
最终机间防碰撞
障碍物安全距离
速度和加速度安全约束
地理围栏
控制能力限制
```

安全过滤器只修正必要部分，不重新承担完整局部规划。

---

# 5. 运行模式

MoSim规划体系支持以下模式。

## 5.1 MANUAL_REFERENCE

不运行在线规划器。

```text
轨迹发生器
→ 圆形、8字、螺旋、Minimum-Snap
→ 控制器
```

用于控制器标准测试。

---

## 5.2 SINGLE_POINT_TO_POINT

单机从当前位置规划到目标点。

---

## 5.3 SINGLE_WAYPOINT_MISSION

依次执行多个航点。

---

## 5.4 SINGLE_REPLAN

使用局部地图持续重新规划。

---

## 5.5 FORMATION_REFERENCE

只生成队形参考，不进行障碍物规划。

适合空旷环境编队控制测试。

---

## 5.6 FORMATION_PLANNING

编队约束和障碍物规划联合运行。

---

## 5.7 DECENTRALIZED_SWARM

每架无人机独立规划，并交换邻机状态或轨迹。

---

## 5.8 CENTRALIZED_SWARM

中央规划器统一生成所有无人机轨迹。

---

## 5.9 EMERGENCY_HOLD

停止任务，生成安全悬停或减速轨迹。

---

## 5.10 EMERGENCY_LAND

规划安全下降和着陆轨迹。

---

# 6. 核心接口分类

MoSim定义以下规划与编队接口：

```text
MissionRequest
MissionStatus
GoalReference
WaypointSequence

PlannerInput
PlannerRequest
PlannerCapability
PlannerStatus

FormationSpecification
FormationCommand
FormationAssignment
FormationReference
FormationStatus

NeighborState
NeighborTrajectory
CommunicationStatus

ExecutableTrajectory
TrajectoryMetadata
TrajectoryValidationResult
TrajectoryExecutionStatus
```

---

# 7. 通用标识

每条规划和编队消息必须包含：

```text
vehicle_id
swarm_id
mission_id
formation_id
trajectory_id
segment_id
source_id
sequence
sample_time_us
valid_until_us
```

禁止仅依赖ROS节点名或命名空间识别无人机。

---

# 8. MissionRequest接口

```cpp
enum class MissionType : uint8_t {
    NONE = 0,
    HOLD,
    TAKEOFF,
    LAND,
    POINT_TO_POINT,
    WAYPOINT_SEQUENCE,
    PATROL,
    FORMATION_NAVIGATION,
    AREA_COVERAGE,
    RETURN_HOME,
    EMERGENCY_LAND
};

struct MissionRequest {
    MessageHeader header;

    uint32_t mission_id;
    MissionType type;

    uint32_t vehicle_count;
    std::array<uint32_t, MOSIM_MAX_VEHICLES> vehicle_ids;

    uint32_t waypoint_count;
    std::array<Waypoint, MOSIM_MAX_WAYPOINTS> waypoints;

    bool loop;
    bool allow_replan;
    bool allow_formation_reconfiguration;

    double mission_timeout_s;
};
```

---

# 9. Waypoint接口

```cpp
struct Waypoint {
    Vector3 position_enu_m;

    double yaw_enu_rad;
    double acceptance_radius_m;
    double desired_speed_mps;

    double hold_time_s;

    uint32_t action_flags;
};
```

`acceptance_radius_m`只用于任务完成判断，不得直接作为控制误差容限。

---

# 10. GoalReference接口

```cpp
struct GoalReference {
    MessageHeader header;

    uint32_t mission_id;
    uint32_t goal_id;

    Vector3 position_enu_m;
    Vector3 velocity_enu_mps;

    double yaw_enu_rad;
    double yaw_rate_radps;

    double position_tolerance_m;
    double velocity_tolerance_mps;

    bool stop_at_goal;
};
```

---

# 11. PlannerInput接口

```cpp
struct PlannerInput {
    TimeUs planning_time_us;

    uint32_t vehicle_id;
    uint32_t mission_id;

    VehicleState current_state;
    GoalReference goal;

    VehicleLimits nominal_limits;
    VehicleLimits available_limits;

    const MapHandle* map;
    const DynamicObstacleSet* dynamic_obstacles;

    const FormationReference* formation_reference;
    const NeighborSet* neighbors;

    const ExecutableTrajectory* current_trajectory;

    PlannerConstraintSet constraints;
};
```

---

# 12. 名义能力和可用能力

规划器必须区分：

```text
nominal_limits
available_limits
```

`nominal_limits`表示设计能力。

`available_limits`表示当前实际可用能力，可能受到：

```text
低电量
电机效率下降
载荷增加
控制器降级
风扰
故障
```

影响。

规划器必须优先使用`available_limits`。

---

# 13. 地图接口

地图不通过普通高频消息完整复制。

使用：

```cpp
struct MapHandle {
    uint32_t map_id;
    uint32_t map_version;

    CoordinateFrame frame;

    double resolution_m;

    MapType type;

    const void* backend_handle;
};
```

支持：

```text
占据栅格
ESDF
TSDF
点云地图
ROG-Map
OctoMap
自定义体素地图
```

控制器不得直接读取地图。

---

# 14. 地图状态

```cpp
struct MapStatus {
    MessageHeader header;

    uint32_t map_id;
    uint32_t map_version;

    bool initialized;
    bool local_region_valid;
    bool global_region_valid;

    Vector3 local_min_enu_m;
    Vector3 local_max_enu_m;

    TimeUs last_update_us;
};
```

---

# 15. 动态障碍物接口

```cpp
struct DynamicObstacle {
    uint32_t obstacle_id;

    Vector3 position_enu_m;
    Vector3 velocity_enu_mps;
    Vector3 acceleration_enu_mps2;

    Vector3 size_m;

    Matrix3 position_covariance;
    Matrix3 velocity_covariance;

    TimeUs prediction_start_us;
    double prediction_duration_s;
};

struct DynamicObstacleSet {
    MessageHeader header;

    uint32_t count;
    std::array<DynamicObstacle,
               MOSIM_MAX_DYNAMIC_OBSTACLES> obstacles;
};
```

---

# 16. PlannerRequest

```cpp
enum class PlannerRequestType : uint8_t {
    PLAN_NEW = 0,
    REPLAN,
    EXTEND,
    STOP,
    HOLD,
    RETURN_HOME,
    EMERGENCY
};

struct PlannerRequest {
    MessageHeader header;

    PlannerRequestType type;

    uint32_t mission_id;
    uint32_t request_id;

    GoalReference goal;

    TimeUs desired_start_time_us;
    double maximum_planning_time_s;

    bool require_collision_free;
    bool require_dynamic_feasibility;
    bool require_formation_consistency;
};
```

---

# 17. PlannerCapability

```cpp
enum class TrajectoryRepresentation : uint32_t {
    NONE               = 0,
    BSPLINE            = 1U << 0,
    PIECEWISE_POLYNOMIAL = 1U << 1,
    SAMPLED            = 1U << 2,
    MOTION_PRIMITIVE   = 1U << 3
};

struct PlannerCapability {
    const char* planner_name;
    const char* planner_version;

    bool supports_single_agent;
    bool supports_multi_agent;
    bool supports_dynamic_obstacles;
    bool supports_unknown_environment;
    bool supports_formation_constraints;
    bool supports_replanning;

    uint32_t supported_trajectory_types;

    double nominal_planning_rate_hz;
    double maximum_planning_time_s;

    uint32_t maximum_vehicle_count;
};
```

---

# 18. Planner状态机

```cpp
enum class PlannerLifecycleState : uint8_t {
    UNCONFIGURED = 0,
    WAITING_FOR_STATE,
    WAITING_FOR_MAP,
    WAITING_FOR_GOAL,
    READY,
    PLANNING,
    TRAJECTORY_READY,
    EXECUTING,
    REPLANNING,
    HOLDING,
    RECOVERING,
    FAILED,
    STOPPED
};
```

标准流程：

```text
WAITING_FOR_STATE
        ↓
WAITING_FOR_MAP
        ↓
WAITING_FOR_GOAL
        ↓
READY
        ↓
PLANNING
        ↓
TRAJECTORY_READY
        ↓
EXECUTING
        ↓
REPLANNING
```

---

# 19. PlannerResult

```cpp
enum class PlannerResult : int32_t {
    OK = 0,

    NOT_CONFIGURED,
    STATE_UNAVAILABLE,
    STATE_STALE,
    MAP_UNAVAILABLE,
    MAP_STALE,
    GOAL_INVALID,

    START_IN_COLLISION,
    GOAL_IN_COLLISION,
    PATH_NOT_FOUND,
    OPTIMIZATION_FAILED,
    TRAJECTORY_INFEASIBLE,
    TRAJECTORY_COLLISION,

    NEIGHBOR_DATA_STALE,
    FORMATION_INFEASIBLE,

    PLANNING_TIMEOUT,
    CANCELLED,
    INTERNAL_ERROR
};
```

---

# 20. PlannerStatus

```cpp
struct PlannerStatus {
    MessageHeader header;

    uint32_t planner_id;
    uint32_t mission_id;
    uint32_t request_id;

    PlannerLifecycleState lifecycle;
    PlannerResult result;

    double planning_time_ms;
    double trajectory_duration_s;
    double trajectory_length_m;

    double minimum_obstacle_distance_m;
    double minimum_agent_distance_m;

    uint32_t replan_count;
    uint32_t failed_plan_count;
};
```

---

# 21. 队形定义

## 21.1 FormationSpecification

```cpp
enum class FormationType : uint8_t {
    CUSTOM = 0,
    LINE,
    COLUMN,
    V_SHAPE,
    TRIANGLE,
    SQUARE,
    CIRCLE,
    HEXAGON,
    GRID,
    CUBE
};

struct FormationSlot {
    uint32_t slot_id;

    Vector3 offset_flu_m;

    double preferred_yaw_offset_rad;
    uint32_t role_flags;
};

struct FormationSpecification {
    MessageHeader header;

    uint32_t formation_id;
    FormationType type;

    uint32_t slot_count;
    std::array<FormationSlot,
               MOSIM_MAX_VEHICLES> slots;

    double scale;
    bool rotate_with_heading;
    bool allow_deformation;
};
```

---

# 22. 队形参考系

队形槽位可以相对于以下参考系定义：

```text
FORMATION_HEADING_FRAME
LEADER_BODY_FRAME
WORLD_ENU
PATH_TANGENT_FRAME
```

推荐默认：

```text
FORMATION_HEADING_FRAME
```

其中：

```text
X轴：编队前进方向
Y轴：编队左侧
Z轴：上方
```

---

# 23. FormationCommand

```cpp
struct FormationCommand {
    MessageHeader header;

    uint32_t formation_id;

    Vector3 centroid_position_enu_m;
    Vector3 centroid_velocity_enu_mps;
    Vector3 centroid_acceleration_enu_mps2;

    double heading_enu_rad;
    double heading_rate_radps;

    double scale;

    bool preserve_shape;
    bool allow_reconfiguration;
};
```

---

# 24. FormationAssignment

```cpp
struct FormationAssignment {
    MessageHeader header;

    uint32_t formation_id;

    uint32_t member_count;

    std::array<uint32_t,
               MOSIM_MAX_VEHICLES> vehicle_ids;

    std::array<uint32_t,
               MOSIM_MAX_VEHICLES> slot_ids;

    uint32_t leader_vehicle_id;
};
```

成员和槽位必须显式绑定，不得默认：

```text
vehicle_id == slot_id
```

---

# 25. FormationReference

每架无人机最终接收单独的名义参考。

```cpp
struct FormationReference {
    MessageHeader header;

    uint32_t formation_id;
    uint32_t slot_id;

    Vector3 nominal_position_enu_m;
    Vector3 nominal_velocity_enu_mps;
    Vector3 nominal_acceleration_enu_mps2;

    double nominal_yaw_enu_rad;
    double nominal_yaw_rate_radps;

    double position_weight;
    double shape_weight;

    bool deformation_allowed;
};
```

---

# 26. 编队拓扑

```cpp
struct FormationEdge {
    uint32_t source_vehicle_id;
    uint32_t target_vehicle_id;

    double position_weight;
    double velocity_weight;

    Vector3 desired_relative_position_m;
};

struct FormationTopology {
    MessageHeader header;

    uint32_t topology_id;

    uint32_t edge_count;
    std::array<FormationEdge,
               MOSIM_MAX_FORMATION_EDGES> edges;

    bool directed;
    bool time_varying;
};
```

支持：

```text
全连接
链式
环形
星形
树形
有向图
时变拓扑
```

---

# 27. NeighborState

```cpp
struct NeighborState {
    MessageHeader header;

    uint32_t vehicle_id;

    Vector3 position_enu_m;
    Vector3 velocity_enu_mps;
    Vector3 acceleration_enu_mps2;

    Quaternion attitude_enu_flu;

    double position_uncertainty_m;
    double clock_uncertainty_s;

    bool healthy;
};
```

---

# 28. NeighborTrajectory

```cpp
struct NeighborTrajectory {
    MessageHeader header;

    uint32_t vehicle_id;
    uint32_t trajectory_id;

    TrajectoryRepresentation representation;

    TimeUs start_time_us;
    double duration_s;

    SharedTrajectoryData trajectory;
};
```

邻机轨迹必须携带：

```text
开始时间
持续时间
轨迹ID
更新时间
有效期
```

不得只广播若干无时间语义的位置点。

---

# 29. NeighborSet

```cpp
struct NeighborSet {
    MessageHeader header;

    uint32_t count;

    std::array<NeighborState,
               MOSIM_MAX_NEIGHBORS> states;

    std::array<NeighborTrajectory,
               MOSIM_MAX_NEIGHBORS> trajectories;
};
```

---

# 30. 通信状态

```cpp
struct CommunicationStatus {
    MessageHeader header;

    uint32_t peer_vehicle_id;

    double latency_s;
    double packet_loss_ratio;
    double update_rate_hz;

    TimeUs last_state_receive_us;
    TimeUs last_trajectory_receive_us;

    bool synchronized;
    bool connection_healthy;
};
```

---

# 31. 轨迹表达体系

MoSim支持三种主要连续轨迹和一种离散轨迹：

```text
B样条轨迹
分段多项式轨迹
运动基元轨迹
采样轨迹
```

控制器不直接区分其来源。

---

# 32. BSplineTrajectory

```cpp
struct BSplineTrajectory {
    uint32_t degree;
    uint32_t control_point_count;
    uint32_t knot_count;

    std::array<Vector3,
               MOSIM_MAX_CONTROL_POINTS> position_control_points;

    std::array<double,
               MOSIM_MAX_KNOTS> knots;

    bool has_yaw_spline;

    std::array<double,
               MOSIM_MAX_CONTROL_POINTS> yaw_control_points;
};
```

要求：

```text
节点序列非递减
控制点数量合法
阶数合法
轨迹时间范围明确
```

---

# 33. PolynomialTrajectory

```cpp
struct PolynomialSegment {
    double duration_s;

    uint32_t order;

    std::array<double,
               MOSIM_MAX_POLY_COEFF> coeff_x;

    std::array<double,
               MOSIM_MAX_POLY_COEFF> coeff_y;

    std::array<double,
               MOSIM_MAX_POLY_COEFF> coeff_z;

    std::array<double,
               MOSIM_MAX_POLY_COEFF> coeff_yaw;
};

struct PolynomialTrajectory {
    uint32_t segment_count;

    std::array<PolynomialSegment,
               MOSIM_MAX_SEGMENTS> segments;
};
```

---

# 34. MotionPrimitiveTrajectory

```cpp
struct MotionPrimitive {
    uint32_t primitive_id;

    TimeUs start_time_us;
    double duration_s;

    Vector3 initial_position_m;
    Vector3 initial_velocity_mps;

    Vector3 control_input;
};

struct MotionPrimitiveTrajectory {
    uint32_t count;

    std::array<MotionPrimitive,
               MOSIM_MAX_PRIMITIVES> primitives;
};
```

---

# 35. SampledTrajectory

```cpp
struct SampledTrajectory {
    uint32_t count;
    double nominal_dt_s;

    std::array<TrajectoryPoint,
               MOSIM_MAX_TRAJECTORY_POINTS> points;
};
```

采样轨迹适合：

```text
日志回放
外部黑盒规划器
简单规划器
跨进程通用传输
```

但高阶导数精度通常不如连续表达。

---

# 36. ExecutableTrajectory

```cpp
struct ExecutableTrajectory {
    MessageHeader header;

    uint32_t mission_id;
    uint32_t trajectory_id;

    TrajectoryRepresentation representation;

    TimeUs start_time_us;
    TimeUs end_time_us;

    double duration_s;

    TrajectoryMetadata metadata;

    union {
        BSplineTrajectory bspline;
        PolynomialTrajectory polynomial;
        MotionPrimitiveTrajectory primitive;
        SampledTrajectory sampled;
    };
};
```

若生成工具不适合使用`union`，可以改为固定字段加有效位。

---

# 37. TrajectoryMetadata

```cpp
struct TrajectoryMetadata {
    uint32_t planner_id;
    uint32_t planner_version;

    uint32_t map_version;

    double maximum_velocity_mps;
    double maximum_acceleration_mps2;
    double maximum_jerk_mps3;

    double minimum_obstacle_distance_m;
    double minimum_agent_distance_m;

    double trajectory_cost;

    bool collision_checked;
    bool dynamic_feasibility_checked;
    bool formation_checked;
};
```

---

# 38. 轨迹服务器接口

```cpp
class ITrajectoryEvaluator {
public:
    virtual bool configure(
        const ExecutableTrajectory& trajectory) = 0;

    virtual bool evaluate(
        TimeUs time_us,
        TrajectoryPoint& point) const = 0;

    virtual bool evaluateHorizon(
        TimeUs time_us,
        double horizon_dt_s,
        uint32_t count,
        ReferenceHorizon& horizon) const = 0;

    virtual bool finished(
        TimeUs time_us) const = 0;
};
```

---

# 39. 轨迹求值输出

Trajectory Server向控制器发布：

```text
TrajectoryPoint
ReferenceHorizon
TrajectoryExecutionStatus
```

标准Topic：

```text
/mosim/uav<N>/reference/trajectory
/mosim/uav<N>/reference/horizon
/mosim/uav<N>/trajectory/status
```

---

# 40. 轨迹激活机制

新轨迹不得发布后立即无条件覆盖旧轨迹。

标准流程：

```text
规划器生成候选轨迹
        ↓
Trajectory Validator检查
        ↓
Controller Manager确认控制能力
        ↓
分配activation_time
        ↓
Trajectory Server预加载
        ↓
到达activation_time
        ↓
原子切换
```

---

# 41. 双阶段轨迹提交

## 阶段一：PREPARE

检查：

```text
轨迹格式
起点一致性
轨迹连续性
动力学约束
碰撞
执行器能力
控制器能力
```

## 阶段二：ACTIVATE

只有所有模块确认后，轨迹才成为当前执行轨迹。

---

# 42. 轨迹起点匹配

新轨迹起点必须与预计切换时刻状态匹配。

检查：

```text
位置差
速度差
加速度差
航向差
航向角速度差
```

若超出门槛：

```text
重新规划
生成过渡段
延迟切换
拒绝轨迹
```

---

# 43. 连续性要求

根据控制器类型要求：

| 控制器        | 最低参考连续性 |
| ---------- | ------- |
| PX4原生位置控制  | C1      |
| PID / LQR  | C1或C2   |
| SE(3)      | C2      |
| DFBC-Jerk  | C3      |
| DFBC-Full  | C4      |
| MPC / NMPC | 取决于预测模型 |

定义：

```text
C0：位置连续
C1：速度连续
C2：加速度连续
C3：jerk连续
C4：snap连续
```

---

# 44. 轨迹拼接

轨迹拼接方法包括：

```text
直接连续拼接
过渡多项式
Minimum-Jerk过渡
Minimum-Snap过渡
旧轨迹短时延伸
紧急减速轨迹
```

禁止通过跳变参考点完成重规划切换。

---

# 45. 轨迹结束处理

轨迹结束后可执行：

```text
保持末端位置
保持末端速度
切换下一段
切换悬停
请求新规划
降落
```

行为必须由任务Profile明确配置。

---

# 46. TrajectoryValidationResult

```cpp
enum class TrajectoryRejectReason : uint32_t {
    NONE                 = 0,
    INVALID_TIME         = 1U << 0,
    NON_FINITE           = 1U << 1,
    START_MISMATCH       = 1U << 2,
    VELOCITY_LIMIT       = 1U << 3,
    ACCELERATION_LIMIT   = 1U << 4,
    JERK_LIMIT           = 1U << 5,
    THRUST_LIMIT         = 1U << 6,
    COLLISION            = 1U << 7,
    AGENT_COLLISION      = 1U << 8,
    FORMATION_VIOLATION  = 1U << 9
};

struct TrajectoryValidationResult {
    MessageHeader header;

    bool accepted;

    uint32_t reject_flags;

    double maximum_velocity_mps;
    double maximum_acceleration_mps2;
    double maximum_jerk_mps3;

    double minimum_obstacle_distance_m;
    double minimum_agent_distance_m;

    TimeUs accepted_start_time_us;
};
```

---

# 47. 轨迹动力学检查

至少检查：

```text
最大速度
最大加速度
最大jerk
最大snap
最大倾角需求
最大总推力需求
最小总推力需求
最大角速度估计
单电机推力可达性
```

轨迹标称满足速度和加速度限制，并不一定代表电机推力可达。

---

# 48. 碰撞检查责任

## 规划器

负责生成碰撞风险较低的候选轨迹。

## Trajectory Validator

负责独立检查候选轨迹。

## Safety Filter

负责处理执行过程中出现的新风险。

## Gazebo碰撞系统

负责记录实际碰撞结果。

不得只依赖规划器自身返回的“成功”标志。

---

# 49. 安全距离

定义：

```text
d_vehicle
d_obstacle
d_agent
d_emergency
```

其中：

```text
d_emergency < d_agent
```

当距离低于：

```text
d_agent
```

触发安全过滤。

当低于：

```text
d_emergency
```

触发紧急避碰或制动。

---

# 50. CBF安全过滤接口

```cpp
struct SafetyFilterInput {
    VehicleState current_state;
    TrajectoryPoint nominal_reference;

    NeighborSet neighbors;
    DynamicObstacleSet obstacles;

    VehicleLimits limits;
};

struct SafetyFilterOutput {
    TrajectoryPoint safe_reference;

    bool modified;
    uint32_t active_constraint_count;

    double minimum_safety_margin;
};
```

安全过滤器输出应尽可能接近名义参考，不得无原因大幅改变任务轨迹。

---

# 51. 编队控制和安全过滤冲突

优先级：

```text
飞行稳定
   >
机间和障碍物安全
   >
执行器约束
   >
队形保持
   >
航向美观
```

安全过滤器可以暂时破坏队形。

风险解除后，Formation Manager负责平滑恢复队形。

---

# 52. 重新规划触发条件

标准触发条件：

```text
新任务
新目标
当前轨迹接近结束
地图发生重要变化
轨迹检测到碰撞
动态障碍物进入预测区域
邻机轨迹冲突
跟踪误差过大
控制器能力下降
执行器故障
队形发生变化
通信拓扑变化
规划器主动请求
```

---

# 53. 跟踪误差触发

控制器向规划器提供：

```cpp
struct TrackingPerformance {
    MessageHeader header;

    double position_error_m;
    double velocity_error_mps;
    double attitude_error_rad;

    double thrust_saturation_ratio;
    double actuator_saturation_ratio;

    bool controller_degraded;
    bool trajectory_untrackable;
};
```

当轨迹无法跟踪时，规划器应：

```text
降低速度
降低加速度
增加避障距离
缩短规划时域
重新规划
```

而不是继续发送同一条不可执行轨迹。

---

# 54. 控制能力反馈

```cpp
struct ControlCapabilityFeedback {
    MessageHeader header;

    VehicleLimits currently_available_limits;

    double control_quality;
    double tracking_quality;

    bool nominal_control_available;
    bool aggressive_flight_available;
    bool yaw_control_degraded;
};
```

故障容错控制器可以通过该接口通知规划器：

```text
当前只能低速飞行
当前Yaw不可控
当前需要尽快降落
```

---

# 55. 规划失败处理

单次失败：

```text
继续执行当前安全轨迹
缩短目标距离
调整规划参数
重新规划
```

连续失败：

```text
减速
进入悬停
尝试备用规划器
返航
安全降落
```

禁止规划失败后继续使用已经过期或存在碰撞的轨迹。

---

# 56. 备用规划器

建议Planner Manager支持：

```text
PRIMARY_PLANNER
SECONDARY_PLANNER
HOLD_PLANNER
EMERGENCY_PLANNER
```

示例：

```text
主规划器：EGO
备用规划器：Fast-Planner
保持规划器：Minimum-Jerk停止轨迹
紧急规划器：垂直减速与悬停
```

---

# 57. 规划器切换

切换流程：

```text
检测当前规划器失败
        ↓
保存当前轨迹
        ↓
初始化备用规划器
        ↓
传入当前状态和剩余任务
        ↓
生成候选轨迹
        ↓
Validator检查
        ↓
平滑切换
```

规划器切换不得直接清空当前安全轨迹。

---

# 58. 编队控制模式

## 58.1 虚拟结构

Formation Manager生成：

```text
编队质心
编队航向
每个槽位相对偏移
```

---

## 58.2 Leader-Follower

跟随机参考由：

```text
领航机状态
相对位置
相对速度
```

生成。

---

## 58.3 一致性控制

使用邻接拓扑生成名义速度或加速度参考。

---

## 58.4 分布式MPC编队

每架无人机预测：

```text
自身未来轨迹
邻机未来轨迹
队形误差
碰撞约束
```

---

## 58.5 联合编队轨迹优化

队形、障碍物和动力学约束在同一轨迹优化中处理。

---

# 59. 队形变形

支持：

```text
缩放
旋转
平移
压缩
拉伸
平面队形转三维队形
狭窄通道重构
```

变形过程必须时间参数化，不允许瞬时修改所有槽位。

---

# 60. 队形切换接口

```cpp
struct FormationTransition {
    MessageHeader header;

    uint32_t source_formation_id;
    uint32_t target_formation_id;

    TimeUs start_time_us;
    double duration_s;

    TransitionMethod method;

    bool preserve_centroid;
    bool preserve_leader;
};
```

---

# 61. 成员加入和退出

成员状态：

```cpp
enum class SwarmMemberState : uint8_t {
    UNKNOWN = 0,
    JOINING,
    ACTIVE,
    DEGRADED,
    LEAVING,
    FAILED,
    REMOVED
};
```

成员退出后必须：

```text
更新FormationAssignment
更新FormationTopology
更新邻机列表
重新分配槽位
重新规划
```

---

# 62. 领航机失效

处理顺序：

```text
检测领航机失效
      ↓
冻结或减速编队参考
      ↓
选择新领航机
      ↓
更新拓扑
      ↓
重新分配队形参考
      ↓
重新规划
```

---

# 63. 故障成员隔离

故障无人机如果仍可控：

```text
退出队形
降低速度
飞往安全点
降落
```

其他成员：

```text
扩大安全距离
重构队形
重新分配任务
```

---

# 64. 分布式系统时间同步

多机轨迹必须基于可比较的时间轴。

每架无人机记录：

```text
本地单调时间
仿真时间
时钟偏移
时钟不确定度
```

若时间同步质量不足：

```text
扩大机间安全距离
降低速度
使用状态外推
降低邻机轨迹可信度
```

---

# 65. 坐标系对齐

多机系统必须明确：

```text
所有无人机是否共享同一map_enu
是否各自使用独立odom_enu
各odom到map的变换
变换更新时间和协方差
```

编队规划不得直接比较两个未对齐`odom`坐标中的位置。

---

# 66. 无全局坐标模式

若多机没有统一全局坐标，可采用：

```text
相对位置
相对速度
相对观测
局部一致性
```

此时必须标记：

```text
global_frame_available = false
```

并禁止使用依赖全局绝对位置的编队模式。

---

# 67. 通信丢失处理

邻机数据超时分级：

```text
轻微超时：
状态外推

中度超时：
扩大安全半径并降低速度

严重超时：
将邻机视为不确定动态障碍物

完全失联：
悬停、退出编队或执行预设策略
```

---

# 68. ROS 1命名空间

单机：

```text
/mosim/uav0/
```

多机：

```text
/mosim/uav0/
/mosim/uav1/
/mosim/uav2/
```

集群公共命名空间：

```text
/mosim/swarm/
```

任务公共命名空间：

```text
/mosim/mission/
```

---

# 69. ROS 1推荐Topic

## 69.1 任务Topic

```text
/mosim/mission/request
/mosim/mission/status
/mosim/mission/waypoints
```

## 69.2 编队Topic

```text
/mosim/swarm/formation/specification
/mosim/swarm/formation/command
/mosim/swarm/formation/assignment
/mosim/swarm/formation/topology
/mosim/swarm/formation/status
```

## 69.3 单机规划Topic

```text
/mosim/uav<N>/planner/request
/mosim/uav<N>/planner/status
/mosim/uav<N>/planner/candidate_trajectory
```

## 69.4 轨迹执行Topic

```text
/mosim/uav<N>/trajectory/accepted
/mosim/uav<N>/trajectory/active
/mosim/uav<N>/trajectory/status

/mosim/uav<N>/reference/trajectory
/mosim/uav<N>/reference/horizon
```

## 69.5 邻机Topic

```text
/mosim/swarm/agent_state
/mosim/swarm/agent_trajectory
/mosim/swarm/communication_status
```

---

# 70. ROS Service和Action

适合Service的操作：

```text
加载规划器
重置规划器
清空地图
查询规划器能力
```

适合Action的操作：

```text
执行点到点任务
执行航点任务
执行编队任务
队形切换
返航
降落
```

长时间任务不得仅通过同步Service阻塞执行。

---

# 71. 原生规划器Topic隔离

外部规划器原生Topic放入：

```text
/mosim_adapter/<planner_name>/...
```

例如：

```text
/mosim_adapter/ego/...
/mosim_adapter/fast/...
/mosim_adapter/super/...
```

MoSim其他模块不得直接依赖这些Topic。

---

# 72. EGO Adapter

职责：

```text
输入当前里程计
输入目标点
输入局部地图
输入邻机轨迹
接收原生B样条轨迹
转换为ExecutableTrajectory
映射规划状态
```

单机模式：

```text
只启用本机规划
```

多机模式：

```text
交换带时间信息的邻机轨迹
```

EGO Adapter不得承担编队槽位生成。

---

# 73. Fast-Planner Adapter

职责：

```text
提供状态和目标
提供深度图或点云及位姿
连接地图和ESDF模块
接收B样条轨迹
转换轨迹元数据
```

Fast-Planner既可以使用自己的地图模块，也可以通过适配层读取MoSim地图服务。

---

# 74. SUPER Adapter

职责：

```text
输入当前状态
输入目标
输入点云或地图
接收安全走廊和轨迹结果
转换为MoSim连续轨迹
记录重规划和轨迹质量信息
```

SUPER应作为独立ROS进程运行，不进入PX4飞控板。

---

# 75. GCOPTER Adapter

GCOPTER主要作为轨迹优化后端。

其上游应提供：

```text
航点
安全走廊
起点状态
终点状态
动力学约束
```

输出转换为：

```text
PolynomialTrajectory
```

---

# 76. Primitive-Planner Adapter

用于大规模集群。

职责：

```text
载入运动基元库
输入集群任务
输入邻机信息
输出运动基元序列
转换为ExecutableTrajectory
```

规划器的运动基元库版本必须记录在TrajectoryMetadata中。

---

# 77. Swarm-Formation Adapter

用于联合队形与轨迹优化。

其输出仍必须经过：

```text
Trajectory Validator
Trajectory Server
```

不得因规划器内部已经检查队形和碰撞而绕过统一验证。

---

# 78. 学习式规划器接口

保留：

```text
DiffusionPlannerAdapter
LearningPlannerAdapter
```

学习式规划器必须额外输出：

```text
模型版本
训练数据版本
置信度
推理时间
安全验证状态
```

学习式轨迹未经Validator验证不得执行。

---

# 79. 规划器与MWORKS边界

MWORKS适合：

```text
基础轨迹发生
编队控制律
一致性控制
分布式MPC验证
任务状态机建模
规划器输入输出回放
```

大型地图、点云和复杂开源规划器优先作为ROS 1进程运行。

标准链路：

```text
MWORKS编队控制器
      ↓
FormationReference
      ↓
ROS规划器
      ↓
ExecutableTrajectory
      ↓
MWORKS或PX4单机控制器
```

---

# 80. 规划器与PX4边界

规划器默认运行在伴随计算机。

PX4只接收：

```text
位置、速度和加速度参考
姿态和推力参考
角速度和推力参考
```

标准模式一：

```text
规划器
→ Trajectory Server
→ MAVROS位置、速度、加速度设定值
→ PX4原生控制器
```

标准模式二：

```text
规划器
→ Trajectory Server
→ px4ctrl / SE3 / DFBC / MPC
→ 姿态或角速度设定值
→ PX4内环
```

标准模式三：

```text
规划器
→ Trajectory Server
→ PX4内部MoSim控制器Module
→ PX4剩余控制链
```

---

# 81. 禁止规划器直接发布MAVROS控制Topic

以下结构禁止作为正式架构：

```text
EGO节点
直接发布/mavros/setpoint_raw/attitude
```

正确结构：

```text
EGO
→ EGO Adapter
→ MoSim ExecutableTrajectory
→ Trajectory Server
→ Controller Manager
→ MAVROS或PX4 Module
```

这样才能统一：

```text
控制器切换
日志
安全检查
故障回退
前端管理
```

---

# 82. Offboard健康管理

ROS 1—PX4适配器负责：

```text
持续发送有效设定值或心跳
检测PX4连接
检测Offboard状态
检测解锁状态
处理模式退出
处理设定值超时
```

规划器自身不得管理PX4解锁和飞行模式。

---

# 83. 参数体系

规划参数分为：

```text
通用参数
规划器专用参数
编队参数
安全参数
通信参数
执行参数
```

---

# 84. 通用规划参数

```text
规划频率
最大规划时间
规划时域
地图安全边界
目标容差
最大速度
最大加速度
最大jerk
轨迹切换提前时间
```

---

# 85. 编队参数

```text
编队类型
编队尺度
成员数量
领航机
相对位置
拓扑权重
队形误差权重
重构时间
```

---

# 86. 安全参数

```text
障碍物安全距离
机间安全距离
紧急安全距离
通信失联安全距离
最大预测不确定度
CBF权重
```

---

# 87. Planner Profile

示例：

```yaml
profile:
  id: "ego_swarm_dfbc"

mission:
  mode: "formation_navigation"

formation:
  controller: "virtual_structure"
  shape: "v_shape"
  scale: 2.0

planner:
  primary: "ego_swarm"
  fallback: "hold_planner"
  replanning_rate_hz: 10

trajectory:
  representation: "bspline"
  output_rate_hz: 100
  continuity_required: "C3"

limits:
  max_velocity_mps: 5.0
  max_acceleration_mps2: 6.0
  max_jerk_mps3: 12.0

safety:
  obstacle_distance_m: 0.6
  agent_distance_m: 1.2
  emergency_distance_m: 0.7

controller:
  profile: "dfbc_indi"
```

---

# 88. 日志要求

每次规划记录：

```text
规划请求
起点状态
目标
地图版本
邻机数据版本
规划器名称和版本
规划开始和结束时间
规划结果
候选轨迹
验证结果
轨迹激活时间
重新规划原因
失败原因
```

---

# 89. 多机日志

额外记录：

```text
编队规格
成员分配
拓扑
邻机状态
邻机轨迹
通信延迟
丢包率
队形误差
最小机间距离
成员加入和退出事件
```

---

# 90. 错误码分组

```text
0x1xxx 任务错误
0x2xxx 地图错误
0x3xxx 规划错误
0x4xxx 轨迹错误
0x5xxx 编队错误
0x6xxx 通信错误
0x7xxx 安全错误
0x8xxx 适配器错误
```

示例：

```text
MOS_PLAN_E_NO_STATE
MOS_PLAN_E_NO_MAP
MOS_PLAN_E_NO_PATH
MOS_PLAN_E_TIMEOUT
MOS_TRAJ_E_COLLISION
MOS_TRAJ_E_INFEASIBLE
MOS_FORM_E_ASSIGN
MOS_FORM_E_TOPOLOGY
MOS_COMM_E_TIMEOUT
```

---

# 91. 推荐代码目录

```text
MoSim/
├── Planning/
│   ├── interfaces/
│   │   ├── mission/
│   │   ├── planner/
│   │   ├── trajectory/
│   │   ├── formation/
│   │   └── communication/
│   │
│   ├── mission_manager/
│   ├── planner_manager/
│   ├── trajectory_server/
│   ├── trajectory_validator/
│   ├── safety_filter/
│   │
│   ├── adapters/
│   │   ├── ego/
│   │   ├── fast_planner/
│   │   ├── super/
│   │   ├── gcopter/
│   │   ├── primitive_planner/
│   │   └── swarm_formation/
│   │
│   ├── trajectory/
│   │   ├── bspline/
│   │   ├── polynomial/
│   │   ├── primitive/
│   │   ├── sampled/
│   │   └── stitching/
│   │
│   └── tests/
│
├── Formation/
│   ├── virtual_structure/
│   ├── leader_follower/
│   ├── consensus/
│   ├── dmpc/
│   ├── assignment/
│   ├── topology/
│   └── reconfiguration/
│
├── Msg/
│   └── ros1/
│
└── Config/
    ├── missions/
    ├── planners/
    ├── formations/
    └── planning_profiles/
```

---

# 92. ROS消息包目录

```text
mosim_msgs/
└── msg/
    ├── MissionRequest.msg
    ├── MissionStatus.msg
    ├── GoalReference.msg
    ├── PlannerRequest.msg
    ├── PlannerStatus.msg
    ├── ExecutableTrajectory.msg
    ├── BSplineTrajectory.msg
    ├── PolynomialTrajectory.msg
    ├── SampledTrajectory.msg
    ├── FormationSpecification.msg
    ├── FormationCommand.msg
    ├── FormationAssignment.msg
    ├── FormationReference.msg
    ├── FormationTopology.msg
    ├── NeighborState.msg
    ├── NeighborTrajectory.msg
    └── CommunicationStatus.msg
```

---

# 93. 首版实施范围

V1.0实现：

```text
基础轨迹发生器
EGO-Swarm Adapter
Fast-Planner Adapter
Trajectory Server
Trajectory Validator
Mission Manager
虚拟结构编队
Leader-Follower编队
一致性编队
邻机状态和轨迹接口
ROS 1命名空间
MAVROS/PX4输出适配
```

V1.0轨迹格式：

```text
B样条
分段多项式
采样轨迹
```

---

# 94. 第二阶段实施范围

```text
SUPER Adapter
GCOPTER Adapter
Primitive-Planner Adapter
Swarm-Formation Adapter
CBF安全过滤
编队重构
故障成员退出
领航机重选
通信延迟补偿
```

---

# 95. 接口验收测试

至少验证：

```text
规划器切换
轨迹格式转换
B样条求值
多项式求值
轨迹拼接
轨迹超时
规划失败回退
地图版本变化
邻机轨迹超时
队形切换
成员退出
通信丢包
控制能力下降重新规划
```

---

# 96. 规划闭环验收

统一测试链：

```text
目标和地图
   ↓
规划器
   ↓
ExecutableTrajectory
   ↓
Trajectory Validator
   ↓
Trajectory Server
   ↓
单机控制器
   ↓
Gazebo / PX4
   ↓
状态反馈
   ↓
重新规划
```

必须确认该链路中不存在规划器直接绕过MoSim接口控制PX4的路径。

---

# 97. 编队闭环验收

```text
FormationCommand
      ↓
Formation Manager
      ↓
每机FormationReference
      ↓
多机规划
      ↓
每机ExecutableTrajectory
      ↓
每机Trajectory Server
      ↓
每机单机控制器
      ↓
Gazebo多机动力学
      ↓
邻机状态和轨迹反馈
```

---

# 98. 强制性规则

1. 规划器和控制器必须通过统一轨迹接口连接。

2. 编队控制器只生成名义参考或约束，不直接控制电机。

3. 外部规划器必须通过独立Adapter接入。

4. 规划器原生消息不得传播到MoSim其他模块。

5. 所有规划轨迹必须经过Trajectory Validator。

6. 所有新轨迹必须通过准备和激活两个阶段切换。

7. 重规划时必须保证规定阶数的连续性。

8. Planner Manager必须保留当前安全轨迹，直到新轨迹被接受。

9. 规划失败不得继续执行已知碰撞轨迹。

10. 轨迹服务器统一负责高频参考点和预测时域输出。

11. 规划器不得直接发布电机、力矩或PX4执行器命令。

12. 规划器不得自行解锁PX4或控制飞行模式。

13. 编队参考、邻机状态和邻机轨迹必须携带时间戳和车辆ID。

14. 不同无人机的坐标必须在比较前完成坐标对齐。

15. 通信超时后必须扩大安全约束或进入降级模式。

16. 队形保持的优先级低于碰撞安全和飞行稳定。

17. 控制器必须向规划器反馈当前可用动力学能力。

18. 故障发生后必须更新规划器使用的速度、加速度和推力限制。

19. 学习式规划器的输出必须经过传统安全检查。

20. 规划器源码、版本、参数和许可证必须纳入实验记录。

---

# 99. 最终结论

MoSim规划与编队系统不应采用：

```text
每个规划器直接连接不同控制器
每个规划器使用自己的轨迹消息
EGO直接发MAVROS
编队控制器直接修改电机命令
多机之间只交换无时间戳位置
规划失败后继续使用旧危险轨迹
```

应采用：

```text
任务层
   ↓
编队参考层
   ↓
统一Planner Manager
   ↓
规划器Adapter
   ↓
统一ExecutableTrajectory
   ↓
Trajectory Validator
   ↓
Trajectory Server
   ↓
安全过滤器
   ↓
统一单机控制接口
   ↓
PX4 / Gazebo / MWORKS
```

最终实现：

```text
规划器可替换
编队算法可替换
控制器可替换
轨迹表达可扩展
多机数量可扩展
故障和降级可管理
ROS与PX4接口可统一
实验结果可复现
```

从而使EGO、Fast-Planner、SUPER、Primitive-Planner等开源规划系统，以及虚拟结构、一致性、Leader-Follower、分布式MPC等编队算法，都能够通过同一套MoSim接口与单机控制器、Gazebo仿真和PX4部署链路稳定连接。
