#!/usr/bin/env julia

# Minimal metrics script for project-standard quadrotor CSV files.
#
# Usage:
#   julia scripts/calc_metrics.jl results/raw/figure8.csv results/metrics/figure8.json
#   julia scripts/calc_metrics.jl --self-test

using Dates

function parse_args()
    if length(ARGS) == 1 && ARGS[1] == "--self-test"
        return "tests/fixtures/sample_tracking.csv", "results/test_reports/sample_tracking_metrics.json", "sample_tracking", "fixture"
    end
    if length(ARGS) < 2
        println(stderr, "Usage: julia scripts/calc_metrics.jl <raw_csv> <metrics_json> [scene_id] [controller_id]")
        println(stderr, "       julia scripts/calc_metrics.jl --self-test")
        exit(2)
    end
    raw_csv = ARGS[1]
    metrics_json = ARGS[2]
    scene_id = length(ARGS) >= 3 ? ARGS[3] : splitext(basename(raw_csv))[1]
    controller_id = length(ARGS) >= 4 ? ARGS[4] : "unknown"
    return raw_csv, metrics_json, scene_id, controller_id
end

function read_csv(path::AbstractString)
    lines = readlines(path)
    if isempty(lines)
        error("CSV is empty: $path")
    end
    header = split(strip(lines[1]), ",")
    columns = Dict(name => Float64[] for name in header)
    for line in lines[2:end]
        isempty(strip(line)) && continue
        values = split(strip(line), ",")
        for (name, value) in zip(header, values)
            push!(columns[name], parse(Float64, value))
        end
    end
    return header, columns
end

function require_columns(columns, names)
    missing = [name for name in names if !haskey(columns, name)]
    if !isempty(missing)
        error("Missing required CSV columns: $(join(missing, ", "))")
    end
end

mean_value(values) = isempty(values) ? NaN : sum(values) / length(values)
rmse(values) = isempty(values) ? NaN : sqrt(mean_value(values .^ 2))

function trapezoid_integral(time, values)
    if length(time) < 2 || length(values) < 2
        return NaN
    end
    total = 0.0
    for i in 2:length(time)
        dt = time[i] - time[i - 1]
        total += 0.5 * dt * (values[i] + values[i - 1])
    end
    return total
end

function json_escape(text)
    return replace(string(text), "\\" => "\\\\", "\"" => "\\\"")
end

function write_json(path, metrics)
    mkpath(dirname(path))
    open(path, "w") do io
        println(io, "{")
        keys_sorted = sort(collect(keys(metrics)))
        for (i, key) in enumerate(keys_sorted)
            value = metrics[key]
            suffix = i == length(keys_sorted) ? "" : ","
            if value isa Number
                if isnan(value) || isinf(value)
                    println(io, "  \"$(json_escape(key))\": null$suffix")
                else
                    println(io, "  \"$(json_escape(key))\": $(value)$suffix")
                end
            elseif value isa Bool
                println(io, "  \"$(json_escape(key))\": $(value ? "true" : "false")$suffix")
            else
                println(io, "  \"$(json_escape(key))\": \"$(json_escape(value))\"$suffix")
            end
        end
        println(io, "}")
    end
end

function main()
    raw_csv, metrics_json, scene_id, controller_id = parse_args()
    header, columns = read_csv(raw_csv)
    require_columns(columns, ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"])

    time = columns["time"]
    ex = columns["x"] .- columns["x_ref"]
    ey = columns["y"] .- columns["y_ref"]
    ez = columns["z"] .- columns["z_ref"]
    ep = sqrt.(ex .^ 2 .+ ey .^ 2 .+ ez .^ 2)

    final_window_start = isempty(time) ? 0.0 : maximum(time) - max(5.0, 0.2 * (maximum(time) - minimum(time)))
    final_idx = findall(t -> t >= final_window_start, time)
    final_error = isempty(final_idx) ? Float64[] : ep[final_idx]

    motor_cols = [name for name in ["u1", "u2", "u3", "u4"] if haskey(columns, name)]
    control_norm_sq = Float64[]
    saturation_samples = 0
    if !isempty(motor_cols)
        n = length(time)
        control_norm_sq = zeros(n)
        for name in motor_cols
            control_norm_sq .+= columns[name] .^ 2
            saturation_samples += count(u -> u <= 1e-9 || u >= 1.0 - 1e-9, columns[name])
        end
    end

    metrics = Dict{String, Any}()
    metrics["generated_at"] = string(now())
    metrics["raw_file"] = raw_csv
    metrics["scene_id"] = scene_id
    metrics["controller_id"] = controller_id
    metrics["row_count"] = length(time)
    metrics["duration_s"] = isempty(time) ? NaN : maximum(time) - minimum(time)
    metrics["position_rmse_m"] = rmse(ep)
    metrics["x_rmse_m"] = rmse(ex)
    metrics["y_rmse_m"] = rmse(ey)
    metrics["z_rmse_m"] = rmse(ez)
    metrics["max_position_error_m"] = isempty(ep) ? NaN : maximum(ep)
    metrics["steady_state_error_m"] = mean_value(final_error)
    metrics["control_energy"] = isempty(control_norm_sq) ? NaN : trapezoid_integral(time, control_norm_sq)
    metrics["saturation_ratio"] = isempty(motor_cols) ? NaN : saturation_samples / (length(time) * length(motor_cols))
    metrics["nan_count"] = sum(count(isnan, values) for values in values(columns))
    metrics["valid"] = metrics["row_count"] > 10 && metrics["nan_count"] == 0

    write_json(metrics_json, metrics)
    csv_path = replace(metrics_json, r"\.json$" => ".csv")
    open(csv_path, "w") do io
        println(io, "metric,value")
        for key in sort(collect(keys(metrics)))
            println(io, "$key,$(metrics[key])")
        end
    end
    println("Metrics written: $metrics_json")
    println("Metrics CSV: $csv_path")
end

main()
