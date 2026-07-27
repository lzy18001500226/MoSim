#!/usr/bin/env julia

# Generate the required Syslab controller-comparison table and figures from
# formal MWORKS CSV exports. Base Julia is used deliberately so the script is
# runnable in a clean Syslab session without relying on an unverified package.
#
# Usage:
#   julia Scripts/syslab/compare_controllers.jl \
#     --climb official_pid=Results/.../climb.csv cascade_pid=Results/.../climb.csv \
#     --step official_pid=Results/.../step.csv cascade_pid=Results/.../step.csv \
#     --output-dir Results/control_platform/seven_scenario_ab/syslab_comparison
#   julia Scripts/syslab/compare_controllers.jl --self-test

include(joinpath(@__DIR__, "..", "results", "calc_metrics.jl"))

const COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#8c564b", "#e377c2"]

function svg_escape(value)
    return replace(string(value), "&" => "&amp;", "<" => "&lt;", ">" => "&gt;", "\"" => "&quot;")
end

function parse_pair(value::AbstractString)
    separator = findfirst(==('='), value)
    separator === nothing && error("Expected controller_id=csv_path, got: $value")
    controller_id = strip(value[1:prevind(value, separator)])
    path = strip(value[nextind(value, separator):end])
    isempty(controller_id) && error("Missing controller ID in: $value")
    isempty(path) && error("Missing CSV path in: $value")
    return controller_id, path
end

function parse_compare_args(args)
    length(args) == 1 && args[1] == "--self-test" && return Dict("self_test" => true)
    climb = Pair{String, String}[]
    step = Pair{String, String}[]
    output_dir = ""
    index = 1
    while index <= length(args)
        option = args[index]
        if option == "--climb" || option == "--step"
            target = option == "--climb" ? climb : step
            index += 1
            start_count = length(target)
            while index <= length(args) && !startswith(args[index], "--")
                controller_id, path = parse_pair(args[index])
                push!(target, controller_id => path)
                index += 1
            end
            length(target) > start_count || error("$option requires at least one controller_id=csv_path value")
            continue
        elseif option == "--output-dir"
            index + 1 <= length(args) || error("--output-dir requires a path")
            output_dir = args[index + 1]
            index += 2
            continue
        else
            error("Unknown option: $option")
        end
    end
    isempty(climb) && error("At least one --climb CSV is required")
    isempty(step) && error("At least one --step CSV is required")
    isempty(output_dir) && error("--output-dir is required")
    return Dict("self_test" => false, "climb" => climb, "step" => step, "output_dir" => output_dir)
end

function load_series(controller_id::String, path::String, scene_id::String)
    isfile(path) || error("CSV does not exist: $path")
    _, columns = read_csv(path)
    metrics = compute_metrics(columns; raw_file = path, scene_id = scene_id, controller_id = controller_id)
    return Dict("controller_id" => controller_id, "path" => path, "columns" => columns, "metrics" => metrics)
end

function sample_indices(length_value::Int, maximum_points::Int = 400)
    length_value <= maximum_points && return collect(1:length_value)
    stride = max(1, ceil(Int, length_value / maximum_points))
    indices = collect(1:stride:length_value)
    indices[end] == length_value || push!(indices, length_value)
    return indices
end

function scaled(value, lower, upper, pixel_lower, pixel_upper)
    upper <= lower + 1e-12 && return (pixel_lower + pixel_upper) / 2
    return pixel_lower + (value - lower) * (pixel_upper - pixel_lower) / (upper - lower)
end

function polyline_points(time, values, x_min, x_max, y_min, y_max, x0, y0, width, height)
    points = String[]
    for index in sample_indices(length(time))
        isfinite(time[index]) && isfinite(values[index]) || continue
        px = scaled(time[index], x_min, x_max, x0, x0 + width)
        py = scaled(values[index], y_min, y_max, y0 + height, y0)
        push!(points, "$(round(px; digits = 2)),$(round(py; digits = 2))")
    end
    return join(points, " ")
end

function write_climb_rmse_bar(path::String, climb_rows)
    width, height = 980, 560
    left, right, top, bottom = 90.0, 40.0, 55.0, 115.0
    labels = [row["controller_id"] for row in climb_rows]
    values = [Float64(row["metrics"]["position_rmse_m"]) for row in climb_rows]
    valid_values = [value for value in values if isfinite(value)]
    maximum_value = isempty(valid_values) ? 1.0 : maximum(valid_values)
    y_max = maximum_value <= 0 ? 1.0 : maximum_value * 1.15
    plot_width = width - left - right
    plot_height = height - top - bottom
    bar_width = 0.65 * plot_width / max(1, length(labels))

    mkpath(dirname(path))
    open(path, "w") do io
        println(io, "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"$width\" height=\"$height\" viewBox=\"0 0 $width $height\">")
        println(io, "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>")
        println(io, "<text x=\"$(width / 2)\" y=\"30\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"20\">ClimbPath Position RMSE Comparison</text>")
        println(io, "<line x1=\"$left\" y1=\"$(height - bottom)\" x2=\"$(width - right)\" y2=\"$(height - bottom)\" stroke=\"#222\"/>")
        println(io, "<line x1=\"$left\" y1=\"$top\" x2=\"$left\" y2=\"$(height - bottom)\" stroke=\"#222\"/>")
        for tick in 0:5
            value = y_max * tick / 5
            y = scaled(value, 0.0, y_max, height - bottom, top)
            println(io, "<line x1=\"$left\" y1=\"$y\" x2=\"$(width - right)\" y2=\"$y\" stroke=\"#dddddd\"/>")
            println(io, "<text x=\"$(left - 10)\" y=\"$(y + 4)\" text-anchor=\"end\" font-family=\"Arial\" font-size=\"12\">$(round(value; digits = 3))</text>")
        end
        for (index, (label, value)) in enumerate(zip(labels, values))
            center_x = left + (index - 0.5) * plot_width / length(labels)
            bar_height = isfinite(value) ? value / y_max * plot_height : 0.0
            y = height - bottom - bar_height
            color = COLORS[mod1(index, length(COLORS))]
            println(io, "<rect x=\"$(center_x - bar_width / 2)\" y=\"$y\" width=\"$bar_width\" height=\"$bar_height\" fill=\"$color\"/>")
            rendered = isfinite(value) ? string(round(value; digits = 4)) : "n/a"
            println(io, "<text x=\"$center_x\" y=\"$(y - 7)\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"12\">$rendered</text>")
            println(io, "<text x=\"$center_x\" y=\"$(height - bottom + 20)\" text-anchor=\"end\" transform=\"rotate(-35 $center_x $(height - bottom + 20))\" font-family=\"Arial\" font-size=\"12\">$(svg_escape(label))</text>")
        end
        println(io, "<text x=\"20\" y=\"$(height / 2)\" transform=\"rotate(-90 20 $(height / 2))\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"14\">Position RMSE (m)</text>")
        println(io, "</svg>")
    end
end

function write_step_response_overlay(path::String, step_rows)
    width, height = 1080, 720
    left, right, top, bottom = 85.0, 40.0, 60.0, 80.0
    gap = 60.0
    panel_height = (height - top - bottom - gap) / 2
    all_time = vcat([row["columns"]["time"] for row in step_rows]...)
    all_x = vcat([row["columns"]["x"] for row in step_rows]...)
    all_y = vcat([row["columns"]["y"] for row in step_rows]...)
    ref_columns = step_rows[1]["columns"]
    all_x = vcat(all_x, ref_columns["x_ref"])
    all_y = vcat(all_y, ref_columns["y_ref"])
    x_min, x_max = minimum(all_time), maximum(all_time)
    x_min == x_max && (x_max = x_min + 1.0)
    y_x_min, y_x_max = minimum(all_x), maximum(all_x)
    y_y_min, y_y_max = minimum(all_y), maximum(all_y)
    y_x_min == y_x_max && (y_x_max = y_x_min + 1.0)
    y_y_min == y_y_max && (y_y_max = y_y_min + 1.0)
    plot_width = width - left - right
    y_panels = [(top, "X position (m)", "x", "x_ref", y_x_min, y_x_max), (top + panel_height + gap, "Y position (m)", "y", "y_ref", y_y_min, y_y_max)]

    mkpath(dirname(path))
    open(path, "w") do io
        println(io, "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"$width\" height=\"$height\" viewBox=\"0 0 $width $height\">")
        println(io, "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>")
        println(io, "<text x=\"$(width / 2)\" y=\"30\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"20\">Step Response Overlay (XY)</text>")
        for (panel_index, (y0, y_label, response_key, reference_key, y_min, y_max)) in enumerate(y_panels)
            println(io, "<rect x=\"$left\" y=\"$y0\" width=\"$plot_width\" height=\"$panel_height\" fill=\"none\" stroke=\"#222\"/>")
            for tick in 0:4
                y_value = y_min + (y_max - y_min) * tick / 4
                y_pixel = scaled(y_value, y_min, y_max, y0 + panel_height, y0)
                println(io, "<line x1=\"$left\" y1=\"$y_pixel\" x2=\"$(width - right)\" y2=\"$y_pixel\" stroke=\"#eeeeee\"/>")
                println(io, "<text x=\"$(left - 8)\" y=\"$(y_pixel + 4)\" text-anchor=\"end\" font-family=\"Arial\" font-size=\"11\">$(round(y_value; digits = 2))</text>")
            end
            reference_points = polyline_points(ref_columns["time"], ref_columns[reference_key], x_min, x_max, y_min, y_max, left, y0, plot_width, panel_height)
            println(io, "<polyline points=\"$reference_points\" fill=\"none\" stroke=\"#111111\" stroke-width=\"2\" stroke-dasharray=\"6,4\"/>")
            for (index, row) in enumerate(step_rows)
                columns = row["columns"]
                points = polyline_points(columns["time"], columns[response_key], x_min, x_max, y_min, y_max, left, y0, plot_width, panel_height)
                color = COLORS[mod1(index, length(COLORS))]
                println(io, "<polyline points=\"$points\" fill=\"none\" stroke=\"$color\" stroke-width=\"2\"/>")
            end
            println(io, "<text x=\"20\" y=\"$(y0 + panel_height / 2)\" transform=\"rotate(-90 20 $(y0 + panel_height / 2))\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"13\">$y_label</text>")
            if panel_index == length(y_panels)
                println(io, "<text x=\"$(left + plot_width / 2)\" y=\"$(height - 25)\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"13\">Time (s)</text>")
            end
        end
        legend_x, legend_y = left, height - 50
        println(io, "<line x1=\"$legend_x\" y1=\"$legend_y\" x2=\"$(legend_x + 24)\" y2=\"$legend_y\" stroke=\"#111111\" stroke-width=\"2\" stroke-dasharray=\"6,4\"/>")
        println(io, "<text x=\"$(legend_x + 30)\" y=\"$(legend_y + 4)\" font-family=\"Arial\" font-size=\"12\">reference</text>")
        for (index, row) in enumerate(step_rows)
            x = legend_x + 110 * index
            color = COLORS[mod1(index, length(COLORS))]
            controller_label = svg_escape(row["controller_id"])
            println(io, "<line x1=\"$x\" y1=\"$legend_y\" x2=\"$(x + 24)\" y2=\"$legend_y\" stroke=\"$color\" stroke-width=\"2\"/>")
            println(io, "<text x=\"$(x + 30)\" y=\"$(legend_y + 4)\" font-family=\"Arial\" font-size=\"12\">$controller_label</text>")
        end
        println(io, "</svg>")
    end
end

function write_comparison_table(path::String, climb_rows, step_rows)
    step_by_id = Dict(row["controller_id"] => row for row in step_rows)
    controller_ids = sort(unique(vcat([row["controller_id"] for row in climb_rows], [row["controller_id"] for row in step_rows])))
    climb_by_id = Dict(row["controller_id"] => row for row in climb_rows)
    open(path, "w") do io
        println(io, "controller_id,climbpath_position_rmse_m,step_position_rmse_m,step_overshoot_percent_x,step_overshoot_percent_y,step_settling_time_s,step_steady_state_error_m")
        for controller_id in controller_ids
            climb_metrics = haskey(climb_by_id, controller_id) ? climb_by_id[controller_id]["metrics"] : Dict{String, Any}()
            step_metrics = haskey(step_by_id, controller_id) ? step_by_id[controller_id]["metrics"] : Dict{String, Any}()
            values = [
                get(climb_metrics, "position_rmse_m", NaN),
                get(step_metrics, "position_rmse_m", NaN),
                get(step_metrics, "overshoot_percent_x", NaN),
                get(step_metrics, "overshoot_percent_y", NaN),
                get(step_metrics, "settling_time_s", NaN),
                get(step_metrics, "steady_state_error_m", NaN),
            ]
            rendered = [value isa Number && isfinite(value) ? string(value) : "" for value in values]
            println(io, "$(controller_id),$(join(rendered, ','))")
        end
    end
end

function write_manifest(path::String, climb_rows, step_rows, output_dir::String)
    manifest = Dict{String, Any}(
        "schema" => "mosim.syslab_controller_comparison.v1",
        "status" => "generated_from_csv",
        "climb_controller_count" => length(climb_rows),
        "step_controller_count" => length(step_rows),
        "output_dir" => output_dir,
        "climb_rmse_figure" => joinpath(output_dir, "figures", "climbpath_rmse_bar.svg"),
        "step_overlay_figure" => joinpath(output_dir, "figures", "step_response_overlay.svg"),
        "summary_table" => joinpath(output_dir, "controller_comparison_metrics.csv"),
    )
    write_json(path, manifest)
end

function run_comparison(climb_pairs, step_pairs, output_dir::String)
    climb_rows = [load_series(String(pair.first), String(pair.second), "climb_path") for pair in climb_pairs]
    step_rows = [load_series(String(pair.first), String(pair.second), "step_response") for pair in step_pairs]
    figures_dir = joinpath(output_dir, "figures")
    mkpath(figures_dir)
    write_climb_rmse_bar(joinpath(figures_dir, "climbpath_rmse_bar.svg"), climb_rows)
    write_step_response_overlay(joinpath(figures_dir, "step_response_overlay.svg"), step_rows)
    write_comparison_table(joinpath(output_dir, "controller_comparison_metrics.csv"), climb_rows, step_rows)
    write_manifest(joinpath(output_dir, "COMPARE_CONTROLLERS_MANIFEST.json"), climb_rows, step_rows, output_dir)
    return Dict(
        "climb_rows" => climb_rows,
        "step_rows" => step_rows,
        "output_dir" => output_dir,
    )
end

function compare_self_test()
    root = joinpath(pwd(), ".tmp", "compare_controllers_jl_self_test")
    isdir(root) && rm(root; recursive = true, force = true)
    try
        mkpath(root)
        raw = joinpath(root, "step_response.csv")
        write_self_test_csv(raw)
        output_dir = joinpath(root, "comparison")
        run_comparison(["official_pid" => raw, "cascade_pid" => raw], ["official_pid" => raw, "cascade_pid" => raw], output_dir)
        for artifact in (
            joinpath(output_dir, "controller_comparison_metrics.csv"),
            joinpath(output_dir, "COMPARE_CONTROLLERS_MANIFEST.json"),
            joinpath(output_dir, "figures", "climbpath_rmse_bar.svg"),
            joinpath(output_dir, "figures", "step_response_overlay.svg"),
        )
            isfile(artifact) || error("self-test did not create: $artifact")
        end
        println("[OK] compare_controllers.jl self-test")
        return 0
    finally
        isdir(root) && rm(root; recursive = true, force = true)
    end
end

function compare_main(args = ARGS)
    options = parse_compare_args(args)
    options["self_test"] && return compare_self_test()
    output_dir = options["output_dir"]
    run_comparison(options["climb"], options["step"], output_dir)
    println("Syslab comparison written: $output_dir")
    return 0
end

if abspath(PROGRAM_FILE) == @__FILE__
    exit(compare_main())
end
