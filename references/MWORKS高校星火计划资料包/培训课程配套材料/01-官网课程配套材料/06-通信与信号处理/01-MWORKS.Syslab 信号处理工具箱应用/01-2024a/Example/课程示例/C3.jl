using TyPlot
using TySignalProcessing
using TyMath
using  TyBase
# C3E1
x = [4 0 1 6 6
    2 0 2 7 7
    4 0 1 5 5
    2 0 5 6 6
    4 0 1 7 7
    2 0 2 5 5
    4 0 1 6 6
    2 1 5 7 2]
p = seqperiod(x)

# C3E2
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

# C3E3
using TySignalProcessing: TySignalProcessing
pkg_dir = pkgdir(TySignalProcessing)
source_path = pkg_dir * "/examples/Resource/pulseex.mat"
y = TyBase.load(source_path)
x = y["x"]
figure(1)
d, = dutycycle(x; plotfig=true)
# 占空比
figure(2)
p, = pulseperiod(x, t; plotfig=true)
# 脉冲周期
w, = pulsewidth(x, t)
# 脉宽

# C3E4
using TySignalProcessing: TySignalProcessing
pkg_dir = pkgdir(TySignalProcessing)
source_path1 = pkg_dir * "/examples/Resource/transitionex.mat"
source_path2 = pkg_dir * "/examples/Resource/negtransitionex.mat"
y = TyBase.load(source_path1)
y2 = TyBase.load(source_path2)
x = y["x"]
x2 = y2["x"]
figure(1)
R, = risetime(x, t; plotfig=true)
# 上升时间
figure(2)
F, = falltime(x2, t; plotfig=true)
# 下降时间
figure(3)
O, = overshoot(x; plotfig=true)
# 超调

# C3E5
rng = MT19937ar(1234)
t = 0:0.001:1-0.001;
x = cos.(2 * pi * 100 * t) + randn(rng, size(t));
# 高斯白噪声中创建100Hz余弦波
x = x[:]
pband = bandpower(x, 1000, [50 150]);
# 50Hz和150Hz频率总功率
ptot = bandpower(x, 1000, [0 500]);
per_power = 100 * (pband / ptot)
# 确定指定频率功率百分比

# C3E6
Fs = 10000;
f = 2100;
t = [0:1/Fs:1;]
rng = MT19937ar(1234)
x = tanh.(sin.(2 * pi * f * t) .+ 0.1) + 0.001 * randn(rng, length(t))
Sxx, F = periodogram(x, kaiser(length(x), 38), Fs, nargout=2)
# 使用kaiser窗计算功率谱
figure(1)
SNR1, = snr(x, Fs, 7; plotType="power")
# 信噪比，计算不包括最低7次谐波中包含的功率
figure(2)
SNR2, = snr(x, Fs, 7; harmType="aliased", plotType="power")
# 混叠谐波视为信号的
figure(3)
SNR3, = snr(x, Fs, 5; harmType="aliased", plotType="power")
# 计算不包括最低5次谐波中包含的功率



