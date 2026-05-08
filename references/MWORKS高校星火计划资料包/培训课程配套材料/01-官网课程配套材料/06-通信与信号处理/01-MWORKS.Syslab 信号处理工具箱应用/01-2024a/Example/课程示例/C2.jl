using TyPlot
using TySignalProcessing
using TyMath
# C2E1
fs = 100;
t = 0:(1 / fs):(1 - 1 / fs);
x = sin.(2 * pi * t * 3) + 0.25 * sin.(2 * pi * t * 40);
# 引入噪声
y = medfilt1(x, 5);
y1 = medfilt1(x, 10);
# 中值滤波，指定窗长度为5或10
figure(1)
plot(t, x, t, y)
legend(["Original", "Filtered"])
figure(2)
plot(t, x, t, y1)
legend(["Original", "Filtered"])

# C2E2
pkg_dir = pkgdir(TySignalProcessing)
source_path =pkg_dir * "/examples/SignalGenerationAndPreprocessing/SmoothingAndDenoising/sgolayfilt/data_sgolayfilt.jl"
include(source_path)
t = (0:(length(mtlb) - 1)) / Fs;
rd = 9;
fl = 21;
smtlb = sgolayfilt(mtlb, rd, fl);
# SG滤波
kmtlb = sgolayfilt(mtlb, rd, fl, kaiser(fl, 38));
# 指定凯撒窗为权重向量的SG滤波
subplot(2, 1, 1)
plot(t, mtlb);
axis([0.2 0.22 -3 2]);title("Original");grid()
subplot(2, 1, 2)
plot(t, smtlb);hold("on");
title("Filtered");grid()
plot(t, kmtlb);
axis([0.2 0.22 -3 2]);
hold("off")

# C2E3
rng = MT19937ar(1234)
n = 59
x = sin.(pi ./ [15 10]' * transpose((1:n)[:]) .+ pi / 3)'
spk = rand(rng, 1:(2 * n), 9, 1)
x[spk] = x[spk] * 2
x[rand(rng, 1:(2 * n), 6, 1)] .= NaN
# 随机注入异常值
y1 = medfilt1(x', [], [], 2;nanflag="omitnan")
# 忽略异常值，端点外为零补全
y2 = medfilt1(x, 4, [], [];nanflag="omitnan", padding="truncate");
# 忽略异常值，端点外为截断
figure(1)
plot(x)
figure(2)
plot(y1')
figure(3)
plot(y2)

# C2E4
x = sin.(2 * pi * [0:99;] / 100)
x[6] = 2
x[20] = -2
# 随机注入异常值
y, i, xmedian, xsigma = hampel(x)
# 计算局部中值、估计标准差
n = [1:length(x);]
figure(1)
plot(n, x)
hold("on")
plot(n, xmedian - 3 * xsigma, n, xmedian + 3 * xsigma)
# 绘制估计范围权限，包括上限和下限
legend(["Original signal", "Lower limit", "Upper limit"])
figure(2)
plot(n, x)
hold("on")
plot(n, y)
idx = findall(x -> x > 0, i)
# 获取异常值下标
plot(n[idx], x[idx], "sk")
legend(["Original signal", "Filtered signal", "Outliers"])

# C2E5
t = 0:0.01:2
y = chirp(collect(t), 0, 1, 250)
# 扫频余弦信号
figure(1)
plot(t, y)
xlabel("Time/s")
ylabel("Y")
grid("on")

T = 10 * (1 / 50)
fs = 1000
t = 0:1/fs:T-1/fs
y = sawtooth(2 * pi * 50 * t)
# 锯齿波信号
figure(2)
plot(t, y)
grid("on")


