# 9. 项目概述：Genesis World

## 9.1 定位

Genesis World 原名  **Genesis** ，是面向机器人、具身智能和 Physical AI 的通用仿真平台。它并不是只做刚体动力学的 MuJoCo 替代品，而是试图把以下能力放进同一个框架：

```text
多物理场求解
机器人刚体动力学
GPU并行环境
传感器
强化学习训练
可微分仿真
实时/离线渲染
统一Python接口
跨硬件编译
```

官方当前将系统分为四层：

```text
Simulation Interface
    机器人、传感器、控制器、并行环境、GUI和资产导入

Physics
    刚体、软体、颗粒、流体及多求解器耦合

Rendering
    Nyx、Luisa、Pyrender等渲染路径

Compiler
    Quadrants跨平台计算编译层
```

项目已经由早期的 `Genesis` 更名为 `Genesis World`，当前官方仓库是 `genesis-world`，采用 Apache 2.0 许可证。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

对我们的长期项目而言，Genesis 最合适的定位是：

```text
高速GPU物理和强化学习候选后端
多物理场研究后端
无人机RL快速实验平台
新一代仿真接口设计参考
```

它暂时不应该替代：

```text
Gazebo：
    PX4、ROS2、MID360和工程级系统验证

UE：
    最终高质量展示前端

PX4：
    飞控和实机迁移标准
```

---

# 9.2 核心设计理念

| 设计原则       | 说明                                                       |
| -------------- | ---------------------------------------------------------- |
| 统一多物理场   | 刚体、软体、颗粒、流体等求解器可以在同一场景中运行和耦合   |
| Python优先     | 用户通过Python创建场景、模型、传感器和训练环境             |
| GPU原生        | 从计算内核和数据结构层面面向GPU并行，而不是事后添加GPU包装 |
| 多环境并行     | 同一个模型可批量运行大量环境，服务RL和参数扫描             |
| 求解器可插拔   | 不同材料和物理现象使用不同Solver，但遵循统一生命周期接口   |
| 渲染独立       | 物理与渲染分层，渲染器通过相机传感器接入                   |
| 跨平台计算     | 通过Quadrants适配CUDA、ROCm、Metal、Vulkan、x86和ARM64     |
| 机器人接口统一 | URDF、MJCF、OBJ、GLB、USD等资产可以进入统一场景接口        |
| 可微分方向     | 在计算基础设施中预留自动微分和反向传播能力                 |
| 研究代码友好   | 希望既能在普通电脑上运行，又能扩展到数据中心GPU            |

Genesis 当前物理层包含 Rigid、FEM、MPM、PBD、SPH、IPC、SAP等求解器，并允许多个求解器在同一场景中共同步进。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

---

# 9.3 系统设计逻辑

## 9.3.1 第一性原理：为什么要做“统一多物理场”？

MuJoCo、Gazebo这类平台最擅长的通常是刚体、关节和接触。

但真实机器人环境不只有刚体：

```text
刚体：
    无人机机身
    电机
    机械臂
    障碍物

柔性物体：
    绳索
    布料
    软体结构

颗粒：
    沙土
    粉末
    碎石

流体：
    水
    液体
    烟雾

弹塑性材料：
    橡胶
    泡沫
    可变形地面
```

传统做法是为每类现象单独选择仿真器：

```text
刚体 → MuJoCo
流体 → SPH引擎
软体 → FEM/MPM
布料 → PBD
```

然后不同系统之间很难同步。

Genesis 的核心想法是：

```text
不同材料用不同求解器
        ↓
所有求解器共享同一个Scene
        ↓
由Coupler协调相互作用
        ↓
统一推进仿真时间
```

例如：

```text
刚体无人机
    与
柔性网、绳索、流体或颗粒环境
    发生相互作用
```

对普通四旋翼导航，这种能力可能暂时用不上；但如果以后做：

```text
无人机吊挂
柔性负载
绳索运输
沙尘环境
水面起降
无人机机械臂
碰撞软障碍物
```

多物理场就会有明显价值。

---

## 9.3.2 第二性原理：为什么采用“求解器统一接口”？

不同物理方法的数学形式完全不同：

```text
Rigid Solver：
    刚体、关节和接触约束

FEM：
    网格化连续体

MPM：
    粒子与背景网格结合

PBD：
    直接修正位置满足约束

SPH：
    基于粒子的流体求解
```

Genesis 没有试图用一个算法解决所有现象，而是统一求解器的生命周期：

```text
build()
    初始化求解资源

reset()
    重置指定环境状态

step()
    前进一步或子步
```

官方Solver基类和多求解器示例都采用这种思路：不同求解器各自负责内部物理，但由统一场景组织共同执行。([Genesis World](https://genesis-world.readthedocs.io/en/latest/api_reference/engine/solvers/index.html "Solvers — Genesis 1.0.0 documentation"))

这对我们的架构很有启发。

我们也不应该要求：

```text
Gazebo
MuJoCo
Genesis
自研动力学
```

具有完全相同的内部实现。

只需要定义统一外部接口：

```text
PhysicsBackend

initialize(model, config)
reset(env_ids)
apply_action(action)
step(dt)
get_state()
get_sensor_data()
```

不同后端内部自己选择最合适的求解方式。

---

## 9.3.3 第三性原理：为什么Python接口下还能高性能？

正常情况下，Python循环很慢。

如果每个刚体、每个粒子、每个接触都通过Python逐个计算，性能必然很差。

Genesis 的设计不是让Python直接执行每一个数值运算，而是：

```text
Python：
    描述场景
    配置模型
    调用高层接口
    定义任务和训练逻辑

Quadrants：
    将计算内核编译到具体硬件

硬件：
    CUDA / ROCm / Metal / Vulkan / CPU
```

也就是说：

```text
Python是控制面
编译后的Kernel是数据面
```

官方架构说明，Quadrants负责把Python计算内核降低到CUDA、AMD ROCm、Apple Metal、Vulkan、x86和ARM64，并承载自动微分、GPU Graph和缓存机制。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

这与普通Python逐步调用物理引擎不同，更接近：

```text
Python定义计算图
        ↓
编译
        ↓
GPU批量执行
```

---

# 9.4 Genesis 的四层架构

## 9.4.1 Simulation Interface

这一层是用户直接接触的接口。

它负责：

```text
Scene
Entity
Robot
Sensor
Controller
Environment
Viewer
Asset Loader
Parallel Environments
```

支持的资产入口包括：

```text
URDF
MJCF
OBJ
GLB
USD
STL等
```

还提供：

```text
IMU
LiDAR
深度相机
接触力
触觉
表面距离
温度场
```

等传感器示例。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

这一层对我们最重要的启发是：

> 上层任务不应该知道底层Solver的全部细节。

比如无人机强化学习任务只关心：

```text
飞机状态
控制动作
传感器数据
奖励
终止条件
```

不需要知道刚体求解器内部每一次碰撞迭代。

---

## 9.4.2 Physics

Physics层由多个Solver构成：

```text
RigidSolver
    刚体、机器人、关节和刚性物体

MPMSolver
    弹性体、颗粒、黏性材料

FEMSolver
    弹性/塑性连续体

PBDSolver
    布料、软体和粒子

SPHSolver
    流体

SFSolver
    绳索、纤维和毛发

ToolSolver
    工具和运动学约束
```

官方文档明确把这些Solver视为不同材料和物理现象的专用计算引擎，并通过统一场景实现多求解器共同运行。([Genesis World](https://genesis-world.readthedocs.io/en/latest/api_reference/engine/solvers/index.html "Solvers — Genesis 1.0.0 documentation"))

对于四旋翼，第一阶段只需要：

```text
RigidSolver
```

不要因为Genesis有多物理能力，就一开始把软体、流体、颗粒全部塞进项目。

---

## 9.4.3 Rendering

当前Genesis提供或集成三类渲染路径：

```text
Nyx
    面向机器人场景设计的自研渲染器

Luisa
    基于DSL的光线追踪路径

Pyrender
    传统光栅化渲染
```

渲染路径作为相机传感器接入，而不是和物理求解器混在一起。官方示例还包含PBR材质、多相机、多环境、附着相机和3D Gaussian Splat等能力。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

这对我们的启发是：

```text
物理后端和渲染后端可以独立选择
```

例如：

```text
Genesis负责GPU批量物理
Nyx负责训练观测

或者：

Genesis负责物理
UE负责最终展示
```

并不一定要求Genesis物理只能配Genesis渲染。

---

## 9.4.4 Compiler

Quadrants是Genesis底层跨平台计算编译层。

它的职责不是编译整个Python应用，而是编译物理和渲染中高密度计算Kernel：

```text
碰撞
粒子更新
约束求解
矩阵/向量运算
批量环境更新
```

目标硬件包括：

```text
NVIDIA CUDA
AMD ROCm
Apple Metal
Vulkan
x86 CPU
ARM64
```

这说明Genesis的设计目标比只支持NVIDIA GPU更宽，但实际性能、功能覆盖和稳定性仍需针对具体平台验证。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

---

# 9.5 并行环境设计

Genesis的重要用途之一是批量强化学习。

它的思路与MJX类似：

```text
同一个机器人模型
        ↓
创建大量环境实例
        ↓
一次性批量推进
```

官方Solver文档说明，Genesis支持批量多环境仿真；当前官方无人机悬停训练示例默认配置甚至创建了8192个环境，并用PPO训练四维动作的悬停任务。([Genesis World](https://genesis-world.readthedocs.io/en/latest/api_reference/engine/solvers/index.html "Solvers — Genesis 1.0.0 documentation"))

无人机悬停示例中已经出现了：

```text
四维动作
动作延迟模拟
目标位置随机重采样
位置、速度和角速度观测
碰撞/坠落终止
PPO训练
批量环境数量
```

这说明Genesis并不是“理论上能做无人机”，而是已经提供了实际无人机RL示例。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/hover_train.py "genesis-world/examples/drone/hover_train.py at main · Genesis-Embodied-AI/genesis-world · GitHub"))

但需要注意：

> 官方示例证明了接口和训练链路可行，不代表其无人机模型已经等同于真实云纵Sunray-150，也不代表训练策略可以直接部署实机。

我们仍需自行校准：

```text
质量
惯量
电机位置
推力系数
反扭矩系数
电机动态
空气阻力
风扰
传感器噪声
控制延迟
```

---

# 9.6 无人机在 Genesis 里的建模方式

## 9.6.1 可用的两种层级

### 高层控制模型

动作可以是：

```text
目标推力
目标姿态
目标角速度
目标速度
```

底层控制器负责把动作转换为电机控制。

适合：

```text
高层导航RL
轨迹跟踪RL
抗扰策略
目标点控制
```

### 电机级模型

动作直接是：

```text
motor_1
motor_2
motor_3
motor_4
```

然后计算：

```text
T_i = k_f ω_i²
Q_i = k_m ω_i²
```

适合：

```text
端到端控制
控制分配
单电机退化
容错控制
底层策略训练
```

对我们的项目，建议先做高层或中层控制，再做电机级。

---

## 9.6.2 云纵模型迁移

Genesis支持URDF、MJCF和常见网格资产导入，但我们的Sunray-150不能只导入外形模型。

真正需要的是：

```text
geometry:
    机身和电机位置

mass:
    总质量和各部件质量

inertia:
    完整惯量矩阵

motors:
    位置
    轴向
    转向
    k_f
    k_m
    最大转速
    时间常数

sensors:
    IMU
    MID360
    Camera

aerodynamics:
    线性/二次阻力
    风扰
```

也就是说：

```text
导入mesh ≠ 完成无人机模型
```

mesh只解决“长什么样”，动力学参数才决定“怎么飞”。

---

# 9.7 传感器系统

Genesis当前仿真接口已经提供IMU、LiDAR、深度相机、接触力、触觉等传感器类型和示例，并支持在并行环境中使用。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

这对我们很有吸引力，因为理论上可以建立：

```text
Genesis无人机
    ↓
IMU + LiDAR + Depth Camera
    ↓
RL观测或感知算法
```

但必须区分两类需求。

## 训练型传感器

只要提供足够信息给策略：

```text
距离射线
简化深度
IMU
真值速度
相对目标位置
```

Genesis很合适。

## 工程型传感器

要严格复现MID360：

```text
非重复扫描模式
真实FOV
点频
时间戳
逐点时间
噪声
盲区
ROS2 PointCloud2
Livox消息格式
```

目前仍需要自行建模和验证。

因此：

```text
Genesis LiDAR：
    适合RL和快速感知实验

Gazebo/专用MID360模型：
    更适合工程联调

真实MID360：
    最终验证
```

官方仓库存在LiDAR、IMU和深度传感器实例，但这并不等于内置了针对Livox MID360的完整工程级扫描模型。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

---

# 9.8 可微分仿真

可微分仿真的目标是：

```text
仿真输出
    对
模型参数或控制输入
    可求梯度
```

例如：

```text
位置误差
    对
电机推力系数
```

求梯度后，可以用于：

```text
系统辨识
参数优化
轨迹优化
控制器优化
形状优化
材料参数估计
```

Genesis通过Quadrants提供自动微分和反向传播基础设施，并将可微分仿真作为长期核心能力。([Genesis World](https://genesis-world.readthedocs.io/en/latest/index.html "Genesis World — Genesis 1.0.0 documentation"))

但这里必须谨慎：

> 不同Solver、碰撞路径和版本的可微分支持程度可能不同，不能看到“支持可微分”就假设刚体、碰撞、传感器和所有多物理耦合都能无条件反向传播。

对我们第一阶段而言，可微分不是首要任务。

优先级应该是：

```text
先让四旋翼动力学正确
    ↓
再让控制和RL环境正确
    ↓
最后考虑可微系统辨识或梯度控制
```

---

# 9.9 Genesis 与 MuJoCo 的区别

| 维度         | Genesis World                   | MuJoCo                  |
| ------------ | ------------------------------- | ----------------------- |
| 核心范围     | 多物理场、GPU并行、传感器、渲染 | 刚体、关节、接触、控制  |
| 成熟程度     | 较新、快速演进                  | 历史更长、控制领域成熟  |
| 接口风格     | Python优先                      | C核心 + Python API      |
| 物理类型     | 刚体、软体、颗粒、流体等        | 主要刚体与关节          |
| GPU批量      | 原生重点                        | MJX/Warp实现            |
| 模型格式     | URDF、MJCF及多种网格资产        | MJCF为核心              |
| 渲染         | Nyx/Luisa/Pyrender              | 调试型OpenGL渲染        |
| 传感器       | 提供较丰富统一传感器层          | 内置状态/力学传感器为主 |
| RL示例       | 有批量无人机等示例              | 生态成熟但需环境框架    |
| 控制优化     | 正在发展                        | MPC、系统辨识生态成熟   |
| 多物理       | 强项                            | 非主要目标              |
| 工程PX4/ROS2 | 需要自建                        | 同样需要自建            |

Genesis官方明确将MuJoCo列为其刚体动力学实现的参考来源之一。([GitHub](https://github.com/Genesis-Embodied-AI/Genesis "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

所以二者关系更像：

```text
MuJoCo：
    稳定、专注控制和刚体动力学

Genesis：
    更广、多物理、GPU并行、传感器和渲染一体化
```

不需要现在二选一。

---

# 9.10 Genesis 与 Gazebo 的区别

| 维度           | Genesis                          | Gazebo                         |
| -------------- | -------------------------------- | ------------------------------ |
| 核心目标       | Physical AI、RL、多物理、GPU并行 | 机器人系统工程仿真             |
| ROS2生态       | 需要自行适配                     | ros_gz成熟                     |
| PX4生态        | 非官方标准链路                   | PX4官方主要仿真路线            |
| 多环境RL       | 强                               | 不是首要设计目标               |
| MID360工程联调 | 需要自建                         | 更容易接ROS2模型               |
| 多物理场       | 强                               | 相对有限                       |
| 仿真接口       | Python原生                       | SDF、C++插件、Gazebo Transport |
| 适合阶段       | 训练与研究                       | 工程集成与验证                 |

因此：

```text
Genesis：
    负责大量训练与多物理研究

Gazebo：
    负责ROS2/PX4和工程验证
```

---

# 9.11 Genesis 与 Isaac Sim 的区别

两者都试图提供：

```text
GPU物理
机器人场景
传感器
强化学习
高质量渲染
```

但理念不同。

```text
Isaac Sim：
    NVIDIA Omniverse/RTX生态
    工业工具链和USD生态较强
    与NVIDIA硬件结合更深

Genesis：
    开源Python物理栈
    跨CUDA、ROCm、Metal、Vulkan等后端
    更强调统一多物理和研究可扩展性
```

Genesis当前源码采用Apache 2.0许可证，并通过Quadrants宣称支持多类硬件后端。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

对于我们的开源生态目标，Genesis值得重点关注；但Isaac在成熟视觉、工业资产和NVIDIA机器人生态方面仍有参考价值。

---

# 9.12 Genesis 与 UE 的关系

Genesis已经有自己的渲染路径，所以不依赖UE才能显示。

但我们仍然可以采用：

```text
Genesis：
    快速物理与RL

UE：
    高质量展示
```

统一链路：

```text
Genesis批量训练
    ↓
选出策略
    ↓
Genesis单环境或Gazebo验证
    ↓
发布VehicleState
    ↓
UE展示
```

训练阶段一般不需要UE：

```text
训练：
    Headless Genesis

评估：
    Genesis Viewer / Nyx

最终展示：
    UE
```

这能避免UE拖慢大量并行训练。

---

# 9.13 Genesis 与 ROS2/PX4 的关系

Genesis目前不是围绕ROS2和PX4构建的工程仿真器。

要接入ROS2，需要适配节点：

```text
genesis_sim_node

发布：
    odometry
    imu
    pointcloud
    motor_state
    collision

订阅：
    actuator_command
    attitude_setpoint
    velocity_setpoint

服务：
    reset
    step
    randomize
```

训练时不建议每个仿真步都经过ROS2：

```text
训练：
    Python直接调用Genesis

工程验证：
    ROS2 Adapter接入统一接口
```

PX4接入则还需要：

```text
执行器命令转换
虚拟传感器
仿真协议
坐标转换
时钟同步
```

因此第一阶段不要把Genesis改造成PX4 SITL后端。

更合理的路径是：

```text
Genesis训练策略
        ↓
导出策略
        ↓
ROS2节点或PX4外部控制器
        ↓
Gazebo + PX4验证
```

---

# 9.14 对我们最有价值的设计

## 吸收一：统一多后端Solver接口

```text
Solver
    build
    reset
    step
```

我们的物理后端也要采用统一生命周期。

## 吸收二：计算后端和用户API分离

```text
Python用户接口
    不等于
Python逐元素计算
```

高层易用与底层高性能可以并存。

## 吸收三：多环境和异构环境

平台不要只考虑：

```text
1000架完全一样的飞机
```

还要考虑：

```text
不同质量
不同电机
不同传感器
不同环境
不同任务
```

Genesis已将并行和异构环境作为仿真接口层能力。([GitHub](https://github.com/Genesis-Embodied-AI/genesis-world "GitHub - Genesis-Embodied-AI/genesis-world: Simulation platform for general-purpose robotics &amp; embodied AI learning. · GitHub"))

## 吸收四：物理、渲染、编译、接口四层分离

```text
Simulation Interface
Physics
Rendering
Compiler
```

这比把所有代码塞在一个仿真器进程里更清楚。

## 吸收五：传感器是平台一级组件

传感器不应只是物理后端里的临时插件，而应具有统一：

```text
配置
生命周期
更新频率
输出格式
噪声
批量维度
```

## 吸收六：RL示例应当随平台交付

平台不能只给物理引擎，还应提供：

```text
悬停
轨迹跟踪
风扰
电机故障
```

等标准环境，帮助用户验证安装和算法。

---

# 9.15 不应该照搬什么？

## 不照搬一：不要因为功能多就全都集成

第一阶段只需要：

```text
RigidSolver
并行环境
简单IMU
四旋翼动作
RL接口
```

软体、流体、颗粒暂时放后面。

## 不照搬二：不要轻信性能宣传数字

官方宣称其性能可比现有GPU机器人仿真器快10至80倍，但这是项目方自己的总体宣传，实际性能高度依赖：

```text
模型
碰撞
求解器
环境数量
GPU
精度
传感器
渲染
```

应通过我们的Sunray-150场景做独立基准测试，而不能直接把宣传数字写进架构决策。([Genesis World](https://genesis-world.readthedocs.io/en/latest/index.html "Genesis World — Genesis 1.0.0 documentation"))

## 不照搬三：不要让Python对象渗透整个主干

ROS2/PX4/UE主干仍以：

```text
C++
ROS消息
标准数据结构
```

为主。

Genesis的Python对象只存在于Genesis后端内部。

## 不照搬四：不要让Genesis模型成为唯一参数真源

仍然应该维护：

```text
vehicle.yaml
motor.yaml
sensor.yaml
mesh assets
```

再生成或配置：

```text
Genesis模型
MuJoCo模型
Gazebo SDF
UE资产
```

## 不照搬五：不要把RL成功当成工程成功

策略在Genesis里悬停成功，只说明：

```text
在Genesis模型和训练分布内成功
```

还必须经过：

```text
CPU/不同随机种子评估
Gazebo验证
PX4闭环验证
UE高保真验证
实机验证
```

---

# 9.16 在长期架构中的位置

```text
                           UE高保真前端
                                  ↑
                         统一VehicleState
                                  ↑
┌────────────────────────────────────────────────────┐
│                Core Simulation API                 │
│ Model / State / Action / Sensor / Clock / Env      │
└──────────↑────────────────↑────────────────↑────────┘
           │                │                │
     Gazebo Backend    MuJoCo Backend   Genesis Backend
     工程验证/PX4      控制研究/MPC      GPU RL/多物理
           │                │                │
      ROS2/PX4         Python/JAX        Python/PyTorch
```

Genesis的角色：

```text
高速批量RL后端
多物理研究后端
传感器和渲染实验后端
```

不是：

```text
当前默认PX4后端
ROS2主总线
唯一模型格式
最终UE替代品
```

---

# 9.17 最小研究任务

针对你们已下载的 `genesis-world`，建议按以下顺序研究：

```text
1. 跑通刚体基础示例
2. 理清Scene、Entity、Solver和Morph
3. 跑通官方无人机悬停示例
4. 阅读HoverEnv的observation、action和reward
5. 理清8192并行环境如何组织
6. 测试CPU、CUDA或当前硬件后端性能
7. 建立Sunray-150简化刚体模型
8. 替换质量、惯量和电机参数
9. 实现电机推力和反扭矩
10. 加入电机一阶响应
11. 加入风扰和电机退化
12. 跑通IMU和LiDAR示例
13. 建立Gymnasium兼容包装
14. 将同一控制器与MuJoCo做对比
15. 将训练策略迁移到Gazebo
16. 写Genesis REVIEW.md
```

第一阶段成功标准：

```text
Sunray-150简化模型能稳定悬停

能够：
    批量创建环境
    reset
    step
    输出观测
    接收四维动作
    注入风扰
    注入电机退化
    训练基础策略

训练后的策略：
    能在单环境中复现
    能导出并进入Gazebo验证
```

---

# 9.18 Genesis REVIEW.md 建议结构

```text
1. 项目定位
    GPU原生多物理机器人和Physical AI仿真平台

2. 它解决什么问题
    多物理场
    批量RL
    传感器
    渲染
    跨平台计算
    可微分仿真

3. 它不直接解决什么问题
    PX4官方SITL
    ROS2工程总线
    MID360完整工程模型
    实机安全系统

4. 核心设计
    Simulation Interface
    Physics
    Render
    Compiler
    Multi-Solver
    Parallel Environments

5. 我们吸收什么
    Solver统一接口
    多环境设计
    物理/渲染/编译分层
    传感器一级抽象
    GPU后端
    无人机RL示例结构

6. 是否进入主干
    作为第二阶段RL和多物理后端
    不替代Gazebo工程主干

7. 风险
    项目较新且API快速变化
    性能宣传需自行验证
    四旋翼气动仍需自建
    ROS2/PX4接口需要自建
    不同Solver可微程度不同
    多后端模型一致性难维护

8. 第一阶段用途
    悬停训练
    风扰训练
    电机退化训练
    批量参数扫描

9. 长期用途
    GPU强化学习
    多物理无人机任务
    系统辨识
    柔性负载
    复杂环境交互
```

---

# 9.19 最终判断

```text
是否进入长期项目：
    是

是否作为当前第一主干：
    否

进入哪一层：
    GPU批量训练后端
    多物理场后端
    RL实验后端

主要吸收：
    四层架构
    多Solver统一接口
    GPU原生批量仿真
    跨硬件编译
    传感器抽象
    无人机RL环境
    多环境和异构环境
    可微分基础设施

不承担：
    默认PX4 SITL
    ROS2主总线
    最终工程验证
    最终高保真UE展示
```

一句话：

> **Genesis最值得我们关注的，是它把多物理场、GPU批量环境、传感器和渲染放到统一Python接口下。它比MuJoCo覆盖更广，更适合探索高速RL和复杂物理；但项目较新，ROS2/PX4工程生态远不如Gazebo成熟，因此应作为训练和研究后端，而不是立即替代Gazebo主干。**

下一项应讲  **Flightmare** ：它专门围绕四旋翼、高速飞行、强化学习和“动力学—渲染解耦”设计，与我们当前的无人机目标非常直接。
