# 布局探针 v4 —— 验证 typlot_figure_style.jl：
#   (1) ticklab_* 封死顺序后，长词组标签是否恢复 Times New Roman
#   (2) 字号随画幅等比缩放后，大画布上字是否不再显小
#   (3) pie 的 labels 字体能否控制（TyPlot Python 侧不在磁盘，只能实测）
#   (4) 堆叠横条替代饼图 / 极坐标的效果
using TyPlot, JSON, DelimitedFiles

const BASE = raw"C:\Users\HP\Desktop\MoSim"
include(joinpath(BASE, "Scripts", "syslab", "typlot_figure_style.jl"))
const OUT = joinpath(BASE, ".tmp", "typlot_probe_v4")
mkpath(OUT)

out(n) = joinpath(OUT, n * ".png")

function report(p)
    io = open(p, "r"); b = read(io, 33); close(io)
    w = Int(b[17])<<24 | Int(b[18])<<16 | Int(b[19])<<8 | Int(b[20])
    h = Int(b[21])<<24 | Int(b[22])<<16 | Int(b[23])<<8 | Int(b[24])
    println("  ", rpad(basename(p), 36), "$(w)x$(h)  ",
            round(w/FIG_RES, digits=1), "x", round(h/FIG_RES, digits=1), " in",
            "  label=", lab_pt(fig_w()), "pt tick=", tik_pt(fig_w()), "pt")
end

const FAM_ORDER = ["pid_family", "linear_robust_state_feedback", "nonlinear_adaptive",
    "sliding_mode", "optimization_predictive", "geometric_flatness",
    "learning", "engineering_deployment_baseline"]
const FAM_LABEL = ["PID", "Linear Robust", "Nonlinear Adaptive", "Sliding Mode",
    "Optimization", "Geometric", "Learning", "Engineering Baseline"]

function family_stats()
    data = JSON.parsefile(joinpath(BASE, "Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json"))
    cat = JSON.parsefile(joinpath(BASE, "Config/control_platform/control_scheme_catalog.json"))
    ad = JSON.parsefile(joinpath(BASE, "Config/control_platform/scheme_id_alias_map.json"))
    al = Dict{String,String}()
    for a in ad["aliases"]
        a["g3_controller_id"] !== nothing && (al[a["catalog_scheme_id"]] = a["g3_controller_id"])
    end
    rows = Dict(r["controller_id"] => r for r in data["rows"])
    tot = zeros(Int, 8); pas = zeros(Int, 8)
    for s in cat["schemes"]
        gid = get(al, s["scheme_id"], s["scheme_id"])
        haskey(rows, gid) || continue
        i = findfirst(==(s["category"]), FAM_ORDER); i === nothing && continue
        tot[i] += 1
        rows[gid]["status"] == "pass" && (pas[i] += 1)
    end
    return tot, pas
end

TOT, PAS = family_stats()
RATE = [TOT[i] > 0 ? PAS[i] / TOT[i] * 100 : 0.0 for i in eachindex(TOT)]
# 标签自带样本量：解决"Learning 0/2 与 PID 1/7 都显示 0%/14% 看不出分母"
LAB_N = [FAM_LABEL[i] * " (n=" * string(TOT[i]) * ")" for i in eachindex(TOT)]
println("对齐 ", sum(TOT), " / 达标 ", sum(PAS))

# ===== 探针 1：达标率横条，替代 taxonomy_radar 的极坐标 =====
fig(10, 7)
barh(1:8, RATE)
hold("on")
for i in 1:8
    annot(RATE[i] + 2, i, string(round(RATE[i], digits=1)) * "%")
end
ticklab_y(1:8, LAB_N)
styled(xlabel("Performance-Accepted Rate (%)"))
styled(ylabel("Controller Family"))
xlim([0, 120]); grid("on")
report(save_fig(out("p1_pass_rate_barh_10x7")))

# ===== 探针 2：堆叠横条，替代 taxonomy_failed_pie 的饼图 =====
# 达标 + 未达标 = 对齐条目数，缺口即未达标，分母可见
fig(10, 7)
barh(1:8, hcat(PAS, TOT .- PAS), style="stacked")
ticklab_y(1:8, FAM_LABEL)
styled(xlabel("Catalog-Aligned Entries (n = $(sum(TOT)))"))
styled(ylabel("Controller Family"))
styled_legend(["Performance-Accepted", "Not Accepted"]; loc="southeast")
grid("on")
report(save_fig(out("p2_stacked_barh_10x7")))

# ===== 探针 3：pie 字体能否控（实测 autopct 与 labels 字体）=====
failed = TOT .- PAS
fl = String[]; fc = Int[]
for i in 1:8
    failed[i] > 0 && (push!(fl, FAM_LABEL[i] * " " * string(failed[i])); push!(fc, failed[i]))
end
fig(10, 8)
pie(fc, labels=fl, autopct="%1.1f%%")
axes_font()
report(save_fig(out("p3_pie_fontcheck_10x8")))

println("\n探针 v4 完成 -> ", OUT)
