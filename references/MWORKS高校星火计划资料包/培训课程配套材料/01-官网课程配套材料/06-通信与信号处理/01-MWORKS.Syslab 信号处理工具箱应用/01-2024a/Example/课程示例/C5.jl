using TyPlot
using TySignalProcessing
using TyMath
using  TyBase
# C5E1
rng = MT19937ar(1234)
n = 0:319;
x = cos.(pi / 4 * n)' + randn(rng, 1, size(n, 1));
nfft = length(x);
pxx = periodogram(x, [], nfft)
# 功率谱密度估计
periodogram(x, [], nfft; plotfig=true)
# 绘制功率谱密度估计曲线


# C5E2
rng = MT19937ar(1234)
n = 0:319;
x = cos.(pi / 4 .* n)' + randn(rng, (1, size(n, 1)))
pxx, w = pwelch(x; nargout=2)
# 功率谱密度估计
pwelch(x; nargout=0, plotfig=true)
# 绘制功率谱密度估计曲线

# C5E3
rng = MT19937ar(1234)
n = 0:319
x = cos.(pi / 4 * n) + randn(rng, size(n))
a, b = pmtm(x)
# 功率谱密度估计
figure()
plot(b/pi, a)
xlabel("Normalized Frequency(x pi rad/sample)")
ylabel("Power/frequency (dB/(rad/sample))")
title("Thoms on Multitaper Power Spectral Density Estimate")

# C5E4
A = [1, -2.7607, 3.8106, -2.6535, 0.9238]
H, F = freqz(1, A, [], 1)
figure(1)
plot(F, 20 * log10.(abs.(H)))
xlabel("Frequency (Hz)")
ylabel("PSD (dB/Hz)")
# 创建 AR(4) 系统功能。
# 获取频率响应并绘制系统 PSD。
rng = MT19937ar(1234)
x = randn(rng, 1000)
y, = filter1(1, A, x)
figure(2)
subplot(2, 2, 1)
Pxx1, = pburg(y, 4, 1024; fs=1, plotfig=true)
# Burg方法
legend("pburg PSD Estimate")
subplot(2, 2, 2)
Pxx2, = pcov(y, 4, 1024; fs=1, plotfig=true)
# 协方差方法
legend("pcov PSD Estimate")
subplot(2, 2, 3)
Pxx3, = pmcov(y, 4, 1024; fs=1, plotfig=true)
# 修正协方差方法
legend("pmcov PSD Estimate")
subplot(2, 2, 4)
Pxx4, = pyulear(y, 4, 1024; fs=1, plotfig=true)
# Yule_Walker方法
legend("pyulear PSD Estimate")

# C5E5
n = 0:199;
rng = MersenneTwister(1234)
x = cos.(0.257 .* pi .* n) .+ sin.(0.2 .* pi .* n) .+ 0.01 * randn(rng, length(n))
Pxx, w, = pmusic(x, 4; plotfig=true)
p, f = peig(x, 4; plotfig=true)
# 基于特征向量法的伪谱估计
figure(2)
Pxx, w, = pmusic(x, 4; plotfig=true)
# 基于MUSIC算法的伪谱估计

# C5E6
y_hann = hann(64)
# 汉宁窗
y_blackman = blackman(64)
# 布莱克曼窗
y_flattopwin = flattopwin(64)
# 平顶窗
y_gausswin = gausswin(64)
# 高斯窗
y_hamming = hamming(64)
# 汉明窗
y_kaiser = kaiser(200, 2.5)
# 凯撒窗
figure(1)
subplot(3,2,1);plot(y_hann);grid("on");title("hann");
subplot(3,2,2);plot(y_blackman);grid("on");title("blackman");
subplot(3,2,3);plot(y_flattopwin);grid("on");title("flattopwin");
subplot(3,2,4);plot(y_gausswin);grid("on");title("gausswin");
subplot(3,2,5);plot(y_hamming);grid("on");title("hamming");
subplot(3,2,6);plot(y_kaiser);grid("on");title("kaiser");
