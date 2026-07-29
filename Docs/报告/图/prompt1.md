# 竞标书单图 Prompt Pack

本文件按“每次只生成一张图”使用方式重组。每个图的代码块都是完整 prompt，可单独复制给生图 agent，不依赖任何前置全局说明。

使用规则：

- 每次只复制一个图对应的代码块。
- 不要再额外拼接全局前缀。
- 图片中不要出现图名、图号、Figure、Caption 等标题性文字。
- 如果某张图生成不稳定，优先补强当前图自己的 Layout、Mandatory nodes、Mandatory connections 和 Negative constraints。`

---

### 图 1 系统应用场景与业务闭环图

`	ext
Create a high-end, strict 2D engineering diagram for a professional software engineering document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background.
Color Palette & Borders: High-contrast engineering. Use PURE BLACK (#000000) for ALL text, connecting lines, and arrowheads. EVERY SINGLE INDIVIDUAL NODE MUST have a solid black 1px border/outline. Do not leave any node text floating without a visible rectangular or rounded-rectangular boundary. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes.
Containers: ABSOLUTELY NO large grouping boxes enclosing multiple nodes, NO dashed boundaries beneath nodes. Standalone nodes only.
Aesthetics: ABSOLUTELY NO 3D, NO TRAYS, NO BASES. Draw the UML nodes directly on the empty white canvas. NEVER draw a secondary box, dashed box, or shadow underneath the nodes. Focus heavily on 'Code Architecture' and technical rigor.
Layout & Connections: COMPACT UML FLOWCHART STYLE. Grid-based pixel-perfect alignment with tight, compact node spacing. ONLY use strictly ORTHOGONAL lines (straight vertical/horizontal lines with explicit 90-degree right-angle turns). Absolutely NO diagonal lines. Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows.
Typography constraint: MUST USE EXACT TEXT as provided in the nodes/connections list. DO NOT translate, DO NOT reformat, DO NOT generate new labels. Copy the exact text provided (e.g. "EnglishCodeName (中文注释)").

Figure Subject:
系统应用场景与业务闭环图

Diagram type:
Compact UML Activity/Flow Architecture Diagram

Layout:
Strictly compact left-to-right horizontal pipeline. Route ALL lines universally as orthogonal lines with 90-degree corners. EVERY node MUST be drawn inside a solid black rectangular box.

Mandatory nodes:
- SourceSignals (外部信号源)
- DataGateway (数据接入中间件)
- RealtimeCache (实时内存缓存)
- StatsAnalysis (统计分析模块)
- FftAnalysis (FFT频谱分析)
- AlarmEvaluator (报警判断模块)
- AsyncFileWriter (异步文件记录)
- HistoryReplay (历史回放引擎)
- GraphicsRender (图形渲染引擎)
- MonitorDashboard (单窗口监控界面)

Mandatory connections:
- SourceSignals (外部信号源) -> DataGateway (数据接入中间件)
- DataGateway (数据接入中间件) -> RealtimeCache (实时内存缓存)
- RealtimeCache (实时内存缓存) -> StatsAnalysis (统计分析模块)
- RealtimeCache (实时内存缓存) -> FftAnalysis (FFT频谱分析)
- StatsAnalysis (统计分析模块) -> AlarmEvaluator (报警判断模块)
- RealtimeCache (实时内存缓存) -> GraphicsRender (图形渲染引擎)
- FftAnalysis (FFT频谱分析) -> GraphicsRender (图形渲染引擎)
- AlarmEvaluator (报警判断模块) -> GraphicsRender (图形渲染引擎)
- GraphicsRender (图形渲染引擎) -> MonitorDashboard (单窗口监控界面)
- RealtimeCache (实时内存缓存) -> AsyncFileWriter (异步文件记录)
- AsyncFileWriter (异步文件记录) -> HistoryReplay (历史回放引擎)
- HistoryReplay (历史回放引擎) -> MonitorDashboard (单窗口监控界面)

Negative constraints:
CRITICAL: DO NOT draw any trays, platforms, dashed outlines, or secondary boxes beneath the text nodes. Each node MUST be drawn as a shape (e.g., rectangle) with a solid black border and pastel background. DO NOT leave text floating without a border box. Reject any 3D or pseudo-3D styling. No screenshots, no decorative elements. PURE 2D FLAT DESIGN ONLY.
`

---

### 图 2 项目总体目标关系图

`	ext
Create a high-end, strict 2D engineering diagram for a professional software engineering document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background.
Color Palette & Borders: High-contrast engineering. Use PURE BLACK (#000000) for ALL text, connecting lines, and arrowheads. EVERY SINGLE INDIVIDUAL NODE MUST have a solid black 1px border/outline. Do not leave any node text floating without a visible rectangular or rounded-rectangular boundary. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes.
Containers: ABSOLUTELY NO large grouping boxes enclosing multiple nodes, NO dashed boundaries beneath nodes. Standalone nodes only.
Aesthetics: ABSOLUTELY NO 3D, NO TRAYS, NO BASES. Draw the UML nodes directly on the empty white canvas. NEVER draw a secondary box, dashed box, or shadow underneath the nodes. Focus heavily on 'Code Architecture' and technical rigor.
Layout & Connections: COMPACT UML FLOWCHART STYLE. Grid-based pixel-perfect alignment with tight, compact node spacing. ONLY use strictly ORTHOGONAL lines (straight vertical/horizontal lines with explicit 90-degree right-angle turns). Absolutely NO diagonal lines. Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows.
Typography constraint: MUST USE EXACT TEXT as provided in the nodes/connections list. DO NOT translate, DO NOT reformat, DO NOT generate new labels. Copy the exact text provided (e.g. "EnglishCodeName (中文注释)").

Figure Subject:
项目总体目标关系图

Diagram type:
Compact Horizontal UML Tree Diagram

Layout:
STRICTLY LEFT-TO-RIGHT HORIZONTAL TREE LAYOUT. The SimulationSystem node sits at the center-left, explicitly branching into 3 horizontal logical goals. Connections MUST be 90-degree orthogonal lines branching outward. EVERY node MUST be drawn inside a solid black rectangular box.

Mandatory nodes:
- SimulationSystem (实时监控智能分析系统)
- FuncGoals (功能应用目标)
- TechGoals (底层架构目标)
- MgmtGoals (工程管理目标)
- SignalSimulation (信号模拟)
- RealtimeDisplay (实时显示)
- StatsModule (统计分析)
- LayeredArch (分层架构)
- MultiThreading (多线程并发)
- MemoryPools (内存池化缓存)
- AgileDev (敏捷开发循环)
- GitControl (Git版本控制)
- ProjectMgmt (项目管理工具)

Mandatory connections:
- SimulationSystem (实时监控智能分析系统) -> FuncGoals (功能应用目标)
- SimulationSystem (实时监控智能分析系统) -> TechGoals (底层架构目标)
- SimulationSystem (实时监控智能分析系统) -> MgmtGoals (工程管理目标)
- FuncGoals (功能应用目标) -> SignalSimulation (信号模拟)
- FuncGoals (功能应用目标) -> RealtimeDisplay (实时显示)
- FuncGoals (功能应用目标) -> StatsModule (统计分析)
- TechGoals (底层架构目标) -> LayeredArch (分层架构)
- TechGoals (底层架构目标) -> MultiThreading (多线程并发)
- TechGoals (底层架构目标) -> MemoryPools (内存池化缓存)
- MgmtGoals (工程管理目标) -> AgileDev (敏捷开发循环)
- MgmtGoals (工程管理目标) -> GitControl (Git版本控制)
- MgmtGoals (工程管理目标) -> ProjectMgmt (项目管理工具)

Negative constraints:
CRITICAL: DO NOT draw any trays, platforms, dashed outlines, or secondary boxes beneath the text nodes. Each node MUST be drawn as a shape (e.g., rectangle) with a solid black border and pastel background. DO NOT leave text floating without a border box. Reject any 3D or pseudo-3D styling. No screenshots, no decorative elements. PURE 2D FLAT DESIGN ONLY.
`

---

### 图 3 项目利益相关者图

`	ext
Create a high-end, strict 2D engineering diagram for a professional software engineering document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background.
Color Palette & Borders: High-contrast engineering. Use PURE BLACK (#000000) for ALL text, connecting lines, and arrowheads. EVERY SINGLE INDIVIDUAL NODE MUST have a solid black 1px border/outline. Do not leave any node text floating without a visible rectangular or rounded-rectangular boundary. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes.
Containers: ABSOLUTELY NO large grouping boxes enclosing multiple nodes, NO dashed boundaries beneath nodes. Standalone nodes only.
Aesthetics: ABSOLUTELY NO 3D, NO TRAYS, NO BASES. Draw the UML nodes directly on the empty white canvas. NEVER draw a secondary box, dashed box, or shadow underneath the nodes. Focus heavily on 'Code Architecture' and technical rigor.
Layout & Connections: COMPACT UML FLOWCHART STYLE. Grid-based pixel-perfect alignment with tight, compact node spacing. ONLY use strictly ORTHOGONAL lines (straight vertical/horizontal lines with explicit 90-degree right-angle turns). Absolutely NO diagonal lines. Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows.
Typography constraint: MUST USE EXACT TEXT as provided in the nodes/connections list. DO NOT translate, DO NOT reformat, DO NOT generate new labels. Copy the exact text provided (e.g. "EnglishCodeName (中文注释)").

Figure Subject:
项目利益相关者图

Diagram type:
Compact UML Use Case & Actor Diagram

Layout:
STRICTLY TOP-TO-BOTTOM VERTICAL TREE LAYOUT. ProjectManager stands rigidly at the top, delegating downwards into stakeholders through explicit 90-degree orthogonal line branches. EVERY node MUST be drawn inside a solid black rectangular box.

Mandatory nodes:
- ProjectManager (项目经理)
- EvaluatingTeachers (评审教师组)
- DevTeamMembers (开发小组成员)
- EndUsers (系统最终用户)
- CourseRequirements (课程评分标准)
- ArchGroup (架构与主链路组)
- StorageGroup (存储与回放组)
- UiRenderGroup (UI与渲染组)
- AlgoAlarmGroup (算法与报警组)
- TestDocGroup (测试与文档组)

Mandatory connections:
- ProjectManager (项目经理) -> EvaluatingTeachers (评审教师组)
- ProjectManager (项目经理) -> DevTeamMembers (开发小组成员)
- ProjectManager (项目经理) -> EndUsers (系统最终用户)
- ProjectManager (项目经理) -> CourseRequirements (课程评分标准)
- DevTeamMembers (开发小组成员) -> ArchGroup (架构与主链路组)
- DevTeamMembers (开发小组成员) -> StorageGroup (存储与回放组)
- DevTeamMembers (开发小组成员) -> UiRenderGroup (UI与渲染组)
- DevTeamMembers (开发小组成员) -> AlgoAlarmGroup (算法与报警组)
- DevTeamMembers (开发小组成员) -> TestDocGroup (测试与文档组)

Negative constraints:
CRITICAL: DO NOT draw any trays, platforms, dashed outlines, or secondary boxes beneath the text nodes. Each node MUST be drawn as a shape (e.g., rectangle) with a solid black border and pastel background. DO NOT leave text floating without a border box. Reject any 3D or pseudo-3D styling. No screenshots, no decorative elements. PURE 2D FLAT DESIGN ONLY.
`

---

### 图 4 项目建设范围图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
项目建设范围图

Diagram type:
Scope boundary diagram

Layout:
Use exactly 3 vertical sections from left to right:
1. 首版范围
2. 增强实现
3. 研究预留

Mandatory nodes:
首版范围:
- 信号模拟
- 实时曲线
- 基础统计
- 阈值报警
- CSV 异步记录
- 历史回放
- 三级页面展示

增强实现:
- IIR/FIR
- 高频记录增强
- 性能优化

研究预留:
- TDMS/Binary
- 更底层 GPU 渲染优化
- 复杂压缩
- 高级异常检测

Mandatory connections:
No arrows required except a light progression arrow from 首版范围 -> 增强实现 -> 研究预留.

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No concentric circles.
No mixed hierarchy and timeline in one image.
```

---

### 图 5 系统总用例图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
系统总用例图

Diagram type:
UML use case diagram

Layout:
Actor on the left.
One system boundary rectangle on the right.
Use cases arranged in 3 rows inside the boundary.

Layout aesthetics: Place primary use cases in a left column inside the boundary. Place secondary (included/extended) use cases in a right column. Ensure all lines (both solid and dashed) are straight angular lines (no curves). Use clear arrowheads for all <<include>> and <<extend>> dashed lines. No overlapping lines.
Layout aesthetics: Place primary use cases in a left column inside the boundary. Place secondary (included/extended) use cases in a right column. Ensure all lines (both solid and dashed) are straight angular lines (no curves). Use clear arrowheads for all <<include>> and <<extend>> dashed lines. No overlapping lines.
Mandatory nodes:
Actors:
- 操作员
- 文件系统

System boundary label:
- 实时数据监控与智能分析模拟系统

Use cases:
- 配置参数
- 启动模拟
- 停止模拟
- 浏览实时数据
- 统管设备与通道
- 管理记录与回放
- 设置报警阈值

Mandatory connections:
- 操作员 -> 启动模拟
- 操作员 -> 停止模拟
- 操作员 -> 配置参数
- 操作员 -> 浏览实时数据
- 操作员 -> 统管设备与通道
- 操作员 -> 管理记录与回放
- 操作员 -> 设置报警阈值
- 管理记录与回放 <.. 文件系统
- 导出文件 <.. 文件系统
- 启动模拟 ..> 配置参数 : <<include>>
- 统管设备与通道 ..> 浏览实时数据 : <<extend>>
- All <<include>> and <<extend>> must use dashed arrows and stereotype labels.

Text rules:
CRITICAL UML USE CASE RULE: MUST draw a large System Boundary Box. ALL Actors (Stick figures) go OUTSIDE the boundary. ALL Use Cases (Ovals) go INSIDE. Use dashed open arrows for <<include>>/<<extend>>.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No class boxes.
No flowchart arrows.
No more than 2 actors.
```

---

### 图 6 信号模拟与监控用例图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
信号模拟与监控用例图

Diagram type:
UML use case diagram

Layout:
Actor on the left, one system boundary on the right.
Inside the boundary, group use cases into 3 clusters.

Layout aesthetics: Place primary use cases in a left column inside the boundary. Place secondary (included/extended) use cases in a right column. Ensure all lines (both solid and dashed) are straight angular lines (no curves). Use clear arrowheads for all <<include>> and <<extend>> dashed lines. No overlapping lines.
Layout aesthetics: Place primary use cases in a left column inside the boundary. Place secondary (included/extended) use cases in a right column. Ensure all lines (both solid and dashed) are straight angular lines (no curves). Use clear arrowheads for all <<include>> and <<extend>> dashed lines. No overlapping lines.
Mandatory nodes:
Actor:
- 操作员

System boundary:
- 信号模拟与监控模块

Use case cluster 1:
- 配置信号
- 选择波形
- 设置频率
- 设置幅值
- 设置噪声

Use case cluster 2:
- 启动模拟
- 停止模拟

Use case cluster 3:
- 查看总览
- 查看设备
- 查看通道
- 查看统计
- 查看频谱
- 设置报警阈值

Mandatory connections:
- 操作员 -> 配置信号
- 操作员 -> 启动模拟
- 操作员 -> 停止模拟
- 操作员 -> 查看总览
- 操作员 -> 查看设备
- 操作员 -> 查看通道
- 操作员 -> 设置报警阈值
- 配置信号 ..> 选择波形 : <<include>>
- 配置信号 ..> 设置频率 : <<include>>
- 配置信号 ..> 设置幅值 : <<include>>
- 配置信号 ..> 设置噪声 : <<include>>
- 查看统计 ..> 查看总览 : <<extend>>
- 查看频谱 ..> 查看通道 : <<extend>>
- All <<include>> and <<extend>> must use dashed arrows and stereotype labels.

Text rules:
CRITICAL UML USE CASE RULE: MUST draw a large System Boundary Box. ALL Actors (Stick figures) go OUTSIDE the boundary. ALL Use Cases (Ovals) go INSIDE. Use dashed open arrows for <<include>>/<<extend>>.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No secondary actors.
Clearly render <<include>> and <<extend>> stereotypes on dashed lines.
```

---

### 图 7 记录与回放用例图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
记录与回放用例图

Diagram type:
UML use case diagram

Layout:
Actor on the left, optional second actor lower left, system boundary on the right.

Layout aesthetics: Place primary use cases in a left column inside the boundary. Place secondary (included/extended) use cases in a right column. Ensure all lines (both solid and dashed) are straight angular lines (no curves). Use clear arrowheads for all <<include>> and <<extend>> dashed lines. No overlapping lines.
Layout aesthetics: Place primary use cases in a left column inside the boundary. Place secondary (included/extended) use cases in a right column. Ensure all lines (both solid and dashed) are straight angular lines (no curves). Use clear arrowheads for all <<include>> and <<extend>> dashed lines. No overlapping lines.
Mandatory nodes:
Actors:
- 操作员
- 文件系统

System boundary:
- 记录与回放模块

Use cases:
- 开始记录
- 停止记录
- 导出 CSV
- 选择回放文件
- 开始回放
- 暂停回放
- 停止回放
- 切换时间窗
- 按设备筛选
- 按通道筛选

Mandatory connections:
- 操作员 -> 开始记录
- 操作员 -> 停止记录
- 操作员 -> 开始回放
- 操作员 -> 暂停回放
- 操作员 -> 停止回放
- 操作员 -> 导出 CSV
- 操作员 -> 选择回放文件
- 导出 CSV <.. 文件系统
- 选择回放文件 <.. 文件系统
- 读取历史文件 <.. 文件系统
- 开始回放 ..> 选择回放文件 : <<include>>
- 开始回放 ..> 读取历史文件 : <<include>>
- 切换时间窗 ..> 开始回放 : <<extend>>
- 按设备筛选 ..> 开始回放 : <<extend>>
- 按通道筛选 ..> 开始回放 : <<extend>>
- All <<include>> and <<extend>> must use dashed arrows and stereotype labels.

Text rules:
CRITICAL UML USE CASE RULE: MUST draw a large System Boundary Box. ALL Actors (Stick figures) go OUTSIDE the boundary. ALL Use Cases (Ovals) go INSIDE. Use dashed open arrows for <<include>>/<<extend>>.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No decorative file icons.
No more than 2 actors.
```

---

### 图 8 系统业务流程图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
系统业务流程图

Diagram type:
UML activity diagram

Layout:
Strictly vertical portrait layout (top-to-bottom pipeline). Do NOT draw left-to-right. Use diamond decision nodes and clear branching Yes/No paths.

Mandatory nodes:
- 启动系统 (Start node, solid circle)
- 配置应用参数 (Action)
- 启动信号模拟与采集 (Action)
- 实时读取数据块 (Action)
- [判断]是否满足报警条件? (Decision diamond)
- 触发界面报警与日志 (Action)
- 更新UI缓存与显示 (Action)
- [判断]是否开启记录? (Decision diamond)
- 异步写入数据文件 (Action)
- [判断]是否停止运行? (Decision diamond)
- 结束系统 (End node, bullseye)

Mandatory connections:
- 启动系统 -> 配置应用参数 -> 启动信号模拟与采集 -> 实时读取数据块 -> [判断]是否满足报警条件?
- [判断]是否满足报警条件? -->|Yes| 触发界面报警与日志 -> 更新UI缓存与显示
- [判断]是否满足报警条件? -->|No| 更新UI缓存与显示
- 更新UI缓存与显示 -> [判断]是否开启记录?
- [判断]是否开启记录? -->|Yes| 异步写入数据文件 -> [判断]是否停止运行?
- [判断]是否开启记录? -->|No| [判断]是否停止运行?
- [判断]是否停止运行? -->|No| 实时读取数据块
- [判断]是否停止运行? -->|Yes| 结束系统

Text rules:
CRITICAL UML ACTIVITY RULE: MUST include a standard Initial Node (Solid Black Circle) at the start and an Activity Final Node (Bullseye/Circle) at the end. Use Diamond shapes for decisions with [guard conditions].

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No UML notation.
No circular layout.
```

---

### 图 9 系统上下文数据流图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
系统上下文数据流图

Diagram type:
Yourdon/DeMarco standard Level-0 Context Data Flow Diagram (DFD).

Layout:
One large central process in the middle, external entities radially distributed around it.

Mandatory nodes:
Central process (A single rectangular box):
- P0 实时数据监控与智能分析模拟系统

External entities (Square boxes):
- E1 操作员
- E2 文件磁盘系统
- E3 外部硬件设备

Mandatory flows (Directed edges with data payload labels):
- E1 操作员 -->|配置与控制指令| P0 实时数据监控与智能分析模拟系统
- P0 实时数据监控与智能分析模拟系统 -->|系统状态与告警画面| E1 操作员
- P0 实时数据监控与智能分析模拟系统 -->|连续流数据文件| E2 文件磁盘系统
- E2 文件磁盘系统 -->|历史数据块| P0 实时数据监控与智能分析模拟系统
- E3 外部硬件设备 -->|模拟采样数据| P0 实时数据监控与智能分析模拟系统

Text rules:
CRITICAL DFD RULE: An External Entity MUST NEVER connect directly to a Data Store. Processes (Circles/Rounded rects) must mediate all data flows. Label flows with nouns.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
Absolutely NO direct connections between External Entities.
Absolutely NO data stores in a Level-0 Context DFD.
Absolutely NO unlabelled arrows.
Absolutely NO UML actors (stick figures).
``
```

---

### 图 10 一级数据流图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
一级数据流图

Diagram type:
Yourdon/DeMarco standard Level-1 Data Flow Diagram (DFD).

Layout:
Entities on borders, Processes (as rectangular boxes) in center, Data stores horizontally placed. strictly directional edges with NO bidirectional arrows.

Mandatory nodes:
External entities (Square boxes):
- E1 操作员

Processes (Rectangular boxes):
- P1 信号生成
- P2 实时处理
- P3 统计分析
- P4 报警处理
- P5 图形显示
- P6 文件记录
- P7 历史回放

Data stores (Open-ended rectangles/Two parallel lines):
- D1 实时缓存
- D2 历史文件库

Mandatory flows (Directed edges with data labels):
- E1 操作员 -->|配置参数| P1 信号生成
- P1 信号生成 -->|模拟信号流| P2 实时处理
- P2 实时处理 -->|处理后数据流| D1 实时缓存
- P2 实时处理 -->|落盘数据块| P6 文件记录
- P6 文件记录 -->|存储文件| D2 历史文件库
- D1 实时缓存 -->|最近时间窗数据| P3 统计分析
- P3 统计分析 -->|异常状态事件| P4 报警处理
- P3 统计分析 -->|分析结果| P5 图形显示
- P4 报警处理 -->|界面报警提示| E1 操作员
- E1 操作员 -->|回放查询指令| P7 历史回放
- D2 历史文件库 -->|历史数据| P7 历史回放
- P7 历史回放 -->|回放坐标点| P5 图形显示
- P5 图形显示 -->|用户可视画面| E1 操作员

Text rules:
CRITICAL DFD RULE: An External Entity MUST NEVER connect directly to a Data Store. Processes (Circles/Rounded rects) must mediate all data flows. Label flows with nouns.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
Absolutely NO direct connections between an External Entity and a Data Store.
Absolutely NO direct connections between two Data Stores.
Absolutely NO unlabelled arrows. NO bidirectional arrows.
Absolutely NO UML actors (stick figures).
``
```

---

### 图 11 系统总体架构图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly clean, non-overlapping orthogonal routing (right-angled lines) to optimize edge flows and prevent messy crossovers. Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Emphasize clear spacing between connecting lines to enhance readability. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
系统总体架构图

Diagram type:
Strict 2D layered software architecture diagram

Layout:
Use exactly 4 horizontal layers stacked from top to bottom in this order:
1. 应用层 (App)
2. 基础设施层 (Infrastructure)
3. 核心层 (Core)
4. 领域层 (Domain)

Mandatory nodes:
应用层 (App):
- MainWindow
- OverviewViewModel
- DeviceViewModel
- ChannelDetailViewModel

基础设施层 (Infrastructure):
- SignalGenerator
- CsvWriter
- HistoryReader
- ConfigProvider

核心层 (Core):
- StatisticsService
- FftService
- AlarmService
- CacheManager
- ReplayController
- Scheduler

领域层 (Domain):
- Device
- Channel
- SampleBlock
- StatisticsSnapshot
- SpectrumFrame
- AlarmState

Mandatory connections:
- 应用层 (App) -> 核心层 (Core)
- 基础设施层 (Infrastructure) -> 核心层 (Core)
- 核心层 (Core) -> 领域层 (Domain)
- No direct 应用层 (App) -> 领域层 (Domain)
- No 领域层 (Domain) -> 基础设施层 (Infrastructure)

Text rules:
Layer names MUST be bilingual strictly formatted as "Chinese Name (English Name)".
Module names must stay exact.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No extra layers.
No random floating boxes.
No decorative cloud/database icons unless minimal.
```

---

### 图 12 单窗口三级展示结构图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
单窗口三级展示结构图

Diagram type:
UI structure diagram

Layout:
Use one large outer window rectangle.
Split into left control area and right content area.
Inside right content area show 3 main views.

Mandatory nodes:
- 主窗口
- 左侧控制区
- 右侧内容区
- 总览页
- 设备页
- 通道分析页

Mandatory connections:
- 主窗口 contains 左侧控制区 and 右侧内容区
- 右侧内容区 contains 总览页, 设备页, 通道分析页
- Navigation path: 总览页 -> 设备页 -> 通道分析页

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No high-fidelity UI.
No color-rich dashboard appearance.
```

---

### 图 13 系统运行时数据流图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
系统运行时数据流图

Diagram type:
Data flow diagram with horizontal swimlanes.

Layout:
Split the image into two horizontal lanes explicitly labelled:
Top lane = '实时模式 (Real-time Mode)'
Bottom lane = '回放模式 (Replay Mode)'

Mandatory nodes:
Realtime lane:
- (Source) 信号源数据接入
- (Queue) 实时环形缓存
- (Process) 统计与时频分析
- (Process) 报警逻辑判断
- (Sink) 图形界面渲染
- (DataStore) 异步存储记录

Replay lane:
- (DataStore) 本地历史文件
- (Source) 历史阅读器解析
- (Process) 回放进度与速度控制
- (Sink) 复用图形界面渲染

Mandatory connections:
- 信号源数据接入 -->|高速采样数据流| 实时环形缓存
- 实时环形缓存 -->|按时间窗获取数据| 统计与时频分析
- 统计与时频分析 -->|计算参数阈值| 报警逻辑判断
- 报警逻辑判断 -->|报警状态事件| 图形界面渲染
- 统计与时频分析 -->|波形/FFT矩阵| 图形界面渲染
- 实时环形缓存 -->|批量落盘数据| 异步存储记录
- 本地历史文件 -->|历史二进制数据块| 历史阅读器解析
- 历史阅读器解析 -->|抽显/完整波形数据| 回放进度与速度控制
- 回放进度与速度控制 -->|时间坐标对齐帧| 复用图形界面渲染

Text rules:
CRITICAL DFD RULE: An External Entity MUST NEVER connect directly to a Data Store. Processes (Circles/Rounded rects) must mediate all data flows. Label flows with nouns.
Use explicitly labeled, straight arrow connections. Describe the data payload matching the connections above.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
Do not intertwine Realtime and Replay pipelines.
No UML stick figures.
No empty strings on arrows.
``
```

---

### 图 14 实时处理与并发控制总体图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
实时处理与并发控制总体图

Diagram type:
Concurrent processing architecture diagram

Layout:
Use a left-to-right pipeline with 4 thread groups and a central sharded processing area.

Mandatory nodes:
- 数据生成线程
- 接入队列
- 数据处理线程
- Shard 1
- Shard 2
- Shard N
- 统计分析
- 报警判断
- UI 快照队列
- 记录队列
- 文件写入线程
- UI 刷新线程

Mandatory connections:
- 数据生成线程 -> 接入队列 -> 数据处理线程
- 数据处理线程 -> Shard 1 / Shard 2 / Shard N
- Shard blocks -> 统计分析
- 统计分析 -> 报警判断
- 统计分析 -> UI 快照队列 -> UI 刷新线程
- Shard blocks -> 记录队列 -> 文件写入线程

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No single-thread interpretation.
No more than 3 shard example blocks.
```

---

### 图 15 队列与背压控制图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly clean, non-overlapping orthogonal routing (right-angled lines) Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
队列与背压控制图

Diagram type:
Strict 2D Structural Flow (no 3D queue cylinders)

Layout:
Use a highly compact, horizontal pipeline 2D block layout flowing STRICTLY Left-to-Right.
Organize into 4 parallel horizontal functional zones (swimlanes), wrapped in dashed boundary boxes with very light transparent backgrounds:
- Zone 1: 数据接入层 (Data Ingest Layer) - Top lane
- Zone 2: 核心分析层 (Core Analysis Layer) - Upper-middle lane
- Zone 3: 持久化存储层 (Persistence Storage Layer) - Lower-middle lane
- Zone 4: 实时展示层 (Real-time UI Layer) - Bottom lane
Critically: Embed the 'Backpressure Strategies (背压策略)' directly as attached sticky sub-tags securely bound to the bottom border of the 'Queues (队列)'. Keep all routing strictly orthogonal and cleanly organized.

Mandatory nodes:
Zone 1 - Ingest Layer Nodes:
- 硬件端 (Hardware Device)
- 驱动采集模块 (Driver Endpoint)
- 接入缓冲队列 (Ingest Buffer Queue)
- 数据解析器 (Data Parser)
- 流量分发路由器 (Dispatcher Router)

Zone 2 - Analysis Layer Nodes:
- 分析任务队列 (Analysis Task Queue)
- 并发分析引擎 (Concurrent Analysis Engine)

Zone 3 - Storage Layer Nodes:
- 记录刷盘队列 (Record IO Queue)
- 高速存储模块 (Storage Module)
- 时序数据库 (Time-Series DB)

Zone 4 - UI Layer Nodes:
- UI 快照队列 (UI Snapshot Queue)
- 渲染推送网关 (Render Push Gateway)
- 客户端界面 (Client UI Viewer)

Backpressure Strategies (Tag tightly to Queues):
- 策略 1: 流量整形与限流 (Traffic Shaping & Rate Limit)
- 策略 2: 自适应负载丢弃 (Adaptive Load Drop)
- 策略 3: 内存池积攒批量写入 (Memory Pool & Batch Write)
- 策略 4: 无锁覆盖旧数据并降帧 (Lock-Free Overwrite & Reduce FPS)

Mandatory connections:
# Core Main Flow
- 硬件端 (Hardware Device) -> 驱动采集模块 (Driver Endpoint) -> 接入缓冲队列 (Ingest Buffer Queue) -> 数据解析器 (Data Parser) -> 流量分发路由器 (Dispatcher Router)

# Parallel Forks from Dispatcher
- 流量分发路由器 (Dispatcher Router) -> 分析任务队列 (Analysis Task Queue) -> 并发分析引擎 (Concurrent Analysis Engine)
- 流量分发路由器 (Dispatcher Router) -> 记录刷盘队列 (Record IO Queue) -> 高速存储模块 (Storage Module) -> 时序数据库 (Time-Series DB)
- 流量分发路由器 (Dispatcher Router) -> UI 快照队列 (UI Snapshot Queue) -> 渲染推送网关 (Render Push Gateway) -> 客户端界面 (Client UI Viewer)

# Strategy Bindings (Draw as sticky sub-boxes below queues)
- 接入缓冲队列 (Ingest Buffer Queue) -> 策略 1: 流量整形与限流
- 分析任务队列 (Analysis Task Queue) -> 策略 2: 自适应负载丢弃
- 记录刷盘队列 (Record IO Queue) -> 策略 3: 内存池积攒批量写入
- UI 快照队列 (UI Snapshot Queue) -> 策略 4: 无锁覆盖旧数据并降帧

Text rules:
Modules use Soft Tech Blue backgrounds.
Queues use Pale Gray backgrounds.
Strategies MUST be attached/clamped tightly to their queues, drawn as warning/rule tags with pale orange or distinct background. Nodes must be identical rounded rectangles. Ensure perfect alignment.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No fancy gauges.
No random queue icons.
```

---

### 图 16 分层缓存结构图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
分层缓存结构图

Diagram type:
Layered cache architecture diagram

Layout:
Use exactly 4 stacked layers from top to bottom.

Mandatory nodes:
- 短时原始缓存
- 选中通道高精度缓存
- 长时聚合摘要缓存
- 历史文件数据

Side annotations:
- 统计分析
- 高频显示
- 总览与设备页趋势显示
- 历史回放

Mandatory connections:
- Layer usage notes connected to the corresponding cache layer
- Light downward progression arrows between layers

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No database server style.
No 3D stacked cylinders.
```

---

### 图 17 三级页面绘制粒度对比图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
三级页面绘制粒度对比图

Diagram type:
Three-panel comparison diagram

Layout:
Use exactly 3 vertical panels from left to right.

Mandatory nodes:
Panel 1:
- 总览页
- 设备级摘要
- 长时聚合缓存

Panel 2:
- 设备页
- 多通道聚合趋势
- 聚合摘要缓存

Panel 3:
- 通道分析页
- 高精度时域 + 频谱
- 原始缓存 + 高精度缓存

Mandatory connections:
Use left-to-right directional cue showing increasing detail.

Text rules:
The visual complexity should clearly increase from left to right.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No screenshot-like UI.
No unrelated widgets.
```

---

### 图 18 核心领域类图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
核心领域类图

Diagram type:
UML class diagram

Layout:
Use a centered class diagram with Device at upper left, Channel under Device, SampleBlock in the center, result classes on the right, persistence-related classes at lower area.

Mandatory classes:
- Device
- Channel
- SampleBlock
- StatisticsSnapshot
- SpectrumFrame
- AlarmState
- RecordingTask
- HistoryReader

Mandatory 3-Compartment Class Details (MUST draw Name, Attributes, and Methods compartments for EVERY class):
- Class: Device
  Attributes: +DeviceId: Guid, +DeviceName: string
  Methods: +Connect(): void, +Disconnect(): void
- Class: Channel
  Attributes: +ChannelId: int, +SampleRate: double
  Methods: +StartSample(): void, +StopSample(): void
- Class: SampleBlock
  Attributes: +StartTime: DateTime, +SampleCount: int
  Methods: +GetBuffer(): double[]
- Class: StatisticsSnapshot
  Attributes: +Max: double, +Min: double, +Mean: double
  Methods: +CompareThreshold(): bool
- Class: SpectrumFrame
  Attributes: +FrequencyBins: double[], +Amplitude: double[]
  Methods: +GetPeak(): double
- Class: AlarmState
  Attributes: +Threshold: double, +State: Enum
  Methods: +TriggerAlarm(): void
- Class: RecordingTask
  Attributes: +TaskId: string, +IsActive: bool
  Methods: +Execute(): void
- Class: HistoryReader
  Attributes: +FilePath: string
  Methods: +ReadBlock(): SampleBlock

Mandatory relationships:
Use strict UML standard relation arrows exactly matching the class names provided:
- Device "1" *-- "*" Channel: Composition
- Channel "1" *-- "*" SampleBlock: Composition
- Channel "1" *-- "*" StatisticsSnapshot: Composition
- Channel "1" *-- "*" SpectrumFrame: Composition
- Channel "1" *-- "*" AlarmState: Composition
- RecordingTask "1" o-- "*" SampleBlock: Aggregation
- HistoryReader --> SampleBlock: Dependency (reads)

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No sequence arrows.
No ER diagram notation.
```

---

### 图 19 分析服务类图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
分析服务类图

Diagram type:
UML class diagram

Layout:
Use a strictly formal UML Class Diagram structural layout. Force explicit 3-compartment UML class boxes (Class Name, Attributes, Operations) with solid horizontal separator lines. Place the interface "IAnalysisService" at the top. Place the four service classes (StatisticsService, FftService, FilterService, AlarmService) below it as implementations. Place the data classes (SampleBlock, StatisticsSnapshot, etc.) connected as parameters/returns.

Mandatory classes:
- <<interface>> IAnalysisService
- StatisticsService
- FftService
- FilterService
- AlarmService
- SampleBlock
- StatisticsSnapshot
- SpectrumFrame
- AlarmState

Mandatory 3-Compartment Class Details (MUST draw Name, Attributes, and Methods compartments for EVERY class):
- Class: <<interface>> IAnalysisService
  Attributes: +ServiceId: Guid
  Methods: +Process(block: SampleBlock): void
- Class: StatisticsService
  Attributes: +Config: TargetEnum
  Methods: +Calculate(block): StatisticsSnapshot
- Class: FftService
  Attributes: +WindowType: Enum
  Methods: +ComputeSpectrum(block): SpectrumFrame
- Class: FilterService
  Attributes: +CutoffFrequency: double
  Methods: +ApplyFilter(block): SampleBlock
- Class: AlarmService
  Attributes: +ActiveRules: List
  Methods: +Evaluate(snapshot): AlarmState
- Class: SampleBlock
  Attributes: +Buffer: double[], +StartTime: DateTime
  Methods: +Clone(): SampleBlock
- Class: StatisticsSnapshot
  Attributes: +Max: double, +Mean: double
  Methods: +Serialize(): string
- Class: SpectrumFrame
  Attributes: +FrequencyBins: double[]
  Methods: +Normalize(): void
- Class: AlarmState
  Attributes: +IsTriggered: bool, +Message: string
  Methods: +Acknowledge(): void

Mandatory relationships:
Use strictly standard UML connectors (solid lines with hollow triangles for inheritance/realization, dashed arrows for dependency):
- StatisticsService ..|> IAnalysisService : Realization / Implements
- FftService ..|> IAnalysisService : Realization / Implements
- FilterService ..|> IAnalysisService : Realization / Implements
- AlarmService ..|> IAnalysisService : Realization / Implements
- StatisticsService ..> SampleBlock : <<use>>
- FftService ..> SampleBlock : <<use>>
- FilterService ..> SampleBlock : <<use>>
- StatisticsService ..> StatisticsSnapshot : <<create>>
- FftService ..> SpectrumFrame : <<create>>
- AlarmService ..> AlarmState : <<create>>

Text rules:
Service names must remain in English.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
CRITICAL: MUST draw an exact Inheritance/Realization tree with hollow triangle arrowheads pointing to IAnalysisService.
No more than the listed classes.
```

---

### 图 20 存储与回放类图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
存储与回放类图

Diagram type:
UML class diagram

Layout:
Use a top-down and left-to-right organized UML class diagram.
Top tier: RecordingService, ReplayController
Middle tier: RecordingTask, HistoryReader
Bottom tier: CsvWriter, TdmsWriter, EnhancedWriter (align horizontally)

Mandatory classes:
- RecordingService
- CsvWriter
- TdmsWriter
- EnhancedWriter
- HistoryReader
- ReplayController
- RecordingTask

Mandatory 3-Compartment Class Details (MUST draw Name, Attributes, and Methods compartments for EVERY class):
- Class: RecordingService
  Attributes: +ActiveTasks: int
  Methods: +StartRecording(), +StopRecording()
- Class: RecordingTask
  Attributes: +TaskId: string, +FilePath: string
  Methods: +ValidatePath(): bool
- Class: CsvWriter
  Attributes: +Delimiter: char
  Methods: +WriteChunk(data)
- Class: TdmsWriter
  Attributes: +FileVersion: int
  Methods: +WriteChunk(data)
- Class: EnhancedWriter
  Attributes: +BufferSize: int
  Methods: +WriteOptimized(data)
- Class: HistoryReader
  Attributes: +ReadCursor: long
  Methods: +ReadChunk(timeRange)
- Class: ReplayController
  Attributes: +SpeedMultiplier: double
  Methods: +Play(), +Pause(), +JumpTo(time)

Mandatory relationships:
Use strict UML standard relation arrows exactly matching the class names provided:
- RecordingService "1" *-- "*" RecordingTask: Composition
- RecordingService --> CsvWriter: Dependency
- RecordingService --> TdmsWriter: Dependency
- RecordingService --> EnhancedWriter: Dependency
- ReplayController --> HistoryReader: Dependency
- HistoryReader --> RecordingTask: Dependency

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No database schema style.
No missing connection labels.
```

---

### 图 21 界面与 ViewModel 类图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
界面与 ViewModel 类图

Diagram type:
UML class diagram

Layout:
Use a top-down hierarchical UML layout.
Top tier: MainWindow
Middle tier: OverviewViewModel, DeviceViewModel, ChannelDetailViewModel (align horizontally)
Bottom tier: ViewModelBase (or place ViewModelBase at the top of the ViewModels, properly aligned)

Mandatory classes:
- MainWindow
- OverviewViewModel
- DeviceViewModel
- ChannelDetailViewModel
- ViewModelBase

Mandatory 3-Compartment Class Details (MUST draw Name, Attributes, and Methods compartments for EVERY class):
- Class: MainWindow
  Attributes: +ThemeMode: string
  Methods: +InitializeComponent(), +BindDataContext()
- Class: OverviewViewModel
  Attributes: +Devices: List, +TotalAlarms: int
  Methods: +UpdateGlobalStats()
- Class: DeviceViewModel
  Attributes: +DeviceId: Guid, +IsOnline: bool
  Methods: +SelectDevice(id), +RefreshStatus()
- Class: ChannelDetailViewModel
  Attributes: +CurrentChannel: Channel, +ZoomLevel: double
  Methods: +ZoomIn(), +ZoomOut()
- Class: ViewModelBase
  Attributes: +IsBusy: bool
  Methods: +OnPropertyChanged(name)

Mandatory relationships:
Use strict UML standard relation arrows exactly matching the class names provided:
- MainWindow "1" *-- "1" OverviewViewModel : Composition
- MainWindow "1" *-- "1" DeviceViewModel : Composition
- MainWindow "1" *-- "1" ChannelDetailViewModel : Composition
- OverviewViewModel --|> ViewModelBase : Inheritance
- DeviceViewModel --|> ViewModelBase : Inheritance
- ChannelDetailViewModel --|> ViewModelBase : Inheritance

Text rules:
English class names exactly as listed.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No UI screenshot appearance.
```

---

### 图 22 FFT 频谱分析流程图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
FFT 频谱分析流程图

Diagram type:
UML activity diagram

Layout:
Top-to-bottom workflow with specific decision nodes.

Mandatory nodes:
- 开始分析 (Start, solid circle)
- 捕获时域窗口数据 (Action)
- 应用汉宁窗 (Action)
- 执行FFT变换 (Action)
- 计算幅度谱 (Action)
- [判断]是否存在明显峰值? (Decision diamond)
- 标记主频与谐波 (Action)
- 提取频带能量 (Action)
- 结束分析 (End, bullseye)

Mandatory connections:
- 开始分析 -> 捕获时域窗口数据 -> 应用汉宁窗 -> 执行FFT变换 -> 计算幅度谱 -> [判断]是否存在明显峰值?
- [判断]是否存在明显峰值? -->|Yes| 标记主频与谐波 -> 提取频带能量
- [判断]是否存在明显峰值? -->|No| 提取频带能量
- 提取频带能量 -> 结束分析

Text rules:
CRITICAL UML ACTIVITY RULE: MUST include a standard Initial Node (Solid Black Circle) at the start and an Activity Final Node (Bullseye/Circle) at the end. Use Diamond shapes for decisions with [guard conditions].

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No DSP waveform background.
No oscilloscope decoration.
```

---

### 图 23 报警引擎状态机图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
报警引擎状态机图

Diagram type:
Finite-state machine diagram

Layout:
Use a standard UML State Machine Diagram layout with circular or distinct state nodes (flat rounded rectangles).
Draw the Initial State (solid black circle) pointing to the '正常 (Normal)' state.
Arrange states to show a clear progression from Normal -> Warning -> Alarm -> Recovery -> Normal, with feedback loops.

Mandatory states:
- 初始状态 (Initial Start, black dot)
- 正常 (Normal)
- 防抖预警中 (Debounce/Warning)
- 活跃报警 (Active Alarm)
- 滞回恢复中 (Hysteresis Recovery)

Mandatory transitions:
- 初始状态 (Initial Start) -> 正常 (Normal): 系统启动
- 正常 (Normal) -> 防抖预警中 (Debounce/Warning): 采样值 > 触发阈值
- 防抖预警中 (Debounce/Warning) -> 活跃报警 (Active Alarm): 异常持续时间 >= 设定触发窗口
- 防抖预警中 (Debounce/Warning) -> 正常 (Normal): 采样值回落至安全区 (误报过滤)
- 活跃报警 (Active Alarm) -> 滞回恢复中 (Hysteresis Recovery): 采样值 < (触发阈值 - 滞回容差)
- 滞回恢复中 (Hysteresis Recovery) -> 活跃报警 (Active Alarm): 采样值再次 > 触发阈值 (二次触发)
- 滞回恢复中 (Hysteresis Recovery) -> 正常 (Normal): 恢复状态维持时间 >= 设定恢复窗口


Text rules:
Use standard strict UML State Machine Diagram notation. States must be flat rounded rectangles. Use curved or orthogonal standard arrows for transitions. Make transition condition text highly visible.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No flowchart boxes.
No more than 4 states unless a tiny start marker is needed.
```

---

### 图 24 实时处理时序图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
实时处理时序图

Diagram type:
UML sequence diagram

Layout:
Participants from left to right in this exact order:
1. 数据生成线程 (Data Gen Thread)
2. 实时处理线程 (Process Thread)
3. 统计分析服务 (Statistics Service)
4. 报警引擎服务 (Alarm Service)
5. UI快照队列 (UI Snapshot Queue)
6. 记录刷盘队列 (Record Queue)
7. 界面渲染线程 (UI View Thread)

Mandatory messages:
- 数据生成线程 (Data Gen Thread) -> 实时处理线程 (Process Thread): 1. 生成采样数据块 (Generate SampleBlock)
- 实时处理线程 (Process Thread) -> 统计分析服务 (Statistics Service): 2. 调度统计计算 (Compute Statistics)
- 统计分析服务 (Statistics Service) -> 实时处理线程 (Process Thread): 3. 返回统计快照 (Return Snapshot)
- 实时处理线程 (Process Thread) -> 报警引擎服务 (Alarm Service): 4. 发起报警评估 (Evaluate Alarm)
- 报警引擎服务 (Alarm Service) -> 实时处理线程 (Process Thread): 5. 返回报警状态 (Return Alarm State)
- 实时处理线程 (Process Thread) -> UI快照队列 (UI Snapshot Queue): 6. 推送混合快照数据 (Push UI Snapshot)
- 实时处理线程 (Process Thread) -> 记录刷盘队列 (Record Queue): 7. 提交异步写入任务 (Enqueue Record Task)
- UI快照队列 (UI Snapshot Queue) -> 界面渲染线程 (UI View Thread): 8. 触发缓存更新 (Update Cache)
- 界面渲染线程 (UI View Thread) -> 界面渲染线程 (UI View Thread): 9. 界面重绘刷新 (Refresh Screen)


Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No class diagram elements.
No horizontal time direction.
```

---

### 图 25 历史回放时序图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
历史回放时序图

Diagram type:
UML sequence diagram

Layout:
Participants from left to right in exact bilingual order:
1. 操作员 (Operator)
2. 回放控制器 (Replay Controller)
3. 历史数据引擎 (History DB Engine)
4. 核心分析链路 (Core Analysis Pipeline)
5. 界面渲染线程 (UI View Thread)

Mandatory messages (MUST use STRICT UML line styles: Solid lines for Calls, Dashed lines for Returns):
- (Solid line) 操作员 (Operator) -> 回放控制器 (Replay Controller): 1. 加载历史文件 (Load File)
- (Solid line) 回放控制器 (Replay Controller) -> 历史数据引擎 (History DB Engine): 2. 解析文件元数据 (Parse Metadata)
- (Dashed line) 历史数据引擎 (History DB Engine) --> 回放控制器 (Replay Controller): 3. 返回时间范围/通道信息 (Return Meta Info)
- (Solid line) 操作员 (Operator) -> 回放控制器 (Replay Controller): 4. 设置回放时间轴与倍速 (Set Time Window & Speed)
- (Solid line) 操作员 (Operator) -> 回放控制器 (Replay Controller): 5. 启动回放 (Start Playback)
Draw a UML Loop Fragment box named 'Loop (Data Streaming Continuous)' around the following messages 6 to 10:
- (Solid line) 回放控制器 (Replay Controller) -> 历史数据引擎 (History DB Engine): 6. [循环]按步长抽取数据切片 (Fetch Data Chunk)
- (Dashed line) 历史数据引擎 (History DB Engine) --> 回放控制器 (Replay Controller): 7. [循环返回]当前切片采样块 (Return Sample Block)
- (Solid line) 回放控制器 (Replay Controller) -> 核心分析链路 (Core Analysis Pipeline): 8. 投递历史数据至分析总线 (Dispatch to Pipeline)
- (Solid line) 核心分析链路 (Core Analysis Pipeline) -> 界面渲染线程 (UI View Thread): 9. 推送离线分析快照 (Push Analysis Snapshot)
- (Solid line loop) 界面渲染线程 (UI View Thread) -> 界面渲染线程 (UI View Thread): 10. 更新回放波形与进度条 (Update Waveform & Progress)
End of Loop Fragment.
- (Dashed line) 历史数据引擎 (History DB Engine) --> 回放控制器 (Replay Controller): 11. [达到终点触发] 发送EOF信号 (Send EOF Event)
- (Solid line) 回放控制器 (Replay Controller) -> 界面渲染线程 (UI View Thread): 12. 广播回放完成状态 (Broadcast Finish Status)

Text rules:
Show clear top-to-bottom time order. CRITICAL: Use SOLID lines with filled arrowheads for forward calls. Use DASHED lines with open/stick arrowheads for return messages. Draw active execution boxes (activation bars) on lifelines. Draw a clear UML [Loop] fragment container covering steps 6 to 10 to denote continuous streaming!

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No live processing thread participants beyond the listed ones.
```

---

### 图 26 主窗口总体布局图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
主窗口总体布局图

Diagram type:
Low-fidelity UI wireframe

Layout:
One outer application window.
Top title bar.
Left control panel.
Right content panel.

Mandatory regions:
- 标题区
- 左侧控制区
- 参数配置
- 记录控制
- 回放控制
- 右侧内容区
- 总览页
- 设备页
- 通道分析页

Mandatory connections:
The left control panel should visually feed the right content panel.

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No polished product UI.
No gradients.
No charts with real data.
```

---

### 图 27 总览页原型图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
总览页原型图

Diagram type:
Low-fidelity page wireframe

Layout:
Use a dashboard-style grid with 3 major areas.

Mandatory regions:
- 设备状态区
- 报警概览区
- 运行指标区
- 小型摘要趋势区

Text rules:
Use simple labeled boxes.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No realistic polished dashboard.
No dense tiny widgets.
```

---

### 图 28 设备页原型图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
设备页原型图

Diagram type:
Low-fidelity page wireframe

Layout:
Top information area, central multi-channel trend area, side or bottom statistics area.

Mandatory regions:
- 设备信息区
- 多通道趋势区
- 设备级统计区

Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No high-fidelity line chart rendering.
```

---

### 图 29 通道分析页原型图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
通道分析页原型图

Diagram type:
Low-fidelity page wireframe

Layout:
Large waveform area on top-left, spectrum area on top-right or lower-right, control and information panels around it.

Mandatory regions:
- 高精度时域波形区
- 频谱图区
- 统计信息区
- 报警信息区
- 记录/回放控制区

Text rules:
This page must visually read as a detailed analysis page.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No dashboard overview layout.
No realistic chart styling.
```

---

### 图 30 敏捷开发流程图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
敏捷开发流程图

Diagram type:
Cyclic workflow diagram

Layout:
Use a highly professional, strict 2D Agile/Scrum process pipeline layout flowing from left to right, containing a clear iterative cycle in the middle.
Divide the canvas into 3 distinct logical zones (Swimlanes or Group Bounds):
- Zone 1 (Left): 【需求与规划】 (Planning & Backlog)
- Zone 2 (Center): 【迭代冲刺循环】 (Sprint Iteration) - Highlight this as a cyclic iteration area!
- Zone 3 (Right): 【发布与反馈】 (Release & Feedback)

Mandatory nodes (Use bilingual labels):
Zone 1:
- 需求调研与分析 (Requirements Analysis)
- 架构方案设计 (Architecture Design)
- 产品待办列表 (Product Backlog)

Zone 2 (The Agile Loop):
- 迭代计划会议 (Sprint Planning)
- 冲刺待办项 (Sprint Backlog)
- 编码开发 (Coding)
- 单元测试 (Unit Testing)
- 每日站会同步 (Daily Standup)

Zone 3:
- 系统集成联调 (Integration Testing)
- 试运行与交付 (Trial Release)
- 评审与反馈修正 (Retrospective & Feedback)

Mandatory connections:
# Main Flow
- 需求调研与分析 (Requirements Analysis) -> 架构方案设计 (Architecture Design) -> 产品待办列表 (Product Backlog)
- 产品待办列表 (Product Backlog) -> 迭代计划会议 (Sprint Planning) -> 冲刺待办项 (Sprint Backlog)
- 冲刺待办项 (Sprint Backlog) -> 编码开发 (Coding)

# Sprint Cyclic Loop (Inside Zone 2)
- 编码开发 (Coding) -> 单元测试 (Unit Testing) -> 每日站会同步 (Daily Standup) -> 编码开发 (Coding)

# Outflow & Feedback
- 单元测试 (Unit Testing) -> 系统集成联调 (Integration Testing)
- 系统集成联调 (Integration Testing) -> 试运行与交付 (Trial Release) -> 评审与反馈修正 (Retrospective & Feedback)

# Feedback Loops (Dashed lines to indicate continuous improvement)
- 评审与反馈修正 (Retrospective & Feedback) -> [Feedback] 产品待办列表 (Product Backlog)

Text rules:
Keep labels explicitly bilingual. Ensure the central Sprint cyclic loop is visually distinct (e.g., using a grouped box). Nodes must be standard 2D flat rounded rectangles.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes. No messy spaghetti lines; strictly use orthogonal routing.

```

---

### 图 31 项目实施甘特图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
项目实施甘特图

Diagram type:
Standard WBS / PlantUML-style Gantt Chart

Layout:
Horizontal axis = weeks.
Vertical axis = tasks.
Use a clean spreadsheet-like gantt layout.

Mandatory tasks:
- 需求分析
- 总体架构
- 主链路开发
- 多设备多通道页面
- FFT 与频谱
- CSV 记录与回放
- 增强功能
- 联调测试
- 试运行
- 竞标材料整理

Mandatory features:
- At least one milestone marker
- Clear weekly spans

Text rules:
CRITICAL GANTT RULE: Display a strict left-to-right timeline header. Put WBS tasks on the Left Y-axis. Explicitly show milestone markers (Diamonds).

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No 3D bars.
No project-management software screenshot style.
```

---

### 图 32 WBS 工作分解图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
WBS 工作分解图

Diagram type:
Work Breakdown Structure tree diagram

Layout:
Top-down tree with one root, multiple level-2 branches, and visible level-3 branches.

Mandatory nodes:
Root:
- 实时数据监控与智能分析模拟系统项目

Level 2:
- 需求分析
- 总体设计
- 主链路开发
- 算法分析
- 界面与交互
- 存储与回放
- 测试与试运行
- 材料与答辩

Mandatory requirement:
Each level-2 branch must have at least 2 level-3 child tasks.

Mandatory connections:
- Root connected down to all Level-2 branches.
- Each Level-2 branch connected to its Level-3 child tasks.


Mandatory connections:
- Root connected down to all Level-2 branches.
- Each Level-2 branch connected to its Level-3 child tasks.


Mandatory connections:
- Root connected down to all Level-2 branches.
- Each Level-2 branch connected to its Level-3 child tasks.


Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No circular flow.
No org chart styling.
```

---

### 图 33 Git 分支管理流程图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
Git 分支管理流程图

Diagram type:
Standard Enterprise GitFlow Network Diagram

Layout:
Use a strict horizontal Git tree network layout, simulating a professional Git commit history graph from left (past) to right (future).
Organize branches as parallel horizontal lanes (Swimlanes):
- Lane 1 (Top): main (Production & Tags)
- Lane 2 (Middle): develop (Integration)
- Lane 3 (Bottom): feature/* (Local Development)

Mandatory Branches and Commits (Bilingual):
Branch: main (主分支)
- Commits: [Init], [v1.0.0 Release], [v1.1.0 Release]

Branch: develop (开发分支)
- Commits: [Dev Init], [Sprint 1 Merge], [Sprint 2 Merge]

Branch: feature/core (核心功能分支)
- Commits: [Feature A], [Feature B]

Branch: feature/ui (界面功能分支)
- Commits: [UI Draft], [UI Final]

Mandatory connections (Git Branching & Merging):
- main [Init] -> branches off to -> develop [Dev Init]
- develop [Dev Init] -> branches off to -> feature/core [Feature A]
- develop [Dev Init] -> branches off to -> feature/ui [UI Draft]
- feature/core [Feature B] -> MERGES INTO -> develop [Sprint 1 Merge] (Annotation: Pull Request / Code Review)
- feature/ui [UI Final] -> MERGES INTO -> develop [Sprint 2 Merge] (Annotation: Pull Request / Code Review)
- develop [Sprint 2 Merge] -> MERGES INTO -> main [v1.0.0 Release] (Annotation: CI/CD Pipeline)

Text rules:
Keep labels bilingual. Draw commits as solid distinct circles (dots). Draw branch lines as thick horizontal lines connecting the dots.
CRITICAL: Draw merge lines and branch-off connections as strict VERTICAL or ORTHOGONAL lines (90-degree angles only) from one branch's commit to another branch's commit. Absolutely NO diagonal or slanted lines.


Text rules:

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No GitHub UI screenshot appearance.
```

---

### 图 34 项目组织结构图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
项目组织结构图

Diagram type:
Organization chart

Layout:
Top-down hierarchy.

Mandatory nodes:
Top:
- 项目经理

Second level:
- 架构与主链路
- 存储与回放
- UI 与渲染
- 算法与报警
- 测试与文档

Annotation:
- 六人团队

Mandatory connections:
- 项目经理 connected downward to all five role blocks

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No stakeholder map style.
No circular layout.
```

---

### 图 35 项目管理闭环图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
项目管理闭环图

Diagram type:
Enterprise DevOps-style Infinity Loop / 4-Phase Chevron Pipeline (Closed-Loop Management)

Layout:
Do NOT use a pie chart or a simple circle.
Use a high-end modern DevOps-style symmetric infinity loop, OR a distinct 4-block square pipeline connected by sleek 90-degree orthogonal arrows.
The overall structure must look like a professional tech-stack architecture diagram, not a kindergarten wheel.

Mandatory Phases (Bilingual) and Sub-nodes:
Phase 1: 计划 (Plan)
- 目标设定 (Goal Setting)
- 任务拆分 (Task Breakdown)
- 资源排期 (Allocation)

Phase 2: 执行 (Do)
- 架构设计 (Design)
- 编码实施 (Coding)
- 每日站会 (Daily Sync)

Phase 3: 检查 (Check)
- 进度打卡 (Reporting)
- 代码评审 (Code Review)
- 里程碑验收 (Audit)

Phase 4: 行动 (Act)
- 风险干预 (Risk Mitigation)
- 缺陷修复 (Issue Fix)
- 全局复盘 (Retrospective)

Mandatory connections:
- Connect the 4 phases into a continuous loop: (Plan) -> (Do) -> (Check) -> (Act) -> (Plan).
- Place the label: [项目生命周期管理 / Lifecycle Management] prominently in the absolute center.
- Draw connection arrows as thick, tech-style directional flow trackers.

Text rules:
Keep all phase titles and task nodes cleanly bilingual. Use minimalist text blocks.

Negative constraints:
CRITICAL: NO pie charts! NO childish circular gears! NO 3D or depth! Use pure 2D flat geometric blocks (chevrons or rounded rectangles) arranged in a sleek loop. Completely empty white canvas behind the nodes.
```

---

### 图 36 测试验证体系图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
测试验证体系图

Diagram type:
Standard Enterprise Testing Strategy Mind-Map / Tree Diagram

Layout:
Use a structured hierarchical tree or professional mind-map layout starting from the center or top, branching out symmetrically to 6 major testing domains.

Mandatory nodes (Bilingual):
Center/Root:
- 测试验证体系 (Testing Validation Framework)

Branches (Level 1) & Sublabels (Level 2):
1. 功能测试 (Functional Testing)
   - 功能正确性 (Functional Correctness)
2. 性能测试 (Performance Testing)
   - 响应与吞吐 (Response & Throughput)
3. 渲染测试 (Rendering Testing)
   - 界面流畅度 (UI Fluency & FPS)
4. 存储测试 (Storage Testing)
   - 写入稳定性 (Write Stability)
5. 回放测试 (Playback Testing)
   - 闭环正确性 (Closed-Loop Accuracy)
6. 长稳测试 (Long-Term Stability)
   - 连续运行可靠性 (Continuous Reliability)

Mandatory connections:
- Center node connects outward to the 6 Level 1 branches via solid lines.
- Each Level 1 branch connects to its respective Level 2 sublabel.

Text rules:
Keep all labels STRICTLY bilingual (Chinese and English).


Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No security testing branch unless explicitly added later.
No decorative icons.
```

---

### 图 37 方案定型流程图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
方案定型流程图

Diagram type:
Standard Stage-Gate Decision Pipeline Workflow

Layout:
Strict left-to-right horizontal pipeline with 5 sequential stage blocks (Chevron or rounded rectangles).

Mandatory nodes (Bilingual):
- 候选方案提出 (Candidate Proposal)
- 专项测试设计 (Specialized Test Design)
- 结果比较 (Result Comparison)
- 阶段评审 (Stage-Gate Review)
- 最终定型 (Final Formalization)

Optional floating labels (attached to specific stages):
- 存储方案 (Storage Plan), 压缩方案 (Compression Plan), 渲染方案 (Rendering Plan)

Mandatory connections:
- 候选方案提出 -> 专项测试设计 -> 结果比较 -> 阶段评审 -> 最终定型 (Connect via thick horizontal arrows).

Text rules:
Keep all text strictly bilingual.

Optional side labels:
- 存储方案
- 压缩方案
- 渲染方案

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No business iconography.
No more than 5 main stages.
```

---

### 图 38 试运行闭环流程图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. ABSOLUTELY NO grouping boxes, NO dashed boundaries, and NO containers enclosing the nodes. Standalone nodes only.
Aesthetics: ABSOLUTELY NO 3D, NO TRAYS, NO BASES. Draw the UML nodes directly on the empty white canvas. NEVER draw a secondary box, dashed box, or shadow underneath the nodes.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
试运行闭环流程图

Diagram type:
Standard UML Activity Diagram (Vertical Workflow)

Layout:
Strictly vertical (top-to-bottom) centerline layout.
Use standard UML Activity Diagram notation:
- Solid circle for Start Node.
- Rounded rectangles for Action Nodes.
- Diamond for Decision Node.
- Bullseye (circle with a dot) for End Node.
To represent the feedback loop, draw a separate return line that goes OUT to the right, travels UP alongside the main column, and goes LEFT back into the [连续试运行] node. Absolutely no criss-crossing lines. Ensure strict orthogonal lines (vertical and horizontal only).

Mandatory nodes (Bilingual):
- [Start Node] 版本冻结 (Version Freeze)
- [Action Node] 连续试运行 (Continuous Trial Run)
- [Decision Diamond] 是否发现异常? (Anomaly Found?)
- [Action Node] 异常处理与修复 (Log & Fix)
- [Action Node] 回归验证 (Regression Test)
- [Action Node] 结果回收 (Collect Results)
- [End Node] 试运行结束 (Trial Completed)

Mandatory connections:
- [Start Node] 版本冻结 -> [Action Node] 连续试运行
- [Action Node] 连续试运行 -> [Decision Diamond] 是否发现异常?
- [Decision Diamond] 是否发现异常? --[YES (是)]--> [Action Node] 异常处理与修复 (Line goes straight down)
- [Action Node] 异常处理与修复 -> [Action Node] 回归验证 (Line goes straight down)
- [Action Node] 回归验证 --[Return Path routed on the RIGHT side]--> loops back up to --> [Action Node] 连续试运行
- [Decision Diamond] 是否发现异常? --[NO (否)]--> [Action Node] 结果回收 (Line routed OUT to the LEFT and DOWN)
- [Action Node] 结果回收 -> [End Node] 试运行结束

Mandatory annotation:
- Place floating note: 冻结后仅允许缺陷修复和参数微调 (Only fixes and tweaks allowed after freeze)

Text rules:
Keep all text strictly bilingual. YES/NO decision routes must be clearly labeled with exact UML transitions.
Negative constraints:
CRITICAL: DO NOT draw any trays, platforms, dashed outlines, or secondary boxes beneath the text nodes. The nodes must float directly on the pure white #FFFFFF background. Reject any 3D or pseudo-3D styling. Use pure simple 2D shapes (circles, rounded rectangles, diamonds).
```

---

###  图 39 问题跟踪闭环图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
问题跟踪闭环图

Diagram type:
Sequential Pipeline Flowchart (Defect Lifecycle)

Layout:
Use a strictly linear horizontal pipeline from left to right, using chevron arrows (like a value stream) or linked rectangles.
Place nodes strictly in a single horizontal row to prevent messy layouts.
For the failure return path, draw a single long curved or orthogonal line arching OVER the top of the main pipeline returning to a previous step. DO NOT draw a tangled web.

Mandatory nodes in order (Bilingual):
1. 问题发现 (Discovered)
2. 问题登记 (Logged)
3. 责任分派 (Assigned)
4. 修复实现 (Fixed)
5. 验证确认 (Verified)
6. 问题关闭 (Closed)

Mandatory connections:
- Forward path (solid straight arrows): 问题发现 -> 问题登记 -> 责任分派 -> 修复实现 -> 验证确认 -> 问题关闭
- Return path (dashed line routed ABOVE the sequence): 验证确认 --[验证未通过 (Verification Fails)]--> returns to --> 修复实现

Text rules:
Keep all text strictly bilingual. Ensure the return path is cleanly separated from the main path.

Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No bug icon stickers.
No issue tracker screenshot look.
```

---

### 图 40 风险热力图

```text
Create a high-end, strict 2D engineering diagram for a professional software engineering bid document.
Style: Modern enterprise IT architecture style (similar to official technical whitepapers of AWS/Azure), flat vector-like graphics with supreme clarity, pure white background, suitable for high-res printing.
Color Palette: High-contrast engineering style with pastel backgrounds. Use PURE BLACK (#000000) for ALL text, connecting lines, arrowheads, and node borders. For node backgrounds, use soft pastel tech blue (#EFF6FF) for core modules, and pale gray (#F3F4F6) for secondary nodes. Group boundaries should use black dotted lines with extremely transparent light blue backgrounds.
Aesthetics: STRICTLY FLAT UI DESIGN. Use clean, zero-depth 2D wireframe rectangles on a pure white canvas. Nodes must be simple flat geometric shapes with 1px borders. No depth, no layers, no shadows.
Layout & Connections: Grid-based pixel-perfect alignment, symmetrical layouts, and even node spacing. Use strictly straight lines (orthogonal or diagonal/angled). Absolutely NO curved, wavy, or spaghetti lines. Use explicit sharp arrowheads for dependencies and directed flows. Line strokes must be consistent in width.
Typography constraint: Chinese text handling must be as exact as possible. The figure title must NOT be rendered as a headline inside the image. Use exact node labels provided. Do not add extra unlabeled elements.
If the diagram is UML, keep it close to standard UML notation.
If the diagram is DFD, do not mix UML symbols into it.
If the diagram is a wireframe, keep it low-fidelity and schematic.
Figure ID:
风险热力图

Diagram type:
Standard Enterprise Risk Heatmap Matrix (5x5 Grid)

Layout:
Use a standard 2D matrix / Cartesian coordinate system.
- X-Axis (Horizontal): 影响程度 (Impact Severity) [Low -> High]
- Y-Axis (Vertical): 发生概率 (Likelihood/Probability) [Low -> High]
Divide the matrix into a grid with background colors mapping from Green (Bottom-Left) to Yellow to Red (Top-Right).

Mandatory risk items (Bilingual, placed as text elements inside the grid cells):
- 线程竞争 (Thread Contention) -> High Risk Area
- 写盘瓶颈 (Write Bottleneck) -> High Risk Area
- 界面渲染卡顿 (UI Rendering Lag) -> Medium Risk Area
- 首版延期 (v1.0 Delay) -> Medium Risk Area
- 试运行长稳问题 (Trial Stability Issue) -> Low/Medium Risk Area
- 接口边界不清 (Unclear API Boundaries) -> Low Risk Area

Text rules:
Keep all text securely bilingual. The axes MUST have bilingual labels. Render the title explicitly. Do NOT render the matrix in 3D.


Negative constraints:
CRITICAL: NO depth illusion! NO 3D! NO isometric! DO NOT draw objects below the text boxes. Nodes must NOT be placed on surfaces. Use a completely empty white background behind text boxes.
No decorative warning icons.
No 3D heatmap.
No unlabeled axes.
```

---

## 四、实际使用建议

### 1. 先画核心图

优先级最高的 10 张：

- 图 1 项目应用场景示意图
- 图 5 系统总用例图
- 图 10 一级数据流图
- 图 11 系统总体架构图
- 图 13 系统运行时数据流图
- 图 14 实时处理与并发控制总体图
- 图 18 核心领域类图
- 图 30 敏捷开发流程图
- 图 31 项目实施甘特图
- 图 36 测试验证体系图

### 2. 原型图最后出

低保真原型图建议在结构图和流程图出完后再做：

- 图 26 主窗口总体布局图
- 图 27 总览页原型图
- 图 28 设备页原型图
- 图 29 通道分析页原型图

### 3. 若某张图生成不稳，按这个顺序补约束

1. 先补 `Layout`
2. 再补 `Mandatory nodes`
3. 再补 `Mandatory connections`
4. 最后补 `Negative constraints`

### 4. 不建议交给生图 agent 的情况

如果出现以下问题，建议改用 draw.io / ProcessOn / Visio 手工绘制：

- UML 关系总是错误
- DFD 符号总被混成架构图
- 甘特图时间轴不准
- 类图总是多出未定义类
- 中文标签清晰度不足
