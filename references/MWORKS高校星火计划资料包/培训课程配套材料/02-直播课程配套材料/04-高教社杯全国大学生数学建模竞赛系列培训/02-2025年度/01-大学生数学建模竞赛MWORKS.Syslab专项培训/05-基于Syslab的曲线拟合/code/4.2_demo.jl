# 加载数据
include(pkgdir(TyCurveFitting) * "/examples/docs/franke.jl")
# 多项式模型曲面拟合
surffit = fit("poly23", [x y], z, normalize=true)

# 绘制图像
plot3fit(surffit, [x y], z)
# 绘制拟合残差
figure()
plot3fit(surffit, [x y], z, "style", "residuals")
# 绘制拟合的信赖区间
figure()
plot3fit(surffit, [x y], z, "style", "predfunc")

# 在单个指定点计算拟合
surffit(1000, 0.5)

# 在多个指定点计算拟合
xi = [500; 1000; 1200]
yi = [0.7; 0.6; 0.5]
surffit(xi, yi)

# 获得这些值的预测区间。
ci, zi = predint(surffit, [xi yi])

# 获取模型方程
formula(surffit)

# 获取系数名称和值，通过顺序指定系数。
p00 = surffit.params[1]
p03 = surffit.params[9]

# 得到所有的系数名
coeffnames(surffit)

# 查看系数值
coeffvalues(surffit)

# 得到系数的信赖区间
confint(surffit)[1]

