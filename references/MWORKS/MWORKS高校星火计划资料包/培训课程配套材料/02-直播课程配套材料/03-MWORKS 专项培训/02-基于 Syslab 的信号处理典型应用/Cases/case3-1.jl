using TySignalProcessing
using TyControlSystems
using TyPlot

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
