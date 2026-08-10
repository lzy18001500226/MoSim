# 控制器分类可视化（族系与状态来自当前目录 48 条对账）
# 生成 2 张分类图：族系分组堆叠横条、达标率横条。
# 原设计为 4 张，达标率雷达图与失败分布饼图已于 2026-07-31 废弃，废弃理由见文件末尾。
#
# 口径说明：
#   当前目录对账已经把 48 条 catalog entry、类别和当前状态放在同一份
#   G3_CATALOG_48_CURRENT_STATUS.json 中。本图直接读取该文件，避免把历史
#   G3_STATUS.json 的 28 条快照与当前 30/48 结果混用。

using TyPlot
using JSON

# 读取当前目录 48 条对账文件
status_path = "Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json"
data = JSON.parsefile(status_path)

# 族系顺序与英文标签（图上不显示中文，防止字体回退）
family_order = ["pid_family", "linear_robust_state_feedback", "nonlinear_adaptive",
                "sliding_mode", "optimization_predictive", "geometric_flatness",
                "learning", "engineering_deployment_baseline"]
family_labels = ["PID", "Linear Robust", "Nonlinear Adaptive", "Sliding Mode",
                 "Optimization", "Geometric", "Learning", "Engineering Baseline"]

# 当前对账已经完成目录/执行归并，直接按 category 派生分组
category_to_index = Dict(
    "pid_family" => 1,
    "linear_robust_state_feedback" => 2,
    "nonlinear_adaptive" => 3,
    "sliding_mode" => 4,
    "optimization_predictive" => 5,
    "geometric_flatness" => 6,
    "learning" => 7,
    "engineering_deployment_baseline" => 8,
)
family_total = zeros(Int, length(family_order))
family_passed = zeros(Int, length(family_order))

for row in data["rows"]
    idx = get(category_to_index, String(row["category"]), 0)
    idx == 0 && error("当前对账行缺少可识别 category: $(row["scheme_id"])")
    family_total[idx] += 1
    if String(row["status"]) == "pass"
        family_passed[idx] += 1
    end
end

family_names = family_labels
@assert sum(family_total) == 48 "当前目录条目应为 48，实际 $(sum(family_total))"
@assert sum(family_passed) == 30 "当前目录达标应为 30，实际 $(sum(family_passed))"
println("当前目录族系统计：$(sum(family_total)) 条，其中达标 $(sum(family_passed)) 条")

# 排版标准（已审定）：Times New Roman、无中文、无标题；画幅与字号规范见
# typlot_figure_style.jl（figsize 定画幅、字号随画幅等比、刻度标签顺序封死）
include(joinpath(@__DIR__, "typlot_figure_style.jl"))

const OUTDIR = "Docs/报告/figures/第10章"

# 表示法修正（2026-07-31 审定）：
#   竖柱 -> 横条：8 个长族系名（"Engineering Baseline"）挤横轴，12in 画幅仍重叠，
#     是槽位结构问题，放大画布治不了。
#   极坐标 -> 横条：达标率是各族独立量，闭合折线暗示族间可插值且围出的面积无意义，
#     还抹掉样本量（Learning 0/2 与 PID 1/7 都贴近圆心）。横条直读百分比并标注 n。
#   饼图 -> 堆叠横条：TyPlot 这版 pie 的 autopct 被静默忽略（实测无百分比渲染），
#     且 labels 是独立 text 对象，gca 字体管不到，必然回退无衬线。堆叠横条
#     同时给出分母、达标数、未达标数，信息量严格更大。

x = 1:length(family_names)
n_aligned = sum(family_total)

# 图1：各族系条目数与达标数（堆叠横条，同时替代原饼图）
fig(10, 7)
barh(x, hcat(family_passed, family_total .- family_passed), style="stacked")
ticklab_y(x, family_names)
styled(xlabel("Catalog-Aligned Entries (n = $n_aligned)"))
styled(ylabel("Controller Family"))
styled_legend(["Performance-Accepted", "Not Accepted"]; loc="southeast")
grid("on")
save_fig(joinpath(OUTDIR, "taxonomy_family_bars.png"))

# 图2：各族系达标率（横条，标签自带样本量）
pass_rates = [family_total[i] > 0 ? family_passed[i] / family_total[i] * 100 : 0.0
              for i in eachindex(family_total)]
labels_n = [family_names[i] * " (n=" * string(family_total[i]) * ")" for i in eachindex(family_total)]

fig(10, 7)
barh(x, pass_rates)
hold("on")
for i in eachindex(pass_rates)
    annot(pass_rates[i] + 2, i, string(round(pass_rates[i], digits=1)) * "%")
end
ticklab_y(x, labels_n)
styled(xlabel("Performance-Accepted Rate (%)"))
styled(ylabel("Controller Family"))
xlim([0, 120])
grid("on")
save_fig(joinpath(OUTDIR, "taxonomy_pass_rate.png"))

# 原图3（达标率极坐标雷达）与图4（未达标族系饼图）已于 2026-07-31 废弃：
#   雷达：达标率非循环量，闭合折线暗示族间可插值、围出面积无解释，且抹掉样本量。
#         其信息已由图2 横条承接（直读百分比 + 标签带 n）。
#   饼图：TyPlot pie 的 autopct 实测被静默忽略、labels 字体无法控（回退无衬线）。
#         其信息已由图1 堆叠横条承接（分母 + 达标 + 未达标一图全含）。
# 旧文件 taxonomy_radar.png / taxonomy_failed_pie.png 已不再生成，正文引用已于
# 2026-08-01 核对确认为零，无需再移除。

println("✓ 控制器分类图生成完成（4 张 -> 2 张，表示法修正）")
println("  - taxonomy_family_bars.png (堆叠横条：族系条目数与达标数)")
println("  - taxonomy_pass_rate.png (横条：达标率 + 样本量)")
println("\n统计摘要:")
for i in 1:length(family_names)
    println("  $(family_names[i]): $(family_passed[i])/$(family_total[i]) ($(round(pass_rates[i], digits=1))%)")
end
println("\n总计: $(sum(family_passed))/$(sum(family_total)) ($(round(sum(family_passed)/sum(family_total)*100, digits=1))%)")
