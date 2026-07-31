#!/usr/bin/env julia
# 第11章 七场景 / 灵敏度 / 三机编队 / ECBF 安全 —— TyPlot 原生绘图（真 Syslab 产物）
#
# 替代的手写 SVG（均非 Syslab 输出，靠像素算术拼 XML）：
#   Docs/报告/figures/第11章/七场景对比/*.svg    6 张，1080×620 同一模板
#   Docs/报告/figures/第11章/灵敏度分析/*.svg    3 张，同模板
#   生成器 Scripts/syslab/plot_sensitivity_analysis.jl（svg_escape / scaled 像素math）
#   生成器 Scripts/syslab/plot_seven_scenario_comparison.jl（残桩，数据源与输出路径均错）
#
# 产物 15 张 PNG @ resolution=600：
#   七场景对比/  6 张  {scenario}_position_error_comparison
#   灵敏度分析/  3 张  wind_disturbance / parameter_mismatch / motor_efficiency
#   三机编队/    3 张  formation_trajectory_xy / inter_uav_distance / formation_error
#   ECBF安全/    3 张  tracking_error_divergence / ecbf_pair_distance / ecbf_applied_offset
#
# 数据源（不重算已冻结的标量，时序从 raw CSV 现算）：
#   Results/control_platform/seven_scenario_ab_v2/{arm}/{scenario}/raw/result.csv  29 列
#   Results/control_platform/sensitivity_{wind,param,motor}_v1/{arm}/{profile}/metrics/METRICS.json
#   Results/control_platform/px4ctrl_three_uav_figure8_v1/raw/result.csv           28 列
#   Results/planning/three_uav_openblocks_px4ctrl_ecbf_safety_20260731/raw/*full_304p84s.csv  44 列
#
# 相对手写 SVG 修正的一处实质缺陷：
#   motor_efficiency_sensitivity.svg 图例列出 Official PID 蓝色标记却无曲线，
#   且未说明其 4 点为 failed_execution_solver_stall（数值求解器停滞，86% 处卡死）。
#   边界原文：OFFICIAL_PID_MOTOR_SOLVER_STALL_RECLASSIFICATION.json
#     "Execution-level numerical solver stall only; not a terminal-error
#      robustness result or physical controller-failure threshold."
#   本脚本改为在图内显式标注"求解器停滞/不可评估"，不画成控制发散。
#
# motor_efficiency_fault 场景在 §11.1 七场景对比中排除，与手写 SVG 一致：
#   official_pid 无主 raw/result.csv（result_data_status=missing）
#   px4ctrl 仅 1707 行（partial，17.07 s 处终止，终端误差 15.66 m）
#   该场景单独由 §11.2 灵敏度 motor 组承载。

using TyPlot
using JSON
using Printf
using Statistics

include(joinpath(@__DIR__, "typlot_figure_style.jl"))

const BASE_DIR    = raw"C:\Users\HP\Desktop\MoSim"
const SEVEN_ROOT  = joinpath(BASE_DIR, "Results", "control_platform", "seven_scenario_ab_v2")
const SENS_ROOT   = joinpath(BASE_DIR, "Results", "control_platform")
const F8_CSV      = joinpath(BASE_DIR, "Results", "control_platform",
                             "px4ctrl_three_uav_figure8_v1", "raw", "result.csv")
const ECBF_CSV    = joinpath(BASE_DIR, "Results", "planning",
                             "three_uav_openblocks_px4ctrl_ecbf_safety_20260731",
                             "raw", "mworks_px4ctrl_ecbf_safety_full_304p84s.csv")
const OUTPUT_ROOT = joinpath(BASE_DIR, "Docs", "报告", "figures", "第11章")

const RESOLUTION = FIG_RES

# 画布（英寸）—— 导出尺寸只受 figsize 控制，OuterPosition 对 exportgraphics 无效
const CV_TIME = (10.0, 6.0)    # 时序类（位置误差、机间距、队形误差）
const CV_SENS = (9.0, 6.5)     # 灵敏度折线（4 个扫描点，需留图内标注空间）
const CV_XY   = (9.0, 7.5)     # 三机 x-y 轨迹，axis equal
const CV_STACK = (10.0, 8.5)   # 上下两栏共享时间轴（量纲差两个数量级时必须分栏）

# §11.1 六场景。motor_efficiency_fault 见文件头说明，不在此列。
const SCENARIOS = [
    ("hover",              "Hover"),
    ("step_response",      "Step Response"),
    ("spiral",             "Spiral"),
    ("figure8",            "Figure-8"),
    ("wind_disturbance",   "Wind Disturbance"),
    ("parameter_mismatch", "Parameter Mismatch"),
]

const ARMS = [("official_pid", "Official PID"), ("px4ctrl", "px4ctrl")]

# ===== CSV 读取（与 plot_28_passed_detail_typlot.jl 同一实现）=====
function load_csv(path::String)
    isfile(path) || error("CSV not found: $path")
    lines = readlines(path)
    length(lines) >= 2 || error("CSV too short: $path")
    header = [strip(h) for h in split(lines[1], ',')]
    ncol = length(header)
    cols = [Float64[] for _ in 1:ncol]
    for i in 2:length(lines)
        isempty(strip(lines[i])) && continue
        vals = split(lines[i], ',')
        length(vals) == ncol || continue
        for j in 1:ncol
            push!(cols[j], something(tryparse(Float64, strip(vals[j])), NaN))
        end
    end
    return Dict(header[j] => cols[j] for j in 1:ncol)
end

save_fig(dir::String, name::String) = save_fig(joinpath(dir, name))

# 位置误差范数。七场景 raw CSV 无 position_error_norm 列，从 x/y/z 与 ref 现算。
function position_error(d::Dict)
    n = length(d["time"])
    return [sqrt((d["x"][i] - d["x_ref"][i])^2 +
                 (d["y"][i] - d["y_ref"][i])^2 +
                 (d["z"][i] - d["z_ref"][i])^2) for i in 1:n]
end

# ===== §11.1 七场景位置误差对比（6 张）=====
# 两臂同轴对比。RMSE 取自 SCENARIO_RMSE_MATRIX（已冻结），图注标出，
# 不用现算时序再求一遍——避免出现两个略有差异的 RMSE 口径。
function fig_scenario_comparison(scenario::String, label::String,
                                 rmse_by_arm::Dict{String,Float64}, outdir::String)
    fig(CV_TIME...)
    items = String[]
    started = false
    for (arm, arm_label) in ARMS
        path = joinpath(SEVEN_ROOT, arm, scenario, "raw", "result.csv")
        isfile(path) || continue
        d = load_csv(path)
        err = position_error(d)
        plot(thin(d["time"]), thin(err), linewidth=1.8)
        if !started
            hold("on"); started = true
        end
        r = get(rmse_by_arm, arm, NaN)
        push!(items, isnan(r) ? arm_label :
                     @sprintf("%s (RMSE = %.4f m)", arm_label, r))
    end
    styled(xlabel("Time (s)"))
    styled(ylabel("Position Error Norm (m)"))
    grid("on")
    styled_legend(items; loc="best")
    hold("off")
    save_fig(outdir, "$(scenario)_position_error_comparison.png")
end

# ===== §11.2 灵敏度（3 张）=====
# 纵轴 position_rmse_m 取自每次运行的 metrics/METRICS.json。
# 注意：批次矩阵 SENSITIVITY_BATCH_MATRIX.csv 只有 terminal / maximum 两列，无 rmse，
#   手写 SVG 的数据源是单次运行的 METRICS.json（已逐点核对到小数第 4 位）。
const SENS_SPECS = [
    ("wind_disturbance", "sensitivity_wind_v1", "Wind Gust Force X (N)",
     ["sensitivity_wind_x_020N_v1", "sensitivity_wind_x_040N_v1",
      "sensitivity_wind_x_060N_v1", "sensitivity_wind_x_080N_v1"],
     [0.2, 0.4, 0.6, 0.8]),
    ("parameter_mismatch", "sensitivity_param_v1", "Plant Mass Scale (-)",
     ["sensitivity_parameter_scale_110_v1", "sensitivity_parameter_scale_120_v1",
      "sensitivity_parameter_scale_130_v1", "sensitivity_parameter_scale_140_v1"],
     [1.1, 1.2, 1.3, 1.4]),
    ("motor_efficiency", "sensitivity_motor_v1", "Rotor Effectiveness (%)",
     ["sensitivity_motor_efficiency_055_v1", "sensitivity_motor_efficiency_065_v1",
      "sensitivity_motor_efficiency_075_v1", "sensitivity_motor_efficiency_085_v1"],
     [55.0, 65.0, 75.0, 85.0]),
]

function sens_rmse(batch::String, arm::String, profile::String)
    p = joinpath(SENS_ROOT, batch, arm, profile, "metrics", "METRICS.json")
    isfile(p) || return NaN
    m = JSON.parsefile(p)
    v = get(m, "position_rmse_m", nothing)
    return v isa Number ? Float64(v) : NaN
end

function fig_sensitivity(scenario::String, batch::String, xlabel_str::String,
                         profiles::Vector{String}, xvals::Vector{Float64}, outdir::String)
    fig(CV_SENS...)
    items = String[]
    started = false
    # 图例项只能给真画出来的曲线：TyPlot 的 legend 按曲线创建顺序配标签，
    # 为无曲线的臂 push 图例项会让下一条曲线错拿该标签（已实测踩到）。
    # 无数据的臂改用 text() 在轴内标注。
    stalled = String[]
    ymax = 0.0
    for (arm, arm_label) in ARMS
        ys = [sens_rmse(batch, arm, p) for p in profiles]
        valid = .!isnan.(ys)
        if !any(valid)
            push!(stalled, arm_label)
            continue
        end
        if !started; hold("on"); started = true; end
        plot(xvals[valid], ys[valid], "-o", linewidth=2.0, markersize=6)
        push!(items, arm_label)
        ymax = max(ymax, maximum(ys[valid]))
    end
    # 停滞臂改走 NaN 序列：不用浮动小字，但"哪些臂在本图范围内、为何无曲线"必须留档。
    # NaN 序列不画任何可见图元，却真实占一个序列位，所以标签配对不会错位
    # （上面注释里的错位是"只 push 标签、不建序列"造成的，这里不适用）。
    # 边界见 OFFICIAL_PID_MOTOR_SOLVER_STALL_RECLASSIFICATION.json：仅执行层数值
    # 求解器停滞（86% 进度卡死），不是控制发散，不构成鲁棒性阈值结论。
    for arm_label in stalled
        if !started; hold("on"); started = true; end
        plot([xvals[1]], [NaN], "-o", linewidth=2.0, markersize=6)
        push!(items, "$arm_label (no RMSE — failed_execution_solver_stall)")
    end
    styled(xlabel(xlabel_str))
    styled(ylabel("Position RMSE (m)"))
    grid("on")
    isempty(items) || styled_legend(items; loc="best")
    hold("off")
    save_fig(outdir, "$(scenario)_sensitivity.png")
end

# ===== §11.3.1 三机 figure8 编队（3 张）=====
# 数据源：28 列 / 5001 行。formation_error_m 和 min_inter_uav_distance_m 为预存列。
# RUN_RECORD 记录：status=passed，最小机间距 2.078461 m，队形误差 RMSE 2.2855e-13 m。

function fig_formation_xy(d::Dict, outdir::String)
    fig(CV_XY...)
    # 先实际后参考：legend 按曲线创建顺序配标签，这个次序下 6 条曲线的标签
    # 一一对应，三条参考只在最后一条给名，前两条不产生空白图例行。
    plot(thin(d["x"]),      thin(d["y"]),      linewidth=1.8)
    hold("on")
    plot(thin(d["uav2_x"]), thin(d["uav2_y"]), linewidth=1.8)
    plot(thin(d["uav3_x"]), thin(d["uav3_y"]), linewidth=1.8)
    # 参考轨迹（灰色虚线）。三机参考为同一 8 字加固定三角偏移，
    # 故 UAV1/2/3 的参考互不重合，须分别画。
    plot(thin(d["x_ref"]),      thin(d["y_ref"]),      "--", color=[0.6,0.6,0.6], linewidth=1.5)
    plot(thin(d["uav2_x_ref"]), thin(d["uav2_y_ref"]), "--", color=[0.6,0.6,0.6], linewidth=1.5)
    plot(thin(d["uav3_x_ref"]), thin(d["uav3_y_ref"]), "--", color=[0.6,0.6,0.6], linewidth=1.5)
    styled(xlabel("X Position (m)"))
    styled(ylabel("Y Position (m)"))
    grid("on"); axis("equal")
    styled_legend(["UAV 1", "UAV 2", "UAV 3", "Reference (UAV 1-3)"];
                  loc="eastoutside")
    hold("off")
    save_fig(outdir, "formation_trajectory_xy.png")
end

function fig_inter_uav_distance(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time"]; dist = d["min_inter_uav_distance_m"]
    plot(t, dist, linewidth=2.0)
    hold("on")
    # 1.0 m 安全门限线（红色虚线）
    plot([t[1], t[end]], [1.0, 1.0], "--r", linewidth=1.5)
    styled(xlabel("Time (s)"))
    styled(ylabel("Minimum Inter-UAV Distance (m)"))
    grid("on")
    styled_legend(["Min pair distance", "Safety threshold (1.0 m)"]; loc="best")
    hold("off")
    save_fig(outdir, "inter_uav_distance.png")
end

function fig_formation_error(d::Dict, outdir::String)
    fig(CV_TIME...)
    plot(d["time"], d["formation_error_m"], linewidth=2.0)
    styled(xlabel("Time (s)"))
    styled(ylabel("Formation Error (m)"))
    grid("on")
    save_fig(outdir, "formation_error.png")
end

# ===== §11.3.2 ECBF 安全（2 张，负样本）=====
# status=blocked / accepted=False。三条判负门限：
#   safety_intervened=False   硬约束一次未激活（safety_active_pair_count 全程 0）
#   tracking_diagnostic=False uav2 跟踪发散，RMSE 2229.64 m / 终端 14471.30 m
#   clearance_proxy_nonnegative_diagnostic=False  最小 −14470.85 m
# 需要写清的两点区分，否则读者会误读：
#   (1) pair_separation 门限是 True——最小实际机间距 1.5225 m > 1.0 m，机间距从未出问题
#   (2) clearance 的 −14470.85 m 是 uav2 发散的副产品，不是撞障碍
#   (3) 参考调节器并非未动作：202/306 样本施加非零 offset，最大 0.2696 m 已落地 safe_ref；
#       intervention_sample_count=0 统计的是硬约束激活样本，与 offset 是两套口径。

function fig_ecbf_divergence(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time_s"]
    # uav2 达 1.4e4 m，uav1/uav3 在 2.4 m 量级；线性轴下后两者会压成零线，用对数轴。
    # 误差首样本为 0，log 轴需下限截断。
    floorv = 1e-3
    clamp_log(v) = [max(x, floorv) for x in v]
    semilogy(t, clamp_log(d["uav1_tracking_error_m"]), linewidth=1.8)
    hold("on")
    semilogy(t, clamp_log(d["uav2_tracking_error_m"]), linewidth=2.2)
    semilogy(t, clamp_log(d["uav3_tracking_error_m"]), linewidth=1.8)
    styled(xlabel("Time (s)"))
    styled(ylabel("Tracking Error (m, log scale)"))
    grid("on")
    styled_legend(["UAV 1 (RMSE 0.2926 m)",
                   "UAV 2 (RMSE 2229.64 m — diverged)",
                   "UAV 3 (RMSE 0.1988 m)"]; loc="best")
    hold("off")
    save_fig(outdir, "tracking_error_divergence.png")
end

# 已落地修正量 = max_uav max_axis |safe_ref - nominal_ref|。
# 不用 safety_maximum_reference_offset_m 作"已施加"的度量：该列有 202/306 个非零样本，
# 但其中绝大多数是 1e-9 以下的浮点噪声（>1e-9 仅 36 个，>0.01 仅 12 个），
# 直接引用 202 会把噪声说成动作。已落地量非零 56 个样本，最大 0.2676 m，是可辩护的口径。
function applied_offset(d::Dict)
    n = length(d["time_s"])
    out = zeros(n)
    for i in 1:n, u in 1:3, ax in ("x", "y", "z")
        v = abs(d["uav$(u)_safe_ref_$(ax)_m"][i] - d["uav$(u)_nominal_ref_$(ax)_m"][i])
        v > out[i] && (out[i] = v)
    end
    return out
end

# 原 ecbf_intervention_evidence 是 2x1 分栏图，按评审要求拆成两张独立图。
# 拆分本身也更正确：上下两栏量纲差两个数量级（1.5 m 对 0.27 m / 0 计数），
# 同图叠放只能靠分栏，分栏又让每栏高度腰斩。

# (a) 机间距 vs 门限
function fig_ecbf_pair_distance(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time_s"]
    plot(t, d["minimum_pair_distance_m"], linewidth=2.0)
    hold("on")
    plot([t[1], t[end]], [1.0, 1.0], "--r", linewidth=1.5)
    styled(xlabel("Time (s)"))
    styled(ylabel("Pair Distance (m)"))
    grid("on")
    styled_legend(["Min pair distance (min 1.5225 m)", "Pair threshold (1.0 m)"]; loc="best")
    axes_font()
    hold("off")
    save_fig(outdir, "ecbf_pair_distance.png")
end

# (b) 已落地参考修正量 vs 硬约束激活计数
function fig_ecbf_applied_offset(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time_s"]
    off = applied_offset(d)
    nz = count(>(0.0), off)
    plot(t, off, linewidth=1.8)
    hold("on")
    plot(t, d["safety_active_pair_count"], linewidth=2.0)
    styled(xlabel("Time (s)"))
    styled(ylabel("Applied Offset (m) / Count (-)"))
    grid("on")
    # 两行长图例占顶部约 25% 高度，0.2676 m 的峰会被压住，留出图例带
    ylim([-0.012, 0.365])
    styled_legend([@sprintf("Applied reference offset (%d/%d samples, max %.4f m)",
                            nz, length(t), maximum(off)),
                   "Active pair count (0 throughout — hard constraint never engaged)"];
                  loc="best")
    axes_font()
    hold("off")
    save_fig(outdir, "ecbf_applied_offset.png")
end

# ===== 主流程 =====
const RESULTS = Tuple{String,Bool,String}[]

function attempt(name::String, f::Function)
    try
        f()
        push!(RESULTS, (name, true, ""))
        println("  OK   $name")
    catch e
        msg = sprint(showerror, e)
        push!(RESULTS, (name, false, msg))
        println("  FAIL $name : $(first(msg, 200))")
    end
end

println("TyPlot 第11章：七场景 6 + 灵敏度 3 + 三机编队 3 + ECBF 3 = 15 张 PNG @ resolution=$RESOLUTION")

# 七场景 RMSE 从冻结矩阵读，避免与现算时序产生第二个口径
const MATRIX_PATH = joinpath(SEVEN_ROOT, "SCENARIO_RMSE_MATRIX.pending_syslab.json")
rmse_lookup = Dict{String,Dict{String,Float64}}()
if isfile(MATRIX_PATH)
    mx = JSON.parsefile(MATRIX_PATH)
    for row in mx["rows"]
        sc = row["scenario_id"]; arm = row["controller_id"]
        v = get(row, "position_rmse_m", nothing)
        haskey(rmse_lookup, sc) || (rmse_lookup[sc] = Dict{String,Float64}())
        rmse_lookup[sc][arm] = v isa Number ? Float64(v) : NaN
    end
end

dir_seven = joinpath(OUTPUT_ROOT, "七场景对比")
println("[§11.1 七场景] 6 张 -> 第11章/七场景对比/")
for (sc, label) in SCENARIOS
    attempt("$(sc)_position_error_comparison",
            () -> fig_scenario_comparison(sc, label,
                    get(rmse_lookup, sc, Dict{String,Float64}()), dir_seven))
end

dir_sens = joinpath(OUTPUT_ROOT, "灵敏度分析")
println("[§11.2 灵敏度] 3 张 -> 第11章/灵敏度分析/")
for (sc, batch, xlab, profiles, xvals) in SENS_SPECS
    attempt("$(sc)_sensitivity",
            () -> fig_sensitivity(sc, batch, xlab, profiles, xvals, dir_sens))
end

dir_f8 = joinpath(OUTPUT_ROOT, "三机编队")
println("[§11.3.1 三机编队] 3 张 -> 第11章/三机编队/")
if isfile(F8_CSV)
    d8 = load_csv(F8_CSV)
    attempt("formation_trajectory_xy", () -> fig_formation_xy(d8, dir_f8))
    attempt("inter_uav_distance",      () -> fig_inter_uav_distance(d8, dir_f8))
    attempt("formation_error",         () -> fig_formation_error(d8, dir_f8))
else
    println("  SKIP figure8 CSV 不存在：$F8_CSV")
end

dir_ecbf = joinpath(OUTPUT_ROOT, "ECBF安全")
println("[§11.3.2 ECBF 安全] 3 张 -> 第11章/ECBF安全/")
if isfile(ECBF_CSV)
    de = load_csv(ECBF_CSV)
    attempt("tracking_error_divergence", () -> fig_ecbf_divergence(de, dir_ecbf))
    attempt("ecbf_pair_distance",        () -> fig_ecbf_pair_distance(de, dir_ecbf))
    attempt("ecbf_applied_offset",       () -> fig_ecbf_applied_offset(de, dir_ecbf))
else
    println("  SKIP ECBF CSV 不存在：$ECBF_CSV")
end

# ===== manifest =====
total_ok = count(r -> r[2], RESULTS)
manifest = Dict(
    "schema" => "mosim.chapter11.typlot_manifest.v1",
    "generator" => "Scripts/syslab/plot_chapter11_typlot.jl",
    "renderer" => "TyPlot (Syslab native)",
    "resolution" => RESOLUTION,
    "figure_count_expected" => 15,
    "figure_count_generated" => total_ok,
    "output_root" => OUTPUT_ROOT,
    "replaces_handwritten_svg" => [
        "Docs/报告/figures/第11章/七场景对比/*.svg  6 张 1080×620 手写 XML",
        "Docs/报告/figures/第11章/灵敏度分析/*.svg  3 张 同模板",
        "生成器 Scripts/syslab/plot_sensitivity_analysis.jl（svg_escape/scaled 像素算术）",
        "生成器 Scripts/syslab/plot_seven_scenario_comparison.jl（残桩，数据源与输出路径均错）"],
    "results" => [Dict("figure" => r[1], "ok" => r[2], "error" => r[3]) for r in RESULTS],
    "scope_notes" => Dict(
        "motor_efficiency_fault_excluded_from_11_1" =>
            "official_pid 无主 raw/result.csv（result_data_status=missing）；" *
            "px4ctrl 仅 1707 行（partial，17.07 s 终止，终端误差 15.66 m）。" *
            "该场景由 §11.2 灵敏度 motor 组承载，与手写 SVG 的排除口径一致。",
        "official_pid_motor_solver_stall" =>
            "sensitivity_motor_v1 的 official_pid 4 点均为 failed_execution_solver_stall，" *
            "86% 进度处卡死，无 METRICS.json。边界：仅执行层数值求解器停滞，" *
            "不构成终端误差鲁棒性结论或物理控制失败阈值。" *
            "手写 SVG 图例列出该臂却无曲线也无说明，本脚本改为图内显式标注。",
        "sensitivity_rmse_source" =>
            "position_rmse_m 取自各次运行 metrics/METRICS.json；" *
            "SENSITIVITY_BATCH_MATRIX.csv 只有 terminal/maximum 两列，无 rmse。",
        "ecbf_intervention_two_definitions" =>
            "intervention_sample_count=0 与 maximum_active_pair_count=0 统计的是硬约束激活样本" *
            "（safety_active_pair_count 列全程 0），故 gates/safety_intervened 判负；" *
            "但参考调节器确实动作：已落地修正量 |safe_ref−nominal_ref| 在 56/306 样本非零，" *
            "最大 0.2676 m。两者非同一口径，图分上下栏区分。",
        "ecbf_offset_column_not_used_as_applied" =>
            "safety_maximum_reference_offset_m 有 202/306 非零样本，但 >1e-9 仅 36 个、" *
            ">0.01 仅 12 个，余为浮点噪声；引用 202 会把噪声说成动作。" *
            "图上\"已施加\"一律用 |safe_ref−nominal_ref| 逐点算出的 56 样本口径。",
        "ecbf_clearance_negative_cause" =>
            "clearance_lower_bound 最小 −14470.85 m 是 uav2 跟踪发散的副产品，不是撞障碍；" *
            "pair_separation 门限为 True，最小实际机间距 1.5225 m > 1.0 m 门限。"),
)

open(joinpath(OUTPUT_ROOT, "TYPLOT_CHAPTER11_MANIFEST.json"), "w") do io
    JSON.print(io, manifest, 2)
end

println("完成：$total_ok / 15 张")
for (name, ok, msg) in RESULTS
    ok || println("  未生成 $name : $(first(msg, 300))")
end
