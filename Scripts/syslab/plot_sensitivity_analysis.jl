#!/usr/bin/env julia

# Generate sensitivity analysis figures
# Usage:
#   julia Scripts/syslab/plot_sensitivity_analysis.jl \
#     --wind Results/control_platform/sensitivity_wind_v1 \
#     --param Results/control_platform/sensitivity_param_v1 \
#     --motor Results/control_platform/sensitivity_motor_v1 \
#     --output Docs/figures/第11章/灵敏度分析

include(joinpath(@__DIR__, "..", "results", "calc_metrics.jl"))

const COLORS = ["#1f77b4", "#d62728"]

function svg_escape(value)
    return replace(string(value), "&" => "&amp;", "<" => "&lt;", ">" => "&gt;", "\"" => "&quot;")
end

function scaled(value, lower, upper, pixel_lower, pixel_upper)
    upper <= lower + 1e-12 && return (pixel_lower + pixel_upper) / 2
    return pixel_lower + (value - lower) * (pixel_upper - pixel_lower) / (upper - lower)
end

function load_sensitivity_csv(path::String)
    isfile(path) || return nothing
    _, columns = read_csv(path)
    return columns
end

function compute_position_rmse(columns)
    error_x = columns["x"] .- columns["x_ref"]
    error_y = columns["y"] .- columns["y_ref"]
    error_z = columns["z"] .- columns["z_ref"]
    return sqrt(sum(error_x.^2 .+ error_y.^2 .+ error_z.^2) / length(error_x))
end

function write_sensitivity_curve(path::String, x_values, official_rmse, px4ctrl_rmse, x_label::String, title::String)
    width, height = 1080, 620
    left, right, top, bottom = 140.0, 45.0, 55.0, 90.0

    valid_rmse = vcat(
        [r for r in official_rmse if isfinite(r)],
        [r for r in px4ctrl_rmse if isfinite(r)]
    )

    x_min, x_max = minimum(x_values), maximum(x_values)
    y_min = 0.0
    y_max = isempty(valid_rmse) ? 1.0 : maximum(valid_rmse) * 1.15

    plot_width = width - left - right
    plot_height = height - top - bottom

    mkpath(dirname(path))
    open(path, "w") do io
        println(io, "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"$width\" height=\"$height\" viewBox=\"0 0 $width $height\">")
        println(io, "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>")

        # Axes
        println(io, "<rect x=\"$left\" y=\"$top\" width=\"$plot_width\" height=\"$plot_height\" fill=\"none\" stroke=\"#222\"/>")

        # Y-axis grid and labels
        for tick in 0:5
            y_value = y_min + (y_max - y_min) * tick / 5
            y_pixel = scaled(y_value, y_min, y_max, top + plot_height, top)
            println(io, "<line x1=\"$left\" y1=\"$y_pixel\" x2=\"$(left + plot_width)\" y2=\"$y_pixel\" stroke=\"#eeeeee\"/>")
            println(io, "<text x=\"$(left - 8)\" y=\"$(y_pixel + 4)\" text-anchor=\"end\" font-family=\"Times New Roman\" font-size=\"16\">$(round(y_value; digits = 3))</text>")
        end

        # X-axis labels
        for (i, x_val) in enumerate(x_values)
            x_pixel = scaled(x_val, x_min, x_max, left, left + plot_width)
            println(io, "<text x=\"$x_pixel\" y=\"$(top + plot_height + 24)\" text-anchor=\"middle\" font-family=\"Times New Roman\" font-size=\"16\">$(x_val)</text>")
        end

        # Plot lines with markers
        for (i, x_val) in enumerate(x_values)
            x_pixel = scaled(x_val, x_min, x_max, left, left + plot_width)

            # Official PID
            if isfinite(official_rmse[i])
                y_pixel_off = scaled(official_rmse[i], y_min, y_max, top + plot_height, top)
                println(io, "<circle cx=\"$x_pixel\" cy=\"$y_pixel_off\" r=\"5\" fill=\"$(COLORS[1])\"/>")
                if i < length(x_values)
                    x_next = scaled(x_values[i+1], x_min, x_max, left, left + plot_width)
                    y_next_off = scaled(official_rmse[i+1], y_min, y_max, top + plot_height, top)
                    println(io, "<line x1=\"$x_pixel\" y1=\"$y_pixel_off\" x2=\"$x_next\" y2=\"$y_next_off\" stroke=\"$(COLORS[1])\" stroke-width=\"2.0\"/>")
                end
            end

            # px4ctrl
            if isfinite(px4ctrl_rmse[i])
                y_pixel_px = scaled(px4ctrl_rmse[i], y_min, y_max, top + plot_height, top)
                println(io, "<circle cx=\"$x_pixel\" cy=\"$y_pixel_px\" r=\"5\" fill=\"$(COLORS[2])\"/>")
                if i < length(x_values)
                    x_next = scaled(x_values[i+1], x_min, x_max, left, left + plot_width)
                    y_next_px = scaled(px4ctrl_rmse[i+1], y_min, y_max, top + plot_height, top)
                    println(io, "<line x1=\"$x_pixel\" y1=\"$y_pixel_px\" x2=\"$x_next\" y2=\"$y_next_px\" stroke=\"$(COLORS[2])\" stroke-width=\"2.0\"/>")
                end
            end
        end

        # Axis labels
        println(io, "<text x=\"$(left + plot_width / 2)\" y=\"$(height - 20)\" text-anchor=\"middle\" font-family=\"Times New Roman\" font-size=\"18\">$(svg_escape(x_label))</text>")
        println(io, "<text x=\"30\" y=\"$(top + plot_height / 2)\" transform=\"rotate(-90 30 $(top + plot_height / 2))\" text-anchor=\"middle\" font-family=\"Times New Roman\" font-size=\"18\">Position RMSE (m)</text>")

        # Legend
        legend_y = height - 62
        println(io, "<line x1=\"$left\" y1=\"$legend_y\" x2=\"$(left + 24)\" y2=\"$legend_y\" stroke=\"$(COLORS[1])\" stroke-width=\"2.0\"/>")
        println(io, "<circle cx=\"$(left + 12)\" cy=\"$legend_y\" r=\"5\" fill=\"$(COLORS[1])\"/>")
        println(io, "<text x=\"$(left + 30)\" y=\"$(legend_y + 4)\" font-family=\"Times New Roman\" font-size=\"14\">Official PID</text>")
        println(io, "<line x1=\"$(left + 180)\" y1=\"$legend_y\" x2=\"$(left + 204)\" y2=\"$legend_y\" stroke=\"$(COLORS[2])\" stroke-width=\"2.0\"/>")
        println(io, "<circle cx=\"$(left + 192)\" cy=\"$legend_y\" r=\"5\" fill=\"$(COLORS[2])\"/>")
        println(io, "<text x=\"$(left + 210)\" y=\"$(legend_y + 4)\" font-family=\"Times New Roman\" font-size=\"14\">px4ctrl</text>")

        println(io, "</svg>")
    end
end

function process_wind_sensitivity(wind_dir::String, output_dir::String)
    wind_levels = [20, 40, 60, 80]
    official_rmse = Float64[]
    px4ctrl_rmse = Float64[]

    for level in wind_levels
        official_path = joinpath(wind_dir, "official_pid", "sensitivity_wind_x_$(lpad(level, 3, '0'))N_v1", "raw", "result.csv")
        px4ctrl_path = joinpath(wind_dir, "px4ctrl", "sensitivity_wind_x_$(lpad(level, 3, '0'))N_v1", "raw", "result.csv")

        official_data = load_sensitivity_csv(official_path)
        px4ctrl_data = load_sensitivity_csv(px4ctrl_path)

        push!(official_rmse, isnothing(official_data) ? NaN : compute_position_rmse(official_data))
        push!(px4ctrl_rmse, isnothing(px4ctrl_data) ? NaN : compute_position_rmse(px4ctrl_data))
    end

    output_file = joinpath(output_dir, "wind_disturbance_sensitivity.svg")
    write_sensitivity_curve(output_file, wind_levels, official_rmse, px4ctrl_rmse, "Wind Disturbance Force (N)", "Wind Disturbance Sensitivity")
    println("Written: $output_file")
end

function process_param_sensitivity(param_dir::String, output_dir::String)
    param_scales = [110, 120, 130, 140]
    official_rmse = Float64[]
    px4ctrl_rmse = Float64[]

    for scale in param_scales
        official_path = joinpath(param_dir, "official_pid", "sensitivity_parameter_scale_$(scale)_v1", "raw", "result.csv")
        px4ctrl_path = joinpath(param_dir, "px4ctrl", "sensitivity_parameter_scale_$(scale)_v1", "raw", "result.csv")

        official_data = load_sensitivity_csv(official_path)
        px4ctrl_data = load_sensitivity_csv(px4ctrl_path)

        push!(official_rmse, isnothing(official_data) ? NaN : compute_position_rmse(official_data))
        push!(px4ctrl_rmse, isnothing(px4ctrl_data) ? NaN : compute_position_rmse(px4ctrl_data))
    end

    output_file = joinpath(output_dir, "parameter_mismatch_sensitivity.svg")
    write_sensitivity_curve(output_file, param_scales, official_rmse, px4ctrl_rmse, "Parameter Scale (%)", "Parameter Mismatch Sensitivity")
    println("Written: $output_file")
end

function process_motor_sensitivity(motor_dir::String, output_dir::String)
    motor_efficiencies = [55, 65, 75, 85]
    official_rmse = Float64[]
    px4ctrl_rmse = Float64[]

    for eff in motor_efficiencies
        official_path = joinpath(motor_dir, "official_pid", "sensitivity_motor_efficiency_$(lpad(eff, 3, '0'))_v1", "raw", "result.csv")
        px4ctrl_path = joinpath(motor_dir, "px4ctrl", "sensitivity_motor_efficiency_$(lpad(eff, 3, '0'))_v1", "raw", "result.csv")

        official_data = load_sensitivity_csv(official_path)
        px4ctrl_data = load_sensitivity_csv(px4ctrl_path)

        push!(official_rmse, isnothing(official_data) ? NaN : compute_position_rmse(official_data))
        push!(px4ctrl_rmse, isnothing(px4ctrl_data) ? NaN : compute_position_rmse(px4ctrl_data))
    end

    output_file = joinpath(output_dir, "motor_efficiency_sensitivity.svg")
    write_sensitivity_curve(output_file, motor_efficiencies, official_rmse, px4ctrl_rmse, "Motor Efficiency (%)", "Motor Efficiency Sensitivity")
    println("Written: $output_file")
end

function main(args = ARGS)
    wind_dir = ""
    param_dir = ""
    motor_dir = ""
    output_dir = ""

    index = 1
    while index <= length(args)
        if args[index] == "--wind"
            index + 1 <= length(args) || error("--wind requires a directory")
            wind_dir = args[index + 1]
            index += 2
        elseif args[index] == "--param"
            index + 1 <= length(args) || error("--param requires a directory")
            param_dir = args[index + 1]
            index += 2
        elseif args[index] == "--motor"
            index + 1 <= length(args) || error("--motor requires a directory")
            motor_dir = args[index + 1]
            index += 2
        elseif args[index] == "--output"
            index + 1 <= length(args) || error("--output requires a directory")
            output_dir = args[index + 1]
            index += 2
        else
            error("Unknown option: $(args[index])")
        end
    end

    isempty(output_dir) && error("--output is required")
    mkpath(output_dir)

    !isempty(wind_dir) && process_wind_sensitivity(wind_dir, output_dir)
    !isempty(param_dir) && process_param_sensitivity(param_dir, output_dir)
    !isempty(motor_dir) && process_motor_sensitivity(motor_dir, output_dir)

    println("Sensitivity analysis figures complete: $output_dir")
    return 0
end

if abspath(PROGRAM_FILE) == @__FILE__
    exit(main())
end
