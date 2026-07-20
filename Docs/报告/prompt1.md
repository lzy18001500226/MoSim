# MoSim 仿真分析报告自绘图 Prompt Pack

本文件用于生成《仿真分析报告》正文中的自绘架构图、流程图、原理图和数据流图。每个代码块都是一条可以单独使用的完整提示词，不依赖其他提示词。

统一要求：

- 一次只生成一张图。
- 图内不出现图号、图名、Figure、Caption、水印或页眉页脚，图名由Word题注统一添加。
- 除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest、PID、INDI、NMPC、SMC、L1、AWFF、FDI、FTC等专有名词外，全部使用简体中文。
- 使用纯白背景、黑色文字和黑色连线；核心模块使用浅蓝色，控制模块使用浅绿色，安全与故障模块使用浅红色，数据与评价模块使用浅黄色，显示模块使用浅灰色。
- 所有文字必须位于带黑色细边框的矩形或圆角矩形内，不允许文字悬空。
- 采用严格二维矢量工程图风格，不使用三维透视、阴影、渐变、装饰图标、人物、照片、卡通元素。
- 连线优先使用水平或垂直正交线，转折为90度，箭头清晰，避免交叉；反馈路径可用虚线，但必须在图例中说明。
- 画布优先使用16:9横向构图，四周留白均匀，字号适合插入A4论文后阅读。
- 必须准确呈现下列节点和连接，不增加未经说明的系统能力。

---

## 图1 MoSim总体分层架构

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张高质量二维工程架构图，纯白背景，16:9横向构图，黑色文字和正交箭头。图内不要放图名。

采用自上而下五层结构，每层节点独立排列，不使用包围整层的大色块：
第一层“实验配置与任务层”：Model Studio、Experiment Profile、任务与场景配置；
第二层“MWORKS建模与验证层”：多领域整机模型、控制器模型、MIL/SIL、指标计算、GenerateModelCode；
第三层“飞行控制与运行层”：px4ctrl、PX4、MAVROS、唯一控制权威；
第四层“物理与算法环境层”：Gazebo/Sunray、传感器与故障、FAST-LIO、Diff-Planner、FUEL、多机编队；
第五层“显示与证据层”：MWORKS结果查看器、RViz、UE、QGC、日志与报告图表。

必须连接：Experiment Profile指向MWORKS模型和运行环境；MWORKS控制器经GenerateModelCode指向px4ctrl；px4ctrl经MAVROS/PX4驱动Gazebo/Sunray；Gazebo传感器数据指向FAST-LIO；FAST-LIO状态和地图指向Diff-Planner与FUEL；规划轨迹指向px4ctrl；所有层的结果汇入日志与报告图表。用虚线反馈箭头从部署指标返回MWORKS参数优化。明确标注“控制器设计权威”“运行Plant权威”“显示不参与控制”。
```

## 图2 建模、部署与反馈优化闭环

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张严格二维闭环流程图，纯白背景，横向主流程，黑色正交箭头，图内不要放图名。

主流程依次为：赛题需求分析 -> 场景与指标定义 -> MWORKS多领域建模 -> 控制器设计 -> 模型检查 -> MIL仿真 -> 参数优化 -> SIL与生成代码一致性 -> GenerateModelCode -> ROS1/PX4/Gazebo部署 -> 典型任务与扰动故障验证 -> 指标提取 -> 问题定位 -> MWORKS等效复现 -> 参数与结构再优化 -> 复验 -> 报告结论。

将“模型检查失败”“性能未达门限”“代码一致性失败”“部署异常”画成四个菱形判定节点，失败路径分别返回模型、控制器、Adapter或参数环节。成功路径用实线，问题反馈路径用红色虚线。右下角增加证据输出节点：Result.msr、曲线、指标JSON、截图、日志、视频。突出这是可重复迭代的闭环，不是单向演示流程。
```

## 图3 控制、状态与评价数据流

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维数据流图，白色背景，横向布局，图内不要放图名。用不同颜色区分参考数据、状态数据、控制指令、故障事件和评价数据，并在右下角放小型图例。

节点从左到右：任务与轨迹源、Reference Adapter、统一ReferenceFrame、控制器与增强层、安全层、Command Adapter、执行器与四旋翼Plant、传感器、状态估计、统一StateFrame、指标与证据系统、结果显示。

连接关系：任务与轨迹源依次经过Reference Adapter和ReferenceFrame进入控制器；控制器输出经过增强层和安全层，再经Command Adapter驱动Plant；Plant状态经过传感器与状态估计生成StateFrame，反馈给控制器；风扰与电机效率故障直接进入Plant并产生AppliedEvent；参考、状态、控制量、故障事件同时进入指标与证据系统；显示系统只读取状态和结果，不向控制回路写入。明确标注“唯一指令发布者”和“显示只读”。
```

## 图4 项目核心文件结构

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张工程目录树图，纯白背景，左侧为根目录MoSim，向右展开一级和关键二级目录，使用正交树状连线，图内不要放图名。

一级目录必须包括：Models、Config、Scripts、Results、Docs、apps、References。
Models下包括MoSimQuadrotorModel、QuadrotorControllerBlocks、QuadrotorExperiments；Config下包括控制器注册表、Experiment Profiles、场景配置、兼容矩阵；Scripts下包括仿真运行、指标计算、代码生成、证据整理；Results下包括MWORKS、control_platform、sunray_ros1、planning、ui_platform；Docs下包括Design、Workflows、报告；apps下包括model_studio；References标注“冻结的上游参考源码”。

每个一级目录旁添加一句简短职责说明。使用小标签区分“源码”“配置”“生成结果”“文档”“第三方参考”。不要展示缓存、备份、临时目录和个人路径。
```

## 图5 坐标系与四旋翼姿态定义

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维技术示意图，白色背景，左侧画世界坐标系ENU，右侧画四旋翼俯视轮廓和机体系FLU，图内不要放图名。

世界坐标系明确标注X东、Y北、Z上；机体系明确标注X前、Y左、Z上。四旋翼机体中心标记质心，四个旋翼编号为1至4，并用箭头标出相邻旋翼相反转向。标出滚转角、俯仰角、偏航角及正方向。中间用旋转矩阵和四元数节点连接两个坐标系，标注“q_enu_from_flu，跨进程顺序xyzw”“内部控制核心可使用wxyz，由Adapter显式转换”。增加NED/FRD小型转换节点，但不得画成主要坐标系。
```

## 图6 四旋翼六自由度受力与力矩

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张论文级二维受力分析图，白色背景，中心为简化四旋翼，图内不要放图名。

四个旋翼分别画向上的推力F1、F2、F3、F4；质心处画总推力T、重力mg、机体三轴气动阻力；标出机臂长度l。围绕机体三轴标出滚转力矩、俯仰力矩、偏航力矩。右侧增加紧凑公式关系框，只显示符号关系：总推力由四个旋翼推力求和，滚转和俯仰力矩由对置旋翼推力差产生，偏航力矩由旋翼反扭矩差产生。所有箭头方向必须物理一致，不画三维渲染和复杂背景。
```

## 图7 电机、电调、旋翼与气动力链

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张从控制指令到气动力的二维信号链图，白色背景，横向正交布局，图内不要放图名。

节点依次为：归一化电机指令 -> 电调动态 -> 电机电气模型 -> 电机机械模型 -> 转速与角速度 -> 桨叶推力模型 -> 反扭矩模型 -> 机体合力与合力矩。

在电调动态旁标出饱和、延迟和一阶响应；电机模型标出电阻、电感、反电动势、转动惯量；旋翼模型标出推力系数和力矩系数。增加“效率因子eta_i”从上方乘入桨叶推力和反扭矩节点，eta_i=1表示正常，0到1表示效率下降。底部增加转速、推力、电流三个观测输出，连接到故障检测模块。
```

## 图8 四电机执行机构与效率故障模型

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张左右对称的二维模块图，白色背景，图内不要放图名。左侧为控制分配器，中间为四条并行电机通道，右侧为合力与力矩。

控制分配器输入为总推力、滚转力矩、俯仰力矩、偏航力矩；输出为u1、u2、u3、u4。每条电机通道均包含限幅、电调、电机、效率因子eta_i、旋翼推力。四条通道汇入合力与力矩计算。故障注入命令从上方进入指定效率因子；AppliedEvent从效率因子返回故障管理器。强调requested_value与applied_value分离，恢复命令令eta1至eta4回到1。0。用红色突出单电机效率下降路径。
```

## 图9 传感器、机载计算机与飞控组成

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维整机电子与信息架构图，白色背景，中心为飞控和机载计算机，外围为传感器与执行器，图内不要放图名。

必须包含：IMU、激光雷达MID360、气压计、磁力计、GPS候选接口、电池与电源、飞控PX4、机载计算机ROS1、MAVROS、四个电调与电机、QGC。IMU等低层传感器连接PX4；MID360连接ROS1和FAST-LIO；PX4与ROS1通过MAVROS双向通信；PX4输出执行器命令到电调；QGC通过MAVLink读取飞行状态和发送任务级命令。明确标注当前Factory场景不依赖GPS，Gazebo传感器噪声属于Plant侧。
```

## 图10 MWORKS整机多领域模型组成

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张仿照系统工程白皮书的二维多领域模型结构图，白色背景，图内不要放图名。不要模仿软件截图，而是重绘逻辑结构。

中央为“六自由度机体与STL几何”，左侧依次为任务轨迹、位置控制器、姿态与角速度内环、控制分配；下方为四套电调、电机和旋翼；右侧为IMU、位置速度传感器、激光雷达接口和状态输出；上方为风场、重力、地面与障碍物环境。四套执行器连接机体，机体状态反馈到传感器和控制器，几何状态连接结果查看器动画。用不同浅色区分控制域、电气域、机械域、环境域和显示域。
```

## 图11 MWORKS原生三维动画生成机制

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维数据映射流程图，白色背景，图内不要放图名。

从左到右依次为：MWORKS求解器 -> 机体位置与姿态 -> 坐标与四元数转换 -> STL机体变换 -> 四个桨叶局部旋转 -> 障碍物与地面几何 -> 结果查看器三维动画。下方并行画出Result.msr -> 曲线变量选择 -> 轨迹与状态曲线。强调动画和曲线来自同一次仿真的统一时间轴，不是预制视频。标注“求解速度可快于或慢于物理时间”“动画显示不参与控制计算”。
```

## 图12 分层可组合控制架构

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张纵向分层控制架构图，白色背景，图内不要放图名。

从上到下依次为：任务模式与目标点、轨迹规划层、位置与平动外环、姿态与角速度内环、增强与扰动补偿层、安全过滤与参考治理层、FDI与FTC层、控制分配层、四电机Plant。右侧画统一StateFrame自下而上反馈，左侧画ReferenceFrame自上而下传递。

每层列出代表算法：外环含Official PID、LQR/LQI、NMPC、DFBC；姿态内环含PX4内环、INDI、SO(3)、SMC；增强层含AWFF、L1、DOB/ESO、ADRC、神经网络残差、RL增益调度；安全层含Safety Filter、CBF、Reference Governor；FTC层含检测、隔离、重构和安全降落。用红色禁止符号表示输出边界不兼容的模块不能直接连接。
```

## 图13 四类控制输出边界与Runner

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张四列对照式二维架构图，白色背景，图内不要放图名。四列分别为ATTITUDE_THRUST、BODY_RATE_THRUST、WRENCH、ROTOR_COMMAND。

每列从上到下画：适用控制器 -> 标准输出 -> Adapter -> 内环或控制分配所有者 -> Plant。ATTITUDE_THRUST输出期望姿态和总推力，在线v1由PX4姿态与角速度内环拥有；BODY_RATE_THRUST输出机体系角速度和总推力；WRENCH输出三轴力与三轴力矩；ROTOR_COMMAND直接输出四个旋翼命令。四列之间不画横向连接，顶部用红色说明“禁止隐式跨输出边界连接”。底部标注离线Runner与在线Adapter必须分别验证。
```

## 图14 统一Adapter与接口合同

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维接口转换图，白色背景，横向布局，图内不要放图名。

左侧为不同来源：MWORKS模型、生成C/C++控制器、px4ctrl原生控制器；中间为统一接口：ReferenceFrame、StateFrame、ControllerCommand、ControllerDiagnostics、InjectionCommand、AppliedEvent；右侧为四类Command Adapter和ROS1/PX4/Gazebo接口。

在Adapter内部明确画出单位转换、ENU/FLU与NED/FRD转换、四元数xyzw与wxyz转换、推力N到归一化推力转换、饱和与新鲜度检查。每帧携带run_id、profile_hash、sequence、source_stamp。异常输出进入安全回退，而不是直接进入执行器。
```

## 图15 Profile、兼容矩阵与RunManifest

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维配置冻结流程图，白色背景，图内不要放图名。

左侧为Model Studio分层选择：任务、UAV数量、地图、外环、内环、增强层、安全层、故障层；中间为兼容矩阵检查，包含输出边界、状态需求、参数完整性、代码生成能力、场景适用性五个门禁；通过后生成Experiment Profile并计算profile_hash；QGC侧生成Mission Artifact和mission_hash；两者交给Orchestrator生成不可变RunManifest；右侧输出MWORKS仿真、生成代码部署和结果目录。

失败组合返回明确禁用原因。区分Certified Profile和Custom Compatible Profile：前者已有完整证据，后者仿真成功后仍需验收才能标记accepted。
```

## 图16 Model Studio三模式职责边界

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张三列二维产品职责图，白色背景，图内不要放图名。

第一列“在线建模验证”：选择控制器组合、UAV数量、地图和场景，应用配置，打开MWORKS模型，人工点击仿真，在结果查看器查看曲线与动画。
第二列“实时联合仿真”：选择合法控制器组合、应用风扰与电机效率配置、显示连接状态与通信延迟、打开联合仿真模型；标注实时能力由RT门禁验证。
第三列“生成代码部署”：选择已验证Profile、生成C/C++、构建、发布，进入QGC执行飞行任务；不提供在线风扰滑块。

底部画Orchestrator作为唯一命令裁决者，QGC负责解锁、起飞、任务、降落和安全停止，Model Studio不直接操作PX4飞行命令。
```

## 图17 PID控制族演进关系

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张由左向右演进的二维控制族关系图，白色背景，图内不要放图名。

从Official PID基线开始，分支到级联PID、Anti-windup、Feedforward Profile、增益调度PID、Fuzzy PID、Neural PID和PID-INDI。每个节点下方用一行短语说明改进点：多环解耦、积分饱和抑制、参考前馈、工况调度、模糊在线修正、神经残差修正、增量动态逆补偿。所有分支最终汇入统一ATTITUDE_THRUST输出边界。用虚线连接到统一实验与指标节点，说明各算法在同一Plant和场景下对比。
```

## 图18 级联PID、抗饱和与前馈融合

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张详细二维控制框图，白色背景，图内不要放图名。

外环位置误差进入位置PID，输出期望速度；速度误差进入速度PID，输出期望加速度；前馈轨迹提供速度、加速度和必要的jerk，分别加到对应通道；加速度经姿态推力投影生成期望姿态与总推力。执行器饱和检测产生饱和差值，通过反算Anti-windup路径返回积分器。状态反馈包括位置、速度、姿态。标出积分限幅、输出限幅、微分滤波和重力补偿。
```

## 图19 增益调度、模糊与神经PID

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张三列并列的二维控制对比图，白色背景，图内不要放图名。

第一列“增益调度PID”：高度、速度、误差幅值和任务阶段进入调度器，插值得到Kp、Ki、Kd，再进入PID。
第二列“Fuzzy PID”：误差e和误差变化率de进入模糊化、规则库、推理、解模糊，输出增益修正量。
第三列“Neural PID”：状态特征归一化后进入冻结神经网络，输出受限增益或残差修正，并设置信心门限与回退。

三列使用相同参考、状态、Plant和评价指标，底部共同输出期望姿态与总推力。明确神经网络只做有界补偿，不画成完全替代全部飞控。
```

## 图20 现代、鲁棒与非线性控制族谱

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维分类树，白色背景，图内不要放图名。

根节点为“MoSim控制器族”，分为五个主分支：线性最优与状态反馈、鲁棒控制、非线性控制、滑模控制、预测控制。
线性最优包括LQR、LQI、LQG、Pole Placement + Luenberger、H2 State Feedback；鲁棒控制包括H∞、L1 Adaptive、Passivity-Based Control；非线性控制包括Feedback Linearization、NDI、INDI、Backstepping、Adaptive Backstepping、SO(3)、SE(3)、DFBC；滑模包括Boundary-Layer SMC、Integral SMC、Terminal SMC、Non-singular Terminal SMC、Super-Twisting SMC、Adaptive SMC、Fuzzy-SMC、Neural-SMC；预测控制包括Linear MPC、NMPC Outer、Robust MPC、Tube MPC、Adaptive MPC、Learning MPC、Distributed MPC、iLQR/MPPI。

用小标签标记“已实现”“实验”“阻塞”，不要虚构全部accepted。
```

## 图21 滑模控制族与抖振抑制

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维原理与演进图，白色背景，图内不要放图名。

左侧画误差状态进入滑模面s，控制律分为等效控制和切换控制，合成后驱动Plant。中间画Boundary Layer使用饱和函数替代符号函数以降低抖振。右侧按演进关系排列Integral SMC、Terminal SMC、Non-singular Terminal SMC、Super-Twisting SMC、Adaptive SMC、Fuzzy-SMC、Neural-SMC，并分别标注积分消除稳态误差、有限时间收敛、避免奇异、连续高阶切换、自适应增益、模糊增益、神经扰动估计。底部画模型不确定性与外扰进入Plant，观测误差反馈到滑模面。
```

## 图22 INDI、NDI与Backstepping控制关系

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张三列二维原理对比图，白色背景，图内不要放图名。

NDI列：参考动态 -> 完整非线性模型求逆 -> 控制量 -> Plant。
INDI列：当前角加速度和上一周期控制量 -> 局部增量模型 -> 控制增量 -> 控制量累加 -> Plant，突出降低对完整模型精度依赖。
Backstepping列：位置误差 -> 虚拟速度控制 -> 速度误差 -> 虚拟姿态控制 -> 姿态误差 -> 实际控制量，突出递归Lyapunov设计。

三列共享状态估计、限幅和安全层。用注释说明PID-INDI由名义PID和INDI增量补偿融合，NMPC-INDI由预测外环和INDI姿态内环组合。
```

## 图23 MPC控制族预测与约束结构

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维滚动优化结构图，白色背景，图内不要放图名。

参考轨迹和当前状态进入预测模型；预测模型在预测时域内生成状态序列；目标函数包含跟踪误差、控制增量、平滑性和终端代价；约束模块包含位置、速度、姿态、推力、控制变化率和安全距离；优化器输出第一步控制量，下一周期滚动重算。

右侧列出Linear MPC、NMPC Outer、Robust MPC、Tube MPC、Adaptive MPC、Learning MPC、Explicit/Gain-Scheduled MPC、Distributed MPC、iLQR/MPPI，并用箭头指出它们对预测模型、鲁棒管束、在线辨识、学习残差或分布式耦合的不同扩展。NMPC Outer输出期望加速度，再经INDI或PX4内环执行。
```

## 图24 AWFF、L1、DOB/ESO与ADRC增强层

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维增强层组合图，白色背景，图内不要放图名。

中央为名义控制器，输出u_nominal。上方为轨迹前馈和AWFF，基于参考速度、加速度和风扰估计生成u_ff；下方并列L1 Adaptive、DOB、ESO、ADRC四个扰动估计器，使用状态误差和控制输入估计总扰动，生成有界补偿u_comp；两者经权重、限幅和变化率限制后与名义控制量合成。

合成结果进入Safety Filter，再进入Plant。Plant受到风扰、参数摄动和未建模动力学影响。所有增强模块均画旁路开关，关闭时保持名义控制器输出，异常时回退而不是继续放大补偿。
```

## 图25 神经网络残差与强化学习调度

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张两列二维智能增强结构图，白色背景，图内不要放图名。

左列“神经网络残差补偿”：状态与误差特征 -> 归一化 -> 冻结12-12-3神经网络 -> tanh -> 三轴残差加速度限幅正负0.6米每二次方秒 -> 与名义加速度合成 -> 姿态推力投影。标出训练数据为合成域随机化样本，运行时只做推理。

右列“强化学习增益调度”：状态特征 -> 冻结策略 -> 动作限幅 -> PID或增强增益调制 -> 名义控制器。两列均包含输入合法性、置信度、输出限幅、fallback_active和安全层。明确智能算法是增强层，不直接拥有电机命令权威。
```

## 图26 安全过滤、参考治理与应急状态机

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维安全控制架构图，白色背景，图内不要放图名。

名义控制指令首先进入通用Safety Filter和CBF约束；任务参考进入Reference Governor和Geofence；飞行状态、通信健康、控制器健康、估计器健康进入Failsafe状态机。三路在安全监督器中统一仲裁，动作优先级依次为正常控制、约束修正、悬停、返航、受控降落、安全停止。

右侧画状态机：ready_on_ground -> arming -> taking_off -> hovering -> mission_active -> hovering -> landing -> completed；异常分支为degraded -> fallback_hover -> landing或safe_stop。强调安全层可以修改或拒绝命令，但不能绕过唯一命令权威。
```

## 图27 故障注入、FDI、FTC与控制重构闭环

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张从左到右的二维故障容错闭环图，白色背景，图内不要放图名。

InjectionCommand携带command_id、vehicle_id、run_id、rotor_index和requested_value，进入Gazebo或MWORKS故障执行器；执行器应用电机效率下降并返回AppliedEvent与applied_value。电机转速、推力、姿态残差和控制残差进入FDI，依次完成检测、持续性判定、故障电机隔离和效率估计。FTC根据故障掩码选择Passive FTC或Active FTC，并进入故障感知控制分配器重构四电机命令。恢复成功进入正常控制，无法恢复进入单电机安全降落。

用红色显示故障路径，绿色显示恢复路径。明确“请求已接收”不等于“故障已应用”。
```

## 图28 统一仿真、指标与证据生成流水线

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维自动化实验流水线图，白色背景，横向布局，图内不要放图名。

节点依次为：选择Certified或Custom Profile -> 兼容性检查 -> 生成薄Wrapper -> 打开统一Runner -> MWORKS模型检查 -> 仿真 -> Result.msr -> 变量导出 -> 指标计算 -> 状态判定 -> 曲线生成 -> 截图与动画 -> 正文结论。

指标节点列出RMSE、最大误差、稳态误差、调节时间、超调量、控制平滑性、故障恢复时间、最小机间距离和最小障碍净空。状态判定分为accepted、executed_blocked、not_run。所有结果绑定run_id、profile_hash、模型入口和证据路径。失败结果也进入负样本分析，不被删除。
```

## 图29 基础轨迹与扰动故障时间线

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张上下两部分的二维实验设计图，白色背景，图内不要放图名。

上半部分并列画五种参考任务的小型轨迹示意：起飞悬停降落、位置阶跃、平面8字、三维螺旋、复杂地图目标点轨迹。每种只画简洁坐标轴和轨迹，不画装饰。

下半部分画统一时间轴：初始化、起飞、稳态悬停、注入风扰、恢复、注入1号电机效率下降、FDI确认、FTC重构、恢复正常、降落。用不同色带标出基线窗口、扰动窗口、故障窗口和恢复评价窗口。标注风扰强度、电机效率eta1和关键指标采样区间。
```

## 图30 多机编队控制分层结构

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张三机编队二维架构图，白色背景，图内不要放图名。

顶层为任务目标与编队中心轨迹；编队控制层并列Leader-Follower、Virtual Structure、Consensus、Containment、Formation Tracking、Formation Reconfiguration、Fault-Tolerant Formation、Formation CBF、Distributed MPC；中间为每架无人机独立参考轨迹和碰撞约束；下层为UAV1、UAV2、UAV3各自的位置控制器、姿态内环和Plant。

画出邻接通信图和每架无人机的局部状态交换，但每架无人机控制回路保持独立。明确Diff-Planner swarm是多机规划工程基线，不等同于自研编队控制；编队误差、机间距离和障碍净空进入统一指标系统。
```

## 图31 复杂地图可重构编队避障流程

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维俯视规划示意图，白色背景，图内不要放图名。画布比例近似90米乘60米，包含墙体、柱体、窄通道和开放区，用浅灰色表示障碍。

左下角三架无人机以三角队形起飞，右上角为三角终点队形。宽阔区域保持三角编队；进入窄通道前经过“通道宽度判断”和“队形重构”节点，变为纵列或分时通行；穿越后恢复三角队形。分别画UAV1、UAV2、UAV3三条不同颜色轨迹，并标出局部重规划、最小机间距离、障碍膨胀边界和恢复队形位置。不要画成全程刚性固定编队，也不要宣称未知地图自主探索。
```

## 图32 MWORKS实时联合仿真三平面架构

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张三层二维通信架构图，白色背景，图内不要放图名。

第一层“GUI控制面”：Model Studio、QGC、Orchestrator，传输Profile发布、prepare_run、任务命令、故障命令和异步ACK；注明文件队列或本地IPC只适合低频控制面。
第二层“ROS1实时数据面”：MWORKS实时Adapter、px4ctrl、Gazebo插件、StateFrame、ReferenceFrame、AttitudeThrustCommand、ControllerDiagnostics、InjectionCommand、AppliedEvent；标注高频控制链不经过GUI和文件队列。
第三层“MAVLink飞行面”：QGC、MAVROS、PX4，传输连接、模式、解锁、起飞、任务、降落、标准遥测与COMMAND_ACK。

Orchestrator位于三层交汇处但不进入100Hz控制回路。将mworks_live标记为“候选能力，需RT0门禁验证”。
```

## 图33 自动代码生成与部署链路

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维工程流水线图，白色背景，横向布局，图内不要放图名。

从左到右依次为：MWORKS控制器模型 -> 模型检查 -> 固定Profile与参数 -> GenerateModelCode -> 生成C/C++源码与头文件 -> 编译与静态检查 -> CFunction SIL夹具 -> MIL/SIL数值比较 -> Controller Adapter -> px4ctrl构建 -> ROS1运行 -> MAVROS/PX4 -> Gazebo/Sunray任务验证。

上方画版本与追溯信息：controller_id、output_variant、parameter_hash、source_commit、generated_hash。下方画失败回路：代码生成失败返回模型，数值不一致返回类型与采样检查，运行异常返回Adapter与坐标系检查，性能不足返回MWORKS调参。不得画成一键生成后无需验证即可飞行。
```

## 图34 MIL、SIL与Gazebo跨平台一致性验证

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张三通道二维对比图，白色背景，图内不要放图名。

统一Experiment Profile、参考轨迹和初始条件分成三路：MWORKS MIL模型、生成代码SIL、ROS1/PX4/Gazebo部署。MIL与SIL比较控制器输入输出、最大绝对差和均方差；MWORKS与Gazebo比较轨迹RMSE、最大误差、控制响应、扰动恢复和故障状态。三路输出汇入统一时间对齐、坐标系转换和指标计算模块。

右侧结果分为“数值等价”“趋势一致但物理环境不同”“接口或参数异常”。明确Gazebo包含执行器、传感器噪声、通信延迟和PX4状态机，因此不要求曲线逐点完全相同。
```

## 图35 FAST-LIO定位与建图适配流程

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维激光雷达惯性里程计数据流图，白色背景，图内不要放图名。

MID360点云和IMU数据分别经过时间戳检查、外参转换和数据同步，进入FAST-LIO；FAST-LIO内部画出IMU传播、点云去畸变、局部地图、迭代误差状态更新和位姿输出；输出包括里程计、累计点云和局部地图。里程计先进入独立真值评价，再通过PX4外部视觉或里程计融合进入统一MAVROS状态源，不能直接与Gazebo truth混用。

右侧连接RViz显示、Diff-Planner地图输入和指标计算。指标包括位置误差、漂移、频率、延迟和点云非空性。Gazebo truth只连接评价模块，不连接控制器。
```

## 图36 Diff-Planner单机与三机适配流程

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张上下双通道二维规划架构图，白色背景，图内不要放图名。

上通道为单机：目标点 -> Planner Adapter -> Diff-Planner -> 局部地图与障碍膨胀 -> 轨迹优化 -> PolyTraj与position_cmd -> Trajectory Server -> px4ctrl -> UAV1。状态与FAST-LIO/MAVROS里程计反馈给规划器和控制器。

下通道为三机：分别为UAV1、UAV2、UAV3建立独立规划器、轨迹服务器和控制器；三机通过broadcast_traj交换预测轨迹并进行基础避碰；每架无人机接收独立目标点。右侧输出到Gazebo、RViz和指标模块。明确这是已知目标点规划工程基线，不是自主探索，也不等同于自研固定编队。
```

## 图37 FUEL自主探索适配流程

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维自主探索闭环图，白色背景，图内不要放图名。

传感器点云经过滤波与坐标转换进入占据栅格或体素地图；地图更新进入前沿提取；前沿聚类与收益评价选择下一最佳视点；路径搜索生成几何路径；轨迹优化生成满足动力学约束的轨迹；Trajectory Adapter转换为px4ctrl参考；无人机执行后产生新点云，闭环返回地图更新。

右侧画评价模块：探索覆盖率、有效前沿数量、轨迹长度、飞行时间、最小障碍距离、规划失败次数。将“已知目标点Diff-Planner”和“未知区域FUEL探索”画成两个明确不同的任务入口。不要把FUEL结果写成控制器算法本身的性能提升。
```

## 图38 QGC、RViz、UE与结果查看器显示职责

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维多视图显示架构图，白色背景，图内不要放图名。

中央为运行数据源：MWORKS结果、ROS1 topics、PX4/MAVROS遥测、Gazebo真值与传感器。四个只读显示节点分别为：MWORKS结果查看器，显示曲线、变量和原生STL动画；RViz，显示点云、栅格、轨迹和TF；UE，显示高质量场景、飞机姿态和轨迹残影；QGC，显示连接、模式、位置姿态、任务、故障与安全状态。

QGC的飞行命令通过Orchestrator和MAVROS进入PX4；其他显示节点不拥有控制权。所有显示画面和日志汇入视频与报告证据。明确Gazebo/PX4/MAVROS仍是在线运行权威，UE不提供控制真值。
```

## 图39 部署问题回灌与控制器再优化

```text
统一风格：严格二维矢量工程图，16:9横向，纯白背景，黑色文字、黑色细边框和正交箭头；核心模块浅蓝色，控制模块浅绿色，安全与故障模块浅红色，数据与评价模块浅黄色，显示模块浅灰色；除MWORKS、Sysplorer、Sysblock、Model Studio、MIL、SIL、ROS1、PX4、MAVROS、Gazebo、FAST-LIO、Diff-Planner、FUEL、RViz、UE、QGC、Adapter、Profile、RunManifest及控制算法缩写外，全部使用简体中文；所有文字必须放在边框节点内；禁止图名、图号、水印、3D、透视、阴影、渐变、照片、卡通和装饰元素；字号清晰，文字不得截断，连线避免交叉。

生成一张二维因果闭环图，白色背景，图内不要放图名。

左侧为部署现象：跟踪误差增大、姿态振荡、控制饱和、风扰恢复慢、电机故障后偏航、规划轨迹不可跟踪、坐标系或时间戳异常。中间为问题分类：控制器参数、模型失配、执行器动态、传感器噪声、Adapter与坐标系、状态机与安全门限、规划轨迹动态约束。右侧为MWORKS等效复现场景和调整动作：增益调度、Anti-windup、前馈、INDI、L1/AWFF、Safety Filter、FTC重构、轨迹平滑。

调整后依次经过MIL、SIL、GenerateModelCode和Gazebo复验，输出优化前后指标对比。用虚线反馈回路连接到问题分类。强调无法修复或收益过低的路线进入“止损并保留负样本”，不能标记accepted。
```

---

## 建议绘制顺序

优先完成最能体现总体工作量且对正文结构影响最大的图：

1. 图1、图2、图3、图12、图13、图33、图34。
2. 图5至图11的动力学与整机建模图。
3. 图17至图27的控制器、增强、安全和FTC图。
4. 图30至图32的编队与联合仿真图。
5. 图35至图38的FAST-LIO、Diff-Planner、FUEL与显示平台图。
6. 图4、图15、图16、图28、图29、图39等工程流程与总结图。

生成后建议导出PNG和可编辑SVG两种格式。PNG用于快速插入Word，SVG用于后续修改错字、调整箭头和统一字体。最终图片统一放入 `Docs/报告/图/` 对应分类目录。
