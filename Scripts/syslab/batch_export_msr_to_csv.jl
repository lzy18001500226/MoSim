#!/usr/bin/env julia
# Batch export MSR to CSV for 28 passed controllers
# Run in MWORKS Syslab environment

# 28个G3通过控制器
PASSED_CONTROLLERS = [
    "adaptive_backstepping",
    "adaptive_smc",
    "backstepping_baseline",
    "dfbc_basic",
    "dfbc_high_order_body_rate",
    "dfbc_high_order",
    "dfbc_smooth_robust_body_rate",
    "dfbc_smooth_robust",
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

BASE_PATH = raw"C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath"

# 导出的CSV列（根据calc_metrics.jl的需求）
EXPORT_COLUMNS = [
    "time", "x", "y", "z", "x_ref", "y_ref", "z_ref",
    "vx", "vy", "vz", "roll", "pitch", "yaw",
    "u1", "u2", "u3", "u4"
]

function find_latest_msr(controller_id::String)
    base_dir = joinpath(BASE_PATH, controller_id)
    !isdir(base_dir) && return nothing

    # 查找所有 native_result_g6_* 目录
    g6_dirs = filter(readdir(base_dir, join=true)) do path
        isdir(path) && startswith(basename(path), "native_result_g6_")
    end

    isempty(g6_dirs) && return nothing

    # 在每个g6目录中查找Result.msr
    msr_files = String[]
    for g6_dir in g6_dirs
        for (root, dirs, files) in walkdir(g6_dir)
            for file in files
                if file == "Result.msr"
                    push!(msr_files, joinpath(root, file))
                end
            end
        end
    end

    isempty(msr_files) && return nothing

    # 选择最新的
    return sort(msr_files, by=mtime, rev=true)[1]
end

function export_msr_to_csv(msr_path::String, csv_path::String)
    # 使用MWORKS Result类读取MSR并导出CSV
    try
        # 方法1：使用ModelingPy.Result (如果可用)
        # result = ModelingPy.Result(msr_path)
        # result.export_csv(csv_path, columns=EXPORT_COLUMNS)

        # 方法2：使用Syslab命令行工具（如果有）
        # run(`syslab --export-csv $msr_path --output $csv_path --columns $(join(EXPORT_COLUMNS, ","))`)

        # 方法3：手动读取MSR并写CSV
        println("  WARNING: Automatic MSR export not implemented")
        println("  Please manually export: $msr_path -> $csv_path")
        return false
    catch e
        println("  ERROR: $e")
        return false
    end
end

function main()
    success_count = 0
    fail_count = 0

    println("Starting MSR to CSV batch export...")
    println("=" ^ 60)

    for controller_id in PASSED_CONTROLLERS
        println("\nProcessing: $controller_id")

        # 1. 查找MSR文件
        msr_path = find_latest_msr(controller_id)
        if isnothing(msr_path)
            println("  ERROR: No MSR file found")
            fail_count += 1
            continue
        end
        println("  MSR: $msr_path")

        # 2. 准备输出路径
        output_dir = joinpath(BASE_PATH, controller_id, "raw")
        mkpath(output_dir)
        csv_path = joinpath(output_dir, "climbpath50s.csv")

        # 3. 导出CSV
        if export_msr_to_csv(msr_path, csv_path)
            println("  SUCCESS: $csv_path")
            success_count += 1
        else
            println("  FAILED: Auto-export not available")
            fail_count += 1
        end
    end

    println("\n" * "=" ^ 60)
    println("Export summary:")
    println("  Total: $(length(PASSED_CONTROLLERS))")
    println("  Success: $success_count")
    println("  Failed: $fail_count")

    if fail_count > 0
        println("\nNOTE: Auto-export failed. Manual export required.")
        println("See MSR_EXPORT_MANUAL_GUIDE.md for instructions.")
    end
end

main()
