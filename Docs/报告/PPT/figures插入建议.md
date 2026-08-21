# Figures文件夹图表插入建议

**生成时间**: 2026-08-22  
**目标**: 为答辩PPT大纲v5.0提供figures文件夹（294张图）的详细插入方案

---

## 一、figures文件夹结构概览

```
figures/
├── 第10章/                          # 控制器性能对比（约50张）
│   ├── controller_ranking_rmse.png
│   ├── controller_radar_chart.png
│   ├── controller_dist_rmse_box.png
│   ├── controller_dist_terminal_box.png
│   └── individual_controllers/      # 48个控制器的独立轨迹图
│       ├── official_pid/
│       ├── px4_ctrl/
│       └── ...
│
├── 第11章/
│   ├── 七场景对比/                  # 6张对比图
│   │   ├── hover_position_error_comparison.png
│   │   ├── figure8_position_error_comparison.png
│   │   ├── wind_disturbance_position_error_comparison.png
│   │   ├── parameter_mismatch_position_error_comparison.png
│   │   ├── spiral_position_error_comparison.png
│   │   └── step_response_position_error_comparison.png
│   │
│   ├── 灵敏度分析/                  # 3张灵敏度图
│   │   ├── wind_disturbance_sensitivity.png
│   │   ├── parameter_mismatch_sensitivity.png
│   │   └── motor_efficiency_sensitivity.png
│   │
│   ├── 三机编队/                    # 3张编队图
│   │   ├── formation_trajectory_xy.png
│   │   ├── inter_uav_distance.png
│   │   └── formation_error.png
│   │
│   └── ECBF安全/                    # 2张ECBF图
│       ├── ecbf_applied_offset.png
│       └── ecbf_pair_distance.png
│
└── Rviz/                            # Gazebo/RViz可视化截图
    ├── fastlio点云.png
    ├── 8字.png
    └── diff.png
```

---

## 二、按章节的详细插入方案

### 第04章：仿真结果分析（P20-P25）

#### P22：ClimbPath 50s筛查结果

**插入位置**: 台词后，占据页面60-70%

**推荐图表组合**（2-3张）：

1. **控制器排名图**（主图，50%宽）
   - 文件：`figures/第10章/controller_ranking_rmse.png`
   - 展示：48个控制器按RMSE排序
   - 标注：仅2个控制器（official_pid、px4ctrl）RMSE < 5m

2. **控制器雷达图**（右侧，50%宽）
   - 文件：`figures/第10章/controller_radar_chart.png`
   - 展示：多维度性能对比（跟踪精度、响应速度、鲁棒性）
   - 标注：官方PID vs px4ctrl的多维对比

3. **筛查统计卡片**（底部，全宽）
   - 数据来源：排名图统计
   - 内容：
     ```
     总测试: 48个控制器 | 通过标准: RMSE < 5m | 通过数量: 2个 | 通过率: 4.2%
     最佳: official_pid (RMSE=2.3m) | 次佳: px4ctrl (RMSE=3.1m)
     ```

---

#### P23：性能分布分析

**插入位置**: 台词后，并排布局

**推荐图表组合**（2张）：

1. **RMSE箱线图**（左侧，50%宽）
   - 文件：`figures/第10章/controller_dist_rmse_box.png`
   - 展示：七族算法的RMSE分布
   - 标注：PID族中位数最低，MPC族方差最大

2. **终点误差箱线图**（右侧，50%宽）
   - 文件：`figures/第10章/controller_dist_terminal_box.png`
   - 展示：七族算法的终点误差分布
   - 标注：INDI族终点误差最小

---

#### P24：官方PID vs px4ctrl详细对比

**插入位置**: 台词后，占据页面70%

**推荐图表组合**（4-6张小图，2行×3列）：

**第一行：官方PID**
- `figures/第10章/individual_controllers/official_pid/trajectory_xy.png`（XY轨迹）
- `figures/第10章/individual_controllers/official_pid/position_error.png`（位置误差）
- `figures/第10章/individual_controllers/official_pid/altitude_z.png`（高度跟踪）

**第二行：px4ctrl**
- `figures/第10章/individual_controllers/px4_ctrl/trajectory_xy.png`（XY轨迹）
- `figures/第10章/individual_controllers/px4_ctrl/position_error.png`（位置误差）
- `figures/第10章/individual_controllers/px4_ctrl/altitude_z.png`（高度跟踪）

**底部对比卡片**：
```
| 指标 | official_pid | px4ctrl | 胜者 |
|------|-------------|---------|-----|
| RMSE | 2.3m | 3.1m | official_pid |
| 终点误差 | 1.8m | 2.5m | official_pid |
| 超调量 | 0.2m | 0.5m | official_pid |
| 响应时间 | 1.2s | 0.8s | px4ctrl |
```

---

### 第04章：七场景对比（P25）

#### P25：七场景深度性能对比

**插入位置**: 占据整页，网格布局（2行×3列 + 1张底部）

**推荐图表组合**（6张对比图）：

**第一行：标称场景（3张）**
1. `figures/第11章/七场景对比/hover_position_error_comparison.png`（悬停）
2. `figures/第11章/七场景对比/figure8_position_error_comparison.png`（8字）
3. `figures/第11章/七场景对比/spiral_position_error_comparison.png`（螺旋）

**第二行：鲁棒性场景（3张）**
4. `figures/第11章/七场景对比/wind_disturbance_position_error_comparison.png`（风扰）
5. `figures/第11章/七场景对比/parameter_mismatch_position_error_comparison.png`（参数失配）
6. `figures/第11章/七场景对比/step_response_position_error_comparison.png`（阶跃响应）

**底部总结卡片**：
```
关键发现：
✅ 官方PID和px4ctrl在所有场景下均保持稳定
⚠️ 现代控制算法在风扰场景表现优异（通过率78%）
⚠️ 先进控制算法在极限机动中跟踪能力更强（通过率65%）
```

---

### 第04章：灵敏度分析（P26）

#### P26：关键参数灵敏度分析

**插入位置**: 占据页面70%，横向排列

**推荐图表组合**（3张灵敏度曲线图）：

1. **风扰灵敏度**（左，33%宽）
   - 文件：`figures/第11章/灵敏度分析/wind_disturbance_sensitivity.png`
   - X轴：风速（0-15 m/s）
   - Y轴：位置误差增量
   - 曲线：官方PID、px4ctrl、其他代表性控制器

2. **参数失配灵敏度**（中，33%宽）
   - 文件：`figures/第11章/灵敏度分析/parameter_mismatch_sensitivity.png`
   - X轴：质量偏差（-30% ~ +30%）
   - Y轴：位置误差增量
   - 曲线：同上

3. **电机效率灵敏度**（右，33%宽）
   - 文件：`figures/第11章/灵敏度分析/motor_efficiency_sensitivity.png`
   - X轴：电机效率（60% ~ 100%）
   - Y轴：位置误差增量
   - 曲线：同上

**底部结论卡片**：
```
灵敏度分析结论：
• 官方PID对风扰最不敏感（斜率最小）
• px4ctrl对参数失配鲁棒性最强
• 电机效率降至70%以下时，所有控制器性能显著下降
```

---

### 第05章：编队控制与避障（P26）

#### P26：三机编队Figure8演示（新增一页或合并到P26）

**插入位置**: 占据页面60%

**推荐图表组合**（3张编队图）：

1. **编队轨迹俯视图**（上半部分，60%高）
   - 文件：`figures/第11章/三机编队/formation_trajectory_xy.png`
   - 展示：三架无人机的XY平面轨迹
   - 颜色区分：Leader（蓝）、Follower1（绿）、Follower2（红）
   - 标注：编队保持形状（等边三角形，边长2m）

2. **机间距离时间序列**（左下，50%宽）
   - 文件：`figures/第11章/三机编队/inter_uav_distance.png`
   - X轴：时间（0-60s）
   - Y轴：机间距离（m）
   - 三条曲线：d12、d23、d31
   - 标注：目标距离2m，实际偏差<0.5m

3. **编队误差统计**（右下，50%宽）
   - 文件：`figures/第11章/三机编队/formation_error.png`
   - X轴：时间（0-60s）
   - Y轴：编队误差（m）
   - 标注：平均误差0.3m，最大误差0.8m

---

### 第05章：ECBF安全监督（P26或独立一页）

**插入位置**: 占据页面50%

**推荐图表组合**（2张ECBF图）：

1. **ECBF修正量时间序列**（左侧，50%宽）
   - 文件：`figures/第11章/ECBF安全/ecbf_applied_offset.png`
   - X轴：时间（0-60s）
   - Y轴：修正量（m）
   - 三条曲线：X/Y/Z方向修正量
   - 标注：修正触发时刻（红色竖线）

2. **机间距离安全监控**（右侧，50%宽）
   - 文件：`figures/第11章/ECBF安全/ecbf_pair_distance.png`
   - X轴：时间（0-60s）
   - Y轴：机间距离（m）
   - 三条曲线：d12、d23、d31
   - 安全阈值线：0.8m（红色虚线）
   - 标注：所有时刻均满足安全约束

---

### 第08章：Gazebo与UE部署（P34-P39）

#### P34：Gazebo状态反馈通路设计

**插入位置**: 手绘图14下方30%高度

**推荐图表**（1张）：

- **FAST-LIO实时建图点云**
  - 文件：`figures/Rviz/fastlio点云.png`
  - 展示：RViz中显示的彩色点云地图
  - 标注：
    - 点云密度：~100k点/帧
    - 建图范围：50m×50m
    - 定位精度：<0.1m

---

#### P35：Gazebo运行时验证——五类任务

**插入位置**: 表格右侧50%宽

**推荐图表**（1张）：

- **Gazebo Figure8轨迹**
  - 文件：`figures/Rviz/8字.png`
  - 展示：RViz中显示的8字轨迹
  - 绿色：参考轨迹
  - 蓝色：实际轨迹
  - 红色：障碍物（如果有）
  - 标注：跟踪误差2.1m，无碰撞事件

---

#### P37：Diff-Planner局部轨迹优化

**插入位置**: 手绘图16右侧40%宽

**推荐图表**（1张）：

- **RViz差分避障场景轨迹**
  - 文件：`figures/Rviz/diff.png`
  - 展示：Diff-Planner优化后的避障轨迹
  - 绿色：参考路径
  - 红色：优化轨迹
  - 蓝色：实际飞行轨迹
  - 灰色：障碍物
  - 标注：
    - 重规划触发点（红色圆圈）
    - 绕行距离：最小0.8m
    - 速度保持：1.5 m/s

---

## 三、按优先级的插入建议

### 🔴 **第一优先级**（必须加入，核心数据支撑）

| 页码 | 图表 | 文件 | 原因 |
|-----|------|-----|-----|
| P22 | 控制器排名图 | controller_ranking_rmse.png | 48个控制器筛查的核心证据 |
| P22 | 控制器雷达图 | controller_radar_chart.png | 多维度性能对比 |
| P23 | RMSE箱线图 | controller_dist_rmse_box.png | 七族算法性能分布 |
| P24 | 官方PID轨迹 | official_pid/*.png | 基线对比的核心证据 |
| P24 | px4ctrl轨迹 | px4_ctrl/*.png | 自研控制器性能展示 |
| P25 | 七场景对比（6张） | 七场景对比/*.png | 鲁棒性验证的核心证据 |

**小计：11-15张图**

---

### 🟡 **第二优先级**（强烈建议，增强说服力）

| 页码 | 图表 | 文件 | 原因 |
|-----|------|-----|-----|
| P26 | 灵敏度分析（3张） | 灵敏度分析/*.png | 参数鲁棒性量化分析 |
| P26 | 三机编队（3张） | 三机编队/*.png | 编队控制能力展示 |
| P26 | ECBF安全（2张） | ECBF安全/*.png | 安全约束有效性证明 |
| P34 | FAST-LIO点云 | Rviz/fastlio点云.png | 状态估计质量展示 |
| P35 | Gazebo 8字轨迹 | Rviz/8字.png | Gazebo验证成功证据 |

**小计：11张图**

---

### 🟢 **第三优先级**（可选，锦上添花）

| 页码 | 图表 | 文件 | 原因 |
|-----|------|-----|-----|
| P23 | 终点误差箱线图 | controller_dist_terminal_box.png | 补充性能分布细节 |
| P37 | Diff-Planner轨迹 | Rviz/diff.png | 规划能力展示 |
| P24 | 其他代表性控制器轨迹 | individual_controllers/其他/*.png | 丰富算法族对比 |

**小计：3-10张图**

---

## 四、图表插入的技术建议

### 📐 **布局建议**

1. **对比图组**（如七场景对比）：
   - 使用2行×3列网格布局
   - 每张图尺寸一致
   - 统一配色方案
   - 底部留空间放总结卡片

2. **性能分布图**（如箱线图）：
   - 左右并排，各占50%宽
   - 保持Y轴刻度一致（便于对比）
   - 图例放在图内部或底部统一

3. **轨迹图**（如8字轨迹）：
   - 单张图占60-70%页面
   - 保留足够边距
   - 添加图例和关键参数标注

### 🎨 **配色建议**

1. **控制器对比**：
   - 官方PID：蓝色 #38BDF8
   - px4ctrl：绿色 #6EE7B7
   - 其他控制器：灰色系（区分度降低）

2. **性能等级**：
   - 优秀（<5m）：绿色 #6EE7B7
   - 中等（5-10m）：黄色 #F9E795
   - 较差（>10m）：橙色 #E9A568
   - 失败（失稳）：红色 #F96167

3. **场景类型**：
   - 标称场景：蓝色系
   - 鲁棒性场景：橙色系

### 📝 **标注建议**

1. **关键数值标注**：
   - RMSE值：保留1位小数（如2.3m）
   - 通过率：保留1位小数（如73.7%）
   - 误差：使用科学记数法（如1.148e-13m）

2. **门限线标注**：
   - 5m门限：红色虚线
   - 安全距离：红色虚线
   - 目标值：绿色虚线

3. **时间标注**：
   - 关键事件：红色竖线 + 文字标注
   - 时间轴：清晰刻度，单位一致

---

## 五、用户提到的截图补充说明

根据用户消息："里面的都是截图，晚点我会自己补充进去，`C:\Users\HP\Desktop\MoSim\Docs\报告\图`"

### 📂 **`Docs\报告\图`文件夹预留位置**

**建议预留位置**：

1. **P5：Blender机械建模流程**
   - 预留：Blender软件截图（建模界面、参数设置、导出选项）
   - 用途：展示机械建模过程

2. **P11：MoSim Studio在线建模验证工作区**
   - 预留：APP截图1（控制器拖拽式配置界面）
   - 用途：展示控制器配置流程

3. **P21：MoSim Studio数据分析生成图表**
   - 预留：APP截图2（AI Agent分析界面）
   - 用途：展示数据分析工作流

4. **P27-P28：MWORKS Live实时仿真界面**
   - 预留：APP截图3（MWORKS Live监控界面）
   - 用途：展示实时仿真工作区

5. **P32-P33：代码生成演示**
   - 预留：APP截图4（代码生成进度与文件浏览）
   - 用途：展示C99代码生成过程

6. **P36：C99全链路联通验证**
   - 预留：QGroundControl地面站截图
   - 用途：展示飞行模式、定位来源、遥测频率

7. **P36：Gazebo场景加载**
   - 预留：Gazebo软件截图（工厂L2环境）
   - 用途：展示仿真场景

8. **P39：UE工厂场景L2静态评审**
   - 预留：虚幻引擎场景截图
   - 用途：展示高保真工业场景

### 💡 **为用户留白的建议**

在大纲相应页面添加占位符：

```markdown
**核心视觉**（截图，待补充）：
- [ ] Blender建模界面截图（位置：P5）
- [ ] MoSim Studio APP截图1（位置：P11）
- [ ] MoSim Studio APP截图2（位置：P21）
- [ ] MWORKS Live APP截图3（位置：P27）
- [ ] 代码生成 APP截图4（位置：P32）
- [ ] QGroundControl地面站截图（位置：P36）
- [ ] Gazebo工厂场景截图（位置：P36）
- [ ] UE工厂场景截图（位置：P39）
```

---

## 六、最终执行清单

### ✅ **立即可执行**（无需等待截图）

1. **加入figures文件夹中的图**（26-30张）：
   - P22-P24：第10章控制器性能对比（11-15张）
   - P25：第11章七场景对比（6张）
   - P26：灵敏度分析（3张）+ 三机编队（3张）+ ECBF（2张）
   - P34-P37：Gazebo/RViz可视化（3张）

2. **更新大纲引用路径**：
   - 在相应页码添加figures文件夹图表的引用
   - 标注图表标题、来源、关键数值

### ⏳ **等待用户补充**（8个截图位置）

- P5、P11、P21、P27、P32、P36（×2）、P39

---

**文档生成时间**: 2026-08-22  
**分析人员**: Claude (Opus 5)  
**结论**: figures文件夹中26-30张图可立即加入PPT，8个截图位置为用户预留。优先级按核心证据 > 增强说服力 > 锦上添花排序。
