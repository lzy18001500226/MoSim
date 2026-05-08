# 示例1：AR(4)模型的Burg功率谱密度估计
# 创建 AR(4) 广义平稳随机过程的实现。使用 Burg 方法估计 PSD。将基于单个实现的 PSD 估计值与随机过程的实 PSD 进行比较。

# 创建 AR(4) 系统功能。获取频率响应并绘制系统 PSD。
using TyBase
using TyMath
using TyPlot
using TyControlSystems
using TySignalProcessing

A = [1, -2.7607, 3.8106, -2.6535, 0.9238]
H, F = freqz(1, A, [], 1)
plot(F, 20 * log10.(abs.(H)))

xlabel("Frequency (Hz)")
ylabel("PSD (dB/Hz)")

# 创建 AR(4) 随机过程的实现。将随机数生成器设置为可再现结果的默认设置。实现长度为 1000 样本。假设采样频率为 1 Hz。使用 pburg 估计四阶过程的 PSD。将 PSD 估计值与实 PSD 进行比较。

rng = MT19937ar(1234)

x = randn(rng, 1000)
y, = filter1(1, A, x)
Pxx, F = pburg(y, 4, 1024; fs=1)

hold("on")
plot(F, 10 * log10.(Pxx))
legend(["True Power Spectral Density", "pburg PSD Estimate"])

# 协方差法
Pxx, F = pcov(y, 4, 1024; fs=1)
plot(F, 10 * log10.(Pxx))
legend(["True Power Spectral Density", "pburg PSD Estimate", "pcov PSD Estimate"])

# 修正协方差法
Pxx, F = pmcov(y, 4, 1024; fs=1)
plot(F, 10 * log10.(Pxx))
legend(["True Power Spectral Density", "pburg PSD Estimate", "pcov PSD Estimate", "pmcov PSD Estimate"])

# Yule-Walker法
Pxx, F = pyulear(y, 4, 1024; fs=1)
plot(F, 10 * log10.(Pxx))
legend(["True Power Spectral Density", "pburg PSD Estimate", "pcov PSD Estimate", "pmcov PSD Estimate", "pyulear PSD Estimate"])