# Syslab图表生成技术规格

> **目标**：为仿真分析报告第10章生成标准化的性能对比图表
> **作者**：Claude + Codex协作
> **日期**：2026-07-30

---

## 一、数据源现状

### 1.1 已有数据（28个accepted控制器）

**统一G3 ClimbPath50s批次**：
- 路径：`Results/control_platform/phase2_full_48_climbpath/`
- 状态清单：`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json`
- 28个控制器的Result.msr、raw/result.csv、metrics/metrics.csv全部存在

**28个控制器清单**：
```
adaptive_backstepping, adaptive_smc, backstepping_baseline, dfbc_basic,
dfbc_high_order_body_rate, dfbc_high_order, dfbc_smooth_robust_body_rate,
dfbc_smooth_robust, explicit_gain_scheduled_mpc, feedback_linearization,
fuzzy_smc, h_2_state_feedback, ilqr, integral_smc, lqg, lqi, lqr_baseline,
mppi, ndi, nonsingular_terminal_smc, official_pid,
official_pid_yaw_authority_mapped, passivity_based_control, px4ctrl,
robust_mpc, se_3_basic, terminal_smc, tube_mpc
```

**重点对比基线**：
- **Official PID**：`Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/`
- **px4ctrl**：`Results/control_platform/phase2_full_48_climbpath/px4ctrl/`（用于统一对比）
- **px4ctrl图形化专用**：`Results/control_platform/px4ctrl_graphical_completion_20260728/`（用于图8-2展示）

### 1.2 未跑的场景

**七场景批次**（仅2个控制器需要跑）：
- Official PID × 7场景（hover/step_response/figure8/spiral/wind_disturbance/parameter_mismatch/motor_efficiency_fault）
- px4ctrl × 7场景
- 配置：`Config/control_platform/seven_scenario_experiment_profiles_v2.json`

**灵敏度分析**（仅2个控制器需要跑）：
- 电机故障边界η扫描（0.75~0.85）
- 风扰强度扫描（0~0.8 N）
- 参数摄动扫描（1.0x~1.4x）

**其余历史批次控制器**：只需要ClimbPath50s一个场景的图表（工作量展示，非深度分析）

---

## 二、图表需求清单

### 2.1 第10章图表映射

| 图号 | 内容 | 数据源 | 实现方式 |
|------|------|--------|----------|
| **图10-1a** | Official PID ClimbPath50s 轨迹俯视图XY | official_pid/raw/result.csv | `plot_results.py` |
| **图10-1b** | Official PID ClimbPath50s 高度跟踪Z | 同上 | `plot_results.py` |
| **图10-1c** | Official PID ClimbPath50s 位置误差 | 同上 | `plot_results.py` |
| **图10-1d** | Official PID ClimbPath50s 控制输入u1~u4 | 同上 | `plot_results.py` |
| **图10-2a** | PID族ClimbPath50s RMSE柱状图 | 多个metrics.csv | `compare_controllers.jl`扩展 |
| **图10-2b** | PID族ClimbPath50s 轨迹XY叠加图 | 多个result.csv | `compare_controllers.jl`扩展 |
| **图10-3** | 现代控制器代表性曲线（选3~5个） | 多个result.csv | `plot_results.py`批量 |
| **图10-4** | px4ctrl vs Official PID对比 | 两份result.csv | `compare_controllers.jl`专用 |
| **图10-5a** | 28控制器G3状态矩阵（✅/❌/⏸️） | G3_STATUS.json | 新脚本`generate_status_matrix.py` |
| **图10-5b** | 28控制器RMSE热力图 | 28份metrics.csv | 新脚本`generate_heatmap.py` |
| **图10-5c** | 控制器族雷达图（RMSE/能量/超调） | 28份metrics.csv | 新脚本`generate_radar_chart.py` |

### 2.2 未来扩展（初赛不做）

- 七场景完整对比（Official PID + px4ctrl）
- 灵敏度曲线图（η/风扰/参数摄动）
- 动态视频（UE5渲染）

---

## 三、脚本设计规范

### 3.1 plot_results.py — 单控制器4子图生成

**输入参数**：
```bash
python Scripts/results/plot_results.py \
  <result_csv> \
  <output_dir> \
  --metrics <metrics_json> \
  --controller-id <name> \
  --scene-id <scene_name>
```

**输出文件**：
```
<output_dir>/
├── trajectory_xy.svg          # 轨迹俯视图
├── altitude_z.svg             # 高度跟踪
├── position_error.svg         # 位置误差||e_p||
├── control_input.svg          # 控制输入u1~u4
├── attitude.svg               # 可选：roll/pitch/yaw（如果CSV有）
└── figure_manifest.json       # 元数据
```

**绘图样式规范**：
- **字体**：Times New Roman，12pt（标题14pt）
- **线宽**：实际轨迹2.0pt，参考轨迹1.5pt虚线（dash pattern: 6,4）
- **颜色方案**：
  - 实际轨迹：`#1f77b4`（蓝色）
  - 参考轨迹：`#222222`（深灰）
  - 误差曲线：`#d62728`（红色）
  - 控制输入：u1/u2/u3/u4分别用`#1f77b4`, `#ff7f0e`, `#2ca02c`, `#d62728`
- **图幅尺寸**：1080×720 px（保持现有compare_controllers.jl的风格）
- **坐标轴标签**：X轴"Time (s)"，Y轴"Position (m)" / "Error (m)" / "Command"
- **图例位置**：右上角，无边框

**CSV列要求**：
```
必需列：time, x, y, z, x_ref, y_ref, z_ref
控制输入：u1, u2, u3, u4（如果没有则跳过control_input.svg）
姿态角：roll, pitch, yaw（如果没有则跳过attitude.svg）
```

**figure_manifest.json格式**：
```json
{
  "schema": "mosim.plot_results.v1",
  "generated_at": "2026-07-30T12:00:00Z",
  "controller_id": "official_pid",
  "scene_id": "climbpath50s",
  "raw_csv": "Results/.../raw/result.csv",
  "metrics_json": "Results/.../metrics/metrics.json",
  "figures": [
    {"file": "trajectory_xy.svg", "type": "trajectory_xy"},
    {"file": "altitude_z.svg", "type": "altitude_z"},
    {"file": "position_error.svg", "type": "position_error"},
    {"file": "control_input.svg", "type": "control_input"}
  ],
  "key_metrics": {
    "position_rmse_m": 0.276,
    "terminal_position_error_m": 0.0027,
    "control_energy": 12345.67
  }
}
```

---

### 3.2 compare_controllers.jl — 多控制器对比（扩展版）

**当前功能**：
- `--climb` + `--step`：生成RMSE柱状图和Step响应XY叠加图

**需要扩展的功能**：

#### 3.2.1 新增ClimbPath轨迹叠加图
```julia
# 新增函数：write_climbpath_trajectory_overlay
# 输入：多个controller的(time, x, y, z, x_ref, y_ref, z_ref)
# 输出：<output_dir>/figures/climbpath_trajectory_overlay.svg
# 布局：XY俯视图（单面板，多条曲线+参考虚线）
```

#### 3.2.2 新增控制能量对比柱状图
```julia
# 新增函数：write_control_energy_bar
# 输入：多个controller的metrics.json中的control_energy
# 输出：<output_dir>/figures/control_energy_bar.svg
```

#### 3.2.3 新增终端误差对比柱状图
```julia
# 新增函数：write_terminal_error_bar
# 输入：多个controller的metrics.json中的terminal_position_error_m
# 输出：<output_dir>/figures/terminal_error_bar.svg
```

**扩展后的调用方式**：
```bash
julia Scripts/syslab/compare_controllers.jl \
  --climbpath \
    official_pid=Results/.../official_pid/raw/result.csv \
    cascade_pid=Results/.../cascade_pid/raw/result.csv \
    lqr_baseline=Results/.../lqr_baseline/raw/result.csv \
  --output-dir Results/syslab_comparison/pid_vs_lqr
```

**新增输出文件**：
```
<output_dir>/figures/
├── climbpath_rmse_bar.svg           # 已有
├── climbpath_trajectory_overlay.svg # 新增：轨迹叠加
├── control_energy_bar.svg           # 新增：控制能量
├── terminal_error_bar.svg           # 新增：终端误差
└── controller_comparison.csv        # 已有：汇总表格
```

**样式统一**：
- 继承现有的COLORS数组、svg_escape、scaled等工具函数
- 字体统一为Times New Roman
- 图幅尺寸保持1080×720（或980×560，与现有柱状图一致）

---

### 3.3 generate_status_matrix.py — 28控制器状态矩阵

**输入参数**：
```bash
python Scripts/syslab/generate_status_matrix.py \
  --status-json Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json \
  --output Docs/报告/figures/第10章/controller_status_matrix.svg
```

**输出**：28行×1列的状态表格，每行包含：
```
[控制器名] [族标签] [状态图标] [RMSE数值]
```

**状态图标规则**：
- ✅ `accepted` — 绿色
- ❌ `executed_blocked` — 红色
- ⏸️ `not_run` — 灰色

**样式**：
- 字体：Times New Roman 11pt
- 图幅：自适应高度（28行 × 40px/行 ≈ 1120px），宽度800px
- 背景：白色
- 分组：按控制器族分段（PID族/线性鲁棒族/非线性族/滑模族/优化族/几何族/学习增强族/工程基线）

**族标签映射表**（内嵌到脚本）：
```python
CONTROLLER_FAMILY = {
    "official_pid": "PID族",
    "cascade_pid": "PID族",
    "lqr_baseline": "线性/鲁棒族",
    "lqg": "线性/鲁棒族",
    "backstepping_baseline": "非线性/自适应族",
    "adaptive_backstepping": "非线性/自适应族",
    "integral_smc": "滑模族",
    "terminal_smc": "滑模族",
    "ilqr": "优化/预测族",
    "mppi": "优化/预测族",
    "se_3_basic": "几何/微分平坦族",
    "px4ctrl": "工程基线",
    # ... 补全28个
}
```

---

### 3.4 generate_heatmap.py — RMSE热力图

**输入参数**：
```bash
python Scripts/syslab/generate_heatmap.py \
  --metrics-dir Results/control_platform/phase2_full_48_climbpath \
  --output Docs/报告/figures/第10章/rmse_heatmap.svg
```

**输出**：28行（控制器）×1列（ClimbPath50s场景）的热力图

**颜色编码**：
- 0.0~0.2 m：深绿色 `#2ca02c`
- 0.2~0.5 m：浅绿色 `#7fbc41`
- 0.5~1.0 m：黄色 `#ffd92f`
- 1.0~2.0 m：橙色 `#ff7f0e`
- >2.0 m：红色 `#d62728`
- NaN/失败：灰色 `#cccccc`

**布局**：
- 左侧：控制器名称（按族分组）
- 右侧：颜色条（colorbar）标注RMSE范围
- 字体：Times New Roman 10pt

---

### 3.5 generate_radar_chart.py — 控制器族雷达图

**输入参数**：
```bash
python Scripts/syslab/generate_radar_chart.py \
  --metrics-dir Results/control_platform/phase2_full_48_climbpath \
  --output Docs/报告/figures/第10章/controller_radar_chart.svg
```

**输出**：每个控制器族一个雷达图子图（2×4布局，共8个族）

**雷达图维度**（5轴）：
1. **位置RMSE**（越低越好，归一化：max=2.0m）
2. **终端误差**（越低越好，归一化：max=5.0m）
3. **控制能量**（越低越好，归一化：相对Official PID）
4. **最大误差**（越低越好，归一化：max=10.0m）
5. **计算效率**（暂时用固定值1.0占位，未来可接入求解时间）

**聚合方式**：
- 每个族取该族内所有accepted控制器的**中位数**
- 如果某族只有1个控制器，直接用其数值
- 如果某族全部failed，雷达图显示为灰色虚线

**样式**：
- 每个族用不同颜色填充（半透明alpha=0.3）
- 外框五边形，5条轴线
- 字体：Times New Roman 10pt
- 总图幅：1600×1200 px

---

## 四、批量处理编排脚本

### 4.1 generate_all_chapter10_figures.py

**功能**：一键生成第10章所有图表

**调用方式**：
```bash
python Scripts/syslab/generate_all_chapter10_figures.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output-dir Docs/报告/figures/第10章 \
  --focus-controllers official_pid,px4ctrl \
  --compare-groups pid_family,modern_control
```

**执行流程**：
```python
# Step 1: 扫描28个accepted控制器
accepted_controllers = load_accepted_from_g3_status()

# Step 2: 为focus_controllers生成完整4子图
for controller in ["official_pid", "px4ctrl"]:
    run_plot_results(controller)

# Step 3: 为其余历史批次控制器只生成trajectory_xy（工作量展示）
for controller in accepted_controllers - focus_controllers:
    run_plot_results(controller, figures=["trajectory_xy"])

# Step 4: 按族分组生成对比图
pid_family = ["official_pid", "cascade_pid", ...]
run_compare_controllers(pid_family, output="pid_family_comparison")

modern_control = ["lqr_baseline", "lqg", "backstepping_baseline", ...]
run_compare_controllers(modern_control, output="modern_control_comparison")

# Step 5: 生成状态矩阵
run_generate_status_matrix()

# Step 6: 生成热力图
run_generate_heatmap()

# Step 7: 生成雷达图
run_generate_radar_chart()

# Step 8: 生成汇总报告ANALYSIS_REPORT.md
generate_summary_report()
```

**输出结构**：
```
Docs/报告/figures/第10章/
├── official_pid/                      # 完整4子图
│   ├── trajectory_xy.svg
│   ├── altitude_z.svg
│   ├── position_error.svg
│   └── control_input.svg
├── px4ctrl/                           # 完整4子图
│   └── ...
├── lqr_baseline/                      # 只有轨迹图
│   └── trajectory_xy.svg
├── adaptive_backstepping/             # 只有轨迹图
│   └── trajectory_xy.svg
├── ...（其余24个控制器）
├── pid_family_comparison/
│   ├── climbpath_rmse_bar.svg
│   ├── climbpath_trajectory_overlay.svg
│   ├── control_energy_bar.svg
│   └── terminal_error_bar.svg
├── modern_control_comparison/
│   └── ...（同上）
├── controller_status_matrix.svg       # 图10-5a
├── rmse_heatmap.svg                   # 图10-5b
├── controller_radar_chart.svg         # 图10-5c
└── ANALYSIS_REPORT.md                 # 自动生成的汇总
```

---

## 五、Codex任务分配

### 任务1：补全plot_results.py（优先级P0）
**文件**：`Scripts/results/plot_results.py`
**需求**：根据§3.1规范，实现4个SVG生成函数
**参考**：`Scripts/syslab/compare_controllers.jl`的SVG生成风格
**测试命令**：
```bash
python Scripts/results/plot_results.py \
  Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/raw/result.csv \
  /tmp/test_output \
  --metrics Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/metrics/metrics.csv
```

### 任务2：扩展compare_controllers.jl（优先级P0）
**文件**：`Scripts/syslab/compare_controllers.jl`
**需求**：根据§3.2规范，新增3个函数和`--climbpath`参数
**测试命令**：
```bash
julia Scripts/syslab/compare_controllers.jl \
  --climbpath \
    official_pid=Results/.../official_pid/raw/result.csv \
    lqr_baseline=Results/.../lqr_baseline/raw/result.csv \
  --output-dir /tmp/test_compare
```

### 任务3：新增状态矩阵脚本（优先级P1）
**文件**：`Scripts/syslab/generate_status_matrix.py`
**需求**：根据§3.3规范，从G3_STATUS.json生成状态表格SVG

### 任务4：新增热力图脚本（优先级P1）
**文件**：`Scripts/syslab/generate_heatmap.py`
**需求**：根据§3.4规范，从28个metrics.csv生成RMSE热力图

### 任务5：新增雷达图脚本（优先级P1）
**文件**：`Scripts/syslab/generate_radar_chart.py`
**需求**：根据§3.5规范，生成控制器族性能雷达图

### 任务6：一键批处理脚本（优先级P2）
**文件**：`Scripts/syslab/generate_all_chapter10_figures.py`
**需求**：根据§4.1规范，编排调用上述所有脚本

---

## 六、验收标准

### 6.1 单元测试
- [ ] `plot_results.py`能从official_pid的CSV生成4个有效SVG
- [ ] `compare_controllers.jl`能从2个控制器的CSV生成对比图
- [ ] 所有SVG文件用浏览器打开无报错
- [ ] figure_manifest.json格式正确且可解析

### 6.2 集成测试
- [ ] 运行`generate_all_chapter10_figures.py`完整流程无报错
- [ ] `Docs/报告/figures/第10章/`下生成28个控制器目录
- [ ] 状态矩阵/热力图/雷达图SVG存在且可视化正确

### 6.3 报告引用测试
- [ ] 在`仿真分析报告_正文骨架.md`中能找到所有图表文件
- [ ] 图表编号与报告章节对应（图10-1a/b/c/d, 图10-2a/b, ...）
- [ ] ANALYSIS_REPORT.md中的RMSE数值与metrics.csv一致

---

## 七、后续扩展

**初赛后需要补充的功能**：
1. 七场景完整图表（Official PID + px4ctrl × 7场景）
2. 灵敏度分析曲线（电机故障边界/风扰/参数摄动）
3. 动态视频生成（调用UE5/stream_unreal_udp.py）
4. AI Agent集成（自然语言查询、异常检测）

**不在本次范围**：
- 频域分析（Bode图/Nyquist图）— 报告§13需要手动用Syslab Control Toolbox
- 实时仿真对比 — 需要单独的Gazebo/PX4部署证据
