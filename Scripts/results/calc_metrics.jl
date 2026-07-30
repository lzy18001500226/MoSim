#!/usr/bin/env julia

# Syslab/Julia metrics for the formal quadrotor result CSV contract.
#
# Usage:
#   julia Scripts/results/calc_metrics.jl <raw_csv> <metrics_json> [scene_id] [controller_id] [metric_context]
#   julia Scripts/results/calc_metrics.jl --self-test
#
# This file intentionally uses Base Julia only so it can run in a clean
# MWORKS.Syslab session without requiring an unverified package installation.

using Dates

const REQUIRED_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]
const MOTOR_COLUMNS = ["u1", "u2", "u3", "u4"]
const STEP_RESPONSE_TIME_S = 15.0
const STEP_RESPONSE_EVALUATION_END_S = 45.0
const STEP_RESPONSE_SETTLING_FRACTION = 0.05
const STEP_RESPONSE_STEADY_STATE_START_S = 40.0
const MOTOR_FAULT_TIME_S = 15.0

function parse_metric_context(raw::AbstractString)
    context = Dict{String, Float64}()
    isempty(strip(raw)) && return context
    for assignment in split(raw, ",")
        parts = split(assignment, "="; limit = 2)
        length(parts) == 2 || error("Invalid metric context entry: $assignment")
        key = strip(parts[1])
        isempty(key) && error("Metric context key must not be empty")
        value = parse(Float64, strip(parts[2]))
        isfinite(value) || error("Metric context values must be finite")
        context[key] = value
    end
    return context
end

function read_csv(path::AbstractString)
    lines = readlines(path)
    isempty(lines) && error("CSV is empty: $path")
    header = [String(strip(name)) for name in split(strip(lines[1]), ",")]
    missing = [name for name in REQUIRED_COLUMNS if !(name in header)]
    isempty(missing) || error("Missing required CSV columns: $(join(missing, ", "))")
    columns = Dict(name => Float64[] for name in header)
    for (offset, line) in enumerate(lines[2:end])
        line_no = offset + 1
        stripped = strip(line)
        isempty(stripped) && continue
        values = split(stripped, ",")
        length(values) == length(header) || error("CSV row $line_no has $(length(values)) values, expected $(length(header))")
        for (name, value) in zip(header, values)
            token = strip(value)
            push!(columns[name], isempty(token) ? NaN : parse(Float64, token))
        end
    end
    return header, columns
end

finite_values(values) = [Float64(value) for value in values if isfinite(value)]
mean_value(values) = isempty(values) ? NaN : sum(values) / length(values)
rmse(values) = begin
    finite = finite_values(values)
    isempty(finite) ? NaN : sqrt(mean_value(finite .^ 2))
end
max_or_nan(values) = begin
    finite = finite_values(values)
    isempty(finite) ? NaN : maximum(finite)
end

function trapezoid_integral(time, values)
    length(time) < 2 && return NaN
    length(values) < 2 && return NaN
    total = 0.0
    for index in 2:length(time)
        dt = time[index] - time[index - 1]
        isfinite(dt) && dt > 0 || continue
        total += 0.5 * dt * (values[index] + values[index - 1])
    end
    return total
end

function windowed(time, values, start_s::Real, end_s::Real)
    return [
        value
        for (current_time, value) in zip(time, values)
        if start_s - 1e-9 <= current_time <= end_s + 1e-9 && isfinite(value)
    ]
end

function value_before(time, values, event_time_s::Real)
    candidates = [
        value
        for (current_time, value) in zip(time, values)
        if current_time < event_time_s - 1e-9 && isfinite(value)
    ]
    return isempty(candidates) ? NaN : candidates[end]
end

function value_at_or_after(time, values, event_time_s::Real)
    for (current_time, value) in zip(time, values)
        if current_time >= event_time_s - 1e-9 && isfinite(value)
            return value
        end
    end
    return NaN
end

function signed_step_overshoot_percent(time, response, reference, step_time_s::Real, evaluation_end_s::Real)
    initial_ref = value_before(time, reference, step_time_s)
    target_ref = value_at_or_after(time, reference, step_time_s)
    amplitude = target_ref - initial_ref
    (!isfinite(amplitude) || abs(amplitude) < 1e-9) && return NaN
    direction = amplitude > 0 ? 1.0 : -1.0
    responses = windowed(time, response, step_time_s, evaluation_end_s)
    isempty(responses) && return NaN
    signed_peak = maximum(direction * (value - initial_ref) for value in responses)
    return 100.0 * max(0.0, signed_peak - abs(amplitude)) / abs(amplitude)
end

function persistent_step_settling_time(time, x, y, x_ref, y_ref, step_time_s::Real, evaluation_end_s::Real, fraction::Real)
    x_initial = value_before(time, x_ref, step_time_s)
    y_initial = value_before(time, y_ref, step_time_s)
    x_target = value_at_or_after(time, x_ref, step_time_s)
    y_target = value_at_or_after(time, y_ref, step_time_s)
    x_band = fraction * abs(x_target - x_initial)
    y_band = fraction * abs(y_target - y_initial)
    all(isfinite, (x_target, y_target, x_band, y_band)) || return NaN
    (x_band <= 0 || y_band <= 0) && return NaN
    indices = [
        index for index in eachindex(time)
        if step_time_s - 1e-9 <= time[index] <= evaluation_end_s + 1e-9
    ]
    isempty(indices) && return NaN
    for index in indices
        stable = true
        for later_index in indices
            later_index < index && continue
            if !isfinite(x[later_index]) || !isfinite(y[later_index]) ||
               abs(x[later_index] - x_target) > x_band + 1e-9 ||
               abs(y[later_index] - y_target) > y_band + 1e-9
                stable = false
                break
            end
        end
        stable && return time[index] - step_time_s
    end
    return NaN
end

function compute_step_response_metrics(time, x, y, x_ref, y_ref, position_error)
    return Dict{String, Any}(
        "overshoot_percent_x" => signed_step_overshoot_percent(time, x, x_ref, STEP_RESPONSE_TIME_S, STEP_RESPONSE_EVALUATION_END_S),
        "overshoot_percent_y" => signed_step_overshoot_percent(time, y, y_ref, STEP_RESPONSE_TIME_S, STEP_RESPONSE_EVALUATION_END_S),
        "settling_time_s" => persistent_step_settling_time(
            time, x, y, x_ref, y_ref, STEP_RESPONSE_TIME_S,
            STEP_RESPONSE_EVALUATION_END_S, STEP_RESPONSE_SETTLING_FRACTION,
        ),
        "steady_state_error_m" => mean_value(windowed(
            time, position_error, STEP_RESPONSE_STEADY_STATE_START_S,
            STEP_RESPONSE_EVALUATION_END_S,
        )),
        "step_response_time_s" => STEP_RESPONSE_TIME_S,
        "step_response_evaluation_end_s" => STEP_RESPONSE_EVALUATION_END_S,
        "step_response_settling_fraction" => STEP_RESPONSE_SETTLING_FRACTION,
    )
end

function compute_metrics(
    columns::Dict{String, Vector{Float64}};
    raw_file::AbstractString = "",
    scene_id::AbstractString = "",
    controller_id::AbstractString = "unknown",
    metric_context::Dict{String, Float64} = Dict{String, Float64}(),
)
    time = columns["time"]
    isempty(time) && error("Metrics input has no data rows: $raw_file")
    x = columns["x"]
    y = columns["y"]
    z = columns["z"]
    x_ref = columns["x_ref"]
    y_ref = columns["y_ref"]
    z_ref = columns["z_ref"]
    ex = x .- x_ref
    ey = y .- y_ref
    ez = z .- z_ref
    ep = sqrt.(ex .^ 2 .+ ey .^ 2 .+ ez .^ 2)
    xy_error = sqrt.(ex .^ 2 .+ ey .^ 2)
    duration_s = maximum(time) - minimum(time)
    final_window_start = maximum(time) - max(5.0, 0.2 * duration_s)
    final_error = windowed(time, ep, final_window_start, maximum(time))
    tail_error = windowed(time, ep, maximum(time) - 5.0, maximum(time))

    motor_cols = [name for name in MOTOR_COLUMNS if haskey(columns, name)]
    control_norm_sq = zeros(length(time))
    if !isempty(motor_cols)
        for name in motor_cols
            control_norm_sq .+= columns[name] .^ 2
        end
    end
    nan_count = sum(count(value -> !isfinite(value), values) for values in values(columns))

    metrics = Dict{String, Any}(
        "generated_at" => string(now()),
        "raw_file" => raw_file,
        "scene_id" => scene_id,
        "controller_id" => controller_id,
        "row_count" => length(time),
        "duration_s" => duration_s,
        "sample_rate_hz" => length(time) > 1 && duration_s > 0 ? (length(time) - 1) / duration_s : NaN,
        "position_rmse_m" => rmse(ep),
        "x_rmse_m" => rmse(ex),
        "y_rmse_m" => rmse(ey),
        "z_rmse_m" => rmse(ez),
        "xy_rmse_m" => rmse(xy_error),
        "max_position_error_m" => max_or_nan(ep),
        "steady_state_error_m" => mean_value(final_error),
        "tail_rmse_m" => rmse(tail_error),
        "terminal_position_error_m" => isempty(ep) ? NaN : ep[end],
        "control_energy" => isempty(motor_cols) ? NaN : trapezoid_integral(time, control_norm_sq),
        "nan_count" => nan_count,
        "valid" => length(time) > 10 && nan_count == 0,
        "overshoot_percent_x" => NaN,
        "overshoot_percent_y" => NaN,
        "step_response_time_s" => NaN,
        "step_response_evaluation_end_s" => NaN,
        "step_response_settling_fraction" => NaN,
        "disturbance_window_rmse_m" => NaN,
        "fault_start_s" => NaN,
        "pre_fault_rmse_m" => NaN,
        "post_fault_rmse_m" => NaN,
        "post_fault_peak_error_m" => NaN,
    )

    if scene_id == "step_response"
        merge!(metrics, compute_step_response_metrics(time, x, y, x_ref, y_ref, ep))
    end
    if scene_id == "wind_disturbance"
        disturbance_start_s = get(metric_context, "gust_start_s", 0.0)
        disturbance_duration_s = get(metric_context, "gust_duration_s", 50.0)
        disturbance_end_s = min(disturbance_start_s + disturbance_duration_s, maximum(time))
        metrics["disturbance_window_start_s"] = disturbance_start_s
        metrics["disturbance_window_end_s"] = disturbance_end_s
        metrics["disturbance_window_rmse_m"] = rmse(windowed(time, ep, disturbance_start_s, disturbance_end_s))
    end
    if scene_id == "motor_efficiency_fault"
        fault_start_s = get(metric_context, "fault_start_s", MOTOR_FAULT_TIME_S)
        pre_fault = [
            error for (current_time, error) in zip(time, ep)
            if current_time < fault_start_s - 1e-9 && isfinite(error)
        ]
        post_fault = windowed(time, ep, fault_start_s, maximum(time))
        metrics["fault_start_s"] = fault_start_s
        metrics["pre_fault_rmse_m"] = rmse(pre_fault)
        metrics["post_fault_rmse_m"] = rmse(post_fault)
        metrics["post_fault_peak_error_m"] = max_or_nan(post_fault)
    end
    return metrics
end

function json_escape(text)
    return replace(string(text), "\\" => "\\\\", "\"" => "\\\"", "\n" => "\\n")
end

function write_json(path::AbstractString, metrics::Dict{String, Any})
    mkpath(dirname(path))
    open(path, "w") do io
        println(io, "{")
        keys_sorted = sort(collect(keys(metrics)))
        for (index, key) in enumerate(keys_sorted)
            value = metrics[key]
            suffix = index == length(keys_sorted) ? "" : ","
            if value isa Bool
                rendered = value ? "true" : "false"
                println(io, "  \"$(json_escape(key))\": $rendered$suffix")
            elseif value isa Number
                if !isfinite(value)
                    println(io, "  \"$(json_escape(key))\": null$suffix")
                else
                    println(io, "  \"$(json_escape(key))\": $(value)$suffix")
                end
            else
                println(io, "  \"$(json_escape(key))\": \"$(json_escape(value))\"$suffix")
            end
        end
        println(io, "}")
    end
end

function write_metrics_csv(path::AbstractString, metrics::Dict{String, Any})
    open(path, "w") do io
        println(io, "metric,value")
        for key in sort(collect(keys(metrics)))
            value = metrics[key]
            rendered = value isa Number && !isfinite(value) ? "" : string(value)
            println(io, "$(key),$(replace(rendered, ',' => ';'))")
        end
    end
end

function write_self_test_csv(path::AbstractString)
    open(path, "w") do io
        println(io, "time,x,y,z,x_ref,y_ref,z_ref")
        for time_s in 0.0:1.0:45.0
            x_ref = time_s < STEP_RESPONSE_TIME_S ? 0.0 : 1.0
            y_ref = time_s < STEP_RESPONSE_TIME_S ? 0.0 : -1.0
            x = time_s < STEP_RESPONSE_TIME_S ? 0.0 : 1.0 - exp(-(time_s - STEP_RESPONSE_TIME_S) / 2.0)
            y = time_s < STEP_RESPONSE_TIME_S ? 0.0 : -1.0 + exp(-(time_s - STEP_RESPONSE_TIME_S) / 2.0)
            println(io, "$(time_s),$(x),$(y),2.0,$(x_ref),$(y_ref),2.0")
        end
    end
end

function self_test()
    root = joinpath(pwd(), ".tmp", "calc_metrics_jl_self_test")
    isdir(root) && rm(root; recursive = true, force = true)
    try
        mkpath(root)
        raw = joinpath(root, "step_response.csv")
        output = joinpath(root, "metrics.json")
        write_self_test_csv(raw)
        _, columns = read_csv(raw)
        metrics = compute_metrics(columns; raw_file = raw, scene_id = "step_response", controller_id = "self_test")
        write_json(output, metrics)
        metrics["overshoot_percent_x"] == 0.0 || error("self-test expected zero x overshoot")
        metrics["overshoot_percent_y"] == 0.0 || error("self-test expected zero y overshoot")
        isfinite(metrics["settling_time_s"]) || error("self-test expected a finite settling time")
        metrics["steady_state_error_m"] < 0.05 || error("self-test expected a small steady-state error")
        println("[OK] calc_metrics.jl self-test")
        return 0
    finally
        isdir(root) && rm(root; recursive = true, force = true)
    end
end

function main(args = ARGS)
    if length(args) == 1 && args[1] == "--self-test"
        return self_test()
    end
    if length(args) < 2
        println(stderr, "Usage: julia Scripts/results/calc_metrics.jl <raw_csv> <metrics_json> [scene_id] [controller_id] [metric_context]")
        println(stderr, "       metric_context format: gust_start_s=15,gust_duration_s=35")
        println(stderr, "       julia Scripts/results/calc_metrics.jl --self-test")
        return 2
    end
    raw_csv = args[1]
    metrics_json = args[2]
    scene_id = length(args) >= 3 ? args[3] : splitext(basename(raw_csv))[1]
    controller_id = length(args) >= 4 ? args[4] : "unknown"
    metric_context = length(args) >= 5 ? parse_metric_context(args[5]) : Dict{String, Float64}()
    _, columns = read_csv(raw_csv)
    metrics = compute_metrics(
        columns;
        raw_file = raw_csv,
        scene_id = scene_id,
        controller_id = controller_id,
        metric_context = metric_context,
    )
    write_json(metrics_json, metrics)
    write_metrics_csv(replace(metrics_json, r"\.json$" => ".csv"), metrics)
    println("Metrics written: $metrics_json")
    return 0
end

if abspath(PROGRAM_FILE) == @__FILE__
    exit(main())
end
