#!/usr/bin/env julia
# 28 条性能达标控制器详图 —— TyPlot 原生绘图（Syslab 产物）
#
# 口径：28 = performance_accepted（终端位置误差 < 5 m）= effective_passed_count。
#   口径权威：Config/control_platform/climbpath_baseline_count_definition.json
#
# 负样本模式（DETAIL_NEGATIVE_SAMPLE_IDS）：
#   正文 10.6 以 awff 作为"跑通但未达标"的负性能样本列出，需要同规格 TyPlot 详图。
#   Docs/报告/图/归档/awff负性能样本_20260731/ 下的 4 张是 Python 产物
#   （mosim.plot_results.v1），按图件口径不能作为 Syslab 绘图证据，故用本脚本重出。
#   该模式清单唯一来自 G3 的 status=="fail"，与达标集合互斥；manifest 打
#   negative_sample=true 并保留真实 status，避免被误读为达标控制器。
#
# 与 plot_28_passed_controllers_detail.jl 的区别：
#   那个脚本手写 SVG XML，不是 Syslab 输出；本脚本用 TyPlot，产物为真 Syslab 图。
#
# 7 张/控制器 × 28 = 196 张 PNG @ resolution=600
#   trajectory_xy   x-y 平面轨迹 + 参考
#   trajectory_3d   x-y-z 立体轨迹 + 参考（plot3）
#   altitude_z      高度跟踪
#   position_error  位置误差范数
#   velocity        速度三分量
#   attitude        姿态三角
#   control_input   四路控制量
#
# 采样率说明（图注标注，尊重控制器原生特征）：
#   25 条 dt=0.002 s（25001 点）；dfbc_high_order / lqr_baseline / px4ctrl
#   dt=0.01 s（5001 点）。三者仿真时长同为 50 s，差异为控制器原生输出特征，
#   原因未在运行配置中记录。

using TyPlot
using JSON
using Printf

include(joinpath(@__DIR__, "typlot_figure_style.jl"))

const BASE_DIR    = raw"C:\Users\HP\Desktop\MoSim"
const CSV_ROOT    = joinpath(BASE_DIR, "Results", "control_platform", "phase2_full_48_climbpath")
const OUTPUT_ROOT = joinpath(BASE_DIR, "Docs", "报告", "figures", "第10章")
const G3_PATH     = joinpath(CSV_ROOT, "g3_repair", "G3_STATUS.json")

const RESOLUTION = FIG_RES

# 画布尺寸（英寸）—— exportgraphics 只认 figsize，OuterPosition 对导出完全无效
const CV_XY   = (9.0, 7.5)    # x-y 平面轨迹，需 axis equal
const CV_3D   = (9.0, 7.5)    # 立体轨迹（已过审：p1_traj3d_9x7p5）
const CV_TIME = (10.0, 6.0)   # 时序类

# dt=0.01 s 的三条（其余 25 条为 dt=0.002 s）
const COARSE_DT = ["dfbc_high_order", "lqr_baseline", "px4ctrl"]

# ===== 数据加载 =====
function load_csv(controller_id::String)
    path = joinpath(CSV_ROOT, controller_id, "raw", "climbpath50s.csv")
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

# ===== 样式 =====
# 字体/字号/画布/导出统一由 typlot_figure_style.jl 提供：
#   fig(w,h) 设画布并记录宽度；styled() 标签；axes_font() 刻度；
#   styled_legend() 图例；save_fig(path) 导出。字号按画布宽度等比缩放。
save_fig(dir::String, name::String) = save_fig(joinpath(dir, name))

# ===== 7 张图 =====

function fig_trajectory_xy(d, outdir)
    fig(CV_XY...)
    plot(d["x"], d["y"], linewidth=2.0)
    hold("on")
    plot(d["x_ref"], d["y_ref"], linestyle="--", linewidth=1.5)
    axes_font()
    styled(xlabel("X (m)")); styled(ylabel("Y (m)"))
    grid("on"); axis("equal")
    styled_legend(["Actual", "Reference"])
    hold("off")
    save_fig(outdir, "trajectory_xy.png")
end

function fig_trajectory_3d(d, outdir)
    fig(CV_3D...)
    plot3(d["x"], d["y"], d["z"], linewidth=2.0)
    hold("on")
    plot3(d["x_ref"], d["y_ref"], d["z_ref"], linestyle="--", linewidth=1.5)
    axes_font()
    styled(xlabel("X (m)")); styled(ylabel("Y (m)")); styled(zlabel("Z (m)"))
    grid("on")
    styled_legend(["Actual", "Reference"])
    hold("off")
    save_fig(outdir, "trajectory_3d.png")
end

function fig_altitude_z(d, outdir)
    fig(CV_TIME...)
    plot(d["time"], d["z"], linewidth=2.0)
    hold("on")
    plot(d["time"], d["z_ref"], linestyle="--", linewidth=1.5)
    axes_font()
    styled(xlabel("Time (s)")); styled(ylabel("Altitude Z (m)"))
    grid("on")
    styled_legend(["Actual", "Reference"])
    hold("off")
    save_fig(outdir, "altitude_z.png")
end

function fig_position_error(d, outdir)
    fig(CV_TIME...)
    plot(d["time"], d["position_error_norm"], linewidth=2.0)
    axes_font()
    styled(xlabel("Time (s)")); styled(ylabel("Position Error Norm (m)"))
    grid("on")
    save_fig(outdir, "position_error.png")
end

function fig_velocity(d, outdir)
    fig(CV_TIME...)
    plot(d["time"], d["vx"], linewidth=1.8)
    hold("on")
    plot(d["time"], d["vy"], linewidth=1.8)
    plot(d["time"], d["vz"], linewidth=1.8)
    axes_font()
    styled(xlabel("Time (s)")); styled(ylabel("Velocity (m/s)"))
    grid("on")
    styled_legend(["Vx", "Vy", "Vz"])
    hold("off")
    save_fig(outdir, "velocity.png")
end

function fig_attitude(d, outdir)
    fig(CV_TIME...)
    plot(d["time"], d["roll"], linewidth=1.8)
    hold("on")
    plot(d["time"], d["pitch"], linewidth=1.8)
    plot(d["time"], d["yaw"], linewidth=1.8)
    axes_font()
    styled(xlabel("Time (s)")); styled(ylabel("Attitude (rad)"))
    grid("on")
    styled_legend(["Roll", "Pitch", "Yaw"])
    hold("off")
    save_fig(outdir, "attitude.png")
end

function fig_control_input(d, outdir)
    fig(CV_TIME...)
    plot(d["time"], d["u1"], linewidth=1.6)
    hold("on")
    plot(d["time"], d["u2"], linewidth=1.6)
    plot(d["time"], d["u3"], linewidth=1.6)
    plot(d["time"], d["u4"], linewidth=1.6)
    axes_font()
    styled(xlabel("Time (s)")); styled(ylabel("Control Input"))
    grid("on")
    styled_legend(["u1", "u2", "u3", "u4"])
    hold("off")
    save_fig(outdir, "control_input.png")
end

const FIGURES = [
    ("trajectory_xy",   fig_trajectory_xy,   ["x","y","x_ref","y_ref"]),
    ("trajectory_3d",   fig_trajectory_3d,   ["x","y","z","x_ref","y_ref","z_ref"]),
    ("altitude_z",      fig_altitude_z,      ["time","z","z_ref"]),
    ("position_error",  fig_position_error,  ["time","position_error_norm"]),
    ("velocity",        fig_velocity,        ["time","vx","vy","vz"]),
    ("attitude",        fig_attitude,        ["time","roll","pitch","yaw"]),
    ("control_input",   fig_control_input,   ["time","u1","u2","u3","u4"]),
]

# ===== 主循环 =====
g3 = JSON.parsefile(G3_PATH)
g3_by_id = Dict(r["controller_id"] => r for r in g3["rows"])
passed = sort([r["controller_id"] for r in g3["rows"] if r["status"] == "pass"])
# 清单唯一来自 G3 的 status=="pass"，不手写控制器列表，避免两处清单漂移
@assert length(passed) == 28 "达标数应为 28，实际 $(length(passed))；检查 G3_STATUS.json"
@assert !("awff" in passed) "awff 为跑通未达标，不应出现在达标集合；其详图走负样本模式"

failed_ids = sort([r["controller_id"] for r in g3["rows"] if r["status"] == "fail"])

# 负样本模式：设 DETAIL_NEGATIVE_SAMPLE_IDS 只出指定的未达标控制器（如 awff）。
# 与达标集合互斥，清单唯一来自 G3 status=="fail"，不手写。
const NEGATIVE_MODE = isdefined(Main, :DETAIL_NEGATIVE_SAMPLE_IDS) &&
                      !isempty(Main.DETAIL_NEGATIVE_SAMPLE_IDS)

targets = passed
if NEGATIVE_MODE
    req = collect(Main.DETAIL_NEGATIVE_SAMPLE_IDS)
    unknown = setdiff(req, failed_ids)
    isempty(unknown) || error("负样本 ID 不在 G3 未达标集合：" * join(unknown, ", "))
    targets = sort(req)
    println("【负样本模式】仅生成 " * join(targets, ", ") * "（status=fail，不计入达标数）")
elseif isdefined(Main, :DETAIL_SAMPLE_IDS) && !isempty(Main.DETAIL_SAMPLE_IDS)
    # 抽样模式：只出指定达标控制器，供人工审核；未设则全量 28 条。
    unknown = setdiff(Main.DETAIL_SAMPLE_IDS, passed)
    isempty(unknown) || error("抽样 ID 不在达标集合：" * join(unknown, ", "))
    targets = sort(collect(Main.DETAIL_SAMPLE_IDS))
    println("【抽样模式】仅生成 " * join(targets, ", "))
end

println("开始为 $(length(targets)) 条控制器生成 $(length(FIGURES)) 张/条，共 $(length(targets)*length(FIGURES)) 张 PNG @ resolution=$RESOLUTION")

total_ok = 0
total_fail = 0
failures = String[]

# 输出根目录可覆盖：抽样审核时写临时目录，避免未过审就覆盖已交付图
const OUT_ROOT_EFF = isdefined(Main, :DETAIL_OUTPUT_ROOT) ? Main.DETAIL_OUTPUT_ROOT : OUTPUT_ROOT

for (idx, cid) in enumerate(targets)
    outdir = joinpath(OUT_ROOT_EFF, cid)
    d = load_csv(cid)
    npts = length(d["time"])
    dt = npts >= 2 ? d["time"][2] - d["time"][1] : NaN
    row = g3_by_id[cid]

    @printf("[%2d/%2d] %-42s rows=%-6d dt=%.4f status=%s\n",
            idx, length(targets), cid, npts, dt, row["status"])

    written = String[]
    for (name, fn, _) in FIGURES
        try
            fn(d, outdir)
            push!(written, name * ".png")
            global total_ok += 1
        catch e
            global total_fail += 1
            push!(failures, "$cid/$name: $(sprint(showerror, e))")
            @warn "FAILED $cid/$name" exception=e
        end
    end

    manifest = Dict(
        "schema"      => "mosim.typlot_detail.v1",
        "controller_id" => cid,
        "generator"   => "Scripts/syslab/plot_28_passed_detail_typlot.jl",
        "engine"      => "Syslab TyPlot",
        "resolution"  => RESOLUTION,
        "raw_csv"     => relpath(joinpath(CSV_ROOT, cid, "raw", "climbpath50s.csv"), BASE_DIR),
        "sample_count"    => npts,
        "sample_interval_s" => dt,
        "duration_s"  => d["time"][end],
        "sampling_note" => cid in COARSE_DT ?
            "本控制器采样间隔 0.01 s（$(npts) 点），区别于其余 25 条的 0.002 s（25001 点）。" *
            "该差异为控制器原生输出特征，原因未在运行配置中记录；仿真时长同为 50 s。" :
            "采样间隔 0.002 s（25001 点），与本批 25 条一致。",
        "key_metrics" => Dict(
            "position_rmse_m" => row["position_rmse_m"],
            "terminal_position_error_norm_m" => row["terminal_position_error_norm_m"],
        ),
        "g3_status"   => row["status"],
        "negative_sample" => row["status"] != "pass",
        "figures"     => written,
        "count_definition_authority" => "Config/control_platform/climbpath_baseline_count_definition.json",
    )
    if row["status"] != "pass"
        manifest["failure_class"] = get(row, "failure_class", nothing)
        manifest["negative_sample_note"] =
            "本控制器 G3 状态为 $(row["status"])（$(get(row, "failure_class", "未记录"))），" *
            "计入 ran_to_completion=38，不计入 performance_accepted=28。" *
            "图件仅作负性能样本证据，不得作为达标结论引用。"
    end
    open(joinpath(outdir, "figure_manifest.typlot.json"), "w") do io
        JSON.print(io, manifest, 2)
    end
end

println("\n=== 完成 ===")
println("成功 $total_ok 张，失败 $total_fail 张")
if !isempty(failures)
    println("失败明细：")
    for f in failures; println("  - $f"); end
end
println("采样率异于主流的 3 条已在各自 manifest 的 sampling_note 中标注：", join(COARSE_DT, ", "))
