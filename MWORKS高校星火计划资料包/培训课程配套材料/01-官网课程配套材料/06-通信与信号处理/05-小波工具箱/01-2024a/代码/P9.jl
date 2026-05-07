# 载入信号
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/noisdopp.mat"
y = load(source_path)
noisdopp = y["noisdopp"]
# 生成滤波器组，设置滤波器的信号长度
fb = cwtfilterbank(; SignalLength=length(noisdopp))

# 进行连续小波变换
# 获得小波系数矩阵、小波系数对应的频率以及影响锥
cfs, f, coi, = wt(fb, noisdopp)
# 绘制时频图
t = 0:(length(noisdopp) - 1)
p = imagesc(abs.(cfs),xvalue=t, yvalue= f)
ax = gca()
ax.set_yscale("log")
ylim([minimum(coi) * 1.054, maximum(coi)])
hold("on")
plot(t, coi; color="w", linewidth=3)
xlabel("Time (Samples)")
ylabel("Normalized Frequency (cycles/sample)")
title("Scalogram")
