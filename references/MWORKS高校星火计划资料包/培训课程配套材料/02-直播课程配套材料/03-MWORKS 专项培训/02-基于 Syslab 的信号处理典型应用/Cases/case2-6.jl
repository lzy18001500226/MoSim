using TySignalProcessing
using TyMath

Fs = 10000;
f = 2100;
t = [0:1/Fs:1;]
rng = MT19937ar(1234)
x = tanh.(sin.(2 * pi * f * t) .+ 0.1) + 0.001 * randn(rng, length(t))
Sxx, F = ty_periodogram(x, kaiser(length(x), 38), Fs)
# 使用kaiser窗计算功率谱
figure(1)
SNR1, = snr(x, Fs, 7; plotType="power")
# 信噪比，计算不包括至少7个谐波的功率
figure(2)
SNR2, = snr(x, Fs, 7; harmType="aliased", plotType="power")
# 混叠谐波视为信号的
figure(3)
SNR3, = snr(x, Fs, 5; harmType="aliased", plotType="power")
# 计算不包括至少7个谐波的功率
