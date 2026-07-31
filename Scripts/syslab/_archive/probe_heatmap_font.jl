# 探针：TyPlot heatmap 的 yvalues 标签字体能否控制（决定两张热图是修还是转表）
using TyPlot, TyBase

include(raw"C:\Users\HP\Desktop\MoSim\Scripts\syslab\typlot_figure_style.jl")

const OUTH = raw"C:\Users\HP\Desktop\MoSim\.tmp\typlot_probe_heatmap"
mkpath(OUTH)

ids = ["official_pid", "adaptive_backstepping", "nonsingular_terminal_smc",
       "explicit_gain_scheduled_mpc", "dfbc_high_order_body_rate",
       "passivity_based_control", "feedback_linearization", "robust_mpc"]
vals = [0.0897, 0.2104, 0.3080, 1.4530, 1.8619, 2.0460, 2.5550, 2.7052]

fig(7, 9)
heatmap(reshape(vals, length(vals), 1),
        xvalues=["ClimbPath50s RMSE (m)"], yvalues=ids)
axes_font()
save_fig(joinpath(OUTH, "h1_after_axesfont.png"))

println("✓ heatmap 字体探针完成")
