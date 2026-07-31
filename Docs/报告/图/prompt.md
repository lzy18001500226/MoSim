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
