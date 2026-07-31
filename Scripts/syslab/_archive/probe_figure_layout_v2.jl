# 布局修复探针 v2 —— 只写 .tmp/，不动已交付图
# 根因：画布 1500px + 18pt 字 => 字占画幅 1.67%，插报告(15cm)后仅 7.1pt
# 修法：画布压到 900px => 2.78%，插报告后 11.8pt，与正文齐平
using TyPlot, DelimitedFiles

const BASE = raw"C:\Users\HP\Desktop\MoSim"
const IDX  = joinpath(BASE, ".tmp", "chapter10_typlot", "accepted_controller_index.csv")
const OUT  = joinpath(BASE, ".tmp", "typlot_probe_v2")
const RES  = 600
const FONT = "Times New Roman"
const SZL  = 18
const SZT  = 16

mkpath(OUT)

# 关键：OuterPosition 只影响屏幕窗口，对 exportgraphics 输出尺寸无效。
# 唯一控制导出画幅的是 figure(figsize=[w,h])，单位英寸，默认 [6.4,4.8] -> 裁边后 5.6x4.2。
# 反推：图按 15cm(5.9in) 插报告，欲使 18pt 字渲染成 ~10.5pt(=正文字号)，需画布宽 ~10in。
fig(w, h) = figure(figsize=[w, h])

function read_index()
    raw, hdr = readdlm(IDX, ',', String, header=true)
    cols = vec(hdr)
    return [Dict(cols[j] => raw[i, j] for j in eachindex(cols)) for i in 1:size(raw, 1)]
end

num(r, k) = (v = get(r, k, ""); isempty(v) ? NaN : something(tryparse(Float64, v), NaN))

function style_axes()
    a = gca()
    plt_set(a, "fontname", FONT)
    plt_set(a, "fontsize", SZT)
end

styled(h) = (plt_set(h, "fontname", FONT); plt_set(h, "fontsize", SZL); h)

function save(name)
    p = joinpath(OUT, name)
    exportgraphics(gcf(), p, resolution=RES)
    println("  ", name, "  ", filesize(p), " B")
    return p
end

function thin(v, maxpts=1200)
    n = length(v)
    n <= maxpts && return v
    step = max(1, ceil(Int, n / maxpts))
    idx = collect(1:step:n)
    idx[end] == n || push!(idx, n)
    return v[idx]
end

function read_raw(path)
    raw, hdr = readdlm(path, ',', Float64, header=true)
    cols = vec(hdr)
    return Dict(cols[j] => raw[:, j] for j in eachindex(cols))
end

rows  = read_index()
geo   = [r for r in rows if r["family_slug"] == "geometric"]
sort!(geo, by = r -> num(r, "position_rmse_m"))
println("geometric n=", length(geo))

# ---- 探针 1：barh 柱状图（替代 bar + xtickangle(30)）----
# 控制器名放 y 轴横向正读，不旋转；条形末端直接标数值
fig(10, 6.0)
ids  = [r["controller_id"] for r in geo]
vals = [num(r, "position_rmse_m") for r in geo]
barh(1:length(vals), vals)
# 注意：barh(text=...) 能在窗口渲染但 exportgraphics 会崩，必须用 text() 手动标
hold("on")
for i in eachindex(vals)
    text(vals[i] + maximum(vals) * 0.02, i, string(round(vals[i], digits=3)),
         fontsize=13, fontname=FONT)
end
yticks(1:length(vals)); yticklabels(ids)
xlim([0, maximum(vals) * 1.22])
style_axes()
styled(xlabel("ClimbPath50s Position RMSE (m)"))
grid("on"); hold("off")
save("p1_geo_rmse_barh.png")

# ---- 探针 2：轨迹叠加（去 axis("equal")，legend 回坐标区内）----
# 原图 y 轴被拉到 [-13,27]（数据仅到 11.5），因为 axis("equal") 按窄框等比放大
strip_prefix(s) = replace(s, r"^dfbc_" => "", r"^official_" => "", r"^se_3_" => "SE3-")
fig(10, 6.0)
d0 = read_raw(geo[1]["raw_csv"])
plot(thin(d0["x_ref"]), thin(d0["y_ref"]), linestyle="--", linewidth=2.0, color="#222222")
hold("on")
items = ["Reference"]
for r in geo
    d = read_raw(r["raw_csv"])
    plot(thin(d["x"]), thin(d["y"]), linewidth=1.8)
    push!(items, strip_prefix(r["controller_id"]))
end
style_axes()
styled(xlabel("X Position (m)")); styled(ylabel("Y Position (m)"))
grid("on")
lg = legend(items; loc="best")
plt_set(lg, "fontname", FONT); plt_set(lg, "fontsize", 13)
hold("off")
save("p2_geo_traj.png")

# ---- 雷达评分（与 generate_radar_chart.py 口径一致）----
lower_is_better(v, lim) = (isfinite(v) && lim > 0) ? max(0.0, min(1.0, 1.0 - v / lim)) : 0.0
function fmed(vs)
    f = filter(isfinite, vs)
    isempty(f) && return NaN
    return sort(f)[cld(length(f), 2)]
end
const E0 = 838825.6055603315  # official_pid 控制能量基准

function scores5(rs)
    [lower_is_better(fmed([num(r, "position_rmse_m") for r in rs]), 2.0),
     lower_is_better(fmed([num(r, "terminal_position_error_m") for r in rs]), 5.0),
     lower_is_better(fmed([num(r, "control_energy") for r in rs]), E0),
     lower_is_better(fmed([num(r, "max_position_error_m") for r in rs]), 10.0),
     1.0]
end

# ---- 探针 3/4：单族雷达，5 维 vs 4 维（Compute 恒为 1.0，零区分度）----
for (tag, dims, sc) in [("p3_radar_geo_5dim", ["RMSE","Term.Err","Energy","Max.Err","Compute"], scores5(geo)),
                        ("p4_radar_geo_4dim", ["RMSE","Term.Err","Energy","Max.Err"], scores5(geo)[1:4])]
    th = collect(range(0, 2π, length=length(dims)+1))[1:end-1]
    fig(9, 9)
    polarplot([th; th[1]], [sc; sc[1]], "-o", linewidth=2.5)
    style_axes(); rlim([0, 1])
    thetaticks(rad2deg.(th)); thetaticklabels(dims)
    styled(title("Geometric (n = $(length(geo)))"))
    save("$tag.png")
end

# ---- 探针 5：合并雷达（族系缩写 + 4 列 legend，4 维）----
const FAM = [("pid","PID"),("linear","LIN"),("nonlinear","NL"),("sliding","SMC"),
             ("optimal","OPT"),("geometric","GEO"),("baseline","BASE")]
dims4 = ["RMSE","Term.Err","Energy","Max.Err"]
th4 = collect(range(0, 2π, length=5))[1:end-1]
fig(9, 9)
labs = String[]
let started = false
    for (slug, code) in FAM
        rs = [r for r in rows if r["family_slug"] == slug]
        isempty(rs) && continue
        sc = scores5(rs)[1:4]
        polarplot([th4; th4[1]], [sc; sc[1]], "-o", linewidth=2.0)
        if !started
            hold("on"); started = true
        end
        push!(labs, "$code (n=$(length(rs)))")
    end
end
style_axes(); rlim([0, 1])
thetaticks(rad2deg.(th4)); thetaticklabels(dims4)
lg = legend(labs; loc="southoutside", ncol=4)
plt_set(lg, "fontname", FONT); plt_set(lg, "fontsize", 13)
hold("off")
save("p5_radar_combined.png")

# ---- 探针 6：28 条排名图 barh（替代 1800px 画布 + 28 个 x 轴标签）----
allr = sort(rows, by = r -> num(r, "position_rmse_m"))
fig(10, 14)
av = [num(r, "position_rmse_m") for r in allr]
barh(1:length(av), av)
yticks(1:length(av)); yticklabels([r["controller_id"] for r in allr])
style_axes()
styled(xlabel("ClimbPath50s Position RMSE (m)"))
grid("on")
save("p6_ranking_barh.png")

# ---- 探针 7：控制器详图画布对比（回答 204 张要不要一起改）----
# 旧 1200x900 vs 新 900x650，同一份数据同一段代码
op = first(r for r in rows if r["controller_id"] == "official_pid")
dd = read_raw(op["raw_csv"])
for (tag, w, h) in [("p7a_detail_default_5p6in", 6.4, 4.8), ("p7b_detail_new_10in", 10.0, 6.0)]
    fig(w, h)
    plot(thin(dd["time"]), thin(dd["x"] .- dd["x_ref"]), linewidth=1.6)
    hold("on")
    plot(thin(dd["time"]), thin(dd["y"] .- dd["y_ref"]), linewidth=1.6)
    plot(thin(dd["time"]), thin(dd["z"] .- dd["z_ref"]), linewidth=1.6)
    style_axes()
    styled(xlabel("Time (s)")); styled(ylabel("Position Error (m)"))
    grid("on")
    lg = legend(["ex", "ey", "ez"]; loc="best")
    plt_set(lg, "fontname", FONT); plt_set(lg, "fontsize", SZT)
    hold("off")
    save("$tag.png")
end

println("\n探针完成 -> ", OUT)





