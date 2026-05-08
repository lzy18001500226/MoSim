using TyCurveFitting
using TyPlot
using TyBase

# ######多项式######
# # 加载数据
# load("census.jl")
# # 利用函数拟合二次多项式
# fitpoly2 = fit("poly2",cdate,pop)
# figure()
# plotfit(fitpoly2,cdate,pop)
# # 指定拟合选项
# fitpoly3 = fit("poly3", cdate, pop, normalize=true,robust="on")
# figure()
# plotfit(fitpoly3,cdate,pop)


# ######威布尔######
# time = [0.1;0.1;0.3;0.3;1.3;1.7;2.1;2.6;3.9;3.9;5.1;5.6;6.2;6.4;7.7;8.1;8.2;8.9;9;9.5;9.6;10.2;10.3;10.8;11.2;11.2;11.2;11.7;12.1;12.3;12.3;13.1;13.2;13.4;13.7;14;14.3;15.4;16.1;16.1;16.4;16.4;16.7;16.7;17.5;17.6;18.1;18.5;19.3;19.7];
# conc = [0.01;0.08;0.13;0.16;0.55;0.9;1.11;1.62;1.79;1.59;1.83;1.68;2.09;2.17;2.66;2.08;2.26;1.65;1.7;2.39;2.08;2.02;1.65;1.96;1.91;1.3;1.62;1.57;1.32;1.56;1.36;1.05;1.29;1.32;1.2;1.1;0.88;0.63;0.69;0.69;0.49;0.53;0.42;0.48;0.41;0.27;0.36;0.33;0.17;0.2];
# f = fit("weibull", time, conc/25, startpt=[0.01, 2])
# plotfit(f,time,conc/25,"o");

# ######单指数#######
# x = 0:0.2:5;
# y = 2*exp.(-0.2*x) + 0.1*randn(size(x));
# # 指数模型拟合
# f = fit("exp1",x,y)
# # 绘制图像
# plotfit(f,x,y)

# ######傅里叶######
# # 加载数据
# load("enso.jl")
# # 傅里叶模型拟合
# f2 = fit("fourier2",month,pressure)
# # 绘制图像
# plotfit(f2,month,pressure)

# ######高斯######
# x,y = titanium();
# # 高斯模型拟合
# f = fit("gauss2", vec(x), vec(y))
# # 绘制图像
# plotfit(f,vec(x),vec(y))

# ######幂######
# # 加载数据
# load("hahn1.jl")
# # 幂模型拟合
# f = fit("power1",temp,thermex)
# # 绘制图像
# plotfit(f,temp,thermex)

# ######有理######
# # 加载数据
# load("hahn1.jl")
# # 有理模型拟合
# f = fit("rational32", temp, thermex)
#  # 绘制图像
# plotfit(f,temp,thermex)

# ######正弦和######
# # 加载数据
# load("enso.jl")
# # 正弦和模型拟合
# f = fit("sumsine6", month, pressure)
# # 绘制图像
# plotfit(f,month,pressure)

# ######线性插值######
# # 加载数据
# load("census.jl")
# # 正弦和模型拟合
# f = fit("cubicspline", cdate,pop)
# # 绘制图像
# plotfit(f, cdate,pop)

# ######曲面拟合及后处理######
# load("franke.jl")
# # 多项式模型拟合
# surffit = fit("poly23", [x y], z, normalize=true)
# # # 绘制图像
# # plot3fit(surffit, [x y], z)
# # 绘制拟合残差
# figure()
# plot3fit(surffit, [x y], z, "style", "residuals")
# # 绘制拟合的信赖区间
# figure()
# plot3fit(surffit, [x y], z, "Style", "predfunc")
# # 在单个指定点计算拟合
# surffit(1000,0.5)
# # 在多个指定点计算拟合
# xi = [500; 1000; 1200]
# yi = [0.7; 0.6; 0.5]
# surffit(xi,yi)
# # 获得这些值的预测区间。
# ci, zi = predint(surffit, [xi yi])
# # 获取模型方程
# formula(surffit)
# # 获取系数名称和值，通过顺序指定系数。
# p00 = surffit.params[1]
# p03 = surffit.params[9]
# # 得到所有的系数名
# coeffnames(surffit)
# # 查看系数值
# coeffvalues(surffit)
# # 得到系数的信赖区间
# confint(surffit)[1]



# ######利用双谐波插值进行曲面拟合######
# load("franke.jl")
# # 多项式模型拟合
# surffit = fit("biharmonicinterp", [x y], z)
# # 绘制图像
# plot3fit(surffit, [x y], z)

# ######利用局部二次回归进行曲面拟合######
# load("franke.jl")
# # 多项式模型拟合
# surffit = fit("loess", [x y], z)
# # 绘制图像
# plot3fit(surffit, [x y], z)


# ######曲线拟合及后处理######
# # 加载数据
# load("census.jl")
# # 三次多项式拟合
# curvefit = fit("poly3", cdate, pop, normalize=true)
# # 绘制图像
# plotfit(curvefit, cdate, pop)
# # 绘制拟合残差
# figure()
# plotfit(curvefit, cdate, pop, "residuals")
# # 绘制拟合预测区间
# figure()
# plotfit(curvefit, cdate, pop, "predfunc")
# # 在单个指定点计算拟合
# curvefit(1991)
# # 在多个指定点计算拟合
# xi = 2000:10:2050
# curvefit(xi)
# # 获得这些值的预测区间。
# ci, = predint(curvefit, xi)
# # 在外推的拟合范围内绘制拟合和预测区间
# figure()
# h = plot(cdate, pop, "o")
# h[1].set_label("")
# xlim([1900, 2050])
# hold("on")
# plotfit(curvefit, "predobs")
# hold("off")
# # 获取模型方程
# formula(curvefit)
# # 获取系数名称和值，通过顺序指定系数。
# p1 = curvefit.params[1]
# p2 = curvefit.params[2]
# # 得到所有的系数名
# coeffnames(curvefit)
# # 查看系数值
# coeffvalues(curvefit)
# # 得到系数的信赖区间
# confint(curvefit)[1]
# # 获取拟合优度统计信息
# gof = curvefit.s_data
# # 计算残差直方图
# figure()
# res = pop - fvallm(curvefit, cdate)
# histogram(res, 10)
# # 绘制拟合、数据和残差
# figure()
# h = plotfit(curvefit, cdate, pop, "fit", "residuals")
# # 计算一些新查询点的值
# cdateFuture = 2000:10:2020
# popFuture = curvefit(cdateFuture)
# # 计算未来人口预测的 95% 信赖区间
# ci, = predint(curvefit, cdateFuture; level=0.95, intv="o")
# # 绘制未来人口预测以及信赖区间，包括拟合和数据值
# figure()
# plot(cdate, pop, "o")
# xlim([1900, 2040])
# hold("on")
# plotfit(curvefit)
# h = errorbar(cdateFuture, popFuture, popFuture - ci[:, 1], ci[:, 2] - popFuture, fmt=".")
# hold("off")
# legend(["cdate v pop", "poly2", "prediction"]; loc="northwest")
# ylim([50,400])



# ######微分以及积分拟合######
# # 创建正弦基信号
# using TyPlot
# using TyCurveFitting
# using TyMath
# xdata = 0:.1:2*pi
# y0 = sin.(xdata)
# # 给信号添加噪声
# rng = MersenneTwister(1234)
# noise = 2*y0 .* randn(rng,size(y0)...) 
# ydata = y0 + noise
# # 用自定义正弦模型拟合含噪数据
# f = fittype("a*sin(b*x)")
# fit1 = fit(f,xdata,ydata,startpt=[1,1])
# # 在预测变量处找到拟合的导数
# d1,d2 = differentiate1(fit1,xdata,order = 2)
# # 绘制数据、拟合和导数
# subplot(3,1,1)
# plotfit(fit1,xdata,ydata)
# tightlayout()
# subplot(3,1,2)
# plot(xdata,d1,"m") # double plot method
# grid("on")
# legend("1st derivative",loc="northeast")
# subplot(3,1,3)
# plot(xdata,d2,"c") # double plot method
# grid("on")
# legend("2nd derivative", loc="northeast")
# # 使用 plotfit 方法直接计算和绘制导数
# figure()
# plotfit(fit1,xdata,ydata,("fit","deriv1","deriv2"))
# # 求预测变量处拟合的积分
# int = TyCurveFitting.integrate(fit1,xdata,0)
# # 绘制数据、拟合和积分
# figure()
# subplot(2,1,1)
# plotfit(fit1,xdata,ydata) # cfit plot method
# xlabel("x")
# ylabel("y") 
# subplot(2,1,2)
# plot(xdata,int,"m") # double plot method
# grid("on")
# legend(["integral"])
# # 使用 plotfit 方法直接计算和绘制积分
# figure()
# plotfit(fit1,xdata,ydata,("fit","integral"))