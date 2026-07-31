# v5 探针：验证剩余两类未验证图 —— 极坐标雷达 theta 标签、28 条横向排名
using TyPlot, TyBase

include(raw"C:\Users\HP\Desktop\MoSim\Scripts\syslab\typlot_figure_style.jl")

const OUT = raw"C:\Users\HP\Desktop\MoSim\.tmp\typlot_probe_v5"
mkpath(OUT)

# ---- 读 28 条达标索引 ----
const IDX = raw"C:\Users\HP\Desktop\MoSim\.tmp\chapter10_typlot\accepted_controller_index.csv"
lines = readlines(IDX)
hdr = split(strip(lines[1]), ",")
col(name) = findfirst(==(name), hdr)
rows = [split(strip(l), ",") for l in lines[2:end] if !isempty(strip(l))]
ci, cr = col("controller_id"), col("position_rmse_m")
names_all = [r[ci] for r in rows]
rmse_all  = [parse(Float64, r[cr]) for r in rows]
println("读入 $(length(names_all)) 条")

# ===== 探针1：极坐标雷达 —— 4 维长标签，验证 ticklab_theta 顺序封死是否生效 =====
DIMS = ["Tracking Accuracy", "Terminal Convergence", "Control Energy", "Peak Deviation"]
ANG  = collect(0:2π/length(DIMS):2π-0.01)
sc   = [0.82, 0.64, 0.71, 0.55]

fig(9, 9)
polarplot([ANG; ANG[1]], [sc; sc[1]], "-o", linewidth=2.5)
rlim([0, 1])
ticklab_theta(rad2deg.(ANG), DIMS)
styled(title("Sliding Mode (n = 6)"))
save_fig(joinpath(OUT, "p1_radar_theta_9x9.png"))
println("  p1 雷达 label=$(lab_pt(9))pt tick=$(tik_pt(9))pt")

# ===== 探针2：28 条排名 —— 原竖版 90° 旋转必堆叠，改横条 =====
ord = sortperm(rmse_all)
sn, sv = names_all[ord], rmse_all[ord]
y = 1:length(sv)

fig(10, 11.3)
barh(y, sv)
ticklab_y(y, sn)
styled(xlabel("Position RMSE (m)"))
styled(ylabel("Controller (ranked, n = $(length(sv)))"))
grid("on")
save_fig(joinpath(OUT, "p2_ranking_barh_10x11p3.png"))
println("  p2 排名 label=$(lab_pt(10))pt tick=$(tik_pt(10))pt")

# ===== 探针3：多族系叠加雷达 + 轴外 legend =====
fig(9, 9)
FAMS = ["PID", "Linear Robust", "Nonlinear Adaptive", "Sliding Mode", "Optimization", "Geometric"]
DATA = [[0.55,0.48,0.61,0.42], [0.72,0.66,0.58,0.63], [0.68,0.71,0.52,0.59],
        [0.82,0.64,0.71,0.55], [0.76,0.80,0.44,0.70], [0.70,0.62,0.66,0.58]]
for (k, d) in enumerate(DATA)
    polarplot([ANG; ANG[1]], [d; d[1]], "-o", linewidth=2.2)
    k == 1 && hold("on")
end
rlim([0, 1])
ticklab_theta(rad2deg.(ANG), DIMS)
styled_legend([FAMS[k] * " (n=$k)" for k in eachindex(FAMS)]; loc="southoutside", ncol=3)
hold("off")
save_fig(joinpath(OUT, "p3_radar_combined_9x9.png"))
println("✓ v5 完成，输出 $OUT")
