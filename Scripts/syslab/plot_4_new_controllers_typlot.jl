#!/usr/bin/env julia
# 4 条新控制器详图 —— TyPlot（Syslab 产物）
# 2 passed: fixed_awff_l1_indi, fixed_linear_mpc_l1_indi
# 2 failed: fixed_awff_l1_residual, fixed_qp_nmpc_l1_indi_cbf
#
# 新 CSV 只有 14 列（无 vx/vy/vz/position_error_norm），
# 通过数值微分和欧氏距离补算。

using TyPlot
using Printf

include(joinpath(@__DIR__, "typlot_figure_style.jl"))

const BASE_DIR    = raw"C:\Users\HP\Desktop\MoSim"
const CSV_ROOT    = joinpath(BASE_DIR, "Results", "control_platform",
    "phase2_full_48_climbpath", "g3_repair",
    "catalog_missing_formal_runners_20260801", "runs")
const OUTPUT_ROOT = joinpath(BASE_DIR, "Docs", "报告", "figures", "第10章")

const RESOLUTION = FIG_RES
const CV_XY   = (9.0, 7.5)
const CV_3D   = (9.0, 7.5)
const CV_TIME = (10.0, 6.0)

const CONTROLLERS = [
    ("fixed_awff_l1_indi",          "pass"),
    ("fixed_linear_mpc_l1_indi",    "pass"),
    ("fixed_awff_l1_residual",      "fail"),
    ("fixed_qp_nmpc_l1_indi_cbf",   "fail"),
]

# ===== 数据加载（14列CSV，补算速度和误差） =====
function load_csv(controller_id::String)
    path = joinpath(CSV_ROOT, controller_id, "raw", "$controller_id.csv")
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
    d = Dict(header[j] => cols[j] for j in 1:ncol)

    # 补算 position_error_norm
    n = length(d["time"])
    err = sqrt.((d["x"] .- d["x_ref"]).^2 .+
                (d["y"] .- d["y_ref"]).^2 .+
                (d["z"] .- d["z_ref"]).^2)
    d["position_error_norm"] = err

    # 补算速度（中心差分）
    dt = n >= 2 ? d["time"][2] - d["time"][1] : 0.002
    vx = zeros(n); vy = zeros(n); vz = zeros(n)
    for i in 2:n-1
        vx[i] = (d["x"][i+1] - d["x"][i-1]) / (2dt)
        vy[i] = (d["y"][i+1] - d["y"][i-1]) / (2dt)
        vz[i] = (d["z"][i+1] - d["z"][i-1]) / (2dt)
    end
    vx[1] = (d["x"][2] - d["x"][1]) / dt
    vy[1] = (d["y"][2] - d["y"][1]) / dt
    vz[1] = (d["z"][2] - d["z"][1]) / dt
    vx[n] = (d["x"][n] - d["x"][n-1]) / dt
    vy[n] = (d["y"][n] - d["y"][n-1]) / dt
    vz[n] = (d["z"][n] - d["z"][n-1]) / dt
    d["vx"] = vx; d["vy"] = vy; d["vz"] = vz

    return d
end

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
    fig_trajectory_xy,
    fig_trajectory_3d,
    fig_altitude_z,
    fig_position_error,
    fig_velocity,
    fig_attitude,
    fig_control_input,
]

const FIG_NAMES = [
    "trajectory_xy", "trajectory_3d", "altitude_z",
    "position_error", "velocity", "attitude", "control_input",
]

# ===== 主循环 =====
println("开始为 $(length(CONTROLLERS)) 条控制器生成 7 张/条，共 $(length(CONTROLLERS)*7) 张 PNG")

total_ok = 0
total_fail = 0

for (idx, (cid, st)) in enumerate(CONTROLLERS)
    outdir = joinpath(OUTPUT_ROOT, cid)
    println("[$idx/$(length(CONTROLLERS))] $cid (status=$st)")

    d = load_csv(cid)
    npts = length(d["time"])
    dt = npts >= 2 ? d["time"][2] - d["time"][1] : NaN
    @printf("  rows=%d dt=%.4f\n", npts, dt)

    for (fn, fname) in zip(FIGURES, FIG_NAMES)
        try
            fn(d, outdir)
            global total_ok += 1
        catch e
            global total_fail += 1
            @warn "FAILED $cid/$fname" exception=e
        end
    end
end

println("\n=== 完成 ===")
println("成功 $total_ok 张，失败 $total_fail 张")
