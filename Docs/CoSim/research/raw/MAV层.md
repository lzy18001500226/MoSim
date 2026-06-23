# 16. MAVLink、MAVROS、QGroundControl、MAVSDK

先把四者的关系彻底钉死：

```text
MAVLink
    通信协议和消息规范

MAVROS
    MAVLink ↔ ROS/ROS 2 的协议网关

MAVSDK
    基于MAVLink封装的高级应用开发SDK

QGroundControl
    基于MAVLink运行的完整地面站应用
```

可以类比为：

```text
MAVLink        = 通信语言
MAVROS         = MAVLink与ROS之间的翻译官
MAVSDK         = 调用飞行器能力的应用程序接口
QGroundControl = 已经制作完成的飞行器控制和配置软件
```

它们不是竞争关系，也不能四选一。CoSim 中很可能四者都会存在，但分别承担不同职责。

---

# 16.1 MAVLink：整个飞控生态的通信协议层

## 16.1.1 MAVLink是什么？

MAVLink 是为无人系统、受限计算平台和低带宽链路设计的二进制消息协议。它同时采用两种通信模式：

```text
遥测状态：
    发布—订阅式连续广播

参数、任务、命令等：
    点对点请求—响应
    必要时确认、超时和重传
```

因此它不是简单的“串口数据格式”，而是一套包含消息、命令、参数、任务、文件、相机、时间同步等子协议的无人系统通信体系。([MAVLink](https://mavlink.io/en/about/overview.html?utm_source=chatgpt.com "Protocol Overview | MAVLink Guide"))

典型链路包括：

```text
飞控 ↔ 地面站
飞控 ↔ 伴随计算机
飞控 ↔ 云端服务器
飞控 ↔ 相机/云台
飞控 ↔ 仿真器
多个飞控 ↔ MAVLink路由器
```

---

## 16.1.2 MAVLink数据包

MAVLink 2数据包主要包含：

```text
Magic
Payload Length
Incompatibility Flags
Compatibility Flags
Sequence Number
System ID
Component ID
Message ID
Payload
Checksum
Optional Signature
```

其中 `seq` 可辅助发现丢包，`sysid` 和 `compid` 标识发送系统与组件，`msgid` 指示消息类型，校验码还能帮助发现两端消息定义不一致。([MAVLink](https://mavlink.io/en/about/overview.html?utm_source=chatgpt.com "Protocol Overview | MAVLink Guide"))

需要明确：

```text
MAVLink只定义消息如何编码和交换

它不固定底层必须使用：
    UART
    USB
    UDP
    TCP
    无线数传
    共享内存
```

所以同一套 MAVLink 消息可以跨串口、局域网、数传电台和仿真 UDP 链路运行。

---

# 16.2 System ID与Component ID

## 16.2.1 System ID

每一个独立 MAVLink 系统必须具有唯一的：

```text
system_id
```

通常一架飞行器对应一个 system：

```text
飞行器1：
    sysid = 1

飞行器2：
    sysid = 2

飞行器3：
    sysid = 3
```

MAVLink 的系统 ID 范围是 1～255；地面站和开发 API 常使用数值区间较高的 ID，例如 255，以降低与飞控冲突的可能。([MAVLink](https://mavlink.io/en/guide/routing.html?utm_source=chatgpt.com "Routing | MAVLink Guide"))

---

## 16.2.2 Component ID

一架飞行器内部又可以具有多个 MAVLink 组件：

```text
sysid = 1
├── autopilot
├── companion computer
├── camera
├── gimbal
├── obstacle avoidance
├── ADS-B receiver
└── payload controller
```

它们共享相同的 `sysid`，但拥有不同的 `compid`。

这意味着 MAVLink 的逻辑模型不是：

```text
一架无人机 = 一个程序
```

而是：

```text
一个系统
    由多个可寻址组件组成
```

这个设计对 CoSim 非常重要，因为后续可以把：

```text
ArduPlane
CoSim Companion
UE Camera
模拟云台
载荷管理器
```

表示为同一架飞行器中的不同组件。

---

# 16.3 MAVLink路由

## 16.3.1 为什么需要路由？

同一架飞行器的 MAVLink 数据通常需要同时提供给：

```text
QGroundControl
MAVSDK应用
MAVROS
CoSim日志系统
调试工具
远程监控端
```

不能让这些程序全部抢占同一个串口。

正确结构是：

```text
                    ┌── QGroundControl
飞控 ── MAVLink ── Router ── MAVSDK
                    ├── MAVROS
                    ├── CoSim Logger
                    └── Remote Station
```

MAVLink网络根据 `sysid`、`compid`、目标字段和已学习到的通道进行消息转发；被转发的数据包原则上不应被重新封装或修改。([MAVLink](https://mavlink.io/en/guide/routing.html?utm_source=chatgpt.com "Routing | MAVLink Guide"))

---

## 16.3.2 CoSim不应使用QGC作为主路由器

QGroundControl具有 MAVLink forwarding 能力，可以把收到的数据继续转发给某个 UDP 端点。([QGroundControl Docs](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/settings_view/telemetry.html?utm_source=chatgpt.com "Telemetry Settings | QGC Guide"))

但不建议形成：

```text
飞控
    ↓
QGroundControl
    ↓
MAVSDK / MAVROS / CoSim
```

因为这样一旦 QGC 关闭，其他链路也会断开。

更合理的是：

```text
飞控
    ↓
mavlink-router
    ├── QGroundControl
    ├── MAVSDK
    ├── MAVROS
    └── CoSim
```

开源 `mavlink-router` 专门用于在串口、UDP、TCP等端点之间转发 MAVLink 数据。([GitHub](https://github.com/mavlink-router/mavlink-router?utm_source=chatgpt.com "GitHub - mavlink-router/mavlink-router: Route mavlink packets between endpoints · GitHub"))

---

## 16.3.3 多机路由设计

建议 CoSim 为每架飞行器明确分配：

```yaml
vehicle_id: fw_01
mavlink:
  system_id: 11
  autopilot_component_id: 1
  companion_component_id: 191
  router_endpoint: udp://127.0.0.1:14611
```

多机时不要只依赖端口区分，还要保证：

```text
每架飞行器sysid唯一
每个组件compid正确
ROS命名空间唯一
SITL实例唯一
日志目录唯一
```

---

# 16.4 MAVLink消息定义与Dialect

## 16.4.1 消息不是手写结构体

MAVLink消息通过 XML 定义：

```text
common.xml
standard.xml
minimal.xml
ardupilotmega.xml
以及其他厂商或项目Dialect
```

再由代码生成器生成 C、C++、Python 等语言的序列化代码。每个 XML 消息集合称为一个 dialect。官方建议优先使用标准 `common.xml` 中已有的消息，而不是创建含义重复的私有消息。([MAVLink](https://mavlink.io/en/index.html?utm_source=chatgpt.com "MAVLink Developer Guide | MAVLink Guide"))

典型关系：

```text
minimal.xml
    最小网络和Heartbeat能力

standard.xml
    多个主流飞控兼容实现的标准定义

common.xml
    主流飞控生态普遍使用的消息

ardupilotmega.xml
    ArduPilot专用扩展
```

---

## 16.4.2 CoSim是否需要自定义Dialect？

可以预留：

```text
cosim.xml
```

但要非常克制。

适合自定义的内容：

```text
CoSim仿真控制事件
故障注入状态
特定载荷状态
实验阶段标识
特殊仿真元数据
```

不应重新定义：

```text
位置
姿态
速度
电池
航点
参数
相机
云台
心跳
```

因为这些已有标准消息。

推荐原则：

```text
标准消息可表达：
    使用common.xml

ArduPilot专有能力：
    使用ardupilotmega.xml

只有CoSim独有且确实要跨MAVLink传输：
    使用cosim.xml
```

CoSim 内部的完整状态总线也不应该全部使用 MAVLink，否则点云、地图、批量仿真状态和大型调试数据会受到消息表达及带宽限制。

---

# 16.5 MAVLink Microservices

这里的 “Microservices” 不是云计算中的容器微服务，而是：

> 建立在一组 MAVLink 消息之上的高层交互协议。

官方定义的典型服务包括：

```text
Heartbeat
Command
Mission
Parameter
FTP
Camera
Gimbal
Time Synchronization
Image Transmission
Terrain
Landing Target
Open Drone ID
High Latency
```

这些协议会定义请求、响应、确认、重传、序号及错误处理方式。([MAVLink](https://mavlink.io/en/services/index.html?utm_source=chatgpt.com "Microservices | MAVLink Guide"))

---

## 16.5.1 Heartbeat

`HEARTBEAT` 用于：

```text
发现系统
识别飞控类型
识别载具类型
识别飞行状态
判断链路是否仍然存在
```

但 MAVLink 本身并不规定 Heartbeat 必须以多少 Hz 发送，也不规定丢失多少帧必须判断断线，这些由具体系统和链路决定。([MAVLink](https://mavlink.io/zh/services/heartbeat.html?utm_source=chatgpt.com "心跳/连接协议 | MAVLink Guide"))

因此 CoSim 应自己配置：

```yaml
heartbeat:
  publish_rate_hz: 1
  warning_timeout_ms: 2500
  disconnect_timeout_ms: 5000
```

---

## 16.5.2 Command Protocol

Command Protocol 适合：

```text
解锁
上锁
起飞
降落
切换飞行模式
执行校准
重启设备
控制相机
```

它使用 `COMMAND_LONG` 或 `COMMAND_INT` 发出命令，并通过 `COMMAND_ACK` 返回接受、拒绝、失败、执行中等状态。该协议提供有确认的命令传输，但不等于任何命令都会被飞控接受；飞控仍会根据状态和安全条件拒绝命令。([MAVLink](https://mavlink.io/en/services/command.html?utm_source=chatgpt.com "Command Protocol | MAVLink Guide"))

---

## 16.5.3 Mission Protocol

Mission Protocol 用于传输：

```text
航点任务
地理围栏
集结点
导航命令
条件命令
动作命令
```

任务由带序号的 Mission Item 构成，并包含上传、下载、清空、设置当前任务项和任务类型等交互。([MAVLink](https://mavlink.io/en/services/mission.html?utm_source=chatgpt.com "Mission (Plan) Protocol | MAVLink Guide"))

对固定翼 ArduPlane 而言，任务协议非常重要，因为大多数稳定的航点、盘旋、返航和自动任务并不需要 ROS。

---

## 16.5.4 Parameter Protocol

Parameter Protocol 用于读取和修改飞控参数。

需要理解：

```text
MAVLink只规定参数如何传输

PX4参数名和ArduPilot参数名：
    并不统一
```

例如同一个“最大倾角”，不同飞控可能采用不同参数名称、单位和作用机制。

这也是为什么 QGroundControl 必须为 PX4 和 ArduPilot 实现不同的固件插件，而不能只靠一套通用参数页面。([QGroundControl Docs](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-dev-guide/firmware_plugin.html?utm_source=chatgpt.com "Plugin Architecture | QGC Guide (v5.0)"))

---

## 16.5.5 Time Synchronization

MAVLink Time Synchronization 用于估计不同组件时钟之间的偏移。([MAVLink](https://mavlink.io/zh/services/timesync.html?utm_source=chatgpt.com "Time Synchronization Protocol v2 | MAVLink Guide"))

但 CoSim 中要区分：

```text
MAVLink TIMESYNC：
    飞控与伴随计算机时间关系

CoSim SimulationClock：
    整个仿真实验的逻辑时间

ROS /clock：
    ROS 2仿真时间

Wall Clock：
    电脑现实时间
```

不能把四者混为一个时间源。

---

# 16.6 MAVLink 2签名与安全边界

MAVLink 2支持消息签名，使接收端能够验证消息是否来自可信来源。([MAVLink](https://mavlink.io/ko/guide/message_signing.html?utm_source=chatgpt.com "Message Signing (Authentication) | MAVLink Guide"))

由此可以得出：

```text
签名主要解决：
    来源认证
    消息完整性
    部分重放防护

签名不等同于：
    数据内容加密
    网络访问控制
    完整系统安全
```

因此不要因为启用了 MAVLink Signing，就认为无线链路中的位置、任务和状态数据自动获得了保密性。

CoSim 实机链还需要考虑：

```text
VPN或加密无线链路
主机防火墙
端口访问限制
密钥管理
命令权限
人工接管
Safety Supervisor
```

---

# 16.7 MAVROS：MAVLink与ROS之间的网关

## 16.7.1 MAVROS是什么？

MAVROS 是一个可扩展的 MAVLink—ROS 网关。当前 ROS 2 分支将 MAVLink 连接、系统抽象和消息翻译组织成 Router、UAS 和插件系统，并通过插件把不同 MAVLink 能力映射为 ROS 2 topic、service 和相关接口。([GitHub](https://github.com/mavlink/mavros?utm_source=chatgpt.com "GitHub - mavlink/mavros: MAVLink to ROS gateway with proxy for Ground Control Station · GitHub"))

基本结构：

```text
飞控
    ↓ MAVLink
MAVROS Router / Connection
    ↓
UAS
    ↓
Plugins
    ├── State
    ├── Local Position
    ├── Global Position
    ├── IMU
    ├── Parameters
    ├── Mission
    ├── Command
    ├── Setpoint Position
    ├── Setpoint Velocity
    └── ...

ROS 2 Topics / Services
```

---

## 16.7.2 Router、UAS与Plugin

### Router

负责：

```text
MAVLink连接
端点管理
消息路由
与地面站代理
```

### UAS

代表一个 MAVLink 无人系统，维护：

```text
目标system id
目标component id
飞控类型
时间同步
坐标转换
系统状态
插件上下文
```

### Plugin

负责一种具体能力的翻译：

```text
MAVLink LOCAL_POSITION_NED
    ↓
ROS Odometry / Pose

ROS Position Setpoint
    ↓
MAVLink SET_POSITION_TARGET_...
```

MAVROS 的价值就在于：不用每个 ROS 节点都重新解析 MAVLink 数据包。

---

# 16.8 MAVROS坐标转换

MAVROS最容易出错、也最重要的部分是坐标转换。

常见关系：

```text
PX4 / ArduPilot：
    NED
    FRD

ROS：
    ENU
    FLU
```

MAVROS会在多个插件中执行：

```text
NED ↔ ENU
FRD ↔ FLU
经纬高 ↔ 地心/局部坐标
```

官方 ROS 2 README 特别列出了 frame conversions 和 GeographicLib 地理坐标数据支持。([GitHub](https://github.com/mavlink/mavros/blob/ros2/mavros/README.md?utm_source=chatgpt.com "mavros/mavros/README.md at ros2 · mavlink/mavros · GitHub"))

这也意味着：

> 不能看到 MAVROS 输出的 x、y、z，就认为它们仍然是飞控原始 NED 数据。

CoSim 应规定：

```text
MAVROS输出：
    进入MavrosAdapter

MavrosAdapter：
    转换为CoSim标准ENU/FLU

业务算法：
    只接触CoSim标准坐标
```

不要让规划器直接依赖某个 MAVROS topic 的历史坐标约定。

---

# 16.9 MAVROS的适用场景

MAVROS特别适合：

```text
ArduPilot与ROS/ROS 2接入
传统MAVLink飞控接入
旧ROS项目迁移
需要完整MAVLink插件生态
需要QGC代理与ROS同时连接
```

对于 PX4 + ROS 2 新项目，CoSim 主线更适合优先：

```text
PX4 uXRCE-DDS
    ↓
px4_msgs
    ↓
ROS 2
```

MAVROS保留用于：

```text
兼容旧系统
MAVLink专用功能
ArduPilot
第三方飞控
通用地面站链路
```

原因不是 MAVROS “不能用”，而是 PX4 原生 DDS 接口更贴近 uORB 数据模型；如果高频状态先转 MAVLink、再转 MAVROS、再转 ROS 2，会增加一层映射和语义转换。

---

# 16.10 MAVROS不应成为CoSim Core

错误结构：

```text
CoSim Core
    直接依赖mavros_msgs
```

正确结构：

```text
CoSim Core
    使用VehicleState / VehicleCommand

MavrosAdapter
    mavros_msgs
        ↕
    CoSim Core Types
```

这样未来可以替换成：

```text
PX4DDSAdapter
ArduPilotDDSAdapter
MAVSDKAdapter
HardwareAdapter
ReplayAdapter
```

而不会影响算法层。

---

# 16.11 QGroundControl：地面站应用

## 16.11.1 QGC负责什么？

QGroundControl 是跨平台地面站，支持 PX4、ArduPilot 以及其他使用 MAVLink 的飞行器，主要能力包括：

```text
固件安装
飞控配置
传感器校准
遥控器配置
飞行模式配置
参数查看与修改
任务规划
地理围栏
集结点
实时飞行监控
多机管理
日志下载
MAVLink Inspector
MAVLink Console
视频与飞行仪表
```

它支持 Windows、Linux、macOS、Android 和 iOS，并以同一套 Qt/QML 代码适配桌面和移动设备。([QGroundControl Docs](https://docs.qgroundcontrol.com/en/?utm_source=chatgpt.com "QGroundControl Guide | QGC Guide"))

---

## 16.11.2 QGC不是仿真器

QGC不会负责：

```text
飞行动力学
传感器物理
点云生成
SLAM
路径规划算法
ROS 2节点调度
多后端仿真时间
UE场景
```

它只通过 MAVLink 与飞行器交互。

所以在 CoSim 中：

```text
CoSim Studio：
    管理仿真实验

QGroundControl：
    管理飞控和飞行任务
```

二者不能合并概念。

---

# 16.12 QGC内部架构

## 16.12.1 Vehicle对象

QGC 中的 `Vehicle` 对象是应用代码与实际飞行器通信的主要接口。固件差异由固件插件隔离，使上层 UI 不必到处判断当前使用的是 PX4 还是 ArduPilot。([QGroundControl Docs](https://docs.qgroundcontrol.com/master/en/qgc-dev-guide/classes/index.html?utm_source=chatgpt.com "Class Hierarchy (high level) | QGC Guide"))

基本关系：

```text
MAVLink Link
    ↓
Vehicle
    ↓
FirmwarePlugin
    ↓
Mission / Parameters / Commands / Telemetry
    ↓
Qt/QML UI
```

---

## 16.12.2 FirmwarePlugin

`FirmwarePlugin` 处理不同飞控对 MAVLink 的不同解释和实现差异，例如：

```text
飞行模式名称
支持的命令
任务行为
参数语义
飞控特有消息
```

MAVLink虽然统一了协议，但 PX4 和 ArduPilot 实现的消息子集、飞行模式和参数体系并不完全相同，因此 QGC 使用插件隔离差异。([QGroundControl Docs](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-dev-guide/firmware_plugin.html?utm_source=chatgpt.com "Plugin Architecture | QGC Guide (v5.0)"))

---

## 16.12.3 AutoPilotPlugin

`AutoPilotPlugin` 主要负责：

```text
飞行器配置页面
传感器校准
机架配置
动力系统配置
参数化设置界面
```

因为 MAVLink没有统一规定不同飞控应该使用哪套参数名称和配置步骤，所以飞控设置页面必须按飞控实现区分。([QGroundControl Docs](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-dev-guide/firmware_plugin.html?utm_source=chatgpt.com "Plugin Architecture | QGC Guide (v5.0)"))

---

## 16.12.4 QGCCorePlugin

`QGCCorePlugin` 用于修改与具体飞行器无关的应用能力，例如：

```text
菜单
品牌
功能启用
UI布局
自定义构建
```

QGC官方推荐通过 `FirmwarePlugin`、`AutoPilotPlugin` 和 `QGCCorePlugin` 制作定制版本，而不是到处修改主代码。([QGroundControl Docs](https://docs.qgroundcontrol.com/master/en/qgc-dev-guide/custom_build/plugins.html?utm_source=chatgpt.com "Custom Build Plugins | QGC Guide"))

---

## 16.12.5 Fact System

QGC Fact System 统一表示：

```text
参数
遥测值
配置值
元数据
单位
最小值
最大值
枚举
显示名称
```

QML控件连接 Fact 和 FactMetaData，就能自动获得单位、范围、枚举及值更新等能力。([QGroundControl Docs](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-dev-guide/fact_system.html?utm_source=chatgpt.com "Fact System | QGC Guide (v5.0)"))

这套设计值得 CoSim Studio 借鉴。

例如 CoSim 参数也可以采用：

```text
ParameterValue
    value
    unit
    minimum
    maximum
    enum
    source
    confidence
    readonly
```

而不是每个配置页面自行解释 YAML 字段。

---

# 16.13 CoSim要不要Fork QGroundControl？

第一阶段：**不要。**

建议直接使用官方 QGC：

```text
PX4配置
ArduPilot配置
任务规划
飞控调试
日志下载
MAVLink检查
```

CoSim自己开发：

```text
仿真后端管理
场景配置
车辆资产
实验编排
算法选择
ROS 2状态
UE显示
批量测试
评价报告
```

---

## 16.13.1 什么时候才考虑定制QGC？

只有明确需要以下能力时：

```text
CoSim品牌版本
特定航模配置向导
简化操作界面
特定载荷页面
定制飞控参数页面
特殊任务编辑器
```

再考虑 QGC Custom Build。

QGC当前源码采用 Apache 2.0 与 GPLv3 双许可证体系；制作和分发定制版本前需要按实际链接方式、Qt组件和发布形式审核许可证。([QGroundControl Docs](https://docs.qgroundcontrol.com/master/en/qgc-dev-guide/?utm_source=chatgpt.com "QGroundControl Dev Guide (Daily Builds) | QGC Guide"))

---

# 16.14 MAVSDK：高级MAVLink应用SDK

## 16.14.1 MAVSDK解决什么问题？

直接使用 MAVLink 时，开发者需要自己处理：

```text
连接
系统发现
消息发送
消息订阅
命令确认
超时
重试
任务上传
参数请求
数据速率
异步回调
```

MAVSDK 在 MAVLink 之上提供面向能力的高级 API：

```text
Action
Telemetry
Mission
MissionRaw
Param
Offboard
Camera
Gimbal
Geofence
FTP
LogFiles
Shell
TrackingServer
Transponder
```

MAVSDK 当前核心使用 C++ 实现，并通过插件提供不同飞行器能力。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/index.html?utm_source=chatgpt.com "MAVSDK C++ Library | MAVSDK Guide"))

---

## 16.14.2 MAVSDK基础结构

```text
Application
    ↓
MAVSDK Plugin
    ↓
System
    ↓
MAVSDK Core
    ↓
MAVLink Connection
    ↓
Vehicle
```

`System` 对象表示发现到的 MAVLink 系统，应用根据需要创建：

```cpp
Telemetry telemetry{system};
Action action{system};
Mission mission{system};
```

同一应用可以为同一个系统同时使用多个插件。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/guide/using_plugins.html?utm_source=chatgpt.com "Managing Systems/Vehicles (Using Plugins) | MAVSDK Guide"))

---

## 16.14.3 Telemetry Plugin

Telemetry提供：

```text
位置
姿态
速度
角速度
加速度
GPS
电池
飞行模式
健康状态
固定翼指标
距离传感器
执行器状态
```

并提供同步和异步接口，许多遥测项还可请求特定数据更新频率。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/guide/telemetry.html?utm_source=chatgpt.com "Telemetry | MAVSDK Guide"))

这非常适合：

```text
CoSim Vehicle Monitor
自动化测试
实机状态监控
非ROS伴随程序
日志采集
```

---

## 16.14.4 Action Plugin

Action用于：

```text
Arm
Disarm
Takeoff
Land
Return to Launch
Kill
Reboot
```

这类离散飞行动作。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/guide/taking_off_landing.html?utm_source=chatgpt.com "Actions (Take-off, Landing, Arming, etc) | MAVSDK Guide"))

它适合表达：

```text
“执行一次起飞操作”
```

不适合表达：

```text
“以100 Hz连续跟踪这条轨迹”
```

---

## 16.14.5 Mission与MissionRaw

`Mission` 提供简化的跨平台任务API，例如：

```text
航点
高度
速度
相机动作
云台动作
```

`MissionRaw` 则更接近完整 MAVLink Mission Item，可以访问更广泛的飞控命令和字段。官方文档建议，需要完整 MAVLink 任务能力时使用 MissionRaw。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/guide/general_usage.html?utm_source=chatgpt.com "MAVSDK Paradigms/Usage | MAVSDK Guide"))

对固定翼 ArduPlane，MissionRaw通常比高度简化的 Mission API 更有价值，因为固定翼任务可能包含：

```text
盘旋
航向
空速
起飞
降落
条件命令
飞控专有命令
```

---

## 16.14.6 Offboard Plugin

MAVSDK当前 Offboard 插件主要面向 PX4 的多旋翼和 VTOL，支持速度及航向类 setpoint；官方文档明确指出，它目前不支持 PX4 固定翼 Offboard。插件会自动以20 Hz重发 setpoint，以满足 PX4 对连续 setpoint 的要求。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/guide/offboard.html?utm_source=chatgpt.com "Offboard Control | MAVSDK Guide"))

因此：

```text
MAVSDK Offboard：
    不是通用固定翼制导接口
```

CoSim固定翼 + ArduPlane更适合采用：

```text
Mission / MissionRaw
GUIDED模式相关MAVLink接口
ArduPilot专用消息
自定义伴随计算机Adapter
```

而不是硬套 MAVSDK Offboard。

---

# 16.15 MAVSDK Client Plugins与Server Plugins

## 16.15.1 Client Plugin

普通插件通常扮演客户端：

```text
MAVSDK应用
    请求飞控执行动作
    请求参数
    请求遥测
    上传任务
```

---

## 16.15.2 Server Plugin

MAVSDK还提供 Server Plugin，使非传统飞控系统、伴随计算机、相机、云台或其他组件能够对外提供 MAVLink 服务。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/server_plugins.html?utm_source=chatgpt.com "Server Plugins | MAVSDK Guide"))

例如 CoSim 可以模拟一个相机组件：

```text
QGroundControl
    ↓ Camera Protocol
CoSim Virtual Camera Component
    ↓
UE Camera
```

或者模拟一个简单飞行器：

```text
MAVSDK Server
    对外发布Heartbeat、Telemetry、Mission服务
```

这对 CoSim 虚拟载荷和仿真组件非常有价值。

---

# 16.16 MAVSDK多语言结构

MAVSDK的核心 MAVLink 实现位于 C++；部分其他语言接口通过 `mavsdk_server` 暴露的 gRPC API 和自动生成的绑定实现。([MAVSDK](https://mavsdk.mavlink.io/main/en/cpp/contributing/plugins.html?utm_source=chatgpt.com "Writing Plugins | MAVSDK Guide"))

简化结构：

```text
Python Application
    ↓ Generated Python API
gRPC
    ↓
mavsdk_server
    ↓
MAVSDK C++
    ↓
MAVLink
```

C++程序则可以直接链接 MAVSDK Core，不需要额外 gRPC 进程。

因此 CoSim 中：

```text
实时C++ Gateway：
    直接使用MAVSDK C++

Python实验脚本：
    可使用MAVSDK-Python

极低层自定义协议：
    使用MavlinkDirect或生成的MAVLink库
```

MAVSDK 当前推荐使用 `MavlinkDirect` 扩展未被高层插件覆盖的 MAVLink 能力；旧 `MavlinkPassthrough` 已被标记为将逐步弃用。([GitHub](https://github.com/mavlink/MAVSDK?utm_source=chatgpt.com "GitHub - mavlink/MAVSDK: API and library for MAVLink compatible systems written in C++ 20 · GitHub"))

---

# 16.17 MAVSDK与MAVROS的区别

这是最容易混淆的部分。

| 维度                | MAVROS              | MAVSDK                |
| ------------------- | ------------------- | --------------------- |
| 本质                | MAVLink与ROS的网关  | MAVLink高级应用SDK    |
| 主要用户            | ROS节点             | C++、Python等应用程序 |
| 输出形式            | ROS topic、service  | 函数、回调、异步API   |
| 是否需要ROS         | 需要                | 不需要                |
| 坐标转换            | 大量内置NED/ENU转换 | API按插件定义         |
| 适合感知规划        | 很适合ROS生态       | 需自行组织算法        |
| 适合小型伴随程序    | 较重                | 很合适                |
| 适合自动化测试      | 可以，但较复杂      | 很合适                |
| 适合固定翼无ROS部署 | 不适合              | 较适合                |
| 原始MAVLink扩展     | 插件或消息接口      | MavlinkDirect         |
| 多种ROS算法集成     | 强                  | 弱                    |
| 飞控高层管理        | 中等                | 强                    |

简单判断：

```text
程序已经是ROS 2系统：
    使用MAVROS或飞控原生DDS

程序不需要ROS：
    使用MAVSDK

只想直接解析MAVLink：
    使用生成的MAVLink库或pymavlink
```

---

# 16.18 MAVSDK与QGroundControl的区别

```text
QGroundControl：
    给人使用

MAVSDK：
    给程序使用
```

例如：

```text
用户点击“起飞”
    → QGroundControl

CoSim自动测试脚本执行100次起飞
    → MAVSDK
```

```text
用户手动规划航点
    → QGroundControl

程序自动生成并上传任务
    → MAVSDK
```

```text
人工查看参数
    → QGroundControl

CI检查参数是否正确
    → MAVSDK
```

CoSim不应通过模拟鼠标操作 QGC 来实现自动化，而应该直接使用 MAVSDK 或底层 MAVLink API。

---

# 16.19 四者在CoSim中的推荐职责

## MAVLink

定位：

```text
飞控、地面站、伴随计算机和载荷之间的标准边缘协议
```

使用场景：

```text
PX4 / ArduPilot ↔ QGC
ArduPlane ↔ Guidance Computer
飞控 ↔ CoSim HIL
虚拟相机/云台
远程遥测
```

---

## MAVROS

定位：

```text
通用MAVLink飞控接入ROS 2的兼容网关
```

优先用于：

```text
ArduPilot + ROS 2
第三方MAVLink飞控
旧ROS算法迁移
需要MAVROS插件生态的系统
```

不作为：

```text
CoSim Core数据模型
PX4 ROS 2新系统唯一通道
```

---

## QGroundControl

定位：

```text
飞控配置、任务规划、人工监控和调试地面站
```

负责：

```text
固件
参数
校准
任务
飞行模式
飞控日志
MAVLink调试
```

不负责：

```text
CoSim实验编排
ROS 2算法管理
点云和地图
仿真后端管理
批量实验
```

---

## MAVSDK

定位：

```text
CoSim原生非ROS飞控应用SDK
```

优先用于：

```text
固定翼伴随计算机
自动化测试
实机状态采集
任务上传
起飞降落控制
飞控健康检查
飞行器注册
MAVLink Gateway
```

---

# 16.20 CoSim建议通信架构

## 16.20.1 PX4多旋翼模式

```text
                          ┌── QGroundControl
PX4 ── MAVLink ── Router ├── MAVSDK Test Service
                          └── MAVLink Logger

PX4 ── uXRCE-DDS ── ROS 2
                       ├── Fast-LIO
                       ├── EGO-Planner
                       ├── Mission Manager
                       └── CoSim ROS Adapter
```

原则：

```text
高频自主系统数据：
    DDS / ROS 2

地面站、任务、参数和兼容工具：
    MAVLink
```

---

## 16.20.2 ArduPlane固定翼独立模式

```text
                          ┌── QGroundControl
ArduPlane ── MAVLink ── Router
                          ├── MAVSDK Guidance Gateway
                          └── CoSim Logger
```

此模式不需要 ROS 2。

---

## 16.20.3 ArduPlane协同模式

```text
ArduPlane
    ↓ MAVLink
MAVSDK / MAVROS Gateway
    ↓ CoSim VehicleState
ROS 2 Mission Bus
    ↓
异构协同系统
```

这样固定翼飞行端可以保持轻量，而系统侧仍然进入 ROS 2 协同网络。

---

## 16.20.4 HIL模式

```text
真实飞控
    ↓ MAVLink / Serial / UDP
MAVLink Router
    ├── QGroundControl
    ├── CoSim HIL Adapter
    ├── MAVSDK Monitor
    └── Logger

CoSim HIL Adapter
    ↔ Physics Backend
```

需要明确：

```text
QGC：
    人工监控

MAVSDK：
    自动检查与管理

CoSim HIL Adapter：
    仿真传感器和执行器闭环

Router：
    链路分发
```

---

# 16.21 CoSim内部接口设计

建议不要让 Core 暴露原始 MAVLink 类型。

## 16.21.1 飞控网关

```cpp
class IAutopilotGateway {
public:
    virtual void connect() = 0;
    virtual void disconnect() = 0;

    virtual AutopilotStatus status() const = 0;
    virtual VehicleState vehicleState() const = 0;

    virtual CommandResult sendCommand(
        const VehicleCommand&) = 0;

    virtual ParameterResult getParameter(
        const std::string& name) = 0;

    virtual ParameterResult setParameter(
        const ParameterValue&) = 0;

    virtual MissionResult uploadMission(
        const Mission&) = 0;
};
```

实现：

```text
MavsdkAutopilotGateway
MavrosAutopilotGateway
Px4DdsAutopilotGateway
ArduPilotDdsAutopilotGateway
ReplayAutopilotGateway
```

---

## 16.21.2 保留原始协议通道

虽然平台使用统一数据类型，但必须保留：

```text
RawMavlinkChannel
```

用途：

```text
调试未知消息
转发自定义Dialect
连接QGC
协议抓包
兼容尚未映射的能力
```

统一接口和原始接口应同时存在：

```text
标准功能：
    使用CoSim VehicleState / Command

飞控专有功能：
    使用Raw MAVLink或扩展Adapter
```

---

# 16.22 MAVLink日志设计

CoSim需要同时记录：

```text
原始MAVLink字节流
解析后的消息
标准化VehicleState
命令与ACK
连接状态
丢包和延迟
sysid/compid
端点来源
```

建议：

```text
runs/<experiment_id>/mavlink/
├── raw.tlog
├── parsed.mcap
├── routing.jsonl
├── commands.jsonl
└── link_metrics.csv
```

QGC常用 `.tlog` 记录 MAVLink 遥测，而飞控内部则仍使用 PX4 ULog 或 ArduPilot BIN Log。不同日志必须通过同一个实验 ID 和统一时间基准关联。

---

# 16.23 关键设计禁区

## 不要把MAVLink当ROS 2替代品

MAVLink适合：

```text
飞控遥测
任务
参数
命令
低带宽状态
```

不适合成为：

```text
MID360完整点云总线
大规模地图传输
高分辨率多相机内部总线
复杂机器人组件发现系统
GPU批量仿真状态总线
```

---

## 不要把ROS 2消息直接等同MAVLink消息

两边语义可能不同：

```text
坐标系不同
时间不同
单位不同
有效性不同
状态机不同
更新频率不同
```

必须经过 Adapter。

---

## 不要把QGC作为平台后端

QGC退出不能导致：

```text
飞控与CoSim断线
日志停止
算法停止
仿真停止
```

---

## 不要让多个程序同时无管理地发送控制命令

例如：

```text
QGC
MAVSDK
MAVROS
ROS 2 Planner
```

同时控制一架飞机，会产生命令竞争。

CoSim必须建立：

```text
Command Authority Manager
```

明确当前谁拥有控制权：

```text
MANUAL
QGC
MISSION
ROS2_PLANNER
MAVSDK_GUIDANCE
SAFETY
EMERGENCY
```

---

## 不要轻易自定义MAVLink消息

自定义 Dialect 会引入：

```text
代码生成版本
QGC兼容
MAVROS兼容
MAVSDK兼容
飞控固件同步
日志解析同步
```

只有无法用标准消息表达的能力才创建自定义消息。

---

# 16.24 推荐目录

```text
CoSim/
├── protocols/
│   └── mavlink/
│       ├── dialects/
│       │   └── cosim.xml
│       ├── generated/
│       ├── router/
│       └── tests/
│
├── transports/
│   ├── mavlink/
│   │   ├── connection/
│   │   ├── routing/
│   │   ├── logging/
│   │   └── raw_channel/
│   │
│   └── ros2/
│
├── gateways/
│   ├── mavsdk/
│   ├── mavros/
│   ├── px4_dds/
│   └── ardupilot_dds/
│
├── ground_control/
│   ├── qgc_profiles/
│   ├── parameter_sets/
│   └── mission_templates/
│
└── tools/
    ├── mavlink_inspector/
    ├── link_monitor/
    └── log_converter/
```

---

# 16.25 最小研究任务

```text
1. 阅读MAVLink 2数据包格式
2. 理解sysid和compid
3. 理解Heartbeat
4. 理解Command与COMMAND_ACK
5. 理解Mission Protocol
6. 理解Parameter Protocol
7. 理解Time Synchronization
8. 理解Dialect与代码生成
9. 跑通mavlink-router
10. 同时连接QGC和MAVSDK
11. 记录并分析tlog
12. 跑通MAVROS ROS 2
13. 追踪一个MAVLink状态到ROS topic
14. 追踪一个ROS setpoint到MAVLink消息
15. 验证NED/ENU和FRD/FLU转换
16. 使用MAVSDK读取Telemetry
17. 使用MAVSDK执行Action
18. 使用MAVSDK上传Mission
19. 测试MissionRaw
20. 测试多飞行器sysid隔离
21. 建立Command Authority Manager
22. 建立CoSim统一AutopilotGateway
23. 建立原始MAVLink日志
24. 写MAVLink-Toolchain REVIEW.md
```

---

# 16.26 最终选型结论

```text
MAVLink：
    必须进入CoSim
    作为飞控和外部设备边缘协议

MAVROS：
    可选进入
    作为ROS 2兼容网关
    尤其适合ArduPilot和传统MAVLink系统

QGroundControl：
    直接使用官方版本
    作为飞控地面站
    不替代CoSim Studio

MAVSDK：
    必须重点使用
    作为非ROS应用、自动化测试和固定翼伴随程序的高级API

mavlink-router：
    建议作为标准基础设施
    统一连接飞控、QGC、MAVSDK、MAVROS和日志系统
```

最终关系：

```text
                        QGroundControl
                              ↑
                              │
PX4 / ArduPilot ←→ MAVLink Router ←→ MAVSDK Gateway
                              │
                              ├── MAVROS / ROS 2
                              ├── CoSim Logger
                              └── Remote Ground Station
```

一句话总结：

> **MAVLink负责让飞控和外部系统说同一种语言，MAVROS负责把这种语言翻译进ROS，MAVSDK负责让程序以高级API控制飞行器，QGroundControl则负责让人配置、规划和监控飞行器。CoSim应同时支持四者，但不能把任何一个等同于整个平台：MAVLink是边缘协议，MAVROS和MAVSDK是适配手段，QGC是人工地面站，CoSim Core仍保持协议和中间件无关。**
>
