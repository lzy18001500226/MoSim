using TyPlot
using TySignalProcessing
using TyMath
using  TyBase
using TyControlSystems
# C4E1
n = 5
f = 2e9
zb,pb,kb = butter(n, 2 * pi * f, "s"; otype="zpk") 
# 巴特沃斯滤波器
bb, ab = zp2tf(zb,pb,kb) 
hb, wb = freqs(bb, ab, 4096)
z1, p1, k1 = cheby1(n, 3, 2 * pi * f, "s"; otype="zpk") 
# # 切比雪夫I型，3dB通带纹波  
b1, a1 = zp2tf(z1,p1,k1)
h1, w1 = freqs(b1, a1, 4096)
z2, p2, k2 = cheby2(n, 30, 2 * pi * f, "s"; otype="zpk")
# 切比雪夫II型，30dB阻带衰减
b2, a2 = zp2tf(z2,p2,k2)
h2, w2 = freqs(b2, a2, 4096)
ze, pe, ke = ellip(n, 3, 30, 2 * pi * f, "s"; otype="zpk") 
# 椭圆滤波器，通带纹波为3dB、阻带衰减为30dB
be, ae, = zp2tf(ze,pe,ke) 
he, we = freqs(be, ae, 4096)
plot(wb/(2e9*pi),mag2db.(abs.(hb))) 
hold("on") 
plot(w1/(2e9*pi),mag2db.(abs.(h1))) 
plot(w2/(2e9*pi),mag2db.(abs.(h2))) 
plot(we/(2e9*pi),mag2db.(abs.(he))) 
axis([0 4 -40 5]) 
grid("on") 
xlabel("Frequency (GHz)") 
ylabel("Attenuation (dB)") 
legend(["butter","cheby1","cheby2","ellip"]) 

# C4E2
fc = 20
fs = 200
z, p, k = ellip(6, 3, 90, 2 * pi * fc, "lowpass", "s", otype="zpk")
# 模拟椭圆滤波器设计
b, a = zp2tf(z, p, k)
bd, ad = bilinear(b, a, fs)
# 双线性变换
freqz(bd, ad; plotfig=true)
b1, a1 = ellip(6, 3, 90, 2 * pi * fc, "lowpass", "s", otype="ba")
# 直接输出ba
bd1, ad1 = bilinear(b1', a1', fs)
freqz(bd1, ad1; plotfig=true)

# C4E3
b = fir1(48, [0.35 0.65],"bandpass") 
freqz(b, [1],512,plotfig = true)
b = fir1(48, [0.35 0.65],"bandstop") 
freqz(b, [1],512,plotfig = true)

# C4E4
F1 = [0:0.01:0.18...]
A1 = 0.5 .+ sin.(2 * pi * 7.5 * F1) / 4
F2 = [0.2, 0.38, 0.4, 0.55, 0.562, 0.585, 0.6, 0.78]
A2 = [0.5, 2.3, 1, 1, -0.2, -0.2, 1, 1]
F3 = [0.79:0.01:1...]
A3 = 0.2 .+ 18 * ((1) .- F3) .^ 2
FreqVect = [F1; F2; F3]
AmplVect = [A1; A2; A3]
figure(1)
plot(FreqVect, AmplVect)
grid("on")
N=50
ham = fir2(N, FreqVect, AmplVect)
# 使用汉明窗设计滤波器。指定滤波器阶数为50
kai = fir2(N, FreqVect, AmplVect, kaiser(N + 1, 3))
# 使用形状参数为3的Kaiser窗口重复计算
hr_ham, w = freqz(ham, [1])
hr_kai, = freqz(kai, [1])
figure(2)
plot(w / pi, abs.(hr_ham))
grid()
hold("on")
plot(w / pi, abs.(hr_kai))
plot(FreqVect, AmplVect, "k:")
ylabel("幅值(dB)")
xlabel("频率 (Hz)")
legend(["Hamming", "Kaiser", "ideal"])
title("零相位响应")
hold("off")

# C4E5
z, p, k = ellip(4, 3, 30, 200 / 500, "lowpass"; otype="zpk")
zplane(z, p)
# 零极点分布
b, a = zp2tf(z, p, k)
freqz(b, a, plotfig=true)
# 频率响应
h, t = stepz(vec(b), vec(a))
# 阶跃响应
figure()
stem(t, h)
xlabel("n(samples)")
ylabel("Amplitude")

