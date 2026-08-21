# 7张缺失手绘图的生成Prompt

**生成时间**: 2026-08-21  
**目标**: 补齐大纲需要但prompt.md中缺失的7张手绘图

---

## PPT-21: Sysblock控制器结构树

**使用位置**: P5（第159行）  
**大纲描述**: "手绘图1 - MWORKS Sysblock控制器结构树"

### 生成指令

**画面主题**: Sysblock图形化控制器的层级结构与建模方式

**布局**: 竖版（1920×1080），深色背景（#0A0D12）

**内容结构**：

1. **顶部标题**（20%高度）
   - 主标题：`Sysblock Graphical Controller Modeling Architecture`
   - 副标题：`Pure Graphical Block Programming — No Code Required`

2. **中部结构树**（60%高度，三层树状图）

   **第一层：控制器接口层**
   - 左侧输入端口（绿色圆圈）：
     - `State Input` (position, velocity, attitude)
     - `Reference Input` (desired trajectory)
   - 右侧输出端口（橙色圆圈）：
     - `Control Output` (thrust, body_rate, wrench, rotor_cmd)

   **第二层：控制逻辑核心**（中央大框，浅青色 #1E2636）
   - 顶部：`Outer Loop` 模块（位置/速度控制器）
   - 中部：`Inner Loop` 模块（姿态/角速度控制器）
   - 底部：`Control Allocation` 模块（控制分配矩阵）
   - 用箭头连接三个模块的数据流

   **第三层：参数配置层**
   - 右侧悬浮：`Parameter Panel`（参数面板，半透明框）
     - 列出参数项：`Kp`, `Kd`, `Ki`, `mass`, `inertia`
     - 标注：`Tunable Parameters — No Recompilation`

3. **底部特性标注**（20%高度）
   - 左下角：图标 + 文字
     - ✅ `Drag-and-Drop Modeling`（拖拽建模）
     - ✅ `Real-Time Parameter Tuning`（实时参数调优）
     - ✅ `48 Controllers Built with This Architecture`（48个控制器采用此架构）
   - 右下角：图标
     - MWORKS Sysblock Logo（小图标）

**配色**：
- 背景：深蓝黑 #0A0D12
- 输入端口：绿色 #6EE7B7
- 输出端口：橙色 #E9A568
- 控制模块：浅青 #1E2636 + 边框 #38BDF8
- 箭头：白色 #FFFFFF，带辉光效果
- 文字：白色 #FFFFFF（标题）、浅灰 #CADCFC（说明）

**风格**：
- 手绘风格：线条略带抖动，模块边角带手绘感
- 箭头采用实心箭头，粗线条（4px）
- 参数面板带阴影，营造浮动感

---

## PPT-22: MoSim Studio主界面

**使用位置**: P11（第365行）  
**大纲描述**: "手绘图5 - MoSim Studio主界面"

### 生成指令

**画面主题**: MoSim Studio拖拽式配置工具的用户界面

**布局**: 横版（1920×1080），模拟软件界面截图的手绘版

**内容结构**：

1. **顶部菜单栏**（10%高度）
   - 左侧：`MoSim Studio` Logo + 文字
   - 右侧：`File` | `Edit` | `Run` | `Export` 菜单按钮

2. **左侧控制器库**（30%宽度）
   - 标题：`Controller Library`（控制器库）
   - 展示7个控制器族的图标+名称（垂直排列）：
     - `🎯 PID Family` (8个)
     - `🚀 INDI Family` (6个)
     - `🎮 MPC Family` (5个)
     - `🔧 AWFF Family` (7个)
     - `🌊 L1 Family` (4个)
     - `🧠 Hybrid Family` (9个)
     - `⭐ px4ctrl` (1个)

3. **中央配置画布**（50%宽度）
   - 标题：`Experiment Configuration`（实验配置）
   - 展示一个配置流程图（手绘风格）：
     ```
     [Scenario: ClimbPath] → [Controller: official_pid] → [Adapter: ENU] → [Plant: Quadrotor] → [Run Simulation]
     ```
   - 每个模块用圆角矩形框表示，带拖拽手柄（左上角三条横线图标）
   - 模块之间用箭头连接

4. **右侧参数面板**（20%宽度）
   - 标题：`Parameter Tuning`（参数调优）
   - 展示滑块控件（手绘风格）：
     - `Kp_xy: 5.0` （滑块）
     - `Kd_xy: 3.0` （滑块）
     - `Kp_z: 8.0` （滑块）
   - 底部：`Apply` 和 `Reset` 按钮

5. **底部状态栏**（10%高度）
   - 左侧：`✅ Ready to Run` （就绪状态）
   - 中央：`Simulation Time: 50s | Step Size: 0.01s`
   - 右侧：`Export to C99` 按钮（高亮）

**配色**：
- 背景：深灰 #0F131C
- 左侧库：深蓝 #161D2B
- 中央画布：稍浅 #1E2636
- 右侧面板：深蓝 #161D2B
- 高亮元素：青色 #38BDF8
- 按钮：橙色 #E9A568

**风格**：
- 手绘界面风格，但保持清晰可读
- 控制器族图标用emoji+文字组合
- 模块框带轻微阴影

---

## PPT-23: MPC滚动时域优化原理

**使用位置**: P13（第442行）  
**大纲描述**: "手绘图6 - MPC滚动时域优化原理"

### 生成指令

**画面主题**: MPC预测窗口、滚动优化、代价函数的工作原理

**布局**: 横版（1920×1080），深色背景

**内容结构**：

1. **顶部标题**（15%高度）
   - 主标题：`Model Predictive Control — Receding Horizon Optimization`
   - 副标题：`Predict Future → Optimize Trajectory → Execute First Step → Repeat`

2. **中部核心图示**（70%高度）

   **左侧：时间轴示意图**（40%宽度）
   - 横轴：时间轴（0s, 1s, 2s, 3s, 4s）
   - 纵轴：状态（位置/速度）
   - 展示三个时刻的预测窗口：
     - **t=0s**: 预测窗口0→3s（蓝色虚线轨迹）
     - **t=1s**: 预测窗口1→4s（绿色虚线轨迹）
     - **t=2s**: 预测窗口2→5s（橙色虚线轨迹）
   - 标注：`Prediction Horizon = 3s`
   - 实际执行轨迹：实线（红色），只执行每个窗口的第一步

   **右侧：代价函数与约束**（60%宽度）
   - 顶部框：`Cost Function`（代价函数）
     ```
     J = Σ (||x - x_ref||² + ||u||²)
     ```
     - 解释：`Tracking Error + Control Effort`
   
   - 中部框：`Constraints`（约束）
     - `|u| ≤ u_max`（控制输入限制）
     - `|x| ≤ x_max`（状态限制）
     - `Collision Avoidance`（避障约束，画一个禁飞区圆形）
   
   - 底部框：`Online Optimization`（在线优化）
     - 画一个循环箭头图标
     - 文字：`Solve QP at 20Hz → Update Control`

3. **底部特性标注**（15%高度）
   - 左下：✅ `Handles Constraints Explicitly`（显式处理约束）
   - 中下：✅ `Predictive — Not Reactive`（预测式而非反应式）
   - 右下：✅ `5 MPC Variants in MoSim`（MoSim中5个MPC变体）

**配色**：
- 背景：深蓝黑 #0A0D12
- 预测轨迹：蓝#38BDF8、绿#6EE7B7、橙#E9A568（渐变透明）
- 实际轨迹：红色 #F96167，实线粗3px
- 代价函数框：深青 #1E2636，边框青色
- 约束框：深紫 #2C1E3A，边框紫色 #9D4EDD

**风格**：
- 时间轴轨迹图手绘风格，线条带抖动
- 公式用清晰的Sans-serif字体
- 禁飞区用虚线圆圈+阴影表示

---

## PPT-24: 七场景卡片墙

**使用位置**: P21（第676行）  
**大纲描述**: "手绘图9 - 七场景卡片墙（24布局，最后一个空位）"

### 生成指令

**画面主题**: 7个仿真场景的快照卡片墙，2×4网格布局

**布局**: 横版（1920×1080），深色背景

**内容结构**：

1. **顶部标题**（10%高度）
   - 主标题：`Seven Validation Scenarios`
   - 副标题：`From Basic Tracking to Complex Formation & Exploration`

2. **中部卡片墙**（80%高度，2行×4列网格）

   **第一行（4张卡片）**：
   
   - **卡片1: ClimbPath**
     - 图示：简化的3D轨迹线（螺旋上升）
     - 标题：`ClimbPath`
     - 标签：`Basic Tracking` | `50s Duration`
   
   - **卡片2: Figure8**
     - 图示：8字形轨迹（俯视图）
     - 标题：`Figure8`
     - 标签：`Aggressive Maneuver` | `30s`
   
   - **卡片3: ThreeUAV Formation**
     - 图示：三个无人机图标排成三角形
     - 标题：`Formation (3-UAV)`
     - 标签：`Multi-Agent` | `60s`
   
   - **卡片4: ECBF Safety**
     - 图示：两个无人机+中间虚线安全距离
     - 标题：`ECBF Safety Test`
     - 标签：`Collision Avoidance` | `40s`

   **第二行（4张卡片）**：
   
   - **卡片5: OpenBlocks Obstacle**
     - 图示：无人机+障碍物方块
     - 标题：`OpenBlocks Planning`
     - 标签：`Local Planner` | `50s`
   
   - **卡片6: Diff-Planner**
     - 图示：B样条轨迹+梯度箭头
     - 标题：`Diff-Planner Optimization`
     - 标签：`Trajectory Optimization` | `30s`
   
   - **卡片7: FUEL Exploration**
     - 图示：未知地图+探索路径
     - 标题：`FUEL Autonomous Exploration`
     - 标签：`Frontier Search` | `120s`
   
   - **卡片8: 空位**（灰色虚线框）
     - 文字：`Reserved for Future Scenarios`

3. **底部统计**（10%高度）
   - 左侧：`Total: 7 Active Scenarios | 1 Reserved`
   - 右侧：`Tested Controllers: 48 | Success Rate: 73.7%`

**配色**：
- 背景：深蓝黑 #0A0D12
- 卡片背景：深灰 #1E2636
- 卡片边框：青色 #38BDF8（2px）
- 标签背景：半透明青 rgba(56, 189, 248, 0.2)
- 空位卡片：虚线框 #4A5568

**风格**：
- 每张卡片内的图示用极简手绘风格
- 卡片之间留20px间距
- 标签用圆角矩形，小字号

---

## PPT-25: MWORKS Live实时仿真界面

**使用位置**: P27（第978行）  
**大纲描述**: "手绘图10 - MWORKS Live实时联合仿真工作区界面"

### 生成指令

**画面主题**: MWORKS Live实时仿真的工作区界面截图手绘版

**布局**: 横版（1920×1080），模拟软件界面

**内容结构**：

1. **顶部工具栏**（8%高度）
   - 左侧：`MWORKS Live` Logo
   - 中央：播放/暂停/停止按钮（▶ ⏸ ⏹）
   - 右侧：实时时钟 `00:05:32 / 00:50:00`

2. **左上：Sysblock控制器视图**（35%宽度×40%高度）
   - 标题：`Controller Model (Sysblock)`
   - 显示简化的Sysblock框图：
     - 输入框 `State` → 控制器框 `PID Controller` → 输出框 `Thrust`
   - 标注：`Running at 200Hz`

3. **右上：3D可视化窗口**（60%宽度×40%高度）
   - 标题：`Gazebo Simulation View`
   - 显示简化的3D场景：
     - 一个四旋翼无人机（俯视图）
     - 地面网格
     - 参考轨迹线（虚线）
   - 标注：`WSL2 Ubuntu 20.04 + ROS1 Noetic`

4. **左下：参数监控面板**（35%宽度×50%高度）
   - 标题：`Real-Time Parameter Monitor`
   - 显示参数列表（表格形式）：
     ```
     Parameter    | Value   | Status
     -------------|---------|-------
     Kp_xy        | 5.0     | ✅ OK
     Kd_xy        | 3.0     | ✅ OK
     thrust       | 12.5 N  | ✅ OK
     altitude     | 10.2 m  | ✅ OK
     ```

5. **右下：实时曲线图**（60%宽度×50%高度）
   - 标题：`Position Tracking (Real-Time)`
   - 显示三条曲线（X/Y/Z位置）：
     - X轴：时间（0-50s）
     - Y轴：位置（m）
     - 三条曲线：蓝色（X）、绿色（Y）、红色（Z）
   - 参考线用虚线标注

**配色**：
- 背景：深灰 #0F131C
- 各窗口背景：稍浅 #1E2636
- 工具栏：深蓝 #161D2B
- 曲线：蓝#38BDF8、绿#6EE7B7、红#F96167

**风格**：
- 界面元素手绘风格但保持清晰
- 3D视图用简化的线框模型
- 曲线图用平滑曲线

---

## PPT-26: Gazebo五类任务性能对比

**使用位置**: P35（第1286行）  
**大纲描述**: "手绘图15 - Gazebo五类任务性能对比"

### 生成指令

**画面主题**: 五种Gazebo仿真任务的性能对比柱状图

**布局**: 横版（1920×1080），深色背景

**内容结构**：

1. **顶部标题**（15%高度）
   - 主标题：`Gazebo Simulation Performance Comparison`
   - 副标题：`Tracking Error & Success Rate Across Five Task Types`

2. **中部双柱状图**（70%高度）

   **上半部分：跟踪误差对比**（45%高度）
   - 标题：`Average Tracking Error (meters)`
   - X轴：五种任务类型
     - `ClimbPath`
     - `Figure8`
     - `Formation`
     - `Obstacle Avoidance`
     - `Exploration`
   - Y轴：误差（0-15m）
   - 柱状图数据（示例数据，手绘风格）：
     - ClimbPath: 2.3m（绿色，低误差）
     - Figure8: 4.8m（黄色，中误差）
     - Formation: 6.5m（橙色，中高误差）
     - Obstacle: 3.2m（绿色）
     - Exploration: 8.1m（红色，高误差）
   - 标注门限线：`5m Threshold`（虚线，红色）

   **下半部分：成功率对比**（45%高度）
   - 标题：`Success Rate (% of Controllers Passed)`
   - X轴：同上五种任务
   - Y轴：成功率（0-100%）
   - 柱状图数据：
     - ClimbPath: 73.7%（绿色）
     - Figure8: 45.2%（黄色）
     - Formation: 38.5%（橙色）
     - Obstacle: 62.1%（黄绿）
     - Exploration: 28.3%（红色）
   - 标注目标线：`80% Target`（虚线，蓝色）

3. **底部统计摘要**（15%高度）
   - 左侧：`Total Tests: 240 (48 controllers × 5 tasks)`
   - 中央：`Overall Success Rate: 49.6%`
   - 右侧：`Best Performer: official_pid & px4_ctrl (100%)`

**配色**：
- 背景：深蓝黑 #0A0D12
- 柱状图：绿#6EE7B7、黄#F9E795、橙#E9A568、红#F96167
- 门限线：红色虚线
- 目标线：蓝色虚线 #38BDF8
- 网格线：浅灰 #2A3142

**风格**：
- 柱状图手绘风格，边缘略带抖动
- 每根柱子顶部标注数值
- 网格线用细虚线

---

## PPT-27: 七场景验证矩阵

**使用位置**: P40（第1558行）  
**大纲描述**: "手绘图19 - 七场景验证矩阵"

### 生成指令

**画面主题**: 7个场景×多个验证维度的矩阵表格

**布局**: 横版（1920×1080），深色背景

**内容结构**：

1. **顶部标题**（10%高度）
   - 主标题：`Seven-Scenario Validation Matrix`
   - 副标题：`Comprehensive Testing Across Multiple Dimensions`

2. **中部矩阵表格**（80%高度，7行×6列）

   **列标题**（第一行）：
   - `Scenario` | `MWORKS SIL` | `Gazebo HIL` | `RT0 Real-Time` | `Tracking Error` | `Safety Check` | `Overall Status`

   **行内容**（7个场景）：
   
   - **Row 1: ClimbPath**
     - MWORKS SIL: ✅（绿色勾）
     - Gazebo HIL: ✅
     - RT0 Real-Time: ✅
     - Tracking Error: `2.3m`（绿色）
     - Safety Check: ✅
     - Overall: ✅ `PASS`
   
   - **Row 2: Figure8**
     - MWORKS SIL: ✅
     - Gazebo HIL: ⚠️（黄色警告）
     - RT0: ❌（红色叉）
     - Tracking Error: `4.8m`（黄色）
     - Safety: ✅
     - Overall: ⚠️ `PARTIAL`
   
   - **Row 3: Formation**
     - MWORKS SIL: ✅
     - Gazebo HIL: ✅
     - RT0: ⚠️
     - Tracking Error: `6.5m`（橙色）
     - Safety: ✅
     - Overall: ⚠️ `PARTIAL`
   
   - **Row 4: ECBF Safety**
     - MWORKS SIL: ✅
     - Gazebo HIL: ✅
     - RT0: ❌
     - Tracking Error: `3.2m`（绿色）
     - Safety: ✅
     - Overall: ⚠️ `PARTIAL`
   
   - **Row 5: OpenBlocks**
     - MWORKS SIL: ✅
     - Gazebo HIL: ✅
     - RT0: ❌
     - Tracking Error: `5.1m`（黄色）
     - Safety: ✅
     - Overall: ⚠️ `PARTIAL`
   
   - **Row 6: Diff-Planner**
     - MWORKS SIL: ✅
     - Gazebo HIL: ⚠️
     - RT0: N/A（灰色）
     - Tracking Error: `7.2m`（橙色）
     - Safety: ✅
     - Overall: ⚠️ `PARTIAL`
   
   - **Row 7: FUEL**
     - MWORKS SIL: ✅
     - Gazebo HIL: ✅
     - RT0: N/A
     - Tracking Error: `8.1m`（红色）
     - Safety: ⚠️
     - Overall: ⚠️ `PARTIAL`

3. **底部统计**（10%高度）
   - 左侧：`✅ Full Pass: 1/7 (14.3%)`
   - 中央：`⚠️ Partial Pass: 6/7 (85.7%)`
   - 右侧：`❌ Fail: 0/7 (0%)`

**配色**：
- 背景：深蓝黑 #0A0D12
- 表格背景：深灰 #1E2636
- 表头：深青 #0F2A3D，文字白色
- ✅绿色勾：#6EE7B7
- ⚠️黄色警告：#F9E795
- ❌红色叉：#F96167
- 边框：浅灰 #2A3142

**风格**：
- 表格手绘风格，线条略带抖动
- 图标（✅⚠️❌）用手绘风格
- 误差数值用颜色编码（<5m绿色、5-7m黄色、>7m红色）

---

**所有7张图的prompt已准备完毕**  
**下一步**：使用这些prompt生成21.png到27.png，然后更新大纲引用路径
