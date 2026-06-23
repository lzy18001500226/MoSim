# CoSim 多域机器人与自主系统协同仿真平台总体设计说明书

**文档版本：** v0.1
**项目名称：** CoSim
**项目类型：** 多域、多载具、多动力学、多飞控、仿真—实机一体化平台
**适用对象：** 多旋翼、固定翼、地面车辆、足式机器人、空地异构集群及其他自主系统

---

# 一、项目概述

## 1.1 项目定位

CoSim 是一个面向机器人与自主系统的可组合协同仿真和开发平台。

CoSim 不试图重新实现所有动力学引擎、飞控系统、机器人中间件和渲染引擎，而是建立统一的平台内核、数据模型、插件接口和实验管理体系，将不同领域中成熟的工具组合为可复用、可迁移、可验证的完整系统。

CoSim 的核心目标是解决以下问题：

1. 多旋翼、固定翼、小车和机器狗分别使用不同动力学后端时，如何由一套平台统一管理。
2. PX4、ArduPilot、直接控制器和强化学习策略如何接入统一系统。
3. ROS 2 如何作为高级自主与协同总线，同时不成为所有载具的强制依赖。
4. Gazebo、JSBSim、MuJoCo、Genesis 等后端如何共享统一状态、命令、时间和日志接口。
5. 仿真算法如何迁移到软件在环、硬件在环和真实载具。
6. Unreal Engine 如何作为独立高保真显示端，而不与具体动力学后端绑定。
7. 单机自主系统如何逐步扩展为多机、空地和异构协同系统。
8. 不同实验如何保持可配置、可记录、可重复和可评价。

---

## 1.2 CoSim 的三层含义

CoSim 中的 `Co` 同时表达：

### Co-Simulation

多个动力学模型、飞控系统、算法和渲染器进行联合仿真。

### Composable Simulation

系统由可替换、可组合的模块构成，而不是一个不可拆分的单体程序。

### Cooperative Simulation

支持多机器人、多飞行器及异构系统之间的协同任务仿真。

---

## 1.3 一句话定位

> CoSim 是面向多旋翼、固定翼、地面车辆、足式机器人和异构集群的多动力学、多飞控、仿真—实机一体化开放平台。

---

# 二、建设目标

## 2.1 总体目标

CoSim 应形成从模型开发到算法验证、从软件仿真到实机部署的完整技术链：

```text
车辆模型
    ↓
动力学仿真
    ↓
飞控与控制器
    ↓
感知、定位、规划与任务
    ↓
协同系统
    ↓
高保真显示
    ↓
日志、评价与回放
    ↓
SIL / HIL / 实机部署
```

---

## 2.2 第一阶段目标

第一阶段以云纵 Sunray-150 四旋翼和 MID360 为标准验证对象，完成：

* Gazebo 四旋翼动力学；
* PX4 SITL；
* ROS 2 通信；
* MID360 仿真；
* 定位、建图和局部规划；
* UE 独立显示；
* 实验配置与日志；
* 仿真和实机接口统一。

---

## 2.3 第二阶段目标

加入固定翼域：

* JSBSim 固定翼动力学；
* ArduPlane SITL；
* 普通固定翼和通用鸭式研究飞机；
* 舵面、襟翼、起落架及推进系统；
* 独立制导算法核心；
* UE 固定翼显示；
* 固定翼仿真到涵道航模部署链。

---

## 2.4 第三阶段目标

加入其他机器人：

* 地面无人车；
* 机器狗和足式机器人；
* 空地协同；
* 异构任务分配；
* 多机器人状态共享；
* 多后端统一显示和实验管理。

---

## 2.5 长期目标

长期形成以下能力：

```text
模型在环 MIL
软件在环 SIL
处理器在环 PIL
硬件在环 HIL
实机在环
日志回放
强化学习
参数辨识
故障注入
批量实验
数字孪生
异构集群协同
```

---

# 三、非目标

CoSim 第一阶段不追求：

1. 自研通用物理引擎；
2. 自研完整飞控固件；
3. 替代 Gazebo、JSBSim、MuJoCo 或 Unreal Engine；
4. 精确复现真实战斗机的专有气动数据库；
5. 同时支持所有机器人和所有仿真后端；
6. 让所有模块强制依赖 ROS 2；
7. 将所有第三方项目源码复制进一个巨型仓库；
8. 第一阶段完成大规模异构集群；
9. 第一阶段实现完全精确的空气动力、推进和传感器模型。

---

# 四、总体设计原则

## 4.1 外部集成，内部解耦

对使用者，CoSim 应表现为一个统一平台：

* 一个启动器；
* 一个配置体系；
* 一个实验管理器；
* 一套车辆资产；
* 一套日志和回放工具；
* 一个高保真显示端。

对内部，各领域保持独立：

* 多旋翼使用自己的动力学和飞控；
* 固定翼使用自己的动力学和飞控；
* 小车使用自己的动力学和控制系统；
* 机器狗使用自己的关节动力学和控制系统。

---

## 4.2 统一平台，不统一动力学

不同载具不应被强行塞入同一个动力学模型。

推荐关系：

| 载具类型  | 默认工程后端              | 高速训练后端               | 默认控制系统          |
| ----- | ------------------- | -------------------- | --------------- |
| 多旋翼   | Gazebo              | MuJoCo、Genesis       | PX4             |
| 固定翼   | JSBSim              | JSBSim Batch、自定义快速模型 | ArduPlane       |
| 地面车辆  | Gazebo              | MuJoCo、CARLA或简化模型    | ROS 2、ArduRover |
| 足式机器人 | MuJoCo、Isaac、Gazebo | MuJoCo、Isaac、Genesis | 关节控制器           |
| 异构协同  | 多后端联合               | 简化多智能体模型             | ROS 2任务系统       |

---

## 4.3 一个实体只能有一个权威物理后端

每个仿真实体必须声明：

```text
authoritative_physics_backend
```

例如：

```text
sunray_01:
    Gazebo

fixedwing_01:
    JSBSim

quadruped_01:
    MuJoCo
```

其他系统只能：

* 读取状态；
* 镜像显示；
* 生成传感器；
* 发送命令；
* 记录数据。

不得同时由两个物理引擎推进同一实体的六自由度状态。

---

## 4.4 UE 默认只负责显示

Unreal Engine 默认职责：

* 三维场景；
* 车辆外观；
* 舵面、桨叶、起落架动画；
* 摄像机；
* 光照与天气效果；
* 高质量演示；
* 日志回放；
* 可选视觉传感器。

UE 默认不负责：

* 主动力学积分；
* 飞控执行；
* ROS 2任务调度；
* 精确接触求解；
* 控制器状态管理。

---

## 4.5 ROS 2 是可选系统总线

ROS 2 不应成为 CoSim Core 的强制依赖。

三种运行模式：

```text
Standalone
    无ROS，飞控和算法直接通信

ROS Integrated
    ROS 2负责感知、规划和任务

Collaborative
    ROS 2负责多机和异构协同
```

固定翼普通航模可以只运行：

```text
ArduPlane + MAVLink
```

需要进入协同系统时，通过 Gateway 接入 ROS 2。

---

## 4.6 算法核心与通信框架分离

算法核心不能直接继承 ROS Node，也不能直接调用 Gazebo、PX4 或 JSBSim API。

正确结构：

```text
Algorithm Core
    纯C++ / Rust / Python计算逻辑

Adapter
    ROS2 Adapter
    MAVLink Adapter
    Simulation Adapter
    Replay Adapter
```

---

## 4.7 仿真、控制、传感器和渲染使用独立频率

系统必须支持：

```text
physics_rate
autopilot_rate
control_rate
planning_rate
sensor_rate
render_rate
logging_rate
```

不得让 UE 帧率决定物理步长，也不得要求所有传感器与控制器使用相同频率。

---

## 4.8 参数单一来源

车辆参数不得分别散落在：

* Gazebo SDF；
* MuJoCo MJCF；
* JSBSim XML；
* PX4参数；
* ArduPilot参数；
* UE Blueprint；
* ROS YAML。

必须建立中立参数源，再生成各后端资产。

---

# 五、系统总体架构

```text
┌───────────────────────────────────────────────────────────┐
│                    CoSim Studio                           │
│ 场景编辑 / 车辆配置 / 实验配置 / 启动 / 监控 / 回放       │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                  CoSim Orchestrator                       │
│ 生命周期 / 时钟 / 后端调度 / 实体管理 / 故障恢复           │
└──────────────┬──────────────┬──────────────┬──────────────┘
               │              │              │
┌──────────────▼───┐ ┌────────▼───────┐ ┌───▼─────────────┐
│ Physics Backends │ │ Autopilot      │ │ Algorithm       │
│ Gazebo           │ │ PX4            │ │ Localization    │
│ JSBSim           │ │ ArduPilot      │ │ Planning        │
│ MuJoCo           │ │ Direct Control │ │ Guidance        │
│ Genesis          │ │ Hardware FCU   │ │ Swarm           │
└──────────────┬───┘ └────────┬───────┘ └───┬─────────────┘
               │              │              │
┌──────────────▼──────────────▼──────────────▼──────────────┐
│                    CoSim Core                             │
│ State / Command / Time / Coordinates / Config / Events    │
└─────────────────────────────┬─────────────────────────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
┌──────▼──────┐        ┌──────▼──────┐       ┌──────▼──────┐
│ Transports  │        │ Data System │       │ Renderer    │
│ ROS 2       │        │ Log/Record  │       │ Unreal      │
│ MAVLink     │        │ Replay      │       │ Debug View  │
│ DDS         │        │ Metrics     │       │ Headless    │
│ UDP/SHM     │        │ Dataset     │       │             │
└─────────────┘        └─────────────┘       └─────────────┘
```

---

# 六、软件产品组成

## 6.1 CoSim Core

负责平台最底层的公共抽象：

* 数据类型；
* 状态与命令；
* 时间；
* 坐标；
* 配置；
* 事件；
* 插件发现；
* 序列化；
* 错误处理；
* 版本管理。

CoSim Core 不依赖 ROS 2、Gazebo、PX4 或 UE。

---

## 6.2 CoSim Runtime

负责：

* 加载实验配置；
* 创建实体；
* 加载后端；
* 推进时间；
* 调度物理；
* 路由命令；
* 汇总状态；
* 故障检测；
* 进程管理；
* 停止和重置实验。

---

## 6.3 CoSim Studio

面向用户的配置和管理程序：

* 创建项目；
* 选择载具；
* 选择场景；
* 选择后端；
* 配置传感器；
* 配置飞控；
* 配置算法；
* 配置实验；
* 启动和停止；
* 查看状态；
* 管理日志；
* 回放实验。

第一阶段可以先使用 CLI 与 YAML，GUI 后续实现。

---

## 6.4 CoSim Flight

航空器领域包：

```text
aerial_common
multirotor
fixedwing
vtol
test_vehicle
```

负责航空器公共状态、控制命令、气动参数和飞行任务接口。

---

## 6.5 CoSim Ground

地面机器人领域包：

* 轮式车辆；
* 履带车辆；
* 阿克曼车辆；
* 差速车辆；
* ArduRover；
* ROS 2导航接口。

---

## 6.6 CoSim Legged

足式机器人领域包：

* 关节状态；
* 足端状态；
* 接触；
* 步态；
* 关节控制；
* 高层速度命令；
* MuJoCo、Isaac、Gazebo适配。

---

## 6.7 CoSim Swarm

负责：

* 多机器人注册；
* 状态共享；
* 任务分配；
* 编队；
* 协同搜索；
* 空地协同；
* 通信拓扑；
* 冲突检测；
* 多机评价。

---

## 6.8 CoSim Bridge

负责：

* ROS 2；
* MAVLink；
* PX4 DDS；
* ArduPilot DDS；
* UDP；
* TCP；
* Shared Memory；
* FMI；
* UE连接。

---

## 6.9 CoSim View

负责：

* UE实时显示；
* 车辆动画；
* 相机切换；
* 场景和天气；
* 日志回放；
* 状态叠加；
* HUD；
* 调试可视化；
* 视频和数据输出。

---

## 6.10 CoSim Lab

负责：

* 强化学习环境；
* 批量仿真；
* 参数扫描；
* 参数辨识；
* Monte Carlo；
* 域随机化；
* 故障测试；
* 数据集生成；
* 控制器比较。

---

## 6.11 CoSim Deploy

负责：

* SIL；
* PIL；
* HIL；
* 实机部署；
* 参数发布；
* 配置同步；
* 版本检查；
* 飞行前检查；
* 实机日志回收。

---

# 七、领域模型设计

## 7.1 基础实体

```cpp
struct EntityId {
    std::string value;
};

struct Timestamp {
    int64_t nanoseconds;
};

struct Pose3D {
    Vector3 position;
    Quaternion orientation;
};

struct Twist3D {
    Vector3 linear;
    Vector3 angular;
};

struct EntityState {
    EntityId id;
    Timestamp timestamp;
    uint64_t sequence;
    Pose3D pose;
    Twist3D velocity;
    Vector3 linear_acceleration;
    HealthState health;
};
```

---

## 7.2 航空器公共状态

```cpp
struct AerialVehicleState : EntityState {
    GeoPoint geodetic_position;
    double altitude_msl;
    double altitude_agl;
    double heading;
    Vector3 wind_enu;
};
```

---

## 7.3 多旋翼状态

```cpp
struct MultirotorState : AerialVehicleState {
    std::vector<double> rotor_speed;
    std::vector<double> motor_command;
    double collective_thrust;
    double battery_voltage;
    double battery_current;
};
```

---

## 7.4 固定翼状态

```cpp
struct FixedWingState : AerialVehicleState {
    double true_airspeed;
    double indicated_airspeed;
    double mach;
    double angle_of_attack;
    double sideslip_angle;
    double dynamic_pressure;

    double throttle;
    double aileron;
    double elevator;
    double rudder;
    double flap;
    double canard;
    double airbrake;
    double landing_gear;

    double fuel_mass;
};
```

---

## 7.5 地面车辆状态

```cpp
struct GroundVehicleState : EntityState {
    std::vector<double> wheel_speed;
    double steering_angle;
    double longitudinal_speed;
    int gear;
};
```

---

## 7.6 足式机器人状态

```cpp
struct LeggedState : EntityState {
    std::vector<double> joint_position;
    std::vector<double> joint_velocity;
    std::vector<double> joint_torque;
    std::vector<bool> foot_contact;
};
```

---

# 八、能力声明系统

每个实体必须发布能力描述。

```cpp
struct VehicleCapabilities {
    bool supports_position_command;
    bool supports_velocity_command;
    bool supports_attitude_command;
    bool supports_body_rate_command;
    bool supports_motor_command;
    bool supports_waypoint_command;
    bool supports_path_command;
    bool supports_hover;
    bool supports_takeoff;
    bool supports_landing;
};
```

固定翼不应声明悬停能力，普通小车不应声明高度命令能力。

任务系统根据能力选择控制方式。

---

# 九、命令体系

## 9.1 公共命令头

```cpp
struct CommandHeader {
    EntityId target;
    Timestamp timestamp;
    uint64_t sequence;
    std::string frame;
    int priority;
    double timeout;
};
```

---

## 9.2 通用命令

```text
TakeoffCommand
LandCommand
EmergencyStopCommand
HoldCommand
MissionCommand
```

---

## 9.3 多旋翼命令

```text
PositionCommand
VelocityCommand
AttitudeThrustCommand
BodyRateThrustCommand
MotorCommand
```

---

## 9.4 固定翼命令

```text
WaypointCommand
PathCommand
AirspeedAltitudeCommand
BankClimbCommand
AttitudeCommand
ControlSurfaceCommand
ThrottleCommand
```

---

## 9.5 地面车辆命令

```text
BodyVelocityCommand
AckermannCommand
WheelCommand
PathCommand
```

---

## 9.6 足式机器人命令

```text
BodyVelocityCommand
BodyPoseCommand
JointPositionCommand
JointTorqueCommand
FootTargetCommand
```

---

# 十、插件接口设计

## 10.1 物理后端接口

```cpp
class IPhysicsBackend {
public:
    virtual ~IPhysicsBackend() = default;

    virtual BackendInfo info() const = 0;
    virtual void configure(const BackendConfig&) = 0;
    virtual void loadWorld(const WorldConfig&) = 0;
    virtual void spawnEntity(const EntityConfig&) = 0;
    virtual void removeEntity(const EntityId&) = 0;

    virtual void reset(const ResetRequest&) = 0;
    virtual void applyActuator(
        const EntityId&,
        const ActuatorCommand&) = 0;

    virtual void applyExternalWrench(
        const EntityId&,
        const ExternalWrench&) = 0;

    virtual void step(Duration dt) = 0;
    virtual EntityState getState(const EntityId&) const = 0;
    virtual BackendDiagnostics diagnostics() const = 0;
};
```

实现：

```text
GazeboPhysicsBackend
JSBSimPhysicsBackend
MuJoCoPhysicsBackend
GenesisPhysicsBackend
FmiPhysicsBackend
SimpleKinematicBackend
```

---

## 10.2 飞控后端接口

```cpp
class IAutopilotBackend {
public:
    virtual void configure(const AutopilotConfig&) = 0;
    virtual void start() = 0;
    virtual void stop() = 0;
    virtual void reset() = 0;

    virtual void pushSensorData(
        const SensorPacket&) = 0;

    virtual ActuatorCommand pullActuatorCommand() = 0;
    virtual AutopilotStatus status() const = 0;

    virtual void sendHighLevelCommand(
        const VehicleCommand&) = 0;
};
```

实现：

```text
PX4SITLBackend
ArduPilotSITLBackend
PX4HardwareBackend
ArduPilotHardwareBackend
DirectControllerBackend
ReplayAutopilotBackend
```

---

## 10.3 通信接口

```cpp
class ITransport {
public:
    virtual void start() = 0;
    virtual void stop() = 0;
    virtual void publish(const Envelope&) = 0;
    virtual Subscription subscribe(
        const Topic&,
        Callback callback) = 0;
};
```

实现：

```text
Ros2Transport
MavlinkTransport
DdsTransport
UdpTransport
TcpTransport
SharedMemoryTransport
InProcessTransport
```

---

## 10.4 渲染器接口

```cpp
class IRendererBackend {
public:
    virtual void connect() = 0;
    virtual void loadWorld(const RenderWorld&) = 0;
    virtual void spawnEntity(const RenderEntity&) = 0;
    virtual void updateState(const EntityState&) = 0;
    virtual void updateAnimation(const AnimationState&) = 0;
    virtual void removeEntity(const EntityId&) = 0;
    virtual void renderFrame(const RenderRequest&) = 0;
};
```

---

## 10.5 算法运行时接口

```cpp
class IAlgorithmRuntime {
public:
    virtual void configure(const AlgorithmConfig&) = 0;
    virtual void reset() = 0;
    virtual void update(
        const AlgorithmInput&,
        AlgorithmOutput&) = 0;
};
```

实现：

```text
NativeCppRuntime
PythonRuntime
Ros2NodeRuntime
SimulinkGeneratedRuntime
FmuRuntime
ReplayRuntime
```

---

# 十一、动力学后端设计

## 11.1 Gazebo 后端

主要负责：

* 多旋翼；
* 机器人传感器；
* 地面车辆；
* 机器狗工程验证；
* 碰撞与环境交互；
* PX4 SITL；
* ROS 2感知规划链。

Gazebo后端内部组件：

```text
GazeboServerManager
GazeboEntityAdapter
GazeboSensorAdapter
GazeboMotorSystem
GazeboFaultSystem
RosGzAdapter
```

---

## 11.2 JSBSim 后端

主要负责：

* 固定翼；
* 喷气模型；
* 鸭式布局；
* 舵面；
* 襟翼；
* 起落架；
* 发动机；
* 空中释放研究；
* ArduPlane SITL。

JSBSim后端不得依赖ROS。

内部组件：

```text
JSBSimExecutive
AircraftModelLoader
PropertyMapper
ControlSurfaceAdapter
ArduPilotAdapter
WeatherAdapter
ReleaseOrchestrator
```

---

## 11.3 MuJoCo 后端

主要负责：

* 高速控制实验；
* 强化学习；
* 机器狗；
* 小车；
* 多旋翼简化动力学；
* 控制器比较。

---

## 11.4 Genesis 后端

主要负责：

* GPU批量训练；
* 多环境强化学习；
* 多物理研究；
* 大规模参数随机化。

---

## 11.5 简化运动学后端

用于：

* 大规模集群；
* 任务分配；
* 编队逻辑；
* 网络拓扑；
* 快速算法测试。

该后端不用于证明真实动力学性能。

---

# 十二、飞控集成

## 12.1 PX4

PX4默认用于：

* 多旋翼；
* 后续可能的VTOL；
* 多旋翼实机部署；
* PX4 SITL和HIL。

接口优先级：

```text
1. uXRCE-DDS / px4_msgs
2. MAVLink / MAVSDK
3. MAVROS兼容层
```

必须处理：

* PX4消息版本匹配；
* 多机命名空间；
* 实例ID；
* 端口；
* Offboard心跳；
* 坐标转换；
* 时间同步；
* 模式和Failsafe。

---

## 12.2 ArduPilot

ArduPilot默认用于：

* 固定翼；
* 涵道航模；
* 地面车辆；
* 部分复合翼。

接口模式：

```text
Standalone:
    ArduPilot + MAVLink

Companion:
    ArduPilot + Native Guidance Process

ROS Integrated:
    ArduPilot + DDS / ROS2

Simulation:
    ArduPilot SITL + JSBSim
```

---

## 12.3 飞控与ROS的关系

飞控独立完成基础稳定与安全控制。

ROS 2负责：

* 感知；
* 定位；
* 规划；
* 任务；
* 协同；
* 高级决策。

ROS 2失效时，飞控仍应能够：

* 保持稳定；
* 进入安全模式；
* 返航或降落；
* 接受人工遥控。

---

# 十三、算法架构

## 13.1 算法核心去中间件化

推荐目录：

```text
autonomy/
├── guidance_core/
├── control_core/
├── planning_core/
├── mapping_core/
├── estimation_core/
└── swarm_core/
```

适配层：

```text
adapters/
├── ros2/
├── mavlink/
├── px4/
├── ardupilot/
├── gazebo/
├── jsbsim/
└── replay/
```

---

## 13.2 标准算法接口

```cpp
struct AlgorithmInput {
    Timestamp timestamp;
    EntityState state;
    SensorBundle sensors;
    MissionTarget target;
};

struct AlgorithmOutput {
    VehicleCommand command;
    AlgorithmDiagnostics diagnostics;
};
```

---

## 13.3 四旋翼自主链

```text
MID360
    ↓
Localization / Fast-LIO
    ↓
Local Map
    ↓
Planner / EGO
    ↓
Trajectory
    ↓
PX4 Adapter
    ↓
PX4
```

---

## 13.4 固定翼自主链

```text
GPS / Airspeed / IMU / Optional Vision
    ↓
Guidance Core
    ↓
Path / Airspeed / Altitude Command
    ↓
ArduPilot Adapter
    ↓
ArduPlane
```

---

## 13.5 异构协同链

```text
Mission Manager
    ↓
Task Allocation
    ↓
Per-Vehicle Goal
    ↓
Vehicle-Specific Planner
    ↓
Vehicle-Specific Controller
```

协调层不得直接生成所有载具的电机或舵面命令。

---

# 十四、ROS 2架构

## 14.1 ROS 2的适用范围

ROS 2主要用于：

* 四旋翼感知和规划；
* 机器狗和小车；
* 多机器人协同；
* 地图和任务共享；
* 工具和可视化；
* 实验控制。

固定翼可以选择是否加入ROS 2。

---

## 14.2 ROS 2节点生命周期

关键节点应使用生命周期：

```text
Unconfigured
    ↓
Inactive
    ↓
Active
    ↓
Finalized
```

适合生命周期管理的组件：

* 传感器；
* 仿真后端；
* 飞控适配器；
* 规划器；
* 地图；
* 记录器；
* UE Bridge。

---

## 14.3 ROS 2组件化

高频、低延迟节点可在同一进程中组件化，例如：

```text
MID360 Preprocess
Fast-LIO Adapter
Local Map
Planner Adapter
```

低信任或可能崩溃的模块保持独立进程。

---

## 14.4 命名空间

统一格式：

```text
/cosim/<experiment_id>/<vehicle_id>/<subsystem>/<topic>
```

例如：

```text
/cosim/exp_001/uav_01/state
/cosim/exp_001/uav_01/sensors/lidar
/cosim/exp_001/uav_01/planning/trajectory
/cosim/exp_001/uav_01/command
```

飞控原始接口放在独立命名空间：

```text
/px4/uav_01/...
/ardupilot/fw_01/...
```

---

# 十五、时间系统

## 15.1 统一仿真时钟

```cpp
struct SimulationClock {
    int64_t sim_time_ns;
    int64_t step_size_ns;
    uint64_t step_id;
    double real_time_factor;
    ClockState state;
};
```

---

## 15.2 时间模式

```text
Realtime
    尽量与现实时间同步

Accelerated
    快于现实时间

Slow Motion
    慢于现实时间

Lockstep
    所有关键模块完成后再推进

Step
    用户手动推进一步

Replay
    按日志时间推进
```

---

## 15.3 调度顺序

推荐一个主步内按以下顺序运行：

```text
1. 获取当前命令
2. 更新飞控
3. 获取执行器输出
4. 推进动力学
5. 生成传感器
6. 更新状态估计
7. 更新控制与规划
8. 记录日志
9. 更新渲染
10. 推进仿真时间
```

实际系统允许多速率运行，但必须保证数据时间戳和因果顺序。

---

## 15.4 多速率调度

示例：

```yaml
rates:
  physics: 1000
  autopilot: 400
  imu: 400
  lidar: 20
  localization: 100
  planner: 20
  mission: 5
  renderer: 60
  logger: 100
```

---

# 十六、坐标系统

## 16.1 平台标准

CoSim内部标准：

```text
全球坐标：
    WGS84 / ECEF

局部世界坐标：
    ENU

平台机体系：
    X前、Y左、Z上

旋转：
    右手四元数
```

---

## 16.2 后端转换

| 系统            | 常见坐标       |
| ------------- | ---------- |
| ROS 2         | ENU / FLU  |
| PX4           | NED / FRD  |
| ArduPilot     | NED及自身机体系  |
| JSBSim        | 地理坐标和航空机体系 |
| Unreal Engine | 左手坐标、厘米    |
| Gazebo        | 右手世界坐标     |
| MuJoCo        | 右手坐标       |

所有转换必须集中实现：

```text
CoordinateTransformService
```

禁止在业务代码中散落坐标轴交换。

---

## 16.3 坐标测试

必须建立以下测试：

* 原点测试；
* 单轴平移；
* 90度滚转；
* 90度俯仰；
* 90度偏航；
* 速度转换；
* 角速度转换；
* 经纬高转换；
* UE厘米和米转换；
* NED和ENU往返误差。

---

# 十七、车辆资产系统

## 17.1 中立参数源

每种车辆维护：

```text
vehicles/<vehicle_name>/
├── manifest.yaml
├── geometry.yaml
├── mass.yaml
├── actuators.yaml
├── aerodynamics.yaml
├── sensors.yaml
├── autopilot.yaml
├── limits.yaml
├── frames.yaml
├── visual/
├── collision/
└── calibration/
```

---

## 17.2 生成目标

从中立参数生成：

```text
Gazebo SDF
MuJoCo MJCF
JSBSim XML
Genesis配置
PX4参数
ArduPilot参数
UE Actor配置
ROS 2传感器配置
```

---

## 17.3 参数分级

每个参数必须标记来源和可信度：

```yaml
mass:
  value: 2.35
  unit: kg
  source: measured
  confidence: high

drag_coefficient:
  value: 0.42
  source: estimated
  confidence: low
```

来源类型：

```text
Manufacturer
CAD
Measured
Identified
PublicReference
Estimated
Default
```

---

## 17.4 参数版本

每次实验必须记录：

```text
vehicle_model_version
parameter_set_version
autopilot_parameter_version
sensor_calibration_version
```

---

# 十八、场景系统

## 18.1 场景清单

```text
scenarios/
├── indoor_lab/
├── outdoor_field/
├── urban/
├── runway/
├── fixedwing_airspace/
├── heterogeneous_test/
└── benchmark/
```

---

## 18.2 场景内容

```yaml
world:
  origin:
  terrain:
  weather:
  wind:
  magnetic_field:
  gravity:

entities:
  vehicles:
  obstacles:
  landmarks:
  targets:
  dynamic_objects:

sensors:
  beacons:
  cameras:
  motion_capture:

events:
  failures:
  disturbances:
  weather_changes:
```

---

## 18.3 场景资产映射

同一场景可具有：

```text
Gazebo Asset
UE Asset
Isaac Asset
Simplified Collision Asset
Map Ground Truth
```

所有版本通过统一场景ID关联。

---

# 十九、实验系统

## 19.1 实验定义

```yaml
experiment:
  id: exp_2026_001
  name: sunray_mid360_avoidance
  seed: 12345
  duration: 180
  clock_mode: lockstep

vehicles:
  - id: uav_01
    profile: sunray150_px4_gazebo

scenario:
  name: indoor_lab

algorithms:
  localization: fast_lio
  planner: ego_planner
  mission: waypoint_sequence

recording:
  rosbag: true
  ulog: true
  core_log: true
  video: true

metrics:
  - trajectory_error
  - collision_count
  - planning_latency
  - minimum_obstacle_distance
```

---

## 19.2 可重复性

每次实验必须记录：

* Git commit；
* 依赖版本；
* 容器镜像；
* 操作系统；
* GPU和CPU；
* 配置文件；
* 随机种子；
* 车辆模型；
* 参数；
* 飞控版本；
* 算法版本；
* 日志路径。

---

## 19.3 实验状态

```text
CREATED
CONFIGURED
STARTING
RUNNING
PAUSED
STOPPING
COMPLETED
FAILED
ABORTED
```

---

# 二十、日志与数据系统

## 20.1 日志类型

```text
CoSim Core Log
ROSBag2
PX4 ULog
ArduPilot BIN Log
Physics Backend Log
Algorithm Diagnostics
UE Video
Dataset Output
```

---

## 20.2 统一实验目录

```text
runs/<experiment_id>/
├── manifest.json
├── config/
├── core/
├── rosbag/
├── px4_ulog/
├── ardupilot_log/
├── backend/
├── metrics/
├── video/
├── dataset/
└── report/
```

---

## 20.3 日志统一时间

所有日志必须记录：

```text
simulation_time
wall_time
source_time
sequence_id
vehicle_id
```

---

## 20.4 回放

回放模式下：

```text
Log Replay Backend
    替代Physics Backend

Recorded State
    驱动UE、RViz和评价工具
```

回放不应要求重新启动 PX4、ArduPilot 或物理引擎。

---

# 二十一、UE显示系统

## 21.1 通信方式

优先级：

```text
1. Shared Memory，本机高频状态
2. UDP，本机或局域网低延迟
3. ROS2，开发与调试
4. gRPC/TCP，可靠控制与管理
```

推荐数据分层：

```text
高频状态：
    UDP / Shared Memory

管理命令：
    TCP / gRPC

ROS调试：
    ROS2 Bridge
```

---

## 21.2 UE实体接口

每个Actor至少接收：

```text
entity_id
asset_id
pose
velocity
animation_state
control_surface_state
lighting_state
effect_state
```

---

## 21.3 动画状态

多旋翼：

```text
rotor_speed
motor_status
landing_gear
gimbal
```

固定翼：

```text
aileron
elevator
rudder
flap
canard
airbrake
landing_gear
engine_state
```

小车：

```text
wheel_rotation
steering
suspension
lights
```

机器狗：

```text
joint_position
foot_contact
gait_state
```

---

# 二十二、故障与扰动系统

## 22.1 故障类型

```text
电机效率下降
电机失效
舵面卡死
舵面效率下降
传感器偏置
传感器丢包
GPS失效
LiDAR噪声
通信延迟
通信中断
风扰
质量变化
质心变化
电池衰减
```

---

## 22.2 故障接口

```cpp
struct FaultEvent {
    EntityId target;
    Timestamp trigger_time;
    FaultType type;
    std::map<std::string, double> parameters;
    Duration duration;
};
```

---

## 22.3 故障注入位置

```text
Physics Fault
Sensor Fault
Actuator Fault
Communication Fault
Autopilot Fault
Algorithm Fault
```

不得把所有故障统一成“修改状态”。

---

# 二十三、安全系统

## 23.1 Safety Supervisor

负责：

* 状态有效性；
* 命令超时；
* 地理围栏；
* 速度和姿态限制；
* 高度限制；
* 控制输入限制；
* 碰撞风险；
* 通信健康；
* 飞控状态；
* 紧急停止；
* 人工接管。

---

## 23.2 命令优先级

```text
Emergency
Manual Override
Safety
Autopilot
Mission
Planner
Background
```

低优先级命令不得覆盖安全和人工接管命令。

---

## 23.3 仿真与实机隔离

所有命令必须包含目标环境：

```text
SIMULATION
HIL
REAL
```

实机命令不得因配置错误发送到仿真实例，反之亦然。

---

# 二十四、部署模式

## 24.1 纯仿真

```text
CoSim Runtime
Physics Backend
SITL
Algorithms
UE
```

---

## 24.2 软件在环

真实飞控软件运行在计算机中：

```text
PX4 SITL / ArduPilot SITL
    ↔
CoSim Physics Backend
```

---

## 24.3 硬件在环

```text
真实飞控硬件
    ↔
CoSim传感器模拟
    ↔
CoSim动力学
```

---

## 24.4 实机模式

```text
真实传感器
真实飞控
真实载具
    ↔
CoSim Mission / Logging / Monitoring
```

实机模式不启动仿真物理，只保留：

* 任务；
* 通信；
  -监控；
* 日志；
* 地面站；
* UE数字孪生显示。

---

# 二十五、运行Profile

## 25.1 多旋翼工程模式

```yaml
profile: sunray150_engineering

vehicle:
  model: sunray150

physics:
  backend: gazebo

autopilot:
  backend: px4_sitl

middleware:
  ros2: enabled

sensors:
  mid360: enabled
  imu: enabled

autonomy:
  localization: fast_lio
  planner: ego_planner

renderer:
  backend: unreal
```

---

## 25.2 固定翼独立模式

```yaml
profile: fixedwing_standalone

vehicle:
  model: generic_canard

physics:
  backend: jsbsim

autopilot:
  backend: arduplane_sitl

middleware:
  ros2: disabled
  mavlink: enabled

renderer:
  backend: unreal
```

---

## 25.3 固定翼高级制导模式

```yaml
profile: fixedwing_guidance

vehicle:
  model: generic_canard

physics:
  backend: jsbsim

autopilot:
  backend: arduplane_sitl

algorithm:
  guidance_core: native_cpp

transport:
  guidance_to_autopilot: mavlink

renderer:
  backend: unreal
```

---

## 25.4 异构协同模式

```yaml
profile: heterogeneous_collaboration

vehicles:
  - id: fw_01
    type: fixedwing
    physics: jsbsim
    autopilot: arduplane
    gateway: mavlink_ros2

  - id: uav_01
    type: multirotor
    physics: gazebo
    autopilot: px4
    gateway: px4_ros2

  - id: rover_01
    type: ground_vehicle
    physics: gazebo
    controller: ros2

  - id: dog_01
    type: quadruped
    physics: mujoco
    controller: native
    gateway: ros2

mission:
  backend: ros2

renderer:
  backend: unreal
```

---

# 二十六、仓库设计

```text
CoSim/
├── README.md
├── LICENSE
├── CMakeLists.txt
├── cmake/
├── docs/
│   ├── architecture/
│   ├── guides/
│   ├── adr/
│   ├── api/
│   └── tutorials/
│
├── core/
│   ├── include/cosim/
│   ├── state/
│   ├── commands/
│   ├── capabilities/
│   ├── time/
│   ├── coordinates/
│   ├── config/
│   ├── events/
│   ├── logging/
│   └── plugin/
│
├── domains/
│   ├── aerial_common/
│   ├── multirotor/
│   ├── fixedwing/
│   ├── ground_vehicle/
│   └── legged/
│
├── backends/
│   ├── gazebo/
│   ├── jsbsim/
│   ├── mujoco/
│   ├── genesis/
│   ├── simple/
│   └── fmi/
│
├── autopilots/
│   ├── px4/
│   ├── ardupilot/
│   ├── direct/
│   └── hardware/
│
├── transports/
│   ├── ros2/
│   ├── mavlink/
│   ├── dds/
│   ├── udp/
│   ├── grpc/
│   └── shared_memory/
│
├── autonomy/
│   ├── guidance/
│   ├── control/
│   ├── localization/
│   ├── mapping/
│   ├── planning/
│   └── swarm/
│
├── renderers/
│   ├── unreal/
│   └── debug/
│
├── vehicles/
│   ├── sunray150/
│   ├── generic_quadrotor/
│   ├── generic_fixedwing/
│   ├── generic_canard/
│   ├── rover/
│   └── quadruped/
│
├── scenarios/
├── profiles/
├── experiments/
├── tools/
├── scripts/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   ├── hil/
│   └── performance/
│
└── third_party/
    └── manifests/
```

---

# 二十七、第三方依赖管理

不建议把所有第三方仓库直接复制到 `References` 后长期手工维护。

建议采用：

```text
third_party/
├── manifest.yaml
├── patches/
├── licenses/
└── lockfiles/
```

每个依赖记录：

```yaml
name: px4
repository:
commit:
license:
purpose:
patches:
update_policy:
```

第三方代码分类：

```text
Runtime Dependency
Build Dependency
Development Tool
Reference Only
Optional Plugin
```

---

# 二十八、版本策略

## 28.1 稳定版本矩阵

每个CoSim版本发布时固定：

```text
ROS 2版本
Gazebo版本
PX4版本
ArduPilot版本
JSBSim版本
MuJoCo版本
UE版本
编译器版本
Python版本
```

---

## 28.2 版本通道

```text
stable
    课程、比赛和正式实验

development
    日常开发

experimental
    Genesis、Isaac、FMI等实验功能
```

---

## 28.3 兼容规则

核心接口使用语义版本：

```text
MAJOR.MINOR.PATCH
```

破坏状态或命令字段时升级 MAJOR。

---

# 二十九、测试体系

## 29.1 单元测试

覆盖：

* 坐标转换；
* 时间；
* 插件加载；
* 配置解析；
* 数据序列化；
* 状态和命令；
* 参数生成。

---

## 29.2 集成测试

覆盖：

```text
Gazebo + PX4
JSBSim + ArduPlane
ROS2 + PX4
MAVLink + ArduPilot
Core + UE
Replay + UE
```

---

## 29.3 回归测试

固定任务：

```text
四旋翼悬停
四旋翼轨迹跟踪
固定翼直线飞行
固定翼转弯
自动起降
MID360点云
局部规划
日志回放
```

每次版本更新自动比较：

* 轨迹误差；
* CPU；
* 内存；
* 实时因子；
* 控制输出；
* 传感器频率；
* 崩溃率。

---

## 29.4 多后端一致性测试

对同一车辆参数和输入，在不同后端中比较：

```text
稳态悬停
阶跃响应
自由落体
固定翼配平
转弯响应
风扰响应
```

多后端不要求完全一致，但差异必须可解释。

---

## 29.5 HIL测试

自动检查：

* 飞控连接；
* 传感器频率；
* 执行器输出；
* 时间同步；
* 超时；
* Failsafe；
* 日志完整性。

---

# 三十、性能指标

## 30.1 核心性能

目标指标：

```text
Core状态路由：
    单机高频状态不成为瓶颈

调度抖动：
    固定步长模式保持可预测

UE显示：
    不阻塞物理仿真

日志：
    异步写盘

多机：
    车辆数量增加时线性或近线性扩展
```

---

## 30.2 第一阶段参考目标

```text
四旋翼物理：
    500 Hz以上

PX4：
    正常SITL频率

MID360：
    10～20 Hz

规划：
    20 Hz目标

UE：
    30～60 FPS

单机实时因子：
    ≥ 1.0

日志丢失：
    关键状态为0
```

这些是工程目标，不是所有设备上的强制保证。

---

# 三十一、开发规范

## 31.1 代码语言

```text
C++：
    Core、Runtime、后端和实时算法

Python：
    实验、训练、工具和自动化

Rust：
    可用于后续高可靠通信或工具

C# / UE C++：
    UE前端

YAML / JSON：
    配置

Protocol Buffers：
    跨进程和网络接口
```

---

## 31.2 禁止事项

禁止：

* 在算法中硬编码 topic；
* 在业务代码中手写坐标转换；
* 把仿真真值直接作为实机接口；
* 把可视网格当作碰撞网格；
* 把UE帧率作为仿真时间；
* 把第三方代码无许可证记录地复制入核心；
* 让平台Core依赖ROS2；
* 让一个实体同时被多个物理后端推进；
* 把实验参数硬编码进启动脚本。

---

# 三十二、实施路线

## 阶段0：架构冻结

完成：

* Core数据模型；
* 插件接口；
* 时间模型；
* 坐标标准；
* 配置格式；
* 仓库结构；
* ADR文档。

---

## 阶段1：四旋翼主链

完成：

```text
Sunray-150
Gazebo
PX4 SITL
ROS2
MID360
Fast-LIO
EGO
Core Log
```

暂时不做完整UE编辑器。

---

## 阶段2：独立UE显示

完成：

```text
Gazebo状态
    ↓
CoSim Renderer Protocol
    ↓
UE Actor
```

支持：

* 断线重连；
* 实时显示；
* 航迹；
* 传感器视锥；
* 日志回放。

---

## 阶段3：固定翼域

完成：

```text
JSBSim
ArduPlane SITL
Generic Fixed Wing
Generic Canard
UE舵面动画
MAVLink Adapter
```

重点验证算法去ROS化。

---

## 阶段4：多后端实验

加入：

```text
MuJoCo
Genesis
Simple Kinematic
```

建立统一Gym环境和批量实验。

---

## 阶段5：小车和机器狗

先完成：

* 状态接口；
* 能力声明；
* ROS2 Gateway；
* UE显示；
* 简单协同。

不立即重写已有控制器。

---

## 阶段6：异构协同

完成：

* Mission Manager；
* Task Allocation；
* Vehicle Registry；
* 状态共享；
* 空地协同；
* 通信仿真；
* 协同评价。

---

## 阶段7：HIL和实机

完成：

```text
PX4 HIL
ArduPilot HIL
Sunray-150实机
固定翼航模
数字孪生显示
统一实验日志
```

---

# 三十三、关键里程碑

## M1：Core Alpha

* 数据模型稳定；
* 插件可动态加载；
* 时钟可运行；
* CLI可启动空实验。

## M2：Quadrotor Alpha

* Sunray-150可在Gazebo飞行；
* PX4闭环；
* ROS2状态和命令可用。

## M3：Perception Alpha

* MID360；
* 定位；
* 地图；
* 规划。

## M4：UE Alpha

* 多旋翼状态同步；
* 高质量显示；
* 日志回放。

## M5：FixedWing Alpha

* JSBSim；
* ArduPlane；
* 舵面；
* 固定翼航点飞行。

## M6：Multi-Backend Beta

* Gazebo、JSBSim、MuJoCo共用Core；
* 统一实验系统。

## M7：Heterogeneous Beta

* 四旋翼、固定翼、小车或机器狗协同运行。

## M8：Deploy Release

* SIL、HIL和实机统一；
* 发布稳定版本矩阵。

---

# 三十四、主要风险

## 34.1 范围失控

风险：

```text
同时开发太多载具
同时维护太多后端
```

措施：

* 每阶段只增加一个新域；
* 核心接口先稳定；
* 实验功能与平台功能分离。

---

## 34.2 参数不可信

措施：

* 参数来源标记；
* 参数版本；
* 台架和飞行数据；
* 参数辨识；
* 多后端对比；
* 不确定性随机化。

---

## 34.3 多后端时间不一致

措施：

* 中央SimulationClock；
* Lockstep；
* sequence_id；
* 时间监控；
* 后端超时策略。

---

## 34.4 坐标错误

措施：

* 中央转换服务；
* 单元测试；
* 可视化坐标轴；
* 禁止业务代码手写转换。

---

## 34.5 第三方版本冲突

措施：

* 版本锁定；
* 容器；
* 兼容矩阵；
* Patch管理；
* CI自动构建。

---

## 34.6 平台过度依赖ROS

措施：

* Core无ROS；
* 算法核心无ROS；
* ROS作为Adapter；
* 固定翼支持纯MAVLink模式。

---

## 34.7 UE与物理耦合

措施：

* UE默认只读状态；
* Renderer协议独立；
* UE断开不影响物理；
* 日志可独立回放。

---

# 三十五、架构决策记录

建议建立：

```text
docs/adr/
```

初始ADR：

```text
ADR-001 CoSim采用模块化多进程架构
ADR-002 CoSim Core不依赖ROS2
ADR-003 每个实体只有一个权威物理后端
ADR-004 平台内部局部世界坐标使用ENU
ADR-005 UE默认只作为Renderer
ADR-006 多旋翼默认使用Gazebo+PX4
ADR-007 固定翼默认使用JSBSim+ArduPlane
ADR-008 算法核心与中间件分离
ADR-009 车辆参数采用中立参数源
ADR-010 实验必须记录完整版本和随机种子
ADR-011 第三方依赖不直接无管理地复制入Core
ADR-012 FMI仅作为后续扩展，不阻塞第一阶段
```

---

# 三十六、第一版最小可行系统

CoSim v0.1 只需要实现：

```text
CoSim Core
    状态
    命令
    时间
    坐标
    配置
    插件
    日志

Gazebo Backend
PX4 SITL Backend
ROS2 Adapter
Sunray-150模型
MID360基础仿真
UE状态显示
CLI实验启动
```

第一版不需要：

```text
完整GUI Studio
固定翼
机器狗
小车
Genesis
Isaac
大规模协同
FMI
完整云服务
```

---

# 三十七、最终架构结论

CoSim 应当是：

```text
一个平台产品
    +
多个车辆领域
    +
多个可替换动力学后端
    +
多个可替换飞控后端
    +
可选ROS2系统总线
    +
独立UE显示前端
    +
统一实验、日志和部署体系
```

四旋翼和固定翼之间：

```text
分开：
    动力学
    飞控
    控制接口
    参数模型
    传感器配置

共享：
    Core
    时间
    坐标
    配置
    场景
    日志
    实验
    UE显示
    任务和协同
```

ROS 2：

```text
不是所有载具的强制基础
而是高级自主和异构协同的系统总线
```

UE：

```text
不是默认物理真值
而是独立、可替换、高质量的显示端
```

CoSim 最终不是一个“大而全的单体仿真器”，而是一个：

> **能够统一组织不同动力学、不同飞控、不同机器人、不同算法、不同仿真层级和真实设备的开放式无人系统开发与验证平台。**
