# 载入地震数据
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/kobe.mat"
y = load(source_path)
kobe = y["kobe"]
# 绘制地震数据
figure()
plot((1:length(kobe)) ./ 60, kobe)
xlabel("Time (mins)")
ylabel("Vertical Acceleration (nm/s^2)")
title("Kobe Earthquake Data")
grid("on")
axis("tight")
# 使用频率单位对信号进行连续小波变换
cfs, f, coi = cwt(kobe, 1)
# 连续小波变换绘图（频率单位）
figure()
cwt(kobe, 1; plotfig=true)
# 连续小波变换绘图（时间单位）
cfs, periods, coi = cwt(kobe, cwtMin(1 / 60))
figure()
cwt(kobe, cwtMin(1 / 60); plotfig=true)
