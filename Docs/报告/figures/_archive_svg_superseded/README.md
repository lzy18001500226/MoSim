# 已被 TyPlot PNG 取代的 SVG 归档

归档日期：2026-08-01

## 归档原因

本目录 42 个 SVG 均为**手写/脚本生成**图元，不是 Syslab (TyPlot) 真实输出。
报告图形口径要求全部图形来自 MWORKS/Syslab 实跑，故这些 SVG 全部被同名
TyPlot PNG（600 dpi、Times New Roman）取代。

目录结构保持原始相对路径，便于溯源。每个 SVG 在原位置都有同名 `.png` 替代。

## 清单

- 第10章：33 个（6 族系 × 4 + 雷达 8 + controller_radar_chart）
- 第11章：9 个（七场景对比 6 + 灵敏度分析 3）

## 追加归档（2026-08-01，用户决定清理）

`第10章/controller_status_matrix.svg`
`第10章/rmse_heatmap.svg`

这两个**没有 PNG 替代**。用户决定不补 TyPlot 版，直接清理。
**副作用**：正文 `仿真分析报告_正文骨架.md` 793 / 800 行的图10-5a / 图10-5b
引用随之失效，需在引用修正批次中一并删除这两条引用。

`第10章/DIRECTORY_TREE.png`

出自 `Scripts/syslab/generate_all_chapter10_figures.py`，是 Python 产物而非
TyPlot 实跑，且正文从未引用，属旧 Python 管线残留，一并归档。

## 归档后状态

`figures/` 下已无 SVG，258 张 PNG 全部为 TyPlot 实跑产物。
