using TySignalProcessing

fc = 20
fs = 200
z, p, k = ellip(6, 3, 90, 2 * pi * fc, "lowpass", "s", otype="zpk")
# 模拟椭圆滤波器设计
b, a = zp2tf(z, p, k)
bd, ad = bilinear(b, a, fs)
# 双线性变换
freqz(bd, ad; plotfig=true)
tightlayout()

b1, a1 = ellip(6, 3, 90, 2 * pi * fc, "lowpass", "s", otype="ba")
# 直接输出ba
bd1, ad1 = bilinear(b1, a1, fs)
freqz(bd1, ad1; plotfig=true)
tightlayout()
