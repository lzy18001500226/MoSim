## PPT-01 Full-Chain Pipeline: Sysblock → C99 → SIL → ROS Bridge → Gazebo

```text
Figure Subject:
Create a strict left-to-right pipeline diagram showing the complete MoSim chain from MWORKS Sysblock graphical modelling through ISO C99 code generation, CFunction SIL verification, a custom ROS bridge, to PX4 SITL and Gazebo runtime connection. Use a white background, flat vector graphics, black text, solid black borders, and a restrained four-color palette: pale blue for MWORKS nodes, pale green for generated-code and SIL nodes, pale orange for the ROS/runtime layer, and pale gray for evidence or display nodes.

Diagram type:
Horizontal five-stage pipeline with one evidence column at the far right.

Layout:
Use a 16:9 horizontal canvas with five equal-width vertical stages and one narrow shared evidence column. Place one primary node per stage in a single center row. Put key technical details inside each stage node as compact text, not as separate annotation boxes below. Keep all connectors strictly horizontal; no diagonal lines. Add a thin dashed gray comparison row at the very bottom labeled "等效路径（仅供参考）" with "Simulink → Embedded Coder → PX4 SITL" nodes in light gray.

Mandatory nodes:
- Stage 1 (pale blue): "MWORKS.Sysblock\n图形化控制器建模\n可生成代码"
- Stage 2 (pale green): "GenerateModelCode\nISO C99 源码\nGCC 直接编译\n无 Runtime 依赖"
- Stage 3 (pale green): "CFunction SIL 夹具\n数值一致性验证\nRMSE 1.148e-13 m"
- Stage 4 (pale orange): "自研ROS Bridge\n四接口统一接入\nATTITUDE/BODY_RATE/\nWRENCH/ROTOR"
- Stage 5 (pale orange): "Gazebo Classic\nUbuntu 20.04\nROS1 Noetic\nrosbag 录屏"
- Evidence column (pale gray): "Result.msr\nrosbag\nRViz截图\n指标CSV"
- Comparison row: light gray nodes "Simulink", "Embedded Coder", "PX4 SITL" with label "等效路径（仅供参考）"

Mandatory connections:
- Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5, all as solid black horizontal arrows.
- Stage 5 → Evidence column as one solid black arrow.
- The comparison row runs below the main pipeline with light gray arrows Simulink → Embedded Coder → PX4 SITL and a bracket connecting it to the main pipeline to indicate equivalence only.

Negative constraints:
Do not use separate annotation boxes below nodes; put all key info inside the node boxes. Do not label Stage 5 as "Figure8验证通过". Do not imply deployment to physical drone. Do not merge SIL node with Gazebo node. Do not draw comparison row as a data path. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, or floating text outside bordered nodes.
```

---

## PPT-02 Five-Layer MoSim Architecture

```text
Figure Subject:
Create a five-layer vertical stack architecture diagram for the MoSim platform showing that the first four layers are entirely inside MWORKS and only the fifth layer belongs to WSL2. Each layer is a full-width horizontal band. Use a white background, flat vector graphics, black text, and one distinct pale color per layer. Keep all connectors strictly vertical between adjacent layers; no diagonal lines.

Diagram type:
Five-layer vertical architecture stack with integrated tool labels and scope brackets.

Layout:
Use a 16:9 horizontal canvas. Stack five equal-height bands top to bottom. Put tool names and layer content inside each band as compact inline text, not as separate columns. Draw a single pale blue bracket spanning layers 1–4 on the left margin labeled "纯 MWORKS 内部" and a separate pale orange bracket spanning layer 5 labeled "WSL2 运行层". Keep all inter-layer arrows as short vertical drops centered on the band border.

Mandatory nodes (top to bottom, all content inside each band):
- Layer 1 (pale blue, "建模层"): "MWORKS.Sysplorer (MultiBody机体·6DOF) | Sysblock (控制器图形化·46路) | Syslab (数据分析·Julia)"
- Layer 2 (pale green, "生成层"): "GenerateModelCode → ISO C99 源码（无Runtime依赖）"
- Layer 3 (pale yellow, "验证层"): "CFunction SIL夹具 (RMSE 1.148e-13 m) | FormalRunner (ClimbPath 50s·30/48 通过)"
- Layer 4 (pale cyan, "MWORKS扩展层"): "三机编队 TriangleFigure8 (MWORKS Sysplorer) | OpenBlocks 轨迹 (A*冻结参数·Modelica) | ECBF 安全层 (Modelica·全MWORKS内)"
- Layer 5 (pale orange, "WSL2运行层"): "自研ROS Bridge·PX4 SITL·Gazebo Classic | FAST-LIO 感知节点 (Ubuntu 20.04/ROS1 Noetic)"

Mandatory connections:
- One centered vertical arrow from Layer 1 bottom edge to Layer 2 top edge.
- One centered vertical arrow from Layer 2 to Layer 3.
- One centered vertical arrow from Layer 3 to Layer 4.
- One centered vertical arrow from Layer 4 to Layer 5, labeled "C99导出" on the arrow.
- A thin dashed gray upward arrow from Layer 5 back to Layer 3 labeled "运行时证据回传" on the right margin, not crossing any band content.

Negative constraints:
Do not use separate left tool-label column or right annotation column; put all info inside bands. Do not place OpenBlocks, ECBF, or three-UAV formation in Layer 5. They run inside MWORKS. Do not merge layers or draw horizontal connectors within layers. Do not label WSL2 as Docker. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, crossed connectors, or floating text.
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
Use a 16:9 horizontal canvas. Draw a pale blue dashed outer boundary box labeled "纯 MWORKS Sysplorer 仿真（不含 Gazebo / ROS）" enclosing the entire diagram. Inside, place four horizontal rows top to bottom: (1) formation goal, (2) Guidance layer with ECBF sublayer (dashed pale red, optional/pluggable), (3) three parallel controller nodes, (4) three parallel Plant nodes. Add metrics text at the bottom outside MWORKS box. Keep all connectors strictly vertical within each lane.

Mandatory nodes:
- Row 1: "编队任务目标\n等边三角形 Figure8"
- Row 2: "Guidance 层\nTriangleFigure8Reference.mo\nMWORKS Modelica 模型"
- ECBF row (dashed pale red border): "ECBF 安全层（可插拔）\nThreeUavPairwiseEcbfReferenceSafetyFilter.mo\nh(x)≥0, ḣ+γh≥0"
- Row 3 (three equal nodes): "px4ctrl\nUAV1", "px4ctrl\nUAV2", "px4ctrl\nUAV3"
- Row 4 (three equal nodes): "Plant UAV1\n云纵150 MultiBody", "Plant UAV2\n云纵150 MultiBody", "Plant UAV3\n云纵150 MultiBody"
- Metrics text (below MWORKS box): "协同指标：编队RMSE = 2.2855e-13 m | 最近距离 = 2.0785 m（MIL仿真，非实飞）"

Mandatory connections:
- "编队任务目标" → "Guidance 层" by one centered vertical arrow.
- "Guidance 层" → three equal vertical drops into ECBF row (or directly into controller row if ECBF bypassed).
- ECBF row → three vertical arrows into the three controller nodes.
- Each controller → its matching Plant by one vertical arrow.
- Each Plant → metrics text by one short downward arrow.
- Thin dashed gray bidirectional lateral arrows between Plant×UAV1 ↔ Plant×UAV2 and Plant×UAV2 ↔ Plant×UAV3 labeled "协同状态采集" only.

Negative constraints:
Do not draw any Gazebo, ROS, or WSL2 node inside this diagram. Do not draw command wire from any Plant to different UAV's controller. Keep ECBF dashed border to show it's optional. Do not present formation RMSE as physical-hardware or Gazebo measurement. MWORKS boundary box must be visible and labeled. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, crossed connectors, or floating text.
```

---

## PPT-05 WSL2 Deployment Stack

```text
Figure Subject:
Create a strict 2D layered deployment diagram for the MoSim runtime environment running inside WSL2. Show the hardware host, the WSL2 boundary, and the software stack layers inside WSL2 clearly. Use a white background, flat vector graphics, black text, a dashed border for the WSL2 isolation boundary, pale blue for OS/kernel nodes, pale orange for ROS/middleware nodes, pale green for simulation nodes, and pale gray for the host hardware strip.

Diagram type:
Nested vertical layer stack inside a dashed WSL2 boundary box.

Layout:
Use a 16:9 horizontal canvas. Draw a pale gray host strip at the very bottom labeled "Windows 11 宿主机（MWORKS GUI·UE·显卡·授权）". Above it draw a large dashed-border rectangle labeled "WSL2 隔离边界". Inside the rectangle stack five horizontal bands from bottom to top. Put explanatory text inside the boundary box at top-right corner as a compact note, not as external annotation column.

Mandatory nodes (bottom to top inside WSL2 box):
- Band 1 (pale blue): "Ubuntu 20.04 LTS"
- Band 2 (pale blue): "ROS1 Noetic"
- Band 3 (pale orange): "MAVROS·rosbridge·自研ROS Bridge"
- Band 4 (pale green): "PX4 SITL·Gazebo Classic·RViz"
- Band 5 (pale green): "FAST-LIO 感知节点·MoSim ROS Bridge节点"
- Host strip (pale gray, below dashed box): "Windows 11 宿主机（MWORKS·UE·显卡·授权）"
- Inside WSL2 box at top-right corner: "WSL2 vs Docker\nMWORKS/UE 需本机 GUI 和显卡\nDocker 无法承载\nWSL2 共享宿主 GPU 和授权"

Mandatory connections:
- Short upward arrows between each adjacent band pair inside the WSL2 box, one per band boundary, centered.
- One bidirectional horizontal arrow crossing the dashed WSL2 boundary labeled "X11/WSLg 图形透传" connecting Band 4 to the host strip area.

Negative constraints:
Do not place OpenBlocks or ECBF or any formation controller inside WSL2 box. They are pure Modelica models that run inside MWORKS, not in WSL2. Do not use external right annotation column; put explanation inside boundary box. Do not label WSL2 as Docker or mention Docker inside figure. Do not imply host strip runs ROS stack. Do not show separate Docker layer. No 3D, gradients, shadows, screenshots, decorative icons, curved lines, or floating text.
```

---

## PPT-06 Quadrotor Dynamics Model

```text
Figure Subject:
Create a strict 2D quadrotor dynamics and control allocation diagram showing the X-configuration four-rotor layout, body-frame force and torque balance, control allocation matrix, and first-order motor response model. Use a white background, flat vector graphics, black text, solid black borders, pale blue for rotor discs, orange for torque vectors, blue for thrust vectors, and pale cream for equation boxes.

Diagram type:
Two-panel technical schematic with dynamics model and allocation matrix.

Layout:
Use a 16:9 horizontal canvas split into two horizontal panels. The upper panel (60% height) shows the quadrotor X-configuration with body axes, four rotors with rotation directions, arm length labels, thrust and torque vectors, and a force-torque equation box at the right. The lower panel (40% height) shows the 4×4 control allocation matrix on the left and the first-order motor response block diagram on the right. Place a parameter table at the bottom-right corner. Keep all mathematical text inside bordered boxes; no floating equations.

Mandatory nodes:
- Upper panel center: X-configuration quadrotor frame with body coordinate system labeled "X_B (Forward)", "Y_B (Left)", "Z_B (Up)".
- Four rotors with labels and rotation directions:
  - "Rotor 1\nfront-right\nCCW ⟲"
  - "Rotor 2\nrear-left\nCCW ⟲"
  - "Rotor 3\nfront-left\nCW ⟳"
  - "Rotor 4\nrear-right\nCW ⟳"
- Arm length label: "L = 0.22 m" on two arms.
- Thrust vectors: "T₁", "T₂", "T₃", "T₄" pointing upward from each rotor.
- Total thrust: "F = T₁ + T₂ + T₃ + T₄" at body center with large upward arrow.
- Torque vectors: "τₓ", "τᵧ", "τᵤ" at body center.
- Upper panel right box: "Force balance:\nm·a = F - mg - F_drag\n\nEuler dynamics:\nJ·ω̇ = τ - ω × (J·ω)\n\nwhere:\nF = [0, 0, Σ Tᵢ]ᵀ\nτ = [τₓ, τᵧ, τᵤ]ᵀ"
- Lower panel left: "Control Allocation Matrix B\n[F  ]     [1    1    1    1  ] [ω₁²]\n[τₓ]  =   [0   -Ly   0    Ly ] [ω₂²]\n[τᵧ]      [Lx   0   -Lx   0  ] [ω₃²]\n[τᵤ]      [-c   c   -c    c  ] [ω₄²]"
- Lower panel right: Motor response block diagram with boxes "ω_des" → "G(s) = 1/(τs+1)\nτ=0.02s" → "ω_act" → "T = k_T·ω²".
- Bottom-right parameter table: "Parameters\nArm length: L = 0.22 m\nLift coeff: k_T = 1.05×10⁻⁵ N/(rad/s)²\nTorque coeff: k_M = 1.8×10⁻⁷ Nm/(rad/s)²\nMotor τ: 0.02 s"

Mandatory connections:
- Dashed arrows from each rotor thrust vector to the allocation matrix.
- Solid horizontal arrows in the motor response block diagram: ω_des → G(s) → ω_act → T formula.

Negative constraints:
Do not use 3D perspective rendering. Do not add shading or gradients on the quadrotor frame. Do not use curved arrows. Do not place equations as floating text; keep them inside bordered boxes. Do not add decorative elements or photo-realistic rendering. No diagonal connectors except for the X-frame arms themselves.
```

---

## PPT-07 Adapter Coordinate Transformation

```text
Figure Subject:
Create a strict left-right split diagram showing coordinate system transformation between MWORKS ENU/FLU and PX4 NED/FRD, plus quaternion order conversion with code snippet and critical warning. Use a white background, flat vector graphics, black text, standard RGB for coordinate axes, pale blue for matrix boxes, dark background for code, and pale yellow with red border for the warning box.

Diagram type:
Left-right split: coordinate transformations on left, quaternion conversion with code on right.

Layout:
Use a 16:9 horizontal canvas split vertically into two equal halves. Left half shows two side-by-side 3D coordinate system diagrams with transformation matrix between them. Right half shows two quaternion format boxes, conversion code snippet in a dark box, and a warning box at bottom-right. Keep all elements inside bordered boxes; no floating text.

Mandatory nodes:
- Left section, upper-left: "ENU/FLU (MWORKS)\nMWORKS Modelica" with 3D axes "X_ENU: East (right)", "Y_ENU: North (forward)", "Z_ENU: Up (upward)".
- Left section, upper-right: "NED/FRD (PX4)\nPX4 Flight Controller" with 3D axes "X_NED: North (forward)", "Y_NED: East (right)", "Z_NED: Down (downward)".
- Left section, center: Transformation matrix box "R_ENU→NED = [0  1  0]\n            [1  0  0]\n            [0  0 -1]\n\nPosition: [x_NED] = R_ENU→NED · [x_ENU]\n          [y_NED]              [y_ENU]\n          [z_NED]              [z_ENU]"
- Right section, upper: "MWORKS format\nq_MWORKS = [w, x, y, z]\n           ↑ scalar first"
- Right section, below: "PX4 format\nq_PX4 = [x, y, z, w]\n        ↑ vector first"
- Right section, center: Code snippet box "// Adapter layer code\nvoid convertQuaternion(\n    const double q_mworks[4],  // [w,x,y,z]\n    double q_px4[4]            // [x,y,z,w]\n) {\n    q_px4[0] = q_mworks[1];  // x\n    q_px4[1] = q_mworks[2];  // y\n    q_px4[2] = q_mworks[3];  // z\n    q_px4[3] = q_mworks[0];  // w\n}"
- Right section, bottom-right: Warning box "⚠ Critical: Quaternion order mismatch\ncauses 180° attitude errors!\nAlways use Adapter layer conversion."

Mandatory connections:
- Bidirectional horizontal arrow between ENU/FLU and NED/FRD coordinate system boxes.
- Downward arrow from MWORKS quaternion format to code snippet box.
- Downward arrow from PX4 quaternion format to code snippet box.
- Label "Adapter" on the arrow connecting the two quaternion boxes through the code.

Negative constraints:
Do not render 3D mesh of quadrotor. Do not use curved transformation arrows. Do not place code or warnings as floating text; keep them inside bordered boxes. Do not add decorative borders around code. Keep coordinate diagrams simple with axes only; no terrain or environment. No gradients, shadows, or photo-realistic elements.
```

---

## PPT-08 Unified Experiment Framework

```text
Figure Subject:
Create a strict top-to-bottom flow diagram showing the MoSim unified experiment framework with Profile configuration, Sysblock controller core, four-interface Adapter, shared Plant, parallel fault injection panel, output collection, and unified evaluation metrics. Use a white background, flat vector graphics, black text, pale blue for config, vibrant green for controller, orange for Adapter, deep blue for Plant, red for fault injection, and purple for evaluation nodes.

Diagram type:
Top-to-bottom vertical flow with parallel fault injection branch on the right side.

Layout:
Use a 16:9 horizontal canvas. Stack five main layers vertically down the left 70% of the canvas: (1) Profile config, (2) Sysblock controller core with annotation callout, (3) Adapter with four output branches, (4) unified Plant, (5) output and evaluation. Place a fault injection panel on the right 30% parallel to layers 2-4 with dashed injection arrows into the Plant. Add two annotation boxes and one numerical summary card on the right margin below the fault panel. Keep all connectors strictly vertical in the main flow; fault injection uses horizontal dashed arrows.

Mandatory nodes:
- Layer 1 (pale blue): "Profile Config\nTrajectory type: hover/climb/figure8/spiral\nController selection: 48 options\nFault injection settings\nEvaluation metrics"
- Layer 2 (vibrant green): "Sysblock Controller Core\nPosition control block\nAttitude control block\nControl allocation block" with star-burst annotation callout "48个控制器全部改为Sysblock图形建模"
- Layer 3 (orange): "Adapter\nENU/FLU ↔ NED/FRD" with four labeled output branches "ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"
- Layer 4 (deep blue): "Sunray150 MultiBody Plant\n6-DOF dynamics\n共享Plant确保同条件对比"
- Layer 5, left box (purple): "Output Collection\nPosition trajectory\nAttitude response\nControl inputs"
- Layer 5, right box (purple): "Unified Evaluation Metrics\nRMSE (position tracking)\nResponse time\nOvershoot percentage"
- Right panel, fault injection (red): "Fault Injection\nWind disturbance: 10 m/s\nParameter mismatch: ±30%\nMotor efficiency fault: 60%"
- Right panel, annotation box 1: "✅ 核心架构:\nMoSimQuadrotorModel.Experiment.Baselines"
- Right panel, annotation box 2: "✅ 统一验证条件:\n- 同一Plant模型\n- 同一评价指标\n- 同一扰动注入"
- Right panel, numerical summary: "控制器总数: 48个\n有Runner: 46个\n缺失: 2个\n(fixed_awff_pid, pid_awff_linear_eso)"

Mandatory connections:
- Profile → Controller by one centered vertical arrow.
- Controller → Adapter by one centered vertical arrow.
- Adapter four branches merge → Plant by four short arrows into one.
- Plant → Output and Evaluation boxes by two vertical arrows.
- Fault injection panel → Plant by three horizontal dashed red arrows labeled "Wind", "Param±", "Motor".
- Output and Evaluation → annotation boxes by thin dotted feedback arrows.

Negative constraints:
Do not use photo-realistic Sysblock screenshots. Do not show detailed controller internals beyond the three named blocks. Do not use gradient fills on major boxes. Keep all main-flow connectors strictly vertical and orthogonal. Do not use curved arrows. Do not add drop shadows. No 3D, decorative icons, or floating text outside bordered nodes.
```

---

## PPT-09 Seven Algorithm Families Classification Tree

```text
Figure Subject:
Create a strict top-down hierarchical tree diagram showing 48 controllers organized into seven algorithm families: PID improvements (9), Linear/Robust (4), Sliding Mode (6), Optimal/Predictive (5), Geometric (3), Intelligent (5), and Learning/Adaptive (12). Use a white background, flat vector graphics, black text, deep blue for the root node, seven distinct pastel colors for family nodes, and white fill with colored borders for controller leaf nodes.

Diagram type:
Two-level hierarchical tree: root → seven family branches → controller leaf nodes.

Layout:
Use a 16:9 horizontal canvas. Place one large root node at top center. Draw seven branches downward to seven evenly-spaced family nodes across the width. Under each family node, arrange its controller names in a compact vertical column with small bordered boxes. Keep tree depth strictly at 2 levels (family → controller). Use straight orthogonal or angled branch lines; no curves. Annotate key controllers with small star markers or inline labels inside their boxes.

Mandatory nodes:
- Root (deep blue): "控制算法族 (48个控制器)"
- Family 1 (pale green): "PID改进族 (9个)" with controllers: "cascade_pid", "official_pid ★工程基线", "awff 前馈增强", "pid_linear_eso", "incremental_pid", "fuzzy_pid", "adaptive_pid", "pid_awff", "setpoint_prefilter_pid"
- Family 2 (pale blue): "线性/鲁棒控制 (4个)" with controllers: "lqr", "lqg", "h_infinity", "robust_pole_placement"
- Family 3 (pale orange): "滑模控制 (6个)" with controllers: "smc 传统滑模", "stc Super-Twisting", "adaptive_smc", "terminal_smc", "integral_smc", "fast_terminal_smc"
- Family 4 (pale purple): "最优/预测控制 (5个)" with controllers: "mpc 线性MPC", "nmpc 非线性MPC", "empc 经济MPC", "tube_mpc", "adaptive_mpc"
- Family 5 (pale teal): "几何控制 (3个)" with controllers: "se3_control SE(3)流形", "quaternion_control", "geometric_tracking"
- Family 6 (pale pink): "智能算法 (5个)" with controllers: "fuzzy_logic", "neural_pid", "anfis_control", "expert_system", "rule_based"
- Family 7 (pale yellow): "学习/自适应 (12个)" with controllers: "adaptive_backstepping", "mrac 模型参考自适应", "l1_adaptive", "gain_scheduling", "iterative_learning", "reinforcement_learning", "neural_network_adaptive", "online_optimization", "self_tuning", "adaptive_sliding_mode", "adaptive_robust", "dual_adaptive"

Mandatory connections:
- Root → each of the seven family nodes by thick straight branch lines radiating downward and outward.
- Each family node → its controller leaf nodes by thin straight vertical lines.
- Branch thickness: root→family (thick 2px), family→controller (thin 1px).

Negative constraints:
Do not use decorative leaf or tree imagery. Do not use gradient fills. Do not use drop shadows. Do not use curved connector lines. Do not show photo-realistic controller screenshots. Do not add floating text outside bordered nodes. Keep family icons simple geometric symbols only, not detailed illustrations. Controller boxes must align in neat vertical columns under each family, not scattered.
```

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

## PPT-11 AI Agent Knowledge Injection Architecture

```text
Figure Subject:
Create a strict five-layer vertical architecture diagram showing AI agent knowledge injection flow from MWORKS documentation through rule distillation, MCP server configuration, Syslab execution engine, to AI agent interaction. Include a right-side vertical data flow pipeline and a bottom-right benefits annotation box. Use a white background, flat vector graphics, black text, pale blue for knowledge source, pale green for distillation, orange for MCP, deep blue for Syslab, purple for AI agent, and light gray with blue arrows for data flow.

Diagram type:
Five-layer vertical architecture with side data pipeline and benefits box.

Layout:
Use a 16:9 horizontal canvas. Place five main layers vertically from top to bottom occupying the left 70% of canvas width. On the right 30%, draw a vertical data flow pipeline from top to bottom. Place a benefits annotation box at bottom-right corner. Use straight orthogonal connectors between layers; no diagonals. Each layer is a horizontal band with icons, text, and sample content boxes.

Mandatory nodes:
- Top layer (pale blue): "MWORKS官方文档" with document stack icon, listing sub-items: "API函数签名", "参数类型约束", "返回值规范", "使用示例"
- Second layer (pale green): "结构化规则蒸馏" process box with arrow labeled "人工标注 + 自动解析" → "规则库 (JSON/YAML)", show sample rule card in monospace JSON format for SimulateModel function
- Third layer (orange): "MCP服务器" with server icon, configuration panel showing "Tool registration", "Schema validation", "Execution sandbox", bidirectional connection to Syslab layer below
- Fourth layer (deep blue): "Syslab Julia引擎" large box containing components "Code interpreter", "TyPlot visualization", "Data I/O handler", with sample Julia code snippet in monospace font showing readResult and plot commands
- Fifth layer (purple): "AI Agent interaction" with chat interface mockup showing user input "分析px4ctrl与官方PID的seven场景对比" and agent response workflow numbered 1-5
- Right side vertical pipeline (light gray background): "仿真结果文件 (.mat)" → "助手调用MCP工具" → "Syslab读取数据" → "Julia计算指标" → "TyPlot生成图表" → "返回图表给用户", connected by blue arrows
- Bottom-right benefits box (light yellow): three checkmarked items "✅ 领域知识固化", "✅ 自动化分析流程", "✅ 零学习门槛", each with two bullet sub-points

Mandatory connections:
- Solid thick arrows connecting each layer top-to-bottom for main knowledge flow.
- Dashed arrows for configuration and control signals between layers.
- Bidirectional arrow between MCP layer and Syslab layer.
- Blue arrows connecting each step in right-side data pipeline vertically.

Negative constraints:
Do not use photo-realistic chat interface screenshots. Do not use actual MWORKS documentation screenshots. Do not use decorative AI or robot imagery. Do not use curved arrows; only orthogonal or 45-degree angles. Do not use gradient fills. Do not add floating text outside defined layer boxes. Code snippets must use monospace font and remain inside their containing layer boxes.
```

---


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

## PPT-12 OpenBlocks Planning Pipeline

```text
Figure Subject:
Create a strict left-to-right pipeline diagram showing OpenBlocks planning chain within MWORKS boundary: A* search and min-snap smoothing both completed inside MWORKS. Show 3D obstacle map, A* waypoint search, min-snap trajectory optimization, and controller handoff. Include three annotation callout boxes and a bottom comparison table distinguishing OpenBlocks from other planners. Use a white background, flat vector graphics, black text, light blue dashed border for MWORKS boundary, pale green for A* stage, pale orange for min-snap stage, and deep blue for controller.

Diagram type:
Four-stage left-to-right pipeline enclosed in MWORKS boundary box.

Layout:
Use a 16:9 horizontal canvas. Draw a large light blue dashed boundary box covering 80% of canvas labeled "MWORKS" at top-left. Inside this box, arrange four stages horizontally from left to right: 3D obstacle map → A* search → min-snap optimization → controller. Place three annotation callout boxes at top-right, middle-right, and bottom-right inside boundary. Below the MWORKS box, place a small comparison table showing OpenBlocks vs Diff-Planner vs FUEL. Use straight orthogonal connectors between stages; no curves.

Mandatory nodes:
- Stage 1 (gray): "3D障碍物地图" with cubic obstacle blocks shown
- Stage 2 (pale green): "A*搜索" box showing waypoint path through obstacles
- Stage 3 (pale orange): "min-snap轨迹优化" box with smooth trajectory curve overlaid on waypoints
- Stage 4 (deep blue): "控制器 (px4ctrl)" receiving optimized trajectory
- Callout 1 (top-right, light yellow): "OpenBlocks特点:" with three green checkmarks for "纯MWORKS实现", "无外部依赖", "状态机集成"
- Callout 2 (middle-right, light yellow): "A*参数:" showing "搜索空间: 100×100×10", "启发函数: Euclidean"
- Callout 3 (bottom-right, light yellow): "min-snap优化:" showing "多项式阶数: 7", "优化目标: 最小化snap", "约束: 速度≤3m/s, 加速度≤5m/s²"
- Comparison table (below MWORKS box): three-column table with headers "规划组件", "运行环境", "本页说明", showing OpenBlocks (MWORKS, ✅本图), Diff-Planner (Gazebo, ❌P47页), FUEL (Gazebo, ❌P48页)

Mandatory connections:
- Thick solid arrows connecting each stage left-to-right for main pipeline flow.
- Thin dashed arrows from callout boxes pointing to their corresponding stages.
- Blue highlighted arrow from min-snap output to controller showing trajectory handoff.

Negative constraints:
Do not use photo-realistic obstacle environment rendering. Do not use curved pipeline arrows; only straight orthogonal connectors. Do not use gradient fills on stage boxes. Do not use 3D perspective depth cueing on obstacles. Do not add decorative planning path animations. Do not show screenshots of actual MWORKS interface. Keep obstacle blocks as simple gray cubes.
```

---



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

## PPT-13 MWORKS Real-Time Outer Loop with WSL2 Data Flow

```text
Figure Subject:
Create a strict vertical two-tier architecture diagram showing MWORKS real-time outer loop with WSL2 data flow: 200Hz Sysblock controller on Windows host, UDP non-blocking communication through vEthernet WSL adapter, ROS Bridge node receiving commands, MAVROS publishing to PX4 SITL inner loop, Gazebo physics engine with sensor simulation, and 100Hz state feedback path returning upward. Include a right-side frequency annotation table and three annotation boxes. Use a white background, flat vector graphics, black text, pale blue for Windows tier, pale green for WSL2 tier, and yellow circular badges for frequency labels.

Diagram type:
Two-tier vertical architecture with bidirectional data flow and frequency annotations.

Layout:
Use a 16:9 horizontal canvas. Draw two large horizontal bounding boxes: top box for Windows host (occupying upper 40% of height), bottom box for WSL2 Ubuntu (occupying lower 50% of height). Between them, draw a thick bidirectional network arrow spanning the gap. Inside each tier, arrange components vertically with clear spacing. On the right side, place a frequency table. Place three annotation boxes: top-right, middle-right, and bottom-left. Use straight orthogonal connectors within each tier; no curves.

Mandatory nodes:
- Windows tier (pale blue box) labeled "Windows主机 (MWORKS实时环境)":
  - "Sysblock控制器 (sim_mode=2)" with yellow "200 Hz" badge, showing three-layer structure: Position control (outer), Velocity control (mid), Attitude setpoint generation
  - "UDP非阻塞发送" node showing properties: 单向, 无等待, 零拷贝, with buffer icon
  - "vEthernet (WSL)" virtual adapter with IP addressing 172.x.x.x
- Network layer (middle): thick bidirectional arrow with two labels:
  - Uplink (down arrow): "AttitudeThrustCommand (200Hz)" with packet structure: quaternion [w,x,y,z] + thrust
  - Downlink (up arrow): "StateFrame (100Hz)" with packet structure: position [x,y,z] + velocity [vx,vy,vz] + attitude [quaternion]
- WSL2 tier (pale green box) labeled "WSL2 Ubuntu 20.04 (ROS1 Noetic)":
  - "ROS Bridge节点 (C++)" with function: UDP接收 + 解析
  - "MAVROS" with ROS topic `/mavros/setpoint_attitude/thrust`, MAVLink protocol, 200Hz publish
  - "PX4 SITL (姿态率控制 + failsafe)" showing inner loop: Attitude tracking, Body rate control, Motor mixing; failsafe logic: Geofence, RC loss, Battery monitoring; output: Motor PWM (4 channels)
  - "Gazebo物理引擎" with simulation frequency 1000Hz, ODE solver, sensor simulation: IMU (200Hz), GPS (5Hz), Optical flow (30Hz); upward arrow: State feedback (position, velocity, attitude)
- Right-side frequency table (white with borders): four rows showing MWORKS外环 (200 Hz), PX4内环 (250 Hz), Gazebo物理 (1000 Hz), 状态反馈 (100 Hz)
- Annotation 1 (top-right, light yellow): "✅ 外环（MWORKS）:" with three bullets: 位置控制, 速度控制, 姿态期望生成
- Annotation 2 (middle-right, light yellow): "✅ 内环（PX4）:" with three bullets: 姿态率控制, 电机分配, failsafe保护
- Annotation 3 (bottom-left, light yellow): "通信频率:" showing MWORKS → PX4: 200Hz, PX4 → MWORKS: 100Hz

Mandatory connections:
- Thick solid arrows for command data flow downward within WSL2 tier: ROS Bridge → MAVROS → PX4 → Gazebo.
- Dashed arrows for state feedback upward within WSL2 tier: Gazebo → PX4 → MAVROS → ROS Bridge.
- Thick bidirectional network arrow between Windows and WSL2 tiers with frequency labels on each direction.
- Thin arrows from annotation boxes pointing to their corresponding components.

Negative constraints:
Do not use photo-realistic component screenshots. Do not use curved arrows; only straight orthogonal or 45-degree connectors. Do not use gradient fills on tier boxes or component boxes. Do not add decorative network cable imagery. Do not show actual MWORKS or Gazebo interface screenshots. Keep component icons simple geometric symbols, not detailed illustrations. Frequency badges must be simple yellow circles with bold numbers, no decorative styling.
```

---


- No decorative network cable imagery
- No gradient backgrounds on tiers
- Arrows must be straight orthogonal/45°, no curves
- No drop shadows on component boxes

---

## PPT-14 C99 Code Package Structure and Deployment Paths

```text
Figure Subject:
Create a strict two-panel horizontal diagram showing C99 code package structure on the left with indented file tree, and three deployment paths on the right: CFunction SIL verification in MWORKS, ROS Bridge node for Gazebo runtime, and standalone embedded compilation for real flight. Include a bottom comparison table and top-right features annotation box. Use a white background, flat vector graphics, black text, pale blue for file tree, pale green for SIL path, pale orange for ROS path, pale purple for embedded path, and light yellow for feature annotations.

Diagram type:
Two-panel horizontal layout: file tree + three vertical deployment paths.

Layout:
Use a 16:9 horizontal canvas. Divide into left panel (40% width) showing file tree structure, and right panel (60% width) showing three vertical deployment paths side-by-side. Place a features annotation box at top-right corner. Place a comparison table spanning full width at bottom. Use straight orthogonal connectors; no curves. Each deployment path flows top-to-bottom with process boxes connected by arrows.

Mandatory nodes:
- Left panel (pale blue): "C99代码包结构" with root folder icon px4ctrl_controller/ and indented file tree in monospace font showing: px4ctrl_controller.c (控制器核心, controller_step() 单步执行 <50μs), px4ctrl_controller.h (接口头文件 with ControllerState/Input/Output), px4ctrl_controller_data.c (参数数据 with Kp,Ki,Kd初始化), px4ctrl_controller_types.h (类型定义 with struct definitions), CMakeLists.txt (构建脚本 building libpx4ctrl.a and libpx4ctrl.so). Annotate file sizes: .c files ~12 KB, .h files ~3 KB, .so library ~48 KB
- Right panel Path 1 (pale green): "CFunction SIL (MWORKS内验证)" showing flow: C99代码包 → 编译为共享库 (.so/.dll) → MWORKS CFunction模块加载 → Sysblock SIL测试模型 (原生控制器参考 + CFunction C99代码) → 逐采样点对比 → RMSE验证: 1.148×10⁻¹³ m
- Right panel Path 2 (pale orange): "ROS Bridge节点 (Gazebo运行时)" showing flow: C99代码包 → 集成到ROS节点工程 (CMakeLists.txt ROS, package.xml, px4ctrl_node.cpp wrapper) → catkin build编译 → ROS可执行节点 (订阅 /mavros/state, 调用 controller_step(), 发布 /mavros/setpoint_attitude) → Gazebo闭环运行
- Right panel Path 3 (pale purple): "独立嵌入式编译 (真机部署)" showing flow: C99代码包 → ARM交叉编译 (arm-none-eabi-gcc, 优化等级 -O2, 浮点 -mfpu=fpv5-sp-d16) → 嵌入式二进制 (Flash ~20 KB, RAM ~8 KB) → 烧录到飞控板 (PX4固件集成, 自定义控制模块) → 真机飞行测试
- Bottom comparison table (white with borders): five columns showing 部署路径, 编译器, 运行环境, 验证目标, 实时性; three rows for SIL验证 (GCC/MSVC, MWORKS, 算法一致性, 非实时), ROS Bridge (GCC, WSL2/ROS, 闭环性能, 软实时), 嵌入式 (ARM-GCC, 飞控板, 真机飞行, 硬实时)
- Top-right features box (light yellow): three checkmarked items "✅ ISO C99标准" (无外部依赖, 仅依赖math.h), "✅ 双输出格式" (静态库.a用于嵌入式, 共享库.so/.dll用于SIL/ROS), "✅ 跨平台兼容" (Windows MSVC, Linux GCC, ARM arm-none-eabi-gcc)

Mandatory connections:
- Solid arrows connecting process boxes within each deployment path vertically.
- Dashed arrows for build and compile processes within each path.
- Three branch arrows from C99 code package (left panel) pointing to the starting point of each of the three deployment paths.

Negative constraints:
Do not use actual code screenshots. Do not use photo-realistic file explorer windows. Do not use decorative compiler logos or IDE screenshots. Do not use curved arrows; only straight orthogonal connectors. Do not use gradient fills on path boxes. File tree must use monospace font and proper indentation. Keep folder and file icons simple geometric symbols, not detailed illustrations.
```

---


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

## PPT-15 Gazebo State Feedback Pathway Design

```text
Figure Subject:
Create a strict five-layer vertical architecture diagram showing Gazebo state feedback pathway: two parallel sensor branches (MID360 LiDAR+IMU for XY via FAST-LIO, laser altimeter for Z), multi-rate fusion in PX4 EKF2, MAVROS broadcasting, and MWORKS controller input with interpolation. Include right-side design rationale boxes and a bottom-right benefits box. Use a white background, flat vector graphics, black text, pale blue for XY branch, pale green for Z branch, orange for EKF2, and light yellow for rationale boxes.

Diagram type:
Five-layer vertical architecture with two parallel sensor branches merging at fusion layer.

Layout:
Use a 16:9 horizontal canvas. Place five main layers vertically from top to bottom occupying the left 65% of canvas width. On the right 35%, place two design rationale boxes (XY positioning and Z positioning) stacked vertically, plus a benefits box at bottom-right. Show two parallel sensor branches at top layer that merge at the third layer fusion node. Use straight orthogonal connectors; no curves.

Mandatory nodes:
- Top layer Gazebo environment box (pale gray) containing two sensor branches:
  - Left branch (pale blue): MID360 LiDAR icon (20Hz点云, ~100k点/帧) + IMU icon (200Hz加速度+角速度)
  - Right branch (pale green): Laser altimeter icon with downward laser beam (50Hz高度测量, 0-30m量程)
- Second layer XY branch (pale blue): "FAST-LIO (增量EKF + ikd-Tree)" showing point cloud preprocessing, incremental ikd-Tree insertion, IMU pre-integration, tightly-coupled EKF update; output XY position + attitude (20Hz) with performance: 定位精度 <0.1m, 建图范围 50m×50m, 计算延迟 <50ms
- Third layer fusion (orange): "PX4 EKF2状态估计器 (100Hz)" receiving inputs: XY位置 from FAST-LIO (20Hz), Z高度 from laser altimeter (50Hz), 姿态 from FAST-LIO+IMU (200Hz); fusion algorithm: Extended Kalman Filter, multi-rate sensor fusion, outlier rejection; output fused state: position [x,y,z], velocity [vx,vy,vz], attitude quaternion [w,x,y,z]
- Fourth layer broadcast (light purple): "MAVROS (100Hz状态广播)" publishing ROS topics: /mavros/local_position/pose, /mavros/local_position/velocity, /mavros/imu/data
- Fifth layer controller (vibrant blue): "MWORKS控制器 (200Hz位置/速度控制)" with note "插值补偿频率差 (100Hz → 200Hz)"
- Right-side XY design rationale box (light yellow): "XY定位设计 (FAST-LIO)" with two checkmarked sections: "✅ 激光雷达+IMU紧耦合" (互补传感器特性, 高频IMU预测 200Hz, 点云低频修正 20Hz), "✅ 无GPS环境定位" (室内/GPS拒止环境, 相对定位精度高, 在线构建环境地图)
- Right-side Z design rationale box (light yellow): "Z轴定位设计 (激光定高)" with two checkmarked sections: "✅ 独立Z轴反馈" (避免FAST-LIO Z轴漂移, 直接测距精度高, 低延迟 50Hz高频), "✅ 两路互补设计" (XY: FAST-LIO, Z: 激光定高, 三轴高质量反馈)
- Bottom-right benefits box (light yellow): showing 融合频率 PX4 EKF2 100Hz, 控制器输入 MWORKS 200Hz (插值), XY定位精度 <0.1m (FAST-LIO), Z定位精度 <0.05m (激光定高)

Mandatory connections:
- Solid arrows from each sensor to its processing layer (LiDAR+IMU → FAST-LIO, laser altimeter → directly to PX4 EKF2).
- Solid arrows from FAST-LIO XY output to PX4 EKF2.
- Dashed arrows for feedback and correction paths within FAST-LIO.
- Thick arrows for fused state output from PX4 EKF2 → MAVROS → MWORKS controller.

Negative constraints:
Do not use photo-realistic sensor hardware images. Do not use actual RViz point cloud screenshots. Do not use decorative sensor icons; keep them simple geometric symbols. Do not use curved arrows; only straight orthogonal connectors. Do not use gradient fills on fusion boxes. Keep algorithm boxes showing process steps as text lists, not flowcharts within boxes.
```

---



---

## PPT-16 Diff-Planner Differential Flatness Trajectory Optimization

```text
Figure Subject:
Create a strict six-layer vertical pipeline diagram showing Diff-Planner differential flatness trajectory optimization: FAST-LIO point cloud map input, ESDF distance field construction with gradient computation, B-spline trajectory parameterization, optimization objective with snap minimization and obstacle penalty, L-BFGS gradient descent solver, and optimized trajectory output. Include right-side constraints box, advantages box, and bottom warning label. Use a white background, flat vector graphics, black text, pale blue for input, pale green for ESDF, pale orange for parameterization, vibrant blue for optimization, deep blue for solver, and light yellow for advantages.

Diagram type:
Six-layer vertical optimization pipeline with mathematical formulations.

Layout:
Use a 16:9 horizontal canvas. Place six main layers vertically from top to bottom occupying the left 70% of canvas width. On the right 30%, place a constraints box at middle height and an advantages box below it. At the bottom outside main pipeline, place a warning annotation box. Use straight orthogonal connectors; no curves. Display mathematical formulas prominently in Computer Modern font.

Mandatory nodes:
- Top layer (pale blue): "FAST-LIO点云地图（实时更新）" with sparse point cloud icon, update frequency 20Hz, map size 50m×50m×5m
- Second layer (pale green): "可微距离场构建 (ESDF)" showing Euclidean Signed Distance Field with resolution 0.2m, update frequency 10Hz, mathematical representation showing d(x) = min ||x - x_obs|| and gradient ∇d(x) = (x - x_nearest) / ||x - x_nearest||; include key property box "✅ 可微特性:" listing 距离梯度可计算, 梯度回传到轨迹参数, 加速收敛速度
- Third layer (pale orange): "轨迹参数化 (B样条/多项式)" with B-spline curve visualization, representation showing r(t) = Σ Pᵢ · Bᵢ(t) for 7阶多项式, where Pᵢ are control points (optimization variables) and Bᵢ(t) are B-spline basis functions
- Fourth layer (vibrant blue): "优化目标函数" with large prominent mathematical formulation: min J = ∫₀ᵀ (||snap||² + λ_obs·C_obs + λ_time·1) dt, where snap = d⁴r/dt⁴ (smoothness), C_obs = max(0, d_safe - d(r))² (obstacle penalty), T is total trajectory time (time optimal)
- Fifth layer (deep blue): "梯度下降求解器" showing L-BFGS or Adam optimizer, convergence criterion ||∇J|| < ε, performance metrics: 求解时间 <10ms, 优化频率 100Hz, 迭代次数 10-20次
- Sixth layer (purple): Output bundle showing optimized trajectory r*(t), velocity v*(t) = dr*/dt, acceleration a*(t) = d²r*/dt², with arrow to "MWORKS控制器跟踪"
- Right-side constraints box (white with border): "动力学可行性约束:" showing ||v(t)|| ≤ v_max = 3.0 m/s, ||a(t)|| ≤ a_max = 5.0 m/s²; "碰撞避免约束:" showing d(r(t)) ≥ d_safe = 0.5 m; "时间约束:" showing T_min ≤ T ≤ T_max
- Right-side advantages box (light yellow): "可微框架优势:" with three checkmarked items "✅ 梯度信息直接回传" (障碍约束→轨迹参数, 避免盲目搜索, 收敛速度快1个数量级), "✅ 实时重规划" (求解时间 <10ms, 在线调整轨迹, 遇障碍立即响应), "✅ 动力学保证" (速度/加速度约束, snap最小化平滑, 可执行性验证)
- Bottom warning box (pale red with orange border): "⚠ 注意: Diff-Planner是Gazebo/ROS组件 (非MWORKS，运行于WSL2/ROS环境)"

Mandatory connections:
- Solid arrows connecting each layer vertically for main pipeline flow.
- Dashed arrows for gradient backpropagation from solver to parameterization layer.
- Red arrows for constraint violation feedback from optimization to constraints box.

Negative constraints:
Do not use photo-realistic RViz visualizations. Do not use actual trajectory animation frames. Do not use decorative optimization convergence plots. Do not use curved arrows; only straight orthogonal connectors. Do not use gradient fills on major boxes. Mathematical formulas must use Computer Modern font or similar serif math font, not Arial. Distance field visualization should be a simple gradient heatmap, not detailed 3D rendering.
```

---



---

## PPT-17 FUEL Autonomous Exploration Architecture

```text
Figure Subject:
Create a strict two-tier hierarchical architecture diagram showing FUEL autonomous exploration: global layer with frontier detection, information gain evaluation, and target selection; local layer with A* search, B-spline trajectory optimization, and dynamics feasibility verification. Include FAST-LIO point cloud map input at top, MWORKS controller output at bottom, right-side characteristics boxes, and bottom warning label. Use a white background, flat vector graphics, black text, pale green for global layer, pale orange for local layer, and light yellow for characteristics.

Diagram type:
Two-tier hierarchical architecture: global decision layer + local planning layer.

Layout:
Use a 16:9 horizontal canvas. Place input layer at top (10% height). Draw two large horizontal bounding boxes: global layer (30% height) and local layer (30% height) stacked vertically. Place output layer at bottom (10% height). On the right 30%, place two characteristics boxes stacked vertically, plus a warning box at bottom. Use straight orthogonal connectors; no curves. Show occupancy grid visualization with frontier points and planned path overlaid.

Mandatory nodes:
- Input layer (pale blue): "FAST-LIO点云地图（实时更新）" with occupancy grid representation showing 已知区域 (white), 未知区域 (gray), 障碍物 (black)
- Global layer box (pale green) labeled "全局层：Frontier检测与评估" containing three stages:
  - Stage 1: "Frontier提取（未知边界）" showing 已知/未知栅格边界检测, output Frontier候选点集合 (F₁, F₂, ..., Fₙ), with colored boundary points on map visualization
  - Stage 2: "信息增益评估" with mathematical formula I(Fᵢ) = V_unknown(Fᵢ) / (d(Fᵢ) + ε), where V_unknown is observable unknown volume (m³), d(Fᵢ) is distance to Fᵢ (m), ε is regularization constant (0.1); showing evaluation: ray casting for visible volume, path length estimation, information gain scoring
  - Stage 3: "目标选择" with decision rule F* = argmax I(Fᵢ), output next exploration target F*
- Thick arrow down labeled "下一个探索目标 F*"
- Local layer box (pale orange) labeled "局部层：安全路径规划" containing three stages:
  - Stage 1: "A*搜索（粗路径）" with grid resolution 0.2m, cost function distance + obstacle penalty, output waypoint sequence
  - Stage 2: "B样条轨迹优化" with optimization objective min J = ∫ (||snap||² + λ·C_collision) dt, collision penalty soft constraint, output smooth trajectory
  - Stage 3: "动力学可行性验证" checking constraints ||v(t)|| ≤ v_max and ||a(t)|| ≤ a_max, output feasible safe trajectory
- Output layer (deep blue): "MWORKS控制器跟踪" with arrow from local layer
- Right-side characteristics box 1 (light yellow): "分层决策优势:" with three checkmarked items "✅ 全局信息引导" (避免局部最优, 探索效率高, 覆盖未知区域最大化), "✅ 局部路径安全" (障碍物实时避让, 动力学约束满足, 可执行性保证), "✅ 解耦设计" (全局决策独立, 局部规划响应快, 模块化易扩展)
- Right-side metrics box 2 (light cream): "性能指标:" showing 探索效率 >85%, 地图覆盖率 >90%, 规划频率 10Hz, 平均速度 2.5m/s
- Bottom warning box (pale red with orange border): "⚠ 注意: FUEL是Gazebo/ROS组件 (非MWORKS，运行于WSL2/ROS环境)"

Mandatory connections:
- Solid arrows connecting main decision and planning flow vertically through both layers.
- Dashed arrows for evaluation feedback within global layer.
- Thick arrows for target output from global to local layer, and trajectory output from local to controller.

Negative constraints:
Do not use photo-realistic exploration screenshots. Do not use actual RViz frontier visualization. Do not use decorative robot or drone imagery. Do not use curved arrows; only straight orthogonal connectors. Do not use gradient fills on major boxes. Keep occupancy grid visualization simple with three distinct colors (white/gray/black), not complex shading. Frontier points should be simple colored markers, not detailed 3D visualizations.
```

---



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

## PPT-18 UE to Gazebo Mesh Export Pipeline

```text
Figure Subject:
Create a strict six-stage horizontal pipeline diagram showing UE to Gazebo mesh export workflow: UE high-fidelity scene (industrial pipes, steel structures, storage tanks, narrow corridors, dynamic conveyors), StaticMesh FBX export, Blender geometry optimization (LOD generation, face reduction, UV optimization), Collada DAE export, Gazebo SDF model (visual and collision meshes), and Gazebo simulation. Include bottom performance comparison table and right-side optimization strategies. Use a white background, flat vector graphics, black text, pale purple for UE stage, pale blue for export stages, pale green for Blender optimization, pale orange for Gazebo stages, and light yellow for strategies.

Diagram type:
Six-stage horizontal pipeline with optimization branches.

Layout:
Use a 16:9 horizontal canvas. Arrange six large rectangular boxes horizontally across the width (85% of canvas), each representing one pipeline stage. Stack boxes vertically where optimization substages occur (Blender stage has three substages). On the right 15%, place optimization strategies box. At bottom 15%, place performance comparison table. Use straight orthogonal connectors; no curves. Show thick solid arrows for main flow, dashed arrows for optimization branches, blue arrows for data export/import.

Mandatory nodes:
- Stage 1 (pale purple): "虚幻引擎场景（高保真建模）" with Scene elements 工业管道 (直径0.5-1.2m), 钢结构支架 (高度8-15m), 储罐与容器 (高度5-10m), 狭窄通道 (宽度2-3m), 动态传送带; Visual quality 材质 PBR (物理渲染), 光照 动态全局光照, 细节 高模 + 法线贴图; Face count ~200,000 faces
- Stage 2 (pale blue): "StaticMesh导出" with Export format FBX, Settings Coordinate system Z-up → Z-up, Unit scale cm → m (×0.01), Tangents/binormals Yes, Smooth groups Yes
- Stage 3 (pale green) labeled "Blender几何优化" containing three substages:
  - Substage A: "LOD层级生成" with Levels LOD0 100% detail (原始), LOD1 50% faces, LOD2 25% faces, LOD3 10% faces (远景)
  - Substage B: "面数简化" with Process Algorithm Decimate modifier, Target 200k → 50k faces (减少75%), Preservation 保持轮廓特征
  - Substage C: "UV映射优化" with Smart UV unwrap, Texture atlas packing, 减少纹理数量
- Stage 4 (pale blue): "Collada (DAE) 导出" with Export settings Format COLLADA 1.4, Geometry Triangulated mesh, Materials Embedded textures, Coordinate Z-up (Gazebo compatible)
- Stage 5 (pale orange) labeled "Gazebo SDF模型" containing two components:
  - Component A: "视觉网格（优化）" with 用途 渲染显示, 面数 ~50k faces, 材质 Simplified materials, 纹理 Compressed textures (1024×1024)
  - Component B: "碰撞网格（简化）" with 用途 物理碰撞, 几何体 32个凸包 (convex hulls), 面数 ~500 faces per hull, 简化比例 原始的1%
- Stage 6 (pale orange): "Gazebo物理仿真 + 渲染" with Performance metrics 加载时间 <5s, 渲染帧率 60 FPS, 物理更新 1000 Hz, 碰撞检测 <1ms per frame
- Bottom table (white with light gray borders) labeled "性能对比":
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
- Right-side strategies box (light yellow with green checkmarks): "关键优化策略:" with three items "✅ LOD层级生成" (远景低面数, 近景高细节, 自动切换), "✅ 面数简化" (保持轮廓特征, 减少75%面数, 视觉质量可接受), "✅ 碰撞体分离" (视觉网格: 细节, 碰撞网格: 简化, 物理性能提升10×)

Mandatory connections:
- Thick solid arrows connecting main pipeline flow horizontally through all six stages.
- Dashed arrows for optimization branches within Blender stage (Stage 3).
- Blue arrows for data export from UE and import to Gazebo.

Negative constraints:
Do not use actual UE/Blender/Gazebo screenshots. Do not use photo-realistic scene renderings. Do not use decorative 3D software logos or industrial scene imagery. Do not use curved connectors; only straight orthogonal arrows. Do not use gradient fills on stage boxes. Keep table simple with monospace font (Consolas 9pt) and light gray borders, not heavy borders or colored cells.
```

---


## PPT-19 MWORKS Full-Chain Capability Map

```text
Figure Subject:
Create a strict six-layer vertical capability flow diagram showing MoSim full-chain capabilities on MWORKS platform: modeling capabilities (Blender mechanical modeling, MultiBody 6DOF dynamics, Sysblock graphical controllers, unified interface design), verification capabilities (ClimbPath 50s screening, seven-scenario comparison, three-UAV formation with ECBF safety, OpenBlocks autonomous obstacle avoidance, MoSim Studio online workspace), real-time capabilities (MWORKS Live real-time kernel, RT0 verification, ROS Bridge), code generation capabilities (Sysblock to ISO C99, SIL verification, three deployment paths), deployment capabilities (Gazebo physics simulation, FAST-LIO positioning + laser altimeter, UE to Gazebo high-fidelity rendering), and extension capabilities (Diff-Planner, FUEL, MoSim GroundControl). Include bottom summary metrics table. Use a white background, flat vector graphics, black text, pale blue for modeling, pale green for verification, pale orange for real-time, vibrant blue for generation, deep purple for deployment, light yellow for extension capabilities, and white with borders for metrics table.

Diagram type:
Six-layer vertical capability flow with downward arrows between layers.

Layout:
Use a 16:9 horizontal canvas. Place six large horizontal boxes vertically from top to bottom, each representing one capability layer. Each box contains bullet points listing specific capabilities. Connect layers with thick downward arrows. At bottom 20%, place a summary metrics table spanning full width. Use straight orthogonal connectors; no curves.

Mandatory nodes:
- Layer 1 (pale blue): "建模能力" containing four items: Blender机械建模（自测参数）, MultiBody六自由度动力学, Sysblock图形化控制器（48个）, 统一接口设计（四接口共享Plant）
- Thick downward arrow
- Layer 2 (pale green): "验证能力" containing five items: ClimbPath 50s标准筛查, 七场景深度对比, 三机编队与ECBF安全, OpenBlocks自主避障（7118障碍体）, MoSim Studio在线验证工作区
- Thick downward arrow
- Layer 3 (pale orange): "实时能力" containing three items: MWORKS Live实时内核, RT0验证（200.02Hz，P99=5.71ms）, ROS Bridge（MWORKS外环 + PX4内环）
- Thick downward arrow
- Layer 4 (vibrant blue): "生成能力" containing three items: Sysblock → ISO C99, SIL验证（RMSE 1.148e-13m）, 三条部署路径（SIL/ROS/嵌入式）
- Thick downward arrow
- Layer 5 (deep purple): "部署能力" containing three items: Gazebo物理仿真（五类任务100%成功）, FAST-LIO定位（XY）+ 激光定高（Z）, 工业场景高保真渲染（UE → Gazebo）
- Thick downward arrow
- Layer 6 (light yellow): "扩展能力（Gazebo/ROS组件）" containing three items: Diff-Planner局部轨迹优化, FUEL自主探索规划, MoSim GroundControl地面站
- Bottom metrics table (white with light gray borders) labeled "数字总结" with seven rows:
  ```
  ┌──────────────────┬────────────────────┐
  │ 维度             │ 成果               │
  ├──────────────────┼────────────────────┤
  │ 控制器总数       │ 48个（7族算法）    │
  │ 验证场景         │ 7个（标称+鲁棒性） │
  │ 编队规模         │ 3架UAV             │
  │ 障碍体数         │ 7118个             │
  │ 实时频率         │ 200.02 Hz          │
  │ SIL精度          │ 1.148e-13 m        │
  │ Gazebo任务成功率 │ 100% (5/5)         │
  └──────────────────┴────────────────────┘
  ```

Mandatory connections:
- Thick solid downward arrows connecting each capability layer vertically from top to bottom.

Negative constraints:
Do not use decorative platform logos or software screenshots. Do not use photo-realistic imagery. Do not use curved arrows; only straight orthogonal downward arrows. Do not use gradient fills on capability boxes. Keep bullet points as simple text lists with dashes or arrows, not decorated icons. Table must use monospace font (Consolas 9pt) with light gray borders, not heavy borders or colored cells. Do not add decorative checkmarks or badges on capability items; keep text plain and clean.
```


