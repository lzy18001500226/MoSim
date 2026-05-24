# 加载图像
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/sinsin.mat"
y = load(source_path)
Y = y["Y"]
X = y["X"]

# 生成默认的小波去噪参数
thr, sorh, keepapp = ddencmp("den", "wv", Y)

# 去噪并绘图比较
xd, = wdencmp("gbl", Y, "sym4", 2, thr, sorh, keepapp)
subplot(1, 3, 1)
imagesc(X)
title("Original Image")
subplot(1, 3, 2)
imagesc(Y)
title("Noisy Image")
subplot(1, 3, 3)
imagesc(xd)
title("Denoised Image")
tightlayout()
