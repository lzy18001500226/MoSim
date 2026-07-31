# Python 绘图旧详图归档（2026-07-31）

## 归档原因

本目录为 28 条性能达标控制器的**旧详图**，共 112 张 SVG（4 张/控制器）
＋ 28 份 `figure_manifest.json`。

这批图由 `Scripts/results/plot_results.py` 生成，**是手写 SVG XML，不是 Syslab 输出**。
schema 统一为 `mosim.plot_results.v1`。

2026-07-31 已由 TyPlot 原生重绘替代，新图为真 Syslab 产物：

| 项 | 旧（本目录） | 新（正文） |
|---|---|---|
| 生成器 | `Scripts/results/plot_results.py` | `Scripts/syslab/plot_28_passed_detail_typlot.jl` |
| 引擎 | Python 手写 SVG XML | Syslab TyPlot 1.0.47 |
| schema | `mosim.plot_results.v1` | `mosim.typlot_detail.v1` |
| 格式 | SVG | PNG @ resolution=600（3360×2520） |
| 张数/控制器 | 4 | 7 |
| 总张数 | 112 | 196 |

## 旧 4 图与新 7 图的对应

旧图名全部被新图覆盖，无信息丢失：

- `trajectory_xy` → 保留同名
- `altitude_z` → 保留同名
- `position_error` → 保留同名
- `control_input` → 保留同名
- 新增 `trajectory_3d`（x-y-z 立体轨迹，`plot3`）
- 新增 `velocity`（vx / vy / vz）
- 新增 `attitude`（roll / pitch / yaw）

新增 3 张覆盖了旧版式闲置的 6 列数据（vx, vy, vz, roll, pitch, yaw）。
18 列 CSV 至此全部被利用。

## 口径说明

- 归档不等于删除。若需追溯 2026-07-31 之前的图，引用本目录。
- **本目录图不得作为 Syslab 绘图证据**，因其为 Python 产物。
- 数据源未变：两批图同读
  `Results/control_platform/phase2_full_48_climbpath/<id>/raw/climbpath50s.csv`，
  重绘只换绘图引擎，不改数据。

正文新图位置：`Docs/报告/figures/第10章/<controller_id>/*.png`
口径权威：`Config/control_platform/climbpath_baseline_count_definition.json`
