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

## Restored Prompts for Hand-Drawn Figures Used in PPT

The two prompts below correspond to hand-drawn figures 11 and 15 that are currently used in the PPT outline. If AI regeneration is needed, use these prompts.

---

## PPT-03 (Replaces Hand-Drawn Figure 11): Four Output Interfaces with Runner and Adapter Boundary

```text
Figure Subject:
Create a strict 2D four-lane parallel architecture diagram showing the four controller output interfaces used in MoSim, each with its own Runner, unit conversion, saturation check, and allocator/inner-loop path, all converging on one shared Plant. Use a white background, flat vector graphics, black borders, and four distinct pale colors for the lanes.

Diagram type:
Four-lane parallel pipeline with shared Plant sink.

Layout:
Use a 16:9 horizontal canvas with four equal-height horizontal lanes stacked vertically. Each lane flows strictly left-to-right. Align equivalent stages (Runner, unit conversion, saturation check, allocator) vertically across all lanes. Place one shared Plant node at the far right that all four lanes feed into. Below the Plant, add one Animation output node. Use orthogonal connectors only; no diagonal lines or lane crossings.

Mandatory nodes:
- Lane 1 label: "ATTITUDE_THRUST接口"
- "姿态推力控制器核心"
- "ATTITUDE_THRUST Runner"
- "单位转换 (deg→rad, N→kg·m/s²)"
- "限幅检查"
- "姿态内环 + Allocator"
- Lane 2 label: "BODY_RATE_THRUST接口"
- "体轴角速度推力控制器核心"
- "BODY_RATE_THRUST Runner"
- "单位转换 (deg/s→rad/s)"
- "限幅检查"
- "角速度内环 + Allocator"
- Lane 3 label: "WRENCH接口"
- "力矩控制器核心"
- "WRENCH Runner"
- "单位转换 (N·m→kg·m²/s²)"
- "限幅检查"
- "控制分配器"
- Lane 4 label: "ROTOR_COMMAND接口"
- "电机指令控制器核心"
- "ROTOR_COMMAND Runner"
- "单位转换 (RPM→rad/s)"
- "限幅检查"
- "执行器模型"
- Shared right column: "统一Plant (云纵150 MultiBody)", "Animation输出"
- Annotation: "48个控制器通过四接口之一输出，共享Plant确保同条件对比"

Mandatory connections:
- Each lane: 控制器核心 → Runner → 单位转换 → 限幅检查 → allocator/inner-loop → Plant.
- All four allocator/inner-loop outputs must converge into the single shared Plant node using four equal horizontal arrows.
- Plant → Animation by one downward arrow.
- Bind annotation to the bottom of the diagram.

Negative constraints:
Do not duplicate the Plant for each lane. Do not merge lanes before reaching the Plant. Do not use diagonal connectors. Do not imply automatic interface conversion between lanes. No 3D, gradients, shadows, screenshots, curved lines, crossed lanes, or floating labels.
```

---

## PPT-13 (Replaces Hand-Drawn Figure 15): MWORKS Real-Time Outer Loop with WSL2 ROS Bridge Data Flow

```text
Figure Subject:
Create a strict 2D two-tier architecture diagram showing MWORKS real-time outer-loop controller (200Hz) on Windows host communicating via UDP with PX4 SITL inner-loop controller running in WSL2 Ubuntu, with Gazebo physics simulation and state feedback path. Use a white background, flat vector graphics, black borders, pale blue for Windows tier, pale green for WSL2 tier, and frequency badges.

Diagram type:
Two-tier system architecture with bidirectional data flow and frequency annotations.

Layout:
Use a 16:9 horizontal canvas. Draw two large horizontal bounding boxes: top box labeled "Windows 主机 (MWORKS实时环境)", bottom box labeled "WSL2 Ubuntu 20.04 (ROS1 Noetic)". Inside each box, place components in left-to-right flow. Between boxes, draw thick bidirectional network arrows with frequency labels. Use orthogonal connectors only.

Mandatory nodes:

**Windows tier (top box)**:
- "MWORKS Sysblock控制器 (sim_mode=2)"
  - Internal: "位置控制外环", "速度控制中环", "姿态期望生成"
  - Output: "AttitudeThrustCommand"
  - Frequency badge: "200 Hz"
- "UDP非阻塞发送"
  - Properties: "单向 | 无等待 | 零拷贝"
- "vEthernet (WSL) 虚拟网卡"
  - IP: "172.x.x.x"

**Network layer (between tiers)**:
- Downlink arrow (Windows → WSL2): "AttitudeThrustCommand (200Hz) | quaternion [w,x,y,z] + thrust"
- Uplink arrow (WSL2 → Windows): "StateFrame (100Hz) | position [x,y,z] + velocity + attitude"

**WSL2 tier (bottom box)**:
- "ROS Bridge节点 (C++)"
  - Function: "UDP接收 + 解析"
- "MAVROS"
  - ROS topic: "/mavros/setpoint_attitude/thrust"
  - Protocol: "MAVLink"
  - Frequency: "200Hz publish"
- "PX4 SITL"
  - Components: "姿态率控制内环 | 电机混合 | failsafe"
  - Output: "Motor PWM (4通道)"
  - Frequency badge: "250 Hz"
- "Gazebo物理引擎"
  - Physics: "ODE求解器 | 1000Hz"
  - Sensors: "IMU 200Hz | GPS 5Hz"
  - Upward arrow labeled: "状态反馈"

**Feedback path** (dashed):
- Gazebo → PX4 → MAVROS → ROS Bridge → UDP → MWORKS
- Label: "状态反馈 (100Hz)"

**Frequency table** (right side outside boxes):
```
┌─────────────┬────────┐
│ 层级        │ 频率   │
├─────────────┼────────┤
│ MWORKS外环  │ 200 Hz │
│ PX4内环     │ 250 Hz │
│ Gazebo物理  │ 1000Hz │
│ 状态反馈    │ 100 Hz │
└─────────────┴────────┘
```

Mandatory connections:
- Windows tier: MWORKS控制器 → UDP发送 → vEthernet.
- Network: vEthernet ↔ WSL2 network stack (bidirectional).
- WSL2 tier: ROS Bridge → MAVROS → PX4 → Gazebo → (feedback) → PX4 → MAVROS → ROS Bridge.
- Feedback path crosses network boundary upward back to MWORKS.

Annotations:
- "✅ 外环(MWORKS): 位置控制 | 速度控制 | 姿态期望" (top-right)
- "✅ 内环(PX4): 姿态率控制 | 电机分配 | failsafe保护" (bottom-right)

Negative constraints:
Do not place OpenBlocks, ECBF, or formation controller in WSL2 tier; they run in MWORKS Modelica. Do not use curved network arrows. Do not merge Windows and WSL2 boxes. Do not imply Docker; this is WSL2. No 3D, gradients, shadows, screenshots, decorative icons, or floating text.
```

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
## PPT-19: MWORKS Full-Chain Capability Map (P50页)


**Figure Subject**: MWORKS全链路能力地图：从建模到部署的完整能力展示
**Figure Subject**: MWORKS全链路能力地图：从建模到部署的完整能力展示


**Diagram type**: Hierarchical capability map with metrics (A类：架构/流程图)
**Diagram type**: Hierarchical capability map with metrics (A类：架构/流程图)


**Layout**: 16:9 landscape, vertical capability stack with right-side metrics
**Layout**: 16:9 landscape, vertical capability stack with right-side metrics


**Mandatory nodes and visual elements**:
**Mandatory nodes and visual elements**:


**Large bounding box encompassing all capabilities**:
**Large bounding box encompassing all capabilities**:
- Title at top: "MoSim 全链路能力地图"
- Title at top: "MoSim 全链路能力地图"
- Subtitle: "基于MWORKS平台的UAV开发全流程"
- Subtitle: "基于MWORKS平台的UAV开发全流程"


**Capability Layer 1 — Modeling (建模能力)**:
**Capability Layer 1 — Modeling (建模能力)**:
- Large box: "建模能力"
- Large box: "建模能力"
- Sub-capabilities (4 items, horizontal layout):
- Sub-capabilities (4 items, horizontal layout):
  1. **Blender机械建模**
  1. **Blender机械建模**
     - 自测参数（1.0kg质量）
     - 自测参数（1.0kg质量）
     - 传感器安装坐标标定
     - 传感器安装坐标标定
  2. **MultiBody六自由度动力学**
  2. **MultiBody六自由度动力学**
     - 牛顿-欧拉方程
     - 牛顿-欧拉方程
     - 气动模型 + 执行器响应
     - 气动模型 + 执行器响应
  3. **Sysblock图形化控制器**
  3. **Sysblock图形化控制器**
     - 48个控制器（7族算法）
     - 48个控制器（7族算法）
     - 零代码图形化建模
     - 零代码图形化建模
  4. **统一接口设计**
  4. **统一接口设计**
     - 四接口共享Plant
     - 四接口共享Plant
     - Adapter坐标转换层
     - Adapter坐标转换层


**Arrow down labeled: "验证流程"**
**Arrow down labeled: "验证流程"**


**Capability Layer 2 — Verification (验证能力)**:
**Capability Layer 2 — Verification (验证能力)**:
- Large box: "验证能力"
- Large box: "验证能力"
- Sub-capabilities (5 items):
- Sub-capabilities (5 items):
  1. **ClimbPath 50s标准筛查**
  1. **ClimbPath 50s标准筛查**
     - 38/48通过（79%）
     - 38/48通过（79%）
  2. **七场景深度对比**
  2. **七场景深度对比**
     - hover/figure8/wind/motor_fault
     - hover/figure8/wind/motor_fault
  3. **三机编队与ECBF安全**
  3. **三机编队与ECBF安全**
     - 编队RMSE 2.2855e-13m
     - 编队RMSE 2.2855e-13m
  4. **OpenBlocks自主避障**
  4. **OpenBlocks自主避障**
     - 7118障碍体实时规划
     - 7118障碍体实时规划
  5. **MoSim Studio在线验证**
  5. **MoSim Studio在线验证**
     - 统一工作区界面
     - 统一工作区界面


**Arrow down labeled: "实时验证"**
**Arrow down labeled: "实时验证"**


**Capability Layer 3 — Real-time (实时能力)**:
**Capability Layer 3 — Real-time (实时能力)**:
- Large box: "实时能力"
- Large box: "实时能力"
- Sub-capabilities (3 items):
- Sub-capabilities (3 items):
  1. **MWORKS Live实时内核**
  1. **MWORKS Live实时内核**
     - 硬实时调度
     - 硬实时调度
     - 确定性执行
     - 确定性执行
  2. **RT0验证**
  2. **RT0验证**
     - 200.02Hz采样
     - 200.02Hz采样
     - P99延迟5.71ms
     - P99延迟5.71ms
     - 零丢包率
     - 零丢包率
  3. **ROS Bridge架构**
  3. **ROS Bridge架构**
     - MWORKS外环（200Hz）
     - MWORKS外环（200Hz）
     - PX4内环（250Hz）
     - PX4内环（250Hz）


**Arrow down labeled: "代码生成"**
**Arrow down labeled: "代码生成"**


**Capability Layer 4 — Generation (生成能力)**:
**Capability Layer 4 — Generation (生成能力)**:
- Large box: "生成能力"
- Large box: "生成能力"
- Sub-capabilities (3 items):
- Sub-capabilities (3 items):
  1. **Sysblock → ISO C99**
  1. **Sysblock → ISO C99**
     - 自动代码生成
     - 自动代码生成
     - 无外部依赖
     - 无外部依赖
  2. **SIL验证**
  2. **SIL验证**
     - 双精度一致性
     - 双精度一致性
     - RMSE 1.148e-13m
     - RMSE 1.148e-13m
  3. **三条部署路径**
  3. **三条部署路径**
     - SIL验证
     - SIL验证
     - ROS Bridge节点
     - ROS Bridge节点
     - 独立嵌入式编译
     - 独立嵌入式编译


**Arrow down labeled: "运行时部署"**
**Arrow down labeled: "运行时部署"**


**Capability Layer 5 — Deployment (部署能力)**:
**Capability Layer 5 — Deployment (部署能力)**:
- Large box: "部署能力"
- Large box: "部署能力"
- Sub-capabilities (3 items):
- Sub-capabilities (3 items):
  1. **Gazebo物理仿真**
  1. **Gazebo物理仿真**
     - 五类任务100%成功
     - 五类任务100%成功
     - Figure8跟踪RMSE 2.1m
     - Figure8跟踪RMSE 2.1m
  2. **FAST-LIO定位 + 激光定高**
  2. **FAST-LIO定位 + 激光定高**
     - XY定位精度<0.1m
     - XY定位精度<0.1m
     - 两路互补设计
     - 两路互补设计
  3. **工业场景高保真渲染**
  3. **工业场景高保真渲染**
     - UE → Gazebo mesh导出
     - UE → Gazebo mesh导出
     - 动态障碍物+狭窄通道
     - 动态障碍物+狭窄通道


**Arrow down labeled: "运行时扩展"**
**Arrow down labeled: "运行时扩展"**


**Capability Layer 6 — Extension (扩展能力, Gazebo/ROS组件)**:
**Capability Layer 6 — Extension (扩展能力, Gazebo/ROS组件)**:
- Large box: "扩展能力（Gazebo/ROS组件）"
- Large box: "扩展能力（Gazebo/ROS组件）"
- Sub-capabilities (3 items):
- Sub-capabilities (3 items):
  1. **Diff-Planner局部优化**
  1. **Diff-Planner局部优化**
     - 可微距离场
     - 可微距离场
     - <10ms实时重规划
     - <10ms实时重规划
  2. **FUEL自主探索**
  2. **FUEL自主探索**
     - 信息增益驱动
     - 信息增益驱动
     - 95%覆盖率
     - 95%覆盖率
  3. **MoSim GroundControl**
  3. **MoSim GroundControl**
     - 地面站监控
     - 地面站监控
     - 任务管理
     - 任务管理


**Right side — Comprehensive metrics summary card**:
**Right side — Comprehensive metrics summary card**:
```
```
━━━━━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━━━━━
      MoSim 成果总结
      MoSim 成果总结
━━━━━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━━━━━


控制器总数:     48个
控制器总数:     48个
算法族:         7个
算法族:         7个
验证场景:       7个
验证场景:       7个
编队规模:       3架UAV
编队规模:       3架UAV
障碍体数:       7118个
障碍体数:       7118个


实时频率:       200.02 Hz
实时频率:       200.02 Hz
P99延迟:        5.71 ms
P99延迟:        5.71 ms
丢包率:         0%
丢包率:         0%


SIL精度:        1.148×10⁻¹³ m
SIL精度:        1.148×10⁻¹³ m
编队RMSE:       2.2855×10⁻¹³ m
编队RMSE:       2.2855×10⁻¹³ m


Gazebo任务:     5类
Gazebo任务:     5类
成功率:         100%
成功率:         100%
跟踪RMSE:       2.1 m
跟踪RMSE:       2.1 m


探索覆盖率:     95%
探索覆盖率:     95%
重规划延迟:     <10 ms
重规划延迟:     <10 ms
━━━━━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━━━━━
```
```


**Bottom — Platform foundation label**:
**Bottom — Platform foundation label**:
```
```
基于国产MWORKS平台 | 从建模到部署全链路贯通 | 自主可控
基于国产MWORKS平台 | 从建模到部署全链路贯通 | 自主可控
```
```


**Connections**:
**Connections**:
- Thick vertical arrows: main capability flow
- Thick vertical arrows: main capability flow
- Horizontal lines: connecting sub-capabilities within each layer
- Horizontal lines: connecting sub-capabilities within each layer
- Dashed lines: feedback/iteration paths between layers
- Dashed lines: feedback/iteration paths between layers


**Color scheme**:
**Color scheme**:
- Layer 1 (Modeling): pale blue #AED6F1
- Layer 1 (Modeling): pale blue #AED6F1
- Layer 2 (Verification): pale green #A9DFBF
- Layer 2 (Verification): pale green #A9DFBF
- Layer 3 (Real-time): pale orange #F8C471
- Layer 3 (Real-time): pale orange #F8C471
- Layer 4 (Generation): pale purple #D7BDE2
- Layer 4 (Generation): pale purple #D7BDE2
- Layer 5 (Deployment): vibrant blue #3498DB
- Layer 5 (Deployment): vibrant blue #3498DB
- Layer 6 (Extension): light gray #ECF0F1 (external components)
- Layer 6 (Extension): light gray #ECF0F1 (external components)
- Metrics card: light yellow #FFF9E6 with bold numbers
- Metrics card: light yellow #FFF9E6 with bold numbers
- Foundation label: deep blue #2E86C1 background with white text
- Foundation label: deep blue #2E86C1 background with white text


**Typography**:
**Typography**:
- Main title: Arial Bold, 18pt
- Main title: Arial Bold, 18pt
- Layer titles: Arial Bold, 15pt
- Layer titles: Arial Bold, 15pt
- Sub-capability titles: Arial Bold, 11pt
- Sub-capability titles: Arial Bold, 11pt
- Sub-capability details: Arial, 9pt
- Sub-capability details: Arial, 9pt
- Metrics card title: Arial Bold, 14pt
- Metrics card title: Arial Bold, 14pt
- Metrics numbers: Arial Bold, 13pt
- Metrics numbers: Arial Bold, 13pt
- Metrics labels: Arial, 10pt
- Metrics labels: Arial, 10pt
- Foundation label: Arial Bold, 12pt
- Foundation label: Arial Bold, 12pt


**Negative constraints**:
**Negative constraints**:
- No photo-realistic component screenshots
- No photo-realistic component screenshots
- No decorative capability icons
- No decorative capability icons
- No gradient backgrounds on layers
- No gradient backgrounds on layers
- Arrows must be straight vertical/horizontal, no diagonals
- Arrows must be straight vertical/horizontal, no diagonals
- No drop shadows on capability boxes
- No drop shadows on capability boxes
- Keep layout clean and hierarchical
- Keep layout clean and hierarchical


---
---


## PPT-20: ECBF Safety Supervisor and Degradation Handling (P28页)
## PPT-20: ECBF Safety Supervisor and Degradation Handling (P28页)


**Figure Subject**: ECBF安全监督器与降级处置流程：实时碰撞检测与参考修正
**Figure Subject**: ECBF安全监督器与降级处置流程：实时碰撞检测与参考修正


**Diagram type**: Safety architecture flowchart (A类：架构/流程图)
**Diagram type**: Safety architecture flowchart (A类：架构/流程图)


**Layout**: 16:9 landscape, left-to-right safety monitoring pipeline
**Layout**: 16:9 landscape, left-to-right safety monitoring pipeline


**Mandatory nodes and visual elements**:
**Mandatory nodes and visual elements**:


**Top layer — Formation reference generator**:
**Top layer — Formation reference generator**:
- Box: "编队参考生成器"
- Box: "编队参考生成器"
- Inputs:
- Inputs:
  - Leader trajectory: r_leader(t)
  - Leader trajectory: r_leader(t)
  - Formation pattern: Triangle (3m edge)
  - Formation pattern: Triangle (3m edge)
- Outputs:
- Outputs:
  - UAV1 reference: r_1_ref(t)
  - UAV1 reference: r_1_ref(t)
  - UAV2 reference: r_2_ref(t)
  - UAV2 reference: r_2_ref(t)
  - UAV3 reference: r_3_ref(t)
  - UAV3 reference: r_3_ref(t)
- Arrow labeled: "初始参考轨迹"
- Arrow labeled: "初始参考轨迹"


**Middle layer — ECBF safety supervisor** (main component):
**Middle layer — ECBF safety supervisor** (main component):
- Large central box: "ECBF安全监督器"
- Large central box: "ECBF安全监督器"
- Three parallel monitoring channels inside:
- Three parallel monitoring channels inside:


  **Channel 1 — Distance monitoring**:
  **Channel 1 — Distance monitoring**:
  - Monitor block: "机间距离检测"
  - Monitor block: "机间距离检测"
  - Calculate:
  - Calculate:
    ```
    ```
    d₁₂ = ||r₁ - r₂||
    d₁₂ = ||r₁ - r₂||
    d₂₃ = ||r₂ - r₃||
    d₂₃ = ||r₂ - r₃||
    d₃₁ = ||r₃ - r₁||
    d₃₁ = ||r₃ - r₁||
    ```
    ```
  - Threshold check: d_ij < d_trigger = 2.8m ?
  - Threshold check: d_ij < d_trigger = 2.8m ?


  **Channel 2 — CBF constraint evaluation**:
  **Channel 2 — CBF constraint evaluation**:
  - Math block: "控制障碍函数 (CBF)"
  - Math block: "控制障碍函数 (CBF)"
  - Barrier function:
  - Barrier function:
    ```
    ```
    h(x) = d_ij - d_safe
    h(x) = d_ij - d_safe
    
    
    Safety constraint:
    Safety constraint:
    ḣ(x) + α·h(x) ≥ 0
    ḣ(x) + α·h(x) ≥ 0
    
    
    where:
    where:
      d_safe = 2.5m  (安全阈值)
      d_safe = 2.5m  (安全阈值)
      α = 0.5        (衰减系数)
      α = 0.5        (衰减系数)
    ```
    ```
  - Output: Safety violation flag
  - Output: Safety violation flag


  **Channel 3 — Repulsive force calculation**:
  **Channel 3 — Repulsive force calculation**:
  - Calculation block: "排斥力计算"
  - Calculation block: "排斥力计算"
  - If violation detected:
  - If violation detected:
    ```
    ```
    Δr_i = k_repel · (r_i - r_j) / ||r_i - r_j||
    Δr_i = k_repel · (r_i - r_j) / ||r_i - r_j||
    
    
    where:
    where:
      k_repel = 0.2  (排斥增益)
      k_repel = 0.2  (排斥增益)
      ||Δr_i|| ≤ 0.5m (最大修正量)
      ||Δr_i|| ≤ 0.5m (最大修正量)
    ```
    ```
  - Output: Position offset Δr_i
  - Output: Position offset Δr_i


**Decision diamond** (below safety supervisor):
**Decision diamond** (below safety supervisor):
- Diamond shape: "触发安全修正？"
- Diamond shape: "触发安全修正？"
- Two branches:
- Two branches:
  - YES (red path): "机间距离 < 2.8m"
  - YES (red path): "机间距离 < 2.8m"
  - NO (green path): "保持原参考"
  - NO (green path): "保持原参考"


**YES branch — Reference correction**:
**YES branch — Reference correction**:
- Process box: "参考位置修正"
- Process box: "参考位置修正"
- Operation:
- Operation:
  ```
  ```
  r_i_corrected = r_i_ref + Δr_i
  r_i_corrected = r_i_ref + Δr_i
  ```
  ```
- Annotation: "施加排斥力，远离冲突"
- Annotation: "施加排斥力，远离冲突"
- Output: Modified reference
- Output: Modified reference


**NO branch — Direct pass-through**:
**NO branch — Direct pass-through**:
- Direct arrow bypass
- Direct arrow bypass
- Annotation: "无冲突，保持原轨迹"
- Annotation: "无冲突，保持原轨迹"
- Output: Original reference
- Output: Original reference


**Bottom layer — Individual controllers**:
**Bottom layer — Individual controllers**:
- Three controller boxes:
- Three controller boxes:
  - UAV1 controller (px4ctrl)
  - UAV1 controller (px4ctrl)
  - UAV2 controller (px4ctrl)
  - UAV2 controller (px4ctrl)
  - UAV3 controller (px4ctrl)
  - UAV3 controller (px4ctrl)
- Input: Corrected/original reference
- Input: Corrected/original reference
- Output: Control commands to each UAV
- Output: Control commands to each UAV


**Right side — Key characteristics**:
**Right side — Key characteristics**:


**ECBF特性**:
**ECBF特性**:
```
```
✅ 实时修正
✅ 实时修正
   - 检测频率: 200Hz
   - 检测频率: 200Hz
   - 修正延迟: <5ms
   - 修正延迟: <5ms
   - 无需离线规划
   - 无需离线规划


✅ 保证安全又不破坏队形
✅ 保证安全又不破坏队形
   - 最大修正量: 0.5m
   - 最大修正量: 0.5m
   - 触发阈值: 2.8m
   - 触发阈值: 2.8m
   - 安全距离: 2.5m
   - 安全距离: 2.5m


✅ 纯MWORKS实现
✅ 纯MWORKS实现
   - Guidance层实现
   - Guidance层实现
   - 无需外部规划器
   - 无需外部规划器
   - 与控制层解耦
   - 与控制层解耦
```
```


**Performance metrics box** (bottom-right):
**Performance metrics box** (bottom-right):
```
```
实际运行数据:
实际运行数据:
━━━━━━━━━━━━━━
━━━━━━━━━━━━━━
触发时刻: t=12s, 25s, 38s
触发时刻: t=12s, 25s, 38s
最大修正量: 0.48m
最大修正量: 0.48m
修正持续时间: ~2s
修正持续时间: ~2s
最小机间距: 2.52m
最小机间距: 2.52m
碰撞事件: 0
碰撞事件: 0
```
```


**Timing diagram** (top-right, small inset):
**Timing diagram** (top-right, small inset):
- Time axis showing:
- Time axis showing:
  - Normal state (green): d > 2.8m, no correction
  - Normal state (green): d > 2.8m, no correction
  - Warning state (yellow): 2.8m > d > 2.5m, ECBF active
  - Warning state (yellow): 2.8m > d > 2.5m, ECBF active
  - Violation state (red): d < 2.5m, emergency (never reached)
  - Violation state (red): d < 2.5m, emergency (never reached)


**Visual elements**:
**Visual elements**:
- Three UAV icons showing formation positions
- Three UAV icons showing formation positions
- Distance lines d₁₂, d₂₃, d₃₁ between UAVs
- Distance lines d₁₂, d₂₃, d₃₁ between UAVs
- Repulsive force vectors (red arrows) when ECBF triggers
- Repulsive force vectors (red arrows) when ECBF triggers
- Safety boundary circle (dashed, 2.5m radius) around each UAV
- Safety boundary circle (dashed, 2.5m radius) around each UAV


**Connections**:
**Connections**:
- Solid thick arrows: main reference flow
- Solid thick arrows: main reference flow
- Dashed arrows: monitoring/feedback signals
- Dashed arrows: monitoring/feedback signals
- Red arrows: safety correction paths
- Red arrows: safety correction paths
- Green arrows: normal pass-through
- Green arrows: normal pass-through


**Color scheme**:
**Color scheme**:
- Formation generator: pale blue #AED6F1
- Formation generator: pale blue #AED6F1
- ECBF supervisor box: vibrant orange #F8C471 (safety color)
- ECBF supervisor box: vibrant orange #F8C471 (safety color)
- Distance monitoring: pale green #A9DFBF
- Distance monitoring: pale green #A9DFBF
- CBF evaluation: pale yellow #FFF9E6
- CBF evaluation: pale yellow #FFF9E6
- Repulsive force: pale red #F5B7B1
- Repulsive force: pale red #F5B7B1
- Decision diamond: white with bold orange border
- Decision diamond: white with bold orange border
- YES branch: red path #E74C3C
- YES branch: red path #E74C3C
- NO branch: green path #27AE60
- NO branch: green path #27AE60
- Controllers: deep blue #2E86C1
- Controllers: deep blue #2E86C1
- Characteristics box: light yellow #FFF9E6 with green checkmarks
- Characteristics box: light yellow #FFF9E6 with green checkmarks
- Metrics box: light cream #FFFACD
- Metrics box: light cream #FFFACD
- Timing diagram: green/yellow/red segments
- Timing diagram: green/yellow/red segments


**Typography**:
**Typography**:
- Main box titles: Arial Bold, 14pt
- Main box titles: Arial Bold, 14pt
- Process labels: Arial Bold, 12pt
- Process labels: Arial Bold, 12pt
- Mathematical formulas: Computer Modern, 11pt
- Mathematical formulas: Computer Modern, 11pt
- Decision text: Arial Bold, 11pt
- Decision text: Arial Bold, 11pt
- Annotations: Arial, 10pt
- Annotations: Arial, 10pt
- Metrics: Consolas monospace, 10pt
- Metrics: Consolas monospace, 10pt


**Negative constraints**:
**Negative constraints**:
- No photo-realistic UAV models
- No photo-realistic UAV models
- No actual flight trajectory plots
- No actual flight trajectory plots
- No decorative safety icons (shields, warning signs)
- No decorative safety icons (shields, warning signs)
- Arrows must be orthogonal or 45°, no curves
- Arrows must be orthogonal or 45°, no curves
- No gradient fills on major boxes
- No gradient fills on major boxes
- No drop shadows on decision diamond
- No drop shadows on decision diamond


---
---


## 完成！所有AI生图prompt已补充完毕
## 完成！所有AI生图prompt已补充完毕


### 最终Prompt清单（共20个）：
### 最终Prompt清单（共20个）：


**原有5个**：
**原有5个**：
1. PPT-01: 全链路管道
1. PPT-01: 全链路管道
2. PPT-02: 五层架构
2. PPT-02: 五层架构
3. PPT-03: 四接口共享Plant
3. PPT-03: 四接口共享Plant
4. PPT-04: 三机Guidance架构（已废弃）
4. PPT-04: 三机Guidance架构（已废弃）
5. PPT-05: WSL2部署栈（已废弃）
5. PPT-05: WSL2部署栈（已废弃）


**新增15个**：
**新增15个**：
6. PPT-06: 四旋翼动力学模型 (P07)
6. PPT-06: 四旋翼动力学模型 (P07)
7. PPT-07: Adapter坐标转换 (P08)
7. PPT-07: Adapter坐标转换 (P08)
8. PPT-08: 统一实验框架 (P08)
8. PPT-08: 统一实验框架 (P08)
9. PPT-09: 七族算法分类树 (P10)
9. PPT-09: 七族算法分类树 (P10)
10. PPT-10: px4ctrl三层架构 (P17)
10. PPT-10: px4ctrl三层架构 (P17)
11. PPT-11: AI Agent知识注入 (P21)
11. PPT-11: AI Agent知识注入 (P21)
12. PPT-12: OpenBlocks规划链路 (P29)
12. PPT-12: OpenBlocks规划链路 (P29)
13. PPT-13: MWORKS实时外环与WSL2数据流 (P35)
13. PPT-13: MWORKS实时外环与WSL2数据流 (P35)
14. PPT-14: C99代码包结构与部署路径 (P40)
14. PPT-14: C99代码包结构与部署路径 (P40)
15. PPT-15: Gazebo状态反馈通路设计 (P43)
15. PPT-15: Gazebo状态反馈通路设计 (P43)
16. PPT-16: Diff-Planner微分平坦轨迹优化 (P47)
16. PPT-16: Diff-Planner微分平坦轨迹优化 (P47)
17. PPT-17: FUEL自主探索架构 (P48)
17. PPT-17: FUEL自主探索架构 (P48)
18. PPT-18: UE → Gazebo mesh导出链路 (P49)
18. PPT-18: UE → Gazebo mesh导出链路 (P49)
19. PPT-19: MWORKS全链路能力地图 (P50)
19. PPT-19: MWORKS全链路能力地图 (P50)
20. **PPT-20: ECBF安全监督器与降级处置流程 (P28)**
20. **PPT-20: ECBF安全监督器与降级处置流程 (P28)**


**全部完成！可以开始根据prompt生成图了。**
**全部完成！可以开始根据prompt生成图了。**


### 新增Prompt清单总结：
### 新增Prompt清单总结：


| 编号 | 页码 | 图名称 | 复杂度 | 优先级 |
| 编号 | 页码 | 图名称 | 复杂度 | 优先级 |
|------|------|--------|--------|--------|
|------|------|--------|--------|--------|
| PPT-06 | P07 | 四旋翼动力学模型 | 中 | 高 |
| PPT-06 | P07 | 四旋翼动力学模型 | 中 | 高 |
| PPT-07 | P08 | Adapter坐标转换详解 | 中 | 高 |
| PPT-07 | P08 | Adapter坐标转换详解 | 中 | 高 |
| PPT-08 | P08 | 统一实验框架 | 高 | 高 |
| PPT-08 | P08 | 统一实验框架 | 高 | 高 |
| PPT-09 | P10 | 七族算法分类树 | 高 | 高 |
| PPT-09 | P10 | 七族算法分类树 | 高 | 高 |
| PPT-10 | P17 | px4ctrl三层架构 | 高 | 高 |
| PPT-10 | P17 | px4ctrl三层架构 | 高 | 高 |
| PPT-11 | P21 | AI Agent知识注入架构 | 中 | 中 |
| PPT-11 | P21 | AI Agent知识注入架构 | 中 | 中 |
| PPT-12 | P29 | OpenBlocks规划链路 | 高 | 高 |
| PPT-12 | P29 | OpenBlocks规划链路 | 高 | 高 |
| PPT-13 | P35 | MWORKS实时外环与WSL2数据流 | 高 | 高 |
| PPT-13 | P35 | MWORKS实时外环与WSL2数据流 | 高 | 高 |
| PPT-14 | P40 | C99代码包结构与部署路径 | 中 | 高 |
| PPT-14 | P40 | C99代码包结构与部署路径 | 中 | 高 |
| PPT-15 | P43 | Gazebo状态反馈通路设计 | 高 | 高 |
| PPT-15 | P43 | Gazebo状态反馈通路设计 | 高 | 高 |
| PPT-16 | P47 | Diff-Planner微分平坦轨迹优化 | 高 | 中 |
| PPT-16 | P47 | Diff-Planner微分平坦轨迹优化 | 高 | 中 |
| PPT-17 | P48 | FUEL自主探索架构 | 高 | 中 |
| PPT-17 | P48 | FUEL自主探索架构 | 高 | 中 |
| PPT-18 | P49 | UE → Gazebo mesh导出链路 | 中 | 低 |
| PPT-18 | P49 | UE → Gazebo mesh导出链路 | 中 | 低 |
| PPT-19 | P50 | MWORKS全链路能力地图 | 高 | 高 |
| PPT-19 | P50 | MWORKS全链路能力地图 | 高 | 高 |


**所有prompt已追加到 `prompt.md` 文件末尾！**
**所有prompt已追加到 `prompt.md` 文件末尾！**
