using TySignalProcessing
using TyPlot

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
