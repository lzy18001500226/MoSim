# MoSim统一控制接口规范

> 文档编号：MoSim-CTRL-02
> 文档名称：MoSim统一控制接口规范
> 适用项目：MoSim四旋翼多领域建模、控制与联合仿真平台
> 当前版本：V0.1 Draft
> 依赖文档：MoSim-CTRL-01《MoSim控制体系总览》
> 后续文档：
>
> * MoSim-CTRL-03《MoSim单机控制器实现规范》
> * MoSim-CTRL-04《MoSim控制增强与容错规范》
> * MoSim-CTRL-05《MoSim规划与编队控制接口规范》
> * MoSim-CTRL-06《MoSim控制器管理与配置规范》
> * MoSim-CTRL-07《MoSim控制器代码生成与PX4部署规范》
> * MoSim-CTRL-08《MoSim控制系统测试与评价规范》

---

# 0. 当前阶段接口冻结

当前第一阶段只实现 `ATTITUDE_THRUST` 实际链路。

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

当前 MWORKS 控制器核心输入固定为：

```text
position
velocity
attitude
angular_velocity
position_reference
velocity_reference
acceleration_reference
yaw_reference
yaw_rate_reference（可选）
mass
gravity
dt
reset
enable
```

当前输出固定为：

```text
desired_attitude_quaternion
desired_collective_thrust_N
controller_status
controller_diagnostics
```

硬规则：

```text
MWORKS输出物理总推力N。
MWORKS不直接输出MAVROS 0~1归一化油门。
归一化推力映射属于公共ATTITUDE_THRUST Adapter。
BODY_RATE_THRUST、WRENCH、ROTOR_THRUST、ROTOR_SPEED只保留枚举和未来规划，不建立第一阶段实际Adapter。
```

---

# 1. 文档目的

本文档定义MoSim控制系统中各模块之间的统一数据接口、坐标系、单位、时间同步、有效性判断、控制输出层级、异常处理和适配规则。

该规范的目标是保证同一套控制算法核心可以在以下环境中复用：

```text
MWORKS.Sysplorer / Sysblock模型仿真
ROS 1外部控制节点
Gazebo联合仿真
PX4 SITL
PX4飞控板载Module
硬件在环HITL
真实四旋翼飞行平台
```

本文档不规定PID、SE(3)、MPC、NMPC等控制器的具体算法，而是规定所有控制器必须遵循的输入、输出和运行契约。

---

# 2. 总体设计目标

MoSim统一控制接口应满足以下目标：

## 2.1 算法与运行环境解耦

控制算法核心不得直接依赖：

```text
ROS消息类型
MAVROS消息类型
PX4 uORB结构体
Gazebo插件类型
MWORKS图形模型端口类型
操作系统接口
网络通信接口
```

算法核心只允许依赖MoSim定义的标准数据结构。

ROS、PX4、Gazebo和MWORKS分别通过适配器完成数据转换。

---

## 2.2 同一算法多后端运行

同一控制器算法应尽可能保持同一份核心代码：

```text
                    ┌─ MWORKS Block Adapter
                    │
Controller Core ────┼─ ROS 1 Node Adapter
                    │
                    ├─ PX4 uORB Module Adapter
                    │
                    └─ Unit Test / Offline Replay
```

不得分别维护“MWORKS版PID”“ROS版PID”和“PX4版PID”三套彼此独立的算法代码。

---

## 2.3 控制层级可替换

MoSim必须支持以下控制接管层级：

```text
位置参考
加速度参考
姿态 + 推力
角速度 + 推力
力矩 + 推力
单旋翼推力
电机转速
```

不同控制器可以选择不同的输出层级。

例如：

```text
PX4原生控制器
轨迹参考 → PX4位置、速度、姿态和角速度控制器

px4ctrl类控制器
轨迹参考 → 姿态 + 总推力 → PX4姿态和角速度控制器

DFBC
轨迹参考 → 角速度 + 总推力 → PX4角速度控制器

完整NMPC
状态与参考轨迹 → 单旋翼推力 → 控制分配以下层级
```

---

## 2.4 坐标、单位和符号唯一

所有接口必须明确规定：

```text
坐标系
参考系
单位
正方向
四元数顺序
时间基准
有效性
归一化方式
```

禁止通过函数名、变量名或使用习惯隐式推断。

---

## 2.5 实时与嵌入式兼容

控制算法单周期执行函数必须满足：

```text
不进行文件读写
不进行网络通信
不执行阻塞操作
不在实时循环内动态申请内存
不抛出未捕获异常
不依赖非确定性线程调度
具有明确的最大执行时间
```

---

# 3. 系统边界

MoSim控制接口位于规划、状态估计、控制算法、控制增强、控制分配和执行器模型之间。

```text
任务与场景层
      ↓
轨迹发生器 / 在线规划器
      ↓
TrajectoryReference / ReferenceHorizon
      ↓
编队控制 / 安全过滤
      ↓
ControllerInput
      ↓
单机控制器
      ↓
ControllerCommand
      ↓
INDI / L1 / AWFF / DOB
      ↓
姿态与角速度内环
      ↓
控制分配
      ↓
ActuatorCommand
      ↓
PX4 / Gazebo / MWORKS动力学模型
```

---

# 4. 接口分层

MoSim控制系统定义五类核心接口。

## 4.1 参考接口

描述无人机应当到达的状态：

```text
TrajectoryPoint
ReferenceHorizon
TrajectorySegment
FormationReference
```

## 4.2 状态接口

描述无人机当前估计状态：

```text
VehicleState
ActuatorState
BatteryState
EstimatorStatus
```

## 4.3 模型接口

描述控制器所使用的模型与约束：

```text
VehicleModel
ActuatorModel
VehicleLimits
EnvironmentModel
```

## 4.4 控制输出接口

描述控制器计算出的控制命令：

```text
ControllerCommand
ActuatorCommand
```

## 4.5 状态与诊断接口

描述控制器自身状态：

```text
ControllerStatus
ControllerCapability
ControllerDiagnostics
```

---

# 5. MoSim标准坐标系

## 5.1 总体原则

MoSim算法核心统一采用：

```text
世界坐标系：ENU
机体坐标系：FLU
```

PX4适配器负责完成：

```text
ENU ↔ NED
FLU ↔ FRD
```

采用该方案的原因是：

```text
ROS 1和Gazebo通常采用ENU/FLU
多数规划器输出ENU轨迹
MWORKS模型更适合使用Z轴向上的惯性系
PX4 uORB内部采用NED/FRD
```

所有坐标转换只能在适配层完成。

控制器核心内部不得同时混用ENU和NED。

---

## 5.2 世界坐标系

### 5.2.1 map_enu

```text
X：East，向东
Y：North，向北
Z：Up，向上
```

用于：

```text
全局地图
任务航点
规划器轨迹
编队目标
长期一致的局部世界坐标
```

### 5.2.2 odom_enu

```text
X：East
Y：North
Z：Up
```

用于：

```text
连续局部定位
视觉里程计
激光里程计
Gazebo真值
控制器当前状态
```

`odom_enu`应保持连续，不应因全局定位修正产生瞬时跳变。

### 5.2.3 world_enu

仿真系统的统一惯性坐标系。

在单地图、单局部场景中可以令：

```text
world_enu = map_enu = odom_enu
```

但接口中仍保留不同的frame标识。

---

## 5.3 机体坐标系

### 5.3.1 base_link_flu

```text
X：Forward，机头前方
Y：Left，机体左侧
Z：Up，机体上方
```

MoSim控制器核心中的：

```text
角速度
角加速度
机体系力
机体系力矩
电机安装位置
```

默认均使用FLU机体系。

### 5.3.2 base_link_frd

PX4机体系：

```text
X：Forward
Y：Right
Z：Down
```

只允许在PX4适配器、日志转换器和接口调试工具中使用。

---

## 5.4 ENU和NED转换

向量从ENU转换到NED：

[
\begin{bmatrix}
x_N\
y_E\
z_D
\end{bmatrix}
=============

\begin{bmatrix}
0&1&0\
1&0&0\
0&0&-1
\end{bmatrix}
\begin{bmatrix}
x_E\
y_N\
z_U
\end{bmatrix}
]

定义：

```cpp
C_NED_ENU =
[
    0, 1,  0,
    1, 0,  0,
    0, 0, -1
];
```

即：

```text
x_ned =  y_enu
y_ned =  x_enu
z_ned = -z_enu
```

---

## 5.5 FLU和FRD转换

```cpp
C_FRD_FLU =
[
    1,  0,  0,
    0, -1,  0,
    0,  0, -1
];
```

即：

```text
x_frd =  x_flu
y_frd = -y_flu
z_frd = -z_flu
```

角速度、角加速度、力和力矩均按照向量方式转换。

---

## 5.6 姿态转换

MoSim统一使用旋转矩阵：

[
R_{ENU}^{FLU}
]

表示将FLU机体系向量转换到ENU世界坐标系。

转换到PX4使用的姿态：

[
R_{NED}^{FRD}
=============

C_{NED\leftarrow ENU}
R_{ENU}^{FLU}
C_{FLU\leftarrow FRD}
]

禁止通过简单交换四元数分量完成ENU/NED或FLU/FRD转换。

所有四元数转换必须经过经过验证的坐标转换函数。

---

## 5.7 航向角定义

MoSim航向角采用ENU定义：

```text
yaw = 0：机头指向East
yaw正方向：从East向North逆时针旋转
单位：rad
范围：[-π, π)
```

转换到NED航向：

[
\psi_{ned}
==========

\frac{\pi}{2}-\psi_{enu}
]

转换后必须执行角度归一化。

---

# 6. 单位规范

MoSim算法核心统一采用SI单位。

| 物理量  | 单位     |
| ---- | ------ |
| 位置   | m      |
| 速度   | m/s    |
| 加速度  | m/s²   |
| jerk | m/s³   |
| snap | m/s⁴   |
| 角度   | rad    |
| 角速度  | rad/s  |
| 角加速度 | rad/s² |
| 质量   | kg     |
| 惯量   | kg·m²  |
| 力    | N      |
| 力矩   | N·m    |
| 电机转速 | rad/s  |
| 时间   | s或μs   |
| 电压   | V      |
| 电流   | A      |
| 功率   | W      |

禁止在算法核心中使用：

```text
角度制deg
rpm
厘米cm
毫秒整数作为动力学dt
归一化油门代替真实推力
```

适配器可以处理外部单位转换，但进入控制器核心前必须转换为SI单位。

---

# 7. 四元数规范

MoSim四元数采用Hamilton约定：

```text
q = [w, x, y, z]
```

定义：

```cpp
struct Quaternion {
    double w;
    double x;
    double y;
    double z;
};
```

四元数表示机体系到世界系的主动旋转。

要求：

```text
模长必须接近1
输入控制器前必须归一化
不得包含NaN或Inf
相邻周期保持符号连续
```

由于：

[
q和-q
]

表示同一姿态，因此适配器应执行：

```cpp
if (dot(q_current, q_previous) < 0.0) {
    q_current = -q_current;
}
```

防止日志、微分和控制误差出现跳变。

---

# 8. 时间规范

## 8.1 时间类型

统一定义：

```cpp
using TimeUs = uint64_t;
```

单位为微秒。

每个动态数据结构至少包含：

```cpp
TimeUs sample_time_us;
TimeUs publish_time_us;
uint32_t sequence;
```

其中：

* `sample_time_us`：该数据所表示状态的实际采样时刻；
* `publish_time_us`：该消息被发布或写入接口的时刻；
* `sequence`：单调递增序号。

控制器必须以`sample_time_us`计算状态时间。

---

## 8.2 时间源

不同运行环境使用：

| 环境       | 时间源                         |
| -------- | --------------------------- |
| MWORKS   | 仿真求解器时间                     |
| Gazebo   | `/clock`仿真时间                |
| ROS 1    | `ros::Time`，启用仿真时使用`/clock` |
| PX4 SITL | PX4单调高分辨率时间                 |
| PX4真机    | 飞控单调高分辨率时间                  |
| 离线回放     | 日志记录时间                      |

禁止使用系统日历时间参与控制计算。

---

## 8.3 时间单调性

控制器要求：

```text
sample_time_us单调递增
dt > 0
dt处于配置范围内
```

若出现：

```text
时间回退
时间跳跃
dt过大
仿真重新开始
日志循环回放
```

控制器必须执行软复位或完全复位。

---

## 8.4 控制周期

每个控制器必须声明：

```cpp
double nominal_period_s;
double minimum_period_s;
double maximum_period_s;
```

推荐默认运行频率：

| 控制层      |       推荐频率 |
| -------- | ---------: |
| 在线规划器    |   10～30 Hz |
| 参考轨迹求值   |  50～100 Hz |
| 位置/速度外环  |  50～100 Hz |
| 姿态控制     | 100～250 Hz |
| 角速度控制    | 250～500 Hz |
| 电机与执行器控制 |  500 Hz及以上 |

最终频率由控制器、求解器和飞控板算力配置决定。

---

# 9. 数据有效性规范

## 9.1 禁止使用NaN表示内部字段缺失

MoSim算法核心使用显式有效位：

```cpp
uint64_t valid_mask;
```

例如：

```cpp
enum TrajectoryField : uint64_t {
    REF_POSITION          = 1ULL << 0,
    REF_VELOCITY          = 1ULL << 1,
    REF_ACCELERATION      = 1ULL << 2,
    REF_JERK              = 1ULL << 3,
    REF_SNAP              = 1ULL << 4,
    REF_YAW               = 1ULL << 5,
    REF_YAW_RATE          = 1ULL << 6,
    REF_YAW_ACCELERATION  = 1ULL << 7
};
```

NaN只允许在PX4或MAVLink适配器中作为外部协议语义使用。

---

## 9.2 有效性检查

进入控制器前必须检查：

```text
字段有效位
数值是否有限
四元数是否合法
时间戳是否过期
frame是否正确
单位版本是否一致
数据序号是否回退
```

---

## 9.3 数据超时

建议采用周期相关超时：

```cpp
state_timeout =
    max(3 * state_nominal_period, configured_min_timeout);

reference_timeout =
    max(5 * reference_nominal_period, configured_min_timeout);
```

推荐默认值：

| 数据      |   默认超时 |
| ------- | -----: |
| 姿态和角速度  |  20 ms |
| 位置和速度状态 |  50 ms |
| 执行器反馈   | 100 ms |
| 轨迹参考点   | 200 ms |
| 编队邻机状态  | 300 ms |
| 健康状态    | 500 ms |

实际值由运行Profile覆盖。

---

# 10. 通用头部结构

所有MoSim运行时数据使用统一头部。

```cpp
enum class CoordinateFrame : uint8_t {
    UNKNOWN = 0,
    WORLD_ENU,
    MAP_ENU,
    ODOM_ENU,
    BODY_FLU,
    WORLD_NED,
    BODY_FRD
};

struct MessageHeader {
    uint16_t interface_major;
    uint16_t interface_minor;

    uint32_t vehicle_id;
    uint32_t source_id;
    uint32_t sequence;

    TimeUs sample_time_us;
    TimeUs publish_time_us;
    TimeUs valid_until_us;

    CoordinateFrame frame;
    uint64_t valid_mask;
};
```

---

# 11. 轨迹参考接口

## 11.1 TrajectoryPoint

```cpp
struct TrajectoryPoint {
    MessageHeader header;

    Vector3 position_enu_m;
    Vector3 velocity_enu_mps;
    Vector3 acceleration_enu_mps2;
    Vector3 jerk_enu_mps3;
    Vector3 snap_enu_mps4;

    double yaw_enu_rad;
    double yaw_rate_radps;
    double yaw_acceleration_radps2;

    uint32_t trajectory_id;
    uint32_t segment_id;
};
```

---

## 11.2 字段语义

### position

期望位置：

```text
frame：MAP_ENU或ODOM_ENU
单位：m
```

### velocity

期望世界系线速度：

```text
frame：与position一致
单位：m/s
```

### acceleration

不含重力的期望运动学加速度：

```text
悬停时 acceleration = [0, 0, 0]
```

重力补偿由控制器或公共动力学模块统一完成。

禁止部分控制器认为`acceleration.z`包含重力，另一些控制器认为不包含重力。

### jerk和snap

分别为位置的三阶和四阶导数：

```text
jerk：m/s³
snap：m/s⁴
```

用于DFBC、微分平坦控制和前馈控制。

---

## 11.3 ReferenceHorizon

MPC、NMPC和预测型控制器需要未来参考轨迹。

```cpp
constexpr size_t MOSIM_MAX_HORIZON = 64;

struct ReferenceHorizon {
    MessageHeader header;

    uint32_t trajectory_id;
    uint32_t count;

    double nominal_dt_s;

    std::array<TrajectoryPoint, MOSIM_MAX_HORIZON> points;
};
```

要求：

```text
count不得超过MOSIM_MAX_HORIZON
所有点时间单调递增
不得在实时循环中动态分配内存
第一点时间不得晚于当前控制时间过多
```

非预测控制器只读取当前参考点。

预测控制器读取整个参考时域。

---

## 11.4 时间参数化轨迹

规划器适配器应优先输出可求值的时间参数化轨迹。

控制循环在当前控制时刻：

[
t_c
]

对轨迹进行求值，得到：

[
p(t_c),v(t_c),a(t_c),j(t_c),s(t_c)
]

禁止直接以规划器最近一次发布的位置点作为持续保持目标。

---

# 12. 飞行器状态接口

## 12.1 VehicleState

```cpp
struct VehicleState {
    MessageHeader header;

    Vector3 position_enu_m;
    Vector3 velocity_enu_mps;
    Vector3 acceleration_enu_mps2;

    Quaternion attitude_enu_flu;

    Vector3 angular_velocity_flu_radps;
    Vector3 angular_acceleration_flu_radps2;

    uint32_t estimator_reset_counter;

    bool landed;
    bool armed;
};
```

---

## 12.2 状态语义

### 位置和速度

默认表示质心状态。

传感器安装点或IMU安装点状态必须先转换到质心。

### 加速度

`acceleration_enu_mps2`表示质心运动学加速度。

不得直接将IMU比力当作世界系加速度。

### 角速度

```text
坐标系：BODY_FLU
单位：rad/s
```

### 姿态

表示从BODY_FLU到ENU世界系的旋转。

---

## 12.3 EstimatorStatus

```cpp
struct EstimatorStatus {
    MessageHeader header;

    bool attitude_valid;
    bool horizontal_position_valid;
    bool vertical_position_valid;
    bool horizontal_velocity_valid;
    bool vertical_velocity_valid;

    bool using_ground_truth;
    bool using_external_odometry;

    double position_variance_m2[3];
    double velocity_variance_m2ps2[3];
    double attitude_variance_rad2[3];

    uint32_t reset_counter;
};
```

控制器可以根据估计器状态切换：

```text
完整位置控制
仅速度控制
仅姿态控制
安全降落
失效回退
```

---

# 13. 执行器状态接口

## 13.1 ActuatorState

```cpp
constexpr size_t MOSIM_MAX_ACTUATORS = 16;

struct ActuatorState {
    MessageHeader header;

    uint32_t actuator_count;

    std::array<double, MOSIM_MAX_ACTUATORS> rotor_speed_radps;
    std::array<double, MOSIM_MAX_ACTUATORS> rotor_thrust_N;
    std::array<double, MOSIM_MAX_ACTUATORS> motor_current_A;
    std::array<double, MOSIM_MAX_ACTUATORS> motor_temperature_C;

    std::array<double, MOSIM_MAX_ACTUATORS> effectiveness;
    std::array<uint8_t, MOSIM_MAX_ACTUATORS> health_state;
};
```

`effectiveness`定义为：

```text
1.0：正常
0.8：只能产生标称80%的作用
0.0：完全失效
```

---

## 13.2 BatteryState

```cpp
struct BatteryState {
    MessageHeader header;

    double voltage_V;
    double current_A;
    double remaining_ratio;
    double discharged_capacity_Ah;

    bool voltage_valid;
    bool current_valid;
};
```

---

# 14. 飞行器模型接口

## 14.1 VehicleModel

```cpp
struct VehicleModel {
    uint32_t model_version;

    double mass_kg;
    Matrix3 inertia_kgm2;

    Vector3 center_of_mass_offset_flu_m;

    double gravity_mps2;

    uint32_t actuator_count;
};
```

---

## 14.2 ActuatorGeometry

```cpp
enum class RotationDirection : int8_t {
    CLOCKWISE = -1,
    COUNTER_CLOCKWISE = 1
};

struct ActuatorGeometry {
    Vector3 position_flu_m;
    Vector3 thrust_axis_flu;

    RotationDirection rotation_direction;

    double thrust_coefficient;
    double torque_coefficient;
    double motor_time_constant_s;

    double minimum_thrust_N;
    double maximum_thrust_N;
    double maximum_thrust_rate_Nps;
};
```

电机编号、安装位置和旋转方向必须由几何描述文件确定。

禁止控制器硬编码：

```text
电机1一定是左前
电机2一定是右后
```

---

## 14.3 VehicleLimits

```cpp
struct VehicleLimits {
    double maximum_speed_mps;
    double maximum_acceleration_mps2;
    double maximum_jerk_mps3;

    double maximum_tilt_rad;
    double maximum_yaw_rate_radps;

    Vector3 maximum_body_rate_radps;
    Vector3 maximum_body_torque_Nm;

    double minimum_collective_thrust_N;
    double maximum_collective_thrust_N;

    std::array<double, MOSIM_MAX_ACTUATORS>
        maximum_rotor_thrust_N;
};
```

所有控制器、控制分配器和安全过滤器应读取同一份约束描述。

---

# 15. 扰动和故障接口

## 15.1 DisturbanceEstimate

```cpp
struct DisturbanceEstimate {
    MessageHeader header;

    Vector3 force_enu_N;
    Vector3 torque_flu_Nm;

    Matrix3 force_covariance;
    Matrix3 torque_covariance;

    uint32_t estimator_type;
};
```

该接口可由：

```text
DOB
ESO
INDI
L1
Kalman扰动观测器
AWFF
```

提供。

---

## 15.2 ActuatorHealth

```cpp
enum class ActuatorHealthState : uint8_t {
    UNKNOWN = 0,
    NORMAL,
    DEGRADED,
    STUCK,
    INTERMITTENT,
    FAILED
};

struct ActuatorHealth {
    MessageHeader header;

    uint32_t actuator_count;

    std::array<ActuatorHealthState,
               MOSIM_MAX_ACTUATORS> state;

    std::array<double,
               MOSIM_MAX_ACTUATORS> effectiveness;

    std::array<double,
               MOSIM_MAX_ACTUATORS> confidence;
};
```

---

# 16. 控制器输入接口

```cpp
struct ControllerInput {
    TimeUs control_time_us;
    double dt_s;

    const TrajectoryPoint* current_reference;
    const ReferenceHorizon* reference_horizon;

    const VehicleState* vehicle_state;
    const EstimatorStatus* estimator_status;

    const VehicleModel* vehicle_model;
    const VehicleLimits* vehicle_limits;

    const ActuatorState* actuator_state;
    const BatteryState* battery_state;

    const DisturbanceEstimate* disturbance_estimate;
    const ActuatorHealth* actuator_health;
};
```

不需要的数据可以为空指针，但控制器必须在`ControllerCapability`中声明必需输入。

---

# 17. 控制输出层级

## 17.1 输出类型

```cpp
enum class ControlOutputType : uint8_t {
    NONE = 0,

    POSITION_SETPOINT,
    VELOCITY_SETPOINT,
    ACCELERATION_YAW,

    ATTITUDE_THRUST,
    BODY_RATE_THRUST,

    WRENCH,

    ROTOR_THRUST,
    ROTOR_SPEED
};
```

---

## 17.2 AccelerationYawCommand

```cpp
struct AccelerationYawCommand {
    Vector3 acceleration_enu_mps2;

    double yaw_enu_rad;
    double yaw_rate_radps;
};
```

---

## 17.3 AttitudeThrustCommand

```cpp
struct AttitudeThrustCommand {
    Quaternion attitude_enu_flu;

    double collective_thrust_N;

    double yaw_rate_feedforward_radps;
};
```

`collective_thrust_N`定义为总正推力标量：

```text
collective_thrust_N >= 0
```

其作用方向为机体系`+Z_FLU`。

禁止在MoSim算法核心中将其直接表示为PX4归一化负Z推力。

---

## 17.4 BodyRateThrustCommand

```cpp
struct BodyRateThrustCommand {
    Vector3 body_rate_flu_radps;
    double collective_thrust_N;
};
```

---

## 17.5 WrenchCommand

```cpp
struct WrenchCommand {
    Vector3 force_flu_N;
    Vector3 torque_flu_Nm;
};
```

四旋翼常规控制中：

```text
force.x ≈ 0
force.y ≈ 0
force.z = collective_thrust_N
```

但接口保留完整三维力，支持倾转执行器等扩展。

---

## 17.6 RotorThrustCommand

```cpp
struct RotorThrustCommand {
    uint32_t actuator_count;

    std::array<double,
               MOSIM_MAX_ACTUATORS> thrust_N;
};
```

---

## 17.7 RotorSpeedCommand

```cpp
struct RotorSpeedCommand {
    uint32_t actuator_count;

    std::array<double,
               MOSIM_MAX_ACTUATORS> speed_radps;
};
```

---

## 17.8 ControllerCommand

```cpp
struct ControllerCommand {
    MessageHeader header;

    ControlOutputType type;

    union {
        AccelerationYawCommand acceleration_yaw;
        AttitudeThrustCommand attitude_thrust;
        BodyRateThrustCommand body_rate_thrust;
        WrenchCommand wrench;
        RotorThrustCommand rotor_thrust;
        RotorSpeedCommand rotor_speed;
    };

    uint32_t saturation_flags;
    uint32_t safety_flags;
};
```

生产实现中如果编译器或代码生成工具不适合使用`union`，可以改为固定字段加有效位结构。

---

# 18. 推力语义与推力映射

## 18.1 核心接口使用物理推力

MoSim算法核心统一输出：

```text
N
```

而不是：

```text
0～1油门
-1～1归一化推力
PWM
DShot数值
```

---

## 18.2 推力适配器

PX4、MAVROS或电机适配器负责：

[
T_N
\rightarrow
u_{normalized}
\rightarrow
PWM/DShot/RPM
]

推力映射器至少考虑：

```text
悬停油门
电池电压
推力系数
电机转速
桨叶参数
空气密度
执行器效率
```

---

## 18.3 映射接口

```cpp
class IThrustMapper {
public:
    virtual bool thrustToNormalized(
        double thrust_N,
        const BatteryState& battery,
        double& normalized_command) = 0;

    virtual bool normalizedToThrust(
        double normalized_command,
        const BatteryState& battery,
        double& thrust_N) = 0;
};
```

---

# 19. 控制器能力描述

```cpp
enum class InputRequirement : uint64_t {
    POSITION             = 1ULL << 0,
    VELOCITY             = 1ULL << 1,
    ACCELERATION         = 1ULL << 2,
    ATTITUDE             = 1ULL << 3,
    ANGULAR_VELOCITY     = 1ULL << 4,
    ANGULAR_ACCELERATION = 1ULL << 5,
    MOTOR_SPEED          = 1ULL << 6,
    BATTERY_STATE        = 1ULL << 7,
    DISTURBANCE_ESTIMATE = 1ULL << 8,
    ACTUATOR_HEALTH      = 1ULL << 9
};

struct ControllerCapability {
    const char* controller_name;
    const char* controller_version;

    uint64_t required_state_mask;
    uint64_t required_reference_mask;

    ControlOutputType output_type;

    bool supports_constraints;
    bool supports_fault_tolerance;
    bool supports_online_parameter_update;
    bool supports_codegen;
    bool supports_px4_onboard;
    bool supports_reference_horizon;

    double nominal_period_s;
    double worst_case_execution_time_s;
};
```

---

# 20. 控制器核心API

## 20.1 C++接口

```cpp
class IController {
public:
    virtual ~IController() = default;

    virtual const ControllerCapability&
    capability() const = 0;

    virtual bool configure(
        const ControllerConfiguration& configuration,
        const VehicleModel& model,
        const VehicleLimits& limits) = 0;

    virtual bool reset(
        const VehicleState& state,
        const TrajectoryPoint& reference,
        TimeUs reset_time_us) = 0;

    virtual ControllerResult update(
        const ControllerInput& input,
        ControllerCommand& output,
        ControllerStatus& status) = 0;

    virtual void deactivate() = 0;
};
```

---

## 20.2 C兼容接口

为MWORKS代码生成和PX4集成提供C ABI：

```cpp
extern "C" {

int32_t mosim_controller_create(
    MosimControllerHandle* handle);

int32_t mosim_controller_configure(
    MosimControllerHandle handle,
    const MosimControllerConfig* config,
    const MosimVehicleModel* model,
    const MosimVehicleLimits* limits);

int32_t mosim_controller_reset(
    MosimControllerHandle handle,
    const MosimVehicleState* state,
    const MosimTrajectoryPoint* reference,
    uint64_t time_us);

int32_t mosim_controller_step(
    MosimControllerHandle handle,
    const MosimControllerInput* input,
    MosimControllerCommand* command,
    MosimControllerStatus* status);

int32_t mosim_controller_destroy(
    MosimControllerHandle handle);

}
```

---

## 20.3 代码生成限制

生成的控制算法核心应尽量满足：

```text
纯C/C++接口
固定尺寸数组
无动态内存
无RTTI依赖
无异常依赖
无文件系统依赖
无ROS/PX4头文件依赖
可重复初始化
可显式复位
```

---

# 21. 控制器状态接口

## 21.1 状态枚举

```cpp
enum class ControllerLifecycleState : uint8_t {
    UNCONFIGURED = 0,
    READY,
    STANDBY,
    ACTIVE,
    DEGRADED,
    FAILED,
    FALLBACK
};
```

---

## 21.2 结果码

```cpp
enum class ControllerResult : int32_t {
    OK = 0,

    NOT_CONFIGURED,
    NOT_INITIALIZED,

    INVALID_INPUT,
    INVALID_FRAME,
    INVALID_PARAMETER,

    STALE_STATE,
    STALE_REFERENCE,

    ESTIMATOR_INVALID,
    ACTUATOR_INVALID,

    SOLVER_TIMEOUT,
    SOLVER_INFEASIBLE,
    SOLVER_DIVERGED,

    NON_FINITE_OUTPUT,
    LIMIT_VIOLATION,

    INTERNAL_ERROR
};
```

---

## 21.3 ControllerStatus

```cpp
struct ControllerStatus {
    MessageHeader header;

    ControllerLifecycleState lifecycle;
    ControllerResult result;

    double execution_time_us;
    double worst_execution_time_us;

    uint32_t solver_iterations;
    double solver_cost;
    double solver_residual;

    uint32_t saturation_flags;
    uint32_t warning_flags;
    uint32_t error_flags;

    uint64_t active_parameter_version;
    uint64_t active_model_version;
};
```

---

# 22. 参数更新接口

参数分为：

```text
HOT参数
运行中可以原子更新

COLD参数
更新后必须重新初始化控制器

BUILD参数
必须重新编译
```

## 22.1 HOT参数示例

```text
PID增益
权重矩阵
约束限值
扰动补偿开关
滤波频率
```

## 22.2 COLD参数示例

```text
MPC预测时域
状态维数
控制维数
电机数量
求解器结构
```

## 22.3 BUILD参数示例

```text
最大预测步数
固定数组尺寸
算法编译选项
求解器后端
```

参数更新必须在控制周期边界原子生效，不得在一次`update()`执行过程中改变。

---

# 23. ROS 1接口规范

## 23.1 消息包

建立独立消息包：

```text
mosim_msgs
```

建议包含：

```text
TrajectoryPoint.msg
ReferenceHorizon.msg
VehicleState.msg
VehicleModel.msg
VehicleLimits.msg
ActuatorState.msg
ActuatorHealth.msg
ControllerCommand.msg
ControllerStatus.msg
ControllerSelection.msg
```

---

## 23.2 ROS命名空间

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

禁止多个无人机共享无命名空间的控制话题。

---

## 23.3 推荐Topic

```text
/mosim/uav0/reference/trajectory
/mosim/uav0/reference/horizon

/mosim/uav0/state/vehicle
/mosim/uav0/state/actuator
/mosim/uav0/state/battery
/mosim/uav0/state/estimator

/mosim/uav0/control/command
/mosim/uav0/control/status

/mosim/uav0/fault/actuator_health
/mosim/uav0/disturbance/estimate

/mosim/uav0/controller/select
/mosim/uav0/controller/parameter_update
```

---

## 23.4 ROS适配器职责

ROS适配器负责：

```text
订阅ROS消息
检查frame_id
执行tf转换
转换单位
转换到MoSim结构
调用控制器核心
转换控制输出
发布MAVROS/PX4/Gazebo消息
维护心跳和状态
```

控制器核心不得自行调用ROS API。

---

# 24. Gazebo接口规范

Gazebo在MoSim中负责：

```text
动力学
碰撞
环境
执行器
传感器
真值状态
```

Gazebo适配器输出：

```text
GroundTruthState
SensorMeasurement
ActuatorState
CollisionState
EnvironmentState
```

控制器默认不得直接订阅Gazebo真值。

只有以下模式可以使用真值：

```text
算法理想条件测试
控制器理论验证
估计器误差对照
Test Harness基准计算
```

正式闭环应通过：

```text
PX4 EKF
外部里程计
LIO/VIO
仿真传感器融合
```

获得控制状态。

---

# 25. PX4 uORB适配规范

## 25.1 设计原则

MoSim控制器核心不得包含uORB订阅和发布代码。

PX4侧建立：

```text
mosim_controller_module
mosim_controller_manager
mosim_frame_adapter
mosim_thrust_mapper
```

---

## 25.2 PX4输入映射

PX4适配器可读取：

```text
vehicle_local_position
vehicle_attitude
vehicle_angular_velocity
vehicle_acceleration
vehicle_odometry

trajectory_setpoint

battery_status
esc_status
actuator_motors

vehicle_status
land_detected
parameter_update
```

适配器将NED/FRD数据转换为MoSim ENU/FLU数据。

---

## 25.3 PX4输出映射

### 输出位置/速度/加速度参考

映射到：

```text
trajectory_setpoint
```

保留PX4：

```text
位置环
速度环
姿态环
角速度环
控制分配
```

### 输出姿态和总推力

映射到：

```text
vehicle_attitude_setpoint
```

保留PX4：

```text
姿态环
角速度环
控制分配
```

### 输出角速度和总推力

映射到：

```text
vehicle_rates_setpoint
```

保留PX4：

```text
角速度环
控制分配
```

### 输出力矩和推力

映射到：

```text
vehicle_torque_setpoint
vehicle_thrust_setpoint
```

保留PX4：

```text
控制分配
执行器输出
```

### 输出单电机命令

映射到：

```text
actuator_motors
```

绕过：

```text
位置环
速度环
姿态环
角速度环
控制分配
```

该模式必须由专门的安全策略控制。

---

## 25.4 发布所有权

任何时刻，一个控制通道只能有一个有效生产者。

禁止同时存在：

```text
PX4原生位置控制器发布姿态设定值
MoSim控制器也发布姿态设定值
```

建议采用以下结构：

```text
多个控制器候选
      ↓
MoSim Controller Manager
      ↓
唯一标准PX4控制Topic发布者
```

所有控制器将命令交给Controller Manager。

只有Controller Manager能够向标准PX4控制Topic发布最终命令。

---

## 25.5 自定义uORB消息

建议为MoSim内部管理创建：

```text
mosim_controller_request
mosim_controller_status
mosim_controller_command
mosim_actuator_health
mosim_disturbance_estimate
```

这些消息不得与PX4标准消息重复表达同一语义。

MoSim自定义消息用于：

```text
控制器管理
算法诊断
故障状态
模块切换
内部物理单位传递
```

最终PX4标准控制消息由适配器统一生成。

---

# 26. 控制层级所有权

| 输出模式              | MoSim负责   | PX4保留  |
| ----------------- | --------- | ------ |
| PX4_NATIVE        | 无外部控制     | 全部控制环  |
| POSITION_SETPOINT | 参考生成      | 位置至执行器 |
| ACCELERATION_YAW  | 外部位置/速度控制 | 姿态至执行器 |
| ATTITUDE_THRUST   | 外部轨迹跟踪    | 姿态至执行器 |
| BODY_RATE_THRUST  | 外部位置和姿态控制 | 角速度与分配 |
| WRENCH            | 外部完整刚体控制  | 控制分配   |
| ROTOR_THRUST      | 外部控制与分配   | 执行器映射  |
| ROTOR_SPEED       | 外部完整控制    | 电机驱动   |

每个Profile必须明确声明控制所有权。

---

# 27. MWORKS接口规范

MWORKS模型通过Sysblock或代码生成包装器调用控制器核心。

## 27.1 输入端口组

```text
ReferenceBus
StateBus
ModelBus
LimitsBus
ActuatorBus
DisturbanceBus
HealthBus
```

## 27.2 输出端口组

```text
CommandBus
StatusBus
DiagnosticsBus
```

## 27.3 代码生成要求

生成代码只实现：

```text
初始化
参数写入
状态复位
单周期计算
状态输出
```

以下功能由PX4或ROS包装层实现：

```text
uORB
Topic
日志
参数服务器
模式切换
解锁
心跳
故障回退
```

---

# 28. 控制命令安全检查

Controller Manager在接受任何控制输出前必须检查：

```text
输出类型是否与当前模式匹配
时间戳是否有效
数据是否有限
四元数是否合法
推力是否为正
控制量是否超过限制
执行器数量是否匹配
状态序号是否连续
控制器是否处于ACTIVE状态
```

---

## 28.1 最终限幅顺序

建议顺序：

```text
控制器内部约束
      ↓
增强模块约束
      ↓
安全过滤器
      ↓
Controller Manager最终限幅
      ↓
PX4/执行器硬件限幅
```

Controller Manager的限幅是最后的软件安全边界。

---

## 28.2 饱和标志

```cpp
enum SaturationFlag : uint32_t {
    SAT_NONE             = 0,
    SAT_POSITION         = 1U << 0,
    SAT_VELOCITY         = 1U << 1,
    SAT_ACCELERATION     = 1U << 2,
    SAT_TILT             = 1U << 3,
    SAT_BODY_RATE        = 1U << 4,
    SAT_TORQUE           = 1U << 5,
    SAT_COLLECTIVE_THRUST= 1U << 6,
    SAT_ACTUATOR         = 1U << 7
};
```

---

# 29. 异常和降级规则

## 29.1 状态过期

```text
保持上次输出不超过一个短暂周期
随后进入DEGRADED
切换到安全控制器
严重时进入降落或停机策略
```

禁止长期保持旧控制命令。

---

## 29.2 参考轨迹过期

默认降级顺序：

```text
保持当前安全轨迹点
      ↓
切换定点悬停
      ↓
返航或降落
```

---

## 29.3 求解器失败

MPC/NMPC失败时：

```text
第一次失败：
使用上一次可行解的首个控制量

连续失败：
切换备用SE(3)或PID

长期失败：
触发安全悬停或降落
```

---

## 29.4 非有限输出

任何NaN或Inf输出必须立即拒绝，不得发送到执行器。

---

# 30. 多机接口

每条消息必须包含：

```text
vehicle_id
source_id
trajectory_id
sequence
```

多机系统禁止仅依赖ROS命名空间判断无人机身份。

编队接口必须区分：

```text
本机状态
邻机广播状态
领航机状态
编队参考
规划轨迹
避碰修正
```

不同无人机时间戳应映射到统一仿真时间或经过时钟同步的系统时间。

---

# 31. 接口版本管理

## 31.1 版本格式

```text
MAJOR.MINOR.PATCH
```

### MAJOR

不兼容的数据结构变更。

### MINOR

向后兼容地增加字段或能力。

### PATCH

修复说明、边界检查或实现错误。

---

## 31.2 ABI兼容

C接口结构体建议包含：

```cpp
uint32_t struct_size;
uint16_t interface_major;
uint16_t interface_minor;
```

接收方必须根据`struct_size`判断可读取字段范围。

---

# 32. 日志接口

每个控制周期至少记录：

```text
控制时间
控制器名称
控制器状态
参考位置、速度、加速度
当前位置、速度、姿态、角速度
控制器原始输出
安全过滤后输出
最终执行器输出
饱和状态
求解时间
求解器状态
故障和降级状态
```

MWORKS、ROS bag、PX4 ULog和Gazebo真值日志应使用：

```text
vehicle_id
trajectory_id
experiment_id
timestamp
```

进行对齐。

---

# 33. 接口验收测试

统一接口完成后必须通过以下测试。

## 33.1 坐标转换测试

```text
ENU → NED → ENU
FLU → FRD → FLU
Quaternion → Matrix → Quaternion
Yaw ENU → NED → ENU
```

往返误差必须低于规定数值容差。

---

## 33.2 单位测试

验证：

```text
rad与deg不会混用
rad/s与rpm不会混用
N与归一化油门不会混用
μs与s不会混用
```

---

## 33.3 时间测试

验证：

```text
正常周期
周期抖动
时间回退
大时间跳跃
仿真暂停
仿真重启
日志回放
```

---

## 33.4 有效性测试

验证：

```text
字段缺失
状态过期
参考过期
NaN输入
Inf输入
非法四元数
错误frame
错误车辆ID
```

---

## 33.5 输出层级测试

分别验证：

```text
TrajectorySetpoint
Attitude + Thrust
Body Rate + Thrust
Wrench
Rotor Thrust
Rotor Speed
```

能够正确映射到MWORKS、ROS、Gazebo和PX4。

---

## 33.6 跨平台一致性测试

同一输入数据集分别驱动：

```text
MWORKS控制器
ROS控制器节点
PX4 Module
离线测试程序
```

其控制器核心输出应在设定浮点误差范围内一致。

---

# 34. 推荐代码目录

```text
MoSim/
├── Interfaces/
│   ├── include/
│   │   └── mosim/
│   │       ├── core/
│   │       │   ├── types.hpp
│   │       │   ├── time.hpp
│   │       │   ├── frames.hpp
│   │       │   └── result.hpp
│   │       ├── reference/
│   │       │   ├── trajectory_point.hpp
│   │       │   └── reference_horizon.hpp
│   │       ├── state/
│   │       │   ├── vehicle_state.hpp
│   │       │   ├── actuator_state.hpp
│   │       │   └── estimator_status.hpp
│   │       ├── model/
│   │       │   ├── vehicle_model.hpp
│   │       │   ├── actuator_geometry.hpp
│   │       │   └── vehicle_limits.hpp
│   │       ├── control/
│   │       │   ├── controller_input.hpp
│   │       │   ├── controller_command.hpp
│   │       │   ├── controller_status.hpp
│   │       │   └── controller_api.hpp
│   │       └── fault/
│   │           ├── actuator_health.hpp
│   │           └── disturbance_estimate.hpp
│   │
│   ├── src/
│   │   ├── frame_conversion.cpp
│   │   ├── validity_check.cpp
│   │   └── thrust_mapping.cpp
│   │
│   └── tests/
│       ├── test_frame_conversion.cpp
│       ├── test_quaternion.cpp
│       ├── test_interface_version.cpp
│       └── test_validity.cpp
│
├── Adapters/
│   ├── mworks/
│   ├── ros1/
│   ├── gazebo/
│   ├── px4_uorb/
│   └── offline/
│
└── Msg/
    ├── ros1/
    └── px4_uorb/
```

---

# 35. 首版实施范围

统一接口V1.0首先实现：

```text
TrajectoryPoint
ReferenceHorizon
VehicleState
VehicleModel
VehicleLimits
ControllerInput
ControllerCommand
ControllerStatus
ControllerCapability

ENU/FLU与NED/FRD转换
ROS 1适配器
MWORKS适配器
PX4 uORB适配器
Gazebo真值与执行器适配器
```

首版至少支持：

```text
PX4原生控制器
px4ctrl复现
MWORKS PID
SE(3)
DFBC
LMPC
NMPC
```

---

# 36. 强制性设计规则汇总

1. 控制器核心统一使用ENU世界系和FLU机体系。

2. PX4适配器负责NED/FRD转换。

3. 控制器核心统一使用SI单位和物理推力。

4. 归一化推力、PWM和DShot只存在于执行器适配层。

5. 内部字段缺失使用`valid_mask`，不得使用NaN。

6. 四元数统一为Hamilton `[w,x,y,z]`。

7. 所有动态数据必须携带采样时间、发布时间和序号。

8. 控制器核心不得直接依赖ROS、uORB、Gazebo或MWORKS类型。

9. 控制器不得在单周期函数中执行动态内存申请和阻塞操作。

10. 一个PX4标准控制通道同一时刻只能有一个最终生产者。

11. Controller Manager是最终控制命令的唯一仲裁者。

12. 所有控制器必须声明能力、必需输入、输出层级和运行周期。

13. 所有控制器输出都必须通过统一合法性检查和最终安全限幅。

14. MWORKS、ROS节点和PX4 Module必须调用同一套控制器核心。

15. 接口变更必须遵守版本管理和跨平台回归测试要求。

---

# 37. 文档结论

MoSim统一控制接口不是简单定义若干ROS Topic或uORB消息，而是建立一个与运行环境无关的控制算法契约。

通过该接口，MoSim能够形成：

```text
统一参考输入
统一状态输入
统一物理单位
统一坐标约定
统一控制输出
统一异常状态
统一控制器管理
统一跨平台部署
```

最终使同一个控制器能够依次经历：

```text
MWORKS模型仿真
      ↓
离线数据回放
      ↓
ROS 1 + Gazebo联合仿真
      ↓
PX4 SITL
      ↓
PX4板载Module
      ↓
HITL
      ↓
真实四旋翼飞行
```

而不需要重新实现控制算法本体。
