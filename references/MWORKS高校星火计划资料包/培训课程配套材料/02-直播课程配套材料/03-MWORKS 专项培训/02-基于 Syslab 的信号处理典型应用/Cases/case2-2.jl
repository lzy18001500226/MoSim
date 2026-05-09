using TySignalProcessing
using TyPlot

t = 0:(1/2000):(2-1/2000)
q = chirp(t .- 2, 4, 1 / 2, 6, "quadratic", 100, "convex") .* exp.(-4 * (t .- 1) .^ 2)
figure(1)
plot(t, q)
up, lo = envelope(q)
# 上包络、下包络
hold("on")
plot(t, up, t, lo; linewidth=1.5)
legend(["q", "up", "lo"])
hold("off")
figure(2)
envelope(q; plotfig=true)
# 全包络图绘制
