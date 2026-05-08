#定义自变量t的取值范围
t = 0:pi/50:5*pi
#计算对应于自变量数组的y数组，使用广播
y = exp.(-t / 2.5) .* sin.(3t)
#绘制特征为实线、蓝色、线宽为2的曲线和0参考线
plot(t, y, "-b", linewidth = 2,t,zeros(size(t)))
#标注输出图线的最大值最小值,x轴为[0,5*pi]，y轴为[-1,1]
axis([0, 5 * pi, -1, 1])
#定义xy坐标轴的名称
xlabel("t/s")
ylabel("y")
#定义图形名称
title("y-t  curve")
#在(6.77,0.12)位置处插入"←dy/dx=0"
text(6.77, 0.12, raw"$\leftarrow dy/dx=0$")
#鼠标选择的位置插入文本"myplot"
gtext("myplot")
