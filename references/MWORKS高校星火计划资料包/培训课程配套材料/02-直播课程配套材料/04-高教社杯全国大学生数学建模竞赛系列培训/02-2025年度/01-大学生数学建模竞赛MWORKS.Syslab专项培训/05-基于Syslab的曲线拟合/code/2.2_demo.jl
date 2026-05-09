x, y = titanium();
#高斯模型拟合
f = fit("gauss2", vec(x), vec(y))
#绘制图像
plotfit(f, vec(x), vec(y))
