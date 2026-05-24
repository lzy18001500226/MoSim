# 加载带噪信号 
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/noisdopp.mat"
y = load(source_path)
noisdopp = y["noisdopp"]

# 使用默认方法（经验贝叶斯）去噪
xden, = wdenoise(noisdopp)
plot(noisdopp)
hold("on")
plot(xden)
legend(["Original Signal", "Denoised Signal"])
