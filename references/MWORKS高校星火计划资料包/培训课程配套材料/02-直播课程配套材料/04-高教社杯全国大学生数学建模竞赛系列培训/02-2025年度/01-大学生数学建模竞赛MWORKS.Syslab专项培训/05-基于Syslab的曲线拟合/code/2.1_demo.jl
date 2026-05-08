# 加载数据
include(pkgdir(TyCurveFitting) * "/examples/docs/census.jl")
# 利用函数拟合二次多项式
fitpoly2 = fit("poly2", cdate, pop)
figure()
plotfit(fitpoly2, cdate, pop)
# 指定拟合选项
fitpoly3 = fit("poly3", cdate, pop, normalize=true, robust="on")
figure()
plotfit(fitpoly3, cdate, pop)
