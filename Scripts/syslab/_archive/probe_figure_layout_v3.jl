# 布局探针 v3 —— 覆盖 v2 未验证的 5 种原型：3D 轨迹 / 饼图 / 箱线 / 直方图 /
# 8 长标签竖柱 / 8 长标签极坐标。只写 .tmp/，不动已交付图。
using TyPlot, JSON, DelimitedFiles

const BASE = raw"C:\Users\HP\Desktop\MoSim"
const OUT  = joinpath(BASE, ".tmp", "typlot_probe_v3")
const RES  = 600
const FONT = "Times New Roman"
const SZL  = 18
const SZT  = 16
mkpath(OUT)

fig(w, h) = figure(figsize=[w, h])

function style_axes()
    a = gca()
    plt_set(a, "fontname", FONT)
    plt_set(a, "fontsize", SZT)
end

styled(h) = (plt_set(h, "fontname", FONT); plt_set(h, "fontsize", SZL); h)

function save(name)
    p = joinpath(OUT, name * ".png")
    exportgraphics(gcf(), p, resolution=RES)
    io = open(p, "r"); b = read(io, 33); close(io)
    w = Int(b[17])<<24 | Int(b[18])<<16 | Int(b[19])<<8 | Int(b[20])
    h = Int(b[21])<<24 | Int(b[22])<<16 | Int(b[23])<<8 | Int(b[24])
    println("  ", rpad(name * ".png", 30), "$(w)x$(h)  ",
            round(w/RES, digits=1), "x", round(h/RES, digits=1), " in")
end

thin(v, n=1200) = length(v) <= n ? v : v[1:cld(length(v), n):end]

# ---- 族系统计（口径同 plot_controller_taxonomy.jl：目录 category + 别名桥接，只统 41 条对齐）
const FAM_ORDER = ["pid_family", "linear_robust_state_feedback", "nonlinear_adaptive",
    "sliding_mode", "optimization_predictive", "geometric_flatness",
    "learning", "engineering_deployment_baseline"]
const FAM_LABEL = ["PID", "Linear Robust", "Nonlinear Adaptive", "Sliding Mode",
    "Optimization", "Geometric", "Learning", "Engineering Baseline"]

function family_stats()
    data = JSON.parsefile(joinpath(BASE, "Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json"))
    catalog = JSON.parsefile(joinpath(BASE, "Config/control_platform/control_scheme_catalog.json"))
    alias_doc = JSON.parsefile(joinpath(BASE, "Config/control_platform/scheme_id_alias_map.json"))
    alias = Dict{String,String}()
    for a in alias_doc["aliases"]
        a["g3_controller_id"] !== nothing && (alias[a["catalog_scheme_id"]] = a["g3_controller_id"])
    end
    rows = Dict(r["controller_id"] => r for r in data["rows"])
    tot = zeros(Int, length(FAM_ORDER)); pas = zeros(Int, length(FAM_ORDER))
    for s in catalog["schemes"]
        gid = get(alias, s["scheme_id"], s["scheme_id"])
        haskey(rows, gid) || continue
        i = findfirst(==(s["category"]), FAM_ORDER); i === nothing && continue
        tot[i] += 1
        rows[gid]["status"] == "pass" && (pas[i] += 1)
    end
    return tot, pas
end

TOT, PAS = family_stats()
println("对齐 ", sum(TOT), " 条 / 达标 ", sum(PAS), " 条")

# ============ 探针 1：3D 轨迹（plot3，三轴刻度是否挤）============
idx = joinpath(BASE, ".tmp", "chapter10_typlot", "accepted_controller_index.csv")
iraw, ihdr = readdlm(idx, ',', header=true)
icols = vec(String.(ihdr))
IR = [Dict(icols[j] => iraw[i, j] for j in eachindex(icols)) for i in 1:size(iraw, 1)]
row1 = IR[1]
craw, chdr = readdlm(string(row1["raw_csv"]), ',', header=true)
ccols = vec(String.(chdr))
col(k) = (j = findfirst(==(k), ccols); j === nothing ? nothing : thin(Float64.(craw[:, j])))

fig(9, 7.5)
plot3(col("x"), col("y"), col("z"), linewidth=2.0)
hold("on")
plot3(col("x_ref"), col("y_ref"), col("z_ref"), linestyle="--", linewidth=1.5)
style_axes()
styled(xlabel("X (m)")); styled(ylabel("Y (m)")); styled(zlabel("Z (m)"))
lg = legend(["Actual", "Reference"]; loc="northeast"); plt_set(lg, "fontname", FONT); plt_set(lg, "fontsize", 14)
grid("on")
save("p1_traj3d_9x7p5")

# ============ 探针 2：饼图（长族系名 + 百分比是否重叠）============
failed = TOT .- PAS
fl = String[]; fc = Int[]
for i in eachindex(FAM_LABEL)
    failed[i] > 0 && (push!(fl, FAM_LABEL[i]); push!(fc, failed[i]))
end
println("饼图分片 ", length(fc), " 片: ", fl, " = ", fc)
fig(10, 8)
pie(fc, labels=fl, autopct="%1.1f%%")
style_axes()
save("p2_failed_pie_10x8")

# ============ 探针 3：箱线图 + 直方图 ============
num(r, k) = (v = r[k]; v isa Number ? Float64(v) : (x = tryparse(Float64, string(v)); x === nothing ? NaN : x))
rmse = [num(r, "position_rmse_m") for r in IR]
term = [num(r, "terminal_position_error_m") for r in IR]

fig(7, 8)
boxchart(ones(length(rmse)), rmse)
style_axes()
styled(ylabel("Position RMSE (m)"))
styled(xlabel("Performance-Accepted Controllers (n = $(length(rmse)))"))
grid("on")
save("p3a_box_7x8")

fig(10, 6)
histogram(rmse, 10)
style_axes()
styled(xlabel("Position RMSE (m)")); styled(ylabel("Controller Count"))
grid("on")
save("p3b_hist_10x6")

# ============ 探针 4：8 长标签竖柱（分组）============
fig(12, 6.5)
bar(1:length(FAM_LABEL), TOT)
hold("on")
bar(1:length(FAM_LABEL), PAS)
style_axes()
xticks(1:length(FAM_LABEL)); xticklabels(FAM_LABEL)
styled(ylabel("Controller Count")); styled(xlabel("Controller Family"))
lg = legend(["Catalog-Aligned", "Performance-Accepted"]; loc="northeast")
plt_set(lg, "fontname", FONT); plt_set(lg, "fontsize", 14)
grid("on")
save("p4a_family_bars_vertical_12x6p5")

# 备选：横向 barh，长标签天然水平不旋转
fig(10, 7)
barh(1:length(FAM_LABEL), TOT)
style_axes()
yticks(1:length(FAM_LABEL)); yticklabels(FAM_LABEL)
styled(xlabel("Catalog-Aligned Entries")); styled(ylabel("Controller Family"))
grid("on")
save("p4b_family_barh_10x7")

# ============ 探针 5：8 长标签极坐标（最可能"字堆一起"）============
rate = [TOT[i] > 0 ? PAS[i] / TOT[i] * 100 : 0.0 for i in eachindex(TOT)]
ang = collect(0:2π/length(FAM_LABEL):2π-0.01)

fig(11, 11)
polarplot([ang; ang[1]], [rate; rate[1]], "-o", linewidth=2.5)
style_axes()
rlim([0, 100])
thetaticks(rad2deg.(ang)); thetaticklabels(FAM_LABEL)
save("p5a_pass_rate_polar_11x11")

# 备选：极坐标标签太长时改横向条形，达标率直读
fig(10, 7)
barh(1:length(FAM_LABEL), rate)
hold("on")
for i in eachindex(rate)
    text(rate[i] + 2, i, string(round(rate[i], digits=1)) * "%", fontsize=13, fontname=FONT)
end
style_axes()
yticks(1:length(FAM_LABEL)); yticklabels(FAM_LABEL)
xlim([0, 118])
styled(xlabel("Performance-Accepted Rate (%)")); styled(ylabel("Controller Family"))
grid("on")
save("p5b_pass_rate_barh_10x7")

println("\n探针 v3 完成 -> ", OUT)
