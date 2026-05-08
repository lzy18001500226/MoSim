using TyPlot
using TySignalProcessing
using TyMath

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
