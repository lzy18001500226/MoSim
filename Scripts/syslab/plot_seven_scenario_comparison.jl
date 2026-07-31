# 七场景性能对比：Official PID vs px4ctrl
# 注：官方数据结构只有ClimbPath场景，暂时使用该场景数据进行验证

using TyPlot
using JSON

# 读取G2状态文件
status_path = "Results/control_platform/phase2_full_48_climbpath/G2_STATUS.json"
data = JSON.parsefile(status_path)

# 提取所有通过的控制器数据
passed_controllers = filter(row -> row["status"] == "pass", data["rows"])

println("找到 $(length(passed_controllers)) 个通过的控制器")

# 提取official_pid和px4ctrl数据
official_pid = findfirst(r -> r["controller_id"] == "official_pid", passed_controllers)
px4ctrl = findfirst(r -> r["controller_id"] == "px4ctrl", passed_controllers)

if isnothing(official_pid)
    println("警告：official_pid在通过列表中未找到，检查失败列表")
    all_rows = data["rows"]
    official_pid_row = findfirst(r -> r["controller_id"] == "official_pid", all_rows)
    if !isnothing(official_pid_row)
        println("official_pid状态：", all_rows[official_pid_row]["status"])
    end
else
    official_rmse = passed_controllers[official_pid]["position_rmse_m"]
    px4ctrl_rmse = passed_controllers[px4ctrl]["position_rmse_m"]

    official_terminal = passed_controllers[official_pid]["terminal_position_error_norm_m"]
    px4ctrl_terminal = passed_controllers[px4ctrl]["terminal_position_error_norm_m"]

    println("Official PID - RMSE: $official_rmse, Terminal: $official_terminal")
    println("px4ctrl - RMSE: $px4ctrl_rmse, Terminal: $px4ctrl_terminal")

    # 图1：ClimbPath性能对比（简化版）
    figure()
    x = [1, 2]
    width = 0.35
    bar(x .- width/2, [official_rmse, px4ctrl_rmse], width, label="Position RMSE")
    bar(x .+ width/2, [official_terminal, px4ctrl_terminal], width, label="Terminal Error")
    xticks(x)
    xticklabels(["Official PID", "px4ctrl"])
    ylabel("误差 (m)")
    title("ClimbPath场景性能对比")
    legend()
    grid(true)
    ax = gca()
    exportgraphics(ax, "Docs/报告/figures/第10章/climbpath_comparison.png", resolution=300)

    println("✓ ClimbPath对比图生成完成")
    println("  - climbpath_comparison.png")
end

println("\n注：当前G2数据只包含ClimbPath场景，七场景数据需要从其他批次获取")
