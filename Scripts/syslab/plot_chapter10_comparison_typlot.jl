#!/usr/bin/env julia
# 第10章 族系对比 / 雷达 / 状态矩阵 / RMSE 热图 —— TyPlot 原生绘图（真 Syslab 产物）
#
# 替代的手写 SVG 生成器（均非 Syslab 输出）：
#   Scripts/syslab/compare_controllers.jl      Julia 手写 SVG 字符串
#   Scripts/syslab/generate_radar_chart.py     Python 手写 SVG
#   Scripts/syslab/generate_status_matrix.py   Python 手写 SVG
#   Scripts/syslab/generate_heatmap.py         Python 手写 SVG
#
# 产物 33 张 PNG @ resolution=600：
#   6 族系目录 × 4 张 = 24    climbpath_rmse_bar / terminal_error_bar
#                            control_energy_bar / climbpath_trajectory_overlay
#   controller_radar/  8 张   radar_01_pid … radar_08_baseline
#   第10章根目录       1 张   controller_radar_chart
#   rmse_heatmap 已于 2026-07-31 废弃（与 controller_ranking_rmse 重复）
#   controller_status_matrix 已于 2026-07-31 废弃（48 条堆单列，无分析价值，转文字说明）
#
# 数据源（不重算，直接取当前记录中的已有值）：
#   .tmp/chapter10_typlot/accepted_controller_index.csv  当前 30 条达标控制器
#   .tmp/chapter10_typlot/g3_status_index.csv            当前目录全 48 条状态
#   由 Scripts/syslab/build_chapter10_typlot_index.py 生成，指标全部来自
#   各 source_record 绑定的 metrics.csv/metrics.json 与 raw CSV。
#
# 口径：30 = current catalog performance_accepted（终端位置误差 < 5 m）；
#   48 = current catalog entries。历史 28 条 G3 快照只作追溯，不进入本图集。
#   权威：Results/control_platform/phase2_full_48_climbpath/g3_repair/
#   G3_CATALOG_48_CURRENT_STATUS.json
#
# 与原 SVG 的唯一内容差异：controller_status_matrix 原为历史全 accepted 的文本表格
#   （status 列恒等，作图无信息量）；当前图集保留 48 条状态索引供审计，
#   但不再生成该重复图。

using TyPlot
using JSON
using Printf
using Statistics

include(joinpath(@__DIR__, "typlot_figure_style.jl"))

const BASE_DIR    = raw"C:\Users\HP\Desktop\MoSim"
const INDEX_DIR   = joinpath(BASE_DIR, ".tmp", "chapter10_typlot")
const OUTPUT_ROOT = isdefined(Main, :CMP_OUTPUT_ROOT) ? Main.CMP_OUTPUT_ROOT :
                    joinpath(BASE_DIR, "Docs", "报告", "figures", "第10章")

const RESOLUTION = FIG_RES

# 画布（英寸）—— 导出尺寸只受 figsize 控制
const CV_FBAR    = (10.0, 7.0)    # 族系指标横条（≤7 条控制器）
const CV_OVERLAY = (10.0, 7.5)    # 轨迹叠加 + 轴外图例
const CV_RADAR   = (9.0, 9.0)     # 雷达（已过审）

# 族系顺序与 generate_status_matrix.py 的 FAMILY_ORDER 一致。
# 图上一律用英文族名：Times New Roman 无中文字形，中文会渲染成豆腐块；
# 英文标签与 plot_controller_taxonomy.jl 的 family_labels 保持同一套。
const FAMILIES = [
    ("pid",       "PID",                 "PID族",          "pid_family_comparison",       "radar_01_pid"),
    ("linear",    "Linear Robust",       "线性/鲁棒族",     "linear_family_comparison",    "radar_02_linear"),
    ("nonlinear", "Nonlinear Adaptive",  "非线性/自适应族", "nonlinear_family_comparison", "radar_03_nonlinear"),
    ("sliding",   "Sliding Mode",        "滑模族",         "smc_family_comparison",       "radar_04_sliding"),
    ("optimal",   "Optimization",        "优化/预测族",     "mpc_family_comparison",       "radar_05_optimal"),
    ("geometric", "Geometric",           "几何/微分平坦族", "geometric_family_comparison", "radar_06_geometric"),
    ("learning",  "Learning",            "学习增强族",      "",                            "radar_07_learning"),
    ("baseline",  "Engineering Baseline","工程基线",        "",                            "radar_08_baseline"),
]

# 雷达五维与 generate_radar_chart.py 的 DIMENSIONS 一致（越小越好，除算力效率）
# 雷达四维。相对原 generate_radar_chart.py 的两处口径变更（记入 manifest）：
#   1. 删掉 Compute Efficiency —— 无实测数据、恒取 1.0，八族全同，不构成区分度。
#   2. 归一化从"固定阈值"改为"当前 30 条达标控制器族系中位数的 min-max"。
#      固定阈值下 Control Energy 是死轴：基准取 official_pid 自身能量，
#      七族得分极差仅 0.006，肉眼无法分辨；min-max 后极差 0.362。
const RADAR_DIMS  = ["Position RMSE", "Terminal Error", "Control Energy", "Max Error"]
const RADAR_KEYS  = ["position_rmse_m", "terminal_position_error_m",
                     "control_energy", "max_position_error_m"]
# 旧固定阈值口径，仅留档于 manifest，不再参与作图
const RADAR_LIMIT_LEGACY = Dict("position_rmse_m" => 2.0, "terminal_position_error_m" => 5.0,
                                "max_position_error_m" => 10.0)

# ===== CSV 读取 =====
function read_index(path::String)
    isfile(path) || error("索引不存在，请先运行 build_chapter10_typlot_index.py: $path")
    lines = readlines(path)
    header = [strip(h) for h in split(lines[1], ',')]
    rows = Dict{String,String}[]
    for i in 2:length(lines)
        isempty(strip(lines[i])) && continue
        vals = split(lines[i], ',')
        length(vals) == length(header) || continue
        push!(rows, Dict(header[j] => strip(String(vals[j])) for j in 1:length(header)))
    end
    return rows
end

num(row, key) = (v = get(row, key, ""); isempty(v) ? NaN : something(tryparse(Float64, v), NaN))

function read_raw_csv(path::String)
    isfile(path) || error("原始 CSV 不存在: $path")
    lines = readlines(path)
    header = [strip(h) for h in split(lines[1], ',')]
    cols = [Float64[] for _ in 1:length(header)]
    for i in 2:length(lines)
        isempty(strip(lines[i])) && continue
        vals = split(lines[i], ',')
        length(vals) == length(header) || continue
        for j in 1:length(header)
            push!(cols[j], something(tryparse(Float64, strip(vals[j])), NaN))
        end
    end
    return Dict(header[j] => cols[j] for j in 1:length(header))
end

function raw_series(data, names::Vector{String})
    for name in names
        haskey(data, name) && return data[name]
    end
    error("原始 CSV 缺少列: $(join(names, " / "))")
end

# ===== 样式 =====
# 字体/字号/画布/导出/抽稀统一由 typlot_figure_style.jl 提供。
# ticklab_x / ticklab_y / ticklab_theta 内部封死"先建标签→后设字体"的顺序，
# 否则刻度标签是新建文本对象，不继承 gca() 字体，会回退无衬线。
save_fig(dir::String, name::String) = save_fig(joinpath(dir, name))

# ===== 族系柱状图（3 张）=====
# 竖版 + xtickangle(30) 在长控制器名下会互相压字，统一改横条：
# 名字沿 y 轴自然排开，与已过审的 28 条排名图同一形式。
function fig_metric_bar(rows, metric::String, ylab::String, outdir::String, fname::String)
    valid_rows = [r for r in rows if isfinite(num(r, metric))]
    isempty(valid_rows) && error("族系没有可用的 $metric 指标")
    ids = [r["controller_id"] for r in valid_rows]
    vals = [num(r, metric) for r in valid_rows]
    fig(CV_FBAR...)
    y = 1:length(vals)
    barh(y, vals)
    ticklab_y(y, ids)
    styled(xlabel(ylab))
    styled(ylabel("Controller (available n = $(length(ids)) / $(length(rows)))"))
    grid("on")
    save_fig(outdir, fname)
end

# ===== 族系轨迹叠加图 =====
function fig_trajectory_overlay(rows, outdir::String)
    fig(CV_OVERLAY...)
    first_raw = read_raw_csv(rows[1]["raw_csv"])
    plot(thin(raw_series(first_raw, ["x_ref", "position_ref_x_m"])),
         thin(raw_series(first_raw, ["y_ref", "position_ref_y_m"])),
         linestyle="--", linewidth=2.0, color="#222222")
    hold("on")
    items = ["Reference"]
    for r in rows
        d = read_raw_csv(r["raw_csv"])
        plot(thin(raw_series(d, ["x", "position_x_m"])),
             thin(raw_series(d, ["y", "position_y_m"])), linewidth=1.8)
        push!(items, r["controller_id"])
    end
    axes_font()
    styled(xlabel("X Position (m)")); styled(ylabel("Y Position (m)"))
    grid("on"); axis("equal")
    # axis("equal") 后轨迹常占满画布，legend 放轴外避免压曲线
    styled_legend(items; loc="eastoutside")
    hold("off")
    save_fig(outdir, "climbpath_trajectory_overlay.png")
end

# ===== 雷达图 =====
function finite_median(vals::Vector{Float64})
    f = [v for v in vals if isfinite(v)]
    return isempty(f) ? NaN : median(f)
end

# 族系中位数（四个原始指标，未归一化）
function family_medians(rows)
    isempty(rows) && return Dict{String,Float64}()
    return Dict{String,Float64}(
        k => finite_median([num(r, k) for r in rows]) for k in RADAR_KEYS)
end

# 跨族 min-max：四维各自在"有达标控制器的族系"内取极值，
# 越小越好 → 得分 = (max - v) / (max - min)，最差族得 0、最优族得 1。
# 单族或极差为 0 时退化为 0.5，避免除零并明示"无区分度"。
function build_radar_scaler(medians_by_family)
    rng = Dict{String,Tuple{Float64,Float64}}()
    for k in RADAR_KEYS
        vs = [m[k] for (_, m) in medians_by_family if haskey(m, k) && isfinite(m[k])]
        rng[k] = isempty(vs) ? (NaN, NaN) : (minimum(vs), maximum(vs))
    end
    return rng
end

function radar_scores(med, rng)
    isempty(med) && return Float64[]
    return [begin
        v = get(med, k, NaN); lo, hi = rng[k]
        (!isfinite(v) || !isfinite(lo)) ? 0.0 :
            (hi - lo <= 0 ? 0.5 : max(0.0, min(1.0, (hi - v) / (hi - lo))))
    end for k in RADAR_KEYS]
end

# polarplot 收弧度，thetaticks 收角度（度）——混用会触发 Locator.MAXTICKS。
# 偏移 45°：不偏移时 theta=0° 的长标签会被画布右边缘裁切，且 theta=90° 标签压住标题。
const RADAR_ANGLES = collect(0:2π/length(RADAR_DIMS):2π-0.01) .+ π/4

# r 刻度标签默认画在 90°（正上方），会与标题重叠，挪到 -80°（右下空白区）
function radar_axes()
    rlim([0, 1])
    rtickangle(-80)
    ticklab_theta(rad2deg.(RADAR_ANGLES), RADAR_DIMS)
end

function fig_family_radar(slug::String, label::String, rows, medians_by_family, rng,
                          outdir::String, fname::String)
    fig(CV_RADAR...)
    # 全项目不出标题。但 8 张单族雷达图轮廓形状相近，去掉族名就无法分辨是哪一张，
    # 族名与 n 改由图例承担（雷达图只有一条序列，图例即标识）。
    if isempty(rows)
        # 学习增强族无达标控制器，画空轮廓（与原 SVG 的 "No accepted controller" 一致）
        zero_scores = zeros(length(RADAR_DIMS))
        polarplot([RADAR_ANGLES; RADAR_ANGLES[1]], [zero_scores; zero_scores[1]],
                  "-o", linewidth=2.0)
        radar_axes()
        # southoutside：极坐标区是满幅圆，任何区内位置都会压到外圈线上
        styled_legend(["$label — no accepted controller (n = 0)"]; loc="southoutside")
    else
        scores = radar_scores(medians_by_family[slug], rng)
        polarplot([RADAR_ANGLES; RADAR_ANGLES[1]], [scores; scores[1]], "-o", linewidth=2.5)
        radar_axes()
        styled_legend(["$label (n = $(length(rows)))"]; loc="southoutside")
    end
    save_fig(outdir, fname)
end

function fig_combined_radar(by_family, medians_by_family, rng, outdir::String)
    fig(CV_RADAR...)
    items = String[]
    started = false
    for (slug, label, _, _, _) in FAMILIES
        rows = get(by_family, slug, Dict{String,String}[])
        isempty(rows) && continue
        scores = radar_scores(medians_by_family[slug], rng)
        polarplot([RADAR_ANGLES; RADAR_ANGLES[1]], [scores; scores[1]], "-o", linewidth=2.2)
        if !started
            hold("on")
            started = true
        end
        push!(items, "$label (n=$(length(rows)))")
    end
    radar_axes()
    # 极坐标区四周都是 theta 标签，legend 必须挪到轴外，否则压住维度名
    styled_legend(items; loc="southoutside", ncol=3)
    hold("off")
    save_fig(outdir, "controller_radar_chart.png")
end

# ===== rmse_heatmap 已于 2026-07-31 废弃 =====
# 单列 N×1 热图与 controller_ranking_rmse.png 是同一份 30 条 RMSE 排序数据，
# 后者直读数值、可比长短，前者只能凭颜色估大小。属重复，删除。
# 旧文件 rmse_heatmap.png 需从磁盘与报告引用中移除。

# ===== 状态矩阵已于 2026-07-31 整体废弃 =====
# 两版画法都试过并否决：
#   横条三色堆叠  —— 48 行在 14 in 高度下 y 标签竖向压字；x 轴全为 1.0，零信息量
#   单列热图      —— 只有一列无从横向比较；连续色标为三态离散值造出 1.2 / 1.8 中间刻度
# 三态计数（28 / 10 / 10）改由正文文字叙述，口径唯一来自
# Config/control_platform/climbpath_baseline_count_definition.json 的五级定义。
# 报告需删除对 controller_status_matrix.png 的引用。
#=
function fig_status_matrix(status_rows, outdir::String)
    ids = [r["controller_id"] for r in status_rows]
    codes = [get(STATUS_CODE, r["status_class"], 0.0) for r in status_rows]
    accepted = count(==(2.0), codes)
    blocked = count(==(1.0), codes)
    notrun = count(==(0.0), codes)

    fig(CV_STATUS...)
    y = 1:length(codes)
    # 三个互斥系列：未命中该状态的条目取 0 长度，使每行只有一根有色条
    barh(y, hcat([c == 2.0 ? 1.0 : 0.0 for c in codes],
                 [c == 1.0 ? 1.0 : 0.0 for c in codes],
                 [c == 0.0 ? 1.0 : 0.0 for c in codes]), style="stacked")
    ticklab_y(y, ids)
    styled(xlabel("Execution Status"))
    styled(ylabel("Catalog-Frozen Entry (n = $(length(ids)))"))
    styled_legend(["Accepted ($accepted)", "Executed-Blocked ($blocked)",
                   "Not Run ($notrun)"]; loc="southoutside", ncol=3)
    xlim([0, 1.15])
    grid("on")
    save_fig(outdir, "controller_status_matrix.png")
end

# 对照版：保留原热图画法，仅供你比选，不进交付
function fig_status_heatmap_alt(status_rows, outdir::String)
    ids = [r["controller_id"] for r in status_rows]
    codes = [get(STATUS_CODE, r["status_class"], 0.0) for r in status_rows]
    fig(8.0, 14.0)
    heatmap(reshape(codes, length(codes), 1),
            xvalues=["2 = accepted   1 = executed-blocked   0 = not run"], yvalues=ids)
    axes_font()
    save_fig(outdir, "ALT_status_heatmap.png")
end
=#

# ===== 主流程 =====
accepted_rows = read_index(joinpath(INDEX_DIR, "accepted_controller_index.csv"))
status_rows   = read_index(joinpath(INDEX_DIR, "g3_status_index.csv"))

@assert length(accepted_rows) == 30 "当前达标数应为 30，实际 $(length(accepted_rows))"
@assert length(status_rows) == 48 "G3 冻结条目应为 48，实际 $(length(status_rows))"
@assert !any(r -> r["controller_id"] == "pid_awff_linear_eso", accepted_rows) "负性能 ESO 不应出现在达标集合"

by_family = Dict{String,Vector{Dict{String,String}}}()
for r in accepted_rows
    push!(get!(by_family, r["family_slug"], Dict{String,String}[]), r)
end
for (_, v) in by_family
    sort!(v, by = r -> r["controller_id"])
end

official = findfirst(r -> r["controller_id"] == "official_pid", accepted_rows)
official === nothing && error("索引中缺少 official_pid")
const OFFICIAL_ENERGY = num(accepted_rows[official], "control_energy")

# 雷达归一化基准：先算各族四维中位数，再取跨族 min-max
const MEDIANS = Dict(slug => family_medians(get(by_family, slug, Dict{String,String}[]))
                     for (slug, _, _, _, _) in FAMILIES)
const MED_NONEMPTY = Dict(k => v for (k, v) in MEDIANS if !isempty(v))
const RADAR_RANGE = build_radar_scaler(MED_NONEMPTY)

println("TyPlot 第10章当前对比图：6 族系 × 4 + 雷达 8 + 根目录 1 = 33 张 PNG @ resolution=$RESOLUTION")
println("雷达归一化跨族 min-max 区间：")
for k in RADAR_KEYS
    lo, hi = RADAR_RANGE[k]
    @printf("  %-28s min=%.6g  max=%.6g  极差=%.6g\n", k, lo, hi, hi - lo)
end

total_ok = 0
failures = String[]

function attempt(desc::String, fn)
    try
        fn()
        global total_ok += 1
        println("  [OK] $desc")
    catch e
        push!(failures, "$desc: $(sprint(showerror, e))")
        @warn "FAILED $desc" exception=e
    end
end

# --- 6 族系 × 4 张 ---
for (slug, label, _, dirname, _) in FAMILIES
    isempty(dirname) && continue
    rows = get(by_family, slug, Dict{String,String}[])
    if isempty(rows)
        push!(failures, "$dirname: 该族系无达标控制器，跳过")
        continue
    end
    outdir = joinpath(OUTPUT_ROOT, dirname, "figures")
    println("[$label] $(length(rows)) 条 -> $dirname/figures/")
    attempt("$dirname/climbpath_rmse_bar", () -> fig_metric_bar(
        rows, "position_rmse_m", "ClimbPath Position RMSE (m)", outdir, "climbpath_rmse_bar.png"))
    attempt("$dirname/terminal_error_bar", () -> fig_metric_bar(
        rows, "terminal_position_error_m", "Terminal Position Error (m)", outdir, "terminal_error_bar.png"))
    attempt("$dirname/control_energy_bar", () -> fig_metric_bar(
        rows, "control_energy", "Control Energy", outdir, "control_energy_bar.png"))
    attempt("$dirname/climbpath_trajectory_overlay", () -> fig_trajectory_overlay(rows, outdir))
end

# --- 雷达 8 张 ---
radar_dir = joinpath(OUTPUT_ROOT, "controller_radar")
println("[雷达] 8 张 -> controller_radar/")
for (slug, label, _, _, radar_name) in FAMILIES
    rows = get(by_family, slug, Dict{String,String}[])
    attempt("controller_radar/$radar_name", () -> fig_family_radar(
        slug, label, rows, MEDIANS, RADAR_RANGE, radar_dir, "$radar_name.png"))
end

# --- 根目录 1 张（rmse_heatmap 与 controller_status_matrix 均已废弃）---
println("[根目录] 1 张 -> 第10章/")
attempt("controller_radar_chart", () -> fig_combined_radar(by_family, MEDIANS, RADAR_RANGE, OUTPUT_ROOT))

# --- 族系 manifest（TyPlot 版，与旧 SVG manifest 并存，schema 区分）---
for (slug, label, label_zh, dirname, _) in FAMILIES
    isempty(dirname) && continue
    rows = get(by_family, slug, Dict{String,String}[])
    isempty(rows) && continue
    agg = MEDIANS[slug]
    scores = radar_scores(agg, RADAR_RANGE)
    manifest = Dict(
        "schema"     => "mosim.typlot_controller_comparison.v1",
        "engine"     => "Syslab TyPlot",
        "generator"  => "Scripts/syslab/plot_chapter10_comparison_typlot.jl",
        "resolution" => RESOLUTION,
        "family"      => label_zh,
        "family_label_en" => label,
        "family_slug" => slug,
        "controller_count" => length(rows),
        "controllers" => [r["controller_id"] for r in rows],
        "figures" => ["figures/climbpath_rmse_bar.png", "figures/terminal_error_bar.png",
                      "figures/control_energy_bar.png", "figures/climbpath_trajectory_overlay.png"],
        "metric_source" => "当前目录各 source_record 绑定的 metrics.csv/metrics.json（已有值，未重算）",
        "index_source"  => ".tmp/chapter10_typlot/accepted_controller_index.csv（当前 catalog 30 条 pass）",
        "family_median" => agg,
        "radar_scores"  => Dict(RADAR_DIMS[i] => scores[i] for i in 1:length(RADAR_DIMS)),
        "count_definition_authority" => "Config/control_platform/climbpath_baseline_count_definition.json",
    )
    open(joinpath(OUTPUT_ROOT, dirname, "COMPARE_CONTROLLERS_MANIFEST.typlot.json"), "w") do io
        JSON.print(io, manifest, 2)
    end
end

# --- 总 manifest ---
summary = Dict(
    "schema"     => "mosim.typlot_chapter10_comparison.v1",
    "engine"     => "Syslab TyPlot",
    "generator"  => "Scripts/syslab/plot_chapter10_comparison_typlot.jl",
    "resolution" => RESOLUTION,
    "figure_count_expected" => 33,
    "figure_count_written"  => total_ok,
    "failures"   => failures,
    "accepted_controller_count" => length(accepted_rows),
    "current_catalog_entry_count" => length(status_rows),
    "metric_source" => "当前目录各 source_record 绑定的 metrics.csv/metrics.json（已有值，未重算）",
    "index_source"  => ".tmp/chapter10_typlot/accepted_controller_index.csv（当前 catalog 30 条 pass）",
    "family_breakdown" => Dict(slug => length(get(by_family, slug, Dict{String,String}[]))
                               for (slug, _, _, _, _) in FAMILIES),
    "replaces_handwritten_svg" => [
        "Scripts/syslab/compare_controllers.jl",
        "Scripts/syslab/generate_radar_chart.py",
        "Scripts/syslab/generate_status_matrix.py",
        "Scripts/syslab/generate_heatmap.py",
    ],
    "status_matrix_scope_note" =>
        "原 controller_status_matrix.svg 为历史全 accepted 的文本表格（status 列恒等，" *
        "作图无信息量）；当前图集保留 48 条状态索引供审计，但不再生成该重复图。",
    "radar_dimension_change_20260731" => Dict(
        "removed_dimension" => "Compute Efficiency",
        "reason" => "无实测数据，原口径恒取 1.0，八族全同，不构成区分度；五维降为四维。",
        "dims_now" => RADAR_DIMS),
    "radar_normalization_change_20260731" => Dict(
        "from" => "固定阈值 1 - v/limit（RMSE≤2, Terminal≤5, Max≤10, Energy 基准=official_pid 自身能量）",
        "to"   => "跨族 min-max：得分 =(max-v)/(max-min)，越小越好，最差族 0 / 最优族 1",
        "reason" => "固定阈值下 Control Energy 是死轴 —— 基准取 official_pid 自身能量时" *
                    "七族得分极差仅 0.006，肉眼不可分；min-max 后极差 0.362。",
        "legacy_limits" => RADAR_LIMIT_LEGACY,
        "minmax_range" => Dict(k => Dict("min" => RADAR_RANGE[k][1], "max" => RADAR_RANGE[k][2])
                               for k in RADAR_KEYS),
        "degenerate_rule" => "单族或极差为 0 时该维退化为 0.5，明示无区分度而非误报满分"),
    "rmse_heatmap_removed_20260731" =>
        "单列 N×1 热图与 controller_ranking_rmse.png 同为 30 条 RMSE 排序，" *
        "后者可直读数值、比长短，前者仅凭颜色估大小；属重复，删除。",
    "status_matrix_removed_20260731" => Dict(
        "rejected_encodings" => [
            "2/1/0 单列热图：连续色标为三态离散值造出 1.2/1.8 中间刻度，且单列无从横向比较",
            "三色互斥堆叠横条：48 行在 14 in 高度下 y 标签竖向压字，x 轴全为 1.0 零信息量"],
                        "resolution" => "整体删除，三态计数由当前 48 条对账正文文字叙述；" *
                        "报告需同步删除对 controller_status_matrix.png 的引用"),
    "control_energy_baseline_legacy" => Dict("controller_id" => "official_pid", "value" => OFFICIAL_ENERGY),
    "count_definition_authority" => "Config/control_platform/climbpath_baseline_count_definition.json",
)
open(joinpath(OUTPUT_ROOT, "TYPLOT_COMPARISON_MANIFEST.json"), "w") do io
    JSON.print(io, summary, 2)
end

println()
println("完成：$total_ok / 33 张")
if !isempty(failures)
    println("失败 $(length(failures)) 项：")
    for f in failures
        println("  - $f")
    end
end
