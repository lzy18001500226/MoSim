# 第10章 Syslab 图表工具链测试日志

生成日期：2026-07-31（CST）

## 已通过的自动检查

| 检查项 | 命令或方法 | 结果 |
|---|---|---|
| Python 语法 | `python -m py_compile Scripts/results/plot_results.py Scripts/syslab/generate_status_matrix.py Scripts/syslab/generate_heatmap.py Scripts/syslab/generate_radar_chart.py Scripts/syslab/generate_all_chapter10_figures.py` | 通过 |
| Julia 自检 | `julia Scripts/syslab/compare_controllers.jl --self-test` | 通过 |
| 完整批处理 | `python Scripts/syslab/generate_all_chapter10_figures.py --batch-dir Results/control_platform/phase2_full_48_climbpath --output-dir Docs/figures/第10章 --focus-controllers official_pid,px4ctrl` | 通过 |
| 批处理契约 | `VALIDATION_REPORT.json` | 28 个 accepted 控制器、6 个族内对比目录、61 个 SVG，`passed=true` |
| SVG XML | PowerShell XML 解析 61 个 SVG | 61/61 通过 |
| 静态依赖 | 搜索 `matplotlib`、`pyplot`、`Arial` | 无命中 |
| 文本产物换行 | 递归检查 `.csv/.json/.md/.svg/.txt` | 全部为 LF |
| 数据一致性 | `ANALYSIS_REPORT.md` 与每个有效 `metrics.csv` 的 RMSE 字段逐行匹配 | 28/28 通过 |

## 手工与浏览器审查边界

本执行环境中，Chrome 与 Edge 的 headless 启动均统一返回退出码 `21` 且没有标准错误输出；内置浏览器对本地 `file://` 路径执行了 URL 安全策略拦截。因此，自动浏览器渲染并未被声明为通过，也没有把该环境限制解释为 SVG 错误。

已完成的替代性机器验证是 XML 解析、SVG 目录契约、字体/依赖静态检查和数据一致性检查。交付前的人工浏览器审查应至少打开下列代表性文件，确认页面没有浏览器解析提示且曲线和文本可读：

- `official_pid/trajectory_xy.svg`
- `official_pid/altitude_z.svg`
- `controller_status_matrix.svg`
- `rmse_heatmap.svg`
- `controller_radar_chart.svg`

完整的批处理子命令与每个子脚本的标准输出见 `GENERATION_LOG.txt`。
