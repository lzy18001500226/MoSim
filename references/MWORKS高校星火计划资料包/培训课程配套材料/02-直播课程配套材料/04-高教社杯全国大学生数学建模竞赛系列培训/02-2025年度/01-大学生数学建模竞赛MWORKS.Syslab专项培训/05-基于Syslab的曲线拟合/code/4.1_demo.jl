# 加载数据
include(pkgdir(TyCurveFitting) * "/examples/docs/census.jl")
# 三次多项式拟合
curvefit = fit("poly3", cdate, pop, normalize=true)


# 绘制图像
plotfit(curvefit, cdate, pop)
# 绘制拟合残差
figure()
plotfit(curvefit, cdate, pop, "residuals")
# 绘制拟合预测区间
figure()
plotfit(curvefit, cdate, pop, "predfunc")

# 在单个指定点计算拟合
curvefit(1991)

# 在多个指定点计算拟合
xi = 2000:10:2050
curvefit(xi)


# 获得这些值的预测区间。
ci, = predint(curvefit, xi)

# 在外推的拟合范围内绘制拟合和预测区间
figure()
h = plot(cdate, pop, "o")
h[1].set_label("")
xlim([1900, 2050])
hold("on")
plotfit(curvefit, "predfunc")
# plotfit(curvefit, "predobs")
hold("off")

# 获取模型方程
formula(curvefit)


# 在外推的拟合范围内绘制拟合和预测区间
figure()
h = plot(cdate, pop, "o")
h[1].set_label("")
xlim([1900, 2050])
hold("on")
plotfit(curvefit, "predobs")
hold("off")

# 获取系数名称和值，通过顺序指定系数。
p1 = curvefit.params[1]
p2 = curvefit.params[2]


# 得到所有的系数名
coeffnames(curvefit)


# 查看系数值
coeffvalues(curvefit)


# 得到系数的信赖区间
confint(curvefit)[1]

#获取拟合优度统计信息。
gof = curvefit.s_data

# 计算残差直方图。
figure()
res = pop - fvallm(curvefit, cdate)
histogram(res, 10)

# 计算一些新查询点的值
cdateFuture = 2000:10:2020
popFuture = curvefit(cdateFuture)

# 计算未来人口预测的 95% 信赖区间
ci, = predint(curvefit, cdateFuture; level=0.95, intv="o")

# 绘制未来人口预测以及信赖区间，包括拟合和数据值
figure()
plot(cdate, pop, "o")
xlim([1900, 2040])
hold("on")
plotfit(curvefit)
h = errorbar(cdateFuture, popFuture, popFuture - ci[:, 1], ci[:, 2] - popFuture, fmt=".")
hold("off")
legend(["cdate v pop", "poly2", "prediction"]; loc="northwest")
ylim([50, 400])






