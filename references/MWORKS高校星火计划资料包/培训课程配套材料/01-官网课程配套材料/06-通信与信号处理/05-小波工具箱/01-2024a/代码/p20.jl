# 载入图像
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/xbox.mat"
y = load(source_path)
xbox = y["xbox"]
# 进行二维哈尔小波变换
a, h, v, d = haart2(xbox)

# 绘制原图
imagesc(xbox)

# 绘制对角线和水平方向的一级细节系数
figure()
subplot(2, 1, 1)
imagesc(d[1])
title("Diagonal Level 1 Details")
subplot(2, 1, 2)
imagesc(h[1])
title("Horizontal Level 1 Details")
