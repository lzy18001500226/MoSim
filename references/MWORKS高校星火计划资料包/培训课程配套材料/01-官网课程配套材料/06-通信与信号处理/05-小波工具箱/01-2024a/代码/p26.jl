# 加载ECG信号
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/wecg.mat"
y = load(source_path)
wecg = y["wecg"]

# 最大重叠离散小波变换多级分解
wtecg = modwt(wecg)

# 绘制1至3级的细节系数
for i in 1:3
    subplot(4, 1, i)
    plot(wtecg[i, :])
    title("Level $i Wavelet Coefficients")
end
subplot(4, 1, 4)
plot(wecg)
title("Original Signal")
tightlayout()

# 加载ECG信号
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/wecg.mat"
y = load(source_path)
wecg = y["wecg"]

# 连续小波变换，序列二维化
cwt(wecg; plotfig=true)
