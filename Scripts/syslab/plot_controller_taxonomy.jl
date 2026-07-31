# 控制器分类可视化（族系来自 control_scheme_catalog.json，状态来自 G3_STATUS.json）
# 生成 2 张分类图：族系分组堆叠横条、达标率横条。
# 原设计为 4 张，达标率雷达图与失败分布饼图已于 2026-07-31 废弃，废弃理由见文件末尾。
#
# 口径说明（不要改回手写映射）：
#   族系归属唯一来自目录的 category 字段，不得手写。目录用设计侧 ID，
#   G3 用执行侧 ID，两套命名靠 scheme_id_alias_map.json 桥接。
#   目录 48 条中 41 条能对齐 G3 行，本图只统计这 41 条。
#   另有 7 条目录条目无 G3 行、7 条 G3 行无目录条目（后者无目录术语，
#   按 claim_boundary 不得挂族系标签），单列为 execution-only 说明。
#   41 条中达标 27 条；加上执行侧独有的 official_pid_yaw_authority_mapped
#   共 28 条达标，与 effective_passed_count 一致。
# 口径权威：Config/control_platform/climbpath_baseline_count_definition.json

using TyPlot
using JSON

# 读取G3有效状态文件
status_path = "Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json"
data = JSON.parsefile(status_path)

# 读取控制器目录与别名映射
catalog_path = "Config/control_platform/control_scheme_catalog.json"
catalog = JSON.parsefile(catalog_path)
alias_path = "Config/control_platform/scheme_id_alias_map.json"
alias_doc = JSON.parsefile(alias_path)

# 设计侧 scheme_id -> 执行侧 controller_id
alias = Dict{String,String}()
for a in alias_doc["aliases"]
    if a["g3_controller_id"] !== nothing
        alias[a["catalog_scheme_id"]] = a["g3_controller_id"]
    end
end

rows_by_id = Dict(r["controller_id"] => r for r in data["rows"])

# 族系顺序与英文标签（图上不显示中文，防止字体回退）
family_order = ["pid_family", "linear_robust_state_feedback", "nonlinear_adaptive",
                "sliding_mode", "optimization_predictive", "geometric_flatness",
                "learning", "engineering_deployment_baseline"]
family_labels = ["PID", "Linear Robust", "Nonlinear Adaptive", "Sliding Mode",
                 "Optimization", "Geometric", "Learning", "Engineering Baseline"]

# 从目录 category 派生分组，只统计能对齐 G3 的条目
family_total = zeros(Int, length(family_order))
family_passed = zeros(Int, length(family_order))
aligned_ids = String[]

for s in catalog["schemes"]
    sid = s["scheme_id"]
    gid = get(alias, sid, sid)
    haskey(rows_by_id, gid) || continue
    idx = findfirst(==(s["category"]), family_order)
    idx === nothing && continue
    family_total[idx] += 1
    push!(aligned_ids, gid)
    if rows_by_id[gid]["status"] == "pass"
        family_passed[idx] += 1
    end
end

family_names = family_labels
@assert sum(family_total) == 41 "对齐条目应为 41，实际 $(sum(family_total))"
@assert sum(family_passed) == 27 "对齐达标应为 27，实际 $(sum(family_passed))"
println("族系统计：对齐 $(sum(family_total)) 条，其中达标 $(sum(family_passed)) 条")
println("执行侧独有 $(length(setdiff(keys(rows_by_id), aligned_ids))) 条不挂族系标签")

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
