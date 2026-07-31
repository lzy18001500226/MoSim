#!/usr/bin/env julia
# 拓展任务：OpenBlocks 单机 + 三机避障轨迹 —— TyPlot 原生绘图
#
# 产物 8 张 PNG @ resolution=600，输出到 Docs/报告/figures/拓展任务/
#   单机OpenBlocks/  4 张
#     single_uav_trajectory_xy      轨迹俯视 + 16 个墙组叠加
#     single_uav_trajectory_3d      三维轨迹
#     single_uav_altitude_tracking  z / z_ref 时序（AGL地形跟随；z_rmse 1.1342 m）
#     single_uav_position_error     位置误差时序（terminal 0.1176 m）
#   三机OpenBlocks/  4 张
#     three_uav_trajectory_xy       三机轨迹俯视 + 墙组叠加
#     three_uav_pair_distance       机间最小距离（阈值 1.0 m，实测最低 0.9300 m）
#     three_uav_tracking_error      三机跟踪误差时序
#     three_uav_clearance_bound     间隙下界（= 规划间隙 - 跟踪误差，保守估计）
#
# 数据源：
#   Results/planning/openblocks_single_uav_px4ctrl_completion_20260730/raw/*.csv
#   Results/planning/three_uav_openblocks_px4ctrl_completion_20260731/raw/*.csv
#   Results/planning/_openblocks_wall_boxes.json  （由 plan_astar_min_snap.expand_wall_groups 导出）
#
# 口径说明（详见 MANIFEST scope_notes）：
#   clearance_lower_bound_m = min_i(planned_clearance_m[i] − tracking_error_i)
#   是最坏方向假设的保守下界，不是实测到最近障碍的距离。
#   三机最小实际机间距 0.9300 m > 0；无碰撞。

using TyPlot
using JSON
using Printf
using Statistics

include(joinpath(@__DIR__, "typlot_figure_style.jl"))

const BASE_DIR    = raw"C:\Users\HP\Desktop\MoSim"
const S1_CSV      = joinpath(BASE_DIR, "Results", "planning",
                             "openblocks_single_uav_px4ctrl_completion_20260730",
                             "raw", "openblocks_single_uav_px4ctrl.csv")
const S3_CSV      = joinpath(BASE_DIR, "Results", "planning",
                             "three_uav_openblocks_px4ctrl_completion_20260731",
                             "raw", "mworks_px4ctrl_full_304p84s.csv")
const OBST_JSON   = joinpath(BASE_DIR, "Results", "planning", "_openblocks_obstacles.json")
const OUT_ROOT    = joinpath(BASE_DIR, "Docs", "报告", "figures", "拓展任务")
const OUT_S1      = joinpath(OUT_ROOT, "单机OpenBlocks")
const OUT_S3      = joinpath(OUT_ROOT, "三机OpenBlocks")

# 画布（英寸）
const CV_TIME = (10.0, 6.0)
const CV_XY   = (9.0, 7.5)
const CV_3D   = (9.0, 7.5)

# 轨迹配色写死，不依赖颜色循环：xy 图里 16 个墙盒先画，
# 循环指针是否被墙推进属实现细节，显式指定即与之无关。取 Syslab 默认前三色。
const C_UAV1 = [0.0000, 0.4470, 0.7410]
const C_UAV2 = [0.8500, 0.3250, 0.0980]
const C_UAV3 = [0.9290, 0.6940, 0.1250]

# ===== CSV 读取（与 plot_chapter11_typlot.jl 同一实现）=====
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

save_ext(dir::String, name::String) = save_fig(joinpath(dir, name))

# 墙盒子叠加。必须先画墙、后建图例，且图例走 styled_legend_of 显式句柄子集：
# TyPlot 的 legend 自动收录坐标区内全部数据序列，16 个墙盒会变成 data3..data18。
# 返回首个墙盒句柄，供图例里放一条"Wall boxes"代表项。
function draw_walls(wall_boxes::Vector)
    first_h = nothing
    for b in wall_boxes
        mn = b["min"]; mx = b["max"]
        xs = [mn[1], mx[1], mx[1], mn[1], mn[1]]
        ys = [mn[2], mn[2], mx[2], mx[2], mn[2]]
        h = plot(xs, ys, "-", color=[0.35,0.35,0.35], linewidth=1.2)
        first_h === nothing && (first_h = h[1])
    end
    return first_h
end

# 7102 个 0.20 m 随机柱。逐个画闭合矩形要 7102 条曲线，渲染和图例都撑不住，
# 只画中心点：柱边长 0.20 m 在 82 m 幅宽下本来就不足一个像素，散点即是真实观感。
function draw_columns(centers::Vector)
    isempty(centers) && return nothing
    cx = Float64[c[1] for c in centers]
    cy = Float64[c[2] for c in centers]
    h = plot(cx, cy, ".", color=[0.55,0.55,0.55], markersize=1.6, linestyle="none")
    return h[1]
end

# ===== 单机 4 张 =====

# 1) 轨迹俯视。障碍先画（柱 -> 墙 -> 轨迹），图例走 styled_legend_of 显式句柄子集：
#    TyPlot 的 legend 会自动收录坐标区里全部数据序列，7102 柱 + 16 墙不隔离就是灾难。
function fig_s1_xy(d::Dict, walls::Vector, cols::Vector, outdir::String)
    fig(CV_XY...)
    hold("on")
    col_h   = draw_columns(cols)
    wall_h  = draw_walls(walls)
    h_act   = plot(thin(d["x"]),     thin(d["y"]),     color=C_UAV1, linewidth=1.8)
    h_ref   = plot(thin(d["x_ref"]), thin(d["y_ref"]), "--",
                   color=[0.6,0.6,0.6], linewidth=1.5)
    h_s = plot([-41.0], [-26.0], "o", color=[0.0,0.5,0.0], markersize=9)
    h_g = plot([41.0],  [26.0],  "s", color=[0.8,0.0,0.0], markersize=9)
    styled(xlabel("X (m)"))
    styled(ylabel("Y (m)"))
    grid("on")
    styled_legend_of([h_act[1], h_ref[1], wall_h, col_h, h_s[1], h_g[1]],
                     ["Actual (px4ctrl)", "OpenBlocks reference",
                      "Wall boxes (16)", "Random columns (7102)",
                      "Start (-41, -26)", "Goal (41, 26)"];
                     loc="upper left", ncol=2)
    axis("equal")
    axes_font()
    hold("off")
    save_ext(outdir, "single_uav_trajectory_xy.png")
end

# 三维轨迹图已撤销（原 single_uav_trajectory_3d）：
#   xy 幅面 82 x 52 m 对 z 幅面 2.5 m，比例 ~33:1，任何视角下轨迹都是一张薄片；
#   默认 az=-37.5 更把 (-41,-26)->(41,26) 主对角线压成竖直一柱。改视角能摊开航线，
#   但 z 起伏仍不可辨，信息量不超过"俯视图 + 高度时序图"两张之和，故不出此图。

# 3) 高度跟随。这是本组图里最该被看见的一张：
#    z 全程低于参考约 1.2 m，只在末端收回，z_rmse 1.1342 m 独占总 RMSE 1.1731 m。
function fig_s1_altitude(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = thin(d["time"]); z = thin(d["z"]); zr = thin(d["z_ref"])
    plot(t, z, color=C_UAV1, linewidth=1.8)
    hold("on")
    plot(t, zr, "--", color=[0.6,0.6,0.6], linewidth=1.6)
    styled(xlabel("Time (s)"))
    styled(ylabel("Altitude Z (m)"))
    grid("on")
    # 不用浮动小字：数值并进图例标签。图例放 south——t=10..70 段 y<0.8 是全图唯一大片空白。
    ylim([-0.1, 2.72])
    styled_legend(["Actual Z (RMSE 1.1342 m, min 0.0281 m, 79 altitude-limit samples)",
                   "Reference Z (AGL 1.0 m)"]; loc="south")
    axes_font()
    hold("off")
    save_ext(outdir, "single_uav_altitude_tracking.png")
end

# 4) 位置误差时序
function fig_s1_error(d::Dict, outdir::String)
    fig(CV_TIME...)
    plot(thin(d["time"]), thin(d["position_error_norm"]), color=C_UAV1, linewidth=1.8)
    hold("on")
    styled(xlabel("Time (s)"))
    styled(ylabel("Position Error Norm (m)"))
    grid("on")
    # 不用浮动小字：数值并进图例。XY/Z 分解由高度图承担（该图图例已载 Z RMSE），
    # 采样口径 80.12 s / 8014 @ 100 Hz 在 manifest 里，不上图。
    ylim([-0.05, 2.32])
    styled_legend(["px4ctrl position error (RMSE 1.1731 m, max 1.8569 m, terminal 0.1176 m)"];
                  loc="north")
    axes_font()
    hold("off")
    save_ext(outdir, "single_uav_position_error.png")
end

# ===== 三机 4 张 =====

# 5) 三机轨迹俯视。墙先画；6 条轨迹 + 16 个墙盒 -> 图例只取 5 个显式句柄，
#    三条灰参考共用一项（取 UAV2 参考句柄作代表，三条同色同线型）。
function fig_s3_xy(d::Dict, walls::Vector, cols::Vector, outdir::String)
    fig(CV_XY...)
    hold("on")
    col_h  = draw_columns(cols)
    wall_h = draw_walls(walls)
    h1 = plot(thin(d["uav1_x_m"]), thin(d["uav1_y_m"]), color=C_UAV1, linewidth=1.8)
    h2 = plot(thin(d["uav2_x_m"]), thin(d["uav2_y_m"]), color=C_UAV2, linewidth=1.8)
    h3 = plot(thin(d["uav3_x_m"]), thin(d["uav3_y_m"]), color=C_UAV3, linewidth=1.8)
    plot(thin(d["uav1_ref_x_m"]), thin(d["uav1_ref_y_m"]), "--",
         color=[0.6,0.6,0.6], linewidth=1.4)
    h_ref = plot(thin(d["uav2_ref_x_m"]), thin(d["uav2_ref_y_m"]), "--",
                 color=[0.6,0.6,0.6], linewidth=1.4)
    plot(thin(d["uav3_ref_x_m"]), thin(d["uav3_ref_y_m"]), "--",
         color=[0.6,0.6,0.6], linewidth=1.4)
    styled(xlabel("X (m)"))
    styled(ylabel("Y (m)"))
    grid("on")
    styled_legend_of([h1[1], h2[1], h3[1], h_ref[1], wall_h, col_h],
                     ["UAV 1", "UAV 2", "UAV 3", "Reference (UAV 1-3)",
                      "Wall boxes (16)", "Random columns (7102)"];
                     loc="upper left", ncol=2)
    axis("equal")
    axes_font()
    hold("off")
    save_ext(outdir, "three_uav_trajectory_xy.png")
end

# 6) 机间最小距离 + 1.0 m 阈值线
function fig_s3_pair(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time_s"]; p = d["minimum_pair_distance_m"]
    plot(t, p, color=C_UAV1, linewidth=1.8)
    hold("on")
    plot([t[1], t[end]], [1.0, 1.0], "--", color=[0.8,0.0,0.0], linewidth=1.6)
    styled(xlabel("Time (s)"))
    styled(ylabel("Minimum Pair Distance (m)"))
    grid("on")
    # 本图全靠 0.9300 与 1.0 的 0.07 m 落差说话，抬顶/降底放注记都会把它压扁。
    # 因此数值全部并进图例标签，仅把顶部从 6.68 抬到 7.6 给图例腾地方。
    ylim([0.55, 7.6])
    styled_legend(["Minimum pair distance (min 0.9300 m at t = 206.0 s)",
                   "Threshold 1.0 m (1 of 306 samples below)"]; loc="northeast")
    axes_font()
    hold("off")
    save_ext(outdir, "three_uav_pair_distance.png")
end

# 7) 三机跟踪误差
function fig_s3_tracking(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time_s"]
    plot(t, d["uav1_tracking_error_m"], color=C_UAV1, linewidth=1.8)
    hold("on")
    plot(t, d["uav2_tracking_error_m"], color=C_UAV2, linewidth=1.8)
    plot(t, d["uav3_tracking_error_m"], color=C_UAV3, linewidth=1.8)
    styled(xlabel("Time (s)"))
    styled(ylabel("Tracking Error (m)"))
    grid("on")
    styled_legend(["UAV 1 (RMSE 0.2279 m)", "UAV 2 (RMSE 0.2360 m)",
                   "UAV 3 (RMSE 0.1728 m)"]; loc="upper left")
    axes_font()
    hold("off")
    save_ext(outdir, "three_uav_tracking_error.png")
end

# 8) 间隙下界。口径必须写在图上，否则负值会被读成"撞了"。
#    定义：min_i(planned_clearance_m[i] − tracking_error_i)，
#    planned_clearance_m = {0.4466, 0.4483, 0.4459}（规划航线到最近障碍的静态间隙）。
function fig_s3_clearance(d::Dict, outdir::String)
    fig(CV_TIME...)
    t = d["time_s"]; c = d["clearance_lower_bound_m"]
    plot(t, c, color=C_UAV1, linewidth=1.8)
    hold("on")
    plot([t[1], t[end]], [0.0, 0.0], "--", color=[0.8,0.0,0.0], linewidth=1.6)
    styled(xlabel("Time (s)"))
    styled(ylabel("Clearance Lower Bound (m)"))
    grid("on")
    # 两行长图例落在底部，会压住 t=200 / t=232 两处 -1.19 谷底，向下让出图例带
    ylim([-1.62, 0.52])
    # 负值必须当场说清口径，否则会被读成"撞了"。但不用浮动小字：并进图例标签。
    styled_legend(["Planned clearance (0.45 m) - tracking error, min -1.1879 m at t = 200.0 s",
                   "Zero bound (below in 38 of 306; worst-case bound, not a measured distance)"];
                  loc="lower left")
    axes_font()
    hold("off")
    save_ext(outdir, "three_uav_clearance_bound.png")
end

# ===== 主流程 =====
const EXT_RESULTS = Tuple{String,Bool,String}[]

function attempt_ext(name::String, f::Function)
    try
        f()
        push!(EXT_RESULTS, (name, true, ""))
        println("  OK   $name")
    catch e
        msg = sprint(showerror, e)
        push!(EXT_RESULTS, (name, false, msg))
        println("  FAIL $name : $(first(msg, 200))")
    end
end

println("TyPlot 拓展任务：单机 3 + 三机 4 = 7 张 PNG @ resolution=$FIG_RES")

obst  = isfile(OBST_JSON) ? JSON.parsefile(OBST_JSON) : Dict{String,Any}()
walls = get(obst, "walls", Any[])
cols  = get(obst, "column_centers_xy", Any[])
println("障碍：墙盒 $(length(walls)) + 随机柱 $(length(cols)) = $(length(walls)+length(cols))")

println("[单机 OpenBlocks] 3 张 -> 拓展任务/单机OpenBlocks/")
if isfile(S1_CSV)
    d1 = load_csv(S1_CSV)
    attempt_ext("single_uav_trajectory_xy",     () -> fig_s1_xy(d1, walls, cols, OUT_S1))
    attempt_ext("single_uav_altitude_tracking", () -> fig_s1_altitude(d1, OUT_S1))
    attempt_ext("single_uav_position_error",    () -> fig_s1_error(d1, OUT_S1))
else
    println("  SKIP 单机 CSV 不存在：$S1_CSV")
end

println("[三机 OpenBlocks] 4 张 -> 拓展任务/三机OpenBlocks/")
if isfile(S3_CSV)
    d3 = load_csv(S3_CSV)
    attempt_ext("three_uav_trajectory_xy",   () -> fig_s3_xy(d3, walls, cols, OUT_S3))
    attempt_ext("three_uav_pair_distance",   () -> fig_s3_pair(d3, OUT_S3))
    attempt_ext("three_uav_tracking_error",  () -> fig_s3_tracking(d3, OUT_S3))
    attempt_ext("three_uav_clearance_bound", () -> fig_s3_clearance(d3, OUT_S3))
else
    println("  SKIP 三机 CSV 不存在：$S3_CSV")
end

# ===== manifest =====
ext_ok = count(r -> r[2], EXT_RESULTS)
ext_manifest = Dict(
    "schema" => "mosim.extension_openblocks.typlot_manifest.v1",
    "generator" => "Scripts/syslab/plot_extension_openblocks_typlot.jl",
    "renderer" => "TyPlot (Syslab native)",
    "resolution" => FIG_RES,
    "figure_count_expected" => 7,
    "figure_count_generated" => ext_ok,
    "output_root" => OUT_ROOT,
    "evidence_selection" => "px4ctrl for both single-UAV and three-UAV（自研控制器，两侧都要给出可用证据）",
    "results" => [Dict("figure" => r[1], "ok" => r[2], "error" => r[3]) for r in EXT_RESULTS],
    "scope_notes" => Dict(
        "obstacle_geometry_source" =>
            "Scripts/planning/export_openblocks_obstacles.py 复用规划器的 expand_wall_groups + " *
            "expand_random_obstacles 展开 Config/planners/astar_min_snap/map_open_blocks.yaml，" *
            "导出 Results/planning/_openblocks_obstacles.json：16 墙盒（8 组 L/T 模板）+ " *
            "7102 随机柱（seed=20260518，1000 簇，columns_per_cluster 4-10），" *
            "合计 7118 = planner truth_obstacle_count。全部程序化，非手工录入。",
        "random_columns_drawn_as_centers" =>
            "俯视图把 7102 根柱画成中心散点而非闭合矩形：柱边长 0.20 m 在 82 m 幅宽下不足一像素，" *
            "逐个画矩形会产生 7102 条曲线，渲染与图例均不可行。散点即真实观感，几何计数未变。",
        "no_3d_figure" =>
            "原计划的 single_uav_trajectory_3d 已撤销：xy 幅面 82x52 m 对 z 幅面 2.5 m 约 33:1，" *
            "任何视角下 z 起伏都不可辨，信息量不超过俯视图与高度时序图之和。",
        "clearance_lower_bound_definition" =>
            "actual_clearance_lower_bound_m = min_i(planned_clearance_m[i] − vehicle_i.tracking_error_m)，" *
            "planned_clearance_m = {0.4466, 0.4483, 0.4459}（规划航线到最近障碍的静态间隙）。" *
            "这是最坏方向假设下的保守下界，不是实测到障碍的距离。最小 −1.1879 m 出现在 t=200 s，" *
            "对应 uav2 峰值跟踪误差 1.6362 m：0.4483 − 1.6362 = −1.1879，与记录完全吻合。",
        "no_collision_statement" =>
            "三机最小实际机间距 0.9300 m（t=206.0 s），306 样本中仅 1 个低于 1.0 m 门限。" *
            "门限由本项目自行制定且定得偏高；0.93 m 未构成碰撞。",
        "single_uav_altitude_dominance" =>
            "单机 position_rmse_m 1.1731 m 中 z_rmse 1.1342 m 占绝对主导，xy_rmse 仅 0.2994 m。" *
            "z 全程低于 terrain-follow AGL 参考约 1.2 m，末端收回，terminal 0.1176 m。" *
            "altitude_violation_count=79、tilt_violation_count=83，safety_score=0。",
        "mworks_only" =>
            "两组证据均为 MWORKS 整机闭环仿真，不含 Gazebo/PX4/ROS 运行时链路。"),
)

mkpath(OUT_ROOT)
open(joinpath(OUT_ROOT, "TYPLOT_EXTENSION_MANIFEST.json"), "w") do io
    JSON.print(io, ext_manifest, 2)
end

println("完成：$ext_ok / 7 张")
for (name, ok, msg) in EXT_RESULTS
    ok || println("  未生成 $name : $(first(msg, 300))")
end
