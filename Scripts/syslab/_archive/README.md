# Syslab 脚本归档（2026-08-01）

归档不等于删除。以下脚本已不参与当前报告图件生成链路。

## 布局探针（开发产物）

`probe_figure_layout_v2.jl` … `probe_figure_layout_v6.jl`、`probe_heatmap_font.jl`

用于确定 TyPlot 导出参数（`figsize` 生效、`OuterPosition` 对 `exportgraphics`
无效）与热力图字号。结论已固化进 `typlot_figure_style.jl` 与各正式绘图脚本，
探针本身不再需要运行。

## 已被取代的详图生成器

`plot_28_passed_controllers_detail.jl`（449 行）

被 `plot_28_passed_detail_typlot.jl` 取代。后者在同样的 7 张/控制器口径上
增加了负样本模式（`DETAIL_NEGATIVE_SAMPLE_IDS`），并在 manifest 中标注
`negative_sample` / `failure_class`，因此 awff 详图可以在不破坏
"达标数 = 28"断言的前提下生成。旧脚本的头注释仍写着"awff 已归档"，
与当前状态不一致，保留仅作历史对照。

口径权威仍为 `Config/control_platform/climbpath_baseline_count_definition.json`。
