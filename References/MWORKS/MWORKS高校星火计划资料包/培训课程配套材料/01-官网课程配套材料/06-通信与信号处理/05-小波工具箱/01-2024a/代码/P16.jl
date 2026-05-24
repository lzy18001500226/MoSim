# 载入数据
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/sumsin.mat"
y = load(source_path)
sumsin = y["sumsin"]
plot(sumsin)
title("Signal")
# 小波分解
c, l = wavedec(sumsin, 3, "db2")
# 获取小波系数
approx = appcoef(c, l, "db2")
cd1, cd2, cd3 = detcoef(c, l, [1 2 3])

# 绘制各级细节系数和最后一级近似系数
figure()
subplot(4, 1, 1)
plot(approx)
title("Approximation Coefficients")
subplot(4, 1, 2)
plot(cd3)
title("Level 3 Detail Coefficients")
subplot(4, 1, 3)
plot(cd2)
title("Level 2 Detail Coefficients")
subplot(4, 1, 4)
plot(cd1)
title("Level 1 Detail Coefficients")
gcf().tight_layout()
