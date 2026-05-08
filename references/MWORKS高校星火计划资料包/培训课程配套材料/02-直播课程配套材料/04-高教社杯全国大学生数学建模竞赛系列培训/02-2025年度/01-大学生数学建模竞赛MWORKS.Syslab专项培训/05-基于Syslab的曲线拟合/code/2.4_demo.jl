# 加载数据
include(pkgdir(TyCurveFitting) * "/examples/docs/franke.jl")
# 多项式模型拟合
surffit = fit("loess", [x y], z)
# 绘制图像
plot3fit(surffit, [x y], z)




