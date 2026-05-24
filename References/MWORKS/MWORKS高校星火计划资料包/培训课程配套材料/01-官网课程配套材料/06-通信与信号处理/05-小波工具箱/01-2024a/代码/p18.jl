# 载入带噪信号
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/noisbloc.mat"
y = load(source_path)
s = y["noisbloc"]
sLen = length(s)
# 平稳小波变换，取第三级系数
swa, swd = swt(s, 3, "db1")
swd3 = swd[3, :]
swa3 = swa[3, :]
# 绘制原信号与第三级系数
plot(s)
xlim([0 sLen])
title("Original Signal")
figure()
subplot(2, 1, 1)
plot(swa3)
xlim([0 sLen])
title("Level 3 Approximation coefficients")
subplot(2, 1, 2)
plot(swd3)
xlim([0 sLen])
title("Level 3 Detail coefficients ")
tightlayout()
