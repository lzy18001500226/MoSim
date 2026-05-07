# using TyCurveFitting
# 加载数据
include(pkgdir(TyCurveFitting) * "/examples/docs/franke.jl")
# 多项式模型曲面拟合
sf = fit("poly23", [x y], z)
# 绘制图像
plot3fit(sf, [x y], z)

