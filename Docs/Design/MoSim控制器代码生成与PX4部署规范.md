
# MoSim控制器代码生成与PX4部署规范

> 文档编号：MoSim-CTRL-07
> 文档名称：MoSim控制器代码生成与PX4部署规范
> 适用项目：MoSim四旋翼多领域建模、控制与联合仿真平台
> 当前版本：V0.1 Draft
> 依赖文档：
>
> * MoSim-CTRL-01《MoSim控制体系总览》
> * MoSim-CTRL-02《MoSim统一控制接口规范》
> * MoSim-CTRL-03《MoSim单机控制器实现规范》
> * MoSim-CTRL-04《MoSim控制增强与容错规范》
> * MoSim-CTRL-06《MoSim控制器管理与配置规范》
> * MoSim-CTRL-08《MoSim控制系统测试与评价规范》

---

# 0. 当前阶段代码生成冻结

当前代码生成主线只服务于：

```text
PX4CTRL Golden Vertical Slice
```

当前不做完整 PX4 Module 板载部署，不做 BODY_RATE_THRUST/WRENCH/ROTOR_* 代码回灌。

当前顺序：

```text
原始px4ctrl运行
→ 上游与Sunray差异审计
→ 抽取px4ctrl_core
→ core离线对齐
→ MWORKS重建px4ctrl_core
→ MWORKS模型离线对齐
→ 生成标准C代码
→ 四方离线一致性
→ 接回同一Sunray/ROS包装层
→ Gazebo闭环A/B一致性
```

四方一致性对象：

```text
A. 原始px4ctrl
B. 抽取后的C++ core
C. MWORKS Sysblock模型
D. MWORKS生成C代码
```

强制规则：

```text
离线一致性未通过，不允许进入Gazebo闭环。
生成代码不得直接依赖ROS、MAVROS、PX4或Gazebo类型。
推力比较使用物理总推力N，不使用内部0~1油门值。
```

---

# 1. 文档目的

本文档规定MoSim控制器从MWORKS模型设计、仿真验证、嵌入式代码生成，到ROS 1、PX4 SITL、PX4板载Module、HITL和真实飞控部署的完整技术流程。

本规范重点解决以下问题：

```text
MWORKS生成的控制器代码如何组织
生成代码如何避免依赖MWORKS运行环境
控制器如何接入PX4 uORB
不同控制层级如何映射到PX4
控制器如何编译进不同飞控板固件
参数如何进入PX4参数系统和QGroundControl
多个控制器如何共存、切换和降级
如何保证MWORKS模型、生成代码和PX4运行结果一致
```

本规范不规定PID、SE(3)、DFBC、MPC、NMPC等算法的具体控制律，而是规定其代码生成、包装、构建、部署和运行契约。

---

# 2. 总体技术路线

MoSim控制器部署链路统一设计为：

```text
MWORKS.Sysblock控制模型
        ↓
模型级仿真和测试
        ↓
生成标准C算法代码
        ↓
MoSim Codegen Normalizer
代码规范化与接口封装
        ↓
MoSim Controller Core
平台无关控制器核心
        ↓
┌──────────────┬──────────────┬──────────────┐
│ MWORKS Adapter│ ROS 1 Adapter│ PX4 Adapter  │
└──────────────┴──────────────┴──────────────┘
                                      ↓
                              PX4 uORB Module
                                      ↓
                           姿态/角速度/力矩/电机
                                      ↓
                          Gazebo / HITL / 真机
```

核心原则：

> **控制算法只生成一次，运行平台通过适配器替换，不为MWORKS、ROS和PX4分别维护三套算法。**

---

# 3. 系统分层

MoSim代码生成与部署体系分为六层。

## 3.1 模型层

包含：

```text
Sysblock控制器模型
数据字典
控制器参数
控制器内部状态
输入输出总线
测试用例
代码生成配置
```

## 3.2 生成代码层

包含：

```text
控制器初始化函数
控制器单周期函数
控制器复位函数
参数结构体
状态结构体
输入结构体
输出结构体
生成代码追溯信息
```

## 3.3 平台无关核心层

对生成代码进行统一包装，形成：

```text
IController
ControllerInput
ControllerCommand
ControllerStatus
ControllerCapability
```

## 3.4 PX4适配层

负责：

```text
uORB订阅
uORB发布
参数读取
坐标转换
推力映射
时间戳处理
数据有效性检查
状态机与安全检查
```

## 3.5 PX4运行与管理层

包含：

```text
mosim_control_server
mosim_controller_manager
轻量控制器插件
重型控制器Worker
控制输出仲裁器
故障与降级管理
```

## 3.6 构建与发布层

包含：

```text
CMake
Kconfig
px4board配置
module.yaml
Airframe启动脚本
CI构建
固件打包
版本和哈希记录
```

---

# 4. 部署模式

MoSim控制器支持四种部署模式。

## 4.1 模式A：MWORKS内部模型运行

```text
MWORKS控制器模型
        ↓
MWORKS四旋翼动力学模型
```

用途：

```text
控制算法设计
参数整定
快速迭代
消融实验
批量测试
```

该模式不涉及ROS、uORB或PX4。

---

## 4.2 模式B：ROS 1外部控制器

```text
MWORKS生成代码
        ↓
MoSim ROS 1 Wrapper
        ↓
MAVROS / MAVLink
        ↓
PX4 Offboard
        ↓
PX4内环
```

用途：

```text
px4ctrl复现
生成代码快速接入Gazebo
不修改PX4固件的早期验证
规划器—控制器联合仿真
```

该模式适合第一阶段验证，但不是最终板载部署形式。

---

## 4.3 模式C：PX4内部Module

```text
MWORKS生成代码
        ↓
MoSim Controller Core
        ↓
PX4 mosim_control_server
        ↓
uORB
        ↓
PX4剩余控制环和执行器
```

用途：

```text
PX4 SITL
真实飞控板
HITL
最终嵌入式部署
低延迟控制
```

---

## 4.4 模式D：PX4外置Module目录

MoSim控制器源码和生成代码保存在PX4源码树之外：

```text
MoSim/PX4External/
```

构建时通过：

```text
EXTERNAL_MODULES_LOCATION
```

加入PX4固件。

该模式作为MoSim正式推荐模式，理由是：

```text
MoSim代码与PX4上游代码解耦
便于升级PX4版本
避免大量修改PX4主仓库
便于竞赛作品独立开源
便于生成不同控制器固件
便于维护版权和第三方许可证
```

---

# 5. 推荐总体架构

不建议为每个控制器创建一个直接发布PX4标准控制Topic的独立Module。

推荐架构：

```text
                  ┌─ PID Controller Core
                  ├─ PX4 Native Adapter
                  ├─ px4ctrl Controller Core
                  ├─ SE3 Controller Core
Trajectory ──────►├─ DFBC Controller Core
State ───────────►├─ LMPC Controller Core
                  ├─ NMPC Controller Worker
                  └─ Fault-Tolerant Controller
                              ↓
                    Controller Candidate
                              ↓
                   mosim_controller_manager
                              ↓
                  唯一最终控制命令发布者
                              ↓
             PX4标准uORB控制设定值Topic
```

核心要求：

> **同一PX4标准控制Topic在同一时刻只能由一个MoSim最终发布者控制。**

---

# 6. Module划分

## 6.1 mosim_control_server

负责轻量控制器的加载和运行。

适合承载：

```text
PID
改进PID
LQR/LQI
Backstepping
SMC
SO(3)
SE(3)
DFBC
轻量LMPC
控制增强模块
```

职责：

```text
订阅统一状态和参考
调用选定控制器
生成候选控制命令
发布MoSim内部候选消息
记录控制器状态
```

---

## 6.2 mosim_nmpc_worker

用于计算量大或运行时间不确定的控制器：

```text
NMPC
鲁棒MPC
自适应MPC
iLQR
MPPI
复杂QP控制器
```

该模块不得直接发布PX4最终控制Topic。

它只发布：

```text
mosim_controller_candidate
```

交由Controller Manager仲裁。

---

## 6.3 mosim_controller_manager

负责：

```text
控制器选择
输出合法性检查
超时检查
控制权限仲裁
无扰切换
故障降级
最终限幅
最终uORB发布
```

它是PX4标准控制Topic的唯一MoSim发布者。

---

## 6.4 mosim_frame_adapter

负责：

```text
NED ↔ ENU
FRD ↔ FLU
四元数转换
航向角转换
角速度和力矩转换
```

---

## 6.5 mosim_thrust_mapper

负责：

```text
物理推力N
        ↓
归一化PX4推力
```

考虑：

```text
飞行器质量
最大推力
悬停油门
电池电压
执行器效率
在线推力辨识
```

---

## 6.6 mosim_fault_manager

负责：

```text
执行器效率估计
故障检测
故障隔离
故障状态发布
故障控制配置切换
控制分配重构
```

---

# 7. 为什么不把所有控制器都做成独立PX4 Module

如果每个控制器独立发布：

```text
vehicle_attitude_setpoint
vehicle_rates_setpoint
vehicle_torque_setpoint
actuator_motors
```

会产生以下问题：

```text
多个发布者争用同一Topic
切换时命令不连续
控制器无法统一降级
参数命名重复
日志难以区分
多个控制器同时占用CPU
前端难以准确控制当前算法
```

因此MoSim采用：

```text
多个算法核心
        ↓
统一运行服务器或Worker
        ↓
统一Controller Manager
        ↓
一个最终PX4发布者
```

---

# 8. MWORKS模型代码生成要求

## 8.1 控制器必须位于Sysblock

用于产品级嵌入式代码生成的控制算法必须建立在：

```text
MWORKS.Sysblock
```

中。

Sysplorer多领域模型可以用于动力学和系统仿真，但准备部署的控制器应封装成Sysblock可生成代码的算法子系统。

---

## 8.2 生成代码边界

MWORKS只生成：

```text
控制算法计算
控制器内部状态更新
滤波器和观测器
控制器参数结构
数值求解逻辑
```

MWORKS不生成：

```text
uORB通信
ROS Topic
MAVLink通信
PX4参数服务器
PX4 Module状态机
解锁和模式切换
日志系统
故障回退状态机
启动脚本
Kconfig
```

以上功能由MoSim包装层实现。

---

## 8.3 统一入口函数

每个生成控制器必须最终提供：

```c
int32_t <controller>_initialize(
    <controller>_Context* context,
    const <controller>_Parameters* parameters);

int32_t <controller>_reset(
    <controller>_Context* context,
    const <controller>_Input* input);

int32_t <controller>_step(
    <controller>_Context* context,
    const <controller>_Input* input,
    <controller>_Output* output);

int32_t <controller>_terminate(
    <controller>_Context* context);
```

禁止只生成全局无参函数：

```c
void model_initialize(void);
void model_step(void);
```

若生成器默认使用该形式，必须由Normalizer生成实例化包装器。

---

## 8.4 上下文实例化

所有控制器内部状态必须存入：

```c
ControllerContext
```

禁止依赖不可复制的全局状态。

正确形式：

```c
typedef struct {
    float integrator_x;
    float integrator_y;
    float integrator_z;

    float filter_state[6];
    float observer_state[12];

    uint8_t initialized;
} MosimPidContext;
```

这样才能支持：

```text
多架无人机
多个控制器影子运行
相同控制器多实例
离线并行仿真
单元测试
```

---

## 8.5 固定尺寸内存

生成代码必须满足：

```text
固定尺寸数组
固定预测时域上限
固定状态维数
固定输入维数
无运行时malloc
无运行时new
无可变长数组
无递归
```

MPC和NMPC必须在构建时确定最大维数。

---

## 8.6 禁止项

单周期函数内禁止：

```text
文件读写
控制台输出
网络通信
线程创建
睡眠
阻塞等待
动态内存分配
异常抛出
非确定性随机数
环境变量访问
系统时间访问
```

---

## 8.7 数值类型

MoSim支持两种构建Profile：

```text
MODEL_DOUBLE
TARGET_FLOAT
```

### MODEL_DOUBLE

用于：

```text
MWORKS模型验证
离线高精度对照
理论计算
```

### TARGET_FLOAT

用于：

```text
PX4板载控制
STM32飞控
资源受限硬件
```

每个控制器必须通过float与double一致性测试。

禁止一个控制器部分模块使用float，另一部分无明确理由地使用double。

---

## 8.8 时间步长

控制器不得自行读取系统时间。

时间步长由外部传入：

```c
input->dt_s
input->sample_time_us
```

控制器必须检测：

```text
dt ≤ 0
dt过小
dt过大
时间回退
```

异常时返回明确错误码。

---

## 8.9 输入输出单位

生成代码核心统一使用：

```text
ENU世界坐标系
FLU机体坐标系
SI单位
物理推力N
物理力矩N·m
电机转速rad/s
四元数[w,x,y,z]
```

禁止生成代码直接使用：

```text
PX4 NED
PX4 FRD
归一化油门
PWM
DShot
```

这些由PX4适配层转换。

---

# 9. 数据字典规范

MWORKS数据字典必须分为：

```text
AlgorithmParameters
VehicleParameters
ActuatorParameters
NumericalParameters
BuildParameters
```

## 9.1 AlgorithmParameters

例如：

```text
位置增益
速度增益
姿态增益
角速度增益
积分限幅
观测器增益
MPC权重
```

## 9.2 VehicleParameters

例如：

```text
质量
惯量
质心
重力常数
阻力参数
```

## 9.3 ActuatorParameters

例如：

```text
电机数量
臂长
推力系数
反扭矩系数
电机时间常数
推力上下限
```

## 9.4 NumericalParameters

例如：

```text
采样周期
滤波器截止频率
求解器容差
最大迭代次数
```

## 9.5 BuildParameters

例如：

```text
最大预测步数
是否启用INDI
是否启用L1
是否启用故障分配
是否使用单精度
```

---

# 10. 代码生成产物

每个控制器的生成目录必须包含：

```text
generated/
├── include/
│   ├── controller_types.h
│   ├── controller_parameters.h
│   ├── controller_context.h
│   └── controller_api.h
├── src/
│   ├── controller_initialize.c
│   ├── controller_reset.c
│   ├── controller_step.c
│   └── controller_terminate.c
├── metadata/
│   ├── controller_manifest.yaml
│   ├── parameter_manifest.yaml
│   ├── traceability.json
│   └── generation_report.txt
└── tests/
    ├── reference_inputs/
    └── reference_outputs/
```

---

# 11. Controller Manifest

每个控制器必须生成清单文件。

```yaml
schema_version: "1.0"

controller:
  id: "se3_dfbc"
  display_name: "SE3 Differential Flatness Controller"
  version: "1.0.0"

source:
  model_file: "se3_dfbc.mo"
  model_hash: "..."
  generator: "MWORKS.Sysblock 2026"
  generated_at: "..."

interface:
  required_reference:
    - position
    - velocity
    - acceleration
    - jerk
    - yaw
    - yaw_rate

  required_state:
    - position
    - velocity
    - attitude
    - angular_velocity

  output_type: "BODY_RATE_THRUST"

runtime:
  nominal_rate_hz: 200
  maximum_dt_s: 0.01
  precision: "float32"
  reentrant: true
  dynamic_memory: false

deployment:
  mworks: true
  ros1: true
  px4_sitl: true
  px4_onboard: true

resources:
  estimated_stack_bytes: 6000
  estimated_static_bytes: 18000
  maximum_execution_time_us: 500
```

---

# 12. 生成代码规范化工具

建立：

```text
Tools/codegen/mosim_codegen_normalizer
```

职责：

```text
复制生成代码
规范文件名
移除不需要的运行库依赖
生成统一API
生成Controller Manifest
生成参数映射文件
生成PX4包装器骨架
生成ROS包装器骨架
运行格式化
运行静态分析
计算源码哈希
```

Normalizer不得修改控制算法数学逻辑。

任何人工修改生成算法代码的行为都必须重新同步到MWORKS模型。

---

# 13. 生成代码不可手工维护原则

目录分为：

```text
generated/
handwritten/
```

`generated/`中的文件：

```text
禁止手工修改
每次生成时可以完全删除重建
```

`handwritten/`中保存：

```text
PX4适配器
ROS适配器
Controller Wrapper
安全检查
参数映射
测试代码
```

若必须修复生成代码问题，应：

```text
修改Sysblock模型或代码生成模板
重新生成
重新执行一致性测试
```

---

# 14. MoSim控制器核心包装层

包装器结构：

```cpp
class GeneratedControllerAdapter final : public IController
{
public:
    bool configure(
        const ControllerConfiguration& config,
        const VehicleModel& model,
        const VehicleLimits& limits) override;

    bool reset(
        const VehicleState& state,
        const TrajectoryPoint& reference,
        TimeUs time_us) override;

    ControllerResult update(
        const ControllerInput& input,
        ControllerCommand& output,
        ControllerStatus& status) override;

    void deactivate() override;

private:
    GeneratedControllerContext _context{};
    GeneratedControllerParameters _parameters{};
};
```

包装器负责：

```text
MoSim输入转换为生成代码输入
调用生成代码step
生成代码输出转换为MoSim命令
检查NaN和Inf
检查输出范围
测量执行时间
发布诊断状态
```

---

# 15. PX4源码组织方案

推荐MoSim外置PX4目录：

```text
MoSim/
└── PX4External/
    ├── CMakeLists.txt
    ├── Kconfig
    ├── msg/
    │   ├── CMakeLists.txt
    │   ├── MosimControllerCandidate.msg
    │   ├── MosimControllerStatus.msg
    │   ├── MosimControllerRequest.msg
    │   ├── MosimActuatorHealth.msg
    │   └── MosimDisturbanceEstimate.msg
    │
    └── src/
        ├── modules/
        │   ├── mosim_control_server/
        │   ├── mosim_controller_manager/
        │   ├── mosim_nmpc_worker/
        │   └── mosim_fault_manager/
        │
        ├── lib/
        │   ├── mosim_interface/
        │   ├── mosim_frames/
        │   ├── mosim_thrust_mapper/
        │   ├── mosim_controller_core/
        │   └── generated_controllers/
        │
        └── controllers/
            ├── pid/
            ├── px4ctrl/
            ├── lqr_lqi/
            ├── se3/
            ├── dfbc/
            ├── smc/
            ├── lmpc/
            └── nmpc/
```

---

# 16. 顶层外置CMake

```cmake
set(config_module_list_external
    modules/mosim_control_server
    modules/mosim_controller_manager
    modules/mosim_fault_manager
    PARENT_SCOPE
)

if(CONFIG_MOSIM_NMPC)
    list(APPEND config_module_list_external
        modules/mosim_nmpc_worker
    )
endif()
```

实际实现时应确认列表追加后正确回传父作用域。

---

# 17. PX4 Module CMake规范

示例：

```cmake
px4_add_module(
    MODULE modules__mosim_control_server
    MAIN mosim_control_server

    SRCS
        MosimControlServer.cpp
        MosimControlServer.hpp
        MosimControllerRegistry.cpp

    DEPENDS
        px4_work_queue
        mosim_controller_core
        mosim_generated_controllers
        mosim_frames
        mosim_thrust_mapper

    MODULE_CONFIG
        module.yaml

    EXTERNAL
)
```

重型控制器示例：

```cmake
px4_add_module(
    MODULE modules__mosim_nmpc_worker
    MAIN mosim_nmpc_worker

    STACK_MAIN
        12000

    SRCS
        MosimNmpcWorker.cpp

    DEPENDS
        mosim_nmpc_core
        mosim_interface

    MODULE_CONFIG
        module.yaml

    EXTERNAL
)
```

栈大小必须通过实际板载测试确定，不得长期使用随意估计值。

---

# 18. Work Queue与独立Task选择

## 18.1 推荐使用Work Queue的模块

适用条件：

```text
执行时间短
执行时间确定
不阻塞
不等待文件或网络
不进行长时间优化
可由uORB更新触发
```

适合：

```text
PID
LQR
SO(3)
SE(3)
DFBC
SMC
控制分配
坐标转换
推力映射
```

---

## 18.2 推荐使用独立Task的模块

适用条件：

```text
计算时间较长
可能发生求解超时
需要独立栈
需要独立调度优先级
不应阻塞其他飞控任务
```

适合：

```text
NMPC
鲁棒MPC
自适应MPC
大规模QP
复杂故障隔离
```

---

## 18.3 禁止行为

Work Queue任务不得：

```text
sleep
poll阻塞等待
执行文件读写
进行网络阻塞
长时间占用CPU
```

---

# 19. 调度方式

支持两种调度模式。

## 19.1 事件驱动

由高频状态Topic触发：

```text
vehicle_angular_velocity
vehicle_attitude
vehicle_local_position
```

适合：

```text
角速度环
姿态环
状态更新驱动控制器
```

## 19.2 固定周期

使用固定周期调度：

```text
ScheduleOnInterval
```

适合：

```text
位置外环
MPC
故障诊断
Controller Manager健康检查
```

---

## 19.3 推荐频率

```text
位置与速度外环：50～100 Hz
姿态控制：100～250 Hz
角速度控制：250～500 Hz
INDI：250～500 Hz
LMPC：50～100 Hz
NMPC：50～100 Hz
控制分配：250～500 Hz
故障诊断：50～200 Hz
Controller Manager：与最终输出层同步
```

具体频率由Profile和目标飞控性能决定。

---

# 20. PX4输入Topic映射

## 20.1 基础状态输入

MoSim PX4适配器至少订阅：

```text
vehicle_local_position
vehicle_attitude
vehicle_angular_velocity
vehicle_acceleration
vehicle_odometry
```

按控制器能力选择实际使用字段。

---

## 20.2 系统和飞行状态

订阅：

```text
vehicle_status
vehicle_control_mode
vehicle_land_detected
actuator_armed
```

用于：

```text
判断是否解锁
判断是否处于正确模式
判断是否允许控制器接管
判断落地状态
```

---

## 20.3 执行器与电源

订阅：

```text
battery_status
esc_status
actuator_motors
actuator_outputs
```

用于：

```text
推力映射
电池补偿
电机转速反馈
故障检测
INDI
```

具体Topic可用性取决于飞控板和电调协议。

---

## 20.4 参数更新

订阅：

```text
parameter_update
```

在安全的周期边界更新HOT参数。

---

## 20.5 参考输入

根据运行方式读取：

```text
trajectory_setpoint
vehicle_attitude_setpoint
vehicle_rates_setpoint
MoSim自定义轨迹消息
MoSim内部Controller Request
```

标准MoSim控制器应优先使用统一内部参考结构，而不是直接把uORB结构传入算法核心。

---

# 21. PX4输出层级

## 21.1 PX4原生控制模式

MoSim不发布控制设定值。

```text
PX4原生位置控制器
PX4原生姿态控制器
PX4原生角速度控制器
PX4原生控制分配
```

用于基线。

---

## 21.2 POSITION_SETPOINT

MoSim只负责轨迹或位置参考：

```text
MoSim
  ↓
trajectory_setpoint
  ↓
PX4位置与速度控制
  ↓
PX4姿态与角速度控制
```

适合：

```text
EGO轨迹直接接PX4
Fast-Planner轨迹直接接PX4
PX4原生控制基线
```

---

## 21.3 ACCELERATION_YAW

MoSim负责位置和速度外环，输出加速度与航向参考。

根据采用的PX4版本和内部接口，由适配层映射到适合的位置控制输入或姿态推力设定值。

该层必须通过版本适配测试，不能假设所有PX4版本具有完全一致的内部接管路径。

---

## 21.4 ATTITUDE_THRUST

MoSim输出：

```text
期望姿态
总推力
Yaw rate前馈
```

映射到：

```text
vehicle_attitude_setpoint
```

保留：

```text
PX4姿态控制
PX4角速度控制
PX4控制分配
```

适合：

```text
px4ctrl
基础SE(3)
基础DFBC
MWORKS外环PID
```

---

## 21.5 BODY_RATE_THRUST

MoSim输出：

```text
期望机体系角速度
总推力
```

映射到：

```text
vehicle_rates_setpoint
```

保留：

```text
PX4角速度控制
PX4控制分配
```

适合：

```text
完整DFBC
角速度前馈控制
部分NMPC
外部姿态控制
```

---

## 21.6 WRENCH

MoSim输出：

```text
三轴力矩
推力向量
```

映射到：

```text
vehicle_torque_setpoint
vehicle_thrust_setpoint
```

保留：

```text
PX4控制分配
执行器输出
```

适合：

```text
完整SE(3)刚体控制
NDI
INDI
力矩级NMPC
```

---

## 21.7 ROTOR_THRUST

MoSim输出单电机物理推力。

经过：

```text
MoSim故障感知控制分配
MoSim推力映射
```

转换为：

```text
actuator_motors
```

绕过PX4控制分配。

适合：

```text
单电机输入NMPC
故障容错控制
特殊控制分配研究
```

---

## 21.8 ROTOR_SPEED

MoSim直接输出目标电机转速。

需要底层电调或电机闭环支持。

该模式风险最高，不作为首版默认模式。

---

# 22. 坐标转换

MoSim算法核心统一：

```text
世界：ENU
机体：FLU
```

PX4内部适配器转换为：

```text
世界：NED
机体：FRD
```

转换必须集中在：

```text
mosim_frame_adapter
```

禁止每个控制器自行实现一套坐标转换。

---

# 23. 推力转换

MoSim内部：

```text
collective_thrust_N ≥ 0
方向为+Z_FLU
```

PX4多旋翼姿态和角速度设定值通常使用：

```text
FRD机体系
Z轴负方向推力
归一化范围
```

适配器执行：

```text
物理推力N
   ↓
按当前最大可用推力归一化
   ↓
转换到FRD负Z方向
   ↓
PX4 thrust_body[2]
```

基本形式：

[
u_T =
\operatorname{clamp}
\left(
\frac{T}{T_{\max,\ available}},
0,1
\right)
]

然后：

```text
thrust_body = [0, 0, -u_T]
```

实际实现还应考虑：

```text
电池电压
执行器效率
最大推力变化
悬停油门辨识
推力非线性
```

---

# 24. 推力映射分层

支持三种推力映射器。

## 24.1 StaticThrustMapper

```text
固定最大推力
固定线性比例
```

用于基础仿真。

## 24.2 VoltageCompensatedMapper

根据电池电压调整推力映射。

## 24.3 AdaptiveThrustMapper

根据：

```text
IMU加速度
电机命令
电机转速
当前姿态
```

在线估计油门—推力关系。

可复现px4ctrl的在线推力模型思想。

---

# 25. uORB内部自定义消息

建议建立：

```text
MosimControllerRequest.msg
MosimControllerCandidate.msg
MosimControllerStatus.msg
MosimActuatorHealth.msg
MosimDisturbanceEstimate.msg
MosimProfileStatus.msg
```

---

## 25.1 MosimControllerRequest

包含：

```text
目标控制器ID
目标Profile
请求输出层级
切换原因
请求时间
是否允许自动回退
```

---

## 25.2 MosimControllerCandidate

包含：

```text
控制器ID
输出类型
控制命令
命令时间
有效期
执行时间
求解器状态
健康状态
```

---

## 25.3 MosimControllerStatus

包含：

```text
当前控制器
备用控制器
当前Profile
控制器生命周期
连续失败次数
最后成功时间
执行时间
错误码
```

---

# 26. 标准Topic发布所有权

PX4标准Topic：

```text
trajectory_setpoint
vehicle_attitude_setpoint
vehicle_rates_setpoint
vehicle_torque_setpoint
vehicle_thrust_setpoint
actuator_motors
```

在MoSim控制模式下只允许：

```text
mosim_controller_manager
```

发布最终命令。

轻量控制器、NMPC Worker和故障控制器只能发布MoSim内部候选消息。

---

# 27. 与PX4原生控制器的冲突处理

Controller Manager接管前必须确认：

```text
当前控制模式允许外部或自定义控制
对应PX4原生控制环不会同时产生最终命令
当前输出层级已正确配置
当前Topic不存在另一个有效MoSim发布者
```

不得通过“多个Module同时发布，依靠最后到达消息覆盖”的方式实现切换。

---

# 28. PX4参数体系

MoSim参数分为四类：

```text
运行时算法参数
运行模式参数
机型与执行器参数
构建时参数
```

---

## 28.1 参数命名前缀

由于PX4参数名长度有限，建议统一前缀：

```text
MOS_
```

示例：

```text
MOS_CTRL_SEL
MOS_OUT_LVL
MOS_RATE_HZ
MOS_FAIL_MAX
MOS_THR_MAP
MOS_SE3_KPX
MOS_SE3_KPZ
MOS_NMPC_N
MOS_NMPC_IT
MOS_INDI_EN
MOS_L1_EN
```

参数名必须：

```text
不超过16个ASCII字符
含义清晰
同一参数组使用共同前缀
```

---

# 29. 运行模式参数

建议首批参数：

| 参数             | 说明               |
| ---------------- | ------------------ |
| `MOS_CTRL_SEL` | 当前控制器选择     |
| `MOS_OUT_LVL`  | 控制输出层级       |
| `MOS_RATE_HZ`  | 控制器运行频率     |
| `MOS_FALLBACK` | 备用控制器         |
| `MOS_FAIL_MAX` | 连续失败上限       |
| `MOS_SHADOW`   | 是否启用影子控制器 |
| `MOS_AUTO_SW`  | 是否允许自动切换   |
| `MOS_LOG_LVL`  | 日志详细度         |

---

# 30. 控制器选择枚举

示例：

```text
0  PX4_NATIVE
1  PX4CTRL
2  PID_BASE
3  PID_ENH
4  LQI
5  SMC_ST
6  SO3
7  SE3
8  DFBC
9  LMPC
10 NMPC
11 FTC_SE3
12 FTC_NMPC
```

最终枚举由Controller Registry自动生成，不应在多个文件中重复维护。

---

# 31. HOT、COLD和BUILD参数

## HOT参数

运行中可以更新：

```text
控制增益
控制权重
限幅值
滤波器参数
补偿开关
```

## COLD参数

更新后必须重置控制器：

```text
预测时域
状态维度
执行器数量
模型结构
观测器阶数
```

## BUILD参数

必须重新编译：

```text
是否编译某控制器
最大预测步数
是否启用特定求解器
浮点精度
固定数组上限
```

---

# 32. module.yaml规范

每个MoSim Module使用：

```text
module.yaml
```

定义：

```text
参数名
默认值
单位
最小值
最大值
小数位
说明
重启要求
枚举值
参数分组
```

示例：

```yaml
module_name: MoSim Control Server

parameters:
  - group: MoSim Control
    definitions:

      MOS_CTRL_SEL:
        description:
          short: Active MoSim controller
          long: Selects the active MoSim controller profile.
        type: enum
        default: 0
        values:
          0: PX4 Native
          1: PX4Ctrl
          2: PID Baseline
          7: SE3
          8: DFBC
          9: LMPC
          10: NMPC
        reboot_required: false

      MOS_RATE_HZ:
        description:
          short: Controller update rate
        type: int32
        default: 200
        min: 20
        max: 500
        unit: Hz
        reboot_required: true
```

具体YAML结构应根据目标PX4版本的schema检查。

---

# 33. 参数访问

PX4 Module采用统一参数类：

```cpp
class MosimControlServer :
    public ModuleBase<MosimControlServer>,
    public ModuleParams,
    public px4::ScheduledWorkItem
{
    DEFINE_PARAMETERS(
        (ParamInt<px4::params::MOS_CTRL_SEL>) _param_ctrl_sel,
        (ParamInt<px4::params::MOS_RATE_HZ>)  _param_rate_hz
    )
};
```

在收到：

```text
parameter_update
```

后调用：

```cpp
updateParams();
```

参数更新应在控制周期开始前生效。

---

# 34. 参数映射生成

建立自动工具：

```text
MWORKS数据字典
      ↓
Parameter Manifest
      ↓
PX4 module.yaml
      ↓
PX4参数绑定代码
      ↓
QGroundControl参数界面
```

必须避免：

```text
MWORKS参数名
PX4参数名
前端参数名
```

三套独立手工维护。

---

# 35. 参数版本与哈希

每次启动记录：

```text
参数版本
参数哈希
控制器模型哈希
生成代码哈希
固件Git Commit
```

ControllerStatus中应包含：

```text
active_parameter_version
active_model_version
active_controller_version
```

---

# 36. Kconfig体系

Kconfig只控制：

```text
是否编译某Module
是否编译某控制器
是否编译某求解器
是否启用调试功能
是否启用特定执行器接口
```

不得使用Kconfig保存：

```text
PID增益
控制权重
推力上限
飞行质量
```

这些属于运行参数。

---

# 37. 顶层Kconfig示例

```text
menuconfig MODULES_MOSIM_CONTROL
    bool "MoSim control framework"
    default n
    help
        Enable the MoSim controller deployment framework.

if MODULES_MOSIM_CONTROL

config MOSIM_CTRL_PID
    bool "MoSim PID controllers"
    default y

config MOSIM_CTRL_SE3
    bool "MoSim SE3 controller"
    default y

config MOSIM_CTRL_DFBC
    bool "MoSim DFBC controller"
    default y

config MOSIM_CTRL_LMPC
    bool "MoSim linear MPC"
    default n

config MOSIM_CTRL_NMPC
    bool "MoSim nonlinear MPC"
    default n

config MOSIM_INDI
    bool "MoSim INDI augmentation"
    default n

config MOSIM_L1
    bool "MoSim L1 adaptive augmentation"
    default n

config MOSIM_DEBUG
    bool "MoSim detailed debug output"
    default n

endif
```

实际符号命名应与PX4模块路径命名规范保持一致。

---

# 38. 飞控板配置

目标飞控板的：

```text
boards/<vendor>/<board>/default.px4board
```

应启用：

```text
CONFIG_MODULES_MOSIM_CONTROL=y
```

根据板载资源选择：

```text
CONFIG_MOSIM_CTRL_PID=y
CONFIG_MOSIM_CTRL_SE3=y
CONFIG_MOSIM_CTRL_DFBC=y
CONFIG_MOSIM_CTRL_LMPC=n
CONFIG_MOSIM_CTRL_NMPC=n
```

高算力飞控Profile可启用MPC/NMPC。

---

# 39. 板载预选项的准确含义

所谓“在板载预选项里加进去”，实际应拆成：

```text
Kconfig：
决定Module和算法是否进入固件

px4board：
决定某块飞控默认编译哪些Module

module.yaml：
决定有哪些运行时参数

Airframe脚本：
决定具体机型使用哪些参数默认值

启动脚本：
决定Module何时启动
```

不能把以上内容全部笼统称为“参数编译进去”。

---

# 40. 板级Profile

建议建立：

```text
mosim_minimal
mosim_standard
mosim_advanced
mosim_full
```

## mosim_minimal

包含：

```text
PID
SE3
Controller Manager
基本坐标转换
```

## mosim_standard

增加：

```text
DFBC
INDI
故障检测
QP控制分配
```

## mosim_advanced

增加：

```text
LMPC
L1
高级日志
影子运行
```

## mosim_full

增加：

```text
NMPC
多控制器并行
完整故障容错
高级诊断
```

---

# 41. 编译命令

## 41.1 SITL外置模块

示例：

```bash
make px4_sitl EXTERNAL_MODULES_LOCATION=/absolute/path/to/MoSim/PX4External
```

若采用具体PX4版本支持的完整目标名，可使用对应SITL目标。

---

## 41.2 目标飞控

示例：

```bash
make px4_fmu-v6x_default \
    EXTERNAL_MODULES_LOCATION=/absolute/path/to/MoSim/PX4External
```

实际目标由飞控板型号决定。

---

## 41.3 清理规则

以下变化后必须重新配置或清理构建目录：

```text
首次加入外置模块
新增uORB消息
新增参数文件
修改Kconfig
修改模块列表
修改MODULE_CONFIG
切换外置模块路径
```

建议命令：

```bash
make distclean
```

或删除对应构建目录后重新构建。

---

# 42. 构建产物

每次构建应归档：

```text
固件文件
ELF文件
MAP文件
参数元数据
uORB消息元数据
Airframe元数据
控制器清单
生成代码哈希
构建日志
编译器版本
PX4 Commit
```

---

# 43. 启动机制

PX4启动由启动脚本组织。

MoSim Module支持：

```text
mosim_control_server start
mosim_control_server stop
mosim_control_server status

mosim_controller_manager start
mosim_controller_manager stop
mosim_controller_manager status
```

---

# 44. Airframe脚本

为MoSim建立独立机型配置，例如：

```text
ROMFS/px4fmu_common/init.d/airframes/
41000_mosim_quad_x
```

脚本职责：

```text
设置机型几何
设置质量与推力相关默认值
设置控制器Profile默认值
设置控制频率
启动MoSim Module
```

示例：

```sh
#!/bin/sh

. ${R}etc/init.d/rc.mc_defaults

param set-default MOS_CTRL_SEL 7
param set-default MOS_OUT_LVL 3
param set-default MOS_RATE_HZ 200
param set-default MOS_FALLBACK 2

mosim_controller_manager start
mosim_control_server start
```

首版开发阶段可不自动启动，而由NSH手动启动，稳定后再进入Airframe脚本。

---

# 45. 启动顺序

推荐：

```text
PX4基础系统
   ↓
传感器和状态估计
   ↓
Commander和飞行模式
   ↓
Controller Manager
   ↓
控制器Server / Worker
   ↓
故障管理器
   ↓
控制权授权
```

Controller Manager不得在状态估计有效前发布控制命令。

---

# 46. Module生命周期

MoSim Module状态：

```text
UNINITIALIZED
CONFIGURED
STANDBY
ACTIVE
DEGRADED
FAILED
STOPPING
```

## UNINITIALIZED

参数和模型尚未加载。

## CONFIGURED

参数有效，控制器已初始化。

## STANDBY

控制器运行或准备运行，但不拥有最终控制权。

## ACTIVE

控制器拥有当前控制权。

## DEGRADED

控制器仍运行，但输入、求解器或执行器能力下降。

## FAILED

控制器输出不再允许发布。

---

# 47. 控制器切换

切换流程：

```text
收到Controller Request
        ↓
检查目标控制器是否已编译
        ↓
检查输入状态是否满足
        ↓
初始化目标控制器
        ↓
进入SHADOW状态
        ↓
比较候选输出
        ↓
状态和积分器对齐
        ↓
命令渐变或无扰切换
        ↓
目标控制器ACTIVE
        ↓
旧控制器STANDBY
```

---

# 48. 影子运行

影子控制器：

```text
订阅相同输入
执行完整计算
不发布最终命令
```

记录：

```text
候选输出
执行时间
求解状态
约束状态
与主控制器差异
```

用途：

```text
真机前验证新控制器
NMPC稳定性观察
控制器切换准备
异常提前检测
```

---

# 49. 求解失败处理

对于MPC和NMPC：

```text
单次失败：
使用上一次可行控制量

连续失败：
切换SE3或PID

长期失败：
安全悬停或降落
```

必须设置：

```text
最大求解时间
最大连续失败次数
最大可使用旧解时长
备用控制器
```

---

# 50. 控制权管理

Controller Manager只在以下条件满足时发布：

```text
飞行状态允许
控制器ACTIVE
状态有效
参考有效
输出有限
输出未过期
输出层级匹配
无严重安全错误
```

否则执行：

```text
拒绝候选命令
保持短时安全输出
切换备用控制器
请求悬停、返航或降落
```

---

# 51. 安全限制

最终发布前统一检查：

```text
最大速度
最大加速度
最大倾角
最大角速度
最大力矩
总推力范围
单电机推力范围
推力变化率
电机数量
时间戳有效性
```

即使控制器内部已经限幅，Controller Manager仍保留最终安全限幅。

---

# 52. 解锁和飞行模式

MoSim控制器不得自行无条件解锁。

解锁、模式和失效保护仍由PX4系统管理。

MoSim可以：

```text
请求控制模式
报告控制器健康状态
拒绝在状态无效时接管
触发安全回退请求
```

首版不直接修改Commander核心逻辑。

---

# 53. 实时性要求

每个控制器声明：

```text
标称运行周期
最大允许周期
平均执行时间目标
P99执行时间目标
观测最大执行时间
最大栈使用
静态内存
```

建议要求：

```text
平均执行时间 ≤ 30%控制周期
P99执行时间 ≤ 70%控制周期
观测最大执行时间 < 控制周期
截止时间错过率 = 0
```

具体标准由08文档定义。

---

# 54. 性能测量

PX4包装器记录：

```text
控制器总执行时间
生成代码执行时间
坐标转换时间
推力映射时间
安全检查时间
求解器迭代次数
求解器状态
连续超时次数
```

不得只测量整个Module循环，而不区分各部分。

---

# 55. 栈与内存

独立Task必须设置：

```text
STACK_MAIN
```

Work Queue共享栈，因此轻量控制器应严格控制局部大数组。

禁止在控制周期函数中定义大型局部数组：

```cpp
float Q[100][100];
float workspace[50000];
```

大型工作区应放在控制器Context或静态预分配区域。

---

# 56. NMPC部署规则

NMPC板载部署前必须完成：

```text
固定预测时域
固定最大迭代次数
固定工作区
Warm Start
超时中止
可行解保持
求解失败回退
执行时间分布测试
```

NMPC不得运行在会阻塞IMU、姿态控制或角速度控制的Work Queue上。

---

# 57. INDI部署规则

INDI通常要求：

```text
高频角速度
角加速度估计
电机转速或执行器状态
低延迟执行器模型
```

若目标飞控无法获得可靠电机转速反馈，应明确切换为：

```text
命令电机模型
估计电机状态
简化INDI
关闭INDI
```

不得假装存在真实转速反馈。

---

# 58. L1部署规则

L1自适应控制器必须设置：

```text
预测器状态复位
自适应增益上限
低通滤波器
补偿输出限幅
输入失效处理
切换时状态初始化
```

L1补偿不得绕过最终安全限幅。

---

# 59. 故障控制部署规则

故障控制模块输出：

```text
ActuatorHealth
effectiveness
confidence
fault_type
fault_time
```

控制分配器根据：

[
G_f = G\Lambda
]

更新执行器有效性矩阵。

严重故障时Controller Manager可切换：

```text
Fault-Tolerant SE3
Fault-Tolerant NMPC
Yaw-Degraded Controller
Emergency Land
```

---

# 60. 控制器注册机制

每个控制器提供：

```cpp
struct ControllerDescriptor {
    uint16_t id;
    const char* name;
    const char* version;

    ControlOutputType output_type;

    bool onboard_supported;
    bool codegen_generated;
    bool requires_worker_task;

    IController* (*create)();
};
```

Controller Registry根据Kconfig自动加入已编译控制器。

未编译控制器不得出现在可选参数枚举中。

---

# 61. 编译期控制器裁剪

示例：

```cpp
#if defined(CONFIG_MOSIM_CTRL_SE3)
registerController(makeSe3Descriptor());
#endif

#if defined(CONFIG_MOSIM_CTRL_DFBC)
registerController(makeDfbcDescriptor());
#endif

#if defined(CONFIG_MOSIM_CTRL_NMPC)
registerController(makeNmpcDescriptor());
#endif
```

这样不同飞控板可编译不同控制器集合。

---

# 62. ROS 1包装器

为了在进入PX4 Module前快速验证生成代码，提供：

```text
mosim_controller_ros
```

订阅：

```text
/mosim/uav0/reference/trajectory
/mosim/uav0/state/vehicle
```

发布：

```text
/mavros/setpoint_raw/attitude
或
/mavros/setpoint_raw/local
```

ROS包装器与PX4包装器必须调用同一个Controller Core。

---

# 63. px4ctrl复现定位

px4ctrl复现应先作为ROS外部控制器实现：

```text
EGO PositionCommand
        ↓
px4ctrl Controller Core
        ↓
ROS MAVROS Adapter
        ↓
PX4姿态 + 推力接口
```

完成后再将同一核心包装为PX4 Module。

不得分别重写两套px4ctrl控制公式。

---

# 64. PX4原生基线

PX4原生控制器不需要重新实现。

MoSim仅提供：

```text
轨迹适配器
参数快照
日志采集
测试场景
指标计算
```

其作用是建立：

```text
PX4_NATIVE_BASELINE
```

---

# 65. 控制器迁移顺序

推荐工程顺序：

```text
1. PX4原生控制器 + Gazebo
2. px4ctrl ROS复现
3. 建立统一Controller Core接口
4. MWORKS PID生成代码接入ROS
5. MWORKS PID生成代码接入PX4 SITL Module
6. SE3 / DFBC接入
7. LMPC接入
8. NMPC Worker接入
9. INDI / L1增强接入
10. 故障容错和控制分配接入
11. HITL
12. 真机
```

---

# 66. 跨平台一致性

同一输入数据集必须依次运行：

```text
MWORKS原模型
MWORKS生成代码
离线C测试程序
ROS 1包装器
PX4 SITL Module
PX4板载Module
```

比较：

```text
控制器内部状态
姿态指令
角速度指令
推力指令
力矩指令
电机指令
```

任何显著差异必须定位原因。

---

# 67. 常见不一致来源

```text
float与double差异
离散步长差异
积分器初始化差异
坐标转换错误
重力补偿重复
推力归一化错误
参数默认值不同
滤波器状态不同
求解器配置不同
编译器数学优化
时间戳和dt不同
```

---

# 68. 静态分析

生成代码和手写包装层至少执行：

```text
编译器警告
clang-tidy或同类检查
未初始化变量检查
数组越界检查
浮点异常检查
MISRA规则检查
复杂度分析
```

生成代码警告不得简单整体关闭。

---

# 69. 单元测试

至少覆盖：

```text
初始化
复位
零误差悬停
正负位置误差
正负姿态误差
最大输入
最小输入
NaN输入
非法dt
参数边界
输出饱和
连续运行
多实例运行
```

---

# 70. PX4 SITL验收

每个控制器接入PX4后至少验证：

```text
Module可启动和停止
参数可见
参数更新正确
uORB输入正常
uORB输出正确
无Topic争用
无NaN
控制器切换正常
日志完整
PX4 SITL稳定飞行
```

---

# 71. 板载验收

目标飞控板上至少验证：

```text
固件可正常启动
Module可自动或手动启动
参数正常加载
CPU负载符合要求
栈无溢出
内存占用符合要求
控制周期无超时
运行30分钟无异常
日志完整
复位后状态正确
```

---

# 72. HITL验收

验证：

```text
真实飞控固件
真实调度
真实串口和USB链路
Gazebo传感器输入
电机命令回传
控制器实时性
控制器切换
故障回退
```

---

# 73. 真机前置条件

必须完成：

```text
MWORKS闭环通过
生成代码一致性通过
ROS + Gazebo通过
PX4 SITL通过
板载实时性通过
推力映射标定完成
遥控接管验证完成
安全限幅验证完成
日志验证完成
```

---

# 74. 真机部署包

每次真机测试固件必须包含：

```text
固件文件
PX4 Commit
MoSim Commit
控制器模型哈希
生成代码哈希
参数文件
Airframe ID
飞控板型号
编译器版本
测试计划
回滚固件
```

---

# 75. 日志规范

MoSim PX4 Module应记录：

```text
当前控制器ID
当前Profile
控制器输入摘要
原始控制输出
最终控制输出
推力映射结果
饱和标志
控制器执行时间
求解器状态
切换事件
故障事件
回退事件
```

高频内部状态只在调试Profile启用，避免占用过多日志带宽。

---

# 76. 事件与错误码

建议错误码分类：

```text
0x1xxx 输入错误
0x2xxx 参数错误
0x3xxx 求解器错误
0x4xxx 输出错误
0x5xxx 执行器错误
0x6xxx 控制器切换错误
0x7xxx 实时性错误
0x8xxx 内部错误
```

示例：

```text
MOS_E_STATE_STALE
MOS_E_REF_STALE
MOS_E_Q_INVALID
MOS_E_SOLVER_TIMEOUT
MOS_E_SOLVER_INFEAS
MOS_E_OUTPUT_NAN
MOS_E_THRUST_LIMIT
MOS_E_SWITCH_FAIL
```

---

# 77. 前端接口

前端通过MAVLink、ROS或独立管理接口读取：

```text
已编译控制器列表
当前控制器
当前输出层级
当前Profile
控制器健康状态
执行时间
求解器状态
故障状态
备用控制器
参数版本
固件版本
```

前端只发送：

```text
控制器切换请求
Profile切换请求
参数修改请求
测试场景请求
```

最终安全决策仍由PX4侧Controller Manager执行。

---

# 78. CI构建矩阵

每次正式提交至少构建：

```text
Linux离线控制器
ROS 1控制器节点
PX4 SITL
目标飞控板Minimal Profile
目标飞控板Standard Profile
```

发布版本增加：

```text
Advanced Profile
Full Profile
不同PX4版本兼容构建
```

---

# 79. CI流水线

```text
检查模型和Manifest
        ↓
生成控制代码
        ↓
检查生成代码是否有未提交变化
        ↓
静态分析
        ↓
单元测试
        ↓
离线一致性测试
        ↓
ROS编译
        ↓
PX4 SITL编译
        ↓
目标飞控板交叉编译
        ↓
SITL快速回归
        ↓
生成固件和报告
```

---

# 80. 版本锁定

每个正式版本锁定：

```text
MWORKS版本
PX4版本和Commit
ROS版本
Gazebo版本
编译器版本
求解器版本
控制器模型版本
生成代码版本
```

不得只记录“PX4最新版”或“MWORKS 2026”。

---

# 81. 第三方代码与许可证

每个控制器Manifest记录：

```text
原创实现
论文复现
开源代码改编
开源代码直接依赖
许可证
原始仓库
原始Commit
修改内容
```

生成代码、PX4代码和第三方求解器的许可证必须分别管理。

---

# 82. 发布目录

```text
Release/
└── mosim-control-<version>/
    ├── firmware/
    │   ├── sitl/
    │   └── boards/
    ├── controllers/
    │   ├── generated/
    │   └── manifests/
    ├── parameters/
    ├── airframes/
    ├── metadata/
    ├── licenses/
    ├── reports/
    └── checksums/
```

---

# 83. 推荐工程目录

```text
MoSim/
├── Config/
│   └── controllers/
│
├── Controllers/
│   ├── core/
│   ├── generated/
│   ├── handwritten/
│   ├── manifests/
│   └── tests/
│
├── Interfaces/
│
├── Adapters/
│   ├── mworks/
│   ├── ros1/
│   ├── px4/
│   └── offline/
│
├── PX4External/
│   ├── CMakeLists.txt
│   ├── Kconfig
│   ├── msg/
│   └── src/
│
├── Codegen/
│   ├── templates/
│   ├── normalizer/
│   ├── parameter_generator/
│   └── wrapper_generator/
│
├── Airframes/
│
├── Parameters/
│
├── Test/
│
└── Release/
```

---

# 84. 首版实现范围

V1.0至少支持：

```text
PX4原生控制器
px4ctrl
MWORKS PID
SE(3)
DFBC
LMPC
NMPC
```

部署层级：

```text
POSITION_SETPOINT
ATTITUDE_THRUST
BODY_RATE_THRUST
WRENCH
```

首版不要求直接支持：

```text
ROTOR_SPEED真机控制
动态PX4插件加载
运行时加载任意二进制控制器
所有控制器同时编译到低资源飞控板
```

---

# 85. 首版Module集合

```text
mosim_controller_manager
mosim_control_server
mosim_nmpc_worker
mosim_frame_adapter
mosim_thrust_mapper
```

其中：

```text
frame_adapter和thrust_mapper优先做成库
而不是独立后台Module
```

---

# 86. 首版Kconfig集合

```text
MODULES_MOSIM_CONTROL
MOSIM_CTRL_PID
MOSIM_CTRL_PX4CTRL
MOSIM_CTRL_SE3
MOSIM_CTRL_DFBC
MOSIM_CTRL_LMPC
MOSIM_CTRL_NMPC
MOSIM_INDI
MOSIM_L1
MOSIM_DEBUG
```

---

# 87. 首版参数集合

```text
MOS_CTRL_SEL
MOS_OUT_LVL
MOS_RATE_HZ
MOS_FALLBACK
MOS_FAIL_MAX
MOS_AUTO_SW
MOS_SHADOW
MOS_THR_MAP
MOS_LOG_LVL
```

各控制器增益单独分组。

---

# 88. 开发实施顺序

## 第一阶段：接口和基线

```text
统一控制器C/C++接口
PX4原生基线
px4ctrl ROS复现
PX4坐标转换
PX4推力映射
```

## 第二阶段：生成代码

```text
MWORKS PID生成
离线C一致性
ROS包装器
PX4 SITL包装器
```

## 第三阶段：统一Module

```text
mosim_control_server
Controller Registry
Controller Manager
标准参数系统
```

## 第四阶段：高级控制器

```text
SE3
DFBC
LMPC
NMPC Worker
```

## 第五阶段：增强与容错

```text
INDI
L1
AWFF
故障诊断
故障控制分配
```

## 第六阶段：板载与真机

```text
板载资源测试
HITL
真机低风险测试
高级控制器真机测试
```

---

# 89. 强制性设计规则

1. MWORKS只生成平台无关控制算法，不生成uORB、ROS或飞行模式代码。
2. 用于嵌入式部署的控制器必须建立在可生成代码的Sysblock模型中。
3. 生成代码不得直接依赖PX4头文件。
4. 生成代码不得在实时周期中动态分配内存。
5. 每个控制器必须具有独立Context，支持多实例和复位。
6. 所有控制器核心统一使用ENU、FLU和SI单位。
7. PX4坐标转换只能由统一适配层完成。
8. 控制器核心输出物理推力，PX4适配器负责归一化。
9. 同一PX4标准控制Topic只能有一个最终MoSim发布者。
10. 所有控制器候选输出必须经过Controller Manager仲裁。
11. Kconfig只决定构建功能，不保存控制增益。
12. 运行增益使用PX4参数系统管理。
13. 具体机型默认值使用Airframe脚本设置。
14. 控制器参数名必须符合PX4长度和命名限制。
15. 轻量确定性控制器优先使用Work Queue。
16. 重型优化控制器使用独立Task或Worker。
17. NMPC不得阻塞姿态、角速度或传感器相关Work Queue。
18. MWORKS模型、生成代码、ROS包装器和PX4 Module必须进行一致性测试。
19. 生成代码目录不得手工修改。
20. 所有正式固件必须记录模型、参数、生成代码和PX4版本哈希。
21. 真机前必须通过MWORKS、Gazebo、SITL和板载实时性测试。
22. 控制器失效时必须存在明确备用控制器和安全策略。

---

# 90. 最终结论

MoSim的PX4部署不应采用：

```text
每个控制器复制一套PX4 Module
每个控制器各自处理uORB
每个控制器各自转换坐标
每个控制器各自发布标准PX4 Topic
```

而应采用：

```text
MWORKS模型
   ↓
统一生成代码接口
   ↓
平台无关Controller Core
   ↓
统一Controller Registry
   ↓
统一PX4运行Server / Worker
   ↓
统一Controller Manager
   ↓
统一uORB与安全发布
```

最终形成：

```text
同一控制器模型
      ↓
MWORKS仿真
      ↓
生成C代码
      ↓
ROS 1 + Gazebo验证
      ↓
PX4 SITL Module
      ↓
目标飞控板固件
      ↓
HITL
      ↓
真实四旋翼
```

整个过程中控制算法本体保持一致，仅替换运行适配层。

这使MoSim具备：

```text
模型到代码的一致性
多控制器统一部署
飞控板资源裁剪
运行时控制器切换
统一参数管理
统一安全管理
统一日志和测试
可追溯固件发布
```

从而真正实现基于MWORKS的控制器设计、自动代码生成、PX4嵌入式部署和Gazebo/真机闭环验证。
