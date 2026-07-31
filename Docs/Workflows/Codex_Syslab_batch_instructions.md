# Codex任务指令：Syslab图表生成脚本实现

---

## 任务概述

实现MoSim项目仿真分析报告第10章所需的标准化图表生成工具链。

**背景文档**：`C:/Users/HP/Desktop/MoSim/Docs/Workflows/Syslab图表生成技术规格.md`（必读）

**数据源**：28个accepted控制器的ClimbPath50s结果已存在，路径规则见技术规格§1.1

**目标交付物**：6个脚本 + 完整测试 + 第10章全部图表

---

## 任务分解（按优先级）

### 【任务1】补全plot_results.py — 单控制器4子图生成（P0，最优先）

**文件路径**：`Scripts/results/plot_results.py`

**当前状态**：只有占位代码，写入figure_manifest.md但不生成真实SVG

**需求**：根据技术规格§3.1，实现完整的4子图生成功能

**必须实现的函数**：
1. `generate_trajectory_xy(csv_data, output_path)` — 轨迹俯视图XY
2. `generate_altitude_z(csv_data, output_path)` — 高度跟踪Z
3. `generate_position_error(csv_data, output_path)` — 位置误差||e_p||
4. `generate_control_input(csv_data, output_path)` — 控制输入u1~u4

**输入**：
```bash
python Scripts/results/plot_results.py \
  Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/raw/result.csv \
  Docs/figures/test_output \
  --metrics Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/metrics/metrics.csv \
  --controller-id official_pid \
  --scene-id climbpath50s
```

**输出文件**（必须全部生成）：
```
Docs/figures/test_output/
├── trajectory_xy.svg          # 必需
├── altitude_z.svg             # 必需
├── position_error.svg         # 必需
├── control_input.svg          # 必需（如果CSV中有u1~u4）
└── figure_manifest.json       # 必需
```

**CSV列名规范**：
- 必需列：`time`, `x`, `y`, `z`, `x_ref`, `y_ref`, `z_ref`
- 控制输入列（可选）：`u1`, `u2`, `u3`, `u4`
- 如果CSV缺少控制输入列，跳过`control_input.svg`但其余3个图必须生成

**SVG绘图规范（必须严格遵守）**：
- **字体**：Times New Roman，12pt（标题14pt）
- **图幅尺寸**：1080×720 px
- **线宽**：实际轨迹2.0pt，参考轨迹1.5pt
- **参考轨迹样式**：虚线，stroke-dasharray="6,4"
- **颜色方案**：
  - 实际轨迹（x/y/z）：`#1f77b4`
  - 参考轨迹：`#222222`
  - 误差曲线：`#d62728`
  - 控制输入u1/u2/u3/u4：`#1f77b4`, `#ff7f0e`, `#2ca02c`, `#d62728`
- **坐标轴**：X轴"Time (s)"，Y轴标签见技术规格
- **图例**：右上角，无边框

**参考代码风格**：`Scripts/syslab/compare_controllers.jl`的SVG生成模式（手写XML标签，不依赖matplotlib）

**验收标准**：
1. 用官方PID的CSV运行脚本，生成4个SVG文件
2. 用浏览器打开SVG无报错，曲线清晰可见
3. figure_manifest.json格式符合技术规格§3.1
4. 轨迹图中参考线为虚线，实际线为实线
5. 所有文字使用Times New Roman字体

---

### 【任务2】扩展compare_controllers.jl — 多控制器对比（P0）

**文件路径**：`Scripts/syslab/compare_controllers.jl`

**当前状态**：支持`--climb` + `--step`，生成RMSE柱状图和Step响应XY叠加图

**需求**：根据技术规格§3.2，新增3个功能

**需要新增的函数**：
1. `write_climbpath_trajectory_overlay(path::String, climbpath_rows)` — ClimbPath轨迹XY叠加图
2. `write_control_energy_bar(path::String, rows)` — 控制能量柱状图
3. `write_terminal_error_bar(path::String, rows)` — 终端误差柱状图

**需要新增的命令行参数**：
- `--climbpath` — 接受多个`controller_id=csv_path`参数

**调用方式**：
```bash
julia Scripts/syslab/compare_controllers.jl \
  --climbpath \
    official_pid=Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/raw/result.csv \
    lqr_baseline=Results/control_platform/phase2_full_48_climbpath/lqr_baseline/raw/result.csv \
    px4ctrl=Results/control_platform/phase2_full_48_climbpath/px4ctrl/raw/result.csv \
  --output-dir Docs/figures/test_compare
```

**新增输出文件**：
```
Docs/figures/test_compare/figures/
├── climbpath_rmse_bar.svg           # 复用现有函数write_climb_rmse_bar
├── climbpath_trajectory_overlay.svg # 新增：XY俯视图叠加
├── control_energy_bar.svg           # 新增：控制能量对比
├── terminal_error_bar.svg           # 新增：终端误差对比
```

**轨迹叠加图布局**：
- 单面板XY俯视图（不分X/Y两个面板）
- 参考轨迹：黑色虚线（stroke-dasharray="6,4"）
- 各控制器实际轨迹：用COLORS数组的不同颜色
- 图例：右上角，标注各控制器名称

**控制能量/终端误差柱状图**：
- 复用现有的`write_climb_rmse_bar`函数结构
- 修改Y轴标签和数据源（从metrics中读取`control_energy`或`terminal_position_error_m`）

**样式统一**：
- 继承现有COLORS数组、svg_escape、scaled等工具函数
- 字体：Times New Roman
- 图幅尺寸：980×560（与现有柱状图一致）

**验收标准**：
1. 用3个控制器的CSV运行扩展后的脚本，生成4个SVG
2. 轨迹叠加图中能清晰区分各控制器的轨迹
3. 柱状图的Y轴标签正确（"Control Energy" / "Terminal Error (m)"）
4. 所有SVG用浏览器打开无报错

---

### 【任务3】新增generate_status_matrix.py — 28控制器状态矩阵（P1）

**文件路径**：`Scripts/syslab/generate_status_matrix.py`（新建）

**需求**：根据技术规格§3.3，从G3_STATUS.json生成状态表格SVG

**输入数据**：
```json
// Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json
{
  "effective_run_record": [
    {
      "controller_id": "official_pid",
      "status": "accepted",
      "position_rmse_m": 0.276705,
      ...
    },
    ...
  ]
}
```

**调用方式**：
```bash
python Scripts/syslab/generate_status_matrix.py \
  --status-json Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json \
  --output Docs/figures/第10章/controller_status_matrix.svg
```

**输出格式**：28行的状态表格SVG，每行包含：
```
[序号] [控制器名] [族标签] [状态图标] [RMSE数值]
```

**状态图标**：
- ✅ accepted — 用绿色圆圈 `<circle fill="#2ca02c" r="8"/>`
- ❌ executed_blocked — 用红色叉号 `<path d="M-6,-6 L6,6 M-6,6 L6,-6" stroke="#d62728" stroke-width="2"/>`
- ⏸️ not_run — 用灰色暂停符号 `<rect fill="#999999" width="4" height="12"/>`

**控制器族映射表**（嵌入到脚本中）：
```python
CONTROLLER_FAMILY = {
    "official_pid": "PID族",
    "official_pid_yaw_authority_mapped": "PID族",
    "lqr_baseline": "线性/鲁棒族",
    "lqg": "线性/鲁棒族",
    "lqi": "线性/鲁棒族",
    "h_2_state_feedback": "线性/鲁棒族",
    "backstepping_baseline": "非线性/自适应族",
    "adaptive_backstepping": "非线性/自适应族",
    "feedback_linearization": "非线性/自适应族",
    "ndi": "非线性/自适应族",
    "passivity_based_control": "非线性/自适应族",
    "integral_smc": "滑模族",
    "terminal_smc": "滑模族",
    "nonsingular_terminal_smc": "滑模族",
    "adaptive_smc": "滑模族",
    "fuzzy_smc": "滑模族",
    "ilqr": "优化/预测族",
    "mppi": "优化/预测族",
    "explicit_gain_scheduled_mpc": "优化/预测族",
    "robust_mpc": "优化/预测族",
    "tube_mpc": "优化/预测族",
    "se_3_basic": "几何/微分平坦族",
    "dfbc_basic": "几何/微分平坦族",
    "dfbc_high_order": "几何/微分平坦族",
    "dfbc_high_order_body_rate": "几何/微分平坦族",
    "dfbc_smooth_robust": "几何/微分平坦族",
    "dfbc_smooth_robust_body_rate": "几何/微分平坦族",
    "px4ctrl": "工程基线",
}
```

**布局**：
- 按族分组，族之间用灰色分隔线
- 每行高度40px
- 总图幅：800px宽 × (28×40 + 分隔线) px高
- 字体：Times New Roman 11pt

**验收标准**：
1. SVG生成成功，用浏览器打开显示28行状态
2. 状态图标颜色正确（✅绿色/❌红色/⏸️灰色）
3. RMSE数值与G3_STATUS.json一致
4. 按族分组，族标签显示正确

---

### 【任务4】新增generate_heatmap.py — RMSE热力图（P1）

**文件路径**：`Scripts/syslab/generate_heatmap.py`（新建）

**需求**：根据技术规格§3.4，从28个metrics.csv生成RMSE热力图

**调用方式**：
```bash
python Scripts/syslab/generate_heatmap.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output Docs/figures/第10章/rmse_heatmap.svg
```

**数据扫描逻辑**：
1. 从`<batch-dir>/g3_repair/G3_STATUS.json`读取28个accepted控制器列表
2. 对每个控制器，读取`<batch-dir>/<controller_id>/metrics/metrics.csv`（或g3_repair子目录）
3. 提取`position_rmse_m`列的值

**热力图布局**：
- 28行（控制器）× 1列（ClimbPath50s场景）
- 左侧：控制器名称（按族分组）
- 右侧：颜色条（colorbar），标注RMSE范围

**颜色编码**（必须严格遵守）：
```python
def rmse_to_color(rmse):
    if rmse < 0.2:
        return "#2ca02c"  # 深绿
    elif rmse < 0.5:
        return "#7fbc41"  # 浅绿
    elif rmse < 1.0:
        return "#ffd92f"  # 黄
    elif rmse < 2.0:
        return "#ff7f0e"  # 橙
    else:
        return "#d62728"  # 红
    # NaN或失败：return "#cccccc"
```

**图幅尺寸**：
- 宽度：900px（左侧名称200px + 热力图600px + colorbar 100px）
- 高度：28行 × 30px = 840px

**验收标准**：
1. SVG生成成功，28个控制器全部显示
2. 颜色映射正确（低RMSE绿色，高RMSE红色）
3. colorbar标注清晰（0.2/0.5/1.0/2.0 m刻度线）
4. 控制器按族分组排列

---

### 【任务5】新增generate_radar_chart.py — 控制器族雷达图（P1）

**文件路径**：`Scripts/syslab/generate_radar_chart.py`（新建）

**需求**：根据技术规格§3.5，生成8个控制器族的性能雷达图

**调用方式**：
```bash
python Scripts/syslab/generate_radar_chart.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output Docs/figures/第10章/controller_radar_chart.svg
```

**雷达图5个维度**：
1. 位置RMSE（归一化：max=2.0m，越低越好 → 显示时取反：1 - rmse/2.0）
2. 终端误差（归一化：max=5.0m，越低越好 → 显示时取反）
3. 控制能量（归一化：相对Official PID，越低越好 → 显示时取反）
4. 最大误差（归一化：max=10.0m，越低越好 → 显示时取反）
5. 计算效率（暂时全部用1.0占位，未来接入求解时间）

**族聚合方式**：
- 每个族取该族内所有accepted控制器的**中位数**
- 如果某族只有1个控制器，直接用其数值
- 如果某族全部failed，雷达图显示为灰色虚线（值全为0）

**布局**：
- 2×4子图布局（8个族各占1个子图）
- 每个子图：正五边形，5条轴线从中心向外
- 总图幅：1600×1200 px

**样式**：
- 每个族用不同颜色填充（半透明alpha=0.3）
- 外框线：2.0pt实线
- 字体：Times New Roman 10pt
- 轴标签：5个维度名称标注在五边形顶点外侧

**验收标准**：
1. SVG生成成功，8个子图全部显示
2. 雷达图五边形形状正确
3. 各族的填充颜色不同且半透明
4. 维度标签清晰可读

---

### 【任务6】一键批处理脚本generate_all_chapter10_figures.py（P2）

**文件路径**：`Scripts/syslab/generate_all_chapter10_figures.py`（新建）

**需求**：根据技术规格§4.1，编排调用上述所有脚本

**调用方式**：
```bash
python Scripts/syslab/generate_all_chapter10_figures.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output-dir Docs/figures/第10章 \
  --focus-controllers official_pid,px4ctrl
```

**执行逻辑**：
```python
# Step 1: 加载28个accepted控制器列表
accepted = load_accepted_controllers(batch_dir)

# Step 2: 为focus_controllers生成完整4子图
for controller in focus_controllers:
    run_plot_results(controller, figures=["trajectory_xy", "altitude_z", "position_error", "control_input"])

# Step 3: 为其余历史批次控制器只生成trajectory_xy（工作量展示）
for controller in (accepted - focus_controllers):
    run_plot_results(controller, figures=["trajectory_xy"])

# Step 4: 按族分组生成对比图
pid_family = filter_by_family(accepted, "PID族")
run_compare_controllers(pid_family, "pid_family_comparison")

linear_family = filter_by_family(accepted, "线性/鲁棒族")
run_compare_controllers(linear_family, "linear_family_comparison")

# ... 其余各族同理

# Step 5: 生成状态矩阵、热力图、雷达图
run_generate_status_matrix()
run_generate_heatmap()
run_generate_radar_chart()

# Step 6: 生成ANALYSIS_REPORT.md
generate_summary_report(output_dir)
```

**输出结构**：
```
Docs/figures/第10章/
├── official_pid/                      # 完整4子图
├── px4ctrl/                           # 完整4子图
├── lqr_baseline/                      # 只有trajectory_xy
├── ...（其余24个控制器）
├── pid_family_comparison/
│   ├── climbpath_rmse_bar.svg
│   ├── climbpath_trajectory_overlay.svg
│   ├── control_energy_bar.svg
│   └── terminal_error_bar.svg
├── linear_family_comparison/
├── nonlinear_family_comparison/
├── smc_family_comparison/
├── mpc_family_comparison/
├── geometric_family_comparison/
├── controller_status_matrix.svg       # 图10-5a
├── rmse_heatmap.svg                   # 图10-5b
├── controller_radar_chart.svg         # 图10-5c
└── ANALYSIS_REPORT.md
```

**ANALYSIS_REPORT.md格式**：
```markdown
# Syslab分析汇总报告

生成时间: 2026-07-30 14:30:00

## 控制器统计

- 总数：28个
- 已通过G3门禁：28个
- 待验证：20个

## 位置RMSE汇总表

| 控制器 | 族 | RMSE (m) | 状态 |
|--------|-----|----------|------|
| official_pid | PID族 | 0.2767 | ✅ |
| px4ctrl | 工程基线 | 0.xxxx | ✅ |
| ... | ... | ... | ... |

## 生成的图表清单

- `official_pid/trajectory_xy.svg`
- `official_pid/altitude_z.svg`
- ...
```

**验收标准**：
1. 运行脚本无报错，完整生成所有目录和文件
2. `Docs/figures/第10章/`下有28个控制器子目录
3. focus_controllers有完整4子图，其余只有trajectory_xy
4. 各族对比图目录存在且包含4个SVG
5. ANALYSIS_REPORT.md格式正确，RMSE数值与metrics.csv一致

---

## 全局约束（所有任务必须遵守）

### 1. 代码风格
- Python脚本：使用`argparse`解析命令行参数，用`pathlib.Path`处理路径
- Julia脚本：继承现有`compare_controllers.jl`的函数命名和代码结构
- 不依赖matplotlib/pyplot，所有SVG手写XML标签（参考compare_controllers.jl）

### 2. 路径规范
- 所有路径使用正斜杠`/`，兼容Windows和Linux
- 输出目录不存在时自动创建（Python用`Path.mkdir(parents=True, exist_ok=True)`）
- 相对路径基准：项目根目录`C:/Users/HP/Desktop/MoSim`

### 3. 错误处理
- CSV缺少必需列时，打印清晰错误信息并退出（不生成部分文件）
- 如果metrics.csv中某个字段为空或NaN，跳过该图表但继续其他图表
- 所有subprocess调用需要检查返回码，失败时打印stderr

### 4. 日志输出
- 每个脚本开头打印：`[INFO] 脚本名 - 开始执行`
- 每生成一个文件打印：`[OK] 已生成: 文件路径`
- 脚本结束打印：`[DONE] 脚本名 - 完成，共生成N个文件`

### 5. 测试数据
- 使用Official PID的真实数据进行单元测试：
  - CSV: `Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/raw/result.csv`
  - Metrics: `Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/metrics/metrics.csv`

---

## 执行顺序建议

1. **先做任务1**（plot_results.py）— 这是其他任务的基础
2. **再做任务2**（compare_controllers.jl扩展）— 复用现有代码，改动相对小
3. **并行做任务3/4/5**（状态矩阵/热力图/雷达图）— 三个独立脚本，可同时开发
4. **最后做任务6**（一键批处理）— 需要前5个任务全部完成才能测试

---

## 提交检查清单

完成所有任务后，运行以下测试：

### 单元测试
```bash
# 任务1测试
python Scripts/results/plot_results.py \
  Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/raw/result.csv \
  /tmp/test_plot \
  --metrics Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/metrics/metrics.csv

# 任务2测试
julia Scripts/syslab/compare_controllers.jl \
  --climbpath \
    official_pid=Results/control_platform/phase2_full_48_climbpath/g3_repair/official_pid/raw/result.csv \
    lqr_baseline=Results/control_platform/phase2_full_48_climbpath/lqr_baseline/raw/result.csv \
  --output-dir /tmp/test_compare

# 任务3测试
python Scripts/syslab/generate_status_matrix.py \
  --status-json Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json \
  --output /tmp/test_status_matrix.svg

# 任务4测试
python Scripts/syslab/generate_heatmap.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output /tmp/test_heatmap.svg

# 任务5测试
python Scripts/syslab/generate_radar_chart.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output /tmp/test_radar.svg
```

### 集成测试
```bash
# 任务6测试（完整流程）
python Scripts/syslab/generate_all_chapter10_figures.py \
  --batch-dir Results/control_platform/phase2_full_48_climbpath \
  --output-dir /tmp/test_chapter10 \
  --focus-controllers official_pid,px4ctrl
```

### 最终验收
- [ ] 所有单元测试通过，生成的SVG用浏览器打开无报错
- [ ] 集成测试生成28个控制器目录
- [ ] official_pid和px4ctrl有完整4子图
- [ ] 其余历史批次控制器有trajectory_xy
- [ ] 6个族对比图目录存在且完整
- [ ] 状态矩阵、热力图、雷达图SVG存在且可视化正确
- [ ] ANALYSIS_REPORT.md格式正确，数值与原始数据一致

---

## 注意事项

1. **不要修改现有calc_metrics.jl和calc_metrics.py** — 这两个脚本已冻结，只读取其输出
2. **不要重新导出CSV** — 28个控制器的CSV已存在，直接使用
3. **不要修改报告骨架** — 本次任务只生成图表，不修改报告文档
4. **遇到问题先检查技术规格** — 所有设计细节都在`Syslab图表生成技术规格.md`中

---

## 完成标志

当以下文件全部生成且通过验收时，任务完成：

1. `Scripts/results/plot_results.py` — 补全完成
2. `Scripts/syslab/compare_controllers.jl` — 扩展完成
3. `Scripts/syslab/generate_status_matrix.py` — 新增完成
4. `Scripts/syslab/generate_heatmap.py` — 新增完成
5. `Scripts/syslab/generate_radar_chart.py` — 新增完成
6. `Scripts/syslab/generate_all_chapter10_figures.py` — 新增完成
7. `Docs/figures/第10章/` — 完整目录树生成
8. `Docs/figures/第10章/ANALYSIS_REPORT.md` — 汇总报告生成

完成后，将以下两个文件发给用户审查：
1. 技术规格文档：`Docs/Workflows/Syslab图表生成技术规格.md`
2. 本任务指令文档：`Docs/Workflows/Codex_Syslab_batch_instructions.md`
