# 示例1：模拟 IIR 低通滤波器对比

# 设计一个截止频率为 2GHz 的 5 阶模拟巴特沃斯低通滤波器。乘以 2π，将频率转换为 rad/s。计算 4096 点处滤波器的频率响应。
using TyBase
using TyMath
using TyPlot
using TyControlSystems
using TySignalProcessing

n = 5
f = 2e9

zb, pb, kb = butter(n, 2 * pi * f, "s"; otype="zpk")
bb, ab = zp2tf(zb, pb, kb)
hb, wb = freqs(bb, ab, 4096)

# 设计具有相同边缘频率和 3dB 通带纹波的5阶切比雪夫 I 型滤波器。计算其频率响应。

z1, p1, k1 = cheby1(n, 3, 2 * pi * f, "s"; otype="zpk")
b1, a1 = zp2tf(z1, p1, k1)
h1, w1 = freqs(b1, a1, 4096)

# 设计具有相同边缘频率和 30dB 阻带衰减的5阶切比雪夫 II 型滤波器。计算其频率响应。

z2, p2, k2 = cheby2(n, 30, 2 * pi * f, "s"; otype="zpk")
b2, a2 = zp2tf(z2, p2, k2)
h2, w2 = freqs(b2, a2, 4096)

# 设计一个边缘频率相同、通带纹波为 3dB、阻带衰减为 30dB 的 5 阶椭圆滤波器。计算其频率响应。

ze, pe, ke = ellip(n, 3, 30, 2 * pi * f, "s"; otype="zpk")
be, ae = zp2tf(ze, pe, ke)
he, we = freqs(be, ae, 4096)

# 以分贝为单位绘制衰减曲线。以千兆赫表示频率。比较滤波器。

plot(wb / (2e9 * pi), mag2db.(abs.(hb)))
hold("on")
plot(w1 / (2e9 * pi), mag2db.(abs.(h1)))
plot(w2 / (2e9 * pi), mag2db.(abs.(h2)))
plot(we / (2e9 * pi), mag2db.(abs.(he)))
axis([0 4 -40 5])
grid("on")
xlabel("Frequency (GHz)")
ylabel("Attenuation (dB)")
legend(["butter", "cheby1", "cheby2", "ellip"])
