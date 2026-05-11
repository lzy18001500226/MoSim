# results 结果审核入口

本目录按模型/场景在根目录直接分组。每个结果组内部再按资产类型划分为 `raw/`、`metrics/`、`replay/`、`logs/`、`figures/`，人工审核以 `人工审核清单.csv` 为入口。

## 分类规则

| 分类 | 用途 | 审核优先级 |
|---|---|---|
| `official/example3_figure8/` | 官方 Example3 8 字形轨迹，视频与报告高优先级素材 | high |
| `official/example2_helix/` | 官方 Example2 螺旋爬升 | medium |
| `official/example1_step/` | 官方 Example1 阶梯爬升和控制器对比 | medium |
| `robustness/mass20_example1/` | 质量摄动鲁棒性 | medium |
| `robustness/wind_gust_example1/` | 横向阵风鲁棒性 | medium |
| `robustness/rotor1_loss15_example1/` | 单旋翼效率下降鲁棒性 | medium |
| `smoke/` | 0-1 s MCP 链路烟雾验证，只证明流程通，不作为最终展示素材 | low |

## 当前数量

- `example1_step`: 6 组
- `example1_step_smoke`: 3 组
- `example2_helix`: 3 组
- `example3_figure8`: 3 组
- `mass20_example1`: 4 组
- `rotor1_loss15_example1`: 4 组
- `wind_gust_example1`: 5 组

## 人工审核要求

1. 优先审核 `official/example3_figure8/` 下的 `raw/`、`metrics/`、`replay/`、`figures/`。这才是 8 字形轨迹相关证据。
2. `smoke/` 目录默认不进入演示视频和正式报告主图，只保留为自动化链路证据。
3. 每次新增或重生成图后，更新 `人工审核清单.csv` 的 `review_status` 和 `notes`。
4. 图不合格时不要删除同组 raw/metrics/replay/logs；在清单里标注原因，再决定是否重新生成。
