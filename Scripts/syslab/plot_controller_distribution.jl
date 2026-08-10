# 控制器性能分布可视化（基于当前目录 48 条对账，30 条性能达标）
# 生成5张分布图：2个箱线图 + 2个直方图 + 1个排名柱状图
#
# 口径：数据源为当前 G3_CATALOG_48_CURRENT_STATUS.json 的 accepted index，
# status=="pass" 即当前 30 条性能达标（终端位置误差 < 5 m）。
# 不要改回历史 G3_STATUS.json；它是 28 条快照，只用于追溯。

using TyPlot
using Statistics

include(joinpath(@__DIR__, "typlot_figure_style.jl"))

# 输出根目录可覆盖：抽样审核时写临时目录
const OUTDIR = isdefined(Main, :DIST_OUTPUT_ROOT) ? Main.DIST_OUTPUT_ROOT :
               raw"C:\Users\HP\Desktop\MoSim\Docs\报告\figures\第10章"

const INDEX_PATH = raw"C:\Users\HP\Desktop\MoSim\.tmp\chapter10_typlot\accepted_controller_index.csv"

function read_index(path::String)
    isfile(path) || error("当前 accepted index 不存在，请先运行 build_chapter10_typlot_index.py: $path")
    lines = readlines(path)
    header = [strip(value) for value in split(lines[1], ',')]
    rows = Dict{String,String}[]
    for line in lines[2:end]
        isempty(strip(line)) && continue
        values = split(line, ',')
        length(values) == length(header) || error("accepted index 含有无法解析的行")
        push!(rows, Dict(header[i] => strip(String(values[i])) for i in eachindex(header)))
    end
    rows
end

num(row, key) = (value = get(row, key, ""); isempty(value) ? NaN : something(tryparse(Float64, value), NaN))

# 提取当前目录对账中的 30 条性能达标控制器数据
passed_controllers = read_index(INDEX_PATH)
println("成功读取 $(length(passed_controllers)) 条当前性能达标控制器数据（应为 30）")
@assert length(passed_controllers) == 30 "当前达标数应为 30，实际 $(length(passed_controllers))；检查 current catalog index"

# 收集指标数据
all_rmse = [num(r, "position_rmse_m") for r in passed_controllers]
all_terminal = [num(r, "terminal_position_error_m") for r in passed_controllers]
controller_names = [r["controller_id"] for r in passed_controllers]
@assert all(isfinite, all_rmse) "当前 accepted index 存在缺失 position_rmse_m"
@assert all(isfinite, all_terminal) "当前 accepted index 存在缺失 terminal_position_error_m"

# 排版标准由 typlot_figure_style.jl 统一提供：Times New Roman、无中文、无标题，
# 字号按画布宽度等比缩放（锚点为已过审的 9 in / 18 pt 标签 / 16 pt 刻度）。
# 导出尺寸只受 figure(figsize=) 控制，OuterPosition 对 exportgraphics 完全无效。
const N = length(passed_controllers)

const CV_BOX  = (6.0, 7.5)     # 单组箱线，窄高
const CV_HIST = (10.0, 6.0)    # 直方
const CV_RANK = (10.0, 11.3)   # 30 条排名：改横条，竖版 90° 旋转必堆叠

# 图1：Position RMSE箱线图
fig(CV_BOX...)
boxchart(ones(length(all_rmse)), all_rmse)
# 单组箱线的 x 刻度默认显示分组序号 "1.0"，无含义，替换为样本说明
ticklab_x([1], ["All Accepted"])
styled(ylabel("Position RMSE (m)"))
styled(xlabel("Performance-Accepted Controllers (n = $N)"))
grid("on")
save_fig(joinpath(OUTDIR, "controller_dist_rmse_box.png"))

# 图2：Terminal Error箱线图
fig(CV_BOX...)
boxchart(ones(length(all_terminal)), all_terminal)
ticklab_x([1], ["All Accepted"])
styled(ylabel("Terminal Position Error (m)"))
styled(xlabel("Performance-Accepted Controllers (n = $N)"))
grid("on")
save_fig(joinpath(OUTDIR, "controller_dist_terminal_box.png"))

# 图3：RMSE直方图
fig(CV_HIST...)
histogram(all_rmse, 10)
axes_font()
styled(xlabel("Position RMSE (m)"))
styled(ylabel("Controller Count"))
grid("on")
save_fig(joinpath(OUTDIR, "controller_dist_rmse_hist.png"))

# 图4：Terminal Error直方图
fig(CV_HIST...)
histogram(all_terminal, 10)
axes_font()
styled(xlabel("Terminal Position Error (m)"))
styled(ylabel("Controller Count"))
grid("on")
save_fig(joinpath(OUTDIR, "controller_dist_terminal_hist.png"))

# 图5：综合性能排名（按RMSE排序的柱状图）
sorted_indices = sortperm(all_rmse)
sorted_rmse = all_rmse[sorted_indices]
sorted_names = controller_names[sorted_indices]

# 竖版 + xtickangle(90) 在 30 条长控制器名下必堆叠，改横条（已过审：p2_ranking_barh）
fig(CV_RANK...)
y = 1:length(sorted_rmse)
barh(y, sorted_rmse)
ticklab_y(y, sorted_names)
styled(xlabel("Position RMSE (m)"))
styled(ylabel("Controller (ranked by RMSE, n = $N)"))
grid("on")
save_fig(joinpath(OUTDIR, "controller_ranking_rmse.png"))

println("✓ $(length(passed_controllers))条达标控制器分布图生成完成")
println("  - controller_dist_rmse_box.png")
println("  - controller_dist_terminal_box.png")
println("  - controller_dist_rmse_hist.png")
println("  - controller_dist_terminal_hist.png")
println("  - controller_ranking_rmse.png")

# 输出统计摘要
println("\n统计摘要:")
println("  RMSE - 最小: $(minimum(all_rmse)), 最大: $(maximum(all_rmse)), 均值: $(mean(all_rmse))")
println("  Terminal Error - 最小: $(minimum(all_terminal)), 最大: $(maximum(all_terminal)), 均值: $(mean(all_terminal))")
