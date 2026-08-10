# 项目综合实践 III 图件提示词

本文件覆盖正文中需要绘制的八张规范图件。图 4-2 的云纵 150 装配图、图 4-9 和图 4-10 的 Studio 界面均使用项目已有的真实素材，不用生成式图片替代。每个代码块只生成一张图；图号和图题由正文统一排版，不在生成图外额外添加图例或长段说明。

全局约定（适用于全部八张图）：

- 拉丁字母标识符一律逐字保留，不得翻译、缩写或改写大小写：MWORKS、Modelica、Sysblock、Studio、QGC、RViz、UE、ROS1、PX4、Gazebo、C99、ABI、SIL、JSON、CSV、FormalRunner、CheckModel、Profile、Adapter、Plant，以及文件名 Result.msr、METRICS.json、RUN_MANIFEST.json。含斜杠的复合标签（例如 `ROS1/PX4/Gazebo`、`QGC / RViz / UE`）必须完整保留斜杠与全部条目，不得省略其中任何一项。
- 中文文字须与拉丁标识符同等清晰地渲染，不得压缩、截断或省略。
- 每张图都必须画出该图指定的 UML note 或边界标注。边界声明不允许只写在 Negative constraints 里而不出现在图面上：Negative constraints 只约束生成，读者看不到。
- 每张图都必须按该图声明的画布比例排版；不得为适配更窄的画布而缩小文字或截断标签。

## 图 3-1：MoSim 系统用例图

```text
Figure Subject:
Create a standard UML use-case diagram for the MoSim quadrotor simulation and control platform. The diagram explains who uses the system and which core activities they perform. It is a requirements model, not a class diagram, runtime topology, screenshot, or performance claim.

Diagram type:
Standard UML use-case diagram. Use stick-figure actors, one visible system boundary, ellipses for use cases, and plain association lines.

System boundary:
Label the boundary "MoSim 四旋翼仿真与控制平台".

Layout:
Use a 16:9 canvas. Place the single system boundary in the centre, "使用者" to its left, and the three external actors to its right.
- Left: place "使用者" as one stick figure, vertically centred against the boundary.
- Right: stack "维护者", "MWORKS 仿真环境", and "ROS1/PX4/Gazebo" from top to bottom in exactly that order.
- Inside the boundary, use two columns. Left column, top to bottom: "配置实验任务", "运行模型检查与仿真", "查看指标与结果". Right column, top to bottom: "生成 C99 并完成 SIL", "登记运行时任务与记录".
- Align "生成 C99 并完成 SIL" to the same vertical height as "维护者", and "登记运行时任务与记录" to the same vertical height as "ROS1/PX4/Gazebo".
- Keep the right column clear at the vertical height of "运行模型检查与仿真": no ellipse may occupy that band in the right column, so the associations from "维护者" and "MWORKS 仿真环境" can reach the left column horizontally without passing through any ellipse.

Mandatory associations:
- 使用者 connects to 配置实验任务, 运行模型检查与仿真, and 查看指标与结果.
- 维护者 connects to 运行模型检查与仿真 and 生成 C99 并完成 SIL.
- MWORKS 仿真环境 connects only to 运行模型检查与仿真.
- ROS1/PX4/Gazebo connects only to 登记运行时任务与记录.

Routing:
"运行模型检查与仿真" receives three associations. Attach them at three distinct points on its ellipse boundary: the association from "使用者" on its left side, and the associations from "维护者" and "MWORKS 仿真环境" on its right side at two different heights. Route every association as an orthogonal or straight segment. No association may cross another, and none may pass through an ellipse or through the actor figures.

Mandatory UML notes:
- Note attached to "MWORKS 仿真环境": "外部仿真环境；通过接口参与，不代表已通过验收"
- Note attached to "ROS1/PX4/Gazebo": "外部运行时；仅参与任务与记录登记"
- Note attached to "生成 C99 并完成 SIL": "SIL 为软件在环；不等同于实机验证"

Visual requirements:
White background, light blue system boundary, dark thin association lines, blue ellipse outlines, ample whitespace, no crossing lines, and legible Chinese text. Draw associations as undirected lines, not sequence arrows.

Negative constraints:
Do not place classes, attributes, methods, flowchart diamonds, state nodes, databases, screenshots, 3D aircraft models, metrics curves, pass/fail labels, or runtime-success claims in this figure. External systems participate through interfaces only; do not imply they have passed acceptance.
```

## 图 4-1：MoSim 分层软件体系结构图

```text
Figure Subject:
Create a two-dimensional layered software architecture diagram for MoSim. The figure must show responsibility boundaries between the operator surface, delivery/runtime path, experiment execution, controller interface, and physical model. It is not a UML class diagram and not a real-time data-flow screenshot.

Layout:
Use a 16:9 canvas with five horizontal layers stacked top to bottom. Each layer is one full-width band containing a colored layer label in a narrow left column and three equally sized rounded module boxes aligned in a row to its right. All five layer bands have the same height; all fifteen module boxes have the same width and height, and the three columns are vertically aligned across all five layers.
Between each pair of adjacent layers, draw exactly one vertical arrow on the horizontal centre axis of the canvas, pointing downward. Four arrows total. Each arrow denotes the dependency direction between the two adjacent layers as a whole: the upper layer depends on the lower layer.

Mandatory layers and modules:
1. 操作与辅助层: "MoSim Studio", "QGC / RViz / UE", "只读本地助手".
2. 交付与运行层: "代码生成与 C99 ABI", "ROS1/PX4/Gazebo 适配器", "构建与 SIL".
3. 实验执行层: "任务 Profile", "FormalRunner", "原始结果与指标".
4. 控制器接口层: "控制器实现", "Adapter 与输出合同", "控制分配".
5. 物理模型层: "Modelica 公共 Plant", "旋翼执行器", "参数 Profile".

Module box sizing:
The longest labels are "代码生成与 C99 ABI", "ROS1/PX4/Gazebo 适配器", "Modelica 公共 Plant", and "Adapter 与输出合同". Size every module box wide enough that each of these renders on at most two lines at full text size. Do not shrink label text to fit a box, and do not let any label overflow its box.

Layer label colors:
操作与辅助层 pale blue; 交付与运行层 pale orange; 实验执行层 pale green; 控制器接口层 pale yellow; 物理模型层 pale violet.

Mandatory notes:
- Note attached to "只读本地助手": "只读辅助；不产生指标，不改变模型"
- Note attached to "构建与 SIL": "SIL 为软件在环；不等同于实机验证"
- Note attached to "原始结果与指标": "指标由原始结果计算；显示软件不是指标来源"

Visual requirements:
White background; restrained pale blue, orange, green, yellow, and violet layer labels; white module boxes with thin dark borders; blue vertical arrows; no gradients, shadows, decorative icons, screenshots, or three-dimensional rendering. Keep every label within its box.

Negative constraints:
Do not draw one arrow per column between layers, and do not draw any arrow between two individual module boxes. Column alignment is a visual grid only; a module in one layer is not paired with, and does not feed, the module directly above or below it. Specifically, do not imply that "只读本地助手" drives "构建与 SIL", that "原始结果与指标" is an input to "控制分配", or that "参数 Profile" is produced by "控制分配". Modules inside one layer are peers, not a pipeline. Do not claim that the UI proves a model check, that a runtime adapter proves formal simulation, or that display software is the source of metrics. Do not turn the layers into a left-to-right process or a UML class diagram.
```

## 图 4-3：正式实验核心活动图

```text
Figure Subject:
Create a standard UML activity diagram for the formal experiment path. It must distinguish task configuration, configuration validation, CheckModel, formal simulation, valid-result handling, one configuration retry loop, and two failure exits.

Diagram type:
UML activity diagram with a filled start circle, rounded action nodes, diamond decision nodes, directional arrows, and filled final nodes.

Layout:
Use a tall 2:3 portrait canvas. Place the entire main path as one strictly vertical column on the horizontal centre axis, in this top-to-bottom order: start circle, "配置任务与控制器", "校验任务配置", decision "配置有效", "执行 CheckModel", decision "检查通过", "启动正式仿真", decision "结果有效", "归档结果并计算指标", final node.
Reserve the left margin exclusively for the retry loop and the right margin exclusively for the two failure exits. Nothing else may occupy either margin.

Main path:
Start -> "配置任务与控制器" -> "校验任务配置" -> decision "配置有效" -> "执行 CheckModel" -> decision "检查通过" -> "启动正式仿真" -> decision "结果有效" -> "归档结果并计算指标" -> final.

Retry loop (left margin only):
配置无效 leaves the left side of decision "配置有效", goes to "配置无效，修改任务" placed in the left margin, then returns upward as one orthogonal path into the left side of "校验任务配置". This loop must stay entirely within the left margin and must not cross any main-path arrow.

Failure exits (right margin only):
- 检查未通过 leaves the right side of decision "检查通过", goes to "检查未通过，记录失败" in the right margin, then to its own filled final node immediately below it.
- 结果无效 leaves the right side of decision "结果有效", goes to "结果无效，记录中断" in the right margin, then to its own filled final node immediately below it.
Give each failure exit its own final node so the two exit paths never converge and never cross. Because "检查通过" sits above "结果有效" on the main path, the first failure exit and its final node must both sit above the second failure exit in the right margin.

Guard labels:
Label both outgoing edges of every decision. decision "配置有效": [有效] downward, [无效] leftward. decision "检查通过": [通过] downward, [未通过] rightward. decision "结果有效": [有效] downward, [无效] rightward.

Mandatory notes:
- Note attached to "执行 CheckModel": "检查通过仅允许进入下一活动；不是性能结论"
- Note attached to "归档结果并计算指标": "指标由归档结果计算；不代表验收通过"
- Note attached to "结果无效，记录中断": "中断按失败记录；不计入有效结果"

Visual requirements:
Use one vertical main path, pale blue configuration actions, pale green formal-execution actions, pale yellow decisions, pale orange/red failure actions, and straight orthogonal non-crossing arrows. Chinese labels must be complete and legible.

Negative constraints:
Do not route the retry loop through the right margin or the failure exits through the left margin. Do not merge the two failure exits into one shared final node. Do not add timing estimates, numerical performance thresholds, solver settings, actual run results, screenshots, class boxes, lifelines, or claims that any controller has passed. A CheckModel pass only permits the next activity; it is not a performance conclusion.
```

## 图 4-8：配置到报告的数据流图

```text
Figure Subject:
Create a software data-flow diagram for traceable report data. Show how project profiles become task configuration, how execution produces raw results, and how raw results plus a runtime manifest support metrics and report figures.

Layout and objects:
Use a wide 2:1 canvas with an upper band holding the main row and a lower band holding the runtime manifest.
In the upper band, place five boxes in one horizontally aligned left-to-right row, all at the same vertical height and the same box height:
1. "机体 Profile / 路由合同 / 实验 Profile".
2. "任务配置 / JSON / Modelica harness".
3. "MWORKS / Modelica / FormalRunner / 或运行时后端".
4. "原始结果 / Result.msr / CSV".
5. "指标与报告 / METRICS.json / 图表与正文".
Render each box label as stacked lines, one slash-separated item per line, with the slashes removed. Every box must be wide enough for its longest line at full size; box 3 is the widest and sets the minimum column width. Do not shrink text to fit.
In the lower band, place "运行清单 / RUN_MANIFEST.json / 后端与生命周期状态" horizontally centred beneath the gap between box 3 and box 4.

Arrow routing:
Draw four blue arrows along the upper band, each one a single short horizontal segment between adjacent boxes: 1->2, 2->3, 3->4, 4->5.
Draw the first red arrow from the bottom edge of box 3 straight down into the top edge of the runtime manifest box.
Draw the second red arrow from the right edge of the runtime manifest box as an orthogonal path: horizontally rightward through the lower band, passing below box 4 without touching it, then vertically upward into the bottom edge of box 5.
Use orthogonal connectors only. The red path must stay in the lower band until its final upward segment, so it never overlaps the blue row and never crosses any blue arrow.

Mandatory notes:
- Note attached to the runtime manifest box: "运行清单记录后端与生命周期状态；不代表运行通过"
- Note attached to box 4: "原始结果为运行产物；指标由其计算得出"

Visual requirements:
White background, thin dark borders, no overlap, and enough width for every file name. Colour the five main-row boxes pale blue, pale yellow, pale green, pale orange, and pale violet from left to right; colour the runtime manifest box pale gray. Use ordinary data-flow arrows only.

Negative constraints:
Do not route the red arrows through the upper band or let them cross the blue row. Do not draw a database, an OCR step, manual screenshot entry, a closed-loop feedback arrow, a performance pass badge, or an invented runtime result. The diagram describes provenance, not acceptance status.
```

## 图 4-4 至图 4-7：四张标准 UML 类图

下列四个代码块分别独立使用，每个代码块只生成一张标准 UML 类图。图中必须使用标准 UML 类框：上部为类名和 stereotype，中部为属性，下部为操作。属性和操作均使用可见性符号、名称、类型、参数和返回值。类框之间只使用标准 UML 关系：继承、组合、聚合、关联或依赖；不要把普通数据流箭头画成流程图箭头。

统一制图要求：白色背景、二维工程制图风格、黑色细边框、正交走线、类框对齐、留白充足、禁止连线交叉。抽象类名使用斜体；组合使用实心菱形；聚合使用空心菱形；继承使用空心三角箭头；依赖使用虚线箭头；关联线只有在明确声明可导航时才加箭头，并在两端标出角色名和多重性。不要画时序生命线、状态节点、流程框、组件图标、数据库图标、3D 模型、截图、渐变、阴影、水印、图题、图例或解释性段落。

关系端点约定：组合与聚合的菱形一律画在 owner 端；角色名和多重性一律标在 part 端。若某关系已在属性栏以带类型的属性表达（例如 `+profile: Sunray150VirtualPx4Classic [1]`），则不再为同一语义额外补画关联线，避免重复表达和长距离连线。

语言约定：类名、stereotype、属性名、操作名、类型签名、以及对应源码实例名的角色名（例如 `physical`、`sensors`、`plant`、`vehicles`、`core`）一律保持英文原文，逐字与源码一致，不得翻译或改写。UML note 与描述性依赖标签一律使用中文。信号名构成的依赖标签（例如 `attitude_ref, collective_thrust_delta`、`rotor_command`）保持英文，因其为源码变量名。中文文字须与英文标识符同等清晰地渲染，不得压缩或省略。四张图各自都必须带 note，不允许只有部分图有 note。

## 图 4-4：Sunray150 物理模型领域类图

```text
Figure Subject:
Create a source-aligned standard UML class diagram for the Sunray150 physical-model domain. Use actual project class names where listed. The purpose is to show ownership, specialization, and physical-model responsibilities, not a simulation flow and not a source-code reverse-engineering claim.

Diagram type:
Standard UML class diagram with three-compartment class boxes.

Layout:
Use a 16:9 canvas divided into a wide main area on the left and a narrow independent column on the right.
In the main area, use a three-row vertical ownership structure with "Sunray150Assembly" as the central owner class in the middle row.
- Row 1 (top): leave empty above the central class; do not place any box directly above "Sunray150Assembly".
- Row 2 (middle): place "Sunray150Assembly" at the horizontal center, and place "Sunray150VirtualPx4Classic" as a small record box immediately to its right at the same vertical height.
- Row 3 (bottom): place the three composed classes in one aligned row, left to right: "PhysicalWrenchAdapter", "Sunray150VisualShell", "Sensors".
- Below "PhysicalWrenchAdapter", extend one vertical ownership branch downward: "WrapperSurface" then "RotorActuatorCore".
In the narrow right column, place the inheritance pair "Sunray150GazeboAlignedVisualChassis" above "QuadChassis" as a visually separate branch that connects to nothing else in the figure. This right column may be rendered narrower and shorter than the main area; do not stretch it to fill the canvas height.
All three composition lines from "Sunray150Assembly" run downward as parallel vertical segments to the bottom row without crossing. The single association to "Sunray150VirtualPx4Classic" is one short horizontal segment. Use only short orthogonal relationship segments.

Mandatory class boxes:
- <<model>> "Sunray150Assembly"
  Attributes: +profile: Sunray150VirtualPx4Classic [1]; +initial_position_m: Real[3]; +rotor_command: Real[4]; +position: Real[3]; +attitude: Real[3]
  Operations: +applyRotorCommand(command: Real[4]): void; +measurePosition(): Real[3]; +measureAttitude(): Real[3]
- <<record>> "Sunray150VirtualPx4Classic"
  Attributes: +takeoff_mass_kg: Real; +body_inertia_diagonal_kg_m2: Real[3]; +mworks_visual_thrust_coefficient: Real; +moment_constant_ratio_m: Real; +mworks_yaw_direction: Real[4]
  Operations: leave empty; do not print a dash.
- <<model>> "PhysicalWrenchAdapter"
  Attributes: +lift_coefficient: Real; +reaction_moment_ratio: Real; +fault_rotor_index: Integer; +fault_rotor_effectiveness: Real
  Operations: +computeBodyWrench(): Wrench; +applyBodyWrench(): void; +evaluateMotorFault(index: Integer): Boolean
- <<model>> "WrapperSurface"
  Attributes: -mass_kg: Real; -moment_constant: Real; -yaw_direction: Real[4]; +total_thrust: Real; +total_moment_body: Real[3]
  Operations: +updateRotorDynamics(command: Real[4]): void; +computeTotalThrust(): Real; +computeTotalMoment(): Real[3]
- <<model>> "RotorActuatorCore"
  Attributes: -omega: Real[4]; -thrust: Real[4]; -yaw_reaction_moment: Real[4]; -thrust_effectiveness: Real[4]
  Operations: +updateRotorSpeed(command: Real[4]): void; +computeThrust(): Real[4]; +computeYawReactionMoment(): Real[4]
- <<model>> "Sensors"
  Attributes: +PosMea: Real[3]; +AngleMea: Real[3]; +VelMea: Real[3]; +BodyRateMea: Real[3]; +QuatMea: Real[4]
  Operations: +measurePosition(): Real[3]; +measureAttitude(): Real[3]; +measureBodyRate(): Real[3]
- <<model>> "Sunray150VisualShell"
  Attributes: +rotor_speed: Real[4]; +profile: Sunray150VirtualPx4Classic [1]
  Operations: +updateVisualState(rotor_speed: Real[4]): void
- <<model>> "Sunray150GazeboAlignedVisualChassis"
  Attributes: leave empty; do not print a dash.
  Operations: +updatePropellerGeometry(): void
- <<external base>> "QuadChassis"
  Attributes: #mass: Real; #inertia: Real[3]
  Operations: +applyWrench(force: Real[3], torque: Real[3]): void

Mandatory relationships:
- "Sunray150Assembly" *-- "PhysicalWrenchAdapter" with role "physical" and multiplicity 1 at the part end.
- "Sunray150Assembly" *-- "Sunray150VisualShell" with role "visual_shell" and multiplicity 1 at the part end.
- "Sunray150Assembly" *-- "Sensors" with role "sensors" and multiplicity 1 at the part end.
- "PhysicalWrenchAdapter" *-- "WrapperSurface" with role "wrapper" and multiplicity 1 at the part end.
- "WrapperSurface" *-- "RotorActuatorCore" with role "dynamics" and multiplicity 1 at the part end.
- "Sunray150Assembly" --> "Sunray150VirtualPx4Classic" with role "profile" and multiplicity 1 at the record end, drawn as one short horizontal segment.
- "Sunray150GazeboAlignedVisualChassis" --|> "QuadChassis".

Mandatory UML notes:
- Note attached to "Sunray150Assembly": "本图仅为物理域；不含控制器与分配器"
- Note attached to "Sensors": "输出为测量量；不代表真值"
- Note attached to "Sunray150GazeboAlignedVisualChassis": "外观对齐分支；不参与动力学计算"

Negative constraints:
Do not draw an association line from "Sunray150VisualShell" to "Sunray150VirtualPx4Classic"; that reference is already expressed by the "+profile" attribute in the "Sunray150VisualShell" box. Do not draw "position", "attitude", or "rotor_command" as separate class boxes. Do not add a fake "Controller" relationship to this physical-domain figure. Do not use a feedback loop, timeline, state transition, or generic left-to-right pipeline. The class descriptions must remain consistent with the actual physical assembly: rotor commands enter the plant, the plant applies force and torque, and Sensors expose measured outputs.
```

## 图 4-5：控制器与执行机构类图

```text
Figure Subject:
Create a standard UML class diagram for the controller-to-actuator domain of the MoSim quadrotor model. Distinguish the abstract ATTITUDE_THRUST controller contract, the PX4CTRL equation bridge, the offline attitude/rate allocator, and the reusable whole-aircraft vehicle class.

Diagram type:
Standard UML class diagram with inheritance and composition.

Layout:
Use a 16:9 canvas with a left-spine ownership structure organised as three vertical columns.
- Left column: place "OpenBlocksPx4CtrlVehicle" as a single tall box, vertically centred. This is the owner class.
- Middle column: stack the three owned classes top to bottom as an aligned vertical strip: "Px4CtrlAttitudeThrustAdapter", then "OfflineAttitudeRateAllocator", then "Sunray150Assembly".
- Place the abstract class "PartialAttitudeThrustController" at the top of the middle column, directly above "Px4CtrlAttitudeThrustAdapter".
- Right column: place "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock" at the same vertical height as "Px4CtrlAttitudeThrustAdapter", and place the small record box "Sunray150VirtualPx4Classic" at the same vertical height as "OfflineAttitudeRateAllocator".
Route the three composition lines from the left column to the middle column as three parallel horizontal segments at three different heights, so they never cross each other and never pass through any box. Route the inheritance line as one vertical segment upward inside the middle column. Route the two dependency lines as short vertical segments between vertically adjacent boxes in the middle column. Route the two right-hand relationships as short horizontal segments from the middle column to the right column.

Mandatory class boxes:
- <<abstract model>> "PartialAttitudeThrustController"
  Attributes: +position_ref: Real[3]; +velocity_ref: Real[3]; +acceleration_ref: Real[3]; +position_mea: Real[3]; +velocity_mea: Real[3]; +attitude_mea: Real[3]; +attitude_ref: Real[3]; +collective_thrust_delta: Real
  Operations: +computeAttitudeReference(): Real[3]; +computeCollectiveThrustDelta(): Real
- <<model>> "Px4CtrlAttitudeThrustAdapter"
  Attributes: -profile: Sunray150VirtualPx4Classic [1]; -pitch_argument_domain_margin: Real; +attitude_ref: Real[3]; +collective_thrust_delta: Real
  Operations: +convertStateToQuaternion(): Real[4]; +computeAttitudeReference(): Real[3]; +adaptPX4CTRLOutput(): void
- <<sysblock model>> "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock"
  Attributes: +position: Real[3]; +velocity: Real[3]; +quaternion: Real[4]; +reference_position: Real[3]; +collective_thrust_n: Real
  Operations: +evaluateOuterLoop(): void; +computeDesiredAttitude(): Real[3]; +computeCollectiveThrust(): Real
- <<model>> "OfflineAttitudeRateAllocator"
  Attributes: -profile: Sunray150VirtualPx4Classic [1]; -kp_attitude: Real; -kd_attitude: Real; -kp_yaw: Real; -inner_limit: Real; +rotor_command: Real[4]
  Operations: +computeBodyRateFeedback(): Real[3]; +allocateAttitudeAndThrust(): Real[4]; +applySaturation(): Real[4]
- <<model>> "OpenBlocksPx4CtrlVehicle"
  Attributes: -initial_position: Real[3]; -controller_sample_period_s: Real; +position: Real[3]; +tracking_error_m: Real
  Operations: +trackReference(): void; +computeTrackingError(): Real; +sampleControllerInputs(): void
- <<record>> "Sunray150VirtualPx4Classic"
  Attributes: +mworks_hover_visual_rotor_speed_rad_s: Real; +mworks_visual_thrust_coefficient: Real; +moment_constant_ratio_m: Real
  Operations: leave empty; do not print a dash.
- <<model>> "Sunray150Assembly"
  Attributes: -rotor_command: Real[4]; +position: Real[3]; +attitude: Real[3]
  Operations: +applyRotorCommand(command: Real[4]): void; +measureState(): void

Mandatory relationships:
- "Px4CtrlAttitudeThrustAdapter" --|> "PartialAttitudeThrustController", drawn as one vertical segment.
- "OpenBlocksPx4CtrlVehicle" *-- "Px4CtrlAttitudeThrustAdapter" with role "controller" and multiplicity 1 at the part end.
- "OpenBlocksPx4CtrlVehicle" *-- "OfflineAttitudeRateAllocator" with role "allocator" and multiplicity 1 at the part end.
- "OpenBlocksPx4CtrlVehicle" *-- "Sunray150Assembly" with role "plant" and multiplicity 1 at the part end.
- "Px4CtrlAttitudeThrustAdapter" *-- "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock" with role "core" and multiplicity 1 at the part end, drawn as one short horizontal segment.
- "Px4CtrlAttitudeThrustAdapter" ..> "OfflineAttitudeRateAllocator" with dependency label "attitude_ref, collective_thrust_delta".
- "OfflineAttitudeRateAllocator" ..> "Sunray150Assembly" with dependency label "rotor_command".
- "OfflineAttitudeRateAllocator" --> "Sunray150VirtualPx4Classic" with role "profile" and multiplicity 1 at the record end, drawn as one short horizontal segment.

Mandatory UML notes:
- Note attached to "PartialAttitudeThrustController": "抽象控制契约；不可实例化"
- Note attached to "OfflineAttitudeRateAllocator": "离线姿态/角速率分配；不等同于 PX4 运行时证据"
- Note attached to "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock": "Sysblock 实现；经 connect 方程接入计算链"

Negative constraints:
Do not draw an association line from "Px4CtrlAttitudeThrustAdapter" to "Sunray150VirtualPx4Classic"; that reference is already expressed by the "-profile" attribute in the adapter box. Do not draw the signal handovers between adapter, allocator, and plant as navigable associations with role names; they are realised by connect equations and must appear only as the two labelled dependency arrows listed above. Do not treat the abstract contract as a concrete controller instance. Do not use component icons, sequence messages, state transitions, or generic data-flow arrows. Do not draw "PX4", "MAVROS", or "QGC" as classes in this figure; this figure stops at the project-owned controller and plant boundary. Do not claim the offline allocator is PX4 runtime evidence.
```

## 图 4-6：规划、轨迹与多机组织类图

```text
Figure Subject:
Create a standard UML class diagram for reference generation, OpenBlocks planning, and optional three-UAV organization in the MoSim model. Keep planning classes separate from controller and plant implementation classes, while showing the explicit composition of three references and three reusable vehicle objects.

Diagram type:
Standard UML class diagram with package stereotypes, composition, association, and dependency.

Layout:
Use a 16:9 canvas with a two-column ownership structure.
- Left column: stack two boxes vertically, "PlannedQuinticPx4CtrlReference" on top and "OpenBlocksPx4CtrlVehicle" below it, left-aligned with each other.
- Centre-right: place "OpenBlocksThreeUavPx4CtrlFormation" as the owner class, vertically centred between the two left-column boxes.
- Place "TriangleFigure8Reference" directly above "OpenBlocksThreeUavPx4CtrlFormation" and "OpenBlocksThreeUavPx4CtrlFormationEcbfSafety" directly below it.
- Place "OpenBlocksMapTruthDisplay" as a separate gray class box at the lower-right corner, clearly to the right of the safety class.
Route the two composition lines from the formation class leftward as two parallel horizontal segments at two different heights, one meeting "PlannedQuinticPx4CtrlReference" and one meeting "OpenBlocksPx4CtrlVehicle", so they never cross. Route the association between the two left-column boxes as one short vertical segment inside the left column. Route the reference and safety dependencies as short vertical segments on the formation class centre axis. Route the map-truth dependency from the lower-right corner as a horizontal-then-vertical path entering the right edge of the formation class. No diagonal or crossing connectors.

Mandatory class boxes:
- <<block>> "PlannedQuinticPx4CtrlReference"
  Attributes: +n_segments: Integer; +p_x: Real[:]; +p_y: Real[:]; +p_z: Real[:]; +segment_duration: Real[:]; +position_command: Real[3]; +velocity_command: Real[3]; +acceleration_command: Real[3]
  Operations: +interpolatePosition(time: Real): Real[3]; +interpolateVelocity(time: Real): Real[3]; +interpolateAcceleration(time: Real): Real[3]
- <<model>> "OpenBlocksPx4CtrlVehicle"
  Attributes: -initial_position: Real[3]; -controller_sample_period_s: Real; +position: Real[3]; +tracking_error_m: Real
  Operations: +trackReference(): void; +computeTrackingError(): Real
- <<model>> "OpenBlocksThreeUavPx4CtrlFormation"
  Attributes: -vehicle_count: Integer = 3; +formation_error: Real; +minimum_separation: Real
  Operations: +updateThreeReferences(): void; +evaluateFormationSeparation(): Real; +publishPredictedTrajectories(): void
- <<model>> "TriangleFigure8Reference"
  Attributes: +uav_count: Integer = 3; +reference_scale: Real; +position_command: Real[3]
  Operations: +generateFormationReference(time: Real): Real[3]; +updateRelativeOffsets(): void
- <<model>> "OpenBlocksThreeUavPx4CtrlFormationEcbfSafety"
  Attributes: +safety_margin: Real; +pair_count: Integer = 3
  Operations: +evaluatePairwiseSafety(): Boolean; +applySafetyReference(): void
- <<model>> "OpenBlocksMapTruthDisplay"
  Attributes: +n_segments: Integer; +actual_position: Real[3]; +reference_position: Real[3]
  Operations: +updateTruthOverlay(): void; +showReferenceAndActual(): void

Mandatory relationships:
- "OpenBlocksPx4CtrlVehicle" --> "PlannedQuinticPx4CtrlReference" with role "reference input" and multiplicity 1 at the reference end, drawn as one short vertical segment.
- "OpenBlocksThreeUavPx4CtrlFormation" *-- "PlannedQuinticPx4CtrlReference" with role "references" and multiplicity 3 at the part end.
- "OpenBlocksThreeUavPx4CtrlFormation" *-- "OpenBlocksPx4CtrlVehicle" with role "vehicles" and multiplicity 3 at the part end.
- "TriangleFigure8Reference" --> "OpenBlocksThreeUavPx4CtrlFormation" with role "formation reference" and multiplicity 1 at the formation end.
- "OpenBlocksThreeUavPx4CtrlFormationEcbfSafety" ..> "OpenBlocksThreeUavPx4CtrlFormation" with dependency label "附加两两安全参考层".
- "OpenBlocksMapTruthDisplay" ..> "OpenBlocksThreeUavPx4CtrlFormation" with dependency label "只读实际/参考叠加显示".

Mandatory UML notes:
- Note attached to "OpenBlocksThreeUavPx4CtrlFormationEcbfSafety": "附加安全层；非继承变体"
- Note attached to "OpenBlocksMapTruthDisplay": "只读显示；不作为控制器输入"
- Note attached to "OpenBlocksThreeUavPx4CtrlFormation": "三机组织为可选编排；不含固定编队控制律"

Negative constraints:
Do not place "OpenBlocksPx4CtrlVehicle" between "PlannedQuinticPx4CtrlReference" and "OpenBlocksThreeUavPx4CtrlFormation" on a single horizontal axis; the two composition lines must reach the left column without passing through any box. Do not draw a sequence diagram, timing arrows, frontier pipeline, or state machine. Do not use inheritance between the safety variant and the base formation unless the rendered relation is explicitly a verified generalization; use the listed dependency instead. Do not portray "OpenBlocksMapTruthDisplay" as a planner, controller, or truth input to the controller. Do not imply autonomous exploration or fixed-formation control beyond the listed class responsibilities.
```

## 图 4-7：实验入口与证据记录类图

```text
Figure Subject:
Create a standard UML class diagram for experiment entry points, formal runners, real-time probes, the read-only telemetry observer, and their documentation evidence records in the MoSim project. Separate formal simulation classes from real-time and display-only classes using stereotypes and note objects. The diagram must show evidence boundaries, not claim that any run passed.

Diagram type:
Standard UML class diagram with abstract classes, realizations, dependencies, and logical record classes.

Layout:
Use a wide 2:1 canvas so that ten three-compartment class boxes and three notes remain legible at full size; do not shrink attribute or operation text to fit a narrower canvas.
Organise the canvas as an upper band with three columns and a lower band with one row.
- Upper-left column: place the formal-runner inheritance chain as one vertical stack, "FormalAttitudeThrustRunnerBase" on top, "Px4CtrlFormalRunner" in the middle, "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop" at the bottom.
- Upper-middle column: place "CompleteSystemGraphical" beside that chain, aligned with "Px4CtrlFormalRunner".
- Upper-right column: place "RT0RealtimeProbe", "RT1OfficialPidShadow50Hz", and "RTTelemetryScope50Hz" as three boxes aligned in one vertical stack in that order.
- Lower band: place the three logical record classes in one aligned row with this fixed left-to-right order: "EvidenceArtifact", "RunRecord", "MetricSeries".
Keep the inheritance chain strictly vertical. Route every dependency that targets "RunRecord" downward into the top edge of the "RunRecord" box. Route the telemetry dependency that targets "MetricSeries" down the right edge of the canvas into the top edge of "MetricSeries", so it never enters the bundle of lines arriving at "RunRecord". Route the two composition lines from "RunRecord" as one short horizontal segment to the left toward "EvidenceArtifact" and one short horizontal segment to the right toward "MetricSeries". Use orthogonal connectors only, with no crossings.

Mandatory class boxes:
- <<abstract model>> "FormalAttitudeThrustRunnerBase"
  Attributes: +start_time: Real; +stop_time: Real; +interval: Real; +tolerance: Real
  Operations: +checkModel(): Boolean; +simulate(): ResultSeries; +collectResultSeries(): ResultSeries
- <<formal runner>> "Px4CtrlFormalRunner"
  Attributes: +controller_id: String; +output_variant: String; +parameter_hash: String
  Operations: +prepareRun(): void; +runFormalSimulation(): ResultSeries; +writeRunRecord(): RunRecord
- <<formal scenario>> "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop"
  Attributes: +initial_position_m: Real[3]; +stop_time: Real
  Operations: +configureReference(): void; +configurePlant(): void; +runScenario(): RunRecord
- <<graphical entry>> "CompleteSystemGraphical"
  Attributes: +stop_time: Real; +sample_interval: Real
  Operations: +openModelReview(): void; +runGraphicalScenario(): RunRecord
- <<realtime probe>> "RT0RealtimeProbe"
  Attributes: +samplePeriod: Real; +processedFrames: Integer; +sentFrames: Integer; +outputValid: Integer
  Operations: +exchangeFrame(simulationTime: Real): ProbeFrame; +countProcessedFrames(): Integer
- <<shadow controller>> "RT1OfficialPidShadow50Hz"
  Attributes: +samplePeriod: Real; +kp: Real[3]; +kv: Real[3]; +frameValid: Integer; +outputValid: Integer
  Operations: +receiveFrame(): StateFrame; +computeShadowCommand(): CommandFrame; +sendCommand(frame: CommandFrame): Integer
- <<read-only observer>> "RTTelemetryScope50Hz"
  Attributes: +samplePeriod: Real; +sequence: Integer; +frameValid: Integer; +positionErrorNorm: Real; +roundTripMs: Real
  Operations: +receiveTelemetry(): TelemetryFrame; +computeReadOnlyMetrics(): MetricSeries
- <<logical record>> "RunRecord"
  Attributes: +controller_id: String; +model_id: String; +status: String; +source_commit: String
  Operations: +attachArtifact(artifact: EvidenceArtifact): void; +isComplete(): Boolean
- <<logical record>> "MetricSeries"
  Attributes: +time: Real[:]; +position_error: Real[:]; +attitude_error: Real[:]; +sample_count: Integer
  Operations: +validateNonEmpty(): Boolean; +computeSummary(): void
- <<logical record>> "EvidenceArtifact"
  Attributes: +artifact_type: String; +path: String; +sha256: String; +evidence_class: String
  Operations: +verifyIntegrity(): Boolean; +classifyEvidence(): String

Mandatory relationships:
- "Px4CtrlFormalRunner" --|> "FormalAttitudeThrustRunnerBase".
- "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop" --|> "Px4CtrlFormalRunner".
- "CompleteSystemGraphical" ..> "RunRecord" with dependency label "图形化评审元数据".
- "Px4CtrlFormalRunner" ..> "RunRecord" with dependency label "正式运行元数据".
- "RT0RealtimeProbe" ..> "RunRecord" with dependency label "RT0 探针记录".
- "RT1OfficialPidShadow50Hz" ..> "RunRecord" with dependency label "RT1 影子记录".
- "RTTelemetryScope50Hz" ..> "MetricSeries" with dependency label "只读遥测指标".
- "RunRecord" *-- "EvidenceArtifact" with role "artifacts" and multiplicity 1..* at the part end.
- "RunRecord" *-- "MetricSeries" with role "metrics" and multiplicity 0..* at the part end.

Mandatory UML notes:
- Note attached to "RT1OfficialPidShadow50Hz": "shadow-only；不自动取得 MAVROS 控制权"
- Note attached to "RTTelemetryScope50Hz": "只读观察者；不发布控制命令"
- Note attached to "RunRecord": "逻辑证据记录类，不等同于运行通过"

Negative constraints:
Do not place "MetricSeries" between "EvidenceArtifact" and "RunRecord" in the bottom row; the fixed order must be EvidenceArtifact, RunRecord, MetricSeries from left to right. Treat "ProbeFrame", "StateFrame", "CommandFrame", "TelemetryFrame", and "ResultSeries" only as types appearing in attribute or operation signatures; do not draw them as additional class boxes. Do not connect RT0, RT1, and RTTelemetryScope50Hz as concurrent publishers. Do not make the telemetry observer a subclass of the controller. Do not use arrows to imply execution order. Do not turn evidence records into performance claims. No component icons, lifelines, state circles, flowchart diamonds, crossed lines, curved lines, screenshots, decorative icons, captions, or a legend.
```
