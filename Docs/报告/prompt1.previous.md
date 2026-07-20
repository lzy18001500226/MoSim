# MoSim Report Figure Prompt Pack

Use one prompt block at a time. Every block is self-contained and can be sent directly to an image-generation agent.

Rules:

- Generate exactly one figure from each prompt block.
- All instructional text is English.
- Text rendered inside the figure must use the exact labels listed under `Mandatory nodes` and `Mandatory connections`.
- Ordinary labels inside the figure are Simplified Chinese; established technical terms, product names, protocol names, and algorithm abbreviations remain in English.
- Do not add a figure title, figure number, caption, watermark, legend paragraph, or explanatory prose inside the generated image unless explicitly required.
- Export both PNG and editable SVG when possible.

---

## 01 Layered Architecture of the MoSim Platform

```text
Figure Subject:
Create a strict 2D engineering architecture diagram showing the complete layered structure of the MoSim quadrotor modeling, control, deployment, and evidence platform. Use a pure white background, flat vector graphics, black text, solid black 1 px node borders, and sharp arrowheads. Use pale blue for modeling modules, pale green for control modules, pale red for safety and fault modules, pale yellow for evidence modules, and pale gray for display modules. Use only the exact in-figure labels listed below.

Diagram type:
Layered system architecture diagram with compact UML-style rectangular nodes.

Layout:
Use a 16:9 horizontal canvas. Arrange five horizontal layers from top to bottom. Keep all nodes aligned to a strict grid with even spacing. Use only orthogonal vertical and horizontal connectors with 90-degree turns. The main closed-loop flow must remain visually dominant from scenario configuration through modeling, control, runtime validation, display, and evidence.

Mandatory nodes:
- Layer label: "实验配置层"
- "Model Studio"
- "Profile配置"
- "任务与场景配置"
- Layer label: "MWORKS建模与控制层"
- "整机多领域模型"
- "可组合控制器"
- "安全与故障模块"
- "结果查看器"
- Layer label: "代码生成与接口层"
- "GenerateModelCode"
- "Controller Adapter"
- "坐标系与单位转换"
- Layer label: "ROS1部署验证层"
- "PX4"
- "MAVROS"
- "px4ctrl"
- "Gazebo"
- "FAST-LIO"
- "Diff-Planner / FUEL"
- Layer label: "显示与证据层"
- "QGC"
- "RViz"
- "UE"
- "指标与报告证据"

Mandatory connections:
- "Model Studio" -> "Profile配置" -> "整机多领域模型"
- "任务与场景配置" -> "整机多领域模型"
- "整机多领域模型" <-> "可组合控制器"
- "可组合控制器" -> "安全与故障模块" -> "结果查看器"
- "可组合控制器" -> "GenerateModelCode" -> "Controller Adapter" -> "px4ctrl"
- "坐标系与单位转换" must sit between "Controller Adapter" and the runtime modules.
- "px4ctrl" -> "MAVROS" -> "PX4" -> "Gazebo"
- "Gazebo" -> "FAST-LIO" -> "Diff-Planner / FUEL" -> "px4ctrl"
- "结果查看器", "QGC", "RViz", and "UE" -> "指标与报告证据"
- Add one feedback arrow from "指标与报告证据" back to "Profile配置".

Negative constraints:
No 3D, perspective, gradients, shadows, trays, floating text, decorative icons, screenshots, photos, curved lines, diagonal lines, crossed connectors, or large empty regions. Do not imply that QGC, RViz, or UE owns the control loop. Do not add any labels not explicitly listed.
```

---

## 02 Modeling, Deployment Validation, and Parameter Feedback Loop

```text
Figure Subject:
Create a strict 2D closed-loop engineering workflow showing how MoSim moves from MWORKS model construction to simulation, generated-code deployment, physical-runtime validation, problem diagnosis, and controller parameter feedback. Use a pure white background, flat vector graphics, black text, solid black borders, and a restrained pale engineering color palette. Use only the exact in-figure labels listed below.

Diagram type:
Closed-loop lifecycle flowchart.

Layout:
Use a 16:9 horizontal canvas. Place the main forward pipeline in a single left-to-right row. Place deployment observations and diagnosis in a lower return row that flows right-to-left back to MWORKS. Use orthogonal connectors only. Use green arrows for accepted forward progress, red arrows for detected problems, and blue arrows for parameter feedback.

Mandatory nodes:
- "需求与任务定义"
- "MWORKS图形化建模"
- "控制器设计与调参"
- "MIL仿真"
- "Result.msr与原生动画"
- "GenerateModelCode"
- "SIL一致性检查"
- "ROS1 / PX4 / Gazebo部署"
- "FAST-LIO与规划任务验证"
- "运行问题分类"
- "模型失配"
- "控制参数问题"
- "接口与坐标系问题"
- "执行器与传感器问题"
- "参数回灌与模型修正"
- "报告结论与证据"

Mandatory connections:
- "需求与任务定义" -> "MWORKS图形化建模" -> "控制器设计与调参" -> "MIL仿真" -> "Result.msr与原生动画"
- "Result.msr与原生动画" -> "GenerateModelCode" -> "SIL一致性检查" -> "ROS1 / PX4 / Gazebo部署" -> "FAST-LIO与规划任务验证"
- "FAST-LIO与规划任务验证" -> "运行问题分类"
- "运行问题分类" -> "模型失配"
- "运行问题分类" -> "控制参数问题"
- "运行问题分类" -> "接口与坐标系问题"
- "运行问题分类" -> "执行器与传感器问题"
- All four problem nodes -> "参数回灌与模型修正" -> "MWORKS图形化建模"
- "Result.msr与原生动画" -> "报告结论与证据"
- "FAST-LIO与规划任务验证" -> "报告结论与证据"

Negative constraints:
No claim that generated code can be deployed without SIL and interface validation. No claim that Gazebo results replace MWORKS formal model evidence. No 3D, perspective, gradients, shadows, screenshots, decorative scenery, curved arrows, crossed lines, floating labels, or unboxed text.
```

---

## 03 Reference, State, Command, Fault, and Metrics Data Flow

```text
Figure Subject:
Create a formal 2D data-flow diagram defining the ownership and direction of reference, state, command, fault, and metrics data in MoSim. Use a pure white background, flat vector graphics, black text, solid black node borders, pale blue data nodes, pale green control nodes, pale red fault nodes, and pale yellow metrics nodes. Use only the exact in-figure labels listed below.

Diagram type:
Directed data-flow and authority-boundary diagram.

Layout:
Use a 16:9 horizontal canvas with three aligned bands. The top band contains reference authority, the middle band contains the high-frequency control loop, and the bottom band contains injection, diagnostics, and metrics. Use orthogonal connectors. Make the single command-authority path visually explicit and prevent any display module from entering the high-frequency loop.

Mandatory nodes:
- "任务参考源"
- "ReferenceFrame"
- "参考权威"
- "状态估计"
- "StateFrame"
- "控制器"
- "CommandFrame"
- "命令权威"
- "Adapter"
- "Plant / PX4"
- "传感器反馈"
- "InjectionCommand"
- "故障执行器"
- "AppliedEvent"
- "ControllerDiagnostics"
- "MetricsFrame"
- "证据存储"
- "只读显示"

Mandatory connections:
- "任务参考源" -> "ReferenceFrame" -> "参考权威" -> "控制器"
- "传感器反馈" -> "状态估计" -> "StateFrame" -> "控制器"
- "控制器" -> "CommandFrame" -> "命令权威" -> "Adapter" -> "Plant / PX4"
- "Plant / PX4" -> "传感器反馈"
- "InjectionCommand" -> "故障执行器" -> "Plant / PX4"
- "故障执行器" -> "AppliedEvent" -> "MetricsFrame"
- "控制器" -> "ControllerDiagnostics" -> "MetricsFrame"
- "StateFrame" -> "MetricsFrame"
- "ReferenceFrame" -> "MetricsFrame"
- "CommandFrame" -> "MetricsFrame"
- "MetricsFrame" -> "证据存储" -> "只读显示"
- Add a red annotation label on the fault path: "请求不等于已应用"
- Add a green annotation label on the command path: "单一发布权威"

Negative constraints:
Do not connect the read-only display node to the controller, command-authority node, or plant. Do not show a file queue inside the high-frequency control loop. No 3D, shadows, gradients, screenshots, decorative icons, curved lines, connector crossings, floating text, or unlabeled authority changes.
```

---

## 04 ENU/FLU, NED/FRD, and Quaternion Conversion

```text
Figure Subject:
Create a rigorous 2D coordinate-frame engineering diagram explaining the MoSim attitude convention and the Adapter conversion between ENU/FLU and NED/FRD. Use a pure white background, precise axes, black text, solid lines, and a limited technical color palette. Use only the exact in-figure labels listed below.

Diagram type:
Coordinate-frame definition and transformation diagram.

Layout:
Use a 16:9 horizontal canvas divided into three columns. The left column shows the world ENU frame and body FLU frame. The center column shows quaternion meaning, normalization, sign continuity, and Adapter conversion. The right column shows world NED and body FRD. Use straight lines and explicit transformation arrows. Axes may use diagonal directions only where geometrically necessary.

Mandatory nodes:
- "世界坐标系 ENU"
- Axis labels: "X East", "Y North", "Z Up"
- "机体坐标系 FLU"
- Axis labels: "X Forward", "Y Left", "Z Up"
- "q_enu_from_flu_xyzw"
- "四元数归一化"
- "符号连续性检查"
- "Adapter坐标转换"
- "世界坐标系 NED"
- Axis labels: "X North", "Y East", "Z Down"
- "机体坐标系 FRD"
- Axis labels: "X Forward", "Y Right", "Z Down"
- "内部ABI wxyz"
- "跨进程Schema xyzw"
- "frame_contract_id"

Mandatory connections:
- "机体坐标系 FLU" -> "q_enu_from_flu_xyzw" -> "世界坐标系 ENU"
- "q_enu_from_flu_xyzw" -> "四元数归一化" -> "符号连续性检查" -> "Adapter坐标转换"
- "内部ABI wxyz" -> "Adapter坐标转换" -> "跨进程Schema xyzw"
- "世界坐标系 ENU" <-> "Adapter坐标转换" <-> "世界坐标系 NED"
- "机体坐标系 FLU" <-> "Adapter坐标转换" <-> "机体坐标系 FRD"
- "frame_contract_id" must bind the complete conversion path.
- Include the exact formula inside a bordered formula node: "v_enu = R(q_enu_from_flu) v_flu"

Negative constraints:
Do not interchange quaternion order. Do not omit axis directions. Do not use an unlabeled generic XYZ frame. No decorative aircraft rendering, globe, map, 3D perspective, gradients, shadows, curved lines, or text outside bordered annotation boxes except axis labels.
```

---

## 05 Quadrotor Six-Degree-of-Freedom Forces and Moments

```text
Figure Subject:
Create a precise 2D engineering mechanics diagram for a quadrotor showing translational forces, rotational moments, rotor numbering, and the relationship between individual rotor thrusts and the total wrench. Use a white background, black technical linework, flat vector graphics, and restrained color coding. Use only the exact in-figure labels listed below.

Diagram type:
Free-body diagram plus force-and-moment allocation diagram.

Layout:
Use a 16:9 horizontal canvas. Place a top-view quadrotor free-body diagram on the left, a side-view force diagram in the center, and a compact wrench-equation block on the right. Use straight dimension and force arrows. Rotor thrust arrows must be parallel and directionally consistent.

Mandatory nodes:
- "机体系 FLU"
- "Rotor 1"
- "Rotor 2"
- "Rotor 3"
- "Rotor 4"
- "推力 f1"
- "推力 f2"
- "推力 f3"
- "推力 f4"
- "总推力 T"
- "重力 mg"
- "气动阻力"
- "滚转力矩 tau_x"
- "俯仰力矩 tau_y"
- "偏航力矩 tau_z"
- "质心"
- "惯性矩阵 J"
- Formula node: "m v_dot = R(q) T e3 - m g e3 + F_d"
- Formula node: "J omega_dot = tau - omega x J omega"
- Formula node: "[T, tau_x, tau_y, tau_z]^T = B [f1, f2, f3, f4]^T"

Mandatory connections:
- Each rotor node -> its corresponding thrust node -> "总推力 T".
- "Rotor 1", "Rotor 2", "Rotor 3", and "Rotor 4" -> "滚转力矩 tau_x", "俯仰力矩 tau_y", and "偏航力矩 tau_z" through a compact allocation block.
- "总推力 T", "重力 mg", and "气动阻力" -> translational formula node.
- "滚转力矩 tau_x", "俯仰力矩 tau_y", "偏航力矩 tau_z", and "惯性矩阵 J" -> rotational formula node.
- Show opposite rotor rotation directions with straight circular-arrow symbols near the rotor disks, without decorative rendering.

Negative constraints:
No photorealistic drone, no 3D perspective, no unexplained aerodynamic effects, no wrong thrust direction, no missing rotor numbers, no gradients, shadows, curved data connectors, decorative background, or floating formula text.
```

---

## 06 Layered Composable Control Architecture

```text
Figure Subject:
Create a strict 2D architecture diagram showing how MoSim composes planning, reference shaping, nominal control, augmentation, safety, fault-tolerant control, allocation, plant, and metrics as independent layers. Use a white background, flat vector graphics, solid black borders, and the specified pale engineering colors. Use only the exact in-figure labels listed below.

Diagram type:
Layered composable control-block architecture.

Layout:
Use a 16:9 horizontal canvas with the main signal chain in one left-to-right row. Place selectable algorithm families in compact vertical stacks directly above their owning layer. Place state feedback below the main chain. Use orthogonal connectors and one clear feedback loop.

Mandatory nodes:
- "任务与规划层"
- "轨迹与参考整形"
- "标称控制层"
- "PID族"
- "LQR / LQG"
- "SMC族"
- "MPC族"
- "NDI / INDI / Backstepping"
- "增强补偿层"
- "AWFF"
- "L1"
- "DOB / ESO / ADRC"
- "神经网络残差"
- "安全层"
- "Safety Filter"
- "CBF"
- "Reference Governor"
- "故障容错层"
- "FDI"
- "Passive FTC"
- "Active FTC"
- "控制分配器"
- "Plant"
- "状态估计"
- "统一指标"

Mandatory connections:
- "任务与规划层" -> "轨迹与参考整形" -> "标称控制层" -> "增强补偿层" -> "安全层" -> "故障容错层" -> "控制分配器" -> "Plant"
- All nominal algorithm-family nodes -> "标称控制层".
- All augmentation nodes -> "增强补偿层".
- All safety nodes -> "安全层".
- "FDI", "Passive FTC", and "Active FTC" -> "故障容错层".
- "Plant" -> "状态估计" -> "标称控制层".
- "Plant", "状态估计", and all controller layers -> "统一指标".
- Add a small label above each selectable stack: "同层单选或合法组合".

Negative constraints:
Do not draw all algorithms as one controller. Do not connect algorithms across incompatible layers without an Adapter. Do not imply arbitrary Cartesian-product compatibility. No 3D, shadows, gradients, screenshots, curved connectors, diagonal connectors, crossed lines, floating labels, or nested decorative containers.
```

---

## 07 Four Output Boundaries and Adapter Conversion

```text
Figure Subject:
Create a formal 2D interface architecture diagram separating the four controller output boundaries used by MoSim: ATTITUDE_THRUST, BODY_RATE_THRUST, WRENCH, and ROTOR_COMMAND. Show that each boundary requires its own Runner and Adapter path. Use a white background, flat vector graphics, black borders, and distinct pale colors. Use only the exact in-figure labels listed below.

Diagram type:
Parallel interface-boundary and Adapter diagram.

Layout:
Use a 16:9 horizontal canvas with four strictly separated horizontal lanes. Each lane flows left to right from controller output to a boundary-specific Runner, Adapter, inner-loop or allocator ownership, and Plant. Align corresponding stages vertically. Use orthogonal connectors only. Use a red prohibition mark between lanes to indicate that implicit cross-boundary wiring is forbidden.

Mandatory nodes:
- Lane label: "ATTITUDE_THRUST"
- "姿态与总推力控制器"
- "ATTITUDE_THRUST Runner"
- "姿态内环与allocator"
- Lane label: "BODY_RATE_THRUST"
- "角速度与总推力控制器"
- "BODY_RATE_THRUST Runner"
- "角速度内环与allocator"
- Lane label: "WRENCH"
- "力与力矩控制器"
- "WRENCH Runner"
- "控制分配器"
- Lane label: "ROTOR_COMMAND"
- "电机指令控制器"
- "ROTOR_COMMAND Runner"
- "执行器模型"
- "统一Plant与Animation"
- "单位转换"
- "限幅与有效性检查"
- "输出边界不兼容"

Mandatory connections:
- "姿态与总推力控制器" -> "ATTITUDE_THRUST Runner" -> "单位转换" -> "姿态内环与allocator" -> "统一Plant与Animation"
- "角速度与总推力控制器" -> "BODY_RATE_THRUST Runner" -> "单位转换" -> "角速度内环与allocator" -> "统一Plant与Animation"
- "力与力矩控制器" -> "WRENCH Runner" -> "单位转换" -> "控制分配器" -> "统一Plant与Animation"
- "电机指令控制器" -> "ROTOR_COMMAND Runner" -> "限幅与有效性检查" -> "执行器模型" -> "统一Plant与Animation"
- Place "限幅与有效性检查" on every lane before the Plant-facing stage, even if shown as one repeated standardized block.
- Place "输出边界不兼容" beside red blocked cross-lane arrows.

Negative constraints:
Do not merge the four Runners. Do not imply automatic conversion between output variants. Do not omit inner-loop ownership. No 3D, gradients, shadows, screenshots, curved lines, crossed lanes, floating labels, decorative icons, or unlabeled conversion blocks.
```

---

## 08 PID-INDI and NMPC-INDI Combined Innovation Structures

```text
Figure Subject:
Create a rigorous 2D comparison diagram showing two MoSim combined-control routes: improved PID outer-loop plus INDI inner-loop, and NMPC outer-loop plus INDI inner-loop. Emphasize shared interfaces, disturbance rejection, constraints, and the reason for combining the algorithms. Use a white background, flat vector graphics, black borders, pale green controller nodes, pale blue state nodes, and pale yellow comparison nodes. Use only the exact in-figure labels listed below.

Diagram type:
Dual-lane comparative control architecture.

Layout:
Use a 16:9 horizontal canvas with two parallel left-to-right lanes. The upper lane is the PID-INDI route; the lower lane is the NMPC-INDI route. Align equivalent stages vertically. Place one shared Plant and state-estimation feedback block on the right and a comparison table block at the far right. Use orthogonal connectors only.

Mandatory nodes:
- Upper lane label: "PID-INDI路线"
- "位置与速度误差"
- "增益调度PID"
- "Anti-windup与前馈"
- "期望加速度"
- "姿态与推力转换"
- "INDI姿态内环"
- Lower lane label: "NMPC-INDI路线"
- "状态与参考预测"
- "NMPC滚动优化"
- "状态与输入约束"
- "最优期望加速度"
- "统一接口"
- "角加速度反馈"
- "执行器增量控制"
- "Quadrotor Plant"
- "状态估计与滤波"
- "跟踪精度"
- "扰动恢复"
- "约束满足"
- "计算开销"

Mandatory connections:
- "位置与速度误差" -> "增益调度PID" -> "Anti-windup与前馈" -> "期望加速度" -> "姿态与推力转换" -> "INDI姿态内环"
- "状态与参考预测" -> "NMPC滚动优化".
- "状态与输入约束" -> "NMPC滚动优化" -> "最优期望加速度" -> "统一接口" -> "INDI姿态内环"
- "INDI姿态内环" -> "执行器增量控制" -> "Quadrotor Plant"
- "Quadrotor Plant" -> "状态估计与滤波" -> both outer-loop routes.
- "角加速度反馈" -> "INDI姿态内环".
- Both routes -> "跟踪精度", "扰动恢复", "约束满足", and "计算开销".

Negative constraints:
Do not show PID and NMPC running simultaneously in one nominal-control slot. Do not portray INDI as a planner. Do not omit the NMPC constraint input or the INDI angular-acceleration feedback. No 3D, gradients, shadows, screenshots, curved arrows, crossed connectors, floating text, or decorative aircraft.
```

---

## 09 Sliding-Mode Control Family and Chattering Suppression

```text
Figure Subject:
Create a strict 2D taxonomy and mechanism diagram for the MoSim sliding-mode control family, showing how each branch modifies the sliding surface, reaching law, adaptation, or approximation mechanism to reduce chattering or improve convergence. Use a white background, flat vector graphics, black borders, pale green control nodes, pale blue mechanism nodes, and pale yellow effect nodes. Use only the exact in-figure labels listed below.

Diagram type:
Algorithm-family tree combined with a compact control-loop mechanism.

Layout:
Use a 16:9 horizontal canvas. Place the SMC family root node at center-left. Branch to algorithm variants in two aligned columns. Route each variant to one mechanism node and then to one expected-effect node. Place a small common closed-loop chain along the bottom. Use orthogonal connectors and no crossing branches.

Mandatory nodes:
- "SMC控制族"
- "Boundary-Layer SMC"
- "Integral SMC"
- "Terminal SMC"
- "Non-singular Terminal SMC"
- "Super-Twisting SMC"
- "Adaptive SMC"
- "Fuzzy-SMC"
- "Neural-SMC"
- "边界层饱和函数"
- "积分滑模面"
- "有限时间收敛"
- "消除奇异项"
- "连续高阶控制"
- "在线切换增益"
- "模糊增益整定"
- "神经网络逼近"
- "抖振降低"
- "稳态误差降低"
- "扰动上界不确定性适应"
- "参考状态"
- "滑模面构造"
- "到达律"
- "Plant"
- "状态反馈"

Mandatory connections:
- "SMC控制族" -> every SMC variant.
- "Boundary-Layer SMC" -> "边界层饱和函数" -> "抖振降低"
- "Integral SMC" -> "积分滑模面" -> "稳态误差降低"
- "Terminal SMC" -> "有限时间收敛"
- "Non-singular Terminal SMC" -> "消除奇异项" -> "有限时间收敛"
- "Super-Twisting SMC" -> "连续高阶控制" -> "抖振降低"
- "Adaptive SMC" -> "在线切换增益" -> "扰动上界不确定性适应"
- "Fuzzy-SMC" -> "模糊增益整定" -> "抖振降低"
- "Neural-SMC" -> "神经网络逼近" -> "扰动上界不确定性适应"
- Bottom loop: "参考状态" -> "滑模面构造" -> "到达律" -> "Plant" -> "状态反馈" -> "滑模面构造".

Negative constraints:
Do not imply that all variants have identical convergence proofs. Do not show Neural-SMC as accepted without training and runtime evidence. No 3D, shadows, gradients, screenshots, decorative waveforms, curved connectors, crossed branches, floating labels, or dense unreadable equations.
```

---

## 10 MPC Receding-Horizon Optimization and Constraint Structure

```text
Figure Subject:
Create a formal 2D engineering diagram explaining the receding-horizon principle, objective function, prediction model, constraints, optimizer, and first-control-action execution of the MoSim MPC family. Use a white background, flat vector graphics, black borders, pale green optimization nodes, pale blue model nodes, and pale yellow evaluation nodes. Use only the exact in-figure labels listed below.

Diagram type:
Receding-horizon control loop with algorithm-family side branch.

Layout:
Use a 16:9 horizontal canvas. Place the repeated MPC loop in the center as a left-to-right pipeline. Above it, draw a compact time-horizon strip from k to k+N with predicted states and inputs. Below it, branch from the MPC family root node to the variants. Use orthogonal connectors for blocks; straight diagonal line segments are allowed only in the predicted trajectory strip.

Mandatory nodes:
- "当前状态 x(k)"
- "参考轨迹 r(k:k+N)"
- "预测模型"
- "目标函数 J"
- "状态约束"
- "输入约束"
- "障碍与安全约束"
- "在线优化器"
- "最优控制序列"
- "只执行首个控制量 u(k)"
- "Plant"
- "状态更新"
- "预测时域 N"
- "控制时域"
- "MPC控制族"
- "Linear MPC"
- "NMPC"
- "Robust MPC"
- "Adaptive MPC"
- "Tube MPC"
- "Learning MPC"
- "Explicit / Gain-Scheduled MPC"
- "Distributed MPC"
- "iLQR / MPPI"

Mandatory connections:
- "当前状态 x(k)" and "参考轨迹 r(k:k+N)" -> "预测模型".
- "预测模型", "目标函数 J", "状态约束", "输入约束", and "障碍与安全约束" -> "在线优化器".
- "在线优化器" -> "最优控制序列" -> "只执行首个控制量 u(k)" -> "Plant" -> "状态更新" -> "当前状态 x(k)".
- "预测时域 N" and "控制时域" must annotate the horizon strip.
- "MPC控制族" -> every listed MPC variant.
- Add a loop annotation: "滚动优化".

Negative constraints:
Do not show the full optimal sequence being applied at once. Do not omit constraints or state feedback. Do not claim every MPC variant shares the same solver. No 3D, shadows, gradients, screenshots, curved block connectors, crossed lines, floating labels, or decorative charts.
```

---

## 11 Composite Disturbance Compensation with L1, AWFF, DOB/ESO, and ADRC

```text
Figure Subject:
Create a strict 2D architecture diagram comparing and composing disturbance-compensation mechanisms used in MoSim: AWFF, L1 adaptive compensation, DOB, ESO, and ADRC. Clearly separate nominal control from augmentation. Use a white background, flat vector graphics, black borders, pale green nominal-control nodes, pale blue observer nodes, pale yellow augmentation nodes, and pale red disturbance nodes. Use only the exact in-figure labels listed below.

Diagram type:
Parallel augmentation-path control diagram.

Layout:
Use a 16:9 horizontal canvas. Place the nominal control chain through the center. Place four optional augmentation branches above and below the nominal command summation node. Place external disturbance and model mismatch entering the Plant from the top-right. Use orthogonal connectors and one feedback loop.

Mandatory nodes:
- "参考轨迹"
- "标称控制器"
- "标称控制量"
- "增强补偿求和"
- "Plant"
- "状态反馈"
- "外部风扰"
- "参数与模型失配"
- "AWFF"
- "风扰前馈估计"
- "L1自适应律"
- "低通滤波器"
- "DOB"
- "扰动观测值"
- "ESO"
- "扩张状态"
- "ADRC状态误差反馈"
- "补偿量限幅"
- "ControllerDiagnostics"

Mandatory connections:
- "参考轨迹" -> "标称控制器" -> "标称控制量" -> "增强补偿求和" -> "Plant" -> "状态反馈" -> "标称控制器".
- "外部风扰" and "参数与模型失配" -> "Plant".
- "风扰前馈估计" -> "AWFF" -> "补偿量限幅" -> "增强补偿求和".
- "状态反馈" -> "L1自适应律" -> "低通滤波器" -> "补偿量限幅".
- "状态反馈" -> "DOB" -> "扰动观测值" -> "补偿量限幅".
- "状态反馈" -> "ESO" -> "扩张状态" -> "ADRC状态误差反馈" -> "补偿量限幅".
- All augmentation paths -> "ControllerDiagnostics".
- Add a label beside the branches: "按Profile选择合法增强组合".

Negative constraints:
Do not label AWFF as an independent nominal controller. Do not show all augmentation branches active by default. Do not omit filtering or output limiting. No 3D, shadows, gradients, screenshots, curved lines, crossed connectors, decorative disturbance waves, or floating labels.
```

---

## 12 Neural Residual Compensation and RL Gain Scheduling

```text
Figure Subject:
Create a rigorous 2D engineering diagram separating two learning-based enhancement routes in MoSim: neural residual compensation and reinforcement-learning gain scheduling. Show offline training, frozen artifacts, runtime inference, confidence gating, fallback, and the nominal controller that remains authoritative. Use a white background, flat vector graphics, black borders, pale green controller nodes, pale blue learning nodes, pale yellow data nodes, and pale red safety gates. Use only the exact in-figure labels listed below.

Diagram type:
Dual-route learning-control lifecycle and runtime diagram.

Layout:
Use a 16:9 horizontal canvas split vertically. The left half shows offline data and training. The right half shows two parallel runtime branches converging on a nominal control chain. Place fallback and safety gating directly before the command summation or gain update. Use orthogonal connectors only.

Mandatory nodes:
- "仿真与运行数据"
- "状态误差与扰动特征"
- "训练集与验证集"
- "Neural Residual训练"
- "RL策略训练"
- "冻结权重与版本哈希"
- Runtime route label: "神经网络残差补偿"
- "在线特征归一化"
- "残差控制量"
- Runtime route label: "RL增益调度"
- "状态与性能特征"
- "增益修正量"
- "标称控制器"
- "置信度与范围门禁"
- "输出限幅"
- "确定性回退"
- "最终控制指令"
- "Plant"
- "运行指标与事件"

Mandatory connections:
- "仿真与运行数据" -> "状态误差与扰动特征" -> "训练集与验证集".
- "训练集与验证集" -> "Neural Residual训练" -> "冻结权重与版本哈希".
- "训练集与验证集" -> "RL策略训练" -> "冻结权重与版本哈希".
- "冻结权重与版本哈希" -> "在线特征归一化" -> "残差控制量" -> "置信度与范围门禁".
- "冻结权重与版本哈希" -> "状态与性能特征" -> "增益修正量" -> "置信度与范围门禁".
- "标称控制器" -> "最终控制指令".
- "置信度与范围门禁" -> "输出限幅" -> either nominal gain update or residual summation before "最终控制指令".
- Rejected gate output -> "确定性回退" -> "标称控制器".
- "最终控制指令" -> "Plant" -> "运行指标与事件".

Negative constraints:
Do not portray neural residual compensation as full controller replacement. Do not portray RL as unrestricted online exploration during flight. Do not claim Neural-SMC training in this figure. No 3D, gradients, shadows, screenshots, brain icons, decorative neural meshes, curved lines, crossed connectors, or floating labels.
```

---

## 13 Safety Filter, CBF, Reference Governor, and Emergency State Machine

```text
Figure Subject:
Create a formal 2D safety architecture diagram showing how nominal commands are checked and modified by a Safety Filter, CBF, Reference Governor, geofence, actuator limits, and an emergency state machine. Use a white background, flat vector graphics, black borders, pale green nominal nodes, pale red safety nodes, pale yellow diagnostics nodes, and clear state-transition arrows. Use only the exact in-figure labels listed below.

Diagram type:
Safety-control pipeline plus finite-state machine.

Layout:
Use a 16:9 horizontal canvas. Place the command-safety pipeline across the top. Place the emergency state machine across the bottom in one aligned row. Connect safety violations from the top pipeline to the relevant state transitions below. Use orthogonal connectors only.

Mandatory nodes:
- "标称参考与控制指令"
- "Reference Governor"
- "Safety Filter"
- "CBF约束"
- "Geofence"
- "姿态与速度限制"
- "推力与电机限制"
- "安全控制指令"
- "安全干预量"
- "状态与约束监测"
- State: "正常运行"
- State: "性能降级"
- State: "回退悬停"
- State: "受控降落"
- State: "安全停止"
- State: "任务完成"
- "Emergency Stop请求"
- "Return-and-Land请求"
- "PX4 failsafe"
- "事件与证据记录"

Mandatory connections:
- "标称参考与控制指令" -> "Reference Governor" -> "Safety Filter" -> "安全控制指令".
- "CBF约束", "Geofence", "姿态与速度限制", and "推力与电机限制" -> "Safety Filter".
- "Safety Filter" -> "安全干预量" -> "事件与证据记录".
- "状态与约束监测" -> all emergency-state transitions.
- "正常运行" -> "性能降级" -> "回退悬停" -> "受控降落" -> "任务完成".
- "Emergency Stop请求" -> "安全停止".
- "Return-and-Land请求" -> "受控降落".
- "PX4 failsafe" -> "受控降落" or "安全停止" with two explicitly labeled branches: "仍可控" and "不可控".
- Every state transition -> "事件与证据记录".

Negative constraints:
Do not reduce the safety layer to simple saturation only. Do not show Emergency Stop as direct uncontrolled motor cutoff while airborne. Do not omit state-based arbitration. No 3D, gradients, shadows, screenshots, curved arrows, crossed transitions, decorative warning icons, or floating labels.
```

---

## 14 Fault Injection, FDI, FTC, and Control Allocation Reconstruction

```text
Figure Subject:
Create a strict 2D fault-tolerant-control closed-loop diagram covering fault request, actual application, detection, persistence confirmation, isolation, effectiveness estimation, passive or active FTC, allocation reconstruction, recovery, and safe landing. Use a white background, flat vector graphics, black borders, red fault paths, green recovery paths, pale blue control nodes, and pale yellow evidence nodes. Use only the exact in-figure labels listed below.

Diagram type:
Fault injection and recovery control-loop diagram.

Layout:
Use a 16:9 horizontal canvas. Place the injection transaction across the top, FDI and FTC processing in the center, and the vehicle feedback loop along the bottom. Keep the sequence strictly left to right. Use orthogonal connectors only and make requested versus applied values visually distinct.

Mandatory nodes:
- "InjectionCommand"
- "command_id / run_id / rotor_index"
- "requested_value"
- "故障执行器"
- "AppliedEvent"
- "applied_value"
- "电机转速与推力"
- "姿态与控制残差"
- "FDI故障检测"
- "持续性判定"
- "故障电机隔离"
- "效率估计"
- "故障掩码"
- "Passive FTC"
- "Active FTC"
- "故障感知控制分配器"
- "四电机重构指令"
- "Quadrotor Plant"
- "恢复正常控制"
- "单电机安全降落"
- "事务式恢复"
- "partial_failure"

Mandatory connections:
- "InjectionCommand" -> "command_id / run_id / rotor_index" -> "requested_value" -> "故障执行器" -> "Quadrotor Plant".
- "故障执行器" -> "AppliedEvent" -> "applied_value".
- "Quadrotor Plant" -> "电机转速与推力" and "姿态与控制残差".
- "电机转速与推力" and "姿态与控制残差" -> "FDI故障检测" -> "持续性判定" -> "故障电机隔离" -> "效率估计" -> "故障掩码".
- "故障掩码" -> "Passive FTC" and "Active FTC" -> "故障感知控制分配器" -> "四电机重构指令" -> "Quadrotor Plant".
- Successful recovery -> "恢复正常控制".
- Insufficient control authority -> "单电机安全降落".
- "事务式恢复" -> "故障执行器"; incomplete restoration -> "partial_failure".
- Add the exact annotation: "请求已接收不等于故障已应用".

Negative constraints:
Do not infer applied motor effectiveness from actuator output alone. Do not skip detection or isolation. Do not show accepted request as successful fault application. No 3D, gradients, shadows, screenshots, curved arrows, crossed lines, decorative failure explosions, or floating labels.
```

---

## 15 Reconfigurable Three-UAV Formation in a Complex Obstacle Map

```text
Figure Subject:
Create a strict 2D top-down planning diagram showing three UAVs maintaining a triangular formation in open regions, reconfiguring into a line or time-separated passage in narrow corridors, avoiding obstacles, and restoring the formation afterward. Use a white background, light-gray obstacles, black borders, three clearly distinct trajectory colors, and exact labels only.

Diagram type:
Top-down multi-UAV formation planning and reconfiguration diagram.

Layout:
Use a 16:9 canvas representing an approximately 90 m by 60 m environment. Place the start formation at the lower left and the target formation at the upper right. Include walls, columns, a narrow corridor, and an open area. Draw three continuous trajectories with clear separation. Place decision blocks outside the map boundary and connect them using straight orthogonal callout lines.

Mandatory nodes:
- "三角起始编队"
- "UAV1"
- "UAV2"
- "UAV3"
- "墙体"
- "柱体障碍"
- "窄通道"
- "开放区域"
- "局部地图"
- "通道宽度判断"
- "编队保持"
- "队形重构"
- "纵列通过"
- "分时通过"
- "局部重规划"
- "恢复三角编队"
- "三角目标编队"
- "障碍膨胀边界"
- "最小机间距离"
- "最小障碍净空"

Mandatory connections:
- "三角起始编队" -> "开放区域" -> "编队保持".
- "局部地图" -> "通道宽度判断".
- Wide path branch: "通道宽度判断" -> "编队保持".
- Narrow path branch: "通道宽度判断" -> "队形重构" -> "纵列通过" or "分时通过".
- Obstacle conflict -> "局部重规划" -> updated UAV trajectories.
- Passage completion -> "恢复三角编队" -> "三角目标编队".
- Mark "障碍膨胀边界", "最小机间距离", and "最小障碍净空" directly on the map using bordered callouts.

Negative constraints:
Do not draw a rigid triangular formation through the narrow corridor. Do not claim unknown-map autonomous exploration. Do not merge the three UAV paths. No 3D, perspective, terrain texture, photorealism, decorative scenery, curved callout connectors, trajectory intersections, unlabeled obstacles, or floating prose.
```

---

## 16 MWORKS Real-Time Co-Simulation Control, ROS1 Data, and MAVLink Flight Planes

```text
Figure Subject:
Create a strict 2D three-plane communication architecture for MWORKS real-time co-simulation with Model Studio, QGC, Orchestrator, ROS1, MAVROS, PX4, and Gazebo. Clearly separate low-frequency control-plane traffic, high-frequency real-time data, and standard MAVLink flight operations. Use a white background, black borders, flat vector graphics, and a distinct pale color for each plane. Use only the exact in-figure labels listed below.

Diagram type:
Three-plane communication and authority architecture.

Layout:
Use a 16:9 horizontal canvas with three horizontal bands. Place the GUI control plane at the top, the ROS1 real-time data plane in the middle, and the MAVLink flight plane at the bottom. Place Orchestrator at the left boundary between planes but outside the 100 Hz loop. Use orthogonal connectors only. Use thicker arrows for the real-time loop and thinner arrows for control-plane requests.

Mandatory nodes:
- Plane label: "GUI控制面"
- "Model Studio"
- "QGC"
- "Orchestrator"
- "Profile发布与prepare_run"
- "任务与故障命令"
- "异步ACK"
- Plane label: "ROS1实时数据面"
- "MWORKS实时Adapter"
- "StateFrame"
- "ReferenceFrame"
- "AttitudeThrustCommand"
- "ControllerDiagnostics"
- "InjectionCommand / AppliedEvent"
- "px4ctrl"
- "Gazebo插件"
- Plane label: "MAVLink飞行面"
- "MAVROS"
- "PX4"
- "连接与模式"
- "解锁、起飞、任务与降落"
- "标准遥测与COMMAND_ACK"
- "候选能力，需RT0门禁验证"
- "高频控制链不经过GUI或文件队列"

Mandatory connections:
- "Model Studio" <-> "Orchestrator" through "Profile发布与prepare_run" and "异步ACK".
- "QGC" <-> "Orchestrator" through "任务与故障命令" and "异步ACK".
- "MWORKS实时Adapter" <-> "StateFrame", "ReferenceFrame", "AttitudeThrustCommand", and "ControllerDiagnostics".
- "AttitudeThrustCommand" -> one command authority -> "px4ctrl" or "MAVROS".
- "InjectionCommand / AppliedEvent" <-> "Gazebo插件".
- "QGC" <-> "MAVROS" <-> "PX4" through the standard flight-plane nodes.
- "PX4" <-> "Gazebo插件".
- Place "高频控制链不经过GUI或文件队列" directly beside the middle band.
- Bind "候选能力，需RT0门禁验证" to "MWORKS实时Adapter".

Negative constraints:
Do not route 100 Hz control through QGC, Orchestrator, HTTP, or a file queue. Do not give Model Studio arm or takeoff authority. Do not show concurrent MWORKS and px4ctrl setpoint publishers. No 3D, gradients, shadows, screenshots, curved lines, crossed planes, floating labels, or decorative network clouds.
```

---

## 17 GenerateModelCode, MIL/SIL Consistency, and Gazebo Deployment

```text
Figure Subject:
Create a strict 2D engineering pipeline showing model validation, fixed Profile parameters, GenerateModelCode, compilation, generated-code SIL, MIL/SIL numerical comparison, Controller Adapter integration, ROS1 build, PX4/Gazebo deployment, and feedback to MWORKS. Use a white background, flat vector graphics, black borders, pale blue model nodes, pale green code nodes, pale yellow validation nodes, and pale red failure paths. Use only the exact in-figure labels listed below.

Diagram type:
Code-generation, verification, and deployment pipeline.

Layout:
Use a 16:9 horizontal canvas. Place the successful path in one left-to-right row. Place provenance information in a narrow row above. Place failure feedback loops in a row below. Use orthogonal connectors only and maintain a compact layout.

Mandatory nodes:
- "MWORKS控制器模型"
- "模型检查"
- "冻结Profile与参数"
- "GenerateModelCode"
- "C / C++源码与头文件"
- "编译与静态检查"
- "CFunction SIL夹具"
- "MIL / SIL数值比较"
- "Controller Adapter"
- "px4ctrl构建"
- "ROS1运行"
- "MAVROS / PX4"
- "Gazebo / Sunray任务验证"
- "controller_id"
- "output_variant"
- "parameter_hash"
- "source_commit"
- "generated_hash"
- "代码生成失败"
- "数值不一致"
- "接口与坐标系异常"
- "性能不满足门限"
- "返回MWORKS修正"

Mandatory connections:
- "MWORKS控制器模型" -> "模型检查" -> "冻结Profile与参数" -> "GenerateModelCode" -> "C / C++源码与头文件" -> "编译与静态检查" -> "CFunction SIL夹具" -> "MIL / SIL数值比较" -> "Controller Adapter" -> "px4ctrl构建" -> "ROS1运行" -> "MAVROS / PX4" -> "Gazebo / Sunray任务验证".
- All provenance nodes must bind "冻结Profile与参数", generated files, and deployment evidence.
- "代码生成失败" -> "返回MWORKS修正" -> "MWORKS控制器模型".
- "数值不一致" -> "返回MWORKS修正".
- "接口与坐标系异常" -> "Controller Adapter".
- "性能不满足门限" -> "返回MWORKS修正".
- Add the exact annotation: "生成成功不等于部署验收通过".

Negative constraints:
Do not draw a one-click path that skips checks. Do not claim generated source alone as runtime evidence. Do not omit provenance hashes. No 3D, gradients, shadows, screenshots, curved lines, crossed feedback paths, floating labels, or decorative code icons.
```

---

## 18 MID360, FAST-LIO, PX4 Fusion, and Ground-Truth Evaluation

```text
Figure Subject:
Create a formal 2D data-flow diagram for MID360 point clouds, IMU synchronization, FAST-LIO estimation, PX4 external-vision fusion, planner input, RViz display, and independent Gazebo ground-truth evaluation. Use a white background, flat vector graphics, black borders, pale blue sensor and estimation nodes, pale green flight nodes, pale yellow evaluation nodes, and gray display nodes. Use only the exact in-figure labels listed below.

Diagram type:
Localization, mapping, fusion, and evaluation data-flow diagram.

Layout:
Use a 16:9 horizontal canvas. Put sensor inputs on the left, FAST-LIO processing in the center, and fusion/planning/display outputs on the right. Put Gazebo truth and evaluation in a separate bottom lane that never feeds the controller. Use orthogonal connectors only.

Mandatory nodes:
- "MID360点云"
- "IMU数据"
- "时间戳检查"
- "外参转换"
- "数据同步"
- "FAST-LIO"
- "IMU传播"
- "点云去畸变"
- "局部地图"
- "迭代误差状态更新"
- "里程计输出"
- "累计点云"
- "MAVROS ODOMETRY"
- "PX4外部视觉融合"
- "统一状态源"
- "Diff-Planner / FUEL地图输入"
- "RViz点云与轨迹"
- "Gazebo truth"
- "独立真值评价"
- "位置误差与漂移"
- "频率与延迟"
- "点云非空性"

Mandatory connections:
- "MID360点云" -> "时间戳检查" -> "外参转换" -> "数据同步" -> "FAST-LIO".
- "IMU数据" -> "时间戳检查" -> "数据同步" -> "FAST-LIO".
- "FAST-LIO" contains or connects through "IMU传播", "点云去畸变", "局部地图", and "迭代误差状态更新".
- "FAST-LIO" -> "里程计输出" and "累计点云".
- "里程计输出" -> "MAVROS ODOMETRY" -> "PX4外部视觉融合" -> "统一状态源".
- "局部地图" -> "Diff-Planner / FUEL地图输入".
- "累计点云" and "里程计输出" -> "RViz点云与轨迹".
- "Gazebo truth" -> "独立真值评价".
- "里程计输出" -> "独立真值评价" -> "位置误差与漂移", "频率与延迟", and "点云非空性".

Negative constraints:
Do not feed "Gazebo truth" into the controller, FAST-LIO, or planner. Do not mix truth and estimated odometry. Do not omit time synchronization or extrinsics. No 3D, gradients, shadows, screenshots, decorative point clouds, curved connectors, crossed lines, or floating labels.
```

---

## 19 Diff-Planner Single-UAV and Three-UAV Adaptation

```text
Figure Subject:
Create a strict 2D dual-lane architecture diagram showing MoSim adaptation of Diff-Planner for one UAV and three UAVs, including goal input, map input, trajectory optimization, trajectory server, px4ctrl tracking, state feedback, and inter-UAV predicted-trajectory exchange. Use a white background, flat vector graphics, black borders, pale blue planning nodes, pale green control nodes, and pale yellow evaluation nodes. Use only the exact in-figure labels listed below.

Diagram type:
Single-UAV versus three-UAV planning-adaptation comparison.

Layout:
Use a 16:9 horizontal canvas with two separated lanes. The upper lane is the single-UAV path. The lower lane contains three compact parallel sublanes for UAV1, UAV2, and UAV3. Align common stages vertically. Use orthogonal connectors only and distinct thin colors for the three UAV paths.

Mandatory nodes:
- Upper lane label: "单机已知目标点规划"
- "目标点"
- "Planner Adapter"
- "Diff-Planner"
- "局部地图与障碍膨胀"
- "轨迹优化"
- "PolyTraj / position_cmd"
- "Trajectory Server"
- "px4ctrl"
- "UAV1"
- "FAST-LIO / MAVROS里程计"
- Lower lane label: "三机独立目标与基础避碰"
- "UAV1目标"
- "UAV2目标"
- "UAV3目标"
- "UAV1规划器与控制器"
- "UAV2规划器与控制器"
- "UAV3规划器与控制器"
- "broadcast_traj"
- "预测轨迹交换"
- "基础避碰"
- "Gazebo"
- "RViz"
- "轨迹与安全指标"
- "不是自主探索"
- "不等同于固定编队控制"

Mandatory connections:
- Upper lane: "目标点" -> "Planner Adapter" -> "Diff-Planner" -> "轨迹优化" -> "PolyTraj / position_cmd" -> "Trajectory Server" -> "px4ctrl" -> "UAV1".
- "局部地图与障碍膨胀" -> "Diff-Planner".
- "FAST-LIO / MAVROS里程计" -> "Diff-Planner" and "px4ctrl".
- Lower lane: each UAV goal -> its corresponding planner and controller -> its UAV runtime path.
- All three UAV planner paths <-> "broadcast_traj" -> "预测轨迹交换" -> "基础避碰".
- Both lanes -> "Gazebo", "RViz", and "轨迹与安全指标".
- Bind "不是自主探索" and "不等同于固定编队控制" as bordered scope labels beside the lower-right evidence outputs.

Negative constraints:
Do not portray Diff-Planner as unknown-area exploration. Do not portray three independent goals as a self-designed formation controller. Do not omit odometry feedback or predicted-trajectory exchange. No 3D, gradients, shadows, screenshots, curved lines, crossed sublanes, decorative map imagery, or floating prose.
```

---

## 20 FUEL Frontier Exploration and Control Tracking Loop

```text
Figure Subject:
Create a strict 2D autonomous-exploration closed-loop diagram showing point-cloud preprocessing, occupancy-map update, frontier extraction, frontier clustering, information-gain evaluation, next-best-view selection, path search, trajectory optimization, controller tracking, and map feedback. Use a white background, flat vector graphics, black borders, pale blue mapping nodes, pale green planning and control nodes, and pale yellow metrics nodes. Use only the exact in-figure labels listed below.

Diagram type:
Frontier-based autonomous-exploration control loop.

Layout:
Use a 16:9 horizontal canvas. Place the main exploration pipeline in a single left-to-right row. Place map feedback below the pipeline as a return path. Place evaluation metrics in a compact right-side column. Add a small separate task-boundary comparison at the bottom-right. Use orthogonal connectors only.

Mandatory nodes:
- "传感器点云"
- "滤波与坐标转换"
- "占据栅格 / 体素地图"
- "地图更新"
- "前沿提取"
- "前沿聚类"
- "信息增益与代价评价"
- "下一最佳视点"
- "路径搜索"
- "动力学约束轨迹优化"
- "Trajectory Adapter"
- "px4ctrl"
- "无人机执行"
- "新点云反馈"
- "探索覆盖率"
- "有效前沿数量"
- "轨迹长度与飞行时间"
- "最小障碍距离"
- "规划失败次数"
- "已知目标点 Diff-Planner"
- "未知区域 FUEL探索"
- "任务边界不同"

Mandatory connections:
- "传感器点云" -> "滤波与坐标转换" -> "占据栅格 / 体素地图" -> "地图更新" -> "前沿提取" -> "前沿聚类" -> "信息增益与代价评价" -> "下一最佳视点" -> "路径搜索" -> "动力学约束轨迹优化" -> "Trajectory Adapter" -> "px4ctrl" -> "无人机执行".
- "无人机执行" -> "新点云反馈" -> "传感器点云".
- "占据栅格 / 体素地图" -> "路径搜索".
- "地图更新", "下一最佳视点", "动力学约束轨迹优化", and "无人机执行" -> all listed metrics.
- "已知目标点 Diff-Planner" and "未知区域 FUEL探索" -> "任务边界不同".
- Add the exact scope annotation: "FUEL不是控制器算法".

Negative constraints:
Do not merge FUEL with Diff-Planner. Do not claim control-performance improvement solely from exploration coverage. Do not omit closed-loop map feedback. No 3D, gradients, shadows, screenshots, decorative terrain, curved lines, crossed connectors, floating labels, or added task claims.
```

---

## Recommended Drawing Order

1. Figures 01, 02, 03, 06, 07, 16, and 17.
2. Figures 04 and 05.
3. Figures 08 through 14.
4. Figure 15.
5. Figures 18 through 20.

Use real screenshots instead of additional hand-drawn figures for the MWORKS whole-aircraft model, motor and sensor subsystem models, Model Studio UI, MWORKS Result Viewer animation, controller Sysblock models, controller result curves, QGC, RViz, UE, point clouds, maps, and runtime windows.
