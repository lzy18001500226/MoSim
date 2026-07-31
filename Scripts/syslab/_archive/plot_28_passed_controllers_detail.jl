#!/usr/bin/env julia
# 为 28 条性能达标控制器生成详细轨迹图（7 张/控制器 = 196 张总计）
# 口径：28 = performance_accepted（终端位置误差 < 5 m），等于 effective_passed_count。
# awff 已于 2026-07-31 归档至 Docs/报告/图/归档/awff负性能样本_20260731/
#   （跑通但终端误差 48.82 m，属 ran_to_completion=38 而非 performance_accepted=28）。
# 口径权威：Config/control_platform/climbpath_baseline_count_definition.json
# 输出目录: Docs/报告/figures/第10章/{controller_id}/

using Statistics

# ===== 配置 =====
const BASE_DIR = raw"C:\Users\HP\Desktop\MoSim"
const CSV_ROOT = joinpath(BASE_DIR, "Results", "control_platform", "phase2_full_48_climbpath")
const OUTPUT_ROOT = joinpath(BASE_DIR, "Docs", "报告", "figures", "第10章")
const G3_STATUS_PATH = joinpath(BASE_DIR, "Results", "control_platform", "phase2_full_48_climbpath", "g3_repair", "G3_STATUS.json")

# 28 条性能达标控制器 ID（终端位置误差 < 5 m）
const PASSED_CONTROLLERS = [
    "adaptive_backstepping",
    "adaptive_smc",
    "backstepping_baseline",
    "dfbc_basic",
    "dfbc_high_order",
    "dfbc_high_order_body_rate",
    "dfbc_smooth_robust",
    "dfbc_smooth_robust_body_rate",
    "explicit_gain_scheduled_mpc",
    "feedback_linearization",
    "fuzzy_smc",
    "h_2_state_feedback",
    "ilqr",
    "integral_smc",
    "lqg",
    "lqi",
    "lqr_baseline",
    "mppi",
    "ndi",
    "nonsingular_terminal_smc",
    "official_pid",
    "official_pid_yaw_authority_mapped",
    "passivity_based_control",
    "px4ctrl",
    "robust_mpc",
    "se_3_basic",
    "terminal_smc",
    "tube_mpc"
]

# ===== 字体标准 =====
const AXIS_FONT_SIZE = 18
const TICK_FONT_SIZE = 16
const FONT_FAMILY = "Times New Roman"

# ===== 辅助函数 =====
function load_csv(controller_id::String)
    csv_path = joinpath(CSV_ROOT, controller_id, "raw", "climbpath50s.csv")
    if !isfile(csv_path)
        @warn "CSV not found for $controller_id: $csv_path"
        return nothing
    end

    # 简单 CSV 解析（假设逗号分隔，第一行是表头）
    lines = readlines(csv_path)
    if length(lines) < 2
        @warn "CSV too short for $controller_id"
        return nothing
    end

    header = split(lines[1], ',')
    data = Dict{String, Vector{Float64}}()

    for col_name in header
        data[strip(col_name)] = Float64[]
    end

    for line in lines[2:end]
        values = split(line, ',')
        if length(values) != length(header)
            continue
        end
        for (i, col_name) in enumerate(header)
            try
                push!(data[strip(col_name)], parse(Float64, values[i]))
            catch
                push!(data[strip(col_name)], NaN)
            end
        end
    end

    return data
end

function write_svg(path::String, content::String)
    mkpath(dirname(path))
    open(path, "w") do io
        write(io, content)
    end
    println("✓ Written: $path")
end

function finite_values(arr)
    filter(x -> isfinite(x), arr)
end

# ===== SVG 绘图函数 =====

function plot_trajectory_xy(data::Dict{String, Vector{Float64}}, controller_id::String)
    width, height = 980, 720
    left, right, top, bottom = 100.0, 40.0, 60.0, 90.0
    plot_width = width - left - right
    plot_height = height - top - bottom

    x_vals = finite_values(data["x"])
    y_vals = finite_values(data["y"])
    x_ref_vals = finite_values(data["x_ref"])
    y_ref_vals = finite_values(data["y_ref"])

    if isempty(x_vals) || isempty(y_vals)
        @warn "No valid XY data for $controller_id"
        return nothing
    end

    x_min = min(minimum(x_vals), minimum(x_ref_vals))
    x_max = max(maximum(x_vals), maximum(x_ref_vals))
    y_min = min(minimum(y_vals), minimum(y_ref_vals))
    y_max = max(maximum(y_vals), maximum(y_ref_vals))

    x_range = x_max - x_min
    y_range = y_max - y_min
    x_min -= 0.1 * x_range
    x_max += 0.1 * x_range
    y_min -= 0.1 * y_range
    y_max += 0.1 * y_range

    scale_x(v) = left + (v - x_min) / (x_max - x_min) * plot_width
    scale_y(v) = height - bottom - (v - y_min) / (y_max - y_min) * plot_height

    # 生成路径
    ref_points = join(["$(scale_x(xr)),$(scale_y(yr))" for (xr, yr) in zip(x_ref_vals, y_ref_vals)], " ")
    actual_points = join(["$(scale_x(x)),$(scale_y(y))" for (x, y) in zip(x_vals, y_vals)], " ")

    # X 轴刻度
    x_ticks = range(x_min, x_max, length=6)
    x_tick_svg = join(["""
        <line x1="$(scale_x(xt))" y1="$(height - bottom)" x2="$(scale_x(xt))" y2="$(height - bottom + 5)" stroke="#333" stroke-width="1"/>
        <text x="$(scale_x(xt))" y="$(height - bottom + 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(xt, digits=1))</text>
    """ for xt in x_ticks], "\n")

    # Y 轴刻度
    y_ticks = range(y_min, y_max, length=6)
    y_tick_svg = join(["""
        <line x1="$(left)" y1="$(scale_y(yt))" x2="$(left - 5)" y2="$(scale_y(yt))" stroke="#333" stroke-width="1"/>
        <text x="$(left - 10)" y="$(scale_y(yt) + 5)" text-anchor="end" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(yt, digits=1))</text>
    """ for yt in y_ticks], "\n")

    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="$width" height="$height">
        <rect width="$width" height="$height" fill="white"/>

        <!-- 坐标轴 -->
        <line x1="$left" y1="$(height - bottom)" x2="$(width - right)" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        <line x1="$left" y1="$top" x2="$left" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>

        <!-- X 轴刻度 -->
        $x_tick_svg

        <!-- Y 轴刻度 -->
        $y_tick_svg

        <!-- 轴标签 -->
        <text x="$(width/2)" y="$(height - 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold">X Position (m)</text>
        <text x="25" y="$(height/2)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold" transform="rotate(-90, 25, $(height/2))">Y Position (m)</text>

        <!-- 参考轨迹 -->
        <polyline points="$ref_points" fill="none" stroke="#999" stroke-width="2" stroke-dasharray="5,5"/>

        <!-- 实际轨迹 -->
        <polyline points="$actual_points" fill="none" stroke="#2563eb" stroke-width="2.5"/>

        <!-- 图例 -->
        <line x1="$(width - right - 150)" y1="$(top + 20)" x2="$(width - right - 110)" y2="$(top + 20)" stroke="#999" stroke-width="2" stroke-dasharray="5,5"/>
        <text x="$(width - right - 105)" y="$(top + 25)" font-family="$FONT_FAMILY" font-size="14px">Reference</text>
        <line x1="$(width - right - 150)" y1="$(top + 45)" x2="$(width - right - 110)" y2="$(top + 45)" stroke="#2563eb" stroke-width="2.5"/>
        <text x="$(width - right - 105)" y="$(top + 50)" font-family="$FONT_FAMILY" font-size="14px">Actual</text>
    </svg>
    """

    return svg
end

function plot_altitude_z(data::Dict{String, Vector{Float64}}, controller_id::String)
    width, height = 980, 620
    left, right, top, bottom = 100.0, 40.0, 60.0, 90.0
    plot_width = width - left - right
    plot_height = height - top - bottom

    t_vals = finite_values(data["time"])
    z_vals = finite_values(data["z"])
    z_ref_vals = finite_values(data["z_ref"])

    if isempty(t_vals) || isempty(z_vals)
        @warn "No valid Z data for $controller_id"
        return nothing
    end

    t_min, t_max = minimum(t_vals), maximum(t_vals)
    z_min = min(minimum(z_vals), minimum(z_ref_vals))
    z_max = max(maximum(z_vals), maximum(z_ref_vals))

    z_range = z_max - z_min
    z_min -= 0.1 * z_range
    z_max += 0.1 * z_range

    scale_x(t) = left + (t - t_min) / (t_max - t_min) * plot_width
    scale_y(z) = height - bottom - (z - z_min) / (z_max - z_min) * plot_height

    ref_points = join(["$(scale_x(t)),$(scale_y(zr))" for (t, zr) in zip(t_vals, z_ref_vals)], " ")
    actual_points = join(["$(scale_x(t)),$(scale_y(z))" for (t, z) in zip(t_vals, z_vals)], " ")

    t_ticks = range(t_min, t_max, length=6)
    t_tick_svg = join(["""
        <line x1="$(scale_x(tt))" y1="$(height - bottom)" x2="$(scale_x(tt))" y2="$(height - bottom + 5)" stroke="#333" stroke-width="1"/>
        <text x="$(scale_x(tt))" y="$(height - bottom + 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(tt, digits=1))</text>
    """ for tt in t_ticks], "\n")

    z_ticks = range(z_min, z_max, length=6)
    z_tick_svg = join(["""
        <line x1="$(left)" y1="$(scale_y(zt))" x2="$(left - 5)" y2="$(scale_y(zt))" stroke="#333" stroke-width="1"/>
        <text x="$(left - 10)" y="$(scale_y(zt) + 5)" text-anchor="end" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(zt, digits=1))</text>
    """ for zt in z_ticks], "\n")

    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="$width" height="$height">
        <rect width="$width" height="$height" fill="white"/>
        <line x1="$left" y1="$(height - bottom)" x2="$(width - right)" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        <line x1="$left" y1="$top" x2="$left" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        $t_tick_svg
        $z_tick_svg
        <text x="$(width/2)" y="$(height - 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold">Time (s)</text>
        <text x="25" y="$(height/2)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold" transform="rotate(-90, 25, $(height/2))">Altitude (m)</text>
        <polyline points="$ref_points" fill="none" stroke="#999" stroke-width="2" stroke-dasharray="5,5"/>
        <polyline points="$actual_points" fill="none" stroke="#16a34a" stroke-width="2.5"/>
        <line x1="$(width - right - 150)" y1="$(top + 20)" x2="$(width - right - 110)" y2="$(top + 20)" stroke="#999" stroke-width="2" stroke-dasharray="5,5"/>
        <text x="$(width - right - 105)" y="$(top + 25)" font-family="$FONT_FAMILY" font-size="14px">Reference</text>
        <line x1="$(width - right - 150)" y1="$(top + 45)" x2="$(width - right - 110)" y2="$(top + 45)" stroke="#16a34a" stroke-width="2.5"/>
        <text x="$(width - right - 105)" y="$(top + 50)" font-family="$FONT_FAMILY" font-size="14px">Actual</text>
    </svg>
    """

    return svg
end

function plot_position_error(data::Dict{String, Vector{Float64}}, controller_id::String)
    width, height = 980, 620
    left, right, top, bottom = 100.0, 40.0, 60.0, 90.0
    plot_width = width - left - right
    plot_height = height - top - bottom

    t_vals = finite_values(data["time"])
    ex_vals = data["x_ref"] .- data["x"]
    ey_vals = data["y_ref"] .- data["y"]
    ez_vals = data["z_ref"] .- data["z"]

    ex_vals = finite_values(ex_vals)
    ey_vals = finite_values(ey_vals)
    ez_vals = finite_values(ez_vals)

    if isempty(t_vals)
        @warn "No valid time data for $controller_id"
        return nothing
    end

    t_min, t_max = minimum(t_vals), maximum(t_vals)
    e_min = min(minimum(ex_vals), minimum(ey_vals), minimum(ez_vals))
    e_max = max(maximum(ex_vals), maximum(ey_vals), maximum(ez_vals))

    e_range = e_max - e_min
    e_min -= 0.1 * e_range
    e_max += 0.1 * e_range

    scale_x(t) = left + (t - t_min) / (t_max - t_min) * plot_width
    scale_y(e) = height - bottom - (e - e_min) / (e_max - e_min) * plot_height

    ex_points = join(["$(scale_x(t)),$(scale_y(e))" for (t, e) in zip(t_vals, ex_vals)], " ")
    ey_points = join(["$(scale_x(t)),$(scale_y(e))" for (t, e) in zip(t_vals, ey_vals)], " ")
    ez_points = join(["$(scale_x(t)),$(scale_y(e))" for (t, e) in zip(t_vals, ez_vals)], " ")

    t_ticks = range(t_min, t_max, length=6)
    t_tick_svg = join(["""
        <line x1="$(scale_x(tt))" y1="$(height - bottom)" x2="$(scale_x(tt))" y2="$(height - bottom + 5)" stroke="#333" stroke-width="1"/>
        <text x="$(scale_x(tt))" y="$(height - bottom + 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(tt, digits=1))</text>
    """ for tt in t_ticks], "\n")

    e_ticks = range(e_min, e_max, length=6)
    e_tick_svg = join(["""
        <line x1="$(left)" y1="$(scale_y(et))" x2="$(left - 5)" y2="$(scale_y(et))" stroke="#333" stroke-width="1"/>
        <text x="$(left - 10)" y="$(scale_y(et) + 5)" text-anchor="end" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(et, digits=2))</text>
    """ for et in e_ticks], "\n")

    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="$width" height="$height">
        <rect width="$width" height="$height" fill="white"/>
        <line x1="$left" y1="$(height - bottom)" x2="$(width - right)" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        <line x1="$left" y1="$top" x2="$left" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        $t_tick_svg
        $e_tick_svg
        <text x="$(width/2)" y="$(height - 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold">Time (s)</text>
        <text x="25" y="$(height/2)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold" transform="rotate(-90, 25, $(height/2))">Position Error (m)</text>
        <polyline points="$ex_points" fill="none" stroke="#dc2626" stroke-width="2"/>
        <polyline points="$ey_points" fill="none" stroke="#16a34a" stroke-width="2"/>
        <polyline points="$ez_points" fill="none" stroke="#2563eb" stroke-width="2"/>
        <line x1="$(width - right - 150)" y1="$(top + 20)" x2="$(width - right - 110)" y2="$(top + 20)" stroke="#dc2626" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 25)" font-family="$FONT_FAMILY" font-size="14px">e_x</text>
        <line x1="$(width - right - 150)" y1="$(top + 45)" x2="$(width - right - 110)" y2="$(top + 45)" stroke="#16a34a" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 50)" font-family="$FONT_FAMILY" font-size="14px">e_y</text>
        <line x1="$(width - right - 150)" y1="$(top + 70)" x2="$(width - right - 110)" y2="$(top + 70)" stroke="#2563eb" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 75)" font-family="$FONT_FAMILY" font-size="14px">e_z</text>
    </svg>
    """

    return svg
end

function plot_control_input(data::Dict{String, Vector{Float64}}, controller_id::String)
    width, height = 980, 720
    left, right, top, bottom = 100.0, 40.0, 60.0, 90.0
    plot_width = width - left - right
    plot_height = height - top - bottom

    t_vals = finite_values(data["time"])
    u1_vals = finite_values(data["u1"])
    u2_vals = finite_values(data["u2"])
    u3_vals = finite_values(data["u3"])
    u4_vals = finite_values(data["u4"])

    if isempty(t_vals)
        @warn "No valid control data for $controller_id"
        return nothing
    end

    t_min, t_max = minimum(t_vals), maximum(t_vals)
    u_min = min(minimum(u1_vals), minimum(u2_vals), minimum(u3_vals), minimum(u4_vals))
    u_max = max(maximum(u1_vals), maximum(u2_vals), maximum(u3_vals), maximum(u4_vals))

    u_range = u_max - u_min
    u_min -= 0.1 * u_range
    u_max += 0.1 * u_range

    scale_x(t) = left + (t - t_min) / (t_max - t_min) * plot_width
    scale_y(u) = height - bottom - (u - u_min) / (u_max - u_min) * plot_height

    u1_points = join(["$(scale_x(t)),$(scale_y(u))" for (t, u) in zip(t_vals, u1_vals)], " ")
    u2_points = join(["$(scale_x(t)),$(scale_y(u))" for (t, u) in zip(t_vals, u2_vals)], " ")
    u3_points = join(["$(scale_x(t)),$(scale_y(u))" for (t, u) in zip(t_vals, u3_vals)], " ")
    u4_points = join(["$(scale_x(t)),$(scale_y(u))" for (t, u) in zip(t_vals, u4_vals)], " ")

    t_ticks = range(t_min, t_max, length=6)
    t_tick_svg = join(["""
        <line x1="$(scale_x(tt))" y1="$(height - bottom)" x2="$(scale_x(tt))" y2="$(height - bottom + 5)" stroke="#333" stroke-width="1"/>
        <text x="$(scale_x(tt))" y="$(height - bottom + 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(tt, digits=1))</text>
    """ for tt in t_ticks], "\n")

    u_ticks = range(u_min, u_max, length=6)
    u_tick_svg = join(["""
        <line x1="$(left)" y1="$(scale_y(ut))" x2="$(left - 5)" y2="$(scale_y(ut))" stroke="#333" stroke-width="1"/>
        <text x="$(left - 10)" y="$(scale_y(ut) + 5)" text-anchor="end" font-family="$FONT_FAMILY" font-size="$(TICK_FONT_SIZE)px">$(round(ut, digits=0))</text>
    """ for ut in u_ticks], "\n")

    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="$width" height="$height">
        <rect width="$width" height="$height" fill="white"/>
        <line x1="$left" y1="$(height - bottom)" x2="$(width - right)" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        <line x1="$left" y1="$top" x2="$left" y2="$(height - bottom)" stroke="#333" stroke-width="2"/>
        $t_tick_svg
        $u_tick_svg
        <text x="$(width/2)" y="$(height - 25)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold">Time (s)</text>
        <text x="25" y="$(height/2)" text-anchor="middle" font-family="$FONT_FAMILY" font-size="$(AXIS_FONT_SIZE)px" font-weight="bold" transform="rotate(-90, 25, $(height/2))">Rotor Speed (rad/s)</text>
        <polyline points="$u1_points" fill="none" stroke="#dc2626" stroke-width="1.5"/>
        <polyline points="$u2_points" fill="none" stroke="#16a34a" stroke-width="1.5"/>
        <polyline points="$u3_points" fill="none" stroke="#2563eb" stroke-width="1.5"/>
        <polyline points="$u4_points" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
        <line x1="$(width - right - 150)" y1="$(top + 20)" x2="$(width - right - 110)" y2="$(top + 20)" stroke="#dc2626" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 25)" font-family="$FONT_FAMILY" font-size="14px">Motor 1</text>
        <line x1="$(width - right - 150)" y1="$(top + 45)" x2="$(width - right - 110)" y2="$(top + 45)" stroke="#16a34a" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 50)" font-family="$FONT_FAMILY" font-size="14px">Motor 2</text>
        <line x1="$(width - right - 150)" y1="$(top + 70)" x2="$(width - right - 110)" y2="$(top + 70)" stroke="#2563eb" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 75)" font-family="$FONT_FAMILY" font-size="14px">Motor 3</text>
        <line x1="$(width - right - 150)" y1="$(top + 95)" x2="$(width - right - 110)" y2="$(top + 95)" stroke="#f59e0b" stroke-width="2"/>
        <text x="$(width - right - 105)" y="$(top + 100)" font-family="$FONT_FAMILY" font-size="14px">Motor 4</text>
    </svg>
    """

    return svg
end

# ===== 主流程 =====
function main()
    println("开始生成 28 个通过控制器的详细轨迹图...")
    println("输出目录: $OUTPUT_ROOT")

    total_generated = 0

    for controller_id in PASSED_CONTROLLERS
        println("\n处理控制器: $controller_id")

        data = load_csv(controller_id)
        if data === nothing
            @warn "跳过 $controller_id (CSV 不存在)"
            continue
        end

        output_dir = joinpath(OUTPUT_ROOT, controller_id)

        # 1. trajectory_xy
        svg = plot_trajectory_xy(data, controller_id)
        if svg !== nothing
            write_svg(joinpath(output_dir, "trajectory_xy.svg"), svg)
            total_generated += 1
        end

        # 2. altitude_z
        svg = plot_altitude_z(data, controller_id)
        if svg !== nothing
            write_svg(joinpath(output_dir, "altitude_z.svg"), svg)
            total_generated += 1
        end

        # 3. position_error
        svg = plot_position_error(data, controller_id)
        if svg !== nothing
            write_svg(joinpath(output_dir, "position_error.svg"), svg)
            total_generated += 1
        end

        # 4. control_input
        svg = plot_control_input(data, controller_id)
        if svg !== nothing
            write_svg(joinpath(output_dir, "control_input.svg"), svg)
            total_generated += 1
        end
    end

    println("\n" * "="^60)
    println("✅ 完成！共生成 $total_generated 张 SVG 图片")
    println("预期: 28 控制器 × 4 图/控制器 = 112 张")
    println("="^60)
end

main()
