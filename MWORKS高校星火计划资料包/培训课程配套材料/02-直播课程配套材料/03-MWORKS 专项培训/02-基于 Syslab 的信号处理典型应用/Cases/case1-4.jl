using TyPlot
using TySignalProcessing
using TyMath

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
