# MoSim Report Figure Prompt Pack

Use one prompt block at a time. Every block is self-contained and can be sent directly to an image-generation agent.

Drawing discipline:

- Treat every block as a layout specification first, not just a label list.
- If a block has layers, keep each layer as one straight band or row with aligned nodes.
- If a block has parallel lanes, separate them clearly and never let connectors cross lanes unless the block explicitly asks for a shared junction.
- If a block has a feedback loop, draw the return path as a distinct lower or outer loop, not as a diagonal shortcut through the main chain.
- Keep comparison figures strictly parallel, taxonomy figures strictly branched, and pipeline figures strictly left-to-right unless the block states another direction.
- Put every annotation, warning, and scope note inside a bordered label or a compact callout next to the relevant arrow.
- Prefer orthogonal connectors everywhere; only use diagonal segments when the block explicitly allows them.
- When a block names a root, keep that root visually dominant and do not duplicate it.
- When a block names a shared Plant, keep it as one shared sink node, not multiple copies.
- When a block includes evidence, place evidence to the right or bottom edge and keep it read-only.
- When a block includes comparison outputs, align the comparison outputs in a final row or final column, never inside the main loop.
- When a block includes interface boundaries, keep the boundary labels separate from the implementation nodes.
- Every retained figure is a main-body report figure. Do not render "附录", "Appendix", "supplementary", or a separate supplementary-material path.
- Keep architecture explanation, formal MWORKS evidence, independent runtime evidence, and read-only display in visibly separate lanes. A dashed gray factual-reference arrow is never a control, deployment, or performance-equivalence arrow.
- For multi-output hardware diagrams, make each output a dedicated horizontal or vertical lane from its source port to its matching destination port. Do not merge four motor wires into a fan-out/fan-in tangle.
- Keep a node's incoming and outgoing ports on consistent sides: left-to-right signal flow enters on the left and exits on the right; only declared lower feedback rails may return right-to-left.
- A block may declare more than one feedback rail. Every right-to-left wire must belong to a rail that the block lists explicitly, and each rail occupies its own reserved horizontal track so rails never share a line.
- Dotted reference guides that pair an indexed item with its index-ordered counterpart are exempt from the orthogonal-only routing rule. They may be drawn as thin straight or gently curved leaders and may cross one another; solid signal wires may not.

Rules:

- Generate exactly one figure from each prompt block.
- All instructional text is English.
- Text rendered inside the figure must use the exact labels listed under `Mandatory nodes` and `Mandatory connections`.
- Ordinary labels inside the figure are Simplified Chinese; established technical terms, product names, protocol names, and algorithm abbreviations remain in English.
- Do not add a figure title, figure number, caption, watermark, legend paragraph, or explanatory prose inside the generated image unless explicitly required.
- Export both PNG and editable SVG when possible.

---

## Active Redraw Set

Use the six replacement blocks below for the current redraw pass. They replace
the earlier versions of the corresponding hand-drawn figures; the other
hand-drawn figures are not regenerated in this pass.

| Report figure | Prompt block | Required change |
|---|---|---|
| `12_Profile配置与状态注入链路.png` | 03 | Split the MWORKS formal Plant from the independent ROS1/PX4 lane and preserve command/event authority. |
| `16_MWORKS建模仿真代码生成反馈闭环.png` | 02 | Replace the single deployment loop with separate formal-evidence, code-delivery, and runtime-evidence lanes. |
| `19_四旋翼动力学与控制分配模型.png` | 05 | Use the source-aligned signed X allocation, actuator lag, rotor order, and principal inertia. |
| `20_实验平台分层与故障反馈链路.png` | 01 | Show the actual motor/ESC/airframe graphical review and distinguish it from FormalRunner evidence. |
| `21.png` | 21 | Replace the obsolete 46-route/cost taxonomy with a 48-entry catalogue and evidence map. |
| `22.png` | 22 | Replace the speculative diagnostic tree with the frozen four-class G3 failure classification. |

---

## 01 Figure 20: Sunray150 System Architecture, Formal Evidence, and Display Boundary

```text
Figure Subject:
Create a source-aligned 2D engineering architecture diagram for the Sunray150 graphical system review and the separate MWORKS whole-aircraft formal-evidence path. The upper lane must make the battery, controller, ESC, four motors, and airframe easy to inspect. The lower lane must show the actual FormalRunner evidence path. Use a pure white background, flat vector graphics, black text, solid black 1 px borders, and sharp arrowheads. Use pale blue for model/state nodes, pale green for control and actuator nodes, pale yellow for evidence nodes, and pale gray for read-only display or independent-runtime nodes.

Diagram type:
Two-lane source-and-evidence architecture diagram with a shared report-output column.

Layout:
Use a 16:9 horizontal canvas with two full-width horizontal lanes and one narrow shared evidence column at the far right. Label the upper lane "图形化系统审查（结构说明）" and the lower lane "MWORKS正式仿真证据（性能结论）". Keep the lanes separated by a solid horizontal divider; do not draw a control wire across it.

In the upper lane, place computation and sensing at the left, the controller and ESC at the center, and propulsion/airframe at the right. Put "BatteryPowerModule" directly above "ESCDriveModule" with one vertical power arrow. Put the four motor nodes in four equal-height rows immediately right of the ESC. Put the four matching airframe rotor ports in the same four rows immediately right of the motors. Each ESC-to-motor-to-airframe route must be a straight horizontal lane: Motor 1 only reaches Rotor 1, and so on. Reserve two stacked right-to-left return tracks below the propulsion rows inside the upper lane. The upper track carries the four motor-speed reports back to the flight controller; the lower outer track carries airframe -> sensor-feedback hub -> perception and flight-controller inputs. Keep the two tracks on separate horizontal lines and never merge them into one rail. Do not draw diagonal motor, power, or feedback wires.

In the lower lane, place the formal path in one left-to-right row. Put the Plant-state feedback in a separate lower return rail inside this lane. Place the shared evidence column outside both loops. Use only orthogonal connectors, strict grid alignment, equal motor spacing, and no nested decorative containers.

Mandatory nodes:
- Lane label: "图形化系统审查（结构说明）"
- "PerceptionInterfaceModule"
- "V6XFlightControllerModule"
- "ORINNXMissionComputerModule"
- "SystemSupervisorModule"
- "系统状态记录"
- "AWFFControllerModule"
- "BatteryPowerModule"
- "ESCDriveModule"
- "MotorDriveModule 1"
- "MotorDriveModule 2"
- "MotorDriveModule 3"
- "MotorDriveModule 4"
- "Sunray150AirframeSensorModule"
- "传感器反馈汇聚"
- "电机转速回报汇聚"
- "系统图形审查截图"
- Lane label: "MWORKS正式仿真证据（性能结论）"
- "Profile配置"
- "FormalRunner + Adapter + Controller"
- "ActuatorCommandMapper"
- "RotorActuatorCore"
- "PhysicalWrenchAdapter"
- "MultiBody Plant"
- "Result.msr / 原始CSV / 指标"
- "原生结果窗口"
- "独立ROS1运行时记录"
- "正文图、表与代码片段（无附录）"
- Annotation: "结构审查不等于控制器性能结论"
- Annotation: "运行时记录仅作事实性引用"

Mandatory connections:
- "PerceptionInterfaceModule" -> "V6XFlightControllerModule".
- "PerceptionInterfaceModule" -> "ORINNXMissionComputerModule".
- "V6XFlightControllerModule" -> "ORINNXMissionComputerModule".
- "ORINNXMissionComputerModule" -> "AWFFControllerModule".
- "V6XFlightControllerModule" -> "AWFFControllerModule".
- "AWFFControllerModule" -> "ESCDriveModule".
- "BatteryPowerModule" -> "ESCDriveModule" as one vertical arrow.
- "BatteryPowerModule" -> "SystemSupervisorModule" -> "系统状态记录" as a thin side-status route, not a controller command route.
- "ESCDriveModule" -> "MotorDriveModule 1" -> "Sunray150AirframeSensorModule" rotor port 1.
- "ESCDriveModule" -> "MotorDriveModule 2" -> "Sunray150AirframeSensorModule" rotor port 2.
- "ESCDriveModule" -> "MotorDriveModule 3" -> "Sunray150AirframeSensorModule" rotor port 3.
- "ESCDriveModule" -> "MotorDriveModule 4" -> "Sunray150AirframeSensorModule" rotor port 4.
- "Sunray150AirframeSensorModule" -> "传感器反馈汇聚" -> "PerceptionInterfaceModule" and "V6XFlightControllerModule" by the outer sensor-feedback rail, which is the lower of the two reserved return tracks in the upper lane.
- "MotorDriveModule 1", "MotorDriveModule 2", "MotorDriveModule 3", and "MotorDriveModule 4" each send one motor-speed report to "电机转速回报汇聚" -> "V6XFlightControllerModule" port "motor_speed_raw[1..4]", carried on the upper of the two reserved return tracks in the upper lane. Draw these four reports as short vertical drops from each motor row into the shared track so they never cross the ESC-to-motor-to-airframe lanes.
- "Sunray150AirframeSensorModule" -> "系统图形审查截图".
- "系统状态记录" -> "系统图形审查截图".
- "Profile配置" -> "FormalRunner + Adapter + Controller" -> "ActuatorCommandMapper" -> "RotorActuatorCore" -> "PhysicalWrenchAdapter" -> "MultiBody Plant" -> "Result.msr / 原始CSV / 指标".
- "MultiBody Plant" -> "FormalRunner + Adapter + Controller" by the lower formal-lane feedback rail.
- "Result.msr / 原始CSV / 指标" -> "原生结果窗口" and "正文图、表与代码片段（无附录）".
- "系统图形审查截图" -> "正文图、表与代码片段（无附录）".
- "独立ROS1运行时记录" -> "正文图、表与代码片段（无附录）" using a thin dashed gray factual-reference arrow only.
- Bind "结构审查不等于控制器性能结论" to the divider between the two main lanes.
- Bind "运行时记录仅作事实性引用" to "独立ROS1运行时记录".

Negative constraints:
Do not draw a direct control arrow from the graphical-review lane, the runtime-record node, or any display node into the FormalRunner. Do not merge the four motor wires, duplicate the Plant, imply generated-code deployment success, or treat the system-graphical review as whole-aircraft performance evidence. No 3D, perspective, gradients, shadows, screenshots, photos, curved lines, diagonal lines, crossed connectors, fan-out tangles, large empty regions, appendix labels, or unlabeled authority changes.
```

---

## 02 Figure 16: MWORKS Modeling, Simulation, Code Delivery, and Evidence Lanes

```text
Figure Subject:
Create a strict 2D evidence workflow for the report body. Separate the MWORKS formal simulation path, the source-bound code-delivery verification branch, and the independent ROS1 runtime-record path. The diagram must show that the three paths may contribute factual material to the same report, but one path does not prove completion or equivalence of another. Use a pure white background, flat vector graphics, black text, solid black borders, and a restrained pale engineering color palette.

Diagram type:
Three-lane evidence workflow with one contained review-return path.

Layout:
Use a 16:9 horizontal canvas with three horizontal lanes and a shared report-output column at the far right. The upper lane is the only formal control-evidence path and runs strictly left-to-right. The middle lane is a short code-delivery verification branch that takes off from "CheckModel" in the upper lane and is placed directly below "CheckModel"; it is not a deployment route. The lower lane contains independent completed ROS1 runtime records and must not enter either the formal or code lane.

Keep every lane on a strict grid. Put the only feedback path above the upper lane: it must return from evidence review to the MWORKS model through one blue outer rail labelled as a separately authorized review action, drawn on a reserved track between the upper lane label and the top canvas edge. Route it as a rectangular outer arc: up out of the review node, right-to-left across the reserved top track, then down into the model node. It must not pass through, above, or beside the code-delivery lane, and it must not enter the ROS1 lane. Use black arrows for normal artifact flow, a blue arrow for that single review return, red short arrows only from a failed check to the retained failure record, and thin dashed gray arrows only for factual citation into the report. Do not use diagonal arrows or shared junctions between the three lanes.

Mandatory nodes:
- Lane label: "MWORKS形式化证据主线"
- "任务与场景定义"
- "冻结Profile与参数"
- "MWORKS控制器模型与Adapter"
- "CheckModel"
- "FormalRunner ClimbPath 50 s"
- "Result.msr / 原始CSV"
- "指标、截图与失败记录"
- Lane label: "源绑定代码交付核验"
- "GenerateModelCode"
- "生成C/C++源码"
- "CFunction SIL夹具"
- "构建与静态检查"
- "源绑定交付工件"
- Lane label: "独立ROS1运行时证据线"
- "ROS1 / Gazebo / PX4 / MAVROS / px4ctrl / RViz"
- "已完成运行时记录"
- "事实性正文引用"
- "源与接口复核（需另行授权）"
- "正文图、表与代码片段（无附录）"
- Annotation: "三条证据线不互相等价"
- Annotation: "失败记录保留，不改写为通过"

Mandatory connections:
- "任务与场景定义" -> "冻结Profile与参数" -> "MWORKS控制器模型与Adapter" -> "CheckModel" -> "FormalRunner ClimbPath 50 s" -> "Result.msr / 原始CSV" -> "指标、截图与失败记录" -> "正文图、表与代码片段（无附录）".
- "CheckModel" -> "GenerateModelCode" -> "生成C/C++源码" -> "CFunction SIL夹具" -> "构建与静态检查" -> "源绑定交付工件" -> "正文图、表与代码片段（无附录）".
- "ROS1 / Gazebo / PX4 / MAVROS / px4ctrl / RViz" -> "已完成运行时记录" -> "事实性正文引用" -> "正文图、表与代码片段（无附录）" using thin dashed gray arrows only.
- "指标、截图与失败记录" -> "源与接口复核（需另行授权）" -> "MWORKS控制器模型与Adapter" by the single blue outer feedback rail on the reserved top track above the upper lane.
- "CheckModel" -> "GenerateModelCode" must leave "CheckModel" from its bottom port as one vertical drop into the code-delivery lane; the code lane's first node sits directly beneath "CheckModel".
- Add a short red arrow from a small failed-check marker beside "CheckModel" and from a small failed-run marker beside "FormalRunner ClimbPath 50 s" into "指标、截图与失败记录"; do not create a second failure branch.
- Bind "三条证据线不互相等价" to the vertical separation between the lanes.
- Bind "失败记录保留，不改写为通过" to "指标、截图与失败记录".

Negative constraints:
Do not draw any arrow from generated C/C++ code into the ROS1 runtime lane. Do not draw an arrow from the runtime lane back into MWORKS, code generation, controller tuning, or the formal Plant. Do not claim that code generation, SIL, ROS1, Gazebo, or a display record proves the other lane. No 3D, perspective, gradients, shadows, screenshots, decorative scenery, curved arrows, crossed lines, floating labels, unboxed text, appendix labels, or deployment-success claims.
```

---

## 03 Figure 12: Profile Configuration, State Sources, Event Injection, and Evidence Boundary

```text
Figure Subject:
Create a formal 2D data-flow diagram defining Profile configuration, reference/state/command authority, fault event application, and metrics collection for the MWORKS FormalRunner path. Keep the independent ROS1/PX4 runtime record visibly outside the high-frequency loop. Use a pure white background, flat vector graphics, black text, solid black node borders, pale blue data nodes, pale green control nodes, pale red event nodes, pale yellow metrics nodes, and pale gray read-only or independent-runtime nodes.

Diagram type:
Directed data-flow and authority-boundary diagram.

Layout:
Use a 16:9 horizontal canvas with three aligned horizontal bands plus a narrow gray independent-runtime box at the far right. The top band contains Profile-driven reference and parameter authority. The middle band is the only high-frequency MWORKS FormalRunner loop. The bottom band contains event injection, diagnostics, metrics, and read-only evidence. Keep all high-frequency signal flow strictly left-to-right; draw the Plant-to-state return on one lower outer rail of the middle band.

Place the fault route below the command route in red. It must show that the fault is a Profile-declared parameter frozen at translation time and then applied deterministically inside the rotor actuator, not a runtime request that waits for an acknowledgement. Do not merge the formal Plant with the runtime stack in a single node. Keep "MWORKS Formal Plant" and "独立ROS1/PX4运行时记录" as separate nodes with no command wire between them. Use only orthogonal connectors, aligned ports, and no crossings.

Mandatory nodes:
- "Profile配置"
- "任务与场景配置"
- "任务参考源"
- "ReferenceFrame"
- "参考权威"
- "状态源"
- "StateFrame"
- "状态权威"
- "FormalRunner"
- "控制器"
- "CommandFrame"
- "命令权威"
- "Adapter"
- "MWORKS Formal Plant"
- "传感器反馈"
- "故障注入参数"
- "fault_start_s / fault_rotor_index / fault_rotor_effectiveness"
- "翻译期参数冻结"
- "RotorActuatorCore"
- "fault_effectiveness[i]"
- "DiagnosticsFrame"
- "MetricsFrame"
- "证据存储"
- "只读显示"
- "独立ROS1/PX4运行时记录"
- Annotation: "故障注入为翻译期参数，按时间确定性生效"
- Annotation: "单一发布权威"
- Annotation: "运行时记录不进入MWORKS高频环"

Mandatory connections:
- "Profile配置" -> "任务与场景配置" -> "任务参考源" -> "ReferenceFrame" -> "参考权威" -> "FormalRunner" -> "控制器".
- "MWORKS Formal Plant" -> "传感器反馈" -> "状态源" -> "StateFrame" -> "状态权威" -> "FormalRunner" by the lower outer return rail of the middle band.
- "控制器" -> "CommandFrame" -> "命令权威" -> "Adapter" -> "MWORKS Formal Plant".
- "Profile配置" -> "故障注入参数" -> "fault_start_s / fault_rotor_index / fault_rotor_effectiveness" -> "翻译期参数冻结" -> "RotorActuatorCore".
- "RotorActuatorCore" -> "fault_effectiveness[i]" -> "MWORKS Formal Plant".
- "fault_effectiveness[i]" -> "MetricsFrame"
- "控制器" -> "DiagnosticsFrame" -> "MetricsFrame"
- "StateFrame" -> "MetricsFrame"
- "ReferenceFrame" -> "MetricsFrame"
- "CommandFrame" -> "MetricsFrame"
- "MetricsFrame" -> "证据存储" -> "只读显示"
- "独立ROS1/PX4运行时记录" -> "证据存储" using one thin dashed gray factual-reference arrow only.
- Bind the red annotation label "故障注入为翻译期参数，按时间确定性生效" to the route from "故障注入参数" through "翻译期参数冻结" to "RotorActuatorCore".
- Bind the green annotation label "单一发布权威" to the route from "CommandFrame" through "命令权威" to "Adapter".
- Bind "运行时记录不进入MWORKS高频环" to "独立ROS1/PX4运行时记录".

Negative constraints:
Do not connect the read-only display node or the independent-runtime node to the controller, command-authority node, Adapter, FormalRunner, or MWORKS Formal Plant. Do not show a file queue inside the high-frequency loop. Do not draw an injection request node, an acknowledgement node, a request-versus-applied pair, or any command-plane handshake on the MWORKS fault route; that handshake exists only in the ROS1 sidecar path and is out of scope for this figure. Do not invent Frame names: use only ReferenceFrame, StateFrame, CommandFrame, DiagnosticsFrame, and MetricsFrame. No 3D, shadows, gradients, screenshots, decorative icons, curved lines, connector crossings, floating text, appendix labels, or unlabeled authority changes.
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
Keep the left and right columns as mirrored frame families and place the conversion logic only in the center column.

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

## 05 Figure 19: Source-Aligned Quadrotor Actuation, Dynamics, and X Allocation

```text
Figure Subject:
Create a precise source-aligned 2D engineering mechanics diagram for the MoSim Sunray150 virtual plant. Show the actual FLU rotor order, signed motor commands, a compact graphical-review-only ESC drive context, first-order motor/propeller actuator lag, per-rotor thrust/effectiveness, rotor-center moment, principal-inertia rigid-body dynamics, and the current signed X allocation. Use a white background, black technical linework, flat vector graphics, solid black node borders, green physical force arrows, blue state/signal arrows, pale red only for the fault/effectiveness multiplier, and a thin gray dashed boundary for the graphical-review-only ESC context.

Diagram type:
Three-panel actuation, force/moment, and signed-allocation diagram.

Layout:
Use a 16:9 horizontal canvas with three equal-height panels separated by thin vertical dividers. The left panel is a top-view FLU rotor map. The middle panel is an actuator-to-force-and-moment chain. The right panel is a compact signed X-allocation and rigid-body-equation panel. Do not use one large enclosing card.

In the left panel, orient the nose and +x_B upward and +y_B leftward. Place Rotor 1 at front-right (+x,-y), Rotor 2 at front-left (+x,+y), Rotor 3 at rear-left (-x,+y), and Rotor 4 at rear-right (-x,-y). Print the signed visual command and yaw-direction symbols beside the disks as +, -, +, -. Do not substitute an arbitrary symmetric B matrix or arbitrary CW/CCW convention.

In the middle panel, reserve a narrow gray-dashed context strip along the top edge for the graphical system review only: ESCDriveModule applies bus-voltage scaling, a power_ok gate, and an absolute motor-command clamp before the four motors. Keep this strip visibly outside the FormalRunner dynamics chain. Below it, use four vertically aligned mini-lanes with identical left-to-right geometry: command -> lagged motor/propeller speed -> nominal propeller thrust -> effectiveness -> force/moment contribution. Each row must preserve its rotor index. Route the four force/moment contributions into one aligned sum bus at the right edge of the middle panel; do not use diagonal wires. Put translational and rotational formulas below that bus. Use a lower thin feedback annotation only if needed; it must not cross actuator lanes.

Mandatory nodes:
- Left-panel label: "机体系 FLU（x前、y左、z上）"
- "Rotor 1 (+x,-y)"
- "Rotor 2 (+x,+y)"
- "Rotor 3 (-x,+y)"
- "Rotor 4 (-x,-y)"
- "旋向/偏航符号：+，-，+，-"
- "ESCDriveModule（系统图形审查）"
- "母线缩放 + power_ok 栅控 + |motor_command|≤80"
- Annotation: "图形审查上下文；FormalRunner 以 ActuatorCommandMapper + RotorActuatorCore 为准"
- "命令角速度 ω_cmd,i"
- "一阶电机滞后"
- Formula node: "dω_i/dt = (ω_cmd,i - ω_i) / τ_lag"
- Formula node: "τ_lag = τ_up if |ω_cmd,i| > |ω_i| else τ_down"
- "τ_up = 0.0125 s，τ_down = 0.025 s（四旋翼共用）"
- "实际角速度 ω_i"
- "电机/桨叶旋翼"
- Formula node: "T0,i = C_T ω_i²"
- Formula node: "T_i = η_f,i η_T,i T0,i"
- "旋翼位置 r_i"
- Formula node: "τ_i = [r_y,i T_i, -r_x,i T_i, η_f,i d_i η_M,i C_M η_T,i T0,i]^T"
- Formula node: "T = Σ T_i，τ = Σ τ_i"
- "质心"
- "重力 mg"
- Formula node: "m v_dot = R(q) T e3 - m g e3"
- Annotation: "虚拟Plant未施加气动阻力，F_d = 0"
- Formula node: "J = diag(Jx, Jy, Jz)"
- Formula node: "J ω_dot = τ - ω × Jω"
- Right-panel label: "当前带符号X型分配"
- Formula node: "ω_1,raw = ω_h + Δω_c - y - p + r"
- Formula node: "ω_2,raw = -ω_h - Δω_c - y + p + r"
- Formula node: "ω_3,raw = ω_h + Δω_c - y + p - r"
- Formula node: "ω_4,raw = -ω_h - Δω_c - y - p - r"
- Formula node: "Rotor 1,3: [0, ω_max]；Rotor 2,4: [-ω_max, 0]"
- Annotation: "虚拟Plant工程参数，不是实机辨识真值"

Mandatory connections:
- Each rotor map entry must connect by one indexed dotted guide to its matching actuator mini-lane only: Rotor 1 -> lane 1, Rotor 2 -> lane 2, Rotor 3 -> lane 3, Rotor 4 -> lane 4. The rotor map is a 2D quadrant layout and the mini-lanes are an index-ordered vertical column, so these four dotted guides will cross; that crossing is permitted and expected. Draw them as thin dotted leaders and do not reorder either panel to avoid it.
- In the gray-dashed context strip, draw "motor_command_raw[1..4]" -> "ESCDriveModule（系统图形审查）" -> "motor_command[1..4]". Print the compact source-aligned note "voltage_scale = clamp(bus_voltage / 16.8, 0, 1); power_ok=0 -> command=0; |command|≤80" inside that strip. Connect its output to the four command entries only by thin dashed gray factual-reference guides, never as a FormalRunner dynamics wire. Bind "图形审查上下文；FormalRunner 以 ActuatorCommandMapper + RotorActuatorCore 为准" to the dashed boundary.
- Place "dω_i/dt = (ω_cmd,i - ω_i) / τ_lag", "τ_lag = τ_up if |ω_cmd,i| > |ω_i| else τ_down", and "τ_up = 0.0125 s，τ_down = 0.025 s（四旋翼共用）" as one grouped caption beside the "一阶电机滞后" stage, printed once for the whole panel rather than repeated in each of the four lanes.
- In every mini-lane, "命令角速度 ω_cmd,i" -> "一阶电机滞后" -> "实际角速度 ω_i" -> "电机/桨叶旋翼" -> "T0,i = C_T ω_i²" -> "T_i = η_f,i η_T,i T0,i" -> "τ_i = [r_y,i T_i, -r_x,i T_i, η_f,i d_i η_M,i C_M η_T,i T0,i]^T".
- The four per-rotor thrust contributions enter "T = Σ T_i，τ = Σ τ_i" through four equal horizontal ports, one per row.
- "T = Σ T_i，τ = Σ τ_i" and "重力 mg" -> "m v_dot = R(q) T e3 - m g e3".
- Bind "虚拟Plant未施加气动阻力，F_d = 0" beside the translational equation as a plain text note, not as a node with an incoming arrow.
- "T = Σ T_i，τ = Σ τ_i" and "J = diag(Jx, Jy, Jz)" -> "J ω_dot = τ - ω × Jω".
- Place "旋翼位置 r_i" directly beside the per-rotor moment formula, not on a crossing connector.
- Place all four signed-allocation formulas in one right-panel vertical stack, ordered 1 through 4; place the saturation formula directly beneath them.
- Bind "虚拟Plant工程参数，不是实机辨识真值" to the lower-right corner outside the equations.

Negative constraints:
Do not use a generic full inertia tensor, a generic B allocation matrix, an arbitrary rotor order, unsigned motor commands, or an unlabelled clockwise/counter-clockwise convention. Do not reverse the thrust direction or map a motor lane to the wrong rotor port. Do not draw an aerodynamic drag force arrow, a drag node, or a drag term in the translational equation. Do not print a per-rotor lag constant subscript such as τ_1 through τ_4, and do not reuse the symbol τ_i for both the lag constant and the moment vector. No photorealistic drone, 3D perspective, unexplained aerodynamic effects, gradients, shadows, curved solid data connectors, decorative background, floating formula text, crossed solid motor lines, or appendix labels.
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
Keep the main chain centered horizontally and keep all selectable algorithm stacks narrow enough that they read as options, not as separate controllers.

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
Use a 16:9 horizontal canvas with four strictly separated horizontal lanes. Order the lanes from top to bottom as ATTITUDE_THRUST, BODY_RATE_THRUST, WRENCH, and ROTOR_COMMAND. Each lane flows left to right from controller output to a boundary-specific Runner, Adapter, inner-loop or allocator ownership, and Plant. Align corresponding stages vertically across all lanes so the Runner and Adapter columns line up. Use orthogonal connectors only. Use a red prohibition mark between lanes to indicate that implicit cross-boundary wiring is forbidden.
Keep the four lanes equal in width and do not let any lane borrow the visual space of another lane.

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
Make the shared Plant sit exactly once on the right edge so both lanes terminate into the same sink.

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
Keep the taxonomy branches symmetrical around the root and keep the bottom loop thin so it does not compete with the taxonomy.

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
Keep the horizon strip thin and detached from the main loop so it reads as prediction context rather than another control lane.

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
Keep the nominal chain uninterrupted and keep augmentation branches as side branches that merge only at the summation node.

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
Use a 16:9 horizontal canvas split vertically. The left half shows offline data and training. The right half shows two parallel runtime branches converging on a nominal control chain. Keep the learning branches vertically separated and let them merge only at the gating point. Place fallback and safety gating directly before the command summation or gain update. Use orthogonal connectors only.
Keep offline training isolated on the left half and do not let any runtime path start until the frozen-artifact block.

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
Keep the top pipeline compact and keep the state machine evenly spaced so the transition order is visually obvious.

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
Keep request/application evidence on the top track and keep recovery/landing outputs on the bottom track.

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
Keep the map as the dominant visual field and keep the decision blocks outside the map so the planning logic does not overlap the geometry.

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
Keep the middle plane widest because it is the only plane that carries the high-frequency loop.

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
Keep provenance strictly above the success path and keep failure reasons strictly below it so validation and rollback do not blend.

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
Keep the task-boundary comparison isolated from the main pipeline so Diff-Planner and FUEL are not visually merged.

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

## 21 Figure 21: 48-Controller Catalogue and Evidence Map

```text

Figure Subject:
Create a strict 2D catalogue-and-evidence diagram for the 48 frozen report entries. The figure must distinguish the 47 MWORKS Control Profiles from the one px4ctrl engineering/deployment baseline, group the Profiles by the seven report families, and state the current G3 effective screening result without turning structural coverage into a performance claim. Use a white background, flat vector graphics, black borders, and distinct restrained pale colors for family cards and evidence-status cards.

Diagram type:
Catalogue hierarchy with a parallel family grid and a bottom evidence-status strip.

Layout:
Use a 16:9 horizontal canvas. Put one root at the top center. In the second row, place the 47 MWORKS Profile parent on the left two-thirds and the px4ctrl baseline card on the right third. Under the MWORKS parent, place seven equal-size family cards in a strict 4-plus-3 grid with a blank grid cell for balance; do not draw controller-name leaves. Put a full-width bottom status strip below the family grid. All connectors are short orthogonal downward segments or a single horizontal bus with equal vertical drops. Keep the px4ctrl card visually separate from the seven-family grid.

Mandatory nodes:
- Root: "48个冻结目录条目"
- "MWORKS Control Profiles（47条）"
- "px4ctrl工程/部署基线（1条）"
- "PID族（10条）"
- "线性与鲁棒（6条）"
- "非线性与自适应（6条）"
- "滑模（7条）"
- "预测与优化（10条）"
- "几何与微分平坦（6条）"
- "学习控制（2条）"
- "名义ClimbPath 50 s筛查"
- "G3有效状态：28通过 / 20失败"
- "结构覆盖不等于性能通过"
- "逐控制器证据见正文表格"
- Scope note: "G3状态表的48行与冻结目录的48条不是同一命名空间，二者仅41条对齐"
- Scope note: "五个口径不可相加：目录48 / 脚本49 / 对齐41 / 跑完38 / 性能接受28"

Mandatory connections:
- "48个冻结目录条目" -> "MWORKS Control Profiles（47条）" and "px4ctrl工程/部署基线（1条）" using two short orthogonal downward branches.
- "MWORKS Control Profiles（47条）" -> all seven family cards by one horizontal bus with seven equal vertical drops.
- The seven family cards -> "名义ClimbPath 50 s筛查" by seven short aligned dotted evidence guides; do not connect family cards to one another.
- "名义ClimbPath 50 s筛查" -> "G3有效状态：28通过 / 20失败" -> "结构覆盖不等于性能通过" -> "逐控制器证据见正文表格" as a left-to-right bottom strip.
- "px4ctrl工程/部署基线（1条）" -> "逐控制器证据见正文表格" using one thin dashed factual-reference guide, not a family membership arrow.
- Print "G3状态表的48行与冻结目录的48条不是同一命名空间，二者仅41条对齐" as a gray callout bound to the boundary between the family grid and "名义ClimbPath 50 s筛查", so the screening strip is read as a separate namespace rather than a subtotal of the root.
- Print "五个口径不可相加：目录48 / 脚本49 / 对齐41 / 跑完38 / 性能接受28" as a gray callout at the lower-right corner of the bottom strip.

Negative constraints:
Do not sum, subtract, or otherwise reconcile the root count with any screening count, and do not draw the bottom strip as a partition of the 48 root entries. Do not show 46 routes, historical year timelines, MATLAB toolbox prices, annual-cost claims, software logos, individual controller leaves, family-to-family evolution arrows, or a claim that all entries passed or were deployed. Do not treat px4ctrl as a MWORKS Profile family member. No 3D, gradients, shadows, screenshots, decorative icons, curved branches, crossed lines, floating text, appendix labels, or marketing comparisons.
```

---

## 22 Figure 22: G3 Effective Failure Classification

```text

Figure Subject:
Create a strict 2D classification diagram for the frozen G3 effective failures in the nominal ClimbPath 50 s screen. It must report four mutually exclusive result-status classes and their counts without guessing root causes, giving example controllers, or drawing a decision/diagnostic process that the evidence does not establish. Use a white background, flat vector graphics, black borders, pale red for failure-class cards, pale yellow for the screen/source strip, and pale gray for scope notes.

Diagram type:
Four-column result-classification matrix with a shared evidence-source strip.

Layout:
Use a 16:9 horizontal canvas. Place the screen node at the upper left and the root failure-total node at the upper center. Draw one short horizontal bus below the root. Under it, place four equal-width and equal-height failure-class cards in one left-to-right row. Connect the bus to the cards with four equal vertical drops; do not use diamonds, nested branches, side statistics boxes, or diagonal lines. Put one full-width shared source strip below the cards. Put the two scope notes in compact gray callouts at the lower corners.

Mandatory nodes:
- "ClimbPath 50 s名义筛查"
- Root: "G3有效失败（20 / 48）"
- Card 1: "CheckModel未通过（1）"
- Code label: "check_model_failed"
- Card 2: "仿真API失败（2）"
- Code label: "simulate_failed"
- Card 3: "MCP仿真超时（8）"
- Code label: "simulation_timeout"
- Card 4: "终端位置误差 ≥ 5 m（9）"
- Code label: "terminal_position_error_exceeds_5m"
- "G3_STATUS.json + 各控制器RUN_RECORD"
- "分类仅为结果状态，不等于根因分析"
- "失败记录保留，不改写为“待跑”"
- Scope note: "G3_STATUS.json 记为 completed = false，扫描尚未收口，计数为2026-07-30快照"

Mandatory connections:
- "ClimbPath 50 s名义筛查" -> "G3有效失败（20 / 48）".
- "G3有效失败（20 / 48）" -> one short horizontal bus -> the four failure-class cards by four equal vertical drops.
- Place each code label directly inside the lower edge of its matching card; do not draw it as a separate connected node.
- Put "G3_STATUS.json + 各控制器RUN_RECORD" as the shared full-width source strip below the four cards, with no causal arrows into the cards.
- Print "G3_STATUS.json 记为 completed = false，扫描尚未收口，计数为2026-07-30快照" inside the source strip as a second line of that strip, in gray, not as a separate connected node.
- Bind "分类仅为结果状态，不等于根因分析" to the lower-left gray callout.
- Bind "失败记录保留，不改写为“待跑”" to the lower-right gray callout.

Negative constraints:
Do not show controller examples, common causes, parameter-tuning recommendations, fault trees, decision diamonds, success paths, recovery promises, or permanent-failure claims. Do not present the counts as a closed or final sweep result. Do not imply that this classification replaces a controller-specific evidence review. No 3D, gradients, shadows, screenshots, decorative icons, curved connectors, crossed branches, floating text, appendix labels, or success-biased language.
```

---

## Recommended Drawing Order

1. Figures 01, 02, 03, 06, 07, 16, and 17.
2. Figures 04 and 05.
3. Figures 08 through 14.
4. Figure 15.
5. Figures 18 through 20.
6. **Figures 21 and 22 after the Chapter 10 catalogue table and G3 source-status table are fixed.**

Use real screenshots instead of additional hand-drawn figures for the MWORKS whole-aircraft model, motor and sensor subsystem models, Model Studio UI, MWORKS Result Viewer animation, controller Sysblock models, controller result curves, QGC, RViz, UE, point clouds, maps, and runtime windows.

---

## PPT-Specific Blocks

The blocks below are new figures needed for the 答辩PPT only. They are not report body figures.
Send one block at a time to the image-generation model.

---

## PPT-01 Full-Chain Pipeline: Sysblock → C99 → SIL → ROS Bridge → Gazebo

```text
Figure Subject:
Create a strict left-to-right pipeline diagram showing the complete MoSim chain from MWORKS Sysblock graphical modelling through ISO C99 code generation, CFunction SIL verification, a custom ROS bridge, to PX4 SITL and Gazebo runtime connection. Use a white background, flat vector graphics, black text, solid black borders, and a restrained four-color palette: pale blue for MWORKS nodes, pale green for generated-code and SIL nodes, pale orange for the ROS/runtime layer, and pale gray for evidence or display nodes.

Diagram type:
Horizontal five-stage pipeline with one evidence column at the far right.

Layout:
Use a 16:9 horizontal canvas with five equal-width vertical stages and one narrow shared evidence column. Place one primary node per stage in a single center row. Add a short annotation band below each stage node. Keep all connectors strictly horizontal; no diagonal lines. Add a thin dashed gray comparison row at the very bottom labeled "等效路径（仅供参考）" with "Simulink → Embedded Coder → PX4 SITL" nodes in light gray to show the equivalent MATLAB toolchain.

Mandatory nodes:
- Stage 1 (pale blue): "MWORKS.Sysblock\n图形化控制器建模"
- Stage 2 (pale green): "GenerateModelCode\n→ ISO C99 源码\n（无Runtime依赖）"
- Stage 3 (pale green): "CFunction SIL 夹具\n数值一致性验证\nRMSE 1.148e-13 m"
- Stage 4 (pale orange): "自研ROS Bridge\n四接口统一接入\nMAVROS · PX4 SITL"
- Stage 5 (pale orange): "Gazebo Classic\n全链路联通\n（rosbag + RViz 录屏）"
- Evidence column (pale gray): "Result.msr / rosbag\nRViz截图 / 指标CSV"
- Comparison row: light gray nodes "Simulink", "Embedded Coder", "PX4 SITL" with label "等效路径（仅供参考）"
- Annotation below Stage 1: "Sysblock 图形 = 可生成代码的控制模型"
- Annotation below Stage 2: "ISO C99，GCC 直接编译，无 Runtime 依赖"
- Annotation below Stage 3: "MIL/SIL 双精度量级一致，已通过"
- Annotation below Stage 4: "ATTITUDE_THRUST / BODY_RATE_THRUST\nWRENCH / ROTOR_COMMAND"
- Annotation below Stage 5: "Ubuntu 20.04 / ROS1 Noetic / Gazebo Classic / WSL2"

Mandatory connections:
- Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5, all as solid black horizontal arrows.
- Stage 5 → Evidence column as one solid black arrow.
- The comparison row runs below the five stage annotations with light gray arrows Simulink → Embedded Coder → PX4 SITL and a bracket or brace connecting it to the main pipeline to indicate equivalence only, not a data flow.

Negative constraints:
Do not label Stage 5 as "Figure8验证通过" or imply a formal tracking performance pass in Gazebo. Do not imply that the generated code has been deployed to a physical drone. Do not merge the SIL node with the Gazebo node. Do not draw the comparison row as a data path into or out of the main pipeline. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, or floating text outside bordered nodes.
```

---

## PPT-02 Five-Layer MoSim Architecture

```text
Figure Subject:
Create a five-layer vertical stack architecture diagram for the MoSim platform showing that the first four layers are entirely inside MWORKS and only the fifth layer belongs to WSL2. Each layer is a full-width horizontal band. Use a white background, flat vector graphics, black text, and one distinct pale color per layer. Keep all connectors strictly vertical between adjacent layers; no diagonal lines.

Diagram type:
Five-layer vertical architecture stack with a right-side annotation column and a left-side tool-label column.

Layout:
Use a 16:9 horizontal canvas. Stack five equal-height bands top to bottom. Put a tool-label strip on the left edge of each band (tool names only). Put node names inside each band. Put a right-side annotation column with one short note per layer. Keep all inter-layer arrows as short vertical drops centered on the band border. Draw a single pale blue bracket spanning layers 1–4 on the left margin labeled "纯 MWORKS 内部" and a separate pale orange bracket spanning layer 5 labeled "WSL2 运行层".

Mandatory nodes (top to bottom):
- Layer 1 (pale blue, "建模层"): "MWORKS.Sysplorer（MultiBody机体 · 6DOF）", "MWORKS.Sysblock（控制器图形化 · 46路）", "MWORKS.Syslab（数据分析 · Julia）"
- Layer 2 (pale green, "生成层"): "GenerateModelCode → ISO C99 源码（无Runtime依赖）"
- Layer 3 (pale yellow, "验证层"): "CFunction SIL夹具（RMSE 1.148e-13 m）", "FormalRunner（ClimbPath 50s · 30/48 通过）"
- Layer 4 (pale cyan, "MWORKS扩展层"): "三机编队 TriangleFigure8（MWORKS Sysplorer）", "OpenBlocks 轨迹（A*冻结参数·Modelica）", "ECBF 安全层（Modelica·全MWORKS内）"
- Layer 5 (pale orange, "WSL2运行层"): "自研ROS Bridge · PX4 SITL · Gazebo Classic", "FAST-LIO 感知节点（Ubuntu 20.04 / ROS1 Noetic）"
- Right annotation col: "MWORKS主线 ←" beside layers 1–3; "MWORKS内扩展 ←" beside layer 4; "WSL2链路 ←" beside layer 5

Mandatory connections:
- One centered vertical arrow from Layer 1 bottom edge to Layer 2 top edge.
- One centered vertical arrow from Layer 2 to Layer 3.
- One centered vertical arrow from Layer 3 to Layer 4.
- One centered vertical arrow from Layer 4 to Layer 5, labeled "C99导出 → ROS Bridge" on the arrow.
- A thin dashed gray upward arrow from Layer 5 back to Layer 3 labeled "运行时证据回传" on the right margin, not crossing any band content.

Negative constraints:
Do not place OpenBlocks, ECBF, or three-UAV formation in Layer 5 (WSL2). OpenBlocks and ECBF are pure Modelica models running inside MWORKS; they have no Gazebo dependency. Do not merge layers or draw horizontal connectors between nodes inside the same layer. Do not label WSL2 as Docker. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, crossed connectors, or floating text.
```

---

## PPT-03 Four Output Interfaces Shared Plant

```text
Figure Subject:
Create a strict 2D diagram showing four parallel control-output interface types converging on one shared Plant node. Use a white background, flat vector graphics, black text, solid black borders, pale blue for interface nodes, pale green for the Adapter node, and pale gray for the Plant and evidence nodes.

Diagram type:
Four-to-one fan-in pipeline with a shared Adapter and shared Plant.

Layout:
Use a 16:9 horizontal canvas. Place four equal-height interface nodes in a vertical column on the left. Place one Adapter node in the center. Place one shared Plant node on the right. Draw four horizontal arrows from the interface column to the Adapter, then one arrow from Adapter to Plant. Below the Plant, add a small pale gray evidence node. Keep all connectors strictly horizontal; no diagonal lines and no fan-out tangles.

Mandatory nodes:
- Interface 1: "ATTITUDE_THRUST\n姿态+推力指令"
- Interface 2: "BODY_RATE_THRUST\n机体角速率+推力"
- Interface 3: "WRENCH\n力和力矩"
- Interface 4: "ROTOR_COMMAND\n电机转速指令"
- Center: "Adapter\n（坐标变换 ENU/FLU ↔ NED/FRD）"
- Right: "共享 Plant\n（云纵150 MultiBody）"
- Below Plant: "Result.msr / 评测指标"
- Annotation: "46条控制器均通过上述接口之一输出"

Mandatory connections:
- Each of the four interface nodes → Adapter by one straight horizontal arrow.
- Adapter → Plant by one straight horizontal arrow.
- Plant → Result node by one short downward arrow.
- Bind annotation "46条控制器均通过上述接口之一输出" below the four interface nodes as a bracket label.

Negative constraints:
Do not duplicate the Plant node. Do not merge any two interface lanes into one arrow before the Adapter. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, or floating text.
```

---

## PPT-04 Three-UAV Formation Guidance Architecture

```text
Figure Subject:
Create a strict top-down architecture diagram for the MoSim three-UAV formation control system running entirely inside MWORKS Sysplorer. Show the formation task goal feeding a single Guidance layer that generates three independent reference trajectories, each consumed by an independent single-UAV controller, each driving an independent Plant. Use a white background, flat vector graphics, black text, pale blue for guidance nodes, pale green for controller nodes, pale gray for Plant nodes, and pale red for the optional ECBF safety layer.

Diagram type:
Top-down fan-out hierarchy with three independent lanes and one optional ECBF layer, all inside a labeled MWORKS boundary box.

Layout:
Use a 16:9 horizontal canvas. Draw a pale blue dashed outer boundary box labeled "纯 MWORKS Sysplorer 仿真（不含 Gazebo / ROS）" that encloses the entire diagram. Inside, place four horizontal rows top to bottom: (1) formation goal, (2) Guidance layer with ECBF sublayer (dashed pale red, pluggable), (3) three parallel controller nodes, (4) three parallel Plant nodes. Add an optional ECBF row between rows 2 and 3, shown in pale red with a dashed border to indicate it is pluggable. Below row 4, add a metrics strip outside the MWORKS box. Keep all connectors strictly vertical within each of the three lanes; cross-lane comparison outputs belong only in the bottom metrics row.

Mandatory nodes:
- Row 1: "编队任务目标（等边三角形 Figure8）"
- Row 2: "Guidance 层\nTriangleFigure8Reference.mo\n（MWORKS Modelica 模型）"
- ECBF row (dashed pale red): "ECBF 安全层（可插拔）\nThreeUavPairwiseEcbfReferenceSafetyFilter.mo\nh(x)≥0，ḣ+γh≥0"
- Row 3 (three equal nodes): "px4ctrl × UAV1", "px4ctrl × UAV2", "px4ctrl × UAV3"
- Row 4 (three equal nodes): "Plant × UAV1\n（云纵150 MultiBody）", "Plant × UAV2\n（云纵150 MultiBody）", "Plant × UAV3\n（云纵150 MultiBody）"
- Metrics strip (below MWORKS box): "协同指标：编队RMSE = 2.2855e-13 m｜最近距离 = 2.0785 m（MIL仿真，非实飞）"

Mandatory connections:
- "编队任务目标" → "Guidance 层" by one centered vertical arrow.
- "Guidance 层" → three equal vertical drops into the ECBF row (or directly into the controller row if ECBF is bypassed).
- ECBF row → three vertical arrows into the three controller nodes.
- Each controller → its matching Plant by one vertical arrow.
- Each Plant → metrics strip by one short downward arrow.
- A thin dashed gray bidirectional lateral arrow between Plant×UAV1 and Plant×UAV2 and between Plant×UAV2 and Plant×UAV3 labeled "协同状态采集" only, not a command wire.

Negative constraints:
Do not draw any Gazebo, ROS, or WSL2 node inside this diagram. Do not draw a command wire from any Plant to a different UAV's controller. Do not draw the ECBF node as a mandatory pass-through in the main chain; keep its dashed border to show it is optional. Do not present the formation RMSE as a physical-hardware or Gazebo measurement. The MWORKS outer boundary box must be visible and labeled. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, crossed connectors, or floating text.
```

---

## PPT-05 WSL2 Deployment Stack

```text
Figure Subject:
Create a strict 2D layered deployment diagram for the MoSim runtime environment running inside WSL2. Show the hardware host, the WSL2 boundary, and the software stack layers inside WSL2 clearly. Use a white background, flat vector graphics, black text, a dashed border for the WSL2 isolation boundary, pale blue for OS/kernel nodes, pale orange for ROS/middleware nodes, pale green for simulation nodes, and pale gray for the host hardware strip.

Diagram type:
Nested vertical layer stack inside a dashed WSL2 boundary box.

Layout:
Use a 16:9 horizontal canvas. Draw a pale gray host strip at the very bottom labeled "Windows 11 宿主机（MWORKS GUI · UE · 显卡）". Above it draw a large dashed-border rectangle labeled "WSL2 隔离边界". Inside the rectangle stack five horizontal bands from bottom to top. Add a right-side annotation column outside the WSL2 box explaining why WSL2 is preferred over Docker.

Mandatory nodes (bottom to top inside WSL2 box):
- Band 1 (pale blue): "Ubuntu 20.04 LTS"
- Band 2 (pale blue): "ROS1 Noetic"
- Band 3 (pale orange): "MAVROS · rosbridge · 自研ROS Bridge"
- Band 4 (pale green): "PX4 SITL · Gazebo Classic · RViz"
- Band 5 (pale green): "FAST-LIO 感知节点 · MoSim ROS Bridge节点"
- Host strip (pale gray, below dashed box): "Windows 11 宿主机（MWORKS · UE · 显卡 · 授权）"
- Right annotation col:
  - "WSL2 vs Docker"
  - "MWORKS/UE 需本机 GUI 和显卡 →\nDocker 无法承载"
  - "WSL2 共享宿主 GPU 和授权 →\n完整演示链路"

Mandatory connections:
- Short upward arrows between each adjacent band pair inside the WSL2 box, one per band boundary, centered.
- One bidirectional horizontal arrow crossing the dashed WSL2 boundary labeled "X11 / WSLg 图形透传" connecting Band 4 to the host strip area.

Negative constraints:
Do not place OpenBlocks or ECBF or any formation controller inside the WSL2 box. OpenBlocks and ECBF are pure Modelica models that run inside MWORKS, not in WSL2. Do not label WSL2 as Docker or mention Docker anywhere inside the figure. Do not imply the host strip runs the ROS stack. Do not show a separate Docker layer. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, or floating text.
```

---

## PPT Drawing Order

Send PPT blocks in this order:

1. **PPT-01** — Full-chain pipeline (封面三联图替代品，P04页)
2. **PPT-02** — Five-layer architecture (P05页)
3. **PPT-03** — Four interfaces shared Plant (P08页)
4. **PPT-04** — Three-UAV Guidance architecture (已废弃，改为P29 OpenBlocks架构)
5. **PPT-05** — WSL2 deployment stack (已废弃，改为P35 ROS Bridge架构)
6. **PPT-06** — Quadrotor dynamics model (P07页)
7. **PPT-07** — Adapter coordinate transformation (P08页)
8. **PPT-08** — Unified experiment framework (P08页)
9. **PPT-09** — Seven algorithm families classification tree (P10页)
10. **PPT-10** — px4ctrl three-layer architecture (P17页)
11. **PPT-11** — AI Agent knowledge injection architecture (P21页)
12. **PPT-12** — OpenBlocks planning pipeline (P29页)
13. **PPT-13** — MWORKS real-time outer loop with WSL2 data flow (P35页)
14. **PPT-14** — C99 code package structure and deployment paths (P40页)
15. **PPT-15** — Gazebo state feedback pathway design (P43页)
16. **PPT-16** — Diff-Planner differential flatness trajectory optimization (P47页)
17. **PPT-17** — FUEL autonomous exploration architecture (P48页)
18. **PPT-18** — UE to Gazebo mesh export pipeline (P49页)
19. **PPT-19** — MWORKS full-chain capability map (P50页)

---

## PPT-06: Quadrotor Dynamics Model (P07页)

**Figure Subject**: 四旋翼六自由度动力学模型与控制分配矩阵

**Diagram type**: Technical schematic (A类：架构/流程图)

**Layout**: 16:9 landscape, top-bottom split layout

**Mandatory nodes and visual elements**:

**Upper section (60% height) — Dynamics model**:
- Central quadrotor frame (X configuration):
  - Body coordinate system: FLU (Forward-Left-Up), labeled axes X_B, Y_B, Z_B
  - Four rotors numbered 1-4:
    - Rotor 1: front-right, CCW rotation (⟲)
    - Rotor 2: rear-left, CCW rotation (⟲)
    - Rotor 3: front-left, CW rotation (⟳)
    - Rotor 4: rear-right, CW rotation (⟳)
  - Arm length L = 0.22m labeled on two arms
  - Thrust vectors T₁, T₂, T₃, T₄ pointing upward from each rotor
  - Total thrust F = T₁ + T₂ + T₃ + T₄ (large upward arrow at center)
  - Torque vectors τₓ, τᵧ, τᵤ at body center

**Key equations box (right side of upper section)**:
```
Force balance:
m·a = F - mg - F_drag

Euler dynamics:
J·ω̇ = τ - ω × (J·ω)

where:
F = [0, 0, Σ Tᵢ]ᵀ
τ = [τₓ, τᵧ, τᵤ]ᵀ
```

**Lower section (40% height) — Control allocation matrix**:
- Left: Allocation matrix B (4×4):
```
[F  ]     [1    1    1    1  ] [ω₁²]
[τₓ]  =   [0   -Ly   0    Ly ] [ω₂²]
[τᵧ]      [Lx   0   -Lx   0  ] [ω₃²]
[τᵤ]      [-c   c   -c    c  ] [ω₄²]
```
- Right: Motor response model block diagram:
  - Input: ω_des (desired rotor speed)
  - Block: First-order inertia G(s) = 1/(τs+1), τ=0.02s
  - Output: ω_act (actual rotor speed) → T (thrust)
  - Formula: T = k_T·ω²

**Parameter annotation box (bottom-right corner)**:
```
Arm length:    L = 0.22 m
Lift coeff:    k_T = 1.05×10⁻⁵ N/(rad/s)²
Torque coeff:  k_M = 1.8×10⁻⁷ Nm/(rad/s)²
Motor τ:       0.02 s
```

**Connections**:
- Dashed arrows from rotor thrusts to allocation matrix
- Solid arrows showing data flow in motor response model

**Color scheme**:
- Quadrotor frame: dark gray #2C3E50
- Rotor discs: pale blue #AED6F1 with rotation direction arrows
- Thrust vectors: vibrant blue #3498DB
- Torque vectors: orange #E67E22
- Equation boxes: light cream background #FFF9E6 with dark text
- Parameter box: pale green background #E8F8E8

**Typography**:
- Equation font: Computer Modern (LaTeX style), 14pt
- Labels: Arial, 12pt
- Parameters: Arial, 10pt

**Negative constraints**:
- No 3D perspective rendering
- No shading or gradients on the quadrotor frame
- No decorative elements
- Connectors must be orthogonal or 45° diagonal, no curved arrows
- No photo-realistic rendering

---

## PPT-07: Adapter Coordinate Transformation (P08页)

**Figure Subject**: 坐标系转换与四元数顺序适配层详解

**Diagram type**: Technical schematic with code snippets (A类：架构/流程图 + 代码)

**Layout**: 16:9 landscape, left-right split layout

**Mandatory nodes and visual elements**:

**Left section (50% width) — Coordinate transformations**:
- Two coordinate system diagrams side-by-side:
  
  **ENU/FLU (MWORKS)**:
  - 3D coordinate axes:
    - X_ENU: East (right), red arrow
    - Y_ENU: North (forward), green arrow
    - Z_ENU: Up (upward), blue arrow
  - Quadrotor orientation: Forward=North, Left=West, Up=Up
  - Label: "MWORKS Modelica"

  **NED/FRD (PX4)**:
  - 3D coordinate axes:
    - X_NED: North (forward), red arrow
    - Y_NED: East (right), green arrow
    - Z_NED: Down (downward), blue arrow
  - Quadrotor orientation: Forward=North, Right=East, Down=Down
  - Label: "PX4 Flight Controller"

- Transformation matrix between them:
```
R_ENU→NED = [0  1  0]
            [1  0  0]
            [0  0 -1]

Position: [x_NED] = R_ENU→NED · [x_ENU]
          [y_NED]              [y_ENU]
          [z_NED]              [z_ENU]
```

**Right section (50% width) — Quaternion order conversion**:
- Two quaternion representations:

  **MWORKS format**:
  ```
  q_MWORKS = [w, x, y, z]
             ↑  scalar first
  ```

  **PX4 format**:
  ```
  q_PX4 = [x, y, z, w]
          ↑  vector first
  ```

- Conversion code snippet box:
```cpp
// Adapter layer code
void convertQuaternion(
    const double q_mworks[4],  // [w,x,y,z]
    double q_px4[4]            // [x,y,z,w]
) {
    q_px4[0] = q_mworks[1];  // x
    q_px4[1] = q_mworks[2];  // y
    q_px4[2] = q_mworks[3];  // z
    q_px4[3] = q_mworks[0];  // w
}
```

**Warning box (bottom-right)**:
```
⚠ Critical: Quaternion order mismatch
causes 180° attitude errors!
Always use Adapter layer conversion.
```

**Connections**:
- Bidirectional arrow between ENU/FLU and NED/FRD coordinate systems
- Arrow from MWORKS quaternion to PX4 quaternion with "Adapter" label
- Dashed box around code snippet

**Color scheme**:
- Coordinate axes: standard RGB (red X, green Y, blue Z)
- Transformation matrix: light blue background #D6EAF8
- Code snippet: dark background #2C3E50 with syntax highlighting
  - Keywords: blue #3498DB
  - Comments: green #27AE60
  - Values: orange #E67E22
- Warning box: pale yellow background #FFF3CD with red border #E74C3C

**Typography**:
- Coordinate labels: Arial Bold, 14pt
- Matrix elements: Computer Modern, 12pt
- Code: Consolas monospace, 10pt
- Warning text: Arial, 11pt

**Negative constraints**:
- No 3D mesh rendering of quadrotor
- No curved transformation arrows
- No decorative borders around code
- Keep coordinate diagrams simple, no terrain or environment

---

## PPT-08: Unified Experiment Framework (P08页)

**Figure Subject**: 基于Sysblock的统一实验框架架构与故障注入路径

**Diagram type**: System architecture diagram (A类：架构/流程图)

**Layout**: 16:9 landscape, top-to-bottom flow with side annotations

**Mandatory nodes and visual elements**:

**Top layer — Configuration**:
- Profile configuration file icon (document with gears)
- Label: "Profile Config"
- Parameters listed:
  - Trajectory type (hover/climb/figure8/spiral)
  - Controller selection (48 options)
  - Fault injection settings
  - Evaluation metrics

**Second layer — Controller Core**:
- Large central box: "Sysblock Controller Core"
- Sub-components visible through transparent overlay:
  - Position control block
  - Attitude control block
  - Control allocation block
- Annotation callout (star-burst style): "48个控制器全部改为Sysblock图形建模"

**Third layer — Adapter**:
- Adapter layer box with 4 output branches:
  - ATTITUDE_THRUST
  - BODY_RATE_THRUST
  - WRENCH
  - ROTOR_COMMAND
- Coordinate transformation icon (ENU↔NED)

**Fourth layer — Plant**:
- Unified Plant box: "Sunray150 MultiBody Model"
- Icon showing 6-DOF dynamics
- Label: "共享Plant确保同条件对比"

**Right side — Fault injection module** (parallel to controller→plant flow):
- Fault injection panel with three switches:
  - Wind disturbance (wind icon, 10 m/s)
  - Parameter mismatch (mass/inertia sliders, ±30%)
  - Motor efficiency fault (motor icon with red X, 60%)
- Dashed arrows injecting into Plant

**Bottom layer — Output & Evaluation**:
- Output collection box:
  - Position trajectory
  - Attitude response
  - Control inputs
- Unified evaluation metrics box:
  - RMSE (position tracking)
  - Response time
  - Overshoot percentage

**Right panel — Key annotations**:
- Annotation box 1:
  ```
  ✅ 核心架构:
  MoSimQuadrotorModel.Experiment.Baselines
  ```
- Annotation box 2:
  ```
  ✅ 统一验证条件:
  - 同一Plant模型
  - 同一评价指标
  - 同一扰动注入
  ```

**Numerical summary card (bottom-right)**:
```
控制器总数: 48个
有Runner: 46个
缺失: 2个 (fixed_awff_pid, pid_awff_linear_eso)
```

**Connections**:
- Solid arrows: main data flow (Profile → Controller → Adapter → Plant → Output)
- Dashed arrows: fault injection paths (Fault module → Plant)
- Dotted arrows: feedback paths (Output → Evaluation)

**Color scheme**:
- Profile config: pale blue #D6EAF8
- Sysblock controller: vibrant green #58D68D with semi-transparent fill
- Adapter: orange #F8B400
- Plant: deep blue #2E86C1
- Fault injection: red #E74C3C with warning stripes
- Output/Evaluation: purple #9B59B6
- Annotation boxes: light yellow #FFF9E6 with green checkmarks #27AE60

**Typography**:
- Main labels: Arial Bold, 14pt
- Sub-labels: Arial, 11pt
- Annotations: Arial, 10pt
- Numerical card: Arial Bold, 12pt for numbers, 10pt for labels

**Negative constraints**:
- No photo-realistic Sysblock screenshots
- No detailed controller internals visible
- No gradient fills on major boxes
- Connectors must be orthogonal, no curved arrows
- No drop shadows on boxes

---

## PPT-09: Seven Algorithm Families Classification Tree (P10页)

**Figure Subject**: 七族控制算法分类树状结构图

**Diagram type**: Hierarchical tree diagram (A类：架构/流程图)

**Layout**: 16:9 landscape, top-down tree expansion

**Mandatory nodes and visual elements**:

**Root node (top center)**:
- Large box: "控制算法族 (48个控制器)"
- Icon: controller symbol (PID block generic icon)

**Level 1 — Seven families** (7 branches from root):

1. **PID改进族 (9个)**
   - Sub-nodes (Level 2):
     - cascade_pid
     - official_pid (标注: 工程基线)
     - awff (标注: 前馈增强)
     - pid_linear_eso
     - incremental_pid
     - fuzzy_pid
     - adaptive_pid
     - pid_awff
     - setpoint_prefilter_pid

2. **线性/鲁棒控制 (4个)**
   - Sub-nodes:
     - lqr
     - lqg
     - h_infinity
     - robust_pole_placement

3. **滑模控制 (6个)**
   - Sub-nodes:
     - smc (标注: 传统滑模)
     - stc (标注: Super-Twisting)
     - adaptive_smc
     - terminal_smc
     - integral_smc
     - fast_terminal_smc

4. **最优/预测控制 (5个)**
   - Sub-nodes:
     - mpc (标注: 线性MPC)
     - nmpc (标注: 非线性MPC)
     - empc (标注: 经济MPC)
     - tube_mpc
     - adaptive_mpc

5. **几何控制 (3个)**
   - Sub-nodes:
     - se3_control (标注: SE(3)流形)
     - quaternion_control
     - geometric_tracking

6. **智能算法 (5个)**
   - Sub-nodes:
     - fuzzy_logic
     - neural_pid
     - anfis_control
     - expert_system
     - rule_based

7. **学习/自适应 (12个)**
   - Sub-nodes:
     - adaptive_backstepping
     - mrac (标注: 模型参考自适应)
     - l1_adaptive
     - gain_scheduling
     - iterative_learning
     - reinforcement_learning
     - neural_network_adaptive
     - online_optimization
     - self_tuning
     - adaptive_sliding_mode
     - adaptive_robust
     - dual_adaptive

**Visual styling for tree structure**:
- Root node: large rounded rectangle, bold border
- Family nodes (Level 1): medium rounded rectangles with family icons
- Controller nodes (Level 2): small rounded rectangles, lighter fill

**Family icons** (simple symbols next to family names):
- PID: classic PID block symbol
- Linear/Robust: eigenvalue diagram
- Sliding Mode: switching function symbol
- Optimal/Predictive: horizon timeline
- Geometric: manifold curve
- Intelligent: neural network node
- Learning/Adaptive: feedback loop with adaptation

**Annotations** (callout style):
- Official PID baseline: small star marker
- Key distinguishing features for major families

**Connections**:
- Tree branches: straight lines, orthogonal or angled
- Branch thickness: root→family (thick), family→controller (thin)

**Color scheme**:
- Root node: deep blue #2E86C1
- Family colors (pastel palette for distinction):
  - PID: pale green #A9DFBF
  - Linear/Robust: pale blue #AED6F1
  - Sliding Mode: pale orange #F8C471
  - Optimal/Predictive: pale purple #D7BDE2
  - Geometric: pale teal #A2D9CE
  - Intelligent: pale pink #F5B7B1
  - Learning/Adaptive: pale yellow #F9E79F
- Controller nodes: white fill with family-colored border

**Typography**:
- Root: Arial Bold, 16pt
- Family names: Arial Bold, 13pt
- Controller names: Arial, 10pt
- Annotations: Arial Italic, 9pt
- Count numbers: Arial Bold, 11pt

**Layout constraints**:
- Families spread evenly across width
- Controllers under each family arranged in compact columns
- Tree depth maximum 2 levels (family → controller)
- Maintain symmetry where possible

**Negative constraints**:
- No decorative leaf/tree imagery
- No gradient fills
- No drop shadows
- No curved connector lines
- No photo-realistic controller screenshots

---

## PPT-10: px4ctrl Three-Layer Architecture (P17页)

**Figure Subject**: px4ctrl分层控制器架构：外环位置/中环速度/内环姿态

**Diagram type**: Layered control architecture diagram (A类：架构/流程图)

**Layout**: 16:9 landscape, vertical three-layer stack with data flow

**Mandatory nodes and visual elements**:

**Top layer — Outer Loop (Position Control)**:
- Large box labeled: "外环：位置控制 (Outer Loop: Position Control)"
- Inputs (left side):
  - Position reference: (x_ref, y_ref, z_ref, yaw_ref)
  - Current position: (x, y, z, yaw)
- PID controller blocks:
  - X-axis PID: P=1.5, I=0.1, D=0.8
  - Y-axis PID: P=1.5, I=0.1, D=0.8
  - Z-axis PID: P=1.5, I=0.1, D=0.8
- Outputs (right side):
  - Desired velocity: (v_x_des, v_y_des, v_z_des)
  - Desired yaw: yaw_des

**Middle layer — Mid Loop (Velocity Control)**:
- Large box labeled: "中环：速度控制 (Mid Loop: Velocity Control)"
- Inputs (from outer loop):
  - Velocity error: (v_err_x, v_err_y, v_err_z)
- PID controller blocks:
  - V_x PID: P=2.0, I=0.5, D=0.3
  - V_y PID: P=2.0, I=0.5, D=0.3
  - V_z PID: P=2.0, I=0.5, D=0.3
- Attitude conversion block:
  - Converts velocity commands to desired attitude (roll_des, pitch_des)
  - Thrust calculation: T = m·(a_z_des + g)
- Outputs (right side):
  - Desired attitude: (roll_des, pitch_des, yaw_des)
  - Thrust: T

**Bottom layer — Inner Loop (Attitude Control)**:
- Large box labeled: "内环：姿态控制 (Inner Loop: Attitude Control)"
- Inputs (from mid loop):
  - Attitude error: (roll_err, pitch_err, yaw_err)
- PD controller blocks:
  - Roll PD: P=6.0, D=0.5
  - Pitch PD: P=6.0, D=0.5
  - Yaw PD: P=4.5, D=0.3
- Outputs (right side):
  - Body rate command: (p, q, r) [rad/s]
  - Final output format: BODY_RATE_THRUST

**Data flow arrows**:
- Solid thick arrows: primary control signal flow (top to bottom)
- Dashed arrows: reference inputs from external sources
- Thin solid arrows: internal block connections

**Parameter annotation boxes** (beside each layer):
- Outer loop: "快速跟踪 + 消除静差 + 阻尼振荡"
- Mid loop: "姿态响应 + 抗风扰 + 推力补偿"
- Inner loop: "快速姿态 + 抑制抖振 + 偏航稳定"

**Performance metrics card (bottom-right)**:
```
px4ctrl性能指标:
━━━━━━━━━━━━━━━
ClimbPath RMSE: 1.42m
vs Official PID: ↓32%
抗风扰能力: ↑45%
电机故障: 稳定飞行
```

**Connections**:
- Outer loop output → Mid loop input
- Mid loop output → Inner loop input
- Feedback paths (dotted lines) from each layer back to reference comparator

**Color scheme**:
- Outer loop: pale green #A9DFBF
- Mid loop: pale blue #AED6F1
- Inner loop: pale orange #F8C471
- PID blocks: white fill with layer-colored border
- Parameter boxes: light yellow #FFF9E6
- Performance card: light cream #FFFACD with green text for improvements

**Typography**:
- Layer titles: Arial Bold, 14pt
- PID parameters: Consolas monospace, 11pt
- Input/output labels: Arial, 10pt
- Annotation text: Arial, 9pt
- Performance metrics: Arial Bold, 11pt for numbers, Arial 9pt for labels

**Negative constraints**:
- No Sysblock screenshot overlays
- No decorative control system icons
- No gradient backgrounds on layers
- Arrows must be straight, no curved connectors
- No drop shadows on boxes

---

## PPT-11: AI Agent Knowledge Injection Architecture (P21页)

**Figure Subject**: MoSim助手领域知识注入架构与Syslab数据分析流程

**Diagram type**: System architecture diagram with data flow (A类：架构/流程图)

**Layout**: 16:9 landscape, top-to-bottom pipeline with side components

**Mandatory nodes and visual elements**:

**Top layer — Knowledge source**:
- Large document stack icon: "MWORKS官方文档"
- Sub-items listed:
  - API函数签名
  - 参数类型约束
  - 返回值规范
  - 使用示例

**Second layer — Knowledge distillation**:
- Process box: "结构化规则蒸馏"
- Arrow labeled: "人工标注 + 自动解析"
- Output: "规则库 (JSON/YAML)"
- Sample rule card displayed:
```json
{
  "function": "SimulateModel",
  "params": {
    "modelName": "string (required)",
    "stopTime": "number (optional, default 10)",
    "tolerance": "number (optional)"
  },
  "returns": "boolean (success/failure)"
}
```

**Third layer — MCP server configuration**:
- Server icon: "MCP服务器"
- Configuration panel showing:
  - Tool registration
  - Schema validation
  - Execution sandbox
- Bidirectional connection to Syslab

**Fourth layer — Syslab execution engine**:
- Large box: "Syslab Julia引擎"
- Components:
  - Code interpreter
  - TyPlot visualization
  - Data I/O handler
- Sample Julia code snippet:
```julia
# Example: Read simulation result
result = readResult("px4ctrl_result.mat")
rmse = calculateRMSE(result.position)
plot(result.time, result.position)
```

**Fifth layer — AI Agent interaction**:
- Chat interface mockup (left side):
  - User input: "分析px4ctrl与官方PID的seven场景对比"
  - Agent response workflow:
    1. Parse request
    2. Query rule library
    3. Generate Julia code
    4. Execute via MCP
    5. Return visualization

**Right side — Data flow pipeline**:
- Vertical flow diagram:
```
仿真结果文件 (.mat)
    ↓
助手调用MCP工具
    ↓
Syslab读取数据
    ↓
Julia计算指标
    ↓
TyPlot生成图表
    ↓
返回图表给用户
```

**Key benefits annotation box (bottom-right)**:
```
✅ 领域知识固化
   - 无需每次重新提示
   - 规则一致性保证

✅ 自动化分析流程
   - 从请求到图表全自动
   - 无人工编码介入

✅ 零学习门槛
   - 用户自然语言交互
   - 助手处理技术细节
```

**Connections**:
- Solid arrows: main knowledge/data flow
- Dashed arrows: configuration and control signals
- Bidirectional arrows: MCP ↔ Syslab communication

**Color scheme**:
- Knowledge source: pale blue #D6EAF8
- Distillation process: pale green #A9DFBF
- MCP server: orange #F8C471
- Syslab engine: deep blue #2E86C1
- AI Agent: purple #D7BDE2
- Data flow pipeline: light gray #ECF0F1 with blue arrows
- Benefits box: light yellow #FFF9E6 with green checkmarks

**Typography**:
- Layer titles: Arial Bold, 14pt
- Code snippets: Consolas monospace, 9pt
- Process labels: Arial, 11pt
- Annotations: Arial, 10pt
- Benefits text: Arial, 10pt

**Negative constraints**:
- No photo-realistic chat interface screenshots
- No actual MWORKS documentation screenshots
- No decorative AI/robot imagery
- Arrows must be orthogonal or 45°, no curves
- No gradient fills

---

## PPT-12: OpenBlocks Planning Pipeline (P29页)

**Figure Subject**: OpenBlocks规划链路：A*搜索与min-snap平滑在MWORKS内完成

**Diagram type**: Pipeline architecture diagram (A类：架构/流程图)

**Layout**: 16:9 landscape, left-to-right pipeline with MWORKS boundary

**Mandatory nodes and visual elements**:

**Large bounding box — MWORKS Sysplorer environment**:
- Dashed border encompassing entire pipeline
- Label at top-left: "MWORKS Sysplorer 内部实现"

**Pipeline stages (left to right within MWORKS box)**:

**Stage 1 — Obstacle map**:
- Grid map icon: "障碍地图"
- Parameters displayed:
  - 障碍体数量: 7118个
  - 栅格分辨率: 0.5m
  - 地图范围: 50m × 50m × 5m
- 3D obstacle visualization (simple voxel grid representation)

**Stage 2 — A* search**:
- Algorithm box: "A*搜索"
- Process details:
  - Cost function: f(n) = g(n) + h(n)
  - Heuristic: Euclidean distance
  - 8-connectivity search
- Arrow labeled: "离散航点 (waypoints)"
- Output: Sequence of waypoints (24个点)

**Stage 3 — min-snap smoothing**:
- Algorithm box: "min-snap平滑"
- Mathematical formulation:
```
min ∫ ||d⁴r/dt⁴||² dt
s.t. r(t) passes through waypoints
     ||v(t)|| ≤ v_max
     ||a(t)|| ≤ a_max
```
- Polynomial degree: 7th order
- Arrow labeled: "连续参考轨迹"

**Stage 4 — Trajectory output**:
- Output bundle:
  - Position: r(t) = [x(t), y(t), z(t)]
  - Velocity: v(t) = dr/dt
  - Acceleration: a(t) = d²r/dt²
- Time discretization: 50Hz (Δt = 0.02s)
- Total duration: 50s

**Stage 5 — MWORKS controller**:
- Controller box: "MWORKS控制器 (px4ctrl)"
- Reference tracking input
- Arrow to Plant (outside MWORKS boundary)

**Key annotation callouts**:

**Callout 1 (top-right, star-burst)**:
```
✅ 纯MWORKS Sysplorer内完成
   - 无需Gazebo
   - 无需外部规划器
   - 7118个障碍体实时规划
```

**Callout 2 (middle-right)**:
```
A*搜索参数:
━━━━━━━━━━
栅格分辨率: 0.5m
搜索空间: 100×100×10
启发函数: Euclidean
```

**Callout 3 (bottom-right)**:
```
min-snap优化:
━━━━━━━━━━━━
多项式阶数: 7
优化目标: 最小化snap
约束: 速度≤3m/s, 加速度≤5m/s²
```

**Comparison note (bottom, outside MWORKS box)**:
- Small comparison table:
```
┌─────────────────┬──────────┬─────────────┐
│ 规划组件        │ 运行环境 │ 本页说明    │
├─────────────────┼──────────┼─────────────┤
│ OpenBlocks      │ MWORKS   │ ✅ 本图     │
│ Diff-Planner    │ Gazebo   │ ❌ P47页    │
│ FUEL            │ Gazebo   │ ❌ P48页    │
└─────────────────┴──────────┴─────────────┘
```

**Visual elements**:
- Waypoints: small colored dots along A* path
- Smooth trajectory: continuous curve overlaid on waypoints
- Obstacles: gray cubic blocks in 3D space

**Connections**:
- Thick solid arrows: main pipeline flow
- Thin dashed arrows: parameter/configuration inputs
- Blue highlight: trajectory output

**Color scheme**:
- MWORKS boundary box: light blue dashed border #3498DB
- Obstacle map: gray #95A5A6
- A* search: pale green #A9DFBF
- min-snap: pale orange #F8C471
- Trajectory output: vibrant blue #3498DB
- Controller: deep blue #2E86C1
- Annotation boxes: light yellow #FFF9E6 with green checkmarks
- Comparison table: white with light gray borders

**Typography**:
- Stage titles: Arial Bold, 13pt
- Process labels: Arial, 11pt
- Mathematical formulas: Computer Modern, 11pt
- Parameters: Consolas monospace, 9pt
- Annotations: Arial, 10pt

**Negative constraints**:
- No photo-realistic obstacle environment rendering
- No curved pipeline arrows
- No gradient fills on stage boxes
- No 3D perspective depth cueing on obstacles
- No decorative planning path animations

---

## PPT-13: MWORKS Real-Time Outer Loop with WSL2 Data Flow (P35页)

**Figure Subject**: MWORKS实时外环与WSL2数据流：200Hz控制器+PX4内环+Gazebo仿真

**Diagram type**: System architecture with data flow frequencies (A类：架构/流程图)

**Layout**: 16:9 landscape, vertical two-tier architecture

**Mandatory nodes and visual elements**:

**Top tier — Windows host (MWORKS real-time environment)**:
- Large bounding box labeled: "Windows主机 (MWORKS实时环境)"
- Components inside:

  **Sysblock Controller**:
  - Box: "Sysblock控制器 (sim_mode=2)"
  - Real-time badge: "200 Hz"
  - Output port: "AttitudeThrustCommand"
  - Structure:
    - Position control (outer loop)
    - Velocity control (mid loop)
    - Attitude setpoint generation

  **UDP non-blocking send**:
  - Communication node: "UDP非阻塞发送"
  - Properties:
    - 单向（one-way）
    - 无等待（no blocking）
    - 零拷贝（zero-copy）
  - Buffer icon showing datagram queue

  **Network interface**:
  - Virtual adapter: "vEthernet (WSL)"
  - IP addressing: 172.x.x.x

**Middle — Network layer**:
- Thick bidirectional arrow between Windows and WSL2
- Uplink (Windows → WSL2):
  - Label: "AttitudeThrustCommand (200Hz)"
  - Packet structure: quaternion [w,x,y,z] + thrust (scalar)
- Downlink (WSL2 → Windows):
  - Label: "StateFrame (100Hz)"
  - Packet structure: position [x,y,z] + velocity [vx,vy,vz] + attitude [quaternion]

**Bottom tier — WSL2 Ubuntu 20.04 (ROS1 Noetic)**:
- Large bounding box labeled: "WSL2 Ubuntu 20.04 (ROS1 Noetic)"
- Components inside (top to bottom):

  **ROS Bridge Node**:
  - Box: "ROS Bridge节点 (C++)"
  - Function: UDP接收 + 解析
  - Output: quaternion + thrust

  **MAVROS**:
  - Box: "MAVROS"
  - ROS topic: `/mavros/setpoint_attitude/thrust`
  - Communication: MAVLink protocol
  - Frequency: 200Hz publish

  **PX4 SITL**:
  - Box: "PX4 SITL (姿态率控制 + failsafe)"
  - Inner loop control:
    - Attitude tracking
    - Body rate control
    - Motor mixing
  - Failsafe logic:
    - Geofence
    - RC loss handling
    - Battery monitoring
  - Output: Motor PWM (4 channels)

  **Gazebo Physics Engine**:
  - Box: "Gazebo物理引擎"
  - Simulation frequency: 1000Hz
  - Physics: ODE solver
  - Sensor simulation:
    - IMU (200Hz)
    - GPS (5Hz)
    - Optical flow (30Hz)
  - Upward arrow: State feedback
    - Position (from ground truth)
    - Velocity (numerical derivative)
    - Attitude (from IMU)

**Feedback path** (bottom to top):
- Dashed arrow from Gazebo → PX4 → MAVROS → ROS Bridge → UDP → MWORKS
- Label: "状态反馈 (100Hz)"

**Frequency annotation table** (right side):
```
┌─────────────────┬──────────┐
│ 层级            │ 频率     │
├─────────────────┼──────────┤
│ MWORKS外环      │ 200 Hz   │
│ PX4内环         │ 250 Hz   │
│ Gazebo物理      │ 1000 Hz  │
│ 状态反馈        │ 100 Hz   │
└─────────────────┴──────────┘
```

**Key annotations**:

**Annotation 1 (top-right)**:
```
✅ 外环（MWORKS）:
   - 位置控制
   - 速度控制
   - 姿态期望生成
```

**Annotation 2 (middle-right)**:
```
✅ 内环（PX4）:
   - 姿态率控制
   - 电机分配
   - failsafe保护
```

**Annotation 3 (bottom-left)**:
```
通信频率:
MWORKS → PX4: 200Hz
PX4 → MWORKS: 100Hz
```

**Connections**:
- Thick solid arrows: command data flow (downward)
- Dashed arrows: state feedback (upward)
- Network arrows: bidirectional with frequency labels

**Color scheme**:
- Windows tier: pale blue #D6EAF8
- WSL2 tier: pale green #A9DFBF
- MWORKS controller: vibrant blue #3498DB
- ROS Bridge: orange #F8C471
- MAVROS: light purple #D7BDE2
- PX4 SITL: deep blue #2E86C1
- Gazebo: gray #95A5A6
- Network layer: white with blue arrows
- Frequency badges: yellow circles #F8B400 with bold numbers
- Annotation boxes: light yellow #FFF9E6

**Typography**:
- Tier labels: Arial Bold, 14pt
- Component names: Arial Bold, 12pt
- Frequency labels: Arial Bold, 11pt
- Process details: Arial, 10pt
- Annotations: Arial, 10pt
- Table: Consolas monospace, 9pt

**Negative constraints**:
- No photo-realistic component screenshots
- No decorative network cable imagery
- No gradient backgrounds on tiers
- Arrows must be straight orthogonal/45°, no curves
- No drop shadows on component boxes

---

## PPT-14: C99 Code Package Structure and Deployment Paths (P40页)

**Figure Subject**: C99代码包结构与三条部署路径

**Diagram type**: File structure tree with deployment flowchart (A类：架构/流程图)

**Layout**: 16:9 landscape, left 40% file tree, right 60% deployment paths

**Mandatory nodes and visual elements**:

**Left section — C99 code package structure**:
- Root folder icon: `px4ctrl_controller/`
- File tree (indented):
```
px4ctrl_controller/
├── px4ctrl_controller.c        (控制器核心)
│   └── controller_step()       (单步执行 <50μs)
│
├── px4ctrl_controller.h        (接口头文件)
│   ├── ControllerState         (状态结构体)
│   ├── ControllerInput         (输入结构体)
│   └── ControllerOutput        (输出结构体)
│
├── px4ctrl_controller_data.c   (参数数据)
│   └── 常量初始化（Kp, Ki, Kd等）
│
├── px4ctrl_controller_types.h  (类型定义)
│   ├── struct ControllerState
│   ├── struct ControllerInput
│   └── struct ControllerOutput
│
└── CMakeLists.txt              (构建脚本)
    ├── 静态库: libpx4ctrl.a
    └── 共享库: libpx4ctrl.so
```

**File size annotations**:
- .c files: ~12 KB each
- .h files: ~3 KB each
- .so library: ~48 KB

**Right section — Three deployment paths**:

**Path 1 — CFunction SIL (MWORKS内验证)**:
```
C99代码包
    ↓
编译为共享库 (.so / .dll)
    ↓
MWORKS CFunction模块加载
    ↓
Sysblock SIL测试模型
    ├── 原生控制器 (参考)
    └── CFunction (C99代码)
    ↓
逐采样点对比
    ↓
RMSE验证: 1.148×10⁻¹³ m
```

**Path 2 — ROS Bridge节点 (Gazebo运行时)**:
```
C99代码包
    ↓
集成到ROS节点工程
    ├── CMakeLists.txt (ROS)
    ├── package.xml
    └── px4ctrl_node.cpp (wrapper)
    ↓
catkin build 编译
    ↓
ROS可执行节点
    ├── 订阅: /mavros/state
    ├── 调用: controller_step()
    └── 发布: /mavros/setpoint_attitude
    ↓
Gazebo闭环运行
```

**Path 3 — 独立嵌入式编译 (真机部署)**:
```
C99代码包
    ↓
ARM交叉编译
    ├── arm-none-eabi-gcc
    ├── 优化等级: -O2
    └── 浮点: -mfpu=fpv5-sp-d16
    ↓
嵌入式二进制
    ├── Flash大小: ~20 KB
    └── RAM占用: ~8 KB
    ↓
烧录到飞控板
    ├── PX4固件集成
    └── 自定义控制模块
    ↓
真机飞行测试
```

**Deployment path comparison table** (bottom):
```
┌────────────┬──────────┬──────────┬──────────────┬──────────┐
│ 部署路径   │ 编译器   │ 运行环境 │ 验证目标     │ 实时性   │
├────────────┼──────────┼──────────┼──────────────┼──────────┤
│ SIL验证    │ GCC/MSVC │ MWORKS   │ 算法一致性   │ 非实时   │
│ ROS Bridge │ GCC      │ WSL2/ROS │ 闭环性能     │ 软实时   │
│ 嵌入式     │ ARM-GCC  │ 飞控板   │ 真机飞行     │ 硬实时   │
└────────────┴──────────┴──────────┴──────────────┴──────────┘
```

**Key features annotation** (top-right):
```
✅ ISO C99标准
   - 无外部依赖
   - 仅依赖标准数学库 (math.h)

✅ 双输出格式
   - 静态库 (.a) 用于嵌入式
   - 共享库 (.so/.dll) 用于SIL/ROS

✅ 跨平台兼容
   - Windows (MSVC)
   - Linux (GCC)
   - ARM (arm-none-eabi-gcc)
```

**Connections**:
- Solid arrows: main deployment flow
- Dashed arrows: build/compile processes
- Branch points: from C99 package to three paths

**Color scheme**:
- File tree: pale blue #D6EAF8 with folder/file icons
- Path 1 (SIL): pale green #A9DFBF
- Path 2 (ROS): pale orange #F8C471
- Path 3 (Embedded): pale purple #D7BDE2
- Comparison table: white with light gray borders
- Feature annotation: light yellow #FFF9E6 with green checkmarks

**Typography**:
- File tree: Consolas monospace, 10pt
- Path labels: Arial Bold, 12pt
- Process steps: Arial, 10pt
- Table: Consolas monospace, 9pt
- Annotations: Arial, 10pt

**Negative constraints**:
- No actual code screenshots
- No photo-realistic file explorer windows
- No decorative compiler logos
- Arrows must be orthogonal, no curved connectors
- No gradient fills on path boxes

---

## PPT-15: Gazebo State Feedback Pathway Design (P43页)

**Figure Subject**: Gazebo状态反馈通路设计：FAST-LIO(XY) + 激光定高(Z) 两路互补

**Diagram type**: System architecture with sensor fusion diagram (A类：架构/流程图)

**Layout**: 16:9 landscape, top-to-bottom sensor fusion pipeline

**Mandatory nodes and visual elements**:

**Top layer — Sensor sources in Gazebo**:
- Bounding box: "Gazebo物理仿真环境"
- Two parallel sensor branches:

  **Branch 1 (XY positioning)**:
  - Sensor: "MID360 LiDAR"
    - Icon: rotating LiDAR scanner
    - Spec: 20Hz点云, ~100k点/帧
  - Sensor: "IMU"
    - Icon: IMU chip
    - Spec: 200Hz加速度+角速度

  **Branch 2 (Z positioning)**:
  - Sensor: "激光定高传感器"
    - Icon: downward laser beam
    - Spec: 50Hz高度测量, 0-30m量程

**Second layer — Sensor fusion (XY branch)**:
- Algorithm box: "FAST-LIO (增量EKF + ikd-Tree)"
- Process details:
  - Point cloud preprocessing
  - Incremental insertion to ikd-Tree
  - IMU pre-integration
  - Tightly-coupled EKF update
- Output: XY position + attitude (20Hz)
- Performance annotation:
  - 定位精度: <0.1m
  - 建图范围: 50m × 50m
  - 计算延迟: <50ms

**Third layer — State estimation fusion**:
- Central fusion node: "PX4 EKF2状态估计器 (100Hz)"
- Inputs:
  - XY位置 ← FAST-LIO (20Hz)
  - Z高度 ← 激光定高传感器 (50Hz)
  - 姿态 ← FAST-LIO + IMU (200Hz)
- Fusion algorithm:
  - Extended Kalman Filter
  - Multi-rate sensor fusion
  - Outlier rejection
- Output: Fused state estimate
  - Position: [x, y, z]
  - Velocity: [vx, vy, vz]
  - Attitude: quaternion [w,x,y,z]

**Fourth layer — State broadcast**:
- Communication box: "MAVROS (100Hz状态广播)"
- ROS topics:
  - `/mavros/local_position/pose`
  - `/mavros/local_position/velocity`
  - `/mavros/imu/data`

**Fifth layer — Controller input**:
- Controller box: "MWORKS控制器 (200Hz位置/速度控制)"
- Note: "插值补偿频率差 (100Hz → 200Hz)"

**Right side — Design rationale**:

**XY定位设计 (FAST-LIO)**:
```
✅ 激光雷达+IMU紧耦合
   - 互补传感器特性
   - 高频IMU预测 (200Hz)
   - 点云低频修正 (20Hz)

✅ 无GPS环境定位
   - 室内/GPS拒止环境
   - 相对定位精度高
   - 在线构建环境地图
```

**Z轴定位设计 (激光定高)**:
```
✅ 独立Z轴反馈
   - 避免FAST-LIO Z轴漂移
   - 直接测距，精度高
   - 低延迟 (50Hz高频)

✅ 两路互补设计
   - XY: FAST-LIO
   - Z: 激光定高
   - 三轴高质量反馈
```

**Key benefits box** (bottom-right):
```
融合频率: PX4 EKF2 100Hz
控制器输入: MWORKS 200Hz (插值)
XY定位精度: <0.1m (FAST-LIO)
Z定位精度: <0.05m (激光定高)
```

**Connections**:
- Solid arrows: sensor data flow
- Dashed arrows: feedback/correction paths
- Thick arrows: fused state output

**Color scheme**:
- Gazebo environment: pale gray #ECF0F1
- XY branch: pale blue #AED6F1
- Z branch: pale green #A9DFBF
- FAST-LIO algorithm: deep blue #2E86C1
- PX4 EKF2: orange #F8C471
- MAVROS: light purple #D7BDE2
- MWORKS controller: vibrant blue #3498DB
- Design rationale boxes: light yellow #FFF9E6 with green checkmarks

**Typography**:
- Layer titles: Arial Bold, 13pt
- Sensor specs: Consolas monospace, 9pt
- Algorithm details: Arial, 10pt
- Annotations: Arial, 10pt
- Rationale text: Arial, 9pt

**Negative constraints**:
- No photo-realistic sensor hardware images
- No actual RViz point cloud screenshots
- No decorative sensor icons
- Arrows must be straight, no curved connectors
- No gradient fills on fusion boxes

---

## PPT-16: Diff-Planner Differential Flatness Trajectory Optimization (P47页)

**Figure Subject**: Diff-Planner微分平坦轨迹优化：可微距离场+梯度下降实时重规划

**Diagram type**: Algorithm architecture with mathematical formulation (A类：架构/流程图)

**Layout**: 16:9 landscape, top-to-bottom optimization pipeline

**Mandatory nodes and visual elements**:

**Top layer — Input: FAST-LIO point cloud map**:
- Box: "FAST-LIO点云地图（实时更新）"
- Visualization: sparse point cloud icon
- Update frequency: 20Hz
- Map size: 50m × 50m × 5m

**Second layer — Distance field construction**:
- Process box: "可微距离场构建 (ESDF)"
- Algorithm details:
  - Euclidean Signed Distance Field
  - 分辨率: 0.2m
  - 更新频率: 10Hz
- Mathematical representation:
  ```
  d(x) = min ||x - x_obs||
         x_obs∈Obstacles
  
  ∇d(x) = (x - x_nearest) / ||x - x_nearest||
  ```
- Key property box:
  ```
  ✅ 可微特性:
     - 距离梯度可计算
     - 梯度回传到轨迹参数
     - 加速收敛速度
  ```

**Third layer — Trajectory parameterization**:
- Box: "轨迹参数化 (B样条/多项式)"
- B-spline curve visualization
- Representation:
  ```
  r(t) = Σ Pᵢ · Bᵢ(t)    (7阶多项式)
       i=1
  
  where:
    Pᵢ: 控制点 (优化变量)
    Bᵢ(t): B样条基函数
  ```

**Fourth layer — Optimization objective**:
- Central box: "优化目标函数"
- Mathematical formulation (large, prominent):
  ```
  min J = ∫₀ᵀ (||snap||² + λ_obs·C_obs + λ_time·1) dt
  
  where:
    snap = d⁴r/dt⁴           (平滑性)
    C_obs = max(0, d_safe - d(r))²  (障碍惩罚)
    T: 轨迹总时间 (时间最优)
  ```

**Constraints box** (right side of optimization):
```
动力学可行性约束:
━━━━━━━━━━━━━━━━
||v(t)|| ≤ v_max = 3.0 m/s
||a(t)|| ≤ a_max = 5.0 m/s²

碰撞避免约束:
━━━━━━━━━━━━━━━━
d(r(t)) ≥ d_safe = 0.5 m

时间约束:
━━━━━━━━━━━━━━━━
T_min ≤ T ≤ T_max
```

**Fifth layer — Gradient descent solver**:
- Solver box: "梯度下降求解器"
- Algorithm: L-BFGS or Adam optimizer
- Convergence criterion: ||∇J|| < ε
- Performance metrics:
  - 求解时间: <10ms
  - 优化频率: 100Hz
  - 迭代次数: 10-20次

**Sixth layer — Output**:
- Output bundle:
  - Optimized trajectory: r*(t)
  - Velocity: v*(t) = dr*/dt
  - Acceleration: a*(t) = d²r*/dt²
- Arrow to: "MWORKS控制器跟踪"

**Right side — Key advantages**:

**可微框架优势**:
```
✅ 梯度信息直接回传
   - 障碍约束 → 轨迹参数
   - 避免盲目搜索
   - 收敛速度快1个数量级

✅ 实时重规划
   - 求解时间 <10ms
   - 在线调整轨迹
   - 遇障碍立即响应

✅ 动力学保证
   - 速度/加速度约束
   - snap最小化 (平滑)
   - 可执行性验证
```

**Bottom annotation — Gazebo/ROS component label**:
```
⚠ 注意: Diff-Planner是Gazebo/ROS组件
         (非MWORKS，运行于WSL2/ROS环境)
```

**Visual elements**:
- Distance field: gradient heatmap showing obstacle proximity
- B-spline curve: smooth trajectory curve
- Gradient vectors: small arrows showing ∇d(x) direction

**Connections**:
- Solid arrows: main pipeline flow
- Dashed arrows: gradient backpropagation
- Red arrows: constraint violation feedback

**Color scheme**:
- FAST-LIO input: pale blue #AED6F1
- ESDF construction: pale green #A9DFBF
- Trajectory parameterization: pale orange #F8C471
- Optimization objective: vibrant blue #3498DB
- Solver: deep blue #2E86C1
- Output: purple #D7BDE2
- Advantages box: light yellow #FFF9E6 with green checkmarks
- Warning box: pale red #F5B7B1 with orange border

**Typography**:
- Layer titles: Arial Bold, 13pt
- Mathematical formulas: Computer Modern (LaTeX), 11pt
- Algorithm details: Arial, 10pt
- Constraints: Consolas monospace, 9pt
- Annotations: Arial, 10pt

**Negative constraints**:
- No photo-realistic RViz visualizations
- No actual trajectory animation frames
- No decorative optimization convergence plots
- Arrows must be straight, no curved connectors
- No gradient fills on major boxes

---

## PPT-17: FUEL Autonomous Exploration Architecture (P48页)

**Figure Subject**: FUEL自主探索架构：分层决策+信息增益驱动

**Diagram type**: Hierarchical architecture diagram (A类：架构/流程图)

**Layout**: 16:9 landscape, two-tier architecture (global + local)

**Mandatory nodes and visual elements**:

**Input layer (top)**:
- Box: "FAST-LIO点云地图（实时更新）"
- Map representation: occupancy grid
  - 已知区域: 白色
  - 未知区域: 灰色
  - 障碍物: 黑色

**Global layer — Frontier detection and evaluation**:
- Large bounding box: "全局层：Frontier检测与评估"
- Three stages inside:

  **Stage 1 — Frontier extraction**:
  - Process box: "Frontier提取（未知边界）"
  - Algorithm: 已知/未知栅格边界检测
  - Output: Frontier候选点集合 (F₁, F₂, ..., Fₙ)
  - Visualization: colored boundary points on map

  **Stage 2 — Information gain evaluation**:
  - Process box: "信息增益评估"
  - Mathematical formula:
    ```
    I(Fᵢ) = V_unknown(Fᵢ) / (d(Fᵢ) + ε)
    
    where:
      V_unknown: 可观测未知体积 (m³)
      d(Fᵢ): 当前位置到Fᵢ的距离 (m)
      ε: 正则化常数 (0.1)
    ```
  - Evaluation for each frontier:
    - Ray casting to compute visible volume
    - Path length estimation
    - Information gain scoring

  **Stage 3 — Target selection**:
  - Process box: "目标选择"
  - Decision rule:
    ```
    F* = argmax I(Fᵢ)
         Fᵢ∈Frontiers
    ```
  - Output: Next exploration target F*

**Arrow down — Target output**:
- Thick arrow labeled: "下一个探索目标 F*"

**Local layer — Safe path planning**:
- Large bounding box: "局部层：安全路径规划"
- Three stages inside:

  **Stage 1 — A* search (coarse path)**:
  - Process box: "A*搜索（粗路径）"
  - Grid resolution: 0.2m
  - Cost function: distance + obstacle penalty
  - Output: Waypoint sequence

  **Stage 2 — B-spline trajectory optimization**:
  - Process box: "B样条轨迹优化"
  - Optimization objective:
    ```
    min J = ∫ (||snap||² + λ·C_collision) dt
    ```
  - Collision penalty: soft constraint
  - Output: Smooth trajectory

  **Stage 3 — Dynamics feasibility verification**:
  - Process box: "动力学可行性验证"
  - Constraints checked:
    - ||v(t)|| ≤ v_max
    - ||a(t)|| ≤ a_max
  - Output: Feasible safe trajectory

**Output layer (bottom)**:
- Box: "MWORKS控制器跟踪"
- Arrow from local layer to controller

**Right side — Key characteristics**:

**分层决策优势**:
```
✅ 全局+局部解耦
   - 全局层: 决策去哪里
   - 局部层: 规划怎么去
   - 互不干扰，职责清晰

✅ 信息增益驱动
   - 自主决策探索方向
   - 最大化信息收集
   - 无需预设路径

✅ 探索效率接近最优
   - 贪心策略+路径优化
   - 避免重复探索
   - 快速覆盖未知区域
```

**Exploration metrics box** (bottom-right):
```
典型探索性能:
━━━━━━━━━━━━━━
探索空间: 50m×50m×5m
探索时长: 180s
覆盖率: 95%
Frontier总数: 28个
平均信息增益: 11.3 m³
```

**Bottom annotation — Gazebo/ROS component label**:
```
⚠ 注意: FUEL是Gazebo/ROS组件
         (非MWORKS，运行于WSL2/ROS环境)
```

**Visual elements**:
- Frontier points: colored markers on occupancy grid
- Information gain heatmap: gradient coloring for I(Fᵢ)
- Selected target: highlighted with star icon
- Planned path: smooth curve overlaid on grid

**Connections**:
- Solid arrows: main decision/planning flow
- Dashed arrows: evaluation feedback
- Thick arrows: target output and trajectory output

**Color scheme**:
- FAST-LIO input: pale blue #AED6F1
- Global layer: pale green #A9DFBF
- Local layer: pale orange #F8C471
- Frontier extraction: light purple #D7BDE2
- Information gain: gradient yellow-to-red
- Path planning: vibrant blue #3498DB
- Controller output: deep blue #2E86C1
- Characteristics box: light yellow #FFF9E6 with green checkmarks
- Metrics box: light cream #FFFACD
- Warning box: pale red #F5B7B1 with orange border

**Typography**:
- Layer titles: Arial Bold, 14pt
- Stage labels: Arial Bold, 12pt
- Mathematical formulas: Computer Modern, 11pt
- Process details: Arial, 10pt
- Annotations: Arial, 10pt
- Metrics: Consolas monospace, 10pt

**Negative constraints**:
- No photo-realistic exploration screenshots
- No actual RViz frontier visualization
- No decorative robot/drone imagery
- Arrows must be orthogonal, no curved connectors
- No gradient fills on major boxes

---

## PPT-18: UE to Gazebo Mesh Export Pipeline (P49页)

**Figure Subject**: 虚幻引擎到Gazebo网格导出链路：高保真建模到优化仿真

**Diagram type**: Pipeline flowchart with technical specifications (A类：架构/流程图)

**Layout**: 16:9 landscape, left-to-right pipeline

**Mandatory nodes and visual elements**:

**Stage 1 — UE scene (high-fidelity modeling)**:
- Box: "虚幻引擎场景（高保真建模）"
- Scene elements listed:
  - 工业管道 (直径0.5-1.2m)
  - 钢结构支架 (高度8-15m)
  - 储罐与容器 (高度5-10m)
  - 狭窄通道 (宽度2-3m)
  - 动态传送带
- Visual quality:
  - 材质: PBR (物理渲染)
  - 光照: 动态全局光照
  - 细节: 高模 + 法线贴图
- Face count: ~200,000 faces

**Stage 2 — StaticMesh export**:
- Process box: "StaticMesh导出"
- Export format: FBX
- Settings:
  - Coordinate system: Z-up → Z-up
  - Unit scale: cm → m (×0.01)
  - Tangents/binormals: Yes
  - Smooth groups: Yes

**Stage 3 — Blender geometry optimization**:
- Box: "Blender几何优化"
- Three sub-processes:

  **LOD generation**:
  - Process: "LOD层级生成"
  - Levels:
    - LOD0: 100% detail (原始)
    - LOD1: 50% faces
    - LOD2: 25% faces
    - LOD3: 10% faces (远景)

  **Face reduction**:
  - Process: "面数简化"
  - Algorithm: Decimate modifier
  - Target: 200k → 50k faces (减少75%)
  - Preservation: 保持轮廓特征

  **UV optimization**:
  - Process: "UV映射优化"
  - Smart UV unwrap
  - Texture atlas packing
  - 减少纹理数量

**Stage 4 — Collada export**:
- Process box: "Collada (DAE) 导出"
- Export settings:
  - Format: COLLADA 1.4
  - Geometry: Triangulated mesh
  - Materials: Embedded textures
  - Coordinate: Z-up (Gazebo compatible)

**Stage 5 — Gazebo SDF model**:
- Box: "Gazebo SDF模型"
- Two components:

  **Visual mesh (优化)**:
  - 用途: 渲染显示
  - 面数: ~50k faces
  - 材质: Simplified materials
  - 纹理: Compressed textures (1024×1024)

  **Collision mesh (简化)**:
  - 用途: 物理碰撞
  - 几何体: 32个凸包 (convex hulls)
  - 面数: ~500 faces per hull
  - 简化比例: 原始的1%

**Stage 6 — Gazebo simulation**:
- Box: "Gazebo物理仿真 + 渲染"
- Performance metrics:
  - 加载时间: <5s
  - 渲染帧率: 60 FPS
  - 物理更新: 1000 Hz
  - 碰撞检测: <1ms per frame

**Bottom — Performance comparison table**:
```
┌──────────────┬──────────┬──────────┬──────────┐
│ 阶段         │ 面数     │ 文件大小 │ 用途     │
├──────────────┼──────────┼──────────┼──────────┤
│ UE原始       │ ~200k    │ 85 MB    │ 建模编辑 │
│ Blender优化  │ ~50k     │ 22 MB    │ 导出准备 │
│ Gazebo视觉   │ ~50k     │ 18 MB    │ 渲染显示 │
│ Gazebo碰撞   │ ~16k     │ 3 MB     │ 物理检测 │
└──────────────┴──────────┴──────────┴──────────┘
```

**Key optimization strategies** (right side):
```
✅ LOD层级生成
   - 远景低面数
   - 近景高细节
   - 自动切换

✅ 面数简化
   - 保持轮廓特征
   - 减少75%面数
   - 视觉质量可接受

✅ 碰撞体分离
   - 视觉网格: 细节
   - 碰撞网格: 简化
   - 物理性能提升10×
```

**Connections**:
- Thick solid arrows: main pipeline flow
- Dashed arrows: optimization branches
- Blue arrows: data export/import

**Color scheme**:
- UE stage: pale purple #D7BDE2
- Export stages: pale blue #AED6F1
- Blender optimization: pale green #A9DFBF
- Gazebo stages: pale orange #F8C471
- Performance table: white with light gray borders
- Optimization strategies: light yellow #FFF9E6 with green checkmarks

**Typography**:
- Stage titles: Arial Bold, 13pt
- Process details: Arial, 10pt
- Settings: Consolas monospace, 9pt
- Table: Consolas monospace, 9pt
- Annotations: Arial, 10pt

**Negative constraints**:
- No actual UE/Blender/Gazebo screenshots
- No photo-realistic scene renderings
- No decorative 3D software logos
- Arrows must be straight, no curved connectors
- No gradient fills on stage boxes

---

## PPT-19: MWORKS Full-Chain Capability Map (P50页)

**Figure Subject**: MWORKS全链路能力地图：从建模到部署的完整能力展示

**Diagram type**: Hierarchical capability map with metrics (A类：架构/流程图)

**Layout**: 16:9 landscape, vertical capability stack with right-side metrics

**Mandatory nodes and visual elements**:

**Large bounding box encompassing all capabilities**:
- Title at top: "MoSim 全链路能力地图"
- Subtitle: "基于MWORKS平台的UAV开发全流程"

**Capability Layer 1 — Modeling (建模能力)**:
- Large box: "建模能力"
- Sub-capabilities (4 items, horizontal layout):
  1. **Blender机械建模**
     - 自测参数（1.0kg质量）
     - 传感器安装坐标标定
  2. **MultiBody六自由度动力学**
     - 牛顿-欧拉方程
     - 气动模型 + 执行器响应
  3. **Sysblock图形化控制器**
     - 48个控制器（7族算法）
     - 零代码图形化建模
  4. **统一接口设计**
     - 四接口共享Plant
     - Adapter坐标转换层

**Arrow down labeled: "验证流程"**

**Capability Layer 2 — Verification (验证能力)**:
- Large box: "验证能力"
- Sub-capabilities (5 items):
  1. **ClimbPath 50s标准筛查**
     - 38/48通过（79%）
  2. **七场景深度对比**
     - hover/figure8/wind/motor_fault
  3. **三机编队与ECBF安全**
     - 编队RMSE 2.2855e-13m
  4. **OpenBlocks自主避障**
     - 7118障碍体实时规划
  5. **MoSim Studio在线验证**
     - 统一工作区界面

**Arrow down labeled: "实时验证"**

**Capability Layer 3 — Real-time (实时能力)**:
- Large box: "实时能力"
- Sub-capabilities (3 items):
  1. **MWORKS Live实时内核**
     - 硬实时调度
     - 确定性执行
  2. **RT0验证**
     - 200.02Hz采样
     - P99延迟5.71ms
     - 零丢包率
  3. **ROS Bridge架构**
     - MWORKS外环（200Hz）
     - PX4内环（250Hz）

**Arrow down labeled: "代码生成"**

**Capability Layer 4 — Generation (生成能力)**:
- Large box: "生成能力"
- Sub-capabilities (3 items):
  1. **Sysblock → ISO C99**
     - 自动代码生成
     - 无外部依赖
  2. **SIL验证**
     - 双精度一致性
     - RMSE 1.148e-13m
  3. **三条部署路径**
     - SIL验证
     - ROS Bridge节点
     - 独立嵌入式编译

**Arrow down labeled: "运行时部署"**

**Capability Layer 5 — Deployment (部署能力)**:
- Large box: "部署能力"
- Sub-capabilities (3 items):
  1. **Gazebo物理仿真**
     - 五类任务100%成功
     - Figure8跟踪RMSE 2.1m
  2. **FAST-LIO定位 + 激光定高**
     - XY定位精度<0.1m
     - 两路互补设计
  3. **工业场景高保真渲染**
     - UE → Gazebo mesh导出
     - 动态障碍物+狭窄通道

**Arrow down labeled: "运行时扩展"**

**Capability Layer 6 — Extension (扩展能力, Gazebo/ROS组件)**:
- Large box: "扩展能力（Gazebo/ROS组件）"
- Sub-capabilities (3 items):
  1. **Diff-Planner局部优化**
     - 可微距离场
     - <10ms实时重规划
  2. **FUEL自主探索**
     - 信息增益驱动
     - 95%覆盖率
  3. **MoSim GroundControl**
     - 地面站监控
     - 任务管理

**Right side — Comprehensive metrics summary card**:
```
━━━━━━━━━━━━━━━━━━━━━━
      MoSim 成果总结
━━━━━━━━━━━━━━━━━━━━━━

控制器总数:     48个
算法族:         7个
验证场景:       7个
编队规模:       3架UAV
障碍体数:       7118个

实时频率:       200.02 Hz
P99延迟:        5.71 ms
丢包率:         0%

SIL精度:        1.148×10⁻¹³ m
编队RMSE:       2.2855×10⁻¹³ m

Gazebo任务:     5类
成功率:         100%
跟踪RMSE:       2.1 m

探索覆盖率:     95%
重规划延迟:     <10 ms
━━━━━━━━━━━━━━━━━━━━━━
```

**Bottom — Platform foundation label**:
```
基于国产MWORKS平台 | 从建模到部署全链路贯通 | 自主可控
```

**Connections**:
- Thick vertical arrows: main capability flow
- Horizontal lines: connecting sub-capabilities within each layer
- Dashed lines: feedback/iteration paths between layers

**Color scheme**:
- Layer 1 (Modeling): pale blue #AED6F1
- Layer 2 (Verification): pale green #A9DFBF
- Layer 3 (Real-time): pale orange #F8C471
- Layer 4 (Generation): pale purple #D7BDE2
- Layer 5 (Deployment): vibrant blue #3498DB
- Layer 6 (Extension): light gray #ECF0F1 (external components)
- Metrics card: light yellow #FFF9E6 with bold numbers
- Foundation label: deep blue #2E86C1 background with white text

**Typography**:
- Main title: Arial Bold, 18pt
- Layer titles: Arial Bold, 15pt
- Sub-capability titles: Arial Bold, 11pt
- Sub-capability details: Arial, 9pt
- Metrics card title: Arial Bold, 14pt
- Metrics numbers: Arial Bold, 13pt
- Metrics labels: Arial, 10pt
- Foundation label: Arial Bold, 12pt

**Negative constraints**:
- No photo-realistic component screenshots
- No decorative capability icons
- No gradient backgrounds on layers
- Arrows must be straight vertical/horizontal, no diagonals
- No drop shadows on capability boxes
- Keep layout clean and hierarchical

---

## 完成！14个AI生图prompt已全部编写

### 新增Prompt清单总结：

| 编号 | 页码 | 图名称 | 复杂度 | 优先级 |
|------|------|--------|--------|--------|
| PPT-06 | P07 | 四旋翼动力学模型 | 中 | 高 |
| PPT-07 | P08 | Adapter坐标转换详解 | 中 | 高 |
| PPT-08 | P08 | 统一实验框架 | 高 | 高 |
| PPT-09 | P10 | 七族算法分类树 | 高 | 高 |
| PPT-10 | P17 | px4ctrl三层架构 | 高 | 高 |
| PPT-11 | P21 | AI Agent知识注入架构 | 中 | 中 |
| PPT-12 | P29 | OpenBlocks规划链路 | 高 | 高 |
| PPT-13 | P35 | MWORKS实时外环与WSL2数据流 | 高 | 高 |
| PPT-14 | P40 | C99代码包结构与部署路径 | 中 | 高 |
| PPT-15 | P43 | Gazebo状态反馈通路设计 | 高 | 高 |
| PPT-16 | P47 | Diff-Planner微分平坦轨迹优化 | 高 | 中 |
| PPT-17 | P48 | FUEL自主探索架构 | 高 | 中 |
| PPT-18 | P49 | UE → Gazebo mesh导出链路 | 中 | 低 |
| PPT-19 | P50 | MWORKS全链路能力地图 | 高 | 高 |

**所有prompt已追加到 `prompt.md` 文件末尾！**
