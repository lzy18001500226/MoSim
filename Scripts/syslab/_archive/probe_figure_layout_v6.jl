# v6 探针：修雷达 theta=0° 标签被画布右边缘裁切 + 标题压住 theta=90° 标签
using TyPlot, TyBase

include(raw"C:\Users\HP\Desktop\MoSim\Scripts\syslab\typlot_figure_style.jl")

const OUT = raw"C:\Users\HP\Desktop\MoSim\.tmp\typlot_probe_v6"
mkpath(OUT)

DIMS = ["Tracking Accuracy", "Terminal Convergence", "Control Energy", "Peak Deviation"]
sc   = [0.82, 0.64, 0.71, 0.55]

# ---- 方案A：theta 偏移 45°，四个标签落在四个对角，远离画布上下左右边缘 ----
ANG_A = collect(0:2π/4:2π-0.01) .+ π/4
fig(9, 9)
polarplot([ANG_A; ANG_A[1]], [sc; sc[1]], "-o", linewidth=2.5)
rlim([0, 1])
ticklab_theta(rad2deg.(ANG_A), DIMS)
styled(title("Sliding Mode (n = 6)"))
save_fig(joinpath(OUT, "pA_radar_offset45_9x9.png"))

# ---- 方案B：不偏移，缩小极坐标轴区留出四周边距 ----
ANG_B = collect(0:2π/4:2π-0.01)
fig(9, 9)
polarplot([ANG_B; ANG_B[1]], [sc; sc[1]], "-o", linewidth=2.5)
rlim([0, 1])
ticklab_theta(rad2deg.(ANG_B), DIMS)
plt_set(gca(), "Position", [0.16, 0.14, 0.68, 0.68])
styled(title("Sliding Mode (n = 6)"))
save_fig(joinpath(OUT, "pB_radar_shrink_9x9.png"))

println("✓ v6 完成")
